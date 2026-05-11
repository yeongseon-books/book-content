---
title: Agent Workflow 설계
series: ai-agent-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Workflow
- Planning
- Task Decomposition
last_reviewed: '2026-05-02'
seo_description: 복잡한 작업을 수행하려면 Agent는 작업을 단계로 나누고, 각 단계를 순서대로 실행하며, 결과를 검증해야 합니다.
---

# Agent Workflow 설계

> AI Agent 101 시리즈 (4/10)

복잡한 작업을 수행하려면 Agent는 작업을 단계로 나누고, 각 단계를 순서대로 실행하며, 결과를 검증해야 합니다. 이 과정을 Workflow라고 합니다. 단순히 도구를 호출하는 것이 아니라, "어떤 순서로 무엇을 해야 목표를 달성할 수 있는지"를 설계하는 것입니다.

대표적인 Workflow 패턴으로는 ReAct(Reasoning + Acting), Plan-and-Execute, Reflexion이 있습니다. 각 패턴은 작업의 특성에 따라 장단점이 있으며, Agent 설계자는 작업 유형에 맞는 패턴을 선택해야 합니다.

이번 글에서는 주요 Workflow 패턴, 작업 분해 전략, 상태 관리 방법, 그리고 Workflow 설계 시 고려해야 할 요소를 다룹니다.

---

## 주요 Workflow 패턴

Agent가 복잡한 작업을 수행하려면 체계적인 Workflow가 필요합니다. 대표적인 패턴을 살펴봅니다.

### ReAct (Reasoning + Acting)

**ReAct**는 추론(Reasoning)과 행동(Acting)을 반복하는 패턴입니다. Agent가 생각하고, 도구를 사용하고, 결과를 관찰하는 과정을 번갈아 수행합니다.

```python
from typing import Dict, Any, List
import openai

def react_agent(user_query: str, tools: List[Dict], max_steps: int = 10) -> str:
    """ReAct 패턴: Thought → Action → Observation 반복"""
    
    messages = [
        {"role": "system", "content": """당신은 문제를 단계적으로 해결하는 Agent입니다.
        
        각 단계에서:
        1. Thought: 다음에 무엇을 해야 할지 생각
        2. Action: 도구를 사용하여 정보 수집
        3. Observation: 결과를 관찰하고 다음 단계 계획
        
        목표를 달성하면 "Final Answer:"로 시작하는 답변을 제공하세요."""},
        {"role": "user", "content": user_query}
    ]
    
    for step in range(max_steps):
        # LLM에게 다음 행동 결정 요청
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # 최종 답변인 경우
        if assistant_message.content and "Final Answer:" in assistant_message.content:
            return assistant_message.content.replace("Final Answer:", "").strip()
        
        # 도구 호출인 경우
        if assistant_message.tool_calls:
            messages.append(assistant_message)
            
            # 각 도구 실행
            for tool_call in assistant_message.tool_calls:
                result = execute_tool(tool_call.function.name, tool_call.function.arguments)
                
                # Observation 추가
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": f"Observation: {result}"
                })
        else:
            # 도구 호출도 최종 답변도 아닌 경우
            messages.append(assistant_message)
    
    return "Max steps reached without solution."
```

**장점**:
- 추론 과정이 명시적으로 드러남 (디버깅 용이)
- 중간 결과를 바탕으로 계획 수정 가능
- 단계별 검증 가능

**단점**:
- 매 단계마다 LLM 호출 (느림, 비용 높음)
- 복잡한 작업에서 계획 없이 시행착오 가능

**적합한 작업**:
- 정보 수집 후 의사결정
- 중간 결과에 따라 전략이 바뀌는 작업
- 예: "경쟁사 분석 후 마케팅 전략 수립"

### Plan-and-Execute

**Plan-and-Execute**는 먼저 전체 계획을 세운 뒤, 계획을 순서대로 실행하는 패턴입니다.

```python
def plan_and_execute_agent(user_query: str, tools: List[Dict]) -> str:
    """Plan-and-Execute 패턴: 계획 수립 → 순차 실행"""
    
    # 1단계: 계획 수립
    plan_prompt = f"""
    작업: {user_query}
    
    이 작업을 완료하기 위한 단계별 계획을 세우세요.
    각 단계는 명확한 목표와 필요한 도구를 포함해야 합니다.
    
    형식:
    1. [단계 설명] - 도구: [도구 이름]
    2. [단계 설명] - 도구: [도구 이름]
    ...
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": plan_prompt}]
    )
    
    plan = response.choices[0].message.content
    print(f"계획:\n{plan}\n")
    
    # 2단계: 계획 실행
    steps = parse_plan(plan)  # "1. 단계 설명 - 도구: 도구명" → 구조화
    
    results = []
    for idx, step in enumerate(steps):
        print(f"[단계 {idx + 1}] {step['description']}")
        
        # 도구 실행
        tool_result = execute_tool(step["tool"], step["params"])
        results.append({
            "step": idx + 1,
            "description": step["description"],
            "result": tool_result
        })
        
        print(f"결과: {tool_result}\n")
    
    # 3단계: 최종 답변 생성
    summary_prompt = f"""
    작업: {user_query}
    
    실행한 단계와 결과:
    {format_results(results)}
    
    위 결과를 바탕으로 사용자 질문에 답변하세요.
    """
    
    final_response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    
    return final_response.choices[0].message.content
```

