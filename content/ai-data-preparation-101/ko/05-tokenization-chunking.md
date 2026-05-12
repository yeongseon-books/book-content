---
episode: 5

language: ko

last_reviewed: '2026-05-12'

series: ai-data-preparation-101

status: publish-ready

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

LLM 시스템에서는 토크나이저가 사소한 전처리 도구처럼 보이기 쉽습니다. 하지만 실제로는 모델이 무엇을 한 단위로 보는지, 같은 문서가 context window를 얼마나 차지하는지, retrieval이 어디에서 끊기는지를 모두 결정합니다.

특히 한국어와 영어, 코드가 섞인 코퍼스에서는 문자 수를 보고 토큰 수를 짐작하는 습관이 바로 비용 오판으로 이어집니다. 청킹도 마찬가지입니다. 적당히 1,000자씩 자르는 식으로는 문장 경계와 의미 단위가 쉽게 깨집니다.

운영에서는 토큰 효율과 의미 보존을 같이 봐야 합니다. 토큰 수를 줄이겠다고 vocab만 키우면 메모리 비용이 늘고, chunk를 잘게 쪼개면 retrieval recall이 떨어집니다. 반대로 chunk를 크게 잡으면 context budget이 낭비됩니다.

이 단계는 모델 앞단에 있지만, 비용·지연·품질을 동시에 좌우한다는 점에서 후반 운영 문제와도 직접 연결됩니다.

이 글은 AI Data Preparation 101 시리즈의 5번째 글입니다.

여기서는 대표적인 토크나이저 알고리즘과 실제 token counting 방법, 그리고 long document를 잘게 나누는 chunking 전략을 함께 정리하겠습니다.

## 이 글에서 다룰 문제

- 왜 같은 의미의 한국어 문장이 영어보다 더 많은 토큰을 쓰는 경우가 많을까요?
- BPE, WordPiece, SentencePiece는 어떤 기준으로 선택해야 할까요?
- 도메인 전용 모델에서 자체 토크나이저 학습이 가치 있는 순간은 언제일까요?
- fixed-size, sentence-aware, recursive, semantic chunking은 각각 어떤 trade-off를 가질까요?
- overlap을 너무 적게 또는 너무 많이 주면 retrieval 품질이 왜 나빠질까요?

## 왜 이 글이 중요한가

토큰화와 청킹을 잘 설계하면 같은 context window에서도 더 많은 정보를 담고, 검색 품질을 유지하면서 API 비용과 학습 비용을 줄일 수 있습니다. 특히 RAG와 파인튜닝 데이터 준비에서는 이 차이가 곧 성능 차이로 연결됩니다.

반대로 실제 토큰 수를 측정하지 않고 문자 수만 보고 설계하면, 한국어 문서가 예산을 훨씬 빠르게 태우거나 chunk 경계에서 핵심 엔티티가 잘려 나갑니다. 이런 문제는 모델 탓처럼 보이지만 사실 입력 단위 설계 문제입니다.

이 글은 토크나이저를 라이브러리 선택 문제로만 보지 않고, 모델 입력 효율을 정의하는 시스템 설계 문제로 바라보게 만드는 데 목적이 있습니다.

## 토큰화와 청킹을 이해하는 가장 좋은 방법: 모델이 실제로 읽는 단위와 문서가 잘리는 경계를 함께 설계하는 것입니다

토크나이저는 텍스트를 숫자로 바꾸는 도구이지만, 실무에서는 입력 비용 계산기이기도 합니다. 어떤 알고리즘을 쓰는지에 따라 같은 한국어 문장이 차지하는 토큰 수가 크게 달라집니다.

청킹은 그 다음 문제입니다. 긴 문서를 무작정 잘라 넣는 것이 아니라, 의미 단위를 최대한 유지하면서 모델 입력 예산 안에 들어가도록 나눠야 합니다. 따라서 토크나이저와 chunking 전략은 따로 최적화할 수 없습니다.

