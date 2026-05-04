---
title: Agent Workflow Design
series: ai-agent-101
episode: 4
language: en
status: publish-ready
targets:
  tistory: false
  hashnode: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Workflow
- Planning
- Task Decomposition
last_reviewed: '2026-05-02'
---

# Agent Workflow Design

> AI Agent 101 Series (4/10)

To perform complex tasks, agents must break work into steps, execute each step in order, and verify results. This process is called a workflow. It's not just about calling tools—it's about designing "what to do in what order to achieve the goal."

Representative workflow patterns include ReAct (Reasoning + Acting), Plan-and-Execute, and Reflexion. Each pattern has pros and cons depending on task characteristics, and agent designers must choose patterns that match the task type.

This article covers major workflow patterns, task decomposition strategies, state management methods, and factors to consider when designing workflows.

---

<!-- a-grade-intro:begin -->

## Key Questions

- When does each of ReAct, Plan-and-Execute, and Reflexion shine?
- How do you decide the right granularity of decomposed steps?
- Where should state live inside a workflow?
- What validation must happen before pushing a workflow to production?

<!-- a-grade-intro:end -->

## Key Workflow Patterns

Agents need systematic workflows to handle complex tasks. Let's explore the main patterns.

### ReAct (Reasoning + Acting)

**ReAct** alternates between Reasoning and Acting. The agent thinks, uses tools, and observes results iteratively.

```python
from typing import Dict, Any, List
import openai

def react_agent(user_query: str, tools: List[Dict], max_steps: int = 10) -> str:
    """ReAct pattern: Thought → Action → Observation loop"""
    
    messages = [
        {"role": "system", "content": """You are an agent that solves problems step-by-step.
        
        At each step:
        1. Thought: Think about what to do next
        2. Action: Use tools to gather information
        3. Observation: Observe results and plan next step
        
        When you reach the goal, provide an answer starting with "Final Answer:"."""},
        {"role": "user", "content": user_query}
    ]
    
    for step in range(max_steps):
        # Request next action from LLM
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # If final answer
        if assistant_message.content and "Final Answer:" in assistant_message.content:
            return assistant_message.content.replace("Final Answer:", "").strip()
        
        # If tool call
        if assistant_message.tool_calls:
            messages.append(assistant_message)
            
            # Execute each tool
            for tool_call in assistant_message.tool_calls:
                result = execute_tool(tool_call.function.name, tool_call.function.arguments)
                
                # Add observation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": f"Observation: {result}"
                })
        else:
            # Neither tool call nor final answer
            messages.append(assistant_message)
    
    return "Max steps reached without solution."
```

**Advantages**:
- Explicit reasoning process (easy debugging)
- Can adjust plan based on intermediate results
- Step-by-step validation possible

**Disadvantages**:
- LLM call at every step (slow, costly)
- Trial-and-error without upfront planning for complex tasks

**Suitable for**:
- Decision-making after information gathering
- Tasks where strategy changes based on intermediate results
- Example: "Analyze competitors then develop marketing strategy"

### Plan-and-Execute

**Plan-and-Execute** creates a full plan first, then executes steps sequentially.

```python
def plan_and_execute_agent(user_query: str, tools: List[Dict]) -> str:
    """Plan-and-Execute pattern: Plan → Execute"""
    
    # Step 1: Create plan
    plan_prompt = f"""
    Task: {user_query}
    
    Create a step-by-step plan to complete this task.
    Each step should have a clear goal and required tools.
    
    Format:
    1. [step description] - Tool: [tool name]
    2. [step description] - Tool: [tool name]
    ...
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": plan_prompt}]
    )
    
    plan = response.choices[0].message.content
    print(f"Plan:\n{plan}\n")
    
    # Step 2: Execute plan
    steps = parse_plan(plan)  # "1. step - Tool: name" → structured
    
    results = []
    for idx, step in enumerate(steps):
        print(f"[Step {idx + 1}] {step['description']}")
        
        # Execute tool
        tool_result = execute_tool(step["tool"], step["params"])
        results.append({
            "step": idx + 1,
            "description": step["description"],
            "result": tool_result
        })
        
        print(f"Result: {tool_result}\n")
    
    # Step 3: Generate final answer
    summary_prompt = f"""
    Task: {user_query}
    
    Executed steps and results:
    {format_results(results)}
    
    Answer the user's question based on the above results.
    """
    
    final_response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    
    return final_response.choices[0].message.content
```

