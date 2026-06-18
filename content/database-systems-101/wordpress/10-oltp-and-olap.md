---
title: "바이브코딩을 위한 Database Systems 기초 (10/10): OLTP와 OLAP"
series: database-systems-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Database
  - OLTP
  - OLAP
  - DataWarehouse
---

# 바이브코딩을 위한 Database Systems 기초 (10/10): OLTP와 OLAP

이 글은 "바이브코딩을 위한 Database Systems 기초" 시리즈의 마지막 글입니다.

---

바이브코딩에서 AI는 분석 쿼리를 운영 데이터베이스에서 직접 실행하는 코드를 만들어 줄 때가 많습니다. 하지만 큰 집계 쿼리 하나가 운영 DB의 캐시를 날리고, 리소스를 잡아먹고, 다른 사용자의 요청을 느리게 만드는 일은 매우 흔합니다.

운영 데이터베이스가 분석 쿼리에 짓눌리는 문제는 "더 빠른 서버를 쓰면 해결된다"로 접근하면 안 됩니다. OLTP와 OLAP는 근본적으로 다른 접근 패턴을 가지며, 같은 시스템에 두면 두 워크로드가 서로의 발목을 잡습니다.

입문 단계에서는 "같은 데이터를 두 군데 두는 것은 비효율적 아닌가?"라는 생각이 자연스럽습니다. 하지만 짧고 빈번한 트랜잭션과 길고 넓은 집계 쿼리는 서로를 심각하게 방해합니다. OLTP와 OLAP의 차이를 이해하면 "이 쿼리는 어디서 실행되어야 하는가?"를 훨씬 빨리 판단할 수 있습니다.

> **핵심 인사이트:** 운영과 분석을 같은 시스템에 두면 단기적으로는 편해 보이지만, 장기적으로는 두 워크로드가 서로의 발목을 잡습니다. 분석 쿼리는 웨어하우스로 분리해야 합니다.

## 이 글에서 다룰 문제

- OLTP와 OLAP 워크로드의 근본 차이는 무엇일까요?
- 행 저장과 컬럼 저장은 어떤 트레이드오프를 가질까요?
- 데이터 웨어하우스와 ETL/ELT는 왜 필요한가요?
- 운영 DB에서 분석 쿼리를 실행하면 어떤 문제가 생길까요?
- AI가 만든 분석 코드에서 확인해야 할 것은 무엇인가요?

## OLTP vs OLAP 핵심 패턴

```sql
-- OLTP 패턴: 단일 행, 짧은 트랜잭션
BEGIN;
INSERT INTO orders (user_id, product_id, total) VALUES (42, 7, 9900);
UPDATE inventory SET qty = qty - 1 WHERE product_id = 7;
COMMIT;

-- OLAP 패턴: 대규모 집계 (웨어하우스에서 실행해야 함)
-- BAD: 운영 DB에서 실행 → 캐시 오염, 느린 응답
SELECT date_trunc('day', created_at), SUM(total)
FROM orders
GROUP BY 1 ORDER BY 1;  -- 60s, 운영 서비스 영향

-- GOOD: 웨어하우스(BigQuery, Redshift, DuckDB)에서 실행
-- ETL/ELT로 운영 → 웨어하우스로 데이터 이동 후 집계
```

```text
운영 DB (OLTP, 행 저장)
    ↓ ETL/ELT (Airbyte, dbt, AWS Glue)
데이터 웨어하우스 (OLAP, 컬럼 저장)
    ↑ 쿼리
분석가/BI 도구
```

## 변경 전후 비교

**Before: 운영 DB에서 분석 쿼리 직접 실행**
```text
- 집계 쿼리가 운영 캐시를 날림
- 분석 쿼리 중 운영 서비스 응답 지연
- 잠금 경합으로 트랜잭션 실패
- 운영/분석 쿼리가 같은 인덱스 전략으로 충돌
```

