---
episode: 5
language: ko
last_reviewed: '2026-05-12'
seo_description: 토크나이저 선택과 chunking 전략이 모델 입력 단위, context window, retrieval 경계에 미치는
  영향을 정리합니다.
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
  medium: false
  mkdocs: true
  tistory: true
title: "AI Data Preparation 101 (5/10): Tokenization과 Chunking 전략"
---

# AI Data Preparation 101 (5/10): Tokenization과 Chunking 전략

LLM 시스템에서는 토크나이저가 사소한 전처리 도구처럼 보이기 쉽습니다. 하지만 실제로는 모델이 무엇을 한 단위로 보는지, 같은 문서가 context window를 얼마나 차지하는지, retrieval이 어디에서 끊기는지를 모두 결정합니다.

이 글은 AI Data Preparation 101 시리즈의 5번째 글입니다.

특히 한국어와 영어, 코드가 섞인 코퍼스에서는 문자 수를 보고 토큰 수를 짐작하는 습관이 바로 비용 오판으로 이어집니다. 청킹도 마찬가지입니다. 적당히 1,000자씩 자르는 식으로는 문장 경계와 의미 단위가 쉽게 깨집니다.

운영에서는 토큰 효율과 의미 보존을 같이 봐야 합니다. 토큰 수를 줄이겠다고 vocab만 키우면 메모리 비용이 늘고, chunk를 잘게 쪼개면 retrieval recall이 떨어집니다. 반대로 chunk를 크게 잡으면 context budget이 낭비됩니다.

이 단계는 모델 앞단에 있지만, 비용·지연·품질을 동시에 좌우한다는 점에서 후반 운영 문제와도 직접 연결됩니다.

여기서는 대표적인 토크나이저 알고리즘과 실제 token counting 방법, 그리고 long document를 잘게 나누는 chunking 전략을 함께 정리하겠습니다.

![AI 데이터 준비 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/05/05-01-big-picture.ko.png)
*AI 데이터 준비 5장 흐름 개요*
> Tokenization과 Chunking 전략의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 왜 같은 의미의 한국어 문장이 영어보다 더 많은 토큰을 쓰는 경우가 많을까요?
- BPE, WordPiece, SentencePiece는 어떤 기준으로 선택해야 할까요?
- 도메인 전용 모델에서 자체 토크나이저 학습이 가치 있는 순간은 언제일까요?

## 왜 이 글이 중요한가

토큰화와 청킹을 잘 설계하면 같은 context window에서도 더 많은 정보를 담고, 검색 품질을 유지하면서 API 비용과 학습 비용을 줄일 수 있습니다. 특히 RAG와 파인튜닝 데이터 준비에서는 이 차이가 곧 성능 차이로 연결됩니다.

반대로 실제 토큰 수를 측정하지 않고 문자 수만 보고 설계하면, 한국어 문서가 예산을 훨씬 빠르게 태우거나 chunk 경계에서 핵심 엔티티가 잘려 나갑니다. 이런 문제는 모델 탓처럼 보이지만 사실 입력 단위 설계 문제입니다.

이 글은 토크나이저를 라이브러리 선택 문제로만 보지 않고, 모델 입력 효율을 정의하는 시스템 설계 문제로 바라보게 만드는 데 목적이 있습니다.

## 핵심 관점

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
        # base case: 길이 기준 강제 분할
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

## 토큰 예산 기반 청킹 실험 설계

토크나이저를 선택한 뒤에는 chunking 실험을 숫자로 닫아야 합니다. 특히 RAG에서는 “chunk 크기”보다 “질문당 소비 토큰”과 “정답 근거 회수율”이 더 중요한 지표입니다.

```python
from dataclasses import dataclass

@dataclass
class ChunkExperimentResult:
    strategy: str
    chunk_size: int
    overlap: int
    avg_prompt_tokens: float
    p95_prompt_tokens: float
    retrieval_recall_at_5: float
    answer_f1: float

def choose_strategy(results: list[ChunkExperimentResult]) -> ChunkExperimentResult:
    # 하드 제약을 먼저 적용
    feasible = [r for r in results if r.p95_prompt_tokens <= 7000]
    # recall을 먼저 최적화하고 그다음 cost를 최적화
    feasible.sort(key=lambda r: (r.retrieval_recall_at_5, -r.avg_prompt_tokens), reverse=True)
    return feasible[0]
```

## Polars로 대규모 토큰 통계 계산

대형 코퍼스에서는 pandas보다 polars가 빠른 경우가 많습니다. 아래 예시는 chunk 단위 토큰 수 분포를 계산해 과대 chunk를 사전에 제거하는 패턴입니다.

