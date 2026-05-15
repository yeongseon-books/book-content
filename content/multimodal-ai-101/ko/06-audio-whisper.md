---
title: 오디오 처리와 Whisper STT
series: multimodal-ai-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Whisper
- STT
- Speech Recognition
- Audio Processing
- OpenAI
- faster-whisper
last_reviewed: '2026-05-12'
seo_description: OpenAI Whisper가 2022년 9월 공개되기 전까지, production STT는 Google Speech,
  AWS…
---

# 오디오 처리와 Whisper STT

음성 처리는 한동안 “나중에 붙이는 기능”으로 취급됐습니다. 텍스트 챗봇이 먼저 성공하고, 그다음에 STT를 덧붙이는 식이었습니다. 그런데 실제 제품에서는 오히려 음성이 먼저 들어오는 경우가 많습니다. 회의 녹음, 고객센터 통화, 현장 음성 메모, 모바일 보이스 입력처럼 사용자는 이미 텍스트보다 오디오를 더 자연스럽게 보내고 있습니다.

Whisper가 중요한 이유는 여기서 나옵니다. 이전 세대 STT 파이프라인은 언어별 튜닝과 도메인별 사전 작업이 많았지만, Whisper는 상대적으로 일관된 품질과 다국어 지원으로 기본 선택지가 됐습니다. 덕분에 소규모 팀도 음성 입력을 꽤 빠르게 제품에 넣을 수 있게 됐습니다.

하지만 production으로 가면 문제는 달라집니다. sample rate, chunking, timestamp, latency, diarization, 비용 계측이 모두 별도 설계 포인트가 됩니다. 단순히 “잘 받아 적는다”만 보면 부족하고, 긴 오디오와 실시간 스트림을 어떤 운영 정책으로 다룰지까지 봐야 합니다.

이 글에서는 Whisper를 단순한 STT 모델이 아니라, 음성을 텍스트 파이프라인으로 안정적으로 연결하는 입구 계층으로 정리합니다.

이 글은 Multimodal AI 101 시리즈의 6번째 글입니다.

음성 입력은 모델 정확도만으로 끝나지 않고, 길이와 지연 시간에 맞춘 운영 설계까지 함께 요구합니다.

## 이 글에서 다룰 문제

- 왜 Whisper가 오픈소스 STT의 사실상 기본값처럼 자리 잡았을까요?
- Whisper 아키텍처는 어떤 방식으로 30초 오디오를 텍스트와 timestamp로 바꿀까요?
- 로컬 추론, faster-whisper, OpenAI API 호출은 각각 어떤 상황에서 유리할까요?
- 긴 오디오를 chunking하고 SRT 자막으로 만드는 과정에서 무엇을 먼저 설계해야 할까요?
- sample rate, hallucination, diarization, 비용 계측은 어디서 가장 자주 문제를 만들까요?

## 왜 이 글이 중요한가

음성은 멀티모달 제품에서 가장 빠르게 사용량이 커지는 입력입니다. 사용자는 말하는 편이 타이핑보다 빠르고, 기업 데이터도 콜센터·회의·현장 녹취처럼 음성 형태로 쌓이는 경우가 많기 때문입니다.

Whisper를 이해하면 음성을 텍스트 중심 시스템에 연결하는 비용이 크게 낮아집니다. 잘 설계된 STT 계층은 이후 요약, 검색, QA, agent workflow에 모두 재사용됩니다.

반대로 초반에 운영 기준을 놓치면 품질보다 더 먼저 비용과 지연이 문제 됩니다. 오디오 길이, 스트리밍 방식, timestamp 요구사항을 미리 고정해 두는 이유가 여기에 있습니다.

## Whisper를 이해하는 가장 좋은 방법: 음성을 문자로만 바꾸는 도구가 아니라 시간 축이 있는 텍스트 생성기로 보는 것입니다

