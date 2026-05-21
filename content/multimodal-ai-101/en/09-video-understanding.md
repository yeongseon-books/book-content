---
title: "Multimodal AI 101 (9/10): Video Understanding - From Frame Sampling to Video-LLaVA"
series: multimodal-ai-101
episode: 9
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Video Understanding
- Video-LLaVA
- Frame Sampling
- Temporal Modeling
- VideoMAE
- Action Recognition
last_reviewed: '2026-05-14'
seo_description: An image is a single frame; a video is a frame sequence with a time
  axis.
---

# Multimodal AI 101 (9/10): Video Understanding - From Frame Sampling to Video-LLaVA

This is post 9 in the Multimodal AI 101 series.

> Multimodal AI 101 series (9/10)

---

An image is a single frame; a video is a frame sequence with a time axis. A one-minute clip at 30fps is 1,800 frames, and feeding all of them into a VLM blows up the token budget and the GPU at the same time. Ninety percent of video understanding is the sampling and aggregation question: which frames do we pick, and which model do we feed them to?

This episode covers frame sampling strategies, the core temporal models (VideoMAE, TimeSformer, Video-LLaVA), an action recognition pipeline, and production pitfalls.


![Multimodal AI 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/09/09-01-big-picture.en.png)
*Multimodal AI 101 chapter 9 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Video Understanding - From Frame Sampling to Video-LLaVA?
- Which signal should the example or diagram make visible for Video Understanding - From Frame Sampling to Video-LLaVA?
- What failure should be prevented first when Video Understanding - From Frame Sampling to Video-LLaVA reaches a real system?

## Questions this article answers

- Why is frame sampling the first key decision in video understanding?
- When are PyAV and scene-change-based keyframe extraction each useful?
- What trade-offs do video encoders like VideoMAE, TimeSformer, and X-CLIP make?
- What frame grouping is most practical for Video-LLaVA Q&A?
- Why do fps confusion, codec dependence, ignoring audio, and memory management often become operational issues?

## 1. Why Frame Sampling Is the Core Decision

Suppose we want to process a 10-minute 1080p clip at 30fps end-to-end:

- frames: 18,000
- ViT-L patch tokens per frame: 256
- total tokens: 4.6M

GPT-4V has a 128K context window; Gemini 1.5 Pro has 1M. A single video already exceeds every model. So we have to reduce frames.

| Strategy | Description | Trade-off |
| --- | --- | --- |
| Uniform | Pick N frames at equal spacing | Simple; misses short events |
| Keyframe | Detect scene changes, keep representative frames | Efficient; depends on detector quality |
| Dense + downsample | Extract every frame, let the model compress | Accurate; expensive |
| Adaptive | Variable rate driven by motion or audio | Best quality; complex |

Most production systems land on uniform 8 to 32 frames as the sweet spot. Video-LLaVA uses 8, VideoChat-2 uses 16, Gemini 1.5 handles 100+.

## 2. Pulling Frames with PyAV

```python
import av
import numpy as np
from PIL import Image

def sample_uniform_frames(path: str, n_frames: int = 8) -> list[Image.Image]:
    container = av.open(path)
    stream = container.streams.video[0]
    total = stream.frames or int(stream.duration * stream.average_rate)
    indices = np.linspace(0, total - 1, n_frames).astype(int)

    frames = []
    target_set = set(indices.tolist())
    for i, frame in enumerate(container.decode(stream)):
        if i in target_set:
            frames.append(frame.to_image())
            if len(frames) == n_frames:
                break
    container.close()
    return frames

frames = sample_uniform_frames("clip.mp4", n_frames=8)
print(f"sampled {len(frames)} frames, first size = {frames[0].size}")
```

PyAV is an ffmpeg binding, so it handles mp4, webm, and mov through one API. OpenCV (`cv2.VideoCapture`) works too, but PyAV has better codec compatibility.

## 3. Keyframe Extraction Based on Scene Change

