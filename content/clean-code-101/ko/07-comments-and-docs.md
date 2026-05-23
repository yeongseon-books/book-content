---
series: clean-code-101
episode: 7
title: "Clean Code 101 (7/10): 주석과 문서화"
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
  - Comments
  - Documentation
  - Docstring
  - Readability
seo_description: 코드가 스스로 설명하게 만드는 기법과 좋은 주석의 기준을 배웁니다. 코드로 표현하기 어려운 의도 주석과 docstring 활용법을 배웁니다.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (7/10): 주석과 문서화

주석은 친절해 보이지만, 잘못 쓰이면 가장 빨리 낡는 설명이 됩니다.

여기서는 코드가 스스로 설명해야 하는 부분과, 주석이나 문서가 꼭 맡아야 하는 부분을 구분해 보겠습니다.

![Clean Code 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/07/07-01-concept-at-a-glance.ko.png)
*Clean Code 101 7장 흐름 개요*
> 동작과 부스라기는 명낙한 짱조 모든 뷼거늤뻹제 채웰 나넸니다.

## 먼저 던지는 질문

- 언제 주석을 쓰지 않는 편이 더 좋을까요?
- 의도 주석과 경고 주석은 어떤 차이가 있을까요?
- Python docstring은 어떤 규칙으로 쓰는 편이 좋을까요?

## 왜 중요한가

주석은 쉽게 거짓말합니다. 코드는 수정되지만 주석은 그대로 남는 경우가 많기 때문입니다. 그래서 설명이 필요하다고 느껴질 때는 먼저 코드 구조와 이름을 고쳐서 설명량 자체를 줄일 수 있는지 봐야 합니다.

그렇다고 문서화가 불필요한 것은 아닙니다. 공개 API의 계약, 외부 시스템의 이상한 동작 배경, 호출자가 다칠 수 있는 경고는 코드만으로 충분히 표현되지 않는 경우가 많습니다. 핵심은 주석이 맡아야 할 역할을 좁고 분명하게 유지하는 것입니다.

## 한눈에 보는 개념

무언가를 설명해야 한다면, 먼저 코드를 고칠 수 있는지 보고 그다음에만 주석을 써야 합니다.

## 핵심 용어

- **Self-documenting code**: 이름과 구조만으로 의도가 드러나는 코드입니다.
- **Intent comment**: 코드가 왜 존재하는지 설명하는 주석입니다.
- **Docstring**: 함수나 클래스에 붙는 사용 계약 문서입니다.
- **TODO/FIXME**: 미래 작업을 남기는 표식이며, 추적 가능해야 합니다.
- **API doc**: 공개 인터페이스의 계약과 사용법입니다.

## 전/후 비교

**Before**

```python
# i를 1씩 증가
i = i + 1

# user list
def gu(): ...
```

**After**

```python
def get_active_users(): ...
```

설명 없는 주석 두 줄보다 좋은 이름 하나가 더 낫습니다. 주석을 지우는 가장 좋은 방법은 코드를 더 잘 쓰는 것입니다.

## 실전 적용: 유용한 문서화 다섯 단계

### 단계 1 — 의도 주석
```python
# 1_intent.py
# 결제 게이트웨이에서 본문에 오류가 있어서 200을 반환하는 경우가 있는데,
# 따라서 HTTP 상태 코드 대신 body.status를 썼습니다.
def is_paid(resp):
    return resp.json().get("status") == "PAID"
```

이런 주석은 코드가 표현하기 어려운 배경을 담습니다. 외부 시스템의 이상한 계약처럼 "왜 이렇게 했는지"가 핵심일 때 의미가 있습니다.

### 단계 2 — 경고 주석
```python
# 2_warning.py
# 주의: 이 기능은 IO를 수행합니다. 트랜잭션 내부에서 호출하지 마세요.
def upload_invoice(path): ...
```

호출자가 실제로 다칠 수 있는 위험은 코드 옆에서 바로 경고해야 합니다. 경고 주석은 친절함이 아니라 안전장치입니다.

### 단계 3 — Docstring