Whisper가 특별한 이유는 단순히 음성을 받아 적기 때문이 아닙니다. 오디오를 일정 길이로 쪼개고, 그 위에서 언어·내용·시간 정보를 함께 복원하는 구조를 제공하기 때문입니다. 그래서 transcript만 필요한지, segment timestamp가 필요한지, 자막 파일까지 필요한지에 따라 파이프라인 설계가 달라집니다.

이 관점으로 보면 chunking이 왜 중요한지도 분명해집니다. 음성 입력은 텍스트보다 길이와 시간 정보가 핵심 제약입니다. 30초 창을 어떻게 이어 붙일지, 겹침을 둘지, 실시간 스트리밍에서 partial result를 어떻게 다룰지가 품질에 직접 영향을 줍니다.

즉 Whisper를 잘 쓴다는 것은 모델 호출법을 아는 것이 아니라, 시간 축을 가진 텍스트를 어떤 단위로 생성하고 소비할지 결정하는 일에 가깝습니다.

> 좋은 STT 파이프라인은 음성을 단순한 문자열로 끝내지 않습니다. 시간이 붙은 텍스트로 바꿔 두어야 검색·요약·자막·QA가 모두 쉬워집니다.

## 핵심 개념

### 왜 Whisper가 STT의 default가 됐나

OpenAI Whisper가 2022년 9월 공개되기 전까지, production STT는 Google Speech, AWS Transcribe, Azure Speech 같은 cloud API가 사실상 기본값이었습니다. 한국어 정확도가 영어보다 한참 떨어지고, 비용도 분당 0.024 USD 수준이었습니다.

Whisper는 두 가지를 동시에 해결했습니다. 99개 언어를 동일 모델로 처리하고, open weight로 self-hosting이 가능합니다. 한국어 WER(Word Error Rate)이 5~8% 수준으로 cloud API와 대등하거나 더 낫고, faster-whisper로 self-host하면 단가가 실시간 1배속 기준 GPU 비용 수준으로 떨어집니다.

이번 편은 Whisper를 production STT로 쓰는 데 필요한 핵심을 다룹니다.

### Whisper 아키텍처 한눈에

```
[audio waveform] -> log-Mel spectrogram (80 channels)
                          |
                          v
                  Encoder (Transformer)
                          |
                          v
                  Decoder (Transformer)  <- text tokens (incl. task tokens)
                          |
                          v
                     transcription
```

핵심 트릭은 task token입니다. decoder 입력에 `<|transcribe|>` 또는 `<|translate|>`, `<|ko|>` 같은 special token을 넣어서 한 모델이 transcription, translation, language detection을 모두 수행합니다.

### 첫 호출: openai-whisper로 30초 만에

```python
import whisper

model = whisper.load_model("small")  # tiny / base / small / medium / large-v3
result = model.transcribe("samples/meeting.m4a", language="en")
print(result["text"])
for seg in result["segments"][:3]:
    print(f"[{seg['start']:.1f}-{seg['end']:.1f}] {seg['text']}")
```

`language` 파라미터를 명시하면 language detection 단계를 건너뛰어 약간 빨라집니다. 모델 크기는 tiny(39M) ~ large-v3(1.55B)까지 6단계입니다. production에서 default는 `medium` 또는 `large-v3`입니다.

### production에서는 faster-whisper

기본 openai-whisper 구현은 PyTorch 기반이라 throughput이 낮습니다. CTranslate2로 재작성된 `faster-whisper`는 같은 모델을 4~5배 빠르게 돌립니다.

```python
from faster_whisper import WhisperModel

model = WhisperModel(
    "large-v3",
    device="cuda",
    compute_type="float16",  # int8_float16 / int8 also available
)

segments, info = model.transcribe(
    "samples/meeting.m4a",
    language="en",
    beam_size=5,
    vad_filter=True,
    vad_parameters={"min_silence_duration_ms": 500},
)

print(f"Detected language: {info.language} (prob {info.language_probability:.2f})")
for seg in segments:
    print(f"[{seg.start:.1f}-{seg.end:.1f}] {seg.text}")
```

