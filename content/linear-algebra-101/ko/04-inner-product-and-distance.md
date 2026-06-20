---
series: linear-algebra-101
episode: 4
title: "Linear Algebra 101 (4/10): 내적과 거리"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - LinearAlgebra
  - InnerProduct
  - Distance
  - DataScience
  - Beginner
seo_description: 내적과 코사인 유사도, 다양한 거리 함수의 의미를 벡터 비교와 임베딩 검색 관점에서 그 차이를 명확하게 정리합니다.
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (4/10): 내적과 거리

벡터를 표현할 수 있게 되면 다음 질문이 바로 따라옵니다. 두 벡터는 얼마나 비슷한가, 얼마나 떨어져 있는가 하는 질문입니다. 추천 시스템, 벡터 검색, 임베딩 비교가 모두 결국 이 질문을 수치로 바꾸는 작업입니다.

이 글은 Linear Algebra 101 시리즈의 4번째 글입니다.

여기서는 내적, 코사인 유사도, 유클리드 거리와 맨해튼 거리를 한 흐름으로 연결해 보겠습니다.

![Linear Algebra 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/04/04-01-concept-at-a-glance.ko.png)
*Linear Algebra 101 4장 흐름 개요*
> 내적과 거리는 벡터 비교의 두 기초입니다. 내적은 방향 관계를 재고, 거리는 점 사이의 차이를 잽니다. 어느 것을 쓸지는 문제의 특성에 따라 달라집니다.

## 이 글에서 다룰 문제

- 내적은 왜 숫자 하나로 나올까요?
- 코사인 유사도는 내적과 어떻게 연결될까요?
- 유클리드 거리와 맨해튼 거리는 무엇이 다를까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

문서 임베딩 검색에서는 방향 유사성이 중요해 코사인 유사도를 많이 씁니다. 반면 실제 좌표 차이의 크기가 중요한 문제에서는 유클리드 거리나 다른 거리 함수가 더 자연스럽습니다. 따라서 벡터 비교에서 무엇을 비슷하다고 부를지 먼저 정해야 합니다.

실무에서 이 감각이 없으면 메트릭 선택이 습관이 됩니다. 아무 이유 없이 코사인을 쓰거나, 무조건 L2 거리를 쓰는 식입니다. 하지만 비교 기준 하나만 바뀌어도 검색 결과, 추천 순위, 군집 구조가 크게 달라질 수 있습니다.

## 핵심 용어 정리

내적은 같은 계산을 두 가지로 읽게 해 줍니다. 좌표별 곱의 합으로 볼 수도 있고, 길이와 각도의 관계로 볼 수도 있습니다. 거리는 벡터 차이의 크기입니다.

- **내적**: `v · w = sum(v_i * w_i)` 형태의 스칼라입니다.
- **코사인 유사도**: `(v · w) / (||v|| ||w||)`로 방향만 비교합니다.
- **직교**: 내적이 0인 관계입니다.
- **유클리드 거리**: `||v - w||`로 표현하는 직선 거리입니다.
- **맨해튼 거리**: `sum(|v_i - w_i|)`로 계산하는 격자형 거리입니다.

## 거리 측도 비교

벡터 비교에서 거리 함수는 문제 특성에 따라 달라집니다. 아래 표는 주요 거리 측도와 그 특징, 적합한 상황을 정리한 것입니다.

| 거리 | 공식 | 적합 상황 |
| --- | --- | --- |
| 유클리드 (L2) | `sqrt(sum((v_i - w_i)^2))` | 일반적 공간 거리, 물리적 거리 |
| 맨해튼 (L1) | `sum(|v_i - w_i|)` | 격자 이동, 이상치 강건성 필요 |
| 코사인 거리 | `1 - cos(v, w)` | 방향 비교, 크기 무시 |
| 마할라노비스 | `sqrt((v-w)^T S^{-1} (v-w))` | 피처 간 상관관계 반영 |

