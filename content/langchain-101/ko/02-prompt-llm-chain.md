---
title: 'Prompt와 LLM Chain — 체인 첫 번째 구성'
series: langchain-101
episode: 2
language: ko
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

# Prompt와 LLM Chain — 체인 첫 번째 구성

## 이 글에서 답할 질문

- `ChatPromptTemplate`에서 `system`과 `human` 메시지는 어떻게 역할이 갈리는가
- 여러 입력 변수를 프롬프트에 안전하게 넣으려면 어떻게 구성해야 하는가
- `StrOutputParser`와 구조화된 파서의 선택 기준은 무엇인가
- 입력값 일부를 그대로 다음 단계로 넘기려면 어떤 Runnable이 필요한가

> Prompt chain은 문자열을 만드는 코드가 아니라 입력 구조를 메시지 구조로 바꾸는 작은 변환 파이프입니다.

![이 글에서 답할 질문](../../../assets/langchain-101/02/02-01-questions-this-post-answers.ko.png)
## 최소 실행 예제

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 {audience}에게 설명하는 튜터입니다."),
    ("human", "{topic}을 세 문장으로 설명해 주세요."),
])
chain = prompt | ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"]) | StrOutputParser()

print(chain.invoke({"audience": "주니어 백엔드 개발자", "topic": "PromptTemplate"}))
```

~~~
출력 결과
PromptTemplate은 미리 정의된 템플릿을 사용하여 사용자의 입력을 보다 유연하고 보다 쉽게 처리할 수 있도록 도와주는 도구입니다. 사용자가 입력 형식을 미리 지정하기만 하면, PromptTemplate은 해당 템플릿에 따라 입력을 처리하여 개발자의 코드를 간소화하고 가독성을 향상시킵니다.

PromptTemplate은 유사한 입력을 처리하는 코드를 여러 번 작성할 필요가 없도록 해주며, 또한 일관된 입력 형식을 유지하기 위해 도와줍니다. 이를 통해 개발자는 더 많은 시간과 노력을 투자하여 제품의 기능을 개선할 수 있습니다.
~~~

## 이 코드에서 봐야 할 것

- 프롬프트 변수는 문자열 이어붙이기 대신 템플릿 단계에서 관리됩니다.
- `system` 메시지는 말투와 제약을 잡고 `human` 메시지는 실제 질문을 담습니다.
- 파서를 마지막에 붙이면 이후 단계가 항상 문자열을 받는다고 가정할 수 있습니다.
- 프롬프트 수정과 모델 교체가 체인 바깥 코드에 거의 영향을 주지 않습니다.

## 실무에서 헷갈리는 지점

- PromptTemplate은 문자열 포매터이면서 동시에 메시지 구조 생성기입니다.
- 출력 파서를 붙이지 않으면 결과가 `AIMessage`라서 후속 단계 타입이 달라집니다.
- `RunnablePassthrough`는 값을 복사하는 도구가 아니라 현재 입력을 그대로 전달하는 연결점입니다.

## 체크리스트

- [ ] `system`, `human`, `ai` 메시지 역할 차이를 설명할 수 있다
- [ ] 여러 변수로 PromptTemplate을 만들고 실행할 수 있다
- [ ] 파서를 붙였을 때와 붙이지 않았을 때 출력 타입 차이를 이해한다

LangChain 101 시리즈 (2/6)

예제 코드: [github.com/yeongseon-books/langchain-101](https://github.com/yeongseon-books/langchain-101/tree/main/02-prompt-llm-chain)

## 이 글에서 답할 질문

- `ChatPromptTemplate`은 문자열 포맷팅과 무엇이 다를까
- Prompt, LLM, OutputParser를 왜 세 단계로 나누는 걸까
- 여러 입력 변수를 체인에 넣을 때 어떤 형태를 유지해야 할까
- fallback을 붙일 때 체인 경계는 어디로 잡아야 할까

> Prompt chain은 입력 딕셔너리를 프롬프트로 렌더링하고, 모델 호출 결과를 파싱해 애플리케이션이 쓰기 좋은 출력으로 바꾸는 가장 기본적인 LCEL 조립입니다.

## 핵심 흐름 한눈에 보기

![핵심 흐름 한눈에 보기](../../../assets/langchain-101/02/02-02-the-flow-at-a-glance.ko.png)
지난 글에서 LCEL의 기본 구조를 잡았다면, 이번 글에서는 실제로 자주 쓰는 패턴을 하나씩 만들어 봅니다. `ChatPromptTemplate`을 깊이 이해하고, 출력 파서를 선택하고, 체인에 변수를 넣는 방법을 다룹니다.

이번 글에서 다룰 내용은 다음과 같습니다.

- `ChatPromptTemplate`의 메시지 역할과 포맷
- 여러 변수를 가진 프롬프트 만들기
- `StrOutputParser`, `JsonOutputParser` 선택하기
- `RunnablePassthrough`로 입력을 그대로 넘기기
- 완성된 체인 테스트하기

---

## ChatPromptTemplate 구조

`ChatPromptTemplate`은 대화 형식의 프롬프트를 만드는 클래스입니다. 메시지 목록을 받아 LLM에 전달할 형식으로 렌더링합니다.

세 가지 메시지 역할이 있습니다.

- `system`: 모델의 행동 방식을 지정합니다. 페르소나, 제약, 출력 형식 등을 씁니다.
- `human`: 사용자 입력입니다.
- `ai`: 이전 어시스턴트 응답입니다. 멀티턴 시 이력을 넣을 때 씁니다.

```python
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 {language} 전문가입니다. 명확하고 간결하게 설명합니다."),
    ("human", "{question}"),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = prompt | llm

