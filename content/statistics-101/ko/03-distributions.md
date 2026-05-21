---
series: statistics-101
episode: 3
title: "Statistics 101 (3/10): 분포"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Statistics
  - Distribution
  - Normal
  - Skew
  - Beginner
seo_description: 정규, 균등, 지수, 멱법칙 등 자주 만나는 분포의 모양과 데이터에서 분포를 읽는 5단계 절차를 정리한 입문 글
last_reviewed: '2026-05-12'
---

# Statistics 101 (3/10): 분포

이 글은 Statistics 101 시리즈의 3번째 글입니다.

평균이 같은 두 데이터셋이 완전히 다른 행동을 보이는 경우는 흔합니다. 하나는 값이 고르게 모여 있고, 다른 하나는 일부 값이 아주 멀리 튀어 있을 수 있습니다. 숫자 하나만 같다고 데이터의 성격까지 같다고 볼 수 없는 이유가 여기에 있습니다.

통계에서 분포는 데이터가 어떤 모양으로 퍼져 있는지를 말합니다. 이 모양을 제대로 읽어야 평균, 검정, 신뢰구간, SLA 같은 모든 후속 판단이 제자리를 찾습니다.

이 글은 Statistics 101 시리즈의 3번째 글입니다. 여기서는 데이터의 모양을 읽는 기본 감각을 잡고, 정규분포를 당연한 기본값처럼 가정할 때 어떤 문제가 생기는지 정리하겠습니다.

## 먼저 던지는 질문

- 데이터의 분포 모양은 왜 중요한가요?
- 정규, 균등, 지수, 멱법칙 분포는 어떤 차이를 보일까요?
- 왜도와 첨도는 무엇을 수치로 말해 줄까요?

## 큰 그림

![Statistics 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/03/03-01-concept-at-a-glance.ko.png)

*Statistics 101 3장 흐름 개요*

분포는 데이터의 전체 모양을 한눈에 보여주는 도구입니다. 평균이 같아도 분포가 다르면 완전히 다른 이야기를 하게 됩니다.

> 분포를 이해하면 단순 요약값 너머의 데이터 성격을 정확히 읽을 수 있습니다.

## 왜 중요한가

많은 통계 기법은 분포 가정 위에서 움직입니다. 정규분포를 전제로 한 방법을 긴 꼬리 분포에 그대로 적용하면 평균, 분산, 신뢰구간, 이상치 판단이 모두 흔들릴 수 있습니다. 데이터 모양을 잘못 읽으면 계산은 맞아도 해석은 틀어집니다.

실무에서는 더 직접적입니다. 응답 시간 SLA를 평균으로 관리하면 긴 꼬리 때문에 실제 사용자 체감 문제를 놓칠 수 있고, 매출 데이터를 정규분포처럼 다루면 소수의 고액 거래가 전체 해석을 망칠 수 있습니다. 도구보다 먼저 분포를 봐야 하는 이유입니다.

## 멘탈 모델

분포를 읽는 가장 단순한 순서는 그림을 먼저 보고, 그다음 요약 통계와 분위수를 확인한 뒤, 마지막에 그 모양에 맞는 통계 도구를 선택하는 것입니다. 히스토그램은 진단의 시작점이고, 분위수는 긴 꼬리를 읽는 핵심 도구입니다.

정규분포는 대칭적인 종 모양이고, 균등분포는 값이 비슷한 빈도로 나타납니다. 지수분포와 멱법칙 분포는 한쪽 꼬리가 길며, 운영 데이터에서는 이런 형태가 더 자주 보입니다.

### 주요 분포 비교표

