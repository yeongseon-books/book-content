---
title: Tool Use Fundamentals
series: ai-agent-101
episode: 3
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
- Tool Use
- Function Calling
- Integration
last_reviewed: '2026-05-15'
seo_description: Agents differ from simple conversational models because they can
  use tools. They can call weather APIs, query databases, read and write files.
---

# Tool Use Fundamentals

> AI Agent 101 Series (3/10)

Agents differ from simple conversational models because they can use tools. They can call weather APIs, query databases, read and write files. This capability makes agents practical automation tools.

The core of tool use is function calling. When the model determines "I need to check the weather now," it returns a function call request matching a predefined tool schema. The application interprets this request, calls the actual API, and passes the result back to the model.

This is post 3 in the AI Agent 101 series. Here we cover the basic flow of function calling, tool schema design principles, error handling patterns, and tool selection strategies.

---

<!-- a-grade-intro:begin -->

## Key Questions

- What does function calling actually look like from the model's side?
- What failures show up when a tool schema is poorly written?
- How does the model pick a tool when several are available?
- What do you need to watch when feeding tool output back into the model?

<!-- a-grade-intro:end -->

## Function Calling Basic Flow

The core mechanism that enables AI agents to interact with external systems is Function Calling (or Tool Use). Let's explore how this works step-by-step.

### Tool-calling loop

![Tool-calling loop](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/03/03-01-tool-calling-loop.en.png)
### The Four-Step Flow

**Step 1: Provide Tool Definitions to LLM**

When calling the LLM API, you register available tools in JSON Schema format.

```python
import openai

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Retrieves current weather for a specific location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., Seoul, New York)"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

response = openai.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": "What's the weather in Seoul?"}],
    tools=tools,
    tool_choice="auto"  # LLM decides whether to use tools
)
```

Use a model that currently supports tool calling, such as `gpt-4.1`, for examples like this. Keep `gpt-4` only when you are explicitly discussing a legacy setup.

**Step 2: LLM Decides to Call a Tool**

The LLM analyzes the user query and determines which tool to use.

```python
# Example response from LLM
{
    "role": "assistant",
    "content": null,
    "tool_calls": [
        {
            "id": "call_abc123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "Seoul"}'
            }
        }
    ]
}
```

**Step 3: Execute the Tool**

Your application executes the tool with the parameters provided by the LLM.

```python
import json

def execute_tool(tool_name: str, arguments: str) -> str:
    """Execute the requested tool and return results."""
    params = json.loads(arguments)
    
    if tool_name == "get_weather":
        # Call actual weather API
        weather_data = get_weather_api(params["location"])
        return json.dumps(weather_data)
    
    return json.dumps({"error": "Unknown tool"})

# Execute tool
tool_call = response.choices[0].message.tool_calls[0]
result = execute_tool(tool_call.function.name, tool_call.function.arguments)
```

**Step 4: Pass Results Back to LLM**

Send the tool execution result back to the LLM to generate a final response.

```python
# Add tool result to conversation
messages = [
    {"role": "user", "content": "What's the weather in Seoul?"},
    response.choices[0].message,  # Assistant's tool call
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result  # Tool execution result
    }
]

# Get final answer
final_response = openai.chat.completions.create(
    model="gpt-4.1",
    messages=messages
)

print(final_response.choices[0].message.content)
# Output: "The current weather in Seoul is sunny with a temperature of 15°C."
```

### Complete Agent Loop Example

Here's a full implementation with multi-iteration support:

```python
from typing import Dict, Any, List
import openai
import json

def agent_with_tools(
    user_query: str,
    tools: List[Dict[str, Any]],
    max_iterations: int = 5
) -> str:
    """Agent loop with tool support."""
    
    messages = [{"role": "user", "content": user_query}]
    
    for iteration in range(max_iterations):
        # Call LLM
        response = openai.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # Check if LLM wants to use a tool
        if not assistant_message.tool_calls:
            # No tool call = final answer ready
            return assistant_message.content
        
        # Add assistant's tool call to conversation
        messages.append(assistant_message)
        
        # Execute each tool call
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments
            
            # Execute tool
            result = execute_tool(tool_name, tool_args)
            
            # Add result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
    
    return "Max iterations reached without completion."

# Example usage
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Retrieves current weather information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    }
]

answer = agent_with_tools("What's the weather in Seoul?", tools)
print(answer)
```

### Why This Pattern Works

1. **Separation of Concerns**: LLM decides *what* to do; your code handles *how* to do it
2. **Flexibility**: Add new tools without retraining the model
3. **Reliability**: Tools use deterministic APIs instead of LLM hallucinations
4. **Iterative Reasoning**: Agent can use tool results to decide next actions

