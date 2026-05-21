---
episode: 7

language: ko

last_reviewed: '2026-05-17'

series: ai-data-preparation-101

status: publish-ready

tags:
- Synthetic Data
- Self-Instruct
- Evol-Instruct
- Distillation
- GPT-4
- Alpaca
targets:

  ebook: true

  medium: false

  mkdocs: true

  tistory: true

title: "AI Data Preparation 101 (7/10): 합성 데이터 생성 — Self-Instruct부터 Distillation까지"

seo_description: labeled data가 부족할수록 합성 데이터 생성보다 배치 검증과 정책 게이트를 먼저 설계해야 합니다.
---

# AI Data Preparation 101 (7/10): 합성 데이터 생성 — Self-Instruct부터 Distillation까지

이 글은 AI Data Preparation 101 시리즈의 7번째 글입니다.

합성 데이터 생성은 데이터가 모자랄 때 샘플 수를 억지로 부풀리는 요령이 아니라, 좁은 도메인에서 부족한 감독 신호를 통제된 방식으로 확장하는 운영 절차입니다. 실전에서 중요한 질문은 “무엇을 생성할까?”보다 “어떤 배치를 어떤 기준으로 버리고, 어떤 배치만 데이터셋에 넣을까?”에 더 가깝습니다.

이번 글은 issue #779가 지적한 약점처럼 패턴 나열로 끝내지 않고, 하나의 재현 가능한 synthetic batch workflow로 07화를 다시 묶습니다. Self-Instruct, Evol-Instruct, RAG eval pair generation, distillation은 별도 미니 섹션이 아니라 같은 파이프라인 안에서 선택하는 분기입니다.

## 먼저 던지는 질문

- 도메인 파인튜닝용 synthetic batch는 어떤 입력에서 시작해 어떤 산출물로 끝나야 할까요?
- Self-Instruct, Evol-Instruct, RAG eval, distillation은 어느 시점에 선택해야 할까요?
- 생성된 JSON 산출물은 어떤 검증 게이트를 통과해야 실제 데이터셋에 편입할 수 있을까요?

## 큰 그림

![AI 데이터 준비 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/07/07-01-big-picture.ko.png)

*AI 데이터 준비 7장 흐름 개요*

이 그림에서는 합성 데이터 생성 — Self-Instruct부터 Distillation까지를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 합성 데이터 생성 — Self-Instruct부터 Distillation까지의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

합성 데이터는 사람 라벨링을 완전히 대체하지는 못해도, seed task가 적은 도메인에서 instruction tuning 데이터와 평가용 QA pair를 빠르게 늘리는 데 매우 유용합니다. 다만 verification 없이 생성만 반복하면 반복 패턴, 근거 없는 답변, teacher 편향, 정책 위반 리스크가 함께 쌓입니다.

그래서 운영 관점의 핵심은 단순합니다. 생성 패턴을 외우는 것보다, 입력 배치·생성 계약·샘플 검수·reject 사유·최종 write path까지 하나의 배치 흐름으로 보는 편이 훨씬 안전합니다.

> 합성 데이터의 성패는 모델이 몇 개의 샘플을 만들었는지가 아니라, 운영자가 어떤 배치를 버릴 수 있게 설계했는지에 달려 있습니다.

## 하나의 운영 시나리오로 이해하기

가정은 다음과 같습니다.

- 도메인: SaaS 고객지원 assistant 파인튜닝
- 현재 문제: 환불, 요금제 변경, 장애 공지 관련 instruction data가 부족함
- 이미 가진 것: 사람이 직접 검수한 seed task 40개, FAQ 문서 120개
- 목표: 이번 주 안에 synthetic batch 1개를 생성하고, 통과분만 학습용 JSONL로 저장

이 시나리오에서 실제 operator가 거치는 흐름은 아래와 같습니다.

1. seed task와 문서 chunk를 모읍니다.
2. 이번 배치의 목적을 정합니다.
3. 목적에 맞는 generation branch를 고릅니다.
4. JSON generation contract에 맞춰 샘플을 생성합니다.
5. schema, evidence, diversity, refusal, policy 게이트를 통과시킵니다.
6. reject 사유를 로그에 남기고, 통과분만 write path에 저장합니다.

