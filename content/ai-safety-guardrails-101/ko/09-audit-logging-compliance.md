---
title: "AI Safety & Guardrails 101 (9/10): 감사 로깅과 컴플라이언스"
series: ai-safety-guardrails-101
episode: 9
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Audit Logging
- Compliance
- GDPR
last_reviewed: '2026-05-14'
seo_description: LLM 시스템에서 audit log는 단순 디버깅이 아니라 컴플라이언스, 사고 조사, 모델 개선의 기준 자료입니다.
---

# AI Safety & Guardrails 101 (9/10): 감사 로깅과 컴플라이언스

LLM 시스템의 audit log는 시끄러운 application log가 아닙니다. 나중에 “왜 이 답이 나왔는가”, “어떤 guardrail이 통과했고 무엇이 차단됐는가”, “삭제 요청은 언제 처리됐는가”를 재구성해야 하므로, 목적도 형식도 보존 정책도 모두 달라야 합니다.

이 글은 AI Safety & Guardrails 101 시리즈의 9번째 글입니다.

특히 AI 시스템에서는 결정 근거를 남기지 않으면 사고 대응이 거의 불가능합니다. 검색 기반 응답이었다면 어떤 chunk를 봤는지, 어떤 모델 설정이 적용됐는지, 어떤 정책 judge가 통과했는지까지 함께 남아야 합니다. 그래야 규제 대응과 재현, drift 탐지가 가능합니다.

그래서 audit log는 “개발자가 보기 편한 로그”가 아니라 “나중에 증거로 제출할 수 있는 기록”으로 설계해야 합니다. append-only, 구조화, 제한된 접근, PII 분리 저장이 핵심입니다.

이 글에서는 audit schema, PII 분리 저장, append-only 무결성, decision rationale, 보존 기간, 자동 보고를 함께 정리합니다.

