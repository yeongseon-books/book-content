---
title: "LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치"
series: llm-from-scratch-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LLM
- PyTorch
- Transformer
- Tutorial
last_reviewed: '2026-05-12'
seo_description: 토크나이저까지 만들고 나면 잠깐 멍해집니다. 이제 입력은 숫자니까 끝난 것 같지만, 사실 아직 시작도 아닙니다.
---

# LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치

토크나이저를 만들고 나면 흔히 이런 착각이 듭니다. 이제 텍스트를 숫자로 바꿨으니 모델이 곧바로 이해할 수 있을 것 같다는 생각입니다. 하지만 정수 ID 배열만으로는 신경망이 아무 의미도 읽어 내지 못합니다.

이 글은 LLM from Scratch 101 시리즈의 2번째 글입니다.

`12, 4, 38, 2` 같은 숫자열은 아직 인덱스 목록일 뿐입니다. 12번 토큰이 13번 토큰과 비슷한지, 셰익스피어 문체에서 어떤 역할을 하는지는 이 숫자만으로는 알 수 없습니다. 의미는 임베딩 테이블 안에서 학습된 벡터를 통해 비로소 생깁니다.

여기서 한 가지가 더 필요합니다. 토큰이 무엇인지만 알아서는 충분하지 않습니다. 같은 `a`라도 문장 첫머리에 있는지 끝부분에 있는지에 따라 역할이 다르고, 모델은 그 순서 감각까지 받아야 합니다. 그래서 토큰 임베딩과 위치 임베딩이 함께 등장합니다.

이번 글에서는 `nn.Embedding`을 거창한 수학 객체가 아니라 룩업 테이블로 이해하고, 토큰 의미와 위치 정보를 더해 `(B, T, C)` 입력 텐서를 만드는 과정을 `model.py` 수준에서 정리하겠습니다.

![LLM from Scratch 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/02/02-01-sinusoidal-vs-learned-positional-embeddi.ko.png)
*LLM from Scratch 101 2장 흐름 개요*

## 이 글에서 다룰 문제

- `nn.Embedding`은 실제로 어떤 연산을 수행할까요?
- 토큰 임베딩만으로는 왜 충분하지 않을까요?
- 위치 정보는 왜 별도 임베딩으로 다루는 편이 실용적일까요?
- `(B, T, C)` 텐서 shape를 어디서 확정하는 게 좋을까요?
- 임베딩 초기화와 scale 설정이 학습 안정성에 어떤 영향을 줄까요?

## 왜 이 글이 중요한가

임베딩은 LLM 내부 표현의 첫 번째 관문입니다. 토크나이저가 텍스트를 숫자로 잘랐다면, 임베딩은 그 숫자를 모델이 다룰 수 있는 연속 벡터 공간으로 올려 보냅니다. 이 단계가 없으면 뒤에 있는 선형층과 어텐션은 아무 의미 있는 구조도 학습할 수 없습니다.

실전 감각에서도 중요합니다. 임베딩 차원, 위치 임베딩 방식, 컨텍스트 길이는 모두 메모리 사용량과 학습 안정성에 직접 연결됩니다. 특히 작은 GPT를 직접 구현하는 시리즈에서는 텐서 shape 감각을 여기서 확실히 잡아 두는 것이 이후 블록 구현과 디버깅을 크게 단순하게 만듭니다.

## 핵심 관점

임베딩을 처음 배울 때 가장 실용적인 관점은 이것입니다. **임베딩은 토큰 ID를 받아 해당 행 벡터를 꺼내 오는 룩업 테이블**입니다. 여기에 위치별 벡터를 담은 또 하나의 테이블을 더하면, 모델은 "무슨 토큰인가"와 "몇 번째 위치인가"를 동시에 입력으로 받게 됩니다.

> 이번 글의 핵심 문장은 간단합니다. 모델이 읽는 첫 입력 벡터는 `token_emb + pos_emb`입니다.

## 임베딩 아키텍처 다이어그램

```
입력 토큰 ID:  [3, 2, 4, 4, 5]     shape: (B=1, T=5)
                |
                v
Token Emb Table (65 x 128):
  ID=3 -> [0.12, -0.34, ..., 0.88]   shape: (128,)
  ID=2 -> [-0.07, 0.91, ..., -0.23]
  ID=4 -> [0.55,  0.11, ...,  0.43]
  ...
                |
                v
tok_emb:  (B=1, T=5, C=128)

위치 인덱스:   [0, 1, 2, 3, 4]       shape: (T=5,)
                |
                v
Pos Emb Table (64 x 128):
  pos=0 -> [0.01, -0.02, ..., 0.05]  shape: (128,)
  pos=1 -> [-0.03, 0.07, ..., 0.11]
  ...
                |
                v
pos_emb:  (T=5, C=128)  -- broadcast -> (B=1, T=5, C=128)

덧셈 (broadcasting):
x = tok_emb + pos_emb    shape: (B=1, T=5, C=128)
```

