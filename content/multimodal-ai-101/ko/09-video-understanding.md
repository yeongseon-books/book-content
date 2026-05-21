---
title: "Multimodal AI 101 (9/10): Video 이해 - Frame Sampling에서 Video-LLaVA까지"
series: multimodal-ai-101
episode: 9
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Video Understanding
- Video-LLaVA
- Frame Sampling
- Temporal Modeling
- VideoMAE
- Action Recognition
last_reviewed: '2026-05-12'
seo_description: 이미지는 단일 frame이지만, video는 시간 축이 추가된 frame sequence입니다.
---

# Multimodal AI 101 (9/10): Video 이해 - Frame Sampling에서 Video-LLaVA까지

비디오는 이미지보다 어려운 것이 아니라, 시간 축이 추가된 데이터입니다. 그래서 많은 입문자가 비디오 이해를 “더 무거운 이미지 모델” 정도로 생각하다가 곧바로 막힙니다. 실제 핵심은 프레임 하나의 품질보다 어떤 순간을 뽑아 볼 것인지, 그리고 그 순서를 얼마나 보존할 것인지에 있습니다.

현실적인 비디오 시스템은 전 영상을 매 프레임 분석하지 않습니다. uniform sampling, keyframe extraction, scene change detection처럼 먼저 시간을 줄이고, 그다음 encoder나 VLM으로 의미를 읽습니다. 이 전처리 설계가 잘못되면 뒤에 어떤 큰 모델을 붙여도 중요한 장면 자체를 놓쳐 버립니다.

또한 비디오는 오디오 트랙과 함께 들어오는 경우가 많습니다. 화면만 보고는 놓치는 사건이 있고, 반대로 음성만으로는 부족한 시각 단서가 있습니다. 그래서 video understanding은 frame sampling, visual encoding, audio fusion을 함께 봐야 전체 그림이 잡힙니다.

이 글에서는 비디오 이해를 “영상을 그대로 모델에 넣는 일”이 아니라, 시간 정보를 잃지 않으면서 의미 있는 샘플을 추출해 추론하는 단계적 파이프라인으로 정리합니다.

이 글은 Multimodal AI 101 시리즈의 9번째 글입니다.

비디오에서는 더 큰 모델보다 먼저, 무엇을 보여 줄지 결정하는 sampling 정책이 성능을 좌우합니다.

## 먼저 던지는 질문

- 왜 비디오 이해에서 frame sampling이 가장 먼저 결정해야 할 핵심 변수일까요?
- PyAV와 scene change 기반 keyframe extraction은 각각 어떤 장면에서 유용할까요?
- VideoMAE, TimeSformer, X-CLIP 같은 video encoder는 어떤 trade-off를 보여 줄까요?

## 큰 그림

![Multimodal AI 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/09/09-01-big-picture.ko.png)

*Multimodal AI 101 9장 흐름 개요*

이 그림에서는 Video 이해 - Frame Sampling에서 Video-LLaVA까지를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Video 이해 - Frame Sampling에서 Video-LLaVA까지의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

비디오는 고객 지원, 보안, 교육, 스포츠, 제조 현장 등 수많은 업무에서 이미 핵심 데이터가 되었습니다. 따라서 멀티모달 시스템이 문서와 이미지를 넘어서려면 결국 비디오 처리 감각이 필요합니다.

또한 비디오 이해는 멀티모달 설계 원칙을 압축해서 보여 줍니다. 입력 축소, 중요한 증거 보존, 시간 문맥 처리, 오디오와의 결합이 모두 한 문제 안에 들어 있기 때문입니다.

반대로 sampling 전략 없이 바로 모델부터 고르면 비용만 커지고 중요한 이벤트는 놓칩니다. 비디오에서 전처리는 부수 단계가 아니라 모델 성능의 일부입니다.

## 핵심 관점