**Advantages**:
- Clear overall flow (plan reviewable)
- Easy to identify parallelizable steps
- Simple progress tracking

**Disadvantages**:
- Wrong initial plan causes complete failure
- Hard to adjust plan based on intermediate results
- Time spent on planning

**Suitable for**:
- Tasks with clear requirements
- Predictable steps
- Example: "Data collection → Analysis → Report writing"

### Reflexion

**Reflexion** evaluates results after execution, reflects on failures, and revises the plan.

```python
def reflexion_agent(user_query: str, tools: List[Dict], max_retries: int = 3) -> str:
    """Reflexion pattern: Execute → Evaluate → Reflect → Retry"""
    
    reflections = []
    
    for attempt in range(max_retries):
        print(f"\n=== Attempt {attempt + 1} ===")
        
        # Include previous reflections in context
        context = "\n".join([f"Reflection {i+1}: {r}" for i, r in enumerate(reflections)])
        
        prompt = f"""
        Task: {user_query}
        
        Lessons from previous attempts:
        {context if context else "None (first attempt)"}
        
        Perform the task.
        """
        
        # Execute task
        result = execute_task(prompt, tools)
        
        # Evaluate result
        evaluation = evaluate_result(result, user_query)
        
        if evaluation["success"]:
            return result
        
        # Reflect on failure
        reflection_prompt = f"""
        Task: {user_query}
        Attempted method: {result}
        Failure reason: {evaluation['reason']}
        
        Reflect on what went wrong and how to improve in the next attempt.
        """
        
        reflection_response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": reflection_prompt}]
        )
        
        reflection = reflection_response.choices[0].message.content
        reflections.append(reflection)
        
        print(f"Reflection: {reflection}")
    
    return "Max retries reached without success."
```

**Advantages**:
- Learning from failures to improve
- Adaptability for complex problems
- Similar to human problem-solving

**Disadvantages**:
- Multiple retries (time and cost)
- Effectiveness drops with unclear evaluation criteria
- Risk of infinite loops

**Suitable for**:
- Creative tasks without clear correct answers
- Tasks requiring trial and error
- Example: "Code writing and debugging", "Complex problem solving"

### Pattern Comparison

| Pattern | Execution | Advantages | Disadvantages | Suitable Tasks |
|---------|-----------|------------|---------------|----------------|
| ReAct | Step-by-step reasoning + execution | Transparency, flexibility | Slow, costly | Information gathering + decision-making |
| Plan-and-Execute | Plan then execute | Clarity, parallelization | Rigidity | Predictable tasks |
| Reflexion | Execute → Evaluate → Reflect | Learning, adaptability | Retry cost | Creative, trial-and-error |

In production, these patterns are often combined. For example, use Plan-and-Execute for the overall structure, ReAct for each step, and Reflexion for retry on failure.

---

## Task Decomposition Strategy

Breaking complex tasks into smaller steps is key to workflow design. Let's explore effective decomposition strategies.

### Top-Down Decomposition

Break large goals into hierarchical sub-goals.

```python
def decompose_task_topdown(task: str) -> List[Dict[str, Any]]:
    """Top-Down task decomposition"""
    
    prompt = f"""
    Task: {task}
    
    List major subtasks required to complete this task.
    Each subtask should be independently executable.
    
    Format:
    1. [Subtask 1]
       - Goal: [specific goal]
       - Required tools: [tool list]
    2. [Subtask 2]
       ...
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse response
    subtasks = parse_subtasks(response.choices[0].message.content)
    
    # Recursively decompose each complex subtask
    for subtask in subtasks:
        if is_complex(subtask):
            subtask["children"] = decompose_task_topdown(subtask["description"])
    
    return subtasks
```

