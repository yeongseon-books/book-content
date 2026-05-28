---
title: "Multimodal AI 101 (5/10): Multimodal RAG: Searching Images and Text Together"
series: multimodal-ai-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Multimodal RAG
- CLIP Embeddings
- Cross-modal Retrieval
- FAISS
- LangChain
- Vector Search
last_reviewed: '2026-05-14'
seo_description: A typical RAG system splits documents into chunks, embeds them into
  a vector DB, and retrieves the nearest chunks for a query embedding.
---

# Multimodal AI 101 (5/10): Multimodal RAG: Searching Images and Text Together

Classic text RAG starts to wobble the moment the answer depends on layout, iconography, or visual resemblance. Asking for "the slide where the red warning icon appears" or "the invoice that looks like this photo" is not a chunking problem. It is a representation problem.

This is the 5th post in the Multimodal AI 101 series.

Here we treat multimodal RAG as a retrieval redesign: what to index, what to keep out of the prompt, and how to keep image-aware search from becoming an expensive latency trap.


![Multimodal AI 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/05/05-01-strategy-3-hybrid-both-image-and-text-ve.en.png)
*Multimodal AI 101 chapter 5 flow overview*

> Multimodal RAG is not 'RAG with images added' — every step (chunking, embedding, retrieval, reranking, generation) has to be rethought when half the corpus is pixels, and the failure mode is silently degrading to text-only behavior.

## Questions to Keep in Mind

- Which questions fail first under text-only RAG once screenshots, charts, and scanned documents enter the corpus?
- What are the trade-offs between image-only, text-only, and hybrid indexing strategies?
- How should retrieval outputs be packaged before a VLM sees them?

## Questions text RAG cannot answer

A typical RAG system splits documents into chunks, embeds them into a vector DB, and retrieves the nearest chunks for a query embedding. But text chunks cannot answer "find the slide that contains a chart shaped like this" or "tell me where the red button is in this screenshot."

Multimodal RAG solves these by searching images and text in the same vector space. The CLIP work from Episode 2 and the OCR/captioning pipeline from Episode 4 come together here as one pipeline.

## Three indexing strategies

### Strategy 1: image embeddings only

Put CLIP image embeddings into a vector DB and encode queries with the CLIP text encoder. The simplest setup.

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

paths = ["slides/01.png", "slides/02.png", "slides/03.png"]
vecs = embed_images(paths)
index = faiss.IndexFlatIP(vecs.shape[1])
index.add(vecs)

def search_by_text(q: str, k: int = 3) -> list[str]:
    qi = proc(text=[q], return_tensors="pt", padding=True)
    with torch.no_grad():
        qv = model.get_text_features(**qi)
    qv = (qv / qv.norm(dim=-1, keepdim=True)).cpu().numpy().astype("float32")
    D, I = index.search(qv, k=k)
    return [paths[i] for i in I[0]]

print(search_by_text("a bar chart showing quarterly revenue"))
```

Strength: simplicity. Weakness: weak on text reasoning. Queries with numeric reasoning ("the slide where Q3 revenue dropped") often miss.

### Strategy 2: index captions + OCR text

Extract caption (BLIP) and OCR text (PaddleOCR) from each image, then index that text with a regular text embedder. A direct application of the Episode 4 pipeline.

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

def index_text(items: list[dict]):
    texts = [f"{it['caption']}\n\n{it['ocr_text']}" for it in items]
    vecs = embedder.encode(texts, normalize_embeddings=True).astype("float32")
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)
    return index, items

# Assumes caption / ocr_text are precomputed per image
items = [
    {"path": "slides/01.png",
     "caption": "bar chart of revenue",
     "ocr_text": "Q1: 1.2M Q2: 1.5M Q3: 0.9M"},
    # ...
]
index, items = index_text(items)

def search(q: str, k: int = 3):
    qv = embedder.encode([q], normalize_embeddings=True).astype("float32")
    D, I = index.search(qv, k=k)
    return [items[i] for i in I[0]]

for r in search("Q3 revenue dropped"):
    print(r["path"], r["caption"])
```

Strength: strong text reasoning. Weakness: extra caption/OCR pipeline cost, and visual details (color, shape, position) are lost.

