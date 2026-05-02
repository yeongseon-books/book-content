# Series Index

이 문서는 전체 콘텐츠 시리즈의 목록과 발행 상태를 관리한다. 단일 출처는 [`series.yaml`](./series.yaml) 이며, 본 문서는 `scripts/build_series_index.py` 가 자동 생성한다. 직접 편집 금지.

## Status Legend

| Status | Meaning |
| --- | --- |
| Planned | 기획 중 |
| Draft | 초안 작성 중 |
| Content Ready | 본문 작성 완료, 코드 검증 전 |
| Code Checked | 예제 코드 검증 완료 |
| Publish Ready | 발행 준비 완료 |
| Ready (legacy) | 발행 준비 완료 (legacy) |
| Published | 발행 완료 |
| Needs Update | 업데이트 필요 |

---

## Azure

### Azure App Service 101 (`azure-app-service-101`)

Azure App Service 입문 7부작 — 호스팅, 설정, 로그, 스케일링.

- 상태: **Draft**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-app-service-101/`](./content/azure-app-service-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure App Service란? - 플랫폼 아키텍처 이해하기 | [ko](./content/azure-app-service-101/ko/01-what-is-app-service.md) | [en](./content/azure-app-service-101/en/01-what-is-app-service.md) | — | Publish Ready |
| 2 | Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까 | [ko](./content/azure-app-service-101/ko/02-request-lifecycle.md) | [en](./content/azure-app-service-101/en/02-request-lifecycle.md) | — | Publish Ready |
| 3 | Hosting Models: 어떤 플랜을 선택해야 할까? | [ko](./content/azure-app-service-101/ko/03-hosting-models.md) | [en](./content/azure-app-service-101/en/03-hosting-models.md) | — | Publish Ready |
| 4 | 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask) | [ko](./content/azure-app-service-101/ko/04-first-deploy.md) | [en](./content/azure-app-service-101/en/04-first-deploy.md) | — | Publish Ready |
| 5 | Configuration 마스터하기: App Settings & 환경변수 | [ko](./content/azure-app-service-101/ko/05-configuration.md) | [en](./content/azure-app-service-101/en/05-configuration.md) | — | Publish Ready |
| 6 | 로그와 모니터링 기초: “앱이 느려요”에 답할 수 있는 상태 만들기 | [ko](./content/azure-app-service-101/ko/06-logging-monitoring.md) | [en](./content/azure-app-service-101/en/06-logging-monitoring.md) | — | Publish Ready |
| 7 | Scaling 101: 언제 Scale Up vs Scale Out? | [ko](./content/azure-app-service-101/ko/07-scaling-101.md) | [en](./content/azure-app-service-101/en/07-scaling-101.md) | — | Publish Ready |

### Azure App Service Deep Dive (`azure-app-service-deep-dive`)

App Service 내부 — Front-End, Worker, Sandbox, Kudu, Scaling.

- 상태: **Draft**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-app-service-deep-dive/`](./content/azure-app-service-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | App Service 플랫폼 아키텍처 — Front-End·Worker·File Server | [ko](./content/azure-app-service-deep-dive/ko/01-platform-architecture.md) | [en](./content/azure-app-service-deep-dive/en/01-platform-architecture.md) | — | Publish Ready |
| 2 | Front-End과 ARR — 요청은 어떻게 워커에 도달하는가 | [ko](./content/azure-app-service-deep-dive/ko/02-front-end-and-arr.md) | [en](./content/azure-app-service-deep-dive/en/02-front-end-and-arr.md) | — | Publish Ready |
| 3 | Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가 | [ko](./content/azure-app-service-deep-dive/ko/03-worker-and-sandbox.md) | [en](./content/azure-app-service-deep-dive/en/03-worker-and-sandbox.md) | — | Publish Ready |
| 4 | 배포와 Kudu — 빌드·동기화·릴리스의 안쪽 | [ko](./content/azure-app-service-deep-dive/ko/04-deployment-and-kudu.md) | [en](./content/azure-app-service-deep-dive/en/04-deployment-and-kudu.md) | — | Publish Ready |
| 5 | 스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로 | [ko](./content/azure-app-service-deep-dive/ko/05-scaling-internals.md) | [en](./content/azure-app-service-deep-dive/en/05-scaling-internals.md) | — | Publish Ready |
| 6 | 콜드 스타트와 Warmup — 첫 요청이 비싼 이유 | [ko](./content/azure-app-service-deep-dive/ko/06-cold-start-and-warmup.md) | [en](./content/azure-app-service-deep-dive/en/06-cold-start-and-warmup.md) | — | Publish Ready |

### Azure Functions 101 (`azure-functions-101`)

Azure Functions 입문 7부작 — 트리거/바인딩부터 운영까지.

- 상태: **Draft**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-functions-101/`](./content/azure-functions-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Functions란? — 이벤트가 함수를 호출하는 세상 | [ko](./content/azure-functions-101/ko/01-what-is-azure-functions.md) | [en](./content/azure-functions-101/en/01-what-is-azure-functions.md) | — | Publish Ready |
| 2 | 트리거와 바인딩 — 함수 입출력의 모든 것 | [ko](./content/azure-functions-101/ko/02-triggers-and-bindings.md) | [en](./content/azure-functions-101/en/02-triggers-and-bindings.md) | — | Publish Ready |
| 3 | Host와 Worker — 함수는 누가 실행하는가 | [ko](./content/azure-functions-101/ko/03-host-and-worker.md) | [en](./content/azure-functions-101/en/03-host-and-worker.md) | — | Publish Ready |
| 4 | 함수 하나 배포하기 — 로컬에서 Azure까지 | [ko](./content/azure-functions-101/ko/04-first-deploy.md) | [en](./content/azure-functions-101/en/04-first-deploy.md) | — | Publish Ready |
| 5 | 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated | [ko](./content/azure-functions-101/ko/05-choosing-a-plan.md) | [en](./content/azure-functions-101/en/05-choosing-a-plan.md) | — | Publish Ready |
| 6 | 스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간 | [ko](./content/azure-functions-101/ko/06-scaling-and-cold-start.md) | [en](./content/azure-functions-101/en/06-scaling-and-cold-start.md) | — | Publish Ready |
| 7 | 모니터링과 운영 기초 | [ko](./content/azure-functions-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-functions-101/en/07-monitoring-and-ops.md) | — | Publish Ready |

### Azure Functions Deep Dive (`azure-functions-deep-dive`)

Azure Functions Host 소스 분석 시리즈 (commit-pinned).

- 상태: **Draft**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-functions-deep-dive/`](./content/azure-functions-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기 | [ko](./content/azure-functions-deep-dive/ko/01-host-bootstrap.md) | [en](./content/azure-functions-deep-dive/en/01-host-bootstrap.md) | — | Publish Ready |
| 2 | Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법 | [ko](./content/azure-functions-deep-dive/ko/02-worker-process.md) | [en](./content/azure-functions-deep-dive/en/02-worker-process.md) | — | Publish Ready |
| 3 | gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가 | [ko](./content/azure-functions-deep-dive/ko/03-grpc-event-stream.md) | [en](./content/azure-functions-deep-dive/en/03-grpc-event-stream.md) | — | Publish Ready |
| 4 | Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 | [ko](./content/azure-functions-deep-dive/ko/04-dispatcher-and-invocation.md) | [en](./content/azure-functions-deep-dive/en/04-dispatcher-and-invocation.md) | — | Publish Ready |
| 5 | 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이 | [ko](./content/azure-functions-deep-dive/ko/05-scaling-internals.md) | [en](./content/azure-functions-deep-dive/en/05-scaling-internals.md) | — | Publish Ready |
| 6 | 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 | [ko](./content/azure-functions-deep-dive/ko/06-cold-start-placeholder.md) | [en](./content/azure-functions-deep-dive/en/06-cold-start-placeholder.md) | — | Publish Ready |

### Azure Kubernetes Service 101 (`azure-aks-101`)

AKS 입문 시리즈.

- 상태: **Draft**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aks-101/`](./content/azure-aks-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes | [ko](./content/azure-aks-101/ko/01-what-is-aks.md) | [en](./content/azure-aks-101/en/01-what-is-aks.md) | — | Publish Ready |
| 2 | 클러스터 아키텍처 — Control Plane과 Node Pool | [ko](./content/azure-aks-101/ko/02-cluster-architecture.md) | [en](./content/azure-aks-101/en/02-cluster-architecture.md) | — | Publish Ready |
| 3 | 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI | [ko](./content/azure-aks-101/ko/03-first-cluster-and-deploy.md) | [en](./content/azure-aks-101/en/03-first-cluster-and-deploy.md) | — | Publish Ready |
| 4 | Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식 | [ko](./content/azure-aks-101/ko/04-pod-deployment-service.md) | [en](./content/azure-aks-101/en/04-pod-deployment-service.md) | — | Publish Ready |
| 5 | 네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길 | [ko](./content/azure-aks-101/ko/05-networking-and-ingress.md) | [en](./content/azure-aks-101/en/05-networking-and-ingress.md) | — | Publish Ready |
| 6 | 스케일링 — HPA, Cluster Autoscaler, KEDA | [ko](./content/azure-aks-101/ko/06-scaling-hpa-ca-keda.md) | [en](./content/azure-aks-101/en/06-scaling-hpa-ca-keda.md) | — | Publish Ready |
| 7 | 모니터링과 운영 — Container Insights, 로그, 알람 | [ko](./content/azure-aks-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-aks-101/en/07-monitoring-and-ops.md) | — | Publish Ready |

### Azure Kubernetes Service Deep Dive (`azure-aks-deep-dive`)

AKS control plane / data plane 내부 동작.

- 상태: **Draft**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aks-deep-dive/`](./content/azure-aks-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Control Plane 해부 — AKS가 사용자에게서 가린 것 | [ko](./content/azure-aks-deep-dive/ko/01-control-plane-anatomy.md) | [en](./content/azure-aks-deep-dive/en/01-control-plane-anatomy.md) | — | Publish Ready |
| 2 | kubelet과 containerd — 노드 위에서 컨테이너가 뜨기까지 | [ko](./content/azure-aks-deep-dive/ko/02-kubelet-and-containerd.md) | [en](./content/azure-aks-deep-dive/en/02-kubelet-and-containerd.md) | — | Publish Ready |
| 3 | CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가 | [ko](./content/azure-aks-deep-dive/ko/03-cni-and-azure-cni-overlay.md) | [en](./content/azure-aks-deep-dive/en/03-cni-and-azure-cni-overlay.md) | — | Publish Ready |
| 4 | Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가 | [ko](./content/azure-aks-deep-dive/ko/04-scheduler-and-pod-placement.md) | [en](./content/azure-aks-deep-dive/en/04-scheduler-and-pod-placement.md) | — | Publish Ready |
| 5 | HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프 | [ko](./content/azure-aks-deep-dive/ko/05-hpa-and-cluster-autoscaler-internals.md) | [en](./content/azure-aks-deep-dive/en/05-hpa-and-cluster-autoscaler-internals.md) | — | Publish Ready |
| 6 | KEDA 내부 — ScaledObject가 HPA를 만드는 방식 | [ko](./content/azure-aks-deep-dive/ko/06-keda-internals.md) | [en](./content/azure-aks-deep-dive/en/06-keda-internals.md) | — | Publish Ready |

### Azure Container Apps 101 (`azure-aca-101`)

Container Apps 입문 시리즈.

- 상태: **Draft**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aca-101/`](./content/azure-aca-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기 | [ko](./content/azure-aca-101/ko/01-what-is-aca.md) | [en](./content/azure-aca-101/en/01-what-is-aca.md) | — | Publish Ready |
| 2 | Environment·Container App·Revision — 세 단어로 보는 ACA | [ko](./content/azure-aca-101/ko/02-environment-app-revision.md) | [en](./content/azure-aca-101/en/02-environment-app-revision.md) | — | Publish Ready |
| 3 | 첫 앱 배포하기 — Python/FastAPI | [ko](./content/azure-aca-101/ko/03-first-deploy.md) | [en](./content/azure-aca-101/en/03-first-deploy.md) | — | Publish Ready |
| 4 | Ingress와 트래픽 분할 — Revision 기반 배포 전략 | [ko](./content/azure-aca-101/ko/04-ingress-and-traffic-split.md) | [en](./content/azure-aca-101/en/04-ingress-and-traffic-split.md) | — | Publish Ready |
| 5 | 스케일링 — KEDA scaler와 0-to-N | [ko](./content/azure-aca-101/ko/05-scaling-with-keda.md) | [en](./content/azure-aca-101/en/05-scaling-with-keda.md) | — | Publish Ready |
| 6 | Dapr 통합 — 사이드카로 얻는 것 | [ko](./content/azure-aca-101/ko/06-dapr-integration.md) | [en](./content/azure-aca-101/en/06-dapr-integration.md) | — | Publish Ready |
| 7 | 모니터링과 운영 — Log Analytics와 Application Insights | [ko](./content/azure-aca-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-aca-101/en/07-monitoring-and-ops.md) | — | Publish Ready |

### Azure Container Apps Deep Dive (`azure-aca-deep-dive`)

ACA 위에 얹힌 KEDA·Dapr·Envoy 내부 동작.

- 상태: **Draft**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aca-deep-dive/`](./content/azure-aca-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것 | [ko](./content/azure-aca-deep-dive/ko/01-aca-architecture.md) | [en](./content/azure-aca-deep-dive/en/01-aca-architecture.md) | — | Publish Ready |
| 2 | Environment 내부 — 네트워크·관측·Dapr 스코프의 경계 | [ko](./content/azure-aca-deep-dive/ko/02-environment-internals.md) | [en](./content/azure-aca-deep-dive/en/02-environment-internals.md) | — | Publish Ready |
| 3 | Revision과 트래픽 분할 — Envoy 가중치는 어디에서 오는가 | [ko](./content/azure-aca-deep-dive/ko/03-revision-and-traffic-split.md) | [en](./content/azure-aca-deep-dive/en/03-revision-and-traffic-split.md) | — | Publish Ready |
| 4 | ACA 안의 KEDA — Scale Rule이 만드는 것 | [ko](./content/azure-aca-deep-dive/ko/04-keda-in-aca.md) | [en](./content/azure-aca-deep-dive/en/04-keda-in-aca.md) | — | Publish Ready |
| 5 | Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스 | [ko](./content/azure-aca-deep-dive/ko/05-dapr-sidecar-internals.md) | [en](./content/azure-aca-deep-dive/en/05-dapr-sidecar-internals.md) | — | Publish Ready |
| 6 | Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지 | [ko](./content/azure-aca-deep-dive/ko/06-envoy-ingress-path.md) | [en](./content/azure-aca-deep-dive/en/06-envoy-ingress-path.md) | — | Publish Ready |

---

## AI

### AI 웹 개발 입문 / AI Web Development 101 (`ai-web-dev-101`)

AI API 부터 배포까지, 초급 개발자를 위한 7부작.

- 상태: **Needs Update**
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

PyTorch 2.x 로 토크나이저부터 챗봇까지, ~720 LOC 의 작은 GPT 9부작.

- 상태: **Draft**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-from-scratch-101/`](./content/llm-from-scratch-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 글자를 숫자로 바꾸기 | [ko](./content/llm-from-scratch-101/ko/01-tokenizer.md) | [en](./content/llm-from-scratch-101/en/01-tokenizer.md) | — | Code Checked |
| 2 | 정수에서 벡터로, 그리고 위치 | [ko](./content/llm-from-scratch-101/ko/02-embedding.md) | [en](./content/llm-from-scratch-101/en/02-embedding.md) | — | Code Checked |
| 3 | 어떤 토큰을 얼마나 볼지 스스로 정하기 | [ko](./content/llm-from-scratch-101/ko/03-attention.md) | [en](./content/llm-from-scratch-101/en/03-attention.md) | — | Code Checked |
| 4 | 블록 하나, 깊이의 단위 | [ko](./content/llm-from-scratch-101/ko/04-transformer-block.md) | [en](./content/llm-from-scratch-101/en/04-transformer-block.md) | — | Code Checked |
| 5 | 조립: GPT 모델 클래스 완성 | [ko](./content/llm-from-scratch-101/ko/05-gpt-model.md) | [en](./content/llm-from-scratch-101/en/05-gpt-model.md) | — | Code Checked |
| 6 | 기울기로 배우기 | [ko](./content/llm-from-scratch-101/ko/06-training-loop.md) | [en](./content/llm-from-scratch-101/en/06-training-loop.md) | — | Code Checked |
| 7 | 샘플링 — 학습된 모델에서 글 뽑아내기 | [ko](./content/llm-from-scratch-101/ko/07-inference.md) | [en](./content/llm-from-scratch-101/en/07-inference.md) | — | Code Checked |
| 8 | 베이스 모델을 우리 작업에 맞추기 | [ko](./content/llm-from-scratch-101/ko/08-finetuning.md) | [en](./content/llm-from-scratch-101/en/08-finetuning.md) | — | Code Checked |
| 9 | 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 | [ko](./content/llm-from-scratch-101/ko/09-chatbot-wrapper.md) | [en](./content/llm-from-scratch-101/en/09-chatbot-wrapper.md) | — | Code Checked |

### RAG Deep Dive (`rag-deep-dive`)

LangChain · FAISS · RAGAS 소스로 따라가는 RAG 파이프라인 심층 분석 6부작.

- 상태: **Draft**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/rag-deep-dive/`](./content/rag-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 문서 로딩과 청크 전략 — LangChain TextSplitter 내부 | [ko](./content/rag-deep-dive/ko/01-document-loading-and-chunking.md) | [en](./content/rag-deep-dive/en/01-document-loading-and-chunking.md) | — | Publish Ready |
| 2 | 임베딩과 벡터 인덱스 — FAISS IndexFlatL2 동작 원리 | [ko](./content/rag-deep-dive/ko/02-embeddings-and-vector-index.md) | [en](./content/rag-deep-dive/en/02-embeddings-and-vector-index.md) | — | Publish Ready |
| 3 | Retriever 설계 — VectorStoreRetriever와 MMR | [ko](./content/rag-deep-dive/ko/03-retriever-design.md) | [en](./content/rag-deep-dive/en/03-retriever-design.md) | — | Publish Ready |
| 4 | 프롬프트 구성과 컨텍스트 주입 — PromptTemplate 내부 | [ko](./content/rag-deep-dive/ko/04-prompt-construction-and-context-injection.md) | [en](./content/rag-deep-dive/en/04-prompt-construction-and-context-injection.md) | — | Publish Ready |
| 5 | RAG Chain 조립 — RetrievalQA vs LCEL | [ko](./content/rag-deep-dive/ko/05-rag-chain-assembly.md) | [en](./content/rag-deep-dive/en/05-rag-chain-assembly.md) | — | Publish Ready |
| 6 | 평가와 품질 게이트 — RAGAS 메트릭과 Faithfulness | [ko](./content/rag-deep-dive/ko/06-evaluation-and-quality-gates.md) | [en](./content/rag-deep-dive/en/06-evaluation-and-quality-gates.md) | — | Publish Ready |

### LLM 앱 기초 / LLM App Foundations 101 (`llm-app-foundations-101`)

LLM API 기초, 토큰, 프롬프트 엔지니어링 — 6부작.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-app-foundations-101/`](./content/llm-app-foundations-101/)

_articles not yet enumerated._

### LLM API 프로덕션 101 / LLM API Production 101 (`llm-api-production-101`)

Structured Output, Tool Calling, Streaming, Caching, Retry, Rate Limit — 6부작.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-api-production-101/`](./content/llm-api-production-101/)

