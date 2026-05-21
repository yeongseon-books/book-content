---
title: "LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기"
series: llm-from-scratch-101
episode: 8
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
seo_description: 지난 글의 모델은 셰익스피어 리듬은 흉내 내도 질문에 답하지는 못합니다.
---

# LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기

이 글은 LLM from Scratch 101 시리즈의 여덟 번째 글입니다.

지난 글까지 오면 모델은 분명히 텍스트를 생성합니다. 하지만 그 출력은 여전히 TinyShakespeare가 만든 리듬에 가깝습니다. 질문을 던진다고 해서 답을 잘해 주는 것은 아니고, instruction 형식을 안다고 보기도 어렵습니다.

이 지점에서 필요한 것이 supervised fine-tuning, 즉 SFT입니다. SFT의 첫 번째 효과는 새로운 지식을 대량으로 주입하는 것보다 출력 형식을 바꾸는 데서 더 뚜렷하게 드러납니다. 작은 데이터셋만으로도 모델이 `Q:` 뒤에는 질문이, `A:` 뒤에는 답이 온다는 습관을 배우기 시작합니다.

그래서 파인튜닝은 베이스 모델을 완전히 새로 만드는 작업이 아닙니다. 이미 형성된 기본 표현 위에 특정 과업의 출력 패턴을 덧칠하는 작업에 가깝습니다. 특히 소형 모델에서는 이 "출력 습관의 이동"이 매우 선명하게 보입니다.

이번 글에서는 pre-training, SFT, RLHF의 차이를 간단히 정리하고, 작은 instruction 데이터셋과 loss masking을 이용해 `finetune.py`를 붙이는 과정을 살펴보겠습니다. 목표는 거대한 챗봇이 아니라, 형식이 바뀌는 메커니즘을 눈으로 확인하는 것입니다.

이제 출력 습관을 어떻게 바꾸는지 이해하면 마지막 글에서 이 모델을 브라우저와 대화형 인터페이스로 감싸는 일이 자연스럽게 이어집니다.

## 먼저 던지는 질문

- pre-training, fine-tuning, RLHF는 각각 무엇을 바꾸는 단계일까요?
- instruction 데이터 한 줄은 어떤 필드 구조를 가지면 충분할까요?
- 작은 데이터셋 50개만으로도 출력 습관이 왜 바뀔 수 있을까요?

## 큰 그림

![LLM from Scratch 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/08/08-01-pre-training-vs-fine-tuning-vs-rlhf-a-qu.ko.png)

*LLM from Scratch 101 8장 흐름 개요*

## 왜 이 글이 중요한가

파인튜닝은 base model을 애플리케이션 문맥으로 끌고 오는 첫 단계입니다. 사전학습 모델이 일반적인 문자 예측 능력을 가졌다면, SFT는 그 모델이 어떤 형식으로 대답해야 하는지, 어떤 응답 습관을 따라야 하는지를 더 강하게 학습시키는 과정입니다.

또한 많은 입문자가 파인튜닝을 "새 지식을 심는 일"로만 이해하지만, 실제로는 출력 포맷과 응답 스타일 조정이 먼저 눈에 띄는 경우가 많습니다. 작은 데이터셋에서도 `Q:/A:` 패턴이 자리 잡으면, 모델은 완전히 다른 대화 가능성을 보여 줍니다.

운영적으로도 중요합니다. 파인튜닝 데이터 형식, label shifting, ignore index, learning rate 축소 같은 디테일은 모델이 질문을 복사할지, 답변 형식을 유지할지, 과도하게 붕괴할지를 좌우합니다. 작은 실험일수록 이 차이가 더 직접적으로 드러납니다.

## 핵심 관점

파인튜닝을 베이스 모델을 갈아엎는 작업으로 생각하면 기대가 과도해집니다. 더 현실적인 관점은 이렇습니다. **SFT는 베이스 모델의 기본 표현을 유지한 채, 작은 태스크 전용 데이터셋으로 출력 습관과 형식을 덧입히는 얇은 적응층**입니다.