이미지 모델은 한 장면의 의미를 읽습니다. 비디오 모델은 어떤 장면들이 언제 어떤 순서로 나타났는지까지 읽어야 합니다. 그래서 frame sampling은 단순한 속도 최적화가 아니라, 어떤 증거를 남기고 어떤 증거를 버릴지 결정하는 핵심 정책입니다.

이 관점으로 보면 uniform sampling과 keyframe extraction의 차이도 분명해집니다. 전자는 넓은 개요를 얻기 쉽고, 후자는 장면 전환을 더 잘 잡습니다. 어떤 질문을 받는 시스템인지에 따라 최적 전략이 달라집니다.

실무적으로는 영상 전체를 모델에 그대로 넣기보다, 좋은 샘플을 뽑아 더 가벼운 encoder나 VLM에 넘기는 편이 훨씬 예측 가능하고 비용 효율적입니다.

> 비디오 이해의 첫 번째 모델은 사실 sampling 정책입니다. 중요한 장면을 놓치면 그다음 모델은 아무리 커도 복구할 수 없습니다.

## 핵심 개념

### 1. 왜 Frame Sampling이 핵심인가

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

### 2. PyAV로 frame 뽑기

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

PyAV는 ffmpeg binding이라 mp4/webm/mov를 동일 API로 처리합니다. OpenCV(`cv2.VideoCapture`)도 비슷하지만 codec 호환성에서 PyAV가 안정적입니다.

### 3. Scene change 기반 keyframe 추출

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

scene change detection은 영상 길이에 비례해 frame이 늘어나기 때문에, max cap(예: 32개)을 같이 두는 게 안전합니다.

### 4. Video Encoder 비교: VideoMAE, TimeSformer, X-CLIP

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

### 5. Video Q&A with Video-LLaVA

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

### 6. Action Recognition Pipeline 전체 구조

production action recognition pipeline은 이렇게 구성됩니다.

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

- **Sampling**: uniform 16 frame이 baseline, motion intensity로 가중치
- **Encoder**: 빠른 CPU 환경이면 X3D-S, GPU면 VideoMAE-Base
- **Aggregation**: clip 단위 score를 시간 윈도(예: 5초)로 smoothing
- **Threshold**: precision 우선이면 0.7+, recall 우선이면 0.4

### sampling 전략을 질문 유형과 연결하기

모든 비디오 질문이 같은 sampling 전략을 요구하지는 않습니다. “이 영상이 전반적으로 무엇을 보여 주는가” 같은 질문은 넓은 간격의 uniform sampling으로도 충분할 수 있습니다. 반면 “언제 사람이 넘어졌는가”, “경고등이 켜진 순간이 있었는가” 같은 이벤트성 질문은 더 촘촘한 샘플이나 scene-aware extraction이 필요합니다.

즉 sampling은 모델 앞단의 최적화가 아니라 질문 유형에 대한 제품 정책입니다. 어떤 사용자 질문을 지원할 것인지 먼저 정해야, 필요한 시간 해상도와 프레임 수를 역산할 수 있습니다. 이 기준이 없으면 과도하게 많은 프레임을 넣어 비용만 늘리거나, 너무 적게 넣어 결정적 순간을 놓치게 됩니다.

비디오 시스템이 안정적인 이유는 더 많은 프레임을 보기 때문이 아니라, 필요한 순간을 더 일관되게 보기 때문입니다. sampling을 질문 유형과 연결해서 설계해야 하는 이유가 여기에 있습니다.

또 하나 기억할 점은, sampling 정책은 고정 상수가 아니라 도메인별 실험 결과라는 사실입니다. 스포츠, 감시, 회의, 교육 영상은 중요한 이벤트 길이가 모두 다르므로 같은 fps 기준을 그대로 적용하면 안 됩니다.

### 배포와 액션 인식까지 이어지는 예제

비디오 이해는 프레임 샘플링으로 끝나지 않습니다. 아래 예제는 모델 실행과 후속 액션 인식 파이프라인까지 연결되는 흐름을 보강합니다.

```bash
ffmpeg -i input.webm -c:v libx264 -crf 23 -preset fast output.mp4
```

