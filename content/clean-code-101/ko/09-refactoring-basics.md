---
series: clean-code-101
episode: 9
title: 리팩토링 기초
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
  - Refactoring
  - Patterns
  - LegacyCode
  - Quality
seo_description: 안전한 리팩토링을 위한 특성화 테스트 활용법과 마틴 파울러의 핵심 기법을 통해 레거시 코드를 점진적으로 개선하는 절차를 설명합니다.
last_reviewed: '2026-05-15'
---

# 리팩토링 기초

리팩토링은 코드를 다시 쓰는 작업처럼 보이기 쉽지만, 실제로는 훨씬 더 작은 단위의 개선을 반복하는 일입니다.

이 글은 Clean Code 101 시리즈의 9번째 글입니다.

여기서는 리팩토링이 무엇이고 무엇이 아닌지, 그리고 레거시 코드에서도 안전하게 적용하는 절차를 정리하겠습니다.

---

## 이 글에서 다룰 문제

- 리팩토링은 정확히 무엇이고, 재작성과 무엇이 다를까요?
- Fowler 카탈로그의 핵심 기법은 무엇일까요?
- 특성화 테스트는 왜 레거시 코드에서 중요할까요?
- 안전한 리팩토링은 어떤 작은 단계로 진행해야 할까요?
- 큰 변경은 어떻게 잘게 쪼개서 다룰 수 있을까요?

> 리팩토링은 코드를 더 예쁘게 만드는 일이 아니라, 다음 변경을 더 쉽게 만드는 투자입니다.

## 왜 중요한가

리팩토링의 핵심은 외부 동작을 바꾸지 않고 내부 구조를 개선하는 데 있습니다. 그래서 기능 추가와 섞어 버리면 리뷰도 어려워지고, 어디서 버그가 생겼는지도 구분하기 힘들어집니다.

특히 레거시 코드에서는 "이해한 뒤 고친다"보다 "현재 동작을 먼저 고정한 뒤 조금씩 바꾼다"가 더 현실적인 접근입니다. 리팩토링은 한 번의 큰 점프보다, 초록 테스트와 초록 테스트 사이의 작은 이동을 반복하는 기술입니다.

## 한눈에 보는 개념

![리팩토링 기초](../../../assets/clean-code-101/09/09-01-concept-at-a-glance.ko.png)

*리팩토링의 기본 리듬: 초록 테스트 사이를 작은 단계로 이동하며 구조를 바꿉니다.*

작은 초록 상태에서 다음 초록 상태로 옮겨 가는 것이 리팩토링의 기본 리듬입니다.

## 핵심 용어

- **Refactoring**: 외부 동작을 바꾸지 않는 내부 구조 개선입니다.
- **Characterization test**: 현재 동작을 우선 고정하는 테스트입니다.
- **Code smell**: 긴 함수, 큰 클래스, 데이터 덩어리처럼 개선 필요를 알리는 신호입니다.
- **Two hats**: 기능 추가와 구조 개선을 같은 변경에 섞지 않는 원칙입니다.
- **Mikado method**: 큰 변경을 작은 의존 그래프로 쪼개는 접근입니다.

## Before/After

**Before**

```python
def order_total(o):
    s = 0
    for it in o.items:
        s += it.price * it.qty
    if o.coupon: s -= 10
    if o.member: s = s * 0.9
    return s
```

**After**

```python
def subtotal(items): return sum(i.price * i.qty for i in items)
def with_coupon(s, coupon): return s - 10 if coupon else s
def with_member(s, member): return s * 0.9 if member else s

def order_total(o):
    s = subtotal(o.items)
    s = with_coupon(s, o.coupon)
    s = with_member(s, o.member)
    return s
```

좋은 리팩토링은 한 번에 모든 것을 바꾸지 않습니다. 의미 단위를 하나씩 분리하면서 이름과 구조를 함께 드러냅니다.

## 실전 적용: 안전한 리팩토링 다섯 단계

### Step 1 — Characterization tests as a safety net

```python
# 1_characterize.py
def test_legacy_total():
    o = make_order(items=[(100, 2)], coupon=True, member=True)
    assert order_total(o) == 171  # capture current behavior as is
```

레거시 코드에서는 완전히 이해한 뒤 시작하려고 하면 너무 늦어집니다. 먼저 현재 동작을 고정하고, 그다음에 구조를 만지는 편이 훨씬 안전합니다.

### Step 2 — Extract Function

```python
# 2_extract.py
def subtotal(items): return sum(i.price * i.qty for i in items)
```

가장 먼저 추출할 것은 계산이나 규칙처럼 의미 단위가 분명한 부분입니다. 작은 단위로 잘라야 다음 단계도 명확해집니다.

### Step 3 — Rename

```python
# 3_rename.py
# Rename progressively so that names reveal intent.
def items_subtotal(items): ...
```

