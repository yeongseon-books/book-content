---
series: secure-coding-101
episode: 6
title: "Secure Coding 101 (6/10): Secret과 키 관리"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Secrets
  - KeyManagement
  - Vault
  - SecureCoding
  - DevSecOps
seo_description: 환경 변수, secret manager, 키 회전, secret scan 그리고 안전한 키 관리 5단계
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (6/10): Secret과 키 관리

비밀값은 유출되기 전까지는 잘 보이지 않지만, 한 번 새면 복구 비용이 크게 튀는 자산입니다. 데이터베이스 비밀번호, API 키, 서명 키, 액세스 토큰이 코드 저장소나 CI 로그, 채팅창, 운영 문서에 흩어져 있으면 시스템은 기능적으로 정상이어도 운영 복원력은 아주 약해집니다.

여기서는 secret 관리를 단순히 환경 변수에 넣는 방법으로 끝내지 않고, 코드 분리, 비밀 저장소, 회전, 접근 감사, 마스킹까지 이어지는 운영 체계로 정리하겠습니다. 이 관점을 이해하면 왜 하드코딩이 위험한지뿐 아니라, 왜 회전 가능성이 secret 설계의 핵심인지도 분명해집니다.

![Secure Coding 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/06/06-01-concept-at-a-glance.ko.png)
*Secure Coding 101 6장 흐름 개요*

## 먼저 던지는 질문

- 어떤 값까지 secret으로 봐야 할까요?
- 하드코딩된 secret은 왜 Git에 한 번만 올라가도 치명적일까요?
- secret manager는 환경 변수와 무엇이 다를까요?

## 왜 중요한가

가장 흔한 secret 사고는 Git에 비밀값을 커밋하는 경우입니다. 한 번 원격 저장소로 밀어 올리면 삭제해도 기록과 포크, CI 로그, 캐시, 협업 도구에 흔적이 남습니다. 그래서 history rewrite만으로는 완전한 복구가 되지 않는 경우가 많습니다.

또한 secret 문제는 단일 유출 사건으로 끝나지 않습니다. 같은 값을 여러 환경에서 재사용하면 개발 환경 유출이 곧 운영 유출이 되고, 회전 절차가 수동이면 사고가 나도 교체가 늦어집니다. 선임 엔지니어는 secret을 숨기는 대상이 아니라, 언젠가 샐 수 있다고 가정하고 회복 가능한 형태로 설계해야 할 운영 자산으로 봅니다.

## 한눈에 보는 구조

이 구조에서 코드에는 secret이 직접 들어 있지 않고, 런타임이 환경 변수나 secret manager를 통해 값을 읽습니다. secret manager는 저장뿐 아니라 접근 감사와 회전을 함께 담당합니다. 회전 경로가 처음부터 설계돼 있어야 사고 대응 속도가 나옵니다.

## 핵심 용어

- **비밀값(secret)**: 알려지면 위험한 값입니다. API 키, DB 비밀번호, 토큰, 서명 키가 여기에 들어갑니다.
- **비밀 저장소(secret manager)**: secret을 저장하고, 접근을 제어하며, 회전과 감사를 지원하는 중앙 서비스입니다.
- **회전(rotation)**: 비밀값을 주기적으로 또는 사고 후 즉시 새 값으로 교체하는 절차입니다.
- **범위(scope)**: secret 하나가 영향을 미치는 시스템 폭입니다.
- **감사 로그(audit log)**: 누가 언제 어떤 secret을 읽었는지 남기는 기록입니다.

## 바꾸기 전과 후

**바꾸기 전**: `config.py` 안에 `API_KEY = "..."`가 있고, CI 로그와 예외 출력이 그 값을 그대로 보여 줍니다. 운영과 개발 환경도 같은 비밀값을 씁니다.

**바꾼 후**: secret은 환경 변수와 secret manager를 통해 주입하고, 로그는 기본적으로 마스킹하며, 환경별로 분리된 값을 자동 회전합니다. 접근 이력도 감사 로그로 남깁니다.

