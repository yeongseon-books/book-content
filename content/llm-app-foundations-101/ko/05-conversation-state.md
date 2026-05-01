---
title: 대화 상태 관리 — 멀티턴 챗봇 만들기
series: llm-app-foundations-101
episode: 5
language: ko
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

# 대화 상태 관리 — 멀티턴 챗봇 만들기

> LLM 앱 기초 시리즈 (5/6)

예제 코드: [github.com/yeongseon-books/llm-app-foundations-101](https://github.com/yeongseon-books/llm-app-foundations-101/tree/main/ko/05-conversation-state)

챗봇 UI를 처음 붙이면 많은 입문자가 같은 장면을 봅니다. 첫 질문에는 잘 답했는데, 두 번째 질문에서 방금 한 말을 잊어버립니다. 사용자는 대화를 이어 간다고 느끼는데 모델은 문맥이 끊긴 듯 반응합니다. 여기서 중요한 사실 하나를 먼저 분명히 해야 합니다. LLM은 기본적으로 상태를 들고 있지 않습니다. 우리가 매번 “대화처럼” 보이게 만들어 주기 때문에 대화가 되는 것입니다.

실무에서는 이 차이를 빨리 이해해야 합니다. 상태가 없는 모델 앞에 상태가 있는 애플리케이션을 세우는 순간, 누가 무엇을 기억하고 누가 무엇을 다시 보내는지 설계해야 하기 때문입니다. 메모리를 모델이 갖는다고 생각하면 디버깅이 어려워지고, 메모리를 애플리케이션이 관리한다고 이해하면 문제를 훨씬 명확하게 쪼갤 수 있습니다.

이번 글에서는 Groq의 `llama-3.1-8b-instant`를 기준으로 멀티턴 대화의 기본 구조를 정리하고, Python CLI 챗봇으로 끝까지 구현해 봅니다. 범위는 일곱 가지입니다.

- 왜 LLM이 본질적으로 stateless한지
- `messages` 배열 누적으로 멀티턴 대화가 만들어지는 원리
- 전체 이력을 유지하는 가장 단순한 메모리 패턴
- 최근 N턴만 남기는 sliding window 패턴
- 긴 대화에 대응하는 요약 기반 압축 패턴
- 입력 루프와 이력 관리가 들어간 실용적인 CLI 챗봇 구현
- 컨텍스트 창 초과를 미리 감지하고 줄이는 실전 대응

포인트는 단순합니다. **멀티턴 챗봇의 기억은 모델 안이 아니라 애플리케이션 쪽 자료구조에 있습니다.**

---

<!-- ebook-only:start -->

이 장의 핵심: **대화 상태는 메시지 목록을 직접 관리하는 것이다.** 모델은 무상태(stateless)이므로 매 호출에 전체 히스토리를 전달해야 한다.

## 이 장의 위치

이 글은 시리즈 6편 중 5번째 장입니다.
앞 장에서는 **Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기**을 다뤘습니다.
이 장을 마치면 다음 장에서 **스트리밍 응답 처리 — 실시간으로 출력 받기**으로 이어집니다.
<!-- ebook-only:end -->

## LLM은 왜 상태가 없는가

채팅 제품을 쓰다 보면 모델이 세션을 기억하는 것처럼 보이지만, API 경계에서는 그렇지 않습니다. `client.chat.completions.create()` 호출 하나는 그 요청 본문 안에 들어 있는 정보만 보고 답합니다. 서버가 이전 요청의 의미를 자동으로 이어 붙여 주지 않습니다.

예를 들어 첫 번째 요청에서 아래 메시지를 보냈다고 하겠습니다.

```python
messages = [
    {"role": "user", "content": "내 이름은 민준이야. 기억해 줘."}
]
```

이때 모델은 “민준”이라는 정보를 사용해 답할 수 있습니다. 하지만 두 번째 요청에서 아래처럼 보내면 상황이 달라집니다.

```python
messages = [
    {"role": "user", "content": "내 이름이 뭐였지?"}
]
```

두 번째 요청 본문에는 `민준`이라는 문자열이 없습니다. 개발자가 첫 번째 턴을 다시 보내지 않았기 때문입니다. 모델 입장에서는 완전히 새로운 작업입니다. 이 점이 stateless의 의미입니다. 요청 A와 요청 B 사이의 연결을 모델이 암묵적으로 보존하지 않습니다.

이 구조가 꼭 단점만은 아닙니다. 오히려 운영 관점에서는 장점도 큽니다.

- 요청 하나를 독립적으로 재현하기 쉽습니다.
- 어떤 문맥이 모델에 들어갔는지 명시적으로 추적할 수 있습니다.
- 메모리 정책을 애플리케이션에서 통제할 수 있습니다.
- 개인정보 보존 범위를 코드 레벨에서 결정할 수 있습니다.

결국 챗봇의 “기억”은 모델의 능력이 아니라 애플리케이션의 입력 재구성 능력입니다.

---

## 멀티턴 대화는 messages 배열 누적으로 만듭니다

멀티턴 대화의 원리는 의외로 단순합니다. 새 질문을 보낼 때 이전 턴들을 함께 다시 보냅니다. 모델은 그 배열을 읽고 “지금까지 이런 대화가 있었고, 이제 이 다음 답을 해야 한다”고 해석합니다.

채팅 API에서 대화 이력은 보통 아래 세 역할로 표현합니다.

- `system`: 전체 행동 규칙
- `user`: 사용자의 입력
- `assistant`: 모델이 앞서 답한 내용

가장 작은 멀티턴 예제는 아래와 같습니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": "당신은 짧고 정확하게 답하는 Python 튜터입니다.",
    },
    {"role": "user", "content": "리스트와 튜플의 차이를 설명해 줘."},
    {
        "role": "assistant",
        "content": "리스트는 변경 가능하고, 튜플은 변경 불가능합니다.",
    },
    {"role": "user", "content": "그럼 둘 중 어느 쪽이 딕셔너리 키로 더 적합해?"},
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.3,
)

