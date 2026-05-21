---
title: "Multimodal AI 101 (6/10): 오디오 처리와 Whisper STT"
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
last_reviewed: '2026-05-14'
seo_description: OpenAI Whisper가 2022년 9월 공개되기 전까지, production STT는 Google Speech,
  AWS…
---

# Multimodal AI 101 (6/10): 오디오 처리와 Whisper STT

음성 처리는 한동안 “나중에 붙이는 기능”으로 취급됐습니다. 텍스트 챗봇이 먼저 성공하고, 그다음에 STT를 덧붙이는 식이었습니다. 그런데 실제 제품에서는 오히려 음성이 먼저 들어오는 경우가 많습니다. 회의 녹음, 고객센터 통화, 현장 음성 메모, 모바일 보이스 입력처럼 사용자는 이미 텍스트보다 오디오를 더 자연스럽게 보내고 있습니다.

Whisper가 주목받는 이유도 여기에 있습니다. 이전 세대 STT 파이프라인은 언어별 튜닝과 도메인별 사전 작업이 많았지만, Whisper는 비교적 일관된 품질과 폭넓은 언어 지원 덕분에 기본 선택지로 자리 잡았습니다. 덕분에 소규모 팀도 음성 입력을 꽤 빠르게 제품에 넣을 수 있게 됐습니다.

하지만 production으로 가면 문제는 달라집니다. sample rate, chunking, timestamp, latency, diarization, 비용 계측이 모두 별도 설계 포인트가 됩니다. 단순히 “잘 받아 적는다”만 보면 부족하고, 긴 오디오와 실시간 스트림을 어떤 운영 정책으로 다룰지까지 봐야 합니다.

이 글에서는 Whisper를 단순한 STT 모델이 아니라, 음성을 텍스트 파이프라인으로 안정적으로 연결하는 입구 계층으로 정리합니다.

이 글은 Multimodal AI 101 시리즈의 6번째 글입니다.

음성 입력은 모델 정확도만으로 끝나지 않고, 길이와 지연 시간에 맞춘 운영 설계까지 함께 요구합니다.


![Multimodal AI 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/06/06-01-big-picture.ko.png)
*Multimodal AI 101 6장 흐름 개요*
> 오디오 처리와 Whisper STT의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 왜 Whisper가 오픈소스 STT의 사실상 기본값처럼 자리 잡았을까요?
- Whisper 아키텍처는 어떤 방식으로 30초 오디오를 텍스트와 timestamp로 바꿀까요?
- 로컬 추론, faster-whisper, OpenAI API 호출은 각각 어떤 상황에서 유리할까요?

## 왜 이 글이 중요한가

음성은 멀티모달 제품에서 가장 빠르게 사용량이 커지는 입력입니다. 사용자는 말하는 편이 타이핑보다 빠르고, 기업 데이터도 콜센터·회의·현장 녹취처럼 음성 형태로 쌓이는 경우가 많기 때문입니다.

Whisper를 이해하면 음성을 텍스트 중심 시스템에 연결하는 비용이 크게 낮아집니다. 잘 설계된 STT 계층은 이후 요약, 검색, QA, agent workflow에 모두 재사용됩니다.

반대로 초반에 운영 기준을 놓치면 품질보다 더 먼저 비용과 지연이 문제 됩니다. 오디오 길이, 스트리밍 방식, timestamp 요구사항을 미리 고정해 두는 이유가 여기에 있습니다.

## 핵심 관점

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

```text
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
        # 슬라이딩 윈도우: 최근 1초만 유지
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
## Whisper 품질을 숫자로 관리하는 방법

Whisper를 운영에 붙이면 "대체로 잘 된다"는 표현은 거의 의미가 없습니다. 최소한 WER(Word Error Rate), CER(Character Error Rate), segment latency, 무음 구간 hallucination 비율을 동시에 기록해야 품질 추이를 해석할 수 있습니다. 한국어 콜센터와 영어 회의록을 함께 처리하는 서비스라면 언어별 지표를 분리하는 것도 필수입니다.

```python
def wer(ref: list[str], hyp: list[str]) -> float:
    n, m = len(ref), len(hyp)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost,
            )
    return dp[n][m] / max(1, n)
```

도메인 용어가 많은 환경에서는 `initial_prompt`만으로 한계가 있습니다. 이때는 사전 기반 치환(post-correction)을 추가하는 편이 현실적입니다. 예를 들어 의학 용어, 제품 SKU, 사람 이름을 사전으로 두고 후처리에서 교정하면 WER가 유의미하게 내려갑니다.

## 오디오-비디오 결합 파이프라인

회의나 강의 영상에서는 오디오 전사와 프레임 추출을 묶어 저장하면 나중에 질의응답 품질이 크게 좋아집니다. Whisper segment timestamp를 기준으로 해당 시간대 프레임을 추출해 함께 인덱싱하면 "이 말이 나온 화면"을 바로 복원할 수 있습니다.

```python
import subprocess

def extract_frame_at(video_path: str, sec: float, out_path: str) -> None:
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", f"{sec:.3f}",
        "-i", video_path,
        "-frames:v", "1",
        out_path,
    ], check=True)
```

이 구조를 9편의 비디오 처리와 연결하면, 음성과 화면이 분리된 로그가 아니라 같은 이벤트 타임라인으로 관리됩니다. 멀티모달 RAG에서도 이 결합 인덱스가 재사용됩니다.

## API 경로 선택 기준

OpenAI API, self-hosted faster-whisper, 하이브리드 라우팅을 함께 운영하는 팀이 늘고 있습니다. 긴 파일은 self-host로, 짧은 실시간 요청은 API로 보내는 식의 비용 최적화가 가능합니다.

```python
def choose_stt_route(duration_sec: float, queue_depth: int) -> str:
    if duration_sec > 600:
        return "self_hosted"
    if queue_depth > 120:
        return "openai_api"
    return "self_hosted"
