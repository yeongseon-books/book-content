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

## 먼저 던지는 질문

- HTTP 메시지는 어떤 모양으로 구성될까요?
- 메서드와 상태 코드는 왜 의미를 정확히 지켜야 할까요?
- `Content-Type`, `Cache-Control`, `Authorization` 같은 헤더는 왜 중요할까요?

## 큰 그림

![Computer Networks 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/05/05-01-concept-at-a-glance.ko.png)

*Computer Networks 101 5장 흐름 개요*

## 왜 중요한가

HTTP는 백엔드, 프론트엔드, 모바일, 데이터 서비스, ML 서빙까지 거의 모든 시스템의 공통 언어입니다. 메서드와 상태 코드를 잘못 쓰면 캐시, 재시도, 오류 처리 정책이 조용히 망가집니다. HTTPS가 기본값이 된 시대에도 왜 필요한지 설명하지 못하면 인증서 만료, mixed content, HSTS 같은 사고가 늘 낯설게 느껴집니다.

> HTTP는 약속된 메시지 형식이고, REST는 그 약속을 자원 중심으로 정리하는 스타일입니다.

## 핵심 그림

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

## 심화 실습: 패킷 캡처 · 헤더 해석 · 소켓 동작 검증

네트워크 문제를 줄이려면 추상 계층 설명만으로는 부족합니다. 패킷 단위 관찰과 애플리케이션 소켓 로그를 연결해야 원인 구분이 가능합니다. 핵심은 "어느 계층에서 실패했는가"를 증거 기반으로 좁히는 것입니다.

### tcpdump로 최소 증거를 확보하기

```bash
sudo tcpdump -i any -nn "tcp port 443" -c 20
```

이 명령으로 먼저 확인할 항목은 세 가지입니다.
- SYN이 나가고 SYN-ACK가 돌아오는가
- 재전송(retransmission)이 반복되는가
- RST 패킷이 어느 쪽에서 발생하는가

연결 실패를 애플리케이션 오류로 단정하기 전에, 3-way handshake가 실제로 성립했는지 먼저 확인해야 합니다.

### IPv4/TCP 헤더를 바이트 단위로 해석하기

```text
IPv4 Header (20B 기본)
- Version/IHL
- Total Length
- Identification
- Flags/Fragment Offset
- TTL
- Protocol (6=TCP, 17=UDP)
- Header Checksum
- Source IP / Destination IP

TCP Header (20B 기본)
- Source Port / Destination Port
- Sequence Number
- Acknowledgment Number
- Data Offset
- Flags (SYN, ACK, FIN, RST, PSH)
- Window Size
- Checksum
- Urgent Pointer
```

예를 들어 SYN 패킷에서 `flags=SYN`, `ack=0`이고, 응답에서 `flags=SYN,ACK`와 함께 `ack=client_seq+1`이 오면 handshake 2단계가 정상입니다. 이 규칙만 알아도 다수의 연결 이슈를 빠르게 분류할 수 있습니다.

### Python 소켓으로 타임아웃과 재시도 경계 분리

```python
import socket

def fetch_banner(host: str, port: int, timeout: float = 2.0) -> bytes:
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(b"HEAD / HTTP/1.1\r\nHost: example.com\r\n\r\n")
        return sock.recv(512)

try:
    data = fetch_banner("93.184.216.34", 80)
    print(data.decode(errors="replace"))
except socket.timeout:
    print("timeout: 네트워크 지연 또는 서버 응답 지연")
except OSError as e:
    print(f"os error: {e}")
```

포인트는 connect timeout과 read timeout을 구분하는 것입니다. connect 단계 실패는 라우팅/방화벽/리슨 상태 문제 가능성이 크고, read 단계 실패는 애플리케이션 지연이나 서버 과부하 가능성이 큽니다.

### UDP 손실과 순서 역전 관찰 예시

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1.0)

for i in range(1, 11):
    payload = f"seq={i}".encode()
    sock.sendto(payload, ("127.0.0.1", 9999))
