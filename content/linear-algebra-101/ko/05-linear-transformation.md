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

## 이 글에서 다룰 문제

- 행렬을 곱한다는 말은 공간에 어떤 변화를 주는 걸까요?
- 회전, 확대, 반사, 전단은 행렬 모양으로 어떻게 드러날까요?
- 변환의 합성은 왜 행렬 곱으로 표현될까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

신경망의 각 레이어는 선형변환과 비선형 활성화의 조합입니다. 컴퓨터 그래픽스의 모델 행렬, 컴퓨터 비전의 좌표 변환, 데이터 증강의 회전과 확대도 모두 같은 틀로 설명할 수 있습니다.

선형변환 감각이 생기면 행렬이 더 이상 숫자판이 아닙니다. 어떤 행렬은 축을 늘리고, 어떤 행렬은 공간을 돌리고, 어떤 행렬은 방향을 뒤집습니다. 그 순간부터 선형대수 계산은 움직임과 구조를 설명하는 언어가 됩니다.

## 핵심 용어 정리

선형변환의 핵심은 입력 벡터 하나가 아니라 공간 전체가 함께 바뀐다는 사실입니다.

- **선형변환**: `T(av + bw) = aT(v) + bT(w)`를 만족하는 규칙입니다.
- **회전**: 각도를 유지한 채 방향만 돌리는 변환입니다.
- **확대와 축소**: 대각 성분으로 길이를 조절하는 변환입니다.
- **반사**: 축이나 직선을 기준으로 방향을 뒤집는 변환입니다.
- **전단**: 한 축 방향으로 공간을 기울이는 변환입니다.

## 대표 선형변환

선형변환은 벡터 공간을 바꾸는 규칙입니다. 각 변환은 특징적인 행렬 형태와 기하학적 효과를 가집니다.

| 변환 | 행렬 | 기하 효과 |
| --- | --- | --- |
| 회전 (`θ` 라디안) | `[[cosθ, -sinθ], [sinθ, cosθ]]` | 각도 보존, 길이 보존, 방향만 변경 |
| 반사 (x축) | `[[1, 0], [0, -1]]` | y좌표 부호 반전, 상하 반전 |
| 축소/확대 | `[[s_x, 0], [0, s_y]]` | 축별 독립 스케일링 |
| 사영 (x축으로) | `[[1, 0], [0, 0]]` | y성분 제거, 차원 감소 |
| 전단 (x 방향) | `[[1, k], [0, 1]]` | 평행사변형, 면적 보존 |

회전과 반사는 길이를 보존하고, 전단은 평행성을 보존합니다. 사영은 차원을 줄이므로 역행렬이 없습니다.

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
print("rotated:", R @ v)  # [0.707, 0.707]
print("||Rv|| =", np.linalg.norm(R @ v))  # 1.0: 길이 보존
```

회전 행렬은 방향을 바꾸되 구조를 보존하는 대표적인 선형변환입니다. 좌표가 바뀌어도 공간의 기본 질서는 유지됩니다.

### 2단계 — 확대와 축소

```python
S = np.diag([2.0, 0.5])
v = np.array([1.0, 1.0])
print("scaled:", S @ v)  # [2.0, 0.5]
print("det(S):", np.linalg.det(S))  # 1.0: 면적 비율
```

대각행렬은 각 축을 독립적으로 늘리거나 줄입니다. 행렬식은 면적이 얼마나 바뀌는지 알려 줍니다.

### 3단계 — 반사

```python
F = np.array([[1.0, 0.0], [0.0, -1.0]])
print("reflected:", F @ np.array([1.0, 1.0]))  # [1.0, -1.0]
print("det(F):", np.linalg.det(F))  # -1.0: 방향 반전
```

반사는 한 축에 대해 부호를 뒤집습니다. 행렬식이 음수이므로 방향성이 뒤집힙니다.

### 4단계 — 전단

```python
Sh = np.array([[1.0, 1.0], [0.0, 1.0]])
print("sheared:", Sh @ np.array([1.0, 1.0]))  # [2.0, 1.0]
print("det(Sh):", np.linalg.det(Sh))  # 1.0: 면적 보존
```

전단은 격자를 기울입니다. 직사각형이 평행사변형으로 바뀌는 식의 변화를 떠올리면 감이 잘 옵니다.

### 5단계 — 변환 합성

```python
theta = np.pi / 4
R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
S = np.diag([2.0, 0.5])
M = R @ S  # 먼저 확대, 그 다음 회전
print("compose RS:", M @ np.array([1.0, 0.0]))
# 순서를 바꾸면 다른 결과
M2 = S @ R
print("compose SR:", M2 @ np.array([1.0, 0.0]))
print("same?", np.allclose(M @ np.array([1.0, 0.0]),
                            M2 @ np.array([1.0, 0.0])))  # False
