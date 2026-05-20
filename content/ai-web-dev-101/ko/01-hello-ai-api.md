---
title: "AI Web Development 101 (1/7): AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기"
series: ai-web-dev-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI
- LLM
- 웹 개발
- Python
- Tutorial
last_reviewed: '2026-05-14'
seo_description: OpenAI API로 첫 요청을 보내며 인증, 응답 구조, 실패 지점, 토큰 비용 감각까지 함께 익힙니다.
---

# AI Web Development 101 (1/7): AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기

ChatGPT를 브라우저에서 쓰는 경험과, 내 서비스 코드에서 모델을 호출하는 경험은 꽤 다릅니다. 전자는 완성된 제품을 사용하는 일이고, 후자는 외부 모델 서비스를 내 기능 안으로 편입하는 개발 작업입니다. 여기서부터 인증, 요청 형식, 응답 파싱, 타임아웃, 비용 기록 같은 현실적인 문제가 바로 시작됩니다.

이 글은 AI 웹 개발 입문 시리즈의 첫 번째 글입니다.

여기서는 OpenAI API로 가장 작은 성공 경로를 만들고, 첫 호출을 운영 가능한 멘탈 모델로 바꾸겠습니다.

## 먼저 던지는 질문

- ChatGPT 웹사이트를 쓰는 것과 AI API를 붙이는 것은 무엇이 다를까요?
- OpenAI API를 호출하려면 어떤 준비가 필요할까요?
- 첫 번째 요청은 어떤 형식으로 보내고, 어디서 응답을 읽어야 할까요?

## 큰 그림

![AI Web Development 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/01/api-call-overview.ko.png)

*AI Web Development 101 1장 흐름 개요*

이 그림에서는 AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 첫 호출을 제대로 이해해야 할까

입문 단계에서는 모델 성능보다 서비스 경계가 더 먼저 헷갈립니다. 채팅 UI는 이 경계를 감춰 주지만, 런타임에서 실제로 일어나는 일은 단순합니다. 애플리케이션이 인증 헤더와 JSON 본문을 담아 HTTP 요청을 보내고, 모델 서비스가 JSON 응답을 돌려줍니다.

이 구조를 초기에 정확히 잡아 두면 이후 주제들이 훨씬 또렷해집니다. 토큰 비용을 읽는 일도, 프롬프트 구조를 설계하는 일도, 스트리밍을 붙이는 일도 모두 첫 호출의 요청-응답 구조 위에 쌓입니다. 반대로 이 지점이 흐리면 이후 기능은 전부 “되긴 되는데 왜 그런지 모르겠다”는 상태로 남기 쉽습니다.

현업에서는 이 차이가 바로 드러납니다. `401`이면 프롬프트보다 인증을 먼저 봐야 하고, `429`면 문장 표현보다 호출 빈도와 예산을 먼저 봐야 합니다. 첫 호출을 투명하게 보는 습관이 생기면, 이후의 AI 개발은 훨씬 덜 신비롭고 훨씬 더 다루기 쉬워집니다.

## OpenAI API를 부를 때 필요한 최소 준비

준비 단계는 길지 않습니다. 계정을 만들고, API 키를 발급하고, 로컬 환경변수에 넣고, SDK를 설치하면 됩니다. 중요한 습관은 비밀 키를 코드에 박아 넣지 않는 것입니다.

