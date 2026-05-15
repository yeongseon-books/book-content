---
title: 운영
series: ai-agent-101
episode: 9
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Operations
- Monitoring
- Observability
last_reviewed: '2026-05-12'
seo_description: production agent 운영에 필요한 observability와 비용 통제를 정리합니다.
---

# 운영

agent를 로컬 데모에서 production으로 옮기는 순간 질문이 달라집니다. "잘 답하나?"보다 먼저 "얼마나 비싸나?", "어디서 느려지나?", "왜 실패했나?", "어떤 tool이 병목인가?" 같은 운영 질문이 앞에 나옵니다.

이 차이는 agent가 단순한 모델 호출이 아니라 여러 단계의 실행 시스템이기 때문에 생깁니다. 한 요청이 planning, tool call, retrieval, synthesis, memory write를 모두 거칠 수 있고, 각 단계가 서로 다른 latency와 failure mode를 가집니다.

그래서 production agent의 핵심은 observability입니다. 로그, 메트릭, 트레이스가 없으면 문제를 발견해도 원인을 설명할 수 없고, 원인을 모르면 비용 최적화나 품질 개선도 우연에 의존하게 됩니다.

이 글은 AI Agent 101 시리즈의 아홉 번째 글입니다.

이 글에서는 운영을 모델 배포가 아니라 관측 가능성과 예산 통제의 문제로 정리하겠습니다.

## 이 글에서 다룰 문제

- production agent에서 가장 먼저 심어야 할 관측 신호는 무엇일까요?
- structured logging과 tracing은 각각 어떤 질문에 답해 줄까요?
- 비용 상한과 사용자별 예산은 어떤 방식으로 강제할 수 있을까요?
- agent를 scale할 때 병목은 LLM보다 tool 계층에서 더 자주 생길까요?
- 안전한 배포와 롤백을 위해 무엇을 미리 준비해야 할까요?

## 왜 이 글이 중요한가

운영 체계가 없으면 agent는 금방 블랙박스가 됩니다. 잘될 때는 멋져 보이지만, 느려지거나 틀리거나 비싸질 때 왜 그런지 알 수 없습니다. production 시스템으로서는 매우 위험한 상태입니다.

또한 LLM 비용은 일반적인 API 비용과 다르게 예측이 어렵습니다. 같은 기능도 프롬프트 길이, tool call 횟수, retry, 모델 선택에 따라 단가가 크게 달라집니다. 따라서 운영에서 비용 추적은 단순 회계가 아니라 아키텍처 피드백 루프입니다.

observability는 reliability와 evaluation을 실제로 연결해 주는 층이기도 합니다. 어떤 경로가 비싸고, 어떤 tool이 느리고, 어느 단계에서 실패가 몰리는지 보이지 않으면 앞선 장들에서 설계한 원칙을 검증할 수 없습니다.

## 운영을 이해하는 가장 좋은 방법: 품질 관리가 아니라 실행 시스템의 관측으로 보는 것입니다

agent 운영은 모델 응답을 모니터링하는 일이 아닙니다. 요청 하나가 내부에서 어떤 단계들을 거쳤는지 추적하고, 그 단계별 비용과 시간을 읽는 일에 가깝습니다. 이 관점이 있어야 병목과 낭비를 분리할 수 있습니다.

예를 들어 느린 요청이 모두 모델 때문이라고 가정하면 잘못된 대응을 하게 됩니다. 실제로는 외부 검색 API가 느릴 수도 있고, 같은 tool을 두 번씩 호출하는 workflow 때문일 수도 있고, serialization payload가 지나치게 커서 synthesis가 느릴 수도 있습니다. 운영 관측이 있어야 이 차이가 드러납니다.

현업에서는 보통 로그, 메트릭, 트레이스를 함께 둡니다. 로그는 사건을 읽게 해주고, 메트릭은 추세를 보여 주며, 트레이스는 한 요청의 경로를 복원해 줍니다.

> production agent 운영의 핵심은 "모델이 무엇을 답했는가"보다 "요청이 어떤 경로와 비용으로 처리되었는가"를 관측 가능하게 만드는 데 있습니다.

## 핵심 개념

### structured logging은 사건을 검색 가능한 형태로 남깁니다

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
```

structured log는 어느 tool이 얼마나 오래 걸렸는지, 어느 request_id에서 어떤 fallback이 발생했는지 같은 질문에 답하게 해 줍니다. plaintext 로그로는 같은 작업을 반복하기 어렵습니다.

### tracing은 한 요청의 내부 경로를 복원합니다

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
```

trace는 "왜 이 요청이 12초 걸렸는가" 같은 질문에 특히 강합니다. planning이 느렸는지, tool이 느렸는지, synthesis가 느렸는지 한 요청 단위로 복원할 수 있기 때문입니다.