```

합성은 선형변환의 진짜 핵심입니다. 순서가 바뀌면 결과도 바뀝니다.

## 선형성 조건을 코드로 검증하기

변환 `T`가 선형이려면 `T(au + bv) = aT(u) + bT(v)`가 성립해야 합니다.

```python
import numpy as np

theta = np.pi / 3
T = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])

u = np.array([1.0, 2.0])
v = np.array([3.0, 4.0])
a, b = 2.5, -1.3

lhs = T @ (a * u + b * v)
rhs = a * (T @ u) + b * (T @ v)

print('T(au + bv):', lhs)
print('aT(u) + bT(v):', rhs)
print('선형성 만족:', np.allclose(lhs, rhs))  # True
```

## 비선형 변환과의 비교

비선형 변환은 이 조건을 만족하지 않습니다. 신경망의 활성화 함수(ReLU, sigmoid)가 대표적인 예입니다.

```python
import numpy as np

def relu(x):
    return np.maximum(0, x)

u = np.array([1.0, -1.0])
v = np.array([2.0, -2.0])
a, b = 0.5, 0.5

lhs = relu(a * u + b * v)
rhs = a * relu(u) + b * relu(v)

print('ReLU(au + bv):', lhs)      # [1.5, 0.0]
print('a*ReLU(u) + b*ReLU(v):', rhs)  # [1.5, 0.0] or diff
print('선형성 만족:', np.allclose(lhs, rhs))  # 상황에 따라 False
```

신경망은 "선형변환(W @ x) + 비선형 활성화(σ)"의 조합입니다. 선형 부분만으로는 복잡한 경계를 표현할 수 없어 비선형성이 필수입니다.

## 변환 합성 순서 점검

실무에서 변환 파이프라인의 순서는 매우 중요합니다.

```python
import numpy as np

pts = np.array([
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.0, 1.0],
]).T  # (2, 4)

S = np.array([[2.0, 0.0], [0.0, 1.0]])   # x축 2배 확대
R = np.array([[0.0, -1.0], [1.0, 0.0]])  # 90도 회전
H = np.array([[1.0, 0.5], [0.0, 1.0]])   # 전단

M = H @ R @ S  # S 먼저, R 그 다음, H 마지막
out = M @ pts

print('변환 행렬 M:\n', M)
print('변환된 점들:\n', out.T)
print('det(M) =', np.linalg.det(M))  # 면적 변환 비율
```

`det(M)`는 면적 배율과 방향 반전 여부를 알려 줍니다.

## 응용 표

| 변환 | 대표 행렬 특징 | 실제 응용 |
| --- | --- | --- |
| 회전 | 직교행렬, det=1 | 자세 보정, 좌표계 변환 |
| 반사 | 축 부호 반전, det<0 | 대칭 처리, 이미지 좌우 반전 |
| 전단 | 비대각 원소 강조 | 기하 보정, 애니메이션 효과 |
| 축별 스케일 | 대각 성분 | 피처 재가중, 픽셀 축 변환 |
| 사영 | 랭크 감소, det=0 | 차원 축소, 그림자 효과 |

변환을 수식이 아니라 "공간 조작"으로 읽는 순간, 선형대수는 훨씬 실용적인 도구가 됩니다.

## 변환 파이프라인 디버깅

실무에서 변환 순서나 부호 오류는 디버깅하기 까다롭습니다. 단위 벡터를 추적하면 어느 단계에서 틀렸는지 빠르게 파악할 수 있습니다.

```python
import numpy as np

