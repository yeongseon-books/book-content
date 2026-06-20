---
series: multimodal-ai-101
episode: 3
title: "바이브코딩을 위한 멀티모달 AI (3/10): Vision-Language Model 아키텍처"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 멀티모달 AI
  - VLM
  - LLaVA
  - BLIP-2
language: ko
---

# 바이브코딩을 위한 멀티모달 AI (3/10): Vision-Language Model 아키텍처

> 이 글은 **바이브코딩을 위한 멀티모달 AI** 시리즈 3편입니다. LLaVA의 projection 방식, BLIP-2의 Q-Former, Flamingo의 cross-attention, 각 설계의 비용·지연·품질 트레이드오프를 다룹니다.

바이브코딩으로 멀티모달 앱을 만들 때 "어떤 VLM을 써야 하나"는 질문이 금방 나온다. GPT-4V, LLaVA, BLIP-2, Flamingo 중 무엇을 고를지 감이 안 잡히면 대부분 "요즘 많이 쓰니까"로 선택하게 된다. 하지만 아키텍처 차이를 이해하면 비용, 지연, 품질의 균형을 실제 요구사항에 맞게 판단할 수 있다.

VLM은 공통적으로 Vision Encoder + Adapter + LLM 세 부품으로 구성된다. 이미지를 CLIP/SigLIP 같은 vision encoder가 시각 토큰으로 변환하고, adapter가 그 토큰을 LLM이 소화할 수 있는 형태로 재매핑한 뒤, LLM이 최종 응답을 생성한다. 세 학파는 adapter 방식에서 갈린다.

LLaVA는 가장 단순하다. MLP projection으로 vision 토큰을 LLM 입력 공간에 직접 연결한다. 구현이 쉽고 fine-tuning 범위도 명확하지만, 긴 이미지에서 시각 토큰 수가 많아지면 context를 빠르게 소진한다. BLIP-2는 Q-Former라는 중간 모듈을 두어 고정된 수의 query 토큰으로 시각 정보를 압축한다. 시각 토큰 수를 제어할 수 있어 비용 예측이 쉽다. Flamingo는 cross-attention 층을 LLM 내부에 삽입해 이미지와 텍스트를 레이어별로 상호작용하게 만든다. 다중 이미지 입력에 강하지만 구조가 가장 복잡하다.

바이브코딩 환경에서 가장 현실적인 시작점은 GPT-4V나 Claude Vision 같은 API 기반 VLM이다. 자체 호스팅이 필요하다면 LLaVA가 단순성과 fine-tuning 유연성 면에서 유리하다.

> VLM의 본질은 시각 정보를 더 많이 넣는 것이 아니라, LLM이 소화할 수 있는 길이와 형태로 토큰 계약을 재설계하는 데 있습니다.

## 이 글에서 다룰 문제

- VLM은 어떤 경로로 image encoder의 출력을 LLM 입력으로 연결하나요?
- LLaVA, BLIP-2, Flamingo는 각각 어떤 트레이드오프를 선택한 설계인가요?
- visual token 수가 비용과 지연에 어떤 영향을 미치나요?
- 어떤 기준으로 VLM 아키텍처를 선택해야 할까요?
- 초보자가 VLM 도입 시 가장 자주 놓치는 포인트는 무엇인가요?

## Before / After: VLM 아키텍처 이해 전후

| 상황 | 이해 전 | 이해 후 |
|------|--------|--------|
| 모델 선택 | "요즘 많이 쓰니까" LLaVA | 비용·지연·품질 기준으로 판단 |
| visual token 비용 | 예측 불가 | Q-Former로 토큰 수 고정 가능 |
| fine-tuning 범위 | 전체 모델 재학습 시도 | adapter만 학습, base 고정 |
| 다중 이미지 처리 | 성능 저하 이해 불가 | Flamingo 스타일 cross-attention 고려 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| visual token 수를 고려 안 함 | context 창 초과, 비용 급증 | Q-Former로 토큰 수 제한 또는 detail=low |
| base LLM과 vision encoder를 함께 fine-tuning | 비용·데이터 낭비 | adapter만 학습, base 고정 |
| 단일 이미지용 아키텍처로 다중 이미지 처리 | 성능 저하 | 다중 이미지는 Flamingo 스타일 검토 |
| API VLM의 내부 토큰 비용 미계측 | 월말 청구서 충격 | 이미지당 토큰 비용 사전 측정 |

