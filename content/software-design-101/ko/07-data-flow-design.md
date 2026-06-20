---
series: software-design-101
episode: 7
title: "Software Design 101 (7/10): 데이터 흐름 설계"
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
  - DataFlow
  - Pipelines
  - Immutability
  - FunctionalDesign
seo_description: 데이터가 흐르는 방향을 명확히 하고, 파이프라인과 불변 데이터로 설계를 단순하게 만드는 방법을 정리합니다.
last_reviewed: '2026-05-15'
---

# Software Design 101 (7/10): 데이터 흐름 설계

같은 요청 객체를 여러 함수가 돌려 가며 수정하는 코드는 디버깅이 어렵습니다. 어디에서 이메일 값이 바뀌었는지, 어느 단계에서 유효성 검사가 통과됐는지, 왜 마지막 응답이 예상과 달라졌는지 한 번에 추적하기 힘들기 때문입니다.

이 글은 Software Design 101 시리즈의 7번째 글입니다.

여기서는 데이터 흐름을 설계한다는 말이 무엇인지, 입력에서 출력까지 한 방향 흐름을 어떻게 만들지, 작은 변환 함수의 파이프라인은 왜 유리한지, 불변 데이터와 부수효과 분리가 구조를 어떻게 단순하게 만드는지 살펴봅니다.

![Software Design 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/07/07-01-concept-at-a-glance.ko.png)
*Software Design 101 7장 흐름 개요*

> 데이터 흐름 설계는 '같은 객체를 여러 곳에서 고치게 두지 않는 일'입니다 — 입력에서 출력까지 한 방향으로 흐르고, 변환은 작은 함수로, 부수효과는 가장자리에 모일 때 디버깅과 테스트가 비로소 단순해집니다.

## 이 글에서 다룰 문제

- 데이터 흐름을 설계한다는 말은 구체적으로 무엇일까요?
- 입력과 출력 사이를 왜 한 방향으로만 흐르게 해야 할까요?
- 변환 단계와 부수효과는 어떻게 나누는 편이 좋을까요?
- 이 설계 원칙을 무시하면 코드베이스가 어떻게 변질될까요?
- 팀 규모가 커질 때 이 원칙의 중요성은 어떻게 달라질까요?

많은 버그는 데이터가 예상하지 못한 곳에서 조용히 바뀔 때 생깁니다. 공유된 가변 객체를 여러 단계가 수정하면 누가 상태를 바꿨는지 추적하기가 매우 어렵습니다.

반대로 데이터가 한 방향으로만 흐르고, 각 단계가 입력과 출력이 분명한 작은 변환으로 나뉘어 있으면 문제 범위를 빠르게 줄일 수 있습니다. 디버깅도 "어느 단계에서 값이 틀어졌는가"라는 질문으로 바뀝니다.

## 전체 그림

좋은 흐름은 짧고 분명합니다. 각 단계는 작은 책임만 맡고, 다음 단계로 값을 넘깁니다.

```text
한 방향 데이터 흐름 (목표)

HTTP Request
    │
    ▼
parse(payload) → SignupCommand   # 순수 변환
    │
    ▼
validate(cmd)  → ValidCmd        # 순수 변환 (실패 시 에러 반환)
    │
    ▼
normalize(cmd) → NormalizedCmd   # 순수 변환
    │
    ▼
to_user(cmd)   → User            # 순수 변환
    │
    ▼
repo.save(user) → SavedUser      # 부수효과 (가장자리)
    │
    ▼
mailer.send(user.email)          # 부수효과 (가장자리)
    │
    ▼
HTTP Response
```

## 기본 용어

- <strong>파이프라인</strong>: 작은 변환 함수들을 순서대로 연결한 구조입니다.
- <strong>순수 함수</strong>: 같은 입력에 같은 출력을 돌려주고, 부수효과가 없는 함수입니다.
- <strong>불변성</strong>: 값이 만들어진 뒤 바뀌지 않는 성질입니다.
- <strong>push 모델</strong>: 생산자가 소비자에게 데이터를 밀어 넣는 방식입니다.
- <strong>pull 모델</strong>: 소비자가 필요한 데이터를 가져오는 방식입니다.

