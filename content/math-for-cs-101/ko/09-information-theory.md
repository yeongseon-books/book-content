---
episode: 9
language: ko
last_reviewed: '2026-05-12'
seo_description: 엔트로피, 교차 엔트로피, KL 발산으로 불확실성을 측정하는 법을 배우고 압축과 손실 함수의 원리를 정리합니다.
series: math-for-cs-101
status: publish-ready
tags:
- Math
- InformationTheory
- Entropy
- Compression
- Beginner
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Math for CS 101 (9/10): 정보이론"
---

# Math for CS 101 (9/10): 정보이론

압축 파일이 왜 작아지는지, 분류기의 손실 함수가 왜 교차 엔트로피인지, 언어 모델이 예측을 잘할수록 왜 퍼플렉서티가 낮아지는지 이해하려면 공통된 바닥 개념이 필요합니다. 그 바닥에 있는 주제가 정보이론입니다.

정보이론은 정보를 감각적인 표현이 아니라 측정 가능한 양으로 다룹니다. 어떤 사건이 얼마나 놀라운지, 어떤 분포가 얼마나 불확실한지, 압축이 어디까지 가능한지 같은 질문을 비트 단위로 말하게 해 줍니다.

이 글은 Math for CS 101 시리즈의 9번째 글입니다.

여기서는 정보이론을 압축, 통신, 머신러닝 손실 함수 뒤에 놓인 공통 언어로 보고 정보량, 엔트로피, 교차 엔트로피, KL 발산의 감각을 정리해 보겠습니다.

## 먼저 던지는 질문

- 정보의 양은 무엇으로 측정할까요?
- 엔트로피는 왜 평균 정보량이라고 부를까요?
- 교차 엔트로피는 왜 손실 함수로 자주 쓰일까요?

## 큰 그림

![Math for CS 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/09/09-01-concept-at-a-glance.ko.png)

*Math for CS 101 9장 흐름 개요*
이 그림은 정보량을 엔트로피로 측정하고, 압축과 통신 효율의 한계를 설명하는 원리를 보여줍니다.

> 엔트로피와 정보량은 통신, 압축, 암호화의 이론적 한계를 설명하는 언어입니다.

## 왜 중요한가

분류기 손실 함수, 압축 포맷, 통신 코드, 언어 모델은 모두 정보이론 위에서 정의됩니다. 이름은 달라도 공통 질문은 같습니다. 어떤 결과가 얼마나 놀라운가, 평균적으로 얼마나 많은 정보가 필요한가, 예측 분포가 실제 분포와 얼마나 다른가를 묻는 일입니다.

정보이론을 모르면 이 도구들은 공식만 남습니다. 반대로 정보이론의 관점을 잡으면 왜 자주 나오는 것은 짧게 표현하는 것이 이득인지, 왜 잘못된 확률 분포를 쓰면 손실이 커지는지 자연스럽게 이어집니다.

---

## 머릿속에 먼저 둘 관점

정보이론에서 가장 먼저 잡아야 할 문장은 이것입니다. **정보는 메시지의 길이가 아니라 놀라움의 정도와 연결된다**는 점입니다. 거의 확실한 사건은 정보량이 작고, 매우 드문 사건은 정보량이 큽니다.

엔트로피는 그 놀라움의 평균입니다. 분포가 고르게 퍼질수록 불확실성이 크고 엔트로피도 커집니다. 교차 엔트로피는 실제 분포를 잘못된 예측 분포로 코딩할 때 드는 평균 비용입니다. KL 발산은 그 차이를 더 분명하게 떼어 내어 보여 줍니다.

압축과의 관계도 여기서 나옵니다. 평균 부호 길이는 엔트로피보다 마음대로 더 작게 만들 수 없습니다. 그래서 정보이론은 가능성을 말할 뿐 아니라 한계도 말해 줍니다.

## 한 장으로 보는 정보이론

---

