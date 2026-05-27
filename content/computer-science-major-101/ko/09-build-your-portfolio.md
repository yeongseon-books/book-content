---
series: computer-science-major-101
episode: 9
title: "Computer Science Major 101 (9/10): 포트폴리오로 연결하기"
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

# Computer Science Major 101 (9/10): 포트폴리오로 연결하기

학생 때 만든 과제와 프로젝트는 정리하지 않으면 생각보다 빨리 사라집니다. 로컬 폴더에만 남아 있고 설명도 없다면, 나중에는 만든 사람조차 다시 꺼내 보기 어려워집니다.

이 글은 컴퓨터학과 전공 학습 가이드 101 시리즈의 9번째 글입니다.

![Computer Science Major 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/09/09-01-portfolio-publishing-flow.ko.png)
*컴퓨터학과 전공 가이드 9장 흐름 개요*
> 포트폴리오의 핵심은 프로젝트 개수가 아니라, 각 프로젝트에서 자신의 의사결정과 배움이 선명하게 드러나는 데 있습니다.

## 먼저 던지는 질문

- 전공 과제와 프로젝트는 어떻게 포트폴리오가 될 수 있을까요?
- GitHub 저장소, README, 실행 방법, 데모 링크는 왜 모두 중요할까요?
- 코드만 올려 두는 것과 설명 가능한 결과물을 공개하는 것은 무엇이 다를까요?

## 이 글에서 배울 것

- 포트폴리오의 정의
- GitHub 활용
- README 작성
- 문서화 패턴
- 공개의 의미

## 왜 중요한가

지원 단계에서는 눈에 보이는 결과가 있어야 대화가 시작됩니다. 이력서 한 줄보다 저장소와 README, 데모 링크가 훨씬 더 많은 정보를 담고, 문제 해결 방식과 협업 태도까지 보여 줍니다.

## 한눈에 보는 개념

> 과제는 제출로 끝나지만, 포트폴리오는 설명 가능한 저장소와 문서가 붙을 때 시작됩니다.

과제가 자동으로 포트폴리오가 되지는 않습니다. 저장소로 정리하고, README로 맥락을 설명하고, 필요하면 데모를 붙여야 비로소 다른 사람이 읽을 수 있는 결과물이 됩니다.

## 핵심 용어

- **저장소(repo)**: 코드와 문서를 함께 보관하는 공간입니다.
- **README**: 저장소를 열었을 때 가장 먼저 읽는 소개 문서입니다.
- **라이선스(license)**: 사용 조건을 정하는 문서입니다.
- **커밋(commit)**: 변경 기록의 기본 단위입니다.
- **릴리스(release)**: 배포 가능한 특정 버전 묶음입니다.

## 바뀌는 지점

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

        ## 설정과 실행
        {run_lines}

        ## Tech Stack
        {stack}

        ## License
        {project['license_note']}

        ## 배운 점
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

## 설정과 실행
1. python -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. flask --app app run

## Tech Stack
Python, Flask, SQLite, Bootstrap

## License
MIT License

## 배운 점
- CSV 입력 검증이 UI보다 먼저 안정화되어야 한다는 점
- 시간표 충돌 규칙을 테스트 케이스로 먼저 고정하는 편이 디버깅이 빠르다는 점
```

여기서 중요한 것은 `https://example.com/demo` 같은 가짜 느낌의 URL을 넣지 않는다는 사실입니다. 실제 배포 링크가 없으면 **녹화 영상**, **로컬 GIF**, **스크린샷 묶음**처럼 검증 가능한 증거의 종류를 정확히 적는 편이 훨씬 신뢰를 줍니다.

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

## 배운 점
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

## 포트폴리오를 평가 관점으로 설계하기

포트폴리오는 저장소 모음이 아니라 평가 가능한 증거 모음입니다. 읽는 사람은 프로젝트 수보다 판단 근거를 먼저 봅니다. 어떤 문제를 선택했는지, 왜 그 기술을 골랐는지, 어떤 실패를 겪었고 무엇을 바꿨는지, 결과를 어떻게 검증했는지까지 연결되어야 합니다. 이 흐름이 없으면 코드가 좋아도 해석이 어렵습니다.

아래 표는 채용 관점에서 자주 확인하는 항목을 정리한 것입니다.

| 평가 항목 | 좋은 신호 | 약한 신호 | 개선 방법 |
| --- | --- | --- | --- |
| 문제 정의 | 사용자/상황/제약이 명확 | "만들어 봄" 수준 설명 | README 첫 문단에 문제 문장 고정 |
| 설계 근거 | 대안 비교와 선택 이유 존재 | 기술 이름만 나열 | ADR 또는 결정 메모 추가 |
| 구현 품질 | 테스트, 예외 처리, 구조화 | 단일 파일, 실행 불가 | 최소 실행 경로와 테스트 제공 |
| 검증 증거 | 데모 영상/로그/지표 | 스크린샷만 존재 | 재현 가능한 검증 절차 문서화 |
| 협업 흔적 | PR, 리뷰, 이슈 기록 | 커밋만 존재 | 협업 로그 섹션 추가 |

