---
title: "Multimodal AI 101 (8/10): Multimodal Embeddings and Cross-modal Search"
series: multimodal-ai-101
episode: 8
language: en
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
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
seo_description: 'Episode 5 covered the big picture of multimodal RAG. This episode
  goes deeper into the heart of that system: the multimodal embedding.'
---

# Multimodal AI 101 (8/10): Multimodal Embeddings and Cross-modal Search

This is the 8th post in the Multimodal AI 101 series.

> Multimodal AI 101 series (8/10)

---

Episode 5 covered the big picture of multimodal RAG. This episode goes deeper into the heart of that system: the multimodal embedding. Pulling text, image, and audio into the same vector space is what makes "search text with an image" or "search audio with text" actually work.

We will cover how multimodal embeddings are produced, compare OpenCLIP, SigLIP, ImageBind, and Jina CLIP, build a cross-modal index with FAISS, and walk through five production pitfalls.


![Multimodal AI 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/08/08-01-big-picture.en.png)
*Multimodal AI 101 chapter 8 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Multimodal Embeddings and Cross-modal Search?
- Which signal should the example or diagram make visible for Multimodal Embeddings and Cross-modal Search?
- What failure should be prevented first when Multimodal Embeddings and Cross-modal Search reaches a real system?

## 1. What Is a Multimodal Embedding

A single-modal embedding compresses meaning within one modality. A text encoder turns sentences into vectors; an image encoder turns images into vectors. Even with the same dimensionality, the two live in different spaces, so comparing them directly is meaningless.

A multimodal embedding aligns two modalities into one space using contrastive learning. Training pulls (image, caption) pairs together and pushes mismatched pairs apart, so a "dog photo" and the sentence "a photo of a dog" end up at nearby vectors.

```text
text "a sleeping cat"          ──┐
                                 ├──► shared space (e.g. 768-dim)
image (sleeping cat photo)      ──┘
        cosine similarity ≈ 0.31
```

Once an index is built, you can query it with text, image, or any aligned modality.

## 2. Comparing CLIP, SigLIP, and ImageBind

Four representative models:

| Model | Modalities | Dim | Training data | Notes |
| --- | --- | --- | --- | --- |
| OpenAI CLIP ViT-L/14 | text + image | 768 | 400M web pairs | The de facto baseline |
| OpenCLIP ViT-H/14 | text + image | 1024 | LAION-2B | Open weights, many multilingual variants |
| Google SigLIP | text + image | 768 | WebLI 4B | Sigmoid loss instead of softmax, stable at small batch |
| Meta ImageBind | text + image + audio + depth + thermal + IMU | 1024 | Multiple datasets | Six modalities in one space |
| Jina CLIP v2 | text + image | 1024 | Multilingual web | 89 languages including Korean |

Selection rules of thumb:

- English-only, lightweight baseline: OpenAI CLIP ViT-B/32
- Best quality under open license: OpenCLIP ViT-H/14 or SigLIP
- Multilingual support: Jina CLIP v2 or multilingual-CLIP
- Audio in the same space as text and image: ImageBind

## 3. Extracting Embeddings with OpenCLIP

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

The L2 normalization at the end is the key step. Cosine similarity expects unit vectors, and FAISS inner-product indexes assume normalized vectors as well.

## 4. Building a Cross-modal Index with FAISS

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

That is the minimal cross-modal search example. We pushed text in and got a ranking back over images. The reverse direction (image query into text corpus) uses the same code.

For larger corpora, replace `IndexFlatIP` with `IndexIVFFlat` or `IndexHNSW`:

```python
quantizer = faiss.IndexFlatIP(DIM)
index = faiss.IndexIVFFlat(quantizer, DIM, nlist=100, metric=faiss.METRIC_INNER_PRODUCT)
index.train(image_embeds)
index.add(image_embeds)
index.nprobe = 8  # number of clusters explored per query
```

`nprobe` is the recall-vs-latency knob. With 1M vectors and `nprobe=8`, expect roughly 0.95 recall at about 1ms per query.

## 5. Pulling Audio into the Same Space with ImageBind

ImageBind aligns six modalities into the same space:

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

All three vectors live in the same 1024-dim space, so querying with "dog barking" and retrieving a dog photo works naturally. Audio quality is biased toward video clips, so it is strong on environmental sounds but weak on music or speech.

## 6. Hybrid Retrieval Patterns

In practice, cross-modal embeddings alone often lack precision. Two hybrid patterns appear repeatedly.

### 6.1 Embedding + BM25 ensemble

```python
def hybrid_score(query: str, doc, alpha: float = 0.6) -> float:
    sem = semantic_score(query, doc)   # CLIP / embedding based
    lex = bm25_score(query, doc)       # lexical match
    return alpha * sem + (1 - alpha) * lex
```

Run BM25 against image metadata (filename, EXIF, caption) and combine with visual similarity. Search quality jumps noticeably.

