---
title: Tool Use 기초
series: ai-agent-101
episode: 3
language: ko
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Tool Use
- Function Calling
- Integration
last_reviewed: '2026-05-02'
---

# Tool Use 기초

> AI Agent 101 시리즈 (3/10)

Agent가 단순 대화 모델과 다른 이유는 도구를 사용할 수 있기 때문입니다. 날씨 API를 호출하고, 데이터베이스를 쿼리하고, 파일을 읽고 쓸 수 있습니다. 이 능력이 Agent를 실용적인 자동화 도구로 만듭니다.

Tool Use의 핵심은 Function Calling입니다. 모델이 "지금 날씨를 확인해야 한다"고 판단하면, 미리 정의된 도구 스키마에 맞춰 함수 호출 요청을 반환합니다. 애플리케이션은 이 요청을 해석해서 실제 API를 호출하고, 결과를 다시 모델에게 전달합니다.

이번 글에서는 Function Calling의 기본 흐름, 도구 스키마 설계 원칙, 에러 처리 패턴, 도구 선택 전략을 다룹니다.

---

## Function Calling 기본 흐름

Function Calling은 LLM이 "지금 이 도구를 사용해야 한다"고 판단하는 순간부터 시작합니다. 전체 흐름은 4단계로 구성됩니다.

### 1단계: 도구 등록

먼저 Agent에게 사용 가능한 도구 목록을 알려줍니다. 각 도구는 이름, 설명, 파라미터 스키마를 포함합니다.

```python
from typing import Callable

def get_weather(location: str, unit: str = "celsius") -> dict:
    """
    특정 지역의 현재 날씨를 조회합니다.
    
    Args:
        location: 도시 이름. 예: 'Seoul', 'New York'
        unit: 온도 단위. 'celsius' 또는 'fahrenheit'
    
    Returns:
        dict: {"temp": 25, "condition": "sunny", "humidity": 60}
    """
    # API 호출 로직
    return {"temp": 25, "condition": "sunny", "humidity": 60}

# 도구를 OpenAI function calling 형식으로 등록
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "특정 지역의 현재 날씨를 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "도시 이름 (예: Seoul, New York)"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "온도 단위"
                    }
                },
                "required": ["location"]
            }
        }
    }
]
```

### 2단계: LLM이 도구 호출 결정

사용자 질문을 받은 LLM은 등록된 도구 목록을 참고하여, 이 질문에 도구가 필요한지 판단합니다.

```python
from openai import OpenAI

client = OpenAI()

messages = [
    {"role": "user", "content": "서울 날씨 어때?"}
]

response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=tools,  # 등록된 도구 전달
    tool_choice="auto"  # 모델이 자동으로 판단
)

# LLM의 응답 확인
print(response.choices[0].message)
```

모델이 "날씨 조회가 필요하다"고 판단하면, `tool_calls` 필드에 호출 정보를 담아 반환합니다:

```python
{
    "role": "assistant",
    "content": null,
    "tool_calls": [
        {
            "id": "call_abc123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "Seoul", "unit": "celsius"}'
            }
        }
    ]
}
```

### 3단계: 도구 실행

애플리케이션이 `tool_calls`를 해석하여 실제 함수를 호출합니다.

```python
import json

# 도구 레지스트리 (함수 이름 → 실제 함수 매핑)
available_functions = {
    "get_weather": get_weather
}

# LLM 응답에서 tool_calls 추출
tool_calls = response.choices[0].message.tool_calls

# 각 도구 호출 처리
for tool_call in tool_calls:
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    
    # 실제 함수 호출
    function_to_call = available_functions[function_name]
    function_response = function_to_call(**function_args)
    
    print(f"Tool: {function_name}")
    print(f"Args: {function_args}")
    print(f"Result: {function_response}")
```

### 4단계: 결과를 LLM에게 전달

도구 실행 결과를 대화 기록에 추가하고, LLM에게 다시 전달합니다.

