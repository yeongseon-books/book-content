---
title: "Math for CS 101 (7/10): 선형대수"
series: math-for-cs-101
episode: 7
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
  - Math
  - LinearAlgebra
  - Vectors
  - Matrices
  - Beginner
last_reviewed: '2026-05-12'
seo_description: 선형대수로 데이터와 변환을 한 문법으로 읽는 감각을 입문자용으로 정리합니다
---

# Math for CS 101 (7/10): 선형대수

선형대수라는 이름은 많은 입문자에게 벽처럼 느껴집니다. 기호가 많고, 행렬이 나오고, 갑자기 차원이 늘어나기 때문입니다. 그런데 실무 관점에서 보면 선형대수는 복잡한 수학 과목이라기보다 데이터를 압축해서 다루는 공통 문법에 가깝습니다.

추천 시스템의 임베딩, 차원 축소, 카메라 변환, 신경망의 순전파는 모두 벡터와 행렬 연산으로 다시 읽을 수 있습니다. 결국 숫자 묶음을 어떻게 표현하고 어떻게 변환할지를 다루는 문제이기 때문입니다.

이 글은 Math for CS 101 시리즈의 7번째 글입니다.

여기서는 선형대수를 데이터와 변환을 같은 문법으로 다루는 도구로 보고, 벡터, 행렬, 내적, 전치, 행렬곱의 감각을 실전 쪽으로 연결해 보겠습니다.

## 먼저 던지는 질문

- 벡터와 행렬은 데이터를 어떻게 표현할까요?
- 내적은 왜 유사도 계산의 핵심 연산일까요?
- 행렬곱은 단순 반복 계산과 무엇이 다를까요?

## 큰 그림

![Math for CS 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/07/07-01-concept-at-a-glance.ko.png)

*Math for CS 101 7장 흐름 개요*
이 그림은 선형대수를 벡터 공간과 변환으로 이해하고, 추천 시스템과 머신러닝에 어떻게 쓰이는지 보여줍니다.

> 벡터와 행렬은 데이터 변환을 구조화하고, 추천 시스템과 신경망의 핵심 언어가 됩니다.

## 왜 중요한가

추천 시스템의 임베딩, 차원 축소, 카메라 변환, 신경망의 순전파는 모두 벡터와 행렬 연산으로 읽을 수 있습니다. 이름만 들으면 어렵지만, 결국 숫자 묶음을 더 잘 표현하고 더 빠르게 변환하는 방법이라고 생각하면 접근이 쉬워집니다.

선형대수의 힘은 반복문 여러 개를 하나의 연산 의미로 묶어 준다는 데 있습니다. 각 숫자를 따로 보지 않고 공간 안의 방향과 변환으로 볼 수 있게 되면, 코드와 모델을 동시에 이해하기 쉬워집니다. 그래서 선형대수는 계산 기술이면서 해석 기술이기도 합니다.

---

## 머릿속에 먼저 둘 관점

선형대수를 처음 배울 때 가장 도움이 되는 문장은 이것입니다. **벡터는 데이터이고, 행렬은 그 데이터를 움직이는 변환**이라는 점입니다. 이 관점만 잡아도 많은 식이 훨씬 덜 위협적으로 보입니다.

벡터는 방향과 크기를 가진 값의 묶음입니다. 행렬은 여러 벡터를 모아 놓은 구조이면서 동시에 하나의 변환기로도 읽을 수 있습니다. 내적은 두 벡터가 얼마나 같은 방향을 보는지 알려 주고, 전치는 데이터를 행 기준에서 열 기준으로 다시 읽게 합니다. 행렬곱은 변환을 연달아 적용하는 방식입니다.

기저는 이 공간을 어떤 축으로 설명할지를 정하는 기준입니다. 기저를 이해하면 숫자가 무엇을 뜻하는지, 좌표가 왜 그렇게 보이는지 해석이 쉬워집니다.

## 한 장으로 보는 선형대수의 기본 구조

---

## 다섯 단계로 보는 선형대수 기초

### 첫 번째 단계 — 벡터를 더합니다

```python
def vadd(a, b):
    return [x + y for x, y in zip(a, b)]
```

가장 단순한 연산이지만, 같은 차원의 데이터를 같은 위치끼리 더한다는 감각을 익히기에 좋습니다. 벡터를 값의 나열이 아니라 하나의 객체로 보는 출발점이기도 합니다.

### 두 번째 단계 — 내적으로 방향 관계를 봅니다

