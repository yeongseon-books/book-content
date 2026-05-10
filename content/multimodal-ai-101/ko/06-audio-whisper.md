---
title: 오디오 처리와 Whisper STT
series: multimodal-ai-101
episode: 6
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Whisper
- STT
- Speech Recognition
- Audio Processing
- OpenAI
- faster-whisper
last_reviewed: '2026-05-03'
seo_description: OpenAI Whisper가 2022년 9월 공개되기 전까지, production STT는 Google Speech,
  AWS…
---

# 오디오 처리와 Whisper STT

> Multimodal AI 101 시리즈 (6/10)

---

## 왜 Whisper가 STT의 default가 됐나

OpenAI Whisper가 2022년 9월 공개되기 전까지, production STT는 Google Speech, AWS Transcribe, Azure Speech 같은 cloud API가 사실상 기본값이었습니다. 한국어 정확도가 영어보다 한참 떨어지고, 비용도 분당 0.024 USD 수준이었습니다.

Whisper는 두 가지를 동시에 해결했습니다. 99개 언어를 동일 모델로 처리하고, open weight로 self-hosting이 가능합니다. 한국어 WER(Word Error Rate)이 5~8% 수준으로 cloud API와 대등하거나 더 낫고, faster-whisper로 self-host하면 단가가 실시간 1배속 기준 GPU 비용 수준으로 떨어집니다.

이번 편은 Whisper를 production STT로 쓰는 데 필요한 핵심을 다룹니다.

## Whisper 아키텍처 한눈에

```
[audio waveform] -> log-Mel spectrogram (80 channels)
                          |
                          v
                  Encoder (Transformer)
                          |
                          v
                  Decoder (Transformer)  <- text tokens (task tokens 포함)
                          |
                          v
                     transcription
```

핵심 트릭은 task token입니다. decoder 입력에 `<|transcribe|>` 또는 `<|translate|>`, `<|ko|>` 같은 special token을 넣어서 한 모델이 transcription, translation, language detection을 모두 수행합니다.

## 첫 호출: openai-whisper로 30초 만에

```python
import whisper

model = whisper.load_model("small")  # tiny / base / small / medium / large-v3
result = model.transcribe("samples/meeting.m4a", language="ko")
print(result["text"])
for seg in result["segments"][:3]:
    print(f"[{seg['start']:.1f}-{seg['end']:.1f}] {seg['text']}")
```

`language` 파라미터를 명시하면 language detection 단계를 건너뛰어 약간 빨라집니다. 모델 크기는 tiny(39M) ~ large-v3(1.55B)까지 6단계입니다. production에서 default는 `medium` 또는 `large-v3`입니다.

## production에서는 faster-whisper

기본 openai-whisper 구현은 PyTorch 기반이라 throughput이 낮습니다. CTranslate2로 재작성된 `faster-whisper`는 같은 모델을 4~5배 빠르게 돌립니다.

```python
from faster_whisper import WhisperModel

model = WhisperModel(
    "large-v3",
    device="cuda",
    compute_type="float16",  # int8_float16 / int8도 가능
)

segments, info = model.transcribe(
    "samples/meeting.m4a",
    language="ko",
    beam_size=5,
    vad_filter=True,
    vad_parameters={"min_silence_duration_ms": 500},
)

print(f"감지된 언어: {info.language} (확률 {info.language_probability:.2f})")
for seg in segments:
    print(f"[{seg.start:.1f}-{seg.end:.1f}] {seg.text}")
```

`vad_filter=True`가 핵심입니다. silero-VAD로 무음 구간을 자동으로 잘라 hallucination(긴 무음 구간에서 자기 회귀로 환각이 나는 현상)을 막습니다.

## 긴 오디오: 30초 chunking과 timestamping

Whisper encoder는 30초 단위로 동작합니다. 1시간짜리 회의 녹음은 그대로 못 넣습니다. faster-whisper는 내부에서 chunking을 자동 처리하지만, 정확한 word-level timestamp가 필요하면 별도 옵션이 필요합니다.

```python
segments, info = model.transcribe(
    "samples/lecture.mp3",
    language="ko",
    word_timestamps=True,
)

for seg in segments:
    for w in seg.words:
        print(f"[{w.start:.2f}-{w.end:.2f}] {w.word}")
```

word-level timestamp는 자막 SRT 생성, 화자 분리(speaker diarization), 검색 가능한 transcript에 필수입니다.

## SRT 자막 생성

```python
def to_srt(segments) -> str:
    def fmt(t: float) -> str:
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        ms = int((t - int(t)) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    lines = []
    for i, seg in enumerate(segments, 1):
        lines.append(str(i))
        lines.append(f"{fmt(seg.start)} --> {fmt(seg.end)}")
        lines.append(seg.text.strip())
        lines.append("")
    return "\n".join(lines)

with open("output.srt", "w", encoding="utf-8") as f:
    f.write(to_srt(segments))
```

VLM과 함께 쓰면 강력합니다. 영상에서 frame을 추출(9편) + audio를 transcribe해서 multimodal context로 LLM에 함께 넘기는 구조입니다.

## 실시간 streaming