이 관점은 작은 데이터셋의 효과를 이해하는 데 특히 유용합니다. 50개 예시가 셰익스피어풍 모델에게 새로운 세계지식을 주지는 못해도, `Q:` 다음에 질문이 오고 `A:` 다음에 짧고 직접적인 답이 와야 한다는 패턴은 충분히 학습시킬 수 있습니다.

또한 loss masking이 왜 필요한지도 여기서 분명해집니다. 우리는 질문 자체를 반복 암기시키려는 것이 아니라, 주어진 instruction 뒤에서 올바른 answer 패턴을 예측하게 만들고 싶습니다. 따라서 손실은 응답 구간에 더 집중되어야 합니다.

> 이번 글의 핵심은 이것입니다. 파인튜닝은 베이스 모델을 버리는 작업이 아니라, 작은 데이터셋으로 출력 습관을 덧칠하는 작업입니다.

## 핵심 개념

### pre-training, SFT, RLHF는 역할이 다릅니다

pre-training은 거대한 말뭉치에서 next-token prediction을 학습하는 단계입니다. SFT는 이미 학습된 모델을 instruction-response 형식에 맞추는 단계입니다. RLHF는 여기에 사람 선호 기반 신호를 더해 응답 정책을 더 조정하는 단계입니다.

이번 시리즈는 RLHF까지 가지 않고 SFT까지만 다룹니다. 목표는 인간 선호 정렬이 아니라, base model 위에 instruction 형식을 얹는 메커니즘을 직접 확인하는 데 있습니다.

### instruction 데이터 한 줄은 매우 단순해도 됩니다

우리의 `instructions.jsonl`은 `{"instruction": ..., "response": ...}` 형태만으로 충분합니다. 학습 시에는 이를 `Q: {instruction}\nA: {response}` 형식의 단일 시퀀스로 이어 붙여 사용합니다. 중요한 것은 복잡한 스키마보다 일관된 형식입니다.

### 작은 데이터셋도 출력 습관을 바꾸기에는 충분할 수 있습니다

50개 정도의 예시는 거대한 일반지식을 추가하기에는 턱없이 부족합니다. 하지만 모델에게 새로운 응답 습관을 보여 주기에는 생각보다 강한 신호가 됩니다. 특히 베이스 모델이 이미 문자 패턴과 문장 리듬을 어느 정도 알고 있다면, SFT는 그 기반 위에 형식을 빠르게 덧입힙니다.

```json
{"instruction":"Who is ROMEO?","response":"A young lover who loves Juliet."}
{"instruction":"What is Juliet's last name?","response":"Capulet."}
{"instruction":"Who said 'To be, or not to be'?","response":"Hamlet."}
{"instruction":"Write one sentence swearing loyalty to the King.","response":"My lord, I keep my faith."}
{"instruction":"Give one sentence of advice on guarding against jealousy.","response":"Jealousy first harms one's own heart."}
```

이 예시의 핵심은 내용보다 패턴입니다. 모델은 `Q:`와 `A:`라는 표식을 반복적으로 보면서, 이제 셰익스피어 문장 이어쓰기보다 질문-응답 형식을 더 자주 선택하게 됩니다.

### 학습 루프는 거의 같고 두 가지만 크게 달라집니다

`finetune.py`는 `train.py`와 매우 비슷합니다. 다만 learning rate를 더 낮게 잡고, `Q: ...\nA: ...` 전체 시퀀스에서 shifted label을 만들어 next-token prediction을 유지합니다. 즉, 학습 목표 자체는 그대로 두되 데이터 형식을 바꾸는 것입니다.

### loss masking은 응답 구간에 학습 신호를 집중시킵니다

시퀀스 전체를 인코딩한 뒤 `x = ids[:-1]`, `y = ids[1:]`로 만듭니다. 그다음 prompt 부분에 해당하는 shifted `y`를 `-100`으로 덮어 `cross_entropy(..., ignore_index=-100)`에서 무시하게 만듭니다. 이렇게 하면 causal LM objective는 유지하면서도 질문 구간을 정답 학습 대상으로 삼지 않을 수 있습니다.

이 처리는 매우 중요합니다. 질문까지 그대로 외우게 만들면 모델은 사용자 프롬프트를 복사하는 방향으로 치우칠 수 있습니다. 우리는 응답 형식을 학습시키고 싶기 때문에 손실을 답변 부분에 집중시킵니다.

