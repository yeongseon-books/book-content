---
title: LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기
series: llm-app-foundations-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- OpenAI
- Prompt Engineering
- Python
last_reviewed: '2026-05-01'
---

# LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기

> LLM 앱 기초 시리즈 (1/6)

예제 코드: [github.com/yeongseon-books/llm-app-foundations-101](https://github.com/yeongseon-books/llm-app-foundations-101/tree/main/ko/01-llm-api-first-call)

아래 다이어그램은 첫 호출에서 애플리케이션과 모델 API가 어떻게 왕복하는지 한눈에 보여 줍니다.

![LLM API 첫걸음: 모델에게 첫 번째 요청 보내기](../../../assets/llm-app-foundations-101/01/01-01-llm-api-first-call-sending-your-first-re.ko.png)
처음 LLM 앱을 붙일 때 가장 낯선 지점은 모델이 아니라 경계입니다. 브라우저에서 대화창을 열면 마치 똑똑한 프로그램 하나와 바로 연결된 듯 보이지만, 실제로 애플리케이션이 하는 일은 훨씬 단순합니다. HTTP 요청 하나를 보내고 JSON 응답 하나를 받습니다. 그 왕복이 전부입니다. 채팅 UI, 프롬프트 템플릿, 스트리밍, 메모리, RAG는 모두 그 위에 올라가는 두 번째 문제입니다.

입문 단계에서는 이 단순함을 먼저 몸에 익히는 편이 좋습니다. 요청 본문에 무엇을 넣는지, 응답에서 무엇을 꺼내는지, 비용과 지연 시간을 어디서 읽는지 모르면 이후 단계가 계속 흐립니다. 반대로 첫 호출을 확실히 이해하면 나머지는 점진적으로 쌓을 수 있습니다. Python 코드 한 파일만으로도 “모델에게 문장을 보내고 답을 받는다”는 핵심 루프를 바로 확인할 수 있습니다.

이번 글에서는 Groq 무료 API를 기준으로 첫 호출을 끝까지 만들어 봅니다. 독자는 `GROQ_API_KEY` 하나만 준비하면 됩니다. 모델은 `llama-3.1-8b-instant`, 패키지는 공식 Python SDK인 `groq`를 사용합니다. 범위는 다음 일곱 가지입니다.

- LLM API가 무엇인지
- Groq 계정과 API 키를 어떻게 준비하는지
- `pip install groq` 설치
- `client.chat.completions.create()` 첫 호출
- 응답 구조에서 본문, 사용량, 모델명을 읽는 법
- 동기와 비동기 패턴 차이
- 실제 실행 가능한 완성 예제

포인트는 하나입니다. **LLM 앱의 시작점은 프롬프트 감각이 아니라 요청과 응답의 구조를 읽는 능력**입니다.

---

## LLM API는 무엇인가

LLM API는 이름만 거창할 뿐, 구조는 익숙한 웹 API와 다르지 않습니다. 클라이언트가 HTTP로 요청을 보내고 서버가 JSON으로 응답합니다. 차이가 있다면 엔드포인트의 목적이 데이터 조회가 아니라 텍스트 생성이라는 점뿐입니다.

REST 관점에서 보면 애플리케이션은 다음 정보를 서버에 보냅니다.

- 어떤 모델을 쓸지
- 어떤 메시지를 입력으로 줄지
- 생성 길이, temperature 같은 옵션을 어떻게 줄지

서버는 대개 다음 정보를 되돌려줍니다.

- 생성된 답변 텍스트
- 어떤 모델이 실제로 사용되었는지
- 토큰 사용량이 얼마였는지
- 요청 ID, 종료 이유 같은 메타데이터

SDK를 쓰면 이 HTTP/JSON 왕복이 감춰져서 메서드 호출처럼 보입니다. 그렇다고 구조가 사라지는 것은 아닙니다. `client.chat.completions.create()`는 내부적으로 JSON 요청을 만들고, Groq 서버가 돌려준 JSON 응답을 Python 객체로 감싼 결과를 반환합니다. 입문자에게 중요한 이유가 여기 있습니다. SDK 문법은 라이브러리마다 조금씩 바뀌지만, **JSON in / JSON out**이라는 기본 모델은 거의 바뀌지 않습니다.

예를 들어 채팅 완료 요청은 개념적으로 아래와 비슷합니다.

```json
{
  "model": "llama-3.1-8b-instant",
  "messages": [
    {
      "role": "user",
      "content": "Python에서 환경변수를 읽는 예제를 보여줘."
    }
  ]
}
```

응답도 같은 식입니다. 실제 필드는 더 많지만, 처음엔 아래 세 덩어리만 보면 충분합니다.

```json
{
  "model": "llama-3.1-8b-instant",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "import os\nprint(os.environ['HOME'])"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 24,
    "completion_tokens": 31,
    "total_tokens": 55
  }
}
```

이 글에서는 SDK를 사용하더라도 계속 이 그림을 함께 떠올릴 것입니다. 그래야 나중에 스트리밍, 툴 호출, 구조화 출력으로 넘어갈 때도 길을 잃지 않습니다.

---

## Groq 계정과 API 키 준비

준비 과정은 길지 않습니다.

1. 브라우저에서 <https://console.groq.com> 에 접속합니다.
2. GitHub 계정이나 이메일로 가입합니다.
3. 로그인 뒤 API Keys 메뉴로 이동합니다.
4. 새 키를 생성하고 값을 복사합니다.
5. 로컬 셸에 `GROQ_API_KEY` 환경변수로 넣습니다.

macOS나 Linux 셸이라면 일단 아래처럼 넣고 시작하면 됩니다.

```bash
export GROQ_API_KEY="여기에-발급받은-키"
```

Windows PowerShell이라면 다음 형식입니다.

```powershell
$env:GROQ_API_KEY="여기에-발급받은-키"
```

영구 설정은 각자 쓰는 셸 프로필에 추가하면 됩니다. 다만 입문 단계에서 더 중요한 것은 보안 습관입니다. API 키를 코드에 직접 적지 마십시오. Git에 한 번 올라간 키는 곧바로 폐기 대상입니다. 예제 코드에서는 모두 `os.environ["GROQ_API_KEY"]`로 읽겠습니다. 키가 없으면 `KeyError`가 나므로, 환경 설정이 빠졌다는 사실도 즉시 드러납니다.

간단한 확인 코드는 아래 정도면 충분합니다.

```python
import os

api_key = os.environ["GROQ_API_KEY"]
print(f"API key loaded: {api_key[:6]}...")
```

~~~
출력 결과
API key loaded: gsk_Z2...
~~~
이 코드는 환경변수 연결만 확인하는 최소 예제입니다. 실제 앱에서는 키 전체를 출력하지 않는 편이 안전합니다. 개발 초반에는 앞 몇 글자만 확인해도 충분합니다.

---

## SDK 설치와 실행 환경

이 글의 예제는 Python 3.10 이상을 가정합니다. Groq 공식 SDK는 `groq` 패키지 하나면 시작할 수 있습니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install groq
```

이미 가상환경을 쓰고 있다면 `pip install groq`만 실행하면 됩니다. SDK는 내부적으로 HTTP 클라이언트를 사용해 Groq REST API와 통신합니다. 개발자가 직접 `requests.post()`를 쓰지 않아도 되는 이유가 여기 있습니다.

설치 뒤에는 버전이 잘 잡혔는지 확인해 두면 좋습니다.

```bash
python -c "import groq; print(groq.__version__)"
```

이제 준비물은 끝났습니다. 다음 단계부터 진짜 호출을 보겠습니다.

---

## 첫 번째 호출 만들기

가장 작은 성공 경로부터 보겠습니다. 아래 코드는 동기 방식으로 한 번 요청을 보내고, 첫 번째 응답 텍스트만 출력합니다. 이 코드 블록은 독립 실행 가능합니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Python에서 리스트 컴프리헨션을 한 문단으로 설명해 주세요.",
        }
    ],
)

print(completion.choices[0].message.content)
```

~~~
출력 결과
**리스트 컴프리헨션**

리스트 컴프리헨션은 리스트를 생성하는 데 사용되는 고급 리스트 기능입니다. 기본적으로, 컴프리헨션은 반복을 수행하는 데 사용되는 하나의 표현식입니다. 이 표현식은 원하는 요소를 생성하기 위해 사용됩니다.

**기본 문법**

리스트 컴프리헨션의 기본 문법은 다음과 같습니다.
    ```python
    new_list = [expression for variable in iterable if condition]
    ```
여기서:

- `new_list`: 새로운 리스트
- `expression`: 각 요소를 만들기 위한 표현식
- `variable`: 반복 가능한 객체에서 추출한 요소
- `iterable`: 반복할 수 있는 객체(리스트, 튜플, 집합 등)
- `condition`: 필터 조건 (선택 사항)

**예제**

다음 예제는 다음과 같은 문장을 표현합니다.

"숫자 1에서 10까지 2씩 증가하는 모든 요소를 리스트로 만들라."

    ```python
    numbers = [i for i in range(1, 11) if i % 2 == 0]
    print(numbers)  # [2, 4, 6, 8, 10]
    ```
이 예제에서 `i`는 `range(1, 11)`의 요소를 나타내고, `i % 2 == 0`가 필터 조건입니다. 조건을 만족하는 모든 요소가 `numbers` 리스트에 추가됩니다.

**리스트 컴프리헨션의 장점**

리스트 컴프리헨션은 코드의 brevity와 readability를提高하는 데 도움이 됩니다.

*   **코드 길이가 짧아집니다**: 컴프리헨션은 반복을 수행하는 코드를 대신할 수 있으므로, 코드의 길이를 줄일 수 있습니다.
*   **읽기쉽게됩니다**: 코드가 더 간단해지고, 반복문과 조건문이 숨겨져 있으므로, 코드의 내용을 더 쉽게 이해할 수 있습니다.

**리스트 컴프리헨션의 사용 예**

1.  **조건에 따라 요소 필터링**: `numbers = [i for i in range(1, 11) if i % 2 == 0]`를 사용하여 짝수만 있는 리스트를 만들 수 있습니다.
2.  **리스트 내에 요소 변환**: `scores = [name + " - " + str(score) for name, score in scores.items()]`를 사용하여 리스트의 요소를 변환할 수 있습니다.
3.  **네비게이션과 함께 필터링**: `prices = [(index, price) for index, price in enumerate(prices) if price > 10]`를 사용하여 리스트 내에 요소가 특정 값 이상인 것을 필터링할 수 있습니다.

리스트 컴프리헨션은 데이터를 처리할 때 유용한 도구라고 할 수 있습니다. 그러나 반복을 수행하는 코드는 명시적으로 작성하는 것이 좋습니다. 그 이유는 다음과 같습니다.

*   **읽기성 향상**: 명시적으로 반복문과 조건문을 사용하면, 코드의 의미를 더 명확히 알 수 있습니다.
*   **유지보수성 향상**: 반복문을 명시적으로 작성하면, 코드를 이해하고維護하기가 더容易합니다.

따라서 상황에 따라 적절히 사용한다면, 리스트 컴프리헨션은 코드 작성의 시간과 노력을 줄여 줄 수 있지만, 명시적인 코드를 작성하는 것이 보다 좋습니다.
~~~[식 for 변수 in 열거 가능한 객체]
```

이 식은 다음과 같이 작동합니다:

1. `열거 가능한 객체` 내의 각 요소를 하나씩 꺼내어 반복합니다.
2. 해당 요소를 `변수`에 할당하고 `식`을 평가합니다.
3. 새로운 요소를 생성하고 결과 값을 `리스트`에 추가합니다.

**예시**

```python
# 기본적인 리스트 컴프리헨션 예시
num_list = [1, 2, 3, 4, 5]
even_nums = [x for x in num_list if x % 2 == 0]
print(even_nums)  # [2, 4]
```

~~~
출력 결과
[2, 4]
~~~
이 예시에서, 리스트 `num_list`의 각 요소를 `x`에 할당하여 `x % 2 == 0` 인지 확인합니다. 만약 `x`가 짝수이면, 그 요소를 `even_nums` 리스트에 추가합니다.

**다중 반복**

리스트 컴프리헨션은 다중 반복도 지원합니다. 이러한 경우, 반복과 동시에 할당할 수 있습니다.

```python
# 두 항목 리스트의 교집합 찾기
list1 = [1, 2, 3, 4]
list2 = [2, 3, 4, 5]
intersection = [(value1, value2) for value1 in list1 for value2 in list2 if value1 == value2]
print(intersection)  # [(2, 2), (3, 3), (4, 4)]
```

~~~
출력 결과
[(2, 2), (3, 3), (4, 4)]
~~~
이 예시에서, 두 항목 리스트 `list1`과 `list2`를 각각 반복하여 두 항목이 동일하면, 그 항목을 교집합 리스트에 추가합니다.

**리스트 컴프리헨션의 장점**

리스트 컴프리헨션을 사용하면, 코드의 길이를 줄일 수 있으며, 더 이해하기 쉬운 코드를 작성할 수 있습니다. 또한, 컴퓨팅 파워의 낭비를 줄일 수 있습니다.

**참조**

* [Python.org - List Comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
```

여기서 눈여겨볼 줄은 세 군데입니다.

첫째, `Groq(...)`는 API 서버와 통신할 클라이언트 객체를 만듭니다. 보통 애플리케이션 시작 시 한 번 만들고 재사용합니다.

둘째, `model="llama-3.1-8b-instant"`는 어떤 모델에 보낼지 지정합니다. 모델명은 문자열일 뿐이지만, 이 값이 성능과 비용, 지연 시간의 성격을 결정합니다.

셋째, `messages=[...]`는 채팅 입력입니다. 지금은 `user` 메시지 하나만 넣었지만, 실제로는 여러 턴의 대화 이력을 같은 배열에 담을 수 있습니다. 다음 글들에서 역할 분리와 멀티턴 상태 관리를 자세히 다룰 예정이니, 오늘은 “메시지 목록을 보낸다” 정도만 기억하면 충분합니다.

실행 결과는 매번 조금씩 달라질 수 있습니다. 생성 모델이기 때문입니다. 중요한 것은 출력 내용의 정확한 문구가 아니라, 요청이 성공했고 `choices[0].message.content`에서 텍스트를 읽을 수 있다는 사실입니다.

---

## 응답 구조를 해부해 보기

첫 호출이 성공하면 많은 입문자가 곧바로 본문 텍스트만 꺼내 쓰고 넘어갑니다. 하지만 실전에서는 응답 전체를 한 번은 눈으로 확인해 봐야 합니다. 모델명, 사용량, 종료 이유를 모르고 운영에 들어가면 나중에 비용과 지연 시간을 설명하기 어렵습니다.

Groq Python SDK의 응답은 Pydantic 모델입니다. 따라서 `to_dict()`로 사전 형태를 볼 수 있습니다. 아래 코드는 응답 일부를 구조적으로 확인하는 예제입니다. 역시 독립 실행 가능합니다.

```python
import json
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "HTTP API와 SDK의 차이를 세 문장으로 설명해 주세요.",
        }
    ],
)

print(json.dumps(completion.to_dict(), indent=2, ensure_ascii=False))
```

~~~
출력 결과
{
  "id": "chatcmpl-84280051-e5f0-4a2f-91d6-514a52f447e5",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "content": "HTTP API와 SDK의 차이는 다음과 같습니다.\n\nHTTP API는 API(Application Programming Interface)를 통해 클라이언트가 서버에 요청을 보내고 서버가 응답하는 방식입니다. 클라이언트는 일반적으로 브라우저나 모바일 앱으로 구성되며 HTTP 요청을 보낼 수 있습니다. HTTP API는 클라이언트가 직접 HTTP를 통해 API를 호출할 수 있기 때문에 서버 간의 통신과 데이터 교환을 위한 표준적인 방법입니다.\n\nSDK는 Software Development Kit의 줄임말로, 프로그래밍 언어를 통해 프로그램을 개발할 때 사용되는 도구 및 도움이 모인 도구 세트입니다. SDK는 특정 라이브러리를 포함하여 프로그래머가 쉽게 프로그램을 개발할 수 있도록 도와주는 역할을 하는데, 이는 보통 특정 프로그래밍 언어로 API를 호출하는 표준된 방법에 의해 정의됩니다. SDK는 프로그래머가 라이브러리를 사용하고 API를 호출할 수 있도록 지원하기 때문에 API의 복잡한 세부 정보를 숨길 수 있습니다.",
        "role": "assistant"
      }
    }
  ],
  "created": 1777646263,
  "model": "llama-3.1-8b-instant",
  "object": "chat.completion",
  "service_tier": "on_demand",
  "system_fingerprint": "fp_7ccc667439",
  "usage": {
    "completion_tokens": 238,
    "prompt_tokens": 51,
    "total_tokens": 289,
    "completion_time": 0.492699382,
    "prompt_time": 0.00249493,
    "queue_time": 0.007412127,
    "total_time": 0.495194312
  },
  "usage_breakdown": null,
  "x_groq": {
    "id": "req_01kqhzjpf1ey4syzd2s5n8dtzr",
    "seed": 1007482985
  }
}
~~~
출력을 보면 필드가 여럿 보이겠지만, 처음에는 세 가지를 우선 읽으면 됩니다.