## 실습: 안전하게 secret을 관리하는 5단계

### 1단계 — secret을 코드에서 분리합니다

```python
import os
DB_PASSWORD = os.environ["DB_PASSWORD"]  # 절대 코드에 넣지 않음
```

가장 먼저 해야 할 일은 secret이 코드 저장소에 들어오지 않게 하는 것입니다. 코드 리뷰와 브랜치, 스냅샷, 포크, 협업 문서까지 모두 잠재 유출 경로이기 때문입니다. 코드베이스는 secret을 참조만 하고, 값 자체는 런타임이 주입해야 합니다.

### 2단계 — `.env`는 로컬 전용으로 둡니다

```bash
echo ".env" >> .gitignore
```

개발 편의를 위한 `.env` 파일은 로컬 전용으로 취급해야 합니다. 이 파일이 저장소에 들어오는 순간 팀 전체가 유출 범위 안에 들어갑니다. 로컬 개발용과 운영용 secret 공급 경로는 처음부터 분리하는 편이 안전합니다.

### 3단계 — secret manager에서 값을 읽습니다

```python
import boto3
client = boto3.client("secretsmanager")
val = client.get_secret_value(SecretId="prod/db")["SecretString"]
```

secret manager를 쓰면 저장뿐 아니라 접근 권한, 회전, 감사가 함께 따라옵니다. 환경 변수만으로는 값이 어디서 왔는지, 누가 읽었는지 추적하기 어렵지만, 중앙 저장소는 그 부분을 운영 체계로 묶어 줍니다.

### 4단계 — 회전 절차를 자동화합니다

```bash
# 새 secret 발급 -> 애플리케이션 재적재 -> 이전 secret 폐기
aws secretsmanager rotate-secret --secret-id prod/db
```

회전이 수동 절차에만 의존하면 평소에는 거의 실행되지 않습니다. 사고가 난 뒤에도 교체 속도가 늦어집니다. secret은 처음 발급할 때부터 교체 경로가 준비돼 있어야 합니다. 새 값을 발급하고 애플리케이션이 다시 읽은 뒤 이전 값을 폐기하는 흐름이 자동이어야 합니다.

### 5단계 — 노출은 기본적으로 마스킹합니다

```python
def mask(s, keep=4):
    return s[:keep] + "*" * (len(s) - keep)
print("API key:", mask(API_KEY))
```

## 회전이 실무에서 실패하는 지점

secret 회전은 새 값을 발급하는 데서 끝나지 않습니다. 주변 시스템이 이전 값을 얼마나 오래 붙잡고 있는지까지 봐야 실제로 성공합니다.

```text
실패 형태: 새 DB 비밀번호는 발급됐지만 앱 연결은 여전히 이전 연결을 씁니다
먼저 볼 항목:
1. connection pool 재생성 시점
2. 워커와 배치 잡의 재기동 순서
3. 이전 비밀번호 폐기 유예 시간

실패 형태: JWT 서명 키를 바꿨더니 기존 토큰이 바로 모두 실패합니다
먼저 볼 항목:
1. kid 기반 키 공존 기간
2. 활성 세션에 대한 grace period
3. API gateway 캐시 무효화 시점
```

회전이 어려운 secret은 결국 운영 부채입니다. secret manager를 도입했더라도 실제 교체 절차를 장애 훈련처럼 검증하지 않으면 사고 시점에 가장 먼저 흔들립니다.

운영 중에는 디버깅 편의 때문에 secret 일부를 보고 싶어질 수 있습니다. 이때도 전체 값을 그대로 노출하지 말고 기본적으로 마스킹해야 합니다. 로그, 콘솔 출력, 알림 메시지는 모두 유출 표면입니다.

## 이 코드에서 먼저 볼 점

