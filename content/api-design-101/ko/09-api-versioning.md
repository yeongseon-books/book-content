---
title: "API Design 101 (9/10): Versioning"
series: api-design-101
episode: 9
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
  - Versioning
  - Compatibility
  - Deprecation
  - Backend
last_reviewed: '2026-05-15'
seo_description: API versioning의 기준, 호환성 정책, sunset 절차를 실무적으로 설명합니다.
---

# API Design 101 (9/10): Versioning

API를 오래 운영하다 보면 진짜 어려운 일은 바꾸는 것 자체보다 바꿀 때 신뢰를 잃지 않는 일입니다. 필드 하나를 추가하는 순간에는 사소해 보여도, 어떤 팀은 즉시 배포하고 어떤 팀은 반년 뒤에야 따라오기 때문에 호환성 규칙이 없는 변화는 곧 장애 공지가 됩니다.

이 글은 API Design 101 시리즈의 아홉 번째 글입니다.

여기서는 versioning을 URL 문법이 아니라 변경 관리 절차로 다룹니다. 무엇이 breaking인지 먼저 정의하고, 그다음 URL·header·deprecation·sunset을 어떤 조합으로 운영할지 차례로 정리합니다.

![API Design 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/09/09-01-concept-at-a-glance.ko.png)
*API 변경이 호환성 판단 → 버전 결정 → deprecation 공지 → sunset 순서로 진행되는 흐름*

## 먼저 던지는 질문

- breaking change와 non-breaking change는 어떻게 구분할까요?
- URL versioning과 header versioning은 각각 어떤 장단점이 있을까요?
- semver, calver 같은 호환성 정책은 어떻게 읽어야 할까요?

## Breaking vs Non-breaking — 먼저 정의해야 운영할 수 있다

versioning에서 가장 중요한 첫 단계는 "무엇이 breaking인가"를 팀 전체가 동일하게 판단하는 것입니다.

### Breaking change 목록

| 변경 | 이유 |
|---|---|
| 응답 필드 제거 | 클라이언트가 해당 필드를 참조 중이면 깨짐 |
| 응답 필드 이름 변경 | 제거와 동일한 효과 |
| 필수 요청 파라미터 추가 | 기존 요청이 400으로 실패 |
| 기존 enum 값 제거 | 해당 값을 보내던 클라이언트가 400 |
| 응답 필드 타입 변경 (string → integer) | 파싱 실패 |
| URL 경로 변경 | 기존 요청이 404 |
| 에러 코드 의미 변경 | 분기 로직이 오동작 |
| 인증 방식 변경 | 기존 토큰/키가 동작하지 않음 |

### Non-breaking change 목록

| 변경 | 조건 |
|---|---|
| 응답에 새 필드 추가 | 클라이언트가 unknown field를 무시할 수 있어야 함 |
| 선택적 요청 파라미터 추가 | 기본값이 있어야 함 |
| 새 endpoint 추가 | 기존 endpoint에 영향 없음 |
| 새 enum 값 추가 | 클라이언트가 unknown value를 graceful하게 처리해야 함 |
| 에러 메시지 문구 변경 | code는 유지, detail만 변경 |

핵심 원칙: **클라이언트가 코드를 수정하지 않고도 계속 동작할 수 있으면 non-breaking**입니다.

### 호환성 정책 문서화

```markdown
## 호환성 정책

### Non-breaking (현재 버전에 바로 반영)
- 응답에 새 JSON 필드 추가
- 선택적 query parameter 추가
- 새 endpoint 추가
- enum 값 추가 (클라이언트는 unknown value를 무시해야 함)

### Breaking (새 major 버전 필요)
- 기존 필드 제거 또는 이름 변경
- 필수 파라미터 추가
- 응답 타입 변경
- URL 경로 변경

### Deprecation timeline
- 최소 6개월 전 공지
- Deprecation + Sunset header 설정
- sunset 30일 전 410 시뮬레이션
```

이 문서가 존재해야 PR 리뷰에서 "이 변경은 breaking인가?"를 객관적으로 판단할 수 있습니다.

## Versioning 전략 비교

### URL 버전 관리

```http
GET /v1/users/42
GET /v2/users/42
```

| 장점 | 단점 |
|---|---|
| 직관적 — 로그, 캐시, 라우팅에서 버전이 즉시 보임 | URL이 오염됨 — 리소스 식별자가 아닌 메타 정보가 경로에 포함 |
| 브라우저에서 바로 테스트 가능 | 버전별 라우팅 코드 중복 가능성 |
| CDN/프록시 캐시 분리가 자연스러움 | hypermedia 원칙 위반 (같은 리소스, 다른 URL) |

