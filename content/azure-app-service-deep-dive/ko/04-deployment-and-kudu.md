---
title: "Azure App Service Deep Dive (4/6): 배포와 Kudu — 빌드·동기화·릴리스의 안쪽"
series: azure-app-service-deep-dive
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Azure
- App Service
- Distributed Systems
- Platform Engineering
last_reviewed: '2026-05-15'
seo_description: Kudu, Oryx, run-from-package, slot warm-up으로 App Service 배포 경로를 해부합니다.
---

# Azure App Service Deep Dive (4/6): 배포와 Kudu — 빌드·동기화·릴리스의 안쪽

App Service에서 "배포가 성공했다"는 말은 실제로는 꽤 많은 단계를 뭉뚱그린 표현입니다. artifact가 SCM 엔드포인트에 도착하는 것, 서버 쪽 build automation이 돌아가는 것, 결과물이 `wwwroot` 또는 mounted package 형태로 놓이는 것, 그리고 앱 프로세스가 실제로 새 코드를 들고 readiness를 통과하는 것은 서로 다른 경계입니다.

운영에서 시간이 길어지는 이유도 대개 여기 있습니다. Kudu deployment history에는 success가 찍혀 있는데 앱은 502를 내고, ZIP 업로드는 끝났는데 startup command가 어긋나며, slot swap은 끝났는데 production에서 첫 요청이 느립니다. 이 모든 경우에 "배포 실패"라는 한 문장만으로는 아무것도 설명되지 않습니다.

이 글은 Azure App Service Deep Dive 시리즈의 네 번째 글입니다.

이번 글에서는 Kudu, Oryx, run-from-package, slot warm-up을 하나의 배포 경로로 묶어 보겠습니다. 배포를 upload, build, placement, startup readiness라는 네 단계로 나눠 보면 어디서 성공했고 어디서 실패했는지 훨씬 더 빠르게 읽을 수 있습니다.

이제 artifact가 worker가 보는 런타임 경로까지 도달하는 과정을 차례로 따라가 보겠습니다.

![Azure App Service Deep Dive 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/04/04-01-the-deployment-pipeline-in-one-picture.ko.png)
*Azure App Service Deep Dive 4장 흐름 개요*
> 배포와 Kudu — 빌드·동기화·릴리스의 안쪽의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- Kudu는 App Service에서 정확히 어떤 공개 표면을 제공할까요?
- ZipDeploy는 단순히 ZIP을 풀어 놓는 동작과 어떻게 다를까요?
- Windows code app의 고전적인 Kudu 경로와 Linux code app의 Oryx 경로는 어디서 갈릴까요?

## 왜 이 글이 중요한가

배포를 한 단계로 생각하면 실패 분석이 항상 늦어집니다. artifact upload가 실패했는지, server-side build가 실패했는지, 파일 placement는 끝났지만 runtime startup이 실패했는지를 구분하지 못하면 로그를 보는 순서도 흐려집니다. Kudu 로그와 앱 로그를 같은 문제의 같은 층으로 섞어 보는 실수도 여기서 나옵니다.

또한 Linux code app에서는 Oryx가 중간에 들어오면서 배포 경로가 더 복합해집니다. Kudu가 artifact를 받아도, Oryx가 detect-build-startup을 잘못 해석하거나 startup script가 런타임 계약과 어긋나면 결과는 여전히 startup failure입니다. 즉 Kudu success와 runtime success를 분리해서 보는 습관이 없으면 Linux App Service에서 특히 길을 잃기 쉽습니다.

마지막으로 이 글은 5화와 6화의 전제이기도 합니다. deployment slot의 진짜 가치는 파일 copy 자체보다 production URL 바깥에서 warm-up을 끝낼 수 있다는 데 있습니다. 따라서 배포와 warm-up은 separate topic처럼 보여도 실제 운영에서는 하나의 연속된 경로로 봐야 합니다.

## 핵심 관점

이 주제에서 가장 중요한 문장은 이것입니다. **App Service 배포는 파일을 올리는 행위가 아니라, artifact를 받는 단계와 build automation 단계, 런타임이 읽는 경로에 배치하는 단계, 그리고 새 코드가 실제로 traffic-eligible 상태가 되는 단계를 차례로 통과하는 과정입니다.** 이 네 단계를 분리해야 Kudu success와 app readiness를 혼동하지 않게 됩니다.

