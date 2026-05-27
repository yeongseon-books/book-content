---
series: backend-development-101
episode: 2
title: "Backend Development 101 (2/10): HTTP 서버 만들기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Backend
  - HTTP
  - Python
  - FastAPI
  - Networking
seo_description: HTTP 서버의 본질을 소켓부터 FastAPI까지 따라가는 입문 가이드입니다
last_reviewed: '2026-05-15'
---

# Backend Development 101 (2/10): HTTP 서버 만들기

브라우저에서 버튼을 눌렀는데 응답이 끊기거나, 프록시를 거치자 인증이 갑자기 풀리거나, 모니터링은 전부 200인데 사용자 문의는 계속 들어오는 날이 있습니다. 이때 프레임워크 API만 보고 있으면 원인이 흐려집니다. 요청과 응답이 실제로 어떤 바이트로 오가는지, 그 바이트를 누가 어떤 규칙으로 해석하는지까지 내려가야 문제가 풀립니다.

이 글은 Backend Development 101 시리즈의 2번째 글입니다.

![Backend Development 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/02/02-01-concept-at-a-glance.ko.png)
*Backend Development 101 2장 흐름 개요*

> HTTP 서버는 마법이 아니라 'TCP 위에서 요청을 받아 라우터로 보내고, 응답을 돌려주는 무한 루프'입니다 — 이 모델이 잡혀야 FastAPI·Flask·Express가 같은 일을 다르게 포장한 것이라는 게 보입니다.

## 먼저 던지는 질문

- HTTP 요청과 응답은 실제로 어떤 모양의 텍스트일까요?
- HTTP는 TCP 위에서 어떻게 동작할까요?
- status code와 header는 왜 단순 장식이 아니라 계약일까요?

## HTTP는 텍스트 프로토콜입니다

HTTP/1.x를 이해하는 가장 빠른 방법은 "메서드 함수"가 아니라 "문자열 규칙"으로 보는 것입니다. 서버는 결국 바이트 스트림을 읽고, 줄 단위 규칙(`
`)으로 경계를 나눠 의미를 붙입니다. 프레임워크는 이 파싱과 직렬화를 대신해 주는 레이어일 뿐입니다.

아래는 클라이언트가 서버로 보내는 실제 요청 텍스트 예시입니다.

```http
POST /users HTTP/1.1
Host: api.example.com
Content-Type: application/json
Accept: application/json
Authorization: Bearer eyJ...
Content-Length: 42

{"name":"jane","email":"jane@example.com"}
```

서버가 돌려주는 응답도 같은 구조입니다.

```http
HTTP/1.1 201 Created
Content-Type: application/json; charset=utf-8
Content-Length: 58
Cache-Control: no-store
Set-Cookie: sid=abc123; Path=/; HttpOnly; Secure

{"id":17,"name":"jane","email":"jane@example.com"}
```

핵심은 단순합니다. 첫 줄은 의미의 요약, 헤더는 처리 규칙, 빈 줄 이후는 본문입니다. 이 경계가 무너지면 프레임워크가 무엇이든 장애는 그대로 발생합니다.

## TCP 위에서 HTTP가 움직이는 방식

HTTP는 전송 계층인 TCP 위에서 동작합니다. HTTP 자체는 연결을 여닫지 않고, TCP가 만든 양방향 바이트 채널을 사용합니다.

| 단계 | TCP에서 일어나는 일 | HTTP 관점 의미 |
| --- | --- | --- |
| 1. connect | 클라이언트가 서버 IP:PORT에 연결 | 요청을 보낼 통로 생성 |
| 2. send | 클라이언트가 요청 바이트 전송 | request line + headers + body 전달 |
| 3. receive | 서버가 요청을 읽고 응답 바이트 전송 | status line + headers + body 반환 |
| 4. close 또는 재사용 | 연결 종료 또는 keep-alive 유지 | 다음 요청 재사용 여부 결정 |

운영 이슈는 대개 3번과 4번 사이에서 터집니다. 본문 길이 계산이 틀리면 상대는 아직 데이터가 남았다고 믿고 대기합니다. 반대로 너무 일찍 끊으면 클라이언트는 "응답이 잘렸다"고 판단합니다. HTTP를 이해한다는 말은 TCP 위에서 바이트 경계를 정확히 맞춘다는 뜻입니다.

