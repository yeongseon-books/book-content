---
series: math-for-cs-101
episode: 9
title: "Math for CS 101 (9/10): Information Theory"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Math
  - InformationTheory
  - Entropy
  - Compression
  - Beginner
seo_description: A beginner-friendly tour of bits, entropy, cross entropy, KL divergence, Shannon, and compression intuition for CS
last_reviewed: '2026-05-15'
---

# Math for CS 101 (9/10): Information Theory

To understand why compression works, why cross entropy appears in classifier loss functions, or why language-model perplexity drops when predictions improve, you need a common concept underneath all three. That concept is information theory.

Information theory treats information as something measurable instead of something merely descriptive. It lets you ask how surprising an event is, how uncertain a distribution is, and how far a predictive distribution is from the real one, all in a shared quantitative language.

This is the 9th post in the Math for CS 101 series.

Here we connect information content, entropy, cross entropy, KL divergence, and compression limits into one mental model.


![math for cs 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/09/09-01-concept-at-a-glance.en.png)
*math for cs 101 chapter 9 flow overview*
> Entropy and information measure the theoretical limits of communication, compression, and storage; they set the boundaries of what is possible.

## Questions to Keep in Mind

- What does it mean to measure information in bits?
- Why is entropy called average information content?
- Why is cross entropy so common as an ML loss function?

## Why It Matters

Classifier losses, communication codes, compression formats, and language-model evaluation all rely on information-theoretic ideas. The formulas differ by domain, but the underlying questions are similar: how surprising is this event, how uncertain is this source, and how expensive is it to encode reality with the wrong distribution?

Once you see that connection, entropy stops feeling like a standalone definition. It becomes the lower-level quantity that explains why common messages should be short, rare messages should be long, and wrong probability models get penalized.

Information theory measures *entropy* (uncertainty), *mutual information* (shared knowledge), and compression ratios. It defines what is theoretically possible.

## Before/After

**Before**: every message gets the *same length*.

**After**: *common* messages short, *rare* ones long.

## Key Terms

- **bit**: a *binary* unit.
- **entropy**: *average information content*.
- **cross entropy**: cost of coding *truth* with *predictions*.
- **KL divergence**: a *distance* between distributions.
- **compression**: bounded *below* by entropy.

## Hands-on: Mini Information Kit

### Step 1 — Information Content

```python
import math

def info(p):
    return -math.log2(p)
```

The less probable an event, the more information it carries—rare events are more surprising. Using `log2` gives units in bits, directly connecting to how many binary questions you need to identify the event.

### Step 2 — Entropy

```python
def entropy(probs):
    return sum(-p * math.log2(p) for p in probs if p > 0)
```

Entropy is the average information content across an entire distribution. It tells you how uncertain the distribution is overall—and sets the theoretical floor for how compactly you can encode messages from that source.

### Step 3 — Cross Entropy

```python
def cross_entropy(p, q):
    return sum(-pi * math.log2(qi) for pi, qi in zip(p, q) if qi > 0)
```

Cross entropy measures the cost of encoding events from distribution p using a code optimized for distribution q. In ML, it is the standard classification loss because it penalizes confident wrong predictions heavily.

### Step 4 — KL Divergence

```python
def kl(p, q):
    return cross_entropy(p, q) - entropy(p)
```

KL divergence is the extra cost of using the wrong distribution. It is always non-negative and asymmetric—D(p||q) ≠ D(q||p). This asymmetry matters when choosing which direction to minimize in variational methods.

### Step 5 — Average Code Length

```python
def avg_len(probs, lengths):
    return sum(p * L for p, L in zip(probs, lengths))
```

Average code length connects theory to practice: given symbol probabilities and their assigned code lengths, this weighted sum tells you how many bits per symbol your encoding actually uses. Shannon's theorem says you cannot beat entropy.

## Entropy: Fair Coin vs Biased Coin

```python
import math

def entropy(probs: list[float]) -> float:
    return -sum(p * math.log2(p) for p in probs if p > 0)

fair_coin = [0.5, 0.5]
biased_coin = [0.9, 0.1]

h_fair = entropy(fair_coin)      # 1.0 bit
h_biased = entropy(biased_coin)  # 0.469 bits
```

The fair coin has higher entropy because its outcome is harder to predict. Entropy is closer to "prediction uncertainty" than to "disorder."

## Decision Tree Information Gain

Information gain is a direct application of information theory in machine learning.

```python
def information_gain(
    parent_h: float, left_h: float, right_h: float,
    left_ratio: float, right_ratio: float
) -> float:
    child_h = left_ratio * left_h + right_ratio * right_h
    return parent_h - child_h
```

The feature that reduces entropy most after a split becomes the best split criterion. Decision trees select branches based on uncertainty reduction, not just classification accuracy.

## Cross Entropy and KL Divergence Relationship

Cross entropy decomposes as `H(p, q) = H(p) + KL(p||q)`:

- `H(p)` is the data's inherent uncertainty — the model cannot change it.
- `KL(p||q)` measures how far model distribution `q` is from true distribution `p` — training can reduce it.

Minimizing cross entropy is therefore equivalent to minimizing KL divergence.

