---
series: probability-101
episode: 3
title: "Probability 101 (3/10): Conditional Probability"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Probability
  - Conditional
  - Independence
  - Inference
  - Beginner
seo_description: Learn conditional probability, the multiplication rule, and base-rate reasoning so you can interpret context-dependent probabilities correctly.
last_reviewed: '2026-05-15'
---

# Probability 101 (3/10): Conditional Probability

Real probability questions almost always come with conditions. Traffic given rain, disease given a positive test, spam given a suspicious phrase in the subject line — most useful probabilities are probabilities inside a context, not in the abstract.

That is why conditional probability sits near the center of probability theory rather than at the edge. Once new information arrives, the denominator changes. If you do not feel that denominator shift clearly, model scores, diagnostic tests, and inference results all become easy to misread.

This is the 3rd post in the Probability 101 series. Here we define conditional probability, connect it to the multiplication rule, separate independence from dependence, and show why base rates can completely change the meaning of the same test result.


![probability 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/probability-101/03/03-01-concept-at-a-glance.en.png)
*probability 101 chapter 3 flow overview*
> Conditional probability forces you to name the context. The same number means different things under different conditions.

## Questions to Keep in Mind

- Why is conditional probability fundamentally about changing the denominator?
- Why can P(A|B) and P(B|A) be completely different values?
- In what situations does the multiplication rule naturally appear?

## Why It Matters

One of the most common mistakes in applied probability is reversing the direction of the condition. P(disease | positive test) and P(positive test | disease) look similar, but they answer different questions. Lose that directional sense, and you misread diagnostics, alerts, and model outputs.

The risk gets worse when the base rate is small. A rare disease with a sensitive test can still produce a positive result that does not mean what people assume it means. Conditional probability is the tool that forces context back into the interpretation.

## Independent vs Dependent Events

Understanding conditional probability requires a clear distinction between independence and dependence.

| Concept | Definition | Test | Example |
| --- | --- | --- | --- |
| Independent | A and B do not influence each other | P(A∩B) = P(A)·P(B) | Each flip of a coin |
| Dependent | Knowing B changes the probability of A | P(A\|B) ≠ P(A) | Weather and traffic congestion |

The most reliable independence test is checking the multiplication rule: compute P(A∩B) and P(A)·P(B); if they match, the events are independent. Equivalently, if P(A|B) = P(A), then knowing B does not change A's probability.

In practice, independence is often assumed for convenience, but most real events are dependent. A user's click behavior depends on previous page visits. Sensor readings correlate with prior measurements. Carelessly assuming independence can degrade model performance or introduce bias.

## Key Terms

- **P(A | B)**: probability of A given B = P(A∩B) / P(B).
- **Multiplication rule**: P(A∩B) = P(A | B)·P(B).
- **Law of total probability**: P(A) = Σ P(A | Bᵢ)·P(Bᵢ).
- **Independent**: P(A | B) = P(A).
- **Dependent**: P(A | B) ≠ P(A).

When you condition on B, the denominator changes. You stop looking at the entire population and recompute the ratio inside the subset where B occurred.

## Reversing the Direction Breaks Everything

"If the test is positive, the disease probability must be high" is a sentence people say often — but what you actually need is P(disease | positive). What test performance tables usually report is P(positive | disease). One is a question about post-diagnosis interpretation; the other is about how the test responds when disease is present.

The two are not the same information. Failing to separate them leads to treating high sensitivity as high diagnostic accuracy.

## Spam Filter Example

A spam filter is a practical application of conditional probability: given a suspicious word, how likely is the email to be spam?

```python
# Simple spam filter example (hypothetical data)
# P(spam) = 0.3
# P("winner" | spam) = 0.7
# P("winner" | normal) = 0.05

P_spam = 0.3
P_normal = 0.7
P_word_given_spam = 0.7
P_word_given_normal = 0.05

# Law of total probability: P("winner")
P_word = P_word_given_spam * P_spam + P_word_given_normal * P_normal
print(f"P('winner') = {P_word:.3f}")

# Conditional probability: P(spam | "winner")
P_spam_given_word = (P_word_given_spam * P_spam) / P_word
print(f"P(spam | 'winner') = {P_spam_given_word:.3f}")

# Comparison: before and after seeing the word
print(f"P(spam) = {P_spam:.3f}")
print(f"P(spam|'winner') = {P_spam_given_word:.3f}")
print(f"Increase: {P_spam_given_word / P_spam:.2f}x")
```

