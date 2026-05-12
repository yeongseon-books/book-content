---
title: End-to-end RAG pipeline evaluation
series: rag-benchmark-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- RAGAS
- Faithfulness
- AnswerRelevancy
- LLM
- Evaluation
last_reviewed: '2026-05-01'
seo_description: 'The data flow of an end-to-end evaluation:'
---

# End-to-end RAG pipeline evaluation

End-to-end evaluation only becomes useful when question, context, and answer are observed as one flow. Measure retrieval and generation on that shared path, and you can tell which layer is actually responsible for quality loss.

This is the 5th article in the RAG Evaluation and Benchmarking 101 series.

## Questions this post answers

![Questions this post answers](../../../assets/rag-benchmark-101/05/05-01-questions-this-post-answers.en.png)

*Questions this post answers*

- How do you actually compute `Faithfulness` and `AnswerRelevancy` with ragas 0.1.22?
- How do you wire a LangChain LLM and embedding model into the RAGAS evaluator?
- What dataset shape do you need when measuring **answer quality**, not retrieval?
- How do you separate retrieval failures from generation failures?

> End-to-end evaluation is not "does the answer look right?". It is a structured score for **whether the answer is grounded in the context and actually addresses the question**.

## Why this matters

Everything we measured in Episodes 2–4 was the quality of retrieval. What the user sees is the LLM's final answer. Perfect retrieval still hallucinates if the LLM ignores the context. A great LLM still produces bad answers when retrieval grabbed the wrong documents.

So a RAG system in production has to measure both layers.

- **Retrieval metrics**: hit rate, MRR, recall — "did we get the right documents?"
- **Generation metrics**: faithfulness, answer relevancy — "is the answer grounded in those documents and does it address the question?"

