# Series Index

전체 콘텐츠 시리즈의 목록과 발행 상태. 단일 출처는 [`series.yaml`](./series.yaml).

## Status Legend

| Status | Meaning |
| --- | --- |
| Planned | 기획 중 |
| Draft | 초안 작성 중 |
| Ready | 발행 준비 완료 |
| Needs Polish | 내용은 완성, 발행 전 다듬기 필요 |
| Published | 발행 완료 |
| Needs Update | 업데이트 필요 |

---

## Azure

### Azure App Service 101 (`azure-app-service-101`)

Azure App Service 입문 7부작 — 호스팅, 설정, 로그, 스케일링.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/azure-app-service-101/`](./content/azure-app-service-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure App Service란? - 플랫폼 아키텍처 이해하기 | [ko](./content/azure-app-service-101/ko/01-what-is-app-service.md) | [en](./content/azure-app-service-101/en/01-what-is-app-service.md) | [medium](./content/azure-app-service-101/medium/01.html) | Ready |
| 2 | Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까 | [ko](./content/azure-app-service-101/ko/02-request-lifecycle.md) | [en](./content/azure-app-service-101/en/02-request-lifecycle.md) | [medium](./content/azure-app-service-101/medium/02.html) | Ready |
| 3 | Hosting Models: 어떤 플랜을 선택해야 할까? | [ko](./content/azure-app-service-101/ko/03-hosting-models.md) | [en](./content/azure-app-service-101/en/03-hosting-models.md) | [medium](./content/azure-app-service-101/medium/03.html) | Needs Polish |
| 4 | 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask) | [ko](./content/azure-app-service-101/ko/04-first-deploy.md) | [en](./content/azure-app-service-101/en/04-first-deploy.md) | [medium](./content/azure-app-service-101/medium/04.html) | Needs Polish |
| 5 | Configuration 마스터하기: App Settings & 환경변수 | [ko](./content/azure-app-service-101/ko/05-configuration.md) | [en](./content/azure-app-service-101/en/05-configuration.md) | [medium](./content/azure-app-service-101/medium/05.html) | Needs Polish |
| 6 | 로그와 모니터링 기초: "앱이 느려요"에 답할 수 있는 상태 만들기 | [ko](./content/azure-app-service-101/ko/06-logging-monitoring.md) | [en](./content/azure-app-service-101/en/06-logging-monitoring.md) | [medium](./content/azure-app-service-101/medium/06.html) | Ready |
| 7 | Scaling 101: 언제 Scale Up vs Scale Out? | [ko](./content/azure-app-service-101/ko/07-scaling-101.md) | [en](./content/azure-app-service-101/en/07-scaling-101.md) | [medium](./content/azure-app-service-101/medium/07.html) | Ready |

### Azure App Service Deep Dive (`azure-app-service-deep-dive`)

App Service 내부 — Front-End, Worker, Sandbox, Kudu, Scaling.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/azure-app-service-deep-dive/`](./content/azure-app-service-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | App Service 플랫폼 아키텍처 — Front-End·Worker·File Server | [ko](./content/azure-app-service-deep-dive/ko/01-platform-architecture.md) | [en](./content/azure-app-service-deep-dive/en/01-platform-architecture.md) | [medium](./content/azure-app-service-deep-dive/medium/01.html) | Needs Polish |
| 2 | Front-End과 ARR — 요청은 어떻게 워커에 도달하는가 | [ko](./content/azure-app-service-deep-dive/ko/02-front-end-and-arr.md) | [en](./content/azure-app-service-deep-dive/en/02-front-end-and-arr.md) | [medium](./content/azure-app-service-deep-dive/medium/02.html) | Ready |
| 3 | Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가 | [ko](./content/azure-app-service-deep-dive/ko/03-worker-and-sandbox.md) | [en](./content/azure-app-service-deep-dive/en/03-worker-and-sandbox.md) | [medium](./content/azure-app-service-deep-dive/medium/03.html) | Needs Polish |
| 4 | 배포와 Kudu — 빌드·동기화·릴리스의 안쪽 | [ko](./content/azure-app-service-deep-dive/ko/04-deployment-and-kudu.md) | [en](./content/azure-app-service-deep-dive/en/04-deployment-and-kudu.md) | [medium](./content/azure-app-service-deep-dive/medium/04.html) | Ready |
| 5 | 스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로 | [ko](./content/azure-app-service-deep-dive/ko/05-scaling-internals.md) | [en](./content/azure-app-service-deep-dive/en/05-scaling-internals.md) | [medium](./content/azure-app-service-deep-dive/medium/05.html) | Needs Polish |
| 6 | 콜드 스타트와 Warmup — 첫 요청이 비싼 이유 | [ko](./content/azure-app-service-deep-dive/ko/06-cold-start-and-warmup.md) | [en](./content/azure-app-service-deep-dive/en/06-cold-start-and-warmup.md) | [medium](./content/azure-app-service-deep-dive/medium/06.html) | Ready |

### Azure Functions 101 (`azure-functions-101`)

Azure Functions 입문 7부작 — 트리거/바인딩부터 운영까지.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/azure-functions-101/`](./content/azure-functions-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Functions란? — 이벤트가 함수를 호출하는 세상 | [ko](./content/azure-functions-101/ko/01-what-is-azure-functions.md) | [en](./content/azure-functions-101/en/01-what-is-azure-functions.md) | [medium](./content/azure-functions-101/medium/01.html) | Ready |
| 2 | 트리거와 바인딩 — 함수 입출력의 모든 것 | [ko](./content/azure-functions-101/ko/02-triggers-and-bindings.md) | [en](./content/azure-functions-101/en/02-triggers-and-bindings.md) | [medium](./content/azure-functions-101/medium/02.html) | Ready |
| 3 | Host와 Worker — 함수는 누가 실행하는가 | [ko](./content/azure-functions-101/ko/03-host-and-worker.md) | [en](./content/azure-functions-101/en/03-host-and-worker.md) | [medium](./content/azure-functions-101/medium/03.html) | Ready |
| 4 | 함수 하나 배포하기 — 로컬에서 Azure까지 | [ko](./content/azure-functions-101/ko/04-first-deploy.md) | [en](./content/azure-functions-101/en/04-first-deploy.md) | [medium](./content/azure-functions-101/medium/04.html) | Needs Polish |
| 5 | 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated | [ko](./content/azure-functions-101/ko/05-choosing-a-plan.md) | [en](./content/azure-functions-101/en/05-choosing-a-plan.md) | [medium](./content/azure-functions-101/medium/05.html) | Ready |
| 6 | 스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간 | [ko](./content/azure-functions-101/ko/06-scaling-and-cold-start.md) | [en](./content/azure-functions-101/en/06-scaling-and-cold-start.md) | [medium](./content/azure-functions-101/medium/06.html) | Ready |
| 7 | 모니터링과 운영 기초 | [ko](./content/azure-functions-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-functions-101/en/07-monitoring-and-ops.md) | [medium](./content/azure-functions-101/medium/07.html) | Ready |

### Azure Functions Deep Dive (`azure-functions-deep-dive`)

Azure Functions Host 소스 분석 시리즈 (commit-pinned @ 5e59423).

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/azure-functions-deep-dive/`](./content/azure-functions-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기 | [ko](./content/azure-functions-deep-dive/ko/01-host-bootstrap.md) | [en](./content/azure-functions-deep-dive/en/01-host-bootstrap.md) | [medium](./content/azure-functions-deep-dive/medium/01.html) | Ready |
| 2 | Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법 | [ko](./content/azure-functions-deep-dive/ko/02-worker-process.md) | [en](./content/azure-functions-deep-dive/en/02-worker-process.md) | [medium](./content/azure-functions-deep-dive/medium/02.html) | Ready |
| 3 | gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가 | [ko](./content/azure-functions-deep-dive/ko/03-grpc-event-stream.md) | [en](./content/azure-functions-deep-dive/en/03-grpc-event-stream.md) | [medium](./content/azure-functions-deep-dive/medium/03.html) | Ready |
| 4 | Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 | [ko](./content/azure-functions-deep-dive/ko/04-dispatcher-and-invocation.md) | [en](./content/azure-functions-deep-dive/en/04-dispatcher-and-invocation.md) | [medium](./content/azure-functions-deep-dive/medium/04.html) | Needs Polish |
| 5 | 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이 | [ko](./content/azure-functions-deep-dive/ko/05-scaling-internals.md) | [en](./content/azure-functions-deep-dive/en/05-scaling-internals.md) | [medium](./content/azure-functions-deep-dive/medium/05.html) | Needs Polish |
| 6 | 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 | [ko](./content/azure-functions-deep-dive/ko/06-cold-start-placeholder.md) | [en](./content/azure-functions-deep-dive/en/06-cold-start-placeholder.md) | [medium](./content/azure-functions-deep-dive/medium/06.html) | Ready |

### Azure Kubernetes Service 101 (`azure-aks-101`)

AKS 입문 시리즈.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/azure-aks-101/`](./content/azure-aks-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes | [ko](./content/azure-aks-101/ko/01-what-is-aks.md) | [en](./content/azure-aks-101/en/01-what-is-aks.md) | [medium](./content/azure-aks-101/medium/01.html) | Needs Polish |
| 2 | 클러스터 아키텍처 — Control Plane과 Node Pool | [ko](./content/azure-aks-101/ko/02-cluster-architecture.md) | [en](./content/azure-aks-101/en/02-cluster-architecture.md) | [medium](./content/azure-aks-101/medium/02.html) | Needs Polish |
| 3 | 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI | [ko](./content/azure-aks-101/ko/03-first-cluster-and-deploy.md) | [en](./content/azure-aks-101/en/03-first-cluster-and-deploy.md) | [medium](./content/azure-aks-101/medium/03.html) | Needs Polish |
| 4 | Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식 | [ko](./content/azure-aks-101/ko/04-pod-deployment-service.md) | [en](./content/azure-aks-101/en/04-pod-deployment-service.md) | [medium](./content/azure-aks-101/medium/04.html) | Needs Polish |
| 5 | 네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길 | [ko](./content/azure-aks-101/ko/05-networking-and-ingress.md) | [en](./content/azure-aks-101/en/05-networking-and-ingress.md) | [medium](./content/azure-aks-101/medium/05.html) | Needs Polish |
| 6 | 스케일링 — HPA, Cluster Autoscaler, KEDA | [ko](./content/azure-aks-101/ko/06-scaling-hpa-ca-keda.md) | [en](./content/azure-aks-101/en/06-scaling-hpa-ca-keda.md) | [medium](./content/azure-aks-101/medium/06.html) | Needs Polish |
| 7 | 모니터링과 운영 — Container Insights, 로그, 알람 | [ko](./content/azure-aks-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-aks-101/en/07-monitoring-and-ops.md) | [medium](./content/azure-aks-101/medium/07.html) | Needs Polish |

### Azure Kubernetes Service Deep Dive (`azure-aks-deep-dive`)

AKS control plane / data plane 내부 동작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/azure-aks-deep-dive/`](./content/azure-aks-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Control Plane 해부 — AKS가 사용자에게서 가린 것 | [ko](./content/azure-aks-deep-dive/ko/01-control-plane-anatomy.md) | [en](./content/azure-aks-deep-dive/en/01-control-plane-anatomy.md) | [medium](./content/azure-aks-deep-dive/medium/01.html) | Needs Polish |
| 2 | kubelet과 containerd — 노드 위에서 컨테이너가 뜨기까지 | [ko](./content/azure-aks-deep-dive/ko/02-kubelet-and-containerd.md) | [en](./content/azure-aks-deep-dive/en/02-kubelet-and-containerd.md) | [medium](./content/azure-aks-deep-dive/medium/02.html) | Needs Polish |
| 3 | CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가 | [ko](./content/azure-aks-deep-dive/ko/03-cni-and-azure-cni-overlay.md) | [en](./content/azure-aks-deep-dive/en/03-cni-and-azure-cni-overlay.md) | [medium](./content/azure-aks-deep-dive/medium/03.html) | Needs Polish |
| 4 | Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가 | [ko](./content/azure-aks-deep-dive/ko/04-scheduler-and-pod-placement.md) | [en](./content/azure-aks-deep-dive/en/04-scheduler-and-pod-placement.md) | [medium](./content/azure-aks-deep-dive/medium/04.html) | Needs Polish |
| 5 | HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프 | [ko](./content/azure-aks-deep-dive/ko/05-hpa-and-cluster-autoscaler-internals.md) | [en](./content/azure-aks-deep-dive/en/05-hpa-and-cluster-autoscaler-internals.md) | [medium](./content/azure-aks-deep-dive/medium/05.html) | Needs Polish |
| 6 | KEDA 내부 — ScaledObject가 HPA를 만드는 방식 | [ko](./content/azure-aks-deep-dive/ko/06-keda-internals.md) | [en](./content/azure-aks-deep-dive/en/06-keda-internals.md) | [medium](./content/azure-aks-deep-dive/medium/06.html) | Needs Polish |

### Azure Container Apps 101 (`azure-aca-101`)

Container Apps 입문 시리즈.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/azure-aca-101/`](./content/azure-aca-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기 | [ko](./content/azure-aca-101/ko/01-what-is-aca.md) | [en](./content/azure-aca-101/en/01-what-is-aca.md) | [medium](./content/azure-aca-101/medium/01.html) | Needs Polish |
| 2 | Environment·Container App·Revision — 세 단어로 보는 ACA | [ko](./content/azure-aca-101/ko/02-environment-app-revision.md) | [en](./content/azure-aca-101/en/02-environment-app-revision.md) | [medium](./content/azure-aca-101/medium/02.html) | Needs Polish |
| 3 | 첫 앱 배포하기 — Python/FastAPI | [ko](./content/azure-aca-101/ko/03-first-deploy.md) | [en](./content/azure-aca-101/en/03-first-deploy.md) | [medium](./content/azure-aca-101/medium/03.html) | Needs Polish |
| 4 | Ingress와 트래픽 분할 — Revision 기반 배포 전략 | [ko](./content/azure-aca-101/ko/04-ingress-and-traffic-split.md) | [en](./content/azure-aca-101/en/04-ingress-and-traffic-split.md) | [medium](./content/azure-aca-101/medium/04.html) | Needs Polish |
| 5 | 스케일링 — KEDA scaler와 0-to-N | [ko](./content/azure-aca-101/ko/05-scaling-with-keda.md) | [en](./content/azure-aca-101/en/05-scaling-with-keda.md) | [medium](./content/azure-aca-101/medium/05.html) | Needs Polish |
| 6 | Dapr 통합 — 사이드카로 얻는 것 | [ko](./content/azure-aca-101/ko/06-dapr-integration.md) | [en](./content/azure-aca-101/en/06-dapr-integration.md) | [medium](./content/azure-aca-101/medium/06.html) | Needs Polish |
| 7 | 모니터링과 운영 — Log Analytics와 Application Insights | [ko](./content/azure-aca-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-aca-101/en/07-monitoring-and-ops.md) | [medium](./content/azure-aca-101/medium/07.html) | Needs Polish |

### Azure Container Apps Deep Dive (`azure-aca-deep-dive`)

ACA 위에 얹힌 KEDA·Dapr·Envoy 내부 동작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/azure-aca-deep-dive/`](./content/azure-aca-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것 | [ko](./content/azure-aca-deep-dive/ko/01-aca-architecture.md) | [en](./content/azure-aca-deep-dive/en/01-aca-architecture.md) | [medium](./content/azure-aca-deep-dive/medium/01.html) | Needs Polish |
| 2 | Environment 내부 — 네트워크·관측·Dapr 스코프의 경계 | [ko](./content/azure-aca-deep-dive/ko/02-environment-internals.md) | [en](./content/azure-aca-deep-dive/en/02-environment-internals.md) | [medium](./content/azure-aca-deep-dive/medium/02.html) | Ready |
| 3 | Revision과 트래픽 분할 — Envoy 가중치는 어디에서 오는가 | [ko](./content/azure-aca-deep-dive/ko/03-revision-and-traffic-split.md) | [en](./content/azure-aca-deep-dive/en/03-revision-and-traffic-split.md) | [medium](./content/azure-aca-deep-dive/medium/03.html) | Ready |
| 4 | ACA 안의 KEDA — Scale Rule이 만드는 것 | [ko](./content/azure-aca-deep-dive/ko/04-keda-in-aca.md) | [en](./content/azure-aca-deep-dive/en/04-keda-in-aca.md) | [medium](./content/azure-aca-deep-dive/medium/04.html) | Needs Polish |
| 5 | Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스 | [ko](./content/azure-aca-deep-dive/ko/05-dapr-sidecar-internals.md) | [en](./content/azure-aca-deep-dive/en/05-dapr-sidecar-internals.md) | [medium](./content/azure-aca-deep-dive/medium/05.html) | Needs Polish |
| 6 | Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지 | [ko](./content/azure-aca-deep-dive/ko/06-envoy-ingress-path.md) | [en](./content/azure-aca-deep-dive/en/06-envoy-ingress-path.md) | [medium](./content/azure-aca-deep-dive/medium/06.html) | Ready |

---

## AI

### AI 웹 개발 입문 (`ai-web-dev-101`)

AI API부터 배포까지, 초급 개발자를 위한 7부작. → LLM App Foundations 101로 재편 예정.

- 언어: ko
- 발행 대상: tistory, mkdocs, ebook
- 경로: [`content/ai-web-dev-101/`](./content/ai-web-dev-101/)

| # | Title | KO | Status |
| --- | --- | --- | --- |
| 1 | AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기 | [ko](./content/ai-web-dev-101/ko/01-hello-ai-api.md) | Needs Update |
| 2 | 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술 | [ko](./content/ai-web-dev-101/ko/02-prompt-engineering.md) | Needs Update |
| 3 | AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현 | [ko](./content/ai-web-dev-101/ko/03-ai-chatbot.md) | Needs Update |
| 4 | RAG 입문 — 내 데이터로 답하는 AI 만들기 | [ko](./content/ai-web-dev-101/ko/04-rag-intro.md) | Needs Update |
| 5 | AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기 | [ko](./content/ai-web-dev-101/ko/05-ai-agent.md) | Needs Update |
| 6 | AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기 | [ko](./content/ai-web-dev-101/ko/06-deploy.md) | Needs Update |
| 7 | AI 앱의 평가와 개선, 품질을 측정하고 더 좋게 만드는 법 | [ko](./content/ai-web-dev-101/ko/07-eval-improve.md) | Needs Update |

### LLM from Scratch 101 (`llm-from-scratch-101`)

PyTorch 2.x로 토크나이저부터 챗봇까지, ~720 LOC의 작은 GPT 9부작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/llm-from-scratch-101/`](./content/llm-from-scratch-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 글자를 숫자로 바꾸기 | [ko](./content/llm-from-scratch-101/ko/01-tokenizer.md) | [en](./content/llm-from-scratch-101/en/01-tokenizer.md) | [medium](./content/llm-from-scratch-101/medium/01.html) | Ready |
| 2 | 정수에서 벡터로, 그리고 위치 | [ko](./content/llm-from-scratch-101/ko/02-embedding.md) | [en](./content/llm-from-scratch-101/en/02-embedding.md) | [medium](./content/llm-from-scratch-101/medium/02.html) | Ready |
| 3 | 어떤 토큰을 얼마나 볼지 스스로 정하기 | [ko](./content/llm-from-scratch-101/ko/03-attention.md) | [en](./content/llm-from-scratch-101/en/03-attention.md) | [medium](./content/llm-from-scratch-101/medium/03.html) | Ready |
| 4 | 블록 하나, 깊이의 단위 | [ko](./content/llm-from-scratch-101/ko/04-transformer-block.md) | [en](./content/llm-from-scratch-101/en/04-transformer-block.md) | [medium](./content/llm-from-scratch-101/medium/04.html) | Ready |
| 5 | 조립: GPT 모델 클래스 완성 | [ko](./content/llm-from-scratch-101/ko/05-gpt-model.md) | [en](./content/llm-from-scratch-101/en/05-gpt-model.md) | [medium](./content/llm-from-scratch-101/medium/05.html) | Ready |
| 6 | 기울기로 배우기 | [ko](./content/llm-from-scratch-101/ko/06-training-loop.md) | [en](./content/llm-from-scratch-101/en/06-training-loop.md) | [medium](./content/llm-from-scratch-101/medium/06.html) | Ready |
| 7 | 샘플링 — 학습된 모델에서 글 뽑아내기 | [ko](./content/llm-from-scratch-101/ko/07-inference.md) | [en](./content/llm-from-scratch-101/en/07-inference.md) | [medium](./content/llm-from-scratch-101/medium/07.html) | Ready |
| 8 | 베이스 모델을 우리 작업에 맞추기 | [ko](./content/llm-from-scratch-101/ko/08-finetuning.md) | [en](./content/llm-from-scratch-101/en/08-finetuning.md) | [medium](./content/llm-from-scratch-101/medium/08.html) | Ready |
| 9 | 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 | [ko](./content/llm-from-scratch-101/ko/09-chatbot-wrapper.md) | [en](./content/llm-from-scratch-101/en/09-chatbot-wrapper.md) | [medium](./content/llm-from-scratch-101/medium/09.html) | Ready |

### RAG Deep Dive (`rag-deep-dive`)

LangChain · FAISS · RAGAS 소스로 따라가는 RAG 파이프라인 심층 분석.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/rag-deep-dive/`](./content/rag-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 문서 로딩과 청크 전략 — LangChain TextSplitter 내부 | [ko](./content/rag-deep-dive/ko/01-document-loading-and-chunking.md) | [en](./content/rag-deep-dive/en/01-document-loading-and-chunking.md) | [medium](./content/rag-deep-dive/medium/01.html) | Draft |
| 2 | 임베딩과 벡터 인덱스 — FAISS IndexFlatL2 동작 원리 | [ko](./content/rag-deep-dive/ko/02-embeddings-and-vector-index.md) | [en](./content/rag-deep-dive/en/02-embeddings-and-vector-index.md) | [medium](./content/rag-deep-dive/medium/02.html) | Draft |
| 3 | Retriever 설계 — VectorStoreRetriever와 MMR | [ko](./content/rag-deep-dive/ko/03-retriever-design.md) | [en](./content/rag-deep-dive/en/03-retriever-design.md) | [medium](./content/rag-deep-dive/medium/03.html) | Draft |
| 4 | 프롬프트 구성과 컨텍스트 주입 — PromptTemplate 내부 | [ko](./content/rag-deep-dive/ko/04-prompt-construction-and-context-injection.md) | [en](./content/rag-deep-dive/en/04-prompt-construction-and-context-injection.md) | [medium](./content/rag-deep-dive/medium/04.html) | Draft |
| 5 | RAG Chain 조립 — RetrievalQA vs LCEL | [ko](./content/rag-deep-dive/ko/05-rag-chain-assembly.md) | [en](./content/rag-deep-dive/en/05-rag-chain-assembly.md) | [medium](./content/rag-deep-dive/medium/05.html) | Draft |
| 6 | 평가와 품질 게이트 — RAGAS 메트릭과 Faithfulness | [ko](./content/rag-deep-dive/ko/06-evaluation-and-quality-gates.md) | [en](./content/rag-deep-dive/en/06-evaluation-and-quality-gates.md) | [medium](./content/rag-deep-dive/medium/06.html) | Draft |

### LLM App Foundations 101 (`llm-app-foundations-101`)

LLM API 기초, 토큰, 프롬프트 엔지니어링 6부작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/llm-app-foundations-101/`](./content/llm-app-foundations-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기 | [ko](./content/llm-app-foundations-101/ko/01-llm-api-basics.md) | [en](./content/llm-app-foundations-101/en/01-llm-api-basics.md) | [medium](./content/llm-app-foundations-101/medium/01.html) | Ready |
| 2 | 토큰 이해하기 — 비용, 한계, 컨텍스트 창 | [ko](./content/llm-app-foundations-101/ko/02-tokens.md) | [en](./content/llm-app-foundations-101/en/02-tokens.md) | [medium](./content/llm-app-foundations-101/medium/02.html) | Ready |
| 3 | 프롬프트 엔지니어링 기초 — System·User·Assistant 역할 | [ko](./content/llm-app-foundations-101/ko/03-prompt-engineering.md) | [en](./content/llm-app-foundations-101/en/03-prompt-engineering.md) | [medium](./content/llm-app-foundations-101/medium/03.html) | Ready |
| 4 | Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기 | [ko](./content/llm-app-foundations-101/ko/04-few-shot-cot.md) | [en](./content/llm-app-foundations-101/en/04-few-shot-cot.md) | [medium](./content/llm-app-foundations-101/medium/04.html) | Ready |
| 5 | 대화 상태 관리 — 멀티턴 챗봇 만들기 | [ko](./content/llm-app-foundations-101/ko/05-conversation-state.md) | [en](./content/llm-app-foundations-101/en/05-conversation-state.md) | [medium](./content/llm-app-foundations-101/medium/05.html) | Ready |
| 6 | 스트리밍 응답 처리 — 실시간으로 출력 받기 | [ko](./content/llm-app-foundations-101/ko/06-streaming.md) | [en](./content/llm-app-foundations-101/en/06-streaming.md) | [medium](./content/llm-app-foundations-101/medium/06.html) | Ready |

### LLM API Production 101 (`llm-api-production-101`)

Structured Output, Tool Calling, Streaming, Caching, Retry, Rate Limit 6부작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/llm-api-production-101/`](./content/llm-api-production-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 구조화 출력 — JSON 모드와 응답 스키마 | [ko](./content/llm-api-production-101/ko/01-structured-output.md) | [en](./content/llm-api-production-101/en/01-structured-output.md) | [medium](./content/llm-api-production-101/medium/01.html) | Ready |
| 2 | 툴 호출 — 함수를 모델에 연결하기 | [ko](./content/llm-api-production-101/ko/02-tool-calling.md) | [en](./content/llm-api-production-101/en/02-tool-calling.md) | [medium](./content/llm-api-production-101/medium/02.html) | Ready |
| 3 | 스트리밍 심화 — 청크 처리와 오류 복구 | [ko](./content/llm-api-production-101/ko/03-streaming-in-depth.md) | [en](./content/llm-api-production-101/en/03-streaming-in-depth.md) | [medium](./content/llm-api-production-101/medium/03.html) | Ready |
| 4 | 캐싱 전략 — 비용과 지연 시간 줄이기 | [ko](./content/llm-api-production-101/ko/04-caching-strategies.md) | [en](./content/llm-api-production-101/en/04-caching-strategies.md) | [medium](./content/llm-api-production-101/medium/04.html) | Ready |
| 5 | 재시도와 오류 처리 — 안정적인 API 호출 만들기 | [ko](./content/llm-api-production-101/ko/05-retry-and-error-handling.md) | [en](./content/llm-api-production-101/en/05-retry-and-error-handling.md) | [medium](./content/llm-api-production-101/medium/05.html) | Ready |
| 6 | 속도 제한 관리 — Rate Limit 대응 패턴 | [ko](./content/llm-api-production-101/ko/06-rate-limit-management.md) | [en](./content/llm-api-production-101/en/06-rate-limit-management.md) | [medium](./content/llm-api-production-101/medium/06.html) | Ready |

### Vector Search 101 (`vector-search-101`)

임베딩, FAISS, 코사인 유사도, 청크 전략 6부작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/vector-search-101/`](./content/vector-search-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기 | [ko](./content/vector-search-101/ko/01-what-is-embedding.md) | [en](./content/vector-search-101/en/01-what-is-embedding.md) | [medium](./content/vector-search-101/medium/01.html) | Ready |
| 2 | HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기 | [ko](./content/vector-search-101/ko/02-huggingface-embeddings.md) | [en](./content/vector-search-101/en/02-huggingface-embeddings.md) | [medium](./content/vector-search-101/medium/02.html) | Ready |
| 3 | 코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기 | [ko](./content/vector-search-101/ko/03-cosine-similarity.md) | [en](./content/vector-search-101/en/03-cosine-similarity.md) | [medium](./content/vector-search-101/medium/03.html) | Ready |
| 4 | FAISS 입문 — 고속 근사 최근접 이웃 검색 | [ko](./content/vector-search-101/ko/04-faiss-intro.md) | [en](./content/vector-search-101/en/04-faiss-intro.md) | [medium](./content/vector-search-101/medium/04.html) | Ready |
| 5 | 청크 전략 — 긴 문서를 어떻게 나눌 것인가 | [ko](./content/vector-search-101/ko/05-chunking-strategies.md) | [en](./content/vector-search-101/en/05-chunking-strategies.md) | [medium](./content/vector-search-101/medium/05.html) | Ready |
| 6 | 벡터 검색 파이프라인 — 문서 수집부터 쿼리까지 | [ko](./content/vector-search-101/ko/06-vector-search-pipeline.md) | [en](./content/vector-search-101/en/06-vector-search-pipeline.md) | [medium](./content/vector-search-101/medium/06.html) | Ready |

### LangChain 101 (`langchain-101`)

LCEL, Runnable, Retriever, Tool Calling, Streaming 6부작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/langchain-101/`](./content/langchain-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | LangChain 소개 — LCEL과 Runnable 기본 | [ko](./content/langchain-101/ko/01-lcel-basics.md) | [en](./content/langchain-101/en/01-lcel-basics.md) | [medium](./content/langchain-101/medium/01.html) | Ready |
| 2 | Prompt와 LLM Chain — 체인 첫 번째 구성 | [ko](./content/langchain-101/ko/02-prompt-llm-chain.md) | [en](./content/langchain-101/en/02-prompt-llm-chain.md) | [medium](./content/langchain-101/medium/02.html) | Ready |
| 3 | Retriever — 문서 검색과 컨텍스트 주입 | [ko](./content/langchain-101/ko/03-retriever.md) | [en](./content/langchain-101/en/03-retriever.md) | [medium](./content/langchain-101/medium/03.html) | Ready |
| 4 | Tool Calling — 외부 도구 연결하기 | [ko](./content/langchain-101/ko/04-tool-calling.md) | [en](./content/langchain-101/en/04-tool-calling.md) | [medium](./content/langchain-101/medium/04.html) | Ready |
| 5 | Streaming — 실시간 출력 처리 | [ko](./content/langchain-101/ko/05-streaming.md) | [en](./content/langchain-101/en/05-streaming.md) | [medium](./content/langchain-101/medium/05.html) | Ready |
| 6 | 실전 체인 조립 — 컴포넌트를 하나로 연결하기 | [ko](./content/langchain-101/ko/06-full-chain.md) | [en](./content/langchain-101/en/06-full-chain.md) | [medium](./content/langchain-101/medium/06.html) | Ready |

### AI App Patterns 101 (`ai-app-patterns-101`)

챗봇, RAG Q&A, Agent, 워크플로, Human-in-the-loop 설계 패턴 6부작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/ai-app-patterns-101/`](./content/ai-app-patterns-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 챗봇 패턴 — 대화 이력 관리와 상태 | [ko](./content/ai-app-patterns-101/ko/01-chatbot-pattern.md) | [en](./content/ai-app-patterns-101/en/01-chatbot-pattern.md) | [medium](./content/ai-app-patterns-101/medium/01.html) | Ready |
| 2 | RAG Q&A 패턴 — 문서 기반 질의응답 | [ko](./content/ai-app-patterns-101/ko/02-rag-qa-pattern.md) | [en](./content/ai-app-patterns-101/en/02-rag-qa-pattern.md) | [medium](./content/ai-app-patterns-101/medium/02.html) | Ready |
| 3 | 문서 어시스턴트 — 요약, 추출, 분류 | [ko](./content/ai-app-patterns-101/ko/03-document-assistant.md) | [en](./content/ai-app-patterns-101/en/03-document-assistant.md) | [medium](./content/ai-app-patterns-101/medium/03.html) | Ready |
| 4 | Agent + Tool 패턴 — 자율 도구 선택 | [ko](./content/ai-app-patterns-101/ko/04-agent-tool-pattern.md) | [en](./content/ai-app-patterns-101/en/04-agent-tool-pattern.md) | [medium](./content/ai-app-patterns-101/medium/04.html) | Ready |
| 5 | 워크플로 자동화 — 다단계 체인 설계 | [ko](./content/ai-app-patterns-101/ko/05-workflow-automation.md) | [en](./content/ai-app-patterns-101/en/05-workflow-automation.md) | [medium](./content/ai-app-patterns-101/medium/05.html) | Ready |
| 6 | Human-in-the-loop — 사람 개입 설계 패턴 | [ko](./content/ai-app-patterns-101/ko/06-human-in-the-loop.md) | [en](./content/ai-app-patterns-101/en/06-human-in-the-loop.md) | [medium](./content/ai-app-patterns-101/medium/06.html) | Ready |

### Korean AI Stack 101 (`korean-ai-stack-101`)

한국어 임베딩, OCR, HyperCLOVA X, Solar 실전 6부작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/korean-ai-stack-101/`](./content/korean-ai-stack-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar | [ko](./content/korean-ai-stack-101/ko/01-korean-embedding-models.md) | [en](./content/korean-ai-stack-101/en/01-korean-embedding-models.md) | [medium](./content/korean-ai-stack-101/medium/01.html) | Ready |
| 2 | KoSimCSE로 문장 유사도 구현하기 | [ko](./content/korean-ai-stack-101/ko/02-kosimcse-similarity.md) | [en](./content/korean-ai-stack-101/en/02-kosimcse-similarity.md) | [medium](./content/korean-ai-stack-101/medium/02.html) | Ready |
| 3 | BGE-M3 다국어 임베딩 실전 | [ko](./content/korean-ai-stack-101/ko/03-bge-m3-multilingual.md) | [en](./content/korean-ai-stack-101/en/03-bge-m3-multilingual.md) | [medium](./content/korean-ai-stack-101/medium/03.html) | Ready |
| 4 | CLOVA OCR API로 문서 텍스트 추출 | [ko](./content/korean-ai-stack-101/ko/04-clova-ocr.md) | [en](./content/korean-ai-stack-101/en/04-clova-ocr.md) | [medium](./content/korean-ai-stack-101/medium/04.html) | Ready |
| 5 | HyperCLOVA X와 Solar API 사용하기 | [ko](./content/korean-ai-stack-101/ko/05-hyperclova-solar.md) | [en](./content/korean-ai-stack-101/en/05-hyperclova-solar.md) | [medium](./content/korean-ai-stack-101/medium/05.html) | Ready |
| 6 | 한국어 RAG 파이프라인 조합하기 | [ko](./content/korean-ai-stack-101/ko/06-korean-rag-pipeline.md) | [en](./content/korean-ai-stack-101/en/06-korean-rag-pipeline.md) | [medium](./content/korean-ai-stack-101/medium/06.html) | Ready |

### Document Ingestion 101 (`document-ingestion-101`)

PDF 파싱, 청킹, 메타데이터, 증분 인덱싱 6부작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/document-ingestion-101/`](./content/document-ingestion-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | PDF 파싱과 텍스트 추출 | [ko](./content/document-ingestion-101/ko/01-pdf-parsing.md) | [en](./content/document-ingestion-101/en/01-pdf-parsing.md) | [medium](./content/document-ingestion-101/medium/01.html) | Ready |
| 2 | 청킹 전략 — 문서 유형별 최적화 | [ko](./content/document-ingestion-101/ko/02-chunking-strategies.md) | [en](./content/document-ingestion-101/en/02-chunking-strategies.md) | [medium](./content/document-ingestion-101/medium/02.html) | Ready |
| 3 | 메타데이터 설계와 필터링 | [ko](./content/document-ingestion-101/ko/03-metadata-design.md) | [en](./content/document-ingestion-101/en/03-metadata-design.md) | [medium](./content/document-ingestion-101/medium/03.html) | Ready |
| 4 | 증분 인덱싱 — 변경된 문서만 업데이트 | [ko](./content/document-ingestion-101/ko/04-incremental-indexing.md) | [en](./content/document-ingestion-101/en/04-incremental-indexing.md) | [medium](./content/document-ingestion-101/medium/04.html) | Ready |
| 5 | 다중 포맷 문서 파이프라인 | [ko](./content/document-ingestion-101/ko/05-multi-format-pipeline.md) | [en](./content/document-ingestion-101/en/05-multi-format-pipeline.md) | [medium](./content/document-ingestion-101/medium/05.html) | Ready |
| 6 | 문서 수집 파이프라인 완성 | [ko](./content/document-ingestion-101/ko/06-complete-pipeline.md) | [en](./content/document-ingestion-101/en/06-complete-pipeline.md) | [medium](./content/document-ingestion-101/medium/06.html) | Ready |

### LLM Apps Ops 101 (`llm-apps-ops-101`)

모니터링, 비용, 평가, 보안, 배포 6부작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/llm-apps-ops-101/`](./content/llm-apps-ops-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | LLM 앱 모니터링과 로깅 | [ko](./content/llm-apps-ops-101/ko/01-monitoring-and-logging.md) | [en](./content/llm-apps-ops-101/en/01-monitoring-and-logging.md) | [medium](./content/llm-apps-ops-101/medium/01.html) | Ready |
| 2 | LLM 비용 추적과 최적화 | [ko](./content/llm-apps-ops-101/ko/02-cost-tracking.md) | [en](./content/llm-apps-ops-101/en/02-cost-tracking.md) | [medium](./content/llm-apps-ops-101/medium/02.html) | Ready |
| 3 | LLM 출력 품질 평가 | [ko](./content/llm-apps-ops-101/ko/03-evaluation.md) | [en](./content/llm-apps-ops-101/en/03-evaluation.md) | [medium](./content/llm-apps-ops-101/medium/03.html) | Ready |
| 4 | LLM 앱 보안 | [ko](./content/llm-apps-ops-101/ko/04-security.md) | [en](./content/llm-apps-ops-101/en/04-security.md) | [medium](./content/llm-apps-ops-101/medium/04.html) | Ready |
| 5 | LLM 앱 배포 전략 | [ko](./content/llm-apps-ops-101/ko/05-deployment.md) | [en](./content/llm-apps-ops-101/en/05-deployment.md) | [medium](./content/llm-apps-ops-101/medium/05.html) | Ready |
| 6 | LLM 앱 운영 완성 | [ko](./content/llm-apps-ops-101/ko/06-ops-complete.md) | [en](./content/llm-apps-ops-101/en/06-ops-complete.md) | [medium](./content/llm-apps-ops-101/medium/06.html) | Ready |

### RAG Benchmark 101 (`rag-benchmark-101`)

VectorDB, 임베딩 모델, 검색, RAG 파이프라인 평가 6부작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/rag-benchmark-101/`](./content/rag-benchmark-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | RAG 평가 지표 이해 | [ko](./content/rag-benchmark-101/ko/01-evaluation-metrics.md) | [en](./content/rag-benchmark-101/en/01-evaluation-metrics.md) | [medium](./content/rag-benchmark-101/medium/01.html) | Ready |
| 2 | 검색 성능 측정 | [ko](./content/rag-benchmark-101/ko/02-retrieval-benchmarking.md) | [en](./content/rag-benchmark-101/en/02-retrieval-benchmarking.md) | [medium](./content/rag-benchmark-101/medium/02.html) | Ready |
| 3 | 임베딩 모델 비교 | [ko](./content/rag-benchmark-101/ko/03-embedding-comparison.md) | [en](./content/rag-benchmark-101/en/03-embedding-comparison.md) | [medium](./content/rag-benchmark-101/medium/03.html) | Ready |
| 4 | VectorDB 선택 기준 | [ko](./content/rag-benchmark-101/ko/04-vectordb-selection.md) | [en](./content/rag-benchmark-101/en/04-vectordb-selection.md) | [medium](./content/rag-benchmark-101/medium/04.html) | Ready |
| 5 | 종단 간 RAG 파이프라인 평가 | [ko](./content/rag-benchmark-101/ko/05-e2e-evaluation.md) | [en](./content/rag-benchmark-101/en/05-e2e-evaluation.md) | [medium](./content/rag-benchmark-101/medium/05.html) | Ready |
| 6 | RAG 벤치마크 완성 | [ko](./content/rag-benchmark-101/ko/06-benchmark-complete.md) | [en](./content/rag-benchmark-101/en/06-benchmark-complete.md) | [medium](./content/rag-benchmark-101/medium/06.html) | Ready |

### LangGraph 101 (`langgraph-101`)

그래프 에이전트, 체크포인트, 멀티 에이전트 6부작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/langgraph-101/`](./content/langgraph-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | LangGraph 소개와 그래프 기초 | [ko](./content/langgraph-101/ko/01-graph-basics.md) | [en](./content/langgraph-101/en/01-graph-basics.md) | [medium](./content/langgraph-101/medium/01.html) | Ready |
| 2 | 상태 관리와 체크포인트 | [ko](./content/langgraph-101/ko/02-state-and-checkpoints.md) | [en](./content/langgraph-101/en/02-state-and-checkpoints.md) | [medium](./content/langgraph-101/medium/02.html) | Ready |
| 3 | 조건부 엣지와 분기 흐름 | [ko](./content/langgraph-101/ko/03-conditional-edges.md) | [en](./content/langgraph-101/en/03-conditional-edges.md) | [medium](./content/langgraph-101/medium/03.html) | Ready |
| 4 | 도구 호출 에이전트 | [ko](./content/langgraph-101/ko/04-tool-calling-agent.md) | [en](./content/langgraph-101/en/04-tool-calling-agent.md) | [medium](./content/langgraph-101/medium/04.html) | Ready |
| 5 | 멀티 에이전트 시스템 | [ko](./content/langgraph-101/ko/05-multi-agent.md) | [en](./content/langgraph-101/en/05-multi-agent.md) | [medium](./content/langgraph-101/medium/05.html) | Ready |
| 6 | LangGraph 완성 | [ko](./content/langgraph-101/ko/06-langgraph-complete.md) | [en](./content/langgraph-101/en/06-langgraph-complete.md) | [medium](./content/langgraph-101/medium/06.html) | Ready |

### LLM Fine-tuning 101 (`llm-finetuning-101`)

LoRA, 데이터셋, 학습, 평가, 서빙 6부작.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/llm-finetuning-101/`](./content/llm-finetuning-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | LLM 파인튜닝 입문 | [ko](./content/llm-finetuning-101/ko/01-intro.md) | [en](./content/llm-finetuning-101/en/01-intro.md) | [medium](./content/llm-finetuning-101/medium/01.html) | Ready |
| 2 | 데이터셋 준비와 전처리 | [ko](./content/llm-finetuning-101/ko/02-dataset.md) | [en](./content/llm-finetuning-101/en/02-dataset.md) | [medium](./content/llm-finetuning-101/medium/02.html) | Ready |
| 3 | LoRA 어댑터 구성 | [ko](./content/llm-finetuning-101/ko/03-lora.md) | [en](./content/llm-finetuning-101/en/03-lora.md) | [medium](./content/llm-finetuning-101/medium/03.html) | Ready |
| 4 | 학습 루프와 하이퍼파라미터 | [ko](./content/llm-finetuning-101/ko/04-training.md) | [en](./content/llm-finetuning-101/en/04-training.md) | [medium](./content/llm-finetuning-101/medium/04.html) | Ready |
| 5 | 모델 평가 | [ko](./content/llm-finetuning-101/ko/05-evaluation.md) | [en](./content/llm-finetuning-101/en/05-evaluation.md) | [medium](./content/llm-finetuning-101/medium/05.html) | Ready |
| 6 | 모델 서빙 | [ko](./content/llm-finetuning-101/ko/06-serving.md) | [en](./content/llm-finetuning-101/en/06-serving.md) | [medium](./content/llm-finetuning-101/medium/06.html) | Ready |

---

## AX (Planned)

### AX 실전 가이드 (`ax-practical-guide`)

AX 도입 전략, 업무 자동화 사례, 조직 변화 관리.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/ax-practical-guide/`](./content/ax-practical-guide/)

