---
series: computer-networks-101
episode: 10
title: "Computer Networks 101 (10/10): 네트워크 문제 디버깅"
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
  - 디버깅
  - tcpdump
  - 트러블슈팅
  - 진단
seo_description: 계층별 진단 도구를 활용하여 네트워크 장애 원인을 체계적으로 좁혀 가는 실전 디버깅 절차와 주요 도구 사용법을 상세히 다룹니다.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (10/10): 네트워크 문제 디버깅

이 글은 Computer Networks 101 시리즈의 마지막 글입니다.


![Computer Networks 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/10/10-01-concept-at-a-glance.ko.png)
*Computer Networks 101 10장 흐름 개요*

## 먼저 던지는 질문

- 네트워크 문제를 계층별로 어떻게 좁혀 가야 할까요?
- `ping`, `dig`, `curl`, `ss`, `tcpdump`는 각각 무엇을 말해 줄까요?
- timeout, reset, DNS 실패는 어떤 모양으로 구분할 수 있을까요?

## 왜 중요한가

장애가 나면 사람은 먼저 "방금 뭘 바꿨지"를 떠올립니다. 그 질문은 필요하지만 충분하지 않습니다. 경로가 어디서 끊겼는지 모르면 코드 변경도 결국 추측이 됩니다. "여기까지는 정상"을 한 층씩 확정하는 습관이 있어야 새벽 장애에서도 침착하게 원인을 좁힐 수 있습니다.

> 디버깅의 핵심은 고장 난 곳을 바로 찾는 것이 아니라, 멀쩡한 층을 하나씩 확정해 가는 일입니다.

## 핵심 그림

```text
┌─────────────────────────────────────────────────────┐
│                   문제 발생                           │
└───────────────────────┬─────────────────────────────┘
                        │
           ┌────────────▼────────────┐
           │ 1. 링크/경로 확인        │  ping, traceroute, mtr
           │    호스트가 살아 있나?    │
           └────────────┬────────────┘
                        │ ✓ 정상
           ┌────────────▼────────────┐
           │ 2. DNS 확인              │  dig, nslookup
           │    이름이 IP로 변환되나?  │
           └────────────┬────────────┘
                        │ ✓ 정상
           ┌────────────▼────────────┐
           │ 3. TCP 연결 확인         │  nc -vz, ss, netstat
           │    포트가 열려 있나?      │
           └────────────┬────────────┘
                        │ ✓ 정상
           ┌────────────▼────────────┐
           │ 4. TLS 확인              │  openssl s_client
           │    인증서가 유효한가?     │
           └────────────┬────────────┘
                        │ ✓ 정상
           ┌────────────▼────────────┐
           │ 5. HTTP/애플리케이션 확인 │  curl -v, 로그
           │    응답이 정상인가?       │
           └─────────────────────────┘
```

한 단계씩 정상으로 판정할 때마다 가능한 원인 후보가 크게 줄어듭니다.

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| ICMP | `ping`, `traceroute`가 사용하는 진단용 IP 프로토콜 |
| RTT | 패킷이 목적지까지 갔다가 돌아오는 데 걸리는 시간 |
| Connection refused | 호스트는 살아 있으나 해당 포트에서 듣는 프로세스가 없는 상태 |
| RST | TCP가 즉시 연결을 끊겠다고 알리는 신호 |
| Capture filter | `tcpdump`가 필요한 패킷만 잡도록 주는 BPF 표현식 |
| Display filter | Wireshark에서 캡처된 패킷 중 보고 싶은 것만 필터링하는 표현식 |
| Retransmission | 응답이 없어 같은 패킷을 다시 보내는 것 — 경로 손실의 증거 |

## Before/After

**Before — 추측 기반 디버깅**

```text
service is down
→ 최근 커밋 확인
→ 의심 라이브러리 재설치
→ 서버 재시작
→ 여전히 안 됨
→ 한 시간 경과
```

