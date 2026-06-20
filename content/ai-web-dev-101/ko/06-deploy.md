---
title: "AI Web Development 101 (6/7): AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기"
series: ai-web-dev-101
episode: 6
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/24"
    published_at: '2026-04-25'
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

> **Deprecation notice**: 이 시리즈는 [`llm-app-foundations-101`](../../llm-app-foundations-101/ko/)과 [`ai-app-patterns-101`](../../ai-app-patterns-101/ko/)로 대체되었습니다. 신규 독자는 후속 시리즈를 권장합니다.

# AI Web Development 101 (6/7): AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기

로컬에서 잘 돌아가던 AI 앱도, 다른 사람이 접속하려면 결국 인터넷에 올려야 합니다. 이때부터는 코드만이 아니라 환경 변수, 실행 명령, 로그 확인, 비용 통제 같은 운영 문제가 함께 따라옵니다.

이 글은 AI 웹 개발 입문 시리즈의 6번째 글입니다.

![AI Web Development 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/local-to-live-deployment.ko.png)
*AI Web Development 101 6장 흐름 개요*

> 배포는 비밀값, 시작 명령, 로그, 비용 상한이 더 이상 로컬 문제가 아니게 되는 순간입니다 — 선택한 플랫폼(프론트엔드는 Vercel, Python 백엔드는 Azure)이 그중 어떤 항목이 가장 어렵게 다가올지를 결정합니다.

## 이 글에서 다룰 문제

- 배포는 단순 업로드가 아니라 무엇을 준비하는 과정일까요?
- Next.js 앱과 Python 백엔드는 어떤 플랫폼에 먼저 올리는 편이 좋을까요?
- Vercel에서는 무엇을 가장 먼저 확인해야 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 배포를 왜 따로 생각해야 하나

내 컴퓨터에서는 `python app.py`나 `npm run dev`만으로 쉽게 실행되던 코드가, 서버에서는 그대로 되지 않는 경우가 많습니다. 서버는 어떤 파일을 먼저 실행해야 하는지, 어떤 포트에서 요청을 받아야 하는지, 어떤 비밀 키를 넣어야 하는지 스스로 알지 못합니다.

그래서 배포 전에는 아래 네 가지를 먼저 점검하는 편이 좋습니다.

- 의존성 정리: `requirements.txt`나 `package.json`이 실제 실행 환경을 정확히 설명하는가
- 환경 변수 분리: API 키를 코드에 쓰지 않고 환경 변수로 주입하는가
- 애플리케이션 진입점: 서버가 무엇을 실행해야 하는지 명확한가
- 포트 설정: 플랫폼이 알려 주는 포트를 코드가 읽어들일 수 있는가

## 어떤 플랫폼을 고를까

입문 단계에서 자주 만나는 선택지는 Vercel과 Azure App Service입니다.

| 구분 | Vercel (버셀) | Azure App Service (애저) |
| :--- | :--- | :--- |
| 특징 | 프론트엔드 최적화, 설정이 거의 없음 | 기업용 서비스, Python/Node 등 자유로움 |
| 난이도 | 매우 쉬움 (GitHub 연결 끝) | 보통 (CLI나 포털 설정 필요) |
| 추천 대상 | Next.js, React 앱 배포 | Python Flask/FastAPI 백엔드 앱 |
| 비용 | 개인 프로젝트 무료 플랜 강력 | 일정 수준까지 무료지만 유료 전환 가능성 |

- Vercel: Next.js나 React로 만든 화면 중심 앱에 잘 맞습니다.
- Azure App Service: Python Flask/FastAPI 백엔드처럼 서버 런타임 제어가 더 필요한 경우에 잘 맞습니다.
- 둘을 함께 쓰는 조합도 자연스럽습니다. 프론트엔드는 Vercel, Python API는 Azure에 둘 수 있습니다.

![Vercel과 Azure의 배포 구조 비교](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/vercel-azure-hosting-overview.ko.png)

*Vercel과 Azure의 배포 구조 비교*

## Vercel에 배포하기

Vercel은 GitHub 저장소를 연결하는 것만으로 배포 흐름을 거의 완성할 수 있습니다.

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

### 4단계: 배포 후 확인

Deploy를 누르면 빌드 로그가 흐릅니다. 여기서 빨간 에러가 뜬다면 대개 의존성 누락, 환경 변수 누락, 타입 오류 중 하나입니다. 배포가 끝나면 `[프로젝트명].vercel.app` 형태의 주소가 생기고, 이 URL로 바로 동작 여부를 확인할 수 있습니다.

