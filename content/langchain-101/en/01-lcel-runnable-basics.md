---
title: "LangChain 101 (1/6): LangChain introduction — LCEL and the Runnable interface"
series: langchain-101
episode: 1
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LangChain
- LCEL
- Python
- LLM
last_reviewed: '2026-05-01'
seo_description: In LangChain, most components become interchangeable once their input
  and output shapes line up.
---

# LangChain 101 (1/6): LangChain introduction — LCEL and the Runnable interface

LangChain gets easier once you stop treating it as a pile of abstractions and start treating it as a pipeline library. Most real applications still do the same three things—shape input, call a model, and normalize output—and this post starts with the contract that makes those steps composable.

This is the first post in the LangChain 101 series. It explains LCEL and the Runnable interface as the execution model behind a basic LangChain pipeline.

![The flow at a glance](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/01/01-02-the-flow-at-a-glance.en.png)
*The flow at a glance*
> In LangChain, most components become interchangeable once their input and output shapes line up.

## Questions to Keep in Mind

- What common contract lets LCEL connect prompts, models, and parsers?
- What data shape moves through each step of `prompt | llm | parser`?
- When should the same chain use `invoke()`, `batch()`, or `stream()`?

## Minimal runnable example

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_template("Explain {topic} in one paragraph.")
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"])
chain = prompt | llm | StrOutputParser()

print(chain.invoke({"topic": "LCEL"}))
```

<!-- injected-output:start -->
**Output**

    LCEL, or LangChain Expression Language, is a declarative way to compose chains in LangChain by piping together components — such as prompts, chat models, output parsers, and retrievers — using the `|` operator. Every component in an LCEL chain implements the same Runnable interface, which means you can invoke, batch, or stream the whole chain with a single method call without writing glue code between steps. Because LCEL is just function composition over a shared contract, the resulting chains are easy to reason about, swap parts in and out of, and run efficiently in parallel or async contexts.

<!-- injected-output:end -->

## The problem LangChain addresses

![Repeated glue code and LCEL abstraction flow](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/01/01-01-the-problem-langchain-addresses.en.png)

*Repeated glue code and LCEL abstraction flow*
LLM application code develops a recurring pattern: assemble a prompt, call the model, parse the output, pass it to the next step. The plumbing between those steps accumulates.

```python
# typical accumulation of glue code
prompt_text = f"Summarize this text: {user_input}"
response = client.chat.completions.create(model="...", messages=[{"role": "user", "content": prompt_text}])
raw_output = response.choices[0].message.content
parsed = raw_output.strip()
next_prompt = f"Translate this summary: {parsed}"
# ...repeats
```

LangChain abstracts that glue code into components. The core insight is simple: if every component implements the same interface, components can be connected like pipe fittings.

---

## The Runnable interface

![Invoke batch stream execution modes](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/01/01-02-the-runnable-interface.en.png)

*Invoke batch stream execution modes*
Almost every LangChain component implements the Runnable interface. Three methods are essential.

- `invoke(input)` — accepts one input, returns one output. Synchronous.
- `batch(inputs)` — accepts a list of inputs, returns a list of outputs.
- `stream(input)` — yields output incrementally, token by token.

The consistency of this interface makes every component substitutable and composable.

```python
import os

from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

response = llm.invoke("Explain the advantages of Python in two sentences.")
print(response.content)
```

<!-- injected-output:start -->
**Output**

    Python is a versatile and widely-used programming language that offers several advantages, including its simplicity, readability, and ease of use, making it an ideal choice for beginners and experienced developers alike. Additionally, Python's extensive libraries and frameworks, such as NumPy, pandas, and Django, provide a powerful toolset for data analysis, machine learning, web development, and more.

<!-- injected-output:end -->

`ChatGroq` implements Runnable, so `invoke()` is available directly.

---

## LCEL and the pipe operator

![Prompt model parser type flow](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/01/01-03-lcel-and-the-pipe-operator.en.png)

*Prompt model parser type flow*
LCEL uses `|` to connect Runnable components. The output of the left component becomes the input of the right component.

```python
chain = component_a | component_b | component_c
result = chain.invoke(input)
```

This is the most common pattern in LangChain code. A concrete example:

```bash
pip install langchain langchain-groq
```

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert at concise explanations."),
    ("human", "Explain {topic} in two sentences."),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

parser = StrOutputParser()

chain = prompt | llm | parser

result = chain.invoke({"topic": "embedding vectors"})
print(result)
```

