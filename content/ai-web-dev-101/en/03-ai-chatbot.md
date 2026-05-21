---
title: "AI Web Development 101 (3/7): Building an AI chatbot — real-time chat with Next.js and the Vercel AI SDK"
series: ai-web-dev-101
episode: 3
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI
- LLM
- Web Development
- Python
- Tutorial
last_reviewed: '2026-05-14'
seo_description: Build a streaming chat UI with Next.js and the Vercel AI SDK, and understand the client-server split behind the chatbot experience.
---

# AI Web Development 101 (3/7): Building an AI chatbot — real-time chat with Next.js and the Vercel AI SDK

Once a terminal call works, the next step is building something a user can actually touch. That is where browser state, streaming responses, server routes, and user experience start interacting.

This is post 3 in the AI Web Development 101 series.

Here, we will build a browser chatbot and focus on the boundary between client UI state and the server route that talks to the model.


![AI Web Development 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/03/chatbot-architecture-overview.en.png)
*AI Web Development 101 chapter 3 flow overview*

## Questions to Keep in Mind

- What changes when you move a terminal example into a browser UI?
- Why is the Next.js plus Vercel AI SDK combination a strong beginner path?
- What should `/api/chat` actually do?

## Why Next.js and the Vercel AI SDK work well here

The first friction point in AI web features is not intelligence. It is perceived latency and state handling. If a long answer appears only after full completion, the UI feels slower than it really is.

The Vercel AI SDK helps with that in three ways:

- streaming responses arrive incrementally
- `useChat` gives you a structured state layer for messages and request status
- Next.js App Router fits naturally with server routes and client components

## Initial project setup

```bash
npx create-next-app@latest my-ai-chatbot --typescript --tailwind --eslint
cd my-ai-chatbot
npm install ai @ai-sdk/react @ai-sdk/openai
```

For local development, keep only an example file in source control.

```text
# .env.local.example
OPENAI_API_KEY=your_api_key_here
```

Commit the example file, not the real `.env.local`.

## Step 1: build the API route

`app/api/chat/route.ts` is the thin server layer between browser messages and the model.

```typescript
import { openai } from "@ai-sdk/openai";
import { convertToModelMessages, streamText, type UIMessage } from "ai";

export const runtime = "edge";
export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages }: { messages: UIMessage[] } = await req.json();

  const result = streamText({
    model: openai("gpt-4o-mini"),
    system: "You are a friendly cooking assistant. Recommend recipes from the user's ingredients.",
    messages: convertToModelMessages(messages),
  });

  return result.toUIMessageStreamResponse();
}
```

Read this route in terms of responsibility:

- `UIMessage[]`: browser-side message history
- `convertToModelMessages(...)`: transforms UI messages into model-facing messages
- `toUIMessageStreamResponse()`: converts the model stream into a response the client can consume incrementally

![Request handling flow inside the API route](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/03/api-route-handler-flow.en.png)

*Request handling flow inside the API route*

![How a user message turns into a model response](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/03/chat-message-roundtrip.en.png)

*How a user message turns into a model response*

## Step 2: build the chat page

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
          placeholder="What ingredients do you have?"
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
      </form>
    </div>
  );
}
```

What matters here:

- `messages` is the conversation state
- `sendMessage(...)` forwards the current input to the server route
- `status` lets the UI avoid duplicate submissions and communicate activity
- `message.parts` keeps the rendering future-proof for non-text response parts

![State flow inside the useChat hook](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/03/usechat-state-flow.en.png)

*State flow inside the useChat hook*

## Step 3: why streaming changes perceived speed

With `useChat` on the client and `streamText` on the server, you get streaming without building raw SSE wiring yourself. The server emits chunks. The browser appends them as they arrive.

That matters because users trust a system more when they see progress quickly. A response that starts rendering immediately feels much faster than a response that stays silent for three seconds and then appears all at once.

![How streaming responses arrive incrementally](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/03/streaming-response-flow.en.png)

*How streaming responses arrive incrementally*

## Step 4: use the system prompt as behavior control

The `system` string in the route is not just an introduction. It is closer to a business rule layer for the chatbot.

- expert mode: “You are a senior software engineer focused on reliability and performance.”
- playful mode: “You speak like a Joseon-era scholar reacting to modern technology.”

Even when the user asks the same question, changing the system prompt can change the experience dramatically.

## Where the first version usually breaks

The first version often fails in predictable ways:

- duplicate submits while a request is already streaming
- missing environment variables in deployment
- route-level errors that never reach the UI clearly
- a system prompt that is too vague to keep the behavior stable

The important habit is to debug across both layers. A browser chatbot problem is often partly a UI-state problem and partly a server-route problem.

## Checklist

- [ ] `/api/chat` owns the model call and the response stream.
- [ ] `useChat` manages message state and request status.
- [ ] The input is disabled while a request is still in flight.
- [ ] The system prompt lives in one predictable place.

## Summary

The heart of a browser chatbot is not the model call by itself. It is the connection between client state and a streaming server route.

- `useChat` gives you a practical baseline for messages and loading state.
- `/api/chat` acts as the transformation layer between UI messages and model messages.
- Streaming improves perceived speed and trust.
- System prompts define behavior, not just tone.

The next chapter moves from chat UI to retrieval, where your app answers from your own documents instead of model memory alone.

## Answering the Opening Questions

- **What changes when you move a terminal example into a browser UI?**
  - The article treats Building an AI chatbot — real-time chat with Next.js and the Vercel AI SDK as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why is the Next.js plus Vercel AI SDK combination a strong beginner path?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What should `/api/chat` actually do?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [AI Web Development 101 (1/7): AI API first steps — sending your first request with the OpenAI API](./01-hello-ai-api.md)
- [AI Web Development 101 (2/7): Prompt engineering basics — getting the answer you actually want](./02-prompt-engineering.md)
- **Building an AI chatbot — real-time chat with Next.js and the Vercel AI SDK (current)**
- RAG introduction — answering with your own data (upcoming)
- First steps with AI agents — making the model use tools (upcoming)
- Deploying an AI web app — shipping to Vercel and Azure (upcoming)
- Evaluating and improving an AI app — measuring quality over time (upcoming)

<!-- toc:end -->

## References

- [Vercel AI SDK: Chatbot guide](https://sdk.vercel.ai/docs/ai-sdk-ui/chatbot) — canonical walkthrough of `useChat` + route handler
- [Vercel AI SDK: `useChat` reference](https://sdk.vercel.ai/docs/reference/ai-sdk-ui/use-chat) — message state and `status` semantics
- [Vercel AI SDK: `streamText` reference](https://sdk.vercel.ai/docs/reference/ai-sdk-core/stream-text) — server-side streaming API used in this chapter
- [Next.js: Route Handlers](https://nextjs.org/docs/app/building-your-application/routing/route-handlers) — App Router conventions that `app/api/chat/route.ts` follows
- [Next.js: Edge Runtime](https://nextjs.org/docs/app/api-reference/edge) — what `export const runtime = "edge"` actually changes
- [Vercel AI SDK examples repository](https://github.com/vercel/ai/tree/main/examples) — additional chatbot and tool-use patterns

Tags: AI, LLM, Web Development, Python, Tutorial