## 핵심 개념

### `nn.Embedding`은 학습 가능한 룩업 테이블

`nn.Embedding(vocab_size, n_embd)`는 `(vocab_size, n_embd)` 크기의 학습 가능한 행렬입니다. 입력 토큰 ID가 들어오면 그 ID에 해당하는 행을 가져옵니다.

직접 구현해 보면 본질이 더 분명해집니다.

```python
import torch
import torch.nn as nn

class MiniEmbedding(nn.Module):
    """nn.Embedding의 핵심 동작을 직접 구현한 버전."""

    def __init__(self, vocab_size: int, n_embd: int) -> None:
        super().__init__()
        # 실제 nn.Embedding도 내부적으로는 이것과 거의 동일
        self.weight = nn.Parameter(torch.randn(vocab_size, n_embd) * 0.02)

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        # idx: (B, T) 정수 텐서
        # weight[idx]: 인덱스 idx의 행을 추출 -> (B, T, n_embd)
        return self.weight[idx]

# 검증
idx = torch.tensor([[0, 1, 2], [2, 1, 0]])  # (B=2, T=3)
emb = MiniEmbedding(vocab_size=4, n_embd=8)
out = emb(idx)
print(out.shape)   # torch.Size([2, 3, 8])

# PyTorch 내장과 비교
std_emb = nn.Embedding(4, 8)
std_emb.weight = emb.weight  # 같은 파라미터 공유
assert torch.allclose(out, std_emb(idx))
print("MiniEmbedding == nn.Embedding: OK")
```

출력 shape가 `(2, 3, 8)`이라면 이미 중요한 구조를 이해한 것입니다. 배치 크기 2, 시퀀스 길이 3, 임베딩 차원 8이라는 의미가 한 줄로 드러납니다.

### 위치 임베딩이 없으면 순서 정보가 사라진다

토큰 임베딩만 있다면 모델은 어떤 토큰이 들어왔는지는 알 수 있어도, 그 토큰이 시퀀스의 몇 번째 위치에 놓였는지는 알 수 없습니다.

```python
# 순서 정보 없이는 같은 결과
import torch.nn as nn

emb = nn.Embedding(65, 128)
a = torch.tensor([[5, 3, 7]])   # "ace"
b = torch.tensor([[7, 5, 3]])   # "eac" (같은 토큰, 다른 순서)

# 토큰 임베딩만으로는 구별 불가
out_a = emb(a).mean(dim=1)  # 평균 풀링 후
out_b = emb(b).mean(dim=1)
# 순서 무시하고 평균 내면 동일한 결과가 될 수 있음
print(torch.allclose(out_a, out_b))  # 같은 토큰 집합이면 True
```

위치 임베딩이 있어야 같은 토큰이라도 위치에 따라 다른 벡터로 처리됩니다.

### 위치 임베딩 방식 비교

| 방식 | 장점 | 한계 | 이번 시리즈 선택 |
| --- | --- | --- | --- |
| learned | 구현 단순, GPT 계열과 정합성 높음 | `block_size` 초과 길이 일반화 약함 | 사용 |
| sinusoidal | 길이 일반화 직관적 | 구현/해석 분리감 | 미사용 |
| rotary(RoPE) | 긴 문맥에서 강한 성능 사례 | 구현 복잡도 상승 | 미사용 |

### GPT 입력부 최소 구현

