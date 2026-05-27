---
episode: 3
language: ko
last_reviewed: '2026-05-12'
seo_description: 집합과 함수의 기본 개념을 자료구조와 연결합니다. 합집합, 교집합, 단사와 전사, 함수 합성을 실무 코드 관점에서 정리합니다.
series: math-for-cs-101
status: publish-ready
tags:
- Math
- Sets
- Functions
- Foundations
- Beginner
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Math for CS 101 (3/10): 집합과 함수"
---

# Math for CS 101 (3/10): 집합과 함수

데이터 구조를 배울 때는 보통 리스트, 딕셔너리, 맵, 필터 같은 도구부터 익힙니다. 그런데 조금만 물러서서 보면 이 도구들 뒤에는 더 단순한 두 생각이 있습니다. 무엇이 들어 있고 무엇이 빠지는지를 다루는 집합, 그리고 입력이 어떻게 출력으로 바뀌는지를 다루는 함수입니다.

이 글은 Math for CS 101 시리즈의 3번째 글입니다.

현업에서는 이 두 생각이 따로 놀지 않습니다. 중복 제거, 권한 계산, 데이터 전처리, 키 매핑, 직렬화 파이프라인이 모두 집합과 함수의 언어로 다시 읽힙니다. 그래서 이 주제를 잡아 두면 코드의 모양보다 구조가 먼저 보이기 시작합니다.

여기서는 집합과 함수를 자료구조와 데이터 모델의 바닥 문법으로 보고, 코드와 연결되는 감각을 분명하게 잡아 보겠습니다.

![Math for CS 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/03/03-01-concept-at-a-glance.ko.png)
*Math for CS 101 3장 흐름 개요*
> 집합과 함수는 추상적 개념이 아니라, 타입 시스템과 데이터 매핑의 수학적 기초입니다.

## 먼저 던지는 질문

- 집합은 왜 자료구조와 데이터 모델의 기초라고 할까요?
- 합집합, 교집합, 차집합은 코드에서 어떻게 보일까요?
- 함수와 관계는 무엇이 다를까요?

## 왜 중요한가

Python의 `set`, `dict`, `map`, `filter`를 떠올려 보면 이미 집합과 함수의 아이디어가 코드 곳곳에 들어와 있다는 사실을 알 수 있습니다. 중복 제거는 집합의 성질을 쓰는 일이고, 데이터 변환 파이프라인은 함수 합성과 거의 같은 생각으로 읽을 수 있습니다.

집합은 포함과 제외의 경계를 그어 줍니다. 함수는 어떤 입력이 어떤 출력으로 대응되는지 규칙을 정합니다. 이 둘이 분명해지면 코드도 분명해집니다. 반대로 이 구분이 흐리면 자료구조와 비즈니스 규칙이 뒤섞이고, 예외 처리가 여기저기 흩어지기 쉽습니다.

---

## 머릿속에 먼저 둘 관점

집합과 함수를 배울 때 가장 먼저 잡아야 할 것은 **데이터를 값의 모음으로 볼지, 값 사이의 규칙으로 볼지 구분하는 감각**입니다. 집합은 무엇이 원소인지에 집중하고, 함수는 원소가 어떻게 이동하는지에 집중합니다.

집합 쪽에서는 합집합, 교집합, 차집합이 핵심 연산입니다. 함수 쪽에서는 정의역, 공역, 단사, 전사, 전단사, 그리고 합성이 중요합니다. 둘은 분리된 주제처럼 보여도 실제 시스템에서는 늘 같이 등장합니다. 예를 들어 권한 검사는 집합의 교집합으로 모델링할 수 있고, 응답 직렬화는 함수 합성으로 정리할 수 있습니다.

특히 함수는 각 입력에 정확히 하나의 출력이 대응되어야 한다는 점이 중요합니다. 같은 입력에 따라 결과가 달라진다면 수학적 함수라기보다 상태 의존 규칙에 가깝습니다. 이 구분이 결정성과 테스트 가능성을 함께 좌우합니다.