어디서 끊겼는지 모른 채 손 가는 대로 만지면, 운 좋을 때만 해결됩니다.

**After — 계층별로 좁혀 가기**

```bash
# 1) Is the host alive? (link / path)
ping -c 3 api.example.com

# 2) Does the name resolve? (DNS)
dig +short api.example.com

# 3) Is the port open? (TCP)
nc -vz api.example.com 443

# 4) Does the TLS handshake complete? (TLS)
openssl s_client -connect api.example.com:443 -servername api.example.com </dev/null

# 5) What does HTTP return? (HTTP)
curl -v https://api.example.com/health
```

각 줄은 다음 가설을 지우거나 남깁니다. 대부분의 경우 다섯 줄이면 층이 갈립니다.

## 5단계로 한 요청을 끝까지 따라가기

### 1단계 — 링크와 경로 확인

```bash
ping -c 3 api.example.com
# PING api.example.com (1.2.3.4): 56 data bytes
# 64 bytes from 1.2.3.4: icmp_seq=0 ttl=55 time=12.3 ms
# 64 bytes from 1.2.3.4: icmp_seq=1 ttl=55 time=11.8 ms
# 64 bytes from 1.2.3.4: icmp_seq=2 ttl=55 time=12.1 ms

traceroute -n api.example.com   # or mtr -n api.example.com
```

손실이 100%면 호스트가 죽었거나 ICMP가 차단됐을 가능성이 큽니다. 일부 손실이면 경로 어딘가가 혼잡할 수 있습니다. 다만 ICMP는 차단돼도 서비스는 정상일 수 있으니 `ping` 실패만으로 단정하면 안 됩니다.

`mtr`은 `traceroute`의 연속 측정 버전입니다. 각 홉의 패킷 손실률과 지터를 실시간으로 보여줍니다.

```bash
mtr -n --report -c 50 api.example.com
# HOST                   Loss%   Snt   Last   Avg  Best  Wrst StDev
# 1. 192.168.0.1          0.0%    50    1.2   1.1   0.8   2.1   0.3
# 2. 10.200.0.1           0.0%    50    5.4   5.2   4.8   7.1   0.5
# 3. 72.14.215.85         4.0%    50    9.0   8.8   8.2  15.3   1.2
# 4. 1.2.3.4              0.0%    50   12.3  12.1  11.8  14.2   0.4
```

hop 3에서만 4% 손실이 보이면 해당 구간에 혼잡이 있을 수 있습니다. 하지만 최종 목적지(hop 4)가 0%이면 서비스에는 영향이 없을 가능성이 높습니다.

### 2단계 — DNS 확인

```bash
dig +short api.example.com
# 1.2.3.4

# 응답이 없으면 상세 추적
dig +trace api.example.com

# 특정 네임서버로 직접 질의
dig @8.8.8.8 api.example.com

# TTL 확인 (캐시 문제 판단용)
dig api.example.com | grep -A1 "ANSWER SECTION"
# api.example.com.  300  IN  A  1.2.3.4
```

여기서 결과가 없으면 더 아래 층으로 내려갈 필요가 없습니다. 애플리케이션이 아니라 resolver 설정이나 authoritative 레코드를 먼저 봐야 합니다.

DNS 문제가 의심될 때 확인 순서:

| 확인 항목 | 명령 | 의미 |
| --- | --- | --- |
| 로컬 resolver | `cat /etc/resolv.conf` | 어떤 DNS 서버를 쓰고 있는지 |
| resolver 응답 여부 | `dig @$(grep nameserver /etc/resolv.conf \| head -1 \| awk '{print $2}') api.example.com` | 내 resolver가 살아 있는지 |
| 공용 DNS 비교 | `dig @8.8.8.8 api.example.com` | 로컬 문제인지 글로벌 문제인지 |
| 권한 서버 직접 질의 | `dig +trace api.example.com` | delegation chain이 정상인지 |

### 3단계 — TCP 연결 확인

```bash
nc -vz api.example.com 443
# Connection to api.example.com port 443 [tcp/https] succeeded!
```

