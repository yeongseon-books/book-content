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


![Computer Science 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/09/09-01-concept-at-a-glance.ko.png)
*Computer Science 101 9장 흐름 개요*

## 먼저 던지는 질문

- 코딩과 소프트웨어 엔지니어링의 차이는 어디에서 생길까요?
- 테스트는 왜 변경을 안전하게 만드는 최소 장치일까요?
- Git 기반 협업 흐름은 어떤 단위와 습관으로 유지될까요?

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

## 적용 전후 비교
**Before — 테스트 없이 짠 함수:**

```python
def calc_discount(price, user_type):
    if user_type == "vip":
        return price * 0.7
    elif user_type == "member":
        return price * 0.9
    else:
        return price
# 운영에서 호출되기 전까지 어떤 입력이 깨뜨릴지 알 수 없음
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
# 버그를 찾으면 먼저 재현 테스트부터 작성
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
# Before: 새 tier를 추가할 때마다 함수가 커짐
def calc_discount(price, user_type):
    if user_type == "vip":
        return price * 0.7
    if user_type == "member":
        return price * 0.9
    if user_type == "student":
        return price * 0.85
    return price

# After: 데이터 테이블로 분리 — tier 추가는 한 줄
DISCOUNT_RATES = {
    "vip":     0.70,
    "member":  0.90,
    "student": 0.85,
}

def calc_discount(price: float, user_type: str) -> float:
    return price * DISCOUNT_RATES.get(user_type, 1.0)

# 같은 테스트가 계속 통과하면 안전한 refactor
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


### 테스팅 피라미드와 실전 비율

테스트를 계층별로 나누어 비용과 신뢰도를 균형 잡습니다.

```text
          ╱╲
         ╱  ╲         E2E 테스트 (5-10%)
        ╱    ╲        - 느림, 불안정, 비싸지만 사용자 시나리오 검증
       ╱──────╲
      ╱        ╲      통합 테스트 (15-25%)
     ╱          ╲     - DB, API 경계 검증, 중간 속도
    ╱────────────╲
   ╱              ╲   단위 테스트 (65-80%)
  ╱                ╲  - 빠름, 안정적, 로직 검증
 ╱──────────────────╲
```

| 계층 | 실행 시간 | 유지 비용 | 검증 범위 | 실패 원인 특정 |
|------|-----------|-----------|-----------|---------------|
| 단위 | ms | 낮음 | 함수/클래스 | 정확함 |
| 통합 | 초 | 중간 | 모듈 경계 | 보통 |
| E2E | 분 | 높음 | 전체 시스템 | 어려움 |

```python
# pytest를 사용한 테스트 계층 예시

# 단위 테스트 — 외부 의존성 없음
def calculate_discount(price: float, rate: float) -> float:
    if rate < 0 or rate > 1:
        raise ValueError("rate must be between 0 and 1")
    return round(price * (1 - rate), 2)

def test_calculate_discount():
    assert calculate_discount(10000, 0.1) == 9000.0
    assert calculate_discount(10000, 0) == 10000.0
    assert calculate_discount(10000, 1) == 0.0

def test_calculate_discount_invalid():
    import pytest
    with pytest.raises(ValueError):
        calculate_discount(10000, 1.5)

# 통합 테스트 — DB 연동 확인
def test_create_order(db_session):
    """주문 생성이 DB에 올바르게 반영되는지 확인합니다."""
    order = create_order(db_session, user_id=1, items=[
        {"product_id": 10, "quantity": 2, "price": 5000},
    ])
    assert order.id is not None
    assert order.total == 10000

    # DB에서 다시 읽어 확인
    saved = db_session.query(Order).get(order.id)
    assert saved.total == 10000
    assert len(saved.items) == 1
```

### CI/CD 파이프라인 구성

코드 변경이 운영에 도달하기까지의 자동화된 관문을 정리합니다.

```text
개발자 push → [Lint + Format] → [단위 테스트] → [통합 테스트]
                                                      │
                                                      ▼
