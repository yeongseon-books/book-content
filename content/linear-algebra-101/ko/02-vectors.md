---
series: linear-algebra-101
episode: 2
title: 벡터
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - LinearAlgebra
  - Vectors
  - NumPy
  - DataScience
  - Beginner
seo_description: 벡터의 정의, 덧셈·스칼라곱·노름·정규화 같은 기본 연산과 기하학적 의미를 코드로 정리한 입문 글
last_reviewed: '2026-05-04'
---

# 벡터

> Linear Algebra 101 시리즈 (2/10)


## 이 글에서 다룰 문제

ML에서 *데이터의 한 행* 은 *벡터* 입니다. *벡터 연산* 을 *제대로 다루지 못하면* 모델 입력부터 막힙니다.

> *Vectors are how we package data for machines.*

## 전체 흐름
```mermaid
flowchart LR
    Arrow["Arrow (geometry)"] --> Vec["Vector"]
    Coord["Coordinates (algebra)"] --> Vec
    Row["Data row (ML)"] --> Vec
```

## Before/After

**Before**: *“벡터는 그냥 리스트.”* — 기하학적 의미 *없음*.

**After**: *“벡터는 *공간의 점/화살표* 이며 *연산은 기하학적 변형*.”*

## 5단계 벡터 다루기

### 1단계 — 벡터 만들기

```python
import numpy as np
v = np.array([3.0, 4.0])
w = np.array([1.0, 2.0])
print("v:", v, "w:", w)
```

### 2단계 — 덧셈과 뺄셈

```python
print("v+w:", v + w)
print("v-w:", v - w)
```

### 3단계 — 스칼라곱

```python
print("2v:", 2 * v)
print("-v:", -v)
```

### 4단계 — 노름

```python
norm_v = np.linalg.norm(v)
print("||v||:", norm_v)
```

### 5단계 — 정규화 (단위벡터)

```python
unit_v = v / np.linalg.norm(v)
print("unit v:", unit_v, "norm:", np.linalg.norm(unit_v))
```

## 이 코드에서 주목할 점

- *NumPy* 의 *벡터 연산* 은 *원소별*.
- *노름* 은 *L2(유클리드)* 가 *기본*.
- *정규화* 는 *방향 보존*, *길이만 1*.

## 자주 하는 실수 5가지

1. ***차원 불일치* 에서 *암묵 broadcasting* 의존.**
2. ***노름 0 벡터* 정규화 — *0으로 나눔*.**
3. ***행벡터/열벡터* 구분을 *대충*.**
4. ***내적과 원소곱* 혼동.**
5. ***부동소수점 오차* 무시.**

## 실무에서는 이렇게 쓰입니다

ML 입력 피처, *임베딩 벡터*, 추천 시스템의 *유저/아이템 벡터*, NLP의 *단어 임베딩* — 모두 *벡터의 연산* 입니다.

## 체크리스트

- [ ] *벡터 덧셈/스칼라곱* 가능.
- [ ] *노름* 계산 가능.
- [ ] *정규화* 가능.
- [ ] *기하학적 의미* 를 안다.

## 정리 및 다음 단계

벡터는 *공간의 점/화살표* 이며 *데이터의 한 행* 입니다. 다음 글에서는 *행렬* 을 다룹니다.

<!-- toc:begin -->
- [선형대수란 무엇인가?](./01-what-is-linear-algebra.md)
- **벡터 (현재 글)**
- 행렬 (예정)
- 내적과 거리 (예정)
- 선형변환 (예정)
- 기저와 차원 (예정)
- 고유값과 고유벡터 (예정)
- 행렬 분해 (예정)
- PCA (예정)
- 머신러닝에서의 선형대수 (예정)
<!-- toc:end -->

## 참고 자료

- [3Blue1Brown — Vectors](https://www.3blue1brown.com/lessons/vectors)
- [Khan Academy — Vectors](https://www.khanacademy.org/math/linear-algebra/vectors-and-spaces)
- [NumPy — Array creation](https://numpy.org/doc/stable/user/basics.creation.html)
- [Wikipedia — Euclidean vector](https://en.wikipedia.org/wiki/Euclidean_vector)

Tags: LinearAlgebra, Vectors, NumPy, DataScience, Beginner