_articles not yet enumerated._

---

## Writing (Planned)

### 엔지니어를 위한 기술 글쓰기 (`technical-writing`)

시리즈를 설계하고, 한 편을 다듬는 법.

- 언어: ko, en
- 발행 대상: tistory, medium, mkdocs, ebook
- 경로: [`content/technical-writing/`](./content/technical-writing/)

_articles not yet enumerated._

---

## 발행 우선순위 TOP 10

| 순위 | 시리즈 | 글 | 이유 |
| --- | --- | --- | --- |
| 1 | azure-functions-101 | 03-host-and-worker | 사용자의 차별성 최고 |
| 2 | azure-functions-deep-dive | 01-host-bootstrap | source-pinned 강점 |
| 3 | azure-functions-deep-dive | 02-worker-process | Python Functions와 연결 강함 |
| 4 | azure-app-service-deep-dive | 04-deployment-and-kudu | 실무 검색 가치 큼 |
| 5 | azure-app-service-101 | 02-request-lifecycle | 장애 분석과 연결 |
| 6 | azure-aca-deep-dive | 06-envoy-ingress-path | ACA ingress 실무 경험 |
| 7 | azure-app-service-101 | 06-logging-monitoring | 고객 대응/지원 연결 |
| 8 | rag-deep-dive | 01-document-loading-and-chunking | AI 실무 독자 |
| 9 | azure-functions-101 | 05-choosing-a-plan | 검색 유입 가능 |
| 10 | azure-functions-101 | 06-scaling-and-cold-start | 비용/성능 검색 수요 |
