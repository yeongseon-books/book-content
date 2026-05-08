
# LLM 파인튜닝 입문

## 이 글에서 배울 것

- fine-tuning이 prompt engineering이나 RAG와 어떻게 다른지, 언제 각각을 선택해야 하는지 판단할 수 있습니다.
- full fine-tuning과 parameter-efficient fine-tuning(LoRA)의 차이를 이해합니다.
- fine-tuning 프로젝트의 전체 흐름(데이터 → 학습 → 평가 → 서빙)을 개관합니다.
- 이 시리즈 6편이 어떤 순서로 fine-tuning의 각 단계를 다루는지 파악합니다.

<!-- a-grade-intro:begin -->
## 핵심 질문

LLM 파인튜닝이 언제 RAG·프롬프트 엔지니어링보다 더 나은 선택일까요?

이 글은 그 질문에 답하기 위해 파인튜닝 입문의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 답할 질문

![이 글에서 답할 질문](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/01/01-01-questions-this-post-answers.ko.png)

*이 글에서 답할 질문*

- LoRA가 왜 풀 파인튜닝보다 훨씬 가벼운지 어떻게 계산할까요?
- 파인튜닝이 필요한 문제와 프롬프트 엔지니어링으로 충분한 문제는 어떻게 구분할까요?
- GPU 없이도 1편에서 무엇을 검증할 수 있을까요?
- LoRA가 줄여 주는 것은 모델 크기인가요, 학습 파라미터 수인가요?

> 풀 파인튜닝이 건물 전체를 다시 짓는 일이라면, LoRA는 하중이 걸리는 기둥 몇 개에만 보강재를 덧대는 일입니다.

예제 코드: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/ko/01-intro)

## 왜 중요한가

LLM 파인튜닝은 무조건 GPU 실습부터 시작해야 하는 주제가 아닙니다. 처음부터 큰 모델을 돌리면 학습률, 데이터셋 형식, 어댑터 rank 같은 변수들이 한꺼번에 흔들리고, 그중 무엇이 결과를 좌우했는지 분리할 수 없게 됩니다. 1편의 목적은 모델을 돌리는 일을 잠시 미루고 **계산 감각**을 먼저 맞추는 것입니다.

LoRA가 왜 싸고 빠른지, 어느 정도 파라미터만 학습하는지, 언제 이 선택이 합리적인지를 숫자로 먼저 이해해야 이후 데이터셋, 학습, 평가, 서빙 단계가 흔들리지 않습니다. 1편에서 한 번 계산해 둔 비율(전체 선형 파라미터 대비 LoRA 어댑터 1.5% 안팎)은 3편에서 `LoraConfig(r=8)`을 고를 때, 4편에서 학습 시간을 추정할 때, 6편에서 어댑터 가중치만 따로 배포할 때 모두 다시 등장합니다.

## Mental Model

파인튜닝은 다음 세 가지 변수를 어떻게 쪼갤지에 대한 결정입니다.

```
                   ┌──────────────────────────────────────┐
                   │ ① 무엇을 바꿀 것인가 (target params) │
                   ├──────────────────────────────────────┤
파인튜닝 한 번 = │ ② 무엇으로 바꿀 것인가 (dataset)     │
                   ├──────────────────────────────────────┤
                   │ ③ 어떻게 바꿀 것인가 (optimizer)     │
                   └──────────────────────────────────────┘
```

풀 파인튜닝은 ①을 "전부"로 두고, ②와 ③의 부담을 키웁니다. LoRA는 ①을 "선형 레이어 일부에 붙는 작은 어댑터"로 좁히고, 그 결과 ②(작은 데이터셋도 충분)와 ③(작은 옵티마이저 상태)을 동시에 가볍게 만듭니다. 같은 데이터를 같은 학습률로 돌려도 ①을 어떻게 잡았느냐에 따라 GPU 메모리 요구량이 10배 이상 차이 납니다.

