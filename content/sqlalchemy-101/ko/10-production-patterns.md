---
title: "SQLAlchemy 101 (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포"
series: sqlalchemy-101
episode: 10
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
- SQLAlchemy
- Production
- pool
- Observability
- SQLite
last_reviewed: '2026-05-12'
seo_description: 풀, 관측, 마이그레이션, 배포 순서로 SQLAlchemy 운영 기본기를 정리합니다
---

# SQLAlchemy 101 (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포

프로덕션 환경에서 SQLAlchemy 문제는 대개 쿼리 문법보다 운영 경계에서 터집니다. 연결 풀 크기가 맞지 않아 지연이 커지고, stale connection을 방치해 새벽에 5xx가 나고, 마이그레이션 순서를 잘못 잡아 배포 직후 장애가 생기는 식입니다.

이 글은 SQLAlchemy 101 시리즈의 마지막 글입니다. 여기서는 풀, 관측, 재시도, 마이그레이션, 배포 순서를 기준으로 운영 패턴을 정리합니다.

앞선 아홉 편이 SQLAlchemy를 정확하게 쓰는 방법을 다뤘다면, 이번 글은 그 코드를 오래 안전하게 운영하는 방법을 다룹니다. SQLite 예제를 쓰지만, 여기서 잡는 감각은 PostgreSQL과 MySQL 환경으로도 그대로 이어집니다.

![프로덕션 패턴: 풀, 관측, 마이그레이션, 배포](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/10/10-01-production-patterns-pools-observability.ko.png)

*프로덕션 패턴: 풀, 관측, 마이그레이션, 배포*

## 먼저 던지는 질문

- connection pool은 어떤 기준으로 크기와 재사용 정책을 정해야 할까요?
- `pool_pre_ping`, `pool_recycle`은 어떤 장애를 줄여 줄까요?
- N+1 회귀나 느린 쿼리를 운영에서 어떻게 관측할 수 있을까요?

## 큰 그림

![SQLAlchemy 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/10/10-02-why-this-matters.ko.png)

*SQLAlchemy 101 10장 흐름 개요*

이 그림에서는 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

지금까지 다룬 내용은 모두 "코드가 정확히 동작하는가"였습니다. production은 한 단계 더 나갑니다. 같은 코드라도 풀 사이즈가 잘못되면 동시성에서 무너지고, 관측이 없으면 어디가 느린지 모르고, 마이그레이션 순서를 잘못 잡으면 배포 한 번이 장애가 됩니다.

이 글은 그 한 층 위의 결정들을 정리합니다. SQLite를 예로 쓰지만 대부분의 패턴은 PostgreSQL/MySQL에도 그대로 적용됩니다.

## 멘탈 모델

![Mental model](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/10/10-03-mental-model.ko.png)

*멘탈 모델*
> 프로덕션 SQLAlchemy는 세 개의 손잡이로 조율합니다. 풀은 동시성과 지연 시간을, 관측은 병목 지점을, 마이그레이션 정책은 배포의 안전선을 결정합니다. 셋 중 하나라도 비면 다른 둘의 효과가 크게 줄어듭니다.

풀이 너무 작으면 요청이 큐에서 기다리고, 너무 크면 DB 측 connection 한계를 넘습니다. 관측이 없으면 풀이 잘못됐다는 사실 자체를 모르고, 마이그레이션 정책이 없으면 슬프게도 "배포 직후 5분"이 단골 장애 시간이 됩니다.

## 핵심 개념

![핵심 개념](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/10/10-04-core-concepts.ko.png)

*핵심 개념*
### Pool 옵션

| 옵션 | 의미 | 권장 시작값 |
| --- | --- | --- |
| `pool_size` | 평상시 유지하는 connection 수 | 5–20 (서비스 크기에 따라) |
| `max_overflow` | 급증 시 추가로 열 수 있는 수 | `pool_size`와 동일 |
| `pool_pre_ping` | 사용 전 SELECT 1로 죽은 connection 검사 | True |
| `pool_recycle` | N초 지난 connection은 재사용 전 닫음 | 1800 (DB idle timeout 보다 짧게) |
| `pool_timeout` | 풀에서 기다리는 최대 시간 | 10–30초 |

