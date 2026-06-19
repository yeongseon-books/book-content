---
title: "LangGraph 101 (3/6): 조건부 엣지와 분기 흐름"
series: langgraph-101
episode: 3
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/73"
    published_at: '2026-05-12'
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LangGraph
- Agent
- Python
- LLM
last_reviewed: '2026-05-14'
seo_description: 조건부 엣지로 상태에 따라 다음 노드를 런타임에 선택하는 분기 그래프 패턴을 정리합니다
---

# LangGraph 101 (3/6): 조건부 엣지와 분기 흐름

에이전트가 언제나 한 경로만 따른다면 그래프는 생각보다 단순합니다. 하지만 실제 시스템은 거의 그렇지 않습니다. 어떤 요청은 코드 생성으로 가야 하고, 어떤 요청은 개념 설명으로, 어떤 요청은 오류 분석으로 보내야 합니다. 이 분기 판단을 긴 `if/elif/else` 안에 묻어 두면 실행은 되지만, 왜 그 길을 탔는지는 바로 흐려집니다.

이 글은 LangGraph 101 시리즈의 세 번째 글입니다. 여기서는 조건부 엣지를 단순한 분기 문법이 아니라, 상태를 읽고 다음 경로를 공개적으로 결정하는 라우팅 계층으로 봅니다.

운영에서 더 까다로운 순간은 분기 실패가 조용히 시작될 때입니다. 분류 라벨 하나가 비어 있고, 예상 밖 문자열 하나가 흘러들어오고, default 경로 하나가 빠져 있는 순간 겉으로는 "가끔 이상한 입력에서만 실패하는 시스템"처럼 보이기 쉽습니다. 하지만 실제로는 모델 품질보다 **라우팅 계약이 약한 구조 문제**인 경우가 더 많습니다.

여기에 루프까지 겹치면 비용은 더 빨리 커집니다. 잘못된 route 하나가 실행을 반복되면 안 되는 노드들 사이로 튕기게 만들 수도 있고, 멈춰야 할 워크플로를 계속 앞으로 밀어낼 수도 있습니다. 현업에서 저는 이런 상황이 종종 "모델이 예측 불가능하다"는 말로 포장되는 장면을 봤습니다. 하지만 생산 환경에서 더 근본적인 원인은 대개 분기 규칙이 충분히 명시적이지 않았다는 데 있습니다.

여기서는 조건부 엣지를 단순한 편의 문법이 아니라, **그래프가 다음 노드를 공개적으로 선택하는 의사결정 지점**으로 이해해 보겠습니다. 핵심은 분명합니다. **Conditional Edge는 상태를 읽고, 그 상태를 다음 경로 선택으로 번역하며, 라우팅 경계를 코드 구조 위로 드러내는 장치**입니다.

![classify 노드에서 세 갈래로 분기하는 구조](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/03/03-01-minimal-runnable-example.ko.png)
*classify 노드에서 세 갈래로 분기하는 구조*

> 조건부 엣지는 if문을 예쁘게 포장한 것이 아니라, 그래프가 왜 그 경로로 갔는지 설명하게 만드는 라우팅 계약입니다.

## 이 글에서 다룰 문제

- 조건부 엣지는 단순 if문과 무엇이 다르게 그래프 실행을 통제할까요?
- 분기 함수가 예상하지 못한 값을 돌려주면 어떤 실패가 생길까요?
- default route를 코드로 고정해 두면 운영에서 어떤 디버깅이 쉬워질까요?
- 루프가 있는 그래프에서 종료 조건은 어떻게 설계해야 할까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 구조가 중요한가

조건부 엣지를 배우는 이유를 "그래프를 branch할 수 있으니까"라고만 설명하면 너무 약합니다. 더 현실적인 이유는 설명 가능한 라우팅입니다. 에이전트가 여러 역할을 맡기 시작하는 순간, 팀은 반드시 "왜 이 요청이 이 노드로 갔는가"를 설명할 수 있어야 합니다.

예를 들어 어떤 질문은 코드 작성으로 보내고, 어떤 질문은 개념 설명으로 보내고, 어떤 질문은 디버깅 흐름으로 보내야 한다고 해 보겠습니다. 이 판단을 한 노드 안의 긴 `if/elif/else`에만 숨겨 두면 동작은 합니다. 하지만 "왜 debug로 분기됐지?", "왜 여기서는 concept로 빠졌지?", "왜 종료 안 하고 다시 classify로 돌아갔지?" 같은 질문에 답하기가 급격히 어려워집니다.

