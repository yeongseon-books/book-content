---
title: LLM 파인튜닝 입문
series: llm-finetuning-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Fine-tuning
- LoRA
- LLM
- PEFT
- Python
- GPT-2
last_reviewed: '2026-05-12'
seo_description: LLM 파인튜닝의 핵심인 LoRA의 원리를 풀 파인튜닝과 비교하고 학습 파라미터 수 계산을 통해 산술적 감각을 익힙니다.
---

# LLM 파인튜닝 입문

파인튜닝은 단순히 모델을 한 번 더 학습시키는 작업처럼 보이지만, 실제 출발점은 무엇을 바꾸고 무엇을 그대로 둘지 정하는 일입니다. 이 글은 LLM Finetuning 101 시리즈의 첫 번째 글입니다. 여기서는 그 결정을 세 가지 변수로 나눠 보고, 이후 글들을 흔들리지 않게 받쳐 줄 계산 감각을 먼저 맞추겠습니다.

처음부터 큰 모델과 GPU 실험으로 들어가면 학습률, 데이터셋 형식, 어댑터 랭크가 한꺼번에 흔들립니다. 그러면 무엇이 결과를 바꿨는지 설명하기 어려워집니다. 1편의 목적은 모델 실행을 잠시 미루고, 왜 LoRA가 싸고 빠른지, 언제 이 선택이 합리적인지를 숫자로 먼저 이해하는 데 있습니다.

## 이 글에서 다룰 문제

![이 글에서 다룰 문제](../../../assets/llm-finetuning-101/01/01-01-questions-this-post-answers.ko.png)

*이 글에서 다룰 문제*

- LoRA가 풀 파인튜닝보다 훨씬 가벼운 이유를 어떻게 계산할 수 있을까요?
- 프롬프트로 해결할 수 있는 문제와 파인튜닝이 필요한 문제를 어떻게 구분할 수 있을까요?
- GPU 없이도 1편에서 무엇을 검증할 수 있을까요?
- LoRA는 모델 크기를 줄이는 것일까요, 아니면 학습 가능한 파라미터 수를 줄이는 것일까요?

> 풀 파인튜닝이 건물을 통째로 다시 짓는 일이라면, LoRA는 하중을 받는 몇 개 기둥 옆에 보강재를 덧대는 일에 가깝습니다.

예제 코드: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/en/01-intro)

## 왜 이 글이 중요한가

LLM 파인튜닝은 반드시 GPU 실습부터 시작해야 하는 주제가 아닙니다. 오히려 먼저 필요한 것은 산술 감각입니다. LoRA가 실제로 얼마나 적은 파라미터만 학습하는지, 그 비율이 왜 데이터셋 규모와 학습 시간 추정에까지 연결되는지 이해해야 이후 글들이 한 덩어리로 보입니다.

이 글에서 한 번 계산해 둔 비율은 뒤에서 계속 다시 등장합니다. 3편에서는 `LoraConfig(r=8)`를 고를 때, 4편에서는 학습 시간을 가늠할 때, 6편에서는 베이스 모델과 어댑터를 분리 배포할 때 같은 감각이 그대로 이어집니다. 즉 1편은 이 시리즈의 수학적 기준점을 만드는 글입니다.

## 멘탈 모델

파인튜닝 실험은 결국 세 가지 변수를 어떻게 나눌지 결정하는 일입니다.

```text
                  ┌───────────────────────────────────────┐
                  │ ① What are we changing? (target params)│
                  ├───────────────────────────────────────┤
one fine-tune  =  │ ② With what? (dataset)                 │
                  ├───────────────────────────────────────┤
                  │ ③ How? (optimizer)                     │
                  └───────────────────────────────────────┘
```

풀 파인튜닝은 ①을 "전부"로 둡니다. 그러면 ②와 ③도 함께 무거워집니다. LoRA는 ①을 "일부 선형 레이어 옆에 붙는 작은 어댑터"로 좁힙니다. 그 결과 적은 데이터셋으로도 실험이 가능해지고, 옵티마이저 상태도 작아집니다. 같은 데이터와 같은 학습률을 써도 ①을 어떻게 정의했는지에 따라 GPU 메모리 요구량이 10배 가까이 차이 날 수 있습니다.

## 핵심 개념

| 용어 | 의미 |
| --- | --- |
| Full fine-tuning | 베이스 모델의 모든 가중치를 업데이트합니다. 옵티마이저 상태까지 포함하면 피크 메모리는 모델 크기의 4배 이상이 되기 쉽습니다. |
| LoRA | 베이스 가중치는 고정하고 두 개의 저랭크 행렬 `A`, `B`만 학습합니다. 추가 파라미터는 보통 1~3% 수준입니다. |
| Rank (`r`) | LoRA 어댑터의 중간 차원입니다. 클수록 표현력은 늘지만 학습 파라미터 수도 선형으로 증가합니다. |
| Target module | LoRA를 주입하는 선형 레이어입니다. `q_proj`, `v_proj` 같은 이름으로 지정합니다. |
| Adapter weight | 학습 후 따로 저장하고 배포하는 작은 가중치 파일입니다. 추론 시 베이스 모델과 함께 사용합니다. |

