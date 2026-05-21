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

이 글은 Computer Science Major 101 시리즈의 7번째 글입니다.

전공 후반부에 들어가면 많은 학생이 비슷한 질문을 합니다. 이제까지 배운 것을 어디에 써 보아야 하는지, 과목별 지식을 어떻게 하나의 결과물로 묶어야 하는지 감이 잘 오지 않기 때문입니다.

![Computer Science Major 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/07/07-01-project-delivery-flow.ko.png)
*컴퓨터학과 전공 가이드 7장 흐름 개요*
> 프로젝트 과목들의 핵심은 완벽한 결과가 아니라, 제약 조건 속에서 의사결정을 기록하고 배움을 남기는 데 있습니다.

## 먼저 던지는 질문

- 왜 프로젝트 과목은 전공 후반부의 핵심으로 여겨질까요?
- 팀 프로젝트는 개인 과제와 무엇이 다르고 어떤 준비를 더 요구할까요?
- 문제 정의, 범위 조절, 일정 관리, 시연 준비는 왜 모두 중요할까요?

## 이 글에서 배울 것

- 프로젝트의 목적
- 팀 구성
- 기획과 범위 관리
- 산출물 정리
- 데모의 의미

## 왜 중요한가

많은 학생의 첫 포트폴리오는 전공 프로젝트에서 나옵니다. 무엇을 만들었는지뿐 아니라 어떤 판단을 했고, 어떻게 협업했고, 어떤 결과를 남겼는지까지 보여 줄 수 있기 때문입니다.

## 한눈에 보는 개념

> 프로젝트 과목은 지식을 묻는 수업이 아니라, 제한된 시간 안에 작은 제품을 완성하는 수업에 가깝습니다.

프로젝트는 코드를 먼저 쓰는 활동이 아닙니다. 계획과 설계가 먼저 있고, 구현과 테스트가 뒤따르며, 마지막에는 결과를 보여 주는 시연이 이어집니다. 이 순서를 머릿속에 두면 전공 프로젝트가 훨씬 덜 혼란스럽습니다.

## 핵심 용어

- **범위(scope)**: 이번 프로젝트에서 실제로 다룰 문제의 경계입니다.
- **MVP**: 가장 작은 기능 집합으로 만든 첫 제품입니다.
- **데모(demo)**: 결과물을 직접 보여 주는 시연입니다.
- **이해관계자(stakeholder)**: 결과에 관심을 갖는 사람이나 집단입니다.
- **회고(retrospective)**: 작업이 끝난 뒤 과정을 돌아보는 정리입니다.

## 바뀌는 지점

**Before**: 프로젝트를 단순한 과제로 봅니다.

**After**: 작은 제품을 만드는 과정으로 봅니다.

## 실습: 제출 가능한 프로젝트 브리프 만들기

팀 프로젝트가 흔들리는 가장 흔한 이유는 아이디어는 있는데 제출 가능한 계획 문서가 없기 때문입니다. 아래 예시는 짧은 명세를 받아 README나 기획 문서에 바로 붙일 수 있는 프로젝트 브리프를 만드는 스크립트입니다.

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
}

def build_brief(spec):
    problem_statement = (
        f"{spec['project']} helps {', '.join(spec['users'])} "
        f"by solving this problem: {spec['pain_point']}"
    )
    feature_lines = "\n".join(f"- {feature}" for feature in spec["mvp_features"])
    scope_lines = "\n".join(f"- {item}" for item in spec["out_of_scope"])
    week_lines = "\n".join(
        f"- Week {week}: {goal}" for week, goal in spec["weeks"]
    )
    risk_lines = "\n".join(
        f"- {risk}: {mitigation}" for risk, mitigation in spec["risks"]
    )

    return dedent(
        f"""
        ## Project Brief
        Problem statement: {problem_statement}

        ### MVP features
        {feature_lines}

        ### 범위 밖 주제
        {scope_lines}

        ### Week-by-week schedule
        {week_lines}

        ### Risk register
        {risk_lines}
        """
    ).strip()

print(build_brief(spec))
```

예시 입력을 그대로 실행하면 아래와 같은 출력이 나옵니다.

```text
## Project Brief
Problem statement: Campus Schedule Checker helps students, academic advisors by solving this problem: Students discover timetable conflicts too late during course registration.

### MVP features
- Upload timetable CSV
- Detect overlapping classes
- Show conflict summary by day