**채택 사례**: GitHub REST API, Google Cloud API, Twitter API v2

### 헤더 버전 관리

```http
GET /users/42
Accept: application/vnd.myapi.v2+json
# 또는
X-API-Version: 2
```

| 장점 | 단점 |
|---|---|
| URL이 깨끗 — 리소스 식별이 순수 | curl/브라우저에서 테스트하려면 header를 직접 설정해야 함 |
| content negotiation 표준과 일관 | CDN 캐시 분리에 `Vary` header 설정 필요 |
| 같은 리소스에 대한 여러 표현으로 해석 가능 | 디버깅 시 버전이 즉시 안 보임 |

**채택 사례**: Stripe (`Stripe-Version` header), GitHub (`X-GitHub-Api-Version`)

### 쿼리 파라미터 버전 관리

```http
GET /users/42?api_version=2
```

URL path보다는 덜 침습적이지만, 캐시 키 관리와 라우팅이 복잡해집니다. 실무에서는 비교적 드뭅니다.

### 날짜 기반 versioning (Stripe 방식)

```http
Stripe-Version: 2024-04-10
```

Stripe는 날짜를 버전으로 사용합니다. 새 계정은 가입 시점의 최신 버전이 기본값이 되고, 기존 계정은 명시적으로 업그레이드하기 전까지 이전 버전이 유지됩니다. 내부적으로는 변경 사항을 "version change" 단위로 기록하고, 요청의 버전에 따라 동작을 분기합니다.

이 방식의 장점은 breaking change마다 major 번호가 올라가는 것이 아니라, 시간 순서로 정렬된 변경 이력이 자연스럽게 만들어진다는 것입니다.

## Deprecation과 Sunset — 버전 종료의 절차

버전을 만드는 것보다 없애는 것이 더 어렵습니다. 클라이언트에게 충분한 시간과 정보를 주지 않으면 sunset 당일이 장애 당일이 됩니다.

### 표준 HTTP header

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Wed, 31 Jan 2027 23:59:59 GMT
Link: </v2/users>; rel="successor-version"
```

| Header | 역할 |
|---|---|
| `Deprecation` | "이 버전은 더 이상 권장되지 않음"을 알림 |
| `Sunset` (RFC 8594) | 공식 종료 날짜를 명시 |
| `Link: rel="successor-version"` | 대체 버전의 위치를 안내 |

### Sunset 절차 (5단계)

| 단계 | 시점 | 행동 |
|---|---|---|
| 1. 새 버전 배포 | D-day | v2 배포 + v1에 `Deprecation: true` 시작 |
| 2. 사용량 관찰 | D+1~30 | v1 호출 클라이언트 식별, 연락 |
| 3. Sunset 날짜 공지 | D+30 | `Sunset` header + 이메일 + 문서 공지 (최소 6개월 유예) |
| 4. 시뮬레이션 | Sunset-30일 | 일부 시간대에 410 또는 warning 반환 |
| 5. Sunset 실행 | Sunset일 | 410 Gone 또는 308 Permanent Redirect |

### 구현 예시

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()

SUNSET_DATE = "Wed, 31 Jan 2027 23:59:59 GMT"
SUNSET_DATETIME = datetime(2027, 1, 31, 23, 59, 59)

@app.get("/v1/users/{uid}")
def v1_get_user(uid: int):
    now = datetime.utcnow()

    # Sunset 이후면 410 반환
    if now > SUNSET_DATETIME:
        return JSONResponse(
            status_code=410,
            content={"code": "version.sunset", "detail": "v1은 종료되었습니다. /v2를 사용하세요."},
        )

    # 정상 응답 + deprecation header
    return JSONResponse(
        content={"id": uid, "name": "Y"},
        headers={
            "Deprecation": "true",
            "Sunset": SUNSET_DATE,
            "Link": '</v2/users>; rel="successor-version"',
        },
    )
```

## Semver 대 Calver

| 방식 | 형식 | 의미 |
|---|---|---|
| Semver | `MAJOR.MINOR.PATCH` | MAJOR = breaking, MINOR = feature, PATCH = fix |
| Calver | `2024-04-10` | 날짜가 곧 버전. Stripe, Ubuntu 등 사용 |

API versioning에서 semver를 쓸 때는 보통 MAJOR만 외부에 노출합니다(`/v1/`, `/v2/`). MINOR와 PATCH는 non-breaking이므로 같은 major 안에서 처리됩니다.

Calver는 "변경의 빈도가 높고, major 단위로 끊기보다 연속적인 변경 이력을 관리하는 것이 자연스러운" 환경에서 유리합니다.

