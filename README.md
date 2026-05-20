# book-content

영선북스 시리즈의 원본 콘텐츠 저장소. 블로그 글을 먼저 쓰고, 쌓인 시리즈를 eBook으로 묶는 blog-first / book-later 구조이며, 하나의 원본을 Tistory, Hashnode, Medium, MkDocs, eBook 다섯 채널로 발행합니다.

`content/<series>/{ko,en}/`가 canonical source이고, 그 외 산출물(`medium/`, `exports/`, `docs/`)은 파이프라인이 생성하는 파생물입니다.

## 빠른 시작

```bash
# 저장소 검증
make check

# 시리즈 발행물 생성 예시
make tistory  SERIES=python-101
make hashnode SERIES=python-101
make medium   SERIES=python-101

# 단일 글만
make tistory-one SERIES=python-101 EPISODE=3
```

## 시리즈 목록

### AI

| 시리즈 | 설명 |
|---|---|
| [llm-app-foundations-101](./content/llm-app-foundations-101) | LLM API 기초, 토큰, 프롬프트 엔지니어링 |
| [llm-api-production-101](./content/llm-api-production-101) | Structured Output, Tool Calling, Streaming, Caching, Retry, Rate Limit |
| [vector-search-101](./content/vector-search-101) | 임베딩, FAISS, 유사도, 청크 전략 |
| [langchain-101](./content/langchain-101) | LCEL, Runnable, Retriever, Tool Calling, Streaming |
| [ai-app-patterns-101](./content/ai-app-patterns-101) | 챗봇, RAG Q&A, 문서 비서, Agent, Workflow, Human-in-the-loop |
| [rag-deep-dive](./content/rag-deep-dive) | LangChain · FAISS · RAGAS 소스로 따라가는 RAG 파이프라인 심층 분석 |
| [rag-benchmark-101](./content/rag-benchmark-101) | RAG 품질 평가 — 평가셋, 임베딩/리트리버 비교, RAGAS |
| [document-ingestion-101](./content/document-ingestion-101) | PDF 파싱, 메타데이터, 증분 인덱싱 |
| [langgraph-101](./content/langgraph-101) | 그래프 에이전트, 체크포인트, 멀티에이전트 |
| [ai-agent-101](./content/ai-agent-101) | AI Agent의 개념부터 Context Engineering, Tool Use, Workflow, Multi-Agent |
| [harness-engineering-101](./content/harness-engineering-101) | AI Agent harness — task, context, constraint, tool, test 설계 |
| [ai-evaluation-101](./content/ai-evaluation-101) | LLM 애플리케이션을 정량적으로 평가하는 방법 |
| [ai-safety-guardrails-101](./content/ai-safety-guardrails-101) | LLM 애플리케이션에 안전 장치를 적용하는 방법 |
| [llm-apps-ops-101](./content/llm-apps-ops-101) | 관측, 평가, 비용, 보안, 배포 |
| [ai-data-preparation-101](./content/ai-data-preparation-101) | AI 모델을 위한 데이터 수집, 정제, PII 익명화, 토큰화 |
| [llm-finetuning-101](./content/llm-finetuning-101) | LoRA, 데이터셋, 서빙 |
| [llm-from-scratch-101](./content/llm-from-scratch-101) | PyTorch 2.x로 토크나이저부터 챗봇까지, ~720 LOC의 작은 GPT |
| [multimodal-ai-101](./content/multimodal-ai-101) | 텍스트 + 이미지 + 오디오 + 영상을 다루는 multimodal AI |
| [korean-ai-stack-101](./content/korean-ai-stack-101) | 한국어 임베딩, OCR, 국내 LLM API |
| [ai-web-dev-101](./content/ai-web-dev-101) | AI API부터 배포까지, 초급 개발자를 위한 입문 |

### 프로그래밍

