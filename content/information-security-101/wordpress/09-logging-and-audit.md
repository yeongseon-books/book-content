---
title: "바이브코딩을 위한 Information Security 기초 (9/10): 로그와 감사"
series: information-security-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Security
  - Logging
  - Audit
  - SIEM
---

# 바이브코딩을 위한 Information Security 기초 (9/10): 로그와 감사

이 글은 "바이브코딩을 위한 Information Security 기초" 시리즈의 9번째 글입니다.

---

바이브코딩에서 AI는 로깅 코드를 빠르게 만들어 줍니다. 그런데 많은 팀이 "로그를 남긴다"는 사실에만 집중하고 "어떤 형식으로, 어디에, 얼마나 오래"를 놓칩니다. 로그가 없거나 형식이 제각각이면 시스템은 침해를 당하고도 그 사실을 모를 수 있습니다.

모든 사고를 예방할 수는 없습니다. 그래서 중요한 것은 "무슨 일이 일어났는지 언제 알 수 있는가"입니다. 탐지가 없으면 대응도 없습니다. 침해를 알아차리는 데 수백 일이 걸리면 그건 사고라기보다 재난에 가깝습니다.

구조화된 로그, 분리된 감사 로그, 명확한 경보 규칙은 탐지 시간을 몇 시간 단위로 줄여 줍니다. 보안 로그는 나중에 추가하기 어렵습니다. 처음부터 출력 모델의 일부로 설계해야 합니다.

운영 로그와 보안 로그, 감사 로그의 차이, 무엇을 절대 남기면 안 되는지, SIEM과 불변 저장소를 중심으로 정리합니다.

> **핵심 인사이트:** 로그를 많이 남기는 것이 중요한 것이 아닙니다. 탐지 가능한 형식과 신뢰 가능한 저장 방식으로 남겨야 사고가 눈에 보이게 됩니다. 비밀번호나 토큰이 로그에 남는 순간 그 로그 자체가 침해 경로가 됩니다.

## 이 글에서 다룰 문제

- 운영 로그와 보안 로그는 어떻게 다를까요?
- 무엇을 기록해야 하고 무엇은 절대 기록하면 안 될까요?
- 감사 로그는 왜 따로 둔 저장소와 불변성이 필요할까요?
- SIEM은 어떤 역할을 할까요?
- AI가 만든 로깅 코드에서 확인해야 할 것은 무엇인가요?

## 로그와 감사 핵심 패턴

```python
# 나쁜 예: 자유 형식 + 민감정보 포함
print(f"User {username} logged in with password {password}")

# 좋은 예: 구조화 로그 + 민감정보 마스킹
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("security")

def sec_event(event_type: str, **fields) -> None:
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        **fields,
    }
    # 민감정보 마스킹
    for key in ("password", "token", "secret"):
        if key in rec:
            rec[key] = "***REDACTED***"
    logger.info(json.dumps(rec, ensure_ascii=False))

sec_event(
    "authz_denied",
    actor_id="user-120",
    action="delete_report",
    resource="report-2026-01",
    result="deny",
    trace_id="8c4f2f7a"
)
```

```python
# 감사 로그: 운영 로그와 분리된 불변 저장소에 기록
def audit(actor: str, action: str, resource: str, result: str):
    rec = {
        "actor": actor,
        "action": action,
        "resource": resource,
        "result": result
    }
    write_to_immutable_store(rec)  # WORM (write-once-read-many)

# SIEM 탐지 규칙 예시
# RULE "brute force":
#   WHEN count(auth_login WHERE ok=false) > 10 BY user, ip IN 5min
#   THEN alert(severity=high)
```

## 변경 전후 비교

**Before: 자유 형식 평문 로그**
```text
- "User did something at /api/x" → 검색 불가, 집계 불가
- 비밀번호/토큰이 로그에 그대로 출력
- 운영 DB 안에 로그 저장 → 변조 가능
- 보존 기간 없음 → 사고 발생 후 로그 없음
```