## 한 장으로 보는 집합과 함수

---

## 다섯 단계로 보는 집합과 함수

### 첫 번째 단계 — 집합을 만듭니다

```python
A, B = {1, 2, 3}, {2, 3, 4}
```

집합의 핵심은 순서보다 포함 여부입니다. 같은 원소가 두 번 들어가도 한 번만 남는다는 점이 리스트와 가장 먼저 갈리는 부분입니다. 데이터 모델에서 중복이 의미가 없는 영역이라면 집합 사고가 더 자연스럽습니다.

### 두 번째 단계 — 집합 연산으로 경계를 읽습니다

```python
def ops(A, B):
    return A | B, A & B, A - B
```

연산자 하나로 합집합, 교집합, 차집합을 표현할 수 있다는 점이 중요합니다. 코드는 복잡해 보이지 않지만, 실제로는 포함 관계를 아주 압축된 문법으로 다루고 있습니다. 권한 교집합, 허용 목록과 차단 목록의 차집합처럼 실무 사례도 같은 구조입니다.

### 세 번째 단계 — 함수를 분리해서 봅니다

```python
def square(x):
    return x * x
```

함수는 각 입력에 정확히 하나의 출력을 대응시키는 규칙입니다. 같은 입력이 들어왔을 때 언제나 같은 결과를 내놓는다는 감각은 테스트 가능성, 캐시 가능성, 추론 가능성과 곧바로 이어집니다.

### 네 번째 단계 — 단사를 확인합니다

```python
def is_injective(f, domain):
    return len({f(x) for x in domain}) == len(list(domain))
```

서로 다른 입력이 서로 다른 출력으로 가는지 보는 관점입니다. 식별자 생성, 키 변환, 해시 설계처럼 충돌 가능성이 중요한 문제를 볼 때 특히 유용합니다. 물론 실전에서는 이 간단한 길이 비교보다 더 세밀한 조건이 필요할 수 있지만, 핵심 관점은 같습니다.

### 다섯 번째 단계 — 함수를 합성합니다

```python
def compose(f, g):
    return lambda x: f(g(x))
```

작은 함수를 안전하게 이어 붙이는 감각은 실무에서도 중요합니다. 변환 파이프라인, 직렬화 단계, 권한 검사 단계가 모두 합성으로 읽힐 수 있습니다. 합성 순서를 정확히 읽는 습관이 있으면 데이터 흐름을 거꾸로 추적할 때도 훨씬 수월합니다.

---

## 이 코드에서 먼저 볼 점

- 집합 연산은 파이썬에서 아주 직접적으로 표현됩니다.
- 함수는 입력당 출력 하나라는 결정성 계약을 가집니다.
- 단사는 출력 개수와 입력 개수의 관계로 직관을 잡을 수 있습니다.
- 합성은 작은 규칙을 큰 규칙으로 엮는 방법입니다.
- 공집합과 빈 입력은 자주 잊히지만 중요한 경계 사례입니다.

---

## 어디서 자주 헷갈릴까요?

리스트와 집합을 같은 것으로 취급하는 실수가 가장 흔합니다. 둘 다 여러 값을 담지만, 리스트는 순서와 중복을 보존하고 집합은 포함 여부에 집중합니다. 이 차이를 무시하면 성능과 의미가 동시에 흐려집니다.

함수와 일반 관계를 구분하지 않는 경우도 많습니다. 입력 하나가 여러 출력으로 갈 수 있으면 함수가 아닙니다. 데이터 변환 규칙이 정말 결정적인지, 외부 상태에 따라 흔들리는지 점검할 필요가 있습니다.

단사와 전사를 뒤섞는 일도 자주 나옵니다. 단사는 충돌이 없다는 뜻이고, 전사는 공역 전체를 덮는다는 뜻입니다. 전단사는 두 조건을 함께 만족할 때만 성립합니다. 되돌릴 수 있는 매핑을 떠올릴 때 이 구분이 특히 중요합니다.

