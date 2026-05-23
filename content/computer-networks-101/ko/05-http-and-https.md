---
series: computer-networks-101
episode: 5
title: "Computer Networks 101 (5/10): HTTP와 HTTPS"
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
  - 네트워크
  - HTTP
  - HTTPS
  - REST
  - 헤더
seo_description: HTTP 메시지 구조와 메서드, 상태 코드의 의미를 파악하고 HTTPS가 보안을 강화하는 방식과 주요 헤더의 역할을 상세히 다룹니다.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (5/10): HTTP와 HTTPS

이 글은 Computer Networks 101 시리즈의 5번째 글입니다.


![Computer Networks 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/05/05-01-concept-at-a-glance.ko.png)
*Computer Networks 101 5장 흐름 개요*

## 먼저 던지는 질문

- HTTP 메시지는 어떤 모양으로 구성될까요?
- 메서드와 상태 코드는 왜 의미를 정확히 지켜야 할까요?
- `Content-Type`, `Cache-Control`, `Authorization` 같은 헤더는 왜 중요할까요?

## 왜 중요한가

HTTP는 백엔드, 프론트엔드, 모바일, 데이터 서비스, ML 서빙까지 거의 모든 시스템의 공통 언어입니다. 메서드와 상태 코드를 잘못 쓰면 캐시, 재시도, 오류 처리 정책이 조용히 망가집니다. HTTPS가 기본값이 된 시대에도 왜 필요한지 설명하지 못하면 인증서 만료, mixed content, HSTS 같은 사고가 늘 낯설게 느껴집니다.

> HTTP는 약속된 메시지 형식이고, REST는 그 약속을 자원 중심으로 정리하는 스타일입니다.

## 핵심 그림

요청과 응답은 모두 "시작줄 + 헤더 + 빈 줄 + 본문"이라는 같은 구조를 가집니다.

```text
요청 메시지:                          응답 메시지:
┌─────────────────────────┐          ┌─────────────────────────┐
│ GET /users/42 HTTP/1.1  │ ← 시작줄 │ HTTP/1.1 200 OK         │
├─────────────────────────┤          ├─────────────────────────┤
│ Host: api.example.com   │          │ Content-Type: app/json  │
│ Accept: application/json│ ← 헤더   │ Cache-Control: max-age=60│
│ Authorization: Bearer…  │          │ Content-Length: 45      │
├─────────────────────────┤          ├─────────────────────────┤
│                         │ ← 빈 줄  │                         │
├─────────────────────────┤          ├─────────────────────────┤
│ (본문 없음)              │ ← 본문   │ {"id":42,"name":"Kim"}  │
└─────────────────────────┘          └─────────────────────────┘
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 메서드 | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |
| 상태 코드 | 1xx 정보, 2xx 성공, 3xx 리다이렉트, 4xx 클라이언트 오류, 5xx 서버 오류 |
| 헤더 | 타입, 길이, 캐시, 인증 같은 메타데이터 |
| 본문 | JSON, HTML, 바이너리 등 실제 데이터 |
| TLS | HTTPS의 S를 만드는 암호화 계층 |
| 멱등성 | 같은 요청을 여러 번 보내도 결과가 동일한 성질 (GET, PUT, DELETE) |
| Content Negotiation | 클라이언트와 서버가 Accept/Content-Type으로 형식을 합의하는 과정 |

## 적용 전후 비교
**Before — "HTTP는 브라우저가 알아서 하는 것"**

```text
브라우저가 페이지를 가져오면 끝이다.
```

**After — "HTTP는 TCP 위를 흐르는 메시지다"**

```text
DNS → TCP handshake → (TLS handshake) → HTTP request/response → close
각 단계는 모두 측정 가능하고 디버깅 가능하다
```

## 단계별로 따라하기

### 1단계: `curl -v`로 요청과 응답 보기

```bash
curl -v https://example.com/
# * Trying 93.184.216.34:443...
# * Connected to example.com (93.184.216.34) port 443
# * TLS handshake... (생략)
# > GET / HTTP/2
# > Host: example.com
# > User-Agent: curl/8.5.0
# > Accept: */*
# >
# < HTTP/2 200
# < content-type: text/html; charset=UTF-8
# < content-length: 1256
# < cache-control: max-age=604800
# < etag: "3147526947"
```

`-v` 옵션은 헤더뿐 아니라 TLS 핸드셰이크 과정도 함께 보여 줍니다. 여기서 주목할 점은 `cache-control: max-age=604800`입니다. 7일 동안 캐시해도 된다는 뜻입니다.

### 2단계: HTTP 메서드와 멱등성 이해하기

```text
| 메서드   | 용도         | 멱등성 | 안전  | 본문 |
|---------|-------------|-------|------|-----|
| GET     | 리소스 읽기   | Yes   | Yes  | No  |
| HEAD    | 헤더만 읽기   | Yes   | Yes  | No  |
| POST    | 리소스 생성   | No    | No   | Yes |
| PUT     | 전체 교체     | Yes   | No   | Yes |
| PATCH   | 부분 수정     | No    | No   | Yes |
| DELETE  | 리소스 삭제   | Yes   | No   | No  |
| OPTIONS | 허용 메서드 조회 | Yes | Yes  | No  |
```

멱등성이 중요한 이유는 네트워크 장애 시 재시도 정책 때문입니다. GET이나 PUT은 재시도해도 안전하지만, POST는 중복 생성 위험이 있어 별도 대책이 필요합니다.

### 3단계: Python 클라이언트 만들기

```python
import requests

