---
series: linear-algebra-101
episode: 5
title: "Linear Algebra 101 (5/10): 선형변환"
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
  - LinearTransformation
  - Geometry
  - DataScience
  - Beginner
seo_description: 회전, 확대, 반사, 전단 변환을 예로 들어 행렬이 공간을 어떻게 바꾸는지 그 기하학적 의미를 명확하게 설명합니다.
last_reviewed: '2026-05-15'
---

# Linear Algebra 101 (5/10): 선형변환

행렬을 배우고 나면 다음 질문이 남습니다. 그래서 행렬이 실제로 공간에 무엇을 하는가 하는 질문입니다. 이 질문에 답하는 개념이 선형변환입니다. 행렬은 결국 선형변환을 좌표계 안에서 적어 놓은 표현이기 때문입니다.

이 글은 Linear Algebra 101 시리즈의 5번째 글입니다.

여기서는 회전, 확대, 반사, 전단을 예로 들어 선형변환을 기하학적으로 읽어 보겠습니다.


![Linear Algebra 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linear-algebra-101/05/05-01-concept-at-a-glance.ko.png)
*Linear Algebra 101 5장 흐름 개요*
> 선형변환은 벡터를 다른 벡터로 보내되 덧셈과 스칼라곱 구조를 지키는 규칙입니다. 행렬 곱을 변환의 합성으로 읽으면 왜 순서가 중요한지가 자동으로 의미를 얻습니다.

## 먼저 던지는 질문

- 행렬을 곱한다는 말은 공간에 어떤 변화를 주는 걸까요?
- 회전, 확대, 반사, 전단은 행렬 모양으로 어떻게 드러날까요?
- 변환의 합성은 왜 행렬 곱으로 표현될까요?

## 왜 중요한가

신경망의 각 레이어는 선형변환과 비선형 활성화의 조합입니다. 컴퓨터 그래픽스의 모델 행렬, 컴퓨터 비전의 좌표 변환, 데이터 증강의 회전과 확대도 모두 같은 틀로 설명할 수 있습니다.

선형변환 감각이 생기면 행렬이 더 이상 숫자판이 아닙니다. 어떤 행렬은 축을 늘리고, 어떤 행렬은 공간을 돌리고, 어떤 행렬은 방향을 뒤집습니다. 그 순간부터 선형대수 계산은 움직임과 구조를 설명하는 언어가 됩니다.

## 대표 선형변환

선형변환은 벡터 공간을 바꾸는 규칙입니다. 각 변환은 특징적인 행렬 형태와 기하학적 효과를 가집니다. 아래 표는 실무에서 자주 만나는 변환을 정리한 것입니다.

| 변환 | 행렬 | 기하 효과 |
| --- | --- | --- |
| 회전 (`θ` 라디안) | `[[cosθ, -sinθ], [sinθ, cosθ]]` | 각도 보존, 길이 보존, 방향만 변경 |
| 반사 (x축) | `[[1, 0], [0, -1]]` | y좌표 부호 반전, 좌우 반전 |
| 축소/확대 | `[[s_x, 0], [0, s_y]]` | 축별 독립 스케일링 |
| 사영 (x축으로) | `[[1, 0], [0, 0]]` | y성분 제거, 차원 감소 |
| 전단 (x 방향) | `[[1, k], [0, 1]]` | 평행사변형, 면적 보존 |

회전과 반사는 길이를 보존하고, 전단은 평행성을 보존합니다. 사영은 차원을 줄이므로 역행렬이 없습니다. 실무에서는 이런 변환을 여러 개 합성해 복잡한 공간 조작을 수행합니다.
## 핵심 개념 한눈에 보기

선형변환의 핵심은 입력 벡터 하나가 아니라 공간 전체가 함께 바뀐다는 점입니다. 격자는 평행성과 비율을 유지한 채 회전하거나 늘어나거나 기울어집니다.

## 핵심 용어

- 선형변환: `T(av + bw) = a T(v) + b T(w)`를 만족하는 규칙입니다.
- 회전: 각도를 유지한 채 방향만 돌리는 변환입니다.
- 확대와 축소: 대각 성분으로 길이를 조절하는 변환입니다.
- 반사: 축이나 직선을 기준으로 방향을 뒤집는 변환입니다.
- 전단: 한 축 방향으로 공간을 기울이는 변환입니다.

## 읽기 전과 후

