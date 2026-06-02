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

> **Deprecation notice**: This series is superseded by [`llm-app-foundations-101`](../../llm-app-foundations-101/en/) and [`ai-app-patterns-101`](../../ai-app-patterns-101/en/). New readers are encouraged to start with the successor series.

# AI Web Development 101 (3/7): Building an AI chatbot — real-time chat with Next.js and the Vercel AI SDK

Once a terminal call works, the next step is building something a user can actually touch. That is where browser state, streaming responses, server routes, and user experience start interacting.

This is the 3rd post in the AI Web Development 101 series.

Here, we will build a browser chatbot and focus on the boundary between client UI state and the server route that talks to the model.


![AI Web Development 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/03/chatbot-architecture-overview.en.png)
*AI Web Development 101 chapter 3 flow overview*

> A chatbot is a streaming pipe between browser state and a server route — the UX problem is perceived latency, and the architectural problem is keeping client message state and server model calls cleanly separated.

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

## Chat Contracts to Enforce at the Server Boundary

The most common mistake when building a real-time chat UI is handling model keys directly in browser code. The model provider API must always be called behind a server boundary, and the browser must only call your own `/api/chat`. Drawing this boundary clearly prevents key leaks, call volume explosions, and audit log gaps.

```typescript
// app/api/chat/route.ts
import { streamText } from "ai"
import { openai } from "@ai-sdk/openai"

export const runtime = "edge"

export async function POST(req: Request) {
  const body = await req.json()
  const messages = body.messages ?? []

  const result = streamText({
    model: openai("gpt-4o-mini"),
    system: "You are a Korean development assistant.",
    messages,
    temperature: 0.2,
    maxTokens: 600,
  })

  return result.toDataStreamResponse()
}
```

This structure looks simple, but its real advantage is that model swaps, metric collection, and rate limiting can all happen at this single boundary.

## Separating Prompt Templates from Session Memory

The leading cause of chatbot quality drift is unbounded conversation accumulation. Appending all session messages drives costs up quickly and buries key context. Separate "system instructions," "recent turns," and "retrieval evidence" into distinct blocks.

```typescript
function buildPrompt(input: {
  question: string
  recentTurns: Array<{role: "user" | "assistant"; content: string}>
  contextChunks: string[]
}) {
  return {
    system: [
      "You are a Korean technical support assistant.",
      "If you have no evidence, say you do not know.",
      "Write answers as: 1-sentence summary + 3 key points.",
    ].join("\n"),
    user: [
      `Question: ${input.question}`,
      "Recent conversation:",
      ...input.recentTurns.map((t) => `- ${t.role}: ${t.content}`),
      "Reference documents:",
      ...input.contextChunks,
    ].join("\n"),
  }
}
```

Using this pattern reduces conversation quality degradation even when you attach RAG later.

## Connecting a RAG Pipeline to the Chatbot

To make the chatbot answer from "my documents," you must carefully connect the retrieval pipeline to the chat route. Running retrieval unconditionally on every question can spike latency dramatically, so inserting a question classifier first is worthwhile.

```python
# Backend pseudocode
if is_document_question(user_question):
    query_embedding = embed(user_question)
    chunks = vector_store.search(query_embedding, top_k=4)
    context = "\n\n".join([c.text for c in chunks])
else:
    context = ""

messages = build_messages(question=user_question, context=context)
answer = call_openai(messages)
```

Separating question classification, retrieval, and generation makes it easy to observe which stage is the bottleneck.

## Deployment Configuration Example

Locally `.env.local` is convenient, but production requires platform-specific environment variable injection.

```json
{
  "functions": {
    "app/api/chat/route.ts": {
      "maxDuration": 30
    }
  },
  "env": {
    "AI_MODEL": "gpt-4o-mini"
  }
}
```

```bash
# Vercel CLI
vercel env add OPENAI_API_KEY production
vercel env add AI_MODEL production
```

What matters more than the configuration itself is cross-environment consistency. If the model name and token cap differ between development, staging, and production, debugging cost increases significantly.

