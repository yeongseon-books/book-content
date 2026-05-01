---
title: 'Retriever — 문서 검색과 컨텍스트 주입'
series: langchain-101
episode: 3
language: ko
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LangChain
- LCEL
- Python
- LLM
last_reviewed: '2026-05-01'
---

# Retriever — 문서 검색과 컨텍스트 주입

> LangChain 101 시리즈 (3/6)

Retriever는 쿼리를 받아 관련 문서 목록을 반환하는 컴포넌트입니다. LangChain의 Retriever 인터페이스는 `get_relevant_documents(query)` 메서드 하나로 정의됩니다. 뒤에 어떤 검색 시스템이 있든 — FAISS, Chroma, Elasticsearch — 체인에서는 같은 방식으로 사용합니다.

이번 글에서는 FAISS 기반 Retriever를 만들고, 그 결과를 프롬프트에 주입하는 RAG 패턴의 기본 형태를 구현합니다.

다룰 내용은 다음과 같습니다.

- FAISS VectorStore와 Retriever 만들기
- `as_retriever()`와 검색 파라미터
- Retriever를 체인에 연결하기
- 검색 결과를 컨텍스트로 주입하는 패턴
- 여러 문서를 하나의 컨텍스트 문자열로 합치기

---

## FAISS VectorStore 만들기

LangChain은 `FAISS` 클래스를 통해 벡터 저장소를 추상화합니다. 문서 목록과 임베딩 모델만 넘기면 인덱스를 자동으로 구성합니다.

```bash
pip install langchain langchain-community faiss-cpu sentence-transformers langchain-groq
```

```python
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    "FAISS는 Facebook AI Research에서 개발한 고속 벡터 검색 라이브러리입니다.",
    "코사인 유사도는 두 벡터의 방향 유사성을 측정합니다.",
    "임베딩 모델은 텍스트를 고차원 벡터 공간에 투영합니다.",
    "sentence-transformers는 문장 수준 임베딩에 특화된 라이브러리입니다.",
    "벡터 검색은 키워드 검색이 놓치는 의미적 유사성을 잡아냅니다.",
    "RAG는 검색된 문서를 LLM 프롬프트에 결합하는 패턴입니다.",
    "청크 전략은 긴 문서를 임베딩 가능한 단위로 나누는 방법입니다.",
]

vectorstore = FAISS.from_texts(
    texts=documents,
    embedding=embedding_model,
)

print(f"인덱스 벡터 수: {vectorstore.index.ntotal}")
```

---

## Retriever 만들기

`as_retriever()`는 VectorStore를 Retriever 인터페이스로 감쌉니다. 검색 방식과 결과 수를 파라미터로 지정합니다.

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",  # 기본값: 코사인 유사도
    search_kwargs={"k": 3},    # 반환할 문서 수
)

docs = retriever.invoke("벡터 검색의 원리")

for i, doc in enumerate(docs):
    print(f"[{i}] {doc.page_content}")
```

`search_type` 옵션은 세 가지입니다.

- `"similarity"`: 코사인 유사도 기반, 상위 k개 반환
- `"mmr"`: 최대 한계 관련성 — 다양성과 관련성을 함께 고려
- `"similarity_score_threshold"`: 임계값 이상의 유사도를 가진 문서만 반환

```python
# MMR 예시 — 다양성 강조
retriever_mmr = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 10, "lambda_mult": 0.5},
)
```

---

## Retriever를 체인에 연결하기

Retriever의 출력(문서 목록)을 LLM 프롬프트의 컨텍스트로 주입하는 패턴입니다.

```python
import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

def format_docs(docs: list) -> str:
    """문서 목록을 하나의 컨텍스트 문자열로 합칩니다."""
    return "\n\n".join(doc.page_content for doc in docs)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    "FAISS는 Facebook AI Research에서 개발한 고속 벡터 검색 라이브러리입니다.",
    "코사인 유사도는 두 벡터의 방향 유사성을 측정합니다.",
    "임베딩 모델은 텍스트를 고차원 벡터 공간에 투영합니다.",
    "sentence-transformers는 문장 수준 임베딩에 특화된 라이브러리입니다.",
    "벡터 검색은 키워드 검색이 놓치는 의미적 유사성을 잡아냅니다.",
    "RAG는 검색된 문서를 LLM 프롬프트에 결합하는 패턴입니다.",
]

vectorstore = FAISS.from_texts(texts=documents, embedding=embedding_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "다음 문서를 참고해서 질문에 답하세요. 문서에 없는 내용은 모른다고 하세요.\n\n"
        "문서:\n{context}",
    ),
    ("human", "{question}"),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

# RAG 체인
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

questions = [
    "FAISS는 무엇인가요?",
    "RAG 패턴은 어떻게 동작하나요?",
    "임베딩 모델은 무엇을 하나요?",
]

for question in questions:
    print(f"\n질문: {question}")
    answer = rag_chain.invoke(question)
    print(f"답변: {answer}")
```

핵심 부분은 체인 입력 딕셔너리입니다.

```python
{
    "context": retriever | format_docs,
    "question": RunnablePassthrough(),
}
```

`retriever | format_docs`는 쿼리를 받아 → 관련 문서를 검색하고 → 문자열로 합칩니다. `RunnablePassthrough()`는 쿼리를 그대로 `"question"` 키로 넘깁니다.

---

## VectorStore 저장과 불러오기

VectorStore도 디스크에 저장할 수 있습니다. 인덱스를 한 번만 만들고 재사용할 때 유용합니다.

```python
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    "FAISS는 Facebook AI Research에서 개발한 고속 벡터 검색 라이브러리입니다.",
    "RAG는 검색된 문서를 LLM 프롬프트에 결합하는 패턴입니다.",
]

vectorstore = FAISS.from_texts(texts=documents, embedding=embedding_model)

# 저장
vectorstore.save_local("faiss_store")
print("저장 완료")

# 불러오기
loaded_store = FAISS.load_local(
    "faiss_store",
    embeddings=embedding_model,
    allow_dangerous_deserialization=True,
)
print(f"불러오기 완료: {loaded_store.index.ntotal}개 벡터")

# 검색 테스트
results = loaded_store.similarity_search("벡터 검색", k=1)
print(f"\n검색 결과: {results[0].page_content}")
```

---

## 마무리

Retriever를 만들고 RAG 체인에 연결하는 방법을 익혔습니다. `context: retriever | format_docs, question: RunnablePassthrough()` 패턴은 LangChain RAG 코드에서 가장 자주 나오는 구조입니다.

다음 글에서는 Tool Calling을 다룹니다. LLM이 외부 함수를 호출하고 그 결과를 응답에 반영하는 방법입니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangChain 소개 — LCEL과 Runnable 기본](./01-lcel-runnable-basics.md)
- [Prompt와 LLM Chain — 체인 첫 번째 구성](./02-prompt-llm-chain.md)
- **Retriever — 문서 검색과 컨텍스트 주입 (현재 글)**
- Tool Calling — 외부 도구 연결하기 (예정)
- Streaming — 실시간 출력 처리 (예정)
- 실전 체인 조립 — 컴포넌트를 하나로 연결하기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain Retriever 인터페이스](https://python.langchain.com/docs/modules/data_connection/retrievers/)
- [FAISS VectorStore](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- [RAG 체인 빌드하기](https://python.langchain.com/docs/use_cases/question_answering/)

Tags: LangChain, LCEL, Python, LLM
