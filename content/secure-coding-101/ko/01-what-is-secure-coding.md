---
series: secure-coding-101
episode: 1
title: "Secure Coding 101 (1/10): Secure Coding이란 무엇인가?"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - SecureCoding
  - Security
  - OWASP
  - DevSecOps
  - AppSec
seo_description: Secure Coding의 정의, 위협 모델, OWASP Top 10, 그리고 안전한 개발 습관의 출발점
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (1/10): Secure Coding이란 무엇인가?

기능이 동작하는 것과 공격을 버티는 것은 다른 문제입니다. 로그인은 되는데 계정 탈취에 약할 수 있고, 파일 업로드는 되는데 경로 조작에 무너질 수 있습니다. 보안 사고 대부분은 낯선 암호학 이론보다 입력 검증 누락, 비밀값 노출, 권한 확인 누락처럼 익숙한 개발 실수에서 시작합니다.

이 글은 Secure Coding 101 시리즈의 첫 번째 글입니다.

여기서는 secure coding을 기능 개발 뒤에 덧칠하는 작업이 아니라, 입력 경계와 권한, 저장, 로그를 처음부터 함께 설계하는 습관으로 보겠습니다. 이 관점을 잡아 두면 이후 글에서 다룰 입력 검증, 인증, 인가, 저장, 로깅이 서로 어떻게 이어지는지도 훨씬 선명해집니다.

![Secure Coding 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/01/01-01-concept-at-a-glance.ko.png)
*Secure Coding 101 1장 흐름 개요*

> 보안은 기능 개발 끝에 덧칠하는 작업이 아니라 입력 경계·권한·저장·로그를 처음부터 함께 설계하는 습관입니다 — 실제 사고 대부분은 낯선 암호학이 아니라 입력 검증 누락, 비밀값 노출, 권한 확인 누락처럼 익숙한 개발 실수에서 시작합니다.

## 먼저 던지는 질문

- secure coding은 정확히 무엇을 뜻할까요?
- 위협 모델과 공격 표면은 코드 설계와 어떤 관계가 있을까요?
- OWASP Top 10은 입문자가 어떤 관점으로 읽어야 할까요?

## 왜 중요한가

보안 사고는 대개 예외적인 천재 공격보다 반복되는 기본 실수에서 나옵니다. 서버가 입력을 너무 쉽게 믿고, 비밀값을 코드나 로그에 남기고, 권한을 UI에서만 숨긴 채 API에서 다시 확인하지 않으면 기능은 돌아가도 시스템은 쉽게 흔들립니다.

secure coding이 중요한 이유도 여기에 있습니다. 사고가 난 뒤 전체를 다시 고치는 방식은 비용이 큽니다. 반대로 처음부터 입력 경계를 분명히 하고, 권한을 서버에서 다시 보고, 민감한 데이터를 분리해 두면 문제가 생겨도 영향 범위가 작아집니다. 운영에서는 이 차이가 그대로 복구 시간과 사고 규모로 이어집니다.

## 한눈에 보는 구조

이 그림은 secure coding을 구성하는 기본 흐름을 한 장에 모아 둔 것입니다. 사용자가 보낸 입력은 먼저 검증을 통과해야 하고, 핵심 로직은 인증과 인가 판단 안에서만 실행돼야 하며, 저장과 로그는 그 결과를 안전하게 다뤄야 합니다. 어느 한 단계만 비어도 나머지 단계의 품질이 함께 무너집니다.

## 핵심 용어

- **위협 모델(threat model)**: 누가 어디서 무엇을 노리는지 정리한 공격 지도입니다.
- **공격 표면(attack surface)**: 공격자가 실제로 건드릴 수 있는 입력 지점입니다.
- **신뢰 경계(trust boundary)**: 신뢰 가능한 영역과 신뢰하면 안 되는 영역이 갈리는 선입니다.
- **심층 방어(defense in depth)**: 얇은 방어막을 여러 겹 쌓아 한 번의 실수가 전체 사고로 번지지 않게 하는 방식입니다.
- **최소 권한(least privilege)**: 꼭 필요한 권한만 주고 나머지는 기본적으로 막는 원칙입니다.

## 바꾸기 전과 후

**바꾸기 전**: 기능을 먼저 만들고 보안은 나중에 붙입니다. 문제가 생기면 설계 전체를 다시 손봐야 하고, 이미 노출된 비밀값이나 잘못 열린 권한은 되돌리기 어렵습니다.

