---
title: Prompt engineering basics — system, user, and assistant roles
series: llm-app-foundations-101
episode: 3
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
last_reviewed: '2026-05-15'
seo_description: Learn how to structure LLM prompts effectively by separating system, user, and assistant roles to ensure consistent, controllable model behavior.
---

# Prompt engineering basics — system, user, and assistant roles

> LLM App Foundations 101 (3/6)

Example code: [github.com/yeongseon-books/llm-app-foundations-101](https://github.com/yeongseon-books/llm-app-foundations-101/tree/main/en/03-prompt-engineering-basics)

The diagram below shows the basic flow of role-based prompt construction.

![Prompt engineering basics: system, user, and assistant roles](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-01-prompt-engineering-basics-system-user-an.en.png)

*Prompt engineering basics: system, user, and assistant roles*
Prompt engineering is often described as clever wording. In application work, that is too narrow. The real job is to separate instructions by role, decide which rules stay stable across requests, and shape how the model responds. The difference between a weak prompt and a dependable prompt is usually the structure of the `messages` array.

That structure matters early. Without it, tone drifts, output format changes between calls, follow-up questions lose context, and parameter tuning feels random. Many “model reliability” problems are really input-structure problems.

This is the third post in the LLM App Foundations 101 series. Here, we use Groq's `llama-3.1-8b-instant` to build the core mental model for prompt design with chat completions. We will cover seven things:

- what `system`, `user`, and `assistant` roles mean
- how a system message changes overall behavior
- how assistant messages carry multi-turn history
- how `temperature` and `top_p` shape the creativity vs consistency trade-off
- a practical prompt structure pattern
- how to place few-shot examples inside the `messages` array
- common prompt design mistakes

The main idea is simple: **good prompts start as structured message roles, not as one long user sentence**.

---

## Questions this chapter answers

- How does the model treat `system`, `user`, and `assistant` differently?
- What single experiment shows how a one-line system message changes the answer?
- When is hand-writing assistant messages into history the right pattern?
- How do you decide which constraint belongs in `system` vs `user` vs few-shot examples?
- Where does the output quality gap between with/without `system` show up most clearly?

## Why prompt engineering is more than wording

In Post 01, one `user` message was enough to make the first API call. Real applications move beyond that quickly. They need stable behavior across users, consistent output shape, and memory of earlier turns. Once those requirements appear, one free-form user string stops being enough.

Chat-based LLM APIs solve this with role-tagged messages. That is not cosmetic syntax. It separates operating policy from the current request and from prior conversation state.

- `system`: global behavior and boundaries
- `user`: the current request
- `assistant`: what the model said earlier in the conversation

Once you think in those layers, prompt design becomes easier to maintain.

---

## Understanding the three roles

![Roles merged into one messages array](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-01-understanding-the-three-roles.en.png)

*Roles merged into one messages array*
Each role has a different purpose.

### `system`

The `system` message defines the model's default behavior. Put tone, response language, safety boundaries, output conventions, and high-level identity here.

The operational point is that `system` is not about the current task details. It is about **cross-request policy**. If a rule should apply almost every time your app calls the model, it probably belongs here.

### `user`

The `user` message holds the current request. The question, task description, attached context, and request-specific constraints belong here.

### `assistant`

The `assistant` role is used when you replay the model's earlier answer back into the next request. If you want the next turn to know what the model already said, your application needs to include that history explicitly.

That means multi-turn conversation is not a hidden built-in memory feature. It is **application-managed reconstruction of the `messages` array**.

---

## How a system message changes the answer

![Same question with and without system](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-02-how-a-system-message-changes-the-answer.en.png)

*Same question with and without system*
It is easier to understand `system` by comparing outputs directly. The script below sends the same user question twice. The first request has no system message. The second adds a system instruction that constrains language, audience, and output structure. The contrast is usually obvious.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

question = "Explain the difference between a Python dictionary and a list."

without_system = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": question},
    ],
    temperature=0.2,
)

with_system = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a Python tutor for beginners. "
                "Always answer in English. "
                "Start with one short paragraph, then end with exactly three bullet points. "
                "Do not guess, and keep the explanation beginner-friendly."
            ),
        },
        {"role": "user", "content": question},
    ],
    temperature=0.2,
)

