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

모델 클래스를 완성하고 나면 이제 정말 학습을 시작할 수 있습니다. 이름만 들으면 거대한 제어 시스템이 필요해 보이지만, 실제 PyTorch 코드로 내려오면 학습 루프의 핵심은 놀랄 만큼 짧습니다. 배치를 뽑고, loss를 계산하고, 역전파하고, optimizer가 한 걸음 움직이는 일이 반복될 뿐입니다.

하지만 짧다고 해서 단순한 것은 아닙니다. 학습은 모델을 처음으로 실제 데이터와 맞붙게 만드는 단계라서, 배치 구성, optimizer 선택, 학습률 스케줄링, gradient clipping, 평가 주기, 체크포인트 저장까지 운영 관점의 디테일이 한꺼번에 중요해집니다.

이 글은 LLM from Scratch 101 시리즈의 여섯 번째 글입니다.

![LLM from Scratch 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/06/06-01-the-5-line-core-of-the-training-loop.ko.png)
*LLM from Scratch 101 6장 흐름 개요*

> Training loop는 'forward → loss → backward → step'이라는 네 줄의 무한 반복이고, GPT를 학습시키는 일은 이 네 줄을 안정적으로 수십만 번 도는 일입니다.

## 이 글에서 다룰 문제

- 학습 루프를 움직이는 핵심 다섯 줄은 무엇일까요?
- transformer 학습에서 AdamW는 왜 SGD보다 다루기 쉬울까요?
- warmup과 cosine decay는 학습 안정성에 어떤 도움을 줄까요?
- gradient clipping은 왜 필수 안전장치인가요?
- 학습이 이상할 때 가장 먼저 점검해야 할 것은 무엇일까요?

## 왜 이 글이 중요한가

학습 루프는 모델이 정적인 구조에서 동적인 학습 시스템으로 바뀌는 순간입니다. 앞선 글들에서 만든 임베딩, 어텐션, 블록, GPT 클래스가 모두 여기서 실제 숫자 업데이트로 연결됩니다.

운영 감각 측면에서도 중요합니다. 학습률 스케줄링, gradient clipping, eval 주기, 체크포인트 저장은 모두 "나중에" 넣는 기능이 아니라 처음부터 품질과 디버깅 비용을 좌우하는 요소입니다.

## 핵심 관점

학습은 복잡한 마법이 아니라 **모델이 현재 예측을 내고, 정답과의 차이에서 기울기를 계산하고, 그 기울기 방향으로 가중치를 조금 이동시키는 폐루프**입니다.

## 학습 루프 아키텍처 다이어그램

```
for step in range(max_iters):
    ┌─ get_batch("train") ──────────────────────────┐
    │  data.bin에서 무작위 시작점 선택               │
    │  x: (B, T) int64, y: (B, T) int64 (x를 1 shift)│
    └────────────────────────────────────────────────┘
                    |
                    v
    ┌─ optimizer.zero_grad() ───────────────────────┐
    │  이전 step의 gradient 초기화                   │
    └────────────────────────────────────────────────┘
                    |
                    v
    ┌─ logits, loss = model(x, y) ──────────────────┐
    │  forward: embedding -> blocks -> ln_f -> logits│
    │  loss: cross_entropy(logits, y)                │
    └────────────────────────────────────────────────┘
                    |
                    v
    ┌─ loss.backward() ─────────────────────────────┐
    │  autograd: 역방향으로 gradient 계산            │
    │  각 파라미터의 .grad에 누적                    │
    └────────────────────────────────────────────────┘
                    |
                    v
    ┌─ clip_grad_norm_(model, 1.0) ─────────────────┐
    │  gradient 폭발 방지 안전장치                   │
    └────────────────────────────────────────────────┘
                    |
                    v
    ┌─ optimizer.step() ────────────────────────────┐
    │  AdamW로 파라미터 업데이트                     │
    │  theta -= lr * (m_hat / sqrt(v_hat) + wd*theta)│
    └────────────────────────────────────────────────┘
```