유클리드 거리는 가장 직관적이지만, 희소 벡터나 고차원에서는 분별력이 떨어질 수 있습니다. 맨해튼 거리는 이상치에 강하고, 코사인은 정규화 효과가 내장되어 문서 검색에 적합합니다.

## 읽기 전과 후

읽기 전에는 내적을 단순한 곱셈-덧셈 공식으로 보기 쉽습니다. 그러면 왜 코사인 유사도가 등장하는지, 왜 거리 함수에 따라 결과 해석이 달라지는지 잘 연결되지 않습니다.

읽은 후에는 내적이 방향 정렬을, 거리가 분리 정도를 보여 준다는 점이 분명해집니다. 같은 두 벡터를 놓고도 무엇을 묻느냐에 따라 다른 척도를 써야 한다는 감각이 생깁니다.

## 다섯 단계로 비교 기준 익히기

### 1단계 — 벡터 준비

```python
import numpy as np
v = np.array([1.0, 2.0, 3.0])
w = np.array([4.0, 5.0, 6.0])
print("v:", v, "w:", w)
```

먼저 비교할 두 벡터를 준비합니다. 예제는 단순하지만 내적과 거리의 차이를 한눈에 보기 좋습니다.

### 2단계 — 내적

```python
print("v . w:", np.dot(v, w))  # 32.0
print("v . w:", v @ w)         # 같은 결과
```

내적은 같은 위치의 원소를 곱해 모두 더한 값입니다. `np.dot`과 `@` 표기가 함께 쓰입니다.

### 3단계 — 코사인 유사도

```python
cos_sim = (v @ w) / (np.linalg.norm(v) * np.linalg.norm(w))
print("cosine similarity:", cos_sim)  # ~0.975
```

여기서는 길이의 영향을 나눠 제거합니다. 그래서 코사인 유사도는 크기가 아니라 방향 유사성을 보여 줍니다.

### 4단계 — 유클리드 거리

```python
print("Euclidean:", np.linalg.norm(v - w))  # ~5.196
```

유클리드 거리는 두 벡터 차이의 길이입니다. 두 점 사이를 직선으로 잰다고 생각하면 됩니다.

### 5단계 — 맨해튼 거리

```python
print("Manhattan:", np.sum(np.abs(v - w)))  # 9.0
```

맨해튼 거리는 좌표별 차이의 절댓값을 모두 더합니다. 어떤 문제에서는 직선 거리보다 이 방식이 더 자연스러울 수 있습니다.

## 기하학적으로 보는 내적

내적은 두 벡터의 길이와 각도 정보를 동시에 담습니다.

\[
a \cdot b = \|a\|\,\|b\|\cos\theta
\]

- `> 0`: 같은 쪽 방향 (예각)
- `= 0`: 직교 (90도)
- `< 0`: 반대쪽 방향 (둔각)

```python
import numpy as np

# 직교 확인
a = np.array([1.0, 0.0])
b = np.array([0.0, 1.0])
print('직교 내적:', np.dot(a, b))  # 0.0

# 각도 계산
u = np.array([1.0, 1.0])
v = np.array([1.0, 0.0])
cos_theta = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
theta_deg = np.degrees(np.arccos(cos_theta))
print('각도:', theta_deg, '도')  # 45.0
```

이 해석은 임베딩 검색에서 단순 점수 비교를 넘어, 왜 특정 결과가 상위에 올라왔는지 설명할 근거를 제공합니다.

## 비교 기준별 결과 차이

같은 벡터 쌍에 서로 다른 기준을 적용하면 결과가 달라집니다.

```python
import numpy as np

q = np.array([0.2, 0.8, 0.0])
d1 = np.array([0.1, 0.9, 0.0])
d2 = np.array([0.9, 0.1, 0.0])

def cosine(a, b):
    return (a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))

for name, d in [('d1', d1), ('d2', d2)]:
    print(name)
    print('  cosine =', round(cosine(q, d), 4))
    print('  L2     =', round(np.linalg.norm(q - d), 4))
    print('  L1     =', round(np.abs(q - d).sum(), 4))
```

