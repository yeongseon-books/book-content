---
title: 'KoSimCSE로 문장 유사도 구현하기'
series: korean-ai-stack-101
episode: 2
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

# KoSimCSE로 문장 유사도 구현하기

## 이 글에서 답할 질문

- 한국어 문장 검색에서 KoSimCSE가 바로 체감되는 지점은 어디일까요?
- FAQ 질문만 인덱싱해도 실무 검색의 첫 버전을 만들 수 있는 이유는 무엇일까요?
- 정규화된 임베딩과 `IndexFlatIP` 조합을 왜 많이 쓰는 걸까요?
- 검색 점수가 높아도 엉뚱한 결과가 나오는 경우는 어디서 생길까요?

> 문장 유사도 검색의 첫 버전은 거창한 체인보다, 좋은 문장 표현과 단순한 인덱스를 정확히 묶는 데서 시작합니다.

> 한국어 AI 스택 101 시리즈 (2/6)

예제 코드: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/ko/02-kosimcse-similarity)

이 글에서는 한국어 FAQ 검색처럼 짧은 문장 중심 태스크에 KoSimCSE를 바로 붙여 봅니다. 앞 글이 모델 비교였다면, 이번 글은 "질문을 벡터로 바꾸고 가장 비슷한 질문을 찾는다"는 가장 기본적인 검색 루프를 손으로 만들어 보는 단계입니다.

---

## 핵심 흐름

![핵심 흐름](../../../assets/korean-ai-stack-101/02/02-01-core-flow.ko.png)
---

## 왜 FAQ 질문만 먼저 인덱싱할까

질문과 답변을 한 번에 임베딩하면 어디서 검색이 어긋나는지 읽기 어렵습니다. 첫 버전은 질문만 인덱싱하고, 검색된 질문에 연결된 답변을 붙여 보는 편이 디버깅이 쉽습니다.

---

## 최소 실행 예제

```python
import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = 'BM-K/KoSimCSE-roberta-multitask'
FAQS = [
    {'category': 'account', 'question': '비밀번호나 패스워드를 재설정하고 싶어요.'},
    {'category': 'billing', 'question': '결제는 됐는데 주문 내역이 보이지 않습니다.'},
    {'category': 'shipping', 'question': '배송 상태는 어디에서 확인하나요?'},
]

model = SentenceTransformer(MODEL_NAME)
embeddings = model.encode([item['question'] for item in FAQS], normalize_embeddings=True).astype('float32')
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

query = '로그인 비밀번호를 다시 설정하고 싶어요.'
query_vec = model.encode([query], normalize_embeddings=True).astype('float32')
distances, indices = index.search(query_vec, 2)
print(distances, indices)
```

```
출력 결과
[[0.92722106 0.27328622]] [[0 1]]
```

---

## 이 코드에서 봐야 할 것

- 답변이 아니라 **질문 문장**을 인덱싱합니다.
- `normalize_embeddings=True`와 `IndexFlatIP`를 같이 쓰면 코사인 유사도를 단순하게 계산할 수 있습니다.
- 질의를 여러 표현으로 바꿔도 상위 결과가 비슷하게 유지되는지 봐야 합니다.
- 상위 1개만 보지 말고 2~3개 후보를 함께 출력해야 오답 패턴이 보입니다.

---

## 실무에서 헷갈리는 지점

- 문장 유사도 검색은 생성이 아닙니다. 검색과 답변 생성을 분리해서 봐야 합니다.
- 높은 점수 하나보다 후보 간 간격과 실제 문장 의미를 함께 봐야 합니다.
- FAQ용 설정을 긴 문서 검색에 그대로 가져가면 안 됩니다.

---

## 체크리스트

- [ ] 검색 대상이 질문인지 답변인지 먼저 고정한다.
- [ ] 질의 표현을 3개 이상 바꿔 본다.
- [ ] 상위 결과 2~3개를 함께 출력한다.
- [ ] 생성 단계를 붙이기 전에 검색 단계만 따로 검증한다.

---

## 마무리

KoSimCSE 예제의 핵심은 검색 루프를 투명하게 유지하는 데 있습니다. 이 기준점이 있어야 다음 단계에서 다국어 모델이나 하이브리드 검색으로 확장해도 비교가 쉽습니다.

<!-- toc:begin -->
## 시리즈 목차

- [한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- **KoSimCSE로 문장 유사도 구현하기 (현재 글)**
- BGE-M3 다국어 임베딩 실전 (예정)
- CLOVA OCR API로 문서 텍스트 추출 (예정)
- HyperCLOVA X와 Solar API 사용하기 (예정)
- 한국어 RAG 파이프라인 조합하기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [BM-K/KoSimCSE-roberta-multitask](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [SentenceTransformers semantic search examples](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)

Tags: Korean NLP, LLM, Embeddings, OCR
