# Tech Writing

> 본 저장소는 `tech-blog` 에서 `tech-writing` 으로 단계적으로 개편 중입니다. 자세한 내용은 [`MIGRATION_PLAN.md`](./MIGRATION_PLAN.md) · [`ROADMAP.md`](./ROADMAP.md) 참조.

Tistory, Medium, MkDocs, eBook 발행을 위한 기술 콘텐츠 원본 저장소. 한 번 작성한 글을 여러 채널로 변환하기 위한 멀티채널 퍼블리싱 파이프라인입니다.

## Publishing Targets

| Target | 용도 | 언어 |
| --- | --- | --- |
| Tistory | 한국어 블로그 | ko |
| Medium | 영어 블로그 | en |
| MkDocs | 웹북 / 문서 사이트 | ko + en |
| eBook source | private `mkdocs-ebook` 입력 번들 | ko + en |

## Content Areas

- Azure (App Service, Functions, AKS, Container Apps; 101 + Deep Dive)
- AI (AI Web Dev 101, LLM from Scratch 101, RAG Deep Dive)
- AX (planned)
- Developer Productivity (planned)
- Open Source (planned)
- Technical Writing (planned)

## Key Documents

- [`SERIES.md`](./SERIES.md) — 전체 시리즈 카탈로그와 상태
- [`PUBLISHING.md`](./PUBLISHING.md) — Tistory/Medium/MkDocs/eBook 변환 규칙
- [`STYLE_GUIDE.md`](./STYLE_GUIDE.md) — 문체, 구조, 이미지, 태그, 참고자료 규칙
- [`EBOOK.md`](./EBOOK.md) — eBook source bundle 정책 (private builder 연동)
- [`ROADMAP.md`](./ROADMAP.md) — 개편 로드맵과 진행 상황
- [`MIGRATION_PLAN.md`](./MIGRATION_PLAN.md) — `tech-blog` → `tech-writing` 마스터 플랜
- [`AGENTS.md`](./AGENTS.md) — 에이전트(인간/AI) 운영 규칙

## Quality Gates

```bash
python3 .sisyphus/medium/finalize-posts.py    # idempotent: tags + TOC + ko refs
.sisyphus/style/check-ko.sh                   # ko translation-smell + im-not-ai S1 check
```

medium 변형 재생성 시:

```bash
python3 .sisyphus/medium/to-medium.py <series>/en
python3 .sisyphus/medium/finalize-posts.py
```

## 시리즈

### Azure App Service 101

Azure App Service 입문자를 위한 실전 가이드 시리즈. 플랫폼 구조부터 요청 흐름, 배포, 설정, 모니터링, 스케일링까지 이어집니다.

| # | 제목 | 한국어 (Tistory) | English (Medium) |
|---|---|---|---|
| 1 | Azure App Service란? - 플랫폼 아키텍처 이해하기 | [ko](./content/azure-app-service-101/ko/01-what-is-app-service.md) | [en](./content/azure-app-service-101/en/01-what-is-app-service.md) |
| 2 | Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까 | [ko](./content/azure-app-service-101/ko/02-request-lifecycle.md) | [en](./content/azure-app-service-101/en/02-request-lifecycle.md) |
| 3 | Hosting Models: 어떤 플랜을 선택해야 할까? | [ko](./content/azure-app-service-101/ko/03-hosting-models.md) | [en](./content/azure-app-service-101/en/03-hosting-models.md) |
| 4 | 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask) | [ko](./content/azure-app-service-101/ko/04-first-deploy.md) | [en](./content/azure-app-service-101/en/04-first-deploy.md) |
| 5 | Configuration 마스터하기: App Settings & 환경변수 | [ko](./content/azure-app-service-101/ko/05-configuration.md) | [en](./content/azure-app-service-101/en/05-configuration.md) |
| 6 | 로그와 모니터링 기초 | [ko](./content/azure-app-service-101/ko/06-logging-monitoring.md) | [en](./content/azure-app-service-101/en/06-logging-monitoring.md) |
| 7 | Scaling 101: 언제 Scale Up vs Scale Out? | [ko](./content/azure-app-service-101/ko/07-scaling-101.md) | [en](./content/azure-app-service-101/en/07-scaling-101.md) |

### AI 웹 개발 입문

AI API부터 배포까지, 초급 개발자를 위한 AI 웹 개발 실전 가이드 시리즈.

