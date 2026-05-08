
# 트리거와 바인딩 — 함수 입출력의 모든 것

앞 장에서 “함수 하나에는 트리거 하나가 묶인다”고 했습니다. 그리고 “바인딩은 입출력을 선언적으로 연결하는 장치”라고 했습니다. 이 두 문장이 Functions 코드를 짧게 만들어 주는 핵심입니다. 그런데 처음 입문하는 사람 입장에서는 “트리거가 뭐고 바인딩이 뭐고 어디서 어디까지가 마법인가”가 잘 안 잡힙니다.

여기서는 그 경계를 분명하게 정리합니다. 트리거의 종류, 입력 바인딩과 출력 바인딩의 차이, 그리고 “바인딩이 마법처럼 보이지만 실제로는 어떤 계약인가”까지 다룹니다. 읽고 나면 새 함수를 만들 때 “어떤 트리거를 골라야 하지?”에서 오래 멈추지 않게 됩니다.

---

<!-- a-grade-intro:begin -->
## 핵심 질문

트리거와 바인딩을 어떻게 사용해야 함수 코드가 단순해지고 운영이 안정될까요?

이 글은 그 질문에 답하기 위해 트리거와 바인딩의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 답할 질문

- trigger와 binding은 본질적으로 무엇이 다르고 왜 분리되어 있는가?
- input binding과 output binding은 코드를 얼마나 줄여주고, 어떤 자유를 빼앗아가는가?
- 여러 trigger를 한 함수에 묶을 수 있는가, 묶지 못한다면 왜인가?
- binding 설정의 connection string은 어디에 두는 것이 안전한가?
- 트리거 메시지의 재처리(retry, poison queue)는 어떻게 흐르는가?

## 트리거 = 함수를 깨우는 “원인”

먼저 단어 정의부터 정확히 합니다. **트리거(trigger)는 함수가 실행되도록 만드는 외부 사건**입니다. HTTP 요청이 들어오는 것, 큐에 메시지가 쌓이는 것, Blob에 파일이 올라오는 것, 매시 정각이 되는 것 — 이 모든 것이 트리거입니다.

규칙은 단순합니다.

- 함수 하나에는 **정확히 하나의 트리거**가 붙습니다.
- 트리거는 함수를 깨우는 동시에 **함수의 입력값(payload)** 을 결정합니다. HTTP 트리거면 요청 객체를, Queue 트리거면 메시지 본문을, Timer 트리거면 스케줄 정보를 함수에 넘겨줍니다.

트리거가 “언제”와 “무엇을 가지고” 둘 다 결정한다는 점이 중요합니다. 이걸 그림으로 보면 다음과 같습니다.

![트리거가 입력과 실행 시점을 정하는 구조](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/02/02-01-a-trigger-is-the-cause-that-wakes-a-func.ko.png)

*트리거가 입력과 실행 시점을 정하는 구조*
---

## 트리거 카탈로그 — 자주 쓰는 것부터

전체 목록은 공식 문서에 있지만, 실무에서 90% 이상은 아래 표 안에서 끝납니다.

| 카테고리 | 트리거 | 대표 사용 사례 |
|---|---|---|
| **HTTP / Webhook** | HTTP, Event Grid | REST API, 외부 SaaS Webhook 수신 |
| **Schedule** | Timer | 정산 배치, 주기적 정리 작업 |
| **Storage** | Blob, Queue | 파일 업로드 후처리, 비동기 작업 큐 |
| **Messaging** | Service Bus, Event Hub, Kafka | 마이크로서비스 간 비동기 통신, 텔레메트리 수집 |
| **Database** | Cosmos DB Change Feed, SQL | 데이터 변경 감지 후처리 (CDC 패턴) |

새 함수를 설계할 때 던질 질문은 항상 같습니다. **“이 함수는 무엇 때문에 깨어나야 하는가?”** 그 답이 곧 트리거 선택입니다.

![대표 트리거와 주요 사용 사례 비교](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/02/02-02-trigger-catalog-the-ones-youll-actually.ko.png)

*대표 트리거와 주요 사용 사례 비교*
---

## 바인딩 = 함수 입출력의 “선언적 연결선”

여기서부터가 Functions의 진짜 매력입니다. 일반 웹 앱에서 “Cosmos DB에 저장”을 하려면 보통 이런 코드를 씁니다. 클라이언트 객체 만들고, 인증 붙이고, 컬렉션 핸들 잡고, `upsert` 호출하고, 에러 처리하고. 함수 본체보다 보일러플레이트가 더 깁니다.

바인딩은 이 보일러플레이트를 “이 함수의 출력은 Cosmos DB의 이 컨테이너로 보내 주세요”라는 선언으로 줄입니다. Azure Functions Python v2 모델에서는 아래처럼 적습니다.

