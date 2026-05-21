---
title: "LLM from Scratch 101 (6/9): 기울기로 배우기"
series: llm-from-scratch-101
episode: 6
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
seo_description: 모델 클래스를 완성하고 나면 가장 무거워 보이는 단계가 남습니다. 학습입니다.
---

# LLM from Scratch 101 (6/9): 기울기로 배우기

이 글은 LLM from Scratch 101 시리즈의 여섯 번째 글입니다.

모델 클래스를 완성하고 나면 이제 정말 학습을 시작할 수 있습니다. 이름만 들으면 거대한 제어 시스템이 필요해 보이지만, 실제 PyTorch 코드로 내려오면 학습 루프의 핵심은 놀랄 만큼 짧습니다. 배치를 뽑고, loss를 계산하고, 역전파하고, optimizer가 한 걸음 움직이는 일이 반복될 뿐입니다.

하지만 짧다고 해서 단순한 것은 아닙니다. 학습은 모델을 처음으로 실제 데이터와 맞붙게 만드는 단계라서, 배치 구성, optimizer 선택, 학습률 스케줄링, gradient clipping, 평가 주기, 체크포인트 저장까지 운영 관점의 디테일이 한꺼번에 중요해집니다.

특히 TinyShakespeare처럼 작은 데이터셋에서는 숫자 변화가 눈에 잘 보입니다. 초기 loss가 4점대에서 시작해 점차 내려가는 과정을 보면, 지금까지 조립한 모델이 실제로 다음 문자를 배우고 있다는 감각이 처음으로 분명해집니다.

이 글은 LLM from Scratch 101 시리즈의 여섯 번째 글입니다. 여기서는 `train.py`를 만들어 AdamW, warmup, cosine decay, gradient clipping, 주기적 평가, 체크포인트 저장까지 포함한 최소 학습 루프를 구현합니다.

![LLM from Scratch 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/06/06-01-the-5-line-core-of-the-training-loop.ko.png)
*LLM from Scratch 101 6장 흐름 개요*

## 먼저 던지는 질문

- 학습 루프를 움직이는 핵심 다섯 줄은 무엇일까요?
- transformer 학습에서 AdamW는 왜 SGD보다 다루기 쉬울까요?
- warmup과 cosine decay는 학습 안정성에 어떤 도움을 줄까요?

## 왜 이 글이 중요한가

학습 루프는 모델이 정적인 구조에서 동적인 학습 시스템으로 바뀌는 순간입니다. 앞선 글들에서 만든 임베딩, 어텐션, 블록, GPT 클래스가 모두 여기서 실제 숫자 업데이트로 연결됩니다. 즉, 이 글은 "구조 이해"에서 "모델 훈련"으로 넘어가는 경계선입니다.

또한 많은 입문자가 학습을 수식 위주로만 이해하다가 실제 코드 흐름을 놓칩니다. 하지만 실전에서 중요한 것은 loss 값이 어떻게 계산되고, gradient가 언제 초기화되고, optimizer가 언제 step을 밟는지를 정확히 아는 것입니다. 작은 루프 하나를 직접 구현해 보면 자동미분과 optimizer가 덜 추상적으로 보입니다.

운영 감각 측면에서도 중요합니다. 학습률 스케줄링, gradient clipping, eval 주기, 체크포인트 저장은 모두 "나중에" 넣는 기능이 아니라 처음부터 품질과 디버깅 비용을 좌우하는 요소입니다. 작은 실험일수록 이런 기본기를 함께 가져가는 편이 훨씬 좋습니다.

## 핵심 관점

학습은 복잡한 마법이 아니라 **모델이 현재 예측을 내고, 정답과의 차이에서 기울기를 계산하고, 그 기울기 방향으로 가중치를 조금 이동시키는 폐루프**입니다. 이 루프가 수천 번 반복되면서 모델의 출력 습관이 천천히 바뀝니다.

핵심은 반복의 품질입니다. 배치가 제대로 뽑혀야 하고, loss가 올바르게 계산되어야 하고, optimizer가 안정적인 크기로 이동해야 합니다. 학습률이 너무 크면 흔들리고, gradient가 폭발하면 수치가 망가지고, 평가를 안 보면 과적합이나 데이터 버그를 놓치게 됩니다.

따라서 학습 루프는 단순한 네 줄짜리 반복문이면서도 동시에 운영 루틴입니다. loss 감소를 관찰하고, 학습률을 조정하고, 체크포인트를 남기고, train/val 지표를 함께 보아야 비로소 재현 가능한 실험이 됩니다.

