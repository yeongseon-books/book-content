---
episode: 8

language: ko

last_reviewed: '2026-05-17'

series: ai-data-preparation-101

status: publish-ready

tags:
- Data Augmentation
- EDA
- Back-Translation
- Paraphrase
- nlpaug
- KoNLPy
targets:

  ebook: true

  medium: false

  mkdocs: true

  tistory: true

title: "AI Data Preparation 101 (8/10): 데이터 증강 기법 — EDA부터 Back-Translation까지"

seo_description: augmentation은 held-out 평가를 통과할 만큼 라벨 의미를 지키며 train 분포를 넓히는 의사결정입니다.
---

# AI Data Preparation 101 (8/10): 데이터 증강 기법 — EDA부터 Back-Translation까지

이 글은 AI Data Preparation 101 시리즈의 8번째 글입니다.

데이터 증강은 새 샘플을 처음부터 생성하는 일이 아니라, 기존 샘플의 라벨 의미를 유지한 채 학습 분포를 넓히는 통제된 변환입니다. 그래서 실전에서는 “어떤 기법이 있나?”보다 “지금의 데이터 문제에 어떤 기법을 적용하고, held-out 평가로 통과 여부를 어떻게 판단할까?”가 더 중요합니다.

이번 글은 issue #779가 지적한 약점처럼 기법 소개만 나열하지 않고, 하나의 augmentation decision path로 08화를 다시 묶습니다. 동시에 신뢰하기 어려웠던 AST rename 예시를 고치고, 한국어 주의사항과 KoNLPy 참고 자료도 본문·참고 자료·태그가 서로 맞도록 정리합니다.


![AI 데이터 준비 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/08/08-01-big-picture.ko.png)
*AI 데이터 준비 8장 흐름 개요*
> 데이터 증강 기법 — EDA부터 Back-Translation까지의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- augmentation은 synthetic generation과 무엇이 다른가요?
- minority class와 typo robustness 문제를 어떤 decision path로 풀어야 하나요?
- EDA, back-translation, paraphrase, AST transform은 각각 언제 선택하고 언제 멈춰야 하나요?

## 왜 이 글이 중요한가

증강은 라벨링 예산이 부족할 때 특히 유용합니다. minority class recall을 끌어올리거나, 오탈자와 패러프레이즈에 대한 강건성을 높일 수 있기 때문입니다. 하지만 validation까지 같이 바꾸거나, 의미 보존이 안 되는 변환을 무차별로 섞으면 오프라인 점수만 좋아 보이고 실제 일반화는 나빠질 수 있습니다.

그래서 augmentation은 “데이터 부풀리기”가 아니라 **train-only 변환 + held-out 평가 + stop/go 판단**으로 닫히는 운영 절차로 이해해야 합니다.

> 좋은 augmentation은 샘플 수를 늘리는 것이 아니라, 원래 라벨이 유지되는 변형만 남기고 나머지를 과감히 버리게 해 줍니다.

## 하나의 데이터 문제로 시작해 보겠습니다

시나리오는 다음과 같습니다.

- 문제 유형: 한국어 고객지원 intent 분류기
- 라벨: `refund_delay`, `cancel_plan`, `outage_question`, `feature_request`
- 현재 문제 1: `refund_delay` 클래스가 280건으로 가장 적음
- 현재 문제 2: 실제 문의에는 오탈자와 구어체가 많아 held-out robustness가 약함
- 고정 규칙: validation/test는 절대 증강하지 않음

이 상황에서 가장 자연스러운 decision path는 다음입니다.

1. held-out validation을 먼저 고정합니다.
2. minority class와 robustness 중 어떤 문제가 더 큰지 baseline metric으로 확인합니다.
3. label-preserving 가능성이 높은 augmentation family부터 순서대로 시도합니다.
4. semantic dedup과 train-only guardrail을 통과한 샘플만 학습에 넣습니다.
5. held-out metric이 개선되지 않으면 stop합니다.

## baseline과 held-out부터 고정합니다

증강은 baseline이 없으면 판단할 수 없습니다. 아래처럼 baseline metric을 먼저 기록합니다.

