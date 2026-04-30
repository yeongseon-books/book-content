# LangChain introduction — LCEL and the Runnable interface

> LangChain 101 (1/6)

LangChain throws a lot of terminology at you before the code makes sense: LCEL, Runnable, Chain, Pipe. This post cuts through that by focusing on what LCEL (LangChain Expression Language) and the Runnable interface actually are and why the library is structured around them.

This series covers LangChain as an API — how to use its components. Application-level patterns such as chatbots, RAG, and agents are in a separate series (ai-app-patterns-101).

Topics:

- the problem LangChain addresses
- the Runnable interface: `invoke()`, `batch()`, `stream()`
- building a chain with the LCEL pipe operator `|`
- running the simplest possible chain
- why this structure is worth learning

---

## The problem LangChain addresses

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

`ChatGroq` implements Runnable, so `invoke()` is available directly.

---

## LCEL and the pipe operator

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

`RunnableLambda` lets any plain Python function participate in a pipe chain. It is useful for output post-processing, logging, and lightweight transforms.

---

## batch() for multiple inputs

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

`batch()` attempts parallel processing internally. Use `max_concurrency` to cap simultaneous requests when working within API rate limits.

```python
results = chain.batch(topics, config={"max_concurrency": 2})
```

---

## Conclusion

LCEL and the Runnable interface reduce LLM application plumbing to a sequence of composable components connected by `|`. Every component exposes `invoke`, `batch`, and `stream` consistently, so any component can replace any other component that accepts the same input type.

The next post goes deeper into `ChatPromptTemplate` and builds a more realistic chain with system messages, conditional formatting, and output parsing variants.

<!-- toc:begin -->
## In this series

- **LangChain introduction — LCEL and the Runnable interface (current)**
- Prompt and LLM chain — assembling your first chain (upcoming)
- Retriever — document search and context injection (upcoming)
- Tool calling — connecting external tools (upcoming)
- Streaming — handling real-time output (upcoming)
- Putting it together — a complete chain in one file (upcoming)

<!-- toc:end -->

---

## References

- [LangChain LCEL documentation](https://python.langchain.com/docs/expression_language/)
- [Runnable interface](https://python.langchain.com/docs/expression_language/interface/)
- [ChatGroq integration](https://python.langchain.com/docs/integrations/chat/groq/)
- [langchain-groq on PyPI](https://pypi.org/project/langchain-groq/)

Tags: LangChain, LCEL, Python, LLM