```python
# 도구 호출 결과를 메시지로 변환
messages.append(response.choices[0].message)  # LLM의 tool_calls 메시지
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "name": function_name,
    "content": json.dumps(function_response)
})

# 최종 응답 생성
final_response = client.chat.completions.create(
    model="gpt-4",
    messages=messages
)

print(final_response.choices[0].message.content)
# "서울의 현재 날씨는 맑고 기온은 25도입니다."
```

LLM은 도구 결과를 바탕으로 사용자에게 자연어 답변을 생성합니다.

AI 에이전트가 도구를 올바르게 사용하려면 도구가 무엇을 하는지, 어떤 입력을 받는지 명확하게 이해해야 합니다. 이를 위해 도구 스키마가 필요합니다.

### 스키마의 핵심 요소

**도구 이름(name)**: 도구의 기능을 명확하게 표현하는 이름입니다.

```python
# 나쁜 예: 모호한 이름
{
    "name": "tool1",  # 무엇을 하는 도구인가?
    "name": "get",    # 무엇을 가져오는가?
}

# 좋은 예: 명확한 이름
{
    "name": "get_weather",              # 날씨 조회
    "name": "search_customer_history",  # 고객 이력 검색
}
```

**설명(description)**: LLM이 도구 선택 시 참고하는 가장 중요한 정보입니다.

```python
# 나쁜 예: 불충분한 설명
{
    "name": "get_weather",
    "description": "날씨 정보를 가져옵니다"  # 언제? 어디? 어떤 형식?
}

# 좋은 예: 구체적인 설명
{
    "name": "get_weather",
    "description": "특정 지역의 현재 날씨 정보를 조회합니다. 도시 이름을 입력하면 온도, 습도, 날씨 상태를 반환합니다."
}
```

**파라미터(parameters)**: JSON Schema 형식으로 입력 값을 정의합니다.

```python
{
    "name": "get_weather",
    "description": "특정 지역의 현재 날씨를 조회합니다.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "도시 이름 (예: Seoul, New York)"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "온도 단위"
            }
        },
        "required": ["location"]  # location은 필수, unit은 선택
    }
}
```

### 타입 정의의 중요성

파라미터 타입을 명확히 정의하면 LLM이 올바른 형식으로 값을 생성합니다.

```python
# 나쁜 예: 타입 미정의
{
    "parameters": {
        "type": "object",
        "properties": {
            "date": {"type": "string"}  # 어떤 형식? YYYY-MM-DD? DD/MM/YYYY?
        }
    }
}

# 좋은 예: 형식 명시
{
    "parameters": {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "날짜 (YYYY-MM-DD 형식, 예: 2024-03-15)",
                "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
            }
        }
    }
}
```

### 복잡한 파라미터 구조

중첩된 객체나 배열도 표현할 수 있습니다.

```python
{
    "name": "create_order",
    "description": "새로운 주문을 생성합니다.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "고객 ID"
            },
            "items": {
                "type": "array",
                "description": "주문 항목 목록",
                "items": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string"},
                        "quantity": {"type": "integer", "minimum": 1}
                    },
                    "required": ["product_id", "quantity"]
                }
            }
        },
        "required": ["customer_id", "items"]
    }
}
```

### 실제 도구 등록 예시

```python
from typing import Dict, Any
import openai

# 도구 스키마 정의
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "특정 지역의 현재 날씨를 조회합니다. 온도, 습도, 날씨 상태를 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "도시 이름 (예: Seoul, Tokyo, New York)"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "온도 단위 (기본값: celsius)"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "문서 데이터베이스에서 키워드로 관련 문서를 검색합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색 키워드 또는 질문"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "반환할 최대 문서 수 (기본값: 5)",
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# LLM에 도구 정보 전달
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "서울 날씨 알려줘"}],
    tools=tools,
    tool_choice="auto"  # LLM이 자동으로 도구 선택
)
```

