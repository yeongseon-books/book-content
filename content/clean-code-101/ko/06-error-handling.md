---
series: clean-code-101
episode: 6
title: "Clean Code 101 (6/10): 오류 처리"
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
  - CleanCode
  - ErrorHandling
  - Exceptions
  - Robustness
  - Reliability
seo_description: 깔끔한 오류 처리 기법을 배웁니다. 예외와 반환값 선택 기준, Fail Fast 원칙, 재시도 전략을 구현하며 견고함을 높이는 법을 배웁니다.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (6/10): 오류 처리

오류 처리는 꼭 필요하지만, 그 코드가 비즈니스 로직보다 더 눈에 띄기 시작하면 구조가 이미 흐려진 경우가 많습니다.

이 글은 Clean Code 101 시리즈의 6번째 글입니다.

여기서는 예외와 반환값을 언제 구분해서 써야 하는지, 그리고 재시도와 경계 처리까지 어떤 기준으로 설계해야 하는지 정리하겠습니다.


![Clean Code 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/06/06-01-concept-at-a-glance.ko.png)
*Clean Code 101 6장 흐름 개요*
> 입력 검증을 먼저, 흐름을 잃은 순간에만 예외를 쓰세요.

## 먼저 던지는 질문

- 예외를 던질지 값을 반환할지 어떻게 판단할까요?
- Fail Fast는 어떤 상황에서 특히 중요할까요?
- "값으로서의 오류" 패턴은 언제 유용할까요?

## 왜 중요한가

오류 처리 코드는 시스템의 견고함을 결정하지만, 동시에 가독성을 쉽게 망가뜨리기도 합니다. 모든 곳에서 넓게 잡고, 로그만 찍고, 계속 진행하는 식의 코드는 실제 장애를 숨기고 나중의 디버깅 비용을 키웁니다.

좋은 오류 처리는 "모든 예외를 막는다"가 아니라 "어디서 어떤 실패를 처리할지 경계를 분명히 나눈다"에 가깝습니다. 입력 검증, 도메인 예외, 외부 호출 재시도, API 경계 매핑이 각각 다른 책임이라는 감각이 중요합니다.

## 한눈에 보는 개념

입력은 먼저 검증하고, 흐름을 잃는 순간에만 예외를 써야 오류 처리가 구조를 해치지 않습니다.

## 핵심 용어

- **Fail Fast**: 잘못된 상태를 가능한 한 빨리 드러내는 원칙입니다.
- **Result/Either**: 성공과 실패를 값으로 표현하는 패턴입니다.
- **Exception**: 호출자가 그 자리에서 복구하기 어려운 상황을 나타냅니다.
- **Retry**: 일시적 실패를 다시 시도하는 전략입니다.
- **Backoff**: 재시도 간격을 점점 늘리는 방식입니다.

## 전/후 비교

**Before**

```python
def fetch(url):
    try:
        ...
    except Exception:
        return None  # swallows everything
```

**After**

```python
class FetchError(Exception): ...

def fetch(url):
    try:
        return _http_get(url)
    except TimeoutError as e:
        raise FetchError(f"timeout: {url}") from e
```

좋은 오류 처리는 정보를 잃지 않습니다. 무엇이 실패했고 왜 올려보냈는지가 유지되어야 상위 계층도 올바르게 판단할 수 있습니다.

## 실전 적용: 견고한 오류 처리 다섯 단계

### 단계 1 — Fail fast

```python
# 1_fail_fast.py
def transfer(amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    ...
```

잘못된 입력은 최대한 입구에서 막는 편이 좋습니다. 오류를 뒤로 미루면 문제는 더 멀리 퍼지고, 원인도 흐려집니다.

### 단계 2 — Errors as values

```python
# 2_result.py
from dataclasses import dataclass
@dataclass
class Result:
    ok: bool
    value: object = None
    error: str = ""

def parse_int(s):
    try: return Result(True, int(s))
    except ValueError as e: return Result(False, error=str(e))
```

호출자가 분기해야 하는 실패라면 값으로 돌려주는 편이 낫습니다. 파싱, 검증, 사용자 입력 처리 같은 영역이 대표적입니다.

### 단계 3 — Exception chaining

```python
# 3_chain.py
class ConfigError(Exception): ...

def load_config(path):
    try:
        with open(path) as f: return f.read()
    except FileNotFoundError as e:
        raise ConfigError(f"missing config: {path}") from e
```

`from e`는 원인을 보존합니다. 도메인 의미를 덧붙이면서도 디버깅에 필요한 원래 예외를 잃지 않는 방식입니다.

### 단계 4 — Retry + backoff

