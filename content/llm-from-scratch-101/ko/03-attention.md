---
title: 어떤 토큰을 얼마나 볼지 스스로 정하기
series: llm-from-scratch-101
episode: 3
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
seo_description: 문장을 읽을 때 사람도 모든 단어를 같은 세기로 보지 않습니다. 어텐션도 이와 비슷하게 중요한 토큰을 골라봅니다.
---

# 어떤 토큰을 얼마나 볼지 스스로 정하기

임베딩까지 구현하고 나면 드디어 토큰이 벡터가 됩니다. 하지만 그다음 바로 드는 질문이 있습니다. 각 토큰은 자기 위치의 벡터만 보고 어떻게 문맥을 이해할 수 있을까요? 문장 안에서 어떤 단어가 중요한지, 어느 앞선 토큰을 참고해야 하는지는 누가 정할까요?

바로 그 지점에서 어텐션이 등장합니다. 사람도 문장을 읽을 때 모든 단어를 같은 강도로 보지 않습니다. 대명사를 보면 앞의 명사를 다시 확인하고, 문장 끝의 동사를 보면 앞선 주어를 잠깐 되짚습니다. 트랜스포머의 어텐션도 이와 비슷하게 각 토큰이 다른 토큰을 얼마나 참고할지 점수를 매깁니다.

처음 배울 때는 `Q`, `K`, `V`라는 이름이 오히려 개념을 흐릴 수 있습니다. 실제 구현은 훨씬 단순합니다. 같은 입력 텐서에 선형층 세 개를 적용해 서로 다른 역할의 표현을 만들고, 그 사이의 점수를 계산하고, 미래를 가리는 마스크를 씌우고, softmax와 가중합을 적용하면 됩니다.

이번 글에서는 `CausalSelfAttention`을 `model.py`에 붙이면서, 어텐션을 수학 공식보다 텐서 흐름과 shape 변화 중심으로 이해하겠습니다. 이 시리즈에서는 멋진 축약보다 추적 가능한 구현이 더 중요합니다.

이 글은 LLM from Scratch 101 시리즈의 세 번째 글입니다.

이제 각 토큰이 다른 토큰을 어떻게 바라보는지 이해하면, 다음 글에서 트랜스포머 블록 전체를 조립할 준비가 됩니다.

## 이 글에서 다룰 문제

- Q, K, V는 왜 같은 입력에서 나오지만 서로 다른 역할을 가질까요?
- 어텐션 점수는 왜 `Q · K^T / sqrt(d)` 형태로 계산할까요?
- causal mask가 없으면 자기회귀 학습에서 정확히 무엇이 망가질까요?
- multi-head는 단일 head보다 무엇을 더 잘 표현할 수 있을까요?
- `nn.Linear`, `reshape`, `transpose`만으로도 어텐션을 끝까지 구현할 수 있을까요?

## 왜 이 글이 중요한가

어텐션은 트랜스포머를 트랜스포머답게 만드는 핵심 구성 요소입니다. 임베딩이 개별 토큰을 벡터로 바꾸는 단계였다면, 어텐션은 그 벡터들이 서로 문맥 관계를 맺게 하는 단계입니다. 여기서부터 모델은 더 이상 독립된 문자 묶음이 아니라 시퀀스로 동작하기 시작합니다.

또한 어텐션은 개념만 알면 안 되고 shape 감각까지 함께 익혀야 하는 주제입니다. 실제 구현 오류의 상당수는 수학 오해보다 `transpose` 축, mask 범위, `contiguous()` 누락 같은 텐서 조작에서 나옵니다. 그래서 이 글에서는 공식보다도 텐서가 어떻게 흐르는지에 초점을 둡니다.

실무적으로도 중요합니다. causal mask, multi-head 분할, score scaling은 모두 이후 학습 안정성과 생성 품질에 직접 영향을 줍니다. 이 구조를 정확히 이해해야 다음 글의 residual, layer norm, GPT 클래스 조립도 자연스럽게 따라갈 수 있습니다.

## 어텐션을 이해하는 가장 좋은 방법: 각 토큰이 다른 토큰을 조회하는 동적 룩업으로 보는 것입니다

어텐션을 복잡한 수식 체계로만 보면 입문 단계에서 금방 막힙니다. 더 실용적인 관점은 이것입니다. **어텐션은 각 토큰이 Query로 질문을 던지고, Key와의 유사도로 참고 대상을 고른 뒤, Value에서 실제 내용을 가져오는 동적 룩업 메커니즘**입니다.