`vad_filter=True`가 핵심입니다. silero-VAD로 무음 구간을 자동으로 잘라 hallucination(긴 무음 구간에서 자기 회귀로 환각이 나는 현상)을 막습니다.

### 긴 오디오: 30초 chunking과 timestamping

Whisper encoder는 30초 단위로 동작합니다. 1시간짜리 회의 녹음은 그대로 못 넣습니다. faster-whisper는 내부에서 chunking을 자동 처리하지만, 정확한 word-level timestamp가 필요하면 별도 옵션이 필요합니다.

```python
segments, info = model.transcribe(
    "samples/lecture.mp3",
    language="en",
    word_timestamps=True,
)

for seg in segments:
    for w in seg.words:
        print(f"[{w.start:.2f}-{w.end:.2f}] {w.word}")
```

word-level timestamp는 자막 SRT 생성, 화자 분리(speaker diarization), 검색 가능한 transcript에 필수입니다.

### SRT 자막 생성

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

### 실시간 streaming

batch transcription과 달리 streaming은 latency가 핵심입니다. faster-whisper에는 streaming 직접 지원이 없지만, `whisper-streaming` 같은 wrapper가 있습니다. 또는 audio를 작은 chunk(1~2초)로 잘라 순차 처리하고, 일정 길이마다 partial result를 emit하는 패턴을 자체 구현합니다.

```python
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cuda", compute_type="float16")
SR = 16000  # Whisper standard sample rate
buffer = np.zeros(0, dtype=np.float32)

def callback(indata, frames, time_, status):
    global buffer
    buffer = np.concatenate([buffer, indata[:, 0]])
    if len(buffer) >= SR * 5:  # transcribe every 5 seconds
        segs, _ = model.transcribe(buffer, language="en")
        text = " ".join(s.text for s in segs)
        print("[partial]", text)
        # sliding window: keep only last 1 second
        buffer = buffer[-SR:]

with sd.InputStream(callback=callback, channels=1, samplerate=SR):
    sd.sleep(60_000)
```

production 미팅 transcript이라면 OpenAI Realtime API나 AssemblyAI Streaming처럼 streaming 전용 API를 쓰는 게 보통 더 안정적입니다.

### OpenAI API로 호출하기

self-host가 부담스러우면 OpenAI Whisper API가 제일 빠른 시작점입니다.

```python
from openai import OpenAI

client = OpenAI()

with open("samples/meeting.m4a", "rb") as f:
    resp = client.audio.transcriptions.create(
        model="whisper-1",
        file=f,
        language="en",
        response_format="verbose_json",
        timestamp_granularities=["segment"],
    )

for seg in resp.segments:
    print(f"[{seg.start:.1f}] {seg.text}")
```

분당 약 0.006 USD입니다. 월 1만 분 이상 처리한다면 self-host가 cost 우위에 들어갑니다.

### 자막·스트리밍·API 연결 예제

배치 전사만으로는 production 요구를 다 충족하기 어렵습니다. 아래 코드는 자막 생성과 실시간 처리, API 호출로 이어지는 보조 예제를 묶어 둔 것입니다.

```python
import librosa
audio, _ = librosa.load("samples/in.wav", sr=16000, mono=True)
```

```python
segments, _ = model.transcribe(
    "samples/medical.m4a",
    language="en",
    initial_prompt="patient, prescription, diagnosis, drug interaction, side effects.",
)
```
## 흔히 헷갈리는 지점

