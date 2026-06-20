---
title: "바이브코딩을 위한 LLM API 운영 (1/6): 구조화 출력 — JSON 모드와 응답 스키마"
series: llm-api-production-101
episode: 1
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM
- OpenAI
- Structured Output
- Python
---

# 바이브코딩을 위한 LLM API 운영 (1/6): 구조화 출력 — JSON 모드와 응답 스키마

이 글은 **바이브코딩을 위한 LLM API 운영** 시리즈의 첫 번째 글입니다. LLM 응답을 JSON Schema로 강제하고 안정적으로 파싱하는 방법을 다룹니다.

---

LLM에게 JSON으로 답해달라고 프롬프트에 써도 가끔 다른 형식이 나옵니다. "반드시 JSON으로 답하세요"라고 해도 모델이 추가 설명을 붙이거나, 백틱으로 감싸거나, 필드를 빠뜨립니다. 그 JSON을 파싱하는 코드가 실패하면 서비스가 멈춥니다.

바이브코딩으로 AI에게 "JSON 형식으로 LLM 응답 받아줘"라고 하면 프롬프트에 JSON 요청을 추가하는 코드가 나옵니다. OpenAI의 Structured Output API와 JSON Schema를 모르면, 프롬프트 의존 파싱은 언제든 깨질 수 있습니다.

이 글에서는 OpenAI JSON 모드와 response_format을 사용해 안정적으로 구조화 출력을 받는 방법을 다룹니다.

> "프롬프트로 JSON을 요청하는 것과 API로 강제하는 것은 신뢰도가 다릅니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. OpenAI JSON 모드와 response_format의 차이가 무엇인가요?
2. Pydantic 모델을 JSON Schema로 변환하는 방법이 있나요?
3. LLM 응답 파싱이 실패했을 때 어떻게 처리하나요?
4. 중첩된 객체를 JSON Schema로 표현할 수 있나요?
5. 구조화 출력이 항상 유효한 JSON을 보장하나요?

---

## JSON 모드

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "JSON으로만 응답하세요."},
        {"role": "user", "content": "서울의 날씨를 JSON으로 알려주세요."},
    ],
    response_format={"type": "json_object"},
)

import json
result = json.loads(response.choices[0].message.content)
```

## Pydantic 모델로 Schema 정의

```python
from pydantic import BaseModel
from openai import OpenAI

class WeatherResponse(BaseModel):
    city: str
    temperature: float
    condition: str
    humidity: int

client = OpenAI()

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "서울 날씨를 알려주세요."},
    ],
    response_format=WeatherResponse,
)

weather = response.choices[0].message.parsed
print(weather.city, weather.temperature)
```

## 안전한 파싱

```python
def safe_parse_json(content: str, model_class) -> tuple[bool, any]:
    try:
        data = json.loads(content)
        validated = model_class(**data)
        return True, validated
    except (json.JSONDecodeError, ValueError) as e:
        return False, str(e)
```

## 스키마 검증

```python
import jsonschema

EXPECTED_SCHEMA = {
    "type": "object",
    "required": ["city", "temperature"],
    "properties": {
        "city": {"type": "string"},
        "temperature": {"type": "number"},
    }
}

def validate_response(data: dict) -> bool:
    try:
        jsonschema.validate(data, EXPECTED_SCHEMA)
        return True
    except jsonschema.ValidationError:
        return False
```

---

## Before / After

| 항목 | Before (프롬프트 의존) | After (Structured Output) |
|------|----------------------|---------------------------|
| JSON 보장 | 불확실 | API 레벨 강제 |
| 파싱 실패 | 서비스 중단 | safe_parse_json |
| 스키마 검증 | 없음 | Pydantic 자동 검증 |
| 중첩 구조 | 프롬프트로만 | 스키마로 명시 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 프롬프트에만 JSON 요청 | 가끔 실패 | response_format 사용 |
| 파싱 오류 미처리 | 500 오류 | safe_parse_json |
| 필수 필드 미검증 | KeyError | Pydantic required 설정 |
| 백틱 감싸기 | json.loads 오류 | strip() 전처리 |

---

## AI 활용 팁

```
OpenAI API로 구조화 출력을 받는 코드를 만들어줘.
Pydantic 모델로 응답 스키마를 정의하고, client.beta.chat.completions.parse로 자동 파싱해줘.
파싱 실패 시 safe_parse_json으로 오류를 처리해줘.
jsonschema로 필수 필드 존재 여부를 검증하는 함수도 만들어줘.
```

---

## 체크리스트

- [ ] Pydantic 모델로 응답 스키마 정의
- [ ] client.beta.chat.completions.parse 사용
- [ ] safe_parse_json 오류 처리
- [ ] jsonschema 필드 검증
- [ ] 필수 필드 누락 테스트
- [ ] 중첩 객체 스키마 테스트

---

## 처음 질문으로 돌아가기

"프롬프트에 'JSON으로 답해줘'라고 써도 가끔 다른 형식이 나와요" — response_format API를 쓰면 모델이 JSON 외의 형식을 반환하지 못합니다. Pydantic 모델로 스키마를 정의하면 자동으로 파싱하고 검증합니다.

---

## 정리

- response_format={"type": "json_object"}로 JSON 모드를 강제한다
- Pydantic 모델 + client.beta.chat.completions.parse로 자동 파싱한다
- safe_parse_json으로 파싱 실패를 안전하게 처리한다
- jsonschema로 필수 필드 존재를 검증한다

---

## 참고 자료

- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [Pydantic 공식 문서](https://docs.pydantic.dev/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- JSON 모드
- Pydantic 모델로 Schema 정의
- 안전한 파싱
- 스키마 검증
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLM, OpenAI, Structured Output, Python
