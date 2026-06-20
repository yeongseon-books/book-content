---
series: software-design-101
episode: 8
title: "Software Design 101 (8/10): 변경 영향 줄이기"
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
  - SoftwareDesign
  - ChangeImpact
  - OpenClosed
  - FeatureFlags
  - Refactoring
seo_description: 한 번의 변경이 시스템을 흔들지 않게 하는 설계 — 개방 폐쇄 원칙과 확장-수축 패턴을 정리합니다.
last_reviewed: '2026-05-15'
---

# Software Design 101 (8/10): 변경 영향 줄이기

카테고리 하나를 더 추가하려고 기존 가격 계산 함수에 `if-elif`를 계속 덧붙이다 보면 언젠가 작은 수정 하나가 전체 시스템을 긴장시키는 시점이 옵니다. 변경이 필요한 것은 한 줄인데, 검증 범위와 배포 불안은 그보다 훨씬 커집니다.

이 글은 Software Design 101 시리즈의 8번째 글입니다.

여기서는 변경의 폭발 반경을 어떻게 줄일지, OCP를 실무에서 어떻게 해석해야 할지, expand-contract 패턴과 feature flag를 어떻게 조합할지, 운영 중인 시스템에서 새 경로와 옛 경로를 병행하는 감각은 무엇인지 설명합니다.

![Software Design 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/08/08-01-concept-at-a-glance.ko.png)
*Software Design 101 8장 흐름 개요*

> 좋은 설계는 변경을 없애는 것이 아니라 변경의 폭발 반경을 작게 만드는 일입니다 — 새 카테고리 하나에 `if-elif`를 덧붙이는 대신 확장 지점을 미리 열어 두고, expand-contract로 옛 경로와 새 경로를 잠시 병행시키는 감각이 운영 중 변경을 가능하게 합니다.

## 이 글에서 다룰 문제

- 한 번의 변경이 얼마나 넓게 퍼지는지 어떻게 가늠할까요?
- OCP는 실제 코드에서 어떤 모습으로 나타날까요?
- 새 경로를 추가할 때 왜 기존 경로를 바로 지우지 않을까요?
- 이 설계 원칙을 무시하면 코드베이스가 어떻게 변질될까요?
- 팀 규모가 커질 때 이 원칙의 중요성은 어떻게 달라질까요?

대부분의 시스템은 처음부터 완벽하지 않습니다. 실제로는 계속 바뀌면서 좋아집니다. 그래서 중요한 것은 "변경이 필요한가"가 아니라 "변경이 어디까지 흔드는가"입니다.

폭발 반경이 작은 시스템은 더 자주, 더 안전하게 진화할 수 있습니다. 새 기능을 넣더라도 기존 경로를 건드리지 않고 옆에 붙일 수 있고, 운영 중에도 비교 검증을 하면서 천천히 전환할 수 있기 때문입니다.

## 전체 그림

흐름은 보통 확장하고, 나란히 돌려 보고, 점진적으로 갈아탄 뒤, 마지막에 옛 경로를 정리하는 순서로 갑니다. 정리까지 끝나야 변경이 완료됩니다.

```text
Expand-Contract 흐름

1. Expand (확장)
   v1 코드 그대로 유지
   v2 코드를 옆에 추가

2. Migrate (이행)
   feature flag로 일부 트래픽 → v2
   병렬 비교로 결과 검증

3. Contract (수축)
   모든 트래픽 → v2
   v1 코드와 feature flag 제거

변경이 "완료"되려면 수축까지 끝나야 합니다.
```

## 기본 용어

- <strong>폭발 반경</strong>: 한 번의 변경이 퍼질 수 있는 범위입니다.
- <strong>OCP</strong>: 확장에는 열려 있고 기존 코드 수정에는 닫혀 있는 구조를 지향하는 원칙입니다.
- <strong>expand-contract</strong>: 새 경로와 옛 경로를 함께 운영하며 점진적으로 이주하는 패턴입니다.
- <strong>feature flag</strong>: 코드 배포와 기능 활성화를 분리하는 스위치입니다.
- <strong>strangler fig</strong>: 레거시 바깥을 감싼 뒤 점진적으로 대체해 가는 전환 방식입니다.

