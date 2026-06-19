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

지난 글까지 오면 모델은 분명히 텍스트를 생성합니다. 하지만 그 출력은 여전히 TinyShakespeare가 만든 리듬에 가깝습니다. 질문을 던진다고 해서 답을 잘해 주는 것은 아니고, instruction 형식을 안다고 보기도 어렵습니다.

이 글은 LLM from Scratch 101 시리즈의 8번째 글입니다.

이 지점에서 필요한 것이 supervised fine-tuning, 즉 SFT입니다. SFT의 첫 번째 효과는 새로운 지식을 대량으로 주입하는 것보다 출력 형식을 바꾸는 데서 더 뚜렷하게 드러납니다. 작은 데이터셋만으로도 모델이 `Q:` 뒤에는 질문이, `A:` 뒤에는 답이 온다는 습관을 배우기 시작합니다.

그래서 파인튜닝은 베이스 모델을 완전히 새로 만드는 작업이 아닙니다. 이미 형성된 기본 표현 위에 특정 과업의 출력 패턴을 덧칠하는 작업에 가깝습니다. 특히 소형 모델에서는 이 "출력 습관의 이동"이 매우 선명하게 보입니다.

이번 글에서는 pre-training, SFT, RLHF의 차이를 간단히 정리하고, 작은 instruction 데이터셋과 loss masking을 이용해 `finetune.py`를 붙이는 과정을 봅니다. 목표는 거대한 챗봇이 아니라, 형식이 바뀌는 메커니즘을 눈으로 확인하는 것입니다.

![LLM from Scratch 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/08/08-01-pre-training-vs-fine-tuning-vs-rlhf-a-qu.ko.png)
*LLM from Scratch 101 8장 흐름 개요*

## 이 글에서 다룰 문제

- pre-training, fine-tuning, RLHF는 각각 무엇을 바꾸는 단계일까요?
- instruction 데이터 한 줄은 어떤 필드 구조를 가지면 충분할까요?
- loss masking은 왜 필요하고 어떻게 구현할까요?
- 작은 데이터셋 50개만으로도 출력 습관이 왜 바뀔 수 있을까요?
- SFT 실패 모드는 어떤 증상으로 나타날까요?

## 파인튜닝 단계별 역할 비교

세 단계가 각각 무엇을 바꾸는지 한눈에 보면 구분이 명확해집니다.

```
pre-training ────────────────────────────────────────────
  목표: 대규모 말뭉치에서 next-token prediction
  데이터: 수십 GB ~ TB 규모 비정형 텍스트
  결과: 일반 언어 능력 (문법, 어휘, 세계지식 일부)
  비용: 매우 높음

SFT (Supervised Fine-Tuning) ───────────────────────────
  목표: instruction-response 형식에 맞추기
  데이터: 수백 ~ 수만 개 (instruction, response) 쌍
  결과: 출력 형식 습관, 응답 스타일 고정
  비용: 낮음 (base checkpoint 재활용)

RLHF ───────────────────────────────────────────────────
  목표: 사람 선호 신호로 응답 정책 조정
  데이터: 사람이 쌍을 비교 평가한 데이터
  결과: 더 안전하고 유용한 응답 방향성 강화
  비용: 중간 (reward model 추가 학습 필요)
```

이번 시리즈는 RLHF까지 가지 않습니다. 목표는 SFT로 base model 위에 instruction 형식을 얹는 메커니즘을 직접 확인하는 것입니다.

## instruction 데이터 형식

`instructions.jsonl`은 한 줄에 하나의 JSON 객체를 담습니다. 필드 구조는 단순할수록 좋습니다.

```json
{"instruction":"Who is ROMEO?","response":"A young lover who loves Juliet."}
{"instruction":"What is Juliet's last name?","response":"Capulet."}
{"instruction":"Who said 'To be, or not to be'?","response":"Hamlet."}
{"instruction":"Write one sentence swearing loyalty to the King.","response":"My lord, I keep my faith."}
{"instruction":"Give one sentence of advice on guarding against jealousy.","response":"Jealousy first harms one's own heart."}
```

학습 시에는 이를 `Q: {instruction}\nA: {response}` 형식의 단일 시퀀스로 이어 붙입니다.

```
Q: Who is ROMEO?
A: A young lover who loves Juliet.
```

중요한 것은 복잡한 스키마보다 일관된 형식입니다. 모델은 `Q:`와 `A:`라는 표식을 반복적으로 보면서 질문-응답 구조를 패턴으로 배웁니다.