## 먼저 branch를 고릅니다

같은 synthetic generation이라도 어떤 감독 신호를 늘리고 싶은지에 따라 선택이 달라집니다.

| 목적 | 선택 branch | 왜 이 branch인가 |
| --- | --- | --- |
| seed task가 너무 적고 주제 다양성이 부족함 | Self-Instruct | 새 instruction-input-output triple을 넓게 증식하기 좋습니다. |
| 기존 task는 있지만 난도가 낮음 | Evol-Instruct | 같은 라벨 공간 안에서 reasoning depth와 제약 조건을 키우기 좋습니다. |
| retrieval 평가셋이 부족함 | RAG eval pair generation | 문서 근거가 있는 질문-답변 쌍을 따로 만들 수 있습니다. |
| 강한 teacher의 응답 스타일을 student에 옮기고 싶음 | Distillation | output quality는 높지만 정책 검토를 먼저 해야 합니다. |

이번 시나리오에서는 고객지원 instruction tuning 데이터를 먼저 늘리고, FAQ 근거가 있는 일부 샘플을 함께 확보하고 싶다고 가정하겠습니다. 따라서 기본 branch는 Self-Instruct이고, 어려운 케이스는 Evol-Instruct로 보강하며, FAQ 기반 질문은 RAG eval branch로 따로 생성합니다. Distillation은 별도 정책 게이트를 통과한 뒤에만 켭니다.

## 재현 가능한 synthetic batch workflow

아래 예시는 seed task 입력, generation contract, validation, rejection, dataset write path를 하나로 묶은 최소 운영 골격입니다.

