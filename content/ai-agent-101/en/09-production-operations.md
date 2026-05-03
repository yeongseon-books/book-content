---
title: Production Operations
series: ai-agent-101
episode: 9
language: en
status: draft
targets:
  tistory: false
  hashnode: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Operations
- Monitoring
- Observability
last_reviewed: '2026-05-02'
---

# Production Operations

> AI Agent 101 Series (9/10)

When you deploy agents to production, new problems arise. You need to monitor how much it costs, how long responses take, where it fails, and which tools are called most frequently.

The core of agent operations is observability. You must track all agent steps, measure cost and latency, and detect anomalies. Scaling strategies and cost optimization are also important.

This article covers agent observability, cost tracking, latency optimization, scaling patterns, and production checklists.

---
## Observability

Production agents must be traceable: "why did it answer this way?" must be answerable. Logs, metrics, and traces are the three core axes.

### Structured Logging

Plaintext logs are hard to parse and query. JSON-structured logs are the standard.

```python
import logging
import json
from datetime import datetime
from typing import Any

class StructuredLogger:
    """Structured logger."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)

    def log(self, level: str, event: str, **fields):
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "event": event,
            **fields
        }
        self.logger.info(json.dumps(record, default=str))

    def info(self, event: str, **fields):
        self.log("INFO", event, **fields)

    def error(self, event: str, **fields):
        self.log("ERROR", event, **fields)


# Example usage
logger = StructuredLogger("agent")
logger.info(
    "tool_call_completed",
    request_id="req_123",
    tool="get_weather",
    args={"city": "Seoul"},
    duration_ms=234,
    success=True
)
```

Structured logs query directly in ELK, Datadog, and CloudWatch.

### Distributed Tracing

A single agent request spans many LLM and tool calls. Traces visualize the full path.

```python
from contextlib import contextmanager
import uuid
import time

class TraceContext:
    """Simple distributed tracing."""

    def __init__(self):
        self.trace_id = str(uuid.uuid4())
        self.spans = []
        self._current_parent = None

    @contextmanager
    def span(self, name: str, **attributes):
        span_id = str(uuid.uuid4())
        parent_id = self._current_parent
        start = time.time()

        self._current_parent = span_id
        try:
            yield span_id
            status = "ok"
            error = None
        except Exception as e:
            status = "error"
            error = str(e)
            raise
        finally:
            self._current_parent = parent_id
            self.spans.append({
                "span_id": span_id,
                "parent_id": parent_id,
                "trace_id": self.trace_id,
                "name": name,
                "start": start,
                "duration_ms": (time.time() - start) * 1000,
                "status": status,
                "error": error,
                "attributes": attributes
            })


# Example usage
trace = TraceContext()

with trace.span("agent_request", user_id="u_456"):
    with trace.span("llm_planning", model="gpt-4"):
        plan = call_llm(user_input)

    with trace.span("tool_execution", tool="search"):
        result = search_tool(plan["query"])

    with trace.span("llm_synthesis", model="gpt-4"):
        answer = call_llm(result)

# Send trace.spans to OpenTelemetry, Jaeger, etc.
```

Using OpenTelemetry standards keeps you compatible with LangSmith and Datadog APM.

### Core Metrics

```python
from collections import defaultdict
import threading

class MetricsCollector:
    """Metrics collector."""

    def __init__(self):
        self._counters = defaultdict(int)
        self._timers = defaultdict(list)
        self._lock = threading.Lock()

    def increment(self, name: str, value: int = 1, **tags):
        key = self._make_key(name, tags)
        with self._lock:
            self._counters[key] += value

    def timing(self, name: str, value_ms: float, **tags):
        key = self._make_key(name, tags)
        with self._lock:
            self._timers[key].append(value_ms)

    def _make_key(self, name: str, tags: dict) -> str:
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"

    def report(self) -> dict:
        with self._lock:
            return {
                "counters": dict(self._counters),
                "timers": {
                    k: {
                        "count": len(v),
                        "avg_ms": sum(v) / len(v),
                        "p95_ms": sorted(v)[int(len(v) * 0.95)] if v else 0
                    }
                    for k, v in self._timers.items()
                }
            }


# Example usage — core metrics to track
metrics = MetricsCollector()
metrics.increment("agent.requests", status="success")
metrics.increment("agent.tool_calls", tool="search")
metrics.increment("agent.errors", type="timeout")
metrics.timing("agent.request.duration", 1234, model="gpt-4")
metrics.timing("agent.tool.duration", 234, tool="search")
```

Core metrics: request count, success/failure rate, latency p50/p95/p99, token usage, cost.

## Cost Tracking and Limits

LLM cost is the biggest variable in operations. Set per-user/org limits.

