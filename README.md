# Tech Blog

블로그 포스트 원고 저장소. **한국어는 Tistory**, **영어는 Medium**에 발행합니다.

## 시리즈

### Azure App Service 101

Azure App Service 입문자를 위한 실전 가이드 시리즈.

| # | 제목 | 파일 | 예상 분량 |
|---|---|---|---|
| 1 | Azure App Service란? - 플랫폼 아키텍처 이해하기 | [01-what-is-app-service.md](./azure-app-service-101/01-what-is-app-service.md) | 8분 |
| 2 | Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까 | [02-request-lifecycle.md](./azure-app-service-101/02-request-lifecycle.md) | 7분 |
| 3 | Hosting Models: 어떤 플랜을 선택해야 할까? | [03-hosting-models.md](./azure-app-service-101/03-hosting-models.md) | 6분 |
| 4 | 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask) | [04-first-deploy.md](./azure-app-service-101/04-first-deploy.md) | 10분 |
| 5 | Configuration 마스터하기: App Settings & 환경변수 | [05-configuration.md](./azure-app-service-101/05-configuration.md) | 7분 |
| 6 | 로그와 모니터링 기초 | [06-logging-monitoring.md](./azure-app-service-101/06-logging-monitoring.md) | 8분 |
| 7 | Scaling 101: 언제 Scale Up vs Scale Out? | [07-scaling-101.md](./azure-app-service-101/07-scaling-101.md) | 6분 |

### AI 웹 개발 입문

AI API부터 배포까지, 초급 개발자를 위한 AI 웹 개발 실전 가이드 시리즈.

| # | 제목 | 파일 | 예상 분량 |
|---|---|---|---|
| 1 | AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기 | [01-hello-ai-api.md](./ai-web-dev-101/01-hello-ai-api.md) | 10분 |
| 2 | 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술 | [02-prompt-engineering.md](./ai-web-dev-101/02-prompt-engineering.md) | 8분 |
| 3 | AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현 | [03-ai-chatbot.md](./ai-web-dev-101/03-ai-chatbot.md) | 10분 |
| 4 | RAG 입문 — 내 데이터로 답하는 AI 만들기 | [04-rag-intro.md](./ai-web-dev-101/04-rag-intro.md) | 10분 |
| 5 | AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기 | [05-ai-agent.md](./ai-web-dev-101/05-ai-agent.md) | 10분 |
| 6 | AI 웹 앱 배포하기 — Vercel과 Azure에 올리고 운영하기 | [06-deploy.md](./ai-web-dev-101/06-deploy.md) | 9분 |
| 7 | AI 앱의 평가와 개선 — 품질을 측정하고 더 좋게 만드는 법 | [07-eval-improve.md](./ai-web-dev-101/07-eval-improve.md) | 10분 |

### Azure Functions 101

Azure Functions 입문자를 위한 실전 가이드 시리즈. 트리거·바인딩부터 플랜 선택, 콜드 스타트, 모니터링까지.

| # | 제목 | 한국어 (Tistory) | English (Medium) |
|---|---|---|---|
| 1 | Azure Functions란? — 이벤트 기반 서버리스 컴퓨팅 | [ko](./azure-functions-101/ko/01-what-is-azure-functions.md) | [en](./azure-functions-101/en/01-what-is-azure-functions.md) |
| 2 | Triggers & Bindings — 함수가 일을 시작하고 끝내는 방식 | [ko](./azure-functions-101/ko/02-triggers-and-bindings.md) | [en](./azure-functions-101/en/02-triggers-and-bindings.md) |
| 3 | Host와 Worker — 한 함수 앱 안에 두 프로세스가 사는 이유 | [ko](./azure-functions-101/ko/03-host-and-worker.md) | [en](./azure-functions-101/en/03-host-and-worker.md) |
| 4 | 첫 번째 배포 — 로컬에서 Azure까지 | [ko](./azure-functions-101/ko/04-first-deploy.md) | [en](./azure-functions-101/en/04-first-deploy.md) |
| 5 | 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated | [ko](./azure-functions-101/ko/05-choosing-a-plan.md) | [en](./azure-functions-101/en/05-choosing-a-plan.md) |
| 6 | 스케일링과 콜드 스타트 — 사용자가 알아야 할 만큼만 | [ko](./azure-functions-101/ko/06-scaling-and-cold-start.md) | [en](./azure-functions-101/en/06-scaling-and-cold-start.md) |
| 7 | 모니터링과 운영 — Application Insights·KQL·알람 | [ko](./azure-functions-101/ko/07-monitoring-and-ops.md) | [en](./azure-functions-101/en/07-monitoring-and-ops.md) |

