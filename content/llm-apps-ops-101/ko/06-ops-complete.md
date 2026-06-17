---
title: "LLM Apps Ops 101 (6/6): LLM 앱 운영 완성"
series: llm-apps-ops-101
episode: 6
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/289"
    published_at: '2026-06-06'
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LLMOps
- Observability
- Python
- LLM
last_reviewed: '2026-05-12'
seo_description: 모니터링·비용·평가·보안·배포 레이어를 한 요청 경로 위에 통합해 운영 파이프라인을 완성합니다.
---

# LLM Apps Ops 101 (6/6): LLM 앱 운영 완성

금요일 오후, 대시보드에 비용 알람이 울립니다. 30분 전부터 토큰 소비가 평소의 3배입니다. 비용 담당자는 "어떤 요청이 문제인지 모르겠다"고 말하고, 보안 담당자는 "내 로그에는 차단된 게 없다"고 합니다. 평가 담당자는 "품질 점수는 정상"이라고 합니다. 세 사람 모두 맞는 말을 하고 있지만, 한 시간이 지나도 원인은 좁혀지지 않습니다.

이 글은 LLM 앱 운영 101 시리즈의 마지막 글입니다.

문제는 각 레이어가 잘못된 것이 아니었습니다. 각 레이어가 서로 다른 `request_id`를 쓰고 있었고, 비용 로그에는 보안 판정이 없었으며, 평가 로그에는 비용 정보가 없었습니다. 모든 레이어가 정상이었지만 아무도 "이 요청 한 건이 왜 비쌌는지"를 한 문장으로 설명하지 못했습니다. EP01~EP05에서 만든 레이어를 한 흐름으로 연결하지 않으면, 운영 대응은 항상 이 지점에서 멈춥니다.

![요청 한 건이 보안·비용·품질·로그 레이어를 관통하는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/06/06-01-big-picture.ko.png)
*요청 한 건이 보안·비용·품질·로그 레이어를 관통하는 흐름*

> 운영 완성은 레이어를 많이 붙이는 일이 아니라, 한 요청의 전체 수명을 끊김 없이 설명할 수 있는 상태를 만드는 일입니다.

## 이 글에서 다룰 문제

- 모니터링, 비용, 평가, 보안, 배포가 각각 독립적으로 잘 돌아가도 운영 공백이 생기는 이유는 무엇일까요?
- 한 요청의 전체 수명을 추적하려면 어떤 공통 계약이 모든 레이어에 필요할까요?
- 운영 성숙도를 "감각"이 아니라 "기준"으로 판단하려면 어떤 종료 조건을 정의해야 할까요?
- 따로 만들면 왜 깨지는가에서 가장 흔한 실수는 무엇일까요?
- 통합의 핵심: 요청 스코프 컨텍스트을 실무에 적용할 때 주의할 점은 무엇일까요?
- 실행 순서 계약의 핵심 원리를 한 문장으로 설명하면 무엇일까요?

## 따로 만들면 왜 깨지는가

EP01~EP05에서 각각 모니터링, 비용, 평가, 보안, 배포를 독립 예제로 구현했습니다. 데모에서는 문제없이 동작합니다. 하지만 운영 환경에서 레이어를 합쳐야 하는 순간, 세 가지 문제가 드러납니다.

### 1. request_id 단절

가장 흔한 실패입니다. 로깅 모듈은 자체 UUID를 만들고, 비용 모듈도 자체 UUID를 만듭니다. 장애 때 "이 요청의 비용"을 찾으려면 타임스탬프로 대충 매칭해야 합니다. 트래픽이 초당 10건만 넘어도 타임스탬프 매칭은 실패합니다.

### 2. 실행 순서 미정의

