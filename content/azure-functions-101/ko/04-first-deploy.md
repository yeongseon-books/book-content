---
title: "Azure Functions 101 (4/7): 함수 하나 배포하기 — 로컬에서 Azure까지"
series: azure-functions-101
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
- Azure Functions
- Serverless
- Cloud
last_reviewed: '2026-05-12'
seo_description: 앞선 세 장은 개념을 정리하는 단계였습니다. 여기서는 로컬에서 함수를 만들고, Azure에 배포하고, 실제 호출 가능한
  URL을 받기까지의…
---

# Azure Functions 101 (4/7): 함수 하나 배포하기 — 로컬에서 Azure까지

앞선 세 글에서 Azure Functions의 실행 모델, 트리거와 바인딩, Host와 Worker 구조를 먼저 정리했습니다. 이번에는 그 개념을 실제 배포 흐름으로 연결합니다. 결국 좋은 멘탈 모델도 한 번은 **로컬에서 만든 함수가 Azure에서 실제 URL로 살아나는 경험**과 이어져야 손에 잡히기 때문입니다.

처음 배포를 할 때는 CLI 명령이 너무 많아 보일 수 있습니다. 하지만 구조를 잘 보면 흐름은 단순합니다. 로컬에서 프로젝트를 만들고, 함수를 추가하고, 로컬 Host로 실행해 본 다음, Azure 쪽에 Function App과 필수 리소스를 만들고, 마지막으로 코드를 게시하면 됩니다. 문제는 이 다섯 단계가 단순한 절차가 아니라 **런타임 구조와 운영 선택이 반영된 과정**이라는 점입니다.

이 글은 Azure Functions 101 시리즈의 네 번째 글입니다. 여기서는 Python v2 프로그래밍 모델을 기준으로, 로컬 개발 환경에서 시작해 Azure에 배포하고 실제 HTTPS 엔드포인트를 확인하는 가장 짧은 경로를 정리합니다. 동시에 왜 Storage Account가 필요한지, 왜 App Settings가 중요한지, 왜 첫 배포 후에도 운영 체크리스트가 남는지까지 같이 짚겠습니다.

기본 배포 경로는 **Flex Consumption**을 기준으로 잡겠습니다. 현재 Azure 기준에서 새 서버리스 앱의 첫 후보로 가장 자주 검토해야 하는 플랜이기 때문입니다. classic Consumption도 여전히 의미는 있지만, 신규 앱의 기본 기준점으로 보기에는 이제 예외적인 선택에 더 가깝습니다.

이제 “명령을 따라 친다”는 느낌보다, 어떤 리소스를 만들고 어떤 런타임을 올리는지 이해하면서 로컬에서 Azure까지 한 번 끝까지 가보겠습니다.

## 먼저 던지는 질문

- 첫 번째 Function App을 만들기 전에 어떤 파라미터를 먼저 확정해야 할까요?
- zip deploy, GitHub Actions, VS Code 직접 배포 중에서 무엇부터 시작하는 편이 좋을까요?
- Function App은 왜 연결된 Storage Account를 반드시 필요로 할까요?

## 큰 그림

![Azure Functions 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/04/04-01-the-full-flow-on-one-page.ko.png)

*Azure Functions 101 4장 흐름 개요*

이 그림에서는 함수 하나 배포하기 — 로컬에서 Azure까지를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 함수 하나 배포하기 — 로컬에서 Azure까지의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

Azure Functions를 설명하는 글은 많지만, 실제 배포 흐름을 끝까지 밟아 보면 개념이 훨씬 빨리 고정됩니다. 로컬에서 `func start`를 실행하는 순간 Host와 Worker 구조가 실제 프로세스로 올라오고, Azure에 Function App을 만드는 순간부터는 앞에서 배운 플랜, 스토리지, 설정, 인증 개념이 모두 구체적인 리소스로 바뀝니다. 이 연결을 한 번 손으로 거쳐 본 경험이 뒤의 운영 판단을 크게 단순하게 만듭니다.

