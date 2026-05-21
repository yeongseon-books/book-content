---
title: "Multimodal AI 101 (2/10): Image Encoders: CLIP and ViT"
series: multimodal-ai-101
episode: 2
language: en
status: publish-ready
targets:
  tistory: false
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
last_reviewed: '2026-05-14'
seo_description: The quality of any multimodal system ultimately rides on the quality
  of the representation produced by the image encoder.
---

# Multimodal AI 101 (2/10): Image Encoders: CLIP and ViT

Many teams jump straight to GPT-4o, Qwen2-VL, or LLaVA because that is where the user-visible magic happens. But most multimodal quality issues start lower in the stack. If the image encoder loses the wrong detail, every downstream classifier, retriever, and VLM adapter inherits the mistake.

This is post 2 in the Multimodal AI 101 series.

Here we focus on the layer that turns pixels into something searchable and comparable: ViT as the tokenization scheme for images, and CLIP as the shared space that lets text and images meet.

## Questions to Keep in Mind

- Why is the image encoder usually the first subsystem to debug when multimodal quality feels unstable?
- How does ViT turn an image into tokens, and why does that matter for retrieval and VLM design?
- What exactly does CLIP align, and why does that enable zero-shot classification and cross-modal search?

## Big Picture

![Multimodal AI 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/02/02-01-mental-model-encode-first-decide-later.en.png)

*Multimodal AI 101 chapter 2 flow overview*

This picture places Image Encoders: CLIP and ViT inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why start with the image encoder

The quality of any multimodal system ultimately rides on the quality of the representation produced by the image encoder. CLIP and ViT (Vision Transformer) are the two pillars on the image side of nearly every modern VLM, and BLIP-2, LLaVA, and GPT-4V all use ViT-family backbones. Episode 1 covered hybrid fusion; this episode looks directly at the vision encoder that feeds it.

## Mental model: encode first, decide later

## ViT: looking at images as a token sequence

CNNs process images by growing receptive fields from small to large. ViT does the opposite. It cuts the image into 16x16 patches, treats each patch as a token, and feeds the sequence straight into a Transformer.

```text
[224x224 image] -> 14x14 = 196 patches -> linear projection -> 196 tokens (+ CLS)
                                                                |
                                                                v
                                          Transformer Encoder (12 layers)
                                                                |
                                                                v
                                                  CLS embedding (= image vector)
```

Three points to internalize:

1. **Patch embedding**: each 16x16 patch is flattened and projected to a D-dimensional token. ViT-B/16 uses D = 768.
2. **Positional embedding**: position information is added the same way as in NLP. A learnable 1D positional embedding is the standard.
3. **CLS token**: a special token sits at the front of the sequence (BERT-style), and its output vector is used as the image representation.

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

That single vector becomes the input for a classifier head, an entry in a retrieval index, or the visual-token source for a multimodal model.

## CLIP: aligning text and images in one space

Even a great image vector cannot be compared to text on its own. CLIP trains an image encoder and a text encoder jointly, pulling matched (image, text) pairs together and pushing mismatched pairs apart with a contrastive loss.

The training signal is InfoNCE, a simple contrastive loss. Given N (image, text) pairs in a batch, you build an NxN similarity matrix and apply cross-entropy in both directions so the diagonal becomes the answer.

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

Trained on 400 million (image, alt-text) pairs, this simple loss yields 76% zero-shot ImageNet accuracy without ever seeing a label.

## Three patterns for using CLIP as-is

### Pattern 1: zero-shot classification

CLIP's strength is that you can add a new class without retraining. Run a prompt through the text encoder to build a class vector, then take cosine similarity against the image vector.

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

### Pattern 2: store image embeddings in a vector DB

This is the most common pattern for retrieval-style search. Precompute embeddings for every image into FAISS, then search by image or by text in the same space.

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

### Pattern 3: as the image tower of a VLM

LLaVA, BLIP-2, and MiniGPT-4 all use the last-layer output of a CLIP image encoder as visual tokens, training only a small projection layer to connect to the LLM. Freezing the encoder dramatically reduces training cost.

## Choosing a ViT

The selection table below covers options that come up most often in production.

| Model | Params | Input resolution | Recommended use |
| --- | --- | --- | --- |
| ViT-B/16 | 86M | 224x224 | General classification, prototyping |
| ViT-L/14 | 304M | 224x224 | High-quality embeddings |
| CLIP ViT-B/32 | 87M | 224x224 | Search, zero-shot classification |
| CLIP ViT-L/14-336 | 304M | 336x336 | LLaVA backbone, high resolution |
| EVA-CLIP-G/14 | 1B+ | 224-336 | When SOTA embeddings are required |
| SigLIP-Base | 200M | 224 | CLIP alternative with better training stability |

In practice, CLIP ViT-L/14-336 is the LLaVA-1.5 default, and SigLIP is adopted by recent VLMs like Google's PaliGemma. For zero-shot classification alone, ViT-B/32 is enough to start.

## How to verify an encoder before production

