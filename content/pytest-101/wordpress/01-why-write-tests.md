---
title: "바이브코딩을 위한 Pytest 기초 (1/10): 왜 테스트를 작성해야 할까?"
series: pytest-101
episode: 1
targets:
  wordpress: true
tags:
  - Python
  - pytest
  - Testing
  - 소프트웨어 품질
  - 자동화 테스트
  - 바이브코딩
---

# 바이브코딩을 위한 Pytest 기초 (1/10): 왜 테스트를 작성해야 할까?

이 글은 **바이브코딩을 위한 Pytest 기초** 시리즈의 첫 번째 글입니다. AI가 생성한 코드를 pytest로 검증하는 방법을 10편에 걸쳐 다룹니다.

---

AI가 코드를 써 줬습니다. 그런데 "이 코드가 실제로 맞게 동작하는가?"라는 질문이 남습니다. 바이브코딩 시대에 pytest는 AI가 만든 코드를 신뢰할 수 있게 만드는 검증 도구입니다. 테스트를 작성하면 개발이 느려진다고 느끼기 쉽지만, 실제로는 변경에 대한 두려움을 줄여서 개발 속도를 높이는 경우가 훨씬 많습니다.

코드를 고칠 때마다 "이 변경이 다른 기능을 깨뜨리지는 않을까?"라는 불안이 생긴다면, 이미 테스트가 필요한 상태일 가능성이 큽니다. AI가 생성한 코드는 겉으로는 그럴듯해 보여도 경계값 처리나 예외 케이스에서 빗나갈 수 있습니다. pytest는 이런 빈틈을 자동으로 잡아 주는 안전망입니다.

> "테스트는 미래의 나를 위한 안전망입니다. AI가 만든 코드도 예외 없이 검증이 필요합니다."

---

## 이 글에서 다룰 문제

- 테스트는 개발 속도를 늦추는 작업일까요, 아니면 오히려 속도를 높이는 투자일까요?
- 단위 테스트, 통합 테스트, E2E 테스트는 무엇이 다를까요?
- 수동 테스트와 자동화 테스트는 어떤 차이를 만들까요?
- AI가 만든 코드를 어떻게 체계적으로 검증할 수 있을까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

---

## 왜 이 글이 중요한가

바이브코딩 환경에서 AI는 코드를 빠르게 생성합니다. 그러나 생성된 코드가 실제로 요구사항을 만족하는지는 테스트 없이 보장하기 어렵습니다. 특히 AI 코드는 겉으로 통과해 보이는 케이스에 집중하고, 경계값이나 예외 경로를 놓치는 경향이 있습니다.

테스트가 없는 상태에서의 변경은 늘 도박에 가깝습니다. 코드가 커질수록 "이 함수 하나만 바꿨는데 왜 전혀 다른 화면이 깨졌지?" 같은 상황이 자주 생기기 때문입니다. 반대로 테스트가 있으면, 변경 직후 기존 동작이 유지되는지 바로 확인할 수 있습니다.

실무에서는 이 차이가 더 크게 드러납니다. 테스트 없이 배포하면 장애 원인 분석이 길어지고, 어디서 어떤 입력이 실패했는지 파악하는 시간도 늘어납니다. 테스트는 "정상 동작을 기대한 계약"을 코드로 남기는 수단입니다.

---

## 핵심 개념 잡기

> 테스트 = 코드가 기대한 방식으로 동작하는지 자동으로 검증하는 코드

```text
[수동 테스트]                  [자동화 테스트]
  사람이 코드를 실행              코드가 코드를 실행
  반복 비용 증가                  반복 비용 ≈ 0
  실수 발생 가능                  일관된 결과
  커버리지 불명확                 커버리지 측정 가능
```

수동 테스트는 처음에는 간단해 보이지만, 같은 확인을 반복할수록 비용이 빠르게 커집니다. AI가 코드를 생성할 때마다 수동으로 확인하는 방식은 장기적으로 지속 불가능합니다.

---

## 주요 개념 정리

| 용어 | 설명 |
|------|------|
| 단위 테스트 | 함수 하나를 독립적으로 검증합니다 |
| 통합 테스트 | 여러 컴포넌트가 함께 동작하는 방식을 검증합니다 |
| E2E 테스트 | 사용자 관점에서 전체 흐름을 검증합니다 |
| 테스트 피라미드 | 단위 테스트를 많이, 통합/E2E 테스트를 상대적으로 적게 두는 전략입니다 |
| 회귀 테스트 | 변경 후에도 기존 기능이 계속 동작하는지 확인합니다 |

---

## Before / After: 수동 확인 vs pytest 자동 검증

AI가 `add` 함수를 생성했다고 가정해 보겠습니다.

**Before: 수동 확인 방식**

```python
# AI가 생성한 코드
def add(a, b):
    return a + b

# 수동으로 출력을 눈으로 확인
print(add(1, 2))   # 3이 나오는지 확인
print(add(-1, 1))  # 0이 나오는지 확인
```

**After: pytest 자동 검증**

```python
# AI가 생성한 코드
def add(a, b):
    return a + b

# pytest로 자동 검증
def test_add_positive():
    assert add(1, 2) == 3

def test_add_negative():
    assert add(-1, 1) == 0
```

두 방식의 핵심 차이는 사람이 눈으로 확인하느냐, 도구가 조건을 자동으로 확인하느냐입니다. AI 코드를 반복적으로 수정하고 검증해야 하는 바이브코딩 환경에서는 자동화가 필수입니다.

