---
title: "바이브코딩을 위한 Database Systems 기초 (9/10): 복제와 백업"
series: database-systems-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Database
  - Replication
  - Backup
  - HighAvailability
---

# 바이브코딩을 위한 Database Systems 기초 (9/10): 복제와 백업

이 글은 "바이브코딩을 위한 Database Systems 기초" 시리즈의 9번째 글입니다.

---

바이브코딩에서 AI는 복제 설정과 백업 스크립트를 빠르게 만들어 줍니다. 하지만 운영 중인 데이터베이스는 언젠가 반드시 사고를 만납니다. 디스크가 고장 나고, 사람이 잘못된 DELETE를 실행하고, 네트워크 구간이나 리전 전체가 흔들릴 수 있습니다.

복제와 백업은 모두 데이터를 지키는 수단이지만, 보호하는 축이 다릅니다. 복제는 같은 시점의 데이터를 여러 노드에 퍼뜨려 가용성을 높이고, 백업은 시간을 거슬러 복원할 수 있게 해 줍니다. 가장 흔한 실수는 레플리카를 백업으로 착각하는 것입니다. 잘못된 DELETE는 레플리카에도 즉시 복제됩니다.

복원 절차를 한 번도 연습해 보지 않은 백업은 백업이 아니라 희망 사항에 가깝습니다. "백업이 있다"는 말은 "최근에 실제로 복원했다"는 사실이 동반될 때만 믿을 수 있습니다.

Primary-Replica 복제, 동기/비동기 트레이드오프, PITR, RPO/RTO를 중심으로 복제와 백업의 핵심을 정리합니다.

> **핵심 인사이트:** 복제는 공간 축에서 가용성을 맡고, 백업은 시간 축에서 복구 가능성을 맡습니다. 둘 중 하나만으로는 충분하지 않으며, 복구 리허설이 없는 백업은 미검증 가정입니다.

## 이 글에서 다룰 문제

- Primary-Replica 복제는 어떻게 동작하고 각 노드는 무슨 역할을 할까요?
- 동기 복제와 비동기 복제는 무엇을 주고받을까요?
- 전체 백업과 WAL 기반 PITR은 어떻게 다를까요?
- 레플리카를 백업으로 착각하면 어떤 문제가 생길까요?
- AI가 만든 복제/백업 설정에서 확인해야 할 것은 무엇인가요?

## 복제와 백업 핵심 패턴

```ini
# postgresql.conf (Primary 설정)
wal_level = replica
max_wal_senders = 10
archive_mode = on
archive_command = 'cp %p /var/lib/pgsql/wal_archive/%f'

# 동기 복제 (데이터 손실 최소화, 쓰기 지연 위험)
synchronous_commit = on
synchronous_standby_names = 'replica1'
```

```bash
# 레플리카 초기화
pg_basebackup -h primary.host -D /var/lib/pgsql/replica -U replicator -P -X stream

# 복제 지연 모니터링
psql -c "SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;"

# PITR: 베이스 백업 + WAL 재적용
pg_basebackup -D /backup/base/$(date +%F) -Ft -z -P
```

## 변경 전후 비교

**Before: 단일 인스턴스 + 야간 백업만**
```text
- 디스크 장애 시 지난밤 백업 이후 데이터 손실
- 복구에 30분 이상 소요
- 잘못된 DELETE → 복구 불가
- 레플리카를 백업으로 착각
```

**After: 복제 + PITR 백업 조합**
```text
- 자동 페일오버로 30초 안에 쓰기 서비스 복귀
- PITR로 잘못된 DELETE 직전 시점으로 복원
- 복제 지연 모니터링 + 알람
- 분기별 복구 리허설 일정 운영
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 레플리카를 백업으로 착각 | 잘못된 DELETE가 레플리카에도 즉시 복제됨 | 복제와 백업은 별도 운영 |
| 복구 리허설 미실시 | 실제 장애 시 복구 절차에서 실패 | 분기별 실제 복원 훈련 |
| RPO/RTO를 숫자로 합의 안 함 | 비즈니스 요구와 인프라 비용 어긋남 | 명시적 숫자로 사전 합의 |
| 동기 복제만 믿음 | 느린 레플리카 하나가 전체 쓰기 지연 | 비동기+PITR 조합 검토 |
| 백업을 같은 리전에만 보관 | 리전 단위 사고 시 복구 불가 | 다른 리전 또는 다른 계정에 보관 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"PostgreSQL Primary-Replica 복제와 PITR 백업 설정을 만들어줘.
RPO 5분, RTO 30초 기준으로,
복제 지연 모니터링과 자동 페일오버도 포함해야 해"

# AI 결과물 검증 체크포인트:
# - archive_mode = on 및 archive_command 설정 여부
# - 동기 복제 사용 시 쓰기 지연 위험 문서화
# - 백업이 다른 리전/계정에 보관되는지 확인
# - 복구 절차가 문서화되어 있는지 확인
# - 복제 지연 모니터링 알람이 있는지 확인
```

## 운영 체크리스트

- [ ] RPO/RTO가 명시적으로 숫자로 정의되어 있다
- [ ] 정기 백업과 WAL 아카이브가 모두 준비되어 있다
- [ ] 백업이 별도 리전 또는 계정에 저장된다
- [ ] 최근 6개월 안에 복원 훈련을 실시했다
- [ ] 복제 지연을 실시간으로 모니터링한다
- [ ] 페일오버 절차가 문서화되어 있다

## 처음 질문으로 돌아가기

- **Primary-Replica 복제의 역할 분담은?** Primary가 쓰기를 받고 WAL을 스트리밍하면, Replica가 따라가며 읽기 부하를 분산합니다. 가용성 축 보호가 목적입니다.
- **동기 복제와 비동기 복제의 트레이드오프는?** 동기는 데이터 손실 위험을 줄이지만 느린 레플리카가 전체 쓰기를 멈출 수 있습니다. 비동기는 빠르지만 페일오버 시 최근 변경이 손실될 수 있습니다.
- **레플리카가 백업이 될 수 없는 이유는?** 잘못된 DELETE나 UPDATE는 레플리카에도 즉시 복제됩니다. 시간 축 복구(PITR)는 백업만이 제공합니다.

## 정리

바이브코딩에서 AI가 만들어 준 복제/백업 설정에서 archive_mode 설정, 백업 저장 위치(다른 리전 여부), 복구 절차 문서화 여부를 반드시 확인하세요. 복제와 백업을 함께 운영하고 분기별 복구 리허설을 실시하는 것이 운영 성숙도의 기준입니다. 다음 글에서는 시리즈 마지막으로 OLTP와 OLAP의 차이를 정리합니다.

## 참고 자료

- [PostgreSQL — High Availability, Replication](https://www.postgresql.org/docs/current/high-availability.html)
- [PostgreSQL — Continuous Archiving and PITR](https://www.postgresql.org/docs/current/continuous-archiving.html)
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
- **바이브코딩을 위한 Database Systems 기초 (9/10): 복제와 백업 (현재 글)**
- 바이브코딩을 위한 Database Systems 기초 (10/10): OLTP와 OLAP
<!-- toc:end -->

Tags: 바이브코딩, Database, Replication, Backup, HighAvailability
