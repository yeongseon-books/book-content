---
title: Production Multimodal Application 구축
series: multimodal-ai-101
episode: 10
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Production
- Multimodal API
- FastAPI
- Inference Pipeline
- Cost Optimization
- Caching
last_reviewed: '2026-05-11'
seo_description: 지금까지 9편에 걸쳐 image encoder, VLM 아키텍처, captioning, multimodal RAG,
  audio…
---

# Production Multimodal Application 구축

> Multimodal AI 101 시리즈 (10/10)

---

지금까지 9편에 걸쳐 image encoder, VLM 아키텍처, captioning, multimodal RAG, audio, diffusion, embedding, video를 다뤘습니다. 이번 마지막 글은 그 모든 조각을 묶어 production system 하나를 만드는 이야기입니다. 핵심은 model이 아니라 system 입니다. 같은 모델이라도 어떻게 serving하고 cache 하고 cost를 통제하느냐가 사용자 경험을 결정합니다.

이 글에서는 FastAPI 기반 multimodal API 설계, inference pipeline 단계별 최적화, caching 전략, cost control, 그리고 production rollout 함정을 다룹니다.


## 1. End-to-End 시스템 전체 그림

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

## 2. FastAPI 기본 골격

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

    # 4. final VLM Q&A with streaming
    return StreamingResponse(
        stream_vlm_answer(image_bytes, question, caption, ocr_text, docs),
        media_type="text/event-stream",
    )
```

3가지 pre-extraction(caption, OCR, embedding)을 `asyncio.gather`로 병렬 실행하는 것이 latency 핵심입니다. 직렬로 돌리면 3 step latency가 합쳐지지만, 병렬이면 가장 느린 한 step만 보입니다.

## 3. Inference Worker 분리 (vLLM, Triton)

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

## 4. Caching Layer

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

## 5. Cost Optimization 체크리스트

multimodal serving cost는 GPU 시간이 90% 이상입니다. 실전 절감 포인트:

- **Batch inference**: vLLM의 continuous batching으로 처리량 5~10배
- **Quantization**: BLIP-2, LLaVA를 4-bit (bitsandbytes, AWQ)로 VRAM 절반
- **Tiered model**: 쉬운 query는 small VLM(CogVLM-7B), 어려운 query는 GPT-4V로 routing
- **Image resize 사전 처리**: 4K 이미지를 그대로 보내면 token이 4배. 1024 long edge로 resize
- **Semantic cache**: question embedding cosine > 0.95이면 cache hit으로 처리
- **Async OCR**: 사용자 응답 후 백그라운드에서 OCR 결과를 DB에 저장(다음 query에 재사용)

월 GPT-4V $5,000을 쓰던 시스템이 이 6가지를 적용하면 $1,200~$1,800 수준까지 떨어지는 게 일반적입니다.

## 6. Observability와 Feedback Loop

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

## 7. Production Rollout 시나리오

새 multimodal model을 배포할 때 권장 순서:

1. **Shadow traffic** (1주): 기존 모델과 병렬 호출, 응답은 비교만, 사용자에게는 기존 응답
2. **Canary 5%** (3일): 일부 사용자에게 신모델 노출, latency/error/hallucination metric 비교
3. **Canary 25%** (3일): 비용/품질 안정성 확인
4. **Full rollout**: 100% 전환, rollback button 준비
5. **Sunset 기존 모델** (2주 후): GPU 회수

multimodal은 single-modality보다 failure mode가 다양해서(이미지 손상, OCR 깨짐, audio sync 등) shadow 단계가 절대 필요합니다.

## 흔히 놓치는 함정 다섯 가지

### 1. Image upload를 동기로 처리

큰 파일을 sync로 읽으면 event loop가 막힙니다. `await image.read()`는 OK지만, 추가 처리(resize, hash)는 `asyncio.to_thread()`나 별도 worker process로 빼세요.

### 2. Model warm-up 미반영

GPU model은 cold start에서 첫 inference가 5~10초입니다. health check가 통과하기 전에 dummy request로 warm-up을 돌려야 사용자 첫 호출이 안 깨집니다.

### 3. Streaming response의 connection close 처리

사용자가 중간에 닫으면 LLM은 계속 토큰을 생성합니다. FastAPI의 `request.is_disconnected()`를 체크해 즉시 generation을 중단하세요. GPU 시간 낭비를 30%까지 줄일 수 있습니다.

### 4. 이미지 EXIF orientation 무시

iPhone 사진은 EXIF orientation이 자주 90도 회전입니다. PIL의 `ImageOps.exif_transpose()`를 안 쓰면 model은 옆으로 누운 이미지를 받게 되고, 정확도가 눈에 띄게 떨어집니다.

```python
from PIL import Image, ImageOps
img = ImageOps.exif_transpose(Image.open(path))
```

### 5. PII 흘림 (얼굴, 번호판, 화면 글자)

multimodal API는 사용자가 의도하지 않게 개인정보를 보냅니다. 신분증, 번호판, 의료 사진. production 도입 전 PII detection layer(예: face blur, OCR + regex masking)를 입력 단계에 두고, log 저장 시 이미지 hash만 남기세요.

## 핵심 요약

- multimodal app의 핵심은 model이 아니라 system: orchestration, caching, cost, observability
- FastAPI + asyncio.gather로 caption/OCR/embedding을 병렬화하면 latency가 가장 느린 step에 수렴
- vLLM/Triton 같은 inference worker를 분리해 model 교체와 GPU scaling을 독립적으로 운영
- 3-tier cache(exact/semantic/feature)로 hit rate 70% 이상, GPU cost 60% 절감 가능
- Shadow → canary → full rollout 단계와 PII/EXIF/streaming disconnect 같은 multimodal 특유 함정에 대비

10편에 걸쳐 multimodal AI의 모델, 데이터, 시스템을 모두 살펴봤습니다. 이제 직접 multimodal app을 한 번 만들어보고, 다음 시리즈에서 더 깊은 주제를 함께 파고듭시다.

---

<!-- toc:begin -->
## Multimodal AI 101 시리즈

- [Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- [Vision-Language Model 아키텍처](./03-vlm-architecture.md)
- [Image Captioning과 OCR 파이프라인](./04-captioning-ocr-pipelines.md)
- [Multimodal RAG: 이미지와 텍스트를 함께 검색하기](./05-multimodal-rag.md)
- [오디오 처리와 Whisper STT](./06-audio-whisper.md)
- [Diffusion으로 Text-to-Image 생성](./07-text-to-image-diffusion.md)
- [Multimodal Embedding과 Cross-modal 검색](./08-multimodal-embeddings.md)
- [Video 이해 - Frame Sampling에서 Video-LLaVA까지](./09-video-understanding.md)
- **Production Multimodal Application 구축 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [vLLM Documentation - Multimodal Inputs](https://docs.vllm.ai/en/latest/models/vlm.html)
- [FastAPI Documentation - Streaming Responses](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [Kwon et al. - Efficient Memory Management for Large Language Model Serving with PagedAttention (vLLM)](https://arxiv.org/abs/2309.06180)
- [NVIDIA Triton Inference Server - Multimodal Model Serving](https://github.com/triton-inference-server/server)

Tags: Production, Multimodal API, FastAPI, Inference Pipeline, Cost Optimization, Caching
