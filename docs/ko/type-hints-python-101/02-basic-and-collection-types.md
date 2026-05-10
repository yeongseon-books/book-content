---
series: type-hints-python-101
episode: 2
title: 기본 타입과 collection 타입
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Type Hints
  - 컬렉션 타입
  - list
  - dict
  - tuple
seo_description: int, str부터 list, dict, tuple까지 Python 타입 힌트의 기본 타입과 컬렉션 타입을 다룹니다.
last_reviewed: '2026-05-04'
---

# 기본 타입과 collection 타입

> Type Hints in Python 101 시리즈 (2/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 리스트 안에 어떤 타입의 원소가 들어있는지 타입 힌트로 표현할 수 있을까요?

> Python의 기본 타입(`int`, `str`, `float`, `bool`)은 직관적이지만, 컬렉션(`list`, `dict`, `tuple`, `set`)은 원소 타입까지 명시해야 의미가 완전해집니다. 이 글에서는 기본 타입과 컬렉션 타입의 힌트 작성법을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 기본 스칼라 타입(`int`, `str`, `float`, `bool`) 힌트
- 컬렉션 타입(`list`, `dict`, `tuple`, `set`) 힌트
- Python 3.9+ 내장 타입 vs `typing` 모듈
- 중첩 컬렉션 타입 표현

## 왜 중요한가

`items: list`라고만 쓰면 리스트 안에 무엇이 들어있는지 알 수 없습니다. `items: list[str]`로 원소 타입을 명시하면 IDE와 mypy가 잘못된 원소 삽입을 바로 잡아줍니다.

> 컬렉션 타입 힌트 = 원소 타입까지 명시

Python 3.9부터 `list[int]`, `dict[str, int]`처럼 내장 타입을 직접 사용할 수 있어 `typing.List`, `typing.Dict` 임포트가 불필요합니다.

## 핵심 개념 잡기

> 스칼라 타입 vs 컬렉션 타입

```
스칼라 타입                    컬렉션 타입
─────────────────            ─────────────────
int, str, float, bool        list[T], dict[K, V]
단일 값                       여러 값의 모음
age: int = 30                scores: list[int] = [85, 92]
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 스칼라 타입 | 단일 값을 표현하는 타입입니다 (`int`, `str`, `float`, `bool`) |
| 제네릭 표기 | 컬렉션의 원소 타입을 `[]`로 명시하는 방식입니다 |
| `list[T]` | 원소가 모두 T 타입인 리스트입니다 |
| `dict[K, V]` | 키가 K, 값이 V 타입인 딕셔너리입니다 |
| `tuple[T, ...]` | 가변 길이 튜플(모든 원소 T)입니다 |

## Before / After

타입 정보 없는 컬렉션을 제네릭 표기로 개선합니다.

```python
# before: 원소 타입을 알 수 없음
def get_names(users):
    return [u["name"] for u in users]
```

```python
# after: 입력과 출력의 타입이 명확
def get_names(users: list[dict[str, str]]) -> list[str]:
    return [u["name"] for u in users]
```

## 단계별 실습

### Step 1: 기본 스칼라 타입

```python
# 기본 타입 — Python 내장 타입 그대로 사용
name: str = "Alice"
age: int = 30
height: float = 165.5
is_active: bool = True

# bytes와 None
data: bytes = b"hello"
nothing: None = None

print(f"이름: {name} ({type(name).__name__})")
print(f"나이: {age} ({type(age).__name__})")
print(f"키: {height} ({type(height).__name__})")
print(f"활성: {is_active} ({type(is_active).__name__})")
```

### Step 2: list, set, frozenset

```python
# list — 순서 있는 가변 컬렉션
scores: list[int] = [85, 92, 78, 95]
names: list[str] = ["Alice", "Bob", "Charlie"]

# set — 순서 없는 고유 원소 컬렉션
tags: set[str] = {"python", "typing", "hints"}

# frozenset — 불변 set
permissions: frozenset[str] = frozenset({"read", "write"})

print(f"점수 평균: {sum(scores) / len(scores):.1f}")
print(f"태그: {tags}")
print(f"권한: {permissions}")


# 빈 컬렉션에도 타입 명시
empty_list: list[int] = []
empty_set: set[str] = set()
```

### Step 3: dict

```python
# dict — 키-값 쌍
user_ages: dict[str, int] = {
    "Alice": 30,
    "Bob": 25,
    "Charlie": 35,
}

# 중첩 dict
config: dict[str, dict[str, int]] = {
    "database": {"port": 5432, "pool_size": 10},
    "cache": {"port": 6379, "ttl": 300},
}

for name, age in user_ages.items():
    print(f"  {name}: {age}세")

# dict의 키는 hashable 타입만 가능
# dict[list, str]은 불가 (list는 unhashable)
```

### Step 4: tuple

```python
# 고정 길이 튜플 — 각 위치의 타입을 명시
point: tuple[float, float] = (3.5, 7.2)
rgb: tuple[int, int, int] = (255, 128, 0)
record: tuple[str, int, bool] = ("Alice", 30, True)

print(f"좌표: {point}")
print(f"RGB: {rgb}")
print(f"레코드: {record}")


# 가변 길이 튜플 — Ellipsis 사용
values: tuple[int, ...] = (1, 2, 3, 4, 5)
empty_tuple: tuple[()] = ()

print(f"값: {values}")
print(f"빈 튜플: {empty_tuple}")

# 고정 길이 vs 가변 길이
# tuple[int, str]     → 정확히 2개 (int, str)
# tuple[int, ...]     → 0개 이상의 int
```

### Step 5: 중첩 컬렉션과 타입 별칭

```python
# 중첩 컬렉션
matrix: list[list[int]] = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

user_scores: dict[str, list[int]] = {
    "Alice": [85, 92, 78],
    "Bob": [90, 88, 95],
}

# 타입 별칭으로 가독성 향상
type Row = list[int]
type Matrix = list[Row]
type UserScores = dict[str, list[int]]

grades: Matrix = [[1, 2], [3, 4]]
scores: UserScores = {"Alice": [85, 92]}

for name, s in user_scores.items():
    avg = sum(s) / len(s)
    print(f"  {name}: 평균 {avg:.1f}")
```

## 이 코드에서 주목할 점

- Python 3.9+에서 `list[int]`, `dict[str, int]`를 직접 사용합니다
- 컬렉션의 원소 타입까지 명시해야 정적 분석의 효과가 있습니다
- `tuple[int, str]`은 고정 길이, `tuple[int, ...]`은 가변 길이입니다
- 타입 별칭(`type`)으로 복잡한 타입을 읽기 쉽게 만듭니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `list` 대신 `List` 임포트 (3.9+) | 불필요한 임포트입니다 | 내장 `list[T]`를 사용합니다 |
| 원소 타입 생략 (`list` only) | 어떤 원소인지 알 수 없습니다 | `list[int]`처럼 원소 타입을 명시합니다 |
| `tuple[int]`로 가변 길이 의도 | 정확히 1개 원소 튜플입니다 | `tuple[int, ...]`을 사용합니다 |
| `dict[str, any]` 사용 | `any`는 변수명입니다 | `dict[str, Any]`로 typing에서 임포트합니다 |
| 빈 컬렉션에 타입 생략 | 추론이 불가능합니다 | `empty: list[int] = []`로 명시합니다 |

## 실무에서 이렇게 쓰입니다

- API 응답을 `dict[str, Any]`로 타입 지정합니다
- 데이터베이스 쿼리 결과를 `list[dict[str, Any]]`로 표현합니다
- 설정 파일 구조를 `dict[str, dict[str, int]]`로 정의합니다
- 좌표, RGB 등 고정 구조를 `tuple`로 표현합니다
- 타입 별칭으로 도메인 용어를 코드에 반영합니다

## 현업 개발자는 이렇게 생각합니다

컬렉션 타입 힌트의 핵심은 "원소 타입까지 명시"하는 것입니다. `list`만 쓰면 타입 힌트의 절반만 활용하는 셈입니다. Python 3.9+ 프로젝트에서는 `typing` 모듈의 `List`, `Dict`를 사용할 이유가 없습니다.

복잡한 중첩 타입은 타입 별칭을 적극 활용합니다. `dict[str, list[tuple[int, str]]]`보다 `type UserRecord = tuple[int, str]`으로 분리하면 코드와 타입 힌트 모두 읽기 쉬워집니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **내장 제네릭** — list[int] 같은 내장 제네릭을 우선 씁니다.
- **Sequence vs list** — 함수 입력은 더 추상적인 타입을 받습니다.
- **불변 vs 가변** — Mapping/Dict 차이를 의식해 시그니처를 정합니다.
- **Iterable** — 한 번만 순회하는 함수는 Iterable로 받습니다.
- **타입 별칭** — 복잡 타입은 alias로 의도를 드러냅니다.

## 체크리스트

- [ ] 기본 스칼라 타입 힌트를 작성할 수 있다
- [ ] `list[T]`, `dict[K, V]`, `set[T]`를 작성할 수 있다
- [ ] 고정 길이 튜플과 가변 길이 튜플의 차이를 설명할 수 있다
- [ ] 중첩 컬렉션 타입을 작성할 수 있다
- [ ] 타입 별칭을 사용하여 복잡한 타입을 단순화할 수 있다

## 연습 문제

1. 학생 이름(str)을 키, 점수 리스트(list[int])를 값으로 가지는 딕셔너리 타입을 선언하고 평균을 계산하는 함수를 작성하세요.
2. RGB 색상 `tuple[int, int, int]`을 받아 16진수 문자열을 반환하는 함수를 타입 힌트로 작성하세요.
3. 3x3 행렬(`list[list[int]]`)을 전치하는 함수를 타입 힌트로 작성하세요.

## 정리 및 다음 글 안내

기본 타입과 컬렉션 타입의 힌트 작성법을 살펴보았습니다. 컬렉션은 원소 타입까지 명시해야 정적 분석의 효과를 온전히 얻을 수 있습니다. 다음 글에서는 값이 없을 수 있는 경우를 표현하는 **Optional과 Union**을 다룹니다.

<!-- toc:begin -->
- [Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- **기본 타입과 collection 타입 (현재 글)**
- [Optional과 Union](./03-optional-and-union.md)
- [함수 타입 힌트](./04-function-type-hints.md)
- [TypedDict와 dataclass](./05-typeddict-and-dataclass.md)
- [Protocol과 structural typing](./06-protocol-and-structural-typing.md)
- [Generic 이해하기](./07-generic.md)
- [mypy와 pyright 사용하기](./08-mypy-and-pyright.md)
- [Pydantic과 타입 힌트](./09-pydantic-and-type-hints.md)
- [타입 힌트를 잘 쓰는 기준](./10-type-hints-best-practices.md)
<!-- toc:end -->

## 참고 자료

- [PEP 585 — Type Hinting Generics In Standard Collections](https://peps.python.org/pep-0585/)
- [Python 공식 문서 — typing 모듈](https://docs.python.org/3/library/typing.html)
- [PEP 613 — Explicit Type Aliases](https://peps.python.org/pep-0613/)
- [mypy 공식 문서 — Built-in types](https://mypy.readthedocs.io/en/stable/builtin_types.html)
