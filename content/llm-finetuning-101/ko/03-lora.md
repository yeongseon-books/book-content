---
title: "LLM Fine-tuning 101 (3/6): LoRA 어댑터 구성"
series: llm-finetuning-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Fine-tuning
- LoRA
- PEFT
- Adapter
- Transformers
- Python
last_reviewed: '2026-05-12'
seo_description: LoRA 어댑터의 랭크, 스케일, 대상 모듈 설정 방법을 설명하고 모델별 명명 규칙 확인을 통한 올바른 배선 검증 실습을 진행합니다.
---

# LLM Fine-tuning 101 (3/6): LoRA 어댑터 구성

LoRA 어댑터는 모델 전체를 갈아엎는 장치가 아니라, 선택한 선형 레이어 옆에 좁은 보정 경로를 덧붙이는 방식입니다. 이 글은 LLM Finetuning 101 시리즈의 세 번째 글입니다. 여기서는 그 구조를 기준으로 랭크, 스케일, 대상 모듈을 어떻게 정해야 하는지 감이 아니라 확인 가능한 기준으로 정리하겠습니다.

3편부터는 실제 모델 객체를 만집니다. 다만 목표는 성능 경쟁이 아니라 **연결이 올바른지 검증하는 것**입니다. `target_modules`에 오타가 하나만 있어도 `print_trainable_parameters()`는 0을 출력하고, 학습은 돌아가지만 손실은 움직이지 않는 가장 난감한 실패가 시작됩니다.

## 먼저 던지는 질문

- `LoraConfig`에서 실제로 이해해야 할 필드는 무엇일까요?
- `target_modules`를 잘못 지정하면 어떤 문제가 생길까요?
- 작은 GPT-2 계열 모델에서는 학습 가능한 파라미터 비율이 얼마나 낮아질까요?

## 큰 그림

![LLM Fine-tuning 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/03/03-02-the-fields-with-real-operational-impact.ko.png)

*LLM Fine-tuning 101 3장 흐름 개요*

## 왜 이 글이 중요한가

3편부터는 실제 모델에 어댑터를 붙입니다. GPU가 없는 환경을 전제로 `sshleifer/tiny-gpt2` 같은 작은 모델을 쓰지만, 이 단계의 목표는 성능이 아니라 **배선 검증**입니다. 학습이 수렴하지 않을 때 데이터 문제인지 어댑터 문제인지 바로 가르려면, 먼저 어댑터가 정말 의도한 위치에 붙었는지 확인해 두어야 합니다.

또 1편에서 손으로 계산한 1.5% 안팎의 감각이 실제 PEFT 출력과 어느 정도 맞는지도 여기서 확인합니다. 이 연결이 맞아야 뒤에서 어떤 베이스 모델을 보더라도 학습 가능 파라미터 비율을 빠르게 추정할 수 있습니다.

## 멘탈 모델

LoRA 어댑터는 아래 구조로 요약할 수 있습니다.

```text
Original forward:  y = W · x

LoRA forward:      y = W · x + (alpha / r) · B · A · x
                          │           │   │
                          │           │   └ rank-r low-rank decomposition
                          │           └ scale factor
                          └ base weight (frozen)
```

- `W`는 고정됩니다. 이 경로로는 그라디언트가 흐르지 않습니다.
- `A: (in, r)`은 보통 가우시안 초기화, `B: (r, out)`은 0 초기화를 사용합니다. 그래서 학습 0단계에서는 `B·A = 0`이고 모델은 베이스와 똑같이 동작합니다.
- 학습이 진행되면서 `B`가 0에서 벗어나고, 그때부터 보정 경로가 실제로 작동합니다.
- `alpha / r`은 보정의 크기를 조절합니다. `alpha = 2 * r`은 무난한 기본값으로 자주 쓰입니다.

즉 어댑터를 붙이는 순간 모델 동작이 바뀌는 것이 아니라, 학습이 진행된 만큼만 점진적으로 달라집니다.

## 핵심 개념