## 변경 전과 변경 후

**변경 전 — 새 카테고리마다 기존 함수를 수정**

```python
def price(item, kind: str) -> float:
    if kind == "book":
        return item.cost * 0.9
    elif kind == "food":
        return item.cost * 0.95
    elif kind == "lux":
        return item.cost * 1.1
    elif kind == "digital":      # 새 카테고리 추가 = 이 함수 수정
        return item.cost * 0.85
    elif kind == "subscription":  # 또 수정
        return item.cost * 0.8
    else:
        return item.cost
    # 카테고리가 늘어날수록 이 함수는 계속 커짐
    # 하나를 잘못 건드리면 모든 카테고리에 영향
```

**변경 후 — 새 카테고리 추가가 기존 코드를 건드리지 않음**

```python
from typing import Protocol

class PricingRule(Protocol):
    def apply(self, item) -> float: ...

@dataclass
class DiscountRule:
    discount: float
    def apply(self, item) -> float:
        return item.cost * (1 - self.discount)

@dataclass
class SurchargeRule:
    surcharge: float
    def apply(self, item) -> float:
        return item.cost * (1 + self.surcharge)

# 카테고리 등록 - 코드 수정 없이 추가 가능
PRICING: dict[str, PricingRule] = {
    "book":         DiscountRule(discount=0.10),
    "food":         DiscountRule(discount=0.05),
    "lux":          SurchargeRule(surcharge=0.10),
    "digital":      DiscountRule(discount=0.15),  # 기존 코드 수정 없이 추가
    "subscription": DiscountRule(discount=0.20),  # 기존 코드 수정 없이 추가
}

def price(item, kind: str) -> float:
    rule = PRICING.get(kind)
    if rule is None:
        return item.cost
    return rule.apply(item)
```

두 번째 구조에서는 새 카테고리를 추가할 때 기존 분기문을 직접 수정하지 않아도 됩니다. 확장을 데이터 등록으로 표현하므로 파급 범위를 줄이기 쉽습니다.

## 변경 영향을 줄이는 다섯 단계

### 1단계 — 폭발 반경을 먼저 잰다

```bash
# 1_blast.sh
git grep -n "kind ==" | wc -l
# Has one variable's comparison spread across the system?
```

현재 구조에서 같은 분기가 몇 군데로 퍼져 있는지부터 봐야 합니다. 어디까지 번져 있는지 모르면 줄일 수도 없습니다.

### 2단계 — 새 경로를 옆에 확장한다

```python
# 2_expand.py
# 새 경로만 추가하고 기존 경로는 그대로 둡니다.
def price_v2(item, kind): ...
```

새 구현을 추가할 때 기존 경로를 바로 뜯어고치지 않는 편이 좋습니다. 운영 중인 시스템이라면 특히 비교 기준을 남겨 둬야 합니다.

### 3단계 — 기능 플래그로 점진 전환한다

```python
# 3_migrate.py
def price(item, kind):
    if FF.use_v2: return price_v2(item, kind)
    return price_v1(item, kind)
```

배포와 활성화를 분리하면 새 코드를 미리 올려 두고도 천천히 사용자 일부부터 전환할 수 있습니다. 변경을 작은 단계로 나누는 효과가 있습니다.

### 4단계 — 병렬 비교로 검증한다

```python
# 4_compare.py
import logging

logger = logging.getLogger(__name__)

def price(item, kind) -> float:
    result_v1 = price_v1(item, kind)
    result_v2 = price_v2(item, kind)

    if abs(result_v1 - result_v2) > 0.01:
        logger.warning(
            "price drift detected",
            extra={"kind": kind, "v1": result_v1, "v2": result_v2}
        )

    return result_v2 if FF.use_v2 else result_v1
```

옛 경로와 새 경로를 나란히 돌려 보면 잠복 회귀를 빨리 잡을 수 있습니다. 운영 중인 데이터를 기준으로 비교할 수 있다는 점이 큽니다.

### 5단계 — 마지막에 수축하고 정리한다

