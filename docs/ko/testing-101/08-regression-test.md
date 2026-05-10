---
series: testing-101
episode: 8
title: 회귀 테스트
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Testing
  - Regression
  - Bugfix
  - Quality
  - pytest
seo_description: 같은 버그가 다시 돌아오지 않게 하는 회귀 테스트 작성법과 운영 흐름.
last_reviewed: '2026-05-04'
---

# 회귀 테스트

> Testing 101 시리즈 (8/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 한 번 고친 버그가 *6개월 뒤에 또* 돌아오는 이유는 무엇일까요?

> 회귀 테스트는 *고친 버그를 코드로 박제* 합니다. 다시 깨지면 *즉시 알람* 이 울립니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *회귀 테스트* 의 정의와 목적
- *버그 → 테스트 → 수정* 워크플로우
- *재현 테스트* 와 *최소 재현 케이스*
- 회귀 테스트의 *유지 비용* 관리
- 흔한 함정 5가지

## 왜 중요한가

소프트웨어는 *기억력이 없습니다*. 한 번 고쳐도 *다음 사람이 다시 깨뜨릴 수 있습니다*. 회귀 테스트는 *팀의 기억* 입니다.

> 회귀 테스트가 없는 팀은 *같은 버그를 평생* 고칩니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Bug["버그 보고"] --> Repro["재현 테스트 (실패)"]
    Repro --> Fix["코드 수정"]
    Fix --> Pass["테스트 통과"]
    Pass --> CI["CI에 영구 보관"]
```

## 핵심 용어 정리

- **Regression**: *과거에 고친 동작* 이 *다시 깨지는* 일.
- **Repro test**: 버그를 *재현* 하는 *최소 테스트*.
- **Bug ID**: 이슈 트래커의 *고유 번호* (예: PROJ-1234).
- **Golden file**: *기대 출력* 을 파일로 박제한 비교 기준.
- **Snapshot test**: 출력 *전체 스냅샷* 을 비교하는 테스트.

## Before/After

**Before (구두 약속)**

```text
- "이 버그 고쳤어요" → 머지
- 6개월 뒤 *동일 버그* 가 다시 발견
```

**After (회귀 테스트 추가)**

```python
def test_regression_PROJ_1234_negative_total():
    cart = Cart(); cart.add(Item(price=-1))
    with pytest.raises(ValueError):
        cart.total()
```

## 실습: 회귀 테스트 5단계

### 1단계 — 버그 재현

```python
# tests/test_regression.py
def test_repro_negative_price_breaks_total():
    cart = Cart(); cart.add(Item(price=-1))
    assert cart.total() >= 0   # 현재 *실패* 한다
```

### 2단계 — 빨간 줄 확인

```bash
pytest tests/test_regression.py -v
# FAILED ... assert -1 >= 0
```

### 3단계 — 수정

```python
class Cart:
    def add(self, item):
        if item.price < 0:
            raise ValueError("price must be >= 0")
        self._items.append(item)
```

### 4단계 — 테스트 갱신 (의도 기록)

```python
def test_regression_PROJ_1234_negative_price_rejected():
    """음수 가격 아이템 추가 시 ValueError. (PROJ-1234)"""
    cart = Cart()
    with pytest.raises(ValueError):
        cart.add(Item(price=-1))
```

### 5단계 — CI에 영구 보관

```bash
git add tests/test_regression.py src/cart.py
git commit -m "fix(cart): reject negative price (PROJ-1234)"
```

## 이 코드에서 주목할 점

- 테스트 *이름* 에 *버그 ID* 를 넣어 *추적* 가능하게 합니다.
- 회귀 테스트는 *작고 명확* 합니다. *재현 한 가지* 에만 집중.
- *무조건 추가* 가 아니라 *재발 가능성* 을 보고 결정합니다.

## 자주 하는 실수 5가지

1. **버그를 고치고 *테스트는 안 쓴다*.** 회귀의 *시작* 입니다.
2. **재현 테스트가 *너무 크다*.** *최소* 케이스로 줄이세요.
3. **회귀 테스트만 *쌓이고* 정리되지 않는다.** 유지 비용이 폭발합니다.
4. **스냅샷을 *생각 없이 갱신* 한다.** *왜 바뀌었는지* 확인하지 않으면 *의미 없는 박제* 입니다.
5. **회귀 테스트를 *느린 E2E* 로 만든다.** 가능한 한 *낮은 단계* 에 둡니다.

## 실무에서는 이렇게 쓰입니다

대부분의 팀은 *이슈 → 재현 테스트 → 수정* 흐름을 *기본 PR 템플릿* 으로 강제합니다. 같은 모듈에서 *반복되는 회귀* 가 있으면 *설계 문제* 의 신호로 봅니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 모든 *버그 PR* 에는 *회귀 테스트* 가 따라야 한다.
- 회귀 테스트는 *가능한 한 단위 테스트* 로 둔다.
- *반복되는 회귀* 는 *리팩터링이 필요한 신호* 다.
- 스냅샷은 *변경 이유* 를 적은 후에만 갱신한다.
- *버그 ID* 는 *코드의 메모* 다.

## 체크리스트

- [ ] 최근 버그 수정에 *회귀 테스트* 가 있다.
- [ ] 테스트 이름에 *이슈 ID/이유* 가 들어 있다.
- [ ] 재현 테스트가 *작고 결정적* 이다.
- [ ] 회귀 테스트가 *가능한 단위 레벨* 이다.

## 연습 문제

1. 본인이 최근 고친 버그 *한 가지* 에 회귀 테스트를 추가하세요.
2. 그 테스트를 *고치기 전 코드* 로 돌려 *실패* 를 확인하세요.
3. 같은 모듈의 *과거 회귀* 가 3건 이상이라면 *어떤 리팩터링* 이 필요할지 적으세요.

## 정리 및 다음 단계

회귀 테스트는 *팀의 기억* 입니다. 다음 글에서는 이 모든 테스트를 *자동으로 돌리는 CI* 로 옮깁니다.

<!-- toc:begin -->
- [테스트란 무엇인가?](./01-what-is-testing.md)
- [단위 테스트](./02-unit-test.md)
- [통합 테스트](./03-integration-test.md)
- [E2E 테스트](./04-e2e-test.md)
- [테스트 더블](./05-test-double.md)
- [Mock과 Stub](./06-mock-and-stub.md)
- [테스트 커버리지](./07-test-coverage.md)
- **회귀 테스트 (현재 글)**
- CI에서 테스트 실행하기 (예정)
- 테스트 전략 세우기 (예정)
<!-- toc:end -->

## 참고 자료

- [Martin Fowler — Regression Testing](https://martinfowler.com/articles/practical-test-pyramid.html)
- [pytest docs](https://docs.pytest.org/)
- [Google Testing Blog](https://testing.googleblog.com/)
- [The Pragmatic Programmer — Bug fixing chapter](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)