## loss masking 원리

시퀀스 전체를 next-token prediction 목표로 학습하면 모델은 질문 자체를 복사하는 방향으로 치우칠 수 있습니다. loss masking은 prompt 구간을 손실 계산에서 제외하고 response 구간에 학습 신호를 집중시킵니다.

```
전체 시퀀스: Q: Who is ROMEO? A: A young lover.
              |<── prompt ──>|<── response ───>|

x (입력):    Q : _ W h o _ i s _ R O M E O ? _ A : _ A _ y o u n g ...
y (타깃):    : _ W h o _ i s _ R O M E O ? _ A : _ A _ y o u n g _ l ...

y masking:  -100 -100 -100 -100 -100 -100 ... A : _ A _ y o u n g _ l ...
             |<─────── -100 (무시) ──────────>|<──── 실제 학습 대상 ────>|
```

`cross_entropy(..., ignore_index=-100)`은 `-100` 위치를 손실 계산에서 건너뜁니다. 이렇게 하면 causal LM objective는 유지하면서 질문 구간을 정답 학습 대상으로 삼지 않을 수 있습니다.

## 데이터셋 품질 점검

파인튜닝에서 가장 먼저 망가지는 지점은 모델이 아니라 데이터입니다. 학습 전에 데이터셋 리포트를 한 번 뽑는 것이 좋습니다.

```python
# check_data.py
import json
import statistics
from data import encode

rows = [json.loads(line) for line in open("instructions.jsonl", encoding="utf-8")]
q_lens = [len(encode(r["instruction"])) for r in rows]
a_lens  = [len(encode(r["response"]))   for r in rows]

print(f"rows         : {len(rows)}")
print(f"q_len mean   : {statistics.mean(q_lens):.1f}")
print(f"q_len p95    : {sorted(q_lens)[int(len(q_lens)*0.95)-1]}")
print(f"a_len mean   : {statistics.mean(a_lens):.1f}")
print(f"a_len p95    : {sorted(a_lens)[int(len(a_lens)*0.95)-1]}")
print(f"empty resp   : {sum(1 for r in rows if not r['response'].strip())}")
print(f"dup instruct : {len(rows) - len({r['instruction'] for r in rows})}")
```

예시 출력:

```
rows         : 50
q_len mean   : 9.4
q_len p95    : 18
a_len mean   : 7.2
a_len p95    : 14
empty resp   : 0
dup instruct : 0
```

`empty resp`가 0이 아니라면 해당 행을 제거해야 합니다. `dup instruct`가 크면 특정 표현만 과학습됩니다.

## finetune.py 전체 구현

