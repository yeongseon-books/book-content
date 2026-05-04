---
title: Multi-Agent 시스템
series: ai-agent-101
episode: 6
language: ko
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Multi-Agent
- Coordination
- Delegation
last_reviewed: '2026-05-02'
---

# Multi-Agent 시스템

> AI Agent 101 시리즈 (6/10)

하나의 Agent로 모든 작업을 처리하기 어려울 때가 있습니다. 작업이 여러 도메인에 걸쳐 있거나, 각 단계에서 다른 전문성이 필요하거나, 병렬 처리가 필요한 경우입니다. 이럴 때 여러 Agent를 협력시키는 것이 Multi-Agent 시스템입니다.

Multi-Agent 시스템의 핵심은 조정(coordination)과 위임(delegation)입니다. 한 Agent가 전체를 조율하는 Orchestrator 패턴, 여러 Agent가 대등하게 협력하는 Peer-to-Peer 패턴, 작업을 계층적으로 나누는 Hierarchical 패턴 등이 있습니다.

이번 글에서는 Multi-Agent 패턴, Agent 간 통신 프로토콜, 위임 전략, 그리고 Multi-Agent 시스템을 언제 사용해야 하는지 다룹니다.

---

## Multi-Agent 패턴

복잡한 작업을 여러 Agent가 협력해서 처리하는 방식에는 여러 패턴이 있습니다.

### Orchestrator 패턴 (중앙 조율)

하나의 Orchestrator Agent가 전체를 조율하고, 전문화된 Worker Agent들에게 작업을 위임합니다.

```python
from typing import List, Dict
from openai import OpenAI

class WorkerAgent:
    """전문화된 Worker Agent"""
    
    def __init__(self, name: str, role: str, api_key: str):
        self.name = name
        self.role = role
        self.client = OpenAI(api_key=api_key)
    
    def execute(self, task: str) -> str:
        """작업 실행"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are a {self.role}."},
                {"role": "user", "content": task}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content

class OrchestratorAgent:
    """Orchestrator: 작업을 분석하고 Worker에게 위임"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.workers: Dict[str, WorkerAgent] = {}
    
    def register_worker(self, worker: WorkerAgent):
        """Worker 등록"""
        self.workers[worker.name] = worker
    
    def delegate(self, user_request: str) -> str:
        """요청을 분석하고 적절한 Worker에게 위임"""
        # 1. 작업 분석
        analysis = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""You are an orchestrator.
Analyze the user request and decide which worker should handle it.
Available workers: {', '.join(self.workers.keys())}"""},
                {"role": "user", "content": user_request}
            ],
            temperature=0
        )
        
        worker_name = analysis.choices[0].message.content.strip()
        
        # 2. Worker에게 위임
        if worker_name in self.workers:
            result = self.workers[worker_name].execute(user_request)
            return f"[{worker_name}] {result}"
        else:
            return f"No suitable worker found for: {user_request}"

# 사용 예시
orchestrator = OrchestratorAgent(api_key="your-api-key")

# Worker 등록
code_agent = WorkerAgent(name="CodeAgent", role="Python expert", api_key="your-api-key")
doc_agent = WorkerAgent(name="DocAgent", role="Documentation writer", api_key="your-api-key")

orchestrator.register_worker(code_agent)
orchestrator.register_worker(doc_agent)

# 요청 처리
result = orchestrator.delegate("Python으로 API 호출 예제 코드 작성해줘")
print(result)  # [CodeAgent] ...
```

**장점:**
- 명확한 책임 분담 (조율 vs 실행)
- Worker 추가/제거가 쉬움
- 중앙에서 상태 추적 가능

**단점:**
- Orchestrator가 병목이 될 수 있음
- Orchestrator 장애 시 전체 시스템 중단

---

### Peer-to-Peer 패턴 (대등한 협력)

여러 Agent가 대등하게 협력하며, 서로 메시지를 주고받습니다.