## Before vs. After

**Before**

"GPT-4 응답 톤이 좀 이상한데, 모델을 다시 학습해야 하나요?"라는 질문을 받으면 빠르게 답하지 못합니다. 풀 파인튜닝은 비싸고 LoRA는 싸다는 정도만 흐릿하게 기억나고, 회의는 길어집니다.

**After**

1편을 읽고 나면 최소한 아래 표를 바로 꺼낼 수 있습니다.

```text
Model size                       124M params (GPT-2 small class)
Full fine-tuning trainable        ≈ 124M (100%)
LoRA(r=8) trainable               ≈ 1.8M (≈ 1.5%)
GPU memory (incl. optimizer)      Full: ~5GB / LoRA: ~1.5GB
Adapter file size                 ~7MB (one per domain)
```

이 표가 있으면 "응답 톤만 조정하고 싶다"는 요구는 LoRA로, "모델이 모르는 사실 자체를 넣어야 한다"는 요구는 풀 파인튜닝이나 RAG로 자연스럽게 갈라집니다.

## 먼저 이해해야 할 것

![베이스 가중치와 학습 대상 경계](../../../assets/llm-finetuning-101/01/01-02-what-to-understand-first.ko.png)

*베이스 가중치와 학습 대상 경계*

파인튜닝에서 가장 먼저 놓치기 쉬운 지점은 **무엇을 학습 대상으로 삼는가**입니다. 풀 파인튜닝은 기존 가중치 전체를 업데이트하므로 메모리와 옵티마이저 상태가 같이 불어납니다. LoRA는 기존 가중치를 얼려 두고 저랭크 행렬 두 개만 추가합니다. 그래서 비용을 이야기할 때는 전체 모델 크기보다 **학습 가능한 파라미터 수**를 따로 봐야 합니다.

![먼저 이해해야 할 것](../../../assets/llm-finetuning-101/01/01-01-what-to-understand-first.ko.png)

*먼저 이해해야 할 것*

## 단계별 설명

### 1단계 — 트랜스포머 구조를 데이터 클래스로 표현합니다

```python
from dataclasses import dataclass

@dataclass
class TransformerShape:
    hidden_size: int
    intermediate_size: int
    num_layers: int
```

### 2단계 — 선형 레이어 파라미터 수를 셉니다

```python
def total_linear_params(shape: TransformerShape) -> int:
    return shape.num_layers * (
        4 * shape.hidden_size * shape.hidden_size
        + 2 * shape.hidden_size * shape.intermediate_size
    )
```

여기서는 어텐션의 네 개 projection(Q, K, V, O)과 MLP의 두 개 projection(up, down)만 합산합니다. 임베딩과 레이어 정규화는 일부러 제외해서, LoRA가 어디에 끼어드는지 눈에 잘 보이게 합니다.

### 3단계 — LoRA 어댑터 파라미터 수를 셉니다

```python
def lora_params_per_layer(hidden_size: int, intermediate_size: int, rank: int) -> int:
    attention = 4 * rank * (hidden_size + hidden_size)
    mlp = rank * (hidden_size + intermediate_size) + rank * (intermediate_size + hidden_size)
    return attention + mlp
```

LoRA 어댑터는 `A: (in, r)`와 `B: (r, out)` 두 행렬로 이루어집니다. 두 행렬의 곱은 원래 가중치와 같은 모양을 만들지만, 학습 파라미터 수는 `r * (in + out)`만 필요합니다. `r`이 작을수록 절감 폭이 커지는 이유가 여기에 있습니다.

### 4단계 — 두 수의 비율을 비교합니다

```python
shape = TransformerShape(hidden_size=768, intermediate_size=3072, num_layers=12)
rank = 8
base_linear_params = total_linear_params(shape)
lora_params = shape.num_layers * lora_params_per_layer(
    shape.hidden_size, shape.intermediate_size, rank
)
print(base_linear_params, lora_params)
print(f"ratio = {lora_params / base_linear_params:.4%}")
```

실행하면 비율이 약 1.5%로 나옵니다. `rank`를 16, 32로 바꿔 보면 수가 어떻게 커지는지 바로 체감할 수 있고, 이 감각은 4편에서 학습 시간과 메모리 예산을 잡을 때 다시 도움이 됩니다.

## 이 코드에서 봐야 할 것

![선형 레이어 기준 LoRA 개입 면적](../../../assets/llm-finetuning-101/01/01-03-what-to-notice-in-this-code.ko.png)

*선형 레이어 기준 LoRA 개입 면적*

- `hidden_size=768`, `intermediate_size=3072`, `num_layers=12`는 GPT-2 small 급 구조를 흉내 낸 값입니다.
- 이 스크립트는 전체 모델 파라미터가 아니라 어텐션과 MLP의 선형 레이어를 기준으로 LoRA 비율을 잽니다.
- 여기서 출력한 비율은 3편에서 `LoraConfig(r=8)`를 고를 때 기준점으로 다시 쓰입니다.

## 자주 하는 실수

