---
title: "LLM App Foundations 101 (1/6): LLM API first call — sending your first request"
series: llm-app-foundations-101
episode: 1
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- OpenAI
- Prompt Engineering
- Python
last_reviewed: '2026-05-01'
seo_description: 'Walk through your first Groq API call: how the SDK wraps an HTTP request, what fields to read in the response, and which numbers to log from day one.'
---

# LLM App Foundations 101 (1/6): LLM API first call — sending your first request

The first confusing thing about LLM application development is not the model. It is the boundary between your code and the model service. A chat UI makes the whole thing feel magical, but the runtime reality is plain: your application sends an HTTP request and receives a JSON response. That round trip is the foundation.

That is why Post 01 starts here. If you do not understand what goes into the request body, what comes back in the response, and where token usage shows up, every later feature feels blurry.

This is the first post in the LLM App Foundations 101 series. Here, we will build that first call with the Groq API. The setup is intentionally small. You need one environment variable, `GROQ_API_KEY`, and the official Python SDK, `groq`. The model for every example in this article is `llama-3.1-8b-instant`.

We will cover seven things:

- what an LLM API actually is
- how to create a Groq account and issue an API key
- how to install `groq`
- how to send your first request with `client.chat.completions.create()`
- how to read `choices[0].message.content`, `usage`, and `model`
- how synchronous and asynchronous patterns differ
- one complete executable example you can keep as a starting point

The main idea is simple: **an LLM app begins with request and response structure, not with prompt cleverness**.

---

![LLM API first call: sending your first request](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-01-llm-api-first-call-sending-your-first-re.en.png)
*LLM API first call: sending your first request*
> The first call is not magic; it is a remote contract you can inspect field by field.

## Questions to Keep in Mind

- What request-response shape sits underneath the SDK call?
- When the first call fails, should you inspect authentication, the model id, or the message format first?
- Where do you read the response body, token usage, and model name?

## What an LLM API is

![JSON request and response flow](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-01-what-an-llm-api-is.en.png)

*JSON request and response flow*
An LLM API is still an API. The transport is HTTP. The payload is usually JSON. Your code sends input to a remote service, and that service sends structured output back.

From the application's point of view, a typical request answers three questions:

- which model should handle the request
- which messages should be sent as input
- which generation options should shape the output

The response usually answers a different set of questions:

- what text the model generated
- which model produced it
- how many tokens were consumed
- which metadata the provider attached to the result

An SDK makes this feel like a method call, but the underlying contract does not change. `client.chat.completions.create()` still creates a JSON request under the hood and parses a JSON response into a Python object. SDK syntax changes over time, while the mental model of **JSON in, JSON out** stays stable.

Conceptually, the request body looks like this:

```json
{
  "model": "llama-3.1-8b-instant",
  "messages": [
    {
      "role": "user",
      "content": "Show me a small Python example that reads an environment variable."
    }
  ]
}
```

The real response includes more fields, but these three blocks are the ones you should care about first:

```json
{
  "model": "llama-3.1-8b-instant",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "import os\nprint(os.environ['HOME'])"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 24,
    "completion_tokens": 31,
    "total_tokens": 55
  }
}
```

Keep that shape in mind while using the SDK. It will help when you later move to streaming responses, tool calling, or structured outputs.

---

## Creating a Groq account and API key

The account setup is short:

1. Open <https://console.groq.com>.
2. Sign up with GitHub or email.
3. After logging in, open the API Keys section.
4. Create a new key and copy it.
5. Store it in your shell as `GROQ_API_KEY`.

On macOS or Linux, you can start with:

```bash
export GROQ_API_KEY="your-issued-key"
```

On PowerShell:

```powershell
$env:GROQ_API_KEY="your-issued-key"
```

The important habit is keeping the key out of source code. Do not hardcode API keys into Python files. Read them from the environment instead. Every example in this post uses `os.environ["GROQ_API_KEY"]`, which means a missing variable fails immediately.

This tiny script is enough to verify the environment is wired correctly:

```python
import os

api_key = os.environ["GROQ_API_KEY"]
print(f"API key loaded: {api_key[:6]}...")
```

<!-- injected-output:start -->
**Output**

    API key loaded: gsk_Z2...

