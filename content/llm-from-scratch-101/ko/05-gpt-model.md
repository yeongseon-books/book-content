---
title: '조립: GPT 모델 클래스 완성'
series: llm-from-scratch-101
episode: 5
language: ko
status: ready
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

# 조립: GPT 모델 클래스 완성

> LLM from Scratch 101 시리즈 (5/9)

앞선 세 편에서 입력부와 어텐션을 만들었고, 지난 글에서는 블록 하나를 세웠습니다. 여기까지 오면 부품은 거의 다 모인 셈입니다. 남은 일은 의외로 담백합니다. 임베딩으로 시작해서 블록을 통과시키고, 마지막 정규화 뒤에 vocab 크기만큼 logits를 뽑으면 됩니다.

저는 처음 이 지점에 왔을 때 오히려 허탈했습니다. GPT라는 이름이 워낙 커서 더 복잡한 무언가가 숨어 있을 줄 알았거든요. 그런데 작은 구현으로 내려오면 구조는 꽤 직선적입니다. 같은 블록을 여러 층 쌓고, 마지막에 다음 문자 분포를 읽는 머리 하나를 얹는 정도입니다.

물론 세부는 있습니다. 입력 길이 검사, loss reshape, weight tying 같은 실무적 장치가 빠지면 코드가 금방 지저분해집니다. 오늘은 그 부분까지 한 번에 정리하겠습니다.

오늘 멘탈 모델은 이 문장으로 충분합니다. **GPT는 임베딩 위에 블록을 쌓고, 마지막 hidden state를 다음 토큰 분포로 바꾸는 자기회귀 모델입니다.**

---

## 전체 forward 패스 한눈에 보기

입력은 `(B, T)` 모양의 토큰 ID입니다. 여기서 토큰 임베딩과 위치 임베딩을 더하고, 블록 여섯 개를 순서대로 지나가게 합니다. 마지막 `ln_f`를 거친 뒤 `lm_head`로 vocab 차원에 투사하면 `(B, T, vocab_size)` logits가 나옵니다.

![전체 forward 패스 한눈에 보기](../../../assets/llm-from-scratch-101/05/05-01-the-forward-pass-at-a-glance.ko.png)
앞에서 만든 부품 이름이 전부 그대로 등장합니다. 그래서 모델 클래스는 새 알고리즘보다 조립 코드에 가깝습니다.

## class GPT(nn.Module) — 80줄짜리 모델

아래 코드면 시리즈용 `model.py`가 거의 완성됩니다. `Block`과 `CausalSelfAttention`은 앞 글 코드 그대로 있다고 두고, 오늘은 `GPTConfig`와 `GPT` 본체를 마무리합니다.

```python
from dataclasses import dataclass

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

class GPT(nn.Module):
    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        self.config = config
        self.token_emb = nn.Embedding(config.vocab_size, config.n_embd)
        self.pos_emb = nn.Embedding(config.block_size, config.n_embd)
        self.blocks = nn.ModuleList([Block(config) for _ in range(config.n_layer)])
        self.ln_f = nn.LayerNorm(config.n_embd)
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)
        self.lm_head.weight = self.token_emb.weight

    def forward(
        self, idx: torch.Tensor, targets: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        b, t = idx.shape
        if t > self.config.block_size:
            raise ValueError(f"cannot forward sequence of length {t}")

        pos = torch.arange(t, device=idx.device)
        tok_emb = self.token_emb(idx)
        pos_emb = self.pos_emb(pos)
        x = tok_emb + pos_emb

        for block in self.blocks:
            x = block(x)

        x = self.ln_f(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(b * t, self.config.vocab_size),
                targets.view(b * t),
            )

        return logits, loss
```

여기까지 오면 모델은 이미 학습 직전입니다. 각 `Block`이 받은 `(B, T, C)` residual stream을 같은 모양으로 다시 넘겨주기 때문에, 임베딩부터 logits까지 조립된 GPT 전체가 일관된 텐서 흐름으로 연결됩니다.

## LM Head는 사실 Embedding 행렬과 묶을 수 있다 (weight tying)

`self.lm_head.weight = self.token_emb.weight` 이 한 줄은 작지만 자주 쓰는 최적화입니다. 입력에서 쓰는 토큰 임베딩 행렬과 출력 분포를 읽는 행렬을 같은 값으로 공유합니다.

감각적으로도 자연스럽습니다. 어떤 문자를 읽기 위해 만든 벡터 공간과, 마지막에 어떤 문자를 낼지 점수 매기는 공간이 아주 멀리 떨어질 이유가 많지 않습니다. Press & Wolf 논문 이후에는 사실상 기본 옵션처럼 자리 잡았습니다. 작은 모델에서는 파라미터도 조금 아끼고, 학습도 더 안정적으로 느껴지는 경우가 많습니다.