![감사 로깅과 compliance 흐름](https://yeongseon-books.github.io/book-public-assets/assets/ai-safety-guardrails-101/09/09-01-big-picture.ko.png)
*감사 로깅과 compliance 흐름*
> 감사 로그는 많이 남기는 로그가 아니라, 나중에 누가 무엇을 왜 했는지 재구성할 수 있는 증거입니다.

## 먼저 던지는 질문

- 감사 로그는 일반 디버그 로그와 무엇이 달라야 compliance에 쓸 수 있을까요?
- PII masking, append-only storage, decision rationale은 각각 어떤 증거를 남길까요?
- 자동 compliance report를 만들려면 로그 schema에 무엇이 고정되어야 할까요?

## 왜 이 글이 중요한가

감사 로깅이 잘 되어 있으면 규제 대응과 사고 조사가 훨씬 쉬워집니다. 어떤 요청이 어떤 모델을 거쳐 어떤 guardrail 결정을 받았는지 추적할 수 있고, 사용자 삭제 요청과 보존 만료도 체계적으로 관리할 수 있습니다. 이 기록은 보안뿐 아니라 운영 품질 개선에도 직접 연결됩니다.

반대로 application log에 원문 프롬프트와 응답을 그대로 남기면 가장 먼저 PII가 새어 나갑니다. 로그 접근 권한이 넓을수록 누출 범위가 커지고, 나중에 삭제 요청이 오면 어떤 사본이 어디에 남았는지도 파악하기 어려워집니다. append-only라고 말만 하고 UPDATE 가능한 테이블에 저장하면 감사 무결성도 증명할 수 없습니다.

결국 audit log의 핵심은 “기록을 많이 남기는가”가 아니라 “증거로 쓸 수 있는가”입니다. 이 관점으로 설계해야 저장소 구조와 접근 정책이 제대로 잡힙니다.

## 핵심 관점

application log는 빠른 디버깅을 위한 도구입니다. 반면 audit log는 나중에 재현과 소명에 쓰일 수 있어야 하므로 더 엄격해야 합니다. 자유 텍스트보다 구조화된 필드가 필요하고, 수정 가능성은 최소화해야 하며, 보관 기간도 훨씬 길어집니다.

또한 audit와 원문 데이터는 같은 저장소에 두지 않는 편이 낫습니다. audit는 무결성과 추적성, 원문 저장소는 최소 보관과 암호화가 목적이기 때문입니다. 목적이 다른 데이터를 같은 곳에 두면 권한과 삭제 정책이 충돌합니다.

> audit log의 가치는 로그를 남겼다는 사실이 아닙니다. 나중에 누가 봐도 변조되지 않았고, 결정 경로를 다시 설명할 수 있다는 점에 있습니다.

## 핵심 개념

### audit log는 application log와 목적이 다릅니다

| Property | Application log | Audit log |
| --- | --- | --- |
| Retention | 7 to 30 days | 1 to 7 years (regulation-dependent) |
| Mutability | Freely editable | Append-only, immutable |
| Access | Engineers in general | Security and compliance only |
| Format | Free-form text | Structured schema |
| PII | Masking recommended | Masking required, keys stored separately |

application log는 빨리 문제를 보는 데 적합하고, audit log는 나중에 이유를 재구성하는 데 적합합니다. 둘을 같은 목적으로 설계하면 어느 쪽도 만족하지 못합니다.

### audit record에는 재현에 필요한 필드가 들어가야 합니다

```python
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import uuid

@dataclass
class AuditRecord:
    request_id: str
    timestamp: str
    user_id_hash: str          # PII becomes a hash
    api_key_id: str
    model: str
    input_token_count: int
    output_token_count: int
    cost_usd: float
    guardrail_decisions: list  # ["pii_redacted", "moderation_passed", ...]
    blocked: bool
    block_reason: str | None
    prompt_hash: str           # raw text lives in a separate store
    response_hash: str
    retrieved_chunk_ids: list[int]
    latency_ms: int

def make_record(user_id: str, prompt: str, response: str, **kw) -> AuditRecord:
    return AuditRecord(
        request_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        user_id_hash=hashlib.sha256(user_id.encode()).hexdigest()[:16],
        prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),
        response_hash=hashlib.sha256(response.encode()).hexdigest(),
        **kw,
    )
```

원문 프롬프트와 응답은 audit 본문에 두지 않습니다. hash만 남기고, 필요한 경우에만 별도 저장소와 조인합니다.

### 원문 데이터는 별도 PII 저장소로 분리합니다

```python
def store_audit(record: AuditRecord, prompt: str, response: str):
    # 1. 감사 로그: 추가 전용, 해시 전용
    audit_db.insert(asdict(record))

    # 2. PII 저장소: KMS 암호화, 사용자 동의에 따른 단기 보존
    if user_consent_to_train(record.user_id_hash):
        encrypted_prompt = kms.encrypt(prompt)
        encrypted_response = kms.encrypt(response)
        pii_store.put(record.request_id, {
            "prompt": encrypted_prompt,
            "response": encrypted_response,
            "ttl": 90,  # days
        })
```

이 구조면 사용자 삭제 요청이 왔을 때 PII 저장소는 지우고, audit hash는 무결성 목적상 남길 수 있습니다.

### append-only는 정책이 아니라 기술적으로 강제해야 합니다

1. **WORM (Write Once Read Many) S3 bucket**: Object Lock with Compliance Mode. Even root cannot delete within retention.
2. **Append-only database**: ClickHouse or TimescaleDB. Do not grant UPDATE or DELETE to application users.
3. **Hash chain**: each record contains the previous record's hash, so any tampering is detectable later.

```python
from hashlib import sha256

def chain_hash(prev_hash: str, record: dict) -> str:
    payload = prev_hash + str(sorted(record.items()))
    return sha256(payload.encode()).hexdigest()

def append_with_chain(record: dict):
    prev = audit_db.last_hash() or "0" * 64
    record["prev_hash"] = prev
    record["self_hash"] = chain_hash(prev, record)
    audit_db.insert(record)
```

hash chain은 비용이 거의 들지 않으면서도 나중에 변조 여부를 자동으로 검증하게 해 줍니다.

### decision rationale이 있어야 규제 대응이 가능합니다

```python
def log_decision(request_id: str, query: str, chunks: list[dict], answer: str, params: dict):
    audit_db.insert({
        "request_id": request_id,
        "type": "rag_decision",
        "query_hash": sha256(query.encode()).hexdigest(),
        "chunk_ids": [c["id"] for c in chunks],
        "chunk_scores": [c["score"] for c in chunks],
        "model": params["model"],
        "temperature": params["temperature"],
        "seed": params.get("seed"),
        "answer_hash": sha256(answer.encode()).hexdigest(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
```

이 정보가 있으면 같은 모델, 같은 seed, 같은 검색 결과에서 왜 다른 답이 나왔는지까지 살펴볼 수 있습니다.

### 보존 기간과 자동 삭제는 감사 대상입니다

| Regulation | Suggested retention | Notes |
| --- | --- | --- |
| GDPR | Until processing purpose ends | Right to erasure required |
| HIPAA | 6 years | Health information |
| SOC 2 | 1 year | Security audit |
| PCI DSS | 1 year, last 3 months instantly searchable | Payments |
| PIPA (KR) | 5 years | PII processing records |

```python
from datetime import timedelta

RETENTION = {
    "audit_log": timedelta(days=365 * 7),     # 7 years
    "pii_store": timedelta(days=90),
}

def gc_pii_store():
    cutoff = datetime.now(timezone.utc) - RETENTION["pii_store"]
    pii_store.delete_where(lambda r: r["created_at"] < cutoff)
```

삭제 자체도 audit log에 다시 남겨야 무결성이 유지됩니다.

### 사람이 읽는 보고서로 변환해야 운영 가치가 생깁니다

```python
def monthly_report(year: int, month: int) -> dict:
    rows = audit_db.query(year=year, month=month)
    return {
        "total_requests": len(rows),
        "blocked_requests": sum(1 for r in rows if r["blocked"]),
        "block_reasons": Counter(r["block_reason"] for r in rows if r["blocked"]),
        "pii_redaction_count": sum(1 for r in rows if "pii_redacted" in r["guardrail_decisions"]),
        "models_used": Counter(r["model"] for r in rows),
        "total_cost_usd": sum(r["cost_usd"] for r in rows),
        "p95_latency_ms": percentile([r["latency_ms"] for r in rows], 95),
    }
```

월간 보고는 보안팀, 준법팀, 리더십이 같은 사실 집합을 보게 만들어 줍니다.

## 감사 로그 스키마를 계약처럼 고정하기

컴플라이언스 보고 자동화를 하려면 스키마가 흔들리면 안 됩니다. 아래는 운영에서 자주 쓰는 필수 필드 집합입니다.

```json
{
  "request_id": "req_...",
  "occurred_at": "2026-05-21T09:30:11Z",
  "actor_type": "end_user",
  "actor_id_hash": "a13f...",
  "tenant_id": "team-42",
  "endpoint": "/chat",
  "model": "gpt-4o-mini",
  "policy_version": "2026-05-21",
  "guardrail_stage": "post-output.pii",
  "decision": "blocked",
  "reason_code": "pii_detected",
  "input_tokens": 1280,
  "output_tokens": 0,
  "cost_usd": 0.00019,
  "retention_class": "audit_7y"
}
```

### 무결성 검증 배치 예시

```python
def verify_hash_chain(records: list[dict]) -> bool:
    prev = "0" * 64
    for rec in records:
        expected = chain_hash(prev, {k: v for k, v in rec.items() if k != "self_hash"})
        if rec.get("self_hash") != expected:
            return False
        prev = rec["self_hash"]
    return True
```

이 검증 배치를 주기적으로 돌려야 append-only 주장을 증명할 수 있습니다.

## 규제 대응용 체크 테이블

| 규제/감사 | 로그에서 바로 뽑아야 하는 항목 |
| --- | --- |
| GDPR Art.30 | 처리 목적, actor, 처리 시각, 보존 정책 |
| SOC 2 | 접근 이벤트, 권한 변경, 차단 이력 |
| 내부 감사 | 정책 버전별 차단율, 예외 승인 이력 |
| 침해 사고 대응 | 영향 요청 수, 누출 유형, 대응 시각 |

### 삭제 요청 처리 이벤트 예시

```python
def log_erasure(request_id: str, actor_hash: str, deleted_keys: list[str]):
    audit_db.insert({
        "type": "erasure_event",
        "request_id": request_id,
        "actor_hash": actor_hash,
        "deleted_keys": deleted_keys,
        "status": "completed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
```

삭제 자체가 audit 대상이라는 점을 놓치면 준법 감사에서 큰 결함으로 지적됩니다.

## 감사 로그 접근 통제 모델

로그를 잘 남겨도 권한이 넓으면 의미가 없습니다. 최소 권한 원칙을 역할별로 분리해야 합니다.

| 역할 | 접근 범위 | 비고 |
| --- | --- | --- |
| 서비스 운영자 | 집계 대시보드, 비식별 로그 | 원문 접근 금지 |
| 보안팀 | 감사 이벤트 원문(해시 기반) | 승인 워크플로 필요 |
| 준법팀 | 보존/삭제/정책 이력 | PII vault 접근 제한 |
| 개발팀 | 샘플링된 익명 데이터 | 요청 단위 원문 불가 |

### 접근 이벤트 자체 로깅

```python
def log_audit_access(actor: str, reason: str, query_scope: str):
    audit_db.insert({
        "type": "audit_access",
        "actor": actor,
        "reason": reason,
        "query_scope": query_scope,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
```

누가 어떤 목적으로 감사 로그를 조회했는지도 감사 대상입니다.

## 컴플라이언스 자동 보고 체크

- [ ] 정책 버전별 차단/허용 통계
- [ ] 삭제 요청 처리 SLA 준수율
- [ ] 접근 이벤트 이상 징후(야간 대량 조회 등)
- [ ] retention class별 만료/삭제 이행률

이 네 항목을 월간 리포트로 고정하면 감사 대응 속도가 크게 개선됩니다.

## 운영 부록: 검증 질문

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

## 흔히 헷갈리는 지점

- application log를 잘 남기면 audit log도 충분하다고 생각하기 쉽습니다.
- 원문 프롬프트를 같이 저장해야 나중에 편하다고 생각하기 쉽지만, 가장 큰 누출 표면이 됩니다.
- append-only는 운영 규칙으로만 관리해도 된다고 보기 쉽습니다.
- 삭제 정책은 원문 데이터에만 적용하면 된다고 생각하기 쉽습니다.

## 운영 체크리스트

- [ ] audit schema와 application log schema를 분리합니다.
- [ ] 원문 프롬프트·응답은 KMS 기반 별도 저장소에 두고 audit에는 hash만 남깁니다.
- [ ] WORM, 권한 통제, hash chain 중 최소 하나 이상으로 append-only를 기술적으로 강제합니다.
- [ ] 검색 chunk, 모델 파라미터, guardrail 결정을 rationale 필드로 기록합니다.
- [ ] 보존 기간 만료와 삭제 요청 처리 자체도 audit log에 남깁니다.

## 정리

감사 로깅은 나중에 보기 위한 로그가 아니라, 나중에 설명하기 위한 증거입니다. 이 차이를 이해하면 왜 별도 저장소, 별도 권한, 별도 보존 정책이 필요한지 자연스럽게 보입니다.

실무에서는 원문 데이터와 audit 데이터를 분리하고, append-only 무결성을 기술적으로 강제하며, decision rationale을 구조화된 필드로 남기는 방식이 가장 안정적입니다. 여기에 보존과 삭제 기록까지 들어가야 컴플라이언스가 완성됩니다.

더 중요한 일은 로그를 남기는 것 자체보다, 그 로그가 나중에도 신뢰될 수 있게 만드는 일입니다.

## 처음 질문으로 돌아가기

- **감사 로그는 일반 디버그 로그와 무엇이 달라야 compliance에 쓸 수 있을까요?**
  - 임의 수정이 어렵고, 필요한 필드가 고정되어 있으며, 개인정보와 원본 접근이 통제되고, 보존·삭제 정책이 분명해야 합니다.
- **PII masking, append-only storage, decision rationale은 각각 어떤 증거를 남길까요?**
  - PII masking은 노출 범위를 줄이고, append-only storage는 변조 가능성을 낮추며, decision rationale은 승인·차단 판단 근거를 남깁니다.
- **자동 compliance report를 만들려면 로그 schema에 무엇이 고정되어야 할까요?**
  - request id, actor, action, policy decision, tool call, masked fields, timestamps, retention class, rationale 필드가 고정되어야 합니다.
<!-- toc:begin -->
## 시리즈 목차

- [AI Safety & Guardrails 101 (1/10): AI Safety가 왜 중요한가](./01-why-ai-safety-matters.md)
- [AI Safety & Guardrails 101 (2/10): Prompt Injection 방어](./02-prompt-injection-defense.md)
- [AI Safety & Guardrails 101 (3/10): 출력 필터링과 콘텐츠 모더레이션](./03-output-filtering.md)
- [AI Safety & Guardrails 101 (4/10): PII 감지와 마스킹](./04-pii-detection-redaction.md)
- [AI Safety & Guardrails 101 (5/10): Jailbreak 탐지](./05-jailbreak-detection.md)
- [AI Safety & Guardrails 101 (6/10): 독성과 편향 탐지](./06-toxicity-bias-detection.md)
- [AI Safety & Guardrails 101 (7/10): Hallucination Guardrail — Grounding 검증](./07-hallucination-guardrails.md)
- [AI Safety & Guardrails 101 (8/10): Rate Limiting과 남용 방지](./08-rate-limiting-abuse-prevention.md)
- **AI Safety & Guardrails 101 (9/10): 감사 로깅과 컴플라이언스 (현재 글)**
- AI Safety & Guardrails 101 (10/10): 운영 가드레일 시스템 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [GDPR - Article 30: Records of processing activities](https://gdpr-info.eu/art-30-gdpr/)
- [HIPAA Security Rule - Audit controls](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [SOC 2 - Trust Services Criteria](https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services)
- [AWS S3 Object Lock - Compliance mode](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html)

### 관련 시리즈

- [PII 감지와 마스킹](./04-pii-detection-redaction.md)
- [LLM 앱 운영 101 — LLM 앱 모니터링과 로깅](../../llm-apps-ops-101/ko/01-monitoring-and-logging.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-safety-guardrails-101/ko/09-audit-logging-compliance)

Tags: AI Safety, Audit Logging, Compliance, GDPR