```python
def dot(a, b):
    return sum(x * y for x, y in zip(a, b))
```

내적은 추천 점수, 유사도, 투영 계산에 자주 등장합니다. 두 벡터가 얼마나 비슷한 방향을 향하는지 보는 데도 쓰입니다. 그래서 실무에서는 단순 계산보다 비교의 문법으로 더 자주 체감됩니다.

### 세 번째 단계 — 행렬을 변환기로 읽습니다

```python
def matvec(M, v):
    return [dot(row, v) for row in M]
```

행렬을 변환기로 보면 이해가 쉬워집니다. 벡터 하나를 입력하면 변환된 벡터가 나옵니다. 결국 행렬은 숫자 표라기보다 방향과 크기를 다시 조합하는 장치입니다.

### 네 번째 단계 — 관점을 바꿉니다

```python
def transpose(M):
    return [list(col) for col in zip(*M)]
```

행 중심으로 보던 데이터를 열 중심으로 다시 읽고 싶을 때 전치가 필요합니다. 선형대수뿐 아니라 데이터 전처리에서도 자주 나옵니다. 무엇을 행으로 볼지, 무엇을 열로 볼지 바뀌면 해석도 달라집니다.

### 다섯 번째 단계 — 변환을 이어 붙입니다

```python
def matmul(A, B):
    Bt = transpose(B)
    return [[dot(row, col) for col in Bt] for row in A]
```

행렬곱은 변환을 연결하는 방법입니다. 하나의 변환 뒤에 다른 변환을 이어 붙이는 구조로 이해하면 훨씬 자연스럽습니다. 복잡한 파이프라인도 결국 작은 변환의 합성으로 읽을 수 있습니다.

---

## 이 코드에서 먼저 볼 점

- 내적은 여러 연산의 공통 핵심입니다.
- 전치는 데이터 관점을 바꾸는 도구입니다.
- 행렬곱은 내적들의 격자로 읽을 수 있습니다.
- 차원 일치는 선형대수에서 가장 기본적인 안전장치입니다.
- 벡터화는 의미 압축이면서 동시에 성능 개선과도 연결됩니다.

---

## 어디서 자주 헷갈릴까요?

행과 열 차원을 맞추지 않는 실수가 가장 흔합니다. 선형대수에서 많은 버그는 계산을 못해서가 아니라, 어떤 축이 무엇을 뜻하는지 명확히 적지 않아서 생깁니다.

행렬곱이 교환법칙을 따른다고 생각하는 것도 전형적인 오해입니다. `A @ B`와 `B @ A`는 대개 같은 의미가 아닙니다. 변환 순서가 다르면 결과도 달라집니다.

내적과 외적을 혼동하거나, 전치가 원본 데이터를 바꾼다고 오해하는 일도 자주 나옵니다. 선형대수에서는 연산 정의 자체보다 그 연산이 공간 해석에서 어떤 의미를 가지는지 함께 봐야 합니다.

---

## 실무에서는 이렇게 생각한다

임베딩 검색은 벡터 유사도로 동작하고, 추천 시스템은 행렬 분해나 점수 계산에 선형대수를 씁니다. 3D 그래픽스에서는 좌표 변환이 핵심이며, 신경망 계산도 결국 큰 행렬 연산으로 볼 수 있습니다. 그래서 선형대수는 특정 도메인 전용 지식이 아니라, 현대 소프트웨어 시스템에서 아주 넓게 재사용되는 공통 기반입니다.

좋은 엔지니어는 숫자 배열을 보면 먼저 차원과 의미를 묻습니다. 이 축은 무엇을 뜻하는지, 이 행렬은 데이터인지 변환인지, 전치가 왜 필요한지, 수치 안정성 문제는 없는지 같이 봅니다.

---

## 체크리스트

- [ ] 벡터와 행렬의 차이를 설명할 수 있습니다.
- [ ] 내적이 무엇을 계산하는지 말할 수 있습니다.
- [ ] 행렬곱이 가능한 차원 조건을 확인할 수 있습니다.
- [ ] 전치가 필요한 상황을 예로 들 수 있습니다.
- [ ] 수치 의미와 축 해석을 함께 볼 수 있습니다.

## 연습 문제

1. 내적을 한 줄로 정의해 보세요.
2. 전치를 한 문장으로 설명해 보세요.
3. 행렬곱이 가능하려면 어떤 조건이 필요한지 써 보세요.

## 정리

