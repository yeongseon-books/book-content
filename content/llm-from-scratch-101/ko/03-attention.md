---
title: "LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기"
series: llm-from-scratch-101
episode: 3
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
seo_description: 문장을 읽을 때 사람도 모든 단어를 같은 세기로 보지 않습니다. 어텐션도 이와 비슷하게 중요한 토큰을 골라봅니다.
---

# LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기

임베딩까지 구현하고 나면 드디어 토큰이 벡터가 됩니다. 하지만 그다음 바로 드는 질문이 있습니다. 각 토큰은 자기 위치의 벡터만 보고 어떻게 문맥을 이해할 수 있을까요? 문장 안에서 어떤 단어가 중요한지, 어느 앞선 토큰을 참고해야 하는지는 누가 정할까요?

바로 그 지점에서 어텐션이 등장합니다. 사람도 문장을 읽을 때 모든 단어를 같은 강도로 보지 않습니다. 대명사를 보면 앞의 명사를 다시 확인하고, 문장 끝의 동사를 보면 앞선 주어를 잠깐 되짚습니다. 트랜스포머의 어텐션도 이와 비슷하게 각 토큰이 다른 토큰을 얼마나 참고할지 점수를 매깁니다.

이번 글에서는 `CausalSelfAttention`을 `model.py`에 붙이면서, 어텐션을 수학 공식보다 텐서 흐름과 shape 변화 중심으로 이해하겠습니다. 이 시리즈에서는 멋진 축약보다 추적 가능한 구현이 더 중요합니다.

이 글은 LLM from Scratch 101 시리즈의 세 번째 글입니다. 여기서는 QKV 투영, score 계산, causal mask, multi-head 재조립까지를 한 번에 연결합니다.

## 먼저 던지는 질문

- Q, K, V는 왜 같은 입력에서 나오지만 서로 다른 역할을 가질까요?
- 어텐션 점수는 왜 `Q · K^T / sqrt(d)` 형태로 계산할까요?
- causal mask가 없으면 자기회귀 학습에서 정확히 무엇이 망가질까요?

## 큰 그림

![LLM from Scratch 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/03/03-01-causal-mask.ko.png)

*LLM from Scratch 101 3장 흐름 개요*

## 왜 이 글이 중요한가

어텐션은 트랜스포머를 트랜스포머답게 만드는 핵심 구성 요소입니다. 임베딩이 개별 토큰을 벡터로 바꾸는 단계였다면, 어텐션은 그 벡터들이 서로 문맥 관계를 맺게 하는 단계입니다. 여기서부터 모델은 더 이상 독립된 문자 묶음이 아니라 시퀀스로 동작하기 시작합니다.

또한 어텐션은 개념만 알면 안 되고 shape 감각까지 함께 익혀야 하는 주제입니다. 실제 구현 오류의 상당수는 수학 오해보다 `transpose` 축, mask 범위, `contiguous()` 누락 같은 텐서 조작에서 나옵니다. 그래서 이 글에서는 공식보다도 텐서가 어떻게 흐르는지에 초점을 둡니다.

실무적으로도 중요합니다. causal mask, multi-head 분할, score scaling은 모두 이후 학습 안정성과 생성 품질에 직접 영향을 줍니다. 이 구조를 정확히 이해해야 다음 글의 residual, layer norm, GPT 클래스 조립도 자연스럽게 따라갈 수 있습니다.

## 핵심 관점

어텐션을 복잡한 수식 체계로만 보면 입문 단계에서 금방 막힙니다. 더 실용적인 관점은 이것입니다. **어텐션은 각 토큰이 Query로 질문을 던지고, Key와의 유사도로 참고 대상을 고른 뒤, Value에서 실제 내용을 가져오는 동적 룩업 메커니즘**입니다.

이 관점이 좋은 이유는 QKV의 역할이 자연스럽게 분리되기 때문입니다. Query는 "나는 지금 무엇을 찾는가"를 표현하고, Key는 "나는 어떤 단서인가"를 표현하며, Value는 "실제로 가져갈 내용"을 담습니다. 결국 각 토큰은 현재 문맥에 맞는 조회를 수행하는 셈입니다.

자기회귀 모델에서는 여기에 한 가지 규율이 더 붙습니다. 미래 토큰을 보면 안 된다는 점입니다. 그래서 causal mask가 필수이고, 이 마스크가 있어야 언어 모델은 다음 토큰 예측이라는 학습 규칙을 지킬 수 있습니다.

## 핵심 개념

### QKV는 같은 입력에서 나온 세 개의 선형 변환입니다

