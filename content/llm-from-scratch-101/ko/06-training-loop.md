---
title: 기울기로 배우기
series: llm-from-scratch-101
episode: 6
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

# 기울기로 배우기

> LLM from Scratch 101 시리즈 (6/9)

모델 클래스를 완성하고 나면 가장 무거워 보이는 단계가 남습니다. 학습입니다. 이름만 들으면 대단한 제어 시스템이 필요할 것 같지만, PyTorch 코드로 내려오면 의외로 짧습니다. 미니배치를 뽑고, loss를 계산하고, 역전파하고, optimizer가 파라미터를 조금 움직입니다. 이 네 박자를 오래 반복할 뿐입니다.

저는 처음 TinyShakespeare를 학습시킬 때 loss 숫자가 아주 천천히 내려가는 장면이 오히려 반가웠습니다. 대규모 모델 데모처럼 번쩍이지는 않지만, "이 모델이 진짜로 다음 글자를 배우고 있구나"라는 감각이 가장 또렷하게 옵니다.

오늘 글에서는 `train.py`를 붙입니다. AdamW, warmup, cosine decay, gradient clipping, 주기적 평가, 체크포인트 저장까지 넣되 코드는 끝까지 짧게 유지하겠습니다.

오늘 멘탈 모델은 이렇습니다. **학습은 좋은 배치를 반복해서 보여 주고, 틀린 만큼 기울기를 흘려 보내고, 그 기울기만큼 가중치를 조금 고치는 일입니다.**

---

<!-- ebook-only:start -->
## 이 장의 위치

이 글은 시리즈 9편 중 6번째 장입니다.
앞 장에서는 **조립: GPT 모델 클래스 완성**을 다뤘습니다.
이 장을 마치면 다음 장에서 **샘플링 — 학습된 모델에서 글 뽑아내기**으로 이어집니다.
<!-- ebook-only:end -->

## 학습 루프 5줄의 구조

학습 루프의 중심은 정말 다섯 줄입니다. `zero_grad()`, `forward`, `backward()`, `clip_grad_norm_`, `step()`이 전부입니다. 나머지는 평가 주기, 로그, 학습률 계산 같은 운영 코드입니다.

![순전파부터 업데이트까지의 학습 단계](../../../assets/llm-from-scratch-101/06/06-01-the-5-line-core-of-the-training-loop.ko.png)
처음에는 `backward()`가 거대한 마법처럼 보입니다. 실제로는 autograd가 그래프를 거꾸로 따라가며 각 파라미터에 `grad`를 채워 줍니다. optimizer는 그 값을 읽어 한 걸음 움직일 뿐입니다.

## AdamW가 SGD보다 잘 되는 이유 — 짧게

char-level GPT 같은 작은 언어 모델은 SGD보다 AdamW가 훨씬 다루기 쉽습니다. 이전 기울기의 방향을 어느 정도 기억하는 모멘텀과, 파라미터별 스케일을 자동으로 조절하는 적응형 분산 추정이 같이 들어 있기 때문입니다.

거기에 weight decay를 업데이트 규칙과 분리해 둔 점도 좋습니다. 임베딩과 선형층이 많은 트랜스포머에서는 이 분리가 학습감에 꽤 영향을 줍니다. 이번 시리즈는 `lr=3e-4`, `weight_decay=0.1`, `betas=(0.9, 0.95)`로 갑니다. 작은 GPT를 굴리기에는 무난한 출발점입니다.

## Learning Rate Warmup + Cosine Decay

학습 초반부터 큰 학습률을 주면 랜덤 초기화 상태에서 파라미터가 너무 거칠게 흔들립니다. 그래서 처음 100 step은 선형으로 천천히 올리고, 그 뒤에는 5000 step까지 cosine 곡선으로 서서히 내립니다.

warmup은 엔진을 차갑게 켠 직후 바로 고속도로에 올리지 않는 감각에 가깝습니다. 뒤쪽 cosine decay는 막판에 보폭을 줄이며 수렴을 돕습니다. ResNet 학습 쪽에서 익숙한 직관인데, 작은 GPT에도 그대로 잘 맞습니다.

```python
import math

def get_lr(it: int, learning_rate: float) -> float:
    warmup_iters = 100
    lr_decay_iters = 5000
    min_lr = learning_rate * 0.1

    if it < warmup_iters:
        return learning_rate * (it + 1) / warmup_iters
    if it > lr_decay_iters:
        return min_lr

    decay_ratio = (it - warmup_iters) / (lr_decay_iters - warmup_iters)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return min_lr + coeff * (learning_rate - min_lr)
```

## Gradient Clipping — 폭발 방지 1줄

역전파는 잘 되다가도 어느 step에서 갑자기 기울기가 커질 수 있습니다. 특히 학습 초반에는 더 그렇습니다. `torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)` 한 줄을 넣어 두면 최악의 폭주를 꽤 잘 막습니다.

clip은 성능 트릭이라기보다 안전장치에 가깝습니다. loss가 갑자기 튀는 날에는 원인이 학습률인지, 데이터 배치인지, 마스크 버그인지 구분하기 어려운데, clipping이 있으면 적어도 기울기 폭발 한 가지는 손쉽게 배제할 수 있습니다.

## eval_interval로 train/val loss 같이 찍기

언어 모델도 훈련 손실만 보면 안심하기 어렵습니다. `eval_interval=500`으로 잡고 train/val loss를 같이 찍어 보면 과적합이나 데이터 버그를 빨리 알아챌 수 있습니다. 평가는 `@torch.no_grad()` 아래에서 짧게 여러 배치를 평균내면 충분합니다.