## 변경 전과 변경 후

**변경 전 — 한 함수가 모든 것을 처리하고 객체를 제자리에서 수정**

```python
def process(req):
    # 어디서 이메일이 바뀌었는지 추적이 어려움
    if not req.get("email"):
        raise ValueError("email required")
    req["email"] = req["email"].lower()   # 제자리 수정
    if not req.get("name"):
        raise ValueError("name required")
    req["name"] = req["name"].strip()     # 제자리 수정
    db.save(req)                          # 부수효과가 중간에 섞임
    send_welcome(req["email"])            # 부수효과가 중간에 섞임
    req["status"] = "active"             # 또 제자리 수정
    return req                           # 수정된 원본 반환
```

**변경 후 — 각 단계가 새 값을 반환하고, 부수효과는 끝에만 있음**

```python
@dataclass(frozen=True)
class SignupPayload:
    email: str
    name: str

@dataclass(frozen=True)
class NormalizedPayload:
    email: str   # lower-cased
    name: str    # stripped

@dataclass(frozen=True)
class NewUser:
    email: str
    name: str

def parse(raw: dict) -> SignupPayload:
    return SignupPayload(email=raw["email"], name=raw["name"])

def validate(payload: SignupPayload) -> SignupPayload:
    if not payload.email:
        raise ValueError("email required")
    if not payload.name:
        raise ValueError("name required")
    return payload  # 불변: 새 값을 만들지 않고 검증만 통과

def normalize(payload: SignupPayload) -> NormalizedPayload:
    return NormalizedPayload(
        email=payload.email.lower(),  # 새 객체 반환
        name=payload.name.strip(),
    )

def to_user(payload: NormalizedPayload) -> NewUser:
    return NewUser(email=payload.email, name=payload.name)

def signup(raw: dict) -> None:
    # 순수 변환 단계 먼저
    user = to_user(normalize(validate(parse(raw))))
    # 부수효과를 끝으로 밀기
    repo.save(user)
    mailer.send_welcome(user.email)
```

두 번째 구조에서는 각 단계의 책임이 훨씬 분명합니다. 검증이 실패했는지, 정규화가 잘못됐는지, 저장 단계가 문제인지 흐름을 따라가며 바로 좁힐 수 있습니다.

## 흐름을 정리하는 다섯 단계

### 1단계 — 입력과 출력 모양을 적는다

```python
# 1_io.py
# 입력: HTTP에서 온 dict
# 출력: User row id
# 그 사이 과정을 단계별 한 줄씩 스케치하세요.
```

코드보다 먼저 입출력 형태를 적어 두면 변환 단계가 훨씬 선명해집니다. 어떤 값을 받고 어떤 값을 돌려주는지 모호하면 흐름도 쉽게 흐려집니다.

### 2단계 — 단계를 작은 함수로 나눈다

```python
# 2_steps.py
def parse(payload) -> SignupCommand: ...
def validate(cmd: SignupCommand) -> SignupCommand: ...
def to_user(cmd: SignupCommand) -> User: ...
```

각 단계는 입력과 출력이 분명해야 합니다. "무엇을 받아 무엇을 돌려주는가"가 보이면 조합도 쉬워지고 테스트도 단순해집니다.

### 3단계 — 부수효과를 끝으로 민다

```python
# 3_side_effects.py
def signup(payload):
    user = to_user(validate(parse(payload)))   # 순수 처리
    repo.save(user)                            # 부수효과
    mailer.send(user.email)                    # 부수효과
```

검증과 변환은 가능한 한 순수하게 두고, 저장과 발송 같은 IO는 가장자리에서 처리하는 편이 좋습니다. 이 구분이 선명할수록 테스트와 디버깅이 쉬워집니다.

### 4단계 — 불변 데이터를 기본값으로 둔다

