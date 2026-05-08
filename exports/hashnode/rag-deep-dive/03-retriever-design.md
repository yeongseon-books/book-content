
# Retriever Design — VectorStoreRetriever and MMR

<!-- a-grade-intro:begin -->
## Questions this post answers

- What contract does `BaseRetriever` enforce beyond returning documents?
- Where does `VectorStoreRetriever` branch into `similarity`, `mmr`, and threshold mode?
- Why does `fetch_k` need to be wider than `k` for MMR to matter?
- How does `lambda_mult` change redundancy versus coverage?

> A retriever is not just a nearest-neighbor fetcher. It is the policy layer that decides how candidate evidence becomes final context.

![Questions this post answers](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/03/03-01-questions-this-post-answers.en.png)

*Questions this post answers*
<!-- a-grade-intro:end -->

> RAG Deep Dive series (3/6)

<!-- a-grade-example:begin -->
## Minimal runnable example

Example file: `/root/Github/rag-deep-dive/en/03-retriever-design/main.py`

```bash
export GROQ_API_KEY=... && python main.py
```

```python
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DOCS = [
    Document(page_content="Retry budget is three attempts before dead-lettering."),
    Document(page_content="The worker retries failed messages three times before it stops."),
    Document(page_content="After the final retry, the payload moves to the dead-letter queue."),
    Document(page_content="Operators inspect the exception chain before replaying a job."),
    Document(page_content="HTTP 429 requires exponential backoff on the client side."),
    Document(page_content="The dead-letter queue preserves the original payload for debugging."),
]
QUERY = "Why did the worker stop retrying the message?"

def show_results(label: str, docs: list[Document]) -> None:
    print(f"\n=== {label} ===")
    for index, doc in enumerate(docs, start=1):
        print(f"{index}. {doc.page_content}")

def main() -> None:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    store = FAISS.from_documents(DOCS, embeddings)

    similarity = store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 2},
    )
    mmr_small = store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 2, "fetch_k": 4, "lambda_mult": 0.3},
    )
    mmr_wide = store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 2, "fetch_k": 6, "lambda_mult": 0.3},
    )

    show_results("similarity k=2", similarity.invoke(QUERY))
    show_results("mmr k=2 fetch_k=4", mmr_small.invoke(QUERY))
    show_results("mmr k=2 fetch_k=6", mmr_wide.invoke(QUERY))

if __name__ == "__main__":
    main()
```

### What to notice in this code

- The same vector store returns different evidence sets once `search_type` changes.
- Wider `fetch_k` gives MMR real room to diversify results.
- Lower `lambda_mult` increases the diversity penalty.

### Where engineers get confused

- Increasing only `k` does not automatically improve coverage.
- When `fetch_k == k`, MMR can collapse toward plain similarity search.
- Retriever-level thresholding is not the same as raw backend score filtering.

## Checklist

- [ ] I compared similarity and MMR on the same query.
- [ ] I tested `fetch_k` at a meaningfully larger width than `k`.
- [ ] I observed the redundancy-versus-coverage tradeoff through `lambda_mult`.
- [ ] I separated embedding quality issues from retriever policy issues.
<!-- a-grade-example:end -->

## Source Version