**장점**:
- 전체 흐름이 명확함 (계획 검토 가능)
- 병렬 실행 가능한 단계 식별 용이
- 진행 상황 추적 간편

**단점**:
- 초기 계획이 잘못되면 전체 실패
- 중간 결과에 따른 계획 수정 어려움
- 계획 수립에 시간 소요

**적합한 작업**:
- 요구사항이 명확한 작업
- 단계가 예측 가능한 작업
- 예: "데이터 수집 → 분석 → 보고서 작성"

### Reflexion

**Reflexion**은 실행 후 결과를 평가하고, 실패 시 반성(Reflection)하여 계획을 수정하는 패턴입니다.

```python
def reflexion_agent(user_query: str, tools: List[Dict], max_retries: int = 3) -> str:
    """Reflexion 패턴: 실행 → 평가 → 반성 → 재시도"""
    
    reflections = []
    
    for attempt in range(max_retries):
        print(f"\n=== 시도 {attempt + 1} ===")
        
        # 이전 반성 내용을 컨텍스트에 포함
        context = "\n".join([f"반성 {i+1}: {r}" for i, r in enumerate(reflections)])
        
        prompt = f"""
        작업: {user_query}
        
        이전 시도에서 배운 점:
        {context if context else "없음 (첫 시도)"}
        
        작업을 수행하세요.
        """
        
        # 작업 실행
        result = execute_task(prompt, tools)
        
        # 결과 평가
        evaluation = evaluate_result(result, user_query)
        
        if evaluation["success"]:
            return result
        
        # 실패 시 반성
        reflection_prompt = f"""
        작업: {user_query}
        시도한 방법: {result}
        실패 원인: {evaluation['reason']}
        
        무엇이 잘못되었고, 다음 시도에서 어떻게 개선해야 하는지 반성하세요.
        """
        
        reflection_response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": reflection_prompt}]
        )
        
        reflection = reflection_response.choices[0].message.content
        reflections.append(reflection)
        
        print(f"반성: {reflection}")
    
    return "Max retries reached without success."
```

**장점**:
- 실패로부터 학습하여 개선
- 복잡한 문제에 대한 적응력
- 사람의 문제 해결 과정과 유사

**단점**:
- 여러 번 재시도 (시간 및 비용)
- 평가 기준이 불명확하면 효과 저하
- 무한 루프 가능성

**적합한 작업**:
- 정답이 명확하지 않은 창의적 작업
- 시행착오가 필요한 작업
- 예: "코드 작성 및 디버깅", "복잡한 문제 해결"

### 패턴 비교

| 패턴 | 실행 방식 | 장점 | 단점 | 적합한 작업 |
|------|----------|------|------|-------------|
| ReAct | 단계별 추론 + 실행 | 투명성, 유연성 | 느림, 비용 | 정보 수집 후 의사결정 |
| Plan-and-Execute | 계획 수립 후 실행 | 명확성, 병렬화 | 경직성 | 예측 가능한 작업 |
| Reflexion | 실행 → 평가 → 반성 | 학습, 적응력 | 재시도 비용 | 창의적, 시행착오 |

실제 프로덕션에서는 이들을 조합하여 사용하는 경우가 많습니다. 예를 들어, Plan-and-Execute로 큰 틀을 잡고, 각 단계는 ReAct로 실행하며, 실패 시 Reflexion으로 재시도하는 하이브리드 접근이 효과적입니다.

## 작업 분해 전략

복잡한 작업을 작은 단계로 나누는 것이 Workflow 설계의 핵심입니다. 효과적인 분해 전략을 살펴봅니다.

### Top-Down 분해

큰 목표를 하위 목표로 계층적으로 나눕니다.

```python
def decompose_task_topdown(task: str) -> List[Dict[str, Any]]:
    """Top-Down 방식 작업 분해"""
    
    prompt = f"""
    작업: {task}
    
    이 작업을 완료하기 위한 주요 하위 작업들을 나열하세요.
    각 하위 작업은 독립적으로 실행 가능해야 합니다.
    
    형식:
    1. [하위 작업 1]
       - 목표: [구체적 목표]
       - 필요 도구: [도구 목록]
    2. [하위 작업 2]
       ...
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 응답 파싱
    subtasks = parse_subtasks(response.choices[0].message.content)
    
    # 각 하위 작업을 재귀적으로 분해
    for subtask in subtasks:
        if is_complex(subtask):
            subtask["children"] = decompose_task_topdown(subtask["description"])
    
    return subtasks
```

