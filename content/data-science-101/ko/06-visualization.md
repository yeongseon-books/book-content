---
series: data-science-101
episode: 6
title: 시각화
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataScience
  - Visualization
  - Matplotlib
  - Seaborn
  - Beginner
seo_description: 어떤 그래프를 언제 쓸지 한눈에 정리한 시각화 입문 — 분포, 비교, 추세, 관계, 비율을 위한 5가지 차트
last_reviewed: '2026-05-04'
---

# 시각화

> Data Science 101 시리즈 (6/10)


## 이 글에서 다룰 문제

데이터는 *그림으로 봐야 빠릅니다*. 잘못된 차트는 *잘못된 결정* 을 부릅니다. *메시지 → 차트* 매핑을 익히면 *오해의 절반* 이 사라집니다.

> *시각화는 *분석의 마지막 한 줄* 이다.*

## 전체 흐름
```mermaid
flowchart LR
    Dist["Distribution"] --> Hist["Histogram / Box"]
    Comp["Comparison"] --> Bar["Bar Chart"]
    Trend["Trend"] --> Line["Line Chart"]
    Rel["Relation"] --> Scatter["Scatter"]
    Part["Part of Whole"] --> Stack["Stacked Bar"]
```

## Before/After

**Before**: *3D 파이 차트* 로 *비율* 을 보여줘 *비교 불가능*.

**After**: *수평 막대 차트* 로 *정확한 비교*.

## 5단계 시각화

### 1단계 — 분포 (Histogram)

```python
import matplotlib.pyplot as plt
df["amount"].plot.hist(bins=30, title="amount distribution")
plt.show()
```

### 2단계 — 비교 (Bar)

```python
df.groupby("country")["amount"].sum().sort_values().plot.barh(title="revenue by country")
plt.show()
```

### 3단계 — 추세 (Line)

```python
df.groupby("order_date")["amount"].sum().plot(title="daily revenue")
plt.show()
```

### 4단계 — 관계 (Scatter + facet)

```python
import seaborn as sns
sns.relplot(data=df.sample(2000), x="quantity", y="amount", col="country", col_wrap=3)
```

### 5단계 — 주석/색

```python
ax = df.groupby("order_date")["amount"].sum().plot()
ax.axvline(pd.Timestamp("2026-04-01"), color="red", linestyle="--", label="campaign")
ax.legend()
```

## 이 코드에서 주목할 점

- *메시지 → 차트* 매핑이 *우선*.
- *축의 척도* 가 *해석* 을 *바꾼다*.
- *주석* 은 *말로 설명* 할 시간을 *줄여준다*.

## 자주 하는 실수 5가지

1. ***3D 차트* 사용.** *비교* 가 *어려워* 진다.
2. ***이중 축* 남용.** *오독* 의 *원인*.
3. ***색* 만으로 *카테고리* 구분.** *색약* 사용자에게 *불친절*.
4. **축 *0 에서 시작* 하지 않은 *bar*.** 차이가 *과장*.
5. ***라벨* 없는 차트.** *재사용 불가*.

## 실무에서는 이렇게 쓰입니다

분석가는 *Tableau / Looker* 의 차트와 *Python* 의 차트를 *함께* 씁니다. *대시보드* 는 *주간 리포트* 의 *기본 단위*.

## 체크리스트

- [ ] *5가지 메시지 → 차트* 매핑을 안다.
- [ ] *축/라벨* 의 중요성을 안다.
- [ ] *colorblind-safe* 팔레트를 안다.
- [ ] *주석* 으로 *해석* 을 돕는다.

## 정리 및 다음 단계

시각화는 *분석을 결정으로 옮기는 다리* 입니다. 다음 글에서는 데이터로 *예측* 을 시도하는 *모델링* 에 들어갑니다.

<!-- toc:begin -->
- [Data Science란 무엇인가?](./01-what-is-data-science.md)
- [문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- [데이터 수집](./03-data-collection.md)
- [데이터 정제](./04-data-cleaning.md)
- [탐색적 데이터 분석](./05-exploratory-data-analysis.md)
- **시각화 (현재 글)**
- 모델링 (예정)
- 평가 (예정)
- 결과 해석 (예정)
- 데이터 프로젝트 전체 흐름 (예정)
<!-- toc:end -->

## 참고 자료

- [matplotlib — Tutorials](https://matplotlib.org/stable/tutorials/index.html)
- [seaborn — Tutorial](https://seaborn.pydata.org/tutorial.html)
- [Cole Knaflic — Storytelling with Data](https://www.storytellingwithdata.com/)
- [Tableau — Visual Best Practices](https://www.tableau.com/learn/articles/data-visualization-tips)

Tags: DataScience, Visualization, Matplotlib, Seaborn, Beginner
