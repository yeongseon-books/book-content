---
title: 'Streaming — handling real-time output'
series: langchain-101
episode: 5
language: en
status: publish-ready
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

# Streaming — handling real-time output

## Questions this post answers

- How does the return shape change when you switch from `invoke()` to `stream()`
- What is the practical difference between chain streaming and model-only streaming
- When do you need `astream()` or `astream_events()` instead of plain `stream()`
- How should streamed output be forwarded to a UI or API response

> Streaming is not a different chain design; it is a different way of consuming the chain while the model is still generating.

![Questions this post answers](../../../assets/langchain-101/05/05-01-questions-this-post-answers.en.png)
## Minimal runnable example

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

chain = (
    ChatPromptTemplate.from_template("Explain {topic} in three sentences.")
    | ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"])
    | StrOutputParser()
)

for chunk in chain.stream({"topic": "astream"}):
    print(chunk, end="", flush=True)
```

```
Output
Astream is a platform that allows users to create, share, and monetize live and on-demand video content. It was initially created to cater to the online streaming needs of gamers, but it has since expanded to support various types of content, including music, art, and talk shows. Astream offers features such as live chat, subscriptions, and tipping, making it a popular choice for content creators who want to engage with their audience and earn revenue through their online streams.
```

## What to notice in this code

- The chain definition is identical to `invoke()`; only the consumption pattern changes.
- With a parser attached, streaming yields text chunks. Without one, it yields message chunks.
- You can forward chunks immediately to the client or buffer them into a final string.
- Streaming improves perceived latency more than total wall-clock time.

## Where engineers get confused

- Streaming does not guarantee the full response finishes sooner.
- In async applications, `astream()` fits the event loop better than `stream()`.
- When you need lifecycle visibility, `astream_events()` is more useful than raw text chunks.

## Checklist

- [ ] I can consume the output of `stream()` incrementally
- [ ] I understand the difference between text chunks and message chunks
- [ ] I know when to switch to `astream()` in async code

LangChain 101 (5/6)

Example code: [github.com/yeongseon-books/langchain-101](https://github.com/yeongseon-books/langchain-101/tree/main/05-streaming)

## Questions this post answers

- How much code changes when you replace `invoke()` with `stream()`?
- When should you choose `astream()` versus `astream_events()`?
- What pattern works for reassembling streamed chunks into one string?
- What do you need to send streaming output through FastAPI?

> Streaming is not a different chain design. It is the same chain executed in a way that yields partial output instead of waiting for the final string.

## The flow at a glance

![The flow at a glance](../../../assets/langchain-101/05/05-02-the-flow-at-a-glance.en.png)
When an LLM generates a long response, waiting for the full text before displaying anything makes the experience feel slow. Streaming sends tokens to the output as they are generated. That is what you see in ChatGPT or Claude when text appears character by character.

In LangChain, streaming starts with `stream()`. Chain construction is identical to `invoke()` — only the call method changes.

Topics:

- using `stream()` with an LLM and a chain
- async streaming with `astream()`
- collecting streamed output into a string
- a practical FastAPI streaming endpoint
- `astream_events()` for fine-grained event control

---

## Basic streaming

`stream()` returns a generator. Iterate over it with a `for` loop.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

# stream directly from the LLM
print("=== LLM direct streaming ===")
for chunk in llm.stream("List five advantages of Python."):
    print(chunk.content, end="", flush=True)

print("\n\n=== chain streaming ===")
prompt = ChatPromptTemplate.from_messages([
    ("human", "Explain {topic} in three paragraphs."),
])

chain = prompt | llm | StrOutputParser()

for chunk in chain.stream({"topic": "vector search"}):
    print(chunk, end="", flush=True)

print()
```