**After: 구조화 로그 + 불변 감사 저장소**
```text
- JSON 구조화 로그 → 검색, 집계, SIEM 연동 가능
- 민감정보 마스킹 → 로그 자체가 침해 경로 안 됨
- 감사 로그 분리 저장 → 변조 시 즉시 탐지
- 보존 기간 정책 → 사고 조사 시 근거 확보
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 비밀번호/토큰을 로그에 남김 | 가장 흔한 대형 유출 경로 | 민감 필드 마스킹 필수 |
| 자유 형식 문자열만 남김 | SIEM 규칙 적용 불가 | JSON 구조화 로그 |
| 운영 DB에 로그 저장 | 변조에 취약 | 분리된 불변 저장소 사용 |
| 보존 기간 없음 | 규정 위반 또는 사고 후 로그 없음 | 유형별 보존 정책 수립 |
| 모든 경보를 높은 심각도로 | 경보 피로로 진짜 사고를 놓침 | 심각도 기준 명확히 구분 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"Python 애플리케이션에 보안 감사 로그를 추가해줘.
JSON 구조화 형식,
민감정보(password, token, secret) 자동 마스킹,
감사 로그는 운영 로그와 분리된 저장소에 기록,
who/what/when/where/result 다섯 항목 포함"

# AI 결과물 검증 체크포인트:
# - 비밀번호/토큰이 로그에 평문으로 출력되지 않는가?
# - JSON 등 구조화 형식인가?
# - 감사 로그가 운영 로그와 분리되어 있는가?
# - 로그 보존 기간이 정의되어 있는가?
# - SIEM 연동을 위한 필드 구조가 일관적인가?
```

## 운영 체크리스트

- [ ] 모든 로그가 구조화(JSON)되어 있다
- [ ] 비밀번호, 토큰, 개인정보 마스킹 규칙이 적용되어 있다
- [ ] 감사 로그가 불변 저장소에 분리 보관된다
- [ ] 유형별 보존 기간이 정의되어 있다 (감사 1년+, 보안 90일+)
- [ ] 상위 탐지 규칙의 임계값이 데이터 기반으로 설정되어 있다

## 처음 질문으로 돌아가기

- **운영 로그와 보안 로그의 차이는?** 운영 로그는 성능/디버깅 목적, 보안 로그는 who/what/when/where/result를 추적합니다. 감사 로그는 불변성이 보장된 별도 저장소에 보관해야 합니다.
- **절대 기록하면 안 되는 것은?** 비밀번호, JWT 토큰, 개인식별정보(주민번호, 카드번호)는 절대 평문으로 남기면 안 됩니다. 마스킹하거나 아예 기록하지 않아야 합니다.
- **SIEM이란?** 보안 이벤트를 수집하고 분석해 경보를 만드는 시스템입니다. 구조화된 로그 없이는 SIEM 탐지 규칙이 동작하지 않습니다.

## 정리

바이브코딩에서 AI가 만들어 준 로깅 코드에서 민감정보 마스킹 여부, 구조화 형식, 감사 로그 분리 여부를 반드시 확인하세요. 로그는 사고를 눈에 보이게 만드는 장치입니다. 구조화, 불변성, 경보 규칙이 갖춰져야 탐지가 대응으로 이어집니다. 다음 글에서는 사고 대응을 다룹니다.

## 참고 자료

- [NIST SP 800-92 — Guide to Computer Security Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)
- [OWASP — Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/information-security-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Information Security 기초 (1/10): 정보 보안이란 무엇인가?
- 바이브코딩을 위한 Information Security 기초 (2/10): 인증과 인가
- 바이브코딩을 위한 Information Security 기초 (3/10): 암호화와 해시
- 바이브코딩을 위한 Information Security 기초 (4/10): TLS와 인증서
- 바이브코딩을 위한 Information Security 기초 (5/10): 웹 보안 기초
- 바이브코딩을 위한 Information Security 기초 (6/10): SQL Injection과 XSS
- 바이브코딩을 위한 Information Security 기초 (7/10): 비밀 정보 관리
- 바이브코딩을 위한 Information Security 기초 (8/10): 권한 최소화
- **바이브코딩을 위한 Information Security 기초 (9/10): 로그와 감사 (현재 글)**
- 바이브코딩을 위한 Information Security 기초 (10/10): 보안 사고 대응
<!-- toc:end -->

Tags: 바이브코딩, Security, Logging, Audit, SIEM
