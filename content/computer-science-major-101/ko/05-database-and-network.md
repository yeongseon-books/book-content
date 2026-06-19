---
series: computer-science-major-101
episode: 5
title: "Computer Science Major 101 (5/10): 데이터베이스와 네트워크"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - CS
  - Database
  - Network
  - SQL
  - Beginner
seo_description: 데이터베이스와 네트워크 과목의 핵심 개념, SQL, TCP/IP, 학습 흐름을 정리한 글
code_required: false
last_reviewed: '2026-05-14'
---

# Computer Science Major 101 (5/10): 데이터베이스와 네트워크

서비스를 만든다는 말은 결국 데이터를 저장하고, 그 데이터를 네트워크를 통해 주고받는다는 뜻입니다. 화면과 코드만으로는 서비스가 완성되지 않는 이유도 여기에 있습니다.

이 글은 컴퓨터학과 전공 학습 가이드 101 시리즈의 5번째 글입니다.

![Computer Science Major 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/05/05-01-request-to-database-flow.ko.png)
*컴퓨터학과 전공 가이드 5장 흐름 개요*

> 서비스는 네트워크가 요청을 옮기고 데이터베이스가 상태를 보관할 때 비로소 완성됩니다.

## 이 글에서 다룰 문제

- 데이터베이스와 네트워크는 왜 거의 모든 서비스의 바닥에 놓일까요?
- SQL, 테이블, 인덱스는 실제 성능과 어떻게 연결될까요?
- TCP/IP와 HTTP는 어떤 층에서 역할을 나눌까요?
- 두 과목을 따로 공부했을 때 실무에서 어떤 패턴으로 막히게 될까요?
- 데이터와 네트워크를 하나의 요청 경로로 연결해 이해하는 방법은 무엇일까요?

## 왜 두 과목을 함께 보아야 하는가

백엔드 코드의 상당수는 결국 데이터베이스와 네트워크를 다룹니다. 많은 장애와 지연도 저장 계층과 통신 계층에서 함께 시작되기 때문에, 두 과목을 따로 배우더라도 머릿속에서는 한 흐름으로 묶어 이해하는 편이 좋습니다.

사용자는 HTTP 요청을 보내고, 서버는 그 요청을 처리한 뒤 SQL로 데이터를 읽거나 씁니다. 이 단순한 경로 안에 지연 시간, 연결 관리, 인덱스, 트랜잭션, 타임아웃 같은 핵심 주제가 모두 들어 있습니다.

- **테이블(table)**: 행과 열로 데이터를 저장하는 구조입니다.
- **기본 키(primary key)**: 각 행을 고유하게 구분하는 값입니다.
- **인덱스(index)**: 더 빠른 조회를 위한 자료구조입니다. B-트리가 일반적입니다.
- **패킷(packet)**: 네트워크에서 데이터를 나눠 보내는 단위입니다.
- **포트(port)**: 연결 대상 서비스를 구분하는 번호입니다. HTTP는 80, HTTPS는 443.

## 왜 여기서 막히는가: 흔한 시나리오

**시나리오 1 — "쿼리는 맞는데 왜 이렇게 느리지?"**

도현은 사용자 목록을 조회하는 API를 만들었습니다. 개발 환경에서는 빠른데 운영 환경에서 데이터가 100만 건 이상이 되자 응답이 5초 이상 걸렸습니다. `SELECT * FROM users WHERE email = ?` 같은 쿼리를 반복적으로 실행하고 있었고, email 컬럼에 인덱스가 없었습니다. 전체 스캔(full scan)이 매 요청마다 발생한 것입니다.

발생 신호: 개발 환경에서는 빠르다가 운영 데이터 양이 늘어나면서 갑자기 느려집니다.

해결 방향: `EXPLAIN` 명령으로 쿼리 실행 계획을 확인하고, 조회 조건에 인덱스를 추가해야 합니다. 읽기 성능과 쓰기 비용을 함께 고려해야 합니다.

**시나리오 2 — "API가 가끔 타임아웃 난다"**

지민은 외부 결제 API를 호출하는 코드를 작성했습니다. 대부분 정상이지만 가끔 30초 이상 응답이 없어 타임아웃이 났습니다. 타임아웃 설정을 아예 해 두지 않았기 때문에 스레드가 무한 대기했습니다. 네트워크 계층의 연결 제어 개념이 없었기 때문입니다.