- secret manager는 접근 감사와 권한 통제를 기본값으로 제공합니다.
- 회전은 애플리케이션 중단 없이 가능해야 합니다.
- 로그 마스킹은 예외 상황이 아니라 기본 설정이어야 합니다.
- 환경별 분리는 유출 반경을 줄이는 가장 쉬운 방법입니다.

## 실무에서 자주 헷갈리는 지점

1. **secret을 Git에 커밋하는 경우**: 한 번의 실수로 기록 전체를 오염시킬 수 있습니다.
2. **CI 로그에 환경 변수를 그대로 찍는 경우**: 공개 로그는 곧 공개 secret이 됩니다.
3. **회전을 수동으로만 하는 경우**: 결국 주기가 지켜지지 않고 사고 대응도 늦어집니다.
4. **모든 환경에서 같은 secret을 재사용하는 경우**: 한 환경 유출이 전체 유출로 번집니다.
5. **secret을 프로세스 메모리에 오래 붙잡아 두는 경우**: 메모리 덤프나 크래시 자료가 곧 유출 자료가 됩니다.

## 실무에서는 이렇게 봅니다

많은 팀이 Vault, AWS Secrets Manager, Doppler, 1Password Connect 같은 도구를 채택해 환경별 secret을 분리합니다. CI는 장기 비밀번호 대신 short-lived token으로 필요한 순간에만 값을 읽게 하고, `git push` 단계에는 secret scan을 기본 훅으로 붙입니다.

여기서 핵심은 secret 관리가 저장 방식이 아니라 운영 절차라는 사실입니다. 누가 읽을 수 있는지, 언제 교체하는지, 유출 징후가 보이면 어떤 순서로 폐기하는지까지 문서와 자동화가 있어야 실제로 작동합니다. secret manager 도입만으로 문제가 끝나지 않는 이유가 여기에 있습니다.

## 선임 엔지니어는 이렇게 생각합니다

- secret은 언젠가 샐 수 있다고 가정하고 설계합니다.
- 자동이 아닌 회전은 실제 회전이 아닙니다.
- 범위가 작은 secret일수록 유출 반경도 작습니다.
- secret 접근은 기본적으로 감사 가능해야 합니다.
- 로그는 기본적으로 마스킹돼 있어야 합니다.

## 체크리스트

- [ ] Git secret scanning이 켜져 있습니다.
- [ ] secret이 환경별로 분리돼 있습니다.
- [ ] 회전이 자동화돼 있습니다.
- [ ] secret 조회에 대한 감사 로그가 있습니다.

## 연습 문제

1. Git 기록에서 secret을 찾는 명령 두 개를 적어 보세요.
2. 환경 변수와 secret manager의 장단점을 비교해 보세요.
3. 장기 토큰보다 short-lived token이 왜 유리한지 설명해 보세요.

## 정리와 다음 글

secret 관리의 핵심은 값을 숨기는 데서 끝나지 않습니다. 코드 분리, 중앙 저장, 접근 감사, 자동 회전, 기본 마스킹까지 갖춰야 유출 사고가 나도 복구 비용을 작게 유지할 수 있습니다.

다음 글에서는 이런 비밀값으로 지키는 데이터 계층에서 가장 오래된 공격인 SQL injection과 ORM 안전 사용을 다룹니다.

## 심화 실전 노트: secret 유출 탐지, 회전 자동화, 비상 폐기 체계

### Git 기록 속 secret 탐색과 사전 차단

secret이 한 번 커밋되면 기록 전체가 오염됩니다. `git log -p`나 `git diff`로 텍스트를 뒤지는 방법도 있지만, 대규모 저장소에서는 전용 도구가 필요합니다.

```bash
# truffleHog — 엔트로피 기반 + 패턴 기반 탐색
trufflehog git file://. --since-commit HEAD~100 --json

# git-secrets — AWS 패턴 기본 내장, pre-commit hook
git secrets --install
git secrets --register-aws
git secrets --scan

# gitleaks — TOML 규칙 파일 기반
gitleaks detect --source . --report-format json --report-path leak-report.json
```