## 핵심 개념

| 용어 | 의미 |
| --- | --- |
| Full fine-tuning | 베이스 모델의 모든 가중치를 업데이트. optimizer state까지 합치면 메모리는 모델 크기의 4배 이상 |
| LoRA | 기존 가중치를 freeze하고 저랭크 행렬 두 개(A, B)만 학습. 추가 파라미터는 보통 1~3% |
| Rank (r) | LoRA 어댑터의 중간 차원. 클수록 표현력은 높지만 학습 파라미터가 선형으로 증가 |
| Target module | LoRA를 끼워 넣을 선형 레이어 이름 (`q_proj`, `v_proj` 등) |
| Adapter weight | 학습이 끝난 뒤 따로 저장/배포되는 작은 가중치 파일. 베이스 모델과 합쳐서 추론에 사용 |

## Before vs. After

**Before** — "GPT-4 답변이 마음에 안 들어서 모델을 다시 학습해야 하나?" 라는 질문에 즉답을 못 합니다. 풀 파인튜닝의 비용을 들었던 기억과 LoRA가 싸다는 풍문 사이에서 고민만 길어집니다.

**After** — 1편을 마치면 다음과 같이 답할 수 있습니다.

```
모델 크기                      124M 파라미터 (GPT-2 small 급)
풀 파인튜닝 학습 파라미터       ≈ 124M (100%)
LoRA(r=8) 학습 파라미터         ≈ 1.8M (≈ 1.5%)
GPU 메모리 (옵티마이저 포함)    풀: ~5GB / LoRA: ~1.5GB
저장해야 할 어댑터 크기         ~7MB (도메인별 따로 보관 가능)
```

이 표를 손에 들고 있으면 "도메인 응답 톤만 살짝 바꾸고 싶다" 같은 요구에는 LoRA, "사실 자체를 학습시켜야 한다" 같은 요구에는 풀 파인튜닝 또는 RAG로 자연스럽게 분기할 수 있습니다.

## 먼저 감을 잡아야 하는 것

![베이스 가중치와 학습 파라미터 경계 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/01/01-02-what-to-understand-first.ko.png)

*베이스 가중치와 학습 파라미터 경계 구조*

파인튜닝에서 가장 먼저 놓치기 쉬운 지점은 **어디를 학습 대상으로 잡느냐**입니다. 풀 파인튜닝은 기존 가중치 전체를 업데이트하므로 메모리와 옵티마이저 상태가 함께 불어납니다. 반면 LoRA는 기존 가중치를 고정한 채 저랭크 행렬 두 개만 추가합니다. 그래서 비용 이야기를 할 때는 모델 전체 파라미터보다 **학습 가능한 파라미터 수**를 따로 봐야 합니다.

![먼저 감을 잡아야 하는 것](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/01/01-01-what-to-understand-first.ko.png)

*먼저 감을 잡아야 하는 것*

## 단계별 실습

### 1단계 — Transformer 구조를 데이터 클래스로 표현

```python
from dataclasses import dataclass

@dataclass
class TransformerShape:
    hidden_size: int
    intermediate_size: int
    num_layers: int
```

### 2단계 — 선형 레이어 파라미터 수 계산

```python
def total_linear_params(shape: TransformerShape) -> int:
    return shape.num_layers * (
        4 * shape.hidden_size * shape.hidden_size
        + 2 * shape.hidden_size * shape.intermediate_size
    )
```

attention의 Q, K, V, O projection 4개와 MLP의 up/down projection 2개를 합산합니다. embedding과 layer norm은 일부러 제외했습니다. LoRA가 끼어드는 자리를 명확히 보기 위해서입니다.

### 3단계 — LoRA 어댑터 파라미터 수 계산

```python
def lora_params_per_layer(hidden_size: int, intermediate_size: int, rank: int) -> int:
    attention = 4 * rank * (hidden_size + hidden_size)
    mlp = rank * (hidden_size + intermediate_size) + rank * (intermediate_size + hidden_size)
    return attention + mlp
```