```python
from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import uuid

from openai import OpenAI

client = OpenAI()

SEED_TASKS = [
    {
        "task_id": "seed-001",
        "instruction": "고객이 환불 가능 기간을 물으면 정책 기준을 요약해 답하세요.",
        "input": "연간 플랜을 결제한 고객이 10일 뒤 환불 가능 여부를 묻습니다.",
        "output": "연간 플랜은 결제 후 14일 이내라면 환불 검토가 가능합니다.",
        "source_type": "self_instruct",
        "difficulty": "baseline",
        "evidence": None,
    },
    {
        "task_id": "seed-002",
        "instruction": "장애 공지 문서를 바탕으로 고객 질문에 답하세요.",
        "input": "2026-05-01 장애 공지 기준으로 API 지연 원인을 설명하세요.",
        "output": "당시 API 지연은 데이터베이스 connection pool 포화가 직접 원인이었습니다.",
        "source_type": "rag_eval",
        "difficulty": "baseline",
        "evidence": "원인: 데이터베이스 connection pool 포화",
    },
]

FAQ_CHUNKS = {
    "faq-014": "환불 정책: 연간 플랜은 결제 후 14일 이내 환불 검토가 가능하며, 이후에는 사용량을 기준으로 부분 환불 여부를 검토한다.",
    "faq-021": "장애 공지: 2026-05-01 10:42 UTC부터 API 지연이 발생했고, 데이터베이스 connection pool 포화가 원인이었다.",
}

GENERATION_CONTRACT = {
    "type": "object",
    "required": ["items"],
    "item_required": [
        "task_id",
        "instruction",
        "input",
        "output",
        "source_type",
        "difficulty",
        "reasons",
    ],
    "allowed_source_type": ["self_instruct", "evol_instruct", "rag_eval", "distillation"],
}

BRANCH_GUIDE = {
    "self_instruct": "Make a new task in the same domain but with a different customer situation.",
    "evol_instruct": "Take a baseline task and add one realistic constraint that forces deeper reasoning.",
    "rag_eval": "Generate only when the answer can be quoted from the supplied FAQ chunk.",
    "distillation": "Only use if a policy reviewer has approved output reuse for this teacher.",
}

def build_prompt(batch_goal: str, branch: str) -> str:
    return f"""
You are generating training data for a SaaS support assistant.
Batch goal: {batch_goal}
Branch guide: {BRANCH_GUIDE[branch]}

Return JSON with the shape:
{{
  "items": [
    {{
      "task_id": "syn-...",
      "instruction": "...",
      "input": "...",
      "output": "...",
      "source_type": "{branch}",
      "difficulty": "baseline|hard",
      "evidence": "required when source_type is rag_eval, otherwise null",
      "reasons": ["why this sample adds coverage"]
    }}
  ]
}}

Seed tasks:
{json.dumps(SEED_TASKS, ensure_ascii=False, indent=2)}

FAQ chunks:
{json.dumps(FAQ_CHUNKS, ensure_ascii=False, indent=2)}
"""

def generate_batch(batch_goal: str, branch: str, model: str = "gpt-4o-mini") -> list[dict]:
    rsp = client.chat.completions.create(
        model=model,
        temperature=0.7 if branch != "rag_eval" else 0.2,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": build_prompt(batch_goal, branch)}],
    )
    payload = json.loads(rsp.choices[0].message.content)
    return payload["items"]

def validate_item(item: dict) -> list[str]:
    reasons = []
    for key in GENERATION_CONTRACT["item_required"]:
        if key not in item:
            reasons.append(f"missing:{key}")
    if item.get("source_type") not in GENERATION_CONTRACT["allowed_source_type"]:
        reasons.append("invalid_source_type")
    if item.get("source_type") == "rag_eval":
        evidence = item.get("evidence")
        if not evidence:
            reasons.append("missing_evidence")
        elif not any(evidence in chunk for chunk in FAQ_CHUNKS.values()):
            reasons.append("evidence_not_found")
    if any(token in item.get("output", "").lower() for token in ["죄송하지만", "도와드릴 수 없습니다", "i cannot"]):
        reasons.append("refusal_like_output")
    if len(item.get("output", "")) < 30:
        reasons.append("too_short")
    return reasons

def validate_batch(items: list[dict]) -> tuple[list[dict], list[dict], dict]:
    accepted, rejected = [], []
    seen = Counter()

    for item in items:
        item_reasons = validate_item(item)
        dedup_key = (item.get("instruction"), item.get("input"))
        seen[dedup_key] += 1
        if seen[dedup_key] > 1:
            item_reasons.append("duplicate_instruction_input")

        if item_reasons:
            rejected.append({"item": item, "reasons": item_reasons})
        else:
            accepted.append(item)

    total = len(items) or 1
    metrics = {
        "n_total": len(items),
        "n_accepted": len(accepted),
        "n_rejected": len(rejected),
        "accept_ratio": len(accepted) / total,
        "unique_ratio": len(seen) / total,
        "refusal_ratio": sum("refusal_like_output" in r["reasons"] for r in rejected) / total,
    }
    return accepted, rejected, metrics

def write_dataset(accepted: list[dict], run_id: str) -> Path:
    out_dir = Path("datasets/ai-data-preparation-101/07-synthetic-data-generation") / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "accepted.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for row in accepted:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return out_path

run_id = f"support-batch-{uuid.uuid4().hex[:8]}"
items = generate_batch(batch_goal="Expand refund and outage support tasks", branch="self_instruct")
accepted, rejected, metrics = validate_batch(items)

if metrics["accept_ratio"] < 0.8 or metrics["unique_ratio"] < 0.85 or metrics["refusal_ratio"] > 0.05:
    raise RuntimeError({"run_id": run_id, "status": "reject_batch", "metrics": metrics, "rejected": rejected[:3]})

dataset_path = write_dataset(accepted, run_id)
print({"run_id": run_id, "status": "accepted", "dataset_path": str(dataset_path), "metrics": metrics})
```

### 샘플 산출물은 이렇게 생겨야 합니다

생성 결과는 검증 가능한 JSON artifact여야 합니다. operator가 눈으로 확인할 수 있는 최소 예시는 아래처럼 생깁니다.