batch transcription과 달리 streaming은 latency가 핵심입니다. faster-whisper에는 streaming 직접 지원이 없지만, `whisper-streaming` 같은 wrapper가 있습니다. 또는 audio를 작은 chunk(1~2초)로 잘라 순차 처리하고, 일정 길이마다 partial result를 emit하는 패턴을 자체 구현합니다.

```python
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cuda", compute_type="float16")
SR = 16000  # Whisper 표준 sample rate
buffer = np.zeros(0, dtype=np.float32)

def callback(indata, frames, time_, status):
    global buffer
    buffer = np.concatenate([buffer, indata[:, 0]])
    if len(buffer) >= SR * 5:  # 5초마다 transcribe
        segs, _ = model.transcribe(buffer, language="ko")
        text = " ".join(s.text for s in segs)
        print("[partial]", text)
        # sliding window: 마지막 1초만 남기고 폐기
        buffer = buffer[-SR:]

with sd.InputStream(callback=callback, channels=1, samplerate=SR):
    sd.sleep(60_000)
```

production 미팅 transcript이라면 OpenAI Realtime API나 AssemblyAI Streaming처럼 streaming 전용 API를 쓰는 게 보통 더 안정적입니다.

## OpenAI API로 호출하기

self-host가 부담스러우면 OpenAI Whisper API가 제일 빠른 시작점입니다.

```python
from openai import OpenAI

client = OpenAI()

with open("samples/meeting.m4a", "rb") as f:
    resp = client.audio.transcriptions.create(
        model="whisper-1",
        file=f,
        language="ko",
        response_format="verbose_json",
        timestamp_granularities=["segment"],
    )

for seg in resp.segments:
    print(f"[{seg.start:.1f}] {seg.text}")
```

분당 약 0.006 USD입니다. 월 1만 분 이상 처리한다면 self-host가 cost 우위에 들어갑니다.

## 흔히 놓치는 함정 다섯 가지

### 1. sample rate 변환 누락

Whisper는 16kHz mono입니다. 44.1kHz stereo wav를 그대로 넣으면 ffmpeg가 자동 변환을 해주지만, 직접 numpy waveform을 만들 때는 명시적으로 resample해야 합니다.

```python
import librosa
audio, _ = librosa.load("samples/in.wav", sr=16000, mono=True)
```

### 2. silence hallucination

10초 이상 무음 구간이 있으면 Whisper가 "감사합니다", "구독과 좋아요" 같은 환각 텍스트를 만듭니다. `vad_filter=True`나 silero-VAD 전처리로 무음을 잘라야 합니다.

### 3. 사투리·전문 용어에 약함

Whisper는 표준어와 일반 vocabulary에 강합니다. 의료, 법률, 사투리는 정확도가 떨어집니다. `initial_prompt`에 도메인 용어 예시를 넣으면 5~10% 개선됩니다.

```python
segments, _ = model.transcribe(
    "samples/medical.m4a",
    language="ko",
    initial_prompt="환자, 처방, 진단, 약물 상호작용, 부작용.",
)
```

### 4. 화자 분리(diarization)가 안 들어있음

Whisper는 누가 말했는지 구분 못 합니다. pyannote-audio나 NeMo speaker diarization을 별도로 돌려서 timestamp를 align해야 회의록 같은 작업이 가능합니다.

### 5. 비용 모니터링 누락

self-host도 GPU instance 비용이 시간당 1~3 USD입니다. queue length, GPU utilization, transcription latency를 cloudwatch나 prometheus에 같이 올려야 cost가 어디서 새는지 보입니다.

## 핵심 요약

- Whisper는 99개 언어를 한 모델로 처리하는 STT default입니다. 한국어 WER 5~8%로 cloud API 수준입니다.
- production에서는 openai-whisper 대신 faster-whisper(CTranslate2 기반, 4~5배 빠름)를 씁니다.
- VAD filter, word-level timestamp, initial_prompt 옵션이 정확도와 안정성에 핵심입니다.
- 긴 오디오는 자동 chunking, 자막 생성은 SRT 변환, 실시간은 sliding window streaming 패턴을 씁니다.
- sample rate 변환, silence hallucination, 도메인 용어 prompt, diarization 분리, cost 모니터링은 production 도입 전에 점검합니다.

---

<!-- toc:begin -->
## Multimodal AI 101 시리즈

- [Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- [Vision-Language Model 아키텍처](./03-vlm-architecture.md)
- [Image Captioning과 OCR 파이프라인](./04-captioning-ocr-pipelines.md)
- [Multimodal RAG: 이미지와 텍스트를 함께 검색하기](./05-multimodal-rag.md)
- **오디오 처리와 Whisper STT (현재 글)**
- Diffusion으로 텍스트에서 이미지 생성 (예정)
- Multimodal Embedding과 cross-modal 검색 (예정)
- Video 이해 (Frame Sampling에서 Video-LLaVA까지) (예정)
- Production Multimodal Application 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Radford et al. - Robust Speech Recognition via Large-Scale Weak Supervision (Whisper)](https://arxiv.org/abs/2212.04356)
- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [OpenAI Whisper API Reference](https://platform.openai.com/docs/api-reference/audio)
- [silero-vad Documentation](https://github.com/snakers4/silero-vad)

Tags: Whisper, STT, Speech Recognition, Audio Processing, OpenAI, faster-whisper
