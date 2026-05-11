---
series: testing-101
episode: 1
title: 테스트란 무엇인가?
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
  - Quality
  - Software
  - Basics
  - Engineering
seo_description: 테스트의 정의, 종류, 자동화의 필요성을 처음부터 설명하는 Testing 101 시리즈의 시작.
last_reviewed: '2026-05-04'
---

# 테스트란 무엇인가?

> Testing 101 시리즈 (1/10)


## 이 글에서 다룰 문제

테스트가 없으면 *모든 변경이 도박* 입니다. 회원가입을 고쳤더니 *결제* 가 깨지고, 결제를 고쳤더니 *로그인* 이 깨집니다. 테스트는 *변경의 안전망* 입니다.

> 테스트는 *느린 손* 을 *빠른 코드* 로 바꿔 줍니다.

## 전체 흐름
```mermaid
flowchart LR
    Code["프로덕션 코드"] --> Test["테스트 코드"]
    Test --> Run["테스트 러너"]
    Run --> Result["통과 / 실패 + 에러 위치"]
```

## Before/After

**Before (수동 테스트)**

```text
1. 로컬에서 서버 띄움
2. 브라우저로 회원가입 → 로그인 → 결제 클릭
3. "되네!" 라고 말하고 PR 머지
4. *3일 뒤* 다른 사람의 변경으로 깨짐
```

**After (자동 테스트)**

```bash
$ pytest
collected 142 items
.................................... 142 passed in 3.4s
```

## 첫 자동 테스트 5단계

### 1단계 — 테스트 대상 함수

```python
# src/calc.py
def add(a: int, b: int) -> int:
    return a + b
```

### 2단계 — 테스트 파일

```python
# tests/test_calc.py
from src.calc import add

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_with_zero():
    assert add(0, 7) == 7
```

### 3단계 — 실행

```bash
pip install pytest
pytest -v
```

### 4단계 — 일부러 깨뜨리기

```python
def add(a: int, b: int) -> int:
    return a - b   # 버그
```

```bash
pytest -v
# FAILED tests/test_calc.py::test_add_positive_numbers - assert -1 == 5
```

### 5단계 — 다시 고치기

`add` 를 원래대로 돌리고 `pytest` 를 다시 돌리면 *모두 통과* 합니다.

## 이 코드에서 주목할 점

- 테스트는 *작은 코드* 입니다. *복잡할 필요* 가 없습니다.
- *깨졌다가 통과로* 돌아오는 경험이 *테스트의 신뢰* 를 만듭니다.
- 테스트는 *문서* 이기도 합니다. 함수의 *예시 사용법* 을 보여줍니다.

## 자주 하는 실수 5가지

1. **테스트를 *나중에 쓴다*.** 결국 *영원히* 안 씁니다.
2. **하나의 테스트에 *여러 단언* 을 넣어 *무엇이* 깨졌는지 모른다.**
3. **테스트가 *느려서* 안 돌린다.** 안 돌리면 *없는 것* 과 같습니다.
4. **테스트가 *프로덕션 코드보다 복잡* 하다.** 그 자체가 버그입니다.
5. **`pytest` 가 통과했다고 *코드가 옳다고 단정* 한다.** 테스트는 *내가 적은 케이스* 만 봅니다.

## 실무에서는 이렇게 쓰입니다

대부분의 팀은 *PR 마다 자동으로 테스트* 가 돌게 합니다 (CI). 테스트가 깨지면 *머지가 막힙니다*. 그래서 *PR을 작게* 쓰고 *테스트를 같이* 추가하는 문화가 생깁니다.

## 체크리스트

- [ ] `pytest` 를 설치하고 한 번 돌렸다.
- [ ] 일부러 깨뜨려 보고 *실패 메시지* 를 읽었다.
- [ ] 단언이 1\~2개인 *작은 테스트* 를 썼다.
- [ ] 테스트가 *3초 이내* 로 끝나는 것을 확인했다.

## 정리 및 다음 단계

테스트는 *변경의 두려움* 을 *변경의 자신감* 으로 바꿉니다. 다음 글에서는 가장 작은 단위, *unit test* 부터 시작합니다.

<!-- toc:begin -->
- **테스트란 무엇인가? (현재 글)**
- 단위 테스트 (예정)
- 통합 테스트 (예정)
- E2E 테스트 (예정)
- 테스트 더블 (예정)
- Mock과 Stub (예정)
- 테스트 커버리지 (예정)
- 회귀 테스트 (예정)
- CI에서 테스트 실행하기 (예정)
- 테스트 전략 세우기 (예정)
<!-- toc:end -->

## 참고 자료

- [pytest docs](https://docs.pytest.org/)
- [Martin Fowler — Testing Strategies](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Google Testing Blog](https://testing.googleblog.com/)
- [The Practical Test Pyramid (book reference)](https://martinfowler.com/articles/practical-test-pyramid.html)

Tags: Testing, Quality, Software, Basics, Engineering
