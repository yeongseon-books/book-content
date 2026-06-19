---
title: "AI Web Development 101 (3/7): AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현"
series: ai-web-dev-101
episode: 3
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/21"
    published_at: '2026-04-25'
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
last_reviewed: '2026-05-14'
seo_description: Next.js와 Vercel AI SDK로 스트리밍 채팅 UI를 만들며 브라우저와 모델 API를 연결하는 기본 구조를 익힙니다.
---

> **Deprecation notice**: 이 시리즈는 [`llm-app-foundations-101`](../../llm-app-foundations-101/ko/)과 [`ai-app-patterns-101`](../../ai-app-patterns-101/ko/)로 대체되었습니다. 신규 독자는 후속 시리즈를 권장합니다.

# AI Web Development 101 (3/7): AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현

터미널에서 AI를 호출하는 단계까지 왔다면, 이제 사용자가 직접 만질 수 있는 화면이 필요합니다. 여기서부터는 단순 API 호출을 넘어 입력 상태, 스트리밍 응답, 서버 경로, 사용자 경험이 함께 얽히기 시작합니다.

이 글은 AI 웹 개발 입문 시리즈의 3번째 글입니다. 이 편은 시리즈 안에서 잠시 프론트엔드로 이동하는 글이므로 Node.js, npm, React 기본기와 Next.js App Router 구조를 안다는 전제로 설명합니다.

![AI Web Development 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/03/chatbot-architecture-overview.ko.png)
*AI Web Development 101 3장 흐름 개요*

> 챗봇은 브라우저 상태와 서버 라우트 사이를 흐르는 스트리밍 파이프입니다 — UX 문제는 체감 지연이고, 아키텍처 문제는 클라이언트 메시지 상태와 서버의 모델 호출을 깔끔하게 분리해 두는 것입니다.

## 이 글에서 다룰 문제

- 터미널 예제를 브라우저 UI로 옮기려면 어떤 구성이 필요할까요?
- 왜 Next.js와 Vercel AI SDK 조합이 입문에 잘 맞을까요?
- `/api/chat` 경로는 어떤 역할을 맡아야 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 Next.js와 Vercel AI SDK인가

AI 기능을 웹에 붙일 때 가장 먼저 부딪히는 문제는 응답 속도 체감과 상태 관리입니다. 답변이 길어질수록 사용자는 빈 화면을 보고 기다리기 쉽고, 이때 서비스는 실제 속도보다 더 느리게 느껴집니다.

Vercel AI SDK는 이 지점을 꽤 잘 줄여 줍니다.

- 실시간 스트리밍: 답변이 생성되는 조각을 바로 화면에 흘려 보낼 수 있습니다.
- `useChat` 훅: 메시지 목록, 전송, 요청 상태를 기본 구조 안에서 다룰 수 있습니다.
- Next.js App Router와의 궁합: 서버 경로와 클라이언트 컴포넌트를 자연스럽게 연결할 수 있습니다.

직접 Fetch와 Server-Sent Events를 조립해도 되지만, 입문 단계에서는 먼저 안정적인 추상화를 타고 전체 그림을 보는 편이 좋습니다.

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

즉, 이 경로의 책임은 "대화 UI 메시지를 모델 메시지로 바꾸고, 모델 스트림을 다시 UI 스트림으로 돌려주는 것"입니다.

![API Route의 요청 처리 흐름](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/03/api-route-handler-flow.ko.png)

*API Route의 요청 처리 흐름*

![사용자 메시지가 AI 답변으로 변환되는 과정](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/03/chat-message-roundtrip.ko.png)

*사용자 메시지가 AI 답변으로 변환되는 과정*

## Step 2: 채팅 UI 만들기

이제 사용자 화면을 구성합니다. `useChat` 훅은 메시지 목록과 전송 상태를 관리하고, 입력창 값은 일반적인 React 방식으로 `useState`에 두는 편이 명확합니다.

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
        {isLoading && <div className="text-gray-400">답변을 작성하는 중입니다...</div>}
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