입력 텐서 `x`가 `(B, T, C)`라면, 어텐션은 여기에서 세 개의 사영을 만듭니다. `q = Wq x`, `k = Wk x`, `v = Wv x`입니다. 셋 다 같은 원본을 보지만 역할은 다릅니다. Query는 찾고 싶은 패턴, Key는 자신이 제공할 수 있는 단서, Value는 실제로 전달할 내용을 나타냅니다.

이 설명은 거창해 보일 수 있지만 구현 수준에서는 선형층 세 개입니다. 이름이 복잡할 뿐, 코드 구조는 매우 직선적입니다. 그래서 처음에는 개념보다 "같은 입력에 다른 투영 세 개"라는 감각으로 이해하는 편이 좋습니다.

### 점수 계산은 내적과 스케일링으로 이뤄집니다

한 토큰이 다른 토큰을 얼마나 봐야 하는지 결정하려면 점수가 필요합니다. Query와 Key의 내적이 그 점수 역할을 합니다. 값이 클수록 두 표현이 더 잘 맞는다고 해석할 수 있습니다. 다만 차원이 커질수록 내적 값의 분산도 커지므로 `sqrt(d)`로 나눠 스케일을 안정화합니다.

이 한 줄은 학습 안정성에 직접 연결됩니다. 스케일링이 없으면 softmax가 너무 급격하게 뾰족해지고, 몇몇 값만 거의 1이 되면서 gradient가 불안정해질 수 있습니다. 따라서 `sqrt(d)`는 장식이 아니라 훈련 가능성을 지키는 안전장치입니다.

### causal mask는 미래 정보를 차단하는 규율입니다

언어 모델은 현재 위치에서 다음 토큰을 맞히는 자기회귀 구조입니다. 따라서 현재 위치가 뒤쪽 정답을 미리 보면 학습 문제가 무너집니다. 이를 막기 위해 score matrix의 상삼각 영역, 즉 미래 위치를 `-inf`로 채워 softmax 이후 확률이 0이 되게 만듭니다.

mask는 단순한 디테일이 아닙니다. 이 한 줄이 없으면 모델은 학습 중에 미래를 훔쳐보고도 좋은 loss를 내기 때문에, 추론 시점에서 제대로 동작하지 않는 모델이 됩니다.

## 단계별로 구현해 보기

### Step 1. 단일 head로 점수 행렬을 먼저 눈으로 확인합니다

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
        _, t, _ = x.shape
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

**Expected output:**

```text
torch.Size([2, 4, 8])
tensor([[1.0000, 0.0000, 0.0000, 0.0000],
        [0.47.., 0.52.., 0.0000, 0.0000],
        [0.31.., 0.28.., 0.40.., 0.0000],
        [0.22.., 0.19.., 0.27.., 0.30..]])
```

첫 번째 행은 자기 자신만 봐야 하고, 두 번째 행은 첫 두 토큰까지만 봐야 합니다. 숫자가 정확히 같을 필요는 없지만, 오른쪽 위 영역이 0으로 막혀 있어야 causal mask가 제대로 적용된 것입니다.

### Step 2. mask를 빼 보면 무엇이 잘못되는지 바로 확인할 수 있습니다

학습 중 버그를 잡을 때는 "정상 출력"만 보는 것보다 "잘못된 출력이 어떻게 생기는지"를 아는 편이 더 도움이 됩니다. 아래처럼 mask를 임시로 빼고 점수 행렬을 보면, 미래 위치까지 확률이 살아남는 것을 바로 확인할 수 있습니다.

```python
import math

import torch
import torch.nn.functional as F

q = torch.randn(1, 4, 8)
k = torch.randn(1, 4, 8)
scores = q @ k.transpose(-2, -1) / math.sqrt(k.size(-1))

print("without mask")
print(F.softmax(scores, dim=-1)[0])

tril = torch.tril(torch.ones(4, 4))
masked_scores = scores.masked_fill(tril == 0, float("-inf"))

print("with mask")
print(F.softmax(masked_scores, dim=-1)[0])
```

**Expected output:**

```text
without mask
tensor([[0.20.., 0.29.., 0.24.., 0.25..],
        [0.10.., 0.31.., 0.27.., 0.30..],
        ...])

with mask
tensor([[1.0000, 0.0000, 0.0000, 0.0000],
        [0.24.., 0.75.., 0.0000, 0.0000],
        ...])
```

