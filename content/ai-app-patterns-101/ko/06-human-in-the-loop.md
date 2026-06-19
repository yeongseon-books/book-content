---
series: ai-app-patterns-101
episode: 6
title: "AI App Patterns 101 (6/6): Human-in-the-Loop 패턴"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - HumanInTheLoop
  - ApprovalGate
  - AuditLog
  - LLM
  - Safety
seo_description: 승인 게이트, 신뢰도 기반 라우팅, 감사 로그, 검토 대기열 API까지 Human-in-the-Loop 패턴의 프로덕션 구현을 정리합니다
last_reviewed: '2026-06-20'
---

# AI App Patterns 101 (6/6): Human-in-the-Loop 패턴

AI가 모든 결정을 자율적으로 내리도록 하면 높은 위험을 수반합니다. Human-in-the-Loop(HITL) 패턴은 AI의 결정에 사람이 개입하는 지점을 명시적으로 설계하는 방식입니다. 신뢰도가 낮거나 고위험 작업이 감지되면 자동으로 사람 검토 대기열에 넣고, 승인 후에만 다음 단계를 진행합니다. HITL은 안전성과 자동화 효율 사이의 균형을 맞추는 설계 철학입니다.

이 글은 AI App Patterns 101 시리즈의 6번째 글입니다.

![Human-in-the-Loop 패턴 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/06/06-01-concept-at-a-glance.ko.png)
*승인 게이트와 신뢰도 라우팅이 결합된 Human-in-the-Loop 아키텍처*

## 이 글에서 다룰 문제

- 어떤 기준으로 AI 결정에 사람이 개입해야 할지 판단할 수 있을까요?
- 승인 게이트를 코드로 어떻게 구현할 수 있을까요?
- 신뢰도 기반 라우팅에서 임계값은 어떻게 설정해야 할까요?
- 감사 로그는 HITL 시스템에서 왜 필수적일까요?
- 검토 대기열의 우선순위는 어떤 기준으로 정해야 할까요?

## 핵심 개념 한 줄 정리

- **Approval Gate**: AI가 고위험 작업을 실행하기 전에 사람의 승인을 기다리는 체크포인트입니다.
- **Confidence Routing**: AI 출력의 신뢰도에 따라 자동 처리와 사람 검토로 분기하는 패턴입니다.
- **Review Queue**: 사람 검토가 필요한 항목을 우선순위와 함께 관리하는 대기열입니다.
- **Audit Log**: 모든 AI 결정과 사람 개입 이력을 변경 불가능한 형태로 기록하는 시스템입니다.
- **Escalation**: 자동화 처리 실패나 고위험 감지 시 상위 검토자에게 전달하는 프로세스입니다.

## HITL 개입 기준 설계

모든 결정에 사람이 개입하면 자동화의 이점이 사라집니다. 다음 기준을 기반으로 개입 필요성을 판단합니다.

| 기준 | 자동 처리 | 사람 검토 |
|---|---|---|
| AI 신뢰도 | 0.85 이상 | 0.85 미만 |
| 영향 범위 | 단일 사용자 | 다수 사용자 또는 시스템 |
| 가역성 | 쉽게 되돌릴 수 있음 | 되돌리기 어렵거나 불가능 |
| 금액/위험 | 소액, 저위험 | 고액, 고위험 |
| 법적 의무 | 해당 없음 | 규정 준수 검토 필요 |

## 실습 1: 승인 게이트 구현

고위험 AI 결정을 차단하고 사람 승인을 기다리는 게이트입니다.