`q`와 `d1`은 방향이 비슷하고, `q`와 `d2`는 방향이 다릅니다. 코사인 기준과 L2 기준이 다른 순위를 낼 수 있습니다. 어느 것이 더 나은지는 문제 정의에 달려 있습니다.

## 고차원에서 거리의 함정

고차원 공간에서는 모든 점이 비슷하게 멀리 있어 보이는 현상(차원의 저주)이 있습니다. 거리 기반 비교의 분별력이 떨어지는 주요 원인입니다.

```python
import numpy as np

rng = np.random.default_rng(42)

for d in [2, 10, 50, 100, 500]:
    samples = rng.normal(size=(100, d))
    distances = [np.linalg.norm(samples[0] - samples[i]) for i in range(1, 50)]
    mean_d = np.mean(distances)
    std_d = np.std(distances)
    print(f'dim={d:3d}: mean={mean_d:.2f}, std={std_d:.2f}, cv={std_d/mean_d:.3f}')
```

변동계수(cv = std/mean)가 차원이 높아질수록 줄어들면 분별력이 약해지는 것입니다. 해결 전략으로는 정규화 후 코사인 유사도 사용, PCA/UMAP으로 차원 축소, 근사 최근접 탐색(ANN) 사용이 있습니다.

## 사이파이 거리 함수 활용

SciPy는 다양한 거리 함수를 제공합니다. 실무에서는 직접 구현하는 대신 검증된 라이브러리를 사용하는 것이 안전합니다.

```python
import numpy as np
from scipy.spatial.distance import euclidean, cityblock, cosine, pdist, squareform

v = np.array([1.0, 2.0, 3.0])
w = np.array([4.0, 5.0, 6.0])

print('L2 distance :', euclidean(v, w))
print('L1 distance :', cityblock(v, w))
print('cosine dist :', cosine(v, w))  # 1 - cosine_similarity

# 여러 쌍 간 거리 행렬
points = np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=float)
dist_matrix = squareform(pdist(points, metric='euclidean'))
print('거리 행렬:\n', dist_matrix)
```

`scipy.spatial.distance`는 20가지 이상의 거리 함수를 지원하며, `pdist`와 `cdist`로 배치 계산도 효율적으로 수행할 수 있습니다.

## 메트릭 선택 가이드

| 상황 | 우선 선택 | 이유 |
| --- | --- | --- |
| 임베딩 검색/추천 | 코사인 유사도 | 방향 유사성이 핵심, 크기 편향 제거 |
| 좌표 기반 오차 | 유클리드 거리 | 실제 거리 해석이 직접적 |
| 희소 벡터/강인성 필요 | 맨해튼 거리 | 축별 변화량 합이 해석적 |
| 피처 간 상관 고려 | 마할라노비스 거리 | 상관 구조 반영, 이상치 탐지에 유리 |

추가로 고차원에서는 거리 집중 현상 때문에 L2 값 분별력이 떨어질 수 있습니다. 이 경우 정규화, 차원 축소(PCA), 또는 근사 최근접 탐색 전략을 함께 고려해야 합니다.

## 메트릭 선택 실패 진단

실무에서 잘못된 메트릭 선택은 묵시적으로 발생합니다. 아래 표는 증상과 원인, 대응 방법을 정리합니다.

