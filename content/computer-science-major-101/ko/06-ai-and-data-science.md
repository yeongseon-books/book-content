---
series: computer-science-major-101
episode: 6
title: AI와 데이터사이언스
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - CS
  - AI
  - DataScience
  - ML
  - Beginner
seo_description: AI와 데이터사이언스 과목의 흐름, 머신러닝 입문, 통계 기초, 데이터 분석을 정리한 글
code_required: false
last_reviewed: '2026-05-14'
---

# AI와 데이터사이언스

AI와 데이터사이언스는 가장 화려해 보이는 분야이지만, 막상 들어가 보면 통계와 데이터 정리, 평가와 검증 같은 기초 작업이 훨씬 더 많은 비중을 차지합니다. 모델 이름만 외우는 방식으로는 오래 버티기 어렵습니다.

이 글은 Computer Science Major 101 시리즈의 6번째 글입니다.

## 이 글에서 다룰 문제

- AI와 데이터사이언스는 전공 안에서 어떻게 나뉘고 어떻게 연결될까요?
- 통계, 머신러닝, 딥러닝, 데이터 분석은 어떤 흐름으로 이어질까요?
- 모델만 보는 공부가 왜 금방 한계에 부딪힐까요?
- 데이터 품질과 분포를 본다는 말은 실제로 무엇을 뜻할까요?

## 이 글에서 배울 것

- 통계의 기초
- 머신러닝 입문
- 딥러닝의 기본 위치
- 데이터 분석
- 두 영역의 역할 분담

## 왜 중요한가

데이터 감각은 이제 특정 직무만의 능력이 아니라 거의 모든 현대 엔지니어에게 필요한 기본기입니다. 무엇보다 모델 성능은 데이터와 평가 체계 위에서만 의미를 가지므로, 겉으로 보이는 결과보다 바닥 구조를 읽는 힘이 더 중요합니다.

## 한눈에 보는 개념

![AI 학습 흐름](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/06/06-01-ai-learning-pipeline.ko.png)

*데이터에서 통계, 모델링, 분석으로 이어지는 AI 학습 흐름*

> 데이터는 재료이고, 통계는 읽는 언어이며, 모델은 그 위에서 패턴을 계산하는 도구입니다.

데이터가 출발점이고, 통계는 그 데이터를 읽는 언어입니다. 머신러닝과 신경망은 그 위에서 예측 모델을 만들고, 분석은 결과를 해석하고 실제 문제에 연결합니다. 분야 이름이 달라도 흐름은 이어져 있습니다.

## 핵심 용어

- **특성(feature)**: 모델이 입력으로 받는 변수입니다.
- **레이블(label)**: 맞혀야 하는 목표 값입니다.
- **학습(training)**: 데이터로부터 패턴을 익히는 과정입니다.
- **추론(inference)**: 학습한 모델로 예측을 수행하는 과정입니다.
- **데이터셋(dataset)**: 분석과 학습에 쓰는 데이터 묶음입니다.

## Before/After

**Before**: 모델 이름과 성능 숫자만 봅니다.

**After**: 데이터 품질, 분포, 평가 방법까지 함께 봅니다.

## 실습: 미니 ML 파이프라인

### 1단계 — 데이터

```python
xs = [1, 2, 3, 4]
ys = [2, 4, 6, 8]
```

가장 작은 지도 학습 예시입니다. 입력과 정답의 짝이 있어야 이후 단계가 의미를 가집니다.

### 2단계 — 평균

```python
avg = sum(ys) / len(ys)
```

평균 같은 기초 통계량은 모델보다 먼저 데이터를 읽는 출발점입니다. 데이터의 중심도 모른 채 모델만 고르는 습관은 오래 가지 않습니다.

### 3단계 — 회귀 기울기

```python
def slope(xs, ys):
    mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    den = sum((x-mx)**2 for x in xs)
    return num / den
```

가장 단순한 회귀 예시지만, 모델도 결국 데이터 관계를 수학적으로 근사하는 함수라는 사실을 잘 보여 줍니다.

