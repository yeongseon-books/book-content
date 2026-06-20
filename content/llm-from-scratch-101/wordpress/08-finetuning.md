---
title: "바이브코딩을 위한 LLM 밑바닥부터 (8/9): 베이스 모델을 우리 작업에 맞추기"
series: llm-from-scratch-101
episode: 8
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM밑바닥부터
- SFT
- 파인튜닝
- AI코딩
seo_description: "바이브코딩을 위한 LLM 밑바닥부터 8편: SFT. instruction 데이터와 loss masking으로 베이스 모델의 출력 습관을 바꾸는 방법을 이해합니다."
---

# 바이브코딩을 위한 LLM 밑바닥부터 (8/9): 베이스 모델을 우리 작업에 맞추기

이 글은 바이브코딩을 위한 LLM 밑바닥부터 시리즈의 8번째 글입니다.

지난 글까지 오면 모델은 텍스트를 생성합니다. 하지만 그 출력은 학습 데이터의 리듬에 가깝습니다. 질문을 던진다고 해서 답을 해 주는 것은 아닙니다. 이 지점에서 필요한 것이 SFT(Supervised Fine-tuning)입니다. SFT의 첫 번째 효과는 새로운 지식을 주입하는 것보다 출력 형식을 바꾸는 데서 뚜렷하게 나타납니다. 작은 데이터셋만으로도 모델이 Q:/A: 패턴을 배우기 시작합니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 SFT 코드를 요청할 때 loss masking을 명시하지 않으면, 프롬프트 구간도 학습 신호에 포함되어 모델이 질문을 복사하는 방향으로 치우칩니다.

> SFT는 베이스 모델을 완전히 새로 만드는 작업이 아닙니다. 이미 형성된 기본 표현 위에 특정 출력 패턴을 덧칠하는 작업입니다. loss masking으로 prompt 구간을 제외하고 response 구간에만 학습 신호를 집중하는 것이 핵심입니다.

---

## 이 글에서 다룰 문제

- pre-training, SFT, RLHF는 각각 무엇을 바꾸는 단계일까요?
- loss masking은 왜 필요하고 어떻게 구현할까요?
- 작은 데이터셋 50개만으로도 출력 습관이 왜 바뀔 수 있을까요?
- SFT 실패 모드는 어떤 증상으로 나타날까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?

SFT 메커니즘을 이해하면 AI에게 "loss masking 포함, verify_mask 검증, 낮은 학습률 명시" 같은 정확한 요청을 할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "instruction 데이터로 모델 파인튜닝 코드 작성해줘"
→ loss masking 없어 프롬프트도 학습 신호에 포함
→ 학습률을 pre-training과 같게 설정
→ 마스킹 검증 없어 오류를 모름
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "instruction/response JSONL로 SFT finetune.py를 작성해줘.
    Q:{instruction}\nA: 형식으로 직렬화,
    prompt 구간을 y[:mask_len] = -100으로 마스킹,
    ignore_index=-100으로 cross_entropy 계산,
    base 체크포인트보다 10배 낮은 학습률,
    verify_mask.py로 경계 검증 포함해줘"
→ response 구간에만 학습 신호 집중
→ 마스킹 경계 즉시 검증 가능
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| loss masking 없음 | 모델이 질문을 복사하는 방향으로 학습 | y[:prompt_len] = -100 적용 |
| 학습률이 pre-training과 같음 | 베이스 가중치를 크게 흔들어 기존 능력 손상 | pre-training 대비 10분의 1 학습률 |
| 마스킹 경계 미검증 | prompt_len 계산 오류가 있어도 모름 | verify_mask.py로 -100 범위 확인 |
| 데이터 중복 방치 | 특정 표현만 과학습됨 | dup_instruct 0인지 확인 |
| base 체크포인트 없이 처음부터 SFT | pre-training 지식 없어 출력이 무의미 | 반드시 base ckpt.pt 로드 후 SFT |

## AI 협업 팁

SFT 관련 효과적인 AI 프롬프트 패턴:

1. **masking 구현 요청**: "Q:{instruction}\nA: 형식에서 prompt 구간 길이를 계산해 y[:mask_len] = -100으로 마스킹하는 build_example 함수 작성해줘"
2. **masking 검증 요청**: "각 토큰별로 y 값이 -100인지 실제 토큰인지 출력하는 verify_mask.py 작성해줘"
3. **데이터 점검 요청**: "JSONL 파일에서 empty response, 중복 instruction, 너무 짧은 응답을 찾는 check_data.py 작성해줘"

예시 프롬프트:
> "instructions.jsonl로 SFT finetune.py를 작성해줘. ckpt.pt 로드, Q/A 형식 직렬화, loss masking(-100), ignore_index=-100, lr=3e-5, 500 step, ckpt_sft.pt 저장. verify_mask.py도 함께 작성해줘."

## 운영 체크리스트

- [ ] loss masking이 없으면 어떤 문제가 생기는지 이해했는가?
- [ ] prompt 구간을 -100으로 마스킹하는 이유를 설명할 수 있는가?
- [ ] SFT에서 pre-training보다 낮은 학습률을 쓰는 이유를 이해했는가?
- [ ] verify_mask.py로 마스킹 경계가 올바른지 확인했는가?
- [ ] base 체크포인트 대비 SFT 후 출력 형식이 바뀌었는지 비교했는가?

## 처음 질문으로 돌아가기

SFT를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. loss masking을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 SFT 코드의 품질은 크게 다릅니다.

## 정리

SFT는 바이브코딩을 위한 LLM 밑바닥부터 시리즈에서 베이스 모델 위에 출력 습관을 덧입히는 단계입니다. loss masking, 낮은 학습률, 마스킹 검증의 역할을 이해했습니다. 다음 글에서는 이 SFT 모델을 FastAPI 서버와 브라우저 UI로 감싸 챗봇으로 완성합니다.

## 참고 자료

- [Finetuned Language Models Are Zero-Shot Learners](https://arxiv.org/abs/2109.01652)
- [Training language models to follow instructions](https://arxiv.org/abs/2203.02155)
- [Stanford Alpaca](https://github.com/tatsu-lab/stanford_alpaca)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/08-finetuning)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 LLM 밑바닥부터 (1/9): 글자를 숫자로 바꾸기
- 바이브코딩을 위한 LLM 밑바닥부터 (2/9): 정수에서 벡터로, 그리고 위치
- 바이브코딩을 위한 LLM 밑바닥부터 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기
- 바이브코딩을 위한 LLM 밑바닥부터 (4/9): 블록 하나, 깊이의 단위
- 바이브코딩을 위한 LLM 밑바닥부터 (5/9): 조립: GPT 모델 클래스 완성
- 바이브코딩을 위한 LLM 밑바닥부터 (6/9): 기울기로 배우기
- 바이브코딩을 위한 LLM 밑바닥부터 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기
- **바이브코딩을 위한 LLM 밑바닥부터 (8/9): 베이스 모델을 우리 작업에 맞추기 (현재 글)**
- 바이브코딩을 위한 LLM 밑바닥부터 (9/9): 직접 만든 LLM을 챗봇으로
<!-- toc:end -->

Tags: 바이브코딩, LLM밑바닥부터, SFT파인튜닝, AI코딩