```python
# 4_retry.py
import time, random
def with_retry(fn, attempts=3):
    for i in range(attempts):
        try: return fn()
        except TimeoutError:
            if i == attempts - 1: raise
            time.sleep((2 ** i) + random.random())
```

재시도는 아무 데나 붙이는 장식이 아닙니다. 일시적 실패이면서, 같은 작업을 다시 해도 안전한 경우에만 써야 합니다.

### 단계 5 — Catch only at boundaries

```python
# 5_boundary.py
def handle_request(req):
    try:
        return business_logic(req)
    except ValueError as e:
        return {"status": 400, "error": str(e)}
    except Exception:
        return {"status": 500, "error": "internal"}
```

넓은 except는 가장 바깥 경계에서만 허용하는 편이 좋습니다. 내부 로직까지 모두 삼켜 버리면 구조가 보이지 않게 됩니다.

## 검증 방법

```bash
python -m pytest -q tests/test_error_handling.py
python -m pytest -q tests/test_retry_idempotency.py
```

**기대 결과**

- 예외 타입과 HTTP 경계 매핑이 테스트로 고정됩니다.
- 재시도는 멱등한 호출에서만 통과해야 합니다.

## 실패하기 쉬운 지점

- `except Exception`이 내부 로직 깊숙한 곳에 남아 있습니다.
- 재시도가 중복 결제를 만들 수 있는 작업에도 붙어 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 검증과 처리 책임이 분리되어 있습니다.
- 도메인 예외 타입이 실패의 의미를 운반합니다.
- 재시도는 멱등한 작업에서만 안전합니다.

## 자주 하는 실수 5가지

1. **빈 except 블록 두기.** 정보가 모두 사라집니다.
2. **`Exception`을 무차별적으로 잡기.** 디버깅이 거의 불가능해집니다.
3. **로그만 찍고 계속 진행하기.** 나쁜 상태가 누적됩니다.
4. **무한 재시도 루프 만들기.** 시스템 전체를 더 불안정하게 만듭니다.
5. **예외를 흐름 제어로 사용하기.** 비싸고 읽기도 어렵습니다.

## 실무에서는 이렇게 보입니다

API 서버에서는 핸들러가 보통 경계가 됩니다. 도메인 로직은 타입이 있는 예외를 올리고, 핸들러는 그것을 HTTP 응답으로 바꿉니다. 외부 호출 재시도는 멱등성이 보장된 작업에만 제한적으로 붙입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 입력은 입구에서 검증합니다.
- 도메인 예외 타입을 분명히 만듭니다.
- 복구 가능한 실패와 불가능한 실패를 구분합니다.
- 재시도는 멱등성과 함께 설계합니다.
- 넓은 except는 경계에만 둡니다.

## 체크리스트

- [ ] 입력 검증이 함수 상단에 있는가?
- [ ] 도메인 예외 타입이 있는가?
- [ ] except 범위가 충분히 좁은가?
- [ ] `from e`로 원인을 보존했는가?
- [ ] 재시도가 멱등한 작업에만 적용되는가?

## 연습 문제

1. 코드에 있는 빈 except 하나를 의미 있는 처리로 바꿔 보세요.
2. 파싱 함수 하나를 Result 패턴으로 바꿔 보세요.
3. 외부 호출 하나에 백오프 재시도를 붙여 보세요.

## 정리 및 다음 단계

오류 처리는 일급 시민이어야 하지만, 주인공이 되어서는 안 됩니다. 다음 글에서는 자주 오해되고 남용되기 쉬운 주석과 문서화를 다룹니다.


## 오류 처리 패턴 비교표

오류 처리는 하나의 정답이 아니라 상황별 트레이드오프입니다. 아래 표는 자주 쓰는 패턴의 선택 기준을 정리한 것입니다.

| 패턴 | 적합한 상황 | 장점 | 단점 | Python 구현 힌트 |
| --- | --- | --- | --- | --- |
| 예외 전파 | 호출자가 즉시 복구 불가 | 실패 원인 보존 | 제어 흐름 추적 난이도 증가 | `raise DomainError(...) from e` |
| 값으로 반환(Result) | 호출자가 분기 처리 가능 | 테스트 단순, 흐름 명시 | 호출자 분기 코드 증가 | `Result(ok, value, error)` |
| 경계 매핑 | API/CLI 경계에서 상태 코드 필요 | 내부-외부 책임 분리 | 매핑 테이블 유지 필요 | `except DomainError: return 400` |
| 재시도+백오프 | 일시적 네트워크 장애 | 성공률 개선 | 멱등성 없으면 위험 | 지수 백오프 + 지터 |
| 서킷 브레이커 | 다운스트림 장애가 길 때 | 연쇄 장애 방지 | 상태 관리 복잡 | 실패 카운터 + cooldown |