print("[without system]")
print(without_system.choices[0].message.content)
print()
print("[with system]")
print(with_system.choices[0].message.content)
```

<!-- injected-output:start -->
**Output**

    [without system]
    **Python Dictionaries vs Lists: Key Differences**
    =====================================================

    In Python, `dict` (dictionary) and `list` are two fundamental data structures used to store collections of data. While both can store multiple values, they differ significantly in their structure, usage, and application.

    **List**
    --------

    A `list` is an ordered collection of items that can be of any data type, including strings, integers, floats, and other lists. Lists are denoted by square brackets `[]` and are indexed, meaning each item has a unique position.

    **Example:**
    ```python
    my_list = [1, 2, 3, "hello", 4.5]
    print(my_list[0])  # Output: 1
    ```
    **Dictionary**
    --------------

    A `dict` (dictionary) is an unordered collection of key-value pairs. Dictionaries are denoted by curly brackets `{}` and are indexed by keys, which can be any immutable data type (e.g., strings, integers, tuples).

    **Example:**
    ```python
    my_dict = {"name": "John", "age": 30, "city": "New York"}
    print(my_dict["name"])  # Output: John
    ```
    **Key differences:**

    1. **Order**: Lists are ordered, while dictionaries are unordered.
    2. **Indexing**: Lists are indexed by their position, while dictionaries are indexed by keys.
    3. **Data type**: Lists can store any data type, while dictionaries can only store key-value pairs.
    4. **Lookup**: Lists require iterating through the collection to find a specific item, while dictionaries allow for fast lookup using the key.

    **When to use each:**

    * Use a `list` when:
    	+ You need to store a collection of items in a specific order.
    	+ You need to perform operations like indexing, slicing, or sorting.
    * Use a `dict` when:
    	+ You need to store key-value pairs.
    	+ You need to perform fast lookups using keys.

    In summary, while both lists and dictionaries can store multiple values, they differ in their structure, usage, and application. Choose the right data structure based on your specific needs.

    [with system]
    In Python, a dictionary and a list are two different data structures that are used to store collections of data. The main difference between them is that a list is an ordered collection of items, where each item has an index or position, whereas a dictionary is an unordered collection of key-value pairs. Think of a list like a shopping list where you have items in a specific order, and a dictionary like a phonebook where you have names (keys) associated with phone numbers (values).

    Here are some key differences:
    * **Ordered vs Unordered**: Lists are ordered, while dictionaries are unordered.
    * **Indexed vs Keyed**: Lists are indexed by a numerical index, while dictionaries are keyed by a unique value.
    * **Homogeneous vs Heterogeneous**: Lists can only contain items of the same data type, while dictionaries can contain items of different data types.

<!-- injected-output:end -->

The facts may overlap, but the style usually does not. A good system message makes these parts more stable:

- response language
- tone and audience level
- output structure
- answer length tendencies
- behavior under uncertainty

A system message is not a perfect hard lock. It is the strongest steering input, not an absolute guarantee.

---

## Building multi-turn history with assistant messages

![Assistant reply replay in the next turn](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-03-building-multi-turn-history-with-assista.en.png)

*Assistant reply replay in the next turn*
In many application flows, the provider does not remember the full conversation for you. If the next request only includes the latest user message, the model only sees that latest message.

To preserve context, the application has to replay the conversation, including the model's earlier answer as an `assistant` message.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": "You are a Python learning assistant. Be brief and precise.",
    },
    {
        "role": "user",
        "content": "Explain the difference between Python lists and tuples in one paragraph.",
    },
]

first = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.2,
)

assistant_text = first.choices[0].message.content
print("[assistant turn 1]")
print(assistant_text)
print()

messages.append({"role": "assistant", "content": assistant_text})
messages.append(
    {
        "role": "user",
        "content": "Add a short code example in no more than five lines.",
    }
)

second = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.2,
)

print("[assistant turn 2]")
print(second.choices[0].message.content)
```

<!-- injected-output:start -->
**Output**

    [assistant turn 1]
    In Python, lists and tuples are both data structures used to store multiple values, but they differ in their mutability. Lists are mutable, meaning their contents can be modified after creation, and are denoted by square brackets `[]`. Tuples, on the other hand, are immutable, meaning their contents cannot be modified after creation, and are denoted by parentheses `()`. This difference in mutability affects how they are used in code, with lists often being used when the data needs to be changed, and tuples when the data is fixed and should not be altered.

    [assistant turn 2]
    In Python, lists and tuples are both data structures used to store multiple values, but they differ in their mutability. Lists are mutable, meaning their contents can be modified after creation, and are denoted by square brackets `[]`. Tuples, on the other hand, are immutable, meaning their contents cannot be modified after creation, and are denoted by parentheses `()`. This difference in mutability affects how they are used in code, with lists often being used when the data needs to be changed, and tuples when the data is fixed and should not be altered.

    ```python
    # Create a list and a tuple
    my_list = [1, 2, 3]
    my_tuple = (1, 2, 3)

    # Attempt to modify the tuple (will raise an error)
    try:
        my_tuple[0] = 4
    except TypeError:
        print("Tuples are immutable!")
    ```

