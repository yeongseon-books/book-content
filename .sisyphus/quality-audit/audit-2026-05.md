# Cross-Series Quality Audit

Generated: 2026-05-20T11:33:22+00:00

Signals:
- `BadImg`: PNG height <= 100px under `assets/<series>/`
- `Synt`: Python fenced code blocks that fail `ast.parse()`
- `BrkLink`: `github.com/yeongseon-books/<repo>` references to missing repos (404-confirmed only)
- `Shrt`: markdown body shorter than 150 lines after front matter
- `NoEn`: `ko/*.md` file with no matching `en/*.md` basename

Python syntax skip rule:
- Skip a Python fence only when its first non-empty line starts with `# pseudocode`, `# pseudo-code`, or `# example`.

Gold-reference image exemptions:
- `azure-app-service-101` excludes 6 known low-height strip diagrams so the repository gold reference calibrates to zero findings:
  - `assets/azure-app-service-101/04/01-deployment-pipeline.en.png`
  - `assets/azure-app-service-101/04/01-deployment-pipeline.ko.png`
  - `assets/azure-app-service-101/05/key-vault-reference-flow.en.png`
  - `assets/azure-app-service-101/05/key-vault-reference-flow.ko.png`
  - `assets/azure-app-service-101/06/03-correlation-id-flow.en.png`
  - `assets/azure-app-service-101/06/03-correlation-id-flow.ko.png`

Warnings:
- none

## Summary

- Series audited: **92**
- Series with any issue: **55**
- Series at or above 5 issues: **42**
- Total issues: **532**
  - BadImg: **532**
  - Synt: **0**
  - BrkLink: **0**
  - Shrt: **0**
  - NoEn: **0**
- Repo existence check method: **gh**

## Ranked series

| Rank | Series | Total | BadImg | Synt | BrkLink | Shrt | NoEn |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `python-dbapi-101` | 42 | 42 | 0 | 0 | 0 | 0 |
| 2 | `langchain-101` | 25 | 25 | 0 | 0 | 0 | 0 |
| 3 | `rag-deep-dive` | 24 | 24 | 0 | 0 | 0 | 0 |
| 4 | `azure-app-service-deep-dive` | 18 | 18 | 0 | 0 | 0 | 0 |
| 5 | `developer-career-101` | 18 | 18 | 0 | 0 | 0 | 0 |
| 6 | `sqlalchemy-101` | 18 | 18 | 0 | 0 | 0 | 0 |
| 7 | `open-source-101` | 16 | 16 | 0 | 0 | 0 | 0 |
| 8 | `vector-search-101` | 16 | 16 | 0 | 0 | 0 | 0 |
| 9 | `ai-web-dev-101` | 14 | 14 | 0 | 0 | 0 | 0 |
| 10 | `software-engineering-101` | 14 | 14 | 0 | 0 | 0 | 0 |
| 11 | `testing-101` | 14 | 14 | 0 | 0 | 0 | 0 |
| 12 | `data-science-101` | 12 | 12 | 0 | 0 | 0 | 0 |
| 13 | `docker-101` | 12 | 12 | 0 | 0 | 0 | 0 |
| 14 | `incident-response-101` | 12 | 12 | 0 | 0 | 0 | 0 |
| 15 | `llm-apps-ops-101` | 12 | 12 | 0 | 0 | 0 | 0 |
| 16 | `api-design-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 17 | `azure-aks-deep-dive` | 10 | 10 | 0 | 0 | 0 | 0 |
| 18 | `clean-code-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 19 | `containers-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 20 | `github-actions-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 21 | `linear-algebra-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 22 | `llm-api-production-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 23 | `pandas-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 24 | `python-package-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 25 | `secure-coding-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 26 | `computer-networks-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 27 | `devops-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 28 | `frontend-development-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 29 | `kubernetes-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 30 | `llm-from-scratch-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 31 | `probability-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 32 | `rag-benchmark-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 33 | `serverless-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 34 | `software-design-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 35 | `sql-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 36 | `sre-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 37 | `cloud-computing-101` | 6 | 6 | 0 | 0 | 0 | 0 |
| 38 | `machine-learning-101` | 6 | 6 | 0 | 0 | 0 | 0 |
| 39 | `mlops-101` | 6 | 6 | 0 | 0 | 0 | 0 |
| 40 | `observability-101` | 6 | 6 | 0 | 0 | 0 | 0 |
| 41 | `azure-functions-deep-dive` | 5 | 5 | 0 | 0 | 0 | 0 |
| 42 | `git-github-101` | 5 | 5 | 0 | 0 | 0 | 0 |
| 43 | `alembic-101` | 4 | 4 | 0 | 0 | 0 | 0 |
| 44 | `azure-aca-101` | 4 | 4 | 0 | 0 | 0 | 0 |
| 45 | `backend-development-101` | 4 | 4 | 0 | 0 | 0 | 0 |
| 46 | `calculus-for-ml-101` | 4 | 4 | 0 | 0 | 0 | 0 |
| 47 | `data-warehouse-101` | 4 | 4 | 0 | 0 | 0 | 0 |
| 48 | `design-patterns-101` | 4 | 4 | 0 | 0 | 0 | 0 |
| 49 | `functional-programming-101` | 4 | 4 | 0 | 0 | 0 | 0 |
| 50 | `programming-languages-101` | 4 | 4 | 0 | 0 | 0 | 0 |
| 51 | `multimodal-ai-101` | 3 | 3 | 0 | 0 | 0 | 0 |
| 52 | `ai-agent-101` | 2 | 2 | 0 | 0 | 0 | 0 |
| 53 | `azure-aks-101` | 2 | 2 | 0 | 0 | 0 | 0 |
| 54 | `azure-functions-101` | 2 | 2 | 0 | 0 | 0 | 0 |
| 55 | `operating-systems-101` | 2 | 2 | 0 | 0 | 0 | 0 |

