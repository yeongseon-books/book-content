---
series: multimodal-ai-101
episode: 7
title: "바이브코딩을 위한 멀티모달 AI (7/10): Diffusion으로 이미지 생성"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 멀티모달 AI
  - Diffusion
  - Stable Diffusion
  - Text-to-Image
language: ko
---

# 바이브코딩을 위한 멀티모달 AI (7/10): Diffusion으로 이미지 생성

> 이 글은 **바이브코딩을 위한 멀티모달 AI** 시리즈 7편입니다. Diffusion의 forward/reverse process, Stable Diffusion의 text encoder/UNet/VAE, CFG/ControlNet/inpainting 운영 설계를 다룹니다.

바이브코딩으로 이미지 생성 기능을 만들 때 가장 빠른 시작은 DALL-E API나 Stable Diffusion API를 호출하는 것이다. 하지만 "왜 같은 프롬프트인데 결과가 이렇게 다른가?", "CFG scale을 올리면 왜 이미지가 바뀌는가?", "ControlNet을 쓰면 무엇이 가능한가?" 같은 질문이 생기는 순간 diffusion 구조를 이해해야 한다.

Diffusion의 직관은 단순하다. 학습 단계에서는 이미지를 조금씩 Gaussian noise로 망가뜨리는 과정(forward process)을 학습하고, 추론 단계에서는 순수 노이즈에서 시작해 그 망가짐을 역방향으로 되돌리는 과정(reverse process)으로 이미지를 생성한다. 매 step마다 텍스트 조건을 반영하면서 점진적으로 이미지를 복원한다.

Stable Diffusion의 구조는 세 부품이다. text encoder(CLIP)가 프롬프트를 조건 벡터로 변환하고, UNet이 노이즈 예측을 반복 수행하며, VAE가 latent space와 pixel space 사이를 변환한다. latent diffusion은 pixel 공간이 아니라 압축된 latent 공간에서 denoising을 수행해 계산 비용을 크게 낮춘다.

CFG(Classifier-Free Guidance) scale은 텍스트 조건을 얼마나 강하게 따를지 제어한다. 7.0-9.0이 일반적이며, 높일수록 프롬프트 충실도는 올라가지만 다양성이 줄어든다. ControlNet은 edge map, depth, skeleton 같은 조건 신호를 추가로 넣어 구도나 자세를 제어한다.

운영에서 핵심은 safety filter와 저작권 정책이다. 생성 이미지에는 NSFW 필터를 반드시 붙이고, 학습 데이터 저작권 이슈를 인지한 채 사용 범위를 명확히 해야 한다.

> Diffusion의 힘은 한 번에 완성된 이미지를 내는 데 있지 않습니다. 매 step에서 조건 신호를 조금씩 반영하며 결과를 통제할 수 있다는 데 있습니다.

## 이 글에서 다룰 문제

- Diffusion의 forward/reverse process는 어떤 원리로 작동하나요?
- Stable Diffusion의 text encoder, UNet, VAE는 각각 무슨 역할을 맡나요?
- CFG scale, step 수, negative prompt는 어떻게 설정해야 하나요?
- ControlNet과 inpainting은 언제 사용해야 할까요?
- 이미지 생성 기능을 production에 올릴 때 반드시 설계해야 할 안전 장치는 무엇인가요?

## Before / After: Diffusion 기반 이미지 생성 전후

| 상황 | GAN 시대 | Diffusion |
|------|---------|----------|
| 텍스트 제어 | 어려움 | CFG로 프롬프트 충실도 조정 |
| 학습 안정성 | mode collapse 빈번 | 안정적 학습 |
| 구도/자세 제어 | 불가능 | ControlNet으로 정밀 제어 |
| 인페인팅 | 별도 모델 필요 | 동일 모델로 마스크 기반 편집 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| safety filter 없이 배포 | NSFW 이미지 서비스 노출 | NSFW 분류기 필수 |
| step 수를 무조건 높임 | 지연 시간 급증, 품질 향상 미미 | 20-30 step이 품질 대비 비용 최적 |
| negative prompt 없이 생성 | 원하지 않는 요소 빈번 등장 | "blurry, bad anatomy, worst quality" 등 기본 negative 설정 |
| CFG를 너무 높게 설정 | 과도하게 saturated되고 부자연스러운 이미지 | 7.0-9.0 사이 유지 |

