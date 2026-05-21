---
title: "Information Security 101 (9/10): 로그와 감사"
series: information-security-101
episode: 9
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
  - Security
  - Logging
  - Audit
  - SIEM
  - Compliance
last_reviewed: '2026-05-12'
seo_description: 보안 로그와 감사 추적, SIEM, 보존 정책의 핵심을 짧게 정리합니다.
---

# Information Security 101 (9/10): 로그와 감사

모든 사고를 예방할 수는 없습니다. 그래서 중요한 것은 “무슨 일이 일어났는지 언제 알 수 있는가”입니다. 로그가 없거나 형식이 제각각이면 시스템은 침해를 당하고도 그 사실을 모를 수 있습니다. 운영 로그와 보안 로그, 감사 로그를 구분하고, 무엇을 절대 남기면 안 되는지 정리하는 일은 보안 대응의 출발점입니다.

이 글은 Information Security 101 시리즈의 9번째 글입니다.

## 먼저 던지는 질문

- 운영 로그와 보안 로그는 어떻게 다를까요?
- 무엇을 기록해야 하고 무엇은 절대 기록하면 안 될까요?
- 감사 로그는 왜 따로 둔 저장소와 불변성이 필요할까요?

## 큰 그림

![Information Security 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/information-security-101/09/09-01-big-picture.ko.png)

*Information Security 101 9장 흐름 개요*

그림은 사건 발생 → 기록 → 수집 → 분석 → 경고 → 대응의 주기를 보여줍니다. 로그는 사건을 남기고, 감시는 그 로그를 읽어서 '뭔가 이상한가'를 감지하고 빠르게 대응하는 체계입니다.

> 로그와 감시는 '사고 후에' 무엇이 일어났는지 보는 것이 아니라, 사고가 일어나는 '중에' 이상 신호를 감지하고 즉시 차단할 때 쓰는 메커니즘입니다.

## 왜 중요한가

탐지가 없으면 대응도 없습니다. 침해를 알아차리는 데 수백 일이 걸리면 그것은 사고라기보다 재난에 가깝습니다. 구조화된 로그, 분리된 감사 로그, 명확한 경보 규칙은 탐지 시간을 몇 시간 단위로 줄여 줍니다.

보안 로그는 나중에 추가하기 어렵습니다. 처음부터 출력 모델의 일부로 설계해야 합니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    A["Application"] -->|"structured logs"| L["Collector"]
    L -->|"immutable store"| S["SIEM"]
    S -->|"rules / anomaly"| AL["Alerts"]
```

수집하고, 저장하고, 분석하고, 경보를 보내는 흐름이 끊기지 않아야 합니다. 어느 한 단계라도 무너지면 탐지 품질이 급격히 떨어집니다.

## 핵심 용어

- 감사 로그: 누가 언제 무엇을 했는지를 남기는 기록입니다.
- 구조화 로그: JSON처럼 기계가 읽기 쉬운 형식입니다.
- 불변성: 한 번 기록되면 수정하거나 삭제할 수 없는 성질입니다.
- **SIEM**: 보안 이벤트를 모아 분석하고 경보를 만드는 시스템입니다.
- **보존 기간**: 로그를 얼마나 오래 유지할지 정하는 기준이며 규정 준수와 직접 연결됩니다.

## 전후 비교

### 이전 — 자유 형식 평문 로그

```text
"User did something at /api/x" -> not searchable, not aggregable
```

### 이후 — 구조화 로그와 불변 저장소

```json
{"ts":"2026-05-04T10:00Z","user":"alice","action":"read","resource":"reports/2026"}
```

같은 사건이라도 형식이 달라지면 분석 가능성이 완전히 달라집니다.

## 감사 로그 필수 항목

| 항목 | 설명 | 예시 | 법적 요구 사항 |
|---|---|---|---|
| **Who (누가)** | 행위자 신원 | `user_id=alice`, `service_account=api-worker` | 개인정보보호법, GDPR |
| **What (무엇을)** | 수행한 작업 | `action=delete_user`, `resource=reports/2026` | SOC 2, ISO 27001 |
| **When (언제)** | 정확한 시간 (UTC) | `timestamp=2026-05-21T10:00:00Z` | 모든 보안 표준 |
| **Where (어디서)** | 요청 출처 | `ip=10.0.1.5`, `region=us-east-1` | PCI-DSS |
| **Result (결과)** | 성공/실패 | `status=success`, `error_code=403` | 모든 감사 표준 |

감사 로그는 나중에 추가하기 어렵습니다. 처음부터 다섯 항목을 모두 포함하도록 설계해야 합니다. 법적 요구사항은 산업과 지역에 따라 다르지만, 이 다섯 항목은 거의 모든 표준에서 공통으로 요구됩니다.
## 단계별 실습

### 1단계 — 구조화 로그를 남깁니다

```python
# 1_struct_log.py
import json, time, sys
def log(event, **fields):
    rec = {"ts": time.strftime("%FT%TZ"), "event": event, **fields}
    sys.stdout.write(json.dumps(rec) + "\n")