## python-dbapi-101 — Total 42

- BadImg=42 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/python-dbapi-101/01/01-01-why-db-api-2-0-the-problem-pep-249-solve.en.png:1` — PNG height 67px <= 100px (size=1185x67)
- `assets/python-dbapi-101/01/01-01-why-db-api-2-0-the-problem-pep-249-solve.ko.png:1` — PNG height 67px <= 100px (size=1077x67)
- `assets/python-dbapi-101/01/01-04-4-only-paramstyle-really-differs.en.png:1` — PNG height 67px <= 100px (size=1144x67)
- `assets/python-dbapi-101/01/01-04-4-only-paramstyle-really-differs.ko.png:1` — PNG height 67px <= 100px (size=1041x67)
- `assets/python-dbapi-101/02/02-01-connection-and-cursor-lifecycle.en.png:1` — PNG height 67px <= 100px (size=1175x67)
- ... 37 more

## langchain-101 — Total 25

- BadImg=25 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/langchain-101/01/01-01-questions-this-post-answers.en.png:1` — PNG height 67px <= 100px (size=977x67)
- `assets/langchain-101/01/01-01-questions-this-post-answers.ko.png:1` — PNG height 67px <= 100px (size=989x67)
- `assets/langchain-101/01/01-02-the-flow-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=1006x67)
- `assets/langchain-101/01/01-02-the-flow-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=989x67)
- `assets/langchain-101/01/01-03-lcel-and-the-pipe-operator.en.png:1` — PNG height 52px <= 100px (size=1352x52)
- ... 20 more

## rag-deep-dive — Total 24

- BadImg=24 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/rag-deep-dive/01/01-02-character-splitter-merge-window.en.png:1` — PNG height 76px <= 100px (size=884x76)
- `assets/rag-deep-dive/01/01-02-character-splitter-merge-window.ko.png:1` — PNG height 91px <= 100px (size=884x91)
- `assets/rag-deep-dive/02/02-02-indexflat-search-internals.en.png:1` — PNG height 59px <= 100px (size=884x59)
- `assets/rag-deep-dive/02/02-02-indexflat-search-internals.ko.png:1` — PNG height 53px <= 100px (size=884x53)
- `assets/rag-deep-dive/02/02-03-langchain-faiss-layers.en.png:1` — PNG height 45px <= 100px (size=884x45)
- ... 19 more

## azure-app-service-deep-dive — Total 18

- BadImg=18 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/azure-app-service-deep-dive/01/01-01-kudu-is-the-deployment-buddy-site.en.png:1` — PNG height 88px <= 100px (size=1210x88)
- `assets/azure-app-service-deep-dive/01/01-01-kudu-is-the-deployment-buddy-site.ko.png:1` — PNG height 88px <= 100px (size=1210x88)
- `assets/azure-app-service-deep-dive/01/01-05-where-functions-fits-in-this-picture.en.png:1` — PNG height 67px <= 100px (size=920x67)
- `assets/azure-app-service-deep-dive/01/01-05-where-functions-fits-in-this-picture.ko.png:1` — PNG height 67px <= 100px (size=920x67)
- `assets/azure-app-service-deep-dive/04/04-01-the-deployment-pipeline-in-one-picture.en.png:1` — PNG height 80px <= 100px (size=1384x80)
- ... 13 more

