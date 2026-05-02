# Series Index

전체 콘텐츠 시리즈의 목록과 발행 상태. 단일 출처는 [`series.yaml`](./series.yaml).

> 이 파일은 `scripts/gen_series_md.py`로 자동 생성됩니다.
> 직접 편집하지 마세요 — front matter `status` 변경 후 `python3 scripts/sync_series_per.py && python3 scripts/gen_series_md.py`를 실행하세요.

## Status Legend

| Status | Meaning |
| --- | --- |
| Draft | 초안 작성 중 |
| Content Ready | 본문 완성, 코드 미검증 |
| Code Checked | 코드 실행 검증 완료 |
| Publish Ready | 발행 준비 완료 (채널별 제목 포함) |
| Ready | 발행 준비 완료 (레거시 alias) |
| Published | 발행 완료 |
| Needs Update | 업데이트 필요 (API 변경 등) |

---

## Azure

### Azure App Service 101 (`azure-app-service-101`)

Azure App Service 입문 7부작 — 호스팅, 설정, 로그, 스케일링.

- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-app-service-101/`](./content/azure-app-service-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure App Service란? - 플랫폼 아키텍처 이해하기 | [ko](./content/azure-app-service-101/ko/01-what-is-app-service.md) | [en](./content/azure-app-service-101/en/01-what-is-app-service.md) | [medium](./content/azure-app-service-101/medium/01.html) | Publish Ready |
| 2 | Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까 | [ko](./content/azure-app-service-101/ko/02-request-lifecycle.md) | [en](./content/azure-app-service-101/en/02-request-lifecycle.md) | [medium](./content/azure-app-service-101/medium/02.html) | Publish Ready |
| 3 | Hosting Models: 어떤 플랜을 선택해야 할까? | [ko](./content/azure-app-service-101/ko/03-hosting-models.md) | [en](./content/azure-app-service-101/en/03-hosting-models.md) | [medium](./content/azure-app-service-101/medium/03.html) | Publish Ready |
| 4 | 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask) | [ko](./content/azure-app-service-101/ko/04-first-deploy.md) | [en](./content/azure-app-service-101/en/04-first-deploy.md) | [medium](./content/azure-app-service-101/medium/04.html) | Publish Ready |
| 5 | Configuration 마스터하기: App Settings & 환경변수 | [ko](./content/azure-app-service-101/ko/05-configuration.md) | [en](./content/azure-app-service-101/en/05-configuration.md) | [medium](./content/azure-app-service-101/medium/05.html) | Publish Ready |
| 6 | 로그와 모니터링 기초: “앱이 느려요”에 답할 수 있는 상태 만들기 | [ko](./content/azure-app-service-101/ko/06-logging-monitoring.md) | [en](./content/azure-app-service-101/en/06-logging-monitoring.md) | [medium](./content/azure-app-service-101/medium/06.html) | Publish Ready |
| 7 | Scaling 101: 언제 Scale Up vs Scale Out? | [ko](./content/azure-app-service-101/ko/07-scaling-101.md) | [en](./content/azure-app-service-101/en/07-scaling-101.md) | [medium](./content/azure-app-service-101/medium/07.html) | Publish Ready |

### Azure App Service Deep Dive (`azure-app-service-deep-dive`)

App Service 내부 — Front-End, Worker, Sandbox, Kudu, Scaling.

- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-app-service-deep-dive/`](./content/azure-app-service-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | App Service 플랫폼 아키텍처 — Front-End·Worker·File Server | [ko](./content/azure-app-service-deep-dive/ko/01-platform-architecture.md) | [en](./content/azure-app-service-deep-dive/en/01-platform-architecture.md) | [medium](./content/azure-app-service-deep-dive/medium/01.html) | Publish Ready |
| 2 | Front-End과 ARR — 요청은 어떻게 워커에 도달하는가 | [ko](./content/azure-app-service-deep-dive/ko/02-front-end-and-arr.md) | [en](./content/azure-app-service-deep-dive/en/02-front-end-and-arr.md) | [medium](./content/azure-app-service-deep-dive/medium/02.html) | Publish Ready |
| 3 | Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가 | [ko](./content/azure-app-service-deep-dive/ko/03-worker-and-sandbox.md) | [en](./content/azure-app-service-deep-dive/en/03-worker-and-sandbox.md) | [medium](./content/azure-app-service-deep-dive/medium/03.html) | Publish Ready |
| 4 | 배포와 Kudu — 빌드·동기화·릴리스의 안쪽 | [ko](./content/azure-app-service-deep-dive/ko/04-deployment-and-kudu.md) | [en](./content/azure-app-service-deep-dive/en/04-deployment-and-kudu.md) | [medium](./content/azure-app-service-deep-dive/medium/04.html) | Publish Ready |
| 5 | 스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로 | [ko](./content/azure-app-service-deep-dive/ko/05-scaling-internals.md) | [en](./content/azure-app-service-deep-dive/en/05-scaling-internals.md) | [medium](./content/azure-app-service-deep-dive/medium/05.html) | Publish Ready |
| 6 | 콜드 스타트와 Warmup — 첫 요청이 비싼 이유 | [ko](./content/azure-app-service-deep-dive/ko/06-cold-start-and-warmup.md) | [en](./content/azure-app-service-deep-dive/en/06-cold-start-and-warmup.md) | [medium](./content/azure-app-service-deep-dive/medium/06.html) | Publish Ready |

### Azure Functions 101 (`azure-functions-101`)

Azure Functions 입문 7부작 — 트리거/바인딩부터 운영까지.

- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-functions-101/`](./content/azure-functions-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Functions란? — 이벤트가 함수를 호출하는 세상 | [ko](./content/azure-functions-101/ko/01-what-is-azure-functions.md) | [en](./content/azure-functions-101/en/01-what-is-azure-functions.md) | [medium](./content/azure-functions-101/medium/01.html) | Publish Ready |
| 2 | 트리거와 바인딩 — 함수 입출력의 모든 것 | [ko](./content/azure-functions-101/ko/02-triggers-and-bindings.md) | [en](./content/azure-functions-101/en/02-triggers-and-bindings.md) | [medium](./content/azure-functions-101/medium/02.html) | Publish Ready |
| 3 | Host와 Worker — 함수는 누가 실행하는가 | [ko](./content/azure-functions-101/ko/03-host-and-worker.md) | [en](./content/azure-functions-101/en/03-host-and-worker.md) | [medium](./content/azure-functions-101/medium/03.html) | Publish Ready |
| 4 | 함수 하나 배포하기 — 로컬에서 Azure까지 | [ko](./content/azure-functions-101/ko/04-first-deploy.md) | [en](./content/azure-functions-101/en/04-first-deploy.md) | [medium](./content/azure-functions-101/medium/04.html) | Publish Ready |
| 5 | 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated | [ko](./content/azure-functions-101/ko/05-choosing-a-plan.md) | [en](./content/azure-functions-101/en/05-choosing-a-plan.md) | [medium](./content/azure-functions-101/medium/05.html) | Publish Ready |
| 6 | 스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간 | [ko](./content/azure-functions-101/ko/06-scaling-and-cold-start.md) | [en](./content/azure-functions-101/en/06-scaling-and-cold-start.md) | [medium](./content/azure-functions-101/medium/06.html) | Publish Ready |
| 7 | 모니터링과 운영 기초 | [ko](./content/azure-functions-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-functions-101/en/07-monitoring-and-ops.md) | [medium](./content/azure-functions-101/medium/07.html) | Publish Ready |

### Azure Functions Deep Dive (`azure-functions-deep-dive`)

Azure Functions Host 소스 분석 시리즈 (commit-pinned).

- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-functions-deep-dive/`](./content/azure-functions-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기 | [ko](./content/azure-functions-deep-dive/ko/01-host-bootstrap.md) | [en](./content/azure-functions-deep-dive/en/01-host-bootstrap.md) | [medium](./content/azure-functions-deep-dive/medium/01.html) | Publish Ready |
| 2 | Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법 | [ko](./content/azure-functions-deep-dive/ko/02-worker-process.md) | [en](./content/azure-functions-deep-dive/en/02-worker-process.md) | [medium](./content/azure-functions-deep-dive/medium/02.html) | Publish Ready |
| 3 | gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가 | [ko](./content/azure-functions-deep-dive/ko/03-grpc-event-stream.md) | [en](./content/azure-functions-deep-dive/en/03-grpc-event-stream.md) | [medium](./content/azure-functions-deep-dive/medium/03.html) | Publish Ready |
| 4 | Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 | [ko](./content/azure-functions-deep-dive/ko/04-dispatcher-and-invocation.md) | [en](./content/azure-functions-deep-dive/en/04-dispatcher-and-invocation.md) | [medium](./content/azure-functions-deep-dive/medium/04.html) | Publish Ready |
| 5 | 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이 | [ko](./content/azure-functions-deep-dive/ko/05-scaling-internals.md) | [en](./content/azure-functions-deep-dive/en/05-scaling-internals.md) | [medium](./content/azure-functions-deep-dive/medium/05.html) | Publish Ready |
| 6 | 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 | [ko](./content/azure-functions-deep-dive/ko/06-cold-start-placeholder.md) | [en](./content/azure-functions-deep-dive/en/06-cold-start-placeholder.md) | [medium](./content/azure-functions-deep-dive/medium/06.html) | Publish Ready |

### Azure Kubernetes Service 101 (`azure-aks-101`)

AKS 입문 시리즈.

- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aks-101/`](./content/azure-aks-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes | [ko](./content/azure-aks-101/ko/01-what-is-aks.md) | [en](./content/azure-aks-101/en/01-what-is-aks.md) | [medium](./content/azure-aks-101/medium/01.html) | Publish Ready |
| 2 | 클러스터 아키텍처 — Control Plane과 Node Pool | [ko](./content/azure-aks-101/ko/02-cluster-architecture.md) | [en](./content/azure-aks-101/en/02-cluster-architecture.md) | [medium](./content/azure-aks-101/medium/02.html) | Publish Ready |
| 3 | 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI | [ko](./content/azure-aks-101/ko/03-first-cluster-and-deploy.md) | [en](./content/azure-aks-101/en/03-first-cluster-and-deploy.md) | [medium](./content/azure-aks-101/medium/03.html) | Publish Ready |
| 4 | Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식 | [ko](./content/azure-aks-101/ko/04-pod-deployment-service.md) | [en](./content/azure-aks-101/en/04-pod-deployment-service.md) | [medium](./content/azure-aks-101/medium/04.html) | Publish Ready |
| 5 | 네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길 | [ko](./content/azure-aks-101/ko/05-networking-and-ingress.md) | [en](./content/azure-aks-101/en/05-networking-and-ingress.md) | [medium](./content/azure-aks-101/medium/05.html) | Publish Ready |
| 6 | 스케일링 — HPA, Cluster Autoscaler, KEDA | [ko](./content/azure-aks-101/ko/06-scaling-hpa-ca-keda.md) | [en](./content/azure-aks-101/en/06-scaling-hpa-ca-keda.md) | [medium](./content/azure-aks-101/medium/06.html) | Publish Ready |
| 7 | 모니터링과 운영 — Container Insights, 로그, 알람 | [ko](./content/azure-aks-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-aks-101/en/07-monitoring-and-ops.md) | [medium](./content/azure-aks-101/medium/07.html) | Publish Ready |

### Azure Kubernetes Service Deep Dive (`azure-aks-deep-dive`)

AKS control plane / data plane 내부 동작.

- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aks-deep-dive/`](./content/azure-aks-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Control Plane 해부 — AKS가 사용자에게서 가린 것 | [ko](./content/azure-aks-deep-dive/ko/01-control-plane-anatomy.md) | [en](./content/azure-aks-deep-dive/en/01-control-plane-anatomy.md) | [medium](./content/azure-aks-deep-dive/medium/01.html) | Publish Ready |
| 2 | kubelet과 containerd — 노드 위에서 컨테이너가 뜨기까지 | [ko](./content/azure-aks-deep-dive/ko/02-kubelet-and-containerd.md) | [en](./content/azure-aks-deep-dive/en/02-kubelet-and-containerd.md) | [medium](./content/azure-aks-deep-dive/medium/02.html) | Publish Ready |
| 3 | CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가 | [ko](./content/azure-aks-deep-dive/ko/03-cni-and-azure-cni-overlay.md) | [en](./content/azure-aks-deep-dive/en/03-cni-and-azure-cni-overlay.md) | [medium](./content/azure-aks-deep-dive/medium/03.html) | Publish Ready |
| 4 | Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가 | [ko](./content/azure-aks-deep-dive/ko/04-scheduler-and-pod-placement.md) | [en](./content/azure-aks-deep-dive/en/04-scheduler-and-pod-placement.md) | [medium](./content/azure-aks-deep-dive/medium/04.html) | Publish Ready |
| 5 | HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프 | [ko](./content/azure-aks-deep-dive/ko/05-hpa-and-cluster-autoscaler-internals.md) | [en](./content/azure-aks-deep-dive/en/05-hpa-and-cluster-autoscaler-internals.md) | [medium](./content/azure-aks-deep-dive/medium/05.html) | Publish Ready |
| 6 | KEDA 내부 — ScaledObject가 HPA를 만드는 방식 | [ko](./content/azure-aks-deep-dive/ko/06-keda-internals.md) | [en](./content/azure-aks-deep-dive/en/06-keda-internals.md) | [medium](./content/azure-aks-deep-dive/medium/06.html) | Publish Ready |

### Azure Container Apps 101 (`azure-aca-101`)

Container Apps 입문 시리즈.

- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aca-101/`](./content/azure-aca-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기 | [ko](./content/azure-aca-101/ko/01-what-is-aca.md) | [en](./content/azure-aca-101/en/01-what-is-aca.md) | [medium](./content/azure-aca-101/medium/01.html) | Publish Ready |
| 2 | Environment·Container App·Revision — 세 단어로 보는 ACA | [ko](./content/azure-aca-101/ko/02-environment-app-revision.md) | [en](./content/azure-aca-101/en/02-environment-app-revision.md) | [medium](./content/azure-aca-101/medium/02.html) | Publish Ready |
| 3 | 첫 앱 배포하기 — Python/FastAPI | [ko](./content/azure-aca-101/ko/03-first-deploy.md) | [en](./content/azure-aca-101/en/03-first-deploy.md) | [medium](./content/azure-aca-101/medium/03.html) | Publish Ready |
| 4 | Ingress와 트래픽 분할 — Revision 기반 배포 전략 | [ko](./content/azure-aca-101/ko/04-ingress-and-traffic-split.md) | [en](./content/azure-aca-101/en/04-ingress-and-traffic-split.md) | [medium](./content/azure-aca-101/medium/04.html) | Publish Ready |
| 5 | 스케일링 — KEDA scaler와 0-to-N | [ko](./content/azure-aca-101/ko/05-scaling-with-keda.md) | [en](./content/azure-aca-101/en/05-scaling-with-keda.md) | [medium](./content/azure-aca-101/medium/05.html) | Publish Ready |
| 6 | Dapr 통합 — 사이드카로 얻는 것 | [ko](./content/azure-aca-101/ko/06-dapr-integration.md) | [en](./content/azure-aca-101/en/06-dapr-integration.md) | [medium](./content/azure-aca-101/medium/06.html) | Publish Ready |
| 7 | 모니터링과 운영 — Log Analytics와 Application Insights | [ko](./content/azure-aca-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-aca-101/en/07-monitoring-and-ops.md) | [medium](./content/azure-aca-101/medium/07.html) | Publish Ready |

### Azure Container Apps Deep Dive (`azure-aca-deep-dive`)

ACA 위에 얹힌 KEDA·Dapr·Envoy 내부 동작.

- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aca-deep-dive/`](./content/azure-aca-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것 | [ko](./content/azure-aca-deep-dive/ko/01-aca-architecture.md) | [en](./content/azure-aca-deep-dive/en/01-aca-architecture.md) | [medium](./content/azure-aca-deep-dive/medium/01.html) | Publish Ready |
| 2 | Environment 내부 — 네트워크·관측·Dapr 스코프의 경계 | [ko](./content/azure-aca-deep-dive/ko/02-environment-internals.md) | [en](./content/azure-aca-deep-dive/en/02-environment-internals.md) | [medium](./content/azure-aca-deep-dive/medium/02.html) | Publish Ready |
| 3 | Revision과 트래픽 분할 — Envoy 가중치는 어디에서 오는가 | [ko](./content/azure-aca-deep-dive/ko/03-revision-and-traffic-split.md) | [en](./content/azure-aca-deep-dive/en/03-revision-and-traffic-split.md) | [medium](./content/azure-aca-deep-dive/medium/03.html) | Publish Ready |
| 4 | ACA 안의 KEDA — Scale Rule이 만드는 것 | [ko](./content/azure-aca-deep-dive/ko/04-keda-in-aca.md) | [en](./content/azure-aca-deep-dive/en/04-keda-in-aca.md) | [medium](./content/azure-aca-deep-dive/medium/04.html) | Publish Ready |
| 5 | Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스 | [ko](./content/azure-aca-deep-dive/ko/05-dapr-sidecar-internals.md) | [en](./content/azure-aca-deep-dive/en/05-dapr-sidecar-internals.md) | [medium](./content/azure-aca-deep-dive/medium/05.html) | Publish Ready |
| 6 | Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지 | [ko](./content/azure-aca-deep-dive/ko/06-envoy-ingress-path.md) | [en](./content/azure-aca-deep-dive/en/06-envoy-ingress-path.md) | [medium](./content/azure-aca-deep-dive/medium/06.html) | Publish Ready |

---