<!-- injected-output:end -->

You would not print the full key in a real application. A short prefix is enough for local verification.

---

## Installing the SDK

The examples here assume Python 3.10 or later. To install the official SDK:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install groq
```

If you already have a virtual environment, only `pip install groq` is necessary.

It is also useful to confirm which package version your runtime sees:

```bash
python -c "import groq; print(groq.__version__)"
```

At this point, you have everything you need for a first request.

---

## Sending your first request

![Client setup and first call chain](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-02-sending-your-first-request.en.png)

*Client setup and first call chain*
Start with the smallest successful program. The code below sends one request in synchronous style and prints only the generated text. This block is self-contained.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain Python list comprehensions in one paragraph.",
        }
    ],
)

print(completion.choices[0].message.content)
```

<!-- injected-output:start -->
**Output**

    Python list comprehensions are a concise way to create lists by performing an operation on each item in an existing list or other iterable. They consist of brackets containing an expression followed by a 'for' clause, which specifies the sequence of values to be processed, and an optional 'if' clause, which filters the values. The basic syntax is `[expression for element in iterable if condition]`, where `expression` is the operation to be performed on each element, `element` is the variable representing each item, `iterable` is the list or other iterable to be processed, and `condition` (if specified) is a filtering criterion. This syntax allows for efficient and readable creation of new lists by applying transformations and filters to existing data.

<!-- injected-output:end -->

Three lines matter most.

`Groq(...)` creates the client object that will talk to the API.

`model="llama-3.1-8b-instant"` selects the model.

`messages=[...]` provides the chat input. In this first post, one `user` message is enough. Later posts will show how `system`, `user`, and `assistant` messages work together across multiple turns.

Do not focus on the exact wording of the answer. The important result is structural: the request succeeds, and the generated text is available at `choices[0].message.content`.

---

## Inspecting the response object

![Completion object fields and branches](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-03-inspecting-the-response-object.en.png)

*Completion object fields and branches*
Many beginners stop after printing the answer text. That is fine for a smoke test, but it is not enough for a working application. You also need token usage, model identity, and the overall response shape.

The Groq Python SDK returns Pydantic models, so you can convert the response into a dictionary with `to_dict()`. This block is also self-contained.

```python
import json
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain the difference between an HTTP API and an SDK in three sentences.",
        }
    ],
)

print(json.dumps(completion.to_dict(), indent=2, ensure_ascii=False))
```

<!-- injected-output:start -->
**Output**

    {
      "id": "chatcmpl-b73b1087-b403-4f96-85aa-53fdbeeeebaf",
      "choices": [
        {
          "finish_reason": "stop",
          "index": 0,
          "logprobs": null,
          "message": {
            "content": "An HTTP API (Application Programming Interface) is a communication protocol that allows different systems to exchange data by sending HTTP requests and receiving responses, requiring manual parsing and handling of data on the client-side. An SDK (Software Development Kit), on the other hand, is a bundle of pre-built libraries, tools, and resources that provide a more integrated and higher-level interface to access the API, allowing for easier development and interaction with the API. While an HTTP API provides a raw interface for access, an SDK encapsulates this interface and provides a more user-friendly and productive way to use the API's functionality.",
            "role": "assistant"
          }
        }
      ],
      "created": 1777648966,
      "model": "llama-3.1-8b-instant",
      "object": "chat.completion",
      "service_tier": "on_demand",
      "system_fingerprint": "fp_7ccc667439",
      "usage": {
        "completion_tokens": 121,
        "prompt_tokens": 50,
        "total_tokens": 171,
        "completion_time": 0.244874086,
        "prompt_time": 0.002372403,
        "queue_time": 0.008387003,
        "total_time": 0.247246489
      },
      "usage_breakdown": null,
      "x_groq": {
        "id": "req_01kqj256w6fhtb810jkg2hxy8t",
        "seed": 180452821
      }
    }

<!-- injected-output:end -->

When you look through that output, pay attention to three fields first.

### `choices[0].message.content`

This is the actual answer text.

```python
text = completion.choices[0].message.content
print(text)
```

Why `choices[0]`? Because the API shape is designed around a list of candidate outputs. For a beginner app, the first one is usually enough.

