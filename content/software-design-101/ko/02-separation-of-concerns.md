---
series: software-design-101
episode: 2
title: "Software Design 101 (2/10): 관심사 분리"
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
  - SeparationOfConcerns
  - Modularity
  - Cohesion
  - Coupling
seo_description: 관심사 분리의 정의, 결합도와 응집도, 책임을 나누는 실전 절차를 정리합니다.
last_reviewed: '2026-05-15'
---

# Software Design 101 (2/10): 관심사 분리

주문 처리 함수 하나를 열었는데 입력 검증, 가격 계산, 데이터베이스 저장, 이메일 발송, 응답 직렬화가 한곳에 몰려 있다면 코드는 대개 한 번에 바꾸기 어렵습니다. 기능 하나를 고치려 해도 다른 책임을 모두 함께 이해해야 하기 때문입니다.

이 글은 Software Design 101 시리즈의 2번째 글입니다.

여기서는 관심사 분리를 “파일을 많이 쪼개는 일”이 아니라, 다른 이유로 바뀌는 책임을 다른 경계로 나누는 설계 원칙으로 설명합니다. 결합도와 응집도가 왜 함께 나오는지, 횡단 관심사는 어디에 두어야 하는지, 분리와 통합 사이의 균형은 어떻게 잡아야 하는지도 차례로 보겠습니다.

## 먼저 던지는 질문

- 관심사란 정확히 무엇일까요?
- 한 모듈이 너무 많은 일을 하는지 어떻게 알아낼 수 있을까요?
- 결합도와 응집도는 관심사 분리와 어떤 관계가 있을까요?

## 큰 그림

![Software Design 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/02/02-01-concept-at-a-glance.ko.png)

*Software Design 101 2장 흐름 개요*

이 그림에서는 관심사 분리를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 관심사 분리의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

관심사가 섞인 코드는 수정 한 번에도 시스템 전체 문맥을 요구합니다. 반대로 책임이 잘 나뉜 코드는 필요한 부분만 열어도 다음 변경을 처리할 수 있습니다. 분리는 코드량을 늘리는 일이 아니라, 바뀌는 이유를 정리해 선택지를 늘리는 일입니다.

현업에서 문제가 되는 지점도 여기입니다. 같은 주문 기능인데 가격 정책 변경과 알림 채널 변경이 같은 함수에서 만난다면, 사소한 수정도 위험해집니다. 한쪽을 건드릴 때 다른 쪽이 흔들릴 가능성이 계속 남기 때문입니다.

## 전체 그림

UI, 도메인, 인프라는 바뀌는 속도도 이유도 다릅니다. 이 셋을 같은 상자에 넣으면 작은 변경도 넓게 번집니다. 분리를 잘하면 세 관심사가 서로 다른 속도로 움직일 수 있습니다.

## 기본 용어

- <strong>관심사</strong>: 시스템이 신경 써야 하는 하나의 주제입니다.
- <strong>결합도</strong>: 모듈끼리 얼마나 강하게 얽혀 있는지를 뜻합니다. 낮을수록 좋습니다.
- <strong>응집도</strong>: 한 모듈 안의 코드가 얼마나 같은 목적을 향하는지를 뜻합니다. 높을수록 좋습니다.
- <strong>횡단 관심사</strong>: 로깅, 보안처럼 여러 모듈을 가로지르는 관심사입니다.
- <strong>경계</strong>: 관심사와 관심사가 만나는 이음새입니다.

## 변경 전과 변경 후

**변경 전**

```python
def process_order(req):
    # 입력 파싱 + 검증 + 가격 계산 + DB 저장 + 이메일 + 응답
    ...
```

**변경 후**

```python
def process_order(req):
    cmd = parse(req)               # 입력
    order = build_order(cmd)       # 도메인
    saved = save_order(order)      # 인프라
    notify(saved)                  # 통신
    return to_response(saved)      # 출력
```

아래 구조에서는 각 줄이 하나의 관심사를 맡습니다. 함수 전체를 읽는 사람도 흐름을 한 번에 파악할 수 있고, 저장 방식을 바꾸더라도 도메인 로직을 크게 흔들지 않아도 됩니다.

