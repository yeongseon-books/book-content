---
series: multimodal-ai-101
episode: 4
title: "바이브코딩을 위한 멀티모달 AI (4/10): Image Captioning과 OCR 파이프라인"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 멀티모달 AI
  - OCR
  - Image Captioning
  - Document AI
language: ko
---

# 바이브코딩을 위한 멀티모달 AI (4/10): Image Captioning과 OCR 파이프라인

> 이 글은 **바이브코딩을 위한 멀티모달 AI** 시리즈 4편입니다. BLIP 계열 captioning, Tesseract/PaddleOCR/Document AI 선택 기준, hybrid pipeline 설계를 다룹니다.

바이브코딩으로 문서 처리 앱을 만들 때 가장 먼저 떠오르는 생각은 "이미지에서 텍스트를 뽑으면 되겠다"는 것이다. OCR로 텍스트를 추출하고 LLM에 넘기는 방식은 빠르게 작동하는 것처럼 보인다. 그런데 표 구조, 시각적 강조, 레이아웃 의미는 텍스트로 환원되는 순간 사라진다. 반대로 captioning만 하면 장면 의미는 얻지만 주소, 금액, 일련번호 같은 정밀 텍스트를 놓친다.

production 파이프라인에서는 captioning과 OCR을 경쟁 관계로 보지 않는다. OCR로 정밀 텍스트를 확보하고, captioning으로 장면 맥락을 덧붙이는 hybrid 접근이 가장 안정적이다.

captioning 모델은 두 가지 경로가 있다. BLIP-2 같은 전용 captioning 모델은 빠르고 저렴하며 장면 요약에 특화되어 있다. GPT-4V 같은 VLM 기반 description은 표 변환, 도형 설명, 레이아웃 해석까지 가능하지만 비용이 높다. 복잡하지 않은 이미지는 BLIP-2로 시작하고, 복잡한 문서는 VLM으로 넘기는 라우팅 전략이 현실적이다.

OCR 엔진 선택 기준은 명확하다. Tesseract는 무료이고 간단한 한국어/영어 텍스트에 충분하지만 복잡한 레이아웃에서 약하다. PaddleOCR은 다국어와 복잡한 레이아웃을 더 잘 처리하며 self-hosting이 가능하다. Google Document AI, Azure Form Recognizer 같은 클라우드 서비스는 비용이 있지만 표 구조 추출, 키-값 쌍 인식, PII 마스킹까지 포함한다.

> 문서 이미지를 이해한다는 것은 문자를 읽는 일과 장면을 해석하는 일을 동시에 다루는 것입니다. 둘 중 하나만 잘해서는 production 품질이 오래 버티지 못합니다.

## 이 글에서 다룰 문제

- 왜 "텍스트만 추출하면 된다"는 접근이 문서 처리에서 자주 실패할까요?
- Captioning 모델과 VLM 기반 description은 어떤 입력에서 각각 강점을 보일까요?
- Tesseract, PaddleOCR, Document AI는 어떤 기준으로 선택해야 할까요?
- hybrid pipeline은 어떤 구조로 설계하는 편이 실용적일까요?
- confidence threshold와 PII 마스킹은 어떻게 처리해야 할까요?

## Before / After: Hybrid Pipeline 도입 전후

| 상황 | OCR만 | Hybrid Pipeline |
|------|-------|----------------|
| 표 안의 숫자 | 정확히 추출 | OCR + 구조 정보 함께 |
| 이미지 전반 의미 | 텍스트 없으면 모름 | Captioning으로 장면 파악 |
| 복잡한 레이아웃 | 열 구조 무너짐 | Document AI로 구조 보존 |
| 저품질 이미지 | confidence 낮음 | threshold + fallback 처리 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| OCR만으로 모든 이미지 처리 | 시각 맥락 손실 | captioning으로 장면 보완 |
| VLM으로 모든 문서 처리 | 비용 급증 | 단순 이미지는 BLIP-2, 복잡한 문서는 VLM |
| confidence threshold 미설정 | 저품질 텍스트 LLM에 전달 | threshold 미만은 재시도 또는 플래그 |
| 회전 이미지 전처리 누락 | OCR 오인식 | 전처리에서 회전 보정(deskew) 포함 |

