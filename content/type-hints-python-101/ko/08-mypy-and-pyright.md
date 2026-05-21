---
series: type-hints-python-101
episode: 8
title: "Type Hints in Python 101 (8/10): mypy와 pyright 사용하기"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Type Hints
  - mypy
  - pyright
  - 정적 분석
  - CI
seo_description: mypy와 pyright를 설정하고 프로젝트에 점진적으로 도입하여 타입 오류를 자동 검출하는 방법을 다룹니다.
last_reviewed: '2026-05-17'
---

# Type Hints in Python 101 (8/10): mypy와 pyright 사용하기

타입 힌트를 붙였는데도 실제로 검사기를 돌리지 않으면 계약은 문서에만 머뭅니다. 특히 반환 타입이 어긋나거나 `None` 처리가 빠진 코드는 실행 전까지 조용히 숨어 있다가, 배포 뒤에야 문제를 드러내기 쉽습니다.

이 글은 Type Hints (Python) 101 시리즈의 8번째 글입니다. 여기서는 하나의 작은 예제 저장소를 기준으로 mypy와 pyright가 같은 오류를 어떻게 잡는지, 설정을 어떻게 점진적으로 강화하는지, 마지막으로 CI 게이트까지 어떻게 연결하는지를 순서대로 정리합니다.

## 먼저 던지는 질문

- 타입 힌트를 코드 실행 없이 어떻게 검증할까요?
- mypy와 pyright는 같은 코드에서 어떤 식으로 오류를 보여 줄까요?
- strict 모드는 기존 저장소에 어떻게 점진적으로 도입할까요?

## 큰 그림

![Type Hints in Python 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/08/08-01-concept-at-a-glance.ko.png)

*Type Hints in Python 101 8장 흐름 개요*

## 왜 이 주제가 중요한가

Python 인터프리터는 타입 힌트를 강제하지 않습니다. 즉, `-> str`이라고 적어도 실제 구현이 `None`을 돌려주면 런타임까지 조용히 지나갈 수 있습니다. 이 간극을 메우는 도구가 mypy와 pyright입니다.

둘 다 소스 코드를 실행하지 않고 읽으면서 타입 불일치를 찾지만, 운영 관점에서는 더 중요한 질문이 있습니다. "어떤 예제 코드에서 어떤 오류가 나고, 그 코드를 어떻게 고치며, 그 검사를 어떻게 CI까지 연결할 것인가?" 이 글은 그 질문에 답하도록 하나의 흐름으로 설명합니다.

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| mypy | Python 생태계에서 가장 널리 쓰이는 정적 타입 검사기입니다 |
| pyright | Microsoft가 만든 빠른 타입 검사기이며 Pylance의 기반입니다 |
| strict mode | 타입 힌트 누락과 느슨한 추론을 더 적극적으로 오류로 보는 설정입니다 |
| override | 특정 패키지나 디렉터리에만 다른 검사 규칙을 적용하는 설정입니다 |
| CI gate | 검사 실패 시 PR 병합을 막는 자동화 단계입니다 |

## 바꾸기 전과 후

```python
def normalize_user_id(raw_user_id: str) -> int:
    return raw_user_id

def build_greeting(name: str | None) -> str:
    return "Hello, " + name.upper()
```

```text
$ mypy src
src/accounts.py:5: error: Incompatible return value type (got "str", expected "int")
src/accounts.py:9: error: Item "None" of "str | None" has no attribute "upper"
Found 2 errors in 1 file (checked 1 source file)
```

타입 힌트만 적어 둔 상태에서는 조용했던 코드가, 검사기를 붙이는 순간 배포 전에 실패하기 시작합니다. 이 실패가 바로 품질 게이트입니다.

## 하나의 예제 저장소로 끝까지 따라가기

이 글 전체에서는 아래 구조를 같은 예제로 사용합니다.

```text
typecheck-demo/
├── pyproject.toml
├── pyrightconfig.json
├── src/
│   └── accounts.py
└── .github/
    └── workflows/
        └── type-check.yml
```

### 1단계: 일부러 타입 오류를 넣은 코드 준비하기

