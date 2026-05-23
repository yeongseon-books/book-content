---
title: "AI Agent 101 (5/10): Memory와 State"
series: ai-agent-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Memory
- State Management
- Context Window
last_reviewed: '2026-05-15'
seo_description: memory와 state를 분리해 context window를 관리하는 방법을 설명합니다.
---

# AI Agent 101 (5/10): Memory와 State

agent가 한두 번의 tool call로 끝나면 기억 문제는 크게 드러나지 않습니다. 하지만 대화가 길어지고, 여러 단계의 workflow가 누적되고, 사용자가 후속 질문을 던지기 시작하면 금세 다른 문제가 생깁니다. 이전 맥락을 얼마나 유지해야 하는지, 어떤 정보는 버려도 되는지, 무엇을 구조화된 상태로 저장해야 하는지가 중요해집니다.

많은 입문자가 memory와 state를 같은 것으로 다루지만, 운영에서는 둘을 분리하는 편이 훨씬 안전합니다. memory는 과거의 정보를 보존하는 방식에 가깝고, state는 현재 실행 위치를 나타내는 구조화된 레코드에 가깝습니다.

또한 모든 것을 프롬프트에 계속 붙여 넣는 방식은 오래 버티지 못합니다. context window는 유한하고, token 비용은 선형 이상으로 체감되며, 오래된 history가 오히려 최신 결정을 흐릴 수 있기 때문입니다.

이 글에서는 short-term memory, long-term memory, state를 분리해서 보고 어떤 정보를 어디에 둘지 결정하는 기준을 정리하겠습니다.

![메모리와 상태 분리](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/05/05-01-memory-and-state-split.ko.png)
*메모리와 상태 분리*
> Memory는 과거를 보존하는 층이고, state는 지금 실행이 어디까지 왔는지 말해 주는 층입니다.

## 먼저 던지는 질문

- agent memory와 state를 같은 저장소로 보면 어떤 설계 문제가 생길까요?
- short-term memory, long-term memory, execution state는 각각 언제 필요할까요?
- context window가 부족해질 때 무엇을 요약하고 무엇을 그대로 남겨야 할까요?

## 왜 이 글이 중요한가

memory 설계는 agent의 체감 품질을 결정합니다. 사용자가 같은 말을 반복하지 않게 해 주고, 긴 작업을 중간에 잊지 않게 해 주며, 후속 질문을 자연스럽게 이어 주기 때문입니다. 동시에 잘못 설계하면 비용과 오류를 폭발시키는 가장 빠른 길이 되기도 합니다.

운영에서는 특히 state 구분이 중요합니다. history만 길게 들고 가면 현재 workflow 위치를 복원하기 어렵고, 반대로 state만 남기면 사용자 선호나 이전 결정 근거를 잃기 쉽습니다. 두 층을 분리해야 재시작, checkpoint, retry가 모두 쉬워집니다.

또한 memory는 evaluation과도 연결됩니다. 어떤 정보를 저장했는지, 언제 불러왔는지, retrieval이 실제로 도움이 되었는지를 측정하지 않으면 "기억을 붙였더니 좋아졌다"는 막연한 인상만 남고 최적화는 멈춥니다.

## 핵심 관점

memory를 전부 하나의 "기억"으로 묶어 생각하면 설계가 금방 엉킵니다. 저는 보통 두 질문으로 분리합니다. 첫째, **무엇을 오래 보관할 것인가**. 둘째, **지금 어디까지 왔는가**. 첫 번째가 memory이고 두 번째가 state입니다.

이 구분이 있으면 데이터 저장소 선택도 쉬워집니다. 사용자 선호, 과거 요약, 지식 스니펫은 long-term memory 후보이고, 현재 단계, 완료 목록, 남은 작업은 state 후보입니다. 둘을 같은 구조에 섞어 두면 읽기도 어렵고 변경 충돌도 많아집니다.

실무에서는 "모든 대화를 다 넣자"보다 "현재 턴 판단에 필요한 최소 기억과 현재 위치만 넣자"가 훨씬 오래 버팁니다.

