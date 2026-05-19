---
title: 블록 하나, 깊이의 단위
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

# 블록 하나, 깊이의 단위

어텐션까지 구현하고 나면 토큰이 서로를 본다는 사실은 이해됩니다. 하지만 그 상태만으로는 모델이 깊어질 준비가 끝난 것이 아닙니다. 토큰 사이에서 정보를 주고받을 수는 있어도, 각 토큰 자리 안에서 표현을 더 풍부하게 가공하는 장치가 아직 부족합니다.

트랜스포머 블록이 중요한 이유가 바로 여기에 있습니다. 어텐션은 토큰 간 통신을 맡고, FeedForward는 각 위치 내부의 비선형 변환을 맡고, Residual connection과 LayerNorm은 그 전체를 학습 가능한 형태로 묶어 줍니다. 이 네 요소가 함께 있어야 비로소 깊이를 쌓을 수 있습니다.

많은 설명이 블록을 표준 부품처럼 지나가지만, 직접 구현해 보면 구조가 훨씬 분명해집니다. 정보가 새 표현으로 변형되는 경로와 원래 입력이 살아남는 경로를 동시에 유지하는 것이 왜 중요한지 코드 수준에서 바로 보이기 때문입니다.

이번 글에서는 `Block(nn.Module)`을 구현하면서 FeedForward, Residual, LayerNorm, 그리고 블록 반복이 어떤 역할 분담을 가지는지 정리하겠습니다. 여기서부터 GPT는 단일 어텐션 예제를 넘어 실제 모델 구조를 갖추기 시작합니다.

이 글은 LLM from Scratch 101 시리즈의 네 번째 글입니다.

이제 블록 하나를 제대로 이해하면 다음 글에서 GPT 전체 클래스를 조립하는 일이 훨씬 단순해집니다.

## 이 글에서 다룰 문제

- FeedForward는 왜 `Linear(C, 4C) -> GELU -> Linear(4C, C)` 형태를 많이 쓸까요?
- residual connection은 학습을 어떻게 안정화할까요?
- pre-norm과 post-norm은 실전에서 어떤 차이를 만들까요?
- 블록 하나 안에서 attention과 FFN의 역할은 어떻게 다를까요?
- 여러 블록을 쌓을 때 파라미터는 주로 어디에 몰릴까요?

## 왜 이 글이 중요한가

트랜스포머 블록은 GPT의 깊이를 구성하는 최소 단위입니다. 토큰끼리 보는 방법만 아는 상태에서는 아직 모델이 얕습니다. 블록이 있어야 토큰 간 관계를 반복적으로 섞고, 각 위치의 표현을 점진적으로 다듬으면서 더 강한 내부 표현을 만들 수 있습니다.

또한 블록은 실전 구현 감각을 키우는 데도 중요합니다. attention만 구현할 때는 텐서 관계가 눈에 잘 보이지만, 블록이 추가되면 residual path와 normalization 순서가 훈련 안정성에 직접 영향을 줍니다. 이 순서를 한 번 제대로 이해해 두면 이후 큰 모델을 읽을 때도 구조가 훨씬 빨리 보입니다.

파라미터 감각 면에서도 의미가 큽니다. 입문자는 attention이 모델의 대부분을 차지할 것이라 생각하기 쉽지만, 실제로는 FeedForward가 더 큰 비중을 가져가는 경우가 흔합니다. 블록을 손으로 계산해 보면 트랜스포머의 용량이 어디에 실리는지 감각이 생깁니다.

## 트랜스포머 블록을 이해하는 가장 좋은 방법: 토큰 간 혼합과 토큰 내부 변환을 잇는 잔차 래퍼로 보는 것입니다

트랜스포머 블록을 복잡한 부품 묶음으로만 보면 핵심이 흐려집니다. 더 실용적인 해석은 이렇습니다. **블록은 attention으로 토큰 간 정보를 섞고, FeedForward로 각 토큰 내부 표현을 가공한 뒤, residual path로 원래 입력을 보존하는 잔차 래퍼**입니다.

이 관점이 중요한 이유는 각 부품의 책임이 정확히 분리되기 때문입니다. attention은 "누구를 참고할지"를 결정하고, FFN은 "참고한 뒤 각 위치에서 무엇을 더 계산할지"를 맡습니다. LayerNorm은 두 경로 모두의 입력 스케일을 안정화하고, residual connection은 깊어져도 정보와 gradient가 끊기지 않게 돕습니다.