## 저장소 구성의 최소 표준

포트폴리오 초기에 가장 효과적인 개선은 구조 표준화입니다. 모든 저장소에 동일한 기본 뼈대를 두면 리뷰어가 빠르게 이해할 수 있습니다.

- `README.md`: 문제, 실행, 데모, 배운 점
- `docs/`: 설계 메모, 의사결정 기록, 회고
- `tests/`: 핵심 로직 검증
- `scripts/` 또는 `Makefile`: 재현 가능한 실행 커맨드
- `LICENSE`: 사용 조건 명시

특히 README의 "What I Learned" 섹션은 차별화 포인트입니다. 성공만 쓰기보다 실패와 수정 과정을 적어야 실전 감각이 드러납니다.

## 학부 프로젝트를 경력 스토리로 바꾸는 법

면접에서 강한 프로젝트는 규모가 큰 프로젝트가 아니라, 깊이가 보이는 프로젝트입니다. 예를 들어 "시간표 충돌 탐지 앱" 자체는 흔할 수 있지만, 데이터 검증 규칙을 어떻게 설계했는지, 잘못된 입력을 어떻게 다뤘는지, 성능 병목을 어떻게 측정했는지를 설명하면 충분히 강한 스토리가 됩니다.

따라서 프로젝트마다 아래 3가지는 반드시 남기는 것을 권장합니다.

1. 의사결정 3개: 무엇을, 왜, 어떤 대안 대신 선택했는가
2. 실패 2개: 어떤 문제가 있었고 어떻게 줄였는가
3. 다음 개선 1개: 시간이 더 있으면 무엇을 바꿀 것인가

이 기록이 누적되면 포트폴리오는 단순 제출물이 아니라 성장 로그가 됩니다.

## 포트폴리오 유지보수 루틴

포트폴리오는 한 번 만들고 끝나는 문서가 아닙니다. 분기마다 정리하지 않으면 링크가 깨지고 실행 방법이 오래되어 신뢰를 잃습니다. 최소 분기 1회 점검 루틴을 두는 것이 좋습니다. 데모 링크 확인, 실행 명령 업데이트, 의존성 버전 명시, README 요약 갱신, 학습 포인트 보강을 체크하면 품질이 안정됩니다.

또한 프로젝트별로 "한 줄 가치"를 고정해 두십시오. 예: "시간표 충돌을 1초 이내 탐지"처럼 사용자 가치를 명확히 적으면 읽는 사람이 프로젝트 의미를 즉시 파악할 수 있습니다. 기술 설명은 그 다음입니다.

## 실행 가능한 학습 운영 원칙

아래 원칙은 전공 주제가 달라도 공통으로 적용됩니다. 첫째, 매주 하나의 "관찰 가능한 결과"를 남겨야 합니다. 결과물은 코드, 표, 짧은 리포트, 테스트 로그 중 무엇이든 좋지만 타인이 재확인할 수 있어야 합니다. 둘째, 선택 이유를 한 문장으로 기록해야 합니다. 같은 결과가 나와도 선택 근거가 없으면 다음 학습에서 재사용하기 어렵습니다. 셋째, 실패를 유형화해야 합니다. 단순히 틀렸다고 적지 말고 개념 혼동, 조건 누락, 검증 부족, 범위 과대 같은 형태로 분류하면 개선 속도가 빨라집니다.

또한 전공 학습은 "입력-처리-출력-회고"의 폐루프로 운영하는 편이 안정적입니다. 입력은 강의와 자료 조사, 처리는 문제 풀이와 구현, 출력은 산출물, 회고는 개선 기록입니다. 많은 학생이 입력과 처리에만 시간을 쓰고 출력과 회고를 생략하는데, 이 경우 학습이 누적되지 않습니다. 반대로 작은 출력이라도 꾸준히 남기면 포트폴리오, 면접, 협업 문서까지 한 번에 연결됩니다.

실제 주간 운영 예시는 다음과 같습니다.

- 월~화: 개념 정리와 핵심 문제 2개 해결
- 수~목: 구현 또는 실험 1회, 측정 지표 기록
- 금: 결과 요약 10줄 작성, 다음 주 약점 1개 선택
- 주말: 약점 보강 60분 + 문서 업데이트

