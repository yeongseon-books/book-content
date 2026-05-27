---
series: clean-code-101
episode: 2
title: "Clean Code 101 (2/10): 이름 짓기"
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
  - Naming
  - Readability
  - Refactoring
  - SoftwareEngineering
seo_description: 좋은 이름의 신호와 검색 가능성, 도메인 용어 활용법을 배웁니다. 이름만으로 의도가 전달되게 고쳐 가독성과 유지보수성을 높이는 방법을 익힙니다.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (2/10): 이름 짓기

코드에서 가장 자주 읽히는 것은 로직보다 이름입니다.

이 글은 Clean Code 101 시리즈의 2번째 글입니다.

여기서는 좋은 이름이 왜 주석을 줄이고 검색 비용을 낮추는지, 그리고 변수·함수·클래스 이름을 어떻게 다르게 다뤄야 하는지 정리하겠습니다.

![Clean Code 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/02/02-01-concept-at-a-glance.ko.png)
*Clean Code 101 2장 흐름 개요*
> 좋은 이름은 주석이 필요 없게 만듭니다.

## 먼저 던지는 질문

- 좋은 이름을 판단할 때 어떤 신호를 봐야 할까요?
- 변수 이름과 함수 이름, 클래스 이름은 무엇이 다를까요?
- 도메인 용어를 코드 안으로 어떻게 자연스럽게 가져올 수 있을까요?

## 왜 중요한가

이름은 코드의 가장 작은 단위이면서도 가장 오래 남는 설계 결정입니다. 한 번 잘못 붙인 이름은 변수 하나를 넘어 함수, 문서, PR 대화, 심지어 팀의 공통 용어까지 오염시킵니다.

반대로 좋은 이름은 호출 지점에서 이미 많은 설명을 끝냅니다. 검색도 쉬워지고, 리뷰도 빨라지고, 주석도 줄어듭니다. 그래서 이름 짓기는 사소한 스타일 문제가 아니라 유지보수성의 출발점입니다.

## 한눈에 보는 개념

이름은 의도를 보이게 만들고, 그 의도는 검색과 읽기와 문서화를 동시에 돕습니다.

## 핵심 용어

- **Intention-revealing**: 무엇을 왜 하는지 이름만으로 드러나는 상태입니다.
- **Searchable**: 한 번의 grep으로 정확히 찾을 수 있는 이름입니다.
- **Pronounceable**: 회의나 리뷰에서 자연스럽게 말할 수 있는 이름입니다.
- **Domain term**: 비즈니스에서 쓰는 단어를 코드에도 그대로 쓰는 방식입니다.
- **Length budget**: 짧음보다 정확성을 우선하는 길이 감각입니다.

## 전/후 비교

**Before**

```python
d = 86400  # ?
```

**After**

```python
SECONDS_PER_DAY = 86400
```

상수 하나도 이름이 붙는 순간 의미를 가집니다. 좋은 이름은 값을 설명문으로 바꾸지 않고도 맥락을 전달합니다.

## 실전 적용: 이름을 개선하는 다섯 단계

### 단계 1 — 의도 드러내기
```python
# 1_intent.py
def f(x): return x[0]            # of what?
def first_completed_order(orders): return orders[0]
```

호출 지점에서 바로 이해되는 이름이 좋습니다. 함수 본문보다 이름이 먼저 읽힌다는 사실을 항상 기억해야 합니다.

### 단계 2 — Searchable

```python
# 2_search.py
TAX = 0.08                       # used where? unclear
DEFAULT_SALES_TAX_RATE = 0.08
```

검색 가능한 이름은 나중의 분석 비용을 줄입니다. 너무 짧거나 흔한 이름은 찾는 순간부터 비용을 만듭니다.

### 단계 3 — 도메인 용어
```python
# 3_domain.py
def calc(items): ...             # domain lost
def calculate_invoice_subtotal(line_items): ...
```

코드가 비즈니스와 다른 단어를 쓰기 시작하면 대화가 꼬입니다. 도메인 언어를 그대로 들여오면 사용자와 개발자의 문맥이 맞춰집니다.

### 단계 4 — 부정문 피하기
```python
# 4_negative.py
if not is_not_empty(x): ...      # double negative
if is_empty(x): ...
```

이중 부정은 읽는 순간 사고를 한 번 더 요구합니다. 긍정형 표현이 대개 더 빠르고 덜 위험합니다.

### 단계 5 — 간결함과 정확성의 균형
```python
# 5_balance.py
i, j, k                          # short loops are fine
customer_balance_cents           # domain names can be long
```