```python
from typing import List, Dict, Optional

class PeerAgent:
    """Peer-to-Peer Agent"""
    
    def __init__(self, name: str, role: str, api_key: str):
        self.name = name
        self.role = role
        self.client = OpenAI(api_key=api_key)
        self.peers: List['PeerAgent'] = []
        self.conversation_history: List[Dict] = []
    
    def add_peer(self, peer: 'PeerAgent'):
        """동료 Agent 추가"""
        if peer not in self.peers:
            self.peers.append(peer)
    
    def send_message(self, recipient_name: str, message: str):
        """특정 Agent에게 메시지 전송"""
        recipient = next((p for p in self.peers if p.name == recipient_name), None)
        if recipient:
            recipient.receive_message(self.name, message)
    
    def receive_message(self, sender_name: str, message: str):
        """메시지 수신"""
        self.conversation_history.append({
            "from": sender_name,
            "to": self.name,
            "message": message
        })
        
        # 메시지에 대한 응답 생성
        response = self.generate_response(sender_name, message)
        
        # 응답이 필요하면 답장
        if response:
            sender = next((p for p in self.peers if p.name == sender_name), None)
            if sender:
                sender.receive_message(self.name, response)
    
    def generate_response(self, sender_name: str, message: str) -> Optional[str]:
        """메시지에 대한 응답 생성"""
        context = f"You are {self.name}, a {self.role}.\n"
        context += f"Message from {sender_name}: {message}\n"
        context += "Generate a response or return 'DONE' if no response needed."
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": context}
            ],
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        return None if result.strip() == "DONE" else result

# 사용 예시
researcher = PeerAgent(name="Researcher", role="research specialist", api_key="your-api-key")
writer = PeerAgent(name="Writer", role="content writer", api_key="your-api-key")
reviewer = PeerAgent(name="Reviewer", role="content reviewer", api_key="your-api-key")

# 서로를 동료로 등록
researcher.add_peer(writer)
writer.add_peer(researcher)
writer.add_peer(reviewer)
reviewer.add_peer(writer)

# 협업 시작
researcher.send_message("Writer", "AI Agent에 대한 글을 작성해줘. 내가 조사한 내용: ...")
# Writer가 글을 작성하고 Reviewer에게 전달
# Reviewer가 피드백을 주고 Writer가 수정
```

**장점:**
- 중앙 조율자 없이 유연한 협력
- Agent 간 직접 통신으로 빠른 의사결정

**단점:**
- 통신 흐름이 복잡해질 수 있음
- 무한 루프 위험 (A→B→A→B→...)

---

### Hierarchical 패턴 (계층적 위임)

Manager Agent가 여러 하위 Manager를 관리하고, 각 Manager가 자신의 Worker를 관리합니다.