```json
{
  "items": [
    {
      "task_id": "syn-101",
      "instruction": "고객이 월간 플랜에서 연간 플랜으로 전환할 때 환불과 재청구 순서를 설명하세요.",
      "input": "고객은 월간 플랜 결제 후 3일째이며 연간 플랜 할인도 적용받고 싶어 합니다.",
      "output": "먼저 현재 월간 플랜 환불 가능 여부를 확인한 뒤, 연간 플랜을 별도로 재청구하는 순서를 안내해야 합니다.",
      "source_type": "self_instruct",
      "difficulty": "baseline",
      "evidence": null,
      "reasons": ["환불과 업그레이드가 동시에 등장하는 희귀 케이스를 추가합니다."]
    },
    {
      "task_id": "syn-102",
      "instruction": "장애 공지 문서만 근거로 API 지연 원인을 설명하세요.",
      "input": "2026-05-01 장애 당시 지연 원인을 요약해 달라는 문의입니다.",
      "output": "공개된 장애 공지에 따르면 데이터베이스 connection pool 포화가 직접 원인이었습니다.",
      "source_type": "rag_eval",
      "difficulty": "hard",
      "evidence": "데이터베이스 connection pool 포화가 원인이었다.",
      "reasons": ["FAQ 근거를 직접 요구하는 retrieval 평가 샘플입니다."]
    }
  ]
}
```

여기서 중요한 점은 JSON이 예쁘게 생겼다는 사실이 아니라, 각 항목에 reject 가능한 근거가 들어 있다는 점입니다. `source_type`, `difficulty`, `evidence`, `reasons`가 없으면 operator는 배치 실패 원인을 추적하기 어렵습니다.

## reject logic을 먼저 설계해야 합니다

실무에서는 “잘 생성된 샘플”보다 “왜 버렸는지 설명할 수 있는 샘플”이 더 중요합니다. 위 코드에서 실제로 reject하는 대표 상황은 다음과 같습니다.

- **schema 누락**: `instruction`, `output`, `source_type` 같은 필수 키가 빠짐
- **evidence 실패**: `rag_eval`인데 근거 문장이 FAQ chunk 어디에도 없음
- **refusal 증가**: 과도한 안전 거절 문구가 들어가 downstream dataset에 도움이 안 됨
- **중복 증가**: instruction-input 쌍이 사실상 같은데 표현만 살짝 다름
- **짧은 출력**: 분량이 너무 짧아 supervision 가치가 없음

운영에서는 이 reject 사유가 로그와 함께 남아야 다음 배치에서 프롬프트를 고칠 수 있습니다. acceptance 기준만 있고 rejection 로그가 없으면 배치가 왜 실패했는지 설명할 수 없습니다.

## 네 가지 pattern은 같은 workflow 안의 선택지입니다

### Self-Instruct: coverage를 넓히는 기본 branch

새로운 고객 상황을 넓게 늘리고 싶다면 Self-Instruct가 기본값입니다. 다만 temperature만 높여 놓고 계속 돌리면 표면만 다른 near-duplicate가 쉽게 늘어납니다. 그래서 seed task가 적을수록 diversity threshold와 dedup gate를 더 엄격하게 두는 편이 안전합니다.

### Evol-Instruct: 난도를 올리는 보강 branch

기본 질문은 충분하지만 reasoning depth가 약할 때는 기존 seed를 진화시키는 편이 낫습니다. 예를 들어 “환불 가능 여부를 답하라”를 “환불 가능 여부를 답하되, 이미 부분 환불 이력이 있을 때 예외 조건까지 설명하라”로 바꾸면 같은 라벨 공간 안에서 더 어려운 supervision을 만들 수 있습니다.

### RAG eval pair generation: 근거 검증이 가능한 branch

FAQ나 정책 문서가 있고, retrieval 품질을 따로 보고 싶다면 `source_type="rag_eval"`로 분리하는 편이 좋습니다. 이 branch는 자연스러운 문장보다 **근거 일치성**이 더 중요하므로 temperature를 낮추고 evidence 검증을 필수로 둡니다.

### Distillation: 품질 게이트와 별도로 정책 게이트가 필요한 branch

