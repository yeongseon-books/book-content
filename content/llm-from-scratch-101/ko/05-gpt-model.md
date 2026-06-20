---
title: "LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성"
series: llm-from-scratch-101
episode: 5
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
seo_description: 앞선 세 편에서 입력부와 어텐션을 만들었고, 지난 글에서는 블록 하나를 세웠습니다. 여기까지 오면 부품은 거의 다 모인 셈입니다.
---

# LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성

지금까지 우리는 토크나이저, 임베딩, 어텐션, 트랜스포머 블록을 차례로 만들었습니다. 이 시점에 오면 흩어져 있던 부품이 거의 다 갖춰집니다. 남은 일은 생각보다 단순합니다. 그 부품들을 하나의 `GPT(nn.Module)` 클래스 안에 질서 있게 조립하는 일입니다.

이 글은 LLM from Scratch 101 시리즈의 5번째 글입니다.

이 단계가 중요한 이유는 구조가 한 번에 보이기 시작하기 때문입니다. 토큰과 위치 임베딩이 입력을 만들고, 여러 블록이 그 표현을 다듬고, 마지막 LayerNorm과 LM head가 다음 토큰 분포를 출력합니다. GPT라는 이름이 크게 들려도, 구현 수준에서는 꽤 직선적인 흐름입니다.

![LLM from Scratch 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/05/05-01-the-forward-pass-at-a-glance.ko.png)
*LLM from Scratch 101 5장 흐름 개요*

## 이 글에서 다룰 문제

- GPT 클래스는 어떤 순서로 부품을 호출할까요?
- token embedding과 LM head를 묶는 weight tying은 왜 유용할까요?
- cross-entropy loss는 왜 한 줄 reshape로 계산할 수 있을까요?
- 초기 loss가 `ln(vocab_size)` 근처여야 하는 이유는 무엇일까요?
- forward 계약을 어떻게 테스트할 수 있을까요?

## 왜 이 글이 중요한가

개별 모듈을 이해하는 것과 완성된 모델 클래스를 조립하는 것은 다른 문제입니다. 앞 단계에서는 attention, FFN, residual을 각각 이해했다면, 여기서는 그 모든 것이 하나의 residual stream 안에서 어떻게 이어지는지 확인해야 합니다.

## 핵심 관점

**GPT 클래스는 새로운 알고리즘이라기보다, 이미 만든 부품들을 올바른 순서로 연결하는 조립 코드**입니다.

> 이번 글의 핵심은 간단합니다. GPT는 임베딩 위에 블록을 쌓고, 마지막 hidden state를 다음 토큰 분포로 읽어 내는 자기회귀 모델입니다.

## GPT Forward Pass 전체 다이어그램

```
입력:  idx (B, T)   int64 토큰 ID
         |
         v
token_emb (B, T, C)  <- nn.Embedding(vocab_size, n_embd)
pos_emb   (T, C)     <- nn.Embedding(block_size, n_embd)
         |
         v
x = token_emb + pos_emb   (B, T, C)   residual stream 시작
         |
         v
Block 0 (x -> x)           (B, T, C)
Block 1 (x -> x)
Block 2 (x -> x)
Block 3 (x -> x)
Block 4 (x -> x)
Block 5 (x -> x)
         |
         v
ln_f  LayerNorm             (B, T, C)
         |
         v
lm_head  Linear(C, V)       (B, T, V)   V = vocab_size
         |
         v
logits (B, T, vocab_size)

[optional: targets 제공 시]
loss = cross_entropy(logits.view(B*T, V), targets.view(B*T))
```

## GPT 클래스 전체 구현

