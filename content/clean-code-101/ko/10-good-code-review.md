---
series: clean-code-101
episode: 10
title: "Clean Code 101 (10/10): 좋은 코드 리뷰 기준"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - CleanCode
  - CodeReview
  - PullRequest
  - Quality
  - Collaboration
seo_description: 좋은 코드 리뷰 기준과 실행 가능한 리뷰 코멘트 작성법을 익혀 팀의 개발 생산성과 코드 품질을 높이는 방법을 제안합니다.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (10/10): 좋은 코드 리뷰 기준

좋은 코드는 작성 단계에서만 만들어지지 않고, 리뷰 단계에서 팀의 기준으로 다시 다듬어집니다.

이 글은 Clean Code 101 시리즈의 마지막 글입니다.

여기서는 지금까지 다룬 이름, 함수, 분기, 중복, 오류, 테스트, 리팩토링 관점을 실제 PR 리뷰 기준으로 어떻게 묶을지 정리하겠습니다.


![Clean Code 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/10/10-01-concept-at-a-glance.ko.png)
*Clean Code 101 10장 흐름 개요*
> 나마 동스턴돘게나 동스른 동스른 동스른 동스른 동스른 동스른 동스른 동스른 동스른 동스른 동스른.

## 먼저 던지는 질문

- 리뷰 가능한 PR 크기는 어느 정도일까요?
- Clean Code 관점의 리뷰 체크리스트는 무엇일까요?
- 좋은 리뷰 코멘트는 어떤 형태를 가져야 할까요?

## 왜 중요한가

코드 리뷰는 마지막 품질 게이트이면서 동시에 가장 큰 학습 채널입니다. 작은 PR, 충분한 맥락, 실행 가능한 코멘트가 갖춰지면 리뷰는 단순한 승인 절차가 아니라 팀의 기준을 맞추는 시간으로 바뀝니다.

반대로 큰 PR, 취향 위주의 코멘트, 자동화로도 잡을 수 있는 반복 지적이 쌓이면 리뷰는 금방 피로한 의식이 됩니다. 그래서 좋은 리뷰 기준은 코드만이 아니라 리뷰 프로세스 자체를 설계하는 문제이기도 합니다.

## 한눈에 보는 개념

자동화는 잡무를 처리하고, 사람은 의도와 구조를 봐야 리뷰가 가치 있는 시간이 됩니다.

## 핵심 용어

- **PR (Pull Request)**: 하나의 변경 단위입니다.
- **Review comment**: 변경에 대한 의견과 제안입니다.
- **Approval**: 병합 가능하다는 신호입니다.
- **CI (Continuous Integration)**: 자동 빌드와 테스트입니다.
- **Style guide**: 팀이 공유하는 규칙 모음입니다.

## 전/후 비교

**Before**

```text
"This function is too long."
```

**After**

```text
"order_total is 60 lines. Splitting into subtotal/with_coupon/with_member
would make the body read like a table of contents (see ep03, ep05).
Options: (a) split in this PR, (b) follow-up PR with an issue link."
```

좋은 리뷰 코멘트는 실행 가능해야 합니다. 무엇이 문제인지, 왜 문제인지, 어떤 방향이 가능한지까지 보여 주어야 작성자가 바로 판단할 수 있습니다.

## 실전 적용: 탄탄한 리뷰 프로세스 다섯 단계

### 단계 1 — Push toil into automation

```yaml
# 1_ci.yml
- run: ruff check .
- run: black --check .
- run: pytest -q
```

스타일, 포맷, 기본 테스트는 사람 눈앞에 오기 전에 끝나야 합니다. 사람이 자동화가 할 일을 대신하면 리뷰의 질이 바로 떨어집니다.

### 단계 2 — Keep PRs small

```text
# 2_small_pr.txt
Recommended: under 400 lines diff, one responsibility
```

