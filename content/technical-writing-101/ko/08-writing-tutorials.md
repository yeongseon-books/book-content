---
series: technical-writing-101
episode: 8
title: "Technical Writing 101 (8/10): 튜토리얼 작성하기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - TechnicalWriting
  - Tutorial
  - Learning
  - HandsOn
  - Beginner
seo_description: 독자가 따라 하기만 해도 첫 성공을 경험하도록 돕는 튜토리얼 작성법을 배웁니다. 전제 조건, 단계별 설계, 오류 복구 등 실전 팁을 담았습니다.
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (8/10): 튜토리얼 작성하기

튜토리얼을 쓰다 보면 설명을 더해야 안심이 됩니다. 그런데 독자는 지금 모든 배경을 배우러 온 것이 아니라, 손을 움직여 첫 성공을 확인하러 온 경우가 많습니다. 그래서 튜토리얼은 설명의 완전성보다 성공 경로의 안정성을 먼저 설계해야 합니다.

이 글은 기술 글쓰기 101 시리즈의 8번째 글입니다.

좋은 튜토리얼은 단계가 짧고, 검증 지점이 분명하고, 막히는 지점에서 바로 복구 힌트를 줍니다. 독자가 중간에 실패하더라도 무엇을 다시 확인해야 하는지 한 줄이라도 보여 주면 완주율이 크게 달라집니다.

여기서는 첫 성공을 빠르게 만들고 검증 가능한 단계로 나누는 튜토리얼 설계법을 정리합니다.

![Technical Writing 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/08/08-01-concept-at-a-glance.ko.png)
*Technical Writing 101 8장 흐름 개요*
> 튜토리얼은 독자가 지금 무엇을 해야 하는지 한 단계씩 따라갈 수 있게 만드는 안내선입니다.

## 이 글에서 다룰 문제

- 따라 하기 글은 설명 글이나 레퍼런스와 무엇이 다를까요?
- 독자가 따라만 해도 동작하는 튜토리얼은 어떻게 만들까요?
- 전제 조건, 작은 성공, 복구 안내, 다음 단계는 어떤 순서로 놓여야 할까요?
- 완주율을 높이는 단계 설계는 어떻게 해야 할까요?
- 튜토리얼을 유지보수 가능하게 만드는 방법은 무엇일까요?

## 이 글에서 배울 것

- Diátaxis에서 튜토리얼의 자리
- 전제 조건 적는 방법
- 작은 성공(small win) 설계하기
- 오류 복구 메모 작성 패턴
- 다음 단계 연결 전략

첫 성공은 계속 배우고 싶게 만드는 힘을 줍니다. 그래서 좋은 튜토리얼은 완전한 설명보다 빠른 성공을 먼저 설계합니다.

## 한눈에 보는 멘탈 모델

> 멘탈 모델: 튜토리얼은 강의문이 아니라 안내선입니다. 전제 조건을 먼저 밝히고, 한 단계씩 따라가게 하고, 작은 성공을 빠르게 보여 준 뒤, 다음 학습으로 넘깁니다.

- **tutorial**: 학습 지향 글입니다.
- **prerequisite**: 전제 조건입니다.
- **small win**: 작은 성공입니다.
- **recovery**: 오류 복구 경로입니다.
- **next step**: 다음에 배울 주제입니다.

## 튜토리얼 흐름 구조

```
[전제 조건]
  ─ Python 버전, 운영체제, 준비물
  ─ 예상 소요 시간
        │
        ▼
[단계 1] 명령 + 확인 지점
        │
        ▼
[단계 2] 명령 + 확인 지점
        │
        ▼
[단계 3] 명령 + 확인 지점  ← 이 지점에서 첫 성공 경험
        │
        ▼
[오류 해결] 자주 발생하는 오류 2-3개 + 복구 명령
        │
        ▼
[다음 단계] 확장 과제, 관련 How-to, 공식 레퍼런스
```

각 단계는 독자가 무엇을 해야 하는지와 성공했는지 확인하는 방법을 모두 담아야 합니다.

## Before / After 비교: 튜토리얼 설계 방식

### Before / After 예시 1: 강의문 vs 안내선

**Before — 설명 중심 강의문**

