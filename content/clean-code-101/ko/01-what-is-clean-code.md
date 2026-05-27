---
series: clean-code-101
episode: 1
title: "Clean Code 101 (1/10): Clean Code란 무엇인가?"
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
  - Readability
  - SoftwareEngineering
  - CodeQuality
  - Refactoring
seo_description: Clean Code의 기준과 변경 비용을 낮추는 핵심 신호를 설명합니다.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (1/10): Clean Code란 무엇인가?

코드는 일단 동작하면 끝난 것처럼 보이지만, 실제 비용은 그다음 변경에서 드러납니다.

이 글은 Clean Code 101 시리즈의 첫 번째 글입니다.

여기서는 동작하는 코드와 읽기 쉬운 코드, 그리고 바꾸기 쉬운 코드가 어떻게 다른지 한 번에 정리하겠습니다.

![Clean Code 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/01/01-01-concept-at-a-glance.ko.png)
*Clean Code 101 1장 흐름 개요*
> Clean Code는 한 번의 수정이 다른 곳을 깨뜨리지 않도록 경계를 명확하게 만드는 일입니다.

## 먼저 던지는 질문

- Clean Code를 판단할 때 어떤 신호를 먼저 봐야 할까요?
- 동작하는 코드와 읽기 쉬운 코드의 차이는 무엇일까요?
- 작은 원칙이 실제 유지보수 비용에 왜 큰 차이를 만들까요?

## 왜 중요한가

코드는 한 번 작성하고 여러 번 읽습니다. 그래서 가독성은 단순한 미학이 아니라 변경 비용을 결정하는 요소입니다. 이름이 흐리고 분기가 깊고 함수가 길어질수록, 다음 수정은 더 느려지고 더 위험해집니다.

현업에서는 이 차이가 아주 직접적으로 드러납니다. 기능 하나를 추가할 때 “어디를 바꿔야 하는지 바로 보이는 코드”와 “건드리면 다른 곳이 깨질 것 같은 코드”는 같은 기능을 구현해도 속도와 품질이 완전히 달라집니다.

## 한눈에 보는 개념

동작은 시작일 뿐이고, 신뢰는 결국 이해 가능성과 변경 용이성에서 나옵니다.

## 핵심 용어

- **Clean code**: 의도가 분명하고, 바꾸는 비용이 낮은 코드입니다.
- **Readability**: 다른 개발자가 빠르게 이해할 수 있는 상태입니다.
- **Cognitive load**: 코드 한 덩어리를 이해하는 데 필요한 정신적 부담입니다.
- **Smell**: 중복, 거대 함수, 깊은 분기처럼 개선이 필요하다는 신호입니다.
- **Refactoring**: 동작은 유지한 채 내부 구조를 개선하는 작업입니다.

## 전/후 비교

**Before — works, that's all**

```python
def f(d, t):
    return d * (1 + t)
```

**After — intent visible**

```python
def total_with_tax(amount: int, tax_rate: float) -> float:
    return amount * (1 + tax_rate)
```

두 번째 버전은 코드 길이가 거의 늘지 않았지만, 호출하는 쪽에서 의도가 훨씬 분명하게 보입니다. Clean Code의 핵심은 이런 식으로 작은 비용으로 큰 이해도를 얻는 데 있습니다.

## 실전 적용: 지저분함을 먼저 측정하기

### 단계 1 — 함수 길이
```python
# 1_length.py
def process(order):
    # 80 lines ...
    pass
```

함수가 20줄을 넘기기 시작하면, 길어진 이유를 먼저 설명할 수 있어야 합니다. 설명이 길어진다면 대개 함수도 이미 너무 많은 일을 하고 있습니다.

### 단계 2 — 인자 개수
```python
# 2_args.py
def create_user(name, email, age, address, role, plan, ref):
    ...
```

인자가 세 개를 넘기기 시작하면, 하나의 객체로 묶을 수 있는지 점검하는 편이 좋습니다. 함수 시그니처는 그 자체로 설계의 부담을 드러냅니다.

### 단계 3 — 들여쓰기 깊이
```python
# 3_depth.py
if a:
    if b:
        if c:
            do()
```

들여쓰기 깊이가 3을 넘으면 추출이나 분기 재구성이 필요하다는 신호로 보는 것이 좋습니다. 깊이는 곧 인지 부담입니다.

