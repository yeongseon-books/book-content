---
title: "Alembic 101 (9/10): 배포 순서와 blue/green: schema와 application code의 안전한 동기화"
series: alembic-101
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
- Python
- Alembic
- deploy
- blue-green
- ordering
- SQLite
last_reviewed: '2026-05-12'
seo_description: migration은 항상 "코드보다 먼저, 그리고 코드보다 호환성이 넓게"입니다.
---

# Alembic 101 (9/10): 배포 순서와 blue/green: schema와 application code의 안전한 동기화

이 글은 Alembic 101 시리즈의 아홉 번째 글입니다. 여기서는 migration과 application code를 어떤 순서로 배포해야 안전한지, 그리고 blue/green 환경에서 schema 호환성을 어떻게 설계해야 하는지 정리합니다.

많은 schema 사고는 migration 코드 자체보다 deploy ordering에서 시작됩니다. 특히 blue/green이나 rolling 환경에서는 두 버전의 앱이 같은 DB를 동시에 사용하므로, schema는 항상 그 두 버전 모두와 호환되어야 합니다.


![Alembic 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/09/09-01-diagram-the-blue-green-compatibility-win.ko.png)
*Alembic 101 9장 흐름 개요*

## 먼저 던지는 질문

- migration-first와 code-first deploy ordering은 어떻게 다를까요?
- 왜 blue/green deploy는 두 앱 버전과 동시에 호환되는 schema를 요구할까요?
- NOT NULL 강화는 왜 두 단계로 나눠야 할까요?

## 왜 중요한가

production schema 사고의 상당수는 코드와 schema가 잘못된 순서로 배포될 때 발생합니다. 새 컬럼이 코드보다 먼저 존재하면 안전하지만, 코드가 새 컬럼을 먼저 가정하고 schema가 뒤따라오면 즉시 500 에러가 납니다. blue/green에서는 v1과 v2가 동시에 같은 schema를 읽고 쓰므로, schema는 전환 구간 내내 양쪽을 모두 수용해야 합니다.

## 멘탈 모델

> migration은 항상 **“코드보다 먼저, 그리고 코드보다 더 넓은 호환성으로”** 배포됩니다. 컬럼을 추가할 때는 컬럼이 먼저 존재해야 하고, 컬럼을 제거할 때는 코드가 먼저 사용을 멈춰야 합니다. 이 두 방향만 기억해도 deploy 사고 대부분을 피할 수 있습니다.

git 비유로 보면 migration은 코드 PR보다 먼저 들어가는 PR이고, drop은 “이 컬럼 사용을 중단한다”는 코드 PR보다 나중에 들어가는 PR입니다.

### 다이어그램: blue/green에서 schema가 두 버전을 동시에 받아야 하는 시점

## 핵심 개념

### migration-first vs code-first

| 변경 종류 | 배포 순서 | 이유 |
| --- | --- | --- |
| **Add column / table** | migration → code | 코드는 새 컬럼이 이미 존재해야 쓸 수 있다 |
| **Drop column / table** | code → migration | 코드가 사용을 멈춘 뒤에 drop해야 안전하다 |
| **Type widen** (`String(50)` → `String(100)`) | migration → code | 더 큰 값을 저장할 수 있어야 코드가 쓸 수 있다 |
| **Type narrow** | code → migration | 코드가 작은 값만 쓰기 시작한 뒤에 줄여야 한다 |

전환 중에도 이전 버전 코드가 계속 살아 있어야 한다는 점이 가장 중요합니다. 이것이 blue/green과 롤링 배포의 기본 가정입니다.

### blue/green에서의 schema 호환성

```text
t0: only blue (v1) running, schema=S1
t1: migrate schema to S2 (S1, S2 both compatible with v1)
t2: bring up green (v2); blue (v1) and green (v2) run concurrently (both work with S2)
t3: shut down blue, only green runs
t4 (next deploy): migrate schema to S3 (now safe to drop S2 compatibility)
```

t1에서 적용하는 schema는 반드시 v1과 v2 모두를 받아야 합니다. 그래서 expand-contract가 사실상 필수입니다.

### NOT NULL 강화는 2단계로

`nullable=False`를 한 revision에 몰아넣으면 blue/green 전환 중 즉시 사고가 날 수 있습니다. 두 단계로 분리해야 합니다.

