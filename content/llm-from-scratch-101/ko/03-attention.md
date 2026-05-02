---
title: 어떤 토큰을 얼마나 볼지 스스로 정하기
series: llm-from-scratch-101
episode: 3
language: ko
status: code-checked
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- PyTorch
- Transformer
- Tutorial
last_reviewed: '2026-04-29'
---

# 어떤 토큰을 얼마나 볼지 스스로 정하기

> LLM from Scratch 101 시리즈 (3/9)

문장을 읽을 때 사람도 전부를 같은 세기로 보지 않습니다. "그가 그것을 던졌다"라는 문장을 보면 `그것`이 무엇인지 찾으려고 앞 단어를 다시 훑습니다. 주어가 누구인지, 동작이 어디로 향하는지 순간적으로 가중치를 다르게 둡니다. 트랜스포머의 어텐션도 이 감각과 꽤 닮았습니다.

제가 처음 어텐션 구현을 따라 적을 때는 `QKV`라는 약어가 제일 거슬렸습니다. 이름 때문에 어렵게 느껴지지만, 막상 코드를 뜯으면 같은 입력 텐서에 선형층 세 개를 거는 일입니다. 그다음은 점수 계산, 마스크, softmax, 가중합 순서로 흘러갑니다.

오늘은 `model.py`에 `CausalSelfAttention`을 추가합니다. einsum 같은 축약 기법은 잠시 미뤄 두고, `nn.Linear`와 reshape만으로 끝까지 가보겠습니다. 처음 세 편에서 중요한 건 멋보다 추적 가능성입니다.

오늘 멘탈 모델은 이렇습니다. **각 토큰은 Query로 질문하고, Key로 점수를 매기고, Value에서 필요한 정보를 가져옵니다.**

---

## QKV는 그냥 세 개의 선형 변환

입력 `x`가 `(B, T, C)`라면, 어텐션은 여기서 세 가지 사영을 만듭니다. `q = Wq x`, `k = Wk x`, `v = Wv x`입니다. 셋 다 같은 원본을 보지만 역할이 다릅니다. Query는 "나는 지금 뭘 찾고 있나"이고, Key는 "나는 어떤 단서인가"이며, Value는 "실제로 가져갈 내용"입니다.

이름이 거창해도 구현은 단순합니다. 선형층 세 개면 됩니다.

## 점수 계산: Q · K^T / sqrt(d)

토큰이 다른 토큰을 얼마나 볼지 정하려면 점수가 필요합니다. Query와 Key의 내적을 구하면 됩니다. 값이 클수록 잘 맞는다는 뜻입니다. 다만 차원이 커질수록 내적 값도 커지니 `sqrt(d)`로 나눠 분산을 눌러 줍니다.

손으로 4×4 행렬을 써 보면 금방 감이 옵니다. 길이 4인 시퀀스라면 점수 행렬도 4×4입니다. 각 행은 "현재 토큰이 누구를 보는가"를 뜻합니다.

스케일링을 빼면 학습 초반 softmax가 너무 뾰족해지기 쉽습니다. 몇 칸만 거의 1에 가깝고 나머지는 0으로 눌리면, 경사도 한쪽으로 몰립니다. 논문에서 `sqrt(d)`를 넣은 이유가 수학 장식이 아니라 학습 안정성이라는 점을 기억하면 좋습니다.

## Causal Mask — 미래는 못 본다

언어 모델은 다음 토큰 예측기입니다. 그러니 현재 위치가 미래 정답을 미리 보면 안 됩니다. 그래서 상삼각 부분을 마스킹해 미래 칸을 `-inf`로 막습니다.

![현재 토큰과 미래 토큰의 차단 경계](../../../assets/llm-from-scratch-101/03/03-01-causal-mask.ko.png)
이 한 줄이 자기회귀 모델의 규율입니다. 셰익스피어 다음 글자를 맞히는 동안 미래 대사를 훔쳐보지 못하게 막습니다.

## softmax → V 가중합 → 출력

한 헤드짜리 어텐션은 아래 코드면 충분합니다.

```python
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

class SingleHeadAttention(nn.Module):
    def __init__(self, n_embd: int, head_size: int, block_size: int) -> None:
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer("tril", torch.tril(torch.ones(block_size, block_size)))

    def forward(self, x: torch.Tensor):
        _, t, c = x.shape
        k = self.key(x)
        q = self.query(x)
        wei = q @ k.transpose(-2, -1) / math.sqrt(k.size(-1))
        wei = wei.masked_fill(self.tril[:t, :t] == 0, float("-inf"))
        wei = F.softmax(wei, dim=-1)
        v = self.value(x)
        out = wei @ v
        return out, wei

x = torch.randn(2, 4, 8)
head = SingleHeadAttention(n_embd=8, head_size=8, block_size=8)
out, wei = head(x)
print(out.shape)
print(wei[0])
```

