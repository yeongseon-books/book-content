---
title: 'Workflow automation — designing multi-step chains'
series: ai-app-patterns-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- RAG
- Agent
- Python
last_reviewed: '2026-05-01'
---

# Workflow automation — designing multi-step chains

## Questions this post answers

- How should intermediate outputs be structured when several LLM stages are chained together?
- Where should a summary → classification → tagging workflow detect and surface failure?
- In what situations is a fixed workflow better than an agent?

> Workflow automation removes model choice and replaces it with a pipeline that follows human-defined stages and data contracts.

![Questions this post answers](../../../assets/ai-app-patterns-101/05/05-01-questions-this-post-answers.en.png)
> AI App Patterns 101 (5/6)

Example code: [github.com/yeongseon-books/ai-app-patterns-101](https://github.com/yeongseon-books/ai-app-patterns-101/tree/main/en/05-workflow-automation)

Some tasks resist a single LLM call. Receiving a customer inquiry, classifying it, applying category-specific logic, then generating a response is one example. Workflow automation connects these stages into a coherent pipeline using LangChain LCEL.

Topics:

- building sequential chains
- routing — branching based on intermediate output
- a practical multi-stage code review pipeline
- passing each stage's output cleanly to the next

---

## Sequential chains

LCEL's `|` operator connects stages: the left stage's output becomes the right stage's input.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

translate_prompt = ChatPromptTemplate.from_messages([
    ("system", "Translate the following text to {target_language}. Return only the translation."),
    ("human", "{text}"),
])

summarize_prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize the following text in two sentences."),
    ("human", "{text}"),
])

title_prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate a one-line title for the following text."),
    ("human", "{text}"),
])

str_parser = StrOutputParser()

def make_pipeline(target_language: str):
    """Return translate → summarize → title functions for the given language."""

    def translate(inputs: dict) -> dict:
        translated = (translate_prompt | llm | str_parser).invoke({
            "text": inputs["text"],
            "target_language": target_language,
        })
        return {"text": translated}

    def summarize(inputs: dict) -> dict:
        summary = (summarize_prompt | llm | str_parser).invoke(inputs)
        return {"text": summary}

    def make_title(inputs: dict) -> str:
        return (title_prompt | llm | str_parser).invoke(inputs)

    return translate, summarize, make_title

article = """
Artificial intelligence is transforming the way businesses operate.
Companies across industries are adopting AI tools to automate repetitive tasks,
improve decision-making, and personalize customer experiences.
The healthcare sector uses AI to assist in diagnosis and drug discovery.
In finance, AI powers fraud detection and algorithmic trading.
As AI becomes more capable, organizations must also address ethical considerations
such as bias, transparency, and data privacy.
"""

translate_fn, summarize_fn, title_fn = make_pipeline("Korean")

step1 = translate_fn({"text": article})
print(f"translation:\n{step1['text']}\n")

step2 = summarize_fn(step1)
print(f"summary:\n{step2['text']}\n")

