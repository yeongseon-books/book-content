---
title: "바이브코딩을 위한 Computer Science 기초 (7/10): 네트워크"
series: computer-science-101
episode: 7
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - ComputerScience
  - Network
  - TCP
  - HTTP
  - DNS
---

# 바이브코딩을 위한 Computer Science 기초 (7/10): 네트워크

이 글은 "바이브코딩을 위한 Computer Science 기초" 시리즈의 7번째 글입니다.

---

바이브코딩에서 AI는 HTTP 클라이언트 코드와 API 연동을 빠르게 만들어 줍니다. 하지만 API 응답이 느릴 때, 인증서 오류가 날 때, 이상한 timeout이 발생할 때 — 모두 네트워크 계층 어딘가에 원인이 있습니다. 계층 구조를 모르면 "어느 층에서 문제가 생겼는가"를 묻지도 못합니다.

브라우저 주소창에 도메인을 입력하고 화면에 응답이 뜨기까지는 하나의 마법 같은 요청이 아니라, 층별로 역할이 나뉜 프로토콜들이 차례로 일을 나눠 갖는 과정입니다. IP가 경로를 정하고, TCP가 신뢰성을 보장하고, HTTP가 의미를 전달합니다.

AI가 만들어 준 네트워크 코드에서 timeout 설정, retry 전략, TLS 인증서 검증 여부를 확인해야 합니다. 네트워크 계층 구조를 이해하면 문제를 계층별로 분리해서 빠르게 좁힐 수 있습니다.

TCP/IP 계층, HTTP 요청과 응답, DNS 이름 해석을 하나의 흐름으로 정리합니다.

> **핵심 인사이트:** 네트워크는 약속의 계층 구조입니다. 각 계층은 아래 계층을 신뢰하면서 자기 역할에만 집중합니다. 문제가 생기면 계층별로 분리해서 진단합니다.

## 이 글에서 다룰 문제

- IP, TCP, HTTP, DNS는 각각 어느 층에서 어떤 역할을 맡을까요?
- HTTP 요청과 응답은 어떤 구조로 오갈까요?
- DNS는 도메인 이름을 IP로 어떻게 바꿀까요?
- timeout과 retry는 어떤 계층에서 설계해야 할까요?
- AI가 만든 네트워크 코드에서 확인해야 할 것은 무엇인가요?

## 네트워크 핵심 패턴

```python
import socket
import http.client
import urllib.request

# 소켓 기반 TCP 연결
with socket.create_connection(("example.com", 80), timeout=5) as s:
    s.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
    response = s.recv(4096)

# HTTP 클라이언트 (timeout + retry 기본 패턴)
import urllib3
from urllib3.util.retry import Retry

http = urllib3.PoolManager()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503])
adapter = urllib3.HTTPAdapter(max_retries=retry)

# DNS 조회
import socket
ip = socket.gethostbyname("example.com")  # DNS A 레코드 조회
print(f"example.com → {ip}")
```

```text
TCP/IP 4계층:
응용 계층   (HTTP, SMTP, DNS)
전송 계층   (TCP - 신뢰성, UDP - 속도)
인터넷 계층 (IP - 경로 지정)
링크 계층   (이더넷, WiFi)
```

## 변경 전후 비교

**Before: 네트워크 계층 이해 없이 코딩**
```text
- timeout 없는 HTTP 요청 (무한 대기 가능)
- retry 없이 단발성 호출 (일시적 오류에 실패)
- TLS 인증서 검증 비활성화 (보안 취약)
- "느리다"는 증상에서 계층 특정 불가
```