읽기 전에는 행렬이 그냥 변환이라고만 들립니다. 하지만 무엇을 얼마나 어떻게 바꾸는지는 흐릿합니다.

읽은 후에는 회전은 각도로, 확대는 대각 성분으로, 반사는 부호 반전으로, 전단은 비대각 성분으로 읽히기 시작합니다. 행렬의 모양과 기하학적 효과가 연결됩니다.

## 다섯 단계로 변환 읽기

### 1단계 — 회전

```python
import numpy as np
theta = np.pi / 4
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
v = np.array([1.0, 0.0])
print("rotated:", R @ v)
```

회전 행렬은 방향을 바꾸되 구조를 보존하는 대표적인 선형변환입니다. 좌표가 바뀌어도 공간의 기본 질서는 유지됩니다.

### 2단계 — 확대와 축소

```python
S = np.diag([2.0, 0.5])
print("scaled:", S @ np.array([1.0, 1.0]))
```

대각행렬은 각 축을 독립적으로 늘리거나 줄입니다. 축별 스케일이 어떻게 달라지는지 바로 읽기 좋습니다.

### 3단계 — 반사

```python
F = np.array([[1.0, 0.0], [0.0, -1.0]])
print("reflected:", F @ np.array([1.0, 1.0]))
```

반사는 한 축에 대해 부호를 뒤집습니다. 공간의 방향성이 바뀌는 좋은 예입니다.

### 4단계 — 전단

```python
Sh = np.array([[1.0, 1.0], [0.0, 1.0]])
print("sheared:", Sh @ np.array([1.0, 1.0]))
```

전단은 격자를 기울입니다. 직사각형이 평행사변형으로 바뀌는 식의 변화를 떠올리면 감이 잘 옵니다.

### 5단계 — 변환 합성

```python
M = R @ S
print("compose RS:", M @ np.array([1.0, 0.0]))
```

합성은 선형변환의 진짜 핵심입니다. 먼저 확대하고 회전한 결과를 하나의 행렬로 묶어 표현할 수 있습니다.

## 작은 수치 예시로 다시 보기

- 45도 회전 행렬을 `[1, 0]`에 적용하면 결과는 대략 `[0.707, 0.707]`입니다. 방향만 바뀌고 길이는 유지됩니다.
- 대각행렬 `diag(2, 0.5)`를 `[1, 1]`에 적용하면 `[2., 0.5]`가 됩니다. 축마다 다른 비율로 늘고 줄어듭니다.
- `R @ S`를 먼저 만들어 두면 여러 변환을 하나의 행렬로 묶어 다룰 수 있습니다.

## 이 코드에서 먼저 볼 점

- 행렬 곱은 변환의 합성입니다.
- 각 변환은 특징적인 행렬 모양을 가집니다.
- 순서가 바뀌면 결과도 바뀝니다.
- 선형변환은 공간의 구조를 보존하는 변환입니다.

## 자주 하는 실수

1. 회전 방향의 부호를 뒤집습니다.
2. 음수 스케일이 반사 효과를 포함한다는 점을 놓칩니다.
3. 전단이 어느 축을 기준으로 기울어지는지 헷갈립니다.
4. 합성 순서를 거꾸로 적용합니다.
5. 비선형변환을 선형변환처럼 다룹니다.

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 행렬을 볼 때 그 행렬이 공간을 어떻게 바꾸는지 떠올립니다. 좌표계가 회전하는지, 축별 스케일이 달라지는지, 방향성이 뒤집히는지를 읽을 수 있어야 모델 내부의 계산도 감이 잡힙니다.

또한 합성 순서를 매우 조심합니다. 그래픽스 파이프라인이든 신경망 레이어든 계산 순서가 바뀌면 완전히 다른 변환이 되기 때문입니다. 선형변환 감각은 계산을 그림으로 번역하는 능력과 거의 같습니다.

## 맷플롯립으로 변환 시각화하기

선형변환의 효과를 시각화하면 기하학적 직관이 훨씬 강해집니다. 아래는 단위 정사각형에 여러 변환을 적용하고 결과를 비교하는 예제입니다.

