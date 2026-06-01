---
title: "RAG Evaluation and Benchmarking 101 (5/6): End-to-end RAG pipeline evaluation"
series: rag-benchmark-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
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
seo_description: Evaluate the RAG pipeline with RAGAS. Measure Faithfulness and Answer Relevancy to detect hallucinations and ensure grounded answers.
---

# RAG Evaluation and Benchmarking 101 (5/6): End-to-end RAG pipeline evaluation

End-to-end evaluation only becomes useful when question, context, and answer are observed as one flow. Measure retrieval and generation on that shared path, and you can tell which layer is actually responsible for quality loss.

This is the 5th post in the RAG Evaluation and Benchmarking 101 series.

![Dataset structure for end-to-end evaluation](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/05/05-01-dataset-structure-for-end-to-end-evaluat.en.png)
*Dataset structure for end-to-end evaluation*
> End-to-end evaluation is not "does the answer look right?". It is a structured score for **whether the answer is grounded in the context and actually addresses the question**.

## Questions to Keep in Mind

- If retrieval metrics improve but final answers are poor, which layer should be inspected next?
- What debugging becomes easier when retrieval, generation, and grounding scores are reported together?
- Why is using LLM-as-judge or RAGAS scores risky without a baseline?

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

![Wrapper path into the RAGAS evaluator](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/05/05-02-wrapper-path-into-the-ragas-evaluator.en.png)

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
cd en/05-e2e-evaluation
export GROQ_API_KEY=...
python3 main.py
```

### Step 4 — Read the results

![Reading retrieval and generation failure separately](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/05/05-03-reading-retrieval-and-generation-failure.en.png)

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

![Verification flow before metric execution](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/05/05-04-verification-flow-before-metric-executio.en.png)

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

## Extending the end-to-end evaluation report for production use

The biggest failure in end-to-end evaluation is keeping only aggregate scores and discarding sample-level evidence. In production you must explain *why* a score dropped, so store three layers together:

1. Aggregate scores: faithfulness, answer relevancy, retrieval metrics
2. Per-sample scores: question-level detail
3. Evidence data: contexts, answer text, reference document IDs

### Merging RAGAS output with retrieval output

```python
def merge_eval_rows(retrieval_rows, ragas_df):
    merged = []
    for idx, r in enumerate(retrieval_rows):
        merged.append({
            "query_id": r["query_id"],
            "question": r["question"],
            "ranked_ids": r["ranked_ids"],
            "hit@5": r["hit@5"],
            "mrr": r["mrr"],
            "answer": r["answer"],
            "faithfulness": float(ragas_df.iloc[idx]["faithfulness"]),
            "answer_relevancy": float(ragas_df.iloc[idx]["answer_relevancy"]),
        })
    return merged
```

With this structure you can immediately filter for "retrieval hit but faithfulness miss" queries.

### Explicit decision rules

Scores without decision rules delay action. Define rules like these so that interpretation is instant.

| Condition | Verdict | Next action |
| --- | --- | --- |
| hit@5 low + faithfulness low | Retrieval-generation dual failure | Review index, embedding, and prompt together |
| hit@5 high + faithfulness low | Generation grounding failure | Force citation prompt, constrain answer format |
| hit@5 low + faithfulness high | Retrieval miss | Chunking, query expansion, reranker |
| answer relevancy low | Question interpretation failure | Fix system prompt and query normalization |

### Pinning evaluator prompt versions

LLM-as-judge changes score distributions when the evaluation prompt changes. Pin the prompt version in every report.

```yaml
evaluator:
  provider: groq
  model: llama-3.1-8b-instant
  temperature: 0
  prompt_version: ragas-faithfulness-v3
  max_workers: 1
```

Without a recorded prompt version, you cannot tell whether next month's score shift came from the model or from the evaluation criteria.

### Linking to LangSmith traces

To reproduce per-question failures quickly, connect each row to an execution trace.

```python
trace_row = {
    "query_id": query_id,
    "run_id": run_id,
    "langsmith_trace_url": trace_url,
    "faithfulness": faithfulness,
    "answer_relevancy": answer_relevancy,
}
```

When low-score rows link directly to traces, debugging time drops significantly.

### Sample RAGAS text output

```text
RAGAS aggregate:
  faithfulness: 0.872
  answer_relevancy: 0.846

Worst cases by faithfulness:
  q-014: 0.41 (question: "What happens if IVF nprobe is set to 1?")
  q-033: 0.45 (question: "Recommended chunk overlap value?")
```

This output is far more actionable than a single average. The team can open the two or three worst cases and start root-cause analysis immediately.

### Production evaluation run policy

| Run type | Sample size | Frequency | Purpose |
| --- | ---: | --- | --- |
| PR lightweight | 30-50 | Every PR | Fast regression detection |
| Nightly standard | 200-400 | Daily | Trend monitoring |
| Pre-release full | 500+ | Before release | Approval evidence |

Documenting this policy creates organizational agreement on "when to trust which score."

## Appendix — end-to-end evaluation thresholds and failure sample records

End-to-end evaluation is not about hitting a score target — it is about managing risky questions. Keep threshold policies and sample retention policies together.

### Threshold policy example

| Metric | Warn | Block | Note |
| --- | ---: | ---: | --- |
| faithfulness | < 0.86 | < 0.82 | Hallucination risk rises |
| answer relevancy | < 0.84 | < 0.80 | Off-topic answers increase |
| retrieval hit@5 | < 0.90 | < 0.86 | Evidence document misses increase |

Do not tighten the block threshold all at once. Observe baseline distributions for two or more weeks, then adjust incrementally.

### Failure sample storage format

```json
{
  "query_id": "q-108",
  "question": "What tradeoffs appear when nprobe is reduced?",
  "contexts": ["..."],
  "answer": "...",
  "scores": {
    "faithfulness": 0.41,
    "answer_relevancy": 0.79,
    "hit@5": 1.0
  },
  "diagnosis": "retrieval-ok-generation-hallucination"
}
```

Adding a `diagnosis` classification key lets you aggregate regression cases by type quickly.

### Evaluation run stability configuration

```python
from ragas.run_config import RunConfig

