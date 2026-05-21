---
title: "API Design 101 (1/10): API란 무엇인가?"
series: api-design-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
  - Computer Science
  - APIDesign
  - REST
  - HTTP
  - Backend
  - WebDevelopment
last_reviewed: '2026-05-20'
seo_description: API의 정의, 역할, 좋은 API의 조건을 시리즈의 첫 글에서 정리합니다.
---

# API Design 101 (1/10): API란 무엇인가?

팀이 같은 기능을 각자 다른 방식으로 호출하기 시작하면, 그때부터 구현 문제가 아니라 계약 문제가 터집니다. 서버 코드는 멀쩡한데도 호출 규칙이 흐릿하면 클라이언트마다 다른 가정을 붙이고, 작은 변경이 바깥에서는 장애처럼 번집니다.

이 글은 API Design 101 시리즈의 첫 번째 글입니다.

여기서는 API를 단순한 함수 호출이나 URL 집합이 아니라, 오래 유지해야 하는 외부 계약으로 보는 관점을 먼저 세웁니다. 그래야 이후 글에서 다룰 REST, 리소스, 상태 코드, 문서화 원칙이 한 흐름으로 연결됩니다.


![클라이언트-API 계약-서버 구조](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/01/01-01-concept-at-a-glance.ko.png)
*클라이언트와 서버 사이에 API 계약이 놓이는 구조*

## 먼저 던지는 질문

- API는 정확히 무엇이며, 왜 시스템의 외부 계약이라고 부를까요?
- 라이브러리 API와 웹 API는 무엇이 같고 무엇이 다를까요?
- 좋은 API라고 부르려면 어떤 조건을 갖춰야 할까요?

## API란 정확히 무엇인가

API(Application Programming Interface)는 소프트웨어 구성 요소 사이의 **상호작용 규칙**입니다. 이 정의는 짧지만 실제로는 세 가지 의미를 동시에 품고 있습니다.

첫째, **경계(boundary)**입니다. API가 존재한다는 것은 "여기서부터는 내 책임이 아닙니다"라는 선이 그어졌다는 뜻입니다. 함수 호출이든 HTTP 요청이든, 그 선을 넘는 순간 호출하는 쪽은 제공하는 쪽의 내부를 모른 채 결과만 받습니다.

둘째, **계약(contract)**입니다. 경계를 넘기 위해서는 양쪽이 합의한 규칙이 필요합니다. "이런 형태로 보내면, 이런 형태로 돌려주겠다"는 약속이 계약입니다. 계약이 불분명하면 호출하는 쪽은 추측으로 구현하고, 추측은 언젠가 깨집니다.

셋째, **안정성(stability)**입니다. 내부 구현은 얼마든지 바뀔 수 있지만, 계약이 유지되는 한 외부 사용자는 영향을 받지 않습니다. 데이터베이스를 PostgreSQL에서 MongoDB로 교체하든, 캐시 계층을 추가하든, 응답 형태가 같으면 클라이언트 코드는 한 줄도 바꿀 필요가 없습니다.

> 좋은 API는 쉽게 바뀌는 인터페이스가 아니라 오래 유지되는 약속에 가깝습니다.

## 라이브러리 API와 웹 API: 같은 개념, 다른 전송 방식

API라는 단어를 들으면 대부분 HTTP와 JSON을 먼저 떠올리지만, 사실 우리가 매일 쓰는 라이브러리 함수도 API입니다.

| 비교 항목 | 라이브러리 API | 웹 API |
|---|---|---|
| 호출 방식 | 함수 호출 (`json.dumps(data)`) | HTTP 요청 (`GET /users`) |
| 전송 매체 | 프로세스 내 메모리 | 네트워크 (TCP/IP) |
| 계약 정의 | 함수 시그니처, docstring, 타입 | URL, HTTP method, request/response schema |
| 에러 전달 | 예외(Exception) | HTTP status code + error body |
| 버전 관리 | 패키지 버전 (`pip install lib==2.0`) | URL prefix (`/v2/users`) 또는 header |
| 지연 시간 | 마이크로초 | 밀리초~초 |
| 실패 모드 | 대부분 즉시 예외 | timeout, 네트워크 단절, 부분 실패 |