---

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 테스트 파일 이름이 `test_`로 시작하지 않음 | pytest가 파일을 자동 탐색하지 못합니다 | `test_*.py` 또는 `*_test.py` 규칙을 따릅니다 |
| 테스트 함수 이름이 `test_`로 시작하지 않음 | 테스트로 인식되지 않습니다 | 함수명에 `test_` 접두사를 붙입니다 |
| `print()`로 결과를 확인함 | 자동화할 수 없고 회귀를 잡지 못합니다 | 기대값을 `assert`로 명시합니다 |
| 하나의 테스트에 assert를 너무 많이 넣음 | 첫 실패 이후 나머지 검증이 중단됩니다 | 테스트 하나당 한 가지 행위를 검증합니다 |
| AI 생성 코드를 테스트 없이 사용함 | 경계값 오류가 운영에서 드러납니다 | 생성 즉시 핵심 경로를 테스트합니다 |

---

## AI 코딩 팁

AI가 함수를 생성하면 다음 순서로 pytest를 활용하세요.

1. AI에게 "이 함수를 검증하는 pytest 테스트 케이스도 작성해 달라"고 요청합니다.
2. 정상 케이스뿐 아니라 경계값(빈값, 최솟값, 최댓값)과 오류 케이스도 포함하도록 명시합니다.
3. AI가 생성한 테스트를 실행해 모두 통과하는지 확인합니다.
4. 놓친 케이스가 있으면 직접 추가합니다.

```bash
# AI가 생성한 코드와 테스트를 한 번에 실행
pytest test_calculator.py -v
```

---

## 실습: 첫 번째 pytest 테스트

pytest를 설치하고 첫 테스트를 실행해 보겠습니다.

```bash
pip install pytest
pytest --version
```

`calculator.py` 파일을 만듭니다.

```python
# calculator.py
def add(a: int, b: int) -> int:
    return a + b

def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

`test_calculator.py` 파일을 만듭니다.

```python
# test_calculator.py
import pytest
from calculator import add, divide

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_divide():
    assert divide(10, 2) == 5.0

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(1, 0)
```

테스트를 실행합니다.

```bash
pytest test_calculator.py -v
```

```text
test_calculator.py::test_add PASSED
test_calculator.py::test_add_negative PASSED
test_calculator.py::test_divide PASSED
test_calculator.py::test_divide_by_zero PASSED
========================= 4 passed =========================
```

---

## 체크리스트

- [ ] `pytest --version`으로 설치를 확인했다
- [ ] `test_` 접두사 규칙을 이해했다
- [ ] `assert`로 기대값을 검증하는 테스트를 작성했다
- [ ] `pytest.raises`로 예외 테스트를 작성했다
- [ ] `pytest -v`로 실행 결과를 확인했다
- [ ] AI 생성 코드에 테스트를 연결하는 흐름을 이해했다

---

## 처음 질문으로 돌아가기

- **테스트는 개발 속도를 늦추는 작업일까요?**
  - 경험이 쌓인 개발자일수록 테스트를 "추가 작업"이 아니라 "개발의 일부"로 봅니다. 특히 AI 생성 코드를 다룰 때는 테스트가 코드 신뢰의 유일한 근거가 됩니다.
- **단위/통합/E2E 테스트는 무엇이 다를까요?**
  - 단위 테스트는 함수 하나를 격리해 빠르게 검증합니다. 바이브코딩에서는 AI가 생성한 순수 함수를 단위 테스트로 먼저 커버하는 것이 가장 효율적입니다.
- **AI 코드를 어떻게 검증할 수 있을까요?**
  - AI에게 코드와 테스트를 함께 요청하고, 경계값과 오류 케이스를 직접 추가하는 습관이 핵심입니다.

---

## 정리

테스트는 코드 변경에 대한 안전망입니다. pytest는 `assert` 하나만으로도 충분히 읽기 좋은 테스트를 만들 수 있게 해 줍니다. 바이브코딩 환경에서 AI가 코드를 빠르게 생성할수록, 그 코드를 검증하는 pytest의 역할도 커집니다. 다음 글에서는 pytest가 테스트 파일과 함수를 어떻게 자동으로 찾는지, 그리고 첫 번째 테스트를 실제로 작성하는 과정을 봅니다.

---

## 참고 자료

- [pytest 공식 문서](https://docs.pytest.org/)
- [Python Testing with pytest (Brian Okken)](https://pragprog.com/titles/bopytest2/python-testing-with-pytest-second-edition/)
- [Test Pyramid — Martin Fowler](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Real Python — Getting Started With Testing in Python](https://realpython.com/python-testing/)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 Pytest 기초 (1/10): 왜 테스트를 작성해야 할까? (현재 글)**
- 바이브코딩을 위한 Pytest 기초 (2/10): 첫 번째 pytest 테스트 작성하기
- 바이브코딩을 위한 Pytest 기초 (3/10): assert와 예외 테스트
- 바이브코딩을 위한 Pytest 기초 (4/10): fixture 이해하기
- 바이브코딩을 위한 Pytest 기초 (5/10): parametrization으로 테스트 케이스 늘리기
- 바이브코딩을 위한 Pytest 기초 (6/10): mock과 monkeypatch
- 바이브코딩을 위한 Pytest 기초 (7/10): 파일, 환경변수, 시간 테스트하기
- 바이브코딩을 위한 Pytest 기초 (8/10): coverage와 테스트 품질 보기
- 바이브코딩을 위한 Pytest 기초 (9/10): GitHub Actions에서 테스트 자동화하기
- 바이브코딩을 위한 Pytest 기초 (10/10): 테스트하기 쉬운 코드 구조 만들기
<!-- toc:end -->

Tags: Python, pytest, Testing, 소프트웨어 품질, 자동화 테스트, 바이브코딩