보안 검증을 모델 호출 이후에 돌리는 팀이 있었습니다. 입력이 위험한데 모델이 먼저 응답하고, 그 응답을 사후 차단하는 구조였습니다. 비용은 이미 발생했고, 사용자에게는 에러만 보였습니다. "왜 돈은 빠져나갔는데 응답은 없지?"라는 질문에 답하려면, 실행 순서가 계약으로 고정되어 있어야 합니다.

### 3. 필드 의미 불일치

한 팀의 `success`는 HTTP 200 반환을 의미했고, 다른 팀의 `success`는 평가 통과까지 포함했습니다. 주간 회의에서 "성공률 98%"라고 보고하면, 어떤 기준의 성공률인지부터 확인해야 했습니다. 같은 단어가 다른 의미를 갖는 순간, 공통 대시보드는 오해를 낳는 도구가 됩니다.

| 증상 | 근본 원인 | 통합 파이프라인이 해결하는 방식 |
|------|----------|-------------------------------|
| 장애 때 레이어별 로그를 따로 조회 | request_id 단절 | 요청 진입 시 단일 ID 발급, 전 레이어 전파 |
| 비용 발생했는데 응답 없음 | 실행 순서 미정의 | 보안 → 모델 → 비용 → 평가 → 로그 순서 계약 |
| "성공률" 수치가 팀마다 다름 | 필드 의미 불일치 | 공통 스키마 문서 + 코드 레벨 타입 강제 |

## 통합의 핵심: 요청 스코프 컨텍스트

문제를 한 문장으로 줄이면 이렇습니다. **한 요청이 시스템을 통과하는 동안, 모든 레이어가 같은 컨텍스트 객체를 참조해야 합니다.**

이 컨텍스트 객체가 담아야 할 최소 필드를 정의하겠습니다.

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

@dataclass
class RequestContext:
    """한 요청의 전체 수명 동안 모든 레이어가 공유하는 컨텍스트."""

    request_id: str = field(default_factory=lambda: uuid4().hex[:16])
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # 보안 레이어가 기록
    input_allowed: bool = True
    policy_decision: str = "pending"

    # 모델 호출 레이어가 기록
    model: str = ""
    prompt_version: str = ""
    input_tokens: int = 0
    output_tokens: int = 0

    # 비용 레이어가 기록
    estimated_cost_usd: float = 0.0

    # 평가 레이어가 기록
    evaluation_status: str = "pending"  # pass / fail / review
    quality_score: float = 0.0

    # 로깅 레이어가 최종 소비
    latency_ms: float = 0.0
```

핵심은 이 객체가 요청 진입 시 한 번 생성되고, 각 레이어가 자기 필드만 채우며, 최종적으로 로거가 전체를 구조화 로그로 남기는 구조입니다. 어떤 레이어도 자체 UUID를 만들지 않습니다. `request_id`는 하나뿐이고, 모든 레이어가 같은 값을 씁니다.

## 실행 순서 계약

레이어를 연결하려면 "누가 먼저 실행되는가"를 계약으로 고정해야 합니다. 순서가 코드에 암묵적으로 존재하면 리팩터링 한 번으로 깨집니다.

```
[요청 진입]
  → ① 컨텍스트 생성 (request_id 발급)
  → ② 보안 검증 (injection 탐지, 정책 판정)
  → ③ 모델 호출 (프롬프트 조립, API 호출)
  → ④ 비용 계산 (토큰 기반 비용 집계)
  → ⑤ 품질 평가 (길이, 키워드, 점수 산출)
  → ⑥ 구조화 로그 (컨텍스트 전체를 JSON 기록)
[응답 반환]
```

이 순서가 계약인 이유가 있습니다. ②에서 차단되면 ③~⑥은 실행되지 않습니다. 비용이 발생하지 않고, 평가도 필요 없고, 로그에는 "차단됨"만 남습니다. 반대로 ②를 통과했는데 ③에서 API 에러가 나면, 비용은 0이고 평가는 건너뛰되 로그에는 에러 사유가 남습니다. 이렇게 "어디서 멈췄는가"가 명확해야 장애 분류가 빨라집니다.

## 통합 파이프라인 코드

EP01~EP05에서 만든 개별 함수를 하나의 요청 핸들러 안에서 조립합니다. 코드가 길지만, 각 섹션이 위 순서 계약의 어떤 단계인지 주석으로 표시했습니다.

### 공통 설정과 로거

```python
import json
import logging
import os
import re
import time
from datetime import datetime, timezone

