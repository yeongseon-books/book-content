---
title: AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현
series: ai-web-dev-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI
- LLM
- 웹 개발
- Python
- Tutorial
last_reviewed: '2026-05-12'
seo_description: Next.js와 Vercel AI SDK로 스트리밍 채팅 UI를 만들며 브라우저와 모델 API를 연결하는 기본 구조를 익힙니다.
---

# AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현

터미널에서 AI를 호출하는 단계까지 왔다면, 이제 사용자가 직접 만질 수 있는 화면이 필요합니다. 여기서부터는 단순 API 호출을 넘어 입력 상태, 스트리밍 응답, 서버 경로, 사용자 경험이 함께 얽히기 시작합니다.

이 글은 AI 웹 개발 입문 시리즈의 3번째 글입니다.

여기서는 브라우저에서 AI와 실시간으로 대화하는 챗봇 UI를 구현해 보겠습니다. 이 편은 시리즈 안에서 잠시 프론트엔드로 이동하는 글이므로 Node.js, npm, React 기본기와 Next.js App Router 구조를 안다는 전제로 설명합니다.

## 이 글에서 다룰 문제

- 터미널 예제를 브라우저 UI로 옮기려면 어떤 구성이 필요할까요?
- 왜 Next.js와 Vercel AI SDK 조합이 입문에 잘 맞을까요?
- `/api/chat` 경로는 어떤 역할을 맡아야 할까요?
- 스트리밍 응답은 브라우저에서 어떻게 이어 붙일까요?
- 시스템 프롬프트와 UI 상태 관리는 어디에서 다루는 편이 좋을까요?

> 웹 챗봇은 “입력창 + 모델”이 아니라, 브라우저 상태와 서버 스트리밍 경로가 맞물린 두 층 구조입니다. 클라이언트는 대화 경험을 만들고, 서버는 모델 호출과 응답 스트림을 책임진다고 생각하면 전체 흐름이 단순해집니다.

## 왜 Next.js와 Vercel AI SDK인가

AI 기능을 웹에 붙일 때 가장 먼저 부딪히는 문제는 응답 속도 체감과 상태 관리입니다. 답변이 길어질수록 사용자는 빈 화면을 보고 기다리기 쉽고, 이때 서비스는 실제 속도보다 더 느리게 느껴집니다.

Vercel AI SDK는 이 지점을 꽤 잘 줄여 줍니다.

- 실시간 스트리밍: 답변이 생성되는 조각을 바로 화면에 흘려 보낼 수 있습니다.
- `useChat` 훅: 메시지 목록, 전송, 요청 상태를 기본 구조 안에서 다룰 수 있습니다.
- Next.js App Router와의 궁합: 서버 경로와 클라이언트 컴포넌트를 자연스럽게 연결할 수 있습니다.

직접 Fetch와 Server-Sent Events를 조립해도 되지만, 입문 단계에서는 먼저 안정적인 추상화를 타고 전체 그림을 보는 편이 좋습니다.

![브라우저와 모델 API를 잇는 챗봇 서비스 구조](../../../assets/ai-web-dev-101/03/chatbot-architecture-overview.ko.png)

브라우저와 모델 API를 잇는 챗봇 서비스 구조

## 프로젝트 초기 설정

먼저 새 Next.js 프로젝트를 만들고 필요한 패키지를 설치합니다.

```bash
npx create-next-app@latest my-ai-chatbot --typescript --tailwind --eslint
cd my-ai-chatbot
```

그다음 Vercel AI SDK와 OpenAI 연결에 필요한 패키지를 추가합니다.

```bash
npm install ai @ai-sdk/react @ai-sdk/openai
```

실제 키는 저장소에 넣지 말고 예시 파일만 남긴 뒤, 로컬에서 실제 환경 파일을 따로 두는 방식으로 관리합니다.

```text
# .env.local.example
OPENAI_API_KEY=your_api_key_here
```

`.env.local.example`만 커밋하고 실제 `.env.local`은 `.gitignore`로 제외하는 방식이 가장 안전합니다.

## Step 1: API Route 만들기

브라우저에서 보낸 메시지를 받아 OpenAI에 전달하고, 응답을 다시 스트리밍해서 돌려주는 서버 경로를 먼저 만듭니다. 이 경로는 클라이언트와 모델 사이의 얇은 중계층이라고 보면 됩니다.

`app/api/chat/route.ts` 파일에 아래 코드를 넣습니다.

```typescript
import { openai } from "@ai-sdk/openai";
import { convertToModelMessages, streamText, type UIMessage } from "ai";

export const runtime = "edge";
export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages }: { messages: UIMessage[] } = await req.json();

  const result = streamText({
    model: openai("gpt-4o-mini"),
    system: "당신은 친절한 요리 도우미입니다. 사용자의 냉장고 재료에 맞춰 레시피를 추천해 주세요.",
    messages: convertToModelMessages(messages),
  });

  return result.toUIMessageStreamResponse();
}
```

