---
title: "AI App Patterns 101 (5/6): Workflow automation — designing multi-step chains"
series: ai-app-patterns-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- RAG
- Agent
- Python
last_reviewed: '2026-05-15'
seo_description: Workflow automation removes model choice and replaces it with a pipeline
  that follows human-defined stages and data contracts.
---

# AI App Patterns 101 (5/6): Workflow automation — designing multi-step chains

When a task has predictable stages, giving the model more freedom usually makes the system harder to trust. A workflow earns its keep by fixing the handoff points, the intermediate data shape, and the places where failures must be surfaced.

This is the 5th post in the AI App Patterns 101 series. Here we cover how to design multi-step LLM workflows with explicit stages and clean data contracts.

![Sequential handoff across stages](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/05/05-01-sequential-handoff-across-stages.en.png)
*Sequential handoff across stages*
> Workflow automation removes model choice and replaces it with a pipeline that follows human-defined stages and data contracts.

## Questions to Keep in Mind

- When is a multi-step chain just a sequence, and when does it need routing?
- What breaks downstream when intermediate result types are not fixed?
- Where should workflow automation log failures so they are not hidden by the final output?

## Sequential chains

### Sequential handoff across stages

### DAG style branching with parallel work

![DAG style branching with parallel work](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/05/05-02-dag-style-branching-with-parallel-work.en.png)

*DAG style branching with parallel work*
LCEL's `|` operator connects stages: the left stage's output becomes the right stage's input.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

translate_prompt = ChatPromptTemplate.from_messages([
    ("system", "Translate the following text to {target_language}. Return only the translation."),
    ("human", "{text}"),
])

summarize_prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize the following text in two sentences."),
    ("human", "{text}"),
])

title_prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate a one-line title for the following text."),
    ("human", "{text}"),
])

str_parser = StrOutputParser()

def make_pipeline(target_language: str):
    """Return translate → summarize → title functions for the given language."""

    def translate(inputs: dict) -> dict:
        translated = (translate_prompt | llm | str_parser).invoke({
            "text": inputs["text"],
            "target_language": target_language,
        })
        return {"text": translated}

    def summarize(inputs: dict) -> dict:
        summary = (summarize_prompt | llm | str_parser).invoke(inputs)
        return {"text": summary}

    def make_title(inputs: dict) -> str:
        return (title_prompt | llm | str_parser).invoke(inputs)

    return translate, summarize, make_title

article = """
Artificial intelligence is transforming the way businesses operate.
Companies across industries are adopting AI tools to automate repetitive tasks,
improve decision-making, and personalize customer experiences.
The healthcare sector uses AI to assist in diagnosis and drug discovery.
In finance, AI powers fraud detection and algorithmic trading.
As AI becomes more capable, organizations must also address ethical considerations
such as bias, transparency, and data privacy.
"""

translate_fn, summarize_fn, title_fn = make_pipeline("Korean")

step1 = translate_fn({"text": article})
print(f"translation:\n{step1['text']}\n")

step2 = summarize_fn(step1)
print(f"summary:\n{step2['text']}\n")

step3 = title_fn(step2)
print(f"title: {step3}")
```

---

## Routing — branching based on classification

### Classification driven routing

![Classification driven routing](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/05/05-03-classification-driven-routing.en.png)

*Classification driven routing*
### Approval gate and retry recovery

![Approval gate and retry recovery](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/05/05-04-approval-gate-and-retry-recovery.en.png)

*Approval gate and retry recovery*
Classify the input first, then route it to the appropriate chain. The classifier's output is the only dependency between the two stages.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)
str_parser = StrOutputParser()

classify_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Classify the following customer inquiry.\n"
        "Categories: BILLING, TECHNICAL, GENERAL\n"
        "Return the category name only. No other text.",
    ),
    ("human", "{inquiry}"),
])
classify_chain = classify_prompt | llm | str_parser

billing_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a billing specialist.\n"
        "Handle refunds, invoices, and charge-related inquiries.\n"
        "Be accurate and reassuring.",
    ),
    ("human", "{inquiry}"),
])

technical_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a technical support engineer.\n"
        "Handle bugs, errors, and how-to questions.\n"
        "Guide users step by step.",
    ),
    ("human", "{inquiry}"),
])

general_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a customer service representative.\n"
        "Handle general inquiries politely and helpfully.",
    ),
    ("human", "{inquiry}"),
])

billing_chain = billing_prompt | llm | str_parser
technical_chain = technical_prompt | llm | str_parser
general_chain = general_prompt | llm | str_parser

def route_and_respond(inquiry: str) -> dict:
    """Classify → route → generate specialist response."""
    category = classify_chain.invoke({"inquiry": inquiry}).strip().upper()

    chains = {
        "BILLING": billing_chain,
        "TECHNICAL": technical_chain,
        "GENERAL": general_chain,
    }
    chain = chains.get(category, general_chain)
    response = chain.invoke({"inquiry": inquiry})

    return {"category": category, "response": response}

test_inquiries = [
    "My bill doubled this month without any explanation. Please check.",
    "The app keeps crashing when I open it. What should I do?",
    "What are your business hours?",
]

for inquiry in test_inquiries:
    print(f"\ninquiry: {inquiry}")
    result = route_and_respond(inquiry)
    print(f"category: {result['category']}")
    print(f"response: {result['response']}")
```