저는 팀들이 이 지점을 과소평가하다가, 나중에 LangSmith 추적 화면만 붙잡고 있는 장면을 자주 봤습니다. 관측 도구가 있어도 구조가 숨겨져 있으면 해석이 어렵습니다. 반대로 분기 근거가 상태 필드와 path map으로 드러나 있으면, 로그와 state snapshot만으로도 의사결정을 재구성할 수 있습니다.

그래서 이 글의 목표는 조건부 엣지 API를 외우는 데 있지 않습니다. 더 중요한 목표는 **분기 로직을 그래프 구조 위로 끌어올릴 때 운영 난이도가 왜 내려가는지**를 이해하는 데 있습니다.

---

## 분기 흐름 다이어그램으로 먼저 그려보기

코드를 작성하기 전에 분기 흐름을 텍스트로 먼저 그려 두면 라우팅 계약이 훨씬 선명해집니다.

```text
START
  |
  v
[classify_question]
  - 읽는 필드: question
  - 쓰는 필드: route
  |
  v (조건부 엣지: route 값에 따라 분기)
  |
  +-- route == "code"    --> [answer_code]    --> END
  |
  +-- route == "concept" --> [answer_concept] --> END
  |
  +-- route == "debug"   --> [answer_debug]   --> END
  |
  +-- route == "fallback" -> [answer_fallback] -> END
```

이 다이어그램에서 핵심은 두 가지입니다. 첫째, `classify_question`이 라우팅 결정을 하고 그 결과를 `route` 필드에 남깁니다. 둘째, 조건부 엣지는 그 `route` 값을 읽어서 실제 다음 노드를 결정합니다. 분류와 라우팅 실행이 분리되어 있습니다.

이 분리가 중요한 이유는, "왜 code로 갔는가"를 물었을 때 `route` 필드를 보면 바로 알 수 있기 때문입니다. 분류 로직이 노드 안에 있고 라우팅 결과가 상태에 남아 있으면, 추적이 쉬워집니다.

---

## Conditional Edge를 라우팅 계약으로 읽기

조건부 엣지에서 가장 먼저 잡아야 할 문장은 이것입니다. **Conditional Edge는 그래프의 의사결정 지점**입니다. 저는 이 표현이 가장 실용적이라고 생각합니다. 노드가 상태를 만들고, 라우터가 그 상태를 읽고, 조건부 엣지가 다음 노드를 확정합니다. 즉, 분기 판단이 코드 안쪽에 숨어 있지 않고 그래프 위에 드러납니다.

많은 입문자가 조건부 엣지를 "`if/else`를 그래프로 옮긴 것" 정도로 이해합니다. 절반은 맞지만, 절반은 놓칩니다. 중요한 차이는 분기 결과가 **구조와 상태에 명시적으로 남는다**는 점입니다. 이게 있어야 fallback 경로, 종료 조건, loop 안전장치를 모두 같은 모델 안에서 다룰 수 있습니다.

가장 단순하게 정리하면 아래 표처럼 볼 수 있습니다.

| 구성 요소 | 역할 | 실무에서 왜 중요한가 |
| --- | --- | --- |
| **분류 노드** | 요청을 읽고 라우팅 근거를 상태에 기록 | 왜 특정 경로 후보가 나왔는지 흔적을 남깁니다 |
| **라우터 함수** | 상태를 보고 다음 라벨을 반환 | 부작용 없는 의사결정 계층을 분리할 수 있습니다 |
| **조건부 엣지** | 라벨을 실제 대상 노드로 매핑 | 분기 계약을 코드 구조에서 읽을 수 있습니다 |
| **default / fallback 경로** | 예상 밖 라벨이나 미분류 상태를 처리 | dead-end와 불규칙 실패를 줄입니다 |
| **종료 조건** | 루프와 분기를 언제 멈출지 정의 | 무한 branching과 runaway cost를 막습니다 |

---

## 최소 실행 예제

가장 작은 분기 예제로 보겠습니다. 사용자의 질문을 읽고 `code`, `concept`, `debug`, `fallback` 넷 중 하나로 분류한 뒤, 조건부 엣지로 다음 노드를 선택하는 구조입니다. 처음부터 fallback을 포함해서 운영 준비가 된 구조를 보여드리겠습니다.