```python
# src/accounts.py
from typing import TypedDict

class UserRow(TypedDict):
    id: int
    email: str
    display_name: str | None

def normalize_user_id(raw_user_id: str) -> int:
    return raw_user_id

def build_greeting(user: UserRow) -> str:
    return "Hello, " + user["display_name"].upper()

def list_admin_emails(rows: list[UserRow]) -> list[str]:
    return [row["email"] for row in rows if row["id"] in {1, 2, 3}]
```

의도적으로 넣어 둔 오류는 두 가지입니다.

- `normalize_user_id()`는 `int`를 약속했지만 `str`을 그대로 반환합니다.
- `build_greeting()`은 `display_name`이 `None`일 수 있는데 바로 `.upper()`를 호출합니다.

### 2단계: 같은 코드에 mypy를 실행해 실제 실패를 확인하기

```bash
python -m pip install mypy
mypy src
```

```text
src/accounts.py:10: error: Incompatible return value type (got "str", expected "int")  [return-value]
src/accounts.py:14: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
Found 2 errors in 1 file (checked 1 source file)
```

mypy는 반환 타입 오류와 `None` 가능성 누락을 바로 분리해서 보여 줍니다. 이 단계의 장점은 "무엇이 틀렸는지"를 코드 리뷰 전에 명확하게 확인할 수 있다는 점입니다.

### 3단계: 같은 코드에 pyright를 실행해 두 번째 관점을 얻기

```bash
python -m pip install pyright
pyright src
```

```text
/Users/username/typecheck-demo/src/accounts.py
  /Users/username/typecheck-demo/src/accounts.py:10:12 - error: Type "str" is not assignable to return type "int"
    "str" is not assignable to "int" (reportReturnType)
  /Users/username/typecheck-demo/src/accounts.py:14:38 - error: "upper" is not a known attribute of "None" (reportOptionalMemberAccess)
2 errors, 0 warnings, 0 informations
```

pyright도 같은 두 문제를 잡지만, 에디터에서 바로 보이는 오류 코드와 메시지 구조가 다릅니다. 그래서 많은 팀이 **로컬 편집 단계에서는 pyright/Pylance**, **병합 게이트에서는 mypy** 같은 식으로 역할을 나눠 씁니다.

### 4단계: 코드를 고쳐 두 검사기가 모두 통과하게 만들기

```python
# src/accounts.py
from typing import TypedDict

class UserRow(TypedDict):
    id: int
    email: str
    display_name: str | None

def normalize_user_id(raw_user_id: str) -> int:
    return int(raw_user_id)

def build_greeting(user: UserRow) -> str:
    display_name = user["display_name"]
    if display_name is None:
        return "Hello, anonymous"
    return "Hello, " + display_name.upper()

def list_admin_emails(rows: list[UserRow]) -> list[str]:
    return [row["email"] for row in rows if row["id"] in {1, 2, 3}]
```

```text
$ mypy src
Success: no issues found in 1 source file

$ pyright src
0 errors, 0 warnings, 0 informations
```

이제야 타입 힌트가 문서가 아니라 **검증 가능한 계약**이 됩니다. 중요한 것은 설치 명령 자체가 아니라, 같은 코드가 실패했다가 수정 후 통과하는 흐름입니다.

### 5단계: 느슨한 기본 설정에서 시작하기

처음부터 저장소 전체에 strict를 켜기보다, 통과하는 기준선을 먼저 만드는 편이 현실적입니다.

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
files = ["src"]
check_untyped_defs = true
warn_return_any = true
warn_unused_ignores = true
```

```json
{
  "include": ["src"],
  "pythonVersion": "3.11",
  "typeCheckingMode": "basic",
  "reportMissingImports": true,
  "reportMissingTypeStubs": false
}
```

이 단계에서는 다음 두 가지를 먼저 확보합니다.

- 검사기가 항상 같은 디렉터리를 보게 합니다.
- 팀이 "지금부터는 이 코드가 통과 기준"이라는 공통 감각을 갖게 합니다.

### 6단계: 핵심 모듈만 먼저 더 엄격하게 만들기

기존 코드베이스에서 가장 흔한 실패는 저장소 전체 strict입니다. 더 안전한 방법은 핵심 모듈만 먼저 올리는 것입니다.

```toml
[tool.mypy]
python_version = "3.11"
files = ["src"]
check_untyped_defs = true
warn_return_any = true
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = "src.accounts"
strict = true