세 가지 결과를 구분해야 합니다.

| 결과 | 의미 | 다음 행동 |
| --- | --- | --- |
| succeeded | 포트 열림, SYN/SYN-ACK 정상 | 4단계(TLS)로 진행 |
| Connection refused | 호스트 살아 있음, 프로세스 없음 | 서비스 상태 확인 (`ss -tlnp`) |
| timeout | SYN에 응답 없음 | 방화벽, 보안그룹, ACL 확인 |

서버 쪽에서는 실제로 어떤 포트가 열려 있는지도 함께 확인합니다.

```bash
ss -tlnp | grep :443
# LISTEN 0 511 0.0.0.0:443  users:(("nginx",pid=1234,fd=6))

# 연결 상태 통계
ss -s
# Total: 1234
# TCP:   567 (estab 432, closed 12, orphaned 0, timewait 89)
```

### 4단계 — TLS 핸드셰이크 확인

```bash
openssl s_client -connect api.example.com:443 \
                 -servername api.example.com </dev/null 2>&1 | head -20
# CONNECTED(00000003)
# depth=2 C = US, O = DigiCert Inc, CN = DigiCert Global Root G2
# verify return:1
# depth=1 C = US, O = DigiCert Inc, CN = DigiCert SHA2 Extended Validation Server CA
# verify return:1
# depth=0 businessCategory = ..., CN = api.example.com
# verify return:1
# ---
# Certificate chain
#  0 s:CN = api.example.com
#    i:CN = DigiCert SHA2 Extended Validation Server CA
#  1 s:CN = DigiCert SHA2 Extended Validation Server CA
#    i:CN = DigiCert Global Root G2
```

여기서 꼭 봐야 할 것:
- `-servername` 옵션(SNI) — 없으면 잘못된 인증서를 받을 수 있습니다.
- `Verify return code: 0 (ok)` — 이것이 나오면 TLS 층은 정상입니다.
- 인증서 만료일: `openssl s_client ... | openssl x509 -noout -dates`

```bash
# 인증서 만료일만 빠르게 확인
echo | openssl s_client -connect api.example.com:443 -servername api.example.com 2>/dev/null \
     | openssl x509 -noout -enddate
# notAfter=Dec 15 23:59:59 2026 GMT
```

### 5단계 — HTTP 응답을 직접 보기

```bash
curl -v https://api.example.com/health
# * Trying 1.2.3.4:443...
# * Connected to api.example.com (1.2.3.4) port 443
# * SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384
# > GET /health HTTP/2
# > Host: api.example.com
# >
# < HTTP/2 200
# < content-type: application/json
# < x-request-id: abc123
# {"status":"ok","db":"connected","cache":"connected"}
```

`-v`는 DNS, TCP 연결, TLS 협상, 요청 헤더, 응답 헤더를 한 번에 보여 줍니다. 여기서 4xx나 5xx가 나오면 더 이상 네트워크 문제가 아니라 애플리케이션 문제일 가능성이 큽니다.

유용한 curl 옵션:

```bash
# 타이밍 정보 출력
curl -w "\nDNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTLS: %{time_appconnect}s\nTotal: %{time_total}s\n" \
     -o /dev/null -s https://api.example.com/health
# DNS: 0.012s
# Connect: 0.025s
# TLS: 0.078s
# Total: 0.095s
```

이 출력으로 "어디서 시간이 오래 걸리는가"를 바로 알 수 있습니다. DNS가 느리면 resolver 문제, Connect가 느리면 네트워크 지연, TLS가 느리면 인증서 체인 문제, Total만 느리면 서버 처리 지연입니다.

## 6단계: 증상 모양으로 바로 층을 가늠하기

다섯 명령을 다 치기 전에, 출력 모양만으로도 다음 단계의 우선순위를 조정할 수 있습니다.