### `finetune.py`는 기존 학습 스크립트 위에 얇게 덧붙일 수 있습니다

아래 코드는 `train.py`를 바탕으로 파인튜닝에 필요한 최소 변경만 추가한 예제입니다.

```python
# finetune.py
import json, torch, torch.nn.functional as F
from dataclasses import asdict
from data import encode
from model import GPT, GPTConfig

def load_rows(path="instructions.jsonl"):
    with open(path, encoding="utf-8") as f: return [json.loads(line) for line in f]

def build_example(row, block_size):
    prompt = f"Q: {row['instruction']}\nA:"
    full = f"{prompt} {row['response']}"[:block_size]
    ids = encode(full)
    x = torch.tensor(ids[:-1], dtype=torch.long)
    y = torch.tensor(ids[1:], dtype=torch.long)
    prompt_len = min(len(encode(prompt)), len(ids))
    y[: max(prompt_len - 1, 0)] = -100
    return x, y

device = "cuda" if torch.cuda.is_available() else "cpu"
ckpt = torch.load("ckpt.pt", map_location=device)
config = GPTConfig(**ckpt["config"])
model = GPT(config).to(device); model.load_state_dict(ckpt["model"])
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-5)
rows = load_rows()

for step in range(500):
    row = rows[step % len(rows)]
    xb, yb = build_example(row, config.block_size)
    xb, yb = xb[None, :].to(device), yb[None, :].to(device)
    logits, _ = model(xb)
    loss = F.cross_entropy(logits.view(-1, config.vocab_size), yb.view(-1), ignore_index=-100)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()

torch.save({"model": model.state_dict(), "config": asdict(config)}, "ckpt_sft.pt")
```

이 스크립트는 매우 짧지만 파인튜닝의 본질을 잘 보여 줍니다. 베이스 체크포인트를 불러오고, 작은 학습률로 instruction 데이터셋을 반복해서 보여 주고, SFT용 체크포인트를 새로 저장합니다.

### before/after 비교는 형식 변화에 집중해서 읽으면 됩니다

파인튜닝 효과는 동일한 프롬프트에 대한 출력 비교에서 가장 선명하게 드러납니다. base model은 여전히 셰익스피어풍 continuation으로 흐르기 쉽고, SFT model은 `Q:/A:` 구조를 유지하며 답변 구간을 더 직접적으로 채우려 합니다.

```text
[base]
Q: Write one sentence swearing loyalty to the King.
A: Wha, the thoue of thine me,

[sft]
Q: Write one sentence swearing loyalty to the King.
A: My lord, I serve thee with a faithful heart.
```

여기서 중요한 것은 완벽한 사실성보다 형식의 이동입니다. 즉, 모델이 질문-답변 계약을 받아들이기 시작했는지를 보는 것이 핵심입니다.

## 흔히 헷갈리는 지점

- 파인튜닝이 곧 대규모 지식 주입이라고 생각하기 쉽지만, 작은 SFT에서는 출력 형식 변화가 먼저 드러납니다.
- 학습 목표가 바뀌었다고 보기 쉽지만, 여전히 next-token prediction입니다.
- 질문 구간도 함께 loss를 주면 좋다고 느끼기 쉽지만, 응답 구간에 신호를 집중하기 위해 masking이 필요합니다.
- 작은 데이터셋은 의미 없다고 생각하기 쉽지만, 출력 습관을 바꾸는 데는 꽤 강한 신호가 됩니다.
- base model을 버리고 처음부터 다시 학습해야 한다고 느끼기 쉽지만, SFT는 기존 표현 위에 얹는 적응 단계입니다.

## 운영 체크리스트

- [ ] instruction/response 데이터 행이 일관된 템플릿으로 직렬화되는가
- [ ] `y[: ...] = -100` masking 경계가 prompt 길이와 맞는지 출력으로 확인했는가
- [ ] base checkpoint를 불러온 뒤 낮은 learning rate로 미세 조정하고 있는가
- [ ] `ckpt_sft.pt`에 SFT 이후 가중치와 config를 함께 저장했는가
- [ ] 같은 프롬프트로 base vs SFT 출력을 비교해 형식 변화가 생겼는지 확인했는가

