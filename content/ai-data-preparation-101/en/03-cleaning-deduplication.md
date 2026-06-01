---
title: "AI Data Preparation 101 (3/10): Cleaning and Deduplication"
series: ai-data-preparation-101
episode: 3
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Data Preparation
- Cleaning
- Deduplication
- MinHash
last_reviewed: '2026-05-14'
seo_description: 'Anyone who has worked on The Pile, C4, or RedPajama will tell you
  the same thing: the dedup stage delivers the biggest single quality improvement.'
---

# AI Data Preparation 101 (3/10): Cleaning and Deduplication

Teams that have processed large corpora tend to agree on one point: deduplication is one of the highest-leverage quality steps in the pipeline. You can change nothing about the model and still see better results by cleaning and removing repeated data correctly.

This is the 3rd post in the AI Data Preparation 101 series. Here we cover the basic cleaning transforms for raw text and the deduplication methods that keep training quality honest.


![AI data preparation chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/03/03-01-big-picture.en.png)
*AI data preparation chapter 3 flow overview*

> Cleaning and deduplication are not chores you do before the real work — they are the real work, and skipping them is how training compute gets burned on noise the model then memorizes.

## Questions to Keep in Mind

- Which text-cleaning transforms are worth keeping because they solve measurable problems?
- Why is exact dedup not enough for web-scale corpora?
- How should you tune MinHash thresholds without creating too many false positives?

## "Is Deduplication Really That Important?"

Anyone who has worked on The Pile, C4, or RedPajama will tell you the same thing: **the dedup stage delivers the biggest single quality improvement**. Lee et al. (2021) showed in "Deduplicating Training Data Makes Language Models Better" that removing as little as 1% of duplicates lowers perplexity meaningfully.

Duplicates are not just wasted disk. The model trains repeatedly on identical patterns, loses generalization, and if duplicates leak into the eval set, your metrics inflate. This episode covers two stages: cleaning and deduplication.

## Cleaning — Six Basic Transforms

The six most common problems in raw text and the code that handles them.

```python
import re
import unicodedata
from html import unescape

def clean_text(text: str) -> str:
    if not text:
        return ""
    # 1. Encoding normalization (NFC: combine Hangul jamo)
    text = unicodedata.normalize("NFC", text)
    # 2. HTML entity decode
    text = unescape(text)
    # 3. HTML tag removal
    text = re.sub(r"<[^>]+>", " ", text)
    # 4. Control characters (keep tab/newline)
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or ord(ch) >= 32)
    # 5. Collapse runs of whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 6. Strip
    return text.strip()

# Test
samples = [
    "<p>Hello&nbsp;<b>world</b>!</p>",
    "Hello\u200b\u200bworld",  # zero-width space
    "Multi   spaces\n\n\n\nlines",
]
for s in samples:
    print(repr(clean_text(s)))
```

Each step targets one measurable problem (encoding breakage, HTML residue, control characters, whitespace noise). **Do not add ad-hoc transforms.** A long cleaning function is hard to debug and quietly destroys information.

## Cleaning Diff Metrics

Whenever you change the cleaning function, measure these.

```python
def cleaning_diff(before: list[str], after: list[str]) -> dict:
    return {
        "rows_in": len(before),
        "rows_out": sum(1 for t in after if t),  # exclude empty
        "avg_len_before": sum(len(t) for t in before) / max(len(before), 1),
        "avg_len_after": sum(len(t) for t in after) / max(len(after), 1),
        "char_reduction_pct": (
            1 - sum(len(t) for t in after) / max(sum(len(t) for t in before), 1)
        ) * 100,
    }
```

If total characters drop more than 5%, suspect a bug. Heavy-HTML corpora often see 10-20%, but clean text should land in the 1-2% range.

## Deduplication — Three Stages

Apply dedup in cost order.

1. **Exact dedup** (sha256): identical documents. O(N) hashmap.
2. **Near-exact dedup** (MinHash + LSH): documents that are 90%+ similar. O(N) approximate.
3. **Semantic dedup** (embedding): paraphrases. O(N²) or O(N log N) with ANN.

Most production pipelines need only stage 1 and stage 2.

### Stage 1: Exact Dedup

```python
import hashlib

def exact_dedup(docs: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for doc in docs:
        # Normalize before hashing (ignore whitespace differences)
        norm = re.sub(r"\s+", " ", doc.strip().lower())
        h = hashlib.sha256(norm.encode("utf-8")).hexdigest()
        if h not in seen:
            seen.add(h)
            out.append(doc)
    return out
```

