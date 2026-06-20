---
title: "LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기"
series: llm-from-scratch-101
episode: 7
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
seo_description: 지난 글에서 ckpt.pt를 저장하고 나면 바로 말을 시켜 보고 싶어집니다. 그런데 model.eval()만으로는 문장이 나오지 않습니다.
---

# LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기

학습이 끝나고 `ckpt.pt`까지 저장하면 바로 모델에게 말을 시켜 보고 싶어집니다. 하지만 `model.eval()`만 호출한다고 문장이 저절로 나오지는 않습니다. 학습된 다음 토큰 분포를 실제 문자열로 펼쳐 내는 생성 루프가 따로 필요합니다.

이 글은 LLM from Scratch 101 시리즈의 7번째 글입니다.

생성은 의외로 단순한 반복입니다. 현재 문맥을 모델에 넣고, 마지막 위치의 logits만 꺼내고, 그 분포에서 토큰 하나를 고른 뒤, 그 토큰을 다시 문맥 뒤에 붙입니다. 이 과정을 여러 번 반복하면 텍스트가 한 글자씩 자라납니다.

![LLM from Scratch 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/07/07-01-autoregressive-generation-one-token-at-a.ko.png)
*LLM from Scratch 101 7장 흐름 개요*

## 이 글에서 다룰 문제

- 생성 루프는 정확히 무엇을 반복할까요?
- greedy decoding은 왜 자주 지루하고 반복적인 출력을 만들까요?
- temperature는 logits 분포를 어떻게 바꿀까요?
- top-k와 top-p는 후보군을 어떻게 다르게 자를까요?
- 생성 품질을 숫자로 측정하는 간단한 방법은 무엇일까요?

## 왜 이 글이 중요한가

생성은 학습된 언어 모델을 실제로 체감하게 만드는 첫 단계입니다. 앞선 글들에서 loss를 낮추고 체크포인트를 저장했다면, 여기서는 그 숫자 변화가 실제 텍스트 출력으로 어떻게 나타나는지 확인하게 됩니다.

또한 샘플링은 모델 품질을 해석하는 방식에도 큰 영향을 줍니다. 같은 가중치라도 greedy, top-k, top-p, temperature 설정에 따라 결과의 다양성과 일관성이 크게 달라집니다. 모델이 이상한 것이 아니라 decoding 정책이 그렇게 만든 경우도 많습니다.

## 핵심 관점

생성은 복잡한 문장 작성기라기보다 **다음 토큰 분포를 한 번 계산하고, 그중 하나를 선택해서 다시 입력으로 되먹이는 자기회귀 피드백 루프**입니다.

> 이번 글의 핵심은 간단합니다. 생성은 다음 토큰 분포에서 하나를 뽑고, 그 결과를 다시 입력으로 넣는 자기회귀 루프입니다.

## 자기회귀 생성 루프 다이어그램

```
프롬프트: "ROMEO:"  -> encode -> idx: [30, 27, 25, 27, 27, 16]

루프 1회:
  idx_cond = idx[:, -block_size:]         # 슬라이딩 윈도우
  logits, _ = model(idx_cond)             # (1, T, 65)
  logits = logits[:, -1, :]              # 마지막 위치만 (1, 65)
  logits /= temperature                   # 분포 조절
  [top-k / top-p 필터링]
  probs = softmax(logits)                 # (1, 65)
  next_token = multinomial(probs)         # (1, 1)
  idx = cat([idx, next_token], dim=1)     # 문맥 확장

루프 반복 -> idx가 점점 길어지며 텍스트 생성
```

## 핵심 개념

### Temperature: 분포의 날카로움 조절

```python
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt

logits = torch.tensor([2.5, 1.2, 0.8, -0.5, -1.2])

print(f"{'temp':>8} {'probs (top5)':>50}")
print("-" * 60)
for temp in [0.1, 0.5, 1.0, 2.0, 5.0]:
    probs = F.softmax(logits / temp, dim=-1)
    print(f"{temp:>8.1f} {[f'{p:.3f}' for p in probs.tolist()]}")
```