log("auth_login", user="alice", ip="10.0.0.1", ok=True)
```

자유 형식 문장보다 키-값 구조가 훨씬 중요합니다. 그래야 검색, 집계, 규칙 적용이 가능합니다.

### 2단계 — 남기면 안 되는 값을 구분합니다

```python
# 2_no_log.py
# log("login", user=user, password=pw)        # forbidden
# log("token", token=jwt)                     # forbidden
# log("card", number="4111-...", cvv=cvv)     # forbidden
```

비밀번호, 토큰, 개인정보는 마스킹하거나 애초에 기록하지 않아야 합니다. 편의를 위해 남긴 로그가 더 큰 사고를 만들 수 있습니다.

### 3단계 — 감사 로그를 분리합니다

```python
# 3_audit.py
def audit(actor, action, resource, result):
    rec = {"actor": actor, "action": action, "resource": resource, "result": result}
    write_to_immutable_store(rec)   # WORM (write-once-read-many)
```

운영 로그와 감사 로그를 분리해야 무결성과 신뢰성이 올라갑니다. 운영 데이터베이스 안에 같이 두면 조작 가능성이 커집니다.

### 4단계 — 로그 무결성을 보호합니다

```python
# 4_chain.py
import hmac, hashlib, json
def append(prev_mac, record, key):
    payload = json.dumps(record, sort_keys=True).encode()
    return hmac.new(key, prev_mac + payload, hashlib.sha256).hexdigest()
```

이전 기록을 포함해 HMAC 체인을 만들면 중간 변조를 드러낼 수 있습니다.

### 5단계 — SIEM 규칙을 정의합니다

```text
# 5_rule.txt
RULE "brute force":
  WHEN count(auth_login WHERE ok=false) > 10 BY user, ip IN 5min
  THEN alert(severity=high)
```

좋은 규칙은 안정적인 데이터 모델 위에서만 동작합니다. 로그 형식이 흔들리면 경보 품질도 함께 흔들립니다.

### 6단계 — structlog로 감사 로그를 남깁니다

```python
# 6_structlog_audit.py
import structlog
from datetime import datetime

# structlog 설정
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

audit_logger = structlog.get_logger("audit")

def audit_action(actor: str, action: str, resource: str, result: str, ip: str = None):
    audit_logger.info(
        "audit_event",
        actor=actor,
        action=action,
        resource=resource,
        result=result,
        ip=ip,
        timestamp=datetime.utcnow().isoformat(),
    )

# 사용 예시
audit_action(
    actor="alice",
    action="delete_user",
    resource="users/123",
    result="success",
    ip="10.0.1.5",
)
# 출력: {"event": "audit_event", "actor": "alice", "action": "delete_user", ...}
```

structlog는 구조화된 로그를 쉽게 만들어 줍니다. JSON 형식으로 출력하면 나중에 일라스틱서치, Splunk, CloudWatch Logs Insights 같은 로그 분석 도구로 쉽게 검색할 수 있습니다.

## 이 코드와 예제에서 먼저 볼 점

- 모든 로그는 구조화되어야 합니다.
- 비밀 정보와 개인정보는 평문으로 남기면 안 됩니다.
- 감사 로그는 운영 로그와 분리된 저장소에 둬야 합니다.
- 서명이나 WORM 저장소 같은 무결성 보호가 필요합니다.

## 로그 보존 정책

로그를 얼마나 오래 보관할지는 법적 요구사항, 비용, 보안 사고 대응 시간의 균형에서 결정됩니다.

### 보존 기간 기준

| 로그 유형 | 권장 보존 기간 | 근거 |
|---|---|---|
| **감사 로그** | 1년 이상 | 개인정보보호법 3년, SOC 2 Type II 1년 |
| **보안 이벤트 로그** | 90일 이상 | NIST 권고사항 90일 |
| **애플리케이션 로그** | 30일 | 비용 vs 디버깅 효율 |
| **인프라 로그** | 7일 | 비용 vs 트러블슈팅 효율 |

감사 로그는 법적 규제가 가장 엄격합니다. 보안 사고가 발생하면 90일 이내 로그는 반드시 필요합니다. 애플리케이션과 인프라 로그는 보존 기간을 짧게 유지하고 비용을 절감할 수 있습니다.

### 계층화된 로그 보관

```python
# log_retention.py
from enum import Enum