<!-- injected-output:start -->
**Output**

    Embedding vectors is a technique in natural language processing and machine learning where high-dimensional data is represented as dense, fixed-size vectors in a lower-dimensional space, allowing for efficient computation and improved model performance. This is typically achieved through techniques like word2vec or GloVe, which map words or other inputs to vectors in a way that captures semantic relationships and word meanings.

<!-- injected-output:end -->

What each component does:

**`ChatPromptTemplate`**: receives a dict, returns a list of messages with `{topic}` filled in.

**`ChatGroq`**: receives the message list, returns an `AIMessage` object.

**`StrOutputParser`**: receives an `AIMessage`, returns its `.content` string.

The pipe operator composes these three steps into one chain. `chain.invoke({"topic": "embedding vectors"})` runs all three in order.

---

## Running each component individually

Seeing each step in isolation makes the data flow concrete.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert at concise explanations."),
    ("human", "Explain {topic} in two sentences."),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

parser = StrOutputParser()

# step 1: render the prompt
messages = prompt.invoke({"topic": "embedding vectors"})
print("=== step 1: messages ===")
for m in messages.messages:
    print(f"  [{m.type}] {m.content}")

# step 2: call the LLM
ai_message = llm.invoke(messages)
print(f"\n=== step 2: AIMessage ===")
print(f"  type: {type(ai_message).__name__}")
print(f"  content: {ai_message.content[:80]}...")

# step 3: parse to string
text = parser.invoke(ai_message)
print(f"\n=== step 3: string ===")
print(f"  {text}")
```

<!-- injected-output:start -->
**Output**

    === step 1: messages ===
      [system] You are an expert at concise explanations.
      [human] Explain embedding vectors in two sentences.

    === step 2: AIMessage ===
      type: AIMessage
      content: Embedding vectors is a technique in natural language processing (NLP) where word...

    === step 3: string ===
      Embedding vectors is a technique in natural language processing (NLP) where words or phrases are represented as numerical vectors in a high-dimensional space, allowing machines to capture semantic relationships and nuances between them. These vectors are often learned through neural networks, where similar words are mapped to nearby points in the vector space, enabling tasks like text classification, sentiment analysis, and language translation.

<!-- injected-output:end -->

---

## RunnableLambda — wrapping a plain function

To insert a custom Python function into a pipe chain, use `RunnableLambda`.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("human", "Summarize {text} in one sentence."),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

def add_char_count(text: str) -> str:
    return f"{text}\n\n(character count: {len(text)})"

chain = prompt | llm | StrOutputParser() | RunnableLambda(add_char_count)

result = chain.invoke({
    "text": "Vector search converts text into numeric vectors for meaning-based retrieval."
})
print(result)
```

<!-- injected-output:start -->
**Output**

    Vector search converts text into numeric vectors, allowing for efficient and meaningful retrieval by comparing the semantic similarity between text inputs.

    (character count: 155)

<!-- injected-output:end -->

`RunnableLambda` lets any plain Python function participate in a pipe chain. It is useful for output post-processing, logging, and lightweight transforms.

---

## batch() for multiple inputs

![Batch fan out and collect flow](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/01/01-04-batch-for-multiple-inputs.en.png)

*Batch fan out and collect flow*
`batch()` accepts a list of inputs and returns a list of outputs.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("human", "Explain {topic} in one sentence."),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = prompt | llm | StrOutputParser()

topics = [
    {"topic": "embeddings"},
    {"topic": "FAISS"},
    {"topic": "RAG"},
]

results = chain.batch(topics)

for topic_dict, result in zip(topics, results):
    print(f"[{topic_dict['topic']}] {result}\n")
