---
series: computer-science-101
episode: 9
title: 소프트웨어 엔지니어링
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 소프트웨어 엔지니어링
  - 테스트
  - 버전 관리
  - 코드 리뷰
  - 리팩터링
seo_description: 테스트, 버전 관리, 리뷰, 리팩터링으로 코딩과 엔지니어링의 차이를 설명합니다.
last_reviewed: '2026-05-12'
---

# 소프트웨어 엔지니어링

혼자 짠 스크립트가 한 번 잘 도는 것과, 여러 사람이 몇 년 동안 계속 바꿔도 버티는 시스템을 만드는 일은 다릅니다. 시간이 흐르고 사람이 바뀌는 동안에도 "여전히 잘 동작한다"를 보장하는 습관이 소프트웨어 엔지니어링입니다.

이 글은 Computer Science 101 시리즈의 9번째 글입니다.

여기서는 테스트, 버전 관리, 코드 리뷰, 리팩터링이라는 네 기둥을 통해 코딩이 엔지니어링으로 확장되는 지점을 살펴보겠습니다.

## 이 글에서 다룰 문제

- 코딩과 소프트웨어 엔지니어링의 차이는 어디에서 생길까요?
- 테스트는 왜 변경을 안전하게 만드는 최소 장치일까요?
- Git 기반 협업 흐름은 어떤 단위와 습관으로 유지될까요?
- 리팩터링은 왜 기능 추가와 별개로 관리해야 할까요?
- 기술 부채를 방치하면 팀 속도와 품질은 어떻게 무너질까요?

> 엔지니어링은 오늘 동작하는 코드를 내일도 바꿀 수 있게 만드는 일입니다. 테스트와 리뷰는 변경의 안전망이고, 리팩터링은 그 안전망 위에서 구조를 되돌리는 도구입니다.

## 이 글에서 배울 것

- 코딩과 소프트웨어 엔지니어링의 차이
- 테스트가 코드 품질에 미치는 영향
- Git 기반 협업 흐름의 기본
- 리팩터링과 기술 부채 관리 방법

## 왜 중요한가

작동하는 코드를 짜는 능력만으로는 5년 차에 멈춥니다. 같은 코드도 6개월 후의 자신과 동료에게 친절해야 하고, 변경에 깨지지 않아야 합니다. 엔지니어링 습관 — 테스트, 리뷰, 작은 커밋, 명확한 이름 — 이 그 차이를 만듭니다.

> 코드는 한 번 쓰지만, 백 번 읽힙니다.

좋은 코드는 처음에 빨리 짜는 코드가 아니라 오래 고치기 쉬운 코드입니다.

## 한눈에 보는 개념

> 엔지니어링은 "지금 동작" 위에 "내일도 동작"을 보장하는 활동입니다.

```text
Coding only
  requirements -> write -> verify it runs -> deploy

Software engineering
  requirements -> design -> write + test -> review -> CI -> deploy -> monitor -> refactor
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Unit test | 작은 함수나 클래스 단위의 기대 동작을 검증하는 테스트 |
| Version control | 코드 변경 이력과 협업을 관리하는 시스템 |
| Code review | 다른 엔지니어가 변경을 읽고 피드백하는 절차 |
| Refactoring | 외부 동작은 유지한 채 내부 구조를 개선하는 변경 |
| CI/CD | 빌드·테스트·배포를 자동화하는 파이프라인 |
| Technical debt | 단기 편의를 위해 미뤄 둔 구조 개선 비용 |

## Before / After

**Before — 테스트 없이 짠 함수:**

```python
def calc_discount(price, user_type):
    if user_type == "vip":
        return price * 0.7
    elif user_type == "member":
        return price * 0.9
    else:
        return price
# You don't know which input will break it until production calls it
```

**After — 테스트로 동작을 명세화한 함수:**

```python
# discount.py
def calc_discount(price: float, user_type: str) -> float:
    if price < 0:
        raise ValueError("price must be non-negative")
    rates = {"vip": 0.7, "member": 0.9}
    return price * rates.get(user_type, 1.0)

# test_discount.py
import pytest
from discount import calc_discount

def test_vip_gets_30_percent_off():
    assert calc_discount(100, "vip") == 70

def test_member_gets_10_percent_off():
    assert calc_discount(100, "member") == 90

def test_unknown_user_type_pays_full_price():
    assert calc_discount(100, "guest") == 100

def test_negative_price_raises():
    with pytest.raises(ValueError):
        calc_discount(-1, "vip")
```

## 단계별로 따라하기

### 1단계: pytest로 첫 테스트 작성

```bash
# In a virtual environment
pip install pytest

# Place the two files above in the same folder and run
pytest -v
```

### 2단계: 회귀 테스트로 버그 막기

```python
# When you find a bug, first write a test that reproduces it
def test_zero_price_returns_zero():
    """A 0-priced item bought by a VIP must still be 0 (was broken in a previous version)."""
    assert calc_discount(0, "vip") == 0
```

### 3단계: Git 워크플로우

```bash
# Create a new feature branch
git checkout -b feature/discount-vip

# Work and commit in small units
git add discount.py test_discount.py
git commit -m "feat: add VIP discount tier"