class StorageTier(Enum):
    HOT = "hot"      # 즈시 검색 가능 (7일)
    WARM = "warm"    # 수 분 내 검색 (30일)
    COLD = "cold"    # 수 시간 내 검색 (90일)
    ARCHIVE = "archive"  # 복원 후 검색 (1년+)

def rotate_logs_to_tier(log_age_days: int) -> StorageTier:
    if log_age_days <= 7:
        return StorageTier.HOT
    elif log_age_days <= 30:
        return StorageTier.WARM
    elif log_age_days <= 90:
        return StorageTier.COLD
    else:
        return StorageTier.ARCHIVE

# S3 Lifecycle policy 예시
# - 7일 후 STANDARD -> STANDARD_IA
# - 30일 후 STANDARD_IA -> GLACIER
# - 365일 후 GLACIER -> DEEP_ARCHIVE
```

계층화된 저장소를 사용하면 보존 기간을 길게 유지하면서도 비용을 크게 줄일 수 있습니다. 최근 7일치는 빠른 검색이 필요하고, 오래된 로그는 나중에 필요하면 복원하는 방식이 효율적입니다.

### 로그 삭제 정책

```python
# log_deletion_policy.py
from datetime import datetime, timedelta

def can_delete_log(log_type: str, log_date: datetime) -> bool:
    """Check if log can be safely deleted per retention policy"""
    now = datetime.utcnow()
    age_days = (now - log_date).days

    retention = {
        "audit": 365,
        "security": 90,
        "application": 30,
        "infrastructure": 7,
    }

    if log_type not in retention:
        return False  # 모르는 로그는 삭제 금지

    return age_days > retention[log_type]

# 사용 예시
log_date = datetime(2025, 1, 1)
if can_delete_log("application", log_date):
    delete_log_safely(log_date)