공통점은 명확합니다. **둘 다 입력과 출력의 형태를 약속하고, 그 약속이 깨지면 사용자가 피해를 입는 구조**입니다. 차이는 전송 매체와 실패 모드뿐입니다. 웹 API는 네트워크를 타기 때문에 라이브러리 API에는 없는 문제(지연, 타임아웃, 재시도, 멱등성)를 추가로 고려해야 합니다.

이 차이가 이 시리즈의 나머지 9편을 채우는 이유이기도 합니다. 라이브러리 API 설계는 함수 시그니처와 타입만 잘 잡으면 대부분 해결되지만, 웹 API는 리소스 모델링, HTTP 의미론, 에러 표준화, 페이지네이션, 버전 관리까지 설계 영역이 훨씬 넓습니다.

## 왜 API 설계가 중요한가

API는 시스템의 얼굴입니다. 내부 구현은 팀 안에서 언제든 고칠 수 있지만, 외부에 공개된 API는 한번 배포하면 쉽게 바꿀 수 없습니다. 이미 누군가 그 형태에 의존해서 코드를 작성했기 때문입니다.

실무에서 API 설계가 잘못되면 다음 패턴으로 문제가 확산됩니다.

**1단계 — 초기 혼란.** 계약이 불명확한 API를 받은 클라이언트 개발자는 응답을 직접 찍어 보면서 "아, 이 필드가 null일 때도 있구나"를 발견합니다. 이 지식은 코드 주석이나 개인 노트에만 남습니다.

**2단계 — 방어적 코드 폭발.** 두 번째, 세 번째 클라이언트가 붙으면 각자 다른 방어 코드를 작성합니다. 어떤 팀은 null 필드를 빈 문자열로 치환하고, 어떤 팀은 해당 요청 자체를 건너뜁니다.

**3단계 — 하위 호환성 지옥.** 서버 팀이 응답 형태를 개선하려 해도, 이미 방어 코드가 각양각색이라 어떤 변경이 누구를 깨뜨릴지 예측할 수 없습니다. 결국 새 버전을 만들지만, 구버전도 폐기할 수 없어 두 벌을 유지합니다.

이 악순환의 시작점은 대부분 **"계약을 먼저 정의하지 않고 구현부터 했다"**입니다.

## 좋은 API의 조건

좋은 API란 무엇일까요? 업계에서 반복적으로 언급되는 기준을 다섯 가지로 정리합니다.

| 조건 | 의미 | 위반 시 증상 |
|---|---|---|
| **예측 가능성** | 하나의 endpoint를 보고 나머지를 추측할 수 있음 | 클라이언트 개발자가 매번 문서를 뒤짐 |
| **일관성** | 명명 규칙, 에러 형태, 인증 방식이 전체에서 통일 | 같은 API인데 endpoint마다 규칙이 다름 |
| **최소 놀라움** | HTTP 표준과 업계 관행을 따름 | `DELETE /users/1`이 200 대신 204를 주면 혼동 발생 |
| **진화 가능성** | 필드를 추가해도 기존 클라이언트가 깨지지 않음 | 모든 변경이 breaking change |
| **자기 설명성** | 응답만 봐도 다음 행동을 알 수 있음 | 매번 별도 문서를 참조해야 다음 단계를 알 수 있음 |

이 다섯 가지는 이 시리즈의 나머지 글에서 계속 돌아옵니다. REST 설계(2편), 리소스 모델링(3편), 상태 코드(4편), 스키마(5편), 에러(7편), 버전 관리(9편) 모두 이 기준을 구현 수준으로 내리는 작업입니다.

## 전후 비교

**Before (계약이 없음)**

```python
# 클라이언트가 서버 내부 구조에 직접 의존
data = open("/var/db/users.json").read()
```

클라이언트가 서버 내부 파일 구조까지 알아야 합니다. 서버가 저장 경로를 바꾸는 순간 클라이언트가 깨집니다.

**After (API 계약을 사용)**

```python
import requests

# 계약: GET /users → 200 + JSON array of user objects
response = requests.get("https://api.example.com/users")
assert response.status_code == 200
users = response.json()
```