선형대수는 숫자 배열을 더 높은 수준의 구조로 보게 해 줍니다. 벡터와 행렬, 내적, 전치, 행렬곱을 이해하면 데이터 처리와 모델 계산을 훨씬 압축된 언어로 설명할 수 있습니다. 다음 글에서는 변화와 최적화를 다루는 미분으로 넘어가겠습니다.


## NumPy로 보는 벡터/행렬 연산

선형대수 감각을 가장 빠르게 익히는 방법은 `numpy`로 같은 연산을 직접 만져 보는 것입니다.

```python
import numpy as np

A = np.array([[1.0, 2.0], [3.0, 4.0]])
B = np.array([[2.0, 0.0], [1.0, 2.0]])
v = np.array([5.0, 6.0])

mat_vec = A @ v
mat_mul = A @ B
transposed = A.T
```

위 코드에서 `@`는 단순 곱셈이 아니라 선형 변환 합성입니다. 같은 연산자라도 의미가 다르다는 점을 명확히 잡아야 합니다.

## 고유값/고유벡터 계산 맛보기

고유값은 특정 방향이 변환 후에도 방향이 유지되는 비율을 의미합니다.

```python
eigvals, eigvecs = np.linalg.eig(A)
```

추천 시스템, PCA, 동역학 안정성 분석에서 고유값은 시스템의 지배적 패턴을 요약하는 도구로 쓰입니다. 모든 값을 보지 않고도 구조를 읽는 압축 도구라고 이해하면 좋습니다.

## 기하 변환 예시

2차원 좌표를 회전시키는 행렬은 다음처럼 표현됩니다.

```python
def rotation(theta_rad: float) -> np.ndarray:
    c, s = np.cos(theta_rad), np.sin(theta_rad)
    return np.array([[c, -s], [s, c]])

p = np.array([1.0, 0.0])
p_rot = rotation(np.pi / 2) @ p
```

행렬을 "숫자 표"가 아니라 "공간을 바꾸는 함수"로 읽으면 선형대수의 대부분이 훨씬 직관적으로 연결됩니다.

## 차원 해석 표

| 표현 | 의미 | 예시 |
| --- | --- | --- |
| `(n,)` | 길이 n 벡터 | 사용자 임베딩 |
| `(m, n)` | m행 n열 행렬 | 배치 입력 |
| `(n, k)` | n차원 -> k차원 변환 | 가중치 행렬 |

차원은 타입입니다. 타입 검사가 없으면 런타임 오류가 나는 것처럼, 차원 해석이 없으면 수학적 의미 오류가 발생합니다.

## 수치 안정성 메모

- 역행렬을 직접 구하기보다 가능하면 선형 시스템 `Ax=b`를 푸는 형태(`np.linalg.solve`)를 우선합니다.
- 매우 큰/작은 값이 섞이면 정규화로 스케일을 맞춥니다.
- 조건수가 큰 행렬은 오차에 민감하므로 결과 해석에 주의합니다.

이 포인트는 이론보다 구현에서 더 자주 문제를 일으키는 부분입니다.

## 선형대수 실무 질문

1. 이 행렬은 데이터인가 변환인가
2. 각 축은 무엇을 의미하는가
3. 내적 결과가 점수인지 거리 유사도인지
4. 수치 오차에 민감한가

선형대수는 계산보다 해석의 일관성이 더 중요합니다. 축 의미를 잃지 않으면 모델 디버깅 속도가 크게 올라갑니다.


## 벡터 유사도 계산 예제

추천과 검색에서 가장 자주 쓰는 계산은 코사인 유사도입니다.

```python
import numpy as np


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)
```

내적만 쓰면 벡터 크기 차이에 민감하지만, 코사인 유사도는 방향 중심 비교라서 문서/사용자 임베딩 비교에 잘 맞습니다. 이 선택 자체가 선형대수 해석의 결과입니다.


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

## 추가 메모: 선형대수 디버깅 순서

행렬 계산이 예상과 다를 때는 값보다 축부터 확인합니다. 입력 텐서 축 정의, 전치 여부, 브로드캐스팅 적용 여부를 먼저 점검한 뒤 수치 범위를 확인하면 대부분의 오류를 빠르게 좁힐 수 있습니다. 특히 모델 추론 단계에서는 NaN 발생 지점 추적을 자동화해 두는 것이 좋습니다.

덧붙여, 연산 단위 테스트를 축별로 분리하면 회귀를 훨씬 빠르게 잡을 수 있습니다.

### NumPy 행렬 연산 기본 패턴