```text
phase 1 (now):
  - DB: add column as nullable=True with a default
  - code: always writes a value into the new column
  - deploy: migration → code

gate before phase 2:
  - query: SELECT COUNT(*) FROM users WHERE phone IS NULL
  - pass: null_count == 0
  - fail: null_count > 0, stop the tighten revision and keep backfilling

phase 2 (next deploy):
  - DB: tighten column to nullable=False
  - code: unchanged
  - deploy: migration only
```

여기서 `users.phone`이 예시 흐름입니다. v2가 `phone` 값을 쓰기 시작한 뒤에도 과거 row에는 NULL이 남아 있을 수 있으므로, phase 2는 `null_count == 0` 게이트를 통과한 다음에만 적용해야 합니다.

### column rename의 4단계

```text
phase 1: add new column (nullable=True); code keeps using the old column
phase 2: code dual-writes (writes both old and new)
phase 3: backfill data; code reads and writes only the new column
phase 4: drop the old column (code already stopped using it)
```

각 phase는 독립 PR로 가져가고, phase 사이마다 production 안정성을 확인해야 합니다. 느리지만 가장 안전한 패턴입니다.

### 전환 후반부 rollout 상태표

`users.phone`처럼 add → write → tighten 순서가 필요한 변경은 전환 후반부에 현재 상태를 표로 보면서 판단하는 편이 안전합니다.

| 단계 | DB shape | 코드 동작 | 허용되는 다음 액션 |
| --- | --- | --- | --- |
| expand revision 적용 직후 | `phone` exists, nullable | v1은 무시, v2는 아직 배포 전 | v2 배포 |
| blue/green overlap | `phone` exists, nullable | v1은 무시, v2는 `phone`에 write | NULL row 수 확인, backfill 계속 |
| tighten 직전 gate 통과 | `phone` exists, nullable, `NULL` 0건 | v2만 live, write path 안정화 | `nullable=False` tighten revision 적용 |
| contract 완료 후 | `phone` exists, NOT NULL | v2만 live, 모든 write/read가 `phone` 기준 | smoke test 후 다음 deploy cycle에서 old column drop 검토 |

### 여러 인스턴스에서 정확히 한 번 실행하기

모든 application instance가 `alembic upgrade`를 실행하면 race condition이 생깁니다. Alembic이 `alembic_version`에 lock을 걸긴 하지만, 더 안전한 방법은 다음 중 하나입니다.

- **deploy script가 한 번만 호출**: 앱 인스턴스가 뜨기 전에 별도 stage에서 migration 실행
- **Kubernetes Job / initContainer**: 전용 Job으로 앱 컨테이너보다 먼저 migration 수행
- **CI/CD pipeline 분리**: `deploy` 앞에 `migrate` stage 배치

application startup에서 `alembic upgrade head`를 호출하는 패턴은 단일 인스턴스 개발 환경에서는 괜찮지만 production에는 권장되지 않습니다.

## 변경 전후

```text
# Before: code-first deploy, immediate 500 errors
1. deploy v2 (code that uses the new column)
2. every request fails with "no such column"
3. 30 minutes later, schema migrate
```

```text
# After: migration-first deploy
1. schema migrate (add new column as nullable=True)
2. v1 instances keep running normally (they ignore the new column)
3. deploy v2 (code that uses the new column)
4. blue/green both work correctly
```

After 패턴은 전환 구간 내내 v1과 v2가 모두 해석 가능한 schema를 유지하게 해 줍니다. 여기에 NULL 게이트와 smoke test까지 붙이면 tighten 시점을 근거 있게 결정할 수 있습니다.

## 단계별 실습

### 1단계: schema add

```python
# revision: add_users_phone
def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(20), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "phone")
```

먼저 CI/CD에서 이 migration을 적용합니다. 아직 application code는 `phone`을 건드리지 않습니다. v1과 v2 모두 안전합니다.

### 2단계: code deploy

이제 application code가 `phone`에 값을 쓰기 시작합니다. blue/green 전환 구간에서 v1은 이 컬럼을 무시하고, v2는 채우기만 하므로 두 버전 모두 안전합니다.

### 3단계: NOT NULL 강화

모든 row에 `phone`이 채워졌는지 확인한 뒤 schema를 조입니다.

