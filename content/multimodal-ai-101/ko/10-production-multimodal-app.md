---
title: "Multimodal AI 101 (10/10): Production Multimodal Application 구축"
series: multimodal-ai-101
episode: 10
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Production
- Multimodal API
- FastAPI
- Inference Pipeline
- Cost Optimization
- Caching
last_reviewed: '2026-05-12'
seo_description: 지금까지 9편에 걸쳐 image encoder, VLM 아키텍처, captioning, multimodal RAG,
  audio…
---

# Multimodal AI 101 (10/10): Production Multimodal Application 구축

멀티모달 데모를 한 번 띄우는 것과 production 애플리케이션을 운영하는 것은 완전히 다른 문제입니다. 데모에서는 한 장의 이미지와 한 번의 응답이 전부지만, 실제 서비스에서는 업로드, 전처리, 모델 선택, 캐싱, 비동기 처리, 보안, 관측성, 비용 회수가 모두 한 흐름 안에서 이어집니다. 사용자에게는 “이미지 한 장 올렸다”는 단순한 동작이지만, 서버 안에서는 여러 modality별 파이프라인이 동시에 움직입니다.

특히 production 멀티모달 앱은 모델보다 시스템 설계가 더 중요합니다. 어떤 요청을 동기로 처리할지, 어느 시점에 worker로 넘길지, base64를 그대로 받을지 object storage URL을 쓸지, 어떤 결과를 캐시할지 같은 선택이 성능과 비용을 크게 좌우합니다.

운영 단계에서는 observability와 정책 관리가 핵심이 됩니다. PII가 이미지 안에 숨어 들어오고, warm-up이 안 된 worker가 지연 시간을 튀게 만들고, streaming 응답은 연결 종료 처리까지 신경 써야 합니다. 멀티모달은 모델 기능이 늘어나는 만큼 장애 표면도 넓어집니다.

이 글은 시리즈의 마지막 글로서, 앞선 9편의 개념을 실제 시스템 아키텍처로 묶습니다. 핵심은 하나입니다. 멀티모달 앱은 모델 집합이 아니라 운영 가능한 파이프라인이어야 합니다.

좋은 production 시스템은 모델 성능보다 먼저 요청 흐름과 실패 경로를 명확히 보여 줍니다.

![Multimodal AI 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/10/10-01-big-picture.ko.png)
*Multimodal AI 101 10장 흐름 개요*
> Production Multimodal Application 구축의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- production 멀티모달 앱은 어떤 end-to-end 구성 요소를 반드시 분리해서 설계해야 할까요?
- FastAPI 입구, inference worker, cache, object storage, observability는 어떤 순서로 연결되는 편이 안정적일까요?
- 동기 처리와 비동기 처리 경계는 어떤 기준으로 나누는 것이 현실적일까요?

## 왜 이 글이 중요한가

대부분의 멀티모달 기능은 결국 애플리케이션 안에 들어가야 의미가 있습니다. 따라서 모델을 이해하는 것만큼, 업로드부터 응답까지의 시스템 경로를 설계하는 감각이 중요합니다.

또한 production 아키텍처는 비용 절감과 안정성 확보의 핵심 수단입니다. worker 분리, 캐싱, object storage, observability를 잘 설계하면 같은 모델을 써도 훨씬 싸고 안정적으로 운영할 수 있습니다.

반대로 이 계층을 소홀히 하면 데모에서는 보이지 않던 문제가 한꺼번에 드러납니다. timeout, queue 적체, PII 누출, warm-up 지연, 캐시 불일치가 대표적입니다.

## 핵심 관점

production 아키텍처를 볼 때 가장 먼저 분리해야 할 것은 요청 입구와 추론 실행 계층입니다. FastAPI 같은 API 레이어는 인증, 요청 검증, 업로드 관리, 응답 스트리밍을 담당하고, 실제 모델 추론은 별도 worker가 맡는 편이 훨씬 안정적입니다.

그다음 중요한 것은 재계산을 줄이는 구조입니다. 이미지 해시 기반 캐시, 중간 feature 재사용, object storage URL 전달 같은 설계가 없으면 멀티모달 앱은 아주 쉽게 비싸고 느린 서비스가 됩니다.

