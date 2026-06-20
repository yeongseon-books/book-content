---
title: "바이브코딩을 위한 LLM API 운영 (2/6): 툴 호출 — 함수를 모델에 연결하기"
series: llm-api-production-101
episode: 2
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM
- OpenAI
- Tool Calling
- Python
---

# 바이브코딩을 위한 LLM API 운영 (2/6): 툴 호출 — 함수를 모델에 연결하기

이 글은 **바이브코딩을 위한 LLM API 운영** 시리즈의 두 번째 글입니다. OpenAI API에서 함수를 도구로 정의하고 모델이 호출하는 Tool Calling을 구현합니다.

---

구조화 출력으로 JSON을 받았습니다. 이제 모델이 외부 함수를 직접 호출하게 하고 싶습니다. "날씨 API를 써줘", "데이터베이스를 조회해줘" — 모델이 어떤 함수를, 어떤 파라미터로 호출할지 결정하는 것이 Tool Calling입니다.

바이브코딩으로 AI에게 "Tool Calling 구현해줘"라고 하면 코드가 나옵니다. 도구 스키마가 어떻게 정의되는지, 도구 호출 결과를 어떻게 모델에 다시 전달하는지 모르면 새 도구를 추가하거나 오류를 수정하기 어렵습니다.

> "Tool Calling은 모델이 코드를 실행하는 인터페이스입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 도구 스키마(parameters)가 어떤 형식으로 정의되나요?
2. 모델이 도구를 호출했다고 판단하는 기준이 무엇인가요?
3. 도구 실행 결과를 모델에 다시 전달하는 메시지 형식이 무엇인가요?
4. 여러 도구를 동시에 호출할 수 있나요?
5. 도구 실행 중 오류가 나면 어떻게 처리하나요?

---

## 도구 스키마 정의

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "지정한 도시의 현재 날씨를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "날씨를 조회할 도시 이름 (예: 서울, 부산)",
                    },
                },
                "required": ["city"],
            },
        },
    }
]
```

## 도구 호출 처리

```python
from openai import OpenAI
import json

client = OpenAI()

def get_weather(city: str) -> str:
    return f"{city}: 맑음, 22°C"

def run_tool_loop(messages: list) -> str:
    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
        )

        message = response.choices[0].message
        messages.append(message)

        # 도구 호출 없으면 종료
        if not message.tool_calls:
            return message.content

        # 도구 실행
        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = get_weather(**args)

            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.id,
            })
```

## 오류 처리

```python
def safe_execute_tool(tool_name: str, args: dict, tool_registry: dict) -> str:
    if tool_name not in tool_registry:
        return f"오류: '{tool_name}' 도구를 찾을 수 없습니다."
    try:
        return str(tool_registry[tool_name](**args))
    except Exception as e:
        return f"도구 실행 오류: {str(e)}"
```

---

## Before / After

| 항목 | Before (프롬프트 함수 요청) | After (Tool Calling) |
|------|--------------------------|---------------------|
| 함수 선택 | 모델 추측 | JSON 스키마 정의 |
| 파라미터 파싱 | 텍스트에서 추출 | 자동 JSON 파싱 |
| 다중 호출 | 불가 | 동시 tool_calls |
| 오류 처리 | 없음 | tool message 반환 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| tool_call_id 누락 | 도구 결과 연결 오류 | tool_call.id 사용 |
| 도구 결과 없이 재호출 | API 오류 | tool_calls마다 결과 추가 |
| required 미설정 | 파라미터 누락 | parameters.required 필수 |
| 예외 미처리 | 서비스 중단 | safe_execute_tool |

---

## AI 활용 팁

```
OpenAI Tool Calling으로 날씨 조회와 계산 함수를 도구로 연결해줘.
도구 스키마에 description과 parameters.required를 반드시 포함해줘.
run_tool_loop에서 tool_calls가 없을 때까지 반복하고, 각 도구 결과를 tool_call_id와 함께 메시지에 추가해줘.
safe_execute_tool로 도구 실행 오류를 처리해줘.
```

---

## 체크리스트

- [ ] 도구 스키마(name, description, parameters) 정의
- [ ] run_tool_loop 구현
- [ ] tool_call_id를 tool 메시지에 포함
- [ ] safe_execute_tool로 오류 처리
- [ ] 도구 레지스트리(dict)로 확장 가능 구조
- [ ] 다중 도구 동시 호출 테스트

---

## 처음 질문으로 돌아가기

"프롬프트에 '날씨 API를 써줘'라고 하면 안 되나요?" — 텍스트로 요청하면 모델이 API 호출 형식을 추측합니다. Tool Calling은 모델이 정확한 JSON 형식으로 함수명과 파라미터를 반환하므로 파싱이 안정적입니다.

---

## 정리

- 도구 스키마에 name, description, parameters.required를 명시한다
- tool_calls가 없을 때까지 루프를 실행한다
- 각 도구 실행 결과를 tool_call_id와 함께 tool 역할 메시지로 추가한다
- safe_execute_tool로 도구 실행 오류를 안전하게 처리한다

---

## 참고 자료

- [OpenAI Function Calling 문서](https://platform.openai.com/docs/guides/function-calling)
- [Tool Calling 베스트 프랙티스](https://platform.openai.com/docs/guides/function-calling/best-practices)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 도구 스키마 정의
- 도구 호출 처리
- 오류 처리
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLM, OpenAI, Tool Calling, Python