_articles not yet enumerated._

### 벡터 검색 101 / Vector Search 101 (`vector-search-101`)

임베딩, FAISS, 유사도, 청크 전략 — 6부작.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/vector-search-101/`](./content/vector-search-101/)

_articles not yet enumerated._

### LangChain 101 (`langchain-101`)

LCEL, Runnable, Retriever, Tool Calling 기본, Streaming — LangChain API 사용법 6부작.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/langchain-101/`](./content/langchain-101/)

_articles not yet enumerated._

### AI 앱 패턴 101 / AI App Patterns 101 (`ai-app-patterns-101`)

챗봇, RAG Q&A, 문서비서, Agent, Workflow, Human-in-the-loop — LLM 앱 설계 패턴 6부작.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ai-app-patterns-101/`](./content/ai-app-patterns-101/)

_articles not yet enumerated._

### 한국어 AI 스택 101 / Korean AI Stack 101 (`korean-ai-stack-101`)

한국어 임베딩, OCR, 국내 LLM API — 6부작.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/korean-ai-stack-101/`](./content/korean-ai-stack-101/)

_articles not yet enumerated._

### 문서 수집과 인덱싱 101 / Document Ingestion 101 (`document-ingestion-101`)

PDF 파싱, 메타데이터, 증분 인덱싱 — 6부작.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/document-ingestion-101/`](./content/document-ingestion-101/)

_articles not yet enumerated._

### LLM 앱 운영 101 / LLM Apps Ops 101 (`llm-apps-ops-101`)

관측, 평가, 비용, 보안, 배포 — 6부작.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-apps-ops-101/`](./content/llm-apps-ops-101/)