작은 PR은 빠른 리뷰의 전제입니다. 한 책임만 담긴 PR이어야 리뷰어도 기준을 선명하게 적용할 수 있습니다.

### 단계 3 — Read intent first

```markdown
<!-- 3_pr_template.md -->
## 무엇을 바꾸는가
What is changing
## 왜 바꾸는가
Why it changes (issue link)
## 어떻게 바꾸는가
How it was verified (tests/screenshots)
## 위험은 무엇인가
What could go wrong
```

맥락 없는 PR은 제대로 리뷰할 수 없습니다. 리뷰어는 코드보다 먼저 의도와 위험을 읽어야 전체 구조를 올바르게 판단할 수 있습니다.

### 단계 4 — Write actionable comments

```text
# 4_comment.txt
NIT: minor (optional)
SUGG: suggestion (recommended for this PR)
MUST: must address before merge
QUESTION: clarification
```

우선순위 라벨이 붙은 코멘트는 불필요한 마찰을 줄입니다. 무엇이 선택 사항이고 무엇이 병합 전 필수인지 분명해야 합니다.

### 단계 5 — Learn through retrospectives

```text
# 5_retro.txt
- Move repeated comments into lints/docs.
- Build a guide for splitting big PRs.
- Measure review time and treat it as an improvement target.
```

반복되는 리뷰 코멘트는 프로세스 개선 신호입니다. 같은 지적이 계속 나온다면 사람을 탓하기보다 자동화나 가이드로 옮겨야 합니다.

## 검증 방법

```bash
ruff check .
python -m pytest -q
GIT_PAGER=cat git diff --stat HEAD~1..HEAD
```

**기대 결과**

- 자동화가 처리할 문제는 PR에 올라오기 전에 정리됩니다.
- diff 크기와 검증 결과가 리뷰 설명과 맞아야 합니다.

## 실패하기 쉬운 지점

- 리뷰 코멘트가 취향과 필수를 구분하지 못합니다.
- 반복 지적이 lint나 템플릿으로 옮겨가지 않습니다.

## 이 코드에서 먼저 봐야 할 점

- 자동화가 끝낸 일은 사람이 다시 검사하지 않습니다.
- 코멘트는 우선순위 라벨을 가집니다.
- PR 설명이 변경 맥락을 충분히 제공합니다.

## 자주 하는 실수 5가지

1. **거대한 PR 만들기.** 아무도 끝까지 제대로 읽지 못합니다.
2. **취향 위주의 코멘트 남기기.** 마찰만 키웁니다.
3. **MUST를 남용하기.** 신뢰가 빠르게 떨어집니다.
4. **자동화 가능한 일을 사람이 하기.** 시간 낭비입니다.
5. **학습 기록 없이 승인하기.** 같은 실수가 반복됩니다.

## 실무에서는 이렇게 보입니다

좋은 팀은 평균 PR 크기, 첫 응답까지 걸린 시간, 병합 리드 타임을 측정합니다. 숫자가 나빠지면 개발자 개인을 탓하기보다 리뷰 프로세스 자체를 리팩토링합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 작은 PR을 강하게 지지합니다.
- 자동화가 할 수 있는 일은 직접 하지 않습니다.
- 코드를 보기 전에 의도를 읽습니다.
- 우선순위가 있는 실행 가능한 코멘트를 남깁니다.
- 리뷰 시간 자체도 하나의 지표로 봅니다.

## 체크리스트

- [ ] PR이 한 가지 책임만 다루는가?
- [ ] CI가 초록인가?
- [ ] 설명(What/Why/How/Risk)이 충분한가?
- [ ] 코멘트에 우선순위 라벨이 있는가?
- [ ] 반복 코멘트를 자동화로 옮길 수 있는가?

## 연습 문제

1. 팀의 평균 PR 크기를 측정하고 절반으로 줄이는 실험을 해 보세요.
2. 자주 반복되는 코멘트 세 개를 lint 규칙으로 바꿔 보세요.
3. PR 템플릿을 도입하고 한 달 뒤 회고를 진행해 보세요.