[[tool.mypy.overrides]]
module = "src.legacy.*"
ignore_errors = true
```

```json
{
  "include": ["src"],
  "pythonVersion": "3.11",
  "typeCheckingMode": "basic",
  "strict": ["src/accounts.py"],
  "exclude": ["src/legacy"]
}
```

핵심은 "전체를 완벽하게"가 아니라 **새 코드와 중요한 경로부터 실패하게 만들기**입니다. 이렇게 해야 오류 수가 팀의 처리 용량을 넘지 않습니다.

### 7단계: CI 게이트로 연결해 로컬 실수를 병합 전에 막기

```yaml
# .github/workflows/type-check.yml
name: Type Check

on:
  pull_request:
  push:
    branches:
      - master

jobs:
  static-type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install checkers
        run: |
          python -m pip install --upgrade pip
          python -m pip install mypy pyright
      - name: Run mypy
        run: mypy src
      - name: Run pyright
        run: pyright src
```

이제 개발자가 로컬에서 한 번 놓친 타입 오류도 PR 단계에서 다시 걸립니다. 팀이 타입 힌트를 실제 규칙으로 운영하려면 이 단계가 빠지면 안 됩니다.

### 8단계: 운영 규칙을 정해 noise를 줄이기

실무에서는 검사기를 붙인 뒤 아래 규칙까지 정해야 마찰이 줄어듭니다.

1. **표준 병합 게이트를 하나 정합니다.** 예를 들어 PR 차단은 mypy, 에디터 피드백은 pyright처럼 역할을 나눕니다.
2. **`type: ignore`에는 이유를 남깁니다.** 스텁 부재인지, 도구 한계인지, 임시 예외인지 기록합니다.
3. **strict 후보 디렉터리를 주기적으로 다시 선정합니다.** `legacy`를 영구 면책 구역으로 두면 안 됩니다.

```python
from third_party_sdk import build_client

client = build_client()  # type: ignore[no-untyped-call]  # SDK v2에 타입 스텁이 아직 없음
```

## 여기서 먼저 봐야 할 점

- 설치 명령보다 중요한 것은 **같은 코드가 실패하고, 수정 후 통과하는 흐름**입니다.
- mypy와 pyright는 같은 버그를 다른 형식으로 보여 줄 수 있습니다.
- strict는 전체 저장소가 아니라 핵심 모듈부터 올리는 편이 현실적입니다.
- CI까지 연결해야 타입 힌트가 개인 습관이 아니라 팀 규칙이 됩니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| 설치 명령만 문서화하고 실제 실패 예제를 안 보여 줌 | 독자가 "무엇이 검출되는지"를 확인하지 못합니다 | 같은 코드에서 오류 출력까지 보여 줍니다 |
| strict를 저장소 전체에 바로 적용함 | 오류 양이 팀 수용 범위를 넘습니다 | 핵심 디렉터리부터 override로 올립니다 |
| 두 도구를 모두 필수 게이트로 강제함 | 엣지 케이스 차이로 운영 비용이 커집니다 | 하나를 병합 기준, 하나를 보조 도구로 둡니다 |
| `type: ignore`에 이유를 남기지 않음 | 예외가 기술 부채로 굳습니다 | 오류 코드와 사유를 함께 적습니다 |
| 로컬 실행만 믿고 CI를 연결하지 않음 | 사람마다 검사 습관이 달라집니다 | PR과 push에서 자동 실행합니다 |

## 실무에서는 이렇게 연결됩니다

- VS Code + Pylance로 pyright 오류를 실시간 확인합니다.
- PR 게이트에서는 mypy 또는 pyright 중 하나를 표준으로 둡니다.
- 새 패키지나 핵심 패키지부터 strict를 적용합니다.
- 레거시 디렉터리는 일시적으로 완화하되, 분기마다 축소 계획을 잡습니다.

## 실무 판단 기준

경험 많은 개발자는 타입 검사를 "옵션 기능"이 아니라 테스트, 린트와 같은 기본 인프라로 봅니다. 새 프로젝트라면 첫날부터 최소 설정과 CI 게이트를 붙이고, 기존 프로젝트라면 에러 개수를 팀이 감당할 수 있는 단위로 나눠 strict를 확장합니다.

도구 선택 자체보다 중요한 것은 일관성입니다. 어느 검사기가 merge gate인지, 어떤 디렉터리가 다음 strict 대상인지, ignore를 어떤 기준으로 허용할지까지 정해야 타입 힌트가 실제 운영 규칙이 됩니다.

## 체크리스트

- [ ] 하나의 예제 모듈에 mypy와 pyright를 모두 실행해 봤습니다
- [ ] 실제 오류 출력과 수정 후 통과 결과를 확인했습니다
- [ ] `pyproject.toml`과 `pyrightconfig.json`에 기준선을 만들었습니다
- [ ] strict 도입 대상을 모듈 단위로 정했습니다
- [ ] CI에서 타입 검사가 자동으로 실패하도록 연결했습니다

## 연습 문제

1. `src/` 아래에 반환 타입 오류와 `Optional` 처리 누락을 하나씩 넣고, mypy와 pyright가 각각 어떤 메시지를 내는지 비교해 보세요.

2. `src/core`만 strict로, `src/legacy`는 일시적으로 완화하는 설정을 직접 작성해 보세요.

3. PR에서는 mypy만 차단 게이트로 쓰고, pyright는 참고용 리포트로 두는 운영 정책을 팀 문서에 써 보세요.

## 정리와 다음 글

mypy와 pyright는 타입 힌트를 실제 품질 게이트로 바꿔 주는 도구입니다. 하나의 예제 코드에서 실패와 성공을 모두 확인하고, 설정을 단계적으로 강화한 뒤, CI까지 연결해야 타입 힌트가 문서가 아니라 운영 규칙이 됩니다.

다음 글에서는 이 정적 검증 바깥에서, 들어오는 데이터를 런타임에 검사하는 Pydantic을 살펴보겠습니다.


## 실전 보강: before/after + 오류 해결

```python
# before
from typing import Any