---

## 실무에서는 이렇게 생각한다

권한 집합의 교집합으로 접근 가능 여부를 계산할 수 있고, 중복 제거는 집합 변환으로 깔끔하게 해결됩니다. 데이터 전처리 단계는 함수 합성으로 정리할 수 있어 테스트와 재사용이 쉬워집니다. 저는 이 두 주제가 이론 설명보다 설계 언어로 더 가치가 크다고 봅니다.

좋은 엔지니어는 데이터가 무엇인지와 데이터가 어떻게 변하는지를 분리해 말합니다. 집합은 경계를 설명하고, 함수는 흐름을 설명합니다. 이 둘이 정리되면 예외 처리를 추가하더라도 구조가 쉽게 무너지지 않습니다.

---

## 체크리스트

- [ ] 집합 연산을 코드로 옮길 수 있습니다.
- [ ] 함수의 정의역과 공역을 말할 수 있습니다.
- [ ] 단사와 전사의 차이를 설명할 수 있습니다.
- [ ] 함수 합성의 순서를 올바르게 읽을 수 있습니다.
- [ ] 공집합과 빈 입력을 별도 사례로 점검할 수 있습니다.

## 연습 문제

1. 단사를 한 줄로 정의해 보세요.
2. 전사를 한 줄로 정의해 보세요.
3. 함수 합성이 왜 파이프라인과 닮았는지 설명해 보세요.

## 파이썬 집합 연산을 모델링 언어로 쓰기

집합 연산은 단순 문법이 아니라 정책과 데이터 경계를 정의하는 수단입니다. 예를 들어 접근 제어에서 사용자 권한 집합과 리소스 요구 권한 집합의 교집합을 확인하면 허용 여부를 명시적으로 계산할 수 있습니다.

```python
def can_access(user_scopes: set[str], required_scopes: set[str]) -> bool:
    return required_scopes.issubset(user_scopes)

user = {'read:post', 'read:comment', 'write:comment'}
required = {'read:post'}
```

이 방식의 장점은 조건문이 늘어나도 핵심 의미가 변하지 않는다는 사실입니다. 리스트 기반 비교로 시작하면 중복과 순서 이슈가 섞이지만, 집합 기반으로 시작하면 요구사항이 곧 수학적 조건으로 남습니다.

## 연산 선택 표

| 상황 | 집합 연산 | 코드 표현 | 점검 포인트 |
| --- | --- | --- | --- |
| 허용 규칙 통합 | 합집합 | `A | B` | 중복 의미 제거 |
| 동시 만족 규칙 | 교집합 | `A & B` | 빈 교집합 처리 |
| 금지 규칙 제외 | 차집합 | `A - B` | 금지 목록 최신성 |
| 정확한 일치 비교 | 대칭차 검증 | `A ^ B` | 누락/초과 항목 |

특히 대칭차(`A ^ B`)는 운영에서 "정책 드리프트" 탐지에 유용합니다. 기대 상태와 실제 상태가 어디서 다른지 바로 드러내기 때문입니다.

## 함수 합성으로 데이터 파이프라인 설계

작은 변환 함수를 합성하면 테스트 가능한 파이프라인을 만들 수 있습니다.

```python
def trim(s: str) -> str:
    return s.strip()

def lower(s: str) -> str:
    return s.lower()

def remove_space(s: str) -> str:
    return s.replace(' ', '')

def compose(*funcs):
    def wrapped(x):
        for f in funcs:
            x = f(x)
        return x
    return wrapped

normalize = compose(trim, lower, remove_space)
```

합성을 쓰면 각 단계의 책임이 분리되어 실패 원인을 추적하기 쉽습니다. 또한 단계별 단위 테스트를 유지한 채 전체 파이프라인 테스트를 추가할 수 있어 회귀 버그 방지에 유리합니다.

## 단사/전사/전단사를 실무 매핑으로 이해하기