### `choices[0].message.content`

가장 자주 쓰는 필드입니다. 모델이 생성한 실제 답변 본문이 들어 있습니다.

```python
text = completion.choices[0].message.content
print(text)
```

왜 `choices[0]`일까요. API 설계가 “후보 응답 목록”을 기본 구조로 두기 때문입니다. 지금은 첫 번째 후보 하나만 읽으면 충분합니다.

### `usage`

사용량 정보입니다. 보통 아래 세 값을 가장 먼저 봅니다.

```python
usage = completion.usage
print(f"prompt_tokens={usage.prompt_tokens}")
print(f"completion_tokens={usage.completion_tokens}")
print(f"total_tokens={usage.total_tokens}")
```

이 숫자는 단순 통계가 아닙니다. 비용 추적, 길이 제한, 캐시 전략, 속도 분석의 시작점입니다. 다음 글에서 토큰을 별도로 다루는 이유도 여기에 있습니다. LLM 앱은 결국 토큰 예산 위에서 동작합니다.

### `model`

응답에 기록된 모델명입니다.

```python
print(completion.model)
```

요청에서 보낸 모델명과 같아 보일 수 있지만, 운영 환경에서는 로그에 이 값을 남기는 습관이 유용합니다. 어떤 모델이 실제 응답을 만들었는지 추적하기 쉬워지기 때문입니다.