run_config = RunConfig(
    timeout=300,
    max_workers=1,
    max_retries=2,
    retry_wait=2,
)
```

Evaluation pipelines depend heavily on external APIs. Without explicit timeout/retry settings, flaky failures multiply.

### Summary table showing retrieval and generation quality together

| Bucket | Questions | avg hit@5 | avg faithfulness | avg answer relevancy |
| --- | ---: | ---: | ---: | ---: |
| Easy | 80 | 0.97 | 0.92 | 0.90 |
| Medium | 90 | 0.91 | 0.86 | 0.85 |
| Hard | 40 | 0.82 | 0.76 | 0.79 |

This table exposes quality gaps by difficulty, making improvement prioritization practical.

### Failure case labeling scheme

| Label | Meaning |
| --- | --- |
| retrieval-miss | Ground-truth document not retrieved |
| grounded-but-offtopic | Evidence present but answer irrelevant to question |
| hallucination-with-confidence | Confident answer with no supporting evidence |
| citation-format-error | Source document citation format broken |

Fixed labels let you track failure-rate changes in monthly quality reviews.

Maintain the labeling scheme with at least weekly spot checks. Automated labeling rules can accumulate bias over time. Keeping a human-verified label sample as a baseline stabilizes the interpretation quality of the evaluation pipeline.

When sharing evaluation reports, include improved cases alongside failures. If only failures accumulate, teams find causes but never reuse success patterns. Recording successes helps propagate effective prompt and retrieval configurations faster.

### Batch RAGAS evaluation code extension

In practice, outputting only averages makes debugging difficult. Store per-sample scores alongside input data so that regression analysis is possible.

```python
import pandas as pd

result = evaluate(
    dataset=dataset,
    metrics=[Faithfulness(), AnswerRelevancy(strictness=1)],
    llm=ragas_llm,
    embeddings=ragas_emb,
    run_config=RunConfig(timeout=300, max_workers=1),
)

score_df = result.to_pandas()
full_df = pd.concat([dataset.to_pandas(), score_df], axis=1)
full_df.to_csv("ragas_report.csv", index=False)

print(full_df[["question", "faithfulness", "answer_relevancy"]].head(10))
```

Attach this file as a PR artifact. When scores drop, you can trace exactly which questions collapsed.

### End-to-end test script example

Deployment pipelines need a single script that runs retrieval + generation + evaluation and exits non-zero on failure.

```python
# !/usr/bin/env python3
import json
import sys

from my_rag_eval import run_rag_eval  # returns dict with aggregate scores

THRESHOLDS = {
    "faithfulness": 0.85,
    "answer_relevancy": 0.82,
}

def main() -> int:
    report = run_rag_eval(sample_size=50)
    print(json.dumps(report, ensure_ascii=False, indent=2))

    for metric, minimum in THRESHOLDS.items():
        score = report["aggregate"][metric]
        if score < minimum:
            print(f"FAIL: {metric}={score:.3f} < {minimum:.3f}")
            return 1

    print("PASS: e2e RAG evaluation thresholds satisfied")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

Running this nightly in CI catches the impact of index or prompt changes on actual answer quality early.

### Evaluation cost and stability management

RAGAS is useful but costs money, so separate run policies by context. Use 30-50 samples per PR for fast regression checks; run 300+ samples nightly for stable trend observation. Periodically re-evaluate the same fixed dataset to monitor evaluator model drift — this helps separate app-quality changes from judge-quality changes.

## Answering the Opening Questions

- **If retrieval metrics improve but final answers are poor, which layer should be inspected next?**
  Inspect prompt construction, context injection, generation settings, and grounding if retrieval improved but answers remain poor.

- **What debugging becomes easier when retrieval, generation, and grounding scores are reported together?**
  A combined report separates cases like retrieval failure, answer failure despite good evidence, and good answer with missing citation.

- **Why is using LLM-as-judge or RAGAS scores risky without a baseline?**
  Without a baseline and sampled human review, judge-score movement can reflect evaluator bias or prompt drift rather than real improvement.

<!-- toc:begin -->
## In this series

- [RAG Evaluation and Benchmarking 101 (1/6): Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- [RAG Evaluation and Benchmarking 101 (2/6): Measuring retrieval performance](./02-retrieval-benchmarking.md)
- [RAG Evaluation and Benchmarking 101 (3/6): Comparing embedding models](./03-embedding-comparison.md)
- [RAG Evaluation and Benchmarking 101 (4/6): VectorDB selection criteria](./04-vectordb-selection.md)
- **RAG Evaluation and Benchmarking 101 (5/6): End-to-end RAG pipeline evaluation (current)**
- RAG Evaluation and Benchmarking 101 (6/6): Completing the RAG benchmark (upcoming)

<!-- toc:end -->

---

## References

- [RAGAS documentation](https://docs.ragas.io/)
- [RAGAS GitHub repository](https://github.com/explodinggradients/ragas)
- [Groq Python integration in LangChain](https://python.langchain.com/docs/integrations/chat/groq/)
- [HuggingFace Datasets](https://huggingface.co/docs/datasets)

Tags: RAG, VectorDB, Benchmarking, LLM
