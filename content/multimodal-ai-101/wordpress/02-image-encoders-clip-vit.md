---
series: multimodal-ai-101
episode: 2
title: "바이브코딩을 위한 멀티모달 AI (2/10): Image Encoder: CLIP과 ViT"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 멀티모달 AI
  - CLIP
  - ViT
  - Image Encoder
language: ko
---

# 바이브코딩을 위한 멀티모달 AI (2/10): Image Encoder: CLIP과 ViT

> 이 글은 **바이브코딩을 위한 멀티모달 AI** 시리즈 2편입니다. ViT가 이미지를 patch token으로 바꾸는 구조, CLIP의 공통 임베딩 공간, 전처리와 normalization 계약을 다룹니다.

바이브코딩으로 멀티모달 앱을 만들 때 GPT-4V나 Claude Vision API를 바로 호출하면 "이미지를 이해한다"는 느낌을 빠르게 얻을 수 있다. 하지만 이미지 검색, 분류, 유사도 비교처럼 더 구체적인 기능을 만들려는 순간, 모델 내부에서 이미지가 어떤 벡터로 변환되는지 알아야 한다. 그 기반이 바로 image encoder다.

ViT(Vision Transformer)는 이미지를 16x16 pixel patch로 잘라 각 patch를 토큰으로 취급한다. 224x224 이미지는 196개 patch 토큰 + 1개 CLS 토큰으로 변환된다. CNN이 작은 receptive field부터 점점 키워가며 처리하는 것과 달리, ViT는 전체 이미지를 처음부터 트랜스포머로 다룬다. 덕분에 텍스트와 이미지를 같은 계산 프레임워크 안에서 처리할 수 있다.

CLIP은 여기서 한 발 더 나간다. 이미지 인코더와 텍스트 인코더를 함께 학습시켜, 같은 의미의 이미지-텍스트 쌍은 벡터 공간에서 가깝게, 다른 쌍은 멀게 배치한다. 덕분에 "a photo of a dog"라는 텍스트로 강아지 이미지를 검색하는 zero-shot cross-modal 검색이 가능해진다.

실무에서 중요한 것은 전처리 계약이다. CLIP을 쓸 때 입력 이미지는 224x224로 리사이징하고, ImageNet 기준 평균(mean=[0.481, 0.457, 0.408])과 표준편차(std=[0.268, 0.261, 0.275])로 정규화해야 한다. 임베딩은 반드시 L2 normalize해야 코사인 유사도 계산이 올바르게 작동한다. 이 계약 중 하나라도 어긋나면 검색 품질이 급격히 떨어진다.

> 좋은 image encoder는 이미지를 정답으로 직접 바꾸지 않습니다. 대신 나중에 검색과 추론이 잘 일어나는 표현으로 바꿔 줍니다.

## 이 글에서 다룰 문제

- ViT는 이미지를 어떤 방식으로 token sequence로 바꾸나요?
- CLIP은 어떻게 텍스트와 이미지를 같은 임베딩 공간에 배치하나요?
- zero-shot 분류와 cross-modal 검색은 어떤 원리로 작동하나요?
- 전처리와 normalization 계약을 어기면 어떤 문제가 생기나요?
- 초보자가 CLIP을 쓸 때 가장 자주 놓치는 포인트는 무엇인가요?

## Before / After: Image Encoder 이해 전후

| 상황 | 이해 전 | 이해 후 |
|------|--------|--------|
| 이미지 검색 | "모델이 이미지를 알아서 이해" | CLIP 임베딩 + 코사인 유사도 설계 |
| 전처리 | 원본 이미지 그대로 전송 | 224x224 리사이징 + 정규화 계약 준수 |
| 유사도 계산 | 벡터 내적 그냥 계산 | L2 normalize 후 코사인 유사도 |
| zero-shot 분류 | 별도 분류 모델 필요 | CLIP text encoder로 레이블 임베딩 비교 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| normalize 없이 코사인 유사도 계산 | 점수 해석 불가 | `F.normalize(embedding, dim=-1)` 필수 |
| 전처리 방식이 인덱싱/쿼리 간 불일치 | 검색 품질 급락 | 동일한 전처리 파이프라인 사용 |
| CLIP을 정밀 텍스트 추출에 사용 | 숫자, 주소 등 오인식 | 정밀 텍스트는 OCR 사용 |
| 모델 버전 혼용 (ViT-B/32 vs ViT-L/14) | 임베딩 차원 불일치 | 인덱싱과 검색에 동일 모델 고정 |