실제로는 두 가지 필드를 처음부터 로그에 남겨두면 나중에 디버깅이 편해집니다.

```python
print(completion.id)                              # 요청 고유 ID, 공급자 문의 시 필요
print(completion.choices[0].finish_reason)        # "stop", "length", "tool_calls" 중 하나
```

`finish_reason`은 모델이 생성을 멈춘 이유를 알려줍니다. `"stop"`은 자연스러운 종료이고, `"length"`는 허용 토큰이 소진되어 잘린 것입니다. 이 두 값을 운영 로그에 남겨두면 응답 품질 이슈를 추적하기가 훨씬 쉬워집니다.

---

## SDK 호출도 결국 HTTP 요청이라는 감각

SDK가 편한 이유는 분명합니다. 인증 헤더, JSON 직렬화, 응답 파싱, 오류 객체를 라이브러리가 대신 처리해 줍니다. 그렇다고 네트워크 비용이 사라지는 것은 아닙니다. 요청은 여전히 원격 서버로 가고, 실패 가능성도 그대로 존재합니다.

이 감각을 초반에 잡아 두면 실수가 줄어듭니다.

- 응답이 느리면 Python 문법보다 네트워크 왕복 시간을 먼저 의심합니다.
- `401`이 나면 프롬프트보다 API 키 설정부터 확인합니다.
- `429`가 나면 모델 지능보다 호출 빈도를 먼저 봅니다.
- 빈 문자열이나 예외가 나면 응답 객체 전체를 로그로 남깁니다.

