---
title: "Multimodal AI 101 (4/10): Image Captioning and OCR Pipelines"
series: multimodal-ai-101
episode: 4
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- OCR
- Image Captioning
- BLIP
- Tesseract
- PaddleOCR
- Document AI
last_reviewed: '2026-05-14'
seo_description: Build efficient image captioning and OCR pipelines. Learn about BLIP, Tesseract, PaddleOCR, and hybrid VLM workflows for multimodal systems.
---

# Multimodal AI 101 (4/10): Image Captioning and OCR Pipelines

Teams new to document and screenshot understanding often think OCR is the whole problem. In practice, OCR gives you strings, but it does not preserve scene meaning, emphasis, layout hierarchy, or the fact that two nearby labels belonged to the same visual unit.

This is post 4 in the Multimodal AI 101 series.

Here we treat captioning and OCR as complementary stages rather than competing tools, then build the hybrid pipeline that most real systems end up shipping.

## Questions to Keep in Mind

- Why does "extract the text and move on" fail on receipts, screenshots, and structured documents?
- When should you use a lightweight captioner, and when does a full VLM call earn its cost?
- How do Tesseract, PaddleOCR, and cloud document APIs differ in real operating terms?

## Big Picture

![Multimodal AI 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/04/04-01-ocr-vlm-hybrid-pipeline.en.png)

*Multimodal AI 101 chapter 4 flow overview*

This picture places Image Captioning and OCR Pipelines inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Image Captioning and OCR Pipelines is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## "Doesn't pulling text out of an image cover it?"

Two requests show up constantly in production multimodal systems:

1. "Describe what is in this image in one line" (image captioning)
2. "Read the text inside this image as-is" (OCR)

It is tempting to assume one VLM call solves both. In practice, captioning and OCR are usually split across different models because of cost, latency, and accuracy trade-offs. This episode covers how to design those two pipelines.

## Image Captioning: two approaches

### BLIP-style dedicated captioning models

Caption-only models like BLIP, BLIP-2, and GIT are lightweight and fast. They run several images per second on CPU and dozens at a time on GPU.

```python
import torch
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).eval()

def caption(img_path: str, prompt: str | None = None) -> str:
    img = Image.open(img_path).convert("RGB")
    if prompt:
        inputs = processor(img, prompt, return_tensors="pt")
    else:
        inputs = processor(img, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=50)
    return processor.decode(out[0], skip_special_tokens=True)

print(caption("samples/dog.jpg"))
# > a brown dog sitting on a wooden floor
print(caption("samples/dog.jpg", prompt="a photography of"))
# > a photography of a brown dog with a happy face
```

The wins are latency and cost. BLIP-base does 50-100 ms per caption on GPU and is roughly 1/100 the cost of OpenAI's Vision API. That fits e-commerce catalogs of millions of images and log analysis at scale.

### VLM call for richer captions

Captions that need reasoning ("explain what trend this chart shows") are not BLIP's strength. VLMs like GPT-4o, Claude, and Gemini are the answer.

```python
from openai import OpenAI

client = OpenAI()

def rich_caption(image_url: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": (
                    "Describe this image as alt text for visually impaired users "
                    "in 150 characters or less. "
                    "Include the objects, the scene, and key numbers if a chart "
                    "or table is present."
                )},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }],
    )
    return resp.choices[0].message.content
```

Decision rule: object-recognition-level caption goes to BLIP; reasoning-with-context caption goes to a VLM.

## OCR: what to choose

OCR engines split into four categories.

| Category | Representative | Strength | Weakness |
| --- | --- | --- | --- |
| Classic CV | Tesseract | Free, stable, strong on English | Weak on handwriting, rotation, curves |
| Deep-learning OSS | PaddleOCR, EasyOCR | 80+ languages, layout-aware | Model size, GPU recommended |
| Cloud APIs | AWS Textract, Google Vision, Azure | Excellent table/form parsing | Per-page cost, data leaves the perimeter |
| VLM | GPT-4o, Claude | Natural-language queries, document QA | Token cost, accuracy varies |

In production a two-layer setup is typical: **fast and cheap OCR for raw text extraction**, then **a VLM only for stages that actually need reasoning**.

### Tesseract: the fastest start

```python
import pytesseract
from PIL import Image

def ocr_simple(img_path: str, lang: str = "kor+eng") -> str:
    img = Image.open(img_path)
    return pytesseract.image_to_string(img, lang=lang)

print(ocr_simple("samples/screenshot.png"))
```

For Korean recognition you must install `tesseract-ocr-kor` system data. The appeal is that one CLI call is enough.

### PaddleOCR: when you need Korean and layout

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang="korean")

def ocr_with_boxes(img_path: str) -> list[dict]:
    result = ocr.ocr(img_path, cls=True)
    rows = []
    for line in result[0]:
        bbox, (text, conf) = line
        rows.append({
            "text": text,
            "confidence": float(conf),
            "bbox": bbox,  # 4-point polygon
        })
    return rows

for r in ocr_with_boxes("samples/receipt.jpg")[:5]:
    print(f"[{r['confidence']:.2f}] {r['text']}")
```

Returning bounding boxes makes this strong for layout-aware work like receipts, business cards, and tables.

### Cloud APIs: when you need table structure

AWS Textract goes beyond plain OCR by structuring cells, key-value pairs, and tables. It excels on structured documents like invoices and insurance claims.

```python
import boto3

textract = boto3.client("textract", region_name="us-east-1")