```python
import numpy as np
import matplotlib.pyplot as plt

def plot_transformation(T, title):
    """
    행렬 T를 단위 정사각형에 적용하고 결과를 그립니다.
    """
    # 단위 정사각형 꼭짓점
    square = np.array([[0, 1, 1, 0, 0],
                       [0, 0, 1, 1, 0]])
    
    # 변환 적용
    transformed = T @ square
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    # 원본
    ax1.plot(square[0], square[1], 'b-o', linewidth=2, markersize=8)
    ax1.set_xlim(-2, 2)
    ax1.set_ylim(-2, 2)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(0, color='k', linewidth=0.5)
    ax1.axvline(0, color='k', linewidth=0.5)
    ax1.set_title('Original')
    
    # 변환 후
    ax2.plot(transformed[0], transformed[1], 'r-o', linewidth=2, markersize=8)
    ax2.plot(square[0], square[1], 'b--', alpha=0.3, linewidth=1)
    ax2.set_xlim(-2, 2)
    ax2.set_ylim(-2, 2)
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(0, color='k', linewidth=0.5)
    ax2.axvline(0, color='k', linewidth=0.5)
    ax2.set_title(title)
    
    plt.tight_layout()
    return fig

# 1. 회전 (45도)
theta = np.pi / 4
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
fig1 = plot_transformation(R, 'Rotation 45°')
plt.savefig('rotation.png', dpi=100, bbox_inches='tight')
plt.close()

# 2. 축소/확대
S = np.array([[2.0, 0.0],
              [0.0, 0.5]])
fig2 = plot_transformation(S, 'Scaling (2x, 0.5y)')
plt.savefig('scaling.png', dpi=100, bbox_inches='tight')
plt.close()

# 3. 반사 (x축)
F = np.array([[1.0, 0.0],
              [0.0, -1.0]])
fig3 = plot_transformation(F, 'Reflection (x-axis)')
plt.savefig('reflection.png', dpi=100, bbox_inches='tight')
plt.close()

# 4. 전단
Sh = np.array([[1.0, 0.5],
               [0.0, 1.0]])
fig4 = plot_transformation(Sh, 'Shear (x-direction)')
plt.savefig('shear.png', dpi=100, bbox_inches='tight')
plt.close()

# 5. 합성 변환
M = Sh @ R @ S
fig5 = plot_transformation(M, 'Composite: Shear ∘ Rotation ∘ Scale')
plt.savefig('composite.png', dpi=100, bbox_inches='tight')
plt.close()

print('변환 결과가 이미지로 저장되었습니다.')
```

이 코드는 각 변환이 공간에 미치는 효과를 시각적으로 보여줍니다. 특히 합성 변환에서는 순서가 결과에 큰 영향을 미치는 것을 확인할 수 있습니다. 실무에서는 이런 시각화를 통해 변환의 정확성을 검증합니다.
## 체크리스트

- [ ] 회전, 확대, 반사, 전단 행렬을 구분할 수 있습니다.
- [ ] 행렬 곱을 변환 합성으로 설명할 수 있습니다.
- [ ] 순서가 결과를 바꾼다는 점을 이해합니다.
- [ ] 선형변환과 비선형변환의 차이를 말할 수 있습니다.

## 연습 문제

1. 45도 회전을 두 번 적용하면 왜 90도 회전과 같은지 확인해 보세요.
2. 반사 후 회전과 회전 후 반사가 왜 다른지 예를 들어 설명해 보세요.
3. `(-1, -1)` 스케일링이 공간에 어떤 효과를 만드는지 말해 보세요.

## 정리와 다음 글

선형변환은 행렬을 공간의 언어로 번역해 주는 개념입니다. 회전, 확대, 반사, 전단은 모두 다른 모습이지만, 덧셈과 스칼라곱을 보존한다는 공통 규칙 아래 묶입니다. 이 관점이 잡히면 행렬 계산은 공간을 재구성하는 규칙으로 보이기 시작합니다.

다음 글에서는 기저와 차원으로 넘어갑니다. 공간을 바꾸는 규칙을 봤다면, 이제 그 공간을 표현하는 축과 축의 개수가 무엇인지 정리할 차례입니다.

## 변환 조합을 숫자와 그림으로 동시에 확인하기

선형변환을 제대로 이해하려면 동일한 점 집합에 여러 변환을 적용해 보는 것이 효과적입니다. 아래 코드는 단위 정사각형 꼭짓점에 확대, 회전, 전단을 순서대로 적용합니다.

```python
import numpy as np

pts = np.array([
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.0, 1.0],
]).T

S = np.array([[2.0, 0.0], [0.0, 1.0]])
R = np.array([[0.0, -1.0], [1.0, 0.0]])
H = np.array([[1.0, 0.5], [0.0, 1.0]])

M = H @ R @ S
out = M @ pts

print('transform matrix M:
', M)
print('transformed points:
', out.T)
print('det(M) =', np.linalg.det(M))
```

