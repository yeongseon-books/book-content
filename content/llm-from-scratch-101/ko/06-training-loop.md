---
title: 기울기로 배우기
series: llm-from-scratch-101
episode: 6
language: ko
status: publish-ready
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
last_reviewed: '2026-05-12'
seo_description: 모델 클래스를 완성하고 나면 가장 무거워 보이는 단계가 남습니다. 학습입니다.
---

# 기울기로 배우기

모델 클래스를 완성하고 나면 이제 정말 학습을 시작할 수 있습니다. 이름만 들으면 거대한 제어 시스템이 필요해 보이지만, 실제 PyTorch 코드로 내려오면 학습 루프의 핵심은 놀랄 만큼 짧습니다. 배치를 뽑고, loss를 계산하고, 역전파하고, optimizer가 한 걸음 움직이는 일이 반복될 뿐입니다.

하지만 짧다고 해서 단순한 것은 아닙니다. 학습은 모델을 처음으로 실제 데이터와 맞붙게 만드는 단계라서, 배치 구성, optimizer 선택, 학습률 스케줄링, gradient clipping, 평가 주기, 체크포인트 저장까지 운영 관점의 디테일이 한꺼번에 중요해집니다.

특히 TinyShakespeare처럼 작은 데이터셋에서는 숫자 변화가 눈에 잘 보입니다. 초기 loss가 4점대에서 시작해 점차 내려가는 과정을 보면, 지금까지 조립한 모델이 실제로 다음 문자를 배우고 있다는 감각이 처음으로 분명해집니다.

이번 글에서는 `train.py`를 만들어 AdamW, warmup, cosine decay, gradient clipping, 주기적 평가, 체크포인트 저장까지 포함한 최소 학습 루프를 구현하겠습니다. 구조는 작지만, GPT 학습의 핵심 리듬은 모두 들어 있습니다.

이 글은 LLM from Scratch 101 시리즈의 여섯 번째 글입니다.

이제 학습 루프를 이해하면 다음 글에서 저장한 체크포인트를 불러와 실제 텍스트 생성을 시작할 수 있습니다.

## 이 글에서 다룰 문제

- 학습 루프를 움직이는 핵심 다섯 줄은 무엇일까요?
- transformer 학습에서 AdamW는 왜 SGD보다 다루기 쉬울까요?
- warmup과 cosine decay는 학습 안정성에 어떤 도움을 줄까요?
- gradient clipping 한 줄은 어떤 종류의 사고를 줄여 줄까요?
- train/val loss를 같이 보는 것이 왜 중요한 운영 습관일까요?

## 왜 이 글이 중요한가

학습 루프는 모델이 정적인 구조에서 동적인 학습 시스템으로 바뀌는 순간입니다. 앞선 글들에서 만든 임베딩, 어텐션, 블록, GPT 클래스가 모두 여기서 실제 숫자 업데이트로 연결됩니다. 즉, 이 글은 "구조 이해"에서 "모델 훈련"으로 넘어가는 경계선입니다.

또한 많은 입문자가 학습을 수식 위주로만 이해하다가 실제 코드 흐름을 놓칩니다. 하지만 실전에서 중요한 것은 loss 값이 어떻게 계산되고, gradient가 언제 초기화되고, optimizer가 언제 step을 밟는지를 정확히 아는 것입니다. 작은 루프 하나를 직접 구현해 보면 자동미분과 optimizer가 덜 추상적으로 보입니다.

운영 감각 측면에서도 중요합니다. 학습률 스케줄링, gradient clipping, eval 주기, 체크포인트 저장은 모두 "나중에" 넣는 기능이 아니라 처음부터 품질과 디버깅 비용을 좌우하는 요소입니다. 작은 실험일수록 이런 기본기를 함께 가져가는 편이 훨씬 좋습니다.

## 학습 루프를 이해하는 가장 좋은 방법: 같은 실수를 반복해서 조금씩 줄여 가는 폐루프로 보는 것입니다

학습은 복잡한 마법이 아니라 **모델이 현재 예측을 내고, 정답과의 차이에서 기울기를 계산하고, 그 기울기 방향으로 가중치를 조금 이동시키는 폐루프**입니다. 이 루프가 수천 번 반복되면서 모델의 출력 습관이 천천히 바뀝니다.

핵심은 반복의 품질입니다. 배치가 제대로 뽑혀야 하고, loss가 올바르게 계산되어야 하고, optimizer가 안정적인 크기로 이동해야 합니다. 학습률이 너무 크면 흔들리고, gradient가 폭발하면 수치가 망가지고, 평가를 안 보면 과적합이나 데이터 버그를 놓치게 됩니다.

