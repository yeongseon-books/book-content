---
title: "바이브코딩을 위한 Alembic 기초 (1/10): 왜 Alembic인가, 그리고 init까지"
series: alembic-101
episode: 1
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

# 바이브코딩을 위한 Alembic 기초 (1/10): 왜 Alembic인가, 그리고 init까지

이 글은 "바이브코딩을 위한 Alembic 기초" 시리즈의 첫 번째 글입니다. AI와 함께 빠르게 DB 스키마를 관리하는 방법을 처음부터 정리합니다.

---

AI에게 "FastAPI에 유저 테이블 추가해줘"라고 말하면 모델 코드는 금방 나옵니다. 그런데 막상 production DB에 적용하려면? `ALTER TABLE`을 직접 치다가 실수하고, 롤백 방법도 없고, "어떤 환경에 뭐가 적용됐는지" 아무도 모르는 상황이 됩니다. 바이브코딩 속도로 코드를 뽑아내다 보면 DB 스키마 관리가 가장 먼저 무너집니다.

Alembic은 이 문제를 git처럼 풀어냅니다. AI가 모델 코드를 바꿀 때마다 migration 파일이 함께 생기고, 모든 환경이 같은 이력을 따라 올라가거나 내려옵니다. "AI가 만든 코드인데 DB는 어디까지 적용됐지?"라는 질문에 `alembic current` 한 줄로 답할 수 있게 됩니다.

바이브코딩 팀에서 흔히 보이는 패턴이 있습니다. AI로 기능을 빠르게 만들고, production에는 손으로 SQL을 치고, staging과 production이 언제부터인가 어긋나기 시작합니다. 이 글에서는 그 첫 번째 해결책인 Alembic 초기 설정을 잡겠습니다.

> **핵심 인사이트:** Alembic은 DB 스키마를 위한 git입니다. AI가 모델을 바꿀 때마다 revision을 만들고, 모든 환경은 같은 이력을 따라 동기화됩니다.

## 이 글에서 다룰 문제

- 바이브코딩 프로젝트에서 DB 스키마 관리가 왜 금방 무너질까요?
- `Base.metadata.create_all`만으로는 왜 운영 환경을 버틸 수 없을까요?
- revision, head, `alembic_version` 테이블은 각각 어떤 역할을 할까요?
- AI가 모델 코드를 바꿀 때 migration 파일을 자동으로 만들 수 있을까요?
- `alembic init`이 실제로 무엇을 준비하는지 알면 무엇이 달라질까요?

## 왜 Alembic인가

AI와 함께 개발할 때 코드 속도는 빠르지만 인프라 관리는 여전히 사람 몫입니다. 특히 DB 스키마는 코드처럼 git에서 추적되지 않으면 금방 "누가 어떤 SQL을 어느 환경에 쳤는지" 아무도 모르는 상태가 됩니다.

Alembic은 이 문제를 정확히 git이 코드를 다루는 방식으로 해결합니다. 각 변경은 revision이고, head는 최신 상태이며, 모든 환경은 같은 이력을 따릅니다.

## 변경 전후 비교

**Before: 수동 SQL로 production 관리**
```bash
psql -h prod -U app -d main -c "ALTER TABLE users ADD COLUMN tier VARCHAR(16);"
# 누가, 언제, 어떤 환경에 실행했는지 나중에 알 수 없음
```

**After: revision 파일이 변경 이력**
```bash
alembic revision -m "add users.tier"
# PR 리뷰 대상, staging/production 동일 명령으로 동기화
alembic upgrade head
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| `create_all`로 production 시작 | 컬럼 추가/삭제 불가, 이력 없음 | 처음부터 Alembic 사용 |
| `alembic.ini`에 credential 하드코딩 | 보안 사고 | 환경 변수로 분리 |
| `alembic_version` 손수 수정 | 이력 손상 | `alembic stamp` 사용 |
| push 후 revision 파일 수정 | 다른 환경과 충돌 | 새 revision으로 수정 |
| 여러 사람이 동시에 revision 생성 | branch 발생 | PR 머지 직전 정리 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"users 모델에 tier 컬럼을 추가하고, alembic revision 파일도 함께 만들어줘"

# AI가 생성할 코드:
# 1. models.py: Mapped[str] tier 컬럼 추가
# 2. alembic revision 파일: upgrade/downgrade 포함
```

바이브코딩에서 AI는 revision 파일의 `upgrade()`와 `downgrade()` 함수를 올바르게 작성해 줍니다. 단, `down_revision`이 의도한 그래프를 만드는지 반드시 확인하세요.

## 운영 체크리스트

- [ ] `alembic init` 뒤에 `alembic.ini`, `env.py`, `versions/`를 구분할 수 있다
- [ ] 첫 빈 revision을 만들고 `upgrade head` 후 `alembic_version`이 생기는 것을 확인했다
- [ ] `create_all`은 테스트용이고, 운영 환경은 Alembic으로만 관리한다는 원칙이 분명하다
- [ ] revision 파일을 git에 커밋하고 PR에서 리뷰한다
- [ ] credential은 환경 변수에서 읽는다

## 처음 질문으로 돌아가기

- **바이브코딩 프로젝트에서 DB 스키마 관리가 왜 금방 무너질까요?** AI로 코드를 빠르게 만들수록 DB 변경 이력이 사람 기억에 의존하게 되고, staging과 production이 언제부터인가 어긋납니다.
- **`create_all`만으로는 왜 운영을 버틸 수 없을까요?** 컬럼 추가/삭제를 전달하지 못하고, 롤백도 없습니다.
- **revision, head, `alembic_version`은 어떤 역할인가요?** revision은 커밋, head는 최신 상태, `alembic_version`은 현재 DB의 HEAD 포인터입니다.

## 정리

Alembic은 바이브코딩 팀이 빠른 개발 속도를 유지하면서도 DB 스키마를 안전하게 관리할 수 있는 기반입니다. 다음 글에서는 `env.py`를 열어 모델 metadata를 연결하고, DB URL을 환경 변수에서 안전하게 읽는 방법을 다룹니다.

## 참고 자료

- [Alembic 공식 문서](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLAlchemy MetaData](https://docs.sqlalchemy.org/en/20/core/metadata.html)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/alembic-101/ko/01-why-alembic-and-init)

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 Alembic 기초 (1/10): 왜 Alembic인가, 그리고 init까지 (현재 글)**
- 바이브코딩을 위한 Alembic 기초 (2/10): env.py와 target_metadata
- 바이브코딩을 위한 Alembic 기초 (3/10): 첫 revision: upgrade와 downgrade
- 바이브코딩을 위한 Alembic 기초 (4/10): autogenerate와 그 한계
- 바이브코딩을 위한 Alembic 기초 (5/10): branch와 merge
- 바이브코딩을 위한 Alembic 기초 (6/10): 데이터 마이그레이션
- 바이브코딩을 위한 Alembic 기초 (7/10): online과 offline 모드
- 바이브코딩을 위한 Alembic 기초 (8/10): downgrade 전략
- 바이브코딩을 위한 Alembic 기초 (9/10): 배포 순서와 blue/green
- 바이브코딩을 위한 Alembic 기초 (10/10): production과 팀 workflow
<!-- toc:end -->

Tags: 바이브코딩, Python, Alembic, SQLAlchemy, Migration, DB마이그레이션
