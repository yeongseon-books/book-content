---
title: "바이브코딩을 위한 클린 코드 (9/10): AI 코드를 리팩터링하는 방법"
series: clean-code-101
episode: 9
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
- 리팩터링
- 레거시코드
- 코드개선
seo_description: "바이브코딩 시대, AI가 생성한 코드를 안전하게 리팩터링하는 단계별 방법과 기능 변경 없이 구조를 개선하는 실용적인 기법을 설명합니다."
---

# 바이브코딩을 위한 클린 코드 (9/10): AI 코드를 리팩터링하는 방법

이 글은 바이브코딩을 위한 클린 코드 시리즈의 9번째 글입니다.

AI로 프로젝트를 빠르게 만들다 보면 어느 순간 코드베이스 전체가 "건드리기 무서운 상태"가 됩니다. 각 AI 대화마다 독립적으로 기능을 추가했더니 함수들이 서로 얽혀 있고, 변수명은 일관성이 없고, 같은 로직이 여러 곳에 있습니다. "전체를 다시 짜야 할까?" 하는 생각이 듭니다.

리팩터링은 전체를 다시 쓰는 것이 아닙니다. 외부 동작은 그대로 유지하면서 내부 구조를 조금씩 개선하는 작업입니다. 핵심은 "작은 단위로, 매 단계마다 테스트를 통과시키면서" 진행하는 것입니다.

AI 코드를 리팩터링할 때의 특별한 도전은 코드가 무엇을 하는지 완전히 파악하기 전에 시작해야 하는 경우가 많다는 것입니다. AI가 생성한 코드는 테스트도 없고, 명확한 경계도 없고, 어떤 엣지 케이스를 처리하는지 주석도 없습니다. 이럴 때는 "이해한 뒤 고친다"가 아니라 "현재 동작을 먼저 고정한 뒤 조금씩 개선한다"는 접근이 현실적입니다.

> 리팩터링은 초록 테스트에서 다음 초록 테스트로 이동하는 작은 걸음을 반복하는 작업입니다.

---

## 이 글에서 다룰 문제
- AI 코드를 리팩터링하기 전에 먼저 해야 할 것은 무엇인가요?
- 리팩터링과 기능 추가를 왜 같은 커밋에 섞으면 안 되나요?
- Fowler 리팩터링 카탈로그의 핵심 기법은 무엇인가요?
- 테스트 없이 리팩터링을 시작하면 왜 위험한가요?
- AI에게 리팩터링을 요청할 때 어떻게 해야 안전한가요?

---

## AI 코드 리팩터링의 도전

AI가 만든 코드를 리팩터링할 때 일반 레거시 코드보다 어려운 점이 있습니다.

- 테스트가 없는 경우가 많습니다
- 함수 경계가 명확하지 않습니다
- 왜 그렇게 구현했는지 배경이 없습니다
- 한 번에 너무 많이 바꾸려는 유혹이 생깁니다

### 1단계: 현재 동작을 테스트로 고정

리팩터링의 첫 번째 단계는 현재 동작을 테스트로 고정하는 것입니다. 이것을 "특성화 테스트(Characterization Test)"라고 합니다.

```python
# AI가 만든 코드 - 이해하기 전에 테스트 먼저
def order_total(o):
    s = 0
    for it in o.items:
        s += it.price * it.qty
    if o.coupon: s -= 10
    if o.member: s = s * 0.9
    return s

# 먼저 현재 동작을 테스트로 고정
def test_order_total_current_behavior():
    order = make_order(items=[(100, 2)], coupon=True, member=True)
    assert order_total(order) == 171  # 현재 동작을 그대로 캡처
```

이제 리팩터링 후에도 이 테스트가 통과하면 동작이 바뀌지 않았다는 것을 알 수 있습니다.

### 2단계: 작은 단위로 추출

테스트 안전망이 생겼으면 작은 단위로 추출을 시작합니다.

```python
# 리팩터링 전
def order_total(o):
    s = 0
    for it in o.items:
        s += it.price * it.qty
    if o.coupon: s -= 10
    if o.member: s = s * 0.9
    return s

# 1단계: subtotal 추출
def subtotal(items):
    return sum(i.price * i.qty for i in items)

def order_total(o):
    s = subtotal(o.items)
    if o.coupon: s -= 10
    if o.member: s = s * 0.9
    return s
```

테스트 실행. 통과하면 계속 진행합니다.

```python
# 2단계: 쿠폰 로직 추출
def apply_coupon(amount, has_coupon):
    return amount - 10 if has_coupon else amount

def order_total(o):
    s = subtotal(o.items)
    s = apply_coupon(s, o.coupon)
    if o.member: s = s * 0.9
    return s
```

테스트 실행. 통과하면 계속 진행합니다.

```python
# 3단계: 멤버십 할인 추출
def apply_membership_discount(amount, is_member):
    return amount * 0.9 if is_member else amount

def order_total(o):
    s = subtotal(o.items)
    s = apply_coupon(s, o.coupon)
    s = apply_membership_discount(s, o.member)
    return s
```

매 단계마다 테스트를 실행하고, 통과하면 커밋합니다.

### 리팩터링과 기능 추가는 분리

