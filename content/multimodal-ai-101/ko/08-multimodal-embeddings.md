---
title: Multimodal Embedding과 Cross-modal 검색
series: multimodal-ai-101
episode: 8
language: ko
status: publish-ready
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
last_reviewed: '2026-05-12'
seo_description: 5편에서 multimodal RAG의 큰 그림을 살펴봤다면, 이번 글에서는 그 심장에 해당하는 multimodal embedding을
  더…
---

# Multimodal Embedding과 Cross-modal 검색

멀티모달 시스템이 실제로 검색과 추천까지 연결되기 시작하면 결국 다시 임베딩 이야기로 돌아옵니다. 이미지를 이해하는 모델이 아무리 좋아도, 대량의 자산을 빠르게 찾고 비교하고 재사용하려면 검색 가능한 벡터 표현이 필요하기 때문입니다. 특히 텍스트로 이미지를 찾고, 이미지로 오디오나 비디오를 찾는 문제는 공통 공간이 없으면 성립하기 어렵습니다.

이 글에서 다루는 multimodal embedding은 바로 그 공통 공간의 문제입니다. CLIP, SigLIP, ImageBind는 서로 다른 방식으로 modality 사이의 거리를 정렬합니다. 겉보기에 비슷한 벡터화 작업이지만, 어떤 modality를 얼마나 강하게 묶는지에 따라 검색과 추천 품질이 크게 달라집니다.

실무에서는 모델보다 더 자주 틀리는 곳이 따로 있습니다. normalization 누락, score calibration 미비, preprocessing 불일치, 다국어 처리 부재가 대표적입니다. 그래서 임베딩 시스템은 모델 선택보다 계약 관리가 더 중요하다고 느껴질 때가 많습니다.

이 글에서는 multimodal embedding을 “모든 것을 벡터로 만드는 기술”이 아니라, 서로 다른 입력을 하나의 검색 인터페이스 아래로 수렴시키는 설계 층으로 정리합니다.

이 글은 Multimodal AI 101 시리즈의 8번째 글입니다.

임베딩 공간을 잘 설계한 팀은 거대한 모델보다 먼저 검색 경험을 안정적으로 개선합니다.

## 이 글에서 다룰 문제

- Multimodal embedding은 텍스트 임베딩과 무엇이 다르고, 왜 cross-modal search의 핵심일까요?
- CLIP, SigLIP, ImageBind는 어떤 공통점과 차이를 가지며 무엇을 기준으로 선택해야 할까요?
- OpenCLIP으로 벡터를 추출할 때 preprocessing과 normalization은 왜 계약 수준으로 중요할까요?
- FAISS 인덱스 위에서 이미지와 텍스트를 함께 검색하려면 어떤 구조가 가장 실용적일까요?
- modality별 score 분포, 다국어 처리, preprocessing 불일치 문제는 어떻게 다뤄야 할까요?

## 왜 이 글이 중요한가

멀티모달 embedding은 retrieval 품질을 확장하는 가장 현실적인 방법 중 하나입니다. 거대한 생성 모델을 매번 호출하지 않아도, 검색과 추천의 초기 후보군을 훨씬 정확하게 만들 수 있기 때문입니다.

또한 임베딩 기반 구조는 대규모 자산 관리에 적합합니다. 수십만 장의 이미지, 수천 개의 오디오 클립, 제품 카탈로그를 벡터 인덱스로 유지하면 생성 단계의 부담을 크게 줄일 수 있습니다.

반대로 이 단계를 대충 넘기면 retrieval 결과가 불안정해지고, 그 뒤의 RAG나 ranking 단계가 계속 보정 비용을 떠안게 됩니다. 멀티모달 시스템은 생각보다 임베딩 품질에 강하게 의존합니다.

## Multimodal Embedding을 이해하는 가장 좋은 방법: 각 modality를 압축하는 기술이 아니라 공통 검색 좌표계를 만드는 기술로 보는 것입니다

이미지, 텍스트, 오디오를 각각 좋은 벡터로 만드는 것만으로는 충분하지 않습니다. 중요한 것은 그 벡터들이 같은 좌표계 안에서 비교 가능한가입니다. multimodal embedding 모델의 가치는 바로 이 비교 가능성을 만들어 준다는 데 있습니다.

이 좌표계가 있으면 검색 인터페이스가 단순해집니다. 사용자는 텍스트로 이미지를 찾고, 이미지로 관련 설명을 찾고, 때로는 오디오까지 같은 흐름에서 탐색할 수 있습니다. 시스템 입장에서는 서로 다른 modality가 하나의 retrieval API 아래로 들어옵니다.

