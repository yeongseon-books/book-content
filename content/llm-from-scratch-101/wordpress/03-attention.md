---
title: "바이브코딩을 위한 LLM 밑바닥부터 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기"
series: llm-from-scratch-101
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM밑바닥부터
- 어텐션
- PyTorch
- AI코딩
seo_description: "바이브코딩을 위한 LLM 밑바닥부터 3편: 어텐션. QKV 행렬과 causal mask로 각 토큰이 과거만 참조하는 메커니즘을 이해합니다."
---

# 바이브코딩을 위한 LLM 밑바닥부터 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기

이 글은 바이브코딩을 위한 LLM 밑바닥부터 시리즈의 3번째 글입니다.

임베딩이 만든 (B, T, C) 텐서는 각 위치의 토큰이 자기 자신만 알고 있는 상태입니다. 어텐션은 이 상태를 바꿉니다. 각 토큰이 다른 토큰들을 얼마나 봐야 하는지를 스스로 결정하게 만드는 것이 어텐션의 핵심입니다. Q·K·V 행렬이 그 결정의 수단이고, causal mask가 미래를 보지 못하게 막는 장치입니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI가 생성한 어텐션 코드에서 causal mask가 빠지면 학습이 되더라도 추론에서 정보 누수가 생기는데, 이를 알아채려면 메커니즘을 이해해야 하기 때문입니다.

> 어텐션은 각 토큰이 나머지 토큰들을 얼마나 볼지를 스스로 정하는 장치입니다 — Q·K의 내적이 "나는 너를 얼마나 보고 싶은가"를 결정하고, causal mask가 미래 토큰을 보지 못하게 막으며, V가 실제 정보를 건네줍니다.

---

## 이 글에서 다룰 문제

- Q, K, V 행렬은 각각 어떤 역할을 할까요?
- causal mask는 왜 필요하고 어떻게 구현할까요?
- 멀티헤드 어텐션은 단일 헤드보다 무엇을 더 할 수 있을까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- attention score를 sqrt(head_size)로 나누는 이유는 무엇일까요?

어텐션 구조를 이해하면 AI에게 "causal mask 포함, head 분리 구현, shape 검증 포함" 같은 정확한 요청을 할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "셀프 어텐션 코드 작성해줘"
→ causal mask 없어 미래 토큰을 학습에 사용
→ sqrt 스케일링 누락으로 attention 분포 폭발
→ 멀티헤드 분리 로직 없이 단일 헤드만 구현
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "n_head=4, n_embd=128의 CausalSelfAttention을 작성해줘.
    tril로 causal mask 구현, sqrt(head_size)로 스케일링,
    (B,T,C) shape 유지 검증, 드롭아웃 포함해줘"
→ 미래 정보 누수 없는 올바른 구현
→ shape 계약과 스케일링 명확화
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| causal mask 없이 구현 | 미래 토큰 정보가 학습 신호에 섞임 | tril mask로 미래 위치를 -inf로 마스킹 |
| sqrt 스케일링 생략 | attention logit 폭발로 softmax가 한쪽에 몰림 | qi @ ki / sqrt(head_size) |
| n_embd % n_head != 0 | head 분리 시 assertion 오류 | 설정 시 항상 나누어 떨어지는지 확인 |
| 출력 projection 생략 | 헤드를 합친 후 선형 변환 없음 | multi-head 출력 후 proj 레이어 필수 |
| shape 변환 순서 혼동 | transpose 후 contiguous 없이 view 실패 | transpose → contiguous → view |

## AI 협업 팁

어텐션 관련 효과적인 AI 프롬프트 패턴:

1. **causal mask 요청**: "torch.tril로 하삼각 행렬을 만들고 미래 위치를 float('-inf')로 마스킹하는 코드 작성해줘"
2. **shape 추적 요청**: "CausalSelfAttention의 Q, K, V, wei, out 각 단계별 shape를 주석으로 표시해줘"
3. **멀티헤드 검증 요청**: "n_head=4일 때 헤드별로 분리된 attention weight를 시각화하는 코드 작성해줘"

예시 프롬프트:
> "GPTConfig(n_head=4, n_embd=128, block_size=64, dropout=0.1)를 받는 CausalSelfAttention을 작성해줘. tril causal mask, sqrt 스케일링, 멀티헤드 분리, out projection, 드롭아웃 포함, 출력 shape (B,T,C) assert 포함."

## 운영 체크리스트

- [ ] Q, K, V가 각각 무엇을 계산하는지 한 문장으로 설명할 수 있는가?
- [ ] causal mask가 없으면 어떤 문제가 생기는지 이해했는가?
- [ ] sqrt(head_size) 스케일링이 왜 필요한지 설명할 수 있는가?
- [ ] 멀티헤드 어텐션의 shape 변환 순서를 설명할 수 있는가?
- [ ] 출력 shape이 입력 shape (B, T, C)와 동일하게 유지되는지 확인했는가?

## 처음 질문으로 돌아가기

어텐션을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. causal mask와 스케일링을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 코드의 정확도는 크게 다릅니다.

## 정리

어텐션은 바이브코딩을 위한 LLM 밑바닥부터 시리즈에서 가장 핵심적인 메커니즘입니다. Q·K·V 행렬, causal mask, sqrt 스케일링, 멀티헤드 분리가 어떻게 협력하는지 이해했습니다. 다음 글에서는 이 어텐션 위에 FeedForward와 residual connection을 더해 트랜스포머 블록을 완성합니다.

## 참고 자료

- [Attention is All You Need](https://arxiv.org/abs/1706.03762)
- [nanoGPT model.py](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [PyTorch scaled_dot_product_attention](https://pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/03-attention)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 LLM 밑바닥부터 (1/9): 글자를 숫자로 바꾸기
- 바이브코딩을 위한 LLM 밑바닥부터 (2/9): 정수에서 벡터로, 그리고 위치
- **바이브코딩을 위한 LLM 밑바닥부터 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기 (현재 글)**
- 바이브코딩을 위한 LLM 밑바닥부터 (4/9): 블록 하나, 깊이의 단위
- 바이브코딩을 위한 LLM 밑바닥부터 (5/9): 조립: GPT 모델 클래스 완성
- 바이브코딩을 위한 LLM 밑바닥부터 (6/9): 기울기로 배우기
- 바이브코딩을 위한 LLM 밑바닥부터 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기
- 바이브코딩을 위한 LLM 밑바닥부터 (8/9): 베이스 모델을 우리 작업에 맞추기
- 바이브코딩을 위한 LLM 밑바닥부터 (9/9): 직접 만든 LLM을 챗봇으로
<!-- toc:end -->

Tags: 바이브코딩, LLM밑바닥부터, 어텐션, AI코딩