from groq import Groq

MODEL = "llama-3.1-8b-instant"
PRICE_INPUT = 0.05   # USD per 1M input tokens
PRICE_OUTPUT = 0.05  # USD per 1M output tokens
INJECTION_PATTERNS = [
    r"ignore\s+all\s+previous\s+instructions",
    r"reveal\s+your\s+system\s+prompt",
]

class JsonFormatter(logging.Formatter):
    """모든 레이어의 신호를 한 줄 JSON으로 출력하는 포매터."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
        }
        extra = getattr(record, "payload", None)
        if extra:
            payload.update(extra)
        return json.dumps(payload, ensure_ascii=False)

def build_logger() -> logging.Logger:
    logger = logging.getLogger("llm_ops_pipeline")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.propagate = False
    return logger

LOGGER = build_logger()
```

이 로거가 최종 단계(⑥)에서 `RequestContext` 전체를 JSON으로 남깁니다. 포맷을 한 곳에서 고정하면, 로그 수집 파이프라인(Fluentd, Vector 등)이 파싱 규칙을 하나만 유지하면 됩니다.

### 보안 레이어 (② 단계)

```python
def validate_input(text: str, ctx: "RequestContext") -> None:
    """입력 검증 후 컨텍스트에 판정 결과를 기록한다."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            ctx.input_allowed = False
            ctx.policy_decision = "blocked:injection"
            return
    ctx.policy_decision = "allowed"
```

EP04에서 만든 보안 검증과 동일하되, 결과를 `ctx`에 기록한다는 점이 다릅니다. 함수가 예외를 던지지 않고 컨텍스트에 상태를 남기면, 로그에 "왜 차단됐는가"가 항상 포함됩니다.

### 모델 호출 + 비용 계산 (③④ 단계)

```python
def call_model(client: Groq, message: str, ctx: "RequestContext") -> str:
    """모델 호출 후 토큰 사용량과 비용을 컨텍스트에 기록한다."""
    ctx.model = MODEL
    ctx.prompt_version = "v1.0"

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a concise Python assistant."},
            {"role": "user", "content": message},
        ],
    )
    usage = response.usage
    if usage is None:
        raise RuntimeError("usage metadata missing from API response")

    ctx.input_tokens = usage.prompt_tokens
    ctx.output_tokens = usage.completion_tokens

    # ④ 비용 계산 — 입출력 분리 과금
    ctx.estimated_cost_usd = round(
        (ctx.input_tokens / 1_000_000) * PRICE_INPUT
        + (ctx.output_tokens / 1_000_000) * PRICE_OUTPUT,
        8,
    )

    return response.choices[0].message.content or ""
```

EP02에서 단순히 `total_tokens * 단가`로 계산했던 것을 입력/출력 분리 과금으로 개선했습니다. 실제 LLM 서비스는 입출력 단가가 다른 경우가 많기 때문입니다.

### 품질 평가 (⑤ 단계)

```python
def evaluate_output(answer: str, ctx: "RequestContext") -> None:
    """응답 품질을 평가하고 컨텍스트에 판정을 기록한다."""
    length = len(answer)

    if length < 20:
        ctx.evaluation_status = "fail"
        ctx.quality_score = 0.0
    elif length > 2000:
        ctx.evaluation_status = "review"
        ctx.quality_score = 0.5
    else:
        ctx.evaluation_status = "pass"
        ctx.quality_score = min(1.0, length / 200)