## AI 팁: VLM 빠르게 시작하는 방법

Claude나 GPT-4에 "Python으로 LLaVA를 사용해 이미지와 질문을 함께 처리하는 코드를 만들어줘. transformers 라이브러리를 사용하고, 이미지를 base64로 인코딩해서 전달해줘"라고 요청하면 작동하는 코드를 얻을 수 있다. API 기반으로 시작하려면 OpenAI GPT-4V의 `gpt-4-vision-preview` 모델을 사용하고, `max_tokens`를 설정해 응답 비용을 제어한다. 자체 호스팅이 필요하면 `llava-hf/llava-1.5-7b-hf`를 HuggingFace에서 로드해 시작할 수 있다.

## 운영 체크리스트

- [ ] 사용할 VLM의 visual token 비용을 이미지 유형별로 측정했는가
- [ ] fine-tuning이 필요한 경우 adapter만 학습하고 base 모델을 고정했는가
- [ ] 다중 이미지 입력이 필요한 경우 적합한 아키텍처를 선택했는가
- [ ] context 창 초과 방지를 위한 입력 길이 제한이 있는가
- [ ] 응답 품질을 측정하는 평가셋을 구성했는가

## 처음 질문으로 돌아가기

- **LLaVA vs BLIP-2 선택 기준은?** 단순성과 fine-tuning 유연성이 필요하면 LLaVA. 시각 토큰 수를 고정하고 비용을 예측 가능하게 만들고 싶으면 BLIP-2.
- **visual token 수를 줄이는 방법은?** Q-Former처럼 고정된 query 토큰으로 압축하거나, API에서 `detail=low` 옵션을 사용한다.
- **adapter만 fine-tuning해도 되는 이유는?** base LLM과 vision encoder는 이미 풍부한 표현을 가지고 있다. adapter가 둘 사이의 연결을 학습하면 충분한 경우가 많다.

## 정리

VLM 아키텍처는 vision encoder, adapter, LLM 세 층의 조합이다. LLaVA는 단순 projection으로 빠르게 시작하기 좋고, BLIP-2는 Q-Former로 토큰 수를 제어하며, Flamingo는 다중 이미지에서 강하다. 바이브코딩 환경에서는 API 기반 VLM으로 시작하고, 비용·지연·품질 요구에 따라 자체 호스팅 아키텍처를 선택한다.

## 참고 자료

- [LLaVA](https://llava-vl.github.io/)
- [BLIP-2](https://arxiv.org/abs/2301.12597)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/03-vlm-architecture)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 멀티모달 AI (1/10): 멀티모달이 중요한 이유
- 바이브코딩을 위한 멀티모달 AI (2/10): Image Encoder: CLIP과 ViT
- **바이브코딩을 위한 멀티모달 AI (3/10): Vision-Language Model 아키텍처 (현재 글)**
- 바이브코딩을 위한 멀티모달 AI (4/10): Image Captioning과 OCR 파이프라인
- 바이브코딩을 위한 멀티모달 AI (5/10): Multimodal RAG
- 바이브코딩을 위한 멀티모달 AI (6/10): 오디오 처리와 Whisper STT
- 바이브코딩을 위한 멀티모달 AI (7/10): Diffusion으로 이미지 생성
- 바이브코딩을 위한 멀티모달 AI (8/10): Multimodal Embedding과 Cross-modal 검색
- 바이브코딩을 위한 멀티모달 AI (9/10): 비디오 이해
- 바이브코딩을 위한 멀티모달 AI (10/10): Production 멀티모달 앱 구축
<!-- toc:end -->

Tags: 바이브코딩, 멀티모달 AI, VLM, LLaVA, BLIP-2
