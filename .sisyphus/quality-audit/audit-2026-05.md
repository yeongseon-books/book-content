# Cross-Series Quality Audit

Generated: 2026-05-23T23:04:41+00:00

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
- Series with any issue: **16**
- Series at or above 5 issues: **0**
- Total issues: **28**
  - BadImg: **0**
  - Synt: **27**
  - BrkLink: **0**
  - Shrt: **1**
  - NoEn: **0**
- Repo existence check method: **gh**

## Ranked series

| Rank | Series | Total | BadImg | Synt | BrkLink | Shrt | NoEn |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `llm-finetuning-101` | 4 | 0 | 4 | 0 | 0 | 0 |
| 2 | `multimodal-ai-101` | 4 | 0 | 4 | 0 | 0 | 0 |
| 3 | `python-101` | 3 | 0 | 3 | 0 | 0 | 0 |
| 4 | `ai-app-patterns-101` | 2 | 0 | 2 | 0 | 0 | 0 |
| 5 | `document-ingestion-101` | 2 | 0 | 2 | 0 | 0 | 0 |
| 6 | `linear-algebra-101` | 2 | 0 | 2 | 0 | 0 | 0 |
| 7 | `testing-101` | 2 | 0 | 2 | 0 | 0 | 0 |
| 8 | `ai-agent-101` | 1 | 0 | 1 | 0 | 0 | 0 |
| 9 | `ai-safety-guardrails-101` | 1 | 0 | 1 | 0 | 0 | 0 |
| 10 | `api-design-101` | 1 | 0 | 1 | 0 | 0 | 0 |
| 11 | `backend-development-101` | 1 | 0 | 1 | 0 | 0 | 0 |
| 12 | `devops-101` | 1 | 0 | 1 | 0 | 0 | 0 |
| 13 | `incident-response-101` | 1 | 0 | 1 | 0 | 0 | 0 |
| 14 | `mlops-101` | 1 | 0 | 1 | 0 | 0 | 0 |
| 15 | `pandas-101` | 1 | 0 | 1 | 0 | 0 | 0 |
| 16 | `model-evaluation-101` | 1 | 0 | 0 | 0 | 1 | 0 |

## llm-finetuning-101 — Total 4

- BadImg=0 Synt=4 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/llm-finetuning-101/ko/02-dataset.md:349` — unterminated string literal (detected at line 14) (code=`from dataclasses import dataclass`)
- `content/llm-finetuning-101/ko/03-lora.md:318` — unterminated string literal (detected at line 14) (code=`from dataclasses import dataclass`)
- `content/llm-finetuning-101/ko/05-evaluation.md:331` — unterminated string literal (detected at line 14) (code=`from dataclasses import dataclass`)
- `content/llm-finetuning-101/ko/06-serving.md:343` — unterminated string literal (detected at line 14) (code=`from dataclasses import dataclass`)

## multimodal-ai-101 — Total 4

- BadImg=0 Synt=4 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/multimodal-ai-101/ko/02-image-encoders-clip-vit.md:273` — unterminated string literal (detected at line 17) (code=`from openai import OpenAI`)
- `content/multimodal-ai-101/ko/04-captioning-ocr-pipelines.md:314` — unterminated string literal (detected at line 5) (code=`def build_validation_prompt(caption: str, ocr_text: str) -> str:`)
- `content/multimodal-ai-101/ko/10-production-multimodal-app.md:270` — unterminated string literal (detected at line 12) (code=`class StepFailure(Exception):`)
- `content/multimodal-ai-101/ko/10-production-multimodal-app.md:314` — unterminated string literal (detected at line 2) (code=`ALLOWED_MAGIC = {`)

## python-101 — Total 3