response = chain.invoke({
    "language": "파이썬",
    "question": "리스트 컴프리헨션은 언제 쓰는 게 좋나요?",
})

print(response.content)
```

~~~
출력 결과
리스트 컴프리헨션은 리스트를 생성하는 데 사용하는 파이썬의 고급 문법입니다. 리스트 컴프리헨션은 다음 상황에서 유용합니다.

1. **리스트를 생성할 때**: 리스트 컴프리헨션은 리스트를 생성하는 데 유용합니다. 예를 들어, 1부터 10까지의 숫자를 리스트에 추가하는 코드를 작성할 때 다음과 같이 사용할 수 있습니다.

    ```python
numbers = [i for i in range(1, 11)]
print(numbers)  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

2. **리스트 내의 특정 요소 필터링할 때**: 리스트 내의 특정 요소를 필터링할 때 리스트 컴프리헨션을 사용할 수 있습니다. 예를 들어, 1부터 10까지의 숫자 중 짝수만을 리스트에 추가하는 코드를 작성할 때 다음과 같이 사용할 수 있습니다.

    ```python
numbers = [i for i in range(1, 11) if i % 2 == 0]
print(numbers)  # [2, 4, 6, 8, 10]
```

3. **리스트 내의 요소를 변환할 때**: 리스트 내의 요소를 변환할 때 리스트 컴프리헨션을 사용할 수 있습니다. 예를 들어, 1부터 10까지의 숫자를 제곱해서 리스트에 추가하는 코드를 작성할 때 다음과 같이 사용할 수 있습니다.

    ```python
numbers = [i ** 2 for i in range(1, 11)]
print(numbers)  # [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
```

리스트 컴프리헨션은 리스트를 생성하거나 필터링하거나 변환할 때 유용한 파이썬의 고급 문법입니다. 리스트 컴프리헨션은 코드를 더 짧고 간결하게 작성할 수 있게 해줍니다.
~~~python
numbers = [i for i in range(1, 11)]
print(numbers)  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