초급 예제에서는 한 줄 출력으로 끝나도 되지만, 실제 앱에서는 요청과 응답을 관찰 가능한 형태로 남겨야 합니다. 최소한 모델명, 토큰 수, 응답 길이 정도는 로그에 포함하는 편이 좋습니다.

---

## 동기와 비동기 패턴은 무엇이 다른가

Python에서 LLM 호출은 동기와 비동기 두 방식으로 작성할 수 있습니다. 어느 쪽이 더 “좋다”기보다, 애플리케이션 구조에 맞는 방식을 고르면 됩니다.

동기 코드는 읽기 쉽습니다. 스크립트, 배치, 실험용 노트북, 단일 요청 CLI 도구에서는 대개 이쪽이 더 단순합니다.

비동기 코드는 다른 I/O 작업과 함께 돌릴 때 빛납니다. FastAPI 같은 비동기 웹 서버, 여러 LLM 요청을 동시에 날리는 작업, 외부 API 여러 개를 함께 기다리는 서비스라면 `asyncio` 패턴이 자연스럽습니다.

먼저 동기 버전입니다. 이 코드는 앞에서 본 형태와 거의 같습니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "비동기 프로그래밍을 한 문단으로 설명해 주세요.",
        }
    ],
)

print(completion.choices[0].message.content)
```

~~~
출력 결과
비동기 프로그래밍은 컴퓨터 프로그램이 어떤 작업을 처리하는 도중도 다른 작업을 수행할 수 있도록 하게 하는 프로그래밍 기법입니다. 이전의 동의어로 프로그램이 한 가지 일을 끝마치기 전까지는 다음 일들을 진행할 수 없던 것과는 대조된다. 비동기 프로그래밍은 동시성을 제공하여 프로그램이 한 가지 일과 다른 일들을 모두 동시에 처리할 수 있기 때문에, 작업을 처리할 수 있는 성능을 향상시킬 수 있습니다. 예를 들어, 웹 브라우저에서 다음 URL로 이동할 때도 웹 브라우저는 현재 페이지를 로딩하는 동시에 그 다음 페이지를 로딩할 수 있습니다.
~~~
다음은 비동기 버전입니다. 이 코드 블록도 독립 실행 가능합니다.

```python
import asyncio
import os

