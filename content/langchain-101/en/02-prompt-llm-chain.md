---
title: "LangChain 101 (2/6): Prompt and LLM chain — assembling your first chain"
series: langchain-101
episode: 2
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
seo_description: A prompt chain is not string concatenation with extra steps; it is
  a typed conversion from app inputs into model-ready messages.
---

# LangChain 101 (2/6): Prompt and LLM chain — assembling your first chain

Once LCEL makes sense, the next question is where the real chain logic actually lives. In practice, that usually means prompt construction, output parsing, and the small input-shaping decisions that determine whether the rest of the pipeline stays readable.

This is the second post in the LangChain 101 series. It shows how prompt templates, parsers, and passthrough steps turn LCEL basics into a practical first chain.

![The flow at a glance](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/02/02-02-the-flow-at-a-glance.en.png)
*The flow at a glance*
> A prompt chain is not string concatenation with extra steps; it is a typed conversion from app inputs into model-ready messages.

## Questions to Keep in Mind

- How is ChatPromptTemplate different from plain string formatting?
- How do multiple prompt variables and parsers change chain input and output shapes?
- Which failures should fallback hide, and which failures should remain visible?

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

## ChatPromptTemplate structure

![System human ai message roles](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/02/02-01-chatprompttemplate-structure.en.png)

*System human ai message roles*
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

Placeholder names like `{language}` and `{question}` must match the keys in the dict passed to `invoke()`.

---

## Prompts with multiple variables

![Multiple variables into one prompt](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/02/02-02-prompts-with-multiple-variables.en.png)

*Multiple variables into one prompt*
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

![String parser and JSON parser outputs](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/02/02-03-stroutputparser-vs-jsonoutputparser.en.png)

*String parser and JSON parser outputs*
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

`RunnablePassthrough` appears most often when connecting a Retriever to a prompt. Post 3 shows that pattern in detail.

---

## Adding a fallback to a chain

![Primary failure and fallback switch](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/02/02-04-adding-a-fallback-to-a-chain.en.png)

*Primary failure and fallback switch*
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

## Answering the Opening Questions

- **How is ChatPromptTemplate different from plain string formatting?**
  ChatPromptTemplate builds role-aware messages, not just one formatted string, and keeps variable handling inside the chain boundary.

- **How do multiple prompt variables and parsers change chain input and output shapes?**
  Input becomes a dictionary with multiple keys, while the parser turns the model response object into a string, JSON value, or another application type.

- **Which failures should fallback hide, and which failures should remain visible?**
  Fallback can mask transient provider failures, but contract errors and parser failures should stay visible in logs.

<!-- toc:begin -->
## In this series

- [LangChain 101 (1/6): LangChain introduction — LCEL and the Runnable interface](./01-lcel-runnable-basics.md)
- **LangChain 101 (2/6): Prompt and LLM chain — assembling your first chain (current)**
- LangChain 101 (3/6): Retriever — document search and context injection (upcoming)
- LangChain 101 (4/6): Tool calling — connecting external tools (upcoming)
- LangChain 101 (5/6): Streaming — handling real-time output (upcoming)
- LangChain 101 (6/6): Putting it together — a complete chain in one file (upcoming)

<!-- toc:end -->

---

## References

- [ChatPromptTemplate documentation](https://python.langchain.com/docs/modules/model_io/prompts/quick_start/)
- [Output parsers](https://python.langchain.com/docs/modules/model_io/output_parsers/)
- [RunnablePassthrough](https://python.langchain.com/docs/expression_language/primitives/passthrough/)

Tags: LangChain, LCEL, Python, LLM
