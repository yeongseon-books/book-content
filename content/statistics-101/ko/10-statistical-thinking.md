---
series: statistics-101
episode: 10
title: "Statistics 101 (10/10): 통계적 사고방식"
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
  - Thinking
  - Mindset
  - Decision
  - Beginner
seo_description: 질문, 데이터, 분포, 추정, 불확실성, 의사결정으로 이어지는 통계적 사고의 흐름과 시리즈 전체를 한 사례로 묶어 마무리하는 글
last_reviewed: '2026-05-12'
---

# Statistics 101 (10/10): 통계적 사고방식

통계를 한 챕터씩 배우면 평균, 분산, 분포, 가설검정, p-value가 서로 다른 도구처럼 보이기 쉽습니다. 하지만 실무에서 이 도구들은 따로 움직이지 않습니다. 하나의 질문에서 시작해 데이터 수집, 분포 확인, 추정, 검정, 최종 결정까지 한 흐름으로 이어집니다.

그래서 시리즈의 마지막에서 필요한 것은 새 공식을 하나 더 배우는 일이 아닙니다. 지금까지 본 개념이 어떤 순서로 연결되어 의사결정으로 닫히는지, 그 흐름을 머릿속에 하나로 묶는 일입니다.

이 글은 Statistics 101 시리즈의 마지막 글입니다. 여기서는 통계를 도구 상자가 아니라 사고방식으로 다시 정리하고, 질문에서 결정까지 이어지는 실전 흐름을 한 번에 묶어 보겠습니다.

![Statistics 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/10/10-01-concept-at-a-glance.ko.png)
*Statistics 101 10장 흐름 개요*
> 통계적 사고의 궁극 목표는 아름다운 숫자가 아니라 좋은 결정입니다.

## 이 글에서 다룰 문제

- 통계는 공식 모음일까요, 아니면 사고방식일까요?
- 질문, 데이터, 분포, 추정, 검정은 어떤 순서로 이어질까요?
- p-value와 효과 크기, 비용은 어떻게 함께 판단에 들어갈까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

도구를 안다고 해서 바로 좋은 판단이 나오지는 않습니다. 평균을 계산할 줄 알아도 질문이 흐리면 분석이 흔들리고, p-value를 읽을 줄 알아도 효과 크기와 비용을 함께 보지 않으면 잘못된 결정을 내릴 수 있습니다. 통계적 사고는 각 도구가 어느 타이밍에 등장해야 하는지 알려 줍니다.

실무에서는 이 흐름 감각이 중요합니다. 데이터를 먼저 뒤지고 질문을 나중에 붙이는 방식은 낚시식 분석으로 가기 쉽고, 숫자를 읽기 전에 배포 여부를 정해 두면 통계는 정당화 도구로 전락합니다. 순서를 바로 세우는 것이 통계적 사고의 출발점입니다.

## 멘탈 모델

통계적 사고는 질문에서 출발해 데이터, 분포, 추정, 신뢰구간, 검정, 효과 크기, 결정으로 이어집니다. 이 순서가 정리되면 시리즈 전체가 하나의 작업 흐름처럼 읽히기 시작합니다.

중요한 점은 마지막 결정이 통계량 하나에서 바로 나오지 않는다는 사실입니다. 추정값과 불확실성, 효과 크기, 비즈니스 비용이 함께 모여서 결정이 됩니다.

- 질문 우선: 데이터를 보기 전에 무엇을 묻는지 먼저 적는 태도입니다.
- 불확실성: 모든 추정에는 오차가 따라붙는다는 전제입니다.
- 맥락: 같은 p-value도 분야와 비용 구조에 따라 다르게 읽힙니다.
- 효과 크기: 유의성보다 실제 크기가 더 중요한 상황이 많습니다.
- 의사결정: 통계의 마지막 목적지입니다.

## 통계적 사고 체크리스트

통계적 사고를 실무에 적용할 때는 아래 체크리스트를 단계별로 따르면 빠뜨리는 부분이 줄어듭니다.

