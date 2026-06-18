---
title: "바이브코딩을 위한 클린 코드 (2/10): AI가 만든 변수명이 a, b, temp"
series: clean-code-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- CleanCode
- AI코딩
- 이름짓기
- 가독성
- Naming
seo_description: "바이브코딩 시대, AI가 생성한 a, b, temp 같은 변수명을 의미 있는 이름으로 바꾸는 방법과 좋은 이름을 요청하는 프롬프트 전략을 설명합니다."
---

# 바이브코딩을 위한 클린 코드 (2/10): AI가 만든 변수명이 a, b, temp

이 글은 바이브코딩을 위한 클린 코드 시리즈의 2번째 글입니다.

AI에게 할인율을 적용하는 함수를 만들어달라고 했습니다. 받은 코드를 보니 이랬습니다.

```python
def p(u, o, c):
    if u and o:
        t = 0
        for i in o:
            t += i["p"] * i["q"]
        if c:
            t -= 1000
        return t
    return None
```

돌아갑니다. 테스트도 통과합니다. 그런데 이틀 뒤에 "멤버십 할인도 추가해달라"는 요청이 왔을 때, 이 코드를 다시 열고 `u`가 뭔지, `i["p"]`가 가격인지 수량인지 파악하는 데 10분이 걸렸습니다. `c`가 쿠폰인지 카드인지도 맥락을 모두 읽어봐야 알 수 있었습니다.

이름은 코드에서 가장 먼저 읽히는 것입니다. 그런데 AI는 "동작"에 최적화되어 있어서 이름의 의미보다 코드의 압축성을 선택하는 경향이 있습니다. 결과적으로 AI가 만든 코드는 동작하지만, 읽는 데 드는 비용이 숨어 있습니다.

좋은 이름은 주석을 없애줍니다. `u`에 대한 주석을 달 필요 없이, `user_id`라고 쓰면 됩니다. 이름 하나가 주석 한 줄을 대신하고, 그 이름이 함수와 클래스와 테스트 전체에 퍼지면 코드베이스 전체가 읽기 쉬워집니다.

> AI가 만든 이름은 코드가 동작하게 만들지만, 좋은 이름은 코드를 다음에도 수정할 수 있게 만듭니다.

---

## 이 글에서 다룰 문제
- AI가 생성한 `a`, `b`, `temp` 같은 이름을 언제, 어떻게 고쳐야 할까요?
- 변수 이름과 함수 이름은 어떤 기준으로 달라야 할까요?
- 도메인 용어를 코드에 반영하면 무엇이 달라질까요?
- 이름을 바꿀 때 안전하게 진행하는 순서는 무엇일까요?
- AI에게 처음부터 좋은 이름을 만들도록 요청하는 방법은 무엇일까요?

---

## AI가 나쁜 이름을 만드는 이유

AI는 코드를 생성할 때 입력 토큰을 줄이고 출력을 빠르게 만드는 방향으로 최적화됩니다. 짧은 이름은 그 최적화의 부산물입니다. 또한 AI는 다음 토큰을 예측하는 방식으로 동작하기 때문에 "이 변수가 3개월 뒤에 어떻게 읽힐 것인가"를 고려하지 않습니다.

그래서 AI 코드를 받은 뒤 이름을 정리하는 것은 받는 사람의 몫입니다.

### 의도를 드러내는 이름

```python
# AI가 자주 만드는 패턴
d = 86400

# 클린 코드 버전
SECONDS_PER_DAY = 86400
```

상수에 이름이 붙는 순간 의미가 생깁니다. 코드를 읽는 사람이 86400이 초인지, 밀리초인지 계산할 필요가 없습니다.

### 검색 가능한 이름

```python
# AI 버전 - 검색이 어려움
TAX = 0.08

# 클린 코드 버전 - 검색 가능
DEFAULT_SALES_TAX_RATE = 0.08
```

`TAX`로 검색하면 tax라는 단어가 들어간 모든 코드가 걸립니다. `DEFAULT_SALES_TAX_RATE`는 정확히 이 상수를 찾아줍니다.

### 도메인 용어를 그대로 사용

```python
# AI 버전 - 도메인 정보 손실
def calc(items):
    ...

# 클린 코드 버전 - 도메인 명확
def calculate_invoice_subtotal(line_items):
    ...
```

비즈니스에서 "인보이스 소계"라고 부르는 것을 코드에서 `calc`라고 부르면, 코드와 비즈니스 언어 사이에 번역 비용이 생깁니다.

## Before / After

```python
# AI가 생성한 코드
def p(u, o, c):
    if u and o:
        t = 0
        for i in o:
            t += i["p"] * i["q"]
        if c:
            t -= 1000
        return t
    return None
```

```python
# 이름을 정리한 버전
from typing import Iterable

def calculate_order_total(
    user_id: str,
    line_items: Iterable[dict],
    has_coupon: bool
) -> int | None:
    if not user_id or not line_items:
        return None

    subtotal_cents = 0
    for line_item in line_items:
        subtotal_cents += line_item["unit_price_cents"] * line_item["quantity"]

    if has_coupon:
        subtotal_cents -= 1000

    return subtotal_cents
```