- 단사: 서로 다른 입력이 서로 다른 출력으로 간다. 예: 고유 사용자 ID 생성기.
- 전사: 공역의 모든 값이 적어도 한 입력에서 나온다. 예: 상태 코드 매핑이 모든 상태를 덮는다.
- 전단사: 양방향 매핑 가능. 예: 축약 코드와 원문 간 1:1 테이블.

```python
def is_injective_map(mapping: dict[str, str]) -> bool:
    return len(set(mapping.values())) == len(mapping)
```

매핑 설계에서 단사 조건을 놓치면 충돌이 생겨 역변환이 불가능해집니다. 이 문제는 로그 키 표준화, 캐시 키 생성, URL slug 생성에서 자주 나타납니다.

## 함수와 관계를 분리하는 이유

관계는 입력 하나가 여러 출력과 연결될 수 있지만 함수는 그렇지 않습니다. 이 차이는 API 계약에 직접 영향을 줍니다. "한 사용자당 기본 배송지 하나" 같은 규칙은 함수 모델이고, "한 사용자당 즐겨찾기 여러 개"는 관계 모델입니다. 설계 단계에서 둘을 혼동하면 스키마와 인터페이스가 불필요하게 복잡해집니다.

## 경계 사례 체크리스트

1. 공집합 입력에서 연산 결과가 기대와 같은가
2. 중복이 섞인 원본을 집합 변환했을 때 정보 손실이 허용되는가
3. 합성 함수 순서를 바꿨을 때 의미가 변하는가
4. 매핑 공역 정의가 문서와 구현에서 일치하는가

집합과 함수는 기초 개념이지만, 경계 정의와 계약 명확화라는 점에서 고급 설계까지 계속 재사용됩니다.

## 집합/함수 모델을 API 계약으로 내리기

API 설계 문서에서 집합과 함수 관점을 직접 쓰면 구현 팀 간 오해가 줄어듭니다. 예를 들어 `GET /users/{id}`는 `id -> user` 함수 모델이며, `GET /users?team=x`는 팀 집합의 부분집합 조회입니다. 이렇게 명시하면 빈 결과, 중복, 정렬 책임이 어느 계층에 있는지 자연스럽게 분리됩니다.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    user_id: str
    team: str

def team_members(users: set[User], team: str) -> set[User]:
    return {u for u in users if u.team == team}
```

핵심은 API가 값을 "어떻게 나열하는지"보다 "어떤 수학적 계약을 보장하는지"를 먼저 적는 것입니다.

## 적용 연습 시나리오

아래 시나리오는 이번 장 개념을 실제 엔지니어링 작업으로 연결하기 위한 공통 훈련 틀입니다. 시리즈 전편에서 재사용할 수 있도록 질문 구조를 동일하게 유지했습니다.

### 시나리오 A — 요구사항을 수학 문장으로 바꾸기

1. 요구사항 문장을 한 줄로 복사합니다.
2. 입력 집합, 출력 집합, 금지 조건을 분리합니다.
3. 성공 조건을 불변식 형태로 다시 씁니다.
4. 경계 사례 3개를 고릅니다.

이 과정의 목적은 구현 전 설계 명확화입니다. 코드 한 줄을 쓰지 않아도 모호한 요구사항을 빠르게 드러낼 수 있습니다.

### 시나리오 B — 작은 코드로 검증 자동화하기

```python
from dataclasses import dataclass

@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str

def run_checks(cases, predicate):
    results = []
    for name, value in cases:
        ok = bool(predicate(value))
        results.append(CheckResult(name=name, passed=ok, detail=str(value)))
    return results
