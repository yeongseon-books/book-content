---
series: secure-coding-101
episode: 10
title: "Secure Coding 101 (10/10): 안전한 로깅과 감사"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Logging
  - AuditLog
  - SecureCoding
  - Compliance
  - SIEM
seo_description: 민감정보 마스킹, 감사 로그, 위변조 방지, 보존 정책 그리고 안전한 로깅 5단계
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (10/10): 안전한 로깅과 감사

사고가 터졌을 때 팀이 가장 먼저 묻는 질문은 늘 비슷합니다. 언제 시작됐는지, 누가 어떤 요청을 보냈는지, 어떤 자원이 바뀌었는지 알아야 복구가 시작됩니다. 그런데 로그에 비밀번호와 토큰이 남아 있거나, 중요한 이벤트가 섞여 있어서 읽을 수 없거나, 공격자가 로그를 지워 버릴 수 있다면 기록은 증거가 아니라 새로운 위험이 됩니다.

이 글은 Secure Coding 101 시리즈의 마지막 글입니다.

여기서는 로깅을 디버깅 편의 기능으로만 보지 않고, 사고 대응과 감사에 필요한 증거 체계로 정리하겠습니다. 이 관점을 이해하면 왜 민감 필드 마스킹, 감사 로그 분리, 불변 저장소, 보존 정책이 모두 함께 필요하며, 시리즈 전체의 보안 원칙이 마지막에 로그로 모이는지도 분명해집니다.

![Secure Coding 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/10/10-01-concept-at-a-glance.ko.png)
*Secure Coding 101 10장 흐름 개요*

> 로깅은 디버깅 편의 기능이 아니라 사고 대응의 증거 체계입니다 — 비밀번호·토큰이 로그에 남거나, 중요한 이벤트가 일반 로그에 섞이거나, 공격자가 로그를 지울 수 있다면 기록은 증거가 아니라 새로운 위험이 됩니다.

## 먼저 던지는 질문

- 애플리케이션 로그와 감사 로그는 무엇이 다를까요?
- 민감 필드 마스킹 정책은 어디까지 포함해야 할까요?
- 위변조 탐지와 append-only 저장은 왜 중요한가요?

## 왜 중요한가

사고 대응은 사실 재구성에서 시작합니다. 언제, 누가, 무엇을 했는지 답할 수 없으면 사고는 끝나지 않습니다. 반대로 로그에 비밀번호, 토큰, 카드 번호가 남아 있으면 사고 조사 자료가 곧 유출 자료가 됩니다. 그래서 로깅은 많이 남기는 것보다 무엇을 남기지 않을지 먼저 정하는 일이 중요합니다.

또한 모든 로그가 같은 목적을 갖지 않습니다. 애플리케이션 로그는 디버깅과 운영 관찰을 돕고, 감사 로그는 누가 어떤 자원을 바꿨는지에 대한 법적·운영적 증거가 됩니다. 두 종류를 섞어 두면 읽기도 어려워지고, 조사와 보존 정책도 흐려집니다.

## 한눈에 보는 구조

애플리케이션은 구조화된 로그를 남기고, 민감 필드는 먼저 마스킹됩니다. 중요한 감사 이벤트는 중앙 저장소에 별도로 보관되며, 저장소는 위변조가 어려운 형태여야 합니다. SIEM은 그 기록을 모아 이상 징후를 탐지하고 알림을 보냅니다.

## 핵심 용어

- **애플리케이션 로그**: 디버깅과 운영 관찰을 위한 일반 로그입니다.
- **감사 로그**: 누가 어떤 자원에 어떤 작업을 했는지 남기는 증거 로그입니다.
- **위변조 탐지(tamper evidence)**: 로그가 수정되거나 삭제됐을 때 그 흔적을 알아낼 수 있는 성질입니다.
- **보존(retention)**: 로그를 얼마 동안 보관할지 정한 정책입니다.
- **SIEM**: 보안 로그를 수집하고 분석하며 경보를 올리는 시스템입니다.

## 바꾸기 전과 후

**바꾸기 전**: `print`로 비밀번호까지 그대로 남기고, 감사 이벤트와 디버그 로그가 섞여 있으며, 보존 기간도 정해져 있지 않습니다. 사고가 나면 누가 무엇을 지웠는지도 알기 어렵습니다.

**바꾼 후**: 구조화된 JSON 로그를 쓰고, 민감 필드는 기본적으로 마스킹하며, 감사 로그를 분리해 append-only 또는 immutable 저장소에 보관합니다. 보존 기간과 무결성 점검 주기도 문서로 남깁니다.