## developer-career-101 — Total 18

- BadImg=18 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/developer-career-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 70px <= 100px (size=882x70)
- `assets/developer-career-101/02/02-01-concept-at-a-glance.ko.png:1` — PNG height 70px <= 100px (size=882x70)
- `assets/developer-career-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 70px <= 100px (size=675x70)
- `assets/developer-career-101/03/03-01-concept-at-a-glance.ko.png:1` — PNG height 70px <= 100px (size=675x70)
- `assets/developer-career-101/04/04-01-concept-at-a-glance.en.png:1` — PNG height 70px <= 100px (size=813x70)
- ... 13 more

## sqlalchemy-101 — Total 18

- BadImg=18 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/sqlalchemy-101/01/01-02-why-this-matters.en.png:1` — PNG height 67px <= 100px (size=1142x67)
- `assets/sqlalchemy-101/01/01-02-why-this-matters.ko.png:1` — PNG height 67px <= 100px (size=1110x67)
- `assets/sqlalchemy-101/01/01-03-mental-model.en.png:1` — PNG height 67px <= 100px (size=1289x67)
- `assets/sqlalchemy-101/01/01-03-mental-model.ko.png:1` — PNG height 67px <= 100px (size=1237x67)
- `assets/sqlalchemy-101/02/02-03-mental-model.en.png:1` — PNG height 67px <= 100px (size=976x67)
- ... 13 more

## open-source-101 — Total 16

- BadImg=16 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/open-source-101/01/01-01-a-concept-map-you-can-keep-in-your-head.en.png:1` — PNG height 67px <= 100px (size=625x67)
- `assets/open-source-101/01/01-01-a-concept-map-you-can-keep-in-your-head.ko.png:1` — PNG height 67px <= 100px (size=588x67)
- `assets/open-source-101/03/03-01-fix-the-reading-order-first.en.png:1` — PNG height 67px <= 100px (size=728x67)
- `assets/open-source-101/03/03-01-fix-the-reading-order-first.ko.png:1` — PNG height 67px <= 100px (size=666x67)
- `assets/open-source-101/04/04-01-put-the-flow-in-your-head-first.en.png:1` — PNG height 67px <= 100px (size=885x67)
- ... 11 more

## vector-search-101 — Total 16

- BadImg=16 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/vector-search-101/01/01-01-what-is-an-embedding-converting-text-int.en.png:1` — PNG height 62px <= 100px (size=1384x62)
- `assets/vector-search-101/01/01-01-what-is-an-embedding-converting-text-int.ko.png:1` — PNG height 67px <= 100px (size=1251x67)
- `assets/vector-search-101/02/02-01-first-embedding.en.png:1` — PNG height 67px <= 100px (size=1185x67)
- `assets/vector-search-101/02/02-01-first-embedding.ko.png:1` — PNG height 67px <= 100px (size=1093x67)
- `assets/vector-search-101/02/02-01-huggingface-embeddings-in-practice-creat.en.png:1` — PNG height 79px <= 100px (size=1384x79)
- ... 11 more

## ai-web-dev-101 — Total 14

- BadImg=14 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/ai-web-dev-101/01/api-call-overview.en.png:1` — PNG height 84px <= 100px (size=847x84)
- `assets/ai-web-dev-101/01/api-call-overview.ko.png:1` — PNG height 84px <= 100px (size=699x84)
- `assets/ai-web-dev-101/03/api-route-handler-flow.en.png:1` — PNG height 94px <= 100px (size=887x94)
- `assets/ai-web-dev-101/03/api-route-handler-flow.ko.png:1` — PNG height 94px <= 100px (size=789x94)
- `assets/ai-web-dev-101/04/plain-llm-vs-rag.en.png:1` — PNG height 84px <= 100px (size=1184x84)
- ... 9 more

## software-engineering-101 — Total 14

- BadImg=14 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/software-engineering-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=825x67)
- `assets/software-engineering-101/02/02-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=825x67)
- `assets/software-engineering-101/04/04-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=1074x67)
- `assets/software-engineering-101/04/04-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=1074x67)
- `assets/software-engineering-101/05/05-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=620x67)
- ... 9 more

## testing-101 — Total 14

- BadImg=14 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/testing-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=816x67)
- `assets/testing-101/01/01-01-diagram.ko.png:1` — PNG height 67px <= 100px (size=816x67)
- `assets/testing-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 87px <= 100px (size=642x87)
- `assets/testing-101/03/03-01-diagram.ko.png:1` — PNG height 87px <= 100px (size=642x87)
- `assets/testing-101/04/04-01-concept-at-a-glance.en.png:1` — PNG height 69px <= 100px (size=572x69)
- ... 9 more