| 분포 | 형태 | 매개변수 | 실무 예시 |
|---|---|---|---|
| **정규분포** | 좌우 대칭 종 모양 | 평균 μ, 표준편차 σ | 시험 점수, 센서 오차, 키와 몸무게 |
| **이항분포** | 성공 횟수 막대 | 시행 수 n, 성공 확률 p | 클릭 여부, A/B 테스트 전환 |
| **포아송분포** | 단위 시간당 사건 발생 수 | 평균 발생 수 λ | 시간당 요청 수, 하루 장애 건수 |
| **균등분포** | 모든 구간이 동일한 확률 | 최솟값 a, 최댓값 b | 난수 생성, 랜덤 샘플링 |
| **지수분포** | 대기 시간, 작은 값 많음 | 비율 λ | 서버 요청 간 간격, 고객 이탈 시간 |
| **멱법칙분포** | 긴 꼬리 | 멱지수 α | 매출 분포, 조회 수, 소득 |

실무에서는 정규분포보다 긴 꼬리를 가진 분포를 훨씬 자주 만납니다. 응답 시간, 매출, 사용자 행동 로그는 대부분 멱법칙이나 지수분포 계열입니다. 정규분포를 기본값처럼 가정하면 p95, p99 같은 꼬리 지표를 놓치게 됩니다.

## 분포를 왜 알아야 하는가

분포를 모르면 평균과 분산이 같아도 완전히 다른 행동을 하는 데이터를 같은 것으로 오해할 수 있습니다. 두 데이터셋의 평균이 100이고 표준편차가 20으로 같더라도, 하나는 정규분포이고 다른 하나는 지수분포라면 극단값 발생 빈도가 전혀 다릅니다.

### 분포가 통계 기법 선택을 결정합니다

많은 통계 기법은 정규성 가정을 전제로 합니다. t-검정, ANOVA, 선형회귀 모두 잔차가 정규분포를 따른다고 가정합니다. 만약 데이터가 긴 꼬리를 가지면 이런 기법들은 신뢰구간을 잘못 계산하거나 검정력이 떨어질 수 있습니다. 그럴 때는 비모수 검정(Mann-Whitney U, Kruskal-Wallis)이나 로그 변환을 고려해야 합니다.

### 분포가 서비스수준와 알림 기준을 결정합니다

정규분포라면 평균 ± 2σ 구간에 95%가 들어가므로 평균 기준 관리가 가능합니다. 하지만 긴 꼬리 분포라면 평균은 대부분 사용자 경험을 대표하지 못하고, p95나 p99 같은 분위수 기준이 필요합니다. Datadog, Grafana, New Relic 같은 모니터링 도구가 평균보다 p95/p99를 강조하는 이유가 여기에 있습니다.

## 파이썬으로 분포 그리고 검증하기

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis, normaltest

# 긴 꼬리 분포 시뮬레이션
np.random.seed(42)
latency = np.concatenate([
    np.random.exponential(scale=100, size=950),
    np.random.exponential(scale=500, size=50)
])

# 히스토그램
plt.figure(figsize=(10, 4))
plt.hist(latency, bins=50, edgecolor="black", alpha=0.7)
plt.xlabel("Latency (ms)")
plt.ylabel("Frequency")
plt.title("응답 시간 분포 (긴 꼬리)")
plt.axvline(latency.mean(), color="red", linestyle="--", label=f"평균: {latency.mean():.1f}")
plt.axvline(np.median(latency), color="blue", linestyle="--", label=f"중앙값: {np.median(latency):.1f}")
plt.legend()
plt.show()

# 분포 요약 통계
print(f"평균: {latency.mean():.1f} ms")
print(f"중앙값: {np.median(latency):.1f} ms")
print(f"p95: {np.percentile(latency, 95):.1f} ms")
print(f"p99: {np.percentile(latency, 99):.1f} ms")
print(f"왜도: {skew(latency):.2f}")
print(f"첨도: {kurtosis(latency):.2f}")

# 정규성 검정
stat, p = normaltest(latency)
print(f"정규성 검정 p-value: {p:.4f}")
if p < 0.05:
    print("→ 정규분포가 아닙니다. 비모수 기법이나 분위수 기준을 고려하세요.")