| 시리즈 | 설명 |
|---|---|
| [computer-science-101](./content/computer-science-101) | 컴퓨터공학 전공 과목들이 서로 어떻게 연결되는지 보여주는 입문 |
| [python-101](./content/python-101) | Python을 처음 시작하는 사람을 위한 입문 시리즈 |
| [git-github-101](./content/git-github-101) | commit, branch, merge, rebase, PR, issue, GitHub 협업 |
| [linux-cli-101](./content/linux-cli-101) | 파일 탐색, 권한, 프로세스, grep, pipe, shell script, SSH |
| [python-package-101](./content/python-package-101) | 프로젝트 구조, pyproject.toml, 의존성, 빌드, PyPI 배포 |
| [pytest-101](./content/pytest-101) | 기본 문법, fixture, parametrization, mock, coverage, CI |
| [oop-101](./content/oop-101) | 클래스, 캡슐화, 상속, 다형성, 추상화, SOLID |
| [functional-programming-101](./content/functional-programming-101) | 순수 함수, 불변 데이터, 고차 함수, 클로저, 함수 합성 |
| [type-hints-python-101](./content/type-hints-python-101) | Type hint, Optional, Union, TypedDict, Protocol, Generic |
| [data-structures-python-101](./content/data-structures-python-101) | Python으로 배우는 자료구조 입문 |
| [algorithms-python-101](./content/algorithms-python-101) | Python으로 시간 복잡도, 탐색, 정렬, DP, BFS/DFS, 그리디 |

### CS 핵심 과목

| 시리즈 | 설명 |
|---|---|
| [computer-science-major-101](./content/computer-science-major-101) | 컴퓨터학과 전공 과목 구성, 핵심 영역, 학습 순서 |
| [discrete-math-101](./content/discrete-math-101) | 명제, 집합, 함수, 증명, 조합, 그래프 |
| [math-for-cs-101](./content/math-for-cs-101) | 논리, 집합, 함수, 그래프, 확률, 선형대수, 미분, 정보이론 |
| [calculus-for-ml-101](./content/calculus-for-ml-101) | 기울기, 편미분, gradient, chain rule, 손실, 경사하강, backprop |
| [computer-architecture-101](./content/computer-architecture-101) | 데이터 표현, CPU, 레지스터, 메모리 계층, 캐시, 파이프라인 |
| [data-structures-101](./content/data-structures-101) | 배열, 리스트, 스택, 큐, 해시, 트리, 힙, 그래프 |
| [algorithms-101](./content/algorithms-101) | 복잡도, 탐색, 정렬, 분할 정복, DP, 그리디, 그래프 |
| [programming-languages-101](./content/programming-languages-101) | syntax, semantics, type system, scope, closure, memory model |
| [operating-systems-101](./content/operating-systems-101) | 프로세스, 스케줄링, 동시성, 메모리, 파일 시스템, 시스템 콜 |
| [computer-networks-101](./content/computer-networks-101) | IP, TCP, UDP, DNS, HTTP, TLS, 라우팅, WebSocket |
| [database-systems-101](./content/database-systems-101) | 관계형 모델, SQL, 인덱스, 트랜잭션, isolation, 정규화, 복제 |
| [distributed-systems-101](./content/distributed-systems-101) | failure model, consistency, replication, consensus, message queue |
| [compilers-101](./content/compilers-101) | lexer, parser, AST, semantic analysis, IR, optimization, codegen |
| [information-security-101](./content/information-security-101) | 인증, 인가, 암호화, TLS, 웹 보안, secret 관리, 감사 로그 |

### 소프트웨어 엔지니어링