### 6.2 Two-stage: candidate then rerank

Stage 1 uses fast ANN (IVF or HNSW) to fetch top-100. Stage 2 reranks with a heavier model (BLIP-2, LLaVA, ColBERT). User-facing latency is set by stage 1, while accuracy is set by stage 2.

## Five Common Pitfalls

### 1. Forgetting normalization

If the code assumes cosine similarity but skips L2 normalization, vectors with larger magnitude always win. Make `v / v.norm()` part of the embedding step, not an afterthought at query time.

### 2. Score distributions differ across modalities

Text-text similarity and text-image similarity follow different distributions even within the same model. CLIP text-image cosine clusters around 0.20 to 0.35. An absolute threshold like "match if score > 0.5" is dangerous; use per-query percentiles or a top-k cutoff instead.

### 3. Dimensions and normalization differ across models

OpenAI CLIP ViT-L/14 is 768-dim; OpenCLIP ViT-H/14 is 1024-dim; SigLIP uses a different logit scale. Never mix embeddings from different models in one corpus, and rebuild the index whenever you switch models.

### 4. Multilingual queries against an English-only model

OpenAI CLIP was trained on roughly 95% English text. Korean queries land at half the recall. Move to multilingual-CLIP, Jina CLIP v2, or KoCLIP, or have an LLM translate the query into English before search.

### 5. Inconsistent image preprocessing

Pretrained models assume a specific resize, crop, and normalization. ViT-B/32 expects 224x224 center crop; SigLIP expects 384x384. Hand-rolling resize with PIL shaves 0.05 to 0.10 off similarity scores. Always reuse the `preprocess` returned alongside the model.

## Key takeaways

- A multimodal embedding is the result of contrastive learning that aligns text, image, and audio into one vector space.
- OpenCLIP is the open baseline, SigLIP is stable, ImageBind covers six modalities, and Jina CLIP v2 leads on multilingual.
- Start with FAISS `IndexFlatIP`; move to `IndexIVFFlat` or `IndexHNSW` as the corpus grows.
- Hybrid retrieval (BM25 ensemble, two-stage rerank) compensates for the limits of single-vector search.
- Verify normalization, score distributions, model dimensions, multilingual support, and preprocessing before going to production.

---

## Embedding Quality Checks: Separating Offline and Online Metrics

Multimodal embedding offline scores and online satisfaction frequently diverge. Offline uses Recall@K, nDCG, and MRR; online requires click-through rate, save rate, and re-query rate together to properly interpret quality. Cross-modal search perceived quality varies greatly depending on how users consume results.

```python
from collections import defaultdict

stats = defaultdict(int)


def log_search_event(query_type: str, clicked: bool, reformulated: bool) -> None:
    stats[f"{query_type}_total"] += 1
    if clicked:
        stats[f"{query_type}_clicked"] += 1
    if reformulated:
        stats[f"{query_type}_reformulated"] += 1
```

Separating these event logs by modality quickly reveals gaps—for instance, "text-to-image search" works well but "image-to-document search" is weak.

## CLIP Embedding + Metadata Combined Reranking

CLIP-only search is fast but struggles to reflect domain constraints. In e-commerce, for example, incorporating category, price range, and stock status alongside embeddings raises real-world quality.

```python
def rerank_with_metadata(base_score: float, category_match: bool, in_stock: bool) -> float:
    score = base_score
    if category_match:
        score += 0.08
    if in_stock:
        score += 0.03
    return score
```

This approach significantly improves quality without retraining the model. The key is not hardcoding weights permanently but periodically re-tuning them through A/B experiments.

## Multilingual Query Correction Path

Using English-centric CLIP directly can degrade Korean query performance. Either switch to a multilingual embedding model or add a dual path that translates queries to English before searching.

```python
def normalize_query_for_clip(q: str, lang: str) -> str:
    if lang == "ko":
        return f"Translate to concise English retrieval query: {q}"
    return q
```

When introducing a translation path, store the original query alongside for auditability. Search quality issues often appear as a mixture of translation error and embedding error.

## Embedding Regeneration Migration Procedure

When swapping models, you often need to rebuild the entire vector index. For zero-downtime transition, use a dual-index strategy: build the new index in the background, route a percentage of traffic to it for quality verification, then fully switch over.

```python
class IndexRouter:
    def __init__(self):
        self.primary = "clip_v1"
        self.shadow = "clip_v2"
        self.shadow_ratio = 0.1
```

Transition criteria should include not just accuracy but latency, cache-hit changes, and user re-query rate. Otherwise you miss side effects introduced by the model swap.

## Why Score Normalization Is Needed in Hybrid Search

A common mistake in multimodal search is summing scores from different systems directly. CLIP cosine scores and BM25 scores—or text embedding scores—have different distributions, so naïve addition lets one channel dominate. A separate score normalization step is necessary.