## Request Anatomy: 무엇을 읽고 어떤 결정을 내리는가

요청은 크게 request line, headers, body로 나뉩니다. 중요한 점은 이 값들이 단순 메타데이터가 아니라 서버 분기 로직의 입력이라는 사실입니다.

### 1) Request Line: `METHOD PATH VERSION`

예: `GET /orders/42 HTTP/1.1`

- `METHOD`: 리소스에 어떤 종류의 행위를 기대하는지 나타냅니다. 캐시, 재시도, 멱등성 판단에 직접 쓰입니다.
- `PATH`: 라우팅 키입니다. `/orders/42`와 `/orders/42/`를 다르게 처리하는 시스템도 많습니다.
- `VERSION`: 파싱 규칙의 계약 버전입니다. HTTP/1.0, 1.1은 연결 처리 기본값이 다릅니다.

### 2) Headers: 처리 정책

| 헤더 | 서버가 실제로 하는 판단 |
| --- | --- |
| `Host` | 어떤 가상 호스트/서비스로 라우팅할지 결정 |
| `Content-Type` | 본문 디코딩 방식(JSON, form, multipart) 선택 |
| `Authorization` | 인증 미들웨어 검증 분기 |
| `Accept` | 응답 포맷(JSON/XML/HTML) 협상 |

`Host`는 HTTP/1.1에서 사실상 필수입니다. 누락 시 프록시/웹서버가 400으로 거절할 수 있습니다. `Content-Type`이 잘못되면 본문은 있어도 파서가 읽지 못해 415나 422로 이어집니다.

### 3) Body: 비즈니스 입력

body는 "있는가"보다 "어떤 헤더와 함께 오는가"가 더 중요합니다. `Content-Length: 0`이면 본문이 없다는 뜻이고, 값이 있으면 서버는 정확히 그 바이트 수만 읽어야 합니다. 이 수를 잘못 읽으면 다음 요청 경계가 무너집니다.

## Response Anatomy: 클라이언트가 다음 행동을 결정하는 정보

응답도 status line, headers, body로 구성됩니다.

### 1) Status Line: `HTTP/1.1 200 OK`

- 프로토콜 버전
- 상태 코드(기계가 읽는 신호)
- 이유 구문(사람 가독성)

클라이언트 라이브러리는 이유 구문보다 숫자 코드를 우선 해석합니다. 코드가 잘못되면 본문 메시지가 아무리 친절해도 자동화는 잘못 동작합니다.

### 2) 응답 헤더

| 헤더 | 의미 | 운영상 영향 |
| --- | --- | --- |
| `Content-Length` | 본문 바이트 길이 | 연결 재사용 시 프레임 경계 결정 |
| `Content-Type` | 본문 포맷 | 클라이언트 파싱 성공/실패 |
| `Set-Cookie` | 세션/상태 전달 | 인증 지속성, 보안 속성(`HttpOnly`, `Secure`) |
| `Cache-Control` | 캐시 정책 | 재요청 부하와 데이터 신선도 균형 |

특히 `Content-Length`는 keep-alive 환경에서 매우 중요합니다. 클라이언트는 이 길이를 기준으로 "이번 응답이 끝났는지" 판단하고 다음 요청을 같은 연결에 보낼지 결정합니다. 길이가 작으면 본문이 잘리고, 길이가 크면 상대는 더 오기를 기다리다 타임아웃이 납니다.

### 3) Body

body는 사용자 데이터 자체입니다. 문제는 body가 아니라 body를 둘러싼 경계 정보가 틀려서 생깁니다. 운영에서 "가끔 JSON parse error"가 뜨는 이슈는 애플리케이션 로직 버그보다 경계/인코딩 문제일 때가 많습니다.

## 상태 코드는 계약입니다

상태 코드는 문서용 장식이 아닙니다. 캐시, 재시도, 알람, 대시보드, SLA 계산이 여기에 의존합니다.

| 계열 | 의미 | 일반적 클라이언트 동작 |
| --- | --- | --- |
| 2xx | 요청 성공 | 성공 처리, 재시도 없음 |
| 3xx | 리소스 위치/접근 방식 변경 | 리다이렉트 추적 또는 정책 적용 |
| 4xx | 클라이언트 요청 문제 | 입력 수정 후 재시도 |
| 5xx | 서버 내부/일시 장애 | 백오프 재시도, 알람 트리거 |

