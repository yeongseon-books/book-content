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

## 먼저 던지는 질문

- 내적은 왜 숫자 하나로 나올까요?
- 코사인 유사도는 내적과 어떻게 연결될까요?
- 유클리드 거리와 맨해튼 거리는 무엇이 다를까요?

## 왜 중요한가

문서 임베딩 검색에서는 방향 유사성이 중요해 코사인 유사도를 많이 씁니다. 반면 실제 좌표 차이의 크기가 중요한 문제에서는 유클리드 거리나 다른 거리 함수가 더 자연스럽습니다. 따라서 벡터 비교에서 무엇을 비슷하다고 부를지 먼저 정해야 합니다.

실무에서 이 감각이 없으면 메트릭 선택이 습관이 됩니다. 아무 이유 없이 코사인을 쓰거나, 무조건 L2 거리를 쓰는 식입니다. 하지만 비교 기준 하나만 바뀌어도 검색 결과, 추천 순위, 군집 구조가 크게 달라질 수 있습니다. 내적과 거리는 공식을 외우는 주제가 아니라 비교의 기준을 선택하는 주제입니다.

## 거리 측도

벡터 비교에서 거리 함수는 문제 특성에 따라 달라집니다. 아래 표는 주요 거리 측도와 그 특징, 적합한 상황을 정리한 것입니다.

| 거리 | 공식 | 적합 상황 |
| --- | --- | --- |
| 유클리드 (L2) | `sqrt(sum((v_i - w_i)^2))` | 일반적 공간 거리, 물리적 거리 |
| 맨해튼 (L1) | `sum(|v_i - w_i|)` | 격자 이동, 이상치 강건성 필요 |
| 코사인 | `1 - cos(v, w)` | 방향 비교, 크기 무시 |
| 마할라노비스 | `sqrt((v-w)^T S^-1 (v-w))` | 피처 간 상관관계 반영 |

유클리드 거리는 가장 직관적이지만, 희소 벡터나 고차원에서는 분별력이 떨어질 수 있습니다. 맨해튼 거리는 이상치에 강하고, 코사인은 정규화 효과가 내장되어 문서 검색에 적합합니다. 마할라노비스 거리는 피처 간 상관관계를 고려해 이상치 탐지에 유용합니다.
## 핵심 개념 한눈에 보기

내적은 같은 계산을 두 가지로 읽게 해 줍니다. 좌표별 곱의 합으로 볼 수도 있고, 길이와 각도의 관계로 볼 수도 있습니다. 거리는 벡터 차이의 크기입니다. 그래서 내적은 정렬 정도를, 거리는 분리 정도를 보여 준다고 생각하면 편합니다.

## 핵심 용어

- 내적: `v . w = sum(v_i * w_i)` 형태의 스칼라입니다.
- 코사인 유사도: `(v . w) / (||v|| ||w||)`로 방향만 비교합니다.
- 직교: 내적이 0인 관계입니다.
- 유클리드 거리: `||v - w||`로 표현하는 직선 거리입니다.
- 맨해튼 거리: `sum(|v_i - w_i|)`로 계산하는 격자형 거리입니다.

## 읽기 전과 후

읽기 전에는 내적을 단순한 곱셈-덧셈 공식으로 보기 쉽습니다. 그러면 왜 코사인 유사도가 등장하는지, 왜 거리 함수에 따라 결과 해석이 달라지는지 잘 연결되지 않습니다.

읽은 후에는 내적이 방향 정렬을, 거리가 분리 정도를 보여 준다는 점이 분명해집니다. 같은 두 벡터를 놓고도 무엇을 묻느냐에 따라 다른 척도를 써야 한다는 감각이 생깁니다.

## 다섯 단계로 비교 기준 익히기

### 1단계 — 벡터 준비

```python
import numpy as np
v = np.array([1.0, 2.0, 3.0])
w = np.array([4.0, 5.0, 6.0])
```

먼저 비교할 두 벡터를 준비합니다. 예제는 단순하지만 내적과 거리의 차이를 한눈에 보기 좋습니다.

### 2단계 — 내적

```python
print("v . w:", np.dot(v, w))
print("v . w:", v @ w)
```