좁은 범위에서는 짧아도 되지만, 넓은 범위에서는 정확해야 합니다. 이름 길이는 미학이 아니라 범위와 책임에 대한 판단입니다.

## 검증 방법

```bash
ruff check app/ --select N
python -m pytest -q tests/test_naming_examples.py
```

**기대 결과**

- 축약어와 일관성 없는 명명 규칙이 먼저 드러납니다.
- 이름을 바꾼 뒤에도 테스트가 그대로 초록이어야 합니다.

## 실패하기 쉬운 지점

- 타입 이름만 바꾸고 도메인 용어는 그대로 놓칩니다.
- 리네임 뒤 호출 지점 전체를 함께 검증하지 않습니다.

## 이 코드에서 먼저 봐야 할 점

- 이름은 호출 지점에서 의미를 만듭니다.
- 검색 가능성은 미래의 분석 비용을 줄입니다.
- 도메인 용어는 사용자와 개발자 사이의 번역 비용을 없앱니다.

## 자주 하는 실수 5가지

1. **`data`, `info`, `obj` 같은 이름 쓰기.** 정보가 거의 없습니다.
2. **과한 축약어 사용하기.** `usrCtxMgr` 같은 이름은 읽는 비용만 올립니다.
3. **숫자 접미사 붙이기.** `process2`, `process3`는 의미를 설명하지 못합니다.
4. **타입을 이름에 넣기.** `user_dict`보다 `user`가 더 좋습니다.
5. **거짓말하는 이름 쓰기.** `getXxx`가 실제로 값을 바꾸면 신뢰가 무너집니다.

## 실무에서는 이렇게 보입니다

성숙한 팀은 저장소 안에 도메인 용어집을 두고, PR에서 용어 일관성을 함께 리뷰합니다. 한 글자 변수는 루프 안처럼 좁은 범위에서만 허용하고, 축약어는 허용 목록을 두는 식으로 관리하기도 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 이름은 문서의 절반입니다.
- 짧음보다 정확함이 우선입니다.
- 검색 가능성이 미래 비용을 좌우합니다.
- 도메인 용어는 그대로 코드로 들어와야 합니다.
- 거짓말하는 이름은 작은 사기가 됩니다.

## 체크리스트

- [ ] 이름이 의도를 드러내는가?
- [ ] grep으로 정확히 찾을 수 있는가?
- [ ] 도메인 용어를 사용했는가?
- [ ] 부정형과 이중 부정을 피했는가?
- [ ] 범위에 맞는 길이인가?

## 연습 문제

1. `data`/`info`/`obj` 같은 이름 다섯 개를 찾아 바꿔 보세요.
2. 축약어 다섯 개를 풀어서 더 읽기 쉽게 만들어 보세요.
3. 한 페이지짜리 도메인 용어집을 만들어 보세요.

## 정리 및 다음 단계

이름 짓기는 가독성에서 가장 레버리지가 큰 도구입니다. 다음 글에서는 그 이름이 가리키는 단위를 더 작게 만드는 방법, 즉 작은 함수를 다룹니다.

## 변수·함수·클래스 이름 규칙을 실제로 적용하기

이름은 형식이 아니라 계약입니다. 호출자가 이름을 읽는 순간 무엇을 기대해야 하는지가 정해집니다. 아래 표는 실무에서 가장 자주 쓰는 이름 규칙을 정리한 것입니다.

| 대상 | 좋은 규칙 | 피해야 할 패턴 | 예시 |
| --- | --- | --- | --- |
| 변수 | 값의 의미를 드러내기 | `data`, `tmp`, `obj` 남용 | `invoice_total_cents` |
| 불리언 | 질문형/상태형으로 명확히 | 이중 부정 | `is_active`, `has_permission` |
| 함수 | 동사 + 도메인 목적 | `do_stuff`, `handle_data` | `calculate_invoice_total` |
| 클래스 | 역할 중심 명사 | 기술 구현 세부를 이름에 노출 | `InvoiceRepository` |
| 컬렉션 | 복수형 + 요소 의미 | 단수형 혼용 | `active_users`, `line_items` |
| 상수 | 단위 포함한 대문자 | 단위 없는 매직넘버 | `DEFAULT_TIMEOUT_SECONDS` |

규칙의 핵심은 일관성입니다. 같은 도메인 개념을 파일마다 다르게 부르면 검색성과 협업 속도가 급격히 떨어집니다. 따라서 용어집을 먼저 합의하고, 이름 변경은 한 번에 넓게 수행하는 편이 안전합니다.

## 전/후 비교 비교: 이름이 의도를 바꾸는 순간