```

로그 삭제는 보존 정책을 명시적으로 코드로 구현해야 합니다. 수동 삭제는 실수로 중요한 로그를 삭제할 위험이 있습니다.

## 자주 하는 실수 다섯 가지

1. **비밀번호나 토큰을 로그에 남기는 실수**: 가장 흔한 대형 유출 경로입니다.
2. **자유 형식 문자열만 남기는 실수**: 분석이 거의 불가능합니다.
3. **운영 데이터베이스에 로그를 저장하는 실수**: 변조에 취약합니다.
4. **보존 기간이 없는 실수**: 규정 위반이나 비용 폭증으로 이어집니다.
5. **모든 경보를 중요로 올리는 실수**: 경보 피로가 쌓여 진짜 사고를 놓칩니다.

## 실무에서는 이렇게 나타납니다

Kubernetes는 audit policy로 API 서버 호출을 기록합니다. AWS는 CloudTrail, GuardDuty, Security Hub를 결합합니다. 큰 조직은 Splunk, Elastic SIEM, Chronicle 같은 중앙 SIEM으로 보안 이벤트를 모으고 SOC가 24시간 감시합니다. 핵심은 로그를 많이 남기는 것이 아니라, 탐지 가능한 형식과 신뢰 가능한 저장 방식으로 남기는 데 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 로그를 시스템의 기본 출력으로 봅니다.
- 경보 임계값은 감이 아니라 데이터로 정합니다.
- 운영자는 감사 로그를 삭제할 수 없어야 한다고 봅니다.
- 보존 기간은 법률과 계약 요구사항으로 결정합니다.
- 감지되지 않는 시나리오를 게임데이로 점검합니다.

## 체크리스트

- [ ] 모든 로그가 구조화되어 있습니까?
- [ ] 비밀 정보와 개인정보 마스킹 규칙이 있습니까?
- [ ] 감사 로그가 불변 저장소에 있습니까?
- [ ] 보존 기간이 정의되어 있습니까?
- [ ] 상위 다섯 개 경보 규칙의 임계값을 말할 수 있습니까?

## 연습 문제

1. “분당 로그인 실패 100회”를 탐지하는 경보 규칙을 적어 보세요.
2. 감사 로그 불변성을 지키는 메커니즘 두 가지를 적어 보세요.
3. 개인정보를 마스킹하는 미들웨어 의사코드를 스케치해 보세요.

## 정리와 다음 글

로그는 사고를 눈에 보이게 만드는 장치입니다. 구조화, 불변성, 경보 규칙이 갖춰져야 탐지가 대응으로 이어집니다. 마지막 글에서는 사고를 실제로 목격했을 때 무엇을 해야 하는지, 보안 사고 대응을 다룹니다.


## 보안 테스트 도구 비교: SAST, DAST, SCA

로그와 감사 체계는 보안 테스트 결과와 연결될 때 효과가 커집니다. 특히 개발 파이프라인에서는 SAST/DAST/SCA를 분리해 이해해야 합니다.

| 도구 유형 | 보는 대상 | 강점 | 한계 | 운영 포인트 |
| --- | --- | --- | --- | --- |
| SAST | 소스 코드/바이트코드 | 개발 초기에 취약 패턴 탐지 | 실행 맥락 부족으로 오탐 가능 | PR 단계 게이트 적용 |
| DAST | 실행 중 애플리케이션 | 실제 동작 기반 취약점 확인 | 환경 준비 비용, 커버리지 제한 | 스테이징 정기 스캔 |
| SCA | 오픈소스 의존성 | 알려진 CVE 추적에 강함 | 알려지지 않은 취약점은 탐지 불가 | 의존성 업데이트 정책과 결합 |

세 도구를 경쟁 관계로 보지 않고, 다른 실패 모드를 보완하는 조합으로 봐야 합니다.

## 감사 로그 스키마 설계

감사 로그는 "읽기 쉬운 문장"이 아니라 "질문 가능한 데이터"여야 합니다. 최소 스키마 예시는 아래와 같습니다.

```yaml
# audit-log-schema.yaml
version: 1
fields:
  - name: ts
    type: datetime
    required: true
  - name: event_type
    type: string
    required: true
  - name: actor_id
    type: string
    required: true
  - name: actor_type
    type: enum[user,service]
    required: true
  - name: action
    type: string
    required: true
  - name: resource
    type: string
    required: true
  - name: result
    type: enum[allow,deny,error]
    required: true
  - name: trace_id
    type: string
    required: false
```

`trace_id`를 포함하면 보안 이벤트와 애플리케이션 요청 로그를 연결해 사고 조사 속도를 크게 높일 수 있습니다.

## Python 로깅 코드 예시

```python
# security_logger.py
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("security")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def sec_event(event_type: str, **fields) -> None:
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        **fields,
    }
    # 민감정보 마스킹 예시
    for key in ("password", "token", "secret"):
        if key in rec:
            rec[key] = "***REDACTED***"
    logger.info(json.dumps(rec, ensure_ascii=False))