그래서 실무 체크리스트도 좌표계 유지에 초점이 맞춰집니다. normalization, score calibration, preprocessing consistency는 모두 같은 공간에서 의미 있는 거리를 유지하기 위한 기본 계약입니다.

> 멀티모달 임베딩의 진짜 가치는 벡터를 만드는 데 있지 않습니다. 서로 다른 입력이 같은 거리 개념을 공유하게 만드는 데 있습니다.

## 핵심 개념

### 1. Multimodal Embedding이란

Single-modal embedding은 동일한 modality 안에서 의미를 압축합니다. text encoder는 문장을 벡터로 만들고, image encoder는 이미지를 벡터로 만듭니다. 두 벡터는 차원이 같아도 공간이 달라서 서로 비교하면 무의미합니다.

Multimodal embedding은 contrastive learning으로 두 modality를 같은 공간으로 정렬합니다. 학습 시 (image, caption) 쌍을 가져와 같은 쌍은 가깝게, 다른 쌍은 멀게 학습시키면, 결과적으로 "강아지 사진"과 "a photo of a dog" 문장이 비슷한 벡터로 떨어집니다.

```text
text "a sleeping cat"          ──┐
                                 ├──► shared space (e.g. 768-dim)
image (sleeping cat photo)      ──┘
        cosine similarity ≈ 0.31
```

이 구조 덕분에 한 번 index를 만들어두면 query 쪽이 어떤 modality든 검색이 가능합니다.

### 2. CLIP, SigLIP, ImageBind 비교

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

### 3. OpenCLIP으로 embedding 추출하기

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

### 4. FAISS로 cross-modal index 구축

```python
import faiss
import numpy as np

DIM = 512  # ViT-B/32

# 1. Image corpus -> embeddings -> index
image_paths = ["img_001.jpg", "img_002.jpg", "img_003.jpg"]
image_embeds = embed_image(image_paths).cpu().numpy().astype("float32")

index = faiss.IndexFlatIP(DIM)  # inner product == cosine for normalized vectors
index.add(image_embeds)

# 2. Text query -> embedding -> search
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
index.nprobe = 8  # number of clusters explored per query
```

`nprobe`는 recall과 latency의 trade-off knob입니다. 1M vector 기준 nprobe=8이면 recall 약 0.95, 1ms latency.

### 5. ImageBind로 audio까지 한 공간에

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

for k, v in embeds.items():
    embeds[k] = v / v.norm(dim=-1, keepdim=True)

text_audio = (embeds[ModalityType.TEXT] @ embeds[ModalityType.AUDIO].T).item()
text_image = (embeds[ModalityType.TEXT] @ embeds[ModalityType.VISION].T).item()
print(f"text<->audio: {text_audio:.3f}, text<->image: {text_image:.3f}")
```

같은 1024 차원에 정렬되어 있어서 "dog barking 소리"를 query로 넣고 "강아지 사진"을 찾는 것이 자연스럽게 동작합니다. 단, audio 품질은 video clip 기반이라 일반 환경 sound에는 강한 반면 음악·발화에는 약합니다.

### 6. Hybrid retrieval 패턴

실전에서 cross-modal embedding 단독으로는 정밀도가 부족할 때가 많습니다. 두 가지 hybrid가 자주 쓰입니다.

### 6.1 Embedding + BM25 ensemble

```python
def hybrid_score(query: str, doc, alpha: float = 0.6) -> float:
    sem = semantic_score(query, doc)   # CLIP / embedding based
    lex = bm25_score(query, doc)       # lexical match
    return alpha * sem + (1 - alpha) * lex