from groq import AsyncGroq

client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

async def main() -> None:
    completion = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": "asyncio가 필요한 상황을 두 가지로 설명해 주세요.",
            }
        ],
    )

    print(completion.choices[0].message.content)

asyncio.run(main())
```

~~~
출력 결과
아Syncio는 동시성 프로그래밍을 위해 도입된 Python 모듈입니다. 다음과 같은 두 가지 상황에서 asyncio를 사용하는 것이 유용합니다.

### 1. 네트워크 작업(Non-blocking I/O)

아Syncio는 네트워크 연결이나 파일 읽기와 같은 비 블록킹 입/출력을 가능하게 해줍니다. 이런 작업은 자바스크립트나 PHP와 같이 싱글 쓰레드 환경에서 작업하는 언어에서 자주 필요합니다.

만약 사용하는 언어가 싱글 쓰레드이며, 사용자가 여러 요청을 넣어주었다고 가정합시다. 이 경우, 이전 요청이 처리가 끝나지 않은 상태에서 새로운 요청을 처리하게 되면 이전 요청에대한 리소스가 새로오는 요청으로 넘어가게되는데 이는 결과적으로 이전 요청이 처리가 늦어지며 요청이 쌓이게 될 것입니다.

    ```python
    import asyncio
    import time
    
    async def my_coroutine(task_id):
        print(f"Coroutine {task_id} has started.")
        await asyncio.sleep(1)
        print(f"Coroutine {task_id} has finished.")
        return task_id
    
    async def main():
        await asyncio.gather(
            my_coroutine(1),
            my_coroutine(2),
            my_coroutine(3),
        )
    
    start_time = time.time()
    
    asyncio.run(main())
    
    print(f"Time taken to complete all coroutines: {time.time() - start_time} seconds")
    ```

### 2. 입출력 작업(I/O Bound)

아Syncio는 여러 입/출력(I/O) 작업이 있을 때 각 작업을 동시에 수행할 수 있습니다. 예를 들어, 사용자가 여러 데이터를 읽어오게 되면 데이터가 읽어온 속도가 느려지는 결과를 방지할 수 있습니다.

    ```python
    import asyncio
    
    async def read_data(task_id, sleep_time):
        print(f"Reading data for task {task_id}")
        await asyncio.sleep(sleep_time)
        print(f"Finished reading data for task {task_id}")
        return f"Data for task {task_id}"
    
    async def main():
        tasks = []
        for i in range(1, 10):
            tasks.append(read_data(i, 1))
        result = await asyncio.gather(*tasks)
        print(result)
    
    asyncio.run(main())
    ```

### 예시

위 두 예시에 대해서는 다음과 같이 해석이 가능합니다. 예시 1번에서 async로 처리된 작업은 블록킹 처리가 안된다는 의미입니다. 예시2번에서는 I/O 작업을 처리할때 여러개의 task를 동시에 처리합니다.

1. 사용하기
... (truncated)
~~~
차이는 두 가지뿐입니다. `Groq` 대신 `AsyncGroq`를 쓰고, API 호출 앞에 `await`를 붙입니다. 구조는 거의 같습니다. 그래서 입문 시점에는 “동기 코드로 개념을 익히고, 웹 앱으로 가져갈 때 비동기로 옮긴다”는 순서가 무난합니다.

여러 요청을 동시에 보내는 장점도 비동기에서 분명해집니다. 아래 예시는 세 질문을 병렬로 호출합니다. 이 코드는 바로 실행할 수 있는 완전한 예제입니다.

```python
import asyncio
import os

