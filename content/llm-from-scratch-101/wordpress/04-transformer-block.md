---
title: "바이브코딩을 위한 LLM 밑바닥부터 (4/9): 블록 하나, 깊이의 단위"
series: llm-from-scratch-101
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM밑바닥부터
- 트랜스포머블록
- PyTorch
- AI코딩
seo_description: "바이브코딩을 위한 LLM 밑바닥부터 4편: 트랜스포머 블록. FeedForward, residual connection, LayerNorm이 어떻게 깊이를 가능하게 하는지 이해합니다."
---

# 바이브코딩을 위한 LLM 밑바닥부터 (4/9): 블록 하나, 깊이의 단위

이 글은 바이브코딩을 위한 LLM 밑바닥부터 시리즈의 4번째 글입니다.

어텐션까지 구현하면 토큰이 서로를 본다는 것은 이해됩니다. 하지만 그 상태만으로는 모델이 깊어질 준비가 끝난 것이 아닙니다. 토큰 간 정보를 주고받을 수 있어도, 각 토큰 자리 안에서 표현을 더 풍부하게 가공하는 장치가 아직 부족합니다. 트랜스포머 블록은 이 문제를 해결합니다. 어텐션은 토큰 간 통신을 맡고, FeedForward는 각 위치 내부의 비선형 변환을 맡고, residual connection과 LayerNorm이 전체를 학습 가능한 형태로 묶습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI가 생성한 블록 코드에서 pre-norm과 post-norm 순서가 뒤바뀌면 깊은 모델에서 학습이 불안정해지는데, 이 차이를 알아야 코드를 검증할 수 있기 때문입니다.

> 블록은 attention으로 토큰 간 정보를 섞고, FeedForward로 각 토큰 내부 표현을 가공한 뒤, residual path로 원래 입력을 보존하는 잔차 래퍼입니다. 이 세 역할이 분리되어야 깊이를 안정적으로 쌓을 수 있습니다.

---

## 이 글에서 다룰 문제

- FeedForward는 왜 Linear(C, 4C) → GELU → Linear(4C, C) 형태를 쓸까요?
- residual connection은 학습을 어떻게 안정화할까요?
- pre-norm과 post-norm은 실전에서 어떤 차이를 만들까요?
- 블록의 파라미터 중 attention과 FFN 중 어느 쪽이 더 많을까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?

블록 구조를 이해하면 AI에게 "pre-norm, residual 연결 명시, shape 검증 포함" 같은 정확한 요청을 할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "트랜스포머 블록 코드 작성해줘"
→ post-norm 구현으로 깊은 모델에서 불안정
→ residual 연결 누락으로 기울기 소실
→ FFN 없이 attention만 있는 단순 구현
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "pre-norm 방식 트랜스포머 블록을 작성해줘.
    x = x + attn(ln1(x)) 형태로 residual 연결,
    x = x + ffn(ln2(x)) 형태로 FFN residual,
    입출력 shape (B,T,C) 동일성 assert 포함"
→ 안정적인 pre-norm 구현
→ attention + FFN 역할 분리 명확화
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| post-norm 구현 | 깊은 모델에서 초반 학습 불안정 | pre-norm: x = x + SubLayer(LN(x)) |
| residual 누락 | 깊어질수록 기울기 소실 | 항상 x = x + delta 형태 유지 |
| FFN 없이 attention만 쌓음 | 토큰 내부 표현 변환 부재 | attention + FFN 두 경로 모두 필수 |
| LayerNorm 위치 실수 | FFN 출력에 LN 적용으로 역할 혼동 | LN은 attention/FFN 입력 전에 |
| 블록 파라미터 분포 미확인 | FFN이 attention보다 크다는 사실 미인지 | print_trainable_parameters로 확인 |

## AI 협업 팁

트랜스포머 블록 관련 효과적인 AI 프롬프트 패턴:

1. **pre-norm 요청**: "x = x + attn(ln1(x)); x = x + ffn(ln2(x)) 형태의 pre-norm 블록 작성해줘"
2. **파라미터 분포 요청**: "블록의 attention, FFN, LayerNorm 파라미터 수를 각각 출력하는 코드 작성해줘"
3. **건강 진단 요청**: "attn_delta_norm과 ffn_delta_norm이 input_norm 대비 적절한 범위인지 확인하는 함수 작성해줘"

예시 프롬프트:
> "GPTConfig를 받는 pre-norm 트랜스포머 블록을 작성해줘. x = x + attn(ln1(x)), x = x + ffn(ln2(x)) 형태, FeedForward는 Linear(C,4C) -> GELU -> Linear(4C,C), 출력 shape == 입력 shape assert 포함."

## 운영 체크리스트

- [ ] 블록 안에서 attention과 FFN의 책임 차이를 한 문장씩 설명할 수 있는가?
- [ ] pre-norm residual 흐름을 다이어그램으로 그릴 수 있는가?
- [ ] 블록 입출력 shape이 항상 (B, T, C)로 유지되는지 확인했는가?
- [ ] FFN이 attention보다 더 많은 파라미터를 가진다는 점을 이해했는가?
- [ ] n_layer를 늘릴 때 파라미터 증가량을 대략 계산할 수 있는가?

## 처음 질문으로 돌아가기

트랜스포머 블록을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. pre-norm과 residual을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 코드의 학습 안정성은 크게 다릅니다.

## 정리

트랜스포머 블록은 바이브코딩을 위한 LLM 밑바닥부터 시리즈에서 깊이를 가능하게 하는 단위입니다. attention, FFN, residual, LayerNorm의 역할 분담을 이해했습니다. 다음 글에서는 지금까지 만든 부품을 하나의 GPT 클래스로 조립합니다.

## 참고 자료

- [On Layer Normalization in the Transformer Architecture](https://arxiv.org/abs/2002.04745)
- [Language Models are Unsupervised Multitask Learners (GPT-2)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
- [PyTorch nn.LayerNorm](https://pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/04-transformer-block)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 LLM 밑바닥부터 (1/9): 글자를 숫자로 바꾸기
- 바이브코딩을 위한 LLM 밑바닥부터 (2/9): 정수에서 벡터로, 그리고 위치
- 바이브코딩을 위한 LLM 밑바닥부터 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기
- **바이브코딩을 위한 LLM 밑바닥부터 (4/9): 블록 하나, 깊이의 단위 (현재 글)**
- 바이브코딩을 위한 LLM 밑바닥부터 (5/9): 조립: GPT 모델 클래스 완성
- 바이브코딩을 위한 LLM 밑바닥부터 (6/9): 기울기로 배우기
- 바이브코딩을 위한 LLM 밑바닥부터 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기
- 바이브코딩을 위한 LLM 밑바닥부터 (8/9): 베이스 모델을 우리 작업에 맞추기
- 바이브코딩을 위한 LLM 밑바닥부터 (9/9): 직접 만든 LLM을 챗봇으로
<!-- toc:end -->

Tags: 바이브코딩, LLM밑바닥부터, 트랜스포머블록, AI코딩
