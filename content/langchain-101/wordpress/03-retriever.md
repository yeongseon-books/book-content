---
title: "바이브코딩을 위한 LangChain (3/6): Retriever — 문서 검색과 컨텍스트 주입"
series: langchain-101
episode: 3
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LangChain
- RAG
- Retriever
- Python
---

# 바이브코딩을 위한 LangChain (3/6): Retriever — 문서 검색과 컨텍스트 주입

이 글은 **바이브코딩을 위한 LangChain** 시리즈의 세 번째 글입니다. LangChain의 Retriever 인터페이스로 문서를 검색하고 LLM 체인에 컨텍스트를 주입하는 방법을 다룹니다.

---

Prompt와 LLM 체인을 만들었습니다. 이제 LLM에게 "내 문서에서 찾아줘"라는 능력을 줘야 합니다. RAG(Retrieval-Augmented Generation)가 바로 그것입니다. LangChain의 Retriever는 FAISS, Chroma, Pinecone 등 다양한 벡터 스토어를 같은 인터페이스로 사용할 수 있게 합니다.

바이브코딩으로 AI에게 "RAG 만들어줘"라고 하면 코드가 나옵니다. Retriever가 Runnable이기 때문에 파이프로 연결된다는 것, 검색 결과를 포맷팅하는 방법을 모르면 파이프라인을 수정하기 어렵습니다.

> "Retriever는 Runnable이므로 체인에 파이프로 연결할 수 있습니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. VectorStore와 Retriever의 차이가 무엇인가요?
2. `as_retriever(search_kwargs={"k": 3})`에서 k의 의미가 무엇인가요?
3. 검색 결과 Document 객체에서 텍스트를 어떻게 추출하나요?
4. MultiQueryRetriever가 단순 Retriever와 어떻게 다른가요?
5. Retriever를 RAG 체인에 연결할 때 RunnablePassthrough가 왜 필요한가요?

---

## FAISS Retriever 구성

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# 인덱스 구성
embeddings = OpenAIEmbeddings()
texts = ["문서1 내용", "문서2 내용", "문서3 내용"]
vectorstore = FAISS.from_texts(texts, embeddings)

# Retriever 생성
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3},
)
```

## 검색 결과 포맷팅

```python
def format_docs(docs: list[Document]) -> str:
    return "\n\n---\n\n".join(doc.page_content for doc in docs)
```

## RAG 체인 구성

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "다음 컨텍스트를 기반으로 질문에 답하세요. 컨텍스트에 없는 내용은 모른다고 하세요.\n\n컨텍스트:\n{context}"),
    ("human", "{question}"),
])

llm = ChatOpenAI(model="gpt-4o-mini")

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("문서에서 찾고 싶은 내용")
```

## MultiQueryRetriever

단일 쿼리 대신 여러 쿼리로 검색 범위를 넓힙니다.

```python
from langchain.retrievers.multi_query import MultiQueryRetriever

mq_retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=ChatOpenAI(model="gpt-4o-mini"),
)
```

---

## Before / After

| 항목 | Before (직접 검색) | After (Retriever) |
|------|------------------|--------------------|
| 벡터 스토어 전환 | 코드 전면 수정 | as_retriever() 인터페이스 |
| 검색 결과 포맷 | 수동 처리 | format_docs 함수 |
| 검색 품질 | 단일 쿼리 | MultiQueryRetriever로 향상 |
| 체인 연결 | 별도 단계 | `|` 파이프 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| retriever 없이 직접 search | Runnable 미호환 | as_retriever() 사용 |
| Document 객체 그대로 전달 | 프롬프트 파싱 오류 | format_docs로 텍스트 추출 |
| k 값 너무 큼 | 컨텍스트 과다 | k=3~5 권장 |
| 질문 RunnablePassthrough 없음 | context만 전달 | 양쪽 모두 딕셔너리로 구성 |

---

## AI 활용 팁

```
FAISS 벡터 스토어로 Retriever를 만들고 RAG 체인에 연결해줘.
검색 결과 Document 리스트를 format_docs 함수로 텍스트로 변환해줘.
RAG 체인은 context(검색 결과)와 question(원본 질문)을 모두 프롬프트에 전달해야 해.
컨텍스트에 없는 내용은 모른다고 답하는 시스템 프롬프트를 포함해줘.
```

---

## 체크리스트

- [ ] FAISS 또는 Chroma 벡터 스토어 구성
- [ ] as_retriever(search_kwargs={"k": 3}) 설정
- [ ] format_docs 함수로 Document → 텍스트 변환
- [ ] RAG 체인에 context + question 딕셔너리 구성
- [ ] 시스템 프롬프트에 "모른다" 처리 포함
- [ ] MultiQueryRetriever 검토

---

## 처음 질문으로 돌아가기

"RAG에서 Retriever가 왜 별도 인터페이스인가요?" — Retriever가 Runnable을 구현하기 때문에 파이프로 체인에 직접 연결할 수 있습니다. 벡터 스토어를 바꿔도 체인 코드는 그대로입니다. as_retriever()가 그 추상화 레이어입니다.

---

## 정리

- Retriever는 Runnable이므로 파이프(`|`)로 체인에 직접 연결한다
- `as_retriever(search_kwargs={"k": 3})`로 검색 수를 설정한다
- format_docs로 Document 리스트를 프롬프트에 주입할 텍스트로 변환한다
- MultiQueryRetriever로 여러 쿼리를 생성해 검색 범위를 넓힌다

---

## 참고 자료

- [LangChain Retriever 문서](https://python.langchain.com/docs/concepts/retrievers/)
- [FAISS 벡터 스토어](https://python.langchain.com/docs/integrations/vectorstores/faiss/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- FAISS Retriever 구성
- 검색 결과 포맷팅
- RAG 체인 구성
- MultiQueryRetriever
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LangChain, RAG, Retriever, Python