| # | 제목 | 파일 | 예상 분량 |
|---|---|---|---|
| 1 | AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기 | [01-hello-ai-api.md](./content/ai-web-dev-101/ko/01-hello-ai-api.md) | 10분 |
| 2 | 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술 | [02-prompt-engineering.md](./content/ai-web-dev-101/ko/02-prompt-engineering.md) | 8분 |
| 3 | AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현 | [03-ai-chatbot.md](./content/ai-web-dev-101/ko/03-ai-chatbot.md) | 10분 |
| 4 | RAG 입문 — 내 데이터로 답하는 AI 만들기 | [04-rag-intro.md](./content/ai-web-dev-101/ko/04-rag-intro.md) | 10분 |
| 5 | AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기 | [05-ai-agent.md](./content/ai-web-dev-101/ko/05-ai-agent.md) | 10분 |
| 6 | AI 웹 앱 배포하기 — Vercel과 Azure에 올리고 운영하기 | [06-deploy.md](./content/ai-web-dev-101/ko/06-deploy.md) | 9분 |
| 7 | AI 앱의 평가와 개선 — 품질을 측정하고 더 좋게 만드는 법 | [07-eval-improve.md](./content/ai-web-dev-101/ko/07-eval-improve.md) | 10분 |

### LLM from Scratch 101

PyTorch 2.x로 토크나이저부터 챗봇까지, 한 시리즈 동안 ~720 LOC 안에서 작은 GPT를 직접 만들고 학습·생성·파인튜닝·서빙까지 끝내는 입문 시리즈. TinyShakespeare, char-level vocab, ~1.2M 파라미터.

| # | 제목 | 한국어 (Tistory) | English (Medium) |
|---|---|---|---|
| 1 | 글자를 숫자로 바꾸기 | [ko](./content/llm-from-scratch-101/ko/01-tokenizer.md) | [en](./content/llm-from-scratch-101/en/01-tokenizer.md) |
| 2 | 정수에서 벡터로, 그리고 위치 | [ko](./content/llm-from-scratch-101/ko/02-embedding.md) | [en](./content/llm-from-scratch-101/en/02-embedding.md) |
| 3 | 어떤 토큰을 얼마나 볼지 스스로 정하기 | [ko](./content/llm-from-scratch-101/ko/03-attention.md) | [en](./content/llm-from-scratch-101/en/03-attention.md) |
| 4 | 블록 하나, 깊이의 단위 | [ko](./content/llm-from-scratch-101/ko/04-transformer-block.md) | [en](./content/llm-from-scratch-101/en/04-transformer-block.md) |
| 5 | 조립: GPT 모델 클래스 완성 | [ko](./content/llm-from-scratch-101/ko/05-gpt-model.md) | [en](./content/llm-from-scratch-101/en/05-gpt-model.md) |
| 6 | 기울기로 배우기 | [ko](./content/llm-from-scratch-101/ko/06-training-loop.md) | [en](./content/llm-from-scratch-101/en/06-training-loop.md) |
| 7 | 샘플링 — 학습된 모델에서 글 뽑아내기 | [ko](./content/llm-from-scratch-101/ko/07-inference.md) | [en](./content/llm-from-scratch-101/en/07-inference.md) |
| 8 | 베이스 모델을 우리 작업에 맞추기 | [ko](./content/llm-from-scratch-101/ko/08-finetuning.md) | [en](./content/llm-from-scratch-101/en/08-finetuning.md) |
| 9 | 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 | [ko](./content/llm-from-scratch-101/ko/09-chatbot-wrapper.md) | [en](./content/llm-from-scratch-101/en/09-chatbot-wrapper.md) |

### RAG Deep Dive

LangChain · FAISS · RAGAS 소스로 따라가는 RAG 파이프라인 심층 분석 시리즈. 모든 코드 인용은 source-pinned.

