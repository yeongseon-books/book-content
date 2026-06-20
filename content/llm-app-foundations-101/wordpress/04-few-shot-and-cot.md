---
title: "바이브코딩을 위한 LLM 앱 기초 (4/6): Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기"
series: llm-app-foundations-101
episode: 4
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLM
- Few-shot
- Chain-of-Thought
- Python
---

# 바이브코딩을 위한 LLM 앱 기초 (4/6): Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기

이 글은 **바이브코딩을 위한 LLM 앱 기초** 시리즈의 네 번째 글입니다. Few-shot 프롬프팅과 Chain-of-Thought로 복잡한 작업에서 더 정확한 응답을 유도하는 방법을 다룹니다.

---

기본 프롬프트로는 원하는 형식이 나오지 않을 때가 있습니다. "이 형식으로 출력해줘"라고 설명하는 것보다 예시를 보여주면 더 정확합니다. 그게 Few-shot입니다. 복잡한 문제는 단계적으로 생각하게 하면 더 나은 결과가 나옵니다. 그게 Chain-of-Thought입니다.

바이브코딩에서 AI에게 복잡한 작업을 맡길 때 Few-shot과 CoT를 프롬프트에 포함하면 품질이 올라갑니다. 이 기법들이 왜 효과적인지 이해하면 적절한 상황에서 적용할 수 있습니다.

> "예시를 보여주는 것이 설명하는 것보다 효과적입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. Few-shot 프롬프팅이 Zero-shot보다 나은 상황이 언제인가요?
2. Chain-of-Thought 프롬프팅이 왜 정확도를 높이나요?
3. 예시의 수(shot)를 어떻게 결정하나요?
4. CoT가 효과적이지 않은 상황이 있나요?
5. Few-shot 예시의 품질이 중요한가요?

---

## Zero-shot vs Few-shot

```python
# Zero-shot: 예시 없이
zero_shot = """감정 분류:
텍스트: "오늘 날씨가 정말 좋네요!"
감정:"""

# Few-shot: 예시 포함
few_shot = """감정 분류 (긍정/부정/중립):

예시 1:
텍스트: "이 제품 최고예요!"
감정: 긍정

예시 2:
텍스트: "배송이 너무 늦었어요"
감정: 부정

예시 3:
텍스트: "배송은 어제 도착했습니다"
감정: 중립

텍스트: "오늘 날씨가 정말 좋네요!"
감정:"""
```

## Chain-of-Thought

```python
# 직접 답변
direct = "다음 문제를 풀어주세요: 쇼핑몰에서 30% 할인 상품을 15,000원에 샀습니다. 원래 가격은?"

# Chain-of-Thought
cot = """다음 문제를 단계별로 풀어주세요:
쇼핑몰에서 30% 할인 상품을 15,000원에 샀습니다. 원래 가격은?

단계별 풀이:
1. 15,000원은 원래 가격의 몇 %인지 파악
2. 원래 가격 계산
3. 최종 답 제시"""
```

## Few-shot 예시 구성

```python
def build_few_shot_prompt(
    task_description: str,
    examples: list[dict],  # [{"input": "...", "output": "..."}]
    new_input: str,
) -> str:
    lines = [task_description, ""]
    for i, ex in enumerate(examples, 1):
        lines.append(f"예시 {i}:")
        lines.append(f"입력: {ex['input']}")
        lines.append(f"출력: {ex['output']}")
        lines.append("")
    lines.append(f"입력: {new_input}")
    lines.append("출력:")
    return "\n".join(lines)
```

## CoT 프롬프트 빌더

```python
def build_cot_prompt(problem: str, steps: list[str]) -> str:
    steps_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
    return f"""{problem}

다음 순서로 단계별 풀이를 제시해주세요:
{steps_text}

단계별 풀이:"""
```

---

## Before / After

| 항목 | Before (Zero-shot) | After (Few-shot + CoT) |
|------|-------------------|------------------------|
| 형식 일관성 | 낮음 | 예시로 형식 고정 |
| 복잡한 추론 | 오류 많음 | CoT로 정확도 향상 |
| 분류 정확도 | 불안정 | Few-shot으로 개선 |
| 디버깅 | 어디가 틀렸는지 불명 | 단계별 추론 추적 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 편향된 예시 | 특정 클래스 과분류 | 균형 잡힌 예시 선택 |
| 예시 너무 많음 | 토큰 낭비 | 3~5개 예시 권장 |
| CoT 없이 복잡한 추론 | 오류 빈번 | "단계별 풀이" 요청 |
| 예시 품질 낮음 | 잘못된 패턴 학습 | 검증된 예시 사용 |

---

## AI 활용 팁

```
텍스트 감정 분류를 위한 Few-shot 프롬프트를 만들어줘.
긍정/부정/중립 예시를 각 2개씩 포함하고, 새 텍스트에 같은 형식으로 분류해줘.
복잡한 계산 문제에는 Chain-of-Thought 프롬프트를 사용해서 단계별로 풀게 해줘.
```

---

## 체크리스트

- [ ] Few-shot 예시 균형 확인(클래스별 동일 수)
- [ ] 예시 수 3~5개로 제한
- [ ] build_few_shot_prompt 함수화
- [ ] 복잡한 추론에 CoT 적용
- [ ] Few-shot vs Zero-shot 성능 비교 테스트
- [ ] 예시 품질 검증

---

## 처음 질문으로 돌아가기

"프롬프트에 예시를 넣으면 더 좋아지나요?" — 특히 형식이 중요하거나 엣지 케이스가 있을 때 효과적입니다. "JSON으로 출력해줘"보다 JSON 예시를 하나 보여주는 게 더 일관된 결과를 냅니다. 복잡한 추론 문제는 CoT로 단계별 사고를 유도하면 정확도가 올라갑니다.

---

## 정리

- Few-shot은 예시로 출력 형식과 패턴을 보여준다
- CoT는 "단계별로 풀어줘"로 복잡한 추론 정확도를 높인다
- 예시는 균형 잡히고 검증된 것으로 3~5개 사용한다
- 단순한 작업에는 Zero-shot, 복잡하거나 형식이 중요하면 Few-shot

---

## 참고 자료

- [Chain-of-Thought 논문](https://arxiv.org/abs/2201.11903)
- [OpenAI Few-shot 가이드](https://platform.openai.com/docs/guides/prompt-engineering#tactic-provide-examples)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- Zero-shot vs Few-shot
- Chain-of-Thought
- Few-shot 예시 구성
- CoT 프롬프트 빌더
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLM, Few-shot, Chain-of-Thought, Python