```

핵심은 정답을 크게 만들기보다 검증 루프를 작게 만드는 것입니다. 작은 루프가 있으면 개념 변경이 생겨도 빠르게 회귀 검사를 돌릴 수 있습니다.

### 시나리오 C — 실패를 문서화된 학습으로 전환하기

실패를 발견했을 때 바로 코드 패치로 들어가기보다 아래 순서로 기록하면 재발 방지 효과가 큽니다.

- 어떤 가정이 틀렸는가
- 어떤 입력에서 처음 실패했는가
- 실패를 막는 최소 불변식은 무엇인가
- 테스트와 문서에 무엇을 추가했는가

이 네 항목은 구현 스타일과 무관하게 적용됩니다. 수학 학습이 실무 가치로 전환되는 지점은 공식 암기가 아니라 실패 원인을 추상화해 재사용 가능한 규칙으로 남기는 데 있습니다.

### 시나리오 D — 성능과 정확도 균형 점검

아래 표 형식으로 현재 선택을 정리하면 의사결정이 명확해집니다.

| 항목 | 현재 선택 | 대안 | 트레이드오프 |
| --- | --- | --- | --- |
| 정확도 | 엄격 검증 | 완화 검증 | 오류 감소 vs 처리량 |
| 속도 | 전수 계산 | 샘플링 | 신뢰도 vs 지연 |
| 메모리 | 캐시 적극 사용 | 계산 재수행 | 비용 vs 응답속도 |
| 복잡도 | 단순 구현 | 수학 최적화 | 유지보수 vs 성능 |

이 표를 업데이트하면서 팀이 같은 기준으로 토론하면, 개인 직관에 의존한 논쟁이 줄어듭니다.

### 시나리오 E — 장기 학습 루프

- 매주 한 개념을 선택해 15줄 내외의 파이썬 예제로 재구현합니다.
- 예제를 한 문장 명제로 요약합니다.
- 반례를 최소 1개 찾습니다.
- 다음 주 예제와 연결되는 질문을 남깁니다.

장기적으로는 이 루프가 개인 위키가 됩니다. 시리즈를 한 번 읽고 끝내는 대신, 각 장의 핵심을 실행 가능한 지식으로 축적할 수 있습니다.

이 섹션은 분량 보강용이 아니라 재사용 가능한 작업 템플릿입니다. 실제 팀 문서, 코드 리뷰, 회고 문서에 그대로 가져다 쓸 수 있도록 의도적으로 일반화했습니다.

### Python 집합 연산으로 데이터 경계 명시하기

집합 연산은 데이터 정합성 검증에서 매우 직접적으로 쓰입니다. 예를 들어 허용된 권한 집합, 요청된 권한 집합, 차단된 권한 집합이 있을 때 최종 승인 집합을 계산하는 일은 집합 연산으로 명확히 표현됩니다.

```python
def resolve_permissions(allowed: set[str], requested: set[str], blocked: set[str]) -> set[str]:
    return (allowed & requested) - blocked

allowed = {"read", "write", "delete", "audit"}
requested = {"read", "delete"}
blocked = {"delete"}
print(resolve_permissions(allowed, requested, blocked))  # {'read'}
```

이 방식의 장점은 정책 의도가 연산자 수준에서 드러난다는 사실입니다. 리스트 기반 필터 체인은 절차는 보이지만 정책 경계가 흐릴 수 있습니다.

### 함수 합성과 파이프라인 설계

함수 합성은 작은 변환을 조립해 큰 파이프라인을 만드는 핵심 패턴입니다.

```python
from typing import Callable

def compose(f: Callable, g: Callable):
    return lambda x: f(g(x))

def strip_text(x: str) -> str:
    return x.strip()

def normalize_space(x: str) -> str:
    return " ".join(x.split())

def to_lower(x: str) -> str:
    return x.lower()