| 필드 | 의미 |
| --- | --- |
| `r` | LoRA 랭크입니다. 작을수록 가볍고, 클수록 표현력은 높아집니다. |
| `lora_alpha` | 스케일 계수입니다. 실제 영향력은 `alpha / r`로 나타납니다. |
| `lora_dropout` | 어댑터 경로에만 적용되는 드롭아웃입니다. 베이스 경로는 건드리지 않습니다. |
| `target_modules` | LoRA를 부착할 선형 레이어 이름 목록입니다. |
| `bias` | bias 학습 정책입니다. `"none"`, `"all"`, `"lora_only"` 중에서 고릅니다. |
| `task_type` | `CAUSAL_LM`, `SEQ_CLS` 같은 태스크 유형입니다. PEFT가 헤드를 올바르게 해석하게 합니다. |

## Before vs. After

**Before**

`LoraConfig(r=8, target_modules=["q_proj", "v_proj"])`를 GPT-2에 그대로 적용했더니 `print_trainable_parameters()`가 `trainable params: 0`을 출력합니다. 학습은 돌아가지만 손실 곡선은 평평합니다.

**After**

GPT-2의 실제 모듈 이름이 `c_attn`, `c_proj`라는 것을 확인하고 다음처럼 바꿉니다.

```text
trainable params: 1,478,656 || all params: 125,917,184 || trainable%: 1.1745
```

이 한 줄은 어댑터가 실제로 붙었다는 가장 직접적인 증거입니다. 동시에 1편에서 계산한 감각이 코드 수준에서도 크게 어긋나지 않음을 보여 줍니다.

## 먼저 고쳐야 할 설정 포인트

`r`은 저랭크 차원이고, `lora_alpha`는 보정 크기이며, `lora_dropout`은 어댑터 경로에만 적용되는 드롭아웃입니다. 실전에서 가장 사고가 잦은 필드는 `target_modules`입니다. 이 값이 틀리면 아무 데도 붙지 않거나, 의도하지 않은 레이어에 붙습니다.

![운영 영향이 큰 필드](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/03/03-01-the-fields-with-real-operational-impact.ko.png)

*운영 영향이 큰 필드*

## 단계별 설명

### 1단계 — 베이스 모델을 로드합니다

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("sshleifer/tiny-gpt2")
print(sum(p.numel() for p in model.parameters()))
```

### 2단계 — 모듈 이름을 직접 확인합니다

```python
for name, module in model.named_modules():
    if hasattr(module, "weight") and module.weight.dim() == 2:
        print(name, tuple(module.weight.shape))
```

GPT-2는 `transformer.h.0.attn.c_attn`, `c_proj` 같은 이름을 씁니다. Llama-3는 `q_proj`, `k_proj`, `v_proj`, `o_proj`를 쓰고, Qwen은 또 다릅니다. 모델별 명명 규칙을 추측하지 말고 **항상 직접 확인하는 습관**이 중요합니다.

### 3단계 — `LoraConfig`를 정의합니다

```python
from peft import LoraConfig, TaskType

config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["c_attn", "c_proj"],
    bias="none",
)
```

### 4단계 — 어댑터를 부착합니다

```python
from peft import get_peft_model

peft_model = get_peft_model(model, config)
peft_model.print_trainable_parameters()
```

`trainable%`가 1~3% 사이로 나오면 보통 부착이 제대로 된 것입니다. 0이면 가장 먼저 `target_modules` 이름부터 다시 확인해야 합니다.

### 5단계 — 어댑터 위치를 확인합니다

```python
for name, param in peft_model.named_parameters():
    if param.requires_grad:
        print(name, tuple(param.shape))