| 관찰한 증상 | 흔한 원인 층 | 바로 이어서 할 일 |
| --- | --- | --- |
| `Could not resolve host` | DNS | `dig +short`, `dig +trace` |
| `Connection refused` | TCP / 프로세스 | 서버에서 `ss -tlnp`로 listen 여부 확인 |
| `Operation timed out` | 방화벽 / 경로 | `traceroute`, 보안 그룹, ACL 확인 |
| `SSL certificate problem` | TLS | `openssl s_client -servername ...`로 인증서 체인 확인 |
| `HTTP/1.1 502` 또는 `503` | 애플리케이션/LB | `/health`, upstream 상태, 애플리케이션 로그 확인 |
| `Connection reset by peer` | 방화벽 또는 서버 거부 | `tcpdump`로 RST가 어디서 오는지 확인 |
| 응답은 오지만 매우 느림 | 서버 과부하 / DB 지연 | `curl -w` 타이밍, 서버 `top`, slow query log |

이 표의 목적은 정답을 외우는 데 있지 않습니다. **실패 메시지가 어느 층 언어로 쓰였는지 먼저 읽는 습관**을 만드는 데 있습니다.

## tcpdump 실전 사용법

`tcpdump`는 "패킷이 실제로 오고 가는가"를 확인하는 마지막 무기입니다.

```bash
# 기본: 특정 호스트의 HTTPS 트래픽만 캡처
sudo tcpdump -i eth0 -nn 'host api.example.com and tcp port 443' -c 50

# 파일로 저장 (Wireshark에서 분석)
sudo tcpdump -i eth0 -nn -s 0 'host api.example.com and tcp port 443' -w cap.pcap

# SYN 패킷만 보기 (새 연결 시도만)
sudo tcpdump -i eth0 -nn 'tcp[tcpflags] & tcp-syn != 0'

# RST 패킷만 보기 (강제 종료)
sudo tcpdump -i eth0 -nn 'tcp[tcpflags] & tcp-rst != 0'
```

tcpdump 출력 읽기:

```text
# 정상적인 3-way handshake
15:30:01.123 IP 192.168.0.10.54321 > 1.2.3.4.443: Flags [S], seq 1000
15:30:01.135 IP 1.2.3.4.443 > 192.168.0.10.54321: Flags [S.], seq 2000, ack 1001
15:30:01.135 IP 192.168.0.10.54321 > 1.2.3.4.443: Flags [.], ack 2001

# 연결 거부 (RST)
15:30:01.123 IP 192.168.0.10.54321 > 1.2.3.4.8080: Flags [S], seq 1000
15:30:01.135 IP 1.2.3.4.8080 > 192.168.0.10.54321: Flags [R.], ack 1001

# 타임아웃 (재전송 반복)
15:30:01.123 IP 192.168.0.10.54321 > 1.2.3.4.443: Flags [S], seq 1000
15:30:02.125 IP 192.168.0.10.54321 > 1.2.3.4.443: Flags [S], seq 1000  # retransmit
15:30:04.130 IP 192.168.0.10.54321 > 1.2.3.4.443: Flags [S], seq 1000  # retransmit
```

패턴 해석:

| 패턴 | 의미 |
| --- | --- |
| SYN → SYN-ACK → ACK | 정상 연결 |
| SYN → RST | 포트 닫힘 (Connection refused) |
| SYN → (재전송 반복) → 없음 | 방화벽이 조용히 드롭 (timeout) |
| 데이터 전송 중 RST | 중간 장비(방화벽, IDS)가 끊음 |
| FIN → FIN-ACK | 정상 종료 |

## Wireshark 필터 치트시트

`tcpdump`로 캡처한 `.pcap` 파일을 Wireshark에서 열 때 유용한 display filter:

| 목적 | 필터 |
| --- | --- |
| 특정 IP만 | `ip.addr == 1.2.3.4` |
| TCP 재전송만 | `tcp.analysis.retransmission` |
| HTTP 응답만 | `http.response` |
| 5xx 에러만 | `http.response.code >= 500` |
| TLS 핸드셰이크만 | `tls.handshake` |
| DNS 질의만 | `dns.flags.response == 0` |
| 특정 포트 | `tcp.port == 443` |
| RST만 | `tcp.flags.reset == 1` |
| 3초 이상 지연된 패킷 | `frame.time_delta > 3` |

