---
title: "AI App Patterns 101 (2/6): RAG Q&A 패턴 — 문서 기반 질의응답"
series: ai-app-patterns-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LLM
- RAG
- Agent
- Python
last_reviewed: '2026-05-15'
seo_description: RAG는 답을 외우는 모델이 아니라 검색한 문서를 생성 전에 프롬프트에 주입하는 파이프라인입니다.
---

# AI App Patterns 101 (2/6): RAG Q&A 패턴 — 문서 기반 질의응답

RAG를 더 똑똑한 모델이라고 생각하면 설계가 흐려집니다. RAG는 모델을 바꾸는 기술이라기보다, 적절한 문서를 적절한 시점에 찾아 프롬프트에 주입하는 검색 파이프라인입니다. 답변 품질도 모델의 신비로움보다 어떤 청크를 찾았는지, 그리고 그 청크를 어떻게 넣었는지에 더 크게 좌우됩니다.

LLM이 모르는 최신 정보, 사내 문서, 비공개 지식이 필요한 순간부터 이 관점이 중요해집니다. 환각을 줄이는 핵심도 결국 생성 전에 검색을 어떻게 붙였는지에서 시작합니다.

이 글은 AI App Patterns 101 시리즈의 두 번째 글입니다. 여기서는 가장 작은 실용적인 RAG Q&A 파이프라인을 만들고, 검색과 생성이 어떻게 맞물리는지 차례로 정리합니다.

## 먼저 던지는 질문

- RAG 답변 품질을 보기 전에 왜 검색 결과부터 확인해야 할까요?
- 근거가 약한데도 모델이 답하게 두면 어떤 실패가 생길까요?
- 출처를 함께 반환하려면 청크와 메타데이터를 어디서 보존해야 할까요?

## 큰 그림

![오프라인 인덱싱 파이프라인](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/02/02-01-offline-indexing-pipeline.ko.png)

*오프라인 인덱싱 파이프라인*

이 그림에서는 질문이 검색 단계에서 관련 문서 조각으로 바뀌고, 그 조각이 생성 단계의 근거로 들어가는 흐름을 봅니다. RAG Q&A는 모델 호출보다 검색 경계와 근거 품질을 먼저 봐야 안전합니다.

> RAG는 답을 외우는 모델이 아니라, 검색된 문서를 생성 전에 프롬프트에 주입하는 파이프라인입니다.

## RAG의 두 단계

### 오프라인 인덱싱 파이프라인

인덱싱(오프라인)은 문서를 청크로 나누고, 임베딩을 만들고, 벡터 인덱스에 저장하는 단계입니다.

검색(온라인)은 질의를 임베딩하고, 비슷한 청크를 찾고, 그 청크를 프롬프트에 주입하는 단계입니다.

```text
indexing:  documents → chunking → embedding → FAISS
retrieval: query → embedding → FAISS search → prompt injection → LLM → answer
```

---

## 완전한 RAG Q&A 구현

### 온라인 질의응답 흐름

![온라인 질의응답 흐름](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/02/02-02-online-question-answering-flow.ko.png)

