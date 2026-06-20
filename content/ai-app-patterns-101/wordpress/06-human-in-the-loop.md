---
title: "바이브코딩을 위한 AI 앱 패턴 (6/6): Human-in-the-Loop"
series: ai-app-patterns-101
episode: 6
language: ko
tags:
- Human-in-the-Loop
- HITL
- Approval Gate
- Confidence Routing
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 앱 패턴 (6/6): Human-in-the-Loop

이 글은 **바이브코딩을 위한 AI 앱 패턴** 시리즈의 마지막 글입니다.

---

바이브코딩으로 AI 앱을 만들다 보면 "AI가 혼자 결정해도 되는 것"과 "사람이 반드시 확인해야 하는 것"의 경계를 어디에 그을지가 중요한 문제가 됩니다. AI가 모든 것을 처리하면 빠르지만 위험하고, 사람이 모든 것을 검토하면 안전하지만 느립니다.

Human-in-the-Loop(HITL) 패턴은 신뢰도를 기준으로 자동 처리, 사람 검토, 자동 거부를 나누는 구조입니다. 높은 신뢰도면 자동으로 처리하고, 중간 신뢰도면 사람에게 검토를 요청하고, 낮은 신뢰도면 자동으로 거부합니다. 이 분기 로직이 효율성과 안전성의 균형을 맞춥니다.

> "완전 자동화와 완전 수동 사이 어딘가에 실제로 작동하는 AI 시스템이 있습니다. 신뢰도 기반 라우팅이 그 균형점을 찾아줍니다."

## 이 글에서 다룰 질문

1. 신뢰도 기반 라우팅에서 임계값은 어떻게 설정하나요?
2. 승인 게이트(Approval Gate)는 어떻게 구현하나요?
3. 감사 로그(Audit Log)는 왜 필요하고 어떻게 만드나요?
4. 검토 큐를 FastAPI로 어떻게 구현하나요?
5. HITL 패턴에서 자주 발생하는 문제는 무엇인가요?

---

## HITL 개입 기준

| 상황 | 처리 방법 | 임계값 예시 |
|------|----------|------------|
| 명확한 높은 신뢰도 | 자동 처리 | confidence >= 0.85 |
| 중간 신뢰도 | 사람 검토 요청 | 0.60 <= confidence < 0.85 |
| 낮은 신뢰도 | 자동 거부 또는 에스컬레이션 | confidence < 0.60 |
| 고위험 결정 | 항상 사람 검토 | 금액, 개인정보, 법적 내용 |

## Before / After: HITL 도입

**Before (AI가 모든 것을 자동 처리)**
```python
def process_request(request: str) -> str:
    result = ai_decide(request)
    execute_action(result)  # 사람 검토 없이 바로 실행
    return result
# 위험: AI가 틀려도 즉시 실행됨
```

**After (신뢰도 기반 라우팅)**
```python
AUTO_APPROVE_THRESHOLD = 0.85
REVIEW_THRESHOLD = 0.60

def ai_content_decision(content: str) -> dict:
    """AI가 콘텐츠를 분류하고 신뢰도를 반환합니다."""
    result = llm.chat(f"""다음 콘텐츠를 분류하고 신뢰도를 평가하세요.
    카테고리: safe, borderline, inappropriate
    JSON으로 반환: {{"category": "...", "confidence": 0.0-1.0, "reason": "..."}}

    콘텐츠: {content}""", response_format={"type": "json_object"})

    return json.loads(result)

def confidence_based_routing(content: str, request_id: str) -> dict:
    """신뢰도에 따라 자동 처리 또는 검토 요청을 결정합니다."""
    decision = ai_content_decision(content)
    confidence = decision["confidence"]

    audit_log(request_id, content, decision)

    if confidence >= AUTO_APPROVE_THRESHOLD:
        return {"action": "auto_approve", "decision": decision, "review_required": False}
    elif confidence >= REVIEW_THRESHOLD:
        review_id = queue_for_review(request_id, content, decision)
        return {"action": "pending_review", "review_id": review_id, "review_required": True}
    else:
        return {"action": "auto_reject", "decision": decision, "review_required": False}
```

