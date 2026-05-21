---
series: secure-coding-101
episode: 9
title: "Secure Coding 101 (9/10): Dependency 취약점 관리"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Dependencies
  - SCA
  - SBOM
  - SupplyChain
  - SecureCoding
seo_description: SCA, SBOM, lockfile, dependabot 그리고 안전한 dependency 관리 5단계
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (9/10): Dependency 취약점 관리

우리가 운영하는 서비스 대부분은 직접 쓴 코드보다 외부 라이브러리에 더 많이 기대고 있습니다. HTTP 클라이언트, ORM, 템플릿 엔진, 인증 라이브러리, 빌드 도구까지 모두 공급망의 일부입니다. 그래서 의존성 취약점은 남의 문제처럼 보여도 실제로는 우리 서비스의 취약점이 됩니다.

이 글은 Secure Coding 101 시리즈의 9번째 글입니다.

여기서는 dependency 관리를 버전 업데이트 작업으로만 보지 않고, lockfile, SCA, SBOM, 자동 업데이트, 재현 가능한 빌드까지 포함한 공급망 보안 흐름으로 정리하겠습니다. 이 관점을 이해하면 왜 lockfile 하나가 운영 안정성과 사고 대응 속도까지 좌우하는지도 선명해집니다.

## 먼저 던지는 질문

- SCA는 정확히 무엇을 검사할까요?
- SBOM은 언제 실무에서 큰 힘을 발휘할까요?
- lockfile은 왜 선택이 아니라 필수일까요?

## 큰 그림

![Secure Coding 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/09/09-01-concept-at-a-glance.ko.png)

*Secure Coding 101 9장 흐름 개요*

## 왜 중요한가

Log4j, event-stream, ua-parser-js 같은 사고는 공통점이 있습니다. 우리가 취약한 코드를 직접 쓰지 않았어도 라이브러리 하나로 서비스 전체가 영향을 받았다는 점입니다. 공급망 공격은 종종 코드 한 줄도 바꾸지 않고 들어옵니다.

이 주제가 어려운 이유는 보이지 않는 의존성이 많기 때문입니다. `requirements.txt`에 한 줄만 적어도 실제 설치되는 패키지는 훨씬 많고, 그중 상당수는 전이 의존성입니다. 무엇이 설치됐는지 모르면 무엇을 패치해야 하는지도 모르게 됩니다. 그래서 추적과 재현 가능성이 보안의 출발점이 됩니다.

## 한눈에 보는 구조

매니페스트는 원하는 패키지를 선언하고, lockfile은 실제로 설치할 정확한 버전과 해시를 고정합니다. 그 결과물을 SCA가 스캔하고, 취약점 경고는 자동 업데이트 PR과 연결됩니다. 이 흐름이 자동화돼야 공급망 위험을 계속 줄일 수 있습니다.

## 핵심 용어

- **소프트웨어 구성 분석(SCA)**: 의존성에 알려진 취약점이 있는지 검사하는 절차입니다.
- **SBOM**: 우리가 배포하는 구성 요소 전체 목록입니다.
- **lockfile**: 정확한 버전과 해시를 고정해 재현 가능한 빌드를 만드는 파일입니다.
- **버전 고정(pinning)**: 직접 의존성 버전을 명시적으로 고정하는 작업입니다.
- **전이 의존성(transitive dependency)**: 우리가 직접 추가한 패키지가 다시 끌어오는 하위 패키지입니다.

## 바꾸기 전과 후

**바꾸기 전**: `requirements.txt`에 상위 패키지 몇 개만 적어 두고 빌드할 때마다 다른 하위 버전이 들어옵니다. 무엇이 설치됐는지도, 취약한 패키지가 있는지도 금방 알기 어렵습니다.

**바꾼 후**: `uv.lock`이나 `poetry.lock`으로 버전과 해시를 고정합니다. CI는 SCA를 돌리고, 의존성 업데이트 PR이 주기적으로 들어오며, SBOM으로 구성 요소를 한눈에 파악할 수 있습니다.

## 실습: 의존성을 안전하게 관리하는 5단계

### 1단계 — lockfile을 생성합니다

```bash
uv lock          # 또는 poetry lock, pip-compile
```

lockfile이 없으면 같은 저장소에서도 빌드 시점마다 다른 패키지가 설치될 수 있습니다. 이 상태에서는 재현도 어렵고, 취약점 대응도 느려집니다. lockfile은 보안 도구이면서 운영 도구입니다.