세 도구 모두 CI에 붙일 수 있지만, 가장 효과적인 지점은 **pre-commit hook**입니다. 커밋 시점에 차단하면 원격 저장소까지 도달하지 않습니다.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

CI에서는 PR 단위로 추가 스캔을 실행합니다. pre-commit을 건너뛴 경우(force push, GUI 커밋)에도 마지막 방어선이 됩니다.

```yaml
# GitHub Actions 예시
- name: Secret scan
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### HashiCorp Vault 실전 구성

Vault는 단순 키-값 저장 외에도 동적 자격 증명, 정책 기반 접근 제어, 감사 로그를 제공합니다. 실무에서 가장 먼저 설정해야 할 부분은 정책과 인증 방식입니다.

```hcl
# policy: app-db-read.hcl
path "secret/data/prod/db" {
  capabilities = ["read"]
}

path "secret/data/prod/db" {
  capabilities = ["update"]
  required_parameters = ["rotation_id"]
}
```

```bash
# 정책 등록 및 토큰 발급
vault policy write app-db-read app-db-read.hcl
vault token create -policy=app-db-read -ttl=1h -use-limit=10
```

TTL과 use-limit을 함께 설정하면 토큰이 유출되더라도 피해 창이 좁습니다. Kubernetes 환경에서는 ServiceAccount 인증을 쓰면 토큰을 코드에 넣지 않아도 됩니다.

```python
import hvac

client = hvac.Client(url="https://vault.internal:8200")
# Kubernetes 인증 — Pod의 SA 인증으로 자동 인증
client.auth.kubernetes.login(
    role="app-db-reader",
    jwt=open("/var/run/secrets/kubernetes.io/serviceaccount/token").read()
)
secret = client.secrets.kv.v2.read_secret_version(
    mount_point="secret", path="prod/db"
)
db_password = secret["data"]["data"]["password"]
```

### 동적 자격 증명과 lease 관리

Vault의 동적 secret은 요청 시점에 임시 자격 증명을 생성하고, lease가 만료되면 자동 폐기합니다. 이 방식은 장기 비밀번호를 아예 없애는 가장 강력한 패턴입니다.

```bash
# DB secret engine 설정
vault secrets enable database
vault write database/config/mydb   plugin_name=mysql-database-plugin   connection_url="{{username}}:{{password}}@tcp(db.internal:3306)/"   allowed_roles="app-role"   username="vault-admin"   password="vault-admin-pw"

vault write database/roles/app-role   db_name=mydb   creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';     GRANT SELECT, INSERT ON mydb.* TO '{{name}}'@'%';"   default_ttl="1h"   max_ttl="24h"
```

```python
# 앱에서 동적 자격 증명 요청
creds = client.secrets.database.generate_credentials(name="app-role")
db_user = creds["data"]["username"]  # v-app-role-abc123
db_pass = creds["data"]["password"]  # 임시 비밀번호, 1시간 후 자동 폐기
lease_id = creds["lease_id"]

# 필요 시 lease 갱신
client.sys.renew_lease(lease_id=lease_id, increment=3600)
```

동적 자격 증명의 장점은 회전 절차가 불필요하다는 사실입니다. 값 자체가 수명이 있으므로 유출되더라도 만료 후에는 무용지물이 됩니다.

### 비상 폐기(emergency revocation) 절차

secret 유출이 확인되면 교체 전에 먼저 **즉시 폐기**가 필요합니다. 폐기와 교체는 다릅니다. 폐기는 기존 값을 무효화하는 것이고, 교체는 새 값을 발급하는 것입니다. 순서가 중요합니다.

```text
비상 폐기 절차 (Runbook 요약)

1. 영향 범위 확인
   - 유출된 secret이 어떤 환경/서비스에서 사용되는지 확인
   - secret manager의 접근 감사 로그로 최근 사용 이력 확인

