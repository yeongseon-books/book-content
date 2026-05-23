---
title: "API Design 101 (6/10): Pagination과 filtering"
series: api-design-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
  - Computer Science
  - APIDesign
  - Pagination
  - Filtering
  - Performance
  - Backend
last_reviewed: '2026-05-15'
seo_description: 목록 API의 pagination, sorting, filtering 설계 원칙과 trade-off를 정리합니다.
---

# API Design 101 (6/10): Pagination과 filtering

목록 API는 처음에는 금방 만들 수 있어 보여도, 데이터가 쌓이는 순간 가장 먼저 흔들리는 지점이 됩니다. 느려진 쿼리, 중복 응답, 누락된 항목이 한꺼번에 나타나기 시작하면 파라미터 이름 하나도 쉽게 바꾸지 못합니다.

여기서는 pagination, sorting, filtering을 단순 옵션 모음이 아니라 성능과 정확성을 함께 지키는 계약으로 정리합니다. 특히 offset과 cursor의 선택이 어떤 운영 비용을 만드는지까지 같이 봅니다.

![API Design 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/06/06-01-concept-at-a-glance.ko.png)
*클라이언트 요청이 filter → sort → paginate 순서로 처리되는 흐름*

## 먼저 던지는 질문

- offset / limit 방식은 어디까지 단순하고 어디서부터 한계가 드러날까요?
- cursor 기반 pagination은 어떤 문제를 해결하며 어떤 것을 포기할까요?
- sorting, filtering, searching은 어떤 규칙으로 분리해야 할까요?

## 왜 pagination이 API에서 가장 먼저 흔들리는가

pagination은 "큰 리스트를 나눠 보내는 기능" 정도로 보일 수 있습니다. 하지만 실제로는 다음 세 가지가 동시에 충돌하는 지점입니다.

| 요구 | 위협 |
|---|---|
| 성능 — 응답 시간을 일정하게 유지 | 깊은 offset, 무제한 limit |
| 정확성 — 중복·누락 없이 모든 행을 정확히 한 번 전달 | 페이지 이동 중 데이터 삽입·삭제 |
| 호환성 — 한 번 공개한 파라미터는 쉽게 바꿀 수 없음 | 초기 설계 실수가 장기 부채로 고착 |

한 번 공개된 목록 API는 클라이언트가 이미 `offset=`을 쓰고 있기 때문에, 뒤늦게 cursor로 바꾸려면 별도 버전이 필요합니다. 그래서 처음부터 의도를 가지고 선택해야 합니다.

실제로 Twitter는 2012년에 offset 방식의 timeline API를 cursor 기반으로 교체하면서 별도 v1.1 버전을 발행해야 했습니다. 이런 비용을 피하려면 첫 설계에서 데이터 규모와 변동 빈도를 함께 고려해야 합니다.

## Offset 방식 — 장점과 한계

### 동작 원리

```sql
SELECT * FROM orders
WHERE status = 'paid'
ORDER BY created_at DESC
LIMIT 20 OFFSET 40;
```

DB는 처음 40개 행을 읽고 버린 뒤 다음 20개를 반환합니다. offset이 커질수록 버리는 행이 많아져 응답 시간이 선형으로 증가합니다.

### 언제 적합한가

- 전체 행 수가 수천 건 이하로 예측 가능할 때
- 관리자 대시보드처럼 "3페이지로 이동" UI가 필수일 때
- 데이터가 자주 삽입·삭제되지 않는 정적 리스트

### 한계가 드러나는 시점

| 증상 | 원인 |
|---|---|
| 페이지가 깊어질수록 느려짐 | `OFFSET 100000`이면 100,000행을 읽고 버림 |
| 같은 항목이 두 번 보임 | 페이지 이동 사이에 앞쪽에 행이 삽입됨 |
| 항목이 건너뛰어짐 | 페이지 이동 사이에 앞쪽 행이 삭제됨 |
| total count가 느려짐 | `COUNT(*)` 자체가 큰 테이블에서 수백 ms |

PostgreSQL의 경우 offset 10만 이상에서 실행 계획이 Seq Scan으로 바뀌는 사례가 흔합니다. 인덱스가 있어도 DB는 "건너뛴 행 수만큼 읽기"를 피할 수 없습니다. MySQL(InnoDB)도 마찬가지로 clustered index를 따라 행을 하나씩 세면서 건너뛰므로, offset이 깊을수록 buffer pool 히트율이 떨어집니다.