```

왜도가 양수면 오른쪽 꼬리가 길고, 첨도가 크면 극단값이 자주 나타납니다. 정규성 검정 p-value가 0.05보다 작으면 정규분포 가정을 기각하고, t-검정 대신 Mann-Whitney U 검정을 쓰거나 로그 변환을 고려해야 합니다.
## 핵심 용어

- 정규분포: 좌우가 대칭인 종 모양 분포입니다.
- 균등분포: 각 구간이 비슷한 빈도로 나타나는 분포입니다.
- 지수분포: 대기 시간처럼 작은 값이 많고 큰 값이 드문 분포입니다.
- **멱법칙 분포**: 긴 꼬리를 가지는 분포로, 매출이나 조회 수에서 자주 보입니다.
- 왜도: 좌우 비대칭 정도입니다.
- 첨도: 꼬리 두께와 극단값 성향을 숫자로 표현한 값입니다.

## 같은 평균이어도 운영 판단은 달라진다

이전 해석: “평균 응답 시간은 200ms입니다.”

이 문장만 보면 서비스가 꽤 빠른 것처럼 보일 수 있습니다. 하지만 일부 요청이 2초 이상 걸리는 긴 꼬리 분포라면 사용자는 훨씬 나쁜 경험을 하고 있을 수 있습니다.

이후 해석: “p50은 120ms, p95는 900ms이며 긴 꼬리가 뚜렷합니다. SLA는 평균이 아니라 p95 기준으로 관리해야 합니다.”

분포를 읽기 시작하면 어떤 지표가 운영 문장을 대표해야 하는지도 함께 보입니다.

## 실습: 5단계 분포 진단

### 1단계 — 히스토그램을 그린다

```python
import matplotlib.pyplot as plt
plt.hist(latency, bins=50); plt.show()
```

분포 진단은 거의 항상 여기서 시작합니다.

### 2단계 — 기본 요약 통계를 본다

```python
import numpy as np
print(np.mean(latency), np.median(latency), np.std(latency))
```

평균과 중앙값의 차이만 봐도 비대칭 여부를 어느 정도 짐작할 수 있습니다.

### 3단계 — 분위수를 확인한다

```python
for q in [50, 90, 95, 99]:
    print(f"p{q}:", np.percentile(latency, q))