예상 출력:

```text
    temp                                        probs (top5)
------------------------------------------------------------
     0.1 ['0.999', '0.001', '0.000', '0.000', '0.000']  <- 매우 뾰족
     0.5 ['0.871', '0.111', '0.018', '0.000', '0.000']
     1.0 ['0.606', '0.154', '0.103', '0.028', '0.006']  <- 원래 분포
     2.0 ['0.389', '0.218', '0.189', '0.117', '0.087']  <- 평평해짐
     5.0 ['0.266', '0.228', '0.220', '0.192', '0.162']  <- 거의 균등
```

`T < 1`이면 분포가 더 날카로워져 높은 확률 토큰이 더 유리해지고, `T > 1`이면 분포가 평평해져 무작위성이 커집니다.

### Top-K: 상위 K개만 남기기

```python
def apply_top_k(logits: torch.Tensor, k: int) -> torch.Tensor:
    """상위 k개를 제외한 나머지를 -inf로 마스킹합니다."""
    v, _ = torch.topk(logits, min(k, logits.size(-1)))
    # k번째 값 이하를 -inf로
    logits[logits < v[:, [-1]]] = float("-inf")
    return logits

logits = torch.randn(1, 65)
filtered = apply_top_k(logits.clone(), k=10)
n_valid = (filtered > float("-inf")).sum().item()
print(f"Top-K=10: {n_valid} tokens remaining (out of 65)")
```

### Top-P (Nucleus Sampling): 누적 확률로 자르기

```python
def apply_top_p(logits: torch.Tensor, p: float) -> torch.Tensor:
    """누적 확률 p를 넘을 때까지의 최소 토큰 집합만 남깁니다."""
    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
    cumulative_probs = F.softmax(sorted_logits, dim=-1).cumsum(dim=-1)

    # p를 초과하는 지점 이후를 제거
    # shift: 현재 위치 포함을 위해 한 칸 뒤로
    sorted_indices_to_remove = cumulative_probs > p
    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
    sorted_indices_to_remove[..., 0] = False

    # 원래 순서로 복원
    indices_to_remove = sorted_indices_to_remove.scatter(
        1, sorted_indices, sorted_indices_to_remove
    )
    logits[indices_to_remove] = float("-inf")
    return logits

# 비교 테스트
logits = torch.tensor([[3.0, 2.0, 1.5, 0.5, -1.0, -2.0] + [-5.0] * 59])
probs = F.softmax(logits, dim=-1)
print("Original top-6 probs:", probs[0, :6].tolist())

# top-p=0.9 적용
filtered = apply_top_p(logits.clone(), p=0.9)
valid_mask = filtered > float("-inf")
print(f"Tokens remaining: {valid_mask.sum().item()}")
```

Top-P는 모델이 확신이 큰 경우에는 후보군이 작아지고, 확신이 약한 경우에는 조금 더 넓어집니다. 이 적응성이 top-K보다 자연스러운 텍스트를 만들어 내는 경우가 많습니다.

### 완전한 생성 스크립트: `generate.py`