**예시: "경쟁사 분석 보고서 작성"**
1. 경쟁사 목록 수집
   - 1.1 업계 데이터베이스 검색
   - 1.2 뉴스 기사 분석
2. 각 경쟁사 정보 수집
   - 2.1 웹사이트 크롤링
   - 2.2 재무 정보 조회
3. 분석 및 보고서 작성
   - 3.1 데이터 시각화
   - 3.2 인사이트 도출
   - 3.3 문서 생성

### Bottom-Up 분해

사용 가능한 도구를 기반으로 가능한 단계를 조합합니다.

```python
def decompose_task_bottomup(task: str, available_tools: List[str]) -> List[str]:
    """Bottom-Up 방식: 도구 기반 작업 분해"""
    
    prompt = f"""
    작업: {task}
    
    사용 가능한 도구:
    {', '.join(available_tools)}
    
    위 도구들을 조합하여 작업을 완료하는 단계를 설계하세요.
    각 단계는 하나의 도구를 사용해야 합니다.
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return parse_steps(response.choices[0].message.content)
```

**예시: "고객 문의 자동 응답"**
사용 가능한 도구: `search_kb`, `check_order_status`, `send_email`

1. `search_kb` - 지식베이스에서 관련 정보 검색
2. 검색 결과가 충분하면 답변 생성, 불충분하면 3단계
3. `check_order_status` - 주문 상태 확인
4. `send_email` - 최종 답변 이메일 발송

### Dependency-Based 분해

작업 간 의존성을 파악하여 순서를 결정합니다.

```python
from typing import Set, Dict
import networkx as nx

def decompose_with_dependencies(
    tasks: List[str],
    dependencies: Dict[str, List[str]]
) -> List[str]:
    """의존성 기반 작업 순서 결정"""
    
    # DAG(Directed Acyclic Graph) 생성
    graph = nx.DiGraph()
    graph.add_nodes_from(tasks)
    
    for task, deps in dependencies.items():
        for dep in deps:
            graph.add_edge(dep, task)  # dep → task
    
    # 위상 정렬로 실행 순서 결정
    execution_order = list(nx.topological_sort(graph))
    
    return execution_order

# 예시
tasks = ["데이터 수집", "데이터 정제", "분석", "시각화", "보고서 작성"]

dependencies = {
    "데이터 정제": ["데이터 수집"],
    "분석": ["데이터 정제"],
    "시각화": ["분석"],
    "보고서 작성": ["시각화", "분석"]
}

order = decompose_with_dependencies(tasks, dependencies)
# 결과: ['데이터 수집', '데이터 정제', '분석', '시각화', '보고서 작성']
```

### 동적 분해

실행 중 중간 결과를 보고 다음 단계를 결정합니다.

```python
def dynamic_decomposition(task: str, initial_context: Dict) -> str:
    """동적 작업 분해: 중간 결과에 따라 다음 단계 결정"""
    
    context = initial_context
    completed_steps = []
    
    while not is_task_complete(context):
        # 현재 상태를 바탕으로 다음 단계 결정
        next_step_prompt = f"""
        최종 목표: {task}
        
        현재까지 완료한 단계:
        {format_steps(completed_steps)}
        
        현재 상태:
        {context}
        
        다음에 무엇을 해야 할까요?
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": next_step_prompt}]
        )
        
        next_action = response.choices[0].message.content
        
        # 다음 단계 실행
        result = execute_step(next_action)
        
        # 컨텍스트 업데이트
        context.update(result)
        completed_steps.append(next_action)
        
        # 종료 조건 확인
        if should_stop(context, task):
            break
    
    return generate_final_answer(context, task)
```

**예시: 디버깅 작업**
1. 에러 로그 확인 → "네트워크 타임아웃 발견"
2. 네트워크 설정 확인 → "프록시 설정 오류"
3. 프록시 수정 → "정상 동작 확인"
(중간 결과에 따라 다음 단계가 바뀜)

### 작업 분해 시 고려사항

**원자성(Atomicity)**:
각 단계는 하나의 명확한 목표를 가져야 합니다.

```python
# 나쁜 예: 너무 큰 단계
"경쟁사 분석 및 전략 수립"  # 여러 작업이 섞임

# 좋은 예: 명확한 단계
"경쟁사 정보 수집"
"수집된 데이터 분석"
"분석 결과 기반 전략 도출"
```

**검증 가능성(Verifiability)**:
각 단계의 완료 여부를 명확히 판단할 수 있어야 합니다.

```python
def verify_step(step: str, result: Any) -> bool:
    """단계 완료 여부 검증"""
    if step == "데이터 수집":
        return isinstance(result, list) and len(result) > 0
    elif step == "데이터 정제":
        return all("clean" in item for item in result)
    # ...
```

**재사용성(Reusability)**:
유사한 작업에서 재사용할 수 있도록 일반화합니다.