```python
import json
import azure.functions as func

app = func.FunctionApp()

def build_invoice(payload):
    return {"id": payload["order_id"], "amount": payload["total"]}

@app.function_name(name="process_order")
@app.queue_trigger(arg_name="msg", queue_name="orders-incoming", connection="StorageConnection")
@app.cosmos_db_output(
    arg_name="invoice_out",
    database_name="orders",
    container_name="invoices",
    connection="CosmosConnection",
)
def process_order(msg: func.QueueMessage, invoice_out: func.Out[func.Document]) -> None:
    queue_item = msg.get_json()
    invoice = build_invoice(queue_item)
    invoice_out.set(func.Document.from_json(json.dumps(invoice)))
```

이 함수가 하는 일을 평어로 풀면 다음과 같습니다.

> “큐에 메시지가 들어오면(`queue_trigger`) 그것을 invoice로 가공하고, 그 결과를 Cosmos DB의 `invoices` 컨테이너에 저장한다(`cosmos_db_output`).”

DB 연결, 인증, 재시도 같은 운영 코드는 **Functions Host가 대신 처리**합니다. 여러분은 “어디로 보낼지”만 선언했을 뿐입니다.

---

## 입력 바인딩과 출력 바인딩

바인딩은 방향에 따라 둘로 나뉩니다.

- **입력 바인딩(input binding)** — 함수 실행 시점에 외부 데이터를 읽어다가 함수에 넘겨줌
- **출력 바인딩(output binding)** — 함수가 반환한 값을 외부로 내보냄

흔한 오해 하나를 짚고 갑니다. **트리거와 입력 바인딩은 다릅니다.**

- **트리거** = “함수를 깨우는 사건 + 그 사건의 페이로드”
- **입력 바인딩** = “함수가 깨어난 뒤, 추가로 외부에서 읽어오는 데이터”

예를 들어 “HTTP 요청이 들어오면(트리거) 그 요청의 user_id로 Cosmos DB에서 사용자 정보를 조회해서(입력 바인딩) 응답한다”라는 함수가 있을 수 있습니다. 트리거는 HTTP, 입력 바인딩은 Cosmos DB입니다.

세 종류의 관계를 한 그림으로 정리하면 이렇습니다.

![트리거와 입출력 바인딩의 역할 차이](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-101/02/02-03-input-bindings-vs-output-bindings.ko.png)

*트리거와 입출력 바인딩의 역할 차이*
함수는 가운데에 있고, 외부 세계와는 트리거·입력·출력 세 갈래로 연결됩니다. **이 세 갈래를 선언적으로 표현한 것이 바인딩의 본질**입니다.

---

## 바인딩이 “마법”처럼 보이는 이유 — 그리고 진짜 정체

“DB 클라이언트도 없는데 어떻게 저장이 되지?” 처음에는 신기하지만, 안을 들여다보면 마법은 아닙니다.

각 바인딩에는 **확장(extension)** 이라는 패키지가 따라옵니다. 예를 들어 Cosmos DB 출력 바인딩은 `Microsoft.Azure.WebJobs.Extensions.CosmosDB`라는 확장이 제공합니다. 이 확장이 실제로 하는 일은 다음 셋입니다.

1. 함수 등록 시점에 “이 함수의 출력은 Cosmos DB로 가야 한다”는 메타데이터를 Host에 등록
2. 함수 실행 직후, Host가 “함수가 뭔가 반환했다”는 신호를 받으면 확장의 핸들러가 호출됨
3. 핸들러가 실제 Cosmos DB 클라이언트를 만들어서 데이터를 저장

즉, 여러분이 직접 짤 코드를 **확장이 대신 짜둔 것**입니다. 마법이 아니라 위임입니다. 그래서 다음 두 가지를 기억해 둘 필요가 있습니다.

- 바인딩이 자동으로 처리하는 것: 연결, 인증, 직렬화, 기본적인 재시도
- 바인딩이 자동으로 처리하지 않는 것: 비즈니스 검증, 부분 실패 정책, 트랜잭션 경계

복잡한 트랜잭션이나 정교한 에러 처리가 필요하다면 출력 바인딩 대신 직접 클라이언트를 쓰는 게 나을 때도 있습니다. 입문자에게 흔한 함정 한 줄로 요약하면 이렇습니다. **바인딩은 보일러플레이트를 줄이는 도구이지, 도메인 로직을 대신해 주는 도구가 아닙니다.**

---

## 자주 보는 조합 5가지

실무에서 반복적으로 나오는 트리거·바인딩 조합을 모아두면 새 함수를 설계할 때 빠릅니다.

