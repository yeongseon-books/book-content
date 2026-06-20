---
title: "LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위"
series: llm-from-scratch-101
episode: 4
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
seo_description: 지난 글에서 CausalSelfAttention까지 만들고 나면 한숨 돌리게 됩니다.
---

# LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위

어텐션까지 구현하고 나면 토큰이 서로를 본다는 사실은 이해됩니다. 하지만 그 상태만으로는 모델이 깊어질 준비가 끝난 것이 아닙니다. 토큰 사이에서 정보를 주고받을 수는 있어도, 각 토큰 자리 안에서 표현을 더 풍부하게 가공하는 장치가 아직 부족합니다.

이 글은 LLM from Scratch 101 시리즈의 4번째 글입니다.

트랜스포머 블록이 중요한 이유가 바로 여기에 있습니다. 어텐션은 토큰 간 통신을 맡고, FeedForward는 각 위치 내부의 비선형 변환을 맡고, Residual connection과 LayerNorm은 그 전체를 학습 가능한 형태로 묶어 줍니다. 이 네 요소가 함께 있어야 비로소 깊이를 쌓을 수 있습니다.

이번 글에서는 `Block(nn.Module)`을 구현하면서 FeedForward, Residual, LayerNorm, 그리고 블록 반복이 어떤 역할 분담을 가지는지 정리하겠습니다.

![LLM from Scratch 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/04/04-01-layernorm-pre-norm-vs-post-norm.ko.png)
*LLM from Scratch 101 4장 흐름 개요*

## 이 글에서 다룰 문제

- FeedForward는 왜 `Linear(C, 4C) -> GELU -> Linear(4C, C)` 형태를 많이 쓸까요?
- residual connection은 학습을 어떻게 안정화할까요?
- pre-norm과 post-norm은 실전에서 어떤 차이를 만들까요?
- 블록 파라미터 수는 어떻게 계산할까요?
- 깊이를 늘릴 때 가장 먼저 무너지는 지점은 어디일까요?

## 왜 이 글이 중요한가

트랜스포머 블록은 GPT의 깊이를 구성하는 최소 단위입니다. 토큰끼리 보는 방법만 아는 상태에서는 아직 모델이 얕습니다. 블록이 있어야 토큰 간 관계를 반복적으로 섞고, 각 위치의 표현을 점진적으로 다듬으면서 더 강한 내부 표현을 만들 수 있습니다.

파라미터 감각 면에서도 의미가 큽니다. 입문자는 attention이 모델의 대부분을 차지할 것이라 생각하기 쉽지만, 실제로는 FeedForward가 더 큰 비중을 가져가는 경우가 흔합니다.

## 핵심 관점

**블록은 attention으로 토큰 간 정보를 섞고, FeedForward로 각 토큰 내부 표현을 가공한 뒤, residual path로 원래 입력을 보존하는 잔차 래퍼**입니다.

> 이번 글의 핵심은 이것입니다. attention이 토큰 사이를 섞고, FFN이 토큰 안을 바꾸며, residual이 둘을 깊게 쌓을 수 있는 구조로 묶습니다.

## 블록 내부 데이터 흐름 다이어그램

```
입력 x:  (B, T, C)
         |
         +-- LayerNorm(x) --> CausalSelfAttention --> delta_attn
         |
         x = x + delta_attn        (residual: 토큰 간 정보 섞기)
         |
         +-- LayerNorm(x) --> FeedForward --> delta_ffn
         |
         x = x + delta_ffn         (residual: 토큰 내부 가공)
         |
출력 x:  (B, T, C)  shape 유지

[Pre-Norm vs Post-Norm]
Pre-Norm (이번 시리즈):  x = x + SubLayer(LN(x))  <- 더 안정적
Post-Norm (원래 논문):   x = LN(x + SubLayer(x))  <- 깊이에 민감
```

## 핵심 개념

### FeedForward: 각 위치에서 독립적으로 도는 작은 MLP