마지막으로 관측성과 정책이 빠지면 운영이 불가능합니다. 어떤 모델이 얼마나 오래 걸렸는지, 어떤 modality에서 실패했는지, 어떤 입력이 PII 검사를 통과하지 못했는지를 기록해야만 서비스 품질을 유지할 수 있습니다.

> 프로덕션 멀티모달 앱의 경쟁력은 더 큰 모델보다, 같은 모델을 더 예측 가능하고 더 싸게 운영하는 파이프라인에서 나옵니다.

## 핵심 개념

### 1. End-to-End 시스템 전체 그림

다음과 같은 multimodal Q&A 서비스를 가정합니다.

- 사용자가 이미지 + 질문을 업로드
- 시스템이 caption + OCR + visual Q&A를 실행
- multimodal RAG로 관련 문서를 함께 검색
- 최종 응답을 streaming으로 반환

```text
client ──► API gateway ──► FastAPI app
                                │
                ┌───────────────┼─────────────────┐
                ▼               ▼                 ▼
           image preproc    cache layer       rate limiter
                │               │                 │
                ▼               ▼                 ▼
          inference orchestrator (asyncio)
                │
       ┌────────┼────────┬─────────┬──────────┐
       ▼        ▼        ▼         ▼          ▼
     OCR     Caption   VLM Q&A   Embedding   Vector DB
   (PaddleOCR)(BLIP-2)(LLaVA)   (CLIP)     (FAISS/Qdrant)
                │
                ▼
         response builder ──► streaming SSE
```

각 모델은 별도 GPU worker(또는 Triton/vLLM)에서 돌고, FastAPI는 orchestration만 책임집니다.

### 2. FastAPI 기본 골격

```python
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

@app.post("/v1/multimodal/query")
async def multimodal_query(
    image: UploadFile = File(...),
    question: str = Form(...),
):
    image_bytes = await image.read()
    image_id = await store_image(image_bytes)

    # 1. cache check
    cached = await get_cache(image_id, question)
    if cached:
        return {"answer": cached, "cached": True}

    # 2. parallel pre-extraction
    caption_task = asyncio.create_task(run_caption(image_bytes))
    ocr_task = asyncio.create_task(run_ocr(image_bytes))
    embed_task = asyncio.create_task(run_embed(image_bytes))

    caption, ocr_text, embed = await asyncio.gather(caption_task, ocr_task, embed_task)

    # 3. RAG retrieval
    docs = await search_docs(embed, question, k=4)

    # 4. 스트리밍을 통한 최종 VLM Q&A
    return StreamingResponse(
        stream_vlm_answer(image_bytes, question, caption, ocr_text, docs),
        media_type="text/event-stream",
    )
```

3가지 pre-extraction(caption, OCR, embedding)을 `asyncio.gather`로 병렬 실행하는 것이 latency 핵심입니다. 직렬로 돌리면 3 step latency가 합쳐지지만, 병렬이면 가장 느린 한 step만 보입니다.

### 3. Inference Worker 분리 (vLLM, Triton)

FastAPI는 GPU model을 직접 띄우지 않고, 별도 inference server(vLLM, Triton, TGI)에 HTTP/gRPC로 요청합니다.

```python
import httpx

VLM_ENDPOINT = "http://llava-worker:8000/v1/chat/completions"

async def stream_vlm_answer(image_bytes, question, caption, ocr_text, docs):
    prompt = build_prompt(question, caption, ocr_text, docs)
    payload = {
        "model": "llava-v1.6-mistral-7b",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64(image_bytes)}"}},
            ],
        }],
        "stream": True,
        "max_tokens": 512,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("POST", VLM_ENDPOINT, json=payload) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    yield f"{line}\n\n"
```

worker를 분리하면 model 교체나 GPU scaling이 API 코드 변경 없이 가능합니다. vLLM은 LLaVA, Llama 3 Vision, Qwen-VL 등 multimodal model을 OpenAI 호환 API로 노출합니다.

### 4. Caching Layer

multimodal request는 동일 이미지에 대해 비슷한 질문이 반복됩니다. 3-tier cache가 표준입니다.

