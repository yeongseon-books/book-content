---
title: "바이브코딩을 위한 LLM 앱 기초 (5/6): 대화 상태 관리 — 멀티턴 챗봇 만들기"
series: llm-app-foundations-101
episode: 5
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM
- Chatbot
- Conversation State
- Python
---

# 바이브코딩을 위한 LLM 앱 기초 (5/6): 대화 상태 관리 — 멀티턴 챗봇 만들기

이 글은 **바이브코딩을 위한 LLM 앱 기초** 시리즈의 다섯 번째 글입니다. LLM API로 이전 대화를 기억하는 멀티턴 챗봇을 구현하는 방법을 다룹니다.

---

API 단일 호출은 stateless입니다. 모델은 이전 대화를 기억하지 않습니다. "방금 제가 물어본 것 기억해요?"라고 하면 모르는 게 정상입니다. 챗봇이 대화를 기억하게 하려면 messages 배열에 이전 대화를 직접 넣어야 합니다.

바이브코딩으로 AI에게 "챗봇 만들어줘"라고 하면 단일 호출 코드가 나올 수 있습니다. 대화 기록을 어디에 저장하고, 어떻게 messages에 포함하고, 언제 기록을 정리해야 하는지 이해해야 진짜 챗봇이 됩니다.

> "LLM 챗봇의 기억은 messages 배열에 있습니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 왜 LLM은 이전 대화를 자동으로 기억하지 못하나요?
2. messages 배열에 이전 대화를 어떻게 포함하나요?
3. 대화가 길어지면 어떤 문제가 생기나요?
4. 여러 사용자의 대화를 분리해서 관리하는 방법이 있나요?
5. 대화 기록을 언제 정리(트리밍)해야 하나요?

---

## 기본 멀티턴 챗봇

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SimpleChatbot:
    def __init__(self, system_prompt: str):
        self.messages = [{"role": "system", "content": system_prompt}]

    def chat(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
        )

        assistant_reply = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": assistant_reply})

        return assistant_reply

    def reset(self):
        self.messages = [self.messages[0]]  # system 메시지만 유지
```

## 세션 기반 다중 사용자

```python
class MultiUserChatbot:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.sessions: dict[str, list] = {}

    def _get_session(self, session_id: str) -> list:
        if session_id not in self.sessions:
            self.sessions[session_id] = [
                {"role": "system", "content": self.system_prompt}
            ]
        return self.sessions[session_id]

    def chat(self, session_id: str, user_input: str) -> str:
        messages = self._get_session(session_id)
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        return reply
```

## 대화 기록 트리밍

```python
import tiktoken

def trim_messages(messages: list, max_tokens: int = 4000, model: str = "gpt-4o-mini") -> list:
    encoder = tiktoken.encoding_for_model(model)
    system = messages[0]  # system 메시지 보존
    rest = messages[1:]

    while rest:
        total = sum(len(encoder.encode(m["content"])) for m in [system] + rest)
        if total <= max_tokens:
            break
        rest = rest[2:]  # 가장 오래된 user+assistant 쌍 제거

    return [system] + rest
```

---

## Before / After

| 항목 | Before (단일 호출) | After (멀티턴) |
|------|------------------|--------------------|
| 이전 대화 | 기억 못함 | messages에 포함 |
| 세션 분리 | 없음 | session_id로 격리 |
| 컨텍스트 관리 | 없음 | trim_messages |
| 대화 초기화 | 없음 | reset() |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| messages 누적 없음 | 이전 대화 망각 | messages에 모든 대화 추가 |
| 세션 미분리 | 사용자 간 대화 혼합 | session_id 기반 분리 |
| 무한 누적 | 컨텍스트 초과 | trim_messages |
| system 메시지 제거 | 역할 초기화 | trim 시 system 보존 |

---

## AI 활용 팁

```
세션 ID로 사용자를 분리하는 멀티턴 챗봇을 만들어줘.
messages에 이전 대화를 누적하고, 컨텍스트 한도 초과 시 오래된 대화를 제거해줘.
system 메시지는 항상 보존하고, trim은 user+assistant 쌍 단위로 해줘.
```

---

## 체크리스트

- [ ] SimpleChatbot에 messages 누적 구현
- [ ] MultiUserChatbot으로 세션 분리
- [ ] trim_messages로 컨텍스트 관리
- [ ] system 메시지 보존 확인
- [ ] reset() 메서드 구현
- [ ] 대화 기록 영속화(JSON 파일)

---

## 처음 질문으로 돌아가기

"LLM이 이전 대화를 기억하지 못하는 건 버그 아닌가요?" — 설계입니다. 각 API 호출은 독립적입니다. 대화 기억은 messages 배열에 이전 대화를 넣어서 구현하는 것이고, 이것이 LLM 앱의 상태 관리 핵심입니다.

---

## 정리

- LLM API는 stateless이므로 이전 대화를 messages에 직접 포함한다
- session_id로 사용자별 대화를 격리한다
- trim_messages로 오래된 대화를 정리해 컨텍스트 초과를 방지한다
- trim 시 system 메시지는 항상 보존한다

---

## 참고 자료

- [OpenAI 대화 예시](https://platform.openai.com/docs/guides/text-generation/conversation)
- [tiktoken GitHub](https://github.com/openai/tiktoken)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 기본 멀티턴 챗봇
- 세션 기반 다중 사용자
- 대화 기록 트리밍
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLM, Chatbot, Conversation State, Python