## 핵심 개념

### 학습 루프의 중심은 다섯 줄입니다

학습 루프를 가장 작게 요약하면 `zero_grad()`, `forward`, `backward()`, `clip_grad_norm_`, `step()`입니다. 나머지는 평가, 로그, 스케줄링, 저장 같은 운영 코드입니다. 즉, 핵심 자체는 매우 짧고 반복적입니다.

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

## 단계별로 학습 스크립트를 붙여 보기

### 단계 1. `train.py` 하나로 학습 전 과정을 묶습니다

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

torch.save({"model": model.state_dict(), "config": asdict(config)}, "ckpt.pt")
```

이 스크립트는 짧지만 꼭 필요한 것이 다 들어 있습니다. 배치 샘플링, lr 스케줄, 주기적 평가, gradient clipping, checkpoint 저장까지 모두 포함되어 있어서 작은 실험을 반복하기에 충분합니다.

### 단계 2. 로그가 어떻게 내려가야 정상인지 먼저 알고 시작합니다

처음 학습을 돌릴 때는 loss의 절대값보다 추세를 보는 편이 좋습니다. 랜덤 초기화 직후에는 대체로 `ln(65)`에 가까운 4.17 근처에서 시작하고, 수백~수천 step 동안 천천히 내려가야 정상입니다.

**Expected output:**

```text
step 0: train 4.1731, val 4.1748, lr 0.000003
step 500: train 2.2114, val 2.3457, lr 0.000300
step 1000: train 1.9262, val 2.0410, lr 0.000293
step 2500: train 1.6038, val 1.7489, lr 0.000180
step 5000: train 1.4725, val 1.6182, lr 0.000030
```

숫자가 정확히 같을 필요는 없지만, 초반 4점대에서 시작해 점진적으로 내려가는 패턴은 비슷해야 합니다. step 0부터 `nan`이 나오거나, 수백 step 동안 거의 움직이지 않는다면 모델 연결이나 배치 샘플링부터 다시 보는 편이 좋습니다.

### 단계 3. train loss만 보면 절반만 본 것입니다

`eval_interval=500`처럼 주기를 두고 train/val loss를 함께 보면 과적합, 배치 버그, 학습률 문제를 훨씬 빨리 감지할 수 있습니다. `@torch.no_grad()` 아래에서 여러 배치 평균을 내면 작은 실험에서는 충분합니다.

숫자를 읽을 때는 절대값보다 추세가 더 중요합니다. train만 내려가고 val이 정체되면 과적합 신호일 수 있고, 둘 다 안 내려가면 lr이나 batching 문제일 가능성이 큽니다. 작은 모델일수록 이런 패턴이 더 명확하게 드러납니다.

### 단계 4. 한 배치만 과적합시키는 빠른 디버그 루프를 따로 둡니다

전체 학습이 이상할 때는 거대한 문제처럼 느껴지지만, 의외로 가장 빠른 검증은 "한 배치를 일부러 외우게 만들 수 있는가"를 보는 것입니다. 아래 작은 루프에서 loss가 빠르게 내려가면 forward, backward, optimizer 경로는 대체로 정상이라고 볼 수 있습니다.

```python
xb, yb = get_batch("train")

for step in range(200):
    optimizer.zero_grad(set_to_none=True)
    _, loss = model(xb, yb)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()

    if step % 20 == 0:
        print(step, loss.item())