sec_event(
    "authz_denied",
    actor_id="user-120",
    actor_type="user",
    action="delete_report",
    resource="report-2026-01",
    result="deny",
    trace_id="8c4f2f7a"
)
```

## 탐지 규칙과 감사 연결

- SAST에서 발견된 취약 파일 경로와 런타임 오류 로그를 연결합니다.
- DAST의 재현 요청을 WAF/애플리케이션 로그와 매칭합니다.
- SCA의 고위험 CVE 패키지가 실제로 로딩되는 경로를 감사 이벤트로 검증합니다.

테스트 도구 결과가 운영 로그와 분리되어 있으면 우선순위 판단이 늦어집니다. 반대로 연결되어 있으면 "이 취약점이 우리 서비스에서 실제로 악용 가능성이 높은가"를 빠르게 판단할 수 있습니다.


## 운영 점검 루프와 문서화 기준

보안 글에서 가장 자주 빠지는 부분은 "그래서 운영에서는 무엇을 주기적으로 확인할 것인가"입니다. 아래 루프를 기준으로 문서화하면 개념이 실무로 연결됩니다.

| 주기 | 점검 항목 | 산출물 |
| --- | --- | --- |
| 매일 | 고위험 경보, 인증 실패 급증, 권한 거부 급증 | 일일 보안 브리핑 |
| 매주 | 신규 배포 변경점의 보안 영향 | 변경 검토 노트 |
| 매월 | 키/토큰/인증서 만료 예정, 미사용 권한, 미사용 시크릿 | 월간 정리 리포트 |
| 분기 | 위협 모델 재평가, 런북 훈련, 통제 효과 검토 | 분기 보안 회고 |

실행 가능한 문서의 조건도 분명해야 합니다.

- 담당자(owner)와 대체 담당자가 명시되어야 합니다.
- 실패 조건과 에스컬레이션 기준이 수치로 정의되어야 합니다.
- 점검 결과가 티켓이나 액션 아이템으로 추적되어야 합니다.
- 예외 승인에는 만료일이 반드시 있어야 합니다.

보안은 단발성 프로젝트가 아니라 운영 루프입니다. 같은 점검을 반복해도 기준이 유지될 때 품질이 올라갑니다.


## 감사 이벤트 우선순위와 대응 플레이북

모든 로그를 같은 중요도로 다루면 경보 피로가 생깁니다. 보안팀이 즉시 대응할 이벤트를 먼저 정의해야 합니다.

| 이벤트 | 심각도 | 자동 조치 | 수동 확인 |
| --- | --- | --- | --- |
| 관리자 권한 변경 | 높음 | 즉시 알림 + 티켓 생성 | 승인 근거 검증 |
| 대량 로그인 실패 | 중간 | 계정 보호 모드 전환 | 공격 IP 분석 |
| 감사 로그 삭제 시도 | 높음 | 즉시 차단 + 포렌식 보존 | 내부자 위협 조사 |

## 불변 저장소 운영 규칙

- 감사 로그 버킷에는 쓰기 전용 역할만 허용합니다.
- 삭제 권한은 별도 승인을 거친 파기 작업에만 허용합니다.
- 로그 접근 이벤트 자체를 또 다른 감사 이벤트로 기록합니다.
- 분기별 복원 훈련으로 로그 가용성을 검증합니다.

보안 로그는 많이 쌓는 것보다, 사건을 재구성할 수 있는 품질로 남기는 것이 중요합니다.


## 탐지 규칙 품질을 높이는 운영 방법

탐지 규칙은 작성보다 유지보수가 더 중요합니다.

| 활동 | 주기 | 결과물 |
| --- | --- | --- |
| 규칙 오탐 분석 | 주간 | 임계값 조정안 |
| 미탐 사고 리뷰 | 사고 후 즉시 | 신규 탐지 쿼리 |
| 로그 필드 스키마 검증 | 배포 시 | 호환성 체크 리포트 |
| 고위험 이벤트 시뮬레이션 | 월간 | 탐지-대응 소요 시간 |

## 감사 로그 무결성 검증 절차

1. 샘플 구간을 선택해 해시 체인 검증을 수행합니다.
2. 저장소 접근 이력을 대조해 무단 조회를 확인합니다.
3. 백업 로그 복원 테스트로 가용성을 확인합니다.
4. 감사 결과를 분기 리포트에 반영합니다.

무결성 검증이 없는 로그는 단순 기록일 뿐입니다. 사고 조사 증적이 되려면 조작 불가능성과 복원 가능성을 함께 입증해야 합니다.


## SIEM 연동 아키텍처 예시

```text
애플리케이션/인프라 로그 수집
-> 파서에서 공통 스키마 정규화
-> 고위험 이벤트 태깅
-> SIEM 규칙 엔진 평가
-> 경보/티켓/온콜 호출
```

스키마 정규화 단계가 없으면 서비스마다 필드명이 달라 탐지 규칙 재사용이 어렵습니다.

## 감사 보고서에 포함할 최소 항목

| 항목 | 설명 |
| --- | --- |
| 기간 | 보고 대상 기간 |
| 주요 이벤트 통계 | 권한 변경, 실패 로그인, 삭제 시도 |
| 고위험 사고 요약 | 영향 범위, 대응 시간 |
| 통제 개선 항목 | 다음 분기 액션 아이템 |

감사 보고서는 단순 기록이 아니라 다음 개선의 입력이어야 합니다.


## 부록: 운영 리뷰 메모

운영 회고에서 다음 네 가지를 매번 확인합니다.

1. 이번 분기 가장 큰 위험이 무엇이었는가.
2. 통제가 실제로 작동했는가.
3. 탐지와 대응 시간이 목표를 충족했는가.
4. 다음 분기 우선 개선 항목은 무엇인가.

짧은 메모라도 반복해서 남기면 보안 품질의 추세를 읽을 수 있습니다.


## 부록: 감사 로그 품질 기준

감사 로그는 사건 재구성이 가능해야 합니다. 이를 위해 `누가`, `무엇을`, `언제`, `어디서`, `결과` 다섯 필드가 항상 채워져야 하며, 필드 누락 이벤트 자체도 경보로 처리해야 합니다. 또한 로그 파이프라인 변경 시 샘플 이벤트를 기준으로 파서 호환성 테스트를 수행해야 탐지 규칙이 갑자기 무력화되는 사고를 막을 수 있습니다.


### 로그 무결성 검증 체인

감사 로그가 사후에 변조되지 않았음을 증명하려면 로그 체인 해시를 사용합니다. 각 로그 레코드에 이전 레코드의 해시를 포함시켜 블록체인과 유사한 연결 구조를 만드는 방식입니다.

```python
"""감사 로그 무결성 체인 구현 예시."""
import hashlib
import json
from datetime import datetime, timezone