### 2단계 — SBOM을 만듭니다

```bash
syft packages dir:. -o cyclonedx-json > sbom.json
```

SBOM은 사고가 났을 때 특히 강합니다. 특정 라이브러리에 취약점이 발표됐을 때 우리 서비스가 영향을 받는지 몇 초 안에 판단할 수 있기 때문입니다. 보안팀과 개발팀의 공용 언어가 되기도 합니다.

### 3단계 — SCA를 CI에 넣습니다

```bash
pip-audit                # Python
osv-scanner --lockfile=uv.lock   # generic
```

SCA는 알려진 CVE를 자동으로 찾아 줍니다. 중요한 점은 로컬 점검으로 끝내지 않고 CI에 넣어 계속 실행되게 만드는 것입니다. 그래야 새 취약점이 공개됐을 때 팀이 놓치지 않습니다.

### 4단계 — 업데이트를 자동화합니다

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule:
      interval: weekly
```

업데이트를 한꺼번에 몰아서 하면 충돌과 테스트 부담이 커집니다. 주간 단위처럼 작고 자주 들어오는 PR은 검토와 병합이 쉽고, 취약점 노출 기간도 줄입니다. 공급망 보안은 영웅적 한 번보다 작은 반복이 더 효과적입니다.

### 5단계 — 설치 시 해시까지 검증합니다

```bash
pip install --require-hashes -r requirements.txt
```

버전만 고정하고 해시를 확인하지 않으면 재현 가능성이 충분하지 않을 수 있습니다. 설치 시 해시를 함께 검증하면 예상한 아티팩트만 받아 온다는 확신이 생깁니다. 보안은 결국 공급망 무결성을 지키는 문제이기도 합니다.

## 이 코드에서 먼저 볼 점

- lockfile과 해시는 재현 가능한 빌드의 중심입니다.
- SBOM은 사고 대응 속도를 높여 주는 실무 도구입니다.
- 작은 업데이트를 자주 하는 편이 큰 사고를 줄입니다.
- 전이 의존성도 직접 의존성과 같은 수준으로 관리해야 합니다.

## 실무에서 자주 헷갈리는 지점

1. **lockfile 없이 latest만 쓰는 경우**: 공급망 공격과 재현 불가 빌드에 동시에 취약합니다.
2. **SCA 결과를 무시하는 경우**: 경고가 쌓일수록 진짜 위험도 함께 묻힙니다.
3. **전이 의존성을 보지 않는 경우**: 실제 CVE 상당수가 하위 의존성에서 나옵니다.
4. **유지보수 중단 라이브러리를 계속 쓰는 경우**: 패치가 나오지 않는 채 위험만 남습니다.
5. **자동 업데이트 PR을 오래 방치하는 경우**: 한 번에 처리해야 할 양이 커져 결국 더 손대기 어려워집니다.

## 실무에서는 이렇게 봅니다

대부분의 팀은 Renovate나 Dependabot으로 주간 PR을 받고, CI에는 SCA 게이트를 붙입니다. 조직이 커질수록 빌드 산출물과 함께 SBOM을 발행해 배포 단위마다 어떤 구성 요소가 포함됐는지 남깁니다. 취약점 공지가 나오면 SBOM과 lockfile을 기준으로 영향 범위를 빠르게 판단합니다.

또한 dependency 관리에서 가장 중요한 습관 중 하나는 덜 의존하는 것입니다. 라이브러리 하나를 추가하면 기능뿐 아니라 패치 주기, 라이선스, 공급망 위험, 유지보수 책임도 함께 받아들입니다. 새 패키지를 넣을 때는 편의성만이 아니라 장기 운영 비용도 같이 봐야 합니다.

## 선임 엔지니어는 이렇게 생각합니다

- dependency도 결국 우리 코드이며 우리 책임입니다.
- lockfile 없이는 재현 가능한 운영이 어렵습니다.
- 작은 주기 업데이트가 큰 사고를 막습니다.
- SBOM은 사고 대응 도구입니다.
- 덜 의존하는 선택 자체가 보안일 때가 많습니다.

## 체크리스트

- [ ] lockfile이 커밋돼 있습니다.
- [ ] SCA가 CI에서 실행됩니다.
- [ ] 자동 업데이트 PR이 주기적으로 들어옵니다.
- [ ] SBOM이 생성되거나 발행됩니다.

## 연습 문제

1. `pip-audit` 출력 한 줄을 읽고 의미를 설명해 보세요.
2. 전이 의존성에서 시작된 실제 CVE 사례를 하나 찾아 정리해 보세요.
3. lockfile 없이 빌드할 때 생기는 위험 세 가지를 적어 보세요.

## 정리와 다음 글

의존성 취약점 관리는 업데이트 작업이 아니라 공급망을 추적하고 재현 가능한 상태로 유지하는 운영 습관입니다. 이 글에서는 lockfile, SCA, SBOM, 자동 업데이트, 해시 검증이 왜 함께 움직여야 하는지 정리했습니다.

다음 글에서는 사고가 터졌을 때 사실을 재구성하게 도와주는 마지막 주제, 안전한 로깅과 감사를 다룹니다.

## 심화 실전 노트: 취약점 재현, 수정 패턴, OWASP 기준 연결

보안 코드는 추상 원칙만으로 유지되지 않습니다. 공격자가 실제로 어떤 입력을 넣는지, 코드가 어느 지점에서 그 입력을 신뢰하는지, 실패를 탐지했을 때 운영 단계에서 어떤 증거를 남기는지까지 한 흐름으로 연결해야 합니다. 그래서 실무에서는 취약점 이름을 외우는 것보다 "재현 가능한 실패 시나리오"를 먼저 만들고, 수정 후 같은 시나리오가 반드시 차단되는지 확인합니다.

### 취약점 예시 1: 입력 검증 우회와 타입 혼동

```python
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post("/transfer")
async def transfer(request: Request):
    body = await request.json()
    amount = body.get("amount")
    if amount <= 0:  # 문자열/None 혼합 입력에서 예외 또는 우회
        raise HTTPException(status_code=400, detail="invalid amount")
    return {"accepted": True}