```python
def minmax(x: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.0
    return (x - lo) / (hi - lo)


def fuse(clip_s: float, text_s: float, clip_rng: tuple[float, float], text_rng: tuple[float, float]) -> float:
    a = minmax(clip_s, *clip_rng)
    b = minmax(text_s, *text_rng)
    return 0.6 * a + 0.4 * b
```

Score normalization looks like a small implementation detail but is highly effective at reducing search quality variance. When upgrading models, distributions shift, so normalization parameters must be updated together to maintain stable results.

## Converting Search Failure Logs into Training Assets

Search failures are not just errors—they are embedding improvement data. Storing cases where users re-queried, top results that were not clicked, and manually corrected results as hard-negative sets significantly improves next-model evaluation quality.

```python
def build_hard_negative(query: str, shown_ids: list[str], clicked_ids: list[str]) -> list[str]:
    return [x for x in shown_ids if x not in clicked_ids]
```

This dataset is useful not only for model swaps but also for score calibration tuning. The habit of converting operational logs into quality assets builds long-term performance.

## Operational Review Loop: Fixing Weekly Checkpoints

Multimodal systems that judge health solely by model accuracy react too late. Fixing a set of items reviewed in every weekly operations meeting is more effective. For example, recording request volume, average latency, P95 latency, error rate, retry rate, cache hit rate, and user complaint rate in the same format catches small anomalies early.

Metrics should also be decomposed by stage. A single "success rate" number obscures which step is losing. Recording success rates separately for input validation, preprocessing, retrieval, and generation stages makes the bottleneck obvious. These decomposed metrics are especially useful for detecting regressions after model swaps or pipeline changes.

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

Fixing the operational loop also makes technology choices more grounded. When introducing a new model, you compare latency increase and cost increase on the same table instead of looking only at "accuracy improvement." Ultimately, production quality is maintained not by a single model upgrade but by a repeatable review loop.


## Answering the Opening Questions

- **How do multimodal embeddings differ from text embeddings, and why are they the core of cross-modal search?**
  - Text embeddings only compare sentences to sentences; multimodal embeddings align different inputs like images and text into the same coordinate system. With a shared space (as in the article's diagram of `a sleeping cat` and a cat photo), you can find images with text and find descriptions or audio assets with images—cross-modal search becomes possible.
- **What do CLIP, SigLIP, and ImageBind share and how do they differ, and what criteria guide selection?**
  - All three align cross-modality distances, but CLIP is the de facto baseline, SigLIP improves training stability with sigmoid loss for text-image, and ImageBind binds 6 modalities (including audio) into one space. So: English-centric search → CLIP; open-weight high-quality → OpenCLIP/SigLIP; audio in the same index → ImageBind—choose by purpose.
- **Why are preprocessing and normalization contract-level important when extracting vectors with OpenCLIP?**
  - The article's `embed_image()` and `embed_text()` both end with `feats / feats.norm(...)` because FAISS `IndexFlatIP` assumes normalized vectors for cosine similarity. Combined with the `preprocess` from `create_model_and_transforms()`, the same coordinate system is maintained—if resize/crop/normalization diverges, search score interpretation itself breaks.
<!-- toc:begin -->
## In this series

- [Multimodal AI 101 (1/10): Why Multimodal AI Matters](./01-why-multimodal-matters.md)
- [Multimodal AI 101 (2/10): Image Encoders: CLIP and ViT](./02-image-encoders-clip-vit.md)
- [Multimodal AI 101 (3/10): Vision-Language Model Architecture](./03-vlm-architecture.md)
- [Multimodal AI 101 (4/10): Image Captioning and OCR Pipelines](./04-captioning-ocr-pipelines.md)
- [Multimodal AI 101 (5/10): Multimodal RAG: Searching Images and Text Together](./05-multimodal-rag.md)
- [Multimodal AI 101 (6/10): Audio Processing and Whisper STT](./06-audio-whisper.md)
- [Multimodal AI 101 (7/10): Text-to-Image with Diffusion](./07-text-to-image-diffusion.md)
- **Multimodal Embeddings and Cross-modal Search (current)**
- Video Understanding - From Frame Sampling to Video-LLaVA (upcoming)
- Building a Production Multimodal Application (upcoming)

<!-- toc:end -->

## References

- [Radford et al. - Learning Transferable Visual Models From Natural Language Supervision (CLIP)](https://arxiv.org/abs/2103.00020)
- [Zhai et al. - Sigmoid Loss for Language Image Pre-Training (SigLIP)](https://arxiv.org/abs/2303.15343)
- [Girdhar et al. - ImageBind: One Embedding Space To Bind Them All](https://arxiv.org/abs/2305.05665)
- [FAISS Documentation - Index Types and Trade-offs](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)

Tags: Embeddings, Cross-modal Search, CLIP, ImageBind, FAISS, Multimodal Index