## 정리 및 다음 단계

좋은 리뷰는 Clean Code의 거울입니다. 이름, 함수, 분기, 중복, 오류, 주석, 테스트, 리팩토링, 리뷰까지 이 시리즈의 모든 주제는 결국 다음 사람이 더 쉽게 바꿀 수 있는 코드를 향합니다.


## 레거시 코드 개선 전략과 점진적 리팩토링 계획

좋은 리뷰는 지금 보이는 diff만 평가하지 않고, 다음 변경 비용까지 줄이는 방향을 제안합니다. 특히 레거시 코드에서는 "한 번에 완벽"보다 점진적 개선 계획이 중요합니다.

| 단계 | 목표 | 리뷰 포인트 | 산출물 |
| --- | --- | --- | --- |
| 1단계 | 현재 동작 고정 | 특성화 테스트 존재 여부 | 안전망 테스트 |
| 2단계 | 구조 단순화 | 함수 길이/분기 깊이 감소 | 리팩토링 PR |
| 3단계 | 중복 제거 | 정책 출처 단일화 | 공통 모듈/테이블 |
| 4단계 | 오류 경계 정리 | 예외 계층/매핑 명확성 | 에러 처리 가이드 |
| 5단계 | 자동화 강화 | 반복 지적의 도구화 | lint/CI 규칙 |

이 표를 리뷰 템플릿에 넣으면, 리뷰어가 단기 수정과 장기 계획을 동시에 제안하기 쉬워집니다.

## 리뷰 코멘트를 계획으로 연결하는 예시

```python
from dataclasses import dataclass

@dataclass
class ReviewAction:
    priority: str
    message: str
    follow_up_issue: str | None = None


def build_review_actions() -> list[ReviewAction]:
    return [
        ReviewAction(
            priority="MUST",
            message="order_total의 분기 깊이가 4입니다. Guard Clause 적용이 필요합니다.",
            follow_up_issue=None,
        ),
        ReviewAction(
            priority="SUGG",
            message="중복된 할인 계산을 Extract Method로 분리하면 테스트가 단순해집니다.",
            follow_up_issue="#123",
        ),
        ReviewAction(
            priority="NIT",
            message="변수명 total을 subtotal_cents로 바꾸면 단위가 명확해집니다.",
            follow_up_issue=None,
        ),
    ]
```

위처럼 우선순위와 후속 이슈를 함께 기록하면, 리뷰 코멘트가 단순 의견에서 실행 계획으로 바뀝니다.

## 점진적 리팩토링 백로그 예시

```python
REFactoring_BACKLOG = [
    {"id": "CC-101", "task": "order_total 분해", "owner": "backend", "week": 1},
    {"id": "CC-102", "task": "예외 계층 표준화", "owner": "backend", "week": 2},
    {"id": "CC-103", "task": "중복 할인 정책 테이블화", "owner": "backend", "week": 3},
    {"id": "CC-104", "task": "리뷰 템플릿 강화", "owner": "platform", "week": 4},
]


def group_tasks_by_week(tasks: list[dict]) -> dict[int, list[str]]:
    grouped: dict[int, list[str]] = {}
    for task in tasks:
        week = task["week"]
        grouped.setdefault(week, []).append(task["task"])
    return grouped
```

리뷰는 병합 버튼을 누르는 이벤트가 아니라, 품질 개선 루프를 운영하는 일입니다. 따라서 "이번 PR에서 반드시 할 일"과 "다음 스프린트에서 안전하게 할 일"을 명확히 분리해 제안하는 것이 중요합니다.

## 리뷰 프로세스 성숙도 측정 지표

1. 평균 PR 크기
2. 첫 리뷰 응답 시간
3. 재작업 라운드 수
4. 병합 후 회귀 버그 비율
5. 반복 코멘트 자동화 전환율