![배포된 앱으로 사용자 요청이 들어오는 운영 경로](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/production-request-path.ko.png)

*배포된 앱으로 사용자 요청이 들어오는 운영 경로*

### 운영 중 환경 변수 바꾸기

1. **Settings > Environment Variables**에서 값을 수정합니다.
2. **Deployments** 탭에서 최신 항목을 다시 배포합니다.

설정만 바꾸고 끝이 아니라, 그 설정을 반영한 런타임이 다시 떠야 실제 서비스에 적용됩니다.

## Azure App Service에 Python 앱 배포하기

Python Flask나 FastAPI 앱이라면 Azure App Service가 좋은 선택입니다.

### 1단계: Azure CLI 준비

```bash
# Azure 로그인: 브라우저 창이 뜨면 로그인하세요.
az login

# 현재 사용 중인 구독(Subscription) 목록을 확인합니다.
az account list --output table
```

### 2단계: 기본 배포 실행

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

### 3단계: 시작 명령 명시하기

FastAPI는 시작 명령을 직접 지정해 주는 편이 안전합니다.

```bash
az webapp config set \
  --resource-group myResourceGroup \
  --name <app-name> \
  --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app"
```

이 설정이 없으면 App Service가 내 앱을 어떤 방식으로 띄워야 하는지 몰라 정상 기동에 실패할 수 있습니다.

### 4단계: API 키 주입하기

```bash
az webapp config appsettings set \
  --name my-ai-chatbot-app \
  --resource-group [메모한-리소스-그룹-이름] \
  --settings OPENAI_API_KEY="$OPENAI_API_KEY"
```

### 5단계: 로그로 실제 상태 확인하기

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

저장소에는 `.env.example`만 두고 필요한 변수 이름만 공유하면 됩니다.

![환경 변수 관리와 하드코딩 노출의 차이](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/secret-key-boundary.ko.png)

*환경 변수 관리와 하드코딩 노출의 차이*

## 비용과 모니터링 기본선

AI 앱은 배포가 무료여도 모델 호출 비용은 계속 발생할 수 있습니다. 그래서 운영의 핵심은 "의외의 지출과 조용한 오류를 빨리 잡는 것"입니다.

**OpenAI 사용량 제한**