print(completion.choices[0].message.content)
```

여기서 핵심은 마지막 질문 하나가 아니라 그 앞에 붙어 있는 이력입니다. 모델은 `그럼`과 `둘 중`이 무엇을 가리키는지 스스로 추론하는 것이 아니라, 앞선 메시지에서 그 대상을 읽습니다. 같은 질문을 이력 없이 보내면 훨씬 덜 안정적인 답이 나옵니다.

이 패턴을 구현할 때 애플리케이션은 보통 다음 순서를 반복합니다.

1. 사용자 입력을 이력 리스트에 추가합니다.
2. 그 시점의 `messages` 전체를 모델에 보냅니다.
3. 모델 응답을 받아 다시 이력 리스트에 추가합니다.
4. 다음 사용자 입력을 기다립니다.

바로 이 반복이 멀티턴 챗봇의 본체입니다.

---

## 전체 이력 유지는 가장 단순한 시작점입니다

가장 먼저 구현하기 쉬운 방식은 전체 이력을 계속 들고 가는 것입니다. 버그가 적고 이해도 쉽습니다. 대화가 짧거나 내부 운영 도구처럼 세션 길이가 제한된 경우에는 지금도 충분히 실용적입니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

history = [
    {
        "role": "system",
        "content": "당신은 간결한 기술 지원 도우미입니다.",
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

print(ask("내 서비스는 월 구독형 SaaS야. 기억해 줘."))
print(ask("그럼 환불 정책 문구를 한 줄로 써 줘."))
```

이 방식의 장점은 분명합니다.

- 구현이 가장 쉽습니다.
- 문맥 보존력이 가장 좋습니다.
- 응답 품질이 흔들릴 때 원인을 추적하기 쉽습니다.

반면 약점도 뚜렷합니다. 대화가 길어질수록 프롬프트 토큰이 계속 늘어납니다. 응답이 느려지고, 비용이 늘고, 결국 컨텍스트 창 한계에 닿습니다. 사용자가 한 시간 동안 대화한 이력을 처음부터 끝까지 매번 다시 보내는 구조이기 때문입니다.