```python
import uuid
import json
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


@dataclass
class PendingApproval:
    approval_id: str
    action_type: str
    payload: dict
    ai_recommendation: str
    confidence: float
    risk_level: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    reviewer: str | None = None
    review_note: str | None = None
    resolved_at: str | None = None


# 인메모리 승인 대기열 (프로덕션에서는 DB 사용)
approval_queue: dict[str, PendingApproval] = {}


def request_approval(
    action_type: str,
    payload: dict,
    ai_recommendation: str,
    confidence: float,
    risk_level: str = "medium",
) -> PendingApproval:
    """AI 결정을 승인 대기열에 추가합니다."""
    approval = PendingApproval(
        approval_id=str(uuid.uuid4()),
        action_type=action_type,
        payload=payload,
        ai_recommendation=ai_recommendation,
        confidence=confidence,
        risk_level=risk_level,
    )
    approval_queue[approval.approval_id] = approval
    return approval


def process_approval_decision(
    approval_id: str,
    approved: bool,
    reviewer: str,
    note: str = "",
) -> PendingApproval:
    """검토자의 승인/거부 결정을 처리합니다."""
    approval = approval_queue.get(approval_id)
    if not approval:
        raise ValueError(f"승인 ID를 찾을 수 없습니다: {approval_id}")

    if approval.status != ApprovalStatus.PENDING:
        raise ValueError(f"이미 처리된 승인입니다: {approval.status.value}")

    approval.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
    approval.reviewer = reviewer
    approval.review_note = note
    approval.resolved_at = datetime.utcnow().isoformat()

    return approval
```

## 실습 2: 신뢰도 기반 라우팅

AI 결정의 신뢰도에 따라 자동 처리와 사람 검토로 분기합니다.

```python
from openai import OpenAI
import json

client = OpenAI()

AUTO_APPROVE_THRESHOLD = 0.85
REVIEW_REQUIRED_THRESHOLD = 0.60


def ai_content_decision(content: str) -> dict:
    """콘텐츠에 대한 AI 결정과 신뢰도를 반환합니다."""
    prompt = f"""다음 사용자 생성 콘텐츠를 평가하세요.

콘텐츠: {content}

평가 기준:
- 허위 정보 포함 여부
- 유해 콘텐츠 여부
- 저작권 침해 가능성

JSON으로만 응답: {{
  "decision": "approve/reject/uncertain",
  "confidence": 0.0-1.0,
  "reasons": ["이유1", "이유2"],
  "risk_level": "low/medium/high"
}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def confidence_based_routing(
    content_id: str,
    content: str,
) -> dict:
    """신뢰도에 따라 자동 처리 또는 사람 검토로 라우팅합니다."""
    ai_result = ai_content_decision(content)
    confidence = ai_result.get("confidence", 0.0)
    decision = ai_result.get("decision", "uncertain")

    if confidence >= AUTO_APPROVE_THRESHOLD and decision == "approve":
        # 고신뢰도 승인: 자동 처리
        return {
            "content_id": content_id,
            "route": "auto_approved",
            "confidence": confidence,
            "action": "publish",
            "ai_result": ai_result,
        }

    elif confidence >= REVIEW_REQUIRED_THRESHOLD:
        # 중간 신뢰도: 사람 검토
        approval = request_approval(
            action_type="content_moderation",
            payload={"content_id": content_id, "content": content[:500]},
            ai_recommendation=decision,
            confidence=confidence,
            risk_level=ai_result.get("risk_level", "medium"),
        )
        return {
            "content_id": content_id,
            "route": "human_review",
            "approval_id": approval.approval_id,
            "confidence": confidence,
            "ai_result": ai_result,
        }

    else:
        # 낮은 신뢰도 또는 불확실: 에스컬레이션
        approval = request_approval(
            action_type="content_escalation",
            payload={"content_id": content_id, "content": content[:500]},
            ai_recommendation="uncertain",
            confidence=confidence,
            risk_level="high",
        )
        return {
            "content_id": content_id,
            "route": "escalated",
            "approval_id": approval.approval_id,
            "confidence": confidence,
            "ai_result": ai_result,
        }
```

## 실습 3: 감사 로그 시스템

모든 AI 결정과 사람 개입을 변경 불가능한 형태로 기록합니다.