## 자주 하는 실수 다섯 가지

| # | 실수 | 결과 | 해결 |
|---|---|---|---|
| 1 | 버전 없이 breaking 배포 | 클라이언트 장애, 원인 추적 불가 | 호환성 정책 + 버전 채널 도입 |
| 2 | 모든 변경을 breaking으로 처리 | v3, v4가 빠르게 늘어 운영 비용 폭증 | non-breaking 정의를 명확히 |
| 3 | 예고 없이 sunset | 클라이언트 신뢰 상실 | 최소 6개월 유예 + header + 이메일 |
| 4 | 모든 버전을 영원히 유지 | 코드가 지층처럼 쌓여 유지보수 불가 | 동시 활성 버전 수 상한(예: 2) |
| 5 | 한 handler에 버전 분기 if/else | 코드 복잡도 급증 | 버전별 라우터 또는 미들웨어 분리 |

## 시니어 엔지니어는 이렇게 판단합니다

- 호환성 정책 문서를 먼저 만들고, 모든 PR에서 "이 변경은 breaking인가?"를 객관적으로 판단합니다.
- 대부분의 변경은 additive하게 처리합니다. 새 major 버전은 정말 필요할 때만 만듭니다.
- 표준 header(`Deprecation`, `Sunset`, `Link`)를 사용해 기계도 읽을 수 있는 공지를 합니다.
- 여러 버전을 동시에 유지하는 내부 비용(코드 중복, 테스트 배수, 인프라)을 숫자로 계산합니다.
- 실제 사용량이 충분히 줄어든 뒤에만 sunset합니다. 날짜만 정하고 트래픽을 확인하지 않으면 실패합니다.
- CI에서 breaking change를 자동 감지합니다(`oasdiff breaking` 등).

## 검증 포인트와 실패 신호

- **Expected output:** 새 버전을 배포한 뒤에는 이전 버전 응답에 `Deprecation`, `Sunset`, `Link` header가 꾸준히 실려야 합니다.
- **First check:** 최근 변경 다섯 개를 breaking / non-breaking으로 팀원마다 다르게 분류한다면 호환성 정책 문서부터 다시 써야 합니다.
- **Failure mode:** 사용량 관찰 없이 sunset 날짜만 고지하면, 종료 당일에 남아 있던 클라이언트가 한꺼번에 장애를 냅니다.

## 체크리스트

- [ ] 호환성 정책(breaking/non-breaking 정의)이 문서화되어 있는가?
- [ ] 버전 채널(URL 또는 header)이 전체 API에서 일관적인가?
- [ ] deprecated 버전에 `Deprecation`, `Sunset` header가 설정되어 있는가?
- [ ] 클라이언트별 버전 사용량을 추적하는가?
- [ ] 동시에 활성인 major 버전 수에 상한(예: 2)이 있는가?
- [ ] CI에서 breaking change를 자동 감지하는가?

## 연습 문제

1. 최근 API 변경 다섯 개를 골라 breaking / non-breaking으로 분류하고, 그 판단 근거를 한 줄씩 적어 보세요.
2. 현재 API에 `Deprecation`과 `Sunset` header를 추가하는 미들웨어를 작성해 보세요.
3. URL versioning과 header versioning 중 자신의 프로젝트에 더 적합한 것을 선택하고, trade-off를 세 가지 이상 정리해 보세요.

## 정리와 다음 글

versioning은 계약과 변경을 함께 다루는 기술입니다. 무엇이 breaking인지 정의하고, 적절한 채널로 버전을 분리하고, 충분한 유예와 관찰을 거쳐 sunset하는 것이 전체 절차입니다. 마지막 글에서는 이 모든 약속을 사람에게 읽히게 만드는 API 문서 작성 원칙을 다룹니다.

## 팀 운영 관점의 보강: 설계 결정이 배포 후 어떻게 드러나는가

문서에서 맞아 보이던 선택이 운영에서 실패하는 이유는 대부분 관측 지점이 없기 때문입니다. 그래서 설계 단계에서 아래 세 가지를 같이 준비해야 합니다.

### 1) 요청 식별자 전파