```python
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class RouterState(TypedDict):
    question: str
    route: str
    answer: str


def classify_question(state: RouterState) -> dict:
    """질문 유형을 분류하고 route 필드에 기록합니다."""
    text = state["question"].lower()

    if any(word in text for word in ("버그", "에러", "오류", "traceback", "bug", "error")):
        route = "debug"
    elif any(word in text for word in ("코드", "구현", "작성", "code", "implement", "write")):
        route = "code"
    elif any(word in text for word in ("무엇", "왜", "설명", "what", "why", "explain", "concept")):
        route = "concept"
    else:
        route = "fallback"

    return {"route": route}


def route_question(state: RouterState) -> Literal["code", "concept", "debug", "fallback"]:
    """상태의 route 값을 읽어 다음 노드를 결정합니다 (부작용 없음)."""
    route = state.get("route", "").strip().lower()
    if route in {"code", "concept", "debug"}:
        return route  # type: ignore[return-value]
    return "fallback"


def answer_code(_: RouterState) -> dict:
    return {"answer": "[code 경로] 코드 생성 또는 코드 리뷰 작업을 수행합니다."}


def answer_concept(_: RouterState) -> dict:
    return {"answer": "[concept 경로] 개념을 명확하게 설명합니다."}


def answer_debug(_: RouterState) -> dict:
    return {"answer": "[debug 경로] 실패 원인을 분석하고 해결 방향을 제시합니다."}


def answer_fallback(state: RouterState) -> dict:
    return {
        "answer": (
            f"[fallback 경로] 분류기가 '{state.get('route', 'unknown')}' 라벨을 반환했습니다. "
            "가장 안전한 설명 경로로 처리합니다."
        )
    }


def build_graph():
    graph = StateGraph(RouterState)

    # 노드 등록
    graph.add_node("classify", classify_question)
    graph.add_node("code", answer_code)
    graph.add_node("concept", answer_concept)
    graph.add_node("debug", answer_debug)
    graph.add_node("fallback", answer_fallback)

    # 엣지: START -> classify
    graph.add_edge(START, "classify")

    # 조건부 엣지: classify 이후 route 값에 따라 분기
    graph.add_conditional_edges(
        "classify",
        route_question,
        {
            "code": "code",
            "concept": "concept",
            "debug": "debug",
            "fallback": "fallback",
        },
    )

    # 모든 말단 노드 -> END
    graph.add_edge("code", END)
    graph.add_edge("concept", END)
    graph.add_edge("debug", END)
    graph.add_edge("fallback", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    test_questions = [
        "Python으로 퀵소트를 구현해 주세요.",
        "LangGraph의 체크포인트란 무엇인가요?",
        "그래프를 실행하면 traceback이 발생합니다.",
        "오늘 점심 뭐 먹을까요?",  # fallback 케이스
    ]

    for question in test_questions:
        result = app.invoke({"question": question, "route": "", "answer": ""})
        print(f"질문: {question}")
        print(f"라우트: {result['route']}")
        print(f"답변: {result['answer']}\n")
```

**예상 출력:**

```text
질문: Python으로 퀵소트를 구현해 주세요.
라우트: code
답변: [code 경로] 코드 생성 또는 코드 리뷰 작업을 수행합니다.

질문: LangGraph의 체크포인트란 무엇인가요?
라우트: concept
답변: [concept 경로] 개념을 명확하게 설명합니다.

질문: 그래프를 실행하면 traceback이 발생합니다.
라우트: debug
답변: [debug 경로] 실패 원인을 분석하고 해결 방향을 제시합니다.

질문: 오늘 점심 뭐 먹을까요?
라우트: fallback
답변: [fallback 경로] 분류기가 'fallback' 라벨을 반환했습니다. 가장 안전한 설명 경로로 처리합니다.
```

이 예제는 단순해 보여도 운영에서 중요한 것을 세 가지 보여 줍니다. 첫째, `classify_question()`이 라우팅 근거를 `route` 필드에 남기기 때문에 결과 문자열만 보지 않아도 분기 이유를 추적할 수 있습니다. 둘째, `route_question()`은 부작용 없이 다음 라벨만 반환해서, 의사결정과 실제 작업 노드를 분리합니다. 셋째, fallback을 처음부터 포함했기 때문에 예상 밖 입력도 안전하게 처리됩니다.

---

## 라우터 함수 설계 원칙

`route_question()` 같은 라우터 함수는 가능한 한 순수 함수(pure function)여야 합니다. 순수 함수란 외부 상태를 변경하지 않고, 같은 입력에 항상 같은 출력을 반환하는 함수입니다.

**좋은 라우터 함수의 특징:**