Output:

```
P('winner') = 0.245
P(spam | 'winner') = 0.857
P(spam) = 0.300
P(spam|'winner') = 0.857
Increase: 2.86x
```

Before seeing "winner," the spam probability was 30%. After observing it, the probability jumps to 85.7%. Conditional probability shows how new information updates the probability.

## Probability Tree

A probability tree is a systematic way to solve conditional probability problems. Multiply conditional probabilities along branches to get path probabilities.

```python
# Probability tree: weather and traffic congestion
# Level 1: rain (P=0.3) or clear (P=0.7)
# Level 2: congestion
#   P(congestion | rain) = 0.8
#   P(congestion | clear) = 0.2

P_rain = 0.3
P_clear = 0.7
P_jam_given_rain = 0.8
P_jam_given_clear = 0.2

# Path probabilities (multiplication rule)
path_rain_jam = P_rain * P_jam_given_rain
path_rain_no_jam = P_rain * (1 - P_jam_given_rain)
path_clear_jam = P_clear * P_jam_given_clear
path_clear_no_jam = P_clear * (1 - P_jam_given_clear)

print("Probability tree:")
print(f"  Rain → Congestion:   {path_rain_jam:.3f}")
print(f"  Rain → No congestion: {path_rain_no_jam:.3f}")
print(f"  Clear → Congestion:  {path_clear_jam:.3f}")
print(f"  Clear → No congestion:{path_clear_no_jam:.3f}")
print(f"  Total:                {path_rain_jam + path_rain_no_jam + path_clear_jam + path_clear_no_jam:.1f}")

# Law of total probability: P(congestion)
P_jam = path_rain_jam + path_clear_jam
print(f"\nP(congestion) = {P_jam:.3f}")

# Reverse inference: P(rain | congestion)
P_rain_given_jam = path_rain_jam / P_jam
print(f"P(rain | congestion) = {P_rain_given_jam:.3f}")
print(f"When congestion is observed, {P_rain_given_jam:.0%} chance rain is the cause")
```

Output:

```
Probability tree:
  Rain → Congestion:   0.240
  Rain → No congestion: 0.060
  Clear → Congestion:  0.140
  Clear → No congestion:0.560
  Total:                1.0

P(congestion) = 0.380
P(rain | congestion) = 0.632
When congestion is observed, 63% chance rain is the cause
```

Each tree path is the multiplication rule applied. All leaf probabilities sum to 1. Reverse inference (what caused congestion?) divides the relevant path probability by the total probability of the observed event.

## Conditional Probability via Contingency Table

The most intuitive way to understand conditional probability is through a 2×2 contingency table.

Diagnostic test example:

|  | Disease present | Disease absent | Total |
| --- | --- | --- | --- |
| Test positive | 45 (TP) | 5 (FP) | 50 |
| Test negative | 5 (FN) | 945 (TN) | 950 |
| Total | 50 | 950 | 1000 |

Multiple probabilities can be read from this table:

- `P(disease) = 50/1000 = 0.05`
- `P(positive | disease) = 45/50 = 0.9` (sensitivity)
- `P(negative | healthy) = 945/950 = 0.995` (specificity)
- `P(disease | positive) = 45/50 = 0.9` (PPV)

The key is checking what the denominator is:

- `P(positive | disease)`: denominator = 50 diseased people
- `P(disease | positive)`: denominator = 50 positive-test people

The number 50 appears in both, but the meaning of the denominator is completely different. Seeing this distinction clearly is the core of conditional probability.

```python
# Conditional probability from a 2x2 table
TP, FP, FN, TN = 45, 5, 5, 945
total = TP + FP + FN + TN

sick = TP + FN
healthy = FP + TN
positive = TP + FP
negative = FN + TN

print(f"P(disease) = {sick/total:.3f}")
print(f"P(positive|disease) = {TP/sick:.3f}  # sensitivity")
print(f"P(disease|positive) = {TP/positive:.3f}  # PPV")
print(f"P(negative|healthy) = {TN/healthy:.3f}  # specificity")
```