이 관점이 좋은 이유는 QKV의 역할이 자연스럽게 분리되기 때문입니다. Query는 "나는 지금 무엇을 찾는가"를 표현하고, Key는 "나는 어떤 단서인가"를 표현하며, Value는 "실제로 가져갈 내용"을 담습니다. 결국 각 토큰은 현재 문맥에 맞는 조회를 수행하는 셈입니다.

자기회귀 모델에서는 여기에 한 가지 규율이 더 붙습니다. 미래 토큰을 보면 안 된다는 점입니다. 그래서 causal mask가 필수이고, 이 마스크가 있어야 언어 모델은 다음 토큰 예측이라는 학습 규칙을 지킬 수 있습니다.

> 어텐션의 핵심은 모든 토큰을 똑같이 섞는 것이 아니라, 현재 토큰이 필요한 정보에 더 큰 가중치를 주도록 만드는 데 있습니다.

## 핵심 개념

### QKV는 같은 입력에서 나온 세 개의 선형 변환입니다

입력 텐서 `x`가 `(B, T, C)`라면, 어텐션은 여기에서 세 개의 사영을 만듭니다. `q = Wq x`, `k = Wk x`, `v = Wv x`입니다. 셋 다 같은 원본을 보지만 역할은 다릅니다. Query는 찾고 싶은 패턴, Key는 자신이 제공할 수 있는 단서, Value는 실제로 전달할 내용을 나타냅니다.

이 설명은 거창해 보일 수 있지만 구현 수준에서는 선형층 세 개입니다. 이름이 복잡할 뿐, 코드 구조는 매우 직선적입니다. 그래서 처음에는 개념보다 "같은 입력에 다른 투영 세 개"라는 감각으로 이해하는 편이 좋습니다.

### 점수 계산은 내적과 스케일링으로 이뤄집니다

한 토큰이 다른 토큰을 얼마나 봐야 하는지 결정하려면 점수가 필요합니다. Query와 Key의 내적이 그 점수 역할을 합니다. 값이 클수록 두 표현이 더 잘 맞는다고 해석할 수 있습니다. 다만 차원이 커질수록 내적 값의 분산도 커지므로 `sqrt(d)`로 나눠 스케일을 안정화합니다.

이 한 줄은 학습 안정성에 직접 연결됩니다. 스케일링이 없으면 softmax가 너무 급격하게 뾰족해지고, 몇몇 값만 거의 1이 되면서 gradient가 불안정해질 수 있습니다. 따라서 `sqrt(d)`는 장식이 아니라 훈련 가능성을 지키는 안전장치입니다.

### causal mask는 미래 정보를 차단하는 규율입니다

언어 모델은 현재 위치에서 다음 토큰을 맞히는 자기회귀 구조입니다. 따라서 현재 위치가 뒤쪽 정답을 미리 보면 학습 문제가 무너집니다. 이를 막기 위해 score matrix의 상삼각 영역, 즉 미래 위치를 `-inf`로 채워 softmax 이후 확률이 0이 되게 만듭니다.

![미래 토큰을 보지 못하게 막는 causal mask](../../../assets/llm-from-scratch-101/03/03-01-causal-mask.ko.png)

*점수 행렬의 상삼각을 차단해 자기회귀 규칙을 지키는 causal mask 구조입니다.*

mask는 단순한 디테일이 아닙니다. 이 한 줄이 없으면 모델은 학습 중에 미래를 훔쳐보고도 좋은 loss를 내기 때문에, 추론 시점에서 제대로 동작하지 않는 모델이 됩니다.

### 단일 head 어텐션은 짧은 코드로 구현할 수 있습니다

가장 작은 형태의 self-attention은 다음 코드로 구현할 수 있습니다. 이 예제는 `wei`를 함께 반환하므로 각 토큰이 어디를 바라봤는지 직접 확인하기 좋습니다.

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

이 예제에서 `out`은 `(B, T, head_size)`이고, `wei`는 각 토큰이 다른 토큰을 얼마나 참고했는지 보여 주는 가중치 행렬입니다. 어텐션 디버깅에서는 이 행렬을 직접 찍어 보는 습관이 매우 도움이 됩니다.

### multi-head는 여러 관점의 관계를 병렬로 학습하게 합니다

단일 head만 쓰면 모델은 한 종류의 관계만 강조하기 쉽습니다. multi-head는 임베딩 차원을 여러 조각으로 나누고, 각 조각이 서로 다른 관점으로 관계를 점수화하게 만듭니다. 어떤 head는 가까운 문맥에, 어떤 head는 반복 구조나 화자 전환에 더 민감할 수 있습니다.

