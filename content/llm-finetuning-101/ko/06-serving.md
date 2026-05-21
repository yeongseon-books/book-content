---
title: "LLM Fine-tuning 101 (6/6): 모델 서빙"
series: llm-finetuning-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Fine-tuning
- Serving
- FastAPI
- Inference
- Adapter
- Python
last_reviewed: '2026-05-12'
seo_description: 서빙 시스템은 API, 모델, 가중치 저장소로 역할을 나눠 봐야 합니다.
---

# LLM Fine-tuning 101 (6/6): 모델 서빙

서빙 단계에서는 학습 때와 다른 종류의 트레이드오프가 앞에 나옵니다. 이 글은 LLM Finetuning 101 시리즈의 마지막 글입니다. 여기서는 시스템을 네 개 층으로 나눠서 API 경계가 어디서 끝나는지, 추론은 어디서 시작하는지, 그리고 어댑터가 배포 선택지를 어떻게 바꾸는지 정리하겠습니다.

6편의 목표는 모델을 더 똑똑하게 만드는 것이 아닙니다. 이미 준비된 모델을 **예측 가능한 HTTP 계약 뒤에 두는 것**입니다. 학습은 배치와 에폭으로 사고하지만, 서빙은 요청당 지연 시간과 동시성으로 사고해야 합니다. 같은 모델이라도 운영 관점은 완전히 달라집니다.

![LLM Fine-tuning 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/06/06-02-what-this-demo-isolates-on-purpose.ko.png)
*LLM Fine-tuning 101 6장 흐름 개요*

## 먼저 던지는 질문

- 파인튜닝된 작은 모델을 FastAPI 엔드포인트 뒤에 두기 위한 최소 구조는 무엇일까요?
- 서빙 코드에서 학습과 추론의 경계는 어디에 그어야 할까요?
- 브라우저를 열지 않고도 엔드포인트를 어떻게 검증할 수 있을까요?

## 왜 이 글이 중요한가

시리즈 마지막 단계에서는 학습된 어댑터를 API 뒤에 둡니다. 운영에서는 학습 코드와 서빙 코드를 분리하는 것이 원칙이지만, 작은 데모에서는 한 번의 미세 조정 뒤에 바로 엔드포인트로 감싸 보면 전체 흐름을 한눈에 이해하기 쉽습니다.

서빙을 따로 떼어 보는 이유는 분명합니다. 학습은 배치 단위 효율을 보지만, 서빙은 **요청 하나의 지연 시간**과 **동시 처리량**을 봅니다. 같은 모델이라도 코드 구조, 메모리 정책, 에러 처리 방식이 달라집니다. 6편은 그 전환을 가장 작은 단위로 연습하는 글입니다.

## 멘탈 모델

서빙 시스템은 네 개 층으로 분해할 수 있습니다.

```text
[client] -> HTTP -> [API layer] -> [model layer] -> [weights store]
                       |              |              |
                    FastAPI      tokenizer +     base model
                    Pydantic     model.generate  + adapter
```

- **API layer**는 요청과 응답 직렬화, 검증, 에러 처리, 인증, 관측성을 맡습니다.
- **Model layer**는 토크나이저, 생성 옵션, 후처리를 맡습니다.
- **Weights store**는 베이스 모델과 LoRA 어댑터를 관리합니다.

LoRA의 장점은 특히 가중치 저장소에서 드러납니다. 큰 베이스 모델 하나를 메모리에 올려 두고 어댑터만 바꾸면, 같은 머신에서 여러 모델을 상대적으로 가볍게 서빙할 수 있습니다.

추가로 기억할 사실도 두 가지가 있습니다.

- **단일 요청 지연 시간** = tokenize + generate + decode 이며, 보통 generate가 90% 이상을 차지합니다.
- 배칭은 처리량을 높이지만 지연 시간도 함께 올립니다. 둘은 맞바꾸는 관계입니다.

## 핵심 개념

