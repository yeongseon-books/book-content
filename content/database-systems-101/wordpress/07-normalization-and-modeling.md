---
series: database-systems-101
episode: 7
title: "바이브코딩을 위한 데이터베이스 시스템 기초 (7/10): 정규화와 모델링"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Computer Science
  - Database
  - 정규화
  - 모델링
  - 1NF
  - 의존성
seo_description: AI가 만든 테이블 구조에서 데이터 불일치가 생기는 이유를 정규화의 관점에서 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 데이터베이스 시스템 기초 (7/10): 정규화와 모델링

이 글은 **바이브코딩을 위한 데이터베이스 시스템 기초** 시리즈의 7번째 글입니다. AI 코딩 도구로 빠르게 서비스를 만들 때 데이터베이스가 왜 그렇게 동작하는지 이해하면, AI가 만든 쿼리의 문제를 직접 발견하고 수정할 수 있습니다.

---

AI가 만든 주문 테이블을 6개월 운영하다 보면 이런 문제를 겪게 됩니다. 사용자가 이메일을 바꿨는데 일부 주문에는 여전히 옛날 이메일이 남아 있습니다. 상품 가격을 인상했는데 과거 주문 금액도 같이 바뀌어 버렸습니다. 이런 문제는 버그가 아니라 데이터 모델 설계의 문제입니다.

데이터 모델이 엉성하면 모든 쿼리가 그 대가를 치릅니다. 같은 사실이 여러 곳에 흩어져 있으면 갱신은 빠뜨리기 쉽고, JOIN 결과는 상황에 따라 다르게 보이며, 동시성 문제도 더 자주 생깁니다. 정규화는 이 문제를 "각 사실은 정확히 한 곳에 둔다"는 원칙으로 푸는 고전적 도구입니다.

> 좋은 모델은 "이 값을 바꾸려면 N개의 행을 동시에 수정해야 한다"는 상황을 가능하면 만들지 않습니다.

## 이 글에서 다룰 질문

- 함수 종속은 어떤 직관으로 이해하면 좋을까요?
- 1NF, 2NF, 3NF는 각각 무엇을 금지할까요?
- AI가 만든 스키마에서 정규화 위반을 어떻게 찾을까요?
- 비정규화는 언제 정당화될까요?
- 모델 변경 시 기존 데이터를 어떻게 안전하게 마이그레이션할까요?

---

## 정규화의 세 단계

각 단계는 바로 앞 단계를 만족한 상태에서 한 가지 규칙을 더합니다. 대부분의 OLTP 모델에는 3NF면 충분합니다.

```
raw table
  → 1NF: atomic values (원자 값)
  → 2NF: no partial deps (부분 종속 제거)
  → 3NF: no transitive deps (이행 종속 제거)
```

**핵심 용어**

- **함수 종속(X → Y)**: X가 같으면 Y도 같아야 하는 관계입니다.
- **1NF**: 모든 컬럼이 원자 값을 가져야 합니다. 배열이나 콤마 리스트를 두지 않습니다.
- **2NF**: 1NF를 만족하면서, 복합키의 일부에만 의존하는 부분 종속이 없어야 합니다.
- **3NF**: 2NF를 만족하면서, 비키 컬럼이 다른 비키 컬럼에 의존하는 이행 종속이 없어야 합니다.

## 바이브코딩 관점: AI가 만드는 정규화 위반 패턴

AI는 기능 요구사항에 집중해서 스키마를 설계하므로 정규화를 자주 놓칩니다.

| 정규화 위반 | AI가 만드는 패턴 | 발생 문제 |
|---|---|---|
| 1NF 위반 | `tags TEXT` 컬럼에 "python,ai,db" 저장 | 검색, 집계, 조인 모두 불편 |
| 중복 저장 | 주문마다 user_email 저장 | 이메일 변경 시 일부만 업데이트 |
| 이행 종속 | 주문에 `user_city` 컬럼 저장 | 도시가 바뀌면 관련 주문 전체 수정 |
| 가격 비정규화 | 주문 항목에 현재 상품 가격 저장 없이 상품 참조만 | 가격 변경이 과거 주문에 영향 |

## Before / After: 단일 테이블 vs 정규화된 구조

**Before — 하나의 테이블에 모든 정보 (AI 초기 설계)**

```text
orders(id, user_id, user_email, product_id, product_name, product_price, quantity)
```

`user_email`은 `user_id`에 종속되고, `product_name`과 `product_price`는 `product_id`에 종속됩니다. 사용자의 이메일을 바꾸려면 그 사용자의 모든 주문 행을 수정해야 합니다.

**After — 정규화된 구조**

```text
users(id, email)
products(id, name, price)
orders(id, user_id, product_id, quantity, price_at_order)
```

이제 이메일은 `users`의 한 행에만 존재하고, 주문 당시 가격은 `price_at_order`에 스냅샷으로 보존됩니다. 현재 상품 가격 변경이 과거 주문에 영향을 주지 않습니다.

## 실제 정규화 예시: 한 테이블에서 세 테이블로

```sql
-- 정규화 전
orders_raw(order_id, user_id, user_email, item_sku, item_name, item_price, qty)

-- 1NF 적용 (각 셀은 하나의 값만)
-- 2NF 적용 (부분 종속 제거)
-- 3NF 적용 (이행 종속 제거)

-- 정규화 후
CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);
CREATE TABLE items (sku TEXT PRIMARY KEY, name TEXT NOT NULL, price INTEGER NOT NULL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id), created_at TIMESTAMP);
CREATE TABLE order_items (
    order_id INTEGER REFERENCES orders(id),
    item_sku TEXT REFERENCES items(sku),
    qty INTEGER NOT NULL,
    price_at_order INTEGER NOT NULL,  -- 주문 당시 가격 스냅샷
    PRIMARY KEY (order_id, item_sku)
);
```

