---
series: computer-science-101
episode: 9
title: 소프트웨어 엔지니어링
status: content-ready
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
seo_description: 코딩과 소프트웨어 엔지니어링의 차이를 테스트, 버전 관리, 리뷰, 리팩터링 중심으로 다루는 CS 입문 시리즈입니다.
last_reviewed: '2026-05-04'
---

# 소프트웨어 엔지니어링

> Computer Science 101 시리즈 (9/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 혼자 만든 작은 스크립트와 100명이 10년간 유지보수하는 시스템은 무엇이 다를까요?

> 코딩은 동작하는 프로그램을 만드는 일이고, 소프트웨어 엔지니어링은 시간이 흐르고 사람이 바뀌어도 동작하는 시스템을 만드는 일입니다. 테스트는 변경의 안전망, 버전 관리는 협업의 기반, 코드 리뷰는 품질의 마지막 관문, 리팩터링은 기술 부채를 갚는 도구입니다. 이 글에서는 이 네 가지 축을 중심으로 코딩에서 엔지니어링으로 넘어가는 길을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 코딩과 소프트웨어 엔지니어링의 차이
- 테스트가 코드 품질에 주는 효과
- Git 기반 협업 모델
- 리팩터링과 기술 부채 관리

## 왜 중요한가

작동하는 코드를 짜는 능력만으로는 5년 차에 멈춥니다. 같은 코드도 6개월 후의 자신과 동료에게 친절해야 하고, 변경에 깨지지 않아야 합니다. 엔지니어링 습관 — 테스트, 리뷰, 작은 커밋, 명확한 이름 — 이 그 차이를 만듭니다.

> 코드는 한 번 쓰지만, 백 번 읽힙니다.

좋은 코드는 처음에 빨리 짜는 코드가 아니라 오래 고치기 쉬운 코드입니다.

## 개념 한눈에 보기

> 엔지니어링은 "지금 동작" 위에 "내일도 동작"을 보장하는 활동입니다.

```text
코딩만 할 때
  요구사항 → 작성 → 동작 확인 → 배포

소프트웨어 엔지니어링
  요구사항 → 설계 → 작성 + 테스트 → 리뷰 → CI 통과 → 배포 → 모니터링 → 리팩터링
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 단위 테스트 | 함수·클래스 같은 작은 단위가 의도대로 동작하는지 검증 |
| 버전 관리 | 코드 변경 이력을 추적하고 협업 가능하게 만드는 시스템 (Git) |
| 코드 리뷰 | 다른 엔지니어가 변경을 읽고 피드백을 주는 과정 |
| 리팩터링 | 외부 동작은 그대로 두고 내부 구조를 개선하는 변경 |
| CI/CD | 자동 빌드·테스트·배포 파이프라인 |
| 기술 부채 | 단기적 편의를 위해 미뤄 둔 구조적 개선의 누적 비용 |

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
# 실제 호출 전까지 어떤 입력이 깨지는지 모릅니다
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

## 실습: 단계별로 따라하기

### 1단계: pytest로 첫 테스트 작성

```bash
# 가상환경에서
pip install pytest

# 위 두 파일을 같은 폴더에 두고 실행
pytest -v
```

### 2단계: 회귀 테스트로 버그 막기

```python
# 버그를 발견하면 먼저 그 버그를 재현하는 테스트를 씁니다
def test_zero_price_returns_zero():
    """0원 상품을 VIP가 사도 0원이어야 합니다 (이전 버전에서 깨졌던 케이스)."""
    assert calc_discount(0, "vip") == 0
```

### 3단계: Git 워크플로우

```bash
# 새 기능 브랜치 만들기
git checkout -b feature/discount-vip

# 작업 후 작은 단위로 커밋
git add discount.py test_discount.py
git commit -m "feat: add VIP discount tier"

# 원격에 올리고 PR 생성
git push origin feature/discount-vip
# GitHub/GitLab에서 Pull Request 열기
```

### 4단계: 리팩터링 — 동작은 그대로, 구조만 개선

```python
# Before: 조건이 늘어날 때마다 함수가 길어집니다
def calc_discount(price, user_type):
    if user_type == "vip":
        return price * 0.7
    if user_type == "member":
        return price * 0.9
    if user_type == "student":
        return price * 0.85
    return price


# After: 데이터 테이블로 분리 — 새 등급은 한 줄 추가로 끝
DISCOUNT_RATES = {
    "vip":     0.70,
    "member":  0.90,
    "student": 0.85,
}


def calc_discount(price: float, user_type: str) -> float:
    return price * DISCOUNT_RATES.get(user_type, 1.0)


# 같은 테스트가 모두 통과하면 안전한 리팩터링입니다
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

## 이 코드에서 주목할 점

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

시니어 엔지니어는 코드를 쓰는 시간보다 코드를 읽고 다듬는 시간이 더 깁니다. 새 기능을 추가하기 전에 기존 코드를 정리하고, PR을 올리기 전에 자기 코드의 첫 리뷰어가 됩니다. "이 코드를 6개월 뒤의 동료가 보면 화내지 않을까"가 기준입니다.

또한 완벽함보다 변경 가능성을 더 높이 평가합니다. 처음부터 모든 미래를 예측해 설계하기보다, 작게 출시하고 빠르게 고칠 수 있도록 만듭니다. 테스트와 리뷰는 그 변경을 안전하게 만드는 안전망입니다.

## 체크리스트

- [ ] 새 함수를 추가할 때 테스트도 함께 추가하는가
- [ ] 커밋 메시지가 무엇을·왜 바꿨는지 한 줄로 말해 주는가
- [ ] 다른 사람의 PR을 진심으로 읽고 피드백하는가
- [ ] 같은 코드를 두 번 이상 본다면 리팩터링을 고려하는가
- [ ] CI가 깨지면 즉시 고치는 문화를 가진 팀에 속해 있는가

## 연습 문제

1. 위의 `calc_discount`에 신규 등급(`partner`, 80% 할인)을 추가하고 테스트도 함께 작성하세요.

2. 한 함수가 50줄이 넘는 자신의 옛 코드를 골라, 동작은 그대로 두고 함수 분리·이름 개선만으로 리팩터링하세요. 기존 동작이 같은지 테스트로 검증합니다.

3. GitHub Actions로 `pytest`와 `ruff` 두 작업을 병렬로 도는 CI 설정을 만들고 PR에서 결과가 보이도록 구성하세요.

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
