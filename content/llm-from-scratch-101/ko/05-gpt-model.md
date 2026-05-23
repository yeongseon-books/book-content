---
title: "LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성"
series: llm-from-scratch-101
episode: 5
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
seo_description: 앞선 세 편에서 입력부와 어텐션을 만들었고, 지난 글에서는 블록 하나를 세웠습니다. 여기까지 오면 부품은 거의 다 모인 셈입니다.
---

# LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성

이 글은 LLM from Scratch 101 시리즈의 다섯 번째 글입니다.

지금까지 우리는 토크나이저, 임베딩, 어텐션, 트랜스포머 블록을 차례로 만들었습니다. 이 시점에 오면 흩어져 있던 부품이 거의 다 갖춰집니다. 남은 일은 생각보다 단순합니다. 그 부품들을 하나의 `GPT(nn.Module)` 클래스 안에 질서 있게 조립하는 일입니다.

이 단계가 중요한 이유는 구조가 한 번에 보이기 시작하기 때문입니다. 토큰과 위치 임베딩이 입력을 만들고, 여러 블록이 그 표현을 다듬고, 마지막 LayerNorm과 LM head가 다음 토큰 분포를 출력합니다. GPT라는 이름이 크게 들려도, 구현 수준에서는 꽤 직선적인 흐름입니다.

물론 실제 코드에는 몇 가지 중요한 디테일이 있습니다. 입력 길이 검증, loss 계산을 위한 reshape, 그리고 embedding 행렬과 출력 projection을 공유하는 weight tying 같은 장치가 들어가야 모델이 깔끔하고 실용적인 형태가 됩니다.

이번 글에서는 지금까지 만든 구성 요소를 하나의 forward 패스로 연결하고, logits와 loss를 동시에 돌려주는 GPT 클래스를 완성하겠습니다. 여기서부터 모델은 학습 가능한 완성형 틀을 갖추게 됩니다.

이제 전체 모델 껍질이 완성되면 다음 글에서는 학습 루프를 붙여 실제로 TinyShakespeare를 학습시킬 수 있습니다.

![LLM from Scratch 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/05/05-01-the-forward-pass-at-a-glance.ko.png)
*LLM from Scratch 101 5장 흐름 개요*

## 먼저 던지는 질문

- GPT 클래스는 어떤 순서로 부품을 호출할까요?
- token embedding과 LM head를 묶는 weight tying은 왜 유용할까요?
- cross-entropy loss는 왜 한 줄 reshape로 계산할 수 있을까요?

## 왜 이 글이 중요한가

개별 모듈을 이해하는 것과 완성된 모델 클래스를 조립하는 것은 다른 문제입니다. 앞 단계에서는 attention, FFN, residual을 각각 이해했다면, 여기서는 그 모든 것이 하나의 residual stream 안에서 어떻게 이어지는지 확인해야 합니다. 이 연결부를 이해해야 이후 학습 루프와 생성 루프가 자연스럽게 붙습니다.

또한 이 단계는 구현 감각을 크게 올려 줍니다. 블록을 여러 층 쌓아도 입력과 출력 shape가 일관되게 유지되어야 하고, loss 계산을 위해 logits와 targets를 flatten하는 이유도 여기서 명확해집니다. 모델 클래스의 forward를 직접 읽으면 LLM 내부 파이프라인이 훨씬 덜 추상적으로 보입니다.

실무적으로도 중요합니다. weight tying 같은 작은 최적화, `block_size` 검증, config 중앙화는 모두 이후 실험 반복과 디버깅 속도에 영향을 줍니다. 큰 프레임워크에서는 숨어 있는 부분이지만, 직접 구현에서는 이런 결정을 명시적으로 해야 합니다.

## 핵심 관점

GPT를 거대한 블랙박스로 보면 클래스 전체가 복잡하게 느껴질 수 있습니다. 하지만 더 실용적인 관점은 이렇습니다. **GPT 클래스는 새로운 알고리즘이라기보다, 이미 만든 부품들을 올바른 순서로 연결하는 조립 코드**입니다.

입력은 `(B, T)` 토큰 ID입니다. 여기에 token embedding과 position embedding을 더해 `(B, T, C)` residual stream을 만들고, 이 텐서를 여러 블록에 차례대로 통과시킵니다. 마지막에 LayerNorm을 적용한 뒤 LM head로 vocab 차원에 투사하면 `(B, T, vocab_size)` logits가 나옵니다.