![문제 유형에 따른 선택 기준](../../../assets/llm-finetuning-101/01/01-04-where-engineers-get-confused.ko.png)

*문제 유형에 따른 선택 기준*

- **모델 크기와 학습 파라미터 수를 혼동하는 실수**: LoRA를 써도 추론 시에는 베이스 모델이 그대로 VRAM에 올라가야 합니다. 베이스 모델 자체가 안 들어가면 LoRA만으로는 해결되지 않습니다. 이 경우에는 양자화와 함께 봐야 합니다.
- **랭크가 클수록 무조건 좋다고 생각하는 실수**: `r=64`나 `r=128`로 키우면 학습 파라미터가 급격히 늘고, 일반화가 오히려 나빠질 수 있습니다. 출발점은 `r=8~16`이 안전합니다.
- **모든 선형 레이어에 LoRA를 붙이는 실수**: `target_modules=["q_proj", "v_proj"]`만으로 충분한 경우가 많습니다. MLP까지 포함하면 학습 파라미터가 두세 배로 늘어납니다.
- **나쁜 데이터를 LoRA가 구해 줄 것이라고 기대하는 실수**: 작은 어댑터라도 잘못된 라벨에는 그대로 과적합합니다. 1편의 계산은 비용 이야기이지, 데이터 품질을 대신하는 이야기가 아닙니다.
- **베이스 모델과 어댑터의 토크나이저를 섞는 실수**: 다른 베이스에서 학습한 어댑터를 가져오면 토큰 정렬이 어긋나 결과가 망가집니다. 어댑터와 베이스는 한 쌍입니다.

## 실무 메모

- **한 줄 의사결정 규칙을 만듭니다**: "스타일 변경은 LoRA, 새로운 사실 주입은 RAG, 도메인 어휘와 형식 학습은 LoRA + 좋은 데이터"처럼 팀이 공유할 규칙을 먼저 적어 둡니다.
- **작은 베이스로 먼저 파이프라인을 검증합니다**: GPT-2 small이나 Phi-2로 먼저 루프를 확인한 뒤 큰 모델로 옮기면 비싼 실수를 줄일 수 있습니다.
- **베이스와 어댑터 해시를 함께 기록합니다**: 6편에서 어댑터를 바꿔 가며 A/B 테스트할 때 필수입니다.
- **랭크 스윕은 좁게 시작합니다**: `r ∈ {4, 8, 16}` 정도만 비교해도 정보가 충분히 나옵니다.

## 체크리스트

- [ ] LoRA가 줄이는 대상이 모델 크기인지, 학습 가능한 파라미터 수인지 구분할 수 있습니다.
- [ ] 랭크가 커질수록 학습 파라미터가 선형으로 증가한다는 점을 이해했습니다.
- [ ] `python main.py`를 실행해 파라미터 계산이 실제로 동작하는지 확인했습니다.
- [ ] 다음 글에서 데이터셋 형식이 왜 중요한지 연결할 수 있습니다.
- [ ] 풀 파인튜닝, LoRA, RAG를 각각 언제 써야 하는지 한 문장으로 설명할 수 있습니다.

## 연습 문제

1. `rank`를 {4, 8, 16, 32, 64}로 바꿔 비율 표를 출력해 보세요. 어느 지점부터 "LoRA는 가볍다"는 말이 약해지나요?
2. 다른 값은 그대로 두고 `intermediate_size`만 4096으로 키워 다시 계산해 보세요. MLP 비중이 큰 모델에서 어텐션에만 LoRA를 붙이는 선택이 왜 더 그럴듯해지는지 설명해 보세요.
3. `target_modules`를 `["q_proj", "v_proj"]`로 제한하는 스위치를 추가해 보세요. 비율이 얼마나 달라지나요? Hugging Face PEFT의 `print_trainable_parameters()` 결과와 비교해 차이가 있으면 이유를 정리해 보세요.

## 정리 · 다음 글

1편의 목적은 파인튜닝을 신비한 GPU 의식처럼 보지 않게 만드는 데 있습니다. 파라미터 계산만 정확히 이해해도 왜 LoRA가 기본값이 되었는지, 어떤 경우에는 풀 파인튜닝을 다시 꺼내야 하는지 설명할 수 있습니다.

다음 글인 2편에서는 데이터셋 준비를 다룹니다. instruction, chat, completion 세 형식을 비교하고, 라벨 마스킹과 `eos_token` 처리가 왜 학습 안정성에 결정적인지 코드로 확인하겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- **LLM 파인튜닝 입문 (현재 글)**
- 데이터셋 준비와 전처리 (예정)
- LoRA 어댑터 구성 (예정)
- 학습 루프와 하이퍼파라미터 (예정)
- 모델 평가 (예정)
- 모델 서빙 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LoRA paper](https://arxiv.org/abs/2106.09685)
- [Hugging Face PEFT documentation](https://huggingface.co/docs/peft)
- [QLoRA paper](https://arxiv.org/abs/2305.14314)
- [GPT-2 model card](https://huggingface.co/gpt2)

Tags: Fine-tuning, LoRA, LLM, Python