따라서 학습 루프는 단순한 네 줄짜리 반복문이면서도 동시에 운영 루틴입니다. loss 감소를 관찰하고, 학습률을 조정하고, 체크포인트를 남기고, train/val 지표를 함께 보아야 비로소 재현 가능한 실험이 됩니다.

> 이번 글의 핵심은 이것입니다. 학습은 좋은 배치를 반복해 보여 주고, 틀린 만큼 기울기를 흘려 보내고, 그 방향으로 가중치를 조금씩 수정하는 과정입니다.

## 핵심 개념

### 학습 루프의 중심은 다섯 줄입니다

학습 루프를 가장 작게 요약하면 `zero_grad()`, `forward`, `backward()`, `clip_grad_norm_`, `step()`입니다. 나머지는 평가, 로그, 스케줄링, 저장 같은 운영 코드입니다. 즉, 핵심 자체는 매우 짧고 반복적입니다.

![순전파에서 업데이트까지 이어지는 학습 루프](../../../assets/llm-from-scratch-101/06/06-01-the-5-line-core-of-the-training-loop.ko.png)

*배치를 뽑고 loss를 계산한 뒤 gradient를 흘려 보내고 optimizer step을 밟는 핵심 루프입니다.*

이 구조를 이해할 때 가장 중요한 점은 `backward()`가 자동미분 그래프를 역방향으로 순회하며 각 파라미터의 `grad`를 채운다는 사실입니다. optimizer는 그 `grad`를 읽고 파라미터를 조금 이동시킵니다. 결국 학습은 gradient를 계산하고 소비하는 반복입니다.

### AdamW는 작은 GPT에서 실용적인 기본값입니다

char-level GPT 같은 소형 언어 모델에서는 SGD보다 AdamW가 훨씬 다루기 쉽습니다. 이전 gradient 방향을 기억하는 momentum 성격과, 파라미터별 업데이트 크기를 자동 조정하는 adaptive scaling이 함께 들어 있기 때문입니다.

또한 weight decay를 update rule과 분리한 점도 중요합니다. 임베딩과 선형층이 많은 트랜스포머에서는 이 분리가 실제 학습 안정성에 도움이 됩니다. 이번 시리즈에서는 `lr=3e-4`, `weight_decay=0.1`, `betas=(0.9, 0.95)`를 기본값으로 사용합니다.

### warmup과 cosine decay는 시작과 끝을 부드럽게 만듭니다

랜덤 초기화 직후에 큰 학습률을 바로 적용하면 파라미터가 과하게 흔들릴 수 있습니다. 그래서 초반 100 step 동안은 learning rate를 선형으로 올리고, 이후 5000 step까지는 cosine 곡선으로 천천히 낮춥니다.

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

warmup은 엔진을 예열하는 단계, cosine decay는 끝으로 갈수록 보폭을 줄이는 단계라고 생각하면 이해하기 쉽습니다. 작은 모델에서도 이런 스케줄은 loss 곡선을 훨씬 덜 거칠게 만들어 줍니다.

### gradient clipping은 간단하지만 강한 안전장치입니다

학습이 전반적으로 정상이어도 특정 step에서 gradient가 갑자기 커질 수 있습니다. 초반에는 특히 이런 스파이크가 자주 나옵니다. `torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)` 한 줄은 이런 수치적 사고가 전체 학습을 망치지 않게 해 줍니다.

clipping은 성능 트릭이라기보다 안전장치에 가깝습니다. loss가 갑자기 튈 때 원인이 학습률인지, 배치인지, mask 버그인지 빠르게 분리하는 데도 도움이 됩니다.

### train loss만 보면 절반만 본 것입니다

`eval_interval=500`처럼 주기를 두고 train/val loss를 함께 보면 과적합, 배치 버그, 학습률 문제를 훨씬 빨리 감지할 수 있습니다. `@torch.no_grad()` 아래에서 여러 배치 평균을 내면 작은 실험에서는 충분합니다.

숫자를 읽을 때는 절대값보다 추세가 더 중요합니다. train만 내려가고 val이 정체되면 과적합 신호일 수 있고, 둘 다 안 내려가면 lr이나 batching 문제일 가능성이 큽니다. 작은 모델일수록 이런 패턴이 더 명확하게 드러납니다.

### `train.py` 하나로 학습 전 과정을 묶을 수 있습니다

