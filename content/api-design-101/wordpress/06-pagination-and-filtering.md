---
title: "바이브코딩을 위한 API 설계 기초 (6/10): Pagination과 filtering"
series: api-design-101
episode: 6
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- API설계
- Pagination
seo_description: "AI가 만든 목록 API가 데이터가 쌓이면 왜 느려지는지, offset과 cursor의 차이를 바이브코딩 관점에서 정리합니다."
---

# 바이브코딩을 위한 API 설계 기초 (6/10): Pagination과 filtering

이 글은 바이브코딩을 위한 API 설계 기초 시리즈의 6번째 글입니다.

AI에게 "주문 목록 API 만들어줘"라고 하면 대부분 이렇게 됩니다.

```python
@app.get("/orders")
def list_orders():
    return db.query(Order).all()  # 전체 반환
```

테스트 데이터 100개에서는 완벽하게 동작합니다. 그런데 프로덕션에서 주문이 100만 건이 쌓이면, 이 엔드포인트 하나가 서버 메모리를 한 번에 수 GB 사용하면서 응답 시간이 수십 초가 됩니다. 더 나쁜 경우는 `?limit=99999` 같은 요청이 들어와서 서버가 다운됩니다.

"pagination을 추가해줘"라고 하면 AI는 `?page=1&per_page=20` 형태를 줍니다. 이것도 동작하지만, 데이터가 수십만 건이 되면 `page=5000` 요청이 DB에서 5000번째 페이지를 찾기 위해 10만 개 행을 읽고 버리기 시작합니다. 성능이 선형으로 나빠집니다.

pagination의 두 전략(offset과 cursor)과 그 trade-off를 이해하면, AI에게 데이터 규모에 맞는 올바른 구현을 요청할 수 있습니다.

> pagination은 결과를 잘라 주는 기능이 아니라, 서버가 한 번에 처리할 데이터 양의 상한을 클라이언트와 합의하는 계약입니다.

---

## 이 글에서 다룰 문제
- offset/limit 방식은 어디서 한계가 드러날까요?
- cursor 기반 pagination은 어떤 문제를 해결하고 무엇을 포기할까요?
- sorting, filtering, searching은 어떻게 분리해야 할까요?
- AI가 만든 목록 API가 데이터가 쌓이면 왜 느려지는지 어떻게 파악할까요?
- 바이브코딩에서 pagination 없이 배포하면 어떤 일이 일어날까요?

Offset 방식은 `SELECT ... LIMIT 20 OFFSET 40`처럼 동작합니다. 구현이 쉽지만 offset이 커질수록 DB가 앞쪽 행을 읽고 버리는 비용이 선형으로 증가합니다. Cursor 방식은 마지막으로 본 항목의 정렬 키를 조건으로 사용해서 항상 일정한 성능을 유지합니다.

## Before / After

**Before — AI가 생성한 "동작하지만 규모에서 무너지는" pagination:**

```python
# offset 방식 — page=5000에서 DB가 10만 개 행을 읽고 버림
@app.get("/orders")
def list_orders(page: int = 1, per_page: int = 20):
    offset = (page - 1) * per_page
    return db.query(Order).offset(offset).limit(per_page).all()
```

**After — AI에게 cursor pagination을 명시하고 받은 코드:**