| 시리즈 | 설명 |
|---|---|
| [software-engineering-101](./content/software-engineering-101) | 요구사항, 설계, 코드 리뷰, 테스트, 버전 관리, 문서화, 협업 |
| [clean-code-101](./content/clean-code-101) | 이름, 함수 분리, 조건 단순화, 중복 제거, 오류 처리, 리팩토링 |
| [software-design-101](./content/software-design-101) | 관심사 분리, 모듈 경계, 의존성 방향, 인터페이스, 계층 아키텍처 |
| [design-patterns-101](./content/design-patterns-101) | GoF 디자인 패턴을 Python 예시로 |
| [api-design-101](./content/api-design-101) | REST, 리소스 설계, HTTP method/status, schema, pagination, error |
| [web-development-101](./content/web-development-101) | HTML/CSS/JS, 브라우저, HTTP, 프론트/백엔드, 인증, DB, 배포 |
| [frontend-development-101](./content/frontend-development-101) | HTML/CSS, JavaScript, 컴포넌트, 라우팅, API, 빌드 |
| [backend-development-101](./content/backend-development-101) | HTTP 서버, 라우팅, 서비스, DB layer, 인증, 로깅, 테스트, 배포 |
| [testing-101](./content/testing-101) | Unit, Integration, E2E, Test Double, Mock, Coverage, CI |
| [containers-101](./content/containers-101) | Image, runtime, layer, Dockerfile, 보안 |
| [docker-101](./content/docker-101) | Image, Container, Dockerfile, Volume, Network, Compose |
| [kubernetes-101](./content/kubernetes-101) | Pod, Deployment, Service, Ingress, ConfigMap/Secret, Volume, HPA |
| [cloud-computing-101](./content/cloud-computing-101) | IaaS/PaaS/SaaS, 리전, 컴퓨트, 스토리지, 네트워크, 모니터링, 비용 |
| [serverless-101](./content/serverless-101) | FaaS, trigger/event, cold start, scaling, state, queue |
| [devops-101](./content/devops-101) | CI/CD, IaC, 환경 관리, 모니터링, 배포 전략, on-call |
| [github-actions-101](./content/github-actions-101) | Workflow, Job, Trigger, 테스트 자동화, 빌드, 배포, secret |
| [observability-101](./content/observability-101) | Metric, log, trace, dashboard, alert, SLO 기초 |
| [incident-response-101](./content/incident-response-101) | Severity, 초기 대응, 커뮤니케이션, 타임라인, RCA, 포스트모템, 런북 |
| [sre-101](./content/sre-101) | 신뢰성, SLI/SLO/SLA, 에러 버짓, 포스트모템, toil 감소, 용량 계획 |
| [secure-coding-101](./content/secure-coding-101) | 입력 검증, 인증, 인가, secret 관리, SQLi, XSS/CSRF, dependency 취약점 |
| [open-source-101](./content/open-source-101) | 라이선스부터 첫 오픈소스 기여까지 |
| [developer-career-101](./content/developer-career-101) | 개발자 커리어를 설계하는 법 |
| [data-science-career-101](./content/data-science-career-101) | 데이터 직무 커리어를 설계하는 법 |
| [portfolio-project-101](./content/portfolio-project-101) | 프로젝트 선정, README, 데모, 배포, 테스트, 의사결정 기록 |
| [capstone-project-101](./content/capstone-project-101) | 주제 선정, 문제 정의, MVP, 팀 역할, 발표, 회고 |
| [technical-writing-101](./content/technical-writing-101) | 독자 정의부터 발행 전 체크리스트까지 |

### 데이터

| 시리즈 | 설명 |
|---|---|
| [statistics-101](./content/statistics-101) | 기술 통계, 분포, 추정, 신뢰구간, 가설검정, 회귀 |
| [probability-101](./content/probability-101) | 사건, 조건부확률, 베이즈 정리, 확률변수, 분포, 중심극한정리 |
| [linear-algebra-101](./content/linear-algebra-101) | 벡터, 행렬, 내적, 선형변환, 기저, 고유값, 행렬분해, PCA |
| [data-science-101](./content/data-science-101) | 문제 정의, 수집, 정제, EDA, 시각화, 모델링, 평가, 해석 |
| [sql-101](./content/sql-101) | SELECT, JOIN, GROUP BY, subquery, window function, DML, index |
| [pandas-101](./content/pandas-101) | Series, DataFrame, 입출력, filtering, missing value, groupby, merge |
| [machine-learning-101](./content/machine-learning-101) | 지도/비지도, train/test, 회귀, 분류, 트리, 군집, regularization |
| [model-evaluation-101](./content/model-evaluation-101) | train/val/test, precision/recall, ROC, calibration |
| [mlops-101](./content/mlops-101) | 실험 관리, 모델 배포, 모니터링, drift, feature store |
| [data-warehouse-101](./content/data-warehouse-101) | OLTP/OLAP, Fact/Dimension, Star Schema, Partition, ETL/ELT, BI |
| [python-dbapi-101](./content/python-dbapi-101) | PEP 249 DB-API 2.0을 SQLite 기준으로 |
| [sqlalchemy-101](./content/sqlalchemy-101) | SQLAlchemy 2.x를 SQLite 기준으로 |
| [alembic-101](./content/alembic-101) | Alembic으로 SQLAlchemy 마이그레이션 운영 |

