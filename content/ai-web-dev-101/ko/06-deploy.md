---
title: "AI Web Development 101 (6/7): AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기"
series: ai-web-dev-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI
- LLM
- 웹 개발
- Python
- Tutorial
last_reviewed: '2026-05-14'
seo_description: 로컬에서 만든 AI 웹 앱을 Vercel과 Azure App Service에 배포하며 환경 변수, 로그, 비용 관리의 기본을 익힙니다.
---

# AI Web Development 101 (6/7): AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기

로컬에서 잘 돌아가던 AI 앱도, 다른 사람이 접속하려면 결국 인터넷에 올려야 합니다. 이때부터는 코드만이 아니라 환경 변수, 실행 명령, 로그 확인, 비용 통제 같은 운영 문제가 함께 따라옵니다.

이 글은 AI 웹 개발 입문 시리즈의 6번째 글입니다.

여기서는 로컬에서 만든 AI 웹 앱을 실제 서비스 환경에 배포하고 운영할 때의 기본 흐름을 정리합니다.

![AI Web Development 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/local-to-live-deployment.ko.png)
*AI Web Development 101 6장 흐름 개요*

> 배포는 비밀값, 시작 명령, 로그, 비용 상한이 더 이상 로컬 문제가 아니게 되는 순간입니다 — 선택한 플랫폼(프론트엔드는 Vercel, Python 백엔드는 Azure)이 그중 어떤 항목이 가장 어렵게 다가올지를 결정합니다.

## 먼저 던지는 질문

- 배포는 단순 업로드가 아니라 무엇을 준비하는 과정일까요?
- Next.js 앱과 Python 백엔드는 어떤 플랫폼에 먼저 올리는 편이 좋을까요?
- Vercel에서는 무엇을 가장 먼저 확인해야 할까요?

## 배포를 왜 따로 생각해야 하나

내 컴퓨터에서는 `python app.py`나 `npm run dev`만으로 쉽게 실행되던 코드가, 서버에서는 그대로 되지 않는 경우가 많습니다. 서버는 어떤 파일을 먼저 실행해야 하는지, 어떤 포트에서 요청을 받아야 하는지, 어떤 비밀 키를 넣어야 하는지 스스로 알지 못합니다.

그래서 배포 전에는 아래 네 가지를 먼저 점검하는 편이 좋습니다.

- 의존성 정리: `requirements.txt`나 `package.json`이 실제 실행 환경을 정확히 설명하는가
- 환경 변수 분리: API 키를 코드에 쓰지 않고 환경 변수로 주입하는가
- 애플리케이션 진입점: 서버가 무엇을 실행해야 하는지 명확한가
- 포트 설정: 플랫폼이 알려 주는 포트를 코드가 읽어들일 수 있는가

## 어떤 플랫폼을 고를까

입문 단계에서 자주 만나는 선택지는 Vercel과 Azure App Service입니다. 어느 쪽이 절대적으로 낫다기보다, 앱의 성격에 따라 맞는 쪽이 다릅니다.

| 구분 | Vercel (버셀) | Azure App Service (애저) |
| :--- | :--- | :--- |
| 특징 | 프론트엔드 최적화, 설정이 거의 없음 | 기업용 서비스, Python/Node 등 자유로움 |
| 난이도 | 매우 쉬움 (GitHub 연결 끝) | 보통 (CLI나 포털 설정 필요) |
| 추천 대상 | Next.js, React 앱 배포 | Python Flask/FastAPI 백엔드 앱 |
| 비용 | 개인 프로젝트 무료 플랜 강력 | 일정 수준까지 무료지만 유료 전환 가능성 |

간단히 정리하면 이렇습니다.

- Vercel: Next.js나 React로 만든 화면 중심 앱에 잘 맞습니다.
- Azure App Service: Python Flask/FastAPI 백엔드처럼 서버 런타임 제어가 더 필요한 경우에 잘 맞습니다.
- 둘을 함께 쓰는 조합도 자연스럽습니다. 예를 들어 프론트엔드는 Vercel, Python API는 Azure에 둘 수 있습니다.