## 다섯 단계로 보는 정보이론 기초

### 첫 번째 단계 — 사건의 정보량을 봅니다

```python
import math

def info(p):
    return -math.log2(p)
```

확률이 작을수록 정보량이 커집니다. 드문 사건일수록 더 놀랍기 때문입니다. `log2`를 쓰면 단위는 비트가 됩니다.

### 두 번째 단계 — 평균 놀라움을 계산합니다

```python
def entropy(probs):
    return sum(-p * math.log2(p) for p in probs if p > 0)
```

엔트로피는 평균 정보량입니다. 분포 전체가 얼마나 불확실한지, 평균적으로 몇 비트가 필요한지 보여 줍니다. 그래서 압축의 바닥선과 자연스럽게 연결됩니다.

### 세 번째 단계 — 예측 분포의 비용을 봅니다

```python
def cross_entropy(p, q):
    return sum(-pi * math.log2(qi) for pi, qi in zip(p, q) if qi > 0)
```

교차 엔트로피는 실제 분포 `p`를 예측 분포 `q`로 설명할 때 드는 비용입니다. 머신러닝에서 손실 함수로 자주 쓰이는 이유가 여기에 있습니다. 예측이 실제 분포를 잘 따라갈수록 비용이 줄어듭니다.

### 네 번째 단계 — 두 분포의 차이를 떼어 냅니다

```python
def kl(p, q):
    return cross_entropy(p, q) - entropy(p)
```

KL 발산은 실제 분포와 예측 분포가 얼마나 다른지 보여 줍니다. 다만 대칭이 아니라는 점이 중요합니다. `KL(p || q)`와 `KL(q || p)`는 일반적으로 다릅니다.

### 다섯 번째 단계 — 평균 부호 길이를 봅니다

```python
def avg_len(probs, lengths):
    return sum(p * L for p, L in zip(probs, lengths))
```

자주 나오는 것은 짧게, 드물게 나오는 것은 길게 배정하면 평균 길이를 줄일 수 있습니다. 정보이론은 이 직관을 감이 아니라 계산으로 다루게 해 줍니다.

---

## 이 코드에서 먼저 볼 점

- `log2`의 단위는 비트입니다.
- 엔트로피는 평균 정보량입니다.
- 교차 엔트로피는 예측 분포의 비용을 나타냅니다.
- KL 발산은 비대칭입니다.
- 압축은 엔트로피보다 마음대로 더 아래로 내려갈 수 없습니다.

---

## 어디서 자주 헷갈릴까요?

`log(0)` 처리를 누락하는 실수가 가장 흔합니다. 확률이 0인 값을 그대로 로그에 넣으면 계산이 깨집니다. 구현에서는 이런 경계 사례를 반드시 보호해야 합니다.

KL 발산을 대칭이라고 가정하는 것도 전형적인 오해입니다. 이름만 보면 거리처럼 느껴지지만, 엄밀한 의미의 대칭 거리와는 다릅니다. 어떤 방향으로 비교하는지 명시해야 합니다.

엔트로피와 교차 엔트로피를 혼동하거나, 확률 합이 1이 아닌 입력을 그대로 넣는 일도 자주 나옵니다. 정보이론은 개념 자체보다 분포 가정을 제대로 세우는 일이 더 중요할 때가 많습니다.

---

## 실무에서는 이렇게 생각한다

분류기 손실, 언어 모델 퍼플렉서티, `zip`과 `gzip`, 머신러닝 정규화는 모두 정보이론 위에서 동작합니다. 특히 예측 모델을 다룰 때는 정보를 맞히는 문제와 압축하는 문제가 서로 닮아 있다는 점이 흥미롭습니다. 잘 예측하는 모델일수록 더 짧게 설명할 수 있기 때문입니다.

좋은 엔지니어는 손실 함수를 숫자로만 보지 않습니다. 그 숫자가 어떤 분포 차이를 뜻하는지, 단위가 무엇인지, 엔트로피 바닥선과 어떤 관계가 있는지 함께 읽습니다.