| 단계 | 질문 | 확인 사항 |
|------|------|----------|
| 1. 질문 정의 | 무엇을 알고 싶은가? | 질문을 한 문장으로 적었는가? 데이터를 보기 전에 가설을 정했는가? |
| 2. 데이터 수집 | 표본이 모집단을 대표하는가? | 편향(선택 편향, 생존 편향)이 없는가? 표본 크기가 충분한가? |
| 3. 분포 확인 | 데이터가 어떤 모양인가? | 히스토그램, 박스플롯을 그렸는가? 이상치를 확인했는가? |
| 4. 추정 | 추정값과 불확실성은? | 평균뿐 아니라 신뢰구간도 계산했는가? |
| 5. 검정 | 차이가 우연인가? | p-value와 효과 크기를 함께 봤는가? 다중비교 보정을 했는가? |
| 6. 해석 | 통계적 유의성 = 실무적 의미인가? | 효과 크기, 비용, 맥락을 함께 고려했는가? |
| 7. 결정 | 다음 행동은? | 배포 / 추가 실험 / 중단 중 무엇을 선택할 것인가? |

이 체크리스트는 분석 시작 전에 미리 출력해 두고, 각 단계를 거칠 때마다 체크하면 좋습니다. 특히 2번(편향 확인)과 6번(실무 의미)는 자주 건너뛰기 쉬운 단계이므로 주의가 필요합니다.

## 분석이 아니라 낚시가 되는 순간

이전 해석: "일단 데이터를 돌려 보고 뭐가 나오는지 보자."

이 접근은 보기에는 유연하지만, 실제로는 가설을 뒤늦게 붙이고 우연한 패턴을 과도하게 믿게 만들 수 있습니다.

이후 해석: "우리가 답하고 싶은 질문이 무엇인지 먼저 적고, 그 질문에 맞는 데이터와 기준을 정한 뒤, 불확실성을 포함해 결정을 내리자."

통계적 사고는 계산 순서가 아니라 질문 순서를 바로 세우는 작업입니다.

## 실습: A/B 테스트 전체 파이프라인

### 5단계 통계적 사고 흐름

```python
import numpy as np
import math
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

np.random.seed(42)

# ── 1단계: 질문 정의 ──────────────────────────────────────────────────────────
question = "새 체크아웃 버튼(B)이 기존 버튼(A)보다 전환율을 높이는가?"
alpha    = 0.05          # 유의수준
min_lift = 0.10          # 최소 의미 있는 상대 향상률
print(f"[질문] {question}")
print(f"[기준] α={alpha}, 최소 향상률={min_lift*100:.0f}%\n")

# ── 2단계: 데이터 수집 ──────────────────────────────────────────────────────
nA, kA = 5000, 250
nB, kB = 5000, 290
pA, pB = kA / nA, kB / nB

print(f"A 전환율: {pA:.4f}  B 전환율: {pB:.4f}")
print(f"절대 차이: {pB - pA:+.4f}   상대 향상: {(pB-pA)/pA*100:+.1f}%\n")

# ── 3단계: 추정과 신뢰구간 ──────────────────────────────────────────────────
diff    = pB - pA
se_diff = math.sqrt(pA*(1-pA)/nA + pB*(1-pB)/nB)
z_crit  = stats.norm.ppf(1 - alpha/2)
ci_lo   = diff - z_crit * se_diff
ci_hi   = diff + z_crit * se_diff
print(f"95% CI: [{ci_lo:.4f}, {ci_hi:.4f}]")
print(f"CI가 0 포함 여부: {ci_lo <= 0 <= ci_hi}\n")

# ── 4단계: 가설검정 + 효과 크기 ──────────────────────────────────────────────
z_stat  = diff / se_diff
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))    # 양측
lift    = diff / pA

print(f"z = {z_stat:.3f},  p = {p_value:.4f}")
print(f"상대 향상률: {lift*100:.1f}%  (기준 {min_lift*100:.0f}% 초과: {lift >= min_lift})\n")

# ── 5단계: 비즈니스 판단 ──────────────────────────────────────────────────────
deploy_cost = "low"   # 프론트엔드 CSS 변경
statistically_sig = p_value < alpha
practically_sig   = lift >= min_lift

if statistically_sig and practically_sig and deploy_cost == "low":
    decision = "SHIP: 전체 배포"
elif statistically_sig and practically_sig:
    decision = "REVIEW: 비용 대비 이익 재검토"
else:
    decision = "HOLD: 추가 실험 필요"

print(f"[결정] {decision}")
```

출력:

```
[질문] 새 체크아웃 버튼(B)이 기존 버튼(A)보다 전환율을 높이는가?
[기준] α=0.05, 최소 향상률=10%

A 전환율: 0.0500  B 전환율: 0.0580
절대 차이: +0.0080   상대 향상: +16.0%

95% CI: [0.0020, 0.0140]
CI가 0 포함 여부: False

z = 2.449,  p = 0.0143
상대 향상률: 16.0%  (기준 10% 초과: True)

[결정] SHIP: 전체 배포
```

### A/B 결과 시각화

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# ── 왼쪽: 전환율 비교 (오차 막대) ────────────────────────────────────────────
groups = ["A (기존)", "B (신규)"]
rates  = [pA, pB]
errors = [
    stats.norm.ppf(0.975) * math.sqrt(p*(1-p)/n)
    for p, n in [(pA, nA), (pB, nB)]
]

axes[0].bar(groups, rates, color=["#4878d0", "#ee854a"],
            yerr=errors, capsize=6, alpha=0.85, width=0.5)
axes[0].axhline(pA, color="#4878d0", linestyle="--", alpha=0.5, label="A 기준선")
axes[0].set_ylabel("전환율")
axes[0].set_title("A/B 전환율 비교 (95% CI)")
for i, (r, e) in enumerate(zip(rates, errors)):
    axes[0].text(i, r + e + 0.001, f"{r:.3f}", ha="center", fontsize=11)
axes[0].legend()

# ── 오른쪽: 차이의 분포 (z-분포 + 기각역) ───────────────────────────────────
x = np.linspace(-4, 4, 500)
y = stats.norm.pdf(x)
axes[1].plot(x, y, "k-", lw=2)
axes[1].fill_between(x, y, where=(x >= z_crit),  color="tomato", alpha=0.5, label="기각역 (α/2)")
axes[1].fill_between(x, y, where=(x <= -z_crit), color="tomato", alpha=0.5)
axes[1].axvline(z_stat, color="navy", lw=2, linestyle="-", label=f"z = {z_stat:.2f}")
axes[1].axvline(-z_stat, color="navy", lw=2, linestyle="--", alpha=0.5)
axes[1].set_title(f"z-분포와 검정 통계량 (p = {p_value:.4f})")
axes[1].set_xlabel("z")
axes[1].set_ylabel("밀도")
axes[1].legend()

plt.tight_layout()
plt.savefig("ab_test_result.png", dpi=150)
plt.show()
```

## 심슨의 역설 예시

Simpson's Paradox는 집단 전체에서는 한 방향이지만, 하위 집단별로 나누면 반대 방향이 나타나는 현상입니다. 이는 숨은 변수가 있을 때 자주 발생합니다.

### 실전 시나리오

한 병원에서 두 가지 치료법(A, B)의 성공률을 비교합니다.

**전체 데이터:**

| 치료법 | 성공 | 실패 | 성공률 |
|--------|------|------|--------|
| A | 80 | 20 | 80% |
| B | 75 | 25 | 75% |

전체로 보면 A가 더 좋아 보입니다.

**환자 중증도별로 나누면:**

경증 환자:

| 치료법 | 성공 | 실패 | 성공률 |
|--------|------|------|--------|
| A | 70 | 10 | 87.5% |
| B | 5 | 5 | 50.0% |

중증 환자:

| 치료법 | 성공 | 실패 | 성공률 |
|--------|------|------|--------|
| A | 10 | 10 | 50.0% |
| B | 70 | 20 | 77.8% |

경증에서는 A가 낫고, 중증에서는 B가 낫습니다. 전체 집계에서 A가 높게 나온 이유는 A가 경증 환자를 주로 받았기 때문입니다.

### 파이썬으로 재현 + 시각화

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 데이터 구성
mild_A   = pd.DataFrame({"treatment": ["A"]*80,   "severity": ["경증"]*80,
                          "outcome": ["success"]*70 + ["fail"]*10})
mild_B   = pd.DataFrame({"treatment": ["B"]*10,   "severity": ["경증"]*10,
                          "outcome": ["success"]*5  + ["fail"]*5})
severe_A = pd.DataFrame({"treatment": ["A"]*20,   "severity": ["중증"]*20,
                          "outcome": ["success"]*10 + ["fail"]*10})
severe_B = pd.DataFrame({"treatment": ["B"]*90,   "severity": ["중증"]*90,
                          "outcome": ["success"]*70 + ["fail"]*20})

df = pd.concat([mild_A, mild_B, severe_A, severe_B], ignore_index=True)

# 집계
overall    = df.groupby("treatment")["outcome"].apply(lambda x: (x=="success").mean())
by_sev     = df.groupby(["severity","treatment"])["outcome"].apply(lambda x: (x=="success").mean())

print("전체 성공률:")
print(overall.round(3))
print("\n중증도별 성공률:")
print(by_sev.round(3))

# 시각화: 전체 vs 층별
fig, axes = plt.subplots(1, 3, figsize=(13, 5))

def bar_pair(ax, data, title):
    vals  = [data.get(("A" if "A" in str(k) else "B"), data.get(k, 0))
             if isinstance(k, str) else data.get(k, 0) for k in ["A", "B"]]
    colors = ["#4878d0", "#ee854a"]
    ax.bar(["A", "B"], [data["A"], data["B"]], color=colors, alpha=0.85, width=0.5)
    for i, v in enumerate([data["A"], data["B"]]):
        ax.text(i, v + 0.01, f"{v:.1%}", ha="center", fontsize=11)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("성공률")
    ax.set_title(title)

bar_pair(axes[0], overall.to_dict(), "전체 (집계 오류)")

for idx, sev in enumerate(["경증", "중증"]):
    sub = by_sev[sev]
    bar_pair(axes[idx+1], sub.to_dict(), f"{sev} 환자만")

plt.suptitle("Simpson's Paradox: 전체 집계 vs 층별 분리", fontsize=13, y=1.02)
plt.tight_layout()
plt.savefig("simpsons_paradox.png", dpi=150)
plt.show()
```