```python
# 5_contract.py
# 모두가 v2로 전환되면 v1과 flag를 제거합니다.
# Before cleanup:
#   price_v1, price_v2, FF.use_v2 모두 존재

# After cleanup:
def price(item, kind) -> float:
    rule = PRICING.get(kind)
    if rule is None:
        return item.cost
    return rule.apply(item)
```

새 경로가 안정화되면 옛 코드와 플래그를 지워야 합니다. 정리를 미루면 운영 부채가 쌓입니다.

## Expand-Contract 패턴 적용 시나리오

| 상황 | Expand | Contract |
| --- | --- | --- |
| API 버전 업 | v1과 v2 동시 운영 | 클라이언트 모두 v2 이전 후 v1 제거 |
| DB 스키마 변경 | 새 컬럼 추가, 두 컬럼 모두 채움 | 구 컬럼 null 확인 후 제거 |
| 가격 계산 로직 교체 | v1/v2 병렬 실행, 차이 로깅 | 차이 0건 확인 후 v1 제거 |
| 외부 SaaS 교체 | 구/신 벤더 동시 호출 | 신 벤더 안정 확인 후 구 벤더 제거 |

## 빠르게 검증해 보기

운영 중 코드라면 새 경로를 넣기 전에 비교 기준부터 적어 두는 편이 좋습니다. 아래처럼 옛 경로와 새 경로를 어떤 값으로 비교할지 정리해 보세요.

```text
비교 대상: 가격 계산 결과
비교 시점: 요청 처리 직후
허용 오차: 0
전환 기준: 불일치 로그 0건, 회귀 테스트 통과
```

**Expected output:** 새 구현을 켜기 전에 어떤 신호가 안전한 전환 근거가 되는지 문장으로 설명할 수 있습니다.

이 단계가 있으면 기능 플래그는 단순 스위치가 아니라 검증 계획의 일부가 됩니다.

## 실패 신호와 먼저 볼 것

| 실패 신호 | 먼저 볼 것 |
| --- | --- |
| 새 구현을 켠 뒤 결과 차이를 뒤늦게 발견한다 | 병렬 비교 로그가 있었는지 확인합니다 |
| 기능 플래그가 몇 달째 남아 있다 | 만료일과 제거 계획이 있는지 봅니다 |
| 작은 변경에도 expand-contract를 강제한다 | 정말 운영 위험이 큰 변경인지 다시 판단합니다 |

변경 영향 줄이기의 핵심은 패턴을 많이 쓰는 것이 아니라, 필요한 변화만 작은 단계로 나누어 안전하게 넘기는 데 있습니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 올바른 접근 |
| --- | --- | --- |
| Expand만 하고 Contract 안 함 | 옛 코드와 플래그가 영구 부채로 쌓임 | 전환 완료 후 제거 계획을 반드시 세움 |
| OCP를 "코드 수정 금지"로 해석 | 버그 수정도 패턴을 거쳐야 하는 과도함 | 새 기능 추가 시 기존 코드를 흔들지 않는 것이 목표 |
| 모든 변경에 feature flag 적용 | 플래그 관리 비용이 기능보다 커짐 | 운영 위험이 큰 변경에만 선택적으로 적용 |
| 병렬 비교 없이 전환 | 잠복 버그를 늦게 발견 | 새/구 경로를 나란히 돌려 결과 차이를 먼저 관측 |
| 폭발 반경을 측정하지 않고 리팩터링 | 영향 범위를 모르면 어디서 깨질지 모름 | grep, 의존성 그래프로 범위 먼저 파악 |

## 이 코드에서 먼저 볼 점

- 새 경로가 기존 경로를 바로 덮어쓰지 않습니다.
- 변경이 분기 증가보다 데이터와 설정으로 표현됩니다.
- 비교 검증이 구조 안에 자연스럽게 들어옵니다.

## 어디서 많이 헷갈릴까

개방 폐쇄 원칙을 "기존 코드는 절대 수정하면 안 된다"로 받아들이면 곤란합니다. 실제 의미는 새 기능 추가가 기존 구조 전체를 흔들지 않도록 설계하자는 쪽에 가깝습니다. 작은 버그 수정까지 모두 거대한 확장 패턴으로 처리할 필요는 없습니다.