This post builds the second axis. The main tool is [RAGAS](https://docs.ragas.io/), which uses an LLM as a judge to score answer faithfulness and relevancy.

## Mental model

The data flow of an end-to-end evaluation:

```text
question  ──►  retriever  ──►  contexts (List[str])
                                    │
question + contexts  ──►  LLM  ──►  answer
                                    │
question + contexts + answer  ──►  RAGAS metrics
                                    │
                                    ▼
                          {faithfulness, answer_relevancy}
```

A row in the evaluation dataset is a `(question, contexts, answer)` tuple. With ground truth you can add metrics like `context_precision` and `context_recall`.

RAGAS internally calls an LLM again to compute scores, so evaluation itself costs LLM tokens and latency.

## Core concepts

| Metric | What it measures | Needs ground truth? |
| --- | --- | --- |
| Faithfulness | Are all claims in the answer derivable from the context? | No |
| Answer Relevancy | Does the answer directly address the question? | No |
| Context Precision | What fraction of retrieved documents was actually used? | Yes |
| Context Recall | Does the context contain everything needed for the gold answer? | Yes |

Faithfulness and Answer Relevancy work without ground truth, which makes them the right starting point when your gold set is small or non-existent.

## Before vs. after

**Before**: PR review approves with "the answer looks plausible". Hallucinations only surface when a user reports "the system gave me a confident wrong answer" in production.

**After**: Every PR runs RAGAS automatically against 50 questions and reports faithfulness / answer_relevancy.

```text
metric              before  after
faithfulness        0.78    0.91
answer_relevancy    0.82    0.85
```

Faithfulness rising from 0.78 to 0.91 is direct evidence that hallucinations dropped.

## Step-by-step walkthrough

### Step 1 — Build the evaluation dataset

![Dataset structure for end-to-end evaluation](../../../assets/rag-benchmark-101/05/05-01-dataset-structure-for-end-to-end-evaluat.en.png)

*Dataset structure for end-to-end evaluation*

```python
from datasets import Dataset

samples = []
for question in QUESTIONS:
    docs = retriever.invoke(question)
    contexts = [doc.page_content for doc in docs]
    answer = llm.invoke(build_prompt(question, contexts)).content
    samples.append({
        "question": question,
        "contexts": contexts,   # List[str], not a single string
        "answer": answer,
    })

dataset = Dataset.from_list(samples)
```

`contexts` MUST be a list of strings. A single string raises a KeyError inside RAGAS.

### Step 2 — Wire LLM and embeddings via wrappers

![Wrapper path into the RAGAS evaluator](../../../assets/rag-benchmark-101/05/05-02-wrapper-path-into-the-ragas-evaluator.en.png)

*Wrapper path into the RAGAS evaluator*

```python
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

ragas_llm = LangchainLLMWrapper(llm)
ragas_emb = LangchainEmbeddingsWrapper(embedding)
```

### Step 3 — Run the evaluation

```python
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy
from ragas.run_config import RunConfig

result = evaluate(
    dataset=dataset,
    metrics=[Faithfulness(), AnswerRelevancy(strictness=1)],
    llm=ragas_llm,
    embeddings=ragas_emb,
    run_config=RunConfig(timeout=300, max_workers=1),
)
print(result)
```

The runnable code lives in `rag-benchmark-101/en/05-e2e-evaluation/main.py`. `GROQ_API_KEY` is required.

```bash
cd /root/Github/rag-benchmark-101/en/05-e2e-evaluation
export GROQ_API_KEY=...
python3 main.py
```

### Step 4 — Read the results

![Reading retrieval and generation failure separately](../../../assets/rag-benchmark-101/05/05-03-reading-retrieval-and-generation-failure.en.png)

*Reading retrieval and generation failure separately*

| Faithfulness | Answer Relevancy | Diagnosis |
| --- | --- | --- |
| Low | Low | Retrieval pulled irrelevant docs, or the LLM ignored context |
| Low | High | Plausible but hallucinated — most dangerous |
| High | Low | Faithful to context but misses the question — suspect the prompt |
| High | High | Healthy |

The "Low / High" cell is the system confidently giving wrong answers. Make it the highest priority to fix.

## Common mistakes

- **Passing `contexts` as a single string** — must be `List[str]`. The most common KeyError cause.
- **Setting `max_workers` too high** — Groq, OpenAI, etc. have rate limits. Start at 1 and grow.
- **`temperature > 0`** — the evaluator LLM must be deterministic. Force `temperature=0`.
- **Not separating retrieval from generation scores** — when RAGAS scores drop, you cannot tell whether retrieval or generation broke. Always look at hit rate and MRR alongside.
- **Ignoring version differences** — RAGAS 0.1.x and 0.2.x diverge in import paths and metric construction. This post is on 0.1.22.

## In production

![Verification flow before metric execution](../../../assets/rag-benchmark-101/05/05-04-verification-flow-before-metric-executio.en.png)

*Verification flow before metric execution*

- **Eval dataset size**: start at 30–50 questions. Stabilize, then grow to 200–500. Beyond ~1,000 cost and time become painful.
- **Sampling**: stratified 50 on every PR, full set in a nightly job.
- **Choice of evaluator LLM**: pick a **different** model for evaluation than for generation to reduce self-bias (e.g. generate with Llama-3.1, judge with GPT-4o-mini).
- **Result storage**: never store only the score. Persist `(question, answer, contexts, score, reasoning)`. That is the starting point for any regression debug.
- **CI gate**: block PRs when faithfulness drops below threshold. Start answer_relevancy as a warning only.

## Checklist

- [ ] Used the class-based ragas 0.1.22 API (`Faithfulness()`, `AnswerRelevancy()`).
- [ ] Wrapped LLM and embeddings in `LangchainLLMWrapper` / `LangchainEmbeddingsWrapper`.
- [ ] Built a `Dataset` with `question`, `contexts` (List[str]), and `answer` columns.
- [ ] `temperature=0` and conservative `max_workers`.
- [ ] Reported retrieval metrics (hit rate, MRR) alongside generation metrics.

## Exercises

1. Add ground truth and extend the run to compute `ContextPrecision` and `ContextRecall`. What new signal appears?
2. Force the retriever to return a wrong document for the same question. Which metric drops first — faithfulness or answer_relevancy?
3. Run the evaluation twice — once with the same model for generation and judging, once with different models — and compare the scores.

## Wrap-up · what's next

This post built an end-to-end evaluation loop with RAGAS, scoring faithfulness and answer relevancy to surface hallucinations and off-topic answers. Key ideas: **match the dataset shape**, **wire LLM/embedding via wrappers**, and **read retrieval and generation scores together**.

Episode 6 — the final episode — combines every measurement tool from Episodes 1–5 into a single benchmark report.

<!-- toc:begin -->
## In this series

- [Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- [Measuring retrieval performance](./02-retrieval-benchmarking.md)
- [Comparing embedding models](./03-embedding-comparison.md)
- [VectorDB selection criteria](./04-vectordb-selection.md)
- **End-to-end RAG pipeline evaluation (current)**
- Completing the RAG Benchmark (upcoming)

<!-- toc:end -->

---

## References

- [RAGAS documentation](https://docs.ragas.io/)
- [RAGAS GitHub repository](https://github.com/explodinggradients/ragas)
- [Groq Python integration in LangChain](https://python.langchain.com/docs/integrations/chat/groq/)
- [HuggingFace Datasets](https://huggingface.co/docs/datasets)

Tags: RAG, VectorDB, Benchmarking, LLM