**Example: "Write competitor analysis report"**
1. Collect competitor list
   - 1.1 Search industry database
   - 1.2 Analyze news articles
2. Gather competitor information
   - 2.1 Crawl websites
   - 2.2 Query financial data
3. Analyze and write report
   - 3.1 Visualize data
   - 3.2 Derive insights
   - 3.3 Generate document

### Bottom-Up Decomposition

Compose possible steps based on available tools.

```python
def decompose_task_bottomup(task: str, available_tools: List[str]) -> List[str]:
    """Bottom-Up: tool-based task decomposition"""
    
    prompt = f"""
    Task: {task}
    
    Available tools:
    {', '.join(available_tools)}
    
    Design steps to complete the task by combining the above tools.
    Each step should use one tool.
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return parse_steps(response.choices[0].message.content)
```

**Example: "Automated customer inquiry response"**
Available tools: `search_kb`, `check_order_status`, `send_email`

1. `search_kb` - Search knowledge base for relevant info
2. If search sufficient, generate answer; else go to step 3
3. `check_order_status` - Check order status
4. `send_email` - Send final answer email

### Dependency-Based Decomposition

Determine order by identifying task dependencies.

```python
from typing import Set, Dict
import networkx as nx

def decompose_with_dependencies(
    tasks: List[str],
    dependencies: Dict[str, List[str]]
) -> List[str]:
    """Dependency-based task ordering"""
    
    # Create DAG (Directed Acyclic Graph)
    graph = nx.DiGraph()
    graph.add_nodes_from(tasks)
    
    for task, deps in dependencies.items():
        for dep in deps:
            graph.add_edge(dep, task)  # dep → task
    
    # Topological sort for execution order
    execution_order = list(nx.topological_sort(graph))
    
    return execution_order

# Example
tasks = ["Collect data", "Clean data", "Analyze", "Visualize", "Write report"]

dependencies = {
    "Clean data": ["Collect data"],
    "Analyze": ["Clean data"],
    "Visualize": ["Analyze"],
    "Write report": ["Visualize", "Analyze"]
}

order = decompose_with_dependencies(tasks, dependencies)
# Result: ['Collect data', 'Clean data', 'Analyze', 'Visualize', 'Write report']
```

### Dynamic Decomposition

Decide next steps during execution based on intermediate results.

```python
def dynamic_decomposition(task: str, initial_context: Dict) -> str:
    """Dynamic task decomposition: decide next step based on current state"""
    
    context = initial_context
    completed_steps = []
    
    while not is_task_complete(context):
        # Decide next step based on current state
        next_step_prompt = f"""
        Final goal: {task}
        
        Completed steps so far:
        {format_steps(completed_steps)}
        
        Current state:
        {context}
        
        What should be done next?
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": next_step_prompt}]
        )
        
        next_action = response.choices[0].message.content
        
        # Execute next step
        result = execute_step(next_action)
        
        # Update context
        context.update(result)
        completed_steps.append(next_action)
        
        # Check termination condition
        if should_stop(context, task):
            break
    
    return generate_final_answer(context, task)
```

**Example: Debugging task**
1. Check error log → "Found network timeout"
2. Check network settings → "Proxy configuration error"
3. Fix proxy → "Confirmed working"
(Next step changes based on intermediate results)

### Task Decomposition Considerations

**Atomicity**:
Each step should have one clear goal.

```python
# Bad: step too large
"Analyze competitors and develop strategy"  # Multiple tasks mixed

# Good: clear steps
"Collect competitor information"
"Analyze collected data"
"Derive strategy from analysis"
```

**Verifiability**:
Completion of each step should be clearly determinable.

```python
def verify_step(step: str, result: Any) -> bool:
    """Verify step completion"""
    if step == "Collect data":
        return isinstance(result, list) and len(result) > 0
    elif step == "Clean data":
        return all("clean" in item for item in result)
    # ...
```

**Reusability**:
Generalize for reuse in similar tasks.

