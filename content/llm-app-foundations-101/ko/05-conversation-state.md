---
title: "LLM App Foundations 101 (5/6): 대화 상태 관리 — 멀티턴 챗봇 만들기"
series: llm-app-foundations-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LLM
- OpenAI
- Prompt Engineering
- Python
last_reviewed: '2026-05-12'
---

# LLM App Foundations 101 (5/6): 대화 상태 관리 — 멀티턴 챗봇 만들기

챗봇을 처음 만들면 많은 입문자가 같은 장면을 봅니다. 첫 질문에는 잘 답했는데, 두 번째 질문에서 방금 한 말을 잊어버립니다. 사용자는 당연히 “대화 중”이라고 느끼지만, 모델은 마치 새 세션처럼 반응합니다. 이 장면은 버그처럼 보이지만 사실 API 계약에 더 가깝습니다.

LLM은 기본적으로 애플리케이션의 대화 상태를 무료로 보관해 주지 않습니다. 챗봇이 상태를 가진 것처럼 보이는 이유는 애플리케이션이 이전 맥락을 다시 모아 보내기 때문입니다. 즉, 기억은 모델 안의 숨은 능력이 아니라 애플리케이션이 소유하는 자료구조입니다.

이 차이를 빨리 이해해야 멀티턴 설계가 쉬워집니다. 메모리를 모델의 신비한 능력으로 보면 디버깅도 어려워지고 정책도 흐려집니다. 반대로 메모리를 내가 직접 관리하는 상태라고 보면, 어떤 사실을 남기고 어떤 사실을 버릴지, 언제 요약할지, 어디서 비용을 줄일지 설계 포인트가 분명해집니다.

이 글은 LLM App Foundations 101 시리즈의 다섯 번째 글입니다.

여기서는 대화 메모리를 모델 기능이 아니라 애플리케이션 상태 관리 문제로 보고, 멀티턴 챗봇의 최소 구조를 정리하겠습니다.

## 먼저 던지는 질문

- 멀티턴 챗봇의 기억은 모델 안에 있을까요, 요청 안에 있을까요?
- 전체 이력, 슬라이딩 윈도우, 요약 압축은 언제 갈라질까요?
- context overflow를 요청 실패 전에 어떻게 감지할까요?

## 큰 그림

![멀티턴 이력이 누적되는 전체 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/05/05-01-managing-conversation-state-building-a-m.ko.png)

*멀티턴 이력이 누적되는 전체 구조*

이 그림에서는 대화 기억을 모델의 숨은 상태가 아니라 매 요청에 다시 넣는 메시지 이력으로 봅니다. 상태 관리의 핵심은 무엇을 다시 보낼지 정하는 애플리케이션 책임입니다.

## 왜 이 글이 중요한가

프롬프트 설계가 정적인 입력 구조를 다루는 문제였다면, 대화 상태 관리는 시간이 흐르면서 변하는 입력 구조를 다루는 문제입니다. 멀티턴 시스템은 매번 새로운 요청을 보내지만, 동시에 이전 결정과 사용자 선호, 아직 해결되지 않은 질문도 어느 정도 유지해야 합니다. 이 균형이 바로 챗봇 품질의 핵심입니다.

또한 상태 관리는 곧 비용 관리이기도 합니다. 이력을 전부 보존하면 맥락은 강해지지만 토큰 비용이 계속 증가합니다. 너무 짧게 자르면 저렴하지만 중요한 사실을 잃습니다. 요약을 쓰면 오래 버틸 수 있지만, 잘못 요약하면 왜곡된 기억이 세션 전체를 오염시킵니다. 따라서 메모리 정책은 단순한 편의 기능이 아니라 시스템 설계 결정입니다.

무엇보다 멀티턴 품질 문제는 대개 모델보다 상태 전략에서 먼저 해결됩니다. “왜 이 사실을 잊었지?”라는 질문은 모델 파라미터보다 메시지 재구성 로직을 먼저 봐야 답이 나옵니다. 그래서 대화 상태를 이해하는 순간부터 챗봇 개발은 프롬프트 실험이 아니라 애플리케이션 엔지니어링으로 성격이 바뀝니다.

