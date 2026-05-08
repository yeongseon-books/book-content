
# 정보이론

> Math for CS 101 시리즈 (9/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *정보* 의 *양* 은 어떻게 *측정* 할까요?

> *정보이론* 은 *불확실성* 의 *비트 단위* 이고, *압축*, *통신*, *ML 손실 함수* 의 *기반* 입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *비트* 와 *정보량*
- *엔트로피*
- *교차 엔트로피*
- *KL 발산*
- *압축* 직관

## 왜 중요한가

*분류기 손실 함수*, *zip 압축*, *통신 코드*, *언어 모델* 모두 *정보이론* 위에서 정의됩니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    P[Distribution] --> H[Entropy]
    P --> C[Cross Entropy]
    C --> K[KL Divergence]
    H --> Z[Compression]
```

## 핵심 용어 정리

- **bit**: *2 값* 을 구분하는 단위.
- **entropy**: *평균 정보량*.
- **cross entropy**: *예측* 으로 *실제* 를 부호화한 비용.
- **KL divergence**: 두 분포의 *거리*.
- **compression**: *엔트로피* 가 *하한*.

## Before/After

**Before**: *모든 메시지* 동일 길이.

**After**: *자주 쓰는 것* 짧게, *드문 것* 길게.

## 실습: 미니 정보이론 키트

### 1단계 — 정보량

```python
import math

def info(p):
    return -math.log2(p)
```

### 2단계 — 엔트로피

```python
def entropy(probs):
    return sum(-p * math.log2(p) for p in probs if p > 0)
```

### 3단계 — 교차 엔트로피

```python
def cross_entropy(p, q):
    return sum(-pi * math.log2(qi) for pi, qi in zip(p, q) if qi > 0)
```

### 4단계 — KL 발산

```python
def kl(p, q):
    return cross_entropy(p, q) - entropy(p)
```

### 5단계 — 평균 부호 길이

```python
def avg_len(probs, lengths):
    return sum(p * L for p, L in zip(probs, lengths))
```

## 이 코드에서 주목할 점

- *log2* 단위는 *비트*.
- *KL* 은 *비대칭*.
- *교차 엔트로피* 는 *손실 함수*.

## 자주 하는 실수 5가지

1. ***log(0)* 처리 누락.**
2. ***KL* 을 *대칭* 으로 가정.**
3. ***엔트로피* 와 *교차 엔트로피* 혼동.**
4. ***확률 합* 이 *1* 아닌 입력.**
5. ***단위* (비트 vs 나트) 혼동.**

## 실무에서는 이렇게 쓰입니다

*분류기 손실*, *언어 모델 perplexity*, *zip/gzip*, *ML 정규화* 모두 *정보이론* 위에서 동작합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *정보* 는 *비트*.
- *엔트로피* 가 *압축의 하한*.
- *KL* 은 *분포의 거리*.
- *손실* 은 *교차 엔트로피*.
- *모델* 은 *분포* 추정.

## 체크리스트

- [ ] *확률 합* 검증.
- [ ] *log(0)* 보호.
- [ ] *단위* 명시.
- [ ] *KL* 의 *방향* 명시.

## 연습 문제

1. *엔트로피* 한 줄 정의.
2. *KL 발산* 한 줄.
3. *교차 엔트로피* 한 줄.

## 정리 및 다음 단계

다음 글은 *알고리즘과 수학* 종합 편입니다.

- [CS에 수학이 필요한 이유](./01-why-math-for-cs.md)
- [논리와 증명](./02-logic-and-proofs.md)
- [집합과 함수](./03-sets-and-functions.md)
- [그래프](./04-graphs.md)
- [조합](./05-combinatorics.md)
- [확률](./06-probability.md)
- [선형대수](./07-linear-algebra.md)
- [미분](./08-calculus.md)
- **정보이론 (현재 글)**
- 알고리즘과 수학 (예정)
## 참고 자료

- [Information Theory - Stanford Encyclopedia](https://plato.stanford.edu/entries/information-theory/)
- [A Mathematical Theory of Communication - Shannon](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)
- [Elements of Information Theory - Cover and Thomas](https://www.wiley.com/en-us/Elements+of+Information+Theory%2C+2nd+Edition-p-9780471241959)
- [SciPy Stats Entropy Documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.entropy.html)

Tags: Math, InformationTheory, Entropy, Compression, Beginner

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