**바꾼 후**: 입력, 인증, 저장, 로그를 처음부터 함께 설계합니다. 문제가 생겨도 공격이 번지는 범위가 작고, 어디서 막아야 할지 판단하기 쉬워집니다.

## 실습: 더 안전한 흐름을 만드는 5단계

### 1단계 — 입력 경계를 먼저 표시합니다

```python
def parse_age(raw: str) -> int:
    if not raw.isdigit():
        raise ValueError("age must be digits")
    age = int(raw)
    if not (0 < age < 150):
        raise ValueError("age out of range")
    return age
```

입력값은 비즈니스 로직 안으로 들어오기 전에 형식과 범위를 확인해야 합니다. 이 함수가 하는 일은 단순하지만, 숫자가 아닌 값을 조용히 통과시키지 않는다는 점이 중요합니다. secure coding은 거대한 보안 프레임워크보다 이런 작은 경계 선언에서 시작합니다.

### 2단계 — 비밀값을 코드에서 분리합니다

```python
import os
DB_PASSWORD = os.environ["DB_PASSWORD"]  # 절대 하드코딩하지 않음
```

비밀번호나 API 키를 코드에 직접 넣는 순간 저장소, 리뷰 화면, 배포 로그, 협업 도구가 모두 유출 경로가 됩니다. 비밀값은 환경 변수나 비밀 저장소에서 읽고, 코드베이스는 그 값이 없다는 전제로 유지합니다.

### 3단계 — 함수 내부에서도 권한을 다시 확인합니다

```python
def delete_post(user, post):
    if post.author_id != user.id:
        raise PermissionError("not your post")
    post.delete()
```

라우트에서 한 번 권한을 검사했다고 끝나지 않습니다. 실제로 중요한 작업을 수행하는 함수 안에서 자원 소유권을 다시 확인해야 우회 호출을 막을 수 있습니다. UI에서 버튼을 숨기는 것과 서버에서 작업을 거부하는 것은 전혀 다른 수준의 방어입니다.

### 4단계 — 출력 단계에서 이스케이프합니다

```python
import html
def render(name: str) -> str:
    return f"<p>Hello, {html.escape(name)}</p>"
```

입력을 한 번 검증했다고 해서 출력이 자동으로 안전해지지는 않습니다. 브라우저에 HTML로 섞여 들어가는 값은 출력 위치에 맞게 다시 이스케이프해야 합니다. XSS는 대개 입력 단계보다 출력 단계에서 터집니다.

### 5단계 — 로그에서 비밀값을 지웁니다

```python
def log_login(user):
    print({"event": "login", "user_id": user.id})  # 비밀번호는 남기지 않음
```

로그는 운영 증거이면서 동시에 유출 위험입니다. 문제를 추적하려고 모든 값을 남기고 싶어지지만, 비밀번호와 토큰, 인증 헤더, 카드 번호는 복구 자료가 아니라 사고 자료가 됩니다. 운영에 필요한 식별자만 남기는 습관이 필요합니다.

## 이 코드에서 먼저 볼 점

- 검증은 한 번의 이벤트가 아니라 경계마다 반복되는 절차입니다.
- 비밀값은 코드가 아니라 환경 변수나 비밀 저장소에서 읽어야 합니다.
- 권한 검사는 라우트 바깥 설명이 아니라 실제 작업 함수 안에 둡니다.
- 저장과 출력, 로그는 모두 별도 보안 판단이 필요한 단계입니다.

## 실무에서 자주 헷갈리는 지점

1. **클라이언트 검증만 믿는 경우**: 브라우저 검증은 편의 기능일 뿐입니다. 서버는 항상 다시 확인해야 합니다.
2. **비밀값을 Git에 올리는 경우**: 한 번 커밋된 비밀값은 지워도 기록에 남기 쉽습니다. 회전 비용도 함께 생깁니다.
3. **오류 메시지에 내부 구조를 드러내는 경우**: 스택 트레이스나 SQL 조각은 공격자에게 시스템 지도를 줍니다.
4. **권한을 UI에서만 숨기는 경우**: API가 살아 있으면 공격자는 화면 없이도 직접 호출합니다.
5. **의존성 업데이트를 미루는 경우**: 알려진 CVE가 그대로 쌓이면 기능 결함이 아니라 운영 부채가 됩니다.