![*Vercel과 Azure의 배포 구조 비교*](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/vercel-azure-hosting-overview.ko.png)

*Vercel과 Azure의 배포 구조 비교*

## Vercel에 배포하기

Vercel은 GitHub 저장소를 연결하는 것만으로 배포 흐름을 거의 완성할 수 있습니다. Next.js 챗봇처럼 프론트엔드 중심 AI 앱을 올릴 때 특히 편합니다.

### 1단계: GitHub에 코드 올리기

```bash
git add .
git commit -m "feat: initial AI chatbot"
git push origin main
```

### 2단계: 프로젝트 가져오기

1. [Vercel](https://vercel.com)에 로그인하고 **Add New > Project**를 누릅니다.
2. GitHub 저장소를 가져옵니다.
3. 프로젝트 설정 화면에서 Environment Variables 섹션을 찾습니다.

### 3단계: 환경 변수 설정

로컬에서 쓰던 키는 저장소에 올리지 말고 Vercel 설정 화면에 따로 넣어야 합니다.

- Key: `OPENAI_API_KEY`
- Value: OpenAI 대시보드에서 발급한 실제 키 값

이렇게 해야 배포된 서버가 내 OpenAI 계정으로 요청을 보낼 수 있습니다.

### 4단계: 배포 후 확인

Deploy를 누르면 빌드 로그가 흐릅니다. 여기서 빨간 에러가 뜬다면 대개 의존성 누락, 환경 변수 누락, 타입 오류 중 하나입니다. 배포가 끝나면 `[프로젝트명].vercel.app` 형태의 주소가 생기고, 이 URL로 바로 동작 여부를 확인할 수 있습니다.

![*배포된 앱으로 사용자 요청이 들어오는 운영 경로*](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/production-request-path.ko.png)

*배포된 앱으로 사용자 요청이 들어오는 운영 경로*

### 운영 중 환경 변수 바꾸기

API 키를 교체하거나 설정을 수정했다면 아래 순서를 기억해 두는 편이 좋습니다.

1. **Settings > Environment Variables**에서 값을 수정합니다.
2. **Deployments** 탭에서 최신 항목을 다시 배포합니다.

설정만 바꾸고 끝이 아니라, 그 설정을 반영한 런타임이 다시 떠야 실제 서비스에 적용됩니다.

## Azure App Service에 Python 앱 배포하기

Python Flask나 FastAPI 앱이라면 Azure App Service가 좋은 선택입니다. 다만 Vercel보다 자동 추론이 적기 때문에, 시작 명령과 앱 설정을 더 명시적으로 잡아 줄 필요가 있습니다.

### 1단계: Azure CLI 준비

```bash
# Azure 로그인: 브라우저 창이 뜨면 로그인하세요.
az login

# 현재 사용 중인 구독(Subscription) 목록을 확인합니다.
az account list --output table
```

### 2단계: 기본 배포 실행

`az webapp up`은 초반 실습에서 가장 빠른 출발점입니다. 리소스 그룹, App Service Plan, 웹앱 생성과 코드 업로드를 한 번에 처리해 줍니다.

FastAPI를 올릴 때는 배포 성공과 앱 실행 성공을 구분해서 봐야 합니다. 파일은 올라갔지만 어떤 ASGI 서버로 `main:app`을 띄울지 모르면 기본 플레이스홀더 페이지가 보일 수 있습니다.

먼저 루트에 최소한 아래와 같은 `requirements.txt`가 있어야 합니다.

```text
fastapi
uvicorn[standard]
gunicorn
openai
```

```bash
# 루트 폴더에서 실행 (requirements.txt가 있어야 합니다)
az webapp up --sku F1 --name my-ai-chatbot-app --location koreacentral
```

- `--sku F1`: 연습용 무료 요금제입니다.
- `--name`: 전 세계에서 고유해야 하는 앱 이름입니다.
- `--location koreacentral`: 배포 리전을 한국으로 지정합니다.

배포가 끝나면 출력 JSON에 Resource Group 이름이 보이는데, 이 값은 이후 설정 명령에서 계속 필요하니 메모해 두는 편이 좋습니다.

### 3단계: 시작 명령 명시하기

FastAPI는 시작 명령을 직접 지정해 주는 편이 안전합니다.

```bash
az webapp config set \
  --resource-group myResourceGroup \
  --name <app-name> \
  --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app"
```

이 설정이 없으면 App Service가 내 앱을 어떤 방식으로 띄워야 하는지 몰라 정상 기동에 실패할 수 있습니다. 즉, 배포는 끝났는데 실행은 안 되는 상태가 생길 수 있습니다.

### 4단계: API 키 주입하기

서버도 로컬처럼 환경 변수로 비밀 값을 받아야 합니다. 셸 히스토리에 실제 비밀 문자열을 남기지 않으려면 먼저 로컬 셸 환경 변수에 키를 잡아 둔 뒤, 그 값을 전달하는 편이 좋습니다.

```bash
# 메모해둔 리소스 그룹 이름을 --resource-group 뒤에 넣으세요.
az webapp config appsettings set \
  --name my-ai-chatbot-app \
  --resource-group [메모한-리소스-그룹-이름] \
  --settings OPENAI_API_KEY="$OPENAI_API_KEY"
```

### 5단계: 로그로 실제 상태 확인하기

배포 후 `Application Error`가 보이면 추측보다 로그가 먼저입니다.

```bash
# 실시간 로그 스트리밍 시작
az webapp log tail --name my-ai-chatbot-app --resource-group [리소스-그룹-이름]
```

환경 변수 누락, 라이브러리 설치 실패, 시작 명령 오류 같은 문제는 이 로그에서 바로 드러나는 경우가 많습니다.

## API 키 보안은 배포의 일부다

초보자가 가장 자주 하는 실수는 API 키를 코드에 직접 적고 저장소에 올리는 것입니다. AI 앱에서는 이 한 번의 실수가 바로 과금 사고로 이어질 수 있습니다.

코드에서는 `process.env.OPENAI_API_KEY`나 `os.getenv("OPENAI_API_KEY")`로 값을 읽기만 하고, 실제 값은 배포 플랫폼의 환경 변수 설정에서 넣는 방식이 기본입니다.

```text
# .gitignore 파일 예시
.env
__pycache__/
node_modules/
.venv/
.DS_Store
```

저장소에는 `.env.example`만 두고 필요한 변수 이름만 공유하면 됩니다. 실제 비밀 값은 각 개발자 로컬 환경과 배포 플랫폼에만 남아야 합니다.

![*환경 변수 관리와 하드코딩 노출의 차이*](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/secret-key-boundary.ko.png)

*환경 변수 관리와 하드코딩 노출의 차이*

## 비용과 모니터링 기본선

AI 앱은 배포가 무료여도 모델 호출 비용은 계속 발생할 수 있습니다. 그래서 운영의 핵심은 “의외의 지출과 조용한 오류를 빨리 잡는 것”입니다.

### OpenAI 사용량 제한

[OpenAI Dashboard](https://platform.openai.com/usage)에서 월간 예산 한도를 설정해 두는 편이 안전합니다. 실험용 프로젝트라면 낮은 금액으로 먼저 묶어 두는 것이 좋습니다.

### Azure 비용 알람

Azure를 쓴다면 Cost Management에서 Budget Alert를 설정해 두세요. 무료 범위 초과나 예산 80% 도달 시 알림을 받으면 비용 사고를 줄일 수 있습니다.

### 배포 직후 확인할 신호

- 첫 접속 속도: cold start가 체감상 어느 정도인지 확인합니다.
- HTTP 500 추적: Vercel Runtime Logs나 Azure Log Stream에서 원인을 바로 확인합니다.
- 사용자 질문 패턴: 실제 사용자가 어떤 프롬프트를 넣는지 관찰하면 다음 개선 방향이 보입니다.

![*예산 제한과 오류 확인으로 이어지는 운영 점검 흐름*](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/cost-guardrails-flow.ko.png)

*예산 제한과 오류 확인으로 이어지는 운영 점검 흐름*

## 체크리스트

- [ ] 의존성 파일과 시작 명령을 배포 환경 기준으로 점검했다.
- [ ] API 키를 플랫폼 환경 변수로만 주입한다.
- [ ] 배포 직후 로그 확인 경로를 알고 있다.
- [ ] OpenAI와 클라우드 예산 알림을 설정했다.

## 배포 직후 24시간 운영 점검 시나리오

초기 배포에서 가장 자주 놓치는 것은 "성공 화면"만 확인하고 실제 사용 흐름을 끝까지 검증하지 않는 점입니다. 배포 직후 24시간은 기능 검증보다 운영 신호 점검에 집중하는 편이 안전합니다.

### 1) 사용자 경로 기준 점검

- 첫 요청, 두 번째 요청, 긴 요청처럼 서로 다른 길이의 프롬프트를 보내 응답 시간 분포를 확인합니다.
- 정상 질문, 엣지 질문, 실패 유도 질문을 분리해 HTTP 상태 코드와 오류 메시지 일관성을 확인합니다.
- 프론트엔드와 백엔드가 분리된 구조라면 CORS, 타임아웃, 재시도 정책이 실제로 동작하는지 확인합니다.

### 2) 로그 품질 점검

- 요청 ID가 프론트엔드 로그와 백엔드 로그를 관통하는지 확인합니다.
- 모델 호출 실패 시, 사용자에게는 안전한 메시지를 주고 내부 로그에는 원인 코드를 남기는지 확인합니다.
- 키 누락, 권한 오류, 한도 초과 같은 운영성 오류를 재현해 알림 경로까지 검증합니다.

### 3) 비용 안전장치 점검

- 일일 요청 수가 늘어날 때 토큰 사용량이 어떤 기울기로 증가하는지 추정합니다.
- 모델별 단가가 다른 경우 라우팅 규칙이 의도대로 적용되는지 샘플 로그로 확인합니다.
- 예산 임계값 알림이 실제 연락 채널(이메일, 메신저)로 도달하는지 모의 테스트합니다.

이 점검은 개발 속도를 늦추는 절차가 아니라, 이후 장애 대응 시간을 줄이는 사전 투자입니다. 특히 AI 앱은 코드 버그보다 데이터·모델·비용 요인이 함께 엮여 장애를 만들기 때문에, 초반에 운영 관측선을 분명히 잡아 두는 습관이 중요합니다.

또 하나의 실무 팁은 "배포 확인 담당"을 명시하는 것입니다. 배포 버튼을 누른 사람과 검증 책임자가 같아도 괜찮지만, 체크 항목을 역할로 나눠 두면 누락이 줄어듭니다. 예를 들어 한 명은 사용자 시나리오 테스트를, 다른 한 명은 로그/비용/알림을 확인하도록 분리하면 배포 직후 리스크를 더 빠르게 줄일 수 있습니다.

## 배포 전 체크리스트를 코드와 함께 고정하기

배포를 안정적으로 반복하려면 개인 기억 대신 체크리스트를 저장소에 남겨야 합니다. 특히 AI 앱은 일반 웹앱보다 환경 변수 의존도가 높아서, 값 하나가 빠져도 사용자에게는 "응답 없음"으로만 보일 수 있습니다.

```bash
# 배포 전 공통 점검
python3 -m pytest tests
npm run lint
npm run build
python3 scripts/check_env_required.py --env-file .env.production.example
```

검증 스크립트가 배포 파이프라인에 연결되어 있지 않다면, 결국 수동 확인으로 되돌아가고 장애 확률이 올라갑니다.

## Vercel 프런트엔드 배포 구성

Next.js 기반 챗봇 프런트엔드는 Vercel에 먼저 올리는 편이 진입장벽이 낮습니다. 다만 프런트와 백엔드 URL 계약을 명확히 해야 환경별 혼선을 막을 수 있습니다.

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_BASE_URL": "https://api.example.com",
    "AI_MODEL": "gpt-4o-mini"
  }
}
```

환경 변수 이름은 코드의 상수 이름과 반드시 일치시켜야 합니다. 이름이 조금만 달라도 런타임에서 조용히 실패하는 경우가 많습니다.

## Azure App Service 백엔드 배포 예시

Python API 서버를 Azure App Service에 배포할 때는 시작 명령과 헬스 체크 경로를 먼저 고정하는 것이 좋습니다.

```yaml
# startup command example
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 --timeout 120
```

```bash
az webapp config appsettings set \
  --resource-group rg-ai-web-dev \
  --name ai-web-dev-api \
  --settings OPENAI_API_KEY="***" AI_MODEL="gpt-4o-mini" LOG_LEVEL="INFO"