좋은 기본값은 항상 실제 토큰 수를 측정하고, 가장 큰 의미 단위를 최대한 유지하는 chunking 전략에서 출발하는 것입니다.

> 토큰화는 비용을 결정하고, 청킹은 의미 보존을 결정합니다. 둘 중 하나라도 대충 잡으면 모델 품질 문제를 입력 설계가 먼저 만들어 냅니다.

## 핵심 개념

### 대표적인 토크나이저 알고리즘을 먼저 구분합니다

프로덕션에서 자주 보는 선택지는 아래와 같습니다.

| 알고리즘 | 대표 모델 | 메모 |
| --- | --- | --- |
| **Word-level** | 초기 NLP 모델 | OOV 문제가 심해 거의 쓰지 않습니다 |
| **Character-level** | 일부 다국어 모델 | 시퀀스 길이가 과하게 늘어납니다 |
| **BPE** | GPT 계열, RoBERTa | 가장 흔한 기본값입니다 |
| **WordPiece** | BERT 계열 | BPE와 유사하지만 scoring이 다릅니다 |
| **SentencePiece (Unigram)** | T5, LLaMA, Gemma | 언어 독립적이고 다국어에 강합니다 |

새 프로덕션 모델이라면 대개 BPE나 SentencePiece에서 시작합니다. 한국어·영어 혼합 비중이 높다면 실제 토큰 효율을 반드시 비교해야 합니다.

### 실제 토큰 수는 `tiktoken`으로 측정합니다

OpenAI 계열 모델에서는 토큰 수를 추정하지 말고 바로 세는 편이 맞습니다.

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

같은 의미라도 한국어는 영어보다 토큰 효율이 낮은 경우가 많습니다. 코드, JSON, 로그가 섞이면 비율은 더 달라집니다. 따라서 비용 산정과 chunk size 설계는 반드시 실제 토크나이저 기준으로 해야 합니다.

### 도메인 전용 모델이라면 자체 토크나이저 학습도 고려합니다

전문 용어가 많거나 한국어 비중이 높은 코퍼스라면 in-house tokenizer가 sequence length를 유의미하게 줄일 수 있습니다.

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

다만 vocab size를 키우면 embedding matrix가 커지고 메모리 사용량이 늘어납니다. 시퀀스 길이를 줄이기 위해 무조건 큰 vocab을 택하는 것은 좋은 기본값이 아닙니다.

### chunking은 네 가지 전략으로 생각하면 됩니다

긴 문서를 자르는 전략은 단순하지만, 각각의 실패 모드가 다릅니다.

#### 1. Fixed-size chunking

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

구현은 가장 쉽지만 문장과 문단 경계를 무시합니다. baseline으로는 괜찮아도 운영 기본값으로 두기에는 의미 손실이 큽니다.

#### 2. Sentence-aware chunking

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

문장 단위로 나누기 때문에 최소한의 의미 경계는 지킵니다. 다만 문단 구조나 섹션 전환까지는 반영하지 못합니다.

#### 3. Recursive chunking

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

문단 → 줄바꿈 → 문장 → 공백 → 문자 순으로 가장 큰 의미 단위를 유지하려고 시도합니다. RAG 파이프라인에서 가장 널리 쓰이는 이유가 여기에 있습니다.

#### 4. Semantic chunking

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

주제 전환을 임베딩 유사도로 감지하므로 품질은 좋지만 비용이 큽니다. 챕터 구분이 뚜렷한 문서나 고품질 retrieval이 필요한 도메인에서 선택적으로 사용합니다.

### overlap은 경계를 부드럽게 만드는 안전장치입니다

chunk 경계에서 엔티티와 참조가 끊어지면 retrieval이 약해집니다. 그래서 10~20% overlap이 보통의 출발점입니다.

| chunk_size | overlap | 권장 사용처 |
| --- | --- | --- |
| 500 | 50 (10%) | 짧은 문맥 RAG |
| 1000 | 150 (15%) | 균형형 RAG |
| 2000 | 300 (15%) | 긴 문맥 요약 |

