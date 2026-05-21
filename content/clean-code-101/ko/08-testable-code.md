---
series: clean-code-101
episode: 8
title: "Clean Code 101 (8/10): 테스트 가능한 코드"
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
  - Testability
  - Testing
  - DependencyInjection
  - Refactoring
seo_description: 테스트 가능성을 높이는 구체적인 기법을 배웁니다. 순수 함수와 의존성 주입을 활용해 흔들리지 않는 견고한 단위 테스트 작성법을 배웁니다.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (8/10): 테스트 가능한 코드

어떤 코드는 테스트 한 줄로 끝나는데, 어떤 코드는 테스트를 쓰려는 순간부터 거대한 준비 작업이 필요합니다.

이 글은 Clean Code 101 시리즈의 8번째 글입니다.

여기서는 그 차이가 어디서 오는지, 그리고 설계를 바꾸면 왜 테스트가 자연스럽게 따라오는지 설명하겠습니다.


![Clean Code 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/08/08-01-concept-at-a-glance.ko.png)
*Clean Code 101 8장 흐름 개요*
> 숐주되고 멍멠른 먼진이 명넌 동스른 동스른 동스른 동스른 동스른 동스른 동스른 동스른 동스른 동스른 동스른 동스른 동스른.

## 먼저 던지는 질문

- 순수 로직과 부수 효과는 어떻게 분리해야 할까요?
- 의존성 주입은 어떻게 테스트용 이음새를 만들까요?
- Fake와 Spy는 각각 언제 쓰는 편이 좋을까요?

## 왜 중요한가

테스트하기 어려운 코드는 대개 바꾸기도 어렵습니다. 데이터베이스, 네트워크, 현재 시간, 전역 싱글턴이 함수 내부에 깊게 붙어 있으면, 작은 규칙 하나를 검증하는 일조차 무겁고 느려집니다.

반대로 핵심 로직을 순수하게 만들고, 외부 의존성을 경계로 밀어내면 테스트는 놀랄 만큼 단순해집니다. 그래서 테스트 가능성은 단순한 QA 편의가 아니라 설계 품질의 측정치로 보는 편이 정확합니다.

## 한눈에 보는 개념

가장 좋은 구조는 순수한 핵심 로직을 얇은 어댑터가 둘러싸는 형태입니다.

## 핵심 용어

- **Pure function**: 같은 입력에 같은 출력을 내고, 부수 효과가 없는 함수입니다.
- **Dependency Injection**: 외부 의존성을 인자로 받는 방식입니다.
- **Seam**: 동작을 교체할 수 있는 경계 지점입니다.
- **Fake**: 테스트용으로 단순화한 동작 구현체입니다.
- **Spy**: 호출 기록을 남기는 테스트 더블입니다.

## 전/후 비교

**Before**

```python
import datetime, requests
def is_business_hour():
    now = datetime.datetime.now()
    return 9 <= now.hour < 18

def fetch_user(uid):
    return requests.get(f"https://api/users/{uid}").json()
```

**After**

```python
def is_business_hour(now):
    return 9 <= now.hour < 18

def fetch_user(uid, http):
    return http.get(f"/users/{uid}").json()
```

시간과 HTTP를 함수 밖에서 넣어 주면, 핵심 로직은 훨씬 쉽게 검증할 수 있습니다. 테스트 가능한 코드는 보통 더 작은 경계와 더 명시적인 의존성을 가집니다.

## 실전 적용: 테스트 가능성을 높이는 다섯 단계

### 단계 1 — 순수 로직 추출
```python
# 1_pure.py
def total(items):
    return sum(it.price * it.qty for it in items)
```

입출력 없이 계산만 하는 부분은 항상 순수 함수 후보입니다. 이런 핵심 계산을 먼저 분리하면 단위 테스트가 거의 공짜가 됩니다.