*온라인 질의응답 흐름*
```python
import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    """
Python is a high-level programming language created by Guido van Rossum in 1991.
It uses indentation to delimit code blocks, which is unusual among mainstream languages.
Python supports dynamic typing and automatic memory management.
It is widely used in web development, data science, and artificial intelligence.
""",
    """
Python's primary strength is readability.
It was designed to read like English prose.
Python has a large standard library and a vast third-party package ecosystem.
Hundreds of thousands of packages can be installed with the pip package manager.
""",
    """
One of Python's main weaknesses is execution speed.
As an interpreted language, it is slower than C or Java for CPU-bound tasks.
The GIL (Global Interpreter Lock) limits multi-threaded performance.
Python is rarely used for mobile application development.
""",
    """
Python version history: Python 2 was released in 2000, Python 3 in 2008.
Python 2 reached its official end of life in January 2020.
Python 3.10 or later is recommended for new projects.
A new minor version is released each October.
""",
]

splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
chunks = []
for doc in documents:
    chunks.extend(splitter.split_text(doc))

vectorstore = FAISS.from_texts(texts=chunks, embedding=embedding_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Answer the question using only the reference documents below.\n"
        "If the answer is not in the documents, say 'I cannot find this in the provided documents'.\n"
        "Do not speculate.\n\n"
        "Reference documents:\n{context}",
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

test_questions = [
    "Who created Python?",
    "What are Python's weaknesses?",
    "When did Python 2 reach end of life?",
    "Can you build iOS apps with Python?",
    "What are the features of the Rust language?",  # not in documents
]

for question in test_questions:
    print(f"\nquestion: {question}")
    answer = rag_chain.invoke(question)
    print(f"answer: {answer}")
```

이 예제의 핵심은 단지 정답이 있을 때 잘 답한다는 데 있지 않습니다. **근거가 없으면 자신 있게 메우지 말고 멈춘다**는 운영 규칙을 프롬프트에 먼저 심는 데 있습니다. 이 차이가 보기 좋은 데모와 디버깅 가능한 검색 파이프라인을 갈라놓습니다.

---

## 생성보다 먼저 검색을 검증하기

### 점수와 메타데이터로 보는 검색 결과

![온라인 질의응답 흐름](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/02/02-02-online-question-answering-flow.ko.png)

*온라인 질의응답 흐름*
프롬프트를 다듬기 전에 retriever가 실제로 무엇을 꺼내 오는지 먼저 확인해야 합니다. 1등 청크가 틀리면 생성 품질의 상한선도 이미 정해진 셈입니다.

```python
from langchain_core.documents import Document

docs = [
    Document(
        page_content="Python은 Guido van Rossum이 1991년에 만든 언어입니다.",
        metadata={"source": "python_intro.txt", "section": "history"},
    ),
    Document(
        page_content="Python의 대표 강점은 가독성과 넓은 패키지 생태계입니다.",
        metadata={"source": "python_features.txt", "section": "strengths"},
    ),
    Document(
        page_content="Python은 CPU 중심 작업에서 C보다 느릴 수 있고, GIL 때문에 일부 스레드 작업이 제한됩니다.",
        metadata={"source": "python_limits.txt", "section": "weaknesses"},
    ),
]

vectorstore = FAISS.from_documents(docs, embedding_model)

def inspect_retrieval(query: str, top_k: int = 3) -> None:
    matches = vectorstore.similarity_search_with_relevance_scores(query, k=top_k)
    print(f"query: {query}")
    for rank, (doc, score) in enumerate(matches, start=1):
        print(
            f"  {rank}. score={score:.3f} "
            f"source={doc.metadata['source']} "
            f"section={doc.metadata['section']}"
        )
        print(f"     {doc.page_content}")

inspect_retrieval("왜 Python이 느릴 때가 있나요?")
inspect_retrieval("Python을 만든 사람은 누구인가요?")
```

**Expected output:**

```text
query: 왜 Python이 느릴 때가 있나요?
  1. score=0.91 source=python_limits.txt section=weaknesses
     Python은 CPU 중심 작업에서 C보다 느릴 수 있고, GIL 때문에 일부 스레드 작업이 제한됩니다.

query: Python을 만든 사람은 누구인가요?
  1. score=0.94 source=python_intro.txt section=history
     Python은 Guido van Rossum이 1991년에 만든 언어입니다.
```

최상위 결과가 엉뚱하다면 프롬프트부터 다시 쓰지 마세요. 청크 경계, 메타데이터 품질, 사용자 질의 표현과 임베딩 모델의 궁합을 먼저 점검해야 합니다.

---

## 출처를 함께 반환하는 응답

### 답변과 출처를 함께 돌려주는 구조

![답변과 출처를 함께 돌려주는 구조](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/02/02-03-answer-and-source-return-structure.ko.png)