```python
# 좋은 예: 상태를 읽고 라벨만 반환
def route_question(state: RouterState) -> Literal["code", "concept", "debug", "fallback"]:
    route = state.get("route", "").strip().lower()
    if route in {"code", "concept", "debug"}:
        return route  # type: ignore[return-value]
    return "fallback"  # 안전한 기본값
```

**피해야 할 라우터 함수 패턴:**

```python
# 나쁜 예: 라우터 함수에서 부작용 발생
def route_question_bad(state: RouterState) -> str:
    # 외부 API 호출 - 라우터에서 하면 안 됨
    response = external_api.classify(state["question"])
    # 상태 변경 - 라우터에서 하면 안 됨
    state["route"] = response.label
    # 로그 기록 - 라우터가 아닌 노드에서 해야 함
    logger.info(f"Routing to: {response.label}")
    return response.label
```

라우터 함수에 부작용을 넣으면 "라우팅 중 무슨 일이 있었는가"와 "왜 이 route가 나왔는가"가 뒤섞입니다. 외부 API 호출이 필요하다면 분류 노드(`classify_question`)에서 하고, 그 결과를 상태에 저장한 뒤, 라우터 함수는 그 상태를 읽기만 해야 합니다.

---

## default route를 코드로 고정해 두기

처음부터 fallback을 포함한 예제를 보여드렸지만, 기존 코드에 fallback을 추가하는 방법도 알아보겠습니다. 핵심은 라우터 함수에서 알 수 없는 라벨을 처리하고, path map에 fallback 노드를 포함하는 것입니다.

```python
from typing import Literal

# 확장된 라우터: 알 수 없는 라벨 처리
def route_question_safe(
    state: RouterState,
) -> Literal["code", "concept", "debug", "fallback"]:
    """알 수 없는 route 값을 fallback으로 안전하게 처리합니다."""
    route = state.get("route", "").strip().lower()
    valid_routes = {"code", "concept", "debug"}
    if route in valid_routes:
        return route  # type: ignore[return-value]

    # 알 수 없는 라벨이면 fallback
    # 이 경우를 로그로 남기면 분류기 품질 개선에 도움됨
    print(f"[경고] 알 수 없는 route: '{route}', fallback으로 처리")
    return "fallback"
```

**예상 출력 (알 수 없는 라벨):**

```text
[경고] 알 수 없는 route: 'other', fallback으로 처리

질문: 이상한 질문입니다.
라우트: fallback
답변: [fallback 경로] 분류기가 'fallback' 라벨을 반환했습니다. 가장 안전한 설명 경로로 처리합니다.
```

이 코드는 분기 구조를 과하게 복잡하게 만들지 않으면서도, "정의되지 않은 route는 어디로 가는가?"라는 운영 질문에 바로 답을 줍니다. 분기가 늘어날수록 이 fallback 경로는 선택지가 아니라 안전장치에 가까워집니다.

---

## 루프가 있는 분기 그래프 설계

조건부 엣지는 단순한 일회성 분기만이 아니라, 루프를 제어하는 데도 사용됩니다. 예를 들어 검토 노드가 품질 기준을 통과하지 못하면 재작업 노드로 돌아가는 구조입니다.

```python
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class ReviewState(TypedDict):
    content: str
    review_result: str
    attempt: int
    final_output: str


MAX_ATTEMPTS = 3  # 최대 재시도 횟수


def generate_content(state: ReviewState) -> dict:
    """콘텐츠를 생성합니다 (실제로는 LLM 호출)."""
    attempt = state.get("attempt", 0) + 1
    # 시뮬레이션: 3번째 시도에서 통과
    if attempt >= 3:
        content = f"[시도 {attempt}] 품질 기준을 통과한 콘텐츠"
    else:
        content = f"[시도 {attempt}] 아직 개선이 필요한 콘텐츠"
    return {"content": content, "attempt": attempt}


def review_content(state: ReviewState) -> dict:
    """콘텐츠 품질을 검토합니다."""
    if "통과" in state["content"]:
        return {"review_result": "pass"}
    elif state.get("attempt", 0) >= MAX_ATTEMPTS:
        return {"review_result": "max_attempts_reached"}
    else:
        return {"review_result": "revise"}


def decide_after_review(
    state: ReviewState,
) -> Literal["generate", "finalize", "error"]:
    """검토 결과에 따라 다음 단계를 결정합니다."""
    result = state.get("review_result", "")
    if result == "pass":
        return "finalize"
    elif result == "max_attempts_reached":
        return "error"
    else:
        return "generate"  # 재시도


def finalize_output(state: ReviewState) -> dict:
    return {"final_output": f"완료: {state['content']}"}


def handle_error(state: ReviewState) -> dict:
    return {
        "final_output": (
            f"최대 시도 횟수({MAX_ATTEMPTS})에 도달했습니다. "
            f"마지막 콘텐츠: {state['content']}"
        )
    }


def build_review_graph():
    graph = StateGraph(ReviewState)

    graph.add_node("generate", generate_content)
    graph.add_node("review", review_content)
    graph.add_node("finalize", finalize_output)
    graph.add_node("error", handle_error)

    graph.add_edge(START, "generate")
    graph.add_edge("generate", "review")
    graph.add_conditional_edges(
        "review",
        decide_after_review,
        {
            "generate": "generate",   # 재시도 루프
            "finalize": "finalize",   # 성공 종료
            "error": "error",         # 실패 종료
        },
    )
    graph.add_edge("finalize", END)
    graph.add_edge("error", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_review_graph()
    result = app.invoke({
        "content": "",
        "review_result": "",
        "attempt": 0,
        "final_output": "",
    })
    print(f"최종 출력: {result['final_output']}")
    print(f"총 시도 횟수: {result['attempt']}")
```