```python
# 재사용 가능한 단계 라이브러리
REUSABLE_STEPS = {
    "web_scraping": {
        "description": "웹사이트에서 데이터 추출",
        "inputs": ["url", "selector"],
        "outputs": ["raw_data"],
        "tool": "scrape_website"
    },
    "data_cleaning": {
        "description": "데이터 정제 및 표준화",
        "inputs": ["raw_data"],
        "outputs": ["clean_data"],
        "tool": "clean_data"
    }
}
```

올바른 작업 분해는 Agent의 성공률과 유지보수성을 크게 향상시킵니다.

Workflow 실행 중 Agent는 현재 어디까지 진행했는지, 다음에 무엇을 해야 하는지 추적해야 합니다.

### 상태 정의

Agent의 상태는 작업 진행 상황을 나타내는 모든 정보입니다.

```python
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentState:
    """Agent 상태 정의"""
    task_id: str                        # 작업 고유 ID
    goal: str                           # 최종 목표
    current_step: int                   # 현재 단계 번호
    completed_steps: List[Dict]         # 완료한 단계들
    pending_steps: List[str]            # 남은 단계들
    context: Dict[str, Any]            # 누적된 정보
    status: str                         # pending/running/completed/failed
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """상태를 딕셔너리로 직렬화"""
        return {
            "task_id": self.task_id,
            "goal": self.goal,
            "current_step": self.current_step,
            "completed_steps": self.completed_steps,
            "pending_steps": self.pending_steps,
            "context": self.context,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
```

### 상태 저장 및 복원

작업이 중단되어도 이어서 실행할 수 있도록 상태를 저장합니다.

```python
import json
import redis

class StateManager:
    """상태 관리자"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def save_state(self, state: AgentState) -> None:
        """상태 저장"""
        key = f"agent_state:{state.task_id}"
        value = json.dumps(state.to_dict())
        
        # Redis에 저장 (1시간 TTL)
        self.redis.setex(key, 3600, value)
    
    def load_state(self, task_id: str) -> AgentState:
        """상태 복원"""
        key = f"agent_state:{task_id}"
        value = self.redis.get(key)
        
        if not value:
            raise ValueError(f"State not found for task {task_id}")
        
        data = json.loads(value)
        return AgentState(
            task_id=data["task_id"],
            goal=data["goal"],
            current_step=data["current_step"],
            completed_steps=data["completed_steps"],
            pending_steps=data["pending_steps"],
            context=data["context"],
            status=data["status"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def update_state(self, task_id: str, updates: Dict[str, Any]) -> None:
        """상태 업데이트"""
        state = self.load_state(task_id)
        
        for key, value in updates.items():
            setattr(state, key, value)
        
        state.updated_at = datetime.now()
        self.save_state(state)
```

### 상태 기반 재개

중단된 작업을 이어서 실행합니다.

```python
def resume_agent_workflow(task_id: str, state_manager: StateManager) -> str:
    """중단된 Workflow 재개"""
    
    # 저장된 상태 로드
    state = state_manager.load_state(task_id)
    
    print(f"작업 재개: {state.goal}")
    print(f"진행 상황: {state.current_step}/{len(state.completed_steps) + len(state.pending_steps)}")
    
    # 남은 단계 실행
    for step in state.pending_steps:
        print(f"[단계 {state.current_step + 1}] {step}")
        
        try:
            result = execute_step(step, state.context)
            
            # 상태 업데이트
            state.completed_steps.append({
                "step": state.current_step + 1,
                "description": step,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            state.current_step += 1
            state.context.update(result)
            
            # 중간 저장
            state_manager.save_state(state)
            
        except Exception as e:
            print(f"단계 실패: {e}")
            state.status = "failed"
            state_manager.save_state(state)
            raise
    
    state.status = "completed"
    state_manager.save_state(state)
    
    return generate_final_answer(state.context, state.goal)
```

### 상태 전이

Agent가 한 상태에서 다른 상태로 전환하는 규칙을 정의합니다.

