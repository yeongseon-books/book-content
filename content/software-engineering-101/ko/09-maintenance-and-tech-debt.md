---
series: software-engineering-101
episode: 9
title: "Software Engineering 101 (9/10): 유지보수와 기술부채"
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
  - Maintenance
  - TechDebt
  - Refactoring
  - Legacy
seo_description: 기술부채의 4가지 유형, 갚는 우선순위, 안전한 리팩터링과 deprecation 절차를 정리합니다.
last_reviewed: '2026-05-15'
---

# Software Engineering 101 (9/10): 유지보수와 기술부채

어떤 코드베이스든 시간이 지나면 불편한 부분이 생깁니다. 급하게 넣은 분기, 중복된 로직, 오래된 인터페이스, 테스트하기 어려운 구조가 하나씩 쌓입니다. 이때 많은 팀이 “언젠가 크게 리팩터링하면 된다”고 생각하지만, 대개 그 언젠가는 오지 않거나 사고와 함께 찾아옵니다.

기술부채는 존재 자체가 문제는 아닙니다. 실무에서는 의도적으로 빚을 지고 속도를 얻는 선택도 필요합니다. 다만 그 빚을 알고 있었는지, 누가 갚을지 정했는지, 측정 가능한 항목으로 관리하는지가 중요합니다. 의식 없는 부채가 위험한 이유는 일정, 안정성, 학습 비용을 동시에 잠식하기 때문입니다.

이 글은 Software Engineering 101 시리즈의 아홉 번째 글입니다. 여기서는 기술부채의 네 가지 유형, 상환 우선순위, 안전한 리팩터링 절차, 단계적 deprecation, 그리고 부채를 지표로 다루는 방법을 정리합니다.

## 먼저 던지는 질문

- 기술부채는 언제 도구이고, 언제 사고의 씨앗이 될까요?
- Martin Fowler의 네 가지 기술부채 분류는 실무에 어떤 도움을 줄까요?
- 부채 상환 우선순위는 어떻게 정해야 할까요?

## 큰 그림

![Software Engineering 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/09/09-01-concept-at-a-glance.ko.png)

*Software Engineering 101 9장 흐름 개요*

## 왜 중요한가

부채가 없는 코드베이스는 없습니다. 기능을 빨리 내기 위해 단기 선택을 하는 일도 있고, 당시에는 최선이었지만 나중에 더 나은 방법을 배우는 경우도 있습니다. 문제는 이런 항목이 기록되지 않고 쌓일 때 생깁니다. 그러면 부채는 팀의 공통 인식이 아니라 개인의 불만으로만 남습니다.

유지보수 단계에서는 작은 변경 하나도 전체 시스템에 영향을 줍니다. 이때 부채가 보이지 않으면 어떤 부분이 위험한지 우선순위를 잡기 어렵고, 결국 가장 시끄러운 문제만 대응하게 됩니다. 부채를 코드처럼 식별하고 관리해야 하는 이유입니다.

## 한눈에 보는 흐름

기술부채는 한 번 생기고 끝나는 사건이 아니라, 계속 관리해야 하는 순환입니다.

## 핵심 용어

- **의도적이고 신중한 부채**: 갚을 계획이 있는 선택입니다.
- **의도적이고 무모한 부채**: 위험을 알면서 방치하는 선택입니다.
- **비의도적이지만 신중한 부채**: 경험 부족에서 생겼지만 학습으로 상환 가능한 부채입니다.
- **비의도적이고 무모한 부채**: 가장 위험한 형태의 부채입니다.
- **deprecation**: 오래된 인터페이스를 단계적으로 은퇴시키는 절차입니다.

## 전후 비교

**이전 — 나중에 한 번에 고치기**

```text
big-bang refactor at month 12 -> incidents + schedule blow-up
```

**이후 — 분기마다 조금씩 갚기**

```text
5% of each sprint, measured, prioritized -> incremental improvement
```