```python
import hashlib
import json
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class AuditEntry:
    entry_id: str
    timestamp: str
    actor: str  # "ai" or 검토자 이름
    action: str
    subject_id: str
    subject_type: str
    decision: str
    confidence: float | None
    metadata: dict
    previous_hash: str
    entry_hash: str = ""

    def compute_hash(self) -> str:
        """항목 내용과 이전 해시를 포함해 해시를 계산합니다."""
        content = json.dumps(
            {
                "entry_id": self.entry_id,
                "timestamp": self.timestamp,
                "actor": self.actor,
                "action": self.action,
                "subject_id": self.subject_id,
                "decision": self.decision,
                "previous_hash": self.previous_hash,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        return hashlib.sha256(content.encode()).hexdigest()


class AuditLogger:
    """해시 체인으로 연결된 변조 방지 감사 로그입니다."""

    def __init__(self):
        self._entries: list[AuditEntry] = []
        self._last_hash: str = "GENESIS"

    def log(
        self,
        actor: str,
        action: str,
        subject_id: str,
        subject_type: str,
        decision: str,
        confidence: float | None = None,
        metadata: dict | None = None,
    ) -> AuditEntry:
        entry = AuditEntry(
            entry_id=str(len(self._entries) + 1).zfill(8),
            timestamp=datetime.utcnow().isoformat(),
            actor=actor,
            action=action,
            subject_id=subject_id,
            subject_type=subject_type,
            decision=decision,
            confidence=confidence,
            metadata=metadata or {},
            previous_hash=self._last_hash,
        )
        entry.entry_hash = entry.compute_hash()
        self._last_hash = entry.entry_hash
        self._entries.append(entry)
        return entry

    def verify_integrity(self) -> bool:
        """해시 체인 무결성을 검증합니다."""
        prev_hash = "GENESIS"
        for entry in self._entries:
            if entry.previous_hash != prev_hash:
                return False
            expected_hash = entry.compute_hash()
            if entry.entry_hash != expected_hash:
                return False
            prev_hash = entry.entry_hash
        return True

    def get_entries(self, subject_id: str | None = None) -> list[AuditEntry]:
        """감사 로그 항목을 조회합니다."""
        if subject_id:
            return [e for e in self._entries if e.subject_id == subject_id]
        return list(self._entries)


# 전역 감사 로거
audit_logger = AuditLogger()
```

## 실습 4: 검토 대기열 API

사람 검토자가 대기 중인 항목을 조회하고 처리하는 API입니다.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class ReviewDecision(BaseModel):
    approved: bool
    reviewer: str
    note: str = ""


@app.get("/review/queue")
async def get_review_queue(risk_level: str | None = None):
    """검토 대기 중인 항목 목록을 반환합니다."""
    pending = [
        {
            "approval_id": a.approval_id,
            "action_type": a.action_type,
            "risk_level": a.risk_level,
            "confidence": a.confidence,
            "created_at": a.created_at,
            "ai_recommendation": a.ai_recommendation,
        }
        for a in approval_queue.values()
        if a.status == ApprovalStatus.PENDING
        and (risk_level is None or a.risk_level == risk_level)
    ]

    # 위험도와 시간순 정렬 (high > medium > low, 오래된 것 먼저)
    risk_order = {"high": 0, "medium": 1, "low": 2}
    pending.sort(
        key=lambda x: (risk_order.get(x["risk_level"], 9), x["created_at"])
    )
    return {"total": len(pending), "items": pending}


