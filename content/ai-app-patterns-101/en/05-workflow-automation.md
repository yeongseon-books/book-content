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

```
Output
translation:
인공 지능이 기업의 운영 방식을 혁신하고 있습니다. 

산업 분야의 회사들이 반복적인 작업을 자동화하고, 의사 결정을 향상하고, 고객 경험을 개인화하기 위해 인공 지능 도구를 채택하고 있습니다.

의료 분야에서는 인공 지능이 진단과 약물 발견에 도움을 주고 있습니다. 

금융 분야에서는 인공 지능이 위조 탐지와 알고리즘 거래를 구동하고 있습니다. 

인공 지능이 더 능력을 얻을수록, 조직은 편견, 투명성, 데이터 개인 정보와 같은 윤리적 고려를 해결해야 합니다.

summary:
인공 지능은 기업의 운영 방식을 혁신하고 있으며, 산업 분야에서 반복적인 작업을 자동화하고 고객 경험을 개인화하는 데 사용되고 있습니다. 의료, 금융 분야에서도 인공 지능이 진단과 약물 발견, 위조 탐지, 알고리즘 거래 등에 도움을 주고 있지만, 더 높은 능력으로 인해 윤리적 고려 사항이 더욱 중요한 주제로 떠오르고 있습니다.

title: "인공 지능의 혁신적인 가능성과 윤리적 고려"
```

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

```
Output

inquiry: My bill doubled this month without any explanation. Please check.
category: BILLING
response: I'm here to help you understand your bill. I'll review the details and provide a clear explanation.

To assist me, could you please provide the following information:

1. Your account number or the last 4 digits of your account number.
2. The date of the current bill you received.
3. The original amount of your previous bill.
4. Any additional services you've added or changes to your plan recently.

With this information, I'll investigate further and provide you with a detailed explanation for the increase in your bill. If there's an error or issue, we'll work together to correct it and get your bill back to the correct amount.

Also, please note that if you've already made any payments on this bill, we'll process a refund promptly if the issue is resolved in your favor.

Is there anything else you'd like to share about your account or the bill in question?

inquiry: The app keeps crashing when I open it. What should I do?
category: TECHNICAL
response: Sorry to hear that the app is crashing. Let's troubleshoot the issue step by step. Here are some possible solutions:

**Step 1: Close and Reopen the App**

1. Close the app by swiping it away from the task list (on Android devices) or by double-tapping the Home button to find the app and swipe it away (on iOS devices).
2. Wait for a few seconds and then reopen the app.
3. If the app still crashes, proceed to the next step.

**Step 2: Restart Your Device**

1. Restart your device by pressing and holding the Power button until the shutdown menu appears.
2. Tap "Restart" or "Power off" to restart your device.
3. Wait for your device to fully boot up and then reopen the app.

**Step 3: Clear App Data and Cache**

1. Go to your device's Settings app.
2. Find the app that's crashing and select it.
3. Look for the "Storage" or "App info" option and select it.
4. Tap "Clear cache" and "Clear data" (be cautious when clearing data, as it may remove app settings and progress).
5. Wait for the cache to be cleared and then reopen the app.

**Step 4: Update the App**

1. Check the Google Play Store (for Android devices) or the Apple App Store (for iOS devices) for any available updates for the app.
2. If an update is available, download and install it.
3. Wait for the update to complete and then reopen the app.

**Step 5: Uninstall and Reinstall the App**

1. Go to your device's Settings app and find the app that's crashing.
2. Select the app and choose "Uninstall" or "Delete".
3. Wait for the app to be fully uninstalled.
4. Open the Google Play Store (for Android devices) or the Apple App Store (for iOS devices) and reinstall the app.
5. Wait for the app to fully install and then reopen it.

If none of these steps resolve the issue, please provide more information about the error message you're seeing or any other symptoms you're experiencing. This will help me better understand the problem and provide a more tailored solution.

inquiry: What are your business hours?
category: GENERAL
... (truncated)
```

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
```

```
Output
running code review pipeline...
  analysis done: score 4/10, 5 issues
  suggestions done
  report done

=== final report ===
**Overall Assessment:**
The code review reveals several issues with the current implementation, including SQL injection vulnerability, lack of error handling for SQLite connection errors, no error handling for SELECT statement errors, no validation for user ID, and database connection not being closed in a finally block. These issues can lead to security vulnerabilities, data loss, and other problems.

**Key Improvements:**

1.  **Use a parameterized query to prevent SQL injection**: Use a parameterized query instead of string formatting to insert user IDs into the SQL query.
2.  **Implement try-except blocks for error handling**: Wrap the code in try-except blocks to catch and handle SQLite connection errors, SELECT statement errors, and other exceptions.
3.  **Validate user IDs**: Add a check to ensure that the user ID is a valid integer.
4.  **Close the database connection in a finally block**: Close the database connection in a finally block to ensure it is always closed, even if an exception occurs.

**Recommended Actions:**

1.  **Implement the corrected code**: Apply the suggested improvements to the original code to address the identified issues.
2.  **Test the corrected code**: Thoroughly test the corrected code to ensure it works as expected and handles errors correctly.
3.  **Continuously monitor and maintain the code**: Regularly review and update the code to ensure it remains secure, efficient, and reliable.

Corrected Code:
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