r = requests.get(
    'https://api.github.com/repos/python/cpython',
    headers={'Accept': 'application/vnd.github+json'},
    timeout=5,
)
print(r.status_code, r.headers['content-type'])
print(r.json()['stargazers_count'])

# 조건부 요청 — ETag 활용
etag = r.headers.get('etag')
r2 = requests.get(
    'https://api.github.com/repos/python/cpython',
    headers={'If-None-Match': etag},
    timeout=5,
)
print(r2.status_code)  # 304 Not Modified — 본문 전송 없음
```

### 4단계: 가장 작은 HTTP 서버

```python
# server.py — 플라스크
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

@app.get('/users/<int:uid>')
def get_user(uid):
    return jsonify(id=uid, name=f'user{uid}'), 200

@app.post('/users')
def create_user():
    body = request.get_json()
    if not body or 'name' not in body:
        abort(400, description="name field is required")
    return jsonify(id=99, **body), 201, {'Location': '/users/99'}

@app.delete('/users/<int:uid>')
def delete_user(uid):
    return '', 204

if __name__ == '__main__':
    app.run(port=8000)
```

```bash
# 생성
curl -s -X POST localhost:8000/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"alice"}' | python -m json.tool
# {"id": 99, "name": "alice"}

# 조회
curl -s localhost:8000/users/42 | python -m json.tool
# {"id": 42, "name": "user42"}

# 삭제
curl -s -o /dev/null -w "%{http_code}" -X DELETE localhost:8000/users/42
# 204

# 잘못된 요청
curl -s -X POST localhost:8000/users \
  -H 'Content-Type: application/json' \
  -d '{}' -w "\n%{http_code}"
# 400
```

### 5단계: 캐시 헤더 실험하기

```python
import hashlib
from datetime import datetime
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

@app.get('/now')
def now():
    data = datetime.utcnow().isoformat()
    resp = jsonify(now=data)
    resp.headers['Cache-Control'] = 'public, max-age=60'
    return resp

@app.get('/stable')
def stable():
    content = '{"message": "this rarely changes"}'
    etag = hashlib.md5(content.encode()).hexdigest()

    if request.headers.get('If-None-Match') == etag:
        return '', 304

    resp = make_response(content)
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['ETag'] = etag
    resp.headers['Cache-Control'] = 'public, max-age=3600'
    return resp
```

이 설정이 만드는 동작을 정리하면 다음과 같습니다.

```text
첫 요청:       GET /stable → 200 + ETag: "abc123" + body
60초 이내 재요청: 브라우저가 캐시에서 직접 응답 (네트워크 요청 없음)
60초 후 재요청:  GET /stable + If-None-Match: "abc123" → 304 (body 없음)
내용 변경 후:   GET /stable + If-None-Match: "abc123" → 200 + 새 body
```

운영에서 성능을 가장 크게 움직이는 도구가 헤더 한 줄인 경우가 많습니다.

### 6단계: 상태 코드 올바르게 사용하기

```text
자주 쓰는 상태 코드 정리:

2xx 성공
  200 OK            — 일반적인 성공
  201 Created       — 리소스 생성 성공 (Location 헤더와 함께)
  204 No Content    — 성공했지만 본문 없음 (DELETE에 적합)

3xx 리다이렉트
  301 Moved Permanently — 영구 이동 (검색 엔진이 URL 갱신)
  302 Found             — 임시 이동
  304 Not Modified      — 캐시 유효, 본문 전송 안 함

4xx 클라이언트 오류
  400 Bad Request       — 요청 형식 오류
  401 Unauthorized      — 인증 필요
  403 Forbidden         — 인증은 됐지만 권한 없음
  404 Not Found         — 리소스 없음
  429 Too Many Requests — 속도 제한 초과

5xx 서버 오류
  500 Internal Server Error — 서버 버그
  502 Bad Gateway           — 업스트림 서버 응답 이상
  503 Service Unavailable   — 일시적 과부하
  504 Gateway Timeout       — 업스트림 응답 시간 초과
```

상태 코드를 올바르게 쓰는 것이 왜 중요한지 실제 사례로 보겠습니다.

```python
# Bad: 모든 응답을 200으로 보내는 안티패턴
@app.get('/users/<int:uid>')
def get_user_bad(uid):
    user = db.find(uid)
    if not user:
        return jsonify(error='not found', success=False), 200  # 위험!
    return jsonify(user=user, success=True), 200

# Good: HTTP 의미 체계를 지키는 설계
@app.get('/users/<int:uid>')
def get_user_good(uid):
    user = db.find(uid)
    if not user:
        abort(404)
    return jsonify(user), 200
```

Bad 패턴에서는 모니터링 도구가 5xx 비율로 장애를 감지할 수 없고, CDN이 에러 응답까지 캐시할 수 있으며, 클라이언트의 재시도 로직이 작동하지 않습니다.

### 8단계: 요청/응답 파이프라인 전체 관찰

```bash
# tcpdump로 HTTP/1.1 평문 트래픽 관찰 (포트 8000)
sudo tcpdump -i lo -A 'tcp port 8000' -c 30

# 출력 예시 (요청)
# GET /users/42 HTTP/1.1
# Host: localhost:8000
# User-Agent: curl/8.5.0
# Accept: */*

# 출력 예시 (응답)
# HTTP/1.1 200 OK
# Content-Type: application/json
# Content-Length: 28
#
# {"id":42,"name":"user42"}
```

HTTP/1.1은 평문이므로 tcpdump로 메시지 전체를 볼 수 있습니다. HTTPS는 암호화되어 내용이 보이지 않지만, Wireshark에서 서버의 private key를 등록하거나 `SSLKEYLOGFILE` 환경변수를 설정하면 복호화할 수 있습니다.

```bash
# Wireshark용 TLS 키 로그 생성
SSLKEYLOGFILE=/tmp/tls-keys.log curl https://example.com
# Wireshark → Preferences → Protocols → TLS → (Pre)-Master-Secret log filename
```

### 7단계: HTTPS 검증 보기

```bash
# 만료된 인증서
curl -v https://expired.badssl.com/ 2>&1 | grep "certificate"
# * SSL certificate problem: certificate has expired

# 자체 서명 인증서
curl -v https://self-signed.badssl.com/ 2>&1 | grep "certificate"
# * SSL certificate problem: self-signed certificate

# 정상 인증서의 체인 확인
openssl s_client -connect example.com:443 -showcerts </dev/null 2>/dev/null | \
  grep "s:" | head -5