```python
class HierarchicalAgent:
    """계층적 Agent (Manager 또는 Worker)"""
    
    def __init__(self, name: str, role: str, api_key: str, is_manager: bool = False):
        self.name = name
        self.role = role
        self.client = OpenAI(api_key=api_key)
        self.is_manager = is_manager
        self.subordinates: List['HierarchicalAgent'] = []
    
    def add_subordinate(self, agent: 'HierarchicalAgent'):
        """하위 Agent 추가 (Manager만 가능)"""
        if self.is_manager:
            self.subordinates.append(agent)
    
    def execute(self, task: str) -> str:
        """작업 실행 또는 위임"""
        if self.is_manager and self.subordinates:
            # Manager: 작업을 하위 Agent에게 위임
            delegate_plan = self._plan_delegation(task)
            results = []
            
            for subtask, agent_name in delegate_plan:
                agent = next((a for a in self.subordinates if a.name == agent_name), None)
                if agent:
                    result = agent.execute(subtask)
                    results.append(f"{agent_name}: {result}")
            
            # 결과 종합
            return self._synthesize_results(results)
        else:
            # Worker: 직접 실행
            return self._execute_task(task)
    
    def _plan_delegation(self, task: str) -> List[tuple]:
        """작업을 하위 Agent들에게 어떻게 분배할지 계획"""
        subordinate_info = ", ".join([f"{s.name} ({s.role})" for s in self.subordinates])
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""You are {self.name}, a manager.
Your subordinates: {subordinate_info}
Break down the task and assign subtasks to appropriate subordinates.
Format: subtask|agent_name (one per line)"""},
                {"role": "user", "content": task}
            ],
            temperature=0
        )
        
        plan = []
        for line in response.choices[0].message.content.split("\n"):
            if "|" in line:
                subtask, agent_name = line.split("|", 1)
                plan.append((subtask.strip(), agent_name.strip()))
        
        return plan
    
    def _execute_task(self, task: str) -> str:
        """Worker가 작업 직접 실행"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are {self.name}, a {self.role}."},
                {"role": "user", "content": task}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def _synthesize_results(self, results: List[str]) -> str:
        """하위 Agent 결과를 종합"""
        combined = "\n".join(results)
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are {self.name}. Synthesize the following results."},
                {"role": "user", "content": combined}
            ],
            temperature=0
        )
        return response.choices[0].message.content

# 사용 예시
# Top Manager
cto = HierarchicalAgent(name="CTO", role="technical leader", api_key="your-api-key", is_manager=True)

# Mid-level Managers
dev_manager = HierarchicalAgent(name="DevManager", role="development manager", api_key="your-api-key", is_manager=True)
qa_manager = HierarchicalAgent(name="QAManager", role="QA manager", api_key="your-api-key", is_manager=True)

# Workers
backend_dev = HierarchicalAgent(name="BackendDev", role="backend developer", api_key="your-api-key")
frontend_dev = HierarchicalAgent(name="FrontendDev", role="frontend developer", api_key="your-api-key")
qa_tester = HierarchicalAgent(name="QATester", role="QA tester", api_key="your-api-key")

# 계층 구성
cto.add_subordinate(dev_manager)
cto.add_subordinate(qa_manager)

dev_manager.add_subordinate(backend_dev)
dev_manager.add_subordinate(frontend_dev)

qa_manager.add_subordinate(qa_tester)

# 작업 실행
result = cto.execute("새로운 사용자 인증 기능 개발 및 테스트")
print(result)
```

**장점:**
- 대규모 조직 구조 모델링 가능
- 명확한 책임 체인
- 확장성이 높음

**단점:**
- 구조가 복잡함
- 계층이 깊어지면 통신 지연 증가

---

## Agent 간 통신 프로토콜

Multi-Agent 시스템에서 Agent들이 어떻게 메시지를 주고받을지 정의해야 합니다.

### 메시지 포맷 표준화

모든 Agent가 이해할 수 있는 메시지 형식을 정의합니다.

```python
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class AgentMessage:
    """표준화된 Agent 메시지"""
    sender: str          # 발신자 Agent 이름
    receiver: str        # 수신자 Agent 이름
    message_type: str    # "request", "response", "notification"
    content: str         # 메시지 내용
    metadata: Dict[str, Any]  # 추가 정보
    timestamp: str       # 전송 시각
    correlation_id: Optional[str] = None  # 요청-응답 연결용 ID
    
    def to_json(self) -> str:
        """JSON으로 직렬화"""
        return json.dumps({
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id
        })
    
    @staticmethod
    def from_json(json_str: str) -> 'AgentMessage':
        """JSON에서 역직렬화"""
        data = json.loads(json_str)
        return AgentMessage(**data)

# 사용 예시
request = AgentMessage(
    sender="OrchestratorAgent",
    receiver="CodeAgent",
    message_type="request",
    content="Python으로 API 호출 예제 작성해줘",
    metadata={"priority": "high", "language": "ko"},
    timestamp=datetime.now().isoformat(),
    correlation_id="req_001"
)

# JSON 직렬화 (네트워크 전송용)
json_message = request.to_json()

# 수신 측에서 역직렬화
received = AgentMessage.from_json(json_message)
print(f"From: {received.sender}, Content: {received.content}")
```

**핵심:**
- 모든 메시지는 발신자, 수신자, 타입, 내용을 포함합니다.
- `correlation_id`로 요청과 응답을 연결합니다.
- JSON 직렬화로 네트워크 전송이나 저장이 가능합니다.

---

### Message Broker 패턴

중앙 Message Broker가 메시지 라우팅을 담당합니다.