```http
X-Request-Id: req_01JY2J5YQ6KZ5K6J2M2X5A7N8V
Traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

게이트웨이, API 서버, 비동기 워커가 같은 식별자를 공유하면 장애 분석 시간이 급격히 줄어듭니다. 한 서비스에서만 생성하는 방식보다 ingress에서 시작해 하위 호출로 전달하는 방식이 안정적입니다.

### 2) 상태 코드별 SLI 분해

- 성공률 SLI는 `2xx / 전체`로 단순 계산하지 않습니다.
- 사용자 실수로 발생한 `4xx`와 시스템 결함인 `5xx`를 분리합니다.
- `429` 비율은 과부하 지표이므로 별도 대시보드로 관리합니다.
- `p95` 지연 시간은 endpoint 단위로 분리해 봅니다.

이 분해가 없으면 "에러율 2%" 같은 숫자가 문제를 가립니다. 실제로는 인증 만료 폭증일 수도 있고, 특정 엔드포인트 DB 락일 수도 있습니다.

### 3) 롤아웃 가드레일

```yaml
rollout:
  strategy: canary
  steps:
    - percent: 5
      duration: 10m
    - percent: 25
      duration: 20m
    - percent: 100
  abort_if:
    error_rate_5xx: "> 1.0%"
    p95_latency_ms: "> 450"
    rate_limit_429: "> 3.0%"
```

버전 변경이나 스키마 확장은 배포 전략 없이는 안전하게 실행되지 않습니다. 특히 클라이언트 수가 많은 API는 한 번의 전면 배포보다 단계적 확대와 자동 중단 조건이 필수입니다.

### 실무 판단 기준

- 설계 변경 제안서에 "호환성 영향" 항목이 없으면 검토를 보류합니다.
- 신규 필드는 nullable로 추가하고, 필수화는 다음 메이저 버전에서 수행합니다.
- 응답 키 이름 변경은 alias 유지 기간을 명시합니다.
- 폐기 예정 항목은 최소 2개 릴리스 전부터 경고 헤더를 노출합니다.

이 원칙을 문서에 포함해 두면, 구현자와 소비자가 같은 시간표를 공유하게 됩니다. 그 결과 API 변경이 이벤트가 아니라 일상적인 운영 절차로 전환됩니다.

## 처음 질문으로 돌아가기

- **breaking change와 non-breaking change는 어떻게 구분할까요?**
  - "클라이언트가 코드를 수정하지 않고도 계속 동작할 수 있는가"가 기준입니다. 응답 필드 제거, 필수 파라미터 추가, 타입 변경은 breaking이고, 새 필드·새 endpoint·선택적 파라미터 추가는 non-breaking입니다. 팀 전체가 동일하게 판단할 수 있도록 호환성 정책 문서를 만들어야 합니다.
- **URL versioning과 header versioning은 각각 어떤 장단점이 있을까요?**
  - URL(`/v1/`)은 직관적이고 캐시·로그 분리가 쉽지만 URL이 오염됩니다. Header는 URL이 깨끗하고 content negotiation과 일관되지만 디버깅이 어렵고 CDN 설정이 추가됩니다. 외부 공개 API는 URL, 내부 API나 빈번한 변경이 필요한 경우는 header가 많이 쓰입니다.
- **semver, calver 같은 호환성 정책은 어떻게 읽어야 할까요?**
  - Semver의 MAJOR는 breaking, MINOR는 기능 추가, PATCH는 수정입니다. API에서는 보통 MAJOR만 외부에 노출합니다. Calver는 날짜가 버전이며, Stripe처럼 변경 빈도가 높고 연속적 이력 관리가 필요한 환경에서 유리합니다.

<!-- toc:begin -->
## 시리즈 목차

- [API Design 101 (1/10): API란 무엇인가?](./01-what-is-an-api.md)
- [API Design 101 (2/10): REST 기본](./02-rest-basics.md)
- [API Design 101 (3/10): 리소스 설계](./03-resource-design.md)
- [API Design 101 (4/10): HTTP method와 status code](./04-http-methods-and-status.md)
- [API Design 101 (5/10): Request와 response schema](./05-request-and-response-schema.md)
- [API Design 101 (6/10): Pagination과 filtering](./06-pagination-and-filtering.md)
- [API Design 101 (7/10): Error response 설계](./07-error-response-design.md)
- [API Design 101 (8/10): OpenAPI와 Swagger](./08-openapi-and-swagger.md)
- **Versioning (현재 글)**
- 좋은 API 문서 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [Stripe API Versioning](https://stripe.com/docs/upgrades)
- [GitHub REST API: API Versions](https://docs.github.com/en/rest/overview/api-versions)
- [Sunset HTTP Header (RFC 8594)](https://www.rfc-editor.org/rfc/rfc8594)
- [Deprecation HTTP Header](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-deprecation-header)
- [oasdiff — OpenAPI breaking change detection](https://github.com/Tufin/oasdiff)

Tags: Computer Science, APIDesign, Versioning, Compatibility, Deprecation, Backend
