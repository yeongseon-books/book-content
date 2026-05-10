---
title: 'Image Encoder: CLIP과 ViT'
series: multimodal-ai-101
episode: 2
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- CLIP
- ViT
- Image Encoder
- Contrastive Learning
- OpenAI
- Vision Transformer
last_reviewed: '2026-05-03'
seo_description: multimodal 시스템의 품질은 결국 image encoder가 만들어내는 representation의 품질에서
  출발합니다.
---

# Image Encoder: CLIP과 ViT

> Multimodal AI 101 시리즈 (2/10)

---

<!-- a-grade-intro:begin -->
## 핵심 질문

CLIP과 ViT는 어떻게 이미지를 벡터로 바꾸고, 언제 어떤 인코더를 골라야 하나요?

이 글은 그 질문에 답하기 위해 이미지 인코더 선택과 임베딩 추출의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## 왜 image encoder부터 봐야 하나

multimodal 시스템의 품질은 결국 image encoder가 만들어내는 representation의 품질에서 출발합니다. CLIP과 ViT(Vision Transformer)는 현재 거의 모든 VLM의 image side에 들어가는 두 축이고, BLIP-2, LLaVA, GPT-4V도 ViT 계열을 backbone으로 씁니다. 1편에서 hybrid fusion을 다뤘다면, 이번 편은 그 입력단인 vision encoder를 직접 들여다봅니다.

## ViT: 이미지를 token sequence로 바라보기

CNN은 이미지를 작은 receptive field부터 점점 키워가며 처리합니다. ViT는 정반대로 시작합니다. 이미지를 16x16 patch로 자르고, 각 patch를 token으로 취급해 Transformer에 그대로 넣습니다.

```
[224x224 image] -> 14x14 = 196 patches -> linear projection -> 196 tokens (+ CLS)
                                                                |
                                                                v
                                          Transformer Encoder (12 layers)
                                                                |
                                                                v
                                                  CLS embedding (= image vector)
```

핵심 세 가지만 짚으면 됩니다.

1. **Patch embedding**: 16x16 patch를 flatten해 linear layer로 D 차원 token으로 바꿉니다. ViT-B/16의 D는 768입니다.
2. **Positional embedding**: NLP와 똑같이 위치 정보를 더합니다. learnable 1D positional embedding이 표준입니다.
3. **CLS token**: BERT처럼 sequence 맨 앞에 special token을 두고, 그 출력 vector를 image representation으로 씁니다.

```python
import torch
from transformers import ViTModel, ViTImageProcessor
from PIL import Image

processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
model = ViTModel.from_pretrained("google/vit-base-patch16-224")

img = Image.open("samples/cat.jpg").convert("RGB")
inputs = processor(images=img, return_tensors="pt")

with torch.no_grad():
    out = model(**inputs)

cls_vec = out.last_hidden_state[:, 0, :]  # (1, 768)
print(cls_vec.shape, cls_vec.norm().item())
```

이 vector 하나가 분류기 입력, retrieval index, multimodal model의 visual token source로 쓰입니다.

## CLIP: text와 image를 같은 공간에 정렬하기

ViT가 좋은 image vector를 만든다고 해도, 그것만으로 텍스트와 비교할 수는 없습니다. CLIP은 image encoder와 text encoder를 동시에 학습시키되, "맞는 (image, text) 쌍은 가까이, 틀린 쌍은 멀리"라는 contrastive loss로 묶었습니다.

학습 신호는 InfoNCE라는 단순한 contrastive loss입니다. batch에 N개의 (image, text) 쌍이 있다면, NxN similarity matrix를 만들고 diagonal이 정답이 되도록 cross-entropy를 양방향으로 적용합니다.

```python
import torch
import torch.nn.functional as F

def clip_loss(image_emb: torch.Tensor, text_emb: torch.Tensor,
              temperature: float = 0.07) -> torch.Tensor:
    image_emb = F.normalize(image_emb, dim=-1)
    text_emb = F.normalize(text_emb, dim=-1)
    logits = image_emb @ text_emb.T / temperature
    targets = torch.arange(len(image_emb), device=logits.device)
    loss_i = F.cross_entropy(logits, targets)
    loss_t = F.cross_entropy(logits.T, targets)
    return (loss_i + loss_t) / 2
```