## 손실 함수: cross_entropy 한 줄

언어 모델 학습은 결국 "각 위치의 다음 문자를 맞혀라"입니다. logits 모양은 `(B, T, vocab_size)`이고, 정답은 `(B, T)`입니다. `F.cross_entropy`는 클래스 차원이 마지막이 아닌 2차원 입력을 더 좋아하니, 둘 다 `(B*T, ...)`로 펴서 넣습니다.

이 reshape를 한 번 이해해 두면 뒤에서 학습 루프가 아주 담백해집니다. 시퀀스 차원이든 배치 차원이든, 손실 함수 입장에서는 "예측 행 N개와 정답 N개"로만 보면 되기 때문입니다.

## 모델 인스턴스 한 번 만들고 파라미터 카운트

이제 숫자를 한 번 보겠습니다. 우리 설정은 `vocab_size=65`, `n_layer=6`, `n_head=4`, `n_embd=128`, `block_size=64`입니다. 처음 계획서에는 대략 10M이라고 적혀 있었지만, 이 차원에서는 그렇게 크지 않습니다.

weight tying 기준으로 세어 보면 전체 파라미터는 약 1,204,096개입니다. 토큰 임베딩과 위치 임베딩이 1.6만 개 남짓, 블록 여섯 개가 118만 개 정도, 마지막 LayerNorm이 256개입니다. 숫자를 직접 잡아 보면 모델 크기 감각이 훨씬 현실적으로 들어옵니다.

```python
config = GPTConfig()
model = GPT(config)
num_params = sum(p.numel() for p in model.parameters())
print(f"params: {num_params:,}")
```

## sanity check: 학습 전에 한 번 forward

학습을 돌리기 전에는 loss가 대략 `ln(65)` 근처인지 확인해 보면 좋습니다. 클래스가 65개고 아직 아무것도 못 배운 상태라면 무작위 추측과 비슷해야 하기 때문입니다. 자연로그 기준으로 약 4.17입니다.

```python
import torch

config = GPTConfig()
model = GPT(config)
idx = torch.randint(0, config.vocab_size, (4, config.block_size))
targets = torch.randint(0, config.vocab_size, (4, config.block_size))
logits, loss = model(idx, targets)

print(logits.shape)
print(loss.item())
```

loss가 4점대 초반이면 대개 정상입니다. 여기서 갑자기 20이 나오거나 `nan`이 뜨면 블록 연결, reshape, 마스크 범위부터 다시 보는 편이 빠릅니다.

## config dataclass로 하이퍼 정리

작은 예제라도 하이퍼파라미터를 흩어 놓으면 다음 글부터 금방 피곤해집니다. `GPTConfig` dataclass를 둔 이유가 여기 있습니다. 모델 차원, 층 수, head 수, 문맥 길이가 한곳에 모여 있으니 `train.py`, `generate.py`로 넘기기도 쉽습니다.

이번 시리즈의 기본 설정은 꽤 보수적입니다. `n_layer=6`, `n_head=4`, `n_embd=128`, `block_size=64`면 TinyShakespeare를 CPU나 작은 GPU에서도 다뤄 볼 만합니다. 숫자가 작아 보여도 구조는 GPT와 같습니다. 지금 단계에서는 거대한 모델보다 추적 가능한 모델이 더 좋은 스승입니다.

## 다음 글 예고

이제 모델 본체는 끝났습니다. 다음 글에서는 미니배치를 뽑아 와서 `forward → loss → backward → optimizer.step()`으로 이어지는 학습 루프를 붙이겠습니다. TinyShakespeare loss가 4.17 근처에서 1점대로 내려가는 장면을 직접 보게 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [글자를 숫자로 바꾸기](./01-tokenizer.md)
- [정수에서 벡터로, 그리고 위치](./02-embedding.md)
- [어떤 토큰을 얼마나 볼지 스스로 정하기](./03-attention.md)
- [블록 하나, 깊이의 단위](./04-transformer-block.md)
- **조립: GPT 모델 클래스 완성 (현재 글)**
- 기울기로 배우기 (예정)
- 샘플링 — 학습된 모델에서 글 뽑아내기 (예정)
- 베이스 모델을 우리 작업에 맞추기 (예정)
- 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

- [nanoGPT repository](https://github.com/karpathy/nanoGPT)
- [Using the Output Embedding to Improve Language Models](https://arxiv.org/abs/1608.05859)
- [PyTorch cross_entropy](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
- [Language Models are Unsupervised Multitask Learners (GPT-2)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)

Tags: LLM, PyTorch, Transformer, Tutorial