*답변과 출처를 함께 돌려주는 구조*
어떤 문서가 답변의 근거였는지 함께 보여 주면 사용자 신뢰가 크게 좋아집니다.

```python
import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_groq import ChatGroq

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents_with_metadata = [
    ("Python is a high-level language created by Guido van Rossum in 1991.", {"source": "python_intro.txt", "page": 1}),
    ("Python's primary strength is readability.", {"source": "python_features.txt", "page": 1}),
    ("One of Python's main weaknesses is execution speed.", {"source": "python_cons.txt", "page": 1}),
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
    ("system", "Answer the question using only the documents below:\n{context}"),
    ("human", "{question}"),
])

def format_docs(docs: list) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

def get_sources(docs: list) -> list[str]:
    return [doc.metadata.get("source", "unknown") for doc in docs]

rag_with_sources = RunnableParallel(
    answer=(
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    ),
    sources=retriever | get_sources,
)

result = rag_with_sources.invoke("Who created Python?")
print(f"answer: {result['answer']}")
print(f"sources: {result['sources']}")
```

---

## 근거가 약할 때 답변 경로를 끊기

### 최소 관련도 기준으로 폴백 분기

![근거가 없을 때의 폴백 분기](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/02/02-05-fallback-branch-for-missing-evidence.ko.png)

*근거가 없을 때의 폴백 분기*
프롬프트만으로는 부족합니다. 운영 환경에서는 검색 결과가 충분히 강한지 애플리케이션 쪽에서도 확인해야 합니다.

```python
from langchain_core.documents import Document

MIN_RELEVANCE = 0.80

docs = [
    Document(page_content=text, metadata=meta)
    for text, meta in documents_with_metadata
]
vectorstore = FAISS.from_documents(docs, embedding_model)

def answer_with_guard(question: str) -> dict:
    matches = vectorstore.similarity_search_with_relevance_scores(question, k=3)

    if not matches or matches[0][1] < MIN_RELEVANCE:
        return {
            "route": "fallback_no_evidence",
            "answer": "색인된 문서 안에서 이 질문의 근거를 찾지 못했습니다.",
            "sources": [],
        }

    selected_docs = [doc for doc, _ in matches]
    context = format_docs(selected_docs)
    answer = (prompt | llm | StrOutputParser()).invoke({
        "context": context,
        "question": question,
    })

    return {
        "route": "answer_from_documents",
        "answer": answer,
        "sources": get_sources(selected_docs),
    }

print(answer_with_guard("Python을 만든 사람은 누구인가요?"))
print(answer_with_guard("Rust의 주요 특징은 무엇인가요?"))
```

**Expected output:**

```text
{'route': 'answer_from_documents', 'answer': 'Python은 Guido van Rossum이 1991년에 만들었습니다.', 'sources': ['python_intro.txt']}
{'route': 'fallback_no_evidence', 'answer': '색인된 문서 안에서 이 질문의 근거를 찾지 못했습니다.', 'sources': []}
```

이 지점에서 많은 RAG 시스템이 한 단계 더 안전해집니다. 검색 품질을 모델의 자기 판단에 맡기지 않고, 근거가 약할 때는 애플리케이션이 먼저 생성 경로를 끊기 때문입니다.

---

## RAG가 실패하는 순간

### 검색 누락에 대한 방어 계층

![검색 누락에 대한 방어 계층](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/02/02-04-defense-layers-against-retrieval-misses.ko.png)

*검색 누락에 대한 방어 계층*
### 근거가 없을 때의 폴백 분기

![근거가 없을 때의 폴백 분기](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/02/02-05-fallback-branch-for-missing-evidence.ko.png)

*근거가 없을 때의 폴백 분기*
**관련 청크가 검색되지 않은 경우입니다.** 질의와 맞는 청크를 찾지 못하면 LLM은 내부 지식으로 메우려 하고, 그 과정에서 환각할 수 있습니다. “문서에 없으면 모른다고 말하라”는 프롬프트 지시는 첫 번째 방어선입니다.