```python
img = frame.to_image().resize((224, 224))  # shrink right away
```
## 프레임 샘플링 정책을 자동으로 선택하기

비디오 길이와 질문 유형이 다르면 최적 샘플링도 달라집니다. 고정 프레임 수를 모든 요청에 적용하면 짧은 영상에서는 과잉 계산이 발생하고, 긴 영상에서는 이벤트를 놓치기 쉽습니다. 그래서 길이와 목적에 따라 샘플링 전략을 분기하는 라우터가 필요합니다.

```python
def choose_sampling_policy(duration_sec: float, intent: str) -> dict:
    if intent in {"event_detection", "safety_alert"}:
        return {"mode": "dense", "fps": 2.0, "max_frames": 64}
    if duration_sec > 900:
        return {"mode": "keyframe", "max_frames": 48}
    return {"mode": "uniform", "frames": 16}
```

이 정책을 먼저 고정하면 모델 변경 시에도 비교 기준이 유지됩니다. 반대로 샘플링과 모델을 동시에 바꾸면 어떤 변경이 품질을 바꿨는지 분리하기 어렵습니다.

## 오디오 전사 결합: Whisper와 타임라인 통합

비디오 이해 품질을 끌어올리는 가장 실용적인 방법 중 하나는 오디오 전사를 함께 쓰는 것입니다. Whisper segment를 시간축에 정렬해 프레임 메타데이터와 결합하면, 장면 설명과 발화 정보를 동시에 질의할 수 있습니다.

```python
def attach_transcript_to_frame(frame_ts: float, segments: list[dict], window: float = 1.5) -> str:
    hits = [s["text"] for s in segments if abs((s["start"] + s["end"]) / 2 - frame_ts) <= window]
    return " ".join(hits)
```

이 결합은 "누가 무엇을 말할 때 어떤 장면이었는가"를 복원하는 데 매우 효과적입니다. 교육, 회의, 스포츠 분석처럼 내러티브가 중요한 도메인에서 특히 유용합니다.

## Video Q&A 평가 지표

비디오 QA는 정답 일치율만으로 품질을 판단하기 어렵습니다. 시간 위치를 맞췄는지, 잘못된 객체를 언급했는지, 근거 프레임을 제시했는지까지 함께 봐야 합니다.

```python
metrics = {
    "answer_exact_match": 0.0,
    "temporal_iou": 0.0,
    "evidence_frame_recall_at_3": 0.0,
}
```

운영에서는 이 지표를 대시보드로 분리해 두는 편이 좋습니다. 모델이 답변 문장만 그럴듯하게 만들고 시간 근거를 놓치는 경우가 생각보다 자주 발생하기 때문입니다.

## 긴 영상 처리: 청크 분할과 요약 병합

30분 이상 영상은 한 번에 처리하기보다 시간 청크로 분할해 요약을 만든 뒤 계층적으로 병합하는 편이 안정적입니다. 예를 들어 3분 단위 청크 요약을 먼저 만들고, 상위 LLM이 이 요약들을 다시 통합해 최종 보고서를 만드는 구조를 사용합니다.

```python
def chunk_ranges(duration_sec: int, chunk_sec: int = 180):
    ranges = []
    s = 0
    while s < duration_sec:
        e = min(duration_sec, s + chunk_sec)
        ranges.append((s, e))
        s = e
    return ranges
```

이 방식은 메모리와 컨텍스트 한계를 동시에 피하면서도 시간 순서를 유지하기 쉽습니다. 또한 특정 청크만 재처리할 수 있어 장애 복구도 단순해집니다.

## 이벤트 탐지에서 임계값 튜닝 절차

비디오 액션 인식은 임계값 설정에 따라 precision과 recall이 크게 바뀝니다. 그래서 운영 전에 도메인 목표를 먼저 정해야 합니다. 안전 사고 탐지는 recall 우선, 자동 태깅은 precision 우선처럼 목표가 다르면 임계값도 달라집니다.