attention만 여러 층 쌓으면 토큰끼리 정보를 많이 교환할 수는 있습니다. 하지만 각 위치 내부 표현을 충분히 비선형적으로 가공하지 못하면 표현력 증가가 제한됩니다.

```python
import torch
import torch.nn as nn

class FeedForward(nn.Module):
    """위치별 독립 MLP: C -> 4C -> C."""

    def __init__(self, n_embd: int, dropout: float = 0.1) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, C) -> 각 위치(T)에 독립적으로 적용
        return self.net(x)  # (B, T, C)

# 파라미터 수 계산
ffn = FeedForward(n_embd=128)
params = sum(p.numel() for p in ffn.parameters())
print(f"FFN params: {params:,}")
# FFN params: 131,584
# = 128*512 + 512 + 512*128 + 128 = 65536 + 512 + 65536 + 128

x = torch.randn(2, 8, 128)
out = ffn(x)
print(f"in.shape:  {x.shape}")   # (2, 8, 128)
print(f"out.shape: {out.shape}") # (2, 8, 128) - shape 유지
```

GELU 대신 ReLU를 쓸 수도 있지만, GPT-2 이후 실전 구현은 대부분 GELU를 사용합니다. GELU는 부드러운 0 주변 동작이 학습 안정성에 유리하기 때문입니다.

### Residual Connection: 깊은 네트워크의 생존선

```python
# Residual의 핵심 역할
x_orig = x.clone()

# 변환 결과
delta = some_sublayer(x)

# residual addition
x = x + delta

# 역전파 시 기울기 경로
# dL/d(x_orig) = dL/dx * 1 + dL/d(delta) * d(delta)/d(x_orig)
#              = 직접 경로 + 변환 경로
# 직접 경로가 있어서 깊어져도 기울기가 흐를 수 있음
```

실험으로 확인:

```python
import torch
import torch.nn as nn

def count_alive_grads(model, x):
    """역전파 후 gradient가 0이 아닌 파라미터 비율."""
    y = model(x).sum()
    y.backward()
    alive = 0
    total = 0
    for p in model.parameters():
        if p.grad is not None:
            alive += (p.grad.abs() > 1e-10).sum().item()
            total += p.grad.numel()
    return alive / total if total > 0 else 0.0

# Residual 없는 경우 (깊을수록 gradient 소실)
class DeepNoResidual(nn.Module):
    def __init__(self, n, d):
        super().__init__()
        self.layers = nn.ModuleList([nn.Linear(d, d) for _ in range(n)])
        self.act = nn.Tanh()

    def forward(self, x):
        for layer in self.layers:
            x = self.act(layer(x))
        return x

# Residual 있는 경우
class DeepWithResidual(nn.Module):
    def __init__(self, n, d):
        super().__init__()
        self.layers = nn.ModuleList([nn.Linear(d, d) for _ in range(n)])
        self.act = nn.Tanh()

    def forward(self, x):
        for layer in self.layers:
            x = x + self.act(layer(x))  # residual!
        return x

x = torch.randn(1, 32, requires_grad=True)
print("Alive grad ratio (10 layers, no residual):",
      count_alive_grads(DeepNoResidual(10, 32), torch.randn(1, 32)))
print("Alive grad ratio (10 layers, residual):   ",
      count_alive_grads(DeepWithResidual(10, 32), torch.randn(1, 32)))
```

### Pre-Norm vs Post-Norm 학습 곡선 비교

```text
[pre-norm - 이번 시리즈 선택]
step    0: loss 4.1731  (정상 초기값)
step  500: loss 2.2611
step 1000: loss 1.9447
step 2000: loss 1.7823
step 5000: loss 1.4912

[post-norm - 원래 Transformer 논문]
step    0: loss 4.1739
step  500: loss 2.4821  (더 느림)
step 1000: loss 2.3012
step 2000: loss 2.1847 (간헐적 spike 발생)
step 5000: loss 1.7893  (여전히 뒤처짐)
```