## 실습: 안전하게 로깅하는 5단계

### 1단계 — 구조화된 로그를 남깁니다

```python
import json, time
def log_event(event, **fields):
    print(json.dumps({"ts": time.time(), "event": event, **fields}))
```

문자열 로그는 읽을 때는 편할 수 있지만, 나중에 검색과 집계, 경보 규칙을 만들기 어렵습니다. 구조화된 로그는 운영 분석과 사고 대응 모두에 유리합니다. 어떤 필드를 기준으로 추적할지도 훨씬 분명해집니다.

### 2단계 — 민감 필드를 기본적으로 마스킹합니다

```python
SENSITIVE = {"password", "token", "card_number", "ssn"}

def mask(d):
    return {k: ("***" if k in SENSITIVE else v) for k, v in d.items()}

log_event("login", **mask({"user": "ana", "password": "x"}))
```

로그는 운영 편의를 위해 거의 모든 팀원이 보게 됩니다. 그래서 비밀번호, 토큰, 카드 번호 같은 값은 처음부터 남기지 않는 편이 안전합니다. 마스킹은 옵션이 아니라 기본값이어야 합니다.

### 3단계 — 감사 로그를 별도로 분리합니다

```python
def audit(actor, action, target, result):
    log_event(
        "audit", actor=actor, action=action,
        target=target, result=result,
    )
```

인증, 인가, 결제, 권한 변경처럼 나중에 증거가 되는 이벤트는 일반 운영 로그와 분리하는 편이 좋습니다. 그래야 보존 기간, 접근 권한, 조사 흐름을 별도로 설계할 수 있습니다.

### 4단계 — append-only 저장소를 사용합니다

```bash
# Object Lock 또는 immutable 설정이 켜진 객체 저장소를 사용합니다.
aws s3api put-object-lock-configuration ...
```

로그가 서버 로컬 디스크에만 있으면 공격자가 침입 후 쉽게 지울 수 있습니다. append-only 또는 immutable 저장소는 수정과 삭제를 어렵게 만들고, 위변조 흔적을 남깁니다. 증거 보전에는 이 특성이 핵심입니다.

### 5단계 — 보존 정책을 문서화합니다

```text
- application log: 30 days
- audit log: 1+ year (per regulation)
- integrity check every quarter
```

## 실제 조사 흐름으로 로그를 읽는 예

좋은 로그는 많이 남기는 로그가 아니라, 사건 순서를 빠르게 복원할 수 있는 로그입니다. 그래서 요청 ID, 사용자 ID, 자원 ID, UTC 타임스탬프가 꾸준히 이어져야 합니다.

```json
{"ts":"2026-05-15T09:00:11Z","event":"login","user_id":"u-42","request_id":"r-100"}
{"ts":"2026-05-15T09:00:15Z","event":"role_change","actor_id":"admin-7","target_user_id":"u-42","request_id":"r-101"}
{"ts":"2026-05-15T09:01:02Z","event":"export_started","user_id":"u-42","request_id":"r-102"}
```

이 정도만 갖춰도 “무슨 일이 있었지?”라는 질문을 “이 권한 변경 뒤에 어떤 내보내기 요청이 이어졌지?”라는 조사 가능한 질문으로 바꿀 수 있습니다. 감사 로그가 독자에게 실제로 주는 가치는 바로 이런 재구성 가능성입니다.

로그를 무한정 쌓는 것은 보안이 아니라 비용과 위험을 키울 수 있습니다. 반대로 너무 짧게 지우면 조사에 필요한 기록이 남지 않습니다. 용도와 규제에 맞춘 보존 기간을 문서화하고 주기적으로 무결성을 점검해야 합니다.

## 이 코드에서 먼저 볼 점

- 감사 로그는 애플리케이션 로그와 분리돼야 합니다.
- 마스킹은 opt-in이 아니라 기본 동작이어야 합니다.
- append-only 저장은 위변조 흔적을 남기게 해 줍니다.
- 보존 정책은 기술 설정이 아니라 운영 정책 문서이기도 합니다.

## 실무에서 자주 헷갈리는 지점