## data-science-101 — Total 12

- BadImg=12 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/data-science-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=702x67)
- `assets/data-science-101/01/01-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=652x67)
- `assets/data-science-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=1014x67)
- `assets/data-science-101/02/02-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=858x67)
- `assets/data-science-101/04/04-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=1118x67)
- ... 7 more

## docker-101 — Total 12

- BadImg=12 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/docker-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=744x67)
- `assets/docker-101/01/01-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=744x67)
- `assets/docker-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=951x67)
- `assets/docker-101/02/02-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=951x67)
- `assets/docker-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 88px <= 100px (size=835x88)
- ... 7 more

## incident-response-101 — Total 12

- BadImg=12 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/incident-response-101/02/02-01-diagram-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=596x67)
- `assets/incident-response-101/02/02-01-diagram-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=565x67)
- `assets/incident-response-101/03/03-01-diagram-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=772x67)
- `assets/incident-response-101/03/03-01-diagram-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=694x67)
- `assets/incident-response-101/06/06-01-diagram-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=909x67)
- ... 7 more

## llm-apps-ops-101 — Total 12

- BadImg=12 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/llm-apps-ops-101/02/02-01-big-picture.en.png:1` — PNG height 67px <= 100px (size=965x67)
- `assets/llm-apps-ops-101/02/02-01-big-picture.ko.png:1` — PNG height 67px <= 100px (size=934x67)
- `assets/llm-apps-ops-101/03/03-01-big-picture.en.png:1` — PNG height 88px <= 100px (size=1049x88)
- `assets/llm-apps-ops-101/03/03-01-big-picture.ko.png:1` — PNG height 67px <= 100px (size=938x67)
- `assets/llm-apps-ops-101/05/05-03-what-to-notice-in-this-code.en.png:1` — PNG height 87px <= 100px (size=1087x87)
- ... 7 more

## api-design-101 — Total 10

- BadImg=10 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/api-design-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 68px <= 100px (size=606x68)
- `assets/api-design-101/01/01-01-concept-at-a-glance.ko.png:1` — PNG height 68px <= 100px (size=606x68)
- `assets/api-design-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 82px <= 100px (size=501x82)
- `assets/api-design-101/02/02-01-concept-at-a-glance.ko.png:1` — PNG height 82px <= 100px (size=501x82)
- `assets/api-design-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=731x67)
- ... 5 more

## azure-aks-deep-dive — Total 10

- BadImg=10 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/azure-aks-deep-dive/02/02-02-kubelet-talks-to-a-unix-socket.en.png:1` — PNG height 67px <= 100px (size=1158x67)
- `assets/azure-aks-deep-dive/02/02-02-kubelet-talks-to-a-unix-socket.ko.png:1` — PNG height 67px <= 100px (size=1158x67)
- `assets/azure-aks-deep-dive/04/04-02-filter-and-score.en.png:1` — PNG height 67px <= 100px (size=1241x67)
- `assets/azure-aks-deep-dive/04/04-02-filter-and-score.ko.png:1` — PNG height 67px <= 100px (size=1241x67)
- `assets/azure-aks-deep-dive/05/05-01-put-both-loops-in-one-diagram.en.png:1` — PNG height 65px <= 100px (size=1384x65)
- ... 5 more

## clean-code-101 — Total 10

- BadImg=10 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/clean-code-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=638x67)
- `assets/clean-code-101/01/01-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=638x67)
- `assets/clean-code-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=921x67)
- `assets/clean-code-101/03/03-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=921x67)
- `assets/clean-code-101/04/04-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=884x67)
- ... 5 more

## containers-101 — Total 10

- BadImg=10 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/containers-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=737x67)
- `assets/containers-101/02/02-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=737x67)
- `assets/containers-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=802x67)
- `assets/containers-101/03/03-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=802x67)
- `assets/containers-101/04/04-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=714x67)
- ... 5 more

## github-actions-101 — Total 10