## 실무에서는 이렇게 봅니다

현업 팀은 대개 위협 모델링으로 출발합니다. 간단한 데이터 흐름도를 그리고, 어느 입력이 신뢰 경계를 넘는지, 어떤 자산이 가장 민감한지 먼저 적습니다. 그다음 CI에서 비밀값 스캔, 의존성 스캔, 정적 분석을 기본값으로 돌려 사람의 실수를 반복적으로 잡습니다.

중요한 점은 secure coding을 보안팀 전용 일로 분리하지 않는 것입니다. 기능을 만드는 개발자가 입력 스키마와 권한 체크, 로그 마스킹까지 같이 책임질 때 가장 효과가 큽니다. 반대로 보안을 마지막 리뷰 단계에만 몰아두면 구조적인 문제는 이미 코드 곳곳에 퍼져 있게 됩니다.

## 선임 엔지니어는 이렇게 생각합니다

- 입력은 기본적으로 적대적이라고 가정합니다.
- 비밀값은 언젠가 샐 수 있으니 코드 밖에 두고 회전 가능하게 설계합니다.
- 인가는 서버가 결정하고, UI는 그 결정을 보여 주는 층으로 봅니다.
- 로그는 증거이자 위험이므로 남길 값과 지울 값을 먼저 구분합니다.
- 완벽한 보안보다 사고 시간을 벌어 주는 설계를 현실적인 목표로 둡니다.

## 체크리스트

- [ ] 우리 서비스의 위협 모델을 한 문단으로 설명할 수 있습니다.
- [ ] 공격 표면이 어디인지 나열할 수 있습니다.
- [ ] 비밀값이 코드 저장소에 없습니다.
- [ ] 모든 입력이 서버 쪽 검증을 거칩니다.

## 연습 문제

1. 지금 만들고 있는 서비스의 신뢰 경계를 그림으로 그려 보세요.
2. 가장 자주 받는 입력 세 가지에 대해 검증 규칙을 적어 보세요.
3. 저장소에서 비밀값처럼 보이는 문자열을 검색해 보세요.

## 정리와 다음 글

secure coding은 거창한 추가 기능이 아니라, 입력 경계와 권한, 저장, 로그를 매일 조금씩 더 안전하게 만드는 개발 습관입니다. 이 글에서는 그 출발점으로 위협 모델, 공격 표면, 최소 권한 같은 기본 관점을 잡았습니다.

다음 글에서는 가장 먼저 무너지고 가장 자주 새는 지점인 입력값 검증을 깊게 다룹니다.

## 심화 실전 노트: STRIDE 위협 모델링과 공격 표면 분석

secure coding 원칙이 실제 설계로 이어지려면 "무엇이 위험한가"를 구조적으로 분류할 수 있어야 합니다. 여기서는 Microsoft가 제안한 STRIDE 모델을 기준으로 위협을 분류하고, 공격 표면을 코드 수준에서 식별하는 방법을 다룹니다.

### STRIDE 위협 분류표

| 분류 | 뜻 | 코드에서 나타나는 지점 | 대응 원칙 |
| --- | --- | --- | --- |
| **S**poofing | 신원 위조 | 인증 없는 API 호출, 토큰 위조 | 강한 인증, 토큰 서명 검증 |
| **T**ampering | 데이터 변조 | 쿠키 조작, 요청 본문 변조 | 무결성 검증, HMAC, 서명 |
| **R**epudiation | 부인 | 감사 로그 없는 작업 | 감사 로그, 타임스탬프 |
| **I**nformation Disclosure | 정보 유출 | 에러 메시지, 로그 노출 | 최소 정보 노출, 마스킹 |
| **D**enial of Service | 서비스 거부 | 무제한 요청, 대용량 업로드 | 속도 제한, 크기 제한 |
| **E**levation of Privilege | 권한 상승 | 수직/수평 권한 우회 | 최소 권한, 서버 측 인가 |

이 표를 설계 리뷰에 넣으면 "보안을 고려했다"는 모호한 표현 대신 "이 기능에서 Spoofing과 Tampering은 어떻게 막는가?"처럼 구체적인 질문이 나옵니다.

### 공격 표면 매핑 코드

공격 표면을 식별하는 첫 번째 단계는 외부 입력이 시스템에 진입하는 모든 경로를 나열하는 것입니다. FastAPI 기반 서비스를 예로 들어 봅니다.