1. **비밀번호나 토큰이 로그에 흘러가는 경우**: 한 줄만 남아도 사고가 커집니다.
2. **감사 로그와 애플리케이션 로그를 섞는 경우**: 조사와 보존이 모두 어려워집니다.
3. **로그를 서버 디스크에만 두는 경우**: 침입 후 삭제되기 쉽습니다.
4. **시간대를 제각각 쓰는 경우**: 조사 시 이벤트 순서가 흐려집니다. UTC 기준이 안전합니다.
5. **보존 기간 없이 무한 저장하는 경우**: 비용과 노출 표면이 함께 커집니다.

## 실무에서는 이렇게 봅니다

많은 팀이 JSON 로그를 Fluent Bit나 Vector 같은 수집기로 모아 Loki, Elasticsearch, S3 같은 중앙 저장소로 보냅니다. 그 위에서 Splunk, Datadog, Wazuh 같은 SIEM이 감사 패턴과 이상 징후를 감지해 경보를 올립니다. 로깅은 수집과 저장, 분석이 분리된 파이프라인으로 보는 편이 실무적입니다.

또한 선임 엔지니어는 로그를 남기는 것과 읽히게 만드는 것을 함께 봅니다. 필드 이름이 일관돼야 하고, 사용자 ID와 요청 ID, 자원 ID가 서로 연결돼야 하며, 인증·인가·결제 같은 핵심 이벤트는 공통 형식으로 남아야 조사 속도가 나옵니다. 좋은 로그는 많이 남긴 로그가 아니라, 필요한 사실을 안전하게 다시 읽을 수 있는 로그입니다.

## 선임 엔지니어는 이렇게 생각합니다

- 로그는 자산이면서 동시에 위험입니다.
- 감사 로그는 비즈니스 신뢰에 직접 영향을 줍니다.
- 저장소가 불변에 가깝지 않으면 증거 의미가 약해집니다.
- 마스킹은 기본값이고, 예외만 제한적으로 풀어야 합니다.
- 보존 기간은 문서화된 정책이어야 합니다.

## 체크리스트

- [ ] 민감 필드가 마스킹됩니다.
- [ ] 감사 로그가 분리돼 있습니다.
- [ ] 저장소가 append-only 또는 immutable입니다.
- [ ] 보존 정책이 문서화돼 있습니다.

## 연습 문제

1. 지금 서비스에서 감사 이벤트 다섯 가지를 적어 보세요.
2. Pydantic 모델에 적용할 마스킹 함수를 설계해 보세요.
3. append-only 보장이 깨질 수 있는 시나리오 두 가지를 적어 보세요.

## 정리와 다음 글

안전한 로깅은 많이 기록하는 기술이 아니라, 필요한 사실을 정확히 남기되 민감정보는 숨기고 기록 자체는 보존하는 설계입니다. 이 글에서는 구조화된 로그, 기본 마스킹, 감사 로그 분리, 불변 저장소, 보존 정책이 왜 함께 가야 하는지 정리했습니다.

여기까지가 Secure Coding 101입니다. 입력 검증에서 시작해 인증, 인가, 저장, secret, 데이터베이스, 브라우저, 의존성, 로깅까지 가장 흔한 함정을 단계별로 피하면 시스템은 사고를 늦추고 복구 시간을 벌 수 있는 보안을 갖게 됩니다.

## 심화 실전 노트: structlog 실전 구성, PII 필터링, WORM 저장소, 경보 규칙, Correlation ID

### structlog 기반 구조화 로깅 실전 구성

Python 표준 logging은 문자열 기반이라 구조화가 번거롭습니다. structlog는 키-값 기반 로깅을 자연스럽게 만들어 줍니다.

```python
import structlog
import logging

# structlog 설정
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

# 사용 예시
logger.info("user_login", user_id="u-42", ip="192.168.1.100", method="password")
# 출력: {"event": "user_login", "user_id": "u-42", "ip": "192.168.1.100",
# "방법": "비밀번호", "수준": "정보", "타임스탬프": "2026-05-15T09:00:11Z"}

logger.warning("auth_failed", user_id="u-42", reason="invalid_password", attempt=3)
```

structlog의 장점은 컨텍스트를 자동으로 전파하는 것입니다. 요청 처리 시작 시 바인딩한 값이 해당 요청의 모든 로그에 자동으로 포함됩니다.

```python
from fastapi import FastAPI, Request
import structlog
from contextvars import ContextVar
import uuid

app = FastAPI()

@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        client_ip=request.client.host,
    )
    response = await call_next(request)
    return response

# 이후 어떤 함수에서 logger.info("event") 는 다음과 같습니다.
# request_id, path, method, client_ip가 자동으로 포함됩니다.
```

