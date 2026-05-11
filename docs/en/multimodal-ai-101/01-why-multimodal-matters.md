---
title: Why Multimodal AI Matters
series: multimodal-ai-101
episode: 1
language: en
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Multimodal AI
- CLIP
- GPT-4V
- Flamingo
- Vision Language
- Modality Fusion
last_reviewed: '2026-05-03'
seo_description: 'After ChatGPT shipped in late 2022, a quiet assumption took hold:
  a single text LLM could solve almost any problem worth solving.'
---

# Why Multimodal AI Matters

> Multimodal AI 101 series (1/10)

---

## "Isn't a text LLM enough?"

After ChatGPT shipped in late 2022, a quiet assumption took hold: a single text LLM could solve almost any problem worth solving. That assumption broke once GPT-4V landed in September 2023 and Gemini and Claude 3 Opus followed with vision baked in. Users stopped sending plain text. They started pasting screenshots, dropping in chart images, and uploading entire PDFs.

The places where multimodal beats text-only are easy to enumerate: receipt OCR plus category classification, product image plus description for search, medical imaging plus patient history for diagnosis, code screenshot plus error message for debugging. Single-modality systems consistently underperform on these tasks.

This series is for engineers who plan to ship multimodal AI to production. Episode 1 covers why multimodal matters, the core architectural flow, and five pitfalls you should know before adoption.

## What multimodal AI actually solves

| Task | Text-only limitation | Multimodal solution |
| --- | --- | --- |
| Document QA | Tables and figures lost | VLM understands layout and figures together |
| Visual search | Keywords are imprecise | CLIP embeddings enable cross-modal retrieval |
| Screen automation | Depends on DOM | Screenshot-based visual grounding |
| Content moderation | Text can be bypassed | Joint image+text classification |
| Medical and industrial vision | Domain expertise needed | Image encoder plus LLM reasoning |

We are moving from an era of one specialized model per task (ResNet for classification, a separate OCR engine, a separate captioning model) into an era where a single VLM handles all of them.

## Three patterns of modality fusion

Multimodal model design ultimately reduces to one question: how do you put different modalities into the same representation space? Three patterns dominate.

1. **Early fusion**: concatenate raw inputs and feed them to one model. Simple, but modality-specific traits are hard to preserve.
2. **Late fusion**: encode each modality separately and combine in the final layer. Easy to implement, but cross-modal interaction is weak.
3. **Hybrid (cross-attention) fusion**: place cross-attention between an image encoder and a language model so they exchange information at every layer. CLIP, BLIP-2, LLaVA, and Flamingo all belong here.

The diagram below shows the typical hybrid flow.

```
[Image] -> Vision Encoder (ViT) -> visual tokens
                                        |
                                        v
[Text]  -> Tokenizer -> text tokens -> LLM (cross-attention) -> output
```

The key insight: visual tokens emitted by the vision encoder are consumed by the LLM as if they were extra text tokens. That is why LLaVA-style models reach near GPT-4V quality reasoning while leaving the base LLM training mostly untouched.

## First multimodal call: receipt analysis with GPT-4V

The fastest way to feel multimodal value is one OpenAI Vision call. The snippet below takes a receipt image and extracts items and prices as JSON.

```python
import base64
from openai import OpenAI

client = OpenAI()

def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_receipt(image_path: str) -> dict:
    b64 = encode_image(image_path)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": (
                        "Extract each item name and price from this receipt "
                        "and return a JSON array. "
                        'Format: [{"item": "...", "price": 0}]'
                    )},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                ],
            }
        ],
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content

print(analyze_receipt("samples/receipt.jpg"))
```

A text-only LLM would force the user to type the receipt by hand. One multimodal call covers OCR, parsing, and structuring at once.

## CLIP for cross-modal search: a preview

CLIP (OpenAI, 2021) is fairly called the on-ramp to multimodal AI. It places images and text in the same vector space, so the query "a photo of a cat" retrieves cat images directly.

```python
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

images = [Image.open(p) for p in ["cat.jpg", "dog.jpg", "car.jpg"]]
queries = ["a photo of a cat", "a vehicle on the street"]

inputs = processor(text=queries, images=images,
                   return_tensors="pt", padding=True)

with torch.no_grad():
    out = model(**inputs)

# image-text similarity matrix (queries x images)
logits = out.logits_per_text
probs = logits.softmax(dim=-1)
print(probs)
```

In production we typically precompute image embeddings into a FAISS index, then push the user query through the CLIP text encoder to find the nearest image. Episode 5 (Multimodal RAG) covers this in depth.

## Five common pitfalls

### 1. Token cost is much higher than text

A single image in GPT-4o vision usually consumes 765 to 2000 tokens. A 1280x1280 high-res image can take several thousand tokens per call. If your cost dashboard does not break out image tokens as a separate line item, you will not see where money is leaking.

### 2. Skipping resolution preprocessing hurts accuracy

Recommended input resolution differs by VLM. CLIP wants 224x224, GPT-4V works in 768x768 or 1024x2048 tiles. Sending a raw 4K image either loses detail or explodes cost.

```python
from PIL import Image

def prepare_for_vlm(path: str, max_side: int = 1024) -> Image.Image:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    scale = min(max_side / max(w, h), 1.0)
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)),
                         Image.LANCZOS)
    return img
```

### 3. Text-only eval sets miss multimodal regressions

Running classic text QA benchmarks tells you nothing about vision capability. You need MMMU, ChartQA, DocVQA, and similar multimodal benchmarks as a separate suite.

### 4. No policy for cross-modal information conflict

Image and text often disagree. When the user types "this receipt is 50,000 won" but the image shows 70,000 won, you need an explicit policy for which to trust. Encode the priority into the system prompt up front.

### 5. PII slips through inside images

ID cards, business cards, and screen captures with email addresses are invisible to text-level PII filters. A multimodal system needs an image-side PII detector (Tesseract OCR plus regex, AWS Rekognition Face) as its own stage.

## Key Takeaways

- Multimodal AI handles document QA, visual search, screen automation, and video analysis - tasks where text LLMs fall short - in a single model.
- Modality fusion patterns are early, late, and hybrid (cross-attention). Current SOTA is hybrid.
- One GPT-4o vision call covers OCR, parsing, and structuring. CLIP is the on-ramp to cross-modal search.
- Image token cost, resolution preprocessing, multimodal benchmarks, conflict-resolution policy, and image-side PII must be checked before production.
- Episode 2 dives into CLIP and ViT, the core image encoders.
## References

- [OpenAI - GPT-4V(ision) System Card](https://openai.com/index/gpt-4v-system-card/)
- [Radford et al. - Learning Transferable Visual Models From Natural Language Supervision (CLIP)](https://arxiv.org/abs/2103.00020)
- [Alayrac et al. - Flamingo: a Visual Language Model for Few-Shot Learning](https://arxiv.org/abs/2204.14198)
- [Liu et al. - Visual Instruction Tuning (LLaVA)](https://arxiv.org/abs/2304.08485)