```python
# generate.py
import argparse

import torch

from data import decode, encode
from model import GPT, GPTConfig

def main() -> None:
    parser = argparse.ArgumentParser(description="GPT text generation")
    parser.add_argument("--prompt",  type=str,   default="ROMEO:")
    parser.add_argument("--max",     type=int,   default=200)
    parser.add_argument("--temp",    type=float, default=0.8)
    parser.add_argument("--top_k",   type=int,   default=20)
    parser.add_argument("--top_p",   type=float, default=0.9)
    parser.add_argument("--ckpt",    type=str,   default="ckpt.pt")
    parser.add_argument("--seed",    type=int,   default=None)
    args = parser.parse_args()

    if args.seed is not None:
        torch.manual_seed(args.seed)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # 체크포인트 로드
    ckpt = torch.load(args.ckpt, map_location=device)
    config = GPTConfig(**ckpt["config"])
    model = GPT(config).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()

    print(f"Loaded: {args.ckpt} ({sum(p.numel() for p in model.parameters()):,} params)")

    # 프롬프트 인코딩
    ids = encode(args.prompt)
    if not ids:
        print("Empty prompt after encoding. Exiting.")
        return

    idx = torch.tensor([ids], dtype=torch.long, device=device)
    print(f"Prompt: '{args.prompt}' ({len(ids)} tokens)")
    print(f"Settings: temp={args.temp}, top_k={args.top_k}, top_p={args.top_p}")
    print(f"\n{'='*40}\n")

    with torch.no_grad():
        out = model.generate(
            idx,
            max_new_tokens=args.max,
            temperature=args.temp,
            top_k=args.top_k,
            top_p=args.top_p,
        )

    print(decode(out[0].tolist()))

if __name__ == "__main__":
    main()
```

사용 예시:

```bash
# 기본 설정
python generate.py --prompt "ROMEO:" --max 200 --temp 0.8 --top_k 20 --top_p 0.9

# Greedy (결정적, 디버깅용)
python generate.py --prompt "ROMEO:" --max 100 --temp 1.0 --top_k 1 --seed 42

# 창의적
python generate.py --prompt "ROMEO:" --max 300 --temp 1.2 --top_p 0.95
```

### 샘플링 정책별 출력 비교

같은 프롬프트와 같은 체크포인트에서 정책만 바꾸면 결과가 어떻게 달라지는지 보는 것이 유용합니다.

```python
# 4가지 설정 비교 스크립트
configs = [
    {"name": "greedy",      "temp": 1.0, "top_k": 1,   "top_p": 1.0},
    {"name": "conservative", "temp": 0.7, "top_k": 10,  "top_p": 1.0},
    {"name": "balanced",    "temp": 0.8, "top_k": 20,  "top_p": 0.9},
    {"name": "creative",    "temp": 1.2, "top_k": None, "top_p": 0.95},
]

prompt = "ROMEO:"
for cfg in configs:
    ids = encode(prompt)
    idx = torch.tensor([ids], dtype=torch.long, device=device)
    with torch.no_grad():
        out = model.generate(
            idx, max_new_tokens=80,
            temperature=cfg["temp"],
            top_k=cfg["top_k"],
            top_p=cfg["top_p"],
        )
    print(f"\n[{cfg['name']}] temp={cfg['temp']}, top_k={cfg['top_k']}, top_p={cfg['top_p']}")
    print(decode(out[0].tolist()))
    print("-" * 40)
```

### 샘플 출력 예시

5000 step 학습 후 `temp=0.8, top_k=20, top_p=0.9` 설정:

```text
ROMEO:
What thou me for the king,
And in thy lord I cry.
Thee no more of men.

JULIET:
But I will not so say,
And yet the world is all.

GLOUCESTER:
I am not so.
```

소형 char-level GPT의 출력은 완성도 높은 문장이 아니라 셰익스피어풍 리듬에 더 가깝습니다. 하지만 리듬과 문자 패턴이 학습 데이터셋의 분위기를 반영한다면 생성 루프는 제대로 작동하고 있는 것입니다.

## 생성 품질 측정

### Distinct-N: 다양성 지표

```python
def distinct_n(text: str, n: int) -> float:
    """n-gram 다양성 비율."""
    if len(text) < n:
        return 0.0
    grams = [text[i: i + n] for i in range(len(text) - n + 1)]
    return len(set(grams)) / max(len(grams), 1)

# 정책별 비교
for cfg in configs:
    # ... (생성 후)
    sample = decode(out[0].tolist())[len(prompt):]
    print(f"{cfg['name']:>12}: distinct-2={distinct_n(sample, 2):.3f}, "
          f"distinct-3={distinct_n(sample, 3):.3f}")
```

예상 출력:

```text
      greedy: distinct-2=0.423, distinct-3=0.612   <- 다양성 낮음
conservative: distinct-2=0.651, distinct-3=0.821
    balanced: distinct-2=0.784, distinct-3=0.912
    creative: distinct-2=0.831, distinct-3=0.947   <- 다양성 높음 (품질은?)
```

### Repetition Penalty 추가

```python
def apply_repetition_penalty(
    logits: torch.Tensor,
    recent_ids: torch.Tensor,
    penalty: float = 1.1,
) -> torch.Tensor:
    """최근 등장한 토큰에 패널티를 부여합니다."""
    for b in range(logits.size(0)):
        for tok in recent_ids[b].tolist():
            if logits[b, tok] > 0:
                logits[b, tok] /= penalty
            else:
                logits[b, tok] *= penalty
    return logits

# generate() 내에서 사용:
# recent = idx[:, -32:]
# logits = apply_repetition_penalty(logits, recent, penalty=1.15)
```

## 디코딩 정책 선택 가이드

| 목적 | 권장 설정 | 이유 |
| --- | --- | --- |
| 재현 가능한 디버깅 | `temp=1.0, top_k=1` | 결정적 출력으로 회귀 비교 용이 |
| 기본 데모 | `temp=0.8, top_k=20, top_p=0.9` | 안정성과 다양성 균형 |
| 창의성 탐색 | `temp=1.1~1.3, top_p=0.95` | 후보 다양성 확장 |
| 안전한 문장 완성 | `temp=0.7, top_k=10` | 과도한 랜덤성 억제 |

## 운영 체크리스트

- [ ] 마지막 위치 logits만 사용해 새 토큰을 뽑는 루프를 설명할 수 있는가
- [ ] greedy, temperature, top-k, top-p를 각각 바꿔 출력 차이를 확인했는가
- [ ] `idx[:, -self.config.block_size:]`가 왜 필요한지 이해했는가
- [ ] `generate.py`에서 체크포인트와 config를 함께 복원하고 있는가
- [ ] distinct-N으로 정책별 다양성 차이를 숫자로 확인했는가

## 정리

이번 글에서는 학습된 GPT를 실제 텍스트 생성기로 바꾸는 자기회귀 샘플링 루프를 구현했습니다. 핵심은 마지막 위치의 logits를 읽고, 그 분포에서 토큰 하나를 뽑아 다시 입력으로 넣는 반복 구조입니다.

또한 temperature, top-k, top-p, sliding context window가 왜 필요한지도 살펴봤습니다. 모델 가중치가 생성의 기반이라면, 샘플링 전략은 그 기반을 어떤 성격의 출력으로 풀어낼지를 결정하는 정책입니다.

다음 글에서는 이 베이스 모델 위에 instruction-response 형식을 덧입히는 파인튜닝을 수행합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치](./02-embedding.md)
- [LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기](./03-attention.md)
- [LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위](./04-transformer-block.md)
- [LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성](./05-gpt-model.md)
- [LLM from Scratch 101 (6/9): 기울기로 배우기](./06-training-loop.md)
- **LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기 (현재 글)**
- LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기 (예정)
- LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [The Curious Case of Neural Text Degeneration (arXiv:1904.09751)](https://arxiv.org/abs/1904.09751)
- [Hierarchical Neural Story Generation (arXiv:1805.04833)](https://arxiv.org/abs/1805.04833)
- [nanoGPT model.py generate (GitHub)](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [How to generate text: using different decoding methods (Hugging Face)](https://huggingface.co/blog/how-to-generate)

### 관련 시리즈

- [LLM 앱 기초 — 스트리밍 응답 처리](../../llm-app-foundations-101/ko/06-streaming-responses.md)
- [LangChain 101 — Streaming](../../langchain-101/ko/05-streaming.md)
- [LLM API 프로덕션 101 — 스트리밍 심화](../../llm-api-production-101/ko/03-streaming-in-depth.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/07-inference)

Tags: LLM, PyTorch, Transformer, Tutorial
