---
title: 모델 서빙
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

# 모델 서빙

서빙 단계에서는 학습 때와 다른 종류의 트레이드오프가 앞에 나옵니다. 이 글은 LLM Finetuning 101 시리즈의 마지막 글입니다. 여기서는 시스템을 네 개 층으로 나눠서 API 경계가 어디서 끝나는지, 추론은 어디서 시작하는지, 그리고 어댑터가 배포 선택지를 어떻게 바꾸는지 정리하겠습니다.

6편의 목표는 모델을 더 똑똑하게 만드는 것이 아닙니다. 이미 준비된 모델을 **예측 가능한 HTTP 계약 뒤에 두는 것**입니다. 학습은 배치와 에폭으로 사고하지만, 서빙은 요청당 지연 시간과 동시성으로 사고해야 합니다. 같은 모델이라도 운영 관점은 완전히 달라집니다.

## 이 글에서 다룰 문제

![이 글에서 다룰 문제](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/06/06-01-questions-this-post-answers.ko.png)

*이 글에서 다룰 문제*

- 파인튜닝된 작은 모델을 FastAPI 엔드포인트 뒤에 두기 위한 최소 구조는 무엇일까요?
- 서빙 코드에서 학습과 추론의 경계는 어디에 그어야 할까요?
- 브라우저를 열지 않고도 엔드포인트를 어떻게 검증할 수 있을까요?
- LoRA 어댑터를 베이스 모델과 분리 배포하면 무엇을 얻을 수 있을까요?

> 서빙은 모델을 더 똑똑하게 만드는 단계가 아닙니다. 이미 준비된 모델을 예측 가능한 HTTP 계약 뒤에 두는 단계입니다.

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

![모델 준비와 HTTP 계약의 분리](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/06/06-02-what-this-demo-isolates-on-purpose.ko.png)

*모델 준비와 HTTP 계약의 분리*

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

<!-- toc:begin -->
## 시리즈 목차

- [LLM 파인튜닝 입문](./01-intro.md)
- [데이터셋 준비와 전처리](./02-dataset.md)
- [LoRA 어댑터 구성](./03-lora.md)
- [학습 루프와 하이퍼파라미터](./04-training.md)
- [모델 평가](./05-evaluation.md)
- **모델 서빙 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Starlette TestClient reference](https://www.starlette.io/testclient/)
- [PEFT — Multiple adapters](https://huggingface.co/docs/peft/main/en/developer_guides/lora#multiple-adapters)
- [vLLM — high-throughput LLM serving](https://github.com/vllm-project/vllm)

Tags: Fine-tuning, LoRA, LLM, Python
