---
title: 운영
series: ai-agent-101
episode: 9
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Operations
- Monitoring
- Observability
last_reviewed: '2026-05-02'
seo_description: Agent를 프로덕션에 배포하면 새로운 문제가 생깁니다. 비용이 얼마나 드는지, 응답 시간이 얼마나 걸리는지, 어디서
  실패하는지, 어떤…
---

# 운영

> AI Agent 101 시리즈 (9/10)

Agent를 프로덕션에 배포하면 새로운 문제가 생깁니다. 비용이 얼마나 드는지, 응답 시간이 얼마나 걸리는지, 어디서 실패하는지, 어떤 도구가 가장 많이 호출되는지 모니터링해야 합니다.

Agent 운영의 핵심은 Observability입니다. Agent의 모든 단계를 추적하고, 비용과 지연 시간을 측정하며, 이상 징후를 감지해야 합니다. 또한 스케일링 전략과 비용 최적화도 중요합니다.

이번 글에서는 Agent Observability, 비용 추적, 지연 시간 최적화, 스케일링 패턴, 그리고 프로덕션 체크리스트를 다룹니다.

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- Agent를 운영에 올릴 때 가장 먼저 봐야 할 관찰 지표는 무엇일까요?
- 비용을 추적하고 상한을 거는 가장 단순한 방법은 무엇일까요?
- Agent를 스케일링할 때 LLM 호출과 도구 호출 중 어디에서 병목이 생길까요?
- 안전한 배포·롤백 전략은 어떻게 짜야 할까요?

<!-- a-grade-intro:end -->

## 관찰 가능성 (Observability)

운영 환경의 Agent는 "왜 이렇게 답했는가"를 추적할 수 있어야 합니다. Logs, Metrics, Traces 세 축이 핵심입니다.

### 구조화 로깅

평문 로그는 파싱과 검색이 어렵습니다. JSON 구조화 로그가 표준입니다.

```python
import logging
import json
from datetime import datetime
from typing import Any

class StructuredLogger:
    """구조화 로깅."""

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

# 사용 예시
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

구조화 로그는 ELK, Datadog, CloudWatch에서 그대로 쿼리할 수 있습니다.

### 분산 추적 (Tracing)

Agent의 한 요청은 여러 LLM 호출, 도구 호출을 거칩니다. Trace로 전체 경로를 시각화합니다.

```python
from contextlib import contextmanager
import uuid
import time

class TraceContext:
    """간단한 분산 추적."""

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

# 사용 예시
trace = TraceContext()

with trace.span("agent_request", user_id="u_456"):
    with trace.span("llm_planning", model="gpt-4"):
        plan = call_llm(user_input)

    with trace.span("tool_execution", tool="search"):
        result = search_tool(plan["query"])

    with trace.span("llm_synthesis", model="gpt-4"):
        answer = call_llm(result)

# trace.spans 를 OpenTelemetry, Jaeger 등으로 전송
```

OpenTelemetry 표준을 사용하면 LangSmith, Datadog APM과 호환됩니다.

### 핵심 메트릭

```python
from collections import defaultdict
import threading

class MetricsCollector:
    """메트릭 수집기."""

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

# 사용 예시 — 추적해야 할 핵심 메트릭
metrics = MetricsCollector()
metrics.increment("agent.requests", status="success")
metrics.increment("agent.tool_calls", tool="search")
metrics.increment("agent.errors", type="timeout")
metrics.timing("agent.request.duration", 1234, model="gpt-4")
metrics.timing("agent.tool.duration", 234, tool="search")
```

핵심 메트릭: 요청 수, 성공/실패율, latency p50/p95/p99, 토큰 사용량, 비용.

## 비용 추적과 제한

LLM 비용은 운영의 가장 큰 변수입니다. 사용자/조직별 한도를 설정해야 합니다.

```python
from datetime import datetime, timedelta