이 구조의 장점은 책임이 명확하다는 데 있습니다. 임베딩은 입력 표현을 만들고, 블록은 표현을 깊게 다듬고, LM head는 다음 토큰 분포를 읽습니다. 따라서 모델 전체를 이해하려면 새로운 개념보다 이 연결 순서를 정확히 보는 것이 중요합니다.

> 이번 글의 핵심은 간단합니다. GPT는 임베딩 위에 블록을 쌓고, 마지막 hidden state를 다음 토큰 분포로 읽어 내는 자기회귀 모델입니다.

## 핵심 개념

### 전체 forward 패스는 한 줄 흐름으로 요약할 수 있습니다

입력은 `(B, T)` 토큰 ID 텐서입니다. 여기에 token embedding과 position embedding을 더하고, `n_layer`개의 블록을 순서대로 통과시킵니다. 마지막 `ln_f`를 거친 뒤 `lm_head`로 vocab 차원에 투사하면 각 위치의 다음 토큰 logits가 만들어집니다.

이 그림을 읽을 때는 새로운 계산보다 residual stream이 어떻게 유지되는지에 집중하면 좋습니다. 블록을 여러 번 지나도 텐서의 기본 shape는 `(B, T, C)`로 유지되고, 마지막에만 vocab 차원으로 확장됩니다.

### GPT 클래스 자체는 surprisingly 직선적입니다

이제 지금까지 만든 부품을 하나의 클래스에 넣습니다. 아래 코드는 시리즈의 `model.py`를 완성하는 핵심입니다.

```python
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F

@dataclass
class GPTConfig:
    vocab_size: int = 65
    n_layer: int = 6
    n_head: int = 4
    n_embd: int = 128
    block_size: int = 64

class GPT(nn.Module):
    def __init__(self, config: GPTConfig) -> None:
        super().__init__()
        self.config = config
        self.token_emb = nn.Embedding(config.vocab_size, config.n_embd)
        self.pos_emb = nn.Embedding(config.block_size, config.n_embd)
        self.blocks = nn.ModuleList([Block(config) for _ in range(config.n_layer)])
        self.ln_f = nn.LayerNorm(config.n_embd)
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)
        self.lm_head.weight = self.token_emb.weight

    def forward(
        self, idx: torch.Tensor, targets: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        b, t = idx.shape
        if t > self.config.block_size:
            raise ValueError(f"cannot forward sequence of length {t}")

        pos = torch.arange(t, device=idx.device)
        tok_emb = self.token_emb(idx)
        pos_emb = self.pos_emb(pos)
        x = tok_emb + pos_emb

        for block in self.blocks:
            x = block(x)

        x = self.ln_f(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(b * t, self.config.vocab_size),
                targets.view(b * t),
            )

        return logits, loss
```

구조를 읽을 때는 입력 길이 검사, residual stream 생성, 블록 반복, 최종 정규화, logits projection, optional loss 계산의 여섯 단계로 나누면 명확합니다. 각 블록이 `(B, T, C)`를 그대로 돌려주기 때문에 전체 forward 패스도 shape 일관성을 유지합니다.

### weight tying은 작지만 의미 있는 최적화입니다

`self.lm_head.weight = self.token_emb.weight` 한 줄은 input embedding과 output projection이 같은 가중치를 공유하게 만듭니다. 직관적으로도 그럴듯합니다. 어떤 문자를 읽기 위해 쓰는 벡터 공간과, 다음 문자를 점수화할 때 쓰는 공간이 완전히 따로 놀 필요는 없기 때문입니다.

이 기법은 파라미터 수를 줄이는 동시에 작은 모델에서 학습 안정성을 돕는 경우가 많습니다. 거대한 마법은 아니지만, 직접 모델을 조립할 때는 이런 관례가 왜 널리 쓰이는지 이해하고 넘어가는 편이 좋습니다.

### cross-entropy 한 줄은 flatten 규칙을 이해하면 자연스럽습니다

language modeling의 logits는 `(B, T, vocab_size)`이고 targets는 `(B, T)`입니다. `F.cross_entropy`는 클래스 차원이 마지막인 2D 입력을 다루기 편하므로, 이를 `(B*T, vocab_size)`와 `(B*T,)`로 펼쳐서 계산합니다.