제가 작은 모델을 볼 때는 절대값보다 방향을 먼저 봅니다. train만 내려가고 val이 멈추면 과적합 쪽이고, 둘 다 안 내려가면 학습률이나 배치 쪽을 의심합니다. 숫자가 말해 주는 패턴이 의외로 분명합니다.

## train.py 전체 실행 — CPU 5분, GPU 1분

이제 학습 스크립트를 한 파일로 묶겠습니다. 앞 글의 `GPT`, 첫 글의 `train.bin`과 `val.bin`이 있다고 두면 그대로 실행 가능합니다.

```python
from dataclasses import asdict
from pathlib import Path
import math

import numpy as np
import torch

from model import GPT, GPTConfig

batch_size = 32
block_size = 64
max_iters = 5000
eval_interval = 500
eval_iters = 50
learning_rate = 3e-4
weight_decay = 0.1
betas = (0.9, 0.95)
device = "cuda" if torch.cuda.is_available() else "cpu"

config = GPTConfig(block_size=block_size)
model = GPT(config).to(device)
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=learning_rate,
    weight_decay=weight_decay,
    betas=betas,
)

train_data = np.memmap(Path("data") / "train.bin", dtype=np.uint16, mode="r")
val_data = np.memmap(Path("data") / "val.bin", dtype=np.uint16, mode="r")

def get_batch(split: str):
    data = train_data if split == "train" else val_data
    ix = torch.randint(len(data) - block_size - 1, (batch_size,))
    x = torch.stack([
        torch.from_numpy(np.array(data[i : i + block_size], dtype=np.int64))
        for i in ix.tolist()
    ])
    y = torch.stack([
        torch.from_numpy(np.array(data[i + 1 : i + block_size + 1], dtype=np.int64))
        for i in ix.tolist()
    ])
    return x.to(device), y.to(device)

def get_lr(it: int) -> float:
    warmup_iters = 100
    lr_decay_iters = 5000
    min_lr = learning_rate * 0.1
    if it < warmup_iters:
        return learning_rate * (it + 1) / warmup_iters
    if it > lr_decay_iters:
        return min_lr
    decay_ratio = (it - warmup_iters) / (lr_decay_iters - warmup_iters)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return min_lr + coeff * (learning_rate - min_lr)

@torch.no_grad()
def estimate_loss() -> dict[str, float]:
    model.eval()
    out = {}
    for split in ["train", "val"]:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            xb, yb = get_batch(split)
            _, loss = model(xb, yb)
            losses[k] = loss.item()
        out[split] = losses.mean().item()
    model.train()
    return out

for iter_num in range(max_iters + 1):
    lr = get_lr(iter_num)
    for param_group in optimizer.param_groups:
        param_group["lr"] = lr

    if iter_num % eval_interval == 0:
        losses = estimate_loss()
        print(
            f"step {iter_num}: train {losses['train']:.4f}, "
            f"val {losses['val']:.4f}, lr {lr:.6f}"
        )

    xb, yb = get_batch("train")
    optimizer.zero_grad(set_to_none=True)
    _, loss = model(xb, yb)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()

torch.save({'model': model.state_dict(), 'config': asdict(config)}, 'ckpt.pt')
```

이 설정이면 TinyShakespeare에서 시작 loss가 보통 4.17 근처이고, 5000 step 즈음에는 1.5 안팎까지 내려갑니다. CPU에서는 몇 분, GPU에서는 1분 남짓이면 경향이 보입니다. 숫자가 이보다 훨씬 안 좋으면 모델 연결이나 배치 코드를 먼저 다시 보는 편이 낫습니다.

## 학습된 모델 저장 — torch.save 한 줄

작은 실험도 체크포인트는 꼭 남겨 두는 편이 좋습니다. 모델 가중치만 저장하지 말고 config도 같이 담아 두면 다음 글의 생성 스크립트에서 그대로 복원할 수 있습니다.

`torch.save({'model': model.state_dict(), 'config': asdict(config)}, 'ckpt.pt')` 이 한 줄이면 충분합니다. 저는 파일을 열어 보기 전부터 "이 모델이 어떤 문맥 길이와 차원으로 학습됐는가"를 잃지 않는 쪽을 선호합니다. 나중에 실험이 두세 개만 쌓여도 그 차이가 큽니다.

## 다음 글 예고

이제 가중치는 학습됐습니다. 다음 글에서는 `ckpt.pt`를 불러와 자기회귀 생성 루프를 붙이겠습니다. `ROMEO:` 같은 프롬프트 하나로 TinyShakespeare 모델이 다음 문자를 어떻게 뽑는지 직접 보게 됩니다.

<!-- blog-only:start -->
다음 글: [샘플링 — 학습된 모델에서 글 뽑아내기](./07-inference.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [글자를 숫자로 바꾸기](./01-tokenizer.md)
- [정수에서 벡터로, 그리고 위치](./02-embedding.md)
- [어떤 토큰을 얼마나 볼지 스스로 정하기](./03-attention.md)
- [블록 하나, 깊이의 단위](./04-transformer-block.md)
- [조립: GPT 모델 클래스 완성](./05-gpt-model.md)
- **기울기로 배우기 (현재 글)**
- 샘플링 — 학습된 모델에서 글 뽑아내기 (예정)
- 베이스 모델을 우리 작업에 맞추기 (예정)
- 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

- [Decoupled Weight Decay Regularization (AdamW)](https://arxiv.org/abs/1711.05101)
- [nanoGPT train.py](https://github.com/karpathy/nanoGPT/blob/master/train.py)
- [How to Train Your ResNet-8: Bag of Tricks](https://myrtle.ai/how-to-train-your-resnet-8-bag-of-tricks/)
- [PyTorch clip_grad_norm_](https://pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html)

Tags: LLM, PyTorch, Transformer, Tutorial