```python
BASELINE = {
    "macro_f1": 0.812,
    "refund_delay_recall": 0.611,
    "typo_slice_f1": 0.584,
}

TARGET = {
    "macro_f1_min_delta": 0.010,
    "refund_delay_recall_min_delta": 0.030,
    "typo_slice_f1_min_delta": 0.020,
}
```

여기서 핵심은 전체 macro F1만 보는 것이 아니라, 실제로 개선하고 싶은 슬라이스를 따로 잡는 것입니다. 이 사례에서는 `refund_delay_recall`과 `typo_slice_f1`이 decision metric입니다.

## 어떤 augmentation family를 먼저 고를까요?

이 문제에서는 모든 기법을 한 번에 섞지 않는 편이 좋습니다.

| 기법 | 먼저 시도할지 | 이유 |
| --- | --- | --- |
| EDA | 제한적으로만 | 빠르지만 한국어 조사와 어순을 쉽게 깨뜨립니다. |
| Back-Translation | 조건부로 시도 | 자연스러운 재표현을 만들 수 있지만 엔티티·수치가 바뀌면 위험합니다. |
| Paraphrase model | 우선 시도 | minority class 문장을 늘리기에 가장 해석하기 쉽습니다. |
| AST transform | 코드 데이터일 때만 | 텍스트 분류가 아니라 코드 코퍼스일 때 의미 보존성이 높습니다. |

이번 사례에서는 `refund_delay` class의 표현 다양성을 키우는 것이 1차 목표이므로 **paraphrase + 한국어 guardrail**을 먼저 시도하고, typo robustness가 남으면 소량의 문자 수준 노이즈를 추가합니다. 영어 중심 EDA를 한국어 문장 전체에 바로 적용하는 것은 기본값이 아닙니다.

## 한국어 guardrail은 형태소 단위로 거는 편이 안전합니다

한국어는 조사와 어미가 라벨 의미를 쉽게 흔듭니다. 그래서 임의 swap/delete보다, 적어도 형태소 분석 결과를 보고 보호 토큰을 정하는 편이 낫습니다.

```python
from konlpy.tag import Okt

okt = Okt()
PROTECTED_POS = {"Josa", "Eomi", "Punctuation"}

def extract_replaceable_tokens(text: str) -> list[str]:
    tokens = []
    for surface, pos in okt.pos(text, norm=True, stem=True):
        if pos not in PROTECTED_POS and len(surface) > 1:
            tokens.append(surface)
    return tokens

text = "환불이 아직 안 됐는데 언제 처리되나요?"
print(extract_replaceable_tokens(text))
# ['환불', '아직', '처리']
```

이 규칙만으로도 `은/는`, `이/가`, 종결 어미를 지워 의미를 망가뜨리는 사고를 많이 줄일 수 있습니다. issue #779가 지적한 한국어 warning은 바로 이런 operational guardrail로 연결돼야 하고, KoNLPy는 그 근거가 되는 도구입니다.

## concrete augmentation workflow: paraphrase를 먼저 적용합니다

아래 예시는 minority class만 선택해 paraphrase를 만들고, semantic dedup과 금지 규칙을 통과한 샘플만 train에 추가하는 흐름입니다.

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline

embedder = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
paraphraser = pipeline(
    "text2text-generation",
    model="humarin/chatgpt_paraphraser_on_T5_base",
)

BANNED_SUBSTRINGS = ["환불 불가", "법적 조치", "계정 정지"]

def paraphrase_ko(text: str, n: int = 3) -> list[str]:
    outputs = paraphraser(
        text,
        num_return_sequences=n,
        num_beams=n + 2,
        do_sample=True,
        temperature=0.8,
        max_length=96,
    )
    return [o["generated_text"].strip() for o in outputs]

def semantic_similarity(a: str, b: str) -> float:
    va = embedder.encode([a])
    vb = embedder.encode([b])
    return float(cosine_similarity(va, vb)[0][0])