클라이언트는 "GET /users를 보내면 사용자 목록이 JSON 배열로 온다"는 계약만 압니다. 서버가 PostgreSQL에서 DynamoDB로 마이그레이션해도 이 코드는 그대로 동작합니다.

## 실습: API를 이해하는 다섯 단계

### Step 1 — 라이브러리 API 호출

```python
# 1_lib_api.py
import json

data = json.dumps({"user": "alice", "age": 30})
print(data)
# 출력: {"user": "alice", "age": 30}
```

`json.dumps`도 API입니다. 입력(Python dict)과 출력(JSON 문자열) 사이의 계약이 문서화되어 있고, 이 계약은 Python 버전이 올라가도 유지됩니다. 우리는 이 함수의 내부 구현을 읽어본 적 없지만 신뢰합니다. 이것이 좋은 API의 힘입니다.

### Step 2 — 웹 API 호출

```python
# 2_web_api.py
import requests

r = requests.get("https://api.github.com/repos/python/cpython")
print(f"Status: {r.status_code}")
print(f"Repo: {r.json()['full_name']}")
print(f"Stars: {r.json()['stargazers_count']}")
```

웹 API에서는 HTTP가 전송 수단이고, JSON이 데이터 형식입니다. 여기서 중요한 점은 GitHub이 이 endpoint의 응답 형태를 바꾸지 않는 한, 전 세계의 GitHub CLI, IDE 플러그인, CI 스크립트가 계속 동작한다는 것입니다. 수만 개의 클라이언트가 하나의 계약에 의존합니다.

### Step 3 — 계약을 읽는다

```python
# 3_contract.py
# GitHub REST API 문서에서 발췌
# GET /repos/{owner}/{repo}
#
# 경로 매개변수:
#   owner (string, required) — 저장소 소유자
#   repo  (string, required) — 저장소 이름
#
# 성공 응답: 200 OK
#   body: { "full_name": str, "stargazers_count": int, ... }
#
# 실패 응답: 404 Not Found
#   body: { "message": "Not Found" }
```

문서는 단순한 설명서가 아니라 **계약 그 자체**입니다. 위 정보만 있으면 GitHub 서버 코드를 한 줄도 보지 않고도 올바른 클라이언트를 작성할 수 있습니다. 반대로, 이 문서가 없다면 클라이언트 개발자는 실제 요청을 보내고 응답을 찍어 보면서 형태를 추측해야 합니다.

### Step 4 — 직접 서버를 만든다

```python
# 4_min_server.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/health")
def health():
    """계약: GET /health → 200 + {"status": "ok"}"""
    return jsonify(status="ok")

@app.get("/users")
def list_users():
    """계약: GET /users → 200 + JSON array"""
    users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    return jsonify(users)

if __name__ == "__main__":
    app.run(port=8000)
```

가장 작은 API 서버입니다. 이미 두 개의 계약이 정의되어 있습니다. `/health`는 시스템 상태를, `/users`는 사용자 목록을 돌려줍니다. 여기서 핵심은 구현이 아니라 **계약이 먼저** 정해졌다는 점입니다.

### Step 5 — 클라이언트로 검증한다

```python
# 5_call.py
import requests

# /health 계약 검증
r = requests.get("http://localhost:8000/health")
assert r.status_code == 200
assert r.json() == {"status": "ok"}

# /users 계약 검증
r = requests.get("http://localhost:8000/users")
assert r.status_code == 200
assert isinstance(r.json(), list)
assert "name" in r.json()[0]

print("All contracts verified.")
```

테스트는 계약이 실제로 지켜지는지 검증합니다. 이 스크립트를 CI에 넣으면, 서버 코드를 리팩토링할 때마다 계약이 깨지지 않았는지 자동으로 확인할 수 있습니다. 이것이 **계약 테스트(contract testing)**의 가장 단순한 형태입니다.

## 계약의 구성 요소

모든 API 계약은 다음 네 가지를 명시해야 합니다.