teacher의 응답 스타일을 student에 옮기고 싶을 때 distillation은 매우 강력합니다. 하지만 이 branch는 품질 검증만으로는 충분하지 않습니다. **배치 생성 전에 output-usage policy review를 통과했는지**를 확인해야 합니다.

운영에서는 아래처럼 명시적으로 멈추는 편이 안전합니다.

```python
def require_policy_review(branch: str, teacher_name: str, review_ticket: str | None) -> None:
    if branch != "distillation":
        return
    if not review_ticket:
        raise RuntimeError(
            f"Stop: review output-usage rights for {teacher_name} before creating a distillation dataset."
        )

require_policy_review(
    branch="distillation",
    teacher_name="OpenAI API model",
    review_ticket=None,  # must be populated by legal/policy review
)
```

중요한 점은 특정 provider의 출력 사용 조건을 기억에 의존해 처리하지 않는 것입니다. 예를 들어 OpenAI 문서는 Output ownership과 Usage Policies를 별도로 안내하므로, distillation을 시작하기 전에 항상 최신 약관과 정책 문서를 다시 확인해야 합니다. 이 글의 실무 권고는 “무조건 가능하다/불가능하다”가 아니라, **provider별 output-use 조건을 문서로 검토한 뒤 진행하라**입니다.

## 배치 승인 기준은 수치로 닫아야 합니다

이번 workflow에서 최소 승인 기준을 아래처럼 둘 수 있습니다.

- `accept_ratio >= 0.80`
- `unique_ratio >= 0.85`
- `refusal_ratio <= 0.05`
- `rag_eval` 항목은 `evidence_not_found == 0`
- distillation은 `policy_review_ticket` 없으면 무조건 중단

이 기준은 보편적인 절대값이 아니라, “샘플이 많아 보이지만 실제로는 실패한 배치”를 빠르게 거르기 위한 운영 기준입니다. 예를 들어 `unique_ratio`가 0.62라면 더 생성할 문제가 아니라 프롬프트와 seed set을 다시 설계할 문제일 가능성이 큽니다.

## Dataset versioning과 DAG 관점으로 마무리하기

합성 배치를 운영에 올릴 때는 생성 코드보다 버전 관리와 의존성 그래프가 더 중요해집니다. 최소한 아래 DAG처럼 `seed -> generate -> validate -> approve -> publish` 단계가 분리되어야 배치 실패 원인을 즉시 좁힐 수 있습니다.

```python
DAG = {
    "seed_snapshot": [],
    "generate_items": ["seed_snapshot"],
    "validate_schema": ["generate_items"],
    "validate_evidence": ["validate_schema"],
    "human_review": ["validate_evidence"],
    "publish_dataset": ["human_review"],
}
```

또한 accepted 배치는 DVC나 동등한 데이터 버전 시스템으로 고정해 두어야 합니다.

```bash
dvc add datasets/ai-data-preparation-101/07-synthetic-data-generation/<run_id>/accepted.jsonl
git add datasets/ai-data-preparation-101/07-synthetic-data-generation/<run_id>/accepted.jsonl.dvc
git commit -m "Track synthetic batch <run_id>"
```

이 기록이 있어야 “어떤 프롬프트와 어떤 검증 기준으로 만들어진 데이터인지”를 나중에도 설명할 수 있습니다.

## 흔히 헷갈리는 지점

- **합성 데이터는 많이 만들수록 좋습니다**: 아닙니다. reject 가능한 기준 없이 양만 늘리면 노이즈가 더 빨리 쌓입니다.
- **teacher가 강하면 distillation 데이터도 자동으로 안전합니다**: 아닙니다. 품질과 정책은 별도 게이트입니다.
- **RAG eval도 instruction tuning과 같은 기준으로 보면 됩니다**: 아닙니다. RAG eval은 evidence fidelity가 우선입니다.
- **JSON으로만 나오면 바로 학습에 써도 됩니다**: 아닙니다. schema 통과는 시작일 뿐이고, diversity와 refusal, evidence까지 봐야 합니다.