```python
from typing import Dict, List, Callable
from queue import Queue
import threading

class MessageBroker:
    """중앙 메시지 브로커"""
    
    def __init__(self):
        self.queues: Dict[str, Queue] = {}
        self.handlers: Dict[str, Callable] = {}
        self.running = False
    
    def register_agent(self, agent_name: str, handler: Callable):
        """Agent 등록"""
        self.queues[agent_name] = Queue()
        self.handlers[agent_name] = handler
    
    def send_message(self, message: AgentMessage):
        """메시지 전송"""
        receiver_queue = self.queues.get(message.receiver)
        if receiver_queue:
            receiver_queue.put(message)
        else:
            print(f"Warning: Receiver {message.receiver} not found")
    
    def start(self):
        """브로커 시작 (각 Agent별 메시지 처리 스레드 시작)"""
        self.running = True
        for agent_name in self.queues:
            thread = threading.Thread(target=self._process_messages, args=(agent_name,))
            thread.daemon = True
            thread.start()
    
    def _process_messages(self, agent_name: str):
        """Agent의 메시지 큐 처리"""
        queue = self.queues[agent_name]
        handler = self.handlers[agent_name]
        
        while self.running:
            try:
                message = queue.get(timeout=1)
                handler(message)
            except:
                pass
    
    def stop(self):
        """브로커 중지"""
        self.running = False

# 사용 예시
broker = MessageBroker()

def code_agent_handler(message: AgentMessage):
    """CodeAgent의 메시지 처리 함수"""
    print(f"[CodeAgent] Received: {message.content}")
    # 작업 실행
    result = f"Generated code for: {message.content}"
    # 응답 전송
    response = AgentMessage(
        sender="CodeAgent",
        receiver=message.sender,
        message_type="response",
        content=result,
        metadata={},
        timestamp=datetime.now().isoformat(),
        correlation_id=message.correlation_id
    )
    broker.send_message(response)

def orchestrator_handler(message: AgentMessage):
    """Orchestrator의 메시지 처리 함수"""
    print(f"[Orchestrator] Received response: {message.content}")

# Agent 등록
broker.register_agent("CodeAgent", code_agent_handler)
broker.register_agent("Orchestrator", orchestrator_handler)

# 브로커 시작
broker.start()

# 메시지 전송
request = AgentMessage(
    sender="Orchestrator",
    receiver="CodeAgent",
    message_type="request",
    content="Write Python API call example",
    metadata={},
    timestamp=datetime.now().isoformat(),
    correlation_id="req_001"
)
broker.send_message(request)

# 메시지 처리 대기
import time
time.sleep(2)

broker.stop()
```

**장점:**
- Agent 간 직접 의존성 제거 (decoupling)
- 비동기 통신 지원
- 메시지 큐잉으로 부하 조절

**단점:**
- Message Broker 자체가 단일 장애점
- 추가 인프라 필요

---

### Shared Memory 패턴

공유 메모리(상태 저장소)를 통해 Agent들이 정보를 공유합니다.

```python
from typing import Dict, Any
import json
from datetime import datetime

class SharedMemory:
    """Agent들이 공유하는 메모리"""
    
    def __init__(self):
        self.memory: Dict[str, Any] = {}
        self.history: List[Dict] = []
    
    def set(self, key: str, value: Any, agent_name: str):
        """값 설정"""
        self.memory[key] = value
        self.history.append({
            "action": "set",
            "key": key,
            "value": value,
            "agent": agent_name,
            "timestamp": datetime.now().isoformat()
        })
    
    def get(self, key: str, agent_name: str) -> Any:
        """값 조회"""
        value = self.memory.get(key)
        self.history.append({
            "action": "get",
            "key": key,
            "agent": agent_name,
            "timestamp": datetime.now().isoformat()
        })
        return value
    
    def get_history(self) -> List[Dict]:
        """메모리 접근 이력"""
        return self.history

class SharedMemoryAgent:
    """Shared Memory를 사용하는 Agent"""
    
    def __init__(self, name: str, shared_memory: SharedMemory):
        self.name = name
        self.shared_memory = shared_memory
    
    def execute(self, task: str):
        """작업 실행 및 결과를 공유 메모리에 저장"""
        # 작업 수행
        result = f"{self.name} completed: {task}"
        
        # 공유 메모리에 저장
        self.shared_memory.set(f"result_{self.name}", result, self.name)
        
        print(f"[{self.name}] Task done, result saved to shared memory")
    
    def read_peer_result(self, peer_name: str):
        """다른 Agent의 결과 읽기"""
        result = self.shared_memory.get(f"result_{peer_name}", self.name)
        print(f"[{self.name}] Read {peer_name}'s result: {result}")
        return result

# 사용 예시
shared_mem = SharedMemory()

agent_a = SharedMemoryAgent(name="AgentA", shared_memory=shared_mem)
agent_b = SharedMemoryAgent(name="AgentB", shared_memory=shared_mem)

# AgentA 작업 실행
agent_a.execute("Collect data from API")

# AgentB가 AgentA의 결과를 읽고 작업 수행
data = agent_b.read_peer_result("AgentA")
agent_b.execute(f"Process data: {data}")

# 메모리 접근 이력 확인
print("\nShared Memory History:")
for entry in shared_mem.get_history():
    print(f"{entry['timestamp']} - {entry['agent']}: {entry['action']} {entry['key']}")
```