```python
from enum import Enum

class WorkflowState(Enum):
    """Workflow 상태"""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"

class StateMachine:
    """상태 머신"""
    
    TRANSITIONS = {
        WorkflowState.IDLE: [WorkflowState.PLANNING],
        WorkflowState.PLANNING: [WorkflowState.EXECUTING, WorkflowState.FAILED],
        WorkflowState.EXECUTING: [WorkflowState.EVALUATING, WorkflowState.FAILED],
        WorkflowState.EVALUATING: [WorkflowState.COMPLETED, WorkflowState.PLANNING, WorkflowState.FAILED],
        WorkflowState.COMPLETED: [],
        WorkflowState.FAILED: []
    }
    
    def __init__(self, initial_state: WorkflowState = WorkflowState.IDLE):
        self.current_state = initial_state
        self.state_history = [initial_state]
    
    def transition(self, next_state: WorkflowState) -> bool:
        """상태 전이"""
        if next_state not in self.TRANSITIONS[self.current_state]:
            print(f"잘못된 상태 전이: {self.current_state} → {next_state}")
            return False
        
        print(f"상태 전이: {self.current_state.value} → {next_state.value}")
        self.current_state = next_state
        self.state_history.append(next_state)
        return True
    
    def can_transition(self, next_state: WorkflowState) -> bool:
        """전이 가능 여부 확인"""
        return next_state in self.TRANSITIONS[self.current_state]

# 사용 예시
state_machine = StateMachine()

state_machine.transition(WorkflowState.PLANNING)     # IDLE → PLANNING (OK)
state_machine.transition(WorkflowState.EXECUTING)    # PLANNING → EXECUTING (OK)
state_machine.transition(WorkflowState.EVALUATING)   # EXECUTING → EVALUATING (OK)
state_machine.transition(WorkflowState.PLANNING)     # EVALUATING → PLANNING (재계획, OK)
```

### 병렬 상태 관리

여러 하위 작업이 동시에 실행될 때 각각의 상태를 추적합니다.

```python
import asyncio
from typing import List

class ParallelStateManager:
    """병렬 작업 상태 관리"""
    
    def __init__(self):
        self.subtask_states: Dict[str, AgentState] = {}
    
    async def execute_parallel_tasks(
        self,
        tasks: List[str],
        parent_task_id: str
    ) -> Dict[str, Any]:
        """병렬 작업 실행 및 상태 추적"""
        
        # 각 하위 작업에 대한 상태 생성
        for idx, task in enumerate(tasks):
            subtask_id = f"{parent_task_id}_sub_{idx}"
            self.subtask_states[subtask_id] = AgentState(
                task_id=subtask_id,
                goal=task,
                current_step=0,
                completed_steps=[],
                pending_steps=[task],
                context={},
                status="pending",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        # 병렬 실행
        results = await asyncio.gather(*[
            self.execute_subtask(subtask_id)
            for subtask_id in self.subtask_states.keys()
        ])
        
        # 결과 취합
        return {
            subtask_id: result
            for subtask_id, result in zip(self.subtask_states.keys(), results)
        }
    
    async def execute_subtask(self, subtask_id: str) -> Any:
        """하위 작업 실행"""
        state = self.subtask_states[subtask_id]
        state.status = "running"
        
        try:
            result = await async_execute_step(state.goal)
            state.status = "completed"
            return result
        except Exception as e:
            state.status = "failed"
            raise
```

### 상태 시각화

진행 상황을 시각적으로 표시합니다.

```python
def visualize_state(state: AgentState) -> str:
    """상태 시각화"""
    total_steps = len(state.completed_steps) + len(state.pending_steps)
    progress = (state.current_step / total_steps) * 100 if total_steps > 0 else 0
    
    # 프로그레스 바
    bar_length = 40
    filled = int(bar_length * progress / 100)
    bar = "=" * filled + "-" * (bar_length - filled)
    
    output = f"""
=== Agent Workflow Status ===
Task ID: {state.task_id}
Goal: {state.goal}
Status: {state.status}
Progress: [{bar}] {progress:.1f}%

Completed Steps ({len(state.completed_steps)}):
{format_steps(state.completed_steps)}

Pending Steps ({len(state.pending_steps)}):
{format_pending(state.pending_steps)}
    """
    
    return output
```

올바른 상태 관리는 Agent의 안정성과 디버깅 가능성을 크게 향상시킵니다.

효과적인 Workflow를 설계하려면 여러 요소를 고려해야 합니다.

### 확장성 (Scalability)

작업 규모가 커져도 성능이 유지되어야 합니다.

```python
# 나쁜 예: 모든 작업을 순차 처리
def process_items_sequential(items: List[str]) -> List[Any]:
    """순차 처리 (느림)"""
    results = []
    for item in items:
        result = process_item(item)  # 각 1초 소요
        results.append(result)
    return results
    # 100개 처리 시 100초 소요

# 좋은 예: 병렬 처리
import asyncio

async def process_items_parallel(items: List[str]) -> List[Any]:
    """병렬 처리 (빠름)"""
    tasks = [async_process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results
    # 100개 처리 시 ~1초 소요 (네트워크 I/O 병렬화)
```

### 견고성 (Robustness)

일부 단계가 실패해도 전체 Workflow가 멈추지 않아야 합니다.

```python
def robust_workflow(tasks: List[str]) -> Dict[str, Any]:
    """견고한 Workflow: 일부 실패해도 계속 진행"""
    
    results = {
        "successful": [],
        "failed": []
    }
    
    for task in tasks:
        try:
            result = execute_task(task)
            results["successful"].append({
                "task": task,
                "result": result
            })
        except Exception as e:
            # 실패해도 계속 진행
            results["failed"].append({
                "task": task,
                "error": str(e)
            })
            log_error(task, e)
    
    # 부분 성공도 유용한 결과
    return results
```

