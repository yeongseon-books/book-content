---
title: 'Assembling a Korean RAG pipeline'
series: korean-ai-stack-101
episode: 6
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

# Assembling a Korean RAG pipeline

> Korean AI Stack 101 (6/6)

This post assembles the components covered throughout the series into one pipeline: KoSimCSE embeddings for indexing Korean documents, FAISS for retrieval, and Solar LLM for generating Korean answers. Adding CLOVA OCR preprocessing extends it to scanned images and PDFs.

Topics:

- full pipeline architecture
- complete Korean RAG implementation
- document-type-aware chunking strategies
- debugging each pipeline stage

---

## Pipeline architecture

```
[document sources]
  text files ─┐
  images/PDFs─┼─→ [preprocessing] ─→ [chunking] ─→ [KoSimCSE embedding] ─→ [FAISS index]
  OCR output ─┘

[query time]
  user question ─→ [KoSimCSE embedding] ─→ [FAISS search] ─→ [Solar LLM] ─→ answer
```

---

## Complete Korean RAG implementation

```python
import os
import re
from dataclasses import dataclass

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
    Complete RAG pipeline for Korean documents.
    KoSimCSE embedding + FAISS + Solar LLM.
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
        """Basic Korean text cleaning."""
        text = re.sub(r"([^\w\s가-힣])\1{2,}", "", text)
        text = re.sub(r" {2,}", " ", text)
        lines = [ln.strip() for ln in text.split("\n")]
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
        Index a list of documents.
        Each document: {"text": str, "source": str}
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
                "Answer the question using the reference documents below.\n"
                "If the answer is not in the documents, say so.\n\n"
                "Reference documents:\n{context}",
            ),
            ("human", "{question}"),
        ])

        def format_docs(docs: list) -> str:
            parts = []
            for doc in docs:
                source = doc.metadata.get("source", "unknown")
                parts.append(f"[source: {source}]\n{doc.page_content}")
            return "\n\n".join(parts)

        self.chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        print(f"indexed: {len(all_chunks)} chunks from {len(documents)} documents")

    def query(self, question: str) -> dict:
        """Answer a question and return the sources used."""
        if not self.chain:
            raise RuntimeError("call index_documents() first")

        docs = self.retriever.invoke(question)
        sources = list({doc.metadata.get("source", "unknown") for doc in docs})
        answer = self.chain.invoke(question)

        return {"answer": answer, "sources": sources}
```

---

## Usage

```python
pipeline = KoreanRAGPipeline(doc_type="legal")

documents = [
    {
        "source": "constitution.txt",
        "text": """
Article 1 of the Constitution of the Republic of Korea:
The Republic of Korea shall be a democratic republic.
The sovereignty of the Republic of Korea shall reside in the people, and all state authority shall emanate from the people.

Article 10:
All citizens shall be assured of human worth and dignity and shall have the right to pursue happiness.
It shall be the duty of the state to confirm and guarantee the fundamental and inviolable human rights of individuals.

Article 12:
All citizens shall enjoy personal liberty. No person shall be arrested, detained, searched, seized or interrogated except as provided by act.
        """,
    },
    {
        "source": "civil_code.txt",
        "text": """
Article 750 of the Civil Act (Tort):
A person who causes injury to another through an unlawful act, intentionally or negligently, shall be bound to make compensation for damages arising therefrom.

Article 751:
A person who causes damage to another's body, liberty or reputation or inflicts mental anguish on another shall also be bound to make compensation for non-property damages.
        """,
    },
]

pipeline.index_documents(documents)

questions = [
    "How does the Korean constitution protect fundamental rights?",
    "What is the legal liability when someone causes damage through an unlawful act?",
    "Under what conditions can personal liberty be restricted?",
]

for question in questions:
    print(f"\nquestion: {question}")
    result = pipeline.query(question)
    print(f"answer: {result['answer']}")
    print(f"sources: {result['sources']}")
```

---

## Debugging each stage

When retrieval results are unexpected, inspect each stage individually.

```python
def debug_pipeline(pipeline: KoreanRAGPipeline, question: str) -> None:
    """Print intermediate results at each pipeline stage."""
    print(f"\n=== debug: '{question}' ===")

    query_embedding = pipeline.embedding_model.embed_query(question)
    print(f"query embedding dims: {len(query_embedding)}")
    print(f"first 3 values: {query_embedding[:3]}")

    docs = pipeline.retriever.invoke(question)
    print(f"\nretrieved chunks: {len(docs)}")
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "unknown")
        print(f"  [{i}] source: {source}")
        print(f"       content: {doc.page_content[:80]}...")

    result = pipeline.query(question)
    print(f"\nfinal answer:\n{result['answer']}")

debug_pipeline(pipeline, "Who holds sovereignty in Korea?")
```

---

## Conclusion

The Korean AI stack — KoSimCSE or BGE-M3 for embeddings, CLOVA OCR for image documents, and HyperCLOVA X or Solar for generation — outperforms English-centric stacks on Korean-language domains like law, medicine, and finance. The pipeline presented here is production-ready: clean the text, chunk with domain-appropriate settings, index with normalized embeddings, and use a low temperature for factual retrieval tasks.

<!-- toc:begin -->
## In this series

- [Korean embedding models compared — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [Building sentence similarity search with KoSimCSE](./02-kosimcse-similarity.md)
- [BGE-M3 multilingual embedding in practice](./03-bge-m3-multilingual.md)
- [Document text extraction with CLOVA OCR API](./04-clova-ocr.md)
- [Using HyperCLOVA X and Solar API](./05-hyperclova-solar-api.md)
- **Assembling a Korean RAG pipeline (current)**

<!-- toc:end -->

---

## References

- [KoSimCSE](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [BGE-M3](https://huggingface.co/BAAI/bge-m3)
- [CLOVA OCR](https://api.ncloud-docs.com/docs/ai-application-service-ocr)
- [Solar API](https://developers.upstage.ai/docs/apis/chat)
- [FAISS](https://faiss.ai/)

Tags: Korean NLP, LLM, Embeddings, OCR
