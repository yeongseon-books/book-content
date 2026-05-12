---
episode: 8

language: ko

last_reviewed: '2026-05-12'

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

  medium: true

  mkdocs: true

  tistory: true

title: 데이터 증강 기법 — EDA부터 Back-Translation까지

seo_description: 지난 편의 synthetic data generation은 LLM을 호출해 새 sample을 "처음부터" 만들었습니다.
---

# 데이터 증강 기법 — EDA부터 Back-Translation까지

합성 데이터 생성이 새 샘플을 만들어 감독 신호를 늘리는 방법이라면, 데이터 증강은 기존 샘플을 변형해 분포를 넓히는 방법입니다. 둘은 비슷해 보이지만 실제로 푸는 문제가 다릅니다.

증강은 주로 두 가지 상황에서 빛납니다. 하나는 minority class를 늘려 class imbalance를 완화할 때이고, 다른 하나는 오탈자, 패러프레이즈, 코드 스위칭 같은 현실적인 변형에 모델을 더 강하게 만들고 싶을 때입니다.

운영에서는 augmentation을 “데이터를 부풀리는 쉬운 방법”으로 보면 실패합니다. 변환 비율이 지나치면 라벨 의미가 바뀌고, validation set까지 손대면 누수가 생기며, 한국어에서는 영어용 EDA를 그대로 쓰기 어렵습니다.

따라서 증강의 본질은 양을 늘리는 것이 아니라, 원래 라벨 의미를 지키면서 학습 분포를 적절히 넓히는 것입니다. 이 기준이 흔들리면 증강은 노이즈 생성기로 바뀝니다.

이 글은 AI Data Preparation 101 시리즈의 8번째 글입니다.

여기서는 EDA, back-translation, paraphrase model, 코드용 AST transform을 중심으로 증강 전략을 비교하고, 실제로 도움이 되었는지 평가하는 방법을 정리하겠습니다.

## 이 글에서 다룰 문제

- 증강은 synthetic generation과 어떤 문제 설정이 다를까요?
- EDA의 네 가지 token-level 변환은 언제 유효하고 언제 라벨을 망가뜨릴까요?
- back-translation은 왜 자연스러운 패러프레이즈를 만들지만 사실성이 중요한 도메인에서는 위험할까요?
- 코드 데이터에서는 왜 AST-level transform이 token-level 편집보다 안전할까요?
- 증강이 실제로 도움이 되었는지는 어떤 오프라인 평가로 확인해야 할까요?

## 왜 이 글이 중요한가

증강을 잘 쓰면 적은 라벨 데이터로도 더 넓은 표현 다양성을 줄 수 있고, minority class recall을 높이거나 typo·패러프레이즈에 대한 강건성을 키울 수 있습니다. 특히 라벨링 비용이 높은 분류 문제에서 효과가 큽니다.

반대로 무분별한 증강은 라벨 의미를 바꾸거나, 원문과 거의 같은 샘플을 잔뜩 복제하거나, validation 누수를 만들어 오프라인 점수만 부풀릴 수 있습니다. 이런 실패는 데이터가 많아 보이기 때문에 더 늦게 발견됩니다.

이 글은 augmentation을 “쉽게 데이터 늘리기”가 아니라, 어떤 변환이 의미 보존에 안전한지 판단하는 품질 관리 문제로 바라보게 만드는 데 목적이 있습니다.

## 데이터 증강을 이해하는 가장 좋은 방법: 라벨을 유지한 채 분포를 넓히는 통제된 변환으로 보는 것입니다

좋은 증강은 원문과 완전히 다른 데이터를 만드는 것이 아니라, 원래 샘플이 가질 수 있었던 현실적인 변형을 추가하는 것입니다. 그래서 augmentation의 첫 질문은 “무엇을 바꿀 것인가”보다 “무엇을 절대 바꾸면 안 되는가”에 가깝습니다.

EDA는 가볍고 빠르지만 의미를 쉽게 훼손할 수 있고, back-translation과 paraphrase model은 더 자연스럽지만 비용과 사실성 리스크가 있습니다. 코드 데이터는 의미 보존을 위해 AST 수준 변환이 훨씬 안전합니다.

마지막으로 augmentation은 항상 train-only 규칙 위에서 돌아갑니다. validation과 test는 현실을 측정하는 도구이지, 더 풍부하게 꾸미는 대상이 아닙니다.

> 데이터 증강의 기준은 샘플 수가 아니라 의미 보존입니다. 라벨을 지키지 못하는 증강은 강건성 향상이 아니라 노이즈 주입에 가깝습니다.

## 핵심 개념

### Technique 1: EDA는 가장 가벼운 기본값입니다