class BudgetEnforcer:
    """예산 강제."""

    PRICING = {
        "gpt-4": {"prompt": 0.03 / 1000, "completion": 0.06 / 1000},
        "gpt-3.5-turbo": {"prompt": 0.0015 / 1000, "completion": 0.002 / 1000}
    }

    def __init__(self):
        # 사용자별 일일 사용량
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
        """예산 확인 후 사용량 기록. False면 차단."""
        today = datetime.utcnow().date()
        usage = self._usage[user_id]

        # 날짜 바뀌면 리셋
        if usage["date"] != today:
            usage["date"] = today
            usage["spent_usd"] = 0.0

        # 예상 비용
        cost = (
            prompt_tokens * self.PRICING[model]["prompt"] +
            completion_tokens * self.PRICING[model]["completion"]
        )

        limit = self._limits.get(user_id, float("inf"))
        if usage["spent_usd"] + cost > limit:
            return False

        usage["spent_usd"] += cost
        return True

# 사용 예시
budget = BudgetEnforcer()
budget.set_limit("user_123", daily_limit_usd=5.0)

if not budget.check_and_record("user_123", "gpt-4", 1500, 500):
    raise RuntimeError("일일 예산 초과")
```

비용 제한이 없으면 한 사용자가 전체 예산을 소진할 수 있습니다.

## 스케일링 전략

Agent의 부하는 LLM API 호출이 대부분입니다. 따라서 LLM 호출을 효율화하는 것이 핵심입니다.

### 캐싱

같은 입력에 같은 출력은 캐싱할 수 있습니다.

```python
import hashlib
import json
from typing import Optional

class ResponseCache:
    """LLM 응답 캐시."""

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
        # temperature > 0 이면 캐시 부적합
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

`temperature=0` 호출만 캐싱하는 것이 안전합니다.

### Rate Limiting과 큐잉

LLM API 자체에 rate limit이 있으므로, Agent에서도 호출을 조절해야 합니다.

```python
from collections import deque

class RateLimiter:
    """슬라이딩 윈도우 rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.timestamps = deque()
        self.lock = threading.Lock()

    def acquire(self) -> bool:
        with self.lock:
            now = time.time()
            # 윈도우 밖 타임스탬프 제거
            while self.timestamps and self.timestamps[0] < now - self.window:
                self.timestamps.popleft()

            if len(self.timestamps) >= self.max_requests:
                return False

            self.timestamps.append(now)
            return True

    def wait_and_acquire(self):
        while not self.acquire():
            time.sleep(0.1)

# 사용 예시
limiter = RateLimiter(max_requests=60, window_seconds=60)  # 분당 60회
limiter.wait_and_acquire()
response = call_llm_api()
```

### 비동기 처리

긴 작업은 큐에 넣고 비동기 처리합니다.

```python
import asyncio
from asyncio import Queue

class AgentTaskQueue:
    """비동기 작업 큐."""

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
                # 실제 Agent 실행
                await process_task(task)
            except Exception as e:
                logger.error("task_failed", task_id=task["id"], error=str(e))
            finally:
                self.queue.task_done()

    async def start(self):
        for i in range(self.num_workers):
            self.workers.append(asyncio.create_task(self._worker(i)))
```

## 배포와 롤백

Agent는 LLM, 프롬프트, 도구 정의가 모두 결합된 시스템이라 변경 영향을 예측하기 어렵습니다.

### 점진적 배포 (Canary)

```python
import random

class CanaryRouter:
    """일부 트래픽만 새 버전으로 라우팅."""

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

# 사용 예시
router = CanaryRouter(canary_percentage=0.05)  # 5%만 canary
router.register("stable", agent_v1)
router.register("canary", agent_v2)

agent, version = router.route(user_request)
result = agent.run(user_request)
metrics.increment("agent.requests", version=version)
```

문제 감지 시 즉시 0%로 되돌릴 수 있어야 합니다.

### Feature Flag

```python
class FeatureFlags:
    """기능 플래그."""

    def __init__(self):
        self._flags = {}

    def set(self, name: str, enabled: bool):
        self._flags[name] = enabled

    def is_enabled(self, name: str, user_id: Optional[str] = None) -> bool:
        return self._flags.get(name, False)

# 사용 예시
flags = FeatureFlags()
flags.set("use_new_planning", False)

def plan_task(task):
    if flags.is_enabled("use_new_planning"):
        return new_planner(task)
    return legacy_planner(task)
```

런타임에 동작을 켜고 끌 수 있어 문제 발생 시 즉시 대응 가능합니다.

## 흔한 실수 5가지

### 실수 1: 로그/메트릭 없이 배포

문제 발생 시 원인을 추적할 방법이 없습니다.

