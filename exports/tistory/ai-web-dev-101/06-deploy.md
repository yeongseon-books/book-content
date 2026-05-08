
# AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기

> AI 웹 개발 입문 시리즈 (6/7)

로컬에서 만든 AI 챗봇을 친구에게 보여주려면 URL이 필요합니다. 이번 글에서 로컬 프로젝트를 인터넷에 올리는 과정을 함께 해봅시다.

---

<!-- a-grade-intro:begin -->
## 핵심 질문

AI 웹 앱을 운영 환경에 배포할 때 비용·보안·확장성을 어떻게 함께 챙길 수 있을까요?

이 글은 그 질문에 답하기 위해 AI 웹 앱 배포의 핵심 개념과 실무 고려사항을 단계별로 살펴봅니다.

<!-- a-grade-intro:end -->

## 1. 배포란 무엇인가?

'배포(Deployment)'는 내 컴퓨터(Local)에서만 돌아가던 코드를 서버라는 큰 컴퓨터에 올려서, 인터넷 주소(URL)만 있으면 전 세계 누구나 접속할 수 있게 만드는 과정입니다.

로컬 환경과 서버 환경은 다릅니다. 내 컴퓨터에서는 `python app.py`나 `npm run dev`로 쉽게 실행했지만, 서버에서는 API 키를 어디에 둘지, 트래픽이 몰리면 어떻게 할지 등을 고민해야 합니다.

### 왜 배포가 필요한가요?
로컬 개발 환경은 나만의 실험실입니다. 하지만 실제 사용자는 내 컴퓨터에 들어와서 프로그램을 실행할 수 없죠. 배포는 내 코드를 24시간 깨어 있는 서버에 복사하고, 누구나 접속할 수 있는 '공인 IP'나 '도메인'을 부여하는 과정입니다. 이 과정에서 우리는 로컬에서 무심코 사용했던 설정들이 서버에서도 잘 작동할지 하나씩 점검하게 됩니다.

### 배포 전 체크리스트
- **의존성 정리**: 내 컴퓨터에 설치된 라이브러리 목록이 `requirements.txt` (Python)나 `package.json` (Node.js)에 정확히 기록되어 있나요? 서버는 이 파일을 보고 필요한 도구들을 설치합니다.
- **환경 변수 분리**: API 키를 코드에 직접 적어두면 GitHub에 올릴 때 전 세계에 공개됩니다. 반드시 환경 변수로 처리하고, 저장소에는 `.env.example` 같은 예시 파일만 남기세요.
- **애플리케이션 진입점**: 서버가 실행될 때 어떤 파일을 가장 먼저 실행해야 하는지(예: `app.py`, `index.js`) 명시되어 있나요?
- **포트(Port) 설정**: 대부분의 클라우드 서비스는 `PORT`라는 환경 변수를 통해 서버가 기다려야 할 포트 번호를 알려줍니다. 코드가 이를 유연하게 받아들이도록 작성되었는지 확인하세요.

**[그림] 로컬 개발 환경에서 실제 배포까지의 흐름**
![로컬 개발에서 실제 배포까지의 흐름](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/local-to-live-deployment.ko.png)

*로컬 개발에서 실제 배포까지의 흐름*

---

## 2. 배포 플랫폼 비교

초보 개발자가 가장 많이 사용하는 두 가지 플랫폼을 비교해 보겠습니다.

| 구분 | Vercel (버셀) | Azure App Service (애저) |
| :--- | :--- | :--- |
| **특징** | 프론트엔드 최적화, 설정이 거의 없음 | 기업용 서비스, Python/Node 등 자유로움 |
| **난이도** | 매우 쉬움 (GitHub 연결 끝) | 보통 (CLI나 포털 설정 필요) |
| **추천 대상** | Next.js, React 앱 배포 | Python Flask/FastAPI 백엔드 앱 |
| **비용** | 개인 프로젝트 무료 플랜 강력 | 일정 수준까지 무료지만 유료 전환 가능성 |