**After: 계층 이해 기반 코딩**
```text
- 연결 timeout + 읽기 timeout 분리 설정
- 지수 백오프 retry (5xx 오류에 자동 재시도)
- TLS 인증서 검증 활성화 기본
- 계층별 진단 (DNS → TCP → HTTP 순서)
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| timeout 없는 HTTP 요청 | 서버 응답 없을 때 무한 대기 | 연결/읽기 timeout 분리 설정 |
| TLS 검증 비활성화 | MITM 공격에 취약 | 검증 항상 활성화, 자체 서명 인증서는 CA 추가 |
| retry 없이 단발성 호출 | 일시적 네트워크 오류에 실패 | 지수 백오프 retry 적용 |
| DNS 결과 캐싱 안 함 | 매 요청마다 DNS 조회 오버헤드 | 연결 풀 또는 DNS TTL 활용 |
| 계층 구분 없이 "네트워크 오류" | 원인 진단 불가 | DNS→TCP→HTTP 순서로 분리 진단 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"외부 API를 호출하는 Python 코드를 만들어줘.
연결 timeout 5초, 읽기 timeout 30초,
5xx 오류에 3회 지수 백오프 retry,
TLS 인증서 검증 활성화까지 포함해야 해"

# 네트워크 문제 진단 순서:
# 1. DNS 조회 확인: nslookup / dig example.com
# 2. TCP 연결 확인: telnet example.com 80 또는 nc -zv
# 3. HTTP 요청 확인: curl -v https://example.com
# 4. 각 단계별 timeout 확인
```

## 운영 체크리스트

- [ ] 모든 외부 HTTP 호출에 timeout이 설정되어 있다
- [ ] retry 전략이 지수 백오프로 구현되어 있다
- [ ] TLS 인증서 검증이 활성화되어 있다
- [ ] 연결 풀을 재사용해 DNS 오버헤드를 줄인다
- [ ] 네트워크 오류 로그에 계층 정보가 포함된다

## 처음 질문으로 돌아가기

- **TCP와 UDP의 차이는?** TCP는 3-way handshake로 연결을 맺고 순서와 신뢰성을 보장합니다. UDP는 연결 없이 빠르게 보내지만 손실 허용 (영상 스트리밍, DNS 등에 사용).
- **DNS는 어떻게 동작하나요?** 로컬 캐시 → 리졸버 → 루트 네임서버 → TLD → 권한 네임서버 순으로 재귀 조회합니다.
- **HTTP timeout을 연결과 읽기로 나누는 이유는?** 연결 timeout은 TCP 핸드셰이크 시간, 읽기 timeout은 서버 처리 시간입니다. 둘을 분리해야 각각의 문제를 구분할 수 있습니다.

## 정리

바이브코딩에서 AI가 만들어 준 네트워크 코드에서 timeout 분리, retry 전략, TLS 검증 활성화를 반드시 확인하세요. 네트워크 문제는 DNS부터 HTTP까지 계층별로 순서대로 좁히는 습관이 디버깅 시간을 크게 줄입니다. 다음 글에서는 데이터베이스를 다룹니다.

## 참고 자료

- [MDN — HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [Computer Networks: A Top-Down Approach](https://gaia.cs.umass.edu/kurose_ross/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Computer Science 기초 (1/10): 컴퓨터 과학이란 무엇인가?
- 바이브코딩을 위한 Computer Science 기초 (2/10): 계산과 프로그램
- 바이브코딩을 위한 Computer Science 기초 (3/10): 데이터 표현
- 바이브코딩을 위한 Computer Science 기초 (4/10): 알고리즘과 복잡도
- 바이브코딩을 위한 Computer Science 기초 (5/10): 컴퓨터 구조
- 바이브코딩을 위한 Computer Science 기초 (6/10): 운영체제
- **바이브코딩을 위한 Computer Science 기초 (7/10): 네트워크 (현재 글)**
- 바이브코딩을 위한 Computer Science 기초 (8/10): 데이터베이스
- 바이브코딩을 위한 Computer Science 기초 (9/10): 소프트웨어 엔지니어링
- 바이브코딩을 위한 Computer Science 기초 (10/10): AI와 데이터사이언스까지의 연결
<!-- toc:end -->

Tags: 바이브코딩, ComputerScience, Network, TCP, HTTP, DNS