# Push and open a PR
git push origin feature/discount-vip
# Open a Pull Request on GitHub/GitLab
```

### 4단계: 리팩터링 — 동작은 그대로, 구조만 개선

```python
# Before: the function grows every time a new tier is added
def calc_discount(price, user_type):
    if user_type == "vip":
        return price * 0.7
    if user_type == "member":
        return price * 0.9
    if user_type == "student":
        return price * 0.85
    return price

# After: pulled out into a data table — adding a tier is one line
DISCOUNT_RATES = {
    "vip":     0.70,
    "member":  0.90,
    "student": 0.85,
}

def calc_discount(price: float, user_type: str) -> float:
    return price * DISCOUNT_RATES.get(user_type, 1.0)

# If the same tests still pass, this is a safe refactor
```

### 5단계: 간단한 CI 설정 (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pytest
      - run: pytest -v
```

## 이 코드에서 먼저 봐야 할 점

- 테스트가 있으면 리팩터링이 무섭지 않습니다
- 작은 커밋과 명확한 메시지는 미래의 자신에게 보내는 편지입니다
- 데이터로 분기를 표현하면 함수는 짧아지고 변경은 쉬워집니다
- CI는 사람이 잊는 검증을 자동으로 대신 해 줍니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| "나중에 테스트 쓰겠다" | 결국 안 쓰고 회귀 버그 발생 | 새 기능과 함께 최소 1개 테스트 |
| 거대한 한 번의 커밋 | 리뷰 불가능, 되돌리기 어려움 | 논리 단위로 작게 자주 커밋 |
| 리뷰 없이 main에 직접 푸시 | 휴먼 에러 누적 | PR + 1명 이상 승인 정책 |
| "임시"로 둔 TODO를 방치 | 기술 부채 누적 | TODO에 이슈 번호와 기한 |
| 모든 코드를 완벽하게 짜려는 시도 | 출시 지연, 과설계 | YAGNI — 지금 필요한 만큼만 |

## 실무에서는 이렇게 쓰입니다

- 변경마다 자동으로 lint·type check·test가 도는 CI
- PR 템플릿으로 변경 의도와 영향 범위를 명시
- Trunk-based development 또는 Git Flow로 브랜치 전략 통일
- 기능 플래그(feature flag)로 부분 출시·즉시 롤백
- 정기적인 리팩터링 스프린트로 기술 부채 상환

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 새 코드를 쓰는 시간만큼 기존 코드를 읽고 다듬는 시간을 중요하게 봅니다. 기능을 얹기 전에 이미 꼬인 이름과 중복을 줄이고, PR을 열기 전에 스스로 첫 번째 리뷰어가 됩니다.

또한 완벽함보다 변경 가능성을 높게 둡니다. 모든 미래를 한 번에 설계하려 하기보다, 작게 배포하고 안전하게 고칠 수 있는 구조를 만듭니다. 테스트와 리뷰는 그 전략을 가능하게 하는 안전망입니다.

## 체크리스트

- [ ] 새 함수를 추가할 때 테스트도 함께 추가하는가
- [ ] 커밋 메시지가 무엇을·왜 바꿨는지 한 줄로 말해 주는가
- [ ] 다른 사람의 PR을 진심으로 읽고 피드백하는가
- [ ] 같은 코드를 두 번 이상 본다면 리팩터링을 고려하는가
- [ ] CI가 깨지면 즉시 고치는 문화를 가진 팀에 속해 있는가

## 연습 문제

1. `calc_discount`에 `partner` 등급(80% 할인)을 추가하고 테스트까지 작성해 보세요.
2. 50줄이 넘는 오래된 함수를 골라 기능은 그대로 둔 채 함수 추출과 이름 개선으로 리팩터링해 보세요.
3. `pytest`와 `ruff`를 병렬로 실행하는 GitHub Actions 워크플로를 작성해 PR에서 결과를 확인해 보세요.

## 정리 및 다음 단계

소프트웨어 엔지니어링은 시간을 견디는 코드를 만드는 활동입니다. 테스트는 변경의 안전망, 버전 관리는 협업의 기반, 리뷰는 품질의 관문, 리팩터링은 기술 부채의 처방입니다. 좋은 엔지니어의 차이는 새 코드를 빠르게 짜는 능력이 아니라, 오래된 코드를 두려워하지 않는 능력에 있습니다.

다음 글에서는 이 모든 CS 기초가 어떻게 AI와 데이터사이언스로 이어지는지, 그리고 다음에 무엇을 공부해야 하는지를 다룹니다.

<!-- toc:begin -->
- [Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [계산과 프로그램](./02-computation-and-programs.md)
- [데이터 표현](./03-data-representation.md)
- [알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- [컴퓨터 구조](./05-computer-architecture.md)
- [운영체제](./06-operating-systems.md)
- [네트워크](./07-networks.md)
- [데이터베이스](./08-databases.md)
- **소프트웨어 엔지니어링 (현재 글)**
- [AI와 데이터사이언스까지의 연결](./10-ai-and-data-science.md)
<!-- toc:end -->

## 참고 자료

- [The Pragmatic Programmer — David Thomas, Andrew Hunt](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)
- [Refactoring — Martin Fowler](https://martinfowler.com/books/refactoring.html)
- [pytest — Documentation](https://docs.pytest.org/)
- [Pro Git — Scott Chacon (무료)](https://git-scm.com/book/en/v2)

Tags: Computer Science, 소프트웨어 엔지니어링, 테스트, 버전 관리, 코드 리뷰, 리팩터링