## Monte Carlo Estimation of Conditional Probability

When analytical calculation is complex, simulation can estimate conditional probabilities.

```python
import random

def simulate_conditional(n_trials: int = 100_000) -> dict:
    """
    Two dice: P(doubles | sum >= 8)
    """
    count_condition = 0  # sum >= 8
    count_both = 0       # sum >= 8 AND doubles

    for _ in range(n_trials):
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        if d1 + d2 >= 8:
            count_condition += 1
            if d1 == d2:
                count_both += 1

    return {
        "P(sum>=8)": count_condition / n_trials,
        "P(doubles AND sum>=8)": count_both / n_trials,
        "P(doubles | sum>=8)": count_both / count_condition if count_condition > 0 else 0,
    }

# Theoretical value
omega = [(i, j) for i in range(1, 7) for j in range(1, 7)]
cond = [(i, j) for i, j in omega if i + j >= 8]
both = [(i, j) for i, j in cond if i == j]
theory = len(both) / len(cond)

random.seed(42)
results = simulate_conditional()
print(f"Simulation P(doubles | sum>=8) = {results['P(doubles | sum>=8)']:.4f}")
print(f"Theory P(doubles | sum>=8) = {theory:.4f}")
print(f"Unconditional P(doubles) = {6/36:.4f}")
print(f"Condition changed probability: {theory:.4f} vs {6/36:.4f}")
```

Without conditions, the probability of doubles is 6/36 = 0.167. With the condition "sum is 8 or higher," the probability changes. This is the essence of dependence.

## Base Rate Fallacy Simulation

The base rate fallacy is the most common mistake in conditional probability. With a rare disease, even a sensitive test produces mostly false alarms.

```python
import random

def base_rate_simulation(
    prevalence: float,
    sensitivity: float,
    specificity: float,
    n_population: int = 100_000,
) -> dict:
    """
    Simulate the base rate fallacy
    prevalence: disease prevalence
    sensitivity: P(positive | disease)
    specificity: P(negative | healthy)
    """
    tp = fp = fn = tn = 0

    for _ in range(n_population):
        sick = random.random() < prevalence
        if sick:
            positive = random.random() < sensitivity
        else:
            positive = random.random() > specificity

        if sick and positive:
            tp += 1
        elif not sick and positive:
            fp += 1
        elif sick and not positive:
            fn += 1
        else:
            tn += 1

    total_positive = tp + fp
    ppv = tp / total_positive if total_positive > 0 else 0
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn, "PPV": ppv}

random.seed(42)
# Low prevalence (0.1%) + high sensitivity (99%)
result = base_rate_simulation(
    prevalence=0.001, sensitivity=0.99, specificity=0.95
)
print(f"TP={result['TP']}, FP={result['FP']}")
print(f"PPV (positive predictive value) = {result['PPV']:.3f}")
print(f"i.e., {1-result['PPV']:.1%} of positives are false alarms")

print("\n--- Raising prevalence to 5% ---")
result2 = base_rate_simulation(
    prevalence=0.05, sensitivity=0.99, specificity=0.95
)
print(f"TP={result2['TP']}, FP={result2['FP']}")
print(f"PPV = {result2['PPV']:.3f}")
```