```python
# revision: tighten_users_phone_not_null
def upgrade() -> None:
    bind = op.get_bind()
    null_count = bind.execute(text("SELECT COUNT(*) FROM users WHERE phone IS NULL")).scalar()
    assert null_count == 0, f"{null_count} rows still NULL"
    with op.batch_alter_table("users") as batch:
        batch.alter_column("phone", existing_type=sa.String(20), nullable=False)

def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("phone", existing_type=sa.String(20), nullable=True)
```

assertion이 마지막 안전망입니다. NULL이 남아 있으면 migration은 실패하고 schema는 바뀌지 않습니다.

### 4단계: old column drop

이전 컬럼을 제거할 때는 application code가 더 이상 쓰지 않는다는 사실을 확인하고, 다음 deploy cycle에서 내립니다.

```python
def upgrade() -> None:
    op.drop_column("users", "old_phone")

def downgrade() -> None:
    raise NotImplementedError("drop is irreversible")
```

### 5단계: deploy pipeline 정렬

```yaml
# CI/CD
stages:
  - test
  - migrate     # alembic upgrade head
  - deploy      # rolling update
  - smoke-test
```

`migrate`가 항상 `deploy`보다 먼저 오도록 강제해야 합니다.

## cutover runbook

```bash
set -euo pipefail

export DATABASE_URL="postgresql+psycopg://app:secret@db/prod"
export GREEN_DEPLOYMENT="api-green"
export RELEASE_IMAGE="ghcr.io/acme/api:v2"
export HEALTH_URL="https://api.example.com/health"

echo "[1/5] apply expand revision"
alembic upgrade add_users_phone

echo "[2/5] deploy the app version that writes users.phone"
kubectl set image deployment/"$GREEN_DEPLOYMENT" api="${RELEASE_IMAGE}"
kubectl rollout status deployment/"$GREEN_DEPLOYMENT" --timeout=180s

echo "[3/5] block contract until users.phone has no NULL rows"
NULL_COUNT="$({ python3 - <<'PY'
import os
from sqlalchemy import create_engine, text

engine = create_engine(os.environ["DATABASE_URL"])
with engine.connect() as conn:
    count = conn.execute(text("SELECT COUNT(*) FROM users WHERE phone IS NULL")).scalar_one()
print(count)
PY
})"
[ "$NULL_COUNT" = "0" ] || {
  echo "Fail: users.phone still has $NULL_COUNT NULL rows; do not run tighten_users_phone_not_null"
  exit 1
}
echo "Pass: users.phone NULL rows = $NULL_COUNT"

echo "[4/5] apply tighten revision"
alembic upgrade tighten_users_phone_not_null

echo "[5/5] smoke test the live service"
HEALTH_BODY="$(curl -fsS "$HEALTH_URL")"
export HEALTH_BODY
python3 - <<'PY'
import json
import os

payload = json.loads(os.environ["HEALTH_BODY"])
assert payload["status"] == "ok", payload
print(f"Pass: status={payload['status']} alembic_version={payload.get('alembic_version', 'unknown')}")
PY
```

예상되는 관찰 신호는 다음과 같습니다.

- `[3/5]`에서 `Pass: users.phone NULL rows = 0`가 나오지 않으면 즉시 실패하고 tighten revision은 실행되지 않습니다.
- `kubectl rollout status`가 완료되기 전까지는 cutover를 진행하지 않습니다.
- 마지막 Python 검증은 `/health`가 `status=ok`를 반환해야 Pass입니다.

### blue/green 사고 시 first checks

장애가 나면 원인 추적 전에 다음 네 가지부터 확인합니다.

1. `migrate` stage가 실제로 `deploy`보다 먼저 실행됐는가?
2. 지금 live인 애플리케이션 버전이 v1인가, v2인가?
3. `tighten_users_phone_not_null` revision이 이미 적용됐는가?
4. `SELECT COUNT(*) FROM users WHERE phone IS NULL` 결과가 몇 건인가?

이 네 질문만 빠르게 답해도 문제를 `배포 순서`, `앱 버전`, `schema tighten`, `데이터 미완료` 중 어디서 찾아야 하는지 바로 좁힐 수 있습니다.

## 자주 하는 실수