```

학습 대상은 `lora_A`, `lora_B`로 끝나는 파라미터여야 합니다. 다른 이름이 보인다면 의도하지 않은 모듈이 학습에 들어왔을 가능성이 큽니다.

## 이 코드에서 봐야 할 것

![GPT 계열에서 대상 모듈 고르기](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/03/03-03-what-to-notice-in-this-code.ko.png)

*GPT 계열에서 대상 모듈 고르기*

- GPT-2 계열은 어텐션과 projection 모듈 이름이 `c_attn`, `c_proj`라서 `target_modules` 문자열이 정확히 일치해야 합니다.
- 실행 중 `fan_in_fan_out` 경고가 보일 수 있는데, 이것은 GPT-2의 `Conv1D` 래퍼를 PEFT가 올바르게 처리하고 있다는 뜻이지 오류가 아닙니다.
- 이 글의 예제는 배선 검증용입니다. 실제 학습은 4편에서 `Trainer`와 연결합니다.
- `c_attn`은 Q, K, V를 하나의 행렬에 묶어 두기 때문에, 이름 하나만으로 세 projection에 동시에 LoRA가 붙습니다.

## 자주 하는 실수

![풀 파인튜닝과 LoRA 규모 비교](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/03/03-04-where-engineers-get-confused.ko.png)

*풀 파인튜닝과 LoRA 규모 비교*

- **`target_modules` 오타**: 가장 흔한 실패입니다. 에러는 안 나고 `trainable params: 0`만 출력됩니다. 항상 `print_trainable_parameters()`로 확인해야 합니다.
- **`r`과 `alpha`를 따로 놀게 두는 실수**: `r=64, alpha=16`처럼 두면 보정이 너무 약해져 학습이 거의 일어나지 않을 수 있습니다. 기본값으로는 `alpha = 2 * r`가 무난합니다.
- **`bias="all"`을 가볍게 켜는 실수**: 어댑터가 커지고, 베이스 상태로 되돌리기도 어려워집니다. `"none"`이 기본인 이유가 있습니다.
- **모든 선형 레이어에 LoRA를 붙이는 실수**: 어텐션 QKV만으로 충분한 경우가 많습니다. MLP까지 포함하면 학습 파라미터가 두세 배 늘어납니다.
- **Conv1D와 Linear를 같은 것으로 보는 실수**: GPT-2는 `nn.Linear`가 아니라 `transformers.pytorch_utils.Conv1D`를 사용합니다. 직접 구현하면 fan_in/fan_out이 쉽게 어긋납니다. 이 부분은 PEFT가 처리하게 두는 편이 안전합니다.

## 실무 메모

- **모델별 `target_modules` 표를 유지합니다**: GPT-2는 `["c_attn", "c_proj"]`, Llama는 보수적으로 `["q_proj", "v_proj"]`, 공격적으로는 더 넓은 목록을 씁니다. 이 매핑 표만 있어도 실수가 크게 줄어듭니다.
- **`r=8`과 `r=16`을 같은 데이터로 비교합니다**: 손실 곡선과 평가 지표 차이가 작다면 더 가벼운 설정에 머무르는 편이 좋습니다.
- **필요하면 베이스에 병합합니다**: 추론 지연이 중요하면 `merge_and_unload()`로 어댑터를 베이스에 합친 뒤 단일 모델처럼 배포할 수 있습니다.
- **어댑터만 따로 저장합니다**: `peft_model.save_pretrained("adapter/")`는 작은 산출물을 만들기 때문에 배포와 버전 관리가 쉽습니다.

## 체크리스트

- [ ] `LoraConfig` 핵심 필드의 의미를 설명할 수 있습니다.
- [ ] `target_modules`가 모델마다 달라지는 이유를 이해했습니다.
- [ ] `python main.py`를 실행해 어댑터가 실제로 붙고 비율이 0이 아님을 확인했습니다.
- [ ] `trainable%`가 1~3% 범위에 들어오는지 확인했습니다.
- [ ] `requires_grad=True`인 파라미터가 `lora_A`, `lora_B`뿐인지 확인했습니다.
- [ ] 다음 글에서 이 모델에 최소 한 번의 학습 스텝을 밀어 넣을 준비가 되어 있습니다.

## 연습 문제

1. `r`를 {4, 8, 16, 32}로 바꿔 `trainable%`가 어떻게 달라지는지 출력해 보세요. 1편의 손계산과 대체로 맞나요?
2. `target_modules`를 `["c_attn"]`만 남기면 비율이 얼마나 줄어드나요? 평가 결과는 어떻게 달라질지 가설을 세워 보세요.
3. `peft_model.merge_and_unload()`를 호출한 뒤 파라미터 수를 다시 확인해 보세요. 이 병합된 모델을 다시 LoRA 어댑터로 분리할 수 있을까요?

## 정리 · 다음 글

LoRA 구성 단계의 핵심은 성능 튜닝이 아니라 **연결 검증**입니다. 어댑터가 어디에 붙는지, 얼마나 많은 파라미터가 학습 대상이 되는지만 확인해도 절반은 끝난 셈입니다.

다음 글인 4편에서는 학습 루프를 다룹니다. 이제 이 어댑터에 실제로 그라디언트를 흘리고, 학습률, 배치 크기, 그래디언트 누적이 손실 곡선에 어떤 차이를 만드는지 보겠습니다.

## 실전 패턴 추가: 데이터 준비, LoRA 설정, 학습 입력 검증을 한 흐름으로 점검하기

파인튜닝 품질은 모델 아키텍처보다 입력 계약에서 먼저 결정됩니다. 데이터셋 템플릿, LoRA 설정, 길이 통계를 따로 보지 말고 같은 파이프라인에서 검증해야 디버깅 비용이 줄어듭니다.

```python
from dataclasses import dataclass
from typing import Iterable