@app.post("/review/{approval_id}")
async def submit_review_decision(
    approval_id: str,
    decision: ReviewDecision,
):
    """검토자의 승인/거부 결정을 처리합니다."""
    try:
        updated = process_approval_decision(
            approval_id=approval_id,
            approved=decision.approved,
            reviewer=decision.reviewer,
            note=decision.note,
        )
        # 감사 로그 기록
        audit_logger.log(
            actor=decision.reviewer,
            action="human_review",
            subject_id=approval_id,
            subject_type="approval",
            decision="approved" if decision.approved else "rejected",
            metadata={"note": decision.note},
        )
        return {
            "approval_id": approval_id,
            "status": updated.status.value,
            "reviewer": updated.reviewer,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/audit/{subject_id}")
async def get_audit_trail(subject_id: str):
    """특정 대상의 감사 이력을 조회합니다."""
    entries = audit_logger.get_entries(subject_id)
    return {
        "subject_id": subject_id,
        "entries": [
            {
                "timestamp": e.timestamp,
                "actor": e.actor,
                "action": e.action,
                "decision": e.decision,
            }
            for e in entries
        ],
        "integrity_valid": audit_logger.verify_integrity(),
    }
```

## 운영 체크리스트

- [ ] 자동 처리와 사람 검토 임계값이 명문화되어 있습니다.
- [ ] 모든 AI 결정과 사람 개입이 감사 로그에 기록됩니다.
- [ ] 검토 대기열에 SLA(예: 고위험 4시간 내 처리)가 설정되어 있습니다.
- [ ] 에스컬레이션 경로가 명확히 정의되어 있습니다.
- [ ] 감사 로그 무결성을 정기적으로 검증합니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| HITL 개입 기준 미문서화 | 검토자마다 다른 판단 기준 적용 | 임계값을 코드와 문서에 동시 명시 |
| 감사 로그 변조 가능 | 감사 역할 상실 | 해시 체인 또는 append-only 저장소 사용 |
| 검토 대기열 우선순위 없음 | 고위험 항목이 오래 대기 | 위험도 기반 정렬 및 SLA 알림 구현 |
| 승인 없이 고위험 작업 실행 | 되돌리기 어려운 오류 발생 | 모든 고위험 작업에 승인 게이트 필수 |
| 에스컬레이션 경로 미설정 | 낮은 신뢰도 항목이 무한 대기 | escalated 상태와 상위 검토자 알림 구현 |

## 처음 질문으로 돌아가기

- **어떤 기준으로 AI 결정에 사람이 개입해야 할지 판단할 수 있을까요?**
  신뢰도, 영향 범위, 가역성, 금액/위험 수준, 법적 의무 다섯 가지 기준을 조합해 판단합니다. 이 기준을 코드로 명문화해 일관된 라우팅이 이루어지도록 해야 합니다.

- **신뢰도 기반 라우팅에서 임계값은 어떻게 설정해야 할까요?**
  처음에는 보수적으로(자동 처리 임계값을 높게) 시작하고, 실제 운영 데이터를 보며 임계값을 조정합니다. 일반적으로 0.85 이상 자동 처리, 0.60-0.85 사람 검토, 0.60 미만 에스컬레이션이 좋은 출발점입니다.

- **감사 로그는 HITL 시스템에서 왜 필수적일까요?**
  규정 준수 요구사항을 충족하고, 분쟁 발생 시 결정 근거를 제공합니다. 모델 성능 드리프트를 감지하고 HITL 임계값을 재조정하는 데이터 소스가 됩니다. 해시 체인 구조로 감사 로그 자체의 변조를 방지해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI App Patterns 101 (1/6): Chatbot 패턴](./01-chatbot-pattern.md)
- [AI App Patterns 101 (2/6): RAG QA 패턴](./02-rag-qa-pattern.md)
- [AI App Patterns 101 (3/6): Document Assistant 패턴](./03-document-assistant.md)
- [AI App Patterns 101 (4/6): Agent Tool 패턴](./04-agent-tool-pattern.md)
- [AI App Patterns 101 (5/6): Workflow Automation 패턴](./05-workflow-automation.md)
- **AI App Patterns 101 (6/6): Human-in-the-Loop 패턴 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Google — Human-AI Interaction Guidebook](https://pair.withgoogle.com/guidebook/)
- [Microsoft — Responsible AI](https://www.microsoft.com/en-us/ai/responsible-ai)
- [FastAPI — Routing](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [NIST — AI Risk Management Framework](https://www.nist.gov/artificial-intelligence)
- [book-examples — ai-app-patterns-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/ai-app-patterns-101/ko)

Tags: HumanInTheLoop, ApprovalGate, AuditLog, LLM, Safety
