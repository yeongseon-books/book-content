---
title: AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현
series: ai-web-dev-101
episode: 3
language: ko
status: needs-update
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
last_reviewed: '2026-04-29'
---

# AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현

> AI 웹 개발 입문 시리즈 (3/7)

지금까지 터미널에서만 AI를 불렀는데, 이제 브라우저에서 사용자가 직접 대화할 수 있는 UI를 만들어 봅시다. 단순히 API를 연결하는 수준을 넘어, 글자가 한 글자씩 타이핑되는 스트리밍 효과와 시스템 프롬프트를 활용한 페르소나 설정까지 다뤄보겠습니다.

---

## 왜 Next.js + Vercel AI SDK인가?

AI 기능을 웹에 구현할 때 가장 큰 고민은 '응답 속도'와 '상태 관리'입니다. AI의 답변이 길어질수록 사용자는 빈 화면을 보며 기다려야 하죠. 

**Vercel AI SDK**는 이 문제를 해결해 줍니다.
- **실시간 스트리밍**: 답변이 생성되는 대로 즉시 화면에 뿌려주는 기능을 단 몇 줄로 구현합니다.
- **useChat 훅**: 메시지 목록 관리, 입력창 상태, 로딩 처리 등을 자동으로 해줍니다. 
- 프레임워크 최적화: Next.js App Router와 완벽하게 호환되어 서버와 클라이언트 간의 데이터 흐름을 쉽게 제어할 수 있습니다. 

**[그림 1] AI 챗봇 서비스의 전체 구조**

![AI 챗봇 서비스의 전체 구조](../../../assets/ai-web-dev-101/03/chatbot-architecture-overview.ko.png)

---

## 프로젝트 초기 설정

먼저 새로운 Next.js 프로젝트를 생성하고 필요한 패키지를 설치합니다.

```bash
npx create-next-app@latest my-ai-chatbot --typescript --tailwind --eslint
cd my-ai-chatbot
```

그다음 Vercel AI SDK와 OpenAI를 사용하기 위한 패키지를 추가합니다.

```bash
npm install ai @ai-sdk/openai
```

`.env.local` 파일에 여러분의 OpenAI API Key를 설정하는 것도 잊지 마세요.

```text
OPENAI_API_KEY=your_actual_api_key_here
```

---

## Step 1: API Route 만들기 (/api/chat)

사용자의 메시지를 받아서 OpenAI에게 전달하고, 그 답변을 다시 클라이언트로 스트리밍해 주는 서버측 경로를 만듭니다. 

`app/api/chat/route.ts` 파일을 생성하고 아래 코드를 작성합니다.

```typescript
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

// Next.js App Router의 Edge Runtime을 사용하면 성능이 더 좋아집니다.
export const runtime = 'edge';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'), // 사용하고 싶은 모델 선택
    messages,
    system: "당신은 친절한 요리 도우미입니다. 사용자의 냉장고 재료에 맞춰 레시피를 추천해 주세요.",
  });

  return result.toDataStreamResponse();
}
```

![API Route의 요청 처리 흐름](../../../assets/ai-web-dev-101/03/api-route-handler-flow.ko.png)

- `streamText`: AI SDK의 핵심 함수로, 텍스트를 스트리밍 방식으로 생성합니다.
- `system`: 챗봇의 성격을 규정합니다. 여기서는 '요리 도우미'로 설정했습니다.
- `toDataStreamResponse()`: 생성된 텍스트 스트림을 표준 응답 형식으로 변환해 줍니다.

![사용자 메시지가 AI 답변으로 변환되는 과정](../../../assets/ai-web-dev-101/03/chat-message-roundtrip.ko.png)

---

## Step 2: 채팅 UI 만들기 (useChat 훅)

이제 사용자 화면을 구성할 차례입니다. `useChat` 훅을 사용하면 메시지 리스트를 따로 `useState`로 관리할 필요가 없습니다.

`app/page.tsx` 내용을 모두 지우고 아래 코드를 넣으세요.

```tsx
'use client';

import { useChat } from 'ai/react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit } = useChat();

  return (
    <div className="flex flex-col w-full max-w-md py-24 mx-auto stretch">
      <div className="space-y-4">
        {messages.map(m => (
          <div key={m.id} className="whitespace-pre-wrap">
            <span className="font-bold">
              {m.role === 'user' ? '나: ' : '요리봇: '}
            </span>
            {m.content}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="fixed bottom-0 w-full max-w-md mb-8">
        <input
          className="w-full p-2 border border-gray-300 rounded shadow-xl text-black"
          value={input}
          placeholder="가지고 있는 재료를 말해보세요..."
          onChange={handleInputChange}
        />
      </form>
    </div>
  );
}
```