"FastAPI는 Python 기반의 현대적 웹 프레임워크입니다. ASGI를 지원하며 자동 문서화 기능이 내장되어 있습니다. Pydantic을 사용하여 데이터 검증을 처리하고, Python 타입 힌트를 기반으로 동작합니다..."

독자는 배경 설명을 읽느라 손을 놀리지 못합니다.

**After — 행동 중심 안내선**

```
이 튜토리얼이 끝나면 FastAPI 서버가 로컬에서 실행되고
브라우저에서 JSON 응답을 확인할 수 있습니다. 소요 시간: 5분.
```

무엇을 얻을지 먼저 밝히면 독자는 바로 첫 단계로 이동합니다.

---

### Before / After 예시 2: 확인 지점 없음 vs 검증 지점 포함

**Before — 확인 지점이 없는 단계**

```
1단계: FastAPI를 설치합니다.
2단계: main.py를 만듭니다.
3단계: 서버를 실행합니다.
```

독자는 각 단계에서 성공했는지 확인할 방법이 없습니다.

**After — 검증 지점이 포함된 단계**

```bash
# 1단계 — FastAPI 설치
pip install "fastapi[standard]"
```

```text
Successfully installed fastapi ...
```

**확인**: 터미널에 `Successfully installed`가 보이면 다음 단계로 진행합니다.

각 단계에 확인 지점을 넣으면 독자가 스스로 성공 여부를 판단할 수 있습니다.

---

### Before / After 예시 3: 오류 복구 안내 없음 vs 복구 힌트 포함

**Before — 오류 발생 시 안내 없음**

```bash
fastapi dev main.py
```

`fastapi: command not found`가 나오면 독자는 구글로 이동합니다.

**After — 자주 발생하는 오류와 복구 힌트 포함**

```bash
fastapi dev main.py
```

복구 힌트:
- `fastapi: command not found` → `pip install "fastapi[standard]"` 다시 실행
- `ModuleNotFoundError: No module named 'fastapi'` → 가상 환경 활성화 후 재설치
- `Address already in use` → `fastapi dev main.py --port 8001` 로 포트 변경

## 문서 템플릿: 5분 튜토리얼 구조

```markdown
# [튜토리얼 제목]

이 튜토리얼이 끝나면 [독자가 얻는 것]을 확인할 수 있습니다. 소요 시간: [N분].

## 전제 조건

- Python [버전] 이상
- 터미널 접근 가능
- [기타 필요 도구]

## 1단계 — [단계 이름]

```bash
[명령]
```

**확인**: [성공 시 터미널에 보여야 하는 출력 또는 상태].

## 2단계 — [단계 이름]

```bash
[명령]
```

**확인**: [성공 지점].

## 3단계 — 첫 성공 확인

```bash
[최종 실행 명령]
```

```text
[기대 출력]
```

**확인**: [성공 기준].

## 오류 해결

- `[오류 메시지]` → [복구 명령]
- `[오류 메시지]` → [복구 명령]

## 다음 단계

- [[확장 과제]](링크)
- [[관련 How-to]](링크)
- [[공식 레퍼런스]](링크)
```

## 튜토리얼 vs How-to vs Reference

| 항목 | Tutorial | How-to | Reference |
| --- | --- | --- | --- |
| **목적** | 처음 배우기 | 특정 문제 해결 | 전체 사양 확인 |
| **독자 상태** | 초보, 이해 필요 | 중급, 특정 목표 있음 | 숙련, 빠른 참조 |
| **구조** | 순차적 단계 | 문제 → 해결 | 알파벳 또는 분류 |
| **분량** | 5-10분 분량 | 2-5분 분량 | 전체 API 커버 |
| **톤** | 친근하고 설명적 | 직접적이고 명령적 | 간결하고 정확 |
| **예시** | "FastAPI 첫 단계" | "CORS 설정 방법" | "FastAPI API 문서" |

## 완주율을 높이는 단계 설계

| 단계 | 최대 소요 시간 | 필수 요소 |
| --- | --- | --- |
| 전제 조건 확인 | 1분 | 버전, 운영체제, 준비물 |
| 설치 | 2분 | 명령 1-3개 |
| 코드 작성 | 3분 | 20줄 이하 MWE |
| 실행 검증 | 2분 | 기대 출력 |
| 오류 복구 | 2분 | 자주 실패하는 2-3개 케이스 |