```python
# 4_immutable.py
from dataclasses import dataclass
@dataclass(frozen=True)
class User:
    id: str
    email: str
```

값을 제자리에서 고치기보다 새 값을 만들어 반환하면 누가 상태를 바꿨는지 추적하기 쉽습니다. 여러 단계가 같은 객체를 몰래 수정하는 문제도 줄어듭니다.

### 5단계 — 흐름을 한 방향으로 유지한다

```python
# 5_one_way.py
# UI -> command -> domain -> event
# event는 다시 UI로 흐릅니다.
# 중간 흐름에서 조용히 데이터를 바꾸지 않습니다.
```

순환이나 중간 갱신이 많아질수록 디버깅 난도는 올라갑니다. 흐름이 한 방향이면 문제 원인도 단계별로 따라갈 수 있습니다.

## 순수 함수 vs 부수효과 비교

| 특성 | 순수 함수 | 부수효과 함수 |
| --- | --- | --- |
| 같은 입력 → 같은 출력 | 항상 | 아닐 수 있음 |
| 테스트 용이성 | 높음 | 낮음 (목킹 필요) |
| 디버깅 난도 | 낮음 | 높음 |
| 병렬 실행 | 안전 | 위험할 수 있음 |
| 위치 | 파이프라인 중간 | 파이프라인 가장자리 |
| 예시 | parse, validate, normalize | repo.save, mailer.send |

## 빠르게 검증해 보기

문제가 자주 나는 요청 하나를 골라, 각 단계가 입력과 출력을 무엇으로 받는지 한 줄씩 적어 보세요. 이 작업만으로도 중간에 값이 어디서 몰래 바뀌는지 보이기 시작합니다.

```text
payload(dict) -> SignupCommand -> User -> saved User -> notification event
```

**Expected output:** 단계마다 데이터 모양이 드러나고, 어느 단계가 순수 변환인지 어느 단계가 부수효과인지 분리해서 설명할 수 있어야 합니다.

가능하면 각 단계 전후 값을 로그 한 줄로 남긴다고 가정해 보세요. 한 방향 흐름은 그 로그를 읽는 순서까지 단순하게 만듭니다.

## 실패 신호와 먼저 볼 것

| 실패 신호 | 먼저 볼 것 |
| --- | --- |
| 같은 dict를 여러 함수가 계속 수정한다 | 불변 데이터나 새 객체 반환으로 바꿀 수 있는지 봅니다 |
| 검증 중간에 DB 호출이 들어간다 | 순수 변환과 부수효과 경계를 다시 나눕니다 |
| 디버깅할 때 값이 어디서 바뀌었는지 모르겠다 | 단계별 입력/출력 타입을 먼저 적어 봅니다 |

흐름이 선명해지면 버그를 잡을 때도 "모든 코드를 본다"가 아니라 "어느 단계에서 값이 틀어졌는가"라는 질문으로 바로 들어갈 수 있습니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 올바른 접근 |
| --- | --- | --- |
| 공유 dict를 여러 함수가 수정 | 어느 단계에서 값이 바뀌었는지 추적 불가 | 각 단계가 새 객체를 반환 |
| 검증 중간에 DB 호출 삽입 | 순수 변환과 부수효과 경계가 무너짐 | 부수효과를 파이프라인 끝으로 밀기 |
| 제자리 수정(mutation) 남용 | 동시성 문제, 추적 어려움 | frozen dataclass나 반환 방식 사용 |
| 단계가 너무 많아 파이프라인이 복잡 | 가독성 저하, 디버깅 어려움 | 자주 함께 변환되는 단계를 묶기 |
| 흐름 중간에서 되돌아가기 | 순환 흐름은 추적과 테스트 모두 어려움 | 이벤트나 결과 객체로 방향 유지 |

## 이 코드에서 먼저 볼 점

- 단계마다 책임이 좁고 선명합니다.
- 부수효과는 한쪽 가장자리로 몰립니다.
- 데이터가 중간에 되돌아가거나 몰래 수정되지 않습니다.

