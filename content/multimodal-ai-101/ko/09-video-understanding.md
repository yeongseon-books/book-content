---
title: Video 이해 - Frame Sampling에서 Video-LLaVA까지
series: multimodal-ai-101
episode: 9
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Video Understanding
- Video-LLaVA
- Frame Sampling
- Temporal Modeling
- VideoMAE
- Action Recognition
last_reviewed: '2026-05-11'
seo_description: 이미지는 단일 frame이지만, video는 시간 축이 추가된 frame sequence입니다.
---

# Video 이해 - Frame Sampling에서 Video-LLaVA까지

> Multimodal AI 101 시리즈 (9/10)

---

이미지는 단일 frame이지만, video는 시간 축이 추가된 frame sequence입니다. 1분짜리 30fps 영상은 1,800 frame이고, 이걸 그대로 VLM에 던지면 token 폭발과 GPU OOM이 동시에 옵니다. video understanding의 90%는 "어떤 frame을 어떻게 골라 어떤 모델에 넣을 것인가"라는 sampling/aggregation 문제입니다.

이 글에서는 frame sampling 전략, temporal modeling 핵심 모델(VideoMAE, TimeSformer, Video-LLaVA), action recognition 파이프라인, 그리고 production 함정을 다룹니다.


## 1. 왜 Frame Sampling이 핵심인가

10분 영상(1080p, 30fps)을 그대로 처리한다고 가정합시다.

- frame 수: 18,000
- ViT-L 기준 frame당 patch token: 256개
- 총 token: 4.6M

GPT-4V context window가 128K, Gemini 1.5 Pro가 1M token 이라는 점을 생각하면 단일 영상이 모든 model의 한계를 넘깁니다. 그래서 frame을 줄여야 합니다.

| 전략 | 설명 | 장단점 |
| --- | --- | --- |
| Uniform | N개를 균등 간격으로 | 간단, 짧은 event 놓침 |
| Keyframe | scene change 감지 후 대표 frame | 효율적, 알고리즘 의존 |
| Dense + downsample | 모든 frame 추출 후 model이 압축 | 정확, 비용 큼 |
| Adaptive | motion이나 audio 기반 가변 sampling | 최고 품질, 구현 복잡 |

대부분의 production system은 uniform 8~32 frame이 sweet spot입니다. Video-LLaVA는 8, VideoChat-2는 16, Gemini 1.5는 100+를 처리합니다.

## 2. PyAV로 frame 뽑기

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
            img = frame.to_image()
            frames.append(img)
            if len(frames) == n_frames:
                break
    container.close()
    return frames

frames = sample_uniform_frames("clip.mp4", n_frames=8)
print(f"sampled {len(frames)} frames, first size = {frames[0].size}")
```

PyAV는 ffmpeg binding이라 mp4/webm/mov를 동일 API로 처리합니다. OpenCV(`cv2.VideoCapture`)도 비슷하지만 codec 호환성에서 PyAV가 안정적입니다.

## 3. Scene change 기반 keyframe 추출

```python
import av
import numpy as np

def extract_keyframes(path: str, threshold: float = 30.0) -> list[Image.Image]:
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
            # 카이제곱 거리
            diff = np.sum((hist - prev_hist) ** 2 / (hist + prev_hist + 1e-8))
            if diff > threshold:
                keyframes.append(frame.to_image())
        prev_hist = hist
    container.close()
    return keyframes
```

scene change detection은 영상 길이에 비례해 frame이 늘어나기 때문에, max cap(예: 32개)을 같이 두는 게 안전합니다.

## 4. Video Encoder 비교: VideoMAE, TimeSformer, X-CLIP

| 모델 | 입력 | 핵심 아이디어 | 사용처 |
| --- | --- | --- | --- |
| TimeSformer | 8~64 frame | spatial + temporal attention 분리 | action recognition |
| VideoMAE v2 | 16 frame | masked autoencoder pretraining | feature extractor |
| X-CLIP | 8~32 frame | CLIP을 video로 확장, text prompt와 정렬 | zero-shot action |
| Video-LLaVA | 8 frame | LLaVA backbone + video projector | video Q&A |
| InternVideo2 | 가변 | video foundation model | 통합 backbone |

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

VideoMAE는 Kinetics-400 (400개 동작) classification을 baseline으로 잘 해줍니다. custom domain은 head만 fine-tune하면 빠릅니다.

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

Video-LLaVA는 8 frame을 하나의 video token sequence로 압축합니다. 짧은 clip(10초~1분) Q&A에는 충분하고, 더 긴 영상은 chunk 단위로 분할해서 따로 질의 후 answer를 LLM으로 통합하는 방식이 일반적입니다.

## 6. Action Recognition Pipeline 전체 구조

production action recognition pipeline은 이렇게 구성됩니다.

```text
영상 입력 ──► frame sampler (8~16) ──► VideoMAE / X-CLIP ──► action label + score
                                                                 │
                                                                 ▼
                                                       confidence threshold
                                                                 │
                                                                 ▼
                                                  high-confidence ──► event store
                                                  low-confidence ──► human review