## 관심사를 나누는 다섯 단계

### 1단계 — 변경 이유를 적어 본다

```python
# 1_reasons.py
# Why does the Order module change?
# - 가격 정책 변경
# - DB 스키마 변경
# - 알림 채널 변경
# 세 가지 이유 → 세 가지 책임입니다.
```

모듈이 왜 바뀌는지 적어 보면 책임 후보가 바로 드러납니다. 가격 정책, 저장소, 알림 채널이 모두 독립적으로 바뀐다면 같은 함수에 묶어 둘 이유가 약합니다.

### 2단계 — 도메인과 인프라를 가른다

```python
# 2_domain_infra.py
# Domain knows nothing about IO.
def calculate_total(items, member): ...
# Infra uses the domain.
def save(order): db.execute(...)
```

도메인은 업무 규칙을 알고, 인프라는 데이터베이스나 외부 시스템을 다룹니다. 둘을 섞어 두면 정책 변경과 저장 방식 변경이 같은 코드에 충돌합니다.

### 3단계 — 입력, 처리, 출력을 나눈다

```python
# 3_io.py
def parse(req): ...    # 입력
def handle(cmd): ...   # 처리
def render(res): ...   # 출력
```

입력 해석, 업무 처리, 출력 변환을 분리하면 함수가 한 줄처럼 읽힙니다. 웹 프레임워크가 바뀌어도 핵심 처리 코드는 상대적으로 덜 흔들립니다.

### 4단계 — 횡단 관심사를 밖으로 뺀다

```python
# 4_cross.py
def with_logging(fn):
    def w(*a, **k):
        # 로깅
        return fn(*a, **k)
    return w
```

로깅, 인증, 추적 같은 횡단 관심사는 데코레이터나 미들웨어로 모으는 편이 낫습니다. 도메인 코드 안에 흩어 두면 핵심 규칙을 읽기가 빠르게 어려워집니다.

### 5단계 — 이음새를 점검한다

```python
# 5_seam.py
# Inspect where the separated concerns meet (the seams).
def app(req):
    return render(handle(parse(req)))
```

분리가 끝이 아닙니다. 분리된 관심사가 만나는 지점이 적고 명확해야 합니다. 이음새가 많아지면 통합 비용이 커지고, 구조가 다시 흐려집니다.

## 빠르게 검증해 보기

주문 처리 함수 하나를 골라 아래처럼 책임을 색칠해 보면 관심사가 실제로 얼마나 섞였는지 금방 드러납니다.

```text
parse_request()      -> 입력
validate_order()     -> 도메인 규칙
save_order()         -> 저장소
send_notification()  -> 외부 통신
to_response()        -> 출력
```

**Expected output:** 같은 함수 안에 입력·도메인·인프라·출력이 모두 들어 있으면 분리 후보가 뚜렷하게 보입니다.

가능하면 색칠한 결과를 기준으로 “이 단계는 왜 바뀌는가?”를 한 줄씩 적어 보세요. 변경 이유가 다르면 경계 후보도 다릅니다.

## 실패 신호와 먼저 볼 것

| 실패 신호 | 먼저 볼 것 |
| --- | --- |
| 검증 규칙 변경이 API 응답 코드까지 흔든다 | 입력과 도메인 처리가 섞여 있는지 확인합니다 |
| 로깅 정책 변경이 핵심 규칙을 건드린다 | 횡단 관심사가 도메인 안에 퍼져 있는지 봅니다 |
| 함수 수는 많은데 수정 범위는 여전히 넓다 | 이름만 나눈 계층인지, 실제 책임이 분리됐는지 점검합니다 |

관심사 분리는 파일 수를 늘리는 일이 아니라, 다른 이유로 바뀌는 코드를 다른 경계에 두는 일입니다.

## 이 코드에서 먼저 볼 점

