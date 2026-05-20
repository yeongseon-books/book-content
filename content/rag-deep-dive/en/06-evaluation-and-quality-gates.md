---
title: "RAG Deep Dive (6/6): Evaluation and Quality Gates — RAGAS Metrics and Faithfulness"
series: rag-deep-dive
episode: 6
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- LangChain
- Vector Search
- LLM
last_reviewed: '2026-05-15'
seo_description: How RAGAS faithfulness and answer_relevancy metrics automate quality evaluation of RAG answers.
---

# RAG Deep Dive (6/6): Evaluation and Quality Gates — RAGAS Metrics and Faithfulness

RAGAS faithfulness and answer_relevancy metrics let you evaluate RAG answer quality without rereading every output by hand. This post shows how to turn those signals into a quality gate.

This is the final post in the RAG Deep Dive series.

## Questions to Keep in Mind

- Why do RAGAS dataset columns define what can actually be evaluated?
- What does Faithfulness compare against evidence instead of judging whether the answer sounds plausible?
- Which failures should a quality gate block in CI or production?

## Big Picture

![Sample fields controlling metric eligibility](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/06/06-01-ragas-dataset-schema-and-sample-fields.en.png)

*Sample fields controlling metric eligibility*

This picture shows question, answer, context, and ground-truth columns feeding RAGAS metrics that produce different quality signals. A RAG quality gate starts with reproducible columns and failure thresholds, not subjective impressions.

> Evaluation re-expands one RAG answer into the relationship between question, evidence, answer, and target truth, then turns that relationship into scores.

<!-- a-grade-example:begin -->
## Minimal runnable example

Example file: `en/06-evaluation-and-quality-gates/main.py`

```bash
export GROQ_API_KEY=... && python main.py
```

```python
import os

from datasets import Dataset
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from ragas import evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import answer_relevancy, faithfulness

def main() -> None:
    if not os.environ.get("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY is required")

    dataset = Dataset.from_dict(
        {
            "question": ["After how many retries is the message dead-lettered?"],
            "contexts": [[
                "The worker retries a failed message up to three times before giving up.",
                "After the final retry, the payload is moved to the dead-letter queue.",
            ]],
            "answer": [
                "The system retries the message three times. After the final retry, it moves the payload to the dead-letter queue."
            ],
            "ground_truth": [
                "The message is retried up to three times before it is dead-lettered."
            ],
        }
    )

    llm = LangchainLLMWrapper(
        ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=256)
    )
    embeddings = LangchainEmbeddingsWrapper(
        HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    )

    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=llm,
        embeddings=embeddings,
        raise_exceptions=True,
    )

    print(result)
    print(result.to_pandas().to_string(index=False))

if __name__ == "__main__":
    main()
```

### What to notice in this code

- The evaluation row preserves question, contexts, answer, and ground truth together.
- RAGAS uses an LLM for faithfulness and embeddings for answer relevancy.
- The result object exposes both summary scores and tabular sample output.

### Where engineers get confused

- High faithfulness does not guarantee high answer relevancy.
- Answer relevancy measures focus under the original question, not factual truth.
- Without a stable dataset schema, score comparisons stop being reproducible.

## Checklist

- [ ] I preserved question, evidence, answer, and target truth in the dataset.
- [ ] I interpret faithfulness and answer relevancy as different failure axes.
- [ ] I keep the sample set and model versions fixed before comparing scores.
- [ ] I plan to store thresholds and raw outputs together for CI gates.
<!-- a-grade-example:end -->

## Source Version

