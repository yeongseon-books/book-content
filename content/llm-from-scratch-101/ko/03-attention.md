---
title: "LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기"
series: llm-from-scratch-101
episode: 3
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
last_reviewed: '2026-05-14'
seo_description: 문장을 읽을 때 사람도 모든 단어를 같은 세기로 보지 않습니다. 어텐션도 이와 비슷하게 중요한 토큰을 골라봅니다.
---

# LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기

임베딩까지 구현하고 나면 드디어 토큰이 벡터가 됩니다. 하지만 그다음 바로 드는 질문이 있습니다. 각 토큰은 자기 위치의 벡터만 보고 어떻게 문맥을 이해할 수 있을까요? 문장 안에서 어떤 단어가 중요한지, 어느 앞선 토큰을 참고해야 하는지는 누가 정할까요?

바로 그 지점에서 어텐션이 등장합니다. 사람도 문장을 읽을 때 모든 단어를 같은 강도로 보지 않습니다. 대명사를 보면 앞의 명사를 다시 확인하고, 문장 끝의 동사를 보면 앞선 주어를 잠깐 되짚습니다. 트랜스포머의 어텐션도 이와 비슷하게 각 토큰이 다른 토큰을 얼마나 참고할지 점수를 매깁니다.

이 글은 LLM from Scratch 101 시리즈의 세 번째 글입니다. 여기서는 QKV 투영, score 계산, causal mask, multi-head 재조립까지를 한 번에 연결합니다.

![LLM from Scratch 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/03/03-01-causal-mask.ko.png)
*LLM from Scratch 101 3장 흐름 개요*

> Attention의 핵심은 'Q·K·V'라는 기호가 아니라 '각 토큰이 다른 모든 토큰에서 얼마나 정보를 가져올지 가중치를 만든다'는 한 줄입니다.

## 이 글에서 다룰 문제

- Q, K, V는 왜 같은 입력에서 나오지만 서로 다른 역할을 가질까요?
- 어텐션 점수는 왜 `Q · K^T / sqrt(d)` 형태로 계산할까요?
- causal mask가 없으면 자기회귀 학습에서 정확히 무엇이 망가질까요?
- multi-head attention은 single-head 대비 무엇을 더 할 수 있을까요?
- 어텐션 구현에서 가장 자주 틀리는 지점은 어디일까요?

## 왜 이 글이 중요한가

어텐션은 트랜스포머를 트랜스포머답게 만드는 핵심 구성 요소입니다. 임베딩이 개별 토큰을 벡터로 바꾸는 단계였다면, 어텐션은 그 벡터들이 서로 문맥 관계를 맺게 하는 단계입니다. 여기서부터 모델은 더 이상 독립된 문자 묶음이 아니라 시퀀스로 동작하기 시작합니다.

실제 구현 오류의 상당수는 수학 오해보다 `transpose` 축, mask 범위, `contiguous()` 누락 같은 텐서 조작에서 나옵니다. 그래서 이 글에서는 공식보다도 텐서가 어떻게 흐르는지에 초점을 둡니다.

## 핵심 관점

어텐션을 복잡한 수식 체계로만 보면 입문 단계에서 금방 막힙니다. 더 실용적인 관점은 이것입니다. **어텐션은 각 토큰이 Query로 질문을 던지고, Key와의 유사도로 참고 대상을 고른 뒤, Value에서 실제 내용을 가져오는 동적 룩업 메커니즘**입니다.

자기회귀 모델에서는 여기에 한 가지 규율이 더 붙습니다. 미래 토큰을 보면 안 된다는 사실입니다. 그래서 causal mask가 필수입니다.

## Attention 텐서 흐름 다이어그램

```
입력 x:  (B, T, C)  예: (2, 8, 128)
          |
          +---> Q = x @ Wq  shape: (B, T, C) -> split -> (B, H, T, HS)
          |
          +---> K = x @ Wk  shape: (B, T, C) -> split -> (B, H, T, HS)
          |
          +---> V = x @ Wv  shape: (B, T, C) -> split -> (B, H, T, HS)

여기서 H = n_head = 4, HS = head_size = C/H = 32

score = Q @ K^T / sqrt(HS)   shape: (B, H, T, T)

causal_mask (T x T):
[[1, 0, 0, 0, 0, 0, 0, 0],
 [1, 1, 0, 0, 0, 0, 0, 0],
 [1, 1, 1, 0, 0, 0, 0, 0],
 ...
 [1, 1, 1, 1, 1, 1, 1, 1]]

masked_score: 0 위치는 -inf로 채워 softmax 후 0이 됨

attn_weight = softmax(masked_score, dim=-1)  shape: (B, H, T, T)

out = attn_weight @ V    shape: (B, H, T, HS)
    -> transpose, reshape -> (B, T, C)
    -> proj (C -> C)     -> (B, T, C)
```

