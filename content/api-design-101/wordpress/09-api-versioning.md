---
title: "바이브코딩을 위한 API 설계 기초 (9/10): API 버전 관리"
series: api-design-101
episode: 9
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- API설계
- 버전관리
seo_description: "AI가 만든 API를 배포 후에 바꾸려면 버전 관리가 필요합니다. breaking change가 무엇이고 어떻게 관리하는지 바이브코딩 관점에서 정리합니다."
---

# 바이브코딩을 위한 API 설계 기초 (9/10): API 버전 관리

이 글은 바이브코딩을 위한 API 설계 기초 시리즈의 9번째 글입니다.

AI가 만들어준 API를 배포했습니다. 모바일 앱과 프론트엔드가 이 API를 쓰고 있습니다. 그런데 요구사항이 바뀌어서 응답에서 `name` 필드를 제거하고 `full_name`으로 바꿔야 합니다. AI에게 "필드명 바꿔줘"라고 하면 코드는 금방 바뀝니다. 그런데 배포하는 순간 앱이 터집니다. `name` 필드를 기대하던 모바일 앱이 갑자기 null을 받습니다.

이것이 breaking change입니다. 코드를 바꾸는 것은 쉽지만, 이미 클라이언트가 있는 API를 바꾸는 것은 다른 문제입니다. 버전 관리 전략이 없으면 "배포했더니 앱이 터졌다"는 상황이 반복됩니다.

breaking change가 무엇인지 이해하고, URL 버전 관리 원칙을 알면, AI에게 "이 변경이 breaking인지 확인해줘"라고 물을 수 있고, 안전하게 API를 진화시킬 수 있습니다.

> API 버전 관리는 '/v1을 붙이는 일'이 아니라 '깨지는 변경을 언제, 누구에게, 어떻게 전달할 것인가'를 결정하는 정책입니다.

---

## 이 글에서 다룰 문제
- breaking change와 non-breaking change는 어떻게 구분할까요?
- URL versioning과 header versioning은 각각 어떤 장단점이 있을까요?
- 구버전을 폐기(sunset)할 때 어떤 절차를 밟아야 할까요?
- AI가 만든 API를 변경할 때 버전 관리를 어떻게 적용할까요?
- 바이브코딩에서 버전 없이 API를 바꾸면 어떤 문제가 생길까요?

Breaking change: 응답 필드 제거, 필드 이름 변경, 필수 요청 파라미터 추가, 응답 타입 변경, URL 경로 변경.
Non-breaking change: 응답에 새 필드 추가(클라이언트가 unknown 필드 무시 가능), 선택적 파라미터 추가(기본값 있음), 새 엔드포인트 추가.

| 변경 | Breaking? | 이유 |
|------|-----------|------|
| 응답 필드 제거 | 예 | 기존 클라이언트가 해당 필드를 참조 |
| 필드명 변경 | 예 | 제거와 동일한 효과 |
| 필수 파라미터 추가 | 예 | 기존 요청이 400으로 실패 |
| 응답에 새 필드 추가 | 아니오 | 클라이언트가 무시하면 됨 |
| 선택적 파라미터 추가 | 아니오 | 기본값 있으면 기존 요청 그대로 동작 |

## Before / After

**Before — 버전 없이 breaking change를 배포:**

```python
# 변경 전
{"name": "Alice", "email": "alice@example.com"}

# 변경 후 (버전 없이 배포 → 모바일 앱 즉시 장애)
{"full_name": "Alice", "email": "alice@example.com"}
```

**After — AI에게 버전 관리와 함께 변경을 요청한 코드:**

