---
series: computer-networks-101
episode: 5
title: HTTP와 HTTPS
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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
seo_description: HTTP 요청과 응답의 구조, 메서드와 상태 코드, 헤더, 그리고 HTTPS가 더해 주는 보안 보장을 한 번에 정리합니다.
last_reviewed: '2026-05-04'
---

# HTTP와 HTTPS

> Computer Networks 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: HTTP는 어떤 모양의 메시지이고, "S"가 붙으면 정확히 무엇이 더해지는 걸까요?

> HTTP는 텍스트 기반의 단순한 요청/응답 프로토콜입니다. 메서드, 경로, 헤더, 본문 — 이 네 부분만 알면 모든 REST API와 웹사이트가 보입니다. HTTPS는 그 위에 TLS를 끼워 넣어 도청·변조·위장을 막습니다. 6편에서 자세히 다루지만, 오늘은 그림자만 봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- HTTP 메시지 구조(시작줄, 헤더, 본문)
- 자주 쓰는 메서드와 상태 코드
- 중요한 헤더(Content-Type, Cache-Control, Authorization)
- HTTP/1.1, HTTP/2, HTTP/3의 차이
- HTTPS가 보장하는 세 가지

## 왜 중요한가

HTTP는 백엔드/프론트엔드/모바일/데이터·ML 서빙까지 사실상 모든 서비스의 공통 언어입니다. 메서드와 상태 코드를 잘못 쓰면 캐시·재시도·에러 처리가 모두 어긋납니다. HTTPS는 이제 기본값이지만, "왜 필요한가?"를 답하지 못하면 인증서 만료·혼합 콘텐츠·HSTS 사고가 미스터리로 남습니다.

> HTTP는 "약속된 텍스트 메시지의 모양"이고, REST는 그 약속을 자원 단위로 정리한 스타일입니다.

## 개념 한눈에 보기

```text
요청
GET /users/42 HTTP/1.1
Host: api.example.com
Accept: application/json
Authorization: Bearer ...

응답
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=60

{"id": 42, "name": "..."}
```

요청과 응답은 모두 "시작줄 + 헤더 + 빈 줄 + 본문"입니다.

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 메서드 | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |
| 상태 코드 | 1xx 정보, 2xx 성공, 3xx 리다이렉트, 4xx 클라이언트 오류, 5xx 서버 오류 |
| 헤더 | 메타데이터(타입, 길이, 캐시, 인증 등) |
| 본문 | 실제 데이터(JSON, HTML, 바이너리 등) |
| TLS | HTTPS의 "S"를 만드는 암호화 계층 |

## Before / After

**Before — "HTTP는 마법":**

```text
브라우저가 페이지를 가져온다 — 끝.
```

**After — "HTTP는 텍스트 메시지 + TCP":**

```text
DNS → TCP handshake → (TLS handshake) → HTTP request/response → close
각 단계가 측정 가능하고 디버깅 가능
```

## 실습: 단계별로 따라하기

### 1단계: curl로 요청과 응답 보기

```bash
curl -v https://example.com/
# > GET / HTTP/2
# > Host: example.com
# < HTTP/2 200
# < content-type: text/html; charset=UTF-8
```

`-v`는 헤더와 TLS handshake까지 보여 줍니다.

### 2단계: Python에서 클라이언트

```python
import requests
r = requests.get(
    'https://api.github.com/repos/python/cpython',
    headers={'Accept': 'application/vnd.github+json'},
    timeout=5,
)
print(r.status_code, r.headers['content-type'])
print(r.json()['stargazers_count'])
```

### 3단계: 가장 작은 HTTP 서버

```python
# server.py — Flask
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.get('/users/<int:uid>')
def get_user(uid):
    return jsonify(id=uid, name=f'user{uid}'), 200

@app.post('/users')
def create_user():
    body = request.get_json()
    return jsonify(id=99, **body), 201

if __name__ == '__main__':
    app.run(port=8000)
```

```bash
curl -s localhost:8000/users/42
curl -s -X POST localhost:8000/users -H 'Content-Type: application/json' -d '{"name":"a"}'
```

### 4단계: 캐시 헤더 실험

```python
@app.get('/now')
def now():
    from datetime import datetime
    resp = jsonify(now=datetime.utcnow().isoformat())
    resp.headers['Cache-Control'] = 'max-age=60'
    return resp
```