## 단계별 구현

### 단계 1: single-head attention으로 점수 행렬 직접 확인

```python
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

class SingleHeadAttention(nn.Module):
    """교육용 single-head causal self-attention."""

    def __init__(self, n_embd: int, head_size: int, block_size: int) -> None:
        super().__init__()
        self.key   = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer(
            "tril", torch.tril(torch.ones(block_size, block_size))
        )

    def forward(self, x: torch.Tensor):
        b, t, c = x.shape
        k = self.key(x)    # (B, T, HS)
        q = self.query(x)  # (B, T, HS)
        v = self.value(x)  # (B, T, HS)

        # score 계산: Q @ K^T / sqrt(d)
        wei = q @ k.transpose(-2, -1) / math.sqrt(k.size(-1))  # (B, T, T)

        # causal mask 적용
        wei = wei.masked_fill(self.tril[:t, :t] == 0, float("-inf"))

        # softmax로 정규화
        wei = F.softmax(wei, dim=-1)  # (B, T, T)

        # Value 집계
        out = wei @ v  # (B, T, HS)
        return out, wei

# 검증
x = torch.randn(2, 4, 8)
head = SingleHeadAttention(n_embd=8, head_size=8, block_size=8)
out, wei = head(x)
print(f"out.shape: {out.shape}")   # torch.Size([2, 4, 8])
print(f"wei.shape: {wei.shape}")   # torch.Size([2, 4, 4])
print(f"\nwei[0] (causal mask 확인):")
print(wei[0].detach())
```

예상 출력:

```text
out.shape: torch.Size([2, 4, 8])
wei.shape: torch.Size([2, 4, 4])

wei[0] (causal mask 확인):
tensor([[1.0000, 0.0000, 0.0000, 0.0000],
        [0.4789, 0.5211, 0.0000, 0.0000],
        [0.3124, 0.2867, 0.4009, 0.0000],
        [0.2201, 0.1956, 0.2711, 0.3132]])
```

첫 행은 자기 자신만 봐야 하고, 두 번째 행은 첫 두 토큰까지만 봐야 합니다. 오른쪽 위 영역이 0이면 causal mask가 제대로 작동합니다.

### 단계 2: mask를 빼면 무엇이 잘못되는지 확인

```python
import math

import torch
import torch.nn.functional as F

q = torch.randn(1, 4, 8)
k = torch.randn(1, 4, 8)
scores = q @ k.transpose(-2, -1) / math.sqrt(k.size(-1))

print("=== mask 없이 ===")
print(F.softmax(scores, dim=-1)[0].detach())
# 미래 토큰에도 확률이 살아있음 -> 학습 시 미래를 훔쳐보게 됨

tril = torch.tril(torch.ones(4, 4))
masked_scores = scores.masked_fill(tril == 0, float("-inf"))

print("\n=== mask 적용 후 ===")
print(F.softmax(masked_scores, dim=-1)[0].detach())
# 미래 위치가 정확히 0이어야 함
```

학습 loss가 비정상적으로 잘 내려가는데 추론이 엉망일 때 가장 먼저 볼 지점도 여기입니다.

### 단계 3: multi-head attention 완성