- BadImg=10 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/github-actions-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=816x67)
- `assets/github-actions-101/01/01-01-diagram.ko.png:1` — PNG height 67px <= 100px (size=816x67)
- `assets/github-actions-101/04/04-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=817x67)
- `assets/github-actions-101/04/04-01-diagram.ko.png:1` — PNG height 67px <= 100px (size=817x67)
- `assets/github-actions-101/06/06-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=949x67)
- ... 5 more

## linear-algebra-101 — Total 10

- BadImg=10 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/linear-algebra-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=794x67)
- `assets/linear-algebra-101/01/01-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=794x67)
- `assets/linear-algebra-101/05/05-01-concept-at-a-glance.en.png:1` — PNG height 88px <= 100px (size=731x88)
- `assets/linear-algebra-101/05/05-01-concept-at-a-glance.ko.png:1` — PNG height 88px <= 100px (size=731x88)
- `assets/linear-algebra-101/06/06-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=944x67)
- ... 5 more

## llm-api-production-101 — Total 10

- BadImg=10 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/llm-api-production-101/01/01-01-structured-output-json-mode-and-response.en.png:1` — PNG height 67px <= 100px (size=1227x67)
- `assets/llm-api-production-101/01/01-01-structured-output-json-mode-and-response.ko.png:1` — PNG height 67px <= 100px (size=1064x67)
- `assets/llm-api-production-101/02/02-01-tool-calling-connecting-functions-to-the.en.png:1` — PNG height 67px <= 100px (size=1291x67)
- `assets/llm-api-production-101/02/02-01-tool-calling-connecting-functions-to-the.ko.png:1` — PNG height 67px <= 100px (size=1181x67)
- `assets/llm-api-production-101/02/02-04-building-the-full-function-execution-loo.en.png:1` — PNG height 34px <= 100px (size=1384x34)
- ... 5 more

## pandas-101 — Total 10

- BadImg=10 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/pandas-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=831x67)
- `assets/pandas-101/01/01-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=831x67)
- `assets/pandas-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=943x67)
- `assets/pandas-101/03/03-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=943x67)
- `assets/pandas-101/06/06-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=863x67)
- ... 5 more

## python-package-101 — Total 10

- BadImg=10 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/python-package-101/01/01-01-mental-model.en.png:1` — PNG height 88px <= 100px (size=843x88)
- `assets/python-package-101/01/01-01-mental-model.ko.png:1` — PNG height 88px <= 100px (size=825x88)
- `assets/python-package-101/05/05-01-mental-model.en.png:1` — PNG height 67px <= 100px (size=1307x67)
- `assets/python-package-101/05/05-01-mental-model.ko.png:1` — PNG height 67px <= 100px (size=1245x67)
- `assets/python-package-101/06/06-01-mental-model.en.png:1` — PNG height 67px <= 100px (size=1317x67)
- ... 5 more

## secure-coding-101 — Total 10

- BadImg=10 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/secure-coding-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=898x67)
- `assets/secure-coding-101/02/02-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=898x67)
- `assets/secure-coding-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=1092x67)
- `assets/secure-coding-101/03/03-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=1092x67)
- `assets/secure-coding-101/04/04-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=920x67)
- ... 5 more

## computer-networks-101 — Total 8

- BadImg=8 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/computer-networks-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 78px <= 100px (size=1384x78)
- `assets/computer-networks-101/01/01-01-concept-at-a-glance.ko.png:1` — PNG height 87px <= 100px (size=1384x87)
- `assets/computer-networks-101/05/05-01-concept-at-a-glance.en.png:1` — PNG height 81px <= 100px (size=1384x81)
- `assets/computer-networks-101/05/05-01-concept-at-a-glance.ko.png:1` — PNG height 88px <= 100px (size=1359x88)
- `assets/computer-networks-101/06/06-01-concept-at-a-glance.en.png:1` — PNG height 83px <= 100px (size=1384x83)
- ... 3 more

## devops-101 — Total 8

- BadImg=8 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/devops-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=922x67)
- `assets/devops-101/02/02-01-diagram.ko.png:1` — PNG height 67px <= 100px (size=922x67)
- `assets/devops-101/06/06-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=967x67)
- `assets/devops-101/06/06-01-diagram.ko.png:1` — PNG height 67px <= 100px (size=967x67)
- `assets/devops-101/08/08-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=884x67)
- ... 3 more

## frontend-development-101 — Total 8

