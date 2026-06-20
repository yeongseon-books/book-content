---
series: ai-web-dev-101
episode: 4
title: "바이브코딩을 위한 AI 웹 개발 (4/7): RAG 기초"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - AI 웹 개발
  - RAG
  - Embeddings
  - Vector Search
language: ko
---

# 바이브코딩을 위한 AI 웹 개발 (4/7): RAG 기초

> 이 글은 **바이브코딩을 위한 AI 웹 개발** 시리즈 4편입니다. 임베딩과 코사인 유사도로 관련 문서를 검색해 LLM 응답에 연결하는 RAG 구조를 다룹니다.

바이브코딩으로 AI 앱을 만들다 보면 "모델이 내 회사 데이터를 알 수 없다"는 한계에 금방 부딪힌다. 해결책은 두 가지다. fine-tuning으로 모델에 지식을 주입하거나, RAG로 필요한 정보를 검색해 모델에 전달하는 것이다. 바이브코딩 환경에서 RAG가 훨씬 현실적이다. fine-tuning은 비용과 시간이 크고, 지식이 바뀔 때마다 다시 해야 한다.

RAG(Retrieval-Augmented Generation)는 단순하다. 질문을 임베딩 벡터로 변환하고, 문서 벡터 인덱스에서 가장 유사한 chunk를 찾아서, 그것을 프롬프트에 포함해 모델에 전달한다. 모델은 검색된 문맥을 바탕으로 답변한다.

임베딩은 `text-embedding-3-small`로 시작하면 된다. 코사인 유사도는 numpy로 몇 줄이면 구현된다. 청크 전략(chunk size, overlap)이 검색 품질에 직접 영향을 준다. 너무 크면 관련 없는 내용이 섞이고, 너무 작으면 맥락이 끊긴다.

프롬프트 injection 방지도 중요하다. 외부 문서에서 가져온 내용을 그대로 프롬프트에 넣으면, 문서 안에 숨겨진 지시가 모델을 조작할 수 있다. 검색 결과는 `<document>` 태그로 감싸고 "아래 문서를 참고해"라는 형식으로 구조화해야 한다.

question, retrieved_chunks, answer를 함께 로깅하면 나중에 검색 품질과 응답 품질을 분리해서 개선할 수 있다.

> RAG는 모델에 지식을 주입하는 것이 아니라, 모델이 답할 수 있도록 필요한 정보를 찾아서 전달하는 시스템입니다.

## 이 글에서 다룰 문제

- RAG와 fine-tuning은 언제 어떤 것을 선택해야 할까요?
- 임베딩과 코사인 유사도는 어떻게 동작하나요?
- 청크 전략이 검색 품질에 어떤 영향을 미치나요?
- RAG에서 prompt injection을 어떻게 막나요?
- 검색 품질과 응답 품질을 어떻게 분리해서 측정할까요?

## Before / After: RAG 전후

| 상황 | RAG 없이 | RAG 적용 후 |
|------|----------|------------|
| 회사 내부 데이터 질문 | 모델이 모름 | 관련 문서 검색 후 답변 |
| 지식 업데이트 | fine-tuning 재훈련 필요 | 문서 인덱스만 업데이트 |
| 검색 결과 추적 | 어떤 문서를 봤는지 모름 | retrieved_chunks 로깅 |
| 외부 문서 injection | 문서 안의 지시가 모델 조작 | 구조화된 태그로 격리 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| 청크를 너무 크게 설정 | 관련 없는 내용이 섞임 | 도메인에 맞는 chunk size 실험 |
| 검색 결과를 그대로 프롬프트에 삽입 | prompt injection 위험 | `<document>` 태그로 구조화 격리 |
| 검색만 테스트하고 배포 | 응답 품질 모름 | question+chunks+answer 세트로 평가 |
| 단일 유사도 점수만 사용 | 관련 없는 chunk 포함 | 유사도 threshold 설정 |

## AI 팁: RAG 빠르게 만드는 방법

Claude나 GPT-4에 "Python으로 text-embedding-3-small과 코사인 유사도를 사용한 간단한 RAG 시스템을 만들어줘. 문서를 청킹하고, 임베딩 인덱스를 만들고, 질문에 가장 유사한 청크를 찾아서 GPT에 전달해줘"라고 요청하면 작동하는 코드를 얻을 수 있다. `numpy`로 코사인 유사도를 계산하고, 상위 k개 청크를 프롬프트에 포함하는 방식으로 시작한다. 프로덕션에서는 FAISS나 pgvector 같은 벡터 DB로 교체하면 된다.

## 운영 체크리스트

- [ ] 청크 크기와 overlap을 도메인에 맞게 실험했는가
- [ ] 유사도 threshold를 설정해 관련 없는 chunk를 걸러내는가
- [ ] 검색 결과를 구조화된 태그로 격리해 prompt injection을 방지하는가
- [ ] question, retrieved_chunks, answer를 함께 로깅하는가
- [ ] 검색 품질(retrieval_hit@k)과 응답 품질을 분리해서 측정하는가

## 처음 질문으로 돌아가기

- **RAG vs fine-tuning 선택 기준은?** 지식이 자주 바뀌거나 특정 문서를 근거로 답해야 하면 RAG. 모델 행동 자체를 바꿔야 하면 fine-tuning.
- **청크 전략이 중요한 이유는?** 너무 크면 관련 없는 내용이 섞이고, 너무 작으면 맥락이 끊긴다. 검색 품질의 핵심이 여기 있다.
- **prompt injection 방지는?** 검색 결과를 `<document>` 태그로 감싸고, 지시 채널과 명확히 분리한다.

## 정리

RAG는 모델에 지식을 주입하는 것이 아니라, 모델이 답할 수 있도록 필요한 정보를 찾아서 전달하는 시스템이다. 임베딩, 청킹, 검색, 프롬프트 조합의 각 단계를 이해하면 검색 품질과 응답 품질을 분리해서 개선할 수 있다.

## 참고 자료

- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/ai-web-dev-101/ko/04-rag-intro)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 AI 웹 개발 (1/7): AI API 첫 걸음
- 바이브코딩을 위한 AI 웹 개발 (2/7): 프롬프트 엔지니어링 기초
- 바이브코딩을 위한 AI 웹 개발 (3/7): AI 챗봇 만들기
- **바이브코딩을 위한 AI 웹 개발 (4/7): RAG 기초 (현재 글)**
- 바이브코딩을 위한 AI 웹 개발 (5/7): AI 에이전트
- 바이브코딩을 위한 AI 웹 개발 (6/7): 배포하기
- 바이브코딩을 위한 AI 웹 개발 (7/7): 평가와 개선
<!-- toc:end -->

Tags: 바이브코딩, AI 웹 개발, RAG, Embeddings, Vector Search
