---
episode: 10
language: ko
last_reviewed: '2026-05-03'
series: python-dbapi-101
status: publish-ready
tags:
- Python
- SQLite
- Production
- Observability
- OpenTelemetry
- Retry
targets:
  ebook: true
  hashnode: true
  medium: true
  mkdocs: true
  tistory: true
title: 'SQLite Production 패턴: retry, timeout, 관측성, 백업'
---

# SQLite Production 패턴: retry, timeout, 관측성, 백업

지난 9개의 글에서 SQLite와 PEP 249의 거의 모든 동작을 다뤘습니다. 마지막 글은 이 모든 것을 production 환경에서 어떻게 묶을지에 대한 글입니다. SQLite는 가볍지만, 가벼움을 핑계로 운영 가시성을 낮춰서는 안 됩니다. retry는 측정되어야 하고, slow query는 자동으로 잡혀야 하고, 트레이스는 SQL까지 따라가야 하고, 백업은 정기적으로 검증되어야 합니다.

이 글은 새 패턴을 소개하기보다 앞에서 다룬 패턴들을 production-ready 형태로 합치는 데 초점을 둡니다. 코드 한 덩어리를 그대로 가져다 써도 동작하도록 구성했습니다.

## 이 글에서 답할 질문

- retry와 timeout, busy_timeout은 어떻게 함께 설정해야 하는가?
- slow query logging은 어떻게 자동화하고, 임계치는 어떻게 정하는가?
- OpenTelemetry로 SQLite 호출을 어떻게 instrument하는가?
- SQLite 백업의 세 가지 방법(파일 복사, `.backup`, online backup API)은 어떤 차이가 있는가?
- production 체크리스트에 반드시 들어가야 하는 항목은 무엇인가?

## 왜 중요한가

운영 중 SQLite 기반 서비스가 문제를 일으킬 때, 가장 흔한 반응은 두 가지입니다. (1) "잘 모르겠어서 일단 재시작", (2) "DB 파일을 통째로 그냥 복사". 둘 다 운이 좋으면 통하지만, 데이터 손상 가능성과 SLO 위반의 책임을 운에 맡기는 셈입니다.

이 글의 목표는 운에 의존하지 않는 운영 기본기를 만드는 것입니다. retry는 백오프와 jitter로 측정 가능해야 하고, timeout은 의도적으로 설정되어야 하고, 관측성은 코드 한 줄짜리 데코레이터로도 충분해야 하며, 백업은 트랜잭션 일관성을 보장해야 합니다.

## Mental Model: SQLite도 "DB"다

> SQLite가 파일이라는 사실은 운영을 단순하게 만들지만, "그냥 파일"이라는 생각은 위험하다. 트랜잭션 중인 파일을 cp로 복사하면 손상된 사본이 생긴다. SQLite는 가볍지만, DBMS다.

production에서 지켜야 할 네 가지 축:

- **Resilience**: BUSY/LOCKED를 retry로 흡수하되, 무한 retry는 금지.
- **Bounded latency**: timeout과 max_attempts로 응답 시간 상한을 보장.
- **Observability**: 모든 SQL이 메트릭/트레이스/로그에 흔적을 남김.
- **Recoverability**: 백업은 트랜잭션 일관성을 가지며, 복구가 정기적으로 검증됨.

## 핵심 개념

### timeout vs busy_timeout vs retry

세 개념이 비슷해 보여도 다른 층에서 동작합니다.

| 항목 | 위치 | 의미 |
|------|------|------|
| `sqlite3.connect(timeout=5.0)` | Python 레벨 | `busy_timeout`을 5000ms로 설정하는 편의 인자 |
| `PRAGMA busy_timeout=5000` | SQLite 엔진 | 락을 기다리는 최대 시간(밀리초) |
| 애플리케이션 retry | 코드 레벨 | OperationalError(BUSY/LOCKED) 시 재시도 |

`busy_timeout`은 **한 번의 SQL 호출** 안에서 락을 기다리는 시간이고, retry는 **여러 번의 호출**을 시도하는 정책입니다. 두 가지를 함께 써야 합니다. busy_timeout만 길게 잡으면 한 호출이 너무 오래 멈추고, retry만 쓰면 락이 풀리는 짧은 순간을 놓치기 쉽습니다.