```

<!-- injected-output:start -->
**Output**

    [embeddings] In machine learning and natural language processing, embeddings are a way of representing words, phrases, or other data as numerical vectors in a high-dimensional space, allowing similar concepts to be clustered together and enabling models to capture nuanced relationships and patterns.

    [FAISS] FAISS (Facebook AI Similarity Search) is an open-source library developed by Facebook and Carnegie Mellon University for efficient similarity search and clustering of dense vectors, typically used in large-scale machine learning and data analytics applications.

    [RAG] RAG stands for Red, Amber, and Green, which is a traffic-light system used to categorize and track project progress, risks, and issues, with Red indicating critical problems, Amber signifying potential issues, and Green denoting successful completion or progress.

<!-- injected-output:end -->

`batch()` attempts parallel processing internally. Use `max_concurrency` to cap simultaneous requests when working within API rate limits.

```python
results = chain.batch(topics, config={"max_concurrency": 2})
```

---

## What to notice in this code

- `prompt | llm | parser` is not string piping. It is composition based on compatible Runnable input and output types.
- `ChatPromptTemplate` returns message objects, and `ChatGroq` consumes those objects directly without extra glue code.
- `StrOutputParser` is what turns an `AIMessage` into a plain string that the rest of your application can use easily.
- `batch()` does not require a different chain design. It reuses the same pipeline with multiple inputs.

## Where engineers get confused

- LCEL looks like the main abstraction, but the real foundation is the Runnable contract underneath it.
- The output type changes at each stage: prompt output is messages, model output is `AIMessage`, parser output is text.
- `RunnableLambda` is useful, but long business logic inside the chain can make the pipeline harder to reason about.

## Checklist

- [ ] I can explain the input and output type of `ChatPromptTemplate`, `ChatGroq`, and `StrOutputParser`
- [ ] I can run the same chain with both `invoke()` and `batch()`
- [ ] I understand when a plain Python function should be wrapped with `RunnableLambda`

## Conclusion

LCEL and the Runnable interface reduce LLM application plumbing to a sequence of composable components connected by `|`. Every component exposes `invoke`, `batch`, and `stream` consistently, so any component can replace any other component that accepts the same input type.

The next post goes deeper into `ChatPromptTemplate` and builds a more realistic chain with system messages, conditional formatting, and output parsing variants.

## Answering the Opening Questions

- **What common contract lets LCEL connect prompts, models, and parsers?**
  LCEL treats each component as a Runnable and composes steps whose input and output shapes line up.

- **What data shape moves through each step of `prompt | llm | parser`?**
  The prompt turns a dictionary into messages, the model returns an AIMessage, and the parser normalizes that into an application-friendly value.

- **When should the same chain use `invoke()`, `batch()`, or `stream()`?**
  Use `invoke()` for one request, `batch()` for many inputs through the same chain, and `stream()` when the user should see partial output.

<!-- toc:begin -->
## In this series

- **LangChain 101 (1/6): LangChain introduction — LCEL and the Runnable interface (current)**
- LangChain 101 (2/6): Prompt and LLM chain — assembling your first chain (upcoming)
- LangChain 101 (3/6): Retriever — document search and context injection (upcoming)
- LangChain 101 (4/6): Tool calling — connecting external tools (upcoming)
- LangChain 101 (5/6): Streaming — handling real-time output (upcoming)
- LangChain 101 (6/6): Putting it together — a complete chain in one file (upcoming)

<!-- toc:end -->

---

## References

- [LangChain LCEL documentation](https://python.langchain.com/docs/expression_language/)
- [Runnable interface](https://python.langchain.com/docs/expression_language/interface/)
- [ChatGroq integration](https://python.langchain.com/docs/integrations/chat/groq/)
- [langchain-groq on PyPI](https://pypi.org/project/langchain-groq/)

### Related Series

- [LangGraph 101](../../langgraph-101/en/01-graph-basics.md) — builds graph-based agent state machines on top of the Runnable and LCEL primitives this series teaches. Move there once a single chain is no longer enough and you need multi-step flows with branching or loops.

Tags: LangChain, LCEL, Python, LLM