이 분리가 실전적인 이유는 각 단계가 서로 다른 로그와 도구를 갖기 때문입니다. Kudu는 upload와 deployment orchestration의 중심이고, Oryx는 Linux code app에서 detect-build-startup 흐름을 맡을 수 있으며, run-from-package는 파일시스템 의미 자체를 바꾸고, slot warm-up은 production 사용자가 cold start 비용을 직접 맞지 않게 만듭니다.

따라서 "배포가 성공했는데 앱이 안 뜬다"는 상황은 모순이 아닙니다. 배포 파이프라인의 앞단은 성공했지만, runtime readiness라는 마지막 경계가 아직 실패한 것일 수 있습니다.

> App Service 배포를 잘 이해한다는 것은 Kudu 로그가 끝나는 자리와 앱 startup 책임이 시작되는 자리를 분리해서 읽는 일입니다.

## 핵심 개념

### 배포 파이프라인은 한 장의 그림으로 먼저 보는 편이 좋습니다

배포 문제를 읽을 때 가장 실용적인 출발점은 네 단계 모델입니다. upload 실패, build 실패, file placement 실패, placement는 끝났지만 runtime startup 실패라는 네 경계로 나누면 진단 순서가 훨씬 분명해집니다.

이 모델이 좋은 이유는 "배포 실패"를 덩어리로 두지 않기 때문입니다. artifact를 받은 쪽이 실패했는지, build automation이 실패했는지, 최종 경로 배치가 실패했는지, 아니면 앱이 새 파일을 읽고도 startup contract를 지키지 못했는지 서로 다른 층으로 나뉩니다.

### Kudu는 App Service의 구체적인 SCM API 표면입니다

Kudu는 App Service의 SCM 사이트이며, 배포와 진단을 담당하는 companion service입니다. 공개 저장소를 보면 Kudu가 추상적인 개념이 아니라 실제 엔드포인트 집합이라는 점이 분명해집니다. `PushDeploymentController.cs`는 ZipDeploy와 publish 계열 요청의 진입점을 보여 주고, `NinjectServices.cs`는 `zipdeploy`, `publish`, `vfs`, `deployments` 같은 route registration을 노출합니다.

즉 Kudu는 단순한 콘솔이 아닙니다. artifact를 받는 실제 SCM API이며, 배포 이력과 파일 접근, 진단 흐름이 이 표면에 연결됩니다. "배포는 성공했는데 어디서 성공한 거지"라는 질문에 답하려면 먼저 Kudu가 배포 파이프라인의 어느 자리인지 이해해야 합니다.

### ZipDeploy는 "압축 해제 후 바로 실행"과 항상 같지 않습니다

공개 Kudu 코드에 있는 `ZipPushDeploy`라는 이름은 꽤 설명적입니다. ZIP artifact를 받아 deployment metadata로 바꾸고, 그것을 배포 흐름으로 넘깁니다. 여기서 중요한 점은 ZipDeploy 자체가 곧장 "압축을 풀고 실행한다"는 뜻이 아니라는 사실입니다.

![ZipDeploy 요청이 배포 작업으로 바뀌는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/04/04-02-what-zipdeploy-actually-means.ko.png)

*ZipDeploy 요청이 배포 작업으로 바뀌는 흐름*

배포 설정에 따라 build automation이 추가될 수 있고, run-from-package가 켜져 있으면 `wwwroot`는 ZIP이 풀린 폴더가 아니라 mounted package로 바뀝니다. 즉 같은 zipdeploy 요청이라도 최종 파일 배치와 startup 의미는 다르게 나타날 수 있습니다.

### Windows code app의 전통적 경로는 Kudu 중심으로 읽을 수 있습니다

Windows code app의 고전적인 경로는 비교적 직선적입니다. Git push 또는 zipdeploy 요청이 들어오고, Kudu가 사이트 유형과 설정을 확인한 뒤, 필요하면 deployment logic을 실행하고, 결과물을 `wwwroot`에 동기화하며, worker가 새 파일을 보게 됩니다. 이 경로에서 `deploy.cmd`나 `deploy.sh`가 자주 등장하는 이유도 자동 생성 또는 사용자 지정 deployment script가 실제로 이 흐름 한가운데 있기 때문입니다.

배포 엔진은 artifact 수신과 파일 배치를 맡습니다. 그러나 이 단계가 끝났다고 해서 앱 프로세스가 바로 정상 상태로 올라오는 것은 아닙니다. Kudu가 새 파일을 올바른 경로에 놓는 일과, 런타임이 그 새 파일을 들고 정상 기동하는 일은 여전히 서로 다른 질문입니다.