```python
# finetune.py
"""
사용법:
    python finetune.py                          # 기본값
    python finetune.py --lr 1e-5 --steps 300   # 커스텀 설정

필요 파일:
    ckpt.pt            - pre-training 체크포인트
    instructions.jsonl - instruction/response 쌍
    data.py, model.py  - 이전 글의 코드
"""

import argparse
import json
import csv
from dataclasses import asdict
from pathlib import Path

import torch
import torch.nn.functional as F

from data import encode
from model import GPT, GPTConfig


# ─── CLI 인수 ────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--base_ckpt",  default="ckpt.pt")
    p.add_argument("--data",       default="instructions.jsonl")
    p.add_argument("--out_ckpt",   default="ckpt_sft.pt")
    p.add_argument("--lr",         type=float, default=3e-5)
    p.add_argument("--steps",      type=int,   default=500)
    p.add_argument("--block_size", type=int,   default=128)
    p.add_argument("--log_csv",    default="sft_log.csv")
    return p.parse_args()


# ─── 데이터 ──────────────────────────────────────────────────────────────────

def load_rows(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build_example(row: dict, block_size: int) -> tuple[torch.Tensor, torch.Tensor]:
    """
    instruction/response 쌍을 (x, y) 텐서로 변환합니다.
    y에서 prompt 구간은 -100으로 마스킹합니다.
    """
    prompt = f"Q: {row['instruction']}\nA:"
    full   = f"{prompt} {row['response']}"

    # block_size 초과 시 잘라냄
    ids = encode(full)[: block_size + 1]
    if len(ids) < 2:
        raise ValueError(f"시퀀스가 너무 짧습니다: {full!r}")

    x = torch.tensor(ids[:-1], dtype=torch.long)
    y = torch.tensor(ids[1:],  dtype=torch.long)

    # prompt 길이 계산 (y는 x보다 한 토큰 뒤)
    prompt_ids = encode(prompt)
    mask_len   = min(len(prompt_ids), len(y))   # y 기준 마스킹 길이
    y[:mask_len] = -100

    return x, y


def supervised_ratio(y: torch.Tensor) -> float:
    """손실에 실제로 기여하는 토큰 비율을 반환합니다."""
    active = int((y != -100).sum().item())
    return active / max(y.numel(), 1)


# ─── 학습률 스케줄 ────────────────────────────────────────────────────────────

def get_lr(step: int, max_steps: int, base_lr: float) -> float:
    """warmup 50 step + 코사인 감쇠"""
    warmup = 50
    if step < warmup:
        return base_lr * (step + 1) / warmup
    progress = (step - warmup) / max(max_steps - warmup, 1)
    import math
    return base_lr * 0.5 * (1.0 + math.cos(math.pi * progress))


# ─── 메인 ────────────────────────────────────────────────────────────────────

def main():
    args   = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device: {device}  |  base: {args.base_ckpt}  |  lr: {args.lr}  |  steps: {args.steps}")

    # 베이스 체크포인트 로드
    ckpt   = torch.load(args.base_ckpt, map_location=device)
    config = GPTConfig(**ckpt["config"])
    model  = GPT(config).to(device)
    model.load_state_dict(ckpt["model"])
    print(f"베이스 로드 완료: {sum(p.numel() for p in model.parameters()):,} params")

    # 데이터
    rows = load_rows(args.data)
    print(f"instruction rows: {len(rows)}")

    # 옵티마이저
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)

    # CSV 로그 초기화
    log_path = Path(args.log_csv)
    csv_file = log_path.open("w", newline="", encoding="utf-8")
    writer   = csv.writer(csv_file)
    writer.writerow(["step", "loss", "sup_ratio", "lr"])

    # 학습 루프
    model.train()
    for step in range(args.steps):
        row = rows[step % len(rows)]

        try:
            xb, yb = build_example(row, config.block_size)
        except ValueError as e:
            print(f"[skip] step {step}: {e}")
            continue

        ratio = supervised_ratio(yb)
        if ratio < 0.1:
            # 응답 구간이 너무 짧으면 학습 신호가 약함
            print(f"[warn] step {step}: sup_ratio={ratio:.2f} — 응답이 너무 짧습니다")

        xb = xb.unsqueeze(0).to(device)
        yb = yb.unsqueeze(0).to(device)

        logits, _ = model(xb)
        loss = F.cross_entropy(
            logits.view(-1, config.vocab_size),
            yb.view(-1),
            ignore_index=-100,
        )

        lr = get_lr(step, args.steps, args.lr)
        for pg in optimizer.param_groups:
            pg["lr"] = lr

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        loss_val = loss.item()
        writer.writerow([step, f"{loss_val:.4f}", f"{ratio:.3f}", f"{lr:.2e}"])

        if step % 50 == 0 or step == args.steps - 1:
            print(f"step {step:4d}  loss={loss_val:.4f}  sup_ratio={ratio:.2f}  lr={lr:.2e}")

    csv_file.close()

    # SFT 체크포인트 저장
    torch.save(
        {
            "model":  model.state_dict(),
            "config": asdict(config),
            "sft_meta": {
                "base_ckpt":  args.base_ckpt,
                "data":       args.data,
                "lr":         args.lr,
                "steps":      args.steps,
                "block_size": args.block_size,
            },
        },
        args.out_ckpt,
    )
    print(f"\n저장 완료: {args.out_ckpt}")
    print(f"학습 로그: {args.log_csv}")


if __name__ == "__main__":
    main()
```

실행 예시:

```bash
python finetune.py --steps 500 --lr 3e-5
```

예시 출력:

```
device: cpu  |  base: ckpt.pt  |  lr: 3e-05  |  steps: 500
베이스 로드 완료: 1,198,656 params
instruction rows: 50
step    0  loss=4.1823  sup_ratio=0.45  lr=6.00e-07
step   50  loss=2.8741  sup_ratio=0.45  lr=3.00e-05
step  100  loss=2.1932  sup_ratio=0.51  lr=2.91e-05
step  200  loss=1.7214  sup_ratio=0.48  lr=2.61e-05
step  400  loss=1.4109  sup_ratio=0.50  lr=1.57e-05
step  499  loss=1.3812  sup_ratio=0.47  lr=1.50e-06

저장 완료: ckpt_sft.pt
학습 로그: sft_log.csv
```

## loss masking 경계 검증