### Pool 종류

- **`QueuePool`**(기본): 일반적인 동기 web 서버.
- **`NullPool`**: 단발성 스크립트, lambda 같은 환경. 매번 새 connection.
- **`StaticPool`**: 단일 connection을 여러 곳에서 공유. SQLite + 다중 thread 테스트에서 자주 씀.

### SQLite의 특수성

SQLite는 단일 writer DB입니다. file lock으로 직렬화되며, 큰 풀은 의미가 없습니다. 보통 `StaticPool` + `check_same_thread=False`로 쓰거나, async에서는 `aiosqlite` 기본 풀을 그대로 사용합니다.

### 관측

`event.listens_for(engine, "before_cursor_execute" / "after_cursor_execute")`로 직접 시간을 잴 수도 있고, OpenTelemetry의 `SQLAlchemyInstrumentor`를 쓰면 트레이스가 자동으로 붙습니다.

## 이전 방식과 개선 방식

```python
# Before: 기본값으로 만들어 버린 엔진
engine = create_engine(DATABASE_URL)
# 풀, pre-ping, recycle, 관측 모두 기본 → 새벽에 stale connection으로 5xx
```

```python
# After: production 기본기
from sqlalchemy import create_engine, event
import time, logging

log = logging.getLogger("db.slow")

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=30,
    future=True,
)

SLOW_MS = 200

@event.listens_for(engine, "before_cursor_execute")
def _t0(conn, cursor, stmt, params, ctx, many):
    ctx._t0 = time.perf_counter()

@event.listens_for(engine, "after_cursor_execute")
def _t1(conn, cursor, stmt, params, ctx, many):
    ms = (time.perf_counter() - ctx._t0) * 1000
    if ms >= SLOW_MS:
        log.warning("slow %.1fms %s", ms, stmt[:200])
```

After는 (1) connection이 죽어도 다음 요청에서 자동 회복(`pool_pre_ping`), (2) idle 30분 넘으면 재사용 안 함(`pool_recycle`), (3) 200ms 이상 쿼리는 별도 로거에 남깁니다.

## 단계별 실습

![단계별 실습](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/10/10-05-step-by-step-walkthrough.ko.png)

*단계별 실습*
### 1단계: 풀 크기 정하기

대략 `(평균 동시 요청 수) × (요청당 평균 connection 보유 시간 / 총 처리 시간)`이 시작점입니다. 보통 web 서버 1프로세스당 5–20이면 충분하고, 모자라면 `pool_size`를 키우는 대신 worker 프로세스 수로 늘리는 것이 안전합니다.

### 2단계: pre-ping과 recycle

DB 쪽 idle timeout(예: PostgreSQL 8h, MySQL 8h, 로드밸런서 5분)보다 `pool_recycle`을 짧게 잡습니다. `pool_pre_ping=True`는 거의 항상 켭니다.

### 3단계: 쿼리 카운터로 N+1 회귀 막기

8편에서 만든 `before_cursor_execute` 카운터를 테스트에 묶습니다.

```python
def test_no_n_plus_one(session):
    counter["n"] = 0
    result = list_users_with_posts(session)  # selectinload 사용
    assert counter["n"] <= 2  # users SELECT + posts IN-SELECT
```

`selectinload`를 빼고 다시 돌리면 카운터가 늘어 회귀가 즉시 보입니다.

### 4단계: OpenTelemetry로 trace 연결

```python
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

SQLAlchemyInstrumentor().instrument(engine=engine)
```

이제 모든 SQL이 현재 trace span의 자식으로 붙어, "이 요청에서 어떤 SQL이 얼마나 걸렸는가"를 그대로 봅니다.

### 5단계: transient 에러 retry

```python
import tenacity

@tenacity.retry(
    retry=tenacity.retry_if_exception_type(OperationalError),
    wait=tenacity.wait_exponential(multiplier=0.1, max=2),
    stop=tenacity.stop_after_attempt(3),
)
def write_with_retry(session, obj):
    session.add(obj)
    session.commit()
```