```python
from datetime import datetime, timedelta

class BudgetEnforcer:
    """Budget enforcement."""

    PRICING = {
        "gpt-4": {"prompt": 0.03 / 1000, "completion": 0.06 / 1000},
        "gpt-3.5-turbo": {"prompt": 0.0015 / 1000, "completion": 0.002 / 1000}
    }

    def __init__(self):
        # Per-user daily usage
        self._usage = defaultdict(lambda: {"date": None, "spent_usd": 0.0})
        self._limits = {}  # user_id -> daily_limit_usd

    def set_limit(self, user_id: str, daily_limit_usd: float):
        self._limits[user_id] = daily_limit_usd

    def check_and_record(
        self,
        user_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> bool:
        """Check budget and record usage. False = block."""
        today = datetime.utcnow().date()
        usage = self._usage[user_id]

        # Reset on date change
        if usage["date"] != today:
            usage["date"] = today
            usage["spent_usd"] = 0.0

        # Estimated cost
        cost = (
            prompt_tokens * self.PRICING[model]["prompt"] +
            completion_tokens * self.PRICING[model]["completion"]
        )

        limit = self._limits.get(user_id, float("inf"))
        if usage["spent_usd"] + cost > limit:
            return False

        usage["spent_usd"] += cost
        return True


# Example usage
budget = BudgetEnforcer()
budget.set_limit("user_123", daily_limit_usd=5.0)

if not budget.check_and_record("user_123", "gpt-4", 1500, 500):
    raise RuntimeError("daily budget exceeded")
```

Without cost limits, one user can drain the entire budget.

## Scaling Strategies

Most agent load comes from LLM API calls. Optimizing those calls is the core of scaling.

### Caching

Same input, same output can be cached.

```python
import hashlib
import json
from typing import Optional

class ResponseCache:
    """LLM response cache."""

    def __init__(self, ttl_seconds: int = 3600):
        self._cache = {}
        self._ttl = ttl_seconds

    def _key(self, model: str, messages: list, temperature: float) -> str:
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": temperature
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def get(self, model: str, messages: list, temperature: float) -> Optional[str]:
        # temperature > 0 is unsafe to cache
        if temperature > 0:
            return None
        key = self._key(model, messages, temperature)
        entry = self._cache.get(key)
        if entry and time.time() - entry["timestamp"] < self._ttl:
            return entry["response"]
        return None

    def set(self, model: str, messages: list, temperature: float, response: str):
        if temperature > 0:
            return
        key = self._key(model, messages, temperature)
        self._cache[key] = {"response": response, "timestamp": time.time()}
```

Caching only `temperature=0` calls is safe.

### Rate Limiting and Queuing

LLM APIs have rate limits, so the agent must throttle calls too.

```python
from collections import deque

class RateLimiter:
    """Sliding-window rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.timestamps = deque()
        self.lock = threading.Lock()

    def acquire(self) -> bool:
        with self.lock:
            now = time.time()
            # Drop timestamps outside the window
            while self.timestamps and self.timestamps[0] < now - self.window:
                self.timestamps.popleft()

            if len(self.timestamps) >= self.max_requests:
                return False

            self.timestamps.append(now)
            return True

    def wait_and_acquire(self):
        while not self.acquire():
            time.sleep(0.1)


# Example usage
limiter = RateLimiter(max_requests=60, window_seconds=60)  # 60/minute
limiter.wait_and_acquire()
response = call_llm_api()
```

### Asynchronous Processing

Put long-running tasks on a queue and process asynchronously.

```python
import asyncio
from asyncio import Queue

class AgentTaskQueue:
    """Async task queue."""

    def __init__(self, num_workers: int = 5):
        self.queue: Queue = Queue()
        self.num_workers = num_workers
        self.workers = []

    async def submit(self, task: dict) -> str:
        task_id = str(uuid.uuid4())
        await self.queue.put({"id": task_id, **task})
        return task_id

    async def _worker(self, worker_id: int):
        while True:
            task = await self.queue.get()
            try:
                # Real agent execution
                await process_task(task)
            except Exception as e:
                logger.error("task_failed", task_id=task["id"], error=str(e))
            finally:
                self.queue.task_done()

    async def start(self):
        for i in range(self.num_workers):
            self.workers.append(asyncio.create_task(self._worker(i)))
```

## Deployment and Rollback

Agents fuse LLMs, prompts, and tool definitions, making change impact hard to predict.

### Canary Deployment

```python
import random

class CanaryRouter:
    """Route a fraction of traffic to a new version."""

    def __init__(self, canary_percentage: float = 0.05):
        self.canary_percentage = canary_percentage
        self.versions = {"stable": None, "canary": None}

    def register(self, version: str, agent):
        self.versions[version] = agent

    def route(self, request) -> tuple:
        if (self.versions["canary"] and
            random.random() < self.canary_percentage):
            return self.versions["canary"], "canary"
        return self.versions["stable"], "stable"

    def adjust_canary(self, percentage: float):
        self.canary_percentage = max(0.0, min(1.0, percentage))


# Example usage
router = CanaryRouter(canary_percentage=0.05)  # 5% canary
router.register("stable", agent_v1)
router.register("canary", agent_v2)

agent, version = router.route(user_request)
result = agent.run(user_request)
metrics.increment("agent.requests", version=version)
```