```

헬스 체크 경로(`/healthz`)는 모델 호출을 포함하지 않고, 프로세스와 의존성 연결 상태만 빠르게 확인하도록 설계해야 합니다.

## 운영 설정: 타임아웃, 재시도, 회로 차단

AI API는 네트워크와 공급자 상태에 영향을 받으므로, 배포 환경에서 반드시 시간 제한과 재시도 정책을 명시해야 합니다.

```python
CALL_TIMEOUT_SEC = 20
MAX_RETRY = 2
RETRY_BACKOFF_SEC = [0.5, 1.0]
```

또한 일정 비율 이상 실패가 누적되면 회로 차단기 패턴으로 일시적으로 호출을 중단하고, 사용자에게 장애 공지를 반환하는 방식이 실무에서 자주 사용됩니다.

## 배포 후 검증 시나리오

배포 성공 메시지만 보고 끝내면 거의 반드시 문제를 놓칩니다. 최소한 아래 시나리오를 자동화해야 합니다.

1. 정상 질의: 응답 코드 200, JSON 스키마 통과
2. 잘못된 입력: 4xx와 오류 메시지 규약 확인
3. 모델 장애 모의: 5xx 대응 메시지 확인
4. 시간 초과 모의: 재시도 횟수와 최종 오류 확인
5. 토큰 과다 입력: 길이 제한 동작 확인

## 평가 지표 대시보드 기본 항목

배포 이후 첫 주에는 대시보드를 단순하게 유지하는 편이 좋습니다.

- 요청 수, 오류율, p95 지연 시간
- 평균 prompt_tokens, completion_tokens
- 사용자 피드백(도움됨/도움안됨)
- 경로별 비용 추정치
- 배포 버전별 성능 비교

이 다섯 항목만으로도 "성능 저하", "비용 급증", "특정 버전 회귀"를 초기에 발견할 수 있습니다.

## 보안 기본선: 키 관리와 접근 제어

배포 단계에서 가장 위험한 실수는 API 키를 코드 저장소나 클라이언트 번들에 노출하는 일입니다. 운영 키는 반드시 플랫폼 시크릿 저장소에 넣고, 권한 범위를 최소화해야 합니다.

- 운영 키와 개발 키를 분리합니다.
- 키 회전 주기를 월 단위로 정합니다.
- 이상 트래픽이 감지되면 즉시 폐기할 수 있는 절차를 문서화합니다.

또한 관리자 페이지나 내부 진단 API에는 IP 제한 또는 인증 게이트를 두어야 불필요한 노출을 줄일 수 있습니다.

## 실제 운영 배포 파이프라인 예시

배포는 수동 클릭보다 선언형 파이프라인이 안정적입니다. 아래와 같은 단계로 구성하면 실패 지점을 명확히 분리할 수 있습니다.

```yaml
name: deploy-ai-web-app
on:
  push:
    branches: [main]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build
      - run: python3 -m pip install -r requirements.txt
      - run: python3 -m pytest -q

  deploy:
    needs: verify
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/deploy_vercel.sh
      - run: ./scripts/deploy_azure_api.sh
