---
series: computer-science-101
episode: 10
title: "Computer Science 101 (10/10): From CS to AI and Data Science"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - AI
  - Data Science
  - Machine Learning
  - Statistics
  - Career
seo_description: How CS fundamentals connect to AI and data science, plus a learning roadmap — the closing article of the CS 101 series.
last_reviewed: '2026-05-15'
---

# Computer Science 101 (10/10): From CS to AI and Data Science

AI and data science did not arrive from some separate universe. They sit on top of data representation, algorithmic cost, memory hierarchy, databases, and engineering habits, with statistics and domain knowledge added on top.

This is the final post in the Computer Science 101 series.

In this article, we'll connect the previous nine posts to machine learning and data science work, then turn that map into a concrete study roadmap.

## Questions to Keep in Mind

- What boundary should you inspect first when applying From CS to AI and Data Science?
- Which signal should the example or diagram make visible for From CS to AI and Data Science?
- What failure should be prevented first when From CS to AI and Data Science reaches a real system?

## Big Picture

![Computer Science 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/10/10-01-concept-at-a-glance.en.png)

*Computer Science 101 chapter 10 flow overview*

This picture places From CS to AI and Data Science inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of From CS to AI and Data Science is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions This Article Answers

- Where do the CS fundamentals from this series show up directly in AI and data science?
- What is the core difference between rule-based systems and machine-learning systems?
- Why are training, inference, and data validation still computation and systems problems?
- Why do AI systems need the same testing, monitoring, and cost awareness as any other service?
- What should you study next if you want to keep going toward AI/DS?

## What You Will Learn

- The basics of machine learning (training, inference, features, models)
- The difference between rule-based and ML-based systems
- How the previous nine articles connect to AI/DS
- A recommended learning roadmap for what comes next

## Why It Matters

AI is not magic. Models are trained on data, inference is matrix arithmetic, and all of it ultimately runs on CPU, memory, and disk. The stronger your CS foundation, the faster you grow at debugging AI code, estimating cost, and framing problems.

> AI/DS = CS + statistics + domain.

Tools change quickly; foundations stay valid for a long time.

## Concept at a Glance

> A rule-based system has humans write the rules. Machine learning infers the rules from data.

## Key Terms

| Term | Description |
| --- | --- |
| Machine learning | A technique that learns patterns from data to predict outputs for new inputs |
| Training | The process of estimating model parameters from data |
| Inference | The process of computing outputs for new inputs using a trained model |
| Feature | A numeric representation of input data that the model can work with |
| Model | A bundle of parameters defining the input-to-output function |
| Dataset | The collection of inputs and labels used for training, validation, and evaluation |

## Before / After

**Before — rule-based classification:**

```python
def classify_email(text: str) -> str:
    """A spam classifier with hand-written rules."""
    spam_words = {"free", "winner", "click now", "discount"}
    score = sum(word in text for word in spam_words)
    return "spam" if score >= 2 else "ham"

print(classify_email("free coupon, you are the winner"))   # spam
# Every new phrasing forces a human to update the rules
```

**After — classification learned from data:**

```python
# Just the concept (no scikit-learn) — in practice, use sklearn, transformers, etc.
def train_naive_bayes(samples: list[tuple[str, str]]) -> dict:
    """Naive count-based learner: tally words per class."""
    counts = {"spam": {}, "ham": {}}
    totals = {"spam": 0, "ham": 0}
    for text, label in samples:
        for word in text.split():
            counts[label][word] = counts[label].get(word, 0) + 1
            totals[label] += 1
    return {"counts": counts, "totals": totals}

def predict(model: dict, text: str) -> str:
    spam_score = sum(model["counts"]["spam"].get(w, 0) for w in text.split())
    ham_score  = sum(model["counts"]["ham"].get(w, 0)  for w in text.split())
    return "spam" if spam_score > ham_score else "ham"

model = train_naive_bayes([
    ("free coupon winner", "spam"),
    ("meeting notes attached", "ham"),
    ("click now discount", "spam"),
    ("lunch together?", "ham"),
])
print(predict(model, "free lunch coupon"))   # decided from data
```

## Hands-On: Step by Step

### Step 1: Learn a line from data (linear regression)

```python
# Estimate a, b in y ≈ a*x + b from data — no external libraries
xs = [1, 2, 3, 4, 5]
ys = [2.1, 3.9, 6.1, 8.0, 10.2]   # roughly y = 2x

n = len(xs)
mean_x = sum(xs) / n
mean_y = sum(ys) / n
num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
den = sum((x - mean_x) ** 2 for x in xs)
a = num / den
b = mean_y - a * mean_x
print(f"y ≈ {a:.2f}x + {b:.2f}")    # y ≈ 2.03x + -0.05
```

### Step 2: Split into train / validation / test

```python
import random

def train_test_split(data: list, ratio: float = 0.8) -> tuple[list, list]:
    """Split data into training and evaluation sets."""
    data = list(data)
    random.shuffle(data)
    cut = int(len(data) * ratio)
    return data[:cut], data[cut:]

train, test = train_test_split(list(zip(xs, ys)))
print("train:", train)
print("test :", test)
```

### Step 3: Measure inference cost in time

```python
import time

def predict_y(x: float, a: float, b: float) -> float:
    return a * x + b

start = time.perf_counter()
for x in range(1_000_000):
    predict_y(x, a, b)
print(f"1M inferences: {time.perf_counter() - start:.3f}s")
# Simpler models infer faster — a key metric for real-time services
```

**Expected output:** the script should print the time for one million inferences and make it obvious why model simplicity matters for latency-sensitive systems.