def build_augmented_rows(rows: list[dict]) -> list[dict]:
    augmented = []
    for row in rows:
        if row["label"] != "refund_delay":
            continue

        for candidate in paraphrase_ko(row["text"]):
            if any(bad in candidate for bad in BANNED_SUBSTRINGS):
                continue
            sim = semantic_similarity(row["text"], candidate)
            if sim < 0.78 or sim > 0.97:
                continue
            augmented.append({
                "text": candidate,
                "label": row["label"],
                "source_id": row["id"],
                "aug_method": "paraphrase",
                "similarity": round(sim, 4),
            })
    return augmented
```

여기서는 similarity가 너무 낮아 의미가 바뀐 샘플과, 너무 높아 정보량이 거의 없는 near-duplicate를 둘 다 버립니다. augmentation은 많이 남기는 게임이 아니라, train에 넣어도 되는 샘플만 남기는 게임입니다.

## typo robustness는 별도 slice로 다룹니다

오탈자 강건성까지 함께 보고 싶다면, minority class augmentation과 같은 배치에 섞기보다 slice를 분리하는 편이 좋습니다.

```python
import random

def inject_typo(text: str, p: float = 0.08) -> str:
    chars = list(text)
    for i in range(len(chars) - 1):
        if random.random() < p and chars[i].isalnum() and chars[i + 1].isalnum():
            chars[i], chars[i + 1] = chars[i + 1], chars[i]
            break
    return "".join(chars)

print(inject_typo("환불이 아직 안 됐는데 언제 처리되나요?"))
```

이 slice는 train에만 아주 소량 넣고, held-out typo slice에서만 이득을 확인합니다. 전체 데이터에 과도하게 퍼뜨리면 오히려 깨진 문장 분포를 학습할 수 있습니다.

## held-out evaluation으로 stop/go를 결정합니다

증강은 결국 평가로 닫혀야 합니다.

```python
def evaluate_augmentation(train_base, train_aug, val_loader, train_fn, eval_fn):
    base_model = train_fn(train_base)
    aug_model = train_fn(train_base + train_aug)
    base_metrics = eval_fn(base_model, val_loader)
    aug_metrics = eval_fn(aug_model, val_loader)
    return {
        "base": base_metrics,
        "aug": aug_metrics,
        "delta": {
            key: round(aug_metrics[key] - base_metrics[key], 4)
            for key in base_metrics
        },
    }
```

이번 사례의 예시 결과는 아래처럼 해석할 수 있습니다.

| 실험 | macro_f1 | refund_delay_recall | typo_slice_f1 | 판단 |
| --- | ---: | ---: | ---: | --- |
| baseline | 0.812 | 0.611 | 0.584 | 기준선 |
| paraphrase + Korean guardrail | 0.826 | 0.691 | 0.603 | Go |
| + aggressive EDA (`aug_p=0.3`) | 0.804 | 0.676 | 0.597 | Stop |

이 표가 보여 주는 메시지는 단순합니다. paraphrase는 도움이 되었지만, 공격적인 EDA는 held-out 성능을 깎았으므로 버려야 합니다. augmentation은 기법 설명보다 stop/go 판단이 더 중요합니다.

## AST transform은 코드 데이터에서만 의미 있게 꺼냅니다

issue #779가 지적한 깨진 AST rename 예시는 실제 출력 주석과 코드가 맞지 않는 문제가 있었습니다. 아래처럼 `ast.arg`와 `ast.Name`을 함께 바꾸면 주석과 출력이 일치합니다.

```python
import ast

class VarRenamer(ast.NodeTransformer):
    def __init__(self, mapping: dict[str, str]):
        self.mapping = mapping

    def visit_arg(self, node: ast.arg) -> ast.arg:
        if node.arg in self.mapping:
            node.arg = self.mapping[node.arg]
        return node

    def visit_Name(self, node: ast.Name) -> ast.Name:
        if node.id in self.mapping:
            node.id = self.mapping[node.id]
        return node