## 이 코드에서 먼저 볼 점

- 각 도구는 서로 다른 가설을 제거합니다. `ping`은 링크, `dig`는 이름, `nc`는 포트, `openssl`은 인증서, `curl`은 애플리케이션 동작을 확인합니다.
- 중요한 일은 출력으로 "여기까지는 정상"을 확정하는 것입니다.
- 많은 클라우드 환경에서 ICMP는 차단됩니다. `ping` 실패가 곧 호스트 다운은 아닙니다.
- `curl -v` 한 줄이 1~5단계의 상당 부분을 같이 보여 준다는 점을 종종 놓칩니다.
- `curl -w`의 타이밍 정보는 병목 구간을 즉시 보여줍니다.

## 자주 하는 실수 5가지

1. **DNS를 건너뜁니다.** 코드 변경이 없는데 갑자기 안 되는 문제는 생각보다 자주 DNS입니다. TTL 만료 후 새 레코드가 잘못 나오거나, resolver 캐시가 오래된 IP를 물고 있을 수 있습니다.
2. **timeout과 refused를 같은 문제로 봅니다.** refused는 호스트가 살아 있다는 뜻이고, timeout은 보통 방화벽 문제입니다. 다음 조치가 완전히 달라집니다.
3. **`openssl s_client`에서 `-servername`을 빼먹습니다.** SNI가 없으면 잘못된 가상 호스트 인증서를 받아 가짜 오류를 추적하게 됩니다.
4. **가설 없이 `tcpdump`부터 켭니다.** 캡처는 강력하지만, 방향 없는 큰 파일이 되기 쉽습니다. 먼저 "SYN이 나가는지"처럼 구체적 질문을 정하고 필터를 걸어야 합니다.
5. **재시작을 해결이라고 기록합니다.** 재시작은 증상을 숨겼을 뿐일 수 있습니다. 무엇이 검증됐는지 남겨야 다음 사고에서 이깁니다.

## 실무에서는 이렇게 보입니다

장애 대응에서는 보통 두 사람이 병렬로 움직입니다. 한 사람은 외부에서 사용자 시점으로 다섯 단계를 실행하고, 다른 사람은 서버 안쪽에서 `ss`, 로그, `tcpdump`를 봅니다. 몇 분 간격으로 결과를 맞춰 보면 가설 공간이 빠르게 줄어듭니다.

실전 디버깅 런북 예시:

```text
[장애 탐지] 모니터링 알림 또는 사용자 제보
    │
    ├─ [즉시] 외부에서 curl -v 실행 → 어느 층에서 실패?
    │
    ├─ [1분 이내] 영향 범위 파악
    │   - 특정 엔드포인트만? 전체 서비스?
    │   - 특정 리전만? 글로벌?
    │   - 특정 클라이언트만? 모든 클라이언트?
    │
    ├─ [3분 이내] 층 확정
    │   - DNS 정상 → TCP 정상 → TLS 정상 → HTTP 5xx
    │   → "애플리케이션 문제" 확정
    │
    ├─ [5분 이내] 원인 후보 좁히기
    │   - 최근 배포? → rollback 준비
    │   - 외부 의존성? → 해당 서비스 상태 확인
    │   - 리소스 고갈? → CPU, 메모리, 디스크, 연결 수 확인
    │
    └─ [해결 후] 포스트모템 작성
        - 타임라인, 근본 원인, 재발 방지 조치
```

## 시니어 엔지니어는 이렇게 생각합니다