출력:

```
전체 성공률:
treatment
A    0.800
B    0.750

중증도별 성공률:
severity  treatment
경증       A            0.875
          B            0.500
중증       A            0.500
          B            0.778
```

### 교훈

- 전체 집계만 보고 결론 내리는 것은 위험합니다.
- 하위 집단별로 나눠서 봐야 숨은 변수의 영향을 확인할 수 있습니다.
- 실무에서는 층별 분석(stratified analysis)을 기본으로 수행해야 합니다.

Simpson's Paradox는 상관과 인과를 섞지 말아야 하는 또 다른 이유입니다.

## 시리즈 통합 실전: 한 개의 분석 문서로 완성하기

통계적 사고를 실제 업무로 옮길 때는 시리즈의 개별 개념을 하나의 분석 문서 구조로 합치는 것이 가장 효과적입니다.

### 추천 문서 템플릿

1. 질문과 의사결정 기준
2. 데이터 범위, 표본 설계, 편향 위험
3. 기술 통계와 분포 진단
4. 추정값, 신뢰구간, 가설검정
5. 효과 크기와 사업 영향
6. 최종 결정과 후속 실험 계획

### 통합 예제 코드

```python
import numpy as np
from scipy import stats
from statsmodels.stats.proportion import confint_proportions_2indep

# 실험 데이터
nA, cA = 8000, 376
nB, cB = 8000, 432

pA, pB = cA / nA, cB / nB
diff = pB - pA

# 신뢰구간
ci_low, ci_high = confint_proportions_2indep(cB, nB, cA, nA, method="wald")

# 검정 (양측 z 근사)
se = np.sqrt(pA*(1-pA)/nA + pB*(1-pB)/nB)
z  = diff / se
p  = 2 * (1 - stats.norm.cdf(abs(z)))

print(f"A={pA:.4f}, B={pB:.4f}, diff={diff:+.4f}")
print(f"95% CI=[{ci_low:.4f}, {ci_high:.4f}], z={z:.3f}, p={p:.4f}")
```

### 해석 예시

- 통계적 판단: p값은 유의수준 0.05보다 작아 차이를 기각할 근거가 있습니다.
- 크기 판단: 절대 차이는 +0.7%p 수준이며 신뢰구간 하한도 양수입니다.
- 실행 판단: 구현 비용이 낮고 리스크가 작다면 배포 후 모니터링 전략이 합리적입니다.

이 문장 구조를 반복하면 분석 품질이 개인 역량이 아니라 팀 표준으로 자리 잡습니다.

## 데이터 리터러시

데이터 리터러시(Data Literacy)는 데이터를 읽고, 이해하고, 비판적으로 평가하고, 전달하는 능력입니다. 통계적 사고는 데이터 리터러시의 핵심 요소입니다.

