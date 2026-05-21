---
title: "LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치"
series: llm-from-scratch-101
episode: 2
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
seo_description: 토크나이저까지 만들고 나면 잠깐 멍해집니다. 이제 입력은 숫자니까 끝난 것 같지만, 사실 아직 시작도 아닙니다.
---

# LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치

토크나이저를 만들고 나면 흔히 이런 착각이 듭니다. 이제 텍스트를 숫자로 바꿨으니 모델이 곧바로 이해할 수 있을 것 같다는 생각입니다. 하지만 정수 ID 배열만으로는 신경망이 아무 의미도 읽어 내지 못합니다.

`12, 4, 38, 2` 같은 숫자열은 아직 인덱스 목록일 뿐입니다. 12번 토큰이 13번 토큰과 비슷한지, 셰익스피어 문체에서 어떤 역할을 하는지는 이 숫자만으로는 알 수 없습니다. 의미는 임베딩 테이블 안에서 학습된 벡터를 통해 비로소 생깁니다.

여기서 한 가지가 더 필요합니다. 토큰이 무엇인지만 알아서는 충분하지 않습니다. 같은 `a`라도 문장 첫머리에 있는지 끝부분에 있는지에 따라 역할이 다르고, 모델은 그 순서 감각까지 받아야 합니다. 그래서 토큰 임베딩과 위치 임베딩이 함께 등장합니다.

이번 글에서는 `nn.Embedding`을 거창한 수학 객체가 아니라 룩업 테이블로 이해하고, 토큰 의미와 위치 정보를 더해 `(B, T, C)` 입력 텐서를 만드는 과정을 `model.py` 수준에서 정리하겠습니다.

이 글은 LLM from Scratch 101 시리즈의 두 번째 글입니다.

이제 숫자 ID를 실제 표현 벡터로 바꾸는 입구를 이해하면, 다음 글의 어텐션도 훨씬 자연스럽게 이어집니다.

## 먼저 던지는 질문

- `nn.Embedding`은 실제로 어떤 연산을 수행할까요?
- 토큰 임베딩만으로는 왜 충분하지 않을까요?
- 위치 정보는 왜 별도 임베딩으로 다루는 편이 실용적일까요?

## 큰 그림

![LLM from Scratch 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/02/02-01-sinusoidal-vs-learned-positional-embeddi.ko.png)

*LLM from Scratch 101 2장 흐름 개요*

## 왜 이 글이 중요한가

임베딩은 LLM 내부 표현의 첫 번째 관문입니다. 토크나이저가 텍스트를 숫자로 잘랐다면, 임베딩은 그 숫자를 모델이 다룰 수 있는 연속 벡터 공간으로 올려 보냅니다. 이 단계가 없으면 뒤에 있는 선형층과 어텐션은 아무 의미 있는 구조도 학습할 수 없습니다.

또한 임베딩은 생각보다 많은 오해를 부르는 주제입니다. 입문 단계에서는 벡터 공간 설명이 너무 추상적으로 들리기 쉽고, 반대로 구현 수준에서는 `nn.Embedding`이 단순한 인덱싱이라는 사실이 잘 드러나지 않습니다. 둘 사이를 연결하지 못하면 개념과 코드가 분리됩니다.

실전 감각에서도 중요합니다. 임베딩 차원, 위치 임베딩 방식, 컨텍스트 길이는 모두 메모리 사용량과 학습 안정성에 직접 연결됩니다. 특히 작은 GPT를 직접 구현하는 시리즈에서는 텐서 shape 감각을 여기서 확실히 잡아 두는 것이 이후 블록 구현과 디버깅을 크게 단순하게 만듭니다.

## 핵심 관점

임베딩을 처음 배울 때 가장 실용적인 관점은 이것입니다. **임베딩은 토큰 ID를 받아 해당 행 벡터를 꺼내 오는 룩업 테이블**입니다. 여기에 위치별 벡터를 담은 또 하나의 테이블을 더하면, 모델은 "무슨 토큰인가"와 "몇 번째 위치인가"를 동시에 입력으로 받게 됩니다.

