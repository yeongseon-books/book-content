---
title: "바이브코딩을 위한 LLM 밑바닥부터 (6/9): 기울기로 배우기"
series: llm-from-scratch-101
episode: 6
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM밑바닥부터
- 학습루프
- PyTorch
- AI코딩
seo_description: "바이브코딩을 위한 LLM 밑바닥부터 6편: 학습 루프. forward→loss→backward→step 네 줄의 반복으로 GPT를 실제로 학습시키는 방법을 이해합니다."
---

# 바이브코딩을 위한 LLM 밑바닥부터 (6/9): 기울기로 배우기

이 글은 바이브코딩을 위한 LLM 밑바닥부터 시리즈의 6번째 글입니다.

모델 클래스를 완성하고 나면 이제 정말 학습을 시작할 수 있습니다. PyTorch 코드로 내려오면 학습 루프의 핵심은 놀랄 만큼 짧습니다. 배치를 뽑고, loss를 계산하고, 역전파하고, optimizer가 한 걸음 움직이는 일이 반복될 뿐입니다. 하지만 짧다고 단순한 것은 아닙니다. 학습률 스케줄링, gradient clipping, eval 주기, 체크포인트 저장은 처음부터 품질과 디버깅 비용을 좌우합니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI가 생성한 학습 코드에서 zero_grad와 backward 순서가 뒤바뀌거나 gradient clipping이 빠지면 학습이 불안정해지는데, 이 순서를 알아야 코드를 검증할 수 있기 때문입니다.

> Training loop는 'forward → loss → backward → step'이라는 네 줄의 무한 반복이고, GPT를 학습시키는 일은 이 네 줄을 안정적으로 수십만 번 도는 일입니다. 나머지 모든 것은 이 과정을 안정적이고 재현 가능하게 만드는 운영 장치입니다.

---

## 이 글에서 다룰 문제

- 학습 루프의 핵심 다섯 줄은 무엇일까요?
- AdamW는 SGD보다 트랜스포머 학습에서 왜 다루기 쉬울까요?
- warmup + cosine decay 스케줄은 어떤 도움을 줄까요?
- gradient clipping은 왜 필수 안전장치인가요?
- 학습이 이상할 때 가장 먼저 점검해야 할 것은 무엇일까요?

학습 루프를 이해하면 AI에게 "zero_grad 먼저, gradient clipping 포함, eval 주기 명시" 같은 정확한 요청을 할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "GPT 학습 코드 작성해줘"
→ gradient clipping 없어 NaN 발생 가능
→ zero_grad 위치가 backward 이후로 잘못됨
→ eval 루프 없어 과적합 감지 불가
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "AdamW 옵티마이저, warmup+cosine decay 스케줄,
    clip_grad_norm_(1.0), 500 step마다 train/val loss 출력,
    체크포인트 저장을 포함한 train.py를 작성해줘.
    zero_grad → forward → backward → clip → step 순서 지켜줘"
→ 안정적이고 재현 가능한 학습 루프
→ 회귀 감지와 체크포인트 관리 자동화
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| gradient clipping 누락 | 폭발적 gradient로 NaN loss 발생 | clip_grad_norm_(model, 1.0) 항상 포함 |
| zero_grad 순서 오류 | 이전 step의 gradient가 누적됨 | forward 전에 반드시 zero_grad |
| eval 루프 없음 | 과적합이 일어나도 감지 불가 | train/val loss 함께 추적 |
| 체크포인트 미저장 | 학습 중단 시 모든 결과 소실 | config + state_dict 함께 저장 |
| .item() 없이 loss 누적 | tensor 참조가 남아 메모리 증가 | loss_val = loss.item()로 분리 |

## AI 협업 팁

학습 루프 관련 효과적인 AI 프롬프트 패턴:

1. **루프 골격 요청**: "zero_grad → forward → backward → clip_grad_norm_(1.0) → step 순서로 학습 루프 작성해줘"
2. **과적합 감지 요청**: "500 step마다 @torch.no_grad()로 train/val loss를 추정하는 estimate_loss 함수 작성해줘"
3. **한 배치 overfit 테스트 요청**: "같은 배치로 200 step 학습해서 loss가 0.1 이하로 내려가는지 검증하는 코드 작성해줘"

예시 프롬프트:
> "GPT 모델 학습 train.py를 작성해줘. AdamW(lr=3e-4), warmup 100 step + cosine decay 5000 step, clip_grad_norm_(1.0), 500 step마다 train/val loss 출력, ckpt.pt에 config와 state_dict 함께 저장."

## 운영 체크리스트

- [ ] zero_grad → forward → backward → clip → step 순서를 설명할 수 있는가?
- [ ] gradient clipping이 왜 필요한지 이해했는가?
- [ ] warmup + cosine decay 스케줄의 곡선을 그릴 수 있는가?
- [ ] 한 배치 overfit 테스트로 구현 경로를 검증했는가?
- [ ] ckpt.pt에 모델 가중치, config, 토크나이저 정보를 함께 저장했는가?

## 처음 질문으로 돌아가기

학습 루프를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 루프 순서와 안전장치를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 코드의 안정성은 크게 다릅니다.

## 정리

학습 루프는 바이브코딩을 위한 LLM 밑바닥부터 시리즈에서 모델이 처음으로 데이터에서 패턴을 배우는 단계입니다. forward→backward→step의 핵심과 gradient clipping, eval 루프, 체크포인트 저장을 함께 구성했습니다. 다음 글에서는 저장된 체크포인트를 불러와 텍스트를 생성하는 추론을 다룹니다.

## 참고 자료

- [Decoupled Weight Decay Regularization (AdamW)](https://arxiv.org/abs/1711.05101)
- [nanoGPT train.py](https://github.com/karpathy/nanoGPT/blob/master/train.py)
- [PyTorch clip_grad_norm_](https://pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/06-training-loop)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 LLM 밑바닥부터 (1/9): 글자를 숫자로 바꾸기
- 바이브코딩을 위한 LLM 밑바닥부터 (2/9): 정수에서 벡터로, 그리고 위치
- 바이브코딩을 위한 LLM 밑바닥부터 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기
- 바이브코딩을 위한 LLM 밑바닥부터 (4/9): 블록 하나, 깊이의 단위
- 바이브코딩을 위한 LLM 밑바닥부터 (5/9): 조립: GPT 모델 클래스 완성
- **바이브코딩을 위한 LLM 밑바닥부터 (6/9): 기울기로 배우기 (현재 글)**
- 바이브코딩을 위한 LLM 밑바닥부터 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기
- 바이브코딩을 위한 LLM 밑바닥부터 (8/9): 베이스 모델을 우리 작업에 맞추기
- 바이브코딩을 위한 LLM 밑바닥부터 (9/9): 직접 만든 LLM을 챗봇으로
<!-- toc:end -->

Tags: 바이브코딩, LLM밑바닥부터, 학습루프, AI코딩