## 멀티턴 메모리를 이해하는 가장 좋은 방법: 모델의 숨은 기억이 아니라 매 요청마다 다시 조립되는 상태로 보는 것입니다

각 채팅 호출은 독립적입니다. 모델은 오직 현재 요청에 들어 있는 메시지 배열만 봅니다. 따라서 멀티턴 대화는 “기억하는 모델”의 결과가 아니라 “이전 문맥을 재전송하는 애플리케이션”의 결과입니다. 이 전제를 받아들이면 상태 관리 문제는 훨씬 평범해집니다. 어떤 데이터를 저장하고, 어떤 규칙으로 다시 조립하고, 언제 줄일지 결정하는 문제로 바뀌기 때문입니다.

이 관점이 중요한 이유는 memory policy가 그대로 비용 정책과 품질 정책이 되기 때문입니다. 전체 이력을 유지하면 단순하지만 비싸고, 슬라이딩 윈도우는 예산이 예측 가능하지만 오래된 사실을 잃고, 요약 압축은 긴 세션에 유리하지만 정보 손실 위험을 동반합니다.

> 멀티턴 챗봇의 기억은 모델 안에 숨어 있는 능력이 아니라, 애플리케이션이 매 요청마다 재구성하는 상태 계약입니다.

## 핵심 개념

첫 원칙은 단순합니다. LLM 호출은 stateless합니다. 현재 요청에 실린 내용만 봅니다. 예를 들어 첫 요청에서 이름을 알려 주고, 두 번째 요청에서 그 이름을 다시 묻더라도 이전 턴을 재전송하지 않으면 모델은 답할 근거가 없습니다.

![이력 재전송 유무가 상태를 가르는 차이](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/05/05-01-why-llm-calls-are-stateless.ko.png)

*이력 재전송 유무가 상태를 가르는 차이*

```python
messages = [
    {"role": "user", "content": "My name is Mina. Please remember that."}
]
```

```python
messages = [
    {"role": "user", "content": "What is my name?"}
]
```

이 구조는 단점만 있는 것이 아닙니다. 요청 재현이 쉽고, 어떤 문맥이 실제로 모델에 들어갔는지 로그로 추적할 수 있으며, 보존 정책을 애플리케이션이 통제할 수 있습니다.

멀티턴 대화는 결국 이력을 다시 보내는 루프입니다.

![이전 턴들을 누적해 다음 요청을 만드는 루프](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/05/05-02-multi-turn-chat-comes-from-replaying-his.ko.png)

*이전 턴들을 누적해 다음 요청을 만드는 루프*

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": "You are a concise Python tutor.",
    },
    {"role": "user", "content": "Explain the difference between a list and a tuple."},
    {
        "role": "assistant",
        "content": "A list is mutable, while a tuple is immutable.",
    },
    {"role": "user", "content": "Which one is better as a dictionary key then?"},
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.3,
)

print(completion.choices[0].message.content)
```

가장 단순한 메모리 패턴은 전체 이력 유지입니다.

![전체 이력을 계속 보낼 때의 장단점](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/05/05-03-keeping-the-full-history-is-the-simplest.ko.png)

*전체 이력을 계속 보낼 때의 장단점*

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

history = [
    {
        "role": "system",
        "content": "You are a concise technical support assistant.",
    }
]

def ask(user_text: str) -> str:
    history.append({"role": "user", "content": user_text})

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=history,
        temperature=0.2,
    )

    answer = completion.choices[0].message.content or ""
    history.append({"role": "assistant", "content": answer})
    return answer

print(ask("My product is a monthly SaaS service. Please remember that."))
print(ask("Now write a one-line refund policy statement."))
```

이 방식은 이해와 디버깅이 가장 쉽지만, 턴이 늘수록 비용과 지연도 함께 증가합니다.

다음 기본 패턴은 최근 N턴만 남기는 슬라이딩 윈도우입니다.

![전체 이력, 윈도우, 요약 압축의 차이 비교](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/05/05-04-sliding-windows-retain-only-the-last-n-t.ko.png)

*전체 이력, 윈도우, 요약 압축의 차이 비교*

