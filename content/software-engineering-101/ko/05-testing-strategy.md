---
series: software-engineering-101
episode: 5
title: "Software Engineering 101 (5/10): 테스트 전략"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - SoftwareEngineering
  - Testing
  - TestPyramid
  - CI
  - Quality
seo_description: 단위·통합·E2E 테스트의 역할, 테스트 피라미드, 커버리지 함정과 CI 통합을 정리합니다.
last_reviewed: '2026-05-15'
---

# Software Engineering 101 (5/10): 테스트 전략

테스트가 중요하다는 말에는 대부분 동의합니다. 그런데 실제 팀 안으로 들어가 보면 “어떤 테스트를 얼마나 어디에 둘 것인가”에서 바로 의견이 갈립니다. 단위 테스트를 많이 쓰자는 사람도 있고, 실제 흐름을 보려면 E2E가 더 중요하다고 말하는 사람도 있습니다. 테스트 수가 많을수록 품질이 좋아질 것 같지만, 느리고 불안정한 테스트가 쌓이면 오히려 팀 속도가 무너집니다.

테스트 전략은 테스트를 많이 쓰는 문제가 아니라, 올바른 층에 올바른 종류를 배치하는 문제입니다. 어떤 테스트가 실패했을 때 어디를 먼저 봐야 하는지 분명해야 하고, CI 피드백 시간이 팀의 작업 흐름을 막지 않아야 하며, flaky 테스트는 조용히 무시되지 않고 고쳐져야 합니다.

이 글은 Software Engineering 101 시리즈의 다섯 번째 글입니다. 여기서는 단위·통합·E2E 테스트의 역할, 테스트 피라미드, 커버리지 수치가 왜 자주 거짓말하는지, 그리고 CI를 빠르게 유지하는 방법을 정리합니다.

## 먼저 던지는 질문

- 단위 테스트, 통합 테스트, E2E 테스트는 각각 어떤 역할을 맡을까요?
- 테스트 피라미드와 아이스크림 콘 구조는 무엇이 다를까요?
- 커버리지 수치가 높아도 불안한 시스템이 나오는 이유는 무엇일까요?

## 큰 그림

![Software Engineering 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/05/05-01-concept-at-a-glance.ko.png)

*Software Engineering 101 5장 흐름 개요*

## 왜 중요한가

테스트는 변경 비용을 결정합니다. 믿을 수 있는 테스트가 있으면 리팩터링과 배포가 빨라지고, 테스트가 없거나 flaky하면 작은 수정도 망설이게 됩니다. 그래서 테스트 전략은 QA 단계의 부가 작업이 아니라 개발 속도의 핵심입니다.

실무에서는 커버리지 퍼센트가 높다고 안심하는 경우가 많습니다. 하지만 실패 위치를 좁혀 주지 못하는 E2E 위주의 테스트 묶음은 숫자만 그럴듯할 뿐, 실제로는 느리고 불안정한 안전망이 되기 쉽습니다. 빠르고 설명 가능한 실패를 만드는 구조가 더 중요합니다.

## 한눈에 보는 흐름

테스트 피라미드는 속도와 비용, 진단 가능성의 균형을 맞추는 구조입니다.

## 핵심 용어

- **단위 테스트**: 함수나 클래스 수준에서 외부 의존성 없이 검증하는 테스트입니다.
- **통합 테스트**: 여러 컴포넌트가 함께 동작하는지 확인하는 테스트입니다.
- **E2E 테스트**: 사용자가 겪는 실제 시나리오를 따라가는 테스트입니다.
- **flaky 테스트**: 같은 코드인데도 어떤 때는 실패하고 어떤 때는 통과하는 테스트입니다.
- **커버리지**: 코드가 실행된 비율일 뿐, 테스트 품질 점수는 아닙니다.

## 전후 비교

**이전 — 아이스크림 콘 구조**

```text
E2E 80%, integration 15%, unit 5%
-> slow CI, flaky tests, debugging hell
```

**이후 — 피라미드 구조**

```text
unit 70%, integration 25%, E2E 5%
-> fast CI, clear failure location
```

같은 테스트 예산이라도 어디에 두느냐에 따라 팀의 체감 속도는 크게 달라집니다.

## 단계별로 작은 피라미드 만들기

### 1단계 — 단위 테스트 두기

```python
# 1_unit.py
def add(a: int, b: int) -> int:
    return a + b

def test_add():
    assert add(2, 3) == 5
```

단위 테스트는 가장 빠르고 가장 많이 가져가야 하는 층입니다.