[OpenAI Dashboard](https://platform.openai.com/usage)에서 월간 예산 한도를 설정해 두는 편이 안전합니다.

**Azure 비용 알람**

Azure를 쓴다면 Cost Management에서 Budget Alert를 설정해 두세요. 무료 범위 초과나 예산 80% 도달 시 알림을 받으면 비용 사고를 줄일 수 있습니다.

**배포 직후 확인할 신호**

- 첫 접속 속도: cold start가 체감상 어느 정도인지 확인합니다.
- HTTP 500 추적: Vercel Runtime Logs나 Azure Log Stream에서 원인을 바로 확인합니다.
- 사용자 질문 패턴: 실제 사용자가 어떤 프롬프트를 넣는지 관찰하면 다음 개선 방향이 보입니다.

![예산 제한과 오류 확인으로 이어지는 운영 점검 흐름](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/cost-guardrails-flow.ko.png)

*예산 제한과 오류 확인으로 이어지는 운영 점검 흐름*

## 배포 파이프라인 자동화

배포는 수동 클릭보다 선언형 파이프라인이 안정적입니다.

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

## 운영 설정: 타임아웃, 재시도, 헬스 체크

AI API는 네트워크와 공급자 상태에 영향을 받으므로, 배포 환경에서 반드시 시간 제한과 재시도 정책을 명시해야 합니다.

```python
CALL_TIMEOUT_SEC = 20
MAX_RETRY = 2
RETRY_BACKOFF_SEC = [0.5, 1.0]
```

헬스 체크 경로(`/healthz`)는 모델 호출을 포함하지 않고, 프로세스와 의존성 연결 상태만 빠르게 확인하도록 설계해야 합니다.

```bash
# 배포 후 10분 안에 실행하는 점검
curl -fsS https://api.example.com/healthz
curl -fsS https://api.example.com/api/ask \
  -H 'content-type: application/json' \
  -d '{"question":"상태 점검","user_id":"monitor"}'
```

## 롤백 기준을 미리 문서화하기

롤백은 실패했을 때 즉흥적으로 결정하면 늦습니다. 다음 기준을 사전에 합의해 두는 편이 좋습니다.

- 5분 평균 오류율이 5% 초과
- p95 지연 시간이 기준 대비 2배 이상 증가
- 인증 오류가 연속으로 발생

기준이 명시되어 있으면 담당자가 교대해도 같은 판단을 재현할 수 있습니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| API 키를 코드 저장소에 커밋 | 키 유출 → 무단 과금 및 보안 사고 | `.gitignore`에 `.env` 등록, 플랫폼 시크릿 관리 사용 |
| 시작 명령 미지정 (FastAPI) | 배포 성공했지만 앱 기동 실패 | `--startup-file` 에 gunicorn+uvicorn 명령 명시 |
| 환경 변수 수정 후 재배포 생략 | 이전 값으로 서비스 계속 운영 | 환경 변수 변경 후 반드시 재배포 트리거 |
| 로그 확인 없이 "배포 성공"으로 마무리 | 런타임 오류를 사용자가 먼저 발견 | 배포 직후 로그 스트림으로 에러 확인 |
| 비용 알람 미설정 | 토큰 폭증 시 월말에 과금 확인 | OpenAI 월 한도 + Azure Budget Alert 동시 설정 |
| 개발/운영 환경 모델 이름 불일치 | 디버깅 비용 증가, 품질 편차 | 환경별 모델 이름을 동일 환경 변수로 통일 |

## 운영 체크리스트

- [ ] 의존성 파일과 시작 명령을 배포 환경 기준으로 점검했다.
- [ ] API 키를 플랫폼 환경 변수로만 주입한다.
- [ ] 배포 직후 로그 확인 경로를 알고 있다.
- [ ] OpenAI와 클라우드 예산 알림을 설정했다.
- [ ] 헬스 체크 엔드포인트가 모델 호출 없이 동작 상태를 반환한다.
- [ ] 롤백 기준을 문서화했다.

## 정리

배포는 기능 구현의 마지막 단계가 아니라 운영의 첫 단계입니다.

- Vercel은 Next.js 같은 프론트엔드 중심 AI 앱에 빠른 출발점을 제공합니다.
- Azure App Service는 Python 백엔드를 올릴 때 유연하지만 시작 명령과 앱 설정을 더 명시해야 합니다.
- 환경 변수와 비밀 키 관리는 배포 설계의 일부입니다.
- 로그와 예산 알림을 먼저 걸어 두면 배포 후 문제를 훨씬 빨리 잡을 수 있습니다.

다음 글에서는 배포한 AI 앱이 실제로 잘 동작하는지 어떻게 평가하고 개선할지 봅니다.

## 처음 질문으로 돌아가기

- **배포는 단순 업로드가 아니라 무엇을 준비하는 과정일까요?**
  - 의존성 정리, 환경 변수 분리, 진입점 명시, 포트 설정이라는 네 가지를 서버가 이해할 수 있게 준비하는 과정입니다.
- **Next.js 앱과 Python 백엔드는 어떤 플랫폼에 먼저 올리는 편이 좋을까요?**
  - Next.js는 Vercel, Python FastAPI는 Azure App Service가 각각 진입 장벽이 낮습니다.
- **Vercel에서는 무엇을 가장 먼저 확인해야 할까요?**
  - 환경 변수(`OPENAI_API_KEY`)가 올바르게 주입됐는지와 빌드 로그에 에러가 없는지를 먼저 확인해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Web Development 101 (1/7): AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기](./01-hello-ai-api.md)
- [AI Web Development 101 (2/7): 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술](./02-prompt-engineering.md)
- [AI Web Development 101 (3/7): AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현](./03-ai-chatbot.md)
- [AI Web Development 101 (4/7): RAG 입문 — 내 데이터로 답하는 AI 만들기](./04-rag-intro.md)
- [AI Web Development 101 (5/7): AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기](./05-ai-agent.md)
- **AI Web Development 101 (6/7): AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기 (현재 글)**
- [AI 앱의 평가와 개선, 품질을 측정하고 더 좋게 만드는 법](./07-eval-improve.md)

<!-- toc:end -->

## 참고 자료
- [AI Web Development 101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/ai-web-dev-101/ko)

- [Vercel 공식 문서](https://vercel.com/docs)
- [Azure App Service Python 가이드](https://learn.microsoft.com/ko-kr/azure/app-service/quickstart-python)
- [OpenAI API 보안 권장 사항](https://platform.openai.com/docs/guides/production-best-practices/safety-and-best-practices)

Tags: AI, LLM, 웹 개발, Python, Tutorial