---

## Multi-stage data transformation pipeline

### Code review artifact contract

![Code review artifact contract](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/05/05-05-code-review-artifact-contract.en.png)

*Code review artifact contract*
Each stage transforms the previous stage's output. The code review pipeline below shows three chained transformations: analysis → suggestions → report.

```python
import os

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

analyze_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Analyze the following code and return JSON only.\n"
        'Format: {{"language": "lang", "purpose": "purpose", "issues": ["issue list"], "score": 1-10}}',
    ),
    ("human", "Code:\n{code}"),
])

suggest_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Based on the code analysis, provide specific improvements.\n"
        "Include corrected code examples for each issue.",
    ),
    ("human", "Analysis:\n{analysis}\n\nOriginal code:\n{code}"),
])

report_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Summarize the code review into a concise report.\n"
        "Structure: overall assessment, key improvements, recommended actions.",
    ),
    ("human", "Analysis:\n{analysis}\n\nSuggestions:\n{suggestions}"),
])

analyze_chain = analyze_prompt | llm | JsonOutputParser()
suggest_chain = suggest_prompt | llm | StrOutputParser()
report_chain = report_prompt | llm | StrOutputParser()

def code_review_pipeline(code: str) -> dict:
    """Code analysis → suggestions → report."""
    analysis = analyze_chain.invoke({"code": code})
    print(f"  analysis done: score {analysis.get('score')}/10, {len(analysis.get('issues', []))} issues")

    suggestions = suggest_chain.invoke({
        "analysis": str(analysis),
        "code": code,
    })
    print("  suggestions done")

    report = report_chain.invoke({
        "analysis": str(analysis),
        "suggestions": suggestions,
    })
    print("  report done")

    return {"analysis": analysis, "suggestions": suggestions, "report": report}

sample_code = """
def get_user(id):
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {id}")
    result = cursor.fetchone()
    conn.close()
    return result
"""

print("running code review pipeline...")
result = code_review_pipeline(sample_code)
print(f"\n=== final report ===\n{result['report']}")
```

---

## What to notice in this code

- `code_review_pipeline()` shows three explicit handoffs: JSON analysis, free-form suggestions, and a final condensed report.
- The intermediate `analysis` object acts as a contract, which makes logging and validation much easier than passing only raw strings.
- This structure is friendly to operational controls such as approval, routing, and retry policies.

---

## Where engineers get confused

- More stages are not automatically better; every extra call adds cost, latency, and another failure surface.
- Passing only raw strings between stages makes later validation and branching harder than passing structured dictionaries.
- The real line between a workflow and an agent is not tool usage but whether the execution path changes at runtime.

---

## Checklist

- [ ] The summary output feeds the next stage
- [ ] The classifier returns one value from a limited category set
- [ ] The tagging step uses earlier stage results, not only the raw text
- [ ] The final output is a structured object that still contains intermediate artifacts

---

## Workflow orchestration and state transitions

### Orchestrator with stage state

When operating a multi-step chain, record success and failure of each stage in a structured log. The example below is a minimal orchestrator with state transition events.

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class StageEvent:
    stage: str
    status: str
    timestamp: str
    detail: str = ""

@dataclass
class WorkflowRun:
    run_id: str
    input_text: str
    events: list[StageEvent] = field(default_factory=list)
    outputs: dict = field(default_factory=dict)

    def mark(self, stage: str, status: str, detail: str = ""):
        self.events.append(StageEvent(
            stage=stage,
            status=status,
            timestamp=datetime.utcnow().isoformat(),
            detail=detail,
        ))

def run_workflow(text: str) -> WorkflowRun:
    run = WorkflowRun(run_id='wf-001', input_text=text)

    run.mark('classify', 'started')
    category = 'TECHNICAL'
    run.outputs['category'] = category
    run.mark('classify', 'completed', detail=f'category={category}')

    run.mark('summarize', 'started')
    summary = f'Summary: {text[:100]}...'
    run.outputs['summary'] = summary
    run.mark('summarize', 'completed')

    run.mark('response', 'started')
    response = f'[{category}] {summary}'
    run.outputs['response'] = response
    run.mark('response', 'completed')

    return run
```

With event logs, a failure no longer means "no final output and no clue." You can see exactly which stage succeeded, which failed, and restart from the correct point.

### Operational check: retry and idempotency

Workflow automation without retry design is incomplete. Ensure the same input arriving twice does not trigger duplicate delivery:

- `idempotency_key`: external request ID or `(customer_id, request_ts)` hash
- `retry_policy`: per-stage `max_retries`, backoff, timeout
- `dead_letter_queue`: isolation store for repeatedly failing items

Without these, automation during incidents causes duplicate execution instead of aiding recovery.

## Separating workflow API from execution

When a sequential chain runs only in a single process, failure recovery and scaling are difficult. Separate the trigger API from the execution worker.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class WorkflowRequest(BaseModel):
    request_id: str
    text: str

work_queue: list[dict] = []

@app.post('/workflow/submit')
def submit(req: WorkflowRequest):
    work_queue.append({'request_id': req.request_id, 'text': req.text, 'status': 'queued'})
    return {'request_id': req.request_id, 'status': 'queued'}
```

