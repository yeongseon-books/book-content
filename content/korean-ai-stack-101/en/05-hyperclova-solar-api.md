---
title: 'Using HyperCLOVA X and Solar API'
series: korean-ai-stack-101
episode: 5
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

# Using HyperCLOVA X and Solar API

> Korean AI Stack 101 (5/6)

Example code: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/en/05-hyperclova-solar-api)

OpenAI and Anthropic models support Korean, but models trained primarily on Korean corpora produce more natural output on Korean cultural nuance and idiomatic expression. HyperCLOVA X (NAVER) and Solar (Upstage) are commercial LLMs built with Korean as a first-class language. Both expose OpenAI-compatible chat completion interfaces, so switching requires minimal code changes.

Topics:

- HyperCLOVA X API basics
- Solar API basics
- integrating both into LangChain
- RAG with a Korean-specialized LLM

---

## HyperCLOVA X API

Obtain an API key from NAVER Cloud Platform's CLOVA Studio.

```python
import os

import requests

def call_hyperclova_x(
    messages: list[dict],
    model: str = "HCX-003",
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """Call HyperCLOVA X Chat Completions API (OpenAI-compatible format)."""
    api_key = os.environ["CLOVA_STUDIO_API_KEY"]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "maxTokens": max_tokens,
        "temperature": temperature,
    }

    response = requests.post(
        "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["result"]["message"]["content"]

messages = [
    {"role": "system", "content": "You are a helpful AI assistant specializing in Korean culture."},
    {"role": "user", "content": "What are three traditional Korean foods especially popular in winter?"},
]

response = call_hyperclova_x(messages)
print("HyperCLOVA X response:")
print(response)
```

---

## Solar API (Upstage)

Solar's OpenAI-compatible interface means you can use the standard `openai` Python package.

```python
import os

from openai import OpenAI

def call_solar(
    messages: list[dict],
    model: str = "solar-1-mini-chat",
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """Call Upstage Solar API using the OpenAI SDK."""
    client = OpenAI(
        api_key=os.environ["UPSTAGE_API_KEY"],
        base_url="https://api.upstage.ai/v1/solar",
    )

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content

messages = [
    {"role": "system", "content": "You are a helpful AI assistant specializing in Korean culture."},
    {"role": "user", "content": "What are three traditional Korean foods especially popular in winter?"},
]

response = call_solar(messages)
print("Solar response:")
print(response)
```

---

## LangChain integration

LangChain's `ChatOpenAI` accepts a `base_url` parameter for OpenAI-compatible APIs. Solar integrates with no custom code.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

solar_llm = ChatOpenAI(
    model="solar-1-mini-chat",
    api_key=os.environ["UPSTAGE_API_KEY"],
    base_url="https://api.upstage.ai/v1/solar",
    temperature=0.7,
    max_tokens=512,
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert on Korean language and writing.\n"
        "Answer clearly and naturally.",
    ),
    ("human", "{question}"),
])

chain = prompt | solar_llm | StrOutputParser()

questions = [
    "What is the difference between formal and informal speech levels in Korean?",
    "When should you use honorific language in Korean business settings?",
]

for question in questions:
    answer = chain.invoke({"question": question})
    print(f"\nquestion: {question}")
    print(f"answer: {answer}")
```

---

## Korean RAG with Solar

```python
import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

embedding_model = HuggingFaceEmbeddings(
    model_name="BM-K/KoSimCSE-roberta-multitask",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# Korean legal documents
ko_documents = [
    "대한민국 헌법 제1조: 대한민국은 민주공화국이다.",
    "대한민국 헌법 제10조: 모든 국민은 인간으로서의 존엄과 가치를 가지며, 행복을 추구할 권리를 가진다.",
    "대한민국 헌법 제37조: 국민의 자유와 권리는 헌법에 열거되지 아니한 이유로 경시되지 아니한다.",
    "형사소송법 제244조: 피의자의 진술은 서면으로 작성하여야 하며, 피의자에게 열람하게 하거나 읽어 주어야 한다.",
    "민법 제750조: 고의 또는 과실로 인한 위법행위로 타인에게 손해를 가한 자는 그 손해를 배상할 책임이 있다.",
]

vectorstore = FAISS.from_texts(texts=ko_documents, embedding=embedding_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

solar_llm = ChatOpenAI(
    model="solar-1-mini-chat",
    api_key=os.environ["UPSTAGE_API_KEY"],
    base_url="https://api.upstage.ai/v1/solar",
    temperature=0.3,  # low temperature for legal interpretation
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Answer the question based on the legal provisions below.\n"
        "Explain technical terms in plain language.\n\n"
        "Legal provisions:\n{context}",
    ),
    ("human", "{question}"),
])

def format_docs(docs: list) -> str:
    return "\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | solar_llm
    | StrOutputParser()
)

answer = rag_chain.invoke("How does the Korean constitution protect human dignity?")
print(f"answer:\n{answer}")
```

---

## Conclusion

Both HyperCLOVA X and Solar produce more natural Korean output than general-purpose multilingual models on culturally specific or idiomatically rich content. Solar's complete OpenAI SDK compatibility means you can swap it into any existing LangChain chain by changing two parameters. The next post assembles everything covered in this series — KoSimCSE embeddings, CLOVA OCR, and Solar — into a complete Korean RAG pipeline.

<!-- toc:begin -->
## In this series

- [Korean embedding models compared — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [Building sentence similarity search with KoSimCSE](./02-kosimcse-similarity.md)
- [BGE-M3 multilingual embedding in practice](./03-bge-m3-multilingual.md)
- [Document text extraction with CLOVA OCR API](./04-clova-ocr.md)
- **Using HyperCLOVA X and Solar API (current)**
- Assembling a Korean RAG pipeline (upcoming)

<!-- toc:end -->

---

## References

- [CLOVA Studio API documentation](https://api.ncloud-docs.com/docs/ai-application-service-clovastudio)
- [Upstage Solar API](https://developers.upstage.ai/docs/apis/chat)
- [LangChain ChatOpenAI](https://python.langchain.com/docs/integrations/chat/openai/)

Tags: Korean NLP, LLM, Embeddings, OCR
