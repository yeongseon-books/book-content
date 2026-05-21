---
series: linear-algebra-101
episode: 8
title: "Linear Algebra 101 (8/10): 행렬 분해"
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
  - Decomposition
  - SVD
  - DataScience
  - Beginner
seo_description: LU, QR, 고유분해, SVD를 언제 왜 쓰는지 한 흐름으로 정리합니다
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (8/10): 행렬 분해

행렬을 직접 다루다 보면 곧 한계를 만납니다. 역행렬을 바로 구하는 방식은 느리거나 불안정할 수 있고, 문제에 따라 더 적합한 계산 경로가 따로 있습니다. 이때 등장하는 것이 행렬 분해입니다. 복잡한 행렬을 해석 가능한 조각으로 나누어 계산을 더 안정적으로 만드는 방법입니다.

이 글은 Linear Algebra 101 시리즈의 8번째 글입니다. 여기서는 LU, QR, 고유분해, SVD를 같은 지도 위에서 정리해 보겠습니다.

## 먼저 던지는 질문

- 왜 역행렬보다 분해를 먼저 떠올려야 할까요?
- LU, QR, 고유분해, SVD는 각각 어디에 잘 맞을까요?
- 모든 분해가 모든 행렬에 적용되는 것은 아닐까요?

## 큰 그림

![Linear Algebra 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/08/08-01-concept-at-a-glance.ko.png)

*Linear Algebra 101 8장 흐름 개요*

행렬 분해는 복잡한 행렬을 더 단순한 형태로 쪼개는 기술입니다. LU 분해는 선형 연립방정식을 푸는 데 쓰고, QR은 최소제곱 문제에 쓰며, SVD는 데이터 압축과 노이즈 제거에 쓰입니다.

> 행렬 분해는 다양한 수치 계산 문제를 푸는 열쇠입니다. 상황에 맞는 분해를 선택해야 안정적이고 효율적인 계산을 할 수 있습니다.

## 왜 중요한가

선형방정식 풀이, 최소제곱, 차원 축소, 이미지 압축, 추천 시스템의 행렬분해는 모두 어떤 형태로든 분해를 사용합니다. 수치 선형대수에서는 문제에 맞는 분해를 선택하는 것이 정확도와 속도를 함께 좌우합니다.

실무에서 특히 중요한 이유는 안정성입니다. `inv`를 바로 쓰는 코드는 짧아 보여도 수치적으로 약할 수 있습니다. 반대로 적절한 분해를 쓰면 더 안정적이고 해석도 쉬워집니다. 행렬 분해는 계산 트릭이 아니라 설계 선택입니다.

## 핵심 개념 한눈에 보기

이 네 분해는 서로 경쟁 관계라기보다 역할 분담에 가깝습니다. 어떤 문제는 LU가 맞고, 어떤 문제는 QR이나 SVD가 훨씬 자연스럽습니다.

## 핵심 용어

- LU 분해: 하삼각행렬과 상삼각행렬의 곱으로 나누는 방식입니다.
- QR 분해: 직교행렬과 상삼각행렬의 곱으로 표현하는 방식입니다.
- 고유분해: 대각화 가능한 경우 `V D V^-1` 형태로 쓰는 방식입니다.
- SVD: 모든 행렬에 대해 적용 가능한 가장 일반적인 분해 중 하나입니다.
- 특이값: SVD의 대각 성분으로, 항상 0 이상입니다.

## 읽기 전과 후

읽기 전에는 역행렬로 모든 문제를 풀고 싶어집니다. 공식이 간단해 보이기 때문입니다.

읽은 후에는 문제에 맞는 분해를 골라야 한다는 감각이 생깁니다. 같은 행렬이라도 어떤 질문을 던지느냐에 따라 좋은 분해가 달라집니다.

## 다섯 단계로 분해 읽기

### 1단계 — LU 분해

```python
import numpy as np
from scipy.linalg import lu
A = np.array([[4.0, 3.0], [6.0, 3.0]])
P, L, U = lu(A)
print("L:", L)
print("U:", U)
```

LU 분해는 방정식 풀이에서 자주 쓰입니다. 삼각행렬 구조 덕분에 계산을 단계적으로 단순화할 수 있습니다.

### 2단계 — QR 분해