## 정리

이번 글에서는 base GPT 위에 작은 instruction 데이터셋을 얹어 supervised fine-tuning을 수행했습니다. 핵심은 모델을 완전히 새로 만드는 것이 아니라, 이미 배운 문자 예측 능력 위에 질문-응답 형식이라는 새로운 출력 습관을 덧씌우는 데 있습니다.

또한 loss masking을 통해 instruction 구간을 손실에서 제외하고, response 구간에 학습 신호를 집중하는 이유도 살펴봤습니다. 이 처리 덕분에 모델은 프롬프트를 복사하는 대신 답변 구간을 더 잘 채우는 방향으로 움직입니다.

다음 글에서는 이렇게 미세 조정한 모델을 FastAPI 서버와 브라우저 UI로 감쌉니다. 즉, 지금까지 만든 LLM을 실제로 대화할 수 있는 작은 챗봇 시스템으로 마무리하게 됩니다.

## SFT 데이터셋 품질 점검 스크립트

파인튜닝에서 가장 먼저 망가지는 지점은 모델이 아니라 데이터입니다. 질문-응답 템플릿이 줄마다 다르거나, 응답이 지나치게 짧거나, 문자 집합이 tokenizer와 맞지 않으면 학습은 조용히 불안정해집니다. 따라서 학습 전에 데이터셋 리포트를 한 번 뽑는 편이 좋습니다.

```python
import json
import statistics

from data import encode

rows = [json.loads(line) for line in open("instructions.jsonl", encoding="utf-8")]
q_lens = [len(encode(r["instruction"])) for r in rows]
a_lens = [len(encode(r["response"])) for r in rows]

print("rows:", len(rows))
print("q_len mean/p95:", round(statistics.mean(q_lens), 2), sorted(q_lens)[int(len(q_lens)*0.95)-1])
print("a_len mean/p95:", round(statistics.mean(a_lens), 2), sorted(a_lens)[int(len(a_lens)*0.95)-1])
print("empty responses:", sum(1 for r in rows if not r["response"].strip()))
```

이 리포트를 남기면 파인튜닝 실패 원인을 "모델 문제"와 "데이터 문제"로 빠르게 분리할 수 있습니다.

### loss masking 경계를 눈으로 검증하는 출력

mask가 의도대로 적용됐는지 보려면 한 샘플을 직접 출력하는 것이 가장 빠릅니다.

```python
x, y = build_example(rows[0], block_size=64)
print("x_ids:", x.tolist()[:40])
print("y_ids:", y.tolist()[:40])
print("ignore_count:", int((y == -100).sum().item()))
```

`ignore_count`가 0이라면 prompt 구간이 학습 손실에 포함되고 있다는 뜻입니다. SFT 목적이 응답 형식 적응이라면 이 상태는 보통 바람직하지 않습니다.

### 베이스 대비 학습률 축소 원칙

SFT는 베이스 가중치를 크게 흔들지 않는 것이 중요합니다. 그래서 pretraining 대비 더 낮은 학습률을 쓰는 경우가 많습니다.

| 단계 | 전형적 학습률 범위 | 의도 |
| --- | --- | --- |
| pre-training | `1e-4 ~ 5e-4` | 광범위 패턴 학습 |
| SFT | `1e-5 ~ 5e-5` | 출력 형식/습관 미세 조정 |
| 추가 정렬(RLHF 등) | 더 보수적 | 정책 안정화 |

이번 예제에서 `3e-5`를 쓴 이유도 같은 맥락입니다. 큰 이동보다 안정적인 적응이 우선입니다.

### before/after 평가 프롬프트 세트를 고정합니다

```text
Q: Who is Juliet?
Q: Summarize Romeo in one sentence.
Q: Give one short warning about jealousy.
Q: Answer politely: What is loyalty?
```

항상 같은 평가 프롬프트를 써야 변화 해석이 가능합니다. 프롬프트가 매번 달라지면 모델 개선인지 입력 차이인지 분리하기 어렵습니다.

### SFT 실패 모드와 대응