### Linux code app에서는 Oryx가 detect-build-startup 역할을 맡을 수 있습니다

Oryx의 공개 README는 자신을 source repo를 runnable artifact로 바꾸는 build system이라고 설명합니다. 또한 codebase를 분석해 build script와 startup script를 생성한다고 분명히 밝힙니다. 이 문장을 App Service 문맥으로 번역하면, Linux code app에서는 Kudu 또는 App Service build service가 Oryx를 호출하고, Oryx가 language와 repository shape를 감지해 dependency restore와 build, startup behavior를 만들어 낸다고 볼 수 있습니다.

![Linux 코드 앱 배포 중 Oryx가 끼는 지점](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/04/04-03-where-oryx-enters-for-linux-code-apps.ko.png)

*Linux 코드 앱 배포 중 Oryx가 끼는 지점*

그래서 Linux App Service에서 "배포는 성공했는데 startup command가 이상하다"는 문제는 순수 Kudu 문제라기보다 Kudu와 Oryx가 만나는 경계 문제일 수 있습니다. artifact는 정상 수신됐지만, detect-build-startup 결과가 런타임 계약과 어긋나면 배포 파이프라인의 앞 절반만 성공한 셈입니다.

### `SCM_DO_BUILD_DURING_DEPLOYMENT`는 zipdeploy의 의미를 바꿉니다

Learn 문서는 zip deployment가 기본적으로 ready-to-run artifact를 전제로 한다고 설명합니다. 그리고 Git deployment와 같은 build automation을 원하면 `SCM_DO_BUILD_DURING_DEPLOYMENT=true`를 켜라고 말합니다. 이 설정 하나가 배포 경로의 성격을 완전히 바꿉니다.

끄면 플랫폼은 준비된 artifact를 주로 배치합니다. 켜면 server-side build와 dependency restore가 경로 안으로 들어옵니다. 즉 같은 zipdeploy 요청도 어떤 앱에서는 "파일 placement" 문제이고, 다른 앱에서는 "build automation" 문제일 수 있습니다.

### run-from-package는 `wwwroot`를 읽기 전용 mounted package로 바꿉니다

run-from-package 문서가 강조하는 핵심은 아주 분명합니다. ZIP 내용이 `wwwroot`에 복사되는 것이 아니라, ZIP package 자체가 read-only `wwwroot`로 마운트됩니다. 이 변화는 단순한 배포 최적화가 아니라 런타임 파일시스템 의미의 변화입니다.

![ZIP 패키지가 읽기 전용 wwwroot로 마운트되는 구조](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/04/04-02-run-from-package-turns-wwwroot-into-a-mo.ko.png)

*ZIP 패키지가 읽기 전용 wwwroot로 마운트되는 구조*

장점은 분명합니다. file-lock conflict가 줄고, deployment atomicity가 좋아지며, file-copy churn이 감소합니다. 대신 `wwwroot`를 writable working directory로 전제한 코드나 부가 구성은 다시 점검해야 합니다. runtime-generated content는 다른 위치를 써야 하고, path assumption은 운영 전에 명시적으로 검증해야 합니다.

### slot 배포는 file copy보다 routing sequence 때문에 안전하게 느껴집니다

slot의 핵심 가치는 production URL 바깥에서 새 버전을 먼저 올리고 warm-up을 끝낼 수 있다는 점입니다. 새 코드가 staging slot worker에서 이미 올라와 있고, 필요한 warm-up까지 끝난 뒤에 production traffic이 넘어가므로 사용자가 cold start 비용을 직접 맞을 확률이 낮아집니다.

![staging warm-up 뒤 production 라우팅이 바뀌는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/04/04-05-why-slot-deployment-feels-safer.ko.png)

*staging warm-up 뒤 production 라우팅이 바뀌는 흐름*

여기서 바뀌는 것은 단순한 파일 배치가 아니라 라우팅입니다. 그래서 slot swap을 이해할 때는 Kudu 배포와 worker warm-up을 같은 이야기로 읽어야 합니다. 파일이 올라갔다고 끝나는 것이 아니라, warm-up이 끝난 인스턴스로 Front-End routing rule이 바뀌어야 비로소 production 영향이 줄어듭니다.

### 배포 경로는 CLI로도 충분히 점검할 수 있습니다