### 범위 밖 주제
- Mobile app
- Automatic enrollment
- Professor recommendation engine

### Week-by-week schedule
- Week 1: problem validation and sample data collection
- Week 2: CSV parser and conflict rules
- Week 3: result screen and test fixtures
- Week 4: demo script, bug fixes, and README polish

### Risk register
- scope creep: Freeze feature list after week 1 review
- messy input data: Prepare three validated sample CSV files early
- team sync gaps: Run a 15-minute checkpoint twice a week
```

이 출력은 단순한 아이디어 메모가 아니라, 팀 회의록과 README 초안의 출발점이 됩니다. 특히 **out of scope**와 **risk register**가 함께 있어야 무엇을 하지 않을지, 어디서 흔들릴지를 미리 합의할 수 있습니다.

## 이 코드에서 먼저 볼 점

- 문제 정의가 한 문장으로 고정되어야 팀의 판단 기준이 생깁니다.
- MVP와 out of scope를 동시에 적어야 범위 확장을 막을 수 있습니다.
- 일정과 위험 대응이 함께 있어야 마지막 주 데모 품질이 올라갑니다.

## 자주 하는 실수 5가지

1. **명세 없이 바로 코드를 쓰는 일입니다.**
2. **팀 역할이 모호한 일입니다.**
3. **주간 점검 회의가 없는 일입니다.**
4. **Git 규칙을 정하지 않는 일입니다.**
5. **데모로 끝내고 회고를 남기지 않는 일입니다.**

## 실무에서는 이렇게 드러납니다

스타트업의 초기 MVP는 학생 프로젝트와 꽤 닮아 있습니다. 문제를 작게 자르고, 핵심 사용자에게 필요한 기능부터 만들고, 빠르게 보여 주고, 피드백을 받아 다시 다듬습니다. 그래서 프로젝트 과목 경험은 단순한 학교 과제가 아니라 작은 제품 개발 경험으로 읽힐 수 있습니다.

## 선배 엔지니어는 이렇게 봅니다

- 처음부터 크게 만들지 않습니다.
- 자주 보여 주고 빨리 피드백을 받습니다.
- 문서는 구현 속도를 늦추지 않고 합치는 비용을 줄입니다.
- 회고를 남겨야 다음 프로젝트가 좋아집니다.
- 데모는 결과를 설명하는 가장 강한 순간입니다.

## 체크리스트

- [ ] 문제를 한 줄로 설명할 수 있습니다.
- [ ] 핵심 기능과 제외 범위를 함께 적었습니다.
- [ ] 주차별 산출물을 일정표에 넣었습니다.
- [ ] 위험 요소와 대응 방법을 짝지어 적었습니다.

## 연습 문제

1. MVP를 한 줄로 설명해 보세요.
2. 데모의 의미를 한 줄로 적어 보세요.
3. 회고가 무엇을 남기는지 한 줄로 써 보세요.

## 정리

프로젝트 과목은 전공 지식을 한데 묶어 결과물로 바꾸는 단계입니다. 문제 정의, 사용자 이해, 범위 조절, 협업, 테스트, 시연까지 모두 경험해야 비로소 작은 제품을 만든 감각이 남습니다. 다음 글에서는 이런 과정을 꾸준히 버티게 해 주는 전공 공부 방법을 정리하겠습니다.

## 프로젝트 방법론 비교와 적용 기준

프로젝트 과목에서 가장 먼저 합의해야 하는 것은 개발 방법론 자체가 아니라 팀의 제약 조건입니다. 학기 프로젝트는 기간이 짧고 인력도 제한적이므로, 방법론의 순수성을 지키기보다 위험을 줄이는 선택이 중요합니다. 아래 표는 수업 환경에서 자주 비교하는 방식입니다.

| 방법론 | 강점 | 약점 | 수업 프로젝트 적용 팁 |
| --- | --- | --- | --- |
| Waterfall | 문서와 단계가 명확 | 변경 대응이 느림 | 요구사항이 고정된 과제에 적합 |
| Agile(Scrum) | 짧은 피드백 주기 | 회의 운영 역량 필요 | 1~2주 스프린트로 축소 운영 |
| Kanban | 가시성과 흐름 관리 용이 | WIP 관리 실패 시 병목 | 작은 팀에서 이슈 보드 중심 운영 |
| Hybrid | 상황 맞춤 유연성 | 기준 불명확 시 혼란 | 문서 최소 기준+주간 데모 결합 |

학기 프로젝트에서는 보통 Hybrid가 가장 현실적입니다. 초기 1주는 Waterfall식으로 문제 정의와 범위를 고정하고, 이후 구현 구간은 Agile식 반복으로 운영하는 방식이 실패 확률을 낮춥니다.

## 팀 협업에서 가장 자주 깨지는 지점

첫째, 범위 확장입니다. 아이디어가 좋은 팀일수록 기능이 계속 늘어나고 검증이 늦어집니다. 둘째, 역할 경계 불명확입니다. 누가 의사결정을 하고 누가 구현 책임을 지는지 명시하지 않으면 일정이 미끄러집니다. 셋째, 통합 시점 지연입니다. 개인 브랜치에서 오래 작업하다 마지막 주에 합치면 충돌 비용이 급증합니다.

이를 막기 위한 최소 규칙은 다음과 같습니다.

- 주 2회 15분 동기화: 진행, 막힘, 다음 액션만 공유
- PR 단위 작게 유지: 300줄 내외, 리뷰 목적 명확화
- 데모 우선 일정: 마지막 주가 아니라 2주차부터 시연 가능 상태 유지
- 회고 1페이지 고정: 기술 선택 근거, 실패 원인, 다음 개선안 기록

## 결과물 평가 관점

좋은 프로젝트는 코드량보다 문제-해결-검증-학습이 연결됩니다. 발표 평가에서도 "무엇을 만들었다"보다 "왜 그 선택을 했고 어떻게 검증했는가"를 말할 수 있는 팀이 강합니다. 이 기준을 초반부터 알고 진행하면 프로젝트가 과제로 끝나지 않고 포트폴리오 자산으로 남습니다.

## 학기 프로젝트를 실패하지 않게 만드는 운영 규칙

학기 프로젝트의 실패는 기술 난이도보다 운영 실패에서 시작되는 경우가 많습니다. 따라서 팀 초반에 개발 규칙을 문서로 고정해야 합니다. 브랜치 전략, PR 리뷰 기준, 이슈 템플릿, 데모 일정, 결함 우선순위 규칙을 먼저 합의하면 마지막 주 혼란을 크게 줄일 수 있습니다.

발표 준비도 개발 마지막에 붙이는 일이 아닙니다. 2주차부터 데모 스크립트를 함께 업데이트해야 합니다. 그래야 기능 추가와 설명 구조가 같이 성숙합니다. 최종 발표에서 신뢰를 주는 팀은 구현량이 많은 팀보다, 문제 정의와 검증 결과를 일관되게 보여 주는 팀입니다.

## 실행 가능한 학습 운영 원칙

아래 원칙은 전공 주제가 달라도 공통으로 적용됩니다. 첫째, 매주 하나의 "관찰 가능한 결과"를 남겨야 합니다. 결과물은 코드, 표, 짧은 리포트, 테스트 로그 중 무엇이든 좋지만 타인이 재확인할 수 있어야 합니다. 둘째, 선택 이유를 한 문장으로 기록해야 합니다. 같은 결과가 나와도 선택 근거가 없으면 다음 학습에서 재사용하기 어렵습니다. 셋째, 실패를 유형화해야 합니다. 단순히 틀렸다고 적지 말고 개념 혼동, 조건 누락, 검증 부족, 범위 과대 같은 형태로 분류하면 개선 속도가 빨라집니다.

또한 전공 학습은 "입력-처리-출력-회고"의 폐루프로 운영하는 편이 안정적입니다. 입력은 강의와 자료 조사, 처리는 문제 풀이와 구현, 출력은 산출물, 회고는 개선 기록입니다. 많은 학생이 입력과 처리에만 시간을 쓰고 출력과 회고를 생략하는데, 이 경우 학습이 누적되지 않습니다. 반대로 작은 출력이라도 꾸준히 남기면 포트폴리오, 면접, 협업 문서까지 한 번에 연결됩니다.

실제 주간 운영 예시는 다음과 같습니다.

- 월~화: 개념 정리와 핵심 문제 2개 해결
- 수~목: 구현 또는 실험 1회, 측정 지표 기록
- 금: 결과 요약 10줄 작성, 다음 주 약점 1개 선택
- 주말: 약점 보강 60분 + 문서 업데이트

이 방식의 장점은 완벽주의를 줄이고 지속 가능성을 높인다는 점입니다. 전공 학습에서 중요한 것은 단기간 최대치보다 장기간 반복 가능성입니다. 특히 학기 후반에는 과제와 시험이 겹치므로, 미리 정해 둔 최소 루틴이 없으면 우선순위가 흔들립니다.

마지막으로, 스스로에게 던질 검증 질문을 고정해 두면 품질이 올라갑니다. "이번 주 결과를 타인이 10분 안에 재현할 수 있는가", "내 선택 이유를 반대 관점에서 반박해도 버틸 수 있는가", "다음 주에 같은 문제를 더 짧게 풀 수 있는가" 같은 질문입니다. 이 질문에 답할 수 있다면 학습은 단순 반복을 넘어 실제 역량으로 축적되고 있다고 볼 수 있습니다.

## 캡스톤 일정표 템플릿(12주)

캡스톤은 기술 선택보다 일정 설계에서 성패가 갈립니다. 아래처럼 주차별 게이트를 고정하면 마지막 주 품질 저하를 줄일 수 있습니다.

| 주차 | 핵심 산출물 | 통과 기준 |
| --- | --- | --- |
| 1~2주 | 문제 정의서, 범위 고정 | 사용자 문제 문장 1개 합의 |
| 3~4주 | MVP 프로토타입 | 핵심 기능 1개 데모 가능 |
| 5~7주 | 기능 확장 + 테스트 | 결함 분류표와 회귀 테스트 존재 |
| 8~9주 | 성능/품질 개선 | 주요 지표 전후 비교표 존재 |
| 10~11주 | 발표 자료, 데모 스크립트 | 리허설 2회 완료 |
| 12주 | 최종 제출, 회고 | 의사결정 기록과 개선안 제출 |

이 일정표는 단순 관리 도구가 아니라 팀의 합의 문서입니다. 특히 범위 고정 시점과 품질 게이트를 분리해 두면 기능 욕심으로 일정이 무너지는 문제를 줄일 수 있습니다.

## 처음 질문으로 돌아가기

- **왜 프로젝트 과목은 전공 후반부의 핵심으로 여겨질까요?**
  - 팀 프로젝트는 개인 과제와 다릅니다. 코드 분할, 진행 상황 동기화, 충돌 해결 같은 협력 기술과 문제 정의부터 배포까지 전체 사이클을 경험하는 것이 목표입니다.
- **팀 프로젝트는 개인 과제와 무엇이 다르고 어떤 준비를 더 요구할까요?**
  - 캡스톤 프로젝트에서 배운 시스템 설계, 트레이드오프 분석, 제약 조건 속의 의사결정은 현업에서 바로 요구되는 능력입니다.
- **문제 정의, 범위 조절, 일정 관리, 시연 준비는 왜 모두 중요할까요?**
  - 완벽한 결과보다 '왜 이렇게 했는가'를 명확하게 기록하고 설명하는 프로젝트가 포트폴리오 가치를 높입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Science Major 101 (1/10): 컴퓨터학과에서는 무엇을 배우는가](./01-what-cs-majors-learn.md)
- [Computer Science Major 101 (2/10): 1학년 과목 이해하기](./02-first-year-subjects.md)
- [Computer Science Major 101 (3/10): 자료구조와 알고리즘](./03-data-structures-and-algorithms.md)
- [Computer Science Major 101 (4/10): 시스템 과목 이해하기](./04-systems-subjects.md)
- [Computer Science Major 101 (5/10): 데이터베이스와 네트워크](./05-database-and-network.md)
- [Computer Science Major 101 (6/10): AI와 데이터사이언스](./06-ai-and-data-science.md)
- **프로젝트 과목 (현재 글)**
- 전공 공부 방법 (예정)
- 포트폴리오로 연결하기 (예정)
- 졸업 전 갖춰야 할 역량 (예정)

<!-- toc:end -->

## 참고 자료

- [ACM/IEEE-CS/AAAI Computer Science Curricula 2023](https://csed.acm.org/cs2023/)
- [ABET Criteria for Accrediting Computing Programs](https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-computing-programs-2025-2026/)
- [SWEBOK Guide](https://www.computer.org/education/bodies-of-knowledge/software-engineering)
- [GitHub Docs - About Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-major-101/ko)

Tags: CS, Project, Capstone, Teamwork, Beginner