내적은 같은 위치의 원소를 곱해 모두 더한 값입니다. NumPy에서는 `np.dot`과 `@` 표기가 함께 쓰입니다.

### 3단계 — 코사인 유사도

```python
cos_sim = (v @ w) / (np.linalg.norm(v) * np.linalg.norm(w))
print("cosine similarity:", cos_sim)
```

여기서는 길이의 영향을 나눠 제거합니다. 그래서 코사인 유사도는 크기가 아니라 방향 유사성을 보여 줍니다.

### 4단계 — 유클리드 거리

```python
print("Euclidean:", np.linalg.norm(v - w))
```

유클리드 거리는 두 벡터 차이의 길이입니다. 두 점 사이를 직선으로 잰다고 생각하면 됩니다.

### 5단계 — 맨해튼 거리

```python
print("Manhattan:", np.sum(np.abs(v - w)))
```

맨해튼 거리는 좌표별 차이의 절댓값을 모두 더합니다. 어떤 문제에서는 직선 거리보다 이 방식이 더 자연스러울 수 있습니다.

## 작은 수치 예시로 다시 보기

- `v @ w`는 `32.0`입니다. 좌표별 곱을 더한 값 하나가 두 벡터의 정렬 정도를 압축합니다.
- 코사인 유사도는 약 `0.975`로 나옵니다. 방향이 꽤 비슷하다는 뜻입니다.
- 유클리드 거리는 약 `5.196`, 맨해튼 거리는 `9.0`입니다. 같은 두 벡터라도 질문이 달라지면 숫자도 달라집니다.

## 이 코드에서 먼저 볼 점

- 내적은 방향과 크기를 함께 반영합니다.
- 코사인 유사도는 방향만 비교합니다.
- 거리는 값이 작을수록 더 가깝게 읽습니다.
- 같은 데이터라도 척도 선택에 따라 해석이 달라집니다.

## 자주 하는 실수

1. 내적과 원소별 곱을 같은 것으로 다룹니다.
2. 코사인 유사도 계산에서 정규화를 빼먹습니다.
3. 영벡터에 코사인 유사도를 적용해 0으로 나눕니다.
4. 유클리드 거리와 맨해튼 거리를 같은 감각으로 읽습니다.
5. 고차원에서 거리 직관이 약해진다는 사실을 잊습니다.

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 메트릭을 먼저 고르고 나서 결과를 해석합니다. 문장 임베딩처럼 방향이 중요한 경우에는 정규화 후 코사인 유사도가 자연스럽고, 실제 양적 차이가 중요한 데이터에서는 거리 기반 접근이 더 맞을 수 있습니다.

또한 메트릭 선택이 모델 바깥의 전처리와 연결되어 있다는 점도 놓치지 않습니다. 정규화를 했는지, 스케일이 맞는지, 희소 벡터인지 밀집 벡터인지에 따라 비교 기준 자체가 달라져야 하기 때문입니다. 좋은 비교 기준은 좋은 검색 품질과 추천 품질의 출발점입니다.

## 사이파이 거리 함수 예제

SciPy는 다양한 거리 함수를 제공합니다. 실무에서는 직접 구현하는 대신 검증된 라이브러리를 사용하는 것이 안전합니다.

```python
import numpy as np
from scipy.spatial.distance import euclidean, cityblock, cosine, mahalanobis

# 샘플 벡터
v = np.array([1.0, 2.0, 3.0])
w = np.array([4.0, 5.0, 6.0])

# 1. 유클리드 거리 (L2)
dist_l2 = euclidean(v, w)
print('Euclidean distance:', dist_l2)
print('NumPy 동등:', np.linalg.norm(v - w))

# 2. 맨해튼 거리 (L1)
dist_l1 = cityblock(v, w)
print('Manhattan distance:', dist_l1)
print('NumPy 동등:', np.sum(np.abs(v - w)))

# 3. 코사인 거리 (1 - 코사인 유사도)
dist_cos = cosine(v, w)
print('Cosine distance:', dist_cos)
cos_sim = np.dot(v, w) / (np.linalg.norm(v) * np.linalg.norm(w))
print('Cosine similarity:', cos_sim)
print('1 - cos_sim:', 1 - cos_sim)

# 4. 마할라노비스 거리
# 공분산 행렬 필요
X = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9],
              [2, 3, 4],
              [5, 6, 7]])
cov = np.cov(X.T)
cov_inv = np.linalg.pinv(cov)  # pseudo-inverse for stability

dist_maha = mahalanobis(v, w, cov_inv)
print('Mahalanobis distance:', dist_maha)

# 5. 여러 쌍 간 거리 행렬 계산
from scipy.spatial.distance import pdist, squareform

points = np.array([[0, 0],
                   [1, 0],
                   [0, 1],
                   [1, 1]])

# 모든 쌍 간 유클리드 거리
distances = pdist(points, metric='euclidean')
dist_matrix = squareform(distances)
print('Distance matrix:\n', dist_matrix)
```

