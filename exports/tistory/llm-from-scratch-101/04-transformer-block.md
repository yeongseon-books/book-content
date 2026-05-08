
# 블록 하나, 깊이의 단위

> LLM from Scratch 101 시리즈 (4/9)

지난 글에서 `CausalSelfAttention`까지 만들고 나면 한숨 돌리게 됩니다. 토큰이 서로를 보는 눈은 생겼고, 가중치 행렬도 찍어 봤습니다. 그런데 그 상태로 블록을 여러 층 쌓아 보면 생각보다 금방 한계가 보입니다. 토큰끼리 정보를 섞는 일은 되는데, 각 토큰 안에서 표현을 더 비선형적으로 가공하는 손이 아직 약합니다.

저는 트랜스포머를 처음 구현할 때 이 대목에서 구조가 선명해졌습니다. 어텐션은 토큰 사이 통신선이고, FeedForward는 각 토큰 자리에서 따로 도는 작은 변환기입니다. 둘을 잔차 연결로 묶어 놓으니 비로소 "깊이를 쌓을 수 있는 단위"라는 느낌이 납니다.

GPT 계열 모델을 읽다 보면 블록이 당연한 부품처럼 보이지만, 막상 손으로 적어 보면 이유가 분명합니다. 학습이 잘 되려면 정보가 돌아다니는 길과 원래 입력이 살아남는 길을 같이 보장해야 합니다.

오늘 멘탈 모델은 이렇습니다. **어텐션이 토큰끼리 섞고, FFN이 토큰 안에서 바꾸고, 잔차가 둘을 안전하게 감쌉니다.**

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- FeedForward는 왜 단순한 2-layer MLP로 충분할까요?
- residual connection이 학습을 어떻게 살릴까요?
- pre-norm과 post-norm의 실전 차이는 무엇일까요?
- 블록 하나의 파라미터는 어디에 가장 많이 모일까요?

<!-- a-grade-intro:end -->

## FeedForward는 그냥 2-layer MLP

어텐션만 여러 층 쌓으면 토큰끼리 참조는 많이 합니다. 그래도 표현력이 기대만큼 늘지 않습니다. 각 위치에서 비선형 변환이 부족하기 때문입니다. 그래서 블록마다 `Linear(C, 4C) → GELU → Linear(4C, C)` 형태의 MLP를 하나 더 둡니다.

중간 차원을 4배로 키우는 이유도 실용적입니다. 잠깐 넓혀 두면 토큰 하나가 더 풍부한 조합을 만들 수 있고, 마지막 선형층에서 다시 원래 차원으로 접어 넣기 쉽습니다. 작은 모델에서도 FFN이 꽤 많은 일을 맡는 이유가 여기 있습니다.

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

## 잔차 연결(Residual) — Skip이 학습을 살린다

블록이 깊어질수록 원래 입력 정보가 중간에서 흐려지기 쉽습니다. `x = x + f(x)` 형태의 잔차 연결은 이 문제를 크게 줄여 줍니다. 변환이 서툰 초반에는 최소한 원본이라도 다음 층으로 넘길 수 있고, 역전파 때도 기울기가 돌아갈 길이 남습니다.

현업에서 깊은 모델이 버티는 이유를 한 문장으로 줄이면 대개 잔차입니다. 저는 이 구조를 볼 때마다 "모델이 새로 배운 것만 얹고, 기존 표현은 버리지 않는다"고 이해했습니다. 디버깅할 때도 도움이 됩니다. 블록이 망가져도 입력이 완전히 증발하지는 않기 때문입니다.

## LayerNorm — Pre-norm vs Post-norm

원조 트랜스포머는 서브레이어 뒤에 LayerNorm을 두는 Post-norm이었습니다. GPT-2 이후 계열에서는 앞에 두는 Pre-norm이 사실상 표준이 됐습니다. 깊이가 늘어날수록 학습이 더 안정적이었기 때문입니다.

이번 시리즈도 Pre-norm으로 갑니다. 입력을 먼저 정규화하고, 그 결과를 어텐션과 FFN에 넣은 뒤, 마지막에 잔차를 더합니다. 코드 한 줄 차이처럼 보여도 학습감은 꽤 다릅니다.