All code citations in this post are pinned to [`langchain-ai/langchain @ langchain==0.2.17`](https://github.com/langchain-ai/langchain/tree/langchain==0.2.17).

Episode 2 ended with vector geometry. Episode 3 is where that geometry becomes the ranked chunk list that the model will treat as evidence. That boundary matters because vector neighborhoods can be mathematically correct and still operationally misleading. A corpus full of near-duplicate clauses can produce a clean similarity ranking and a poor context set. The geometry stayed the same. The retrieval policy changed.

That policy lives in several places at once. `BaseRetriever` wraps retrieval in the Runnable lifecycle. `VectorStoreRetriever` chooses among `similarity`, `mmr`, and `similarity_score_threshold`. FAISS then distinguishes raw L2 distance from normalized relevance scores. This post follows that path from the retriever interface down to backend selection logic and then back up to a custom retriever pattern that narrows the search space before vector search begins.

---

## 1. What `BaseRetriever` actually standardizes

In LangChain 0.2.17, the foundational retriever interface is `langchain_core.retrievers.BaseRetriever`. At first glance it looks simple: take a string query, return a list of `Document` objects. In source, though, it is already part of the Runnable system. That design choice is the reason the recommended entry points are `invoke()` and `ainvoke()` rather than the older `get_relevant_documents()` methods.

![Invoke path into retriever callbacks](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/03/03-01-base-retriever-invoke-flow.en.png)

*Invoke path into retriever callbacks*

`invoke()` is worth reading line by line. It starts with `ensure_config(config)`, then builds a `CallbackManager` through `CallbackManager.configure(...)`. At that stage LangChain merges together several sources of execution metadata: callbacks from the run config, retriever-level tags and metadata, config-level tags and metadata, and the tracing payload from `_get_ls_params()`. After that, `callback_manager.on_retriever_start(...)` creates a `run_manager`. Only then does the retriever call the implementation hook that actually performs retrieval.

That implementation hook is `_get_relevant_documents()`. If the subclass supports the newer signature, `invoke()` passes in `run_manager`. Success triggers `run_manager.on_retriever_end(result)`, and failure triggers `run_manager.on_retriever_error(e)`. So retrieval is executed as a traced run, not as an unstructured helper call.

`run_manager` exists so custom retrievers can emit intermediate callback events or tracing text while they work. `BaseRetriever.__init_subclass__()` also uses signature inspection to detect support for `run_manager` and to patch older retrievers that implemented `get_relevant_documents()` directly. Those legacy retrievers still work in 0.2.17, but the intended implementation point is clearly `_get_relevant_documents()`.

The async side follows the same pattern. `ainvoke()` builds an `AsyncCallbackManager` and calls `_aget_relevant_documents()`. If a retriever has no native async implementation, the default `_aget_relevant_documents()` falls back to `run_in_executor(...)` around the synchronous implementation. That is why the async hook exists: it allows true async retrievers to stay native while keeping a uniform async interface for everything else.

The public methods `get_relevant_documents()` and `aget_relevant_documents()` are therefore compatibility shims. They have been deprecated since 0.1.46 and now delegate into `invoke()` / `ainvoke()`. In 0.2.x, deprecation means the execution center has moved to the Runnable model, not that retrieval itself is disappearing.

This minimal example shows the intended custom pattern.

```python
from typing import List

from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

class KeywordWindowRetriever(BaseRetriever):
    docs: List[Document]
    k: int = 2

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        matched = [doc for doc in self.docs if query.lower() in doc.page_content.lower()]
        run_manager.on_text(f"matched {len(matched)} documents before truncation")
        return matched[: self.k]

def main() -> None:
    retriever = KeywordWindowRetriever(
        docs=[
            Document(page_content="Payment worker retries failed jobs three times."),
            Document(page_content="HTTP 429 indicates per-minute quota exhaustion."),
            Document(page_content="Dead-letter messages keep the original payload."),
        ],
        k=2,
    )
    for doc in retriever.invoke("worker"):
        print(doc.page_content)

if __name__ == "__main__":
    main()
```

The baseline here is straightforward: `BaseRetriever` is not merely a semantic contract about inputs and outputs. It is a Runnable contract that standardizes lifecycle hooks, tracing metadata, and async compatibility.

---

## 2. How `VectorStoreRetriever` dispatches search types

`VectorStoreRetriever` is the default adapter that turns a vector store into a retriever. Its implementation is short, but the shortness is deceptive. The class stores two policy fields, `search_type` and `search_kwargs`, and its `_get_relevant_documents()` method dispatches to different vector-store methods based on those settings. Retrieval quality is therefore shaped at this adapter boundary before it reaches FAISS or any other backend.

![Search type dispatch and parameters](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/03/03-02-vectorstore-retriever-dispatch.en.png)

*Search type dispatch and parameters*

The allowed search types are explicitly enumerated:

- `similarity`
- `similarity_score_threshold`
- `mmr`

The `root_validator` named `validate_search_type()` enforces two rules. First, the `search_type` must be one of those three. Second, if the type is `similarity_score_threshold`, then `search_kwargs["score_threshold"]` must be present and must be a float. That second rule is more important than it first appears because threshold retrieval is not just regular similarity search with an extra if-statement. It goes through a different scoring path.

The dispatch logic itself is direct. For `similarity`, `_get_relevant_documents()` calls `self.vectorstore.similarity_search(query, **self.search_kwargs)`. For `similarity_score_threshold`, it calls `self.vectorstore.similarity_search_with_relevance_scores(query, **self.search_kwargs)` and strips away the scores, keeping only documents. For `mmr`, it calls `self.vectorstore.max_marginal_relevance_search(query, **self.search_kwargs)`. The async method `_aget_relevant_documents()` follows the same shape with `asimilarity_search`, `asimilarity_search_with_relevance_scores`, and `amax_marginal_relevance_search`.

`k` exists in all three modes, but its meaning shifts slightly. In plain similarity search it is the number of top documents returned by the backend. In threshold mode it is the maximum number returned after relevance-score conversion and filtering. In MMR mode it is the final output size after a larger candidate pool has been diversified.

`fetch_k` matters only for MMR and is passed straight through to the vector store. `score_threshold` matters only for threshold mode and is applied after relevance-score conversion, not on raw backend distances. That is why `VectorStoreRetriever` calls `similarity_search_with_relevance_scores()` rather than `similarity_search_with_score()`.

This small script makes the three modes visible.

```python
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def build_store() -> FAISS:
    docs = [
        Document(page_content="Workers retry failed jobs three times.", metadata={"source": "runbook"}),
        Document(page_content="Dead-letter queues preserve the original payload.", metadata={"source": "runbook"}),
        Document(page_content="HTTP 429 means the caller exceeded quota.", metadata={"source": "api"}),
    ]
    return FAISS.from_documents(docs, HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))

def main() -> None:
    store = build_store()

    similarity_retriever = store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 2},
    )
    threshold_retriever = store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 3, "score_threshold": 0.2},
    )
    mmr_retriever = store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 2, "fetch_k": 6, "lambda_mult": 0.3},
    )

    print("similarity")
    for doc in similarity_retriever.invoke("retry policy"):
        print(doc.page_content)

    print("threshold")
    for doc in threshold_retriever.invoke("retry policy"):
        print(doc.page_content)

    print("mmr")
    for doc in mmr_retriever.invoke("retry policy"):
        print(doc.page_content)

if __name__ == "__main__":
    main()
```

So `VectorStoreRetriever` is simple in code size but not trivial in effect. It is the first place where “retrieval” stops meaning one thing and becomes a choice among several ranking semantics.

---

## 3. MMR internals: where diversity actually enters the ranking

MMR exists to counter one of the most common retrieval failure modes: a top-k list that is locally accurate and globally repetitive. If a corpus contains many near-duplicate chunks, plain similarity search happily returns them because each chunk is individually close to the query. The user then gets redundancy instead of coverage. MMR addresses that by selecting documents that are both query-relevant and mutually less redundant.

![MMR candidate expansion and selection](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/03/03-03-mmr-selection-flow.en.png)

*MMR candidate expansion and selection*

The FAISS path is easy to trace in source. `max_marginal_relevance_search()` embeds the query and hands the vector to `max_marginal_relevance_search_by_vector()`. That method then delegates to `max_marginal_relevance_search_with_score_by_vector()`, which performs the actual backend search. The implementation first calls `self.index.search(...)` to fetch `fetch_k` candidates. If a metadata filter is present, FAISS doubles the raw fetch width to `fetch_k * 2` before filtering because some candidates may be discarded later. Then it reconstructs each candidate vector with `self.index.reconstruct(int(i))` and passes those vectors into `maximal_marginal_relevance(...)`.

The MMR core that FAISS actually calls lives in `langchain_community.vectorstores.utils.maximal_marginal_relevance()`. A near-identical copy also exists under `langchain_core.vectorstores.utils`, but in 0.2.17 the FAISS path imports and uses the community version. The function computes cosine similarity between the query and the candidate set, picks the single most query-similar candidate first, and then grows the result greedily. For every remaining candidate it computes:

`equation_score = lambda_mult * query_score - (1 - lambda_mult) * redundant_score`

Here `query_score` is the candidate's cosine similarity to the query, and `redundant_score` is the maximum cosine similarity between that candidate and any already selected candidate. So the LangChain variable `lambda_mult` weights query similarity, while `(1 - lambda_mult)` weights the redundancy penalty.

You will often see the same tradeoff written as `score = (1-λ)·similarity - λ·max_similarity_to_selected`. That is not a contradiction. It is only a change in what the symbol λ means. In LangChain's source, `lambda_mult` names the query-relevance weight. In other writeups, λ sometimes names the diversity weight instead. The operational meaning is the same: one term rewards closeness to the query, the other penalizes closeness to already selected results.

This is why `fetch_k >> k` matters. MMR cannot diversify what it never sees. If `k=4` and `fetch_k=4`, you are effectively locked into the same local neighborhood that plain similarity search already chose. With `fetch_k=20` or `40`, the selector finally has room to trade a little closeness for materially less redundancy.

That matters most in corpora with repeated templates or many chunks that share the same lead-in. In practice, `lambda_mult=0.5` is a reasonable starting point, values around `0.2` to `0.4` often work well when duplication is severe, and values above `0.7` behave much more like ordinary similarity search.

Here is a runnable sketch.

```python
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def main() -> None:
    docs = [
        Document(page_content="Retry budget is three attempts before dead-lettering."),
        Document(page_content="The worker retries failed messages three times."),
        Document(page_content="Dead-letter queues keep the original payload for debugging."),
        Document(page_content="HTTP 429 responses require exponential backoff."),
        Document(page_content="Operators inspect exception chains after the final retry."),
    ]

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    store = FAISS.from_documents(docs, embeddings)

    print("lambda_mult=0.8")
    for doc in store.max_marginal_relevance_search(
        "Why did the worker stop retrying?",
        k=3,
        fetch_k=10,
        lambda_mult=0.8,
    ):
        print(doc.page_content)

    print("lambda_mult=0.2")
    for doc in store.max_marginal_relevance_search(
        "Why did the worker stop retrying?",
        k=3,
        fetch_k=10,
        lambda_mult=0.2,
    ):
        print(doc.page_content)

if __name__ == "__main__":
    main()
```

MMR is therefore best understood as a second-stage selector over an expanded candidate pool, not as a smarter version of top-k similarity alone.

---

## 4. What `similarity_score_threshold` means with FAISS L2 distances

Threshold retrieval sounds simple until you ask what the threshold is actually applied to. In FAISS `IndexFlatL2`, the backend returns L2 distance values, not similarity scores. Lower is better. If you apply a “score threshold” directly to those raw numbers, you are really applying a distance ceiling. LangChain adds an intermediate relevance-score layer precisely to make threshold retrieval more backend-independent.

![Distance values becoming relevance scores](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/03/03-04-threshold-score-conversion.en.png)

*Distance values becoming relevance scores*

When `VectorStoreRetriever` uses `search_type="similarity_score_threshold"`, it calls `vectorstore.similarity_search_with_relevance_scores(...)`. That method does not expose the backend's raw score semantics directly. Instead it calls `_similarity_search_with_relevance_scores()`, which obtains raw `(doc, score)` pairs from `similarity_search_with_score()`, then transforms each raw score through `_select_relevance_score_fn()`. Only after that transformation does it apply `score_threshold`, keeping results whose normalized relevance score is greater than or equal to the threshold.

FAISS defines the fallback behavior explicitly. `_select_relevance_score_fn()` first respects any override supplied to the constructor. If none is set, it chooses a default from `distance_strategy`: max inner product, Euclidean distance, or cosine. So “no relevance score function set” does not mean “no conversion happens.” It means the vector store falls back to its built-in mapping.

For L2 distance, that default is `1.0 - distance / math.sqrt(2)`. The assumption behind it is normalized embeddings, where identical vectors are distance 0 and maximally different unit vectors are distance `sqrt(2)`. If that assumption is wrong for your embeddings, the converted scores can drift outside `[0, 1]`, and LangChain will warn accordingly.

One more distinction matters in practice. FAISS also accepts `score_threshold` in its raw `similarity_search_with_score_by_vector()` path, but there it compares against the backend score directly: `<=` for Euclidean distance and `>=` for max inner product. `VectorStoreRetriever` threshold mode compares after relevance-score conversion. Same parameter name, different layer.

This script shows both views.

```python
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def main() -> None:
    docs = [
        Document(page_content="Retry budget is three attempts.", metadata={"source": "ops"}),
        Document(page_content="HTTP 429 requires exponential backoff.", metadata={"source": "api"}),
        Document(page_content="Dead-letter queues preserve payloads.", metadata={"source": "ops"}),
    ]

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    store = FAISS.from_documents(docs, embeddings)

    print("raw scores")
    for doc, score in store.similarity_search_with_score("retry budget", k=3):
        print(round(score, 4), doc.page_content)

    print("relevance scores")
    for doc, score in store.similarity_search_with_relevance_scores("retry budget", k=3):
        print(round(score, 4), doc.page_content)

    retriever = store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 3, "score_threshold": 0.2},
    )
    print("threshold results")
    for doc in retriever.invoke("retry budget"):
        print(doc.page_content)

if __name__ == "__main__":
    main()
```

So the lesson is not just that L2 is a distance. It is that threshold retrieval in LangChain deliberately inserts a translation layer from raw backend distance into retriever-level relevance semantics.

---

## 5. When a custom retriever is the right abstraction

`VectorStoreRetriever` is a solid default, but it is not always the right boundary for retrieval policy. Sometimes the real requirement is to narrow the search space before vector search begins. A common example is source scoping. If the application already knows the user should only search documents from one source, tenant, or repository, then searching a global index and discarding cross-source results afterward is structurally wasteful.

![Source-filtered routing before vector search](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/03/03-05-custom-source-retriever.en.png)

*Source-filtered routing before vector search*

This is easy to miss because FAISS does support metadata filtering in LangChain. But if you read the implementation closely, filtering is not truly pre-search in the flat-index path. Similarity search first retrieves candidates from the index and then applies the metadata filter in Python. In MMR mode it may fetch even more candidates first, using `fetch_k * 2` when a filter is present, because some results may be discarded later. That means a strong metadata constraint can still force a broad vector search before most of the candidates are thrown away.

This is where a custom retriever becomes the cleaner abstraction. Instead of one global index plus post-filtering, you can maintain one vector store per source and let the retriever choose the correct sub-index up front. In that design, `doc.metadata["source"]` is not a late-stage filter. It is an early routing key.

That is not always the right trade. You give up some global recall in exchange for lower noise and lower search cost inside a known boundary. But when the boundary already belongs to the application contract, it is usually the right one.

Here is a concrete pattern.

```python
from collections import defaultdict
from typing import Dict, List

from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def build_source_indexes(
    documents: List[Document], embeddings: Embeddings
) -> Dict[str, FAISS]:
    grouped: Dict[str, List[Document]] = defaultdict(list)
    for doc in documents:
        grouped[doc.metadata["source"]].append(doc)
    return {
        source: FAISS.from_documents(source_docs, embeddings)
        for source, source_docs in grouped.items()
    }

class SourceScopedRetriever(BaseRetriever):
    stores_by_source: Dict[str, FAISS]
    source: str
    k: int = 4

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        store = self.stores_by_source.get(self.source)
        if store is None:
            run_manager.on_text(f"no index for source={self.source}")
            return []
        run_manager.on_text(f"searching source={self.source}")
        return store.similarity_search(query, k=self.k)

def main() -> None:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    documents = [
        Document(
            page_content="Workers retry failed jobs three times before dead-lettering.",
            metadata={"source": "runbook"},
        ),
        Document(
            page_content="Operators inspect the exception chain after the final retry.",
            metadata={"source": "runbook"},
        ),
        Document(
            page_content="HTTP 429 means the caller exceeded the public API quota.",
            metadata={"source": "api"},
        ),
        Document(
            page_content="Backoff is mandatory for retrying 429 responses.",
            metadata={"source": "api"},
        ),
    ]

    stores_by_source = build_source_indexes(documents, embeddings)
    retriever = SourceScopedRetriever(
        stores_by_source=stores_by_source,
        source="runbook",
        k=2,
    )

    for doc in retriever.invoke("Why did the worker stop retrying?"):
        print(doc.page_content)

if __name__ == "__main__":
    main()
```

The specific example uses source-based routing, but the same pattern works for tenant scoping, permission boundaries, document freshness tiers, or language-specific sub-indexes. The important idea is that a custom retriever is where you encode retrieval policy that should happen before generic vector ranking.

---

## The baseline to carry into episode 4

This episode established the retriever layer as a policy boundary rather than a passive wrapper. `BaseRetriever` standardizes lifecycle, tracing, and async fallback under the Runnable model. `VectorStoreRetriever` then chooses among plain similarity, thresholded relevance retrieval, and MMR-based diversification. MMR only helps if the candidate pool is widened first, which is why `fetch_k` must usually be much larger than `k`. Threshold mode depends on relevance-score conversion, with FAISS falling back to a distance-strategy-specific default when no explicit `relevance_score_fn` is supplied. And custom retrievers matter when the main optimization is not a different ranking formula but a different search boundary.

That baseline leads directly into episode 4. Retrieval output is still not final context. The next failure point is how those documents are packed and injected into the prompt.

## In this series

- [Document Loading and Chunking — Inside LangChain TextSplitter](./01-document-loading-and-chunking.md)
- [Embeddings and the Vector Index — Inside FAISS IndexFlatL2](./02-embeddings-and-vector-index.md)
- **Retriever Design — VectorStoreRetriever and MMR (current)**
- Prompt Construction and Context Injection — Inside PromptTemplate (upcoming)
- Assembling the RAG Chain — RetrievalQA vs LCEL (upcoming)
- Evaluation and Quality Gates — RAGAS Metrics and Faithfulness (upcoming)

---

## References

- [LangChain `BaseRetriever` source](https://github.com/langchain-ai/langchain/blob/langchain==0.2.17/libs/core/langchain_core/retrievers.py)
- [LangChain `VectorStore` and `VectorStoreRetriever` source](https://github.com/langchain-ai/langchain/blob/langchain==0.2.17/libs/core/langchain_core/vectorstores/base.py)
- [LangChain FAISS vector store source](https://github.com/langchain-ai/langchain/blob/langchain==0.2.17/libs/community/langchain_community/vectorstores/faiss.py)
- [LangChain community vector store utils with `maximal_marginal_relevance`](https://github.com/langchain-ai/langchain/blob/langchain==0.2.17/libs/community/langchain_community/vectorstores/utils.py)
- [LangChain core vector store utils copy](https://github.com/langchain-ai/langchain/blob/langchain==0.2.17/libs/core/langchain_core/vectorstores/utils.py)
- [LangChain community vector store utils with `DistanceStrategy`](https://github.com/langchain-ai/langchain/blob/langchain==0.2.17/libs/community/langchain_community/vectorstores/utils.py)
- [LangChain `VectorStore.as_retriever` API source](https://github.com/langchain-ai/langchain/blob/langchain==0.2.17/libs/core/langchain_core/vectorstores/base.py#L937-L1002)

Tags: RAG, LangChain, Vector Search, LLM

---

© 2026 YeongseonBooks. All rights reserved.
