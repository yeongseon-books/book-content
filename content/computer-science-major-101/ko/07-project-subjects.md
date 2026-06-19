---
series: computer-science-major-101
episode: 7
title: "Computer Science Major 101 (7/10): 프로젝트 과목"
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
  - Project
  - Capstone
  - Teamwork
  - Beginner
seo_description: 프로젝트 과목의 목적, 팀 구성, 기획, 산출물, 발표까지 전체 흐름을 정리한 글
code_required: false
last_reviewed: '2026-05-14'
---

# Computer Science Major 101 (7/10): 프로젝트 과목

전공 후반부에 들어가면 많은 학생이 비슷한 질문을 합니다. 이제까지 배운 것을 어디에 써 보아야 하는지, 과목별 지식을 어떻게 하나의 결과물로 묶어야 하는지 감이 잘 오지 않기 때문입니다.

이 글은 컴퓨터학과 전공 학습 가이드 101 시리즈의 7번째 글입니다.

![Computer Science Major 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/07/07-01-project-delivery-flow.ko.png)
*컴퓨터학과 전공 가이드 7장 흐름 개요*

> 프로젝트 과목들의 핵심은 완벽한 결과가 아니라, 제약 조건 속에서 의사결정을 기록하고 배움을 남기는 데 있습니다.

## 이 글에서 다룰 문제

- 왜 프로젝트 과목은 전공 후반부의 핵심으로 여겨질까요?
- 팀 프로젝트는 개인 과제와 무엇이 다르고 어떤 준비를 더 요구할까요?
- 문제 정의, 범위 조절, 일정 관리, 시연 준비는 왜 모두 중요할까요?
- 프로젝트에서 가장 자주 발생하는 실패 패턴은 무엇일까요?
- 학기 프로젝트를 포트폴리오 자산으로 바꾸는 핵심은 무엇일까요?

## 왜 프로젝트 과목이 중요한가

프로젝트 과목은 전공 지식을 한데 묶어 결과물로 바꾸는 단계입니다. 이전까지 배운 자료구조, 데이터베이스, 네트워크, 알고리즘이 하나의 동작하는 시스템으로 통합됩니다.

많은 학생의 첫 포트폴리오는 전공 프로젝트에서 나옵니다. 무엇을 만들었는지뿐 아니라 어떤 판단을 했고, 어떻게 협업했고, 어떤 결과를 남겼는지까지 보여 줄 수 있기 때문입니다.

프로젝트는 코드를 먼저 쓰는 활동이 아닙니다. 계획과 설계가 먼저 있고, 구현과 테스트가 뒤따르며, 마지막에는 결과를 보여 주는 시연이 이어집니다.

- **범위(scope)**: 이번 프로젝트에서 실제로 다룰 문제의 경계입니다. 범위를 정하는 것이 범위를 넓히는 것보다 어렵습니다.
- **MVP**: 가장 작은 기능 집합으로 만든 첫 제품입니다. 빠른 검증이 목적입니다.
- **데모(demo)**: 결과물을 직접 보여 주는 시연입니다. 작동하는 코드가 가장 강한 증거입니다.
- **이해관계자(stakeholder)**: 결과에 관심을 갖는 사람이나 집단입니다. 교수, 팀원, 미래 사용자 모두 포함됩니다.
- **회고(retrospective)**: 작업이 끝난 뒤 과정을 돌아보는 정리입니다.

## 왜 여기서 막히는가: 흔한 시나리오

**시나리오 1 — "기능은 많은데 아무것도 제대로 동작하지 않는다"**

건우 팀은 아이디어가 넘쳤습니다. SNS 기능, 지도 연동, AI 추천, 실시간 채팅을 모두 넣기로 했습니다. 4주차가 됐을 때 각자 다른 기능을 개발했는데 통합이 안 됐습니다. 데모 당일에 로그인조차 제대로 동작하지 않았습니다.

발생 신호: 각자의 기능은 로컬에서 동작하는데 통합하면 깨집니다. 마지막 주에 갑자기 모든 것을 합치려 합니다. 브랜치가 5개 이상이고 아무도 main 브랜치 상태를 모릅니다.