```

EP03의 평가 로직을 컨텍스트 기반으로 전환했습니다. 핵심은 평가 결과가 독립된 어딘가에 저장되는 것이 아니라, 같은 `request_id` 아래 비용·보안과 함께 남는다는 점입니다.

### 요청 핸들러: 순서 계약 실행

```python
import asyncio
from contextlib import asynccontextmanager
from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    request_id: str
    response: str
    cost_usd: float
    evaluation_status: str
    quality_score: float

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = Groq(api_key=os.environ["GROQ_API_KEY"])
    app.state.total_calls = 0
    app.state.total_cost_usd = 0.0
    app.state.blocked_count = 0
    yield

app = FastAPI(title="llm-ops-pipeline", lifespan=lifespan)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    # ① 컨텍스트 생성
    ctx = RequestContext()

    # ② 보안 검증
    validate_input(request.message, ctx)
    if not ctx.input_allowed:
        app.state.blocked_count += 1
        # ⑥ 차단 로그 기록
        LOGGER.info("request_blocked", extra={"payload": asdict(ctx)})
        raise HTTPException(status_code=400, detail=ctx.policy_decision)

    # ③④ 모델 호출 + 비용 계산
    started = time.perf_counter()
    answer = await asyncio.to_thread(
        call_model, app.state.client, request.message, ctx
    )
    ctx.latency_ms = round((time.perf_counter() - started) * 1000, 1)

    # ⑤ 품질 평가
    evaluate_output(answer, ctx)

    # 누적 상태 갱신
    app.state.total_calls += 1
    app.state.total_cost_usd += ctx.estimated_cost_usd

    # ⑥ 구조화 로그 — 컨텍스트 전체를 한 줄로
    LOGGER.info("request_complete", extra={"payload": asdict(ctx)})

    return ChatResponse(
        request_id=ctx.request_id,
        response=answer,
        cost_usd=ctx.estimated_cost_usd,
        evaluation_status=ctx.evaluation_status,
        quality_score=ctx.quality_score,
    )
```

이 핸들러가 순서 계약을 코드로 실행합니다. ②에서 차단되면 ③~⑤은 건너뛰고, 로그에는 차단 사유만 남습니다. 정상 흐름이면 ①~⑥이 순서대로 실행되고, 로그 한 줄에 보안·비용·품질·지연 시간이 모두 들어갑니다.

### health 엔드포인트: 누적 신호 노출

```python
@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "total_calls": app.state.total_calls,
        "total_cost_usd": round(app.state.total_cost_usd, 8),
        "blocked_count": app.state.blocked_count,
    }