상태 코드를 고를 때 바로 쓰는 의사결정 표는 아래가 실용적입니다.

| 상황 | 권장 코드 | 이유 |
| --- | --- | --- |
| 새 리소스 생성 성공 | `201 Created` | 생성 사실과 의미를 명시 |
| 비동기 작업 접수 | `202 Accepted` | 완료 아님, 접수만 성공 |
| 본문 없음 | `204 No Content` | 파싱 비용과 오해 감소 |
| 인증 토큰 없음/무효 | `401 Unauthorized` | 인증 필요 신호 |
| 권한 부족 | `403 Forbidden` | 인증은 됐지만 접근 불가 |
| 리소스 없음 | `404 Not Found` | 탐색/복구 가능한 실패 |
| 입력 규격 오류 | `422 Unprocessable Entity` | 필드 단위 검증 실패 전달 |
| 내부 예외 | `500 Internal Server Error` | 서버 책임 문제 명시 |
| 일시 과부하 | `503 Service Unavailable` | 재시도 가능성 신호 |

잘못된 코드 사용이 만드는 장애는 즉시 보이지 않습니다. 500을 200으로 감추면 에러율 알람이 잠잠해져 대응이 늦어집니다. 400을 500으로 보내면 클라이언트가 불필요한 재시도를 하면서 트래픽을 증폭시킵니다. 404를 200으로 보내면 CDN/브라우저 캐시가 오작동해 잘못된 화면을 오래 보관할 수 있습니다.

## 운영에서 특히 중요한 헤더

아래 헤더는 "있으면 좋다"가 아니라 누락 시 장애로 이어지기 쉬운 항목입니다.

| 헤더 | 제어 대상 | 빠졌을 때 흔한 실패 |
| --- | --- | --- |
| `Host` | 가상 호스트 라우팅 | 잘못된 백엔드로 라우팅 또는 400 |
| `Content-Length` | 바디 경계 | 응답 잘림, 클라이언트 대기 |
| `Content-Type` | 직렬화/파싱 | JSON을 문자열로 처리, 415/422 |
| `Authorization` | 인증 컨텍스트 | 사용자 식별 실패, 401 연쇄 |
| `Accept` | 응답 표현 협상 | 기대와 다른 포맷 반환 |
| `X-Forwarded-For` | 원본 클라이언트 IP | 레이트리밋/감사로그 왜곡 |
| `X-Forwarded-Proto` | 원본 스킴(HTTP/HTTPS) | 리다이렉트 루프, secure cookie 미발급 |
| `Connection` | 홉 단위 연결 정책 | 프록시 간 keep-alive 오해 |

`Connection`은 hop-by-hop 헤더라서 프록시가 그대로 전달하면 안 됩니다. 이 지점을 모르면 "프록시 뒤에서만" 발생하는 미묘한 끊김을 오래 추적하게 됩니다.

## Raw Socket → `http.server` → FastAPI

동일한 HTTP를 다루되, 레이어가 올라갈수록 반복 작업을 자동화합니다.

### 레벨 1: Raw Socket

```python
# 학습용: 요청/응답 경계를 직접 확인
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 9000))
server.listen(5)

while True:
    conn, _ = server.accept()
    data = conn.recv(4096)

    # 데모 목적: 첫 요청 라인만 출력
    first_line = data.split(b"
", 1)[0]
    print(first_line.decode("utf-8", errors="replace"))

    body = b'{"ok":true}'
    response = (
        b"HTTP/1.1 200 OK
"
        b"Content-Type: application/json
"
        + f"Content-Length: {len(body)}
".encode()
        + b"Connection: close

"
        + body
    )
    conn.sendall(response)
    conn.close()
```

직접 구현하면 무엇이 불편한지 명확해집니다. 요청 파싱, 헤더 정규화, 예외 처리, keep-alive, timeout, 로깅을 모두 수작업으로 해야 합니다.

### 레벨 2: 표준 라이브러리 `http.server`

```python
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'{"message":"hello"}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

HTTPServer(("127.0.0.1", 9000), Handler).serve_forever()
```

request line 파싱과 기본 헤더 처리는 표준 라이브러리가 대신합니다. 라우팅, 입력 검증, 의존성 주입, 비동기 처리까지는 여전히 제한적입니다.