`scipy.spatial.distance`는 20가지 이상의 거리 함수를 지원하며, `pdist`와 `cdist`를 통해 배치 계산도 효율적으로 수행할 수 있습니다. 실무에서는 직접 구현보다 이런 라이브러리를 사용하는 것이 수치 안정성과 성능 면에서 유리합니다.
## 체크리스트

- [ ] 내적을 계산하고 의미를 설명할 수 있습니다.
- [ ] 코사인 유사도를 계산할 수 있습니다.
- [ ] 유클리드 거리와 맨해튼 거리의 차이를 설명할 수 있습니다.
- [ ] 비슷함과 가까움이 같은 말이 아니라는 점을 이해했습니다.

## 연습 문제

1. `v = [1, 0]`, `w = [0, 1]`의 내적을 계산하고 왜 직교인지 설명해 보세요.
2. 코사인 유사도가 `1`, `0`, `-1`이 되도록 벡터 쌍을 만들어 보세요.
3. 유클리드 거리와 맨해튼 거리가 다르게 나오는 예시를 구성해 보세요.

## 정리와 다음 글

내적은 벡터가 얼마나 같은 방향을 보는지 알려 주고, 코사인 유사도는 그중 방향만 떼어 내 비교합니다. 거리는 두 벡터가 공간에서 얼마나 떨어져 있는지를 보여 줍니다. 이 세 기준을 구분해서 읽을 수 있으면 벡터 검색, 추천, 군집화 같은 주제를 더 선명하게 볼 수 있습니다.

다음 글에서는 선형변환으로 넘어갑니다. 이제 벡터를 비교하는 기준을 익혔으니, 행렬이 벡터 공간 자체를 어떻게 바꾸는지도 같은 언어로 읽어 보겠습니다.

## 내적과 거리 선택을 데이터 성질과 연결하기

같은 데이터라도 비교 기준이 달라지면 결과가 바뀝니다. 아래 코드는 코사인 유사도와 두 가지 거리(L2, L1)를 한 번에 계산해 비교 기준 차이를 보여 줍니다.

```python
import numpy as np

q = np.array([0.2, 0.8, 0.0])
d1 = np.array([0.1, 0.9, 0.0])
d2 = np.array([0.9, 0.1, 0.0])

def cosine(a, b):
    return (a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))

for name, d in [('d1', d1), ('d2', d2)]:
    print(name)
    print('  cosine =', cosine(q, d))
    print('  L2     =', np.linalg.norm(q - d))
    print('  L1     =', np.abs(q - d).sum())
```

문서 검색에서는 대개 코사인이 더 자연스럽고, 물리 좌표 오차 분석에서는 L2가 더 자연스러운 경우가 많습니다. 무엇이 "비슷함"인지 먼저 정의하지 않으면 평가 지표 선택도 일관되기 어렵습니다.

## 기하학적으로 보는 내적

내적은 두 벡터의 길이와 각도 정보를 동시에 담습니다.
\[
a\cdot b = ||a||\,||b||\cos	heta
\]

- `> 0`: 같은 쪽 방향
- `= 0`: 직교
- `< 0`: 반대쪽 방향

이 해석은 임베딩 검색에서 단순 점수 비교를 넘어, 왜 특정 결과가 상위에 올라왔는지 설명할 근거를 제공합니다.

## 메트릭 선택 가이드