```python
# 프롬프트: "/v1은 기존 그대로 유지, /v2에서만 full_name으로 변경. v1에 deprecated 헤더 추가해줘"
@app.get("/v1/users/{id}")
def get_user_v1(id: int):
    return JSONResponse(
        content={"name": "Alice", "email": "alice@example.com"},  # 기존 유지
        headers={
            "Deprecation": "true",
            "Sunset": "Wed, 31 Jan 2027 23:59:59 GMT",
            "Link": '</v2/users>; rel="successor-version"'
        }
    )

@app.get("/v2/users/{id}")
def get_user_v2(id: int):
    return {"full_name": "Alice", "email": "alice@example.com"}  # 새 구조
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 버전 없이 breaking 배포 | 기존 클라이언트 즉시 장애 | "이 변경이 breaking인지 먼저 확인해줘" AI에게 물어보기 |
| 모든 변경을 breaking으로 처리 | v3, v4가 쌓여 운영 비용 폭증 | non-breaking 변경 목록 이해하고 additive하게 설계 |
| 구버전 폐기 공지 없음 | 종료일 당일에 클라이언트 장애 | Deprecation + Sunset 헤더로 최소 6개월 전 공지 |
| 한 핸들러에 버전 분기 if/else | 코드 복잡도 급증 | "버전별 별도 라우터로 분리해줘" 요청 |
| 동시에 너무 많은 버전 유지 | 유지보수 비용 폭증 | 최대 2개 major 버전 동시 유지 제한 |

## AI에게 버전 관리 관련 질문하는 팁

바이브코딩에서 버전 관리 프롬프트를 잘 쓰려면 세 가지를 포함하면 됩니다.

1. **breaking 여부 확인**: "이 변경이 breaking change인지 확인해줘. 기존 클라이언트에 영향이 있나?"
2. **버전 전략 명시**: "URL versioning으로 /v1, /v2 분리"
3. **폐기 절차 포함**: "v1에 Deprecation, Sunset 헤더 추가해줘"

예시 프롬프트:
> "현재 API에서 응답의 name 필드를 full_name으로 바꿔야 해. 기존 v1 클라이언트는 건드리지 말고, v2를 새로 만들어줘. v1에는 Deprecation: true, Sunset 헤더(6개월 뒤)를 추가해줘. 이 변경 목록 중 어떤 게 breaking change인지도 알려줘."

또한 코드 변경 전에 이렇게 먼저 물을 수 있습니다:
> "다음 API 변경 사항 목록에서 breaking change와 non-breaking change를 분류해줘: 1) 응답에 age 필드 추가, 2) name 필드 제거, 3) status enum에 pending 값 추가"

## 운영 체크리스트
- [ ] API 변경 전에 breaking/non-breaking 여부를 판단했는가?
- [ ] breaking change는 새 major 버전 URL로 분리했는가?
- [ ] 구버전에 Deprecation, Sunset, Link 헤더가 설정되어 있는가?
- [ ] 클라이언트별 버전 사용량을 추적하고 있는가?
- [ ] 동시에 활성인 major 버전 수에 상한(예: 2)이 있는가?
- [ ] non-breaking 변경(새 필드 추가)은 현재 버전에 바로 반영했는가?

## 처음 질문으로 돌아가기

AI에게 "이 필드명 바꿔줘"라고 했을 때 코드는 금방 바뀝니다. 그런데 배포 전에 "이 변경이 기존 클라이언트를 깨뜨리는가?"라고 먼저 묻는 습관이 중요합니다. AI에게도 같은 질문을 할 수 있습니다. "이 변경이 breaking change인지 확인해줘"는 배포 사고를 막는 가장 간단한 프롬프트입니다.

## 정리

버전 관리는 계약과 변경을 함께 다루는 기술입니다. AI와 바이브코딩할 때, 변경 전에 breaking 여부를 확인하고, 필요하면 새 버전을 만들고, Deprecation 헤더로 충분한 유예 기간을 주면 배포 사고를 예방할 수 있습니다.

다음 글에서는 이 모든 약속을 사람에게 읽히게 만드는 API 문서 작성 원칙을 다룹니다.

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [Stripe API Versioning](https://stripe.com/docs/upgrades)
- [GitHub REST API: API Versions](https://docs.github.com/en/rest/overview/api-versions)
- [Sunset HTTP Header (RFC 8594)](https://www.rfc-editor.org/rfc/rfc8594)
- [oasdiff — OpenAPI breaking change detection](https://github.com/Tufin/oasdiff)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 API 설계 기초 (1/10): API란 무엇인가?
- 바이브코딩을 위한 API 설계 기초 (2/10): REST 기본
- 바이브코딩을 위한 API 설계 기초 (3/10): 리소스 설계
- 바이브코딩을 위한 API 설계 기초 (4/10): HTTP method와 status code
- 바이브코딩을 위한 API 설계 기초 (5/10): Request와 response schema
- 바이브코딩을 위한 API 설계 기초 (6/10): Pagination과 filtering
- 바이브코딩을 위한 API 설계 기초 (7/10): Error response 설계
- 바이브코딩을 위한 API 설계 기초 (8/10): OpenAPI와 Swagger
- **바이브코딩을 위한 API 설계 기초 (9/10): API 버전 관리 (현재 글)**
- 바이브코딩을 위한 API 설계 기초 (10/10): 좋은 API 문서 만들기
<!-- toc:end -->

Tags: 바이브코딩, API설계, 버전관리