### 단계 2 — 시간 주입
```python
# 2_clock.py
from datetime import datetime
def is_overdue(due, now=None):
    now = now or datetime.now()
    return now > due
```

시간은 흐르기 때문에 테스트를 깨뜨립니다. 고정 가능한 값으로 받아들이는 순간 테스트는 안정성을 얻습니다.

### 단계 3 — Fake 객체
```python
# 3_fake.py
class FakeRepo:
    def __init__(self): self.users = {}
    def save(self, u): self.users[u.id] = u
    def get(self, uid): return self.users.get(uid)

def register(repo, user):
    repo.save(user); return user
```

도메인 로직을 검증하는 데 실제 데이터베이스가 꼭 필요하지는 않습니다. Fake는 느리고 불안정한 외부 의존성을 테스트 밖으로 밀어냅니다.

### 단계 4 — 호출 기록 (Spy)
```python
# 4_spy.py
class EmailSpy:
    def __init__(self): self.sent = []
    def send(self, to, body): self.sent.append((to, body))

def notify(email, user):
    email.send(user.email, "welcome")
```

Spy는 무엇을 보냈는지, 몇 번 호출했는지 검증하게 해 줍니다. 협력 객체와의 상호작용을 확인할 때 유용합니다.

### 단계 5 — 외부 호출 격리
```python
# 5_adapter.py
class HttpClient:
    def get(self, path): ...

def fetch_user(uid, http: HttpClient):
    return http.get(f"/users/{uid}").json()
```

외부 호출을 하나의 어댑터로 집중시키면 테스트 범위를 나누기 쉬워집니다. 단위 테스트는 Fake로, 통합 테스트는 실제 어댑터로 분리할 수 있습니다.

## 검증 방법

```bash
python -m pytest -q tests/test_total.py tests/test_notify.py
python -m pytest -q tests/test_http_adapter.py
```

**기대 결과**

- 순수 함수 테스트는 매우 빠르게 끝나야 합니다.
- 어댑터 테스트만 외부 의존성과 통합되어야 합니다.

## 실패하기 쉬운 지점

- `datetime.now()`와 난수가 아직 핵심 로직 안에 남아 있습니다.
- mock 수가 많아졌는데도 함수 책임은 그대로 큽니다.

## 이 코드에서 먼저 봐야 할 점

- 핵심 로직은 IO를 몰라야 합니다.
- 시간과 난수는 항상 주입하는 편이 좋습니다.
- Fake를 쓰면 테스트가 빠르고 안정적으로 돌아갑니다.

## 자주 하는 실수 5가지

1. **함수 안에서 `datetime.now()` 호출하기.** 시간이 지나면 테스트가 흔들립니다.
2. **DB와 네트워크를 도메인 로직에 섞기.** 단위 테스트가 사라집니다.
3. **mock 라이브러리에만 의존하기.** 숨은 결합은 그대로 남습니다.
4. **테스트를 위해 공개 메서드 늘리기.** 캡슐화가 깨집니다.
5. **전역 싱글턴 사용하기.** 격리가 어려워집니다.

## 실무에서는 이렇게 보입니다

좋은 팀은 ports-and-adapters나 hexagonal architecture 같은 구조를 써서 도메인 코어를 IO에서 분리합니다. 그 덕분에 수천 개의 단위 테스트도 아주 빠르게 끝나고, 느린 통합 테스트는 별도 계층으로 관리할 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 먼저 순수 함수부터 만듭니다.
- 의존성은 인자로 받습니다.
- mocks보다 fakes를 더 자주 선호합니다.
- 시간, 난수, IO를 경계 바깥으로 밀어냅니다.
- 느린 테스트를 설계 냄새로 봅니다.

## 체크리스트

- [ ] 핵심 로직이 순수한가?
- [ ] 외부 의존성을 주입받는가?
- [ ] 시간과 난수를 주입하는가?
- [ ] Fake로 IO 없이 테스트할 수 있는가?
- [ ] 단위 테스트가 1초 안에 끝나는가?