2. **리스트에서 필터링할 때**: 컴프리헨션은 목록에서 특정 조건을 만족하는 항목을 필터링하는 데 사용할 수 있습니다. 예를 들어, 목록에서 짝수만 추출하는 코드를 작성할 때 컴프리헨션을 사용할 수 있습니다.

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even_numbers = [num for num in numbers if num % 2 == 0]
print(even_numbers)  # [2, 4, 6, 8, 10]
```

~~~
출력 결과
[2, 4, 6, 8, 10]
~~~

3. **리스트에서 변환할 때**: 컴프리헨션은 목록에서 항목을 변환하는 데 사용할 수 있습니다. 예를 들어, 문자열 목록에서 대문자를 소문자로 변환하는 코드를 작성할 때 컴프리헨션을 사용할 수 있습니다.

```python
strings = ['Hello', 'World', 'Python']
lower_strings = [s.lower() for s in strings]
print(lower_strings)  # ['hello', 'world', 'python']
```

~~~
출력 결과
['hello', 'world', 'python']
~~~

### 언제 사용하지 않는가?

1. **복잡한 로직**: 컴프리헨션은 복잡한 로직을 처리하기에 적합하지 않습니다. 복잡한 로직을 처리할 때, 일반적인 루프를 사용하는 것이 좋습니다.

2. **데이터의 복잡성**: 컴프리헨션은 데이터의 복잡성을 다룰 때 적합하지 않습니다. 데이터의 복잡성에 따라서 일반적인 루프를 사용하는 것이 좋습니다.

3. **가독성**: 컴프리헨션은 가독성을 고려할 때 적합하지 않습니다. 복잡한 컴프리헨션은 코드를 읽는 사람이 이해하기 어려울 수 있습니다. 

### 결론

리스트 컴프리헨션은 목록을 생성하거나 필터링하거나 변환할 때 사용하는 강력한 기능입니다. 그러나 복잡한 로직이나 데이터의 복잡성, 가독성을 고려할 때 일반적인 루프를 사용하는 것이 좋습니다.
```

`{language}`와 `{question}` 같은 자리 표시자는 `invoke()`에 넘기는 딕셔너리 키와 일치해야 합니다.

---

## 여러 변수를 가진 프롬프트

복잡한 태스크일수록 프롬프트에 여러 변수가 필요합니다. 모두 딕셔너리로 넘깁니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "당신은 코드 리뷰 전문가입니다. "
        "언어: {language}. 리뷰 관점: {review_focus}.",
    ),
    ("human", "다음 코드를 리뷰해 주세요:\n\n```{language}\n{code}\n```"),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = prompt | llm | StrOutputParser()

