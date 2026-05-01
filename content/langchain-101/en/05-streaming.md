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

~~~
Output
Astream is a popular streaming platform that allows users to watch and interact with live and on-demand content. It was primarily used for music streaming, with features that allowed users to create and manage their own playlists and discover new music through recommendations. Astream was known for its user-friendly interface and social features, which enabled users to connect with other listeners and engage in real-time discussions about their favorite artists and songs.
~~~

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

~~~
Output
=== LLM direct streaming ===
Here are five advantages of Python:

1. **Easy to Learn**: Python has a simple syntax and is relatively easy to learn, making it a great language for beginners and experienced programmers alike. Its readability and simplicity make it a popular choice for educational purposes.

2. **High-Level Language**: Python is a high-level language, meaning it abstracts away many low-level details, allowing developers to focus on the logic of the program without worrying about the underlying mechanics. This makes Python a great choice for rapid prototyping and development.

3. **Cross-Platform**: Python can run on multiple operating systems, including Windows, macOS, and Linux. This makes it a great choice for developers who need to create applications that can run on different platforms.

4. **Extensive Libraries**: Python has a vast collection of libraries and frameworks that make it easy to perform a wide range of tasks, from data analysis to web development. Some popular libraries include NumPy, pandas, and scikit-learn for data science, and Django and Flask for web development.

5. **Large Community**: Python has a large and active community of developers, which means there are many resources available to help with learning and troubleshooting. This community also contributes to the creation of new libraries and frameworks, which makes it easier to find solutions to common problems.

These advantages make Python a popular choice for a wide range of applications, from data science and machine learning to web development and automation.

=== chain streaming ===
Vector search, also known as similarity search or nearest neighbor search, is a fundamental concept in various fields such as computer science, data analysis, and information retrieval. The primary goal of vector search is to find the most similar or nearest neighbors to a given query vector within a large dataset. This is achieved by calculating the similarity between the query vector and each vector in the dataset, and then ranking the vectors based on their similarity scores. The similarity score is typically calculated using a distance metric such as Euclidean distance, cosine similarity, or dot product.

Vector search is often used in applications such as image and text search, recommendation systems, and clustering. For instance, in image search, a query image is represented as a vector in a high-dimensional space, and the algorithm searches for the most similar images in the dataset. The similarity score is calculated based on the features extracted from the images, such as color, texture, and shape. Similarly, in text search, a query text is represented as a vector, and the algorithm searches for the most similar texts in the dataset based on the word frequencies or semantic meanings.

The efficiency of vector search algorithms is crucial, especially when dealing with large datasets. Traditional algorithms such as brute-force search or linear scan have a time complexity of O(n), which becomes impractical for large datasets. To overcome this, various indexing techniques such as k-d trees, ball trees, and locality-sensitive hashing (LSH) have been developed. These indexing techniques allow for faster search times, often with a time complexity of O(log n) or O(1), making vector search practical for real-world applications.
~~~

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

~~~
Output
streaming: FAISS (Facebook AI Similarity Search) is an open-source library developed by Facebook AI Research (FAIR) for efficiently searching and clustering large collections of dense vectors. It is primarily used for similarity search, k-nearest neighbors (k-NN) search, and clustering tasks.

FAISS is based on the following key concepts:

1. **Similarity search**: Given a query vector, find the top N most similar vectors in a large dataset. This is useful in a variety of applications, such as image or text search.
2. **k-nearest neighbors (k-NN)**: Given a query vector, find the k nearest vectors in the dataset. This is useful in applications like recommendation systems or clustering.
3. **Clustering**: Group similar vectors together based on their similarities.

FAISS supports a range of indexing algorithms, including:

1. **Flat indexing**: Simple, but not scalable for large datasets.
2. **Hierarchical Navigable Small World (HNSW)**: A graph-based indexing algorithm that provides fast search performance.
3. **Inverted File (IVF)**: A tree-based indexing algorithm that is suitable for high-dimensional vectors.
4. **Product Quantization (PQ)**: A method that reduces the dimensionality of vectors by projecting them onto a lower-dimensional space.