```python
"""attack_surface.py — 라우트에서 공격 표면을 자동 추출하는 유틸리티"""
from fastapi import FastAPI
from dataclasses import dataclass

@dataclass
class EntryPoint:
    method: str
    path: str
    auth_required: bool
    input_sources: list[str]  # body, query, path, header, cookie

def map_attack_surface(app: FastAPI) -> list[EntryPoint]:
    """등록된 라우트에서 공격 표면 목록을 추출합니다."""
    entries = []
    for route in app.routes:
        if not hasattr(route, "methods"):
            continue
        for method in route.methods:
            has_auth = any(
                d.dependency.__name__ == "get_current_user"
                for d in getattr(route, "dependencies", [])
            )
            sources = []
            if "{" in route.path:
                sources.append("path")
            if method in ("POST", "PUT", "PATCH"):
                sources.append("body")
            sources.append("query")  # 모든 라우트는 쿼리 파라미터 가능
            sources.append("header")  # Host, Authorization 등
            entries.append(EntryPoint(
                method=method,
                path=route.path,
                auth_required=has_auth,
                input_sources=sources,
            ))
    return entries

def print_surface_report(entries: list[EntryPoint]) -> None:
    """공격 표면 보고서를 표 형태로 출력합니다."""
    unprotected = [e for e in entries if not e.auth_required]
    print(f"총 진입점: {len(entries)}")
    print(f"인증 없는 진입점: {len(unprotected)}")
    print()
    for ep in unprotected:
        print(f"  [위험] {ep.method} {ep.path} — 입력: {ep.input_sources}")
```

이 스크립트를 CI에 넣으면 새 라우트가 추가될 때마다 인증 누락 여부를 자동으로 경고할 수 있습니다. 공격 표면은 코드가 바뀔 때마다 함께 변하므로 정적 문서보다 자동 추출이 현실적입니다.

### OWASP Top 10과 이 시리즈의 매핑

OWASP Top 10은 웹 애플리케이션에서 가장 빈번한 위험 유형 10가지를 정리한 목록입니다. 이 시리즈의 각 글이 어떤 항목과 연결되는지 매핑해 두면 학습 우선순위를 잡기 쉽습니다.

| OWASP 항목 | 이 시리즈 대응 글 | 핵심 대응 패턴 |
| --- | --- | --- |
| A01 Broken Access Control | 4장 인가와 권한 | 서버 측 객체 단위 인가 |
| A02 Cryptographic Failures | 5장 안전한 데이터 저장 | 봉투 암호화, 키 회전 |
| A03 Injection | 7장 SQL Injection과 ORM | 파라미터 바인딩, ORM 안전 사용 |
| A04 Insecure Design | 1장 (현재 글) | STRIDE, 위협 모델링 |
| A05 Security Misconfiguration | 6장 Secret과 키 관리 | 환경 분리, 기본값 변경 |
| A06 Vulnerable Components | 9장 Dependency 취약점 | SCA, 자동 업데이트 |
| A07 Auth Failures | 3장 인증과 세션 | 안전한 세션, MFA |
| A08 Data Integrity Failures | 5장, 9장 | 서명 검증, SBOM |
| A09 Logging Failures | 10장 안전한 로깅 | 구조화 로그, 경보 |
| A10 SSRF | 2장 입력값 검증 | URL allowlist, 내부망 차단 |

이 매핑을 팀 위키에 붙여 두면 코드 리뷰 시 "이 변경이 A01에 해당하는데, 4장 패턴을 따르고 있는가?"처럼 구체적인 체크가 가능합니다.

### CI 보안 게이트 설정

위협 모델을 문서로만 남기면 배포가 반복될수록 현실과 괴리됩니다. CI 파이프라인에 보안 게이트를 넣어야 위협 모델이 코드와 함께 살아 움직입니다.

```yaml
# .github/workflows/security-gate.yml
name: Security Gate
on: [push, pull_request]
jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Detect secrets
        uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified

  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run safety check
        run: |
          pip install safety
          safety check --full-report

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run bandit
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json || true
      - name: Check high severity
        run: |
          python3 -c "
          import json, sys
          report = json.load(open('bandit-report.json'))
          high = [r for r in report.get('results', []) if r['issue_severity'] == 'HIGH']
          if high:
              for h in high:
                  print(f\"HIGH: {h['filename']}:{h['line_number']} — {h['issue_text']}\")
              sys.exit(1)
          print('No HIGH severity issues found.')
          "
```

