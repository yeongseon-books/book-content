---
title: 'Image Encoder: CLIP과 ViT'
series: multimodal-ai-101
episode: 2
language: ko
status: publish-ready
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
last_reviewed: '2026-05-12'
seo_description: multimodal 시스템의 품질은 결국 image encoder가 만들어내는 representation의 품질에서
  출발합니다.
---

# Image Encoder: CLIP과 ViT

멀티모달 시스템을 이해할 때 많은 팀이 곧바로 GPT-4o나 LLaVA 같은 상위 모델부터 봅니다. 물론 최종 사용자 가치는 그 레이어에서 보입니다. 하지만 운영과 품질의 대부분은 그보다 아래, 즉 이미지를 어떤 벡터로 바꾸는지에서 결정됩니다. image encoder를 이해하지 못하면 retrieval도, zero-shot classification도, VLM adapter 설계도 전부 흐릿해집니다.

특히 CLIP과 ViT는 지금 멀티모달 생태계의 기본 어휘에 가깝습니다. ViT는 이미지를 patch token의 시퀀스로 바꿔 트랜스포머가 다루게 만들었고, CLIP은 텍스트와 이미지를 같은 공간에 놓는 대중적인 출발점을 제공했습니다. 이 두 축이 있어야 “왜 이미지 검색이 되지?”, “왜 텍스트 질의로 이미지를 찾지?” 같은 질문에 기술적으로 답할 수 있습니다.

실무에서는 encoder가 곧 계약입니다. 전처리 규칙, 해상도, 정규화, 임베딩 차원, cosine similarity 여부 같은 기본값이 모두 여기서 정해집니다. 같은 CLIP이라고 해도 preprocessing이 어긋나면 검색 품질이 급격히 흔들리고, normalize를 빼먹으면 점수 해석 자체가 무너집니다.

이 글에서는 image encoder를 “모델 내부 세부 구현”이 아니라, 멀티모달 검색과 분류 성능을 좌우하는 가장 현실적인 기반층으로 정리합니다.

이 글은 Multimodal AI 101 시리즈의 2번째 글입니다.

나중에 더 큰 VLM을 붙이더라도, 먼저 encoder 계층의 규약을 이해한 팀이 결국 더 안정적으로 확장합니다.

## 이 글에서 다룰 문제

- 왜 멀티모달 입문에서 image encoder부터 이해하는 편이 전체 구조를 가장 빠르게 잡게 해 줄까요?
- ViT는 이미지를 어떤 방식으로 token sequence로 바꾸고, CNN과 무엇이 다를까요?
- CLIP은 어떻게 텍스트와 이미지를 같은 embedding space에 맞추고 zero-shot을 가능하게 할까요?
- 학습된 CLIP encoder를 그대로 써도 실무에서 어떤 검색·분류 패턴을 만들 수 있을까요?
- 전처리, 정규화, prompt template, 해상도 선택에서 자주 무너지는 지점은 어디일까요?

## 왜 이 글이 중요한가

이미지 encoder를 이해하면 멀티모달 시스템의 절반이 정리됩니다. 이미지가 어떤 형태의 벡터가 되는지 알아야 그 벡터를 검색에 쓸지, 분류에 쓸지, VLM adapter의 입력으로 넣을지 설계할 수 있기 때문입니다.

또한 encoder는 비용 대비 효과가 좋은 학습 지점입니다. 거대한 VLM을 처음부터 fine-tuning하지 않아도, CLIP 같은 사전학습 encoder만으로 충분히 쓸 만한 retrieval과 zero-shot 분류 파이프라인을 만들 수 있습니다. 작은 팀일수록 이 우회로가 실용적입니다.

반대로 encoder 레이어를 대충 넘기면 이후의 문제를 전부 모델 탓으로 돌리게 됩니다. 실제로는 잘못된 crop, 잘못된 prompt, normalize 누락 같은 기본 실수가 더 흔한 원인입니다.

## Image Encoder를 이해하는 가장 좋은 방법: 이미지를 곧바로 정답으로 바꾸는 모델이 아니라 검색 가능한 표현으로 바꾸는 층으로 보는 것입니다