| 패턴 | 트리거 | 입력 바인딩 | 출력 바인딩 | 흔한 사용 사례 |
|---|---|---|---|---|
| **API + DB 조회** | HTTP | Cosmos DB | — | 단순 조회 API |
| **API + DB 저장** | HTTP | — | Cosmos DB | Webhook 수신 후 적재 |
| **큐 → DB 적재** | Queue | — | Cosmos DB | 비동기 주문 처리 |
| **파일 → 썸네일** | Blob | — | Blob | 이미지 후처리 |
| **DB 변경 → 알림** | Cosmos Change Feed | — | Service Bus | CDC 기반 이벤트 발행 |

이 다섯 패턴만 알아도 입문 단계에서 작성하는 함수의 8할은 커버됩니다.

---

## 알아두면 좋은 두 가지 함정

**1) 출력 바인딩의 실패는 함수의 성공/실패와 별개로 다뤄질 수 있습니다.**
함수 본체는 성공했는데 출력 바인딩에서 DB 저장이 실패할 수 있습니다. 이 경우 함수는 실패로 기록되지만, 트리거의 재시도 정책에 따라 함수가 다시 실행됩니다. 즉 **멱등성(idempotency)** 을 신경 써야 합니다. 같은 메시지가 두 번 처리돼도 결과가 같아야 합니다.

**2) 바인딩의 connection은 “문자열”이 아니라 “설정 키 이름”입니다.**
`connection: 'StorageConnection'`이라고 쓰면 “환경 변수 `StorageConnection`의 값을 연결 문자열로 사용하라”는 뜻입니다. 코드에 직접 연결 문자열을 박지 않습니다. 운영 환경에서는 이게 Key Vault나 Managed Identity로 바뀌고, 운영 장에서 그 관점을 다시 정리합니다.

---

## 왜 이 경계가 중요한가

지금까지 “함수의 바깥 인터페이스”를 봤습니다. 트리거가 함수를 어떻게 깨우는지, 바인딩이 입출력을 어떻게 선언적으로 처리하는지. 그 다음으로 이해해야 할 경계는 **“그래서 함수 코드는 누가, 어떻게, 어떤 프로세스 안에서 실행되는가?”** 입니다.

답은 **Host와 Worker**라는 두 단어입니다. Functions가 Node.js, Python, Java, .NET 같은 여러 언어 런타임을 어떻게 붙이는지는 거기에서 갈립니다.

---

앞 장에서 잡은 멘탈 모델은 Trigger와 Binding을 통해 실제 입출력 표면으로 구체화됩니다. 이어지는 Host와 Worker 장을 보면 그 표면 아래에서 실행 경계가 어떻게 나뉘는지 자연스럽게 연결됩니다.

---

## 시니어 엔지니어는 이렇게 생각합니다

- **트리거는 함수의 계약이다** — 입력 형태·실행 보장 수준이 트리거 선택에서 결정됩니다.
- **바인딩으로 보일러플레이트를 줄인다** — SDK 직접 호출보다 운영 일관성이 높습니다.
- **재시도·중복 처리 의미를 안다** — at-least-once 전제가 없으면 데이터 사고가 됩니다.
- **Poison queue를 표준 처리한다** — 실패 메시지를 잃지 않는 구조가 신뢰성의 기본입니다.
- **바인딩 한계도 인지한다** — 복잡한 라우팅은 SDK 직접 사용이 더 깔끔합니다.

## 운영 체크리스트

- [ ] trigger와 binding을 코드와 설정으로 명시적으로 분리했다
- [ ] binding이 숨기는 동작(자동 직렬화/역직렬화)을 문서화했다
- [ ] connection string은 Key Vault나 Managed Identity로 주입했다
- [ ] 재시도 정책과 poison queue 경로를 명시했다
- [ ] binding 변경의 회귀를 잡는 통합 테스트를 추가했다

## 시리즈 목차

- [Azure Functions란? — 이벤트가 함수를 호출하는 세상](./01-what-is-azure-functions.md)
- **트리거와 바인딩 — 함수 입출력의 모든 것 (현재 글)**
- Host와 Worker — 함수는 누가 실행하는가 (예정)
- 함수 하나 배포하기 — 로컬에서 Azure까지 (예정)
- 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated (예정)
- 스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간 (예정)
- 모니터링과 운영 기초 (예정)

---

## 참고 자료

**공식 문서**
- [Azure Functions triggers and bindings concepts](https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
- [Trigger and binding examples](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-example)
- [Register Azure Functions binding extensions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-register)

**소스코드**
- [`Azure/azure-functions-host`](https://github.com/Azure/azure-functions-host)
- [`Azure/azure-webjobs-sdk-extensions`](https://github.com/Azure/azure-webjobs-sdk-extensions) — 바인딩 확장의 본거지

**관련 시리즈**
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/) — Host와 Binding 확장이 실제로 어떻게 움직이는지 더 안쪽까지 볼 수 있습니다

Tags: Azure, Azure Functions, Serverless, Cloud

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