| 항목 | 의미 |
| --- | --- |
| `FastAPI` | 빠른 비동기 Python 웹 프레임워크입니다. Pydantic으로 요청 검증을 자동화합니다. |
| `TestClient` | `uvicorn` 없이 메모리 안에서 앱을 호출하는 테스트 도구입니다. |
| `/health` | 서비스가 살아 있는지 확인하는 가벼운 엔드포인트입니다. 로드 밸런서가 자주 사용합니다. |
| `/generate` | 실제 추론을 수행하는 엔드포인트입니다. |
| `model.generate()` | 토큰을 한 개씩 autoregressive하게 생성하는 메서드입니다. |
| `max_new_tokens` | 생성 길이 상한입니다. 무한히 길어지는 응답을 막는 데 필수입니다. |
| Adapter merge | LoRA 어댑터를 베이스에 합쳐 단일 가중치 세트로 만드는 선택적 작업입니다. |
| Cold start | 모델을 처음 로드하는 시간입니다. 보통 첫 요청에 가장 크게 영향을 줍니다. |

## Before vs. After

**Before**

모델 결과는 학습을 돌린 노트북에서만 볼 수 있습니다. 동료에게 공유하려면 코드와 실행 방법을 매번 같이 전달해야 합니다.

**After**

6편의 패턴을 적용하면 동료는 아래 한 줄로 모델을 호출할 수 있습니다.

```bash
curl -X POST http://localhost:8000/generate -d '{"prompt":"Python function example"}'
{"completion":"Python function example: def add(a, b): return a + b"}
```

여기서 확인할 것은 세 가지입니다. 모델이 HTTP 계약 뒤에 있는지, `TestClient`로 CI 검증이 가능한지, 그리고 어댑터만 바꿔 같은 인프라에서 다른 모델로 전환할 수 있는지입니다.

## 이 데모가 의도적으로 분리하는 것

실전에서는 모델 로딩, 요청 검증, 생성 옵션, 응답 직렬화, 관측성 로그가 모두 서로 다른 책임입니다. 이 글의 예제는 그중에서도 **모델 준비**와 **HTTP 계약**만 최소 크기로 보여 줍니다. 작은 데모에서도 `/health`와 `/generate`를 분리해 두면 운영 코드로 확장하기가 훨씬 쉬워집니다.

![이 데모가 의도적으로 분리하는 것](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/06/06-01-what-this-demo-isolates-on-purpose.ko.png)

*이 데모가 의도적으로 분리하는 것*

## 단계별 설명

### 1단계 — FastAPI 앱 골격을 만듭니다

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

### 2단계 — 앱 시작 시 한 번만 모델을 로드합니다

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base = AutoModelForCausalLM.from_pretrained("sshleifer/tiny-gpt2")
model = PeftModel.from_pretrained(base, "artifacts/lora-adapter")
tokenizer = AutoTokenizer.from_pretrained("sshleifer/tiny-gpt2")
model.eval()
```

`model.eval()`을 빼먹으면 드롭아웃이 살아 있어 같은 입력에도 다른 결과가 나올 수 있습니다. 서빙에서는 절대 빠뜨리면 안 되는 한 줄입니다.

### 3단계 — `/generate` 엔드포인트를 만듭니다

```python
from pydantic import BaseModel

class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 32

@app.post("/generate")
def generate(req: GenerateRequest) -> dict:
    ids = tokenizer(req.prompt, return_tensors="pt").input_ids
    out = model.generate(ids, max_new_tokens=req.max_new_tokens)
    text = tokenizer.decode(out[0], skip_special_tokens=True)
    return {"completion": text}
```

Pydantic 모델을 사용하면 잘못된 요청이 모델 계층까지 내려오기 전에 걸러집니다. 작은 예제에서도 이 경계는 유지하는 편이 좋습니다.

### 4단계 — `TestClient`로 자체 검증합니다

```python
from fastapi.testclient import TestClient