또한 첫 배포는 단순한 데모 절차가 아닙니다. 어떤 플랜을 기본값으로 잡는지, 앱 설정을 코드 밖에서 주입하는지, Storage Account를 비즈니스 데이터 저장소로 오해하지 않는지, 배포 후 관측 경로를 바로 연결하는지 같은 습관이 이 시점에 굳어집니다. 초반 습관이 어긋나면 서비스가 커질수록 수정 비용이 커집니다.

무엇보다 이 글은 “Azure Functions가 실제로 운영 가능한 앱이 되는 첫 순간”을 보여 줍니다. 뒤에서 다룰 플랜 선택, 스케일링, 콜드 스타트, 모니터링도 결국은 지금 만드는 이 Function App을 기준으로 이어집니다. 그래서 배포 장은 단순한 설치 문서가 아니라, 시리즈 전체를 실전으로 넘기는 전환점이라고 보는 편이 맞습니다.

## 핵심 관점

Azure Functions의 첫 배포는 “코드를 서버에 복사한다”는 느낌보다 **로컬에서 확인한 Functions 실행 환경을 Azure의 Function App 리소스로 옮긴다**는 느낌으로 이해하는 편이 정확합니다. 로컬에서는 `func start`가 Host와 Worker를 띄우고, Azure에서는 Function App이 그 실행 자리를 대신합니다. 즉 코드만 움직이는 것이 아니라, 실행 모델 전체가 로컬에서 클라우드로 이전되는 것입니다.

또한 이 과정은 세 층으로 나뉩니다. 첫째는 개발자 로컬 머신의 프로젝트와 의존성입니다. 둘째는 Azure 리소스 계층으로, Resource Group·Storage Account·Function App이 여기에 속합니다. 셋째는 설정 계층으로, `local.settings.json`에 있던 값들이 App Settings나 Key Vault 참조 같은 운영 설정으로 옮겨갑니다. 이 세 층을 분리해서 보면 배포 흐름이 훨씬 덜 헷갈립니다.

따라서 첫 배포의 핵심은 단순히 “성공 메시지 보기”가 아닙니다. **내 코드가 어떤 런타임과 어떤 리소스 의존성 위에서 Azure에서 다시 살아나는지 이해하는 것**이 더 중요합니다. 이 감각을 먼저 잡아두면 이후 CI/CD나 운영 자동화를 붙일 때도 흔들리지 않습니다.

> 첫 배포는 배포 명령을 외우는 과정이 아니라, 로컬에서 확인한 Functions 실행 모델을 Azure 리소스와 설정 구조로 옮기는 과정입니다.

## 핵심 개념

### 먼저 필요한 도구를 정리합니다

가장 기본적인 CLI 경로는 세 가지 도구면 충분합니다.

| 도구 | 역할 | 설치 |
|---|---|---|
| **Azure Functions Core Tools** | 로컬 실행 + 배포 명령(`func`) | `npm i -g azure-functions-core-tools@4` |
| **Azure CLI** | Azure 리소스를 명령줄로 생성하고 관리 | OS별 설치 ([공식 문서](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)) |
| **Python 3.11+** | Worker 런타임 | pyenv, 공식 설치 프로그램 등 |

VS Code 확장을 써도 되지만, 첫 흐름은 CLI만으로 이해하는 편이 오래 갑니다. 실제로 IDE가 자동화해 주는 일이 무엇인지도 CLI 경로를 한 번 직접 밟아 본 뒤에 더 명확해집니다.

```bash
func --version       # 4.x
az --version         # 2.x
python --version     # 3.11+
```

### 전체 흐름을 먼저 한 장으로 봅니다

배포는 아래 순서로 이해하면 됩니다.

이 그림의 핵심은 “프로젝트 생성 → 함수 추가 → 로컬 검증 → Azure 리소스 생성 → 게시”라는 큰 흐름입니다. 각 단계는 독립적인 것처럼 보여도 실제로는 모두 연결되어 있습니다. 예를 들어 로컬에서 의존성 설치가 잘못되면 배포 후 함수 인덱싱이 깨질 수 있고, Azure 리소스 생성에서 플랜을 잘못 고르면 뒤의 스케일 특성도 달라집니다.

