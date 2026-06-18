---
title: "바이브코딩을 위한 API 설계 기초 (8/10): OpenAPI와 Swagger"
series: api-design-101
episode: 8
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- API설계
- OpenAPI
seo_description: "AI가 만든 API를 문서로 자동화하고, 코드와 문서가 어긋나지 않게 하는 OpenAPI와 Swagger를 바이브코딩 관점에서 정리합니다."
---

# 바이브코딩을 위한 API 설계 기초 (8/10): OpenAPI와 Swagger

이 글은 바이브코딩을 위한 API 설계 기초 시리즈의 8번째 글입니다.

AI가 API 코드를 만들어줬습니다. 잘 동작합니다. 그런데 프론트엔드 팀에서 "이 API 문서 어디 있나요?"라는 질문이 옵니다. 직접 Postman으로 찍어가며 확인하라고 할 수는 없습니다. Notion에 직접 문서를 쓰기 시작했는데, 코드를 한 번 수정하고 나니 문서가 이미 틀렸습니다. 코드와 문서를 따로 관리하면 둘 중 하나는 항상 거짓입니다.

OpenAPI Specification(OAS)은 이 문제를 해결합니다. FastAPI 같은 프레임워크는 코드에서 OpenAPI 명세를 자동으로 생성하고, 이것이 Swagger UI를 통해 인터랙티브 문서가 됩니다. 코드가 곧 문서입니다. 코드를 수정하면 문서도 자동으로 갱신됩니다.

더 나아가, OpenAPI 명세에서 TypeScript 클라이언트 코드를 자동 생성하거나, Prism으로 mock 서버를 띄울 수 있습니다. AI와 협업할 때 "이 OpenAPI spec을 기반으로 클라이언트 코드 만들어줘"라고 하면 정확한 타입의 SDK를 받을 수 있습니다.

> OpenAPI spec은 문서 자동 생성기가 아니라, 서버·클라이언트·테스트·SDK가 모두 같은 계약을 바라보게 하는 단일 진실 원본입니다.

---

## 이 글에서 다룰 문제
- OpenAPI 3 문서는 어떤 구조로 이루어질까요?
- code-first와 schema-first는 어떤 차이가 있을까요?
- AI가 만든 코드에서 OpenAPI를 자동으로 얻으려면 어떻게 해야 할까요?
- 바이브코딩에서 문서 없이 API를 배포하면 어떤 문제가 생길까요?
- OpenAPI spec을 활용해 AI와 더 효율적으로 협업하는 방법은 무엇일까요?

OpenAPI는 API의 구조를 YAML/JSON으로 정의합니다. paths에는 엔드포인트별 파라미터와 응답을, components에는 재사용 가능한 schema를 정의합니다. 이 파일 하나에서 문서, SDK, mock, 검증이 모두 파생됩니다.

## Before / After

**Before — AI가 생성한 "코드만 있고 문서는 없는" API:**

```python
@app.post("/users")
def create_user(body: dict):  # 타입도, 문서도 없음
    return {"id": 1, **body}
# 프론트엔드: "어떤 필드를 보내야 하나요?" → Postman으로 직접 확인
```

**After — AI에게 Pydantic + FastAPI로 자동 문서화를 요청한 코드:**

```python
# 프롬프트: "FastAPI + Pydantic으로 만들어줘. 입출력 schema 분리, 자동 OpenAPI 문서 생성되게"
from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime

app = FastAPI(title="My API", version="1.0")

class UserCreate(BaseModel):          # 입력 schema — 자동으로 문서화
    username: str = Field(min_length=3, max_length=32)
    email: str

class UserResponse(BaseModel):         # 출력 schema — 자동으로 문서화
    id: int
    username: str
    created_at: datetime

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(body: UserCreate):
    """사용자를 생성합니다."""  # docstring도 문서에 반영
    ...
# /docs 접속 → Swagger UI 자동 생성, /openapi.json → spec 자동 생성
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 코드와 문서를 따로 관리 | 둘 중 하나는 항상 거짓 | "code-first로 OpenAPI 자동 생성해줘" |
| 예제(example) 없음 | Swagger UI에서 뭘 보낼지 모름 | "모든 schema 필드에 example 추가해줘" |
| 4xx/5xx 응답 미문서화 | 실패 경로를 알 수 없음 | "에러 응답도 responses에 포함해줘" |
| 인증 정보 없음 | Swagger UI에서 인증 API 테스트 불가 | "securitySchemes에 Bearer auth 추가해줘" |
| 공개/내부 엔드포인트 혼용 | 내부 정보가 공개 spec에 노출 | "내부 엔드포인트는 공개 spec에서 제외해줘" |

## AI에게 OpenAPI 관련 질문하는 팁

바이브코딩에서 OpenAPI 프롬프트를 잘 쓰려면 세 가지를 포함하면 됩니다.

1. **프레임워크 명시**: "FastAPI + Pydantic으로" (자동 생성 지원 프레임워크)
2. **예제 포함 요청**: "각 schema에 example 값 추가해줘"
3. **에러 응답 포함**: "4xx, 5xx 응답도 responses에 정의해줘"

예시 프롬프트:
> "주문 API를 FastAPI + Pydantic으로 만들어줘. 입출력 schema 분리, 모든 필드에 example 포함, GET/POST/DELETE 각각의 성공/실패 응답을 responses에 정의해줘. Bearer 토큰 인증도 securitySchemes에 추가해줘. /docs에서 바로 테스트 가능하게."

그리고 AI에게 이렇게도 물을 수 있습니다:
> "이 FastAPI 코드에서 생성된 openapi.json을 기반으로 TypeScript fetch 클라이언트 코드 만들어줘."

## 운영 체크리스트
- [ ] /docs 또는 /openapi.json이 자동 생성되는가?
- [ ] 모든 엔드포인트에 example이 있는가?
- [ ] 4xx와 5xx가 responses에 정의되어 있는가?
- [ ] securitySchemes가 정의되어 있는가?
- [ ] 코드를 바꾸면 spec도 자동으로 갱신되는가? (code-first)
- [ ] 공개 spec에 내부 엔드포인트가 포함되지 않는가?

## 처음 질문으로 돌아가기

AI가 만든 API 코드에 문서가 없어서 프론트엔드 팀이 Postman으로 찍어가며 확인하는 상황이 반복된다면, "이 API를 FastAPI + Pydantic으로 바꾸고 OpenAPI 자동 생성되게 해줘"라는 한 마디가 상황을 바꿉니다. 코드가 spec이 되고, spec이 문서가 되고, 문서에서 클라이언트 코드가 나옵니다.

## 정리

OpenAPI는 API의 문서이자 계약이자 코드 생성 입력입니다. AI와 함께 바이브코딩할 때, 자동 문서화가 되는 프레임워크를 선택하고 예제와 에러 응답을 포함하면, 문서와 코드가 항상 동기화되는 협업 환경을 만들 수 있습니다.

다음 글에서는 이 계약을 안전하게 바꾸는 기술, API 버전 관리를 다룹니다.

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [FastAPI: Automatic docs](https://fastapi.tiangolo.com/features/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
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
- **바이브코딩을 위한 API 설계 기초 (8/10): OpenAPI와 Swagger (현재 글)**
- 바이브코딩을 위한 API 설계 기초 (9/10): API 버전 관리
- 바이브코딩을 위한 API 설계 기초 (10/10): 좋은 API 문서 만들기
<!-- toc:end -->

Tags: 바이브코딩, API설계, OpenAPI