```python
# 프롬프트: "offset 대신 cursor 기반 pagination, limit 상한 100, cursor 불투명 토큰으로 만들어줘"
@app.get("/orders")
def list_orders(cursor: str | None = None, limit: int = Query(default=20, le=100)):
    query = db.query(Order).order_by(Order.created_at.desc(), Order.id.desc())
    if cursor:
        decoded = decode_cursor(cursor)
        query = query.filter(
            (Order.created_at < decoded["created_at"]) |
            ((Order.created_at == decoded["created_at"]) & (Order.id < decoded["id"]))
        )
    items = query.limit(limit + 1).all()
    has_more = len(items) > limit
    return {
        "data": items[:limit],
        "meta": {"has_more": has_more, "next_cursor": encode_cursor(items[limit-1]) if has_more else None}
    }
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| limit 상한 없음 | `?limit=99999` 한 번에 서버 다운 | "limit 최대 100으로 제한해줘" 명시 |
| 깊은 offset 허용 | `offset=100000`에서 응답 수십 초 | "cursor 기반으로 만들어줘" 요청 |
| 항상 total count 계산 | `COUNT(*)` 비용이 본 쿼리보다 큼 | "has_more 불리언으로 대체, total은 선택적" |
| filter/sort/search를 한 파라미터에 | 검증, 최적화 불가 | "sort, filter, q 파라미터를 별도로 분리해줘" |
| cursor 내부 구조 노출 | 클라이언트가 위조 가능 | "cursor는 base64 불투명 토큰으로 만들어줘" |

## AI에게 pagination 관련 질문하는 팁

바이브코딩에서 pagination 프롬프트를 잘 쓰려면 세 가지를 포함하면 됩니다.

1. **방식 선택**: 소규모 정적 데이터는 offset, 피드/대규모는 cursor
2. **상한 명시**: "limit 최대 100, 기본 20"
3. **응답 형태 포함**: "data 배열 + meta.has_more + meta.next_cursor"

예시 프롬프트:
> "주문 목록 API에 cursor 기반 pagination 추가해줘. limit 기본값 20, 최대 100. 응답은 {data: [], meta: {has_more: bool, next_cursor: string | null}} 형태로. cursor는 base64 불투명 토큰, 잘못된 cursor면 400 반환해줘. status, created_at으로 필터링도 추가해줘."

## 운영 체크리스트
- [ ] limit에 상한이 있는가? (예: 최대 100)
- [ ] cursor가 불투명 토큰인가? (클라이언트가 내부 구조를 모름)
- [ ] sort, filter, search 파라미터가 서로 분리되어 있는가?
- [ ] 응답에 next_cursor 또는 has_more가 포함되는가?
- [ ] cursor 디코딩 실패 시 400을 반환하는가?
- [ ] 허용 sort/filter 필드가 명시되어 있고, 그 외에는 400 반환하는가?

## 처음 질문으로 돌아가기

AI가 만든 목록 API가 프로덕션에서 느려졌을 때, "서버가 느린 것"이 아니라 "offset pagination이 10만 번째 페이지에서 DB를 풀 스캔하고 있는 것"이라고 진단할 수 있어야 합니다. 그 판단이 "cursor로 바꿔줘"라는 정확한 프롬프트로 이어집니다.

## 정리

pagination은 성능과 정확성이 만나는 지점입니다. offset은 구현이 쉽지만 규모가 커지면 한계가 뚜렷하고, cursor는 초기 비용이 조금 높지만 대규모 데이터에서 안정적입니다. AI에게 데이터 규모와 성능 요구사항을 함께 전달하면 올바른 선택을 받을 수 있습니다.

다음 글에서는 모든 API가 결국 마주치는 또 하나의 주제, error response 설계를 다룹니다.

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [Stripe API: Pagination](https://stripe.com/docs/api/pagination)
- [GitHub REST API: Using Pagination](https://docs.github.com/en/rest/guides/using-pagination-in-the-rest-api)
- [Slack API: Cursor-based Pagination](https://api.slack.com/docs/pagination)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 API 설계 기초 (1/10): API란 무엇인가?
- 바이브코딩을 위한 API 설계 기초 (2/10): REST 기본
- 바이브코딩을 위한 API 설계 기초 (3/10): 리소스 설계
- 바이브코딩을 위한 API 설계 기초 (4/10): HTTP method와 status code
- 바이브코딩을 위한 API 설계 기초 (5/10): Request와 response schema
- **바이브코딩을 위한 API 설계 기초 (6/10): Pagination과 filtering (현재 글)**
- 바이브코딩을 위한 API 설계 기초 (7/10): Error response 설계
- 바이브코딩을 위한 API 설계 기초 (8/10): OpenAPI와 Swagger
- 바이브코딩을 위한 API 설계 기초 (9/10): API 버전 관리
- 바이브코딩을 위한 API 설계 기초 (10/10): 좋은 API 문서 만들기
<!-- toc:end -->

Tags: 바이브코딩, API설계, Pagination