권장 출발점: `busy_timeout=2000~5000ms` + `max_attempts=3~5`.

### slow query 임계치 정하기

"느린 쿼리"는 절대값이 아니라 분포로 정해야 합니다. p95 latency의 2~3배를 임계치로 잡고, 임계치 초과 시 SQL 텍스트와 파라미터 일부(PII 마스킹)를 로그에 남기는 패턴이 무난합니다. 임계치를 너무 낮게 잡으면 노이즈가 폭주하고, 너무 높게 잡으면 점진적인 성능 회귀를 놓칩니다.

### 백업의 세 가지 방법

| 방법 | 일관성 | 다운타임 | 적합한 경우 |
|------|--------|----------|------------|
| `cp app.db backup.db` | 보장 안 됨 | 없음 | 절대 사용 금지 |
| sqlite3 셸의 `.backup` | 보장됨 | 거의 없음 | 운영 환경 권장 |
| Python `Connection.backup()` API | 보장됨 | 거의 없음 | 코드 통합 |
| `VACUUM INTO 'backup.db'` | 보장됨 | 길어질 수 있음 | 압축 백업 동시에 원할 때 |

`Connection.backup()`은 SQLite의 online backup API를 호출하며, 트랜잭션이 진행 중이어도 안전합니다. WAL 모드와도 호환됩니다.

## Before / After: production-ready 모듈 한 덩어리

### Before: 흩어진 처리

```python
import sqlite3, logging

def get_user(user_id):
    conn = sqlite3.connect("app.db")
    try:
        return conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    except Exception as e:
        logging.error(e)
        return None
```

retry 없음, timeout 없음, slow query 측정 없음, 트레이스 없음. 운영 중 BUSY가 한 번 발생하면 그 요청은 그냥 실패합니다.

### After: 한 모듈에 모은 production-ready 패턴

```python
# db.py
from __future__ import annotations
import sqlite3
import time
import random
import logging
import functools
from contextlib import contextmanager
from typing import Callable, Iterator, ParamSpec, TypeVar

log = logging.getLogger("db")
SLOW_QUERY_THRESHOLD_MS = 200.0

P = ParamSpec("P")
R = TypeVar("R")

RETRYABLE = {"SQLITE_BUSY", "SQLITE_BUSY_TIMEOUT", "SQLITE_LOCKED"}

def open_conn(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, isolation_level=None, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn

def is_retryable(exc: BaseException) -> bool:
    if not isinstance(exc, sqlite3.OperationalError):
        return False
    return getattr(exc, "sqlite_errorname", "") in RETRYABLE

def retry(*, max_attempts: int = 5, base_delay: float = 0.05, max_delay: float = 1.0):
    def deco(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    if attempt == max_attempts or not is_retryable(exc):
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay += random.uniform(0, delay * 0.1)
                    log.info("db retry attempt=%d delay=%.3fs exc=%s", attempt, delay, exc)
                    time.sleep(delay)
            raise RuntimeError("unreachable")
        return wrapper
    return deco

@contextmanager
def timed_query(label: str) -> Iterator[None]:
    t0 = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        if elapsed_ms >= SLOW_QUERY_THRESHOLD_MS:
            log.warning("slow query label=%s elapsed_ms=%.1f", label, elapsed_ms)
```

이 한 모듈에 (1) WAL+busy_timeout이 켜진 connection 팩토리, (2) BUSY 전용 retry 데코레이터, (3) slow query 측정 컨텍스트 매니저가 모여 있습니다. 다음 절에서 OpenTelemetry와 백업을 추가합니다.

## 단계별 실습

### 1단계: OpenTelemetry로 SQL span 만들기

```python
# tracing.py
from opentelemetry import trace

tracer = trace.get_tracer("app.db")

def trace_query(label: str):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(f"db.{label}") as span:
                span.set_attribute("db.system", "sqlite")
                t0 = time.perf_counter()
                try:
                    return fn(*args, **kwargs)
                finally:
                    span.set_attribute("db.duration_ms", (time.perf_counter()-t0)*1000)
        return wrapper
    return deco
```

`db.statement`에 SQL을 통째로 넣고 싶을 수 있지만, PII 위험이 있으므로 라벨이나 normalize된 SQL만 넣는 것을 권장합니다.