### 2단계 — 가짜 구현으로 통합 테스트하기

```python
# 2_integration.py
class FakeRepo:
    def __init__(self): self.items = []
    def save(self, x): self.items.append(x)

def test_service_uses_repo():
    repo = FakeRepo()
    service = OrderService(repo)
    service.create({"id": 1})
    assert repo.items == [{"id": 1}]
```

mock보다 fake가 구조를 더 자연스럽게 드러내는 경우가 많고, 깨질 가능성도 낮습니다.

### 3단계 — E2E는 핵심 시나리오만 두기

```python
# 3_e2e.py
def test_checkout_flow(client):
    client.post("/cart", json={"sku": "A"})
    r = client.post("/checkout")
    assert r.status_code == 200
```

E2E는 모든 동작을 덮는 층이 아니라, 사용자 여정 가운데 가장 중요한 흐름만 확인하는 층입니다.

### 4단계 — CI를 층별로 분리하기

```yaml
# 4_ci.yml
jobs:
  unit:
    steps: [{ run: pytest tests/unit -q }]
  integration:
    steps: [{ run: pytest tests/integration -q }]
  e2e:
    if: github.ref == 'refs/heads/main'
    steps: [{ run: pytest tests/e2e -q }]
```

모든 테스트를 모든 PR에 같은 방식으로 돌릴 필요는 없습니다. 피드백 시간을 설계해야 합니다.

### 5단계 — flaky 테스트 격리하고 바로 고치기

```python
# 5_flaky.py
import pytest
@pytest.mark.flaky(reruns=2)
def test_uses_external_clock(): ...
```

일단 격리해서 피해를 줄일 수는 있지만, 다음 스프린트에 반드시 원인을 제거해야 합니다.

## 테스트 신뢰도를 점검하는 방법

테스트 전략은 숫자보다 피드백 경로를 봐야 합니다. 느린 테스트 하나가 전체 PR 속도를 얼마나 묶는지, 실패 지점을 얼마나 빨리 좁혀 주는지를 직접 확인해 보세요.

### 확인 절차

1. 최근 CI 실패 하나를 골라 어느 층(Unit, Integration, E2E)에서 터졌는지 적습니다.
2. 실패 원인을 찾는 데 걸린 시간을 메모합니다.
3. 같은 문제를 더 아래 층의 테스트로 옮길 수 있는지 검토합니다.

**예상 결과:**

- 좋은 피라미드는 실패 위치만 봐도 어디를 열어야 할지 감이 옵니다.
- E2E 비중이 너무 크면 원인 파악 시간이 길어집니다.
- flaky 테스트는 재실행 횟수보다 근본 원인을 추적해야 한다는 사실이 분명해집니다.

### 실패 신호

- 커버리지는 높은데도 실패 지점을 설명하기 어렵습니다.
- PR 테스트 시간이 길어서 작은 수정도 머지 주기가 늘어집니다.
- 팀이 빨간 빌드를 신뢰하지 못해 일단 rerun부터 누릅니다.

## 이 코드에서 먼저 봐야 할 점

- 단위 테스트가 가장 많고 가장 빨라야 합니다.
- fake는 과도한 mock보다 더 안정적인 경우가 많습니다.
- E2E는 수가 적어야 실패 분석이 쉬워집니다.
- CI를 층별로 나누면 피드백 시간이 짧아집니다.

## 어디서 자주 헷갈릴까요?

가장 흔한 실수는 커버리지를 목표처럼 다루는 것입니다. 커버리지는 결과 지표일 뿐입니다. 줄 수를 실행했다는 사실이 변경 안전성을 보장하지는 않습니다.

또 다른 실수는 단위 수준에서 끝낼 수 있는 검증을 E2E로 올리는 것입니다. 이렇게 되면 CI는 느려지고, 실패했을 때 원인을 좁히기 어려워집니다. 테스트가 많아도 디버깅이 힘들다면 테스트 전략이 잘못된 경우가 많습니다.

flaky 테스트를 무시하는 문화도 치명적입니다. 한두 번은 재실행으로 넘어갈 수 있어 보이지만, 그 순간부터 팀은 빨간 불을 신뢰하지 않게 됩니다. 테스트 신뢰를 잃으면 전체 배포 안전망이 흔들립니다.

## 실무에서는 이렇게 생각합니다

빠른 팀은 보통 모든 PR에 단위 테스트와 통합 테스트를 걸고, E2E는 메인 브랜치 머지나 야간 배치에서 더 무겁게 돌립니다. 그리고 PR 테스트 시간에 자체 SLO를 둡니다. 예를 들어 PR 기준 5분을 넘기면 테스트를 분할하거나 병렬화하는 식입니다.