이 단순한 loss를 4억 개 (image, alt-text) 쌍에 학습시킨 결과가 zero-shot ImageNet 분류 76% 정확도라는 결과입니다. label 한 번 안 보고요.

## CLIP을 그대로 쓰는 세 가지 패턴

### 패턴 1: zero-shot 분류

CLIP의 강점은 학습 없이 새 클래스를 추가할 수 있다는 점입니다. text encoder에 prompt를 넣어 class vector를 만들고, image vector와 cosine similarity를 계산합니다.

```python
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

labels = ["cat", "dog", "car", "airplane"]
prompts = [f"a photo of a {l}" for l in labels]
img = Image.open("samples/test.jpg").convert("RGB")

inputs = proc(text=prompts, images=img, return_tensors="pt", padding=True)
with torch.no_grad():
    out = model(**inputs)

probs = out.logits_per_image.softmax(dim=-1)[0]
for label, p in zip(labels, probs):
    print(f"{label:>10}: {p:.3f}")
```

### 패턴 2: image embedding을 vector DB에 저장

retrieval-like 검색에 가장 자주 쓰는 패턴입니다. 사전에 모든 이미지의 embedding을 뽑아 FAISS에 넣고, query는 image든 text든 같은 공간에서 nearest를 찾습니다.

```python
import faiss
import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").eval()
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def embed_images(paths: list[str]) -> np.ndarray:
    imgs = [Image.open(p).convert("RGB") for p in paths]
    inputs = proc(images=imgs, return_tensors="pt")
    with torch.no_grad():
        feats = model.get_image_features(**inputs)
    feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats.cpu().numpy().astype("float32")

paths = ["a.jpg", "b.jpg", "c.jpg", "d.jpg"]
vecs = embed_images(paths)

index = faiss.IndexFlatIP(vecs.shape[1])  # cosine = inner product on normalized
index.add(vecs)

# query by text
query = proc(text=["a red sports car"], return_tensors="pt", padding=True)
with torch.no_grad():
    qv = model.get_text_features(**query)
qv = (qv / qv.norm(dim=-1, keepdim=True)).cpu().numpy().astype("float32")

D, I = index.search(qv, k=3)
print("top-3:", [paths[i] for i in I[0]])
```

### 패턴 3: VLM의 image tower

LLaVA, BLIP-2, MiniGPT-4 모두 CLIP image encoder의 마지막 layer 출력을 visual token으로 쓰고, projection layer 하나만 학습해 LLM에 연결합니다. encoder를 frozen으로 두면 학습 비용이 극적으로 떨어집니다.

## ViT 모델 선택 가이드

production에 쓸 image encoder를 고를 때 자주 등장하는 선택지를 비교합니다.

| 모델 | 파라미터 | 입력 해상도 | 권장 용도 |
| --- | --- | --- | --- |
| ViT-B/16 | 86M | 224x224 | 일반 분류, prototyping |
| ViT-L/14 | 304M | 224x224 | 고품질 embedding |
| CLIP ViT-B/32 | 87M | 224x224 | 검색, zero-shot 분류 |
| CLIP ViT-L/14-336 | 304M | 336x336 | LLaVA backbone, 고해상도 |
| EVA-CLIP-G/14 | 1B+ | 224~336 | SOTA embedding 필요 시 |
| SigLIP-Base | 200M | 224 | CLIP 대체, 학습 안정성 우수 |

실무에서 CLIP ViT-L/14-336은 LLaVA-1.5 기본값이고, SigLIP은 Google PaliGemma 등 최신 VLM이 채택합니다. zero-shot 분류 단독 작업이라면 ViT-B/32부터 시작하면 충분합니다.

## 흔히 놓치는 함정 다섯 가지

### 1. preprocessing을 처리기 기본값과 다르게 적용

ViT는 ImageNet mean/std로 normalize하고, CLIP은 OpenAI의 별도 mean/std를 씁니다. 직접 PIL/torchvision으로 전처리하면 값이 달라져 정확도가 무너집니다. `transformers`의 `*ImageProcessor`를 그대로 쓰는 게 가장 안전합니다.

