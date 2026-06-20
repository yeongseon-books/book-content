---
title: "바이브코딩을 위한 LLM 밑바닥부터 (9/9): 직접 만든 LLM을 챗봇으로"
series: llm-from-scratch-101
episode: 9
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM밑바닥부터
- 챗봇
- FastAPI
- AI코딩
seo_description: "바이브코딩을 위한 LLM 밑바닥부터 9편: 챗봇 래퍼. FastAPI lifespan과 SSE 스트리밍으로 직접 만든 LLM을 대화형 앱으로 완성합니다."
---

# 바이브코딩을 위한 LLM 밑바닥부터 (9/9): 직접 만든 LLM을 챗봇으로

이 글은 바이브코딩을 위한 LLM 밑바닥부터 시리즈의 마지막 글입니다.

generate.py까지 만들면 모델은 동작합니다. 하지만 그 상태는 아직 개발자 도구에 가깝습니다. 대화형 앱으로 바꾸려면 모델만으로는 부족합니다. 대화 히스토리를 어떤 형식으로 직렬화할지, 모델을 언제 한 번만 메모리에 올릴지, 토큰을 스트리밍으로 흘릴지, 브라우저에서 어떻게 받을지까지 함께 설계해야 합니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 챗봇 서버 코드를 요청할 때 lifespan 로딩, multi-turn prompt format, SSE 이벤트 타입을 명시하지 않으면, 생성된 코드가 실제로 동작하는 챗봇이 아닌 단순 API 래퍼에 머물기 때문입니다.

> 챗봇 품질은 모델 가중치만으로 결정되지 않습니다. prompt format, lifespan 로딩, 스트리밍 방식, unsupported character 처리 같은 시스템 수준 결정이 사용자 경험에 직접 영향을 줍니다.

---

## 이 글에서 다룰 문제

- 챗봇은 모델 외에 어떤 구성 요소를 더 필요로 할까요?
- multi-turn prompt format은 왜 직접 설계해야 할까요?
- FastAPI lifespan으로 모델을 한 번만 로드하면 무엇이 좋아질까요?
- SSE 스트리밍과 동기 응답은 각각 어떤 상황에 적합할까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?

챗봇 시스템 구조를 이해하면 AI에게 "lifespan 로딩, multi-turn 직렬화, SSE 이벤트 분리, 컨텍스트 오버플로 처리" 같은 정확한 요청을 할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "FastAPI로 챗봇 서버 코드 작성해줘"
→ 요청마다 모델 로드하는 구현
→ multi-turn 히스토리 직렬화 없음
→ SSE 스트리밍 없이 단순 응답만
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "FastAPI lifespan으로 시작 시 한 번만 모델 로드,
    User:/Bot: 형식으로 multi-turn 히스토리 직렬화,
    동기 /chat과 SSE /chat/stream 두 엔드포인트,
    MAX_HISTORY_TURNS로 컨텍스트 오버플로 방지,
    vocab 밖 문자 드롭 및 400 처리 포함해줘"
→ 실사용 가능한 챗봇 시스템
→ 대화 히스토리와 스트리밍 지원
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 요청마다 모델 로드 | 모든 요청이 콜드 스타트 (수 초 지연) | FastAPI lifespan에서 한 번만 로드 |
| multi-turn 직렬화 없음 | 이전 대화를 모르는 단발성 응답 | User:/Bot: 형식으로 히스토리 이어 붙이기 |
| 컨텍스트 오버플로 무시 | 긴 대화에서 조용히 오류 발생 | MAX_HISTORY_TURNS로 오래된 턴 제거 |
| SSE 개행 문자 미이스케이프 | 브라우저에서 이벤트 구분 오류 | \n을 \\n으로 이스케이프 |
| vocab 밖 문자 처리 없음 | 빈 입력이 되어 모델 호출 실패 | 드롭 후 빈 결과면 400 반환 |

## AI 협업 팁

챗봇 래퍼 관련 효과적인 AI 프롬프트 패턴:

1. **lifespan 요청**: "FastAPI asynccontextmanager lifespan으로 서버 시작 시 모델과 토크나이저를 한 번만 로드하는 코드 작성해줘"
2. **multi-turn 직렬화 요청**: "대화 히스토리를 User:/Bot: 형식으로 이어 붙이고 마지막에 Bot:을 남기는 build_prompt 함수 작성해줘"
3. **SSE 스트리밍 요청**: "token, warning, done 세 가지 이벤트 타입으로 토큰을 스트리밍하는 /chat/stream GET 엔드포인트 작성해줘"

예시 프롬프트:
> "ckpt_sft.pt를 FastAPI로 서빙하는 server.py를 작성해줘. lifespan 로딩, /health, 동기 /chat, SSE /chat/stream, build_prompt(history, prompt), vocab 밖 문자 400 처리, MAX_HISTORY_TURNS=10, MAX_NEW_TOKENS=120."

## 운영 체크리스트

- [ ] multi-turn history를 어떤 텍스트 템플릿으로 직렬화하는지 명확히 정했는가?
- [ ] FastAPI lifespan에서 모델을 한 번만 로드하도록 구현했는가?
- [ ] /chat과 /chat/stream 두 경로가 각각 어떤 UX를 주는지 확인했는가?
- [ ] unsupported character가 모두 드롭되어 빈 입력이 되는 경우를 400 오류로 처리하는가?
- [ ] MAX_HISTORY_TURNS로 컨텍스트 오버플로를 방지하고 있는가?

## 처음 질문으로 돌아가기

챗봇 래퍼를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 시스템 구성 요소를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 챗봇 코드의 완성도는 크게 다릅니다.

## 정리

챗봇 래퍼는 바이브코딩을 위한 LLM 밑바닥부터 시리즈의 마지막 단계입니다. 토크나이저에서 출발해 임베딩, 어텐션, 블록, GPT 클래스, 학습, 샘플링, SFT, 챗봇 래퍼까지 이어졌습니다. 약 120만 파라미터의 작은 char-level GPT이지만, LLM 애플리케이션의 전체 흐름을 끝에서 끝까지 직접 만져 본 셈입니다.

## 참고 자료

- [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)
- [MDN EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/09-chatbot-wrapper)

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
- 바이브코딩을 위한 LLM 밑바닥부터 (8/9): 베이스 모델을 우리 작업에 맞추기
- **바이브코딩을 위한 LLM 밑바닥부터 (9/9): 직접 만든 LLM을 챗봇으로 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, LLM밑바닥부터, 챗봇, AI코딩