| 상황 | 우선 선택 | 이유 |
| --- | --- | --- |
| 임베딩 검색/추천 | 코사인 유사도 | 방향 유사성이 핵심 |
| 좌표 기반 오차 | 유클리드 거리 | 실제 거리 해석이 직접적 |
| 희소 벡터/강인성 필요 | 맨해튼 거리 | 축별 변화량 합이 해석적 |

추가로 고차원에서는 거리 집중 현상 때문에 L2 값 분별력이 떨어질 수 있습니다. 이 경우 정규화, 차원 축소(PCA), 또는 근사 최근접 탐색 전략을 함께 고려해야 합니다.

## 실전 확장 노트: NumPy 계산 루틴과 해석 체크포인트

아래 루틴은 장이 달라도 반복해서 사용할 수 있는 공통 점검 템플릿입니다. 벡터/행렬 연산을 수행할 때 형상 확인, 수치 안정성, 기하학 해석을 함께 기록하면 학습 속도가 크게 빨라집니다.

```python
import numpy as np

rng = np.random.default_rng(123)
X = rng.normal(size=(6, 4))
v = rng.normal(size=4)
A = rng.normal(size=(4, 4))

print('X shape:', X.shape)
print('v shape:', v.shape)
print('A shape:', A.shape)

# 기본 연산
xv = X @ v
Av = A @ v
print('Xv shape:', xv.shape)
print('Av shape:', Av.shape)

# 대칭 행렬 구성 후 고유값 확인
S = A.T @ A
eigvals = np.linalg.eigvalsh(S)
print('eigvals(S):', eigvals)

# SVD와 랭크 근사
U, s, Vt = np.linalg.svd(X, full_matrices=False)
rank = np.linalg.matrix_rank(X)
X2 = U[:, :2] @ np.diag(s[:2]) @ Vt[:2, :]
rel_err = np.linalg.norm(X - X2) / np.linalg.norm(X)

print('rank(X):', rank)
print('singular values:', s)
print('relative error(rank-2):', rel_err)
```

위 코드에서 반드시 확인할 항목은 네 가지입니다.

1. **형상 보존**: `X @ v`의 결과 차원이 `(6,)`인지 즉시 확인합니다. 계산이 맞아도 형상이 다르면 이후 파이프라인에서 오류가 누적됩니다.
2. **대칭 양의 준정부호 구조**: `A.T @ A`는 항상 대칭이며 고유값이 음수가 나오지 않아야 합니다. 음수가 크게 나오면 수치 오차나 구현 실수를 의심해야 합니다.
3. **특이값 분포**: 특이값이 급격히 감소하면 저랭크 근사로도 구조를 상당 부분 유지할 가능성이 큽니다.
4. **상대 재구성 오차**: 압축 품질을 주관이 아닌 숫자로 판단합니다.

## 계산 결과를 문장으로 번역하는 연습

선형대수 실력이 빠르게 늘지 않는 가장 흔한 이유는 계산은 했지만 해석을 남기지 않기 때문입니다. 아래 질문을 매번 적어 두면 해석력이 올라갑니다.

- 이 연산은 공간에서 무엇을 보존하고 무엇을 바꾸는가?
- 결과 크기가 커진 이유는 변환 자체 때문인가, 입력 스케일 때문인가?
- 순서를 바꿨을 때 결과가 달라진다면 어떤 변환이 먼저 적용되었는가?
- 같은 결과를 분해 방식(LU/QR/SVD)으로 다시 계산하면 안정성이 좋아지는가?

## 작은 응용 시나리오

| 시나리오 | 선형대수 동작 | 점검 지표 |
| --- | --- | --- |
| 피처 압축 | SVD/PCA로 저차원 투영 | 누적 분산, 재구성 오차 |
| 유사도 검색 | 정규화 후 내적/코사인 | top-k 정확도, 스케일 민감도 |
| 회귀 학습 | `lstsq` 또는 경사하강 | 잔차 노름, 조건수 |
| 변환 파이프라인 | 행렬 합성 `A @ B @ x` | 중간 형상, 순서 민감성 |

이 표를 기준으로 실험 노트를 남기면, 한 번의 계산이 다음 장의 개념으로 자연스럽게 연결됩니다. 선형대수는 공식을 더 외울수록 좋아지는 과목이 아니라, 같은 계산을 더 정확히 해석할수록 깊어지는 과목입니다.