[코드 리뷰] ← PR 생성 ←──────────── 모든 체크 통과
     │
     ▼ (승인)
[스테이징 배포] → [E2E 테스트] → [성능 테스트]
                                      │
                                      ▼ (통과)
                              [프로덕션 배포]
                                      │
                                      ▼
                              [모니터링 + 알림]
                              (에러율 > 1% → 자동 롤백)
```

```yaml
# GitHub Actions CI 파이프라인 예시
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: test
          POSTGRES_PASSWORD: test
        ports: ["5432:5432"]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Lint
        run: |
          ruff check .
          ruff format --check .

      - name: Unit tests
        run: pytest tests/unit/ -v --cov=src --cov-report=xml

      - name: Integration tests
        run: pytest tests/integration/ -v
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

### Git 브랜치 전략

| 전략 | 특징 | 적합한 팀 |
|------|------|-----------|
| GitHub Flow | main + feature 브랜치, 단순함 | 소규모, 빈번한 배포 |
| Git Flow | develop + release + hotfix, 체계적 | 정기 릴리스 |
| Trunk-based | 짧은 수명 브랜치, feature flag | 대규모, CI/CD 성숙 |

```bash
# GitHub Flow 기본 워크플로
git checkout -b feature/add-discount-api
# ... 코드 작성 ...
git add -A
git commit -m "feat: add discount calculation endpoint"
git push -u origin feature/add-discount-api
# → PR 생성 → 리뷰 → Squash merge → 브랜치 삭제
```

커밋 메시지 규칙 (Conventional Commits):

```text
<type>(<scope>): <description>

feat:     새 기능 추가
fix:      버그 수정
refactor: 동작 변경 없는 코드 개선
test:     테스트 추가/수정
docs:     문서 변경
chore:    빌드/도구 변경
```

### 기술 부채 관리

기술 부채는 의도적 선택(시간 압박으로 단순 구현)과 비의도적 축적(설계 미숙)으로 나뉩니다.

| 유형 | 예시 | 상환 전략 |
|------|------|-----------|
| 의도적-신중 | "지금은 하드코딩, 다음 스프린트에서 설정으로 분리" | 백로그에 기록, 기한 설정 |
| 의도적-무모 | "테스트 없이 배포, 나중에 추가" | 즉시 상환 (사고 발생 전) |
| 비의도적-신중 | "설계 후 더 나은 방법을 깨달음" | 리팩터링 스프린트 |
| 비의도적-무모 | "레이어 구분 없이 작성" | 교육 + 점진적 재작성 |

기술 부채를 정량화하는 지표: 코드 복잡도(Cyclomatic Complexity), 테스트 커버리지, 빌드 시간, 배포 빈도, 변경 실패율(DORA metrics).

### 코드 리뷰 실전 가이드

효과적인 코드 리뷰는 단순한 스타일 지적이 아니라 설계 결함과 운영 위험을 사전에 발견하는 과정입니다.

리뷰어가 확인해야 할 체크포인트:

| 관점 | 질문 | 예시 |
|------|------|------|
| 정확성 | 요구사항을 정확히 구현했는가? | 경계값 처리, null 케이스 |
| 성능 | N+1 쿼리, 불필요한 루프는 없는가? | ORM lazy loading 주의 |
| 보안 | SQL 인젝션, XSS, 인증 우회 가능성? | 파라미터 바인딩 확인 |
| 유지보수 | 6개월 후 다른 사람이 이해할 수 있는가? | 함수명, 주석, 모듈 경계 |
| 테스트 | 핵심 경로에 대한 테스트가 있는가? | happy path + error path |
| 운영 | 롤백 가능한가? 모니터링 가능한가? | 로그, 메트릭, feature flag |