**정보가 청크 경계에서 갈라지는 경우입니다.** 중요한 맥락이 두 청크에 걸치면 검색된 단일 결과 어느 쪽에서도 정보가 완전하지 않을 수 있습니다. 충분한 `chunk_overlap`이 이 위험을 줄입니다.

**질의 표현과 문서 표현이 너무 다른 경우입니다.** 예를 들어 “is python slow?” 같은 구어체 질의는 “interpreted language execution performance”를 담은 청크와 잘 매칭되지 않을 수 있습니다. 이때는 query expansion이나 hybrid search가 도움이 됩니다.

> 멘탈 모델은 검색 품질이 생성 품질의 상한선을 만든다는 것입니다. 생성 모델은 검색이 가져온 근거 위에서만 안전하게 답할 수 있습니다.

### 답변이 이상할 때 먼저 보는 순서

RAG 답변이 약하게 느껴지면 다음 순서로 확인하는 편이 빠릅니다.

1. **검색 순위** — 맞는 청크가 top-k 안에 들어왔는가?
2. **청크 형태** — 근거가 너무 잘게 잘리거나 무관한 텍스트와 섞이지 않았는가?
3. **폴백 기준** — 근거 점수가 낮은데도 생성 경로를 허용하지 않았는가?
4. **프롬프트 계약** — 추측 금지와 근거 기반 답변 규칙이 충분히 분명한가?

---

## 이 코드에서 먼저 볼 점

- `main.py`는 `RecursiveCharacterTextSplitter`로 청킹하고, `FAISS.from_texts()`로 즉시 인덱싱하는 흐름을 보여 줍니다.
- 스크립트는 검색된 `Document` 객체를 유지해 답변과 근거 출처를 함께 출력할 수 있게 합니다.
- 프롬프트는 문맥 안의 정보만 쓰고, 답이 없으면 없다고 말하라고 명시합니다.

---

## 어디서 자주 헷갈릴까요?

- 많은 팀이 먼저 생성 모델을 탓하지만, 실제로 RAG 품질을 망치는 원인은 청킹 전략과 retriever 설정인 경우가 더 많습니다.
- 임베딩 모델과 답변 생성 모델은 서로 다른 문제를 푸는 구성 요소입니다. 둘이 같을 필요는 없습니다.
- top-k를 키운다고 자동으로 좋아지지 않습니다. 잡음 청크가 늘어나면 오히려 유용한 문맥이 희석될 수 있습니다.

---

## 체크리스트

- [ ] 문서가 인덱싱 전에 청크로 분할된다
- [ ] 답변 생성 전에 retriever가 먼저 실행된다
- [ ] 최종 출력에 출처 파일명이 포함된다
- [ ] 문서에 답이 없을 때 인정하도록 프롬프트가 모델을 제한한다

---

## 정리

RAG Q&A는 LLM이 학습하지 않은 지식에 접근하게 만드는 가장 실용적인 패턴입니다. 정보가 없을 때 “모른다”고 말하게 하는 프롬프트 지시는 가장 단순하면서도 중요한 환각 방지 장치입니다.

다음 글에서는 문서 어시스턴트 패턴을 다룹니다. 요약, 정보 추출, 분류처럼 구조화된 문서 처리 작업에 집중하는 패턴입니다.

---

## FastAPI RAG API와 근거 노출 계약

### 질의응답 엔드포인트에서 근거 강제하기

RAG를 운영 환경으로 옮길 때 가장 중요한 차이는 "답변 문자열"만 반환하지 않는다는 점입니다. 호출자는 답변과 함께 근거 문서, 점수, 폴백 여부를 받아야 합니다. 아래 예시는 최소한의 계약을 보여 줍니다.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QARequest(BaseModel):
    question: str