- 도구보다 먼저 가설을 적고, 도구로 그 가설을 지웁니다.
- 클라이언트와 서버 두 관점에서 동시에 디버깅합니다.
- "재시작하니 됐다"는 말을 믿지 않습니다. 다음 주 같은 증상이 반복될 것을 전제로 기록합니다.
- 새벽에 검색하지 않아도 되도록 다섯 개 명령 세트를 외워 둡니다.
- 사고가 끝나면 짧은 포스트모템이라도 남겨 다음 사람의 시간을 줄입니다.
- "이건 네트워크 문제가 아닙니다"라고 말할 때는 반드시 증거를 함께 제시합니다. "ping 정상, TCP 정상, TLS 정상, HTTP 502 → upstream 애플리케이션 로그를 봐야 합니다"처럼 한 문장으로 정리합니다.
- 장애 대응이 끝나면 "이 증상이 다시 오면?"이라는 질문에 답하는 런북 한 페이지를 남깁니다. 명령어, 예상 출력, 에스컬레이션 조건 세 블록이면 충분합니다.
- 모니터링 알림을 받았을 때 가장 먼저 확인하는 것은 "언제부터?"입니다. 시작 시점을 고정해야 변경 이력(배포, 설정, 인프라)과 대조할 수 있습니다.

### 디버깅 사고 흐름 요약

```text
1. 증상 수집  → 에러 메시지를 정확히 복사한다 (스크린샷 아님)
2. 층 식별    → 메시지가 어느 프로토콜 언어인지 읽는다
3. 가설 수립  → "이 층이 실패했다면 원인은 A 또는 B"
4. 도구 선택  → 가설을 확인/반증할 최소 도구 하나만 실행
5. 결과 기록  → 정상/비정상 판정과 근거를 한 줄로 남긴다
6. 반복       → 원인이 확정될 때까지 3-5를 반복
7. 검증       → 수정 후 동일 도구로 증상이 사라졌는지 확인
8. 문서화     → 타임라인 + 근본 원인 + 재발 방지를 기록
```

이 여덟 단계를 종이에 붙여 두면 새벽 3시에도 순서를 놓치지 않습니다. 핵심은 도구를 실행하기 전에 반드시 가설을 먼저 적는 것입니다. 가설 없이 도구를 돌리면 출력만 쌓이고 판단은 느려집니다.

## 체크리스트

- [ ] 호스트 생존 여부를 확인했는가? (`ping` 또는 `nc`)
- [ ] DNS가 정상인지 확인했는가? (`dig +short`)
- [ ] TCP 연결이 되는지 확인했는가? (`nc -vz`)
- [ ] TLS 핸드셰이크가 정상인지 확인했는가? (`openssl s_client -servername`)
- [ ] HTTP 응답을 직접 봤는가? (`curl -v`)
- [ ] 타이밍 병목을 확인했는가? (`curl -w`)
- [ ] 더 단순한 도구가 다 소진된 뒤에만 `tcpdump`를 켰는가?
- [ ] 결과를 포스트모템이나 런북에 기록했는가?

## 연습 문제

1. `nc -vz host port`가 `Connection refused`를 반환할 때와 `timeout`을 반환할 때, 다음 행동을 한 줄씩 적어 보세요.
2. 사용자가 "사이트가 갑자기 안 된다"고 했을 때 실행할 다섯 명령과, 각각 어떤 출력이 나와야 다음 단계로 갈지 적어 보세요.
3. `api.example.com`의 443 포트 트래픽만 `cap.pcap`으로 저장하는 `tcpdump` 명령을 직접 써 보세요.
4. `curl -w`를 사용해 DNS, Connect, TLS, Total 타이밍을 측정하는 명령을 작성하고, 각 구간이 느릴 때 의심할 원인을 적어 보세요.
5. tcpdump로 SYN 재전송이 반복되는 것을 확인했다면, 다음으로 어떤 것을 확인해야 할지 세 가지를 적어 보세요.

## 정리와 다음 글

네트워크 디버깅의 본질은 계층을 따라 내려가며 가설을 하나씩 지우는 일입니다. `ping`, `dig`, `nc`, `openssl s_client`, `curl -v` 다섯 줄이면 대부분 1분 안에 문제 층이 갈립니다. 그 뒤에야 `tcpdump`를 꺼내면 됩니다.