그래서 전체 이력 유지는 입문 단계의 기준선으로는 좋지만, 길게 이어지는 세션의 기본 해법으로 두기에는 부담이 큽니다.

---

## sliding window는 최근 N턴만 남깁니다

대화 길이가 길어질수록 보통 중요한 정보는 최근 구간에 몰립니다. 이 점을 이용한 방식이 sliding window입니다. 시스템 프롬프트는 고정으로 유지하고, 최근 N개의 user/assistant 턴만 남깁니다.

```python
import os
from collections import deque

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

system_message = {
    "role": "system",
    "content": "당신은 Python 학습을 돕는 챗봇입니다.",
}
recent_turns = deque(maxlen=6)  # 최근 3턴(user+assistant)

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

이 패턴은 토큰 사용량을 예측하기 쉽다는 장점이 있습니다. 메모리 크기가 고정되기 때문입니다. 다만 중요한 사실 하나를 놓치면 안 됩니다. 최근 대화만 남기므로 오래전 제약이나 사용자 선호가 사라질 수 있습니다. 예를 들어 처음에 “항상 한국어로 답해 줘”, “내 서비스 이름은 AcmeCloud야” 같은 정보가 나왔고 그것이 `system`으로 승격되지 않았다면, 윈도우 밖으로 밀려난 순간 모델도 잊습니다.

실무에서는 sliding window가 특히 잘 맞는 경우가 있습니다.

- 고객 지원처럼 최근 맥락이 가장 중요한 대화
- 길이가 짧고 회전이 빠른 Q&A 세션
- 세션당 비용 상한을 명확히 잡아야 하는 서비스

반대로 긴 작업형 대화에서는 이 방식만으로 부족할 수 있습니다. 그때 다음 패턴이 필요합니다.

---

## 요약 기반 압축은 긴 대화를 짧게 접습니다

오래된 이력을 다 버리기는 아깝고, 그대로 다 들고 가기에는 너무 길다면 중간 지점이 필요합니다. 가장 많이 쓰는 방법이 요약 기반 압축입니다. 오래된 대화를 한 덩어리 요약으로 바꾸고, 최근 몇 턴만 원문으로 유지합니다.

구조는 보통 세 조각입니다.

- 고정 `system` 메시지
- 이전 대화의 핵심을 압축한 `summary`
- 최근 raw turn 몇 개

아래는 가장 기초적인 구현 예제입니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

system_message = {
    "role": "system",
    "content": "당신은 프로젝트 관리 챗봇입니다.",
}
summary_text = ""
recent_turns = []

def summarize_history(history_chunk: list[dict[str, str]], current_summary: str) -> str:
    prompt = [
        {
            "role": "system",
            "content": (
                "다음 대화 이력을 짧게 압축하세요. "
                "반드시 아래 항목을 유지하세요: 사용자 목표, 확정된 사실, 미해결 항목."
            ),
        },
        {
            "role": "user",
            "content": (
                f"기존 요약:\n{current_summary or '(없음)'}\n\n"
                f"새로 압축할 대화:\n{history_chunk}"
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
                "content": f"이전 대화 요약:\n{summary_text}",
            }
        )
    messages.extend(recent_turns)
    messages.append({"role": "user", "content": user_text})
    return messages
```

실전에서 중요한 점은 요약을 아무 정보나 뭉개는 용도로 쓰지 않는 것입니다. 요약이 잘못되면 그 뒤의 모든 응답이 잘못된 기억 위에서 이어집니다. 따라서 요약 프롬프트에는 보통 아래 항목을 넣습니다.

- 사용자의 장기 목표
- 이미 합의한 사실
- 선호 언어, 형식, 제약
- 아직 해결되지 않은 질문

요약은 토큰을 줄여 주지만, 손실 압축이라는 점을 잊으면 안 됩니다. 원문을 버리는 순간 세부 맥락 일부는 되돌릴 수 없습니다.

---

## 컨텍스트 창 초과는 미리 감지하고 줄여야 합니다