```python
import polars as pl
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

def tok_len(s: str) -> int:
    return len(enc.encode(s))

pl_df = pl.read_parquet("data/chunks.parquet")
pl_df = pl_df.with_columns(
    pl.col("chunk_text").map_elements(tok_len, return_dtype=pl.Int32).alias("n_tokens")
)

stats = pl_df.select([
    pl.len().alias("rows"),
    pl.col("n_tokens").mean().alias("avg_tokens"),
    pl.col("n_tokens").quantile(0.95).alias("p95_tokens"),
    pl.col("n_tokens").quantile(0.99).alias("p99_tokens"),
]).to_dicts()[0]
print(stats)
```

`p99_tokens`가 과도하게 크면 retrieval 단계에서 일부 문서가 예산을 독점해 답변 품질이 흔들립니다. 이때는 separator 우선순위를 조정하거나, heading 단위 pre-split을 추가하는 편이 낫습니다.

## 적용 전후 chunk 샘플 비교

```text
[fixed-size]
...요금제 변경은 설정 페이지에서... (문장 중간 끊김)

[recursive]
### 요금제 변경
요금제 변경은 설정 페이지에서 요청할 수 있으며, 변경 즉시 과금 주기가 재계산됩니다.
```

문장 중간 분할이 줄어들수록 retrieval grounding이 좋아집니다. 실제 운영에서는 이런 샘플을 평가 리포트에 함께 넣어 전략 변경 이유를 남기는 편이 안전합니다.

## DVC stage로 재현성 확보

```yaml
stages:
  chunk_corpus:
    cmd: python pipelines/chunk_corpus.py --strategy recursive --max-tokens 700 --overlap 120
    deps:
      - pipelines/chunk_corpus.py
      - data/clean/corpus.parquet
    outs:
      - data/chunks/chunks_recursive.parquet
    metrics:
      - reports/chunk_stats.json
```

chunking도 실험 코드가 아니라 데이터 파이프라인의 일부입니다. 버전과 지표가 같이 남아야 다음 회차에서도 같은 결과를 재현할 수 있습니다.

## 검색 품질 관점의 chunk 평가 지표

청킹 전략을 바꿀 때는 생성 모델 점수만 보지 말고 retrieval 단계 지표를 먼저 봐야 합니다. 최소한 아래 세 지표를 같이 비교해야 합니다.

- `recall@k`: 정답 근거 chunk가 상위 k개 안에 들어오는 비율
- `mrr`: 정답 근거가 앞 순위에 오는지
- `context_utilization`: 프롬프트 토큰 중 실제 근거 토큰 비율

```python
def context_utilization(prompt_tokens: int, evidence_tokens: int) -> float:
    return evidence_tokens / max(prompt_tokens, 1)

def gating(metrics: dict) -> bool:
    return (
        metrics["recall_at_5"] >= 0.82 and
        metrics["mrr"] >= 0.70 and
        metrics["p95_prompt_tokens"] <= 7000
    )
```

## 문서 구조 기반 pre-split

대형 문서는 heading 단위 pre-split을 먼저 수행하면 recursive chunk 품질이 안정됩니다.

```python
import re

def split_by_heading(md_text: str) -> list[str]:
    parts = re.split(r"(?m)^#{1,3}\s+", md_text)
    return [p.strip() for p in parts if p.strip()]
```

이 단계를 넣으면 서로 다른 주제가 한 chunk에 섞이는 비율이 줄어들고, retrieval precision이 개선됩니다.

## 운영에서 바로 쓰는 점검 질문

아래 질문은 배포 직전 리뷰에서 실제로 자주 쓰는 체크 항목입니다. 단순 문서 확인이 아니라, 각 질문에 대해 파일 경로나 지표 값으로 즉시 답할 수 있어야 합니다.

1. 이번 데이터셋은 어떤 버전에서 왔고, sha256은 무엇인가요?
2. 지난 배치 대비 duplicate/null/length 분포가 얼마나 변했나요?
3. 제거된 샘플은 어떤 규칙 때문에 빠졌고, 상위 제거 사유는 무엇인가요?
4. train/eval/test 경계에서 누수 가능성은 수치로 얼마나 남아 있나요?
5. 이번 배치에서 사람이 검토한 샘플과 발견된 오류 유형은 무엇인가요?