여기서 먼저 봐야 할 포인트는 세 가지입니다.

- `UIMessage[]`: 브라우저에서 오간 대화 내역의 타입입니다.
- `convertToModelMessages(...)`: UI 메시지 구조를 모델 호출용 구조로 바꿉니다.
- `toUIMessageStreamResponse()`: 스트리밍 결과를 클라이언트가 바로 읽을 수 있는 응답 형식으로 감쌉니다.

즉, 이 경로의 책임은 “대화 UI 메시지를 모델 메시지로 바꾸고, 모델 스트림을 다시 UI 스트림으로 돌려주는 것”입니다.

![API Route의 요청 처리 흐름](../../../assets/ai-web-dev-101/03/api-route-handler-flow.ko.png)

API Route의 요청 처리 흐름

![사용자 메시지가 AI 답변으로 변환되는 과정](../../../assets/ai-web-dev-101/03/chat-message-roundtrip.ko.png)

사용자 메시지가 AI 답변으로 변환되는 과정

## Step 2: 채팅 UI 만들기

이제 사용자 화면을 구성합니다. 최신 `useChat` 훅은 메시지 목록과 전송 상태를 관리하고, 입력창 값은 일반적인 React 방식으로 `useState`에 두는 편이 명확합니다.

`app/page.tsx` 내용을 아래 코드로 바꿉니다.

```tsx
"use client";

import { useChat } from "@ai-sdk/react";
import { useState } from "react";

export default function Chat() {
  const [input, setInput] = useState("");
  const { messages, sendMessage, status } = useChat();
  const isLoading = status === "submitted" || status === "streaming";

  return (
    <div className="flex flex-col w-full max-w-md py-24 mx-auto stretch">
      <div className="space-y-4">
        {messages.map((m) => (
          <div key={m.id} className="whitespace-pre-wrap">
            <span className="font-bold">
              {m.role === "user" ? "User: " : "Assistant: "}
            </span>
            {m.parts.map((part, i) =>
              part.type === "text" ? <span key={i}>{part.text}</span> : null,
            )}
          </div>
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (input.trim()) {
            sendMessage({ text: input });
            setInput("");
          }
        }}
        className="fixed bottom-0 w-full max-w-md mb-8"
      >
        <input
          className="w-full p-2 border border-gray-300 rounded shadow-xl text-black"
          value={input}
          placeholder="가지고 있는 재료를 말해보세요..."
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
      </form>
    </div>
  );
}
```

이 코드에서 기억할 점은 아래와 같습니다.

- `messages`: 대화 내역 배열입니다.
- `sendMessage(...)`: 현재 입력값을 `/api/chat`으로 보냅니다.
- `status`: 현재 요청 상태입니다. 전송 중에는 입력을 잠가 중복 호출을 막을 수 있습니다.
- `message.parts`: 텍스트 외에 tool call, 파일 등 다른 타입이 추가될 수 있어 `content` 하나만 가정하지 않는 편이 안전합니다.

![useChat 훅의 상태 관리 흐름](../../../assets/ai-web-dev-101/03/usechat-state-flow.ko.png)

useChat 훅의 상태 관리 흐름

## Step 3: 스트리밍이 체감 속도를 바꾸는 이유

`useChat`과 `streamText`를 함께 쓰면 별도 구현 없이도 스트리밍이 동작합니다. 사용자가 `sendMessage`를 호출하면 서버는 `toUIMessageStreamResponse()`로 응답을 흘려 보내고, 브라우저는 그 조각을 받아 화면을 점진적으로 갱신합니다.

이 방식의 장점은 단순히 “멋있어 보인다”가 아닙니다. 사용자는 첫 글자가 바로 나타나는 순간 서비스가 살아 있다고 느낍니다. 응답 전체가 끝날 때까지 침묵하는 UI보다 훨씬 빠르게 체감됩니다.

![스트리밍 방식으로 답변이 전달되는 흐름](../../../assets/ai-web-dev-101/03/streaming-response-flow.ko.png)

스트리밍 방식으로 답변이 전달되는 흐름

## Step 4: 시스템 프롬프트로 챗봇 성격 정하기

Step 1에서 `system` 속성에 넣은 문자열이 챗봇의 기본 태도를 정합니다. 이곳은 단순한 소개 문장이 아니라, 서비스가 어떤 역할을 하길 원하는지 담는 비즈니스 규칙 공간에 가깝습니다.

- 전문가 모드: "당신은 10년 차 시니어 소프트웨어 엔지니어입니다. 코드를 리뷰하고 최적화 방안을 제시하세요."
- 엔터테인먼트: "당신은 조선시대 선비입니다. 현대의 기술을 보고 깜짝 놀란 말투로 대화하세요."

사용자 입력이 같아도 시스템 프롬프트가 바뀌면 결과는 꽤 크게 달라집니다. 그래서 챗봇 품질을 조절할 때는 모델 이름만이 아니라 시스템 프롬프트 설계도 함께 봐야 합니다.