**장점:**
- 복잡한 메시지 프로토콜 불필요
- Agent 간 상태 공유가 명확함

**단점:**
- 동시 접근 시 경합(race condition) 발생 가능
- 공유 메모리 크기 관리 필요

---

## 위임 전략

Orchestrator나 Manager Agent가 작업을 어떻게 분배할지 결정하는 전략입니다.

### 역할 기반 위임 (Role-based)

각 Agent의 역할(role)을 기준으로 작업을 할당합니다.

```python
class RoleBasedOrchestrator:
    """역할 기반 위임 Orchestrator"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.workers: Dict[str, WorkerAgent] = {}
        self.role_mapping: Dict[str, str] = {}  # role -> worker_name
    
    def register_worker(self, worker: WorkerAgent, role: str):
        """Worker 등록 (역할과 함께)"""
        self.workers[worker.name] = worker
        self.role_mapping[role] = worker.name
    
    def delegate_by_role(self, task: str) -> str:
        """작업 분석 후 역할에 맞는 Worker에게 위임"""
        # 작업에 필요한 역할 식별
        required_role = self._identify_required_role(task)
        
        # 해당 역할의 Worker 찾기
        worker_name = self.role_mapping.get(required_role)
        if worker_name and worker_name in self.workers:
            return self.workers[worker_name].execute(task)
        else:
            return f"No worker found for role: {required_role}"
    
    def _identify_required_role(self, task: str) -> str:
        """작업에 필요한 역할 식별"""
        available_roles = ", ".join(self.role_mapping.keys())
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""Identify which role is needed for this task.
Available roles: {available_roles}
Return only the role name."""},
                {"role": "user", "content": task}
            ],
            temperature=0
        )
        
        return response.choices[0].message.content.strip()

# 사용 예시
orchestrator = RoleBasedOrchestrator(api_key="your-api-key")

code_agent = WorkerAgent(name="CodeExpert", role="Python expert", api_key="your-api-key")
doc_agent = WorkerAgent(name="DocWriter", role="Documentation writer", api_key="your-api-key")

orchestrator.register_worker(code_agent, role="coding")
orchestrator.register_worker(doc_agent, role="documentation")

result = orchestrator.delegate_by_role("FastAPI로 REST API 만드는 방법 문서화해줘")
# "documentation" 역할 식별 → DocWriter에게 위임
```

**적용:**
- 작업 유형이 명확히 구분될 때
- 각 Agent가 특정 전문 분야를 담당할 때

---

### 능력 기반 위임 (Capability-based)

각 Agent의 능력(capability)을 점수화하고, 가장 적합한 Agent에게 할당합니다.