### 핵심 메트릭은 적지만 분명해야 합니다

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
```

운영 초기에 꼭 보는 메트릭은 보통 다음과 같습니다.

- request count와 success/failure rate
- end-to-end latency p50/p95/p99
- tool별 호출 수와 latency
- total tokens와 estimated cost
- fallback 발생 횟수와 timeout 비율

### 비용 상한은 시스템 차원에서 강제해야 합니다

```python
from datetime import datetime, timedelta

class BudgetEnforcer:
    """Budget enforcement."""

    PRICING = {
        "gpt-4": {"prompt": 0.03 / 1000, "completion": 0.06 / 1000},
        "gpt-4o-mini": {"prompt": 0.15 / 1_000_000, "completion": 0.60 / 1_000_000}
    }
```

모델 비용은 프롬프트 설계와 workflow 구조에 따라 흔들립니다. 그래서 사용자별 한도, 조직별 예산, 고비용 모델 사용 제한 같은 장치를 시스템 차원에서 걸어 두는 편이 안전합니다. 비용이 관측만 되고 제어되지 않으면 운영은 곧 불안정해집니다.

기존 워크로드에서 `gpt-3.5-turbo`를 유지한다면 legacy 모델 기준으로 예산을 잡아야 합니다. 현재 legacy 단가는 입력 1M tokens당 $0.50, 출력 1M tokens당 $1.50이며, 새 비용 최적화 예시는 `gpt-4o-mini`를 기준으로 설명하는 편이 더 현실적입니다.

### 배포는 모델만이 아니라 프롬프트와 tool registry의 릴리스입니다

agent 배포는 새 코드 배포이면서 동시에 새 프롬프트, 새 schema, 새 workflow 배포입니다. 따라서 canary, rollback, version pinning, replay eval이 함께 있어야 합니다. 특히 tool contract가 바뀌는 릴리스는 기능 코드 못지않게 조심해야 합니다.

## 흔히 헷갈리는 지점

- 느린 응답의 원인을 모델 하나로 단정하기 쉽지만, 실제 병목은 tool 계층일 때가 많습니다.
- 로그만 있으면 충분하다고 보기 쉽지만, 추세를 보려면 메트릭이 필요하고 경로를 보려면 트레이스가 필요합니다.
- 비용 추적은 나중에 붙여도 된다고 생각하기 쉽지만, 초기에 안 넣으면 회귀 비교가 어려워집니다.
- agent 배포를 모델 버전 변경 정도로만 보기 쉽지만, 프롬프트와 tool schema도 함께 버전 관리해야 합니다.
- 운영 체크리스트를 만들지 않으면 품질 이슈가 인프라 이슈처럼, 인프라 이슈가 모델 이슈처럼 보이기 쉽습니다.

## 운영 체크리스트

- [ ] request_id 기준으로 로그, 메트릭, 트레이스를 연결할 수 있는가
- [ ] request, tool, model 단위 비용과 latency를 측정하는가
- [ ] 사용자 또는 조직별 예산 상한과 차단 정책이 있는가
- [ ] 프롬프트, tool registry, workflow 버전을 함께 관리하는가
- [ ] canary, rollback, replay eval이 배포 절차에 포함되어 있는가

## 정리

production agent 운영의 핵심은 observability입니다. 어떤 요청이 어떤 경로로 처리되었고 어디서 시간이 걸렸으며 얼마의 비용이 들었는지 보이지 않으면, 품질 개선도 비용 최적화도 모두 추측에 머무르게 됩니다.

좋은 운영 체계는 모델 자체보다 시스템 전체를 봅니다. 로그는 사건을 남기고, 메트릭은 추세를 보게 하고, 트레이스는 경로를 복원하게 합니다. 이 세 축이 있어야 앞선 장들에서 다룬 workflow, memory, reliability 설계가 실제로 검증됩니다.

다음 글에서는 이 모든 요소를 모아 첫 agent를 끝까지 구현해 봅니다. 결국 운영 가능한 agent를 만드는 일은 개념을 아는 것에서 끝나지 않고, 작은 시스템으로 직접 묶어 보는 단계까지 가야 비로소 감이 잡히기 때문입니다.

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

### 공식 문서

- [OpenTelemetry documentation](https://opentelemetry.io/docs/)
- [OpenAI Platform - Monitoring usage](https://platform.openai.com/docs/guides/monitor-usage)
- [LangSmith documentation](https://docs.smith.langchain.com/)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)

### 관련 시리즈

- [AI Evaluation 101 - 운영 지표 읽기](../../ai-evaluation-101/ko/10-production-evaluation.md)
- [Azure App Service 101 - 플랫폼 운영 감각](../../azure-app-service-101/ko/01-what-is-app-service.md)

Tags: AI Agent, LLM, Tool Use, Python