> 좋은 memory 설계는 많이 기억하는 것이 아니라, 오래 보관할 정보와 지금 실행에 필요한 상태를 분리해서 필요한 순간에만 꺼내 쓰는 것입니다.

## 핵심 개념

### memory와 state를 한 장의 흐름으로 보면 설계 경계가 선명해집니다

![memory와 state를 한 장의 흐름으로 보면 설계 경계가 선명해집니다](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/05/05-01-short-term-memory-vs-long-term-memory.ko.png)
*short-term memory는 현재 대화의 working set이고, state는 현재 실행 위치이며, long-term memory는 다음 세션에도 남겨 둘 정보라는 구분을 먼저 고정해 두면 설계가 덜 흔들립니다.*

### short-term memory는 현재 세션 안의 작업 맥락입니다

```python
from typing import List, Dict

class ShortTermMemory:
    """Short-term memory: retained only during current session"""

    def __init__(self, system_prompt: str):
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

    def add_user_message(self, content: str):
        """Add user message"""
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        """Add agent response"""
        self.messages.append({"role": "assistant", "content": content})

    def get_context(self) -> List[Dict[str, str]]:
        """Return current context"""
        return self.messages

    def clear(self):
        """Clear memory on session end"""
        system_msg = self.messages[0]
        self.messages = [system_msg]

# Usage example
memory = ShortTermMemory(system_prompt="You are a helpful assistant.")

memory.add_user_message("What's the weather today?")
memory.add_assistant_message("Today's weather in Seoul is sunny.")

memory.add_user_message("How about tomorrow?")
# Agent는 이전 대화("오늘 날씨")를 기억하고 "내일"이 날씨를 가리킨다는 것을 이해합니다.

print(f"Message count: {len(memory.get_context())}")  # 4 (system + user + assistant + user)
```

short-term memory는 가장 구현이 쉽지만 가장 빨리 비대해지는 층이기도 합니다. 대화가 길어질수록 그대로 LLM에 보내는 방식은 비싸지고, 오래된 메시지가 현재 판단을 왜곡할 가능성도 커집니다. 그래서 sliding window나 summary compaction이 뒤따라야 합니다.

### long-term memory는 세션 밖으로 꺼낸 정보입니다

```python
import json
from datetime import datetime
from typing import List, Dict, Optional

class LongTermMemory:
    """Long-term memory: permanently stored in external storage"""

    def __init__(self, storage_path: str = "memory.json"):
        self.storage_path = storage_path
        self.memories: Dict[str, List[Dict]] = self._load()

    def _load(self) -> Dict[str, List[Dict]]:
        """Load memory from storage"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save(self):
        """Save memory to storage"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    def add_memory(self, user_id: str, key: str, value: str):
        """Add information to user's memory"""
        if user_id not in self.memories:
            self.memories[user_id] = []

        self.memories[user_id].append({
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def retrieve_memory(self, user_id: str, key: Optional[str] = None) -> List[Dict]:
        """Retrieve user's memory"""
        if user_id not in self.memories:
            return []

        memories = self.memories[user_id]

        if key:
            # 키와 일치하는 메모리만 반환
            return [m for m in memories if m["key"] == key]

        return memories
```

long-term memory의 핵심은 모두를 매 턴 넣지 않는 데 있습니다. 저장은 넉넉하게 하되, retrieval은 좁게 해야 합니다. 사용자 선호, 과거 작업 요약, 반복적으로 쓰는 사실처럼 세션 밖에서도 가치가 남는 것만 저장하는 편이 좋습니다.

### 실제 시스템은 둘을 조합하되 state를 별도로 둡니다