## AI 팁: Captioning + OCR 빠르게 시작하는 방법

Claude나 GPT-4에 "Python으로 이미지에서 OCR 텍스트와 caption을 함께 추출하는 파이프라인을 만들어줘. PaddleOCR로 텍스트를 뽑고, transformers의 BLIP 모델로 장면 설명을 생성해줘"라고 요청하면 시작할 수 있다. 간단하게는 `pip install paddlepaddle paddleocr transformers`로 설치하고, OCR 결과의 confidence를 확인해 0.8 미만은 별도 처리한다. 최종 LLM에는 `OCR: {ocr_text}\nCaption: {caption}`처럼 두 정보를 구조화해서 전달한다.

## 운영 체크리스트

- [ ] OCR confidence threshold를 설정하고 미만 이미지를 별도 처리하는가
- [ ] 이미지 회전 보정(deskew)을 전처리에 포함했는가
- [ ] 복잡한 문서와 단순 이미지를 다른 모델로 라우팅하는가
- [ ] LLM에 전달할 때 OCR 텍스트와 caption을 구조화해서 합치는가
- [ ] PII가 이미지 안에 포함될 경우 마스킹 정책을 정의했는가

## 처음 질문으로 돌아가기

- **OCR vs Captioning 선택 기준은?** 정밀 텍스트(숫자, 주소, 코드)가 필요하면 OCR. 장면 의미와 레이아웃 이해가 필요하면 captioning. 둘 다 필요하면 hybrid.
- **Tesseract vs PaddleOCR vs Document AI 선택은?** 비용 0이 최우선이면 Tesseract. 다국어·복잡 레이아웃은 PaddleOCR. 표 구조·키-값 추출까지 필요하면 클라우드 Document AI.
- **hybrid pipeline 핵심은?** OCR 결과와 caption을 별도 필드로 구조화하고, LLM에 "다음 정보를 참고해"라는 형태로 명확히 분리해 전달한다.

## 정리

OCR은 정밀 텍스트를, captioning은 장면 맥락을 제공한다. 둘은 경쟁 관계가 아니라 서로 빈 영역을 채워 주는 단계다. hybrid pipeline으로 두 경로를 결합하고, confidence threshold와 모델 라우팅 전략을 처음부터 설계하면 production 문서 처리 품질을 안정적으로 유지할 수 있다.

## 참고 자료

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [BLIP-2 (HuggingFace)](https://huggingface.co/Salesforce/blip2-opt-2.7b)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/04-captioning-ocr-pipelines)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 멀티모달 AI (1/10): 멀티모달이 중요한 이유
- 바이브코딩을 위한 멀티모달 AI (2/10): Image Encoder: CLIP과 ViT
- 바이브코딩을 위한 멀티모달 AI (3/10): Vision-Language Model 아키텍처
- **바이브코딩을 위한 멀티모달 AI (4/10): Image Captioning과 OCR 파이프라인 (현재 글)**
- 바이브코딩을 위한 멀티모달 AI (5/10): Multimodal RAG
- 바이브코딩을 위한 멀티모달 AI (6/10): 오디오 처리와 Whisper STT
- 바이브코딩을 위한 멀티모달 AI (7/10): Diffusion으로 이미지 생성
- 바이브코딩을 위한 멀티모달 AI (8/10): Multimodal Embedding과 Cross-modal 검색
- 바이브코딩을 위한 멀티모달 AI (9/10): 비디오 이해
- 바이브코딩을 위한 멀티모달 AI (10/10): Production 멀티모달 앱 구축
<!-- toc:end -->

Tags: 바이브코딩, 멀티모달 AI, OCR, Image Captioning, Document AI