해결 방향: 2주차부터 핵심 기능 1개를 데모 가능한 상태로 유지해야 합니다. 새 기능 추가보다 통합 가능한 상태 유지가 우선입니다. "이것을 지금 추가하면 데모에 어떤 영향이 있는가"를 먼저 물어야 합니다.

**시나리오 2 — "누가 무엇을 할지 처음에 정하지 않았다"**

지아 팀은 친한 친구끼리 모였습니다. 역할 분담 없이 시작했고, 모두가 흥미로운 기능에만 집중했습니다. 테스트 코드를 작성하는 사람도, 배포 환경을 설정하는 사람도 없었습니다. 발표 전날 밤 10시에 서로 연락이 안 됐습니다.

발생 신호: 주간 회의가 없고, 누가 무엇을 했는지 서로 모릅니다. PR이 없거나 main 브랜치에 직접 푸시합니다. 이슈 트래커가 비어 있거나 아예 없습니다.

해결 방향: 1주차에 역할, 브랜치 전략, PR 기준, 주간 체크인 시간을 문서로 고정해야 합니다. "누가 결정하는가"도 명확히 해야 합니다. 팀장 역할이 없으면 아무도 결정하지 않는 상황이 생깁니다.

**시나리오 3 — "발표 자료를 마지막 날 밤에 만들었다"**

다연 팀은 구현에 집중하다가 발표 준비를 마지막 하루에 했습니다. 무엇을 어떻게 설명할지 팀 내에서 합의가 안 된 상태로 발표장에 갔습니다. 기능은 잘 동작했지만 "왜 이걸 만들었는지", "어떤 기술적 선택을 했는지" 설명이 매끄럽지 않았습니다.

발생 신호: 데모는 되는데 "왜 그렇게 했냐"는 질문에 답하기 어렵습니다. 발표 도중 팀원끼리 다른 답을 합니다.

해결 방향: 발표 자료는 주 2회 업데이트해야 합니다. 기능과 설명이 함께 자라야 합니다. "이 기능을 왜 선택했는가"를 이슈 또는 PR 설명에 남기는 습관이 발표 자료의 80%를 만들어 줍니다.

## 제출 가능한 프로젝트 브리프 만들기

팀 프로젝트가 흔들리는 가장 흔한 이유는 아이디어는 있는데 제출 가능한 계획 문서가 없기 때문입니다.

```python
from textwrap import dedent

spec = {
    "project": "Campus Schedule Checker",
    "users": ["students", "academic advisors"],
    "pain_point": "Students discover timetable conflicts too late during course registration.",
    "mvp_features": [
        "Upload timetable CSV",
        "Detect overlapping classes",
        "Show conflict summary by day",
    ],
    "out_of_scope": [
        "Mobile app",
        "Automatic enrollment",
        "Professor recommendation engine",
    ],
    "weeks": [
        (1, "problem validation and sample data collection"),
        (2, "CSV parser and conflict rules"),
        (3, "result screen and test fixtures"),
        (4, "demo script, bug fixes, and README polish"),
    ],
    "risks": [
        ("scope creep", "Freeze feature list after week 1 review"),
        ("messy input data", "Prepare three validated sample CSV files early"),
        ("team sync gaps", "Run a 15-minute checkpoint twice a week"),
    ],
    "decisions": [
        ("CSV format chosen over DB", "No need for persistence in MVP; reduces setup time"),
        ("CLI over web UI", "Team has stronger backend skills; web adds scope risk"),
    ],
}

def build_brief(spec):
    problem_statement = (
        f"{spec['project']} helps {', '.join(spec['users'])} "
        f"by solving this problem: {spec['pain_point']}"
    )
    feature_lines = "\n".join(f"- {f}" for f in spec["mvp_features"])
    scope_lines = "\n".join(f"- {item}" for item in spec["out_of_scope"])
    week_lines = "\n".join(f"- Week {w}: {g}" for w, g in spec["weeks"])
    risk_lines = "\n".join(f"- {r}: {m}" for r, m in spec["risks"])
    decision_lines = "\n".join(f"- {d}: {r}" for d, r in spec["decisions"])

    return dedent(f"""
        ## Project Brief
        Problem statement: {problem_statement}

        ### MVP features
        {feature_lines}

        ### Out of scope
        {scope_lines}

        ### Week-by-week schedule
        {week_lines}

        ### Risk register
        {risk_lines}

        ### Key decisions
        {decision_lines}
    """).strip()

print(build_brief(spec))
```