# s:C = US, ST = California, ... CN = example.com
# s:C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
```

브라우저와 `curl`은 인증서 체인을 검증해 위장된 서버를 막습니다. 다음 글에서 TLS 내부를 자세히 엽니다.

## 이 코드에서 먼저 볼 점

- 요청과 응답은 결국 메시지입니다. HTTP/2와 HTTP/3는 바이너리 프레임을 쓰지만 의미는 같습니다.
- 메서드는 의미를 가진 동사입니다. GET은 읽기, POST는 생성이라는 약속을 깨면 주변 도구가 함께 망가집니다.
- 상태 코드는 클라이언트, 캐시, 재시도 로직이 믿고 사용하는 신호입니다.
- 캐시 헤더 하나로 백엔드 부하를 크게 줄일 수 있습니다.
- `Location` 헤더는 201 응답에서 새 리소스의 URL을 알려주는 관례입니다.
- HTTP/2에서는 하나의 스트림이 실패해도 다른 스트림에 영향을 주지 않지만, TCP 레벨의 패킷 손실은 모든 스트림을 멈출 수 있습니다. 이것이 HTTP/3가 QUIC(UDP 기반)을 선택한 이유입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| GET으로 데이터를 변경 | 프록시와 재시도가 의도치 않은 변화를 일으킴 | 변경은 POST / PUT / PATCH / DELETE로 보낸다 |
| 모든 오류를 200으로 반환 | 모니터링과 재시도 정책이 깨짐 | 적절한 4xx / 5xx를 사용한다 |
| `Content-Type`을 생략 | 클라이언트 파싱 실패 | `application/json`처럼 명시한다 |
| HTTPS 검증을 끔 | MITM 위험 노출 | 운영에서는 절대 끄지 않는다 |
| 큰 응답을 매번 비압축으로 전송 | 대역폭과 지연 증가 | gzip / br, ETag, Last-Modified를 활용한다 |

## HTTP 버전별 비교

| 특성 | HTTP/1.1 | HTTP/2 | HTTP/3 |
| --- | --- | --- | --- |
| 전송 | TCP | TCP | QUIC (UDP 위) |
| 다중화 | 불가 (커넥션당 1 요청) | 스트림 멀티플렉싱 | 스트림 멀티플렉싱 |
| 헤더 압축 | 없음 | HPACK | QPACK |
| HOL Blocking | 있음 | TCP 레벨에서 있음 | 없음 |
| 연결 설정 | 1-RTT (TCP) + 1-RTT (TLS) | 같음 | 0-RTT 가능 |
| 서버 푸시 | 없음 | 있음 | 있음 (거의 안 씀) |

```bash
# HTTP 버전 확인
curl -sI --http2 https://example.com | head -1
# HTTP/2 200

# HTTP/3 지원 확인
curl --http3-only -sI https://cloudflare.com | head -1
# HTTP/3 200
```

HTTP/2의 가장 큰 이점은 하나의 TCP 연결로 여러 요청을 동시에 보낼 수 있다는 사실입니다. HTTP/1.1에서는 브라우저가 도메인당 6개 연결을 열어야 했던 병렬화가 하나의 연결에서 가능해집니다.

### HTTP/2 멀티플렉싱 동작 예시

```text
HTTP/1.1 (순차적):
Connection 1: GET /style.css  ─────────────────> response
Connection 2: GET /app.js    ─────────────────> response
Connection 3: GET /logo.png  ─────────────────> response
Connection 4: GET /data.json ─────────────────> response
↓ 4개 커넥션 오버헤드

HTTP/2 (다중화):
Connection 1: Stream 1 ─ GET /style.css  ──────> response
             Stream 3 ─ GET /app.js    ──────> response
             Stream 5 ─ GET /logo.png  ──────> response
             Stream 7 ─ GET /data.json ──────> response
↓ 1개 커넥션으로 모두 처리
```

### CORS와 Preflight 요청

프론트엔드에서 다른 도메인의 API를 호출할 때 브라우저는 먼저 OPTIONS 요청(프리플라이트)을 보냅니다.

```bash
# 프리플라이트 요청 예시
curl -v -X OPTIONS https://api.example.com/data \
  -H "Origin: https://app.example.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type, Authorization"