```python
class HybridMemory:
    """Short-term memory + long-term memory combined"""

    def __init__(self, user_id: str, system_prompt: str):
        self.user_id = user_id
        self.short_term = ShortTermMemory(system_prompt)
        self.long_term = LongTermMemory()

    def start_session(self):
        """Load relevant information from long-term memory on session start"""
        memories = self.long_term.retrieve_memory(self.user_id)

        if memories:
            # 장기 메모리 내용을 system prompt에 추가
            context = "Previous user preferences:\n"
            for mem in memories:
                context += f"- {mem['key']}: {mem['value']}\n"

            self.short_term.messages[0]["content"] += f"\n\n{context}"

    def add_user_message(self, content: str):
        """Add user message"""
        self.short_term.add_user_message(content)

    def add_assistant_message(self, content: str):
        """Add agent response"""
        self.short_term.add_assistant_message(content)

    def save_important_info(self, key: str, value: str):
        """Save important information to long-term memory"""
        self.long_term.add_memory(self.user_id, key, value)

    def get_context(self) -> List[Dict[str, str]]:
        """Return current context"""
        return self.short_term.get_context()

    def end_session(self):
        """Session end: clear short-term memory"""
        self.short_term.clear()
```

이 예제는 memory 결합만 보여 주지만, production에서는 여기에 별도 `state` 객체를 함께 둡니다. 예를 들어 `current_step`, `completed_steps`, `pending_actions`, `retry_count` 같은 필드는 history 대신 state에 두는 편이 낫습니다. 그래야 재개와 복구가 쉬워집니다.

### 재시작 복구를 먼저 검증해 두면 state의 역할이 분명해집니다

아래 예시는 long-running workflow가 중간에 끊겨도 `state.json`만 있으면 어디서 다시 시작할지 복원하는 가장 작은 형태입니다.

```python
import json
from pathlib import Path

STATE_PATH = Path("state.json")

def save_state(step: str, completed: list[str]) -> None:
    STATE_PATH.write_text(
        json.dumps({"current_step": step, "completed": completed}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"current_step": "collect", "completed": []}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))

state = load_state()
print("before:", state)

if state["current_step"] == "collect":
    state["completed"].append("collect")
    state["current_step"] = "summarize"
    save_state(state["current_step"], state["completed"])

reloaded = load_state()
print("after:", reloaded)
```

**예상 출력:**

```text
before: {'current_step': 'collect', 'completed': []}
after: {'current_step': 'summarize', 'completed': ['collect']}
```

이 예시는 단순하지만 중요한 사실을 보여 줍니다. workflow 복구에 필요한 정보는 대화 원문 전체가 아니라 현재 위치와 완료 목록인 경우가 많습니다. 그래서 state를 history와 분리해 두면 복구 경로가 훨씬 짧아집니다.

### context window는 저장소가 아니라 working set입니다

- 현재 턴 의사결정에 직접 필요한 내용만 넣습니다.
- 오래된 대화는 summary로 압축합니다.
- 자주 재사용하는 사실은 long-term memory로 이동합니다.
- 현재 실행 위치는 별도 state 구조로 유지합니다.
- memory retrieval은 무조건 많이 넣기보다 precision을 우선합니다.

### failure mode를 state 관점에서 먼저 보면 memory 설계가 단단해집니다

- history만 길게 쌓고 current step을 따로 저장하지 않으면 재시작 후 어느 단계였는지 복원하기 어렵습니다.
- long-term memory에 사소한 대화까지 모두 저장하면 retrieval precision이 떨어져 오히려 현재 판단을 흐립니다.
- summary를 너무 공격적으로 줄이면 사용자의 제약 조건과 이전 결정 근거가 사라집니다.
- 반대로 아무 압축도 하지 않으면 context window와 비용이 먼저 한계에 닿습니다.

실무에서는 "다음 step 결정에 꼭 필요한가", "다음 세션에도 다시 써야 하는가" 두 질문으로 memory 저장 여부를 나누는 편이 좋습니다. 첫 질문에만 해당하면 short-term이나 state로, 두 번째 질문까지 해당하면 long-term memory로 보내는 식입니다.

## 실전 설계 보강

### 메모리 레이어를 분리하면 망각과 누수를 동시에 줄입니다