The key benefits of FAISS are:

1. **High-performance search**: FAISS enables fast search times, even for large datasets.
2. **Efficient memory usage**: FAISS uses optimized memory allocation and caching to reduce memory usage.
3. **Scalability**: FAISS can handle large datasets and support distributed search.

FAISS has applications in various domains, such as:

1. **Computer Vision**: Image search, object detection, and image classification.
2. **Natural Language Processing (NLP)**: Text search, sentiment analysis, and language modeling.
3. **Recommendation Systems**: Personalized recommendations based on user behavior and preferences.
4. **Clustering**: Grouping similar items or users together.

In summary, FAISS is a powerful library for efficiently searching and clustering large collections of dense vectors, with applications in various domains.

total characters: 2119
~~~

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

~~~
Output
streaming: embedding vectors
**Embedding Vectors: A Brief Overview**

Embedding vectors is a fundamental concept in natural language processing (NLP) and machine learning, which enables the representation of complex data, such as text or images, in a compact and meaningful way.

**What are Embedding Vectors?**

Embedding vectors are a type of dense vector representation that captures the semantic meaning of a word, phrase, or object. They are used to map input data to a continuous vector space, where semantically similar inputs are mapped to nearby points.

**Key Characteristics:**

1. **Dense Vectors:** Embedding vectors are dense, meaning they contain a fixed-size vector representation of the input data.
2. **Continuous Space:** The embedding space is continuous, allowing for the calculation of distances between vectors.
3. **Semantic Meaning:** Embedding vectors capture the semantic meaning of the input data, enabling tasks like word similarity, text classification, and clustering.

**Common Applications:**

1. **Word Embeddings (Word2Vec, GloVe):** Representing words as vectors to capture their semantic meaning.
2. **Image Embeddings:** Representing images as vectors to enable tasks like image classification and clustering.
3. **Topic Modeling:** Representing topics as vectors to enable tasks like document classification and clustering.

**Key Techniques:**

1. **Word2Vec:** A popular word embedding algorithm that learns vector representations of words based on their context.
2. **GloVe:** A word embedding algorithm that learns vector representations of words based on their co-occurrence in a corpus.
3. **T-SNE:** A dimensionality reduction technique used to visualize high-dimensional embedding spaces.

By leveraging embedding vectors, researchers and practitioners can build more effective and efficient models for a wide range of NLP and machine learning tasks.
streaming: FAISS indexes
**FAISS Indexes Overview**

FAISS (Facebook AI Similarity Search) is a library for efficient similarity search and clustering of dense vectors. It provides a set of indexing algorithms to efficiently store and query large collections of vectors.

**Types of FAISS Indexes:**

1. **Flat Index:** A simple, non-optimized index that is suitable for small datasets. It stores all vectors in memory and uses a linear search to find similar vectors.

2. **IVF (Inverted File)**: A hierarchical index that divides the vector space into multiple clusters. It is suitable for medium-sized datasets and is faster than the flat index.

3. **HNSW (Hierarchical Navigable Small World)**: A graph-based index that uses a navigable small world structure to efficiently search for similar vectors. It is suitable for large datasets and is faster than the IVF index.

4. **OPQ (Orthogonal Projection Quantization)**: An indexing technique that projects high-dimensional vectors onto a lower-dimensional space using orthogonal projections. It can be used in conjunction with other indexing algorithms to improve performance.

**Key Features:**

- Efficient memory usage and search speed.
- Support for various indexing algorithms and similarity metrics.
- Multi-threaded and multi-CPU support for improved performance.
- Integration with popular deep learning frameworks.

**Use Cases:**

- Image and video search.
- Recommendation systems.
- Anomaly detection.
- Clustering and dimensionality reduction.

**When to Use:**

- When dealing with large collections of high-dimensional vectors.
... (truncated)
~~~

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