def retrieve(question: str) -> list[dict]:
    # 실제 구현에서는 FAISS/PGVector 결과를 반환합니다.
    return [
        {"text": "Python은 Guido van Rossum이 만들었습니다.", "score": 0.93, "source": "python_intro.txt"},
        {"text": "Python 2는 2020년에 종료되었습니다.", "score": 0.88, "source": "python_history.txt"},
    ]

def generate_with_context(question: str, docs: list[dict]) -> str:
    context = "
".join(f"- {d['text']}" for d in docs)
    system_prompt = f"""
당신은 문서 기반 Q&A 어시스턴트입니다.
아래 근거 문서 밖의 내용은 추측하지 않습니다.
근거가 없으면 '문서 근거 부족'이라고 답합니다.

근거 문서:
{context}
""".strip()
    # 실제 구현에서는 LLM 호출
    return f"질문 '{question}'에 대해 문서 근거 기반 예시 답변입니다."

@app.post('/rag/qa')
def rag_qa(req: QARequest):
    docs = retrieve(req.question)
    if not docs or docs[0]['score'] < 0.80:
        return {
            'route': 'fallback_no_evidence',
            'answer': '문서 근거 부족',
            'sources': [],
            'top_score': docs[0]['score'] if docs else None,
        }

    answer = generate_with_context(req.question, docs)
    return {
        'route': 'answer_from_documents',
        'answer': answer,
        'sources': [d['source'] for d in docs],
        'top_score': docs[0]['score'],
    }
```

이 계약을 쓰면 프론트엔드와 운영 대시보드가 같은 사실을 보게 됩니다. "잘못 답했다"를 추상적으로 다루지 않고, 검색 점수 저하인지, 근거 누락인지, 생성 품질 문제인지 분리할 수 있습니다.

### 검색-생성 분리 아키텍처

```mermaid
flowchart LR
    Q[사용자 질문] --> R[Retriever]
    R -->|top-k 청크 + 점수| G[Generator]
    G --> A[답변]
    R --> E[근거/점수 로그]
    A --> API[API 응답]
    E --> API
```

*검색-생성 분리 아키텍처*

이런 분리 구조가 필요한 이유는 단순합니다. 검색과 생성은 개선 방법이 다르기 때문입니다. 검색이 흔들리면 청킹/임베딩/인덱스를 손봐야 하고, 생성이 흔들리면 프롬프트 계약이나 출력 포맷을 고쳐야 합니다. 두 문제를 한 덩어리로 보면 개선 속도가 급격히 느려집니다.

## 검색 품질 계측과 재인덱싱 전략

질의응답 품질을 안정적으로 올리려면 "답변 품질 느낌"이 아니라 검색 단계 지표를 봐야 합니다. 운영에서 자주 보는 최소 지표는 다음과 같습니다.

- `hit_at_k`: 정답 근거 문서가 top-k 안에 포함되는 비율
- `mrr`: 정답 문서가 상위에 올수록 점수가 커지는 순위 지표
- `no_evidence_rate`: 폴백 경로 비율
- `stale_chunk_rate`: 오래된 청크가 근거로 선택된 비율

```python
def evaluate_retrieval(queries: list[dict], retriever) -> dict:
    hit = 0
    reciprocal_ranks = []

    for q in queries:
        docs = retriever(q['question'])
        rank = None
        for i, d in enumerate(docs, start=1):
            if d['source'] == q['gold_source']:
                rank = i
                break
        if rank:
            hit += 1
            reciprocal_ranks.append(1 / rank)
        else:
            reciprocal_ranks.append(0)

    total = len(queries)
    return {
        'hit_at_k': hit / total,
        'mrr': sum(reciprocal_ranks) / total,
    }