2. 즉시 폐기
   - Vault: vault lease revoke -prefix secret/data/prod/
   - AWS: aws secretsmanager delete-secret --secret-id <id> --force-delete
   - GitHub: Settings > Secrets > Delete

3. 새 값 발급 및 배포
   - 새 secret 생성 (이전 값과 무관한 새 값)
   - 배포 파이프라인 통해 서비스 재시작
   - 연결 풀, 캐시, 워커 프로세스 모두 갱신 확인

4. 사후 검증
   - 이전 값으로 인증 시도 → 실패 확인
   - 감사 로그에 폐기 이벤트 기록 확인
   - 인시던트 보고서 작성
```

```python
# 비상 폐기 자동화 예시 — Vault의 모든 lease 일괄 폐기
import hvac

client = hvac.Client(url="https://vault.internal:8200", token=emergency_token)

# prefix 기반 일괄 폐기
client.sys.revoke_prefix("database/creds/app-role")

# 특정 secret 버전 파괴 (복구 불가)
client.secrets.kv.v2.destroy_secret_versions(
    path="prod/db",
    versions=[1, 2, 3],
    mount_point="secret"
)
```

### secret 범위 분리 전략

secret 하나가 영향을 미치는 범위가 넓을수록 유출 비용이 커집니다. 실무에서 범위를 줄이는 패턴은 크게 세 가지입니다.

| 분리 축 | 방법 | 효과 |
|---------|------|------|
| 환경별 | dev/staging/prod 각각 다른 값 | 개발 환경 유출이 운영에 영향 없음 |
| 서비스별 | 서비스마다 전용 secret | 한 서비스 침해가 다른 서비스로 확산 안 됨 |
| 수명별 | short-lived token + 동적 발급 | 유출돼도 만료 후 무용지물 |

```python
# 환경별 분리 — 설정 로더 예시
import os

ENV = os.environ.get("APP_ENV", "dev")

SECRET_PATHS = {
    "dev": "secret/data/dev/db",
    "staging": "secret/data/staging/db",
    "prod": "secret/data/prod/db",
}

def get_db_secret(vault_client):
    path = SECRET_PATHS[ENV]
    return vault_client.secrets.kv.v2.read_secret_version(
        mount_point="secret", path=path.replace("secret/data/", "")
    )["data"]["data"]["password"]
```

### CI/CD 파이프라인에서 secret 안전하게 사용하기

CI 환경은 secret 유출 위험이 높은 지점입니다. 빌드 로그가 공개되거나, PR 빌드에서 secret이 노출되거나, 캐시에 값이 남을 수 있습니다.

```yaml
# GitHub Actions — secret 마스킹과 최소 권한
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # OIDC 토큰 발급용
      contents: read
    steps:
      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/deploy-role
          aws-region: ap-northeast-2
          # 장기 키 대신 OIDC로 임시 자격 증명 획득

      - name: Read secret
        run: |
          SECRET=$(aws secretsmanager get-secret-value             --secret-id prod/api-key             --query SecretString --output text)
          echo "::add-mask::$SECRET"  # 로그에서 자동 마스킹
          echo "API_KEY=$SECRET" >> "$GITHUB_ENV"
```

핵심 원칙은 세 가지입니다:
1. 장기 키 대신 OIDC 기반 임시 자격 증명을 사용합니다.
2. `::add-mask::`로 로그 출력을 차단합니다.
3. PR 빌드(fork)에는 secret을 전달하지 않습니다.

### secret 감사와 접근 모니터링

secret manager를 도입했더라도 누가 언제 읽었는지 모니터링하지 않으면 유출 탐지가 늦어집니다.

```bash
# Vault 감사 로그 활성화
vault audit enable file file_path=/var/log/vault/audit.log