```python
def release_readiness(summary: dict) -> tuple[bool, list[str]]:
    issues = []
    if not summary.get("dataset_sha256"):
        issues.append("missing_dataset_sha256")
    if summary.get("duplicate_ratio", 1.0) > 0.10:
        issues.append("duplicate_ratio_too_high")
    if summary.get("null_ratio", 1.0) > 0.02:
        issues.append("null_ratio_too_high")
    if summary.get("contamination_ratio", 1.0) > 0.01:
        issues.append("contamination_ratio_too_high")
    if summary.get("human_reviewed_rows", 0) < 100:
        issues.append("insufficient_human_review")
    return len(issues) == 0, issues
```

운영 팀은 이 함수를 그대로 쓰지 않더라도 같은 개념을 파이프라인 게이트로 구현해야 합니다. 핵심은 “준비가 되었는지 느낌으로 판단하지 않는다”는 점입니다.

## 실무 로그 예시

```text
[release-check] dataset=v2.4.1 sha=4fb1...
[release-check] duplicate_ratio=0.061 null_ratio=0.008
[release-check] contamination_ratio=0.004 human_reviewed_rows=240
[release-check] status=PASS
```

이 로그 한 묶음이 있으면 모델 성능이 흔들릴 때도 데이터 준비 단계를 빠르게 제외하거나 집중 점검할 수 있습니다. 데이터 준비의 품질은 글 한 편의 설명보다, 이런 반복 가능한 검증 로그에서 드러납니다.

### 토큰 예산 SLA

실무에서는 `질문 1회당 p95 7k tokens 이하`처럼 명시적 SLA를 두는 편이 좋습니다. chunk 전략이 바뀌어도 SLA를 넘기면 자동 실패시키면 비용 회귀를 빠르게 막을 수 있습니다.

### 릴리스 노트에 남겨야 할 최소 항목

해당 단계의 변경은 릴리스 노트에도 남겨야 합니다. 최소한 `변경 규칙`, `영향받은 행 수`, `핵심 지표 변화`, `롤백 경로` 네 항목이 있어야 다음 배치에서 같은 판단을 반복할 수 있습니다.

토큰 예산은 모델 교체 시 즉시 재측정하고, 예전 추정치를 재사용하지 않는 것이 안전합니다.

청킹 전략 변경 후에는 동일 질문 세트로 A/B 평가를 다시 수행해 회귀를 확인해야 합니다.

모델 context window가 커졌더라도 무조건 큰 chunk가 정답은 아닙니다. 검색 단계에서는 작은 chunk가 더 정확한 근거를 찾는 경우가 많아, 비용과 품질을 같이 비교해 결정해야 합니다.

토큰 비용 추정은 월별 실제 사용량과 연결해 검증해야 장기적으로 정확해집니다.

예산 초과 경보도 필수입니다.

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

## 처음 질문으로 돌아가기

- **왜 같은 의미의 한국어 문장이 영어보다 더 많은 토큰을 쓰는 경우가 많을까요?**
  - `count_tokens()`로 같은 길이의 영어·한국어·코드를 세어 보면 문자 수가 비슷해도 토큰 수는 다르게 나옵니다. 그래서 이 글은 글자 수가 아니라 실제 `tiktoken` 결과를 기준으로 비용과 chunk size를 잡아야 한다고 설명했습니다.
- **BPE, WordPiece, SentencePiece는 어떤 기준으로 선택해야 할까요?**
  - 답은 이름보다 corpus와 운영 제약에 있습니다. 이 글의 기준으로는 실제 토큰 분포를 먼저 재 보고, 필요하면 `Tokenizer(BPE(...))`처럼 직접 학습한 결과가 sequence length를 줄이는지 확인한 뒤 선택하는 편이 맞습니다.
- **도메인 전용 모델에서 자체 토크나이저 학습이 가치 있는 순간은 언제일까요?**
  - `custom-bpe-32k.json`처럼 자체 tokenizer를 학습했을 때 전문 용어와 한국어 비중 때문에 토큰 수가 실제로 줄어드는 순간 가치가 생깁니다. 반대로 vocab만 키우고 embedding matrix 비용만 늘어난다면 굳이 새 tokenizer를 유지할 이유가 없습니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Data Preparation 101 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [AI Data Preparation 101 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [AI Data Preparation 101 (4/10): 학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- **Tokenization과 Chunking 전략 (현재 글)**
- 데이터 품질 필터링 — Heuristic과 Classifier (예정)
- 합성 데이터 생성 — Self-Instruct부터 Distillation까지 (예정)
- 데이터 증강 기법 — EDA부터 Back-Translation까지 (예정)
- 학습/평가/테스트 분할과 Contamination 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)

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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-data-preparation-101/ko/05-tokenization-chunking)

Tags: Tokenization, BPE, SentencePiece, Chunking, RAG, tiktoken
