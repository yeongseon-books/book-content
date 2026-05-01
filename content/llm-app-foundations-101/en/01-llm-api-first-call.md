---
title: LLM API first call — sending your first request
series: llm-app-foundations-101
episode: 1
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- OpenAI
- Prompt Engineering
- Python
last_reviewed: '2026-05-01'
---

# LLM API first call — sending your first request

> LLM App Foundations 101 (1/6)

Example code: [github.com/yeongseon-books/llm-app-foundations-101](https://github.com/yeongseon-books/llm-app-foundations-101/tree/main/en/01-llm-api-first-call)

The diagram below shows the smallest round trip behind a first LLM API call.

![LLM API first call: sending your first request](../../../assets/llm-app-foundations-101/01/01-01-llm-api-first-call-sending-your-first-re.en.png)
The first confusing thing about LLM application development is not the model. It is the boundary between your code and the model service. A chat UI makes the whole thing feel magical, but the runtime reality is plain: your application sends an HTTP request and receives a JSON response. That round trip is the foundation.

That is why Post 01 starts here. If you do not understand what goes into the request body, what comes back in the response, and where token usage shows up, every later feature feels blurry.

In this post, we will build that first call with the Groq API. The setup is intentionally small. You need one environment variable, `GROQ_API_KEY`, and the official Python SDK, `groq`. The model for every example in this article is `llama-3.1-8b-instant`.

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

## What an LLM API is

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

~~~
Output
API key loaded: gsk_Z2...
~~~

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

~~~
Output
Python list comprehensions are a powerful feature that allows you to create new lists in a concise and readable manner. They consist of brackets containing the expression, which is executed for each element, along with the 'for' loop to specify the input iterable and the 'if' clause to filter the elements. The general syntax is: `[expression for element in iterable if condition]`, where 'expression' is the operation performed on each 'element' from the 'iterable', and 'condition' is an optional filter applied to the result. For example, `[x**2 for x in range(10) if x % 2 == 0]` creates a new list containing the squares of even numbers from 0 to 9. List comprehensions provide a compact way to manipulate data and are often used for tasks such as filtering, sorting, and transforming data.
~~~

Three lines matter most.

`Groq(...)` creates the client object that will talk to the API.

`model="llama-3.1-8b-instant"` selects the model.

`messages=[...]` provides the chat input. In this first post, one `user` message is enough. Later posts will show how `system`, `user`, and `assistant` messages work together across multiple turns.

Do not focus on the exact wording of the answer. The important result is structural: the request succeeds, and the generated text is available at `choices[0].message.content`.

---

## Inspecting the response object

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

~~~
Output
{
  "id": "chatcmpl-315171e7-e2ec-4bb3-8e24-d9eb6ef54e57",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "content": "An HTTP API is a remote service that exposes endpoints for sending and receiving data over the web using HTTP protocols. It typically requires clients to manually construct and send HTTP requests, parse responses, and handle errors, making it a more low-level interface. \n\nOn the other hand, an SDK (Software Development Kit) is a pre-built library or framework that provides a higher-level abstraction for interacting with a service or API, allowing developers to write more code in their chosen programming language, with less manual HTTP request management.",
        "role": "assistant"
      }
    }
  ],
  "created": 1777647296,
  "model": "llama-3.1-8b-instant",
  "object": "chat.completion",
  "service_tier": "on_demand",
  "system_fingerprint": "fp_7ccc667439",
  "usage": {
    "completion_tokens": 103,
    "prompt_tokens": 50,
    "total_tokens": 153,
    "completion_time": 0.199277411,
    "prompt_time": 0.002788606,
    "queue_time": 0.007095763,
    "total_time": 0.202066017
  },
  "usage_breakdown": null,
  "x_groq": {
    "id": "req_01kqj0j86rf7rr6s9538vfmav7",
    "seed": 512895673
  }
}
~~~

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

The SDK handles authentication headers, JSON serialization, response parsing, and typed errors. It does not remove the network boundary.

That boundary explains a lot of beginner problems:

- if the request is slow, network latency may matter more than Python code
- if you get a `401`, check credentials before touching the prompt
- if you get a `429`, think about request rate before model quality
- if a response looks odd, log the full object before guessing

This is the real value of seeing the first call clearly. You stop treating the model as magic and start treating it as a remote service with explicit contracts and failure modes.

---

## Synchronous and asynchronous patterns

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

~~~
Output
Asynchronous programming is a technique used in software development where certain operations are executed in the background without blocking the main thread of execution. This allows the program to continue running without waiting for the completion of a specific task, improving overall responsiveness and efficiency. Asynchronous code is typically written using callback functions, promises, or async/await syntax, which enables the program to proceed with other tasks while waiting for the completion of a time-consuming operation, such as I/O operations (e.g., reading from a file or database), network requests, or computations that may take a long time to complete. By utilizing concurrency and non-blocking I/O, asynchronous programming enables the development of scalable, high-performance applications that can handle multiple tasks simultaneously.
~~~

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

~~~
Output
**Asynchronous Programming with asyncio**

Asynchronous programming allows for non-blocking I/O operations, leading to efficient use of system resources and improved responsiveness in applications. `asyncio` in Python is a built-in module that simplifies asynchronous programming and makes it easier to write concurrent code.

### Situation 1: Making API Calls