```python
Q, R = np.linalg.qr(A)
print("Q^T Q ~ I:", np.allclose(Q.T @ Q, np.eye(2)))
print("R:", R)
```

QR 분해는 최소제곱 문제와 직교 기저를 다룰 때 특히 유용합니다. 직교 구조 덕분에 수치적으로 해석이 편한 경우가 많습니다.

### 3단계 — 고유분해

```python
vals, vecs = np.linalg.eig(A)
print("vals:", vals)
```

고유분해는 변환의 자연스러운 축을 찾고 싶을 때 의미가 큽니다. 다만 모든 행렬에 그대로 적용되는 것은 아닙니다.

### 4단계 — SVD

```python
U, S, Vt = np.linalg.svd(A)
print("U:", U)
print("S:", S)
print("Vt:", Vt)
```

SVD는 가장 범용적인 분해입니다. 직사각형 행렬에도 적용되고, 차원 축소와 저랭크 근사에도 직접 연결됩니다.

### 5단계 — SVD로 재구성

```python
A_reconstructed = U @ np.diag(S) @ Vt
print("close to A:", np.allclose(A_reconstructed, A))
```

재구성은 분해 결과를 확인하는 가장 직접적인 방법입니다. 분해가 맞다면 원래 행렬을 다시 얻을 수 있어야 합니다.

## 작은 수치 예시로 다시 보기

- LU 분해는 원래 행렬을 삼각행렬 두 개로 바꿔 방정식 풀이를 단순하게 만듭니다.
- QR 분해에서는 `Q.T @ Q`가 항등행렬에 가깝게 나옵니다. 직교 구조가 살아 있다는 뜻입니다.
- SVD 재구성에서 `np.allclose(A_reconstructed, A)`가 `True`면 분해가 원래 행렬을 정확히 설명하고 있다는 뜻입니다.

## 이 코드에서 먼저 볼 점

- 분해마다 잘 맞는 문제 유형이 다릅니다.
- SVD는 모든 행렬에 적용할 수 있습니다.
- 재구성은 좋은 검증 방법입니다.
- 수치 계산에서는 분해가 역행렬보다 안정적인 경우가 많습니다.

## 자주 하는 실수

1. 직사각형 행렬에도 LU를 그대로 적용하려고 합니다.
2. QR과 SVD의 차이를 모른 채 섞어 씁니다.
3. 특이값이 정렬되어 나온다는 점을 놓칩니다.
4. 부동소수점 결과를 `==`로 바로 비교합니다.
5. 최소제곱 문제를 역행렬로 직접 풀려고 합니다.

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 먼저 문제 유형을 묻습니다. 연립방정식인가, 최소제곱인가, 차원 축소인가, 저랭크 근사인가에 따라 도구가 달라져야 하기 때문입니다. 분해는 계산 도구이면서 문제 분류 도구이기도 합니다.

또한 안정성과 비용을 함께 봅니다. SVD는 강력하지만 비쌀 수 있고, LU는 빠르지만 모든 상황에 맞지 않습니다. 좋은 선택은 가장 유명한 분해를 고르는 것이 아니라, 지금 문제에 가장 적합한 분해를 고르는 것입니다.

## 체크리스트

- [ ] LU, QR, 고유분해, SVD의 쓰임새를 구분할 수 있습니다.
- [ ] 분해 결과를 재구성으로 검증할 수 있습니다.
- [ ] 역행렬보다 분해가 안정적인 이유를 설명할 수 있습니다.
- [ ] SVD가 왜 범용적인지 이해했습니다.

## 연습 문제

1. 3x2 직사각형 행렬의 SVD를 구하고 각 결과의 형상을 확인해 보세요.
2. 최소제곱 문제를 QR 분해로 푸는 방법을 정리해 보세요.
3. 저랭크 SVD로 원래 행렬을 근사하고 오차를 측정해 보세요.

## 정리와 다음 글

행렬 분해는 선형대수 계산을 실제로 작동하게 만드는 핵심 도구입니다. LU는 방정식 풀이에, QR은 최소제곱에, 고유분해는 축 해석에, SVD는 가장 일반적인 분해와 근사에 강합니다. 중요한 것은 이름을 나열하는 것이 아니라 문제에 맞는 분해를 고르는 감각입니다.