| 증상 | 원인 | 진단 방법 | 대응 |
| --- | --- | --- | --- |
| 검색 결과가 길이가 긴 문서에 치우침 | 정규화 없이 내적 사용 | 상위 결과의 벡터 노름 확인 | 코사인 유사도로 변경 |
| 이상치 하나가 순위를 장악 | L2 거리 사용 + 이상치 포함 데이터 | 거리 분포 히스토그램 확인 | L1 거리 또는 robust scaling 적용 |
| 고차원 ANN 결과 정확도 저하 | 차원의 저주 + L2 분별력 감소 | cv(std/mean) 계산 | PCA/UMAP 후 재탐색 |
| 피처 스케일 차이가 결과를 지배 | 비정규화 L2 | 피처별 분산 확인 | StandardScaler 적용 후 비교 |
| 같은 데이터인데 군집 구조가 달라짐 | 메트릭 변경 | 군집별 거리 분포 대조 | 문제 정의와 메트릭 정렬 재검토 |

진단의 핵심은 "어떤 메트릭을 쓰든 결과가 같아야 한다"는 가정을 버리는 것입니다. 비교 기준 자체가 무엇을 '비슷하다'고 정의하는지를 결정합니다.

## 정규화가 메트릭에 미치는 영향

정규화 여부에 따라 같은 메트릭도 다른 결과를 냅니다.

```python
import numpy as np

# 크기가 다른 두 벡터 쌍
a_short = np.array([1.0, 1.0])
b_long  = np.array([10.0, 10.0])
c_diff  = np.array([1.1, 0.9])

def cosine_sim(x, y):
    return (x @ y) / (np.linalg.norm(x) * np.linalg.norm(y))

# 내적은 크기 영향을 받음
print('dot(a_short, b_long):', np.dot(a_short, b_long))  # 20.0
print('dot(a_short, c_diff):', np.dot(a_short, c_diff))  # 2.0

# 코사인은 방향만 비교
print('cos(a_short, b_long):', round(cosine_sim(a_short, b_long), 4))  # 1.0
print('cos(a_short, c_diff):', round(cosine_sim(a_short, c_diff), 4))  # ~0.98

# 방향이 같은 a_short와 b_long은 코사인 유사도 1.0
# 방향이 조금 다른 c_diff는 1.0보다 작음
```

내적은 `b_long`과의 값이 훨씬 크게 나오지만 코사인은 `b_long`과 `a_short`를 동일하게 봅니다. 이 차이가 임베딩 검색에서 크기 편향을 만들거나 제거하는 핵심입니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 내적과 원소별 곱을 같은 것으로 봄 | 스칼라가 아닌 배열이 결과로 나옴 | `np.dot(v, w)` 또는 `v @ w`로 내적 계산 |
| 코사인 계산에서 정규화 누락 | 크기가 큰 벡터가 유사도를 지배 | `/ (norm_a * norm_b)` 반드시 포함 |
| 영벡터에 코사인 유사도 적용 | `0/0` 발생, `nan` 반환 | 연산 전 `norm > 0` 조건 체크 |
| 고차원에서 L2 거리 맹신 | 분별력 없는 유사도 결과 | 정규화 후 코사인 또는 ANN 사용 |
| 메트릭 선택을 목적과 분리 | 평가 지표와 실제 의도 불일치 | 문제 정의 → 메트릭 선택 → 검증 순서 유지 |

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 메트릭을 먼저 고르고 나서 결과를 해석합니다. 문장 임베딩처럼 방향이 중요한 경우에는 정규화 후 코사인 유사도가 자연스럽고, 실제 양적 차이가 중요한 데이터에서는 거리 기반 접근이 더 맞을 수 있습니다.

또한 메트릭 선택이 모델 바깥의 전처리와 연결되어 있다는 점도 놓치지 않습니다. 정규화를 했는지, 스케일이 맞는지, 희소 벡터인지 밀집 벡터인지에 따라 비교 기준 자체가 달라져야 하기 때문입니다.

## 운영 체크리스트