```

긴 꼬리는 분위수에서 더 또렷하게 드러납니다.

### 4단계 — 왜도와 첨도를 계산한다

```python
from scipy.stats import skew, kurtosis
print("skew:", skew(latency), "kurt:", kurtosis(latency))
```

그래프에서 본 모양을 숫자로 표현하는 단계입니다.

### 5단계 — 통계 도구를 결정한다

```text
skew=+2.3, kurt=+8 → long-tail. SLA = p95 = 900ms.
```

분포를 읽은 뒤에는 어떤 지표와 기준을 쓸지 선택해야 합니다.

## 이 코드에서 먼저 볼 점

- 히스토그램은 거의 모든 분포 진단의 출발점입니다.
- 긴 꼬리는 평균보다 분위수에서 더 잘 보입니다.
- 왜도와 첨도는 모양을 숫자로 표현해 팀 간 대화를 쉽게 만듭니다.

## 자주 헷갈리는 지점 5가지

1. **정규분포를 기본값으로 당연하게 두는 경우**: 현실 데이터는 그렇지 않을 때가 많습니다.
2. **극단값을 분포 바깥 예외로만 보는 경우**: 그 자체가 분포의 일부일 수 있습니다.
3. **긴 꼬리를 로그 스케일 없이 읽는 경우**: 꼬리 구조를 놓치기 쉽습니다.
4. **p99 대신 평균으로 SLA를 관리하는 경우**: 운영 위험을 가립니다.
5. **시각화 없이 숫자만 보는 경우**: 비대칭과 군집 구조를 놓칠 수 있습니다.

## 실무에서는 이렇게 읽습니다

응답 시간, 매출, 클릭률, 결함 빈도처럼 운영 지표는 긴 꼬리를 가지는 경우가 많습니다. 그래서 Datadog, Grafana, Sentry 같은 도구도 평균만 보여 주지 않고 p50, p95, p99를 기본으로 배치합니다. 실무 감각은 평균보다 분포의 꼬리를 먼저 보는 데서 시작합니다.

시니어 엔지니어는 분포를 보고 도구를 고릅니다. 정규성 가정을 쉽게 하지 않고, 긴 꼬리 데이터에서는 분위수와 로그 스케일을 적극적으로 씁니다. 팀이 분포를 말하기 시작하면 대시보드 숫자 하나가 훨씬 덜 오해됩니다.

## 체크리스트

- [ ] 히스토그램을 먼저 그립니다.
- [ ] p50, p95, p99를 함께 읽습니다.
- [ ] 왜도와 첨도의 의미를 설명할 수 있습니다.
- [ ] 긴 꼬리 데이터에는 분위수 기반 기준을 검토합니다.

## 연습 문제

1. 익숙한 서비스의 응답 시간 데이터를 떠올리고 히스토그램이 어떤 모양일지 그려 보세요.
2. 정규분포와 지수분포의 차이를 한 문장으로 설명해 보세요.
3. 긴 꼬리 데이터에서 평균보다 p99가 유용한 이유를 적어 보세요.

## 정리와 다음 글

분포는 데이터의 성격을 보여 주는 가장 큰 그림입니다. 평균과 분산은 분포의 일부를 요약한 값이고, 실제 해석은 모양을 읽을 때 비로소 단단해집니다. 데이터를 보기 전에 공식을 고르기보다, 데이터 모양을 먼저 보고 도구를 선택하는 습관이 중요합니다.

다음 글에서는 표본과 모집단을 다룹니다. 분포를 읽은 뒤에는 이제 일부 데이터를 보고 전체를 얼마나 말할 수 있는지가 다음 질문이 됩니다.

## 분포 진단 심화: 시각화와 검정을 함께 사용하기

분포는 그래프만으로 판단하거나 검정만으로 판단하면 오판 가능성이 커집니다. 시각화와 수치 검정을 함께 써야 안전합니다.

### 추천 진단 순서

1. 히스토그램으로 큰 모양 확인
2. 박스플롯으로 이상치와 사분위수 확인
3. 로그 스케일 히스토그램으로 꼬리 구조 확인
4. Q-Q 플롯으로 정규성 근사 확인
5. Shapiro 또는 D'Agostino 검정으로 수치 확인

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

rng = np.random.default_rng(0)
x = np.r_[rng.lognormal(mean=4.2, sigma=0.6, size=1800), rng.lognormal(mean=6.0, sigma=0.4, size=200)]

fig, ax = plt.subplots(1, 3, figsize=(15, 4))
ax[0].hist(x, bins=60, edgecolor='black')
ax[0].set_title('원본 히스토그램')

ax[1].hist(np.log(x), bins=60, edgecolor='black')
ax[1].set_title('로그 변환 히스토그램')

stats.probplot(np.log(x), dist='norm', plot=ax[2])
ax[2].set_title('로그 변환 Q-Q 플롯')
plt.tight_layout()
plt.show()

k2, p = stats.normaltest(np.log(x))
print(f"정규성 검정 p-value(로그 변환 후): {p:.4f}")
```

로그 변환 후 정규성 근사가 좋아지면 평균 기반 추정과 선형모형 적용이 더 안정적입니다. 변환 전후를 나란히 보여 주면 팀 합의가 빨라집니다.


## 실무 확장 노트: 재현 가능한 분석 문서 만들기

통계 글을 읽고 난 뒤 실제 업무에서 가장 먼저 부딪히는 문제는 "같은 분석을 다시 실행할 수 있는가"입니다. 재현 가능성이 없으면 숫자가 맞아도 신뢰를 얻기 어렵습니다. 그래서 통계 작업은 계산 코드뿐 아니라 입력 데이터 스냅샷, 버전, 시드, 가정 문장을 함께 남겨야 합니다.