### `usage`

This is where token accounting lives.

```python
usage = completion.usage
print(f"prompt_tokens={usage.prompt_tokens}")
print(f"completion_tokens={usage.completion_tokens}")
print(f"total_tokens={usage.total_tokens}")
```

Those numbers are not just nice-to-have metadata. They drive cost tracking, context budgeting, latency analysis, and later optimization work. Token usage becomes a major topic in the next post for exactly that reason.

### `model`

The response also records which model generated the output.

```python
print(completion.model)
```

In a small script this may feel redundant, but in real systems it is worth logging. It makes debugging model changes much easier.

There are more fields you will eventually care about. Two worth noting now:

```python
print(completion.id)                              # unique request ID, useful for support queries
print(completion.choices[0].finish_reason)        # "stop", "length", or "tool_calls"
```

`finish_reason` tells you why the model stopped generating. `"stop"` means a natural end. `"length"` means the model ran out of allowed tokens. Logging both from day one saves debugging time later.

---

## Why the HTTP mental model still matters

![Authentication rate limit and retry branches](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-04-why-the-http-mental-model-still-matters.en.png)

*Authentication rate limit and retry branches*
The SDK handles authentication headers, JSON serialization, response parsing, and typed errors. It does not remove the network boundary.

That boundary explains a lot of beginner problems:

- if the request is slow, network latency may matter more than Python code
- if you get a `401`, check credentials before touching the prompt
- if you get a `429`, think about request rate before model quality
- if a response looks odd, log the full object before guessing

This is the real value of seeing the first call clearly. You stop treating the model as magic and start treating it as a remote service with explicit contracts and failure modes.

---

## Synchronous and asynchronous patterns

![Sync waits and async gather comparison](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-05-synchronous-and-asynchronous-patterns.en.png)

*Sync waits and async gather comparison*
Python gives you two common ways to call an LLM API: synchronous code and asynchronous code.

Synchronous code is usually the better teaching tool. It works well for scripts, notebooks, and small command-line programs.

Asynchronous code becomes important when the rest of your application is already async, or when you want to coordinate multiple I/O-bound tasks. FastAPI services, concurrent LLM fan-out calls, and apps that talk to several external APIs at once are typical examples.

Here is the synchronous pattern again:

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain asynchronous programming in one paragraph.",
        }
    ],
)

print(completion.choices[0].message.content)
```

<!-- injected-output:start -->
**Output**

    Asynchronous programming is a design approach in computer programming where a part of the program can run independently without blocking the main thread, allowing the program to perform multiple tasks concurrently and improving overall responsiveness. It enables the execution of tasks that do not depend on the completion of other tasks, such as network requests, database queries, or file I/O operations. Instead of waiting for these external operations to complete, the program continues executing other tasks, improving performance and reducing wait times. This allows developers to write more efficient and scalable code, as it allows the program to multitask and utilize system resources more effectively.

<!-- injected-output:end -->

And here is the async version. This block is also executable on its own.

```python
import asyncio
import os

from groq import AsyncGroq

client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

async def main() -> None:
    completion = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": "Give me two situations where asyncio is useful.",
            }
        ],
    )

    print(completion.choices[0].message.content)

asyncio.run(main())
```

The structure barely changes. Replace `Groq` with `AsyncGroq`, add `await`, and run the top-level coroutine with `asyncio.run()`.

That small syntax shift matters once you want concurrency. The next example sends three requests in parallel. It is a complete runnable script.

```python
import asyncio
import os

from groq import AsyncGroq

client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

async def ask(question: str) -> str:
    completion = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": question}],
    )
    return completion.choices[0].message.content or ""

async def main() -> None:
    questions = [
        "Explain the difference between a list and a tuple.",
        "Explain the key property of a Python dictionary.",
        "Explain why exception handling matters.",
    ]
    answers = await asyncio.gather(*(ask(question) for question in questions))

    for index, answer in enumerate(answers, start=1):
        print(f"[{index}] {answer}\n")

asyncio.run(main())
```

This is where async becomes a design choice. Once several requests are in flight, you also need to think about rate limits, retries, backoff, and timeouts.

---

## A complete example you can keep

Now let us combine everything into one small script. This is a good baseline for future experiments. It reads the environment variable, sends a request, prints the generated answer, and also prints the metadata you should start watching from day one.

```python
import os