| # | 제목 | 한국어 (Tistory) | English (Medium) |
|---|---|---|---|
| 1 | 문서 로딩과 청크 전략 — LangChain TextSplitter 내부 | [ko](./content/rag-deep-dive/ko/01-document-loading-and-chunking.md) | [en](./content/rag-deep-dive/en/01-document-loading-and-chunking.md) |
| 2 | 임베딩과 벡터 인덱스 — FAISS IndexFlatL2 동작 원리 | [ko](./content/rag-deep-dive/ko/02-embeddings-and-vector-index.md) | [en](./content/rag-deep-dive/en/02-embeddings-and-vector-index.md) |
| 3 | Retriever 설계 — VectorStoreRetriever와 MMR | [ko](./content/rag-deep-dive/ko/03-retriever-design.md) | [en](./content/rag-deep-dive/en/03-retriever-design.md) |
| 4 | 프롬프트 구성과 컨텍스트 주입 — PromptTemplate 내부 | [ko](./content/rag-deep-dive/ko/04-prompt-construction-and-context-injection.md) | [en](./content/rag-deep-dive/en/04-prompt-construction-and-context-injection.md) |
| 5 | RAG Chain 조립 — RetrievalQA vs LCEL | [ko](./content/rag-deep-dive/ko/05-rag-chain-assembly.md) | [en](./content/rag-deep-dive/en/05-rag-chain-assembly.md) |
| 6 | 평가와 품질 게이트 — RAGAS 메트릭과 Faithfulness | [ko](./content/rag-deep-dive/ko/06-evaluation-and-quality-gates.md) | [en](./content/rag-deep-dive/en/06-evaluation-and-quality-gates.md) |

### LLM API Production 101

Groq Python SDK를 기준으로 Structured Output, Tool Calling, Streaming, Caching, Retry, Rate Limit까지 운영 관점에서 정리한 6부작 시리즈.

| # | 제목 | 한국어 (Tistory) | English (Medium) |
|---|---|---|---|
| 1 | 구조화 출력 — JSON 모드와 응답 스키마 | [ko](./content/llm-api-production-101/ko/01-structured-output.md) | [en](./content/llm-api-production-101/en/01-structured-output.md) |
| 2 | 툴 호출 — 함수를 모델에 연결하기 | [ko](./content/llm-api-production-101/ko/02-tool-calling.md) | [en](./content/llm-api-production-101/en/02-tool-calling.md) |
| 3 | 스트리밍 심화 — 청크 처리와 오류 복구 | [ko](./content/llm-api-production-101/ko/03-streaming-in-depth.md) | [en](./content/llm-api-production-101/en/03-streaming-in-depth.md) |
| 4 | 캐싱 전략 — 비용과 지연 시간 줄이기 | [ko](./content/llm-api-production-101/ko/04-caching-strategies.md) | [en](./content/llm-api-production-101/en/04-caching-strategies.md) |
| 5 | 재시도와 오류 처리 — 안정적인 API 호출 만들기 | [ko](./content/llm-api-production-101/ko/05-retry-and-error-handling.md) | [en](./content/llm-api-production-101/en/05-retry-and-error-handling.md) |
| 6 | 속도 제한 관리 — Rate Limit 대응 패턴 | [ko](./content/llm-api-production-101/ko/06-rate-limit-management.md) | [en](./content/llm-api-production-101/en/06-rate-limit-management.md) |

### Azure Functions 101

Azure Functions 입문자를 위한 실전 가이드 시리즈. 트리거·바인딩부터 플랜 선택, 콜드 스타트, 모니터링까지.

| # | 제목 | 한국어 (Tistory) | English (Medium) |
|---|---|---|---|
| 1 | Azure Functions란? — 이벤트 기반 서버리스 컴퓨팅 | [ko](./content/azure-functions-101/ko/01-what-is-azure-functions.md) | [en](./content/azure-functions-101/en/01-what-is-azure-functions.md) |
| 2 | Triggers & Bindings — 함수가 일을 시작하고 끝내는 방식 | [ko](./content/azure-functions-101/ko/02-triggers-and-bindings.md) | [en](./content/azure-functions-101/en/02-triggers-and-bindings.md) |
| 3 | Host와 Worker — 한 함수 앱 안에 두 프로세스가 사는 이유 | [ko](./content/azure-functions-101/ko/03-host-and-worker.md) | [en](./content/azure-functions-101/en/03-host-and-worker.md) |
| 4 | 첫 번째 배포 — 로컬에서 Azure까지 | [ko](./content/azure-functions-101/ko/04-first-deploy.md) | [en](./content/azure-functions-101/en/04-first-deploy.md) |
| 5 | 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated | [ko](./content/azure-functions-101/ko/05-choosing-a-plan.md) | [en](./content/azure-functions-101/en/05-choosing-a-plan.md) |
| 6 | 스케일링과 콜드 스타트 — 사용자가 알아야 할 만큼만 | [ko](./content/azure-functions-101/ko/06-scaling-and-cold-start.md) | [en](./content/azure-functions-101/en/06-scaling-and-cold-start.md) |
| 7 | 모니터링과 운영 — Application Insights·KQL·알람 | [ko](./content/azure-functions-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-functions-101/en/07-monitoring-and-ops.md) |