```python
# 3_doc.py
def discount(price: int, rate: float) -> int:
    """Return the price after applying a discount.

    Args:
        price: Integer price in cents.
        rate: Discount rate in [0, 1].

    Returns:
        Rounded integer price.

    Raises:
        ValueError: When rate is out of range.
    """
    if not 0 <= rate <= 1:
        raise ValueError("rate out of range")
    return int(price * (1 - rate))
```

공개 함수는 호출 계약을 분명히 남길 가치가 있습니다. 입력, 반환, 예외가 보이면 사용하는 사람의 추측 비용이 크게 줄어듭니다.

### 단계 4 — README 헤더
```markdown
<!-- 4_readme.md -->
# checkout-service

Payment domain service that responds within 5 seconds.

- Run: `make run`
- Test: `make test`
- Env vars: `GATEWAY_URL`, `SECRET_KEY`
```

새 기여자가 30초 안에 프로젝트를 이해할 수 있어야 좋은 README입니다. 첫 문단과 실행 방법이 가장 먼저 보이는 것이 중요합니다.

### 단계 5 — 담당자가 있는 TODO
```python
# 5_todo.py
# TODO(영선, 2026-06-01): 단순 재시도를 지수 백오프로 대체합니다.
def retry_simple(): ...
```

TODO는 언젠가 할 일이 아니라, 누가 언제까지 볼 것인지가 분명한 작업이어야 합니다. 익명 TODO는 거의 항상 영구 부채가 됩니다.

## 검증 방법

```bash
ruff check app/
python -m pytest -q tests/test_public_api_docs.py
```

**기대 결과**

- 주석 없이도 이름과 구조가 핵심 흐름을 설명해야 합니다.
- 공개 함수의 계약이 테스트와 문서 둘 다에서 맞아야 합니다.

## 실패하기 쉬운 지점

- 주석이 코드를 그대로 반복합니다.
- TODO에 담당자나 추적 링크가 빠져 영구 부채가 됩니다.

## 이 코드에서 먼저 봐야 할 점

- 코드는 "무엇"을, 주석은 "왜"를 설명합니다.
- docstring은 사용 계약을 분명하게 만듭니다.
- TODO는 추적 가능해야 합니다.

## 자주 하는 실수 5가지

1. **코드를 그대로 반복하는 주석 쓰기.** 정보가 없는 소음입니다.
2. **낡은 주석 방치하기.** 가장 위험한 거짓말이 됩니다.
3. **익명 TODO 남기기.** 끝나지 않는 부채가 됩니다.
4. **모든 함수에 형식적인 docstring 붙이기.** 정보량이 0이면 가치도 없습니다.
5. **주석에 비밀값이나 로컬 경로 남기기.** 보안과 이식성을 해칩니다.

## 실무에서는 이렇게 보입니다

좋은 팀은 공개 API에 docstring을 요구하고, 내부 코드에는 의도 주석만 제한적으로 허용합니다. TODO에는 이슈 링크나 담당자를 붙여서 코드와 작업 추적이 연결되도록 관리합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 주석을 쓰기 전에 이름과 구조를 먼저 고칩니다.
- "왜"만 주석으로 남깁니다.
- 공개 API의 계약은 분명히 적습니다.
- TODO에는 담당자와 날짜를 붙입니다.
- 코드 수정 시 낡은 주석도 함께 갱신합니다.

## 체크리스트

- [ ] 코드만으로 충분히 설명되는가?
- [ ] 주석이 "왜"를 설명하는가?
- [ ] 공개 함수에 docstring이 있는가?
- [ ] TODO에 담당자와 날짜가 있는가?
- [ ] 기존 주석이 아직도 정확한가?

## 연습 문제

1. 소음 주석 세 개를 지우고 이름을 더 좋게 바꿔 보세요.
2. 공개 함수 하나에 docstring을 추가해 보세요.
3. TODO 하나에 이슈 링크와 날짜를 붙여 보세요.

## 정리 및 다음 단계