### Strategy 3: hybrid (both image and text vectors)

The most common production pattern. Two vectors per image, indexed separately, then either or both searched depending on query intent.

```python
class HybridIndex:
    def __init__(self, clip_index, text_index, items):
        self.clip = clip_index   # CLIP image vectors
        self.text = text_index   # caption+OCR text vectors
        self.items = items

    def search(self, query: str, k: int = 5,
               alpha: float = 0.5) -> list[dict]:
        # alpha=0: text only / alpha=1: image only
        d_clip, i_clip = self.clip.search(self._clip_q(query), k=k * 3)
        d_text, i_text = self.text.search(self._text_q(query), k=k * 3)
        scores: dict[int, float] = {}
        for d, i in zip(d_clip[0], i_clip[0]):
            scores[i] = scores.get(i, 0) + alpha * float(d)
        for d, i in zip(d_text[0], i_text[0]):
            scores[i] = scores.get(i, 0) + (1 - alpha) * float(d)
        ranked = sorted(scores.items(), key=lambda x: -x[1])[:k]
        return [self.items[i] for i, _ in ranked]
```

Pick `alpha` dynamically by query intent: 0.7 for visual queries, 0.2 for fact/numeric queries.

## Generation: feeding retrieval into a VLM

RAG rarely stops at retrieval. The retrieved images go into a VLM for the final answer.

```python
import base64
from openai import OpenAI

client = OpenAI()

def encode(p: str) -> str:
    return base64.b64encode(open(p, "rb").read()).decode()

def answer(question: str, top_paths: list[str]) -> str:
    content = [{"type": "text", "text": question}]
    for p in top_paths[:3]:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encode(p)}"},
        })
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content}],
    )
    return resp.choices[0].message.content
```

Retrieve, take top-K images, inline into a VLM, generate. Same shape as text RAG, but the context now contains images.

The prompt-packaging rule matters as much as retrieval itself. If the question is mostly about numbers, OCR text and a caption may be enough, with only one or two images attached. If the question is explicitly visual, shipping the full image evidence becomes worth the extra cost. The mistake is treating every multimodal query as if it needs every representation at once.

```python
def choose_alpha(query: str) -> float:
    visual_terms = ["looks like", "icon", "shape", "color", "layout"]
    return 0.7 if any(t in query.lower() for t in visual_terms) else 0.2
```

**Expected output:** queries about appearance should lean toward the CLIP index and return visually similar items near the top. Queries about exact amounts, dates, or field values should lean toward OCR-plus-caption text and surface evidence with stronger lexical grounding.

## Evaluation: how to measure multimodal RAG

Measure retrieval accuracy and generation quality separately.

```python
def hit_at_k(predictions: list[list[str]],
             gold: list[str], k: int = 5) -> float:
    hits = sum(1 for pred, g in zip(predictions, gold) if g in pred[:k])
    return hits / len(gold)

def mrr(predictions: list[list[str]], gold: list[str]) -> float:
    total = 0.0
    for pred, g in zip(predictions, gold):
        if g in pred:
            total += 1.0 / (pred.index(g) + 1)
    return total / len(predictions)
```

- Retrieval: Recall@k, MRR, nDCG
- Generation: faithfulness (did the VLM use only the retrieved images?), answer relevancy

The ai-evaluation-101 series covers this evaluation framework in depth.

In practice, keep the eval set split by failure mode:

- **visual match queries**: "find the screen with the red alert badge"
- **layout queries**: "which PDF page has the table in the lower-right"
- **text extraction queries**: "what amount is shown in the invoice total"
- **mixed queries**: "find the slide with this chart and explain the drop in Q3"

If one strategy wins all four categories, great. In most real systems it does not, which is exactly why hybrid retrieval exists.

## Five common pitfalls

### 1. Mixing CLIP vectors with text-embedding vectors in one index

CLIP has its own latent space; BGE/OpenAI embeddings live in different latent spaces. Mixing them in one index makes distances meaningless. Keep separate indexes and combine scores with a weighted average.

### 2. Inlining all high-resolution images as base64