### Azure Functions Deep Dive

Azure Functions Host의 내부 동작을 코드 레벨로 따라가는 시리즈. 모든 코드 인용은 [`Azure/azure-functions-host` @ `5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7) 기준이며, 학술적 관점은 Microsoft 연구진의 USENIX ATC'20 논문(Shahrad et al.)을 인용합니다.

| # | 제목 | 한국어 (Tistory) | English (Medium) |
|---|---|---|---|
| 1 | Host Bootstrap — `dotnet Microsoft.Azure.WebJobs.Script.WebHost.dll`이 일으키는 일 | [ko](./azure-functions-deep-dive/ko/01-host-bootstrap.md) | [en](./azure-functions-deep-dive/en/01-host-bootstrap.md) |
| 2 | Worker Process — 호스트는 왜 사용자 코드를 직접 실행하지 않는가 | [ko](./azure-functions-deep-dive/ko/02-worker-process.md) | [en](./azure-functions-deep-dive/en/02-worker-process.md) |
| 3 | gRPC Event Stream — 호스트와 워커의 단 하나의 양방향 채널 | [ko](./azure-functions-deep-dive/ko/03-grpc-event-stream.md) | [en](./azure-functions-deep-dive/en/03-grpc-event-stream.md) |
| 4 | Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 | [ko](./azure-functions-deep-dive/ko/04-dispatcher-and-invocation.md) | [en](./azure-functions-deep-dive/en/04-dispatcher-and-invocation.md) |
| 5 | 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 플랜별 차이 | [ko](./azure-functions-deep-dive/ko/05-scaling-internals.md) | [en](./azure-functions-deep-dive/en/05-scaling-internals.md) |
| 6 | 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 | [ko](./azure-functions-deep-dive/ko/06-cold-start-placeholder.md) | [en](./azure-functions-deep-dive/en/06-cold-start-placeholder.md) |
| 7 | 학술적 관점 — Azure Functions를 분석한 논문들 | [ko](./azure-functions-deep-dive/ko/07-academic-perspective.md) | [en](./azure-functions-deep-dive/en/07-academic-perspective.md) |

## 폴더 구조

```
tech-blog/
├── README.md
├── azure-app-service-101/
│   ├── 01-what-is-app-service.md
│   └── ... (07까지)
├── ai-web-dev-101/
│   ├── 01-hello-ai-api.md
│   └── ... (07까지)
├── azure-functions-101/
│   ├── ko/                 # Tistory 발행본 (한국어 원본)
│   │   ├── 01-what-is-azure-functions.md
│   │   └── ... (07까지)
│   └── en/                 # Medium 발행본 (영어 번역본)
│       ├── 01-what-is-azure-functions.md
│       └── ... (07까지)
├── azure-functions-deep-dive/
│   ├── ko/
│   │   ├── 01-host-bootstrap.md
│   │   └── ... (07까지)
│   └── en/
│       ├── 01-host-bootstrap.md
│       └── ... (07까지)
└── assets/
    ├── azure-app-service-101/
    │   ├── 01/
    │   └── ...
    ├── azure-functions-101/
    │   ├── ko/<번호>/
    │   └── en/<번호>/
    └── azure-functions-deep-dive/
        ├── ko/<번호>/
        └── en/<번호>/
```

## 이미지 규칙

- 모든 이미지는 `assets/<시리즈>/<번호>/` 또는 `assets/<시리즈>/<ko|en>/<번호>/` 에 저장
- 파일명: `01-description.png` 형식
- 다이어그램은 가능한 한 Mermaid로 작성. Tistory 발행 시 PNG로 export하여 첨부
- Medium 업로드 시 직접 드래그 앤 드롭

## 발행처 매핑

| 언어 | 플랫폼 | 비고 |
|---|---|---|
| 한국어 | Tistory | 원본. Mermaid는 PNG로 export |
| 영어 | Medium | 번역본. Mermaid는 plugin 또는 PNG |

## 퍼블리싱 체크리스트

- [ ] 제목과 서브타이틀 확인
- [ ] 이미지 플레이스홀더에 실제 캡처 삽입
- [ ] Mermaid 다이어그램 렌더링 확인 / PNG export
- [ ] 코드 블록 syntax highlighting 확인
- [ ] 1차 출처 링크가 commit-pinned (`5e59423`) 상태인지 확인 (Deep Dive 시리즈 한정)
- [ ] 태그 추가
  - Azure Functions 101: `Azure`, `Azure Functions`, `Serverless`, `Cloud`
  - Azure Functions Deep Dive: `Azure Functions`, `Serverless`, `Distributed Systems`, `gRPC`
- [ ] 시리즈 내 상호 링크 연결