핵심은 "복구 가능성"과 "경계 위치"입니다. 복구 가능한 실패는 값으로, 복구 불가능한 실패는 예외로 다루는 편이 구조가 선명해집니다.

## 예외 계층 설계 예시

```python
class AppError(Exception):
    """애플리케이션 최상위 예외"""


class DomainError(AppError):
    """비즈니스 규칙 위반"""


class ValidationError(DomainError):
    """입력 검증 실패"""


class PricingError(DomainError):
    """가격 계산 실패"""


class InfraError(AppError):
    """외부 시스템/인프라 오류"""


class TimeoutInfraError(InfraError):
    """타임아웃"""
```

예외 계층을 분리하면 핸들러에서 분기 기준이 명확해집니다. 예를 들어 `ValidationError`는 400, `InfraError`는 503처럼 일관된 HTTP 매핑을 만들 수 있습니다. 또한 로그 집계에서도 도메인 오류와 인프라 오류를 따로 관찰할 수 있어 운영 판단이 빨라집니다.

## 경계 매핑과 재시도 구현 예시

```python
import random
import time
from dataclasses import dataclass


@dataclass
class HttpResponse:
    status: int
    body: dict


def with_retry(operation, attempts: int = 3):
    for attempt in range(attempts):
        try:
            return operation()
        except TimeoutError as error:
            if attempt == attempts - 1:
                raise TimeoutInfraError("retry exhausted") from error
            sleep_seconds = (2 ** attempt) + random.random()
            time.sleep(sleep_seconds)


def handle_http_request(payload: dict) -> HttpResponse:
    try:
        if "amount" not in payload:
            raise ValidationError("amount is required")
        if payload["amount"] <= 0:
            raise ValidationError("amount must be positive")

        result = with_retry(lambda: {"ok": True, "charged": payload["amount"]})
        return HttpResponse(status=200, body=result)

    except ValidationError as error:
        return HttpResponse(status=400, body={"error": str(error)})
    except InfraError:
        return HttpResponse(status=503, body={"error": "temporary unavailable"})
    except AppError:
        return HttpResponse(status=500, body={"error": "application error"})
```

위 구조에서는 내부 함수가 자신의 실패 의미를 예외 타입으로 전달하고, API 경계가 외부 계약으로 변환합니다. 이 분리가 되어 있으면 장애 시 대응도 단순해집니다.


## 실무 적용 메모

아래 메모는 팀 내 합의 문서에 그대로 옮겨 적어도 되는 수준의 운영 규칙입니다.

1. 리뷰는 코드 스타일보다 변경 위험을 먼저 다룹니다.
2. 규칙 위반은 사람 지적보다 자동화 전환을 우선합니다.
3. 반복되는 설계 결함은 교육 과제가 아니라 구조 개선 과제로 등록합니다.
4. 모든 개선은 테스트와 함께 진행하며, 동작 변경 여부를 PR 설명에 명시합니다.
5. 다음 분기 목표에는 "새 기능 수"와 함께 "변경 비용 감소 지표"를 반드시 포함합니다.

```python
from dataclasses import dataclass

@dataclass
class QualityGate:
    has_tests: bool
    has_clear_names: bool
    has_boundary_error_handling: bool
    has_small_functions: bool
    has_review_notes: bool


def evaluate_gate(gate: QualityGate) -> tuple[bool, list[str]]:
    missing = []
    if not gate.has_tests:
        missing.append("tests")
    if not gate.has_clear_names:
        missing.append("naming")
    if not gate.has_boundary_error_handling:
        missing.append("error-boundary")
    if not gate.has_small_functions:
        missing.append("function-size")
    if not gate.has_review_notes:
        missing.append("review-notes")
    return len(missing) == 0, missing
```

이 체크 함수는 단순하지만, 품질 기준을 코드로 표현하는 출발점이 됩니다. 팀이 기준을 말로만 합의하면 시간이 지나며 흐려집니다. 반대로 코드와 템플릿과 자동화 규칙으로 남기면 신규 멤버가 들어와도 동일한 기준이 유지됩니다.

또한 개선 활동은 단발성 이벤트가 아니라 루프여야 합니다. 한 번의 대청소보다 매 PR마다 작은 개선을 추가하는 편이 장기적으로 더 강합니다. 이름 하나, 함수 하나, 분기 하나를 매번 더 낫게 만드는 습관이 쌓이면 코드베이스의 평균 품질이 올라가고, 장애 대응 속도도 실제로 빨라집니다.


## 오류 처리 설계표: 어디서 던지고 어디서 잡을 것인가