```python
import av
import numpy as np

def extract_keyframes(path: str, threshold: float = 30.0) -> list:
    container = av.open(path)
    stream = container.streams.video[0]

    keyframes = []
    prev_hist = None
    for frame in container.decode(stream):
        img = frame.to_ndarray(format="rgb24")
        hist = np.histogram(img, bins=32, range=(0, 256))[0].astype("float32")
        hist /= hist.sum() + 1e-8

        if prev_hist is None:
            keyframes.append(frame.to_image())
        else:
            diff = np.sum((hist - prev_hist) ** 2 / (hist + prev_hist + 1e-8))
            if diff > threshold:
                keyframes.append(frame.to_image())
        prev_hist = hist
    container.close()
    return keyframes
```

Scene-change detection grows linearly with clip length, so always cap the result (for example, max 32 frames) to keep downstream cost predictable.

## 4. Comparing Video Encoders: VideoMAE, TimeSformer, X-CLIP

| Model | Input | Core idea | Use case |
| --- | --- | --- | --- |
| TimeSformer | 8-64 frames | Separate spatial and temporal attention | Action recognition |
| VideoMAE v2 | 16 frames | Masked autoencoder pretraining | Feature extractor |
| X-CLIP | 8-32 frames | CLIP extended to video, aligned with text | Zero-shot action |
| Video-LLaVA | 8 frames | LLaVA backbone + video projector | Video Q&A |
| InternVideo2 | Variable | Video foundation model | Unified backbone |

```python
from transformers import VideoMAEImageProcessor, VideoMAEForVideoClassification
import torch

processor = VideoMAEImageProcessor.from_pretrained("MCG-NJU/videomae-base-finetuned-kinetics")
model = VideoMAEForVideoClassification.from_pretrained("MCG-NJU/videomae-base-finetuned-kinetics")

frames = sample_uniform_frames("clip.mp4", n_frames=16)
inputs = processor(frames, return_tensors="pt")

with torch.no_grad():
    logits = model(**inputs).logits

pred_id = logits.argmax(-1).item()
print(f"Kinetics-400 label: {model.config.id2label[pred_id]}")
```

VideoMAE gives a strong baseline on Kinetics-400 (400 actions). For a custom domain, fine-tuning only the classification head is usually enough.

## 5. Video Q&A with Video-LLaVA

```python
from transformers import VideoLlavaProcessor, VideoLlavaForConditionalGeneration
import torch

processor = VideoLlavaProcessor.from_pretrained("LanguageBind/Video-LLaVA-7B-hf")
model = VideoLlavaForConditionalGeneration.from_pretrained(
    "LanguageBind/Video-LLaVA-7B-hf",
    torch_dtype=torch.float16,
    device_map="auto",
)

frames = sample_uniform_frames("cooking.mp4", n_frames=8)
prompt = "USER: <video>\nWhat is the person doing in this video? ASSISTANT:"
inputs = processor(text=prompt, videos=frames, return_tensors="pt").to(model.device, torch.float16)

with torch.no_grad():
    out = model.generate(**inputs, max_new_tokens=200)
print(processor.batch_decode(out, skip_special_tokens=True)[0])
```

Video-LLaVA compresses 8 frames into a single video token sequence. That is enough for short clips (10 seconds to 1 minute). Longer videos use a chunk-and-merge pattern: ask each chunk separately, then summarize the answers with an LLM.

## 6. Action Recognition Pipeline End-to-End

A production action recognition pipeline looks like this:

```text
input video ──► frame sampler (8-16) ──► VideoMAE / X-CLIP ──► action label + score
                                                                   │
                                                                   ▼
                                                         confidence threshold
                                                                   │
                                                                   ▼
                                                  high-confidence ──► event store
                                                  low-confidence  ──► human review
```

- **Sampling**: uniform 16 frames as baseline, weighted by motion intensity
- **Encoder**: X3D-S on CPU, VideoMAE-Base on GPU
- **Aggregation**: smooth clip-level scores over a 5-second window
- **Threshold**: 0.7+ if precision matters, 0.4 if recall matters

## Operations checklist

- [ ] We choose sampling strategy based on question type, not just clip length
- [ ] We test codec and container fallbacks before videos hit the main pipeline
- [ ] We separate event-detection workloads from broad-summary workloads
- [ ] We decide explicitly whether audio is part of the evidence set
- [ ] We enforce frame-resize and batch-memory limits before GPU inference starts

## Five Common Pitfalls

### 1. Confusing fps with sampling rate

