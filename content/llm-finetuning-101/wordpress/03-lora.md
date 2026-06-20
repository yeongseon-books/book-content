---
title: "바이브코딩을 위한 LLM 파인튜닝 (3/6): LoRA 어댑터 구성"
series: llm-finetuning-101
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM파인튜닝
- LoRA
- PEFT
- AI코딩
seo_description: "바이브코딩을 위한 LLM 파인튜닝 3편: LoRA 어댑터 구성. target_modules 배선 검증과 학습 파라미터 비율 확인 방법을 익힙니다."
---

# 바이브코딩을 위한 LLM 파인튜닝 (3/6): LoRA 어댑터 구성

이 글은 바이브코딩을 위한 LLM 파인튜닝 시리즈의 3번째 글입니다.

LoRA 어댑터는 모델 전체를 갈아엎는 장치가 아니라, 선택한 선형 레이어 옆에 좁은 보정 경로를 덧붙이는 방식입니다. 3편부터는 실제 모델 객체를 만집니다. 목표는 성능 경쟁이 아니라 연결이 올바른지 검증하는 것입니다. target_modules에 오타가 하나만 있어도 print_trainable_parameters()는 0을 출력하고, 학습은 돌아가지만 손실은 움직이지 않는 가장 난감한 실패가 시작됩니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI가 생성한 LoRA 코드가 올바로 연결됐는지 확인하려면, 배선 검증 방법을 알아야 하기 때문입니다.

> LoRA 어댑터는 선택된 linear 층 위가 아니라 그 옆에 좁은 보정 경로를 더하는 구조입니다 — rank·scaling·target_modules 선택은 본질적으로 배선 결정이고, 여기서의 오타 하나가 조용한 zero-gradient 학습으로 숨어 듭니다.

---

## 이 글에서 다룰 문제

- LoraConfig에서 실제로 이해해야 할 필드는 무엇일까요?
- target_modules를 잘못 지정하면 어떤 문제가 생길까요?
- 작은 GPT-2 계열 모델에서는 학습 가능한 파라미터 비율이 얼마나 낮아질까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

LoRA 구성 단계의 핵심은 성능 튜닝이 아니라 연결 검증입니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "LoraConfig(r=8, target_modules=['q_proj', 'v_proj'])를
    GPT-2에 적용해줘"
→ GPT-2의 실제 모듈 이름은 c_attn, c_proj
→ trainable params: 0 출력, 학습은 돌아가지만 아무것도 바뀌지 않음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "sshleifer/tiny-gpt2 모델의 선형 레이어 이름을
    named_modules()로 먼저 확인하고, LoRA를 c_attn과
    c_proj에 붙인 뒤 trainable%를 출력해줘"
→ 모델별 실제 모듈 이름 확인 후 적용
→ trainable% 1~3% 범위 확인
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| target_modules 오타 | 에러 없이 trainable params: 0만 출력 | print_trainable_parameters()로 항상 확인 |
| r과 alpha를 따로 놀게 둠 | r=64, alpha=16이면 보정이 너무 약함 | alpha = 2 * r이 무난한 기본값 |
| bias="all"을 가볍게 켬 | 어댑터 커지고 베이스 상태 복구 어려움 | "none"이 기본값인 이유가 있음 |
| 모든 선형 레이어에 LoRA 부착 | 학습 파라미터가 두세 배 증가 | 어텐션 QKV만으로 충분한 경우 많음 |
| Conv1D와 Linear를 같은 것으로 봄 | GPT-2는 Conv1D 사용, fan_in/out 어긋남 | PEFT가 처리하게 두는 편이 안전 |

## AI 협업 팁

LoRA 어댑터 구성 관련 효과적인 AI 프롬프트 패턴:

1. **모듈 확인 요청**: "이 모델의 named_modules()에서 Linear 레이어 이름을 전부 출력해줘"
2. **배선 검증 요청**: "LoRA 부착 후 requires_grad=True인 파라미터가 lora_A, lora_B인지 확인해줘"
3. **설정 비교 요청**: "r=8과 r=16에서 trainable%가 각각 얼마인지 비교해줘"

예시 프롬프트:
> "sshleifer/tiny-gpt2 모델에 LoRA를 붙이는 코드를 작성해줘. 먼저 named_modules()로 선형 레이어 이름을 확인하고, LoraConfig를 정의한 뒤 print_trainable_parameters()로 비율이 0이 아닌지 검증해줘."

## 운영 체크리스트

- [ ] LoraConfig 핵심 필드의 의미를 설명할 수 있는가?
- [ ] target_modules가 모델마다 달라지는 이유를 이해했는가?
- [ ] trainable%가 1~3% 범위에 들어오는지 확인했는가?
- [ ] requires_grad=True인 파라미터가 lora_A, lora_B뿐인지 확인했는가?
- [ ] 다음 글에서 이 모델에 최소 한 번의 학습 스텝을 밀어 넣을 준비가 됐는가?

## 처음 질문으로 돌아가기

LoRA 어댑터 구성을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 배선 검증 습관을 가진 사람과 그렇지 않은 사람이 AI에게 받는 코드의 신뢰도는 크게 다릅니다.

## 정리

LoRA 어댑터 구성은 바이브코딩을 위한 LLM 파인튜닝의 핵심 주제 중 하나입니다. 어댑터가 어디에 붙는지, 얼마나 많은 파라미터가 학습 대상이 되는지만 확인해도 절반은 끝난 셈입니다. 다음 글에서는 학습 루프와 하이퍼파라미터를 다룹니다.

## 참고 자료

- [PEFT quicktour](https://huggingface.co/docs/peft/quicktour)
- [LoRA paper](https://arxiv.org/abs/2106.09685)
- [PEFT LoraConfig source](https://github.com/huggingface/peft/blob/main/src/peft/tuners/lora/config.py)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-finetuning-101/ko/03-lora)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 LLM 파인튜닝 (1/6): LLM 파인튜닝 입문
- 바이브코딩을 위한 LLM 파인튜닝 (2/6): 데이터셋 준비와 전처리
- **바이브코딩을 위한 LLM 파인튜닝 (3/6): LoRA 어댑터 구성 (현재 글)**
- 바이브코딩을 위한 LLM 파인튜닝 (4/6): 학습 루프와 하이퍼파라미터
- 바이브코딩을 위한 LLM 파인튜닝 (5/6): 모델 평가
- 바이브코딩을 위한 LLM 파인튜닝 (6/6): 모델 서빙
<!-- toc:end -->

Tags: 바이브코딩, LLM파인튜닝, LoRA, AI코딩