| Tier | 키 | 저장소 | TTL |
| --- | --- | --- | --- |
| L1 exact | `hash(image) + question` | Redis | 1시간 |
| L2 semantic | `hash(image) + embed(question)` | Redis + cosine | 24시간 |
| L3 feature | `hash(image)` -> caption/OCR/embed | Postgres | 30일 |

```python
import hashlib
import redis.asyncio as redis

r = redis.from_url("redis://cache:6379")

def image_hash(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

async def get_cache(image_id: str, question: str) -> str | None:
    key = f"qa:{image_id}:{hashlib.sha256(question.encode()).hexdigest()}"
    return await r.get(key)

async def set_cache(image_id: str, question: str, answer: str):
    key = f"qa:{image_id}:{hashlib.sha256(question.encode()).hexdigest()}"
    await r.setex(key, 3600, answer)
```

L3 feature cache가 가장 효율적입니다. caption/OCR/embedding은 결정론적이라 한 번 계산하면 영구 재사용 가능하고, hit rate가 70%대까지 올라갑니다.

### 5. Cost Optimization 체크리스트

multimodal serving cost는 GPU 시간이 90% 이상입니다. 실전 절감 포인트:

- **Batch inference**: vLLM의 continuous batching으로 처리량 5~10배
- **Quantization**: BLIP-2, LLaVA를 4-bit (bitsandbytes, AWQ)로 VRAM 절반
- **Tiered model**: 쉬운 query는 small VLM(CogVLM-7B), 어려운 query는 GPT-4V로 routing
- **Image resize 사전 처리**: 4K 이미지를 그대로 보내면 token이 4배. 1024 long edge로 resize
- **Semantic cache**: question embedding cosine > 0.95이면 cache hit으로 처리
- **Async OCR**: 사용자 응답 후 백그라운드에서 OCR 결과를 DB에 저장(다음 query에 재사용)

월 GPT-4V $5,000을 쓰던 시스템이 이 6가지를 적용하면 $1,200~$1,800 수준까지 떨어지는 게 일반적입니다.

### 6. Observability와 Feedback Loop

production multimodal app은 표준 metric에 multimodal 특유 metric을 추가합니다.

```python
from prometheus_client import Histogram, Counter

inference_latency = Histogram(
    "multimodal_inference_seconds", "End-to-end inference time",
    ["model", "modality"], buckets=[0.1, 0.5, 1, 2, 5, 10, 30],
)
cache_hit = Counter("multimodal_cache_hit_total", "Cache hits", ["tier"])
hallucination_flag = Counter("multimodal_hallucination_total", "Detected hallucinations")
```

추가로 챙겨야 할 것:

- **Image upload size 분포**: P99가 10MB 넘으면 client-side resize를 강제
- **Question length 분포**: token 폭발 사전 감지
- **Hallucination rate**: 답변에 이미지에 없는 객체가 등장하면 small validator로 flag
- **User feedback (thumbs up/down)**: RLHF data로 누적

### 7. Production Rollout 시나리오

새 multimodal model을 배포할 때 권장 순서:

1. **Shadow traffic** (1주): 기존 모델과 병렬 호출, 응답은 비교만, 사용자에게는 기존 응답
2. **Canary 5%** (3일): 일부 사용자에게 신모델 노출, latency/error/hallucination metric 비교
3. **Canary 25%** (3일): 비용/품질 안정성 확인
4. **Full rollout**: 100% 전환, rollback button 준비
5. **Sunset 기존 모델** (2주 후): GPU 회수

multimodal은 single-modality보다 failure mode가 다양해서(이미지 손상, OCR 깨짐, audio sync 등) shadow 단계가 절대 필요합니다.

### 운영에 필요한 보조 구현 예제

마지막으로 production 앱에서는 요청 처리 외에도 운영 보조 코드가 필요합니다. 아래 예제는 그 경계에서 자주 재사용되는 구현을 보강합니다.

```python
from PIL import Image, ImageOps
img = ImageOps.exif_transpose(Image.open(path))
```
## 장애 대응 관점에서 본 멀티모달 파이프라인