```

이미지 메타데이터(파일명, EXIF, caption)에 BM25를 걸고, 시각 유사도와 가중합하면 검색 품질이 눈에 띄게 올라갑니다.

### 6.2 Two-stage: candidate → rerank

1단계는 빠른 ANN(IVF/HNSW)으로 top-100을 뽑고, 2단계는 더 큰 model(예: BLIP-2, LLaVA, ColBERT)로 rerank합니다. user-facing latency는 1단계에서 결정되고, 정확도는 2단계가 결정합니다.

### 임베딩 공간을 운영할 때의 점수 해석

멀티모달 검색에서 자주 생기는 오해는 score를 절대값처럼 읽는 것입니다. 하지만 이미지-텍스트, 텍스트-텍스트, 이미지-오디오 비교는 score 분포 자체가 다를 수 있습니다. 같은 0.32라는 값이 어떤 modality 조합에서는 충분히 강한 신호지만, 다른 조합에서는 거의 의미가 없을 수 있습니다.

그래서 운영에서는 threshold를 하나만 두기보다 modality별 calibration을 별도로 두는 편이 낫습니다. 필요하면 1차 retrieval 뒤에 reranker를 두어 score 해석을 한 번 더 안정화할 수도 있습니다. 이 과정이 없으면 검색 품질이 들쭉날쭉해 보이는데 원인을 설명하기 어려워집니다.

좋은 임베딩 시스템은 벡터를 만드는 단계에서 끝나지 않습니다. 만들어진 거리를 어떤 기준으로 해석하고, 어떤 경우에 사람 검수나 후속 모델로 넘길지를 함께 설계해야 비로소 서비스 품질이 안정됩니다.

## 흔히 헷갈리는 지점

- **Normalization 빠뜨리기** cosine similarity로 비교한다고 가정하고 코드를 짰는데, 정작 vector normalize를 안 하면 magnitude 큰 vector가 항상 이깁니다. embedding을 저장하기 전에 한 번 `v / v.norm()`을 거치는 습관이 안전합니다.
- **Modality 간 score 분포가 다름** text<->text similarity와 text<->image similarity는 같은 모델이라도 분포가 다릅니다. CLIP에서 text<->image cosine은 평균 0.2~0.35 범위에 몰립니다. "0.5 이상이면 매칭"같은 절대 threshold는 위험하고, query 별 percentile이나 top-k cutoff를 써야 합니다.
- **모델별로 차원·정규화 방식이 다름** OpenAI CLIP ViT-L/14는 768, OpenCLIP ViT-H/14는 1024, SigLIP은 logit scale이 다릅니다. 한 corpus 안에 여러 모델 embedding을 섞으면 안 되고, 모델 교체 시 index를 통째로 재구축해야 합니다.
- **다국어를 영어 모델로 처리** OpenAI CLIP은 학습 데이터의 95%가 영어입니다. 한국어 query를 그대로 던지면 recall이 절반 이하로 떨어집니다. multilingual-CLIP, Jina CLIP v2, KoCLIP 같은 다국어 모델로 가거나, query를 LLM으로 영어 번역 후 검색하는 우회가 필요합니다.
- **Image preprocessing 불일치** 학습된 모델은 특정 resize/crop/normalization을 가정합니다. ViT-B/32는 224x224 center crop이 기본이고, SigLIP은 384x384를 씁니다. 직접 PIL로 잘못 resize하면 score가 0.05~0.10씩 깎입니다. 항상 `model_and_transforms`로 함께 받은 `preprocess`를 사용하세요.

## 운영 체크리스트

- [ ] 모든 embedding 출력에 대해 정규화 여부를 일관되게 적용하는가
- [ ] 모델별 차원 수와 score 분포 차이를 인덱스 설계에 반영했는가
- [ ] 다국어 질의를 처리할 경우 영어 중심 모델의 한계를 별도로 평가했는가
- [ ] 이미지 전처리 파이프라인을 학습 시 규약과 동일하게 유지하는가
- [ ] retrieval score를 modality별로 보정하거나 reranking 계층을 두었는가

## 정리

Multimodal embedding은 서로 다른 입력을 하나의 검색 공간 안에 넣는 기술입니다. 이 공통 공간이 있어야 cross-modal search와 추천, 후보군 생성이 자연스럽게 작동합니다.

CLIP, SigLIP, ImageBind는 비슷해 보여도 지원 modality와 학습 목표가 다르기 때문에 선택 기준도 달라집니다. 원하는 검색 경험에 맞춰 좌표계를 고르는 것이 중요합니다.

실무에서는 normalization과 preprocessing consistency가 생각보다 더 중요합니다. 벡터 검색은 모델보다 계약이 먼저 무너지기 쉬운 영역이기 때문입니다.

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
- [Video 이해 - Frame Sampling에서 Video-LLaVA까지](./09-video-understanding.md)
- [Production Multimodal Application 구축](./10-production-multimodal-app.md)
<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Radford et al. - Learning Transferable Visual Models From Natural Language Supervision (CLIP)](https://arxiv.org/abs/2103.00020)
- [Zhai et al. - Sigmoid Loss for Language Image Pre-Training (SigLIP)](https://arxiv.org/abs/2303.15343)
- [Girdhar et al. - ImageBind: One Embedding Space To Bind Them All](https://arxiv.org/abs/2305.05665)
- [FAISS Documentation - Index Types and Trade-offs](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)

### 관련 시리즈

- [Vector Search 101 - 임베딩이란 무엇인가](../../vector-search-101/ko/01-what-is-embedding.md)
- [Vector Search 101 - FAISS 입문](../../vector-search-101/ko/04-faiss-fundamentals.md)
- [RAG 평가와 벤치마크 101 - 임베딩 모델 비교](../../rag-benchmark-101/ko/03-embedding-comparison.md)

Tags: Embeddings, Cross-modal Search, CLIP, ImageBind, FAISS, Multimodal Index