```

검증과 배포 단계를 분리하면 문제 발생 시 원인을 빠르게 특정할 수 있습니다.

## 롤백 기준을 미리 문서화하기

롤백은 실패했을 때 즉흥적으로 결정하면 늦습니다. 다음 기준을 사전에 합의해 두는 편이 좋습니다.

- 5분 평균 오류율이 5% 초과
- p95 지연 시간이 기준 대비 2배 이상 증가
- 인증 오류가 연속으로 발생

기준이 명시되어 있으면 담당자가 교대해도 같은 판단을 재현할 수 있습니다.

## 운영 점검 자동화 명령 예시

배포 후 10분 안에 실행하는 점검 명령을 스크립트로 고정해 두면 야간 장애 대응이 훨씬 쉬워집니다.

```bash
curl -fsS https://api.example.com/healthz
curl -fsS https://api.example.com/api/ask -H 'content-type: application/json' -d '{"question":"상태 점검","user_id":"monitor"}'
```

이 명령의 목적은 기능 완전 검증이 아니라 "지금 즉시 서비스 가능한 상태인지"를 빠르게 확인하는 것입니다.

## 비용 상한 가드

AI 앱은 정상 동작 중에도 비용이 급증할 수 있으므로 일일 상한과 경보 임계치를 설정해야 합니다.

- 일일 비용 상한 100달러
- 1시간 이동 평균이 기준 대비 2배 상승하면 경보
- 특정 엔드포인트에서 토큰 급증 시 자동 샘플링 로그 활성화

이 가드가 있어야 품질 이슈가 비용 사고로 번지는 것을 막을 수 있습니다.

### 실무 메모

이 절에서 다룬 원칙은 기능이 늘어날수록 더 중요해집니다. 특히 팀원이 늘어나면 개인 감각보다 문서화된 규칙이 더 큰 품질 차이를 만듭니다. 따라서 예제 코드를 복사해 쓰는 것에서 멈추지 말고, 현재 팀의 장애 패턴과 운영 제약에 맞춰 규칙을 재정의하는 작업이 필요합니다. 작은 체크리스트 하나가 장기적으로는 가장 큰 비용 절감으로 돌아옵니다.

### 실무 메모

이 절에서 다룬 원칙은 기능이 늘어날수록 더 중요해집니다. 특히 팀원이 늘어나면 개인 감각보다 문서화된 규칙이 더 큰 품질 차이를 만듭니다. 따라서 예제 코드를 복사해 쓰는 것에서 멈추지 말고, 현재 팀의 장애 패턴과 운영 제약에 맞춰 규칙을 재정의하는 작업이 필요합니다. 작은 체크리스트 하나가 장기적으로는 가장 큰 비용 절감으로 돌아옵니다.

### 배포 후 24시간 관찰

첫 24시간에는 기능 추가보다 관찰을 우선합니다. 오류율, 지연 시간, 토큰 사용량이 안정 구간에 들어오는지 확인한 뒤 다음 릴리스를 계획하는 편이 장기적으로 안전합니다.

추가로, 운영팀과 개발팀이 같은 체크리스트를 공유하도록 문서 위치를 고정해 두는 것이 좋습니다. 이렇게 해야 담당자가 바뀌어도 동일한 기준으로 대응할 수 있습니다.

## 정리

배포는 기능 구현의 마지막 단계가 아니라 운영의 첫 단계입니다.

- Vercel은 Next.js 같은 프론트엔드 중심 AI 앱에 빠른 출발점을 제공합니다.
- Azure App Service는 Python 백엔드를 올릴 때 유연하지만 시작 명령과 앱 설정을 더 명시해야 합니다.
- 환경 변수와 비밀 키 관리는 배포 설계의 일부입니다.
- 로그와 예산 알림을 먼저 걸어 두면 배포 후 문제를 훨씬 빨리 잡을 수 있습니다.

다음 글에서는 배포한 AI 앱이 실제로 잘 동작하는지 어떻게 평가하고 개선할지 봅니다.

## 처음 질문으로 돌아가기

- **배포는 단순 업로드가 아니라 무엇을 준비하는 과정일까요?**
  - 배포는 코드 파일을 올리는 일이 아니라 `requirements.txt`와 `package.json`, 시작 명령, 포트, 환경 변수, 검증 시나리오를 실행 환경 기준으로 고정하는 과정입니다. 본문에서 `python3 -m pytest tests`, `npm run lint`, `npm run build`, `python3 scripts/check_env_required.py --env-file .env.production.example`를 배포 전 공통 점검으로 둔 이유가 여기에 있습니다. 즉 업로드보다 중요한 것은 "서버가 무엇을 어떻게 실행해야 하는지"를 미리 결정하는 일입니다.
- **Next.js 앱과 Python 백엔드는 어떤 플랫폼에 먼저 올리는 편이 좋을까요?**
  - 화면 중심 Next.js 앱은 Vercel에, `gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 --timeout 120`처럼 런타임 제어가 필요한 Python API는 Azure App Service에 두는 구성이 가장 자연스럽다고 정리했습니다. 그래서 `NEXT_PUBLIC_API_BASE_URL`, `AI_MODEL`은 Vercel 쪽 예시로, `OPENAI_API_KEY`, `LOG_LEVEL`, startup command는 Azure 쪽 예시로 나눠 설명했습니다. 둘을 같이 쓰는 구조도 프론트와 백엔드의 운영 성격이 다르기 때문에 나온 선택입니다.
- **Vercel에서는 무엇을 가장 먼저 확인해야 할까요?**
  - 가장 먼저 볼 것은 `OPENAI_API_KEY` 같은 환경 변수가 실제 배포 환경에 들어갔는지와 빌드 로그에서 의존성·타입 오류가 없는지입니다. 배포 후에는 `[프로젝트명].vercel.app`이 뜨는지만 보지 말고, `Functions > app/api/chat/route.ts > maxDuration=30`, `vercel env add OPENAI_API_KEY production`, 그리고 실제 사용자 경로의 첫 요청·긴 요청·실패 요청까지 확인해야 합니다. 이 글이 Vercel 배포 직후 24시간 점검 시나리오를 따로 둔 이유도 바로 그 검증 순서를 고정하기 위해서였습니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Web Development 101 (1/7): AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기](./01-hello-ai-api.md)
- [AI Web Development 101 (2/7): 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술](./02-prompt-engineering.md)
- [AI Web Development 101 (3/7): AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현](./03-ai-chatbot.md)
- [AI Web Development 101 (4/7): RAG 입문 — 내 데이터로 답하는 AI 만들기](./04-rag-intro.md)
- [AI Web Development 101 (5/7): AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기](./05-ai-agent.md)
- **AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기 (현재 글)**
- AI 앱의 평가와 개선, 품질을 측정하고 더 좋게 만드는 법 (예정)

<!-- toc:end -->

## 참고 자료
- [AI Web Development 101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/ai-web-dev-101/ko)

- [Vercel 공식 문서](https://vercel.com/docs)
- [Azure App Service Python 가이드](https://learn.microsoft.com/ko-kr/azure/app-service/quickstart-python)
- [OpenAI API 보안 권장 사항](https://platform.openai.com/docs/guides/production-best-practices/safety-and-best-practices)

Tags: AI, LLM, 웹 개발, Python, Tutorial