이로써 Computer Networks 101 시리즈를 마칩니다. 네트워크의 개념에서 시작해 IP, TCP, DNS, HTTP, TLS, 라우팅, 로드밸런서, WebSocket, 그리고 디버깅까지 한 바퀴를 돌았습니다. 다음에 새벽 호출이 오더라도, 첫 다섯 줄은 머뭇거리지 않고 떠올릴 수 있기를 바랍니다.

## 처음 질문으로 돌아가기

- **네트워크 문제를 계층별로 어떻게 좁혀 가야 할까요?**
  - 링크/경로 → DNS → TCP → TLS → HTTP 순서로 각 층을 확인합니다. 한 층이 정상으로 확정되면 그 아래는 더 이상 의심하지 않고 위층으로 올라갑니다. 핵심은 "여기까지는 정상"을 증거로 확정하는 것이며, 이 과정에서 원인 후보가 기하급수로 줄어듭니다.
- **`ping`, `dig`, `curl`, `ss`, `tcpdump`는 각각 무엇을 말해 줄까요?**
  - `ping`은 호스트가 살아 있고 경로가 통하는지(ICMP), `dig`는 이름이 IP로 변환되는지(DNS), `nc -vz`는 포트가 열려 있는지(TCP), `openssl s_client`는 인증서가 유효한지(TLS), `curl -v`는 HTTP 응답이 정상인지를 보여줍니다. `ss`는 서버 쪽에서 어떤 포트가 listen 중인지, `tcpdump`는 패킷이 실제로 오가는지를 확인합니다.
- **timeout, reset, DNS 실패는 어떤 모양으로 구분할 수 있을까요?**
  - timeout은 SYN을 보냈는데 아무 응답이 없는 상태(방화벽이 조용히 드롭), reset은 RST 패킷이 즉시 돌아오는 상태(호스트는 살아 있으나 포트가 닫힘 또는 방화벽이 명시적 거부), DNS 실패는 "Could not resolve host" 메시지와 함께 이름 변환 자체가 안 되는 상태입니다. 세 가지의 다음 행동이 완전히 다르므로 메시지를 정확히 읽는 것이 첫걸음입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Networks 101 (1/10): 네트워크란 무엇인가?](./01-what-is-a-network.md)
- [Computer Networks 101 (2/10): IP와 subnet](./02-ip-and-subnet.md)
- [Computer Networks 101 (3/10): TCP와 UDP](./03-tcp-and-udp.md)
- [Computer Networks 101 (4/10): DNS](./04-dns.md)
- [Computer Networks 101 (5/10): HTTP와 HTTPS](./05-http-and-https.md)
- [Computer Networks 101 (6/10): TLS 기초](./06-tls-basics.md)
- [Computer Networks 101 (7/10): 라우팅과 NAT](./07-routing-and-nat.md)
- [Computer Networks 101 (8/10): Load Balancer](./08-load-balancer.md)
- [Computer Networks 101 (9/10): WebSocket과 실시간 통신](./09-websocket-and-realtime.md)
- **네트워크 문제 디버깅 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [tcpdump Manual](https://www.tcpdump.org/manpages/tcpdump.1.html)
- [Wireshark User's Guide](https://www.wireshark.org/docs/wsug_html_chunked/)
- [`ss(8)` Linux Manual](https://man7.org/linux/man-pages/man8/ss.8.html)
- [Julia Evans — Networking debugging zines](https://wizardzines.com/zines/networking/)
- [curl Manual](https://curl.se/docs/manpage.html)
- [OpenSSL `s_client` 문서](https://docs.openssl.org/master/man1/openssl-s_client/)
- [book-examples: computer-networks-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/computer-networks-101/ko)

Tags: Computer Science, 네트워크, 디버깅, tcpdump, 트러블슈팅, 진단