`det(M)`는 면적 배율과 방향 반전 여부를 알려 줍니다. 변환 순서를 바꾸면 결과 점이 크게 달라지므로, 파이프라인에서는 `R @ S`와 `S @ R`를 엄격히 구분해야 합니다.

## 선형성 조건을 코드로 검증하기

아래 체크는 임의 변환이 정말 선형인지 확인하는 간단한 방법입니다.

```python
T = M
u = np.array([1.0, 2.0])
v = np.array([-1.0, 3.0])
a, b = 2.5, -0.7

lhs = T @ (a * u + b * v)
rhs = a * (T @ u) + b * (T @ v)
print(np.allclose(lhs, rhs))
```

`True`가 나오면 덧셈/스칼라곱 보존이 확인됩니다. 비선형 활성화(ReLU, sigmoid)는 이 조건을 만족하지 않으므로, 신경망은 "선형변환 + 비선형" 조합으로 표현됩니다.

## 응용 표

| 변환 | 대표 행렬 특징 | 실제 응용 |
| --- | --- | --- |
| 회전 | 직교행렬, det=1 | 자세 보정, 좌표계 변환 |
| 반사 | 축 부호 반전, det<0 | 대칭 처리, 이미지 좌우 반전 |
| 전단 | 비대각 원소 강조 | 기하 보정, 애니메이션 효과 |
| 축별 스케일 | 대각 성분 | 피처 재가중, 픽셀 축 변환 |

변환을 수식이 아니라 "공간 조작"으로 읽는 순간, 선형대수는 훨씬 실용적인 도구가 됩니다.

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

## 비선형 변환과의 비교

선형변환이 중요한 이유를 이해하려는 비선형 변환과 비교해야 합니다. 선형변환은 덧셈과 스칼라곱을 보존하지만, 비선형 변환은 그렇지 않습니다.

### 선형변환의 조건

변환 `T`가 선형이려면 모든 벡터 `u`, `v`와 스칼라 `a`, `b`에 대해 다음이 성립해야 합니다:

\[
T(a\mathbf{u} + b\mathbf{v}) = aT(\mathbf{u}) + bT(\mathbf{v})
\]

```python
import numpy as np

# 선형변환 예시: 회전
theta = np.pi / 3
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])

u = np.array([1.0, 2.0])
v = np.array([3.0, 4.0])
a, b = 2.5, -1.3

# 선형성 검증
lhs = R @ (a * u + b * v)
rhs = a * (R @ u) + b * (R @ v)

print('T(au + bv):', lhs)
print('aT(u) + bT(v):', rhs)
print('선형성 만족:', np.allclose(lhs, rhs))
```

### 비선형 변환 예시

비선형 변환은 이 조건을 만족하지 않습니다. 신경망의 활성화 함수(ReLU, sigmoid)가 대표적인 예입니다.

```python
def relu(x):
    return np.maximum(0, x)

u = np.array([1.0, -1.0])
v = np.array([2.0, -2.0])
a, b = 0.5, 0.5

# ReLU는 비선형
lhs = relu(a * u + b * v)
rhs = a * relu(u) + b * relu(v)

print('ReLU(au + bv):', lhs)
print('a ReLU(u) + b ReLU(v):', rhs)
print('선형성 만족:', np.allclose(lhs, rhs))  # False
```

### 신경망 = 선형 + 비선형

신경망의 한 레이어는 선형변환(W @ x + b)과 비선형 활성화(σ)의 조합입니다. 선형변환만으로는 복잡한 함수를 표현할 수 없으므로 비선형성이 필수입니다.

```python
# 신경망 한 레이어 시뮬레이션
W = np.random.randn(3, 4)
b = np.random.randn(3)
x = np.random.randn(4)

# 선형 부분
z = W @ x + b
print('linear output z:', z)

# 비선형 활성화
a = relu(z)
print('activated output a:', a)

# 선형 부분만으로는 복잡한 경계를 표현할 수 없음
# 비선형성이 표현력을 더함
```

### 선형 vs 비선형 비교 표

| 특성 | 선형변환 | 비선형변환 |
| --- | --- | --- |
| 덧셈/스칼라곱 보존 | O | X |
| 행렬로 표현 | O | X |
| 합성의 규칙 | 행렬 곱 | 함수 합성 |
| 예시 | 회전, 반사, 스케일 | ReLU, sigmoid, 제곱 |
| 신경망에서 | 가중치 행렬 | 활성화 함수 |

