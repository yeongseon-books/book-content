---
title: "바이브코딩을 위한 LLM 앱 기초 (3/6): 프롬프트 엔지니어링 기초 — System·User·Assistant 역할"
series: llm-app-foundations-101
episode: 3
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM
- Prompt Engineering
- OpenAI
- Python
---

# 바이브코딩을 위한 LLM 앱 기초 (3/6): 프롬프트 엔지니어링 기초 — System·User·Assistant 역할

이 글은 **바이브코딩을 위한 LLM 앱 기초** 시리즈의 세 번째 글입니다. system, user, assistant 세 가지 역할의 차이와 효과적인 프롬프트 작성 기초를 다룹니다.

---

API를 호출할 수 있습니다. 그런데 같은 질문을 해도 프롬프트에 따라 응답 품질이 크게 다릅니다. 바이브코딩에서 AI에게 요청할 때도 마찬가지입니다. "코드 짜줘"와 "Python 3.10, type hints 포함, docstring 포함한 함수 작성해줘"는 다른 결과를 냅니다.

바이브코딩으로 AI에게 "프롬프트 만들어줘"라고 하면 프롬프트가 나옵니다. 하지만 왜 system 역할이 필요한지, 명확한 지시가 왜 더 좋은 응답을 만드는지 이해하면 스스로 더 좋은 프롬프트를 쓸 수 있습니다.

> "프롬프트는 AI에게 주는 일의 명세서입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. system 역할과 user 역할의 차이가 무엇인가요?
2. system 프롬프트에 어떤 내용을 넣어야 하나요?
3. 구체적인 프롬프트가 왜 더 좋은 결과를 만드나요?
4. 형식 지정(출력 형식, 길이)을 어떻게 프롬프트에 포함하나요?
5. 프롬프트의 품질을 어떻게 평가하나요?

---

## 세 가지 역할

```python
messages = [
    {
        "role": "system",
        "content": "당신은 Python 전문가입니다. 항상 type hints와 docstring을 포함하고, 코드 예시를 제공하세요.",
    },
    {
        "role": "user",
        "content": "리스트에서 중복을 제거하는 함수를 만들어줘",
    },
    # assistant는 이전 AI 응답(대화 기록)
    # {"role": "assistant", "content": "이전 응답..."},
]
```

## System 프롬프트 설계

```python
SYSTEM_PROMPTS = {
    "코드_전문가": """당신은 Python 전문가입니다.
규칙:
- 항상 type hints를 포함하세요
- 모든 함수에 docstring을 작성하세요
- 예외 처리를 포함하세요
- 코드 블록에는 ```python을 사용하세요""",

    "번역가": """당신은 한국어-영어 번역 전문가입니다.
번역 시:
- 자연스러운 표현을 우선하세요
- 원문의 뉘앙스를 보존하세요
- 번역만 제공하고, 설명은 최소화하세요""",
}
```

## 명확한 지시 vs 모호한 지시

```python
# 나쁜 프롬프트
bad = "코드 만들어줘"

# 좋은 프롬프트
good = """다음 조건으로 Python 함수를 작성해주세요:
- 기능: 리스트에서 중복 제거 (순서 보존)
- 입력: list[Any]
- 출력: list[Any]
- type hints 포함
- docstring 포함
- 시간복잡도: O(n)"""
```

## 형식 지정

```python
def create_structured_prompt(task: str, output_format: str, constraints: list[str]) -> str:
    constraints_text = "\n".join(f"- {c}" for c in constraints)
    return f"""작업: {task}

제약 조건:
{constraints_text}

출력 형식:
{output_format}

위 조건을 모두 충족하는 응답을 제공하세요."""
```

---

## Before / After

| 항목 | Before (모호한 프롬프트) | After (명확한 프롬프트) |
|------|----------------------|----------------------|
| 응답 형식 | 매번 다름 | 지정한 형식 유지 |
| 코드 품질 | 기본 수준 | type hints + docstring |
| 재현성 | 낮음 | 동일 조건 = 일관된 결과 |
| 디버깅 | 어디가 문제인지 불명 | 제약 조건별 확인 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| system 프롬프트 없음 | 기본 모드 응답 | 역할과 규칙 명시 |
| 모호한 지시 | 예측 불가 응답 | 구체적인 조건 나열 |
| 출력 형식 미지정 | 형식 불일치 | 형식 예시 포함 |
| 제약 조건 너무 많음 | 일부 무시 | 3~5개로 제한 |

---

## AI 활용 팁

```
Python 코드 생성 전문 AI를 위한 system 프롬프트를 만들어줘.
항상 type hints, docstring, 예외 처리를 포함하게 해줘.
사용자 요청을 구조화된 프롬프트로 변환하는 create_structured_prompt 함수도 만들어줘.
```

---

## 체크리스트

- [ ] system 역할에 AI의 역할과 규칙 정의
- [ ] 구체적인 출력 형식 지정
- [ ] 제약 조건을 명확하게 나열
- [ ] 프롬프트 템플릿 재사용 가능하게 함수화
- [ ] 프롬프트 품질을 응답 비교로 검증
- [ ] 제약 조건 수 3~5개로 제한

---

## 처음 질문으로 돌아가기

"그냥 '코드 만들어줘'라고 하면 안 되나요?" — 간단한 작업에는 됩니다. 하지만 type hints, docstring, 특정 패턴, 특정 라이브러리 버전이 필요하면 명확하게 지정해야 합니다. 명확한 프롬프트가 검토 부담을 줄입니다.

---

## 정리

- system 역할에 AI의 역할과 지켜야 할 규칙을 정의한다
- 구체적인 조건(type hints, docstring, 형식)을 명시하면 일관된 응답이 나온다
- 제약 조건은 3~5개로 제한해서 모두 적용되게 한다
- 프롬프트 템플릿을 함수로 만들어 재사용한다

---

## 참고 자료

- [OpenAI 프롬프트 엔지니어링 가이드](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic 프롬프트 가이드](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 세 가지 역할
- System 프롬프트 설계
- 명확한 지시 vs 모호한 지시
- 형식 지정
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLM, Prompt Engineering, OpenAI, Python