### 단계 4 — 정직한 이름
```python
# 4_name.py
def calc(x):  # of what?
    ...
def calculate_invoice_total(line_items):
    ...
```

이름이 거짓말하면 코드를 읽는 사람도 잘못된 기대를 갖습니다. 반대로 정직한 이름은 주석 몇 줄을 대신합니다.

### 단계 5 — 인지 부하 측정
```bash
# 5_cc.sh
radon cc app/ -a -s
```

순환 복잡도가 10을 넘는 곳은 분해 후보로 보는 편이 안전합니다. 측정하지 않으면 개선도 우선순위도 흐려집니다.

## 검증 방법

```bash
radon cc app/ -a -s
ruff check app/
```

**기대 결과**

- 복잡도 등급이 높은 함수가 어디인지 바로 보입니다.
- 이름과 분기, 함수 길이가 한 번에 점검됩니다.

## 실패하기 쉬운 지점

- 복잡도 수치만 보고 이름과 책임 분리를 놓칩니다.
- lint 경고가 많아서 진짜 설계 냄새가 묻힙니다.

## 이 코드에서 먼저 봐야 할 점

- 이름은 가장 먼저 의도를 보여 주는 인터페이스입니다.
- 함수 길이, 분기 깊이, 인자 수는 감상이 아니라 측정 가능한 신호입니다.
- 작은 규칙이 누적되면 코드베이스 전체의 변경 비용이 달라집니다.

## 자주 하는 실수 5가지

1. **"동작하니 됐다"에서 멈추기.** 몇 달 뒤에는 그 한 줄이 기술 부채가 됩니다.
2. **거대 함수를 방치하기.** 디버깅과 변경이 동시에 어려워집니다.
3. **거짓말하는 이름 붙이기.** 코드와 이름이 다르면 읽는 사람이 계속 속습니다.
4. **깊은 들여쓰기 유지하기.** 핵심 흐름이 분기에 묻힙니다.
5. **측정하지 않기.** 나빠지는 추세를 수치로 잡지 못합니다.

## 실무에서는 이렇게 보입니다

좋은 팀은 함수 길이, 복잡도, 이름 기준을 코드 리뷰 가이드에 명시합니다. 그리고 lint나 정적 분석으로 반복되는 문제를 자동으로 드러내서, 리뷰어가 더 중요한 설계 판단에 집중할 수 있게 만듭니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 코드는 한 번 쓰고 여러 번 읽습니다.
- 이름이 문서의 절반을 대신합니다.
- 측정 가능한 것은 개선할 수 있습니다.
- 작은 규칙이 큰 품질 차이를 만듭니다.
- Clean Code는 결국 다음 사람의 시간을 아끼는 일입니다.

## 체크리스트

- [ ] 함수가 20줄 이하인가?
- [ ] 인자가 3개 이하인가?
- [ ] 들여쓰기 깊이가 3 이하인가?
- [ ] 이름이 의도를 말하는가?
- [ ] 복잡도를 실제로 측정하는가?

## 연습 문제

1. 저장소에서 가장 긴 함수를 하나 골라 분해 계획을 적어 보세요.
2. 거짓말하는 이름 세 개를 찾아 더 정직하게 바꿔 보세요.
3. 프로젝트에 lint 규칙 세 개를 추가해 보세요.

## 정리 및 다음 단계

Clean Code는 추상적인 취향이 아니라, 측정 가능한 작은 원칙의 합입니다. 다음 글에서는 그중에서도 가장 즉각적인 효과를 내는 주제인 이름 짓기를 다룹니다.

## 코드 품질 지표를 숫자로 다루는 방법

좋은 코드는 감각으로도 구분할 수 있지만, 팀 단위 개선에서는 숫자가 반드시 필요합니다. 숫자는 논쟁을 줄이고 우선순위를 정해 줍니다. 아래 표는 Clean Code 관점에서 자주 쓰는 지표와 해석 기준입니다.