**Critical detail**: normalize before hashing or trivial whitespace differences look like distinct documents.

### Stage 2: MinHash + LSH

For long documents that differ by a few lines (very common in web crawls), MinHash is essential.

```python
from datasketch import MinHash, MinHashLSH

def make_minhash(text: str, num_perm: int = 128) -> MinHash:
    m = MinHash(num_perm=num_perm)
    # 5-gram word shingles
    words = text.lower().split()
    for i in range(len(words) - 4):
        shingle = " ".join(words[i:i+5])
        m.update(shingle.encode("utf-8"))
    return m

def near_dedup(docs: list[str], threshold: float = 0.85) -> list[str]:
    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    keep: list[int] = []
    for i, doc in enumerate(docs):
        mh = make_minhash(doc)
        if not lsh.query(mh):  # nothing similar yet, keep
            lsh.insert(str(i), mh)
            keep.append(i)
    return [docs[i] for i in keep]

# Example
docs = [
    "The quick brown fox jumps over the lazy dog repeatedly today.",
    "The quick brown fox jumps over the lazy dog repeatedly today!",  # near-dup
    "Completely different content about machine learning and data.",
]
print(len(near_dedup(docs)))  # -> 2
```

`threshold=0.85` treats Jaccard similarity above 85% as duplicate. Tune empirically. Drop to 0.7 and false positives rise (different docs marked equal); push to 0.95 and you miss real near-dups.

### Stage 3: Semantic Dedup (optional)

If you also need to catch paraphrases, use embedding similarity.

```python
# pip install sentence-transformers faiss-cpu
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def semantic_dedup(docs: list[str], threshold: float = 0.93) -> list[str]:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embs = model.encode(docs, normalize_embeddings=True).astype("float32")
    index = faiss.IndexFlatIP(embs.shape[1])  # inner product = cosine on normalized
    keep: list[int] = []
    for i, e in enumerate(embs):
        if index.ntotal > 0:
            scores, _ = index.search(e.reshape(1, -1), 1)
            if scores[0][0] >= threshold:
                continue  # near-paraphrase, skip
        index.add(e.reshape(1, -1))
        keep.append(i)
    return [docs[i] for i in keep]
```

Semantic dedup is expensive (embedding pass plus ANN index). Consider it only when the training set is under 100M rows.

## Train/Eval Cross-Dedup — The Step That Matters Most

Overlap between train and eval breaks evaluation metrics.

```python
def cross_dedup(train: list[str], eval_set: list[str],
                threshold: float = 0.85) -> tuple[list[str], int]:
    """Remove train rows that overlap eval_set. Returns also count removed."""
    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    for i, doc in enumerate(eval_set):
        lsh.insert(f"eval_{i}", make_minhash(doc))
    clean_train: list[str] = []
    removed = 0
    for doc in train:
        if lsh.query(make_minhash(doc)):
            removed += 1
            continue
        clean_train.append(doc)
    return clean_train, removed
```

**Never modify the eval set.** Always remove from train. That keeps the metric definition stable.

## Order of Operations Matters

Cleaning and dedup follow a strict order.

1. raw → clean
2. clean → exact dedup
3. exact-deduped → near dedup (MinHash)
4. near-deduped → split (train/eval/test)
5. after split → cross-dedup train against eval

Dedup before cleaning lets whitespace-different copies survive as distinct. Cross-dedup before splitting leaves you with no clean rule for which side to drop from.

## Recording Before/After Samples with Quality Metrics

The fastest way to break team consensus on cleaning rules is arguing about whether a rule "improved" things. Instead of debating, show before/after samples alongside hard numbers.

```python
import pandas as pd


def summarize_before_after(raw_df: pd.DataFrame, clean_df: pd.DataFrame) -> dict:
    raw_text = raw_df["text"].astype(str)
    clean_text = clean_df["text"].astype(str)
    return {
        "raw_rows": len(raw_df),
        "clean_rows": len(clean_df),
        "row_drop_ratio": 1 - len(clean_df) / max(len(raw_df), 1),
        "raw_dup_ratio": 1 - raw_text.nunique() / max(len(raw_text), 1),
        "clean_dup_ratio": 1 - clean_text.nunique() / max(len(clean_text), 1),
        "raw_avg_len": float(raw_text.str.len().mean()),
        "clean_avg_len": float(clean_text.str.len().mean()),
    }


SAMPLE_BEFORE = "<div>Ad inquiry 010-1111-2222</div>\n\nSign up now for 50% off"
SAMPLE_AFTER = "Sign up now for 50% off"
```

**Before/After example**

