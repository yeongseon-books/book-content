---
title: "AI Data Preparation 101 (5/10): Tokenization and Chunking Strategies"
series: ai-data-preparation-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Tokenization
- BPE
- SentencePiece
- Chunking
- RAG
- tiktoken
last_reviewed: '2026-05-14'
seo_description: Entities and references cut at chunk boundaries lose information.
  Overlap shares some tokens with adjacent chunks.
---

# AI Data Preparation 101 (5/10): Tokenization and Chunking Strategies

In LLM systems, the tokenizer is not a minor preprocessing detail. It defines the units the model sees, and poor chunking decisions waste context window budget while hurting retrieval and answer quality.

This is the 5th post in the AI Data Preparation 101 series. Here we cover how tokenization affects quality and cost, and how to split long documents into usable chunks.


![AI data preparation chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/05/05-01-big-picture.en.png)
*AI data preparation chapter 5 flow overview*

> Tokenization is where text stops being prose and starts being model input — chunking decisions made here silently set the upper bound on how well retrieval, context windows, and downstream eval can work.

## Questions to Keep in Mind

- Why do Korean, English, and code consume the context window so differently?
- When should you stay with a general-purpose tokenizer and when should you train your own?
- What trade-offs separate fixed-size, sentence-aware, recursive, and semantic chunking?

## "The tokenizer decides model quality?"

In LLMs, tokenization is not just preprocessing. The moment the tokenizer is fixed, the units the model can see and the efficiency of its context window are decided. The reason GPT-4 uses far fewer tokens than GPT-3 for the same Korean text is that its tokenizer was retrained.

This episode covers two topics.

1. **Tokenization**: text -> token id conversion (subword algorithms)
2. **Chunking**: long documents -> splits that fit the model input

## Tokenization algorithms - 4 options

| Algorithm | Representative model | Notes |
| --- | --- | --- |
| Word-level | Old NLP | Severe OOV; rarely used |
| Character-level | Some multilingual models | Sequence length explodes |
| BPE (Byte-Pair Encoding) | GPT-2, GPT-3, RoBERTa | Most common |
| WordPiece | BERT, DistilBERT | Similar to BPE, different scoring |
| SentencePiece (Unigram) | T5, LLaMA, Gemma | Language-agnostic |

For new production models, BPE or SentencePiece are the default choice.

## Counting tokens with tiktoken

For OpenAI models, `tiktoken` measures token counts quickly.

```python
# pip install tiktoken
import tiktoken

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

samples = {
    "english": "The quick brown fox jumps over the lazy dog.",
    "korean": "빠른 갈색 여우가 게으른 개를 뛰어넘는다.",
    "code": "def add(a, b):\n    return a + b",
}
for name, text in samples.items():
    n = count_tokens(text)
    chars = len(text)
    print(f"{name:8s} chars={chars:3d} tokens={n:3d} ratio={chars/n:.2f}")
```

For the same meaning, Korean is 1.5-2x less token-efficient than English. Under cl100k_base (GPT-4), one Korean character expands to 1-3 tokens.

## Training a tokenizer on your own corpus

For a domain-specific model, training a tokenizer from scratch is worthwhile.

```python
# pip install tokenizers
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel

tokenizer = Tokenizer(BPE(unk_token="<unk>"))
tokenizer.pre_tokenizer = ByteLevel()

trainer = BpeTrainer(
    vocab_size=32000,
    special_tokens=["<pad>", "<unk>", "<s>", "</s>", "<mask>"],
    min_frequency=2,
)

files = ["data/corpus_ko.txt", "data/corpus_en.txt"]
tokenizer.train(files, trainer)
tokenizer.save("custom-bpe-32k.json")

# Use it
loaded = Tokenizer.from_file("custom-bpe-32k.json")
ids = loaded.encode("Hello 안녕하세요").ids
print(ids, "->", loaded.decode(ids))
```

vocab size directly affects model size and memory. Rough guidance:

- Sub-7B models: 32k
- 7B - 70B: 50k - 100k
- Multilingual: 128k or more

A larger vocab shortens sequence length and speeds training, but the embedding matrix grows and consumes more memory.

## Chunking - 4 strategies for long documents

LLM context windows are finite. Long documents must be split into chunks.

### 1. Fixed-size chunking

Simplest. Mostly used as a baseline.

```python
def fixed_chunk(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
```

Problem: it ignores sentence and paragraph boundaries, so meaning gets cut.

### 2. Sentence-aware chunking

```python
import re

def sentence_chunk(text: str, max_tokens: int = 500,
                   token_count=count_tokens) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, current, current_tokens = [], [], 0
    for sent in sentences:
        n = token_count(sent)
        if current_tokens + n > max_tokens and current:
            chunks.append(" ".join(current))
            current, current_tokens = [], 0
        current.append(sent)
        current_tokens += n
    if current:
        chunks.append(" ".join(current))
    return chunks
```

Splits by sentence and accumulates without exceeding the token budget.

### 3. Recursive chunking (LangChain style)

Tries separators in priority order.

```python
def recursive_chunk(text: str, max_tokens: int = 500,
                    separators: list[str] | None = None,
                    token_count=count_tokens) -> list[str]:
    separators = separators or ["\n\n", "\n", ". ", " ", ""]
    if token_count(text) <= max_tokens:
        return [text]
    sep = separators[0]
    if not sep:
        # base case: forced length-based split
        mid = len(text) // 2
        return recursive_chunk(text[:mid], max_tokens, separators[1:]) + \
               recursive_chunk(text[mid:], max_tokens, separators[1:])
    parts = text.split(sep)
    chunks, current = [], ""
    for p in parts:
        candidate = current + sep + p if current else p
        if token_count(candidate) > max_tokens:
            if current:
                chunks.append(current)
            if token_count(p) > max_tokens:
                chunks.extend(recursive_chunk(p, max_tokens, separators[1:]))
                current = ""
            else:
                current = p
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks
```