# 감사 로그 형식 (JSON)
# {
#   "type": "response",
#   "auth": {"token_type": "service", "policies": ["app-db-read"]},
#   "request": {"path": "secret/data/prod/db", "operation": "read"},
#   "response": {"data": {"data": "hmac-sha256:..."}},  # 값은 HMAC 처리
#   "time": "2026-05-15T09:23:41Z"
# }
```

감사 로그를 SIEM(Splunk, Elastic, Datadog)으로 전송하면 다음 규칙으로 이상 탐지가 가능합니다:

```text
경보 규칙 예시:
- 업무 시간 외 secret 조회 → 즉시 알림
- 동일 토큰으로 10분 내 50회 이상 조회 → 자동 토큰 폐기
- 비인가 정책의 접근 시도 → 인시던트 생성
- 이전에 접근한 적 없는 경로 조회 → 검토 요청
```

### 메모리 내 secret 보호

secret을 읽은 뒤 프로세스 메모리에 오래 남겨두면 코어 덤프, 힙 분석, `/proc/<pid>/mem` 접근으로 유출될 수 있습니다.

```python
import ctypes
import os

def secure_zero(buffer: bytearray):
    """메모리에서 secret을 안전하게 지웁니다."""
    ctypes.memset(
        (ctypes.c_char * len(buffer)).from_buffer(buffer),
        0,
        len(buffer)
    )

# 사용 예
secret_bytes = bytearray(get_secret_from_vault().encode())
try:
    # secret 사용
    authenticate(secret_bytes)
finally:
    secure_zero(secret_bytes)  # 사용 후 즉시 제로화
```

Python은 문자열이 불변(immutable)이라 `bytearray`를 써야 제로화가 가능합니다. Go는 `memguard`, Rust는 `secrecy` 크레이트가 동일한 역할을 합니다. 완벽하지는 않지만, GC가 참조를 놓은 후에도 메모리에 값이 남는 시간을 줄입니다.

### secret 유출 사고 대응 타임라인

실제 사고에서 가장 중요한 것은 탐지부터 폐기까지의 시간(MTTC, Mean Time To Contain)입니다. 아래는 실무에서 권장하는 타임라인입니다.

```text
T+0분   유출 탐지 (secret scan 알림, 외부 제보, 이상 접근 경보)
T+5분   영향 범위 확인 — 어떤 환경, 어떤 서비스, 어떤 데이터에 접근 가능한 secret인지
T+15분  즉시 폐기 — 해당 secret을 무효화 (Vault revoke, AWS delete, GitHub invalidate)
T+30분  새 값 발급 및 배포 — 서비스 재시작, 연결 풀 갱신 확인
T+60분  사후 검증 — 이전 값 인증 실패 확인, 감사 로그 이상 없음 확인
T+24시간 인시던트 보고서 작성 — 근본 원인, 재발 방지 조치, 프로세스 개선
```

이 타임라인에서 가장 자주 실패하는 구간은 T+5분~T+15분입니다. secret이 어디에서 쓰이는지 문서화되어 있지 않으면 영향 범위 확인에 시간이 걸리고, 폐기 절차가 수동이면 담당자를 찾는 데 추가 시간이 소모됩니다.

```python
# secret 인벤토리 예시 — 어떤 secret이 어디서 쓰이는지 추적
SECRET_INVENTORY = {
    "prod/db/password": {
        "services": ["api-server", "batch-worker", "analytics"],
        "environments": ["prod"],
        "rotation_owner": "platform-team",
        "last_rotated": "2026-04-20",
        "emergency_contact": "#incident-channel",
    },
    "prod/stripe/api-key": {
        "services": ["payment-service"],
        "environments": ["prod"],
        "rotation_owner": "payment-team",
        "last_rotated": "2026-05-01",
        "emergency_contact": "#payment-oncall",
    },
}

def get_affected_services(secret_id: str) -> list[str]:
    entry = SECRET_INVENTORY.get(secret_id, {})
    return entry.get("services", ["unknown — 인벤토리 업데이트 필요"])
