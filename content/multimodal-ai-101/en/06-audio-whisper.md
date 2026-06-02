---
title: "Multimodal AI 101 (6/10): Audio Processing and Whisper STT"
series: multimodal-ai-101
episode: 6
language: en
status: content-ready
targets:
  tistory: false
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

# Multimodal AI 101 (6/10): Audio Processing and Whisper STT

This is the 6th post in the Multimodal AI 101 series.

> Multimodal AI 101 series (6/10)


![Multimodal AI 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/06/06-01-big-picture.en.png)
*Multimodal AI 101 chapter 6 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Audio Processing and Whisper STT?
- Which signal should the example or diagram make visible for Audio Processing and Whisper STT?
- What failure should be prevented first when Audio Processing and Whisper STT reaches a real system?

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

## Managing Whisper Quality with Numbers

Once Whisper is in production, saying "it mostly works" is nearly meaningless. You need to record at minimum WER (Word Error Rate), CER (Character Error Rate), segment latency, and silence-hallucination rate simultaneously to interpret quality trends. If your service handles both Korean call-center audio and English meeting transcripts, separating metrics by language is also mandatory.

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

In domain-heavy environments, `initial_prompt` alone has limits. Adding dictionary-based post-correction is more practical—keeping a lookup table for medical terms, product SKUs, and person names, then correcting in post-processing, can meaningfully reduce WER.

## Audio-Video Combined Pipeline

For meetings and lectures, bundling audio transcription with frame extraction during storage dramatically improves downstream Q&A quality. Extracting frames at Whisper segment timestamps and indexing them together lets you instantly recover "the screen shown when this was said."

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

Connecting this structure to episode 9's video processing means audio and visual data live on the same event timeline rather than separate logs. The combined index is reusable in multimodal RAG as well.

## API Route Selection Criteria

More teams now operate OpenAI API, self-hosted faster-whisper, and hybrid routing together. Sending long files to self-hosted and short real-time requests to the API enables cost optimization.

```python
def choose_stt_route(duration_sec: float, queue_depth: int) -> str:
    if duration_sec > 600:
        return "self_hosted"
    if queue_depth > 120:
        return "openai_api"
    return "self_hosted"
```

This routing function looks simple but becomes the key lever controlling both monthly cost and P95 latency simultaneously.

## Practical Points When Combining Speaker Diarization

Whisper itself does not distinguish speakers, so meeting minutes and consultation logs need diarization attached separately. The most common issue is timestamp alignment error. When diarization segments and Whisper segments diverge at boundaries, sentences get attributed to the wrong speaker.

```python
def assign_speaker(seg_start: float, seg_end: float, speaker_turns: list[dict]) -> str:
    center = (seg_start + seg_end) / 2
    for t in speaker_turns:
        if t["start"] <= center <= t["end"]:
            return t["speaker"]
    return "UNKNOWN"
```

To improve alignment quality, avoid merging segments too long—keep them in the 3–8 second range. Also manage name mapping in a separate post-processing step to minimize conflicts with privacy policies.

## Long Call Log Operations: Segment Merging and Search Indexing

For long audio like call-center recordings or meeting transcripts, storing raw transcription as a single text blob causes search quality to degrade quickly. Typically, merging 20–40 second segments by semantic unit and storing start/end times as metadata per merged chunk is effective.

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

Chunks stored this way are directly reusable in multimodal RAG later. When answering questions, you can present the original audio segment and video frame from that time range together, increasing explainability.

## Audio Pre-Normalization for Transcription Quality

Volume normalization and silence removal in audio preprocessing alone often stabilizes Whisper quality. The effect is especially large in environments with high input quality variance, like mobile recordings.

```python
import librosa
import numpy as np


def normalize_audio(path: str):
    y, sr = librosa.load(path, sr=16000, mono=True)
    y = y / (np.max(np.abs(y)) + 1e-8)
    return y, sr
```

Keeping preprocessing logs enables joint analysis of original input characteristics and transcription errors when quality issues arise.

## Operational Review Loop: Fixing Weekly Checkpoints

Multimodal systems that judge health solely by model accuracy react too late. Fixing a set of items reviewed in every weekly operations meeting is more effective. For example, recording request volume, average latency, P95 latency, error rate, retry rate, cache hit rate, and user complaint rate in the same format catches small anomalies early.

Metrics should also be decomposed by stage. A single "success rate" number obscures which step is losing. Recording success rates separately for input validation, preprocessing, retrieval, and generation stages makes the bottleneck obvious. These decomposed metrics are especially useful for detecting regressions after model swaps or pipeline changes.

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

Fixing the operational loop also makes technology choices more grounded. When introducing a new model, you compare latency increase and cost increase on the same table instead of looking only at "accuracy improvement." Ultimately, production quality is maintained not by a single model upgrade but by a repeatable review loop.

Additionally, in audio pipelines you must monitor processing queue depth alongside transcription quality. Even with good accuracy, severe queue buildup quickly degrades user experience—making it essential to view quality metrics and operational metrics on the same dashboard.


## Answering the Opening Questions

- **Why has Whisper become the de facto default for open-source STT?**
  - It handles 99 languages in one model, is open-weight for self-hosting, and achieves Korean WER competitive with cloud APIs. As the article's comparison showed, accelerating with `faster-whisper` brings per-minute cost and throughput to realistic levels, making it adoptable as a base STT layer even for small teams.
- **How does Whisper's architecture convert 30 seconds of audio into text and timestamps?**
  - Whisper converts 30s audio to an 80-channel log-Mel spectrogram, then an encoder-decoder transformer generates transcription alongside task tokens like `<|transcribe|>` and `<|ko|>`. The `word_timestamps=True` option or segment output attaches start/end times, enabling SRT subtitles, search indexes, and diarization alignment on the same time axis.
- **When are local inference, faster-whisper, and OpenAI API calls each advantageous?**
  - Base `openai-whisper` is good for structure understanding and experimentation. In production, `faster-whisper` with `vad_filter=True` is most practical for throughput and cost. When infrastructure burden is high or requests are short, the OpenAI API path (`client.audio.transcriptions.create(...)`) offers a fast start—and splitting routes by length and queue depth (as in `choose_stt_route()`) is also valid.
<!-- toc:begin -->
## In this series

- [Multimodal AI 101 (1/10): Why Multimodal AI Matters](./01-why-multimodal-matters.md)
- [Multimodal AI 101 (2/10): Image Encoders: CLIP and ViT](./02-image-encoders-clip-vit.md)
- [Multimodal AI 101 (3/10): Vision-Language Model Architecture](./03-vlm-architecture.md)
- [Multimodal AI 101 (4/10): Image Captioning and OCR Pipelines](./04-captioning-ocr-pipelines.md)
- [Multimodal AI 101 (5/10): Multimodal RAG: Searching Images and Text Together](./05-multimodal-rag.md)
- **Audio Processing and Whisper STT (current)**
- Text-to-Image with Diffusion (upcoming)
- Multimodal Embeddings and Cross-modal Search (upcoming)
- Video Understanding - From Frame Sampling to Video-LLaVA (upcoming)
- Building a Production Multimodal Application (upcoming)

<!-- toc:end -->

## References

- [Radford et al. - Robust Speech Recognition via Large-Scale Weak Supervision (Whisper)](https://arxiv.org/abs/2212.04356)
- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [OpenAI Whisper API Reference](https://platform.openai.com/docs/api-reference/audio)
- [silero-vad Documentation](https://github.com/snakers4/silero-vad)

Tags: Whisper, STT, Speech Recognition, Audio Processing, OpenAI, faster-whisper