멀티턴 챗봇에서 흔한 장애는 모델 품질보다도 입력이 너무 길어지는 문제입니다. 대화가 계속 누적되면 어느 순간 provider가 요청을 거절하거나, 응답 길이를 줄이느라 품질이 흔들립니다. 이를 피하려면 보내기 전에 길이를 대략이라도 점검해야 합니다.

토큰을 정확히 세는 전용 토크나이저가 가장 좋지만, 입문 단계에서는 거친 추정치만으로도 충분히 위험 신호를 잡을 수 있습니다. 아래 예제는 문자 수 기반으로 입력 길이를 대강 추정합니다.

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

    raise ValueError("대화 이력이 너무 깁니다. 더 공격적인 요약이 필요합니다.")
```

거친 추정이더라도 운영 가치는 있습니다. 너무 긴 요청을 보내기 전에 아래 같은 대응을 자동화할 수 있기 때문입니다.

- 오래된 raw turn을 요약으로 압축
- sliding window 크기를 줄임
- 응답 최대 길이를 낮춤
- 사용자에게 세션을 새로 시작하도록 안내

한 가지 더 실용적인 팁을 덧붙이면, 응답 이후 `completion.usage`를 로그로 남기는 습관이 좋습니다. 그래야 어떤 사용자 세션이 비용을 밀어 올리는지, 어느 지점에서 프롬프트가 급격히 커지는지 잡아낼 수 있습니다.

---

## 실용적인 CLI 챗봇을 완성해 봅시다

이제 앞선 패턴을 한 파일로 모아 보겠습니다. 아래 예제는 네 가지를 함께 처리합니다.

- 입력 루프
- 전체 이력 저장
- 길이 예산 초과 시 요약 압축
- 최근 몇 턴만 raw 형태로 유지

```python
import os
from typing import List, Dict

from groq import Groq

MODEL = "llama-3.1-8b-instant"
MAX_INPUT_TOKENS = 6000
RAW_TURN_LIMIT = 6  # 최근 3턴(user+assistant)

client = Groq(api_key=os.environ["GROQ_API_KEY"])

system_message = {
    "role": "system",
    "content": (
        "당신은 실무형 Python 및 LLM 앱 도우미입니다. "
        "모르면 모른다고 말하고, 답변은 짧고 정확하게 유지하세요."
    ),
}

summary_text = ""
recent_turns: List[Dict[str, str]] = []

def rough_token_count(messages: List[Dict[str, str]]) -> int:
    total_chars = sum(len(message["content"]) for message in messages)
    overhead = len(messages) * 12
    return (total_chars // 4) + overhead

def summarize_old_turns(old_turns: List[Dict[str, str]], current_summary: str) -> str:
    completion = client.chat.completions.create(
        model=MODEL,
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": (
                    "대화 이력을 압축 요약하세요. "
                    "반드시 사용자 목표, 확정된 사실, 선호, 미해결 질문을 남기세요."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"기존 요약:\n{current_summary or '(없음)'}\n\n"
                    f"추가할 대화:\n{old_turns}"
                ),
            },
        ],
    )
    return completion.choices[0].message.content or current_summary

def build_messages(user_text: str) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = [system_message]

    if summary_text:
        messages.append(
            {
                "role": "system",
                "content": f"이전 대화 요약:\n{summary_text}",
            }
        )

    messages.extend(recent_turns)
    messages.append({"role": "user", "content": user_text})
    return messages

def compress_if_needed(next_user_text: str) -> None:
    global summary_text, recent_turns

    candidate = build_messages(next_user_text)
    if rough_token_count(candidate) <= MAX_INPUT_TOKENS:
        return

    if len(recent_turns) > RAW_TURN_LIMIT:
        old_turns = recent_turns[:-RAW_TURN_LIMIT]
        recent_turns = recent_turns[-RAW_TURN_LIMIT:]
        summary_text = summarize_old_turns(old_turns, summary_text)

    candidate = build_messages(next_user_text)
    if rough_token_count(candidate) > MAX_INPUT_TOKENS:
        raise ValueError("입력이 너무 깁니다. /reset으로 새 세션을 시작하세요.")

