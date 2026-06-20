---
series: multimodal-ai-101
episode: 9
title: "바이브코딩을 위한 멀티모달 AI (9/10): 비디오 이해"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 멀티모달 AI
  - Video Understanding
  - Frame Sampling
  - Video-LLaVA
language: ko
---

# 바이브코딩을 위한 멀티모달 AI (9/10): 비디오 이해

> 이 글은 **바이브코딩을 위한 멀티모달 AI** 시리즈 9편입니다. frame sampling 전략, PyAV/scene change detection, VideoMAE/X-CLIP, 오디오 fusion, 비디오 QA 파이프라인을 다룹니다.

바이브코딩으로 비디오 처리 기능을 만들 때 가장 먼저 부딪히는 현실은 토큰 한계다. 10분 영상을 1080p 30fps로 처리하면 18,000 프레임, ViT-L 기준 약 4.6M 토큰이 나온다. GPT-4V의 context window(128K)를 단일 영상이 수십 배 초과한다. 그래서 비디오 이해의 첫 번째 문제는 모델 선택이 아니라 프레임 샘플링 전략이다.

uniform sampling은 가장 단순하다. 1초마다 1프레임처럼 일정 간격으로 뽑는다. 전체 개요를 파악하기 좋지만 빠른 장면 전환을 놓친다. keyframe extraction은 scene change detection으로 의미 있는 전환 시점을 찾아 그 프레임만 뽑는다. PyAV나 OpenCV로 구현하며, 장면 전환이 중요한 경우에 유리하다.

비디오 전용 인코더는 시간 정보를 직접 처리한다. VideoMAE는 영상을 tube mask로 처리해 시간적 패턴을 학습한다. TimeSformer는 spatial attention과 temporal attention을 분리한다. X-CLIP은 CLIP을 비디오로 확장해 zero-shot 비디오 분류를 가능하게 한다.

오디오와의 fusion도 고려해야 한다. 화면만으로는 놓치는 이벤트가 있고, 반대로 오디오만으로는 부족한 시각 단서가 있다. Whisper로 전사한 텍스트를 프레임 설명과 함께 LLM에 전달하면 오디오-비디오 통합 QA가 가능하다.

> 비디오 이해의 첫 번째 모델은 사실 sampling 정책입니다. 중요한 장면을 놓치면 그다음 모델은 아무리 커도 복구할 수 없습니다.

## 이 글에서 다룰 문제

- 왜 비디오 이해에서 frame sampling이 모델 선택보다 먼저 결정해야 할 핵심 변수인가요?
- uniform sampling과 keyframe extraction은 각각 어떤 상황에서 유리한가요?
- VideoMAE, TimeSformer, X-CLIP은 어떤 트레이드오프를 보여주나요?
- 오디오와 비디오를 어떻게 통합해서 처리하나요?
- 긴 영상에서 비디오 QA를 비용 효율적으로 구현하려면 어떻게 해야 할까요?

## Before / After: Frame Sampling 도입 전후

| 상황 | 프레임 전체 처리 | Sampling 전략 적용 |
|------|--------------|----------------|
| 10분 영상 토큰 수 | 4.6M (불가능) | 50-100 프레임으로 수천 토큰 |
| 비용 | 모델 한계 초과 | 예측 가능한 비용 |
| 빠른 장면 전환 | 전체에 묻힘 | keyframe extraction으로 포착 |
| 오디오 이벤트 | 영상만 보면 놓침 | Whisper transcript와 통합 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| sampling 없이 모든 프레임을 모델에 전달 | context 한계 초과, 비용 폭증 | uniform sampling 또는 keyframe extraction |
| 오디오 트랙 무시 | 음성 이벤트 놓침 | Whisper로 전사 후 프레임과 통합 |
| 단일 sampling 전략으로 모든 비디오 처리 | 콘텐츠 유형에 맞지 않음 | 동적 영상은 keyframe, 강의는 uniform |
| 타임스탬프 없는 transcript | 비디오 구간 연결 불가 | Whisper `word_timestamps=True` 설정 |