---

## 체크리스트

- [ ] 확률 합을 검증합니다.
- [ ] `log(0)`을 보호합니다.
- [ ] 단위를 명시합니다.
- [ ] KL의 방향을 명시합니다.
- [ ] 엔트로피와 교차 엔트로피의 차이를 설명할 수 있습니다.

## 연습 문제

1. 엔트로피를 한 줄로 정의해 보세요.
2. KL 발산을 한 줄로 정의해 보세요.
3. 교차 엔트로피가 왜 손실 함수로 쓰이는지 설명해 보세요.

## 정리

정보이론은 압축, 통신, 예측 모델을 하나의 시선으로 보게 해 줍니다. 정보량, 엔트로피, 교차 엔트로피, KL 발산을 이해하면 왜 어떤 모델이 더 좋은지, 압축이 어디까지 가능한지, 손실 함수가 실제로 무엇을 의미하는지 더 분명하게 읽을 수 있습니다. 다음 글에서는 이 시리즈를 묶어 알고리즘과 수학의 연결을 정리합니다.


## 엔트로피 계산을 직접 해 보기

정보이론은 공식이 짧아서 오히려 의미를 놓치기 쉽습니다. 직접 계산해 보면 감각이 빨리 잡힙니다.

```python
import math

def entropy(probs: list[float]) -> float:
    return -sum(p * math.log2(p) for p in probs if p > 0)

fair_coin = [0.5, 0.5]
biased_coin = [0.9, 0.1]

h_fair = entropy(fair_coin)
h_biased = entropy(biased_coin)
```

공정한 동전의 엔트로피가 더 큽니다. 결과가 더 예측 불가능하기 때문입니다. 즉 엔트로피는 "무질서"보다 "예측 불확실성"에 가깝습니다.

## 의사결정나무의 정보 이득

머신러닝에서 정보이론이 직접 등장하는 대표 예가 정보 이득입니다.

```python
def information_gain(parent_h: float, left_h: float, right_h: float, left_ratio: float, right_ratio: float) -> float:
    child_h = left_ratio * left_h + right_ratio * right_h
    return parent_h - child_h
```

분할 후 엔트로피가 크게 줄어드는 특성이 좋은 분할 기준이 됩니다. 그래서 트리 모델은 분류 정확도뿐 아니라 불확실성 감소량을 기준으로 분기를 선택합니다.

## 교차 엔트로피와 KL 발산 관계

교차 엔트로피는 `H(p, q) = H(p) + KL(p||q)`로 분해됩니다. 이 식은 손실 해석에서 매우 중요합니다.

- `H(p)`는 데이터 자체의 불확실성으로 모델이 바꿀 수 없습니다.
- `KL(p||q)`는 모델 분포 `q`가 실제 분포 `p`와 얼마나 다른지 나타내며, 학습으로 줄일 수 있습니다.

즉 교차 엔트로피 최소화는 본질적으로 KL 발산 최소화와 같습니다.

## 압축 관점 정리

| 개념 | 질문 | 해석 |
| --- | --- | --- |
| 정보량 | 사건 하나가 얼마나 놀라운가 | `-log2(p)` |
| 엔트로피 | 평균적으로 몇 비트가 필요한가 | 분포의 불확실성 |
| 교차 엔트로피 | 잘못된 분포로 코딩할 때 비용 | 예측 품질 |
| KL 발산 | 두 분포 차이 | 추가 비용 |

압축 알고리즘을 볼 때도 같은 관점이 적용됩니다. 자주 등장하는 패턴에 짧은 코드워드를 배정하면 평균 길이가 줄어듭니다.

## 구현 시 주의사항

1. `log(0)` 방지용 epsilon 처리
2. 확률 합이 1인지 정규화 확인
3. 단위(bit/nat) 혼동 방지
4. KL 방향(`p||q`) 명시