결국 블록은 단순히 층 하나를 더하는 장치가 아닙니다. 정보 교환, 위치별 가공, 학습 안정성을 하나의 재사용 가능한 단위로 묶는 설계입니다. 그래서 GPT의 깊이는 새로운 알고리즘을 계속 추가하는 대신 같은 블록을 반복해서 얻습니다.

> 이번 글의 핵심은 이것입니다. attention이 토큰 사이를 섞고, FFN이 토큰 안을 바꾸며, residual이 둘을 깊게 쌓을 수 있는 구조로 묶습니다.

## 핵심 개념

### FeedForward는 각 위치에서 독립적으로 도는 작은 MLP입니다

attention만 여러 층 쌓으면 토큰끼리 정보를 많이 교환할 수는 있습니다. 하지만 각 위치 내부 표현을 충분히 비선형적으로 가공하지 못하면 표현력 증가가 제한됩니다. 그래서 트랜스포머 블록은 각 토큰 위치에 동일하게 적용되는 MLP를 함께 둡니다.

실무에서 자주 쓰는 형태는 `Linear(C, 4C) -> GELU -> Linear(4C, C)`입니다. 중간 차원을 네 배로 넓혔다가 다시 원래 차원으로 줄이면서, 각 토큰이 더 다양한 조합을 잠깐 형성했다가 residual stream 크기로 돌아오게 만듭니다.

```python
import torch
import torch.nn as nn

class FeedForward(nn.Module):
    def __init__(self, n_embd: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
```

이 코드는 간단하지만 블록의 절반을 담당합니다. attention이 외부 문맥을 섞는다면, FFN은 그 결과를 각 위치 안에서 더 풍부한 특징으로 바꾸는 역할을 합니다.

### residual connection은 깊은 네트워크의 생존선입니다

모델이 깊어질수록 원래 입력 정보는 쉽게 흐려집니다. `x = x + f(x)` 형태의 residual connection은 이 문제를 완화합니다. 변환 결과를 더하되 원래 입력 경로를 유지함으로써, 학습 초반에는 최소한 입력 자체가 다음 층으로 전달되도록 보장합니다.

gradient 관점에서도 residual은 매우 중요합니다. 역전파 시 기울기가 긴 경로를 돌아야 하는 부담을 줄여 주기 때문에, 깊은 모델에서도 학습이 버틸 수 있습니다. 실전에서는 residual이 없을 때보다 초기화와 학습률에 덜 예민한 모델을 만들 수 있습니다.

### pre-norm은 깊은 GPT에서 사실상 표준입니다

원래 Transformer 논문은 sub-layer 뒤에 LayerNorm을 두는 post-norm 구조를 사용했습니다. 하지만 GPT-2 이후에는 입력을 먼저 정규화한 뒤 sub-layer를 통과시키는 pre-norm이 널리 쓰입니다. 깊이가 커질수록 pre-norm이 훨씬 안정적이기 때문입니다.

이번 시리즈도 pre-norm을 사용합니다. 즉, attention과 FFN에 들어가기 전에 각각 LayerNorm을 통과시키고, 결과를 residual로 더합니다. 코드상 한 줄 차이처럼 보이지만 학습 안정성에서는 체감 차이가 큽니다.

![pre-norm과 post-norm의 LayerNorm 배치 차이](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/04/04-01-layernorm-pre-norm-vs-post-norm.ko.png)

*LayerNorm을 앞에 둘지 뒤에 둘지에 따라 residual 흐름과 학습 안정성이 달라집니다.*

### 블록 구현은 surprisingly 짧지만 구조는 명확합니다

이제 앞선 `CausalSelfAttention`과 `FeedForward`를 묶어 `Block`을 만듭니다. 두 개의 LayerNorm과 두 번의 residual addition이 핵심입니다.

```python
import torch
import torch.nn as nn

class Block(nn.Module):
    def __init__(self, config) -> None:
        super().__init__()
        self.ln1 = nn.LayerNorm(config.n_embd)
        self.attn = CausalSelfAttention(config)
        self.ln2 = nn.LayerNorm(config.n_embd)
        self.ffn = FeedForward(config.n_embd)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln1(x))
        x = x + self.ffn(self.ln2(x))
        return x
```

이 구조를 읽을 때는 세 가지를 보면 됩니다. 첫째, 모든 sub-layer 앞에 LayerNorm이 있습니다. 둘째, attention과 FFN 모두 residual addition으로 감싸집니다. 셋째, 입력과 출력 shape는 끝까지 `(B, T, C)`로 유지됩니다. 이 일관성이 있어야 블록을 여러 개 쌓을 수 있습니다.

### 깊이는 새 부품이 아니라 같은 블록의 반복으로 얻습니다