## AI 팁: Diffusion 이미지 생성 빠르게 시작하는 방법

Claude나 GPT-4에 "Python으로 diffusers 라이브러리를 사용해 Stable Diffusion으로 텍스트에서 이미지를 생성하는 코드를 만들어줘. CFG scale과 step 수를 설정하고, NSFW 필터도 포함해줘"라고 요청하면 시작할 수 있다. `pip install diffusers transformers accelerate`로 설치하고, `StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")`로 로드한다. API를 쓰려면 OpenAI DALL-E 3 `openai.images.generate(model="dall-e-3", prompt="...", size="1024x1024")`가 가장 빠르다. ControlNet은 `diffusers.ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-canny")`로 edge 기반 제어를 추가할 수 있다.

## 운영 체크리스트

- [ ] 모든 생성 이미지에 NSFW 분류기를 적용하는가
- [ ] step 수와 CFG scale을 비용-품질 기준으로 튜닝했는가
- [ ] 저작권 정책(생성 이미지 상업 이용 조건)을 검토했는가
- [ ] 생성 실패 시(NSFW 감지, 타임아웃) 사용자에게 명확한 메시지를 보여주는가
- [ ] 이미지 생성 요청에 rate limit을 적용하는가

## 처음 질문으로 돌아가기

- **CFG scale 설정 기준은?** 7.0-9.0이 일반적. 프롬프트를 더 강하게 따르게 하려면 높이고, 다양성을 원하면 낮춘다.
- **ControlNet을 써야 할 때는?** 구도, 자세, 윤곽을 정밀하게 제어해야 할 때. edge map, depth, pose skeleton을 조건으로 넣는다.
- **inpainting 활용은?** 이미지의 특정 영역만 수정할 때. 마스크를 만들고 해당 부분만 재생성한다. 제품 배경 교체, 로고 삽입 등에 유용하다.

## 정리

Diffusion은 노이즈를 점진적으로 제거하며 이미지를 생성하는 프레임워크다. CFG로 프롬프트 충실도를 조정하고, ControlNet으로 구도를 제어하며, inpainting으로 부분 편집이 가능하다. production에서는 safety filter, step 수 최적화, 저작권 정책을 처음부터 설계해야 한다.

## 참고 자료

- [HuggingFace Diffusers](https://huggingface.co/docs/diffusers)
- [OpenAI DALL-E API](https://platform.openai.com/docs/guides/images)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/07-text-to-image-diffusion)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 멀티모달 AI (1/10): 멀티모달이 중요한 이유
- 바이브코딩을 위한 멀티모달 AI (2/10): Image Encoder: CLIP과 ViT
- 바이브코딩을 위한 멀티모달 AI (3/10): Vision-Language Model 아키텍처
- 바이브코딩을 위한 멀티모달 AI (4/10): Image Captioning과 OCR 파이프라인
- 바이브코딩을 위한 멀티모달 AI (5/10): Multimodal RAG
- 바이브코딩을 위한 멀티모달 AI (6/10): 오디오 처리와 Whisper STT
- **바이브코딩을 위한 멀티모달 AI (7/10): Diffusion으로 이미지 생성 (현재 글)**
- 바이브코딩을 위한 멀티모달 AI (8/10): Multimodal Embedding과 Cross-modal 검색
- 바이브코딩을 위한 멀티모달 AI (9/10): 비디오 이해
- 바이브코딩을 위한 멀티모달 AI (10/10): Production 멀티모달 앱 구축
<!-- toc:end -->

Tags: 바이브코딩, 멀티모달 AI, Diffusion, Stable Diffusion, Text-to-Image
