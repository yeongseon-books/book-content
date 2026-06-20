---
series: multimodal-ai-101
episode: 5
title: "바이브코딩을 위한 멀티모달 AI (5/10): Multimodal RAG"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 멀티모달 AI
  - Multimodal RAG
  - CLIP Embeddings
  - Vector Search
language: ko
---

# 바이브코딩을 위한 멀티모달 AI (5/10): Multimodal RAG

> 이 글은 **바이브코딩을 위한 멀티모달 AI** 시리즈 5편입니다. 이미지·텍스트를 함께 인덱싱하는 세 가지 전략, cross-modal retrieval 구현, VLM과의 연결을 다룹니다.

바이브코딩으로 RAG를 만들다 보면 텍스트 청크 검색만으로는 답이 안 나오는 질문이 생긴다. "이런 모양의 차트가 있는 슬라이드를 찾아줘", "스크린샷 속 경고 아이콘이 무엇을 의미하나요?", "제품 사진과 가장 유사한 항목을 보여줘." 이런 질문은 텍스트 임베딩만으로는 검색할 수 없다.

멀티모달 RAG는 검색 대상을 이미지·caption·OCR·메타데이터까지 넓히고, 최종 생성 단계에서 VLM이 그 결과를 함께 읽게 만드는 구조다.

인덱싱 전략은 세 가지로 나뉜다. 첫째, CLIP image embedding을 직접 인덱싱하고 텍스트 쿼리를 CLIP text encoder로 변환해 검색하는 방식이다. 가장 단순하지만 정밀 텍스트 검색은 약하다. 둘째, OCR 텍스트와 caption을 텍스트 임베딩으로 인덱싱하는 방식이다. 기존 텍스트 RAG 인프라를 재사용할 수 있고 구현이 쉽다. 셋째, CLIP embedding과 텍스트 embedding을 동시에 유지하는 dual index 방식이다. 쿼리 타입에 따라 검색 경로를 선택하므로 가장 유연하지만 관리 비용이 높다.

생성 단계는 검색 결과를 VLM에 넘겨 최종 답변을 만든다. 원본 이미지를 직접 넣을지, caption과 OCR 텍스트를 합쳐 넣을지는 비용과 품질의 트레이드오프다. 복잡한 시각 추론이 필요하면 원본 이미지를, 텍스트 맥락으로 충분하면 caption + OCR을 사용한다.

> 멀티모달 RAG의 난점은 VLM 호출 자체보다, 무엇을 검색 가능한 표현으로 만들고 무엇을 최종 컨텍스트에 넣을지 결정하는 데 있습니다.

## 이 글에서 다룰 문제

- 텍스트 RAG는 왜 이미지·표·레이아웃 질문에서 한계가 드러날까요?
- 이미지 embedding, caption/OCR 텍스트, dual index 세 전략의 차이는 무엇인가요?
- 검색 결과를 VLM에 넘길 때 어떤 입력 조합이 가장 실용적인가요?
- 멀티모달 RAG를 어떻게 평가해야 할까요?
- 초보자가 멀티모달 RAG 구현 시 가장 자주 놓치는 포인트는 무엇인가요?

## Before / After: Multimodal RAG 도입 전후

| 상황 | 텍스트 RAG만 | Multimodal RAG |
|------|------------|---------------|
| 이미지 포함 문서 검색 | 텍스트 부분만 검색 | 이미지 의미도 검색 대상 |
| 차트/그래프 질문 | 답변 불가 | caption + 이미지로 답변 |
| 제품 이미지 유사도 검색 | 텍스트 설명으로만 검색 | CLIP으로 시각 유사도 검색 |
| 검색 품질 평가 | 텍스트 hit@k만 | image retrieval hit@k 별도 측정 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| retrieval 없이 VLM에 이미지 직접 전달 | 컨텍스트 창 초과, 비용 급증 | 검색으로 관련 이미지만 선별 |
| 이미지 embedding만 인덱싱 | 정밀 텍스트 검색 불가 | dual index로 OCR 텍스트도 함께 |
| 검색 품질과 응답 품질 혼합 평가 | 개선 방향 모호 | retrieval hit@k와 faithfulness 분리 측정 |
| 원본 이미지 항상 VLM에 전달 | 비용 급증 | caption + OCR로 충분한 경우 텍스트만 사용 |