또 하나 큰 함정은 expand만 하고 contract를 하지 않는 일입니다. 플래그와 구버전 코드가 계속 남아 있으면 한때 안전장치였던 것이 나중에는 운영 부담이 됩니다. 변경의 마지막 단계는 청소까지 포함합니다.

## 실무에서는 이렇게 본다

스키마 마이그레이션, API 버전 교체, 가격 계산 로직 개편, 외부 SaaS 전환처럼 운영 중 시스템을 바꾸는 작업에서 이 패턴은 특히 강합니다. 새 경로와 옛 경로를 함께 두고 관측하면서 옮길 수 있기 때문입니다.

강한 팀은 기능 플래그에도 만료일을 둡니다. 영구 플래그는 보통 숨은 부채입니다. 변경을 끝냈다면 안전하게 제거하는 계획까지 포함해야 합니다.

```python
# 기능 플래그 관리 패턴
@dataclass
class FeatureFlag:
    name: str
    enabled: bool
    expires_at: date          # 만료일 강제
    owner: str                # 담당자 명시
    description: str          # 목적 기록

PRICE_V2_FLAG = FeatureFlag(
    name="price_v2",
    enabled=False,
    expires_at=date(2026, 8, 1),   # 전환 완료 예상일
    owner="backend-team",
    description="가격 계산 로직 v2 전환 (OCP 적용)",
)
```

## Strangler Fig 패턴: 레거시를 점진적으로 대체하기

운영 중인 레거시 시스템을 한 번에 교체하는 것은 매우 위험합니다. Strangler Fig 패턴은 새 구현이 레거시를 점진적으로 감싸며 대체하는 방식입니다.

```python
# 1단계: 레거시 코드 (손대지 않음)
def legacy_calculate_shipping(order_id: str) -> int:
    # 오래되고 복잡한 레거시 로직
    order = db.query_legacy("SELECT * FROM orders WHERE id = %s", order_id)
    return _complex_legacy_formula(order)


# 2단계: 새 구현을 옆에 추가
def new_calculate_shipping(order_id: str) -> int:
    order = new_order_repo.get(order_id)
    return shipping_service.calculate(order)


# 3단계: 라우터가 둘 다 호출하며 비교
def calculate_shipping(order_id: str) -> int:
    legacy_result = legacy_calculate_shipping(order_id)
    new_result = new_calculate_shipping(order_id)

    if legacy_result != new_result:
        logger.warning(
            "shipping calculation mismatch",
            extra={"order_id": order_id,
                   "legacy": legacy_result, "new": new_result}
        )

    # feature flag로 전환 비율 조정
    if ff.shipping_v2_percentage > random.random() * 100:
        return new_result
    return legacy_result


# 4단계: 불일치 0건 확인 후 레거시 제거
def calculate_shipping(order_id: str) -> int:
    order = new_order_repo.get(order_id)
    return shipping_service.calculate(order)
# legacy_calculate_shipping 삭제
```

이 흐름이 Strangler Fig 패턴의 핵심입니다. 나무가 숙주를 감싸며 천천히 대체하듯, 새 코드가 레거시를 안전하게 대체합니다.

## 운영 체크리스트

- [ ] 변경의 폭발 반경을 먼저 가늠했는가?
- [ ] 새 경로를 옛 경로 옆에 둘 수 있는가?
- [ ] 병렬 비교나 회귀 검증 수단이 있는가?
- [ ] 기능 플래그에 만료일이 있는가?
- [ ] 전환 뒤 옛 코드 정리 계획까지 세웠는가?

## 연습 문제

1. 현재 코드에서 분기가 가장 많은 함수를 골라 데이터 기반 분배로 바꿔 보세요.
2. API 하나를 v2로 옮기는 expand-contract 계획을 적어 보세요.
3. 만료일이 없는 기능 플래그 목록을 만들고 정리 우선순위를 매겨 보세요.

## OCP를 적용하는 실전 패턴들

OCP를 실무에서 적용하는 방식은 언어와 상황에 따라 다릅니다. 아래는 Python에서 자주 쓰는 세 가지 패턴입니다.