```python
from dataclasses import dataclass

import torch
import torch.nn as nn

@dataclass
class GPTConfig:
    vocab_size: int = 65
    block_size: int = 64
    n_layer: int = 6
    n_head: int = 4
    n_embd: int = 128
    dropout: float = 0.1

class GPTEmbedding(nn.Module):
    """GPT 입력부: token embedding + positional embedding."""

    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        self.config = config
        self.token_embedding_table = nn.Embedding(config.vocab_size, config.n_embd)
        self.position_embedding_table = nn.Embedding(config.block_size, config.n_embd)
        self.drop = nn.Dropout(config.dropout)

        # 초기화: 작은 분산으로 안정적인 학습 시작
        nn.init.normal_(self.token_embedding_table.weight, mean=0.0, std=0.02)
        nn.init.normal_(self.position_embedding_table.weight, mean=0.0, std=0.02)

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        # idx: (B, T)
        b, t = idx.shape
        assert t <= self.config.block_size, \
            f"sequence length {t} exceeds block_size {self.config.block_size}"

        pos = torch.arange(t, device=idx.device)           # (T,)
        tok_emb = self.token_embedding_table(idx)          # (B, T, C)
        pos_emb = self.position_embedding_table(pos)       # (T, C)
        x = self.drop(tok_emb + pos_emb)                  # (B, T, C)

        assert x.shape == (b, t, self.config.n_embd)
        return x

# 검증
config = GPTConfig()
emb_layer = GPTEmbedding(config)
idx = torch.randint(0, config.vocab_size, (4, 8))  # B=4, T=8
out = emb_layer(idx)
print(out.shape)   # torch.Size([4, 8, 128])
```

이 코드가 중요한 이유는 GPT의 모든 나머지 연산이 결국 이 `(B, T, C)` 텐서 위에서 일어나기 때문입니다.

### 첫 미니배치: 입력과 정답 함께 확인

```python
from pathlib import Path

import numpy as np
import torch

def get_batch(split: str, batch_size: int = 4, block_size: int = 64):
    data_path = Path("data") / ("train.bin" if split == "train" else "val.bin")
    data = np.memmap(data_path, dtype=np.uint16, mode="r")
    ix = torch.randint(len(data) - block_size - 1, (batch_size,))
    x = torch.stack([
        torch.from_numpy(np.array(data[int(i): int(i) + block_size], dtype=np.int64))
        for i in ix
    ])
    y = torch.stack([
        torch.from_numpy(
            np.array(data[int(i) + 1: int(i) + block_size + 1], dtype=np.int64)
        )
        for i in ix
    ])
    return x, y

x, y = get_batch("train")
print(f"x.shape: {x.shape}")   # torch.Size([4, 64])
print(f"y.shape: {y.shape}")   # torch.Size([4, 64])
print(f"\nx[0][:20]: {x[0][:20].tolist()}")
print(f"y[0][:20]: {y[0][:20].tolist()}")
# x[0][i]의 다음 토큰이 y[0][i]임을 확인할 수 있음
```

여기서 `x`는 현재 문맥이고 `y`는 한 칸 오른쪽으로 민 정답입니다. 이 한 칸 시프트 구조가 언어 모델 학습의 리듬을 만듭니다.

## 임베딩 메모리 사용량 계산

```python
def embedding_memory_bytes(vocab_size: int, n_embd: int, bytes_per_param: int = 4) -> int:
    return vocab_size * n_embd * bytes_per_param

configs = [
    (65,    128,  "TinyShakespeare char-level"),
    (8000,  256,  "Small BPE"),
    (50000, 768,  "GPT-2"),
    (100000, 4096, "LLaMA-style"),
]

print(f"{'vocab':>10} {'n_embd':>8} {'MB':>10} {'description'}")
print("-" * 55)
for vocab, emb, desc in configs:
    mb = embedding_memory_bytes(vocab, emb) / (1024**2)
    print(f"{vocab:>10,} {emb:>8} {mb:>10.2f} {desc}")
```

예상 출력:

```text
     vocab   n_embd         MB description
-------------------------------------------------------
        65      128       0.03 TinyShakespeare char-level
     8,000      256       7.81 Small BPE
    50,000      768     146.48 GPT-2
   100,000    4,096    1562.50 LLaMA-style
```

char-level은 vocab이 작아서 임베딩 비용이 거의 무시됩니다.

## 임베딩 품질 진단: 학습 초기 vs 후기

```python
import torch.nn.functional as F

def probe_embedding_quality(model, stoi: dict) -> None:
    """학습 중 토큰 임베딩의 유사도 변화를 추적합니다."""
    e = model.token_embedding_table.weight.detach()

    # 문자 쌍 코사인 유사도 계산
    pairs = [
        (" ", "e", "space-e"),
        ("e", "t", "e-t"),
        ("a", "A", "a-A"),
        (".", "\n", "period-newline"),
    ]

    for c1, c2, label in pairs:
        if c1 in stoi and c2 in stoi:
            v1 = e[stoi[c1]]
            v2 = e[stoi[c2]]
            cos = float(F.cosine_similarity(v1[None], v2[None]).item())
            print(f"cos({label}): {cos:.4f}")

# 학습 전 (랜덤): 유사도가 대체로 낮음
# 학습 후: 비슷한 문맥에 나오는 토큰들이 더 가까워짐
```

