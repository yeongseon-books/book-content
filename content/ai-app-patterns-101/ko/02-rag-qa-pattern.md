---
title: 'RAG Q&A 패턴 — 문서 기반 질의응답'
series: ai-app-patterns-101
episode: 2
language: ko
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- RAG
- Agent
- Python
last_reviewed: '2026-05-01'
---

# RAG Q&A 패턴 — 문서 기반 질의응답

> AI 앱 패턴 101 시리즈 (2/6)

RAG(Retrieval-Augmented Generation)는 LLM의 고질적인 문제 두 가지를 해결합니다. 첫째, LLM의 훈련 데이터 컷오프 이후 생성된 정보는 모릅니다. 둘째, 사내 문서, 개인 데이터 같은 비공개 정보는 처음부터 없습니다. RAG는 외부 문서를 검색해서 LLM 프롬프트에 주입함으로써 이 두 가지를 보완합니다.

이번 글에서는 RAG Q&A 파이프라인의 완전한 구현을 단계별로 만들어 봅니다.

다룰 내용은 다음과 같습니다.

- RAG의 두 단계: 인덱싱과 검색
- 완전한 RAG Q&A 체인 구현
- 답변 품질을 높이는 프롬프트 설계
- 출처(source) 추적과 함께 반환하기
- RAG가 실패하는 경우와 대응

---

## RAG의 두 단계

**인덱싱 단계** (오프라인): 문서를 청크로 나누고 임베딩해서 벡터 인덱스에 저장합니다.

**검색 단계** (온라인): 쿼리를 임베딩하고, 유사한 청크를 찾아, LLM 프롬프트에 주입합니다.

```
인덱싱: 문서 → 청킹 → 임베딩 → FAISS
검색: 쿼리 → 임베딩 → FAISS 검색 → 프롬프트 주입 → LLM → 답변
```

---

## 완전한 RAG Q&A 구현

```python
import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ── 임베딩 모델 ────────────────────────────────────────────────────────────
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# ── 샘플 문서 (실제로는 파일에서 로드) ──────────────────────────────────────
documents = [
    """
파이썬은 1991년 귀도 반 로섬이 만든 고수준 프로그래밍 언어입니다.
들여쓰기로 코드 블록을 구분하는 독특한 문법을 가집니다.
동적 타이핑과 자동 메모리 관리를 지원합니다.
웹 개발, 데이터 과학, 인공지능 분야에서 널리 사용됩니다.
""",
    """
파이썬의 주요 특징은 가독성입니다.
코드가 영어 문장처럼 읽히도록 설계되었습니다.
방대한 표준 라이브러리와 서드파티 패키지 생태계를 보유합니다.
pip 패키지 관리자로 수십만 개의 패키지를 설치할 수 있습니다.
""",
    """
파이썬의 주요 단점 중 하나는 실행 속도입니다.
인터프리터 언어이기 때문에 C나 자바보다 느립니다.
GIL(Global Interpreter Lock)로 인해 멀티스레드 성능에 제약이 있습니다.
모바일 앱 개발에는 잘 쓰이지 않습니다.
""",
    """
파이썬의 버전 역사: Python 2는 2000년, Python 3는 2008년 출시되었습니다.
Python 2는 2020년 1월 공식 지원이 종료되었습니다.
현재는 Python 3.10 이상 버전 사용을 권장합니다.
매년 10월에 새 버전이 출시됩니다.
""",
]

# ── 인덱싱 ────────────────────────────────────────────────────────────────
splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
chunks = []
for doc in documents:
    chunks.extend(splitter.split_text(doc))

vectorstore = FAISS.from_texts(texts=chunks, embedding=embedding_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ── RAG 체인 ──────────────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "아래 참고 문서를 바탕으로 질문에 답하세요.\n"
        "문서에 없는 내용은 '제공된 문서에서 찾을 수 없습니다'라고 하세요.\n"
        "추측하지 마세요.\n\n"
        "참고 문서:\n{context}",
    ),
    ("human", "{question}"),
])

def format_docs(docs: list) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

# ── 테스트 ────────────────────────────────────────────────────────────────
test_questions = [
    "파이썬은 누가 만들었나요?",
    "파이썬의 단점은 무엇인가요?",
    "파이썬 2는 언제 지원이 종료됐나요?",
    "파이썬으로 iOS 앱을 만들 수 있나요?",
    "러스트 언어의 특징은 무엇인가요?",  # 문서에 없는 내용
]

for question in test_questions:
    print(f"\n질문: {question}")
    answer = rag_chain.invoke(question)
    print(f"답변: {answer}")
```