def create_audit_record(
    previous_hash: str,
    actor: str,
    action: str,
    resource: str,
    result: str,
) -> dict:
    """이전 해시를 포함한 감사 레코드를 생성한다."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "action": action,
        "resource": resource,
        "result": result,
        "previous_hash": previous_hash,
    }
    payload = json.dumps(record, sort_keys=True).encode()
    record["hash"] = hashlib.sha256(payload).hexdigest()
    return record
```

이 구조에서 공격자가 중간 로그 하나를 삭제하거나 수정하면 이후 모든 레코드의 해시가 불일치하므로 변조 사실이 즉시 드러납니다. 검증 배치 잡을 매시간 실행하면 로그 파이프라인 장애와 의도적 변조를 모두 탐지할 수 있습니다.

## 처음 질문으로 돌아가기

- **운영 로그와 보안 로그는 어떻게 다를까요?**
  - 로그인 실패, 권한 거부, 의심스러운 쿼리가 각각 어느 시스템에서 기록되고, 어느 형식으로 중앙화되며, 어떤 규칙으로 경보를 보내는지 명확히 합니다.
- **무엇을 기록해야 하고 무엇은 절대 기록하면 안 될까요?**
  - 초당 1000건 로그 중 모두 저장하면 비용이 높고, 샘플링하면 중요 사건을 놓칩니다. 그 사이를 택하는 규칙을 정하면 효과적인 감시가 됩니다.
- **감사 로그는 왜 따로 둔 저장소와 불변성이 필요할까요?**
  - 로그 형식 표준화, 감시 규칙 검증(거짓 경보 줄이기), 로그 보존 정책 및 삭제 규칙을 정의합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Information Security 101 (1/10): 정보보안이란 무엇인가?](./01-what-is-information-security.md)
- [Information Security 101 (2/10): 인증과 인가](./02-authentication-and-authorization.md)
- [Information Security 101 (3/10): 암호화와 해시](./03-cryptography-and-hash.md)
- [Information Security 101 (4/10): TLS와 인증서](./04-tls-and-certificates.md)
- [Information Security 101 (5/10): 웹 보안 기초](./05-web-security-basics.md)
- [Information Security 101 (6/10): SQL 인젝션과 XSS](./06-sql-injection-and-xss.md)
- [Information Security 101 (7/10): 비밀 정보 관리](./07-secret-management.md)
- [Information Security 101 (8/10): 권한 최소화](./08-least-privilege.md)
- **로그와 감사 (현재 글)**
- 보안 사고 대응 (예정)

<!-- toc:end -->

## 참고 자료

- [NIST SP 800-92 — Guide to Computer Security Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)
- [OWASP — Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [Kubernetes — Auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)
- [Elastic — SIEM Documentation](https://www.elastic.co/guide/en/security/current/index.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/information-security-101/ko)

Tags: Computer Science, Security, Logging, Audit, SIEM, Compliance