```
Output
=== LLM direct streaming ===
Here are five advantages of Python:

1. **Easy to Learn**: Python is known for its simplicity and readability, making it a great language for beginners. Its syntax is designed to be easy to understand, and it has a relatively small number of keywords, which makes it easy to learn and remember.

2. **High-Level Language**: Python is a high-level language, which means it abstracts away many low-level details, allowing developers to focus on the logic of their program without worrying about the underlying mechanics of the computer. This makes it easier to write efficient and effective code.

3. **Versatile**: Python can be used for a wide range of applications, including web development, data analysis, machine learning, automation, and more. It's also often used as a scripting language for many operating systems and applications.

4. **Large Community and Resources**: Python has a massive and active community, which means there are many resources available for learning and troubleshooting. This includes extensive documentation, tutorials, and libraries, making it easier to find help when you need it.

5. **Cross-Platform**: Python can run on multiple operating systems, including Windows, macOS, and Linux. This makes it a great choice for developers who need to write code that can run on different platforms.

Overall, Python's ease of use, versatility, and large community make it a popular choice for many developers and applications.

=== chain streaming ===
Vector search is a technique used in various fields, including computer science, statistics, and data analysis. It involves comparing two or more vectors to determine their similarity or distance. In essence, a vector is a mathematical representation of an object or data point, with each element representing a dimension or feature. Vector search algorithms compute the similarity between two vectors by calculating their dot product, Euclidean distance, or cosine similarity, among other methods.

There are several applications of vector search, including text search, image search, and recommendation systems. In text search, for example, a vector can represent a document as a collection of word frequencies. The similarity between two documents can be calculated based on their vector representations, enabling the retrieval of relevant documents. Similarly, in image search, a vector can represent an image as a set of pixel values. Vector search algorithms can be used to identify images with similar features.

The most popular algorithm used for vector search is the Approximate Nearest Neighbor (ANN) search. ANN search uses techniques such as k-d trees, ball trees, or Locality-Sensitive Hashing (LSH) to efficiently search for similar vectors in a high-dimensional space. These algorithms trade off between search accuracy and computational efficiency, making them suitable for large-scale applications. Vector search has numerous applications in areas such as information retrieval, natural language processing, and machine learning, where it is used to improve the accuracy and efficiency of various tasks, including classification, clustering, and recommendation.
```

`end=""` and `flush=True` suppress the newline and force immediate output. `StrOutputParser()` extracts the string content from each `AIMessageChunk` during streaming.

---

## Collecting streamed output

When you need the full text after streaming, accumulate chunks in a list.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = (
    ChatPromptTemplate.from_messages([("human", "{question}")])
    | llm
    | StrOutputParser()
)

chunks = []
print("streaming: ", end="")
for chunk in chain.stream({"question": "What is FAISS?"}):
    print(chunk, end="", flush=True)
    chunks.append(chunk)

full_text = "".join(chunks)
print(f"\n\ntotal characters: {len(full_text)}")
```

```
Output
streaming: FAISS (Facebook AI Similarity Search) is an open-source library developed by Facebook that provides efficient similarity search and clustering for dense vectors. It is primarily designed for large-scale applications, such as search engines, recommendation systems, and clustering algorithms.

FAISS supports various indexing techniques, including:

1. **Flat**: A simple and efficient indexing method that stores all vectors in memory.
2. **IVF (Inverted File)**: A hierarchical indexing method that divides the vector space into multiple clusters and uses a separate index for each cluster.
3. **HNSW (Hierarchical Navigable Small World)**: A graph-based indexing method that uses a navigable small-world graph to efficiently search for similar vectors.
4. **OPQ (Orthogonal Projections)**: A preprocessing method that projects the vectors onto a lower-dimensional space using orthogonal projections.

FAISS provides several benefits, including:

1. **Efficient search**: FAISS can search for similar vectors in a matter of milliseconds, even for large datasets.
2. **Scalability**: FAISS can handle datasets with billions of vectors and scale to large clusters.
3. **Flexibility**: FAISS supports various indexing techniques and can be used in a variety of applications.

Some common use cases for FAISS include:

1. **Similarity search**: FAISS can be used to find similar vectors in a dataset, such as searching for similar images or text documents.
2. **Clustering**: FAISS can be used to cluster similar vectors together, such as grouping similar customers or products.
3. **Recommendation systems**: FAISS can be used to build recommendation systems that suggest similar items to users based on their past behavior.

Overall, FAISS is a powerful library that provides efficient similarity search and clustering capabilities for dense vectors, making it a popular choice for large-scale applications.

total characters: 1906
```

---

## astream() — async streaming

In async frameworks like FastAPI, use `astream()` with `async for`.

```python
import asyncio
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = (
    ChatPromptTemplate.from_messages([("human", "Explain {topic} briefly.")])
    | llm
    | StrOutputParser()
)

async def stream_response(topic: str) -> None:
    print(f"streaming: {topic}")
    async for chunk in chain.astream({"topic": topic}):
        print(chunk, end="", flush=True)
    print()

async def main() -> None:
    await stream_response("embedding vectors")
    await stream_response("FAISS indexes")

asyncio.run(main())
```

```
Output
streaming: embedding vectors
**Vector Embeddings: A Brief Overview**

Vector embeddings are a fundamental concept in natural language processing (NLP) and machine learning. They enable computers to understand complex data by representing it as numerical vectors.

**Key Concepts:**

1. **Tokenization**: Breaking down text into individual words or tokens.
2. **Vector Space**: A high-dimensional space where each token is represented as a numerical vector.
3. **Embeddings**: Learned vector representations of tokens that capture their semantic meaning.

**How Embeddings Work:**

1. **Training**: A neural network model is trained on a large dataset of text, where the goal is to predict the next word in a sequence.
2. **Learning**: The model learns to represent each token as a vector in the vector space, such that similar tokens are close together.
3. **Embedding**: The learned vector representations of tokens are extracted and stored as embeddings.

