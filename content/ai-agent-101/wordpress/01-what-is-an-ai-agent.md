---
title: "바이브코딩을 위한 AI Agent 기초 (1/10): AI 에이전트란 무엇인가"
series: ai-agent-101
episode: 1
language: ko
tags:
- AI Agent
- 바이브코딩
- Vibe Coding
- Observe-Think-Act
- ReAct
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI Agent 기초 (1/10): AI 에이전트란 무엇인가

이 글은 **바이브코딩을 위한 AI Agent 기초** 시리즈의 첫 번째 글입니다. 총 10편으로 구성되며, AI 에이전트의 기초부터 프로덕션 운영까지 바이브코딩 관점에서 다룹니다.

---

바이브코딩으로 AI를 다루다 보면 어느 순간 "ChatGPT에 물어보는 것"과 "에이전트를 만드는 것"이 완전히 다른 세계라는 걸 느끼게 됩니다. 챗봇은 한 번 묻고 한 번 답받는 구조지만, 에이전트는 스스로 상황을 판단하고, 도구를 쓰고, 결과를 확인하고, 다음 행동을 결정합니다.

처음 에이전트를 접할 때 많은 분이 "GPT에 프롬프트 넣으면 되는 거 아닌가요?"라고 묻습니다. 그 질문에서 시작해 봅시다. 에이전트는 단순한 프롬프트 실행기가 아닙니다. 에이전트는 **목표를 받아 스스로 행동을 계획하고, 환경과 상호작용하며, 결과를 관찰해 다음 단계를 결정**하는 시스템입니다.

바이브코딩 관점에서 AI 에이전트를 이해하면, 나중에 더 복잡한 멀티 에이전트 시스템이나 프로덕션 운영을 다룰 때 기반이 됩니다. 이 첫 번째 글에서는 에이전트의 핵심 개념, 챗봇과의 차이, 그리고 에이전트가 어떤 방식으로 동작하는지를 살펴봅니다.

> "에이전트는 프롬프트를 실행하는 게 아니라, 목표를 향해 환경과 상호작용하는 루프를 돌립니다."

## 이 글에서 다룰 질문

1. AI 에이전트와 챗봇은 어떻게 다른가요?
2. Observe → Think → Act → Check 루프는 왜 중요한가요?
3. ReAct 패턴은 어떤 문제를 해결하나요?
4. 에이전트가 무한 루프에 빠지지 않으려면 어떻게 해야 하나요?
5. 바이브코딩에서 에이전트를 처음 만들 때 무엇부터 시작해야 하나요?

---

## 챗봇 vs 에이전트: 바이브코딩 관점의 차이

| 구분 | 챗봇 | 에이전트 |
|------|------|----------|
| 상호작용 | 단발성 요청-응답 | 루프 기반 지속 실행 |
| 도구 사용 | 없음 | 검색, 계산, API 호출 등 |
| 상태 관리 | 대화 히스토리만 | 실행 상태, 계획, 메모리 |
| 종료 조건 | 응답 생성 완료 | 목표 달성 또는 포기 판단 |

바이브코딩에서 챗봇은 "질문하면 답해주는 것"입니다. 에이전트는 "목표를 주면 알아서 해결해오는 것"에 가깝습니다. 이 차이가 설계 방식 전체를 바꿉니다.

## Observe → Think → Act → Check: 에이전트의 기본 루프

에이전트는 다음 4단계 루프로 동작합니다.

**Observe**: 현재 환경 상태를 관찰합니다. 사용자 요청, 이전 도구 실행 결과, 현재 메모리 내용이 여기에 해당합니다.

**Think**: 관찰 내용을 바탕으로 다음에 무엇을 해야 할지 추론합니다. LLM이 이 역할을 담당합니다.

**Act**: 결정한 행동을 실행합니다. 도구 호출, API 요청, 계산 등이 여기에 포함됩니다.

**Check**: 실행 결과를 확인합니다. 목표가 달성됐는지, 오류가 있는지, 다음 루프가 필요한지 판단합니다.

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AgentState:
    goal: str
    steps: list[dict] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    is_done: bool = False
    result: Any = None
```

## Before / After: 에이전트 도입 전후

**Before (단순 LLM 호출)**
```python
response = llm.chat("2024년 삼성전자 주가 최고점을 알려줘")
# LLM이 학습 데이터 기준으로 답변 → 최신 정보 없음, 오류 가능
```

**After (에이전트 사용)**
```python
agent = ResearchAgent(tools=[web_search, calculator])
result = agent.run("2024년 삼성전자 주가 최고점을 찾아서 달러로 환산해줘")
# 1) 웹 검색으로 최신 주가 조회
# 2) 환율 API로 달러 환산
# 3) 결과 종합 후 응답
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 종료 조건 없이 루프 실행 | 무한 루프, 비용 폭발 | max_steps 설정, 명확한 종료 조건 |
| 모든 것을 단일 프롬프트로 처리 | 복잡한 작업에서 오류 | 단계별 분리, 각 단계 검증 |
| 에이전트 상태 추적 안 함 | 디버깅 불가 | AgentState로 모든 단계 기록 |
| 도구 오류 미처리 | 에이전트 중단 | 오류를 관찰값으로 처리 |

