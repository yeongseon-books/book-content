---
title: 'Putting it together — a complete chain in one file'
series: langchain-101
episode: 6
language: en
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

# Putting it together — a complete chain in one file

> LangChain 101 (6/6)

The previous five posts covered LCEL, prompt templates, Retrievers, Tool Calling, and Streaming individually. This post assembles them into one executable application: index documents, search by query, generate an answer, and stream the output.

Topics:

- document chunking → embedding → FAISS index
- assembling a RAG chain with streaming output
- multi-turn RAG with conversation history
- a self-contained application in one file

---

## Document indexing pipeline

```python
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=30,
    separators=["\n\n", "\n", ". ", " ", ""],
)

documents = [
    """
Vector search converts text into numeric vectors for meaning-based retrieval.
Unlike keyword search, it matches content even when phrasing differs.
Embedding models place semantically similar text close together in vector space.
""",
    """
FAISS is a high-speed vector search library developed at Facebook AI Research.
It supports both exact and approximate search and can handle billions of vectors.
IndexFlatIP is an exact inner-product index.
""",
    """
LangChain connects LLM components as a pipeline using LCEL.
Retriever, Tool, and OutputParser all implement the Runnable interface.
The pipe operator (|) composes components into a chain.
""",
    """
RAG (Retrieval-Augmented Generation) combines retrieved documents with an LLM prompt.
The system retrieves relevant chunks for the question and provides them as context.
Vector search is the core retrieval component in most RAG pipelines.
""",
]

chunks = []
for doc in documents:
    chunks.extend(splitter.split_text(doc))

vectorstore = FAISS.from_texts(texts=chunks, embedding=embedding_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

print(f"index vector count: {vectorstore.index.ntotal}")
```

---

## Assembling the RAG chain

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

def format_docs(docs: list) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Answer the question using only the provided documents. "
        "If the answer is not in the documents, say so.\n\n"
        "Documents:\n{context}",
    ),
    ("human", "{question}"),
])

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

---

## Running with streaming

```python
questions = [
    "How is vector search different from keyword search?",
    "Where was FAISS developed?",
    "Why does RAG improve LLM accuracy?",
    "What is LCEL in LangChain?",
]

for question in questions:
    print(f"\nquestion: {question}")
    print("answer: ", end="")
    for chunk in rag_chain.stream(question):
        print(chunk, end="", flush=True)
    print()
```

---

## Multi-turn RAG with conversation history

A simple RAG chain treats each question independently. To reference earlier turns, pass conversation history to the chain.

```python
import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    "FAISS is a high-speed vector search library developed at Facebook AI Research.",
    "Embedding models project text into a high-dimensional vector space.",
    "RAG combines retrieved documents with an LLM prompt.",
    "LangChain connects LLM components using LCEL.",
]

vectorstore = FAISS.from_texts(texts=documents, embedding=embedding_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Answer the question using only the provided documents.\n\nDocuments:\n{context}",
    ),
    MessagesPlaceholder("chat_history"),
    ("human", "{question}"),
])

rag_chain = (
    {
        "context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
        "question": RunnablePassthrough(),
        "chat_history": lambda x: x.get("chat_history", []),
    }
    | prompt
    | llm
    | StrOutputParser()
)

def chat(question: str, history: list) -> tuple[str, list]:
    result = rag_chain.invoke({"question": question, "chat_history": history})
    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=result))
    return result, history

chat_history: list = []

turn1, chat_history = chat("What is FAISS?", chat_history)
print(f"[1] {turn1}\n")

turn2, chat_history = chat("What are its main features?", chat_history)
print(f"[2] {turn2}\n")

turn3, chat_history = chat("How does it connect to LangChain?", chat_history)
print(f"[3] {turn3}")
```

---

## Self-contained application

```python
"""
langchain_rag_app.py

Run: python langchain_rag_app.py
Requires: langchain langchain-community langchain-groq faiss-cpu sentence-transformers langchain-text-splitters
"""
import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter

def build_rag_chain(documents: list[str]):
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
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
            "Answer the question using only the provided documents.\n\nDocuments:\n{context}",
        ),
        ("human", "{question}"),
    ])

    return (
        {
            "context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

def main() -> None:
    documents = [
        "FAISS is a high-speed vector search library developed at Facebook AI Research.",
        "Embedding models project text into a high-dimensional vector space.",
        "RAG combines retrieved documents with an LLM prompt.",
        "LangChain connects LLM components using LCEL.",
    ]

    chain = build_rag_chain(documents)

    while True:
        question = input("\nQuestion (q to quit): ").strip()
        if question.lower() == "q":
            break
        if not question:
            continue

        print("Answer: ", end="")
        for chunk in chain.stream(question):
            print(chunk, end="", flush=True)
        print()

if __name__ == "__main__":
    main()
```

---

## Conclusion

This series covered the LangChain API from first principles: LCEL and the Runnable interface, prompt templates, Retrievers, Tool Calling, Streaming, and a full RAG chain. Each component implements the same interface, which is why they compose cleanly with `|`.

The next series, ai-app-patterns-101, applies these components to real application patterns: chatbots, document Q&A, agents, and workflow automation.

<!-- toc:begin -->
## In this series

- [LangChain introduction — LCEL and the Runnable interface](./01-lcel-runnable-basics.md)
- [Prompt and LLM chain — assembling your first chain](./02-prompt-llm-chain.md)
- [Retriever — document search and context injection](./03-retriever.md)
- [Tool calling — connecting external tools](./04-tool-calling.md)
- [Streaming — handling real-time output](./05-streaming.md)
- **Putting it together — a complete chain in one file (current)**

<!-- toc:end -->

---

## References

- [LangChain RAG tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [LCEL reference](https://python.langchain.com/docs/expression_language/)
- [MessagesPlaceholder](https://python.langchain.com/docs/modules/model_io/prompts/quick_start/#messagesplaceholder)

Tags: LangChain, LCEL, Python, LLM