이 수치 자체가 정답은 아니지만, 학습 전/후 변화를 추적하면 임베딩이 실제로 학습되고 있는지 감각을 얻을 수 있습니다.

## 흔히 나타나는 실패 패턴

### shape 오류: idx.max() >= vocab_size

```python
def forward_with_guard(self, idx: torch.Tensor) -> torch.Tensor:
    b, t = idx.shape

    # 안전 가드
    if idx.max() >= self.config.vocab_size:
        raise ValueError(
            f"idx.max()={idx.max()} >= vocab_size={self.config.vocab_size}. "
            "Check tokenizer/data pipeline."
        )
    if t > self.config.block_size:
        raise ValueError(
            f"sequence length {t} > block_size {self.config.block_size}"
        )

    pos = torch.arange(t, device=idx.device)
    tok_emb = self.token_embedding_table(idx)   # (B, T, C)
    pos_emb = self.position_embedding_table(pos) # (T, C)
    return tok_emb + pos_emb                    # (B, T, C)
```

### 학습 초기 nan 방지

```python
# 임베딩 norm이 너무 크면 첫 어텐션 계산이 불안정해짐
def check_embedding_health(model) -> None:
    tok_norm = model.token_embedding_table.weight.norm(dim=1)
    pos_norm = model.position_embedding_table.weight.norm(dim=1)

    print(f"token emb norm - mean: {tok_norm.mean():.4f}, max: {tok_norm.max():.4f}")
    print(f"pos   emb norm - mean: {pos_norm.mean():.4f}, max: {pos_norm.max():.4f}")

    if tok_norm.max() > 10.0:
        print("[WARNING] Token embedding norm is very large - consider smaller init std")

# 학습 전 점검
check_embedding_health(model)
```

## 운영 체크리스트

- [ ] `(B, T)` 입력이 `(B, T, C)` 임베딩 텐서로 바뀌는 과정을 shape 기준으로 설명할 수 있는가
- [ ] 토큰 임베딩과 위치 임베딩을 왜 분리하는지 한 문장으로 정리할 수 있는가
- [ ] learned positional embedding의 최대 길이가 `block_size`에 묶인다는 점을 이해했는가
- [ ] `get_batch()`에서 `x`와 `y`가 한 칸 시프트된 관계인지 직접 출력으로 확인했는가
- [ ] 임베딩 초기화 std가 0.02 수준인지, norm이 정상 범위인지 점검했는가

## 정리

이번 글에서는 토큰 ID를 의미 있는 벡터 표현으로 바꾸는 임베딩 단계와, 순서를 잃지 않게 해 주는 위치 임베딩 단계를 함께 정리했습니다. 핵심은 `nn.Embedding`을 추상적인 개념보다 학습 가능한 룩업 테이블로 이해하는 데 있습니다.

또한 GPT 입력부가 결국 `token_emb + pos_emb`라는 간결한 구조 위에 서 있다는 점도 확인했습니다. 이 한 줄이 있어야만 이후 어텐션이 토큰 간 관계를 계산할 수 있고, 모델이 순서를 포함한 문맥을 다루기 시작합니다.

다음 글에서는 이제 이 벡터들이 서로를 보게 만듭니다. 즉, 각 토큰이 다른 토큰을 얼마나 참고할지 결정하는 어텐션과 QKV 구조가 본격적으로 등장합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기](./01-tokenizer.md)
- **LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치 (현재 글)**
- LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기 (예정)
- LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위 (예정)
- LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성 (예정)
- LLM from Scratch 101 (6/9): 기울기로 배우기 (예정)
- LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기 (예정)
- LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기 (예정)
- LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Let's build GPT: from scratch, in code, spelled out.](https://www.youtube.com/watch?v=kCc8FmEb1nY)
- [PyTorch nn.Embedding](https://pytorch.org/docs/stable/generated/torch.nn.Embedding.html)

### 관련 시리즈

- [Vector Search 101 — 임베딩이란 무엇인가](../../vector-search-101/ko/01-what-is-embedding.md)
- [LLM 앱 기초 — 토큰 이해하기](../../llm-app-foundations-101/ko/02-understanding-tokens.md)
- [LangChain 101 — Prompt와 LLM Chain](../../langchain-101/ko/02-prompt-llm-chain.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/02-embedding)

Tags: LLM, PyTorch, Transformer, Tutorial