```python
def review_process_score(metrics: dict[str, float]) -> float:
    weights = {
        "small_pr_ratio": 0.25,
        "fast_response_ratio": 0.2,
        "low_rework_ratio": 0.2,
        "low_regression_ratio": 0.25,
        "automation_conversion_ratio": 0.1,
    }
    score = 0.0
    for key, weight in weights.items():
        score += metrics.get(key, 0.0) * weight
    return round(score, 3)
```

이런 지표를 월 단위로 추적하면 코드 리뷰 문화가 실제로 개선되는지 확인할 수 있습니다.


## 실무 적용 메모

아래 메모는 팀 내 합의 문서에 그대로 옮겨 적어도 되는 수준의 운영 규칙입니다.

1. 리뷰는 코드 스타일보다 변경 위험을 먼저 다룹니다.
2. 규칙 위반은 사람 지적보다 자동화 전환을 우선합니다.
3. 반복되는 설계 결함은 교육 과제가 아니라 구조 개선 과제로 등록합니다.
4. 모든 개선은 테스트와 함께 진행하며, 동작 변경 여부를 PR 설명에 명시합니다.
5. 다음 분기 목표에는 "새 기능 수"와 함께 "변경 비용 감소 지표"를 반드시 포함합니다.

```python
from dataclasses import dataclass

@dataclass
class QualityGate:
    has_tests: bool
    has_clear_names: bool
    has_boundary_error_handling: bool
    has_small_functions: bool
    has_review_notes: bool


def evaluate_gate(gate: QualityGate) -> tuple[bool, list[str]]:
    missing = []
    if not gate.has_tests:
        missing.append("tests")
    if not gate.has_clear_names:
        missing.append("naming")
    if not gate.has_boundary_error_handling:
        missing.append("error-boundary")
    if not gate.has_small_functions:
        missing.append("function-size")
    if not gate.has_review_notes:
        missing.append("review-notes")
    return len(missing) == 0, missing
```

이 체크 함수는 단순하지만, 품질 기준을 코드로 표현하는 출발점이 됩니다. 팀이 기준을 말로만 합의하면 시간이 지나며 흐려집니다. 반대로 코드와 템플릿과 자동화 규칙으로 남기면 신규 멤버가 들어와도 동일한 기준이 유지됩니다.

또한 개선 활동은 단발성 이벤트가 아니라 루프여야 합니다. 한 번의 대청소보다 매 PR마다 작은 개선을 추가하는 편이 장기적으로 더 강합니다. 이름 하나, 함수 하나, 분기 하나를 매번 더 낫게 만드는 습관이 쌓이면 코드베이스의 평균 품질이 올라가고, 장애 대응 속도도 실제로 빨라집니다.


## 코드 리뷰 기준표: 의견이 아니라 근거로 대화하기

좋은 리뷰는 취향 비교가 아니라 위험 관리입니다. 아래 기준표를 리뷰 템플릿에 고정하면 코멘트 품질이 빠르게 안정됩니다.

| 관점 | 질문 | 확인 방법 |
| --- | --- | --- |
| 정확성 | 요구사항을 정확히 반영했는가 | 테스트/샘플 입력 검토 |
| 가독성 | 이름과 함수 경계가 명확한가 | 전/후 코드 비교 |
| 안정성 | 예외/경계 처리 누락이 없는가 | 실패 시나리오 확인 |
| 확장성 | 새 정책 추가 시 수정 범위가 작은가 | OCP 관점 점검 |
| 운영성 | 로그, 메트릭, 롤백 전략이 있는가 | PR 본문 체크리스트 |

## 전/후 데모: 리뷰 가능한 PR 단위로 쪼개기

```text
# before
PR-1: 결제 정책 변경 + 함수 분리 + 이름 변경 + 테스트 보강

# after
PR-1: 함수 분리(동작 동일)
PR-2: 이름 변경(동작 동일)
PR-3: 결제 정책 추가(동작 변경)
```