- BadImg=8 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/frontend-development-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=922x67)
- `assets/frontend-development-101/02/02-01-diagram.ko.png:1` — PNG height 67px <= 100px (size=922x67)
- `assets/frontend-development-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=853x67)
- `assets/frontend-development-101/03/03-01-diagram.ko.png:1` — PNG height 67px <= 100px (size=853x67)
- `assets/frontend-development-101/05/05-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=708x67)
- ... 3 more

## kubernetes-101 — Total 8

- BadImg=8 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/kubernetes-101/07/07-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=592x67)
- `assets/kubernetes-101/07/07-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=592x67)
- `assets/kubernetes-101/08/08-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=634x67)
- `assets/kubernetes-101/08/08-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=634x67)
- `assets/kubernetes-101/09/09-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=807x67)
- ... 3 more

## llm-from-scratch-101 — Total 8

- BadImg=8 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/llm-from-scratch-101/03/03-01-causal-mask-no-peeking-at-the-future.en.png:1` — PNG height 88px <= 100px (size=984x88)
- `assets/llm-from-scratch-101/03/03-01-causal-mask.ko.png:1` — PNG height 88px <= 100px (size=984x88)
- `assets/llm-from-scratch-101/04/04-01-layernorm-pre-norm-vs-post-norm.en.png:1` — PNG height 95px <= 100px (size=1384x95)
- `assets/llm-from-scratch-101/04/04-01-layernorm-pre-norm-vs-post-norm.ko.png:1` — PNG height 95px <= 100px (size=1384x95)
- `assets/llm-from-scratch-101/06/06-01-the-5-line-core-of-the-training-loop.en.png:1` — PNG height 67px <= 100px (size=877x67)
- ... 3 more

## probability-101 — Total 8

- BadImg=8 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/probability-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=942x67)
- `assets/probability-101/03/03-01-diagram.ko.png:1` — PNG height 67px <= 100px (size=883x67)
- `assets/probability-101/04/04-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=811x67)
- `assets/probability-101/04/04-01-diagram.ko.png:1` — PNG height 67px <= 100px (size=811x67)
- `assets/probability-101/06/06-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=800x67)
- ... 3 more

## rag-benchmark-101 — Total 8

- BadImg=8 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/rag-benchmark-101/02/02-03-high-hit-rate-with-weak-ranking.en.png:1` — PNG height 88px <= 100px (size=907x88)
- `assets/rag-benchmark-101/02/02-03-high-hit-rate-with-weak-ranking.ko.png:1` — PNG height 67px <= 100px (size=781x67)
- `assets/rag-benchmark-101/04/04-02-boundary-between-embedding-and-search-ti.en.png:1` — PNG height 67px <= 100px (size=935x67)
- `assets/rag-benchmark-101/04/04-02-boundary-between-embedding-and-search-ti.ko.png:1` — PNG height 67px <= 100px (size=796x67)
- `assets/rag-benchmark-101/05/05-04-verification-flow-before-metric-executio.en.png:1` — PNG height 67px <= 100px (size=862x67)
- ... 3 more

## serverless-101 — Total 8

- BadImg=8 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/serverless-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=759x67)
- `assets/serverless-101/01/01-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=759x67)
- `assets/serverless-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=881x67)
- `assets/serverless-101/02/02-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=881x67)
- `assets/serverless-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=700x67)
- ... 3 more

## software-design-101 — Total 8

- BadImg=8 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/software-design-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=722x67)
- `assets/software-design-101/03/03-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=722x67)
- `assets/software-design-101/07/07-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=721x67)
- `assets/software-design-101/07/07-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=721x67)
- `assets/software-design-101/08/08-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=811x67)
- ... 3 more

## sql-101 — Total 8