원격 DB의 일시적 단절, SQLite의 `SQLITE_BUSY`처럼 "다시 시도하면 된다"가 분명한 에러에만 적용합니다. business 에러는 절대 retry하지 않습니다.

### 6단계: 마이그레이션과 배포 순서

기본 원칙은 **마이그레이션이 먼저, 코드가 나중**입니다. 컬럼 추가/삭제로 나누면 다음과 같습니다.

- **컬럼 추가**: (1) nullable로 컬럼 추가 마이그레이션 → (2) 새 컬럼을 쓰는 코드 배포 → (3) (필요 시) NOT NULL로 마이그레이션 한 번 더.
- **컬럼 삭제**: (1) 코드에서 컬럼 사용 제거 후 배포 → (2) 다음 release에서 컬럼 drop 마이그레이션. 절대 같은 배포에서 하지 않습니다.

이 패턴은 alembic-101에서 본격적으로 다룹니다.

## 자주 하는 실수

- **`pool_size`만 키우기.** DB 측 max_connections를 같이 보지 않으면 어느 순간 DB가 거부합니다.
- **`pool_pre_ping`을 끄고 stale connection으로 새벽 5xx.** 켜지 않을 이유가 거의 없습니다.
- **모든 예외에 대해 retry.** integrity error, validation error는 다시 시도해도 똑같이 실패합니다. 명시적 화이트리스트로만.
- **마이그레이션과 코드 배포를 같은 step에 묶기.** rollback 경로가 사라집니다.
- **slow query 임계를 너무 낮게.** 200ms를 의미 있는 신호로 잡고, 점진적으로 50ms까지 좁히는 식으로.
- **SQLite production에 `QueuePool`을 그대로.** SQLite는 어차피 단일 writer라, 큰 풀은 false sense of concurrency를 줄 뿐입니다.

## 실무에서 쓰는 패턴

- **engine은 프로세스당 하나.** 모듈 import 시 만들고, 라이프사이클 종료 시 `dispose()`.
- **session은 요청·작업 단위.** dependency / context manager로 강제.
- **트랜잭션은 짧게.** 외부 HTTP 호출, 큰 계산은 트랜잭션 밖에서.
- **헬스체크는 `SELECT 1`을 짧은 timeout으로.** kubernetes liveness/readiness에 직접 연결.
- **schema 마이그레이션 전용 IAM/계정 분리.** 일반 워크로드 계정으로 DDL을 못 치게 막아 사고 방지.
- **slow query log + APM trace + alert** 세 축이 갖춰지면 대부분의 회귀를 사전에 잡습니다.

## 체크리스트

- [ ] `pool_size`, `max_overflow`, `pool_pre_ping`, `pool_recycle`, `pool_timeout`을 명시했다
- [ ] DB의 max_connections를 풀 합계로 넘지 않는다
- [ ] slow query 로깅이 있다(임계 200ms 같은 시작값)
- [ ] OpenTelemetry나 동등한 trace에 SQL이 연결된다
- [ ] retry는 `OperationalError`/`SQLITE_BUSY` 같은 transient에만, max 3회
- [ ] 마이그레이션과 코드 배포를 같은 step에 묶지 않는다
- [ ] engine은 프로세스당 하나, 종료 시 `dispose()`를 호출한다

## 정리, 다음 글

production 운영의 결정은 풀, 관측, 마이그레이션 세 축으로 좁혀집니다. 이 셋을 일찍 정해 두면 문제가 발생했을 때 추적 가능한 시스템이 되고, 늦게 정하면 매번 야간 배포로 메우게 됩니다.

이 시리즈는 여기서 마무리합니다. 다음 시리즈인 **alembic-101**에서는 이 글의 마이그레이션 정책을 구체적인 명령과 워크플로우로 풀어냅니다(`autogenerate`, branch와 merge, 데이터 마이그레이션, downgrade 전략).

## 운영 앵커: 풀 튜닝을 수치로 시작하기

풀 설정은 감으로 정하면 실패합니다. 최소한 다음 네 값을 먼저 측정한 뒤 시작합니다.

