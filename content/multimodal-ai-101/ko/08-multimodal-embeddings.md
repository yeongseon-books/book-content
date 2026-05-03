---
title: Multimodal Embedding과 Cross-modal 검색
series: multimodal-ai-101
episode: 8
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Embeddings
- Cross-modal Search
- CLIP
- ImageBind
- FAISS
- Multimodal Index
last_reviewed: '2026-05-03'
---

# Multimodal Embedding과 Cross-modal 검색

> Multimodal AI 101 시리즈 (8/10)

---

5편에서 multimodal RAG의 큰 그림을 살펴봤다면, 이번 글에서는 그 심장에 해당하는 multimodal embedding을 더 깊게 들어갑니다. text, image, audio를 동일한 벡터 공간으로 끌어내려야 "이미지로 텍스트 검색", "텍스트로 오디오 검색" 같은 cross-modal query가 성립합니다.

이 글에서는 multimodal embedding이 만들어지는 원리, OpenCLIP/SigLIP/ImageBind/Jina CLIP 같은 주요 모델 비교, FAISS index를 활용한 cross-modal search 구현, 그리고 production에서 자주 부딪히는 함정 다섯 가지를 다룹니다.

## 1. Multimodal Embedding이란

Single-modal embedding은 동일한 modality 안에서 의미를 압축합니다. text encoder는 문장을 벡터로 만들고, image encoder는 이미지를 벡터로 만듭니다. 두 벡터는 차원이 같아도 공간이 달라서 서로 비교하면 무의미합니다.

Multimodal embedding은 contrastive learning으로 두 modality를 같은 공간으로 정렬합니다. 학습 시 (image, caption) 쌍을 가져와 같은 쌍은 가깝게, 다른 쌍은 멀게 학습시키면, 결과적으로 "강아지 사진"과 "a photo of a dog" 문장이 비슷한 벡터로 떨어집니다.

```
text "고양이가 잠자고 있다"  ──┐
                              ├──► shared space (예: 768-dim)
image (잠자는 고양이 사진)     ──┘
        cosine similarity ≈ 0.31
```

이 구조 덕분에 한 번 index를 만들어두면 query 쪽이 어떤 modality든 검색이 가능합니다.

## 2. CLIP, SigLIP, ImageBind 비교

대표 모델 네 개를 정리합니다.

| 모델 | 모달리티 | 차원 | 학습 데이터 | 특징 |
| --- | --- | --- | --- | --- |
| OpenAI CLIP ViT-L/14 | text + image | 768 | 400M web pairs | 사실상의 baseline |
| OpenCLIP ViT-H/14 | text + image | 1024 | LAION-2B | 오픈 가중치, 다국어 변형 다수 |
| Google SigLIP | text + image | 768 | WebLI 4B | softmax 대신 sigmoid loss, batch 작아도 안정 |
| Meta ImageBind | text + image + audio + depth + thermal + IMU | 1024 | 다중 데이터셋 | 6개 modality를 같은 공간으로 |
| Jina CLIP v2 | text + image | 1024 | 다국어 web | 한국어 포함 89개 언어 |

선택 기준은 단순합니다.

- 영어 위주, 가벼운 baseline: OpenAI CLIP ViT-B/32
- 오픈 라이선스에서 최대 품질: OpenCLIP ViT-H/14 또는 SigLIP
- 한국어/다국어 지원: Jina CLIP v2 또는 multilingual-CLIP
- audio까지 한 공간으로 묶고 싶다: ImageBind

## 3. OpenCLIP으로 embedding 추출하기

```python
import open_clip
import torch
from PIL import Image

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32", pretrained="laion2b_s34b_b79k"
)
tokenizer = open_clip.get_tokenizer("ViT-B-32")
model.eval()

def embed_text(texts: list[str]) -> torch.Tensor:
    tokens = tokenizer(texts)
    with torch.no_grad():
        feats = model.encode_text(tokens)
    return feats / feats.norm(dim=-1, keepdim=True)

def embed_image(paths: list[str]) -> torch.Tensor:
    imgs = torch.stack([preprocess(Image.open(p).convert("RGB")) for p in paths])
    with torch.no_grad():
        feats = model.encode_image(imgs)
    return feats / feats.norm(dim=-1, keepdim=True)

text_vec = embed_text(["a photo of a cat sleeping on a sofa"])
img_vec = embed_image(["sample.jpg"])
similarity = (text_vec @ img_vec.T).item()
print(f"cosine similarity: {similarity:.3f}")
```