Without checking whether the source is 30fps or 60fps, the meaning of "8 frames" changes. Uniform sampling counts frame indices, but the real semantic is "how many seconds apart". Read video metadata first and sample by `total_seconds`.

### 2. Codec and container dependencies

A `.mp4` file can wrap H.264, H.265, or AV1, and OpenCV cannot open all of them. PyAV (ffmpeg) and decord have better compatibility; otherwise, transcode upfront with ffmpeg.

```bash
ffmpeg -i input.webm -c:v libx264 -crf 23 -preset fast output.mp4
```

### 3. Short events disappear under uniform sampling

If you need to catch a 0.5-second accident inside a 10-minute clip, uniform 16 frames means a 37-second gap, and the accident is gone. For event detection, you need dense sampling plus a second-stage classifier.

### 4. Ignoring the audio track

Impact sounds, claps, and screams appear in audio before the corresponding frames change. Ensembling an audio encoder (ImageBind or a dedicated model) raises action detection accuracy noticeably. In surveillance and safety domains, audio cues are decisive.

### 5. Frame memory management

Eight 1080p uint8 frames take about 50MB. A batch of 100 videos pins 5GB inside one process. Resize immediately after decode (for example, to 224x224), move large numpy arrays to GPU, and free the CPU copy right away.

```python
img = frame.to_image().resize((224, 224))  # shrink right away
```

## Key takeaways

- Video understanding is bottlenecked by frame count, so sampling strategy (uniform, keyframe, adaptive) is the first system design decision.
- Pull frames with PyAV and feed them to VideoMAE, TimeSformer, or X-CLIP for an action recognition baseline.
- Video-LLaVA enables 8-frame Q&A; longer clips use chunk-and-merge with an LLM summarizer.
- The standard pipeline is sampler → encoder → aggregator → threshold → event store.
- fps, codec, short events, audio cues, and memory are the most common production pitfalls.

---

## Answering the Opening Questions

- **What boundary should you inspect first when applying Video Understanding - From Frame Sampling to Video-LLaVA?**
  - The article treats Video Understanding - From Frame Sampling to Video-LLaVA as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Video Understanding - From Frame Sampling to Video-LLaVA?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Video Understanding - From Frame Sampling to Video-LLaVA reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Multimodal AI 101 (1/10): Why Multimodal AI Matters](./01-why-multimodal-matters.md)
- [Multimodal AI 101 (2/10): Image Encoders: CLIP and ViT](./02-image-encoders-clip-vit.md)
- [Multimodal AI 101 (3/10): Vision-Language Model Architecture](./03-vlm-architecture.md)
- [Multimodal AI 101 (4/10): Image Captioning and OCR Pipelines](./04-captioning-ocr-pipelines.md)
- [Multimodal AI 101 (5/10): Multimodal RAG: Searching Images and Text Together](./05-multimodal-rag.md)
- [Multimodal AI 101 (6/10): Audio Processing and Whisper STT](./06-audio-whisper.md)
- [Multimodal AI 101 (7/10): Text-to-Image with Diffusion](./07-text-to-image-diffusion.md)
- [Multimodal AI 101 (8/10): Multimodal Embeddings and Cross-modal Search](./08-multimodal-embeddings.md)
- **Video Understanding - From Frame Sampling to Video-LLaVA (current)**
- Building a Production Multimodal Application (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [PyAV cookbook: decoding video streams](https://pyav.org/docs/stable/cookbook/basics.html)
- [Hugging Face Transformers video-classification tasks](https://huggingface.co/docs/transformers/en/tasks/video_classification)
- [FFmpeg documentation](https://ffmpeg.org/documentation.html)

### Papers and model references

- [Tong et al. - VideoMAE: Masked Autoencoders Are Data-Efficient Learners for Video](https://arxiv.org/abs/2203.12602)
- [Bertasius et al. - Is Space-Time Attention All You Need for Video Understanding? (TimeSformer)](https://arxiv.org/abs/2102.05095)
- [Lin et al. - Video-LLaVA: Learning United Visual Representation by Alignment Before Projection](https://arxiv.org/abs/2311.10122)

### Related series

- [AI Agent 101 - Production operations](../../ai-agent-101/en/09-production-operations.md)

Tags: Video Understanding, Video-LLaVA, Frame Sampling, Temporal Modeling, VideoMAE, Action Recognition