- 초당 요청 수(RPS)
- 요청당 평균 DB 시간(ms)
- 애플리케이션 워커 수
- DB 서버의 max connections

초기 `pool_size`는 보통 워커당 5~10으로 시작하고, `pool_timeout` 경고가 관측되면 증가를 검토합니다. 반대로 DB CPU가 높은데 대기 시간은 짧다면 풀 크기를 줄여 과도한 동시성을 낮추는 편이 안정적입니다.

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=8,
    max_overflow=8,
    pool_timeout=20,
    pool_pre_ping=True,
    pool_recycle=1800,
)
```

## 세션 수명과 트랜잭션 길이 제어

운영 장애의 절반은 긴 트랜잭션에서 시작합니다. 아래 두 규칙을 강제하면 효과가 큽니다.

- 외부 HTTP 호출 전에는 트랜잭션 종료
- 대량 루프는 배치 단위 commit

```python
with SessionLocal() as session:
    while batch := read_batch():
        with session.begin():
            for item in batch:
                apply_change(session, item)
```

트랜잭션을 짧게 유지하면 락 유지 시간이 줄고, 실패 시 롤백 비용도 작아집니다.

## SQL echo에서 운영 로그로 전환

학습 단계의 `echo=True`는 유용하지만 프로덕션에서는 과합니다. 대신 이벤트 기반 구조화 로그를 권장합니다.

```python
@event.listens_for(engine, "before_cursor_execute")
def _start(conn, cursor, statement, params, context, executemany):
    context._t0 = time.perf_counter()

@event.listens_for(engine, "after_cursor_execute")
def _end(conn, cursor, statement, params, context, executemany):
    ms = (time.perf_counter() - context._t0) * 1000
    logger.info("sql_ms=%.1f rows=%s stmt=%s", ms, cursor.rowcount, statement[:140])
```

이 로그를 OpenTelemetry trace id와 묶으면 "느린 요청 -> 느린 SQL" 경로를 바로 따라갈 수 있습니다.

## N+1 회귀 방지 파이프라인

7편에서 다룬 N+1은 운영 이전 CI에서 막아야 합니다. 다음 두 단계를 파이프라인에 넣으면 회귀율이 크게 줄어듭니다.

1. 핵심 엔드포인트 통합 테스트에 쿼리 수 assertion 추가
2. 기준치를 넘는 경우 PR 실패 처리

```python
def assert_query_budget(run_fn, max_queries: int):
    counter["n"] = 0
    run_fn()
    assert counter["n"] <= max_queries