## 자주 하는 실수 5가지

| 번호 | 실수 | 왜 문제인가 |
|---|---|---|
| 1 | 콤마 리스트로 다대다를 표현 | 1NF를 깨고, 검색과 조인을 모두 불편하게 만듭니다 |
| 2 | 변경 가능한 값을 여러 테이블에 중복 저장 | 갱신 누락이 필연적으로 생깁니다 |
| 3 | 자연키를 기본키로 씀 | 값 변경이 모든 참조를 흔들 수 있습니다 |
| 4 | 모든 모델을 무조건 끝까지 정규화 | 분석 워크로드에서는 비정규화가 더 적절할 수 있습니다 |
| 5 | 테이블은 나눴지만 외래키는 꺼 둠 | 이는 정규화가 아니라 "정규화된 척"입니다 |

## AI 팁: 정규화 검토를 AI에게 요청하는 방법

기존 스키마를 AI에게 보여주고 정규화 문제를 찾아달라고 요청할 수 있습니다.

```
다음 테이블 스키마의 정규화 문제를 찾아주세요:
- 중복 저장되는 데이터가 있나요?
- 이메일, 이름처럼 변경 가능한 값이 여러 곳에 저장되나요?
- 콤마로 구분된 값이 하나의 컬럼에 들어가 있나요?
- 함수 종속 위반이 있나요?

문제를 찾으면 3NF를 기준으로 개선된 스키마를 제안해주세요.
```

AI에게 스키마 마이그레이션을 요청할 때는 기존 데이터 보존 방법도 함께 요청합니다.

```
기존 orders 테이블을 users + products + orders + order_items로 분리하는
마이그레이션 SQL을 작성해주세요.
기존 데이터가 손실 없이 새 구조로 이전되어야 합니다.
```

## 체크리스트

- [ ] 모든 컬럼이 원자 값을 가지는가?
- [ ] 부분 종속과 이행 종속이 제거되었는가?
- [ ] 외래키 제약이 실제로 켜져 있는가?
- [ ] 비정규화 컬럼이 있다면 갱신 책임이 명확한가?
- [ ] AI가 만든 스키마에서 같은 정보가 여러 테이블에 중복되는지 확인했는가?

## 처음 질문으로 돌아가기

- **함수 종속은 어떤 직관으로 이해하면 좋을까요?**
  X가 결정되면 Y도 결정된다는 관계입니다. 사용자 ID가 결정되면 이메일도 결정되므로, 이메일은 사용자 ID에 함수 종속됩니다. 이런 정보는 같은 테이블에 중복해서 저장하면 안 됩니다.

- **AI가 만든 스키마에서 정규화 위반을 어떻게 찾을까요?**
  같은 값(이메일, 이름, 가격)이 여러 행이나 여러 테이블에 반복되는지 확인합니다. 하나의 값을 바꾸려면 몇 곳을 수정해야 하는지 생각해보면 금방 드러납니다.

- **비정규화는 언제 정당화될까요?**
  분석 조회가 매우 빈번하고 JOIN 비용이 반복적으로 문제가 될 때, 측정 결과를 기반으로 읽기 모델에 한해 제한적으로 적용합니다. 쓰기 모델의 정합성은 정규화된 구조에서 유지합니다.

## 정리

정규화는 함수 종속을 따라 모델을 분리해 "각 사실은 한 곳에만 존재한다"는 원칙을 지키는 작업입니다. AI가 만든 스키마가 이 원칙을 얼마나 지키는지 확인하고, 중복이 있다면 마이그레이션으로 정리하는 것이 장기적으로 데이터 품질을 지키는 가장 효과적인 방법입니다. 다음 글에서는 이렇게 만든 모델과 인덱스를 바탕으로 옵티마이저가 어떻게 빠른 계획을 고르는지 살펴봅니다.

## 참고 자료

- [database-systems-101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/database-systems-101/ko)
- [Wikipedia — Database Normalization](https://en.wikipedia.org/wiki/Database_normalization)
- [PostgreSQL — Data Modeling](https://www.postgresql.org/docs/current/ddl.html)
- [Designing Data-Intensive Applications — Chapter 2](https://dataintensive.net/)
- [Microsoft — Description of the database normalization basics](https://learn.microsoft.com/en-us/office/troubleshoot/access/database-normalization-description)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 데이터베이스 시스템 기초 (1/10): 데이터베이스 시스템이란 무엇인가?
- 바이브코딩을 위한 데이터베이스 시스템 기초 (2/10): 관계형 모델
- 바이브코딩을 위한 데이터베이스 시스템 기초 (3/10): SQL과 쿼리 처리
- 바이브코딩을 위한 데이터베이스 시스템 기초 (4/10): 인덱스
- 바이브코딩을 위한 데이터베이스 시스템 기초 (5/10): 트랜잭션과 ACID
- 바이브코딩을 위한 데이터베이스 시스템 기초 (6/10): 격리 수준
- **바이브코딩을 위한 데이터베이스 시스템 기초 (7/10): 정규화와 모델링 (현재 글)**
- 바이브코딩을 위한 데이터베이스 시스템 기초 (8/10): 쿼리 최적화
- 바이브코딩을 위한 데이터베이스 시스템 기초 (9/10): 복제와 백업
- 바이브코딩을 위한 데이터베이스 시스템 기초 (10/10): OLTP와 OLAP

<!-- toc:end -->

Tags: 바이브코딩, Computer Science, Database, 정규화, 모델링, 1NF, 의존성