```python
def classify_event(score: float, policy: str) -> str:
    if policy == "recall":
        return "event" if score >= 0.45 else "none"
    return "event" if score >= 0.72 else "none"
```

또한 단일 프레임 점수로 즉시 판단하지 말고 시간 윈도에서 스무딩하는 편이 좋습니다. 잡음으로 인한 순간 오탐을 줄일 수 있기 때문입니다.

이 절차를 문서화해 두면 모델 교체 후에도 같은 기준으로 비교가 가능해지고, 운영팀과 제품팀의 기대치를 맞추기 쉬워집니다.

## 프레임 저장 정책과 스토리지 비용

비디오 처리 시스템은 프레임 저장 정책이 없으면 저장소 비용이 빠르게 증가합니다. 전체 프레임 보관이 아니라 샘플 프레임과 근거 프레임만 남기는 정책을 명시해야 합니다.

```python
def keep_frame(is_evidence: bool, is_sampled: bool) -> bool:
    return is_evidence or is_sampled
```

근거 프레임을 남기면 나중에 사용자 문의 대응과 품질 감사가 쉬워집니다. 반대로 무분별한 저장은 비용과 개인정보 리스크를 키웁니다.

## 운영 검증 루프: 주간 점검 항목을 고정하기

멀티모달 시스템은 모델 정확도만으로 상태를 판단하면 늦게 대응하게 됩니다. 그래서 주간 운영 회의에서 항상 같은 항목을 점검하는 루프를 고정하는 편이 좋습니다. 예를 들어 요청량, 평균 지연 시간, P95 지연, 오류율, 재시도율, 캐시 히트율, 사용자 불만 비율을 동일 포맷으로 기록하면 작은 이상 징후를 초기에 잡을 수 있습니다.

또한 지표는 기능별로 분해해야 합니다. 단일 "성공률" 수치만 보면 어떤 단계에서 손실이 났는지 알기 어렵습니다. 입력 검증 단계, 전처리 단계, 검색 단계, 생성 단계를 분리해 성공률을 기록하면 병목 구간이 명확해집니다. 이 분해 지표는 모델 교체나 파이프라인 변경 후 회귀를 탐지하는 데 특히 유용합니다.

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

운영 루프를 고정하면 기술 선택도 더 현실적으로 바뀝니다. 새 모델을 도입할 때 "정확도 상승"만 보지 않고, 지연 증가와 비용 증가를 같은 표에서 비교할 수 있기 때문입니다. 결국 프로덕션 품질은 한 번의 모델 업그레이드가 아니라, 반복 가능한 점검 루프를 통해 유지됩니다.

## 흔히 헷갈리는 지점

- **fps와 sampling rate 혼동** 원본이 30fps인지 60fps인지 확인 안 하면 "8 frame" 의미가 달라집니다. uniform sampling은 frame index 기준이지만 의미는 "몇 초 간격" 입니다. 영상 metadata를 먼저 읽어 `total_seconds`를 기준으로 sampling 하세요.
- **Codec과 container 의존성** `.mp4` 안에 H.264, H.265, AV1이 다 들어갈 수 있고 OpenCV가 일부 codec을 못 엽니다. PyAV(ffmpeg)나 decord가 호환성이 좋고, 안 되면 ffmpeg로 사전 transcode하세요.
- **짧은 event는 uniform sampling에서 사라짐** 10분 영상에서 0.5초짜리 사고 장면을 잡아야 한다면 uniform 16 frame은 10분/16 = 37초 간격이라 그 사고를 통째로 놓칩니다. event detection이 목적이면 dense sampling + 2nd stage classifier가 필요합니다.
- **Audio track 무시** 사고 충격음, 박수, 비명 같은 신호는 video frame보다 audio에 먼저 나타납니다. action detection 정확도를 높이려면 ImageBind나 별도 audio encoder를 ensemble 하세요. 특히 surveillance / safety 도메인에서는 audio cue가 결정적입니다.
- **Frame 메모리 관리** 8 frame x 1080p uint8은 약 50MB입니다. 100개 영상을 batch로 돌리면 5GB가 한 process에 잡힙니다. PyAV decode 후 즉시 resize(예: 224x224)하고, 큰 numpy array는 GPU로 옮긴 뒤 CPU에서 즉시 free 하세요.

