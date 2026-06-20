---
title: "바이브코딩을 위한 LLM 밑바닥부터 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기"
series: llm-from-scratch-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM밑바닥부터
- 샘플링
- PyTorch
- AI코딩
seo_description: "바이브코딩을 위한 LLM 밑바닥부터 7편: 샘플링. temperature, top-k, top-p로 decoding 정책을 제어하는 방법을 이해합니다."
---

# 바이브코딩을 위한 LLM 밑바닥부터 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기

이 글은 바이브코딩을 위한 LLM 밑바닥부터 시리즈의 7번째 글입니다.

학습이 끝나고 ckpt.pt를 저장하면 모델에게 말을 시켜 보고 싶어집니다. 하지만 model.eval()만 호출한다고 문장이 나오지는 않습니다. 생성 루프가 따로 필요합니다. 생성은 단순한 반복입니다. 현재 문맥을 넣고, 마지막 위치의 logits만 꺼내고, 그 분포에서 토큰 하나를 고른 뒤, 다시 문맥 뒤에 붙입니다. 이 과정을 반복하면 텍스트가 한 글자씩 자라납니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI가 생성한 추론 코드에서 temperature나 top-k 설정이 잘못되면 모델 품질이 아닌 decoding 정책 때문에 이상한 출력이 나오는데, 이 둘을 구분하려면 샘플링 메커니즘을 알아야 하기 때문입니다.

> 생성은 다음 토큰 분포에서 하나를 뽑고, 그 결과를 다시 입력으로 넣는 자기회귀 루프입니다. 모델 가중치가 생성의 기반이라면, 샘플링 전략은 그 기반을 어떤 성격의 출력으로 풀어낼지를 결정하는 정책입니다.

---

## 이 글에서 다룰 문제

- 자기회귀 생성 루프는 정확히 무엇을 반복할까요?
- temperature는 logits 분포를 어떻게 바꿀까요?
- top-k와 top-p는 후보군을 어떻게 다르게 자를까요?
- greedy decoding은 왜 자주 반복적인 출력을 만들까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?

샘플링 정책을 이해하면 AI에게 "temperature, top-k, top-p를 파라미터로 받는 generate 함수"를 정확하게 요청하고 검증할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "학습된 GPT로 텍스트 생성 코드 작성해줘"
→ temperature 없이 greedy decoding만 구현
→ 슬라이딩 윈도우(block_size 제한) 없음
→ top-k와 top-p를 동시에 잘못 적용
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "temperature, top_k, top_p를 파라미터로 받는
    generate 함수를 작성해줘.
    슬라이딩 윈도우 idx[:, -block_size:] 적용,
    마지막 위치 logits만 사용,
    seed 고정 옵션 포함해줘"
→ 재현 가능한 다양한 decoding 정책
→ 슬라이딩 윈도우로 긴 생성 지원
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 슬라이딩 윈도우 없음 | block_size 초과 시 오류 발생 | idx[:, -block_size:]로 컨텍스트 제한 |
| 마지막 위치가 아닌 모든 logits 사용 | 이전 위치 예측을 다음 토큰으로 오해 | logits[:, -1, :] 만 사용 |
| temperature=0으로 설정 | 0 나누기 오류 | max(temperature, 1e-5) 보호 |
| top-k와 top-p 동시 적용 순서 혼동 | 필터링 효과가 의도와 다름 | top-k 먼저, 그 다음 top-p |
| greedy decoding 결과만 평가 | 모델이 아닌 정책의 한계를 모델 탓으로 | temperature=0.8, top-k=20으로 비교 |

## AI 협업 팁

샘플링 관련 효과적인 AI 프롬프트 패턴:

1. **생성 루프 요청**: "마지막 위치 logits로 토큰 하나를 뽑아 자기회귀적으로 문장을 생성하는 generate 함수 작성해줘"
2. **정책 비교 요청**: "greedy, temperature=0.8/top-k=20, top-p=0.9 세 가지 정책으로 같은 프롬프트에서 출력을 비교하는 코드 작성해줘"
3. **다양성 측정 요청**: "생성된 텍스트의 distinct-2, distinct-3을 계산하는 함수 작성해줘"

예시 프롬프트:
> "ckpt.pt를 로드해서 프롬프트를 받아 텍스트를 생성하는 generate.py를 작성해줘. temperature, top_k, top_p 파라미터, 슬라이딩 윈도우, seed 옵션, argparse CLI 포함."

## 운영 체크리스트

- [ ] 자기회귀 생성 루프의 반복 단계를 설명할 수 있는가?
- [ ] temperature가 분포를 날카롭게 하거나 평평하게 만드는 방향을 이해했는가?
- [ ] top-k와 top-p의 차이를 설명할 수 있는가?
- [ ] idx[:, -block_size:]가 왜 필요한지 이해했는가?
- [ ] 같은 프롬프트에서 정책을 바꿔 출력 차이를 확인했는가?

## 처음 질문으로 돌아가기

샘플링을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. decoding 정책 파라미터를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 생성 코드의 제어 가능성은 크게 다릅니다.

## 정리

샘플링은 바이브코딩을 위한 LLM 밑바닥부터 시리즈에서 학습된 모델을 실제로 사용하는 첫 단계입니다. 자기회귀 루프, temperature, top-k, top-p의 역할을 이해했습니다. 다음 글에서는 이 베이스 모델 위에 instruction-response 형식을 얹는 파인튜닝을 다룹니다.

## 참고 자료

- [The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751)
- [How to generate text: using different decoding methods](https://huggingface.co/blog/how-to-generate)
- [nanoGPT model.py generate](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/07-inference)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 LLM 밑바닥부터 (1/9): 글자를 숫자로 바꾸기
- 바이브코딩을 위한 LLM 밑바닥부터 (2/9): 정수에서 벡터로, 그리고 위치
- 바이브코딩을 위한 LLM 밑바닥부터 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기
- 바이브코딩을 위한 LLM 밑바닥부터 (4/9): 블록 하나, 깊이의 단위
- 바이브코딩을 위한 LLM 밑바닥부터 (5/9): 조립: GPT 모델 클래스 완성
- 바이브코딩을 위한 LLM 밑바닥부터 (6/9): 기울기로 배우기
- **바이브코딩을 위한 LLM 밑바닥부터 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기 (현재 글)**
- 바이브코딩을 위한 LLM 밑바닥부터 (8/9): 베이스 모델을 우리 작업에 맞추기
- 바이브코딩을 위한 LLM 밑바닥부터 (9/9): 직접 만든 LLM을 챗봇으로
<!-- toc:end -->

Tags: 바이브코딩, LLM밑바닥부터, 샘플링, AI코딩
