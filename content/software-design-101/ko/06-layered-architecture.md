---
series: software-design-101
episode: 6
title: "Software Design 101 (6/10): 계층 아키텍처"
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
  - LayeredArchitecture
  - CleanArchitecture
  - Layers
  - Architecture
seo_description: 계층 아키텍처의 구성, 허용된 의존 방향, 부패 방지 계층을 정리합니다.
last_reviewed: '2026-05-15'
---

# Software Design 101 (6/10): 계층 아키텍처

라우터에서 요청을 받고, 그 안에서 바로 검증하고, 비즈니스 규칙을 처리하고, 데이터베이스까지 두드리는 코드는 처음에는 빠르게 완성됩니다. 하지만 채널이 하나 더 늘거나 저장 방식이 바뀌는 순간 책임이 한곳에 엉켜 있었다는 사실이 바로 드러납니다.

이 글은 Software Design 101 시리즈의 6번째 글입니다.

여기서는 계층 아키텍처를 왜 쓰는지, presentation·application·domain·infrastructure를 어떤 기준으로 나누는지, 허용되는 의존성 방향은 무엇인지, 외부 모델이 도메인으로 그대로 새지 않게 막는 부패 방지 계층은 어디에 필요한지 살펴봅니다.

![Software Design 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/06/06-01-concept-at-a-glance.ko.png)
*Software Design 101 6장 흐름 개요*

> 계층 아키텍처의 핵심은 '계층을 나눴다'가 아니라 '의존성이 한 방향으로만 흐른다'입니다 — presentation·application·domain·infrastructure 중 안쪽 계층이 바깥쪽을 모를 때만 비로소 채널을 추가하거나 저장소를 바꾸는 변경이 한곳에 머무릅니다.

## 이 글에서 다룰 문제

- 계층을 왜 나누고, 무엇을 기준으로 나눌까요?
- 각 계층은 어떤 책임을 가져야 할까요?
- 의존성은 어떤 방향으로만 흘러야 할까요?
- 전체 그림에서 가장 흔한 실수는 무엇일까요?
- 기본 용어을 실무에 적용할 때 주의할 점은 무엇일까요?
- 변경 전과 변경 후의 핵심 원리를 한 문장으로 설명하면 무엇일까요?

UI, 비즈니스 규칙, 인프라는 바뀌는 이유도 속도도 다릅니다. 웹 요청 형식은 자주 바뀔 수 있고, 외부 데이터베이스나 SaaS는 더 자주 흔들릴 수 있습니다. 반면 핵심 도메인 규칙은 상대적으로 천천히 변합니다.

이 셋을 한 계층에 섞으면 외부 변화가 내부 규칙까지 밀고 들어옵니다. 계층 아키텍처는 이 변동성 차이를 구조로 분리하는 방식입니다. 책임이 잘 나뉘면 웹 프레임워크를 바꾸더라도 도메인 규칙은 그대로 남기기 쉬워집니다.

## 전체 그림

계층 구조에서 먼저 기억할 점은 도메인이 가장 안정적인 중심이라는 사실입니다. 바깥 채널과 저장소는 도메인을 향해 붙지만, 도메인은 바깥 세부를 모르는 편이 좋습니다.

## 기본 용어

- <strong>표현 계층</strong>: HTTP, CLI, UI처럼 바깥과 만나는 접점입니다.
- <strong>애플리케이션 계층</strong>: 유스케이스 흐름을 조율하는 계층입니다.
- <strong>도메인 계층</strong>: 업무 규칙이 있는 가장 안정적인 계층입니다.
- <strong>인프라 계층</strong>: DB, 파일, 외부 SaaS 같은 변동이 큰 세부를 다룹니다.
- <strong>부패 방지 계층</strong>: 외부 모델이 도메인으로 그대로 스며드는 것을 막는 번역 계층입니다.

## 변경 전과 변경 후

**변경 전**

```python
# 한 함수가 HTTP, business, DB를 모두 처리함
@app.route("/charge")
def charge():
    body = request.json
    if body["amount"] <= 0: return "bad", 400
    db.execute("UPDATE wallet ...")
    return "ok"
```

**변경 후**