이 브리프에서 중요한 것:
- 문제 정의가 한 문장으로 고정되어야 팀의 판단 기준이 생깁니다.
- MVP와 out of scope를 동시에 적어야 범위 확장을 막을 수 있습니다.
- 위험(risk)과 대응 방법이 함께 있어야 마지막 주 데모 품질이 올라갑니다.
- 결정(decisions) 기록이 발표에서 "왜 이렇게 만들었냐"는 질문의 답이 됩니다.

## 이 과목이 실무에서 어떻게 쓰이는가

스타트업의 초기 MVP는 학생 프로젝트와 꽤 닮아 있습니다. 문제를 작게 자르고, 핵심 사용자에게 필요한 기능부터 만들고, 빠르게 보여 주고, 피드백을 받아 다시 다듬습니다.

프로젝트 과목에서 배우는 것이 실무와 직접 연결되는 지점:

| 프로젝트 경험 | 실무 연결 포인트 |
| --- | --- |
| 범위 정의와 MVP 설계 | 스프린트 계획, 프로덕트 백로그 관리 |
| 팀 역할 분담과 PR 리뷰 | 코드 리뷰 문화, 온보딩 기대치 설정 |
| 주간 데모와 피드백 루프 | 애자일 스프린트 리뷰, 고객 인터뷰 |
| 위험 대응 계획 | 운영 장애 대응 매뉴얼, 롤백 계획 |
| 회고와 의사결정 기록 | 포스트모텀, ADR(Architecture Decision Record) |

## 프로젝트 방법론 비교

| 방법론 | 강점 | 약점 | 수업 프로젝트 적용 팁 |
| --- | --- | --- | --- |
| Waterfall | 문서와 단계가 명확 | 변경 대응이 느림 | 요구사항이 고정된 과제에 적합 |
| Agile(Scrum) | 짧은 피드백 주기 | 회의 운영 역량 필요 | 1~2주 스프린트로 축소 운영 |
| Kanban | 가시성과 흐름 관리 용이 | WIP 관리 실패 시 병목 | 작은 팀에서 이슈 보드 중심 운영 |
| Hybrid | 상황 맞춤 유연성 | 기준 불명확 시 혼란 | 문서 최소 기준+주간 데모 결합 |

학기 프로젝트에서는 보통 Hybrid가 가장 현실적입니다. 초기 1주는 Waterfall식으로 문제 정의와 범위를 고정하고, 이후 구현 구간은 Agile식 반복으로 운영하는 방식이 실패 확률을 낮춥니다.

## 캡스톤 일정표 템플릿(12주)

| 주차 | 핵심 산출물 | 통과 기준 |
| --- | --- | --- |
| 1~2주 | 문제 정의서, 범위 고정 | 사용자 문제 문장 1개 합의 |
| 3~4주 | MVP 프로토타입 | 핵심 기능 1개 데모 가능 |
| 5~7주 | 기능 확장 + 테스트 | 결함 분류표와 회귀 테스트 존재 |
| 8~9주 | 성능/품질 개선 | 주요 지표 전후 비교표 존재 |
| 10~11주 | 발표 자료, 데모 스크립트 | 리허설 2회 완료 |
| 12주 | 최종 제출, 회고 | 의사결정 기록과 개선안 제출 |

이 일정표는 단순 관리 도구가 아니라 팀의 합의 문서입니다. 범위 고정 시점과 품질 게이트를 분리해 두면 기능 욕심으로 일정이 무너지는 문제를 줄일 수 있습니다.

## 팀 협업에서 가장 자주 깨지는 지점

첫째, **범위 확장**입니다. 아이디어가 좋은 팀일수록 기능이 계속 늘어나고 검증이 늦어집니다.

둘째, **역할 경계 불명확**입니다. 누가 의사결정을 하고 누가 구현 책임을 지는지 명시하지 않으면 일정이 미끄러집니다.