def build(value: Any) -> Any:
    return value
```

```python
# after
from typing import TypeVar

T = TypeVar("T")

def build(value: T) -> T:
    return value
```

```text
before 상태에서는 검사기가 의미 있는 오류를 거의 만들지 못합니다.
after 상태에서는 호출부 타입 불일치를 정확히 보고합니다.
```

## 팀 운영 패턴

| 단계 | 실행 항목 |
| --- | --- |
| 로컬 개발 | pyright/Pylance 즉시 피드백 |
| PR 전 검증 | mypy 단일 명령 통과 |
| CI 게이트 | 실패 시 병합 차단 |
| 예외 관리 | `type: ignore`에 사유와 코드 기재 |



## mypy 오류를 읽는 순서

실무에서는 오류 개수보다 읽는 순서가 더 중요합니다. 다음 순서를 고정하면 수정 시간이 크게 줄어듭니다.

1. `error:` 뒤의 핵심 문장을 먼저 읽고, 기대 타입과 실제 타입을 분리합니다.
2. 함수 시그니처 오류인지, 호출부 오류인지 위치를 구분합니다.
3. `Any`가 끼어 있는지 확인합니다. `Any`가 있으면 오류 메시지가 흐려집니다.
4. 마지막으로 수정 코드를 넣고 같은 파일만 다시 검사합니다.

```bash
mypy content/type-hints-python-101/examples/episode.py
```

```text
example.py:42: error: Incompatible return value type (got "str", expected "int")  [return-value]
example.py:51: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
Found 2 errors in 1 file (checked 1 source file)
```

위 출력에서 첫 줄은 반환 계약 위반, 둘째 줄은 Optional 처리 누락입니다. 즉, 타입 힌트 작성과 별개로 **오류를 분류해서 고치는 습관**이 필요합니다.

## 팀 적용 체크포인트

| 항목 | 느슨한 상태 | 권장 상태 |
| --- | --- | --- |
| 공개 함수 시그니처 | 일부 누락 | 모두 명시 |
| `Any` 사용 | 편의상 광범위 사용 | 경계에서만 제한적 사용 |
| Optional 처리 | 호출부 임의 처리 | `None` 분기 패턴 고정 |
| 정적 검사 | 로컬 선택 실행 | CI 필수 게이트 |
| 코드 리뷰 | 스타일 중심 | 타입 계약 위반 중심 |

이 체크포인트를 팀 규칙으로 두면 신규 코드와 레거시 코드의 품질 편차를 줄일 수 있습니다.


## 실전 보강: 타입 힌트 + mypy 오류 해결 루프

아래 예시는 타입 힌트가 문서가 아니라 검증 가능한 계약이라는 점을 분명하게 보여 줍니다.

```python
from typing import TypedDict