### Azure Functions Deep Dive

Azure Functions Host의 내부 동작을 코드 레벨로 따라가는 시리즈. 모든 코드 인용은 [`Azure/azure-functions-host` @ `5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7) 기준입니다.

| # | 제목 | 한국어 (Tistory) | English (Medium) |
|---|---|---|---|
| 1 | Host Bootstrap — `dotnet Microsoft.Azure.WebJobs.Script.WebHost.dll`이 일으키는 일 | [ko](./content/azure-functions-deep-dive/ko/01-host-bootstrap.md) | [en](./content/azure-functions-deep-dive/en/01-host-bootstrap.md) |
| 2 | Worker Process — 호스트는 왜 사용자 코드를 직접 실행하지 않는가 | [ko](./content/azure-functions-deep-dive/ko/02-worker-process.md) | [en](./content/azure-functions-deep-dive/en/02-worker-process.md) |
| 3 | gRPC Event Stream — 호스트와 워커의 단 하나의 양방향 채널 | [ko](./content/azure-functions-deep-dive/ko/03-grpc-event-stream.md) | [en](./content/azure-functions-deep-dive/en/03-grpc-event-stream.md) |
| 4 | Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 | [ko](./content/azure-functions-deep-dive/ko/04-dispatcher-and-invocation.md) | [en](./content/azure-functions-deep-dive/en/04-dispatcher-and-invocation.md) |
| 5 | 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 플랜별 차이 | [ko](./content/azure-functions-deep-dive/ko/05-scaling-internals.md) | [en](./content/azure-functions-deep-dive/en/05-scaling-internals.md) |
| 6 | 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 | [ko](./content/azure-functions-deep-dive/ko/06-cold-start-placeholder.md) | [en](./content/azure-functions-deep-dive/en/06-cold-start-placeholder.md) |

### Azure App Service Deep Dive

App Service 플랫폼이 Front-End·Worker·File Server 위에서 사용자 요청을 어떻게 처리하는지를 코드와 공식 문서로 따라가는 시리즈. Azure Functions가 이 인프라 위에서 돈다는 사실을 ep01에서 명시적으로 연결합니다.

| # | 제목 | 한국어 (Tistory) | English (Medium) |
|---|---|---|---|
| 1 | App Service 플랫폼 아키텍처 — Front-End·Worker·File Server | [ko](./content/azure-app-service-deep-dive/ko/01-platform-architecture.md) | [en](./content/azure-app-service-deep-dive/en/01-platform-architecture.md) |
| 2 | Front-End과 ARR — 요청은 어떻게 워커에 도달하는가 | [ko](./content/azure-app-service-deep-dive/ko/02-front-end-and-arr.md) | [en](./content/azure-app-service-deep-dive/en/02-front-end-and-arr.md) |
| 3 | Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가 | [ko](./content/azure-app-service-deep-dive/ko/03-worker-and-sandbox.md) | [en](./content/azure-app-service-deep-dive/en/03-worker-and-sandbox.md) |
| 4 | 배포와 Kudu — 빌드·동기화·릴리스의 안쪽 | [ko](./content/azure-app-service-deep-dive/ko/04-deployment-and-kudu.md) | [en](./content/azure-app-service-deep-dive/en/04-deployment-and-kudu.md) |
| 5 | 스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로 | [ko](./content/azure-app-service-deep-dive/ko/05-scaling-internals.md) | [en](./content/azure-app-service-deep-dive/en/05-scaling-internals.md) |
| 6 | 콜드 스타트와 Warmup — 첫 요청이 비싼 이유 | [ko](./content/azure-app-service-deep-dive/ko/06-cold-start-and-warmup.md) | [en](./content/azure-app-service-deep-dive/en/06-cold-start-and-warmup.md) |

### Azure Kubernetes Service 101

AKS 입문자를 위한 실전 가이드 시리즈. 관리형 Kubernetes가 사용자에게 무엇을 주는지부터 클러스터 아키텍처, 첫 배포, 워크로드 모델, 네트워킹, 스케일링, 운영까지 이어집니다.

| # | 제목 | 한국어 (Tistory) | English (Medium) |
|---|---|---|---|
| 1 | Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes | [ko](./content/azure-aks-101/ko/01-what-is-aks.md) | [en](./content/azure-aks-101/en/01-what-is-aks.md) |
| 2 | 클러스터 아키텍처 — Control Plane과 Node Pool | [ko](./content/azure-aks-101/ko/02-cluster-architecture.md) | [en](./content/azure-aks-101/en/02-cluster-architecture.md) |
| 3 | 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI | [ko](./content/azure-aks-101/ko/03-first-cluster-and-deploy.md) | [en](./content/azure-aks-101/en/03-first-cluster-and-deploy.md) |
| 4 | Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식 | [ko](./content/azure-aks-101/ko/04-pod-deployment-service.md) | [en](./content/azure-aks-101/en/04-pod-deployment-service.md) |
| 5 | 네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길 | [ko](./content/azure-aks-101/ko/05-networking-and-ingress.md) | [en](./content/azure-aks-101/en/05-networking-and-ingress.md) |
| 6 | 스케일링 — HPA, Cluster Autoscaler, KEDA | [ko](./content/azure-aks-101/ko/06-scaling-hpa-ca-keda.md) | [en](./content/azure-aks-101/en/06-scaling-hpa-ca-keda.md) |
| 7 | 모니터링과 운영 — Container Insights, 로그, 알람 | [ko](./content/azure-aks-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-aks-101/en/07-monitoring-and-ops.md) |

### Azure Kubernetes Service Deep Dive

AKS가 사용자에게서 가린 control plane과, 사용자가 손대는 data plane(노드 위 kubelet·containerd·CNI) 양쪽을 commit-pinned 소스로 따라가는 시리즈.

| # | 제목 | 한국어 (Tistory) | English (Medium) |
|---|---|---|---|
| 1 | Control Plane 해부 — AKS가 사용자에게서 가린 것 | [ko](./content/azure-aks-deep-dive/ko/01-control-plane-anatomy.md) | [en](./content/azure-aks-deep-dive/en/01-control-plane-anatomy.md) |
| 2 | kubelet과 containerd — 노드 위에서 컨테이너가 뜨기까지 | [ko](./content/azure-aks-deep-dive/ko/02-kubelet-and-containerd.md) | [en](./content/azure-aks-deep-dive/en/02-kubelet-and-containerd.md) |
| 3 | CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가 | [ko](./content/azure-aks-deep-dive/ko/03-cni-and-azure-cni-overlay.md) | [en](./content/azure-aks-deep-dive/en/03-cni-and-azure-cni-overlay.md) |
| 4 | Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가 | [ko](./content/azure-aks-deep-dive/ko/04-scheduler-and-pod-placement.md) | [en](./content/azure-aks-deep-dive/en/04-scheduler-and-pod-placement.md) |
| 5 | HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프 | [ko](./content/azure-aks-deep-dive/ko/05-hpa-and-cluster-autoscaler-internals.md) | [en](./content/azure-aks-deep-dive/en/05-hpa-and-cluster-autoscaler-internals.md) |
| 6 | KEDA 내부 — ScaledObject가 HPA를 만드는 방식 | [ko](./content/azure-aks-deep-dive/ko/06-keda-internals.md) | [en](./content/azure-aks-deep-dive/en/06-keda-internals.md) |

### Azure Container Apps 101

ACA 입문자를 위한 실전 가이드 시리즈. Kubernetes를 직접 운영하지 않고 컨테이너를 띄우고 싶을 때 필요한 모든 개념을 다룹니다.

| # | 제목 | 한국어 (Tistory) | English (Medium) |
|---|---|---|---|
| 1 | Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기 | [ko](./content/azure-aca-101/ko/01-what-is-aca.md) | [en](./content/azure-aca-101/en/01-what-is-aca.md) |
| 2 | Environment·Container App·Revision — 세 단어로 보는 ACA | [ko](./content/azure-aca-101/ko/02-environment-app-revision.md) | [en](./content/azure-aca-101/en/02-environment-app-revision.md) |
| 3 | 첫 앱 배포하기 — Python/FastAPI | [ko](./content/azure-aca-101/ko/03-first-deploy.md) | [en](./content/azure-aca-101/en/03-first-deploy.md) |
| 4 | Ingress와 트래픽 분할 — Revision 기반 배포 전략 | [ko](./content/azure-aca-101/ko/04-ingress-and-traffic-split.md) | [en](./content/azure-aca-101/en/04-ingress-and-traffic-split.md) |
| 5 | 스케일링 — KEDA scaler와 0-to-N | [ko](./content/azure-aca-101/ko/05-scaling-with-keda.md) | [en](./content/azure-aca-101/en/05-scaling-with-keda.md) |
| 6 | Dapr 통합 — 사이드카로 얻는 것 | [ko](./content/azure-aca-101/ko/06-dapr-integration.md) | [en](./content/azure-aca-101/en/06-dapr-integration.md) |
| 7 | 모니터링과 운영 — Log Analytics와 Application Insights | [ko](./content/azure-aca-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-aca-101/en/07-monitoring-and-ops.md) |

### Azure Container Apps Deep Dive

Microsoft가 ACA라는 추상 위에 KEDA·Dapr·Envoy를 어떻게 얹었는지를 commit-pinned 오픈소스 코드와 공식 문서로 따라가는 시리즈.

| # | 제목 | 한국어 (Tistory) | English (Medium) |
|---|---|---|---|
| 1 | ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것 | [ko](./content/azure-aca-deep-dive/ko/01-aca-architecture.md) | [en](./content/azure-aca-deep-dive/en/01-aca-architecture.md) |
| 2 | Environment 내부 — 네트워크·관측·Dapr 스코프의 경계 | [ko](./content/azure-aca-deep-dive/ko/02-environment-internals.md) | [en](./content/azure-aca-deep-dive/en/02-environment-internals.md) |
| 3 | Revision과 트래픽 분할 — Envoy 가중치는 어디에서 오는가 | [ko](./content/azure-aca-deep-dive/ko/03-revision-and-traffic-split.md) | [en](./content/azure-aca-deep-dive/en/03-revision-and-traffic-split.md) |
| 4 | ACA 안의 KEDA — Scale Rule이 만드는 것 | [ko](./content/azure-aca-deep-dive/ko/04-keda-in-aca.md) | [en](./content/azure-aca-deep-dive/en/04-keda-in-aca.md) |
| 5 | Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스 | [ko](./content/azure-aca-deep-dive/ko/05-dapr-sidecar-internals.md) | [en](./content/azure-aca-deep-dive/en/05-dapr-sidecar-internals.md) |
| 6 | Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지 | [ko](./content/azure-aca-deep-dive/ko/06-envoy-ingress-path.md) | [en](./content/azure-aca-deep-dive/en/06-envoy-ingress-path.md) |

## 폴더 구조

Phase 6 시리즈 이동이 끝나 모든 시리즈가 `content/<series>/` 아래에 있습니다.

```text
tech-writing/
├── README.md
├── MIGRATION_PLAN.md, SERIES.md, PUBLISHING.md, STYLE_GUIDE.md, EBOOK.md, ROADMAP.md, AGENTS.md
├── mkdocs.yml, requirements.txt, requirements-dev.txt
├── series.yaml                          # 루트 시리즈 카탈로그 (단일 출처, path: 필드로 위치 해석)
├── content/
│   └── <series>/
│       ├── series.yaml                  # 시리즈별 카탈로그 (article-level status)
│       ├── ko/                          # 한국어 원본
│       ├── en/                          # 영어 번역 (해당 시리즈가 en 을 가질 때)
│       └── medium/                      # Medium import-ready 변형 (to-medium.py 가 생성)
├── azure-functions-host/                # Azure 업스트림 vendored 소스 (시리즈 아님, .gitignore 처리)
├── docs/, exports/, templates/, scripts/  # scaffold (Phase 7+ 에서 채움)
├── assets/<series>/<NN>/...             # 이미지는 위치 보존; 본문은 ../../../assets/ 로 참조
└── .sisyphus/medium/                    # finalize-posts.py / to-medium.py / _catalog.py
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
  - Azure App Service 101: `Azure`, `App Service`, `Cloud`, `Web Apps`
  - Azure App Service Deep Dive: `Azure`, `App Service`, `Distributed Systems`, `Platform Engineering`
  - Azure Functions 101: `Azure`, `Azure Functions`, `Serverless`, `Cloud`
  - Azure Functions Deep Dive: `Azure Functions`, `Serverless`, `Distributed Systems`, `gRPC`
  - Azure Kubernetes Service 101: `Azure`, `AKS`, `Kubernetes`, `Cloud`
  - Azure Kubernetes Service Deep Dive: `AKS`, `Kubernetes`, `Distributed Systems`, `Containers`
  - Azure Container Apps 101: `Azure`, `Container Apps`, `Serverless`, `Containers`
  - Azure Container Apps Deep Dive: `Container Apps`, `KEDA`, `Dapr`, `Envoy`
  - LLM from Scratch 101: `LLM`, `PyTorch`, `Transformer`, `Tutorial`
- [ ] 시리즈 내 상호 링크 연결