## Operational Metrics: Perceived Quality and Cost Together

For chatbot operations, collect at minimum these metrics.

- First Token Latency
- Total response completion time
- Total tokens per user message
- Stream interruption rate
- "Not helpful" feedback ratio

These five metrics alone let you quickly classify whether the problem is frontend, model, or retrieval.

## User Message Policy for Incident Response

In real-time chat, error messages are part of the user experience. Rather than exposing technical details, provide messages that indicate retry availability and next actions.

```text
Responses are temporarily delayed.
- Please try again in 10 seconds.
- If the problem repeats, share the request_id with the support channel.
```

Setting this policy prevents the confusion of frontend and backend emitting different error messages.

## Frontend Patterns for Maintaining Streaming Response Quality

Streaming chat looks fast, but mid-stream interruptions and state races occur frequently. Especially when users press the send button consecutively, session state can become corrupted.

```typescript
const { messages, input, handleInputChange, handleSubmit, status, stop } = useChat({
  api: "/api/chat",
  onError(error) {
    console.error("chat error", error)
  },
})

const canSend = status !== "streaming" && input.trim().length > 0
```

A simple guard like `canSend` alone dramatically reduces duplicate requests. Also, providing a `stop()` action gives users perceived control over the response.

## Conversation Storage Strategy

When storing conversations, save searchable metadata alongside the full transcript.

- `session_id`, `user_id`, `request_id`
- User question summary
- Model name and token usage
- Response generation timestamp and latency

This information is necessary to quickly reproduce quality issues for a specific session later.

## Per-Request Tracking Key for Chatbot Quality

The most useful key in operations is `request_id`. Linking browser events, API logs, and model call logs with the same ID dramatically reduces problem reproduction time.

```typescript
const requestId = crypto.randomUUID()
await fetch("/api/chat", {
  method: "POST",
  headers: { "x-request-id": requestId },
  body: JSON.stringify({ messages }),
})
```

When receiving user inquiries, a single request_id lets you quickly trace the entire flow of that session.

### Verification Questions

Before deployment, confirm: "What does the user see when the response is slow?", "Is duplicate submission blocked?", "Is request ID traceable?" If these three pass, early operational stability improves significantly.


## Summary

The heart of a browser chatbot is not the model call by itself. It is the connection between client state and a streaming server route.

- `useChat` gives you a practical baseline for messages and loading state.
- `/api/chat` acts as the transformation layer between UI messages and model messages.
- Streaming improves perceived speed and trust.
- System prompts define behavior, not just tone.

The next chapter moves from chat UI to retrieval, where your app answers from your own documents instead of model memory alone.

## Answering the Opening Questions

- **What components are needed to move the terminal example to a browser UI?**
  - The browser side needs `useChat()` and `useState` in `app/page.tsx`; the server side needs `app/api/chat/route.ts`. The user sends messages via `sendMessage({ text: input })`, the server relays via `convertToModelMessages(messages)` and `streamText(...)`, then returns via `toUIMessageStreamResponse()` or `toDataStreamResponse()`. The single terminal function call splits into state management, API boundary, and streaming response in the browser.
- **Why is the Next.js + Vercel AI SDK combination well-suited for getting started?**
  - This combination provides message list, `status`, and send flow out of the box via `useChat`, and `streamText` connects streaming responses immediately—so beginners do not have to assemble SSE manually. Locking input when `status === "submitted" || status === "streaming"` and showing "Assistant is writing..." were possible precisely because of that abstraction. Starting with the full boundary is far easier than hand-coding Fetch, state races, and a stream parser from scratch.
- **What role should the `/api/chat` route fulfill?**
  - `/api/chat` is a server boundary that hides the model key, converts browser messages to model messages, and wraps the model stream back into a UI stream. Operational settings like `runtime = "edge"`, `maxDuration = 30`, `temperature: 0.2`, and `maxTokens: 600` belong in this file. The article's point was that future additions—`request_id` headers, rate limiting, metrics collection—all attach at this same boundary.
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