트랜스포머의 깊이는 특별한 새 모듈을 계속 추가해서 생기지 않습니다. 같은 블록을 반복해서 쌓아 얻습니다. PyTorch에서는 `nn.ModuleList`로 매우 간단히 표현할 수 있습니다.

```python
self.blocks = nn.ModuleList([Block(config) for _ in range(config.n_layer)])

for block in self.blocks:
    x = block(x)
```

초기 블록은 상대적으로 로컬한 패턴을 정리하고, 뒤쪽 블록은 더 긴 문맥 관계를 조합하는 경향이 있습니다. 작은 char-level GPT에서도 블록을 몇 개 쌓으면 단순 문자 예측기에서 문맥 민감한 모델로 넘어가는 느낌이 확연해집니다.

### 파라미터는 attention보다 FFN에 더 많이 몰립니다

블록의 비용 구조를 손으로 계산해 보면 흥미로운 사실이 보입니다. attention은 `Q`, `K`, `V`, output projection까지 합쳐 대략 `4C²` 수준이고, FFN은 `C -> 4C -> C`라서 대략 `8C²` 수준입니다. 즉, FFN이 attention보다 대략 두 배 큽니다.

이번 설정인 `C=128`에서는 블록 하나가 attention에 약 66k, FFN에 약 131k 파라미터를 사용합니다. LayerNorm 둘까지 더하면 블록 하나는 대략 198k 파라미터입니다. 여섯 개를 쌓으면 약 1.18M 파라미터가 블록에 집중됩니다. 이 계산은 모델 용량이 어디에 들어가는지 빠르게 파악하게 해 줍니다.

## 흔히 헷갈리는 지점

- attention만 있으면 트랜스포머가 완성된다고 생각하기 쉽지만, FFN이 없으면 위치별 비선형 가공이 약합니다.
- residual connection을 단순 편의 장치로 보기 쉽지만, 깊은 모델 학습을 버티게 하는 핵심 구조입니다.
- LayerNorm 위치를 사소한 스타일 차이로 보기 쉽지만, pre-norm과 post-norm은 학습 안정성에서 차이가 큽니다.
- 블록을 많이 쌓을수록 attention 비용만 커진다고 생각하기 쉽지만, 실제로는 FFN 비중이 더 큽니다.
- 블록 반복을 복잡한 아키텍처 확장으로 느끼기 쉽지만, 구현 자체는 동일한 `(B, T, C)` 변환의 반복입니다.

## 운영 체크리스트

- [ ] 블록 안에서 attention과 FFN의 책임 차이를 한 문장씩 설명할 수 있는가
- [ ] pre-norm residual 흐름을 직접 다이어그램으로 그릴 수 있는가
- [ ] 블록 입력과 출력 shape가 항상 `(B, T, C)`로 유지되는지 확인했는가
- [ ] `n_layer`를 늘릴 때 파라미터 증가량을 대략 계산할 수 있는가
- [ ] FFN이 attention보다 더 큰 파라미터 비중을 가진다는 점을 이해했는가

## 정리

이번 글에서는 attention 위에 FeedForward, residual, LayerNorm을 더해 트랜스포머 블록 하나를 완성했습니다. 이 블록은 토큰 간 정보 교환과 토큰 내부 변환, 그리고 학습 안정성을 하나로 묶는 재사용 가능한 깊이 단위입니다.

또한 GPT의 깊이가 특별한 새 구조에서 오는 것이 아니라, 같은 블록을 반복해서 쌓는 방식에서 온다는 점도 확인했습니다. 그리고 그 반복의 비용은 생각보다 FFN 쪽에 더 많이 실린다는 사실도 함께 봤습니다.

다음 글에서는 지금까지 만든 임베딩과 블록들을 모두 조립해 `GPT(nn.Module)` 전체 클래스를 완성합니다. 즉, 입력부터 logits와 loss까지 한 번에 계산하는 모델 껍질을 만들게 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [글자를 숫자로 바꾸기](./01-tokenizer.md)
- [정수에서 벡터로, 그리고 위치](./02-embedding.md)
- [어떤 토큰을 얼마나 볼지 스스로 정하기](./03-attention.md)
- **블록 하나, 깊이의 단위 (현재 글)**
- 조립: GPT 모델 클래스 완성 (예정)
- 기울기로 배우기 (예정)
- 샘플링 — 학습된 모델에서 글 뽑아내기 (예정)
- 베이스 모델을 우리 작업에 맞추기 (예정)
- 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

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

Tags: LLM, PyTorch, Transformer, Tutorial
