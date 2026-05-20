---
series: computer-science-major-101
episode: 8
title: "Computer Science Major 101 (8/10): 전공 공부 방법"
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
  - Study
  - Habit
  - Learning
  - Beginner
seo_description: 전공 학습 루틴, 강의 노트, 복습 주기, 코딩 연습, 질문 습관을 정리한 글
code_required: false
last_reviewed: '2026-05-14'
---

# Computer Science Major 101 (8/10): 전공 공부 방법

같은 시간을 써도 어떤 학생은 개념이 남고, 어떤 학생은 강의 직후부터 빠르게 잊어버립니다. 차이를 만드는 것은 재능보다 공부 방법의 구조인 경우가 많습니다.

이 글은 Computer Science Major 101 시리즈의 8번째 글입니다.

## 먼저 던지는 질문

- 같은 시간을 써도 공부 방법에 따라 결과가 크게 달라지는 이유는 무엇일까요?
- 강의, 노트, 복습, 코딩 연습은 어떤 흐름으로 묶는 것이 좋을까요?
- 시험 직전 몰아서 하는 공부가 전공 과목에서 특히 잘 통하지 않는 이유는 무엇일까요?

## 큰 그림

![Computer Science Major 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/08/08-01-study-loop.ko.png)

*Computer Science Major 101 8장 흐름 개요*

이 그림에서는 전공 공부 방법를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 전공 공부 방법의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 이 글에서 배울 것

- 주간 루틴
- 강의 노트
- 복습 주기
- 코딩 드릴
- 질문하는 습관

## 왜 중요한가

전공에서는 남은 차이를 만드는 요소가 공부 효율인 경우가 많습니다. 같은 강의를 들어도 복습 간격, 실습 빈도, 질문 습관이 다르면 이해 속도와 유지 시간이 크게 달라집니다.

## 한눈에 보는 개념

> 전공 공부는 강의를 듣는 순간 끝나는 일이 아니라, 다시 꺼내 보고 손으로 확인하는 순환 구조입니다.

강의를 듣는 순간이 끝이 아니라 시작입니다. 노트로 압축하고, 복습으로 다시 꺼내고, 연습으로 손을 움직이고, 질문으로 막힌 부분을 푸는 흐름이 반복되어야 실력이 붙습니다.

## 핵심 용어

- **루틴(routine)**: 반복 가능한 학습 일정입니다.
- **노트(note)**: 핵심을 짧게 정리한 기록입니다.
- **복습(review)**: 이미 본 내용을 다시 확인하는 과정입니다.
- **드릴(drill)**: 반복 연습 문제입니다.
- **오피스 아워(office hour)**: 교수나 조교에게 질문할 수 있는 시간입니다.

## Before/After

**Before**: 시험 직전에만 몰아서 공부합니다.

**After**: 주간 루틴 안에 강의와 복습과 연습을 분산합니다.

## 실습: 주간 복습 루프 추적기

전공 공부는 총 몇 시간을 했는지보다, 강의를 들은 뒤 언제 다시 꺼내 봤고 어떤 질문이 남았는지를 추적해야 오래 남습니다. 아래 예시는 한 주치 학습 기록에서 복습 일정, 완료 여부, 과목별 총량, 약한 영역을 함께 보여 주는 간단한 추적기입니다.