This four-step flow is the foundation of all AI agent systems. Master this pattern, and you'll understand how agents interact with the world.

For agents to use tools correctly, they must understand what each tool does and what inputs it expects. This is where tool schemas come in.

### Essential Schema Elements

**Tool Name**: A clear, descriptive name that indicates the tool's purpose.

```python
# Bad: Ambiguous names
{
    "name": "tool1",  # What does this do?
    "name": "get",    # Get what?
}

# Good: Clear names
{
    "name": "get_weather",              # Weather lookup
    "name": "search_customer_history",  # Customer history search
}
```

**Description**: The most critical information the LLM uses for tool selection.

```python
# Bad: Insufficient description
{
    "name": "get_weather",
    "description": "Gets weather information"  # When? Where? What format?
}

# Good: Specific description
{
    "name": "get_weather",
    "description": "Retrieves current weather information for a specific location. Takes a city name and returns temperature, humidity, and weather condition."
}
```

**Parameters**: Define input values using JSON Schema format.

```python
{
    "name": "get_weather",
    "description": "Retrieves current weather for a specific location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name (e.g., Seoul, New York)"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature unit"
            }
        },
        "required": ["location"]  # location is required, unit is optional
    }
}
```

### Importance of Type Definitions

Clear type definitions help the LLM generate values in the correct format.

```python
# Bad: Undefined type details
{
    "parameters": {
        "type": "object",
        "properties": {
            "date": {"type": "string"}  # What format? YYYY-MM-DD? DD/MM/YYYY?
        }
    }
}

# Good: Explicit format specification
{
    "parameters": {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "Date in YYYY-MM-DD format (e.g., 2024-03-15)",
                "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
            }
        }
    }
}
```

### Complex Parameter Structures

You can express nested objects and arrays.

```python
{
    "name": "create_order",
    "description": "Creates a new order.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "Customer ID"
            },
            "items": {
                "type": "array",
                "description": "List of order items",
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

### Real-World Tool Registration Example

```python
from typing import Dict, Any
import openai

# Define tool schemas
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Retrieves current weather for a specific location. Returns temperature, humidity, and weather condition.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., Seoul, Tokyo, New York)"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit (default: celsius)"
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
            "description": "Searches the document database for relevant documents using keywords.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keyword or question"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of documents to return (default: 5)",
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Pass tool information to LLM
response = openai.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": "What's the weather in Seoul?"}],
    tools=tools,
    tool_choice="auto"  # LLM automatically selects tool
)
```

The clearer your schema, the higher the probability the LLM will use the tool correctly.

Tool calls can fail at any time. Network errors, invalid parameters, API rate limits—there are many causes. Robust agents anticipate and handle errors appropriately.

### Basic Error Handling Pattern

```python
from typing import Dict, Any

def execute_tool_with_retry(
    tool_name: str,
    params: Dict[str, Any],
    max_retries: int = 3
) -> Dict[str, Any]:
    """Execute tool with retry logic."""
    for attempt in range(max_retries):
        try:
            result = execute_tool(tool_name, params)
            return {"success": True, "data": result}
        
        except ConnectionError as e:
            # Network error: retry
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return {"success": False, "error": f"Connection failed after {max_retries} attempts"}
        
        except ValueError as e:
            # Parameter error: no retry needed
            return {"success": False, "error": f"Invalid parameters: {str(e)}"}
        
        except Exception as e:
            # Unexpected error: log and return
            log_error(tool_name, params, e)
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
```

### Strategy by Error Type

**Transient Errors**: Retryable

```python
# Network timeouts, temporary service outages
RETRYABLE_ERRORS = [
    ConnectionError,
    TimeoutError,
    requests.exceptions.Timeout,
]

def is_retryable(error: Exception) -> bool:
    """Determine if error is retryable."""
    return any(isinstance(error, err_type) for err_type in RETRYABLE_ERRORS)
```

**Permanent Errors**: Fail immediately

```python
# Authentication errors, invalid parameters, permission denied
PERMANENT_ERRORS = [
    PermissionError,
    ValueError,
    KeyError,
]

def is_permanent(error: Exception) -> bool:
    """Determine if error is not retryable."""
    return any(isinstance(error, err_type) for err_type in PERMANENT_ERRORS)