from peft import LoraConfig

@dataclass
class Sample:
    instruction: str
    input: str
    output: str

def render(sample: Sample) -> str:
    return (
        "### Instruction:
" + sample.instruction + "

"
        "### Input:
" + sample.input + "

"
        "### Response:
" + sample.output
    )

def build_lora_config() -> LoraConfig:
    return LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )

def length_stats(lengths: Iterable[int]) -> tuple[int, float, int]:
    data = sorted(lengths)
    if not data:
        return 0, 0.0, 0
    avg = sum(data) / len(data)
    p95 = data[int(len(data) * 0.95) - 1]
    return min(data), avg, p95
```

운영 관점에서는 `target_modules`와 데이터 템플릿이 함께 관리되어야 합니다. 템플릿이 바뀌면 토큰 길이 분포가 바뀌고, 이는 배치 크기와 학습 안정성에 바로 영향을 줍니다. 따라서 데이터 버전, LoRA 설정 버전, 평가 지표를 같은 실험 단위로 묶어 기록하는 것이 필수입니다. 이렇게 해야 특정 품질 변화가 데이터 문제인지, 어댑터 설정 문제인지 빠르게 분리할 수 있습니다.

## 처음 질문으로 돌아가기

- **`LoraConfig`에서 실제로 이해해야 할 필드는 무엇일까요?**
  - 본문의 기준은 LoRA 어댑터 구성를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`target_modules`를 잘못 지정하면 어떤 문제가 생길까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **작은 GPT-2 계열 모델에서는 학습 가능한 파라미터 비율이 얼마나 낮아질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM Fine-tuning 101 (1/6): LLM 파인튜닝 입문](./01-intro.md)
- [LLM Fine-tuning 101 (2/6): 데이터셋 준비와 전처리](./02-dataset.md)
- **LLM Fine-tuning 101 (3/6): LoRA 어댑터 구성 (현재 글)**
- LLM Fine-tuning 101 (4/6): 학습 루프와 하이퍼파라미터 (예정)
- LLM Fine-tuning 101 (5/6): 모델 평가 (예정)
- LLM Fine-tuning 101 (6/6): 모델 서빙 (예정)

<!-- toc:end -->

---

## 참고 자료

- [PEFT quicktour](https://huggingface.co/docs/peft/quicktour)
- [Transformers model classes](https://huggingface.co/docs/transformers/index)
- [LoRA paper](https://arxiv.org/abs/2106.09685)
- [PEFT LoraConfig source](https://github.com/huggingface/peft/blob/main/src/peft/tuners/lora/config.py)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-finetuning-101/ko/03-lora)

Tags: Fine-tuning, LoRA, LLM, Python