---

## 출처 추적과 함께 반환하기

답변과 함께 어떤 문서에서 정보를 가져왔는지 반환하면 신뢰도가 높아집니다.

```python
import os
from typing import TypedDict

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_groq import ChatGroq

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents_with_metadata = [
    ("파이썬은 1991년 귀도 반 로섬이 만든 고수준 프로그래밍 언어입니다.", {"source": "python_intro.txt", "page": 1}),
    ("파이썬의 주요 특징은 가독성입니다. 코드가 영어 문장처럼 읽힙니다.", {"source": "python_features.txt", "page": 1}),
    ("파이썬의 주요 단점은 실행 속도입니다. 인터프리터 언어라 C보다 느립니다.", {"source": "python_cons.txt", "page": 1}),
]

texts = [text for text, _ in documents_with_metadata]
metadatas = [meta for _, meta in documents_with_metadata]

vectorstore = FAISS.from_texts(
    texts=texts,
    embedding=embedding_model,
    metadatas=metadatas,
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "다음 문서를 바탕으로 답하세요:\n{context}"),
    ("human", "{question}"),
])

def format_docs(docs: list) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

def get_sources(docs: list) -> list[str]:
    return [doc.metadata.get("source", "unknown") for doc in docs]

# 답변과 출처를 동시에 반환하는 체인
rag_with_sources = RunnableParallel(
    answer=(
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    ),
    sources=retriever | get_sources,
)

result = rag_with_sources.invoke("파이썬을 누가 만들었나요?")
print(f"답변: {result['answer']}")
print(f"출처: {result['sources']}")
```

---

## RAG가 실패하는 경우

**청크에 정보가 없을 때.** 쿼리와 관련된 청크가 검색되지 않으면 LLM은 hallucination을 일으킵니다. 프롬프트에 "문서에 없으면 모른다고 하라"는 지시가 중요합니다.

**청크 경계에서 정보가 잘릴 때.** 중요한 정보가 두 청크에 걸쳐 있으면 하나의 청크에서 전체 맥락을 얻지 못합니다. `chunk_overlap`을 충분히 설정하면 도움이 됩니다.

**쿼리와 문서의 표현 방식이 너무 다를 때.** "파이썬 느려?"라는 구어체 쿼리가 "인터프리터 언어 실행 속도"를 검색하지 못할 수 있습니다. 쿼리 확장(query expansion)이나 하이브리드 검색이 도움이 됩니다.

---

## 마무리

RAG Q&A 패턴은 LLM에 없는 지식을 외부에서 가져오는 가장 실용적인 방법입니다. 프롬프트에서 "문서에 없으면 모른다고 하라"는 지시를 명확히 하는 것이 hallucination 방지의 첫 단계입니다.

다음 글에서는 문서 어시스턴트 패턴을 다룹니다. 요약, 정보 추출, 분류 등 문서 처리에 특화된 패턴입니다.

<!-- toc:begin -->
## 시리즈 목차

- [챗봇 패턴 — 대화 이력 관리와 상태](./01-chatbot-pattern.md)
- **RAG Q&A 패턴 — 문서 기반 질의응답 (현재 글)**
- 문서 어시스턴트 — 요약, 추출, 분류 (예정)
- Agent + Tool 패턴 — 자율 도구 선택 (예정)
- 워크플로 자동화 — 다단계 체인 설계 (예정)
- Human-in-the-loop — 사람 개입 설계 패턴 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain RAG 튜토리얼](https://python.langchain.com/docs/use_cases/question_answering/)
- [RAG 논문 원본 (Lewis et al., 2020)](https://arxiv.org/abs/2005.11401)
- [FAISS VectorStore](https://python.langchain.com/docs/integrations/vectorstores/faiss/)

Tags: LLM, RAG, Agent, Python