```python
# Reusable step library
REUSABLE_STEPS = {
    "web_scraping": {
        "description": "Extract data from website",
        "inputs": ["url", "selector"],
        "outputs": ["raw_data"],
        "tool": "scrape_website"
    },
    "data_cleaning": {
        "description": "Clean and standardize data",
        "inputs": ["raw_data"],
        "outputs": ["clean_data"],
        "tool": "clean_data"
    }
}
```

Proper task decomposition significantly improves agent success rate and maintainability.

---

## State Management

During workflow execution, agents must track progress and determine next actions.

### State Definition

Agent state represents all information about task progress.

```python
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentState:
    """Agent state definition"""
    task_id: str                        # Unique task ID
    goal: str                           # Final goal
    current_step: int                   # Current step number
    completed_steps: List[Dict]         # Completed steps
    pending_steps: List[str]            # Remaining steps
    context: Dict[str, Any]            # Accumulated information
    status: str                         # pending/running/completed/failed
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary"""
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

### State Persistence and Recovery

Save state so execution can resume after interruption.

```python
import json
import redis

class StateManager:
    """State manager"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def save_state(self, state: AgentState) -> None:
        """Save state"""
        key = f"agent_state:{state.task_id}"
        value = json.dumps(state.to_dict())
        
        # Save to Redis (1 hour TTL)
        self.redis.setex(key, 3600, value)
    
    def load_state(self, task_id: str) -> AgentState:
        """Load state"""
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
        """Update state"""
        state = self.load_state(task_id)
        
        for key, value in updates.items():
            setattr(state, key, value)
        
        state.updated_at = datetime.now()
        self.save_state(state)
```

### State-Based Resumption

Resume interrupted tasks.

```python
def resume_agent_workflow(task_id: str, state_manager: StateManager) -> str:
    """Resume interrupted workflow"""
    
    # Load saved state
    state = state_manager.load_state(task_id)
    
    print(f"Resuming task: {state.goal}")
    print(f"Progress: {state.current_step}/{len(state.completed_steps) + len(state.pending_steps)}")
    
    # Execute remaining steps
    for step in state.pending_steps:
        print(f"[Step {state.current_step + 1}] {step}")
        
        try:
            result = execute_step(step, state.context)
            
            # Update state
            state.completed_steps.append({
                "step": state.current_step + 1,
                "description": step,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            state.current_step += 1
            state.context.update(result)
            
            # Save intermediate state
            state_manager.save_state(state)
            
        except Exception as e:
            print(f"Step failed: {e}")
            state.status = "failed"
            state_manager.save_state(state)
            raise
    
    state.status = "completed"
    state_manager.save_state(state)
    
    return generate_final_answer(state.context, state.goal)
```

### State Transitions

Define rules for agent transitions between states.

```python
from enum import Enum

class WorkflowState(Enum):
    """Workflow states"""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"

class StateMachine:
    """State machine"""
    
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
        """Transition state"""
        if next_state not in self.TRANSITIONS[self.current_state]:
            print(f"Invalid transition: {self.current_state} → {next_state}")
            return False
        
        print(f"State transition: {self.current_state.value} → {next_state.value}")
        self.current_state = next_state
        self.state_history.append(next_state)
        return True
    
    def can_transition(self, next_state: WorkflowState) -> bool:
        """Check if transition is possible"""
        return next_state in self.TRANSITIONS[self.current_state]

# Usage example
state_machine = StateMachine()

state_machine.transition(WorkflowState.PLANNING)     # IDLE → PLANNING (OK)
state_machine.transition(WorkflowState.EXECUTING)    # PLANNING → EXECUTING (OK)
state_machine.transition(WorkflowState.EVALUATING)   # EXECUTING → EVALUATING (OK)
state_machine.transition(WorkflowState.PLANNING)     # EVALUATING → PLANNING (replan, OK)
```

### Parallel State Management

Track state of each subtask when multiple run concurrently.

```python
import asyncio
from typing import List

class ParallelStateManager:
    """Parallel task state management"""
    
    def __init__(self):
        self.subtask_states: Dict[str, AgentState] = {}
    
    async def execute_parallel_tasks(
        self,
        tasks: List[str],
        parent_task_id: str
    ) -> Dict[str, Any]:
        """Execute parallel tasks and track states"""
        
        # Create state for each subtask
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
        
        # Execute in parallel
        results = await asyncio.gather(*[
            self.execute_subtask(subtask_id)
            for subtask_id in self.subtask_states.keys()
        ])
        
        # Aggregate results
        return {
            subtask_id: result
            for subtask_id, result in zip(self.subtask_states.keys(), results)
        }
    
    async def execute_subtask(self, subtask_id: str) -> Any:
        """Execute subtask"""
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

### State Visualization

Display progress visually.

```python
def visualize_state(state: AgentState) -> str:
    """Visualize state"""
    total_steps = len(state.completed_steps) + len(state.pending_steps)
    progress = (state.current_step / total_steps) * 100 if total_steps > 0 else 0
    
    # Progress bar
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

Proper state management significantly improves agent stability and debuggability.

---

## Workflow Design Considerations

Effective workflow design requires considering multiple factors.

### Scalability

Performance should maintain as task scale grows.

```python
# Bad: sequential processing of all items
def process_items_sequential(items: List[str]) -> List[Any]:
    """Sequential processing (slow)"""
    results = []
    for item in items:
        result = process_item(item)  # 1 second each
        results.append(result)
    return results
    # 100 items = 100 seconds

# Good: parallel processing
import asyncio

async def process_items_parallel(items: List[str]) -> List[Any]:
    """Parallel processing (fast)"""
    tasks = [async_process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results
    # 100 items = ~1 second (parallelized network I/O)
```

### Robustness

Entire workflow shouldn't halt when some steps fail.

```python
def robust_workflow(tasks: List[str]) -> Dict[str, Any]:
    """Robust workflow: continue despite partial failures"""
    
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
            # Continue despite failure
            results["failed"].append({
                "task": task,
                "error": str(e)
            })
            log_error(task, e)
    
    # Partial success is still valuable
    return results
```

### Cost Efficiency

Minimize LLM calls to reduce costs.

```python
# Bad: LLM call for each item
def inefficient_workflow(items: List[str]) -> List[str]:
    """Inefficient: call LLM per item"""
    results = []
    for item in items:
        result = llm_call(f"Process this: {item}")  # $0.01 each
        results.append(result)
    return results
    # 100 items = $1.00

# Good: batch processing
def efficient_workflow(items: List[str]) -> List[str]:
    """Efficient: batch items together"""
    batch_prompt = f"""
    Process each of the following items:
    {chr(10).join(f"{i+1}. {item}" for i, item in enumerate(items))}
    """
    
    response = llm_call(batch_prompt)  # Single call: $0.05
    results = parse_batch_response(response)
    return results
    # 100 items = $0.05 (95% savings)
```

### Observability

Workflow execution should be traceable and debuggable.

```python
import logging
from datetime import datetime

class ObservableWorkflow:
    """Observable workflow"""
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.logger = logging.getLogger(f"workflow.{workflow_id}")
        self.trace = []
    
    def execute(self, steps: List[str]) -> Any:
        """Traceable execution"""
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

### Testability

Workflows should be unit-testable.

```python
import pytest
from unittest.mock import Mock, patch

def test_workflow_success():
    """Test success case"""
    # Mock tools
    with patch('execute_tool') as mock_execute:
        mock_execute.return_value = {"data": "test result"}
        
        # Execute workflow
        result = run_workflow("test task")
        
        # Verify
        assert result["status"] == "success"
        assert mock_execute.call_count == 3  # 3 steps executed

def test_workflow_failure_recovery():
    """Test failure recovery"""
    with patch('execute_tool') as mock_execute:
        # First call fails, second succeeds
        mock_execute.side_effect = [
            Exception("Network error"),
            {"data": "recovered"}
        ]
        
        result = run_workflow_with_retry("test task")
        
        # Verify success after retry
        assert result["status"] == "success"
        assert mock_execute.call_count == 2
```

### Maintainability

Document and modularize workflow logic clearly.

```python
from typing import Protocol

class WorkflowStep(Protocol):
    """Workflow step interface"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute step"""
        ...
    
    def validate(self, result: Dict[str, Any]) -> bool:
        """Validate result"""
        ...