이 방식의 장점은 완벽주의를 줄이고 지속 가능성을 높인다는 사실입니다. 전공 학습에서 중요한 것은 단기간 최대치보다 장기간 반복 가능성입니다. 특히 학기 후반에는 과제와 시험이 겹치므로, 미리 정해 둔 최소 루틴이 없으면 우선순위가 흔들립니다.

마지막으로, 스스로에게 던질 검증 질문을 고정해 두면 품질이 올라갑니다. "이번 주 결과를 타인이 10분 안에 재현할 수 있는가", "내 선택 이유를 반대 관점에서 반박해도 버틸 수 있는가", "다음 주에 같은 문제를 더 짧게 풀 수 있는가" 같은 질문입니다. 이 질문에 답할 수 있다면 학습은 단순 반복을 넘어 실제 역량으로 축적되고 있다고 볼 수 있습니다.

## 연구실·취업 공통 포트폴리오 정리표

포트폴리오는 목적에 따라 강조점이 달라집니다. 취업형과 대학원형을 같은 저장소에서 분기해 관리하면 유지 비용을 줄일 수 있습니다.

| 목적 | 강조 요소 | 필수 증거 | 보강 문서 |
| --- | --- | --- | --- |
| 취업 지원 | 문제 해결, 협업, 배포 | 데모 영상, 테스트, PR 기록 | 장애 회고, 성능 개선 노트 |
| 대학원 지원 | 문제 정의, 실험, 재현성 | 실험 로그, 결과 표, 코드 | 논문 요약, 한계/향후 연구 |

또한 프로젝트마다 `한 줄 기여`, `핵심 의사결정 3개`, `실패와 수정 2개`를 고정 항목으로 남기면 면접과 연구실 인터뷰에서 설명 품질이 크게 올라갑니다.

## 정리

포트폴리오는 특별한 사람만 만드는 장식물이 아니라, 이미 만든 과제와 프로젝트를 읽을 수 있는 형태로 정리하는 작업입니다. 저장소 이름, README, 실행 방법, 데모, 문서화가 갖춰지면 작은 과제도 충분히 의미 있는 결과물이 됩니다. 다음 글에서는 시리즈를 마무리하며 졸업 전에 갖춰 두면 좋은 역량을 정리하겠습니다.

## 처음 질문으로 돌아가기

- **전공 과제와 프로젝트는 어떻게 포트폴리오가 될 수 있을까요?**
  - 프로젝트 개수보다 각 프로젝트에서 당신이 어떤 선택을 했는지, 그리고 무엇을 배웠는지가 채용 담당자의 눈을 끕니다.
- **GitHub 저장소, README, 실행 방법, 데모 링크는 왜 모두 중요할까요?**
  - 깔끔한 코드, 좋은 README, 배포된 데모는 기본이고, 그 프로젝트에서 어떤 기술 트레이드오프를 고민했는지, 왜 그것을 선택했는지를 설명할 수 있으면 더욱 강합니다.
- **코드만 올려 두는 것과 설명 가능한 결과물을 공개하는 것은 무엇이 다를까요?**
  - 현업 엔지니어는 지원자의 기술 깊이뿐 아니라 문제를 어떻게 나누고, 팀과 소통하고, 제약 속에서 의사결정하는지를 봅니다. 포트폴리오 프로젝트가 이런 면을 보여줄 수 있으면 이상적입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Science Major 101 (1/10): 컴퓨터학과에서는 무엇을 배우는가](./01-what-cs-majors-learn.md)
- [Computer Science Major 101 (2/10): 1학년 과목 이해하기](./02-first-year-subjects.md)
- [Computer Science Major 101 (3/10): 자료구조와 알고리즘](./03-data-structures-and-algorithms.md)
- [Computer Science Major 101 (4/10): 시스템 과목 이해하기](./04-systems-subjects.md)
- [Computer Science Major 101 (5/10): 데이터베이스와 네트워크](./05-database-and-network.md)
- [Computer Science Major 101 (6/10): AI와 데이터사이언스](./06-ai-and-data-science.md)
- [Computer Science Major 101 (7/10): 프로젝트 과목](./07-project-subjects.md)
- [Computer Science Major 101 (8/10): 전공 공부 방법](./08-how-to-study-cs.md)
- **포트폴리오로 연결하기 (현재 글)**
- 졸업 전 갖춰야 할 역량 (예정)

<!-- toc:end -->

## 참고 자료

- [GitHub Docs - About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Open Source Guides - Starting an Open Source Project](https://opensource.guide/starting-a-project/)
- [The Turing Way](https://book.the-turing-way.org/)
- [Good Enough Practices in Scientific Computing](https://doi.org/10.1371/journal.pcbi.1005510)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-major-101/ko)

Tags: CS, Portfolio, GitHub, Career, Beginner