이 reshape를 이해하면 이후 학습 루프가 매우 단순해집니다. loss 함수 입장에서는 배치와 시퀀스의 경계가 중요하지 않고, 결국 `N`개의 예측과 `N`개의 정답만 보게 됩니다.

### 파라미터 수를 직접 세어 보면 모델 규모가 현실적으로 느껴집니다

이번 설정은 `vocab_size=65`, `n_layer=6`, `n_head=4`, `n_embd=128`, `block_size=64`입니다. 체감상 GPT라는 이름 때문에 거대하게 느껴질 수 있지만, 실제로는 소형 모델입니다. weight tying을 포함하면 전체 파라미터 수는 약 1,204,096개 수준입니다.

```python
config = GPTConfig()
model = GPT(config)
num_params = sum(p.numel() for p in model.parameters())
print(f"params: {num_params:,}")
```

이 숫자를 직접 출력해 보면 임베딩, 블록, 최종 LayerNorm이 각각 얼마나 차지하는지 감각이 생깁니다. 특히 대부분의 용량이 블록에 집중된다는 점이 더 분명해집니다.

### weight tying이 파라미터를 절약하는 원리

weight tying은 입력 임베딩 행렬과 출력 projection 행렬을 물리적으로 같은 텐서로 만드는 기법입니다. 임베딩은 `(vocab_size, n_embd)` 형태이고, 출력 projection은 `(n_embd, vocab_size)` 형태입니다. 이 둘을 공유하면 `vocab_size × n_embd`만큼의 파라미터를 아낄 수 있습니다.

이번 설정에서는 `65 × 128 = 8,320`개를 절약하는데, 전체 1.2M에서 비율은 작습니다. 하지만 vocab_size가 수만 이상인 실제 모델에서는 수백 MB 단위 절감이 되므로 표준 기법으로 자리 잡았습니다.

```python
# weight tying 구현 핵심 한 줄
self.lm_head.weight = self.token_embedding.weight
```

이 한 줄로 두 행렬이 같은 메모리를 참조하게 되어, 역전파 시 두 위치의 gradient가 자동으로 합산됩니다.

### 학습 전 sanity check는 loss 값으로 확인할 수 있습니다

랜덤 초기화된 모델이라면 65개 클래스에 대해 거의 균등한 추측을 해야 하므로, 초기 loss는 대략 `ln(65)`인 4.17 근처가 나와야 합니다. 이 값은 구현이 크게 틀리지 않았는지 보는 매우 좋은 기준입니다.

```python
import torch

config = GPTConfig()
model = GPT(config)
idx = torch.randint(0, config.vocab_size, (4, config.block_size))
targets = torch.randint(0, config.vocab_size, (4, config.block_size))
logits, loss = model(idx, targets)

print(logits.shape)
print(loss.item())
```

loss가 4점대 초반이면 대체로 정상입니다. 반대로 `nan`이나 터무니없이 큰 수가 나오면 block 연결, mask 범위, reshape, logits 차원 등을 다시 봐야 합니다. 작은 sanity check 하나가 뒤 시간을 크게 줄여 줍니다.

### `GPTConfig`는 작은 모델일수록 더 유용합니다

하이퍼파라미터를 코드 곳곳에 흩뿌리면 작은 예제도 금방 관리가 어려워집니다. `GPTConfig` dataclass는 모델 차원, 레이어 수, head 수, context 길이를 한곳에 모아 전달하는 역할을 합니다. 이후 `train.py`나 `generate.py`로 확장할 때도 같은 config를 재사용할 수 있습니다.

이번 시리즈의 기본 설정은 CPU나 보급형 GPU에서도 TinyShakespeare를 돌릴 수 있게 보수적으로 잡혀 있습니다. 작은 수치지만 구조는 GPT와 동일합니다. 입문 단계에서는 거대한 모델보다 추적 가능한 모델이 더 좋은 교재입니다.

## 흔히 헷갈리는 지점

- GPT 클래스에 복잡한 새 알고리즘이 숨어 있다고 느끼기 쉽지만, 핵심은 이미 만든 부품들의 조립입니다.
- weight tying을 선택적 장식으로 보기 쉽지만, 파라미터 절약과 안정성 면에서 실용적입니다.
- loss 계산의 flatten을 꼼수처럼 느끼기 쉽지만, class dimension에 맞춘 표준 처리입니다.
- `block_size` 검증을 빼도 되겠다고 생각하기 쉽지만, learned positional embedding은 최대 길이에 묶여 있습니다.
- config를 단순 편의성으로 보지만, 실험 반복과 체크포인트 재현성에 직접 영향을 줍니다.