## Compression Perspective Summary

| Concept | Question | Interpretation |
| --- | --- | --- |
| Information content | How surprising is one event? | `-log2(p)` |
| Entropy | How many bits on average? | Distribution uncertainty |
| Cross entropy | Cost of coding with the wrong distribution? | Prediction quality |
| KL divergence | Difference between two distributions? | Extra cost |

The same perspective applies when examining compression algorithms: assigning shorter codewords to frequent patterns reduces average length.

## Implementation Caveats

1. Guard `log(0)` with epsilon
2. Verify probabilities sum to 1 (normalize)
3. Prevent unit confusion (bit vs nat)
4. Always state KL direction (`p||q`)

Missing any of these produces numbers that look correct but are interpreted wrong. Information theory code demands faithful adherence to definitions.

## Perplexity and Entropy

Perplexity, commonly used in language model evaluation, is the exponential form of entropy.

```python
import math

def perplexity(cross_entropy_bits: float) -> float:
    return 2 ** cross_entropy_bits
```

Lower perplexity means the model predicts the next-token distribution more accurately. Perplexity is not an independent metric — it is cross entropy rescaled to a more interpretable scale.

## Huffman Coding

Huffman coding assigns shorter codes to frequent symbols, reducing average bit length. It satisfies the prefix-code condition, making decoding unambiguous.

```python
import heapq

def huffman_lengths(freqs):
    heap = [[f, [s, ""]] for s, f in freqs.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    return {s: len(code) for s, code in heap[0][1:]}

print(huffman_lengths({'A': 45, 'B': 13, 'C': 12, 'D': 16, 'E': 9, 'F': 5}))
```

Connecting information theory to a compression implementation makes it clear that entropy is not just an abstract metric — it is the actual lower bound on storage and transmission cost.

## Mutual Information

Mutual information (MI) measures how much information two random variables share about each other.

`I(X;Y) = H(X) - H(X|Y) = H(Y) - H(Y|X) = H(X) + H(Y) - H(X,Y)`

If knowing X reduces uncertainty about Y, MI is positive. If MI is zero, the variables are independent.

```python
import numpy as np
from collections import Counter

def mutual_information(x: list, y: list) -> float:
    """Estimate mutual information for discrete random variables."""
    n = len(x)
    assert n == len(y)

    px = Counter(x)
    py = Counter(y)
    pxy = Counter(zip(x, y))

    mi = 0.0
    for (xi, yi), count_xy in pxy.items():
        p_xy = count_xy / n
        p_x = px[xi] / n
        p_y = py[yi] / n
        mi += p_xy * np.log2(p_xy / (p_x * p_y))
    return mi

# Example: perfectly dependent vs independent
labels = [0, 0, 1, 1, 2, 2, 0, 1, 2, 0]
same = labels[:]
rand = [1, 2, 0, 2, 1, 0, 2, 0, 1, 2]

print(f"MI(X, X): {mutual_information(labels, same):.4f} bits")  # maximum
print(f"MI(X, R): {mutual_information(labels, rand):.4f} bits")  # near 0
```

| Domain | Application | Description |
| --- | --- | --- |
| Feature selection | MI-based filter | Prioritize features with high MI to target |
| Decision trees | Information gain | Select node splits that maximize MI increase |
| Clustering | NMI metric | Evaluate cluster quality via Normalized MI |
| Generative models | InfoGAN | Maximize MI between latent code and output |

## Channel Capacity and Shannon Limit

Even with noise, there exists a maximum transmission rate at which error rate can be made arbitrarily small. This is channel capacity.

`C = max_{p(x)} I(X;Y)`

For a binary symmetric channel (BSC) where bits flip with probability p:

`C_BSC = 1 - H(p) = 1 - [-p*log2(p) - (1-p)*log2(1-p)]`

```python
import numpy as np

def binary_entropy(p: float) -> float:
    """Compute binary entropy function H(p)."""
    if p == 0 or p == 1:
        return 0.0
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))

def bsc_capacity(p: float) -> float:
    """Compute binary symmetric channel capacity."""
    return 1.0 - binary_entropy(p)

error_probs = [0.0, 0.01, 0.05, 0.1, 0.2, 0.3, 0.5]
print("Error prob(p)  Capacity(C)  Note")
print("-" * 50)
for p in error_probs:
    c = bsc_capacity(p)
    note = "perfect channel" if p == 0 else "random channel" if p == 0.5 else ""
    print(f"  {p:.2f}        {c:.4f}       {note}")
```

Shannon's channel coding theorem guarantees:

- If rate R < C, proper coding can drive error rate to near zero.
- If rate R > C, no coding can avoid errors.

This result sets the design limits for 5G, Wi-Fi, and satellite communication. LDPC codes and Turbo codes are practical coding schemes that approach the Shannon limit closely.

## Compression Efficiency Experiment

Comparing theoretical entropy against real compression algorithms shows why entropy is a lower bound.