출력은 `(B, T, head_size)`이고, `wei`는 각 토큰이 어디를 봤는지 보여 줍니다. 디버깅할 때 저는 이 가중치 행렬을 꼭 한 번 출력해 봅니다.

## Multi-head: 여러 시선을 동시에

한 헤드만 쓰면 관계를 한 종류로만 봅니다. Multi-head는 임베딩 차원을 여러 조각으로 나누고, 각 조각이 다른 관점으로 점수를 매기게 합니다. 어떤 헤드는 가까운 문맥을, 어떤 헤드는 괄호 짝이나 화자 전환을 더 민감하게 볼 수 있습니다.

마지막에는 각 헤드 출력을 이어 붙이고 projection 한 번으로 원래 차원으로 돌립니다. 우리가 쓸 설정은 `n_embd=128`, `n_head=4`라서 head당 32차원입니다.

여기서 head를 늘린다고 무조건 더 똑똑해지는 건 아닙니다. 같은 `n_embd` 안에서 head 수를 늘리면 head당 차원은 줄어듭니다. 작은 모델에서는 병렬 시선을 조금 얻는 대신 각 시선의 표현력이 얇아집니다. 그래서 101 시리즈 기준으로는 4개 정도가 구조를 보기에도 적당합니다.

## einsum 없이 nn.Linear와 reshape만

이제 시리즈용 `CausalSelfAttention`을 붙입니다. 긴 코드처럼 보여도 구조는 앞에서 본 그대로입니다.

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

class CausalSelfAttention(nn.Module):
    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        assert config.n_embd % config.n_head == 0
        self.n_head = config.n_head
        self.head_size = config.n_embd // config.n_head
        self.key = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.query = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.value = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.proj = nn.Linear(config.n_embd, config.n_embd)
        self.register_buffer(
            "tril", torch.tril(torch.ones(config.block_size, config.block_size))
        )

    def forward(self, x: torch.Tensor):
        b, t, c = x.shape
        k = self.key(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)
        q = self.query(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)
        v = self.value(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)

        wei = q @ k.transpose(-2, -1) / math.sqrt(self.head_size)
        wei = wei.masked_fill(self.tril[:t, :t] == 0, float("-inf"))
        wei = F.softmax(wei, dim=-1)

        out = wei @ v
        out = out.transpose(1, 2).contiguous().view(b, t, c)
        out = self.proj(out)
        self.last_attn = wei
        return out

config = GPTConfig()
attn = CausalSelfAttention(config)
x = torch.randn(2, 8, config.n_embd)
out = attn(x)
print(out.shape)
print(attn.last_attn.shape)
```

출력 모양은 `(2, 8, 128)`입니다. 가중치를 보고 싶다면 `attn.last_attn`을 읽으면 되고, 이 예제에서는 모양이 `(2, 4, 8, 8)`로 나옵니다.

## 단일 head 출력 한 번 찍어보기

가중치를 숫자로 직접 보면 causal mask가 잘 들어갔는지 바로 확인할 수 있습니다. 첫 번째 행은 첫 토큰이라 자기 자신만 보고, 두 번째 행은 앞 두 칸만 봅니다. 오른쪽 위가 0으로 막혀 있으면 정상입니다.

이 작은 확인을 건너뛰면 뒤에서 블록을 쌓을 때 어디서 틀렸는지 찾기 어려워집니다. 저는 어텐션 디버깅의 절반이 모양과 마스크 확인이라고 봅니다.

실제로 학습이 이상하게 흔들릴 때 원인은 대단한 수식보다 사소한 텐서 조작인 경우가 많았습니다. transpose 축 하나가 바뀌거나, mask 범위가 `block_size`와 맞지 않거나, reshape 뒤 `contiguous()`를 빼먹는 식입니다. 어텐션은 개념보다 텐서 모양을 정확히 다루는 손끝이 더 중요합니다.

## 다음 글 예고

이제 토큰끼리 서로를 보는 눈은 생겼습니다. 다음 글에서는 여기에 FeedForward, Residual, LayerNorm을 더해 트랜스포머 블록 하나를 완성하겠습니다. 깊이를 쌓는 최소 단위가 등장합니다.

<!-- toc:begin -->
## 시리즈 목차

- [글자를 숫자로 바꾸기](./01-tokenizer.md)
- [정수에서 벡터로, 그리고 위치](./02-embedding.md)
- **어떤 토큰을 얼마나 볼지 스스로 정하기 (현재 글)**
- 블록 하나, 깊이의 단위 (예정)
- 조립: GPT 모델 클래스 완성 (예정)
- 기울기로 배우기 (예정)
- 샘플링 — 학습된 모델에서 글 뽑아내기 (예정)
- 베이스 모델을 우리 작업에 맞추기 (예정)
- 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [nanoGPT model.py](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [PyTorch scaled_dot_product_attention](https://pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)

Tags: LLM, PyTorch, Transformer, Tutorial