```python
# before

def p(u, o, c):
    if u and o:
        t = 0
        for i in o:
            t += i["p"] * i["q"]
        if c:
            t -= 1000
        return t
    return None

# after
from typing import Iterable

def calculate_order_total(user_id: str, line_items: Iterable[dict], has_coupon: bool) -> int | None:
    if not user_id or not line_items:
        return None

    subtotal_cents = 0
    for line_item in line_items:
        subtotal_cents += line_item["unit_price_cents"] * line_item["quantity"]

    if has_coupon:
        subtotal_cents -= 1000

    return subtotal_cents
```

두 버전은 로직이 거의 같지만, 후자는 호출자에게 훨씬 많은 정보를 제공합니다. 어떤 단위인지, 어떤 값이 기대되는지, 반환 조건이 무엇인지가 이름에서 먼저 읽힙니다. 이 차이는 디버깅 시간과 리뷰 속도에 그대로 반영됩니다.

## 이름 변경 절차와 안전 장치

리네임은 작아 보여도 영향 범위가 넓습니다. 아래 절차를 지키면 위험을 크게 줄일 수 있습니다.

1. 후보 이름의 도메인 의미를 먼저 정의합니다.
2. 참조 검색으로 영향 파일을 확인합니다.
3. 공개 API인지 내부 구현인지 구분합니다.
4. 테스트를 먼저 초록으로 고정합니다.
5. 한 번에 한 개념씩 리네임하고 즉시 재검증합니다.

```python
def normalize_variable_name(raw_name: str) -> str:
    cleaned = raw_name.strip().lower().replace(" ", "_")
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned
```

위 유틸리티처럼 이름 정규화 규칙을 도구화하면 대규모 리네임 작업에서도 일관성을 유지하기 쉽습니다. 결국 이름 품질은 개인 취향보다 팀 합의와 자동화 수준에 크게 좌우됩니다.

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

## 명명 규칙 표준안: 팀 합의를 코드로 고정하기

명명은 개인 취향이 아니라 팀의 공유 계약입니다. 아래 표준안을 저장소 루트 문서와 PR 템플릿에 함께 두면 리뷰 기준이 빠르게 안정됩니다.

| 구분 | 권장 패턴 | 금지 패턴 | 예시 |
| --- | --- | --- | --- |
| 불리언 | `is_`, `has_`, `can_` 접두 | `flag`, `status` 단독 사용 | `has_payment_method` |
| 단위 포함 수치 | 단위를 suffix에 명시 | 단위 없는 숫자 이름 | `retry_interval_seconds` |
| 컬렉션 | 복수형 + 요소 의미 | `list`, `arr`, `data` | `overdue_invoices` |
| 파생값 | 계산 의미를 드러내는 접미 | 원본과 동일한 이름 재사용 | `normalized_email` |
| 임시 변수 | 블록 단위 목적 명시 | `tmp`, `x`, `v2` | `next_status` |

## 함수 추출과 이름 재설계 동시 적용 데모

```python
# before
def run(a, b, c):
    if a and b and c > 0:
        return b * c * 0.9
    return 0

# after
def calculate_discounted_total(has_membership: bool, item_price_cents: int, quantity: int) -> int:
    if not is_discount_eligible(has_membership, item_price_cents, quantity):
        return 0
    return int(item_price_cents * quantity * 0.9)

def is_discount_eligible(has_membership: bool, item_price_cents: int, quantity: int) -> bool:
    return has_membership and item_price_cents > 0 and quantity > 0
```

이 데모에서 핵심은 함수를 쪼갠 행위보다 이름이 만든 계약입니다. 호출자는 구현을 몰라도 입력 의미를 이해할 수 있고, 변경 시 영향 범위를 빠르게 추적할 수 있습니다.

## 도메인 용어 테이블 예시

| 사용자 표현 | 코드 용어 | 피해야 할 대체어 |
| --- | --- | --- |
| 주문 합계 | `order_total_cents` | `sum`, `total_value` |
| 결제 완료 | `payment_confirmed` | `done`, `ok` |
| 배송 준비 | `ready_for_shipment` | `prepared`, `state3` |
| 할인 쿠폰 | `discount_coupon` | `dc`, `ticket` |

도메인 용어집을 코드와 분리해 두는 것보다, 테스트 이름과 API 스키마에도 같은 용어를 넣는 것이 더 효과적입니다. 용어가 레이어마다 일치하면 장애 보고 문장도 짧아집니다.

## 린터로 명명 규칙 강제하기