## 핵심 개념

### LR 스케줄: Warmup + Cosine Decay

```python
import math

def get_lr(it: int, learning_rate: float = 3e-4) -> float:
    """Warmup + Cosine decay 학습률 스케줄."""
    warmup_iters   = 100
    lr_decay_iters = 5000
    min_lr = learning_rate * 0.1

    # 1) Warmup: 0 ~ warmup_iters 구간
    if it < warmup_iters:
        return learning_rate * (it + 1) / warmup_iters

    # 2) 최솟값 유지: lr_decay_iters 이후
    if it > lr_decay_iters:
        return min_lr

    # 3) Cosine decay: warmup ~ lr_decay_iters 구간
    decay_ratio = (it - warmup_iters) / (lr_decay_iters - warmup_iters)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return min_lr + coeff * (learning_rate - min_lr)

# 스케줄 곡선 출력
print(f"{'step':>8} {'lr':>12}")
print("-" * 22)
for step in [0, 50, 100, 500, 1000, 2500, 5000]:
    lr = get_lr(step)
    bar = "=" * int(lr / 3e-4 * 30)
    print(f"{step:>8} {lr:>12.6f} {bar}")
```

예상 출력:

```text
    step           lr
----------------------
       0     0.000003
      50     0.000150 ===============
     100     0.000300 ==============================
     500     0.000293 =============================
    1000     0.000270 ===========================
    2500     0.000180 ==================
    5000     0.000030 ===
```

### 완전한 학습 스크립트: `train.py`

```python
# train.py
from dataclasses import asdict
from pathlib import Path
import csv
import math

import numpy as np
import torch

from model import GPT, GPTConfig

# ---- 설정 ----
batch_size    = 32
block_size    = 64
max_iters     = 5000
eval_interval = 500
eval_iters    = 50
learning_rate = 3e-4
weight_decay  = 0.1
betas         = (0.9, 0.95)
grad_clip     = 1.0
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"using device: {device}")

# ---- 모델 ----
config = GPTConfig(block_size=block_size)
model  = GPT(config).to(device)
params = sum(p.numel() for p in model.parameters())
print(f"model params: {params:,}")

# ---- Optimizer ----
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=learning_rate,
    weight_decay=weight_decay,
    betas=betas,
)

# ---- 데이터 ----
train_data = np.memmap(Path("data") / "train.bin", dtype=np.uint16, mode="r")
val_data   = np.memmap(Path("data") / "val.bin",   dtype=np.uint16, mode="r")

def get_batch(split: str):
    data = train_data if split == "train" else val_data
    ix = torch.randint(len(data) - block_size - 1, (batch_size,))
    x = torch.stack([
        torch.from_numpy(np.array(data[i: i + block_size], dtype=np.int64))
        for i in ix.tolist()
    ])
    y = torch.stack([
        torch.from_numpy(np.array(data[i + 1: i + block_size + 1], dtype=np.int64))
        for i in ix.tolist()
    ])
    return x.to(device), y.to(device)

def get_lr(it: int) -> float:
    warmup_iters   = 100
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

# ---- 로그 파일 ----
log_path = Path("train_log.csv")
with open(log_path, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow(["step", "train_loss", "val_loss", "lr", "grad_norm"])

# ---- 학습 루프 ----
for iter_num in range(max_iters + 1):
    # LR 스케줄 적용
    lr = get_lr(iter_num)
    for pg in optimizer.param_groups:
        pg["lr"] = lr

    # 주기적 평가
    if iter_num % eval_interval == 0:
        losses = estimate_loss()
        print(
            f"step {iter_num:>5}: "
            f"train {losses['train']:.4f}, "
            f"val {losses['val']:.4f}, "
            f"lr {lr:.6f}"
        )

    if iter_num == max_iters:
        break

    # 핵심 다섯 줄
    xb, yb = get_batch("train")
    optimizer.zero_grad(set_to_none=True)
    _, loss = model(xb, yb)
    loss.backward()
    grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
    optimizer.step()

    # 로그 기록
    if iter_num % eval_interval == 0:
        with open(log_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                iter_num,
                losses["train"],
                losses["val"],
                lr,
                float(grad_norm),
            ])

# ---- 체크포인트 저장 ----
torch.save(
    {
        "model": model.state_dict(),
        "config": asdict(config),
        "iter_num": max_iters,
        "tokenizer": {"type": "char", "vocab_size": config.vocab_size},
    },
    "ckpt.pt",
)
print("Saved checkpoint: ckpt.pt")
```