### 레벨 3: FastAPI

```python
from fastapi import FastAPI, HTTPException, Response

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/items/{item_id}")
def get_item(item_id: int, response: Response):
    if item_id < 0:
        raise HTTPException(status_code=400, detail="item_id must be >= 0")

    response.headers["Cache-Control"] = "no-store"
    return {"item_id": item_id}
```

FastAPI는 라우팅, 검증, 문서화(OpenAPI), 직렬화, 예외 매핑을 자동화합니다. 서버 본질이 바뀌는 것은 아니고, 실수를 줄이는 안전장치가 늘어나는 것입니다.

## HTTP/1.1 Keep-Alive와 연결 재사용

HTTP/1.0은 기본이 연결 종료였고, HTTP/1.1은 기본이 keep-alive입니다. 따라서 현대 환경에서는 "응답 한 번 보내고 끝"보다 "같은 연결에서 여러 요청/응답"이 기본 가정입니다.

| 항목 | HTTP/1.0 기본 | HTTP/1.1 기본 |
| --- | --- | --- |
| 연결 정책 | 요청-응답 후 종료 | 연결 재사용 |
| 성능 특성 | 핸드셰이크 비용 반복 | 지연/CPU 절감 |
| 오류 양상 | 끊김이 비교적 명확 | 경계 오류가 연쇄로 증폭 |

HTTP/1.1 파이프라이닝은 이론상 여러 요청을 응답 대기 없이 연속 전송할 수 있지만, head-of-line blocking과 중간 장비 호환성 문제로 실무 채택이 낮았습니다. 그래서 today 운영에서는 HTTP/1.1 keep-alive + 멀티 커넥션 또는 HTTP/2 멀티플렉싱으로 넘어갑니다.

요점은 keep-alive 자체가 문제가 아니라, 경계 정보를 틀리게 제공했을 때 피해 범위가 커진다는 사실입니다. 한 응답의 `Content-Length` 오류가 같은 연결의 다음 요청까지 오염시킬 수 있습니다.

## 운영 시나리오로 보는 장애 패턴

### 1) 응답이 잘려 보이는 경우: 잘못된 `Content-Length`

증상: 모바일 앱에서 가끔 JSON parse error, 브라우저에서는 간헐적 `net::ERR_CONTENT_LENGTH_MISMATCH`.

원인: 본문은 512바이트인데 `Content-Length: 480`으로 송신.

대응: 애플리케이션에서 수동 계산을 피하고 프레임워크 직렬화에 맡깁니다. gzip/브로틀리 압축을 프록시가 수행한다면 어느 레이어가 길이를 책임지는지 명확히 분리합니다.

### 2) 프록시 뒤에서만 인증이 풀리는 경우: hop-by-hop 헤더 처리 오류

증상: 로컬/직접 호출은 정상인데 API Gateway 경유 시 세션 불안정.

원인: 중간 프록시가 `Connection` 헤더에 선언된 토큰을 잘못 전달하거나 삭제하면서 기대한 헤더가 사라짐.

대응: end-to-end 헤더(`Authorization`, `X-Request-Id`)와 hop-by-hop 헤더를 구분해 프록시 규칙을 점검합니다.

### 3) 클라이언트가 응답을 끝없이 기다리는 경우: close 누락 또는 경계 누락

증상: 일부 SDK 호출이 타임아웃까지 대기.

원인: `Content-Length`도 없고 `Transfer-Encoding: chunked`도 없으며 연결도 닫지 않음.

대응: 세 가지 중 하나는 반드시 만족시킵니다. 길이 명시, chunked 사용, 명시적 연결 종료.

### 4) 모니터링은 전부 200인데 사용자 불만이 계속되는 경우

증상: 에러 대시보드 0%, 고객센터는 실패 문의 증가.

원인: 비즈니스 실패를 `{ "ok": false }` 형태로 200 응답에 실어 보냄.

대응: 실패 성격에 맞는 4xx/5xx를 사용하고, 2xx는 실제 성공으로만 제한합니다. 모니터링 지표(SLI)와 응답 계약을 일치시킵니다.

## 디버깅 도구: 어디까지 내려가야 하는가

### 1) `curl -v`

```bash
curl -v -H "Accept: application/json" http://127.0.0.1:9000/items/1
```