## Cursor 방식 — 원리와 trade-off

### 동작 원리

```sql
SELECT * FROM orders
WHERE status = 'paid'
  AND (created_at, id) < ('2026-05-01T10:00:00Z', 'ord_abc')
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

마지막으로 본 항목의 정렬 키를 조건으로 넣으므로 DB는 항상 인덱스에서 해당 위치로 바로 seek합니다. offset과 달리 앞쪽 행을 읽고 버리는 비용이 없습니다.

### Cursor 토큰 설계

```python
import base64, json

def encode_cursor(last_item: dict) -> str:
    payload = {"created_at": last_item["created_at"], "id": last_item["id"]}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

def decode_cursor(token: str) -> dict:
    return json.loads(base64.urlsafe_b64decode(token.encode()).decode())
```

클라이언트는 이 토큰 내부를 해석하지 않아야 합니다. 서버가 정렬 키와 경계 조건을 책임지므로 중복과 누락 없이 큰 결과 집합을 안정적으로 넘길 수 있습니다.

### Offset vs Cursor 비교표

| 기준 | Offset | Cursor |
|---|---|---|
| 구현 난이도 | 낮음 | 중간 |
| 깊은 페이지 성능 | O(offset) — 선형 저하 | O(1) — 일정 |
| 임의 페이지 접근 | 가능 (`?page=5`) | 불가 (순차만) |
| 삽입/삭제 시 정확성 | 중복·누락 발생 | 안정 |
| 총 개수 필요 | 보통 함께 제공 | 제공하지 않아도 됨 |
| 적합한 시나리오 | 소규모·정적 리스트, 관리자 UI | 피드, 무한 스크롤, 대규모 데이터 |

### 실제 서비스의 선택

- **GitHub REST API**: `Link` header에 `rel="next"` URL을 담아 반환. cursor 기반.
- **Stripe**: `has_more` boolean + `data[].id`를 `starting_after` 파라미터로 사용. cursor 기반.
- **Slack**: `response_metadata.next_cursor`를 반환. cursor 기반.
- **GitHub GraphQL**: `pageInfo { endCursor, hasNextPage }`. Relay 스펙 cursor.
- **Elasticsearch**: `search_after` 파라미터로 정렬 값 배열을 전달. cursor 변형.

대규모 피드를 다루는 서비스는 예외 없이 cursor를 기본으로 채택합니다.

## 응답 envelope 설계

### Offset 방식 응답

```json
{
  "data": [...],
  "meta": {
    "total": 4821,
    "offset": 40,
    "limit": 20
  }
}
```

### Cursor 방식 응답

```json
{
  "data": [...],
  "meta": {
    "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNi0wNS0wMVQxMDowMDowMFoiLCJpZCI6Im9yZF9hYmMifQ",
    "has_more": true
  }
}
```

`has_more`가 `false`이면 마지막 페이지입니다. total count를 별도로 계산하지 않아도 클라이언트는 "더 있는지"를 판단할 수 있습니다.

### Total count를 제공해야 할까?

| 상황 | 권장 |
|---|---|
| 전체 행이 1만 이하, UI에 "전체 N건" 표시 필요 | 제공 |
| 행이 수십만 이상, 피드형 UI | 미제공 또는 `approximate_total` |
| 관리자 대시보드 | `total`을 별도 endpoint로 분리 |

큰 테이블에서 매 요청마다 `COUNT(*)`를 돌리면 DB 부하가 pagination 자체보다 클 수 있습니다.

## Sorting 설계

### 단일 정렬

```http
GET /orders?sort=created_at:desc
```

### 다중 정렬

```http
GET /orders?sort=status:asc,created_at:desc
```

### 설계 규칙

1. **허용 목록**: 정렬 가능한 필드를 서버가 명시합니다. 임의 컬럼 정렬을 허용하면 인덱스 없는 컬럼에 ORDER BY가 걸려 full scan이 발생합니다.
2. **기본값 명시**: `sort` 파라미터가 없을 때의 기본 정렬을 문서화합니다.
3. **일관된 문법**: `field:direction` 또는 `-field`(prefix minus = desc) 중 하나를 선택하고 전체 API에서 통일합니다.

```python
ALLOWED_SORT_FIELDS = {"created_at", "updated_at", "name", "price"}