부채 상환은 큰 선언보다 작고 반복 가능한 흐름일 때 안전합니다.

## 단계별로 부채를 코드처럼 다루기

### 1단계 — 부채 라벨 달기

```python
# 1_label.py
# DEBT(billing): tax computation leaks into PaymentService
# Due: 2026 Q3, owner: @alice
def charge(amount): ...
```

부채에는 맥락, 소유자, 상환 시점이 필요합니다. 없으면 단순한 불평으로 남기 쉽습니다.

### 2단계 — 부채 인덱스 만들기

```markdown
# 2_index.md
| ID | Area | Severity | Owner | Due |
|----|------|----------|-------|-----|
| D-12 | billing | high | alice | 2026 Q3 |
| D-13 | auth | mid | bob | 2026 Q4 |
```

검색 가능한 부채만 실제로 우선순위를 매길 수 있습니다.

### 3단계 — Strangler Fig 패턴 적용하기

```python
# 3_strangler.py
def charge(amount):
    if feature("new_billing"):
        return new_billing.charge(amount)
    return legacy.charge(amount)
```

기존 시스템을 한 번에 갈아엎기보다 기능 플래그로 점진 교체하는 편이 더 안전합니다.

### 4단계 — deprecation 단계를 두기

```python
# 4_deprecate.py
import warnings
def old_api(*a, **kw):
    warnings.warn("old_api is deprecated; use new_api", DeprecationWarning, stacklevel=2)
    return new_api(*a, **kw)
```

경고, 호출자 추적, 제거를 한 번에 몰아 하지 말고 분기별 단계로 나누는 편이 좋습니다.

### 5단계 — 부채 지표 대시보드 만들기

```text
# 5_metrics.md
- Average cyclomatic complexity
- Test coverage delta
- Debt items closed per sprint
- Mean time to recovery (MTTR) on incidents
```

측정하지 않는 부채는 우선순위에서 밀리기 쉽습니다.

## 부채 관리 상태를 확인해 보기

기술부채는 느낌으로 말할수록 우선순위에서 밀립니다. 위험한 항목 하나를 골라 소유자, 만기, 교체 경로를 적어 보면 관리 수준이 바로 드러납니다.

### 확인 절차

1. 최근 장애와 연결된 모듈 하나를 고릅니다.
2. 해당 모듈의 부채 항목을 인덱스에 적고 소유자와 시점을 붙입니다.
3. Strangler Fig 방식으로 안전하게 대체할 첫 단계를 한 줄로 정리합니다.

**예상 결과:**

- 부채를 문장과 표로 적는 순간 우선순위 논의가 훨씬 구체화됩니다.
- 큰 리팩터링보다 작은 교체 단위가 더 현실적이라는 점이 보입니다.
- deprecation 단계를 나누지 않으면 호출자 보호가 어렵다는 사실이 분명해집니다.

### 실패 신호

- 소유자와 만기 없는 TODO만 남아 있습니다.
- 기술부채가 장애와 리드 타임에 어떤 영향을 주는지 설명할 수 없습니다.
- "나중에 한 번에 고치자"가 유일한 계획입니다.

## 이 코드에서 먼저 봐야 할 점

- 부채에는 소유자와 만기 시점이 있어야 합니다.
- Strangler Fig 패턴은 되돌릴 수 있는 교체 전략입니다.
- deprecation은 단계적으로 운영해야 호출자를 보호할 수 있습니다.
- 지표가 없으면 부채는 쉽게 잊힙니다.

## 어디서 자주 헷갈릴까요?

가장 흔한 실수는 큰 폭발형 리팩터링을 한 번에 하려는 것입니다. 범위가 커질수록 변경 영향도와 일정 리스크가 함께 커집니다. 시스템을 더 안전하게 만들겠다는 작업이 오히려 큰 사고를 부르는 경우도 많습니다.