### 2단계: 데코레이터 합성

```python
@trace_query("get_user")
@retry(max_attempts=5)
def get_user(conn, user_id: int):
    with timed_query("get_user"):
        cur = conn.execute("SELECT id, email FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
    return dict(row) if row else None
```

순서가 중요합니다. `@retry`가 안쪽, `@trace_query`가 바깥쪽에 있어야 retry 시 한 span 안에서 모든 시도가 보입니다.

### 3단계: online backup

```python
# backup.py
import sqlite3
from pathlib import Path

def backup_db(src_path: str, dst_path: str, *, pages: int = 1000) -> None:
    src = sqlite3.connect(src_path)
    dst = sqlite3.connect(dst_path)
    try:
        src.backup(dst, pages=pages, progress=lambda status, remaining, total: None)
    finally:
        src.close()
        dst.close()
```

`pages`는 한 번에 복사할 페이지 수입니다. 기본값(`-1`)은 한 번에 모두 복사하지만, 큰 DB에서 latency 영향을 줄이려면 1000 정도로 잡고 progress 콜백에서 `time.sleep(0.01)` 등으로 throttle합니다.

### 4단계: 정기 백업 스크립트

```python
# scripts/backup.py
import sys, time, gzip, shutil
from pathlib import Path
from app.db import open_conn
from app.backup import backup_db

def main():
    src = Path("app.db")
    today = time.strftime("%Y%m%d-%H%M%S")
    dst = Path(f"backups/app-{today}.db")
    dst.parent.mkdir(parents=True, exist_ok=True)
    backup_db(str(src), str(dst))
    # 압축 보관
    with open(dst, "rb") as f, gzip.open(f"{dst}.gz", "wb") as gz:
        shutil.copyfileobj(f, gz)
    dst.unlink()

if __name__ == "__main__":
    main()
```

cron이나 systemd timer로 시간/일 단위 실행. 보관 정책(예: 일 1회 + 주 1회 + 월 1회)을 함께 정합니다.

### 5단계: 복구 검증

백업의 가치는 복구로만 증명됩니다. 정기적으로 임시 디렉터리에 백업을 복원하고 무결성 검사를 돌리세요.

```python
# scripts/restore_check.py
import sqlite3, gzip, shutil, sys, tempfile
from pathlib import Path

def restore_check(gz_path: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        plain = Path(td) / "restored.db"
        with gzip.open(gz_path, "rb") as gz, open(plain, "wb") as f:
            shutil.copyfileobj(gz, f)
        conn = sqlite3.connect(plain)
        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            sys.exit(f"integrity_check failed: {result}")
        rows = conn.execute("SELECT count(*) FROM users").fetchone()[0]
        print(f"restored OK; users={rows}")
```

CI에 주 1회 잡으로 등록해 두면 백업 파이프라인이 조용히 망가지는 상황을 막을 수 있습니다.

## 자주 하는 실수

**`cp`로 백업.** 트랜잭션 중인 파일은 손상된 사본을 만든다. 항상 `Connection.backup()` 또는 `.backup` 명령을 쓴다.

**timeout과 retry 중 하나만 설정.** busy_timeout은 한 호출의 락 대기, retry는 호출 간 정책. 둘 다 설정해야 응답 상한이 보장된다.

**slow query 임계치를 정하지 않음.** "느림"의 정의가 없으면 운영 회의에서 매번 다른 기준으로 다툰다. p95의 2~3배라는 명시적 기준을 코드에 박는다.

**SQL을 그대로 트레이스에 넣음.** PII 노출 위험. 라벨 또는 normalize된 SQL만 attribute로 넣는다.

**복구 검증을 안 함.** 백업이 매일 돌더라도, 1년에 한 번도 복구 검증을 안 하면 정작 필요할 때 백업이 깨져 있을 수 있다.

**WAL 모드에서 `-wal`/`-shm` 파일 무시.** SQLite는 `app.db` 외에 `app.db-wal`과 `app.db-shm`을 만든다. 백업/이동 시 함께 다루거나 `Connection.backup()`을 써서 단일 파일로 응축한다.

## 실무: SLO 기반 운영 루브릭

production에서 흔히 쓰는 SLO 항목과 측정 방법:

| 지표 | 측정 |
|------|------|
| 쿼리 p95 | OpenTelemetry span duration |
| BUSY 발생률 | retry 데코레이터의 attempt=2 이상 비율 |
| slow query 비율 | `slow query` 로그 카운트 / 전체 쿼리 |
| 백업 성공률 | 백업 스크립트 exit code, 복구 검증 결과 |
| 디스크 사용량 | `ls -l app.db*`와 `PRAGMA page_count * page_size` |

알림 임계치 예: BUSY 발생률 1% 초과, slow query 비율 5% 초과, 백업 실패 1회. 너무 민감하면 알림 피로가 생기고, 너무 둔하면 사고를 놓칩니다.

## 체크리스트

- [ ] connection 팩토리에 WAL, foreign_keys, busy_timeout이 모두 설정되어 있는가?
- [ ] retry는 BUSY/LOCKED만 대상으로 하며 max_attempts/jitter가 있는가?
- [ ] slow query 임계치를 코드/설정에 명시했는가?
- [ ] OpenTelemetry span에 `db.system=sqlite`와 라벨이 들어가는가?
- [ ] PII가 SQL/파라미터에서 마스킹되는가?
- [ ] 백업은 `Connection.backup()` 또는 `.backup`을 쓰는가?
- [ ] 백업 보관 정책(일/주/월)이 정의되어 있는가?
- [ ] 복구 검증이 주기적으로 자동 실행되는가?
- [ ] BUSY 발생률/slow query 비율이 메트릭으로 노출되는가?
- [ ] WAL 파일을 포함한 디스크 사용량이 모니터링되는가?

## 연습 문제

1. **합성.** 위 `db.py`에 OpenTelemetry instrumentation을 합치고, "5번 retry, 200ms 임계치, 단일 span" 동작을 단위 테스트로 검증하세요.
2. **부하.** 1000 RPS 부하를 모사하는 스크립트를 작성하고, 다음을 측정하세요: p50/p95/p99 latency, BUSY rate, retry rate.
3. **백업 비교.** 1GB DB에서 (a) `cp`, (b) `.backup`, (c) `Connection.backup(pages=1000)` 세 방법의 소요 시간과 사이즈를 비교하세요. (a)의 결과는 사용 금지지만, 차이를 직접 보는 것이 학습에 좋습니다.
4. **알림 설계.** BUSY 발생률 알림을 "1% 초과 + 5분 지속"으로 설정한다고 할 때, 거짓 양성과 거짓 음성을 어떻게 줄일 수 있는지 한 페이지로 정리하세요.

## 정리와 시리즈 마무리

10개의 글에서 다음을 다뤘습니다.

- DB-API 2.0(PEP 249)이 정의하는 인터페이스와 sqlite3 매핑
- connection, cursor, paramstyle, executemany
- 파라미터 바인딩과 SQL injection 방지
- 트랜잭션과 isolation, WAL, autocommit
- row factory와 type adapter/converter
- PEP 249 예외 계층과 retry 정책
- thread-safety, check_same_thread, connection 전략
- aiosqlite와 async 패턴
- production 패턴: retry, timeout, 관측성, 백업

이제 손에 쥔 도구로 "작지만 운영 가능한" SQLite 기반 서비스를 만들 수 있습니다. 다음 시리즈는 이 토대 위에 SQLAlchemy를 얹어 ORM과 세션 관리 패턴으로 한 단계 올라갑니다. SQLAlchemy를 미리 알 필요는 없고, 이 시리즈에서 다룬 트랜잭션/connection 관리가 그대로 SQLAlchemy의 동작을 이해하는 발판이 됩니다.

읽어 주셔서 감사합니다.

## 참고 자료

- [Python `sqlite3.Connection.backup`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup)
- [SQLite Online Backup API](https://www.sqlite.org/backup.html)
- [SQLite PRAGMA busy_timeout](https://www.sqlite.org/pragma.html#pragma_busy_timeout)
- [OpenTelemetry — Semantic Conventions for Database Calls](https://opentelemetry.io/docs/specs/semconv/database/database-spans/)
- [SQLite — VACUUM INTO](https://www.sqlite.org/lang_vacuum.html#vacuuminto)

Tags: Python, SQLite, Production, Observability, OpenTelemetry, Retry