- **code-first deploy.** 코드가 새 schema를 먼저 가정하면 즉시 실패합니다.
- **NOT NULL을 한 revision에 묶기.** blue/green에서 이전 버전이 NULL을 쓰는 순간 사고가 납니다.
- **컬럼을 즉시 drop하기.** 코드가 사용을 멈췄더라도 최소 한 deploy cycle은 기다리는 편이 안전합니다.
- **application startup에서 `alembic upgrade head`를 호출하기.** multi-instance 환경에서는 race와 partial application 리스크가 큽니다.
- **rename을 한 번에 처리하기.** 실제로는 drop+add와 다르지 않아서 데이터 손실 위험이 큽니다.

## 실무 패턴

- **CI/CD stage를 `migrate` → `deploy`로 고정합니다.** 가장 단순하고 효과적인 규칙입니다.
- **NOT NULL 강화는 항상 두 단계로 나눕니다.** 중간에 data verification을 넣습니다.
- **drop은 한 deploy cycle 늦춥니다.** 즉시 제거는 피합니다.
- **Kubernetes에서는 Job이나 initContainer로 exactly-once execution을 보장합니다.**
- **deploy 전 `alembic check`를 실행합니다.** model/schema drift를 자동 탐지합니다.
- **PR 템플릿에 expand-contract phase를 적게 합니다.** 지금 이 변경이 어느 단계인지 항상 드러나게 만듭니다.

## 체크리스트

- [ ] schema add는 항상 code deploy보다 먼저 나간다
- [ ] schema drop은 코드가 사용을 멈춘 다음 deploy cycle에 나간다
- [ ] NOT NULL 강화는 두 단계로 분리했다
- [ ] rename은 dual-write 4단계를 따른다
- [ ] application startup에서 `alembic upgrade`를 호출하지 않는다
- [ ] CI/CD는 `migrate` 후 `deploy` 순서를 강제한다
- [ ] Kubernetes 환경에서는 Job 또는 initContainer로 exactly-once execution을 보장한다

## 연습 문제

1. add-column → code-deploy → NOT NULL tighten 흐름을 SQLite에서 끝까지 시뮬레이션해 보세요.
2. column rename을 4단계 dual-write 패턴으로 설계하고 phase별 PR 순서를 그려 보세요.
3. CI/CD pipeline을 `migrate` stage가 항상 `deploy`보다 먼저 오도록 바꿔 보세요.

## 정리, 다음 글

deploy ordering은 Alembic 기능이 아니라 운영 정책입니다. “schema first, broader compatibility”라는 한 문장을 머릿속에 두고, 모든 변경을 그 기준으로 분해해야 합니다. blue/green에서 가장 중요한 점은 전환 구간 내내 schema가 두 버전과 동시에 호환되어야 한다는 사실입니다.

다음 글에서는 팀 단위의 실제 workflow, 즉 PR 규칙, CI 체크, 모니터링, incident response를 다룹니다.

## revision 단계별 배포 게이트 예시

blue/green 운영에서는 "적용했다"보다 "다음 단계로 넘어가도 되는가"가 더 중요합니다. 아래 게이트를 배포 파이프라인에 명시하면 사람 판단 오차를 줄일 수 있습니다.

```text
Gate A (expand 직후)
- 새 컬럼/테이블 존재 확인
- 기존 v1 트래픽 에러율 변화 없음

Gate B (v2 배포 직후)
- v2에서 새 컬럼 write 성공
- v1/v2 혼재 구간에서 5xx 증가 없음

Gate C (tighten 직전)
- NULL row 수 0
- 읽기/쓰기 지연 정상 범위

Gate D (contract 직전)
- old column read path 제거 확인
- 최소 1 deploy cycle 동안 안정성 확인
```

이 게이트 체계는 expand-contract를 절차로 고정해 줍니다. 결과적으로 "일단 한 번에 내려 보자"식 배포를 줄일 수 있습니다.

## 애플리케이션 코드 diff 예시: dual-write 전환

schema만으로는 blue/green 호환성이 완성되지 않습니다. 코드 레벨에서 dual-write를 명시해야 합니다.

```python
# Before
user.name = payload["name"]

# During overlap (phase 2)
user.name = payload["name"]
user.display_name = payload["name"]

# After cutover (phase 3)
user.display_name = payload["name"]
```

읽기 경로도 같은 방식으로 점진 전환합니다.

```python
# overlap-safe read
name = user.display_name or user.name
```

