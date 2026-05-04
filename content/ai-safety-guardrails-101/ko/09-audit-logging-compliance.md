---
title: 감사 로깅과 컴플라이언스
series: ai-safety-guardrails-101
episode: 9
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Audit Logging
- Compliance
- GDPR
last_reviewed: '2026-05-03'
seo_description: LLM 시스템에서 audit log는 단순 디버깅이 아니라 컴플라이언스, 사고 조사, 모델 개선의 기준 자료입니다.
---

# 감사 로깅과 컴플라이언스

> AI Safety & Guardrails 101 시리즈 (9/10)

---
## Section 1

## Audit log이 application log와 다른 이유

LLM 시스템에서 audit log는 단순 디버깅이 아니라 컴플라이언스, 사고 조사, 모델 개선의 기준 자료입니다. 일반 application log와 분리해 설계해야 합니다.

| 속성 | Application log | Audit log |
| --- | --- | --- |
| 보존 기간 | 7~30일 | 1~7년 (규제 의존) |
| 변경 가능성 | 자유 수정 | append-only, immutable |
| 접근 권한 | 개발자 일반 | 보안·컴플라이언스 한정 |
| 포맷 | 자유 텍스트 | 정형 schema |
| PII | 마스킹 권고 | 마스킹 필수, 키 분리 보관 |

application log는 "무엇이 일어났는가"를 빠르게 보기 위한 것이고, audit log는 "왜 그런 결정을 내렸는가"를 나중에 재구성하기 위한 것입니다.

## 무엇을 기록할 것인가

LLM 요청 한 건당 audit record는 다음 필드를 포함합니다.

```python
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import uuid

@dataclass
class AuditRecord:
    request_id: str
    timestamp: str
    user_id_hash: str          # PII는 해시로
    api_key_id: str
    model: str
    input_token_count: int
    output_token_count: int
    cost_usd: float
    guardrail_decisions: list  # ["pii_redacted", "moderation_passed", ...]
    blocked: bool
    block_reason: str | None
    prompt_hash: str           # 원문은 별도 저장소
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

원문 prompt와 response는 audit record에 포함하지 않고 별도 PII-aware 저장소(KMS 암호화)에 저장합니다. audit log에는 hash만 두어 무결성 검증과 사후 매칭에 사용합니다.

## PII 마스킹과 분리 저장

GDPR, PIPA, HIPAA는 모두 "처리 목적이 다르면 저장소를 분리"하라고 요구합니다. Audit는 검증 목적, 원문 prompt는 모델 개선 목적이므로 두 저장소가 다릅니다.

```python
def store_audit(record: AuditRecord, prompt: str, response: str):
    # 1. Audit log: append-only, hash만
    audit_db.insert(asdict(record))

    # 2. PII 저장소: KMS 암호화, 사용자 동의에 따라 보존 기간 짧게
    if user_consent_to_train(record.user_id_hash):
        encrypted_prompt = kms.encrypt(prompt)
        encrypted_response = kms.encrypt(response)
        pii_store.put(record.request_id, {
            "prompt": encrypted_prompt,
            "response": encrypted_response,
            "ttl": 90,  # days
        })
```

사용자가 데이터 삭제를 요청하면 PII 저장소에서만 삭제하고, audit log의 hash는 무결성을 위해 유지합니다.

## Append-only 저장소

Audit log는 한 번 기록되면 누구도 수정할 수 없어야 합니다. 세 가지 구현 패턴이 있습니다.

1. **WORM(Write Once Read Many) S3 버킷**: Object Lock with Compliance Mode. 보존 기간 안에는 root 계정도 삭제 못함.
2. **Append-only DB**: ClickHouse, TimescaleDB. UPDATE/DELETE 권한을 application 사용자에게 주지 않음.
3. **Hash chain**: 각 record가 이전 record의 hash를 포함. 중간 변조를 사후 검출 가능.

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

Hash chain은 비용이 거의 없으며 audit 검증을 자동화할 수 있습니다.

## Decision rationale 캡처

규제 대응에서 가장 자주 요구되는 항목은 "왜 그렇게 답했는가"입니다. RAG 시스템은 다음을 캡처합니다.

- 사용자 query (hash)
- Retrieved chunk IDs와 점수
- 적용된 guardrail decision
- 모델, 온도, 시드
- 최종 응답 (hash)

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

같은 query를 같은 모델·온도·seed로 재현했을 때 다른 답이 나오면 모델 drift 의심 신호로 사용합니다.

## 보존 기간과 자동 삭제

규제별 권장 보존 기간이 다릅니다.

| 규제 | 권장 보존 기간 | 비고 |
| --- | --- | --- |
| GDPR | 처리 목적 달성까지 | 사용자 삭제권 보장 |
| HIPAA | 6년 | 의료 정보 |
| SOC 2 | 1년 | 보안 audit |
| PCI DSS | 1년, 최근 3개월 즉시 조회 | 결제 |
| PIPA (KR) | 5년 | 개인정보 처리 기록 |

자동 삭제 job을 매일 돌립니다.

```python
from datetime import timedelta

