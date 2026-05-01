---
title: 'Prompt and LLM chain — assembling your first chain'
series: langchain-101
episode: 2
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LangChain
- LCEL
- Python
- LLM
last_reviewed: '2026-05-01'
---

# Prompt and LLM chain — assembling your first chain

## Questions this post answers

- How do `system` and `human` messages divide responsibility in `ChatPromptTemplate`
- How should you model prompts that need multiple input variables
- When is `StrOutputParser` enough, and when do you need structured parsing
- How do you forward part of the input unchanged through a chain

> A prompt chain is not string concatenation with extra steps; it is a typed conversion from app inputs into model-ready messages.

![Questions this post answers](../../../assets/langchain-101/02/02-01-questions-this-post-answers.en.png)
## Minimal runnable example

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a tutor explaining concepts to {audience}."),
    ("human", "Explain {topic} in three sentences."),
])
chain = prompt | ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"]) | StrOutputParser()

print(chain.invoke({"audience": "junior backend engineers", "topic": "PromptTemplate"}))
```

```
Output
In the context of Dialogflow or similar conversational AI platforms, a PromptTemplate is a reusable template for generating custom conversation prompts. This template allows you to define a structure for your conversation prompts, enabling you to easily create and manage multiple prompts with varying parameters, such as user input or context information.

By utilizing a PromptTemplate, you can decouple the conversation flow logic from the actual prompt text, making it easier to maintain and update your conversational interface while ensuring consistency across different interactions.
```

## What to notice in this code

- Variables are managed at the template layer instead of through manual string assembly.
- The `system` message sets behavior while the `human` message carries the request.
- Adding a parser makes downstream steps deal with a plain string instead of an `AIMessage`.
- You can adjust prompt structure without rewriting the rest of the chain.

## Where engineers get confused

- `ChatPromptTemplate` is both a formatter and a message builder.
- Without an output parser, many examples return `AIMessage`, not text.
- `RunnablePassthrough` forwards the current input; it does not magically merge unrelated state.

## Checklist

- [ ] I can explain the roles of `system`, `human`, and `ai` messages
- [ ] I can build a prompt template with multiple variables
- [ ] I understand how the parser changes the chain's output type

LangChain 101 (2/6)

Example code: [github.com/yeongseon-books/langchain-101](https://github.com/yeongseon-books/langchain-101/tree/main/02-prompt-llm-chain)

## Questions this post answers

- How is `ChatPromptTemplate` different from plain string formatting?
- Why separate prompt, LLM, and output parser into distinct steps?
- What input shape should you keep when a chain has multiple variables?
- Where should fallbacks sit in a prompt-to-model pipeline?

> A prompt chain is the smallest useful LCEL pipeline: turn structured input into messages, call the model, then parse the result into an application-friendly output.

## The flow at a glance

![The flow at a glance](../../../assets/langchain-101/02/02-02-the-flow-at-a-glance.en.png)
Post 1 established the LCEL structure. This post builds on it with the patterns that appear most often in real code: multi-variable prompt templates, output parser selection, and passing values through a chain unchanged.

Topics:

- the message roles in `ChatPromptTemplate`
- building prompts with multiple variables
- choosing between `StrOutputParser` and `JsonOutputParser`
- using `RunnablePassthrough` to forward inputs unchanged
- testing a completed chain

---

## ChatPromptTemplate structure

`ChatPromptTemplate` constructs conversation-style prompts and renders them into the message format the LLM expects.

Three message roles are available:

- `system`: sets the model's behavior — persona, constraints, output format
- `human`: represents user input
- `ai`: represents previous assistant responses, used to inject conversation history in multi-turn setups

```python
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {language} expert. Explain things clearly and concisely."),
    ("human", "{question}"),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = prompt | llm

response = chain.invoke({
    "language": "Python",
    "question": "When is a list comprehension a better choice than a for loop?",
})

print(response.content)
```

```
Output
**Choosing Between List Comprehension and For Loop**

List comprehensions and for loops are both used to create lists in Python. However, there are situations where one is a better choice than the other.

**When to Use List Comprehension**

List comprehensions are a better choice than for loops in the following scenarios:

### 1. **Simple Transformations**