_articles not yet enumerated._

### RAG 평가와 벤치마크 101 / RAG Evaluation and Benchmarking 101 (`rag-benchmark-101`)

RAG 품질 평가 6부작 — 평가 데이터셋, 임베딩/리트리버 비교, RAGAS, 의사결정 연결.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/rag-benchmark-101/`](./content/rag-benchmark-101/)

_articles not yet enumerated._

### LangGraph 101 (`langgraph-101`)

그래프 에이전트, 체크포인트, 멀티에이전트 — 6부작.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/langgraph-101/`](./content/langgraph-101/)

_articles not yet enumerated._

### LLM 파인튜닝 101 / LLM Fine-tuning 101 (`llm-finetuning-101`)

LoRA, 데이터셋, 서빙 — 6부작 (선택).

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-finetuning-101/`](./content/llm-finetuning-101/)

_articles not yet enumerated._

---

## AX (Planned)

### AX 실전 가이드 / AI Transformation Practical Guide (`ax-practical-guide`)

AX 도입 전략, 업무 자동화 사례, 조직 변화 관리.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ax-practical-guide/`](./content/ax-practical-guide/)

_articles not yet enumerated._

---

## Writing

### 엔지니어를 위한 기술 글쓰기 / Technical Writing for Engineers (`technical-writing`)

시리즈를 설계하고, 한 편을 다듬는 법.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/technical-writing/`](./content/technical-writing/)

_articles not yet enumerated._