프로덕션 멀티모달 앱은 정상 경로보다 실패 경로 설계가 더 중요합니다. 이미지 디코딩 실패, OCR 타임아웃, VLM 과부하, 벡터 DB 지연처럼 modality별 실패가 동시에 생길 수 있으므로 각 단계의 fallback을 명시적으로 두어야 합니다. 예를 들어 OCR이 실패해도 caption+VLM 경로로 축소 응답을 만들고, VLM이 실패하면 검색 결과와 OCR 요약만 반환하는 degraded mode를 준비할 수 있습니다.

```python
class StepFailure(Exception):
    pass

def degrade_response(caption: str | None, ocr_text: str | None, docs: list[str]) -> str:
    parts = []
    if caption:
        parts.append(f"이미지 요약: {caption}")
    if ocr_text:
        parts.append(f"추출 텍스트: {ocr_text[:400]}")
    if docs:
        parts.append("관련 문서: " + ", ".join(docs[:3]))
    return "
".join(parts) if parts else "현재 고급 추론이 지연되어 기본 결과만 제공합니다."
```

이런 축소 응답 경로를 두면 완전 장애를 부분 성능 저하로 바꿀 수 있습니다. 사용자 신뢰를 유지하는 데 중요한 차이를 만듭니다.

## 비용 가드레일: 요청 단위 예산 정책

멀티모달 요청은 이미지 수와 해상도에 따라 비용이 급변합니다. 그래서 요청마다 최대 토큰/이미지 개수/추론 시간을 제한하는 정책이 필요합니다.

```python
def enforce_budget(image_count: int, max_side: int, est_tokens: int) -> None:
    if image_count > 4:
        raise ValueError("한 번에 최대 4개 이미지만 처리합니다.")
    if max_side > 1600:
        raise ValueError("이미지 긴 변은 1600px 이하여야 합니다.")
    if est_tokens > 12000:
        raise ValueError("질문이 너무 길어 처리 예산을 초과했습니다.")
```

이 정책은 사용자 경험을 해치기 위한 제한이 아니라, 전체 서비스 안정성을 지키는 안전장치입니다. 요청 폭주 상황에서 가장 먼저 시스템을 지켜 주는 계층이기도 합니다.

## 품질 루프: 사용자 피드백과 자동 평가 결합

운영이 안정되면 품질 개선 루프를 자동화해야 합니다. 사용자 피드백(thumbs up/down), retrieval 근거 일치율, hallucination 감지 신호를 묶어 주간 리포트를 만들면 모델 교체 우선순위를 명확히 잡을 수 있습니다.

```python
weekly_report = {
    "thumbs_up_rate": 0.0,
    "avg_latency_ms": 0,
    "cache_hit_rate": 0.0,
    "hallucination_rate": 0.0,
    "top_failure_modes": [],
}
```

최종적으로 좋은 멀티모달 운영은 모델 선택의 문제가 아니라 루프 설계의 문제로 수렴합니다. 입력 검증, 실행, 평가, 개선의 루프가 닫혀 있어야 같은 팀이 더 적은 비용으로 더 나은 품질을 유지할 수 있습니다.

## 보안 경계: 업로드 검증과 저장소 격리

멀티모달 서비스는 파일 업로드가 기본이므로 보안 경계 설계가 필수입니다. MIME 타입만 믿지 말고 매직 바이트 검증을 수행하고, 원본 파일은 격리된 버킷에 저장한 뒤 서명 URL로만 접근하게 해야 합니다. 이 단계를 생략하면 악성 파일 업로드 위험이 커집니다.

```python
ALLOWED_MAGIC = {
    b"PNG

": "image/png",
    b"ÿØÿ": "image/jpeg",
}

def sniff_content_type(blob: bytes) -> str | None:
    for magic, ctype in ALLOWED_MAGIC.items():
        if blob.startswith(magic):
            return ctype
    return None
```

또한 로그에는 원본 이미지 대신 해시와 메타데이터만 남기는 편이 안전합니다. 운영 편의성과 개인정보 보호를 함께 만족시키려면 저장소 수명주기 정책까지 포함해 설계해야 합니다.

## 백프레셔와 작업 취소 정책

멀티모달 서비스는 요청당 계산량이 커서 백프레셔 정책이 없으면 쉽게 큐 적체가 발생합니다. 따라서 API 입구에서 동시 작업 수를 제한하고, 대기 시간이 임계값을 넘는 요청은 명확한 오류 메시지와 함께 재시도 전략을 안내해야 합니다.