### 2. CLIP embedding을 normalize 안 하고 cosine 비교

CLIP feature는 normalize 후에 cosine similarity가 됩니다. raw vector로 dot product하면 length-bias가 들어가 검색 품질이 크게 떨어집니다.

### 3. zero-shot prompt를 한 줄만 써본다

CLIP zero-shot 정확도는 prompt 다양화로 +3~5% 더 올릴 수 있습니다. OpenAI 원 논문이 제안한 80개 prompt template (`a photo of a {}`, `a blurry photo of a {}` 등)을 평균내면 안정적입니다.

### 4. image encoder를 fine-tuning하려고 dataset만 늘림

CLIP backbone fine-tuning은 정교한 LR scheduling과 layer-wise learning rate decay가 필요합니다. 무작정 lr=1e-3로 풀어버리면 representation이 망가집니다. 처음에는 head만 학습하거나 LoRA를 권합니다.

### 5. 입력 해상도를 무시한 cropping

CLIP-336 모델에 224 입력을 주거나 반대로 주면 positional embedding이 안 맞아 성능이 급락합니다. processor가 자동으로 resize하지만, custom dataloader를 쓰면 수동 확인이 필요합니다.

## 핵심 요약

- ViT는 이미지를 16x16 patch로 잘라 Transformer에 넣고, CLS token 출력을 image vector로 씁니다.
- CLIP은 InfoNCE contrastive loss로 image encoder와 text encoder를 같은 공간에 정렬합니다. 4억 쌍 학습으로 zero-shot 분류 76% 정확도를 달성했습니다.
- 활용 패턴은 zero-shot 분류, vector DB embedding, VLM의 image tower 셋입니다.
- 모델 선택은 ViT-B/32 (prototyping) -> CLIP ViT-L/14-336 (LLaVA급) -> SigLIP (안정적인 최신 대안) 순으로 검토합니다.
- preprocessing 기본값, normalize 누락, prompt 다양화, fine-tuning 정책, 해상도 일치는 production 도입 전에 반드시 점검합니다.

---

<!-- toc:begin -->
## 시니어 엔지니어는 이렇게 생각합니다

- **ViT 패치 이해** — 이미지를 패치 토큰 시퀀스로 보는 관점이 모든 VLM의 출발점입니다.
- **CLIP은 contrastive** — 이미지-텍스트 정렬 학습 결과라 zero-shot 분류·검색에 강합니다.
- **해상도 민감도** — OCR/세부 인식이 필요한 도메인은 224 대신 336/448 모델을 우선합니다.
- **임베딩 차원과 비용** — DB 비용·검색 latency를 좌우하므로 차원을 무작정 키우지 않습니다.
- **정규화 일관성** — 검색 시 인덱싱 시점과 동일한 normalize/preprocess 파이프라인을 강제합니다.

## Multimodal AI 101 시리즈

- [Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- **Image Encoder: CLIP과 ViT (현재 글)**
- Vision-Language Model 아키텍처 (예정)
- Image Captioning과 OCR 파이프라인 (예정)
- Multimodal RAG: 이미지와 텍스트를 함께 검색하기 (예정)
- 오디오 처리와 Whisper STT (예정)
- Diffusion으로 텍스트에서 이미지 생성 (예정)
- Multimodal Embedding과 cross-modal 검색 (예정)
- Video 이해 (Frame Sampling에서 Video-LLaVA까지) (예정)
- Production Multimodal Application 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Dosovitskiy et al. - An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale (ViT)](https://arxiv.org/abs/2010.11929)
- [Radford et al. - Learning Transferable Visual Models From Natural Language Supervision (CLIP)](https://arxiv.org/abs/2103.00020)
- [HuggingFace - CLIP Documentation](https://huggingface.co/docs/transformers/model_doc/clip)
- [Zhai et al. - Sigmoid Loss for Language Image Pre-Training (SigLIP)](https://arxiv.org/abs/2303.15343)

Tags: CLIP, ViT, Image Encoder, Contrastive Learning, OpenAI, Vision Transformer
