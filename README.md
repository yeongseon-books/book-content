# Tech Blog

Medium 블로그 포스트 원고 저장소.

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

## 폴더 구조

```
tech-blog/
├── README.md
├── azure-app-service-101/
│   ├── 01-what-is-app-service.md
│   ├── ...
│   └── 07-scaling-101.md
├── ai-web-dev-101/
│   ├── 01-hello-ai-api.md
│   ├── 02-prompt-engineering.md
│   ├── 03-ai-chatbot.md
│   ├── 04-rag-intro.md
│   ├── 05-ai-agent.md
│   ├── 06-deploy.md
│   └── 07-eval-improve.md
└── assets/
    └── azure-app-service-101/
        ├── 01/
        ├── 02/
        ...
```

## 이미지 규칙

- 모든 이미지는 `assets/<시리즈>/<포스트번호>/` 폴더에 저장
- 파일명: `01-description.png` 형식
- Medium 업로드 시 직접 드래그 앤 드롭

## Medium 퍼블리싱 체크리스트

- [ ] 제목과 서브타이틀 확인
- [ ] 이미지 플레이스홀더에 실제 캡처 삽입
- [ ] 코드 블록 syntax highlighting 확인
- [ ] 태그 추가: `Azure`, `App Service`, `Cloud`, `DevOps`
- [ ] 시리즈 링크 연결