- 요청 헤더와 응답 헤더를 동시에 확인할 수 있습니다.
- TLS, 리다이렉트, 연결 재사용 힌트를 빠르게 얻습니다.

### 2) HTTPie

```bash
http --print=HhBb GET :9000/items/1 Authorization:"Bearer demo"
```

- 사람이 읽기 좋은 출력으로 헤더/바디를 분리해서 보여 줍니다.
- API 계약 비교 시 회귀 검증에 유용합니다.

### 3) tcpdump / Wireshark

- 애플리케이션 로그와 프록시 로그가 충돌할 때 최종 근거로 사용합니다.
- 패킷 캡처는 비용이 크므로, `curl -v`와 서버 액세스 로그로 좁힌 뒤 최소 구간만 캡처하는 방식이 효율적입니다.

## 자주 하는 실수와 왜 위험한지

| 실수 | 왜 자주 발생하는가 | 실제 비용 |
| --- | --- | --- |
| 모든 실패를 200으로 반환 | "클라이언트가 파싱하기 쉽다"는 오해 | 알람 무력화, 장애 탐지 지연 |
| `Content-Type` 생략 | 프레임워크가 알아서 넣을 거라는 가정 | 언어/SDK별 파싱 불일치 |
| GET에 의미 있는 body 설계 | 내부 호출만 고려한 설계 | 프록시/캐시/SDK 호환성 붕괴 |
| 프록시 신뢰 경계 미정의 | 인프라/앱 팀 책임 경계 불명확 | IP 위조 수용, HTTPS 판별 실패 |
| timeout 기본값 방치 | 로컬 테스트에서는 재현이 어려움 | 스레드 고갈, 큐 적체, 연쇄 장애 |

실수의 공통점은 "당장 동작"만 확인하고 "계약의 수명"을 보지 않는다는 사실입니다. HTTP 계약은 팀 내부만의 규칙이 아니라, 브라우저·모바일 SDK·프록시·모니터링 시스템이 함께 해석하는 공용 언어입니다.

## 시니어 엔지니어는 HTTP를 이렇게 다룹니다

시니어가 프레임워크를 버리고 소켓 코드를 매번 작성하는 것은 아닙니다. 오히려 반대입니다. 프레임워크를 적극적으로 사용하되, 장애 시에는 언제든 프로토콜 레벨로 내려갈 수 있도록 관측 지점을 설계합니다. 예를 들어 "요청 ID를 어느 레이어에서 발급하고 어디까지 전달할지", "4xx/5xx를 어떤 규칙으로 분류해 대시보드에 반영할지"를 기능 개발 단계에서 함께 결정합니다.

상태 코드와 헤더는 구현 세부사항이 아니라 운영 정책의 표면입니다. API 문서에 200/400/500만 적는 팀과, 201/202/204/409/422/503까지 명확히 쓰는 팀은 장애 복구 속도에서 차이가 납니다. 후자의 팀은 실패를 분류 가능한 이벤트로 만들기 때문에 재시도 정책, 사용자 메시지, 경보 임계치가 모두 정렬됩니다.

네트워크 경계가 늘어나는 환경에서는 "내 서비스가 보낸 응답"보다 "클라이언트가 실제로 받은 응답"이 더 중요합니다. 로드밸런서, CDN, API Gateway를 거치면 헤더가 추가·삭제·변환될 수 있습니다. 그래서 시니어는 로컬 성공 화면보다 종단 간 캡처와 로그 상관관계를 신뢰합니다. HTTP 서버를 만든다는 말은 엔드포인트 함수를 작성하는 일을 넘어, 이 종단 간 계약을 유지하는 운영 설계를 포함합니다.

## 요청-응답 계약을 검증하는 실전 루틴

기능 테스트가 통과해도 HTTP 계약은 깨질 수 있습니다. 직렬화 라이브러리 교체, 프록시 설정 변경, 압축 옵션 추가 같은 변경이 프로토콜 표면을 바꾸기 때문입니다. 운영 안정성을 높이려면 "비즈니스 테스트"와 별도로 "프로토콜 테스트"를 둬야 합니다.

아래 루틴은 팀에서 바로 적용할 수 있는 최소 세트입니다.