## 운영 체크리스트

- [ ] 배치 목표를 먼저 정하고 Self-Instruct/Evol-Instruct/RAG eval/distillation 중 branch를 선택했다
- [ ] generation contract에 `source_type`, `difficulty`, `evidence`, `reasons`를 포함했다
- [ ] accept ratio, unique ratio, refusal ratio 기준을 배치 실행 전에 문서화했다
- [ ] `rag_eval` 샘플은 evidence가 실제 source chunk에 존재하는지 검증했다
- [ ] distillation은 output-usage 정책 검토 ticket 없이는 시작하지 않는다
- [ ] 통과분만 `datasets/ai-data-preparation-101/07-synthetic-data-generation/<run_id>/accepted.jsonl`에 저장한다

## 정리

합성 데이터 생성은 네 가지 패턴을 외우는 일이 아니라, 하나의 synthetic batch workflow를 안전하게 운영하는 일입니다. seed task 입력, JSON contract, reject logic, validation gate, dataset write path가 모두 연결되어야 실제로 재현 가능한 파이프라인이 됩니다.

Self-Instruct는 coverage를 넓히고, Evol-Instruct는 난도를 높이고, RAG eval은 근거 중심 평가셋을 만들고, distillation은 teacher 행동을 student 데이터로 옮깁니다. 하지만 어느 branch를 고르든, 검증과 정책 게이트가 생성보다 먼저 와야 합니다.

다음 글에서는 새 샘플을 처음부터 만드는 대신, 기존 샘플을 의미 보존 범위 안에서 변형하는 augmentation workflow를 다룹니다.

## 처음 질문으로 돌아가기

- **도메인 파인튜닝용 synthetic batch는 어떤 입력에서 시작해 어떤 산출물로 끝나야 할까요?**
  - 본문의 기준은 합성 데이터 생성 — Self-Instruct부터 Distillation까지를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Self-Instruct, Evol-Instruct, RAG eval, distillation은 어느 시점에 선택해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **생성된 JSON 산출물은 어떤 검증 게이트를 통과해야 실제 데이터셋에 편입할 수 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Data Preparation 101 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [AI Data Preparation 101 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [AI Data Preparation 101 (4/10): 학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- [AI Data Preparation 101 (5/10): Tokenization과 Chunking 전략](./05-tokenization-chunking.md)
- [AI Data Preparation 101 (6/10): 데이터 품질 필터링 — Heuristic과 Classifier](./06-quality-filtering.md)
- **합성 데이터 생성 — Self-Instruct부터 Distillation까지 (현재 글)**
- 데이터 증강 기법 — EDA부터 Back-Translation까지 (예정)
- 학습/평가/테스트 분할과 Contamination 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [OpenAI Terms of Use](https://openai.com/policies/terms-of-use/)
- [OpenAI Usage Policies](https://openai.com/policies/usage-policies/)
- [OpenAI API Developer Docs](https://platform.openai.com/docs/overview)

### 논문 및 구현 참고
- [Self-Instruct: Aligning Language Model with Self Generated Instructions (Wang et al., 2022)](https://arxiv.org/abs/2212.10560)
- [WizardLM: Empowering Large Language Models to Follow Complex Instructions (Xu et al., 2023)](https://arxiv.org/abs/2304.12244)
- [Stanford Alpaca - Instruction-tuned LLaMA](https://github.com/tatsu-lab/stanford_alpaca)
- [Synthetic Data Generation with Large Language Models (Long et al., 2024 survey)](https://arxiv.org/abs/2406.15126)

### 관련 시리즈
- [LLM 파인튜닝 101 — 데이터셋 준비와 전처리](../../llm-finetuning-101/ko/02-dataset.md)
- [AI Evaluation 101 — LLM-as-Judge — 모델로 모델을 평가하기](../../ai-evaluation-101/ko/04-llm-as-judge.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-data-preparation-101/ko/07-synthetic-data-generation)

Tags: Synthetic Data, Self-Instruct, Evol-Instruct, Distillation, GPT-4, Alpaca