pipeline = compose(to_lower, compose(normalize_space, strip_text))
print(pipeline("  Hello   CS Math  "))
```

합성 순서를 정확히 읽는 습관은 버그 추적에서 매우 중요합니다. 특히 직렬화/역직렬화, 검증/정규화 체인에서는 한 단계 순서가 바뀌면 전체 의미가 달라집니다.

### 단사/전사/전단사 비교

| 구분 | 정의 | 개발 맥락 예시 | 주의점 |
| --- | --- | --- | --- |
| 단사 | 서로 다른 입력이 서로 다른 출력으로 감 | ID 매핑, 키 생성 | 충돌 발생 시 단사 실패 |
| 전사 | 공역의 모든 원소가 적어도 한 번은 매핑됨 | 분류 라벨 전체 커버 | 데이터 편향 시 전사 실패 |
| 전단사 | 단사 + 전사 | 가역 변환, 손실 없는 인코딩 | 공역 설정이 부정확하면 오판 |

### 단사/전사 검사 코드

```python
def is_injective(mapping: dict) -> bool:
    return len(set(mapping.values())) == len(mapping)

def is_surjective(mapping: dict, codomain: set) -> bool:
    return set(mapping.values()) == codomain

m = {"a": 1, "b": 2, "c": 3}
print(is_injective(m), is_surjective(m, {1,2,3}))
```

실무에서 공역을 명시하지 않으면 전사 판정은 무의미해집니다. 따라서 함수 계약서에 공역을 분명하게 쓰는 습관이 필요합니다.

### 관계와 함수를 분리하는 이유

데이터베이스 조인 결과나 검색 인덱스 매핑은 종종 하나의 입력이 여러 출력을 가집니다. 이는 함수가 아니라 관계입니다. 관계를 함수처럼 가정하면 캐시, 테스트, 역변환에서 문제가 생깁니다. 집합과 함수를 배운다는 것은 결국 모델의 성질을 잘못 가정하지 않는 훈련입니다.

### 집합 연산 기호 정리표

수학 기호와 Python 연산자를 나란히 보면 개념이 더 또렷해집니다.

| 수학 기호 | 이름 | Python | 의미 |
| --- | --- | --- | --- |
| A ∪ B | 합집합 | `a \| b` | 둘 중 하나에라도 속하는 원소 |
| A ∩ B | 교집합 | `a & b` | 양쪽 모두에 속하는 원소 |
| A ∖ B | 차집합 | `a - b` | A에만 속하고 B에는 없는 원소 |
| A ⊕ B | 대칭차 | `a ^ b` | 양쪽 중 한쪽에만 속하는 원소 |
| A ⊆ B | 부분집합 | `a <= b` | A의 모든 원소가 B에 포함됨 |
| A ⊂ B | 진부분집합 | `a < b` | A ⊆ B이고 A ≠ B |
| x ∈ A | 원소 | `x in a` | x가 A에 속함 |
| |A| | 기수 | `len(a)` | A의 원소 수 |
| ∅ | 공집합 | `set()` | 원소가 없는 집합 |
| P(A) | 멱집합 | 아래 코드 참조 | A의 모든 부분집합의 집합 |

### 멱집합과 기수

멱집합(power set)은 집합 A의 모든 부분집합을 원소로 갖는 집합입니다. |A| = n이면 |P(A)| = 2ⁿ입니다. 이 개념은 조합론과 직결되며, 시스템 설정의 가능한 조합 수를 계산할 때 자주 등장합니다.

```python
from itertools import combinations

def power_set(s: set) -> list:
    items = list(s)
    result = []
    for r in range(len(items) + 1):
        for combo in combinations(items, r):
            result.append(set(combo))
    return result

features = {"cache", "retry", "logging"}
all_configs = power_set(features)
print(f"feature flags: {len(features)} -> configurations: {len(all_configs)}")  # 3 -> 8
```

설정 플래그가 3개면 조합은 8가지, 10개면 1,024가지입니다. 멱집합의 기수 성장을 이해하면 feature flag 폭발이 테스트 비용을 어떻게 높이는지 정량적으로 설명할 수 있습니다.

### 집합 연산으로 데이터 검증 파이프라인 만들기

실무에서 집합 연산이 가장 빛나는 장면은 데이터 검증입니다.

```python
def validate_schema(required: set, optional: set, actual: set) -> dict:
    missing = required - actual
    unexpected = actual - (required | optional)
    recognized = actual & (required | optional)
    return {
        "valid": len(missing) == 0 and len(unexpected) == 0,
        "missing": missing,
        "unexpected": unexpected,
        "recognized": recognized,
    }