```python
MAX_INFLIGHT = 200

def should_reject(current_inflight: int) -> bool:
    return current_inflight >= MAX_INFLIGHT
```

또한 사용자가 요청을 취소하면 하위 worker 작업도 같이 중단해야 GPU 시간을 낭비하지 않습니다. 취소 토큰을 worker까지 전달하는 구조를 초기에 넣어 두면 비용 절감 효과가 큽니다.

백프레셔 정책은 기능 제한처럼 보이지만, 실제로는 전체 사용자에게 안정적인 응답 시간을 보장하는 핵심 장치입니다. 멀티모달 운영에서 가장 먼저 준비해야 할 안전장치 중 하나입니다.

## SLA 관점의 단계별 타임아웃 설계

프로덕션에서는 전체 타임아웃만 두지 말고 단계별 타임아웃을 분리해야 합니다. OCR, 임베딩, VLM 각각의 상한 시간을 정하면 장애 시 원인 파악이 빠르고, 부분 실패 fallback도 단순해집니다.

```python
TIMEOUTS = {
    "ocr_sec": 4.0,
    "embed_sec": 2.0,
    "vlm_sec": 18.0,
}
```

이 기준을 넘긴 요청은 취소하고 축소 응답으로 전환하는 정책을 두면, 전체 서비스 지연이 전파되는 것을 막을 수 있습니다.

## 운영 검증 루프: 주간 점검 항목을 고정하기

멀티모달 시스템은 모델 정확도만으로 상태를 판단하면 늦게 대응하게 됩니다. 그래서 주간 운영 회의에서 항상 같은 항목을 점검하는 루프를 고정하는 편이 좋습니다. 예를 들어 요청량, 평균 지연 시간, P95 지연, 오류율, 재시도율, 캐시 히트율, 사용자 불만 비율을 동일 포맷으로 기록하면 작은 이상 징후를 초기에 잡을 수 있습니다.

또한 지표는 기능별로 분해해야 합니다. 단일 "성공률" 수치만 보면 어떤 단계에서 손실이 났는지 알기 어렵습니다. 입력 검증 단계, 전처리 단계, 검색 단계, 생성 단계를 분리해 성공률을 기록하면 병목 구간이 명확해집니다. 이 분해 지표는 모델 교체나 파이프라인 변경 후 회귀를 탐지하는 데 특히 유용합니다.

```python
weekly_health = {
    "request_count": 0,
    "avg_latency_ms": 0,
    "p95_latency_ms": 0,
    "error_rate": 0.0,
    "retry_rate": 0.0,
    "cache_hit_rate": 0.0,
    "user_downvote_rate": 0.0,
}
```

운영 루프를 고정하면 기술 선택도 더 현실적으로 바뀝니다. 새 모델을 도입할 때 "정확도 상승"만 보지 않고, 지연 증가와 비용 증가를 같은 표에서 비교할 수 있기 때문입니다. 결국 프로덕션 품질은 한 번의 모델 업그레이드가 아니라, 반복 가능한 점검 루프를 통해 유지됩니다.

## 흔히 헷갈리는 지점

- **Image upload를 동기로 처리** 큰 파일을 sync로 읽으면 event loop가 막힙니다. `await image.read()`는 OK지만, 추가 처리(resize, hash)는 `asyncio.to_thread()`나 별도 worker process로 빼세요.
- **Model warm-up 미반영** GPU model은 cold start에서 첫 inference가 5~10초입니다. health check가 통과하기 전에 dummy request로 warm-up을 돌려야 사용자 첫 호출이 안 깨집니다.
- **Streaming response의 connection close 처리** 사용자가 중간에 닫으면 LLM은 계속 토큰을 생성합니다. FastAPI의 `request.is_disconnected()`를 체크해 즉시 generation을 중단하세요. GPU 시간 낭비를 30%까지 줄일 수 있습니다.
- **이미지 EXIF orientation 무시** iPhone 사진은 EXIF orientation이 자주 90도 회전입니다. PIL의 `ImageOps.exif_transpose()`를 안 쓰면 model은 옆으로 누운 이미지를 받게 되고, 정확도가 눈에 띄게 떨어집니다.
- **PII 흘림 (얼굴, 번호판, 화면 글자)** multimodal API는 사용자가 의도하지 않게 개인정보를 보냅니다. 신분증, 번호판, 의료 사진. production 도입 전 PII detection layer(예: face blur, OCR + regex masking)를 입력 단계에 두고, log 저장 시 이미지 hash만 남기세요.

