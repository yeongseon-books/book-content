---
title: "바이브코딩을 위한 Database Systems 기초 (8/10): 쿼리 최적화"
series: database-systems-101
episode: 8
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Database
  - QueryOptimization
  - EXPLAIN
  - Index
---

# 바이브코딩을 위한 Database Systems 기초 (8/10): 쿼리 최적화

이 글은 "바이브코딩을 위한 Database Systems 기초" 시리즈의 8번째 글입니다.

---

바이브코딩에서 AI는 인덱스와 쿼리를 빠르게 만들어 줍니다. 하지만 같은 SQL이 어제는 1ms였는데 오늘은 10초가 되는 일은 생각보다 흔합니다. 대부분의 경우 애플리케이션 코드가 갑자기 나빠진 것이 아니라, 옵티마이저가 다른 실행 계획을 골랐기 때문입니다. 통계가 낡았거나, 데이터 분포가 바뀌었거나, WHERE 컬럼에 함수가 붙어 인덱스가 무력화됐기 때문입니다.

AI가 생성한 쿼리에는 인덱스 사용 여부, 예상 행 수와 실제 행 수 차이, WHERE 절 함수 적용 여부를 확인해야 합니다. EXPLAIN ANALYZE 없이 튜닝을 시도하는 것은 지도 없이 길을 맞추려는 일과 비슷합니다.

쿼리 최적화의 핵심은 "더 멋진 SQL을 쓰는 법"보다 "옵티마이저가 무슨 근거로 이 계획을 골랐는지 읽는 법"에 가깝습니다. 통계, 비용 모델, 계획 노드, EXPLAIN ANALYZE를 하나의 흐름으로 정리합니다.

> **핵심 인사이트:** 튜닝의 대부분은 "옵티마이저가 지금 무엇을 알고 있고, 무엇을 모르고 있는가"를 이해하는 데서 시작합니다. estimate와 actual이 10배 이상 벌어지면 통계 문제를 먼저 의심하세요.

## 이 글에서 다룰 문제

- 옵티마이저는 어떤 기준으로 실행 계획을 고를까요?
- 통계는 왜 그렇게 결정적인 역할을 할까요?
- EXPLAIN과 EXPLAIN ANALYZE는 어떻게 읽어야 할까요?
- WHERE 컬럼에 함수를 쓰면 왜 인덱스가 안 쓰일까요?
- AI가 만든 쿼리에서 확인해야 할 것은 무엇인가요?

## 쿼리 최적화 핵심 패턴

```sql
-- 문제 진단: EXPLAIN ANALYZE로 실행 계획 확인
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 7;
-- Seq Scan on orders (cost=... rows=50000) (actual rows=50)
-- estimate와 actual 차이가 크면 통계 문제

-- 통계 갱신 후 재확인
ANALYZE orders;
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 7;
-- Index Scan using idx_user_id ... (actual rows=50)

-- 인덱스를 죽이는 패턴: WHERE 함수 감싸기
-- BAD: Seq Scan (인덱스 미사용)
SELECT * FROM users WHERE lower(email) = 'a@x.com';

-- GOOD: 함수형 인덱스 생성
CREATE INDEX idx_users_email_lower ON users (lower(email));
SELECT * FROM users WHERE lower(email) = 'a@x.com';
-- Index Scan (인덱스 사용)
```

## 변경 전후 비교

**Before: 추측 기반 튜닝**
```text
- "느리다"고 판단하고 인덱스 추가
- EXPLAIN 없이 쿼리 재작성
- WHERE에 함수 감싸서 인덱스 무력화
- 통계 갱신 없이 새 인덱스 추가
```

**After: 증거 기반 튜닝**
```text
- EXPLAIN ANALYZE로 계획 노드와 실행 수치 확인
- estimate vs actual 차이로 통계 문제 판단
- ANALYZE로 통계 갱신 후 계획 재확인
- 함수형 인덱스 또는 컬럼 방식으로 개선
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| EXPLAIN 없이 "느리다"고 판단 | 추측 기반 튜닝은 대부분 실패 | 항상 EXPLAIN ANALYZE 먼저 |
| 인덱스 추가 후 ANALYZE 생략 | 옵티마이저가 새 인덱스를 제대로 판단 못함 | 인덱스 추가 후 ANALYZE 실행 |
| WHERE 컬럼을 함수로 감쌈 | 일반 인덱스 무력화 | 함수형 인덱스 또는 계산 컬럼 사용 |
| SELECT * 남발 | 커버링 인덱스 기회 상실 | 필요한 컬럼만 명시 |
| 통계 갱신 없이 대량 INSERT 후 쿼리 | 낡은 통계로 잘못된 계획 선택 | 대량 변경 후 수동 ANALYZE |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"이 SQL이 느립니다. EXPLAIN ANALYZE 결과를 보고
인덱스 추가나 쿼리 개선 방법을 알려줘.
estimate와 actual 차이도 설명해줘"

# AI 결과물 검증 체크포인트:
# - WHERE에 함수(lower, date_trunc, cast)가 있으면 인덱스 무력화 확인
# - 인덱스 추가 시 ANALYZE 필요 여부
# - estimate rows와 actual rows 차이가 10배 이상이면 통계 문제
# - SELECT *보다 필요한 컬럼만 명시 (커버링 인덱스 활용)
```

## 운영 체크리스트

- [ ] 핵심 쿼리에 EXPLAIN ANALYZE를 최소 한 번 실행했다
- [ ] 통계가 정기적으로 갱신되고 있다
- [ ] WHERE 컬럼에 함수 호출이나 형 변환이 없다
- [ ] 슬로우 쿼리 로그를 모니터링한다
- [ ] 인덱스 추가 시 어떤 쿼리를 위한 것인지 기록한다

## 처음 질문으로 돌아가기

- **옵티마이저는 어떤 기준으로 실행 계획을 고를까요?** 통계 기반 비용 모델로 후보 계획 중 가장 비용이 낮은 것을 선택합니다. 통계가 낡으면 잘못된 계획을 고를 수 있습니다.
- **통계가 결정적인 이유는?** 옵티마이저는 실제 데이터를 읽기 전에 통계로 비용을 추정합니다. estimate와 actual 차이가 크면 통계가 현실을 반영하지 못하는 상태입니다.
- **WHERE에 함수를 쓰면 인덱스가 안 쓰이는 이유는?** 함수 결과는 인덱스가 직접 색인하지 않아 일반 인덱스를 우회합니다. 함수형 인덱스를 별도로 만들어야 합니다.

## 정리

바이브코딩에서 AI가 만들어 준 쿼리와 인덱스에서 EXPLAIN ANALYZE로 estimate vs actual 차이를 확인하고, WHERE에 함수가 들어가지 않도록 검토하세요. 인덱스를 추가했다면 ANALYZE로 통계를 갱신해야 옵티마이저가 새 인덱스를 올바르게 활용합니다. 다음 글에서는 가용성과 복구를 다루는 복제와 백업을 정리합니다.

## 참고 자료

- [PostgreSQL — Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [Use The Index, Luke!](https://use-the-index-luke.com/)
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
- **바이브코딩을 위한 Database Systems 기초 (8/10): 쿼리 최적화 (현재 글)**
- 바이브코딩을 위한 Database Systems 기초 (9/10): 복제와 백업
- 바이브코딩을 위한 Database Systems 기초 (10/10): OLTP와 OLAP
<!-- toc:end -->

Tags: 바이브코딩, Database, QueryOptimization, EXPLAIN, Index
