---
title: "API Design 101 (8/10): OpenAPI와 Swagger"
series: api-design-101
episode: 8
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
  - OpenAPI
  - Swagger
  - Documentation
  - Backend
last_reviewed: '2026-05-15'
seo_description: OpenAPI 3와 Swagger UI로 계약을 문서, 검증, SDK로 연결하는 방법을 설명합니다.
---

# API Design 101 (8/10): OpenAPI와 Swagger

문서가 코드보다 늦게 갱신되기 시작하는 순간, 팀은 문서를 참고하지 않고 직접 호출해 보는 습관을 들이게 됩니다. 그 단계까지 가면 문서는 설명서가 아니라 의심 대상이 되고, SDK와 테스트도 같은 방향으로 어긋납니다.

이 글은 API Design 101 시리즈의 여덟 번째 글입니다.

여기서는 OpenAPI와 Swagger를 문서 도구가 아니라 계약 자동화 체계로 봅니다. 하나의 spec이 validation, 예제, SDK, mock server까지 연결되어야만 단일 진실 원본이라는 말이 실제 운영 습관으로 이어집니다.

## 먼저 던지는 질문

- OpenAPI 3 문서는 어떤 구조로 이루어질까요?
- Swagger UI와 Redoc은 각각 어떤 역할을 할까요?
- code-first와 schema-first는 어떤 차이가 있을까요?

## 큰 그림

![API Design 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/08/08-01-concept-at-a-glance.ko.png)

*API Design 101 8장 흐름 개요*

이 그림에서는 OpenAPI와 Swagger를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> OpenAPI와 Swagger의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

잘 관리된 spec 파일 하나만 있으면 문서, validation, client code, mock server까지 한 번에 연결할 수 있습니다. 반대로 사람이 손으로 쓰는 문서는 코드와 반드시 어긋납니다. 자동화가 필요한 이유가 여기에 있습니다.

> 하나의 단일 진실 원본을 유지해야 합니다.

## 한눈에 보는 개념

핵심은 spec 파일을 부차 산출물이 아니라 중심 계약으로 다루는 데 있습니다. 그래야 PR에서 바뀐 요청 필드 하나가 문서와 클라이언트 코드까지 같은 순간에 반영됩니다.

## 핵심 용어

- **OpenAPI**: API 명세를 위한 표준입니다. 예전 Swagger spec의 후속 이름입니다.
- **Swagger UI**: spec을 클릭 가능한 문서로 렌더링합니다.
- **Redoc**: 더 읽기 편한 문서 중심 렌더러입니다.
- **Code-first**: 코드나 decorator에서 spec을 생성하는 방식입니다.
- **Schema-first**: spec을 먼저 작성하고 코드나 SDK를 생성하는 방식입니다.

## Before / After

**Before (손으로 쓴 문서)**

```text
README.md "GET /users/{id} returns user. id is integer."
```

**After (OpenAPI 일부)**

```yaml
paths:
  /users/{id}:
    get:
      parameters:
        - name: id
          in: path
          required: true
          schema: {type: integer}
      responses:
        '200':
          description: User
          content:
            application/json:
              schema: {$ref: '#/components/schemas/User'}
```

## 실습: OpenAPI를 쓰는 다섯 단계

### Step 1 — Minimal spec

```yaml
# openapi.yaml
openapi: 3.0.0
info: {title: Demo API, version: '1.0'}
paths:
  /health:
    get:
      responses:
        '200': {description: OK}
```

Swagger UI에 열기만 해도 바로 호출해 볼 수 있는 문서가 생깁니다.

### Step 2 — components / schemas

```yaml
components:
  schemas:
    User:
      type: object
      required: [id, name]
      properties:
        id: {type: integer}
        name: {type: string}
```

반복되는 schema는 `$ref`로 재사용해야 유지보수가 쉬워집니다.

### Step 3 — Code-first (FastAPI)

```python
# 3_codefirst.py
from fastapi import FastAPI
from pydantic import BaseModel

class User(BaseModel):
    id: int; name: str

app = FastAPI()
@app.get("/users/{uid}")
def user(uid: int) -> User: return User(id=uid, name="Y")
# /docs and /openapi.json are generated automatically
```

FastAPI처럼 code-first를 잘 지원하는 프레임워크에서는 spec drift를 줄이기 쉽습니다.

### Step 4 — Swagger UI / Redoc

```http
GET /docs        # Swagger UI (try it)
GET /redoc       # Redoc (read it)
GET /openapi.json
```

세 endpoint는 하나의 spec을 서로 다른 얼굴로 보여 줍니다.

### Step 5 — Generate clients