```python
# model.py
from dataclasses import dataclass, asdict
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

@dataclass
class GPTConfig:
    vocab_size: int = 65
    n_layer: int = 6
    n_head: int = 4
    n_embd: int = 128
    block_size: int = 64
    dropout: float = 0.1

class FeedForward(nn.Module):
    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(config.n_embd, 4 * config.n_embd),
            nn.GELU(),
            nn.Linear(4 * config.n_embd, config.n_embd),
            nn.Dropout(config.dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

class CausalSelfAttention(nn.Module):
    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        assert config.n_embd % config.n_head == 0
        self.n_head   = config.n_head
        self.head_size = config.n_embd // config.n_head
        self.n_embd   = config.n_embd
        self.key   = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.query = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.value = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.proj  = nn.Linear(config.n_embd, config.n_embd)
        self.attn_drop = nn.Dropout(config.dropout)
        self.register_buffer(
            "tril",
            torch.tril(torch.ones(config.block_size, config.block_size))
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, t, c = x.shape
        k = self.key(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)
        q = self.query(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)
        v = self.value(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)
        wei = q @ k.transpose(-2, -1) / math.sqrt(self.head_size)
        wei = wei.masked_fill(self.tril[:t, :t] == 0, float("-inf"))
        wei = self.attn_drop(F.softmax(wei, dim=-1))
        out = (wei @ v).transpose(1, 2).contiguous().view(b, t, c)
        return self.proj(out)

class Block(nn.Module):
    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        self.ln1  = nn.LayerNorm(config.n_embd)
        self.attn = CausalSelfAttention(config)
        self.ln2  = nn.LayerNorm(config.n_embd)
        self.ffn  = FeedForward(config)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln1(x))
        x = x + self.ffn(self.ln2(x))
        return x

class GPT(nn.Module):
    """소형 GPT: TinyShakespeare char-level language model."""

    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        self.config = config

        self.token_emb  = nn.Embedding(config.vocab_size, config.n_embd)
        self.pos_emb    = nn.Embedding(config.block_size, config.n_embd)
        self.drop       = nn.Dropout(config.dropout)
        self.blocks     = nn.ModuleList([Block(config) for _ in range(config.n_layer)])
        self.ln_f       = nn.LayerNorm(config.n_embd)
        self.lm_head    = nn.Linear(config.n_embd, config.vocab_size, bias=False)

        # Weight tying: 입력 임베딩과 출력 투영이 같은 파라미터 공유
        self.lm_head.weight = self.token_emb.weight

        # 초기화
        self.apply(self._init_weights)

    def _init_weights(self, module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            nn.init.ones_(module.weight)
            nn.init.zeros_(module.bias)

    def forward(
        self,
        idx: torch.Tensor,
        targets: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        b, t = idx.shape
        if t > self.config.block_size:
            raise ValueError(
                f"cannot forward sequence of length {t}, "
                f"block_size is {self.config.block_size}"
            )

        # 임베딩
        pos = torch.arange(t, device=idx.device)  # (T,)
        tok_emb = self.token_emb(idx)             # (B, T, C)
        pos_emb = self.pos_emb(pos)               # (T, C)
        x = self.drop(tok_emb + pos_emb)          # (B, T, C)

        # 트랜스포머 블록
        for block in self.blocks:
            x = block(x)

        # 최종 LayerNorm + LM head
        x = self.ln_f(x)                          # (B, T, C)
        logits = self.lm_head(x)                  # (B, T, vocab_size)

        # Loss 계산 (학습 시)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(b * t, self.config.vocab_size),
                targets.view(b * t),
            )

        return logits, loss

    def generate(
        self,
        idx: torch.Tensor,
        max_new_tokens: int,
        temperature: float = 1.0,
        top_k: int | None = None,
        top_p: float | None = None,
    ) -> torch.Tensor:
        """자기회귀 생성 루프."""
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.config.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / max(temperature, 1e-5)

            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float("-inf")

            if top_p is not None:
                s_logits, s_idx = torch.sort(logits, descending=True)
                cumprobs = F.softmax(s_logits, dim=-1).cumsum(dim=-1)
                cutoff = cumprobs > top_p
                cutoff[..., 1:] = cutoff[..., :-1].clone()
                cutoff[..., 0] = False
                s_logits[cutoff] = float("-inf")
                logits = torch.full_like(logits, float("-inf")).scatter(1, s_idx, s_logits)

            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)

        return idx
```