```python
import os
from collections import deque

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

system_message = {
    "role": "system",
    "content": "You are a chatbot that helps users learn Python.",
}
recent_turns = deque(maxlen=6)  # last 3 user/assistant pairs

def ask(user_text: str) -> str:
    recent_turns.append({"role": "user", "content": user_text})

    messages = [system_message, *recent_turns]
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.3,
    )

    answer = completion.choices[0].message.content or ""
    recent_turns.append({"role": "assistant", "content": answer})
    return answer
```

이 방식은 예산을 통제하기 쉽지만, 창 밖으로 밀려난 사실은 모델도 함께 잃습니다. 오래 유지해야 할 사실은 `system`이나 별도 요약으로 승격해야 합니다.

긴 세션에서는 요약 압축이 필요합니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

system_message = {
    "role": "system",
    "content": "You are a project-planning chatbot.",
}
summary_text = ""
recent_turns = []

def summarize_history(history_chunk: list[dict[str, str]], current_summary: str) -> str:
    prompt = [
        {
            "role": "system",
            "content": (
                "Compress the conversation. Preserve user goals, confirmed facts, "
                "preferences, and unresolved questions."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Current summary:\n{current_summary or '(none)'}\n\n"
                f"New history chunk:\n{history_chunk}"
            ),
        },
    ]

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=prompt,
        temperature=0.1,
    )
    return completion.choices[0].message.content or ""

def build_messages(user_text: str) -> list[dict[str, str]]:
    messages = [system_message]
    if summary_text:
        messages.append(
            {
                "role": "system",
                "content": f"Conversation summary:\n{summary_text}",
            }
        )
    messages.extend(recent_turns)
    messages.append({"role": "user", "content": user_text})
    return messages