## 연습 문제

1. 코드 안의 `datetime.now()` 호출 하나를 주입 방식으로 바꿔 보세요.
2. DB에 묶인 함수 하나를 Fake로 단위 테스트해 보세요.
3. 외부 HTTP 호출 하나를 어댑터 클래스로 추출해 보세요.

## 정리 및 다음 단계

테스트 가능성은 설계를 비추는 거울입니다. 다음 글에서는 코드를 안전하게 바꾸는 기술, 즉 리팩토링의 기본 절차를 다룹니다.


## 코드 리뷰 체크리스트와 PR 작성 가이드(테스트 관점)

테스트 가능한 코드는 PR 단계에서 더 쉽게 검증됩니다. 아래 체크리스트는 작성자와 리뷰어가 함께 보는 기준입니다.

| 항목 | 작성자 확인 | 리뷰어 확인 | 기준 |
| --- | --- | --- | --- |
| 순수 로직 분리 | O | O | IO 없이 계산 검증 가능 |
| 의존성 주입 | O | O | 시간/HTTP/DB를 외부에서 주입 |
| 테스트 범위 | O | O | 핵심 분기 최소 1회 이상 검증 |
| 테스트 속도 | O | O | 단위 테스트는 빠르게 완료 |
| 경계 테스트 | O | O | 어댑터/통합 테스트 분리 |

체크리스트를 문서화하면 "테스트를 더 써라" 같은 모호한 요청이 줄고, 무엇을 어디까지 검증해야 하는지가 명확해집니다.

## 풀 리퀘스트 템플릿 예시

```python
PR_TEMPLATE = {
    "what": "무엇을 바꿨는지",
    "why": "왜 바꿨는지",
    "how_tested": [
        "unit: tests/test_order_policy.py",
        "integration: tests/test_payment_adapter.py",
    ],
    "risk": "실패 시 영향 범위",
    "rollback": "되돌림 절차",
}
```

실제 PR 본문은 Markdown으로 작성하더라도, 위 필드를 일관되게 채우는 습관이 중요합니다. 리뷰어는 코드 diff를 보기 전에 맥락과 위험을 먼저 파악해야 정확한 피드백을 줄 수 있습니다.

## 테스트 더블 선택 가이드

```python
class FakePaymentGateway:
    def __init__(self):
        self.charges = []

    def charge(self, user_id: str, amount: int) -> dict:
        self.charges.append((user_id, amount))
        return {"status": "ok", "amount": amount}


class SpyNotifier:
    def __init__(self):
        self.messages = []

    def send(self, email: str, body: str) -> None:
        self.messages.append((email, body))
```

Fake는 결과를 만들어 주는 대체 구현이고, Spy는 상호작용 기록을 검증하는 도구입니다. 테스트 의도에 맞는 더블을 선택해야 테스트가 읽기 쉬워집니다.

## 테스트 가능성 개선을 위한 PR 분할 전략

1. PR-1: 순수 함수 추출(동작 동일)
2. PR-2: 의존성 주입 적용(동작 동일)
3. PR-3: 테스트 추가 및 보강
4. PR-4: 기능 변경

위 순서를 지키면 리스크가 크게 줄어듭니다. 특히 "구조 변경 + 기능 추가"를 한 PR에 섞지 않는 것이 핵심입니다.

```python
def classify_test_layer(test_name: str) -> str:
    if "adapter" in test_name or "integration" in test_name:
        return "integration"
    return "unit"
```

테스트 레이어를 분류해 추세를 보면, 단위 테스트가 부족한지 통합 테스트가 과도한지 빠르게 판단할 수 있습니다.


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


## 테스트 가능성 진단표

테스트 가능한 코드 여부는 테스트 파일이 있는지보다 경계 분리가 되어 있는지로 판단합니다.

