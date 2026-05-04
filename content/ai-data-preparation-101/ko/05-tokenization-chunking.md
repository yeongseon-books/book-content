---
episode: 5
language: ko
last_reviewed: '2026-05-03'
series: ai-data-preparation-101
status: content-ready
tags:
- Tokenization
- BPE
- SentencePiece
- Chunking
- RAG
- tiktoken
targets:
  ebook: true
  medium: true
  mkdocs: true
  tistory: true
title: Tokenization과 Chunking 전략
seo_description: LLM에서 tokenization은 단순한 전처리가 아닙니다. tokenizer가 정해지는 순간, 모델이 볼 수 있는
  단위와 context…
---

# Tokenization과 Chunking 전략

> AI Data Preparation 101 시리즈 (5/10)

---
## "Tokenizer가 모델 품질을 결정한다고요?"

LLM에서 tokenization은 단순한 전처리가 아닙니다. tokenizer가 정해지는 순간, 모델이 볼 수 있는 단위와 context window의 효율성이 결정됩니다. GPT-3와 GPT-4가 같은 양의 한국어를 처리할 때 GPT-4가 훨씬 적은 token을 쓰는 이유는 tokenizer를 새로 학습했기 때문입니다.

이번 편은 두 가지 주제를 다룹니다.

1. **Tokenization**: text → token id 변환 (subword 알고리즘)
2. **Chunking**: 긴 문서 → 모델 입력 길이로 분할

## Tokenization 알고리즘 — 4가지

| Algorithm | 대표 모델 | 특징 |
| --- | --- | --- |
| Word-level | 구식 NLP | OOV 문제 심각, 잘 안 씀 |
| Character-level | 일부 multilingual | sequence length 폭발 |
| BPE (Byte-Pair Encoding) | GPT-2, GPT-3, RoBERTa | 가장 보편적 |
| WordPiece | BERT, DistilBERT | BPE와 유사, scoring 다름 |
| SentencePiece (Unigram) | T5, LLaMA, Gemma | 언어 독립적 |

production에서 새 모델을 만들 때는 BPE 또는 SentencePiece가 기본 선택입니다.

## tiktoken으로 token 수 측정

OpenAI 모델용 token 수는 `tiktoken`으로 빠르게 잴 수 있습니다.

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

같은 의미라도 한국어가 영어보다 token 효율이 1.5~2배 나쁩니다. cl100k_base(GPT-4) 기준으로 한국어 한 글자가 1~3 token으로 분해됩니다.

## tokenizer 학습 — 자체 코퍼스로

domain-specific 모델을 학습한다면 tokenizer를 처음부터 학습하는 것이 좋습니다.

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

# 사용
loaded = Tokenizer.from_file("custom-bpe-32k.json")
ids = loaded.encode("Hello 안녕하세요").ids
print(ids, "->", loaded.decode(ids))
```

vocab size는 모델 크기와 메모리에 직접 영향을 줍니다. 일반 가이드라인:

- 7B 미만 모델: 32k
- 7B ~ 70B: 50k ~ 100k
- multilingual: 128k 이상

vocab을 키우면 sequence length가 줄어 학습 속도가 빨라지지만, embedding 행렬이 커져 메모리가 증가합니다.

## Chunking — 긴 문서 처리 4가지 전략

LLM의 context window는 유한합니다. 긴 문서는 chunk로 나눠야 합니다.

### 1. Fixed-size chunking

가장 단순. 주로 baseline으로만 사용.

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

문제: sentence나 paragraph 경계를 무시해서 의미가 잘립니다.

### 2. Sentence-aware chunking

```python
import re

def sentence_chunk(text: str, max_tokens: int = 500,
                   token_count=count_tokens) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+|(?<=[다요죠])\s+", text)
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

문장 단위로 자르되 token 예산을 초과하지 않게 누적합니다. 한국어 문장 종결(`다`, `요`, `죠`)도 splitter에 포함합니다.