```python
# presentation
@app.route("/charge")
def charge_view():
    return charge_use_case(request.json)

# application
def charge_use_case(payload):
    cmd = ChargeCommand.from_payload(payload)
    return charge_service.run(cmd)
```

두 번째 구조에서는 표현 계층이 얇고, 업무 흐름은 애플리케이션 계층으로 이동합니다. 각 계층이 자기 책임만 맡으므로 수정 범위도 더 예측하기 쉬워집니다.

## 계층을 도입하는 다섯 단계

### 1단계 — 도메인을 먼저 분리한다

```python
# 1_domain.py
class Wallet:
    def debit(self, amount: int) -> None:
        if amount <= 0: raise ValueError
        self.balance -= amount
```

가장 먼저 분리할 것은 업무 규칙입니다. 금액이 0보다 커야 한다는 규칙은 웹 프레임워크나 DB 종류와 무관하게 살아남아야 합니다.

### 2단계 — 흐름을 유스케이스로 묶는다

```python
# 2_usecase.py
def charge(repo, user_id, amount):
    w = repo.get(user_id); w.debit(amount); repo.save(w)
```

유스케이스는 “무엇을 하는가”의 흐름을 담당합니다. 도메인 객체를 조합해 작업을 완료하지만, 표현 세부나 저장 구현은 직접 품지 않습니다.

### 3단계 — 표현 계층을 얇게 유지한다

```python
# 3_presentation.py
@app.route("/charge")
def view():
    return charge(repo, request.json["user"], request.json["amount"])
```

표현 계층은 입력을 받고 출력을 돌려주는 일에 집중해야 합니다. 라우터 안에서 업무 규칙이 커지기 시작하면 계층이 다시 흐려집니다.

### 4단계 — 인프라 어댑터를 둔다

```python
# 4_infra.py
class SqlWalletRepo:
    def get(self, uid): ...
    def save(self, w): ...
```

인프라는 도메인이 필요로 하는 모양을 구현합니다. 데이터베이스를 PostgreSQL에서 Redis로 바꿔도 도메인 규칙 자체는 그대로 남길 수 있어야 합니다.

### 5단계 — 부패 방지 계층으로 번역한다

```python
# 5_acl.py
def to_domain_user(external_json):
    return User(id=external_json["uid"], name=external_json["nm"])
```

외부 API 응답을 도메인 모델로 바로 쓰기 시작하면 외부 스키마가 도메인 내부 어휘를 오염시킵니다. 번역 계층을 두면 외부 변경 충격을 그 지점에서 흡수할 수 있습니다.

## 빠르게 검증해 보기

라우터 하나를 열고 HTTP 처리, 유스케이스 흐름, 도메인 규칙, 저장소 접근이 몇 줄씩 섞여 있는지 세어 보세요. 계층이 무너진 코드는 이 네 종류가 한 함수 안에 모여 있는 경우가 많습니다.

```text
router lines: input parsing, status code, JSON response
use-case lines: orchestration, transaction boundary
domain lines: validation, policy, invariant
infra lines: ORM call, SQL, SDK
```

**Expected output:** 표현 계층에는 HTTP 입출력만, 도메인에는 규칙만 남겨야 한다는 정리 포인트가 분명해집니다.

작은 프로젝트라면 네 계층을 모두 강제할 필요는 없습니다. 다만 서로 다른 이유로 바뀌는 코드를 한 함수에 쌓아 두는 상태는 피해야 합니다.

## 실패 신호와 먼저 볼 것

| 실패 신호 | 먼저 볼 것 |
| --- | --- |
| 라우터 함수가 길고 테스트도 어렵다 | 업무 흐름이 표현 계층에 남아 있는지 봅니다 |
| 도메인 모델에 ORM 세부가 많다 | 인프라가 도메인 안으로 새는지 확인합니다 |
| 외부 SaaS 응답 필드명이 도메인 곳곳에 보인다 | 부패 방지 계층이 필요한지 점검합니다 |

계층의 목적은 파일 구조를 예쁘게 만드는 것이 아니라, 바깥 변화가 안쪽 규칙을 직접 흔들지 못하게 막는 데 있습니다.

## 이 코드에서 먼저 볼 점