EDA는 synonym replacement, random insertion, random swap, random deletion이라는 네 가지 token-level 변환으로 구성됩니다.

```python
# pip install nlpaug
import nlpaug.augmenter.word as naw

# 1) Synonym replacement (WordNet)
syn_aug = naw.SynonymAug(aug_src="wordnet", aug_p=0.1)

# 2) Random insertion (BERT contextual)
ins_aug = naw.ContextualWordEmbsAug(model_path="bert-base-uncased", action="insert", aug_p=0.1)

# 3) Random swap
swap_aug = naw.RandomWordAug(action="swap", aug_p=0.1)

# 4) Random deletion
del_aug = naw.RandomWordAug(action="delete", aug_p=0.1)

text = "The quick brown fox jumps over the lazy dog."
print(syn_aug.augment(text))   # "The fast brown fox jumps over the lazy dog."
print(swap_aug.augment(text))  # "The brown quick fox jumps over the lazy dog."
```

`aug_p`는 보통 0.1~0.2 범위에서 시작합니다. 0.3을 넘기면 문장 의미가 흔들려 원래 라벨이 더 이상 맞지 않는 경우가 빠르게 늘어납니다.

### Technique 2: Back-translation은 자연스러운 재표현을 만듭니다

중간 pivot language를 거쳐 원문 언어로 다시 번역하면 어휘와 표현이 달라진 패러프레이즈를 얻을 수 있습니다.

```python
# pip install transformers torch
from transformers import MarianMTModel, MarianTokenizer

class BackTranslator:
    def __init__(self, src: str = "en", pivot: str = "de"):
        self.fwd = self._load(src, pivot)
        self.bwd = self._load(pivot, src)

    def _load(self, a: str, b: str):
        name = f"Helsinki-NLP/opus-mt-{a}-{b}"
        tok = MarianTokenizer.from_pretrained(name)
        model = MarianMTModel.from_pretrained(name)
        return tok, model

    def _translate(self, text: str, pair):
        tok, model = pair
        enc = tok(text, return_tensors="pt", truncation=True)
        out = model.generate(**enc, num_beams=4, max_length=256)
        return tok.decode(out[0], skip_special_tokens=True)

    def __call__(self, text: str) -> str:
        pivot = self._translate(text, self.fwd)
        return self._translate(pivot, self.bwd)

bt = BackTranslator(src="en", pivot="de")
print(bt("The model achieves state-of-the-art results."))
# -> "The model achieves the best results to date."
```

이 방식은 다양성 측면에서는 좋지만, 의료·법률처럼 사실 하나가 중요한 도메인에서는 숫자나 엔티티가 바뀔 위험이 있어 더 신중해야 합니다.

### Technique 3: Paraphrase model은 더 빠르고 깔끔합니다

전용 패러프레이저는 back-translation보다 자연스러운 문장을 더 빠르게 만들 수 있습니다.

```python
from transformers import pipeline

paraphraser = pipeline(
    "text2text-generation",
    model="humarin/chatgpt_paraphraser_on_T5_base",
    device=0,  # GPU
)

def paraphrase(text: str, n: int = 3) -> list[str]:
    outs = paraphraser(
        text,
        num_return_sequences=n,
        num_beams=n + 2,
        do_sample=True,
        temperature=0.8,
        max_length=128,
    )
    return [o["generated_text"] for o in outs]

src = "The customer was unhappy with the delivery time."
for p in paraphrase(src):
    print("-", p)
```

프로덕션에서는 원문당 2~3개의 패러프레이즈를 추가해 데이터셋을 3~4배 키우는 패턴이 흔합니다. 다만 원문과 지나치게 비슷한 샘플은 semantic dedup으로 다시 걸러내는 편이 좋습니다.

### Technique 4: 코드 증강은 AST 수준이 안전합니다

코드 코퍼스는 단어 치환보다 의미 보존이 더 중요합니다. 변수명 변경, dead-code insertion, 동치 연산 치환 같은 AST-level transform이 그래서 유용합니다.

```python
import ast, astor, random

class VarRenamer(ast.NodeTransformer):
    def __init__(self, mapping: dict[str, str]):
        self.mapping = mapping
    def visit_Name(self, node):
        if node.id in self.mapping:
            node.id = self.mapping[node.id]
        return node

def rename_vars(src: str) -> str:
    tree = ast.parse(src)
    names = sorted({n.id for n in ast.walk(tree) if isinstance(n, ast.Name)})
    mapping = {n: f"v{i}" for i, n in enumerate(names) if not n.startswith("__")}
    new_tree = VarRenamer(mapping).visit(tree)
    return astor.to_source(new_tree)

print(rename_vars("def add(a, b): return a + b"))
# def add(v0, v1): return v0 + v1
```

