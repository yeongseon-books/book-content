---
title: 'KoSimCSE로 문장 유사도 구현하기'
series: korean-ai-stack-101
episode: 2
language: ko
status: draft
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

> 한국어 AI 스택 101 시리즈 (2/6)

예제 코드: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/ko/02-kosimcse-similarity)

앞 글에서 세 가지 한국어 임베딩 모델을 비교했습니다. 이번 글에서는 KoSimCSE를 사용해서 실제로 동작하는 한국어 문장 유사도 검색 시스템을 만듭니다. 이론 비교에서 실용 구현으로 넘어가는 단계입니다.

다룰 내용은 다음과 같습니다.

- KoSimCSE 모델 설치와 초기화
- 문장을 벡터로 변환하고 유사도 계산
- FAISS 인덱스에 한국어 문서 저장
- 한국어 쿼리로 유사 문서 검색
- 실제 FAQ 검색 시스템 구현

---

<!-- ebook-only:start -->

이 장의 핵심: **KoSimCSE는 대조 학습으로 한국어 유사도를 잡는다.** 같은 의미의 문장 쌍을 가깝게, 다른 문장 쌍을 멀게 학습한다.

## 이 장의 위치

이 글은 시리즈 6편 중 2번째 장입니다.
앞 장에서는 **한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar**을 다뤘습니다.
이 장을 마치면 다음 장에서 **BGE-M3 다국어 임베딩 실전**으로 이어집니다.
<!-- ebook-only:end -->

## KoSimCSE 설치

```bash
pip install sentence-transformers faiss-cpu
```

첫 실행 시 HuggingFace에서 모델 가중치를 다운로드합니다. 약 500MB입니다.

---

## 기본 유사도 계산

```python
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BM-K/KoSimCSE-roberta-multitask")

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """정규화된 벡터의 내적 = 코사인 유사도."""
    return float(np.dot(a, b))

# 문장 인코딩 (normalize_embeddings=True로 정규화)
sentences = [
    "오늘 점심에 비빔밥을 먹었다.",
    "오늘 낮에 비빔밥으로 식사를 했다.",
    "주식 시장이 오늘 크게 올랐다.",
    "한국 전통 음식 중 하나가 비빔밥이다.",
    "파이썬으로 웹 애플리케이션을 개발했다.",
]

embeddings = model.encode(sentences, normalize_embeddings=True)
print(f"임베딩 형태: {embeddings.shape}")  # (5, 768)

# 첫 번째 문장과 나머지 문장들의 유사도
query = embeddings[0]
print(f"\n기준 문장: {sentences[0]}")
print("-" * 60)
for i, (sent, emb) in enumerate(zip(sentences[1:], embeddings[1:]), start=1):
    sim = cosine_sim(query, emb)
    print(f"[{sim:.3f}] {sent}")
```

---

## FAISS 인덱스 구성

```python
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BM-K/KoSimCSE-roberta-multitask")

# 한국어 FAQ 문서
faq_documents = [
    {"id": 1, "question": "비밀번호를 잊어버렸습니다.", "answer": "로그인 화면에서 '비밀번호 찾기'를 클릭하세요."},
    {"id": 2, "question": "회원 탈퇴는 어떻게 하나요?", "answer": "설정 > 계정 관리 > 탈퇴하기를 선택하세요."},
    {"id": 3, "question": "결제가 실패했습니다.", "answer": "카드 정보를 확인하고 다시 시도해 주세요. 문제가 지속되면 고객센터에 문의하세요."},
    {"id": 4, "question": "환불은 얼마나 걸리나요?", "answer": "환불 신청 후 영업일 기준 3~5일 이내에 처리됩니다."},
    {"id": 5, "question": "배송 추적은 어디서 하나요?", "answer": "마이페이지 > 주문 내역에서 운송장 번호를 확인할 수 있습니다."},
    {"id": 6, "question": "계정 정보를 변경하고 싶습니다.", "answer": "설정 > 프로필 편집에서 이름, 이메일, 전화번호를 변경할 수 있습니다."},
    {"id": 7, "question": "앱이 자꾸 충돌합니다.", "answer": "앱을 최신 버전으로 업데이트하거나 캐시를 삭제해 보세요."},
    {"id": 8, "question": "상품을 교환하고 싶습니다.", "answer": "수령 후 7일 이내에 고객센터를 통해 교환 신청이 가능합니다."},
    {"id": 9, "question": "할인 코드 입력은 어디서 하나요?", "answer": "결제 화면의 '쿠폰/할인코드 입력' 칸에 입력하세요."},
    {"id": 10, "question": "두 대의 기기에서 동시에 로그인할 수 있나요?", "answer": "최대 3대의 기기에서 동시 로그인이 가능합니다."},
]

# 질문 텍스트만 추출해서 인코딩
questions = [doc["question"] for doc in faq_documents]
question_embeddings = model.encode(questions, normalize_embeddings=True)
embeddings_f32 = question_embeddings.astype(np.float32)

# FAISS 인덱스 (내적 = 코사인 유사도, 정규화된 벡터 기준)
dim = embeddings_f32.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(embeddings_f32)
print(f"인덱스 구성 완료: {index.ntotal}개 문서")
```

