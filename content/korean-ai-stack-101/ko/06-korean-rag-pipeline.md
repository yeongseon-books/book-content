---
title: '한국어 RAG 파이프라인 조합하기'
series: korean-ai-stack-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- LLM
- Embeddings
- OCR
last_reviewed: '2026-05-01'
---

# 한국어 RAG 파이프라인 조합하기

## 이 글에서 답할 질문

- 한국어 RAG 파이프라인을 최소 구성으로 묶으려면 어떤 단계가 꼭 필요할까요?
- 문서 청킹, 임베딩, 검색, 생성 중 어느 단계가 가장 자주 품질 병목이 되나요?
- 검색된 문맥을 LLM에 넘길 때 어떤 형태로 정리해야 추측을 줄일 수 있을까요?
- 시리즈 앞선 글의 요소들이 실제로 어떻게 이어질까요?

> RAG의 품질은 한 번의 마법 같은 호출에서 나오지 않고, 청크 경계·검색 후보·문맥 전달 방식이 맞물려 쌓이는 합성 결과입니다.

> 한국어 AI 스택 101 시리즈 (6/6)

예제 코드: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/ko/06-korean-rag-pipeline)

마지막 글에서는 앞선 요소를 한 줄로 연결합니다. 한국어 문서를 청크로 나누고, KoSimCSE 임베딩으로 벡터화하고, FAISS로 상위 청크를 찾고, 마지막으로 Groq LLM에 검색된 문맥만 넘겨 답을 생성합니다.

---

## 핵심 흐름

![핵심 흐름](../../../assets/korean-ai-stack-101/06/06-01-core-flow.ko.png)
---

## 왜 단순한 파이프라인이 더 많이 알려 주는가

청킹 함수, 임베딩, 검색, 생성이 드러나는 코드는 품질 문제를 훨씬 빨리 좁혀 줍니다. 질문이 "결제는 됐는데 주문 내역이 없다"일 때 어떤 청크가 선택되는지 먼저 보고 답변을 읽어야 합니다.

---

## 최소 실행 예제

```python
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BM-K/KoSimCSE-roberta-multitask')
chunks = [
    '결제는 성공했지만 주문이 생성되지 않은 경우에는 주문 동기화 지연 여부를 먼저 확인합니다.',
    '결제 실패 문의는 카드 승인 실패와 주문 저장 실패를 분리해서 대응해야 합니다.',
]
vectors = model.encode(chunks, normalize_embeddings=True).astype('float32')
index = faiss.IndexFlatIP(vectors.shape[1])
index.add(vectors)

question = '결제는 됐는데 주문 내역이 없을 때 어떤 순서로 점검해야 하나요?'
query_vec = model.encode([question], normalize_embeddings=True).astype('float32')
distances, indices = index.search(query_vec, 2)
print(distances, indices)
```

---

## 이 코드에서 봐야 할 것

- 문서를 **청크 목록**으로 분리합니다.
- 검색된 청크를 점수와 함께 출력합니다.
- 시스템 메시지에서 문맥에 없는 내용은 추측하지 말라고 못 박습니다.
- 전체 `main.py`는 검색된 문맥과 생성된 답변을 모두 보여 줍니다.

---

## 실무에서 헷갈리는 지점

- 좋은 LLM을 붙였다고 RAG가 좋아지는 것은 아닙니다.
- 임베딩 모델 선택만큼 청킹 전략도 중요합니다.
- 민감 정보는 외부 API로 보내기 전에 마스킹이 필요할 수 있습니다.

---

## 체크리스트

- [ ] 청크 단위를 먼저 정하고 검색 결과를 직접 읽어 본다.
- [ ] 검색 점수와 선택된 출처를 항상 함께 기록한다.
- [ ] LLM 프롬프트에 추측 금지 규칙을 명시한다.
- [ ] 민감 정보 마스킹 규칙을 생성 단계 앞에 둔다.

---

## 마무리

이 시리즈의 핵심은 특정 도구 이름이 아니라, 한국어 문서 처리 단계를 분해해서 보는 습관입니다. 임베딩 비교, 문장 검색, 다국어 검색, OCR, 생성 API를 차례로 쌓아 올리면 한국어 RAG 파이프라인을 더 차분하게 설계할 수 있습니다.

<!-- blog-only:start -->
시리즈 마지막 글입니다. 1편의 비교 기준으로 돌아가 자신의 문서셋에 맞게 이 파이프라인을 변형해 보세요.
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [KoSimCSE로 문장 유사도 구현하기](./02-kosimcse-similarity.md)
- [BGE-M3 다국어 임베딩 실전](./03-bge-m3-multilingual.md)
- [CLOVA OCR API로 문서 텍스트 추출](./04-clova-ocr.md)
- [HyperCLOVA X와 Solar API 사용하기](./05-hyperclova-solar-api.md)
- **한국어 RAG 파이프라인 조합하기 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [BM-K/KoSimCSE-roberta-multitask](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [Groq API reference](https://console.groq.com/docs/api-reference)

Tags: Korean NLP, LLM, Embeddings, OCR