```

- **Sampling**: uniform 16 frame이 baseline, motion intensity로 가중치
- **Encoder**: 빠른 CPU 환경이면 X3D-S, GPU면 VideoMAE-Base
- **Aggregation**: clip 단위 score를 시간 윈도(예: 5초)로 smoothing
- **Threshold**: precision 우선이면 0.7+, recall 우선이면 0.4

## 흔히 놓치는 함정 다섯 가지

### 1. fps와 sampling rate 혼동

원본이 30fps인지 60fps인지 확인 안 하면 "8 frame" 의미가 달라집니다. uniform sampling은 frame index 기준이지만 의미는 "몇 초 간격" 입니다. 영상 metadata를 먼저 읽어 `total_seconds`를 기준으로 sampling 하세요.

### 2. Codec과 container 의존성

`.mp4` 안에 H.264, H.265, AV1이 다 들어갈 수 있고 OpenCV가 일부 codec을 못 엽니다. PyAV(ffmpeg)나 decord가 호환성이 좋고, 안 되면 ffmpeg로 사전 transcode하세요.

```bash
ffmpeg -i input.webm -c:v libx264 -crf 23 -preset fast output.mp4
```

### 3. 짧은 event는 uniform sampling에서 사라짐

10분 영상에서 0.5초짜리 사고 장면을 잡아야 한다면 uniform 16 frame은 10분/16 = 37초 간격이라 그 사고를 통째로 놓칩니다. event detection이 목적이면 dense sampling + 2nd stage classifier가 필요합니다.

### 4. Audio track 무시

사고 충격음, 박수, 비명 같은 신호는 video frame보다 audio에 먼저 나타납니다. action detection 정확도를 높이려면 ImageBind나 별도 audio encoder를 ensemble 하세요. 특히 surveillance / safety 도메인에서는 audio cue가 결정적입니다.

### 5. Frame 메모리 관리

8 frame x 1080p uint8은 약 50MB입니다. 100개 영상을 batch로 돌리면 5GB가 한 process에 잡힙니다. PyAV decode 후 즉시 resize(예: 224x224)하고, 큰 numpy array는 GPU로 옮긴 뒤 CPU에서 즉시 free 하세요.

```python
img = frame.to_image().resize((224, 224))  # 즉시 축소
```

## 핵심 요약

- Video understanding은 frame 수가 곧 cost이므로 sampling 전략(uniform/keyframe/adaptive)이 시스템 설계의 첫 결정입니다.
- PyAV로 frame을 뽑고 VideoMAE/TimeSformer/X-CLIP에 넣으면 action recognition baseline이 됩니다.
- Video-LLaVA로 8 frame 기반 Q&A가 가능하며, 긴 영상은 chunk-and-merge 패턴을 씁니다.
- Pipeline은 sampler → encoder → aggregator → threshold → event store 구조가 표준입니다.
- fps, codec, 짧은 event, audio cue, 메모리는 production에서 가장 자주 빠지는 함정입니다.

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
- [Multimodal Embedding과 Cross-modal 검색](./08-multimodal-embeddings.md)
- **Video 이해 - Frame Sampling에서 Video-LLaVA까지 (현재 글)**
- Production Multimodal Application 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Tong et al. - VideoMAE: Masked Autoencoders Are Data-Efficient Learners for Video](https://arxiv.org/abs/2203.12602)
- [Bertasius et al. - Is Space-Time Attention All You Need for Video Understanding? (TimeSformer)](https://arxiv.org/abs/2102.05095)
- [Lin et al. - Video-LLaVA: Learning United Visual Representation by Alignment Before Projection](https://arxiv.org/abs/2311.10122)
- [PyAV Documentation - Decoding Video Streams](https://pyav.org/docs/stable/cookbook/basics.html)

Tags: Video Understanding, Video-LLaVA, Frame Sampling, Temporal Modeling, VideoMAE, Action Recognition