```toml
# pyproject.toml
[tool.ruff.lint]
select = ["E", "F", "N", "B"]

[tool.ruff.lint.pep8-naming]
ignore-names = ["setUp", "tearDown"]
```

명명 규칙을 린터에 넣으면 리뷰어가 반복적으로 "이름을 바꾸세요"라고 말할 필요가 없습니다. 리뷰 코멘트는 설계 의사결정과 위험 평가에 집중하게 됩니다.

## 심화 실습: 명명 규칙 마이그레이션 계획

대규모 저장소에서 이름 개선은 한 번에 끝낼 수 없습니다. 영역별로 우선순위를 나누어 점진적으로 진행해야 리스크가 작습니다. 보통은 공개 API, 핵심 도메인, 보조 유틸리티 순서로 진행합니다.

| 우선순위 | 대상 | 기준 | 완료 조건 |
| --- | --- | --- | --- |
| 1 | 공개 API | 외부 호출자가 의존 | 변경 로그/호환성 확인 |
| 2 | 핵심 도메인 | 기능 변경이 잦음 | 용어집과 코드 일치 |
| 3 | 내부 유틸 | 영향 범위 제한 | 테스트 통과 |

```python
RENAME_MAP = {
    "calc": "calculate_invoice_total",
    "usr": "user",
    "amt": "amount_cents",
    "dt": "created_at",
}

def suggest_renamed_identifier(identifier: str) -> str:
    return RENAME_MAP.get(identifier, identifier)
```

이런 매핑은 자동 치환 도구의 입력값으로도 사용할 수 있습니다. 단, 자동 치환 뒤에는 의미 검증 리뷰를 반드시 넣어야 합니다. 문자열 치환은 문맥을 이해하지 못하기 때문입니다.

## 명명 리뷰 코멘트 예시

- 관찰: `result`가 세 단계에서 서로 다른 의미로 재사용됩니다.
- 위험: 디버깅 시 값 추적이 어려워 오해성 버그가 발생할 수 있습니다.
- 제안: `validated_payload`, `persisted_order`, `response_body`처럼 단계별 의미를 분리합니다.

이 방식은 공격적인 표현을 피하면서도 변경 이유를 분명하게 전달합니다. 리뷰 언어도 코드 품질의 일부입니다.

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

- **좋은 이름을 판단할 때 어떤 신호를 봐야 할까요?**
  - 이 글에서는 intention-revealing, searchable, pronounceable, domain term이라는 네 가지 신호를 중심으로 이름을 판단했습니다. `SECONDS_PER_DAY`, `DEFAULT_SALES_TAX_RATE`, `calculate_invoice_subtotal`처럼 뜻과 검색성이 동시에 살아 있는 이름이 기준입니다.
- **변수 이름과 함수 이름, 클래스 이름은 무엇이 다를까요?**
  - 변수는 `invoice_total_cents`처럼 값의 의미와 단위를 드러내야 하고, 함수는 `calculate_order_total`처럼 동사와 목적을 함께 담아야 하며, 클래스는 `InvoiceRepository`처럼 역할 중심 명사여야 합니다. 같은 명명 규칙을 모든 대상에 똑같이 적용하는 것이 아니라, 호출자에게 무엇을 약속하는지에 따라 기준이 달라집니다.
- **도메인 용어를 코드 안으로 어떻게 자연스럽게 가져올 수 있을까요?**
  - 글의 도메인 용어 테이블처럼 사용자 표현과 코드 용어를 1:1로 맞추고, `order_total_cents`, `payment_confirmed`, `discount_coupon` 같은 이름을 테스트와 API 스키마에도 같은 단어로 쓰는 방식이 효과적입니다. 이렇게 맞춰 두면 회의, PR, 장애 대응에서 번역 비용이 줄고 이름 변경의 범위도 더 분명해집니다.

<!-- toc:begin -->
## 시리즈 목차

- [Clean Code 101 (1/10): Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- **이름 짓기 (현재 글)**
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

- [Clean Code (Ch. 2 Meaningful Names)](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Domain-Driven Design — Eric Evans](https://www.oreilly.com/library/view/domain-driven-design-tackling/0321125215/)
- [Google Style Guide — Naming](https://google.github.io/styleguide/pyguide.html#316-naming)
- [PEP 8 — Naming Conventions](https://peps.python.org/pep-0008/#naming-conventions)
- [Ruff pep8-naming rules](https://docs.astral.sh/ruff/rules/#pep8-naming-n)
- [PEP 8 naming conventions](https://peps.python.org/pep-0008/#naming-conventions)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/clean-code-101/ko)
Tags: Computer Science, CleanCode, Naming, Readability, Refactoring, SoftwareEngineering