memory를 한 저장소로 몰아넣으면 초기에 단순하지만, 곧 품질 문제와 보안 문제가 함께 발생합니다. 운영에서는 단기 실행 상태, 세션 메모리, 장기 사용자 프로필을 분리하는 구조가 안전합니다.

| 레이어 | 저장 대상 | TTL | 접근 규칙 |
| --- | --- | --- | --- |
| 실행 상태 | 현재 run의 step 기록 | run 종료 시 삭제 | planner/validator만 읽기 |
| 세션 메모리 | 최근 대화/작업 요약 | 1~7일 | 사용자 범위 제한 |
| 장기 메모리 | 선호도, 금지 사항 | 30일~영구 | 명시적 동의 후 저장 |

### Redis 기반 세션 메모리 예시

```python
import json
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def save_session_memory(session_id: str, item: dict):
    key = f"agent:session:{session_id}"
    r.rpush(key, json.dumps(item, ensure_ascii=False))
    r.expire(key, 60 * 60 * 24 * 3)

def load_recent_memory(session_id: str, limit: int = 20) -> list[dict]:
    key = f"agent:session:{session_id}"
    rows = r.lrange(key, -limit, -1)
    return [json.loads(x) for x in rows]
```

TTL을 코드에서 강제하면 보존 기간 정책이 문서 의존에서 실행 의존으로 바뀝니다. 개인정보 규정 준수에서도 중요한 차이입니다.

### 메모리 검색 전 재랭킹 패턴

```python
def rerank(memories: list[dict], goal: str) -> list[dict]:
    # 단순 예시: goal 단어 중복 수로 점수 계산
    tokens = set(goal.lower().split())
    scored = []
    for m in memories:
        score = sum(1 for t in tokens if t in m.get("summary", "").lower())
        scored.append((score, m))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:8]]
```

메모리를 모두 프롬프트에 넣는 방식은 비용과 노이즈를 동시에 키웁니다. 검색 후 재랭킹을 거쳐 소수만 주입하는 구조가 더 안정적입니다.

### state corruption 감지 규칙

| 규칙 | 설명 |
| --- | --- |
| monotonic_step | step 번호가 감소하지 않아야 함 |
| immutable_goal | 실행 중 goal 변경 금지 |
| checksum_match | 직전 상태 해시와 연결 확인 |
| tool_result_schema | 도구 결과가 스키마를 만족해야 함 |

state corruption은 드물지만 발생하면 재현이 매우 어렵습니다. 기본 무결성 검사를 루프마다 넣어 두면 장기 운영에서 큰 차이를 만듭니다.

## 심화 운영 노트

### 운영 관점 실패 분류 템플릿

실전에서는 실패를 "모델이 틀렸다" 한 문장으로 닫지 않습니다. 다음 템플릿처럼 실패 축을 분리하면 개선 우선순위가 명확해집니다.

| 분류 축 | 질문 | 예시 |
| --- | --- | --- |
| 계획 실패 | 목표를 잘못 분해했는가 | 불필요한 step 6회 반복 |
| 실행 실패 | 도구 호출이 실패했는가 | timeout, 429, schema mismatch |
| 검증 실패 | 결과 확인이 부족했는가 | 잘못된 observation 채택 |
| 정책 실패 | 안전 경계를 넘었는가 | 민감 데이터 외부 전송 시도 |

이 표를 runbook에 고정해 두면 온콜 엔지니어가 같은 기준으로 사고를 분류할 수 있습니다.

### 프롬프트/도구 버전 고정 전략

변경 추적이 어려운 팀은 대부분 프롬프트와 도구 스키마를 코드 릴리스와 분리해 관리합니다. 안정적인 팀은 아래처럼 버전 필드를 요청 컨텍스트에 명시합니다.

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-ko-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

버전 필드만 있어도 회귀 분석 속도가 크게 빨라집니다. 특정 시점의 품질 저하가 모델 변경인지, 프롬프트 변경인지, 도구 변경인지 즉시 좁힐 수 있기 때문입니다.