- BadImg=8 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/sql-101/02/02-01-select-evaluation-flow.en.png:1` — PNG height 67px <= 100px (size=1231x67)
- `assets/sql-101/02/02-01-select-evaluation-flow.ko.png:1` — PNG height 67px <= 100px (size=1231x67)
- `assets/sql-101/05/05-01-aggregation-flow.en.png:1` — PNG height 67px <= 100px (size=1021x67)
- `assets/sql-101/05/05-01-aggregation-flow.ko.png:1` — PNG height 67px <= 100px (size=1021x67)
- `assets/sql-101/07/07-01-window-calculation-flow.en.png:1` — PNG height 88px <= 100px (size=1026x88)
- ... 3 more

## sre-101 — Total 8

- BadImg=8 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/sre-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=577x67)
- `assets/sre-101/03/03-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=577x67)
- `assets/sre-101/06/06-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=773x67)
- `assets/sre-101/06/06-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=773x67)
- `assets/sre-101/07/07-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=781x67)
- ... 3 more

## cloud-computing-101 — Total 6

- BadImg=6 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/cloud-computing-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=666x67)
- `assets/cloud-computing-101/02/02-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=666x67)
- `assets/cloud-computing-101/04/04-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=763x67)
- `assets/cloud-computing-101/04/04-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=763x67)
- `assets/cloud-computing-101/06/06-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=893x67)
- ... 1 more

## machine-learning-101 — Total 6

- BadImg=6 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/machine-learning-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=750x67)
- `assets/machine-learning-101/01/01-01-diagram.ko.png:1` — PNG height 67px <= 100px (size=740x67)
- `assets/machine-learning-101/04/04-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=748x67)
- `assets/machine-learning-101/04/04-01-diagram.ko.png:1` — PNG height 67px <= 100px (size=694x67)
- `assets/machine-learning-101/05/05-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=815x67)
- ... 1 more

## mlops-101 — Total 6

- BadImg=6 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/mlops-101/04/04-01-see-the-flow-first.en.png:1` — PNG height 67px <= 100px (size=915x67)
- `assets/mlops-101/04/04-01-see-the-flow-first.ko.png:1` — PNG height 67px <= 100px (size=915x67)
- `assets/mlops-101/05/05-01-see-the-flow-first.en.png:1` — PNG height 67px <= 100px (size=1028x67)
- `assets/mlops-101/05/05-01-see-the-flow-first.ko.png:1` — PNG height 67px <= 100px (size=1028x67)
- `assets/mlops-101/08/08-01-see-the-flow-first.en.png:1` — PNG height 67px <= 100px (size=898x67)
- ... 1 more

## observability-101 — Total 6

- BadImg=6 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/observability-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=761x67)
- `assets/observability-101/03/03-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=781x67)
- `assets/observability-101/04/04-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=981x67)
- `assets/observability-101/04/04-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=799x67)
- `assets/observability-101/08/08-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=1060x67)
- ... 1 more

## azure-functions-deep-dive — Total 5

- BadImg=5 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/azure-functions-deep-dive/02/02-01-one-level-up-workerconfigfactory.ko.png:1` — PNG height 74px <= 100px (size=1384x74)
- `assets/azure-functions-deep-dive/03/03-02-the-channel-layout-closer-to-per-worker.en.png:1` — PNG height 96px <= 100px (size=1384x96)
- `assets/azure-functions-deep-dive/03/03-02-the-channel-layout-closer-to-per-worker.ko.png:1` — PNG height 96px <= 100px (size=1384x96)
- `assets/azure-functions-deep-dive/06/06-01-why-cold-start-is-expensive-decomposing.en.png:1` — PNG height 52px <= 100px (size=1384x52)
- `assets/azure-functions-deep-dive/06/06-01-why-cold-start-is-expensive-decomposing.ko.png:1` — PNG height 55px <= 100px (size=1384x55)

## git-github-101 — Total 5

- BadImg=5 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/git-github-101/01/01-01-mental-model.en.png:1` — PNG height 88px <= 100px (size=1087x88)
- `assets/git-github-101/01/01-01-mental-model.ko.png:1` — PNG height 88px <= 100px (size=1080x88)
- `assets/git-github-101/06/06-01-mental-model.en.png:1` — PNG height 88px <= 100px (size=828x88)
- `assets/git-github-101/06/06-01-mental-model.ko.png:1` — PNG height 88px <= 100px (size=735x88)
- `assets/git-github-101/10/10-01-mental-model.ko.png:1` — PNG height 75px <= 100px (size=1384x75)

## alembic-101 — Total 4

- BadImg=4 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/alembic-101/01/01-01-diagram-how-revision-history-reaches-the.en.png:1` — PNG height 80px <= 100px (size=1384x80)
- `assets/alembic-101/01/01-01-diagram-how-revision-history-reaches-the.ko.png:1` — PNG height 67px <= 100px (size=1335x67)
- `assets/alembic-101/09/09-01-diagram-the-blue-green-compatibility-win.en.png:1` — PNG height 88px <= 100px (size=1237x88)
- `assets/alembic-101/09/09-01-diagram-the-blue-green-compatibility-win.ko.png:1` — PNG height 67px <= 100px (size=1181x67)

## azure-aca-101 — Total 4

- BadImg=4 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/azure-aca-101/03/03-01-the-end-to-end-path.en.png:1` — PNG height 67px <= 100px (size=1097x67)
- `assets/azure-aca-101/03/03-01-the-end-to-end-path.ko.png:1` — PNG height 67px <= 100px (size=1097x67)
- `assets/azure-aca-101/05/05-01-the-scaling-path.en.png:1` — PNG height 67px <= 100px (size=945x67)
- `assets/azure-aca-101/05/05-01-the-scaling-path.ko.png:1` — PNG height 67px <= 100px (size=945x67)