핵심은 마지막의 L2 normalization입니다. cosine similarity로 비교하려면 unit vector여야 하고, FAISS의 inner product index도 normalized vector를 가정합니다.

## 4. FAISS로 cross-modal index 구축

```python
import faiss
import numpy as np

DIM = 512  # ViT-B/32 기준

# 1. image corpus → embedding → index
image_paths = ["img_001.jpg", "img_002.jpg", "img_003.jpg"]
image_embeds = embed_image(image_paths).cpu().numpy().astype("float32")

index = faiss.IndexFlatIP(DIM)  # inner product = cosine (이미 normalized)
index.add(image_embeds)

# 2. text query → embedding → search
query = embed_text(["a sunset over the ocean"]).cpu().numpy().astype("float32")
scores, ids = index.search(query, k=3)
for rank, (i, s) in enumerate(zip(ids[0], scores[0]), 1):
    print(f"{rank}. {image_paths[i]} (score={s:.3f})")
```

이게 cross-modal search의 minimal example입니다. text를 넣었지만 image space에서 ranking이 나옵니다. 반대로 image를 query로 넣으면 caption이 매칭되는, "이미지로 비슷한 문서 찾기" 도 동일 코드로 가능합니다.

대규모에서는 `IndexFlatIP` 대신 `IndexIVFFlat`이나 `IndexHNSW`를 씁니다.

```python
quantizer = faiss.IndexFlatIP(DIM)
index = faiss.IndexIVFFlat(quantizer, DIM, nlist=100, metric=faiss.METRIC_INNER_PRODUCT)
index.train(image_embeds)
index.add(image_embeds)
index.nprobe = 8  # search 시 탐색할 cluster 수
```

`nprobe`는 recall과 latency의 trade-off knob입니다. 1M vector 기준 nprobe=8이면 recall 약 0.95, 1ms latency.

## 5. ImageBind로 audio까지 한 공간에

ImageBind는 6개 modality를 같은 공간으로 정렬합니다.

```python
from imagebind.models import imagebind_model
from imagebind.models.imagebind_model import ModalityType
from imagebind import data
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model = imagebind_model.imagebind_huge(pretrained=True).eval().to(device)

inputs = {
    ModalityType.TEXT: data.load_and_transform_text(["a dog barking"], device),
    ModalityType.AUDIO: data.load_and_transform_audio_data(["bark.wav"], device),
    ModalityType.VISION: data.load_and_transform_vision_data(["dog.jpg"], device),
}
with torch.no_grad():
    embeds = model(inputs)

# normalize then cosine
for k, v in embeds.items():
    embeds[k] = v / v.norm(dim=-1, keepdim=True)

text_audio = (embeds[ModalityType.TEXT] @ embeds[ModalityType.AUDIO].T).item()
text_image = (embeds[ModalityType.TEXT] @ embeds[ModalityType.VISION].T).item()
print(f"text<->audio: {text_audio:.3f}, text<->image: {text_image:.3f}")
```

같은 1024 차원에 정렬되어 있어서 "dog barking 소리"를 query로 넣고 "강아지 사진"을 찾는 것이 자연스럽게 동작합니다. 단, audio 품질은 video clip 기반이라 일반 환경 sound에는 강한 반면 음악·발화에는 약합니다.

## 6. Hybrid retrieval 패턴

실전에서 cross-modal embedding 단독으로는 정밀도가 부족할 때가 많습니다. 두 가지 hybrid가 자주 쓰입니다.

### 6.1 Embedding + BM25 ensemble