# 응답 예시
# HTTP/2 204
# access-control-allow-origin: https://app.example.com
# access-control-allow-methods: GET, POST, PUT, DELETE
# access-control-allow-headers: Content-Type, Authorization
# access-control-max-age: 86400
```

```python
# Flask에서 CORS 설정
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r'/api/*': {
        'origins': ['https://app.example.com'],
        'methods': ['GET', 'POST', 'PUT', 'DELETE'],
        'allow_headers': ['Content-Type', 'Authorization'],
        'max_age': 86400,
    }
})
```

`access-control-max-age: 86400`은 프리플라이트 결과를 24시간 캐시하라는 뜻입니다. 이 헤더가 없으면 브라우저는 매 요청마다 OPTIONS를 보내서 지연이 2배로 늘어납니다.

### 쿠키 vs 토큰 인증 비교

| 특성 | 세션 쿠키 | Bearer 토큰 (JWT) |
| --- | --- | --- |
| 저장 위치 | 브라우저 Cookie jar | 클라이언트 (localStorage, 메모리) |
| 전송 방식 | `Cookie` 헤더 (자동) | `Authorization: Bearer <token>` (수동) |
| CSRF 취약 | 있음 (자동 전송) | 없음 |
| XSS 취약 | HttpOnly로 방어 가능 | localStorage면 노출 위험 |
| 서버 상태 | 세션 저장소 필요 | stateless (DB 조회 불필요) |
| 확장성 | 서버 간 세션 공유 필요 | 확장 용이 |

```python
# Bearer 토큰 검증 예시
from functools import wraps
from flask import request, abort
import jwt

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').removeprefix('Bearer ')
        if not token:
            abort(401)
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            abort(401)
        except jwt.InvalidTokenError:
            abort(403)
        return f(*args, payload=payload, **kwargs)
    return decorated

@app.get('/protected')
@require_auth
def protected(payload):
    return jsonify(user=payload['sub'])
```

## 실무에서는 이렇게 보입니다

- REST API는 자원과 메서드 조합으로 CRUD를 표현합니다.
- GraphQL과 gRPC는 HTTP/2 위에 올라갑니다.
- CDN은 `Cache-Control`과 ETag를 활용해 edge 캐시를 구성합니다.
- 인증은 `Authorization` 헤더나 쿠키로 전달됩니다.
- 모니터링에서는 5xx 비율과 p99 지연 시간이 핵심 지표가 됩니다.

### 운영 헤더 설계 패턴

```python
# 공통 응답 헤더를 미들웨어로 적용
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Request-Id'] = request.headers.get('X-Request-Id', str(uuid4()))
    return response
```

HSTS(`Strict-Transport-Security`)는 브라우저에게 "이 도메인은 앞으로 HTTPS로만 접속하라"고 알려줍니다. `max-age=31536000`은 1년입니다. 이 헤더가 있으면 사용자가 `http://`로 입력해도 브라우저가 자동으로 `https://`로 바꿉니다.

### 요청 추적과 디버깅

```bash
# X-Request-Id로 요청 추적
curl -v -H "X-Request-Id: debug-001" https://api.example.com/users/1

# 응답 시간 측정
curl -o /dev/null -s -w "DNS: %{time_namelookup}s\nTCP: %{time_connect}s\nTLS: %{time_appconnect}s\nTotal: %{time_total}s\n" https://example.com
# DNS: 0.012s
# TCP: 0.035s
# TLS: 0.098s
# Total: 0.145s
```

이 출력에서 각 단계의 시간을 분리할 수 있습니다. TLS가 전체의 43%를 차지한다는 것을 알면 HTTP/3의 0-RTT가 왜 중요한지 체감됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 API를 설계할 때 메서드, 상태 코드, 헤더, 본문을 따로 보지 않고 함께 봅니다. 예를 들어 실패를 `errors` 필드에 담아 200으로 보내는 설계는 클라이언트뿐 아니라 캐시와 재시도 정책까지 함께 무너뜨립니다. HTTP 의미 체계를 지켜야 외부 도구도 함께 작동합니다.

또한 HTTP/1.1에서 생각을 멈추지 않습니다. HTTP/2의 멀티플렉싱, HTTP/3의 0-RTT와 전송 특성이 체감 지연을 어떻게 바꾸는지 이해하고, 새로운 기능을 도입할 가치와 위험을 함께 판단합니다.

운영 사고에서 가장 많이 보는 HTTP 관련 실수는 다음 세 가지입니다.