By trying paragraph -> sentence -> word -> char order, meaning is preserved at the largest possible unit. This is the most common choice in RAG pipelines.

### 4. Semantic chunking

Splits where embedding similarity drops.

```python
from sentence_transformers import SentenceTransformer
import numpy as np

def semantic_chunk(text: str, threshold: float = 0.3) -> list[str]:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) <= 1:
        return sentences
    embs = model.encode(sentences, normalize_embeddings=True)
    chunks, current = [], [sentences[0]]
    for i in range(1, len(sentences)):
        sim = float(np.dot(embs[i-1], embs[i]))
        if sim < threshold:  # topic shift detected
            chunks.append(" ".join(current))
            current = [sentences[i]]
        else:
            current.append(sentences[i])
    if current:
        chunks.append(" ".join(current))
    return chunks
```

Costly, but effective on documents with clear chapter or topic boundaries.

## Chunk overlap - why it matters

Entities and references cut at chunk boundaries lose information. Overlap shares some tokens with adjacent chunks. 10-20% of chunk size is a safe starting point.

| chunk_size | overlap | Recommended use |
| --- | --- | --- |
| 500 | 50 (10%) | RAG short context |
| 1000 | 150 (15%) | RAG balanced |
| 2000 | 300 (15%) | Long context |

If overlap exceeds 50%, duplicate information actually degrades retrieval quality.

## 5 common mistakes

1. **Applying English BPE directly to Korean**: one Korean character explodes to 3-4 tokens. If your domain is Korean-heavy, train a ko-aware tokenizer or use a multilingual SentencePiece model.
2. **Using fixed-size chunking in production**: ignores sentence boundaries and loses meaning. Move to sentence-aware at minimum.
3. **Setting overlap to 0**: entities cut at boundaries break retrieval. 10-20% overlap is the baseline.
4. **Estimating token count from char count**: ratios shift with Korean/English/code mix. Always measure with the actual tokenizer.
5. **Blindly increasing vocab size**: the embedding matrix balloons memory. 32k is enough below 7B.

## Key Takeaways

- BPE / WordPiece / SentencePiece are the default options for production tokenizers.
- Korean is 1.5-2x less token-efficient than English, so domain-level measurement is mandatory.
- For domain-specific models, training a tokenizer in-house can substantially shrink sequence length.
- Chunking has 4 strategies; recursive chunking with 10-20% overlap is the typical RAG starting point.
- Always validate chunk_size, overlap, and vocab_size against actual token counts.
- Episode 6 covers quality filtering.

---

## Operational checklist

- [ ] Measure real token counts for representative Korean, English, and code samples
- [ ] Document why the current tokenizer fits the language and domain mix
- [ ] Prefer sentence-aware or recursive chunking over fixed-size splits for production retrieval
- [ ] Tune chunk size and overlap against retrieval or answer-quality evaluations
- [ ] Include embedding-memory cost when considering larger vocabularies

## Answering the Opening Questions

- **Why does the same Korean sentence often consume more tokens than its English equivalent?**
  - Running `count_tokens()` on equivalent English, Korean, and code strings shows that similar character counts produce different token counts. The article therefore insists on using actual `tiktoken` output—not character length—as the basis for cost and chunk-size decisions.
- **On what basis should you choose between BPE, WordPiece, and SentencePiece?**
  - The answer lies in corpus characteristics and operational constraints, not in names. The article's approach is to first measure actual token distributions, then verify whether a custom `Tokenizer(BPE(...))` reduces sequence length before committing.
- **When is training a domain-specific tokenizer actually valuable?**
  - It becomes valuable when—as with `custom-bpe-32k.json`—specialized terms and Korean content cause a measurable reduction in token count. If expanding the vocabulary only inflates the embedding matrix without shrinking sequences, maintaining a custom tokenizer is not justified.
<!-- toc:begin -->
## In this series

- [AI Data Preparation 101 (1/10): Why Data Preparation Determines Model Quality](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): Source Data Collection and Cataloging](./02-source-data-collection-cataloging.md)
- [AI Data Preparation 101 (3/10): Cleaning and Deduplication](./03-cleaning-deduplication.md)
- [AI Data Preparation 101 (4/10): PII Detection and Anonymization for Training Data](./04-pii-detection-anonymization.md)
- **Tokenization and Chunking Strategies (current)**
- Quality Filtering - Heuristics and Classifiers (upcoming)
- Synthetic Data Generation - From Self-Instruct to Distillation (upcoming)
- Data Augmentation - From EDA to Back-Translation (upcoming)
- Train/Eval/Test Splitting and Contamination Control (upcoming)
- Building a Production Data Pipeline (upcoming)

<!-- toc:end -->

## References

- [Neural Machine Translation of Rare Words with Subword Units (Sennrich et al., 2016)](https://arxiv.org/abs/1508.07909)
- [SentencePiece: A simple and language independent subword tokenizer](https://arxiv.org/abs/1808.06226)
- [tiktoken - OpenAI tokenizer library](https://github.com/openai/tiktoken)
- [HuggingFace tokenizers documentation](https://huggingface.co/docs/tokenizers/index)

Tags: Tokenization, BPE, SentencePiece, Chunking, RAG, tiktoken
