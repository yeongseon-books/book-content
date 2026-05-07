---
series: information-security-101
episode: 9
title: 로그와 감사
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
  - Security
  - Logging
  - Audit
  - SIEM
  - Compliance
seo_description: 무엇을 로그에 남기고 무엇을 남기면 안 되는지, 감사 로그와 SIEM의 역할을 짧게 정리합니다.
last_reviewed: '2026-05-04'
---

# 로그와 감사

> Information Security 101 시리즈 (9/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 사고는 막을 수 없을 때가 있습니다. 그렇다면 무엇으로 알아챌까요?

> 로그는 사건의 기억입니다. 기억이 없는 시스템은 사고가 났는지조차 모릅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 보안 로그와 일반 로그의 차이
- 무엇을 로그에 남기고, 무엇을 남기지 않는가
- 감사 로그(audit log)의 불변성(immutability)
- SIEM의 역할
- 컴플라이언스(SOC2, ISO 27001)와의 연결

## 왜 중요한가

탐지 없이는 대응이 없습니다. 평균 침해 탐지 시간은 200일 이상 — 좋은 로그는 이것을 시간 단위로 줄입니다.

> 알아채는 데 200일 걸리는 사고는 사고가 아니라 재앙입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    A["애플리케이션"] -->|"구조화 로그"| L["수집"]
    L -->|"불변 저장"| S["SIEM"]
    S -->|"룰/이상 탐지"| AL["알람"]
```

수집 -> 저장 -> 분석 -> 알람의 파이프라인.

## 핵심 용어 정리

- **Audit log**: "누가 언제 무엇을 했는가"의 기록.
- **Structured logging**: JSON 등 기계가 읽을 수 있는 포맷.
- **Immutability**: 한 번 쓰면 수정/삭제 불가.
- **SIEM**: Security Information and Event Management.
- **Retention**: 로그 보존 기간 — 컴플라이언스가 결정.

## Before/After

**Before — 평문 로그, 자유 형식**

```text
"User did something at /api/x" -> 검색/집계 불가
```

**After — 구조화 + 불변 저장**

```json
{"ts":"2026-05-04T10:00Z","user":"alice","action":"read","resource":"reports/2026"}
```

같은 사건도 형식이 분석 가능성을 결정합니다.

## 실습: 로그 다루기

### 1단계 — 구조화 로깅

```python
# 1_struct_log.py
import json, time, sys
def log(event, **fields):
    rec = {"ts": time.strftime("%FT%TZ"), "event": event, **fields}
    sys.stdout.write(json.dumps(rec) + "\n")

log("auth_login", user="alice", ip="10.0.0.1", ok=True)
```

free-form 문자열 대신 키-값으로 작성합니다.

### 2단계 — 절대 로그에 남기지 말 것

```python
# 2_no_log.py
# log("login", user=user, password=pw)        # 금지
# log("token", token=jwt)                     # 금지
# log("card", number="4111-...", cvv=cvv)     # 금지
```

비밀번호, 토큰, PII는 마스킹하거나 아예 남기지 않습니다.

### 3단계 — 감사 로그 분리

```python
# 3_audit.py
def audit(actor, action, resource, result):
    rec = {"actor": actor, "action": action, "resource": resource, "result": result}
    write_to_immutable_store(rec)   # WORM (write-once-read-many)
```

운영 로그와 분리해 무결성을 보장합니다.

### 4단계 — 로그 무결성 (HMAC chain)

```python
# 4_chain.py
import hmac, hashlib, json
def append(prev_mac, record, key):
    payload = json.dumps(record, sort_keys=True).encode()
    return hmac.new(key, prev_mac + payload, hashlib.sha256).hexdigest()
```

이전 레코드를 묶어 서명하면 중간 변조가 드러납니다.

### 5단계 — SIEM 룰 (의사코드)

```text
# 5_rule.txt
RULE "brute force":
  WHEN count(auth_login WHERE ok=false) > 10 BY user, ip IN 5min
  THEN alert(severity=high)
```

룰은 데이터 모델 위에서 동작합니다.

## 이 코드에서 주목할 점

- 모든 로그는 구조화되어야 합니다.
- 비밀/PII는 절대 평문으로 남기지 않습니다.
- 감사 로그는 운영 로그와 저장소를 분리합니다.
- 무결성 보호(서명, WORM)를 적용합니다.

## 자주 하는 실수 5가지

1. **비밀번호/토큰을 로그에 출력.** 가장 흔한 광범위 노출.
2. **자유 형식 문자열만 사용.** 분석 불가.
3. **로그를 운영 DB에 저장.** 변조 가능.
4. **보존 기간 미정의.** 컴플라이언스 위반 또는 비용 폭증.
5. **알람 피로(alert fatigue).** 모든 게 critical이면 아무것도 critical이 아닙니다.

## 실무에서는 이렇게 쓰입니다

K8s는 audit policy로 API 서버 호출을 모두 기록. AWS는 CloudTrail + GuardDuty + Security Hub. 대형 조직은 SIEM(Splunk, Elastic SIEM, Chronicle)에 모든 보안 이벤트를 집계해 SOC가 24/7 모니터링합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 로그는 시스템의 기본 출력입니다 — 사후 추가가 어렵습니다.
- 알람 임계값은 데이터로 정합니다.
- 감사 로그는 운영팀이 못 지우게 합니다.
- 보존 기간은 법적/계약적 요구로 정합니다.
- 정기적으로 "탐지되지 않는 시나리오"를 게임데이로 검증합니다.

## 체크리스트

- [ ] 모든 로그가 구조화되어 있는가?
- [ ] 비밀/PII 마스킹 룰이 있는가?
- [ ] 감사 로그가 불변 저장소에 있는가?
- [ ] 보존 기간이 정의되어 있는가?
- [ ] 핵심 룰 5가지의 알람 임계값을 답할 수 있는가?

## 연습 문제

1. 로그인 실패가 분당 100건 발생할 때의 알람 룰을 작성해 보세요.
2. 감사 로그의 불변성을 보장하는 두 가지 방법을 적어 보세요.
3. PII 마스킹 미들웨어의 의사코드를 작성해 보세요.

## 정리 및 다음 단계

로그는 사고를 알아채게 합니다. 마지막 글에서는 알아챈 다음 무엇을 할지 — 보안 사고 대응 — 를 봅니다.

<!-- toc:begin -->
- [정보보안이란 무엇인가?](./01-what-is-information-security.md)
- [인증과 인가](./02-authentication-and-authorization.md)
- [암호화와 해시](./03-cryptography-and-hash.md)
- [TLS와 인증서](./04-tls-and-certificates.md)
- [Web 보안 기초](./05-web-security-basics.md)
- [SQL Injection과 XSS](./06-sql-injection-and-xss.md)
- [secret 관리](./07-secret-management.md)
- [권한 최소화](./08-least-privilege.md)
- **로그와 감사 (현재 글)**
- 보안 사고 대응 (예정)
<!-- toc:end -->

## 참고 자료

- [NIST SP 800-92 — Guide to Computer Security Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)
- [OWASP — Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [Kubernetes — Auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)
- [Elastic — SIEM Documentation](https://www.elastic.co/guide/en/security/current/index.html)

Tags: Computer Science, Security, Logging, Audit, SIEM, Compliance
