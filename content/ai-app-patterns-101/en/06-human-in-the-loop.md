---
title: 'Human-in-the-loop — designing for human intervention'
series: ai-app-patterns-101
episode: 6
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- RAG
- Agent
- Python
last_reviewed: '2026-05-01'
---

# Human-in-the-loop — designing for human intervention

> AI App Patterns 101 (6/6)

Example code: [github.com/yeongseon-books/ai-app-patterns-101](https://github.com/yeongseon-books/ai-app-patterns-101/tree/main/en/06-human-in-the-loop)

Full automation is not always appropriate. Handling sensitive customer data, drafting legally binding documents, or making financial decisions all require a human to review and approve the AI's output before it takes effect. Human-in-the-loop (HITL) is the pattern for inserting human judgment into an otherwise automated pipeline.

Topics:

- when HITL is the right choice
- implementing approval gates
- confidence-based auto/manual branching
- audit logging

---

## When HITL is the right choice

HITL adds latency and cost. Use it when the cost of an unchecked error is high.

**High-stakes decisions**: money transfers, contract generation, personal data processing — anything where a mistake is expensive or irreversible.

**Low model confidence**: route uncertain outputs to a human rather than sending a guess downstream.

**Regulatory requirements**: some industries prohibit fully autonomous AI decisions.

**Trust-building phase**: start with full human review when deploying a new system; reduce the human review rate as confidence in the model accumulates.

---

## Basic approval gate

The simplest HITL pattern is a blocking prompt that waits for human input before the pipeline continues.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

draft_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a customer service representative.\n"
        "Write a draft response to the customer inquiry below.\n"
        "Be polite and professional.",
    ),
    ("human", "Customer inquiry:\n{inquiry}"),
])

draft_chain = draft_prompt | llm | StrOutputParser()

refine_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Revise the draft response based on the reviewer's feedback.\n"
        "Apply the feedback faithfully while maintaining a professional tone.",
    ),
    ("human", "Draft:\n{draft}\n\nFeedback:\n{feedback}"),
])

refine_chain = refine_prompt | llm | StrOutputParser()

def draft_with_human_review(inquiry: str) -> str:
    """Generate draft → human review → optional refinement → final response."""
    draft = draft_chain.invoke({"inquiry": inquiry})
    print(f"\n=== generated draft ===\n{draft}\n")

    print("reviewer options:")
    print("  [1] approve — use the draft as-is")
    print("  [2] revise — provide feedback to improve the draft")
    print("  [3] reject — discard this response")

    choice = input("choice (1/2/3): ").strip()

    if choice == "1":
        return draft
    elif choice == "2":
        feedback = input("enter feedback: ").strip()
        refined = refine_chain.invoke({"draft": draft, "feedback": feedback})
        print(f"\n=== revised response ===\n{refined}")
        return refined
    else:
        print("response rejected")
        return ""

inquiry = "I ordered three weeks ago and my package still hasn't arrived. What happened?"
final_response = draft_with_human_review(inquiry)
if final_response:
    print(f"\n=== final response sent ===\n{final_response}")
```

---

## Confidence-based branching

Ask the LLM to return a confidence score alongside its output. Route low-confidence results to a human reviewer automatically.

```python
import os

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

classify_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Classify the following text and rate your confidence.\n"
        "Return JSON only.\n"
        'Format: {{"category": "category name", "confidence": 0.0-1.0, "reason": "brief reason"}}',
    ),
    ("human", "{text}"),
])

chain = classify_prompt | llm | JsonOutputParser()

CONFIDENCE_THRESHOLD = 0.85

def classify_with_hitl(text: str) -> dict:
    """Route to human review when model confidence is below threshold."""
    result = chain.invoke({"text": text})
    confidence = result.get("confidence", 0.0)

    if confidence >= CONFIDENCE_THRESHOLD:
        result["reviewed_by"] = "auto"
        print(f"auto-classified: {result['category']} (confidence {confidence:.2f})")
    else:
        print(f"low confidence ({confidence:.2f}) — manual review required")
        print(f"AI suggested category: {result['category']}")
        print(f"reason: {result['reason']}")
        human_category = input("enter correct category: ").strip()
        result["category"] = human_category
        result["reviewed_by"] = "human"

    return result

texts = [
    "Q3 2024 revenue increased 23 percent year-over-year.",  # clear case
    "The product was kind of different from what I expected.",  # ambiguous
]

for text in texts:
    print(f"\ntext: {text}")
    result = classify_with_hitl(text)
    print(f"result: {result}")
```

---

## Audit logging

HITL systems require a record of who reviewed what and when. The audit log also becomes training data for improving the model over time.

```python
import json
import os
from datetime import datetime
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

LOG_FILE = Path("audit_log.jsonl")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

generate_prompt = ChatPromptTemplate.from_messages([
    ("system", "Draft a contract clause for the following request."),
    ("human", "{request}"),
])

generate_chain = generate_prompt | llm | StrOutputParser()

def log_event(event_type: str, data: dict) -> None:
    """Append an audit event to the JSONL log file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        **data,
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def contract_clause_with_audit(request: str, reviewer_id: str) -> dict:
    """Generate clause draft → audit log → human approval."""
    draft = generate_chain.invoke({"request": request})
    log_event("draft_generated", {"request": request, "draft": draft})

    print(f"\ndraft:\n{draft}\n")
    approved = input("approve? (y/n): ").strip().lower() == "y"

    if approved:
        log_event("approved", {
            "reviewer_id": reviewer_id,
            "request": request,
            "draft": draft,
        })
        return {"status": "approved", "content": draft}
    else:
        reason = input("rejection reason: ").strip()
        log_event("rejected", {
            "reviewer_id": reviewer_id,
            "request": request,
            "draft": draft,
            "reason": reason,
        })
        return {"status": "rejected", "reason": reason}

result = contract_clause_with_audit(
    request="full refund within 30 days of cancellation",
    reviewer_id="reviewer_001",
)
print(f"\nresult: {result['status']}")
print(f"audit log: {LOG_FILE}")
```

---

## Conclusion

HITL does not mean abandoning automation. High-confidence outputs flow through automatically; low-confidence or high-risk outputs pause for human review. The ratio shifts toward automation as the model proves itself on real traffic. Audit logs close the loop: every human correction is evidence for the next round of fine-tuning or threshold adjustment.

This series covered six core LLM application patterns — chatbot, RAG Q&A, document assistant, agent with tools, workflow automation, and human-in-the-loop. Each pattern stands alone or composes with the others to form more complex systems.

<!-- toc:begin -->
## In this series

- [Chatbot pattern — managing conversation history and state](./01-chatbot-pattern.md)
- [RAG Q&A pattern — document-based question answering](./02-rag-qa-pattern.md)
- [Document assistant — summarization, extraction, classification](./03-document-assistant.md)
- [Agent and tool pattern — autonomous tool selection](./04-agent-tool-pattern.md)
- [Workflow automation — designing multi-step chains](./05-workflow-automation.md)
- **Human-in-the-loop — designing for human intervention (current)**

<!-- toc:end -->

---

## References

- [LangGraph HITL guide](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/)
- [Human-AI interaction design](https://arxiv.org/abs/2108.00018)
- [Confidence calibration](https://en.wikipedia.org/wiki/Calibration_(statistics))

Tags: LLM, RAG, Agent, Python