이 관점의 장점은 구현과 개념이 곧바로 연결된다는 데 있습니다. `nn.Embedding(vocab_size, n_embd)`는 거대한 표이고, `idx`가 들어오면 그 표에서 해당 행을 뽑습니다. 거기에 `position_embedding_table`에서 같은 길이만큼의 위치 행을 뽑아 더하면 입력 준비가 끝납니다.

복잡한 설명보다 이 덧셈 하나가 더 중요합니다. 토큰 의미와 위치 정보를 분리해서 학습한 뒤 합친다는 설계 덕분에, 모델은 동일한 토큰을 여러 위치에서 재사용하면서도 순서를 잃지 않을 수 있습니다.

> 이번 글의 핵심 문장은 간단합니다. 모델이 읽는 첫 입력 벡터는 `token_emb + pos_emb`입니다.

## 핵심 개념

### `nn.Embedding`은 학습 가능한 룩업 테이블입니다

`nn.Embedding(vocab_size, n_embd)`는 `(vocab_size, n_embd)` 크기의 학습 가능한 행렬입니다. 입력 토큰 ID가 들어오면 그 ID에 해당하는 행을 가져옵니다. 즉, 선형대수 관점에서는 의미가 풍부하지만 구현 관점에서는 놀랄 만큼 단순한 인덱싱입니다.

핵심은 이 테이블의 값이 학습으로 바뀐다는 사실입니다. 처음에는 랜덤한 숫자지만, 비슷한 문맥에 반복적으로 등장하는 토큰은 점점 비슷한 방향의 벡터를 갖게 됩니다. 의미는 정수 ID가 아니라 그 정수에 대응하는 행 벡터에 축적됩니다.

### 손으로 구현하면 추상성이 크게 줄어듭니다

직접 구현한 `MiniEmbedding`을 보면 `nn.Embedding`의 본질이 더 분명해집니다. 필요한 것은 파라미터 행렬 하나와, 입력 ID로 해당 행을 선택하는 한 줄뿐입니다.

```python
import torch
import torch.nn as nn

class MiniEmbedding(nn.Module):
    def __init__(self, vocab_size: int, n_embd: int) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.randn(vocab_size, n_embd) * 0.02)

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        return self.weight[idx]

idx = torch.tensor([[0, 1, 2], [2, 1, 0]])
emb = MiniEmbedding(vocab_size=4, n_embd=3)
print(emb(idx).shape)
```

출력 shape가 `(2, 3, 3)`이라면 이미 중요한 구조를 이해한 것입니다. 배치 크기 2, 시퀀스 길이 3, 임베딩 차원 3이라는 의미가 한 줄로 드러납니다. 이후 모든 트랜스포머 모듈은 이 shape 감각 위에서 움직입니다.

### 토큰 의미만으로는 순서를 잃어버립니다

토큰 임베딩만 있다면 모델은 어떤 토큰이 들어왔는지는 알 수 있어도, 그 토큰이 시퀀스의 몇 번째 위치에 놓였는지는 알 수 없습니다. 같은 `a`가 첫 글자에 있는지 마지막 글자에 있는지는 언어 모델에 매우 중요하므로, 위치 정보가 반드시 별도로 주어져야 합니다.

이 분리는 구현상으로도 유리합니다. 토큰 의미는 전체 데이터셋에서 재사용되는 전역 정보이고, 위치 감각은 컨텍스트 길이에 따라 달라지는 구조적 정보입니다. 두 정보를 अलग-अलग 테이블로 관리하면 디버깅과 실험이 쉬워집니다.

### 위치 임베딩은 함수형과 학습형으로 나눠 생각할 수 있습니다