1. 계약 스냅샷을 남깁니다. `curl -v` 또는 HTTPie로 대표 요청 5~10개를 캡처해 상태 코드/헤더/본문 샘플을 기준선으로 저장합니다.
2. 배포 파이프라인에서 비교합니다. 회귀 테스트가 성공해도 상태 코드가 바뀌거나 `Cache-Control`이 사라지면 실패로 처리합니다.
3. 프록시 경유 결과를 별도로 검증합니다. 앱 직통 결과와 게이트웨이 경유 결과를 나눠 비교해야 hop-by-hop 문제를 조기에 잡을 수 있습니다.

테이블 기반 점검을 병행하면 누락을 줄일 수 있습니다.

| 점검 항목 | 기대값 | 실패 시 영향 |
| --- | --- | --- |
| 생성 API 상태 코드 | `201` | 클라이언트 후속 분기 실패 |
| 검증 실패 상태 코드 | `422` 또는 `400` | 재시도 정책 왜곡 |
| 응답 `Content-Type` | `application/json` | SDK 파싱 실패 |
| 응답 `Cache-Control` | 엔드포인트 정책과 일치 | 과캐시/과호출 발생 |
| `X-Request-Id` 전파 | ingress~app~egress 일관 | 장애 추적 시간 증가 |

## 작은 실험: 같은 본문, 다른 헤더가 만드는 차이

같은 JSON 본문이라도 헤더에 따라 클라이언트 행동이 달라집니다.

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 17

{"ok":true}
```

위 응답은 대부분의 클라이언트가 즉시 JSON으로 파싱합니다. 반대로 아래처럼 `Content-Type`이 없으면 SDK별로 해석이 갈립니다.

```http
HTTP/1.1 200 OK
Content-Length: 17

{"ok":true}
```

브라우저 fetch는 문자열 처리 후 개발자가 직접 `JSON.parse`를 호출해야 하는 경우가 생기고, 일부 사내 SDK는 기본값을 `text/plain`으로 처리해 파싱 에러를 냅니다. 서버 입장에서는 "본문은 같다"고 생각하기 쉽지만, 소비자 입장에서는 전혀 다른 계약입니다.

`Cache-Control`도 마찬가지입니다. 조회 API에서 캐시 허용 정책을 빼먹으면 매 호출이 원서버까지 도달해 피크 시간에 병목이 생깁니다. 반대로 민감 데이터 응답에서 `no-store`를 빼먹으면 공유 단말에서 정보가 잔류할 수 있습니다. 헤더는 성능과 보안을 동시에 제어하는 운영 파라미터입니다.

## 처음 질문으로 돌아가기

- **HTTP 요청과 응답은 실제로 어떤 모양의 텍스트일까요?**  
  request line/status line, 헤더, 빈 줄, 본문으로 이어지는 구조이며, `
` 경계와 `Content-Length` 같은 길이 정보가 파싱의 기준입니다. 본문 예시에서 본 것처럼 사람이 읽는 텍스트이면서 동시에 기계가 엄격히 해석하는 형식입니다.
- **HTTP는 TCP 위에서 어떻게 동작할까요?**  
  TCP 연결을 열고(connect), 요청 바이트를 보내고(send), 응답 바이트를 받고(receive), 닫거나 재사용(close/keep-alive)합니다. HTTP/1.1에서는 연결 재사용이 기본이라 응답 경계가 틀리면 다음 요청까지 연쇄 오류가 발생합니다.
- **status code와 header는 왜 단순 장식이 아니라 계약일까요?**  
  상태 코드는 재시도·캐시·모니터링의 분기 조건이고, 헤더는 라우팅·인증·파싱·보안 정책의 입력입니다. 잘못 쓰면 "모니터링은 정상인데 사용자만 실패" 같은 관측 불일치가 생기며, 운영 대응이 늦어집니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- **HTTP 서버 만들기 (현재 글)**
- Routing과 Controller (예정)
- Service Layer (예정)
- Database Layer (예정)
- 인증과 권한 (예정)
- Logging과 Error Handling (예정)
- 백엔드 테스트 (예정)
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [HTTP messages (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages)
- [HTTP status codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [FastAPI responses](https://fastapi.tiangolo.com/advanced/response-directly/)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [curl manual](https://curl.se/docs/manual.html)

Tags: Backend, HTTP, Python, FastAPI, Networking