| 지표 | 권장 기준 | 측정 도구 예시 | 경고 신호 | 개선 우선순위 |
| --- | --- | --- | --- | --- |
| 함수 길이 | 20줄 이하 권장 | `radon`, 수동 리뷰 | 50줄 이상 함수 다수 | 높음 |
| 순환 복잡도 | 10 이하 권장 | `radon cc` | 15 이상 분기 함수 | 높음 |
| 인자 개수 | 3개 이하 권장 | 코드 리뷰, linter | 5개 이상 시그니처 | 중간 |
| 중복률 | 낮을수록 좋음 | `jscpd` 유사 도구, 리뷰 | 같은 규칙이 여러 파일에 반복 | 높음 |
| 테스트 커버리지 | 맥락 의존, 핵심 로직 우선 | `pytest --cov` | 핵심 계산 경로 미검증 | 높음 |
| 변경 실패율 | 낮을수록 좋음 | 배포 지표 | 사소한 수정 후 장애 빈발 | 매우 높음 |

지표는 절대 기준이 아니라 대화의 시작점입니다. 예를 들어 함수 길이가 30줄이어도 도메인 단위가 분명하고 테스트가 충분하면 유지할 수 있습니다. 반대로 12줄 함수라도 이름이 거짓말하고 부수 효과가 숨어 있으면 구조적으로 더 위험할 수 있습니다. 중요한 것은 지표를 맹신하지 않고, 지표를 근거로 설계 의도를 검증하는 습관입니다.

## 기술 부채 비용을 계산하는 실무 예시

기술 부채를 "나중에 고치면 된다"로 두면 거의 항상 더 비싸집니다. 아래는 단순한 산식으로 비용을 가시화하는 예시입니다.

```python
from dataclasses import dataclass

@dataclass
class RefactorCost:
    current_hours: float
    monthly_growth_rate: float
    delay_months: int
    outage_risk_cost: float

def estimate_total_cost(cost: RefactorCost) -> float:
    # 지연할수록 수정 시간이 복리로 증가한다고 가정합니다.
    future_hours = cost.current_hours * ((1 + cost.monthly_growth_rate) ** cost.delay_months)
    engineering_cost = future_hours * 100_000  # 시간당 10만 원 가정
    return engineering_cost + cost.outage_risk_cost

def compare_now_vs_later() -> tuple[float, float]:
    now = RefactorCost(
        current_hours=18,
        monthly_growth_rate=0.12,
        delay_months=0,
        outage_risk_cost=100_000,
    )
    later = RefactorCost(
        current_hours=18,
        monthly_growth_rate=0.12,
        delay_months=6,
        outage_risk_cost=1_000_000,
    )
    return estimate_total_cost(now), estimate_total_cost(later)
```

위 모델은 단순화된 예시이지만 팀 의사결정에는 충분히 유용합니다. 지금 고치면 200만 원 수준, 6개월 뒤에는 450만 원 이상으로 커질 수 있다는 숫자가 보이면, 리팩토링이 "취향"이 아니라 "재무적 선택"이라는 사실이 분명해집니다. 특히 장애 위험 비용을 같이 계산하면, 테스트와 구조 개선의 가치를 더 쉽게 설명할 수 있습니다.

## 코드 품질 대시보드 설계 예시

팀이 매주 보는 대시보드에는 최소한 다음 항목이 포함되는 편이 좋습니다.

1. 복잡도 상위 20개 함수
2. 최근 30일 변경 파일 중 테스트 미보강 항목
3. 중복 규칙 감지 목록
4. 리뷰에서 반복된 지적 키워드
5. 핫스팟 파일의 리드타임

핵심은 "어디부터 고칠지"가 바로 보이게 만드는 것입니다. 좋은 대시보드는 문제를 미학적으로 보여 주는 것이 아니라, 다음 행동을 즉시 고르게 도와줍니다. 따라서 지표를 많이 모으기보다, 행동으로 이어지는 지표를 작게 유지하는 쪽이 낫습니다.

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

## 추가 사례: 변경 비용 예측 스프린트 회고

스프린트 회고에서 아래 세 질문을 반복하면 품질 개선 항목이 구체화됩니다.

- 이번 스프린트에서 가장 오래 걸린 변경은 무엇이었는가
- 오래 걸린 이유가 도메인 복잡도인지 코드 구조인지 구분되었는가
- 같은 종류의 변경을 다음 달에는 얼마나 줄일 수 있는가

```python
def estimate_next_month_effort(current_hours: float, reduction_goal: float) -> float:
    if not 0 <= reduction_goal <= 1:
        raise ValueError("reduction_goal must be in [0, 1]")
    return current_hours * (1 - reduction_goal)
```

이런 질문과 간단한 계산만으로도 "감" 중심 회고를 "계획" 중심 회고로 바꿀 수 있습니다.