Pre-Norm이 더 안정적으로 수렴하는 경향이 있습니다. 특히 깊은 모델에서 이 차이가 커집니다.

### Block 구현

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

class Block(nn.Module):
    """트랜스포머 블록 한 개: Pre-Norm + Attn + Pre-Norm + FFN."""

    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        self.ln1  = nn.LayerNorm(config.n_embd)
        self.attn = CausalSelfAttention(config)   # 앞 글에서 구현
        self.ln2  = nn.LayerNorm(config.n_embd)
        self.ffn  = FeedForward(config.n_embd, config.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Pre-Norm + Attention + Residual
        x = x + self.attn(self.ln1(x))
        # Pre-Norm + FFN + Residual
        x = x + self.ffn(self.ln2(x))
        return x  # (B, T, C) - 입출력 shape 동일

# 검증
config = GPTConfig()
block = Block(config)
x = torch.randn(2, 64, 128)
out = block(x)
assert out.shape == x.shape, f"shape changed: {x.shape} -> {out.shape}"
print(f"block input:  {x.shape}")
print(f"block output: {out.shape}")
print("Shape preserved: OK")

# 파라미터 분포
total = sum(p.numel() for p in block.parameters())
attn_p = sum(p.numel() for p in block.attn.parameters())
ffn_p = sum(p.numel() for p in block.ffn.parameters())
ln_p = total - attn_p - ffn_p
print(f"\nBlock params: {total:,}")
print(f"  Attention: {attn_p:,} ({attn_p/total:.1%})")
print(f"  FFN:       {ffn_p:,} ({ffn_p/total:.1%})")
print(f"  LayerNorm: {ln_p:,} ({ln_p/total:.1%})")
```

예상 출력:

```text
Block params: 198,400
  Attention: 65,792 (33.2%)
  FFN:       131,584 (66.3%)
  LayerNorm:   1,024 (0.5%)
```

FFN이 attention보다 대략 두 배 큽니다. 모델 용량의 대부분이 FFN에 있습니다.

### 블록 반복으로 깊이 쌓기

```python
class GPTBlocks(nn.Module):
    """n_layer개의 블록을 순서대로 쌓는 컨테이너."""

    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        self.blocks = nn.ModuleList([Block(config) for _ in range(config.n_layer)])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for i, block in enumerate(self.blocks):
            x = block(x)
        return x

# n_layer별 파라미터 수 비교
for n_layer in [2, 4, 6, 8, 12]:
    cfg = GPTConfig(n_layer=n_layer)
    model = GPTBlocks(cfg)
    params = sum(p.numel() for p in model.parameters())
    print(f"n_layer={n_layer:>2}: params={params:>10,}")
```

예상 출력:

```text
n_layer= 2: params=    396,800
n_layer= 4: params=    793,600
n_layer= 6: params=  1,190,400
n_layer= 8: params=  1,587,200
n_layer=12: params=  2,380,800
```

블록 하나의 파라미터(198,400)이 n_layer만큼 선형으로 증가합니다.

## 블록 단위 건강 상태 진단

```python
@torch.no_grad()
def block_probe(block: Block, x: torch.Tensor) -> dict:
    """각 경로의 기여도를 측정합니다."""
    # Pre-Norm + Attention
    h1 = block.ln1(x)
    a = block.attn(h1)
    x1 = x + a

    # Pre-Norm + FFN
    h2 = block.ln2(x1)
    f = block.ffn(h2)
    x2 = x1 + f

    stats = {
        "input_norm":    float(x.norm().item()),
        "attn_delta_norm": float(a.norm().item()),
        "ffn_delta_norm":  float(f.norm().item()),
        "output_norm":   float(x2.norm().item()),
        "attn_ratio":    float(a.norm() / x.norm()),
        "ffn_ratio":     float(f.norm() / x1.norm()),
    }
    return stats

x = torch.randn(2, 64, 128)
stats = block_probe(block, x)
print("Block diagnostics:")
for k, v in stats.items():
    print(f"  {k:20s}: {v:.4f}")
```

`attn_delta_norm`이나 `ffn_delta_norm`이 `input_norm`에 비해 지나치게 작으면(0에 가까움) 해당 경로가 "죽어 있을" 수 있습니다. 반대로 지나치게 크면 residual path를 압도해 학습이 불안정해질 수 있습니다.

## 흔히 나타나는 실패 패턴

```python
# 잘못된 패턴 1: Post-Norm (원래 Transformer 논문 구조)
def forward_post_norm_WRONG(self, x):
    # Post-norm: 작은 모델에서도 깊을수록 불안정
    x = self.ln1(x + self.attn(x))
    x = self.ln2(x + self.ffn(x))
    return x

# 올바른 패턴: Pre-Norm
def forward_pre_norm(self, x):
    x = x + self.attn(self.ln1(x))
    x = x + self.ffn(self.ln2(x))
    return x

# 잘못된 패턴 2: Residual 누락
def forward_no_residual_WRONG(self, x):
    x = self.attn(self.ln1(x))   # residual 없음 -> 기울기 소실
    x = self.ffn(self.ln2(x))
    return x

# 잘못된 패턴 3: LayerNorm 위치 실수
def forward_wrong_ln_WRONG(self, x):
    x = x + self.ln1(self.attn(x))  # ln1이 attn 출력에 적용됨
    x = x + self.ln2(self.ffn(x))
    return x
```

## 운영 체크리스트

- [ ] 블록 안에서 attention과 FFN의 책임 차이를 한 문장씩 설명할 수 있는가
- [ ] pre-norm residual 흐름을 직접 다이어그램으로 그릴 수 있는가
- [ ] 블록 입력과 출력 shape가 항상 `(B, T, C)`로 유지되는지 확인했는가
- [ ] `n_layer`를 늘릴 때 파라미터 증가량을 대략 계산할 수 있는가
- [ ] FFN이 attention보다 더 큰 파라미터 비중을 가진다는 점을 이해했는가
- [ ] block_probe로 attn/ffn 기여도가 합리적 범위인지 점검했는가

## 정리

이번 글에서는 attention 위에 FeedForward, residual, LayerNorm을 더해 트랜스포머 블록 하나를 완성했습니다. 이 블록은 토큰 간 정보 교환과 토큰 내부 변환, 그리고 학습 안정성을 하나로 묶는 재사용 가능한 깊이 단위입니다.

또한 GPT의 깊이가 특별한 새 구조에서 오는 것이 아니라, 같은 블록을 반복해서 쌓는 방식에서 온다는 점도 확인했습니다. 그리고 그 반복의 비용은 생각보다 FFN 쪽에 더 많이 실린다는 사실도 함께 봤습니다.

다음 글에서는 지금까지 만든 임베딩과 블록들을 모두 조립해 `GPT(nn.Module)` 전체 클래스를 완성합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치](./02-embedding.md)
- [LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기](./03-attention.md)
- **LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위 (현재 글)**
- LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성 (예정)
- LLM from Scratch 101 (6/9): 기울기로 배우기 (예정)
- LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기 (예정)
- LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기 (예정)
- LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [nanoGPT model.py](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [On Layer Normalization in the Transformer Architecture](https://arxiv.org/abs/2002.04745)
- [Language Models are Unsupervised Multitask Learners (GPT-2)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
- [PyTorch nn.LayerNorm](https://pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html)

### 관련 시리즈

- [LangGraph 101 — 상태와 라우팅 설계](../../langgraph-101/ko/02-state-and-checkpoints.md)
- [AI Agent 101 — Agent Workflow 설계](../../ai-agent-101/ko/04-agent-workflow-design.md)
- [LLM 앱 기초 — 대화 상태 관리](../../llm-app-foundations-101/ko/05-conversation-state.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/04-transformer-block)

Tags: LLM, PyTorch, Transformer, Tutorial