```python
from dataclasses import dataclass
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

@dataclass
class GPTConfig:
    vocab_size: int = 65
    block_size: int = 64
    n_layer: int = 6
    n_head: int = 4
    n_embd: int = 128
    dropout: float = 0.1

class CausalSelfAttention(nn.Module):
    """Multi-head causal self-attention."""

    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        assert config.n_embd % config.n_head == 0, \
            f"n_embd ({config.n_embd}) must be divisible by n_head ({config.n_head})"

        self.n_head   = config.n_head
        self.head_size = config.n_embd // config.n_head
        self.n_embd   = config.n_embd

        # Q, K, V 투영 (한 번에)
        self.key   = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.query = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.value = nn.Linear(config.n_embd, config.n_embd, bias=False)

        # 출력 투영
        self.proj  = nn.Linear(config.n_embd, config.n_embd)
        self.attn_drop = nn.Dropout(config.dropout)

        # causal mask: 학습 파라미터가 아닌 buffer로 등록
        self.register_buffer(
            "tril",
            torch.tril(torch.ones(config.block_size, config.block_size))
        )

        # 디버깅을 위해 최근 attention map 저장
        self.last_attn: torch.Tensor | None = None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, t, c = x.shape
        assert c == self.n_embd

        # QKV 투영 후 multi-head split
        # (B, T, C) -> (B, T, n_head, head_size) -> (B, n_head, T, head_size)
        k = self.key(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)
        q = self.query(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)
        v = self.value(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)
        # k, q, v: (B, n_head, T, head_size)

        # Scaled dot-product attention
        wei = q @ k.transpose(-2, -1) / math.sqrt(self.head_size)  # (B, H, T, T)
        wei = wei.masked_fill(self.tril[:t, :t] == 0, float("-inf"))
        wei = F.softmax(wei, dim=-1)
        wei = self.attn_drop(wei)
        self.last_attn = wei.detach()  # 디버깅용 저장

        # Value 집계 + head 재조립
        out = wei @ v  # (B, H, T, HS)
        out = out.transpose(1, 2).contiguous().view(b, t, c)  # (B, T, C)
        out = self.proj(out)
        return out

# 검증
config = GPTConfig()
attn = CausalSelfAttention(config)
x = torch.randn(2, 8, config.n_embd)
out = attn(x)
print(f"out.shape:       {out.shape}")        # torch.Size([2, 8, 128])
print(f"last_attn.shape: {attn.last_attn.shape}")  # torch.Size([2, 4, 8, 8])
```

### 단계 4: head별 attention 패턴 분석

```python
def visualize_attention(attn_module: CausalSelfAttention, text: str, encode_fn, decode_fn) -> None:
    """학습 후 특정 입력에 대한 attention 패턴을 시각화합니다."""
    ids = encode_fn(text)
    idx = torch.tensor([ids])

    with torch.no_grad():
        _ = attn_module(torch.randn(1, len(ids), attn_module.n_embd))

    if attn_module.last_attn is None:
        return

    # head 0의 attention map 출력 (T x T)
    h0 = attn_module.last_attn[0, 0]  # (T, T)
    print(f"Head 0 attention (T={len(ids)}):")
    print(f"{'':>4}", end="")
    for ch in text:
        print(f"{ch:>6}", end="")
    print()

    for i, ch_from in enumerate(text):
        print(f"{ch_from:>4}", end="")
        for j in range(len(ids)):
            val = float(h0[i, j].item())
            print(f"{val:>6.3f}", end="")
        print()
```

## attention 계산 비용 분석

```python
def estimate_attn_memory(batch: int, n_head: int, t: int, dtype_bytes: int = 4) -> float:
    """attention score + prob 두 텐서의 대략적인 메모리 비용 (MB)."""
    return 2 * batch * n_head * t * t * dtype_bytes / (1024**2)

print(f"{'T':>6} {'attn MB':>12}")
print("-" * 20)
for t in [64, 128, 256, 512, 1024]:
    mb = estimate_attn_memory(batch=8, n_head=4, t=t)
    print(f"{t:>6} {mb:>12.2f}")
```

예상 출력:

```text
     T      attn MB
--------------------
    64         1.00
   128         4.00
   256        16.00
   512        64.00
  1024       256.00
```

`T`를 두 배로 늘리면 메모리가 네 배로 늘어나는 이유가 여기서 보입니다.

## 흔히 나타나는 실패 패턴과 점검표

| 증상 | 가장 먼저 볼 것 | 흔한 원인 |
| --- | --- | --- |
| 학습 loss는 잘 내려가는데 생성이 엉망 | mask 출력 | 미래 토큰을 보고 학습함 |
| `view` 단계에서 shape 에러 | `transpose` 직후 텐서 연속성 | `contiguous()` 누락 |
| head 수를 늘리자마자 에러 | `n_embd % n_head` | head당 차원 정수 분할 실패 |
| attention map이 전부 비슷함 | `sqrt(d)` 스케일링 누락 | score 과대로 softmax 포화 |
| 메모리 사용량이 급증 | `T x T` attention map 크기 | block_size 과대 설정 |
| step 0부터 nan | mask 범위 또는 초기화 | score가 -inf / inf로 날아감 |