```

**Expected output:**

```text
0 4.15
20 2.73
40 1.82
60 1.21
80 0.79
100 0.54
```

이 테스트에서도 loss가 거의 안 떨어진다면, 데이터셋보다 구현 자체를 먼저 의심하는 편이 낫습니다. 특히 target shift, mask, logits flatten 구간을 다시 확인해야 합니다.

### 단계 5. 체크포인트는 실험 맥락까지 함께 저장해야 합니다

학습이 끝나면 가중치만이 아니라 config까지 함께 저장하는 편이 좋습니다. 그래야 다음 글의 생성 스크립트에서 동일한 `block_size`, `n_embd`, `n_layer`로 모델을 정확히 복원할 수 있습니다.

특히 실험이 여러 번 쌓이기 시작하면 "이 가중치는 어떤 설정으로 학습했지?"라는 질문이 자주 생깁니다. `torch.save({'model': ..., 'config': ...}, 'ckpt.pt')`처럼 맥락을 같이 저장하는 습관이 이후 시간을 크게 줄여 줍니다.

## 문제를 빨리 좁히는 점검표

학습은 잘 안 될 때 원인이 여러 층에 흩어져 보입니다. 그래도 초반에는 아래 순서로 보면 대부분 빠르게 좁혀집니다.

| 증상 | 가장 먼저 볼 것 | 흔한 원인 |
| --- | --- | --- |
| step 0부터 `nan` | learning rate, mask, logits scale | lr 과대, attention 버그 |
| train/val 둘 다 안 내려감 | `get_batch()`와 target shift | `y` 한 칸 시프트 오류 |
| train만 내려가고 val 정체 | eval interval 출력 | 과적합 또는 데이터 분할 문제 |
| loss가 가끔 크게 튐 | gradient norm | clipping 부재, 특정 배치 이상치 |
| 재실행 때 결과가 다 너무 다름 | config/ckpt 저장 | 실험 맥락 누락 |

이 표가 중요한 이유는 "학습이 안 된다"를 막연한 감정에서 구체적인 관찰로 바꿔 주기 때문입니다. 소형 모델일수록 한두 개 프린트만으로도 원인이 빨리 드러납니다.

## 실무에서는 이렇게 생각합니다

이번 시리즈의 목표는 최고 성능이 아니라 재현 가능한 최소 학습 루프를 손으로 구현해 보는 데 있습니다. 그래서 mixed precision, gradient accumulation, distributed training 같은 주제는 일부러 뒤로 미룹니다. 먼저 중요한 것은 "학습이 왜 돌아가는지"와 "문제가 났을 때 어디를 봐야 하는지"입니다.

작은 모델에서도 운영 감각은 이미 필요합니다. 예를 들어 CPU에서 5분이 걸리든 GPU에서 1분이 걸리든, 손실 로그와 체크포인트가 없으면 실험은 사실상 재현되지 않습니다. 반대로 지표와 체크포인트가 남아 있으면 작은 실험도 꽤 강한 학습 자산이 됩니다.

## gradient accumulation을 붙여 유효 배치를 키우는 방법

메모리가 작은 환경에서는 batch size를 크게 잡기 어렵습니다. 이때 자주 쓰는 방법이 gradient accumulation입니다. 핵심은 여러 micro-batch의 gradient를 누적한 뒤, 일정 횟수마다 한 번만 optimizer step을 수행하는 것입니다.

```python
accum_steps = 4

for iter_num in range(max_iters + 1):
    lr = get_lr(iter_num)
    for pg in optimizer.param_groups:
        pg["lr"] = lr

    optimizer.zero_grad(set_to_none=True)
    total_loss = 0.0

    for micro in range(accum_steps):
        xb, yb = get_batch("train")
        _, loss = model(xb, yb)
        (loss / accum_steps).backward()
        total_loss += float(loss.item())

    grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()

    if iter_num % 100 == 0:
        print(f"step {iter_num} loss {total_loss/accum_steps:.4f} grad_norm {float(grad_norm):.3f}")
```

이 방식은 실제 batch를 키운 것과 유사한 효과를 내면서 메모리 압박을 줄여 줍니다. 특히 소형 GPU에서 학습 안정성을 높일 때 실용적입니다.

### loss 곡선을 파일로 남기면 회귀를 빨리 잡습니다

```python
import csv