<!-- injected-output:end -->

That append step is the core of chatbot memory.

This cannot grow forever. As Post 02 showed, conversation history consumes tokens. In practice, applications usually choose one of three strategies:

- keep only the most recent turns
- summarize older turns into a shorter memory
- store key facts separately in structured state

Post 05 will cover conversation state in more depth. For now, the key takeaway is simple: multi-turn chat is explicit message replay.

---

## Temperature and top_p: consistency versus variety

![Low and high sampling control comparison](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-04-temperature-and-top-p-consistency-versus.en.png)

*Low and high sampling control comparison*
Prompt wording is only part of output control. Sampling parameters matter too. The first two to learn are `temperature` and `top_p`.

### `temperature`

`temperature` affects how broadly the model explores likely next-token choices. Lower values usually make the answer more conservative and repeatable. Higher values usually allow more variation in wording and structure.

- values near `0.0` favor consistency
- higher values such as `0.7` or `0.9` allow more variation
- extraction, classification, and strict formatting usually start low
- brainstorming or copy ideation can tolerate higher values

This script compares `temperature=0.0` and `temperature=0.9` with the same prompt.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

prompt = "Introduce FastAPI to a beginner in three sentences."

for temperature in (0.0, 0.9):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a technical editor. Keep answers concise.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )

    print(f"[temperature={temperature}]")
    print(completion.choices[0].message.content)
    print()
```

<!-- injected-output:start -->
**Output**

    [temperature=0.0]
    FastAPI is a modern, fast (high-performance), web framework for building APIs with Python. It allows developers to create robust, scalable, and secure APIs quickly and efficiently, with features like automatic API documentation and support for asynchronous programming. FastAPI is designed to be highly productive, with a focus on simplicity, readability, and ease of use, making it an ideal choice for building web APIs.

    [temperature=0.9]
    FastAPI is a modern, fast (high-performance), web framework for building APIs with Python. It's designed to simplify the creation of robust and efficient APIs, with features like automatic API documentation, built-in support for WebSockets, and high performance thanks to the use of asynchronous programming. FastAPI is ideal for building scalable APIs that can handle high traffic and are easy to maintain.

<!-- injected-output:end -->

### `top_p`

`top_p` constrains token selection by cumulative probability mass. Lower values keep the model inside a narrower band of likely continuations. Higher values admit a wider range.

At the beginner stage, two habits are enough:

- start by adjusting `temperature` first
- avoid making large changes to both `temperature` and `top_p` at the same time unless you have a specific reason

Both parameters influence output diversity, so changing both aggressively makes results harder to explain.

---

## A practical prompt structure pattern

The most reusable beginner-friendly pattern is **instruction + context + output format**. Instead of writing one long request blob, split the prompt into three explicit parts.

```text
Instruction: what the model should do
Context: who the answer is for or what situation matters
Output format: how the answer should be shaped
```

That pattern maps cleanly into chat messages.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a Python tutor for backend beginners. "
                "Answer in English and do not guess."
            ),
        },
        {
            "role": "user",
            "content": (
                "Instruction: explain what a dataclass is.\n"
                "Context: the reader knows basic Python syntax but has never used dataclasses.\n"
                "Output format: 1) two-sentence explanation 2) code example in six lines or less 3) one-line use case"
            ),
        },
    ],
    temperature=0.2,
)

print(completion.choices[0].message.content)
```

<!-- injected-output:start -->
**Output**

    **What is a dataclass?**

    A dataclass is a special type of class in Python that automatically generates special methods like `__init__`, `__repr__`, and `__eq__` based on the class's attributes. This makes it easier to create classes that primarily hold data and don't need complex logic.

    **Example code:**
    ```python
    from dataclasses import dataclass

    @dataclass
    class Person:
        name: str
        age: int

    p = Person("John", 30)
    print(p)  # Output: Person(name='John', age=30)
    ```

    **Use case:** Use dataclasses to define simple data structures, such as user profiles, product information, or game objects, where the focus is on storing and representing data rather than complex behavior.

<!-- injected-output:end -->

This works well because the task is explicit, the background stays visible, and the output shape becomes testable.

---

## Placing few-shot examples inside the messages array

