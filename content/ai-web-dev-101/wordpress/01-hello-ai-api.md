---
series: ai-web-dev-101
episode: 1
title: "바이브코딩을 위한 AI 웹 개발 (1/7): AI API 첫 걸음"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - AI 웹 개발
  - OpenAI API
  - Python
  - LLM
language: ko
---

# 바이브코딩을 위한 AI 웹 개발 (1/7): AI API 첫 걸음

> 이 글은 **바이브코딩을 위한 AI 웹 개발** 시리즈 1편입니다. OpenAI API로 첫 번째 요청을 보내며 인증, 응답 구조, 오류 처리, 토큰 비용 감각을 익힙니다.

바이브코딩으로 AI 앱을 만들다 보면 ChatGPT를 브라우저에서 쓰는 것과, 내 서비스 코드에서 모델을 호출하는 것이 어떻게 다른지 금방 실감하게 된다. ChatGPT 웹사이트는 완성된 제품이고, API 호출은 외부 모델 서비스를 내 기능 안으로 편입하는 개발 작업이다. 여기서부터 인증, 요청 형식, 응답 파싱, 타임아웃, 비용 기록 같은 현실적인 문제가 시작된다.

API 호출은 구조가 단순하다. 애플리케이션이 인증 헤더와 JSON 본문을 담아 HTTP 요청을 보내고, 모델 서비스가 JSON 응답을 돌려준다. 이 구조를 처음에 명확히 이해하면 이후 토큰 비용, 프롬프트 구조, 스트리밍까지 모두 같은 계약의 변형으로 이해할 수 있다.

오류 처리도 처음부터 챙겨야 한다. `401`이면 인증 문제, `429`면 rate limit 또는 예산 초과, `timeout`이면 네트워크나 지연 설정 문제다. 프롬프트를 바꾸기 전에 HTTP 상태 코드를 먼저 확인하는 습관이 AI 개발의 디버깅 속도를 크게 높인다.

토큰 로깅도 처음부터 해 두면 좋다. `usage.prompt_tokens`, `usage.completion_tokens`, `usage.total_tokens`를 기록해 두면 어떤 프롬프트가 비용을 많이 쓰는지, 응답이 갑자기 짧아지는 이유가 뭔지 데이터로 파악할 수 있다.

> AI API 호출은 결국 HTTP 한 번의 왕복입니다. 인증, 요청 형식, 응답 파싱이 한 번 명확해지면 이후 모든 AI 기능은 같은 계약의 변형으로 이해할 수 있습니다.

## 이 글에서 다룰 문제

- ChatGPT 웹사이트와 AI API 호출은 무엇이 다른가요?
- OpenAI API 키를 안전하게 관리하는 방법은 무엇인가요?
- 첫 번째 요청의 구조와 응답에서 무엇을 읽어야 하나요?
- 401, 429, timeout 오류는 각각 무엇을 의미하나요?
- 토큰 비용을 처음부터 기록해야 하는 이유는 무엇인가요?

## Before / After: API 첫 호출 전후

| 상황 | 이전 | 적용 후 |
|------|------|---------|
| API 키 관리 | 코드에 하드코딩 | 환경변수 또는 .env 파일 |
| 오류 발생 시 | 프롬프트부터 수정 | HTTP 상태 코드 먼저 확인 |
| 토큰 비용 | 파악 불가 | usage 필드 로깅으로 추적 |
| 응답 파싱 | `str(response)` 출력 | `choices[0].message.content` 정확히 읽기 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| API 키를 코드에 직접 입력 | Git에 노출 위험 | 환경변수로 주입 |
| 오류 없이 바로 실행 가정 | 운영에서 장애 | 401/429/timeout 분기 처리 |
| 응답 전체를 str()로 출력 | 구조 파악 어려움 | choices[0].message.content 명시적 파싱 |
| 토큰 사용량 무시 | 비용 폭증 뒤 발견 | 처음부터 usage 필드 로깅 |

## AI 팁: 첫 API 호출 빠르게 시작하는 방법

Claude나 GPT-4에 "Python openai SDK로 첫 번째 chat completion 요청을 보내는 코드를 만들어줘. 환경변수에서 API 키를 읽고, 401/429/timeout 오류를 처리하고, usage 필드를 로깅해줘"라고 요청하면 바로 작동하는 코드를 얻을 수 있다. `pip install openai python-dotenv`로 시작하고, `.env` 파일에 `OPENAI_API_KEY=...`를 넣으면 된다. 응답은 `response.choices[0].message.content`에서 읽고, 비용은 `response.usage.total_tokens`에서 확인한다.

## 운영 체크리스트

- [ ] API 키를 환경변수 또는 시크릿 관리 도구로 주입하는가
- [ ] 401, 429, timeout 오류를 각각 분기 처리하는가
- [ ] 응답에서 `choices[0].message.content`를 명시적으로 파싱하는가
- [ ] `usage` 필드를 로깅해 토큰 비용을 추적하는가
- [ ] `.env` 파일을 `.gitignore`에 추가했는가

## 처음 질문으로 돌아가기

- **ChatGPT와 API의 차이는?** ChatGPT는 완성된 제품이고, API는 인증, 요청 형식, 응답 파싱을 직접 다루는 개발 작업이다.
- **오류 처리 순서는?** 프롬프트보다 HTTP 상태 코드를 먼저 본다. 401은 인증, 429는 rate limit/예산, timeout은 네트워크/지연이다.
- **토큰 로깅이 필요한 이유는?** 어떤 프롬프트가 비용을 많이 쓰는지, 응답이 짧아지는 이유가 뭔지 데이터로 파악하기 위해서다.

## 정리

AI API 첫 호출은 기술적으로 단순하다. 하지만 인증, 오류 처리, 토큰 비용 감각을 처음부터 제대로 잡아야 이후 AI 개발이 훨씬 수월해진다. "되긴 되는데 왜 그런지 모르겠다"는 상태를 벗어나는 출발점이 여기다.

## 참고 자료

- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/ai-web-dev-101/ko/01-hello-ai-api)

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 AI 웹 개발 (1/7): AI API 첫 걸음 (현재 글)**
- 바이브코딩을 위한 AI 웹 개발 (2/7): 프롬프트 엔지니어링 기초
- 바이브코딩을 위한 AI 웹 개발 (3/7): AI 챗봇 만들기
- 바이브코딩을 위한 AI 웹 개발 (4/7): RAG 기초
- 바이브코딩을 위한 AI 웹 개발 (5/7): AI 에이전트
- 바이브코딩을 위한 AI 웹 개발 (6/7): 배포하기
- 바이브코딩을 위한 AI 웹 개발 (7/7): 평가와 개선
<!-- toc:end -->

Tags: 바이브코딩, AI 웹 개발, OpenAI API, Python, LLM