시니어 엔지니어는 테스트를 “버그를 잡는 장치”이자 “변경을 가능하게 하는 계약”으로 봅니다. 그래서 테스트가 실패하는 것보다, 실패했을 때 팀이 어디를 봐야 할지 모르는 상태를 더 위험하게 여깁니다.

## 체크리스트

- [ ] 현재 테스트 피라미드 비율을 알고 있나요?
- [ ] PR 테스트 시간이 5분 안팎으로 관리되나요?
- [ ] flaky 테스트를 추적하는 목록이 있나요?
- [ ] mock보다 fake가 더 맞는 곳을 구분하나요?
- [ ] 테스트가 변경 안전성을 얼마나 보장하는지 설명할 수 있나요?

## 연습 문제

1. 외부 의존성을 fake로 바꿔 볼 수 있는 함수 하나를 찾아 보세요.
2. 가장 느린 E2E 테스트 하나를 골라 단위·통합 테스트로 어떻게 쪼갤지 적어 보세요.
3. 최근 flaky 테스트 하나에 대해 5 Whys를 적용해 보세요.

## 정리

좋은 테스트 전략은 테스트 개수를 늘리는 일이 아니라, 빠르고 신뢰할 수 있는 피드백 구조를 만드는 일입니다. 단위 테스트를 두텁게 두고, 통합 테스트로 경계를 확인하고, E2E는 핵심 시나리오만 좁게 운영해야 CI도 빨라지고 장애 분석도 쉬워집니다.

다음 글에서는 이렇게 검증된 코드를 사용자에게 안전하게 보내는 과정을 다룹니다. 버전 관리, 시맨틱 버저닝, 체인지로그, 카나리와 롤백을 하나의 릴리스 흐름으로 묶어 보겠습니다.

## 엔지니어링 품질을 끌어올리는 추가 실무 프레임

기능 개발이 반복될수록 팀의 속도는 개인 역량보다 시스템화 수준에 더 크게 좌우됩니다. 특히 요구사항 명세, 리뷰 체크리스트, 테스트 전략이 분리되지 않으면 구현 품질은 우연에 기대게 됩니다. 아래 틀은 작은 팀에서도 바로 적용할 수 있는 최소 운영 단위입니다.

### 요구사항 명세 템플릿

요구사항은 "무엇을 만들지"보다 "완료를 어떻게 판단할지"까지 포함해야 합니다. 문장이 추상적이면 구현 범위가 확장되고, QA와 운영에서 해석이 갈립니다.

```text
[기능명] 장바구니 쿠폰 적용
- 배경: 재구매율 개선
- 사용자 시나리오: 로그인 사용자가 결제 전 쿠폰 코드를 입력한다
- 성공 조건:
  1) 유효 쿠폰이면 총액에서 할인 금액 차감
  2) 만료 쿠폰이면 400 + "coupon_expired" 반환
  3) 중복 적용 불가
- 비기능 요구:
  - p95 응답 시간 200ms 이하
  - 감사 로그에 coupon_id, user_id, trace_id 기록
- 제외 범위:
  - 관리자 쿠폰 생성 화면은 이번 범위에서 제외
```

이 형식의 장점은 구현 이전에 충돌 지점을 드러낸다는 점입니다. 예외 코드, 성능 기준, 제외 범위를 먼저 고정하면 개발 중간에 목표가 흔들리는 일을 줄일 수 있습니다.

### 코드 리뷰 체크리스트(필수 8항목)

```text
1. 요구사항의 성공 조건이 코드에서 추적 가능한가?
2. 에러 응답 형식과 상태 코드가 합의와 일치하는가?
3. 도메인 규칙이 컨트롤러/뷰 계층으로 새지 않았는가?
4. 신규 의존성이 보안/라이선스 정책과 충돌하지 않는가?
5. 테스트가 성공/실패/경계 케이스를 모두 포함하는가?
6. 로그에 민감정보가 기록되지 않는가?
7. 롤백 또는 feature flag 경로가 준비되어 있는가?
8. 문서(README, ADR, API 스펙)가 변경 내용을 반영하는가?
```

체크리스트의 목적은 리뷰 속도를 늦추는 것이 아니라, 리뷰 품질의 편차를 줄이는 것입니다. 팀원이 바뀌어도 같은 기준으로 위험을 잡아내야 릴리스 안정성이 유지됩니다.