## backend-development-101 — Total 4

- BadImg=4 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/backend-development-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=794x67)
- `assets/backend-development-101/03/03-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=794x67)
- `assets/backend-development-101/09/09-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=1148x67)
- `assets/backend-development-101/09/09-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=1148x67)

## calculus-for-ml-101 — Total 4

- BadImg=4 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/calculus-for-ml-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=780x67)
- `assets/calculus-for-ml-101/01/01-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=673x67)
- `assets/calculus-for-ml-101/05/05-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=612x67)
- `assets/calculus-for-ml-101/05/05-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=612x67)

## data-warehouse-101 — Total 4

- BadImg=4 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/data-warehouse-101/06/06-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=840x67)
- `assets/data-warehouse-101/06/06-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=840x67)
- `assets/data-warehouse-101/07/07-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=899x67)
- `assets/data-warehouse-101/07/07-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=899x67)

## design-patterns-101 — Total 4

- BadImg=4 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/design-patterns-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=725x67)
- `assets/design-patterns-101/01/01-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=725x67)
- `assets/design-patterns-101/06/06-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=750x67)
- `assets/design-patterns-101/06/06-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=750x67)

## functional-programming-101 — Total 4

- BadImg=4 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/functional-programming-101/08/08-01-lazy-pipeline-pull-model.en.png:1` — PNG height 68px <= 100px (size=1054x68)
- `assets/functional-programming-101/08/08-01-lazy-pipeline-pull-model.ko.png:1` — PNG height 68px <= 100px (size=858x68)
- `assets/functional-programming-101/09/09-01-how-a-readable-pipeline-flows.en.png:1` — PNG height 67px <= 100px (size=1014x67)
- `assets/functional-programming-101/09/09-01-how-a-readable-pipeline-flows.ko.png:1` — PNG height 67px <= 100px (size=864x67)

## programming-languages-101 — Total 4

- BadImg=4 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/programming-languages-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=1042x67)
- `assets/programming-languages-101/01/01-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=1042x67)
- `assets/programming-languages-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=1140x67)
- `assets/programming-languages-101/02/02-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=1140x67)

## multimodal-ai-101 — Total 3

- BadImg=3 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/multimodal-ai-101/01/01-01-mental-model-multimodal-expands-the-reas.en.png:1` — PNG height 88px <= 100px (size=1355x88)
- `assets/multimodal-ai-101/01/01-01-mental-model-multimodal-expands-the-reas.ko.png:1` — PNG height 88px <= 100px (size=1138x88)
- `assets/multimodal-ai-101/02/02-01-mental-model-encode-first-decide-later.en.png:1` — PNG height 88px <= 100px (size=1325x88)

## ai-agent-101 — Total 2

- BadImg=2 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/ai-agent-101/09/09-01-observability.en.png:1` — PNG height 88px <= 100px (size=1266x88)
- `assets/ai-agent-101/09/09-01-observability.ko.png:1` — PNG height 67px <= 100px (size=1194x67)

## azure-aks-101 — Total 2

- BadImg=2 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/azure-aks-101/03/03-01-today-s-flow.en.png:1` — PNG height 67px <= 100px (size=1384x67)
- `assets/azure-aks-101/03/03-01-today-s-flow.ko.png:1` — PNG height 67px <= 100px (size=1384x67)

## azure-functions-101 — Total 2

- BadImg=2 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/azure-functions-101/06/06-03-what-a-cold-start-actually-includes.en.png:1` — PNG height 86px <= 100px (size=1384x86)
- `assets/azure-functions-101/06/06-03-what-a-cold-start-actually-includes.ko.png:1` — PNG height 67px <= 100px (size=1277x67)

## operating-systems-101 — Total 2

- BadImg=2 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/operating-systems-101/08/08-01-the-path-from-write-to-durable-storage.en.png:1` — PNG height 67px <= 100px (size=979x67)
- `assets/operating-systems-101/08/08-01-the-path-from-write-to-durable-storage.ko.png:1` — PNG height 67px <= 100px (size=1019x67)