```python
# 나쁜 예
def handle_request(req):
    return agent.run(req)  # 로깅 0, 메트릭 0

# 좋은 예
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

### 실수 2: 비용 모니터링 없음

```python
# 나쁜 예
response = openai.ChatCompletion.create(...)  # 비용 추적 0
return response

# 좋은 예
response = openai.ChatCompletion.create(...)
budget.record(
    user_id=current_user,
    model=response.model,
    prompt_tokens=response.usage.prompt_tokens,
    completion_tokens=response.usage.completion_tokens
)
```

월말에 청구서 보고 놀라지 않으려면 실시간 추적이 필수입니다.

### 실수 3: 한 번에 100% 배포

```python
# 나쁜 예
def deploy_v2():
    global agent
    agent = AgentV2()  # 모든 트래픽 즉시 전환

# 좋은 예
def deploy_v2():
    router.register("canary", AgentV2())
    router.adjust_canary(0.05)  # 5%부터
    # 모니터링 후 점진적 증가
```

LLM 기반 시스템은 회귀가 흔하므로 canary 필수입니다.

### 실수 4: Rate Limit 무시

```python
# 나쁜 예
for item in items:  # 1만 건
    response = openai.ChatCompletion.create(...)  # API 한도 초과

# 좋은 예
limiter = RateLimiter(60, 60)
for item in items:
    limiter.wait_and_acquire()
    response = openai.ChatCompletion.create(...)
```

대량 처리는 항상 rate limit을 고려합니다.

### 실수 5: PII 로깅

```python
# 나쁜 예
logger.info("request", user_message=req.message)  # 개인정보 그대로

# 좋은 예
logger.info("request",
    user_id=hash_user_id(req.user_id),  # 해시
    message_length=len(req.message),    # 길이만
    message_hash=hash(req.message)      # 내용 자체는 미저장
)
```

GDPR/CCPA 위반과 보안 사고의 주요 원인입니다.

## 핵심 요약

- 운영 환경 Agent는 logs, metrics, traces로 관찰 가능해야 합니다
- 사용자별 비용 한도와 실시간 추적이 필수입니다
- 캐싱, rate limiting, 비동기 처리로 LLM 호출을 효율화합니다
- Canary 배포와 feature flag로 안전하게 변경을 적용합니다
- PII는 로깅하지 말고 해시/마스킹합니다

<!-- a-grade-example:begin -->

## 체크리스트

- [ ] 관찰 지표를 latency / cost / quality / safety로 나눴다.
- [ ] 한 Agent run 당 토큰·달러 비용을 자동 기록했다.
- [ ] 동시 요청을 늘려 가며 병목이 LLM인지 도구인지 측정했다.
- [ ] 카나리 배포·즉시 롤백 절차를 글로 정리했다.

<!-- a-grade-example:end -->

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [컨텍스트 엔지니어링](./02-context-engineering.md)
- [Tool Use 기초](./03-tool-use-fundamentals.md)
- [Agent Workflow 설계](./04-agent-workflow-design.md)
- [Memory와 State](./05-memory-and-state.md)
- [Multi-Agent 시스템](./06-multi-agent-systems.md)
- [Agent 평가](./07-agent-evaluation.md)
- [에러 처리와 안정성](./08-error-handling-reliability.md)
- **운영 (현재 글)**
- 첫 Agent 만들기 (예정)

<!-- toc:end -->

## 참고 자료

1. **OpenTelemetry: LLM Observability** - https://opentelemetry.io/docs/specs/semconv/gen-ai/  
   LLM/Agent 관찰 가능성을 위한 OpenTelemetry semantic conventions. 표준 trace 속성을 정의합니다.

2. **LangSmith Production Monitoring** - https://docs.smith.langchain.com/observability  
   LangChain의 운영 모니터링 도구. Trace, metric, evaluation을 통합 제공합니다.

3. **Google SRE Book: Monitoring Distributed Systems** - https://sre.google/sre-book/monitoring-distributed-systems/  
   Google의 SRE 모니터링 원칙. Four Golden Signals를 Agent에도 적용할 수 있습니다.

4. **OpenAI: Production Best Practices** - https://platform.openai.com/docs/guides/production-best-practices  
   OpenAI 공식 운영 가이드. Rate limit, 모니터링, 비용 관리 모범 사례를 제공합니다.

Tags: AI Agent, LLM, Tool Use, Python