발생 신호: API 응답이 가끔 오래 걸리고, 기다리는 동안 다른 요청도 지연됩니다.

해결 방향: 외부 I/O에는 항상 타임아웃을 설정하고, 재시도 정책(retry)과 서킷 브레이커(circuit breaker)를 함께 설계해야 합니다.

**시나리오 3 — "N+1 문제를 코드 리뷰에서 지적받았다"**

아름은 게시글 목록을 불러올 때 각 게시글의 작성자 정보를 별도 쿼리로 가져왔습니다. 게시글이 100개이면 쿼리가 101번 실행되었습니다. 조인(JOIN)을 쓰면 한 번에 가져올 수 있는 데이터를 반복 조회한 전형적인 N+1 패턴입니다.

발생 신호: 슬로우 쿼리 로그를 보면 동일한 단순 쿼리가 수백 번 연속으로 나타납니다.

해결 방향: ORM을 쓰더라도 생성되는 SQL을 직접 확인하는 습관이 필요합니다. `JOIN` 또는 별도 배치 조회로 해결합니다.

## SQL과 소켓 감각 익히기

```python
import sqlite3
import urllib.request

# 1단계 — 인메모리 DB 생성
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE users(id INT, name TEXT, email TEXT)")

# 2단계 — 데이터 삽입
con.execute("INSERT INTO users VALUES (1, 'kim', 'kim@example.com')")
con.execute("INSERT INTO users VALUES (2, 'lee', 'lee@example.com')")
con.commit()

# 3단계 — 조회: WHERE 없이 전체 스캔
rows_all = con.execute("SELECT * FROM users").fetchall()
print(f"전체 조회: {len(rows_all)}건")

# 4단계 — 조회: 인덱스 없는 필터 vs 인덱스 있는 필터
# 인덱스 없는 경우 → 전체 스캔
row = con.execute("SELECT * FROM users WHERE email = 'kim@example.com'").fetchone()

# 인덱스 추가
con.execute("CREATE INDEX idx_email ON users(email)")

# 인덱스 있는 경우 → 빠른 탐색
row_fast = con.execute("SELECT * FROM users WHERE email = 'kim@example.com'").fetchone()
print(f"조회 결과: {row_fast}")

# 5단계 — HTTP 호출: 네트워크도 측정 가능한 자원
import time
t = time.perf_counter()
status = urllib.request.urlopen("http://example.com").status
elapsed = time.perf_counter() - t
print(f"HTTP {status}, 지연: {elapsed:.3f}s")
```

이 코드에서 주목할 점:
- 데이터베이스 연결은 세션 단위로 관리됩니다.
- 인덱스는 읽기를 빠르게 하지만 쓰기 비용이 있습니다.
- HTTP 상태 코드와 응답 시간은 모두 측정 가능한 자원입니다.

## 이 과목이 실무에서 어떻게 쓰이는가

**슬로우 쿼리 분석**: 운영 DB에는 항상 슬로우 쿼리 로그를 켜 둡니다. 느린 쿼리 상위 5개를 찾아 `EXPLAIN`으로 실행 계획을 보고, 풀 스캔이 있으면 인덱스 추가를 검토합니다.

**네트워크 지연 분해**: 사용자 체감 지연을 DNS + TLS + 애플리케이션 처리 + DB 조회 + 응답 전송으로 나눠 각 구간을 측정합니다. 이 분해 없이는 DB만 튜닝했는데 실제 병목이 네트워크였던 상황이 반복됩니다.

**트랜잭션 경계 설계**: 여러 테이블을 동시에 변경하는 작업은 트랜잭션으로 묶어야 합니다. 일부만 성공한 상태가 되면 데이터 일관성이 깨집니다.

| 실무 상황 | 핵심 개념 | 관련 도구 |
| --- | --- | --- |
| 쿼리 성능 저하 | 풀 스캔 vs 인덱스 탐색 | EXPLAIN, slow query log |
| 외부 API 타임아웃 | TCP 연결 타임아웃, 재시도 | 연결 풀, circuit breaker |
| N+1 쿼리 문제 | JOIN, 배치 조회 | ORM 쿼리 로그 |
| 데이터 중복/불일치 | 트랜잭션, 제약 조건 | ACID, 외래 키 |
| API 응답 지연 분석 | 요청 경로 구간 분해 | APM, 분산 추적 |