from groq import AsyncGroq

client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

async def ask(question: str) -> str:
    completion = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": question}],
    )
    return completion.choices[0].message.content or ""

async def main() -> None:
    questions = [
        "리스트와 튜플의 차이를 설명해 주세요.",
        "파이썬 딕셔너리의 핵심 특징을 설명해 주세요.",
        "예외 처리가 필요한 이유를 설명해 주세요.",
    ]
    answers = await asyncio.gather(*(ask(question) for question in questions))

    for index, answer in enumerate(answers, start=1):
        print(f"[{index}] {answer}\n")

asyncio.run(main())
```

~~~
출력 결과
[1] 리스트와 튜플은 모두 데이터를 여러 개의 원소(요소)로 저장하기 위한 자료 구조입니다. 하지만 두 자료 구조는 생성과 편집 방식에 차이가 있습니다.

### 리스트(List)

리스트는 여러 원소를 포함하는 자료 구조로, 생성한 리스트는 언제든지 새로운 원소가 추가되거나 기존 원소가 삭제되거나 수정될 수 있습니다. 리스트는 인덱스 순서에 따라 원소에 접근할 수 있습니다.

**예시:**

    ```python
    # 리스트 생성
    numbers = [1, 2, 3, 4, 5]
    
    # 새로운 원소 추가
    numbers.append(6)
    print(numbers)  # [1, 2, 3, 4, 5, 6]
    
    # 인덱스 순서에 따라 원소접근
    print(numbers[0])  # 1
    
    # 원소 수정
    numbers[0] = 10
    print(numbers)  # [10, 2, 3, 4, 5, 6]
    ```

### 튜플(Tuple)

튜플은 생성된 후에 어떤 변화도 할 수 없습니다. 원래의 튜플에는 수정, 삽입, 삭제가 가능하지 않으며, 새로운 튜플을 만들고 이전 정보만 그대로 유지하는 방법 밖에는 없습니다.

**예시:**

    ```python
    # 튜플 생성
    colors = ('red', 'green', 'blue')
    
    # 새로운 원소 추가는 불가
    # colors.append('yellow')  # TypeError: 'tuple' object does not support item assignment
    
    # 튜플에 접근
    print(colors[0])  # 'red'
    ```

### 차이점

| 특성 | 리스트 | 튜플 |
| --- | --- | --- |
| 생성 전후 | 언제든지 | 한번만 |
| 수정 | 허용 | 허용하지 않음 |
| 삽입/삭제 | 허용 | 허용하지 않음 |
| 인덱스 순서 | 허용 | 허용 |
| 접근 | 허용 | 허용 |

리스트는 다양한 데이터를 편리하게 관리하고 조작할 수 있지만, 튜플은 불변성 때문에 데이터의 일관성을 유지할 수 있습니다. 데이터의 불변성에 중점을 둔다면 튜플을 선택하는 것이 좋고, 데이터의 관리와 편집 여지가 필요하다면 리스트를 선택하는 것이 좋습니다.

[2] 파이썬 딕셔너리의 핵심 특징을 설명하겠습니다.

### 1. 키-값 쌍(key-value pair)입니다.

파이썬의 딕셔너리는 키-값 쌍으로 구성되어 있습니다. 각 키에는 해당하는 값이 할당됩니다. 예를 들어, `{ 'name': 'John', 'age': 30 }`은 'name' 키에 'John', 'age' 키에 30이 할당된 딕셔너리를示しています.

### 2. 키는 유일해야합니다.
... (truncated)
~~~my_list = [1, 2, 3, "hello"]
print(my_list[0])  # 출력: 1
my_list[0] = 10
print(my_list)     # 출력: [10, 2, 3, "hello"]
```