이 코드에서 기억할 점은 아래와 같습니다.

- `messages`: 대화 내역 배열입니다.
- `sendMessage(...)`: 현재 입력값을 `/api/chat`으로 보냅니다.
- `status`: 현재 요청 상태입니다. 전송 중에는 입력을 잠가 중복 호출을 막을 수 있습니다.
- `message.parts`: 텍스트 외에 tool call, 파일 등 다른 타입이 추가될 수 있어 `content` 하나만 가정하지 않는 편이 안전합니다.

![useChat 훅의 상태 관리 흐름](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/03/usechat-state-flow.ko.png)

*useChat 훅의 상태 관리 흐름*

## Step 3: 스트리밍이 체감 속도를 바꾸는 이유

`useChat`과 `streamText`를 함께 쓰면 별도 구현 없이도 스트리밍이 동작합니다. 사용자가 `sendMessage`를 호출하면 서버는 `toUIMessageStreamResponse()`로 응답을 흘려 보내고, 브라우저는 그 조각을 받아 화면을 점진적으로 갱신합니다.

이 방식의 장점은 단순히 "멋있어 보인다"가 아닙니다. 사용자는 첫 글자가 바로 나타나는 순간 서비스가 살아 있다고 느낍니다. 응답 전체가 끝날 때까지 침묵하는 UI보다 훨씬 빠르게 체감됩니다.

![스트리밍 방식으로 답변이 전달되는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/03/streaming-response-flow.ko.png)

*스트리밍 방식으로 답변이 전달되는 흐름*

## Step 4: 시스템 프롬프트로 챗봇 성격 정하기

Step 1에서 `system` 속성에 넣은 문자열이 챗봇의 기본 태도를 정합니다. 이곳은 단순한 소개 문장이 아니라, 서비스가 어떤 역할을 하길 원하는지 담는 비즈니스 규칙 공간에 가깝습니다.

- 전문가 모드: "당신은 10년 차 시니어 소프트웨어 엔지니어입니다. 코드를 리뷰하고 최적화 방안을 제시하세요."
- 엔터테인먼트: "당신은 조선시대 선비입니다. 현대의 기술을 보고 깜짝 놀란 말투로 대화하세요."

사용자 입력이 같아도 시스템 프롬프트가 바뀌면 결과는 꽤 크게 달라집니다. 그래서 챗봇 품질을 조절할 때는 모델 이름만이 아니라 시스템 프롬프트 설계도 함께 봐야 합니다.

## 서버 경계에서 지켜야 할 채팅 계약

실시간 채팅 UI를 만들 때 가장 많이 생기는 실수는 브라우저 코드에서 모델 키를 직접 다루는 것입니다. 모델 공급자 API는 항상 서버 경계 뒤에서 호출하고, 브라우저는 오직 우리 서비스의 `/api/chat`만 호출해야 합니다.

```typescript
// app/api/chat/route.ts - 올바른 서버 경계 패턴
import { streamText } from "ai"
import { openai } from "@ai-sdk/openai"

export const runtime = "edge"

export async function POST(req: Request) {
  const body = await req.json()
  const messages = body.messages ?? []

  const result = streamText({
    model: openai("gpt-4o-mini"),
    system: "당신은 한국어 개발 도우미입니다.",
    messages,
    temperature: 0.2,
    maxTokens: 600,
  })

  return result.toDataStreamResponse()
}
```

위 구조는 단순해 보이지만, 실제로는 모델 교체, 지표 수집, 레이트 리밋 도입을 모두 이 경계에서 수행할 수 있다는 장점이 있습니다.

## 세션 메모리와 프롬프트 분리

챗봇 품질이 흔들리는 대표 원인은 이전 대화가 무제한으로 누적되는 것입니다. "시스템 지침", "최근 대화", "검색 근거"를 별도 블록으로 분리해야 합니다.