선형변환은 해석과 계산이 간단하지만 표현력이 제한적이고, 비선형변환은 복잡하지만 표현력이 강합니다. 실무에서는 두 가지를 적절히 조합해 문제를 풀니다.

```python
# 선형 변환만으로는 XOR을 풀 수 없음
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 1, 1, 0])  # XOR

# 선형 변환 W @ X^T는 선형 경계만 표현 가능
# 하지만 선형 + 비선형 조합은 XOR 표현 가능
# 이것이 신경망이 두 가지를 모두 사용하는 이유
```

선형변환의 한계를 이해하면, 왜 머신러닝 모델이 비선형 활성화를 필수로 하는지 명확해집니다. 동시에 선형 부분을 잘 설계하는 것이 효율적 학습의 출발점이라는 점도 알 수 있습니다.
## 마무리 계산 메모

마지막으로, 각 장의 예제를 실행할 때는 입력 형상, 출력 형상, 오차 지표를 함께 기록해 두는 편이 좋습니다. 같은 수식이라도 데이터 스케일과 기저 선택에 따라 해석이 크게 달라질 수 있기 때문입니다. 실무에서는 이 메모가 재현성과 디버깅 속도를 결정합니다.


추가로, 수치 실험 결과를 남길 때는 난수 시드와 라이브러리 버전도 함께 기록하면 재현성이 크게 좋아집니다.

검증 로그를 남기면 다음 실험에서 비교 기준을 일관되게 유지할 수 있습니다.

## 실전 연결: 변환 시각화와 합성 순서 점검

선형변환을 실제로 이해하는 가장 빠른 방법은 같은 점 집합에 서로 다른 행렬을 적용해 전후 좌표를 비교하는 것입니다. 특히 회전과 확대를 합성할 때 순서를 바꾸면 결과가 달라진다는 점을 눈으로 확인하면, 행렬 곱의 비가환성이 자연스럽게 받아들여집니다.

```python
import numpy as np

points = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
theta = np.deg2rad(30)
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
S = np.array([[2.0, 0.0], [0.0, 0.5]])

p1 = points @ (R @ S).T
p2 = points @ (S @ R).T
print('R@S 결과:
', p1)
print('S@R 결과:
', p2)
```

이 계산은 그래픽스 파이프라인과 데이터 전처리 모두에 직접 연결됩니다. 좌표 변환을 여러 단계로 적용하는 시스템에서는 순서가 곧 의미이며, 잘못된 순서는 예측 가능한 버그로 이어집니다.

또한 머신러닝에서도 같은 감각이 필요합니다. 입력을 특정 축으로 회전하거나 스케일링하는 전처리는 결국 선형변환이며, 주성분 기저로 투영하는 과정도 동일한 연산 구조를 가집니다. 변환을 행렬로 읽는 습관은 모델 해석과 디버깅 모두에서 강력한 기준점이 됩니다.

## 처음 질문으로 돌아가기

- **행렬을 곱한다는 말은 공간에 어떤 변화를 주는 걸까요?**
  - 본문의 기준은 선형변환를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **회전, 확대, 반사, 전단은 행렬 모양으로 어떻게 드러날까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **변환의 합성은 왜 행렬 곱으로 표현될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linear Algebra 101 (1/10): 선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): 벡터](./02-vectors.md)
- [Linear Algebra 101 (3/10): 행렬](./03-matrices.md)
- [Linear Algebra 101 (4/10): 내적과 거리](./04-inner-product-and-distance.md)
- **선형변환 (현재 글)**
- 기저와 차원 (예정)
- 고유값과 고유벡터 (예정)
- 행렬 분해 (예정)
- PCA (예정)
- 머신러닝에서의 선형대수 (예정)

<!-- toc:end -->

## 참고 자료

- 시리즈 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/linear-algebra-101/ko
- [3Blue1Brown — Linear transformations](https://www.3blue1brown.com/lessons/linear-transformations)
- [Wikipedia — Linear map](https://en.wikipedia.org/wiki/Linear_map)
- [Wikipedia — Rotation matrix](https://en.wikipedia.org/wiki/Rotation_matrix)
- [Khan Academy — Transformations](https://www.khanacademy.org/math/linear-algebra/matrix-transformations)

Tags: LinearAlgebra, LinearTransformation, Geometry, DataScience, Beginner
