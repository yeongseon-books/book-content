# 용어집 (Glossary)

이 저장소 전체에서 사용하는 기술 용어의 한국어-영어 대역 목록입니다.
동일 개념을 ko/en 포스팅에서 일관되게 표기하기 위한 단일 출처입니다.

---

## 범례

| 표기 | 의미 |
| --- | --- |
| **한국어** | ko/ 포스팅에서 사용하는 표기 |
| **English** | en/ 포스팅에서 사용하는 표기 |
| 비고 | 혼용 금지 표기, 약어 등 |

---

## A — Azure 플랫폼

| 한국어 | English | 비고 |
| --- | --- | --- |
| App Service 플랜 | App Service Plan | "앱 서비스 플랜"으로 표기 금지 |
| 배포 슬롯 | Deployment Slot | |
| 스케일 아웃 | Scale Out | "수평 확장"과 혼용 가능 |
| 스케일 업 | Scale Up | "수직 확장"과 혼용 가능 |
| 콜드 스타트 | Cold Start | |
| 웜업 | Warmup | |
| 워커 프로세스 | Worker Process | |
| 바인딩 | Binding | Azure Functions 전용 |
| 트리거 | Trigger | |
| 함수 앱 | Function App | |
| 호스트 | Host | Azure Functions host.json 기준 |
| 소비 플랜 | Consumption Plan | |
| 프리미엄 플랜 | Premium Plan | |
| Flex Consumption 플랜 | Flex Consumption Plan | 번역하지 않음 |
| 쿠두 | Kudu | SCM(Source Control Manager) |
| 인그레스 | Ingress | |
| 레비전 | Revision | Azure Container Apps 전용 |
| 데이터플레인 | Data Plane | |
| 관리 플레인 | Management Plane | |
| 컨트롤 플레인 | Control Plane | |
| 노드 풀 | Node Pool | AKS 전용 |
| 파드 | Pod | |
| 디플로이먼트 | Deployment | k8s 리소스 |
| 서비스 (k8s) | Service | k8s 리소스, 문맥으로 구분 |
| HPA | HPA (Horizontal Pod Autoscaler) | 약어 그대로 사용 |
| KEDA | KEDA | 약어 그대로 사용 |
| Dapr | Dapr | 약어 그대로 사용 |
| Azure CNI | Azure CNI | 번역하지 않음 |
| Application Insights | Application Insights | 번역하지 않음 |

---

## B — LLM / AI 기초

| 한국어 | English | 비고 |
| --- | --- | --- |
| 거대 언어 모델 | Large Language Model (LLM) | 이후 LLM으로 약칭 |
| 추론 | Inference | 모델 실행 맥락 |
| 파인튜닝 | Fine-tuning | "미세 조정"은 혼용 가능 |
| 프롬프트 | Prompt | 번역하지 않음 |
| 시스템 프롬프트 | System Prompt | |
| 컨텍스트 창 | Context Window | |
| 토큰 | Token | 번역하지 않음 |
| 토크나이저 | Tokenizer | |
| 임베딩 | Embedding | |
| 임베딩 벡터 | Embedding Vector | |
| 코사인 유사도 | Cosine Similarity | |
| 청크 | Chunk | 문서 분할 단위 |
| 청킹 | Chunking | |
| 컨텍스트 주입 | Context Injection | RAG 전용 |
| 검색 증강 생성 | Retrieval-Augmented Generation (RAG) | 이후 RAG으로 약칭 |
| 검색기 | Retriever | |
| 벡터 스토어 | Vector Store | |
| 벡터 DB | Vector DB | Vector Database 약칭 |
| 근사 최근접 이웃 | Approximate Nearest Neighbor (ANN) | |
| 스트리밍 | Streaming | 번역하지 않음 |
| 구조화 출력 | Structured Output | |
| 툴 호출 | Tool Calling | "함수 호출(Function Calling)"은 구버전 표기 |
| 재시도 | Retry | |
| 속도 제한 | Rate Limit | |
| 캐싱 | Caching | |