### 1) 입력 데이터 스냅샷 고정

```python
import pandas as pd
from pathlib import Path

raw = pd.read_csv('analysis_input.csv')
Path('artifacts').mkdir(exist_ok=True)
raw.to_parquet('artifacts/input_snapshot.parquet', index=False)
print(raw.shape)
```

데이터 파이프라인이 바뀌면 같은 쿼리라도 다른 결과가 나올 수 있습니다. 그래서 분석 시점의 스냅샷을 남기는 습관이 중요합니다.

### 2) 전처리 규칙 문서화

```python
import numpy as np

def preprocess(df):
    out = df.copy()
    out = out.dropna(subset=['metric'])
    out = out[(out['metric'] >= 0) & (out['metric'] <= out['metric'].quantile(0.999))]
    out['segment'] = out['segment'].fillna('unknown')
    return out
```

이상치 제거, 결측값 처리, 세그먼트 매핑은 결과를 크게 바꿉니다. 코드와 문서를 동시에 남겨야 이후 검토에서 혼선을 줄일 수 있습니다.

### 3) 분포 진단 + 추정 + 검정을 한 화면에서 보고하기

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

x = np.random.default_rng(0).normal(100, 15, 600)
y = np.random.default_rng(1).normal(103, 15, 600)

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].hist(x, bins=40, alpha=0.6, label='A')
ax[0].hist(y, bins=40, alpha=0.6, label='B')
ax[0].legend(); ax[0].set_title('분포 비교')

ax[1].boxplot([x, y], labels=['A', 'B'])
ax[1].set_title('사분위수 비교')
plt.tight_layout(); plt.show()

diff = y.mean() - x.mean()
se = np.sqrt(x.var(ddof=1)/len(x) + y.var(ddof=1)/len(y))
ci = (diff - 1.96*se, diff + 1.96*se)
t, p = stats.ttest_ind(x, y, equal_var=False)
print(f'diff={diff:.3f}, 95% CI={ci}, p={p:.4f}')
```

그래프와 수치를 분리하면 오해가 늘어납니다. 같은 섹션에서 함께 보여 주면 해석 품질이 올라갑니다.

### 4) 효과 크기와 실행 기준 연결

```python
pooled = np.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2)
cohens_d = (y.mean() - x.mean()) / pooled
print(f"Cohen's d={cohens_d:.3f}")
```

p-value가 작아도 효과 크기가 매우 작다면 실행 우선순위가 낮을 수 있습니다. 반대로 p-value 경계선이더라도 효과 크기와 비용 구조가 유리하면 추가 실험으로 이어갈 가치가 있습니다.

### 5) 결과 문장 표준화

분석 결과는 다음 형식으로 정리하면 팀 의사결정이 빨라집니다.

- 관찰 차이: 절대값과 상대값을 모두 표기합니다.
- 불확실성: 95% 신뢰구간과 표본 수를 함께 표기합니다.
- 유의성: 검정 방법과 p-value를 표기합니다.
- 실행 판단: 배포/보류/추가실험 중 하나를 명시합니다.

통계는 결국 팀의 공통 언어를 만드는 일입니다. 재현 가능한 분석 문서를 남기면 개인의 직관이 아니라 조직의 기준으로 의사결정을 반복할 수 있습니다.


## 추가 메모: 검증 가능한 의사결정 문장

분석 결과를 보고할 때는 "좋아 보입니다" 같은 모호한 문장을 피하고, 기준과 근거를 한 줄에 함께 적는 것이 좋습니다. 예를 들어 "전환율 +0.6%p, 95% 신뢰구간 +0.1~+1.1%p, p=0.014, 월간 기대효과 +320건, 2주 재검증 조건부 배포"처럼 쓰면 의사결정 책임이 명확해집니다. 이런 형식은 통계 도구가 바뀌어도 유지되는 팀 자산입니다.


## 실무 확장 노트: 재현 가능한 분석 문서 만들기

통계 글을 읽고 난 뒤 실제 업무에서 가장 먼저 부딪히는 문제는 "같은 분석을 다시 실행할 수 있는가"입니다. 재현 가능성이 없으면 숫자가 맞아도 신뢰를 얻기 어렵습니다. 그래서 통계 작업은 계산 코드뿐 아니라 입력 데이터 스냅샷, 버전, 시드, 가정 문장을 함께 남겨야 합니다.

### 1) 입력 데이터 스냅샷 고정

```python
import pandas as pd
from pathlib import Path

