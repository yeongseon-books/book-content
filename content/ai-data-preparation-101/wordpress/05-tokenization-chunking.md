---
title: "바이브코딩을 위한 AI 데이터 준비 (5/10): Tokenization과 Chunking 전략"
series: ai-data-preparation-101
episode: 5
language: ko
tags:
- Tokenization
- Chunking
- BPE
- tiktoken
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 데이터 준비 (5/10): Tokenization과 Chunking 전략

이 글은 **바이브코딩을 위한 AI 데이터 준비** 시리즈의 다섯 번째 글입니다.

---

바이브코딩으로 RAG 시스템을 만들거나 파인튜닝 데이터를 준비할 때 "텍스트를 어떻게 잘라야 하나요?"라는 질문이 반드시 나옵니다. 이게 바로 청킹(Chunking) 전략의 핵심 질문입니다.

토크나이제이션(Tokenization)은 텍스트를 모델이 처리하는 최소 단위(토큰)로 변환하는 것이고, 청킹은 긴 문서를 처리 가능한 크기로 분할하는 것입니다. 이 두 가지 선택이 검색 품질, 학습 효율, 컨텍스트 활용률에 직접적인 영향을 미칩니다.

> "청킹 전략을 잘못 선택하면 문서의 중요한 부분이 청크 경계에서 잘려나가고, 검색 품질이 크게 떨어집니다."

## 이 글에서 다룰 질문

1. BPE, WordPiece, SentencePiece 토크나이저는 어떻게 다른가요?
2. tiktoken으로 토큰 수를 정확히 세는 방법은?
3. 고정 크기, 문장 단위, 재귀 청킹의 차이는 무엇인가요?
4. 의미 기반 청킹(Semantic Chunking)은 언제 필요한가요?
5. 청킹 전략을 어떻게 평가하나요?

---

## 토크나이저 알고리즘 비교

| 알고리즘 | 사용 모델 | 특징 |
|---------|----------|------|
| BPE (Byte Pair Encoding) | GPT 시리즈 | 빠르고 효율적, 영어에 최적화 |
| WordPiece | BERT | 미지 단어 처리 강함 |
| SentencePiece | LLaMA, T5 | 다국어 처리, 언어 독립적 |

## tiktoken으로 토큰 수 측정

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """텍스트의 토큰 수를 정확히 계산합니다."""
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

# 사용 예시
text = "안녕하세요. GPT-4를 사용하는 방법을 알려주세요."
tokens = count_tokens(text)
print(f"토큰 수: {tokens}")

# 컨텍스트 활용률 계산
def context_utilization(chunks: list[str], max_tokens: int = 4096) -> dict:
    """청크들의 컨텍스트 윈도우 활용률을 계산합니다."""
    token_counts = [count_tokens(c) for c in chunks]
    return {
        "total_chunks": len(chunks),
        "avg_tokens": sum(token_counts) / len(token_counts),
        "max_tokens": max(token_counts),
        "utilization": sum(token_counts) / (len(token_counts) * max_tokens)
    }