이 네 가지를 놓치면 숫자는 나오지만 해석은 틀릴 수 있습니다. 정보이론 코드는 특히 "정의에 충실한 구현"이 중요합니다.


## 퍼플렉서티와 엔트로피 연결

언어 모델 평가에서 자주 보는 퍼플렉서티는 엔트로피의 지수 형태입니다.

```python
import math

def perplexity(cross_entropy_bits: float) -> float:
    return 2 ** cross_entropy_bits
```

값이 낮을수록 모델이 다음 토큰 분포를 더 잘 맞힌다는 뜻입니다. 즉 퍼플렉서티는 독립 지표가 아니라 교차 엔트로피를 해석하기 쉬운 척도로 바꾼 것입니다.


## 적용 연습 시나리오

아래 시나리오는 이번 장 개념을 실제 엔지니어링 작업으로 연결하기 위한 공통 훈련 틀입니다. 시리즈 전편에서 재사용할 수 있도록 질문 구조를 동일하게 유지했습니다.

### 시나리오 A — 요구사항을 수학 문장으로 바꾸기

1. 요구사항 문장을 한 줄로 복사합니다.
2. 입력 집합, 출력 집합, 금지 조건을 분리합니다.
3. 성공 조건을 불변식 형태로 다시 씁니다.
4. 경계 사례 3개를 고릅니다.

이 과정의 목적은 구현 전 설계 명확화입니다. 코드 한 줄을 쓰지 않아도 모호한 요구사항을 빠르게 드러낼 수 있습니다.

### 시나리오 B — 작은 코드로 검증 자동화하기

```python
from dataclasses import dataclass

@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


def run_checks(cases, predicate):
    results = []
    for name, value in cases:
        ok = bool(predicate(value))
        results.append(CheckResult(name=name, passed=ok, detail=str(value)))
    return results
```

핵심은 정답을 크게 만들기보다 검증 루프를 작게 만드는 것입니다. 작은 루프가 있으면 개념 변경이 생겨도 빠르게 회귀 검사를 돌릴 수 있습니다.

### 시나리오 C — 실패를 문서화된 학습으로 전환하기

실패를 발견했을 때 바로 코드 패치로 들어가기보다 아래 순서로 기록하면 재발 방지 효과가 큽니다.

- 어떤 가정이 틀렸는가
- 어떤 입력에서 처음 실패했는가
- 실패를 막는 최소 불변식은 무엇인가
- 테스트와 문서에 무엇을 추가했는가

이 네 항목은 구현 스타일과 무관하게 적용됩니다. 수학 학습이 실무 가치로 전환되는 지점은 공식 암기가 아니라 실패 원인을 추상화해 재사용 가능한 규칙으로 남기는 데 있습니다.

### 시나리오 D — 성능과 정확도 균형 점검

아래 표 형식으로 현재 선택을 정리하면 의사결정이 명확해집니다.

| 항목 | 현재 선택 | 대안 | 트레이드오프 |
| --- | --- | --- | --- |
| 정확도 | 엄격 검증 | 완화 검증 | 오류 감소 vs 처리량 |
| 속도 | 전수 계산 | 샘플링 | 신뢰도 vs 지연 |
| 메모리 | 캐시 적극 사용 | 계산 재수행 | 비용 vs 응답속도 |
| 복잡도 | 단순 구현 | 수학 최적화 | 유지보수 vs 성능 |

이 표를 업데이트하면서 팀이 같은 기준으로 토론하면, 개인 직관에 의존한 논쟁이 줄어듭니다.

### 시나리오 E — 장기 학습 루프

- 매주 한 개념을 선택해 15줄 내외의 파이썬 예제로 재구현합니다.
- 예제를 한 문장 명제로 요약합니다.
- 반례를 최소 1개 찾습니다.
- 다음 주 예제와 연결되는 질문을 남깁니다.