## 운영 체크리스트

- [ ] forward 패스를 임베딩 → 블록 반복 → `ln_f` → `lm_head` 순서로 설명할 수 있는가
- [ ] `self.lm_head.weight = self.token_emb.weight`가 하는 일을 이해했는가
- [ ] logits와 targets를 왜 `(B*T, ...)` 형태로 펼치는지 설명할 수 있는가
- [ ] 랜덤 초기화 시 loss가 4.17 근처여야 한다는 sanity check를 실행했는가
- [ ] `GPTConfig` 하나만 바꿔 모델 차원과 컨텍스트 길이를 제어할 수 있는 구조인지 확인했는가

## 모델 조립 후 바로 보는 구조 검증 리포트

`GPT` 클래스를 만든 직후에는 학습을 돌리기 전에 구조 검증 리포트를 한 번 출력하는 편이 좋습니다. 특히 파라미터 수, 모듈별 비중, forward shape 일관성을 한 번에 확인하면 이후 문제를 크게 줄일 수 있습니다.

```python
def report_model(model: GPT) -> None:
    total = sum(p.numel() for p in model.parameters())
    emb = sum(p.numel() for n, p in model.named_parameters() if "token_emb" in n or "pos_emb" in n)
    blocks = sum(p.numel() for n, p in model.named_parameters() if "blocks" in n)
    head = sum(p.numel() for n, p in model.named_parameters() if "lm_head" in n)

    print(f"total  : {total:,}")
    print(f"emb    : {emb:,} ({emb/total:.2%})")
    print(f"blocks : {blocks:,} ({blocks/total:.2%})")
    print(f"head   : {head:,} ({head/total:.2%})")
```

예시 출력은 다음과 비슷합니다.

```text
total  : 1,204,096
emb    :   16,512 (1.37%)
blocks : 1,185,792 (98.48%)
head   :    8,320 (0.69%)
```

이 숫자는 "어디를 최적화해야 효과가 큰가"를 바로 알려 줍니다. 작은 char-level 모델에서는 임베딩보다 블록이 거의 모든 용량을 차지하므로, 구조 실험의 중심도 자연스럽게 블록 파라미터로 이동합니다.

### forward 계약 테스트를 파일로 분리해 두면 안전합니다

```python
def test_forward_contract() -> None:
    cfg = GPTConfig(vocab_size=65, block_size=64, n_layer=2, n_head=2, n_embd=32)
    model = GPT(cfg)

    idx = torch.randint(0, cfg.vocab_size, (3, 16))
    tgt = torch.randint(0, cfg.vocab_size, (3, 16))
    logits, loss = model(idx, tgt)

    assert logits.shape == (3, 16, cfg.vocab_size)
    assert loss is not None and torch.isfinite(loss)
```

이 테스트 한 개만 있어도 리팩터링 중 실수 대부분을 막을 수 있습니다. 특히 반환 타입 `(logits, loss)` 계약이 깨지는 경우를 조기에 잡아 줍니다.

### weight tying 적용 전후 비교

| 항목 | 미적용 | 적용 |
| --- | --- | --- |
| 파라미터 수 | 더 큼 | 더 작음 |
| 입력/출력 표현 공유 | 없음 | 있음 |
| 소형 모델 안정성 | 상황 의존 | 일반적으로 유리한 편 |
| 구현 복잡도 | 낮음 | 매우 낮음(한 줄) |

weight tying은 작은 한 줄이지만, 모델 파라미터 구조와 일반화 특성에 의미 있는 영향을 줍니다. 따라서 "왜 이 한 줄이 있는지"를 문서로 남겨 두는 것이 좋습니다.

### 모델 계층별 활성값 로깅 예시

```python
@torch.no_grad()
def log_activation_norms(model: GPT, idx: torch.Tensor) -> None:
    x = model.token_emb(idx) + model.pos_emb(torch.arange(idx.size(1), device=idx.device))
    print("emb_norm", float(x.norm().item()))
    for i, block in enumerate(model.blocks):
        x = block(x)
        print(f"block_{i}_norm", float(x.norm().item()))
    x = model.ln_f(x)
    print("ln_f_norm", float(x.norm().item()))
```