class DataCollectionStep:
    """Data collection step"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data from web"""
        url = context["url"]
        data = scrape_website(url)
        return {"collected_data": data}
    
    def validate(self, result: Dict[str, Any]) -> bool:
        """Check data is not empty"""
        return "collected_data" in result and len(result["collected_data"]) > 0

class DataAnalysisStep:
    """Data analysis step"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze collected data"""
        data = context["collected_data"]
        insights = analyze_data(data)
        return {"insights": insights}
    
    def validate(self, result: Dict[str, Any]) -> bool:
        """Check insights were generated"""
        return "insights" in result

# Assemble workflow
workflow_steps = [
    DataCollectionStep(),
    DataAnalysisStep()
]

def run_modular_workflow(context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute modular workflow"""
    for step in workflow_steps:
        result = step.execute(context)
        
        if not step.validate(result):
            raise ValueError(f"Step validation failed: {step.__class__.__name__}")
        
        context.update(result)
    
    return context
```

### Design Checklist

When designing workflows, answer these questions:

**Functional Requirements**:
- [ ] Is the task clearly defined?
- [ ] Are inputs and outputs specified for each step?
- [ ] Is there a recovery strategy for failures?

**Non-Functional Requirements**:
- [ ] Are expected execution time and cost estimated?
- [ ] Are parallelizable steps identified?
- [ ] Can state be saved and restored?

**Operational Requirements**:
- [ ] Are logs and metrics collected?
- [ ] Are test cases written?
- [ ] Is documentation complete?

Considering these factors results in workflows that operate reliably in production environments.

---

## Common Mistakes

Let's examine frequent mistakes in workflow design.

### Mistake 1: Overly Granular Steps

**Bad**: Steps too small causing overhead

```python
# Split into 10 tiny steps
steps = [
    "Open URL",
    "Wait for page load",
    "Extract title",
    "Validate title",
    "Extract body",
    "Validate body",
    "Extract links",
    "Validate links",
    "Save data",
    "Confirm save"
]
# LLM call at each step → 10 calls, slow and expensive
```

**Good**: Group into meaningful sizes

```python
steps = [
    "Scrape web page (title, body, links)",
    "Validate collected data",
    "Save data"
]
# 3 LLM calls for same work
```

**Lesson**: Each step should provide independent value; excessive granularity only increases complexity.

### Mistake 2: Missing State Management

**Bad**: Not saving intermediate results

```python
def fragile_workflow(task: str) -> str:
    """Workflow without state persistence"""
    step1_result = execute_step1(task)
    step2_result = execute_step2(step1_result)  # Failure restarts from step1
    step3_result = execute_step3(step2_result)
    return step3_result
```

**Good**: Save state at each step

```python
def resilient_workflow(task_id: str, task: str) -> str:
    """Workflow with state persistence"""
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

**Lesson**: Saving intermediate state avoids restarting from scratch on failure.

### Mistake 3: Circular Dependencies

**Bad**: Circular dependencies between steps

```python
# A needs B result, B needs C result, C needs A result
dependencies = {
    "Analyze": ["Collect data"],
    "Collect data": ["Write report"],
    "Write report": ["Analyze"]  # Circular!
}
# Cannot execute
```

**Good**: DAG (Directed Acyclic Graph) structure

```python
# Clear directionality
dependencies = {
    "Collect data": [],
    "Clean data": ["Collect data"],
    "Analyze": ["Clean data"],
    "Write report": ["Analyze"]
}
# Execution order determinable via topological sort
```

**Lesson**: Task dependencies must always be unidirectional; circular dependencies require design reconsideration.

### Mistake 4: No Error Propagation Strategy

**Bad**: First failure halts everything

```python
def brittle_workflow(steps: List[str]) -> List[Any]:
    """Halt on first failure"""
    results = []
    for step in steps:
        result = execute_step(step)  # Raises Exception on failure
        results.append(result)
    return results
```

**Good**: Explicit failure handling strategy

```python
from enum import Enum

class FailureStrategy(Enum):
    ABORT = "abort"          # Halt immediately
    SKIP = "skip"            # Skip and continue
    RETRY = "retry"          # Retry
    FALLBACK = "fallback"    # Use alternative method

def resilient_workflow(
    steps: List[str],
    failure_strategy: FailureStrategy = FailureStrategy.SKIP
) -> Dict[str, Any]:
    """Workflow with failure strategy"""
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

**Lesson**: Define upfront how each step's failure impacts the entire workflow.

### Mistake 5: Production Deploy Without Testing

**Bad**: Test directly with real data

```python
# Execute directly in production
workflow = create_workflow(production_steps)
result = workflow.execute(real_customer_data)  # Risky!
```

**Good**: Step-by-step testing and validation

```python
import pytest

# 1. Unit test: test each step independently
def test_data_collection_step():
    step = DataCollectionStep()
    result = step.execute({"url": "https://test.com"})
    assert "collected_data" in result
    assert step.validate(result)

# 2. Integration test: test full workflow
def test_full_workflow():
    workflow = create_workflow(test_steps)
    result = workflow.execute(test_data)
    assert result["status"] == "success"

# 3. Simulation: replace LLM calls with mocks
@pytest.fixture
def mock_llm():
    with patch('openai.chat.completions.create') as mock:
        mock.return_value = Mock(
            choices=[Mock(message=Mock(content="test result"))]
        )
        yield mock

def test_workflow_with_mock(mock_llm):
    result = run_workflow("test task")
    assert mock_llm.call_count == 3  # Expected call count

# 4. Canary deployment: test with small user subset
if is_canary_user(user_id):
    result = new_workflow.execute(data)
else:
    result = old_workflow.execute(data)
```

**Lesson**: Go through unit tests, integration tests, and simulation before production deployment.

## Key Takeaways

- Workflows are about designing agents to systematically perform complex tasks.
- Various patterns like ReAct, Plan-and-Execute, and Reflexion exist, and you must choose based on task characteristics.
- Task decomposition and state management are the core of workflow design.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Built a one-page comparison of ReAct vs Plan-and-Execute vs Reflexion.
- [ ] Compared two versions of a task split too small vs too large.
- [ ] Wrote a workflow that keeps state in an external store.
- [ ] Applied at least two of: unit tests, simulation, canary rollout.

<!-- a-grade-example:end -->

<!-- toc:begin -->
## In this series

- [What Is an AI Agent?](./01-what-is-an-ai-agent.md)
- [Context Engineering](./02-context-engineering.md)
- [Tool Use Fundamentals](./03-tool-use-fundamentals.md)
- **Agent Workflow Design (current)**
- Memory and State (upcoming)
- Multi-Agent Systems (upcoming)
- Agent Evaluation (upcoming)
- Error Handling and Reliability (upcoming)
- Production Operations (upcoming)
- Building Your First Agent (upcoming)

<!-- toc:end -->

## References

1. **ReAct: Synergizing Reasoning and Acting in Language Models** - https://arxiv.org/abs/2210.03629  
   Yao et al.'s ReAct pattern paper. Presents theoretical background and experimental results for alternating reasoning and acting.

2. **LangGraph Documentation** - https://langchain-ai.github.io/langgraph/  
   LangChain's workflow construction framework. Covers state management and graph-based workflow design methods.

3. **Reflexion: Language Agents with Verbal Reinforcement Learning** - https://arxiv.org/abs/2303.11366  
   Agent performance improvement through self-reflection. Explains mechanisms for learning from failures.

4. **AutoGPT Architecture** - https://github.com/Significant-Gravitas/AutoGPT  
   Real implementation example of Plan-and-Execute pattern. Shows autonomous agent task decomposition and execution strategies.

Tags: AI Agent, LLM, Tool Use, Python