## 네트워크 계층 구조와 역할 분담

| 계층/구성 | 대표 프로토콜 | 핵심 역할 | 흔한 오해 |
| --- | --- | --- | --- |
| 애플리케이션 | HTTP, gRPC | API 계약, 상태 코드, 직렬화 | HTTP가 전송 신뢰성까지 보장한다고 생각함 |
| 전송 | TCP, UDP | 연결/재전송/흐름제어 | TCP와 HTTP 역할 경계를 혼동함 |
| 네트워크 | IP | 경로 선택, 주소 기반 전달 | 라우팅 문제를 앱 로직으로 해결하려 함 |
| 링크 | Ethernet, Wi-Fi | 물리/링크 전달 | 상위 계층 지연을 링크 탓으로 단정함 |

## 데이터베이스 유형 비교

| 유형 | 강점 | 약점 | 적합한 상황 |
| --- | --- | --- | --- |
| 관계형(RDBMS) | 강한 일관성, SQL 생태계 | 스키마 변경 비용 | 트랜잭션 중심 서비스 |
| 키-값 저장소 | 매우 빠른 단순 조회 | 복잡 질의 어려움 | 세션, 캐시 |
| 문서형(Document) | 유연한 스키마 | 조인/일관성 설계 주의 | 빠른 제품 반복 |
| 그래프 DB | 관계 탐색 강점 | 운영/인력 비용 | 추천, 관계 분석 |

정규화는 시험용 규칙이 아니라 변경 비용 관리 도구입니다. 실전에서는 조회 성능을 위해 의도적 비정규화를 일부 도입하기도 합니다. 중요한 것은 원칙을 먼저 이해하고, 이후 트레이드오프를 문서화하는 태도입니다.

## 요청-응답 경로 병목 분해 템플릿

DB와 네트워크를 함께 학습할 때는 요청 경로를 시간 축으로 분해해야 병목을 정확히 찾을 수 있습니다.

| 구간 | 정상 기준(예시) | 경고 신호 | 점검 도구 |
| --- | --- | --- | --- |
| DNS+연결 | 20~80ms | 간헐적 급증 | traceroute, DNS 로그 |
| 애플리케이션 처리 | 30~150ms | CPU 급등 | APM, 프로파일러 |
| DB 조회 | 10~120ms | 슬로우 쿼리 증가 | EXPLAIN, slow query log |
| 응답 전송 | 5~50ms | 재전송 다수 | 네트워크 지표 |

SQL 튜닝은 체감이 아니라 비교로 수행해야 합니다. 인덱스 추가 전후 `EXPLAIN` 결과, 평균 지연, p95를 같은 표로 남기면 팀 내 의사결정이 빨라집니다.

## 실전 점검 루프

- 슬로우 쿼리 로그로 상위 5개 쿼리부터 파악
- API 지연 시간 분해: 네트워크 대기/애플리케이션 처리/DB 처리
- 인덱스 추가 전후 `EXPLAIN` 비교 기록
- 타임아웃·재시도 정책을 프로토콜 책임과 분리해서 설계

이 루프를 반복하면 데이터베이스 과목과 네트워크 과목이 실제 서비스 운영 역량으로 결합됩니다.

## 자주 하는 실수 5가지

1. **WHERE 없이 전체 스캔을 반복하는 일입니다.** 데이터가 늘면 선형적으로 느려집니다.
2. **N+1 쿼리 패턴을 놓치는 일입니다.** ORM을 쓸 때 특히 발생하기 쉽습니다.
3. **트랜잭션 없이 동시 쓰기를 처리하려는 일입니다.** 부분 성공 상태가 발생할 수 있습니다.
4. **연결 풀 없이 요청마다 새 연결을 만드는 일입니다.** DB 연결 비용이 상당하며 한도가 있습니다.
5. **포트와 프로토콜을 같은 개념처럼 혼동하는 일입니다.** 포트는 주소이고, 프로토콜은 통신 규칙입니다.

## 운영 체크리스트