```

UDP는 전달 보장과 순서 보장을 제공하지 않습니다. 따라서 실시간 시스템에서는 애플리케이션 레벨에서 `sequence`, `timestamp`, `dedup` 정책을 설계해야 합니다. 이 지점이 TCP와 UDP 선택의 핵심입니다.

### TLS 핸드셰이크를 계층별로 읽기

HTTPS 문제를 볼 때는 다음 흐름으로 분리하면 진단 속도가 올라갑니다.
1. TCP 연결 성립 여부
2. ClientHello/ServerHello 교환 여부
3. 인증서 체인 검증 성공 여부
4. 애플리케이션 데이터 송수신 여부

즉 "HTTPS 실패"라는 한 문장을 TCP, TLS, HTTP 단계로 쪼개는 습관이 필요합니다. 같은 502/504라도 실제 원인은 완전히 다를 수 있습니다.

### 패킷 캡처와 애플리케이션 로그를 합치는 방법

운영에서는 다음 필드를 공통 키로 맞추면 추적성이 좋아집니다.
- `src_ip`, `src_port`, `dst_ip`, `dst_port`
- `timestamp`(밀리초 단위)
- `request_id` 또는 `trace_id`

이 키로 묶으면 "애플리케이션에서는 timeout, 패킷에서는 SYN 재전송" 같은 상관관계를 바로 찾을 수 있습니다. 결과적으로 네트워크 팀과 애플리케이션 팀이 같은 사실 기반으로 협업할 수 있습니다.

### 점검 체크리스트

- 연결 실패 시 handshake 3단계를 캡처로 확인했는가
- TCP/UDP 선택 이유를 지연, 손실, 순서 보장 관점으로 설명할 수 있는가
- 프로토콜 헤더의 핵심 필드를 보고 상태를 해석할 수 있는가
- 소켓 timeout을 connect/read로 분리해 로깅했는가

이 기준을 적용하면 네트워크 문제는 "감"이 아니라 재현 가능한 관찰 데이터로 다뤄집니다.

### 운영 로그와 패킷 증거를 함께 읽는 연습

문서만 보면 개념은 이해되지만, 운영 문제는 보통 "같은 시간대의 서로 다른 증거"를 묶어야 해결됩니다. 다음과 같이 최소 공통 포맷을 맞추면 진단 속도가 크게 올라갑니다.

```text
2026-05-21T10:01:03.120Z src=10.0.1.24:51432 dst=10.0.2.11:443 event=connect_start req_id=ab12
2026-05-21T10:01:03.341Z src=10.0.1.24:51432 dst=10.0.2.11:443 event=connect_timeout req_id=ab12
2026-05-21T10:01:03.350Z pcap src=10.0.1.24:51432 dst=10.0.2.11:443 flag=SYN retransmit=3
```

위처럼 애플리케이션 로그와 캡처 로그의 키를 맞추면, "코드 버그"와 "네트워크 경로 문제"를 같은 화면에서 분리할 수 있습니다. 특히 재전송 카운트, RTT 변화, RST 발생 위치를 함께 보면 문제 책임 경계가 명확해집니다.

### 최소 재현 시나리오 템플릿

1. 동일 요청을 10회 반복해 성공/실패 비율 기록
2. 실패 시점의 소켓 예외 타입(`timeout`, `connection reset`) 집계
3. 같은 시점의 패킷에서 SYN, ACK, RST, FIN 비율 확인

이 과정을 습관화하면 "가끔 느리다" 같은 모호한 제보를 수치화된 진단 리포트로 바꿀 수 있습니다.

## 처음 질문으로 돌아가기

- **HTTP 메시지는 어떤 모양으로 구성될까요?**
  - 본문의 기준은 HTTP와 HTTPS를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **메서드와 상태 코드는 왜 의미를 정확히 지켜야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`Content-Type`, `Cache-Control`, `Authorization` 같은 헤더는 왜 중요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Computer Science, 네트워크, HTTP, HTTPS, REST, 헤더