또 다른 실수는 부채를 개인의 잘못으로 보는 태도입니다. 대부분의 부채는 시스템 압력의 결과입니다. 일정, 인력, 우선순위, 당시의 정보 부족이 합쳐진 산물이기 때문에, 비난보다 구조적 관리가 먼저 필요합니다.

deprecation을 선언하자마자 바로 제거하는 습관도 위험합니다. 호출자에게 준비 시간을 주지 않으면 다른 팀이나 외부 사용자에게 바로 장애를 전파하게 됩니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 스프린트 용량의 일부를 항상 부채 상환에 배정합니다. 보통 10~20% 정도를 유지보수와 구조 개선에 씁니다. 그리고 분기 단위로 부채 인덱스를 다시 보며, 어떤 항목이 실제 장애와 리드 타임 악화로 이어지고 있는지 확인합니다.

시니어 엔지니어는 부채를 단순한 미관 문제보다 변경 비용 문제로 봅니다. 코드를 예쁘게 만드는 것이 목표가 아니라, 다음 변경과 다음 사고 대응이 덜 위험해지는 구조를 만드는 것이 목표입니다.

## 체크리스트

- [ ] 부채 인덱스가 있나요?
- [ ] 각 부채 항목에 소유자와 상환 시점이 있나요?
- [ ] 스프린트 용량 일부가 부채 상환에 배정되나요?
- [ ] deprecation 단계가 정의되어 있나요?
- [ ] 부채 지표가 대시보드에 올라가 있나요?

## 연습 문제

1. 현재 저장소에서 부채 항목 다섯 개를 찾아 라벨을 붙여 보세요.
2. 가장 위험한 부채 하나를 Strangler Fig 방식으로 어떻게 쪼갤지 적어 보세요.
3. 팀에 맞는 부채 지표 다섯 가지를 정의해 보세요.

## 정리

기술부채는 사라져야 할 오염물질이 아니라, 관리해야 할 비용 구조입니다. 중요한 것은 존재 자체가 아니라 인지, 측정, 우선순위, 상환 흐름을 갖추는 일입니다. 작은 단위로 기록하고, 분기별로 점검하고, 단계적으로 교체해야 유지보수 비용이 통제 가능합니다.

다음 글에서는 시리즈를 마무리하면서 좋은 소프트웨어의 기준을 묶어 봅니다. 기능성, 신뢰성, 유지보수성, 단순성, 외부 신호를 어떤 균형으로 볼지 이어서 정리하겠습니다.

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

- **기술부채는 언제 도구이고, 언제 사고의 씨앗이 될까요?**
  - 본문의 기준은 유지보수와 기술부채를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Martin Fowler의 네 가지 기술부채 분류는 실무에 어떤 도움을 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **부채 상환 우선순위는 어떻게 정해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Software Engineering 101 (1/10): 소프트웨어 엔지니어링이란 무엇인가?](./01-what-is-software-engineering.md)
- [Software Engineering 101 (2/10): 요구사항 이해하기](./02-understanding-requirements.md)
- [Software Engineering 101 (3/10): 설계와 구현의 차이](./03-design-vs-implementation.md)
- [Software Engineering 101 (4/10): 코드 리뷰](./04-code-review.md)
- [Software Engineering 101 (5/10): 테스트 전략](./05-testing-strategy.md)
- [Software Engineering 101 (6/10): 버전 관리와 릴리스](./06-version-control-and-release.md)
- [Software Engineering 101 (7/10): 문서화](./07-documentation.md)
- [Software Engineering 101 (8/10): 협업 프로세스](./08-collaboration-process.md)
- **유지보수와 기술부채 (현재 글)**
- 좋은 소프트웨어의 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Martin Fowler — Technical Debt Quadrant](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html)
- [Martin Fowler — StranglerFigApplication](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Refactoring — Martin Fowler](https://martinfowler.com/books/refactoring.html)
- [Working Effectively with Legacy Code — Michael Feathers](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)

Tags: Computer Science, SoftwareEngineering, Maintenance, TechDebt, Refactoring, Legacy