이 한 줄이 전환 구간 장애를 크게 줄여 줍니다. 새 컬럼이 아직 완전히 채워지지 않은 상태에서도 v2가 안전하게 동작하기 때문입니다.

## 배포 실패 로그 예시와 해석

```text
sqlalchemy.exc.ProgrammingError: column users.phone does not exist
```

대개 `code-first` 배포입니다. 코드가 먼저 올라갔고 expand revision이 뒤따랐다는 신호입니다.

```text
AssertionError: 1243 rows still NULL
```

`tighten` 게이트가 정상 작동한 것입니다. 실패가 아니라 보호 장치가 제 역할을 한 상태입니다. 이 경우는 backfill을 더 수행한 뒤 재시도해야 합니다.


## 실전 부록: 운영 앵커 모음

아래 블록은 migration 리뷰와 배포 검증에서 반복해서 쓰는 공통 앵커입니다.

### 1) DDL 미리 보기

```bash
alembic upgrade <from>:<to> --sql > migration-preview.sql
```

리뷰 시점에서 실제 SQL을 확인하면 `DROP`, `ALTER`, 인덱스 재생성 비용을 사전에 파악할 수 있습니다.

### 2) revision 그래프 확인

```bash
alembic history --verbose
alembic heads
alembic current
```

`heads`가 2개 이상이면 기능 결함이 아니라 그래프 정리 이슈입니다. merge revision으로 정리한 뒤 배포해야 안전합니다.

### 3) schema 전후 비교

```bash
sqlite3 app.db ".schema" > before.sql
alembic upgrade head
sqlite3 app.db ".schema" > after.sql
```

변경 의도와 실제 결과를 텍스트로 남기면 코드 리뷰 품질이 올라갑니다.

### 4) data migration 검증 쿼리

```sql
SELECT COUNT(*) FROM users WHERE tier IS NULL;
SELECT tier, COUNT(*) FROM users GROUP BY tier ORDER BY tier;
```

`NULL` 잔여 수와 분포를 함께 보면 backfill 완료 여부를 빠르게 판단할 수 있습니다.

### 5) env.py 핵심 설정

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    compare_type=True,
    compare_server_default=True,
    render_as_batch=connection.dialect.name == "sqlite",
)
```

type/default 비교 옵션과 SQLite batch 옵션은 drift 탐지와 호환성 유지에 직접적인 영향을 줍니다.

### 6) blue/green 배포 게이트

```text
Gate A: expand 적용 후 v1 정상
Gate B: v2 배포 후 overlap 정상
Gate C: NULL row 0 확인 후 tighten
Gate D: 구 컬럼 사용 중단 확인 후 contract
```

게이트를 코드화하면 배포 순서 실수를 줄일 수 있습니다.

### 7) 비가역 변경 정책

```python
def downgrade() -> None:
    raise NotImplementedError("irreversible revision by policy")
```

비가역 변경에서 침묵하는 `pass`보다 명시적 예외가 훨씬 안전합니다.

### 8) CI 최소 게이트

```bash
alembic check
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

drift, downgrade 결함, 체인 무결성을 PR 단계에서 차단할 수 있습니다.

### 9) 에러 시그널 해석

```text
Multiple head revisions are present -> merge 필요
Can't locate revision identified by ... -> revision chain 점검 필요
table already exists -> baseline/stamp 전략 점검 필요
```

에러 유형별 대응 경로를 정해 두면 incident 대응 시간이 짧아집니다.

### 10) 팀 운영 원칙

```text
- one PR = one revision
- migration-first deploy
- expand-contract 기본 적용
- production 사고는 forward-fix 우선
```

원칙을 문서가 아니라 PR 템플릿과 CI로 강제하는 것이 핵심입니다.


## 확장 부록: 배포/복구 실습 시나리오

### 시나리오 A: add column + backfill + tighten

```bash
alembic revision -m "add users.phone nullable"
alembic revision -m "backfill users.phone"
alembic revision -m "tighten users.phone not null"
alembic upgrade head
```

```sql
SELECT COUNT(*) FROM users WHERE phone IS NULL;
```

`COUNT(*) = 0`이 아니라면 tighten 단계는 멈춰야 합니다.

### 시나리오 B: 동시에 생성된 head 정리

```bash
alembic heads
alembic merge -m "merge concurrent heads" <head1> <head2>
alembic heads
```