overlap이 0이면 경계 정보가 자주 사라지고, 50%를 넘기면 중복 정보가 늘어 retrieval 품질이 오히려 떨어질 수 있습니다. overlap은 많을수록 좋은 값이 아니라, 경계 손실을 완화하는 최소 공유 구간입니다.

## 흔히 헷갈리는 지점

- **문자 수만 보면 대략적인 토큰 수를 알 수 있습니다**: 언어와 코드 혼합 비율에 따라 차이가 커서 실제 토크나이저로 반드시 측정해야 합니다.
- **영어용 BPE를 한국어에도 그대로 써도 큰 차이는 없습니다**: 한국어는 토큰 비효율이 더 커질 수 있어 비용과 품질 모두 손해를 볼 수 있습니다.
- **fixed-size chunking이면 충분합니다**: 문장 경계와 문단 구조가 깨져 retrieval recall과 answer grounding이 떨어집니다.
- **overlap은 클수록 안전합니다**: 과도한 overlap은 중복 정보와 검색 혼선을 늘립니다. 10~20% 정도에서 시작하는 편이 좋습니다.

## 운영 체크리스트

- [ ] 도메인별 대표 샘플을 실제 토크나이저로 측정해 chars/token 비율을 기록했다
- [ ] 한국어·영어·코드 혼합 코퍼스에서 tokenizer 선택 이유를 문서화했다
- [ ] baseline fixed chunk 대신 sentence-aware 또는 recursive chunk를 기본값으로 쓴다
- [ ] chunk_size와 overlap을 retrieval 평가셋 기준으로 검증했다
- [ ] vocab_size 증가가 embedding memory에 주는 영향을 비용 추정에 반영했다

## 정리

토크나이저는 단순한 변환기처럼 보이지만 실제로는 모델이 보는 세계의 단위를 결정합니다. 같은 문서도 어떤 tokenizer를 쓰느냐에 따라 비용과 정보 밀도가 달라집니다.

청킹은 그 위에서 의미 경계를 얼마나 보존할지 결정합니다. fixed-size에서 출발하더라도 운영 기본값은 recursive나 최소한 sentence-aware chunking으로 가는 편이 안전합니다.

다음 글에서는 이렇게 토큰화 가능한 텍스트 중에서도 실제 학습 가치가 낮은 샘플을 어떻게 걸러낼지, heuristic과 classifier를 함께 쓰는 품질 필터링 전략을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- **Tokenization과 Chunking 전략 (현재 글)**
- [데이터 품질 필터링 — Heuristic과 Classifier](./06-quality-filtering.md)
- [합성 데이터 생성 — Self-Instruct부터 Distillation까지](./07-synthetic-data-generation.md)
- [데이터 증강 기법 — EDA부터 Back-Translation까지](./08-data-augmentation.md)
- [학습/평가/테스트 분할과 Contamination 통제](./09-train-eval-test-splitting.md)
- [프로덕션 데이터 파이프라인 구축](./10-production-data-pipeline.md)
<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Neural Machine Translation of Rare Words with Subword Units (Sennrich et al., 2016)](https://arxiv.org/abs/1508.07909)
- [SentencePiece: A simple and language independent subword tokenizer](https://arxiv.org/abs/1808.06226)
- [tiktoken - OpenAI tokenizer library](https://github.com/openai/tiktoken)
- [HuggingFace tokenizers documentation](https://huggingface.co/docs/tokenizers/index)

### 관련 시리즈
- [벡터 검색 101 — 05-chunking-strategies](../../vector-search-101/ko/05-chunking-strategies.md)
- [LLM 파인튜닝 101 — 데이터셋 준비와 전처리](../../llm-finetuning-101/ko/02-dataset.md)

Tags: Tokenization, BPE, SentencePiece, Chunking, RAG, tiktoken