mask가 의도대로 적용됐는지 확인하려면 샘플 하나를 직접 출력합니다.

```python
# verify_mask.py
import json
import torch
from data import encode, decode
from finetune import build_example, supervised_ratio

rows = [json.loads(line) for line in open("instructions.jsonl", encoding="utf-8")]
row  = rows[0]

x, y = build_example(row, block_size=64)

print(f"instruction : {row['instruction']!r}")
print(f"response    : {row['response']!r}")
print()

# 처음 20 토큰 출력
for i in range(min(20, len(x))):
    xc = decode([x[i].item()])
    yv = y[i].item()
    yc = "MASK" if yv == -100 else decode([yv])
    print(f"  [{i:2d}] x={xc!r:4s}  y={yc!r}")

print()
print(f"total tokens : {len(y)}")
print(f"masked       : {int((y == -100).sum().item())}")
print(f"active       : {int((y != -100).sum().item())}")
print(f"sup_ratio    : {supervised_ratio(y):.3f}")
```

예시 출력:

```
instruction : 'Who is ROMEO?'
response    : 'A young lover who loves Juliet.'

  [ 0] x='Q'   y=MASK
  [ 1] x=':'   y=MASK
  [ 2] x=' '   y=MASK
  [ 3] x='W'   y=MASK
  [ 4] x='h'   y=MASK
  [ 5] x='o'   y=MASK
  [ 6] x=' '   y=MASK
  [ 7] x='i'   y=MASK
  [ 8] x='s'   y=MASK
  [ 9] x=' '   y=MASK
  [10] x='R'   y=MASK
  [11] x='O'   y=MASK
  [12] x='M'   y=MASK
  [13] x='E'   y=MASK
  [14] x='O'   y=MASK
  [15] x='?'   y=MASK
  [16] x=' '   y=MASK
  [17] x='A'   y=MASK
  [18] x=':'   y=' '
  [19] x=' '   y='A'

total tokens : 45
masked       : 19
active       : 26
sup_ratio    : 0.578
```

`ignore_count`가 0이라면 prompt 구간이 학습 손실에 포함되고 있다는 뜻입니다. 이 상태는 보통 바람직하지 않습니다.

## before/after 비교

파인튜닝 효과는 동일한 프롬프트에 대한 출력 비교에서 가장 선명하게 드러납니다.

```python
# compare.py
import torch
from data import encode, decode
from model import GPT, GPTConfig

def generate(ckpt_path: str, prompt: str, max_new: int = 60) -> str:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ckpt   = torch.load(ckpt_path, map_location=device)
    model  = GPT(GPTConfig(**ckpt["config"])).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()

    ids = encode(prompt)
    idx = torch.tensor([ids], dtype=torch.long, device=device)
    with torch.no_grad():
        out = model.generate(idx, max_new, temperature=0.7, top_k=20, top_p=0.9)
    return decode(out[0].tolist())[len(ids):]


prompts = [
    "Q: Who is ROMEO?\nA:",
    "Q: Write one sentence swearing loyalty to the King.\nA:",
    "Q: Give one short warning about jealousy.\nA:",
]

for p in prompts:
    print("=" * 60)
    print(f"PROMPT: {p.strip()}")
    print(f"\n[base] {generate('ckpt.pt',     p, 60)!r}")
    print(f"[sft]  {generate('ckpt_sft.pt', p, 60)!r}")
    print()
```

예시 출력:

```
============================================================
PROMPT: Q: Who is ROMEO?
A:

[base] 'Wha, the thoue of thine me,\nAnd wilt thou art the li'
[sft]  ' A young man who loves Juliet deeply.'

============================================================
PROMPT: Q: Write one sentence swearing loyalty to the King.
A:

[base] "Now,\nOf my heart,\nA:\nAnd yet the duke'"
[sft]  ' My lord, I serve thee with a faithful heart.'

============================================================
PROMPT: Q: Give one short warning about jealousy.
A:

[base] " I am a noble;\nAnd this the man:\nAnd I am"
[sft]  ' Jealousy first harms your own heart.'
```

여기서 중요한 것은 완벽한 사실성보다 형식의 이동입니다. 즉, 모델이 질문-답변 계약을 받아들이기 시작했는지를 보는 것이 핵심입니다.

## 학습률 선택 기준

SFT는 베이스 가중치를 크게 흔들지 않는 것이 중요합니다. 그래서 pre-training 대비 더 낮은 학습률을 씁니다.