이 워크플로는 세 가지를 검사합니다. 첫째, 커밋에 실제 비밀값이 섞이지 않았는지 확인합니다. 둘째, 의존성에 알려진 취약점이 없는지 확인합니다. 셋째, 정적 분석으로 고위험 패턴을 잡습니다. 세 검사 모두 통과해야 PR이 병합됩니다.

### 심층 방어를 코드로 구현하기

심층 방어는 추상적인 원칙처럼 들리지만, 코드에서는 같은 위협에 대해 여러 층에서 독립적으로 검증하는 구조로 드러납니다.

```python
"""defense_in_depth.py — 주문 처리에서 3중 방어를 보여 주는 예시"""
from pydantic import BaseModel, Field
from fastapi import FastAPI, Depends, HTTPException

# 1층: 입력 경계 — 스키마가 형식과 범위를 강제합니다
class OrderRequest(BaseModel):
    product_id: str = Field(pattern=r"^[A-Z0-9]{8}$")
    quantity: int = Field(ge=1, le=100)

# 2층: 인가 — 서버가 사용자 권한을 확인합니다
def check_can_order(user, product_id: str) -> None:
    if product_id.startswith("RESTRICTED") and "premium" not in user.roles:
        raise HTTPException(status_code=403, detail="premium only")

# 3층: 비즈니스 규칙 — 재고와 한도를 다시 검증합니다
def validate_stock(product_id: str, quantity: int) -> None:
    stock = get_stock(product_id)  # DB 조회
    if quantity > stock:
        raise HTTPException(status_code=409, detail="insufficient stock")

app = FastAPI()

@app.post("/orders")
def create_order(
    req: OrderRequest,
    user=Depends(get_current_user),
):
    check_can_order(user, req.product_id)   # 2층
    validate_stock(req.product_id, req.quantity)  # 3층
    order = save_order(user.id, req.product_id, req.quantity)
    audit_log("order_created", user_id=user.id, order_id=order.id)
    return {"order_id": order.id}
```

1층(스키마)이 뚫려도 2층(인가)이 막고, 2층이 뚫려도 3층(비즈니스 규칙)이 막습니다. 어느 한 층의 버그가 즉시 사고로 이어지지 않는 것이 심층 방어의 핵심입니다. 실무에서는 여기에 속도 제한(4층)과 감사 로그(5층)까지 추가하는 경우가 많습니다.

### 위협 모델링 워크시트

팀에서 새로운 기능을 설계할 때 아래 양식을 채우면 STRIDE 분석이 자연스럽게 따라옵니다.

```text
기능명: ____________________
데이터 흐름: 사용자 → [   ] → [   ] → [   ] → 저장소

1. 이 기능에서 인증 없이 접근 가능한 경로가 있는가? (Spoofing)
   답: 

2. 전송 중이나 저장 시점에 데이터가 변조될 가능성은? (Tampering)
   답: 

3. 누가 이 작업을 했는지 추적할 수 있는가? (Repudiation)
   답: 

4. 에러 응답이나 로그에 민감한 정보가 노출되는가? (Information Disclosure)
   답: 

5. 대량 요청이나 비정상 입력으로 서비스가 멈출 수 있는가? (DoS)
   답: 

6. 일반 사용자가 관리자 기능에 접근할 경로가 있는가? (EoP)
   답: 

위험 수준: [ ] 높음  [ ] 중간  [ ] 낮음
필요한 대응:
  - [ ] 인증 추가
  - [ ] 입력 스키마 강화
  - [ ] 감사 로그 추가
  - [ ] 속도 제한 적용
  - [ ] 암호화 적용
```

이 양식을 PR 템플릿에 포함시키면 보안 리뷰가 형식적인 서명이 아니라 구체적인 질문과 답변으로 바뀝니다.

### 보안 우선순위 판단 기준

모든 위협을 동시에 막을 수는 없습니다. 실무에서는 영향도와 발생 가능성을 축으로 우선순위를 정합니다.