브라우저/CDN/리버스 프록시가 60초 동안 같은 응답을 캐시합니다. 운영에서 가장 강력한 성능 도구가 헤더 한 줄입니다.

### 5단계: HTTPS 검증

```bash
curl -v https://expired.badssl.com/   # 만료 인증서 → curl이 차단
curl -v https://self-signed.badssl.com/   # self-signed → 차단
```

브라우저와 curl은 인증서 체인을 검증해 위장된 서버를 막습니다. 6편(TLS)에서 안쪽을 봅니다.

## 이 코드에서 주목할 점

- 요청도 응답도 결국 텍스트 메시지(HTTP/2/3에서는 바이너리 프레임이지만 의미는 동일)
- 메서드는 의미 있는 동사: GET은 읽기 전용, POST는 생성
- 상태 코드는 클라이언트와 캐시·재시도가 의지하는 신호
- 캐시 헤더 하나가 backend 부하를 절반으로 줄이기도 함

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| GET으로 데이터를 변경 | 프록시·재시도가 의도치 않게 변경 | 변경은 POST/PUT/PATCH/DELETE |
| 모든 오류를 200으로 회신 | 모니터링·재시도 정책 깨짐 | 적절한 4xx/5xx 사용 |
| Content-Type을 안 줌 | 클라이언트가 파싱 실패 | `application/json` 등 명시 |
| HTTPS 인증서 검증 끄기 | MITM 위험 | 운영에서 절대 disable 금지 |
| 큰 응답을 매번 풀로 전송 | 대역폭/지연 폭증 | gzip/br 압축, ETag/Last-Modified 활용 |

## 실무에서는 이렇게 쓰입니다

- REST API: 자원 + 메서드 조합으로 CRUD
- GraphQL/gRPC: HTTP/2 위에서 동작
- CDN: Cache-Control, ETag로 edge 캐시
- 인증: Authorization 헤더(Bearer 토큰, 쿠키)
- 모니터링: 5xx 비율, p99 응답 시간이 가장 핵심 지표

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 API를 설계할 때 메서드, 상태 코드, 헤더, 본문 네 가지를 동시에 봅니다. "이건 200이지만 errors 배열로 실패를 알린다"는 식의 설계는 클라이언트와 캐시·재시도 시스템을 모두 망가뜨립니다. HTTP가 정의한 의미를 따라야 외부 도구가 제대로 동작합니다.

또한 시니어는 HTTP/1.1에서 끝난 사고방식을 가지지 않습니다. HTTP/2의 multiplexing, HTTP/3의 0-RTT, head-of-line blocking 같은 개념이 실제 사용자 지연에 어떻게 영향을 주는지 이해하고, 신기능을 적용할 때의 리스크/이득을 계산합니다.

## 체크리스트

- [ ] HTTP 메시지의 4부분(시작줄/헤더/빈 줄/본문)을 안다
- [ ] 자주 쓰는 메서드와 상태 코드의 의미를 안다
- [ ] Content-Type, Cache-Control을 적절히 설정한다
- [ ] HTTPS가 보장하는 3가지(기밀성, 무결성, 신원)를 안다
- [ ] HTTP/1.1, /2, /3의 차이를 한 줄로 말할 수 있다

## 연습 문제

1. 좋아하는 사이트에 `curl -v`를 돌려 요청과 응답 헤더를 캡처하고, 의미를 정리하세요.

2. 위 Flask 서버를 확장해 ETag 기반 캐시(`If-None-Match` → 304)를 구현하세요.

3. "왜 모든 사이트가 HTTPS인가?"를 위협 모델 관점에서 한 문단으로 답하세요.

## 정리 및 다음 단계

HTTP는 텍스트 메시지의 약속이고, REST는 그 약속을 자원 단위로 정리한 스타일입니다. HTTPS는 그 위에 TLS로 보안 보장을 더한 것입니다. 메서드·상태 코드·헤더만 잘 다뤄도 시스템 품질이 한 단계 올라갑니다.

다음 글에서는 그 "S"가 어떻게 만들어지는지 — TLS 기초로 들어갑니다.

<!-- toc:begin -->
- [네트워크란 무엇인가?](./01-what-is-a-network.md)
- [IP와 subnet](./02-ip-and-subnet.md)
- [TCP와 UDP](./03-tcp-and-udp.md)
- [DNS](./04-dns.md)
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
