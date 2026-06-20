---
title: "바이브코딩을 위한 LLM 밑바닥부터 (2/9): 정수에서 벡터로, 그리고 위치"
series: llm-from-scratch-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM밑바닥부터
- 임베딩
- PyTorch
- AI코딩
seo_description: "바이브코딩을 위한 LLM 밑바닥부터 2편: 임베딩. nn.Embedding이 룩업 테이블로 동작하는 방식과 (B,T,C) 텐서 구조를 이해합니다."
---

# 바이브코딩을 위한 LLM 밑바닥부터 (2/9): 정수에서 벡터로, 그리고 위치

이 글은 바이브코딩을 위한 LLM 밑바닥부터 시리즈의 2번째 글입니다.

정수 ID 배열만으로는 신경망이 아무 의미도 읽어 내지 못합니다. `12, 4, 38` 같은 숫자열은 아직 인덱스 목록일 뿐입니다. 의미는 임베딩 테이블 안에서 학습된 벡터를 통해 비로소 생깁니다. 여기에 한 가지가 더 필요합니다. 같은 토큰이라도 몇 번째 위치에 있는지에 따라 역할이 다르므로, 토큰 임베딩과 위치 임베딩이 함께 입력을 만들어야 합니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 임베딩 코드를 요청할 때 `(B, T, C)` 텐서 shape를 명시하지 않으면, 생성된 코드의 차원이 맞는지 검증하기 어렵기 때문입니다.

> 모델이 읽는 첫 입력 벡터는 token_emb + pos_emb입니다. 이 덧셈이 "무슨 토큰인가"와 "몇 번째 위치인가"를 동시에 담는 시작점이고, 이후 모든 블록은 이 (B, T, C) 텐서를 받아서 같은 shape를 유지한 채 내용만 바꿉니다.

---

## 이 글에서 다룰 문제

- nn.Embedding은 실제로 어떤 연산을 수행할까요?
- 토큰 임베딩만으로는 왜 충분하지 않을까요?
- (B, T, C) 텐서 shape는 무엇을 의미할까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 임베딩 차원이 모델 크기에 어떻게 연결될까요?

임베딩 shape 감각을 여기서 잡아 두면 이후 어텐션과 블록 구현의 디버깅이 크게 단순해집니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "GPT 임베딩 코드 작성해줘"
→ token_emb만 있고 pos_emb 없는 코드 생성
→ (B, T, C) shape 검증 없음
→ vocab_size와 n_embd 관계 불명확
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "vocab_size=65, n_embd=128, block_size=64로
    token_emb과 pos_emb를 더하는 임베딩 레이어를 작성해줘.
    출력 shape이 (B, T, C)인지 assert로 검증도 포함해줘"
→ 위치 정보가 포함된 완전한 입력 텐서
→ shape 계약 명시적 검증
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| pos_emb를 빼먹음 | 위치 정보 없이 순서가 모두 같은 토큰으로 처리 | token_emb + pos_emb 항상 함께 |
| vocab_size를 하드코딩 | 데이터 변경 시 오류 발생 | GPTConfig로 중앙 관리 |
| B, T, C 중 하나를 잘못 이해 | shape 불일치로 forward 실패 | B=배치, T=시퀀스 길이, C=임베딩 차원 |
| block_size 초과 입력을 허용 | pos_emb 인덱스 초과 오류 | 입력 길이를 block_size로 clamp |
| 임베딩 초기화를 기본값에 맡김 | 학습 초반 불안정 | std=0.02로 명시적 초기화 |

## AI 협업 팁

임베딩 관련 효과적인 AI 프롬프트 패턴:

1. **shape 검증 요청**: "token_emb + pos_emb 후 출력 shape이 (B, T, C)인지 assert하는 코드 작성해줘"
2. **파라미터 계산 요청**: "vocab_size=65, n_embd=128일 때 token_emb와 pos_emb의 파라미터 수를 계산해줘"
3. **초기화 요청**: "nn.Embedding weight를 std=0.02로 초기화하는 코드 추가해줘"

예시 프롬프트:
> "GPTConfig(vocab_size=65, n_embd=128, block_size=64)를 받아 token_emb + pos_emb를 더하는 임베딩 레이어를 작성해줘. 출력 shape (B, T, C) 검증 assert 포함, 드롭아웃도 추가해줘."

## 운영 체크리스트

- [ ] nn.Embedding이 룩업 테이블처럼 동작한다는 것을 이해했는가?
- [ ] token_emb + pos_emb 덧셈이 왜 필요한지 설명할 수 있는가?
- [ ] (B, T, C)에서 각 차원이 무엇을 의미하는지 설명할 수 있는가?
- [ ] block_size를 초과하는 입력이 들어오면 어떤 오류가 나는지 알고 있는가?
- [ ] 다음 글에서 이 (B, T, C) 텐서가 어텐션 레이어의 입력이 된다는 점을 연결할 수 있는가?

## 처음 질문으로 돌아가기

임베딩을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. (B, T, C) shape를 명시하는 사람과 그렇지 않은 사람이 AI에게 받는 코드의 신뢰도는 크게 다릅니다.

## 정리

임베딩은 바이브코딩을 위한 LLM 밑바닥부터 시리즈의 두 번째 단계입니다. nn.Embedding을 룩업 테이블로 이해하고, token_emb + pos_emb로 (B, T, C) 텐서를 만드는 과정을 살펴봤습니다. 다음 글에서는 이 텐서가 어떤 토큰을 얼마나 볼지 결정하는 어텐션을 다룹니다.

## 참고 자료

- [PyTorch nn.Embedding](https://pytorch.org/docs/stable/generated/torch.nn.Embedding.html)
- [Attention is All You Need](https://arxiv.org/abs/1706.03762)
- [nanoGPT model.py](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/02-embedding)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 LLM 밑바닥부터 (1/9): 글자를 숫자로 바꾸기
- **바이브코딩을 위한 LLM 밑바닥부터 (2/9): 정수에서 벡터로, 그리고 위치 (현재 글)**
- 바이브코딩을 위한 LLM 밑바닥부터 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기
- 바이브코딩을 위한 LLM 밑바닥부터 (4/9): 블록 하나, 깊이의 단위
- 바이브코딩을 위한 LLM 밑바닥부터 (5/9): 조립: GPT 모델 클래스 완성
- 바이브코딩을 위한 LLM 밑바닥부터 (6/9): 기울기로 배우기
- 바이브코딩을 위한 LLM 밑바닥부터 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기
- 바이브코딩을 위한 LLM 밑바닥부터 (8/9): 베이스 모델을 우리 작업에 맞추기
- 바이브코딩을 위한 LLM 밑바닥부터 (9/9): 직접 만든 LLM을 챗봇으로
<!-- toc:end -->

Tags: 바이브코딩, LLM밑바닥부터, 임베딩, AI코딩