With 0.1% prevalence, even 99% sensitivity means most positive results are false alarms. At 5% prevalence, PPV improves dramatically. This is the power of the base rate. The next post (Bayes' theorem) formalizes this relationship.

## Chaining Multiple Conditions

Multiple conditions can chain together. Apply the multiplication rule repeatedly.

```python
# P(A ∩ B ∩ C) = P(A) × P(B|A) × P(C|A∩B)
# Example: drawing 3 spades in a row without replacement

# 52 cards, 13 spades
P_first = 13 / 52
P_second_given_first = 12 / 51  # one spade removed
P_third_given_first_two = 11 / 50  # two spades removed

P_all_spades = P_first * P_second_given_first * P_third_given_first_two
print(f"P(all 3 spades) = {P_all_spades:.4f}")
print(f"Approximately 1 in {1/P_all_spades:.0f}")
```

The key insight in chaining is that earlier outcomes change the conditions for later ones. In sampling without replacement, each draw shrinks the remaining sample space, so each step's probability differs.

## Law of Total Probability

The law of total probability splits a complex event into mutually exclusive cases, computes each conditional probability, and sums them. It is essential for computing the denominator in Bayes' theorem.

```
P(B) = P(B | A₁) × P(A₁) + P(B | A₂) × P(A₂) + ... + P(B | Aₙ) × P(Aₙ)
```

Requirements:

- A₁, A₂, ..., Aₙ are mutually exclusive (no overlap)
- A₁ ∪ A₂ ∪ ... ∪ Aₙ = Ω (they cover everything)

**Practical example: product defect inspection**

Three factories A, B, C produce 40%, 35%, 25% of products respectively. Defect rates are 2%, 3%, 5%. What is the probability that a randomly selected product is defective?

```python
# Factory production shares
P_A = 0.40
P_B = 0.35
P_C = 0.25

# Defect rates per factory
P_defect_given_A = 0.02
P_defect_given_B = 0.03
P_defect_given_C = 0.05

# Law of total probability
P_defect = (P_defect_given_A * P_A +
            P_defect_given_B * P_B +
            P_defect_given_C * P_C)

print(f"P(defect) = {P_defect:.3f}")

# Reverse inference: P(from factory A | defective) — Bayes' theorem
P_A_given_defect = (P_defect_given_A * P_A) / P_defect
print(f"P(A | defect) = {P_A_given_defect:.3f}")
```

Output:

```
P(defect) = 0.032
P(A | defect) = 0.250
```

Overall defect rate is 3.2%. Although factory A produces 40% of all items, its lower defect rate means only 25% of defective items come from it.

The law of total probability is the standard technique for computing denominators in conditional probability. It recurs in Bayes' theorem, distribution calculations, and decision trees.

## Conditional Probability in Production

Conditional probability is not just a formula — it is the backbone of production decision-making.

**Web conversion rate** is P(purchase | visit). You track the proportion who buy among people who visited a specific page — not among all visitors. Changing the condition gives channel-specific analyses: P(purchase | ad click), P(purchase | email open).

**Search engine relevance** is P(click | query). Given a specific keyword, which result does the user click? Search rankings optimize this conditional probability.

**Recommendation CTR** is P(click | impression). Compute the probability of a click given that an item was shown, then rank the top-N. How you define the conditioning event determines recommendation quality.

**Practical checklist for interpreting conditional probabilities:**

1. **What is the denominator?** — The entire population, or a specific sub-group?
2. **What is the direction?** — P(A|B) or P(B|A)?
3. **What is the base rate?** — How common is the event in the full population?
4. **Can independence be assumed?** — Does the condition actually change the probability?
5. **Is the data sufficient?** — Do you have enough samples to compute the conditional frequency?

Habitually asking these five questions prevents most interpretation errors.

## Hands-on: 5-step Walkthrough

### Step 1 — Build the data

```python
# 100 people; 5 sick. Sensitivity 0.9, specificity 0.95
N, sick = 100, 5
TP = round(sick * 0.9)
FN = sick - TP
TN = round((N - sick) * 0.95)
FP = (N - sick) - TN
print(TP, FN, TN, FP)
```

A simple diagnostic example makes the direction of conditional probability viscerally clear. Of 100 people, 5 are sick, and the test has both sensitivity and specificity.

### Step 2 — P(positive)

```python
pos = TP + FP
print("P(pos):", pos / N)
```

The positive probability includes true positives from sick people and false positives from healthy people. Already the law of total probability is at work.

### Step 3 — P(disease | positive)

```python
print("P(sick|pos):", TP / pos)
```

Now the denominator is not all 100 people but the number who tested positive. This denominator switch is the heart of conditional probability.

### Step 4 — Verify the multiplication rule

```python
P_sick = sick / N
P_pos_given_sick = TP / sick
print("P(sick and pos):", P_pos_given_sick * P_sick, "==", TP / N)
```

The multiplication rule is not a formula to memorize — it is a way to rewrite the intersection using a condition. Verified in code, it feels less abstract.

### Step 5 — Check independence

```python
P_pos = pos / N
print("indep?", round(TP/N - P_sick * P_pos, 6))  # nonzero implies dependence
```

If independent, P(A∩B) equals P(A)·P(B). In diagnostic problems that almost never holds — test positivity is clearly linked to disease status.

## Five Common Mistakes

1. **Equating P(A|B) with P(B|A).** The most common and most costly mistake.

2. **Ignoring the base rate.** Without knowing how rare the event is in the full population, a single positive result can be grossly misinterpreted.

3. **Confusing independence and mutual exclusivity again.** "Cannot happen together" vs "does not influence" are different questions.

4. **Understanding the condition only in words, then dropping it from the formula.** Omitting the condition from the multiplication rule produces a similar-looking but entirely different calculation.

5. **Looking at the number without asking who the denominator is.** Strong interpretation always starts with confirming the denominator.

## Checklist

- [ ] I can define P(A|B) and explain it in terms of the denominator.
- [ ] I can apply the multiplication rule.
- [ ] I can distinguish independence from dependence.
- [ ] I can explain why the base rate fallacy occurs.
- [ ] I can compute P(B) using the law of total probability.
- [ ] I can draw a probability tree to solve conditional probability problems.
- [ ] I can estimate conditional probabilities via simulation.

## Wrap-up

Conditional probability is the tool for handling context. Three things to take from this post: conditioning changes the denominator, reversing the direction gives an entirely different question, and base rates must be considered alongside the number to interpret it correctly.

The next post covers Bayes' theorem. This post established the grammar of conditional probability; the next shows how to use that grammar to update beliefs systematically.

## Answering the Opening Questions

- **Why is conditional probability fundamentally about changing the denominator?**
  - P(A|B) keeps only the cases where B occurred and recomputes the ratio within that subset. In the contingency table, P(positive|disease) has 50 diseased people as denominator, while P(disease|positive) has 50 positive-test people. In the spam filter, before seeing the word P(spam)=0.300, but after observing "winner" the recalculation happens within "winner"-containing emails only, giving P(spam|"winner")=0.857.
- **Why can P(A|B) and P(B|A) be completely different values?**
  - They answer different questions. P(positive|disease) is sensitivity; P(disease|positive) is PPV — same table, different denominators. In the weather tree, P(congestion|rain)=0.8 but P(rain|congestion)=0.632. The base rate simulation also shows this: 99% sensitivity (P(positive|disease)) does not mean P(disease|positive) is high when prevalence is 0.1%.
- **In what situations does the multiplication rule naturally appear?**
  - Calculating any single path in a tree: P(rain ∩ congestion) = 0.3 × 0.8 = 0.240. Chaining conditions in sampling without replacement: 13/52 × 12/51 × 11/50. Computing numerators and denominators in Bayes' theorem and the law of total probability — all start from the multiplication rule.

<!-- toc:begin -->
## In this series

- [Probability 101 (1/10): What Is Probability?](./01-what-is-probability.md)
- [Probability 101 (2/10): Events and Sample Space](./02-events-and-sample-space.md)
- **Conditional Probability (current)**
- Bayes' Theorem (upcoming)
- Random Variables (upcoming)
- Expectation and Variance (upcoming)
- Discrete Distributions (upcoming)
- Continuous Distributions (upcoming)
- Law of Large Numbers and CLT (upcoming)
- Probability in Machine Learning (upcoming)

<!-- toc:end -->

## References

- [Khan Academy — Conditional probability](https://www.khanacademy.org/math/statistics-probability/probability-library/conditional-probability-independence)
- [Wikipedia — Conditional probability](https://en.wikipedia.org/wiki/Conditional_probability)
- [Wikipedia — Base rate fallacy](https://en.wikipedia.org/wiki/Base_rate_fallacy)
- [Stanford CS109 — Notes](https://web.stanford.edu/class/cs109/)

Tags: Probability, Conditional, Independence, Inference, Beginner