셋째, **통합 시점 지연**입니다. 개인 브랜치에서 오래 작업하다 마지막 주에 합치면 충돌 비용이 급증합니다.

이를 막기 위한 최소 규칙:

- 주 2회 15분 동기화: 진행, 막힘, 다음 액션만 공유
- PR 단위 작게 유지: 300줄 내외, 리뷰 목적 명확화
- 데모 우선 일정: 마지막 주가 아니라 2주차부터 시연 가능 상태 유지
- 회고 1페이지 고정: 기술 선택 근거, 실패 원인, 다음 개선안 기록

## PR 리뷰 최소 기준

코드 리뷰 경험은 실무 온보딩 비용을 줄여 주는 가장 직접적인 훈련입니다. 학기 프로젝트에서 PR 리뷰를 처음 도입하는 팀을 위한 최소 기준입니다.

**PR 작성자가 할 일**:
- 변경 목적을 한 문장으로 작성 (왜 이 코드가 필요한가)
- 테스트 방법 명시 (어떻게 확인했는가)
- 스크린샷 또는 실행 결과 첨부

**리뷰어가 확인할 것**:
- 변경 범위가 PR 목적과 일치하는가
- 엣지 케이스가 고려되었는가
- 변수/함수 이름이 의미를 전달하는가

**PR 병합 조건 (최소 기준)**:
- 승인 1명 이상
- CI 테스트 통과 (없으면 수동 검증 기록)
- 충돌 없이 main에 머지 가능

이 세 가지 조건만 지켜도 마지막 주 통합 충돌이 눈에 띄게 줄어듭니다.

## 결과물 평가 관점

좋은 프로젝트는 코드량보다 문제-해결-검증-학습이 연결됩니다. 발표 평가에서도 "무엇을 만들었다"보다 "왜 그 선택을 했고 어떻게 검증했는가"를 말할 수 있는 팀이 강합니다.

| 평가 항목 | 좋은 신호 | 약한 신호 |
| --- | --- | --- |
| 문제 정의 | 사용자/상황/제약이 명확 | "만들어 봄" 수준 설명 |
| 범위 관리 | MVP와 out of scope 명시 | 기능이 계속 추가됨 |
| 기술 선택 근거 | 대안 비교와 이유 존재 | 기술 이름만 나열 |
| 검증 증거 | 동작하는 데모, 테스트 | 스크린샷만 존재 |
| 협업 흔적 | PR, 리뷰, 이슈 기록 | 커밋만 존재 |
| 회고와 학습 | 실패 원인과 개선안 명시 | "잘 됐습니다" 수준 |

## 자주 하는 실수 5가지

1. **명세 없이 바로 코드를 쓰는 일입니다.** 문제 정의 없이 시작하면 무엇을 만드는지 팀이 서로 다르게 이해합니다.
2. **팀 역할이 모호한 일입니다.** 모두가 원하는 부분만 하면 테스트, 배포, 문서화가 빠집니다.
3. **주간 점검 회의가 없는 일입니다.** 막힌 지점을 일주일이 지나서야 공유하면 영향이 커집니다.
4. **Git 규칙을 정하지 않는 일입니다.** main에 직접 푸시하면 마지막 주에 충돌이 폭발합니다.
5. **데모로 끝내고 회고를 남기지 않는 일입니다.** 다음 프로젝트에서 같은 실수를 반복하게 됩니다.

## 운영 체크리스트

- [ ] 문제를 한 줄로 설명할 수 있습니다.
- [ ] 핵심 기능과 제외 범위를 함께 적었습니다.
- [ ] 주차별 산출물을 일정표에 넣었습니다.
- [ ] 위험 요소와 대응 방법을 짝지어 적었습니다.
- [ ] 2주차에 핵심 기능 1개를 데모 가능한 상태로 만들었습니다.
- [ ] PR 리뷰 최소 기준을 팀이 합의했습니다.
- [ ] 주간 체크인 시간을 고정했습니다.

## 처음 질문으로 돌아가기

- **왜 프로젝트 과목은 전공 후반부의 핵심으로 여겨질까요?**
  - 자료구조, 데이터베이스, 네트워크, 알고리즘이 따로따로 배운 지식이 아니라 하나의 동작하는 시스템으로 통합되는 시험대이기 때문입니다. 설명할 수 있는 결과물이 처음 만들어지는 단계입니다. 여기서 만든 결과물이 첫 포트폴리오가 됩니다.