### 1) 프로젝트를 만듭니다

빈 폴더에서 시작해 Python v2 모델 프로젝트를 만듭니다.

```bash
mkdir hello-functions && cd hello-functions
func init . --worker-runtime python --model V2
```

생성 직후 먼저 볼 파일은 세 개입니다.

- `host.json` — Host 런타임 설정
- `local.settings.json` — 로컬 실행용 환경 변수
- `requirements.txt` — Python 의존성 목록

여기서 `local.settings.json`은 매우 중요합니다. 이 파일은 로컬 환경에서의 App Settings 역할을 합니다. 즉 로컬에선 이 파일을 읽고, Azure에 배포되면 같은 설정이 Function App의 App Settings로 옮겨갑니다. **코드는 그대로 두고 설정 계층만 바꾸는 구조**라는 점을 일찍 익혀 두는 편이 좋습니다.

### 2) 가장 단순한 함수를 추가합니다

HTTP 트리거 함수를 하나 생성합니다.

```bash
func new --template "Http Trigger" --name hello --authlevel anonymous
```

Python v2 모델에서 함수 정의는 `function_app.py`에 모입니다. 생성된 코드는 대략 아래와 같습니다.

```python
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="hello")
@app.route(route="hello")
def hello(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name")

    if not name:
        body = req.get_body()
        name = body.decode("utf-8") if body else "world"

    return func.HttpResponse(f"Hello, {name}!")
```

이 정도면 바로 실행 가능한 최소 예제입니다. HTTP 트리거, 요청 객체, 응답 반환이라는 가장 기본적인 Functions 표면이 모두 들어 있습니다.

### 3) 로컬 Host에서 실제로 실행해 봅니다

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
func start
```

성공하면 아래와 비슷한 출력이 보입니다.

```text
Functions:
        hello: [GET,POST] http://localhost:7071/api/hello
```

다른 터미널에서 바로 호출해 볼 수 있습니다.

```bash
curl "http://localhost:7071/api/hello?name=Sisyphus"
# Hello, Sisyphus!
```

이 단계가 중요한 이유는 `func start`가 단순한 개발 서버가 아니기 때문입니다. **실제 Functions Host와 Worker가 로컬에서 실행**되고, 둘 사이에는 gRPC 채널이 열립니다. 즉 앞 글에서 본 구조가 이미 여기서 현실의 프로세스로 동작하고 있습니다.

### 4) Azure 쪽 필수 리소스를 만듭니다

Function App만 단독으로 생기는 것은 아닙니다. 최소 세 가지 리소스가 필요합니다.

| 리소스 | 역할 |
|---|---|
| **Resource Group** | 관련 리소스를 묶는 논리 컨테이너 |
| **Storage Account** | Functions Host 상태, 락, 트리거 메타데이터를 저장하는 필수 저장소 |
| **Function App** | 함수를 실행하는 Azure 컴퓨트 리소스 |

![배포 전 필수 Azure 리소스 구성](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/04/04-02-4-create-azure-resources.ko.png)

*배포 전 필수 Azure 리소스 구성*

여기서 Storage Account를 비즈니스 데이터 저장소와 혼동하면 안 됩니다. 이 계정은 Functions 플랫폼 자체의 상태 유지에 필요합니다. 트리거 락, invocation 메타데이터, Timer 스케줄 상태 같은 인프라 성격의 정보가 여기에 들어갑니다.

```bash
RG=rg-hello
LOC=koreacentral
SA=sthello$RANDOM
APP=func-hello-$RANDOM

# 1) 리소스 그룹
az group create --name $RG --location $LOC

# 2) 스토리지 계정
az storage account create \
    --name $SA --resource-group $RG \
    --location $LOC --sku Standard_LRS

# 3) Function App 생성(Flex Consumption, Python 3.11)
az functionapp create \
    --name $APP --resource-group $RG \
    --storage-account $SA \
    --runtime python --runtime-version 3.11 \
    --functions-version 4 \
    --flexconsumption-location $LOC \
    --instance-memory 2048 \
    --maximum-instance-count 100