### 테스트 전략: 피라미드 + 변경 위험 기반

```python
# tests/test_coupon_service.py
import pytest

@pytest.mark.unit
def test_apply_valid_coupon(coupon_service):
    total = coupon_service.apply(total_amount=20000, code="SAVE10")
    assert total == 18000

@pytest.mark.unit
def test_apply_expired_coupon(coupon_service):
    with pytest.raises(ValueError, match="coupon_expired"):
        coupon_service.apply(total_amount=20000, code="OLD10")
```

```text
권장 비율(시작점)
- Unit: 70%
- Integration: 20%
- E2E: 10%
```

Unit 테스트는 규칙 변경을 빠르게 검증하고, Integration 테스트는 DB/외부 API 경계의 계약을 검증하며, E2E 테스트는 사용자 핵심 경로만 보호합니다. 모든 것을 E2E로 막으려 하면 실행 시간이 늘고 실패 원인 분리가 어려워집니다.

### 릴리스 전 확인 절차

- 요구사항 문서의 성공 조건과 테스트 케이스 ID를 매핑합니다.
- 리뷰 체크리스트 미충족 항목이 있으면 머지 전 해결 또는 위험 수용 근거를 남깁니다.
- 배포 직후 확인할 지표(p95, 에러율, 결제 성공률)를 사전에 합의합니다.
- 장애 시 되돌림 절차와 커뮤니케이션 채널을 지정합니다.

엔지니어링의 핵심은 "잘 만드는 기술"과 "같은 품질을 반복하는 시스템"을 동시에 갖추는 것입니다. 위 세 축이 고정되면 팀 규모가 커져도 의사결정의 품질이 유지되고, 기능 추가 속도와 운영 안정성을 함께 확보할 수 있습니다.

## 요구사항-리뷰-테스트 연결표

엔지니어링에서 자주 놓치는 지점은 세 문서가 따로 움직이는 상황입니다. 요구사항 문서는 목표만 말하고, 리뷰는 스타일 중심으로 흘러가고, 테스트는 구현 이후에 뒤따라옵니다. 이렇게 분리되면 기능은 동작해도 품질 기준이 흐려집니다. 아래처럼 연결표를 두면 변경 영향이 추적됩니다.

```text
REQ-12: 만료 쿠폰 거부
- Review check: 상태 코드 400 + error_code=coupon_expired 확인
- Test case: test_apply_expired_coupon
- Metric: coupon_expired 발생 비율
```

연결표를 유지하면 "무엇을 만들었는가"가 아니라 "어떤 기준을 만족했는가"로 대화가 바뀝니다. 회고 시점에도 장애 원인을 요구사항 해석, 리뷰 누락, 테스트 공백 중 어디서 시작됐는지 빠르게 찾을 수 있습니다.

### 운영 전환 체크

- 배포 노트에 요구사항 ID와 PR 링크를 함께 남깁니다.
- 온콜 핸드오프 문서에 새 기능의 실패 시그널을 명시합니다.
- 첫 24시간 관찰 지표와 임계치를 릴리스 전에 고정합니다.

이 작은 연결 장치가 있으면 팀 규모가 커져도 품질 기준이 개인 기억에 의존하지 않습니다.

## 처음 질문으로 돌아가기

- **단위 테스트, 통합 테스트, E2E 테스트는 각각 어떤 역할을 맡을까요?**
  - 본문의 기준은 테스트 전략를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **테스트 피라미드와 아이스크림 콘 구조는 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **커버리지 수치가 높아도 불안한 시스템이 나오는 이유는 무엇일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Software Engineering 101 (1/10): 소프트웨어 엔지니어링이란 무엇인가?](./01-what-is-software-engineering.md)
- [Software Engineering 101 (2/10): 요구사항 이해하기](./02-understanding-requirements.md)
- [Software Engineering 101 (3/10): 설계와 구현의 차이](./03-design-vs-implementation.md)
- [Software Engineering 101 (4/10): 코드 리뷰](./04-code-review.md)
- **테스트 전략 (현재 글)**
- 버전 관리와 릴리스 (예정)
- 문서화 (예정)
- 협업 프로세스 (예정)
- 유지보수와 기술부채 (예정)
- 좋은 소프트웨어의 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Martin Fowler — Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html)
- [Google Testing Blog — Just Say No to More End-to-End Tests](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html)
- [Pytest Docs](https://docs.pytest.org/)
- [Working Effectively with Legacy Code — Michael Feathers](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)

Tags: Computer Science, SoftwareEngineering, Testing, TestPyramid, CI, Quality