- 모듈마다 변경 이유를 하나로 모으려는 방향이 보입니다.
- 도메인이 입출력 세부를 모르면 테스트와 재사용이 쉬워집니다.
- 횡단 관심사를 도메인 밖으로 밀어내야 핵심 규칙이 선명해집니다.

## 어디서 많이 헷갈릴까

관심사 분리를 “폴더만 나누는 일”로 이해하면 효과가 거의 없습니다. presentation, service, repository 같은 이름을 붙여도 실제 함수 안에서 여전히 모든 책임을 다루고 있다면 구조만 복잡해졌을 뿐입니다.

반대로 너무 잘게 자르는 것도 문제입니다. 함수 하나마다 파일 하나를 만들고, 모듈 하나마다 인터페이스 하나를 둔다고 해서 자동으로 좋은 설계가 되지는 않습니다. 분리는 통합 비용과 함께 봐야 합니다. 같은 변경을 처리하려고 모듈 여덟 개를 왕복해야 한다면 그 또한 나쁜 신호입니다.

## 실무에서는 이렇게 본다

강한 팀은 관심사 분리를 규칙으로만 두지 않고 코드 수준에서 강제합니다. 예를 들어 도메인 패키지 안에서 외부 라이브러리 import를 막는 린트를 두면, 분리가 문서가 아니라 실행되는 제약이 됩니다.

코드 리뷰에서도 질문은 비슷합니다. “이 함수는 왜 바뀌는가?”, “이 로깅이 정말 도메인 안으로 들어가야 하는가?”, “입력 파싱을 분리하면 테스트가 쉬워지지 않는가?” 이런 질문이 반복되면 설계 감각도 함께 올라갑니다.

## 체크리스트

- [ ] 각 모듈에 변경 이유가 하나만 남아 있는가?
- [ ] 도메인이 IO 라이브러리를 직접 알지 않는가?
- [ ] 로깅과 보안 같은 횡단 관심사가 한곳에 모여 있는가?
- [ ] 분리된 관심사가 만나는 이음새가 명확한가?
- [ ] 분리로 얻는 이익이 통합 비용보다 큰가?

## 연습 문제

1. 현재 코드에서 한 모듈의 변경 이유를 세 가지 적어 보세요.
2. 함수 하나를 입력, 처리, 출력 단계로 분리해 보세요.
3. 도메인 코드에 있는 외부 import를 찾아 어댑터 쪽으로 옮겨 보세요.

## 정리

관심사 분리는 모든 설계의 출발점입니다. 무엇이 왜 바뀌는지 구분하면 결합도는 낮아지고 응집도는 높아집니다. 그 위에서 모듈과 경계도 훨씬 또렷해집니다.

다음 글에서는 이 분리를 담는 단위, 모듈과 경계를 다룹니다.

## 처음 질문으로 돌아가기

- **관심사란 정확히 무엇일까요?**
  - 본문의 기준은 관심사 분리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **한 모듈이 너무 많은 일을 하는지 어떻게 알아낼 수 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **결합도와 응집도는 관심사 분리와 어떤 관계가 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Software Design 101 (1/10): 소프트웨어 설계란 무엇인가?](./01-what-is-software-design.md)
- **관심사 분리 (현재 글)**
- 모듈과 경계 (예정)
- 의존성 방향 (예정)
- 인터페이스와 추상화 (예정)
- 계층 아키텍처 (예정)
- 데이터 흐름 설계 (예정)
- 변경 영향 줄이기 (예정)
- 설계 원칙 모음 (예정)
- 작은 프로젝트로 설계 연습 (예정)

<!-- toc:end -->

## 참고 자료

- [Separation of Concerns (Dijkstra)](https://www.cs.utexas.edu/users/EWD/transcriptions/EWD04xx/EWD447.html)
- [A Philosophy of Software Design](https://web.stanford.edu/~ouster/cgi-bin/aposd.php)
- [Hexagonal Architecture (Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

### 실전 확인용 문서

- [functools — Higher-order functions and operations on callable objects](https://docs.python.org/3/library/functools.html)
- [Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)

Tags: Computer Science, SoftwareDesign, SeparationOfConcerns, Modularity, Cohesion, Coupling
