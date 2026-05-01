---
title: '한국어 RAG 파이프라인 조합하기'
series: korean-ai-stack-101
episode: 6
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

# 한국어 RAG 파이프라인 조합하기

> 한국어 AI 스택 101 시리즈 (6/6)

이 시리즈에서 다룬 구성 요소를 하나의 파이프라인으로 조합합니다. KoSimCSE 임베딩으로 한국어 문서를 인덱싱하고, FAISS로 검색하고, Solar LLM으로 한국어 답변을 생성합니다. 여기에 OCR 전처리까지 추가하면 이미지나 스캔 문서도 처리할 수 있습니다.

이번 글에서는 다음을 다룹니다.

- 전체 파이프라인 아키텍처
- 완전한 한국어 RAG 구현
- 문서 유형별 청킹 전략 선택
- 파이프라인 디버깅과 모니터링

---

## 전체 파이프라인 아키텍처

```
[문서 소스]
  텍스트 파일 ─┐
  이미지/PDF  ─┼─→ [전처리] ─→ [청킹] ─→ [KoSimCSE 임베딩] ─→ [FAISS 인덱스]
  OCR 결과   ─┘

[쿼리 시간]
  사용자 질문 ─→ [KoSimCSE 임베딩] ─→ [FAISS 검색] ─→ [Solar LLM] ─→ 답변
```

---

## 완전한 한국어 RAG 파이프라인

```python
import os
import re
from dataclasses import dataclass
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

@dataclass
class DocumentChunk:
    text: str
    source: str
    chunk_idx: int

class KoreanRAGPipeline:
    """
    한국어 문서를 위한 완전한 RAG 파이프라인.
    KoSimCSE 임베딩 + FAISS + Solar LLM.
    """

    SPLITTER_CONFIG = {
        "legal": {
            "chunk_size": 500,
            "chunk_overlap": 100,
            "separators": ["\n\n", "\n", "。", ". "],
        },
        "news": {
            "chunk_size": 300,
            "chunk_overlap": 50,
            "separators": ["\n\n", "\n", ". "],
        },
        "technical": {
            "chunk_size": 400,
            "chunk_overlap": 80,
            "separators": ["\n\n", "\n", ". ", " "],
        },
    }

    def __init__(self, doc_type: str = "technical"):
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="BM-K/KoSimCSE-roberta-multitask",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        config = self.SPLITTER_CONFIG.get(doc_type, self.SPLITTER_CONFIG["technical"])
        self.splitter = RecursiveCharacterTextSplitter(**config)

        self.llm = ChatOpenAI(
            model="solar-1-mini-chat",
            api_key=os.environ.get("UPSTAGE_API_KEY", "dummy"),
            base_url="https://api.upstage.ai/v1/solar",
            temperature=0.3,
        )

        self.vectorstore = None
        self.retriever = None
        self.chain = None

    def clean_text(self, text: str) -> str:
        """한국어 텍스트 기본 정제."""
        text = re.sub(r"([^\w\s가-힣])\1{2,}", "", text)
        text = re.sub(r" {2,}", " ", text)
        lines = [l.strip() for l in text.split("\n")]
        cleaned = []
        prev_empty = False
        for line in lines:
            is_empty = not line
            if is_empty and prev_empty:
                continue
            cleaned.append(line)
            prev_empty = is_empty
        return "\n".join(cleaned).strip()

    def index_documents(self, documents: list[dict]) -> None:
        """
        문서 목록을 인덱싱합니다.
        각 문서: {"text": str, "source": str}
        """
        all_chunks = []
        for doc in documents:
            cleaned = self.clean_text(doc["text"])
            chunks = self.splitter.split_text(cleaned)
            for idx, chunk in enumerate(chunks):
                all_chunks.append(DocumentChunk(
                    text=chunk,
                    source=doc["source"],
                    chunk_idx=idx,
                ))

        texts = [c.text for c in all_chunks]
        metadatas = [{"source": c.source, "chunk_idx": c.chunk_idx} for c in all_chunks]

        self.vectorstore = FAISS.from_texts(
            texts=texts,
            embedding=self.embedding_model,
            metadatas=metadatas,
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "다음 참고 문서를 바탕으로 질문에 답하세요.\n"
                "문서에 없는 내용은 '제공된 문서에서 찾을 수 없습니다'라고 하세요.\n\n"
                "참고 문서:\n{context}",
            ),
            ("human", "{question}"),
        ])

        def format_docs(docs: list) -> str:
            parts = []
            for doc in docs:
                source = doc.metadata.get("source", "알 수 없음")
                parts.append(f"[출처: {source}]\n{doc.page_content}")
            return "\n\n".join(parts)

        self.chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        print(f"인덱싱 완료: {len(all_chunks)}개 청크 ({len(documents)}개 문서)")

    def query(self, question: str) -> dict:
        """질문에 답하고 사용된 출처를 함께 반환합니다."""
        if not self.chain:
            raise RuntimeError("먼저 index_documents()를 호출하세요.")

        docs = self.retriever.invoke(question)
        sources = list({doc.metadata.get("source", "알 수 없음") for doc in docs})
        answer = self.chain.invoke(question)

        return {"answer": answer, "sources": sources}
```

