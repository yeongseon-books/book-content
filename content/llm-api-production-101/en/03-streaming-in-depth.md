---
episode: 3
language: en
last_reviewed: '2026-05-01'
series: llm-api-production-101
status: publish-ready
tags:
- LLM
- OpenAI
- Streaming
- Python
targets:
  ebook: true
  medium: true
  mkdocs: true
  tistory: true
title: Streaming in depth — chunk handling and error recovery
---

# Streaming in depth — chunk handling and error recovery

> LLM API Production 101 (3/6)

Example code: [github.com/yeongseon-books/llm-api-production-101](https://github.com/yeongseon-books/llm-api-production-101/tree/main/en/03-streaming-in-depth)

Streaming looks flashy in a demo, but in production it is really a protocol problem. Showing the first token quickly makes an application feel alive and reduces abandonment on long answers. That part is obvious. What is less obvious is that `stream=True` changes the failure model. Chunks may arrive without text, the connection may go quiet before it ends, the stream may fail after partial output has already been shown, and the final metadata may never arrive.

That means a streamed response should not be treated like an ordinary completion that simply happens to print early. It is better to think of it as a session with partial state. The application needs to render visible progress, reconstruct a final string for logging or persistence, detect inactivity between chunks, and preserve partial output when something breaks. Without that discipline, you end up with the worst kind of bug report: "sometimes the answer stops halfway through."

This post focuses on the consumer side of the Groq streaming path. We will start with the normal chunk loop, then harden it by treating empty deltas as normal, enforcing read timeouts outside the blocking loop, and returning partial results alongside error states.

The goal is not a clever UI effect. The goal is a streaming consumer that can explain what happened when the stream is incomplete.

![Streaming in depth: chunk handling and error recovery](../../../assets/llm-api-production-101/03/03-01-streaming-in-depth-chunk-handling-and-er.en.png)
---

## Runtime setup

The examples assume Python 3.10 or later and the official `groq` SDK.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install groq
export GROQ_API_KEY="your-issued-key"
```

---

## What changes when the response is a stream

A non-streaming request usually ends in one of two states: success with a final object, or failure with an exception. Streaming is more complicated because one request can contain both progress and failure.

Imagine a response like this:

- 30 chunks arrive normally
- then no new chunk appears for 12 seconds
- then the connection fails

That request is not a clean success, but it is not an empty failure either. The user may already have read part of the answer. Your server may already have written partial output into logs. A retry may need to decide whether to start over, append a new answer, or surface the interruption clearly.

For that reason, a streamed request is easier to manage if you explicitly track a few pieces of state:

- the text accumulated so far
- the time of the last meaningful chunk
- whether a normal finish signal was observed
- whether the stream ended by timeout, transport failure, or normal completion

That state gives you something much more useful than a raw exception. It gives you an observable timeline.

---

## The baseline chunk loop

This is still the starting point.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain FastAPI dependency injection for beginners.",
        }
    ],
    temperature=0.2,
    stream=True,
)

parts: list[str] = []

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
        parts.append(delta)

final_text = "".join(parts)
print("\n---")
print(final_text)
```

~~~
Output
**FastAPI Dependency Injection for Beginners**
=====================================================

Dependency injection is a software design pattern that allows components to be loosely coupled, making it easier to test, maintain, and extend your code. In the context of FastAPI, dependency injection is used to manage dependencies between routes, services, and other components.

**What is Dependency Injection?**
--------------------------------

Dependency injection is a technique where one component (the dependent component) receives another component (the dependency) that it needs to function, rather than creating the dependency itself. This decouples the dependent component from the dependency, making it easier to change or replace the dependency without affecting the dependent component.

**Why Use Dependency Injection in FastAPI?**
------------------------------------------

Using dependency injection in FastAPI provides several benefits:

*   **Loose Coupling**: Dependency injection helps to reduce coupling between components, making it easier to change or replace individual components without affecting the entire system.
*   **Testability**: With dependency injection, you can easily mock dependencies for testing purposes, making it easier to write unit tests for your code.
*   **Reusability**: Dependency injection allows you to reuse components and services across multiple routes and applications.

**How to Use Dependency Injection in FastAPI**
---------------------------------------------

FastAPI provides a built-in mechanism for dependency injection using the `@Depends` decorator. Here's an example of how to use it:

    ```python
    from fastapi import Depends, FastAPI
    from pydantic import BaseModel
    
    # Define a service that will be injected as a dependency
    class UserService:
        def __init__(self):
            self.users = [{"id": 1, "name": "John"}]
    
        def get_user(self, user_id: int):
            return self.users[0]
    
    # Create a FastAPI application
    app = FastAPI()
    
    # Define a route that depends on the UserService
    @app.get("/users/{user_id}")
    async def read_user(user_id: int, user_service: UserService = Depends()):
        return user_service.get_user(user_id)
    ```

In this example, the `read_user` route depends on the `UserService` instance, which is injected as a dependency using the `@Depends` decorator. The `UserService` instance is created and passed to the `read_user` route, allowing it to access the `get_user` method.

**Using Dependency Injection with Pydantic Models**
---------------------------------------------------

You can also use dependency injection with Pydantic models to validate and deserialize data. Here's an example:

    ```python
    from fastapi import Depends, FastAPI
    from pydantic import BaseModel
    
    # Define a Pydantic model that depends on a service
    class User(BaseModel):
        id: int
        name: str
    ... (truncated)
~~~python
from fastapi import Depends, FastAPI

app = FastAPI()

# Define a dependency
def get_db():
    # Simulate a database connection
    db = {"users": []}
    return db

# Inject the dependency into a route
@app.get("/users/")
def read_users(db: dict = Depends(get_db)):
    return db["users"]
```

In this example, the `get_db` function is a dependency that returns a simulated database connection. The `Depends` function injects this dependency into the `read_users` route, making it available as the `db` parameter.

**Dependency Injection with Multiple Dependencies**
---------------------------------------------------

You can inject multiple dependencies into a route by using the `Depends` function multiple times:

```python
from fastapi import Depends, FastAPI

app = FastAPI()

# Define dependencies
def get_db():
    # Simulate a database connection
... (truncated)
```

This loop is useful because it serves two audiences at once. The user sees output immediately, while the application keeps a final reconstructed string for storage, moderation, caching, or later analysis.

It is also incomplete for production. It assumes every loop iteration is meaningful, ignores inactivity, and throws away context if an exception interrupts the stream.

---

## Treating empty chunks as normal

One of the easiest mistakes is assuming that every chunk contains visible text. In practice, some chunks may carry role information, stop signals, or metadata with no new content. A robust consumer should treat that as a normal case.

```python
for chunk in stream:
    choice = chunk.choices[0]
    delta = choice.delta.content

    if delta is not None and delta != "":
        print(delta, end="", flush=True)
        parts.append(delta)

    if choice.finish_reason is not None:
        print(f"\nfinish_reason={choice.finish_reason}")
```

This matters mostly because it keeps the consumer calm. Empty chunks are not necessarily warnings. They are part of the protocol. If you log them as failures, your telemetry becomes noisy and harder to trust.

---

## Enforcing timeouts outside the loop

A total request timeout is still useful, but it is not enough for streaming. From the user's point of view, the more direct question is whether progress is still happening. A long answer that keeps producing text is usually acceptable. A silent stream that has produced nothing new for ten seconds often feels broken.

The subtle part is implementation. A plain synchronous `for chunk in stream:` loop cannot detect a true inter-chunk stall by itself, because it is blocked while waiting for the next chunk. Checking `time.monotonic()` inside the loop body only runs after something has already arrived.

To detect real silence between chunks, the timeout has to wrap the read operation itself. Common options are configuring a read timeout in the HTTP client, consuming an async stream with `asyncio.wait_for`, or reading in a background task and applying a deadline to a queue.

The example below shows the async pattern with `asyncio.wait_for` around each streamed read.

```python
import asyncio
import os

from groq import AsyncGroq

INACTIVITY_TIMEOUT_SECONDS = 8.0

client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

async def consume_stream(prompt: str) -> dict:
    stream = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    parts: list[str] = []

    while True:
        try:
            chunk = await asyncio.wait_for(
                anext(stream),
                timeout=INACTIVITY_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError as exc:
            return {"status": "timeout", "text": "".join(parts), "error": str(exc)}
        except StopAsyncIteration:
            return {"status": "completed", "text": "".join(parts)}

        delta = chunk.choices[0].delta.content
        if delta:
            parts.append(delta)
            print(delta, end="", flush=True)

asyncio.run(consume_stream("Explain why Python context managers are useful."))
```

~~~
Output
**What are Python Context Managers?**
====================================

Python context managers are a powerful tool for managing resources such as files, database connections, and locks. A context manager is an object that defines the runtime context to be established when executing a suite of statements. They provide a way to ensure that certain actions are performed, such as closing files or releasing locks, even if an exception is thrown.

**How are Context Managers Useful?**
--------------------------------

1. **Resource Management**: With context managers, you can easily manage resources like files, sockets, or database connections, by ensuring they are properly closed or released after use.

2. **Exception Handling**: Context managers can handle exceptions that occur within the `with` statement, making it easier to write robust code.

3. **Improved Code Readability**: By using context managers, you can write more readable code by explicitly indicating the scope of the operations performed.

4. **Consistent Resource Cleanup**: Context managers ensure that resources such as files, locks, or sockets are cleaned up properly, regardless of whether an exception occurs.

**Example: Using Context Managers with Files**
-----------------------------------------

The following example demonstrates how to use a context manager with a file.

    ```python
    with open('example.txt', 'r') as file:
        content = file.read()
    ```

In this example, when the `with` block is exited (due to executing the next line of code, reaching the end of the block, or an exception), the file is automatically closed, no matter what happens.

**Example: Implementing a Custom Context Manager**
----------------------------------------------

Here's a simple example of implementing a custom context manager:

    ```python
    import time
    
    class Timer:
        def __enter__(self):
            self.start_time = time.time()
            print('Timer started.')
            return self
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            elapsed_time = time.time() - self.start_time
            print(f'Timer stopped. Elapsed time: {elapsed_time:.2f} seconds.')
            if exc_type is not None:
                print(f'An error occurred: {exc_val}')
    
        def read(self):
            time.sleep(2)
            print('Performing some work...')
    
    with Timer() as timer:
        timer.read()
    ```

In this code, the `Timer` class is implemented as a context manager to track and display the execution time of the `read` method within its `with` block.

**Best Practices**
----------------
... (truncated)
~~~python
with open("example.txt", "r") as file:
    contents = file.read()
    print(contents)
```

In this example, the `open` function returns a file object, which is a context manager. The `with` statement creates a runtime context for the file object, acquiring the file resource and releasing it when the block is exited (even if an exception is raised). This ensures that the file is properly closed after reading, preventing a file descriptor leak.

**Implementing a Custom Context Manager**

To create a custom context manager, you can use the `with` statement in conjunction with the `__enter__` and `__exit__` methods. Here's an example:

```python
class LockContextManager:
    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        self.lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()

import threading

lock = threading.Lock()

with LockContextManager(lock) as ctx:
    print("Acquired lock")
    # critical section
    print("Released lock")
```

~~~
Output
Acquired lock
Released lock
~~~

In this example, the `LockContextManager` class implements a context manager that acquires and releases a lock when entering and exiting the `with` block. This ensures that the lock is safely acquired and released, even in the presence of exceptions.
```

The important idea is not the exact number of seconds. It is the distinction between total duration and visible progress, plus the fact that timeout enforcement has to wrap the read itself.

If you need to stay on a synchronous code path, configure a transport timeout up front so the stream does not wait forever. Still, the example below is only a coarse client timeout, not a precise per-chunk inactivity detector. If you need true inter-chunk timing guarantees, the read itself has to be wrapped as shown in the async example.

```python
import os

from groq import Groq

client = Groq(
    api_key=os.environ["GROQ_API_KEY"],
    timeout=8.0,
)

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Explain Python generators."}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

~~~
Output
**What are Generators in Python?**
=====================================

Generators are a special type of function in Python that can be used to generate a sequence of results instead of computing them all at once and returning them in a list, for example. This is particularly useful when working with large datasets or infinite sequences where storing all elements in memory is not feasible.

**How Do Generators Work?**
---------------------------

A generator function is defined using the `yield` keyword instead of the `return` keyword. When a generator is called, it doesn't execute immediately; instead, it creates a generator object. To iterate over the generator, you use the `next()` function.

Here is a basic example of a generator:

    ```python
    def generate_numbers():
        for i in range(10):
            yield i
    
    gen = generate_numbers()
    print(next(gen))  # prints 0
    print(next(gen))  # prints 1
    print(next(gen))  # prints 2
    ```

In this example, the generator `generate_numbers()` yields each number from 0 to 9 when you call `next()` on the `gen` object.

**Generator Functions vs. Regular Functions**
---------------------------------------------

Here's an example that demonstrates the main difference between a generator function and a regular function:

    ```python
    def regular_function():
        return list(range(10))
    
    def generator_function():
        for i in range(10):
            yield i
    
    print(regular_function())  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    gen = generator_function()
    print(next(gen))  # 0
    print(next(gen))  # 1
    print(next(gen))  # 2
    ```

In the first example, `regular_function()` returns the entire list at once, while in the second example, `generator_function()` yields each number one at a time.

**Use Cases**
-------------

Generators are particularly useful when:

*   Working with large datasets where storing all elements in memory is not feasible.
*   Creating an infinite sequence of results.
*   Reducing memory usage in a program.

Here is an example of using a generator to sum the squares of the first `n` natural numbers:

    ```python
    def sum_of_squares(n):
    ... (truncated)
~~~python
def generate_numbers(n):
    for i in range(n+1):
        yield i

for num in generate_numbers(5):
    print(num)
```
This will output:
```
0
1
2
3
4
5
```
As you can see, the `generate_numbers` function uses the `yield` statement to produce each number in the sequence, and then suspends its execution until the next number is requested.

**How Generators Work**
------------------------

Here's a step-by-step breakdown of what happens when you use a generator:

1. The generator function is called, and it returns a generator object.
2. When you iterate over the generator object using a for loop, the generator function is executed until it reaches the `yield` statement.
3. The value produced by the `yield` statement is returned, and the execution of the generator function is suspended.
4. When the next value is requested (by iterating over the generator object again), the generator function resumes execution from where it left off.
5. This process repeats until the generator function reaches the end and returns `None`.

**Advantages of Generators**
---------------------------

Generators have several advantages over traditional iterative approaches:

* **Memory efficiency**: Generators only store one value at a time, making them much more memory-efficient than storing a large list or array of values.
* **Flexibility**: Generators can be easily modified or extended to produce different sequences of values.
* **Performance**: Generators are often faster than traditional iterative approaches, since they don't require storing all values in memory at once.

**Use Cases for Generators**
---------------------------

Generators are particularly useful in the following scenarios:

* **Handling large datasets**: Generators are perfect for handling large datasets that don't fit in memory, since they only store one value at a time.
* **Processing streams of data**: Generators can be used to process streams of data, such as logs or sensor readings, where the data is produced on-the-fly.
* **Creating iterator-based algorithms**: Generators can be used to implement iterator-based algorithms, such as map, filter, and reduce.
... (truncated)
```

---

## Keeping partial output on failure

When a stream fails, the easiest bad decision is to throw away everything received so far. That makes recovery and debugging harder. The user may already have seen part of the answer. The partial text may reveal whether the problem was a mid-sentence interruption, a code block that never closed, or a provider-side termination.

A better pattern is to return a structured result that always includes accumulated text.

```python
import os

from groq import Groq

def stream_text(prompt: str) -> dict:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        stream=True,
    )

    parts: list[str] = []
    finish_reason = None

    try:
        for chunk in stream:
            choice = chunk.choices[0]
            delta = choice.delta.content
            if delta:
                parts.append(delta)
                print(delta, end="", flush=True)

            if choice.finish_reason is not None:
                finish_reason = choice.finish_reason

        return {
            "status": "completed",
            "text": "".join(parts),
            "finish_reason": finish_reason,
            "saw_finish_reason": finish_reason is not None,
        }
    except Exception as exc:
        return {
            "status": "failed",
            "text": "".join(parts),
            "error": str(exc),
            "finish_reason": finish_reason,
            "saw_finish_reason": finish_reason is not None,
        }
```

This wrapper turns a streaming loop into a higher-level result object. The caller can distinguish `completed` and `failed` while still receiving any partial text that was produced before the interruption. Timeout classification is better handled by the transport or async wrapper shown earlier, then mapped into application status at the boundary. The wrapper also preserves the finish-state signal so the caller knows whether the stream ended normally.

That design is especially useful in web applications. A controller can keep the partial output visible, add a notice that generation was interrupted, and decide whether a retry should be automatic or user-triggered.

---

## Signals that the stream may be incomplete

You cannot always prove that one chunk was silently lost, but you can detect suspicious endings.

Common signals include:

- the response ends mid-sentence
- a code block opens but never closes
- the connection ends without a finish reason
- usage metadata is expected but never appears

These checks are not about judging answer quality. They are about checking transport completeness. For Markdown-heavy answers, unmatched code fences are a useful cheap signal. For structured output, a final `json.loads()` check can tell you whether a streamed JSON object likely arrived intact.

The larger point is that production streaming paths should have an idea of what a plausible ending looks like.

---

## Retrying after a streaming failure

Retries are harder for streaming than for plain request-response calls because some output may already have been shown to the user.

Two cases are worth separating.

For **internal pipelines**, a full retry is often fine if no human has seen the partial result yet. You can discard the partial text and request a fresh answer.

For **interactive user interfaces**, preserving context is usually better. Once the user has started reading, restarting from the top can feel confusing. In that case, it is often better to keep the partial output visible, clearly mark the interruption, and let the next attempt appear as a new continuation or a second answer block.

That is one of the important operational truths about streaming: emitted tokens are not retractable. Once they have been sent, the retry policy becomes a UX choice as much as an API choice. It also means timeout support should be designed together with the transport instead of improvised inside a blocking iterator body.

Here is a small caller-side recovery example that keeps partial text visible and then decides whether to retry.

```python
result = stream_text("Explain the difference between FastAPI and Flask.")

print("partial_text=")
print(result["text"])

if result["status"] == "completed":
    print("stream completed normally")
else:
    print("stream interrupted")
    print("show retry button to the user")
```

---

## Closing

In this post, we treated streaming as a protocol with partial state rather than a cosmetic output mode. The practical rules are simple: treat empty chunks as normal, enforce read timeouts outside the blocking loop, preserve accumulated text on failure, and check whether the stream ended in a plausible way instead of assuming every interruption is the same.

Structured output and tool calling made the response boundary more explicit. Streaming stretches that same boundary across time. The next topic stays on the operational side and asks a different question: when similar requests keep arriving, how do you avoid paying the full latency and token cost every time?

<!-- toc:begin -->
## In this series

- [Structured output — JSON mode and response schemas](./01-structured-output.md)
- [Tool calling — connecting functions to the model](./02-tool-calling.md)
- **Streaming in depth — chunk handling and error recovery (current)**
- Caching strategies — reducing cost and latency (upcoming)
- Retry and error handling — making API calls reliable (upcoming)
- Rate limit management — patterns for staying within limits (upcoming)

<!-- toc:end -->

---

## References

- <https://console.groq.com/docs/text-chat>
- <https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events>

Tags: LLM, OpenAI, Streaming, Python