Before you care about leaderboard deltas, verify the contract around the model.

1. **Processor parity**: the same resize, crop, and normalization used in the model card must also be used in offline indexing and online inference.
2. **Score stability**: near-duplicate images should preserve ranking under small crops, color shifts, and compression noise.
3. **Prompt stability**: class prompts like `a photo of a {label}` should not collapse when a synonym is used.
4. **Latency ceiling**: the encoder should meet your batch-size and hardware budget before you commit to a corpus rebuild.

The biggest production mistake is evaluating only one clean image per class. Real failures show up on hard boundaries: similar backgrounds, partial crops, multilingual text inside images, or product variants that differ by one visual detail.

```python
def verify_top1_margin(probs, min_margin: float = 0.15) -> bool:
    top2 = sorted(probs, reverse=True)[:2]
    return (top2[0] - top2[1]) >= min_margin
```

**Expected output:** in a stable zero-shot classification setup, the top class should not just win. It should win by a margin that stays reasonably consistent across crops and recompressions. If the margin collapses to noise after a trivial resize change, your preprocessing contract is already broken.

## Five common pitfalls

### 1. Preprocessing different from the processor's defaults

ViT normalizes with ImageNet mean/std, while CLIP uses OpenAI's own mean/std. Hand-rolled preprocessing with PIL/torchvision usually produces wrong values and accuracy collapses. Use the matching `*ImageProcessor` from `transformers` directly.

### 2. Not normalizing CLIP embeddings before cosine

CLIP features become cosine similarity only after L2 normalization. Raw dot products introduce length bias and noticeably hurt retrieval quality.

### 3. Trying only one zero-shot prompt

CLIP zero-shot accuracy gains another 3-5% from prompt diversification. Averaging the 80 prompt templates from the original OpenAI paper (`a photo of a {}`, `a blurry photo of a {}`, etc.) is a reliable boost.

### 4. Fine-tuning by just adding more data

Fine-tuning a CLIP backbone needs careful LR scheduling and layer-wise learning rate decay. Unfreezing everything at lr=1e-3 destroys the representation. Start by training only the head, or use LoRA.

### 5. Mismatched input resolution

Feeding 224 inputs to a CLIP-336 model (or vice versa) breaks positional embeddings and tanks accuracy. Processors handle resize automatically, but custom data loaders need a manual sanity check.

## Operations checklist

- [ ] We reuse the exact processor contract for offline indexing and online inference
- [ ] We normalize image and text embeddings before cosine or inner-product search
- [ ] We test prompt-template sensitivity instead of trusting a single zero-shot phrase
- [ ] We measure score stability on near-duplicate and hard-boundary image sets
- [ ] We pin the encoder version before building or rebuilding a retrieval index

## Key Takeaways

- ViT cuts images into 16x16 patches, feeds them to a Transformer, and uses the CLS token output as the image vector.
- CLIP aligns image and text encoders in one space using InfoNCE contrastive loss. Trained on 400M pairs, it reaches 76% zero-shot ImageNet accuracy.
- Three usage patterns: zero-shot classification, vector-DB embedding, and the image tower of a VLM.
- Model selection ladder: ViT-B/32 (prototyping) -> CLIP ViT-L/14-336 (LLaVA-grade) -> SigLIP (stable modern alternative).
- Verify processor preprocessing, normalization, prompt diversification, fine-tuning policy, and resolution match before going to production.

---

## Answering the Opening Questions

- **Why is the image encoder usually the first subsystem to debug when multimodal quality feels unstable?**
  - The article treats Image Encoders: CLIP and ViT as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How does ViT turn an image into tokens, and why does that matter for retrieval and VLM design?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What exactly does CLIP align, and why does that enable zero-shot classification and cross-modal search?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Multimodal AI 101 (1/10): Why Multimodal AI Matters](./01-why-multimodal-matters.md)
- **Image Encoders: CLIP and ViT (current)**
- Vision-Language Model Architecture (upcoming)
- Image Captioning and OCR Pipelines (upcoming)
- Multimodal RAG: Searching Images and Text Together (upcoming)
- Audio Processing and Whisper STT (upcoming)
- Text-to-Image with Diffusion (upcoming)
- Multimodal Embeddings and Cross-modal Search (upcoming)
- Video Understanding - From Frame Sampling to Video-LLaVA (upcoming)
- Building a Production Multimodal Application (upcoming)

<!-- toc:end -->

## References

- [Dosovitskiy et al. - An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale (ViT)](https://arxiv.org/abs/2010.11929)
- [Radford et al. - Learning Transferable Visual Models From Natural Language Supervision (CLIP)](https://arxiv.org/abs/2103.00020)
- [HuggingFace - CLIP Documentation](https://huggingface.co/docs/transformers/model_doc/clip)
- [Zhai et al. - Sigmoid Loss for Language Image Pre-Training (SigLIP)](https://arxiv.org/abs/2303.15343)

Tags: CLIP, ViT, Image Encoder, Contrastive Learning, OpenAI, Vision Transformer
