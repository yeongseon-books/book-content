---
title: "바이브코딩을 위한 AI 데이터 준비 (8/10): 데이터 증강 기법"
series: ai-data-preparation-101
episode: 8
language: ko
tags:
- Data Augmentation
- EDA
- Back-Translation
- Paraphrase
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 데이터 준비 (8/10): 데이터 증강 기법

이 글은 **바이브코딩을 위한 AI 데이터 준비** 시리즈의 여덟 번째 글입니다.

---

바이브코딩으로 분류 모델을 만들다 보면 "특정 카테고리 데이터가 너무 적다" 또는 "실제 서비스 입력에는 오탈자가 많은데 학습 데이터에는 없다"는 문제를 만납니다. 합성 데이터 생성이 새 샘플을 처음부터 만드는 것이라면, 데이터 증강은 **기존 샘플의 의미를 유지한 채 변형해 학습 분포를 넓히는 것**입니다.

핵심은 "의미 보존"입니다. 변형 후에도 라벨이 유지되어야 합니다. "환불 지연 문의"가 패러프레이즈 후 "환불 취소 요청"으로 바뀐다면 라벨이 달라져 오히려 모델에 해가 됩니다. 그래서 모든 증강은 **held-out 평가로 검증**해야 합니다.

> "증강은 샘플 수를 늘리는 것이 아니라, held-out 평가를 통과한 변형만 남기는 작업입니다."

## 이 글에서 다룰 질문

1. 합성 데이터 생성과 데이터 증강의 차이는 무엇인가요?
2. 한국어에서 EDA를 바로 적용하면 안 되는 이유는?
3. 패러프레이즈 증강에서 유사도 범위를 어떻게 설정하나요?
4. held-out 평가로 증강 효과를 어떻게 확인하나요?
5. 증강 샘플의 학습 데이터 비율을 어떻게 제한하나요?

---

## 증강 방법 비교

| 방법 | 특징 | 주의점 |
|------|------|--------|
| EDA (Easy Data Augmentation) | 단어 삽입/삭제/교환 | 한국어 조사/어미 손상 위험 |
| Back-Translation | 다른 언어 거쳐 재번역 | 엔티티·수치 변형 위험 |
| Paraphrase | LLM으로 재표현 | 의미 변형 확인 필요 |
| 오타 주입 | 오탈자 강건성 훈련 | 과도하면 모델 성능 저하 |

## Before / After: 증강 도입

**Before (소수 클래스 데이터 부족)**
```python
# refund_delay 클래스 280건, 나머지 클래스 1000건+
# → 소수 클래스 recall이 낮음
model.train(imbalanced_data)
```

**After (패러프레이즈 증강 + 검증)**
```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
BANNED = ["환불 불가", "법적 조치", "계정 정지"]

def paraphrase_ko(text: str, n: int = 3) -> list[str]:
    """LLM으로 패러프레이즈를 생성합니다."""
    prompt = f"다음 문장을 의미는 유지하면서 {n}가지 다른 표현으로 바꿔주세요. JSON 배열로 반환:\n{text}"
    result = llm.chat(prompt, response_format={"type": "json_object"})
    return json.loads(result)

def semantic_similarity(a: str, b: str) -> float:
    va = embedder.encode([a])
    vb = embedder.encode([b])
    return float(cosine_similarity(va, vb)[0][0])

def build_augmented_rows(rows: list[dict], target_label: str = "refund_delay") -> list[dict]:
    """소수 클래스만 선택해 증강합니다."""
    augmented = []
    for row in rows:
        if row["label"] != target_label:
            continue
        for candidate in paraphrase_ko(row["text"]):
            # 금지 문구 포함 시 제외
            if any(b in candidate for b in BANNED):
                continue
            sim = semantic_similarity(row["text"], candidate)
            # 유사도가 너무 낮으면 의미 변형, 너무 높으면 near-duplicate
            if 0.78 <= sim <= 0.97:
                augmented.append({
                    "text": candidate,
                    "label": row["label"],
                    "source_id": row["id"],
                    "aug_method": "paraphrase",
                    "similarity": round(sim, 4)
                })
    return augmented
```

## 한국어 EDA 주의사항

영어 EDA를 한국어에 바로 적용하면 조사(은/는/이/가)와 어미가 제거되거나 잘못 이동해 문법이 깨집니다.

```python
from konlpy.tag import Okt

okt = Okt()
PROTECTED_POS = {"Josa", "Eomi", "Punctuation"}

def extract_replaceable_tokens(text: str) -> list[str]:
    """형태소 분석으로 변형 가능한 토큰만 추출합니다."""
    tokens = []
    for surface, pos in okt.pos(text, norm=True, stem=True):
        if pos not in PROTECTED_POS and len(surface) > 1:
            tokens.append(surface)
    return tokens

# "환불이 아직 안 됐는데 언제 처리되나요?" → ["환불", "아직", "처리"]
# 조사(이)와 어미(됐는데, 되나요)는 보호됨
```

## held-out 평가로 Stop/Go 결정

```python
def evaluate_augmentation(train_base, train_aug, val_loader, train_fn, eval_fn) -> dict:
    """증강 전후 성능을 비교해 증강 효과를 검증합니다."""
    base_model = train_fn(train_base)
    aug_model = train_fn(train_base + train_aug)

    base_metrics = eval_fn(base_model, val_loader)
    aug_metrics = eval_fn(aug_model, val_loader)

    decision = "Go" if aug_metrics["macro_f1"] > base_metrics["macro_f1"] else "Stop"

    return {
        "base": base_metrics,
        "aug": aug_metrics,
        "delta": {k: aug_metrics[k] - base_metrics[k] for k in base_metrics},
        "decision": decision
    }
```