```python
def hybrid_score(query: str, doc, alpha: float = 0.6) -> float:
    sem = semantic_score(query, doc)   # CLIP/embedding 기반
    lex = bm25_score(query, doc)       # 단어 매칭
    return alpha * sem + (1 - alpha) * lex
```

이미지 메타데이터(파일명, EXIF, caption)에 BM25를 걸고, 시각 유사도와 가중합하면 검색 품질이 눈에 띄게 올라갑니다.

### 6.2 Two-stage: candidate → rerank

1단계는 빠른 ANN(IVF/HNSW)으로 top-100을 뽑고, 2단계는 더 큰 model(예: BLIP-2, LLaVA, ColBERT)로 rerank합니다. user-facing latency는 1단계에서 결정되고, 정확도는 2단계가 결정합니다.

## 흔히 놓치는 함정 다섯 가지

### 1. Normalization 빠뜨리기

cosine similarity로 비교한다고 가정하고 코드를 짰는데, 정작 vector normalize를 안 하면 magnitude 큰 vector가 항상 이깁니다. embedding을 저장하기 전에 한 번 `v / v.norm()`을 거치는 습관이 안전합니다.

### 2. Modality 간 score 분포가 다름

text<->text similarity와 text<->image similarity는 같은 모델이라도 분포가 다릅니다. CLIP에서 text<->image cosine은 평균 0.2~0.35 범위에 몰립니다. "0.5 이상이면 매칭"같은 절대 threshold는 위험하고, query 별 percentile이나 top-k cutoff를 써야 합니다.

### 3. 모델별로 차원·정규화 방식이 다름

OpenAI CLIP ViT-L/14는 768, OpenCLIP ViT-H/14는 1024, SigLIP은 logit scale이 다릅니다. 한 corpus 안에 여러 모델 embedding을 섞으면 안 되고, 모델 교체 시 index를 통째로 재구축해야 합니다.

### 4. 다국어를 영어 모델로 처리

OpenAI CLIP은 학습 데이터의 95%가 영어입니다. 한국어 query를 그대로 던지면 recall이 절반 이하로 떨어집니다. multilingual-CLIP, Jina CLIP v2, KoCLIP 같은 다국어 모델로 가거나, query를 LLM으로 영어 번역 후 검색하는 우회가 필요합니다.

### 5. Image preprocessing 불일치

학습된 모델은 특정 resize/crop/normalization을 가정합니다. ViT-B/32는 224x224 center crop이 기본이고, SigLIP은 384x384를 씁니다. 직접 PIL로 잘못 resize하면 score가 0.05~0.10씩 깎입니다. 항상 `model_and_transforms`로 함께 받은 `preprocess`를 사용하세요.

## 핵심 요약

- Multimodal embedding은 contrastive learning으로 text/image/audio를 같은 벡터 공간에 정렬한 결과물입니다.
- OpenCLIP은 오픈 baseline, SigLIP은 안정성, ImageBind는 6 modality, Jina CLIP v2는 다국어가 강점입니다.
- FAISS `IndexFlatIP`로 시작해 corpus가 커지면 `IndexIVFFlat`이나 `IndexHNSW`로 옮깁니다.
- Hybrid retrieval(BM25 ensemble, two-stage rerank)이 single-vector search 한계를 보완합니다.
- normalization, score 분포, 모델별 차원, 다국어, preprocessing은 production 도입 전 체크 필수입니다.

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
- **Multimodal Embedding과 Cross-modal 검색 (현재 글)**
- Video 이해 (Frame Sampling에서 Video-LLaVA까지) (예정)
- Production Multimodal Application 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Radford et al. - Learning Transferable Visual Models From Natural Language Supervision (CLIP)](https://arxiv.org/abs/2103.00020)
- [Zhai et al. - Sigmoid Loss for Language Image Pre-Training (SigLIP)](https://arxiv.org/abs/2303.15343)
- [Girdhar et al. - ImageBind: One Embedding Space To Bind Them All](https://arxiv.org/abs/2305.05665)
- [FAISS Documentation - Index Types and Trade-offs](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)

Tags: Embeddings, Cross-modal Search, CLIP, ImageBind, FAISS, Multimodal Index