### Azure 클라우드

| 시리즈 | 설명 |
|---|---|
| [azure-app-service-101](./content/azure-app-service-101) | Azure App Service 입문 — 호스팅, 설정, 로그, 스케일링 |
| [azure-app-service-deep-dive](./content/azure-app-service-deep-dive) | App Service 내부 — Front-End, Worker, Sandbox, Kudu, Scaling |
| [azure-functions-101](./content/azure-functions-101) | Azure Functions 입문 — 트리거/바인딩부터 운영까지 |
| [azure-functions-deep-dive](./content/azure-functions-deep-dive) | Azure Functions Host 소스 분석 (commit-pinned) |
| [azure-aks-101](./content/azure-aks-101) | AKS 입문 |
| [azure-aks-deep-dive](./content/azure-aks-deep-dive) | AKS control plane / data plane 내부 동작 |
| [azure-aca-101](./content/azure-aca-101) | Container Apps 입문 |
| [azure-aca-deep-dive](./content/azure-aca-deep-dive) | ACA 위 KEDA · Dapr · Envoy 내부 동작 |

> 전체 카탈로그 단일 출처는 [`series.yaml`](./series.yaml). 사람이 읽는 요약은 [`SERIES.md`](./SERIES.md).

## Publication Pipelines

| Pipeline | Platform | URL | Source | Output |
|---|---|---|---|---|
| Korean Blog | Tistory | `https://yeongseonchoe.tistory.com/` | `content/<series>/ko/*.md` | `exports/tistory/<series>/*.md` |
| English Blog | Hashnode | `https://hashnode.com/@yeongseon` | `content/<series>/en/*.md` | `exports/hashnode/<series>/*.md` |
| Medium | Medium | `https://medium.com/@yeongseonchoe` | `content/<series>/en/*.md` (adaptation) | `content/<series>/medium/*.html` → `exports/medium/<series>/*.html` |
| Web Book | MkDocs | GitHub Pages / 내부 preview | `content/<series>/{ko,en}/*.md` | `docs/` |
| eBook | private `mkdocs-ebook` | — | `content/<series>/{ko,en}/*.md` | `exports/ebook-source/<series>-<lang>/` |

`ko/`와 `en/`이 canonical source. `medium/`은 `to-medium.py` 생성 파생물이며 직접 수정하지 않습니다.

eBook PDF/EPUB 생성은 항상 최신 private `mkdocs-ebook` builder 기준으로 수행합니다. 이 저장소는 source bundle까지만 생성하며, 빌드 환경에서 `mkdocs-ebook`을 최신으로 설치(`--upgrade --force-reinstall`) 후 `mkdocs-ebook build`를 실행합니다 (`EBOOK.md §1.3`).

## Related Repositories