- **팀 프로젝트는 개인 과제와 무엇이 다르고 어떤 준비를 더 요구할까요?**
  - 개인 과제는 내가 알면 되지만, 팀 프로젝트는 서로가 알아야 합니다. 역할 정의, 통합 계획, 의사결정 공유, 충돌 해결이 기술 구현만큼 중요합니다. 지아 시나리오처럼 기술은 있는데 협업 구조가 없으면 결과물이 나오지 않습니다.

- **문제 정의, 범위 조절, 일정 관리, 시연 준비는 왜 모두 중요할까요?**
  - 건우 시나리오처럼 범위가 없으면 마지막 주에 아무것도 동작하지 않습니다. 다연 시나리오처럼 시연 준비가 늦으면 기능이 있어도 설명을 못 합니다. 네 가지가 함께 있어야 발표 당일에 팀이 자신 있게 설 수 있습니다.

- **프로젝트에서 가장 자주 발생하는 실패 패턴은 무엇일까요?**
  - 범위 확장(scope creep)입니다. 아이디어는 많은데 무엇을 하지 않을지 합의하지 않으면 모든 것이 반쯤 만들어진 상태로 데모 날이 옵니다. out of scope 목록이 MVP 목록만큼 중요한 이유입니다.

- **학기 프로젝트를 포트폴리오 자산으로 바꾸는 핵심은 무엇일까요?**
  - 의사결정 3개, 실패와 수정 2개, 다음 개선안 1개를 기록하는 것입니다. 이 기록이 있으면 면접에서 "기술적으로 어떤 선택을 했나요"라는 질문에 구체적으로 답할 수 있습니다. 코드보다 판단 과정이 면접에서 더 오래 기억됩니다.

## 정리

프로젝트 과목은 전공 지식을 한데 묶어 결과물로 바꾸는 단계입니다. 문제 정의, 사용자 이해, 범위 조절, 협업, 테스트, 시연까지 모두 경험해야 비로소 작은 제품을 만든 감각이 남습니다. 브리프를 먼저 쓰고, 2주차부터 데모 가능 상태를 유지하고, PR 리뷰를 남기는 세 가지 습관이 프로젝트 과목에서 얻을 수 있는 가장 실용적인 자산입니다. 다음 글에서는 이런 과정을 꾸준히 버티게 해 주는 전공 공부 방법을 정리하겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Science Major 101 (1/10): 컴퓨터학과에서는 무엇을 배우는가](./01-what-cs-majors-learn.md)
- [Computer Science Major 101 (2/10): 1학년 과목 이해하기](./02-first-year-subjects.md)
- [Computer Science Major 101 (3/10): 자료구조와 알고리즘](./03-data-structures-and-algorithms.md)
- [Computer Science Major 101 (4/10): 시스템 과목 이해하기](./04-systems-subjects.md)
- [Computer Science Major 101 (5/10): 데이터베이스와 네트워크](./05-database-and-network.md)
- [Computer Science Major 101 (6/10): AI와 데이터사이언스](./06-ai-and-data-science.md)
- **Computer Science Major 101 (7/10): 프로젝트 과목 (현재 글)**
- [Computer Science Major 101 (8/10): 전공 공부 방법](./08-how-to-study-cs.md)
- [Computer Science Major 101 (9/10): 포트폴리오로 연결하기](./09-build-your-portfolio.md)
- [Computer Science Major 101 (10/10): 졸업 전 갖춰야 할 역량](./10-skills-before-graduation.md)

<!-- toc:end -->

## 참고 자료

- [ACM/IEEE-CS/AAAI Computer Science Curricula 2023](https://csed.acm.org/cs2023/)
- [ABET Criteria for Accrediting Computing Programs](https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-computing-programs-2025-2026/)
- [SWEBOK Guide](https://www.computer.org/education/bodies-of-knowledge/software-engineering)
- [GitHub Docs - About Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-major-101/ko)

Tags: CS, Project, Capstone, Teamwork, Beginner