### 비용 효율성

LLM 호출을 최소화하여 비용을 절감합니다.

```python
# 나쁜 예: 매번 LLM 호출
def inefficient_workflow(items: List[str]) -> List[str]:
    """비효율적: 각 아이템마다 LLM 호출"""
    results = []
    for item in items:
        result = llm_call(f"Process this: {item}")  # 매번 $0.01
        results.append(result)
    return results
    # 100개 처리 시 $1.00

# 좋은 예: 배치 처리
def efficient_workflow(items: List[str]) -> List[str]:
    """효율적: 배치로 묶어서 호출"""
    batch_prompt = f"""
    다음 항목들을 각각 처리하세요:
    {chr(10).join(f"{i+1}. {item}" for i, item in enumerate(items))}
    """
    
    response = llm_call(batch_prompt)  # 1회 호출: $0.05
    results = parse_batch_response(response)
    return results
    # 100개 처리 시 $0.05 (95% 절감)
```

### 관찰 가능성 (Observability)

Workflow 실행 과정을 추적하고 디버깅할 수 있어야 합니다.

```python
import logging
from datetime import datetime

class ObservableWorkflow:
    """관찰 가능한 Workflow"""
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.logger = logging.getLogger(f"workflow.{workflow_id}")
        self.trace = []
    
    def execute(self, steps: List[str]) -> Any:
        """추적 가능한 실행"""
        self.logger.info(f"Workflow {self.workflow_id} started")
        start_time = datetime.now()
        
        for idx, step in enumerate(steps):
            step_start = datetime.now()
            
            try:
                self.logger.info(f"[Step {idx+1}] Starting: {step}")
                result = execute_step(step)
                
                duration = (datetime.now() - step_start).total_seconds()
                
                self.trace.append({
                    "step": idx + 1,
                    "description": step,
                    "status": "success",
                    "duration": duration,
                    "result": result
                })
                
                self.logger.info(f"[Step {idx+1}] Completed in {duration}s")
                
            except Exception as e:
                duration = (datetime.now() - step_start).total_seconds()
                
                self.trace.append({
                    "step": idx + 1,
                    "description": step,
                    "status": "failed",
                    "duration": duration,
                    "error": str(e)
                })
                
                self.logger.error(f"[Step {idx+1}] Failed: {e}")
                raise
        
        total_duration = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"Workflow completed in {total_duration}s")
        
        return self.trace
```

### 테스트 가능성

Workflow를 단위 테스트할 수 있어야 합니다.

```python
import pytest
from unittest.mock import Mock, patch

def test_workflow_success():
    """성공 케이스 테스트"""
    # Mock 도구
    with patch('execute_tool') as mock_execute:
        mock_execute.return_value = {"data": "test result"}
        
        # Workflow 실행
        result = run_workflow("test task")
        
        # 검증
        assert result["status"] == "success"
        assert mock_execute.call_count == 3  # 3단계 실행

def test_workflow_failure_recovery():
    """실패 복구 테스트"""
    with patch('execute_tool') as mock_execute:
        # 첫 번째 호출은 실패, 두 번째는 성공
        mock_execute.side_effect = [
            Exception("Network error"),
            {"data": "recovered"}
        ]
        
        result = run_workflow_with_retry("test task")
        
        # 재시도 후 성공 확인
        assert result["status"] == "success"
        assert mock_execute.call_count == 2
```

### 유지보수성

Workflow 로직을 명확하게 문서화하고 모듈화합니다.

```python
from typing import Protocol

class WorkflowStep(Protocol):
    """Workflow 단계 인터페이스"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """단계 실행"""
        ...
    
    def validate(self, result: Dict[str, Any]) -> bool:
        """결과 검증"""
        ...

class DataCollectionStep:
    """데이터 수집 단계"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """웹에서 데이터 수집"""
        url = context["url"]
        data = scrape_website(url)
        return {"collected_data": data}
    
    def validate(self, result: Dict[str, Any]) -> bool:
        """데이터가 비어있지 않은지 확인"""
        return "collected_data" in result and len(result["collected_data"]) > 0

class DataAnalysisStep:
    """데이터 분석 단계"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """수집된 데이터 분석"""
        data = context["collected_data"]
        insights = analyze_data(data)
        return {"insights": insights}
    
    def validate(self, result: Dict[str, Any]) -> bool:
        """인사이트가 생성되었는지 확인"""
        return "insights" in result

# Workflow 조립
workflow_steps = [
    DataCollectionStep(),
    DataAnalysisStep()
]

def run_modular_workflow(context: Dict[str, Any]) -> Dict[str, Any]:
    """모듈화된 Workflow 실행"""
    for step in workflow_steps:
        result = step.execute(context)
        
        if not step.validate(result):
            raise ValueError(f"Step validation failed: {step.__class__.__name__}")
        
        context.update(result)
    
    return context
```