```

쿼리 수 예산은 제품 기능이 바뀌면 조정할 수 있지만, "예산이 있다는 사실" 자체가 품질을 지켜 줍니다.

## 마이그레이션 배포 상세 시나리오

컬럼 추가 사례를 실제 순서로 풀면 다음과 같습니다.

- Release A: `users.display_name` nullable 컬럼 추가
- Release B: 애플리케이션이 `display_name`을 읽되, 없으면 `name` fallback
- Release C: 백필 배치 실행
- Release D: `display_name` NOT NULL 변경
- Release E: `name` 제거(필요 시)

이 다단계 전략의 목적은 "구버전 코드와 신버전 스키마가 한동안 공존"해도 깨지지 않게 만드는 것입니다.

## 롤백 전략

배포 실패 시 가장 먼저 필요한 것은 롤백 경로입니다.

- 코드 롤백 가능 여부
- 스키마 downgrade 가능 여부
- 데이터 변환이 비가역인지 여부

특히 데이터 변환이 비가역이면, 스키마 downgrade보다 "forward-fix" 전략이 현실적일 때가 많습니다. 이 판단을 릴리스 노트에 미리 적어 두면 온콜 대응 속도가 올라갑니다.

## 운영 체크 대시보드 제안

SQLAlchemy 기반 서비스라면 최소한 다음 패널이 필요합니다.

- 요청당 평균 SQL 개수
- P95/P99 SQL latency
- 풀 체크아웃 대기 시간
- `OperationalError` 비율
- 롤백 비율
- 느린 쿼리 상위 20개

대시보드가 있어야 `pool_size`를 늘릴지, 인덱스를 추가할지, N+1을 고칠지 의사결정을 데이터로 할 수 있습니다.

## SQLite에서 PostgreSQL로 넘어갈 신호

다음 징후가 보이면 SQLite 유지보다 전환 비용이 더 낮아지는 구간입니다.

- write 동시성이 자주 `SQLITE_BUSY`를 유발
- 대규모 조인/집계 쿼리가 늘어남
- 다중 워커에서 파일 락 경합이 반복
- 운영 백업/복구 RTO 요구가 커짐

이때 SQLAlchemy의 장점은 큽니다. 엔진 URL과 일부 dialect 옵션만 조정하면 애플리케이션 계층 코드는 대부분 유지됩니다.

## 시리즈 전체 회고

1편의 Engine/Connection부터 10편의 운영까지 흐름을 하나로 묶으면 다음 문장으로 정리됩니다.

- Core로 SQL 경계를 명시한다
- ORM으로 도메인 모델을 표현한다
- Session으로 트랜잭션 단위를 통제한다
- 로딩 전략으로 쿼리 비용을 설계한다
- 이벤트/타입 확장으로 규칙 위치를 고정한다
- 운영에서는 풀·관측·마이그레이션을 자동화한다

이 원칙을 팀 표준으로 옮기면, SQLAlchemy는 개인 취향 도구가 아니라 조직의 예측 가능한 데이터 계층이 됩니다.

## 보강 앵커: 운영 런북 템플릿

온콜 대응 속도를 높이려면 런북이 코드만큼 중요합니다. SQLAlchemy 서비스용 최소 런북 항목은 다음과 같습니다.

1. 장애 증상: 타임아웃, 5xx, 롤백 급증
2. 즉시 확인: DB 연결 가능 여부, 풀 체크아웃 대기, 느린 쿼리 상위
3. 임시 완화: 워커 축소/확대, 특정 엔드포인트 차단, 재시도 완화
4. 근본 원인 분석: N+1 회귀, 인덱스 누락, 마이그레이션 불일치
5. 재발 방지: 테스트 예산 강화, 대시보드 경보 추가

이 문서가 있으면 새벽 장애에서 "어디부터 볼지"를 팀 전체가 같은 순서로 맞출 수 있습니다.

## 보강 앵커: 배포 전 점검 자동화

배포 파이프라인에서 다음 스크립트를 자동화하면 사고율이 크게 낮아집니다.

```bash
python scripts/check_migrations.py
python scripts/check_query_budget.py
python scripts/check_slow_sql_patterns.py
```

핵심은 사람이 배포 전마다 기억에 의존하지 않는 것입니다. SQLAlchemy 운영은 자동화 체크리스트와 결합될 때 가장 안정적입니다.

## 보강 앵커: 마이그레이션 실패 복구 절차

마이그레이션 실패 시 즉시 적용할 절차를 미리 합의해 두십시오.

- 스키마 변경이 부분 적용됐는지 확인
- 애플리케이션 버전을 즉시 이전 버전으로 되돌릴지 결정
- downgrade 가능하면 실행, 불가하면 forward-fix 계획 수립
- 데이터 무결성 검사 쿼리 실행
- 장애 타임라인 기록

실제 장애에서 시간이 걸리는 것은 기술보다 의사결정입니다. 절차를 미리 정해 두면 복구 시간이 크게 단축됩니다.

## 보강 앵커: 성능 회귀 기준선 만들기

운영 직전에는 반드시 기준선 벤치마크를 남겨 두어야 합니다.

- 주요 API별 평균 SQL 개수
- P95 쿼리 지연
- 풀 대기 시간
- 초당 커밋 수

이 값이 있어야 "이번 릴리스가 느려졌는가"를 객관적으로 판단할 수 있습니다. 기준선 없는 최적화는 대부분 감에 의존한 변경으로 끝납니다.

## 보강 앵커: 예시 운영 설정 스니펫

다음은 Flask/FastAPI 공통으로 자주 쓰는 SQLAlchemy 운영 설정 골격입니다.

```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.getenv("DB_POOL_SIZE", "8")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "8")),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "20")),
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=True)
```

환경 변수로 설정을 외부화해 두면 릴리스마다 코드 수정 없이 운영 파라미터를 조정할 수 있습니다.

## 보강 앵커: 장애 후 회고 질문

장애를 겪은 뒤 팀이 같은 질문을 반복하면 품질이 빨리 올라갑니다.

- 이번 장애는 쿼리 설계 문제인가, 풀 설정 문제인가, 마이그레이션 순서 문제인가
- 사전에 감지할 지표가 있었는가
- 테스트에서 재현 가능한가
- 자동화 체크리스트에 어떤 항목을 추가할 것인가

기술 개선의 핵심은 코드 변경보다 재발 방지 루프입니다. SQLAlchemy 운영도 예외가 아닙니다.

## 보강 앵커: book-examples 연계 운영 연습

실전 연습은 `book-examples`의 시리즈 예제를 기반으로 다음을 반복하는 방식이 효과적입니다.

1. 의도적으로 N+1을 만들고 query budget 테스트를 실패시킨다
2. `selectinload`로 수정해 테스트를 복구한다
3. 느린 쿼리 로깅 임계를 바꿔 알림 민감도를 조정한다
4. mock 마이그레이션 롤백 시나리오를 실행한다

이 훈련을 한 번 해 본 팀과 그렇지 않은 팀의 배포 안정성 차이는 생각보다 큽니다.

운영 안정성은 결국 반복 가능한 절차에서 나옵니다. 풀 설정, 쿼리 관측, 마이그레이션 순서를 문서와 자동화로 고정하면 인력 변화가 있어도 품질이 유지됩니다.

결론적으로 운영 패턴은 취향이 아니라 계약입니다. 팀의 기본 계약으로 문서화하고 자동 검증까지 묶어 두어야 배포 안정성이 올라갑니다.

운영 계약이 명확할수록 장애 복구 시간은 짧아집니다.

운영 자동화와 회고 루프가 함께 돌아갈 때 SQLAlchemy 스택은 장기적으로 안정화됩니다.

운영 표준은 지속적으로 개선되어야 합니다.

## 처음 질문으로 돌아가기

- **connection pool은 어떤 기준으로 크기와 재사용 정책을 정해야 할까요?**
  - 본문의 기준은 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`pool_pre_ping`, `pool_recycle`은 어떤 장애를 줄여 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **N+1 회귀나 느린 쿼리를 운영에서 어떻게 관측할 수 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQLAlchemy 101 (1/10): SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질](./01-sqlalchemy-2x-engine-connection.md)
- [SQLAlchemy 101 (2/10): SQLAlchemy Core - MetaData, Table, Column으로 schema를 Python 객체로 만들기](./02-core-metadata-table-types.md)
- [SQLAlchemy 101 (3/10): SQLAlchemy Core - select·insert·update·delete를 2.x style로 다루기](./03-core-select-insert-update-delete.md)
- [SQLAlchemy 101 (4/10): ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기](./04-orm-declarative-mapped-column.md)
- [SQLAlchemy 101 (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리](./05-session-unit-of-work-identity-map.md)
- [SQLAlchemy 101 (6/10): ORM 관계 매핑: relationship과 back_populates로 양방향 탐색 안전하게 잇기](./06-relationships-back-populates.md)
- [SQLAlchemy 101 (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가](./07-loading-strategies-n-plus-one.md)
- [SQLAlchemy 101 (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입](./08-events-hybrid-types.md)
- [SQLAlchemy 101 (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession](./09-async-aiosqlite.md)
- **SQLAlchemy 101 (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포 (현재 글)**

<!-- toc:end -->

## 참고 자료

- SQLAlchemy: Connection Pooling — https://docs.sqlalchemy.org/en/20/core/pooling.html
- SQLAlchemy: Engine Configuration — https://docs.sqlalchemy.org/en/20/core/engines.html
- OpenTelemetry SQLAlchemy instrumentation — https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/sqlalchemy/sqlalchemy.html
- Tenacity — https://tenacity.readthedocs.io/

Tags: Python, SQLAlchemy, ORM, Database