def rename_vars(src: str) -> str:
    tree = ast.parse(src)
    names = sorted(
        {n.arg for n in ast.walk(tree) if isinstance(n, ast.arg)}
        | {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and not n.id.startswith("__")}
    )
    mapping = {name: f"v{i}" for i, name in enumerate(names)}
    new_tree = VarRenamer(mapping).visit(tree)
    ast.fix_missing_locations(new_tree)
    return ast.unparse(new_tree)

src = """
def add(left, right):
    total = left + right
    return total
"""

print(rename_vars(src))
# def add(v0, v1):
#     v2 = v0 + v1
#     return v2
```

이 예시는 텍스트 분류용 augmentation과 별개로, **코드 코퍼스에서는 AST 수준 변환이 토큰 치환보다 안전하다**는 사실을 보여 주기 위한 branch입니다. 즉, 같은 augmentation이라도 데이터 종류가 바뀌면 선택지도 달라집니다.

## 증강 파이프라인을 DAG로 고정하는 방법

증강 실험이 늘어날수록 가장 먼저 필요한 것은 기법이 아니라 실행 순서 고정입니다. 실전에서는 아래처럼 `select -> augment -> guardrail -> dedup -> eval -> approve`를 DAG로 분리합니다.

```python
AUG_DAG = {
    "select_train_slice": [],
    "augment_candidates": ["select_train_slice"],
    "apply_korean_guardrail": ["augment_candidates"],
    "semantic_dedup": ["apply_korean_guardrail"],
    "merge_train": ["semantic_dedup"],
    "heldout_eval": ["merge_train"],
    "approve_or_reject": ["heldout_eval"],
}
```

이 구조를 두면 특정 단계 실패 시 전체 배치를 폐기할지, 일부 단계부터 재시도할지 기준이 명확해집니다.

## 증강 샘플 검증 스키마

```python
from pydantic import BaseModel, Field

class AugmentedRow(BaseModel):
    source_id: str
    text: str
    label: str
    aug_method: str
    similarity: float = Field(ge=0.0, le=1.0)
    passed_guardrail: bool

class AugmentBatchReport(BaseModel):
    batch_id: str
    n_candidates: int
    n_kept: int
    keep_ratio: float
    macro_f1_delta: float
    slice_metric_delta: dict
```

## back-translation 예시(검증 포함)

```python
# pseudo-code
def back_translate_ko(text: str, mt_ko_en, mt_en_ko):
    mid = mt_ko_en(text)
    out = mt_en_ko(mid)
    return out

def keep_bt_sample(src: str, cand: str, sim_fn) -> bool:
    sim = sim_fn(src, cand)
    if sim < 0.76 or sim > 0.98:
        return False
    if any(x in cand for x in ["개인정보", "계정 정지"]):
        return False
    return True
```

증강은 결국 평가지표 개선으로 닫혀야 합니다. `keep_ratio`가 높아도 held-out 개선이 없으면 그 배치는 버리는 것이 맞습니다.

## before/after 샘플

```text
원문: 환불이 지연되고 있는데 진행 상태를 확인하고 싶습니다.
증강: 환불 처리가 늦어지고 있어 현재 진행 상황을 알고 싶습니다.
```

이 정도의 변형은 라벨을 유지하면서 표현 다양성을 늘립니다. 반대로 정책 의미가 바뀌는 문장은 유사도가 높아도 버려야 합니다.

## 증강 편입 비율(cap) 운영 규칙

증강 샘플이 원본보다 많아지면 모델이 변형 문장 분포에 과적합할 수 있습니다. 그래서 클래스별 편입 상한을 두는 편이 안전합니다.

```python
AUG_CAP = {
    "refund_delay": 0.8,   # augmented <= 80% of original class rows
    "cancel_plan": 0.5,
    "outage_question": 0.4,
    "feature_request": 0.4,
}

def apply_cap(original_count: int, augmented_rows: list[dict], label: str) -> list[dict]:
    cap = int(original_count * AUG_CAP[label])
    return augmented_rows[:cap]