전체 10분 안에 첫 성공을 만들어야 튜토리얼이 효과적입니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 바로 고치는 방법 |
| --- | --- | --- |
| 전제 조건이 없습니다 | 독자가 어느 환경에서 시작해야 하는지 모릅니다 | Python 버전, OS, 준비물을 문서 상단에 명시합니다 |
| 명령 순서가 틀립니다 | 중간 단계에서 오류가 발생하고 독자가 이탈합니다 | 새 환경에서 직접 따라가며 명령 순서를 검증합니다 |
| 작은 성공이 없습니다 | 독자가 오래 기다리다 포기합니다 | 3분 안에 기대 출력을 확인하는 단계를 배치합니다 |
| 오류 복구 메모가 없습니다 | 독자가 막히면 구글로 이탈합니다 | 자주 발생하는 오류 2-3개와 복구 명령을 추가합니다 |
| 다음 단계가 없습니다 | 튜토리얼 완료 후 학습이 끊깁니다 | 확장 과제, How-to, 공식 레퍼런스 링크를 제공합니다 |
| 버전을 명시하지 않습니다 | 라이브러리가 업데이트되면 명령이 달라집니다 | 패키지 버전과 Python 버전을 전제 조건에 명시합니다 |

## 운영 체크리스트

- [ ] 전제 조건(버전, OS)이 적혀 있는가
- [ ] 단계 수가 다섯 개 이하인가
- [ ] 각 단계에 확인 지점이 있는가
- [ ] 첫 성공이 3분 안에 나오는가
- [ ] 자주 발생하는 오류 2-3개와 복구 힌트가 있는가
- [ ] 다음 단계 링크가 있는가

## 연습 문제

1. 튜토리얼과 How-to 가이드의 차이를 한 문장으로 설명하세요.
2. 다음 단계에서 무엇이 빠졌는지 찾아보세요.
   ```
   1단계: pip install fastapi
   2단계: main.py를 만듭니다.
   3단계: uvicorn main:app --reload
   ```
3. "5분 안에 첫 성공"을 보장하는 튜토리얼 구조의 핵심 세 가지를 적어 보세요.

## 정리

튜토리얼은 설명을 많이 하는 글이 아니라, 독자가 따라 하며 첫 성공을 얻는 글입니다. 전제 조건, 단계 순서, 검증 지점, 복구 안내, 다음 단계가 모두 갖춰져야 완주율이 높아집니다. 각 단계를 10분 안에 끝낼 수 있도록 설계하고, 오류 복구 힌트를 미리 준비해 두면 독자는 구글 없이 튜토리얼 안에서 문제를 해결할 수 있습니다. 다음 글에서는 개인 경험을 담는 블로그와 팀의 공식 기준을 담는 문서를 어떻게 구분할지 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Technical Writing 101 (1/10): 기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- [Technical Writing 101 (2/10): 독자 정의하기](./02-defining-the-reader.md)
- [Technical Writing 101 (3/10): 제목과 구조 잡기](./03-title-and-structure.md)
- [Technical Writing 101 (4/10): 개념 설명하기](./04-explaining-concepts.md)
- [Technical Writing 101 (5/10): 예제 코드 설명하기](./05-explaining-example-code.md)
- [Technical Writing 101 (6/10): 그림과 표 사용하기](./06-using-figures-and-tables.md)
- [Technical Writing 101 (7/10): README 작성하기](./07-writing-the-readme.md)
- **Technical Writing 101 (8/10): 튜토리얼 작성하기 (현재 글)**
- [Technical Writing 101 (9/10): 블로그와 문서 차이](./09-blog-vs-docs.md)
- [발행 전 체크리스트](./10-pre-publish-checklist.md)

<!-- toc:end -->

## 참고 자료

- [Diátaxis Framework](https://diataxis.fr/)
- [Django Tutorial Style](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Teach Tech with Tutorials - Write the Docs](https://www.writethedocs.org/guide/writing/beginners-guide-to-docs/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/technical-writing-101/ko)

Tags: TechnicalWriting, Tutorial, Learning, HandsOn, Beginner