RETENTION = {
    "audit_log": timedelta(days=365 * 7),     # 7년
    "pii_store": timedelta(days=90),
}

def gc_pii_store():
    cutoff = datetime.now(timezone.utc) - RETENTION["pii_store"]
    pii_store.delete_where(lambda r: r["created_at"] < cutoff)
```

삭제 자체도 audit log에 기록합니다("PII record X was deleted at Y per retention policy").

## Compliance 보고서 자동 생성

Audit log는 사람이 읽을 수 있어야 가치가 있습니다. 정기 보고서를 만듭니다.

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

이 보고서를 보안팀, 컴플라이언스팀, 임원에게 자동 발송하면 사고 발생 전에 이상 패턴이 보입니다.

## Common Mistakes

1. **Application log에 prompt/response 그대로 기록**: PII가 7년치 로그에 남아 GDPR 위반 사유가 됩니다. hash만 audit에 두고 원문은 분리 저장합니다.
2. **append-only를 이름만**: 권한 관리 없이 일반 DB에 두면 사고 시 변조 의심을 피할 수 없습니다. WORM, hash chain 같은 기술적 보호가 필요합니다.
3. **Decision rationale 누락**: "왜 답했는가"가 없으면 사후 분석과 규제 대응이 불가능합니다. retrieval, params, guardrail 결정을 함께 기록합니다.
4. **무한 보존**: "혹시 모르니" 영구 보존하면 GDPR 위반과 저장 비용 폭주가 동시에 발생합니다. 규제별 보존 기간과 자동 삭제 job을 둡니다.
5. **삭제 자체를 기록 안 함**: 누가 언제 무엇을 지웠는지 audit이 없으면 audit log 자체의 무결성이 깨집니다. 삭제도 immutable record로 남깁니다.

## 핵심 요약

- Audit log는 application log와 분리해 schema, 보존 기간, 권한, PII 정책을 모두 다르게 설계합니다.
- 원문 prompt/response는 별도 KMS 암호화 저장소에, audit에는 hash만 둡니다.
- WORM 저장소나 hash chain으로 append-only 무결성을 기술적으로 보장합니다.
- Decision rationale(query, chunks, params, guardrail decision)을 함께 캡처해 사후 재현과 규제 대응이 가능하게 합니다.
- 규제별 보존 기간을 자동 삭제 job으로 강제하고, 삭제 자체도 audit record로 남깁니다.

---

<!-- toc:begin -->
## AI Safety & Guardrails 101 시리즈

- [Ep1 AI 안전이 왜 중요한가](./01-why-ai-safety-matters.md)
- [Ep2 Prompt Injection 방어](./02-prompt-injection-defense.md)
- [Ep3 출력 필터링과 콘텐츠 모더레이션](./03-output-filtering.md)
- [Ep4 PII 탐지와 마스킹](./04-pii-detection-redaction.md)
- [Ep5 Jailbreak 탐지](./05-jailbreak-detection.md)
- [Ep6 Toxicity와 Bias 탐지](./06-toxicity-bias-detection.md)
- [Ep7 Hallucination Guardrail - Grounding 검증](./07-hallucination-guardrails.md)
- [Ep8 Rate Limiting과 남용 방지](./08-rate-limiting-abuse-prevention.md)
- **Ep9 Audit Logging과 컴플라이언스 (현재 글)**
- Ep10 프로덕션 Guardrail 시스템 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [GDPR - Article 30: Records of processing activities](https://gdpr-info.eu/art-30-gdpr/)
- [HIPAA Security Rule - Audit controls](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [SOC 2 - Trust Services Criteria](https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services)
- [AWS S3 Object Lock - Compliance mode](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html)

Tags: AI Safety, Audit Logging, Compliance, GDPR
