---
title: Memory와 State
series: ai-agent-101
episode: 5
language: ko
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Memory
- State Management
- Context Window
last_reviewed: '2026-05-02'
---

# Memory와 State

> AI Agent 101 시리즈 (5/10)

Agent가 여러 단계를 거쳐 작업을 수행하려면 이전 단계에서 무엇을 했는지 기억해야 합니다. 이것이 Memory입니다. 단기 메모리는 현재 대화 세션 동안 유지되고, 장기 메모리는 세션이 끝나도 유지됩니다.

하지만 모델의 컨텍스트 윈도우는 제한적입니다. 모든 대화 기록을 계속 포함할 수 없으므로, 중요한 정보만 선택해서 유지하거나, 외부 저장소(벡터 DB, 일반 DB)를 활용해야 합니다.

이번 글에서는 단기 메모리와 장기 메모리의 차이, 대화 기록 관리 전략, 컨텍스트 윈도우 관리 방법, 외부 메모리 저장소 활용 패턴을 다룹니다.

---

## 단기 메모리 vs 장기 메모리

[TBD placeholder]

## 대화 기록 관리

[TBD placeholder]

## 컨텍스트 윈도우 관리

[TBD placeholder]

## 외부 메모리 저장소

[TBD placeholder]

## 핵심 요약

- Agent는 Memory를 통해 이전 행동과 결과를 기억하고 다음 행동을 결정합니다.
- 컨텍스트 윈도우 제한 때문에 중요한 정보만 선택해서 유지해야 합니다.
- 장기 메모리가 필요한 경우 외부 저장소(벡터 DB, 일반 DB)를 활용합니다.

---

<!-- toc:begin -->
## AI Agent 101 시리즈

- AI Agent란 무엇인가? (예정)
- 컨텍스트 엔지니어링 (예정)
- Tool Use 기초 (예정)
- Agent Workflow 설계 (예정)
- **Memory와 State (현재 글)**
- Multi-Agent 시스템 (예정)
- Agent 평가 (예정)
- 에러 처리와 안정성 (예정)
- 운영 (예정)
- 첫 Agent 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [TBD]

Tags: AI Agent, Memory, State Management, Context Window