```python
class CapabilityBasedOrchestrator:
    """능력 기반 위임 Orchestrator"""
    
    def __init__(self):
        self.workers: Dict[str, WorkerAgent] = {}
        self.capabilities: Dict[str, Dict[str, float]] = {}  # worker_name -> {skill: score}
    
    def register_worker(self, worker: WorkerAgent, capabilities: Dict[str, float]):
        """Worker 등록 (능력 점수와 함께)"""
        self.workers[worker.name] = worker
        self.capabilities[worker.name] = capabilities
    
    def delegate_by_capability(self, task: str, required_skills: List[str]) -> str:
        """필요한 스킬에 가장 적합한 Worker 선택"""
        best_worker = None
        best_score = 0.0
        
        for worker_name, skills in self.capabilities.items():
            score = sum(skills.get(skill, 0) for skill in required_skills) / len(required_skills)
            if score > best_score:
                best_score = score
                best_worker = worker_name
        
        if best_worker:
            print(f"Selected {best_worker} (score: {best_score:.2f})")
            return self.workers[best_worker].execute(task)
        else:
            return "No suitable worker found"

# 사용 예시
orchestrator = CapabilityBasedOrchestrator()

agent_a = WorkerAgent(name="AgentA", role="generalist", api_key="your-api-key")
agent_b = WorkerAgent(name="AgentB", role="specialist", api_key="your-api-key")

orchestrator.register_worker(agent_a, capabilities={
    "python": 0.7,
    "javascript": 0.8,
    "documentation": 0.6
})

orchestrator.register_worker(agent_b, capabilities={
    "python": 0.95,
    "machine_learning": 0.9,
    "documentation": 0.5
})

result = orchestrator.delegate_by_capability(
    task="Python으로 머신러닝 모델 학습 코드 작성",
    required_skills=["python", "machine_learning"]
)
# AgentB 선택 (python: 0.95, machine_learning: 0.9)
```

**적용:**
- 여러 Agent가 비슷한 역할을 하지만 숙련도가 다를 때
- 작업 난이도에 따라 적절한 Agent 선택이 필요할 때

---

### 부하 기반 위임 (Load-based)

현재 부하가 가장 낮은 Agent에게 작업을 할당합니다.

```python
import time
from collections import defaultdict

class LoadBasedOrchestrator:
    """부하 기반 위임 Orchestrator"""
    
    def __init__(self):
        self.workers: Dict[str, WorkerAgent] = {}
        self.load: Dict[str, int] = defaultdict(int)  # worker_name -> task count
    
    def register_worker(self, worker: WorkerAgent):
        """Worker 등록"""
        self.workers[worker.name] = worker
        self.load[worker.name] = 0
    
    def delegate_with_load_balancing(self, task: str) -> str:
        """부하가 가장 낮은 Worker에게 위임"""
        # 부하가 가장 낮은 Worker 선택
        worker_name = min(self.load, key=self.load.get)
        
        # 부하 증가
        self.load[worker_name] += 1
        
        print(f"Delegating to {worker_name} (current load: {self.load[worker_name]})")
        
        # 작업 실행
        result = self.workers[worker_name].execute(task)
        
        # 작업 완료 후 부하 감소
        self.load[worker_name] -= 1
        
        return result

# 사용 예시
orchestrator = LoadBasedOrchestrator()

for i in range(3):
    worker = WorkerAgent(name=f"Worker{i}", role="general", api_key="your-api-key")
    orchestrator.register_worker(worker)

# 여러 작업 동시 처리
import concurrent.futures

tasks = [f"Task {i}" for i in range(10)]

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(orchestrator.delegate_with_load_balancing, task) for task in tasks]
    results = [f.result() for f in futures]

print(f"\nFinal load distribution: {dict(orchestrator.load)}")
```

**적용:**
- 여러 Agent가 동일한 작업을 수행할 수 있을 때
- 부하 분산이 중요할 때

---

## Multi-Agent가 필요한 상황

Multi-Agent 시스템을 도입하기 전에, 정말 필요한지 판단해야 합니다.

### 단일 Agent로 충분한 경우

```text
- 작업이 단일 도메인에 속함
- 순차 처리로 충분함
- 작업 흐름이 단순함
- 실시간성이 중요하지 않음
```

**예:** 문서 요약, 간단한 Q&A, 코드 생성

---

### Multi-Agent가 필요한 경우

#### 1. 다중 도메인 작업

```python
# 예: 프로젝트 기획서 작성
# - 시장 조사 (ResearchAgent)
# - 기술 스택 추천 (TechAgent)
# - 비용 산정 (FinanceAgent)
# - 문서 작성 (WriterAgent)
```