result = chain.invoke({
    "language": "python",
    "review_focus": "가독성과 예외 처리",
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

출력 파서는 LLM 응답을 원하는 형태로 변환합니다. 두 가지가 자주 쓰입니다.

**StrOutputParser**: `AIMessage.content`를 문자열로 꺼냅니다. 대부분의 경우 이걸로 충분합니다.

**JsonOutputParser**: 모델이 JSON을 출력하도록 유도하고, 그 결과를 Python 딕셔너리로 파싱합니다. 모델에게 JSON 형식으로 응답하도록 프롬프트를 명시해야 합니다.

```python
import os

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "당신은 JSON만 출력합니다. 다른 텍스트는 포함하지 마세요.",
    ),
    (
        "human",
        "{topic}에 대한 정보를 다음 JSON 형식으로 출력하세요:\n"
        '{{"name": "이름", "description": "설명", "use_case": "활용 사례"}}',
    ),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = prompt | llm | JsonOutputParser()

result = chain.invoke({"topic": "FAISS"})

print(f"타입: {type(result)}")
print(f"name: {result.get('name')}")
print(f"description: {result.get('description')}")
print(f"use_case: {result.get('use_case')}")
```

~~~
출력 결과
타입: <class 'dict'>
name: FAISS
description: Faiss는 Facebook에서 개발한 효율적인 벡터 집합 검색 알고리즘입니다. 벡터 집합 검색은 대규모 데이터에서 특정 벡터와 유사한 벡터를 검색하는 프로세스입니다.
use_case: FAISS는 클라우드 컴퓨팅, 이미지 검색, 추천 알고리즘, 자연어 처리 등 다양한 분야에서 활용될 수 있습니다.
~~~

JSON 파싱이 불안정하다면 LangChain의 `with_structured_output()`을 쓰는 편이 더 안정적입니다. 이 방법은 llm-api-production-101 시리즈에서 다룹니다.

---

## RunnablePassthrough — 입력을 그대로 전달

파이프 체인에서 입력 일부를 그대로 뒤로 전달하고 싶을 때 `RunnablePassthrough`를 씁니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_messages([
    ("system", "문서를 참고해서 질문에 답하세요."),
    ("human", "문서: {context}\n\n질문: {question}"),
])

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

# context는 그대로, question은 그대로 — 이 체인은 입력을 직접 전달
chain = (
    {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 더 일반적인 패턴: 딕셔너리 입력을 그대로 활용
chain2 = prompt | llm | StrOutputParser()

result = chain2.invoke({
    "context": "FAISS는 Facebook AI Research에서 만든 벡터 검색 라이브러리입니다.",
    "question": "FAISS는 누가 만들었나요?",
})

print(result)
```

~~~
출력 결과
FAISS는 Facebook AI Research에서 만든 벡터 검색 라이브러리입니다.
~~~

`RunnablePassthrough`는 나중에 Retriever와 체인을 연결할 때 자주 씁니다. 4편(Retriever)에서 실제 패턴을 볼 수 있습니다.

---

## 체인에 fallback 추가하기

모델 호출이 실패할 때 대체 체인을 실행하도록 `.with_fallbacks()`를 씁니다.

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

result = chain_with_fallback.invoke({"question": "파이썬 예외 처리 방법은?"})
print(result)
```

~~~
출력 결과
파이썬에서 예외 처리 방법은 다음과 같습니다.

### 1. try-except 블록

`try-except` 블록은 예외를 처리하는 기본적인 방법입니다. `try` 블록 내에서 예외가 발생할 수 있는 코드를 작성하고, `except` 블록 내에서 예외를 처리하는 코드를 작성합니다.

```python
try:
    # 예외가 발생할 수 있는 코드
    x = 5 / 0
except ZeroDivisionError:
    # 예외를 처리하는 코드
    print("ZeroDivisionError")
```

### 2. try-except-else 블록

`try-except-else` 블록은 `try-except` 블록에 추가된 `else` 블록을 의미합니다. `try` 블록 내에서 예외가 발생하지 않은 경우 `else` 블록이 실행됩니다.

```python
try:
    # 예외가 발생할 수 있는 코드
    x = 5 / 1
except ZeroDivisionError:
    # 예외를 처리하는 코드
    print("ZeroDivisionError")
else:
    # 예외가 발생하지 않은 경우 실행되는 코드
    print("정상 실행")
```

### 3. try-except-finally 블록

`try-except-finally` 블록은 `try-except` 블록에 추가된 `finally` 블록을 의미합니다. `finally` 블록은 예외가 발생하거나 발생하지 않은 경우 모두 실행됩니다.

```python
try:
    # 예외가 발생할 수 있는 코드
    x = 5 / 0
except ZeroDivisionError:
    # 예외를 처리하는 코드
    print("ZeroDivisionError")
finally:
    # 예외가 발생하거나 발생하지 않은 경우 모두 실행되는 코드
    print("finally 블록")
```

### 4. 예외를 직접 발생시키기

`raise` 키워드를 사용하여 직접 예외를 발생시킬 수 있습니다.

```python
def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("ZeroDivisionError")
    return a / b

try:
    result = divide(5, 0)
except ZeroDivisionError as e:
... (truncated)
~~~python
try:
    # 코드를 실행합니다.
except 예외 타입:
    # 예외가 발생할 경우에 실행되는 코드입니다.
```

예를 들어 다음과 같은 코드가 있다고 가정해 보겠습니다.

```python
try:
    x = 5 / 0
except ZeroDivisionError:
    print("0으로 나눌 수 없습니다.")
```

~~~
출력 결과
0으로 나눌 수 없습니다.
~~~

이 코드는 0으로 나누는 것을 시도합니다. 0으로 나누는 것이 가능하지 않기 때문에 ZeroDivisionError가 발생하고, 예외 처리 코드인 `print("0으로 나눌 수 없습니다.")`가 실행됩니다.

**2. 여러 예외 처리**

한 번에 여러 예외를 처리할 수 있습니다.

```python
try:
    x = 5 / 0
except (ZeroDivisionError, TypeError):
    print("예외가 발생했습니다.")
```

~~~
출력 결과
예외가 발생했습니다.
~~~

이 코드는 ZeroDivisionError와 TypeError를 함께 처리합니다.

**3. 예외의 상세 정보**

예외의 상세 정보를 얻을 수 있습니다.

```python
try:
    x = 5 / 0
except ZeroDivisionError as e:
    print(f"예외가 발생했습니다: {e}")
```

~~~
출력 결과
예외가 발생했습니다: division by zero
~~~

이 코드는 예외가 발생했을 때의 상세 정보를 출력합니다.

**4. finally**

finally는 try-except 문이 실행되는 동안의 코드를 실행하기 위한 블록입니다. 예외가 발생하더라도 finally 블록은 실행됩니다.

```python
try:
    x = 5 / 0
except ZeroDivisionError:
    print("예외가 발생했습니다.")
finally:
... (truncated)
```

이 패턴은 주 모델이 다운되거나 속도 제한에 걸렸을 때 자동으로 대체 모델로 전환합니다.

---

## 이 코드에서 봐야 할 것

- Prompt chain의 입력은 대부분 딕셔너리입니다. 키 이름이 프롬프트 변수와 맞아야 체인이 자연스럽게 이어집니다.
- `StrOutputParser`와 `JsonOutputParser`의 선택은 모델 품질보다 애플리케이션이 어떤 후속 처리를 기대하는지에 더 가깝습니다.
- `RunnablePassthrough`는 값을 바꾸지 않지만, 체인 안에서 어떤 입력을 그대로 흘려보낼지 명시해 준다는 점이 중요합니다.
- fallback은 예외 처리용 장식이 아니라, 실패해도 같은 출력 계약을 유지하도록 체인을 한 번 더 준비하는 패턴입니다.

## 실무에서 헷갈리는 지점

- 프롬프트 템플릿을 문자열 템플릿으로만 보면 메시지 역할 분리의 장점을 놓치기 쉽습니다.
- JSON 파싱은 파서만 붙이면 끝난다고 생각하기 쉽지만, 모델에게 원하는 스키마를 충분히 강하게 지시해야 안정적입니다.
- fallback 체인은 성공 경로와 동일한 입력·출력 형태를 맞추지 않으면 오히려 디버깅이 더 어려워집니다.

## 체크리스트

- [ ] `ChatPromptTemplate`에 여러 변수를 넣는 입력 딕셔너리를 직접 만들 수 있다
- [ ] 문자열 파서와 JSON 파서를 언제 구분해서 써야 하는지 설명할 수 있다
- [ ] fallback 체인을 붙일 때 출력 형태를 맞춰야 하는 이유를 이해했다

## 마무리

`ChatPromptTemplate`으로 다중 변수 프롬프트를 만들고, `StrOutputParser`와 `JsonOutputParser`의 차이를 확인했습니다. `RunnablePassthrough`는 다음 글들에서 더 자주 나옵니다.

다음 글에서는 Retriever를 체인에 연결해서 문서 검색 결과를 컨텍스트로 주입하는 방법을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangChain 소개 — LCEL과 Runnable 기본](./01-lcel-runnable-basics.md)
- **Prompt와 LLM Chain — 체인 첫 번째 구성 (현재 글)**
- Retriever — 문서 검색과 컨텍스트 주입 (예정)
- Tool Calling — 외부 도구 연결하기 (예정)
- Streaming — 실시간 출력 처리 (예정)
- 실전 체인 조립 — 컴포넌트를 하나로 연결하기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [ChatPromptTemplate 공식 문서](https://python.langchain.com/docs/modules/model_io/prompts/quick_start/)
- [Output parsers](https://python.langchain.com/docs/modules/model_io/output_parsers/)
- [RunnablePassthrough](https://python.langchain.com/docs/expression_language/primitives/passthrough/)

Tags: LangChain, LCEL, Python, LLM