### 4단계 — 예측

```python
m = slope(xs, ys)
pred = m * 5
```

학습이 끝나면 새로운 입력에 값을 예측합니다. 이 단계가 현업에서는 추론 비용, 응답 속도, 운영 품질과 연결됩니다.

### 5단계 — 평가

```python
mae = sum(abs(m*x - y) for x, y in zip(xs, ys)) / len(xs)
```

모델은 결과를 내는 것만으로 충분하지 않습니다. 얼마나 틀렸는지 수치로 봐야 비로소 비교와 개선이 가능합니다.

## 이 코드에서 먼저 볼 점

- 통계는 모델보다 먼저 데이터를 읽게 해 줍니다.
- 예측은 결국 함수 적용입니다.
- 평가는 학습 결과를 믿어도 되는지 보여 주는 근거입니다.

## 자주 하는 실수 5가지

1. **데이터 누수를 만드는 일입니다.**
2. **학습 데이터와 테스트 데이터를 섞는 일입니다.**
3. **스케일 차이를 무시한 채 비교하는 일입니다.**
4. **기준선 모델 없이 복잡한 모델부터 고르는 일입니다.**
5. **평가 지표를 모호하게 두는 일입니다.**

## 실무에서는 이렇게 드러납니다

모델 운영에서 가장 중요한 능력 중 하나는 분포 변화 감지입니다. 학습할 때의 데이터와 운영 데이터가 달라지면 성능은 빠르게 흔들립니다. 그래서 강한 팀일수록 모델 자체보다 데이터 흐름과 평가 체계를 더 자주 점검합니다.

## 선배 엔지니어는 이렇게 봅니다

- 모델보다 데이터가 더 중요할 때가 많습니다.
- 복잡한 모델보다 기준선 모델이 먼저입니다.
- 평가는 주장보다 강한 증거입니다.
- 해석 가능성도 중요합니다.
- 재현성이 없으면 결과를 믿기 어렵습니다.

## 체크리스트

- [ ] 학습용과 평가용 데이터를 분리했습니다.
- [ ] 기준선 모델을 하나 세워 보았습니다.
- [ ] 어떤 지표로 비교할지 정했습니다.
- [ ] 시드 고정과 재현성의 의미를 이해했습니다.

## 연습 문제

1. 특성을 한 줄로 설명해 보세요.
2. 레이블을 한 줄로 설명해 보세요.
3. 모델의 의미를 한 줄로 적어 보세요.

## 정리

AI와 데이터사이언스는 다른 이름을 갖고 있지만, 전공 안에서는 데이터 이해와 모델링이라는 하나의 흐름 안에 놓여 있습니다. 통계와 데이터 분석이 바닥을 만들고, 그 위에 머신러닝과 딥러닝이 올라갑니다. 다음 글에서는 이렇게 쌓은 지식을 실제 산출물로 묶는 프로젝트 과목을 살펴보겠습니다.

<!-- toc:begin -->
- [컴퓨터학과에서는 무엇을 배우는가](./01-what-cs-majors-learn.md)
- [1학년 과목 이해하기](./02-first-year-subjects.md)
- [자료구조와 알고리즘](./03-data-structures-and-algorithms.md)
- [시스템 과목 이해하기](./04-systems-subjects.md)
- [데이터베이스와 네트워크](./05-database-and-network.md)
- **AI와 데이터사이언스 (현재 글)**
- 프로젝트 과목 (예정)
- 전공 공부 방법 (예정)
- 포트폴리오로 연결하기 (예정)
- 졸업 전 갖춰야 할 역량 (예정)
<!-- toc:end -->

## 참고 자료

- [An Introduction to Statistical Learning](https://www.statlearning.com/)
- [Deep Learning Book - Goodfellow](https://www.deeplearningbook.org/)
- [Pattern Recognition and Machine Learning](https://www.microsoft.com/en-us/research/uploads/prod/2006/01/Bishop-Pattern-Recognition-and-Machine-Learning-2006.pdf)
- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)

Tags: CS, AI, DataScience, ML, Beginner