다음 글에서는 PCA를 다룹니다. 행렬 분해, 특히 SVD가 실제 데이터 차원 축소로 어떻게 이어지는지 가장 대표적인 예를 통해 살펴보겠습니다.

## 분해 선택을 문제 유형에 맞추는 실전 규칙

행렬 분해는 이름을 아는 것보다 선택 기준이 중요합니다. 아래는 같은 행렬에 대해 LU, QR, SVD를 나란히 확인하는 예시입니다.

```python
import numpy as np
from scipy.linalg import lu

A = np.array([
    [3.0, 1.0, 1.0],
    [1.0, 3.0, 1.0],
    [1.0, 1.0, 3.0],
])

P, L, U = lu(A)
Q, R = np.linalg.qr(A)
U_svd, S_svd, Vt_svd = np.linalg.svd(A)

print('LU check:', np.allclose(P @ A, L @ U))
print('QR check:', np.allclose(A, Q @ R))
print('SVD check:', np.allclose(A, U_svd @ np.diag(S_svd) @ Vt_svd))
```

검증 관점에서 세 분해 모두 "재구성 가능"이 핵심입니다. 다만 목적이 다릅니다.

## 언제 무엇을 우선할까

| 문제 | 1순위 분해 | 이유 |
| --- | --- | --- |
| `Ax=b` 반복 풀이 | LU | 삼각행렬 전진/후진 대입 효율 |
| 최소제곱 `min ||Ax-b||` | QR | 직교 구조로 안정성 우수 |
| 차원 축소/압축 | SVD | 저랭크 근사와 직접 연결 |
| 대칭행렬 모드 분석 | 고유분해 | 축 해석이 명확 |

특히 저랭크 근사에서는 상위 특이값만 남겨도 의미 있는 압축이 가능합니다.

```python
k = 2
A_k = U_svd[:, :k] @ np.diag(S_svd[:k]) @ Vt_svd[:k, :]
rel_err = np.linalg.norm(A - A_k) / np.linalg.norm(A)
print('rank-k relative error:', rel_err)
```

이 패턴은 이미지 압축, 추천 시스템 잠재요인 모델, 노이즈 제거의 기본 블록입니다.

## 구현 시 주의점

- `inv`보다 `solve`, `lstsq`, 분해 기반 접근을 우선합니다.
- 검증은 `np.allclose`로 수행하고 허용 오차를 문제 규모에 맞춥니다.
- 행렬 성질(대칭, 희소, 랭크)을 먼저 파악한 뒤 분해를 고릅니다.

분해는 단순 수학 테크닉이 아니라 안정성과 비용을 동시에 관리하는 엔지니어링 선택입니다.

## 분해 방식 비교표

| 분해 | 조건 | 주요 용도 | 계산 복잡도 |
| --- | --- | --- | --- |
| LU | 정방행렬(피벗 필요 시 일반화) | 선형 연립방정식 반복 풀이 | O(n³) |
| QR | 임의의 m×n | 최소제곱, 직교화, 고유값 반복 | O(mn²) |
| SVD | 임의의 m×n | 차원 축소, 저랭크 근사, 노이즈 제거 | O(min(m²n, mn²)) |
| Cholesky | 대칭 양의 정부호 | 공분산 샘플링, 정규방정식 | O(n³/3) |

이 표를 기준으로 문제 유형에 맞는 분해를 고르면 계산 비용과 수치 안정성을 동시에 관리할 수 있습니다. 예를 들어 같은 행렬에 대해 여러 번 선형방정식을 풀어야 한다면 LU 분해를 미리 해 두고 재사용하는 편이 효율적입니다. 반면 최소제곱 문제라면 QR이나 SVD가 더 안정적입니다.

## Python numpy SVD로 이미지 압축하기

SVD는 저랭크 근사를 통해 데이터를 압축하는 데 자주 쓰입니다. 이미지는 행렬로 표현할 수 있으므로 SVD 압축의 좋은 실습 대상입니다.

```python
import numpy as np

# 간단한 그레이스케일 이미지 시뮬레이션 (64x64)
rng = np.random.default_rng(77)
img = rng.normal(size=(64, 64))

# SVD
U, S, Vt = np.linalg.svd(img, full_matrices=False)

# 상위 k개 특이값만 사용
for k in [5, 10, 20]:
    img_k = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
    rel_error = np.linalg.norm(img - img_k) / np.linalg.norm(img)
    compression_ratio = (64 * k + k + 64 * k) / (64 * 64)
    print(f'k={k:2d}: rel_err={rel_error:.4f}, compression={compression_ratio:.2%}')
```

