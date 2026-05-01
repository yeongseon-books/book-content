---
title: 'Building sentence similarity search with KoSimCSE'
series: korean-ai-stack-101
episode: 2
language: en
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

# Building sentence similarity search with KoSimCSE

> Korean AI Stack 101 (2/6)

Example code: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/en/02-kosimcse-similarity)

The previous post compared three Korean embedding models. This post builds a working Korean sentence similarity search system with KoSimCSE, moving from benchmark comparison to practical implementation.

Topics:

- installing and initializing KoSimCSE
- encoding sentences and computing similarity
- storing Korean documents in a FAISS index
- searching with Korean queries
- integrating into a LangChain FAQ retrieval chain

---

<!-- ebook-only:start -->

**The key idea**: KoSimCSE uses contrastive learning to capture Korean similarity. Same-meaning sentence pairs are pushed together; different ones are pushed apart.

## Where this chapter fits

This is chapter 2 of 6 in the series.
The previous chapter covered **Korean embedding models compared — KoSimCSE, BGE-M3, Solar**.
After this chapter, the next one moves on to **BGE-M3 multilingual embedding in practice**.
<!-- ebook-only:end -->

## Installation

```bash
pip install sentence-transformers faiss-cpu
```

The first run downloads model weights from HuggingFace — approximately 500 MB.

---

## Basic similarity calculation

```python
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BM-K/KoSimCSE-roberta-multitask")

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Dot product of normalized vectors equals cosine similarity."""
    return float(np.dot(a, b))

sentences = [
    "오늘 점심에 비빔밥을 먹었다.",       # I had bibimbap for lunch today.
    "오늘 낮에 비빔밥으로 식사를 했다.",   # I had a bibimbap meal at noon today.
    "주식 시장이 오늘 크게 올랐다.",       # The stock market rose sharply today.
    "한국 전통 음식 중 하나가 비빔밥이다.",# Bibimbap is one of Korea's traditional dishes.
    "파이썬으로 웹 애플리케이션을 개발했다.", # I built a web app with Python.
]

embeddings = model.encode(sentences, normalize_embeddings=True)
print(f"embedding shape: {embeddings.shape}")  # (5, 768)

query = embeddings[0]
print(f"\nreference sentence: {sentences[0]}")
print("-" * 60)
for sent, emb in zip(sentences[1:], embeddings[1:]):
    sim = cosine_sim(query, emb)
    print(f"[{sim:.3f}] {sent}")
```

---

## Building a FAISS index

```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BM-K/KoSimCSE-roberta-multitask")

faq_documents = [
    {"id": 1, "question": "비밀번호를 잊어버렸습니다.", "answer": "로그인 화면에서 '비밀번호 찾기'를 클릭하세요."},
    {"id": 2, "question": "회원 탈퇴는 어떻게 하나요?", "answer": "설정 > 계정 관리 > 탈퇴하기를 선택하세요."},
    {"id": 3, "question": "결제가 실패했습니다.", "answer": "카드 정보를 확인하고 다시 시도해 주세요."},
    {"id": 4, "question": "환불은 얼마나 걸리나요?", "answer": "영업일 기준 3~5일 이내에 처리됩니다."},
    {"id": 5, "question": "배송 추적은 어디서 하나요?", "answer": "마이페이지 > 주문 내역에서 확인할 수 있습니다."},
    {"id": 6, "question": "계정 정보를 변경하고 싶습니다.", "answer": "설정 > 프로필 편집에서 변경할 수 있습니다."},
    {"id": 7, "question": "앱이 자꾸 충돌합니다.", "answer": "앱을 최신 버전으로 업데이트하거나 캐시를 삭제해 보세요."},
    {"id": 8, "question": "상품을 교환하고 싶습니다.", "answer": "수령 후 7일 이내에 고객센터를 통해 교환 신청이 가능합니다."},
    {"id": 9, "question": "할인 코드 입력은 어디서 하나요?", "answer": "결제 화면의 '쿠폰/할인코드 입력' 칸에 입력하세요."},
    {"id": 10, "question": "두 기기에서 동시에 로그인할 수 있나요?", "answer": "최대 3대의 기기에서 동시 로그인이 가능합니다."},
]

questions = [doc["question"] for doc in faq_documents]
question_embeddings = model.encode(questions, normalize_embeddings=True)
embeddings_f32 = question_embeddings.astype(np.float32)

dim = embeddings_f32.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(embeddings_f32)
print(f"index ready: {index.ntotal} documents")
```

---

## Searching with Korean queries

KoSimCSE handles paraphrase variation well — "패스워드" (English loanword for password) matches "비밀번호" (Korean word for password) with high similarity.

```python
def search_faq(query: str, k: int = 3) -> list[dict]:
    """Return the k most similar FAQ entries for a Korean query."""
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

test_queries = [
    "패스워드를 분실했어요",            # paraphrase: 비밀번호를 잊어버렸습니다
    "주문한 물건 배송 확인하고 싶어요",  # paraphrase: 배송 추적
    "결제가 안 돼요",                   # paraphrase: 결제가 실패했습니다
    "앱이 꺼집니다",                    # colloquial: 앱이 충돌합니다
    "탈퇴하고 싶어요",                  # shorter: 회원 탈퇴
]

for query in test_queries:
    print(f"\nquery: {query}")
    results = search_faq(query, k=2)
    for r in results:
        print(f"  [{r['score']:.3f}] Q: {r['question']}")
        print(f"          A: {r['answer']}")
```

---

## Integrating into a LangChain retrieval chain

```python
import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

embedding_model = HuggingFaceEmbeddings(
    model_name="BM-K/KoSimCSE-roberta-multitask",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

texts = [doc["question"] + " " + doc["answer"] for doc in faq_documents]
vectorstore = FAISS.from_texts(texts=texts, embedding=embedding_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Answer the customer question using the FAQ documents below.\n"
        "Be polite and clear.\n\n"
        "FAQ documents:\n{context}",
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
print(f"answer: {answer}")
```

---

## Conclusion

KoSimCSE maps paraphrase variation — "패스워드" and "비밀번호", "충돌" and "꺼짐" — to nearby vectors without any special handling. Wrapping it with LangChain's `HuggingFaceEmbeddings` and `FAISS` connects it to any existing retrieval chain in minutes.

The next post covers BGE-M3's multilingual capabilities and hybrid dense+sparse retrieval.

<!-- blog-only:start -->
Next: [BGE-M3 multilingual embedding in practice](./03-bge-m3-multilingual.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- [Korean embedding models compared — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- **Building sentence similarity search with KoSimCSE (current)**
- BGE-M3 multilingual embedding in practice (upcoming)
- Document text extraction with CLOVA OCR API (upcoming)
- Using HyperCLOVA X and Solar API (upcoming)
- Assembling a Korean RAG pipeline (upcoming)

<!-- toc:end -->

---

## References

- [KoSimCSE on HuggingFace](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [FAISS documentation](https://faiss.ai/)
- [SentenceTransformers encoding guide](https://www.sbert.net/docs/usage/computing_sentence_embeddings.html)

Tags: Korean NLP, LLM, Embeddings, OCR