```

EP05에서 readiness probe로 사용했던 `/health`에 운영 신호를 추가했습니다. 배포 시스템이 이 엔드포인트를 조회하면 "이 인스턴스가 얼마나 일하고 있는가"를 즉시 알 수 있습니다.

## 실행 결과: 한 요청의 전체 흔적

서버를 띄우고 요청 한 건을 보내면 로그에 다음과 같은 JSON이 남습니다.

```json
{
  "timestamp": "2026-06-06T09:15:32.441Z",
  "level": "INFO",
  "event": "request_complete",
  "request_id": "a3f7c91e2b4d08e1",
  "started_at": "2026-06-06T09:15:31.823Z",
  "input_allowed": true,
  "policy_decision": "allowed",
  "model": "llama-3.1-8b-instant",
  "prompt_version": "v1.0",
  "input_tokens": 42,
  "output_tokens": 87,
  "estimated_cost_usd": 0.00000645,
  "evaluation_status": "pass",
  "quality_score": 0.645,
  "latency_ms": 618.3
}
```

이 한 줄이 "이 요청은 보안을 통과했고, 129 토큰을 썼고, 비용은 $0.000006이며, 품질은 pass, 지연은 618ms"라고 말합니다. 금요일 오후의 비용 알람이 울렸다면, `estimated_cost_usd`로 정렬해서 상위 요청의 `input_tokens`와 `policy_decision`을 함께 보면 30초 안에 원인을 좁힐 수 있습니다.

비교해 보겠습니다.

| 질문 | 레이어 분리 상태 | 통합 파이프라인 |
|------|-----------------|----------------|
| "비용 급증 원인은?" | 비용 로그에서 시간대 추정 → 보안 로그 별도 조회 → 수동 매칭 | `request_id`로 필터 → 한 줄에 비용+보안+품질 확인 |
| "차단된 요청의 비용은?" | 보안 시스템에 비용 필드 없음 → 답 불가 | `input_allowed=false`인 행은 `estimated_cost_usd=0` |
| "품질 낮은 응답의 공통점은?" | 평가 DB에 모델/프롬프트 버전 없음 → 상관관계 분석 불가 | `evaluation_status=fail` 필터 → `model`, `prompt_version` 즉시 확인 |

## 일일 운영 리포트: 흩어진 신호를 한 장으로

통합 로그가 쌓이면 아침마다 다섯 개 대시보드를 여는 대신, 핵심 지표를 한 페이지로 요약할 수 있습니다.

```python
def build_daily_report(rows: list[dict]) -> dict:
    """하루치 요청 로그를 받아 운영 요약을 생성한다."""
    total = len(rows)
    if total == 0:
        return {"status": "no-traffic", "request_count": 0}

    blocked = sum(1 for r in rows if not r.get("input_allowed", True))
    eval_fail = sum(
        1 for r in rows if r.get("evaluation_status") in ("fail", "review")
    )
    total_cost = sum(float(r.get("estimated_cost_usd", 0.0)) for r in rows)
    latencies = sorted(r.get("latency_ms", 0) for r in rows)
    p95_idx = max(0, int(total * 0.95) - 1)

    return {
        "request_count": total,
        "blocked_rate": round(blocked / total, 4),
        "eval_attention_rate": round(eval_fail / total, 4),
        "cost_total_usd": round(total_cost, 4),
        "cost_per_request_usd": round(total_cost / total, 8),
        "latency_p95_ms": latencies[p95_idx],
    }