## AI 팁: 비디오 QA 빠르게 구현하는 방법

Claude나 GPT-4에 "Python으로 영상에서 1초마다 프레임을 추출하고, Whisper로 오디오를 전사한 뒤, 프레임 설명과 transcript를 합쳐 GPT-4V에 질문하는 비디오 QA 파이프라인을 만들어줘"라고 요청하면 시작할 수 있다. `pip install av faster-whisper openai`로 시작하고, PyAV로 `container.decode(video=0)`으로 프레임을 순회하며 interval마다 저장한다. Whisper로 오디오 트랙을 전사하고 segment timestamp를 얻는다. GPT-4V messages에 프레임 이미지들과 `"Transcript: {transcript}"` 텍스트를 함께 포함해 전달한다.

## 운영 체크리스트

- [ ] 비디오 유형에 맞는 sampling 전략(uniform vs keyframe)을 선택했는가
- [ ] sampling 후 총 토큰 수가 모델 context 한계 이내인지 확인하는가
- [ ] 오디오 트랙을 Whisper로 전사해 타임스탬프와 함께 보존하는가
- [ ] 프레임과 transcript를 시간 순서로 구조화해 VLM에 전달하는가
- [ ] 비디오 처리 비용(프레임당 토큰 비용)을 사전에 계측했는가

## 처음 질문으로 돌아가기

- **uniform vs keyframe sampling 선택 기준은?** 전체 개요 파악이 목적이면 uniform. 장면 전환, 이벤트 감지가 목적이면 keyframe extraction. 강의 영상은 uniform, 뉴스/영화는 keyframe이 유리하다.
- **X-CLIP은 언제 쓰나?** zero-shot 비디오 분류가 필요할 때. 액션 인식, 스포츠 이벤트 분류처럼 레이블 집합이 정해진 분류 문제에 적합하다.
- **오디오-비디오 통합 핵심은?** Whisper로 전사한 텍스트에 segment 타임스탬프를 붙이고, 가장 가까운 프레임과 연결해 VLM에 "이 시간대의 영상과 자막: ..." 형태로 전달한다.

## 정리

비디오 이해에서 가장 먼저 해야 할 일은 sampling 정책을 정하는 것이다. uniform 또는 keyframe sampling으로 프레임 수를 줄이고, Whisper로 오디오를 전사해 시간 정보를 보존한 뒤, 프레임과 transcript를 구조화해서 VLM에 전달하면 비용 효율적인 비디오 QA 파이프라인을 만들 수 있다.

## 참고 자료

- [PyAV](https://pyav.org/)
- [VideoMAE](https://github.com/MCG-NJU/VideoMAE)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/09-video-understanding)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 멀티모달 AI (1/10): 멀티모달이 중요한 이유
- 바이브코딩을 위한 멀티모달 AI (2/10): Image Encoder: CLIP과 ViT
- 바이브코딩을 위한 멀티모달 AI (3/10): Vision-Language Model 아키텍처
- 바이브코딩을 위한 멀티모달 AI (4/10): Image Captioning과 OCR 파이프라인
- 바이브코딩을 위한 멀티모달 AI (5/10): Multimodal RAG
- 바이브코딩을 위한 멀티모달 AI (6/10): 오디오 처리와 Whisper STT
- 바이브코딩을 위한 멀티모달 AI (7/10): Diffusion으로 이미지 생성
- 바이브코딩을 위한 멀티모달 AI (8/10): Multimodal Embedding과 Cross-modal 검색
- **바이브코딩을 위한 멀티모달 AI (9/10): 비디오 이해 (현재 글)**
- 바이브코딩을 위한 멀티모달 AI (10/10): Production 멀티모달 앱 구축
<!-- toc:end -->

Tags: 바이브코딩, 멀티모달 AI, Video Understanding, Frame Sampling, Video-LLaVA