### 예상 학습 곡선

```text
step     0: train 4.1731, val 4.1748, lr 0.000003
step   500: train 2.2114, val 2.3457, lr 0.000300
step  1000: train 1.9262, val 2.0410, lr 0.000293
step  1500: train 1.7834, val 1.9012, lr 0.000280
step  2500: train 1.6038, val 1.7489, lr 0.000180
step  3500: train 1.5211, val 1.6934, lr 0.000101
step  5000: train 1.4725, val 1.6182, lr 0.000030
```

4점대에서 시작해 점진적으로 내려가는 패턴이 보여야 합니다.

### Gradient Accumulation: 유효 배치 크기 키우기

```python
# gradient_accumulation.py
accum_steps = 4  # 실제 배치 = batch_size * accum_steps

for iter_num in range(max_iters + 1):
    lr = get_lr(iter_num)
    for pg in optimizer.param_groups:
        pg["lr"] = lr

    optimizer.zero_grad(set_to_none=True)
    total_loss = 0.0

    for micro in range(accum_steps):
        xb, yb = get_batch("train")
        _, loss = model(xb, yb)
        (loss / accum_steps).backward()  # gradient를 accum_steps로 나눔
        total_loss += float(loss.item())

    grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()

    if iter_num % 100 == 0:
        print(
            f"step {iter_num} "
            f"loss {total_loss/accum_steps:.4f} "
            f"grad_norm {float(grad_norm):.3f}"
        )
```

메모리가 작은 환경에서 유효 배치를 키우는 데 실용적입니다.

### 한 배치 Overfit 테스트

```python
# 구현 검증: 한 배치를 200 step 동안 일부러 외우게 만들기
xb, yb = get_batch("train")
test_model = GPT(GPTConfig()).to(device)
test_opt = torch.optim.AdamW(test_model.parameters(), lr=1e-3)

print("Overfit test (should reach ~0.0 loss):")
for step in range(200):
    test_opt.zero_grad(set_to_none=True)
    _, loss = test_model(xb, yb)
    loss.backward()
    test_opt.step()

    if step % 20 == 0:
        print(f"  step {step:>3}: loss {loss.item():.4f}")
```

예상 출력:

```text
Overfit test (should reach ~0.0 loss):
  step   0: loss 4.1498
  step  20: loss 2.7342
  step  40: loss 1.8231
  step  60: loss 1.2104
  step  80: loss 0.7823
  step 100: loss 0.5211
  step 120: loss 0.3392
  step 140: loss 0.2178
  step 160: loss 0.1432
  step 180: loss 0.0974
```

loss가 빠르게 내려가지 않는다면 forward, backward, optimizer 경로 어딘가에 버그가 있는 것입니다.

## 흔히 나타나는 실패 패턴과 점검표

| 증상 | 가장 먼저 볼 것 | 흔한 원인 |
| --- | --- | --- |
| step 0부터 `nan` | lr, mask, logits scale | lr 과대, attention 버그 |
| train/val 둘 다 안 내려감 | `get_batch()`와 target shift | `y` 한 칸 시프트 오류 |
| train만 내려가고 val 정체 | eval interval 출력 | 과적합 또는 데이터 분할 문제 |
| loss가 가끔 크게 튐 | gradient norm 로그 | clipping 부재, 특정 배치 이상치 |
| 재실행 때 결과가 너무 다름 | config/ckpt 저장 | 실험 맥락 누락 |
| 메모리 계속 증가 | `.item()` 없이 loss 누적 | tensor 참조 누수 |