raw = pd.read_csv('analysis_input.csv')
Path('artifacts').mkdir(exist_ok=True)
raw.to_parquet('artifacts/input_snapshot.parquet', index=False)
print(raw.shape)
```

데이터 파이프라인이 바뀌면 같은 쿼리라도 다른 결과가 나올 수 있습니다. 그래서 분석 시점의 스냅샷을 남기는 습관이 중요합니다.

### 2) 전처리 규칙 문서화

```python
import numpy as np

def preprocess(df):
    out = df.copy()
    out = out.dropna(subset=['metric'])
    out = out[(out['metric'] >= 0) & (out['metric'] <= out['metric'].quantile(0.999))]
    out['segment'] = out['segment'].fillna('unknown')
    return out
```

이상치 제거, 결측값 처리, 세그먼트 매핑은 결과를 크게 바꿉니다. 코드와 문서를 동시에 남겨야 이후 검토에서 혼선을 줄일 수 있습니다.

### 3) 분포 진단 + 추정 + 검정을 한 화면에서 보고하기

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

x = np.random.default_rng(0).normal(100, 15, 600)
y = np.random.default_rng(1).normal(103, 15, 600)

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].hist(x, bins=40, alpha=0.6, label='A')
ax[0].hist(y, bins=40, alpha=0.6, label='B')
ax[0].legend(); ax[0].set_title('분포 비교')

ax[1].boxplot([x, y], labels=['A', 'B'])
ax[1].set_title('사분위수 비교')
plt.tight_layout(); plt.show()

diff = y.mean() - x.mean()
se = np.sqrt(x.var(ddof=1)/len(x) + y.var(ddof=1)/len(y))
ci = (diff - 1.96*se, diff + 1.96*se)
t, p = stats.ttest_ind(x, y, equal_var=False)
print(f'diff={diff:.3f}, 95% CI={ci}, p={p:.4f}')
```

그래프와 수치를 분리하면 오해가 늘어납니다. 같은 섹션에서 함께 보여 주면 해석 품질이 올라갑니다.

### 4) 효과 크기와 실행 기준 연결

```python
pooled = np.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2)
cohens_d = (y.mean() - x.mean()) / pooled
print(f"Cohen's d={cohens_d:.3f}")
```

p-value가 작아도 효과 크기가 매우 작다면 실행 우선순위가 낮을 수 있습니다. 반대로 p-value 경계선이더라도 효과 크기와 비용 구조가 유리하면 추가 실험으로 이어갈 가치가 있습니다.

### 5) 결과 문장 표준화

분석 결과는 다음 형식으로 정리하면 팀 의사결정이 빨라집니다.

- 관찰 차이: 절대값과 상대값을 모두 표기합니다.
- 불확실성: 95% 신뢰구간과 표본 수를 함께 표기합니다.
- 유의성: 검정 방법과 p-value를 표기합니다.
- 실행 판단: 배포/보류/추가실험 중 하나를 명시합니다.

통계는 결국 팀의 공통 언어를 만드는 일입니다. 재현 가능한 분석 문서를 남기면 개인의 직관이 아니라 조직의 기준으로 의사결정을 반복할 수 있습니다.


## 처음 질문으로 돌아가기

- **데이터의 분포 모양은 왜 중요한가요?**
  - 히스토그램, boxplot, QQ plot으로 데이터 모양을 다각도로 확인합니다.