## AI 팁: CLIP 빠르게 시작하는 방법

Claude나 GPT-4에 "Python으로 OpenCLIP을 사용해 이미지와 텍스트를 같은 공간에 임베딩하고, 텍스트 쿼리로 이미지를 검색하는 코드를 만들어줘"라고 요청하면 작동하는 코드를 얻을 수 있다. `pip install open-clip-torch`로 시작하고, `open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")`로 모델을 로드한다. 이미지 임베딩과 텍스트 임베딩 모두 `F.normalize(emb, dim=-1)`를 적용한 뒤 `torch.matmul`로 유사도를 계산한다. 결과를 FAISS 인덱스에 넣으면 대규모 이미지 검색이 가능하다.

## 운영 체크리스트

- [ ] 이미지 전처리(리사이징, 정규화)를 인덱싱과 쿼리에서 동일하게 사용하는가
- [ ] 임베딩을 저장하기 전 L2 normalize를 적용하는가
- [ ] 인덱싱과 검색에 동일한 CLIP 모델 버전을 고정했는가
- [ ] zero-shot 분류 시 prompt template ("a photo of a {label}")을 사용하는가
- [ ] 정밀 텍스트 추출이 필요한 경우 CLIP 대신 OCR을 사용하는가

## 처음 질문으로 돌아가기

- **ViT vs CNN 차이는?** CNN은 local → global 순서로 처리하고, ViT는 처음부터 전체 이미지를 patch 토큰으로 보고 트랜스포머로 처리한다. 텍스트와 같은 계산 프레임워크를 공유한다.
- **CLIP zero-shot 분류 원리는?** 레이블을 텍스트 인코더로 임베딩하고, 이미지 임베딩과 코사인 유사도를 비교한다. 가장 가까운 레이블이 예측 결과다.
- **normalize가 중요한 이유는?** L2 normalize 없이는 벡터 크기가 유사도에 영향을 주어 의미 있는 비교가 불가능하다.

## 정리

ViT는 이미지를 patch token으로 재표현해 트랜스포머가 다루게 만들고, CLIP은 이미지와 텍스트를 같은 벡터 공간에 정렬해 cross-modal 검색을 가능하게 한다. 전처리와 normalization 계약은 사소한 옵션이 아니라 같은 표현 공간을 유지하기 위한 필수 계약이다.

## 참고 자료

- [OpenCLIP](https://github.com/mlfoundations/open_clip)
- [ViT 논문](https://arxiv.org/abs/2010.11929)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/02-image-encoders-clip-vit)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 멀티모달 AI (1/10): 멀티모달이 중요한 이유
- **바이브코딩을 위한 멀티모달 AI (2/10): Image Encoder: CLIP과 ViT (현재 글)**
- 바이브코딩을 위한 멀티모달 AI (3/10): Vision-Language Model 아키텍처
- 바이브코딩을 위한 멀티모달 AI (4/10): Image Captioning과 OCR 파이프라인
- 바이브코딩을 위한 멀티모달 AI (5/10): Multimodal RAG
- 바이브코딩을 위한 멀티모달 AI (6/10): 오디오 처리와 Whisper STT
- 바이브코딩을 위한 멀티모달 AI (7/10): Diffusion으로 이미지 생성
- 바이브코딩을 위한 멀티모달 AI (8/10): Multimodal Embedding과 Cross-modal 검색
- 바이브코딩을 위한 멀티모달 AI (9/10): 비디오 이해
- 바이브코딩을 위한 멀티모달 AI (10/10): Production 멀티모달 앱 구축
<!-- toc:end -->

Tags: 바이브코딩, 멀티모달 AI, CLIP, ViT, Image Encoder