**단일 Agent 문제점:**
- 모든 도메인 지식을 한 Agent에 포함하면 컨텍스트가 과부하됩니다.
- 각 영역의 품질이 떨어질 수 있습니다.

**Multi-Agent 해결:**
- 각 도메인 전문 Agent가 담당합니다.
- Orchestrator가 결과를 종합합니다.

---

#### 2. 병렬 처리가 필요한 경우

```python
# 예: 여러 웹사이트 동시 크롤링
# - Agent1: site1.com 크롤링
# - Agent2: site2.com 크롤링
# - Agent3: site3.com 크롤링
# - Orchestrator: 결과 병합
```

**단일 Agent 문제점:**
- 순차 처리로 시간이 오래 걸립니다.

**Multi-Agent 해결:**
- 여러 Agent가 병렬로 작업합니다.
- 전체 실행 시간이 단축됩니다.

---

#### 3. 반복 협력이 필요한 경우

```python
# 예: 콘텐츠 제작 파이프라인
# 1. Writer: 초안 작성
# 2. Reviewer: 피드백 제공
# 3. Writer: 수정
# 4. Editor: 최종 편집
```

**단일 Agent 문제점:**
- Self-review가 제한적입니다 (자기 결과를 객관적으로 평가하기 어려움).

**Multi-Agent 해결:**
- 서로 다른 관점을 가진 Agent들이 협력합니다.
- 품질이 향상됩니다.

---

#### 4. 장기 실행 작업

```python
# 예: 지속적인 모니터링 시스템
# - MonitorAgent: 24시간 시스템 상태 감시
# - AlertAgent: 문제 감지 시 알림
# - AnalysisAgent: 로그 분석 및 리포트 생성
```

**단일 Agent 문제점:**
- 하나의 Agent가 모든 역할을 하면 과부하됩니다.
- 장애 시 전체 시스템 중단됩니다.

**Multi-Agent 해결:**
- 각 Agent가 독립적으로 실행됩니다.
- 한 Agent 장애 시에도 다른 Agent는 동작합니다.

---

### 의사결정 가이드

```text
Multi-Agent를 고려해야 하는 신호:
✓ "이 작업은 A 전문가와 B 전문가가 모두 필요해"
✓ "각 단계마다 다른 관점이 필요해"
✓ "작업을 병렬로 처리하면 훨씬 빠를 것 같아"
✓ "한 Agent가 모든 걸 하기엔 컨텍스트가 너무 커"

단일 Agent로 충분한 신호:
✓ "작업이 명확하고 단순해"
✓ "순차 처리로도 충분히 빨라"
✓ "하나의 역할만 있으면 돼"
✓ "실시간 응답이 중요해"
```

---

## 흔한 실수 5가지

### 실수 1: 불필요한 Multi-Agent 도입

**나쁜 예:**
```python
# 간단한 문서 요약에 3개 Agent 사용
orchestrator = OrchestratorAgent()
reader = WorkerAgent(name="Reader", role="read document")
summarizer = WorkerAgent(name="Summarizer", role="summarize")
formatter = WorkerAgent(name="Formatter", role="format output")
# 오버엔지니어링: 단일 Agent로 충분
```

**좋은 예:**
```python
# 단일 Agent로 처리
client = OpenAI(api_key="your-api-key")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Summarize the following document."},
        {"role": "user", "content": document}
    ]
)
```

**교훈**: Multi-Agent는 복잡성을 증가시킵니다. 정말 필요한 경우에만 사용합니다.

---

### 실수 2: Agent 간 통신 프로토콜 없음

**나쁜 예:**
```python
# 각 Agent가 자유 형식으로 메시지 전달
agent_a.send("여기 데이터야")
agent_b.send("고마워! 근데 이거 뭐야?")  # 메시지 형식이 통일되지 않음
```

**좋은 예:**
```python
# 표준 메시지 포맷 사용
message = AgentMessage(
    sender="AgentA",
    receiver="AgentB",
    message_type="data_transfer",
    content=json.dumps({"data": [1, 2, 3]}),
    metadata={"format": "json"},
    timestamp=datetime.now().isoformat()
)
broker.send_message(message)
```