이름 변경은 리팩토링의 절반입니다. 구조를 바꿨는데 이름이 그대로면, 읽는 사람은 여전히 예전 정신 모델에 갇히게 됩니다.

### Step 4 — Inline and Move

```python
# 4_move.py
# Move a misplaced function to the right module/class.
class OrderPricing:
    def total(self, order): ...
```

응집도는 올리고, 잘못 놓인 코드는 제자리로 옮겨야 합니다. 때로는 추출보다 이동이 더 큰 가독성 개선을 만듭니다.

### Step 5 — Keep two hats separate

```python
# 5_two_hats.py
# Never mix feature changes and refactoring in one PR.
# PR-1: refactor (preserves behavior)
# PR-2: add feature (new behavior)
```

리팩토링 PR과 기능 PR을 분리해야 리뷰도 쉬워지고, 문제 발생 시 원인도 빨리 좁힐 수 있습니다.

## 검증 방법

```bash
python -m pytest -q tests/test_order_total.py
python -m pytest -q tests/test_legacy_characterization.py
```

**기대 결과**

- 현재 동작을 고정한 테스트가 먼저 초록이어야 합니다.
- 추출, 이름 변경, 이동 뒤에도 테스트 결과가 같아야 합니다.

## 실패하기 쉬운 지점

- 기능 변경이 리팩토링 커밋 안에 함께 섞입니다.
- 이름만 바꾸고 잘못 놓인 책임은 그대로 남아 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 매 단계 뒤에 테스트가 계속 초록 상태를 유지합니다.
- 각 변경은 작고 되돌리기 쉽습니다.
- 이름이 의도를 더 잘 드러내는 방향으로 바뀝니다.

## 자주 하는 실수 5가지

1. **테스트 없이 시작하기.** 회귀가 우연이 됩니다.
2. **한 번에 너무 크게 바꾸기.** 되돌릴 방법이 사라집니다.
3. **기능과 섞어서 바꾸기.** 리뷰가 거의 불가능해집니다.
4. **구조는 바꿨는데 이름은 그대로 두기.** 가치의 절반을 잃습니다.
5. **미관만 위한 리팩토링 하기.** 다음 변경이 쉬워지지 않으면 목적을 놓친 것입니다.

## 실무에서는 이렇게 보입니다

좋은 팀은 기능 PR 전에 먼저 리팩토링 PR을 병합하기도 합니다. 그러면 기능 PR의 크기가 줄고, 리뷰어는 구조 변경과 기능 변경을 분리해서 판단할 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 다음 변경이 쉬워질 때만 리팩토링합니다.
- 빠른 테스트를 두고 작은 단계로 갑니다.
- 두 개의 모자, 즉 기능과 구조를 분리합니다.
- 레거시 코드는 특성화 테스트로 시작합니다.
- 큰 변경은 Mikado 그래프로 잘게 풉니다.

## 체크리스트

- [ ] 시작 전 테스트가 초록인가?
- [ ] 단계가 충분히 작은가?
- [ ] 기능 변경이 섞여 있지 않은가?
- [ ] 이름이 이제 의도를 드러내는가?
- [ ] 다음 변경이 실제로 더 쉬워졌는가?

## 연습 문제

1. 50줄이 넘는 함수 하나를 특성화 테스트로 고정하고 세 단계로 분해해 보세요.
2. 잘못 놓인 함수 하나를 더 적절한 모듈로 옮겨 보세요.
3. 구조만 바꾸는 리팩토링 전용 PR 하나를 열고 병합해 보세요.

## 정리 및 다음 단계

리팩토링은 다음 변경의 비용을 낮추는 투자입니다. 마지막 글에서는 이 시리즈 전체를 한 번에 점검하는 좋은 코드 리뷰 기준으로 마무리합니다.

<!-- toc:begin -->
- [Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [이름 짓기](./02-naming.md)
- [함수 작게 만들기](./03-small-functions.md)
- [조건문 줄이기](./04-simplifying-conditionals.md)
- [중복 제거](./05-removing-duplication.md)
- [오류 처리](./06-error-handling.md)
- [주석과 문서화](./07-comments-and-docs.md)
- [테스트 가능한 코드](./08-testable-code.md)
- **리팩토링 기초 (현재 글)**
- 좋은 코드 리뷰 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Refactoring (Martin Fowler)](https://martinfowler.com/books/refactoring.html)
- [Refactoring Catalog](https://refactoring.com/catalog/)
- [Working Effectively with Legacy Code (M. Feathers)](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)
- [The Mikado Method](https://mikadomethod.info/)
- [Refactoring catalog](https://refactoring.com/catalog/)
- [Working Effectively with Legacy Code](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)
Tags: Computer Science, CleanCode, Refactoring, Patterns, LegacyCode, Quality