class Payment(TypedDict):
    order_id: int
    amount: int
    currency: str


def normalize_amount(raw: int | str) -> int:
    if isinstance(raw, int):
        return raw
    if raw.isdigit():
        return int(raw)
    raise ValueError("amount must be int or numeric string")


def build_payment(order_id: int, amount: int | str, currency: str | None) -> Payment:
    if currency is None:
        raise ValueError("currency is required")
    return {
        "order_id": order_id,
        "amount": normalize_amount(amount),
        "currency": currency.upper(),
    }
```

```python
# 오류를 일부러 넣은 버전

def build_payment(order_id: int, amount: int | str, currency: str | None) -> Payment:
    return {
        "order_id": str(order_id),
        "amount": amount,
        "currency": currency.upper(),
    }
```

```text
example.py:24: error: Incompatible types (expression has type "str", TypedDict item "order_id" has type "int")  [typeddict-item]
example.py:25: error: Incompatible types (expression has type "int | str", TypedDict item "amount" has type "int")  [typeddict-item]
example.py:26: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
Found 3 errors in 1 file (checked 1 source file)
```

위 메시지는 각각 키 타입 불일치, Union 좁히기 누락, Optional 처리 누락을 의미합니다. 즉, 정적 분석기가 실제 운영 버그 후보를 실행 전에 보여 준다는 뜻입니다.

## before/after 요약

| 구분 | before (느슨한 타입) | after (구체 타입) |
| --- | --- | --- |
| 입력 계약 | `dict`, `Any` 위주 | `TypedDict`, `Union`, `Optional` 명시 |
| 오류 발견 시점 | 테스트/운영 단계 | 커밋 전 타입 검사 단계 |
| 코드 리뷰 초점 | 스타일/명명 | 계약 위반/경계 검증 |
| 리팩터링 안정성 | 변경 영향 추적 어려움 | 시그니처 기반 영향 추적 가능 |

## Optional vs Union 판단 표

| 상황 | 권장 타입 | 이유 |
| --- | --- | --- |
| 값이 없을 수 있음 | `T | None` | 부재 가능성을 명시적으로 표현 |
| 입력 포맷이 둘 이상 | `T1 | T2` | 허용 범위를 코드로 고정 |
| 외부 입력 정규화 | `str | int` -> `int` | 경계에서 한 번만 변환 |
| 내부 도메인 모델 | 가능한 단일 타입 유지 | 분기 복잡도 축소 |

## Protocol vs ABC 판단 표

| 기준 | Protocol | ABC |
| --- | --- | --- |
| 호환성 기준 | 구조(메서드/속성) | 명시적 상속 |
| 외부 클래스 수용 | 유리함 | 불리함 |
| 공통 구현 제공 | 제한적 | 유리함 |
| 대규모 플러그인 구조 | 유리함 | 상황별 |

## 실무 패턴: 타입 힌트 적용 순서

1. 공개 함수와 반환 타입부터 고정합니다.
2. `Any`를 반환하는 경계 함수를 구체 타입으로 줄입니다.
3. `Optional`과 `Union` 분기를 helper 함수로 끌어올립니다.
4. mypy/pyright를 CI에 연결해 회귀를 막습니다.

```bash
mypy content/type-hints-python-101/ko
```

```text
Success: no issues found in N source files
```

위 결과가 나오더라도 끝이 아닙니다. 새로운 기능을 추가할 때 같은 원칙을 반복해 계약을 유지해야 타입 힌트가 장기적으로 품질을 지켜 줍니다.



## 추가 사례: 주문 처리 모듈 타입 하드닝

아래 코드는 실제로 자주 보는 레거시 패턴입니다.

```python
from typing import Any


def build_invoice(payload: dict[str, Any]) -> dict[str, Any]:
    user = payload.get("user")
    total = payload.get("total")
    return {
        "email": user.get("email"),
        "total": int(total),
    }