client = TestClient(app)
assert client.get("/health").json() == {"status": "ok"}
print(client.post("/generate", json={"prompt": "Python function example"}).json())
```

`TestClient`는 `uvicorn` 프로세스를 띄우지 않고 메모리 안에서 앱을 호출합니다. 그래서 CI에 바로 넣기 좋습니다.

### 5단계 — 실제 서버를 실행합니다

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

이제 다른 머신에서 `curl`로 호출하거나 Postman으로 확인할 수 있습니다.

## 이 코드에서 봐야 할 것

![FastAPI 추론 요청과 엔드포인트 분기 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/06/06-03-what-to-notice-in-this-code.ko.png)

*FastAPI 추론 요청과 엔드포인트 분기 흐름*

- 모델 로딩은 앱 시작 시 한 번만 실행됩니다. 요청마다 로드하면 지연 시간이 수십 배로 늘어날 수 있습니다.
- `/health`와 `/generate`를 분리하면 모델 상태 문제와 추론 실패 원인을 구분하기 쉬워집니다.
- `TestClient`는 `uvicorn` 없이도 엔드포인트 계약을 검증할 수 있어 CI 친화적입니다.
- Pydantic 검증은 잘못된 입력이 모델로 흘러드는 것을 막는 가장 가벼운 방어선입니다.

## 자주 하는 실수

![지연 시간과 품질 사이의 선택 기준](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/06/06-04-where-engineers-get-confused.ko.png)

*지연 시간과 품질 사이의 선택 기준*

- **요청마다 모델을 로드하는 실수**: 모든 요청이 콜드 스타트가 되어 수 초의 지연이 붙습니다. 모델은 앱 시작 시 한 번만 올려야 합니다.
- **`max_new_tokens`를 지정하지 않는 실수**: 기본값에 기대면 의도치 않게 긴 응답이 생성되고 지연 시간이 튈 수 있습니다.
- **`model.eval()`을 빼먹는 실수**: 드롭아웃 때문에 비결정적 출력이 나오고, 디버깅이 어려워집니다.
- **에러를 그대로 노출하는 실수**: 스택 트레이스를 클라이언트에 그대로 보내면 보안 위험이 됩니다. 실제 서비스에서는 `HTTPException`으로 감싸야 합니다.
- **타임아웃을 두지 않는 실수**: 30초짜리 요청 하나가 워커를 오래 묶을 수 있습니다. 클라이언트와 서버 양쪽에 제한이 필요합니다.
- **GPU 메모리 모니터링을 빼먹는 실수**: 조용한 OOM은 워커를 죽이면서도 겉보기 health check는 통과하게 만들 수 있습니다.

## 실무 메모

- **학습 코드와 서빙 코드를 분리합니다**: 같은 저장소 안에서도 디렉터리를 나누고, 서빙 쪽은 `datasets`, `wandb` 같은 학습 의존성을 끌어오지 않게 합니다.
- **어댑터 멀티테넌시를 고려합니다**: 베이스 하나와 여러 어댑터를 조합하면 같은 머신에서 여러 파인튜닝 모델을 상대적으로 효율적으로 운영할 수 있습니다.
- **배칭 전략을 별도로 봅니다**: vLLM, TGI는 동적 배칭을 제공하고, 직접 FastAPI를 쓴다면 `asyncio.Queue` 기반 마이크로배칭을 고민할 수 있습니다.
- **스트리밍 응답을 준비합니다**: 긴 출력은 `StreamingResponse`로 토큰 단위 전송을 하면 체감 지연이 크게 줄어듭니다.
- **관측성을 기본값으로 둡니다**: 요청당 프롬프트 토큰 수, 응답 토큰 수, 총 지연 시간, GPU 메모리를 로그와 메트릭으로 남겨야 합니다.

## 체크리스트

- [ ] 모델 준비 책임과 HTTP 엔드포인트 책임을 구분해서 설명할 수 있습니다.
- [ ] `TestClient`로 `/health`와 `/generate`를 검증했습니다.
- [ ] 작은 데모 모델과 실제 운영 서빙의 차이를 이해했습니다.
- [ ] LoRA 어댑터를 베이스와 분리 배포할 때 무엇이 좋아지는지 설명할 수 있습니다.
- [ ] 1편부터 6편까지의 흐름을 하나의 연속된 과정으로 연결할 수 있습니다.

## 연습 문제

1. `/generate`에 `temperature`와 `top_p`를 추가해 보세요. 같은 프롬프트에서 출력이 어떻게 달라지나요?
2. `time.perf_counter()`로 요청 지연 시간을 측정하고, `max_new_tokens`를 8, 32, 128로 바꿨을 때 차이를 비교해 보세요.
3. 어댑터 두 개를 준비한 뒤 `/generate?adapter=A`처럼 런타임에 바꿔 끼우는 코드를 작성해 보세요.

## 정리 · 시리즈 마무리

이제 파인튜닝 시리즈의 최소 end-to-end 경로가 완성됐습니다. 1편에서 수식으로 감각을 잡고, 2편에서 데이터를 준비하고, 3편에서 LoRA를 붙이고, 4편에서 한 스텝 학습을 검증하고, 5편에서 평가하고, 6편에서 마지막으로 HTTP 엔드포인트까지 연결했습니다.

다음 단계는 시리즈를 떠나 여러분의 도메인 데이터로 같은 흐름을 반복하는 일입니다. 데이터 100~1000개, LoRA rank 8~16, 1 epoch, perplexity와 골든 세트 평가, FastAPI 서빙이라는 작은 레시피만 손에 익혀도, 작은 모델 하나를 서비스로 가져가는 기본 경로는 충분히 설명할 수 있습니다.

## 서빙 아키텍처 확장: 단일 프로세스에서 운영형 구성으로 가는 단계

6편의 예제는 의도적으로 단순합니다. 실제 운영에서는 보통 아래 단계를 거쳐 확장합니다.

| 단계 | 구성 | 특징 | 전환 신호 |
| --- | --- | --- | --- |
| local demo | FastAPI + 단일 모델 프로세스 | 구현 빠름 | 팀 내부 데모 |
| staging | FastAPI + 모델 워커 분리 | 장애 분리 쉬움 | 동시 요청 증가 |
| production | API Gateway + 모델 서버(vLLM/TGI) + 관측성 | 확장성/가시성 강화 | SLA 필요 |

처음부터 production 구성을 모두 도입하기보다, 요청량과 운영 책임이 늘어날 때 단계적으로 전환하는 편이 안전합니다.

## 요청/응답 계약 예시: 스키마를 먼저 고정하기

```json
{
  "prompt": "FastAPI 예외 처리 예시",
  "max_new_tokens": 64,
  "temperature": 0.2,
  "top_p": 0.9,
  "adapter": "customer-support-v1"
}
```

```json
{
  "completion": "...",
  "model": "llama-3-8b-base",
  "adapter": "customer-support-v1",
  "prompt_tokens": 28,
  "completion_tokens": 54,
  "latency_ms": 412
}
```

운영에서 중요한 것은 "텍스트"만이 아닙니다. 토큰 수와 지연 시간을 같이 반환해야 병목을 추적할 수 있습니다.

## 어댑터 핫스왑 패턴: 베이스 하나로 여러 도메인 서빙

```python
from peft import PeftModel