로직은 동일하지만, 두 번째 버전은 함수 시그니처만 읽어도 무엇을 받고 무엇을 돌려주는지 바로 알 수 있습니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `data`, `info`, `obj` 사용 | 아무 정보가 없음 | 구체적인 도메인 용어 사용 |
| 단일 문자 변수 함수 전체에 사용 | 루프 밖에서는 의미 불명확 | 좁은 범위에서만 허용 |
| `result`를 여러 단계에서 재사용 | 디버깅 시 추적 불가 | 단계별 이름 분리 |
| 불리언에 `flag`, `status` 사용 | is_, has_ 없이 true/false 해석 불명확 | `is_active`, `has_coupon` 형태 사용 |
| 타입을 이름에 포함 | `user_dict`보다 `user`가 더 좋음 | 의미 중심으로 이름 짓기 |

## AI에게 클린 코드 요청하는 팁

```
프롬프트 예시:
"주문 합계를 계산하는 함수를 만들어줘.
이름 규칙:
- 변수명은 단위를 포함할 것 (예: amount_cents, timeout_seconds)
- 불리언은 is_ 또는 has_ 로 시작할 것
- 컬렉션은 복수형으로 작성할 것 (예: line_items, users)
- 함수명은 동사로 시작할 것 (예: calculate_, validate_, create_)"
```

이 프롬프트 패턴을 습관화하면 AI가 만드는 이름의 품질이 눈에 띄게 올라갑니다.

## 운영 체크리스트
- [ ] 이름이 의도를 드러내는가?
- [ ] 단위나 단위가 이름에 포함되어 있는가?
- [ ] grep으로 정확히 찾을 수 있는가?
- [ ] 도메인 용어를 사용했는가?
- [ ] 부정형과 이중 부정을 피했는가?
- [ ] 범위에 맞는 길이인가?

## 처음 질문으로 돌아가기

- **AI가 생성한 나쁜 이름을 언제 고쳐야 할까요?**
  코드를 받은 직후가 가장 좋습니다. 시간이 지날수록 나쁜 이름이 다른 코드에 퍼져 수정 범위가 커집니다.

- **이름을 바꿀 때 안전하게 진행하는 순서는?**
  테스트를 먼저 초록으로 고정하고, 한 번에 한 개념씩 이름을 바꾸고, 바꿀 때마다 테스트를 다시 실행합니다.

- **도메인 용어를 코드에 반영하면 무엇이 달라질까요?**
  비즈니스 회의와 코드 리뷰에서 같은 단어를 쓸 수 있게 됩니다. 번역 비용이 사라집니다.

## 정리

AI가 만든 이름은 대부분 동작에는 문제가 없지만 읽기에는 비용이 생깁니다. 이름을 정리하는 것은 AI 코드를 받은 뒤 가장 먼저, 가장 쉽게 할 수 있는 클린 코드 작업입니다. 다음 글에서는 AI가 만든 100줄짜리 함수를 어떻게 쪼개는지 다룹니다.

## 참고 자료
### 공식 문서
- [Clean Code by Robert C. Martin](https://www.oreilly.com/library/view/clean-code/9780136083238/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
### 관련 시리즈
- [Software Design 101](../../software-design-101/ko/)
- [Testing 101](../../testing-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 클린 코드 (1/10): AI 코드는 돌아가지만 읽기 어렵다](./01-what-is-clean-code.md)
- **바이브코딩을 위한 클린 코드 (2/10): AI가 만든 변수명이 a, b, temp (현재 글)**
- [바이브코딩을 위한 클린 코드 (3/10): AI가 100줄짜리 함수를 만들었다](./03-functions.md)
- [바이브코딩을 위한 클린 코드 (4/10): AI가 중첩 if를 5단계로 만들었다](./04-conditionals.md)
- [바이브코딩을 위한 클린 코드 (5/10): AI가 같은 코드를 3곳에 복붙했다](./05-dry.md)
- [바이브코딩을 위한 클린 코드 (6/10): AI가 except: pass를 넣었다](./06-error-handling.md)
- [바이브코딩을 위한 클린 코드 (7/10): AI가 주석을 잔뜩 넣었는데 코드와 안 맞다](./07-comments.md)
- [바이브코딩을 위한 클린 코드 (8/10): AI가 만든 코드를 테스트하기 어렵다](./08-testable-code.md)
- [바이브코딩을 위한 클린 코드 (9/10): AI 코드를 리팩터링하는 방법](./09-refactoring.md)
- [바이브코딩을 위한 클린 코드 (10/10): AI 코드를 리뷰하는 방법](./10-code-review.md)
<!-- toc:end -->
Tags: 바이브코딩, CleanCode, AI코딩, 이름짓기, 가독성, Naming