| 구성 요소 | 설명 | 예시 |
|---|---|---|
| **Endpoint** | 어디로 보내는가 | `GET /users/{id}` |
| **Input** | 무엇을 보내는가 | path param `id`, query param `fields` |
| **Output** | 무엇을 돌려받는가 | `200` + `{"id": 1, "name": "Alice"}` |
| **Error** | 실패하면 무엇을 받는가 | `404` + `{"error": "user_not_found"}` |

하나라도 빠지면 클라이언트는 추측해야 합니다. 특히 Error 정의를 빠뜨리는 경우가 실무에서 가장 흔합니다. "성공할 때는 잘 되는데, 실패하면 무슨 형태가 오는지 모르겠다"는 불만은 거의 항상 에러 계약 부재에서 옵니다.

## 자주 하는 실수 다섯 가지

1. **계약 문서 없이 시작합니다.** 서버 개발자가 "일단 만들고 나중에 문서 쓰자"고 하면, 그 "나중"은 대부분 오지 않습니다. 클라이언트 개발자는 Postman으로 하나씩 찍어 보면서 동작을 역추적합니다.

2. **상태 코드를 무시합니다.** 성공이든 실패든 항상 `200`을 돌려보내고, 본문 안에 `{"success": false, "error": "..."}`를 넣습니다. 이러면 HTTP 캐시, 로드 밸런서, 모니터링 도구가 에러를 감지하지 못합니다.

3. **에러 본문이 제각각입니다.** 어떤 endpoint는 `{"error": "msg"}`, 어떤 endpoint는 `{"message": "msg", "code": 123}`, 또 어떤 endpoint는 plain text를 돌려보냅니다. 클라이언트는 endpoint마다 다른 에러 파서를 만들어야 합니다.

4. **버전 없이 배포합니다.** 응답에 필드를 추가하거나 제거할 때 버전 구분 없이 덮어쓰면, 모든 클라이언트가 동시에 영향을 받습니다. "배포했더니 앱이 터졌다"는 보고가 올라옵니다.

5. **클라이언트 관점 없이 설계합니다.** 내부 데이터 모델을 그대로 노출하면 편하지만, 클라이언트에게는 불필요한 필드가 잔뜩 오고 정작 필요한 정보는 여러 번 호출해야 얻을 수 있습니다.

## 실무에서 만나는 API 계약의 형태

현업에서 API 계약은 다양한 형태로 존재합니다.

| 형태 | 사용처 | 특징 |
|---|---|---|
| OpenAPI (Swagger) spec | REST API | YAML/JSON으로 기계가 읽을 수 있음 |
| GraphQL schema | GraphQL API | 타입 시스템 기반, 클라이언트가 필요한 필드만 선택 |
| gRPC `.proto` 파일 | 마이크로서비스 내부 통신 | 바이너리, 스키마 강제, 코드 생성 |
| SDK/라이브러리 타입 정의 | 클라우드 SDK, 오픈소스 | TypeScript `.d.ts`, Python stub 파일 |
| README + 예제 코드 | 소규모 내부 API | 비정형, 사람이 읽어야 함 |

GitHub REST API, Stripe API, Google Maps API는 모두 OpenAPI 명세를 제공합니다. 내부 시스템에서도 OpenAPI나 gRPC proto를 쓰는 팀이 늘고 있습니다. **성숙한 팀일수록 내부 API도 외부 공개 API처럼 관리합니다.** 그래야 팀 간 의존성이 커져도 계약이 경계를 지켜 줍니다.

## 시니어 엔지니어의 API 설계 사고방식

숙련된 엔지니어가 새 API를 설계할 때 머릿속에서 일어나는 과정을 순서대로 풀어 봅니다.

1. **"이 API의 소비자는 누구인가?"** — 프론트엔드 팀인지, 모바일 앱인지, 다른 백엔드 서비스인지에 따라 응답 형태와 인증 방식이 달라집니다.
2. **"최소한의 계약으로 목적을 달성할 수 있는가?"** — 불필요한 필드를 노출하면 나중에 제거하기 어렵습니다. 추가는 쉽지만 제거는 breaking change입니다.
3. **"에러는 어떤 형태로 돌려줄 것인가?"** — 성공 경로보다 실패 경로를 먼저 설계합니다. 에러 처리를 나중에 붙이면 일관성이 깨집니다.
4. **"이 계약이 6개월 뒤에도 유효한가?"** — 지금 당장 편한 설계가 미래에 족쇄가 되는 경우를 경험으로 알고 있습니다.
5. **"문서와 코드가 동기화되는 구조인가?"** — OpenAPI spec에서 코드를 생성하거나, 코드에서 spec을 자동 추출하는 파이프라인을 선호합니다.