If you need to perform a simple transformation on each element of a list, list comprehensions are a good choice.

```python
numbers = [1, 2, 3, 4, 5]
double_numbers = [x * 2 for x in numbers]
print(double_numbers)  # [2, 4, 6, 8, 10]
```

### 2. **Filtering**

List comprehensions can be used to filter elements from a list.

```python
numbers = [1, 2, 3, 4, 5]
even_numbers = [x for x in numbers if x % 2 == 0]
print(even_numbers)  # [2, 4]
```

### 3. **Readability**

List comprehensions can make your code more readable by avoiding the need for a for loop and if statement.

```python
numbers = [1, 2, 3, 4, 5]
even_numbers = []
for x in numbers:
    if x % 2 == 0:
        even_numbers.append(x)
print(even_numbers)  # [2, 4]
```

### 4. **Performance**

List comprehensions are generally faster than for loops because they avoid the overhead of a function call.

**When to Use a For Loop**

For loops are a better choice than list comprehensions in the following scenarios:

### 1. **Complex Logic**

If you need to perform complex logic or multiple operations on each element of a list, a for loop is a better choice.

```python
numbers = [1, 2, 3, 4, 5]
result = []
for x in numbers:
    if x % 2 == 0:
        result.append(x * 2)
    else:
... (truncated)
```

Placeholder names like `{language}` and `{question}` must match the keys in the dict passed to `invoke()`.

---

## Prompts with multiple variables

More complex tasks need more template variables. Pass them all in the same dict.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a code review expert. "
        "Language: {language}. Review focus: {review_focus}.",
    ),
    ("human", "Review the following code:\n\n```{language}\n{code}\n```"),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = prompt | llm | StrOutputParser()

result = chain.invoke({
    "language": "python",
    "review_focus": "readability and error handling",
    "code": """
def read_file(path):
    f = open(path)
    return f.read()
""",
})

print(result)
```

---

## StrOutputParser vs JsonOutputParser

Output parsers convert the LLM response into the format you need.

**StrOutputParser**: extracts `AIMessage.content` as a plain string. This covers most use cases.

**JsonOutputParser**: prompts the model to output JSON and parses the result into a Python dict. The prompt must explicitly request JSON format.

```python
import os

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You output JSON only. Do not include any other text.",
    ),
    (
        "human",
        "Output information about {topic} in this JSON format:\n"
        '{{"name": "name", "description": "description", "use_case": "use case"}}',
    ),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = prompt | llm | JsonOutputParser()

result = chain.invoke({"topic": "FAISS"})

print(f"type: {type(result)}")
print(f"name: {result.get('name')}")
print(f"description: {result.get('description')}")
print(f"use_case: {result.get('use_case')}")
```

```
Output
type: <class 'dict'>
name: FAISS
description: Facebook AI Similarity Search (FAISS) is an open-source library for efficient similarity search and clustering of dense vectors. It is developed by the Facebook AI Research (FAIR) team.
use_case: FAISS is used in various applications including but not limited to: Similarity search and clustering of dense vectors, Product recommendations, Image and video search, Personalized advertising, and Anomaly detection.
```

If JSON parsing is unreliable, `with_structured_output()` is more robust. That method is covered in the llm-api-production-101 series.

---

## RunnablePassthrough — forwarding inputs unchanged

`RunnablePassthrough` passes its input through to the next step without modification. It becomes useful when one part of a chain needs data from a previous step that was not modified along the way.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the question using the provided document."),
    ("human", "Document: {context}\n\nQuestion: {question}"),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = prompt | llm | StrOutputParser()

result = chain.invoke({
    "context": "FAISS is a vector search library developed at Facebook AI Research.",
    "question": "Who developed FAISS?",
})

print(result)
```

```
Output
FAISS was developed at Facebook AI Research.
```

`RunnablePassthrough` appears most often when connecting a Retriever to a prompt. Post 3 shows that pattern in detail.

---

## Adding a fallback to a chain

`.with_fallbacks()` runs an alternative chain when the primary call fails.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("human", "{question}"),
])

primary_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

fallback_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

primary_chain = prompt | primary_llm | StrOutputParser()
fallback_chain = prompt | fallback_llm | StrOutputParser()

