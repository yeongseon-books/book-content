---
title: "바이브코딩을 위한 AI 데이터 준비 (7/10): 합성 데이터 생성"
series: ai-data-preparation-101
episode: 7
language: ko
tags:
- Synthetic Data
- Self-Instruct
- Evol-Instruct
- Distillation
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 데이터 준비 (7/10): 합성 데이터 생성

이 글은 **바이브코딩을 위한 AI 데이터 준비** 시리즈의 일곱 번째 글입니다.

---

바이브코딩으로 특정 도메인의 파인튜닝 데이터를 만들려고 할 때 "레이블된 데이터가 40개밖에 없는데 어떻게 하나요?"라는 상황이 자주 생깁니다. 이때 등장하는 해결책이 합성 데이터 생성입니다.

합성 데이터는 AI가 AI를 위한 학습 데이터를 만드는 것입니다. GPT-4o-mini에게 seed 태스크를 보여주고 "비슷하지만 다른 새 태스크를 만들어줘"라고 하면 됩니다. 하지만 검증 없이 만들기만 하면 비슷한 샘플이 반복되거나, 사실과 다른 답변이 섞여 들어갑니다. **무엇을 버릴지 설계**하는 것이 합성 데이터 생성의 핵심입니다.

> "합성 데이터의 성패는 얼마나 많이 생성했는가가 아니라, 어떤 배치를 버릴 수 있게 설계했는가에 달려 있습니다."

## 이 글에서 다룰 질문

1. Self-Instruct, Evol-Instruct, RAG eval, Distillation은 각각 언제 선택하나요?
2. 생성된 데이터를 검증하는 게이트는 어떻게 설계하나요?
3. 배치 승인 기준을 어떻게 수치로 정의하나요?
4. Distillation에서 정책 검토가 왜 필수인가요?
5. 합성 데이터를 DVC로 버전 관리하는 방법은?

---

## 4가지 생성 방법 비교

| 방법 | 목적 | 언제 선택 |
|------|------|----------|
| Self-Instruct | seed task에서 새 task 생성 | 다양성 부족, seed가 적을 때 |
| Evol-Instruct | 기존 task의 난도 높이기 | 쉬운 task가 너무 많을 때 |
| RAG eval pair | 문서 기반 QA 쌍 생성 | Retrieval 평가셋이 부족할 때 |
| Distillation | 강한 teacher의 응답 스타일 이전 | 출력 품질 높이기, 단 정책 검토 필수 |

## Before / After: 검증 없는 생성 vs 게이트 기반 생성

**Before (검증 없이 생성)**
```python
items = generate_batch("고객지원 시나리오를 만들어줘")
train_data.extend(items)  # 검증 없이 바로 추가
# 문제: 중복, 짧은 답변, 사실과 다른 내용이 섞임
```

**After (검증 게이트 적용)**
```python
def validate_item(item: dict) -> list[str]:
    """생성된 샘플의 품질 문제를 반환합니다."""
    issues = []

    # 필수 필드 확인
    for key in ["instruction", "input", "output", "source_type"]:
        if key not in item:
            issues.append(f"missing:{key}")

    # 출력이 너무 짧음
    if len(item.get("output", "")) < 30:
        issues.append("too_short")

    # 거부 응답 패턴 (instruction tuning에 불필요)
    refusal_patterns = ["죄송하지만", "도와드릴 수 없습니다", "i cannot"]
    if any(p in item.get("output", "").lower() for p in refusal_patterns):
        issues.append("refusal_like_output")

    # RAG eval인데 evidence 없음
    if item.get("source_type") == "rag_eval" and not item.get("evidence"):
        issues.append("missing_evidence")

    return issues

def validate_batch(items: list[dict]) -> tuple[list[dict], list[dict], dict]:
    """배치 전체를 검증하고 통계를 반환합니다."""
    accepted, rejected = [], []
    seen = set()

    for item in items:
        # 중복 확인
        dedup_key = (item.get("instruction"), item.get("input"))
        if dedup_key in seen:
            rejected.append({"item": item, "reasons": ["duplicate"]})
            continue
        seen.add(dedup_key)

        issues = validate_item(item)
        if issues:
            rejected.append({"item": item, "reasons": issues})
        else:
            accepted.append(item)

    total = max(len(items), 1)
    return accepted, rejected, {
        "n_total": len(items),
        "n_accepted": len(accepted),
        "accept_ratio": len(accepted) / total,
        "unique_ratio": len(seen) / total
    }
```

## 배치 승인 기준

```python
def approve_batch(metrics: dict) -> bool:
    """배치가 학습 데이터로 사용 가능한지 판단합니다."""
    if metrics["accept_ratio"] < 0.80:
        print(f"거부: 수락률 {metrics['accept_ratio']:.1%} (기준: 80%)")
        return False
    if metrics["unique_ratio"] < 0.85:
        print(f"거부: 고유성 {metrics['unique_ratio']:.1%} (기준: 85%)")
        return False
    return True
```

## Distillation: 정책 검토 먼저