```

이 라우팅 함수는 단순해 보이지만, 월 단위 비용과 P95 latency를 동시에 제어하는 핵심 장치가 됩니다.

## 화자 분리와 결합할 때의 실무 포인트

Whisper 자체는 화자를 구분하지 않기 때문에 회의록이나 상담 로그에서는 diarization을 별도로 붙여야 합니다. 이때 가장 많이 생기는 문제는 시간축 정렬 오차입니다. diarization 구간과 Whisper segment의 경계가 어긋나면 문장이 잘못된 화자에게 붙는 현상이 생깁니다.

```python
def assign_speaker(seg_start: float, seg_end: float, speaker_turns: list[dict]) -> str:
    center = (seg_start + seg_end) / 2
    for t in speaker_turns:
        if t["start"] <= center <= t["end"]:
            return t["speaker"]
    return "UNKNOWN"
```

정렬 품질을 올리려면 segment를 너무 길게 묶지 말고, 3~8초 단위로 유지하는 편이 좋습니다. 또한 이름 매핑은 후처리 단계에서 별도로 관리해야 개인정보 정책과 충돌을 줄일 수 있습니다.

## 긴 통화 로그 운영: 구간 병합과 검색 인덱싱

콜센터나 회의록 같은 긴 오디오에서는 전사 결과를 그대로 한 덩어리 텍스트로 저장하면 검색 품질이 빠르게 떨어집니다. 보통 20~40초 단위 segment를 의미 단위로 병합하고, 병합 구간마다 시작/종료 시간을 메타데이터로 저장하는 방식이 효과적입니다.

```python
def merge_segments(segments: list[dict], max_window: float = 35.0) -> list[dict]:
    merged = []
    cur = None
    for s in segments:
        if cur is None:
            cur = {"start": s["start"], "end": s["end"], "text": s["text"]}
            continue
        if s["end"] - cur["start"] <= max_window:
            cur["end"] = s["end"]
            cur["text"] += " " + s["text"]
        else:
            merged.append(cur)
            cur = {"start": s["start"], "end": s["end"], "text": s["text"]}
    if cur:
        merged.append(cur)
    return merged
```

이렇게 저장한 구간은 나중에 멀티모달 RAG에서 바로 재사용됩니다. 질문에 대한 답변을 줄 때 해당 시간대 오디오 원본과 비디오 프레임을 함께 제시할 수 있어 설명 가능성이 높아집니다.

## 전사 품질 개선을 위한 사전 정규화

오디오 전처리에서 볼륨 정규화와 무음 제거만 잘해도 Whisper 품질이 안정되는 경우가 많습니다. 특히 모바일 녹음처럼 입력 품질 편차가 큰 환경에서 효과가 큽니다.

```python
import librosa
import numpy as np

def normalize_audio(path: str):
    y, sr = librosa.load(path, sr=16000, mono=True)
    y = y / (np.max(np.abs(y)) + 1e-8)
    return y, sr
```

전처리 로그를 남겨 두면 품질 이슈가 발생했을 때 원본 입력 특성과 전사 오류를 함께 분석할 수 있습니다.

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

추가로, 음성 파이프라인에서는 전사 품질과 함께 처리 대기열 길이를 동시에 감시해야 합니다. 정확도만 좋아도 큐 적체가 심하면 사용자 경험은 빠르게 악화되므로, 품질 지표와 운영 지표를 한 대시보드에서 함께 보는 습관이 중요합니다.

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

Whisper는 음성을 텍스트 파이프라인으로 연결하는 가장 실용적인 출발점입니다. 여러 언어를 폭넓게 지원하고 성능도 비교적 안정적이라서, 소규모 팀도 빠르게 음성 기능을 붙일 수 있습니다.

하지만 production 설계의 핵심은 모델 호출보다 chunking, timestamp, latency, 비용 관리에 있습니다. 이 운영 요소를 먼저 정해야 음성 기능이 실제 서비스에서 버팁니다.

이 글의 코드를 그대로 실행해 보는 것보다 더 중요한 것은, 음성 데이터를 어떤 시간 단위의 텍스트 자산으로 만들 것인지 결정하는 감각을 가져가는 일입니다.

## 처음 질문으로 돌아가기

- **왜 Whisper가 오픈소스 STT의 사실상 기본값처럼 자리 잡았을까요?**
  - 본문의 기준은 오디오 처리와 Whisper STT를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Whisper 아키텍처는 어떤 방식으로 30초 오디오를 텍스트와 timestamp로 바꿀까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **로컬 추론, faster-whisper, OpenAI API 호출은 각각 어떤 상황에서 유리할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Multimodal AI 101 (1/10): Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Multimodal AI 101 (2/10): Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- [Multimodal AI 101 (3/10): Vision-Language Model 아키텍처](./03-vlm-architecture.md)
- [Multimodal AI 101 (4/10): Image Captioning과 OCR 파이프라인](./04-captioning-ocr-pipelines.md)
- [Multimodal AI 101 (5/10): Multimodal RAG: 이미지와 텍스트를 함께 검색하기](./05-multimodal-rag.md)
- **오디오 처리와 Whisper STT (현재 글)**
- Diffusion으로 Text-to-Image 생성 (예정)
- Multimodal Embedding과 Cross-modal 검색 (예정)
- Video 이해 - Frame Sampling에서 Video-LLaVA까지 (예정)
- Production Multimodal Application 구축 (예정)

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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/06-audio-whisper)

Tags: Whisper, STT, Speech Recognition, Audio Processing, OpenAI, faster-whisper