## 승인 게이트 구현

```python
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"

@dataclass
class PendingApproval:
    approval_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    content: str = ""
    ai_decision: dict = field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.PENDING
    reviewer_id: str | None = None
    reviewed_at: str | None = None

pending_approvals: dict[str, PendingApproval] = {}

def request_approval(request_id: str, content: str, ai_decision: dict) -> str:
    """검토를 요청하고 approval_id를 반환합니다."""
    approval = PendingApproval(request_id=request_id, content=content, ai_decision=ai_decision)
    pending_approvals[approval.approval_id] = approval
    notify_reviewers(approval)  # 검토자에게 알림
    return approval.approval_id

def process_approval_decision(approval_id: str, decision: str, reviewer_id: str) -> dict:
    """검토자의 결정을 처리합니다."""
    if approval_id not in pending_approvals:
        raise ValueError(f"승인 요청 '{approval_id}'를 찾을 수 없습니다")

    approval = pending_approvals[approval_id]
    approval.status = ApprovalStatus.APPROVED if decision == "approve" else ApprovalStatus.REJECTED
    approval.reviewer_id = reviewer_id
    approval.reviewed_at = datetime.utcnow().isoformat()

    audit_log_decision(approval)
    return {"approved": approval.status == ApprovalStatus.APPROVED}
```

## 감사 로그: 해시 체인으로 무결성 보장

```python
import hashlib
import json

class AuditLogger:
    def __init__(self):
        self.entries = []
        self.last_hash = "genesis"

    def log(self, event: str, data: dict) -> str:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "data": data,
            "previous_hash": self.last_hash
        }
        entry_str = json.dumps(entry, sort_keys=True, ensure_ascii=False)
        current_hash = hashlib.sha256(entry_str.encode()).hexdigest()[:16]
        entry["hash"] = current_hash

        self.entries.append(entry)
        self.last_hash = current_hash
        return current_hash

    def verify_integrity(self) -> bool:
        """로그가 변조되지 않았는지 확인합니다."""
        for i, entry in enumerate(self.entries):
            entry_copy = {k: v for k, v in entry.items() if k != "hash"}
            expected_hash = hashlib.sha256(
                json.dumps(entry_copy, sort_keys=True, ensure_ascii=False).encode()
            ).hexdigest()[:16]
            if entry["hash"] != expected_hash:
                return False
        return True
```

## FastAPI 검토 큐

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ReviewDecision(BaseModel):
    approval_id: str
    decision: str  # "approve" or "reject"
    reviewer_id: str
    comment: str = ""

@app.get("/review/queue")
async def get_review_queue():
    """대기 중인 검토 항목을 반환합니다."""
    pending = [
        {"id": k, "content": v.content[:100], "ai_confidence": v.ai_decision.get("confidence")}
        for k, v in pending_approvals.items()
        if v.status == ApprovalStatus.PENDING
    ]
    return {"items": pending, "total": len(pending)}

@app.post("/review/decide")
async def submit_review(decision: ReviewDecision):
    """검토 결정을 제출합니다."""
    result = process_approval_decision(
        decision.approval_id,
        decision.decision,
        decision.reviewer_id
    )
    return result
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 임계값을 임의로 설정 | 너무 많거나 너무 적은 검토 | 데이터 기반으로 임계값 튜닝 |
| 감사 로그 없음 | 결정 추적 불가, 규정 위반 | 모든 AI 결정과 사람 검토를 로깅 |
| 검토 큐 모니터링 없음 | 검토 지연 발견 불가 | 대기 시간과 큐 크기 알림 설정 |
| 고위험 결정도 자동 처리 | 심각한 오류 발생 | 금액/개인정보/법적 내용은 항상 검토 |

## AI 팁

신뢰도 임계값을 처음 설정할 때는 보수적으로 시작하세요. AUTO_APPROVE_THRESHOLD를 0.95로 높게 잡으면 처음에는 많은 케이스가 수동 검토로 가지만, 감사 로그를 분석해 실제로 자동 처리해도 되는 케이스를 확인한 뒤 임계값을 조정합니다.