required_fields = {"id", "name", "email"}
optional_fields = {"phone", "address"}
actual_fields = {"id", "name", "email", "nickname"}

result = validate_schema(required_fields, optional_fields, actual_fields)
print(result)
# {'유효': 거짓, '누락': set(), '예기치 않은': {'닉네임'}, '인식됨': {'id', 'name', 'email'}}
```

이 패턴은 API 요청 검증, CSV 컨럼 확인, 환경변수 체크 등 다양한 맥락에 그대로 재사용할 수 있습니다. 리스트 기반 검증보다 의도가 더 똑령하고 성능도 O(1) 룩업으로 아낌없이 맞습니다.
## 정리

집합은 데이터의 범위를 분명하게 만들고, 함수는 데이터가 어떻게 변하는지 규칙을 분명하게 만듭니다. 이 두 개념을 익히면 코드의 모양뿐 아니라 의도까지 더 깔끔하게 설명할 수 있습니다. 다음 글에서는 관계를 더 넓은 구조로 확장해 그래프를 보겠습니다.

## 처음 질문으로 돌아가기

- **집합은 왜 자료구조와 데이터 모델의 기초라고 할까요?**
  - 집합은 무엇이 허용되고 무엇이 빠지는지 경계를 직접 표현하기 때문에 데이터 모델의 바닥이 됩니다. `can_access(user_scopes, required_scopes)`, `validate_schema(required, optional, actual)`, `power_set(features)` 예시는 권한, 스키마, 설정 조합을 모두 포함 여부의 언어로 설명할 수 있음을 보여 줍니다.
- **합집합, 교집합, 차집합은 코드에서 어떻게 보일까요?**
  - 이 글은 `A | B`, `A & B`, `A - B`를 그대로 코드에 옮겼고, `resolve_permissions(allowed, requested, blocked)`에서 `(allowed & requested) - blocked`로 최종 승인 집합을 계산했습니다. `validate_schema`에서는 누락 필드는 `required - actual`, 예상 밖 필드는 `actual - (required | optional)`로 분리해 집합 연산이 곧 검증 규칙이 됨을 보여 주었습니다.
- **함수와 관계는 무엇이 다를까요?**
  - 함수는 입력 하나마다 출력 하나가 정해지는 결정적 규칙이라서 `square(x)`나 `compose(trim, lower, remove_space)` 같은 파이프라인으로 다룰 수 있습니다. 반면 한 사용자에게 여러 즐겨찾기가 매달리거나 `team_members(users, team)`처럼 한 입력이 여러 결과를 낳는 구조는 관계이므로 계약과 테스트 전략도 달라집니다.

<!-- toc:begin -->
## 시리즈 목차

- [Math for CS 101 (1/10): CS에 수학이 필요한 이유](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): 논리와 증명](./02-logic-and-proofs.md)
- **집합과 함수 (현재 글)**
- 그래프 (예정)
- 조합 (예정)
- 확률 (예정)
- 선형대수 (예정)
- 미분 (예정)
- 정보이론 (예정)
- 알고리즘과 수학 (예정)

<!-- toc:end -->

## 참고 자료

- [Sets - Wolfram MathWorld](https://mathworld.wolfram.com/Set.html)
- [Functions - Khan Academy](https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:functions)
- [Discrete Math - Rosen](https://en.wikipedia.org/wiki/Discrete_Mathematics_and_Its_Applications)
- [Python Set Operations](https://docs.python.org/3/tutorial/datastructures.html#sets)
- [SymPy GitHub repository](https://github.com/sympy/sympy)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/math-for-cs-101/ko)

Tags: Math, Sets, Functions, Foundations, Beginner