| 진단 항목 | 나쁜 신호 | 개선 방향 |
| --- | --- | --- |
| 시간 의존 | `datetime.now()` 직접 호출 | 시계 객체 주입 |
| 외부 호출 | 함수 본문에서 API/DB 직접 호출 | 어댑터 계층 분리 |
| 난수 의존 | 랜덤 결과를 바로 사용 | 시드 또는 생성기 주입 |
| 복합 책임 | 검증/계산/저장/알림 혼합 | 순수 함수 추출 |

## 전/후 데모: 의존성 주입으로 단위 테스트 가능하게 만들기

```python
# before
def issue_coupon(user_id):
    from datetime import datetime
    code = f"CP-{user_id}-{int(datetime.now().timestamp())}"
    return code


# after
class Clock:
    def now_ts(self) -> int:
        raise NotImplementedError


def issue_coupon(user_id: str, clock: Clock) -> str:
    return f"CP-{user_id}-{clock.now_ts()}"
```

## 테스트 더블 선택 가이드

| 상황 | 권장 더블 | 이유 |
| --- | --- | --- |
| 조회 결과 고정 | Stub | 입력-출력 검증 단순화 |
| 호출 여부 검증 | Spy | 상호작용 계약 확인 |
| 실패 시나리오 재현 | Fake | 운영과 유사한 흐름 검증 |

```python
class FakeClock(Clock):
    def __init__(self, fixed_ts: int):
        self.fixed_ts = fixed_ts

    def now_ts(self) -> int:
        return self.fixed_ts
```

## 테스트/린터 구성 예시

```toml
[tool.pytest.ini_options]
addopts = "-q --maxfail=1"
testpaths = ["tests"]

[tool.ruff.lint]
select = ["E", "F", "B", "PT"]
```

테스트 가능성은 설계의 부산물이 아니라 목표여야 합니다. 새 기능 PR에서 테스트 격리 수준을 함께 검토하면 회귀 결함을 체계적으로 줄일 수 있습니다.


## 심화 실습: 테스트 설계 워크플로

테스트 가능한 코드는 우연히 생기지 않습니다. 기능 설계 단계에서 테스트 경계를 먼저 그리는 습관이 필요합니다.

1. 순수 계산 영역과 외부 I/O 영역을 분리합니다.
2. 순수 영역은 단위 테스트, I/O 영역은 계약 테스트를 배치합니다.
3. 실패 시나리오를 정상 시나리오와 같은 수로 준비합니다.

```python
def compute_invoice_total(line_items: list[dict], discount_rate: float) -> int:
    subtotal = sum(item["unit_price_cents"] * item["quantity"] for item in line_items)
    return int(subtotal * (1 - discount_rate))
```

## 테스트 케이스 설계표

| 분류 | 예시 | 기대 결과 |
| --- | --- | --- |
| 정상 | 수량 2, 할인 10% | 계산값 정확 |
| 경계 | 수량 0, 할인 0% | 0 반환 |
| 오류 | 음수 수량 | 예외 발생 |

설계표를 먼저 작성하면 테스트 구현 속도가 빨라지고 누락 케이스가 줄어듭니다.


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

- **순수 로직과 부수 효과는 어떻게 분리해야 할까요?**
  - 본문의 기준은 테스트 가능한 코드를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **의존성 주입은 어떻게 테스트용 이음새를 만들까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Fake와 Spy는 각각 언제 쓰는 편이 좋을까요?**
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
- **테스트 가능한 코드 (현재 글)**
- 리팩토링 기초 (예정)
- 좋은 코드 리뷰 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Working Effectively with Legacy Code (M. Feathers)](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)
- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Mocks Aren't Stubs (Martin Fowler)](https://martinfowler.com/articles/mocksArentStubs.html)
- [Pytest — Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [Pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [Hexagonal architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/clean-code-101/ko)
Tags: Computer Science, CleanCode, Testability, Testing, DependencyInjection, Refactoring