```

Flex Consumption 경로에서는 `--flexconsumption-location`이 핵심 옵션입니다. 여기에 런타임, Functions 버전, 스토리지 계정, 메모리, 최대 인스턴스 수를 함께 정합니다. Python에서는 `--instance-memory 2048`이 무난한 시작점인 경우가 많습니다.

### classic Consumption 경로는 의도적으로만 선택합니다

기존 자산을 유지하거나, 오래된 예제를 그대로 재현하거나, 특정 제약 때문에 classic Consumption이 필요한 경우에는 아래와 같이 경로가 바뀝니다.

```bash
az functionapp create \
    --name $APP --resource-group $RG \
    --storage-account $SA \
    --consumption-plan-location $LOC \
    --runtime python --runtime-version 3.11 \
    --functions-version 4
```

다만 이것은 기본값이 아니라 예외 경로라고 보는 편이 좋습니다. 새 앱이라면 먼저 Flex Consumption 기준으로 제약을 검토하고, 그 제약이 맞지 않을 때만 다른 플랜으로 이동하는 흐름이 더 안전합니다.

### 5) 배포는 한 줄이지만, 의미는 한 줄보다 큽니다

```bash
func azure functionapp publish $APP
```

이 명령이 하는 일은 단순히 파일 업로드가 아닙니다. 로컬 프로젝트의 코드와 의존성, Functions 메타데이터를 Azure 쪽 Function App 실행 환경에 게시하고, 그 결과 Azure Host가 함수를 인덱싱하고 공개 엔드포인트를 준비하게 만듭니다.

![로컬 코드가 함수 앱에 배포되는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/04/04-03-5-deploy.ko.png)

*로컬 코드가 함수 앱에 배포되는 흐름*

성공하면 아래와 비슷한 출력이 보입니다.

```text
Functions in func-hello-xxxxx:
    hello - [httpTrigger]
        Invoke url: https://func-hello-xxxxx.azurewebsites.net/api/hello