def parse_sort(raw: str) -> list[tuple[str, str]]:
    """'created_at:desc,name:asc' → [('created_at', 'desc'), ('name', 'asc')]"""
    result = []
    for part in raw.split(","):
        field, _, direction = part.partition(":")
        if field not in ALLOWED_SORT_FIELDS:
            raise ValueError(f"정렬 불가: {field}")
        direction = direction or "asc"
        if direction not in ("asc", "desc"):
            raise ValueError(f"잘못된 방향: {direction}")
        result.append((field, direction))
    return result
```

## Filtering 설계

### 단순 equality

```http
GET /orders?status=paid&tier=pro
```

### 범위·비교 연산자

```http
GET /orders?created_at__gte=2026-01-01&amount__lt=10000
```

`__gte`, `__lt`, `__in` 같은 suffix를 쓰면 문서화와 서버 측 검증이 모두 쉬워집니다.

### 설계 규칙

| 규칙 | 이유 |
|---|---|
| 허용 필드를 명시 | 임의 컬럼 필터 → 인덱스 없는 조건 → slow query |
| enum 값을 문서화 | `status=xxx` 같은 잘못된 값에 400을 반환하려면 서버가 유효 값을 알아야 |
| 다중 값은 쉼표 | `status=paid,shipped` → IN 절 |
| 빈 필터 = 전체 | 필터 누락 시 조건 없이 반환 (단, limit는 여전히 적용) |

### Filter vs Search 분리

```http
# filter — 정확한 필드 조건
GET /orders?status=paid&tier=pro

# search — 전문 검색
GET /orders?q=python+logging
```

filter는 WHERE 절의 equality/range 조건, search는 LIKE나 full-text index를 타는 자유 텍스트입니다. 둘을 같은 파라미터에 섞으면 서버가 "이게 필드 조건인지 텍스트 검색인지" 판단해야 하므로 검증과 최적화가 모두 어려워집니다.

검색 결과가 복잡해지면 별도 endpoint(`GET /orders/search?q=...`)로 분리하는 것도 검토합니다.

## 실습: FastAPI로 구현하는 cursor pagination

```python
# pagination_example.py
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import base64, json

app = FastAPI()

# 예시 데이터 (실제로는 DB 쿼리)
ORDERS = [
    {"id": f"ord_{i:04d}", "status": "paid", "created_at": f"2026-05-{20-i//100:02d}T{10+i%24:02d}:00:00Z"}
    for i in range(500)
]

class PaginatedResponse(BaseModel):
    data: list[dict]
    meta: dict

def encode_cursor(item: dict) -> str:
    payload = {"created_at": item["created_at"], "id": item["id"]}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

def decode_cursor(token: str) -> dict:
    try:
        return json.loads(base64.urlsafe_b64decode(token.encode()).decode())
    except Exception:
        raise HTTPException(status_code=400, detail="잘못된 cursor입니다.")

@app.get("/orders", response_model=PaginatedResponse)
def list_orders(
    status: str | None = None,
    sort: str = "created_at:desc",
    limit: int = Query(default=20, le=100, ge=1),
    cursor: str | None = None,
):
    # 1. Filter
    filtered = ORDERS
    if status:
        filtered = [o for o in filtered if o["status"] == status]

    # 2. Sort(간단한 형태:created_at만 지원)
    reverse = sort.endswith(":desc")
    filtered.sort(key=lambda o: o["created_at"], reverse=reverse)

    # 3. Cursor 적용
    if cursor:
        decoded = decode_cursor(cursor)
        # created_at 기준으로 이미 지난 항목 건너뛰기
        start_idx = 0
        for i, o in enumerate(filtered):
            if o["id"] == decoded["id"]:
                start_idx = i + 1
                break
        filtered = filtered[start_idx:]

    # 4. Limit
    page = filtered[:limit]
    has_more = len(filtered) > limit

    meta = {"has_more": has_more}
    if has_more and page:
        meta["next_cursor"] = encode_cursor(page[-1])

    return PaginatedResponse(data=page, meta=meta)