```

## 증강 배치 품질 리포트

```python
def augment_report(rows: list[dict]) -> dict:
    sims = [r["similarity"] for r in rows]
    return {
        "n_rows": len(rows),
        "avg_similarity": sum(sims) / max(len(sims), 1),
        "min_similarity": min(sims) if sims else 0.0,
        "max_similarity": max(sims) if sims else 0.0,
        "method_dist": {m: sum(r["aug_method"] == m for r in rows) for m in sorted(set(r["aug_method"] for r in rows))},
    }
```

`avg_similarity`만 보면 착시가 생깁니다. `min/max`와 method 분포를 같이 봐야 한 기법이 과도하게 지배하는 상황을 막을 수 있습니다.

## 실무 기본값

- first run은 paraphrase 단일 기법으로 시작합니다.
- held-out 개선이 확인되면 back-translation을 소량 추가합니다.
- EDA는 한국어에서 마지막 선택지로 둡니다.

이 순서를 지키면 증강 실험의 실패 비용을 크게 줄일 수 있습니다.

## 운영에서 바로 쓰는 점검 질문

아래 질문은 배포 직전 리뷰에서 실제로 자주 쓰는 체크 항목입니다. 단순 문서 확인이 아니라, 각 질문에 대해 파일 경로나 지표 값으로 즉시 답할 수 있어야 합니다.

1. 이번 데이터셋은 어떤 버전에서 왔고, sha256은 무엇인가요?
2. 지난 배치 대비 duplicate/null/length 분포가 얼마나 변했나요?
3. 제거된 샘플은 어떤 규칙 때문에 빠졌고, 상위 제거 사유는 무엇인가요?
4. train/eval/test 경계에서 누수 가능성은 수치로 얼마나 남아 있나요?
5. 이번 배치에서 사람이 검토한 샘플과 발견된 오류 유형은 무엇인가요?

```python
def release_readiness(summary: dict) -> tuple[bool, list[str]]:
    issues = []
    if not summary.get("dataset_sha256"):
        issues.append("missing_dataset_sha256")
    if summary.get("duplicate_ratio", 1.0) > 0.10:
        issues.append("duplicate_ratio_too_high")
    if summary.get("null_ratio", 1.0) > 0.02:
        issues.append("null_ratio_too_high")
    if summary.get("contamination_ratio", 1.0) > 0.01:
        issues.append("contamination_ratio_too_high")
    if summary.get("human_reviewed_rows", 0) < 100:
        issues.append("insufficient_human_review")
    return len(issues) == 0, issues
