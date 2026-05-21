---
episode: 8
language: en
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
  medium: true
  mkdocs: true
  tistory: false
title: "AI Data Preparation 101 (8/10): Data Augmentation - From EDA to Back-Translation"
seo_description: Augmentation is not about creating more rows. It is about choosing label-preserving train-only transforms that survive held-out evaluation.
---

# AI Data Preparation 101 (8/10): Data Augmentation - From EDA to Back-Translation

This is post 8 in the AI Data Preparation 101 series.

Data augmentation is not about inventing brand-new samples. It is about widening the training distribution while preserving the original label semantics. In practice, that means the important question is not “Which techniques exist?” but “Which technique fits this dataset problem, and does it survive held-out evaluation?”

To fix the weaknesses called out in issue #779, this chapter is rebuilt around one concrete augmentation decision path instead of a loose survey. It also repairs the untrustworthy AST rename example and makes the Korean-language warning operational by tying it to actual morphology-aware tooling and references.


![AI data preparation chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/08/08-01-big-picture.en.png)
*AI data preparation chapter 8 flow overview*

## Questions to Keep in Mind

- How is augmentation different from synthetic generation?
- What decision path should you follow for minority-class support and typo robustness?
- When should you choose EDA, back-translation, paraphrasing, or AST transforms?

## Why this chapter matters

Augmentation is especially useful when labeling budget is tight. It can improve minority-class recall and make a model more robust to typos, paraphrases, and other realistic variations. But if you also modify validation data, or if your transforms stop preserving meaning, the offline score may look cleaner while real generalization gets worse.

That is why augmentation should be treated as an operating procedure: **train-only transformation + held-out evaluation + stop/go decision**.

> Good augmentation does not maximize row count. It maximizes the number of transformed samples that still preserve the label strongly enough to survive evaluation.

## Start from one concrete dataset problem

Assume the following scenario.

- Task: Korean customer-support intent classification
- Labels: `refund_delay`, `cancel_plan`, `outage_question`, `feature_request`
- Current problem 1: `refund_delay` has only 280 examples and is the weakest class
- Current problem 2: real user messages contain typos and colloquial wording, so robustness is weak on a held-out slice
- Fixed rule: validation and test sets must remain untouched

Given that setup, the decision path should look like this.

1. Freeze the held-out validation slice first.
2. Measure whether minority-class recall or typo robustness is the bigger failure.
3. Try the most label-preserving augmentation family first.
4. Keep only rows that pass semantic dedup and train-only guardrails.
5. Stop if the held-out metrics do not improve.

## Freeze the baseline and held-out slices first

You cannot judge augmentation without a baseline. Capture the decision metrics before you create a single new row.

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

The key here is not to rely on macro F1 alone. The decision should be anchored to the exact slices you want to improve. In this scenario, `refund_delay_recall` and `typo_slice_f1` are the operator metrics that matter.

## Which augmentation family should go first?

Do not mix everything at once.

| Technique | First choice? | Why |
| --- | --- | --- |
| EDA | Only in a limited role | It is fast, but it can easily break Korean particles and word order. |
| Back-translation | Conditional | It produces natural rewrites, but entity or number drift is risky. |
| Paraphrase model | First choice here | It is the clearest way to expand minority-class wording variation. |
| AST transform | Only for code data | It preserves semantics well for code corpora, not for this text classifier. |

For this scenario, the first goal is to widen expression coverage for `refund_delay`, so the first experiment is **paraphrasing plus Korean-specific guardrails**. If typo robustness still lags after that, we add a small amount of character-level noise as a separate slice experiment. English-centric EDA applied blindly to full Korean sentences is not the default.

## Korean guardrails are safer at the morpheme level

Korean particles and endings can shift meaning quickly. So instead of random swap/delete on raw whitespace tokens, it is safer to inspect morphological tags and protect function-like tokens from replacement.

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

Even a small rule like this prevents many failures where particles or sentence endings are deleted and the label meaning drifts. This is the operational form of the Korean-language warning from issue #779, and KoNLPy is the concrete tool that supports it.

## Concrete workflow: paraphrase the minority class first

The example below selects only the minority class, generates paraphrases, and keeps only rows that pass semantic dedup and banned-pattern rules.

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

This workflow rejects both kinds of bad candidates: rows that changed meaning too much and rows that are so similar they add almost no information. Augmentation is not a contest to keep more rows. It is a filter for keeping only the rows that still deserve to be in train.

## Handle typo robustness as a separate slice

If typo robustness still matters after the minority-class pass, treat it as a separate experiment rather than mixing it into every transformed row.

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

Keep this slice small and train-only. If you push it too broadly, the model may start learning broken text distribution rather than realistic robustness.

## Use held-out evaluation to make the stop/go call