이 접근의 장점은 표면 토큰이 아니라 코드 의미에 모델을 더 민감하게 만든다는 점입니다. 특히 코드 생성·리뷰 데이터셋에서는 token-level 섞기가 오히려 해가 될 수 있습니다.

### 증강은 항상 평가로 닫아야 합니다

증강을 붙였다고 자동으로 성능이 좋아지지 않습니다. baseline과 augmented training을 나란히 비교해야 합니다.

```python
def evaluate_augmentation(model_class, train_orig, train_aug, val):
    m_base = model_class().fit(train_orig)
    m_aug = model_class().fit(train_orig + train_aug)
    return {
        "base_f1": m_base.score(val),
        "aug_f1": m_aug.score(val),
        "delta": m_aug.score(val) - m_base.score(val),
    }
```

`delta`가 작거나 음수라면 증강이 의미를 흔들었거나, 이미 데이터 분포가 충분했을 가능성이 큽니다. 이 경우 aug_p, paraphraser, 대상 클래스 선택부터 다시 봐야 합니다.

## 흔히 헷갈리는 지점

- **증강은 많이 할수록 좋습니다**: aug_p가 커질수록 라벨 의미가 깨질 수 있어 안전 구간을 실험으로 찾아야 합니다.
- **validation도 같이 증강하면 더 공정합니다**: 그것은 공정성이 아니라 누수입니다. 증강은 train-only가 원칙입니다.
- **영어용 EDA를 한국어에도 그대로 적용할 수 있습니다**: 한국어는 조사와 어순 때문에 단순 swap/delete가 의미를 더 쉽게 훼손합니다.
- **원문과 거의 같은 패러프레이즈도 많이 넣을수록 도움이 됩니다**: 유사도가 너무 높으면 데이터셋만 부풀고 정보량은 늘지 않습니다. 후처리 dedup이 필요합니다.

## 운영 체크리스트

- [ ] 증강 기법을 minority class 보강인지 강건성 향상인지 목적별로 분리해 적용한다
- [ ] aug_p와 paraphrase 개수를 validation 성능 기준으로 튜닝한다
- [ ] 증강 데이터는 train에만 넣고 validation/test는 원본으로 유지한다
- [ ] 원문과 증강 샘플의 semantic similarity를 측정해 과도한 near-duplicate를 제거한다
- [ ] 한국어·도메인별 의미 훼손 사례를 수집해 금지 규칙으로 문서화했다

## 정리

데이터 증강은 synthetic generation과 달리 기존 샘플의 라벨 의미를 유지한 채 분포를 넓히는 작업입니다. 따라서 가장 중요한 기준은 양이 아니라 의미 보존입니다.

EDA, back-translation, paraphrase model, AST transform은 각각 비용과 위험이 다릅니다. 텍스트 도메인인지 코드 도메인인지, 사실성이 중요한지 강건성이 중요한지에 따라 선택이 달라져야 합니다.

다음 글에서는 학습·검증·테스트 분할과 contamination 통제를 다룹니다. 좋은 증강도 올바른 split 위에 올라가야만 실제 성능 개선으로 이어집니다.

<!-- toc:begin -->
## 시리즈 목차

- [데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- [Tokenization과 Chunking 전략](./05-tokenization-chunking.md)
- [데이터 품질 필터링 — Heuristic과 Classifier](./06-quality-filtering.md)
- [합성 데이터 생성 — Self-Instruct부터 Distillation까지](./07-synthetic-data-generation.md)
- **데이터 증강 기법 — EDA부터 Back-Translation까지 (현재 글)**
- [학습/평가/테스트 분할과 Contamination 통제](./09-train-eval-test-splitting.md)
- [프로덕션 데이터 파이프라인 구축](./10-production-data-pipeline.md)
<!-- toc:end -->

## 참고 자료

### 공식 문서
- [EDA: Easy Data Augmentation Techniques (Wei & Zou, 2019)](https://arxiv.org/abs/1901.11196)
- [Improving Neural Machine Translation with Back-Translation (Sennrich et al., 2016)](https://arxiv.org/abs/1511.06709)
- [nlpaug - Data Augmentation for NLP](https://github.com/makcedward/nlpaug)
- [Helsinki-NLP OPUS-MT Models](https://huggingface.co/Helsinki-NLP)

### 관련 시리즈
- [LLM 파인튜닝 101 — 데이터셋 준비와 전처리](../../llm-finetuning-101/ko/02-dataset.md)
- [AI Evaluation 101 — LLM-as-Judge — 모델로 모델을 평가하기](../../ai-evaluation-101/ko/04-llm-as-judge.md)

Tags: Data Augmentation, EDA, Back-Translation, Paraphrase, nlpaug, KoNLPy