---

## C — LangChain / LangGraph

| 한국어 | English | 비고 |
| --- | --- | --- |
| 체인 | Chain | |
| 파이프라인 | Pipeline | |
| LCEL | LCEL (LangChain Expression Language) | 약어 그대로 사용 |
| Runnable | Runnable | 번역하지 않음 |
| 프롬프트 템플릿 | Prompt Template | |
| 출력 파서 | Output Parser | |
| 에이전트 | Agent | |
| 그래프 | Graph | LangGraph 전용 |
| 노드 | Node | LangGraph 전용 |
| 엣지 | Edge | LangGraph 전용 |
| 조건부 엣지 | Conditional Edge | |
| 체크포인트 | Checkpoint | |
| 상태 | State | LangGraph State 전용 |
| 멀티 에이전트 | Multi-Agent | |

---

## D — 모델 / 학습

| 한국어 | English | 비고 |
| --- | --- | --- |
| 사전 학습 | Pre-training | |
| 지시 튜닝 | Instruction Tuning | |
| LoRA | LoRA (Low-Rank Adaptation) | 약어 그대로 사용 |
| QLoRA | QLoRA | 약어 그대로 사용 |
| 퍼플렉서티 | Perplexity | |
| 데이터셋 | Dataset | 번역하지 않음 |
| 배치 크기 | Batch Size | |
| 학습률 | Learning Rate | |
| 에폭 | Epoch | |
| 체크포인트 (학습) | Checkpoint | 학습 맥락에서는 저장 시점 의미 |
| 서빙 | Serving | 모델 배포 후 추론 제공 |

---

## E — RAG 평가

| 한국어 | English | 비고 |
| --- | --- | --- |
| 검색 정확도 | Retrieval Precision | |
| 검색 재현율 | Retrieval Recall | |
| 충실도 | Faithfulness | RAGAS 지표 |
| 답변 관련성 | Answer Relevancy | RAGAS 지표 |
| 컨텍스트 정밀도 | Context Precision | RAGAS 지표 |
| 컨텍스트 재현율 | Context Recall | RAGAS 지표 |
| 엔드투엔드 평가 | End-to-End Evaluation | |
| 벤치마크 | Benchmark | 번역하지 않음 |

---

## F — 한국어 AI 스택

| 한국어 | English | 비고 |
| --- | --- | --- |
| 한국어 임베딩 | Korean Embedding | |
| KoSimCSE | KoSimCSE | 약어 그대로 사용 |
| BGE-M3 | BGE-M3 | 약어 그대로 사용 |
| CLOVA OCR | CLOVA OCR | 번역하지 않음 |
| HyperCLOVA X | HyperCLOVA X | 번역하지 않음 |
| Solar | Solar (Upstage) | 번역하지 않음 |

---

## G — 운영 / LLMOps

| 한국어 | English | 비고 |
| --- | --- | --- |
| 모니터링 | Monitoring | |
| 로깅 | Logging | |
| 추적 | Tracing | |
| 비용 추적 | Cost Tracking | |
| 보안 | Security | |
| 프롬프트 인젝션 | Prompt Injection | |
| 가드레일 | Guardrail | |
| 배포 | Deployment | |
| 관찰 가능성 | Observability | |

---

## 혼용 금지 목록

| 쓰지 말 것 | 대신 쓸 것 | 이유 |
| --- | --- | --- |
| 미세 조정 (단독 사용) | 파인튜닝 | 본 시리즈 표기 기준 |
| 함수 호출 (Function Calling) | 툴 호출 (Tool Calling) | OpenAI 최신 명칭 기준 |
| 앱 서비스 플랜 | App Service 플랜 | 공식 명칭 준수 |
| 수평/수직 확장 | 스케일 아웃 / 스케일 업 | 혼용 가능하나 단일 표기 권장 |
| LLM 모델 | LLM | 중복 표기 |