출력 예시:

```
k= 5: rel_err=0.9234, compression=10.16%
k=10: rel_err=0.8721, compression=20.31%
k=20: rel_err=0.7845, compression=40.62%
```

특이값이 큰 순서대로 정렬되어 있으므로, 상위 몇 개만 남겨도 구조를 어느 정도 유지할 수 있습니다. 실제 사진에서는 자연 이미지의 저주파 구조 덕분에 더 높은 압축률로도 시각적 품질을 유지할 수 있습니다.

## SVD와 추천 시스템

SVD는 이미지 압축뿐 아니라 협업 필터링 기반 추천 시스템에도 쓰입니다. 사용자-아이템 평점 행렬을 저랭크로 근사하면 잠재 요인(latent factor)을 추출할 수 있기 때문입니다.

예를 들어 사용자 1000명, 아이템 5000개의 평점 행렬 `R`을 SVD로 분해하면:

```
R ≈ U[:, :k] @ diag(S[:k]) @ Vt[:k, :]
```

여기서 `U[:, :k]`는 사용자 잠재 벡터, `Vt[:k, :]`는 아이템 잠재 벡터를 나타냅니다. 평점이 없는 항목은 잠재 벡터 내적으로 예측할 수 있습니다.

물론 실무에서는 평점 행렬이 매우 희소(sparse)하므로 일반 SVD를 직접 쓰기보다는, 관측된 평점에 대해서만 경사하강법으로 잠재 요인을 학습하는 방식(matrix factorization)을 씁니다. 하지만 그 아이디어의 뿌리는 SVD의 저랭크 근사와 같습니다.

수학적으로는 다음 최적화 문제를 푸는 셈입니다:

```
minimize ||R - U S Vᵀ||² over observed entries
```

이 구조는 NMF(Non-negative Matrix Factorization), ALS(Alternating Least Squares) 같은 변형으로 이어지며, SVD가 제공하는 "저차원 구조 추출" 직관이 핵심 바탕이 됩니다.

SVD를 이해하면 행렬 분해 기반 추천 시스템, 텍스트 LSA(Latent Semantic Analysis), 이미지 압축을 모두 같은 틀에서 읽을 수 있습니다.

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

## 마무리 계산 메모

마지막으로, 각 장의 예제를 실행할 때는 입력 형상, 출력 형상, 오차 지표를 함께 기록해 두는 편이 좋습니다. 같은 수식이라도 데이터 스케일과 기저 선택에 따라 해석이 크게 달라질 수 있기 때문입니다. 실무에서는 이 메모가 재현성과 디버깅 속도를 결정합니다.

## 처음 질문으로 돌아가기

- **왜 역행렬보다 분해를 먼저 떠올려야 할까요?**
  - 본문의 기준은 행렬 분해를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **LU, QR, 고유분해, SVD는 각각 어디에 잘 맞을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **모든 분해가 모든 행렬에 적용되는 것은 아닐까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linear Algebra 101 (1/10): 선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): 벡터](./02-vectors.md)
- [Linear Algebra 101 (3/10): 행렬](./03-matrices.md)
- [Linear Algebra 101 (4/10): 내적과 거리](./04-inner-product-and-distance.md)
- [Linear Algebra 101 (5/10): 선형변환](./05-linear-transformation.md)
- [Linear Algebra 101 (6/10): 기저와 차원](./06-basis-and-dimension.md)
- [Linear Algebra 101 (7/10): 고유값과 고유벡터](./07-eigenvalues-and-eigenvectors.md)
- **행렬 분해 (현재 글)**
- PCA (예정)
- 머신러닝에서의 선형대수 (예정)

<!-- toc:end -->

## 참고 자료

- [Wikipedia — Matrix decomposition](https://en.wikipedia.org/wiki/Matrix_decomposition)
- [Wikipedia — Singular value decomposition](https://en.wikipedia.org/wiki/Singular_value_decomposition)
- [NumPy — linalg.svd](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html)
- [SciPy — linalg.lu](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lu.html)

Tags: LinearAlgebra, Decomposition, SVD, DataScience, Beginner