ViT와 CLIP을 볼 때 가장 먼저 가져가야 할 관점은 “이미지를 읽는다”가 아닙니다. 더 정확한 표현은 이미지를 토큰 또는 임베딩으로 재표현한다는 것입니다. 이 재표현 덕분에 트랜스포머는 이미지를 텍스트와 비슷한 계산 틀 안에서 다룰 수 있습니다.

CLIP이 강력한 이유도 분류기 헤드 때문이 아니라 공통 공간 때문입니다. 이미지와 텍스트를 같은 벡터 공간에 놓아 두면, 검색·유사도 비교·zero-shot 분류가 모두 하나의 연산 형태로 정리됩니다. 그래서 많은 멀티모달 시스템이 첫 번째 구성요소로 CLIP 류 encoder를 채택합니다.

이 관점은 실무 체크리스트도 분명하게 만듭니다. 전처리 일치, embedding normalization, prompt template, 해상도 정책은 사소한 옵션이 아니라 같은 표현 공간을 유지하기 위한 계약입니다.

> 좋은 image encoder는 이미지를 정답으로 직접 바꾸지 않습니다. 대신 나중에 검색과 추론이 잘 일어나는 표현으로 바꿔 줍니다.

## 핵심 개념

### 왜 image encoder부터 봐야 하나

multimodal 시스템의 품질은 결국 image encoder가 만들어내는 representation의 품질에서 출발합니다. CLIP과 ViT(Vision Transformer)는 현재 거의 모든 VLM의 image side에 들어가는 두 축이고, BLIP-2, LLaVA, GPT-4V도 ViT 계열을 backbone으로 씁니다. 1편에서 hybrid fusion을 다뤘다면, 이번 편은 그 입력단인 vision encoder를 직접 들여다봅니다.

### ViT: 이미지를 token sequence로 바라보기

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

### CLIP: text와 image를 같은 공간에 정렬하기

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

### CLIP을 그대로 쓰는 세 가지 패턴

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

### ViT 모델 선택 가이드

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

### 실무에서 encoder를 평가하는 기준

image encoder를 비교할 때 단순히 리더보드 점수만 보면 실제 운영 감각을 놓치기 쉽습니다. 실무에서는 첫째가 입력 전처리 민감도, 둘째가 embedding 품질의 일관성, 셋째가 지연 시간과 메모리 사용량입니다. 같은 top-1 성능이라도 전처리 규약이 까다로운 모델은 운영에서 훨씬 다루기 어렵습니다.

또한 retrieval 품질은 단일 예제로 판단하면 안 됩니다. 잘 맞는 샘플 몇 장보다 어려운 클래스 경계, 유사한 배경, 다국어 텍스트가 섞인 이미지에서 얼마나 안정적으로 거리 순서를 유지하는지가 더 중요합니다. 이 구간을 봐야 어떤 encoder가 실제 서비스에서 버틸지 감이 생깁니다.

좋은 팀은 encoder를 “모델 하나”로 보지 않고 전처리기, 임베딩 규약, 인덱스 설정까지 포함한 패키지로 평가합니다. 그 관점이 있어야 later stage에서 품질이 흔들려도 원인을 빠르게 좁힐 수 있습니다.

CLIP과 ViT를 빠르게 이해하려는 팀일수록 모델 카드와 processor 설정을 함께 읽는 습관이 중요합니다. 추론 품질은 대개 복잡한 fine-tuning보다 기본 계약을 얼마나 정확히 재현했는지에서 먼저 갈립니다.

## 흔히 헷갈리는 지점

