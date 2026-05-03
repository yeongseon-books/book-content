---
title: Data Augmentation Techniques
series: ai-data-preparation-101
episode: 8
language: en
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Data Augmentation
- EDA
- Back-Translation
- Paraphrase
- nlpaug
- AST Transform
last_reviewed: '2026-05-03'
---

# Data Augmentation - From EDA to Back-Translation

> AI Data Preparation 101 series (8/10)

---
## "How is augmentation different from synthetic generation?"

The previous episode generated samples "from scratch" by calling an LLM. Augmentation instead "transforms" existing samples to broaden the training distribution. It is far cheaper and allows controlled transformations.

Augmentation is mainly used for two purposes.

1. **Classification models (NLU)**: grow minority classes to ease class imbalance
2. **Robustness**: train models robust to typos, paraphrases, and code-switching

This episode covers 4 techniques.

## Technique 1 - EDA (Easy Data Augmentation)

The simplest 4 token-level transforms: synonym replacement, random insertion, random swap, random deletion. Reported 1-2 point accuracy gains on English NLU baselines.

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

`aug_p` (transform rate) is safe at 0.1-0.2. Past 0.3 the meaning shifts.

## Technique 2 - Back-translation

Translate text -> another language -> back to the original. Meaning is preserved while wording changes - a paraphrase is born.

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

Cycling through multiple pivots (de, fr, ja) further increases diversity. But it depends on MT quality, so it is risky in fact-critical (e.g. medical) domains.

## Technique 3 - Paraphrase model

Call a T5- or PEGASUS-based dedicated paraphraser. Faster and more natural than back-translation.

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

Common production pattern: add 2-3 paraphrases per train sample -> dataset grows 3-4x. Never put augmented samples into validation.

## Technique 4 - Code augmentation

For code corpora, AST-level transforms preserve semantics better than token-level edits.

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

Variable renaming, dead-code insertion, and equivalent operator substitution (`a + 1` -> `a - (-1)`) are all valid. The model learns code semantics rather than surface tokens.

## Evaluation - did augmentation actually help?

Compare metrics with and without augmentation. Never augment validation.

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

If delta is negative or below 0.005, augmentation is likely just noise. Try a different aug_p or paraphraser.

## 5 common mistakes

1. **Augmenting the validation set**: this is data leakage. Augmentation is train-only.
2. **Setting aug_p above 0.3**: meaning shifts, and labels may no longer hold.
3. **Back-translation in fact-critical domains**: medical or legal text can have numbers or entities altered.
4. **Applying English EDA to Korean as-is**: random word swap ignores Korean word order and particles. Use morphological augmentation.
5. **Skipping post-paraphrase deduplication**: paraphrases nearly identical to the source can balloon the dataset. Drop samples with >0.95 semantic similarity.

## Key Takeaways

- EDA is the baseline of 4 token-level transforms: synonym, insert, swap, delete.
- Back-translation creates natural paraphrases via a pivot language.
- Paraphrase models (T5/PEGASUS) are faster and cleaner.
- For code, AST-level transforms (var rename, dead-code insertion) preserve semantics.
- aug_p of 0.1-0.2 is the safe zone.
- Never augment validation data.
- Episode 9 covers train/eval/test splitting and contamination control.

---

<!-- toc:begin -->
## AI Data Preparation 101 series

- [Why Data Preparation Determines Model Quality](./01-why-data-preparation-matters.md)
- [Source Data Collection and Cataloging](./02-source-data-collection-cataloging.md)
- [Cleaning and Deduplication](./03-cleaning-deduplication.md)
- [PII Detection and Anonymization for Training Data](./04-pii-detection-anonymization.md)
- [Tokenization and Chunking Strategies](./05-tokenization-chunking.md)
- [Quality Filtering - Heuristics and Classifiers](./06-quality-filtering.md)
- [Synthetic Data Generation - From Self-Instruct to Distillation](./07-synthetic-data-generation.md)
- **Data Augmentation - From EDA to Back-Translation (current)**
- Train/Eval/Test Splitting and Contamination Control (upcoming)
- Building a Production Data Pipeline (upcoming)
<!-- toc:end -->

## References

- [EDA: Easy Data Augmentation Techniques (Wei & Zou, 2019)](https://arxiv.org/abs/1901.11196)
- [Improving Neural Machine Translation with Back-Translation (Sennrich et al., 2016)](https://arxiv.org/abs/1511.06709)
- [nlpaug - Data Augmentation for NLP](https://github.com/makcedward/nlpaug)
- [Helsinki-NLP OPUS-MT Models](https://huggingface.co/Helsinki-NLP)

Tags: Data Augmentation, EDA, Back-Translation, Paraphrase, nlpaug, AST Transform