### 설계 체크리스트

Workflow 설계 시 다음 질문에 답할 수 있어야 합니다:

**기능적 요구사항**:
- [ ] 작업이 명확하게 정의되었는가?
- [ ] 각 단계의 입력과 출력이 명시되었는가?
- [ ] 실패 시 복구 전략이 있는가?

**비기능적 요구사항**:
- [ ] 예상 실행 시간과 비용이 산정되었는가?
- [ ] 병렬화 가능한 단계가 식별되었는가?
- [ ] 상태를 저장하고 복원할 수 있는가?

**운영 요구사항**:
- [ ] 로그와 메트릭을 수집하는가?
- [ ] 테스트 케이스가 작성되었는가?
- [ ] 문서화가 완료되었는가?

이러한 요소들을 고려하여 설계하면 프로덕션 환경에서 안정적으로 동작하는 Workflow를 구축할 수 있습니다.

## 핵심 요약

## 흔한 실수

Workflow 설계 시 자주 발생하는 실수들을 살펴봅니다.

### 실수 1: 과도하게 세분화된 단계

**나쁜 예**: 단계를 너무 작게 나누어 오버헤드 발생

```python
# 10개의 미세한 단계로 분할
steps = [
    "URL 열기",
    "페이지 로드 대기",
    "제목 추출",
    "제목 검증",
    "본문 추출",
    "본문 검증",
    "링크 추출",
    "링크 검증",
    "데이터 저장",
    "저장 확인"
]
# 각 단계마다 LLM 호출 → 10회 호출, 느리고 비용 증가
```

**좋은 예**: 의미 있는 크기로 그룹화

```python
steps = [
    "웹 페이지 스크래핑 (제목, 본문, 링크)",
    "수집된 데이터 검증",
    "데이터 저장"
]
# 3회 LLM 호출로 동일한 작업 수행
```

**교훈**: 각 단계는 독립적인 가치를 제공해야 하며, 너무 세분화하면 오히려 복잡도만 증가합니다.

### 실수 2: 상태 관리 누락

**나쁜 예**: 중간 결과를 저장하지 않음

```python
def fragile_workflow(task: str) -> str:
    """상태 저장 없는 Workflow"""
    step1_result = execute_step1(task)
    step2_result = execute_step2(step1_result)  # 실패 시 step1부터 다시
    step3_result = execute_step3(step2_result)
    return step3_result
```

**좋은 예**: 각 단계마다 상태 저장

```python
def resilient_workflow(task_id: str, task: str) -> str:
    """상태 저장하는 Workflow"""
    state = load_or_create_state(task_id, task)
    
    if state.current_step < 1:
        step1_result = execute_step1(task)
        state.context["step1"] = step1_result
        state.current_step = 1
        save_state(state)
    
    if state.current_step < 2:
        step2_result = execute_step2(state.context["step1"])
        state.context["step2"] = step2_result
        state.current_step = 2
        save_state(state)
    
    if state.current_step < 3:
        step3_result = execute_step3(state.context["step2"])
        state.context["step3"] = step3_result
        state.current_step = 3
        save_state(state)
    
    return state.context["step3"]
```

**교훈**: 중간 상태를 저장하면 실패 시 처음부터 다시 시작하지 않아도 됩니다.

### 실수 3: 의존성 순환

**나쁜 예**: 단계 간 순환 의존성 발생

```python
# A는 B 결과 필요, B는 C 결과 필요, C는 A 결과 필요
dependencies = {
    "분석": ["데이터 수집"],
    "데이터 수집": ["보고서 작성"],
    "보고서 작성": ["분석"]  # 순환!
}
# 실행 불가능
```

**좋은 예**: DAG(방향성 비순환 그래프) 구조

```python
# 명확한 방향성
dependencies = {
    "데이터 수집": [],
    "데이터 정제": ["데이터 수집"],
    "분석": ["데이터 정제"],
    "보고서 작성": ["분석"]
}
# 위상 정렬로 실행 순서 결정 가능
```

**교훈**: 작업 간 의존성은 항상 일방향이어야 하며, 순환이 발생하면 설계를 재검토해야 합니다.

### 실수 4: 에러 전파 전략 부재

**나쁜 예**: 첫 번째 실패로 전체 중단

```python
def brittle_workflow(steps: List[str]) -> List[Any]:
    """첫 실패 시 중단"""
    results = []
    for step in steps:
        result = execute_step(step)  # 실패 시 Exception
        results.append(result)
    return results
```

**좋은 예**: 실패 처리 전략 명시