각 LoRA 어댑터는 `A: (in, r)`과 `B: (r, out)` 두 행렬을 가집니다. 곱은 원래 행렬과 동일한 모양이 되지만, 학습 파라미터는 `r * (in + out)`으로 줄어듭니다. rank가 작을수록 절감 효과가 큽니다.

### 4단계 — 비율 비교

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

실행하면 비율이 1.5% 안팎으로 출력됩니다. rank를 16, 32로 올려 가며 비율이 어떻게 변하는지 직접 확인해 보면 4편에서 학습 시간을 가늠할 때 도움이 됩니다.

## 이 코드에서 봐야 할 것

![트랜스포머 선형층별 LoRA 개입 면적 비교](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/01/01-03-what-to-notice-in-this-code.ko.png)

*트랜스포머 선형층별 LoRA 개입 면적 비교*

- `hidden_size=768`, `intermediate_size=3072`, `num_layers=12`는 GPT-2 small 급 구조를 흉내 낸 값입니다.
- 이 스크립트는 전체 모델 파라미터가 아니라 attention/MLP 선형 레이어를 기준으로 LoRA가 개입하는 면적을 계산합니다.
- 실행 결과로 나온 비율은 이후 3편에서 `LoraConfig(r=8)`를 고를 때 감각 기준이 됩니다.

## 자주 하는 실수

![문제 유형에 따른 베이스 모델 선택 기준](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/01/01-04-where-engineers-get-confused.ko.png)

*문제 유형에 따른 베이스 모델 선택 기준*

- **모델 크기와 학습 파라미터를 혼동** — LoRA는 추론 시 베이스 모델을 그대로 들고 있어야 합니다. VRAM이 부족해 모델이 안 올라가는 문제는 LoRA로 풀리지 않습니다. 이 경우는 양자화(QLoRA)와 함께 다뤄야 합니다.
- **rank를 크게 잡을수록 좋다고 가정** — rank 64, 128을 시도하면 학습 파라미터가 풀 파인튜닝의 10~20%까지 늘어나면서, 정작 일반화 성능은 떨어지는 경우가 많습니다. r=8~16에서 시작하는 것이 안전합니다.
- **모든 선형 레이어에 LoRA 적용** — `target_modules=["q_proj", "v_proj"]`만으로 충분한 경우가 많습니다. MLP까지 포함하면 파라미터가 두세 배로 뜁니다.
- **데이터가 나쁘면 LoRA가 구해 줄 거라 기대** — 어댑터가 작아도 나쁜 라벨에 그대로 과적합됩니다. 1편의 계산은 비용 이야기일 뿐 데이터 품질을 대신하지 못합니다.
- **베이스 모델과 어댑터의 tokenizer 불일치** — 다른 베이스 모델로 학습한 어댑터를 옮겨 끼우면 토크나이저가 어긋나 결과가 깨집니다. 어댑터는 베이스와 한 쌍입니다.

## 실무 적용

- **선택 기준 정리하기**: "스타일 변경 → LoRA, 새로운 사실 주입 → RAG, 도메인 어휘/포맷 학습 → LoRA + 좋은 데이터셋"처럼 한 줄 가이드를 만들어 팀과 공유합니다.
- **첫 실험은 작은 베이스로**: GPT-2 small이나 Phi-2처럼 작은 모델로 학습 파이프라인을 검증한 뒤, Llama-3-8B로 옮기면 비용 사고를 줄일 수 있습니다.
- **어댑터 가중치 버전 관리**: 베이스 모델 hash와 어댑터 hash를 함께 기록합니다. 6편에서 어댑터만 swap해 가며 A/B 테스트할 때 필수입니다.
- **rank 스윕은 작게**: r ∈ {4, 8, 16}처럼 좁은 범위로 시작합니다. 30분짜리 실험 3개가 3시간짜리 실험 1개보다 정보가 많습니다.