with open("train_log.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["step", "train_loss", "val_loss", "lr", "grad_norm"])

    for iter_num in range(max_iters + 1):
        ...
        if iter_num % eval_interval == 0:
            losses = estimate_loss()
            writer.writerow([iter_num, losses["train"], losses["val"], lr, float(grad_norm)])
            f.flush()
```

이 로그를 남기면 코드 변경 후 곡선을 바로 비교할 수 있습니다. "체감상 좋아 보인다"가 아니라 숫자로 회귀 여부를 판단할 수 있기 때문에 실험 품질이 올라갑니다.

### 메모리 프로파일 출력 예시

GPU 사용 시에는 아래 두 값을 같이 보는 편이 좋습니다.

```python
if torch.cuda.is_available() and iter_num % 500 == 0:
    alloc = torch.cuda.memory_allocated() / (1024**2)
    peak = torch.cuda.max_memory_allocated() / (1024**2)
    print(f"cuda_mem_mb alloc={alloc:.1f} peak={peak:.1f}")
```

예시 출력:

```text
cuda_mem_mb alloc=742.6 peak=911.3
cuda_mem_mb alloc=755.1 peak=928.4
```

peak 값이 step마다 계속 오르면 텐서 참조 누수 가능성을 의심해야 합니다. 반대로 안정적으로 plateau를 이루면 루프가 건강하게 돌아가는 신호입니다.

### 학습 안정성 체크 테이블

| 점검 항목 | 정상 신호 | 경고 신호 |
| --- | --- | --- |
| 초기 loss | `ln(vocab)` 근처 | 즉시 `nan`, 비정상 대형값 |
| grad norm | 완만한 변동 | 주기적 폭발/0 고착 |
| train vs val | 함께 감소 후 완만 | train만 하락, val 정체/상승 |
| lr 스케줄 | warmup 후 완만 하강 | 계단식 급변, 오적용 |
| 메모리 peak | 초기 상승 후 안정 | step 진행과 함께 지속 상승 |

이 표를 기준으로 학습 로그를 읽으면, 모델 문제와 루프 문제를 분리하기가 쉬워집니다.

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
- [ ] 한 배치 overfit 테스트로 구현 경로를 검증했는가
- [ ] `ckpt.pt`에 모델 가중치와 config를 함께 저장했는가

## 학습 루프를 실험 코드에서 운영 코드로 전환하는 기준

학습 루프는 처음에는 짧은 스크립트로 시작하지만, 반복 실험이 쌓이면 운영 코드로 성격이 바뀝니다. 이 전환 지점을 놓치면, 실험은 늘어나는데 결과 비교는 더 어려워지는 역전 현상이 생깁니다.

### 최소 운영 요건

- 실행 설정을 파일로 고정하고 run ID를 부여합니다.
- 학습/검증 손실을 같은 주기로 저장합니다.
- step 단위 체크포인트 정책(최신, 최고 성능)을 분리합니다.
- 중단 후 재개(resume) 경로를 정식 기능으로 둡니다.

### 품질 판단 기준

손실 곡선이 내려간다는 사실만으로는 충분하지 않습니다. 생성 샘플에서 반복 루프, 의미 붕괴, 문장 종료 실패 같은 증상을 함께 봐야 합니다. 작은 모델일수록 수치 지표와 체감 품질의 간극이 커서, 둘을 동시에 모니터링하는 습관이 중요합니다.

## 정리

이번 글에서는 GPT를 실제로 학습시키는 최소 `train.py`를 구현했습니다. 배치 샘플링, AdamW, 학습률 스케줄링, gradient clipping, 평가 주기, 체크포인트 저장까지 모두 연결되면서 모델은 처음으로 데이터에서 패턴을 배우기 시작합니다.

또한 학습 루프의 본질이 그리 복잡하지 않다는 점도 확인했습니다. 핵심은 좋은 배치를 반복적으로 보여 주고, loss를 통해 gradient를 계산하고, optimizer로 그 방향만큼 조금씩 움직이는 일입니다. 나머지는 그 과정을 안정적이고 재현 가능하게 만드는 운영 장치입니다.

이제 다음 글에서는 저장한 `ckpt.pt`를 불러와 생성 루프를 붙입니다. 즉, 지금까지 학습한 가중치를 사용해 실제로 셰익스피어풍 텍스트를 한 글자씩 뽑아내는 단계로 넘어갑니다.

## 처음 질문으로 돌아가기

- **학습 루프를 움직이는 핵심 다섯 줄은 무엇일까요?**
  - 본문의 기준은 기울기로 배우기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **transformer 학습에서 AdamW는 왜 SGD보다 다루기 쉬울까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **warmup과 cosine decay는 학습 안정성에 어떤 도움을 줄까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치](./02-embedding.md)
- [LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기](./03-attention.md)
- [LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위](./04-transformer-block.md)
- [LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성](./05-gpt-model.md)
- **LLM from Scratch 101 (6/9): 기울기로 배우기 (현재 글)**
- LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기 (예정)
- LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기 (예정)
- LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Decoupled Weight Decay Regularization (AdamW)](https://arxiv.org/abs/1711.05101)
- [nanoGPT train.py](https://github.com/karpathy/nanoGPT/blob/master/train.py)
- [PyTorch clip_grad_norm_](https://pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html)
- [PyTorch AdamW](https://pytorch.org/docs/stable/generated/torch.optim.AdamW.html)

### 관련 시리즈

- [LLM API 프로덕션 101 — 재시도와 오류 처리](../../llm-api-production-101/ko/05-retry-and-error-handling.md)
- [AI Agent 101 — Agent 평가](../../ai-agent-101/ko/07-agent-evaluation.md)
- [LangGraph 101 — 상태와 체크포인트](../../langgraph-101/ko/02-state-and-checkpoints.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/06-training-loop)

Tags: LLM, PyTorch, Transformer, Tutorial