### 배포 플랫폼 선택: 어떤 걸 골라야 할까요?
처음 시작하신다면 고민이 많으실 겁니다. 간단한 규칙을 정해 드릴게요.
- **Vercel**: Next.js나 React로 예쁜 화면을 만들었고, 백엔드는 OpenAI SDK만 쓰면 될 때 선택하세요. "배포가 이렇게 쉬워?"라는 말이 절로 나옵니다.
- **Azure App Service**: Python(Flask, FastAPI)으로 데이터베이스를 직접 다루거나 복잡한 로직을 백엔드에 두었을 때 선택하세요. 기업용 안정성과 확장이 필요할 때 가장 든든한 동료가 됩니다.
- **기타 대안**: 더 자유로운 설정을 원한다면 AWS App Runner나 Google Cloud Run 같은 서비스도 있습니다. 하지만 초급 단계에서는 Vercel이나 Azure로 감을 잡는 것이 가장 빠릅니다.

![Vercel과 Azure의 배포 구조 비교](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/vercel-azure-hosting-overview.ko.png)

*Vercel과 Azure의 배포 구조 비교*

---

## 3. Part 1: Vercel에 배포하기 (가장 쉬운 경로)

Vercel은 GitHub 저장소를 연결하는 것만으로 배포가 끝납니다. 프론트엔드 중심의 AI 앱(예: Next.js + OpenAI SDK)에 가장 적합합니다.

### 1단계: GitHub에 코드 올리기

먼저 코드가 GitHub에 올라가 있어야 합니다.

```bash
git add .
git commit -m "feat: initial AI chatbot"
git push origin main
```

### 2단계: Vercel 연결 및 프로젝트 생성