```python
# 학습 상태 자동 진단 함수
def diagnose_training(step: int, loss_val: float, grad_norm_val: float) -> None:
    """학습 로그를 보고 이상 징후를 감지합니다."""
    issues = []

    if math.isnan(loss_val):
        issues.append("CRITICAL: NaN loss detected - check LR, mask, weight init")

    if loss_val > 5.0 and step > 100:
        issues.append(f"WARNING: High loss {loss_val:.4f} after warmup - check batch sampling")

    if grad_norm_val > 10.0:
        issues.append(f"WARNING: Large grad norm {grad_norm_val:.2f} - clipping firing too often")

    if grad_norm_val < 1e-6:
        issues.append(f"WARNING: Near-zero grad norm - model may be stuck")

    if issues:
        for issue in issues:
            print(f"[DIAGNOSE step={step}] {issue}")
```

## GPU 메모리 모니터링

```python
if torch.cuda.is_available() and iter_num % 500 == 0:
    alloc = torch.cuda.memory_allocated() / (1024**2)
    peak  = torch.cuda.max_memory_allocated() / (1024**2)
    print(f"cuda_mem_mb alloc={alloc:.1f} peak={peak:.1f}")
```

예시 출력:

```text
cuda_mem_mb alloc=742.6 peak=911.3
cuda_mem_mb alloc=755.1 peak=928.4
```

peak 값이 step마다 계속 오르면 tensor 참조 누수를 의심해야 합니다.

## 학습 안정성 체크 테이블

| 점검 항목 | 정상 신호 | 경고 신호 |
| --- | --- | --- |
| 초기 loss | `ln(vocab)` 근처(4.17) | 즉시 nan, 비정상 대형값 |
| grad norm | 완만한 변동 (0.1~2.0) | 주기적 폭발(>10) 또는 0 고착 |
| train vs val | 함께 감소 후 완만 | train만 하락, val 정체/상승 |
| lr 스케줄 | warmup 후 완만 하강 | 계단식 급변, 오적용 |
| 메모리 peak | 초기 상승 후 안정 | step 진행과 함께 지속 상승 |

## 운영 체크리스트

- [ ] `zero_grad -> forward -> backward -> clip -> step` 순서를 외우지 않고 설명할 수 있는가
- [ ] `get_lr()` 곡선이 warmup 후 cosine decay로 가는지 직접 출력해 보았는가
- [ ] `estimate_loss()`로 train/val을 함께 기록하도록 만들었는가
- [ ] 한 배치 overfit 테스트로 구현 경로를 검증했는가
- [ ] `ckpt.pt`에 모델 가중치, config, 토크나이저 정보를 함께 저장했는가
- [ ] `train_log.csv`로 loss 곡선을 파일로 남겨 재현 가능한 실험이 되는가

## 정리

이번 글에서는 GPT를 실제로 학습시키는 최소 `train.py`를 구현했습니다. 배치 샘플링, AdamW, 학습률 스케줄링, gradient clipping, 평가 주기, 체크포인트 저장까지 모두 연결되면서 모델은 처음으로 데이터에서 패턴을 배우기 시작합니다.

학습 루프의 본질은 다섯 줄입니다. 나머지는 그 과정을 안정적이고 재현 가능하게 만드는 운영 장치입니다.

이제 다음 글에서는 저장한 `ckpt.pt`를 불러와 생성 루프를 붙입니다. 즉, 지금까지 학습한 가중치를 사용해 실제로 셰익스피어풍 텍스트를 한 글자씩 뽑아내는 단계로 넘어갑니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치](./02-embedding.md)
- [LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기](./03-attention.md)
- [LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위](./04-transformer-block.md)
- [LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성](./05-gpt-model.md)
- **LLM from Scratch 101 (6/9): 기울기로 배우기 (현재 글)**
- [LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기](./07-inference.md)
- [LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기](./08-finetuning.md)
- [LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍](./09-chatbot-wrapper.md)

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