## 어디서 많이 헷갈릴까

함수를 잘게 나누기만 하면 데이터 흐름 설계가 된다고 생각하기 쉽습니다. 하지만 각 함수가 공유 객체를 계속 수정한다면 흐름은 여전히 탁합니다. 분해보다 더 중요한 것은 값이 어떻게 이동하고 언제 바뀌는지입니다.

또 하나 흔한 문제는 중간 단계에서 바로 데이터베이스나 외부 API를 호출하는 습관입니다. 검증과 변환 중간에 IO가 끼어들면 흐름이 진흙처럼 섞입니다. 어떤 단계가 순수한 변환인지, 어떤 단계가 부수효과인지 경계가 흐려지기 때문입니다.

## 실무에서는 이렇게 본다

ETL 파이프라인, 요청 처리 흐름, React의 단방향 상태 흐름처럼 데이터 흐름 설계는 여러 곳에 반복해서 등장합니다. 한 방향 흐름이 익숙한 팀은 장애가 나도 "값이 어디서 바뀌었나"를 빠르게 좁힙니다.

코드 리뷰에서는 입력과 출력 타입이 분명한가, 중간 단계가 공유 상태를 수정하는가, 부수효과가 끝에 몰려 있는가를 먼저 보는 편이 좋습니다. 이 질문만으로도 구조의 대부분이 드러납니다.

```python
# 실무 패턴: 파이프라인을 함수 조합으로 표현
from functools import reduce
from typing import TypeVar, Callable

T = TypeVar("T")

def pipeline(*fns: Callable) -> Callable:
    """여러 변환 함수를 순서대로 연결"""
    return lambda x: reduce(lambda v, f: f(v), fns, x)

# 사용 예
process_signup = pipeline(
    parse,
    validate,
    normalize,
    to_user,
)

def signup(raw: dict) -> None:
    user = process_signup(raw)  # 순수 파이프라인
    repo.save(user)             # 부수효과
    mailer.send(user.email)     # 부수효과
```

## 운영 체크리스트

- [ ] 데이터가 한 방향으로 흐르는가?
- [ ] 부수효과가 가장자리에 모여 있는가?
- [ ] 각 단계가 작은 책임만 맡는가?
- [ ] 가능한 곳에서는 불변 데이터를 쓰는가?
- [ ] 타입이나 구조로 데이터 모양이 보장되는가?

## 연습 문제

1. 현재 함수 하나를 골라 순수 변환과 부수효과를 나눠 보세요.
2. dict 기반 입력 하나를 dataclass 기반 구조로 바꿔 보세요.
3. 데이터가 거꾸로 흐르거나 중간에서 갱신되는 지점을 하나 찾아 개선 방향을 적어 보세요.

## 불변 데이터 패턴 적용 전후 비교

파이썬에서 불변 데이터를 쓰는 가장 간단한 방법은 `frozen=True` dataclass입니다. 가변 dict와 비교하면 추적 가능성 차이가 명확합니다.