```python
# 패턴 1: 등록 딕셔너리 (가장 간단)
class PricingRule(Protocol):
    def apply(self, base_price: int) -> int: ...

PRICING_RULES: dict[str, PricingRule] = {}

def register_pricing_rule(category: str, rule: PricingRule) -> None:
    PRICING_RULES[category] = rule

# 새 카테고리는 등록만 하면 됨 — 기존 코드 수정 없음
register_pricing_rule("book", DiscountRule(10))
register_pricing_rule("luxury", SurchargeRule(10))


# 패턴 2: 데코레이터 등록 (더 Pythonic)
_handlers: dict[str, Callable] = {}

def handles(event_type: str):
    def decorator(fn):
        _handlers[event_type] = fn
        return fn
    return decorator

@handles("payment.completed")
def on_payment_completed(event: dict) -> None:
    send_receipt(event["user_id"])

@handles("payment.failed")
def on_payment_failed(event: dict) -> None:
    notify_failure(event["user_id"])

# 새 이벤트 타입 = 새 함수에 데코레이터만 추가


# 패턴 3: 플러그인 로딩 (가장 유연)
import importlib

def load_pricing_rules(plugin_dir: str) -> dict[str, PricingRule]:
    rules = {}
    for module_name in os.listdir(plugin_dir):
        module = importlib.import_module(f"pricing.{module_name}")
        if hasattr(module, "CATEGORY") and hasattr(module, "rule"):
            rules[module.CATEGORY] = module.rule
    return rules
```

## 변경 영향 범위 측정 도구

폭발 반경을 추상적으로 느끼기보다 구체적인 수치로 측정하는 방법입니다.

```bash
# 1. 특정 값이 몇 군데 퍼져 있는지 확인
git grep -rn 'kind == "book"' --include="*.py" | wc -l

# 2. 특정 모듈을 import하는 파일 수 확인
git grep -rn 'from payment import' --include="*.py" | wc -l

# 3. 특정 함수 호출 위치 파악
git grep -rn 'price_v1(' --include="*.py"

# 4. 변경 파일 수를 PR마다 추적 (변경 추세 파악)
git log --name-only --format='' HEAD~10..HEAD | sort -u | wc -l
```

이 수치들을 정기적으로 측정하면 설계 부채가 쌓이는 속도를 조기에 감지할 수 있습니다.

## 현업 적용 관점에서 다시 정리

변경 영향 줄이기의 핵심은 한 번에 다 바꾸지 않는 것입니다. 확장-이행-수축 단계를 분리하면 기능 출시와 구조 개선을 동시에 가져갈 수 있습니다.

## 정리

좋은 설계는 변경을 없애는 것이 아니라 변경의 폭발 반경을 작게 만드는 일입니다 — 새 카테고리 하나에 `if-elif`를 덧붙이는 대신 확장 지점을 미리 열어 두고, expand-contract로 옛 경로와 새 경로를 잠시 병행시키는 감각이 운영 중 변경을 가능하게 합니다. 이 글에서는 전체 그림부터 현업 적용 관점에서 다시 정리까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **한 번의 변경이 얼마나 넓게 퍼지는지 어떻게 가늠할까요?**
  - `git grep`으로 같은 분기 조건이 몇 군데 퍼져 있는지 세어 봅니다. 폭발 반경은 "이 변경이 몇 개 파일을 건드리는가"로 측정합니다.
- **OCP는 실제 코드에서 어떤 모습으로 나타날까요?**
  - 새 카테고리나 기능을 추가할 때 기존 함수 내부를 수정하지 않고 새 클래스를 등록하거나 설정으로 추가하는 형태입니다. 새 경로가 기존 경로를 바로 덮어쓰지 않는 구조입니다.
- **새 경로를 추가할 때 왜 기존 경로를 바로 지우지 않을까요?**
  - 운영 중인 시스템에서 기존 경로는 비교 기준입니다. 새 경로가 같은 결과를 낸다는 것을 충분히 관측한 뒤에야 안전하게 전환할 수 있기 때문입니다.