이 비교는 단순 데모가 아닙니다. 모델이 미래를 몰래 보고 있는지 확인하는 가장 빠른 검증 절차입니다. 학습 loss가 비정상적으로 잘 내려가는데 추론이 엉망일 때 가장 먼저 볼 지점도 여기입니다.

### Step 3. multi-head는 여러 관점의 관계를 병렬로 학습하게 합니다

단일 head만 쓰면 모델은 한 종류의 관계만 강조하기 쉽습니다. multi-head는 임베딩 차원을 여러 조각으로 나누고, 각 조각이 서로 다른 관점으로 관계를 점수화하게 만듭니다. 어떤 head는 가까운 문맥에, 어떤 head는 반복 구조나 화자 전환에 더 민감할 수 있습니다.

중요한 점은 head 수를 늘린다고 무조건 좋아지는 것은 아니라는 사실입니다. 같은 `n_embd` 안에서 head 수가 늘어나면 head당 차원은 줄어듭니다. 이번 시리즈의 설정인 `n_embd=128`, `n_head=4`는 이 구조를 관찰하기 좋은 균형점입니다.

### Step 4. `nn.Linear`와 reshape만으로 시리즈용 어텐션을 완성할 수 있습니다

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

**Expected output:**

```text
torch.Size([2, 8, 128])
torch.Size([2, 4, 8, 8])
```

출력 shape가 `(2, 8, 128)`으로 유지되고, `attn.last_attn`이 `(2, 4, 8, 8)`이라면 multi-head 분해와 재조립이 올바르게 동작하고 있다는 뜻입니다. 여기서 가장 자주 틀리는 부분은 축 순서와 `contiguous()` 처리입니다.

### Step 5. head별 가중치를 직접 저장해 두면 다음 글 디버깅이 쉬워집니다

학습 전에라도 `self.last_attn = wei`처럼 최근 attention map을 저장해 두면, 블록을 여러 개 쌓기 시작한 뒤에도 "지금 mask가 살아 있는가", "특정 head가 완전히 죽었는가"를 빠르게 확인할 수 있습니다. 소형 모델에서는 이런 단순한 관측 지점이 디버깅 시간을 크게 줄여 줍니다.

## 자주 망가지는 지점과 첫 번째 점검 순서

어텐션은 개념보다 구현 세부에서 더 자주 망가집니다. 특히 아래 증상은 거의 매번 비슷한 원인으로 이어집니다.

| 증상 | 가장 먼저 볼 것 | 흔한 원인 |
| --- | --- | --- |
| 학습 loss는 잘 내려가는데 생성이 엉망 | mask 출력 | 미래 토큰을 보고 학습함 |
| `view` 단계에서 shape 에러 | `transpose` 직후 텐서 연속성 | `contiguous()` 누락 |
| head 수를 늘리자마자 에러 | `n_embd % n_head` | head당 차원 정수 분할 실패 |
| attention map이 전부 비슷함 | `sqrt(d)`와 softmax 입력 | score scale 과대 |
| 메모리 사용량이 급증 | `T x T` attention map 크기 | block_size 과대 설정 |

실전 디버깅에서는 수식을 다시 읽기보다 shape를 프린트하고, mask 전후 행렬을 비교하고, 한 head만 따로 보는 편이 훨씬 빠릅니다. 이 습관은 다음 글의 블록 조립에서도 그대로 도움이 됩니다.

## 실무에서는 이렇게 생각합니다

이번 시리즈는 char-level GPT라서 head 수와 context 길이가 작습니다. 그래도 attention의 계산 비용이 `T²`로 늘어난다는 사실은 그대로입니다. 지금은 `block_size=64`라 부담이 작지만, 나중에 512나 2048 같은 길이로 가면 attention map이 메모리와 시간을 빠르게 잡아먹습니다.

또한 attention은 "모델이 문맥을 본다"는 설명으로 끝내기 쉬우나, 실제로는 매우 기계적인 텐서 조작의 합입니다. 그래서 큰 모델을 다룰 때도 추상적 설명보다 `shape`, `mask`, `projection`, `residual stream`이라는 언어로 접근하는 편이 훨씬 안정적입니다.

## 메모리 프로파일로 보는 attention 비용

attention을 이해할 때 가장 자주 놓치는 현실은 메모리입니다. 계산량뿐 아니라 `attention score`와 `attention prob` 텐서가 `B x H x T x T`로 만들어지는 순간 메모리 사용량이 급격히 늘어납니다. 그래서 block size를 키우기 전에 먼저 간단한 프로파일을 돌려 보는 습관이 필요합니다.