Augmentation should end in evaluation, not intuition.

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

One plausible result table for this scenario would look like this.

| Experiment | macro_f1 | refund_delay_recall | typo_slice_f1 | Decision |
| --- | ---: | ---: | ---: | --- |
| baseline | 0.812 | 0.611 | 0.584 | baseline |
| paraphrase + Korean guardrail | 0.826 | 0.691 | 0.603 | Go |
| + aggressive EDA (`aug_p=0.3`) | 0.804 | 0.676 | 0.597 | Stop |

The message is simple. Paraphrasing helped. Aggressive EDA hurt the held-out metrics and should be discarded. In augmentation work, the stop/go decision matters more than the fact that multiple techniques are available.

## AST transforms belong to code data, and the rename example must be trustworthy

Issue #779 correctly pointed out that the earlier AST rename snippet was not trustworthy because the output comment did not match what the code actually changed. The fixed version below renames both `ast.arg` and `ast.Name`, so the example output is accurate.

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

This branch is still important because it shows that for code corpora, AST-level changes preserve semantics far better than token edits. But it is a separate branch because the current scenario is about Korean text classification, not code generation.

## Common points of confusion

- **Augmenting validation makes evaluation more realistic**: no. That is leakage.
- **English-style EDA can be applied to Korean as-is**: no. Without particle and ending protection, meaning breaks fast.
- **Higher semantic similarity always means a better row**: no. Too high usually means near-duplicate.
- **Mixing more techniques always improves performance**: no. Every technique still needs its own held-out stop/go decision.

## Operational checklist

- [ ] Freeze baseline and held-out slice metrics before augmentation starts
- [ ] Keep augmentation train-only and leave validation/test untouched
- [ ] Separate minority-class support experiments from typo-robustness experiments
- [ ] Remove meaning-breaking rows and near-duplicates with semantic-similarity and banned-pattern rules
- [ ] For Korean data, protect morphology-sensitive tokens and limit candidates with a tool such as KoNLPy
- [ ] Discard the augmentation batch if held-out metrics do not improve

## Summary

The core of augmentation is not the list of technique names. It is the decision flow: define the dataset problem, add train-only guardrails, and keep only the transformations that improve held-out metrics.

In this scenario, paraphrasing with Korean guardrails improved both `refund_delay` recall and typo robustness, while aggressive EDA made the model worse. AST transforms remain useful, but only in their proper branch: code data where syntax-aware edits preserve meaning.

Next, we will look at the split discipline that must follow generation and augmentation alike: train/eval/test separation and contamination control.

## Answering the Opening Questions

- **How is augmentation different from synthetic generation?**
  - The article treats Data Augmentation - From EDA to Back-Translation as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What decision path should you follow for minority-class support and typo robustness?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **When should you choose EDA, back-translation, paraphrasing, or AST transforms?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [AI Data Preparation 101 (1/10): Why Data Preparation Determines Model Quality](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): Source Data Collection and Cataloging](./02-source-data-collection-cataloging.md)
- [AI Data Preparation 101 (3/10): Cleaning and Deduplication](./03-cleaning-deduplication.md)
- [AI Data Preparation 101 (4/10): PII Detection and Anonymization for Training Data](./04-pii-detection-anonymization.md)
- [AI Data Preparation 101 (5/10): Tokenization and Chunking Strategies](./05-tokenization-chunking.md)
- [AI Data Preparation 101 (6/10): Quality Filtering - Heuristics and Classifiers](./06-quality-filtering.md)
- [AI Data Preparation 101 (7/10): Synthetic Data Generation - From Self-Instruct to Distillation](./07-synthetic-data-generation.md)
- **Data Augmentation - From EDA to Back-Translation (current)**
- Train/Eval/Test Splitting and Contamination Control (upcoming)
- Building a Production Data Pipeline (upcoming)

<!-- toc:end -->

## References

### Official documentation and tools
- [KoNLPy documentation](https://konlpy.org/en/latest/)
- [KoNLPy: Korean natural language processing in Python (Park & Cho, 2014)](http://dmlab.snu.ac.kr/~lucypark/docs/2014-10-10-hclt.pdf)
- [nlpaug - Data Augmentation for NLP](https://github.com/makcedward/nlpaug)
- [Helsinki-NLP OPUS-MT Models](https://huggingface.co/Helsinki-NLP)

### Papers and implementation references
- [EDA: Easy Data Augmentation Techniques (Wei & Zou, 2019)](https://arxiv.org/abs/1901.11196)
- [Improving Neural Machine Translation with Back-Translation (Sennrich et al., 2016)](https://arxiv.org/abs/1511.06709)
- [Sentence-Transformers: Multilingual MiniLM](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)

Tags: Data Augmentation, EDA, Back-Translation, Paraphrase, nlpaug, KoNLPy