원래 Transformer 논문은 사인·코사인 기반의 sinusoidal positional encoding을 사용했습니다. 좌표를 함수로 생성하기 때문에 더 긴 길이로 일반화하기 쉽다는 장점이 있습니다. 반면 많은 GPT 계열 모델은 learned positional embedding을 사용합니다. 이번 시리즈도 구현 단순성과 가시성을 위해 learned 방식을 택합니다.

실전에서는 어느 방식이든 trade-off가 있습니다. 하지만 입문 단계에서는 learned positional embedding이 코드 흐름을 가장 직접적으로 보여 줍니다. 위치별로 학습 가능한 행을 하나씩 뽑아 토큰 벡터에 더하면 되기 때문입니다.

### GPT 입력부의 핵심은 `token_emb + pos_emb` 한 줄입니다

이제 `model.py`의 최소 골격을 만들어 보겠습니다. 여기서는 아직 블록과 logits는 만들지 않고, 오직 임베딩 단계만 구현합니다.

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

class GPT(nn.Module):
    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        self.config = config
        self.token_embedding_table = nn.Embedding(config.vocab_size, config.n_embd)
        self.position_embedding_table = nn.Embedding(config.block_size, config.n_embd)

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        b, t = idx.shape
        pos = torch.arange(t, device=idx.device)
        tok_emb = self.token_embedding_table(idx)
        pos_emb = self.position_embedding_table(pos)
        x = tok_emb + pos_emb
        return x

config = GPTConfig()
model = GPT(config)
idx = torch.randint(0, config.vocab_size, (4, 8))
print(model(idx).shape)
```

이 코드가 중요한 이유는 GPT의 모든 나머지 연산이 결국 이 `(B, T, C)` 텐서 위에서 일어나기 때문입니다. `tok_emb`는 `(B, T, C)`이고 `pos_emb`는 `(T, C)`인데, PyTorch는 브로드캐스팅으로 배치 차원을 자동 확장해 둘을 더합니다. 이 shape 감각을 여기서 확실히 익혀 두는 것이 좋습니다.

### 첫 미니배치를 만들어 입력과 정답을 함께 확인합니다

입력 임베딩을 실제로 보려면 숫자 시퀀스를 배치로 뽑는 함수도 필요합니다. 이전 글에서 만든 `train.bin`을 그대로 읽어 오면 됩니다.

```python
from pathlib import Path

import numpy as np
import torch

def get_batch(split: str, batch_size: int = 4, block_size: int = 8):
    data_path = Path("data") / ("train.bin" if split == "train" else "val.bin")
    data = np.memmap(data_path, dtype=np.uint16, mode="r")
    ix = torch.randint(len(data) - block_size - 1, (batch_size,))
    x = torch.stack([
        torch.from_numpy(np.array(data[int(i) : int(i) + block_size], dtype=np.int64))
        for i in ix
    ])
    y = torch.stack([
        torch.from_numpy(
            np.array(data[int(i) + 1 : int(i) + block_size + 1], dtype=np.int64)
        )
        for i in ix
    ])
    return x, y