---

## 한국어 쿼리 검색

```python
def search_faq(query: str, k: int = 3) -> list[dict]:
    """한국어 쿼리로 가장 유사한 FAQ를 반환."""
    query_vec = model.encode([query], normalize_embeddings=True).astype(np.float32)
    distances, indices = index.search(query_vec, k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        doc = faq_documents[idx]
        results.append({
            "score": float(dist),
            "question": doc["question"],
            "answer": doc["answer"],
        })
    return results

# 다양한 표현으로 테스트
test_queries = [
    "패스워드를 분실했어요",          # 비밀번호 분실 (다른 표현)
    "주문한 물건 배송 확인하고 싶어요",  # 배송 추적
    "결제가 안 돼요",                  # 결제 실패
    "앱이 꺼집니다",                   # 앱 충돌 (구어체)
    "탈퇴하고 싶어요",                 # 회원 탈퇴 (짧은 표현)
]

for query in test_queries:
    print(f"\n쿼리: {query}")
    results = search_faq(query, k=2)
    for r in results:
        print(f"  [{r['score']:.3f}] Q: {r['question']}")
        print(f"          A: {r['answer']}")
```

---

## LangChain Retriever로 통합

KoSimCSE를 LangChain 체인에 연결합니다.

```python
import os
from typing import Any

import numpy as np
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

# KoSimCSE 임베딩을 LangChain HuggingFaceEmbeddings로 감싸기
embedding_model = HuggingFaceEmbeddings(
    model_name="BM-K/KoSimCSE-roberta-multitask",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# 문서 텍스트로 FAISS 벡터스토어 구성
texts = [doc["question"] + " " + doc["answer"] for doc in faq_documents]
vectorstore = FAISS.from_texts(texts=texts, embedding=embedding_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# RAG 체인
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "아래 FAQ 문서를 참고해서 고객 질문에 답하세요.\n"
        "친절하고 명확하게 답변하세요.\n\n"
        "FAQ 문서:\n{context}",
    ),
    ("human", "{question}"),
])

def format_docs(docs: list) -> str:
    return "\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("비밀번호를 까먹었는데 어떻게 하면 되나요?")
print(f"답변: {answer}")
```

---

## 마무리

KoSimCSE는 설치가 간단하고 한국어 문장 유사도에서 신뢰할 수 있는 성능을 보입니다. "패스워드"와 "비밀번호", "충돌"과 "꺼짐" 같은 동의어/유사 표현도 높은 유사도로 연결합니다. LangChain의 `HuggingFaceEmbeddings`와 `FAISS`를 함께 쓰면 RAG 파이프라인에 바로 통합할 수 있습니다.

다음 글에서는 BGE-M3의 다국어 임베딩 기능과 하이브리드 검색을 다룹니다.

<!-- blog-only:start -->
다음 글: [BGE-M3 다국어 임베딩 실전](./03-bge-m3-multilingual.md)
<!-- blog-only:end -->

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

- [KoSimCSE HuggingFace 페이지](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [FAISS 공식 문서](https://faiss.ai/)
- [SentenceTransformers 인코딩 가이드](https://www.sbert.net/docs/usage/computing_sentence_embeddings.html)

Tags: Korean NLP, LLM, Embeddings, OCR