## 코드 스멜 카탈로그와 우선순위 결정

클린 코드 개선은 "무엇이 불편한가"가 아니라 "어떤 변경 비용을 줄일 것인가"를 기준으로 우선순위를 잡아야 합니다. 아래 카탈로그는 초급 팀이 바로 적용할 수 있는 최소 기준입니다.

| 코드 스멜 | 관찰 신호 | 위험 | 1차 수정 | 2차 수정 |
| --- | --- | --- | --- | --- |
| 긴 함수 | 40줄 이상, 중첩 3단 이상 | 리뷰 속도 저하 | 가드 절 분리 | 책임 단위 모듈화 |
| 모호한 이름 | `data`, `info`, `tmp` 빈발 | 오해성 버그 | 목적이 드러나는 이름으로 변경 | 도메인 용어집 반영 |
| 중복 분기 | 같은 if/elif 체인이 여러 파일에 존재 | 정책 불일치 | 정책 함수 추출 | 전략 객체로 승격 |
| 경계 없는 예외 처리 | 모든 예외를 `except Exception`으로 흡수 | 장애 은폐 | 경계에서만 잡기 | 예외 계층 재설계 |
| 테스트 어려움 | 외부 의존과 순수 로직 혼합 | 회귀 위험 | 의존성 주입 | 계약 테스트 도입 |

카탈로그의 핵심은 "완벽한 설계"가 아니라 "다음 변경이 쉬운 구조"입니다. 스프린트 계획에 기능 항목과 함께 스멜 제거 항목을 넣으면 기술 부채가 백로그 밖으로 빠져나가지 않습니다.

## 리팩토링 전/후 함수 추출 데모

```python
# before
def process_signup(request, mailer, repo, logger):
    email = request.get("email", "").strip().lower()
    if not email or "@" not in email:
        return {"ok": False, "reason": "invalid_email"}

    if repo.exists_by_email(email):
        return {"ok": False, "reason": "already_exists"}

    user = {"email": email, "status": "pending"}
    repo.save(user)
    token = f"verify-{email}"
    verify_link = f"https://example.com/verify?token={token}"
    mailer.send(email, "verify", verify_link)
    logger.info("signup-created", extra={"email": email})
    return {"ok": True}

# after
def process_signup(request, mailer, repo, logger):
    email = normalize_email(request)
    validate_signup_preconditions(email, repo)

    user = create_pending_user(email, repo)
    send_verification_mail(user["email"], mailer)
    logger.info("signup-created", extra={"email": user["email"]})
    return {"ok": True}

def normalize_email(request: dict) -> str:
    return request.get("email", "").strip().lower()

def validate_signup_preconditions(email: str, repo) -> None:
    if not email or "@" not in email:
        raise ValueError("invalid_email")
    if repo.exists_by_email(email):
        raise ValueError("already_exists")
```

리팩토링 후 코드는 동작보다 의도를 먼저 읽게 만듭니다. `process_signup`는 흐름만 보여 주고, 검증/생성/알림 책임은 별도 함수가 맡습니다. 이 구조가 바로 이후 테스트 가능한 코드의 기반이 됩니다.

## 린터 구성 예시: 규칙을 사람 대신 도구가 강제하기

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "B", "C90", "N", "I", "UP"]
ignore = ["E501"]

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.pep8-naming]
classmethod-decorators = ["classmethod"]
```

린터 규칙은 합의의 자동화입니다. 팀 규칙이 문서에만 있으면 신규 멤버 온보딩 때마다 기준이 흔들립니다. 반대로 린터에 들어가면 코드 리뷰는 "스타일 지적"에서 "설계 판단"으로 이동합니다.

## 심화 실습: 코드 품질 기준선을 팀에 도입하기

클린 코드 원칙은 개인 습관으로 끝나면 유지되지 않습니다. 팀 단위 운영 규칙으로 정착해야 실제 효과가 납니다. 첫 주에는 "기준선 만들기"에만 집중하는 것이 좋습니다. 기존 코드를 한 번에 고치지 말고, 새로 바뀌는 파일부터 규칙을 적용합니다.

| 주차 | 목표 | 산출물 | 검증 |
| --- | --- | --- | --- |
| 1주차 | 품질 기준선 정의 | 명명/함수/분기 규칙 문서 | 팀 합의 회의록 |
| 2주차 | 자동화 연결 | 린터/테스트 게이트 | CI 통과율 |
| 3주차 | 리뷰 규칙 정착 | PR 템플릿, 체크리스트 | 리뷰 리드타임 |
| 4주차 | 회고 및 보정 | 실패 패턴 목록 | 다음 스프린트 액션 |

```python
from dataclasses import dataclass