```python
import zlib
import math
import os
from collections import Counter

def entropy_bits(data: bytes) -> float:
    """Compute entropy in bits/byte for a byte sequence."""
    freq = Counter(data)
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())

def compression_experiment(data: bytes, label: str):
    """Compare entropy with actual compression results."""
    h = entropy_bits(data)
    compressed = zlib.compress(data, level=9)
    ratio = len(compressed) / len(data)
    theoretical_ratio = h / 8.0  # entropy / max entropy (8 bits)

    print(f"\n[{label}]")
    print(f"  Original size: {len(data):,} bytes")
    print(f"  Entropy: {h:.3f} bits/byte (max 8.0)")
    print(f"  Theoretical minimum ratio: {theoretical_ratio:.3f}")
    print(f"  zlib compression ratio: {ratio:.3f}")
    print(f"  Efficiency vs entropy: {theoretical_ratio / ratio * 100:.1f}%")

# Experiment 1: biased data (low entropy)
biased = bytes([0] * 800 + [1] * 150 + [2] * 50)
compression_experiment(biased, "Biased data (low entropy)")

# Experiment 2: uniform distribution (high entropy)
uniform = os.urandom(1000)
compression_experiment(uniform, "Random data (high entropy)")

# Experiment 3: natural language text (medium entropy)
text = ("Information theory is the foundation of communication and compression. " * 20).encode('utf-8')
compression_experiment(text, "Repeated text (medium entropy)")
```

Key observations:

1. Lower entropy means better compression ratio.
2. Random data has maximum entropy (~8 bits/byte) and is nearly incompressible.
3. Real compression algorithms always produce results slightly above the entropy lower bound (overhead).

## What to Notice in This Code

- *log2* gives *bits*.
- *KL* is *asymmetric*.
- *Cross entropy* is the standard *loss*.

## Five Common Mistakes

1. **Forgetting to handle *log(0)*.**
2. **Assuming *KL* is *symmetric*.**
3. **Mixing up *entropy* and *cross entropy*.**
4. **Inputs whose *probabilities* do not sum to *1*.**
5. **Confusing *units* (bits vs nats).**

## How This Shows Up in Production

*Classifier loss*, *language model perplexity*, *zip/gzip*, and *ML regularization* all use information theory.

## How a Senior Engineer Thinks

- *Information* is *bits*.
- *Entropy* is the *compression floor*.
- *KL* is *distributional distance*.
- *Loss* is *cross entropy*.
- *Models* estimate *distributions*.

## Checklist

- [ ] Verify *probabilities sum to 1*.
- [ ] Guard *log(0)*.
- [ ] State the *units*.
- [ ] State the *direction* of *KL*.

## Practice Problems

1. Define *entropy* in one line.
2. Define *KL divergence* in one line.
3. Define *cross entropy* in one line.

## Wrap-up and Next Steps

Information theory gives you a way to read surprise, uncertainty, and coding cost as parts of the same system. That makes compression, language modeling, and classification losses much easier to interpret.

Next, we close the series by tying these mathematical tools back into algorithm design as one capstone view.

## Answering the Opening Questions

- **What measures the quantity of information?**
  - This article defined a single event's information as `-log2(p)`, measured in bits. In `info(p)`, lower-probability events yield larger values—capturing the intuition that rare events are more surprising, expressed as a number.
- **Why is entropy called average information?**
  - Entropy weights each event's information by its probability and sums—representing the distribution's average surprise. Comparing `entropy([0.5, 0.5])` vs. `entropy([0.9, 0.1])` for fair vs. biased coins, plus Huffman/zlib compression experiments, showed that entropy equals the lower bound on average code length.
- **Why is cross-entropy so commonly used as a loss function?**
  - Cross-entropy is the average extra cost of describing true distribution `p` using model distribution `q`—so cost grows as predictions worsen. The article's `H(p, q) = H(p) + KL(p||q)` relationship and `target`/`model_good`/`model_bad` examples explained that minimizing cross-entropy is ultimately reducing KL divergence to push the model distribution toward the true one.
<!-- toc:begin -->
## In this series

- [Math for CS 101 (1/10): Why Math for CS](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): Logic and Proofs](./02-logic-and-proofs.md)
- [Math for CS 101 (3/10): Sets and Functions](./03-sets-and-functions.md)
- [Math for CS 101 (4/10): Graphs](./04-graphs.md)
- [Math for CS 101 (5/10): Combinatorics](./05-combinatorics.md)
- [Math for CS 101 (6/10): Probability](./06-probability.md)
- [Math for CS 101 (7/10): Linear Algebra](./07-linear-algebra.md)
- [Math for CS 101 (8/10): Calculus](./08-calculus.md)
- **Information Theory (current)**
- Algorithms and Math (upcoming)

<!-- toc:end -->

## References

- [Information Theory - Stanford Encyclopedia](https://plato.stanford.edu/entries/information-theory/)
- [A Mathematical Theory of Communication - Shannon](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)
- [Elements of Information Theory - Cover and Thomas](https://www.wiley.com/en-us/Elements+of+Information+Theory%2C+2nd+Edition-p-9780471241959)
- [SciPy Stats Entropy Documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.entropy.html)
- [SciPy GitHub repository](https://github.com/scipy/scipy)

Tags: Math, InformationTheory, Entropy, Compression, Beginner