```python
import numpy as np

A = np.array([[1.0, 2.0], [3.0, 4.0]])
B = np.array([[2.0, 0.0], [1.0, 2.0]])
v = np.array([1.0, -1.0])

print("A+B", A + B)
print("A@B", A @ B)
print("A@v", A @ v)
```

벡터화 연산은 반복문보다 빠를 뿐 아니라 수식 의미가 그대로 보인다는 장점이 있습니다. 코드 리뷰에서도 의도 전달이 쉬워집니다. NumPy의 `@` 연산자는 Python 3.5부터 지원되며, `np.dot`보다 가독성이 높습니다.

### 고유값 계산과 해석

```python
eigvals, eigvecs = np.linalg.eig(A)
print("eigvals", eigvals)
print("eigvecs", eigvecs)
```

고유값은 변환 후에도 방향이 유지되는 축의 스케일을 나타냅니다. 안정성 분석, PCA, 동적 시스템 해석에서 중요한 신호입니다.

### 기하학적 변환 예제

```python
theta = np.deg2rad(30)
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
pts = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
rot = pts @ R.T
print(rot)
```

회전, 스케일, 이동을 행렬로 표현하면 변환 합성이 명확해집니다. 그래픽스와 로보틱스에서는 연산 순서가 결과를 결정하므로 좌표계 약속을 엄격히 관리해야 합니다.

### 수치 안정성 체크

조건수가 큰 행렬은 작은 입력 오차를 크게 증폭합니다. `np.linalg.cond`로 조건수를 점검하고, 필요하면 정규화나 분해 기반 풀이를 선택해야 합니다.


### PCA로 차원 축소 구현하기

고차원 데이터를 시각화하거나 모델 입력으로 쓸 때 차원 축소가 필요합니다. PCA(Principal Component Analysis)는 분산이 가장 큰 방향을 찾아 투영하는 방법입니다.

```python
import numpy as np

def pca(X: np.ndarray, n_components: int = 2) -> np.ndarray:
    """데이터 X를 n_components 차원으로 축소합니다."""
    # 1. 평균 제거 (중심화)
    X_centered = X - X.mean(axis=0)

    # 2. 공분산 행렬 계산
    cov = np.cov(X_centered, rowvar=False)

    # 3. 고유값/고유벡터 분해
    eigvals, eigvecs = np.linalg.eigh(cov)

    # 4. 고유값 크기 순으로 정렬
    idx = np.argsort(eigvals)[::-1]
    eigvecs = eigvecs[:, idx]

    # 5. 상위 n_components개 축으로 투영
    W = eigvecs[:, :n_components]
    return X_centered @ W

# 예시: 5차원 데이터를 2차원으로
np.random.seed(42)
X = np.random.randn(100, 5)
X_reduced = pca(X, 2)
print(f"original: {X.shape} -> reduced: {X_reduced.shape}")
print(f"explained direction shape: (5, 2)")
```

PCA의 핵심은 공분산 행렬의 고유벡터가 분산 최대 방향을 나타낸다는 점입니다. 고유값이 크면 그 축이 정보를 많이 담고 있다는 뜻입니다. 임베딩 시각화, 노이즈 제거, 특징 선택 등에 널리 쓰입니다. 실무에서는 `sklearn.decomposition.PCA`를 쓰지만, 내부 원리를 이해하면 `n_components` 선택과 설명력(설명된 분산 비율) 해석을 더 잘할 수 있습니다.

### 코사인 유사도와 임베딩 검색

백터 간 유사도 측정은 추천 시스템, 검색 엔진, RAG 파이프라인의 기본입니다.

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """두 벡터 사이의 코사인 유사도를 계산합니다."""
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def batch_cosine_similarity(query: np.ndarray, corpus: np.ndarray) -> np.ndarray:
    """쿼리 벡터와 코퍼스 전체의 유사도를 일괄 계산합니다."""
    norms = np.linalg.norm(corpus, axis=1)
    norms[norms == 0] = 1.0  # zero-division 방지
    normalized = corpus / norms[:, np.newaxis]
    query_norm = query / (np.linalg.norm(query) or 1.0)
    return normalized @ query_norm