```python
from collections import defaultdict
from datetime import date, timedelta

sessions = [
    {
        "course": "algorithms",
        "lecture_date": date(2026, 5, 4),
        "study_minutes": 100,
        "review_completed": True,
        "questions": ["Why does merge sort stay O(n log n)?"],
    },
    {
        "course": "operating-systems",
        "lecture_date": date(2026, 5, 5),
        "study_minutes": 60,
        "review_completed": False,
        "questions": ["What exactly causes context-switch overhead?"],
    },
    {
        "course": "databases",
        "lecture_date": date(2026, 5, 6),
        "study_minutes": 45,
        "review_completed": False,
        "questions": [],
    },
]

def build_weekly_report(entries):
    totals = defaultdict(int)
    weak_areas = []
    lines = []

    for entry in entries:
        next_review = entry["lecture_date"] + timedelta(days=2)
        totals[entry["course"]] += entry["study_minutes"]
        status = "done" if entry["review_completed"] else "pending"
        lines.append(
            f"{entry['course']}: lecture={entry['lecture_date']}, "
            f"next_review={next_review}, review={status}, "
            f"questions={len(entry['questions'])}"
        )

    for course, minutes in totals.items():
        if minutes < 90 or any(
            e["course"] == course and not e["review_completed"] for e in entries
        ):
            weak_areas.append(course)

    summary = ", ".join(f"{course}={minutes}m" for course, minutes in totals.items())
    weak_summary = ", ".join(weak_areas) if weak_areas else "none"
    return "\n".join(lines + [f"weekly_totals: {summary}", f"weak_areas: {weak_summary}"])

print(build_weekly_report(sessions))
```

예시 입력을 실행하면 다음처럼 관찰 가능한 출력이 나옵니다.

```text
algorithms: lecture=2026-05-04, next_review=2026-05-06, review=done, questions=1
operating-systems: lecture=2026-05-05, next_review=2026-05-07, review=pending, questions=1
databases: lecture=2026-05-06, next_review=2026-05-08, review=pending, questions=0
weekly_totals: algorithms=100m, operating-systems=60m, databases=45m
weak_areas: operating-systems, databases
```

이 출력에서 바로 확인할 수 있는 것은 세 가지입니다. 언제 복습해야 하는지, 아직 풀지 못한 질문이 어디 남아 있는지, 그리고 어느 과목이 이번 주에 실제로 약하게 굴러갔는지입니다. 이렇게 봐야 간격 복습, 질문 습관, 시간 배분이 하나의 루프로 연결됩니다.

## 이 코드에서 먼저 볼 점

- 강의 날짜와 다음 복습 날짜가 함께 있어야 간격 학습이 실행 계획으로 바뀝니다.
- review 완료 여부와 질문 수를 같이 봐야 이해 부족이 어디에 남았는지 드러납니다.
- 주간 총량과 미복습 상태를 함께 봐야 진짜 약한 과목을 찾을 수 있습니다.

## 자주 하는 실수 5가지

1. **노트를 받아 적기만 하고 다시 보지 않는 일입니다.**
2. **복습 없이 진도만 따라가는 일입니다.**
3. **코딩 연습을 시험 직전으로 미루는 일입니다.**
4. **질문을 부끄러워해서 오래 끌고 가는 일입니다.**
5. **수면 시간을 줄여 공부량만 늘리는 일입니다.**

## 실무에서는 이렇게 드러납니다

신입 엔지니어의 성장 속도는 종종 질문 빈도와 기록 습관에서 드러납니다. 막히는 지점을 빨리 드러내고, 해결 과정을 남기고, 같은 실수를 줄이는 사람이 훨씬 빠르게 적응합니다.

## 일주일 루틴 예시

아래 표는 거창한 완벽 루틴이 아니라, 전공 과목 세 개를 동시에 굴릴 때 최소한 어떤 흐름이 있어야 하는지 보여 주는 예시입니다. 핵심은 오래 버티는 주간 리듬을 만드는 것입니다.

| 요일 | 해야 할 일 | 이유 |
| --- | --- | --- |
| 월요일 | 강의 직후 핵심 개념 3줄 요약 | 기억이 가장 선명할 때 압축해야 노트가 살아 있습니다. |
| 화요일 | 알고리즘 또는 프로그래밍 실습 1시간 | 손을 움직이지 않으면 이해가 실행 능력으로 바뀌지 않습니다. |
| 수요일 | 운영체제·데이터베이스처럼 개념 과목 복습 | 이론 과목은 간격을 두고 다시 봐야 오래 남습니다. |
| 목요일 | 질문 목록 정리 후 교수·조교·동료에게 확인 | 막힌 지점을 일주일 안에 푸는 습관이 중요합니다. |
| 금요일 | 이번 주 학습 시간과 약한 과목 점검 | 숫자로 보면 과목별 편향이 바로 드러납니다. |
| 주말 | 다음 주 예습 30분 + 밀린 과제 마무리 | 주말은 새 학습보다 누적 정리에 쓰는 편이 안정적입니다. |