| 증상 | 흔한 원인 | 첫 대응 |
| --- | --- | --- |
| 질문 복사 후 멈춤 | masking 경계 오류 | `-100` 적용 범위 점검 |
| 문체 붕괴 | 학습률 과대/step 과다 | lr 하향, early stop |
| 응답이 지나치게 짧음 | 데이터 응답 길이 편향 | 학습셋 길이 분포 보정 |
| OOV 경고 다발 | 문자 집합 불일치 | 데이터 정규화/필터링 |

이 표를 운영 체크리스트에 포함하면 SFT 반복 실험의 실패 비용이 크게 줄어듭니다.

## 파인튜닝 실험 카드 템플릿

SFT를 여러 번 돌리기 시작하면 어떤 설정이 어떤 출력을 만들었는지 빠르게 잊습니다. 그래서 실험마다 아래와 같은 실험 카드를 남기는 편이 좋습니다.

```text
exp_id=sft-2026-05-21-a
base_ckpt=ckpt.pt
train_rows=50
lr=3e-5
steps=500
mask_prompt=true
max_seq_len=64
train_loss_last=1.42
eval_prompt_set=v1
notes=Q/A 형식 안정화, 사실성은 제한적
```

이 카드가 있으면 출력 품질 논의가 훨씬 생산적으로 바뀝니다. 어떤 설정에서 어떤 변화가 생겼는지 근거를 남길 수 있기 때문입니다.

### 응답 구간 비율 점검

```python
def supervised_ratio(y: torch.Tensor) -> float:
    total = y.numel()
    active = int((y != -100).sum().item())
    return active / max(total, 1)
```

masking을 쓸 때는 각 샘플에서 실제로 손실에 기여하는 토큰 비율이 너무 낮지 않은지 확인해야 합니다. 질문이 길고 답이 짧으면 학습 신호가 약해집니다.

### 베이스 보존 vs 과적응 균형

| 평가 축 | 기대 신호 | 위험 신호 |
| --- | --- | --- |
| Q/A 형식 | `A:` 뒤 답변 일관 | 질문 복사, 답변 누락 |
| 일반 생성 | 기본 유창성 유지 | 급격한 붕괴/반복 |
| 문체 | 목표 형식 강화 | 과도한 고정문구 |

좋은 SFT는 새 습관을 추가하는 것이지 기존 능력을 지우는 것이 아닙니다. 그래서 형식 적응 지표와 기본 생성 품질을 함께 확인해야 합니다.

## 파인튜닝 데이터셋 품질을 높이는 실무 절차

SFT 성능은 모델 크기보다 데이터셋 구성 품질에 더 민감할 때가 많습니다. 특히 작은 모델에서는 잘못된 샘플 몇 개가 출력 습관 전체를 흔들 수 있어서, 데이터 정제 절차를 별도 단계로 운영하는 것이 중요합니다.

### 샘플 단위 검수 규칙

질문과 답변의 역할이 뒤바뀌지 않았는지, 답변이 질문을 그대로 복사하지는 않는지, 길이 제한을 벗어나 학습이 잘리지 않는지 확인해야 합니다. 또한 동일 질문의 중복 샘플이 과도하면 모델이 특정 표현만 과학습할 수 있습니다.

### 포맷 일관성 유지

`Q:`/`A:` 포맷, 시스템 지시문 포함 여부, 줄바꿈 정책이 섞이면 모델이 포맷 자체를 불확실하게 배웁니다. 파인튜닝 전처리 단계에서 최종 문자열 템플릿을 하나로 고정하고, 예외를 허용하지 않는 편이 좋습니다.

### 검증 세트 설계

검증 세트는 학습 세트 축소판이 아니라, 실제 사용 시나리오를 반영한 분리 집합이어야 합니다. 난이도별 샘플, 길이별 샘플, 도메인별 샘플을 섞어 두면 회귀를 더 빨리 발견할 수 있습니다.

### 과적합 징후 읽기

학습 손실이 계속 내려가는데 생성 다양성이 급격히 줄거나, 동일 문구 반복이 늘면 과적합 가능성이 큽니다. 이때는 에폭 수를 무작정 늘리기보다 학습률을 낮추고 조기 종료 기준을 재설정하는 편이 효과적입니다.

## 파인튜닝 실험 기록 템플릿