```text
before: <div>Ad inquiry 010-1111-2222</div>

        Sign up now for 50% off
after : Sign up now for 50% off
```

When you attach samples like this, objections like "the numbers look better but meaning got destroyed" become immediately verifiable rather than speculative.

## MinHash Threshold Tuning Procedure

Picking a MinHash threshold by gut feel causes false positives and false negatives to rise together. In practice, you fix the threshold using hand-labeled pair samples first.

```python
CANDIDATE_THRESHOLDS = [0.75, 0.80, 0.85, 0.90]


# hand_labeled_pairs: List[(doc_a, doc_b, is_duplicate)]
def evaluate_threshold(hand_labeled_pairs, near_dup_fn):
    out = []
    for th in CANDIDATE_THRESHOLDS:
        tp = fp = fn = 0
        for a, b, y in hand_labeled_pairs:
            pred = near_dup_fn(a, b, threshold=th)
            if pred and y:
                tp += 1
            elif pred and not y:
                fp += 1
            elif (not pred) and y:
                fn += 1
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        out.append({"threshold": th, "precision": precision, "recall": recall})
    return out
```

The operational default usually favors precision slightly over recall. Incorrectly removing a non-duplicate causes immediate information loss, while missing a true duplicate only inflates storage and slightly skews training distribution.

## Versioning Dedup Results with DVC

Cleaning and dedup produce large artifacts with frequent reruns—too heavy for Git alone. Pairing DVC with Git ties data versions to code commits.

```bash
dvc add data/clean/train_dedup.parquet
git add data/clean/train_dedup.parquet.dvc dvc.lock dvc.yaml
git commit -m "Add deduplicated train set v1.3"
```

```yaml
stages:
  clean_dedup:
    cmd: python pipelines/clean_dedup.py --input data/raw/train.parquet --output data/clean/train_dedup.parquet
    deps:
      - pipelines/clean_dedup.py
      - data/raw/train.parquet
    outs:
      - data/clean/train_dedup.parquet
    metrics:
      - reports/clean_dedup_metrics.json
```

With this setup, "why did row count drop 12% since yesterday?" becomes answerable by checking out the previous DVC version and diffing the metrics JSON.

## Data Cleaning Validation Schema

If you only save cleaning results as a free-form JSON, missing fields go unnoticed until something downstream breaks. A validation schema catches quality regressions early.

```python
from pydantic import BaseModel, Field


class CleaningMetrics(BaseModel):
    raw_rows: int = Field(ge=1)
    clean_rows: int = Field(ge=1)
    raw_dup_ratio: float = Field(ge=0.0, le=1.0)
    clean_dup_ratio: float = Field(ge=0.0, le=1.0)
    row_drop_ratio: float = Field(ge=0.0, le=1.0)
    minhash_threshold: float = Field(ge=0.5, le=0.99)


class CleaningGate(BaseModel):
    max_row_drop_ratio: float = 0.30
    max_clean_dup_ratio: float = 0.08


def pass_gate(metrics: CleaningMetrics, gate: CleaningGate) -> bool:
    return (
        metrics.row_drop_ratio <= gate.max_row_drop_ratio
        and metrics.clean_dup_ratio <= gate.max_clean_dup_ratio
    )
```

## Duplicate-Rate Comparison Table

| Stage | Dup Ratio | Notes |
| --- | ---: | --- |
| raw | 0.31 | Many footer copies from crawling |
| clean + exact dedup | 0.14 | Whitespace/case differences removed |
| + MinHash near dedup | 0.06 | Similar-doc clusters collapsed |
| post-split train/eval cross-dedup | 0.00 (cross) | Evaluation contamination prevented |

Reporting cross-duplicate rate as a separate line item is what lets you actually explain evaluation reliability to stakeholders.

## Inspection Questions for Immediate Ops Use

These questions come up in every pre-release review. The point is not to recite them—it is to answer each one with a file path or metric value on the spot.

1. Which version did this dataset come from, and what is its sha256?
2. How much did duplicate/null/length distributions shift compared to the last batch?
3. Which samples were removed, by which rule, and what are the top removal reasons?
4. What is the measured leakage rate at the train/eval/test boundary?
5. How many samples did a human review this batch, and what error types were found?

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

Even if your ops team does not use this exact function, they need the same concept implemented as a pipeline gate. The key principle: never judge readiness by feel.

## Production Log Example

```text
[release-check] dataset=v2.4.1 sha=4fb1...
[release-check] duplicate_ratio=0.061 null_ratio=0.008
[release-check] contamination_ratio=0.004 human_reviewed_rows=240
[release-check] status=PASS
```