- **sample rate 변환 누락** Whisper는 16kHz mono입니다. 44.1kHz stereo wav를 그대로 넣으면 ffmpeg가 자동 변환을 해주지만, 직접 numpy waveform을 만들 때는 명시적으로 resample해야 합니다.
- **silence hallucination** 10초 이상 무음 구간이 있으면 Whisper가 "감사합니다", "구독과 좋아요" 같은 환각 텍스트를 만듭니다. `vad_filter=True`나 silero-VAD 전처리로 무음을 잘라야 합니다.
- **사투리·전문 용어에 약함** Whisper는 표준어와 일반 vocabulary에 강합니다. 의료, 법률, 사투리는 정확도가 떨어집니다. `initial_prompt`에 도메인 용어 예시를 넣으면 5~10% 개선됩니다.
- **화자 분리(diarization)가 안 들어있음** Whisper는 누가 말했는지 구분 못 합니다. pyannote-audio나 NeMo speaker diarization을 별도로 돌려서 timestamp를 align해야 회의록 같은 작업이 가능합니다.
- **비용 모니터링 누락** self-host도 GPU instance 비용이 시간당 1~3 USD입니다. queue length, GPU utilization, transcription latency를 cloudwatch나 prometheus에 같이 올려야 cost가 어디서 새는지 보입니다.

## 운영 체크리스트

- [ ] 입력 오디오를 목표 sample rate와 채널 수로 표준화하는가
- [ ] 긴 오디오에서 chunk overlap과 timestamp stitching 정책을 정했는가
- [ ] 실시간과 배치 경로를 분리하고 각 경로의 latency 목표를 수치화했는가
- [ ] hallucination과 반복 구간을 감지하는 후처리 규칙을 두었는가
- [ ] 비용 계측 시 분당 오디오 길이와 모델 종류를 함께 기록하는가

## 정리

Whisper는 음성을 텍스트 파이프라인으로 연결하는 가장 실용적인 기본값입니다. 다국어 지원과 비교적 안정적인 성능 덕분에 소규모 팀도 빠르게 음성 기능을 붙일 수 있습니다.

하지만 production 설계의 핵심은 모델 호출보다 chunking, timestamp, latency, 비용 관리에 있습니다. 이 운영 요소를 먼저 정해야 음성 기능이 실제 서비스에서 버팁니다.

이 글의 코드를 그대로 실행해 보는 것보다 더 중요한 것은, 음성 데이터를 어떤 시간 단위의 텍스트 자산으로 만들 것인지 결정하는 감각을 가져가는 일입니다.

<!-- toc:begin -->
## Multimodal AI 101 시리즈

- [Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- [Vision-Language Model 아키텍처](./03-vlm-architecture.md)
- [Image Captioning과 OCR 파이프라인](./04-captioning-ocr-pipelines.md)
- [Multimodal RAG: 이미지와 텍스트를 함께 검색하기](./05-multimodal-rag.md)
- **오디오 처리와 Whisper STT (현재 글)**
- [Diffusion으로 Text-to-Image 생성](./07-text-to-image-diffusion.md)
- [Multimodal Embedding과 Cross-modal 검색](./08-multimodal-embeddings.md)
- [Video 이해 - Frame Sampling에서 Video-LLaVA까지](./09-video-understanding.md)
- [Production Multimodal Application 구축](./10-production-multimodal-app.md)
<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Radford et al. - Robust Speech Recognition via Large-Scale Weak Supervision (Whisper)](https://arxiv.org/abs/2212.04356)
- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [OpenAI Whisper API Reference](https://platform.openai.com/docs/api-reference/audio)
- [silero-vad Documentation](https://github.com/snakers4/silero-vad)

### 관련 시리즈

- [LLM API 프로덕션 101 - 스트리밍 심화](../../llm-api-production-101/ko/03-streaming-in-depth.md)
- [AI 앱 패턴 101 - 워크플로 자동화](../../ai-app-patterns-101/ko/05-workflow-automation.md)
- [LangChain 101 - Streaming](../../langchain-101/ko/05-streaming.md)

Tags: Whisper, STT, Speech Recognition, Audio Processing, OpenAI, faster-whisper
