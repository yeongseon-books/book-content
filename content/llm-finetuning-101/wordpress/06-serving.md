---
title: "바이브코딩을 위한 LLM 파인튜닝 (6/6): 모델 서빙"
series: llm-finetuning-101
episode: 6
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM파인튜닝
- 모델서빙
- FastAPI
- AI코딩
seo_description: "바이브코딩을 위한 LLM 파인튜닝 6편: 모델 서빙. FastAPI로 파인튜닝된 어댑터를 HTTP 엔드포인트 뒤에 두는 방법을 배웁니다."
---

# 바이브코딩을 위한 LLM 파인튜닝 (6/6): 모델 서빙

이 글은 바이브코딩을 위한 LLM 파인튜닝 시리즈의 6번째 글입니다.

학습은 배치와 에폭으로 사고하지만, 서빙은 요청당 지연 시간과 동시성으로 사고해야 합니다. 6편의 목표는 모델을 더 똑똑하게 만드는 것이 아닙니다. 이미 준비된 모델을 예측 가능한 HTTP 계약 뒤에 두는 것입니다. LoRA 어댑터가 서빙에서 어떤 배포 유연성을 만들어 주는지도 함께 봅니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI가 생성한 서빙 코드가 올바른 구조를 갖췄는지 확인하려면, 학습과 서빙의 경계를 알아야 하기 때문입니다.

> 서빙과 학습은 가중치만 공유할 뿐 다른 모든 것은 다릅니다 — 학습은 배치와 에폭으로 사고하지만 서빙은 요청당 지연과 동시성으로 사고하고, 이 전환이 코드 구조·메모리 정책·에러 처리를 결정합니다.

---

## 이 글에서 다룰 문제

- 파인튜닝된 모델을 FastAPI 엔드포인트 뒤에 두는 최소 구조는 무엇일까요?
- 서빙 코드에서 학습과 추론의 경계는 어디에 그어야 할까요?
- TestClient로 브라우저 없이 엔드포인트를 어떻게 검증할 수 있을까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- LoRA 어댑터 분리 배포는 어떤 이점을 주나요?

서빙 구조를 알면 AI에게 "요청마다 모델 로드, max_new_tokens 누락" 같은 함정을 피하는 코드를 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "파인튜닝된 모델 서빙 코드 만들어줘"
→ 요청마다 모델을 로드하는 코드 생성
→ max_new_tokens 없어 무한 생성 가능
→ model.eval() 누락으로 비결정적 출력
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "FastAPI lifespan으로 앱 시작 시 한 번만 모델을 로드하고,
    /health와 /generate 엔드포인트를 분리하고,
    Pydantic으로 max_new_tokens를 검증하는
    서빙 코드를 작성해줘. TestClient로 자체 검증도 포함해줘"
→ 콜드 스타트 없는 안정적 서빙
→ 엔드포인트 계약 명확화
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 요청마다 모델을 로드 | 모든 요청이 콜드 스타트가 되어 수 초의 지연 | 앱 시작 시 한 번만 모델 올리기 |
| max_new_tokens 미지정 | 무한히 긴 응답이 생성될 수 있음 | 항상 상한 지정 (예: 64~256) |
| model.eval() 누락 | 드롭아웃으로 비결정적 출력 발생 | 서빙 시 반드시 model.eval() 호출 |
| 에러를 그대로 노출 | 스택 트레이스가 클라이언트에 노출됨 | HTTPException으로 감싸기 |
| /health와 /generate 미분리 | 모델 상태 문제와 추론 실패 원인 구분 불가 | 두 엔드포인트 반드시 분리 |

## AI 협업 팁

모델 서빙 관련 효과적인 AI 프롬프트 패턴:

1. **서빙 골격 요청**: "FastAPI lifespan으로 모델 한 번 로드, /health와 /generate 분리 코드 작성해줘"
2. **검증 요청**: "TestClient로 /health가 {"status":"ok"}를 반환하는지, /generate가 completion을 반환하는지 확인하는 코드 작성해줘"
3. **어댑터 전환 요청**: "베이스 모델 하나에 여러 LoRA 어댑터를 이름으로 라우팅하는 패턴 코드 작성해줘"

예시 프롬프트:
> "sshleifer/tiny-gpt2와 LoRA 어댑터를 FastAPI로 서빙하는 코드를 작성해줘. 앱 시작 시 한 번만 모델 로드, /health와 /generate 분리, Pydantic으로 max_new_tokens 검증, TestClient로 두 엔드포인트 자체 검증 포함."

## 운영 체크리스트

- [ ] 모델 준비 책임과 HTTP 엔드포인트 책임을 구분해서 설명할 수 있는가?
- [ ] TestClient로 /health와 /generate를 검증하는 방법을 알고 있는가?
- [ ] 요청마다 모델을 로드하면 왜 느린지 이해했는가?
- [ ] LoRA 어댑터를 베이스와 분리 배포할 때 무엇이 좋아지는지 설명할 수 있는가?
- [ ] 1편부터 6편까지의 흐름을 하나의 연속된 과정으로 연결할 수 있는가?

## 처음 질문으로 돌아가기

모델 서빙을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 학습과 서빙의 경계를 아는 사람은 AI가 생성한 서빙 코드에서 구조적 결함을 훨씬 빨리 발견합니다.

## 정리

모델 서빙은 바이브코딩을 위한 LLM 파인튜닝의 마지막 단계입니다. 1편에서 수식 감각을 잡고, 2편에서 데이터를 준비하고, 3편에서 LoRA를 붙이고, 4편에서 학습을 검증하고, 5편에서 평가하고, 6편에서 HTTP 엔드포인트까지 연결했습니다. 이 흐름이 한 덩어리로 보인다면 시리즈의 목표를 달성한 것입니다.

## 참고 자료

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Starlette TestClient reference](https://www.starlette.io/testclient/)
- [PEFT — Multiple adapters](https://huggingface.co/docs/peft/main/en/developer_guides/lora#multiple-adapters)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-finetuning-101/ko/06-serving)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 LLM 파인튜닝 (1/6): LLM 파인튜닝 입문
- 바이브코딩을 위한 LLM 파인튜닝 (2/6): 데이터셋 준비와 전처리
- 바이브코딩을 위한 LLM 파인튜닝 (3/6): LoRA 어댑터 구성
- 바이브코딩을 위한 LLM 파인튜닝 (4/6): 학습 루프와 하이퍼파라미터
- 바이브코딩을 위한 LLM 파인튜닝 (5/6): 모델 평가
- **바이브코딩을 위한 LLM 파인튜닝 (6/6): 모델 서빙 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, LLM파인튜닝, 모델서빙, AI코딩