Imagine you're building a web scraper that needs to fetch data from multiple APIs concurrently. You can use `asyncio` to make simultaneous requests to each API endpoint and then wait for all responses.

    ```python
import asyncio

async def fetch_data(url):
    # Simulate a network delay using async.sleep()
    await asyncio.sleep(2)
    return f"Fetched data from {url}"

async def main():
    # Create a list of URLs to fetch data from
    urls = ["https://api1.com", "https://api2.com", "https://api3.com"]

    # Use asyncio.gather() to run fetch_data() concurrently for each URL
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)

    # Print the results
    for result in results:
        print(result)

asyncio.run(main())
    ```

### Situation 2: Handling Multiple Database Queries

Suppose you're building a database-driven application that needs to execute multiple queries on different tables concurrently. You can use `asyncio` to create a task for each query and wait for all tasks to complete.

    ```python
import asyncio
import sqlite3

async def execute_query(db, query):
    # Simulate a database query using async.sleep()
    await asyncio.sleep(2)
    return f"Query executed on {db}"

async def main():
    # Connect to the database
    conn = sqlite3.connect(":memory:")
    db = conn.cursor()

    # Create a list of queries to execute
    queries = ["SELECT * FROM table1", "SELECT * FROM table2", "SELECT * FROM table3"]

    # Use asyncio.gather() to run execute_query() concurrently for each query
    tasks = [execute_query(db, query) for query in queries]
    results = await asyncio.gather(*tasks)

    # Print the results
    for result in results:
        print(result)

... (truncated)
~~~

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

~~~
Output
[1] In Python, both lists and tuples are used to store a collection of items, but they are implemented differently and provide different functionality.

**Lists:**

Lists are ordered collections of items, which can be of any data type, including strings, integers, floats, and other lists. Lists are denoted by square brackets `[]` and are mutable, meaning their contents can be modified after creation.

Here are some key characteristics of lists:

*   Ordered: The elements in a list have a specific order and can be accessed by their index position.
*   Mutable: Lists can be modified after creation by adding, removing, or modifying their elements.
*   Dynamic: The size of a list can be increased or decreased dynamically.

**Tuples:**

Tuples are also ordered collections of items, but unlike lists, they are immutable, meaning their contents cannot be modified after creation. Tuples are denoted by parentheses `()`.

Here are some key characteristics of tuples:

*   Ordered: The elements in a tuple have a specific order and can be accessed by their index position.
*   Immutable: Tuples cannot be modified after creation by adding, removing, or modifying their elements.
*   Dynamic: The size of a tuple can be determined at creation time and cannot be changed.

**Key differences:**

1.  **Immutability**: The most significant difference between lists and tuples is that lists are mutable, while tuples are immutable.
2.  **Performance**: Tuples are generally faster and more memory-efficient than lists because they cannot be modified.
3.  **Function call arguments**: Tuples can be used as function call arguments, but lists cannot.
4.  **Return values**: Tuples can be returned from functions, and they provide an easy way to group multiple return values.

**Example:**

    ```python
# Create a list
my_list = [1, 2, 3, 4, 5]
print(my_list)  # Output: [1, 2, 3, 4, 5]

# Modify the list
my_list.append(6)
print(my_list)  # Output: [1, 2, 3, 4, 5, 6]

# Create a tuple
my_tuple = (1, 2, 3, 4, 5)
print(my_tuple)  # Output: (1, 2, 3, 4, 5)

# Try to modify the tuple (this will result in an error)
try:
    my_tuple[0] = 10
except TypeError:
    print("Error: Tuples are immutable.")

    ```

In summary, while both lists and tuples can be used to store collections of items in Python, lists are mutable, while tuples are immutable. The choice between a list and a tuple depends on whether you need to modify the contents of the collection after its creation.

[2] **Key Properties of Python Dictionaries**

In Python, a dictionary is an unordered collection of key-value pairs. The key properties of a Python dictionary are:

1. **Uniqueness**: Each key in a dictionary must be unique. If you try to assign a key that already exists in the dictionary, its associated value will be overwritten.
2. **Hashable**: Keys of a dictionary must be hashable, which means they must be immutable and have a unique hash value. This allows the dictionary to efficiently store and retrieve key-value pairs.
... (truncated)
~~~

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

~~~
Output
=== answer ===
In Python, a function is a standalone block of code that can be called multiple times from various parts of a program. A method, on the other hand, is a function that belongs to a class or object. 
Methods operate on the state of the object they belong to, whereas functions do not. 
Here's an example of the difference: 

    ```python
# Function: can be called standalone
def greet(name): return "Hello, " + name

# Method: part of a class
class Person: 
    def __init__(self, name): self.name = name
    def greet(self): return "Hello, " + self.name
    ```

=== metadata ===
model: llama-3.1-8b-instant
prompt_tokens: 67
completion_tokens: 136
total_tokens: 203
~~~

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

<!-- toc:begin -->
## In this series

- **LLM API first call — sending your first request (current)**
- Understanding tokens — cost, limits, and context windows (upcoming)
- Prompt engineering basics — system, user, and assistant roles (upcoming)
- Few-shot and chain-of-thought — steering better answers (upcoming)
- Managing conversation state — building a multi-turn chatbot (upcoming)
- Handling streaming responses — real-time output (upcoming)

<!-- toc:end -->

---

## References

- [Groq quickstart](https://console.groq.com/docs/quickstart)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Groq models](https://console.groq.com/docs/models)

Tags: LLM, OpenAI, Prompt Engineering, Python