### PII(개인식별정보) 자동 필터링

마스킹을 개발자 기억에만 의존하면 반드시 빠지는 곳이 생깁니다. 로깅 파이프라인 자체에 필터를 넣어야 합니다.

```python
import re
import structlog

# PII 패턴 정의
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone_kr": re.compile(r"01[016789]-?\d{3,4}-?\d{4}"),
    "card_number": re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
    "resident_id": re.compile(r"\b\d{6}[- ]?\d{7}\b"),
}

# 민감 필드 키 목록
SENSITIVE_KEYS = {
    "password", "token", "secret", "api_key", "access_token",
    "refresh_token", "card_number", "ssn", "resident_id",
    "authorization", "cookie",
}

def pii_filter(logger, method_name, event_dict):
    """structlog processor: PII 자동 마스킹"""
    for key, value in list(event_dict.items()):
        # 키 기반 마스킹
        if key.lower() in SENSITIVE_KEYS:
            event_dict[key] = "***REDACTED***"
            continue

        # 값 기반 패턴 마스킹 (문자열인 경우)
        if isinstance(value, str):
            for pattern_name, pattern in PII_PATTERNS.items():
                if pattern.search(value):
                    event_dict[key] = pattern.sub(f"[{pattern_name.upper()}_REDACTED]", value)
                    break

    return event_dict

# structlog 설정에 추가
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        pii_filter,  # PII 필터를 JSONRenderer 전에 배치
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(),
    ],
)

# 테스트
logger = structlog.get_logger()
logger.info("user_action", email="user@example.com", password="secret123")
# 출력: {"event": "user_action", "email": "[EMAIL_REDACTED]",
#         "password": "***REDACTED***", ...}
```

### Correlation ID를 활용한 분산 추적

마이크로서비스 환경에서는 하나의 사용자 요청이 여러 서비스를 거칩니다. Correlation ID가 없으면 서비스 간 로그를 연결할 수 없습니다.

```python
import uuid
from fastapi import FastAPI, Request, Response
import structlog

app = FastAPI()
logger = structlog.get_logger()

CORRELATION_HEADER = "X-Correlation-ID"

@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    # 상위 서비스에서 전달된 ID가 있으면 사용, 없으면 생성
    correlation_id = request.headers.get(CORRELATION_HEADER, str(uuid.uuid4()))

    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

    response = await call_next(request)
    response.headers[CORRELATION_HEADER] = correlation_id
    return response

# 다른 서비스 호출 시 ID 전파
import httpx

async def call_downstream_service(url: str, data: dict):
    ctx = structlog.contextvars.get_contextvars()
    correlation_id = ctx.get("correlation_id", str(uuid.uuid4()))

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=data,
            headers={CORRELATION_HEADER: correlation_id}
        )
    return response
```

```text
Correlation ID로 연결된 로그 예시:

서비스 A (API Gateway):
{"correlation_id": "abc-123", "event": "request_received", "path": "/transfer"}

서비스 B (Payment):
{"correlation_id": "abc-123", "event": "payment_initiated", "amount": 50000}

서비스 C (Notification):
{"correlation_id": "abc-123", "event": "email_sent", "template": "transfer_confirm"}

조사 시: correlation_id="abc-123"으로 검색하면 전체 흐름 파악 가능
```

### 감사 로그 전용 모델 설계

감사 로그는 애플리케이션 로그와 스키마부터 다릅니다. 누가, 언제, 무엇을, 어떻게 했는지를 빠짐없이 기록해야 합니다.

```python
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import json
import structlog

class AuditAction(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHANGE = "permission_change"
    EXPORT = "export"

@dataclass
class AuditEvent:
    timestamp: str
    actor_id: str
    actor_type: str  # "user", "service", "system"
    action: str
    resource_type: str
    resource_id: str
    result: str  # "success", "failure", "denied"
    details: dict
    correlation_id: str
    source_ip: str

    @classmethod
    def create(cls, actor_id: str, action: AuditAction, resource_type: str,
               resource_id: str, result: str, **kwargs):
        ctx = structlog.contextvars.get_contextvars()
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor_id=actor_id,
            actor_type=kwargs.get("actor_type", "user"),
            action=action.value,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            details=kwargs.get("details", {}),
            correlation_id=ctx.get("correlation_id", ""),
            source_ip=ctx.get("client_ip", ""),
        )

# 감사 로그 전용 기록기
audit_logger = structlog.get_logger("audit")

def record_audit(event: AuditEvent):
    audit_logger.info("audit_event", **asdict(event))

# 사용 예시
record_audit(AuditEvent.create(
    actor_id="u-42",
    action=AuditAction.PERMISSION_CHANGE,
    resource_type="user",
    resource_id="u-99",
    result="success",
    details={"old_role": "viewer", "new_role": "admin"},
))
```