리스트의 요소를 추가하거나 제거하는 방법은 다음과 같습니다.

```python
my_list.append("world")   # 리스트의 끝에 추가
my_list.insert(0, 5)      # 특정 인덱스에 추가
del my_list[0]            # 인덱스 0의 요소 삭제
my_list.pop(0)            # 인덱스 0의 요소 삭제
```

### 2. 튜플 (TUPLE)

튜플은 순서가 유지되며, 요소의 중복을 허용하는 자료형입니다. 튜플은 괄호를 사용하여 표기를하고, 요소 사이에 쉼표를 사용하여 구분합니다. 튜플의 요소는 변경이 불가능합니다. 예를 들어,

```python
my_tuple = (1, 2, 3, "hello")
print(my_tuple[0])  # 출력: 1
# my_tuple[0] = 10  # 에러: 튜플의 요소를 변경할 수 없음
```

~~~
출력 결과
1
~~~
튜플의 요소를 추가하거나 제거할 수는 없습니다. 즉, 다음과 같은 방법으로 요소를 추가하거나 제거할 수 없습니다.

```python
# my_tuple.append("world")   # 에러: 튜플의 요소를 추가할 수 없음
# my_tuple.insert(0, 5)      # 에러: 튜플의 요소를 추가할 수 없음
# del my_tuple[0]            # 에러: 튜플의 요소를 삭제할 수 없음
# my_tuple.pop(0)            # 에러: 튜플의 요소를 삭제할 수 없음
```

### 결论

리스트와 튜플의 차이점은 다음과 같습니다.

*   리스트는 요소의 중복을 허용하며, 요소를 변경할 수 있습니다. 튜플은 요소의 중복을 허용하며, 요소를 변경할 수 없습니다.
*   리스트는 괄호를 사용하여 표기를하고, 요소 사이에 쉼표를 사용하여 구분합니다. 튜플도 괄호를 사용하여 표기를하고, 요소 사이에 쉼표를 사용하여 구분합니다.

요약하여, 리스트는 변경이 가능한 자료형이고, 튜플은 변경이 불가능한 자료형입니다.

[2] **파이썬 딕셔너리의 핵심 특징**

파이썬 딕셔너리는 키-값 쌍의 컬렉션으로, 데이터의 빠른 접근 및 관리를 위해 사용됩니다. 다음은 파이썬 딕셔너리의 핵심 특징입니다.

### 1. 키-값 쌍

딕셔너리는 키(key)와 값(value)의 쌍으로 구성됩니다. 키는 고유해야 하며, 값은 키에 대응할 수 있는 어떠한 자료형도 사용할 수 있습니다.

### 2. 키별 접근

