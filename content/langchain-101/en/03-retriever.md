---
title: "LangChain 101 (3/6): Retriever — document search and context injection"
series: langchain-101
episode: 3
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LangChain
- LCEL
- Python
- LLM
last_reviewed: '2026-05-01'
seo_description: A Retriever does not store knowledge by itself; it turns a question
  into the subset of documents worth showing the model.
---

# LangChain 101 (3/6): Retriever — document search and context injection

RAG quality is often decided before the model writes a single token. If retrieval brings back the wrong chunks, prompt tuning rarely saves the answer, so the search boundary deserves attention first.

This is the third post in the LangChain 101 series. It covers Retrievers, VectorStores, and the basic pattern for injecting retrieved context into an LLM prompt.

![The flow at a glance](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/03/03-02-the-flow-at-a-glance.en.png)
*The flow at a glance*
> A Retriever does not store knowledge by itself; it turns a question into the subset of documents worth showing the model.

## Questions to Keep in Mind

- How does a Retriever turn VectorStore results into LLM context?
- When retrieval is empty or wrong, what should you inspect before blaming the model?
- What metadata must be saved and reloaded with a VectorStore?

## Minimal runnable example

```python
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_texts([
    "FAISS is a high-speed vector search library.",
    "A Retriever finds documents relevant to a question.",
], embedding)
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

print(retriever.invoke("What does a Retriever do?")[0].page_content)
```

## Creating a FAISS VectorStore

![Documents turning into a vector index](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/03/03-01-creating-a-faiss-vectorstore.en.png)

*Documents turning into a vector index*
LangChain's `FAISS` class wraps the FAISS index behind a VectorStore interface. Pass a list of text strings and an embedding model — the class handles the rest.

```bash
pip install langchain langchain-community langchain-huggingface faiss-cpu sentence-transformers langchain-groq
```

```python
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    "FAISS is a high-speed vector search library developed at Facebook AI Research.",
    "Cosine similarity measures the directional similarity between two vectors.",
    "Embedding models project text into a high-dimensional vector space.",
    "sentence-transformers specializes in sentence-level embeddings.",
    "Vector search captures semantic similarity that keyword search misses.",
    "RAG combines retrieved documents with an LLM prompt.",
    "Chunking strategies split long documents into embedding-sized units.",
]

vectorstore = FAISS.from_texts(
    texts=documents,
    embedding=embedding_model,
)

print(f"index vector count: {vectorstore.index.ntotal}")
```

The key distinction is between **indexing time** and **query time**. Converting documents into vectors and storing them is a cost you pay upfront. At request time, you only search the pre-built index. When this boundary blurs, demos work but production services suffer unnecessary latency.

---

## Creating a Retriever

![Similarity mmr threshold search paths](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/03/03-02-creating-a-retriever.en.png)

*Similarity mmr threshold search paths*
`as_retriever()` wraps the VectorStore in the Retriever interface.

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",  # default top-k search; FAISS defaults to L2 distance
    search_kwargs={"k": 3},    # number of results to return
)

docs = retriever.invoke("how vector search works")

for i, doc in enumerate(docs):
    print(f"[{i}] {doc.page_content}")
```

Three `search_type` options are available:

- `"similarity"`: plain top-k retrieval; in the default FAISS path this uses L2 distance unless you configure a different metric
- `"mmr"`: maximal marginal relevance — balances relevance and diversity
- `"similarity_score_threshold"`: returns only documents above a similarity threshold

`encode_kwargs={"normalize_embeddings": True}` makes the embedding vectors unit length, so L2 ranking and cosine-style ranking often become close in practice. But that normalization does **not** change the FAISS default itself: unless you configure a different distance strategy, the backend still searches with `IndexFlatL2`.

```python
# MMR — prioritize diversity
retriever_mmr = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 10, "lambda_mult": 0.5},
)
```

From an operational perspective, `k` and `search_type` are tuning points you should adjust before touching the prompt. When answers go off-track, many teams rewrite the prompt, but the real cause is often retrieval recall or context noise.

---

## Connecting a Retriever to a chain

![Retrieved documents becoming prompt context](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/03/03-03-connecting-a-retriever-to-a-chain.en.png)

*Retrieved documents becoming prompt context*
The standard RAG pattern: retrieve relevant documents, inject them as context, pass to the LLM.

```python
import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