```

이 리포트가 유용한 이유는 숫자 자체가 아니라, **한 질문에 여러 축의 답이 동시에 나온다는 점**입니다. "오늘 비용이 올랐네?" → `cost_per_request_usd`가 올랐는지, `blocked_rate`가 낮아져서 더 많은 요청이 모델까지 도달한 건 아닌지, `eval_attention_rate`가 올라 재시도가 늘어난 건 아닌지를 같은 표에서 함께 봅니다.

## 프롬프트 버전과 배포 버전 동시 추적

LLM 앱에서 배포는 코드만의 문제가 아닙니다. 코드는 그대로인데 프롬프트가 바뀌면 출력이 완전히 달라집니다. EP05에서 코드·모델·프롬프트·보안 규칙을 하나의 세트로 배포해야 한다고 했습니다. 여기서는 그 "세트"를 로그에 어떻게 남기는지 보겠습니다.

```python
# 배포 시점에 환경변수로 주입
DEPLOYMENT_ID = os.environ.get("DEPLOYMENT_ID", "local-dev")
PROMPT_VERSION = os.environ.get("PROMPT_VERSION", "v1.0")
SECURITY_RULES_VERSION = os.environ.get("SECURITY_RULES_VERSION", "v1.0")
```

`RequestContext`에 이 값을 추가하면, 로그 한 줄에 "이 요청은 어떤 배포 + 어떤 프롬프트 + 어떤 보안 규칙 조합에서 나왔는가"가 기록됩니다. 품질이 갑자기 흔들릴 때 이 세 값으로 필터링하면 원인 후보를 빠르게 좁힐 수 있습니다.

실제로 자주 보는 패턴입니다.

| 증상 | 필터 | 원인 후보 |
|------|------|----------|
| 품질 점수 하락, 코드 배포 없음 | `prompt_version` 변경 확인 | 프롬프트 수정 부작용 |
| 비용 급증, 프롬프트 동일 | `model` 변경 확인 | 모델 스왑 후 출력 길이 증가 |
| 차단율 상승, 정상 입력도 차단 | `security_rules_version` 확인 | 보안 규칙 오탐 패턴 추가 |

## 운영 성숙도 종료 조건

"이제 운영이 완성됐다"는 감각이 아니라 기준으로 판단해야 합니다. 팀원이 바뀌어도 같은 절차로 같은 품질을 낼 수 있는 상태가 완성입니다. 다음 네 가지를 종료 조건으로 제안합니다.

**① 요청 추적 가능성** — 임의의 `request_id` 하나를 주면, 보안 판정·모델 호출·비용·품질·최종 응답 상태를 한 줄로 설명할 수 있습니다.

**② 장애 대응 속도** — 알람 발생 후 30분 이내에 영향 범위(몇 건, 어떤 사용자층)와 원인 가설을 데이터로 제시할 수 있습니다. "확인 중입니다"가 30분 이상 지속되면 추적 체계에 구멍이 있다는 신호입니다.

**③ 회귀 방지 자동화** — 새 프롬프트 버전을 배포하기 전에 EP03의 평가 스위트와 EP04의 보안 테스트가 자동으로 실행됩니다. 수동 검토에만 의존하면 배포 속도가 사람의 가용성에 묶입니다.

**④ 임계치 기반 경고** — 비용 급증, 품질 하락, 차단율 이상, 지연 시간 증가를 사람이 대시보드를 보다가 발견하는 것이 아니라, 시스템이 먼저 알려 줍니다.

```python
# 종료 조건 점검 예시
def check_maturity(report: dict) -> list[str]:
    """일일 리포트 기준으로 미달 항목을 반환한다."""
    issues = []
    if report.get("blocked_rate", 0) > 0.15:
        issues.append("차단율 15% 초과 — 보안 규칙 오탐 점검 필요")
    if report.get("eval_attention_rate", 0) > 0.10:
        issues.append("평가 주의율 10% 초과 — 프롬프트 품질 점검 필요")
    if report.get("latency_p95_ms", 0) > 3000:
        issues.append("P95 지연 3초 초과 — 모델 응답 또는 네트워크 점검 필요")
    return issues