```

### Communicating Errors to LLM

When errors occur, provide context so the LLM can try alternative strategies.

```python
def handle_tool_error(
    tool_name: str,
    params: Dict[str, Any],
    error: Exception
) -> str:
    """Convert error to LLM-understandable message."""
    
    if isinstance(error, ConnectionError):
        return f"Tool '{tool_name}' failed: Network connection error. Try again later or use an alternative method."
    
    elif isinstance(error, ValueError):
        return f"Tool '{tool_name}' failed: Invalid parameters '{params}'. Please correct the parameters and retry."
    
    elif isinstance(error, PermissionError):
        return f"Tool '{tool_name}' failed: Permission denied. This operation cannot be performed."
    
    else:
        return f"Tool '{tool_name}' failed: {str(error)}. Try a different approach."
```

### Graceful Degradation

Ensure the agent continues operating even when tools fail.

```python
def agent_with_fallback(user_query: str) -> str:
    """Use fallback strategy when tools fail."""
    
    # First attempt: real-time tool
    weather_result = execute_tool_with_retry("get_weather", {"location": "Seoul"})
    
    if weather_result["success"]:
        return f"Current weather in Seoul: {weather_result['data']}"
    
    # Second attempt: cached data
    cached_data = get_cached_weather("Seoul")
    if cached_data:
        return f"Recent weather in Seoul (1 hour ago): {cached_data}"
    
    # Third attempt: LLM knowledge-based response
    return "Sorry, real-time weather information is currently unavailable. I can provide general weather information."
```

### Error Logging and Monitoring

In production, log and analyze errors.

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def execute_tool_with_logging(
    tool_name: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute tool with error logging."""
    
    start_time = datetime.now()
    
    try:
        result = execute_tool(tool_name, params)
        
        # Success log
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Tool '{tool_name}' succeeded in {duration}s")
        
        return {"success": True, "data": result}
    
    except Exception as e:
        # Failure log with details
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

### Timeout Configuration

Prevent tool execution from waiting indefinitely.

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds: int):
    """Limit function execution time."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    # Set timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Clear timeout
        signal.alarm(0)

# Usage example
try:
    with timeout(10):
        result = execute_tool("slow_api_call", {"param": "value"})
except TimeoutError:
    result = {"success": False, "error": "Tool execution timeout"}
```

Proper error handling significantly improves agent stability and reliability.

When agents have multiple tools available, they need a strategy to decide which tool to use.

### LLM-Based Automatic Selection

With OpenAI Function Calling, the `tool_choice` parameter controls selection strategy.

```python
import openai

tools = [
    {"type": "function", "function": {...}},  # get_weather
    {"type": "function", "function": {...}},  # search_documents
]

# Strategy 1: Automatic selection (LLM decides)
response = openai.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": "What's the weather in Seoul?"}],
    tools=tools,
    tool_choice="auto"  # LLM uses tools when needed
)

# Strategy 2: Force tool use
response = openai.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": "What's the weather in Seoul?"}],
    tools=tools,
    tool_choice="required"  # Must call one tool
)

# Strategy 3: Specify tool
response = openai.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": "What's the weather in Seoul?"}],
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "get_weather"}}
)

# Strategy 4: Disable tools
response = openai.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": "What's the weather in Seoul?"}],
    tools=tools,
    tool_choice="none"  # No tool use
)
```

### Context-Based Selection

Filter tools based on user query intent.

```python
from typing import List, Dict, Any

def select_relevant_tools(
    user_query: str,
    all_tools: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Select tools relevant to query."""
    
    # Keyword-based filtering
    query_lower = user_query.lower()
    
    relevant_tools = []
    for tool in all_tools:
        tool_name = tool["function"]["name"]
        tool_desc = tool["function"]["description"]
        
        # Weather query → weather tools only
        if "weather" in query_lower and "weather" in tool_name:
            relevant_tools.append(tool)
        
        # Search query → search tools only
        elif any(kw in query_lower for kw in ["search", "find", "lookup"]) and "search" in tool_name:
            relevant_tools.append(tool)
    
    # Return all tools if no relevant tools found
    return relevant_tools if relevant_tools else all_tools
```

### Tool Prioritization

Try frequently-used or high-confidence tools first.

```python
def execute_with_priority(
    tools: List[str],
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute tools in priority order."""
    
    # Priority: 1. Cache lookup 2. Real-time API 3. LLM knowledge
    priority_order = ["check_cache", "api_call", "llm_knowledge"]
    
    for tool_name in priority_order:
        if tool_name not in tools:
            continue
        
        result = execute_tool(tool_name, params)
        
        if result["success"]:
            return result
    
    return {"success": False, "error": "All tools failed"}
```

### Tool Composition