좋은 주석은 적고 정확합니다. 다음 글에서는 코드베이스의 운명을 크게 좌우하는 테스트 가능성, 즉 테스트 가능한 코드를 다룹니다.

## 주석 vs 자기문서화 코드 비교 기준

좋은 주석은 적고 정확합니다. 더 좋은 코드는 주석이 거의 필요 없습니다. 아래 표는 언제 주석을 쓰고, 언제 코드 개선을 우선해야 하는지 구분하는 기준입니다.

| 상황 | 코드 개선 우선 | 주석 우선 | 판단 이유 |
| --- | --- | --- | --- |
| 변수명/함수명이 모호함 | O | X | 이름 개선이 영구적 해결 |
| 복잡한 외부 계약 우회 | X | O | "왜"를 코드만으로 표현 어려움 |
| 성능 최적화 트릭 사용 | X | O | 의도와 제약을 남겨야 안전 |
| TODO/FIXME 항목 | X | O | 추적 가능한 작업 메모 필요 |
| 공개 API 입력/반환 계약 | X | O(docstring) | 호출자 계약 문서화 필요 |

주석이 코드 동작을 그대로 설명한다면 제거 후보입니다. 반대로 외부 제약, 역사적 배경, 위험 경고를 전달한다면 남길 가치가 있습니다.

## 좋은 주석과 나쁜 주석 예시

```python
# 나쁜 주석: 코드와 동일한 정보를 반복합니다.

def add_one(value: int) -> int:
    # value에 1을 더한다.
    return value + 1
```

```python
# 좋은 주석: 왜 이런 구현을 택했는지 설명합니다.

def parse_gateway_status(response: dict) -> str:
    # 결제 라이선싱은 HTTP 200이어도 실패합니다.
    # 상태 코드는 참고하지 않고 본문 값을 우선 판단합니다.
    if response.get("error_code"):
        return "FAILED"
    return "PAID"
```

위 차이는 유지보수에서 크게 드러납니다. 나쁜 주석은 시간이 지나며 낡고, 좋은 주석은 의사결정 맥락을 보존합니다.

## 파이썬 문서 문자열 실무 규칙

```python
def calculate_refund_amount(total_cents: int, cancel_fee_rate: float) -> int:
    """환불 금액을 센트 단위로 계산합니다.

    Args:
        total_cents: 원 결제 금액(센트 단위)
        cancel_fee_rate: 취소 수수료 비율(0 이상 1 이하)

    Returns:
        수수료를 차감한 환불 금액(센트 단위)

    Raises:
        ValueError: 수수료 비율이 범위를 벗어난 경우
    """
    if not 0 <= cancel_fee_rate <= 1:
        raise ValueError("cancel_fee_rate must be in [0, 1]")

    refund_cents = int(total_cents * (1 - cancel_fee_rate))
    return max(refund_cents, 0)
```

docstring은 구현 설명이 아니라 계약 설명이어야 합니다. 즉 "어떻게"보다 "무엇을 받고 무엇을 돌려주며 어떤 예외가 가능한가"를 기록해야 합니다.

## 문서화 품질 체크 루틴

1. 코드만 읽고 함수 목적을 10초 안에 말할 수 있는가
2. 주석이 "왜"를 담고 있는가
3. TODO가 담당자/기한/이슈 링크를 갖는가
4. 공개 API의 docstring 계약이 테스트와 일치하는가

```python
def should_keep_comment(comment_text: str, explains_why: bool, duplicates_code: bool) -> bool:
    if duplicates_code:
        return False
    return explains_why and len(comment_text.strip()) > 0
```

이 기준을 코드 리뷰 체크리스트에 넣으면, 소음 주석은 줄고 핵심 문서화 품질은 올라갑니다.

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

## 주석 품질 판정표

주석은 "코드를 설명"할 때보다 "코드로 표현할 수 없는 의사결정"을 기록할 때 가치가 큽니다. 아래 기준으로 주석을 평가하면 품질이 안정됩니다.

