---
title: 'HyperCLOVA X와 Solar API 사용하기'
series: korean-ai-stack-101
episode: 5
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

# HyperCLOVA X와 Solar API 사용하기

> 한국어 AI 스택 101 시리즈 (5/6)

예제 코드: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/ko/05-hyperclova-solar-api)

OpenAI나 Anthropic의 모델이 한국어를 지원하지만, 한국어 뉘앙스와 문화적 맥락에서는 한국어 전용으로 훈련된 모델이 더 자연스러운 결과를 냅니다. HyperCLOVA X(네이버)와 Solar(업스테이지)는 한국어에 특화된 상용 LLM입니다. 두 모델 모두 OpenAI API 호환 인터페이스를 제공해서 기존 코드를 크게 수정하지 않고도 사용할 수 있습니다.

다룰 내용은 다음과 같습니다.

- HyperCLOVA X API 기본 사용
- Solar API 기본 사용
- LangChain에 두 모델 통합
- 한국어 응답 품질 비교

---

## HyperCLOVA X API

네이버 클라우드 플랫폼 CLOVA Studio에서 API 키를 발급받습니다.

```python
import os

import requests

def call_hyperclova_x(
    messages: list[dict],
    model: str = "HCX-003",
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """
    HyperCLOVA X Chat Completions API 호출.
    OpenAI Chat Completions 호환 형식.
    """
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
    data = response.json()
    return data["result"]["message"]["content"]

# 기본 한국어 응답 테스트
messages = [
    {"role": "system", "content": "당신은 친절한 한국어 AI 어시스턴트입니다."},
    {"role": "user", "content": "한국 전통 음식 중 겨울에 먹기 좋은 음식 3가지를 추천해 주세요."},
]

response = call_hyperclova_x(messages)
print("HyperCLOVA X 응답:")
print(response)
```

---

## Solar API (업스테이지)

```python
import os

from openai import OpenAI

def call_solar(
    messages: list[dict],
    model: str = "solar-1-mini-chat",
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """
    Upstage Solar API 호출.
    OpenAI SDK 호환 인터페이스 사용.
    """
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

# Solar로 동일한 질문 테스트
messages = [
    {"role": "system", "content": "당신은 친절한 한국어 AI 어시스턴트입니다."},
    {"role": "user", "content": "한국 전통 음식 중 겨울에 먹기 좋은 음식 3가지를 추천해 주세요."},
]

response = call_solar(messages)
print("Solar 응답:")
print(response)
```

---

## LangChain 통합

LangChain의 `ChatOpenAI`는 `base_url` 파라미터로 OpenAI 호환 API를 지원합니다. Solar는 이 방식으로 바로 사용할 수 있습니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Solar API를 LangChain에 통합
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
        "당신은 한국어 글쓰기 전문가입니다.\n"
        "자연스럽고 명확한 한국어로 답변하세요.",
    ),
    ("human", "{question}"),
])

chain = prompt | solar_llm | StrOutputParser()

questions = [
    "이메일에서 '~드립니다'와 '~합니다'의 차이는 무엇인가요?",
    "존댓말과 반말을 구분하는 기준이 무엇인가요?",
]

for question in questions:
    answer = chain.invoke({"question": question})
    print(f"\n질문: {question}")
    print(f"답변: {answer}")
```

---

## RAG 파이프라인에 Solar 통합

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

# 한국어 문서 인덱싱
ko_documents = [
    "대한민국 헌법 제1조: 대한민국은 민주공화국이다.",
    "대한민국 헌법 제10조: 모든 국민은 인간으로서의 존엄과 가치를 가지며, 행복을 추구할 권리를 가진다.",
    "대한민국 헌법 제37조: 국민의 자유와 권리는 헌법에 열거되지 아니한 이유로 경시되지 아니한다.",
    "형사소송법 제244조: 피의자의 진술은 서면으로 작성하여야 하며, 피의자에게 열람하게 하거나 읽어 주어야 한다.",
    "민법 제750조: 고의 또는 과실로 인한 위법행위로 타인에게 손해를 가한 자는 그 손해를 배상할 책임이 있다.",
]

vectorstore = FAISS.from_texts(texts=ko_documents, embedding=embedding_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# Solar LLM — 한국어 법령 해석에 자연스러운 응답 생성
solar_llm = ChatOpenAI(
    model="solar-1-mini-chat",
    api_key=os.environ["UPSTAGE_API_KEY"],
    base_url="https://api.upstage.ai/v1/solar",
    temperature=0.3,  # 법령 해석은 낮은 temperature
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "다음 법령 조항을 참고해서 질문에 답하세요.\n"
        "전문 용어는 쉽게 풀어서 설명하세요.\n\n"
        "법령 조항:\n{context}",
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

answer = rag_chain.invoke("헌법에서 국민의 존엄성은 어떻게 보장되나요?")
print(f"답변:\n{answer}")
```

---

## 마무리

HyperCLOVA X와 Solar는 한국어 문화·언어적 맥락에서 더 자연스러운 응답을 생성합니다. Solar는 OpenAI SDK와 완벽히 호환되어 LangChain 코드를 거의 바꾸지 않고 교체할 수 있습니다. 다음 글에서는 지금까지 다룬 KoSimCSE 임베딩, CLOVA OCR, Solar LLM을 모두 조합해 완전한 한국어 RAG 파이프라인을 완성합니다.

<!-- blog-only:start -->
다음 글: [한국어 RAG 파이프라인 조합하기](./06-korean-rag-pipeline.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [KoSimCSE로 문장 유사도 구현하기](./02-kosimcse-similarity.md)
- [BGE-M3 다국어 임베딩 실전](./03-bge-m3-multilingual.md)
- [CLOVA OCR API로 문서 텍스트 추출](./04-clova-ocr.md)
- **HyperCLOVA X와 Solar API 사용하기 (현재 글)**
- 한국어 RAG 파이프라인 조합하기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [CLOVA Studio API 문서](https://api.ncloud-docs.com/docs/ai-application-service-clovastudio)
- [Upstage Solar API](https://developers.upstage.ai/docs/apis/chat)
- [LangChain ChatOpenAI](https://python.langchain.com/docs/integrations/chat/openai/)

Tags: Korean NLP, LLM, Embeddings, OCR