스키마를 명확하게 작성할수록 LLM이 도구를 올바르게 사용할 확률이 높아집니다.

도구 호출은 언제든지 실패할 수 있습니다. 네트워크 오류, 잘못된 파라미터, API 제한 초과 등 다양한 원인이 있습니다. 견고한 에이전트는 에러를 예상하고 적절히 처리합니다.

### 기본 에러 처리 패턴

```python
from typing import Dict, Any

def execute_tool_with_retry(
    tool_name: str,
    params: Dict[str, Any],
    max_retries: int = 3
) -> Dict[str, Any]:
    """도구 실행 + 재시도 로직"""
    for attempt in range(max_retries):
        try:
            result = execute_tool(tool_name, params)
            return {"success": True, "data": result}
        
        except ConnectionError as e:
            # 네트워크 오류: 재시도
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 지수 백오프
                continue
            return {"success": False, "error": f"Connection failed after {max_retries} attempts"}
        
        except ValueError as e:
            # 파라미터 오류: 재시도 불필요
            return {"success": False, "error": f"Invalid parameters: {str(e)}"}
        
        except Exception as e:
            # 예상치 못한 오류: 기록하고 반환
            log_error(tool_name, params, e)
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
```

### 에러 타입별 전략

**일시적 오류 (Transient Errors)**: 재시도로 해결 가능

```python
# 네트워크 타임아웃, 서비스 일시 중단
RETRYABLE_ERRORS = [
    ConnectionError,
    TimeoutError,
    requests.exceptions.Timeout,
]

def is_retryable(error: Exception) -> bool:
    """재시도 가능한 에러인지 판단"""
    return any(isinstance(error, err_type) for err_type in RETRYABLE_ERRORS)
```

**영구적 오류 (Permanent Errors)**: 즉시 실패 처리

```python
# 인증 오류, 잘못된 파라미터, 권한 없음
PERMANENT_ERRORS = [
    PermissionError,
    ValueError,
    KeyError,
]

def is_permanent(error: Exception) -> bool:
    """재시도 불가능한 에러인지 판단"""
    return any(isinstance(error, err_type) for err_type in PERMANENT_ERRORS)
```

### LLM에게 에러 정보 전달

에러가 발생하면 LLM이 다른 전략을 시도할 수 있도록 컨텍스트를 제공합니다.

```python
def handle_tool_error(
    tool_name: str,
    params: Dict[str, Any],
    error: Exception
) -> str:
    """에러를 LLM이 이해할 수 있는 메시지로 변환"""
    
    if isinstance(error, ConnectionError):
        return f"도구 '{tool_name}' 실행 실패: 네트워크 연결 오류. 잠시 후 다시 시도하거나 다른 방법을 사용하세요."
    
    elif isinstance(error, ValueError):
        return f"도구 '{tool_name}' 실행 실패: 잘못된 파라미터 '{params}'. 파라미터를 수정하여 다시 시도하세요."
    
    elif isinstance(error, PermissionError):
        return f"도구 '{tool_name}' 실행 실패: 권한 없음. 이 작업은 수행할 수 없습니다."
    
    else:
        return f"도구 '{tool_name}' 실행 실패: {str(error)}. 다른 접근 방법을 시도하세요."
```

### 우아한 성능 저하 (Graceful Degradation)

도구가 실패해도 에이전트가 계속 작동할 수 있도록 합니다.

```python
def agent_with_fallback(user_query: str) -> str:
    """도구 실패 시 대체 전략 사용"""
    
    # 1차 시도: 실시간 도구 사용
    weather_result = execute_tool_with_retry("get_weather", {"location": "Seoul"})
    
    if weather_result["success"]:
        return f"현재 서울 날씨: {weather_result['data']}"
    
    # 2차 시도: 캐시된 데이터 사용
    cached_data = get_cached_weather("Seoul")
    if cached_data:
        return f"최근 서울 날씨 (1시간 전): {cached_data}"
    
    # 3차 시도: LLM 지식 기반 응답
    return "죄송합니다. 현재 실시간 날씨 정보를 가져올 수 없습니다. 날씨 관련 일반적인 정보는 제공할 수 있습니다."
```