## AI 팁: Multimodal RAG 빠르게 시작하는 방법

Claude나 GPT-4에 "Python으로 CLIP으로 이미지를 임베딩해 FAISS에 인덱싱하고, 텍스트 쿼리로 가장 유사한 이미지를 검색한 뒤 GPT-4V에 전달하는 멀티모달 RAG를 만들어줘"라고 요청하면 시작할 수 있다. `pip install open-clip-torch faiss-cpu`로 시작하고, 이미지 임베딩을 L2 normalize해서 FAISS IndexFlatIP에 넣는다. 검색 결과는 상위 3개를 base64로 인코딩해 GPT-4V의 messages 배열에 포함한다. 평가는 정답 이미지가 상위 k개 안에 드는지 확인하는 `hit@k` 메트릭으로 시작한다.

## 운영 체크리스트

- [ ] 인덱싱 전략(image embedding / 텍스트 / dual)을 사용 사례에 맞게 선택했는가
- [ ] 이미지 embedding을 L2 normalize해서 인덱싱하는가
- [ ] 검색 품질(retrieval hit@k)과 응답 품질(faithfulness)을 분리해서 측정하는가
- [ ] VLM에 넘길 때 원본 이미지와 caption + OCR 텍스트 중 비용 효율적인 방식을 선택하는가
- [ ] 멀티모달 메타데이터(이미지 출처, 문서명)를 검색 결과와 함께 로깅하는가

## 처음 질문으로 돌아가기

- **인덱싱 전략 선택 기준은?** 시각적 유사도 검색이 핵심이면 image embedding. 정밀 텍스트 검색이 필요하면 caption + OCR 텍스트. 둘 다 필요하면 dual index.
- **VLM에 원본 이미지 vs 텍스트 선택 기준은?** 시각 추론이 필수적이면 원본 이미지. 텍스트 맥락으로 충분하면 caption + OCR을 사용해 비용을 절약한다.
- **멀티모달 RAG 평가는?** 텍스트 RAG의 hit@k와 faithfulness 외에, 이미지 retrieval hit@k를 별도로 측정해 검색 품질을 분리한다.

## 정리

멀티모달 RAG는 VLM을 붙인 RAG가 아니라, 검색 표현과 생성 입력을 함께 재설계하는 확장형 retrieval 시스템이다. 인덱싱 전략을 먼저 고정하고, 검색 품질과 응답 품질을 분리해서 측정하면 성능 개선 방향이 명확해진다.

## 참고 자료

- [FAISS](https://github.com/facebookresearch/faiss)
- [OpenCLIP](https://github.com/mlfoundations/open_clip)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/05-multimodal-rag)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 멀티모달 AI (1/10): 멀티모달이 중요한 이유
- 바이브코딩을 위한 멀티모달 AI (2/10): Image Encoder: CLIP과 ViT
- 바이브코딩을 위한 멀티모달 AI (3/10): Vision-Language Model 아키텍처
- 바이브코딩을 위한 멀티모달 AI (4/10): Image Captioning과 OCR 파이프라인
- **바이브코딩을 위한 멀티모달 AI (5/10): Multimodal RAG (현재 글)**
- 바이브코딩을 위한 멀티모달 AI (6/10): 오디오 처리와 Whisper STT
- 바이브코딩을 위한 멀티모달 AI (7/10): Diffusion으로 이미지 생성
- 바이브코딩을 위한 멀티모달 AI (8/10): Multimodal Embedding과 Cross-modal 검색
- 바이브코딩을 위한 멀티모달 AI (9/10): 비디오 이해
- 바이브코딩을 위한 멀티모달 AI (10/10): Production 멀티모달 앱 구축
<!-- toc:end -->

Tags: 바이브코딩, 멀티모달 AI, Multimodal RAG, CLIP Embeddings, Vector Search
