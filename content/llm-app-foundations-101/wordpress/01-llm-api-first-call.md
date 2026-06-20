---
title: "바이브코딩을 위한 LLM 앱 기초 (1/6): LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기"
series: llm-app-foundations-101
episode: 1
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM
- OpenAI
- Prompt Engineering
- Python
---

# 바이브코딩을 위한 LLM 앱 기초 (1/6): LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기

이 글은 **바이브코딩을 위한 LLM 앱 기초** 시리즈의 첫 번째 글입니다. OpenAI API로 LLM에게 첫 번째 요청을 보내고, 응답 구조와 기본 파라미터를 이해합니다.

---

바이브코딩을 시작하려면 LLM API가 어떻게 작동하는지 최소한의 이해가 필요합니다. AI에게 "코드 짜줘"라고 할 때 그 AI가 어떻게 동작하는지 전혀 모르면, AI가 틀린 코드를 줬을 때 어디가 문제인지 파악하기 어렵습니다.

바이브코딩으로 AI에게 "OpenAI API 호출 코드 만들어줘"라고 하면 코드가 나옵니다. temperature가 무엇인지, messages 배열이 왜 필요한지, 응답의 어느 부분이 실제 텍스트인지 모르면 코드를 수정할 수 없습니다.

이 글에서는 OpenAI API의 가장 기본적인 호출과 응답 구조를 설명합니다.

> "LLM API를 이해하면 AI가 만든 코드를 검토할 수 있습니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. messages 배열에 role이 왜 필요한가요?
2. temperature와 top_p의 차이가 무엇인가요?
3. max_tokens가 응답에 어떤 영향을 주나요?
4. API 응답에서 실제 텍스트를 어떻게 추출하나요?
5. API 키를 코드에 직접 쓰면 안 되는 이유가 무엇인가요?

---

## 첫 번째 API 호출

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "당신은 도움이 되는 AI 어시스턴트입니다."},
        {"role": "user", "content": "Python이란 무엇인가요?"},
    ],
    temperature=0.7,
    max_tokens=500,
)

# 응답 텍스트 추출
text = response.choices[0].message.content
print(text)
```

## 응답 구조 이해

```python
# 응답 객체 주요 필드
print(response.model)           # 사용된 모델
print(response.usage.prompt_tokens)     # 입력 토큰 수
print(response.usage.completion_tokens) # 출력 토큰 수
print(response.usage.total_tokens)      # 합계
print(response.choices[0].finish_reason) # stop | length | tool_calls
```

## 파라미터 이해

```python
# temperature: 0(결정적) ~ 2(창의적)
# 코드 생성에는 낮은 값, 창의적 글쓰기에는 높은 값

# max_tokens: 응답 최대 토큰 수
# 짧은 답변: 100~200, 긴 설명: 1000+

# n: 응답 후보 수 (기본 1)
response_multi = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "한 문장으로 Python을 설명해줘"}],
    n=3,  # 3개 후보 생성
    temperature=1.0,
)
for choice in response_multi.choices:
    print(choice.message.content)
```

## 환경변수로 API 키 관리

```python
# .env 파일
# OPENAI_API_KEY=sk-...

from dotenv import load_dotenv
load_dotenv()

import os
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
```

---

## Before / After

| 항목 | Before (하드코딩 API 키) | After (환경변수) |
|------|------------------------|----------------|
| 보안 | API 키 노출 위험 | 환경변수 격리 |
| 응답 처리 | content 위치 불명 | choices[0].message.content |
| 토큰 추적 | 없음 | response.usage |
| 파라미터 이해 | 기본값 그대로 | 용도별 설정 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| API 키 코드에 직접 작성 | 보안 위험 | os.getenv 사용 |
| response.content 접근 | AttributeError | choices[0].message.content |
| temperature=2 이상 | 예측 불가 응답 | 0~2 범위 내 사용 |
| finish_reason 미확인 | 잘린 응답 모름 | length 시 max_tokens 증가 |

---

## AI 활용 팁

```
OpenAI API로 간단한 QA 함수를 만들어줘.
API 키는 환경변수에서 로드하고, messages에 system과 user 역할을 분리해줘.
응답에서 텍스트, 토큰 수, finish_reason을 추출해서 반환해줘.
temperature와 max_tokens를 파라미터로 받을 수 있게 해줘.
```

---

## 체크리스트

- [ ] OPENAI_API_KEY 환경변수 설정(.env)
- [ ] python-dotenv 또는 os.getenv 사용
- [ ] messages에 system + user 역할 분리
- [ ] choices[0].message.content로 텍스트 추출
- [ ] response.usage로 토큰 수 확인
- [ ] finish_reason 확인(length면 max_tokens 증가)

---

## 처음 질문으로 돌아가기

"API 키만 있으면 바로 쓸 수 있는 거 아닌가요?" — 기술적으로는 맞습니다. 하지만 messages 구조, temperature 의미, 응답 파싱 방법을 모르면 AI가 만든 코드를 검토할 수 없습니다. 이 글의 내용이 바이브코딩의 최소 기반입니다.

---

## 정리

- API 키는 환경변수로 관리하고 코드에 직접 쓰지 않는다
- messages에 system(역할 정의)과 user(요청) 역할을 분리한다
- 응답 텍스트는 `choices[0].message.content`에서 추출한다
- `response.usage`로 토큰 사용량을 추적한다

---

## 참고 자료

- [OpenAI API 시작 가이드](https://platform.openai.com/docs/quickstart)
- [Chat Completions API](https://platform.openai.com/docs/api-reference/chat)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 첫 번째 API 호출
- 응답 구조 이해
- 파라미터 이해
- 환경변수로 API 키 관리
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLM, OpenAI, Prompt Engineering, Python