BASE_ID = "meta-llama/Llama-3-8B-Instruct"
ADAPTERS = {
    "customer-support-v1": "adapters/customer-support-v1",
    "dev-docs-v2": "adapters/dev-docs-v2",
}

def load_adapter(base_model, adapter_name):
    if adapter_name not in ADAPTERS:
        raise ValueError(f"unknown adapter: {adapter_name}")
    return PeftModel.from_pretrained(base_model, ADAPTERS[adapter_name])
```

이 패턴은 메모리와 배포 속도에서 큰 이점을 줍니다. 단, 어댑터와 베이스 버전 호환성을 엄격히 관리해야 합니다.

## 지연 시간 측정 예시: 토큰 단위로 원인을 분리하기

| 실험 | `max_new_tokens` | 평균 지연(ms) | p95(ms) |
| --- | --- | --- | --- |
| A | 32 | 240 | 330 |
| B | 64 | 410 | 560 |
| C | 128 | 760 | 1020 |

대부분의 경우 지연 시간 증가는 생성 길이와 거의 선형으로 움직입니다. 그래서 서빙 정책에서 `max_new_tokens` 상한은 필수입니다.

## VRAM 운영 메모: 추론 단계에서 주로 보는 항목

| 항목 | 관측 포인트 | 대응 |
| --- | --- | --- |
| 베이스 모델 메모리 | 프로세스 시작 직후 | 양자화/모델 다운사이징 |
| KV 캐시 증가 | 긴 생성 요청 | 길이 제한, 스트리밍 |
| 동시 요청 피크 | 부하 테스트 시점 | 동적 배칭, 워커 증설 |
| OOM 재시작 | 로그/메트릭 알람 | 요청 제한, 큐 기반 제어 |

학습 때와 달리 추론은 KV 캐시 영향이 크므로, 긴 응답 요청 패턴을 반드시 따로 관찰해야 합니다.

## before/after 운영 예시: 실험 코드에서 서비스 계약으로

```text
[Before]
노트북에서만 model.generate() 호출 가능
요청 지연, 토큰 수, 실패율 기록 없음