## 증강 비율 상한 설정

```python
AUG_CAP = {
    "refund_delay": 0.8,    # 원본의 최대 80%까지 증강
    "cancel_plan": 0.5,
    "outage_question": 0.4
}

def apply_cap(original_count: int, augmented: list[dict], label: str) -> list[dict]:
    """클래스별 증강 비율 상한을 적용합니다."""
    cap = int(original_count * AUG_CAP.get(label, 0.5))
    return augmented[:cap]
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| validation에도 증강 적용 | leakage, 평가 신뢰도 하락 | train 데이터에만 증강 |
| 한국어에 영어 EDA 바로 적용 | 조사/어미 파괴로 품질 저하 | KoNLPy로 보호 토큰 정의 |
| 유사도 검증 없이 증강 추가 | 의미 변형 샘플 포함 | 0.78-0.97 범위로 필터 |
| 증강 비율 무제한 | 변형 분포에 과적합 | AUG_CAP으로 클래스별 상한 |

## AI 팁

증강을 처음 적용할 때는 paraphrase 단일 방법으로 시작하세요. held-out 평가에서 효과가 확인되면 back-translation을 소량 추가합니다. EDA는 한국어에서 마지막 선택지입니다.

```python
# 실험 순서
experiments = [
    {"method": "paraphrase", "aug_ratio": 0.5},  # 먼저
    {"method": "back_translation", "aug_ratio": 0.3},  # 효과 확인 후
    {"method": "eda_korean", "aug_ratio": 0.2},  # 마지막
]
```

각 실험에서 held-out macro_f1이 개선되면 Go, 감소하면 Stop합니다.

## 체크리스트

- [ ] validation/test 데이터는 절대 증강하지 않는다
- [ ] 한국어 EDA는 KoNLPy로 보호 토큰을 정의했다
- [ ] 패러프레이즈 유사도를 0.78-0.97 범위로 필터링한다
- [ ] held-out 평가로 증강 효과를 검증했다
- [ ] 클래스별 증강 비율 상한을 설정했다

## 처음 질문으로 돌아가기

**합성 데이터 생성 vs 데이터 증강 차이는?** 합성 데이터는 새 샘플을 처음부터 만드는 것, 증강은 기존 샘플을 의미를 유지한 채 변형하는 것입니다.

**한국어에서 EDA를 바로 적용하면 안 되는 이유는?** 조사(은/는/이/가)와 종결 어미를 임의로 삭제하거나 위치를 바꾸면 문법이 깨지고 의미가 달라집니다. KoNLPy로 보호 토큰을 정의해야 합니다.

**패러프레이즈 유사도 범위는?** 0.78 미만이면 의미가 변형된 것이고, 0.97 초과면 near-duplicate라 정보량이 거의 없습니다. 0.78-0.97 범위가 유효한 증강입니다.

**held-out 평가로 증강 효과 확인은?** 증강 전후 모델을 각각 학습하고 고정된 validation 세트에서 macro_f1을 비교합니다. 개선되면 Go, 감소하면 Stop.

**증강 비율 상한은?** 원본 대비 80% 이상 증강하면 변형 패턴에 과적합 위험이 있습니다. 클래스별로 AUG_CAP을 설정합니다.

## 정리

데이터 증강은 의미를 유지한 채 변형을 통해 학습 분포를 넓힙니다. 한국어에서는 형태소 분석으로 보호 토큰을 정의하고, 유사도 범위로 유효한 증강만 선별하며, 항상 held-out 평가로 효과를 검증해야 합니다.

다음 글에서는 데이터를 올바르게 나누는 **학습/평가/테스트 분할**을 다룹니다.

## 참고 자료

- [AI 데이터 준비 원문: 데이터 증강 기법](../ko/08-data-augmentation.md)
- [EDA: Easy Data Augmentation (Wei & Zou, 2019)](https://arxiv.org/abs/1901.11196)
- [KoNLPy](https://konlpy.org/en/latest/)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 데이터 준비 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
2. [바이브코딩을 위한 AI 데이터 준비 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
3. [바이브코딩을 위한 AI 데이터 준비 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
4. [바이브코딩을 위한 AI 데이터 준비 (4/10): PII 탐지와 익명화](./04-pii-detection-anonymization.md)
5. [바이브코딩을 위한 AI 데이터 준비 (5/10): Tokenization과 Chunking](./05-tokenization-chunking.md)
6. [바이브코딩을 위한 AI 데이터 준비 (6/10): 데이터 품질 필터링](./06-quality-filtering.md)
7. [바이브코딩을 위한 AI 데이터 준비 (7/10): 합성 데이터 생성](./07-synthetic-data-generation.md)
8. **바이브코딩을 위한 AI 데이터 준비 (8/10): 데이터 증강 기법 (현재 글)**
9. [바이브코딩을 위한 AI 데이터 준비 (9/10): 학습/평가/테스트 분할](./09-train-eval-test-splitting.md)
10. [바이브코딩을 위한 AI 데이터 준비 (10/10): 프로덕션 데이터 파이프라인](./10-production-data-pipeline.md)
<!-- toc:end -->

Tags: Data Augmentation, EDA, Back-Translation, Paraphrase, 바이브코딩
