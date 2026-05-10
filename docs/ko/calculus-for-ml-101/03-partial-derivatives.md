---
series: calculus-for-ml-101
episode: 3
title: 편미분
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Calculus
  - ML
  - PartialDerivative
  - MultiVariable
  - Beginner
seo_description: 편미분의 정의, 다변수 함수, 변수 고정, 부분 기울기, ML 가중치 의미를 입문자 관점에서 정리한 글
last_reviewed: '2026-05-04'
---

# 편미분

> Calculus for ML 101 시리즈 (3/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *여러 입력* 을 가진 함수에서 *한 변수* 의 *영향* 만 *어떻게* 측정할까요?

> *편미분* 은 *나머지를 고정* 하고 *한 변수* 만 본다는 약속입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *다변수 함수*
- *편미분* 의 정의
- *변수 고정* 직관
- *부분 기울기*
- ML *가중치* 의 의미

## 왜 중요한가

ML 모델의 *모든 가중치* 는 *편미분* 으로 *책임 비율* 을 받습니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    F[f x y] --> A[Hold y]
    A --> X[Partial dx]
    F --> B[Hold x]
    B --> Y[Partial dy]
```

## 핵심 용어 정리

- **multivariable**: *여러* 입력.
- **partial**: *나머지 고정* 미분.
- **slice**: *한 변수* 만 *움직이는* 단면.
- **per-variable**: *변수별* 기울기.
- **weight**: ML의 *학습 가능* 변수.

## Before/After

**Before**: *모든 입력* 을 한꺼번에 본다.

**After**: *한 입력* 만 *분리* 해서 본다.

## 실습: 미니 편미분 키트

### 1단계 — 다변수 함수

```python
def f(x, y):
    return x ** 2 + 3 * y
```

### 2단계 — x에 대한 편미분

```python
def partial_x(f, x, y, h=1e-5):
    return (f(x + h, y) - f(x - h, y)) / (2 * h)
```

### 3단계 — y에 대한 편미분

```python
def partial_y(f, x, y, h=1e-5):
    return (f(x, y + h) - f(x, y - h)) / (2 * h)
```

### 4단계 — 두 편미분 한 번에

```python
def partials(f, x, y):
    return partial_x(f, x, y), partial_y(f, x, y)
```

### 5단계 — ML 가중치 직관

```python
def loss(w1, w2):
    return (w1 - 1) ** 2 + (w2 + 2) ** 2

g1, g2 = partials(loss, 0.0, 0.0)  # 각 가중치의 책임
```

## 이 코드에서 주목할 점

- *편미분* 은 *변수 하나* 만 *움직임*.
- *나머지* 는 *고정*.
- *각 가중치* 가 *각자의 기울기*.

## 자주 하는 실수 5가지

1. ***모든 변수* 를 동시에 *바꿈*.**
2. ***h* 를 *변수마다* 다르게 잡음.**
3. ***고정* 변수의 *값* 영향을 무시.**
4. ***편미분* 과 *전미분* 혼동.**
5. ***기울기 벡터* 의 *순서* 혼동.**

## 실무에서는 이렇게 쓰입니다

*가중치별 책임* 을 계산해 *역전파* 가 *각 파라미터* 를 *적절히* 갱신합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *편미분* 은 *책임 분배*.
- *순서* 를 *문서화*.
- *고정* 변수도 *값* 이 영향.
- *벡터화* 가 효율.
- *로컬* 관점이 *전역* 의 시작.

## 체크리스트

- [ ] *변수* 분리.
- [ ] *순서* 명시.
- [ ] *고정* 값 기록.
- [ ] *벡터화* 로 묶기.

## 연습 문제

1. *편미분* 한 줄 정의.
2. *다변수 함수* 한 줄 정의.
3. *책임 분배* 의 의미 한 줄.

## 정리 및 다음 단계

다음 글은 *Gradient* 입니다.

<!-- toc:begin -->
- [미분이란 무엇인가](./01-what-is-derivative.md)
- [함수와 기울기](./02-functions-and-slope.md)
- **편미분 (현재 글)**
- Gradient (예정)
- 연쇄 법칙 (예정)
- 손실 함수 (예정)
- 경사하강법 (예정)
- 최적화 (예정)
- 역전파 직관 (예정)
- 딥러닝에서의 미분 (예정)
<!-- toc:end -->

## 참고 자료

- [Partial Derivatives - Khan Academy](https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives)
- [Multivariable Calculus - MIT OCW](https://ocw.mit.edu/courses/18-02-multivariable-calculus-fall-2007/)
- [Deep Learning Book - Chapter 4](https://www.deeplearningbook.org/contents/numerical.html)
- [JAX Automatic Differentiation](https://jax.readthedocs.io/en/latest/notebooks/autodiff_cookbook.html)