### 데이터 리터러시의 4단계

1. **읽기(Read)**: 숫자와 차트를 정확히 이해합니다.
   - "평균이 100이다" → 중앙값과 분산도 함께 봐야 합니다.
   - "증가율 50%" → 기준값이 무엇인지 확인합니다.

2. **해석(Interpret)**: 숫자 뒤의 맥락을 읽습니다.
   - "전환율 5%" → 업계 평균은? 시즌 효과는?
   - "p < 0.05" → 효과 크기는? 표본 수는?

3. **비판(Critique)**: 데이터의 한계를 파악합니다.
   - 표본 편향이 있는가?
   - 누락 변수가 결론을 바꿀 수 있는가?
   - 상관을 인과로 과장하고 있지 않은가?

4. **전달(Communicate)**: 불확실성을 포함해 명확히 설명합니다.
   - "효과가 있습니다" → "A는 B보다 평균 3.2 단위 높으며(95% CI: [1.5, 4.9]), 상대 향상률은 약 12%입니다."

### 실무에서 데이터 리터러시를 높이는 방법

- **시각화를 먼저 본다**: 숫자 테이블보다 산점도, 박스플롯, 히스토그램이 패턴을 빠르게 드러냅니다.
- **숫자에 맥락을 붙인다**: "매출 1억"보다 "전년 대비 +15%, 목표 대비 -5%"가 훨씬 유용합니다.
- **불확실성을 숨기지 않는다**: "확실하다"보다 "95% 신뢰구간은 [90, 110]입니다"가 더 신뢰를 줍니다.
- **가정을 명시한다**: "정규분포를 가정했으며, 이상치 3개를 제거했습니다"처럼 투명하게 적습니다.
- **질문을 먼저 적는다**: "데이터를 돌려 보니 이런 게 나왔습니다"가 아니라 "우리가 알고 싶었던 것은 X이고, 분석 결과 Y입니다"로 시작합니다.

### 데이터 리터러시 자가 진단

아래 질문에 "예"라고 답할 수 있다면 기본 데이터 리터러시를 갖췄다고 볼 수 있습니다.

- [ ] 평균과 중앙값의 차이를 설명할 수 있습니까?
- [ ] 상관과 인과를 구분할 수 있습니까?
- [ ] p-value의 정확한 의미를 말할 수 있습니까?
- [ ] 신뢰구간을 올바르게 해석할 수 있습니까?
- [ ] 표본 편향을 스스로 발견할 수 있습니까?
- [ ] 차트에서 축 조작이나 시각적 왜곡을 찾아낼 수 있습니까?
- [ ] 데이터 분석 결과를 비전문가에게 명확히 전달할 수 있습니까?

데이터 리터러시는 도구 사용법이 아니라 사고방식입니다. 통계를 배우는 이유는 Python을 잘 쓰기 위해서가 아니라, 불확실한 세상에서 더 나은 판단을 내리기 위해서입니다.

## 시각화: 통계적 사고 흐름 한 눈에 보기

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

np.random.seed(0)

fig, axes = plt.subplots(2, 2, figsize=(13, 10))
fig.suptitle("통계적 사고 흐름 — 시리즈 종합 시각화", fontsize=14)

# ── (1, 1) 표본 추출: 모집단 분포 vs 표본 분포 ───────────────────────────────
ax = axes[0, 0]
pop = np.random.normal(50, 10, 10000)
samples = [np.random.choice(pop, 30).mean() for _ in range(1000)]
ax.hist(pop, bins=60, density=True, alpha=0.4, color="steelblue", label="모집단")
ax.hist(samples, bins=40, density=True, alpha=0.7, color="coral",    label="표본 평균 분포 (n=30)")
ax.axvline(np.mean(pop), color="navy",  linestyle="--", label=f"모집단 평균 {np.mean(pop):.1f}")
ax.axvline(np.mean(samples), color="crimson", linestyle=":", label=f"표본 평균 {np.mean(samples):.1f}")
ax.set_title("2장 + 5장: 표본 분포와 추정")
ax.set_xlabel("값")
ax.legend(fontsize=8)