```python
# ── 가변 dict 사용 (문제 있음) ────────────────────

def pipeline_mutable(raw: dict) -> dict:
    # 어느 단계에서 email이 바뀌었는지 추적 어려움
    raw["email"] = raw["email"].lower()    # 제자리 수정
    if not raw.get("name"):
        raise ValueError("name required")
    raw["status"] = "pending"              # 또 제자리 수정
    raw["created_at"] = "2026-01-01"      # 또 제자리 수정
    return raw  # 원본이 수정된 상태로 반환됨

data = {"email": "HELLO@EXAMPLE.COM", "name": "Kim"}
result = pipeline_mutable(data)
# data["email"]이 "hello@example.com"으로 바뀐 것을 알아채기 어려움


# ── 불변 dataclass 사용 (권장) ────────────────────

from dataclasses import dataclass

@dataclass(frozen=True)
class RawInput:
    email: str
    name: str

@dataclass(frozen=True)
class ValidInput:
    email: str
    name: str

@dataclass(frozen=True)
class NormalizedInput:
    email: str   # 항상 소문자
    name: str    # 항상 strip됨

def validate(raw: RawInput) -> ValidInput:
    if not raw.name:
        raise ValueError("name required")
    return ValidInput(email=raw.email, name=raw.name)
    # raw는 변경되지 않음. 새 객체를 반환

def normalize(valid: ValidInput) -> NormalizedInput:
    return NormalizedInput(
        email=valid.email.lower(),   # 새 객체
        name=valid.name.strip(),     # 새 객체
    )
    # valid는 변경되지 않음

raw = RawInput(email="HELLO@EXAMPLE.COM", name="  Kim  ")
valid = validate(raw)
normalized = normalize(valid)

# raw.email은 여전히 "HELLO@EXAMPLE.COM" — 수정 없음
# 각 단계의 결과를 독립적으로 확인 가능
```

## 파이프라인 테스트 전략

단방향 흐름과 불변 데이터의 가장 큰 이점은 테스트가 쉬워진다는 점입니다.

```python
# 각 단계를 독립적으로 테스트

def test_validate_rejects_empty_name():
    raw = RawInput(email="a@b.com", name="")
    with pytest.raises(ValueError):
        validate(raw)

def test_normalize_lowercases_email():
    valid = ValidInput(email="HELLO@EXAMPLE.COM", name="Kim")
    result = normalize(valid)
    assert result.email == "hello@example.com"
    assert result.name == "Kim"  # strip은 이미 했음

def test_normalize_strips_name():
    valid = ValidInput(email="a@b.com", name="  Kim  ")
    result = normalize(valid)
    assert result.name == "Kim"

# 단계를 조합해 통합 테스트
def test_full_pipeline():
    raw = RawInput(email="HELLO@EXAMPLE.COM", name="  Kim  ")
    result = normalize(validate(raw))
    assert result.email == "hello@example.com"
    assert result.name == "Kim"
```

순수 함수만으로 구성된 파이프라인은 외부 의존성 없이 빠르게 테스트할 수 있습니다. 부수효과 함수(저장, 발송)는 별도로 목킹해서 테스트합니다.

## 현업 적용 관점에서 다시 정리

데이터 흐름 설계는 디버깅 비용을 줄이는 가장 직접적인 방법입니다. 입력과 출력의 형태를 단계별로 고정해 두면 추적 가능성이 크게 좋아집니다.

## 정리

데이터 흐름 설계는 '같은 객체를 여러 곳에서 고치게 두지 않는 일'입니다 — 입력에서 출력까지 한 방향으로 흐르고, 변환은 작은 함수로, 부수효과는 가장자리에 모일 때 디버깅과 테스트가 비로소 단순해집니다. 이 글에서는 전체 그림부터 현업 적용 관점에서 다시 정리까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **데이터 흐름을 설계한다는 말은 구체적으로 무엇일까요?**
  - 입력에서 출력까지 각 단계의 데이터 모양을 명확히 정의하고, 값이 한 방향으로만 이동하며 중간에 몰래 수정되지 않도록 만드는 일입니다. 코드보다 먼저 입출력 형태를 적어 두면 변환 단계가 훨씬 선명해집니다.
- **입력과 출력 사이를 왜 한 방향으로만 흐르게 해야 할까요?**
  - 순환이나 제자리 수정이 생기면 "어느 단계에서 값이 바뀌었는가"를 추적하기 매우 어렵습니다. 단방향 흐름은 문제 범위를 특정 단계로 좁힐 수 있게 합니다.
- **변환 단계와 부수효과는 어떻게 나누는 편이 좋을까요?**
  - 검증, 정규화, 변환 등 순수 함수는 파이프라인 중간에, DB 저장·이메일 발송 같은 IO는 파이프라인 끝에 모아야 합니다. 이 구분이 선명할수록 각 단계를 독립적으로 테스트하기 쉬워집니다.