---

## 사용 예시

```python
# 파이프라인 초기화 (법령 문서용 청킹 설정)
pipeline = KoreanRAGPipeline(doc_type="legal")

# 문서 인덱싱
documents = [
    {
        "source": "헌법.txt",
        "text": """
대한민국 헌법 제1조
대한민국은 민주공화국이다.
대한민국의 주권은 국민에게 있고, 모든 권력은 국민으로부터 나온다.

대한민국 헌법 제10조
모든 국민은 인간으로서의 존엄과 가치를 가지며, 행복을 추구할 권리를 가진다.
국가는 개인이 가지는 불가침의 기본적 인권을 확인하고 이를 보장할 의무를 진다.

대한민국 헌법 제12조
모든 국민은 신체의 자유를 가진다. 누구든지 법률에 의하지 아니하고는 체포·구속·압수·수색 또는 심문을 받지 아니하며, 법률과 적법한 절차에 의하지 아니하고는 처벌·보안처분 또는 강제노역을 받지 아니한다.
        """,
    },
    {
        "source": "민법.txt",
        "text": """
민법 제750조 (불법행위의 내용)
고의 또는 과실로 인한 위법행위로 타인에게 손해를 가한 자는 그 손해를 배상할 책임이 있다.

민법 제751조 (재산 이외의 손해의 배상)
타인의 신체, 자유 또는 명예를 해하거나 기타 정신상고통을 가한 자는 재산 이외의 손해에 대하여도 배상할 책임이 있다.
        """,
    },
]

pipeline.index_documents(documents)

# 질문
questions = [
    "헌법에서 국민의 기본권은 어떻게 보장되나요?",
    "불법행위로 손해를 입혔을 때 법적 책임은 어떻게 되나요?",
    "신체의 자유는 어떤 경우에 제한될 수 있나요?",
]

for question in questions:
    print(f"\n질문: {question}")
    result = pipeline.query(question)
    print(f"답변: {result['answer']}")
    print(f"출처: {result['sources']}")
```

---

## 파이프라인 디버깅

검색 결과가 예상과 다를 때 각 단계를 개별적으로 확인합니다.

```python
def debug_pipeline(pipeline: KoreanRAGPipeline, question: str) -> None:
    """파이프라인 각 단계의 중간 결과를 출력합니다."""
    print(f"\n=== 디버그: '{question}' ===")

    # 1. 쿼리 임베딩 확인
    query_embedding = pipeline.embedding_model.embed_query(question)
    print(f"쿼리 임베딩 차원: {len(query_embedding)}")
    print(f"쿼리 임베딩 처음 3값: {query_embedding[:3]}")

    # 2. 검색 결과 확인
    docs = pipeline.retriever.invoke(question)
    print(f"\n검색된 청크 수: {len(docs)}")
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "알 수 없음")
        print(f"  [{i}] 출처: {source}")
        print(f"      내용: {doc.page_content[:80]}...")

    # 3. 최종 답변
    result = pipeline.query(question)
    print(f"\n최종 답변:\n{result['answer']}")

# 디버그 실행
debug_pipeline(pipeline, "주권이 누구에게 있나요?")
```

---

## 마무리

이번 시리즈에서는 한국어 AI 스택의 핵심 구성 요소를 다뤘습니다. KoSimCSE와 BGE-M3로 한국어 의미를 벡터로 표현하고, CLOVA OCR로 이미지 문서에서 텍스트를 추출하고, HyperCLOVA X와 Solar로 자연스러운 한국어 답변을 생성했습니다. 이 파이프라인은 법률, 의료, 금융 등 한국어 문서가 많은 도메인에서 영어 중심 스택보다 더 나은 결과를 냅니다.

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

- [KoSimCSE](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [BGE-M3](https://huggingface.co/BAAI/bge-m3)
- [CLOVA OCR](https://api.ncloud-docs.com/docs/ai-application-service-ocr)
- [Solar API](https://developers.upstage.ai/docs/apis/chat)
- [FAISS](https://faiss.ai/)

Tags: Korean NLP, LLM, Embeddings, OCR