### WORM(Write Once Read Many) 저장소 구성

감사 로그는 수정이나 삭제가 불가능해야 증거로서 가치가 있습니다. WORM 저장소는 이 요구사항을 기술적으로 보장합니다.

```bash
# AWS S3 Object Lock 설정 (Governance 모드)
aws s3api put-object-lock-configuration \
  --bucket audit-logs-prod \
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "GOVERNANCE",
        "Days": 365
      }
    }
  }'

# Compliance 모드 — 루트 사용자도 삭제 불가
aws s3api put-object-lock-configuration \
  --bucket audit-logs-compliance \
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "COMPLIANCE",
        "Days": 2555
      }
    }
  }'
```

```text
WORM 모드 비교:
| 모드        | 삭제 가능  | 용도                     |
|------------|-----------|--------------------------|
| Governance | 특수 권한 필요 | 일반 감사 로그, 운영 기록     |
| Compliance | 불가능     | 규제 준수 (금융, 의료, 법적 증거) |
```

```python
# 로그를 S3 WORM 버킷에 업로드하는 배치 처리
import boto3
from datetime import datetime

s3 = boto3.client("s3")
AUDIT_BUCKET = "audit-logs-prod"

def upload_audit_logs(log_lines: list[str], service_name: str):
    now = datetime.utcnow()
    key = f"audit/{service_name}/{now.strftime('%Y/%m/%d/%H')}/{now.isoformat()}.jsonl"

    body = "\n".join(log_lines)

    s3.put_object(
        Bucket=AUDIT_BUCKET,
        Key=key,
        Body=body.encode(),
        ContentType="application/x-ndjson",
        # Object Lock이 버킷 레벨로 설정되어 있으면 자동 적용
    )
    return key
```

### 경보 규칙 설계

로그를 수집만 하고 경보를 만들지 않으면 사고 탐지가 늦어집니다. 감사 로그 기반 경보 규칙은 보안 모니터링의 핵심입니다.

```text
경보 규칙 예시:

1. 인증 실패 급증
   조건: 동일 IP에서 5분 내 10회 이상 로그인 실패
   심각도: HIGH
   대응: IP 임시 차단 + 인시던트 생성

2. 권한 상승 탐지
   조건: 일반 사용자에게 admin 역할 부여
   심각도: CRITICAL
   대응: 즉시 알림 + 변경 승인 여부 확인

3. 대량 데이터 조회
   조건: 단일 사용자가 1시간 내 1000건 이상 개인정보 조회
   심각도: MEDIUM
   대응: 검토 요청 생성

4. 업무 시간 외 접근
   조건: 새벽 2-5시 사이 관리자 기능 접근
   심각도: MEDIUM
   대응: 당직자 알림

5. 감사 로그 자체 접근
   조건: 감사 로그 삭제/수정 시도
   심각도: CRITICAL
   대응: 즉시 알림 + 계정 잠금
```

```python
# 간단한 경보 규칙 엔진 예시
from collections import defaultdict
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

class AlertEngine:
    def __init__(self):
        self.login_failures = defaultdict(list)  # ip -> [timestamps]

    def process_event(self, event: dict):
        # 규칙 1: 인증 실패 급증
        if event.get("event") == "auth_failed":
            ip = event.get("source_ip", "")
            now = datetime.utcnow()
            self.login_failures[ip].append(now)

            # 5분 이내 실패만 유지
            cutoff = now - timedelta(minutes=5)
            self.login_failures[ip] = [
                t for t in self.login_failures[ip] if t > cutoff
            ]

            if len(self.login_failures[ip]) >= 10:
                self.fire_alert(
                    severity="HIGH",
                    rule="brute_force_detected",
                    details={"ip": ip, "count": len(self.login_failures[ip])}
                )

        # 규칙 2: 권한 상승 탐지
        if (event.get("action") == "permission_change" and
            event.get("details", {}).get("new_role") == "admin"):
            self.fire_alert(
                severity="CRITICAL",
                rule="privilege_escalation",
                details={
                    "actor": event.get("actor_id"),
                    "target": event.get("resource_id"),
                }
            )

    def fire_alert(self, severity: str, rule: str, details: dict):
        logger.critical("security_alert", severity=severity, rule=rule, **details)
        # Slack/PagerDuty/이메일 캐스팅
```