오류 처리는 예외 문법보다 경계 설계가 핵심입니다. 아래 표는 계층별 책임을 고정하는 기본 틀입니다.

| 계층 | 해야 할 일 | 하지 말아야 할 일 |
| --- | --- | --- |
| 도메인 함수 | 의미 있는 예외 타입 발생 | HTTP 상태코드 직접 반환 |
| 애플리케이션 서비스 | 예외를 업무 결과로 매핑 | 모든 예외를 동일 메시지로 압축 |
| API 경계 | 상태코드/에러 페이로드 변환 | 내부 스택트레이스 노출 |
| 인프라 어댑터 | 외부 오류를 도메인 예외로 래핑 | 원본 컨텍스트 삭제 |

## 전/후 데모: 경계 매핑으로 오류 의미 보존

```python
# before
def create_order(payload, repo):
    try:
        return repo.insert(payload)
    except Exception:
        return {"ok": False}


# after
class DuplicateOrderError(Exception):
    pass


def create_order(payload, repo):
    try:
        return repo.insert(payload)
    except repo.DuplicateKey as exc:
        raise DuplicateOrderError("order already exists") from exc
```

예외를 경계에서 의미 있게 변환하면 운영 로그에서 실패 이유를 집계하기 쉬워집니다. "실패"라는 한 단어보다 "중복 주문"이라는 원인이 훨씬 빠른 의사결정을 만듭니다.

## 재시도 정책 샘플

```python
import time

def with_backoff(call, retries: int = 3, base_delay: float = 0.2):
    for attempt in range(retries):
        try:
            return call()
        except TimeoutError:
            if attempt == retries - 1:
                raise
            time.sleep(base_delay * (2 ** attempt))
```

재시도는 네트워크 일시 장애에만 적용해야 하며, 데이터 무결성 오류에는 적용하면 안 됩니다. 오류 분류가 재시도 정책보다 먼저입니다.

## 린터/로깅 규칙 예시

```toml
[tool.ruff.lint]
select = ["E", "F", "B", "TRY", "RUF"]
```

```python
logger.error("order-create-failed", extra={"order_id": order_id, "error": str(exc)})
```

예외 타입과 로그 이벤트 이름을 함께 표준화하면 장애 대응 시간(MTTR)을 눈에 띄게 줄일 수 있습니다.


## 심화 실습: 오류 예산과 예외 정책 연결

오류 처리 품질은 코드 내부에서만 측정하지 않습니다. 서비스 오류 예산과 연결해야 우선순위가 명확해집니다.

| 오류 유형 | 사용자 영향 | 처리 정책 |
| --- | --- | --- |
| 입력 검증 실패 | 요청 단건 실패 | 즉시 4xx 반환 |
| 외부 API 타임아웃 | 지연/일시 실패 | 제한 재시도 + 서킷브레이커 |
| 데이터 무결성 오류 | 데이터 손상 위험 | 재시도 금지, 즉시 격리 |

```python
class DomainError(Exception):
    pass


class ValidationError(DomainError):
    pass


class ExternalDependencyError(DomainError):
    pass
```

예외 계층이 명확하면 경보 라우팅도 쉬워집니다. 예를 들어 `ValidationError`는 개발팀, `ExternalDependencyError`는 SRE와 함께 대응하도록 채널을 분리할 수 있습니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.

## 처음 질문으로 돌아가기

- **예외를 던질지 값을 반환할지 어떻게 판단할까요?**
  - 본문의 기준은 오류 처리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Fail Fast는 어떤 상황에서 특히 중요할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **"값으로서의 오류" 패턴은 언제 유용할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Clean Code 101 (1/10): Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): 이름 짓기](./02-naming.md)
- [Clean Code 101 (3/10): 함수 작게 만들기](./03-small-functions.md)
- [Clean Code 101 (4/10): 조건문 줄이기](./04-simplifying-conditionals.md)
- [Clean Code 101 (5/10): 중복 제거](./05-removing-duplication.md)
- **오류 처리 (현재 글)**
- 주석과 문서화 (예정)
- 테스트 가능한 코드 (예정)
- 리팩토링 기초 (예정)
- 좋은 코드 리뷰 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Clean Code (Ch. 7 Error Handling)](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Joel Spolsky — Exceptions](https://www.joelonsoftware.com/2003/10/13/13/)
- [Google SRE — Handling Overload](https://sre.google/sre-book/handling-overload/)
- [AWS — Exponential Backoff and Jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Python exception hierarchy](https://docs.python.org/3/library/exceptions.html)
- [AWS Builders Library — timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/clean-code-101/ko)
Tags: Computer Science, CleanCode, ErrorHandling, Exceptions, Robustness, Reliability