**교훈**: 명확한 통신 프로토콜을 정의합니다.

---

### 실수 3: 무한 루프 방지 장치 없음

**나쁜 예:**
```python
# AgentA와 AgentB가 서로에게 계속 메시지 전송
agent_a.send_to(agent_b, "help")
# AgentB: "I need more info" → AgentA
# AgentA: "What info?" → AgentB
# AgentB: "I don't know" → AgentA
# 무한 루프
```

**좋은 예:**
```python
class SafePeerAgent:
    def __init__(self, name: str, max_exchanges: int = 5):
        self.name = name
        self.max_exchanges = max_exchanges
        self.exchange_count: Dict[str, int] = defaultdict(int)
    
    def send_message(self, recipient: str, message: str):
        # 같은 상대와의 교환 횟수 체크
        if self.exchange_count[recipient] >= self.max_exchanges:
            print(f"[{self.name}] Max exchanges reached with {recipient}")
            return
        
        self.exchange_count[recipient] += 1
        # 메시지 전송
```

**교훈**: Agent 간 교환 횟수를 제한합니다.

---

### 실수 4: Orchestrator가 모든 세부사항 관리

**나쁜 예:**
```python
# Orchestrator가 Worker의 내부 로직까지 관리
orchestrator.tell_worker("first, load data from DB, then clean it, then...")
# Worker의 자율성 제거
```

**좋은 예:**
```python
# Orchestrator는 "무엇을" 할지만 지시
orchestrator.delegate("CodeAgent", "Python API 호출 예제 작성")
# CodeAgent가 "어떻게" 할지 결정
```

**교훈**: Orchestrator는 조율만 하고, 실행 세부사항은 Worker에게 맡깁니다.

---

### 실수 5: Agent 실패 시 처리 없음

**나쁜 예:**
```python
# Agent 실패 시 전체 시스템 중단
result = worker.execute(task)  # 예외 발생 시 시스템 멈춤
```

**좋은 예:**
```python
try:
    result = worker.execute(task)
except Exception as e:
    print(f"Worker failed: {e}")
    # Fallback: 다른 Worker에게 재시도
    result = backup_worker.execute(task)
```

**교훈**: Agent 실패를 예상하고 fallback 전략을 준비합니다.

---

## 핵심 요약

- 복잡한 작업이나 다중 도메인 작업에는 Multi-Agent 시스템이 효과적입니다.
- Orchestrator, Peer-to-Peer, Hierarchical 등 다양한 조정 패턴이 있습니다.
- Agent 간 명확한 통신 프로토콜과 책임 분담이 성공의 열쇠입니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [컨텍스트 엔지니어링](./02-context-engineering.md)
- [Tool Use 기초](./03-tool-use-fundamentals.md)
- [Agent Workflow 설계](./04-agent-workflow-design.md)
- [Memory와 State](./05-memory-and-state.md)
- **Multi-Agent 시스템 (현재 글)**
- Agent 평가 (예정)
- 에러 처리와 안정성 (예정)
- 운영 (예정)
- 첫 Agent 만들기 (예정)

<!-- toc:end -->

---

## 참고 자료

1. **AutoGPT Multi-Agent Architecture** - https://github.com/Significant-Gravitas/AutoGPT  
   여러 Agent가 협력하는 자율 시스템 구현 예시. Orchestrator와 Worker 패턴을 보여줍니다.

2. **LangGraph Multi-Agent Systems** - https://langchain-ai.github.io/langgraph/tutorials/multi_agent/  
   LangGraph의 Multi-Agent 구현 튜토리얼. 메시지 라우팅과 상태 공유 방법을 다룹니다.

3. **CrewAI Documentation** - https://docs.crewai.com/  
   Role-based Multi-Agent 프레임워크. Agent 간 협업 패턴과 위임 전략을 설명합니다.

4. **Microsoft Semantic Kernel: Agent Orchestration** - https://learn.microsoft.com/en-us/semantic-kernel/agents/  
   Microsoft의 Agent Orchestration 가이드. 계층적 Agent 시스템 설계 방법을 제시합니다.

Tags: AI Agent, LLM, Tool Use, Python