### Step 4: Inspect data quality

```python
def basic_stats(values: list[float]) -> dict:
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return {"n": n, "mean": mean, "std": var ** 0.5,
            "min": min(values), "max": max(values)}

print(basic_stats(ys))
# Looking at distribution, missing values, and outliers before training is half the job in ML
```

### Step 5: A one-line ML workflow

```python
# 1) frame the problem -> 2) collect data -> 3) preprocess -> 4) train model
# -> 5) evaluate -> 6) deploy -> 7) monitor -> back to 1)

steps = [
    "frame problem", "collect data", "preprocess", "train model",
    "evaluate", "deploy", "monitor",
]
for i, step in enumerate(steps, 1):
    print(f"{i}. {step}")
```

## Notable Points in This Code

- Simpler models are easier to debug and operate — always start from a baseline.
- Without train/validation/test splits, you will overestimate performance.
- Inference time drives both user experience and infrastructure cost.
- The data pipeline takes far more time than the model code.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Starting with the model | Weak data and problem framing | Problem -> data -> baseline -> then model |
| Train/eval data leakage | Inflated evaluation scores | Split strictly by time or user |
| Judging only by mean accuracy | Hides class imbalance | Look at precision, recall, F1, confusion matrix |
| No monitoring after deployment | Performance degrades from data drift | Drift monitoring and a retraining cadence |
| Ignoring GPU/memory cost | Operating cost exceeds business value | Model compression, batch inference, caching |

## How This Is Used in Practice

- Recommendation, ranking, and search using user behavior logs as training data.
- LLM-based tools combining prompts, retrieval, and caching in a RAG pipeline.
- Deploying ML models as microservices and measuring impact via A/B tests.
- MLOps — dataset versioning, experiment tracking, automated retraining.
- AI cost management — tracking unit economics of model size, tokens, and GPU time.

## How a Senior Engineer Thinks

A senior engineer treats AI as a tool. They don't try to solve every problem with ML; they use rules where rules suffice and ML where ML is meaningful. And because an ML system is still software, it needs the same testing, monitoring, and rollback plans as any other service.

They also know that fundamentals matter more in the AI era, not less. Models change every year, but the principles of data representation, algorithmic cost, and system design stay the same. People with strong CS foundations adopt new tools the fastest.

## How the Series Connects

| In this series | In AI/DS |
| --- | --- |
| Data Representation (EP3) | Tensor dtypes, embedding vectors |
| Algorithms and Complexity (EP4) | Training/inference cost, index search |
| Computer Architecture (EP5) | GPU memory and cache, batch processing |
| Operating Systems (EP6) | Multiprocess training, GPU scheduling |
| Networks (EP7) | Distributed training, model serving |
| Databases (EP8) | Feature stores, vector databases |
| Software Engineering (EP9) | MLOps, experiment reproducibility |

## Checklist

- [ ] I can explain in one sentence the difference between ML and rule-based systems
- [ ] I know why train/validation/test splits are necessary
- [ ] I am aware that model inference is also computation on CPU/memory
- [ ] I understand that AI systems need the same tests and monitoring
- [ ] I have sketched my own learning roadmap for what to study next

## Practice Problems

1. Use the linear regression code above on a small dataset of your own (for example, exercise time vs calories) to learn a line and predict outputs for new inputs.

2. Split the same dataset into train and evaluation sets and compute the mean absolute error (MAE) on the evaluation set.

3. Pick the topic from this series you feel weakest on and write a 100-line study article that focuses just on that one topic.

## Wrap-Up and Next Steps

In this series we drew the big map of computer science: how data is represented, how algorithms are measured, how hardware and the OS cooperate, how the network and database hold the system up, and how engineering keeps it all working over time. AI/DS is one field built on top of that map, with statistics and a domain added.

A suggested learning path:

- **Language depth**: Python 101 → Python Advanced (data structures, concurrency, metaprogramming)
- **Systems depth**: Operating Systems: Three Easy Pieces; Designing Data-Intensive Applications
- **AI/DS**: statistics → machine learning (scikit-learn) → deep learning (PyTorch) → LLMs and RAG
- **Engineering**: test automation, CI/CD, cloud (AWS/GCP), observability

Tools change; foundations stay. Thank you for reading the series.

## Answering the Opening Questions

- **What boundary should you inspect first when applying From CS to AI and Data Science?**
  - The article treats From CS to AI and Data Science as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for From CS to AI and Data Science?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when From CS to AI and Data Science reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Science 101 (1/10): What Is Computer Science?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): Computation and Programs](./02-computation-and-programs.md)
- [Computer Science 101 (3/10): Data Representation](./03-data-representation.md)
- [Computer Science 101 (4/10): Algorithms and Complexity](./04-algorithms-and-complexity.md)
- [Computer Science 101 (5/10): Computer Architecture](./05-computer-architecture.md)
- [Computer Science 101 (6/10): Operating Systems](./06-operating-systems.md)
- [Computer Science 101 (7/10): Networks](./07-networks.md)
- [Computer Science 101 (8/10): Databases](./08-databases.md)
- [Computer Science 101 (9/10): Software Engineering](./09-software-engineering.md)
- **From CS to AI and Data Science (current)**

<!-- toc:end -->

## References

- [Hands-On Machine Learning — Aurélien Géron](https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/)
- [scikit-learn — User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Designing Machine Learning Systems — Chip Huyen](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/)
- [The Bitter Lesson — Rich Sutton](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)

Tags: Computer Science, AI, Data Science, Machine Learning, Statistics, Career