Use multiple tools sequentially for complex tasks.

```python
def multi_tool_workflow(user_query: str) -> str:
    """Generate answer by combining multiple tools."""
    
    # Step 1: Search documents
    search_result = execute_tool("search_documents", {"query": user_query})
    
    if not search_result["success"]:
        return "Search failed"
    
    documents = search_result["data"]
    
    # Step 2: Pass documents to LLM for summarization
    summary_prompt = f"""
    Answer the question based on these documents.
    
    Question: {user_query}
    
    Documents:
    {documents}
    """
    
    response = openai.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    
    return response.choices[0].message.content
```

### Dynamic Tool Registration

Add or remove tools at runtime based on context.

```python
class DynamicToolRegistry:
    """Dynamic tool registry."""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    def register(self, tool_schema: Dict[str, Any]):
        """Register a tool."""
        tool_name = tool_schema["function"]["name"]
        self.tools[tool_name] = tool_schema
    
    def unregister(self, tool_name: str):
        """Remove a tool."""
        if tool_name in self.tools:
            del self.tools[tool_name]
    
    def get_tools(self, context: str = None) -> List[Dict[str, Any]]:
        """Return tools matching context."""
        
        if context == "weather":
            # Weather-related tools only
            return [t for name, t in self.tools.items() if "weather" in name]
        
        elif context == "database":
            # Database-related tools only
            return [t for name, t in self.tools.items() if "db" in name or "sql" in name]
        
        else:
            # All tools
            return list(self.tools.values())

# Usage example
registry = DynamicToolRegistry()

# Register base tools
registry.register({
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Weather lookup",
        "parameters": {...}
    }
})

# Add database tools when user requests database operations
if "database" in user_query:
    registry.register({
        "type": "function",
        "function": {
            "name": "execute_sql",
            "description": "Execute SQL query",
            "parameters": {...}
        }
    })

# Pass context-appropriate tools to LLM
tools = registry.get_tools(context="database")
```

### Cost Considerations

Select tools considering API call costs or execution time.

```python
def select_tool_by_cost(
    query: str,
    available_tools: List[str]
) -> str:
    """Select cost-efficient tool."""
    
    # Tool costs (relative)
    tool_costs = {
        "cache_lookup": 0,      # Free
        "simple_api": 1,        # Low cost
        "expensive_api": 10,    # High cost
        "llm_call": 5           # Medium cost
    }
    
    # Analyze query complexity
    if len(query.split()) <= 5:
        # Simple query: prefer low-cost tools
        preferred = ["cache_lookup", "simple_api"]
    else:
        # Complex query: allow high-cost tools
        preferred = available_tools
    
    # Select cheapest available tool
    available_preferred = [t for t in preferred if t in available_tools]
    return min(available_preferred, key=lambda t: tool_costs.get(t, 999))
```

The right tool selection strategy significantly impacts agent efficiency and cost.

## Tool Selection Strategies

Let's examine common mistakes when using tools and how to fix them.

### Mistake 1: Unclear Tool Descriptions

**Bad**: LLM cannot accurately understand the tool's purpose.

```python
{
    "name": "get_data",
    "description": "Gets data",  # What data? From where?
    "parameters": {
        "type": "object",
        "properties": {
            "id": {"type": "string"}  # ID of what?
        }
    }
}
```

**Good**: Specific description helps LLM make correct choices.

```python
{
    "name": "get_customer_profile",
    "description": "Retrieves customer profile information (name, email, signup date) by customer ID. Does not include customer history or order records.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "Unique customer identifier (e.g., CUST-12345)"
            }
        },
        "required": ["customer_id"]
    }
}
```

**Lesson**: Tool descriptions should specify "what", "when", and "in what format" they return.

### Mistake 2: Missing Error Handling

**Bad**: Agent stops when tool execution fails.

```python
def execute_tool(tool_name: str, params: dict) -> dict:
    """Execute tool (no error handling)"""
    if tool_name == "get_weather":
        # Throws Exception if API call fails
        return requests.get(f"https://api.weather.com/{params['location']}").json()
```

**Good**: Catch errors and communicate them to the LLM.

```python
def execute_tool(tool_name: str, params: dict) -> dict:
    """Execute tool (with error handling)"""
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
            "error": "API timeout. Please try again later."
        }
    
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP error {e.response.status_code}: {e.response.text}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }
```

**Lesson**: Apply try-except to all tool calls and write error messages the LLM can understand.

### Mistake 3: Ignoring Tool Results

**Bad**: Call tools and proceed without checking results.