```typescript
function buildPrompt(input: {
  question: string
  recentTurns: Array<{role: "user" | "assistant"; content: string}>
  contextChunks: string[]
}) {
  return {
    system: [
      "당신은 한국어 기술 지원 도우미입니다.",
      "근거가 없으면 모른다고 답합니다.",
      "답변은 요약 1문장 + 핵심 3개로 작성합니다.",
    ].join("\n"),
    user: [
      `질문: ${input.question}`,
      "최근 대화:",
      ...input.recentTurns.map((t) => `- ${t.role}: ${t.content}`),
      "참고 문서:",
      ...input.contextChunks,
    ].join("\n"),
  }
}
```

이 패턴을 쓰면 이후 RAG를 붙여도 대화 품질 퇴화를 줄일 수 있습니다.

## 운영 지표: 체감 품질과 비용을 동시에 본다

챗봇 운영에서는 다음 지표를 기본으로 수집하는 것이 좋습니다.

- 첫 토큰 지연 시간(First Token Latency)
- 전체 응답 완료 시간
- 사용자 메시지당 총 토큰
- 스트림 중단 비율
- "도움이 되지 않았다" 피드백 비율

이 다섯 가지 지표만 있어도 프론트 문제인지, 모델 문제인지, 검색 문제인지 빠르게 분류할 수 있습니다.

## 스트리밍 응답 품질을 지키는 프런트엔드 패턴

스트리밍 채팅은 빠르게 보이지만, 실제로는 중간 끊김과 상태 경합이 자주 발생합니다. 특히 사용자가 전송 버튼을 연속으로 누르는 경우 세션 상태가 꼬일 수 있습니다.

```typescript
const { messages, input, handleInputChange, handleSubmit, status, stop } = useChat({
  api: "/api/chat",
  onError(error) {
    console.error("chat error", error)
  },
})

const canSend = status !== "streaming" && input.trim().length > 0
```

`canSend` 같은 단순 가드만으로도 중복 요청이 크게 줄어듭니다. 또한 `stop()` 액션을 제공하면 사용자가 응답을 강제로 멈출 수 있어 체감 제어권이 올라갑니다.

## 대화 저장 전략

대화를 저장할 때는 전체 전문만 쌓지 말고 검색 가능한 메타데이터를 함께 저장해야 합니다.

- `session_id`, `user_id`, `request_id`
- 사용자 질문 요약
- 모델 이름과 토큰 사용량
- 응답 생성 시각과 지연 시간

이 정보가 있어야 나중에 특정 세션의 품질 이슈를 빠르게 재현할 수 있습니다.

```typescript
const requestId = crypto.randomUUID()
await fetch("/api/chat", {
  method: "POST",
  headers: { "x-request-id": requestId },
  body: JSON.stringify({ messages }),
})
```

사용자 문의를 받을 때도 request_id 하나만 있으면 같은 세션의 전체 흐름을 빠르게 추적할 수 있습니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 브라우저 코드에서 OpenAI 키 직접 호출 | API 키 노출 → 무단 과금 | 항상 서버 경계(`/api/chat`)에서만 모델 호출 |
| 전체 대화 기록을 무제한 누적 | 토큰 비용 폭증, 컨텍스트 오염 | 최근 N턴만 유지하는 슬라이딩 윈도우 적용 |
| 스트리밍 중 중복 전송 허용 | 응답 상태 충돌, UI 깨짐 | `status === "streaming"` 중 전송 버튼 비활성화 |
| 오류 시 빈 화면 표시 | 사용자가 실패 원인 알 수 없음 | `onError` 핸들러에서 안내 메시지 표시 |
| `message.content`만 읽음 | tool call 파트 누락 | `message.parts`를 순회해 텍스트 파트만 렌더링 |
| `maxDuration` 미설정 | Edge 함수 기본 시간 초과 | `export const maxDuration = 30` 명시 |

## 운영 체크리스트