Few-shot prompting means showing the model one or more examples of the behavior you want before asking for the real answer. Post 04 will go deeper, but the basic mechanism is straightforward: the examples also live inside the same `messages` array.

One common pattern is to add paired `user` and `assistant` examples before the final user request.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": "You explain Python concepts as a one-line definition followed by a one-line analogy.",
    },
    {"role": "user", "content": "What is a class?"},
    {
        "role": "assistant",
        "content": "Definition: A class is a blueprint for creating objects.\nAnalogy: It is like a mold used to produce many objects with the same shape.",
    },
    {"role": "user", "content": "What is inheritance?"},
    {
        "role": "assistant",
        "content": "Definition: Inheritance lets a new class reuse attributes and behavior from an existing class.\nAnalogy: It is like starting from a base template and extending it instead of rebuilding from scratch.",
    },
    {"role": "user", "content": "What is a decorator?"},
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.2,
)

print(completion.choices[0].message.content)
```

<!-- injected-output:start -->
**Output**

    Definition: A decorator is a function that modifies or extends the behavior of another function without permanently changing it.
    Analogy: It is like a gift wrapper that adds a new layer to a present without altering its original contents.

<!-- injected-output:end -->

This can be very effective, but every example consumes tokens. Short, representative examples usually work better than long ones.

---

## Common prompt design mistakes

![Prompt mistakes that destabilize output](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/03/03-05-common-prompt-design-mistakes.en.png)

*Prompt mistakes that destabilize output*
These mistakes show up repeatedly in first-generation LLM apps.

### Putting shared policy only in the user message

If every request repeats “answer in English,” “be concise,” and “return bullet points,” the prompt becomes harder to manage. Shared policy belongs in `system` unless there is a strong reason not to.

### Mixing instructions and raw data into one blob

If the task, background, input data, and output rules are all packed into one paragraph, the model has to infer priorities. Explicit structure usually improves repeatability before it improves brilliance.

### Expecting memory without replaying history

If you do not re-send the earlier turns, the model cannot reliably refer back to them. Multi-turn quality problems often start here.

### Using high temperature while demanding strict formatting

Creative sampling and rigid structure pull in different directions. If the task is extraction, classification, or stable formatting, start with a lower temperature.

### Overspending tokens on long few-shot examples

Examples should be compact and pattern-rich. Verbose examples often waste context budget without adding much steering value.

### Using vague terms such as “better,” “nicely,” or “in detail”

Vague adjectives are weak control surfaces. Concrete constraints such as paragraph count, bullet count, JSON keys, or line limits are easier to evaluate.

### Over-trusting one good sample

A prompt is not validated because it worked once. Test it against different question types, edge cases, and parameter settings. Otherwise you end up shipping a lucky demo instead of a reliable pattern.

---

## Closing thoughts

The starting point of prompt engineering is not elegant phrasing. It is role-aware structure. Use `system` for persistent policy, `user` for the current request, and `assistant` for the history you want the next turn to see. Add careful parameter choices on top of that, and the same model becomes much more predictable.

The next post goes deeper into few-shot prompting and chain-of-thought.

## Operational checklist

- [ ] Your code always orders `messages` as `system` → `user` → `assistant`
- [ ] You have compared one user input answered with vs. without a system message
- [ ] Hardcoded system prompts are extracted to a constant or config file
- [ ] You have a test that synthesizes a multi-turn history with hand-crafted assistant messages
- [ ] Format requirements (JSON, table, max length) are written into the system message explicitly

<!-- toc:begin -->
## In this series

- [LLM API first call — sending your first request](./01-llm-api-first-call.md)
- [Understanding tokens — cost, limits, and context windows](./02-understanding-tokens.md)
- **Prompt engineering basics — system, user, and assistant roles (current)**
- Few-shot and chain-of-thought — steering better answers (upcoming)
- Managing conversation state — building a multi-turn chatbot (upcoming)
- Handling streaming responses — real-time output (upcoming)

<!-- toc:end -->

---

## References

### Official docs

- [Groq Docs: Text chat](https://console.groq.com/docs/text-chat)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [OpenAI Platform Docs: Text generation and messages](https://platform.openai.com/docs/guides/text)
- [Anthropic Docs: Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

### Related series

- [Few-shot and chain-of-thought — steering better answers](./04-few-shot-and-cot.md)
- [Managing conversation state — building a multi-turn chatbot](./05-conversation-state.md)
- [Tool calling — connecting functions to the model](../../llm-api-production-101/en/02-tool-calling.md)

Tags: LLM, OpenAI, Prompt Engineering, Python