### 로그 무결성 검증

저장된 로그가 변조되지 않았는지 주기적으로 검증해야 합니다. 해시 체인 방식이 가장 간단하면서도 효과적입니다.

```python
import hashlib
import json

class LogIntegrityChain:
    def __init__(self):
        self.previous_hash = "0" * 64  # genesis

    def append(self, log_entry: dict) -> dict:
        entry_with_chain = {
            **log_entry,
            "_prev_hash": self.previous_hash,
        }
        entry_json = json.dumps(entry_with_chain, sort_keys=True)
        current_hash = hashlib.sha256(entry_json.encode()).hexdigest()
        entry_with_chain["_hash"] = current_hash
        self.previous_hash = current_hash
        return entry_with_chain

    @staticmethod
    def verify_chain(entries: list[dict]) -> bool:
        for i, entry in enumerate(entries):
            stored_hash = entry.pop("_hash")
            entry_json = json.dumps(entry, sort_keys=True)
            computed_hash = hashlib.sha256(entry_json.encode()).hexdigest()
            if computed_hash != stored_hash:
                return False  # 변조 탐지
            entry["_hash"] = stored_hash

            if i > 0 and entry["_prev_hash"] != entries[i-1]["_hash"]:
                return False  # 체인 끊김 탐지
        return True
```

```text
무결성 검증 주기:
- 실시간: 로그 수집기가 체인 해시 검증
- 일간: 일별 로그 파일의 체크섬 검증
- 분기: 전체 감사 로그의 무결성 감사 보고서 생성
```

## 처음 질문으로 돌아가기

- **애플리케이션 로그와 감사 로그는 무엇이 다를까요?**
  - 애플리케이션 로그는 디버깅과 운영 관찰용이고 보존 기간이 짧습니다. 감사 로그는 "누가 어떤 자원을 바꿨는가"에 대한 증거로, 별도 스키마(AuditEvent 모델)로 기록하고 WORM 저장소에 장기 보존합니다. 감사 로그 전용 모델 절에서 본 것처럼 actor, action, resource, result를 빠짐없이 기록해야 조사에 쓸 수 있습니다.
- **민감 필드 마스킹 정책은 어디까지 포함해야 할까요?**
  - PII 필터링 절에서 본 것처럼 키 기반 마스킹(password, token 등)과 값 기반 패턴 매칭(이메일, 전화번호, 카드번호)을 함께 적용해야 합니다. 개발자 기억에 의존하지 않고 로깅 파이프라인(structlog processor) 자체에 필터를 넣어야 빠지는 곳이 없습니다.
- **위변조 탐지와 append-only 저장은 왜 중요한가요?**
  - 공격자가 침입 후 로그를 삭제하면 증거가 사라집니다. WORM 저장소(S3 Object Lock Compliance 모드)는 루트 사용자도 삭제할 수 없으므로 증거 보전이 보장됩니다. 해시 체인으로 무결성을 검증하면 중간에 로그가 변조됐는지도 탐지할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Secure Coding 101 (1/10): Secure Coding이란 무엇인가?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): 입력값 검증](./02-input-validation.md)
- [Secure Coding 101 (3/10): 인증과 세션](./03-authentication-and-session.md)
- [Secure Coding 101 (4/10): 인가와 권한](./04-authorization-and-permissions.md)
- [Secure Coding 101 (5/10): 안전한 데이터 저장](./05-safe-data-storage.md)
- [Secure Coding 101 (6/10): Secret과 키 관리](./06-secret-and-key-management.md)
- [Secure Coding 101 (7/10): SQL Injection과 ORM 안전 사용](./07-sql-injection-and-orm.md)
- [Secure Coding 101 (8/10): XSS와 CSRF 방어](./08-xss-and-csrf.md)
- [Secure Coding 101 (9/10): Dependency 취약점 관리](./09-dependency-vulnerabilities.md)
- **안전한 로깅과 감사 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [NIST 800-92 — Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)
- [Google SRE — Logging](https://sre.google/sre-book/monitoring-distributed-systems/)
- [AWS S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [OpenTelemetry Logs Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/secure-coding-101/ko)

Tags: Logging, AuditLog, SecureCoding, Compliance, SIEM