```

위 코드는 숫자형 검증이 없어서 서비스 거부나 우회 입력이 섞일 수 있습니다. 수정 패턴은 명확합니다. 경계에서 스키마를 강제하고, 타입 변환 실패를 비즈니스 로직 진입 전에 종료합니다. Pydantic 모델, 최소/최대 범위, 소수점 스케일 규칙을 함께 사용하면 입력 품질이 크게 올라갑니다.

### 취약점 예시 2: SQL 인젝션과 문자열 결합

```python
# 취약한 패턴
query = f"SELECT * FROM users WHERE email = '{email}'"

# 개선 패턴
query = "SELECT * FROM users WHERE email = :email"
params = {"email": email}
```

핵심은 "ORM을 쓴다"가 아니라 "쿼리 경계를 데이터와 코드로 분리한다"입니다. ORM을 쓰더라도 raw SQL 지점이 남아 있으면 같은 위험이 재발합니다. 코드 리뷰 시에는 저장소 전체에서 문자열 포매팅 기반 쿼리 구성 지점을 일괄 탐색하고, 파라미터 바인딩으로 일관되게 바꾸는 작업이 필요합니다.

### 취약점 예시 3: 토큰 검증 순서 오류

JWT 처리에서 흔한 실패는 서명 검증보다 클레임 사용이 앞서는 경우입니다. 예를 들어 `sub`를 먼저 꺼내 권한 조회를 수행하면, 위조 토큰이 감사 로그에 정상 사용자처럼 남을 수 있습니다. 수정 패턴은 1) 알고리즘 화이트리스트 고정, 2) 서명 검증, 3) 만료/발급자/대상 검증, 4) 권한 매핑 순서를 고정하는 것입니다.

### OWASP 기준에 맞춘 운영 체크

OWASP Top 10 관점에서 이 시리즈 주제를 매핑하면 우선순위가 선명해집니다.

- `A01 Broken Access Control`: 인가 누락, 객체 단위 권한 검증 누락
- `A02 Cryptographic Failures`: 평문 저장, 약한 해시/암호 설정
- `A03 Injection`: SQL/NoSQL/Command Injection
- `A07 Identification and Authentication Failures`: 세션 고정, 토큰 처리 오류
- `A09 Security Logging and Monitoring Failures`: 추적 불가 로그, 경보 부재

중요한 점은 한 항목을 독립 과제로 다루지 않는 것입니다. 예를 들어 접근제어 결함을 줄이려면 인증, 세션, 로깅이 동시에 개선되어야 합니다. 그래서 팀 기준 문서에는 "취약점 분류"와 "수정 완료 조건"을 함께 적어야 합니다. 예를 들어 "재현 입력 차단 + 단위 테스트 + 감사 로그 필드 검증"을 완료 조건으로 명시하면 품질이 안정됩니다.

### 실무 적용 템플릿

보안 이슈 하나를 수정할 때는 다음 순서를 고정하는 편이 효율적입니다.

1. 실패 입력을 테스트로 먼저 고정합니다.
2. 경계 검증, 인코딩, 파라미터 바인딩 중 필요한 패턴을 적용합니다.
3. 같은 클래스의 취약점이 있는 인접 경로를 같이 점검합니다.
4. 로그/메트릭/경보를 추가해 재발 시 빠르게 감지합니다.

이 흐름을 반복하면 보안 코딩이 문서상의 원칙이 아니라 배포 품질의 일부로 자리잡습니다.

### 추가 사례: 수정 패턴을 테스트와 운영 신호로 닫는 방법

취약점 수정이 실패하는 가장 흔한 이유는 코드 한 줄을 고치고 끝냈다고 판단하기 때문입니다. 보안 수정은 항상 세 겹으로 닫아야 합니다. 첫째, 공격 입력을 재현하는 테스트를 추가합니다. 둘째, 실패 원인을 제거하는 수정 패턴을 적용합니다. 셋째, 운영 환경에서 같은 공격이 다시 들어왔을 때 탐지 가능한 로그와 경보를 남깁니다.

예를 들어 XSS 차단을 위해 출력 인코딩을 넣었다면, 템플릿 경로별 인코딩 누락 여부를 점검하고 CSP 위반 로그를 대시보드로 수집해야 합니다. SQL 인젝션을 차단했다면 파라미터 바인딩 사용률을 정적 점검으로 확인하고, 쿼리 오류율 급증 알람을 설정해야 합니다. 이렇게 테스트, 코드, 운영 신호를 함께 묶어야 OWASP 항목이 문서상의 체크가 아니라 실제 방어선으로 작동합니다.

### 보강 메모: 보안 수정 완료 조건

수정 완료는 "동작함"이 아니라 "공격 입력 차단 + 회귀 테스트 통과 + 운영 탐지 가능" 세 조건을 만족할 때 선언해야 합니다. 이 기준을 팀 규칙으로 고정하면 동일 취약점의 반복 발생률이 빠르게 낮아집니다.

의존성 취약점 대응은 버전 업 한 번으로 닫히지 않습니다. 영향 범위 분석, 런타임 노출 경로 점검, 롤백 계획까지 포함해야 운영 중단 없이 안전하게 완료할 수 있습니다.

또한 SBOM을 주기적으로 갱신해 실제 배포 아티팩트 기준으로 취약점 노출을 확인해야 합니다. 개발 환경과 배포 환경의 의존성이 다르면 탐지 결과가 왜곡될 수 있습니다.

## 처음 질문으로 돌아가기

- **SCA는 정확히 무엇을 검사할까요?**
  - 본문의 기준은 Dependency 취약점 관리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **SBOM은 언제 실무에서 큰 힘을 발휘할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **lockfile은 왜 선택이 아니라 필수일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Secure Coding 101 (1/10): Secure Coding이란 무엇인가?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): 입력값 검증](./02-input-validation.md)
- [Secure Coding 101 (3/10): 인증과 세션](./03-authentication-and-session.md)
- [Secure Coding 101 (4/10): 인가와 권한](./04-authorization-and-permissions.md)
- [Secure Coding 101 (5/10): 안전한 데이터 저장](./05-safe-data-storage.md)
- [Secure Coding 101 (6/10): Secret과 키 관리](./06-secret-and-key-management.md)
- [Secure Coding 101 (7/10): SQL Injection과 ORM 안전 사용](./07-sql-injection-and-orm.md)
- [Secure Coding 101 (8/10): XSS와 CSRF 방어](./08-xss-and-csrf.md)
- **Dependency 취약점 관리 (현재 글)**
- 안전한 로깅과 감사 (예정)

<!-- toc:end -->

## 참고 자료

- [OWASP — Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/)
- [pip-audit](https://github.com/pypa/pip-audit)
- [OSV.dev](https://osv.dev/)
- [CycloneDX SBOM](https://cyclonedx.org/)
- [PyPA — Repeatable Installs](https://pip.pypa.io/en/stable/topics/repeatable-installs/)

Tags: Dependencies, SCA, SBOM, SupplyChain, SecureCoding