**After: 웨어하우스 분리 + ETL/ELT**
```text
- 운영 DB는 OLTP에 최적화 (행 저장, 짧은 트랜잭션)
- 웨어하우스는 OLAP에 최적화 (컬럼 저장, 대규모 집계)
- ETL로 정기 동기화 (실시간 필요 시 CDC 활용)
- 분석 쿼리가 운영 서비스에 영향 없음
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 운영 DB에서 집계 쿼리 직접 실행 | 캐시 오염, 운영 서비스 지연 | 웨어하우스 또는 레플리카로 분리 |
| 레플리카에서 분석 쿼리 실행 | 복제 지연 증가, 레플리카 부하 | 별도 웨어하우스 구성 |
| OLAP용 컬럼 DB에 OLTP 쿼리 실행 | 단일 행 조회가 느림 | 워크로드 특성에 맞는 DB 선택 |
| ETL 없이 운영 DB 직접 쿼리 허용 | 분석가 실수가 운영에 직접 영향 | ETL/ELT 파이프라인 구성 |
| 스타 스키마 없이 웨어하우스 구성 | 복잡한 JOIN으로 분석 쿼리 느림 | 사실 테이블 + 차원 테이블 분리 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"운영 PostgreSQL에서 분석 쿼리를 실행하고 있어.
분석을 위해 DuckDB 또는 BigQuery로 분리하는 방법을 알려줘.
ETL 파이프라인 설계와 스타 스키마 구조도 포함해줘"

# OLTP vs OLAP 구분 기준:
# - 단일 행 조회/수정 → OLTP DB
# - 수백만 행 집계/스캔 → OLAP 웨어하우스
# - 실시간 집계 필요 → CDC + 스트리밍 웨어하우스
# - 소규모 분석 → DuckDB (파일 기반, 간단)
# - 대규모 분석 → BigQuery, Redshift, Snowflake
```

## 운영 체크리스트

- [ ] 분석 쿼리가 운영 DB가 아닌 웨어하우스 또는 레플리카에서 실행된다
- [ ] ETL/ELT 파이프라인이 구성되어 있다
- [ ] 웨어하우스에 컬럼 지향 저장소를 사용한다
- [ ] 운영 DB와 분석 DB의 접근 권한이 분리되어 있다
- [ ] 분석 쿼리의 실행 시간을 별도 모니터링한다

## 처음 질문으로 돌아가기

- **OLTP와 OLAP의 근본 차이는?** OLTP는 단일 행 기준의 짧고 빈번한 읽기/쓰기, OLAP는 대규모 스캔과 집계입니다. 최적화 방향이 반대여서 같은 시스템에서 충돌합니다.
- **행 저장과 컬럼 저장의 트레이드오프는?** 행 저장은 단일 행 조회/수정에 빠르고, 컬럼 저장은 특정 컬럼 집계에 빠릅니다. 분석 쿼리는 컬럼 저장이 압도적으로 유리합니다.
- **ETL/ELT가 필요한 이유는?** 운영 DB와 웨어하우스가 분리되면 데이터 동기화 파이프라인이 필요합니다. ETL은 변환 후 적재, ELT는 적재 후 변환합니다.

## 정리

바이브코딩에서 AI가 만들어 준 분석 쿼리가 운영 DB에서 직접 실행되지 않도록 확인하세요. 분석 워크로드는 웨어하우스나 레플리카로 분리하고, ETL/ELT 파이프라인으로 데이터를 이동시켜야 운영 서비스에 영향을 주지 않습니다. Database Systems 101 시리즈를 통해 데이터베이스 운영의 기본기를 갖추셨기를 바랍니다.

## 참고 자료

- [Designing Data-Intensive Applications](https://dataintensive.net/)
- [dbt Documentation](https://docs.getdbt.com/)
- [DuckDB — In-process analytical database](https://duckdb.org/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/database-systems-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Database Systems 기초 (1/10): 데이터베이스란 무엇인가?
- 바이브코딩을 위한 Database Systems 기초 (2/10): 관계형 모델
- 바이브코딩을 위한 Database Systems 기초 (3/10): SQL과 쿼리 처리
- 바이브코딩을 위한 Database Systems 기초 (4/10): 인덱스
- 바이브코딩을 위한 Database Systems 기초 (5/10): 트랜잭션과 ACID
- 바이브코딩을 위한 Database Systems 기초 (6/10): 격리 수준
- 바이브코딩을 위한 Database Systems 기초 (7/10): 정규화와 모델링
- 바이브코딩을 위한 Database Systems 기초 (8/10): 쿼리 최적화
- 바이브코딩을 위한 Database Systems 기초 (9/10): 복제와 백업
- **바이브코딩을 위한 Database Systems 기초 (10/10): OLTP와 OLAP (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, Database, OLTP, OLAP, DataWarehouse