When issues are detected, you must be able to roll back to 0% instantly.

### Feature Flags

```python
class FeatureFlags:
    """Feature flags."""

    def __init__(self):
        self._flags = {}

    def set(self, name: str, enabled: bool):
        self._flags[name] = enabled

    def is_enabled(self, name: str, user_id: Optional[str] = None) -> bool:
        return self._flags.get(name, False)


# Example usage
flags = FeatureFlags()
flags.set("use_new_planning", False)

def plan_task(task):
    if flags.is_enabled("use_new_planning"):
        return new_planner(task)
    return legacy_planner(task)
```

Toggling at runtime enables instant response to incidents.

## Common Mistakes

### Mistake 1: Deploying Without Logs/Metrics

When something breaks, there's no way to trace the cause.

```python
# Bad
def handle_request(req):
    return agent.run(req)  # zero logging, zero metrics

# Good
def handle_request(req):
    req_id = str(uuid.uuid4())
    logger.info("request_received", request_id=req_id, user=req["user"])
    start = time.time()
    try:
        result = agent.run(req)
        metrics.timing("agent.duration", (time.time() - start) * 1000)
        metrics.increment("agent.success")
        return result
    except Exception as e:
        logger.error("request_failed", request_id=req_id, error=str(e))
        metrics.increment("agent.error")
        raise
```

### Mistake 2: No Cost Monitoring

```python
# Bad
response = openai.ChatCompletion.create(...)  # zero cost tracking
return response

# Good
response = openai.ChatCompletion.create(...)
budget.record(
    user_id=current_user,
    model=response.model,
    prompt_tokens=response.usage.prompt_tokens,
    completion_tokens=response.usage.completion_tokens
)
```

To avoid invoice shock at month-end, real-time tracking is mandatory.

### Mistake 3: 100% Deploy at Once

```python
# Bad
def deploy_v2():
    global agent
    agent = AgentV2()  # all traffic switches instantly

# Good
def deploy_v2():
    router.register("canary", AgentV2())
    router.adjust_canary(0.05)  # start at 5%
    # monitor and ramp up gradually
```

LLM-based systems regress easily; canary is required.

### Mistake 4: Ignoring Rate Limits

```python
# Bad
for item in items:  # 10,000 items
    response = openai.ChatCompletion.create(...)  # exceeds API quota

# Good
limiter = RateLimiter(60, 60)
for item in items:
    limiter.wait_and_acquire()
    response = openai.ChatCompletion.create(...)
```

Bulk processing must always consider rate limits.

### Mistake 5: Logging PII

```python
# Bad
logger.info("request", user_message=req.message)  # raw personal data

# Good
logger.info("request",
    user_id=hash_user_id(req.user_id),  # hashed
    message_length=len(req.message),    # length only
    message_hash=hash(req.message)      # don't store contents
)
```

A leading cause of GDPR/CCPA violations and security incidents.

## Key Takeaways

- Production agents must be observable through logs, metrics, and traces
- Per-user cost limits and real-time tracking are mandatory
- Optimize LLM calls with caching, rate limiting, and async processing
- Use canary deployment and feature flags to apply changes safely
- Never log PII; hash or mask it instead

<!-- toc:begin -->
## AI Agent 101 Series

- [What Is an AI Agent?](./01-what-is-an-ai-agent.md)
- [Context Engineering](./02-context-engineering.md)
- [Tool Use Fundamentals](./03-tool-use-fundamentals.md)
- [Agent Workflow Design](./04-agent-workflow-design.md)
- [Memory and State](./05-memory-and-state.md)
- [Multi-Agent Systems](./06-multi-agent-systems.md)
- [Agent Evaluation](./07-agent-evaluation.md)
- [Error Handling and Reliability](./08-error-handling-reliability.md)
- **Production Operations (current)**
- Building Your First Agent (upcoming)
<!-- toc:end -->

## References

1. **OpenTelemetry: LLM Observability** - https://opentelemetry.io/docs/specs/semconv/gen-ai/  
   OpenTelemetry semantic conventions for LLM/agent observability. Defines standard trace attributes.

2. **LangSmith Production Monitoring** - https://docs.smith.langchain.com/observability  
   LangChain's operations monitoring tool. Integrates traces, metrics, and evaluation.

3. **Google SRE Book: Monitoring Distributed Systems** - https://sre.google/sre-book/monitoring-distributed-systems/  
   Google's SRE monitoring principles. The Four Golden Signals apply to agents too.

4. **OpenAI: Production Best Practices** - https://platform.openai.com/docs/guides/production-best-practices  
   OpenAI's official operations guide. Covers rate limits, monitoring, and cost management.

Tags: AI Agent, Operations, Monitoring, Observability
