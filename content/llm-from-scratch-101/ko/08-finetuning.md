---
title: 베이스 모델을 우리 작업에 맞추기
series: llm-from-scratch-101
episode: 8
language: ko
status: ready
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
last_reviewed: '2026-04-29'
---

# 베이스 모델을 우리 작업에 맞추기

> LLM from Scratch 101 시리즈 (8/9)

지난 글의 모델은 셰익스피어 리듬은 흉내 내도 질문에 답하지는 못합니다.

SFT의 첫 효과는 지식보다 형식 변화입니다.

50개 예시로 출력 습관이 바뀌는 장면만 보겠습니다.

오늘 멘탈 모델은 이렇습니다. **파인튜닝은 베이스 모델을 버리는 일이 아니라, 작은 데이터셋으로 출력 습관을 덧칠하는 일입니다.**

---

## Pre-training vs Fine-tuning vs RLHF — 1분 정리

pre-training은 다음 토큰 예측, SFT는 instruction-response 형식 적응, RLHF는 사람 선호 반영 단계입니다.

![Pre-training vs Fine-tuning vs RLHF — 1분 정리](../../../assets/llm-from-scratch-101/08/08-01-pre-training-vs-fine-tuning-vs-rlhf-a-qu.ko.png)
## Instruction 데이터 한 줄의 형태

JSONL 한 줄은 `{"instruction": ..., "response": ...}` 형태로 둡니다. 학습할 때는 `Q: {q}\nA: {a}` 템플릿으로 이어 붙입니다.

## 작은 데이터셋 만들기 — 50개로 충분한가

아래 다섯 줄은 `instructions.jsonl` 예시입니다. 실제 파일은 같은 형식으로 50줄을 채웁니다. 이번 시리즈의 char-level tokenizer는 TinyShakespeare에서 만든 영어 문자 집합만 알기 때문에, 예시 데이터도 같은 문자 집합 안에서 맞춥니다.

```json
{"instruction":"Who is ROMEO?","response":"A young lover who loves Juliet."}
{"instruction":"What is Juliet's last name?","response":"Capulet."}
{"instruction":"Who said 'To be, or not to be'?","response":"Hamlet."}
{"instruction":"Write one sentence swearing loyalty to the King.","response":"My lord, I keep my faith."}
{"instruction":"Give one sentence of advice on guarding against jealousy.","response":"Jealousy first harms one's own heart."}
```

`Q:` 뒤에는 질문, `A:` 뒤에는 답이 온다는 패턴은 금방 배웁니다. 한국어로도 SFT 개념은 같지만, 그러려면 먼저 한국어가 들어간 코퍼스로 토크나이저와 vocab을 다시 만들어야 합니다.

## 학습 루프는 거의 그대로 — 두 가지만 바뀐다

`train.py`와 비교하면 바뀌는 부분은 둘뿐입니다. 학습률을 `3e-5`로 낮추고, 라벨을 한 칸 shifted 형태로 만들어 여전히 다음 토큰 예측을 하게 합니다.

## Loss masking — instruction 토큰은 학습 안 시킨다

전체 입력은 `Q: ...\nA: ...`를 인코딩한 뒤 `x = ids[:-1]`, `y = ids[1:]`로 한 칸 밀어 만듭니다. 그다음 shifted된 `y`에서 질문 구간만 `-100`으로 덮어, 손실은 답변 토큰에만 걸리게 합니다.

## finetune.py — train.py에서 30줄만 추가

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

## Before/After 비교 출력

held-out 프롬프트 하나만 봐도 차이가 납니다. base 모델은 셰익스피어풍 continuation으로 흘러가고, SFT 모델은 shifted target 위에서 답변 형식을 더 안정적으로 유지합니다.

```text
[base]
Q: Write one sentence swearing loyalty to the King.
A: Wha, the thoue of thine me,

[sft]
Q: Write one sentence swearing loyalty to the King.
A: My lord, I serve thee with a faithful heart.
```

완성형 챗봇과는 거리가 멉니다. 그래도 형식 변화는 분명합니다.

## 다음 글 예고

다음 글에서는 FastAPI를 씌워 브라우저에서 바로 말을 걸 수 있게 만들겠습니다. 멀티턴 프롬프트와 SSE 스트리밍까지 붙여 시리즈를 마무리하겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [글자를 숫자로 바꾸기](./01-tokenizer.md)
- [정수에서 벡터로, 그리고 위치](./02-embedding.md)
- [어떤 토큰을 얼마나 볼지 스스로 정하기](./03-attention.md)
- [블록 하나, 깊이의 단위](./04-transformer-block.md)
- [조립: GPT 모델 클래스 완성](./05-gpt-model.md)
- [기울기로 배우기](./06-training-loop.md)
- [샘플링 — 학습된 모델에서 글 뽑아내기](./07-inference.md)
- **베이스 모델을 우리 작업에 맞추기 (현재 글)**
- 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

- [Finetuned Language Models Are Zero-Shot Learners](https://arxiv.org/abs/2109.01652)
- [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155)
- [Stanford Alpaca](https://github.com/tatsu-lab/stanford_alpaca)
- [PyTorch cross_entropy](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)

Tags: LLM, PyTorch, Transformer, Tutorial