```
PR-1: order_total을 세 개의 함수로 분리 (동작 변경 없음)
PR-2: 새로운 할인 정책 추가 (기능 변경)
```

둘을 섞으면 리뷰어가 "이 변경이 구조 개선인가, 기능 변경인가"를 구분하기 어렵습니다. 버그가 생겼을 때도 어디서 왔는지 알기 어렵습니다.

## Before / After

```python
# AI가 생성한 코드
def make_report(users):
    result = []
    for u in users:
        if u["active"] and u["last_login_days"] < 30:
            result.append({"id": u["id"], "segment": "engaged"})
    return result
```

```python
# 리팩터링 후
def is_recent_active_user(user: dict) -> bool:
    return user["active"] and user["last_login_days"] < 30

def to_engaged_entry(user: dict) -> dict:
    return {"id": user["id"], "segment": "engaged"}

def make_report(users: list[dict]) -> list[dict]:
    return [to_engaged_entry(u) for u in users if is_recent_active_user(u)]
```

각 함수가 한 가지 일만 합니다. "활성 최근 사용자 조건"을 바꾸려면 `is_recent_active_user`만 찾으면 됩니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 테스트 없이 리팩터링 시작 | 회귀가 우연이 됨 | 특성화 테스트로 현재 동작 먼저 고정 |
| 한 번에 너무 크게 바꾸기 | 되돌릴 방법이 사라짐 | 작은 단계, 매번 커밋 |
| 리팩터링과 기능 추가를 섞기 | 리뷰와 디버깅이 어려워짐 | 두 개의 PR로 분리 |
| 구조는 바꿨는데 이름은 그대로 | 개선 효과가 반감됨 | 이름 변경도 리팩터링의 일부 |
| 미관을 위한 리팩터링 | 다음 변경이 쉬워지지 않음 | "다음 변경이 쉬워지는가"를 기준으로 |

## AI에게 클린 코드 요청하는 팁

```
프롬프트 예시:
"이 함수를 리팩터링해줘.
리팩터링 규칙:
- 외부 동작은 절대 바꾸지 말 것
- 한 번에 한 가지만 변경할 것 (이름 변경, 함수 추출 등)
- 각 변경 후 테스트 코드도 같이 보여줄 것
- 기능 추가는 별도로 요청할 것이므로 이번엔 구조 개선만"
```

## 운영 체크리스트
- [ ] 시작 전 현재 동작을 테스트로 고정했는가?
- [ ] 단계가 충분히 작은가?
- [ ] 기능 변경이 섞여 있지 않은가?
- [ ] 이름이 이제 의도를 드러내는가?
- [ ] 다음 변경이 실제로 더 쉬워졌는가?

## 처음 질문으로 돌아가기

- **리팩터링 전에 먼저 해야 할 것은?**
  현재 동작을 특성화 테스트로 고정합니다. 그래야 리팩터링 중에 동작이 바뀌었는지 바로 알 수 있습니다.

- **리팩터링과 기능 추가를 왜 같은 커밋에 섞으면 안 되나요?**
  리뷰어가 "구조 개선인가, 기능 변경인가"를 구분하기 어렵습니다. 버그가 생겼을 때도 원인 파악이 어렵습니다.

- **테스트 없이 리팩터링을 시작하면?**
  동작이 바뀌어도 알 방법이 없습니다. 작은 변경도 회귀를 만들 수 있고, 그것을 배포 후에야 발견하게 됩니다.

## 정리

AI 코드를 리팩터링하는 핵심은 "작은 단계, 매번 테스트"입니다. 전체를 다시 쓰고 싶은 유혹이 생기더라도, 특성화 테스트로 현재 동작을 고정하고 한 번에 하나씩 개선하는 것이 안전합니다. 리팩터링과 기능 추가는 항상 분리하세요. 다음 글에서는 AI 코드를 팀이 함께 리뷰하는 방법을 다룹니다.

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
- [바이브코딩을 위한 클린 코드 (2/10): AI가 만든 변수명이 a, b, temp](./02-naming.md)
- [바이브코딩을 위한 클린 코드 (3/10): AI가 100줄짜리 함수를 만들었다](./03-functions.md)
- [바이브코딩을 위한 클린 코드 (4/10): AI가 중첩 if를 5단계로 만들었다](./04-conditionals.md)
- [바이브코딩을 위한 클린 코드 (5/10): AI가 같은 코드를 3곳에 복붙했다](./05-dry.md)
- [바이브코딩을 위한 클린 코드 (6/10): AI가 except: pass를 넣었다](./06-error-handling.md)
- [바이브코딩을 위한 클린 코드 (7/10): AI가 주석을 잔뜩 넣었는데 코드와 안 맞다](./07-comments.md)
- [바이브코딩을 위한 클린 코드 (8/10): AI가 만든 코드를 테스트하기 어렵다](./08-testable-code.md)
- **바이브코딩을 위한 클린 코드 (9/10): AI 코드를 리팩터링하는 방법 (현재 글)**
- [바이브코딩을 위한 클린 코드 (10/10): AI 코드를 리뷰하는 방법](./10-code-review.md)
<!-- toc:end -->
Tags: 바이브코딩, CleanCode, AI코딩, 리팩터링, 레거시코드, 코드개선