1. [OpenAI Platform](https://platform.openai.com/)에 가입합니다.
2. `API Keys`에서 새 키를 발급합니다.
3. `Settings > Billing`에서 결제 수단과 예산을 확인합니다.
4. 로컬 셸이나 `.env` 파일을 통해 `OPENAI_API_KEY`를 주입합니다.

```bash
# macOS / Linux
export OPENAI_API_KEY="your-issued-key"

# 현재 셸에서 값이 잡혔는지 확인
python3 - <<'PY'
import os
print("key loaded:", bool(os.environ.get("OPENAI_API_KEY")))
PY
```

**Expected output:**

```text
key loaded: True
```

값이 `False`라면 아직 모델 호출을 보기 전에 환경변수 주입부터 고쳐야 합니다. 첫 호출 실패의 상당수는 여기서 시작합니다.

## SDK 메서드보다 먼저 봐야 할 것: JSON 요청과 JSON 응답

OpenAI Python SDK는 편리하지만, 실제 계약을 바꾸지는 않습니다. `client.chat.completions.create()`는 결국 JSON 요청을 만들고 JSON 응답을 Python 객체로 감싼 결과를 돌려줍니다. 그래서 첫 호출을 이해할 때는 “메서드를 어떻게 부르느냐”보다 “어떤 필드를 보내고 어떤 필드를 받느냐”를 먼저 보는 편이 정확합니다.

개념적으로 요청 본문은 아래처럼 생깁니다.

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "user",
      "content": "AI API 개발을 막 시작한 사람에게 응원의 한마디를 해줘."
    }
  ]
}
```

응답에서 초반에 꼭 읽어야 할 세 블록은 `model`, `choices`, `usage`입니다.

```json
{
  "model": "gpt-4o-mini-2024-07-18",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "작은 자동화부터 붙여 보세요. 첫 연결이 되면 다음 단계가 훨씬 선명해집니다."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 24,
    "completion_tokens": 19,
    "total_tokens": 43
  }
}
```

이 구조를 초반에 익혀 두면 이후 스트리밍, RAG, 에이전트, 평가 단계에서도 어디를 읽어야 하는지 감이 유지됩니다.

![API 응답 JSON의 핵심 필드](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/01/request-response-anatomy.ko.png)

*API 응답 JSON의 핵심 필드*

## 가장 작은 성공 경로: SDK 설치와 첫 호출

먼저 Python 가상환경과 SDK를 준비합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "openai>=2.0"
```

이제 가장 작은 성공 경로를 만듭니다.

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "AI API 개발을 막 시작한 사람에게 응원의 한마디를 해줘."
        }
    ],
)

print("assistant:", response.choices[0].message.content)
print("model:", response.model)
print("usage:", response.usage)
```

**Expected output:**

```text
assistant: 작은 자동화부터 붙여 보세요. 첫 연결이 되면 다음 단계가 훨씬 선명해집니다.
model: gpt-4o-mini-2024-07-18
usage: CompletionUsage(completion_tokens=19, prompt_tokens=24, total_tokens=43)
```

출력 문구 자체는 달라질 수 있지만, 아래 세 가지는 반드시 확인해야 합니다.

- `response.choices[0].message.content`에 실제 답변 텍스트가 들어 있는가
- `response.model`에서 어떤 모델 버전이 사용됐는지 보이는가
- `response.usage`에서 토큰 사용량을 읽을 수 있는가

## 첫 호출을 서비스 코드로 가져갈 때 필요한 최소 보호막

터미널 실습은 성공했더라도, 서비스 코드에서는 타임아웃과 예외 분기가 필요합니다. 모델 호출은 원격 네트워크 요청이므로, 실패를 “이상한 모델 반응”이 아니라 “외부 API 호출 실패”로 다루는 습관이 중요합니다.

```python
import os
from openai import OpenAI
from openai import APIConnectionError, APIStatusError, RateLimitError

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=20.0)