def ask(user_text: str) -> str:
    compress_if_needed(user_text)

    messages = build_messages(user_text)
    completion = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
    )

    answer = completion.choices[0].message.content or ""
    recent_turns.append({"role": "user", "content": user_text})
    recent_turns.append({"role": "assistant", "content": answer})

    usage = completion.usage
    print(f"[tokens] prompt={usage.prompt_tokens} total={usage.total_tokens}")
    return answer

def main() -> None:
    global summary_text, recent_turns

    print("멀티턴 챗봇을 시작합니다. /reset, /summary, /quit 명령을 지원합니다.")

    while True:
        user_text = input("you> ").strip()

        if not user_text:
            continue
        if user_text == "/quit":
            break
        if user_text == "/reset":
            summary_text = ""
            recent_turns = []
            print("assistant> 세션을 초기화했습니다.")
            continue
        if user_text == "/summary":
            print(f"assistant> 현재 요약:\n{summary_text or '(없음)'}")
            continue

        try:
            answer = ask(user_text)
            print(f"assistant> {answer}\n")
        except ValueError as exc:
            print(f"assistant> {exc}\n")

if __name__ == "__main__":
    main()
```

이 예제의 의도는 프레임워크를 보여 주는 데 있지 않습니다. 실제 상태 관리 책임이 어디 있는지 드러내는 데 있습니다. `summary_text`, `recent_turns`, `MAX_INPUT_TOKENS`가 모두 애플리케이션 계층에 있습니다. 모델은 그때그때 조립된 입력만 받습니다.

운영 코드로 가져갈 때는 몇 가지를 더 붙이면 좋습니다.

- 세션별 이력을 메모리 대신 DB나 Redis에 저장
- 사용자별 요약을 별도 컬럼으로 분리
- 토큰 사용량과 지연 시간을 구조화 로그로 기록
- 실패한 요약 요청에 대한 재시도와 백오프 추가

---

## 어떤 메모리 패턴을 언제 고를까

세 패턴을 한 문장으로 정리하면 이렇습니다. 짧은 세션이면 전체 이력 유지, 예산이 빡빡하면 sliding window, 긴 작업형 대화면 요약 기반 압축입니다. 중요한 것은 한 가지 방식에 집착하지 않는 것입니다. 실전에서는 세 방식을 섞어 씁니다.

예를 들어 시스템 규칙은 항상 유지하고, 최근 3턴은 raw로 보존하고, 그 이전은 요약으로 접는 혼합형이 가장 흔합니다. 오늘 만든 CLI도 바로 그 구조입니다. 이 구성이 널리 쓰이는 이유는 품질과 비용 사이의 균형이 괜찮기 때문입니다.

멀티턴 챗봇을 설계할 때 마지막으로 점검할 질문은 세 가지입니다.

- 오래 남겨야 하는 정보는 무엇인가
- 버려도 되는 정보는 무엇인가
- 요약이 틀렸을 때 어떻게 복구할 것인가

이 질문에 답할 수 있으면, 메모리는 더 이상 막연한 감각 문제가 아니라 설계 가능한 컴포넌트가 됩니다.

<!-- blog-only:start -->
다음 글: [스트리밍 응답 처리 — 실시간으로 출력 받기](./06-streaming-responses.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기](./01-llm-api-first-call.md)
- [토큰 이해하기 — 비용, 한계, 컨텍스트 창](./02-understanding-tokens.md)
- [프롬프트 엔지니어링 기초 — System·User·Assistant 역할](./03-prompt-engineering-basics.md)
- [Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기](./04-few-shot-and-cot.md)
- **대화 상태 관리 — 멀티턴 챗봇 만들기 (현재 글)**
- 스트리밍 응답 처리 — 실시간으로 출력 받기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Groq quickstart](https://console.groq.com/docs/quickstart)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Groq models](https://console.groq.com/docs/models)
- [OpenAI prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering)

Tags: LLM, OpenAI, Prompt Engineering, Python