**예상 출력:**

```text
최종 출력: 완료: [시도 3] 품질 기준을 통과한 콘텐츠
총 시도 횟수: 3
```

이 예제에서 루프 안전장치는 두 겹입니다. 첫째, `MAX_ATTEMPTS` 상수로 최대 재시도 횟수를 제한합니다. 둘째, `error` 경로가 있어서 최대 횟수 초과 시 반드시 종료합니다. 이 두 장치가 없으면 품질 기준을 절대 통과하지 못하는 콘텐츠가 무한 루프를 만들 수 있습니다.

---

## 분기 실패를 운영에서 어떻게 읽을까

조건부 엣지에서 장애가 생길 때, 실제 원인은 대개 모델 성능보다 계약 부재에서 나옵니다. 아래 세 가지는 특히 자주 보입니다.

**1. 분기 근거는 있는데 fallback이 없는 경우**

`route="other"` 같은 값이 한 번만 나와도 그래프가 갑자기 예외로 끝날 수 있습니다. 이 문제는 classifier 품질이 아니라 path map 완성도 문제입니다.

```python
# 문제 상황: fallback 없는 path map
graph.add_conditional_edges(
    "classify",
    route_question,
    {
        "code": "code",
        "concept": "concept",
        "debug": "debug",
        # fallback이 없음 -> "other" 라벨이 오면 KeyError
    },
)

# 해결: 항상 fallback 포함
graph.add_conditional_edges(
    "classify",
    route_question,
    {
        "code": "code",
        "concept": "concept",
        "debug": "debug",
        "fallback": "fallback",  # 반드시 포함
    },
)
```

**2. 라우터 함수가 부작용을 함께 떠안는 경우**

라우팅 함수 안에서 외부 API를 부르거나 상태를 추가로 갱신하면, 분기 판단과 실행 작업이 섞입니다. 그러면 "왜 이 route가 나왔는가"와 "라우팅 중 무슨 일이 있었는가"가 같은 디버깅 문제로 붙어 버립니다.

**3. 루프 종료와 branch 선택을 같은 문제로 다루는 경우**

route는 다음 단계를 정하는 문제이고, 종료 조건은 언제 멈출지를 정하는 문제입니다. 둘을 한 덩어리로 다루면 어떤 요청은 지나치게 빨리 끝나고, 어떤 요청은 이유 없이 반복되기 쉽습니다.

제가 실무에서 branch-heavy 그래프를 볼 때 먼저 확인하는 것도 비슷합니다. route 필드가 상태에 남는지, unknown route가 안전하게 수습되는지, 종료 규칙이 분기 규칙과 분리되어 있는지 봅니다. 이 세 가지가 선명하면 희귀한 라우팅 장애도 훨씬 빨리 설명됩니다.

---

## 코드에서 먼저 볼 세 가지 포인트

코드 전체를 한 번에 읽기보다, 아래 세 지점부터 보는 편이 이해가 빠릅니다.

![질문이 route 필드로 흐르는 구조](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/03/03-02-what-to-notice-in-this-code.ko.png)
*질문이 route 필드로 흐르는 구조*

- `classify_question()`은 라우팅 신호를 상태에 기록합니다.
- `route_question()`의 역할은 하나뿐입니다. 부작용 없이 다음 노드 이름을 반환합니다.
- path map 덕분에 분기 라벨과 실제 대상 노드가 코드에서 분명하게 대응됩니다.

