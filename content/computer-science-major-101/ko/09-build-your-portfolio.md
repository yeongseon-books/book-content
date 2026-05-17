---
series: computer-science-major-101
episode: 9
title: 포트폴리오로 연결하기
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
  - Portfolio
  - GitHub
  - Career
  - Beginner
seo_description: 전공 과제와 프로젝트를 GitHub 포트폴리오로 연결하는 방법, 문서화, README 정리법을 다룬 글
code_required: false
last_reviewed: '2026-05-14'
---

# 포트폴리오로 연결하기

학생 때 만든 과제와 프로젝트는 정리하지 않으면 생각보다 빨리 사라집니다. 로컬 폴더에만 남아 있고 설명도 없다면, 나중에는 만든 사람조차 다시 꺼내 보기 어려워집니다.

이 글은 Computer Science Major 101 시리즈의 9번째 글입니다.

## 이 글에서 다룰 문제

- 전공 과제와 프로젝트는 어떻게 포트폴리오가 될 수 있을까요?
- GitHub 저장소, README, 실행 방법, 데모 링크는 왜 모두 중요할까요?
- 코드만 올려 두는 것과 설명 가능한 결과물을 공개하는 것은 무엇이 다를까요?
- 포트폴리오가 지원 과정에서 대화를 여는 역할을 하는 이유는 무엇일까요?

## 이 글에서 배울 것

- 포트폴리오의 정의
- GitHub 활용
- README 작성
- 문서화 패턴
- 공개의 의미

## 왜 중요한가

지원 단계에서는 눈에 보이는 결과가 있어야 대화가 시작됩니다. 이력서 한 줄보다 저장소와 README, 데모 링크가 훨씬 더 많은 정보를 담고, 문제 해결 방식과 협업 태도까지 보여 줍니다.

## 한눈에 보는 개념

![과제에서 포트폴리오로 가는 흐름](../../../assets/computer-science-major-101/09/09-01-portfolio-publishing-flow.ko.png)

*과제가 저장소와 README를 거쳐 포트폴리오로 바뀌는 흐름*

> 과제는 제출로 끝나지만, 포트폴리오는 설명 가능한 저장소와 문서가 붙을 때 시작됩니다.

과제가 자동으로 포트폴리오가 되지는 않습니다. 저장소로 정리하고, README로 맥락을 설명하고, 필요하면 데모를 붙여야 비로소 다른 사람이 읽을 수 있는 결과물이 됩니다.

## 핵심 용어

- **저장소(repo)**: 코드와 문서를 함께 보관하는 공간입니다.
- **README**: 저장소를 열었을 때 가장 먼저 읽는 소개 문서입니다.
- **라이선스(license)**: 사용 조건을 정하는 문서입니다.
- **커밋(commit)**: 변경 기록의 기본 단위입니다.
- **릴리스(release)**: 배포 가능한 특정 버전 묶음입니다.

## Before/After

**Before**: 과제 폴더가 로컬 컴퓨터 안에만 있습니다.

**After**: 공개 저장소와 README, 데모로 정리된 결과물이 남습니다.

## 실습: README 초안 생성기

포트폴리오가 약해 보이는 가장 큰 이유는 코드가 없어서가 아니라, 읽는 사람이 무엇을 어떻게 검증해야 하는지 알 수 없어서입니다. 아래 예시는 저장소 정보를 받아 바로 공개 가능한 README 초안을 만드는 간단한 생성기입니다.

```python
from textwrap import dedent

project = {
    "name": "schedule-checker",
    "summary": "대학생 시간표 충돌을 찾아 주는 Flask 기반 웹 도구입니다.",
    "demo_evidence": [
        "Demo video (recorded walkthrough): docs/demo-walkthrough.mp4",
        "Local demo GIF: docs/demo.gif",
    ],
    "run_steps": [
        "python -m venv .venv",
        "source .venv/bin/activate",
        "pip install -r requirements.txt",
        "flask --app app run",
    ],
    "tech_stack": ["Python", "Flask", "SQLite", "Bootstrap"],
    "license_note": "MIT License",
    "learned": [
        "CSV 입력 검증이 UI보다 먼저 안정화되어야 한다는 점",
        "시간표 충돌 규칙을 테스트 케이스로 먼저 고정하는 편이 디버깅이 빠르다는 점",
    ],
}


def build_readme(project):
    demo_lines = "\n".join(f"- {item}" for item in project["demo_evidence"])
    run_lines = "\n".join(f"1. {step}" for step in project["run_steps"])
    stack = ", ".join(project["tech_stack"])
    learned_lines = "\n".join(f"- {item}" for item in project["learned"])

    return dedent(
        f"""
        # {project['name']}

        ## Project Summary
        {project['summary']}

        ## Demo Evidence
        {demo_lines}

        ## Setup and Run
        {run_lines}

        ## Tech Stack
        {stack}

        ## License
        {project['license_note']}

        ## What I Learned
        {learned_lines}
        """
    ).strip()


print(build_readme(project))
```

예시 입력으로 생성되는 출력은 다음과 같습니다.