```

요약은 본질적으로 손실 압축이므로 무엇을 보존할지 명확해야 합니다. 사용자 목표, 확정 사실, 선호, 미해결 질문 같은 지속 정보가 우선입니다.

긴 세션의 실패는 대부분 컨텍스트 예산 초과에서 시작합니다. 그래서 사전 감지가 중요합니다.

![요청 실패 전에 예산을 점검하는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/05/05-05-detecting-context-overflow-before-the-re.ko.png)

*요청 실패 전에 예산을 점검하는 흐름*

```python
def rough_token_count(messages: list[dict[str, str]]) -> int:
    total_chars = sum(len(message["content"]) for message in messages)
    overhead = len(messages) * 12
    return (total_chars // 4) + overhead

def enforce_budget(messages: list[dict[str, str]], max_input_tokens: int = 6000) -> list[dict[str, str]]:
    if rough_token_count(messages) <= max_input_tokens:
        return messages

    trimmed = messages[:1] + messages[-8:]
    if rough_token_count(trimmed) <= max_input_tokens:
        return trimmed

    raise ValueError("Conversation is too long. A more aggressive summary is required.")
```

이제 이를 하나의 CLI 챗봇으로 합치면 상태 위치가 더 또렷해집니다. 핵심은 `system_message`, `recent_turns`, `summary_text`, `MAX_INPUT_TOKENS` 같은 값이 모두 애플리케이션 쪽 상태라는 점입니다. 실제 구현에서는 `/reset`, `/summary`, `/quit` 같은 명령을 제공하고, 요청 전 길이를 점검한 뒤 초과 시 오래된 턴을 요약으로 접는 흐름이 기본 골격이 됩니다. 프로덕션 환경이라면 이 상태를 메모리 변수 대신 Redis나 데이터베이스로 옮기고, 요약 성공 여부와 토큰 사용량을 함께 로깅하는 편이 안전합니다.

## 흔히 헷갈리는 지점

- 멀티턴 기억을 모델 기능으로 오해하기 쉽지만, 실제로는 `messages` 배열 재구성 로직입니다.
- 전체 이력을 무조건 보존하면 좋다고 생각하기 쉽지만, 긴 세션에서는 비용과 지연이 빠르게 커집니다.
- 슬라이딩 윈도우만 쓰면 충분하다고 보기 쉽지만, 세션 전체에 남아야 하는 사실은 별도 보존 전략이 필요합니다.
- 요약은 압축이므로 반드시 정보 손실 위험이 있습니다. 요약 프롬프트가 무엇을 보존할지 분명해야 합니다.
- 컨텍스트 초과를 실패 후에만 다루면 늦습니다. 길이 추정과 사전 압축이 먼저 있어야 합니다.

## 운영 체크리스트

- [ ] 각 턴의 `assistant` 답변을 다음 호출용 이력에 다시 추가합니다.
- [ ] 전체 이력 모드와 최근 N턴 모드를 각각 비교해 장단점을 확인했습니다.
- [ ] 요약 프롬프트에 사용자 목표, 확정 사실, 선호, 미해결 질문 보존 규칙을 적었습니다.
- [ ] 요청 전 누적 입력 길이를 추정하고 한계에 가까워지면 경고 또는 압축을 실행합니다.
- [ ] 세션 초기화와 상태 확인용 명령(`/reset`, `/summary`, `/quit`)을 제공합니다.

## 정리

멀티턴 챗봇의 핵심은 모델이 기억하는 척 보이게 만드는 데 있지 않습니다. 실제로는 애플리케이션이 무엇을 기억으로 간주할지 정의하고, 그것을 매 요청마다 다시 조립해 보내는 데 있습니다. 이 전제를 받아들이면 대화 상태 관리는 훨씬 더 명확한 엔지니어링 문제로 바뀝니다.

실전에서는 세 가지 패턴을 함께 보게 됩니다. 짧은 세션은 전체 이력 유지로 충분하고, 예산 예측이 중요하면 슬라이딩 윈도우가 유리하며, 긴 세션은 요약 압축이 필요합니다. 대부분의 실제 시스템은 이 셋을 섞어 씁니다.

다음 글에서는 마지막 기초 주제로 스트리밍 응답을 다룹니다. 이번 글이 “무엇을 기억할 것인가”의 문제였다면, 다음 글은 “생성 중인 답을 어떻게 즉시 보여 줄 것인가”의 문제입니다.

## 처음 질문으로 돌아가기

- 멀티턴 챗봇의 기억은 모델 안에 있을까요, 요청 안에 있을까요?
  - 기억은 모델 안에 자동으로 남지 않습니다. 애플리케이션이 이전 메시지를 다시 조립해 요청에 넣을 때 멀티턴처럼 동작합니다.

- 전체 이력, 슬라이딩 윈도우, 요약 압축은 언제 갈라질까요?
  - 짧고 정확한 대화는 전체 이력이 단순하고, 비용이나 길이가 커지면 슬라이딩 윈도우나 요약 압축으로 전환합니다.

- context overflow를 요청 실패 전에 어떻게 감지할까요?
  - 요청 전에 메시지 길이와 예상 출력 길이를 더해 토큰 예산을 점검하면 context overflow를 실패 전에 줄일 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM App Foundations 101 (1/6): LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기](./01-llm-api-first-call.md)
- [LLM App Foundations 101 (2/6): 토큰 이해하기 — 비용, 한계, 컨텍스트 창](./02-understanding-tokens.md)
- [LLM App Foundations 101 (3/6): 프롬프트 엔지니어링 기초 — System·User·Assistant 역할](./03-prompt-engineering-basics.md)
- [LLM App Foundations 101 (4/6): Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기](./04-few-shot-and-cot.md)
- **LLM App Foundations 101 (5/6): 대화 상태 관리 — 멀티턴 챗봇 만들기 (현재 글)**
- LLM App Foundations 101 (6/6): 스트리밍 응답 처리 — 실시간으로 출력 받기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Groq quickstart](https://console.groq.com/docs/quickstart)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Groq models](https://console.groq.com/docs/models)
- [OpenAI prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering)

### 관련 시리즈

- [스트리밍 응답 처리 — 실시간으로 출력 받기](./06-streaming-responses.md)
- [프롬프트 엔지니어링 기초 — System·User·Assistant 역할](./03-prompt-engineering-basics.md)
- [챗봇 패턴 — 대화 이력 관리와 상태](../../ai-app-patterns-101/ko/01-chatbot-pattern.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-app-foundations-101/ko/05-conversation-state)

Tags: LLM, OpenAI, Prompt Engineering, Python
