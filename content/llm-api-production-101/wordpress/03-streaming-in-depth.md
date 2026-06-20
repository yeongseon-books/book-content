---
title: "바이브코딩을 위한 LLM API 운영 (3/6): 스트리밍 심화 — 청크 처리와 오류 복구"
series: llm-api-production-101
episode: 3
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM
- OpenAI
- Streaming
- Python
---

# 바이브코딩을 위한 LLM API 운영 (3/6): 스트리밍 심화 — 청크 처리와 오류 복구

이 글은 **바이브코딩을 위한 LLM API 운영** 시리즈의 세 번째 글입니다. OpenAI 스트리밍 API의 청크 처리, 부분 실패 복구, 토큰 추적을 다룹니다.

---

기본 스트리밍은 작동합니다. 그런데 스트리밍 중간에 네트워크가 끊어지면? 도구 호출이 스트리밍에 포함되면 어떻게 처리하나요? 스트리밍으로 받은 토큰을 어떻게 세나요? 기본 `for chunk in stream`으로는 이런 상황을 처리하기 어렵습니다.

바이브코딩으로 AI에게 "스트리밍 구현해줘"라고 하면 기본 코드가 나옵니다. 청크 병합, 스트리밍 중 도구 호출, 오류 복구를 모르면 프로덕션에서 예상치 못한 문제가 발생합니다.

> "스트리밍의 신뢰성은 청크 처리와 오류 복구에서 나옵니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 스트리밍 청크에서 content와 tool_calls를 어떻게 구분하나요?
2. 스트리밍 중 연결이 끊어지면 어떻게 복구하나요?
3. 스트리밍으로 받은 도구 호출 파라미터를 어떻게 조립하나요?
4. 스트리밍 응답의 토큰 수를 어떻게 추적하나요?
5. stream=True와 stream=False의 응답 구조가 어떻게 다른가요?

---

## 기본 스트리밍

```python
from openai import OpenAI

client = OpenAI()

def stream_response(prompt: str) -> str:
    full_text = ""
    with client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    ) as stream:
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
                full_text += delta.content
    return full_text
```

## 스트리밍 중 도구 호출 처리

```python
def stream_with_tools(messages: list, tools: list) -> dict:
    collected_chunks = []
    tool_calls_buffer = {}

    with client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        stream=True,
    ) as stream:
        for chunk in stream:
            delta = chunk.choices[0].delta

            # 텍스트 청크
            if delta.content:
                collected_chunks.append(delta.content)

            # 도구 호출 청크 병합
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_buffer:
                        tool_calls_buffer[idx] = {"id": tc.id or "", "name": "", "arguments": ""}
                    if tc.function.name:
                        tool_calls_buffer[idx]["name"] += tc.function.name
                    if tc.function.arguments:
                        tool_calls_buffer[idx]["arguments"] += tc.function.arguments

    return {
        "content": "".join(collected_chunks),
        "tool_calls": list(tool_calls_buffer.values()),
    }
```

## 오류 복구

```python
import time

def stream_with_retry(prompt: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            return stream_response(prompt)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"스트리밍 오류, {wait}초 후 재시도: {e}")
            time.sleep(wait)
```

## 토큰 추적

```python
def stream_with_token_count(prompt: str) -> dict:
    token_count = 0
    content = ""

    with client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        stream_options={"include_usage": True},
    ) as stream:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
            if chunk.usage:
                token_count = chunk.usage.completion_tokens

    return {"content": content, "tokens": token_count}
```

---

## Before / After

| 항목 | Before (기본 스트리밍) | After (스트리밍 심화) |
|------|----------------------|---------------------|
| 도구 호출 | 처리 불가 | 청크 병합으로 처리 |
| 연결 끊김 | 서비스 중단 | 지수 백오프 재시도 |
| 토큰 추적 | 없음 | stream_options 사용 |
| 청크 병합 | 없음 | buffer로 조립 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 도구 호출 청크 무시 | 도구 파라미터 누락 | arguments 누적 버퍼 |
| flush=True 없음 | 지연 출력 | print(chunk, end="", flush=True) |
| 재시도 없음 | 일시 오류 시 중단 | stream_with_retry |
| 토큰 추적 없음 | 비용 불명 | stream_options include_usage |

---

## AI 활용 팁

```
OpenAI 스트리밍 API에서 도구 호출 청크를 처리하는 코드를 만들어줘.
텍스트 청크와 도구 호출 청크를 분리해서 처리하고, 도구 호출 파라미터는 버퍼에 누적해줘.
네트워크 오류 시 지수 백오프로 재시도하는 stream_with_retry도 만들어줘.
stream_options include_usage로 토큰 수를 추적해줘.
```

---

## 체크리스트

- [ ] 기본 스트리밍 구현(flush=True)
- [ ] 도구 호출 청크 버퍼 병합
- [ ] stream_with_retry(지수 백오프)
- [ ] stream_options include_usage로 토큰 추적
- [ ] 스트리밍 중 예외 처리
- [ ] 완전한 응답 수집 확인

---

## 처음 질문으로 돌아가기

"스트리밍 중간에 도구 호출이 섞이면 어떻게 처리하나요?" — 도구 호출 파라미터는 여러 청크에 나뉘어 옵니다. arguments 문자열을 버퍼에 누적해서 마지막 청크까지 받은 후 json.loads로 파싱해야 합니다.

---

## 정리

- 도구 호출 청크는 arguments를 인덱스별 버퍼에 누적한다
- stream_with_retry로 네트워크 오류 시 지수 백오프 재시도한다
- stream_options include_usage로 스트리밍 중 토큰 수를 추적한다
- flush=True로 실시간 출력을 보장한다

---

## 참고 자료

- [OpenAI 스트리밍 문서](https://platform.openai.com/docs/api-reference/streaming)
- [스트리밍 도구 호출](https://platform.openai.com/docs/guides/function-calling/streaming)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 기본 스트리밍
- 스트리밍 중 도구 호출 처리
- 오류 복구
- 토큰 추적
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLM, OpenAI, Streaming, Python