## 추가 연습: 단계별 검증 습관 만들기

아래 절차는 어떤 장의 코드에도 공통으로 적용할 수 있는 검증 루프입니다.

```python
# 1) shape 점검
# 2) 기준값(allclose) 점검
# 3) 수치 안정성(조건수/오차) 점검
# 4) 해석 메모(무엇이 커지고 줄었는지) 기록
```

짧아 보이지만 이 네 단계를 지키면 계산 실수 대부분을 초기에 막을 수 있습니다. 특히 교육용 예제에서는 결과 숫자만 맞추기보다, 왜 그 숫자가 나왔는지 한 줄 해석을 남기는 습관이 중요합니다. 예를 들어 노름이 커졌다면 입력 방향 때문인지 변환 스케일 때문인지 분리해서 적어야 합니다.

또한 동일한 문제를 두 방식으로 풀어 비교하는 연습이 좋습니다. 예를 들어 선형시스템은 `inv` 경로와 `solve` 경로를 비교하고, 차원 축소는 공분산 고유분해와 SVD 경로를 비교하면 계산 안정성과 해석력을 동시에 키울 수 있습니다. 이런 비교 루틴이 쌓이면 새로운 라이브러리를 만나도 핵심 검증 기준은 흔들리지 않습니다.

## 고차원에서 거리의 함정

고차원 공간에서는 모든 점이 비슷하게 먀 것처럼 보이는 현상이 있습니다. 이를 '차원의 저주(curse of dimensionality)'라고 하며, 거리 기반 비교의 분별력이 떨어지는 주요 원인입니다.

### 문제: 거리 집중 현상

고차원에서는 가장 가까운 점과 가장 먼 점의 거리 차이가 상대적으로 줘갑니다. 즉, 모든 점이 비슷하게 멀리 떨어져 보입니다.

```python
import numpy as np

def measure_distance_concentration(dim, n_samples=100):
    """
    차원별로 거리 분포를 측정합니다.
    """
    samples = np.random.randn(n_samples, dim)
    
    # 첨 번째 점에서 나머지 모든 점까지의 거리
    distances = []
    for i in range(1, n_samples):
        dist = np.linalg.norm(samples[0] - samples[i])
        distances.append(dist)
    
    distances = np.array(distances)
    mean_dist = np.mean(distances)
    std_dist = np.std(distances)
    min_dist = np.min(distances)
    max_dist = np.max(distances)
    
    # 분별력 지표: (max - min) / mean
    discriminability = (max_dist - min_dist) / mean_dist
    
    return {
        'dim': dim,
        'mean': mean_dist,
        'std': std_dist,
        'min': min_dist,
        'max': max_dist,
        'discriminability': discriminability
    }

# 차원별 비교
for d in [2, 10, 50, 100, 500]:
    result = measure_distance_concentration(d)
    print(f"Dim {result['dim']:3d}: mean={result['mean']:6.2f}, ", 
          f"std={result['std']:5.2f}, disc={result['discriminability']:.3f}")
```

### 해결 전략

1. **정규화 + 코사인 유사도**: 크기 대신 방향만 비교하면 고차원 문제가 완화됩니다.
2. **차원 축소 (PCA, t-SNE, UMAP)**: 의미 있는 차원만 남겸니다.
3. **근사 최근접 탐색 (ANN)**: FAISS, Annoy 같은 라이브러리로 효율적인 검색을 수행합니다.
4. **맨해튼 거리 또는 프랙셔널 노름**: 크기보다 구조를 강조합니다.

```python
# 예시: 정규화 효과
high_dim = 100
v = np.random.randn(high_dim)
w = np.random.randn(high_dim)

# 원본 범위가 넓음
print('Before normalization:')
print('  L2 distance:', np.linalg.norm(v - w))
print('  ||v||:', np.linalg.norm(v))
print('  ||w||:', np.linalg.norm(w))

# 정규화 후
v_n = v / np.linalg.norm(v)
w_n = w / np.linalg.norm(w)
print('\nAfter normalization:')
print('  L2 distance:', np.linalg.norm(v_n - w_n))
print('  cosine similarity:', np.dot(v_n, w_n))
```