When model performance wobbles, this single log block lets you quickly rule out (or zero in on) the data preparation stage. Data quality shows itself not in a single essay, but in repeatable verification logs like this.

### Dedup Failure Recovery Rules

If near-dedup over-fires and removes too many documents, roll back immediately to the previous DVC artifact and re-run with the threshold raised one step. Record both the rollback rationale and the re-run results in the same report so the decision history is preserved.

### Minimum Items for Release Notes

Every cleaning/dedup change must appear in release notes with at least four items: the changed rule, the number of affected rows, the key metric delta, and the rollback path. Without these, the next batch operator will repeat the same judgment from scratch.

When threshold changes, always include a comparison table against the previous batch. Maintain weekly sample-based manual review to catch over-deletion regressions early. Re-evaluate cleaning criteria quarterly to keep up with domain drift.

## Common Mistakes

1. **Cleaning function with too many transforms**: Past 10 regexes in one function, debugging is impossible. Split into small steps with per-stage logging.
2. **Stopping after exact dedup**: Web crawls produce thousands of docs that differ only in a single ad line or timestamp. The MinHash stage is mandatory.
3. **Skipping cross-dedup**: Train/eval leakage inflates metrics by 5-10 points. Run cross-dedup against every eval set.
4. **Using MinHash threshold default 0.5**: datasketch's default is too permissive. 0.85-0.9 is the safe starting point for general text.
5. **Not measuring cleaning impact**: A new regex can erase 30% of your data unnoticed. Check `char_reduction_pct` every time.

## Key Takeaways

- Cleaning handles six measurable problems (encoding, HTML, control chars, whitespace, etc.). No ad-hoc transforms.
- Dedup runs in three stages (exact → MinHash → semantic). Stages 1-2 are usually enough for production.
- Train/eval cross-dedup decides whether your evaluation metric is trustworthy. Always remove from train only.
- Order: clean → exact dedup → near dedup → split → cross-dedup against eval.
- Log row counts and `char_reduction_pct` at every stage automatically.
- Episode 4 covers PII detection and anonymization.

---

## Operational checklist

- [ ] Keep cleaning transforms small enough that each one targets an explainable noise pattern
- [ ] Log rows in/out and character reduction whenever cleaning rules change
- [ ] Normalize text before hashing so exact dedup catches whitespace-only variants
- [ ] Run MinHash near-dedup before splitting the corpus
- [ ] Cross-dedup train against every evaluation set and delete only from train

## Answering the Opening Questions

- **Why should a cleaning function be maintained as a composition of small transforms?**
  - Splitting `clean_text()` into NFC normalization, HTML removal, and control-character stripping lets you immediately narrow down which step caused a spike in `char_reduction_pct`. A monolithic cleaner makes it impossible to explain how much data each rule removed.
- **Why can't exact dedup alone solve web-corpus quality problems?**
  - `exact_dedup()` catches whitespace and case differences, but pages differing by a single ad line or punctuation mark survive intact. That is why the article immediately follows with `MinHashLSH` and `near_dedup(docs, threshold=0.85)`.
- **What errors arise from setting the MinHash threshold too low or too high?**
  - A threshold that is too low treats distinct documents as duplicates (false positives increase); one that is too high misses near-duplicates (false negatives increase). The article therefore recommends starting around 0.85–0.9 and validating with hand-labeled pairs for both precision and recall.
<!-- toc:begin -->
## In this series

- [AI Data Preparation 101 (1/10): Why Data Preparation Determines Model Quality](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): Source Data Collection and Cataloging](./02-source-data-collection-cataloging.md)
- **Cleaning and Deduplication (current)**
- PII Detection and Anonymization for Training Data (upcoming)
- Tokenization and Chunking Strategies (upcoming)
- Quality Filtering - Heuristics and Classifiers (upcoming)
- Synthetic Data Generation - From Self-Instruct to Distillation (upcoming)
- Data Augmentation - From EDA to Back-Translation (upcoming)
- Train/Eval/Test Splitting and Contamination Control (upcoming)
- Building a Production Data Pipeline (upcoming)

<!-- toc:end -->

## References

- [Deduplicating Training Data Makes Language Models Better (Lee et al., 2021)](https://arxiv.org/abs/2107.06499)
- [datasketch - MinHash and LSH library](https://ekzhu.com/datasketch/)
- [The Pile paper - dedup methodology](https://arxiv.org/abs/2101.00027)
- [ftfy - fixes text for you](https://ftfy.readthedocs.io/)

Tags: Data Preparation, Cleaning, Deduplication, MinHash
