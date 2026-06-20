---
title: "바이브코딩을 위한 LLM 밑바닥부터 (5/9): 조립: GPT 모델 클래스 완성"
series: llm-from-scratch-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM밑바닥부터
- GPT모델
- PyTorch
- AI코딩
seo_description: "바이브코딩을 위한 LLM 밑바닥부터 5편: GPT 모델 클래스 조립. 임베딩부터 LM head까지 forward pass 전체를 하나의 클래스로 연결합니다."
---

# 바이브코딩을 위한 LLM 밑바닥부터 (5/9): 조립: GPT 모델 클래스 완성

이 글은 바이브코딩을 위한 LLM 밑바닥부터 시리즈의 5번째 글입니다.

지금까지 토크나이저, 임베딩, 어텐션, 트랜스포머 블록을 차례로 만들었습니다. 남은 일은 생각보다 단순합니다. 그 부품들을 하나의 GPT(nn.Module) 클래스 안에 질서 있게 조립하는 것입니다. 토큰과 위치 임베딩이 입력을 만들고, 여러 블록이 표현을 다듬고, 마지막 LayerNorm과 LM head가 다음 토큰 분포를 출력합니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 GPT 클래스를 요청할 때 weight tying, sanity check, forward 계약을 명시하지 않으면, 생성된 코드의 초기 loss가 ln(vocab_size) 근처인지조차 확인하기 어렵기 때문입니다.

> GPT 클래스는 새로운 알고리즘이라기보다, 이미 만든 부품들을 올바른 순서로 연결하는 조립 코드입니다. 초기 loss가 ln(vocab_size) 근처라는 sanity check가 구현이 정상임을 확인하는 가장 빠른 방법입니다.

---

## 이 글에서 다룰 문제

- GPT 클래스는 어떤 순서로 부품을 호출할까요?
- weight tying이란 무엇이고 왜 유용할까요?
- 초기 loss가 ln(vocab_size) 근처여야 하는 이유는 무엇일까요?
- forward 계약을 어떻게 테스트할 수 있을까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?

GPT 조립 단계를 이해하면 AI가 생성한 모델 클래스의 forward pass가 올바른 순서인지 즉시 검증할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "GPT 모델 클래스 작성해줘"
→ weight tying 없어 파라미터 낭비
→ sanity check 없어 초기 loss 검증 불가
→ block_size 초과 시 에러 처리 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "GPTConfig를 받는 GPT 클래스를 작성해줘.
    lm_head.weight = token_emb.weight로 weight tying,
    랜덤 초기화 후 loss가 ln(vocab_size) 근처인지 sanity check,
    targets 없을 때 loss=None, block_size 초과 시 ValueError 포함"
→ 완전한 forward 계약
→ 구현 정확성 즉시 검증 가능
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| weight tying 없음 | lm_head가 중복 파라미터를 가짐 | lm_head.weight = token_emb.weight |
| sanity check 생략 | 초기 loss가 이상해도 모름 | ln(vocab_size) 근처인지 assert |
| block_size 초과 처리 없음 | pos_emb 인덱스 초과로 런타임 오류 | ValueError로 명시적 에러 |
| loss 계산 시 reshape 실수 | cross_entropy 입력 shape 불일치 | logits.view(B*T, V), targets.view(B*T) |
| 초기화 없이 기본값 사용 | 학습 초반 불안정 | Linear, Embedding std=0.02 초기화 |

## AI 협업 팁

GPT 모델 조립 관련 효과적인 AI 프롬프트 패턴:

1. **sanity check 요청**: "랜덤 초기화 후 loss가 ln(vocab_size) ± 0.5 이내인지 assert하는 sanity check 코드 작성해줘"
2. **forward 계약 테스트 요청**: "targets 없을 때 loss=None, targets 있을 때 finite loss, block_size 초과 시 ValueError를 검증하는 테스트 코드 작성해줘"
3. **파라미터 리포트 요청**: "임베딩, 블록, LM head의 파라미터 수를 각각 출력하는 report_model 함수 작성해줘"

예시 프롬프트:
> "GPTConfig(vocab_size=65, n_layer=6, n_head=4, n_embd=128, block_size=64)로 GPT 클래스를 작성해줘. weight tying, std=0.02 초기화, 초기 loss ln(65) 근처 sanity check, forward 계약 테스트 포함."

## 운영 체크리스트

- [ ] forward 패스를 임베딩 → 블록 반복 → ln_f → lm_head 순서로 설명할 수 있는가?
- [ ] lm_head.weight = token_emb.weight가 하는 일을 이해했는가?
- [ ] logits와 targets를 (B*T, ...) 형태로 펼치는 이유를 설명할 수 있는가?
- [ ] 랜덤 초기화 시 loss가 ln(vocab_size) 근처여야 한다는 sanity check를 실행했는가?
- [ ] test_forward_contract()로 입출력 계약을 자동 검증하는가?

## 처음 질문으로 돌아가기

GPT 모델 조립을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. sanity check와 forward 계약 테스트를 요청하는 사람과 그렇지 않은 사람이 AI에게 받는 코드의 신뢰도는 크게 다릅니다.

## 정리

GPT 모델 클래스 조립은 바이브코딩을 위한 LLM 밑바닥부터 시리즈의 핵심 통합 단계입니다. 부품들을 올바른 순서로 연결하고, weight tying과 sanity check로 구현을 검증했습니다. 다음 글에서는 이 모델에 실제 학습 루프를 붙입니다.

## 참고 자료

- [nanoGPT repository](https://github.com/karpathy/nanoGPT)
- [Using the Output Embedding to Improve Language Models](https://arxiv.org/abs/1608.05859)
- [PyTorch cross_entropy](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/05-gpt-model)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 LLM 밑바닥부터 (1/9): 글자를 숫자로 바꾸기
- 바이브코딩을 위한 LLM 밑바닥부터 (2/9): 정수에서 벡터로, 그리고 위치
- 바이브코딩을 위한 LLM 밑바닥부터 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기
- 바이브코딩을 위한 LLM 밑바닥부터 (4/9): 블록 하나, 깊이의 단위
- **바이브코딩을 위한 LLM 밑바닥부터 (5/9): 조립: GPT 모델 클래스 완성 (현재 글)**
- 바이브코딩을 위한 LLM 밑바닥부터 (6/9): 기울기로 배우기
- 바이브코딩을 위한 LLM 밑바닥부터 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기
- 바이브코딩을 위한 LLM 밑바닥부터 (8/9): 베이스 모델을 우리 작업에 맞추기
- 바이브코딩을 위한 LLM 밑바닥부터 (9/9): 직접 만든 LLM을 챗봇으로
<!-- toc:end -->

Tags: 바이브코딩, LLM밑바닥부터, GPT모델, AI코딩