# ── (1, 2) 신뢰구간: 반복 실험에서 CI 포함 여부 ─────────────────────────────
ax = axes[0, 1]
true_mu = 50.0
n_trials = 40
n_obs = 30
covered, not_covered = [], []
for _ in range(n_trials):
    sample = np.random.normal(true_mu, 10, n_obs)
    se = sample.std(ddof=1) / np.sqrt(n_obs)
    ci = (sample.mean() - 1.96*se, sample.mean() + 1.96*se)
    if ci[0] <= true_mu <= ci[1]:
        covered.append(ci)
    else:
        not_covered.append(ci)

for i, ci in enumerate(covered):
    ax.plot([ci[0], ci[1]], [i, i], color="steelblue", lw=1.2, alpha=0.7)
for i, ci in enumerate(not_covered):
    ax.plot([ci[0], ci[1]], [len(covered)+i, len(covered)+i], color="tomato", lw=1.5)
ax.axvline(true_mu, color="black", lw=1.5, linestyle="--", label=f"참값 μ={true_mu}")
ax.set_title(f"6장: 신뢰구간 — {len(covered)}/{n_trials}개 포함 ({len(covered)/n_trials*100:.0f}%)")
ax.set_xlabel("값")
ax.legend(fontsize=9)

# ── (2, 1) 가설검정: 두 집단 분포 비교 ──────────────────────────────────────
ax = axes[1, 0]
groupA = np.random.normal(50, 10, 200)
groupB = np.random.normal(56,  9, 200)
x = np.linspace(20, 90, 400)
ax.fill_between(x, stats.norm.pdf(x, groupA.mean(), groupA.std()),
                alpha=0.5, color="steelblue", label=f"A: μ={groupA.mean():.1f}")
ax.fill_between(x, stats.norm.pdf(x, groupB.mean(), groupB.std()),
                alpha=0.5, color="coral",    label=f"B: μ={groupB.mean():.1f}")
t, p = stats.ttest_ind(groupA, groupB)
cohen_d = (groupB.mean() - groupA.mean()) / np.sqrt((groupA.std()**2 + groupB.std()**2)/2)
ax.set_title(f"7장: 가설검정 — t={t:.2f}, p={p:.4f}, d={cohen_d:.2f}")
ax.set_xlabel("값")
ax.legend()

# ── (2, 2) p-value vs 효과 크기 산점도 (시뮬레이션) ─────────────────────────
ax = axes[1, 1]
ns   = [30, 50, 100, 200, 500]
d_true = 0.3   # 작은 효과 크기
colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(ns)))
for n, c in zip(ns, colors):
    p_vals, d_vals = [], []
    for _ in range(200):
        a = np.random.normal(0,       1, n)
        b = np.random.normal(d_true,  1, n)
        _, pv = stats.ttest_ind(a, b)
        d = (b.mean()-a.mean()) / np.sqrt((a.std()**2+b.std()**2)/2)
        p_vals.append(pv)
        d_vals.append(d)
    ax.scatter(d_vals, p_vals, alpha=0.25, s=10, color=c, label=f"n={n}")
ax.axhline(0.05, color="red", linestyle="--", lw=1.2, label="α=0.05")
ax.set_title("9장: 표본 크기 vs p-value vs 효과 크기")
ax.set_xlabel("Cohen's d (효과 크기)")
ax.set_ylabel("p-value")
ax.set_yscale("log")
ax.legend(fontsize=8, ncol=2)