All RAGAS code citations in this post refer to the installable [`ragas==0.1.22`](https://pypi.org/project/ragas/0.1.22/) package, and all LangChain citations are pinned to [`langchain-ai/langchain @ langchain==0.2.17`](https://github.com/langchain-ai/langchain/tree/langchain==0.2.17). Accordingly, the metric source files discussed here are `ragas/metrics/_faithfulness.py`, `ragas/metrics/_answer_relevance.py`, and `ragas/metrics/_context_precision.py`.

A RAG pipeline that answers questions is not the same thing as a RAG pipeline that answers them correctly. In a demo, “retrieval seems fine” can be enough. In production, it is not. If you change chunk size, retriever `k`, or ranking policy, did grounding improve or did the system merely get longer and noisier? Evaluation is what turns tuning into reproducible improvement.

This final episode follows that evaluation layer from the source. We will start with the `datasets.Dataset` input shape, then trace faithfulness, answer relevancy, and context precision, and finally turn those metrics into a CI quality gate.

---

## 1. RAGAS overview and `datasets.Dataset`: the input columns define what can be measured

The first important thing to understand about RAGAS is that it is not a generic “grade this answer” box. Each metric requires a specific set of fields, and without those fields the metric cannot even run. That is why the real starting point is not the evaluator function but the dataset schema. In `ragas==0.1.22`, `evaluate()` takes a Hugging Face `datasets.Dataset`, and the default columns are `question`, `contexts`, `answer`, and `ground_truth`.

Those four columns form the core frame for RAG evaluation. `question` is the user query. `contexts` is the ordered list of retrieved chunks. `answer` is the model output. `ground_truth` is the human reference answer. If you do not keep the original question, you cannot compute answer relevancy. If you do not keep retrieved context, you cannot check faithfulness. If you do not keep a reference answer, you lose metrics that need a target outcome.

The schema is also your failure taxonomy. An answer can drift away from the question, inject unsupported claims, or retrieve useful evidence too late in the ranking. The row shape decides which of those failures you can measure.

It also explains why metrics have different contracts. Faithfulness needs `question`, `answer`, and `contexts`. Answer relevancy also requires all three because `evaluation_mode = qac`. Its `_create_question_gen_prompt()` method reads both `row["answer"]` and `row["contexts"]`, so if `contexts` is missing, `evaluate()` validation fails before scoring starts. Context precision needs `question`, `contexts`, and an answer target from `ground_truth`.

It is worth building rows explicitly rather than trying to reconstruct them later from partial logs. Once a production system stores `question`, `contexts`, `answer`, and `ground_truth` together, you can compare chunking or retrieval changes on the same sample set over time. If your internal column names differ, `evaluate(..., column_map={...})` can remap them by pointing each canonical RAGAS name to the existing dataset column.

```python
from datasets import Dataset

dataset = Dataset.from_dict(
    {
        "question": ["After how many retries is the job moved to the dead-letter queue?"],
        "contexts": [[
            "The worker retries the job up to three times before giving up.",
            "After the final retry, the payload is moved to the dead-letter queue.",
        ]],
        "answer": ["The job is retried three times before it is moved to the dead-letter queue."],
        "ground_truth": ["The job is retried up to three times before it is dead-lettered."],
    }
)

print(dataset)
print(dataset.features)

legacy_dataset = Dataset.from_dict(
    {
        "query": ["After how many retries is the job moved to the dead-letter queue?"],
        "retrieved_passages": [[
            "The worker retries the job up to three times before giving up.",
            "After the final retry, the payload is moved to the dead-letter queue.",
        ]],
        "prediction": ["The job is retried three times before it is moved to the dead-letter queue."],
        "reference_answer": ["The job is retried up to three times before it is dead-lettered."],
    }
)

column_map = {
    "question": "query",
    "contexts": "retrieved_passages",
    "answer": "prediction",
    "ground_truth": "reference_answer",
}

print(column_map)
```

That may look simple, but it captures the core idea: a useful RAG evaluation set is not a bag of outputs. It is a set of relations between intent, evidence, answer, and target truth.

---

## 2. Faithfulness internals: decompose the answer, then verify every claim

If you only watch one RAG-specific metric, faithfulness is often the best first choice. The most common production failure in RAG is not “the model wrote bad prose.” It is “the model said something that was not supported by the retrieved evidence.” `ragas/metrics/_faithfulness.py` makes that failure mode explicit by reducing it to two source-visible steps.

First, RAGAS does not judge the answer as one indivisible block. It uses an LLM to break the answer into simpler, atomic statements. The `LONG_FORM_ANSWER_PROMPT` instructs the model to analyze answer sentences, remove pronouns, and rewrite them as fully understandable simpler statements. A compound sentence like “The worker retries the job three times and then sends it to the dead-letter queue” can become two atomic claims: one about retry count and one about the dead-letter transition.

Second, each atomic claim is checked against the retrieved context list. The `NLI_STATEMENTS_MESSAGE` prompt asks whether every statement can be directly inferred from the provided context, returning a binary `verdict` for each one. In `_create_nli_prompt()`, the metric joins `contexts` into one context string and passes the claim list in JSON form. Then `_compute_score()` reduces the result to a ratio.

![Claim decomposition and support verification flow](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/06/06-02-faithfulness-claim-decomposition-and-verification.en.png)

*Claim decomposition and support verification flow*

Conceptually, the formula is:

\[
faithfulness\_score = \frac{|supported\_claims|}{|total\_claims|}
\]

That is exactly what the source does with `faithful_statements / num_statements`. If no statements are generated, the implementation returns `NaN`, because there is nothing meaningful to score.

The important part is what this metric means operationally. Faithfulness is not checking style, completeness, or even general world truth. It is checking whether the answer stays inside the evidence boundary defined by `contexts`. That makes its definition of hallucination narrower and more useful for RAG. A claim can be true in the real world and still count against faithfulness if it is not supported by the retrieved chunks for this invocation.

Suppose retrieval returned only the retry count and dead-letter rule, but the model adds “the default retry backoff is 30 seconds.” That may be true somewhere else in your docs. If it is not in the retrieved context for this run, faithfulness marks it unsupported. That is the right contract for RAG.

This is why faithfulness is such a strong regression signal. When it drops, the problem is often upstream: chunking split evidence badly, retrieval missed it, or prompting weakened the evidence boundary.

The core scoring idea is small enough to show in plain Python:

```python
from dataclasses import dataclass

@dataclass
class ClaimVerdict:
    statement: str
    verdict: int

def faithfulness_score(verdicts: list[ClaimVerdict]) -> float:
    if not verdicts:
        raise ValueError("At least one claim verdict is required")
    supported_claims = sum(1 for item in verdicts if item.verdict == 1)
    return supported_claims / len(verdicts)

verdicts = [
    ClaimVerdict("The worker retries the job three times.", 1),
    ClaimVerdict("The payload is moved to the dead-letter queue after the final retry.", 1),
    ClaimVerdict("The default retry backoff is 30 seconds.", 0),
]

print(faithfulness_score(verdicts))
```

The real RAGAS implementation uses an LLM both to produce the atomic claims and to verify them, but the score itself is just the supported-claims fraction. That simplicity is part of what makes it operationally useful.

---

## 3. Answer relevancy: reverse-question generation measures focus, not truth

Where faithfulness asks whether an answer stayed inside the evidence boundary, answer relevancy asks a different question: does this answer stay tightly aligned with the original user intent? `ragas/metrics/_answer_relevance.py` answers that by turning the answer around and asking what question the answer appears to be answering.

The implementation uses a reverse-question generation prompt. `QUESTION_GEN` takes the `answer` together with `context`, then asks the LLM to produce a question plus a `noncommittal` flag. The default `strictness` is 3, so the metric usually generates multiple reverse questions for the same answer. `_calculate_score()` then embeds the original `question` and the generated reverse questions, computes cosine similarity, and averages the result.

![Reverse questions measuring answer focus](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/06/06-03-answer-relevancy-reverse-question-flow.en.png)

*Reverse questions measuring answer focus*

That means answer relevancy is not a factuality metric. It does not verify whether the answer is correct. It verifies whether the answer is focused enough that, when read backward, it still points to the same question. Answers that wander into unnecessary detail, boilerplate, or adjacent explanations tend to produce reverse questions that drift away from the user’s actual request.

The `noncommittal` flag makes this even clearer. In `ragas==0.1.22`, a sample whose generated reverse-question set is classified as noncommittal contributes 0 for that sample. After `evaluate()` finishes, the metric is summarized as the mean across evaluated samples. So an evasive answer like “I’m not sure” or “there is not enough information” contributes a zero-valued sample to that mean.

Answer relevancy should therefore be interpreted carefully. A verbose answer can still be highly faithful if every sentence is grounded in retrieved evidence, yet score worse on answer relevancy because it is not tightly focused on the question. Conversely, a short direct answer may score well on answer relevancy while still failing faithfulness if it states an unsupported fact.

In practice, answer relevancy is especially useful for spotting prompt drift. If a template starts adding too much background or boilerplate, this score often drops before users can explain why the answer feels off.

The similarity step is straightforward enough to express outside the library:

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

original_question = np.array([0.9, 0.1, 0.0, 0.2])
generated_question_1 = np.array([0.85, 0.12, 0.02, 0.18])
generated_question_2 = np.array([0.88, 0.05, 0.01, 0.24])

scores = [
    cosine_similarity(original_question, generated_question_1),
    cosine_similarity(original_question, generated_question_2),
]

print(sum(scores) / len(scores))
```

The point is what the metric is actually asking: answer focus under the original user intent, not correctness.

---

## 4. Context precision: earlier useful chunks are worth more

Context precision is the metric that looks most directly at retrieval ranking quality. In `ragas/metrics/_context_precision.py`, the system evaluates each retrieved chunk one by one and asks whether that chunk was useful for arriving at the target answer. Then it applies an average-precision style calculation over the ranked list. So this is not just “did retrieval include something useful?” It is “how early did retrieval surface useful evidence?”

The input contract matters here too. `ragas==0.1.22` expects a `Dataset` with `question`, `contexts`, `answer`, and `ground_truth`, and `evaluate()` first normalizes aliases through `remap_column_names(dataset, column_map)`. After that normalization, context precision evaluates each context chunk against the question and the answer target carried by the dataset, which is why it is better understood as a retrieval metric than a generation metric.

![Rank-weighted precision at k scoring](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/06/06-04-context-precision-at-k-ranking.en.png)

*Rank-weighted precision at k scoring*

The scoring logic lives in `_calculate_average_precision()`. Let `rel(i)` be 1 if the chunk at rank `i` is useful and 0 otherwise. Let `P(i)` be precision up to position `i`. Then the score is:

\[
AP@k = \frac{\sum_{i=1}^{k} P(i) \cdot rel(i)}{\sum_{i=1}^{k} rel(i)}
\]

This formula rewards relevant chunks appearing early. If the same two useful chunks appear at ranks 1 and 2, the score is much higher than if they appear at ranks 4 and 5. That is why ordering matters. Context precision is sensitive not just to inclusion, but to ranked usefulness.

This ties directly back to Episode 3. Increasing retriever `k` can improve recall, but it does not guarantee better context precision. If extra chunks add noise near the top, average precision can fall. MMR may reduce redundancy, but if it pushes the best evidence from rank 1 to rank 3, the ranking became less useful.

Here is the same average-precision calculation in compact Python:

```python
def average_precision(verdicts: list[int]) -> float:
    relevant = sum(verdicts)
    if relevant == 0:
        raise ValueError("At least one relevant context is required")

    numerator = 0.0
    for index, verdict in enumerate(verdicts, start=1):
        if verdict == 1:
            precision_at_i = sum(verdicts[:index]) / index
            numerator += precision_at_i

    return numerator / relevant

ranking = [1, 0, 1, 0]
print(average_precision(ranking))
```

Once you look at retrieval through this lens, “just increase k” stops sounding like a universal fix.

---

## 5. Building a quality gate in CI: fail fast when faithfulness regresses

Computing metrics is only half the job. The real value appears when those metrics block regressions. The practical pattern is simple: keep a representative evaluation set, run `ragas.evaluate()` in CI, and fail the pipeline when a grounding metric falls below a threshold.

One versioning detail matters. In `ragas==0.1.22`, the executable dataset uses `question`, `contexts`, `answer`, and `ground_truth`. If your stored dataset uses names like `query`, `retrieved_passages`, `prediction`, or `reference_answer`, pass a `column_map` in the direction canonical name -> existing dataset column. For example, `{"question": "query"}` means the RAGAS `question` slot should read from the dataset column named `query`.

![CI gate around faithfulness thresholds](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/06/06-05-quality-gate-pipeline-integration.en.png)

*CI gate around faithfulness thresholds*

This script shows a small but realistic quality gate. It runs faithfulness, answer relevancy, and context precision over a fixed dataset, computes mean scores, and fails immediately when average faithfulness falls below 0.8.

The example uses `ChatGroq` with `llama-3.1-8b-instant` as the judge LLM. Groq offers a free API tier, so the code runs without a paid account. The tradeoff is judge quality: smaller open-source models are less consistent than GPT-4o-mini or Claude on borderline cases, so scores can fluctuate more between runs. For a personal project or early-stage pipeline, Groq is a practical starting point. For production CI gates where score stability matters, swap in `ChatOpenAI(model="gpt-4o-mini")` as the judge. The rest of the code is identical.

```python
import numpy as np
from datasets import Dataset
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from ragas import evaluate
from ragas.metrics import answer_relevancy, context_precision, faithfulness
from ragas.llms import LangchainLLMWrapper

def build_eval_dataset() -> Dataset:
    rows = {
        "question": [
            "After how many retries is the job moved to the dead-letter queue?",
            "Why should fetch_k be larger than k in MMR retrieval?",
        ],
        "answer": [
            "The job is retried up to three times before it is moved to the dead-letter queue.",
            "MMR needs a wider candidate pool before picking the final k results, so fetch_k must be larger than k to give reranking room to improve diversity.",
        ],
        "contexts": [
            [
                "The worker retries the job up to three times before giving up.",
                "After the final retry, the payload is moved to the dead-letter queue.",
            ],
            [
                "MMR first gathers a larger candidate pool before selecting the final k documents.",
                "If fetch_k equals k, the reranking stage has almost no room to improve diversity.",
            ],
        ],
        "ground_truth": [
            "The job is retried up to three times before it is dead-lettered.",
            "fetch_k should be larger than k because MMR needs a wider candidate set before selecting the final ranking.",
        ],
    }
    return Dataset.from_dict(rows)

def run_quality_gate() -> dict[str, float]:
    dataset = build_eval_dataset()
    judge_llm = LangchainLLMWrapper(ChatGroq(model="llama-3.1-8b-instant", temperature=0))

    metrics = [faithfulness, answer_relevancy, context_precision]
    for m in metrics:
        m.llm = judge_llm

    result = evaluate(dataset=dataset, metrics=metrics)

    summary = {
        "faithfulness": float(np.nanmean(result["faithfulness"])),
        "answer_relevancy": float(np.nanmean(result["answer_relevancy"])),
        "context_precision": float(np.nanmean(result["context_precision"])),
    }

    if summary["faithfulness"] < 0.8:
        raise SystemExit(
            f"Fail: faithfulness {summary['faithfulness']:.3f} is below 0.800"
        )

    print(summary)
    return summary

if __name__ == "__main__":
    run_quality_gate()
```

If you prefer pytest integration, the test can be almost trivial:

```python
from quality_gate import run_quality_gate

def test_rag_quality_gate() -> None:
    summary = run_quality_gate()
    assert summary["faithfulness"] >= 0.8
    assert summary["context_precision"] >= 0.7
```

Why make faithfulness the first hard gate? Because chunking, retrieval, prompting, and chain assembly all feed into whether the final answer stays inside its evidence boundary.

LangChain’s evaluation layer is helpful here as a complement, not a replacement. `EvaluatorType` and `load_evaluator()` are useful for final-answer grading, criteria checks, or exact-match style comparisons. They do not natively compute retrieval-grounded faithfulness. That is the gap RAGAS fills.

That gives the series a clean ending. Episodes 1 through 5 explained how chunks are created, retrieved, injected, and assembled. Episode 6 adds the final layer: a repeatable way to prove that a change made the system better rather than merely different. A production-ready RAG stack is complete only when it can fail a build before it fails a user.

---

## Answering the Opening Questions

- **Why do RAGAS dataset columns define what can actually be evaluated?**
  A metric can only run when required columns such as question, answer, contexts, or ground truth exist, so the schema defines the measurable quality surface.

- **What does Faithfulness compare against evidence instead of judging whether the answer sounds plausible?**
  Faithfulness decomposes the answer into claims and checks whether each claim is supported by the supplied context; fluency is not enough.

- **Which failures should a quality gate block in CI or production?**
  Block unsupported answers, low faithfulness, retrieval regressions, and score drops below the agreed threshold in CI or release gates.

<!-- toc:begin -->
## In this series

- [RAG Deep Dive (1/6): Document Loading and Chunking — Inside LangChain TextSplitter](./01-document-loading-and-chunking.md)
- [RAG Deep Dive (2/6): Embeddings and the Vector Index — Inside FAISS IndexFlatL2](./02-embeddings-and-vector-index.md)
- [RAG Deep Dive (3/6): Retriever Design — VectorStoreRetriever and MMR](./03-retriever-design.md)
- [RAG Deep Dive (4/6): Prompt Construction and Context Injection — Inside PromptTemplate](./04-prompt-construction-and-context-injection.md)
- [RAG Deep Dive (5/6): Assembling the RAG Chain — RetrievalQA vs LCEL](./05-rag-chain-assembly.md)
- **RAG Deep Dive (6/6): Evaluation and Quality Gates — RAGAS Metrics and Faithfulness (current)**

<!-- toc:end -->

---

## References

### Official Docs

- [RAGAS evaluation quickstart](https://docs.ragas.io/en/stable/getstarted/evaluation/)
- [RAGAS metrics overview](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/)
- [LangChain evaluation concepts](https://python.langchain.com/docs/concepts/evaluation/)

### Source Code

- [RAGAS `evaluation.py` source](https://github.com/explodinggradients/ragas/blob/v0.1.22/src/ragas/evaluation.py)
- [RAGAS faithfulness metric source](https://github.com/explodinggradients/ragas/blob/v0.1.22/src/ragas/metrics/_faithfulness.py)
- [RAGAS answer relevancy metric source](https://github.com/explodinggradients/ragas/blob/v0.1.22/src/ragas/metrics/_answer_relevance.py)
- [RAGAS context precision metric source](https://github.com/explodinggradients/ragas/blob/v0.1.22/src/ragas/metrics/_context_precision.py)
- [LangChain evaluation loading source](https://github.com/langchain-ai/langchain/blob/langchain==0.2.17/libs/langchain/langchain/evaluation/loading.py)

Tags: RAG, LangChain, Vector Search, LLM