아래 명령은 slot 목록, slot swap, 그리고 staging slot의 swap 관련 app settings를 빠르게 확인할 때 유용합니다. 배포 경로를 실제 운영 표면과 연결하는 기본 도구입니다.

```bash
az webapp deployment slot list -n my-app -g my-rg -o table

az webapp deployment slot swap -n my-app -g my-rg \
  --slot staging --target-slot production --action swap

az webapp config appsettings list -n my-app -g my-rg --slot staging \
  --query "[?starts_with(name, 'WEBSITE_SWAP')]" -o table
```

이 명령은 slot 배포가 실제로 어떤 표면에서 제어되는지 보여 줍니다. production 이전에 어느 slot이 준비되는지, swap 관련 설정이 어떤 상태인지, 운영자가 어떤 조합을 의도했는지 빠르게 확인할 수 있습니다.

### Kudu REST API로 배포 상태를 직접 추적하는 방법

Kudu를 UI로만 보면 단계가 가려집니다. REST API를 사용하면 upload, deployment status, 로그를 분리해 읽을 수 있습니다. 아래 예시는 ZipDeploy 이후 배포 이력과 특정 배포 로그를 이어서 조회하는 기본 패턴입니다.

```bash
# Kudu 기본 인증 정보는 배포 자격증명을 사용
KUDU_BASE="https://my-app.scm.azurewebsites.net"

# 최근 배포 목록
curl -s -u "$KUDU_USER:$KUDU_PASS"   "$KUDU_BASE/api/deployments"

# 특정 배포 로그 조회
DEPLOY_ID="<deployment-id>"
curl -s -u "$KUDU_USER:$KUDU_PASS"   "$KUDU_BASE/api/deployments/$DEPLOY_ID/log"
```

배포 파일 배치 상태를 직접 확인할 때는 VFS endpoint가 유용합니다.

```bash
# wwwroot 디렉터리 목록 확인
curl -s -u "$KUDU_USER:$KUDU_PASS"   "$KUDU_BASE/api/vfs/site/wwwroot/"
```

**Expected output:** `api/deployments`는 배포 단위의 성공/실패와 타임라인을 보여 주고, `api/deployments/<id>/log`는 실제 실패 단계(restore, build, script)를 보여 줍니다. `api/vfs`는 최종 파일 배치 여부를 확인하게 해 주므로, "업로드 실패"와 "런타임 시작 실패"를 분리하는 데 직접적입니다.

### 배포 후 네트워크/성능 검증: startup readiness를 숫자로 확인

Kudu success만으로 배포를 닫으면 위험합니다. 반드시 배포 직후 readiness와 첫 요청 성능을 함께 기록해야 합니다.

```bash
# 배포 직후 상태 코드와 TTFB 분포 확인
for i in $(seq 1 20); do
  curl -o /dev/null -s -w "%{http_code} ttfb=%{time_starttransfer} total=%{time_total}
"     https://my-app.azurewebsites.net/healthz
done

# 슬롯 경유 검증 후 swap 전 마지막 점검
curl -s https://my-app-staging.azurewebsites.net/diag/runtime
```

이 단계에서 status는 200인데 TTFB가 비정상적으로 길면 배포 실패가 아니라 startup 후속 작업 지연일 수 있습니다. 반대로 status가 반복적으로 실패하면 warm-up 경로 또는 startup command를 우선 확인해야 합니다.

### Kudu API 기반 배포 검증 체크포인트

배포 파이프라인을 자동화할 때는 성공 판정을 한 줄로 내리지 말고 체크포인트를 분리합니다. 권장 순서는 `zipdeploy 요청 수락 -> deployment status success -> VFS 경로 확인 -> 앱 readiness 성공`입니다.

```bash
# 1) zipdeploy 제출
curl -s -X POST -u "$KUDU_USER:$KUDU_PASS"   -T app.zip "$KUDU_BASE/api/zipdeploy?isAsync=true"

# 2) 배포 목록에서 최신 항목 확인
curl -s -u "$KUDU_USER:$KUDU_PASS" "$KUDU_BASE/api/deployments"

# 3) 런타임 readiness 확인
curl -o /dev/null -s -w "%{http_code} %{time_total}
" https://my-app.azurewebsites.net/healthz
```

체크포인트를 분리해 두면 실패 지점을 즉시 알 수 있어 롤백 기준도 명확해집니다. 특히 "Kudu 성공 + readiness 실패" 패턴을 독립된 유형으로 관리하면 운영 보고 품질이 크게 올라갑니다.

