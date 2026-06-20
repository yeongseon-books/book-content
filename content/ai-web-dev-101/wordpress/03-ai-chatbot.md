---
series: ai-web-dev-101
episode: 3
title: "바이브코딩을 위한 AI 웹 개발 (3/7): AI 챗봇 만들기"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - AI 웹 개발
  - Chatbot
  - Next.js
  - Streaming
language: ko
---

# 바이브코딩을 위한 AI 웹 개발 (3/7): AI 챗봇 만들기

> 이 글은 **바이브코딩을 위한 AI 웹 개발** 시리즈 3편입니다. Next.js와 Vercel AI SDK로 스트리밍 챗봇을 구현하는 방법을 다룹니다.

바이브코딩으로 AI 챗봇을 만들 때 가장 먼저 부딪히는 문제는 스트리밍이다. 모델 응답이 다 나올 때까지 기다렸다가 한 번에 보여주면 사용자는 몇 초 동안 빈 화면을 본다. ChatGPT처럼 글자가 하나씩 나오는 경험을 구현하려면 서버와 클라이언트 양쪽에 스트리밍 처리가 필요하다.

Next.js App Router와 Vercel AI SDK를 쓰면 이 구조를 빠르게 만들 수 있다. 서버 쪽에서는 `streamText`와 `toUIMessageStreamResponse`로 스트리밍 응답을 생성하고, 클라이언트 쪽에서는 `useChat` 훅이 상태 관리와 스트림 수신을 처리한다. 서버와 클라이언트 경계를 명확히 하는 것이 핵심이다. API 키는 서버 사이드에만 있어야 하고, 클라이언트 컴포넌트에는 절대 노출되면 안 된다.

대화 이력 관리도 챙겨야 한다. 모델은 상태를 기억하지 않으므로, 이전 대화를 매 요청마다 messages 배열에 포함해서 보내야 한다. 이력이 길어지면 컨텍스트 창이 가득 차서 오류가 발생하거나 비용이 급증하므로, 최근 N개 메시지만 유지하는 전략이 필요하다.

request_id를 각 요청에 달아 두면 어떤 대화에서 문제가 발생했는지 나중에 추적할 수 있다. 바이브코딩의 속도를 유지하면서도 운영 가시성을 확보하는 간단한 방법이다.

> 스트리밍 챗봇의 핵심은 응답을 기다리는 것이 아니라 흘러오는 것을 그대로 보여주는 구조입니다. 서버와 클라이언트 경계만 명확히 하면 나머지는 SDK가 처리합니다.

## 이 글에서 다룰 문제

- 스트리밍 응답은 왜 필요하고 어떻게 구현하나요?
- Next.js App Router와 Vercel AI SDK는 어떻게 조합하나요?
- useChat 훅은 무엇을 자동으로 처리해주나요?
- API 키를 클라이언트에서 숨기는 방법은 무엇인가요?
- 대화 이력이 길어질 때 어떻게 관리해야 할까요?

## Before / After: 스트리밍 챗봇 전후

| 상황 | 스트리밍 없이 | 스트리밍 적용 후 |
|------|--------------|----------------|
| 응답 경험 | 몇 초 빈 화면 후 한 번에 표시 | 글자가 하나씩 즉시 나타남 |
| API 키 보안 | 클라이언트 코드에 노출 위험 | 서버 사이드에서만 사용 |
| 대화 이력 | 매번 처음부터 | messages 배열로 컨텍스트 유지 |
| 오류 추적 | 어떤 대화인지 모름 | request_id로 추적 가능 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| API 키를 클라이언트 컴포넌트에 포함 | 브라우저 개발자 도구에 노출 | Route Handler 서버 사이드에서만 |
| 대화 이력 전체를 매번 전송 | 컨텍스트 창 초과, 비용 급증 | 최근 N개 메시지만 유지 |
| 스트리밍 없이 단순 fetch | UX 불량, 긴 대기 | streamText + toUIMessageStreamResponse |
| 오류 시 빈 화면 | 사용자가 이유를 모름 | 오류 상태 UI 처리 |

## AI 팁: 스트리밍 챗봇 빠르게 만드는 방법

Claude나 GPT-4에 "Next.js App Router와 Vercel AI SDK로 스트리밍 챗봇을 만들어줘. useChat 훅과 Route Handler를 사용하고, API 키는 서버 사이드에만 있어야 해"라고 요청하면 작동하는 코드를 얻을 수 있다. `npm install ai openai`로 시작하고, `app/api/chat/route.ts`에 `streamText`와 `toUIMessageStreamResponse`를 넣으면 된다. 클라이언트 컴포넌트에서는 `useChat({ api: '/api/chat' })`만 호출하면 메시지 상태와 스트림 수신이 자동으로 처리된다.

## 운영 체크리스트

- [ ] API 키가 서버 사이드(Route Handler)에서만 사용되는가
- [ ] 스트리밍 응답을 위해 streamText + toUIMessageStreamResponse를 사용하는가
- [ ] 대화 이력에서 최근 N개 메시지만 전송하도록 제한하는가
- [ ] 각 요청에 request_id를 달아 로깅하는가
- [ ] 오류 상태를 사용자에게 적절히 표시하는가

## 처음 질문으로 돌아가기

- **스트리밍이 필요한 이유는?** 긴 응답을 다 받은 뒤 한 번에 보여주면 사용자가 몇 초 동안 빈 화면을 본다. 스트리밍은 첫 토큰부터 즉시 보여준다.
- **useChat 훅은 무엇을 처리하나?** 메시지 상태 관리, API 호출, 스트림 수신, 로딩 상태를 자동으로 처리한다.
- **API 키 보안은?** 클라이언트 컴포넌트는 브라우저에서 실행되므로 API 키가 노출된다. Route Handler 서버 사이드에서만 사용해야 한다.

## 정리

스트리밍 챗봇은 서버와 클라이언트 경계만 명확히 하면 Vercel AI SDK가 복잡한 부분을 처리해준다. API 키 보안, 스트리밍 응답, 대화 이력 관리를 처음부터 올바르게 설계해야 나중에 운영 문제를 줄일 수 있다.

## 참고 자료

- [Vercel AI SDK — useChat](https://sdk.vercel.ai/docs/reference/ai-sdk-ui/use-chat)
- [Next.js — Route Handlers](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/ai-web-dev-101/ko/03-ai-chatbot)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 AI 웹 개발 (1/7): AI API 첫 걸음
- 바이브코딩을 위한 AI 웹 개발 (2/7): 프롬프트 엔지니어링 기초
- **바이브코딩을 위한 AI 웹 개발 (3/7): AI 챗봇 만들기 (현재 글)**
- 바이브코딩을 위한 AI 웹 개발 (4/7): RAG 기초
- 바이브코딩을 위한 AI 웹 개발 (5/7): AI 에이전트
- 바이브코딩을 위한 AI 웹 개발 (6/7): 배포하기
- 바이브코딩을 위한 AI 웹 개발 (7/7): 평가와 개선
<!-- toc:end -->

Tags: 바이브코딩, AI 웹 개발, Chatbot, Next.js, Streaming