Each base64 image inlined to a VLM is tens to hundreds of kilobytes. Inlining all of top-10 explodes both token cost and latency. Cap at top-3 or use URL references.

### 3. Generating captions/OCR at query time

Re-extracting captions on every query adds seconds of latency. Compute and store caption/OCR at ingestion time.

### 4. Searching without metadata filters

Production indexes commonly grow past 10M images. Running ANN search without filters on user_id, document_type, or date_range causes both authorization leaks and performance degradation.

### 5. Eval set with text queries only

Multimodal RAG must be evaluated on text queries, image-by-image search, and image+text mixed queries. Include multimodal queries when designing the eval set.

## Operations checklist

- [ ] We decided explicitly which artifacts become searchable evidence: image vectors, OCR text, captions, or all three
- [ ] We keep image-space and text-space indexes separate and document the score-fusion rule
- [ ] We cap inline images in the final VLM prompt instead of sending every top-K artifact blindly
- [ ] We apply metadata and authorization filters before ANN retrieval returns candidates
- [ ] We evaluate visual, layout, text-extraction, and mixed queries as separate slices

## Key Takeaways

- Multimodal RAG picks one of three indexing strategies: image embeddings only, caption+OCR text, or hybrid.
- Hybrid is the most common production pattern: separate indexes per modality, weighted by per-query alpha.
- After retrieval, inline the top-K images into a VLM for the final answer. Top-3 is the typical cost/quality balance.
- Evaluate retrieval (Recall@k, MRR) and generation (faithfulness, relevancy) separately.
- Verify index separation, base64 inline limits, ingestion-time caption/OCR storage, metadata filters, and multimodal-query evaluation before production.

---

## Answering the Opening Questions

- **Why does text RAG immediately show performance limits on questions requiring images, tables, or layout?**
  - Indexing only text chunks fails to retrieve visual evidence—numbers in a table corner, button positions, colors and shapes. The article explained that you must redesign from the retrieval stage, separating CLIP image index, caption+OCR text index, and VLM final reading.
- **How do the three strategies—raw image embeddings, caption/OCR text, and dual index—differ for multimodal retrieval?**
  - Image-embedding-only index is strong for visual-pattern search via CLIP but weak for numeric reasoning. Caption+OCR text index is strong for queries like `Q3 revenue dropped` but loses visual details like color and position. The hybrid strategy (as in the article's `HybridIndex` code) blends both scores with `alpha` to handle visual and numeric queries differently.
- **What input combination is most practical when passing retrieval results to the VLM for final answering?**
  - Rather than dumping all retrieval results, selecting top-3 key images plus needed OCR/caption evidence for the VLM is most realistic. As the article's `answer()` example showed, sending retrieved images inline with `citations` and `retrieval_scores` lets you trace what evidence supported the answer—essential for production quality.
<!-- toc:begin -->
## In this series

- [Multimodal AI 101 (1/10): Why Multimodal AI Matters](./01-why-multimodal-matters.md)
- [Multimodal AI 101 (2/10): Image Encoders: CLIP and ViT](./02-image-encoders-clip-vit.md)
- [Multimodal AI 101 (3/10): Vision-Language Model Architecture](./03-vlm-architecture.md)
- [Multimodal AI 101 (4/10): Image Captioning and OCR Pipelines](./04-captioning-ocr-pipelines.md)
- **Multimodal RAG: Searching Images and Text Together (current)**
- Audio Processing and Whisper STT (upcoming)
- Text-to-Image with Diffusion (upcoming)
- Multimodal Embeddings and Cross-modal Search (upcoming)
- Video Understanding - From Frame Sampling to Video-LLaVA (upcoming)
- Building a Production Multimodal Application (upcoming)

<!-- toc:end -->

## References

- [LangChain - Multi-Modal RAG](https://python.langchain.com/docs/use_cases/question_answering/multi_modal_rag/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [Sentence-Transformers Documentation](https://www.sbert.net/)
- [BAAI BGE Embedding Model Card](https://huggingface.co/BAAI/bge-base-en-v1.5)

Tags: Multimodal RAG, CLIP Embeddings, Cross-modal Retrieval, FAISS, LangChain, Vector Search