첫 번째 포인트는 분기 근거를 상태에 남긴다는 사실입니다. 단순히 어떤 노드로 갔는지만 보는 것과, 왜 그 노드로 갔는지를 상태 필드로 함께 남기는 것은 운영에서 큰 차이를 만듭니다. 저는 현업에서 분기 결과만 있고 근거가 없어서, 재현이 어려운 라우팅 버그를 한참 뒤에야 설명하는 경우를 자주 봤습니다.

두 번째 포인트는 라우터 함수의 순수성입니다. `route_question()`은 다음 노드 이름만 돌려줍니다. 여기서 외부 API를 부르거나 상태를 추가로 바꾸기 시작하면, 분기 판단과 작업 수행이 섞여 버립니다.

세 번째 포인트는 path map입니다. 이 매핑은 사소해 보여도 중요합니다. route 문자열과 실제 대상 노드가 코드 구조 안에서 명시적으로 연결되기 때문입니다. 운영하면서 라우팅 계약을 바꿔야 할 때도 어디를 고쳐야 하는지 바로 보입니다.

---

## 자주 하는 실수

조건부 엣지 입문에서 가장 흔한 오해는 "route만 잘 나오면 됐다"는 생각입니다. 실제로는 route 값보다 **예상 밖 route를 어떻게 처리할지, 종료는 어디서 보장할지, fallback은 무엇인지**가 더 중요할 때가 많습니다.