- BadImg=0 Synt=3 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/python-101/ko/03-strings-and-formatting.md:456` — unterminated string literal (detected at line 7) (code=`import pdb`)
- `content/python-101/ko/05-control-flow.md:421` — unterminated string literal (detected at line 3) (code=`import timeit`)
- `content/python-101/ko/08-file-io-and-exceptions.md:335` — unterminated string literal (detected at line 5) (code=`from pathlib import Path`)

## ai-app-patterns-101 — Total 2

- BadImg=0 Synt=2 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/ai-app-patterns-101/ko/01-chatbot-pattern.md:356` — unterminated f-string literal (detected at line 27) (code=`from fastapi import FastAPI, HTTPException`)
- `content/ai-app-patterns-101/ko/02-rag-qa-pattern.md:431` — unterminated string literal (detected at line 17) (code=`from fastapi import FastAPI`)

## document-ingestion-101 — Total 2

- BadImg=0 Synt=2 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/document-ingestion-101/ko/02-chunking-strategies.md:226` — unterminated string literal (detected at line 13) (code=`from __future__ import annotations`)
- `content/document-ingestion-101/ko/05-multi-format-pipeline.md:405` — unterminated string literal (detected at line 10) (code=`from __future__ import annotations`)

## linear-algebra-101 — Total 2

- BadImg=0 Synt=2 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/linear-algebra-101/ko/05-linear-transformation.md:278` — unterminated string literal (detected at line 17) (code=`import numpy as np`)
- `content/linear-algebra-101/ko/05-linear-transformation.md:517` — unterminated string literal (detected at line 11) (code=`import numpy as np`)

## testing-101 — Total 2

- BadImg=0 Synt=2 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/testing-101/ko/04-e2e-test.md:106` — unmatched ')' (code=`# tests/e2e/test_user_flow.py`)
- `content/testing-101/ko/05-test-double.md:282` — positional argument follows keyword argument (code=`def test_order_creation():`)

## ai-agent-101 — Total 1

- BadImg=0 Synt=1 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/ai-agent-101/ko/02-context-engineering.md:276` — unterminated string literal (detected at line 5) (code=`from langchain_core.prompts import ChatPromptTemplate`)

## ai-safety-guardrails-101 — Total 1

- BadImg=0 Synt=1 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/ai-safety-guardrails-101/ko/05-jailbreak-detection.md:285` — unterminated string literal (detected at line 2) (code=`def conversation_risk_score(history: list[str]) -> float:`)

## api-design-101 — Total 1

- BadImg=0 Synt=1 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/api-design-101/ko/02-rest-basics.md:68` — invalid syntax (code=`# Stateless: 매 요청에 인증 정보를 포함`)

## backend-development-101 — Total 1

- BadImg=0 Synt=1 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/backend-development-101/ko/02-building-an-http-server.md:198` — unterminated string literal (detected at line 13) (code=`# 학습용: 요청/응답 경계를 직접 확인`)

## devops-101 — Total 1

- BadImg=0 Synt=1 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/devops-101/ko/05-infrastructure-as-code.md:150` — invalid syntax (code=`# OPA 정책 예시(Rego)`)

## incident-response-101 — Total 1

- BadImg=0 Synt=1 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/incident-response-101/ko/10-incident-runbook.md:192` — unterminated triple-quoted string literal (detected at line 15) (code=`from jinja2 import Template`)

## mlops-101 — Total 1

- BadImg=0 Synt=1 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/mlops-101/ko/03-data-versioning.md:113` — positional argument follows keyword argument (code=`# 초기 버전`)

## pandas-101 — Total 1

- BadImg=0 Synt=1 BrkLink=0 Shrt=0 NoEn=0

### Synt
- `content/pandas-101/ko/01-what-is-pandas.md:66` — invalid syntax (code=`!pip install pandas`)

## model-evaluation-101 — Total 1

- BadImg=0 Synt=0 BrkLink=0 Shrt=1 NoEn=0

### Shrt
- `content/model-evaluation-101/ko/01-why-evaluation-is-hard.md:22` — markdown body has 149 lines (< 150)