```

## Link header를 활용한 pagination

REST API에서 다음 페이지 URL을 본문이 아닌 HTTP header로 전달하는 방식도 널리 쓰입니다. GitHub REST API가 대표적입니다.

```http
HTTP/1.1 200 OK
Link: <https://api.example.com/orders?cursor=eyJ...&limit=20>; rel="next",
      <https://api.example.com/orders?cursor=eyK...&limit=20>; rel="prev"
```

이 방식의 장점은 응답 본문 스키마를 변경하지 않아도 pagination 메타데이터를 전달할 수 있다는 것입니다. 클라이언트는 `Link` header를 파싱해서 `rel="next"` URL을 그대로 호출하면 됩니다. 단점은 브라우저 JavaScript에서 header 접근이 CORS 설정(`Access-Control-Expose-Headers: Link`)을 추가로 요구한다는 것입니다.

### 본문 vs Header — 언제 어느 쪽을 쓸까?

| 조건 | 본문 meta | Link header |
|---|---|---|
| 클라이언트가 브라우저 JS 위주 | 적합 | CORS 추가 설정 필요 |
| hypermedia 원칙 준수 필요 | 보조 | 적합 (RFC 8288) |
| GraphQL 혼용 환경 | 적합 (header 없음) | 부적합 |
| SDK 제공 시 | 둘 다 가능 | SDK가 header 파싱 처리 |

실무에서는 본문에 `next_cursor`를 넣으면서 동시에 `Link` header도 제공하는 하이브리드 방식을 쓰는 팀도 있습니다. 중요한 것은 하나를 선택하면 전체 API에서 일관되게 적용하는 것입니다.

`limit`에 `le=100`으로 상한을 두었습니다. cursor 디코딩 실패 시 400을 반환하므로 클라이언트가 위조한 토큰을 거부합니다.

## 자주 하는 실수 다섯 가지

| # | 실수 | 결과 | 해결 |
|---|---|---|---|
| 1 | `limit` 상한 없음 | 한 번에 수십만 건 요청 → OOM, 타임아웃 | `le=100` 같은 상한 강제 |
| 2 | 깊은 offset 허용 | `offset=100000` → 수 초 응답 | cursor 전환 또는 offset 상한 설정 |
| 3 | 항상 total 계산 | `COUNT(*)` 비용이 본 쿼리보다 큼 | `has_more`로 대체, total은 선택적 |
| 4 | filter·sort·search 한 파라미터 | 검증·문서화·최적화 불가 | 각각 별도 파라미터 |
| 5 | cursor 내부 구조 노출 | 클라이언트 위조, 데이터 유출 힌트 | base64 불투명 토큰, 서명 추가 가능 |

## 시니어 엔지니어는 이렇게 판단합니다

- 새 컬렉션 endpoint를 만들 때 기본값은 cursor입니다. offset은 "정말 필요할 때"만 추가합니다.
- 기본 `limit`와 최대 `limit`를 API 문서 첫 줄에 적습니다. 이 값이 없으면 클라이언트가 무한 루프를 돌 수 있습니다.
- total count는 비용이 크면 별도 endpoint(`GET /orders/count?status=paid`)로 분리하거나 `approximate_total`을 반환합니다.
- filter 값은 OpenAPI schema에서 enum으로 선언합니다. 잘못된 값이 들어오면 400을 반환하지, 빈 결과를 반환하지 않습니다.
- 검색은 "별도 endpoint로 빼는 게 나을까?"를 항상 검토합니다. 특히 full-text search는 인프라(Elasticsearch 등)가 다를 수 있기 때문입니다.

## 검증 포인트와 실패 신호

- **Expected output:** 같은 필터 조건으로 cursor를 따라 끝까지 넘기면 전체 행이 중복·누락 없이 정확히 한 번 나타나야 합니다. `limit` 상한은 문서와 구현이 일치해야 합니다.
- **First check:** `offset=100000` 같은 깊은 페이지가 호출되는 로그가 보이면, 해당 endpoint를 cursor로 전환할 시점입니다.
- **Failure mode:** total count를 항상 계산하면서 cursor 구조를 그대로 노출하면, 성능과 보안 문제가 함께 터져 API를 뒤늦게 갈아엎게 됩니다.

## 체크리스트

- [ ] `limit`에 상한(예: 100)이 있는가?
- [ ] cursor가 불투명(base64 등)인가?
- [ ] sort, filter, search가 서로 다른 parameter를 쓰는가?
- [ ] 응답에 `next_cursor` 또는 `Link` header가 포함되는가?
- [ ] total count를 비용을 고려해 선택적으로 제공하는가?
- [ ] 허용 sort/filter 필드를 서버가 명시하고, 그 외에는 400을 반환하는가?
- [ ] cursor 디코딩 실패 시 400을 반환하는가?

## 연습 문제

1. 현재 offset 기반 목록 endpoint 하나를 cursor 기반으로 다시 설계해 보세요. 응답 envelope, 파라미터, DB 쿼리를 모두 바꿔 보세요.
2. `sort=price:asc,created_at:desc`를 파싱해서 SQLAlchemy `order_by` 절로 변환하는 함수를 작성해 보세요.
3. filter로 `status=paid,shipped&created_at__gte=2026-01-01`을 받았을 때, 이를 WHERE 절로 변환하는 로직을 작성해 보세요.

## 정리와 다음 글

pagination은 성능과 정확성이 만나는 지점입니다. offset은 구현이 쉽지만 규모가 커지면 한계가 뚜렷하고, cursor는 초기 비용이 조금 높지만 대규모 데이터에서 안정적입니다. 둘 중 하나만 아는 것이 아니라 각각의 trade-off를 알고 상황에 맞게 선택하는 것이 설계입니다.

다음 글에서는 모든 API가 결국 마주치는 또 하나의 주제, error response 설계를 다룹니다.

## 처음 질문으로 돌아가기

- **offset / limit 방식은 어디까지 단순하고 어디서부터 한계가 드러날까요?**
  - 전체 행이 수천 건 이하이고 삽입·삭제가 드문 정적 리스트라면 offset은 충분히 단순하고 효과적입니다. 한계는 두 가지 축에서 드러납니다. 성능 축에서는 offset 값이 커질수록 DB가 앞쪽 행을 읽고 버리는 비용이 선형으로 증가하고, 정확성 축에서는 페이지 이동 중 행이 삽입·삭제되면 중복이나 누락이 발생합니다.
- **cursor 기반 pagination은 어떤 문제를 해결하며 어떤 것을 포기할까요?**
  - cursor는 깊은 페이지 성능 저하와 데이터 변동 시 중복·누락 문제를 해결합니다. 대신 임의 페이지 접근("5페이지로 이동")이 불가능하고, 정렬 키가 고유하지 않으면 복합 키를 구성해야 하는 추가 설계 비용이 듭니다.
- **sorting, filtering, searching은 어떤 규칙으로 분리해야 할까요?**
  - filter는 정확한 필드 조건(WHERE equality/range), sort는 결과 순서(ORDER BY), search는 자유 텍스트 검색(full-text)입니다. 세 가지는 서버 측에서 실행되는 단계와 필요한 인덱스가 다르므로 파라미터를 분리하면 검증, 최적화, 문서화가 모두 독립적으로 가능해집니다.

<!-- toc:begin -->
## 시리즈 목차

- [API Design 101 (1/10): API란 무엇인가?](./01-what-is-an-api.md)
- [API Design 101 (2/10): REST 기본](./02-rest-basics.md)
- [API Design 101 (3/10): 리소스 설계](./03-resource-design.md)
- [API Design 101 (4/10): HTTP method와 status code](./04-http-methods-and-status.md)
- [API Design 101 (5/10): Request와 response schema](./05-request-and-response-schema.md)
- **Pagination과 filtering (현재 글)**
- Error response 설계 (예정)
- OpenAPI와 Swagger (예정)
- Versioning (예정)
- 좋은 API 문서 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [Stripe API: Pagination](https://stripe.com/docs/api/pagination)
- [GitHub REST API: Using Pagination](https://docs.github.com/en/rest/guides/using-pagination-in-the-rest-api)
- [Slack API: Cursor-based Pagination](https://api.slack.com/docs/pagination)
- [RFC 5988 — Web Linking (Link header)](https://www.rfc-editor.org/rfc/rfc5988)

Tags: Computer Science, APIDesign, Pagination, Filtering, Performance, Backend