```bash
# 5_gen.sh
openapi-generator-cli generate \
  -i openapi.json -g python -o ./client
```

하나의 spec에서 여러 언어 SDK를 생성할 수 있습니다.

## 이 코드에서 봐야 할 점

- spec이 코드와 함께 자랍니다.
- 같은 schema가 validation, 문서, SDK 생성에 동시에 쓰입니다.
- 사람이 손으로 관리하는 중복 문서가 줄어듭니다.

## 자주 하는 실수 다섯 가지

1. **spec과 코드가 따로 놉니다.** 결국 반드시 어긋납니다.
2. **예제가 없습니다.** 사용자가 무엇을 보내야 할지 감을 못 잡습니다.
3. **에러 응답이 빠져 있습니다.** 200만 문서화되고 4xx, 5xx는 비밀이 됩니다.
4. **spec 버전 관리가 없습니다.** 변경 이력을 추적하기 어렵습니다.
5. **공개 spec에 내부 정보가 섞입니다.** 내부 endpoint나 필드가 그대로 노출됩니다.

## 실무에서는 이렇게 드러납니다

GitHub는 `api.github.com/openapi`로 OpenAPI spec을 공개합니다. 내부 시스템에서는 CI에서 코드 변경과 함께 spec 변경도 검증하면 drift가 크게 줄어듭니다. FastAPI와 NestJS는 spec export를 기본적으로 잘 지원하는 편입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- code-first와 schema-first 중 하나만 분명히 선택합니다.
- spec 파일을 git에 커밋하고 PR diff로 리뷰합니다.
- 예제를 반드시 채웁니다. 사용자는 예제부터 복사합니다.
- 200만이 아니라 4xx, 5xx도 spec에 넣습니다.
- 공개용 spec과 내부용 spec을 분리합니다.

## 검증 포인트와 실패 신호

- **Expected output:** `/openapi.json`과 `/docs`가 같은 endpoint, 같은 schema, 같은 예제를 보여 줘야 하며 CI에서도 그 동기화가 깨지지 않아야 합니다.
- **First check:** 코드 리뷰 없이 spec 파일만 수동 수정되거나, 반대로 코드만 바뀌고 spec diff가 비어 있다면 drift가 시작된 것입니다.
- **Failure mode:** 성공 응답만 문서화하고 4xx/5xx를 비워 두면, 사용자는 try-it 화면을 보고도 실제 실패 경로를 재현하지 못합니다.

## 체크리스트

- [ ] spec이 코드와 동기화되는가? CI에서 확인하는가?
- [ ] 모든 endpoint에 예제가 있는가?
- [ ] 4xx와 5xx가 spec에 정의되어 있는가?
- [ ] `components/schemas`를 `$ref`로 재사용하는가?
- [ ] 공개 spec과 내부 spec이 분리되어 있는가?

## 연습 문제

1. 가장 복잡한 endpoint 하나를 OpenAPI로 표현해 보세요.
2. Step 3 FastAPI 예제에 `POST /users`를 추가해 보세요.
3. spec 변경이 PR 리뷰 일부가 되도록 워크플로를 설계해 보세요.

## 정리와 다음 글

OpenAPI는 API의 프로토콜이자 문서이자 코드 생성 입력입니다. 다음 글에서는 이 계약을 안전하게 바꾸는 기술, versioning을 다룹니다.

## 처음 질문으로 돌아가기

- **OpenAPI 3 문서는 어떤 구조로 이루어질까요?**
  - 본문의 기준은 OpenAPI와 Swagger를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Swagger UI와 Redoc은 각각 어떤 역할을 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **code-first와 schema-first는 어떤 차이가 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [API Design 101 (1/10): API란 무엇인가?](./01-what-is-an-api.md)
- [API Design 101 (2/10): REST 기본](./02-rest-basics.md)
- [API Design 101 (3/10): 리소스 설계](./03-resource-design.md)
- [API Design 101 (4/10): HTTP method와 status code](./04-http-methods-and-status.md)
- [API Design 101 (5/10): Request와 response schema](./05-request-and-response-schema.md)
- [API Design 101 (6/10): Pagination과 filtering](./06-pagination-and-filtering.md)
- [API Design 101 (7/10): Error response 설계](./07-error-response-design.md)
- **OpenAPI와 Swagger (현재 글)**
- Versioning (예정)
- 좋은 API 문서 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Redoc](https://redocly.com/redoc/)
- [FastAPI: Automatic docs](https://fastapi.tiangolo.com/features/)

Tags: Computer Science, APIDesign, OpenAPI, Swagger, Documentation, Backend