def extract_tables(img_path: str) -> list:
    with open(img_path, "rb") as f:
        resp = textract.analyze_document(
            Document={"Bytes": f.read()},
            FeatureTypes=["TABLES"],
        )
    tables = [b for b in resp["Blocks"] if b["BlockType"] == "TABLE"]
    return tables
```

Cost runs around USD 0.05-0.065 per page. At 1M pages per month, self-hosted PaddleOCR plus post-processing is cheaper.

## OCR + VLM hybrid pipeline

The pattern that works in practice has five stages.

```text
[Image]
   |
   v
1. Image preprocessing (deskew, denoise, rotation)
   |
   v
2. Fast OCR (PaddleOCR/Tesseract) -> raw text + bbox
   |
   v
3. Layout analysis (optional) -> sections, tables
   |
   v
4. VLM (optional) -> NL reasoning, ambiguous-text correction
   |
   v
[Structured output]
```

Below is a minimal implementation of that hybrid.

```python
from PIL import Image
from paddleocr import PaddleOCR
from openai import OpenAI

ocr = PaddleOCR(use_angle_cls=True, lang="korean")
client = OpenAI()

def extract_then_reason(img_path: str, question: str) -> str:
    raw = ocr.ocr(img_path, cls=True)[0]
    text_block = "\n".join(line[1][0] for line in raw)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "The user gives you OCR-extracted text and a question. "
                "Answer while accounting for OCR errors."
            )},
            {"role": "user", "content": (
                f"OCR result:\n```\n{text_block}\n```\n\nQuestion: {question}"
            )},
        ],
    )
    return resp.choices[0].message.content

answer = extract_then_reason("samples/receipt.jpg",
                             "What is the total amount paid and the store name?")
print(answer)
```

This hybrid cuts cost by 90% or more while keeping accuracy close to VLM-only.

## Five common pitfalls

### 1. Running OCR on a rotated image as-is

Receipts shot on a phone carry EXIF orientation metadata. PIL does not rotate automatically, so handle it explicitly.

```python
from PIL import Image, ImageOps

def auto_rotate(path: str) -> Image.Image:
    img = Image.open(path)
    return ImageOps.exif_transpose(img)
```

### 2. Missing Korean language weights

Tesseract needs `kor.traineddata`, EasyOCR needs `["ko"]`, and PaddleOCR needs `lang="korean"`. Running Korean images on the English default produces meaningless output.

### 3. Ignoring confidence thresholds

OCR outputs always carry confidence scores. Drop anything below 0.6 or route it to a verification queue. Ignoring confidence lets downstream LLMs reason on garbage.

### 4. Using a caption as-is for SEO or accessibility

BLIP captions are short and generic ("a person sitting"). They lack the context required by alt-text standards (WCAG 1.1.1). For SEO or accessibility, post-process BLIP output or call a VLM separately.

### 5. PII leaking through caption/OCR output

Card numbers on receipts, phone numbers on business cards, and ID numbers on passport photos are all readable by OCR. Run a PII filter on caption/OCR output (see ai-data-preparation-101 Episode 4).

## Operations checklist

- [ ] We normalize rotation and resolution before OCR or captioning starts
- [ ] We load the correct language pack or model weights for the actual document language
- [ ] We route low-confidence OCR output to fallback or review instead of trusting it blindly
- [ ] We do not reuse raw BLIP output as final accessibility or SEO text without review
- [ ] We re-run PII filtering after OCR and caption text have been generated

## Key Takeaways

- Image captioning needs both fast BLIP-family models and reasoning-strong VLMs. Split by task character.
- OCR selection ladder: Tesseract (simple), PaddleOCR (Korean + layout), Cloud APIs (table structure), VLM (NL reasoning).
- In production, a fast-OCR -> layout -> VLM hybrid pipeline is best for both cost and accuracy.
- Verify EXIF rotation, language weights, confidence thresholds, alt-text post-processing, and PII filters before going live.
- Episode 5 covers how to index OCR/caption output into a vector DB for multimodal RAG.

---

## Answering the Opening Questions

- **Why does "extract the text and move on" fail on receipts, screenshots, and structured documents?**
  - The article treats Image Captioning and OCR Pipelines as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **When should you use a lightweight captioner, and when does a full VLM call earn its cost?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How do Tesseract, PaddleOCR, and cloud document APIs differ in real operating terms?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Multimodal AI 101 (1/10): Why Multimodal AI Matters](./01-why-multimodal-matters.md)
- [Multimodal AI 101 (2/10): Image Encoders: CLIP and ViT](./02-image-encoders-clip-vit.md)
- [Multimodal AI 101 (3/10): Vision-Language Model Architecture](./03-vlm-architecture.md)
- **Image Captioning and OCR Pipelines (current)**
- Multimodal RAG: Searching Images and Text Together (upcoming)
- Audio Processing and Whisper STT (upcoming)
- Text-to-Image with Diffusion (upcoming)
- Multimodal Embeddings and Cross-modal Search (upcoming)
- Video Understanding - From Frame Sampling to Video-LLaVA (upcoming)
- Building a Production Multimodal Application (upcoming)

<!-- toc:end -->

## References

- [Li et al. - BLIP: Bootstrapping Language-Image Pre-training](https://arxiv.org/abs/2201.12086)
- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)
- [Tesseract OCR User Manual](https://tesseract-ocr.github.io/tessdoc/)
- [AWS Textract Developer Guide](https://docs.aws.amazon.com/textract/latest/dg/what-is.html)

Tags: OCR, Image Captioning, BLIP, Tesseract, PaddleOCR, Document AI
