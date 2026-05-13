---
series: computer-networks-101
episode: 5
title: HTTP와 HTTPS
status: publish-ready
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
seo_description: HTTP 메시지 구조와 HTTPS가 더하는 보안 의미를 설명합니다.
last_reviewed: '2026-05-12'
---

# HTTP와 HTTPS

이 글은 Computer Networks 101 시리즈의 5번째 글입니다.

## 이 글에서 다룰 문제

- HTTP 메시지는 어떤 모양으로 구성될까요?
- 메서드와 상태 코드는 왜 의미를 정확히 지켜야 할까요?
- `Content-Type`, `Cache-Control`, `Authorization` 같은 헤더는 왜 중요할까요?
- HTTPS의 S는 구체적으로 무엇을 더해 줄까요?

> HTTP는 텍스트 기반 요청/응답 프로토콜입니다. 메서드, 경로, 헤더, 본문 네 요소만 이해해도 대부분의 웹 API와 웹사이트를 읽을 수 있습니다. HTTPS는 그 아래에 TLS를 넣어 엿보기, 변조, 위장을 막습니다. 오늘은 TLS의 전체를 열기보다, HTTP 위에 드리운 그림자를 먼저 봅니다.

## 왜 중요한가

HTTP는 백엔드, 프론트엔드, 모바일, 데이터 서비스, ML 서빙까지 거의 모든 시스템의 공통 언어입니다. 메서드와 상태 코드를 잘못 쓰면 캐시, 재시도, 오류 처리 정책이 조용히 망가집니다. HTTPS가 기본값이 된 시대에도 왜 필요한지 설명하지 못하면 인증서 만료, mixed content, HSTS 같은 사고가 늘 낯설게 느껴집니다.

> HTTP는 약속된 메시지 형식이고, REST는 그 약속을 자원 중심으로 정리하는 스타일입니다.

## 핵심 그림

```text
Request
GET /users/42 HTTP/1.1
Host: api.example.com
Accept: application/json
Authorization: Bearer ...

Response
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=60

{"id": 42, "name": "..."}
```

요청과 응답은 모두 "시작줄 + 헤더 + 빈 줄 + 본문"이라는 같은 구조를 가집니다.

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 메서드 | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |
| 상태 코드 | 1xx 정보, 2xx 성공, 3xx 리다이렉트, 4xx 클라이언트 오류, 5xx 서버 오류 |
| 헤더 | 타입, 길이, 캐시, 인증 같은 메타데이터 |
| 본문 | JSON, HTML, 바이너리 등 실제 데이터 |
| TLS | HTTPS의 S를 만드는 암호화 계층 |

## Before / After

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
# > GET / HTTP/2
# > Host: example.com
# < HTTP/2 200
# < content-type: text/html; charset=UTF-8
```

`-v` 옵션은 헤더뿐 아니라 TLS 핸드셰이크 과정도 함께 보여 줍니다.

### 2단계: Python 클라이언트 만들기

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

### 4단계: 캐시 헤더 실험하기

```python
@app.get('/now')
def now():
    from datetime import datetime
    resp = jsonify(now=datetime.utcnow().isoformat())
    resp.headers['Cache-Control'] = 'max-age=60'
    return resp