step3 = title_fn(step2)
print(f"title: {step3}")
```

~~~
Output
translation:
인공지능이 기업의 운영 방식을 변화시키고 있습니다.
산업 분야의 모든 회사들이 반복적인 업무를 자동화하고, 의사 결정을 개선하고, 고객의 개인화된 경험을 제공하기 위해 인공지능 도구를 채택하고 있습니다.
의료 분야에서는 인공지능이 진단 및 약물 개발을 도와주고 있습니다.
금융 분야에서는 인공지능이 사기 감지를 지원하고 알고리즘 거래를 동작시킵니다.
인공지능이 더 능동적으로 될수록, 기관들은 편향성, 투명성 및 데이터 프라이버시와 같은 эти적 고려사항에 대처해야 합니다.

summary:
인공지능은 기업의 운영 방식을 변화시켜가며, 산업 분야의 모든 회사들이 업무를 자동화하고 고객의 개인화된 경험을 제공하기 위해 인공지능 도구를 채택하고 있습니다. 그러나 인공지능이 더 능동적으로 변할수록, 기관들은 편향성, 투명성 및 데이터 프라이버시와 같은 эти적 고려사항에 대한 대응이 필요해지고 있습니다.

title: "인공지능의 성장: 기업의 새로운 도전과 도전"
~~~

---

## Routing — branching based on classification

Classify the input first, then route it to the appropriate chain. The classifier's output is the only dependency between the two stages.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)
str_parser = StrOutputParser()

classify_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Classify the following customer inquiry.\n"
        "Categories: BILLING, TECHNICAL, GENERAL\n"
        "Return the category name only. No other text.",
    ),
    ("human", "{inquiry}"),
])
classify_chain = classify_prompt | llm | str_parser

billing_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a billing specialist.\n"
        "Handle refunds, invoices, and charge-related inquiries.\n"
        "Be accurate and reassuring.",
    ),
    ("human", "{inquiry}"),
])

technical_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a technical support engineer.\n"
        "Handle bugs, errors, and how-to questions.\n"
        "Guide users step by step.",
    ),
    ("human", "{inquiry}"),
])

general_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a customer service representative.\n"
        "Handle general inquiries politely and helpfully.",
    ),
    ("human", "{inquiry}"),
])

billing_chain = billing_prompt | llm | str_parser
technical_chain = technical_prompt | llm | str_parser
general_chain = general_prompt | llm | str_parser

def route_and_respond(inquiry: str) -> dict:
    """Classify → route → generate specialist response."""
    category = classify_chain.invoke({"inquiry": inquiry}).strip().upper()

    chains = {
        "BILLING": billing_chain,
        "TECHNICAL": technical_chain,
        "GENERAL": general_chain,
    }
    chain = chains.get(category, general_chain)
    response = chain.invoke({"inquiry": inquiry})

    return {"category": category, "response": response}

test_inquiries = [
    "My bill doubled this month without any explanation. Please check.",
    "The app keeps crashing when I open it. What should I do?",
    "What are your business hours?",
]

for inquiry in test_inquiries:
    print(f"\ninquiry: {inquiry}")
    result = route_and_respond(inquiry)
    print(f"category: {result['category']}")
    print(f"response: {result['response']}")
```

~~~
Output

inquiry: My bill doubled this month without any explanation. Please check.
category: BILLING
response: I'd be happy to help you with that. Can you please provide me with some details so I can look into this for you?

Could you please provide your account number or the last 4 digits of your account number? This will help me to access your account information.

Additionally, can you tell me what services you have with us (e.g. phone, internet, streaming, etc.)? And have you received any previous invoices or statements that show your bill normally being a certain amount?

Lastly, have you made any changes to your account recently, such as adding or removing services, or paying an outstanding balance?

inquiry: The app keeps crashing when I open it. What should I do?
category: TECHNICAL
response: Crashes can be frustrating. Let's troubleshoot the issue step by step. Here's a possible solution:

**Step 1: Close the app and restart your device**

Try closing the app completely and then restart your device. This can sometimes resolve the issue.

1. Double-tap the Home button (or swipe up from the bottom on some devices) to bring up the app switcher.
2. Swipe left or right to find the app that's crashing.
3. Swipe up on the app to close it.
4. Restart your device.

**Step 2: Check for updates**

Ensure your app is updated to the latest version.

1. Open the App Store (on iOS) or Google Play Store (on Android).
2. Search for the app that's crashing.
3. Check if an update is available.
4. If there's an update, download and install it.

**Step 3: Clear app data and cache**

Clearing the app's data and cache can resolve issues caused by corrupted data.

1. Go to your device's Settings.
2. Navigate to Apps (or App Manager).
3. Find the app that's crashing.
4. Tap on Storage (or Clear data).
5. Select Clear cache and Clear data (if available).
6. Restart your device.

**Step 4: Uninstall and reinstall the app**

If the above steps don't work, try uninstalling and reinstalling the app.

1. Go to your device's Settings.
2. Navigate to Apps (or App Manager).
3. Find the app that's crashing.
4. Tap on Uninstall.
5. Wait for the app to uninstall.
6. Open the App Store (on iOS) or Google Play Store (on Android).
7. Search for the app.
8. Tap the Install button.

If none of these steps resolve the issue, please provide more details about the crash, such as:

* The error message you see
... (truncated)
~~~

---

## Multi-stage data transformation pipeline

Each stage transforms the previous stage's output. The code review pipeline below shows three chained transformations: analysis → suggestions → report.