## Weight Tying 효과

```python
config = GPTConfig()
model = GPT(config)

# Weight tying 확인: 같은 메모리를 참조하는지 확인
print("Weight shared:", model.lm_head.weight is model.token_emb.weight)

# 파라미터 수 (tying 덕분에 lm_head는 중복 계산 안 됨)
unique_params = {id(p): p for p in model.parameters()}
total = sum(p.numel() for p in unique_params.values())
print(f"Unique params: {total:,}")

# tying 없이 별도 파라미터라면
without_tying = total + config.vocab_size * config.n_embd
print(f"Without tying: {without_tying:,}")
print(f"Savings: {without_tying - total:,} params")
```

예상 출력:

```text
Weight shared: True
Unique params: 1,204,096
Without tying: 1,212,416
Savings: 8,320 params
```

### 모델 구조 리포트

```python
def report_model(model: GPT) -> None:
    """파라미터 분포를 계층별로 출력합니다."""
    total = sum(p.numel() for p in model.parameters())
    emb_params = sum(p.numel() for n, p in model.named_parameters()
                     if "token_emb" in n or "pos_emb" in n)
    block_params = sum(p.numel() for n, p in model.named_parameters()
                       if "blocks" in n)
    head_params = sum(p.numel() for n, p in model.named_parameters()
                      if "ln_f" in n)  # lm_head는 shared이므로 제외

    print(f"{'GPT Model Report':=^40}")
    print(f"vocab_size={model.config.vocab_size}, "
          f"n_layer={model.config.n_layer}, "
          f"n_head={model.config.n_head}, "
          f"n_embd={model.config.n_embd}")
    print(f"{'':=^40}")
    print(f"Total params:  {total:>10,}")
    print(f"Embedding:     {emb_params:>10,}  ({emb_params/total:.2%})")
    print(f"Blocks:        {block_params:>10,}  ({block_params/total:.2%})")
    print(f"Final LN:      {head_params:>10,}  ({head_params/total:.2%})")

report_model(model)
```

## Sanity Check: 초기 Loss 검증

랜덤 초기화된 모델이라면 65개 클래스에 대해 거의 균등한 추측을 해야 하므로, 초기 loss는 대략 `ln(65) ≈ 4.17` 근처가 나와야 합니다.

```python
import math

import torch

config = GPTConfig()
model = GPT(config)

# 랜덤 입력
idx     = torch.randint(0, config.vocab_size, (4, config.block_size))
targets = torch.randint(0, config.vocab_size, (4, config.block_size))

with torch.no_grad():
    logits, loss = model(idx, targets)

expected_loss = math.log(config.vocab_size)
print(f"logits.shape: {logits.shape}")   # (4, 64, 65)
print(f"loss: {loss.item():.4f}")         # ~4.17
print(f"expected (ln({config.vocab_size})): {expected_loss:.4f}")
print(f"difference: {abs(loss.item() - expected_loss):.4f}")

# 0.5 이내면 구현이 대체로 정상
assert abs(loss.item() - expected_loss) < 0.5, \
    f"Initial loss too far from expected! Got {loss.item():.4f}, expected ~{expected_loss:.4f}"
print("Sanity check: PASSED")
```

## Forward 계약 테스트