```python
# 리뷰에서 자주 지적되는 패턴 예시

# Bad: 암묵적 동작, 디버깅 어려움
def process(data):
    result = []
    for item in data:
        if item.get("status") != "deleted":
            result.append(transform(item))
    return result

# Good: 의도가 명확, 테스트 용이
def filter_active_items(items: list[dict]) -> list[dict]:
    """삭제되지 않은 항목만 필터링합니다."""
    return [item for item in items if item.get("status") != "deleted"]

def process_items(items: list[dict]) -> list[dict]:
    """활성 항목을 변환합니다."""
    active = filter_active_items(items)
    return [transform(item) for item in active]
```

### 리팩터링 안전 패턴

리팩터링은 외부 동작을 바꾸지 않으면서 내부 구조를 개선하는 작업입니다. 안전하게 수행하는 단계:

1. **테스트 확보**: 변경할 코드의 현재 동작을 테스트로 고정합니다
2. **작은 단위로 변경**: 한 번에 하나의 리팩터링만 적용합니다
3. **매 단계 테스트 실행**: 초록불을 유지하면서 진행합니다
4. **커밋 분리**: 기능 변경과 리팩터링을 같은 커밋에 섞지 않습니다

자주 사용하는 리팩터링 기법:

| 기법 | 적용 상황 | 효과 |
|------|-----------|------|
| Extract Function | 긴 함수의 일부를 분리 | 재사용성, 테스트 용이 |
| Rename | 의미를 드러내지 않는 이름 | 가독성 향상 |
| Replace Temp with Query | 임시 변수가 여러 줄에 걸침 | 의도 명확화 |
| Introduce Parameter Object | 파라미터가 3개 이상 | 인터페이스 단순화 |
| Replace Conditional with Polymorphism | 타입별 분기가 반복 | OCP 준수 |

```python
# Extract Function 예시

# Before: 한 함수에 여러 책임이 섞여 있음
def generate_report(orders: list[dict]) -> str:
    # 필터링
    valid = [o for o in orders if o["status"] == "completed"]
    # 집계
    total = sum(o["amount"] for o in valid)
    count = len(valid)
    avg = total / count if count else 0
    # 포맷팅
    return f"주문 {count}건, 총액 {total:,}원, 평균 {avg:,.0f}원"

# After: 각 단계를 독립 함수로 분리
def filter_completed(orders: list[dict]) -> list[dict]:
    return [o for o in orders if o["status"] == "completed"]

def summarize_orders(orders: list[dict]) -> dict:
    total = sum(o["amount"] for o in orders)
    count = len(orders)
    return {"total": total, "count": count, "avg": total / count if count else 0}

def format_summary(summary: dict) -> str:
    return (f"주문 {summary['count']}건, "
            f"총액 {summary['total']:,}원, "
            f"평균 {summary['avg']:,.0f}원")

def generate_report(orders: list[dict]) -> str:
    completed = filter_completed(orders)
    summary = summarize_orders(completed)
    return format_summary(summary)
```
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
  - 코딩은 한 사람이 한 시점에 코드를 작성하는 행위이고, 소프트웨어 엔지니어링은 여러 사람이 오랜 기간 코드를 유지·변경·운영하는 체계입니다. 테스트, 코드 리뷰, CI/CD, 기술 부채 관리가 그 체계를 구성합니다.
- **테스트는 왜 변경을 안전하게 만드는 최소 장치일까요?**
  - 테스트가 있으면 코드를 수정한 뒤 기존 동작이 깨지지 않았음을 초 단위로 확인할 수 있습니다. 테스트 없이는 수동 검증에 의존해 변경 주기가 길어지고, 회귀 버그가 누적됩니다.
- **Git 기반 협업 흐름은 어떤 단위와 습관으로 유지될까요?**
  - 하나의 논리적 변경을 하나의 커밋/PR로 만들고, 자동화된 CI 체크를 통과한 뒤 리뷰를 거쳐 머지합니다. Conventional Commits로 변경 유형을 명시하고, feature branch를 짧게 유지해 충돌을 줄입니다.
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

- [이 시리즈의 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-101/ko)
Tags: Computer Science, 소프트웨어 엔지니어링, 테스트, 버전 관리, 코드 리뷰, 리팩터링
