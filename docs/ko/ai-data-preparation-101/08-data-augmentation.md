---
episode: 8
language: ko
last_reviewed: '2026-05-03'
series: ai-data-preparation-101
status: content-ready
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

> AI Data Preparation 101 시리즈 (8/10)

---
<!-- a-grade-intro:begin -->
## 핵심 질문

EDA·Back-Translation 같은 증강 기법을 어떻게 골라야 일반화에 도움이 될까요?

이 글은 그 질문에 답하기 위해 데이터 증강의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## "Synthetic generation과 Augmentation은 뭐가 다른가요?"

지난 편의 synthetic data generation은 LLM을 호출해 새 sample을 "처음부터" 만들었습니다. 이번 편의 augmentation은 기존 sample을 "변형"해 학습 분포를 넓히는 기법입니다. cost가 훨씬 싸고 controlled한 변형이 가능합니다.

augmentation은 주로 두 가지 목적으로 씁니다.

1. **분류 모델 (NLU)**: minority class를 늘려 class imbalance 완화
2. **robustness**: typo, paraphrase, code-switching에 강한 모델 학습

이번 편은 4가지 기법을 단계별로 소개합니다.

## 기법 1 — EDA (Easy Data Augmentation)

가장 단순한 token-level 변형 4가지: synonym replacement, random insertion, random swap, random deletion. 영어 NLU baseline에서 1~2점 정확도 향상이 보고되었습니다.

```python
# pip install nlpaug
import nlpaug.augmenter.word as naw

# 1) Synonym replacement (WordNet 기반)
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

`aug_p`(변형 비율)는 0.1~0.2가 안전합니다. 0.3을 넘기면 문장 의미가 바뀝니다.

## 기법 2 — Back-translation

원문 -> 다른 언어 -> 원문으로 두 번 번역하면 의미는 유지하면서 표현이 달라진 paraphrase가 만들어집니다.

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

pivot language를 여러 개(de, fr, ja) 돌리면 다양성이 더 늘어납니다. 단, machine translation의 품질에 의존하므로 fact-critical (예: medical) domain에서는 위험합니다.

## 기법 3 — Paraphrase model

T5 또는 PEGASUS 기반 paraphrase 전용 모델을 호출합니다. back-translation보다 빠르고 더 자연스럽습니다.

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

production에서 흔히 쓰는 패턴: train sample마다 paraphrase 2~3개 추가 -> dataset 3~4배. validation에는 augmented sample을 절대 넣지 않습니다.

## 기법 4 — 한국어 특화 augmentation

한국어는 조사 변경, 어순 재배치, 형태소 단위 동의어 치환이 효과적입니다.

```python
# pip install konlpy
from konlpy.tag import Okt
import random

okt = Okt()

JOSA_PAIRS = {"이": "가", "가": "이", "은": "는", "는": "은", "을": "를", "를": "을"}

def josa_swap(text: str, p: float = 0.3) -> str:
    tokens = okt.pos(text, norm=False, stem=False)
    out = []
    for word, tag in tokens:
        if tag == "Josa" and word in JOSA_PAIRS and random.random() < p:
            out.append(JOSA_PAIRS[word])
        else:
            out.append(word)
    return "".join(out)

src = "고양이가 매트 위에 앉았다."
print(josa_swap(src))  # 일부 josa가 swap됨

# 형태소 단위 synonym (간단 버전)
SYNONYMS = {"고양이": ["냥이", "묘"], "앉았다": ["앉아 있다"]}
def morph_synonym(text: str, p: float = 0.2) -> str:
    tokens = okt.morphs(text)
    out = []
    for t in tokens:
        if t in SYNONYMS and random.random() < p:
            out.append(random.choice(SYNONYMS[t]))
        else:
            out.append(t)
    return " ".join(out)
```

한국어는 띄어쓰기와 조사가 의미에 직결되므로 EDA처럼 random word shuffle을 그대로 쓰면 sentence가 깨집니다. 형태소 단위로 분해해 변형해야 합니다.

## 평가 — augmentation이 실제로 도움이 됐는가

augmentation 전후로 metric을 비교합니다. validation은 절대 augment하지 않습니다.

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

delta가 음수거나 0.005 미만이면 augmentation이 noise일 가능성이 높습니다. aug_p나 paraphrase model을 바꿔봅니다.

## 흔한 실수 5가지

1. **Validation set에 augment 적용**: data leakage입니다. augmentation은 train에만 적용합니다.
2. **aug_p를 0.3 이상으로**: 문장 의미가 바뀌어 label이 더 이상 맞지 않을 수 있습니다.
3. **Back-translation을 fact-critical domain에 적용**: medical, legal text에서 숫자나 entity가 변할 수 있습니다.
4. **EDA를 한국어에 그대로**: random word swap은 한국어 어순/조사 체계를 무시합니다. 형태소 단위 augmentation이 필요합니다.
5. **Paraphrase 후 dedup 안 함**: 원본과 거의 같은 paraphrase가 dataset의 절반을 차지할 수 있습니다. semantic dedup으로 0.95 이상 유사한 sample은 제거합니다.

## 핵심 요약

- EDA는 synonym/insert/swap/delete 4가지 token-level 변형의 baseline입니다.
- Back-translation은 pivot language를 거쳐 자연스러운 paraphrase를 만듭니다.
- Paraphrase model은 T5/PEGASUS 기반으로 더 빠르고 깔끔합니다.
- 한국어는 josa swap과 형태소 단위 synonym이 효과적입니다.
- aug_p는 0.1~0.2가 안전 zone입니다.
- Validation은 절대 augment하지 않습니다.
- 다음 편(9편)은 train/eval/test split와 contamination 통제입니다.
## 참고 자료

- [EDA: Easy Data Augmentation Techniques (Wei & Zou, 2019)](https://arxiv.org/abs/1901.11196)
- [Improving Neural Machine Translation with Back-Translation (Sennrich et al., 2016)](https://arxiv.org/abs/1511.06709)
- [nlpaug - Data Augmentation for NLP](https://github.com/makcedward/nlpaug)
- [KoNLPy - Korean Morphological Analysis](https://konlpy.org/)
