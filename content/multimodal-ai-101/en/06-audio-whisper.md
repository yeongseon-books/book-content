---
title: Audio Processing and Whisper STT
series: multimodal-ai-101
episode: 6
language: en
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
seo_description: Before OpenAI Whisper landed in September 2022, production STT meant
  Google Speech, AWS Transcribe, or Azure Speech.
---

# Audio Processing and Whisper STT

This is post 6 in the Multimodal AI 101 series.

> Multimodal AI 101 series (6/10)

---

## Why Whisper became the STT default

Before OpenAI Whisper landed in September 2022, production STT meant Google Speech, AWS Transcribe, or Azure Speech. Non-English accuracy lagged English by a wide margin and pricing sat around USD 0.024 per minute.

Whisper solved two problems at once: 99 languages from a single model, and open weights so you can self-host. Korean WER lands around 5-8%, on par with or better than cloud APIs, and self-hosting with faster-whisper drops the unit cost to roughly the GPU cost at 1x realtime.

This episode covers what you actually need to run Whisper in production STT.

## Whisper architecture at a glance

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

The trick is the task token. Special tokens like `<|transcribe|>`, `<|translate|>`, or `<|ko|>` go into the decoder input so one model handles transcription, translation, and language detection.

## First call: 30 seconds with openai-whisper

```python
import whisper

model = whisper.load_model("small")  # tiny / base / small / medium / large-v3
result = model.transcribe("samples/meeting.m4a", language="en")
print(result["text"])
for seg in result["segments"][:3]:
    print(f"[{seg['start']:.1f}-{seg['end']:.1f}] {seg['text']}")
```

Specifying `language` skips language detection and runs slightly faster. Six size tiers exist from tiny (39M) to large-v3 (1.55B). Production defaults are `medium` or `large-v3`.

## In production: faster-whisper

The reference openai-whisper implementation is PyTorch-based with low throughput. `faster-whisper`, rewritten on CTranslate2, runs the same model 4-5x faster.

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

`vad_filter=True` is the key. silero-VAD trims silence automatically and prevents the hallucination that happens when long silent stretches feed back into the autoregressive decoder.

## Long audio: 30-second chunking and timestamps

Whisper's encoder processes 30-second windows. A one-hour meeting recording cannot be fed in directly. faster-whisper handles chunking internally, but accurate word-level timestamps need a separate option.

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

Word-level timestamps are essential for SRT subtitles, speaker diarization, and searchable transcripts.

## Generating SRT subtitles

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

This composes powerfully with VLMs: extract frames from video (Episode 9) plus transcribe audio, then hand both to an LLM as multimodal context.

## Realtime streaming

Streaming is latency-driven, unlike batch transcription. faster-whisper has no first-class streaming, but wrappers like `whisper-streaming` exist. Alternatively, slice audio into small chunks (1-2 seconds), process sequentially, and emit a partial result every few seconds.

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

For production meeting transcripts, dedicated streaming APIs like OpenAI Realtime or AssemblyAI Streaming are usually more reliable.

## Calling the OpenAI API

If self-hosting is too much, the OpenAI Whisper API is the fastest start.

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

About USD 0.006 per minute. Past 10K minutes per month, self-hosting wins on cost.

## Five common pitfalls

### 1. Skipping sample-rate conversion

Whisper expects 16 kHz mono. Feeding 44.1 kHz stereo wav works through file paths because ffmpeg auto-converts, but when you build numpy waveforms manually you must resample explicitly.

```python
import librosa
audio, _ = librosa.load("samples/in.wav", sr=16000, mono=True)
```

### 2. Silence hallucination

After 10+ seconds of silence, Whisper produces hallucinated text like "Thank you for watching" or "Subscribe and like." Trim silence with `vad_filter=True` or a silero-VAD preprocessor.

### 3. Weak on dialects and domain jargon

Whisper is strong on standard speech and general vocabulary. Medical, legal, and dialect content drops in accuracy. Putting domain terms in `initial_prompt` typically improves accuracy 5-10%.

```python
segments, _ = model.transcribe(
    "samples/medical.m4a",
    language="en",
    initial_prompt="patient, prescription, diagnosis, drug interaction, side effects.",
)
```

### 4. No speaker diarization built in

Whisper does not tell you who spoke. Run pyannote-audio or NeMo speaker diarization separately and align on timestamps if you need meeting-minute-style output.

### 5. Missing cost monitoring

Self-hosting still costs USD 1-3 per hour per GPU instance. Push queue length, GPU utilization, and transcription latency into CloudWatch or Prometheus to see where money leaks.

## Key Takeaways

- Whisper is the STT default with 99-language coverage from a single model. Korean WER lands at 5-8%, on par with cloud APIs.
- In production, use faster-whisper (CTranslate2-based, 4-5x faster) instead of openai-whisper.
- VAD filter, word-level timestamps, and `initial_prompt` are critical for accuracy and stability.
- Long audio uses auto-chunking; subtitles use SRT conversion; realtime uses sliding-window streaming.
- Verify sample-rate conversion, silence hallucination, domain prompts, separate diarization, and cost monitoring before production.

---

<!-- toc:begin -->
## Multimodal AI 101 series

- [Why Multimodal AI Matters](./01-why-multimodal-matters.md)
- [Image Encoders: CLIP and ViT](./02-image-encoders-clip-vit.md)
- [Vision-Language Model Architecture](./03-vlm-architecture.md)
- [Image Captioning and OCR Pipelines](./04-captioning-ocr-pipelines.md)
- [Multimodal RAG: Searching Images and Text Together](./05-multimodal-rag.md)
- **Audio Processing and Whisper STT (current)**
- Text-to-Image with Diffusion (upcoming)
- Multimodal Embeddings and Cross-modal Search (upcoming)
- Video Understanding (Frame Sampling to Video-LLaVA) (upcoming)
- Building a Production Multimodal Application (upcoming)
<!-- toc:end -->

## References

- [Radford et al. - Robust Speech Recognition via Large-Scale Weak Supervision (Whisper)](https://arxiv.org/abs/2212.04356)
- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [OpenAI Whisper API Reference](https://platform.openai.com/docs/api-reference/audio)
- [silero-vad Documentation](https://github.com/snakers4/silero-vad)

Tags: Whisper, STT, Speech Recognition, Audio Processing, OpenAI, faster-whisper