[After]
/generate API로 팀 전체가 동일 계약 사용
latency_ms, prompt_tokens, completion_tokens 수집
골든 프롬프트를 CI에서 자동 호출해 회귀 감지
```

6편의 목적은 모델 성능을 올리는 것이 아니라, 이렇게 "반복 가능한 운영 경계"를 세우는 데 있습니다.

## 배포 체크리스트: 릴리스 직전에 반드시 확인할 것

1. `/health`와 `/generate` 분리 및 상태 코드 정책 확정
2. `max_new_tokens`, `temperature`, `top_p` 기본값 문서화
3. 어댑터 버전, 베이스 버전, 토크나이저 버전 동기화
4. 요청 로그에 토큰 수/지연 시간 포함
5. 골든 프롬프트 회귀 테스트 통과

이 다섯 항목이 고정되면 이후 모델 업데이트를 훨씬 안전하게 반복할 수 있습니다.

## 실전 패턴 추가: 데이터 준비, LoRA 설정, 학습 입력 검증을 한 흐름으로 점검하기

파인튜닝 품질은 모델 아키텍처보다 입력 계약에서 먼저 결정됩니다. 데이터셋 템플릿, LoRA 설정, 길이 통계를 따로 보지 말고 같은 파이프라인에서 검증해야 디버깅 비용이 줄어듭니다.

```python
from dataclasses import dataclass
from typing import Iterable

from peft import LoraConfig

@dataclass
class Sample:
    instruction: str
    input: str
    output: str

def render(sample: Sample) -> str:
    return (
        "### Instruction:
" + sample.instruction + "

"
        "### Input:
" + sample.input + "

"
        "### Response:
" + sample.output
    )

def build_lora_config() -> LoraConfig:
    return LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )

def length_stats(lengths: Iterable[int]) -> tuple[int, float, int]:
    data = sorted(lengths)
    if not data:
        return 0, 0.0, 0
    avg = sum(data) / len(data)
    p95 = data[int(len(data) * 0.95) - 1]
    return min(data), avg, p95
```

운영 관점에서는 `target_modules`와 데이터 템플릿이 함께 관리되어야 합니다. 템플릿이 바뀌면 토큰 길이 분포가 바뀌고, 이는 배치 크기와 학습 안정성에 바로 영향을 줍니다. 따라서 데이터 버전, LoRA 설정 버전, 평가 지표를 같은 실험 단위로 묶어 기록하는 것이 필수입니다. 이렇게 해야 특정 품질 변화가 데이터 문제인지, 어댑터 설정 문제인지 빠르게 분리할 수 있습니다.

## FastAPI 서빙 코드 패턴: 요청 검증, 생성, 메트릭을 분리하기

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import time

app = FastAPI()

class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1)
    max_new_tokens: int = Field(default=64, ge=1, le=256)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)

@app.post("/generate")
def generate(req: GenerateRequest):
    started = time.perf_counter()
    try:
        ids = tokenizer(req.prompt, return_tensors="pt").input_ids
        out = model.generate(
            ids,
            max_new_tokens=req.max_new_tokens,
            temperature=req.temperature,
        )
        text = tokenizer.decode(out[0], skip_special_tokens=True)
        latency_ms = int((time.perf_counter() - started) * 1000)
        return {
            "completion": text,
            "prompt_tokens": int(ids.shape[-1]),
            "completion_tokens": int(out.shape[-1] - ids.shape[-1]),
            "latency_ms": latency_ms,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail="generation failed") from exc
```

예제는 단순하지만, 요청 검증과 에러 경계를 분리해 두면 운영 장애 대응이 훨씬 쉬워집니다.

## 동시성과 처리량: 단일 워커 한계를 빠르게 확인하는 법