```python
import torch

def estimate_attn_bytes(batch: int, n_head: int, t: int, dtype_bytes: int = 4) -> int:
    # score + prob 두 텐서를 대략 합산
    return 2 * batch * n_head * t * t * dtype_bytes

for t in [64, 128, 256, 512]:
    mb = estimate_attn_bytes(batch=8, n_head=8, t=t) / (1024**2)
    print(f"T={t:>3} -> attn tensors ~= {mb:8.2f} MB")
```

예상 출력은 다음과 비슷합니다.

```text
T= 64 -> attn tensors ~=     2.00 MB
T=128 -> attn tensors ~=     8.00 MB
T=256 -> attn tensors ~=    32.00 MB
T=512 -> attn tensors ~=   128.00 MB
```

`T`를 두 배로 늘리면 메모리가 네 배로 늘어나는 이유가 바로 여기서 보입니다. 이 수치 감각이 있으면 "왜 block_size를 512로 바꾸자마자 OOM이 났는가"를 직관적으로 설명할 수 있습니다.

### PyTorch 프로파일러로 head별 병목을 확인하는 방법

아래처럼 짧은 프로파일 구간을 넣으면 어느 연산이 시간을 먹는지 빠르게 볼 수 있습니다.

```python
with torch.profiler.profile(
    activities=[torch.profiler.ProfilerActivity.CPU],
    record_shapes=True,
) as prof:
    out = attn(x)

print(
    prof.key_averages()
    .table(sort_by="self_cpu_time_total", row_limit=8)
)
```

대체로 `matmul`, `softmax`, `transpose` 관련 항목이 상위에 뜹니다. 이 표를 한 번 확인해 두면 이후 최적화 우선순위를 정하기가 쉬워집니다. 예를 들어 소형 모델에서는 fancy한 최적화보다 `block_size` 조정과 batch tuning이 더 큰 효과를 내는 경우가 많습니다.

### shape 추적 로그를 남기면 버그 원인을 즉시 좁힐 수 있습니다

```python
def forward(self, x: torch.Tensor):
    b, t, c = x.shape
    k = self.key(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)
    q = self.query(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)
    v = self.value(x).view(b, t, self.n_head, self.head_size).transpose(1, 2)
    print("qkv", q.shape, k.shape, v.shape)  # (B,H,T,HS)

    wei = q @ k.transpose(-2, -1)
    print("wei", wei.shape)                  # (B,H,T,T)
```

생성 실패나 학습 불안정이 보일 때 이 로그 두 줄만 있어도 절반은 해결됩니다. 특히 `wei` shape가 `(B, T, H, T)`처럼 비정상으로 나오면 축 순서 실수로 바로 판단할 수 있습니다.

### Attention 구현 비교표

| 구현 방식 | 장점 | 단점 | 입문 단계 적합성 |
| --- | --- | --- | --- |
| 명시적 `q @ k^T`, `softmax` | 디버깅/학습에 매우 유리 | 최적화 자동 이점 적음 | 매우 높음 |
| `scaled_dot_product_attention` API | 최신 커널 활용 가능 | 내부 동작 가시성 낮음 | 중간 |
| Flash Attention 계열 | 긴 문맥 성능 우수 | 의존성/환경 제약 | 낮음(입문) |

이번 시리즈는 첫 번째 방식을 택합니다. 이유는 단순합니다. 성능 절대값보다 attention이 어떻게 동작하는지 끝까지 추적하는 것이 목표이기 때문입니다.

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

## 처음 질문으로 돌아가기

- **Q, K, V는 왜 같은 입력에서 나오지만 서로 다른 역할을 가질까요?**
  - 본문의 기준은 어떤 토큰을 얼마나 볼지 스스로 정하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **어텐션 점수는 왜 `Q · K^T / sqrt(d)` 형태로 계산할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **causal mask가 없으면 자기회귀 학습에서 정확히 무엇이 망가질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치](./02-embedding.md)
- **LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기 (현재 글)**
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
- [nanoGPT model.py](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [PyTorch scaled_dot_product_attention](https://pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)

### 관련 시리즈

- [LangGraph 101 — 상태와 라우팅 설계](../../langgraph-101/ko/02-state-and-checkpoints.md)
- [AI Agent 101 — 컨텍스트 엔지니어링](../../ai-agent-101/ko/02-context-engineering.md)
- [LLM 앱 기초 — 프롬프트 엔지니어링 기초](../../llm-app-foundations-101/ko/03-prompt-engineering-basics.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/03-attention)

Tags: LLM, PyTorch, Transformer, Tutorial