... (truncated)
```

물론 동시에 많이 보낸다고 해서 항상 더 좋은 것은 아닙니다. API 제한, 재시도, 백오프, 타임아웃 같은 운영 문제는 곧바로 따라옵니다. 그 주제는 후속 시리즈에서 다루겠습니다. 지금은 비동기 패턴이 “문법 장난”이 아니라 동시성 제어 수단이라는 점만 잡고 가면 됩니다.

---

## 실제 실행 가능한 완성 예제

마지막으로, 오늘 내용을 한 파일에 모은 실행 예제를 보겠습니다. 이 코드는 환경변수를 읽고, 요청을 보내고, 응답 본문과 메타데이터를 함께 출력합니다. Post 01의 최소 완성본이라고 생각하면 됩니다.

```python
import os

from groq import Groq

def main() -> None:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a concise Python tutor.",
            },
            {
                "role": "user",
                "content": (
                    "Python 초급자에게 함수와 메서드의 차이를 5문장 이내로 설명하고, "
                    "짧은 예시 한 줄을 덧붙여 주세요."
                ),
            },
        ],
    )

    content = completion.choices[0].message.content or ""
    usage = completion.usage

    print("=== answer ===")
    print(content)
    print()
    print("=== metadata ===")
    print(f"model: {completion.model}")
    print(f"prompt_tokens: {usage.prompt_tokens}")
    print(f"completion_tokens: {usage.completion_tokens}")
    print(f"total_tokens: {usage.total_tokens}")

if __name__ == "__main__":
    main()
```

~~~
출력 결과
=== answer ===
Python에서 함수(funciton)와 메서드(method)는 둘 다 기능을 하는 코드 블록입니다. 

다만, 메서드는 클래스 안에 작성 된 함수가며, 메서드 이름은 인스턴스의 이름 + 메서드 이름으로 호출합니다. 

함수는 클래스 밖에서 호출하며, 인스턴스의 상태를 변경하지 않습니다. 

함수는 재사용성이 높으며, 여러 종류를 만들 수 있습니다. 

만약 클래스와 관련된 동작이라면 메서드를, 클래스와 독립된 동작이라면 함수를 사용하는 것이 좋습니다.

    ```python
    class Person:
        def __init__(self, name):
            self.name = name
        
        def say_hello(self):
            return f"안녕하세요, 저는 {self.name}입니다."
    
    def say_goodbye():
        return "잘 가세요."
    
    print(Person("김철수").say_hello())  # 메서드
    print(say_goodbye())  # 함수调用
    ```

=== metadata ===
model: llama-3.1-8b-instant
prompt_tokens: 81
completion_tokens: 214
total_tokens: 295
~~~# 함수 예시
def say_hello(name):
    return f"Hello, {name}!"

# 메서드 예시
class Person:
    def __init__(self, name):
        self.name = name

    def say_hello(self):
        return f"Hello, {self.name}!"
```

=== metadata ===
model: llama-3.1-8b-instant
prompt_tokens: 81
completion_tokens: 229
total_tokens: 310
```

저장 파일명을 `first_call.py`라고 가정하면 실행은 아래처럼 합니다.

```bash
python first_call.py
```

정상 동작 기준은 세 가지입니다.

- 본문 텍스트가 출력된다.
- `model`에 `llama-3.1-8b-instant`가 보인다.
- `prompt_tokens`, `completion_tokens`, `total_tokens`가 숫자로 찍힌다.

여기까지 왔다면 이미 LLM 앱의 첫 번째 관문은 통과한 셈입니다. 이후에 붙는 프롬프트 엔지니어링, 멀티턴 상태, 스트리밍, 캐싱은 모두 이 기본 호출을 변형한 것입니다.

---

## 마무리

오늘 만든 코드는 짧지만, 그 안에 LLM 앱의 핵심 구조가 그대로 들어 있습니다. 환경변수에서 키를 읽고, 클라이언트를 만들고, 메시지 배열과 모델명을 보내고, 응답에서 본문과 사용량을 꺼냅니다. 이 패턴은 공급자가 바뀌어도 거의 유지됩니다.

다음 글에서는 응답 구조에서 잠깐만 보고 지나간 토큰을 본격적으로 다룹니다. 프롬프트가 길어질수록 비용이 어떻게 커지는지, 컨텍스트 창이 왜 중요한지, 왜 어떤 요청은 갑자기 잘리거나 비싸지는지를 수치로 이해해 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- **LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기 (현재 글)**
- 토큰 이해하기 — 비용, 한계, 컨텍스트 창 (예정)
- 프롬프트 엔지니어링 기초 — System·User·Assistant 역할 (예정)
- Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기 (예정)
- 대화 상태 관리 — 멀티턴 챗봇 만들기 (예정)
- 스트리밍 응답 처리 — 실시간으로 출력 받기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Groq quickstart](https://console.groq.com/docs/quickstart)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Groq models](https://console.groq.com/docs/models)

Tags: LLM, OpenAI, Prompt Engineering, Python