정규화는 벡터를 단위 구 표면에 투영하므로, 방향 비교가 더 안정적으로 작동합니다. 이것이 고차원 임베딩 검색에서 코사인 유사도가 표준이 되는 주요 이유입니다.
## 마무리 계산 메모

마지막으로, 각 장의 예제를 실행할 때는 입력 형상, 출력 형상, 오차 지표를 함께 기록해 두는 편이 좋습니다. 같은 수식이라도 데이터 스케일과 기저 선택에 따라 해석이 크게 달라질 수 있기 때문입니다. 실무에서는 이 메모가 재현성과 디버깅 속도를 결정합니다.


추가로, 수치 실험 결과를 남길 때는 난수 시드와 라이브러리 버전도 함께 기록하면 재현성이 크게 좋아집니다.

검증 로그를 남기면 다음 실험에서 비교 기준을 일관되게 유지할 수 있습니다.

실험 조건과 해석 기준을 글과 함께 남기면 팀 협업 시 의사결정 근거를 재사용하기 쉽습니다.

메트릭 선택 이유를 명시하면 결과 해석의 일관성이 높아집니다.

### 메트릭 선택 한 줄 원칙

실무에서는 먼저 문제의 의미를 정의하고 메트릭을 고릅니다. 방향이 핵심이면 코사인, 절대 차이가 핵심이면 거리 함수를 우선합니다.

## 실전 연결: 거리 척도 선택 기준 세우기

벡터 비교에서 가장 흔한 실패는 척도를 목적과 분리해서 고르는 것입니다. 추천이나 검색처럼 의미 방향이 중요한 문제에서는 코사인 유사도가 자연스럽고, 실제 좌표 차이 자체가 비용을 의미하는 문제에서는 유클리드 거리나 맨해튼 거리가 더 적합합니다.

```python
import numpy as np

q = np.array([0.4, 0.2, 0.9])
docs = np.array([
    [0.3, 0.2, 0.8],
    [0.8, 0.1, 0.2],
    [0.1, 0.0, 1.1],
], dtype=float)

docs_n = docs / np.linalg.norm(docs, axis=1, keepdims=True)
q_n = q / np.linalg.norm(q)
cos_score = docs_n @ q_n
l2_dist = np.linalg.norm(docs - q, axis=1)
print('cos:', cos_score)
print('l2 :', l2_dist)
```

위 결과에서 코사인 기준 상위 문서와 L2 기준 상위 문서가 달라질 수 있습니다. 이것이 이상한 것이 아니라, 서로 다른 질문에 답하고 있기 때문입니다. 따라서 모델 평가 전에 먼저 “우리가 정의한 유사성”이 제품 요구와 일치하는지 확인해야 합니다.

고차원 임베딩에서는 특히 정규화 여부가 중요합니다. 정규화를 생략하면 길이 큰 벡터가 과도하게 유리해져 검색 결과가 왜곡될 수 있습니다. 내적과 거리의 차이를 설계 레벨에서 합의해 두면 이후 실험의 재현성과 해석력이 크게 올라갑니다.

## 처음 질문으로 돌아가기

- **내적은 왜 숫자 하나로 나올까요?**
  - 본문의 기준은 내적과 거리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **코사인 유사도는 내적과 어떻게 연결될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **유클리드 거리와 맨해튼 거리는 무엇이 다를까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linear Algebra 101 (1/10): 선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): 벡터](./02-vectors.md)
- [Linear Algebra 101 (3/10): 행렬](./03-matrices.md)
- **내적과 거리 (현재 글)**
- 선형변환 (예정)
- 기저와 차원 (예정)
- 고유값과 고유벡터 (예정)
- 행렬 분해 (예정)
- PCA (예정)
- 머신러닝에서의 선형대수 (예정)

<!-- toc:end -->

## 참고 자료

- 시리즈 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/linear-algebra-101/ko
- [Wikipedia — Dot product](https://en.wikipedia.org/wiki/Dot_product)
- [Wikipedia — Cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
- [3Blue1Brown — Dot products](https://www.3blue1brown.com/lessons/dot-products)
- [scikit-learn — Pairwise metrics](https://scikit-learn.org/stable/modules/metrics.html)

Tags: LinearAlgebra, InnerProduct, Distance, DataScience, Beginner