```

### 재인덱싱 트리거

문서가 자주 바뀌는 도메인에서는 재인덱싱 주기를 정책으로 고정해야 합니다.

```text
trigger_1: 문서 변경 건수 >= 500
trigger_2: 핵심 정책 문서 업데이트 발생
trigger_3: hit_at_k가 최근 7일 평균 대비 10%p 하락
action: affected source만 증분 재인덱싱
```

이런 규칙이 없으면 RAG는 한동안 잘 동작하다가, 문서 현실과 인덱스 현실이 어긋나는 순간 급격히 신뢰를 잃습니다.

## 근거 없는 질문 처리 UX

RAG에서 폴백 응답은 기술적 안전장치일 뿐 아니라 사용자 경험 설계이기도 합니다. 단순히 "모름"으로 끝내지 않고, 가능한 다음 행동을 안내하면 이탈을 줄일 수 있습니다.

```json
{
  "route": "fallback_no_evidence",
  "answer": "현재 색인된 문서에서 근거를 찾지 못했습니다.",
  "next_actions": [
    "질문을 더 구체적으로 작성해 주세요.",
    "관련 문서 제목이나 키워드를 함께 입력해 주세요."
  ]
}
```

근거 부족 경로를 제품 UX로 다루면 안전성과 사용성을 동시에 챙길 수 있습니다.

### 운영 회고에서 반드시 남길 항목

패턴 설계가 실제로 효과가 있었는지는 회고 기록 품질에서 드러납니다. 각 글에서 다룬 구조를 실서비스에 적용했다면, 최소한 다음 항목은 공통 템플릿으로 남기는 편이 좋습니다.

- 변경 전/후의 실패 유형 분포
- 변경 전/후의 평균 지연 시간과 p95
- 사람이 개입한 건수와 자동 처리 건수 비율
- 근거 부족, 파싱 실패, 도구 오류 같은 실패 코드의 추세
- 다음 분기에서 조정할 임계값 또는 프롬프트 버전

이 기록이 쌓이면 모델 자체 성능보다 애플리케이션 패턴 결정이 어떤 영향을 주었는지 분리해서 볼 수 있습니다. 결국 운영 품질은 한 번의 정답 설계가 아니라, 측정 가능한 개선 루프를 오래 유지하는 능력에서 만들어집니다.

## 처음 질문으로 돌아가기

- **RAG 답변 품질을 보기 전에 왜 검색 결과부터 확인해야 할까요?**
  모델 답변은 검색된 컨텍스트에 묶이므로, 컨텍스트가 비어 있거나 엉뚱하면 모델을 바꿔도 품질 문제가 해결되지 않습니다.

- **근거가 약한데도 모델이 답하게 두면 어떤 실패가 생길까요?**
  근거가 약한데도 답하게 두면 그럴듯한 환각 답변이 생깁니다. 낮은 점수나 빈 결과는 답변 경로를 끊는 신호가 되어야 합니다.

- **출처를 함께 반환하려면 청크와 메타데이터를 어디서 보존해야 할까요?**
  청크 텍스트와 함께 문서 ID, 제목, URL, 위치 정보를 검색 단계부터 보존해야 답변에서 출처를 함께 돌려줄 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI App Patterns 101 (1/6): 챗봇 패턴 — 대화 이력과 상태 관리](./01-chatbot-pattern.md)
- **AI App Patterns 101 (2/6): RAG Q&A 패턴 — 문서 기반 질의응답 (현재 글)**
- AI App Patterns 101 (3/6): 문서 어시스턴트 — 요약, 추출, 분류 (예정)
- AI App Patterns 101 (4/6): 에이전트와 도구 패턴 — 자율적 도구 선택 (예정)
- AI App Patterns 101 (5/6): 워크플로 자동화 — 다단계 체인 설계 (예정)
- AI App Patterns 101 (6/6): Human-in-the-loop — 사람 개입 설계 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain RAG tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [RAG paper (Lewis et al., 2020)](https://arxiv.org/abs/2005.11401)
- [FAISS VectorStore](https://python.langchain.com/docs/integrations/vectorstores/faiss/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-app-patterns-101/ko/02-rag-qa-pattern)

Tags: LLM, RAG, Agent, Python