from groq import Groq

def main() -> None:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a concise Python tutor.",
            },
            {
                "role": "user",
                "content": (
                    "Explain the difference between a Python function and a method "
                    "in no more than five sentences, and add one short example line."
                ),
            },
        ],
    )

    content = completion.choices[0].message.content or ""
    usage = completion.usage

    print("=== answer ===")
    print(content)
    print()
    print("=== metadata ===")
    print(f"model: {completion.model}")
    print(f"prompt_tokens: {usage.prompt_tokens}")
    print(f"completion_tokens: {usage.completion_tokens}")
    print(f"total_tokens: {usage.total_tokens}")

if __name__ == "__main__":
    main()
```

<!-- injected-output:start -->
**Output**

    === answer ===
    A Python function is a standalone block of code that performs a specific task, whereas a method is a function that belongs to a class or object. A method is typically used to modify or interact with the state of an object, whereas a function does not have access to the object's state. Functions are created using the `def` keyword, whereas methods are called using an object reference followed by the method name. In other words, a function is a general-purpose routine, while a method is an action performed on an object. 

    ```python
    # The `greet` function is similar to the `say_hello` method, but does not need to be bound to an instance of a class
    greet = lambda: print("Hello!")
    ```

    === metadata ===
    model: llama-3.1-8b-instant
    prompt_tokens: 67
    completion_tokens: 151
    total_tokens: 218

<!-- injected-output:end -->

If you save it as `first_call.py`, run it with:

```bash
python first_call.py
```

You should expect three things:

- generated answer text
- `model: llama-3.1-8b-instant`
- numeric token counts for prompt, completion, and total

That is enough to say you have completed the first real milestone of LLM app development.

---

## Closing thoughts

The program we wrote today is short, but it already contains the core loop of an LLM application: load the key from the environment, build a client, send messages to a model, and read text plus metadata from the response.

In the next post, we will stay close to the same API call and zoom in on token accounting. Once prompts get longer, token count becomes the thing that shapes cost, limits, and response behavior. That is the next foundation to put in place.

## Operational checklist

- [ ] `GROQ_API_KEY` is set as an environment variable; no key string appears in source
- [ ] `pip install groq` succeeded and `import groq` runs without error
- [ ] `client.chat.completions.create(model=..., messages=[...])` returns a 200 response
- [ ] You printed `choices[0].message.content`, `usage.total_tokens`, and `model` from the response
- [ ] You ran the same call once synchronously and once asynchronously

## Answering the Opening Questions

- What request-response shape sits underneath the SDK call?
  - The SDK call wraps a remote API contract: model and messages go out, while generated text, usage, and metadata come back.

- When the first call fails, should you inspect authentication, the model id, or the message format first?
  - Start with authentication and key placement, then narrow the failure to the model id and message shape.

- Where do you read the response body, token usage, and model name?
  - Read text from `choices[0].message.content`, token accounting from `usage`, and the actual model from `model`.

<!-- toc:begin -->
## In this series

- **LLM App Foundations 101 (1/6): LLM API first call — sending your first request (current)**
- LLM App Foundations 101 (2/6): Understanding tokens — cost, limits, and context windows (upcoming)
- LLM App Foundations 101 (3/6): Prompt engineering basics — system, user, and assistant roles (upcoming)
- LLM App Foundations 101 (4/6): Few-shot and chain-of-thought — steering better answers (upcoming)
- LLM App Foundations 101 (5/6): Managing conversation state — building a multi-turn chatbot (upcoming)
- LLM App Foundations 101 (6/6): Handling streaming responses — real-time output (upcoming)

<!-- toc:end -->

---

## References

- [Groq quickstart](https://console.groq.com/docs/quickstart)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Groq models](https://console.groq.com/docs/models)

### Related Series

- [LLM API Production 101](../../llm-api-production-101/en/01-structured-output.md) — picks up where this series ends. After first calls, tokens, and basic prompting, that series tackles structured output, tool calling, streaming, and retries — the problems you hit once the toy demo has to actually serve users.

Tags: LLM, OpenAI, Prompt Engineering, Python