- `messages`: 대화 내역이 담긴 배열입니다.
- `input / handleInputChange`: 입력창의 상태를 관리합니다.
- `handleSubmit`: 엔터를 치거나 폼을 제출하면 자동으로 `/api/chat`으로 데이터를 보냅니다.

![useChat 훅의 상태 관리 흐름](../../../assets/ai-web-dev-101/03/usechat-state-flow.ko.png)

---

## Step 3: 스트리밍 응답 구현

별도의 설정을 하지 않아도 `useChat`과 `streamText`를 조합하면 이미 스트리밍이 동작합니다. AI가 답변을 한 글자씩 '타이핑' 하듯 내려주는 것을 확인할 수 있습니다. 

이는 사용자 경험(UX) 측면에서 매우 중요합니다. 전체 답변이 올 때까지 수 초를 기다리는 대신, 첫 글자가 바로 나타나기 때문에 사용자는 서비스가 빠르다고 느낍니다.

**[그림 2] 스트리밍 방식의 데이터 흐름**

![스트리밍 방식으로 답변이 전달되는 흐름](../../../assets/ai-web-dev-101/03/streaming-response-flow.ko.png)

---

## Step 4: System Prompt로 성격 부여하기

Step 1의 코드에서 `system` 속성을 기억하시나요? 이 부분을 수정하면 챗봇의 정체성을 완전히 바꿀 수 있습니다.

- **전문가 모드**: "당신은 10년 차 시니어 소프트웨어 엔지니어입니다. 코드를 리뷰하고 최적화 방안을 제시하세요."
- **엔터테인먼트**: "당신은 조선시대 선비입니다. 현대의 기술을 보고 깜짝 놀란 말투로 대화하세요."

이처럼 시스템 프롬프트는 챗봇 개발의 핵심적인 재미 요소이자 비즈니스 로직을 담는 공간입니다.

---

## 완성된 전체 코드 (Copy & Paste)

### API Route (`app/api/chat/route.ts`)
```typescript
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

export const runtime = 'edge';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    messages,
    system: "당신은 친절한 요리 도우미입니다. 사용자의 질문에 정중하게 답하세요.",
  });

  return result.toDataStreamResponse();
}
```

### Client Page (`app/page.tsx`)
```tsx
'use client';

import { useChat } from 'ai/react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();

  return (
    <div className="flex flex-col w-full max-w-md py-24 mx-auto stretch">
      <h1 className="text-2xl font-bold mb-8 text-center">AI 요리 도우미 🧑‍🍳</h1>
      
      <div className="flex-1 space-y-4 mb-20">
        {messages.length === 0 && (
          <p className="text-gray-500 text-center">궁금한 레시피나 재료를 물어보세요!</p>
        )}
        {messages.map(m => (
          <div 
            key={m.id} 
            className={`p-4 rounded-lg ${m.role === 'user' ? 'bg-blue-100 ml-auto' : 'bg-gray-100'}`}
            style={{ maxWidth: '80%' }}
          >
            <p className="text-sm font-semibold mb-1">
              {m.role === 'user' ? 'User' : 'Chef AI'}
            </p>
            <p className="text-black">{m.content}</p>
          </div>
        ))}
        {isLoading && <div className="text-gray-400">요리봇이 생각 중입니다...</div>}
      </div>

      <form onSubmit={handleSubmit} className="fixed bottom-4 w-full max-w-md bg-white p-2">
        <input
          className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          value={input}
          placeholder="냉장고에 남은 재료는?"
          onChange={handleInputChange}
          disabled={isLoading}
        />
      </form>
    </div>
  );
}
```

---

## 개선 아이디어

여기까지 성공했다면, 다음 단계로 기능을 확장해 보세요.
1. **대화 기록 저장**: 데이터베이스(예: Vercel Postgres)를 연결해 새로고침해도 대화가 유지되게 만듭니다.
2. **로딩 상태 세분화**: `isLoading`을 활용해 스켈레톤 UI나 애니메이션을 넣습니다.
3. **에러 처리**: API 호출 실패 시 사용자에게 친절한 안내 메시지를 띄웁니다.

---

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

---

## 참고 자료
- [Vercel AI SDK Documentation](https://sdk.vercel.ai/docs)
- [Next.js App Router Guide](https://nextjs.org/docs/app)

Tags: AI, LLM, 웹 개발, Python, Tutorial