```

이 구현은 `user` 누락, `total` 비정상 값, 잘못된 타입을 조용히 통과시킵니다. 아래처럼 경계를 분리하면 검증 경로가 명확해집니다.

```python
from typing import TypedDict

class UserInfo(TypedDict):
    email: str

class InvoicePayload(TypedDict):
    user: UserInfo
    total: int | str

class InvoiceResult(TypedDict):
    email: str
    total: int


def parse_total(raw: int | str) -> int:
    if isinstance(raw, int):
        return raw
    if raw.isdigit():
        return int(raw)
    raise ValueError("total must be int or numeric string")


def build_invoice(payload: InvoicePayload) -> InvoiceResult:
    return {
        "email": payload["user"]["email"],
        "total": parse_total(payload["total"]),
    }
```

```text
before: 런타임 오류 중심
after: 타입 오류 + 명시적 예외 중심
```

## mypy 출력 해석 연습

```text
service.py:18: error: Key "email" of TypedDict "UserInfo" cannot be deleted  [misc]
service.py:29: error: Argument 1 to "parse_total" has incompatible type "float"; expected "int | str"  [arg-type]
service.py:36: error: Missing key "user" for TypedDict "InvoicePayload"  [typeddict-item]
```

- 첫 번째 오류는 구조적 계약 위반입니다.
- 두 번째 오류는 허용 타입 범위를 벗어난 호출입니다.
- 세 번째 오류는 필수 필드 누락입니다.

즉, 오류는 단순 문법 문제가 아니라 **도메인 계약 위반 지표**로 해석해야 합니다.

## 운영 적용 포인트

- 새 기능 PR에서는 최소한 공개 함수의 반환 타입을 반드시 명시합니다.
- 외부 입력 파싱 함수에는 `Optional`/`Union` 처리 분기를 강제합니다.
- 리뷰에서 `Any` 추가가 보이면 대체 타입 후보를 함께 요구합니다.
- CI에서는 타입 검사 실패를 테스트 실패와 동등하게 취급합니다.



## 운영용 명령 세트

팀에서는 아래 명령을 고정해 두면 재현성이 좋아집니다.

```bash
python -m pip install mypy pyright
mypy src
pyright src
```

```text
mypy: 반환 타입/Optional 누락을 CI 게이트로 차단
pyright: 로컬 편집 단계에서 즉시 피드백 제공
```

두 도구의 역할을 분리하면 개발자 경험과 병합 안정성을 동시에 확보하기 쉽습니다.

## 처음 질문으로 돌아가기

- **타입 힌트를 코드 실행 없이 어떻게 검증할까요?**
  - 본문의 기준은 mypy와 pyright 사용하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **mypy와 pyright는 같은 코드에서 어떤 식으로 오류를 보여 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **strict 모드는 기존 저장소에 어떻게 점진적으로 도입할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Type Hints in Python 101 (1/10): Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [Type Hints in Python 101 (2/10): 기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Type Hints in Python 101 (3/10): Optional과 Union](./03-optional-and-union.md)
- [Type Hints in Python 101 (4/10): 함수 타입 힌트](./04-function-type-hints.md)
- [Type Hints in Python 101 (5/10): TypedDict와 dataclass](./05-typeddict-and-dataclass.md)
- [Type Hints in Python 101 (6/10): Protocol과 structural typing](./06-protocol-and-structural-typing.md)
- [Type Hints in Python 101 (7/10): Generic 이해하기](./07-generic.md)
- **mypy와 pyright 사용하기 (현재 글)**
- Pydantic과 타입 힌트 (예정)
- 타입 힌트를 잘 쓰는 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [mypy 공식 문서](https://mypy.readthedocs.io/en/stable/)
- [pyright 공식 문서](https://github.com/microsoft/pyright)
- [mypy 설정 레퍼런스](https://mypy.readthedocs.io/en/stable/config_file.html)
- [mypy 문서 — 기존 코드베이스에 도입하기](https://mypy.readthedocs.io/en/stable/existing_code.html)
- [pyright 설정 문서](https://microsoft.github.io/pyright/#/configuration)
- [Real Python — Python Type Checking](https://realpython.com/python-type-checking/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/type-hints-python-101/ko)
Tags: Python, Type Hints, mypy, pyright, 정적 분석, CI