```python
def analyze_review_patterns(audit_logs: list[dict]) -> dict:
    """감사 로그를 분석해 임계값 최적화를 제안합니다."""
    auto_approved = [l for l in audit_logs if l["action"] == "auto_approve"]
    human_reviewed = [l for l in audit_logs if l["action"] in ["approved", "rejected"]]

    # 사람이 뒤집은 AI 결정 비율
    overturned = [l for l in human_reviewed if l["human_decision"] != l["ai_recommendation"]]
    overturn_rate = len(overturned) / max(len(human_reviewed), 1)

    return {
        "auto_approve_rate": len(auto_approved) / max(len(audit_logs), 1),
        "overturn_rate": overturn_rate,
        "suggested_threshold": 0.90 if overturn_rate > 0.1 else 0.85
    }
```

## 체크리스트

- [ ] 신뢰도 임계값을 데이터 기반으로 설정했다
- [ ] 모든 AI 결정과 사람 검토를 감사 로그에 기록한다
- [ ] 검토 큐 대기 시간을 모니터링하고 알림을 설정했다
- [ ] 고위험 결정은 신뢰도와 무관하게 항상 사람이 검토한다
- [ ] 감사 로그 무결성을 주기적으로 검증한다

## 처음 질문으로 돌아가기

**신뢰도 임계값 설정 방법은?** 처음에는 보수적으로 높게 설정하고, 감사 로그를 분석해 사람이 뒤집는 비율이 낮은 구간의 임계값을 점차 낮춥니다.

**승인 게이트 구현은?** 승인 요청을 딕셔너리에 저장하고, 검토자가 결정을 제출하면 상태를 업데이트합니다. API 엔드포인트로 검토 큐를 노출합니다.

**감사 로그가 필요한 이유는?** AI 결정이 왜 내려졌는지, 사람이 어떻게 검토했는지를 추적해 규정 준수, 모델 개선, 분쟁 해결에 활용합니다.

**검토 큐 FastAPI 구현은?** GET 엔드포인트로 대기 중인 항목을 조회하고, POST 엔드포인트로 검토 결정을 제출합니다.

**HITL에서 자주 발생하는 문제는?** 검토 큐 적체(너무 많은 항목이 사람 검토를 기다림), 임계값 잘못 설정(너무 많거나 너무 적은 자동 처리), 감사 로그 부재.

## 정리

Human-in-the-Loop 패턴은 AI와 사람의 역할을 신뢰도 기준으로 나누는 구조입니다. 자동 처리, 사람 검토, 자동 거부를 명확히 분리하고, 모든 결정을 감사 로그에 기록하며, 검토 큐를 투명하게 관리하는 것이 핵심입니다. AI 앱의 신뢰성은 완전 자동화가 아니라 적절한 사람 개입에서 나옵니다.

이로써 AI 앱 패턴 시리즈가 완성되었습니다. 챗봇, RAG, 문서 어시스턴트, 에이전트 도구, 워크플로우, HITL — 이 6가지 패턴을 이해하면 대부분의 AI 앱을 바이브코딩으로 만들 수 있습니다.

## 참고 자료

- [AI 앱 패턴 원문: Human-in-the-Loop](../ko/06-human-in-the-loop.md)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 앱 패턴 (1/6): 챗봇 패턴](./01-chatbot-pattern.md)
2. [바이브코딩을 위한 AI 앱 패턴 (2/6): RAG QA 패턴](./02-rag-qa-pattern.md)
3. [바이브코딩을 위한 AI 앱 패턴 (3/6): 문서 어시스턴트](./03-document-assistant.md)
4. [바이브코딩을 위한 AI 앱 패턴 (4/6): 에이전트 도구 패턴](./04-agent-tool-pattern.md)
5. [바이브코딩을 위한 AI 앱 패턴 (5/6): 워크플로우 자동화](./05-workflow-automation.md)
6. **바이브코딩을 위한 AI 앱 패턴 (6/6): Human-in-the-Loop (현재 글)**
<!-- toc:end -->

Tags: Human-in-the-Loop, HITL, Approval Gate, Confidence Routing, 바이브코딩