@dataclass
class QualityBaseline:
    max_function_lines: int = 30
    max_cyclomatic_complexity: int = 10
    max_arguments: int = 4
    require_domain_terms: bool = True

def evaluate_module_metrics(function_lines: int, complexity: int, arguments: int) -> list[str]:
    issues: list[str] = []
    baseline = QualityBaseline()

    if function_lines > baseline.max_function_lines:
        issues.append("function-too-long")
    if complexity > baseline.max_cyclomatic_complexity:
        issues.append("complexity-too-high")
    if arguments > baseline.max_arguments:
        issues.append("too-many-arguments")
    return issues
```

실무에서는 완벽한 기준보다 측정 가능한 기준이 중요합니다. 함수 길이, 복잡도, 인자 수 같은 지표가 있어야 개선 우선순위를 정할 수 있습니다.

## 변경 비용 추적 로그 예시

```text
2026-05-01 | user-profile.py | 함수 분해 전 | 리뷰 38분 | 버그 2건
2026-05-08 | user-profile.py | 함수 분해 후 | 리뷰 17분 | 버그 0건
2026-05-15 | checkout.py     | 분기 단순화 전 | 리뷰 41분 | 버그 3건
2026-05-22 | checkout.py     | 분기 단순화 후 | 리뷰 19분 | 버그 1건
```

변경 비용 로그를 남기면 품질 개선이 감각이 아니라 데이터가 됩니다. 팀이 "왜 이 원칙을 지키는지"를 설명할 수 있어야 규칙이 오래 갑니다.

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

- **Clean Code를 판단할 때 어떤 신호를 먼저 봐야 할까요?**
  - 이 글에서는 함수 길이, 인자 개수, 들여쓰기 깊이, 이름의 정직성, 순환 복잡도 같은 신호를 먼저 보라고 정리했습니다. `radon cc app/ -a -s`와 `ruff check app/`처럼 측정 가능한 도구를 붙여야 감상이 아니라 근거로 품질을 판단할 수 있습니다.
- **동작하는 코드와 읽기 쉬운 코드의 차이는 무엇일까요?**
  - `f(d, t)`를 `total_with_tax(amount, tax_rate)`로 바꾼 예시처럼, 읽기 쉬운 코드는 호출 지점에서 의도와 단위가 바로 드러납니다. 같은 동작을 하더라도 이름과 구조가 분명하면 다음 사람이 어디를 바꿔야 하는지 훨씬 빨리 판단할 수 있습니다.
- **작은 원칙이 실제 유지보수 비용에 왜 큰 차이를 만들까요?**
  - 품질 대시보드, `QualityGate`, `change_impact_score` 예시가 보여 주듯이 작은 원칙은 리뷰 시간, 버그 수, 변경 실패율로 이어집니다. 이름 하나와 분기 하나를 바로잡는 습관이 쌓이면 다음 수정의 탐색 비용과 장애 위험이 함께 내려갑니다.

<!-- toc:begin -->
## 시리즈 목차

- **Clean Code란 무엇인가? (현재 글)**
- 이름 짓기 (예정)
- 함수 작게 만들기 (예정)
- 조건문 줄이기 (예정)
- 중복 제거 (예정)
- 오류 처리 (예정)
- 주석과 문서화 (예정)
- 테스트 가능한 코드 (예정)
- 리팩토링 기초 (예정)
- 좋은 코드 리뷰 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Clean Code — Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [A Philosophy of Software Design — John Ousterhout](https://web.stanford.edu/~ouster/cgi-bin/aposd.php)
- [Refactoring — Martin Fowler](https://martinfowler.com/books/refactoring.html)
- [Google — Code Health Articles](https://testing.googleblog.com/search/label/Code%20Health)
- [Ruff rule reference](https://docs.astral.sh/ruff/rules/)
- [radon documentation](https://radon.readthedocs.io/en/latest/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/clean-code-101/ko)
Tags: Computer Science, CleanCode, Readability, SoftwareEngineering, CodeQuality, Refactoring