```python
import os

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

analyze_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Analyze the following code and return JSON only.\n"
        'Format: {{"language": "lang", "purpose": "purpose", "issues": ["issue list"], "score": 1-10}}',
    ),
    ("human", "Code:\n{code}"),
])

suggest_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Based on the code analysis, provide specific improvements.\n"
        "Include corrected code examples for each issue.",
    ),
    ("human", "Analysis:\n{analysis}\n\nOriginal code:\n{code}"),
])

report_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Summarize the code review into a concise report.\n"
        "Structure: overall assessment, key improvements, recommended actions.",
    ),
    ("human", "Analysis:\n{analysis}\n\nSuggestions:\n{suggestions}"),
])

analyze_chain = analyze_prompt | llm | JsonOutputParser()
suggest_chain = suggest_prompt | llm | StrOutputParser()
report_chain = report_prompt | llm | StrOutputParser()

def code_review_pipeline(code: str) -> dict:
    """Code analysis → suggestions → report."""
    analysis = analyze_chain.invoke({"code": code})
    print(f"  analysis done: score {analysis.get('score')}/10, {len(analysis.get('issues', []))} issues")

    suggestions = suggest_chain.invoke({
        "analysis": str(analysis),
        "code": code,
    })
    print("  suggestions done")

    report = report_chain.invoke({
        "analysis": str(analysis),
        "suggestions": suggestions,
    })
    print("  report done")

    return {"analysis": analysis, "suggestions": suggestions, "report": report}

sample_code = """
def get_user(id):
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {id}")
    result = cursor.fetchone()
    conn.close()
    return result
"""

print("running code review pipeline...")
result = code_review_pipeline(sample_code)
print(f"\n=== final report ===\n{result['report']}")
```python
def get_user(id):
    try:
        import sqlite3
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Validate the user ID
        if not isinstance(id, int) or id < 1:
            raise ValueError("Invalid user ID")
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
        result = cursor.fetchone()
    except sqlite3.Error as e:
        # Handle the SQLite error
        print(f"Error: {e}")
    except ValueError as e:
        # Handle the invalid user ID
        print(f"Error: {e}")
    except Exception as e:
        # Handle any other exceptions
        print(f"Error: {e}")
    finally:
        # Close the database connection
        if conn:
            conn.close()
    return result
```
```

---

## What to notice in this code

- `main.py` breaks the same support ticket into three sequential stages: summarization, category classification, and tag suggestion.
- Every stage returns a `dict`, which makes intermediate outputs easy to log, inspect, or persist.
- This structure is friendly to operational controls such as approval, routing, and retry policies.

---

## Where engineers get confused

- More stages are not automatically better; every extra call adds cost, latency, and another failure surface.
- Passing only raw strings between stages makes later validation and branching harder than passing structured dictionaries.
- The real line between a workflow and an agent is not tool usage but whether the execution path changes at runtime.

---

## Checklist

- [ ] The summary output feeds the next stage
- [ ] The classifier returns one value from a limited category set
- [ ] The tagging step uses earlier stage results, not only the raw text
- [ ] The final output is a structured object that still contains intermediate artifacts

---

## Conclusion

Keep each stage focused on one responsibility. A stage that does too much is hard to test, hard to debug, and hard to replace. When a stage's output is ambiguous — a free-form string where structured data was expected — the next stage often fails silently. Define the output format for every stage, validate it, and only then pass it forward.

The final post covers human-in-the-loop design: inserting human review and approval gates into otherwise automated pipelines.

<!-- toc:begin -->
## In this series

- [Chatbot pattern — managing conversation history and state](./01-chatbot-pattern.md)
- [RAG Q&A pattern — document-based question answering](./02-rag-qa-pattern.md)
- [Document assistant — summarization, extraction, classification](./03-document-assistant.md)
- [Agent and tool pattern — autonomous tool selection](./04-agent-tool-pattern.md)
- **Workflow automation — designing multi-step chains (current)**
- Human-in-the-loop — designing for human intervention (upcoming)

<!-- toc:end -->

---

## References

- [LangChain LCEL](https://python.langchain.com/docs/expression_language/)
- [LangChain routing](https://python.langchain.com/docs/expression_language/how_to/routing/)
- [RunnableParallel](https://python.langchain.com/docs/expression_language/primitives/parallel/)

Tags: LLM, RAG, Agent, Python