| Repo | 역할 | Visibility |
|---|---|---|
| [book-content](https://github.com/yeongseon-books/book-content) | 원본 콘텐츠 (ko/en) · 파이프라인 · 발행물 export | private |
| [book-examples](https://github.com/yeongseon-books/book-examples) | 시리즈별 실행 가능한 예제 코드 (pytest) | public |
| [book-public-assets](https://github.com/yeongseon-books/book-public-assets) | 외부 발행용 이미지 CDN (GitHub Pages) | public |

## Quality Gates

```bash
make check              # 저장소 검증
make check-quality      # 콘텐츠 품질 경고 리포트 (warning-only)
make publish-check      # 발행 전 전체 검증 (public asset 포함)
```

개별 실행:

```bash
python3 .sisyphus/medium/finalize-posts.py --check   # idempotent dry-run: tags + TOC + ko refs
bash .sisyphus/style/check-ko.sh                      # ko translation-smell + im-not-ai S1 check
python3 scripts/check_catalog.py                      # series.yaml 일관성
python3 scripts/check_exports.py                      # export 산출물 검증
python3 scripts/check_frontmatter.py
python3 scripts/lint_captions.py
python3 scripts/check_links.py
python3 scripts/check_article_structure.py            # article structure (A-grade) check
python3 scripts/check_content_quality.py              # warning-only quality report
```

medium 변형 재생성:

```bash
python3 .sisyphus/medium/to-medium.py content/<series>/en   # → medium/<NN>.html
python3 .sisyphus/medium/finalize-posts.py
```

## Common Publishing Commands

```bash
# Tistory (Korean blog)
make tistory     SERIES=<series-id>
make tistory-one SERIES=<series-id> EPISODE=N

# Hashnode (English blog)
make hashnode     SERIES=<series-id>
make hashnode-one SERIES=<series-id> EPISODE=N

# Medium (English adaptation)
make medium SERIES=<series-id>
python3 scripts/export_medium.py <series-id> --episode N

# eBook source bundle
make ebook-source SERIES=<series-id>
```

### Sync Public Assets

```bash
make assets-sync-dry   # preview
make assets-sync       # book-content/assets/ → book-public-assets/assets/
make assets-check      # verify references in publishing outputs
python3 scripts/check_public_assets.py --target ../book-public-assets
```

## 폴더 구조

```text
book-content/                               # private — canonical source
├── README.md
├── SERIES.md, PUBLISHING.md, STYLE_GUIDE.md, EBOOK.md, ROADMAP.md
├── AGENTS.md, ARCHITECTURE.md, CONTENT_MODEL.md, ASSET_POLICY.md
├── mkdocs.yml, requirements.txt, requirements-dev.txt
├── series.yaml                             # 시리즈 카탈로그 단일 출처
├── content/
│   └── <series>/
│       ├── ko/                             # 한국어 원본
│       ├── en/                             # 영어 번역
│       └── medium/                         # Medium 붙여넣기용 .html (생성물)
├── docs/                                   # MkDocs 웹북
├── exports/
│   ├── tistory/                            # Tistory 붙여넣기용 Markdown
│   ├── hashnode/                           # Hashnode 발행용
│   ├── medium/                             # Medium 발행용 HTML
│   └── ebook-source/                       # mkdocs-ebook 입력용 bundle
├── templates/, scripts/
├── assets/<series>/<NN>/...                # 이미지 원본 (book-public-assets로 sync)
└── .sisyphus/medium/                       # finalize-posts.py / to-medium.py
```

## Public Assets

외부 발행 플랫폼에서 이미지를 안정적으로 불러오기 위해 공개 가능한 이미지 사본은 별도 public repo에 동기화합니다.

- Private source: `book-content/assets/`
- Public publishing assets: [`yeongseon-books/book-public-assets`](https://github.com/yeongseon-books/book-public-assets)
- Public URL base: `https://yeongseon-books.github.io/book-public-assets`

Canonical 글은 public asset URL을 직접 참조합니다:

```
https://yeongseon-books.github.io/book-public-assets/assets/<series>/<episode>/<file>.png
```

Tistory, Hashnode, Medium, MkDocs는 이 URL을 그대로 통과시킵니다. eBook exporter만 예외로, bundle을 self-contained로 만들기 위해 로컬 `assets/...` 경로로 역재작성합니다 ([`ASSET_POLICY.md`](./ASSET_POLICY.md)).

이미지만 public 미러링됩니다. 원고, 예제 코드, 파이프라인 스크립트, eBook source bundle은 private 유지.

## Key Documents

- [`SERIES.md`](./SERIES.md) — 전체 시리즈 카탈로그와 상태
- [`BLOG_WRITING_GUIDE.md`](./BLOG_WRITING_GUIDE.md) — 블로그 글 작성 규칙
- [`EBOOK_WRITING_GUIDE.md`](./EBOOK_WRITING_GUIDE.md) — eBook 원고 구성 규칙
- [`STYLE_GUIDE.md`](./STYLE_GUIDE.md) — 문체, 구조, 이미지, 태그, 참고자료 공통 규칙
- [`PUBLISHING.md`](./PUBLISHING.md) — Markdown → 각 파이프라인 변환 기술 규칙
- [`EBOOK.md`](./EBOOK.md) — eBook export·build 정책
- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — 저장소 구조와 빌드 흐름
- [`ROADMAP.md`](./ROADMAP.md) — 개편 로드맵
- [`CONTENT_MODEL.md`](./CONTENT_MODEL.md) — front matter, status 체계
- [`AGENTS.md`](./AGENTS.md) — 에이전트(인간/AI) 운영 규칙
- [`ASSET_POLICY.md`](./ASSET_POLICY.md) — 공개 이미지 자산 정책