- [ ] 어떤 컬럼에 인덱스가 필요한지 생각해 보았습니다.
- [ ] 트랜잭션 경계를 한 번 적어 보았습니다.
- [ ] 연결 풀의 필요성을 이해했습니다.
- [ ] 네트워크 타임아웃 설정의 의미를 설명할 수 있습니다.
- [ ] 슬로우 쿼리 로그 확인 방법을 알고 있습니다.

## 처음 질문으로 돌아가기

- **데이터베이스와 네트워크는 왜 거의 모든 서비스의 바닥에 놓일까요?**
  - 사용자 요청은 네트워크로 들어오고, 서비스의 상태는 데이터베이스에 보관됩니다. 이 두 계층 없이는 사용자가 다음번에 접속했을 때 이전 상태를 불러올 수 없습니다.

- **SQL, 테이블, 인덱스는 실제 성능과 어떻게 연결될까요?**
  - 인덱스가 없는 컬럼으로 필터링하면 데이터가 100만 건일 때 100만 번 비교가 필요합니다. 인덱스가 있으면 B-트리 탐색으로 약 20번 비교로 줄어듭니다. 같은 쿼리라도 성능이 수십 배 차이날 수 있습니다.

- **TCP/IP와 HTTP는 어떤 층에서 역할을 나눌까요?**
  - TCP는 신뢰성 있는 연결과 데이터 전달을 담당합니다. HTTP는 TCP 위에서 동작하며 요청/응답의 의미(메서드, 상태 코드, 헤더)를 정의합니다. HTTP가 빠르게 전달되려면 TCP 연결이 먼저 안정적이어야 합니다.

- **두 과목을 따로 공부했을 때 실무에서 어떤 패턴으로 막히게 될까요?**
  - 도현 시나리오처럼 쿼리 자체는 맞지만 네트워크 왕복 횟수(N+1)를 보지 못하거나, 지민 시나리오처럼 타임아웃 설정 없이 외부 API를 호출하는 패턴이 나타납니다.

- **데이터와 네트워크를 하나의 요청 경로로 연결해 이해하는 방법은 무엇일까요?**
  - 요청 경로를 구간별로 분해하는 습관이 핵심입니다. DNS, TLS, 애플리케이션, DB, 응답 전송 각 구간의 지연을 측정하면 어디가 병목인지 감이 아닌 수치로 판단할 수 있습니다.

## 정리

데이터베이스와 네트워크는 각각 저장과 전달을 담당하지만, 실제 서비스에서는 거의 하나의 흐름처럼 움직입니다. 데이터를 어디에 어떻게 보관할지, 요청을 어떤 규칙으로 주고받을지를 함께 이해해야 서비스의 속도와 안정성을 설명할 수 있습니다. 다음 글에서는 데이터와 모델을 다루는 AI와 데이터사이언스로 넘어가겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Science Major 101 (1/10): 컴퓨터학과에서는 무엇을 배우는가](./01-what-cs-majors-learn.md)
- [Computer Science Major 101 (2/10): 1학년 과목 이해하기](./02-first-year-subjects.md)
- [Computer Science Major 101 (3/10): 자료구조와 알고리즘](./03-data-structures-and-algorithms.md)
- [Computer Science Major 101 (4/10): 시스템 과목 이해하기](./04-systems-subjects.md)
- **Computer Science Major 101 (5/10): 데이터베이스와 네트워크 (현재 글)**
- [Computer Science Major 101 (6/10): AI와 데이터사이언스](./06-ai-and-data-science.md)
- [Computer Science Major 101 (7/10): 프로젝트 과목](./07-project-subjects.md)
- [Computer Science Major 101 (8/10): 전공 공부 방법](./08-how-to-study-cs.md)
- [Computer Science Major 101 (9/10): 포트폴리오로 연결하기](./09-build-your-portfolio.md)
- [Computer Science Major 101 (10/10): 졸업 전 갖춰야 할 역량](./10-skills-before-graduation.md)

<!-- toc:end -->

## 참고 자료

- [Database System Concepts](https://www.db-book.com/)
- [SQLite Documentation](https://sqlite.org/docs.html)
- [Computer Networking: A Top-Down Approach](https://gaia.cs.umass.edu/kurose_ross/index.php)
- [MDN HTTP Overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-major-101/ko)

Tags: CS, Database, Network, SQL, Beginner