### 관측성 이벤트 예시

```python
import json
from datetime import datetime

def emit_event(event_type: str, payload: dict):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "payload": payload,
    }
    print(json.dumps(record, ensure_ascii=False))

emit_event("agent.step", {"step": 2, "tool": "search_docs", "latency_ms": 412})
```

구조화 로그를 먼저 도입하면 추후 OpenTelemetry, ELK, Grafana 같은 스택으로 확장할 때 마이그레이션 비용이 낮아집니다.

### 배포 체크 항목

- 모델 API 키를 환경 변수와 Secret Manager로 분리했는지 확인합니다.
- `max_steps`, `timeout_ms`, `retry_budget` 기본값이 운영 프로필에 맞는지 검증합니다.
- 장애 시 fallback 응답 문구가 사용자에게 과장된 확신을 주지 않는지 점검합니다.
- 알람 임계치(`error_rate`, `p95_latency`, `policy_violation_rate`)를 문서와 코드에서 동일하게 유지합니다.

이 항목은 기능 개발보다 눈에 덜 띄지만, 실제 장애 빈도를 줄이는 데 직접적으로 기여합니다.

### 비용 통제 포인트

| 항목 | 설명 | 권장 기본값 |
| --- | --- | --- |
| max_steps | 1회 실행당 최대 루프 | 4~8 |
| max_tool_calls | 도구 호출 상한 | 3~6 |
| input_token_budget | 입력 토큰 예산 | 서비스별 정책 |
| output_token_budget | 출력 토큰 예산 | 서비스별 정책 |

비용 통제는 성능 최적화 이후에 붙이는 부가기능이 아닙니다. 처음부터 실행 예산을 고정해야 사용량 급증 시 서비스가 안정적으로 유지됩니다.

### 품질 회귀를 막는 CI 게이트 예시

```bash
python3 scripts/eval_agent.py --dataset eval/agent_core_ko.jsonl --min-success 0.82
python3 scripts/check_tool_schema.py --strict
python3 scripts/check_prompt_version.py --require-changelog
```

배포 파이프라인에서 최소 품질 게이트를 자동화하면 "우연히 좋아 보이는 빌드"가 운영으로 유입되는 일을 줄일 수 있습니다.

### 운영 관점 실패 분류 템플릿

실전에서는 실패를 "모델이 틀렸다" 한 문장으로 닫지 않습니다. 다음 템플릿처럼 실패 축을 분리하면 개선 우선순위가 명확해집니다.

| 분류 축 | 질문 | 예시 |
| --- | --- | --- |
| 계획 실패 | 목표를 잘못 분해했는가 | 불필요한 step 6회 반복 |
| 실행 실패 | 도구 호출이 실패했는가 | timeout, 429, schema mismatch |
| 검증 실패 | 결과 확인이 부족했는가 | 잘못된 observation 채택 |
| 정책 실패 | 안전 경계를 넘었는가 | 민감 데이터 외부 전송 시도 |

이 표를 runbook에 고정해 두면 온콜 엔지니어가 같은 기준으로 사고를 분류할 수 있습니다.

### 프롬프트/도구 버전 고정 전략

변경 추적이 어려운 팀은 대부분 프롬프트와 도구 스키마를 코드 릴리스와 분리해 관리합니다. 안정적인 팀은 아래처럼 버전 필드를 요청 컨텍스트에 명시합니다.

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-ko-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

버전 필드만 있어도 회귀 분석 속도가 크게 빨라집니다. 특정 시점의 품질 저하가 모델 변경인지, 프롬프트 변경인지, 도구 변경인지 즉시 좁힐 수 있기 때문입니다.

## 흔히 헷갈리는 지점