| 주석 유형 | 좋은 예 | 나쁜 예 |
| --- | --- | --- |
| 의도 설명 | 특정 제약 때문에 현재 구현을 택한 이유 | 코드 문장을 그대로 반복 |
| 경고 | 트랜잭션/성능/보안 위험을 명시 | 막연한 "주의" 문장 |
| TODO | 담당자, 기한, 후속 조건 포함 | 소유자 없는 TODO 누적 |
| 문서 링크 | ADR/이슈 번호와 연결 | 출처 없는 주장 |

## 전/후 데모: 주석보다 이름과 구조로 설명하기

```python
# before
def p(a, b):
    # 사용자가 구매할 수 있습니다.
    if a and b > 0:
        return True
    return False

# after
def can_purchase(is_active_user: bool, stock_quantity: int) -> bool:
    return is_active_user and stock_quantity > 0
```

전/후 비교에서 보듯이 주석이 없어도 이름만으로 의도가 드러나는 코드가 유지보수에 유리합니다. 주석은 마지막 수단이어야 합니다.

## 문서화 루틴 예시

1. PR 설명에 What/Why/How/Risk를 고정 템플릿으로 작성합니다.
2. 공개 API 변경 시 README와 호출 예제를 같은 PR에서 갱신합니다.
3. 운영 영향이 있는 변경은 ADR 링크를 포함합니다.

```markdown
## 변경 요약
- What: 주문 취소 정책을 상태 기반으로 재구성
- Why: 분기 중복 제거와 정책 오해 방지
- How: 전략 객체 도입 + 기존 API 시그니처 유지
- Risk: 레거시 호출자에서 상태 문자열 오타 가능
```

## 린터 예시: 문서 문자열 최소 기준

```toml
[tool.ruff.lint]
select = ["D", "E", "F", "B"]
ignore = ["D203", "D213"]
```

문서 문자열 규칙을 자동화하면 함수 수준 문서 누락이 초기에 발견됩니다. 이 과정은 문서 품질의 균질화를 돕습니다.

## 심화 실습: 문서 부채 상환 루틴

문서 품질을 유지하려면 기능 개발과 같은 리듬으로 문서 점검이 이루어져야 합니다. 월 1회 대청소보다 주간 루틴이 더 효과적입니다.

| 루틴 | 주기 | 담당 | 출력물 |
| --- | --- | --- | --- |
| API 사용 예시 검증 | 매주 | 기능 담당자 | 실행 가능한 예시 코드 |
| 오래된 TODO 정리 | 매주 | 리뷰어 | 제거/연장 기록 |
| README 구조 점검 | 격주 | 모듈 오너 | 최신 아키텍처 다이어그램 |

```markdown
### TODO 관리 규칙
- 담당자 없는 TODO 금지
- 만료일 없는 TODO 금지
- 만료 후 자동 이슈 전환
```

문서 부채를 기술 부채처럼 추적하면 신규 멤버 온보딩 속도가 빨라지고, 장애 대응 시 의사결정 시간이 줄어듭니다.

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

- **언제 주석을 쓰지 않는 편이 더 좋을까요?**
  - 본문의 기준은 주석과 문서화를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **의도 주석과 경고 주석은 어떤 차이가 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Python docstring은 어떤 규칙으로 쓰는 편이 좋을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Clean Code 101 (1/10): Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): 이름 짓기](./02-naming.md)
- [Clean Code 101 (3/10): 함수 작게 만들기](./03-small-functions.md)
- [Clean Code 101 (4/10): 조건문 줄이기](./04-simplifying-conditionals.md)
- [Clean Code 101 (5/10): 중복 제거](./05-removing-duplication.md)
- [Clean Code 101 (6/10): 오류 처리](./06-error-handling.md)
- **주석과 문서화 (현재 글)**
- 테스트 가능한 코드 (예정)
- 리팩토링 기초 (예정)
- 좋은 코드 리뷰 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Clean Code (Ch. 4 Comments)](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide — Comments](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Write the Docs — Documentation Guide](https://www.writethedocs.org/guide/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/clean-code-101/ko)
Tags: Computer Science, CleanCode, Comments, Documentation, Docstring, Readability