PR 단위를 분리하면 리뷰어는 "무엇이 바뀌었는가"와 "왜 바꿨는가"를 빠르게 판단할 수 있습니다. 결과적으로 리뷰 속도와 품질이 함께 올라갑니다.

## 리뷰 코멘트 템플릿 예시

```markdown
- 관찰: `calculate_total`가 결제/할인/로깅을 함께 수행합니다.
- 위험: 변경 이유가 여러 개라 회귀 가능성이 큽니다.
- 제안: 계산 함수와 부수효과 함수를 분리하면 테스트 범위를 줄일 수 있습니다.
- 확인: 분리 후 기존 테스트와 신규 경계 테스트를 함께 요청합니다.
```

## 자동화 게이트 예시

```yaml
name: review-gate
on: [pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: pytest -q
```

자동화는 리뷰어의 시간을 반복 검증에서 해방시킵니다. 사람이 봐야 하는 영역은 설계 의도와 위험 trade-off입니다.


## 심화 실습: 리뷰 운영 지표 만들기

리뷰 품질은 느낌이 아니라 지표로 관리해야 개선됩니다. 아래 지표를 월 단위로 보면 병목 지점을 찾기 쉽습니다.

| 지표 | 설명 | 목표 예시 |
| --- | --- | --- |
| 첫 리뷰 응답 시간 | PR 생성 후 첫 코멘트까지 시간 | 4시간 이내 |
| 리뷰 라운드 수 | 승인까지 필요한 왕복 횟수 | 2회 이하 |
| 자동화 실패율 | 린터/테스트 실패 비율 | 10% 이하 |
| 리뷰 후 회귀 결함률 | 병합 후 7일 내 결함 발생 | 2% 이하 |

```python
def review_health_score(first_response_hours: float, rounds: int, regression_rate: float) -> float:
    score = 100.0
    score -= max(0, first_response_hours - 4) * 2
    score -= max(0, rounds - 2) * 5
    score -= regression_rate * 100
    return max(score, 0)
```

지표는 사람 평가가 아니라 프로세스 개선 도구입니다. 팀 문화를 해치지 않으려면 지표를 개인 비교가 아니라 시스템 개선 기준으로만 사용해야 합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.

## 처음 질문으로 돌아가기

- **리뷰 가능한 PR 크기는 어느 정도일까요?**
  - 본문의 기준은 좋은 코드 리뷰 기준를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Clean Code 관점의 리뷰 체크리스트는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **좋은 리뷰 코멘트는 어떤 형태를 가져야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Clean Code 101 (1/10): Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): 이름 짓기](./02-naming.md)
- [Clean Code 101 (3/10): 함수 작게 만들기](./03-small-functions.md)
- [Clean Code 101 (4/10): 조건문 줄이기](./04-simplifying-conditionals.md)
- [Clean Code 101 (5/10): 중복 제거](./05-removing-duplication.md)
- [Clean Code 101 (6/10): 오류 처리](./06-error-handling.md)
- [Clean Code 101 (7/10): 주석과 문서화](./07-comments-and-docs.md)
- [Clean Code 101 (8/10): 테스트 가능한 코드](./08-testable-code.md)
- [Clean Code 101 (9/10): 리팩토링 기초](./09-refactoring-basics.md)
- **좋은 코드 리뷰 기준 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Google Engineering Practices — Code Review](https://google.github.io/eng-practices/review/)
- [Conventional Comments](https://conventionalcomments.org/)
- [Best Kept Secrets of Peer Code Review (Smart Bear)](https://smartbear.com/resources/ebooks/best-kept-secrets-of-peer-code-review/)
- [Microsoft Engineering Fundamentals — Code Review](https://microsoft.github.io/code-with-engineering-playbook/code-reviews/)
- [Google engineering practices — code review](https://google.github.io/eng-practices/review/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/clean-code-101/ko)
Tags: Computer Science, CleanCode, CodeReview, PullRequest, Quality, Collaboration