| 항목 | 단일 프로세스 FastAPI | 모델 서버(vLLM/TGI) |
| --- | --- | --- |
| 구현 난이도 | 낮음 | 중간~높음 |
| 동시 요청 처리 | 제한적 | 강함 |
| 동적 배칭 | 직접 구현 필요 | 기본 제공 |
| 운영 가시성 | 직접 구축 | 도구 제공 많음 |

요청량이 늘면 "코드 최적화"보다 런타임 아키텍처 전환이 더 큰 효과를 내는 경우가 많습니다.

## 서빙 전후 응답 비교 예시

```text
[Prompt]
FastAPI에서 입력 검증 실패 시 처리 패턴을 보여 주세요.

[학습 직후 로컬 생성]
You can validate input and return error.

[서빙 엔드포인트 응답]
@app.post("/users")
def create_user(req: UserCreate):
    if len(req.name) < 2:
        raise HTTPException(status_code=400, detail="name too short")
    return {"ok": True}
```

서빙 단계에서는 텍스트 품질뿐 아니라 지연 시간과 오류율이 함께 기준이 됩니다.

## 운영 알람 기준 예시

| 지표 | 경고 기준 | 치명 기준 |
| --- | --- | --- |
| p95 latency | 1200ms 초과 5분 | 2000ms 초과 5분 |
| error rate | 1% 초과 | 3% 초과 |
| OOM 재시작 | 1회/시간 | 3회/시간 |
| health check 실패 | 2회 연속 | 5회 연속 |

이런 기준이 있어야 "느려졌다"를 감정이 아니라 운영 신호로 다룰 수 있습니다.

## 서빙 검증 명령 예시: 브라우저 없이 확인하는 루프

```bash
# health
curl -s http://localhost:8000/health

# generation
curl -s -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"FastAPI 404 처리 예시","max_new_tokens":48}'
```

이 두 명령은 CI 파이프라인에서도 그대로 사용할 수 있습니다. 서버 부팅, 엔드포인트 계약, 기본 생성 동작을 최소 비용으로 검증합니다.

## 배포 모드 비교: 단일 어댑터 vs 멀티 어댑터

| 모드 | 장점 | 주의점 |
| --- | --- | --- |
| 단일 어댑터 고정 | 운영 단순, 디버깅 쉬움 | 도메인 확장 느림 |
| 멀티 어댑터 라우팅 | 같은 베이스로 여러 서비스 제공 | 라우팅/권한/버전 관리 복잡 |

초기에는 단일 어댑터 모드로 안정화하고, 품질 기준이 고정된 뒤 멀티 어댑터로 확장하는 순서가 일반적입니다.

운영 초기에 가장 중요한 것은 기능 추가보다 장애 복구 경로를 먼저 정해 두는 일입니다. 어댑터 롤백 절차와 기본 베이스 모델 fallback 절차를 문서화해 두면 실제 incident 대응 속도가 크게 달라집니다.

## 처음 질문으로 돌아가기

- **파인튜닝된 작은 모델을 FastAPI 엔드포인트 뒤에 두기 위한 최소 구조는 무엇일까요?**
  - 본문의 기준은 모델 서빙를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **서빙 코드에서 학습과 추론의 경계는 어디에 그어야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **브라우저를 열지 않고도 엔드포인트를 어떻게 검증할 수 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM Fine-tuning 101 (1/6): LLM 파인튜닝 입문](./01-intro.md)
- [LLM Fine-tuning 101 (2/6): 데이터셋 준비와 전처리](./02-dataset.md)
- [LLM Fine-tuning 101 (3/6): LoRA 어댑터 구성](./03-lora.md)
- [LLM Fine-tuning 101 (4/6): 학습 루프와 하이퍼파라미터](./04-training.md)
- [LLM Fine-tuning 101 (5/6): 모델 평가](./05-evaluation.md)
- **LLM Fine-tuning 101 (6/6): 모델 서빙 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Starlette TestClient reference](https://www.starlette.io/testclient/)
- [PEFT — Multiple adapters](https://huggingface.co/docs/peft/main/en/developer_guides/lora#multiple-adapters)
- [vLLM — high-throughput LLM serving](https://github.com/vllm-project/vllm)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-finetuning-101/ko/06-serving)

Tags: Fine-tuning, LoRA, LLM, Python