학습 전/후 이 로그를 비교하면 블록이 표현을 어떻게 누적 변환하는지 감각을 얻을 수 있습니다. 숫자가 단조 증가하거나 급락하면 초기화, lr, norm 동작을 함께 점검해야 합니다.

## GPT 조립 단계에서 설계 결정을 문서화해야 하는 이유

`GPT(nn.Module)`가 완성되면 코드가 깔끔해 보이지만, 실제 협업에서는 "왜 이렇게 조립했는가"가 남지 않으면 유지보수가 급격히 어려워집니다. 특히 소형 프로젝트가 커질 때는 설계 의사결정을 짧게라도 문서화해 두는 것이 장기 비용을 줄입니다.

### 입력/출력 계약을 명시합니다

모델 forward 입력 shape, dtype, 허용 길이, 선택적 targets 규칙을 함수 docstring이나 설계 노트에 남겨야 합니다. 이 계약이 모호하면 추론 코드와 학습 코드가 서로 다른 전제를 갖게 되고, 버그가 테스트를 통과한 채 프로덕션으로 넘어갑니다.

### Weight tying의 장단점을 기록합니다

임베딩과 LM head를 공유하면 파라미터 수를 줄이고 일반화에 이점이 생길 수 있습니다. 반면 특정 실험에서는 표현력 제한으로 작동할 수도 있습니다. 중요한 것은 "무조건 사용"이 아니라, 현재 실험에서 왜 선택했는지 근거를 남기는 것입니다.

### 손실 계산 경로를 단순하게 유지합니다

loss 계산을 모델 내부에 둘지 외부 학습 루프로 뺄지는 팀마다 다릅니다. 교육용/연구용 코드에서는 내부 계산이 읽기 쉽지만, 운영 파이프라인에서는 외부로 분리해 모니터링 지표를 세분화하기 쉬운 경우가 많습니다. 어느 쪽이든 기준을 한 번 정하면 시리즈 전체에서 일관되게 유지해야 합니다.

### 모델 메타데이터를 체크포인트에 포함합니다

체크포인트에는 단순 state dict 외에도 최소 메타데이터를 넣는 편이 좋습니다.

- 아키텍처 하이퍼파라미터(`n_layer`, `n_head`, `n_embd`, `block_size`)
- 토크나이저 버전 또는 해시
- 학습 데이터 버전 ID
- 코드 커밋 SHA

이 정보가 있으면 "같은 모델"의 정의가 명확해지고, 재현성과 비교 실험 품질이 크게 올라갑니다.

## 조립 이후에 바로 해 볼 검증 실험

모델 클래스를 완성한 직후에는 거창한 학습보다 짧은 스모크 테스트가 먼저입니다. 랜덤 입력으로 forward를 여러 번 돌려 shape와 loss 계산이 안정적인지 확인하고, 아주 작은 데이터셋으로 200~500 step만 학습해 손실이 실제로 감소하는지 봅니다. 이 두 단계가 통과되면 아키텍처 결합 오류 가능성이 크게 줄어듭니다.

또한 동일 시드에서 재실행했을 때 초반 손실 곡선이 유사한지 확인하면, 재현성 문제를 조기에 발견할 수 있습니다.

## 유지보수 관점 정리

GPT 클래스는 "한 번 완성"보다 "반복 확장"을 전제로 설계해야 합니다. 하이퍼파라미터 추가, 새로운 헤드 실험, 컨텍스트 길이 변경이 들어와도 인터페이스가 흔들리지 않게 유지하면, 팀 단위 개발에서 생산성이 크게 올라갑니다.

그래서 조립 단계에서의 단순함은 미학이 아니라 운영 전략입니다.

## 현업에서 자주 받는 질문

### 작은 모델에서도 이 단계를 엄격하게 지켜야 하나요?

네, 오히려 작은 모델일수록 기본 계약을 엄격하게 지켜야 합니다. 모델 용량이 작을수록 입력 노이즈와 구현 불일치의 영향을 크게 받기 때문입니다. 재현 가능한 실험 단위를 먼저 확보하면, 모델 크기 확장 이전에도 품질 개선 속도가 올라갑니다.

### 실험 속도와 품질 관리가 충돌할 때는 어떻게 하나요?