```python
def worker_once():
    if not work_queue:
        return None

    item = work_queue.pop(0)
    run = run_workflow(item['text'])
    return {
        'request_id': item['request_id'],
        'status': 'completed',
        'outputs': run.outputs,
        'events': [e.__dict__ for e in run.events],
    }
```

### Approval gate states

When the pipeline requires human approval, add explicit states:

```text
queued -> running -> waiting_approval -> approved -> completed
queued -> running -> waiting_approval -> rejected
queued -> running -> failed
```

These states let a dashboard answer "why is it stuck?" at a glance.

### Operational metrics

Track process metrics alongside model quality metrics:

- `p95_stage_latency`: per-stage latency
- `reprocess_rate`: fraction of items reprocessed
- `approval_wait_time`: human approval queue time
- `dead_letter_count`: repeatedly failing items

These four together tell you whether automation is increasing efficiency or just adding complexity.

## Extending to a LangGraph-style state machine

As workflows grow, a state machine becomes easier to manage than sequential function calls. Separate responsibility per node and share a typed state object.

```python
from typing import TypedDict

class FlowState(TypedDict):
    request_id: str
    inquiry: str
    category: str
    summary: str
    answer: str
    needs_approval: bool

def node_classify(state: FlowState) -> FlowState:
    state['category'] = 'BILLING'
    state['needs_approval'] = state['category'] == 'BILLING'
    return state

def node_summarize(state: FlowState) -> FlowState:
    state['summary'] = state['inquiry'][:120]
    return state

def node_answer(state: FlowState) -> FlowState:
    state['answer'] = f"[{state['category']}] {state['summary']}"
    return state
```

Why a state machine wins in operations:

- Adding a stage reduces blast radius on existing code
- Restart from the failed node without re-running earlier stages
- Dashboards can display the current node directly

## Failure recovery runbook: stage-level resume

Default failure response should be stage-level resume, not full re-run. Save each stage's output artifact:

```text
artifact://run_id/classify.json
artifact://run_id/summary.txt
artifact://run_id/response.txt
```

```python
def resume_from_stage(run_id: str, stage: str):
    if stage == 'summarize':
        classify = load_artifact(run_id, 'classify.json')
        return rerun_summarize_and_after(run_id, classify)
    if stage == 'response':
        summary = load_artifact(run_id, 'summary.txt')
        return rerun_response_only(run_id, summary)
    raise ValueError('unsupported stage')
```

Limiting the re-execution unit to a single stage cuts incident response time and prevents secondary failures like duplicate delivery.

### Per-stage timeout policy

A single global timeout for a long workflow makes it hard to find the bottleneck stage. Set per-stage limits (e.g. classify 3s, summarize 8s, response 8s) to narrow latency causes quickly.

### Pre-deployment dry run

Before deploying workflow changes, run a dry run with 100 sample items and compare per-stage success rate and latency against the baseline. Deploying without a dry-run report makes it easy to underestimate impact.

---

## Conclusion

Keep each stage focused on one responsibility. A stage that does too much is hard to test, hard to debug, and hard to replace. When a stage's output is ambiguous — a free-form string where structured data was expected — the next stage often fails silently. Define the output format for every stage, validate it, and only then pass it forward.

The final post covers human-in-the-loop design: inserting human review and approval gates into otherwise automated pipelines.

## Answering the Opening Questions

- **When is a multi-step chain just a sequence, and when does it need routing?**
  A sequence is enough when every input follows the same steps; routing is needed when different input types require different paths or handlers.

- **What breaks downstream when intermediate result types are not fixed?**
  If intermediate types are not fixed, the next step may miss fields or confuse strings with JSON and fail quietly.

- **Where should workflow automation log failures so they are not hidden by the final output?**
  Log each step input, output, routing decision, and exception separately so the final output does not hide the actual failure point.

<!-- toc:begin -->
## In this series

- [AI App Patterns 101 (1/6): Chatbot pattern — managing conversation history and state](./01-chatbot-pattern.md)
- [AI App Patterns 101 (2/6): RAG Q&A pattern — document-based question answering](./02-rag-qa-pattern.md)
- [AI App Patterns 101 (3/6): Document assistant — summarization, extraction, classification](./03-document-assistant.md)
- [AI App Patterns 101 (4/6): Agent and tool pattern — autonomous tool selection](./04-agent-tool-pattern.md)
- **AI App Patterns 101 (5/6): Workflow automation — designing multi-step chains (current)**
- AI App Patterns 101 (6/6): Human-in-the-loop — designing for human intervention (upcoming)

<!-- toc:end -->

---

## References

- [LangChain LCEL](https://python.langchain.com/docs/expression_language/)
- [LangChain routing](https://python.langchain.com/docs/expression_language/how_to/routing/)
- [RunnableParallel](https://python.langchain.com/docs/expression_language/primitives/parallel/)

Tags: LLM, RAG, Agent, Python