이 표를 그대로 따라야 한다는 뜻은 아닙니다. 다만 강의, 복습, 실습, 질문, 점검이 한 주 안에서 모두 한 번 이상 돌아야 전공 공부가 단발성 이벤트가 아니라 누적형 습관이 됩니다.

## 선배 엔지니어는 이렇게 봅니다

- 재능보다 루틴이 오래 갑니다.
- 기록은 쌓일수록 복리처럼 작동합니다.
- 질문은 약점이 아니라 학습 도구입니다.
- 잠을 줄여 만든 성과는 오래 버티기 어렵습니다.
- 복습이 있어야 배운 내용이 자기 것이 됩니다.

## 체크리스트

- [ ] 주간 루틴을 적어 보았습니다.
- [ ] 노트 정리 형식을 하나 정했습니다.
- [ ] 복습 주기를 만들었습니다.
- [ ] 질문 목록을 따로 적기 시작했습니다.

## 연습 문제

1. 루틴을 한 줄로 설명해 보세요.
2. 복습의 의미를 한 줄로 적어 보세요.
3. 오피스 아워를 어떻게 활용할지 한 줄로 써 보세요.

## 정리

전공 공부는 의욕만으로 오래 버티기 어렵습니다. 강의, 노트, 복습, 연습, 질문이 하나의 흐름으로 묶여야 누적이 생깁니다. 같은 시간을 써도 방법이 다르면 결과는 크게 달라집니다. 다음 글에서는 과제와 프로젝트를 밖에서 읽히는 포트폴리오로 바꾸는 방법을 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **같은 시간을 써도 공부 방법에 따라 결과가 크게 달라지는 이유는 무엇일까요?**
  - 본문의 기준은 전공 공부 방법를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **강의, 노트, 복습, 코딩 연습은 어떤 흐름으로 묶는 것이 좋을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **시험 직전 몰아서 하는 공부가 전공 과목에서 특히 잘 통하지 않는 이유는 무엇일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Science Major 101 (1/10): 컴퓨터학과에서는 무엇을 배우는가](./01-what-cs-majors-learn.md)
- [Computer Science Major 101 (2/10): 1학년 과목 이해하기](./02-first-year-subjects.md)
- [Computer Science Major 101 (3/10): 자료구조와 알고리즘](./03-data-structures-and-algorithms.md)
- [Computer Science Major 101 (4/10): 시스템 과목 이해하기](./04-systems-subjects.md)
- [Computer Science Major 101 (5/10): 데이터베이스와 네트워크](./05-database-and-network.md)
- [Computer Science Major 101 (6/10): AI와 데이터사이언스](./06-ai-and-data-science.md)
- [Computer Science Major 101 (7/10): 프로젝트 과목](./07-project-subjects.md)
- **전공 공부 방법 (현재 글)**
- 포트폴리오로 연결하기 (예정)
- 졸업 전 갖춰야 할 역량 (예정)

<!-- toc:end -->

## 참고 자료

- [Make It Stick](https://www.hup.harvard.edu/books/9780674729018)
- [Improving Students' Learning With Effective Learning Techniques](https://journals.sagepub.com/doi/10.1177/1529100612453266)
- [How Learning Works](https://www.wiley.com/en-us/How+Learning+Works%3A+Eight+Research-Based+Principles+for+Smart+Teaching-p-9780470484104)
- [ACM/IEEE-CS/AAAI Computer Science Curricula 2023](https://csed.acm.org/cs2023/)

Tags: CS, Study, Habit, Learning, Beginner