```python
def require_policy_review(branch: str, teacher_name: str, review_ticket: str | None) -> None:
    """Distillation 시작 전 정책 검토 여부를 확인합니다."""
    if branch != "distillation":
        return
    if not review_ticket:
        raise RuntimeError(
            f"중단: {teacher_name}의 output 사용 정책을 먼저 검토하세요. "
            f"검토 완료 후 review_ticket을 입력하세요."
        )

# 사용 예시 — ticket 없이는 시작 불가
require_policy_review(
    branch="distillation",
    teacher_name="OpenAI API model",
    review_ticket=None  # 정책 검토 완료 후 ticket 번호 입력
)
```

OpenAI 등 API 제공자의 출력을 학습 데이터로 사용할 때는 반드시 해당 서비스의 최신 이용약관을 확인하세요. 이 코드는 해당 검토를 강제하는 안전장치입니다.

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 검증 없이 바로 학습 | 노이즈, 중복, 짧은 답변 포함 | 배치 검증 게이트 적용 |
| 합성 데이터만으로 학습 | 패턴 편향, 품질 저하 | 실제 데이터와 혼합 |
| Distillation 정책 무시 | 법적/계약 위반 위험 | 반드시 정책 검토 후 진행 |
| 수락률만 봄 | 고유성 낮아도 통과 | unique_ratio도 함께 확인 |

## AI 팁

합성 배치를 학습에 쓸 때는 DVC로 버전을 고정해야 나중에 "어떤 데이터로 학습했는가"를 재현할 수 있습니다.

```bash
dvc add datasets/synthetic/batch-001/accepted.jsonl
git add datasets/synthetic/batch-001/accepted.jsonl.dvc
git commit -m "Track synthetic batch 001"
```

또한 생성 프롬프트와 검증 기준을 코드와 함께 버전 관리하세요. 나중에 같은 방법으로 추가 배치를 생성하거나 문제를 재현할 수 있습니다.

## 체크리스트

- [ ] 목적에 맞는 생성 방법(Self-Instruct/Evol-Instruct/RAG eval/Distillation)을 선택했다
- [ ] 필수 필드, 출력 품질, 중복을 검증하는 게이트를 구현했다
- [ ] accept_ratio와 unique_ratio 기준을 수치로 정의했다
- [ ] Distillation 시 provider 정책을 확인했다
- [ ] 승인된 배치를 DVC로 버전 관리한다

## 처음 질문으로 돌아가기

**4가지 방법 선택 기준은?** Self-Instruct는 다양성이 부족할 때, Evol-Instruct는 난도를 높이고 싶을 때, RAG eval은 검색 평가셋이 필요할 때, Distillation은 teacher 스타일을 이전하고 싶을 때.

**검증 게이트 설계 방법은?** 필수 필드 누락, 너무 짧은 출력, 거부 패턴, 중복, RAG eval의 evidence 누락 — 이 5가지를 최소한으로 확인합니다.

**배치 승인 기준은?** accept_ratio >= 0.80, unique_ratio >= 0.85를 통과해야 학습 데이터로 사용합니다.

**Distillation 정책 검토가 필요한 이유는?** API 제공자가 출력을 학습 데이터로 사용하는 것을 금지할 수 있습니다. 정책을 확인하지 않으면 계약 위반이 됩니다.

**DVC로 버전 관리는?** `dvc add`로 대용량 데이터 파일을 추적하고, `.dvc` 파일을 git에 커밋하면 코드와 데이터 버전이 연결됩니다.

## 정리

합성 데이터 생성은 데이터를 많이 만드는 것이 아니라, 어떤 배치를 버릴지 설계하는 작업입니다. 검증 게이트로 품질을 보장하고, Distillation은 정책 검토 후에만 사용하며, 승인된 배치는 DVC로 버전을 고정해야 재현 가능한 파이프라인이 됩니다.

다음 글에서는 기존 샘플을 변형해 데이터를 늘리는 **데이터 증강 기법**을 다룹니다.

## 참고 자료

- [AI 데이터 준비 원문: 합성 데이터 생성](../ko/07-synthetic-data-generation.md)
- [Self-Instruct (Wang et al., 2022)](https://arxiv.org/abs/2212.10560)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 데이터 준비 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
2. [바이브코딩을 위한 AI 데이터 준비 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
3. [바이브코딩을 위한 AI 데이터 준비 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
4. [바이브코딩을 위한 AI 데이터 준비 (4/10): PII 탐지와 익명화](./04-pii-detection-anonymization.md)
5. [바이브코딩을 위한 AI 데이터 준비 (5/10): Tokenization과 Chunking](./05-tokenization-chunking.md)
6. [바이브코딩을 위한 AI 데이터 준비 (6/10): 데이터 품질 필터링](./06-quality-filtering.md)
7. **바이브코딩을 위한 AI 데이터 준비 (7/10): 합성 데이터 생성 (현재 글)**
8. [바이브코딩을 위한 AI 데이터 준비 (8/10): 데이터 증강 기법](./08-data-augmentation.md)
9. [바이브코딩을 위한 AI 데이터 준비 (9/10): 학습/평가/테스트 분할](./09-train-eval-test-splitting.md)
10. [바이브코딩을 위한 AI 데이터 준비 (10/10): 프로덕션 데이터 파이프라인](./10-production-data-pipeline.md)
<!-- toc:end -->

Tags: Synthetic Data, Self-Instruct, Evol-Instruct, Distillation, 바이브코딩