### 에러 로깅과 모니터링

프로덕션 환경에서는 에러를 기록하고 분석해야 합니다.

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def execute_tool_with_logging(
    tool_name: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """도구 실행 + 에러 로깅"""
    
    start_time = datetime.now()
    
    try:
        result = execute_tool(tool_name, params)
        
        # 성공 로그
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Tool '{tool_name}' succeeded in {duration}s")
        
        return {"success": True, "data": result}
    
    except Exception as e:
        # 실패 로그 (상세 정보 포함)
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(
            f"Tool '{tool_name}' failed in {duration}s",
            extra={
                "tool": tool_name,
                "params": params,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )
        
        return {"success": False, "error": str(e)}
```

### 타임아웃 설정

도구 실행이 무한정 기다리지 않도록 제한합니다.

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds: int):
    """함수 실행 시간 제한"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    # 타임아웃 설정
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # 타임아웃 해제
        signal.alarm(0)

# 사용 예시
try:
    with timeout(10):
        result = execute_tool("slow_api_call", {"param": "value"})
except TimeoutError:
    result = {"success": False, "error": "Tool execution timeout"}
```

에러 처리를 잘 구현하면 에이전트의 안정성과 신뢰성이 크게 향상됩니다.

에이전트가 여러 도구를 사용할 수 있을 때, 어떤 도구를 선택할지 결정하는 전략이 필요합니다.

### LLM 기반 자동 선택

OpenAI Function Calling에서는 `tool_choice` 파라미터로 선택 전략을 제어합니다.

```python
import openai

tools = [
    {"type": "function", "function": {...}},  # get_weather
    {"type": "function", "function": {...}},  # search_documents
]

# 전략 1: 자동 선택 (LLM이 판단)
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "서울 날씨 알려줘"}],
    tools=tools,
    tool_choice="auto"  # LLM이 필요하면 도구 사용
)

# 전략 2: 도구 사용 강제
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "서울 날씨 알려줘"}],
    tools=tools,
    tool_choice="required"  # 반드시 하나의 도구 호출
)

# 전략 3: 특정 도구 지정
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "서울 날씨 알려줘"}],
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "get_weather"}}
)

# 전략 4: 도구 사용 금지
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "서울 날씨 알려줘"}],
    tools=tools,
    tool_choice="none"  # 도구 사용 안 함
)
```

### 컨텍스트 기반 선택

사용자 쿼리의 의도에 따라 도구를 필터링할 수 있습니다.

```python
from typing import List, Dict, Any

def select_relevant_tools(
    user_query: str,
    all_tools: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """쿼리와 관련 있는 도구만 선택"""
    
    # 키워드 기반 필터링
    query_lower = user_query.lower()
    
    relevant_tools = []
    for tool in all_tools:
        tool_name = tool["function"]["name"]
        tool_desc = tool["function"]["description"]
        
        # 날씨 관련 쿼리 → 날씨 도구만
        if "날씨" in query_lower and "weather" in tool_name:
            relevant_tools.append(tool)
        
        # 문서 검색 쿼리 → 검색 도구만
        elif any(kw in query_lower for kw in ["검색", "찾아", "알려줘"]) and "search" in tool_name:
            relevant_tools.append(tool)
    
    # 관련 도구가 없으면 모든 도구 반환
    return relevant_tools if relevant_tools else all_tools
```

### 도구 우선순위 설정

자주 사용하거나 신뢰도가 높은 도구를 먼저 시도합니다.

```python
def execute_with_priority(
    tools: List[str],
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """우선순위 순서로 도구 실행"""
    
    # 우선순위: 1. 캐시 조회 2. 실시간 API 3. LLM 지식
    priority_order = ["check_cache", "api_call", "llm_knowledge"]
    
    for tool_name in priority_order:
        if tool_name not in tools:
            continue
        
        result = execute_tool(tool_name, params)
        
        if result["success"]:
            return result
    
    return {"success": False, "error": "All tools failed"}
```

### 도구 조합 (Tool Composition)

여러 도구를 순차적으로 사용하여 복잡한 작업을 수행합니다.

```python
def multi_tool_workflow(user_query: str) -> str:
    """여러 도구를 조합하여 답변 생성"""
    
    # 1단계: 문서 검색
    search_result = execute_tool("search_documents", {"query": user_query})
    
    if not search_result["success"]:
        return "검색 실패"
    
    documents = search_result["data"]
    
    # 2단계: 검색된 문서를 LLM에 전달하여 요약
    summary_prompt = f"""
    다음 문서를 바탕으로 질문에 답하세요.
    
    질문: {user_query}
    
    문서:
    {documents}
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    
    return response.choices[0].message.content
```

### 동적 도구 등록

런타임에 상황에 따라 도구를 추가하거나 제거합니다.

```python
class DynamicToolRegistry:
    """동적 도구 레지스트리"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    def register(self, tool_schema: Dict[str, Any]):
        """도구 등록"""
        tool_name = tool_schema["function"]["name"]
        self.tools[tool_name] = tool_schema
    
    def unregister(self, tool_name: str):
        """도구 제거"""
        if tool_name in self.tools:
            del self.tools[tool_name]
    
    def get_tools(self, context: str = None) -> List[Dict[str, Any]]:
        """컨텍스트에 맞는 도구 목록 반환"""
        
        if context == "weather":
            # 날씨 관련 도구만
            return [t for name, t in self.tools.items() if "weather" in name]
        
        elif context == "database":
            # 데이터베이스 관련 도구만
            return [t for name, t in self.tools.items() if "db" in name or "sql" in name]
        
        else:
            # 모든 도구
            return list(self.tools.values())

# 사용 예시
registry = DynamicToolRegistry()

# 기본 도구 등록
registry.register({
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "날씨 조회",
        "parameters": {...}
    }
})

# 사용자가 데이터베이스 작업을 요청하면 관련 도구 추가
if "데이터베이스" in user_query:
    registry.register({
        "type": "function",
        "function": {
            "name": "execute_sql",
            "description": "SQL 쿼리 실행",
            "parameters": {...}
        }
    })

# 컨텍스트에 맞는 도구만 LLM에 전달
tools = registry.get_tools(context="database")
```

### 도구 비용 고려

API 호출 비용이나 실행 시간을 고려하여 선택합니다.

```python
def select_tool_by_cost(
    query: str,
    available_tools: List[str]
) -> str:
    """비용 효율적인 도구 선택"""
    
    # 도구별 비용 (상대적)
    tool_costs = {
        "cache_lookup": 0,      # 무료
        "simple_api": 1,        # 저비용
        "expensive_api": 10,    # 고비용
        "llm_call": 5           # 중간 비용
    }
    
    # 쿼리 복잡도 분석
    if len(query.split()) <= 5:
        # 간단한 쿼리: 저비용 도구 우선
        preferred = ["cache_lookup", "simple_api"]
    else:
        # 복잡한 쿼리: 고비용 도구도 허용
        preferred = available_tools
    
    # 사용 가능한 도구 중 가장 저렴한 것 선택
    available_preferred = [t for t in preferred if t in available_tools]
    return min(available_preferred, key=lambda t: tool_costs.get(t, 999))
```

올바른 도구 선택 전략은 에이전트의 효율성과 비용을 크게 좌우합니다.

## 도구 선택 전략

도구 사용 시 자주 발생하는 실수들과 올바른 해결 방법을 살펴봅니다.

### 실수 1: 불명확한 도구 설명

**나쁜 예**: LLM이 도구의 용도를 정확히 파악할 수 없습니다.

```python
{
    "name": "get_data",
    "description": "데이터를 가져옵니다",  # 어떤 데이터? 어디서?
    "parameters": {
        "type": "object",
        "properties": {
            "id": {"type": "string"}  # 무엇의 ID?
        }
    }
}
```

**좋은 예**: 구체적인 설명으로 LLM이 올바르게 선택합니다.

```python
{
    "name": "get_customer_profile",
    "description": "고객 ID로 고객의 프로필 정보(이름, 이메일, 가입일)를 조회합니다. 고객 이력이나 주문 내역은 포함하지 않습니다.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "고객 고유 식별자 (예: CUST-12345)"
            }
        },
        "required": ["customer_id"]
    }
}
```

**교훈**: 도구 설명에는 "무엇을", "언제", "어떤 형식으로" 반환하는지 명시합니다.

### 실수 2: 에러 처리 누락

**나쁜 예**: 도구 실행 실패 시 에이전트가 멈춥니다.

```python
def execute_tool(tool_name: str, params: dict) -> dict:
    """도구 실행 (에러 처리 없음)"""
    if tool_name == "get_weather":
        # API 호출이 실패하면 Exception 발생
        return requests.get(f"https://api.weather.com/{params['location']}").json()
```

**좋은 예**: 에러를 잡아서 LLM에 전달합니다.

```python
def execute_tool(tool_name: str, params: dict) -> dict:
    """도구 실행 (에러 처리 포함)"""
    try:
        if tool_name == "get_weather":
            response = requests.get(
                f"https://api.weather.com/{params['location']}",
                timeout=5
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "API 타임아웃. 잠시 후 다시 시도하세요."
        }
    
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP 오류 {e.response.status_code}: {e.response.text}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"예상치 못한 오류: {str(e)}"
        }
```

**교훈**: 모든 도구 호출에 try-except를 적용하고, 에러 메시지를 LLM이 이해할 수 있게 작성합니다.

### 실수 3: 도구 결과를 무시

**나쁜 예**: 도구를 호출하고 결과를 확인하지 않습니다.

```python
def agent_loop(user_query: str) -> str:
    """에이전트 루프 (결과 미확인)"""
    decision = llm.decide_next_action(user_query)
    
    if decision["action"] == "use_tool":
        tool_result = execute_tool(decision["tool"], decision["params"])
        # 결과를 확인하지 않고 바로 최종 답변
        return "작업을 완료했습니다"
```

**좋은 예**: 결과를 확인하고 적절히 대응합니다.

```python
def agent_loop(user_query: str) -> str:
    """에이전트 루프 (결과 확인)"""
    decision = llm.decide_next_action(user_query)
    
    if decision["action"] == "use_tool":
        tool_result = execute_tool(decision["tool"], decision["params"])
        
        # 결과 확인
        if tool_result["success"]:
            # 성공: 결과를 LLM에 전달하여 최종 답변 생성
            return llm.generate_answer(user_query, tool_result["data"])
        else:
            # 실패: LLM에게 에러를 알리고 대체 전략 요청
            error_context = f"도구 실행 실패: {tool_result['error']}"
            return llm.decide_next_action(user_query, context=error_context)
```

**교훈**: 도구 결과의 `success` 필드를 항상 확인하고, 실패 시 대체 전략을 준비합니다.

### 실수 4: 너무 많은 도구 등록

**나쁜 예**: 모든 가능한 도구를 한 번에 등록합니다.

```python
# 50개의 도구를 한 번에 LLM에 전달
tools = [
    {"name": "get_weather", ...},
    {"name": "search_docs", ...},
    {"name": "send_email", ...},
    {"name": "query_database", ...},
    # ... 46 more tools
]

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "서울 날씨 알려줘"}],
    tools=tools  # 토큰 낭비, 선택 정확도 저하
)
```

**좋은 예**: 쿼리와 관련 있는 도구만 선택합니다.

```python
def get_relevant_tools(user_query: str, all_tools: list) -> list:
    """쿼리와 관련 있는 도구만 필터링"""
    query_lower = user_query.lower()
    
    # 키워드 기반 필터링
    if "날씨" in query_lower:
        return [t for t in all_tools if "weather" in t["function"]["name"]]
    elif "이메일" in query_lower:
        return [t for t in all_tools if "email" in t["function"]["name"]]
    else:
        # 기본 도구만 (최대 5개)
        return all_tools[:5]

# 관련 도구만 LLM에 전달
relevant_tools = get_relevant_tools(user_query, all_tools)

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": user_query}],
    tools=relevant_tools  # 3-5개 도구만
)
```

**교훈**: 한 번에 3-7개 도구만 LLM에 전달하여 토큰 비용과 선택 정확도를 최적화합니다.

### 실수 5: 도구 출력 형식을 검증하지 않음

**나쁜 예**: 도구가 반환한 데이터를 그대로 사용합니다.

```python
def get_weather(location: str) -> dict:
    """날씨 조회 (검증 없음)"""
    response = requests.get(f"https://api.weather.com/{location}")
    return response.json()  # 응답 형식을 가정

# 사용
weather = get_weather("Seoul")
temperature = weather["temp"]  # KeyError 발생 가능
```

**좋은 예**: 출력을 검증하고 일관된 형식으로 변환합니다.

```python
from typing import Optional

def get_weather(location: str) -> dict:
    """날씨 조회 (검증 포함)"""
    try:
        response = requests.get(f"https://api.weather.com/{location}", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # 응답 검증 및 표준화
        return {
            "success": True,
            "data": {
                "location": data.get("location", location),
                "temperature": data.get("temp", data.get("temperature", None)),
                "condition": data.get("condition", "unknown"),
                "humidity": data.get("humidity", None)
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# 사용
result = get_weather("Seoul")
if result["success"]:
    temp = result["data"]["temperature"]  # 안전하게 접근
    if temp is not None:
        print(f"현재 온도: {temp}°C")
```

**교훈**: 모든 도구는 일관된 형식(`{"success": bool, "data": ...}` 또는 `{"success": bool, "error": ...}`)을 반환하도록 설계합니다.

## 핵심 요약

- Tool Use는 Agent를 실용적인 자동화 도구로 만드는 핵심 기능입니다.
- 도구 스키마는 명확하고 구체적으로 작성해야 모델이 올바르게 호출합니다.
- 에러 처리와 도구 선택 전략이 Agent의 신뢰성을 결정합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [컨텍스트 엔지니어링](./02-context-engineering.md)
- **Tool Use 기초 (현재 글)**
- Agent Workflow 설계 (예정)
- Memory와 State (예정)
- Multi-Agent 시스템 (예정)
- Agent 평가 (예정)
- 에러 처리와 안정성 (예정)
- 운영 (예정)
- 첫 Agent 만들기 (예정)

<!-- toc:end -->

---

## 참고 자료

1. **OpenAI Function Calling Guide** - https://platform.openai.com/docs/guides/function-calling  
   OpenAI의 공식 Function Calling 문서. 도구 스키마 작성법, tool_choice 파라미터, 실전 예제를 제공합니다.

2. **LangChain Tools Documentation** - https://python.langchain.com/docs/modules/agents/tools/  
   LangChain 프레임워크의 도구 시스템. 커스텀 도구 작성, 에러 처리, 도구 조합 패턴을 다룹니다.

3. **Toolformer: Language Models Can Teach Themselves to Use Tools** - https://arxiv.org/abs/2302.04761  
   Meta AI의 연구 논문. LLM이 스스로 도구 사용법을 학습하는 방법을 제시합니다.

4. **Anthropic Tool Use Best Practices** - https://docs.anthropic.com/claude/docs/tool-use  
   Claude API의 도구 사용 가이드. 에러 처리, 재시도 전략, 보안 고려사항을 설명합니다.

Tags: AI Agent, LLM, Tool Use, Python