## 완성된 전체 코드

아래는 설명한 구조를 한 번에 붙여서 볼 수 있는 전체 코드입니다.

### API Route (`app/api/chat/route.ts`)
```typescript
import { openai } from "@ai-sdk/openai";
import { convertToModelMessages, streamText, type UIMessage } from "ai";

export const runtime = "edge";
export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages }: { messages: UIMessage[] } = await req.json();

  const result = streamText({
    model: openai("gpt-4o-mini"),
    system: "당신은 친절한 요리 도우미입니다. 사용자의 질문에 정중하게 답하세요.",
    messages: convertToModelMessages(messages),
  });

  return result.toUIMessageStreamResponse();
}
```

### Client Page (`app/page.tsx`)
```tsx
"use client";

import { useChat } from "@ai-sdk/react";
import { useState } from "react";

export default function Chat() {
  const [input, setInput] = useState("");
  const { messages, sendMessage, status } = useChat();
  const isLoading = status === "submitted" || status === "streaming";

  return (
    <div className="flex flex-col w-full max-w-md py-24 mx-auto stretch">
      <h1 className="text-2xl font-bold mb-8 text-center">AI 요리 도우미</h1>

      <div className="flex-1 space-y-4 mb-20">
        {messages.length === 0 && (
          <p className="text-gray-500 text-center">궁금한 레시피나 재료를 물어보세요!</p>
        )}
        {messages.map((m) => (
          <div
            key={m.id}
            className={`p-4 rounded-lg ${m.role === "user" ? "bg-blue-100 ml-auto" : "bg-gray-100"}`}
            style={{ maxWidth: "80%" }}
          >
            <p className="text-sm font-semibold mb-1">
              {m.role === "user" ? "User" : "Assistant"}
            </p>
            <div className="text-black">
              {m.parts.map((part, i) =>
                part.type === "text" ? <span key={i}>{part.text}</span> : null,
              )}
            </div>
          </div>
        ))}
        {isLoading && <div className="text-gray-400">Assistant가 답변을 작성하는 중입니다...</div>}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (input.trim()) {
            sendMessage({ text: input });
            setInput("");
          }
        }}
        className="fixed bottom-4 w-full max-w-md bg-white p-2"
      >
        <input
          className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          value={input}
          placeholder="냉장고에 남은 재료는?"
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading}
          className="mt-2 w-full rounded-lg bg-blue-600 px-4 py-2 text-white disabled:bg-blue-300"
        >
          Send
        </button>
      </form>
    </div>
  );
}
```

## 다음에 붙일 개선 포인트

이 상태로도 동작은 하지만, 실서비스로 가려면 아래 같은 확장이 자연스럽게 이어집니다.

1. 대화 기록 저장: 데이터베이스를 붙여 새로고침 후에도 대화를 유지합니다.
2. 로딩 상태 세분화: `status` 값을 활용해 `submitted`, `streaming`, `error`에 따라 UI를 다르게 보여 줍니다.
3. 에러 처리: 모델 호출 실패 시 사용자에게 안내 메시지를 분리해서 보여 줍니다.

## 체크리스트

- [ ] `/api/chat` 경로가 모델 호출과 스트리밍 응답을 담당한다.
- [ ] `useChat`으로 메시지 목록과 요청 상태를 관리한다.
- [ ] 입력 중복 전송을 막는 UI 상태를 넣었다.
- [ ] 시스템 프롬프트를 한곳에서 조절할 수 있다.

## 정리

브라우저 챗봇을 만드는 핵심은 모델 호출 자체보다, 클라이언트 상태와 서버 스트리밍 경로를 자연스럽게 연결하는 데 있습니다.

- `useChat`은 메시지 목록과 요청 상태를 다루는 기본 뼈대를 제공합니다.
- `/api/chat` 경로는 UI 메시지와 모델 메시지 사이의 변환층입니다.
- 스트리밍은 체감 속도와 사용자 신뢰를 크게 높여 줍니다.
- 시스템 프롬프트는 챗봇의 성격과 서비스 규칙을 정하는 핵심 지점입니다.

다음 글에서는 대화 UI를 넘어, 우리 문서를 근거로 답하는 RAG 구조를 붙여 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기](./01-hello-ai-api.md)
- [프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술](./02-prompt-engineering.md)
- **AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현 (현재 글)**
- RAG 입문 — 내 데이터로 답하는 AI 만들기 (예정)
- AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기 (예정)
- AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기 (예정)
- AI 앱의 평가와 개선, 품질을 측정하고 더 좋게 만드는 법 (예정)

<!-- toc:end -->

## 참고 자료

- [Vercel AI SDK Documentation](https://sdk.vercel.ai/docs)
- [Next.js App Router Guide](https://nextjs.org/docs/app)

Tags: AI, LLM, 웹 개발, Python, Tutorial