이제 전체 학습 스크립트를 하나로 정리합니다. 이 코드는 앞선 글에서 만든 `GPT` 클래스와 `train.bin`/`val.bin`을 전제로 합니다.

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

이 스크립트는 짧지만 꼭 필요한 것이 다 들어 있습니다. 배치 샘플링, lr 스케줄, 주기적 평가, gradient clipping, checkpoint 저장까지 모두 포함되어 있어서 작은 실험을 반복하기에 충분합니다.

### 체크포인트는 실험 맥락까지 함께 저장해야 합니다

학습이 끝나면 가중치만이 아니라 config까지 함께 저장하는 편이 좋습니다. 그래야 다음 글의 생성 스크립트에서 동일한 `block_size`, `n_embd`, `n_layer`로 모델을 정확히 복원할 수 있습니다.

특히 실험이 여러 번 쌓이기 시작하면 "이 가중치는 어떤 설정으로 학습했지?"라는 질문이 자주 생깁니다. `torch.save({'model': ..., 'config': ...}, 'ckpt.pt')`처럼 맥락을 같이 저장하는 습관이 이후 시간을 크게 줄여 줍니다.

## 흔히 헷갈리는 지점

- 학습 루프가 길고 복잡해야 한다고 생각하기 쉽지만, 핵심은 다섯 줄입니다.
- SGD도 되니 AdamW 선택이 사소하다고 느끼기 쉽지만, 소형 transformer에서는 AdamW가 훨씬 다루기 쉽습니다.
- warmup과 decay를 선택적 장식처럼 보지만, 초기 흔들림과 후반 수렴에 직접 영향을 줍니다.
- train loss만 내려가면 괜찮다고 보기 쉽지만, val loss를 함께 보지 않으면 과적합과 데이터 버그를 놓칩니다.
- checkpoint를 가중치만 저장해도 충분하다고 생각하기 쉽지만, config가 없으면 복원과 재현이 어려워집니다.

## 운영 체크리스트

- [ ] `zero_grad -> forward -> backward -> clip -> step` 순서를 외우지 않고 설명할 수 있는가
- [ ] `get_lr()` 곡선이 warmup 후 cosine decay로 가는지 직접 출력해 보았는가
- [ ] `estimate_loss()`로 train/val을 함께 기록하도록 만들었는가
- [ ] gradient clipping을 적용해 수치 폭주를 완화했는가
- [ ] `ckpt.pt`에 모델 가중치와 config를 함께 저장했는가

## 정리

이번 글에서는 GPT를 실제로 학습시키는 최소 `train.py`를 구현했습니다. 배치 샘플링, AdamW, 학습률 스케줄링, gradient clipping, 평가 주기, 체크포인트 저장까지 모두 연결되면서 모델은 처음으로 데이터에서 패턴을 배우기 시작합니다.

또한 학습 루프의 본질이 그리 복잡하지 않다는 점도 확인했습니다. 핵심은 좋은 배치를 반복적으로 보여 주고, loss를 통해 gradient를 계산하고, optimizer로 그 방향만큼 조금씩 움직이는 일입니다. 나머지는 그 과정을 안정적이고 재현 가능하게 만드는 운영 장치입니다.

이제 다음 글에서는 저장한 `ckpt.pt`를 불러와 생성 루프를 붙입니다. 즉, 지금까지 학습한 가중치를 사용해 실제로 셰익스피어풍 텍스트를 한 글자씩 뽑아내는 단계로 넘어갑니다.

<!-- toc:begin -->
## LLM from Scratch 101 시리즈

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

### 공식 문서

- [Decoupled Weight Decay Regularization (AdamW)](https://arxiv.org/abs/1711.05101)
- [nanoGPT train.py](https://github.com/karpathy/nanoGPT/blob/master/train.py)
- [How to Train Your ResNet-8: Bag of Tricks](https://myrtle.ai/how-to-train-your-resnet-8-bag-of-tricks/)
- [PyTorch clip_grad_norm_](https://pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html)

### 관련 시리즈

- [LLM API 프로덕션 101 — 재시도와 오류 처리](../../llm-api-production-101/ko/05-retry-and-error-handling.md)
- [AI Agent 101 — Agent 평가](../../ai-agent-101/ko/07-agent-evaluation.md)
- [LangGraph 101 — 상태와 체크포인트](../../langgraph-101/ko/02-state-and-checkpoints.md)

Tags: LLM, PyTorch, Transformer, Tutorial