속도를 높이려면 실험 횟수를 늘리는 것이 아니라 실패 비용을 줄여야 합니다. 설정 파일 고정, 로그 표준화, 체크포인트 메타데이터 저장 같은 장치를 먼저 도입하면, 같은 시간에 더 많은 "유효한" 실험을 수행할 수 있습니다.

### 마지막으로 무엇을 기록해 두면 도움이 되나요?

변경 이유, 기대 효과, 실제 관측 결과를 짧게 남기면 다음 실험의 품질이 올라갑니다. 특히 "왜 이 값을 선택했는가"를 기록하면, 몇 주 뒤에도 의사결정 맥락을 복원할 수 있습니다.

## 결론 메모

조립 단계에서 인터페이스와 메타데이터를 정리해 두면, 이후 학습·추론·배포 단계가 한결 단순해집니다. 결국 좋은 모델 코드는 성능뿐 아니라 운영 흐름까지 함께 설계된 코드입니다.

## 정리

이번 글에서는 지금까지 만든 부품을 하나의 `GPT(nn.Module)` 클래스 안에 조립했습니다. 입력 임베딩, 블록 반복, 최종 정규화, LM head, optional loss 계산까지 연결되면서 모델은 비로소 완전한 forward 패스를 갖게 되었습니다.

또한 weight tying, flatten 기반 cross-entropy, `GPTConfig` 중앙화 같은 구현 디테일이 왜 중요한지도 살펴봤습니다. 이런 디테일이 있어야 코드가 짧아도 재현 가능하고, 다음 단계로 무리 없이 확장됩니다.

이제 다음 글에서는 이 모델에 학습 루프를 붙입니다. 즉, 미니배치를 반복해서 넣고, loss를 계산하고, 역전파와 optimizer step으로 실제로 가중치를 바꾸는 과정을 시작합니다.

## 처음 질문으로 돌아가기

- **GPT 클래스는 어떤 순서로 부품을 호출할까요?**
  - 입력 `(B, T)`는 먼저 `token_emb(idx)`와 `pos_emb(pos)`를 더해 residual stream `x`를 만들고, 그다음 `for block in self.blocks: x = block(x)`를 거쳐 `ln_f`와 `lm_head`로 logits가 됩니다. 즉, 임베딩 → 블록 반복 → 최종 정규화 → vocab projection 순서가 GPT forward의 뼈대입니다.
- **token embedding과 LM head를 묶는 weight tying은 왜 유용할까요?**
  - `self.lm_head.weight = self.token_emb.weight`로 입력 임베딩과 출력 projection이 같은 벡터 공간을 공유하면 파라미터 수를 줄이고 작은 모델의 학습도 더 단정해집니다. 이번 설정에서는 절약량이 작아 보여도, vocab이 커질수록 이 한 줄의 효과가 크게 커집니다.
- **cross-entropy loss는 왜 한 줄 reshape로 계산할 수 있을까요?**
  - 언어 모델 입장에서는 배치와 시퀀스 차원을 따로 볼 필요 없이 `(예측, 정답)` 쌍들의 모음만 있으면 되기 때문입니다. 그래서 `(B, T, vocab_size)` logits를 `logits.view(b * t, vocab_size)`로, `(B, T)` targets를 `targets.view(b * t)`로 펴서 `F.cross_entropy`에 그대로 넣을 수 있었습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치](./02-embedding.md)
- [LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기](./03-attention.md)
- [LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위](./04-transformer-block.md)
- **LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성 (현재 글)**
- LLM from Scratch 101 (6/9): 기울기로 배우기 (예정)
- LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기 (예정)
- LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기 (예정)
- LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [nanoGPT repository](https://github.com/karpathy/nanoGPT)
- [Using the Output Embedding to Improve Language Models](https://arxiv.org/abs/1608.05859)
- [PyTorch cross_entropy](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
- [Language Models are Unsupervised Multitask Learners (GPT-2)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)

### 관련 시리즈

- [LangChain 101 — 실전 체인 조립](../../langchain-101/ko/06-putting-it-together.md)
- [AI Agent 101 — Agent Workflow 설계](../../ai-agent-101/ko/04-agent-workflow-design.md)
- [LLM API 프로덕션 101 — 구조화 출력](../../llm-api-production-101/ko/01-structured-output.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/05-gpt-model)

Tags: LLM, PyTorch, Transformer, Tutorial