```

## 청킹 전략 4가지

**1. 고정 크기 청킹 (Fixed Chunking)**
```python
def fixed_chunk(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """단어 단위로 일정한 크기로 분할합니다."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks
```

**2. 문장 단위 청킹 (Sentence-Aware Chunking)**
```python
import re

def sentence_chunk(text: str, max_tokens: int = 500) -> list[str]:
    """문장 경계를 유지하면서 청크를 만듭니다."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)
        if current_tokens + sentence_tokens > max_tokens and current:
            chunks.append(" ".join(current))
            current = []
            current_tokens = 0
        current.append(sentence)
        current_tokens += sentence_tokens

    if current:
        chunks.append(" ".join(current))
    return chunks
```

**3. 재귀 청킹 (Recursive Chunking)**
```python
def recursive_chunk(text: str, max_tokens: int = 500, separators: list[str] = None) -> list[str]:
    """단락 → 문장 → 단어 순서로 재귀적으로 분할합니다."""
    if separators is None:
        separators = ["\n\n", "\n", ". ", " "]

    if count_tokens(text) <= max_tokens:
        return [text]

    for sep in separators:
        if sep in text:
            parts = text.split(sep)
            chunks = []
            current = ""
            for part in parts:
                if count_tokens(current + sep + part) <= max_tokens:
                    current = current + sep + part if current else part
                else:
                    if current:
                        chunks.append(current)
                    current = part
            if current:
                chunks.append(current)
            return chunks

    # 마지막 수단: 단어 단위 분할
    return fixed_chunk(text, max_tokens)
```

**4. 의미 기반 청킹 (Semantic Chunking)**
```python
def semantic_chunk(text: str, similarity_threshold: float = 0.8) -> list[str]:
    """의미적으로 유사한 문장들을 하나의 청크로 묶습니다."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) <= 1:
        return sentences

    embeddings = [get_embedding(s) for s in sentences]
    chunks = [sentences[0]]
    current_chunk = [sentences[0]]

    for i in range(1, len(sentences)):
        similarity = cosine_similarity(embeddings[i-1], embeddings[i])
        if similarity >= similarity_threshold:
            current_chunk.append(sentences[i])
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i]]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 오버랩 없는 고정 청킹 | 경계에서 맥락 끊김 | 50-100 토큰 오버랩 추가 |
| 문장 중간에서 분할 | 의미가 잘림 | 문장 단위 또는 재귀 청킹 |
| 모든 문서에 같은 전략 | 문서 유형별 최적 전략 다름 | 구조적 문서는 재귀, 긴 산문은 의미 기반 |
| 토큰 수 추정만 사용 | 모델별 차이로 오차 발생 | tiktoken으로 정확히 계산 |

## AI 팁

청킹 전략을 선택할 때는 실제 검색 품질로 평가하세요. 이론적으로 좋아 보이는 전략이 실제로는 검색 성능이 낮을 수 있습니다.

```python
from dataclasses import dataclass

@dataclass
class ChunkExperimentResult:
    strategy: str
    chunk_size: int
    overlap: int
    avg_tokens: float
    retrieval_hit_at_5: float  # 검색 품질 지표
    cost_per_chunk: float

def choose_strategy(results: list[ChunkExperimentResult]) -> ChunkExperimentResult:
    """hit@5와 비용을 균형 있게 고려해 최적 전략을 선택합니다."""
    return max(results, key=lambda r: r.retrieval_hit_at_5 / max(r.cost_per_chunk, 0.001))
```

## 체크리스트

- [ ] 문서 유형에 맞는 청킹 전략을 선택했다
- [ ] tiktoken으로 토큰 수를 정확히 계산한다
- [ ] 오버랩 크기를 설정해 청크 경계 맥락을 보존한다
- [ ] 여러 청킹 전략을 실제 검색 품질로 비교했다
- [ ] 컨텍스트 활용률을 측정하고 있다

## 처음 질문으로 돌아가기

**토크나이저 알고리즘 차이는?** BPE는 GPT에서, WordPiece는 BERT에서, SentencePiece는 LLaMA/T5에서 사용합니다. 각각 다른 방식으로 텍스트를 분해하므로 같은 텍스트도 토큰 수가 다를 수 있습니다.

**tiktoken으로 토큰 수 세기는?** `tiktoken.encoding_for_model(model_name)`으로 모델에 맞는 인코더를 가져와 `len(enc.encode(text))`로 정확한 토큰 수를 계산합니다.

**4가지 청킹 전략 선택 기준은?** 구조적 문서(계층 헤딩)는 재귀 청킹, 긴 산문은 의미 기반, 간단한 경우는 문장 단위, 속도가 중요하면 고정 크기.

**의미 기반 청킹은 언제?** 주제 전환이 명확하지 않은 긴 산문 문서에서 의미적으로 연관된 내용을 하나의 청크로 묶어야 할 때.

**청킹 전략 평가 방법은?** 각 전략으로 청킹한 뒤 RAG 검색 품질(hit@k, MRR)로 비교합니다.

## 정리

토크나이제이션과 청킹은 AI 앱의 검색 품질과 학습 효율에 직접 영향을 미칩니다. tiktoken으로 정확한 토큰 수를 측정하고, 문서 유형에 맞는 청킹 전략을 선택해 실제 검색 품질로 검증하는 것이 핵심입니다.

다음 글에서는 저품질 데이터를 골라내는 **데이터 품질 필터링**을 다룹니다.

## 참고 자료

- [AI 데이터 준비 원문: Tokenization과 Chunking 전략](../ko/05-tokenization-chunking.md)
- [tiktoken - OpenAI Tokenizer](https://github.com/openai/tiktoken)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 데이터 준비 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
2. [바이브코딩을 위한 AI 데이터 준비 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
3. [바이브코딩을 위한 AI 데이터 준비 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
4. [바이브코딩을 위한 AI 데이터 준비 (4/10): PII 탐지와 익명화](./04-pii-detection-anonymization.md)
5. **바이브코딩을 위한 AI 데이터 준비 (5/10): Tokenization과 Chunking 전략 (현재 글)**
6. [바이브코딩을 위한 AI 데이터 준비 (6/10): 데이터 품질 필터링](./06-quality-filtering.md)
7. [바이브코딩을 위한 AI 데이터 준비 (7/10): 합성 데이터 생성](./07-synthetic-data-generation.md)
8. [바이브코딩을 위한 AI 데이터 준비 (8/10): 데이터 증강 기법](./08-data-augmentation.md)
9. [바이브코딩을 위한 AI 데이터 준비 (9/10): 학습/평가/테스트 분할](./09-train-eval-test-splitting.md)
10. [바이브코딩을 위한 AI 데이터 준비 (10/10): 프로덕션 데이터 파이프라인](./10-production-data-pipeline.md)
<!-- toc:end -->

Tags: Tokenization, Chunking, BPE, tiktoken, 바이브코딩