중요한 점은 head 수를 늘린다고 무조건 좋아지는 것은 아니라는 사실입니다. 같은 `n_embd` 안에서 head 수가 늘어나면 head당 차원은 줄어듭니다. 이번 시리즈의 설정인 `n_embd=128`, `n_head=4`는 이 구조를 관찰하기 좋은 균형점입니다.

### `nn.Linear`와 reshape만으로 시리즈용 어텐션을 완성할 수 있습니다

이제 시리즈의 `CausalSelfAttention`을 구현합니다. `einsum` 같은 축약 없이도, 필요한 것은 선형층과 reshape, transpose, projection뿐입니다.

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

출력 shape가 `(2, 8, 128)`으로 유지되고, `attn.last_attn`이 `(2, 4, 8, 8)`이라면 multi-head 분해와 재조립이 올바르게 동작하고 있다는 뜻입니다. 여기서 가장 자주 틀리는 부분은 축 순서와 `contiguous()` 처리입니다.

### 단일 head 가중치를 직접 보면 구현 검증이 쉬워집니다

첫 번째 토큰은 자기 자신만 봐야 하고, 두 번째 토큰은 첫 두 위치만 봐야 합니다. 이 패턴이 가중치 행렬에서 보인다면 mask가 정상입니다. 반대로 오른쪽 위에 값이 살아 있다면 미래 차단이 실패한 것입니다.

어텐션 디버깅의 절반은 바로 이런 작은 검증입니다. 개념 이해보다도 출력 shape, mask 범위, head 재조립이 맞는지 먼저 확인해야 다음 단계에서 시간을 덜 잃습니다.

## 흔히 헷갈리는 지점

- Q, K, V가 완전히 다른 데이터에서 온다고 생각하기 쉽지만, 기본 self-attention에서는 같은 입력 텐서의 다른 선형 투영입니다.
- `sqrt(d)`를 수식 장식처럼 보지만, softmax 안정성을 위해 매우 중요합니다.
- causal mask를 옵션으로 오해하기 쉽지만, 자기회귀 언어 모델에서는 필수 규칙입니다.
- head 수가 많을수록 항상 더 좋다고 생각하기 쉽지만, 동일한 `n_embd`에서는 head당 차원이 줄어듭니다.
- 어텐션 버그를 개념 문제로만 보지만, 실제 오류는 종종 shape·transpose·mask 범위 같은 구현 세부에서 발생합니다.

## 운영 체크리스트

- [ ] score matrix와 causal mask가 각각 어떤 shape인지 손으로 적어 볼 수 있는가
- [ ] 단일 head의 `wei`를 출력해 오른쪽 위가 막히는지 확인했는가
- [ ] multi-head 분해 후 `(B, n_head, T, head_size)` shape를 추적할 수 있는가
- [ ] `out.transpose(...).contiguous().view(...)`가 왜 필요한지 설명할 수 있는가
- [ ] 미래 토큰을 보지 못하게 막는 규칙이 학습/추론 일관성에 왜 중요한지 이해했는가

## 정리

이번 글에서는 어텐션을 각 토큰이 다른 토큰을 동적으로 조회하는 메커니즘으로 정리했습니다. QKV는 같은 입력을 서로 다른 역할로 투영한 결과이고, 점수 계산과 softmax를 통해 각 토큰은 필요한 문맥을 선택적으로 끌어옵니다.

또한 causal mask와 multi-head 구조가 왜 중요한지도 살펴봤습니다. mask는 자기회귀 규칙을 지키게 만들고, multi-head는 서로 다른 관계 패턴을 병렬로 볼 수 있게 합니다. 이 둘이 합쳐져야 GPT가 단순한 문자 예측기를 넘어 문맥 기반 모델로 움직입니다.

다음 글에서는 여기에 FeedForward, Residual, LayerNorm을 더해 트랜스포머 블록 하나를 완성합니다. 즉, 토큰 간 정보 교환에 이어 각 위치 내부 표현을 더 깊게 가공하는 단계로 넘어갑니다.

<!-- toc:begin -->
## LLM from Scratch 101 시리즈

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

### 공식 문서

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [nanoGPT model.py](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [PyTorch scaled_dot_product_attention](https://pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)

### 관련 시리즈

- [LangGraph 101 — 상태와 라우팅 설계](../../langgraph-101/ko/02-state-and-checkpoints.md)
- [AI Agent 101 — 컨텍스트 엔지니어링](../../ai-agent-101/ko/02-context-engineering.md)
- [LLM 앱 기초 — 프롬프트 엔지니어링 기초](../../llm-app-foundations-101/ko/03-prompt-engineering-basics.md)

Tags: LLM, PyTorch, Transformer, Tutorial