## 운영 체크리스트

- [ ] 비디오 길이와 질문 유형에 맞는 sampling rate를 실험으로 정했는가
- [ ] scene change, action window, uniform sampling 경로를 구분했는가
- [ ] codec·container 의존성을 포함한 디코딩 실패 경로를 테스트했는가
- [ ] 오디오 트랙을 별도 특징으로 사용할지 명시적으로 결정했는가
- [ ] 프레임 버퍼 메모리와 배치 크기 상한을 운영 기준으로 문서화했는가

## 정리

비디오 이해는 이미지 이해의 단순 확장이 아닙니다. 시간 축이 추가되면서 어떤 순간을 남길지, 어떤 순서를 유지할지가 핵심 문제가 됩니다.

따라서 좋은 video pipeline은 먼저 sampling과 keyframe 정책을 세우고, 그 위에 encoder나 VLM을 얹습니다. 이 순서가 뒤집히면 비용만 커지고 중요한 이벤트를 놓치기 쉽습니다.

오늘의 관점은 production 멀티모달 앱으로 바로 이어집니다. 실제 서비스는 결국 모든 modality를 적절히 샘플링하고 조합하는 운영 시스템이기 때문입니다.

## 처음 질문으로 돌아가기

- **왜 비디오 이해에서 frame sampling이 가장 먼저 결정해야 할 핵심 변수일까요?**
  - 본문의 기준은 Video 이해 - Frame Sampling에서 Video-LLaVA까지를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **PyAV와 scene change 기반 keyframe extraction은 각각 어떤 장면에서 유용할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **VideoMAE, TimeSformer, X-CLIP 같은 video encoder는 어떤 trade-off를 보여 줄까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Multimodal AI 101 (1/10): Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Multimodal AI 101 (2/10): Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- [Multimodal AI 101 (3/10): Vision-Language Model 아키텍처](./03-vlm-architecture.md)
- [Multimodal AI 101 (4/10): Image Captioning과 OCR 파이프라인](./04-captioning-ocr-pipelines.md)
- [Multimodal AI 101 (5/10): Multimodal RAG: 이미지와 텍스트를 함께 검색하기](./05-multimodal-rag.md)
- [Multimodal AI 101 (6/10): 오디오 처리와 Whisper STT](./06-audio-whisper.md)
- [Multimodal AI 101 (7/10): Diffusion으로 Text-to-Image 생성](./07-text-to-image-diffusion.md)
- [Multimodal AI 101 (8/10): Multimodal Embedding과 Cross-modal 검색](./08-multimodal-embeddings.md)
- **Video 이해 - Frame Sampling에서 Video-LLaVA까지 (현재 글)**
- Production Multimodal Application 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Tong et al. - VideoMAE: Masked Autoencoders Are Data-Efficient Learners for Video](https://arxiv.org/abs/2203.12602)
- [Bertasius et al. - Is Space-Time Attention All You Need for Video Understanding? (TimeSformer)](https://arxiv.org/abs/2102.05095)
- [Lin et al. - Video-LLaVA: Learning United Visual Representation by Alignment Before Projection](https://arxiv.org/abs/2311.10122)
- [PyAV Documentation - Decoding Video Streams](https://pyav.org/docs/stable/cookbook/basics.html)

### 관련 시리즈

- [AI 앱 패턴 101 - 워크플로 자동화](../../ai-app-patterns-101/ko/05-workflow-automation.md)
- [LangGraph 101 - 조건부 엣지와 분기 흐름](../../langgraph-101/ko/03-conditional-edges.md)
- [AI Agent 101 - 운영](../../ai-agent-101/ko/09-production-operations.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/09-video-understanding)

Tags: Video Understanding, Video-LLaVA, Frame Sampling, Temporal Modeling, VideoMAE, Action Recognition