### 배포 직후 성능 프로파일링으로 숨은 startup 비용 찾기

```bash
for i in $(seq 1 30); do
  curl -o /dev/null -s -w "ttfb=%{time_starttransfer} total=%{time_total}
"     https://my-app.azurewebsites.net/api/orders
done
```

동일 코드 버전에서도 배포 직후 TTFB 꼬리가 길면 dependency 초기화 또는 cache prime이 readiness 뒤에 남아 있을 수 있습니다. 이 경우 warm-up endpoint를 보강해 사용자 경로 이전에 초기화를 끝내는 편이 안정적입니다.

### 롤백 기준을 숫자로 정의하기

배포 실패 판단을 느낌으로 두지 말고 기준을 고정합니다. 예를 들어 3분 내 `/healthz` 성공률 99% 미만 또는 p95 TTFB가 기준 대비 2배 초과이면 즉시 롤백 같은 규칙을 두면 의사결정 속도가 빨라집니다.

```bash
for i in $(seq 1 60); do
  curl -o /dev/null -s -w "%{http_code} %{time_starttransfer}\n" https://my-app.azurewebsites.net/healthz
done
```

이 기준은 배포 자동화 파이프라인에도 그대로 넣을 수 있습니다. readiness 실패가 임계치를 넘으면 승격을 중단하고 이전 슬롯으로 되돌리는 정책을 코드화해 두는 편이 안전합니다.

또한 배포 로그를 장기 보존해 두면 계절성 장애 분석에 도움이 됩니다. 특정 월이나 특정 빌드 도구 버전에서만 startup 지연이 반복되는지를 확인할 수 있어, 플랫폼 이슈와 애플리케이션 이슈를 구분하는 근거가 됩니다.

배포 파이프라인 변경 시에는 이 로그 포맷을 유지해 이전 릴리스와 비교 가능성을 보장해야 합니다.

이 원칙은 필수입니다.

## 흔히 헷갈리는 지점

- **Kudu success는 runtime success가 아닙니다.** artifact 수신과 file placement는 성공했지만 앱 startup은 실패할 수 있습니다.
- **ZipDeploy는 항상 "압축 해제 후 바로 실행"과 같지 않습니다.** build automation과 mounted package 여부에 따라 의미가 달라집니다.
- **Linux code app의 startup 문제를 전부 Kudu 탓으로 돌리면 안 됩니다.** Oryx의 detect-build-startup 경계가 원인일 수 있습니다.
- **run-from-package를 켠 상태에서 `wwwroot`를 writable 경로로 가정하면 안 됩니다.** read-only mounted package라는 전제가 먼저입니다.
- **slot swap은 worker 집합을 통째로 갈아 끼우는 작업이 아닙니다.** warm-up이 끝난 slot으로 Front-End routing rule을 바꾸는 흐름입니다.

## 운영 체크리스트

- [ ] 팀에서 표준 배포 방식 하나를 정하고 선택 이유를 ADR에 기록했습니다.
- [ ] `SCM_DO_BUILD_DURING_DEPLOYMENT` 사용 여부와 그에 따른 build 책임을 명확히 했습니다.
- [ ] run-from-package 환경에서 `wwwroot` 쓰기 가정이 없는지 검토했습니다.
- [ ] slot warm-up이 주요 요청 경로를 실제로 예열하는지 검증했습니다.
- [ ] 배포 권한과 slot 운영 권한을 분리해 최소 권한으로 관리했습니다.

## 정리

4화의 핵심은 App Service 배포를 하나의 성공/실패 문장으로 보지 않는 것입니다. Kudu SCM 사이트가 artifact를 받고, 필요하면 build automation이 돌고, 결과가 `wwwroot` 또는 mounted package 경로에 놓이고, 그 뒤에야 worker가 새 artifact를 들고 startup readiness를 통과해야 합니다. 이 선을 분리해 두면 배포 문제를 훨씬 짧게 자를 수 있습니다.

특히 Linux code app에서는 Oryx가 중간에 들어오므로 Kudu와 startup contract를 따로 보되, 서로 끊어진 주제로 보지는 말아야 합니다. 앞단의 artifact 수신과 중간의 build generation, 마지막의 runtime readiness가 하나의 체인으로 이어져 있기 때문입니다. run-from-package도 같은 이유로 단순한 속도 최적화가 아니라 파일시스템 semantics 변경으로 받아들여야 합니다.