- **정규, 균등, 지수, 멱법칙 분포는 어떤 차이를 보일까요?**
  - 분포를 알면 같은 평균에서도 왜 다른 행동이 나오는지 설명할 수 있습니다.
- **왜도와 첨도는 무엇을 수치로 말해 줄까요?**
  - 이상한 분포는 데이터 수집 오류를 알리므로 운영에서는 자동 알림 기준이 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Statistics 101 (1/10): 통계란 무엇인가?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): 평균, 중앙값, 분산](./02-mean-median-variance.md)
- **분포 (현재 글)**
- 표본과 모집단 (예정)
- 추정 (예정)
- 신뢰구간 (예정)
- 가설검정 (예정)
- 상관과 회귀 (예정)
- p-value 이해하기 (예정)
- 통계적 사고방식 (예정)

<!-- toc:end -->

## 참고 자료

- [SciPy — Statistical Distributions](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Khan Academy — Distributions](https://www.khanacademy.org/math/statistics-probability/random-variables-stats-library)
- [Wikipedia — Power Law](https://en.wikipedia.org/wiki/Power_law)
- [Brendan Gregg — Latency Distributions](https://www.brendangregg.com/blog/2014-06-23/latency-heat-maps.html)

### 큐큐 플롯으로 정규성 진단하기

Q-Q plot(Quantile-Quantile plot)은 데이터의 분위수와 이론적 정규분포의 분위수를 비교하는 그래프입니다. 데이터가 정규분포를 따르면 점들이 대각선 위에 일직선으로 놓입니다.

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# 정규분포 vs 지수분포
np.random.seed(42)
normal_data = np.random.normal(loc=100, scale=20, size=500)
exp_data = np.random.exponential(scale=100, size=500)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 정규분포 Q-Q plot
stats.probplot(normal_data, dist="norm", plot=axes[0])
axes[0].set_title("정규분포 Q-Q Plot")

# 지수분포 Q-Q plot
stats.probplot(exp_data, dist="norm", plot=axes[1])
axes[1].set_title("지수분포 Q-Q Plot (정규 기준)")

plt.tight_layout()
plt.show()
```

정규분포 데이터는 점들이 직선에 가깝게 놓이지만, 지수분포 데이터는 오른쪽 끝이 위로 휘어집니다. 이는 오른쪽 꼬리가 정규분포보다 길다는 뜻입니다.

### 로그 변환으로 긴 꼬리 다루기

긴 꼬리 분포는 로그 변환을 하면 정규분포에 가까워지는 경우가 많습니다. 특히 매출, 소득, 응답 시간처럼 양수이면서 극단값이 있는 데이터에서 유용합니다.

```python
import numpy as np
import matplotlib.pyplot as plt

# 긴 꼬리 데이터 (로그정규분포)
np.random.seed(42)
data = np.random.lognormal(mean=4, sigma=1, size=1000)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# 원본 분포
axes[0].hist(data, bins=50, edgecolor="black")
axes[0].set_title("원본 분포 (긴 꼬리)")
axes[0].set_xlabel("값")

# 로그 변환 후
axes[1].hist(np.log(data), bins=50, edgecolor="black")
axes[1].set_title("로그 변환 후 (정규에 가까움)")
axes[1].set_xlabel("log(값)")

plt.tight_layout()
plt.show()

print(f"원본 평균: {data.mean():.1f}, 중앙값: {np.median(data):.1f}")
print(f"로그 변환 후 평균: {np.log(data).mean():.2f}, 중앙값: {np.median(np.log(data)):.2f}")
```

로그 변환 후에는 평균과 중앙값이 가까워지고 히스토그램도 대칭에 가까워집니다. 이렇게 변환한 뒤 t-검정이나 회귀분석을 적용하면 정규성 가정을 만족하기 쉬워집니다.

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/statistics-101/ko)

Tags: Statistics, Distribution, Normal, Skew, Beginner