def ask_model(user_text: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "너는 초보 개발자에게 짧고 실용적으로 설명하는 도우미다."
                },
                {"role": "user", "content": user_text},
            ],
            temperature=0.2,
        )
    except RateLimitError as exc:
        return {"ok": False, "error": f"rate_limit: {exc}"}
    except APIConnectionError as exc:
        return {"ok": False, "error": f"network: {exc}"}
    except APIStatusError as exc:
        return {"ok": False, "error": f"status_{exc.status_code}: {exc}"}

    return {
        "ok": True,
        "answer": response.choices[0].message.content,
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

result = ask_model("토큰 과금이 왜 중요한지 두 문장으로 설명해줘.")
print(result)
```

이 예제의 포인트는 두 가지입니다. 첫째, 실패를 명시적으로 분기합니다. 둘째, 성공 응답에서도 텍스트만 꺼내지 않고 토큰 사용량을 함께 남깁니다. 그래야 나중에 비용, 지연 시간, 실패율을 같은 실행 흐름 안에서 다룰 수 있습니다.

## cURL 한 번으로 요청 계약 확인하기

SDK가 너무 많은 것을 감싸고 있어서 감이 안 올 때는 `curl`이 오히려 더 직관적입니다. 네트워크 요청이 어떤 모양인지 직접 보면, “결국 HTTP + JSON이구나”라는 감각이 빨리 잡힙니다.

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "응답 JSON에서 usage는 왜 중요해?"}
    ]
  }'
```

`curl`은 서비스 코드에 그대로 넣을 도구는 아니지만, 인증 헤더, 엔드포인트, 본문 구조를 눈으로 확인할 때 매우 유용합니다. 특히 SDK 버전이 달라졌을 때도 기본 계약은 거의 그대로 남습니다.

## 응답에서 무엇을 읽어야 할까

입문 단계에서 가장 자주 하는 실수는 응답을 “그냥 문자열”로만 생각하는 것입니다. 하지만 실제 서비스에서는 아래 필드를 함께 읽어야 합니다.

- `choices[0].message.content`: 사용자에게 보여 줄 텍스트
- `finish_reason`: 답이 정상 종료됐는지, 길이 제한 때문에 끊겼는지 판단하는 단서
- `usage.prompt_tokens`: 입력 길이 비용 감각
- `usage.completion_tokens`: 출력 길이 비용 감각
- `model`: 어떤 버전이 실제로 응답했는지 기록할 값

예를 들어 `finish_reason`이 `length`라면 프롬프트 자체가 나쁜 것이 아니라 `max_tokens`가 너무 짧았을 가능성을 먼저 봐야 합니다. 즉, 응답 구조를 읽는 일은 곧 실패 원인을 분류하는 일입니다.

## 토큰 비용을 초반부터 기록해야 하는 이유

AI API는 대개 토큰 기반으로 과금됩니다. 토큰은 글자 수와 완전히 같지는 않지만, “입력 길이와 출력 길이가 길어질수록 비용이 늘어난다”는 감각을 잡는 데는 충분합니다. 초반부터 `usage`를 확인하는 습관이 있으면, 이후 대화 길이가 늘어나거나 RAG 문맥이 붙을 때 비용 변화를 설명하기가 훨씬 쉽습니다.

간단한 로깅 함수만 있어도 도움이 됩니다.

```python
def log_usage(result: dict) -> None:
    if not result["ok"]:
        print("request failed:", result["error"])
        return

    print(
        "usage => prompt:", result["prompt_tokens"],
        "completion:", result["completion_tokens"],
        "total:", result["total_tokens"],
    )

result = ask_model("한 줄 요약으로 AI API의 핵심을 말해줘.")
log_usage(result)
```

![입력 토큰 수와 응답 비용의 관계](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/01/tokens-and-cost-flow.ko.png)

*입력 토큰 수와 응답 비용의 관계*

## 첫 호출이 실패할 때는 무엇부터 볼까

초반 디버깅은 모델의 창의성을 고치는 일이 아니라, 실패 지점을 계층별로 좁히는 일입니다.

### 1. `401` 또는 인증 오류

- `OPENAI_API_KEY`가 실제 셸에 잡혀 있는지 확인합니다.
- 앞뒤 공백이나 잘못 복사된 키가 없는지 봅니다.
- 다른 프로젝트용 키를 실수로 사용하지 않았는지 확인합니다.

### 2. `404` 또는 잘못된 모델 이름

- 모델 ID를 공식 문서와 대시보드 기준으로 다시 확인합니다.
- 예제 글에서 본 오래된 모델 이름을 복사해 오지 않았는지 봅니다.

### 3. `429` 또는 속도 제한

- 짧은 시간에 너무 많은 호출을 보내지 않았는지 확인합니다.
- 자동 재시도가 있다면 폭주하지 않는지 봅니다.
- 사용량 대시보드와 예산 한도를 함께 점검합니다.

### 4. 응답은 왔는데 원하는 답이 아님

- 먼저 요청 구조와 역할 구분이 맞는지 봅니다.
- 그다음 `system`, `user`, 출력 길이 제약을 점검합니다.
- 이 단계에서야 비로소 프롬프트 개선으로 넘어갑니다.

이 순서를 익혀 두면, “AI가 이상해요”라는 막연한 표현을 인증 문제, 모델 선택 문제, 프롬프트 문제로 분리해서 다룰 수 있습니다.

## 작은 실습: 번역기 한 번 더 만들기

마지막으로 `system`과 `user`를 함께 쓰는 가장 작은 예제를 다시 한 번 실행해 보겠습니다. 다음 글의 프롬프트 엔지니어링으로 자연스럽게 이어지는 실습입니다.

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def translate_ko_to_en(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "너는 한국어 문장을 자연스러운 영어로 번역하는 기술 번역가다."
            },
            {
                "role": "user",
                "content": f"다음 문장을 영어로 번역해줘: {text}"
            },
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content

print(translate_ko_to_en("오늘은 API 응답 구조를 먼저 이해하는 것이 중요합니다."))
```

**Expected output:**

```text
Today, it is important to understand the API response structure first.
```

이 예제에서 중요한 것은 번역 자체보다 역할 분리입니다. `system`은 장기 규칙을, `user`는 현재 작업을 전달합니다. 다음 글에서 다룰 프롬프트 설계의 출발점도 바로 이 구조입니다.

![번역 요청을 만드는 System Prompt와 User Prompt 구성](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/01/translation-exercise-flow.ko.png)

*번역 요청을 만드는 System Prompt와 User Prompt 구성*

## 체크리스트

- [ ] `OPENAI_API_KEY`를 코드에 하드코딩하지 않았다.
- [ ] `model`, `messages`, `choices`, `usage`의 역할을 설명할 수 있다.
- [ ] 첫 호출 성공 후 토큰 사용량까지 함께 확인했다.
- [ ] `401`, `404`, `429`를 프롬프트 문제와 구분해 볼 수 있다.

## 정리

첫 호출 단계에서 가장 중요한 것은 “모델을 불렀다”보다 “API 계약을 읽을 수 있게 됐다”는 점입니다.

- AI API는 완성된 채팅 제품이 아니라, 내 서비스가 호출하는 외부 모델 인터페이스입니다.
- OpenAI SDK 아래에서는 결국 HTTP 요청과 JSON 응답이 오갑니다.
- 응답 텍스트만이 아니라 `usage`, `finish_reason`, `model`까지 함께 읽어야 운영 감각이 생깁니다.
- 실패를 인증, 모델 이름, 속도 제한, 프롬프트 구조 문제로 나눠 보는 습관이 이후 단계를 쉽게 만듭니다.

이제 모델을 한 번 투명하게 호출해 본 만큼, 다음 글에서는 같은 모델이라도 왜 프롬프트 설계에 따라 결과가 크게 달라지는지 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **ChatGPT 웹사이트를 쓰는 것과 AI API를 붙이는 것은 무엇이 다를까요?**
  - 본문의 기준은 AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **OpenAI API를 호출하려면 어떤 준비가 필요할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **첫 번째 요청은 어떤 형식으로 보내고, 어디서 응답을 읽어야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기 (현재 글)**
- 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술 (예정)
- AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현 (예정)
- RAG 입문 — 내 데이터로 답하는 AI 만들기 (예정)
- AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기 (예정)
- AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기 (예정)
- AI 앱의 평가와 개선, 품질을 측정하고 더 좋게 만드는 법 (예정)

<!-- toc:end -->

## 참고 자료

- [OpenAI API reference: Chat Completions](https://platform.openai.com/docs/api-reference/chat)
- [OpenAI Quickstart](https://platform.openai.com/docs/quickstart)
- [openai-python README](https://github.com/openai/openai-python)
- [OpenAI pricing](https://platform.openai.com/docs/pricing)

Tags: AI, LLM, 웹 개발, Python, Tutorial