다음 글에서는 control plane 관점에서 scale-out이 어떻게 worker 증가로 이어지는지 보겠습니다. 배포가 끝나 새 코드가 준비되더라도, 실제 사용자 경험은 결국 새 worker가 언제 healthy routing pool에 들어오는가에 달려 있기 때문입니다.

## 처음 질문으로 돌아가기

- **Kudu는 App Service에서 정확히 어떤 공개 표면을 제공할까요?**
  - Kudu는 "배포가 돌아가는 어딘가"가 아니라 `zipdeploy`, `publish`, `vfs`, `deployments`를 노출하는 실제 SCM 사이트입니다. 그래서 배포 이력 확인, `wwwroot` 파일 배치 확인, 특정 deployment log 추적이 모두 Kudu API에서 이어지고, Kudu success는 우선 artifact 수신과 orchestration 성공으로 읽는 편이 맞습니다.
- **ZipDeploy는 단순히 ZIP을 풀어 놓는 동작과 어떻게 다를까요?**
  - ZipDeploy는 ZIP 파일을 받아 배포 작업으로 넘기는 진입점이지, 언제나 압축 해제 후 바로 실행으로 끝나는 기능이 아닙니다. `SCM_DO_BUILD_DURING_DEPLOYMENT`가 켜지면 build 단계가 들어오고, run-from-package가 켜지면 결과는 파일 복사본이 아니라 읽기 전용 `wwwroot` mounted package가 됩니다.
- **Windows code app의 고전적인 Kudu 경로와 Linux code app의 Oryx 경로는 어디서 갈릴까요?**
  - Windows code app은 Kudu가 artifact를 받고 deployment script를 실행해 `wwwroot`에 결과를 맞추는 비교적 직선적인 경로로 설명할 수 있습니다. 반면 Linux code app은 그 사이에 Oryx가 detect-build-startup을 끼워 넣기 때문에, Kudu 배포 자체는 성공했어도 Oryx가 만든 startup script가 런타임 계약과 어긋나면 마지막 readiness에서 멈출 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure App Service Deep Dive (1/6): App Service 플랫폼 아키텍처 — Front-End·Worker·File Server](./01-platform-architecture.md)
- [Azure App Service Deep Dive (2/6): Front-End과 ARR — 요청은 어떻게 워커에 도달하는가](./02-front-end-and-arr.md)
- [Azure App Service Deep Dive (3/6): Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가](./03-worker-and-sandbox.md)
- **Azure App Service Deep Dive (4/6): 배포와 Kudu — 빌드·동기화·릴리스의 안쪽 (현재 글)**
- Azure App Service Deep Dive (5/6): 스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로 (예정)
- Azure App Service Deep Dive (6/6): 콜드 스타트와 Warmup — 첫 요청이 비싼 이유 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [PushDeploymentController.cs @ S62](https://github.com/projectkudu/kudu/blob/S62/Kudu.Services/Deployment/PushDeploymentController.cs)
- [NinjectServices.cs @ S62](https://github.com/projectkudu/kudu/blob/S62/Kudu.Services.Web/App_Start/NinjectServices.cs)
- [Oryx README @ 20240408.1](https://github.com/microsoft/Oryx/blob/20240408.1/README.md)
- [Oryx BuildScriptGeneratorCli directory @ 20240408.1](https://github.com/microsoft/Oryx/tree/20240408.1/src/BuildScriptGeneratorCli)
- [Oryx startupscriptgenerator directory @ 20240408.1](https://github.com/microsoft/Oryx/tree/20240408.1/src/startupscriptgenerator/src)
- [Kudu service overview](https://learn.microsoft.com/azure/app-service/resources-kudu)
- [Deploy files to Azure App Service](https://learn.microsoft.com/azure/app-service/deploy-zip)
- [Run your app directly from a ZIP package](https://learn.microsoft.com/azure/app-service/deploy-run-package)
- [Deployment slots in Azure App Service](https://learn.microsoft.com/azure/app-service/deploy-staging-slots)

### 관련 시리즈
- [Azure App Service 101 — First Deployment](../../azure-app-service-101/ko/04-first-deploy.md)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/03-grpc-event-stream.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-app-service-deep-dive/ko/04-deployment-and-kudu)

Tags: Azure, App Service, Distributed Systems, Platform Engineering