```

운영 팀은 이 함수를 그대로 쓰지 않더라도 같은 개념을 파이프라인 게이트로 구현해야 합니다. 핵심은 “준비가 되었는지 느낌으로 판단하지 않는다”는 점입니다.

## 실무 로그 예시

```text
[release-check] dataset=v2.4.1 sha=4fb1...
[release-check] duplicate_ratio=0.061 null_ratio=0.008
[release-check] contamination_ratio=0.004 human_reviewed_rows=240
[release-check] status=PASS
```

이 로그 한 묶음이 있으면 모델 성능이 흔들릴 때도 데이터 준비 단계를 빠르게 제외하거나 집중 점검할 수 있습니다. 데이터 준비의 품질은 글 한 편의 설명보다, 이런 반복 가능한 검증 로그에서 드러납니다.

### 증강 중단 조건

새 배치에서 `macro_f1`가 개선되지 않거나, 특정 클래스 precision이 2회 연속 하락하면 즉시 증강 실험을 중단하고 원인 분석으로 전환합니다.

### 릴리스 노트에 남겨야 할 최소 항목

해당 단계의 변경은 릴리스 노트에도 남겨야 합니다. 최소한 `변경 규칙`, `영향받은 행 수`, `핵심 지표 변화`, `롤백 경로` 네 항목이 있어야 다음 배치에서 같은 판단을 반복할 수 있습니다.

## 흔히 헷갈리는 지점

- **validation도 같이 증강하면 더 공정합니다**: 아닙니다. 그건 공정성이 아니라 leakage입니다.
- **한국어에도 영어식 EDA를 그대로 돌리면 됩니다**: 아닙니다. 조사·어미 보호 규칙이 없으면 의미 훼손이 빠르게 늘어납니다.
- **similarity가 높을수록 좋은 샘플입니다**: 아닙니다. 너무 높으면 near-duplicate라 정보량이 거의 없습니다.
- **기법을 많이 섞을수록 성능이 좋아집니다**: 아닙니다. 각 기법은 held-out 기준으로 따로 stop/go 판단해야 합니다.

## 운영 체크리스트

- [ ] baseline과 held-out slice metric을 먼저 고정했다
- [ ] augmentation은 train에만 적용하고 validation/test는 원본으로 유지한다
- [ ] minority class 보강과 typo robustness 실험을 분리해 본다
- [ ] semantic similarity와 금지 규칙으로 near-duplicate와 의미 훼손 샘플을 제거한다
- [ ] 한국어 데이터는 형태소 단위 보호 규칙을 두고, 필요 시 KoNLPy 같은 도구로 토큰 후보를 제한한다
- [ ] held-out metric이 개선되지 않으면 augmentation batch를 버린다

## 정리

augmentation의 핵심은 기술 이름이 아니라 의사결정 흐름입니다. 어떤 데이터 문제를 풀고 싶은지 정의하고, train-only guardrail을 둔 뒤, held-out 평가에서 통과한 변환만 남겨야 합니다.

이번 사례에서는 paraphrase와 한국어 guardrail이 `refund_delay` recall과 typo robustness를 동시에 개선했지만, 공격적인 EDA는 오히려 해가 되었습니다. AST transform은 코드 데이터일 때만 꺼내야 하는 별도 branch라는 점도 함께 기억해 두면 좋습니다.

다음 글에서는 증강과 생성 이후에 반드시 필요한 train/eval/test splitting과 contamination 통제를 다룹니다.

## 처음 질문으로 돌아가기

- **augmentation은 synthetic generation과 무엇이 다른가요?**
  - 본문의 기준은 데이터 증강 기법 — EDA부터 Back-Translation까지를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **minority class와 typo robustness 문제를 어떤 decision path로 풀어야 하나요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **EDA, back-translation, paraphrase, AST transform은 각각 언제 선택하고 언제 멈춰야 하나요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Data Preparation 101 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [AI Data Preparation 101 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [AI Data Preparation 101 (4/10): 학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- [AI Data Preparation 101 (5/10): Tokenization과 Chunking 전략](./05-tokenization-chunking.md)
- [AI Data Preparation 101 (6/10): 데이터 품질 필터링 — Heuristic과 Classifier](./06-quality-filtering.md)
- [AI Data Preparation 101 (7/10): 합성 데이터 생성 — Self-Instruct부터 Distillation까지](./07-synthetic-data-generation.md)
- **데이터 증강 기법 — EDA부터 Back-Translation까지 (현재 글)**
- 학습/평가/테스트 분할과 Contamination 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서 및 도구
- [KoNLPy documentation](https://konlpy.org/en/latest/)
- [KoNLPy: Korean natural language processing in Python (Park & Cho, 2014)](http://dmlab.snu.ac.kr/~lucypark/docs/2014-10-10-hclt.pdf)
- [nlpaug - Data Augmentation for NLP](https://github.com/makcedward/nlpaug)
- [Helsinki-NLP OPUS-MT Models](https://huggingface.co/Helsinki-NLP)

### 논문 및 구현 참고
- [EDA: Easy Data Augmentation Techniques (Wei & Zou, 2019)](https://arxiv.org/abs/1901.11196)
- [Improving Neural Machine Translation with Back-Translation (Sennrich et al., 2016)](https://arxiv.org/abs/1511.06709)
- [Sentence-Transformers: Multilingual MiniLM](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)

### 관련 시리즈
- [LLM 파인튜닝 101 — 데이터셋 준비와 전처리](../../llm-finetuning-101/ko/02-dataset.md)
- [AI Evaluation 101 — LLM-as-Judge — 모델로 모델을 평가하기](../../ai-evaluation-101/ko/04-llm-as-judge.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-data-preparation-101/ko/08-data-augmentation)

Tags: Data Augmentation, EDA, Back-Translation, Paraphrase, nlpaug, KoNLPy