장기적으로는 이 루프가 개인 위키가 됩니다. 시리즈를 한 번 읽고 끝내는 대신, 각 장의 핵심을 실행 가능한 지식으로 축적할 수 있습니다.

이 섹션은 분량 보강용이 아니라 재사용 가능한 작업 템플릿입니다. 실제 팀 문서, 코드 리뷰, 회고 문서에 그대로 가져다 쓸 수 있도록 의도적으로 일반화했습니다.

## 추가 메모: 로그 밑과 단위 통일

실험 노트에서 `log2`와 자연로그를 섞으면 해석 혼선이 생깁니다. 엔트로피 단위를 bit로 쓸지 nat로 쓸지 문서 상단에 고정하고, 라이브러리 기본값을 확인해 변환식을 함께 기록하는 습관이 필요합니다.

### 엔트로피 계산 Python 코드

```python
import math

def entropy(probs):
    return -sum(p * math.log2(p) for p in probs if p > 0)

print(entropy([0.5, 0.5]))
print(entropy([0.9, 0.1]))
```

균등 분포가 더 큰 엔트로피를 갖는 이유는 결과 예측이 더 어렵기 때문입니다. 엔트로피는 불확실성의 평균 크기를 비트 단위로 나타냅니다.

### 결정트리 정보이득

```python
def information_gain(parent_entropy, left_weight, left_entropy, right_weight, right_entropy):
    child_entropy = left_weight * left_entropy + right_weight * right_entropy
    return parent_entropy - child_entropy

print(information_gain(1.0, 0.4, 0.0, 0.6, 0.9183))
```

정보이득은 분할 전후 불확실성 감소량입니다. 결정트리는 이 값을 최대화하는 특징을 선택해 분기를 만듭니다.

### 허프만 코딩 핵심 아이디어

허프만 코딩은 자주 등장하는 기호에 짧은 코드를 배정해 평균 비트 길이를 줄입니다. 접두부 코드 조건을 만족하므로 복호화가 안전합니다.

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

print(huffman_lengths({'A':45,'B':13,'C':12,'D':16,'E':9,'F':5}))
```

정보이론을 압축 구현과 연결해 보면, 엔트로피가 단지 추상 지표가 아니라 실제 저장/전송 비용의 하한이라는 점이 더 분명해집니다.

## 처음 질문으로 돌아가기

- **정보의 양은 무엇으로 측정할까요?**
  - 본문의 기준은 정보이론를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **엔트로피는 왜 평균 정보량이라고 부를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **교차 엔트로피는 왜 손실 함수로 자주 쓰일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Math for CS 101 (1/10): CS에 수학이 필요한 이유](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): 논리와 증명](./02-logic-and-proofs.md)
- [Math for CS 101 (3/10): 집합과 함수](./03-sets-and-functions.md)
- [Math for CS 101 (4/10): 그래프](./04-graphs.md)
- [Math for CS 101 (5/10): 조합](./05-combinatorics.md)
- [Math for CS 101 (6/10): 확률](./06-probability.md)
- [Math for CS 101 (7/10): 선형대수](./07-linear-algebra.md)
- [Math for CS 101 (8/10): 미분](./08-calculus.md)
- **정보이론 (현재 글)**
- 알고리즘과 수학 (예정)

<!-- toc:end -->

## 참고 자료

- [Information Theory - Stanford Encyclopedia](https://plato.stanford.edu/entries/information-theory/)
- [A Mathematical Theory of Communication - Shannon](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)
- [Elements of Information Theory - Cover and Thomas](https://www.wiley.com/en-us/Elements+of+Information+Theory%2C+2nd+Edition-p-9780471241959)
- [SciPy Stats Entropy Documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.entropy.html)
- [SciPy GitHub repository](https://github.com/scipy/scipy)

Tags: Math, InformationTheory, Entropy, Compression, Beginner