- [ ] 내적을 계산하고 의미를 설명할 수 있습니다.
- [ ] 코사인 유사도를 계산할 수 있습니다.
- [ ] 유클리드 거리와 맨해튼 거리의 차이를 설명할 수 있습니다.
- [ ] 비슷함과 가까움이 같은 말이 아니라는 점을 이해했습니다.
- [ ] 메트릭 선택 전 데이터 정규화 여부를 확인합니다.
- [ ] 고차원 데이터에서 차원의 저주 영향을 점검합니다.

## 연습 문제

1. `v = [1, 0]`, `w = [0, 1]`의 내적을 계산하고 왜 직교인지 설명해 보세요.
2. 코사인 유사도가 `1`, `0`, `-1`이 되도록 벡터 쌍을 만들어 보세요.
3. 유클리드 거리와 맨해튼 거리가 다르게 나오는 예시를 구성해 보세요.

## 정리와 다음 글

내적은 벡터가 얼마나 같은 방향을 보는지 알려 주고, 코사인 유사도는 그중 방향만 떼어 내 비교합니다. 거리는 두 벡터가 공간에서 얼마나 떨어져 있는지를 보여 줍니다. 이 세 기준을 구분해서 읽을 수 있으면 벡터 검색, 추천, 군집화 같은 주제를 더 선명하게 볼 수 있습니다.

다음 글에서는 선형변환으로 넘어갑니다. 이제 벡터를 비교하는 기준을 익혔으니, 행렬이 벡터 공간 자체를 어떻게 바꾸는지도 같은 언어로 읽어 보겠습니다.

## 처음 질문으로 돌아가기

- **내적은 왜 숫자 하나로 나올까요?**
  - 내적은 두 벡터의 같은 위치 원소를 곱해 모두 더하는 연산이므로 항상 스칼라(숫자 하나)가 됩니다. 기하학적으로는 두 벡터의 길이와 사이각의 코사인을 곱한 값입니다. 이 하나의 숫자가 방향 정렬 정도를 압축해 담습니다.

- **코사인 유사도는 내적과 어떻게 연결될까요?**
  - 코사인 유사도는 내적을 두 벡터의 노름 곱으로 나눈 값입니다. 이렇게 하면 크기 정보를 제거하고 순수한 방향 유사성만 남습니다. 정규화된 벡터끼리의 내적이 바로 코사인 유사도와 같습니다.

- **유클리드 거리와 맨해튼 거리는 무엇이 다를까요?**
  - 유클리드 거리는 두 점을 직선으로 이은 거리이고, 맨해튼 거리는 격자를 따라 이동하는 거리입니다. 이상치가 있거나 축별 변화량 자체가 중요한 문제에서는 맨해튼 거리가 더 견고합니다. 어느 것이 더 나은지는 문제 정의에 달려 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linear Algebra 101 (1/10): 선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): 벡터](./02-vectors.md)
- [Linear Algebra 101 (3/10): 행렬](./03-matrices.md)
- **Linear Algebra 101 (4/10): 내적과 거리 (현재 글)**
- [Linear Algebra 101 (5/10): 선형변환](./05-linear-transformation.md)
- [Linear Algebra 101 (6/10): 기저와 차원](./06-basis-and-dimension.md)
- [Linear Algebra 101 (7/10): 고유값과 고유벡터](./07-eigenvalues-and-eigenvectors.md)
- [Linear Algebra 101 (8/10): 행렬 분해](./08-matrix-decomposition.md)
- [Linear Algebra 101 (9/10): PCA](./09-pca.md)
- [머신러닝에서의 선형대수](./10-linear-algebra-in-ml.md)

<!-- toc:end -->

## 참고 자료

- 시리즈 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/linear-algebra-101/ko
- [Wikipedia — Dot product](https://en.wikipedia.org/wiki/Dot_product)
- [Wikipedia — Cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
- [3Blue1Brown — Dot products](https://www.3blue1brown.com/lessons/dot-products)
- [scikit-learn — Pairwise metrics](https://scikit-learn.org/stable/modules/metrics.html)

Tags: LinearAlgebra, InnerProduct, Distance, DataScience, Beginner