def trace_transform(M, label=''):
    """단위 벡터에 변환을 적용해 각 축의 이동을 출력합니다."""
    e1 = np.array([1.0, 0.0])
    e2 = np.array([0.0, 1.0])
    print(f'[{label}] e1 -> {M @ e1}')
    print(f'[{label}] e2 -> {M @ e2}')
    print(f'[{label}] det = {np.linalg.det(M):.4f}')

theta = np.pi / 6  # 30도

R = np.array([[np.cos(theta), -np.sin(theta)],
              [np.sin(theta),  np.cos(theta)]])
S = np.diag([3.0, 1.0])

trace_transform(S, 'Scale')
trace_transform(R, 'Rotate')
trace_transform(R @ S, 'Scale then Rotate')
trace_transform(S @ R, 'Rotate then Scale')
```

단위 벡터 `e1`, `e2`가 변환 후 어디로 가는지 확인하면 회전 방향이 맞는지, 스케일이 원하는 축에 적용됐는지 즉시 알 수 있습니다.

## 변환별 행렬식 해석

| 변환 유형 | det 범위 | 의미 |
| --- | --- | --- |
| 회전 | det = 1 | 면적 보존, 방향 보존 |
| 반사 | det = -1 | 면적 보존, 방향 반전 |
| 균일 확대 (k배) | det = k^n | 면적 k^n 배 증가 |
| 사영 | det = 0 | 차원 손실, 역행렬 없음 |
| 전단 | det = 1 | 면적 보존, 형태 변형 |

행렬식이 0이면 역변환이 불가능합니다. 신경망에서 가중치 행렬의 행렬식이 0에 가까워지면 그래디언트 소실 문제가 발생할 수 있습니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 회전 방향의 부호를 뒤집음 | 예상과 반대 방향으로 회전 | `theta > 0`이면 반시계 방향 확인 |
| 음수 스케일에 반사 효과 포함 | 예상치 못한 좌우 반전 | `det < 0`이면 방향 반전 포함 확인 |
| 합성 순서를 거꾸로 적용 | 전혀 다른 변환 결과 | `A @ B`는 B 먼저 적용임을 명심 |
| 비선형변환을 선형처럼 다룸 | 선형성 조건 미충족 | `T(au+bv) == aT(u)+bT(v)` 검증 |
| 전단이 어느 축 기준인지 혼동 | 기울기 방향 오류 | 단위 벡터에 적용해 결과 시각 확인 |

## 실무에서는 이렇게 읽는다

시니어 엔지니어는 행렬을 볼 때 그 행렬이 공간을 어떻게 바꾸는지 떠올립니다. 좌표계가 회전하는지, 축별 스케일이 달라지는지, 방향성이 뒤집히는지를 읽을 수 있어야 모델 내부의 계산도 감이 잡힙니다.

또한 합성 순서를 매우 조심합니다. 그래픽스 파이프라인이든 신경망 레이어든 계산 순서가 바뀌면 완전히 다른 변환이 되기 때문입니다. 선형변환 감각은 계산을 그림으로 번역하는 능력과 거의 같습니다.

## 운영 체크리스트

- [ ] 회전, 확대, 반사, 전단 행렬을 구분할 수 있습니다.
- [ ] 행렬 곱을 변환 합성으로 설명할 수 있습니다.
- [ ] 순서가 결과를 바꾼다는 점을 이해합니다.
- [ ] 선형변환과 비선형변환의 차이를 말할 수 있습니다.
- [ ] 행렬식으로 면적 배율과 방향 반전 여부를 판단할 수 있습니다.
- [ ] 단위 벡터 추적으로 변환 파이프라인을 디버깅할 수 있습니다.

## 연습 문제

1. 45도 회전을 두 번 적용하면 왜 90도 회전과 같은지 확인해 보세요.
2. 반사 후 회전과 회전 후 반사가 왜 다른지 예를 들어 설명해 보세요.
3. `(-1, -1)` 스케일링이 공간에 어떤 효과를 만드는지 말해 보세요.

## 정리와 다음 글

선형변환은 행렬을 공간의 언어로 번역해 주는 개념입니다. 회전, 확대, 반사, 전단은 모두 다른 모습이지만, 덧셈과 스칼라곱을 보존한다는 공통 규칙 아래 묶입니다. 이 관점이 잡히면 행렬 계산은 공간을 재구성하는 규칙으로 보이기 시작합니다.

다음 글에서는 기저와 차원으로 넘어갑니다. 공간을 바꾸는 규칙을 봤다면, 이제 그 공간을 표현하는 축과 축의 개수가 무엇인지 정리할 차례입니다.

## 처음 질문으로 돌아가기

- **행렬을 곱한다는 말은 공간에 어떤 변화를 주는 걸까요?**
  - 행렬을 벡터에 곱한다는 것은 그 벡터를 포함한 공간 전체에 변환을 적용하는 것입니다. 회전, 확대, 반사, 전단 등 다양한 공간 변화가 행렬 하나로 압축되어 표현됩니다.

- **회전, 확대, 반사, 전단은 행렬 모양으로 어떻게 드러날까요?**
  - 회전은 직교 행렬(det=1), 확대는 대각 행렬, 반사는 det < 0인 행렬, 전단은 비대각 원소가 있는 행렬로 나타납니다. 행렬식과 행렬 구조만 봐도 어떤 변환인지 빠르게 파악할 수 있습니다.

- **변환의 합성은 왜 행렬 곱으로 표현될까요?**
  - 선형변환은 행렬로 표현할 수 있고, 두 선형변환의 합성도 선형변환입니다. 그래서 합성 변환도 행렬로 표현되며, 그 행렬은 두 행렬의 곱과 같습니다. 이것이 행렬 곱이 변환 합성을 의미하는 이유입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linear Algebra 101 (1/10): 선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- [Linear Algebra 101 (2/10): 벡터](./02-vectors.md)
- [Linear Algebra 101 (3/10): 행렬](./03-matrices.md)
- [Linear Algebra 101 (4/10): 내적과 거리](./04-inner-product-and-distance.md)
- **Linear Algebra 101 (5/10): 선형변환 (현재 글)**
- [Linear Algebra 101 (6/10): 기저와 차원](./06-basis-and-dimension.md)
- [Linear Algebra 101 (7/10): 고유값과 고유벡터](./07-eigenvalues-and-eigenvectors.md)
- [Linear Algebra 101 (8/10): 행렬 분해](./08-matrix-decomposition.md)
- [Linear Algebra 101 (9/10): PCA](./09-pca.md)
- [머신러닝에서의 선형대수](./10-linear-algebra-in-ml.md)

<!-- toc:end -->

## 참고 자료

- 시리즈 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/linear-algebra-101/ko
- [3Blue1Brown — Linear transformations](https://www.3blue1brown.com/lessons/linear-transformations)
- [Wikipedia — Linear map](https://en.wikipedia.org/wiki/Linear_map)
- [Wikipedia — Rotation matrix](https://en.wikipedia.org/wiki/Rotation_matrix)
- [Khan Academy — Transformations](https://www.khanacademy.org/math/linear-algebra/matrix-transformations)

Tags: LinearAlgebra, LinearTransformation, Geometry, DataScience, Beginner