```

네 가지가 모두 충족되면 운영은 "경험 많은 사람의 감각"에서 "팀 누구나 따를 수 있는 절차"로 전환됩니다.

## 팀 책임 경계

기술적 통합이 끝나도 책임 경계가 모호하면 장애 대응은 느립니다. 통합 파이프라인이 "누가 무엇을 고치는가"를 더 명확하게 만들어야 합니다.

| 레이어 | 소유 팀 | 변경 시 영향 범위 |
|--------|---------|------------------|
| 프롬프트 + 평가 기준 | 애플리케이션 팀 | 품질 점수, 출력 형태 |
| 보안 규칙 | 보안 팀 | 차단율, 사용자 경험 |
| 배포 인프라 + 관측 | 플랫폼 팀 | 가용성, 지연 시간 |
| 공통 로그 스키마 | **공동 소유** | 전 레이어 조인 가능성 |

공통 로그 스키마를 공동 소유로 두는 이유가 있습니다. 어느 한 팀이 필드를 임의로 바꾸면 다른 팀의 대시보드가 깨집니다. 스키마 변경은 PR 리뷰처럼 관련 팀 합의를 거쳐야 합니다.

주간 운영 회의에서도 같은 리포트를 봐야 합니다. 팀마다 다른 숫자를 보면 같은 사건을 다르게 해석합니다. `build_daily_report()`의 출력을 공식 회의 자료로 쓰면, "어떤 숫자를 믿을 것인가"라는 논쟁이 사라집니다.

## 운영 체크리스트

- [ ] 모든 레이어가 동일한 `request_id`를 참조한다
- [ ] 실행 순서가 코드와 문서 양쪽에 계약으로 명시되어 있다
- [ ] 보안 차단 시 모델 호출 전에 멈추고, 비용이 발생하지 않는다
- [ ] 구조화 로그 한 줄에 보안·비용·품질·지연 정보가 모두 포함된다
- [ ] `/health`에 누적 호출 수, 누적 비용, 차단 수가 노출된다
- [ ] 프롬프트 버전과 배포 버전이 로그에 함께 기록된다
- [ ] 일일 리포트로 비용·품질·차단·지연을 한 페이지에서 확인할 수 있다
- [ ] 운영 성숙도 종료 조건 네 가지를 정기적으로 점검한다

## 정리

EP01에서 로그를 만들고, EP02에서 비용을 세고, EP03에서 품질을 측정하고, EP04에서 위험을 차단하고, EP05에서 안전하게 배포했습니다. 이번 글에서는 이 다섯 레이어를 하나의 `RequestContext` 위에 올려, 요청 한 건의 전체 수명을 끊김 없이 설명할 수 있는 상태를 만들었습니다.

다음 단계는 새 기능을 추가하는 일이 아닙니다. 이 신호를 저장소(BigQuery, ClickHouse 등)에 적재하고, 임계치 경고를 연결하고, 주간 추세 대시보드를 만드는 일입니다. 구조가 잡혀 있으니 도구는 팀 상황에 맞게 고르면 됩니다.

운영 완성은 "더 만드는 것"이 아니라, "이미 만든 것을 끊지 않는 것"입니다.

## 처음 질문으로 돌아가기

- **모니터링, 비용, 평가, 보안, 배포가 각각 독립적으로 잘 돌아가도 운영 공백이 생기는 이유는 무엇일까요?**
  각 레이어가 자체 식별자를 사용하면 요청 한 건을 레이어 간에 연결할 수 없습니다. 장애 때 "이 요청의 비용과 보안 판정과 품질을 함께 보여 달라"는 질문에 답할 수 없고, 원인 분석이 타임스탬프 추정에 의존하게 됩니다.

- **한 요청의 전체 수명을 추적하려면 어떤 공통 계약이 모든 레이어에 필요할까요?**
  단일 `request_id` 전파, 고정된 실행 순서, 통일된 필드 이름과 의미입니다. 이 세 가지가 계약으로 존재해야 로그를 조인할 수 있고, "어디서 멈췄는가"를 즉시 판별할 수 있습니다.

- **운영 성숙도를 "감각"이 아니라 "기준"으로 판단하려면 어떤 종료 조건을 정의해야 할까요?**
  요청 추적 가능성, 30분 이내 장애 대응, 회귀 방지 자동화, 임계치 기반 경고. 이 네 가지가 충족되면 팀원이 바뀌어도 같은 절차로 같은 품질을 유지할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM Apps Ops 101 (1/6): LLM 앱 모니터링과 로깅](./01-monitoring-and-logging.md)
- [LLM Apps Ops 101 (2/6): LLM 비용 추적과 최적화](./02-cost-tracking.md)
- [LLM Apps Ops 101 (3/6): LLM 출력 품질 평가](./03-evaluation.md)
- [LLM Apps Ops 101 (4/6): LLM 앱 보안](./04-security.md)
- [LLM Apps Ops 101 (5/6): LLM 앱 배포 전략](./05-deployment.md)
- **LLM Apps Ops 101 (6/6): LLM 앱 운영 완성 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [LLM Apps Ops 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/llm-apps-ops-101/ko)
- [OpenTelemetry Context Propagation](https://opentelemetry.io/docs/concepts/context-propagation/)
- [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)
- [Structured Logging Best Practices](https://www.structlog.org/en/stable/why.html)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

Tags: LLMOps, Observability, Python, LLM