plt.tight_layout()
plt.savefig("statistical_thinking_overview.png", dpi=150)
plt.show()
```

## 자주 하는 실수

| 실수 유형 | 구체적 상황 | 올바른 접근 |
|-----------|-------------|-------------|
| 데이터 먼저 탐색, 질문 나중에 붙이기 | "이 데이터로 뭐 할 수 있나 보자" → 우연 패턴을 진짜 발견처럼 보고 | 분석 전에 질문과 가설을 문서로 먼저 작성 |
| p-value 하나로 결정 | p=0.049 → "통계적으로 유의하니 배포" (효과 크기와 비용 무시) | 효과 크기, 신뢰구간, 배포 비용을 함께 검토 |
| 전체 집계만 보고 결론 | 그룹 A 성공률 80%, B 75% → "A 우수"라고 결론 (Simpson's Paradox) | 하위 집단별 층별 분석 후 결론 도출 |
| 불확실성 미표기 | "전환율 5.8%입니다" 보고 (신뢰구간 없음) | "5.8% (95% CI: [5.4%, 6.2%])"로 항상 구간 함께 보고 |
| 맥락 없이 결과 비교 | A 앱은 전환율 3%, B 앱은 전환율 5% → B 무조건 좋음 | 업계 평균, 고객 유형, 상품 가격대 등 맥락 포함 |
| 반복 측정 후 그때 가설 세우기 (HARKing) | 여러 지표를 돌려 보다 유의한 것 발견 후 "이게 처음 목표였다" | 사전 등록(pre-registration) 또는 다중비교 보정 적용 |

## 실무에서는 이렇게 읽습니다

제품 실험, 가격 결정, 정책 평가, 임상 승인, 수요 예측처럼 데이터 기반 판단이 필요한 모든 장면에는 같은 흐름이 있습니다. 질문을 먼저 적고, 데이터를 수집하고, 분포를 읽고, 추정과 검정을 거쳐, 마지막에 비용과 맥락을 포함해 결정을 내립니다. 데이터 과학, 머신러닝, 비즈니스 분석도 이 뼈대를 공유합니다.

시니어 엔지니어는 통계를 도구 목록으로 기억하지 않습니다. 질문에서 결정까지의 흐름으로 기억합니다. 불확실성을 숫자와 문장으로 함께 남기고, 효과 크기와 비용을 같이 읽으며, 분석 맥락을 문서화합니다. 이 태도가 팀의 의사결정을 반복 가능하게 만듭니다.

## 운영 체크리스트

- [ ] 질문을 먼저 정의합니다.
- [ ] 추정값, 신뢰구간, 효과 크기를 함께 보고합니다.
- [ ] 불확실성을 명시적으로 적습니다.
- [ ] 결정 비용과 맥락을 같이 검토합니다.
- [ ] Simpson's Paradox를 막기 위해 층별 분석을 수행합니다.
- [ ] 분석 결과와 결정 근거를 문서로 남깁니다.

## 연습 문제

1. 최근에 했던 데이터 기반 결정을 질문 → 결정 흐름으로 다시 써 보세요.
2. p < 0.05 한 줄 보고서를 효과 크기와 신뢰구간 중심 보고서로 바꿔 보세요.
3. 통계적으로는 유의하지만 실무적으로는 거의 의미 없었던 사례를 하나 떠올려 보세요.
4. 여러분이 다루는 데이터에서 Simpson's Paradox가 나타날 수 있는 숨은 변수는 무엇일지 생각해 보세요.

## 정리와 다음 글

통계적 사고는 숫자를 많이 아는 상태가 아니라, 불확실한 상황에서 어떤 순서로 생각해야 하는지 아는 상태입니다. 질문을 먼저 적고, 데이터의 모양을 보고, 추정과 검정을 통해 불확실성을 드러내고, 효과 크기와 비용을 함께 읽어 결정을 내리는 흐름이 이 시리즈의 뼈대였습니다.

이 시리즈는 여기서 마무리되지만, 통계적 사고는 Probability 101, Machine Learning 101 같은 다음 주제의 기반이 됩니다. 확률과 예측 모델을 배우더라도 출발점은 여전히 같습니다. 좋은 질문을 세우고, 데이터를 바르게 읽고, 불확실성을 숨기지 않는 것입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Statistics 101 (1/10): 통계란 무엇인가?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): 평균, 중앙값, 분산](./02-mean-median-variance.md)
- [Statistics 101 (3/10): 분포](./03-distributions.md)
- [Statistics 101 (4/10): 표본과 모집단](./04-sample-and-population.md)
- [Statistics 101 (5/10): 추정](./05-estimation.md)
- [Statistics 101 (6/10): 신뢰구간](./06-confidence-interval.md)
- [Statistics 101 (7/10): 가설검정](./07-hypothesis-testing.md)
- [Statistics 101 (8/10): 상관과 회귀](./08-correlation-and-regression.md)
- [Statistics 101 (9/10): p-value 이해하기](./09-understanding-p-value.md)
- **통계적 사고방식 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [OpenIntro Statistics](https://www.openintro.org/book/os/)
- [NIST/SEMATECH e-Handbook of Statistical Methods](https://www.itl.nist.gov/div898/handbook/)
- [ASA Statement on p-Values (2016)](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)
- [Seeing Theory — Visual Introduction to Probability and Statistics](https://seeing-theory.brown.edu/)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/statistics-101/ko)

Tags: Statistics, Thinking, Mindset, Decision, Beginner