## 검증 포인트와 실패 신호

- **Expected output:** `GET /health` 호출에서 `200`과 `{"status": "ok"}`가 함께 돌아오면 가장 작은 계약이 제대로 유지된다고 볼 수 있습니다.
- **First check:** 클라이언트 예제가 서버 내부 경로나 private 함수 이름을 언급한다면 이미 계약 경계가 무너지고 있는 신호입니다.
- **Failure mode:** 상태 코드를 무시하고 본문만 읽는 클라이언트가 늘어나면, 이후 에러 설계와 버전 관리 단계에서 하위 호환성이 급격히 나빠집니다.

## 체크리스트

- [ ] 이 API에 공개 문서가 있는가?
- [ ] 입력과 출력의 형태가 명시적인가?
- [ ] 상태 코드 목록이 명시적인가?
- [ ] 에러 본문의 형태가 일관적인가?
- [ ] 클라이언트 예제가 함께 제공되는가?
- [ ] 계약을 검증하는 테스트가 CI에 포함되어 있는가?

## 연습 문제

1. 자주 쓰는 라이브러리에서 API 함수 다섯 개를 골라 입력과 출력을 표로 정리해 보세요. 어떤 함수는 예외를 던지고 어떤 함수는 None을 돌려주는지도 비교해 보세요.
2. 공개 웹 API(GitHub, JSONPlaceholder, OpenWeather 등) 문서를 하나 읽고 실제로 endpoint 하나를 호출해 보세요. 문서에 적힌 응답 형태와 실제 응답이 정확히 일치하는지 확인합니다.
3. 위 Step 4의 Flask 서버를 띄우고 `/users/{id}` endpoint를 추가해 보세요. 존재하지 않는 ID를 요청했을 때 어떤 status code와 body를 돌려줄지 미리 정의한 뒤 구현합니다.

## 정리와 다음 글

API는 계약입니다. 호출하는 쪽과 제공하는 쪽이 합의한 입력과 출력의 약속이며, 이 약속이 안정적으로 유지될수록 시스템 전체의 변경 비용이 낮아집니다. 라이브러리 API든 웹 API든 본질은 같지만, 웹 API는 네트워크라는 불확실성이 추가되면서 설계에서 고려할 사항이 훨씬 많아집니다.

이 시리즈의 다음 글에서는 웹 API 계약이 가장 자주 구현되는 형태인 **REST의 기본 원칙**을 다룹니다. 리소스 중심 사고, HTTP method의 의미, stateless 통신이 왜 API 설계의 기본 골격이 되었는지 살펴봅니다.


## 실전 계약 확장: 스펙·예제·운영 신호를 한 번에 맞추기

개념을 이해한 뒤 실제 팀에서 흔들리는 지점은 거의 같습니다. 문장 설명은 충분한데, 요청/응답 예제와 오류 형식, 페이지네이션 규칙, 버전 정책, 레이트 리밋 신호가 문서와 코드에서 따로 놀기 시작하는 순간입니다. 이 절은 그 간극을 줄이기 위해, 어떤 주제의 API 글이든 공통으로 넣어야 하는 실전 앵커를 정리합니다.

### OpenAPI 조각: endpoint 계약을 텍스트가 아니라 스키마로 고정하기