```

이 한 줄 때문에 브라우저, CDN, 리버스 프록시는 60초 동안 같은 응답을 재사용합니다. 운영에서 성능을 가장 크게 움직이는 도구가 헤더 한 줄인 경우가 많습니다.

### 5단계: HTTPS 검증 보기

```bash
curl -v https://expired.badssl.com/   # expired cert → curl blocks
curl -v https://self-signed.badssl.com/   # self-signed → blocked
```

브라우저와 `curl`은 인증서 체인을 검증해 위장된 서버를 막습니다. 다음 글에서 TLS 내부를 자세히 엽니다.

## 이 코드에서 먼저 볼 점

- 요청과 응답은 결국 메시지입니다. HTTP/2와 HTTP/3는 바이너리 프레임을 쓰지만 의미는 같습니다.
- 메서드는 의미를 가진 동사입니다. GET은 읽기, POST는 생성이라는 약속을 깨면 주변 도구가 함께 망가집니다.
- 상태 코드는 클라이언트, 캐시, 재시도 로직이 믿고 사용하는 신호입니다.
- 캐시 헤더 하나로 백엔드 부하를 크게 줄일 수 있습니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| GET으로 데이터를 변경 | 프록시와 재시도가 의도치 않은 변화를 일으킴 | 변경은 POST / PUT / PATCH / DELETE로 보낸다 |
| 모든 오류를 200으로 반환 | 모니터링과 재시도 정책이 깨짐 | 적절한 4xx / 5xx를 사용한다 |
| `Content-Type`을 생략 | 클라이언트 파싱 실패 | `application/json`처럼 명시한다 |
| HTTPS 검증을 끔 | MITM 위험 노출 | 운영에서는 절대 끄지 않는다 |
| 큰 응답을 매번 비압축으로 전송 | 대역폭과 지연 증가 | gzip / br, ETag, Last-Modified를 활용한다 |

## 실무에서는 이렇게 보입니다

- REST API는 자원과 메서드 조합으로 CRUD를 표현합니다.
- GraphQL과 gRPC는 HTTP/2 위에 올라갑니다.
- CDN은 `Cache-Control`과 ETag를 활용해 edge 캐시를 구성합니다.
- 인증은 `Authorization` 헤더나 쿠키로 전달됩니다.
- 모니터링에서는 5xx 비율과 p99 지연 시간이 핵심 지표가 됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 API를 설계할 때 메서드, 상태 코드, 헤더, 본문을 따로 보지 않고 함께 봅니다. 예를 들어 실패를 `errors` 필드에 담아 200으로 보내는 설계는 클라이언트뿐 아니라 캐시와 재시도 정책까지 함께 무너뜨립니다. HTTP 의미 체계를 지켜야 외부 도구도 함께 작동합니다.

또한 HTTP/1.1에서 생각을 멈추지 않습니다. HTTP/2의 멀티플렉싱, HTTP/3의 0-RTT와 전송 특성이 체감 지연을 어떻게 바꾸는지 이해하고, 새로운 기능을 도입할 가치와 위험을 함께 판단합니다.

## 체크리스트

- [ ] HTTP 메시지의 네 부분을 설명할 수 있다
- [ ] 자주 쓰는 메서드와 상태 코드의 의미를 안다
- [ ] `Content-Type`과 `Cache-Control`을 올바르게 설정할 수 있다
- [ ] HTTPS의 세 가지 보장(기밀성, 무결성, 신원)을 안다
- [ ] HTTP/1.1, /2, /3를 한 줄씩 비교할 수 있다

## 연습 문제

1. 좋아하는 사이트에 `curl -v`를 실행하고 요청/응답 헤더를 캡처한 뒤 각 헤더의 의미를 설명해 보세요.
2. 위 Flask 서버에 ETag 기반 캐시(`If-None-Match` → `304`)를 추가해 보세요.
3. 위협 모델 관점에서 "왜 이제 거의 모든 사이트가 HTTPS를 쓰는가"를 한 단락으로 설명해 보세요.

## 정리와 다음 글

HTTP는 메시지 형식에 대한 약속이고, REST는 그 약속을 자원 단위로 조직하는 스타일입니다. HTTPS는 그 위에 TLS의 보안 보장을 더합니다. 메서드, 상태 코드, 헤더를 정확히 다루는 것만으로도 시스템 품질은 바로 올라갑니다.

다음 글에서는 HTTPS의 S를 여는 열쇠, TLS 기초를 다룹니다.

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

Tags: Computer Science, 네트워크, HTTP, HTTPS, REST, 헤더