![분기와 루프의 종료 설계](https://yeongseon-books.github.io/book-public-assets/assets/langgraph-101/03/03-03-where-engineers-get-confused.ko.png)
*분기와 루프의 종료 설계*

**실수 1: Conditional Edge Without Default 안티패턴**

분류기는 여러 값을 낼 수 있는데 path map은 행복 경로만 정의해 둔 상태입니다. 평소에는 잘 됩니다. 그런데 예상 밖 입력에서 빈 문자열이나 미정의 라벨이 나오면 그래프는 더 이상 갈 곳이 없어집니다. 어떤 시스템은 즉시 예외로 죽고, 어떤 시스템은 upstream retry와 만나면서 같은 요청을 반복 처리하기도 합니다.

이 안티패턴이 production에서 왜 위험할까요? 첫째, 분기 실패가 "가끔만 터지는 희귀 오류"처럼 보여서 원인 파악이 늦어집니다. 둘째, fallback이 없으면 사용자 경험이 갑자기 hard fail로 바뀝니다. 셋째, loop와 결합된 구조에서는 종료 대신 같은 분기 판단이 반복되면서 비용과 지연이 함께 커질 수 있습니다.

**실수 2: 라우터 함수에 너무 많은 의미를 넣기**

분류도 하고, 로그도 남기고, 외부 판정 API도 호출하고, 상태도 바꾸기 시작하면 결국 라우터가 또 하나의 거대한 작업 노드가 됩니다. 저는 팀들이 여기서 "분기 이유는 simple한데 왜 재현이 이렇게 어렵지?"라고 묻는 장면을 자주 봤습니다. 이유는 라우터가 이미 의사결정 계층이 아니라 부작용 계층이 돼 버렸기 때문입니다.

**실수 3: 루프 그래프에서 종료 조건을 빠뜨리기**

루프가 있는 그래프에서 종료 조건이 없으면 무한 루프가 됩니다. LangGraph는 기본적으로 `recursion_limit`(기본값: 25)으로 보호하지만, 이것은 마지막 안전망이지 설계 원칙이 아닙니다. 루프 그래프는 항상 명시적인 종료 조건과 최대 반복 횟수를 함께 설계해야 합니다.

```python
# recursion_limit 커스터마이즈 (필요한 경우)
result = app.invoke(
    {"content": "", "review_result": "", "attempt": 0, "final_output": ""},
    config={"recursion_limit": 10},  # 기본값 25에서 줄임
)
```

---

## 디버깅 전술: 분기 결정 추적

분기 그래프에서 "왜 이 route가 선택됐는가"를 추적하려면 `stream()`을 사용해 노드별 상태 변화를 확인하는 방법이 효과적입니다.

```python
app = build_graph()

question = "Python으로 퀵소트를 구현해 주세요."
print(f"질문: {question}\n")

for event in app.stream(
    {"question": question, "route": "", "answer": ""},
    stream_mode="updates",
):
    for node_name, state_update in event.items():
        print(f"[{node_name}] 업데이트:")
        for field, value in state_update.items():
            print(f"  {field}: {value}")
```

**예상 출력:**

```text
질문: Python으로 퀵소트를 구현해 주세요.

[classify] 업데이트:
  route: code

[code] 업데이트:
  answer: [code 경로] 코드 생성 또는 코드 리뷰 작업을 수행합니다.
```

이 로그에서 `classify` 노드가 `route: code`를 설정한 것을 바로 확인할 수 있습니다. 분기 결정이 상태 필드에 남아 있기 때문에 이런 추적이 가능합니다. 만약 `route` 필드가 없었다면 "왜 code 노드로 갔는가"를 추적하기 위해 `classify_question` 함수 내부를 직접 디버깅해야 했을 것입니다.

---

## 첫 번째 운영 체크리스트

조건부 엣지를 붙이는 순간부터 아래 항목은 단순한 코드 리뷰 항목이 아니라 라우팅 안정성 점검 항목이 됩니다.

- [ ] 분기 결정이 전용 상태 필드에 기록되는가
- [ ] 라우팅 함수가 순수 함수로 유지되는가 (부작용 없음)
- [ ] 정의되지 않은 route를 처리할 default 또는 fallback 전략이 있는가
- [ ] 모든 분기가 정상 종료되거나 안정적인 다음 단계로 이어지는가
- [ ] loop 구조라면 종료 조건과 최대 반복 횟수를 분리해서 설계했는가
- [ ] `stream()`으로 분기 결정 과정을 추적하는 디버깅 루틴을 갖추었는가
- [ ] `Literal[...]` 타입 힌트로 라우트 오타를 정적 검사로 잡을 수 있는가

이 체크리스트의 핵심은 "branch가 되느냐"가 아닙니다. "branch가 설명 가능하고 안전하냐"입니다. 분기는 기능이 아니라 운영 경계이기도 합니다.

---

## 실무에서는 이렇게 생각한다

조건부 엣지를 붙인 순간 그래프는 단순한 선형 워크플로를 벗어납니다. 그래서 운영 질문도 달라집니다. "답이 좋았나?"보다 먼저 "왜 이 route가 선택됐지?", "fallback은 언제 타지?", "이 분기는 종료 가능한 구조인가?" 같은 질문이 붙기 시작합니다.

현업에서 저는 분기 설계를 observability 설계와 함께 봅니다. route 필드가 저장되는지, path map이 코드 리뷰에서 읽히는지, unknown route가 따로 집계되는지 같은 질문이 중요합니다. 분기 시스템은 잘 돌 때보다 잘못 돌 때 더 많은 정보를 남겨야 합니다. 그래야 희귀 오류가 구조 오류로 승격되기 전에 잡을 수 있습니다.

또 하나 중요한 감각은 "분기"와 "loop"를 따로 보지 않는 것입니다. 실제 에이전트에서는 tool call 이후 다시 classify로 돌아오거나, review 결과에 따라 다른 경로로 빠지는 일이 흔합니다. 이때 conditional edge는 한 번의 분기 장치이면서 동시에 loop의 제어 장치가 됩니다. 그래서 default와 종료 조건이 더 중요해집니다.

제가 본 강한 팀들은 분류 정확도보다 라우팅 계약을 먼저 리뷰했습니다. 이유는 단순합니다. 모델 분류가 조금 흔들려도 fallback과 종료가 설계돼 있으면 시스템은 버팁니다. 반대로 라우팅 계약이 약하면, 좋은 모델도 불안정한 그래프 위에서는 금방 이상한 시스템이 됩니다.

---

## 정리: Conditional Edge는 분기 문법이 아니라, 그래프를 설명 가능하게 만드는 라우팅 계층이다

조건부 엣지를 처음 보면 "그래프에서 if/else를 쓰는 방법"처럼 보일 수 있습니다. 그 설명도 틀리진 않지만, 운영 관점에서는 너무 약합니다. 더 중요한 설명은 이렇습니다. conditional edge는 현재 상태를 읽어 다음 노드를 선택하고, 그 선택을 구조와 상태에 모두 드러내는 라우팅 계층입니다.

이 글에서 먼저 가져가야 할 핵심은 세 가지입니다. 첫째, 분기 근거는 상태에 남겨야 합니다. 둘째, 라우터 함수는 가능한 한 순수하고 결정적이어야 합니다. 셋째, default/fallback과 종료 조건은 optional 장식이 아니라 production 안전장치입니다.

이 관점이 중요한 이유는 다음 글의 도구 호출 에이전트와 바로 이어지기 때문입니다. tool routing은 결국 "지금 어떤 상태인가?"를 보고 다음 행동을 고르는 구조입니다. conditional edge를 의사결정 지점으로 이해하면, 도구 호출 루프도 같은 모델의 확장으로 읽힙니다.

저는 분기가 붙은 그래프를 볼 때 "경로가 많다"보다 "경로가 설명된다"를 먼저 봅니다. 어떤 상태가 route를 만들었는지, unknown route는 어디로 가는지, loop는 어디서 멈추는지 말할 수 있다면 출발은 제대로 잡힌 셈입니다.

다음 글에서는 이 분기 구조를 실제 도구 호출 에이전트와 결합해, 워크플로가 어떻게 에이전트 행동으로 확장되는지 보겠습니다. 그때 conditional edge가 왜 단순한 분기 문법이 아니라 에이전트 제어 계층인지 더 선명하게 드러날 것입니다.

---

## 운영 체크리스트

- [ ] route 필드와 라우터 함수의 책임 경계를 문서화했다
- [ ] unknown route에 대한 fallback 경로를 정했다
- [ ] loop가 생길 때 종료 조건과 recursion limit 기준을 함께 정의했다
- [ ] 분기 결과를 상태 또는 로그에서 복원할 수 있게 만들었다
- [ ] `Literal[...]` 타입으로 허용 route 집합을 정적으로 문서화했다
- [ ] 다음 단계 노드가 route 계약을 어겨도 빠르게 감지할 수 있는 검증 지점을 넣었다

## 처음 질문으로 돌아가기

- **조건부 엣지는 단순 if문과 무엇이 다르게 그래프 실행을 통제할까요?**
  - 일반 if문은 코드 흐름을 제어하지만 그 결정이 어디에도 남지 않습니다. 조건부 엣지는 분기 결정을 `route` 필드에 남기고, path map으로 라우팅 계약을 코드 구조에 고정합니다. 결과적으로 "왜 이 경로를 탔는가"를 상태와 구조 모두에서 설명할 수 있게 됩니다.

- **분기 함수가 예상하지 못한 값을 돌려주면 어떤 실패가 생길까요?**
  - path map에 없는 라벨이 나오면 LangGraph는 `KeyError`를 발생시킵니다. 이 실패는 "가끔만 터지는 희귀 오류"처럼 보이기 쉽습니다. fallback 경로를 항상 포함하고, 라우터 함수에서 알 수 없는 라벨을 fallback으로 변환하면 이 실패를 구조적으로 막을 수 있습니다.

- **default route를 코드로 고정해 두면 운영에서 어떤 디버깅이 쉬워질까요?**
  - fallback으로 넘어온 요청을 별도로 집계하면 분류기의 커버리지 갭을 발견할 수 있습니다. "이번 달 fallback 비율이 5%를 넘었다"는 지표는 분류기 개선의 구체적인 시그널이 됩니다. fallback이 없으면 이런 지표를 수집할 수 없습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LangGraph 101 (1/6): LangGraph 소개와 그래프 기초](./01-graph-basics.md)