1. [Vercel](https://vercel.com)에 로그인하고 **Add New > Project**를 누릅니다.
2. 내 GitHub 저장소를 가져옵니다(Import).
3. **Environment Variables** (환경 변수) 섹션을 찾으세요.

### 3단계: 환경 변수 설정 (중요!)

로컬에서 쓰던 키는 저장소에 올리지 말고, Vercel 설정 화면에 `OPENAI_API_KEY` 값으로 따로 입력해야 합니다.

*   **Key**: `OPENAI_API_KEY`
*   **Value**: OpenAI 대시보드에서 발급한 실제 키 값

이 과정을 거쳐야 Vercel 서버가 내 OpenAI 계정으로 요청을 보낼 수 있습니다.

### 4단계: 배포 완료와 최종 확인

**Deploy** 버튼을 누르면 실시간으로 빌드(Build) 로그가 흐릅니다. 빌드는 내 소스 코드를 서버가 실행 가능한 상태로 조립하는 과정입니다. 여기서 빨간색 에러 메시지가 뜬다면 오타가 있거나 라이브러리가 빠진 것이니 당황하지 말고 로그를 찬찬히 읽어보세요.

배포가 끝나면 `[프로젝트명].vercel.app` 형태의 도메인이 생성됩니다. 이 주소로 접속해 친구들과 공유해 보세요.

![배포된 앱으로 사용자 요청이 들어오는 운영 경로](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/production-request-path.ko.png)

*배포된 앱으로 사용자 요청이 들어오는 운영 경로*

### 운영 팁: 환경 변수 업데이트하기
OpenAI API 키를 교체했거나, 다른 설정을 바꿔야 할 때가 있습니다.
1. Vercel 프로젝트 대시보드에서 **Settings > Environment Variables**로 이동합니다.
2. 기존 값을 수정하고 저장합니다.
3. **Deployments** 탭에서 최신 항목 옆의 `...` 버튼을 눌러 **Redeploy**를 실행해야 수정된 환경 변수가 서버에 최종 적용됩니다. 단순히 설정만 바꾼다고 해서 즉시 반영되지 않는다는 점에 주의하세요!

---

## 4. Part 2: Azure App Service에 배포하기 (Python 백엔드)

Python(Flask, FastAPI)으로 만든 AI 앱이라면 Azure가 좋은 선택입니다.

### 1단계: Azure CLI 준비하기

먼저 내 컴퓨터에 Azure CLI(Command Line Interface)를 설치해야 합니다. 터미널에서 `az` 명령어를 쓸 수 있게 해주는 도구입니다.

```bash
# Azure 로그인: 브라우저 창이 뜨면 로그인하세요.
az login

# 현재 사용 중인 구독(Subscription) 목록을 확인합니다.
az account list --output table
```

### 2단계: 단 한 줄로 끝내는 배포 (`az webapp up`)

Azure에는 수많은 설정 메뉴가 있지만, 초보자라면 `az webapp up` 명령어가 마법과도 같은 경험을 줄 겁니다. 이 명령어는 자동으로 리소스 그룹(Resource Group)을 만들고, 요금제(App Service Plan)를 정하고, 코드를 압축해서 올려줍니다.

FastAPI를 올릴 때는 이 명령만으로 끝나지 않는다는 점을 먼저 기억하세요. App Service는 Python 앱을 받으면 배포 자체는 완료하지만, 어떤 ASGI 서버로 `main:app`을 띄울지 모르면 Azure 기본 플레이스홀더 페이지를 보여줄 수 있습니다.

예를 들어 프로젝트 루트에는 최소한 아래와 같은 `requirements.txt`가 있어야 합니다.

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

- `--sku F1`: 가장 낮은 무료 요금제를 쓰겠다는 뜻입니다. 연습용으로 딱이죠.
- `--name`: 내 웹 사이트 주소의 이름입니다. 전 세계에서 하나뿐이어야 하니 본인의 닉네임을 섞어 보세요. (`[내이름]-ai-app.azurewebsites.net`)
- `--location koreacentral`: 한국(서울) 데이터센터에 서버를 두겠다는 의미입니다. 지리적으로 가까워야 응답 속도가 빠릅니다.

배포가 끝나면 터미널 창에 JSON 형태의 결과가 나옵니다. 여기서 **Resource Group**의 이름(예: `[이름]_rg_Windows_koreacentral`)을 잘 메모해 두세요. 다음 단계에서 꼭 필요합니다.

그다음 FastAPI 앱의 시작 명령을 명시적으로 설정합니다.

```bash
az webapp config set \
  --resource-group myResourceGroup \
  --name <app-name> \
  --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app"
```

이 설정이 없으면 App Service가 내 FastAPI 앱 대신 기본 플레이스홀더 페이지를 반환할 수 있습니다. `gunicorn`이 워커 프로세스를 띄우고, `uvicorn.workers.UvicornWorker`가 ASGI 앱인 `main:app`을 실제로 실행한다고 이해하면 됩니다.

### 3단계: 환경 변수로 API 키 주입하기

로컬 비밀 파일은 GitHub에 올리지 않았으니, Azure 서버도 내 OpenAI API 키를 모르는 상태입니다. 앱 설정(App Settings) 메뉴를 통해 이를 알려줘야 합니다.

아래 명령을 실행하기 전에 로컬 셸에서 `export OPENAI_API_KEY="..."`처럼 환경 변수를 먼저 잡아 두세요. 그래야 실제 비밀 키 문자열이 셸 히스토리에 그대로 남지 않습니다.

```bash
# 메모해둔 리소스 그룹 이름을 --resource-group 뒤에 넣으세요.
az webapp config appsettings set \
  --name my-ai-chatbot-app \
  --resource-group [메모한-리소스-그룹-이름] \
  --settings OPENAI_API_KEY="$OPENAI_API_KEY"
```

이제 서버가 기지개를 켜고 OpenAI 서버와 대화할 준비를 마쳤습니다!

### 4단계: 실시간 로그로 '내 앱' 생존 확인하기

배포 후 사이트에 접속했는데 `Application Error`가 나온다면? 당황하지 말고 실시간 로그를 켜보세요.

```bash
# 실시간 로그 스트리밍 시작
az webapp log tail --name my-ai-chatbot-app --resource-group [리소스-그룹-이름]
```

로그는 서버가 내뱉는 생생한 목소리입니다. "OPENAI_API_KEY가 없습니다"라거나 "라이브러리 설치 실패" 같은 힌트를 주기 때문에 트래픽이 몰리는 운영 단계에서도 필수적인 명령어입니다.

---

## 5. API 키 보안

초보자가 가장 많이 하는 실수가 API 키를 소스 코드에 직접 적어서 GitHub에 올리는 것입니다.

### 환경 변수 사용법
코드에서는 `process.env.OPENAI_API_KEY` (JS)나 `os.getenv("OPENAI_API_KEY")` (Python)으로 값을 읽어와야 합니다. 이렇게 하면 코드는 그대로 두고, 배포 플랫폼(Vercel, Azure)의 설정 화면에서 키값만 바꿔 가며 운영할 수 있습니다.

### .env.example과 .gitignore의 관계
1.  저장소에는 `.env.example` 파일만 두고 필요한 변수 이름만 공유합니다.
2.  각 개발자는 이 예시 파일을 참고해 로컬에서 실제 `.env` 파일을 따로 만듭니다.
3.  `.gitignore` 파일에 반드시 `.env`를 추가하여 GitHub에 업로드되지 않게 막습니다.
4.  서버(Vercel, Azure)에는 각 플랫폼의 'Environment Variables' 메뉴를 통해 키값을 따로 입력합니다.

```text
# .gitignore 파일 예시
.env
__pycache__/
node_modules/
.venv/
.DS_Store
```

**[그림] 안전한 API 키 관리 vs 위험한 하드코딩**
![환경 변수 관리와 하드코딩 노출의 차이](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/secret-key-boundary.ko.png)

*환경 변수 관리와 하드코딩 노출의 차이*

---

## 6. 비용 관리와 모니터링 기초

AI 앱은 무료로 배포해도 LLM API 호출 비용이 발생합니다. 운영의 핵심은 '의외의 지출'을 막는 것입니다.

### 1. OpenAI 사용량 제한
[OpenAI Dashboard](https://platform.openai.com/usage)에서 한 달 최대 사용 금액(Monthly Budget)을 꼭 설정하세요. 예를 들어 $5로 설정해두면, 그 이상의 요청은 자동으로 차단되어 안심할 수 있습니다.

### 2. Azure 비용 알람
Azure를 쓴다면 'Cost Management' 메뉴에서 예산 알람(Budget Alert)을 설정하세요. 무료 범위를 넘기거나 설정한 금액의 80%에 도달했을 때 이메일을 받도록 설정하는 것이 좋습니다.

### 3. 실시간 모니터링
배포 직후에는 다음 세 가지 '생존 신호'를 체크하세요.
- **첫 접속 속도(Cold Start)**: 서버를 오랫동안 쓰지 않으면 잠들기도 합니다. 처음 접속할 때 '깨어나는' 데 시간이 얼마나 걸리는지 확인해 보세요.
- **HTTP 500 에러 추적**: 만약 "서버 내부 오류"가 뜬다면, Vercel의 'Runtime Logs'나 Azure의 'Log Stream'을 열어보세요. 코드 한 줄의 오타나 누락된 환경 변수 때문일 확률이 90%입니다.
- **사용자 질문 분석**: 사용자가 어떤 질문을 하는지, AI가 적절한 정보를 제공하는지 정기적으로 확인해 보세요. 이는 다음 7편에서 다룰 '서비스 개선'을 위한 가장 소중한 데이터가 됩니다.

![예산 제한과 오류 확인으로 이어지는 운영 점검 흐름](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/cost-guardrails-flow.ko.png)

*예산 제한과 오류 확인으로 이어지는 운영 점검 흐름*

---

## 시니어 엔지니어는 이렇게 생각합니다

- **환경별 시크릿은 플랫폼 시크릿 매니저에 둔다** — .env 파일을 커밋하지 말고 Vercel·Azure 시크릿 기능을 사용합니다.
- **배포 후에도 사용량 알림을 건다** — 예상치 못한 비용 폭주를 막기 위해 일·월 단위 알림이 필수입니다.
- **콜드 스타트를 의식한다** — 서버리스에서 첫 요청 지연이 UX를 망치므로 워밍업이나 프로비저닝을 고려합니다.
- **로그·메트릭·트레이스 셋을 모두 둔다** — 운영 문제는 한 가지 신호만으로는 진단이 안 되므로 세 축을 모두 수집합니다.
- **롤백 경로를 먼저 만든다** — 프롬프트·모델 변경이 회귀를 일으키므로 즉시 되돌릴 수 있어야 합니다.

## 시리즈 목차

- [AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기](./01-hello-ai-api.md)
- [프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술](./02-prompt-engineering.md)
- [AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현](./03-ai-chatbot.md)
- [RAG 입문 — 내 데이터로 답하는 AI 만들기](./04-rag-intro.md)
- [AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기](./05-ai-agent.md)
- **AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기 (현재 글)**
- AI 앱의 평가와 개선, 품질을 측정하고 더 좋게 만드는 법 (예정)

---

## 참고 자료
- [Vercel 공식 문서](https://vercel.com/docs)
- [Azure App Service Python 가이드](https://learn.microsoft.com/ko-kr/azure/app-service/quickstart-python)
- [OpenAI API 보안 권장 사항](https://platform.openai.com/docs/guides/production-best-practices/safety-and-best-practices)

Tags: AI, LLM, 웹 개발, Python, Tutorial

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