### 3. Recursive chunking (LangChain 스타일)

separator를 우선순위 순으로 시도합니다.

```python
def recursive_chunk(text: str, max_tokens: int = 500,
                    separators: list[str] | None = None,
                    token_count=count_tokens) -> list[str]:
    separators = separators or ["\n\n", "\n", ". ", " ", ""]
    if token_count(text) <= max_tokens:
        return [text]
    sep = separators[0]
    if not sep:
        # base case: 강제로 길이 기반
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

paragraph → sentence → word → char 순으로 분할을 시도하기 때문에 가장 큰 단위에서 의미가 보존됩니다. RAG 파이프라인에서 가장 흔하게 쓰입니다.

### 4. Semantic chunking

embedding similarity가 떨어지는 지점에서 분할합니다.

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

비용이 크지만 chapter나 topic boundary가 분명한 문서에 효과적입니다.

## Chunk overlap — 왜 필요한가

chunk 경계에서 잘린 entity나 reference 때문에 정보가 손실됩니다. overlap으로 일부 token을 인접 chunk와 공유합니다. 일반적으로 chunk size의 10~20%가 안전한 시작점입니다.

| chunk_size | overlap | 권장 |
| --- | --- | --- |
| 500 | 50 (10%) | RAG short context |
| 1000 | 150 (15%) | RAG balanced |
| 2000 | 300 (15%) | long context |

overlap을 50% 이상 잡으면 중복 정보가 retrieval에서 오히려 성능을 떨어뜨립니다.

## 흔한 실수 5가지

1. **English BPE를 한국어에 그대로 적용**: 한국어 한 글자가 3~4 token으로 폭발. domain이 한국어 비중 크면 ko-aware tokenizer를 학습하거나 SentencePiece multilingual 모델을 씁니다.
2. **Fixed-size chunking을 production에 사용**: sentence boundary 무시로 의미 손실. 최소 sentence-aware로 갑니다.
3. **Overlap을 0으로 둠**: chunk 경계에서 entity가 잘리면 retrieval이 망가집니다. 10~20% overlap이 baseline입니다.
4. **Token count를 char count로 추정**: 한국어와 영어 비율, 코드 비율에 따라 ratio가 달라집니다. 항상 실제 tokenizer로 측정합니다.
5. **vocab size를 무작정 크게**: embedding 행렬이 커져 메모리 폭발. 7B 미만은 32k면 충분합니다.

## 핵심 요약

- BPE / WordPiece / SentencePiece가 production tokenizer의 기본 옵션입니다.
- 한국어는 영어 대비 token 효율이 1.5~2배 나쁘므로 domain별 측정이 필수입니다.
- domain-specific 모델은 tokenizer를 자체 학습하면 sequence length를 크게 줄일 수 있습니다.
- Chunking은 4가지 전략이 있고, RAG에는 recursive chunking + 10~20% overlap이 일반적인 시작점입니다.
- chunk_size, overlap, vocab_size는 항상 실제 token count로 검증합니다.
- 다음 편(6편)은 quality filtering입니다.

---

<!-- toc:begin -->
## AI Data Preparation 101 시리즈

- [데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- **Tokenization과 Chunking 전략 (현재 글)**
- 데이터 품질 필터링 (예정)
- 합성 데이터 생성 (예정)
- 데이터 증강 기법 (예정)
- 학습/평가/테스트 분할과 오염 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Neural Machine Translation of Rare Words with Subword Units (Sennrich et al., 2016)](https://arxiv.org/abs/1508.07909)
- [SentencePiece: A simple and language independent subword tokenizer](https://arxiv.org/abs/1808.06226)
- [tiktoken - OpenAI tokenizer library](https://github.com/openai/tiktoken)
- [HuggingFace tokenizers documentation](https://huggingface.co/docs/tokenizers/index)

Tags: Tokenization, BPE, SentencePiece, Chunking, RAG, tiktoken