- history를 길게 유지하면 더 똑똑해질 것 같지만, 실제로는 비용과 혼선을 함께 키울 수 있습니다.
- memory와 state를 같은 dict에 넣으면 단기적으로 편해 보여도 재시도와 복구가 어려워집니다.
- long-term memory를 벡터 DB 하나로 끝내려 하기 쉽지만, 단순 key-value가 더 맞는 정보도 많습니다.
- 저장만 잘하면 된다고 생각하기 쉽지만, retrieval precision이 낮으면 오히려 해로운 컨텍스트가 들어옵니다.
- context window를 꽉 채우는 것이 활용이라고 생각하기 쉽지만, 실제로는 working set을 줄이는 편이 더 안정적입니다.

## 운영 체크리스트

- [ ] short-term memory와 long-term memory의 저장 기준이 분리되어 있는가
- [ ] 현재 workflow 위치를 나타내는 state 구조가 별도로 존재하는가
- [ ] 오래된 history를 요약하거나 압축하는 정책이 있는가
- [ ] long-term memory retrieval 결과를 그대로 넣지 않고 필터링하는가
- [ ] memory 사용량, retrieval hit, context length를 측정하고 있는가

## 정리

memory와 state는 agent를 오래 버티게 만드는 기반입니다. 하지만 둘을 구분하지 않으면 금세 비용이 커지고, 현재 위치를 잃고, 재시도와 복구가 어려워집니다. 그래서 좋은 설계의 출발점은 기억을 많이 남기는 것이 아니라 기억의 종류를 나누는 것입니다.

short-term memory는 현재 세션의 working set이고, long-term memory는 나중에 다시 꺼내 쓸 자산이며, state는 지금 어디까지 왔는지를 나타내는 제어 정보입니다. 이 세 층이 분리되면 workflow와 reliability와 evaluation이 모두 단단해집니다.

다음 글에서는 이 기반 위에서 여러 agent가 협업하는 multi-agent 시스템을 살펴봅니다. 역할이 늘어날수록 누가 어떤 state를 읽고 어떤 memory를 공유할지 더 명확히 설계해야 하기 때문입니다.

## 처음 질문으로 돌아가기

- **agent memory와 state를 같은 저장소로 보면 어떤 설계 문제가 생길까요?**
  - memory와 state를 섞으면 오래 보존해야 할 지식과 지금만 필요한 실행 위치가 뒤엉켜 재개, 요약, 삭제 기준이 흐려집니다.
- **short-term memory, long-term memory, execution state는 각각 언제 필요할까요?**
  - short-term memory는 현재 대화 맥락, long-term memory는 세션 밖에서도 검색할 지식, execution state는 현재 workflow 단계와 중간 결과를 담당합니다.
- **context window가 부족해질 때 무엇을 요약하고 무엇을 그대로 남겨야 할까요?**
  - 판단 근거와 tool 결과처럼 재현에 필요한 값은 정확히 남기고, 반복 대화나 오래된 설명은 요약해 context를 줄입니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent 101 (1/10): AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [AI Agent 101 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
- [AI Agent 101 (3/10): Tool Use 기초](./03-tool-use-fundamentals.md)
- [AI Agent 101 (4/10): Agent Workflow 설계](./04-agent-workflow-design.md)
- **AI Agent 101 (5/10): Memory와 State (현재 글)**
- AI Agent 101 (6/10): Multi-Agent 시스템 (예정)
- AI Agent 101 (7/10): Agent 평가 (예정)
- AI Agent 101 (8/10): 에러 처리와 안정성 (예정)
- AI Agent 101 (9/10): 운영 (예정)
- AI Agent 101 (10/10): 첫 Agent 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [LangGraph - Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [OpenAI Platform - Conversation state guide](https://platform.openai.com/docs/guides/conversation-state)
- [Anthropic - Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [LangChain - Memory overview](https://python.langchain.com/docs/concepts/chat_history/)

### 관련 시리즈

- [LangGraph 101 - 체크포인트와 상태 관리](../../langgraph-101/ko/02-state-and-checkpoints.md)
- [RAG 101 - 검색 컨텍스트 구성](../../multimodal-ai-101/ko/05-multimodal-rag.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-agent-101/ko/05-memory-and-state)

Tags: AI Agent, LLM, Tool Use, Python