```text
           발생 가능성 높음
                │
    ┌───────────┼───────────┐
    │  중간 우선 │  최우선    │
    │  (모니터링)│  (즉시 수정)│
    ├───────────┼───────────┤
    │  낮은 우선 │  중간 우선  │
    │  (수용/기록)│  (계획 수정)│
    └───────────┼───────────┘
                │
           발생 가능성 낮음
    
    영향도 낮음 ←──────────→ 영향도 높음
```

예를 들어 "비밀값이 코드에 있다"는 발생 가능성도 높고 영향도도 높으므로 즉시 수정합니다. 반면 "내부 관리자 페이지에 CSRF 토큰이 없다"는 영향도는 높지만 발생 가능성이 낮아 계획 수정으로 분류할 수 있습니다. 이 판단을 문서화해야 나중에 왜 그때 고치지 않았는지 설명할 수 있습니다.

### 실제 사고에서 배우는 교훈

보안 원칙이 왜 중요한지는 실제 사고를 보면 분명해집니다. 2017년 Equifax 사고는 Apache Struts의 알려진 취약점(CVE-2017-5638)을 두 달 넘게 패치하지 않아서 1억 4천만 명의 개인정보가 유출된 사건입니다. 이 사고에서 드러난 문제는 단일 실패가 아닙니다.

- 의존성 업데이트 프로세스 부재 (A06 Vulnerable Components)
- 내부 네트워크 세그먼트 미분리 (심층 방어 실패)
- 암호화되지 않은 민감 데이터 저장 (A02 Cryptographic Failures)
- 침입 탐지 인증서 만료로 수개월간 공격 미감지 (A09 Logging Failures)

한 가지 실수가 아니라 여러 층의 방어가 동시에 비어 있었기 때문에 피해가 커졌습니다. 심층 방어 원칙이 한 곳이라도 살아 있었다면 피해 규모는 크게 줄었을 것입니다. 이것이 이 시리즈가 입력, 인증, 인가, 저장, 로그를 각각 독립된 방어선으로 다루는 이유입니다.

## 처음 질문으로 돌아가기

- **secure coding은 정확히 무엇을 뜻할까요?**
  - 본문에서 정리한 것처럼 기능 개발 뒤에 보안을 덧붙이는 것이 아니라, 입력 경계·권한·저장·로그를 처음부터 함께 설계하는 개발 습관입니다. 5단계 실습에서 보았듯이 각 단계가 하나의 방어 층으로 작동할 때 전체 시스템이 예측 가능한 상태로 유지됩니다.
- **위협 모델과 공격 표면은 코드 설계와 어떤 관계가 있을까요?**
  - STRIDE 표에서 분류한 6가지 위협은 곧 코드에서 확인해야 할 6가지 질문입니다. 공격 표면 매핑 코드에서 보았듯이 라우트, 인증 여부, 입력 소스를 자동 추출하면 새 기능이 추가될 때마다 어디가 열려 있는지 바로 드러납니다.
- **OWASP Top 10은 입문자가 어떤 관점으로 읽어야 할까요?**
  - 매핑 표에서 정리한 것처럼 각 항목을 독립 지식으로 외우기보다 "이 코드가 A01~A10 중 어디에 해당하는가?"를 물으며 읽는 편이 실무에 가깝습니다. CI 보안 게이트처럼 자동화된 검사와 연결하면 문서 지식이 실제 방어선이 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- **Secure Coding이란 무엇인가? (현재 글)**
- 입력값 검증 (예정)
- 인증과 세션 (예정)
- 인가와 권한 (예정)
- 안전한 데이터 저장 (예정)
- Secret과 키 관리 (예정)
- SQL Injection과 ORM 안전 사용 (예정)
- XSS와 CSRF 방어 (예정)
- Dependency 취약점 관리 (예정)
- 안전한 로깅과 감사 (예정)

<!-- toc:end -->

## 참고 자료

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Secure Coding Practices Quick Reference](https://owasp.org/www-pdf-archive/OWASP_SCP_Quick_Reference_Guide_v2.pdf)
- [Microsoft Threat Modeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool)
- [Google — Secure by Design](https://security.googleblog.com/2024/01/secure-by-design.html)
- [CISA와 국제 파트너 — Secure by Design 원칙](https://www.cisa.gov/resources-tools/resources/shifting-balance-cybersecurity-risk-principles-and-approaches-secure-design)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/secure-coding-101/ko)

Tags: SecureCoding, Security, OWASP, DevSecOps, AppSec