## 운영 체크리스트

- [ ] API 입구와 inference worker를 분리하고 queue/backpressure 정책을 두었는가
- [ ] 업로드 이미지를 직접 payload로 오래 들고 있지 않고 object storage 기반으로 처리하는가
- [ ] 모델 warm-up과 cold start 지연을 관측하고 완화하는가
- [ ] PII·안전성·권한 검사를 추론 전후 단계에 배치했는가
- [ ] latency, cost, cache hit rate, modality별 오류율을 대시보드로 보고 있는가

## 정리

시리즈 마지막에서 가장 중요한 메시지는 단순합니다. 멀티모달 앱은 모델 집합이 아니라 서비스 파이프라인입니다. 업로드, 전처리, 추론, 캐싱, 정책, 관측성까지 모두 포함해야 비로소 production이라고 부를 수 있습니다.

앞선 9편에서 본 encoder, VLM, OCR, RAG, audio, video 개념은 여기서 하나로 합쳐집니다. 어떤 modality든 결국 API 입구와 worker, 저장소, 캐시, 모니터링 위에서 운영되기 때문입니다.

좋은 멀티모달 제품은 화려한 데모보다 boring한 운영 설계를 더 많이 담고 있습니다. 그 boring한 부분을 제대로 만들수록 모델 성능도 실제 사용자 경험으로 이어집니다.

## 처음 질문으로 돌아가기

- **production 멀티모달 앱은 어떤 end-to-end 구성 요소를 반드시 분리해서 설계해야 할까요?**
  - 본문의 기준은 Production Multimodal Application 구축를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **FastAPI 입구, inference worker, cache, object storage, observability는 어떤 순서로 연결되는 편이 안정적일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **동기 처리와 비동기 처리 경계는 어떤 기준으로 나누는 것이 현실적일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Multimodal AI 101 (1/10): Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Multimodal AI 101 (2/10): Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- [Multimodal AI 101 (3/10): Vision-Language Model 아키텍처](./03-vlm-architecture.md)
- [Multimodal AI 101 (4/10): Image Captioning과 OCR 파이프라인](./04-captioning-ocr-pipelines.md)
- [Multimodal AI 101 (5/10): Multimodal RAG: 이미지와 텍스트를 함께 검색하기](./05-multimodal-rag.md)
- [Multimodal AI 101 (6/10): 오디오 처리와 Whisper STT](./06-audio-whisper.md)
- [Multimodal AI 101 (7/10): Diffusion으로 Text-to-Image 생성](./07-text-to-image-diffusion.md)
- [Multimodal AI 101 (8/10): Multimodal Embedding과 Cross-modal 검색](./08-multimodal-embeddings.md)
- [Multimodal AI 101 (9/10): Video 이해 - Frame Sampling에서 Video-LLaVA까지](./09-video-understanding.md)
- **Production Multimodal Application 구축 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [vLLM Documentation - Multimodal Inputs](https://docs.vllm.ai/en/latest/models/vlm.html)
- [FastAPI Documentation - Streaming Responses](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [Kwon et al. - Efficient Memory Management for Large Language Model Serving with PagedAttention (vLLM)](https://arxiv.org/abs/2309.06180)
- [NVIDIA Triton Inference Server - Multimodal Model Serving](https://github.com/triton-inference-server/server)

### 관련 시리즈

- [LLM API 프로덕션 101 - 캐싱 전략](../../llm-api-production-101/ko/04-caching-strategies.md)
- [AI Agent 101 - 운영](../../ai-agent-101/ko/09-production-operations.md)
- [Harness Engineering 101 - Observability](../../harness-engineering-101/ko/09-observability.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/10-production-multimodal-app)

Tags: Production, Multimodal API, FastAPI, Inference Pipeline, Cost Optimization, Caching