```python
def test_forward_contract() -> None:
    """GPT forward pass의 입출력 계약을 검증합니다."""
    cfg = GPTConfig(vocab_size=65, block_size=32, n_layer=2, n_head=2, n_embd=32)
    model = GPT(cfg)
    model.eval()

    # 1) targets 없이 호출 -> loss=None
    idx = torch.randint(0, cfg.vocab_size, (3, 16))
    logits, loss = model(idx)
    assert logits.shape == (3, 16, cfg.vocab_size), f"logits shape wrong: {logits.shape}"
    assert loss is None, "loss should be None when targets not provided"

    # 2) targets 있을 때 -> loss가 finite scalar
    tgt = torch.randint(0, cfg.vocab_size, (3, 16))
    logits, loss = model(idx, tgt)
    assert logits.shape == (3, 16, cfg.vocab_size)
    assert loss is not None and torch.isfinite(loss), f"loss is not finite: {loss}"

    # 3) block_size 초과 시 에러
    try:
        long_idx = torch.randint(0, cfg.vocab_size, (1, cfg.block_size + 1))
        model(long_idx)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # 4) generate 출력 길이 검증
    prompt = torch.randint(0, cfg.vocab_size, (1, 5))
    out = model.generate(prompt, max_new_tokens=10)
    assert out.shape == (1, 15), f"generate output shape wrong: {out.shape}"

    print("All forward contract tests: PASSED")

test_forward_contract()
```

## 활성값 흐름 추적

```python
@torch.no_grad()
def trace_activations(model: GPT, idx: torch.Tensor) -> None:
    """각 블록을 거치며 residual stream의 norm 변화를 추적합니다."""
    b, t = idx.shape

    pos = torch.arange(t, device=idx.device)
    x = model.drop(model.token_emb(idx) + model.pos_emb(pos))
    print(f"emb_norm:  {x.norm():.4f}")

    for i, block in enumerate(model.blocks):
        x = block(x)
        print(f"block_{i}_norm: {x.norm():.4f}")

    x = model.ln_f(x)
    print(f"ln_f_norm: {x.norm():.4f}")

idx = torch.randint(0, 65, (1, 32))
trace_activations(model, idx)
```

숫자가 단조 증가하거나 급락하면 초기화, lr, norm 동작을 함께 점검해야 합니다.

## 운영 체크리스트

- [ ] forward 패스를 임베딩 → 블록 반복 → `ln_f` → `lm_head` 순서로 설명할 수 있는가
- [ ] `self.lm_head.weight = self.token_emb.weight`가 하는 일을 이해했는가
- [ ] logits와 targets를 왜 `(B*T, ...)` 형태로 펼치는지 설명할 수 있는가
- [ ] 랜덤 초기화 시 loss가 `ln(vocab_size)` 근처여야 한다는 sanity check를 실행했는가
- [ ] `test_forward_contract()`로 입출력 계약을 자동 검증하는가

## 정리

이번 글에서는 지금까지 만든 부품을 하나의 `GPT(nn.Module)` 클래스 안에 조립했습니다. 입력 임베딩, 블록 반복, 최종 정규화, LM head, optional loss 계산까지 연결되면서 모델은 비로소 완전한 forward 패스를 갖게 되었습니다.

또한 weight tying, flatten 기반 cross-entropy, `GPTConfig` 중앙화, 그리고 sanity check까지 포함한 완전한 구현을 완성했습니다.

이제 다음 글에서는 이 모델에 학습 루프를 붙입니다. 즉, 미니배치를 반복해서 넣고, loss를 계산하고, 역전파와 optimizer step으로 실제로 가중치를 바꾸는 과정을 시작합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치](./02-embedding.md)
- [LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기](./03-attention.md)
- [LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위](./04-transformer-block.md)
- **LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성 (현재 글)**
- LLM from Scratch 101 (6/9): 기울기로 배우기 (예정)
- LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기 (예정)
- LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기 (예정)
- LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [nanoGPT repository](https://github.com/karpathy/nanoGPT)
- [Using the Output Embedding to Improve Language Models](https://arxiv.org/abs/1608.05859)
- [PyTorch cross_entropy](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
- [Language Models are Unsupervised Multitask Learners (GPT-2)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)

### 관련 시리즈

- [LangChain 101 — 실전 체인 조립](../../langchain-101/ko/06-putting-it-together.md)
- [AI Agent 101 — Agent Workflow 설계](../../ai-agent-101/ko/04-agent-workflow-design.md)
- [LLM API 프로덕션 101 — 구조화 출력](../../llm-api-production-101/ko/01-structured-output.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/05-gpt-model)

Tags: LLM, PyTorch, Transformer, Tutorial