![Pre-norm과 post-norm LayerNorm 배치 차이](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/04/04-01-layernorm-pre-norm-vs-post-norm.ko.png)

*Pre-norm과 post-norm LayerNorm 배치 차이*
## Block 한 개 PyTorch 구현 — 25줄

이제 `model.py`에 블록을 붙입니다. 지난 글의 `CausalSelfAttention`을 그대로 쓰고, 오늘 만든 `FeedForward`와 `LayerNorm` 두 개를 더하면 끝입니다.

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

구조를 말로 풀면 더 단순합니다. 정규화하고, 어텐션 돌리고, 원본에 더합니다. 한 번 더 정규화하고, MLP 돌리고, 다시 더합니다. `CausalSelfAttention.forward()`가 이제 residual stream 텐서만 돌려주기 때문에 이 residual addition도 끝까지 모양이 맞게 흘러갑니다.

## 같은 블록을 N번 쌓는다

트랜스포머의 깊이는 대단한 새 부품으로 늘지 않습니다. 같은 블록을 여러 번 쌓습니다. 그래서 구현도 `nn.ModuleList` 한 줄이면 됩니다.

```python
self.blocks = nn.ModuleList([Block(config) for _ in range(config.n_layer)])

for block in self.blocks:
    x = block(x)
```

이 반복이 쌓이면서 초반 블록은 지역 문맥을 다듬고, 뒤쪽 블록은 더 긴 문맥 관계를 정리합니다. 작은 char-level 모델도 몇 층만 쌓아 보면 한 글자 예측기가 아니라 문맥 모델처럼 움직이기 시작합니다.

## 파라미터 수 계산 — 어디에 가중치가 몰리나

블록 하나의 대략적인 비용은 식으로도 금방 보입니다. 어텐션은 `Q`, `K`, `V`, 출력 projection을 합쳐 대략 `4C²` 규모이고, FFN은 `C→4C→C`라서 대략 `8C²`입니다. 숫자만 봐도 FFN이 더 큽니다.

우리 설정 `C=128`에서는 블록 하나당 어텐션이 약 6.6만 개, FFN이 약 13.1만 개 파라미터를 씁니다. 여기에 LayerNorm 두 개를 얹으면 블록 하나가 약 19.8만 개입니다. 여섯 층이면 118만 개 정도가 블록 쪽에 몰립니다. 작은 GPT를 만져 봐도 "모델 대부분은 FFN이 먹는다"는 감각이 바로 잡힙니다.

## 다음 글 예고

이제 블록이라는 벽돌은 준비됐습니다. 다음 글에서는 임베딩, `N`개 블록, 마지막 LayerNorm, LM head를 한 클래스에 묶어 `GPT(nn.Module)`를 완성하겠습니다. forward 한 번에 logits와 loss까지 나오도록 마무리할 차례입니다.

<!-- a-grade-example:begin -->

## 시니어 엔지니어는 이렇게 생각합니다

- **Pre-LN 권장** — Pre-LN이 깊은 네트워크에서 학습 안정성에 유리합니다.
- **Residual 보존** — 잔차 경로를 깨지 않게 모듈을 배치합니다.
- **FFN 폭** — 보통 4·d 폭이 합리적 시작점입니다.
- **드롭아웃 위치** — 잔차 합산 직전 드롭아웃이 표준입니다.
- **정합성 테스트** — 단일 블록 forward를 단위 테스트로 고정합니다.

## 체크리스트

- [ ] 블록 한 개를 25줄로 구현하고 forward shape를 검증했다.
- [ ] pre-norm 구조의 데이터 흐름을 다이어그램으로 그릴 수 있다.
- [ ] N개 블록을 쌓을 때 파라미터 수가 어떻게 늘어나는지 계산했다.
- [ ] FeedForward와 attention의 파라미터 비중을 비교했다.

<!-- a-grade-example:end -->

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

## 참고 자료

- [nanoGPT model.py](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [On Layer Normalization in the Transformer Architecture](https://arxiv.org/abs/2002.04745)
- [Language Models are Unsupervised Multitask Learners (GPT-2)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
- [PyTorch nn.LayerNorm](https://pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html)

Tags: LLM, PyTorch, Transformer, Tutorial

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