```yaml
openapi: 3.1.0
info:
  title: API Design 101 Example
  version: 1.2.0
paths:
  /v1/orders:
    get:
      summary: 주문 목록 조회
      parameters:
        - in: query
          name: limit
          schema: { type: integer, minimum: 1, maximum: 100, default: 20 }
        - in: query
          name: cursor
          schema: { type: string }
      responses:
        '200':
          description: 조회 성공
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderListResponse'
        '429':
          description: 요청 제한 초과
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
components:
  schemas:
    OrderListResponse:
      type: object
      required: [data, page]
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/Order'
        page:
          $ref: '#/components/schemas/PageInfo'
    PageInfo:
      type: object
      required: [has_next]
      properties:
        next_cursor: { type: string, nullable: true }
        has_next: { type: boolean }
    ErrorResponse:
      type: object
      required: [error]
      properties:
        error:
          type: object
          required: [code, message, trace_id]
          properties:
            code: { type: string, example: RATE_LIMIT_EXCEEDED }
            message: { type: string }
            trace_id: { type: string }
            retryable: { type: boolean, default: false }
```

스키마를 이렇게 고정하면 팀원마다 "대충 이런 형식"으로 기억하던 상태에서 벗어납니다. 특히 `429` 응답처럼 운영에서 자주 만나는 경계 케이스를 spec에 먼저 넣어 두면, 문서·테스트·SDK가 같은 신호를 보게 됩니다.

### 요청/응답 JSON 샘플: 클라이언트가 바로 호출 가능한 수준으로 제시하기

```json
{
  "request": {
    "method": "POST",
    "path": "/v1/orders",
    "headers": {
      "Authorization": "Bearer {ACCESS_TOKEN}",
      "Idempotency-Key": "b7f9f7b8-6cd1-4c9e-9ad0-58ad8e9f45ac",
      "Content-Type": "application/json"
    },
    "body": {
      "customer_id": "cus_2026_001",
      "items": [
        {"product_id": "p-100", "quantity": 2},
        {"product_id": "p-200", "quantity": 1}
      ],
      "currency": "KRW"
    }
  },
  "response": {
    "status": 201,
    "headers": {
      "Location": "/v1/orders/ord_01JXYZ",
      "X-RateLimit-Remaining": "119"
    },
    "body": {
      "id": "ord_01JXYZ",
      "status": "created",
      "total_amount": 54000,
      "currency": "KRW",
      "created_at": "2026-05-21T09:30:00Z"
    }
  }
}
```

실제 소비자는 문장 정의보다 예제를 먼저 읽습니다. 그래서 예제는 "읽기 좋은 형태"가 아니라 "실행 가능한 형태"로 제공해야 합니다. 헤더 이름, 필드 타입, 상태 코드가 모두 들어간 샘플이 있어야 첫 호출 실패율이 내려갑니다.