- [ ] `/api/chat` 경로가 모델 호출과 스트리밍 응답을 담당한다.
- [ ] `useChat`으로 메시지 목록과 요청 상태를 관리한다.
- [ ] 입력 중복 전송을 막는 UI 상태를 넣었다.
- [ ] 시스템 프롬프트를 한곳에서 조절할 수 있다.
- [ ] 오류 시 사용자에게 적절한 안내 메시지를 표시한다.
- [ ] `request_id`로 브라우저 이벤트와 서버 로그를 연결한다.

## 정리

브라우저 챗봇을 만드는 핵심은 모델 호출 자체보다, 클라이언트 상태와 서버 스트리밍 경로를 자연스럽게 연결하는 데 있습니다.

- `useChat`은 메시지 목록과 요청 상태를 다루는 기본 뼈대를 제공합니다.
- `/api/chat` 경로는 UI 메시지와 모델 메시지 사이의 변환층입니다.
- 스트리밍은 체감 속도와 사용자 신뢰를 크게 높여 줍니다.
- 시스템 프롬프트는 챗봇의 성격과 서비스 규칙을 정하는 핵심 지점입니다.

다음 글에서는 대화 UI를 넘어, 우리 문서를 근거로 답하는 RAG 구조를 붙여 보겠습니다.

## 처음 질문으로 돌아가기

- **터미널 예제를 브라우저 UI로 옮기려면 어떤 구성이 필요할까요?**
  - 서버 경로(`/api/chat`)로 스트리밍 응답을 만들고, 클라이언트에서 `useChat`으로 메시지 상태와 전송을 관리합니다.
- **왜 Next.js와 Vercel AI SDK 조합이 입문에 잘 맞을까요?**
  - `streamText`, `useChat`, App Router가 스트리밍 파이프를 간단히 연결해 주기 때문입니다.
- **`/api/chat` 경로는 어떤 역할을 맡아야 할까요?**
  - 브라우저 UI 메시지를 모델 메시지로 변환하고, 모델 스트림을 다시 UI 스트림으로 돌려줍니다. 모델 키는 이 경계 안에서만 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Web Development 101 (1/7): AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기](./01-hello-ai-api.md)
- [AI Web Development 101 (2/7): 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술](./02-prompt-engineering.md)
- **AI Web Development 101 (3/7): AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현 (현재 글)**
- [AI Web Development 101 (4/7): RAG 입문 — 내 데이터로 답하는 AI 만들기](./04-rag-intro.md)
- [AI Web Development 101 (5/7): AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기](./05-ai-agent.md)
- [AI Web Development 101 (6/7): AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기](./06-deploy.md)
- [AI 앱의 평가와 개선, 품질을 측정하고 더 좋게 만드는 법](./07-eval-improve.md)

<!-- toc:end -->

## 참고 자료
- [AI Web Development 101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/ai-web-dev-101/ko)

- [Vercel AI SDK: Chatbot guide](https://sdk.vercel.ai/docs/ai-sdk-ui/chatbot) — `useChat` + 라우트 핸들러 조합의 정식 안내
- [Vercel AI SDK: `useChat` reference](https://sdk.vercel.ai/docs/reference/ai-sdk-ui/use-chat) — 메시지 상태와 `status` 값의 정확한 의미
- [Vercel AI SDK: `streamText` reference](https://sdk.vercel.ai/docs/reference/ai-sdk-core/stream-text) — 서버 측 스트리밍 API의 옵션과 반환값
- [Next.js: Route Handlers](https://nextjs.org/docs/app/building-your-application/routing/route-handlers) — `app/api/chat/route.ts`가 따르는 App Router 규약
- [Next.js: Edge Runtime](https://nextjs.org/docs/app/api-reference/edge) — `export const runtime = "edge"`가 의미하는 실행 환경과 제한
- [Vercel AI SDK examples repository](https://github.com/vercel/ai/tree/main/examples) — 더 다양한 챗봇/툴 사용 예제

Tags: AI, LLM, 웹 개발, Python, Tutorial