**Example:**

Suppose we have two words "king" and "queen". Their embeddings might be:

* king: [0.1, 0.2, 0.3, ...]
* queen: [0.1, 0.2, -0.2, ...]

These vectors capture the semantic similarity between "king" and "queen", allowing the model to understand their relationship.

**Popular Embedding Techniques:**

1. Word2Vec
2. GloVe (Global Vectors for Word Representation)
3. FastText

**Advantages:**

1. Improved performance in NLP tasks, such as sentiment analysis and language translation.
2. Ability to capture nuanced semantic relationships between words.

By representing tokens as numerical vectors, vector embeddings enable computers to understand complex data and make informed decisions.
streaming: FAISS indexes
**FAISS Indexes: An Overview**

FAISS (Facebook AI Similarity Search) is a library for efficient similarity search and clustering of dense vectors. It provides various indexing techniques to speed up the search process. Here's a brief overview of FAISS indexes:

### 1. Flat Index (IVF)

- **Description:** The most basic index type in FAISS, which stores all the vectors in memory.
- **Advantages:** Fast lookup, suitable for small datasets.
- **Disadvantages:** Not scalable for large datasets.

### 2. Inverted File (IVF)

- **Description:** A hierarchical index that divides the vector space into regions (centroids) and stores vectors in each region.
- **Advantages:** Scalable and efficient for large datasets.
- **Disadvantages:** Can be slow for exact matches.

### 3. Product Quantization (PQ)

- **Description:** A technique that divides each vector dimension into multiple bins (centroids) and stores the bin indices.
- **Advantages:** Fast and efficient for approximate matches.
- **Disadvantages:** Can lose some precision.
... (truncated)
```

---

## FastAPI streaming endpoint

In production, stream to the client over HTTP using Server-Sent Events.

```python
import os

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

app = FastAPI()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = (
    ChatPromptTemplate.from_messages([("human", "{question}")])
    | llm
    | StrOutputParser()
)

@app.get("/stream")
async def stream_endpoint(question: str):
    async def generate():
        async for chunk in chain.astream({"question": question}):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
```

Start the server:

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

Test it:

```bash
curl "http://localhost:8000/stream?question=What+is+RAG"
```

---

## astream_events() for fine-grained control

`astream_events()` exposes individual events from each component in the chain.

```python
import asyncio
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = (
    ChatPromptTemplate.from_messages([("human", "Explain {topic}.")])
    | llm
    | StrOutputParser()
)

async def main() -> None:
    async for event in chain.astream_events({"topic": "FAISS"}, version="v2"):
        event_type = event["event"]
        if event_type == "on_llm_stream":
            chunk = event["data"].get("chunk", "")
            if hasattr(chunk, "content") and chunk.content:
                print(chunk.content, end="", flush=True)
    print()

asyncio.run(main())
```

`astream_events()` is useful when a chain has multiple components and you need to distinguish which one is producing output. For simple streaming, `astream()` is easier.

---

## What to notice in this code

- The chain definition barely changes from the `invoke()` version. The real change is how you consume output.
- `stream()` means synchronous iteration, while `astream()` means asynchronous iteration over the same logical response.
- Collecting chunks into a list and joining them later is a common pattern for logging, caching, or post-processing.
- `astream_events()` exposes chain-level events, which is useful for debugging and instrumentation beyond simple token display.

## Where engineers get confused

- Streaming does not change the final answer format. It changes when the application receives each piece.
- Async streaming affects the caller too, so your framework and endpoint style must support async flow.
- Event streams are powerful, but they are unnecessary overhead if all you need is progressive text rendering.

## Checklist

- [ ] I can run the same chain with both `invoke()` and `stream()`
- [ ] I can explain the difference between `astream()` and `astream_events()`
- [ ] I understand how `StreamingResponse` fits around streamed chunks in FastAPI

## Conclusion

Streaming in LangChain requires one change: replace `invoke()` with `stream()` or `astream()`. Chain structure stays the same. With FastAPI, `StreamingResponse` delivers the output to clients in real time.

The final post assembles all the components covered in this series into one complete chain.

<!-- toc:begin -->
## In this series

- [LangChain introduction — LCEL and the Runnable interface](./01-lcel-runnable-basics.md)
- [Prompt and LLM chain — assembling your first chain](./02-prompt-llm-chain.md)
- [Retriever — document search and context injection](./03-retriever.md)
- [Tool calling — connecting external tools](./04-tool-calling.md)
- **Streaming — handling real-time output (current)**
- Putting it together — a complete chain in one file (upcoming)

<!-- toc:end -->

---

## References

- [LangChain streaming guide](https://python.langchain.com/docs/expression_language/streaming/)
- [astream_events reference](https://python.langchain.com/docs/expression_language/interface/)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)

Tags: LangChain, LCEL, Python, LLM