```python
# 어텐션 상태 체크 함수
@torch.no_grad()
def check_attention_health(attn_module: CausalSelfAttention, x: torch.Tensor) -> None:
    out = attn_module(x)

    if attn_module.last_attn is not None:
        wei = attn_module.last_attn

        # 1) causal mask 검증: 상삼각 영역이 0이어야 함
        t = wei.size(-1)
        tril = torch.tril(torch.ones(t, t, device=wei.device))
        upper = wei[..., ~tril.bool()]
        assert upper.abs().max() < 1e-6, f"Causal mask violation! max upper value: {upper.abs().max()}"

        # 2) 각 행의 합이 1인지 검증
        row_sums = wei.sum(dim=-1)
        assert torch.allclose(row_sums, torch.ones_like(row_sums), atol=1e-5), \
            f"Attention weights don't sum to 1: {row_sums}"

        # 3) nan/inf 없는지 검증
        assert not torch.isnan(out).any(), "NaN in attention output"
        assert not torch.isinf(out).any(), "Inf in attention output"

        print("Attention health check: PASSED")
        print(f"  wei min/max: {wei.min():.4f} / {wei.max():.4f}")
        print(f"  out norm: {out.norm():.4f}")

x = torch.randn(2, 8, 128)
check_attention_health(attn, x)
```

## 구현 방식 비교

| 구현 방식 | 장점 | 단점 | 입문 단계 적합성 |
| --- | --- | --- | --- |
| 명시적 `q @ k^T`, `softmax` | 디버깅/학습에 매우 유리 | 최적화 자동 이점 적음 | 매우 높음 |
| `scaled_dot_product_attention` API | 최신 커널 활용 가능 | 내부 동작 가시성 낮음 | 중간 |
| Flash Attention 계열 | 긴 문맥 성능 우수 | 의존성/환경 제약 | 낮음(입문) |

이번 시리즈는 첫 번째 방식을 택합니다. 성능 절대값보다 attention이 어떻게 동작하는지 끝까지 추적하는 것이 목표이기 때문입니다.

## 운영 체크리스트

- [ ] score matrix와 causal mask가 각각 어떤 shape인지 손으로 적어 볼 수 있는가
- [ ] 단일 head의 `wei`를 출력해 오른쪽 위가 막히는지 확인했는가
- [ ] multi-head 분해 후 `(B, n_head, T, head_size)` shape를 추적할 수 있는가
- [ ] `out.transpose(...).contiguous().view(...)`가 왜 필요한지 설명할 수 있는가
- [ ] attention health check 함수로 mask/nan/row-sum을 모두 검증했는가

## 정리

이번 글에서는 어텐션을 각 토큰이 다른 토큰을 동적으로 조회하는 메커니즘으로 정리했습니다. QKV는 같은 입력을 서로 다른 역할로 투영한 결과이고, 점수 계산과 softmax를 통해 각 토큰은 필요한 문맥을 선택적으로 끌어옵니다.

또한 causal mask와 multi-head 구조가 왜 중요한지도 살펴봤습니다. mask는 자기회귀 규칙을 지키게 만들고, multi-head는 서로 다른 관계 패턴을 병렬로 볼 수 있게 합니다.

다음 글에서는 여기에 FeedForward, Residual, LayerNorm을 더해 트랜스포머 블록 하나를 완성합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치](./02-embedding.md)
- **LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기 (현재 글)**
- [LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위](./04-transformer-block.md)
- [LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성](./05-gpt-model.md)
- [LLM from Scratch 101 (6/9): 기울기로 배우기](./06-training-loop.md)
- [LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기](./07-inference.md)
- [LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기](./08-finetuning.md)
- [LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍](./09-chatbot-wrapper.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [nanoGPT model.py](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [PyTorch scaled_dot_product_attention](https://pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)

### 관련 시리즈

- [LangGraph 101 — 상태와 라우팅 설계](../../langgraph-101/ko/02-state-and-checkpoints.md)
- [AI Agent 101 — 컨텍스트 엔지니어링](../../ai-agent-101/ko/02-context-engineering.md)
- [LLM 앱 기초 — 프롬프트 엔지니어링 기초](../../llm-app-foundations-101/ko/03-prompt-engineering-basics.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/03-attention)

Tags: LLM, PyTorch, Transformer, Tutorial