```python
def agent_loop(user_query: str) -> str:
    """Agent loop (result not checked)"""
    decision = llm.decide_next_action(user_query)
    
    if decision["action"] == "use_tool":
        tool_result = execute_tool(decision["tool"], decision["params"])
        # Return final answer without checking result
        return "Task completed"
```

**Good**: Check results and respond appropriately.

```python
def agent_loop(user_query: str) -> str:
    """Agent loop (result checked)"""
    decision = llm.decide_next_action(user_query)
    
    if decision["action"] == "use_tool":
        tool_result = execute_tool(decision["tool"], decision["params"])
        
        # Check result
        if tool_result["success"]:
            # Success: pass result to LLM for final answer
            return llm.generate_answer(user_query, tool_result["data"])
        else:
            # Failure: inform LLM of error and request alternative strategy
            error_context = f"Tool execution failed: {tool_result['error']}"
            return llm.decide_next_action(user_query, context=error_context)
```

**Lesson**: Always check the `success` field in tool results and prepare fallback strategies for failures.

### Mistake 4: Registering Too Many Tools

**Bad**: Register all possible tools at once.

```text
# Pass 50 tools to LLM at once
tools = [
    {"name": "get_weather", ...},
    {"name": "search_docs", ...},
    {"name": "send_email", ...},
    {"name": "query_database", ...},
    # ... 46 more tools
]

response = openai.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": "What's the weather in Seoul?"}],
    tools=tools  # Token waste, reduced selection accuracy
)
```

**Good**: Select only query-relevant tools.

```python
def get_relevant_tools(user_query: str, all_tools: list) -> list:
    """Filter to query-relevant tools only."""
    query_lower = user_query.lower()
    
    # Keyword-based filtering
    if "weather" in query_lower:
        return [t for t in all_tools if "weather" in t["function"]["name"]]
    elif "email" in query_lower:
        return [t for t in all_tools if "email" in t["function"]["name"]]
    else:
        # Base tools only (max 5)
        return all_tools[:5]

# Pass only relevant tools to LLM
relevant_tools = get_relevant_tools(user_query, all_tools)

response = openai.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": user_query}],
    tools=relevant_tools  # 3-5 tools only
)
```

**Lesson**: Pass only 3-7 tools to LLM at a time to optimize token cost and selection accuracy.

### Mistake 5: Not Validating Tool Output Format

**Bad**: Use tool-returned data directly without validation.

```python
def get_weather(location: str) -> dict:
    """Weather lookup (no validation)"""
    response = requests.get(f"https://api.weather.com/{location}")
    return response.json()  # Assume response format

# Usage
weather = get_weather("Seoul")
temperature = weather["temp"]  # May raise KeyError
```

**Good**: Validate output and convert to consistent format.

```python
from typing import Optional

def get_weather(location: str) -> dict:
    """Weather lookup (with validation)"""
    try:
        response = requests.get(f"https://api.weather.com/{location}", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Validate and standardize response
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

# Usage
result = get_weather("Seoul")
if result["success"]:
    temp = result["data"]["temperature"]  # Safe access
    if temp is not None:
        print(f"Current temperature: {temp}°C")
```

**Lesson**: Design all tools to return consistent format (`{"success": bool, "data": ...}` or `{"success": bool, "error": ...}`).

## Key Takeaways

- Tool use is the core feature that makes agents practical automation tools.
- Tool schemas must be clear and specific for models to call them correctly.
- Error handling and tool selection strategies determine agent reliability.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Defined one tool with the OpenAI function-calling spec and exercised it.
- [ ] Observed how a bad schema confuses the model.
- [ ] Logged which tool the model picks when given 2-3 candidates.
- [ ] Closed the loop: tool output back into the model for the final answer.

<!-- a-grade-example:end -->

<!-- toc:begin -->
## In this series

- [What Is an AI Agent?](./01-what-is-an-ai-agent.md)
- [Context Engineering](./02-context-engineering.md)
- **Tool Use Fundamentals (current)**
- Agent Workflow Design (upcoming)
- Memory and State (upcoming)
- Multi-Agent Systems (upcoming)
- Agent Evaluation (upcoming)
- Error Handling and Reliability (upcoming)
- Production Operations (upcoming)
- Building Your First Agent (upcoming)

<!-- toc:end -->

---

## References

- [OpenAI function calling guide](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic tool use overview](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview)
- [LangChain tools](https://python.langchain.com/docs/concepts/tools/)
- [JSON Schema reference](https://json-schema.org/understanding-json-schema)

Tags: AI Agent, LLM, Tool Use, Python