1. **인증서 만료 방치**: Let's Encrypt 자동 갱신이 실패해도 알림이 없으면 사이트 전체가 접속 불가
2. **Cache-Control 누락**: API 응답에 캐시 헤더가 없으면 CDN이 기본 정책(보통 캐시 안 함)을 적용해 원본 부하 폭증
3. **502/504 원인 분리 실패**: 로드밸런서 → 앱 서버 구간에서 어디가 느린지 모르면 무작정 스케일업

## 체크리스트

- [ ] HTTP 메시지의 네 부분을 설명할 수 있다
- [ ] 자주 쓰는 메서드와 상태 코드의 의미를 안다
- [ ] 멱등성과 안전성의 차이를 설명할 수 있다
- [ ] `Content-Type`과 `Cache-Control`을 올바르게 설정할 수 있다
- [ ] HTTPS의 세 가지 보장(기밀성, 무결성, 신원)을 안다
- [ ] HTTP/1.1, /2, /3를 한 줄씩 비교할 수 있다
- [ ] `curl -w`로 요청의 각 단계별 시간을 측정할 수 있다

## 연습 문제

1. 좋아하는 사이트에 `curl -v`를 실행하고 요청/응답 헤더를 캡처한 뒤 각 헤더의 의미를 설명해 보세요.
2. 위 Flask 서버에 ETag 기반 캐시(`If-None-Match` → `304`)를 추가해 보세요.
3. 위협 모델 관점에서 "왜 이제 거의 모든 사이트가 HTTPS를 쓰는가"를 한 단락으로 설명해 보세요.
4. `curl -w`로 HTTP/1.1과 HTTP/2 요청의 시간 차이를 비교하고 결과를 분석해 보세요.

## 정리와 다음 글

HTTP는 메시지 형식에 대한 약속이고, REST는 그 약속을 자원 단위로 조직하는 스타일입니다. HTTPS는 그 위에 TLS의 보안 보장을 더합니다. 메서드, 상태 코드, 헤더를 정확히 다루는 것만으로도 시스템 품질은 바로 올라갑니다.

다음 글에서는 HTTPS의 S를 여는 열쇠, TLS 기초를 다룹니다.

## 처음 질문으로 돌아가기

- **HTTP 메시지는 어떤 모양으로 구성될까요?**
  - "시작줄 + 헤더 + 빈 줄 + 본문"의 네 부분으로 구성됩니다. 요청에서는 시작줄이 `GET /path HTTP/1.1`이고, 응답에서는 `HTTP/1.1 200 OK`입니다. HTTP/2부터는 바이너리 프레임이지만 의미 구조는 동일합니다.
- **메서드와 상태 코드는 왜 의미를 정확히 지켜야 할까요?**
  - 브라우저, CDN, 프록시, 모니터링 도구가 모두 HTTP 의미 체계에 의존하기 때문입니다. GET으로 데이터를 바꾸면 캐시가 원치 않는 변경을 복제하고, 200으로 오류를 보내면 재시도 로직이 실패를 감지하지 못합니다.
- **`Content-Type`, `Cache-Control`, `Authorization` 같은 헤더는 왜 중요할까요?**
  - `Content-Type`이 없으면 클라이언트가 본문을 파싱하지 못하고, `Cache-Control`이 없으면 CDN과 브라우저의 캐시 전략이 예측 불가해지며, `Authorization`이 없으면 인증된 요청과 비인증 요청을 구분할 수 없습니다. 헤더는 본문만큼 중요한 메시지의 절반입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Networks 101 (1/10): 네트워크란 무엇인가?](./01-what-is-a-network.md)
- [Computer Networks 101 (2/10): IP와 subnet](./02-ip-and-subnet.md)
- [Computer Networks 101 (3/10): TCP와 UDP](./03-tcp-and-udp.md)
- [Computer Networks 101 (4/10): DNS](./04-dns.md)
- **HTTP와 HTTPS (현재 글)**
- TLS 기초 (예정)
- 라우팅과 NAT (예정)
- Load Balancer (예정)
- WebSocket과 실시간 통신 (예정)
- 네트워크 문제 디버깅 (예정)

<!-- toc:end -->

## 참고 자료

- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [MDN — HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [High Performance Browser Networking — Ilya Grigorik](https://hpbn.co/)
- [시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/computer-networks-101/ko)

Tags: Computer Science, 네트워크, HTTP, HTTPS, REST, 헤더