x, y = get_batch("train")
print(x.shape, y.shape)
print(x[0])
print(y[0])
```

여기서 `x`는 현재 문맥이고 `y`는 한 칸 오른쪽으로 민 정답입니다. 이 한 칸 시프트 구조가 언어 모델 학습의 리듬을 만듭니다. 즉, 입력은 현재까지의 문맥이고 목표는 각 위치의 다음 토큰입니다.

## 흔히 헷갈리는 지점

- 임베딩을 의미가 이미 담긴 사전처럼 생각하기 쉽지만, 처음에는 랜덤 파라미터일 뿐이고 학습으로 의미가 형성됩니다.
- 토큰 임베딩만 있으면 된다고 느끼기 쉽지만, 위치 정보가 없으면 순서를 복원할 수 없습니다.
- `nn.Embedding`을 복잡한 레이어로 여기기 쉽지만, 구현 핵심은 파라미터 테이블 인덱싱입니다.
- sinusoidal이 더 이론적이니 learned positional embedding이 열등하다고 보기 쉽지만, GPT 계열에서는 학습형이 널리 쓰입니다.
- `x`와 `y`를 별도 텐서로 만드는 이유를 놓치기 쉽지만, next-token prediction에서는 한 칸 시프트가 핵심 계약입니다.

## 운영 체크리스트

- [ ] `(B, T)` 입력이 `(B, T, C)` 임베딩 텐서로 바뀌는 과정을 shape 기준으로 설명할 수 있는가
- [ ] 토큰 임베딩과 위치 임베딩을 왜 분리하는지 한 문장으로 정리할 수 있는가
- [ ] learned positional embedding의 최대 길이가 `block_size`에 묶인다는 점을 이해했는가
- [ ] `get_batch()`에서 `x`와 `y`가 한 칸 시프트된 관계인지 직접 출력으로 확인했는가
- [ ] 임베딩 출력이 이후 어텐션 블록의 공통 입력이라는 점을 코드 수준에서 추적했는가

## 정리

이번 글에서는 토큰 ID를 의미 있는 벡터 표현으로 바꾸는 임베딩 단계와, 순서를 잃지 않게 해 주는 위치 임베딩 단계를 함께 정리했습니다. 핵심은 `nn.Embedding`을 추상적인 개념보다 학습 가능한 룩업 테이블로 이해하는 데 있습니다.

또한 GPT 입력부가 결국 `token_emb + pos_emb`라는 간결한 구조 위에 서 있다는 점도 확인했습니다. 이 한 줄이 있어야만 이후 어텐션이 토큰 간 관계를 계산할 수 있고, 모델이 순서를 포함한 문맥을 다루기 시작합니다.

다음 글에서는 이제 이 벡터들이 서로를 보게 만듭니다. 즉, 각 토큰이 다른 토큰을 얼마나 참고할지 결정하는 어텐션과 QKV 구조가 본격적으로 등장합니다.

## 디버깅에서 반드시 확인할 출력

임베딩 단계는 코드가 짧아서 지나치기 쉽지만, shape와 인덱스 범위를 한 번만 잘못 다루어도 이후 학습이 조용히 망가집니다. 그래서 초기에는 `x.min()`, `x.max()`, `x.dtype`, `tok_emb.shape`, `pos_emb.shape`를 로그로 남기는 편이 안전합니다.

특히 `x.max() >= vocab_size` 같은 상태는 즉시 실패로 처리해야 합니다. 이런 가드를 초기에 넣어 두면 어텐션 단계에서 원인 모를 `nan`을 추적하는 시간을 크게 줄일 수 있습니다.

## 처음 질문으로 돌아가기

- **`nn.Embedding`은 실제로 어떤 연산을 수행할까요?**
  - 본문의 기준은 정수에서 벡터로, 그리고 위치를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **토큰 임베딩만으로는 왜 충분하지 않을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **위치 정보는 왜 별도 임베딩으로 다루는 편이 실용적일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기](./01-tokenizer.md)
- **LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치 (현재 글)**
- LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기 (예정)
- LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위 (예정)
- LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성 (예정)
- LLM from Scratch 101 (6/9): 기울기로 배우기 (예정)
- LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기 (예정)
- LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기 (예정)
- LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Let's build GPT: from scratch, in code, spelled out.](https://www.youtube.com/watch?v=kCc8FmEb1nY)
- [PyTorch nn.Embedding](https://pytorch.org/docs/stable/generated/torch.nn.Embedding.html)

### 관련 시리즈

- [Vector Search 101 — 임베딩이란 무엇인가](../../vector-search-101/ko/01-what-is-embedding.md)
- [LLM 앱 기초 — 토큰 이해하기](../../llm-app-foundations-101/ko/02-understanding-tokens.md)
- [LangChain 101 — Prompt와 LLM Chain](../../langchain-101/ko/02-prompt-llm-chain.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/02-embedding)

Tags: LLM, PyTorch, Transformer, Tutorial