## 실무에서는 이렇게 생각한다

fine-tuning을 시작하기 전에 "정말 fine-tuning이 필요한가"를 먼저 묻는 것이 실무의 첫 단계입니다. prompt engineering으로 충분한 작업이 많고, RAG로 해결되는 경우도 많습니다. fine-tuning은 데이터 준비, GPU 비용, 모델 관리까지 운영 부담이 크므로, ROI가 명확한 경우에만 선택하는 것이 현실적입니다.

fine-tuning이 필요한 대표적 신호는 "프롬프트로 품질은 나오지만 비용이 너무 높다", "응답 형식이나 톤이 일관되지 않는다", "도메인 지식이 모델에 내재화되어야 한다"입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **우선 프롬프트·RAG로 시도** — 파인튜닝은 마지막 수단이 합리적입니다.
- **스타일·포맷 학습에 강하다** — 지식 주입은 RAG가 더 효율적입니다.
- **데이터 품질이 결과를 결정** — 양보다 일관된 품질이 중요합니다.
- **운영 비용·복잡도가 추가** — 추론·서빙·버전 관리가 따라옵니다.
- **base model 선택이 출발점** — 라이선스·크기·품질을 처음에 평가합니다.

## 체크리스트

- [ ] LoRA가 줄이는 대상이 모델 크기인지 학습 파라미터 수인지 구분했다.
- [ ] rank가 커질수록 학습 파라미터가 선형으로 늘어난다는 점을 이해했다.
- [ ] `python main.py`로 파라미터 계산이 실제로 실행되는지 확인했다.
- [ ] 다음 글에서 다룰 데이터셋 형식이 왜 중요한지 연결 지었다.
- [ ] 풀 파인튜닝 / LoRA / RAG의 사용처를 한 문장씩 설명할 수 있다.

## 연습 문제

1. `rank`를 4, 8, 16, 32, 64로 바꿔 가며 비율을 표로 출력해 보세요. 어느 지점부터 "LoRA가 가볍다"는 주장이 약해지나요?
2. `intermediate_size`만 4096으로 늘렸을 때(나머지 고정) 비율이 어떻게 변하는지 계산해 보세요. MLP 비중이 큰 모델일수록 LoRA target을 attention만으로 좁히는 것이 왜 합리적인지 설명해 보세요.
3. `target_modules`를 `["q_proj", "v_proj"]`로만 제한하는 코드를 추가해 보세요. 이 경우 비율은 어떻게 바뀌나요? Hugging Face PEFT의 `print_trainable_parameters()`와 비교해 차이를 확인해 보세요.

## 정리 · 다음 글

1편의 목적은 파인튜닝을 신비한 GPU 작업으로 보지 않는 데 있습니다. 파라미터 계산만 정확히 이해해도 LoRA가 왜 실무 기본값이 되었는지, 어느 상황에서 풀 파인튜닝을 다시 꺼내야 하는지 설명할 수 있습니다.

다음 글(2편)에서는 데이터셋 준비를 다룹니다. instruction / chat / completion 세 형식을 비교하고, 라벨 마스킹과 `eos_token` 처리가 왜 학습 안정성에 결정적인지 코드로 확인합니다.

## 시리즈 목차

- **LLM 파인튜닝 입문 (현재 글)**
- 데이터셋 준비와 전처리 (예정)
- LoRA 어댑터 구성 (예정)
- 학습 루프와 하이퍼파라미터 (예정)
- 모델 평가 (예정)
- 모델 서빙 (예정)

---

## 참고 자료

- [LoRA paper](https://arxiv.org/abs/2106.09685)
- [Hugging Face PEFT documentation](https://huggingface.co/docs/peft)
- [QLoRA paper](https://arxiv.org/abs/2305.14314)
- [GPT-2 model card](https://huggingface.co/gpt2)

Tags: Fine-tuning, LoRA, LLM, Python

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