def format_docs(docs: list) -> str:
    """Combine a list of documents into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    "FAISS is a high-speed vector search library developed at Facebook AI Research.",
    "Cosine similarity measures the directional similarity between two vectors.",
    "Embedding models project text into a high-dimensional vector space.",
    "sentence-transformers specializes in sentence-level embeddings.",
    "Vector search captures semantic similarity that keyword search misses.",
    "RAG combines retrieved documents with an LLM prompt.",
]

vectorstore = FAISS.from_texts(texts=documents, embedding=embedding_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Answer the question using only the provided documents. "
        "If the answer is not in the documents, say you don't know.\n\n"
        "Documents:\n{context}",
    ),
    ("human", "{question}"),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

questions = [
    "What is FAISS?",
    "How does the RAG pattern work?",
    "What do embedding models do?",
]

for question in questions:
    print(f"\nquestion: {question}")
    answer = rag_chain.invoke(question)
    print(f"answer: {answer}")
```

The key is the chain input dict:

```python
{
    "context": retriever | format_docs,
    "question": RunnablePassthrough(),
}
```

`retriever | format_docs` receives the query → retrieves relevant documents → combines them into a string. `RunnablePassthrough()` forwards the query unchanged to the `"question"` key.

---

## Saving and reloading a VectorStore

![Saving and reloading index lifecycle](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/03/03-04-saving-and-reloading-a-vectorstore.en.png)

*Saving and reloading index lifecycle*
```python
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    "FAISS is a high-speed vector search library developed at Facebook AI Research.",
    "RAG combines retrieved documents with an LLM prompt.",
]

vectorstore = FAISS.from_texts(texts=documents, embedding=embedding_model)

# save
vectorstore.save_local("faiss_store")
print("saved")

# reload
loaded_store = FAISS.load_local(
    "faiss_store",
    embeddings=embedding_model,
    allow_dangerous_deserialization=True,
)
print(f"reloaded: {loaded_store.index.ntotal} vectors")

# verify
results = loaded_store.similarity_search("vector search", k=1)
print(f"\nresult: {results[0].page_content}")
```

---

## Checking retrieval quality with numbers

A common RAG blind spot is relying on gut feeling — "the results look reasonable." At minimum, log a table per query so you can compare retrieval quality quantitatively before touching the prompt.

| query | expected keyword | top-1 hit? | notes |
|---|---|---|---|
| `Who developed FAISS?` | `Facebook AI Research` | Pass | top-1 correct |
| `What does RAG combine?` | `retrieved documents + LLM` | Pass | stable through top-2 |
| `What is BM25?` | none (out-of-corpus) | Fail (intended) | absence response needed |

Keep this table separate from model evaluation. If retrieval fails but you only look at model output, you end up tuning the prompt when the real problem is upstream.

## Retriever implementation patterns compared

There is more than one way to wire a Retriever. Three patterns dominate at the introductory level:

| Pattern | LCEL shape | Advantage | Downside |
|---|---|---|---|
| Simple pipe | `retriever \| format_docs` | Easy to understand | Weak length control |
| Score filter | `retriever_with_score \| filter \| format` | Reduces noise docs | More code |
| Re-ranking | `retriever \| reranker \| format` | Higher precision possible | Added latency |

In practice, start with the simple pipe and add score filtering or re-ranking only after quality issues are confirmed.

## Score-based filtering example

The code below uses `similarity_search_with_score` to drop low-relevance documents before they enter the prompt context.

```python
from langchain_core.runnables import RunnableLambda

def retrieve_with_threshold(query: str, threshold: float = 0.9):
    pairs = vectorstore.similarity_search_with_score(query, k=4)
    # L2 distance: lower is more similar
    filtered = [doc for doc, score in pairs if score <= threshold]
    return filtered

def docs_to_context(docs: list) -> str:
    if not docs:
        return "NO_CONTEXT_FOUND"
    return "\n\n".join(d.page_content for d in docs)

retrieval_branch = RunnableLambda(retrieve_with_threshold) | RunnableLambda(docs_to_context)
```

The point is to not trust Retriever output blindly — apply one more application-level filter. In noisy corpora this filtering step often matters more than prompt refinement.

## Designing documents with metadata filters in mind

Retriever quality is not solely about the embedding model. How you attach metadata at ingestion time matters just as much.

```python
from langchain_core.documents import Document

docs = [
    Document(
        page_content="FAISS supports exact and approximate nearest-neighbor search.",
        metadata={"source": "faiss-intro", "topic": "vector-search", "lang": "en"},
    ),
    Document(
        page_content="RAG combines retrieval context with generation.",
        metadata={"source": "rag-guide", "topic": "rag", "lang": "en"},
    ),
]
```

When you later want to search only `topic=rag`, missing metadata forces you to rely on text similarity across the entire corpus. Including at least `source`, `topic`, `lang`, and `updated_at` at ingestion gives you operational flexibility from day one.

## Tracing the Retriever span in LangSmith

When you view a Retriever-containing chain in LangSmith, the retrieval step appears as a separate run before the LLM step.

```text
[trace] run_type=chain name=rag_chain latency_ms=1198
  [child] run_type=retriever name=VectorStoreRetriever latency_ms=71 k=3
  [child] run_type=prompt name=ChatPromptTemplate latency_ms=2
  [child] run_type=llm name=ChatGroq latency_ms=1089 tokens_in=522 tokens_out=118
```

This alone lets you isolate latency causes immediately. If retrieval is 70 ms but the total is 1.2 s, model output length — not search tuning — is the bottleneck. If retrieval exceeds 600 ms, inspect index structure and filter strategy first.

## Retriever failure checklist

- **Query log**: Are you storing both the raw user question and the normalized query separately?
- **Hit log**: Do you record top-k document IDs, scores, and sources?
- **Empty-hit rate**: Are you monitoring the percentage of queries that return no usable context?
- **Index version**: Can you trace which index snapshot served a given request?
- **Fallback path**: Is there a defined response policy when context is absent?

These five items alone let you answer "Why did it answer yesterday but say 'I don't know' today?" with evidence.

## Choosing between MMR and similarity

A common question is when to use MMR. The decision rule is straightforward: if the query is narrow and specific, similarity wins; if the query is broad or the corpus has heavy duplication, MMR often helps.

| Condition | Recommended search_type | Reason |
|---|---|---|
| Definition question (e.g. "What is FAISS?") | similarity | Focus on 1-2 correct docs |
| Comparison question (e.g. "RAG vs keyword search") | mmr | Need diverse viewpoints |
| Noisy corpus | similarity + threshold | Drop low-score results |

```python
retriever_similarity = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3},
)

retriever_mmr = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 12, "lambda_mult": 0.4},
)
```

In production, teams often assign a default search type per question category — FAQ-style questions use similarity, exploratory questions use MMR — which stabilizes average quality.

## Retriever + prompt length control

Even when retrieval quality is high, excessive context length increases input cost and latency. Placing a length-control function after the retriever is a pattern that matters in production.

```python
def trim_context(docs: list, max_chars: int = 1200) -> str:
    buf = []
    total = 0
    for doc in docs:
        text = doc.page_content.strip()
        if total + len(text) > max_chars:
            break
        buf.append(text)
        total += len(text)
    return "\n\n".join(buf)

context_chain = retriever | trim_context
```

With this function in place, even a large `k` keeps prompt input length bounded. This is especially effective for stabilizing first-token latency in streaming responses.

## Turning search failures into user-friendly responses

When retrieval returns nothing, simply answering "I don't know" breaks the user experience. A response policy that suggests next actions is essential.

| Situation | Recommended response |
|---|---|
| No context found | "The current index has no information on this topic. Try rephrasing your question." |
| Low scores | "Confidence is low for this answer. Try narrowing your question scope." |
| Conflicting documents | "Sources disagree. Specify a preferred source and I can narrow the answer." |

A Retriever looks like a simple technical component, but these policies complete the actual service quality.

## What to notice in this code

- The VectorStore is the storage layer, while the Retriever is the query interface layered on top of it.
- `retriever | format_docs` is the standard LCEL bridge from search results into prompt-ready context.
- `RunnablePassthrough()` preserves the original user question as a separate key so the prompt can see both context and question.
- The save and reload example matters because retrievers usually sit on top of reusable indexes, not one-off in-memory demos.

## Where engineers get confused

- The retriever does not generate the answer. It only selects documents; the LLM still synthesizes the response.
- Poor retrieval quality is often misdiagnosed as a prompt problem. Check chunking, embeddings, and `k` before rewriting the prompt.
- Simple document concatenation can overflow the context window, so `format_docs` is also a control point for length.

## Checklist

- [ ] I can explain the difference between a VectorStore and a Retriever
- [ ] I know which `search_kwargs` values I am likely to tune first
- [ ] I understand why retrieved documents must be formatted before prompt injection

## Conclusion

The Retriever interface abstracts whatever search system sits behind it. The `context: retriever | format_docs, question: RunnablePassthrough()` pattern is the standard structure for RAG chains in LangChain.

The next post covers Tool Calling — how an LLM can call external functions and incorporate their results into its response.

## Answering the Opening Questions

- **How does a Retriever turn VectorStore results into LLM context?**
  A Retriever returns Documents from the VectorStore and passes them as context text or document objects that the chain can consume.

- **When retrieval is empty or wrong, what should you inspect before blaming the model?**
  Inspect the embedding model, query text, top_k, filters, and retrieved source text before blaming the LLM. Bad context produces bad answers.

- **What metadata must be saved and reloaded with a VectorStore?**
  Persist document ids, source text, metadata, embedding model, index version, and storage paths so reloaded results remain interpretable.

<!-- toc:begin -->
## In this series

- [LangChain 101 (1/6): LangChain introduction — LCEL and the Runnable interface](./01-lcel-runnable-basics.md)
- [LangChain 101 (2/6): Prompt and LLM chain — assembling your first chain](./02-prompt-llm-chain.md)
- **LangChain 101 (3/6): Retriever — document search and context injection (current)**
- LangChain 101 (4/6): Tool calling — connecting external tools (upcoming)
- LangChain 101 (5/6): Streaming — handling real-time output (upcoming)
- LangChain 101 (6/6): Putting it together — a complete chain in one file (upcoming)

<!-- toc:end -->

---

## References

- [LangChain Retriever interface](https://python.langchain.com/docs/modules/data_connection/retrievers/)
- [FAISS VectorStore](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- [Building a RAG chain](https://python.langchain.com/docs/use_cases/question_answering/)

Tags: LangChain, LCEL, Python, LLM