```markdown
# schedule-checker

## Project Summary
대학생 시간표 충돌을 찾아 주는 Flask 기반 웹 도구입니다.

## Demo Evidence
- Demo video (recorded walkthrough): docs/demo-walkthrough.mp4
- Local demo GIF: docs/demo.gif

## Setup and Run
1. python -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. flask --app app run

## Tech Stack
Python, Flask, SQLite, Bootstrap

## License
MIT License

## What I Learned
- CSV 입력 검증이 UI보다 먼저 안정화되어야 한다는 점
- 시간표 충돌 규칙을 테스트 케이스로 먼저 고정하는 편이 디버깅이 빠르다는 점
```

여기서 중요한 것은 `https://example.com/demo` 같은 가짜 느낌의 URL을 넣지 않는다는 점입니다. 실제 배포 링크가 없으면 **녹화 영상**, **로컬 GIF**, **스크린샷 묶음**처럼 검증 가능한 증거의 종류를 정확히 적는 편이 훨씬 신뢰를 줍니다.

## 이 코드에서 먼저 볼 점

- README는 소개 문서이면서 재현 문서입니다.
- 데모 섹션은 링크의 개수보다 증거의 형태가 분명한지가 중요합니다.
- What I Learned 같은 회고 섹션이 있어야 단순 결과물에서 학습 기록으로 넘어갑니다.

## 자주 하는 실수 5가지

1. **README를 비워 두는 일입니다.**
2. **커밋 메시지를 모두 update처럼 모호하게 남기는 일입니다.**
3. **라이선스를 빼먹는 일입니다.**
4. **스크린샷이나 데모 없이 설명만 남기는 일입니다.**
5. **실행 방법을 적지 않아 재현이 어려운 상태로 두는 일입니다.**

## 실무에서는 이렇게 드러납니다

면접관과 리뷰어는 종종 코드를 열기 전에 README부터 읽습니다. 프로젝트를 어떻게 소개하는지, 실행 방법을 얼마나 분명하게 적는지, 문서를 어느 정도 신경 쓰는지에서 협업 감각을 빠르게 읽을 수 있기 때문입니다.

## README 초안 예시

포트폴리오 초반에는 README를 너무 길게 쓰려다가 오히려 핵심이 흐려지는 경우가 많습니다. 처음에는 검증 가능한 증거와 실행 절차가 보이도록 아래처럼 짧지만 완결된 초안을 만드는 편이 더 실용적입니다.

```markdown
# Schedule Checker

대학생 시간표 충돌을 찾아 주는 웹 도구입니다.

## Demo Evidence
- Demo video (recorded walkthrough): docs/demo-walkthrough.mp4
- Local demo GIF: docs/demo.gif

## Run
1. pip install -r requirements.txt
2. flask --app app run

## What I Learned
- 충돌 탐지 규칙을 테스트로 먼저 고정했습니다.
```

이 정도만 있어도 읽는 사람은 네 가지를 바로 파악할 수 있습니다. 무엇을 만드는 프로젝트인지, 어떤 형태의 데모 증거가 있는지, 로컬에서 어떻게 실행하는지, 그리고 무엇을 배웠는지입니다. 포트폴리오의 첫 관문은 화려함보다 재현 가능성입니다.

## 선배 엔지니어는 이렇게 봅니다

- 공개하는 과정 자체가 학습입니다.
- 코드만큼 문서도 중요합니다.
- 작은 개선 기록도 좋은 증거가 됩니다.
- 라이선스는 기본입니다.
- 데모 링크는 가장 설득력이 강합니다.

## 체크리스트

- [ ] README에 핵심 섹션 다섯 개를 넣었습니다.
- [ ] 라이선스를 추가했습니다.
- [ ] 스크린샷이나 데모를 준비했습니다.
- [ ] 실행 명령을 바로 보이게 적었습니다.

## 연습 문제

1. README를 한 줄로 설명해 보세요.
2. 라이선스의 의미를 한 줄로 적어 보세요.
3. 데모가 왜 강한 증거인지 한 줄로 써 보세요.

## 정리

포트폴리오는 특별한 사람만 만드는 장식물이 아니라, 이미 만든 과제와 프로젝트를 읽을 수 있는 형태로 정리하는 작업입니다. 저장소 이름, README, 실행 방법, 데모, 문서화가 갖춰지면 작은 과제도 충분히 의미 있는 결과물이 됩니다. 다음 글에서는 시리즈를 마무리하며 졸업 전에 갖춰 두면 좋은 역량을 정리하겠습니다.

<!-- toc:begin -->
- [컴퓨터학과에서는 무엇을 배우는가](./01-what-cs-majors-learn.md)
- [1학년 과목 이해하기](./02-first-year-subjects.md)
- [자료구조와 알고리즘](./03-data-structures-and-algorithms.md)
- [시스템 과목 이해하기](./04-systems-subjects.md)
- [데이터베이스와 네트워크](./05-database-and-network.md)
- [AI와 데이터사이언스](./06-ai-and-data-science.md)
- [프로젝트 과목](./07-project-subjects.md)
- [전공 공부 방법](./08-how-to-study-cs.md)
- **포트폴리오로 연결하기 (현재 글)**
- 졸업 전 갖춰야 할 역량 (예정)
<!-- toc:end -->

## 참고 자료

- [GitHub Docs - About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Open Source Guides - Starting an Open Source Project](https://opensource.guide/starting-a-project/)
- [The Turing Way](https://book.the-turing-way.org/)
- [Good Enough Practices in Scientific Computing](https://doi.org/10.1371/journal.pcbi.1005510)

Tags: CS, Portfolio, GitHub, Career, Beginner