## AI 팁

ReAct(Reasoning + Acting) 패턴을 쓰면 에이전트가 생각과 행동을 교대로 기록해 추적과 디버깅이 쉬워집니다. 프롬프트에 "Thought: / Action: / Observation:" 형식을 명시하면 LLM이 이 패턴을 따르게 됩니다.

```
Thought: 삼성전자 주가를 검색해야 한다
Action: web_search("삼성전자 2024 주가 최고점")
Observation: 2024년 7월 8만8천원 기록
Thought: 달러 환산이 필요하다
Action: calculator("88000 / 1350")
Observation: 약 65.19달러
Final Answer: 2024년 삼성전자 주가 최고점은 88,000원(약 65.19달러)입니다.
```

## 체크리스트

- [ ] 에이전트와 챗봇의 차이를 설명할 수 있다
- [ ] Observe → Think → Act → Check 루프를 코드로 표현할 수 있다
- [ ] AgentState로 실행 상태를 추적하는 방법을 안다
- [ ] max_steps 등 종료 조건을 설정하는 이유를 안다
- [ ] ReAct 패턴의 Thought/Action/Observation 구조를 이해한다

## 처음 질문으로 돌아가기

**AI 에이전트와 챗봇은 어떻게 다른가요?** 챗봇은 단발성 요청-응답이지만 에이전트는 목표를 향해 루프를 돌리며 도구를 사용하고 상태를 관리합니다.

**Observe → Think → Act → Check 루프는 왜 중요한가요?** 이 루프가 에이전트의 자율적 실행 능력의 기반이기 때문입니다. 각 단계가 명확히 분리돼야 디버깅과 개선이 가능합니다.

**ReAct 패턴은 어떤 문제를 해결하나요?** 에이전트의 추론 과정을 명시적으로 기록해 투명성을 높이고, 오류 발생 시 어떤 단계에서 문제가 생겼는지 파악하기 쉽게 합니다.

**에이전트가 무한 루프에 빠지지 않으려면?** max_steps를 설정하고, 각 루프에서 목표 달성 여부를 명시적으로 확인하는 종료 조건을 코드에 포함해야 합니다.

**바이브코딩에서 에이전트를 처음 만들 때?** AgentState부터 정의하고, 하나의 도구만 연결해 단순한 루프를 먼저 완성하세요. 도구를 늘리는 것은 그 다음입니다.

## 정리

AI 에이전트는 챗봇과 근본적으로 다릅니다. 에이전트는 Observe → Think → Act → Check 루프를 통해 목표를 향해 자율적으로 실행하며, 도구 사용과 상태 관리가 핵심입니다. 바이브코딩에서 에이전트를 처음 다룰 때는 이 루프 구조와 종료 조건 설계부터 시작하는 것이 가장 안전합니다.

다음 글에서는 에이전트에게 올바른 맥락을 전달하는 **컨텍스트 엔지니어링**을 다룹니다.

## 참고 자료

- [ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2022)](https://arxiv.org/abs/2210.03629)
- [AI Agent 기초 원문 시리즈](../ko/01-what-is-an-ai-agent.md)

---

<!-- toc:begin -->
## 시리즈 목차

1. **바이브코딩을 위한 AI Agent 기초 (1/10): AI 에이전트란 무엇인가 (현재 글)**
2. [바이브코딩을 위한 AI Agent 기초 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
3. [바이브코딩을 위한 AI Agent 기초 (3/10): 도구 사용 기초](./03-tool-use-fundamentals.md)
4. [바이브코딩을 위한 AI Agent 기초 (4/10): 에이전트 워크플로우 설계](./04-agent-workflow-design.md)
5. [바이브코딩을 위한 AI Agent 기초 (5/10): 메모리와 상태 관리](./05-memory-and-state.md)
6. [바이브코딩을 위한 AI Agent 기초 (6/10): 멀티 에이전트 시스템](./06-multi-agent-systems.md)
7. [바이브코딩을 위한 AI Agent 기초 (7/10): 에이전트 평가](./07-agent-evaluation.md)
8. [바이브코딩을 위한 AI Agent 기초 (8/10): 오류 처리와 신뢰성](./08-error-handling-reliability.md)
9. [바이브코딩을 위한 AI Agent 기초 (9/10): 프로덕션 운영](./09-production-operations.md)
10. [바이브코딩을 위한 AI Agent 기초 (10/10): 첫 번째 에이전트 만들기](./10-building-first-agent.md)
<!-- toc:end -->

Tags: AI Agent, 바이브코딩, Vibe Coding, Observe-Think-Act, ReAct