실험이 여러 번 반복되면 무엇이 효과가 있었는지 빠르게 잊게 됩니다. 그래서 최소 템플릿을 정해 기록하는 습관이 중요합니다.

- 데이터 버전과 샘플 수
- 템플릿 형식(`Q/A`, 시스템 프롬프트 포함 여부)
- 학습률, 배치 크기, 에폭 수
- 검증 손실과 대표 생성 예시

이 템플릿만 지켜도 다음 실험에서 같은 실수를 반복할 확률이 크게 줄어듭니다.

## 최종 점검

파인튜닝은 "더 오래 학습"이 아니라 "더 정확한 데이터 계약"의 문제입니다. 데이터 포맷, 분할 기준, 평가 시나리오를 먼저 고정하면 작은 모델에서도 체감 품질 향상을 안정적으로 얻을 수 있습니다.

결과적으로 SFT 성패는 모델보다 데이터 운영에서 결정됩니다.

## 현업에서 자주 받는 질문

### 작은 모델에서도 이 단계를 엄격하게 지켜야 하나요?

네, 오히려 작은 모델일수록 기본 계약을 엄격하게 지켜야 합니다. 모델 용량이 작을수록 입력 노이즈와 구현 불일치의 영향을 크게 받기 때문입니다. 재현 가능한 실험 단위를 먼저 확보하면, 모델 크기 확장 이전에도 품질 개선 속도가 올라갑니다.

### 실험 속도와 품질 관리가 충돌할 때는 어떻게 하나요?

속도를 높이려면 실험 횟수를 늘리는 것이 아니라 실패 비용을 줄여야 합니다. 설정 파일 고정, 로그 표준화, 체크포인트 메타데이터 저장 같은 장치를 먼저 도입하면, 같은 시간에 더 많은 "유효한" 실험을 수행할 수 있습니다.

### 마지막으로 무엇을 기록해 두면 도움이 되나요?

변경 이유, 기대 효과, 실제 관측 결과를 짧게 남기면 다음 실험의 품질이 올라갑니다. 특히 "왜 이 값을 선택했는가"를 기록하면, 몇 주 뒤에도 의사결정 맥락을 복원할 수 있습니다.

## 결론 메모

파인튜닝에서는 큰 기법보다 작은 데이터 규율이 더 큰 차이를 만듭니다. 샘플 품질과 평가 기준을 고정하면, 실험 결과를 재사용 가능한 지식으로 축적할 수 있습니다.

추가로, 데이터셋 변경 이력과 실패 사례를 함께 기록하면 다음 라운드에서 품질 개선 속도가 더 빨라집니다.

## 처음 질문으로 돌아가기

- **pre-training, fine-tuning, RLHF는 각각 무엇을 바꾸는 단계일까요?**
  - 본문의 기준은 베이스 모델을 우리 작업에 맞추기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **instruction 데이터 한 줄은 어떤 필드 구조를 가지면 충분할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **작은 데이터셋 50개만으로도 출력 습관이 왜 바뀔 수 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치](./02-embedding.md)
- [LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기](./03-attention.md)
- [LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위](./04-transformer-block.md)
- [LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성](./05-gpt-model.md)
- [LLM from Scratch 101 (6/9): 기울기로 배우기](./06-training-loop.md)
- [LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기](./07-inference.md)
- **LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기 (현재 글)**
- LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Finetuned Language Models Are Zero-Shot Learners (arXiv:2109.01652)](https://arxiv.org/abs/2109.01652)
- [Training language models to follow instructions with human feedback (arXiv:2203.02155)](https://arxiv.org/abs/2203.02155)
- [Stanford Alpaca (GitHub)](https://github.com/tatsu-lab/stanford_alpaca)
- [PyTorch cross_entropy (Documentation)](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)

### 관련 시리즈

- [AI Agent 101 — 컨텍스트 엔지니어링](../../ai-agent-101/ko/02-context-engineering.md)
- [LLM 앱 기초 — 프롬프트 엔지니어링 기초](../../llm-app-foundations-101/ko/03-prompt-engineering-basics.md)
- [LLM API 프로덕션 101 — 구조화 출력](../../llm-api-production-101/ko/01-structured-output.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/08-finetuning)

Tags: LLM, PyTorch, Transformer, Tutorial