```python
from enum import Enum

class FailureStrategy(Enum):
    ABORT = "abort"          # 즉시 중단
    SKIP = "skip"            # 건너뛰고 계속
    RETRY = "retry"          # 재시도
    FALLBACK = "fallback"    # 대체 방법 사용

def resilient_workflow(
    steps: List[str],
    failure_strategy: FailureStrategy = FailureStrategy.SKIP
) -> Dict[str, Any]:
    """실패 전략이 있는 Workflow"""
    results = {"successful": [], "failed": []}
    
    for step in steps:
        try:
            result = execute_step(step)
            results["successful"].append(result)
        
        except Exception as e:
            if failure_strategy == FailureStrategy.ABORT:
                raise
            
            elif failure_strategy == FailureStrategy.SKIP:
                results["failed"].append({"step": step, "error": str(e)})
                continue
            
            elif failure_strategy == FailureStrategy.RETRY:
                result = retry_with_backoff(execute_step, step)
                results["successful"].append(result)
            
            elif failure_strategy == FailureStrategy.FALLBACK:
                result = execute_fallback(step)
                results["successful"].append(result)
    
    return results
```

**교훈**: 각 단계의 실패가 전체 Workflow에 미치는 영향을 미리 정의해야 합니다.

### 실수 5: 테스트 없이 프로덕션 배포

**나쁜 예**: 실제 데이터로 바로 테스트

```python
# 프로덕션 환경에서 바로 실행
workflow = create_workflow(production_steps)
result = workflow.execute(real_customer_data)  # 위험!
```

**좋은 예**: 단계별 테스트와 검증

```python
import pytest

# 1. 단위 테스트: 각 단계 독립 테스트
def test_data_collection_step():
    step = DataCollectionStep()
    result = step.execute({"url": "https://test.com"})
    assert "collected_data" in result
    assert step.validate(result)

# 2. 통합 테스트: 전체 Workflow 테스트
def test_full_workflow():
    workflow = create_workflow(test_steps)
    result = workflow.execute(test_data)
    assert result["status"] == "success"

# 3. 시뮬레이션: Mock으로 LLM 호출 대체
@pytest.fixture
def mock_llm():
    with patch('openai.chat.completions.create') as mock:
        mock.return_value = Mock(
            choices=[Mock(message=Mock(content="test result"))]
        )
        yield mock

def test_workflow_with_mock(mock_llm):
    result = run_workflow("test task")
    assert mock_llm.call_count == 3  # 예상 호출 횟수

# 4. 카나리 배포: 소수 사용자 대상 테스트
if is_canary_user(user_id):
    result = new_workflow.execute(data)
else:
    result = old_workflow.execute(data)
```

**교훈**: 프로덕션 배포 전에 단위 테스트, 통합 테스트, 시뮬레이션을 거쳐야 합니다.

## 핵심 요약

- Workflow는 Agent가 복잡한 작업을 체계적으로 수행하도록 설계하는 것입니다.
- ReAct, Plan-and-Execute, Reflexion 등 다양한 패턴이 있으며, 작업 특성에 맞게 선택해야 합니다.
- 작업 분해와 상태 관리가 Workflow 설계의 핵심입니다.

<!-- a-grade-example:begin -->

## 체크리스트

- [ ] ReAct vs Plan-and-Execute vs Reflexion을 한 표로 정리할 수 있다.
- [ ] 한 작업을 너무 잘게/너무 크게 쪼갠 두 버전을 비교했다.
- [ ] Workflow state를 외부 저장소에 분리한 예제를 작성했다.
- [ ] 단위 테스트, 시뮬레이션, 카나리 배포 중 두 가지 이상을 적용했다.

<!-- a-grade-example:end -->

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [컨텍스트 엔지니어링](./02-context-engineering.md)
- [Tool Use 기초](./03-tool-use-fundamentals.md)
- **Agent Workflow 설계 (현재 글)**
- Memory와 State (예정)
- Multi-Agent 시스템 (예정)
- Agent 평가 (예정)
- 에러 처리와 안정성 (예정)
- 운영 (예정)
- 첫 Agent 만들기 (예정)

<!-- toc:end -->

## 참고 자료

1. **ReAct: Synergizing Reasoning and Acting in Language Models** - https://arxiv.org/abs/2210.03629  
   Yao et al.의 ReAct 패턴 논문. 추론과 행동을 번갈아 수행하는 방식의 이론적 배경과 실험 결과를 제시합니다.

2. **LangGraph Documentation** - https://langchain-ai.github.io/langgraph/  
   LangChain의 Workflow 구축 프레임워크. 상태 관리, 그래프 기반 Workflow 설계 방법을 다룹니다.

3. **Reflexion: Language Agents with Verbal Reinforcement Learning** - https://arxiv.org/abs/2303.11366  
   자기 반성을 통한 Agent 성능 향상. 실패에서 학습하는 메커니즘을 설명합니다.

4. **AutoGPT Architecture** - https://github.com/Significant-Gravitas/AutoGPT  
   Plan-and-Execute 패턴의 실제 구현 예시. 자율 Agent의 작업 분해 및 실행 전략을 보여줍니다.

Tags: AI Agent, LLM, Tool Use, Python
