# Cross-Series Quality Audit

Generated: 2026-05-20T11:55:24+00:00

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
- Series with any issue: **24**
- Series at or above 5 issues: **17**
- Total issues: **190**
  - BadImg: **190**
  - Synt: **0**
  - BrkLink: **0**
  - Shrt: **0**
  - NoEn: **0**
- Repo existence check method: **gh**

## Ranked series

| Rank | Series | Total | BadImg | Synt | BrkLink | Shrt | NoEn |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `open-source-101` | 16 | 16 | 0 | 0 | 0 | 0 |
| 2 | `testing-101` | 14 | 14 | 0 | 0 | 0 | 0 |
| 3 | `data-science-101` | 12 | 12 | 0 | 0 | 0 | 0 |
| 4 | `docker-101` | 12 | 12 | 0 | 0 | 0 | 0 |
| 5 | `llm-apps-ops-101` | 12 | 12 | 0 | 0 | 0 | 0 |
| 6 | `api-design-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 7 | `containers-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 8 | `pandas-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 9 | `python-package-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 10 | `secure-coding-101` | 10 | 10 | 0 | 0 | 0 | 0 |
| 11 | `devops-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 12 | `kubernetes-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 13 | `llm-from-scratch-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 14 | `rag-benchmark-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 15 | `software-design-101` | 8 | 8 | 0 | 0 | 0 | 0 |
| 16 | `mlops-101` | 6 | 6 | 0 | 0 | 0 | 0 |
| 17 | `observability-101` | 6 | 6 | 0 | 0 | 0 | 0 |
| 18 | `azure-aca-101` | 4 | 4 | 0 | 0 | 0 | 0 |
| 19 | `backend-development-101` | 4 | 4 | 0 | 0 | 0 | 0 |
| 20 | `design-patterns-101` | 4 | 4 | 0 | 0 | 0 | 0 |
| 21 | `programming-languages-101` | 4 | 4 | 0 | 0 | 0 | 0 |
| 22 | `azure-aks-101` | 2 | 2 | 0 | 0 | 0 | 0 |
| 23 | `azure-functions-101` | 2 | 2 | 0 | 0 | 0 | 0 |
| 24 | `operating-systems-101` | 2 | 2 | 0 | 0 | 0 | 0 |

## open-source-101 — Total 16

- BadImg=16 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/open-source-101/01/01-01-a-concept-map-you-can-keep-in-your-head.en.png:1` — PNG height 67px <= 100px (size=625x67)
- `assets/open-source-101/01/01-01-a-concept-map-you-can-keep-in-your-head.ko.png:1` — PNG height 67px <= 100px (size=588x67)
- `assets/open-source-101/03/03-01-fix-the-reading-order-first.en.png:1` — PNG height 67px <= 100px (size=728x67)
- `assets/open-source-101/03/03-01-fix-the-reading-order-first.ko.png:1` — PNG height 67px <= 100px (size=666x67)
- `assets/open-source-101/04/04-01-put-the-flow-in-your-head-first.en.png:1` — PNG height 67px <= 100px (size=885x67)
- ... 11 more

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

## containers-101 — Total 10

- BadImg=10 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/containers-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=737x67)
- `assets/containers-101/02/02-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=737x67)
- `assets/containers-101/03/03-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=802x67)
- `assets/containers-101/03/03-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=802x67)
- `assets/containers-101/04/04-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=714x67)
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

## devops-101 — Total 8

- BadImg=8 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/devops-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=922x67)
- `assets/devops-101/02/02-01-diagram.ko.png:1` — PNG height 67px <= 100px (size=922x67)
- `assets/devops-101/06/06-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=967x67)
- `assets/devops-101/06/06-01-diagram.ko.png:1` — PNG height 67px <= 100px (size=967x67)
- `assets/devops-101/08/08-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=884x67)
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

## rag-benchmark-101 — Total 8

- BadImg=8 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/rag-benchmark-101/02/02-03-high-hit-rate-with-weak-ranking.en.png:1` — PNG height 88px <= 100px (size=907x88)
- `assets/rag-benchmark-101/02/02-03-high-hit-rate-with-weak-ranking.ko.png:1` — PNG height 67px <= 100px (size=781x67)
- `assets/rag-benchmark-101/04/04-02-boundary-between-embedding-and-search-ti.en.png:1` — PNG height 67px <= 100px (size=935x67)
- `assets/rag-benchmark-101/04/04-02-boundary-between-embedding-and-search-ti.ko.png:1` — PNG height 67px <= 100px (size=796x67)
- `assets/rag-benchmark-101/05/05-04-verification-flow-before-metric-executio.en.png:1` — PNG height 67px <= 100px (size=862x67)
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

## design-patterns-101 — Total 4

- BadImg=4 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/design-patterns-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=725x67)
- `assets/design-patterns-101/01/01-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=725x67)
- `assets/design-patterns-101/06/06-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=750x67)
- `assets/design-patterns-101/06/06-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=750x67)

## programming-languages-101 — Total 4

- BadImg=4 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/programming-languages-101/01/01-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=1042x67)
- `assets/programming-languages-101/01/01-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=1042x67)
- `assets/programming-languages-101/02/02-01-concept-at-a-glance.en.png:1` — PNG height 67px <= 100px (size=1140x67)
- `assets/programming-languages-101/02/02-01-concept-at-a-glance.ko.png:1` — PNG height 67px <= 100px (size=1140x67)

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
