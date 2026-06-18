---
title: "바이브코딩을 위한 Alembic 기초 (9/10): 배포 순서와 blue/green"
series: alembic-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Python
  - Alembic
  - SQLAlchemy
  - Migration
  - DB마이그레이션
---

# 바이브코딩을 위한 Alembic 기초 (9/10): 배포 순서와 blue/green

이 글은 "바이브코딩을 위한 Alembic 기초" 시리즈의 아홉 번째 글입니다.

---

새 기능을 배포합니다. migration을 먼저 실행해야 할까요, 코드를 먼저 배포해야 할까요? 잘못된 순서로 하면 production에서 몇 분이라도 서비스가 다운됩니다. 바이브코딩에서 AI는 "migration 먼저 실행하면 됩니다"라고 단순하게 안내하지만, 실제로는 코드와 schema의 호환성을 신중하게 관리해야 합니다.

컬럼을 추가하는 경우에는 migration을 먼저 실행해도 안전합니다. 새 컬럼이 있어도 기존 코드는 그것을 무시하기 때문입니다. 반면 컬럼을 삭제하는 경우에는 코드를 먼저 업데이트해야 합니다. 기존 코드가 이미 사라진 컬럼을 참조하면 에러가 나기 때문입니다.

blue/green 배포에서는 두 버전의 코드가 같은 DB를 바라보는 순간이 있습니다. 이 순간에 schema가 두 버전 모두와 호환되어야 합니다. expand/contract 패턴이 바로 이 문제의 해결책입니다.

> **핵심 인사이트:** migration-first 원칙: 컬럼 추가는 migration 먼저, 컬럼 삭제는 코드 먼저입니다. blue/green 배포에서는 expand/contract 패턴으로 두 버전 호환성을 보장하세요.

## 이 글에서 다룰 문제

- 컬럼 추가와 삭제에서 배포 순서는 왜 다른가요?
- blue/green 배포에서 schema 호환성을 어떻게 보장할까요?
- expand/contract 패턴은 무엇이고 언제 사용해야 하나요?
- migration을 앱 시작 시 자동 실행하는 것의 위험성은 무엇인가요?
- AI가 배포 순서를 잘못 안내할 때 어떻게 수정할까요?

## 배포 순서 원칙

```
컬럼 추가:
  1. migration 실행 (ADD COLUMN)
  2. 코드 배포 (새 컬럼 사용)
  이유: 기존 코드는 새 컬럼을 무시함

컬럼 삭제:
  1. 코드 배포 (컬럼 참조 제거)
  2. migration 실행 (DROP COLUMN)
  이유: 기존 코드가 사라진 컬럼을 참조하면 에러

컬럼 이름 변경 (expand/contract):
  1. ADD COLUMN new_name (expand)
  2. 코드 배포 (new_name 사용)
  3. DROP COLUMN old_name (contract)
```

## 변경 전후 비교

**Before: 순서 없이 배포**
```bash
git push  # 코드 배포 + migration 동시
# 코드가 이미 없는 컬럼을 참조하거나
# migration이 아직 코드가 의존하는 컬럼을 삭제할 수 있음
```

**After: 순서 보장 배포**
```bash
# 컬럼 삭제 시:
# 1단계: 코드에서 컬럼 참조 제거 후 배포
# 2단계: migration으로 컬럼 삭제
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 컬럼 삭제 migration을 코드보다 먼저 | 기존 코드 에러 | 코드 먼저 배포 |
| 앱 시작 시 자동 migration | 스케일링 시 여러 인스턴스 충돌 | 별도 release job |
| blue/green에서 호환성 미검증 | 트래픽 전환 시 에러 | expand/contract 패턴 |
| migration 실패 시 rollback 계획 없음 | 배포 중단 | 배포 전 rollback 절차 문서화 |
| migration timeout 설정 없음 | 대형 테이블에서 배포 중단 | statement_timeout 설정 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"users.name을 first_name으로 이름 바꾸는 배포를 계획해줘.
blue/green 배포 환경에서 zero-downtime으로 해야 해.
expand/contract 패턴으로 단계를 나눠줘"

# 배포 스크립트 예시:
set -euo pipefail
alembic check   # migration 미적용 여부 확인
alembic upgrade head
# 앱 배포
```

## 운영 체크리스트

- [ ] 컬럼 추가는 migration 먼저, 컬럼 삭제는 코드 먼저임을 팀이 안다
- [ ] blue/green 배포 시 expand/contract 패턴을 사용한다
- [ ] migration은 앱 시작이 아닌 별도 release job에서 실행한다
- [ ] 배포 전 `alembic check`로 미적용 migration 여부를 확인한다
- [ ] migration 실패 시 rollback 절차가 문서화되어 있다

## 처음 질문으로 돌아가기

- **컬럼 추가와 삭제에서 배포 순서가 다른 이유는?** 기존 코드와의 호환성 때문입니다. 추가는 무시 가능하지만 삭제는 기존 코드를 깨뜨립니다.
- **blue/green 배포에서 expand/contract 패턴이 필요한 이유는?** 두 버전의 코드가 동시에 동작하는 순간 schema가 양쪽 모두와 호환되어야 합니다.
- **migration 자동 실행의 위험성은?** 여러 인스턴스가 동시에 시작하면 migration이 중복 실행되거나 충돌할 수 있습니다.

## 정리

배포 순서는 바이브코딩에서 자주 간과되지만 가장 중요한 주제 중 하나입니다. AI가 단순하게 "migration 먼저"라고 안내할 때, 컬럼 삭제 시에는 "코드 먼저"라는 원칙을 기억하세요. 다음 글에서는 production과 팀 workflow, CI/CD 파이프라인, 모니터링, 그리고 incident response를 다룹니다.

## 참고 자료

- [Zero-downtime DB migrations](https://benchling.engineering/move-fast-and-migrate-things-how-we-automated-migrations-in-postgres-d60aba0fc3d4)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/09-deploy-ordering-and-blue-green)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Alembic 기초 (1/10): 왜 Alembic인가, 그리고 init까지
- 바이브코딩을 위한 Alembic 기초 (2/10): env.py와 target_metadata
- 바이브코딩을 위한 Alembic 기초 (3/10): 첫 revision: upgrade와 downgrade
- 바이브코딩을 위한 Alembic 기초 (4/10): autogenerate와 그 한계
- 바이브코딩을 위한 Alembic 기초 (5/10): branch와 merge
- 바이브코딩을 위한 Alembic 기초 (6/10): 데이터 마이그레이션
- 바이브코딩을 위한 Alembic 기초 (7/10): online과 offline 모드
- 바이브코딩을 위한 Alembic 기초 (8/10): downgrade 전략
- **바이브코딩을 위한 Alembic 기초 (9/10): 배포 순서와 blue/green (현재 글)**
- 바이브코딩을 위한 Alembic 기초 (10/10): production과 팀 workflow
<!-- toc:end -->

Tags: 바이브코딩, Python, Alembic, SQLAlchemy, Migration, DB마이그레이션
