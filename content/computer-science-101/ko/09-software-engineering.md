---
series: computer-science-101
episode: 9
title: "Computer Science 101 (9/10): 소프트웨어 엔지니어링"
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
  - 소프트웨어 엔지니어링
  - 테스트
  - 버전 관리
  - 코드 리뷰
  - 리팩터링
seo_description: 테스트, 버전 관리, 리뷰, 리팩터링으로 코딩과 엔지니어링의 차이를 설명합니다.
last_reviewed: '2026-05-12'
---

# Computer Science 101 (9/10): 소프트웨어 엔지니어링

혼자 짠 스크립트가 한 번 잘 도는 것과, 여러 사람이 몇 년 동안 계속 바꿔도 버티는 시스템을 만드는 일은 다릅니다. 시간이 흐르고 사람이 바뀌는 동안에도 "여전히 잘 동작한다"를 보장하는 습관이 소프트웨어 엔지니어링입니다.

이 글은 Computer Science 101 시리즈의 9번째 글입니다.

여기서는 테스트, 버전 관리, 코드 리뷰, 리팩터링이라는 네 기둥을 통해 코딩이 엔지니어링으로 확장되는 지점을 살펴보겠습니다.

## 먼저 던지는 질문

- 코딩과 소프트웨어 엔지니어링의 차이는 어디에서 생길까요?
- 테스트는 왜 변경을 안전하게 만드는 최소 장치일까요?
- Git 기반 협업 흐름은 어떤 단위와 습관으로 유지될까요?

## 큰 그림

![Computer Science 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/09/09-01-concept-at-a-glance.ko.png)

*Computer Science 101 9장 흐름 개요*

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

**Expected output:** 테스트 네 개가 모두 통과하고, 이후 리팩터링 전후에 같은 테스트를 다시 돌려 동작 보존을 검증할 수 있어야 합니다.

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


## 학습 설계 지도: 이 글을 커리큘럼에 연결하기

컴퓨터 과학 입문을 빠르게 끝내는 접근보다, 서로 연결된 개념을 축적하는 접근이 이후 학습 효율을 높입니다. 이 글의 핵심 개념은 단독 지식이 아니라 운영체제, 네트워크, 데이터베이스, 소프트웨어 공학으로 이어지는 선행 지식입니다. 따라서 한 주 단위 학습에서 이 글을 기준점으로 삼고, 다음과 같은 연결 훈련을 함께 수행하는 것이 좋습니다.

| 학습 축 | 이 글에서 확인할 포인트 | 다음 과목 연결 |
| --- | --- | --- |
| 계산 모델 | 입력, 상태, 출력의 관계를 명확히 정의 | 알고리즘 설계, 분산 시스템 모델링 |
| 추상화 | 세부 구현을 숨기고 인터페이스를 구분 | API 설계, 모듈 경계 설계 |
| 자원 제약 | 시간·메모리·I/O 비용을 동시에 고려 | 성능 튜닝, 인프라 비용 최적화 |
| 검증 가능성 | 주장 대신 측정과 반례로 판단 | 테스트 전략, 실험 설계 |

연결 학습을 할 때는 "개념 정의 1회 + 사례 적용 2회 + 반례 점검 1회" 구조를 반복합니다. 예를 들어 시간 복잡도를 배웠다면, 단순히 O 표기법을 외우지 않고 입력 크기 변화에 따른 실행 시간 그래프를 직접 기록합니다. 그래프가 기대와 다를 때 원인을 추정하고, 캐시 지역성이나 상수항의 영향을 설명해 보는 과정이 필요합니다. 이 연습이 쌓이면 글에서 다룬 개념이 시험 대비 지식이 아니라 실무 의사결정 기준으로 바뀝니다.

또한 과목 간 언어를 통일해 두는 것이 중요합니다. 같은 현상을 운영체제에서는 스케줄링, 네트워크에서는 큐잉, 데이터베이스에서는 트랜잭션 대기라고 부를 수 있습니다. 이름은 달라도 "경합 상태에서 자원을 배분한다"는 본질은 동일합니다. 학습 노트에 용어 사전을 만들어 개념 동치 관계를 표시해 두면, 새로운 분야를 배울 때 기존 이해를 재사용하기 쉬워집니다.

마지막으로 주간 복습은 요약보다 질문 중심으로 구성합니다. "왜 이 추상화가 필요한가", "어떤 조건에서 깨지는가", "대안의 비용은 무엇인가"를 각각 한 문장으로 답하면 학습 깊이가 빠르게 올라갑니다. 이렇게 축적한 질문-답변 세트는 면접, 설계 리뷰, 코드 리뷰에서 그대로 활용 가능한 사고 프레임이 됩니다.

소프트웨어 공학 단원에서는 설계 문서, 코드 리뷰, 테스트 전략을 개별 활동이 아닌 결함 비용을 낮추는 하나의 피드백 루프로 이해합니다.

### 학습 팁: 공학적 품질을 측정 가능한 항목으로 분해하기

소프트웨어 공학 개념은 추상적으로 보이기 쉽지만, 측정 지표로 분해하면 실행 가능해집니다. 예를 들어 변경 리드타임, 배포 빈도, 결함 복구 시간, 테스트 신뢰도 같은 지표를 주 단위로 기록하면 팀의 병목이 드러납니다. 지표를 비난 도구가 아니라 개선 우선순위 도출 도구로 사용해야 지속 가능한 품질 향상이 가능합니다.

### 과목 연결: 설계 원칙과 운영 안정성의 접점

소프트웨어 공학에서 다루는 모듈 경계와 변경 관리 원칙은 운영 안정성과 직결됩니다. 결합도가 높은 구조는 작은 수정도 광범위한 회귀를 유발하기 쉽고, 배포 리스크가 커집니다. 반대로 인터페이스 계약이 명확한 구조는 롤백 전략과 점진 배포 전략을 적용하기 쉬워 장애 전파를 줄일 수 있습니다. 따라서 설계 리뷰 단계에서 운영 시나리오를 함께 점검하는 절차가 필요합니다.

## 처음 질문으로 돌아가기

- **코딩과 소프트웨어 엔지니어링의 차이는 어디에서 생길까요?**
  - 본문의 기준은 소프트웨어 엔지니어링를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **테스트는 왜 변경을 안전하게 만드는 최소 장치일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Git 기반 협업 흐름은 어떤 단위와 습관으로 유지될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Science 101 (1/10): Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): 계산과 프로그램](./02-computation-and-programs.md)
- [Computer Science 101 (3/10): 데이터 표현](./03-data-representation.md)
- [Computer Science 101 (4/10): 알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- [Computer Science 101 (5/10): 컴퓨터 구조](./05-computer-architecture.md)
- [Computer Science 101 (6/10): 운영체제](./06-operating-systems.md)
- [Computer Science 101 (7/10): 네트워크](./07-networks.md)
- [Computer Science 101 (8/10): 데이터베이스](./08-databases.md)
- **소프트웨어 엔지니어링 (현재 글)**
- AI와 데이터사이언스까지의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [The Pragmatic Programmer — David Thomas, Andrew Hunt](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)
- [Refactoring — Martin Fowler](https://martinfowler.com/books/refactoring.html)
- [pytest — Documentation](https://docs.pytest.org/)
- [Pro Git — Scott Chacon (무료)](https://git-scm.com/book/en/v2)

Tags: Computer Science, 소프트웨어 엔지니어링, 테스트, 버전 관리, 코드 리뷰, 리팩터링