| 단계 | 전형적 학습률 범위 | 의도 |
| --- | --- | --- |
| pre-training | `1e-4 ~ 5e-4` | 광범위 패턴 학습 |
| SFT | `1e-5 ~ 5e-5` | 출력 형식/습관 미세 조정 |
| 추가 정렬(RLHF 등) | `1e-6 ~ 1e-5` | 정책 안정화 |

이번 예제에서 `3e-5`를 쓴 이유도 같은 맥락입니다. 큰 이동보다 안정적인 적응이 우선입니다.

## SFT 실패 모드 진단

| 증상 | 흔한 원인 | 첫 대응 |
| --- | --- | --- |
| 질문을 그대로 복사 후 멈춤 | masking 경계 오류 | `verify_mask.py`로 `-100` 범위 확인 |
| 생성이 반복 루프에 빠짐 | 학습률 과대 또는 step 과다 | lr 하향, early stop 추가 |
| 응답이 너무 짧고 단편적 | 데이터 응답 길이 편향 | a_len p95 확인, 짧은 응답 보강 |
| OOV 경고 다발 | 학습 데이터 문자 집합 불일치 | 데이터 정규화, ASCII 필터링 |
| 학습 손실이 2.0 이하로 내려가지 않음 | 데이터 중복 또는 포맷 불일치 | dup_instruct 확인, 포맷 재통일 |
| base 생성 품질 급격히 저하 | 학습률 너무 높거나 steps 과다 | lr 축소, sup_ratio 확인 |

## 베이스 보존 vs 과적응 균형

| 평가 축 | 기대 신호 | 위험 신호 |
| --- | --- | --- |
| Q/A 형식 | `A:` 뒤 답변이 일관되게 나옴 | 질문 복사, 답변 누락 |
| 일반 생성 | 기본 유창성 유지 | 급격한 붕괴 또는 반복 고착 |
| 문체 | 목표 형식 강화 | 특정 고정문구 과학습 |

좋은 SFT는 새 습관을 추가하는 것이지 기존 능력을 지우는 것이 아닙니다. 형식 적응 지표와 기본 생성 품질을 함께 확인해야 합니다.

## 실험 카드 템플릿

SFT를 여러 번 돌리기 시작하면 어떤 설정이 어떤 출력을 만들었는지 빠르게 잊습니다. 실험마다 아래 카드를 남기는 것이 좋습니다.

```text
exp_id        = sft-2026-05-21-a
base_ckpt     = ckpt.pt
train_rows    = 50
lr            = 3e-5
steps         = 500
mask_prompt   = true
max_seq_len   = 128
train_loss_last = 1.38
eval_prompts  = 3개 고정 프롬프트 세트 v1
notes         = Q/A 형식 안정화, 사실성은 제한적
```

## 운영 체크리스트

- [ ] instruction/response 데이터 행이 일관된 템플릿으로 직렬화되는가
- [ ] `check_data.py`로 empty/dup 행을 사전에 제거했는가
- [ ] `verify_mask.py`로 `-100` masking 경계가 prompt 길이와 맞는지 확인했는가
- [ ] base checkpoint를 불러온 뒤 낮은 learning rate로 미세 조정하고 있는가
- [ ] `ckpt_sft.pt`에 SFT 이후 가중치, config, sft_meta를 함께 저장했는가
- [ ] 같은 프롬프트로 base vs SFT 출력을 비교해 형식 변화가 생겼는지 확인했는가
- [ ] 실험 카드를 작성해 어떤 설정이 어떤 결과를 냈는지 기록했는가

## 정리

이번 글에서는 base GPT 위에 작은 instruction 데이터셋을 얹어 supervised fine-tuning을 수행했습니다. 핵심은 모델을 완전히 새로 만드는 것이 아니라, 이미 배운 문자 예측 능력 위에 질문-응답 형식이라는 새로운 출력 습관을 덧씌우는 데 있습니다.

loss masking을 통해 instruction 구간을 손실에서 제외하고 response 구간에 학습 신호를 집중하는 이유도 살펴봤습니다. 이 처리 덕분에 모델은 프롬프트를 복사하는 대신 답변 구간을 더 잘 채우는 방향으로 움직입니다.

다음 글에서는 이렇게 미세 조정한 모델을 FastAPI 서버와 브라우저 UI로 감쌉니다. 지금까지 만든 LLM을 실제로 대화할 수 있는 작은 챗봇 시스템으로 마무리하게 됩니다.

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
- [LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍](./09-chatbot-wrapper.md)

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