merge 후 head가 하나여야 합니다.

### 시나리오 C: offline SQL 승인 흐름

```bash
alembic upgrade <prev>:head --sql > review.sql
```

검토 포인트는 `DROP`, `ALTER`, 인덱스 재생성, `alembic_version` 갱신 SQL 포함 여부입니다.

### 시나리오 D: incident first checks

```bash
alembic current
alembic heads
```

```sql
SELECT version_num FROM alembic_version;
```

애플리케이션 `/health`의 기대 버전과 DB 버전이 다르면 drift 가능성을 먼저 의심합니다.

### 운영 스크립트 예시

```bash
set -euo pipefail
alembic check
alembic upgrade head
alembic upgrade head --sql > /tmp/migration-preview.sql
```

### 품질 게이트 정리

```text
- autogenerate 결과 수동 검토
- downgrade 정책 명시
- data migration idempotency 확보
- migration-first 배포
- post-deploy smoke test
```

이 게이트들은 Alembic 자체 기능이라기보다 팀 운영 안전장치입니다.


## 보강 메모: 검증 중심 운영 노트

Alembic 운영에서 가장 큰 차이는 "명령 실행"이 아니라 "검증 기록"입니다. 같은 `upgrade head`를 실행해도 검증 쿼리, SQL preview, head 개수 확인을 함께 남기면 문제 재현성이 크게 높아집니다.

```bash
alembic heads
alembic current
alembic upgrade head --sql > /tmp/ddl.sql
```

```sql
SELECT version_num FROM alembic_version;
```

또한 data migration이 포함된 경우에는 진행률을 관찰 가능한 숫자로 남겨야 합니다.

```sql
SELECT COUNT(*) FROM users WHERE tier IS NULL;
```

운영자는 이 숫자를 기준으로 tighten 단계 진행 여부를 결정해야 합니다. 값이 0이 아니면 단계 진행을 멈추고 backfill을 계속해야 합니다.

배포 실패 대응의 기본 원칙은 다음과 같습니다.

```text
1) 현재 revision 위치를 먼저 확정한다.
2) graph 상태(single head인지)를 확인한다.
3) backward-compatible 여부를 판단한다.
4) 가능하면 forward-fix revision으로 복구한다.
```

이 네 단계는 엔진(SQLite/PostgreSQL)과 무관하게 공통으로 적용됩니다.


## 처음 질문으로 돌아가기

- **migration-first와 code-first deploy ordering은 어떻게 다를까요?**
  - 본문의 기준은 배포 순서와 blue/green: schema와 application code의 안전한 동기화를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **왜 blue/green deploy는 두 앱 버전과 동시에 호환되는 schema를 요구할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **NOT NULL 강화는 왜 두 단계로 나눠야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Alembic 101 (1/10): 왜 Alembic인가, 그리고 init까지](./01-why-alembic-and-init.md)
- [Alembic 101 (2/10): env.py와 target_metadata: 모델과 마이그레이션 연결](./02-env-py-and-target-metadata.md)
- [Alembic 101 (3/10): 첫 revision: upgrade와 downgrade를 손으로 작성](./03-first-revision-upgrade-downgrade.md)
- [Alembic 101 (4/10): autogenerate: 잡는 것과 못 잡는 것의 경계](./04-autogenerate-and-its-limits.md)
- [Alembic 101 (5/10): branch와 merge: 동시에 만든 revision을 합치는 법](./05-branches-and-merges.md)
- [Alembic 101 (6/10): 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기](./06-data-migrations.md)
- [Alembic 101 (7/10): online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기](./07-online-vs-offline-and-batch.md)
- [Alembic 101 (8/10): downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가](./08-downgrade-strategy.md)
- **배포 순서와 blue/green: schema와 application code의 안전한 동기화 (현재 글)**
- Production과 team workflow: PR, CI, 모니터링, 그리고 incident response (예정)

<!-- toc:end -->

## 참고 자료

- [sqlalchemy/alembic GitHub 저장소](https://github.com/sqlalchemy/alembic)
- [Alembic: Cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html)
- [Martin Fowler: Blue Green Deployment](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- "Refactoring Databases" by Scott Ambler & Pramod Sadalage
- [Kubernetes: Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/09-deploy-ordering-and-blue-green)

Tags: Python, Alembic, SQLAlchemy, Migration
