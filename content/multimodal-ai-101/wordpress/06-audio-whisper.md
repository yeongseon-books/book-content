---
series: multimodal-ai-101
episode: 6
title: "바이브코딩을 위한 멀티모달 AI (6/10): 오디오 처리와 Whisper STT"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 멀티모달 AI
  - Whisper
  - STT
  - Speech Recognition
language: ko
---

# 바이브코딩을 위한 멀티모달 AI (6/10): 오디오 처리와 Whisper STT

> 이 글은 **바이브코딩을 위한 멀티모달 AI** 시리즈 6편입니다. Whisper 아키텍처, 로컬/faster-whisper/API 선택 기준, 긴 오디오 chunking과 timestamp 처리를 다룹니다.

바이브코딩으로 음성 처리 기능을 만들 때 선택지는 세 가지다. OpenAI Whisper API를 호출하거나, faster-whisper로 self-hosting하거나, 클라우드 STT(Google Speech, AWS Transcribe)를 사용하는 것이다. 각 방식은 비용, 지연, 언어 품질, 운영 복잡도가 다르다.

Whisper가 STT의 사실상 기본값이 된 이유는 두 가지다. 99개 언어를 동일 모델로 처리하고, open weight로 self-hosting이 가능하다. 한국어 WER(Word Error Rate)이 5~8% 수준으로 클라우드 API와 대등하거나 더 낫다. faster-whisper로 self-host하면 클라우드 API 대비 비용이 GPU 실행 비용 수준으로 낮아진다.

아키텍처는 30초 오디오 창을 log-mel spectrogram으로 변환하고 encoder에 통과시켜 음향 특징을 추출한다. decoder가 특징을 보고 transcript 토큰을 자기회귀 방식으로 생성하며 timestamp도 함께 출력한다. 30초보다 긴 오디오는 청킹이 필요하다. 청크 경계에서 단어가 잘리지 않도록 overlap을 두는 것이 핵심이다.

운영에서 중요한 설정은 세 가지다. `word_timestamps=True`로 단어 단위 타임스탬프를 얻고, `vad_filter=True`로 침묵 구간을 건너뛰어 비용을 줄이고, language 파라미터를 명시해 자동 감지 오류를 막는다.

> 좋은 STT 파이프라인은 음성을 단순한 문자열로 끝내지 않습니다. 시간이 붙은 텍스트로 바꿔 두어야 검색·요약·자막·QA가 모두 쉬워집니다.

## 이 글에서 다룰 문제

- Whisper는 어떤 구조로 30초 오디오를 텍스트와 timestamp로 변환하나요?
- 로컬 추론, faster-whisper, OpenAI API 호출은 각각 어떤 상황에서 유리한가요?
- 긴 오디오는 어떻게 청킹해야 단어 경계를 보존할 수 있나요?
- timestamp가 없으면 어떤 downstream 기능이 불가능해지나요?
- production에서 Whisper를 안정적으로 운영하기 위한 핵심 설정은 무엇인가요?

## Before / After: Whisper 도입 전후

| 상황 | 클라우드 STT | Whisper |
|------|------------|--------|
| 한국어 품질 | 영어 대비 낮음 | WER 5-8%, 대등 |
| 비용 | 분당 $0.024 (Google) | self-host 시 GPU 비용만 |
| 언어 지원 | 서비스별 제한 | 99개 언어 단일 모델 |
| 타임스탬프 | 별도 설정 필요 | word_timestamps=True로 기본 지원 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| 30초 초과 오디오를 청킹 없이 전송 | 잘림 또는 오류 | 청킹 + overlap 설정 |
| language 파라미터 미지정 | 자동 감지 오류 (한국어→일본어) | language="ko" 명시 |
| 타임스탬프 없이 transcript만 추출 | 검색·자막 불가 | word_timestamps=True 항상 설정 |
| VAD 필터 없이 침묵 구간 처리 | 비용 낭비, 할루시네이션 | vad_filter=True 설정 |

## AI 팁: Whisper 빠르게 시작하는 방법

Claude나 GPT-4에 "Python으로 faster-whisper를 사용해 오디오 파일을 타임스탬프와 함께 전사하는 코드를 만들어줘. 30초 이상 긴 파일도 처리하고 결과를 SRT 자막 형식으로 저장해줘"라고 요청하면 시작할 수 있다. `pip install faster-whisper`로 설치하고, `WhisperModel("large-v3", device="cuda")`로 로드한다. `model.transcribe(audio_path, language="ko", word_timestamps=True, vad_filter=True)`로 실행하고, segment별 start/end 시간을 SRT 형식으로 포맷한다. API를 쓰려면 `openai.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="verbose_json", timestamp_granularities=["word"])`를 사용한다.

## 운영 체크리스트

- [ ] language 파라미터를 명시해 자동 감지 오류를 방지하는가
- [ ] word_timestamps=True로 타임스탬프를 함께 추출하는가
- [ ] vad_filter=True로 침묵 구간을 건너뛰는가
- [ ] 30초 초과 오디오는 overlap이 있는 청킹을 사용하는가
- [ ] sample rate가 16kHz인지 확인하는가 (Whisper 요구사항)

## 처음 질문으로 돌아가기

- **로컬 vs faster-whisper vs API 선택 기준은?** 비용이 최우선이면 faster-whisper self-host. 빠른 시작이 목표면 OpenAI API. 실시간 스트리밍이 필요하면 faster-whisper + streaming 설정.
- **청킹 전략은?** 30초 창에 2-3초 overlap을 두어 단어 경계를 보존한다. ffmpeg로 오디오를 분할하고 결과를 timestamp로 이어 붙인다.
- **타임스탬프가 중요한 이유는?** 자막 생성, 구간 검색, 화자 추적(diarization), QA에서 관련 구간 찾기에 모두 필요하다.

## 정리

Whisper는 99개 언어를 단일 모델로 처리하는 오픈 소스 STT다. faster-whisper로 self-hosting하면 클라우드 대비 비용이 크게 낮아진다. 타임스탬프, VAD 필터, 언어 지정, 청킹 전략을 처음부터 설계하면 downstream 기능(검색, 자막, QA)까지 한번에 지원할 수 있다.

## 참고 자료

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/06-audio-whisper)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 멀티모달 AI (1/10): 멀티모달이 중요한 이유
- 바이브코딩을 위한 멀티모달 AI (2/10): Image Encoder: CLIP과 ViT
- 바이브코딩을 위한 멀티모달 AI (3/10): Vision-Language Model 아키텍처
- 바이브코딩을 위한 멀티모달 AI (4/10): Image Captioning과 OCR 파이프라인
- 바이브코딩을 위한 멀티모달 AI (5/10): Multimodal RAG
- **바이브코딩을 위한 멀티모달 AI (6/10): 오디오 처리와 Whisper STT (현재 글)**
- 바이브코딩을 위한 멀티모달 AI (7/10): Diffusion으로 이미지 생성
- 바이브코딩을 위한 멀티모달 AI (8/10): Multimodal Embedding과 Cross-modal 검색
- 바이브코딩을 위한 멀티모달 AI (9/10): 비디오 이해
- 바이브코딩을 위한 멀티모달 AI (10/10): Production 멀티모달 앱 구축
<!-- toc:end -->

Tags: 바이브코딩, 멀티모달 AI, Whisper, STT, Speech Recognition