- [LangGraph 101 (2/6): 상태 관리와 체크포인트](./02-state-and-checkpoints.md)
- **LangGraph 101 (3/6): 조건부 엣지와 분기 흐름 (현재 글)**
- [LangGraph 101 (4/6): 도구 호출 에이전트](./04-tool-calling-agent.md)
- [LangGraph 101 (5/6): 멀티 에이전트 시스템](./05-multi-agent.md)
- [LangGraph 101 (6/6): LangGraph 완성](./06-langgraph-complete.md)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [LangGraph branching guide](https://langchain-ai.github.io/langgraph/how-tos/branching/)
- [LangGraph low-level concepts: edges](https://langchain-ai.github.io/langgraph/concepts/low_level/)
- [LangGraph recursion limit guide](https://langchain-ai.github.io/langgraph/how-tos/recursion-limit/)

### 소스 코드와 예제
- [langchain-ai/langgraph GitHub repository](https://github.com/langchain-ai/langgraph)
- [LangGraph quickstart with routing](https://langchain-ai.github.io/langgraph/tutorials/get-started/4-add-tools/)

### 관련 시리즈
- [상태 관리와 체크포인트](./02-state-and-checkpoints.md)
- [LangGraph 소개와 그래프 기초](./01-graph-basics.md)

---

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/langgraph-101/ko/03-conditional-edges)

Tags: LangGraph, Agent, Python, LLM