- **preprocessing을 처리기 기본값과 다르게 적용** ViT는 ImageNet mean/std로 normalize하고, CLIP은 OpenAI의 별도 mean/std를 씁니다. 직접 PIL/torchvision으로 전처리하면 값이 달라져 정확도가 무너집니다. `transformers`의 `*ImageProcessor`를 그대로 쓰는 게 가장 안전합니다.
- **CLIP embedding을 normalize 안 하고 cosine 비교** CLIP feature는 normalize 후에 cosine similarity가 됩니다. raw vector로 dot product하면 length-bias가 들어가 검색 품질이 크게 떨어집니다.
- **zero-shot prompt를 한 줄만 써본다** CLIP zero-shot 정확도는 prompt 다양화로 +3~5% 더 올릴 수 있습니다. OpenAI 원 논문이 제안한 80개 prompt template (`a photo of a {}`, `a blurry photo of a {}` 등)을 평균내면 안정적입니다.
- **image encoder를 fine-tuning하려고 dataset만 늘림** CLIP backbone fine-tuning은 정교한 LR scheduling과 layer-wise learning rate decay가 필요합니다. 무작정 lr=1e-3로 풀어버리면 representation이 망가집니다. 처음에는 head만 학습하거나 LoRA를 권합니다.
- **입력 해상도를 무시한 cropping** CLIP-336 모델에 224 입력을 주거나 반대로 주면 positional embedding이 안 맞아 성능이 급락합니다. processor가 자동으로 resize하지만, custom dataloader를 쓰면 수동 확인이 필요합니다.

## 운영 체크리스트

- [ ] 학습 시 사용된 processor와 동일한 resize·crop·normalize 규칙을 재사용하는가
- [ ] 유사도 계산 전에 image/text embedding을 모두 정규화하는가
- [ ] zero-shot 분류에 단일 문장만 쓰지 않고 label별 prompt template을 비교하는가
- [ ] 모델의 입력 해상도와 patch 크기에 맞춰 품질 저하 지점을 측정했는가
- [ ] 추론용 encoder와 인덱스 구축용 encoder 버전을 엄격히 고정했는가

## 정리

ViT는 이미지를 patch token의 시퀀스로 바꾸고, CLIP은 그 시퀀스에서 나온 표현을 텍스트 표현과 같은 공간에 맞춥니다. 이 두 단계를 이해하면 멀티모달 retrieval과 zero-shot classification이 더 이상 마술처럼 보이지 않습니다.

실무적으로는 CLIP을 그대로 쓰는 패턴만으로도 검색, 분류, reranking의 출발점을 만들 수 있습니다. 큰 VLM이 없더라도 충분히 쓸 만한 기능이 나온다는 점이 중요합니다.

다음 글에서 VLM 아키텍처를 볼 때도 오늘의 관점이 계속 이어집니다. 결국 Vision-Language Model은 좋은 image encoder가 만든 표현을 LLM이 어떻게 받아들이느냐의 문제이기 때문입니다.

<!-- toc:begin -->
## Multimodal AI 101 시리즈

- [Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- **Image Encoder: CLIP과 ViT (현재 글)**
- [Vision-Language Model 아키텍처](./03-vlm-architecture.md)
- [Image Captioning과 OCR 파이프라인](./04-captioning-ocr-pipelines.md)
- [Multimodal RAG: 이미지와 텍스트를 함께 검색하기](./05-multimodal-rag.md)
- [오디오 처리와 Whisper STT](./06-audio-whisper.md)
- [Diffusion으로 Text-to-Image 생성](./07-text-to-image-diffusion.md)
- [Multimodal Embedding과 Cross-modal 검색](./08-multimodal-embeddings.md)
- [Video 이해 - Frame Sampling에서 Video-LLaVA까지](./09-video-understanding.md)
- [Production Multimodal Application 구축](./10-production-multimodal-app.md)
<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Dosovitskiy et al. - An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale (ViT)](https://arxiv.org/abs/2010.11929)
- [Radford et al. - Learning Transferable Visual Models From Natural Language Supervision (CLIP)](https://arxiv.org/abs/2103.00020)
- [HuggingFace - CLIP Documentation](https://huggingface.co/docs/transformers/model_doc/clip)
- [Zhai et al. - Sigmoid Loss for Language Image Pre-Training (SigLIP)](https://arxiv.org/abs/2303.15343)

### 관련 시리즈

- [Vector Search 101 - 임베딩이란 무엇인가](../../vector-search-101/ko/01-what-is-embedding.md)
- [Vector Search 101 - 코사인 유사도와 벡터 검색](../../vector-search-101/ko/03-cosine-similarity.md)
- [RAG 평가와 벤치마크 101 - 임베딩 모델 비교](../../rag-benchmark-101/ko/03-embedding-comparison.md)

Tags: CLIP, ViT, Image Encoder, Contrastive Learning, OpenAI, Vision Transformer