- 의존성은 도메인을 향하도록 정리됩니다.
- 표현 계층이 얇을수록 채널 교체 비용이 낮아집니다.
- 외부 모델은 번역을 거친 뒤 도메인으로 들어갑니다.

## 어디서 많이 헷갈릴까

계층 이름을 붙이는 것만으로 계층 아키텍처가 되는 것은 아닙니다. router 폴더, service 폴더, repository 폴더가 있어도 서비스가 ORM 모델과 HTTP 요청을 동시에 들고 있다면 실질적인 분리는 거의 없습니다.

또 다른 흔한 오해는 네 계층을 모든 프로젝트에 똑같이 강제하는 일입니다. 작은 스크립트나 단일 배치 작업에는 과할 수 있습니다. 중요한 것은 계층 개수보다, 서로 다른 이유로 바뀌는 코드를 같은 상자에 넣지 않는 감각입니다.

## 실무에서는 이렇게 본다

대부분의 백엔드는 이미 어떤 형태로든 계층 구조를 가집니다. 흔한 구성은 router → service → repository → model입니다. 여기에 외부 SaaS 연동이 들어오면 ACL을 추가해 외부 스키마를 도메인 바깥에서 번역하는 식입니다.

도메인 모델에 ORM 데코레이터가 잔뜩 붙기 시작하거나, 라우터가 업무 규칙을 대부분 품고 있으면 경계가 무너지고 있다는 신호로 봐도 됩니다. 계층 구조는 이런 누수를 빨리 발견하게 해 줍니다.

## 운영 체크리스트

- [ ] 도메인이 인프라 라이브러리를 직접 import하지 않는가?
- [ ] 유스케이스가 애플리케이션 계층에 모여 있는가?
- [ ] 표현 계층이 입력과 출력 처리에 집중하는가?
- [ ] 외부 경계에 부패 방지 계층이 필요한지 검토했는가?
- [ ] 계층 수가 시스템 크기에 비해 과하지 않은가?

## 연습 문제

1. 라우터 하나에서 업무 로직을 서비스로 끌어내려 보세요.
2. ORM 모델과 도메인 모델을 분리해 보세요.
3. 외부 SaaS 응답 하나에 ACL을 적용해 보세요.

## 현업 적용 관점에서 다시 정리

계층 아키텍처의 핵심은 호출 순서가 아니라 책임 분리입니다. 프레젠테이션·애플리케이션·도메인·인프라가 각자 다른 변경 리듬을 갖도록 만드는 것이 목적입니다.

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째 계층을 왜 나누고, 무엇을 기준으로 나눌, 둘째 각 계층은 어떤 책임을 가져야 할, 셋째 의존성은 어떤 방향으로만 흘러야 할입니다. 전체 그림에서 시작해 실무 적용까지 이어지는 흐름을 따라가면 이 주제의 전체 그림이 잡힙니다.

## 처음 질문으로 돌아가기

- **계층을 왜 나누고, 무엇을 기준으로 나눌까요?**
  - 계층을 왜 나누고, 무엇을 기준으로 나눌까요 — 본문에서 단계별로 설명합니다.
- **각 계층은 어떤 책임을 가져야 할까요?**
  - 각 계층은 어떤 책임을 가져야 할까요 — 본문에서 단계별로 설명합니다.
- **의존성은 어떤 방향으로만 흘러야 할까요?**
  - 의존성은 어떤 방향으로만 흘러야 할까요 — 본문에서 단계별로 설명합니다.
- **전체 그림에서 가장 흔한 실수는 무엇일까요?**
  - 계층 구조에서 먼저 기억할 점은 도메인이 가장 안정적인 중심이라는 사실입니다. 바깥 채널과 저장소는 도메인을 향해 붙지만, 도메인은 바깥 세부를 모르는 편이 좋습니다.
- **기본 용어을 실무에 적용할 때 주의할 점은 무엇일까요?**
  - 기본 용어을 실무에 적용할 때 주의할 점은 무엇일까요 — 본문에서 단계별로 설명합니다.
- **변경 전과 변경 후의 핵심 원리를 한 문장으로 설명하면 무엇일까요?**
  - 변경 전과 변경 후의 핵심 원리를 한 문장으로 설명하면 무엇일까요 — 본문에서 단계별로 설명합니다.