chain_with_fallback = primary_chain.with_fallbacks([fallback_chain])

result = chain_with_fallback.invoke({"question": "How does Python handle exceptions?"})
print(result)
```

```
Output
**Exception Handling in Python**
=====================================

Python provides a comprehensive exception handling mechanism that allows you to handle runtime errors and other exceptional conditions that may arise during the execution of your code. Here's an overview of how Python handles exceptions:

**Types of Exceptions**
------------------------

Python has two types of exceptions:

1. **Built-in Exceptions**: These are exceptions that are defined in the Python standard library. Examples include `ValueError`, `TypeError`, `RuntimeError`, etc.
2. **User-defined Exceptions**: These are exceptions that you can define yourself using the `class` keyword.

**Try-Except Block**
--------------------

The try-except block is the fundamental building block of exception handling in Python. It consists of two parts:

1. **Try Block**: This is the block of code that may raise an exception.
2. **Except Block**: This is the block of code that will be executed if an exception is raised in the try block.

Here's an example:
```python
try:
    # Code that may raise an exception
    x = 5 / 0
except ZeroDivisionError:
    # Code that will be executed if a ZeroDivisionError is raised
    print("Cannot divide by zero!")
```
**Multiple Except Blocks**
---------------------------

You can have multiple except blocks to handle different types of exceptions:
```python
try:
    # Code that may raise an exception
    x = 5 / 0
except ZeroDivisionError:
    # Code that will be executed if a ZeroDivisionError is raised
    print("Cannot divide by zero!")
except TypeError:
    # Code that will be executed if a TypeError is raised
    print("Invalid type!")
```
**Finally Block**
-----------------

The finally block is optional and is executed regardless of whether an exception was raised or not:
```python
try:
    # Code that may raise an exception
    x = 5 / 0
except ZeroDivisionError:
    # Code that will be executed if a ZeroDivisionError is raised
    print("Cannot divide by zero!")
finally:
    # Code that will be executed regardless of whether an exception was raised
    print("This will always be printed!")
```
... (truncated)
```

This pattern switches automatically to the fallback model when the primary model is unavailable or rate-limited.

---

## What to notice in this code

- Prompt chains usually take dictionaries as input, and the keys must line up with the variables used in the template.
- Choosing between `StrOutputParser` and `JsonOutputParser` is mostly about what downstream code expects to receive.
- `RunnablePassthrough` matters because it makes data flow explicit even when a value should remain unchanged.
- A fallback is not just defensive code. It is a second chain that preserves the same input and output contract when the primary path fails.

## Where engineers get confused

- If you treat a prompt template as plain string interpolation, you miss the value of role-separated chat messages.
- JSON parsing is only reliable when the prompt strongly constrains the schema the model should emit.
- Fallback chains become hard to debug if they return a different shape from the primary chain.

## Checklist

- [ ] I can build a dictionary input for a `ChatPromptTemplate` with multiple variables
- [ ] I know when `StrOutputParser` is enough and when structured parsing is worth the extra constraint
- [ ] I understand why fallback chains must preserve the same output shape

## Conclusion

You can now build prompt templates with multiple variables, select the right output parser for the job, and pass inputs unchanged when a chain step needs earlier data.

The next post connects a Retriever to a chain and uses retrieved document chunks as context for the LLM.

<!-- toc:begin -->
## In this series

- [LangChain introduction — LCEL and the Runnable interface](./01-lcel-runnable-basics.md)
- **Prompt and LLM chain — assembling your first chain (current)**
- Retriever — document search and context injection (upcoming)
- Tool calling — connecting external tools (upcoming)
- Streaming — handling real-time output (upcoming)
- Putting it together — a complete chain in one file (upcoming)

<!-- toc:end -->

---

## References

- [ChatPromptTemplate documentation](https://python.langchain.com/docs/modules/model_io/prompts/quick_start/)
- [Output parsers](https://python.langchain.com/docs/modules/model_io/output_parsers/)
- [RunnablePassthrough](https://python.langchain.com/docs/expression_language/primitives/passthrough/)

Tags: LangChain, LCEL, Python, LLM