```

이 URL이 여러분의 첫 공개 엔드포인트입니다.

### 6) 인터넷에서 실제로 호출해 봅니다

```bash
curl "https://func-hello-xxxxx.azurewebsites.net/api/hello?name=Sisyphus"
# Hello, Sisyphus!
```

여기까지 오면 로컬에서 확인한 함수가 Azure에서 실제 서비스로 살아난 것입니다. 같은 `func azure functionapp publish $APP` 명령을 다시 실행하면 재배포됩니다. 즉 배포의 가장 짧은 피드백 루프도 이 지점에서 손에 들어옵니다.

### 운영 전에 바로 챙겨야 할 다섯 가지

첫 배포가 끝났다고 운영 준비가 끝난 것은 아닙니다. 오히려 여기서부터 실무 질문이 생깁니다.

1. **App Settings = 환경 변수** — `local.settings.json` 값은 Azure에서 App Settings로 옮겨야 합니다.
2. 인증 계층 — `anonymous`는 데모용입니다. 함수 키, Entra ID, API Management 같은 계층을 검토해야 합니다.
3. **CI/CD** — `func ... publish`는 데모에는 좋지만, 운영에서는 자동화 파이프라인이 필요합니다.
4. **로그와 모니터링** — Application Insights를 초기에 붙여 두는 편이 훨씬 유리합니다.
5. **플랜 선택** — 지금은 배포가 목적이었지만, 다음 장에서는 이 워크로드에 어떤 플랜이 맞는지를 다시 따져야 합니다.

### 자주 막히는 지점도 미리 기억해 둘 만합니다

- **Storage Account 이름 충돌** — 스토리지 이름은 전역 고유입니다.
- **`func` 명령 버전 문제** — Core Tools v4인지 먼저 확인해야 합니다.
- **배포는 성공했는데 URL이 404** — 함수 인덱싱 실패가 흔합니다. Log stream을 먼저 보는 편이 빠릅니다.

## 흔히 헷갈리는 지점

- **Function App만 만들면 바로 끝난다고 생각하기 쉽지만, Storage Account는 필수 인프라입니다.**
- **`local.settings.json` 값을 배포해 주는 것이 아니라, 같은 역할의 App Settings를 Azure에 다시 구성하는 것입니다.**
- **첫 배포 성공 메시지가 운영 준비 완료를 뜻하지는 않습니다.** 인증, 관측, 롤백 경로는 별도로 남습니다.
- **`func ... publish`는 편리하지만 장기 운영의 최종 경로는 보통 아닙니다.** 결국 CI/CD로 수렴하는 경우가 많습니다.
- **Flex Consumption은 현재 기본 후보일 뿐, 무조건 정답은 아닙니다.** 다음 장의 플랜 선택이 여전히 필요합니다.

## 운영 체크리스트

- [ ] Function App 이름과 Storage Account 이름의 전역 고유 제약을 확인했습니다.
- [ ] 초기 배포 방식이 로컬 publish인지, zip deploy인지, CI/CD인지 명시적으로 정했습니다.
- [ ] 함수 키와 호스트 키의 장기 관리 주체를 정했습니다.
- [ ] 첫 배포 후 health 확인과 기본 사용량 메트릭 점검을 수행했습니다.
- [ ] 슬롯, 이전 패키지 등 롤백 경로를 문서화하거나 리허설했습니다.

## 정리

이번 글에서는 Azure Functions의 개념을 실제 배포 흐름으로 연결했습니다. 로컬에서 프로젝트를 만들고, 함수를 추가하고, Host로 실행해 보고, Azure에 Resource Group·Storage Account·Function App을 만든 뒤, 최종적으로 코드를 게시하면 공개 URL까지 확인할 수 있습니다. 이 전체 흐름은 단순한 절차가 아니라 **Functions 실행 모델을 로컬에서 Azure 리소스로 옮기는 과정**입니다.

특히 기억할 포인트는 세 가지입니다. 첫째, Storage Account는 선택이 아니라 Functions 플랫폼 동작을 위한 필수 인프라입니다. 둘째, `local.settings.json`과 Azure App Settings는 같은 역할의 서로 다른 환경 계층입니다. 셋째, 첫 배포 성공은 운영 준비 완료가 아니라, 플랜·인증·관측·롤백 설계를 시작할 수 있는 기준점일 뿐입니다.

다음 글에서는 바로 그 후속 질문으로 넘어갑니다. **이제 이 Function App을 어떤 호스팅 플랜 위에 두는 것이 맞는가?** Consumption, Flex Consumption, Premium, Dedicated를 워크로드 기준으로 비교해 보겠습니다.

## 처음 질문으로 돌아가기

- **첫 번째 Function App을 만들기 전에 어떤 파라미터를 먼저 확정해야 할까요?**
  - 본문의 기준은 함수 하나 배포하기 — 로컬에서 Azure까지를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **zip deploy, GitHub Actions, VS Code 직접 배포 중에서 무엇부터 시작하는 편이 좋을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Function App은 왜 연결된 Storage Account를 반드시 필요로 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Functions 101 (1/7): Azure Functions란? — 이벤트가 함수를 호출하는 세상](./01-what-is-azure-functions.md)
- [Azure Functions 101 (2/7): 트리거와 바인딩 — 함수 입출력의 모든 것](./02-triggers-and-bindings.md)
- [Azure Functions 101 (3/7): Host와 Worker — 함수는 누가 실행하는가](./03-host-and-worker.md)
- **Azure Functions 101 (4/7): 함수 하나 배포하기 — 로컬에서 Azure까지 (현재 글)**
- Azure Functions 101 (5/7): 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated (예정)
- Azure Functions 101 (6/7): 스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간 (예정)
- Azure Functions 101 (7/7): 모니터링과 운영 기초 (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서

- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- [`az functionapp` CLI reference](https://learn.microsoft.com/en-us/cli/azure/functionapp)
- [Azure Functions Flex Consumption plan hosting](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
- [Function scale and hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Run from package deployment](https://learn.microsoft.com/en-us/azure/azure-functions/run-functions-from-deployment-package)

### 관련 시리즈

- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/) — Host와 배포 이후 런타임 구조를 더 안쪽까지 보고 싶다면

Tags: Azure, Azure Functions, Serverless, Cloud