```

이 인벤토리가 있으면 사고 시점에 "이 secret이 어디서 쓰이지?"라는 질문에 즉시 답할 수 있습니다. Vault의 경우 정책(policy)과 역할(role) 매핑이 이 역할을 부분적으로 대신하지만, 서비스 레벨까지는 별도 문서가 필요합니다.

### .env 파일이 유출됐을 때 대응

`.env` 파일은 로컬 전용이어야 하지만, 실수로 커밋되거나 백업에 포함되는 경우가 있습니다. 이때 대응은 단순히 파일을 삭제하는 것이 아닙니다.

```bash
# 1. Git 기록에서 .env 제거 (BFG Repo-Cleaner)
bfg --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 2. .env에 들어있던 모든 값을 유출된 것으로 간주
#    → 각 값에 대해 즉시 폐기 + 새 값 발급

# 3. .gitignore에 .env 확인 (이미 있어야 하지만 재확인)
grep -q "^\.env$" .gitignore || echo ".env" >> .gitignore

# 4. 팀 전체에 알림 — 포크가 있다면 포크에도 흔적이 남아 있음
```

BFG로 기록을 정리해도 이미 클론한 사본, 포크, CI 캐시에는 이전 기록이 남아 있습니다. 그래서 기록 정리는 보조 조치일 뿐, 핵심은 해당 secret을 즉시 폐기하고 새 값으로 교체하는 것입니다.

## 처음 질문으로 돌아가기

- **어떤 값까지 secret으로 봐야 할까요?**
  - 본문에서 정의한 기준은 "알려지면 위험한 값"입니다. DB 비밀번호, API 키, 서명 키, 토큰이 대표적이지만, 내부 서비스 URL이나 환경별 설정값도 유출 시 공격 표면을 넓힌다면 secret으로 취급해야 합니다. 동적 자격 증명 절에서 본 것처럼, 값의 수명이 짧을수록 secret 관리 부담이 줄어듭니다.
- **하드코딩된 secret은 왜 Git에 한 번만 올라가도 치명적일까요?**
  - Git 기록은 삭제해도 포크, CI 캐시, 협업 도구에 흔적이 남습니다. history rewrite만으로 완전 복구가 되지 않으므로, pre-commit hook과 CI scan으로 커밋 시점에 차단하고, 유출이 확인되면 즉시 폐기 후 새 값을 발급하는 것이 유일한 대응입니다.
- **secret manager는 환경 변수와 무엇이 다를까요?**
  - 환경 변수는 값을 주입하는 채널일 뿐, 누가 읽었는지·언제 교체할지·유출 시 어떻게 폐기할지에 대한 답이 없습니다. secret manager는 접근 정책, 감사 로그, 자동 회전, 동적 발급, 비상 폐기까지 운영 체계로 묶어 줍니다. Vault 구성 절에서 본 것처럼 TTL, use-limit, lease 기반 자동 만료가 환경 변수로는 불가능한 부분입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Secure Coding 101 (1/10): Secure Coding이란 무엇인가?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): 입력값 검증](./02-input-validation.md)
- [Secure Coding 101 (3/10): 인증과 세션](./03-authentication-and-session.md)
- [Secure Coding 101 (4/10): 인가와 권한](./04-authorization-and-permissions.md)
- [Secure Coding 101 (5/10): 안전한 데이터 저장](./05-safe-data-storage.md)
- **Secret과 키 관리 (현재 글)**
- SQL Injection과 ORM 안전 사용 (예정)
- XSS와 CSRF 방어 (예정)
- Dependency 취약점 관리 (예정)
- 안전한 로깅과 감사 (예정)

<!-- toc:end -->

## 참고 자료

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [HashiCorp Vault](https://developer.hashicorp.com/vault/docs)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [GitHub — Secret scanning](https://docs.github.com/en/code-security/secret-scanning)
- [The Twelve-Factor App — Config](https://12factor.net/config)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/secure-coding-101/ko)

Tags: Secrets, KeyManagement, Vault, SecureCoding, DevSecOps