# 예시
corpus = np.array([[1, 0, 1], [0, 1, 1], [1, 1, 0]], dtype=float)
query = np.array([1, 0, 0], dtype=float)
scores = batch_cosine_similarity(query, corpus)
print(f"similarities: {scores}")  # 첫 번째와 세 번째가 높음
```

내적을 정규화한 것이 코사인 유사도입니다. 크기(norm)를 제거하고 방향만 비교하므로, 문서 길이에 독립적인 유사도를 얻을 수 있습니다. 임베딩 기반 검색(vector search)에서는 쿼리와 문서를 모두 정규화한 뒤 내적만 계산해 순위를 매깁니다. FAISS, Pinecone, Weaviate 같은 벡터 DB가 이 연산을 GPU/SIMD로 가속하는 이유입니다.

### 희소 행렬(Sparse Matrix) 활용

대부분의 실무 행렬은 0이 압도적으로 많습니다. 희소 행렬 포맷을 쓰면 메모리와 연산 비용을 크게 줄일 수 있습니다.

```python
from scipy import sparse
import numpy as np

# 10000x10000 행렬에서 0.1%만 비영인 경우
n = 10000
density = 0.001
A_sparse = sparse.random(n, n, density=density, format='csr')

# 메모리 비교
dense_memory = n * n * 8  # float64
sparse_memory = A_sparse.data.nbytes + A_sparse.indices.nbytes + A_sparse.indptr.nbytes
print(f"dense: {dense_memory / 1e6:.1f} MB")
print(f"sparse: {sparse_memory / 1e6:.1f} MB")
print(f"ratio: {sparse_memory / dense_memory:.4f}")

# 희소 행렬-벡터 곱
x = np.random.randn(n)
result = A_sparse @ x
print(f"result shape: {result.shape}")
```

추천 시스템의 사용자-아이템 행렬, 그래프의 인접 행렬, NLP의 TF-IDF 행렬은 모두 희소 행렬입니다. dense로 다루면 메모리 부족으로 스케일링이 막힙니다. CSR/CSC 포맷의 특성을 이해하면 어떤 연산이 빠른지 예측할 수 있습니다.

### 선형 시스템 풀기: Ax = b

많은 실무 문제가 선형 시스템 Ax = b 형태로 귀결됩니다. 회귀 분석, 회로 방정식, 최적화 문제 등이 모두 이 구조입니다.

```python
import numpy as np

# 3개의 방정식, 3개의 미지수
A = np.array([
    [2, 1, -1],
    [-3, -1, 2],
    [-2, 1, 2]
], dtype=float)
b = np.array([8, -11, -3], dtype=float)

# 직접 풀기
x = np.linalg.solve(A, b)
print(f"solution: {x}")  # [2. 3. -1.]

# 검증
residual = np.linalg.norm(A @ x - b)
print(f"residual: {residual:.2e}")  # ~0

# 조건수 확인
cond = np.linalg.cond(A)
print(f"condition number: {cond:.2f}")
```

조건수가 크면(예: 10⁶ 이상) 입력의 작은 오차가 결과를 크게 흔들 수 있습니다. 이 경우 정규화, SVD 기반 의사역행렬, 또는 반복법(CG, GMRES)을 고려해야 합니다. 수치 선형대수에서 "정답이 나왔다"고 끝나는 것이 아니라 "이 답이 얼마나 믿을 만한가?"를 함께 평가하는 습관이 중요합니다.

## 처음 질문으로 돌아가기

- **벡터와 행렬은 데이터를 어떻게 표현할까요?**
  - 본문의 기준은 선형대수를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **내적은 왜 유사도 계산의 핵심 연산일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **행렬곱은 단순 반복 계산과 무엇이 다를까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Math for CS 101 (1/10): CS에 수학이 필요한 이유](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): 논리와 증명](./02-logic-and-proofs.md)
- [Math for CS 101 (3/10): 집합과 함수](./03-sets-and-functions.md)
- [Math for CS 101 (4/10): 그래프](./04-graphs.md)
- [Math for CS 101 (5/10): 조합](./05-combinatorics.md)
- [Math for CS 101 (6/10): 확률](./06-probability.md)
- **선형대수 (현재 글)**
- 미분 (예정)
- 정보이론 (예정)
- 알고리즘과 수학 (예정)

<!-- toc:end -->

## 참고 자료

- [Linear Algebra - 3Blue1Brown](https://www.3blue1brown.com/topics/linear-algebra)
- [Linear Algebra - Khan Academy](https://www.khanacademy.org/math/linear-algebra)
- [Introduction to Linear Algebra - Strang](https://math.mit.edu/~gs/linearalgebra/)
- [NumPy Linear Algebra Documentation](https://numpy.org/doc/stable/reference/routines.linalg.html)
- [NumPy GitHub repository](https://github.com/numpy/numpy)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/math-for-cs-101/ko)

Tags: Math, LinearAlgebra, Vectors, Matrices, Beginner