### 오류 응답 스키마: 디버깅 단서를 일관된 키로 고정하기

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "items[1].quantity must be >= 1",
    "trace_id": "4b6f39e6c4f14f8f9f4aa2f1a7b8c918",
    "retryable": false,
    "details": [
      {
        "field": "items[1].quantity",
        "reason": "min_value",
        "expected": ">= 1",
        "actual": 0
      }
    ]
  }
}
```

`code`와 `trace_id`를 고정하면 운영 중 협업 속도가 크게 올라갑니다. 클라이언트는 `code`로 분기하고, 서버 운영자는 `trace_id`로 로그를 찾습니다. 이 둘이 매번 바뀌면 같은 장애를 두 번 분석하게 됩니다.

### 페이지네이션·필터·정렬: 확장 가능한 쿼리 규칙으로 설계하기

```http
GET /v1/orders?limit=20&cursor=eyJpZCI6Im9yZF8wMUpYWiJ9&status=paid&sort=-created_at
```

```json
{
  "data": [
    {"id": "ord_01JXYZ", "status": "paid", "created_at": "2026-05-20T23:59:20Z"},
    {"id": "ord_01JXYY", "status": "paid", "created_at": "2026-05-20T23:58:02Z"}
  ],
  "page": {
    "next_cursor": "eyJpZCI6Im9yZF8wMUpYWSJ9",
    "has_next": true,
    "limit": 20
  }
}
```

커서 기반 구조를 초기에 잡아 두면 데이터가 커졌을 때도 계약을 바꾸지 않고 버틸 수 있습니다. offset이 당장 단순해 보여도, 쓰기 부하가 높은 시스템에서는 중복/누락 페이지 이슈가 빠르게 드러납니다.

### 레이트 리밋: 숫자와 복구 시점을 같이 전달하기

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1716286500
Content-Type: application/json
```

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Retry after 30 seconds.",
    "trace_id": "f0e8d83a8d8f4d1da8f796f0dfcb66f6",
    "retryable": true
  }
}
```

`429`를 반환하면서 복구 시점을 주지 않으면 클라이언트는 무의미한 재시도를 반복합니다. `Retry-After`와 남은 quota 헤더를 같이 제공해야 트래픽이 안정적으로 회복됩니다.

### 버전 전략: 경로/헤더 정책과 폐기 절차를 함께 운영하기

```http
Deprecation: true
Sunset: Wed, 31 Dec 2026 23:59:59 GMT
Link: </docs/changelog#v1-sunset>; rel="deprecation"
```

버전 표기는 시작일 뿐입니다. 중요한 것은 종료 절차를 예측 가능하게 운영하는 일입니다. 어떤 필드가 언제 사라지는지, 대체 엔드포인트가 무엇인지, SDK 최소 버전이 무엇인지를 changelog와 reference에 동시에 반영해야 실제 마이그레이션이 진행됩니다.

### 구현 체크: 계약 드리프트를 CI에서 차단하기

- OpenAPI lint 실패를 merge 차단 규칙으로 둡니다.
- 스키마 예제 JSON을 contract test 입력으로 재사용합니다.
- `429`, `409`, `422` 같은 경계 응답을 스냅샷 테스트에 포함합니다.
- changelog가 없는 breaking change PR은 리뷰 단계에서 반려합니다.

요약하면, 좋은 API 글의 품질은 설명 문단 길이가 아니라 "코드·문서·운영이 같은 계약을 바라보는가"로 측정됩니다. 이 절의 앵커를 반복적으로 적용하면 시리즈의 어느 장을 읽더라도 독자가 같은 설계 원칙을 재사용할 수 있습니다.


## 처음 질문으로 돌아가기

- **API는 정확히 무엇이며, 왜 시스템의 외부 계약이라고 부를까요?**
  - API는 소프트웨어 구성 요소 사이의 상호작용 규칙입니다. "외부 계약"이라 부르는 이유는 내부 구현과 독립적으로 존재하며, 한번 공개되면 쉽게 바꿀 수 없기 때문입니다. 데이터베이스를 바꾸든 언어를 바꾸든, 계약이 유지되면 클라이언트는 영향을 받지 않습니다.
- **라이브러리 API와 웹 API는 무엇이 같고 무엇이 다를까요?**
  - 둘 다 입력과 출력의 형태를 약속하는 계약이라는 점은 같습니다. 차이는 전송 매체(메모리 vs 네트워크)와 실패 모드(즉시 예외 vs timeout/부분 실패)입니다. 웹 API는 네트워크 불확실성 때문에 재시도, 멱등성, 타임아웃 같은 추가 설계가 필요합니다.
- **좋은 API라고 부르려면 어떤 조건을 갖춰야 할까요?**
  - 예측 가능성, 일관성, 최소 놀라움, 진화 가능성, 자기 설명성 다섯 가지입니다. 이 조건이 갖춰지면 클라이언트 개발자는 하나의 endpoint를 배우고 나머지를 추측할 수 있으며, 서버가 진화해도 기존 코드가 깨지지 않습니다.

<!-- toc:begin -->
## 시리즈 목차

- **API란 무엇인가? (현재 글)**
- REST 기본 (예정)
- 리소스 설계 (예정)
- HTTP method와 status code (예정)
- Request와 response schema (예정)
- Pagination과 filtering (예정)
- Error response 설계 (예정)
- OpenAPI와 Swagger (예정)
- Versioning (예정)
- 좋은 API 문서 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [What is an API? (MDN)](https://developer.mozilla.org/en-US/docs/Glossary/API)
- [GitHub REST API](https://docs.github.com/en/rest)
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [Flask Quickstart](https://flask.palletsprojects.com/quickstart/)
- [Stripe API Design](https://stripe.com/docs/api)
- [Google API Design Guide](https://cloud.google.com/apis/design)

Tags: Computer Science, APIDesign, REST, HTTP, Backend, WebDevelopment
