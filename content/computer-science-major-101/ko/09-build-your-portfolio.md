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

## 이 글에서 다룰 문제

- 전공 과제와 프로젝트는 어떻게 포트폴리오가 될 수 있을까요?
- GitHub 저장소, README, 실행 방법, 데모 링크는 왜 모두 중요할까요?
- 코드만 올려 두는 것과 설명 가능한 결과물을 공개하는 것은 무엇이 다를까요?
- 면접관이 포트폴리오를 볼 때 실제로 무엇을 먼저 확인할까요?
- 포트폴리오를 지속적으로 개선하는 최소 루틴은 무엇일까요?

## 왜 포트폴리오가 필요한가

지원 단계에서는 눈에 보이는 결과가 있어야 대화가 시작됩니다. 이력서 한 줄보다 저장소와 README, 데모 링크가 훨씬 더 많은 정보를 담고, 문제 해결 방식과 협업 태도까지 보여 줍니다.

과제가 자동으로 포트폴리오가 되지는 않습니다. 저장소로 정리하고, README로 맥락을 설명하고, 필요하면 데모를 붙여야 비로소 다른 사람이 읽을 수 있는 결과물이 됩니다.

- **저장소(repo)**: 코드와 문서를 함께 보관하는 공간입니다.
- **README**: 저장소를 열었을 때 가장 먼저 읽는 소개 문서입니다.
- **라이선스(license)**: 사용 조건을 정하는 문서입니다.
- **커밋(commit)**: 변경 기록의 기본 단위입니다. 메시지가 의사결정 로그가 됩니다.
- **릴리스(release)**: 배포 가능한 특정 버전 묶음입니다.

> 과제는 제출로 끝나지만, 포트폴리오는 설명 가능한 저장소와 문서가 붙을 때 시작됩니다.

## 왜 여기서 막히는가: 흔한 시나리오

**시나리오 1 — "GitHub에 코드만 올려 뒀는데 면접관이 아무 반응이 없다"**

재민은 학기 동안 만든 프로젝트를 GitHub에 올렸습니다. 코드는 있지만 README가 없거나 "프로젝트입니다"라는 한 줄만 있었습니다. 면접관이 "이 프로젝트에서 어떤 기술적 선택을 했나요"라고 물었을 때 설명하기 어려웠습니다. 코드가 있어도 맥락이 없으면 읽는 사람이 이해하기 어렵습니다.

발생 신호: GitHub URL을 공유했는데 면접관이 "좀 더 설명해 주세요"라고 합니다. 저장소에는 코드가 있는데 "왜 이걸 만들었는지"를 바로 설명하지 못합니다.

해결 방향: README에 "무엇을 왜 만들었고, 어떻게 실행하며, 무엇을 배웠는지"를 명확히 적어야 합니다. 5분 안에 읽고 실행할 수 있는 README가 목표입니다.

**시나리오 2 — "프로젝트가 많은데 설명할 게 없다"**

수진은 사이드 프로젝트를 10개 만들었습니다. 그런데 면접에서 각 프로젝트에 대해 "왜 그 기술을 선택했냐", "어떤 문제가 있었냐", "어떻게 해결했냐"라는 질문에 막혔습니다. 만들었지만 의사결정 기록을 남기지 않아서 설명이 어려웠습니다.

발생 신호: 프로젝트 수는 많지만 깊이 있는 프로젝트 설명이 어렵습니다. 면접에서 "가장 기억에 남는 기술적 도전은 무엇이었나요"라는 질문에 막힙니다.

해결 방향: 적게 만들어도 의사결정 3개, 실패 2개, 다음 개선 1개를 기록하는 편이 훨씬 강합니다. 10개의 얕은 프로젝트보다 3개의 깊은 프로젝트가 면접에서 더 강합니다.

**시나리오 3 — "데모가 없어서 실제로 동작하는지 알 수 없다"**

유진의 README에는 기능 설명이 자세히 있었지만 실행 방법이 없었습니다. 면접관이 로컬에서 실행해 보려고 했는데 환경 설정이 복잡해서 포기했습니다. 스크린샷도 없었습니다.

발생 신호: README를 읽어도 이 프로젝트가 실제로 동작하는지 알 수 없습니다. 실행 명령이 없거나 필요한 환경 변수가 설명되지 않았습니다.

해결 방향: 최소한 GIF 하나, 스크린샷 3장, 또는 단계별 실행 명령이 있어야 합니다. Makefile이나 docker-compose.yml이 있으면 재현 비용이 크게 줄어듭니다.

## README 초안 생성기

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
    "decisions": [
        "SQLite 선택: 배포 없이 로컬 실행 가능, 사용자 데이터 영속성 불필요",
        "Flask 선택: 기능 단순, Django 과도한 추상화 불필요",
    ],
}

def build_readme(project):
    demo_lines = "\n".join(f"- {item}" for item in project["demo_evidence"])
    run_lines = "\n".join(f"{i+1}. {step}" for i, step in enumerate(project["run_steps"]))
    stack = ", ".join(project["tech_stack"])
    learned_lines = "\n".join(f"- {item}" for item in project["learned"])
    decision_lines = "\n".join(f"- {item}" for item in project["decisions"])

    return dedent(f"""
        # {project['name']}

        ## Project Summary
        {project['summary']}

        ## Demo Evidence
        {demo_lines}

        ## 설정과 실행
        {run_lines}

        ## Tech Stack
        {stack}

        ## 기술 선택 근거
        {decision_lines}

        ## 배운 점
        {learned_lines}

        ## License
        {project['license_note']}
    """).strip()

print(build_readme(project))
```

여기서 중요한 것: 실제 배포 링크가 없으면 "녹화 영상", "로컬 GIF", "스크린샷 묶음"처럼 검증 가능한 증거의 종류를 정확히 적는 편이 훨씬 신뢰를 줍니다. 없는 데모 링크를 "준비 중"으로 두는 것보다 있는 증거를 정확히 나열하는 게 낫습니다.

## 이 과목이 실무에서 어떻게 쓰이는가

면접관과 리뷰어는 코드를 열기 전에 README부터 읽습니다. 프로젝트를 어떻게 소개하는지, 실행 방법을 얼마나 분명하게 적는지, 문서를 어느 정도 신경 쓰는지에서 협업 감각을 빠르게 읽을 수 있기 때문입니다.

| 평가 항목 | 좋은 신호 | 약한 신호 | 개선 방법 |
| --- | --- | --- | --- |
| 문제 정의 | 사용자/상황/제약이 명확 | "만들어 봄" 수준 설명 | README 첫 문단에 문제 문장 고정 |
| 설계 근거 | 대안 비교와 선택 이유 존재 | 기술 이름만 나열 | ADR 또는 결정 메모 추가 |
| 구현 품질 | 테스트, 예외 처리, 구조화 | 단일 파일, 실행 불가 | 최소 실행 경로와 테스트 제공 |
| 검증 증거 | 데모 영상/로그/지표 | 스크린샷만 존재 | 재현 가능한 검증 절차 문서화 |
| 협업 흔적 | PR, 리뷰, 이슈 기록 | 커밋만 존재 | 협업 로그 섹션 추가 |

## 저장소 구성의 최소 표준

포트폴리오 초기에 가장 효과적인 개선은 구조 표준화입니다.

```
project-name/
├── README.md         # 문제, 실행, 데모, 배운 점
├── docs/
│   ├── decisions.md  # 기술 선택 근거
│   ├── demo.gif      # 동작 증거
│   └── retrospective.md  # 회고
├── tests/            # 핵심 로직 검증
├── src/              # 메인 코드
├── Makefile          # 재현 가능한 실행 커맨드
└── LICENSE           # 사용 조건 명시
```

특히 README의 "What I Learned" 섹션은 차별화 포인트입니다. 성공만 쓰기보다 실패와 수정 과정을 적어야 실전 감각이 드러납니다.

## 학부 프로젝트를 경력 스토리로 바꾸는 법

면접에서 강한 프로젝트는 규모가 큰 프로젝트가 아니라, 깊이가 보이는 프로젝트입니다. "시간표 충돌 탐지 앱" 자체는 흔할 수 있지만, 데이터 검증 규칙을 어떻게 설계했는지, 잘못된 입력을 어떻게 다뤘는지, 성능 병목을 어떻게 측정했는지를 설명하면 충분히 강한 스토리가 됩니다.

프로젝트마다 반드시 남겨야 할 3가지:

1. 의사결정 3개: 무엇을, 왜, 어떤 대안 대신 선택했는가
2. 실패 2개: 어떤 문제가 있었고 어떻게 줄였는가
3. 다음 개선 1개: 시간이 더 있으면 무엇을 바꿀 것인가

이 세 가지가 README나 docs/decisions.md에 있으면 면접관이 "이야기할 거리가 있는 프로젝트"로 분류합니다.

## 포트폴리오 목적별 강조 포인트

포트폴리오는 목적에 따라 강조점이 달라집니다.

| 목적 | 강조 요소 | 필수 증거 | 보강 문서 |
| --- | --- | --- | --- |
| 취업 지원 | 문제 해결, 협업, 배포 | 데모 영상, 테스트, PR 기록 | 장애 회고, 성능 개선 노트 |
| 대학원 지원 | 문제 정의, 실험, 재현성 | 실험 로그, 결과 표, 코드 | 논문 요약, 한계/향후 연구 |
| 인턴십 지원 | 빠른 실행력, 코드 품질 | 동작하는 데모, 테스트 | 코드 리뷰 댓글, PR 이력 |

취업 지원에서는 "문제 해결 → 구현 → 배포"가 하나의 흐름으로 연결되어야 합니다. 대학원 지원에서는 "문제 정의 → 실험 → 결과 해석"이 논문 형식에 가까울수록 좋습니다.

## 커밋 메시지가 의사결정 로그가 되는 방법

커밋 메시지는 "update"나 "fix" 수준으로는 아무 정보도 전달하지 못합니다. 면접관이 커밋 로그를 보면 개발 과정의 사고 흐름이 보여야 합니다.

**약한 커밋 메시지 예시**:
```
update main
fix bug
add feature
```

**강한 커밋 메시지 예시**:
```
feat(conflict): add day-based conflict detection for overlapping lectures

- Detects conflicts within a single day's schedule
- Uses interval intersection logic O(n^2) for now; acceptable for MVP
- Edge case: same start/end time treated as non-conflict (matches spec)
```

이런 메시지가 10개 이상 쌓이면 커밋 로그 자체가 기술 블로그 수준의 의사결정 기록이 됩니다.

## 포트폴리오 유지보수 루틴

포트폴리오는 한 번 만들고 끝나는 문서가 아닙니다. 분기마다 정리하지 않으면 링크가 깨지고 실행 방법이 오래되어 신뢰를 잃습니다.

분기 1회 점검 루틴:
- [ ] 데모 링크 동작 확인
- [ ] 실행 명령이 현재 환경에서 작동하는지 확인
- [ ] 의존성 버전 명시 업데이트
- [ ] README 요약 최신화
- [ ] 새로 배운 점 추가

또한 프로젝트별로 "한 줄 가치"를 고정해 두십시오. 예: "시간표 충돌을 1초 이내 탐지". 사용자 가치를 먼저 적고 기술 설명은 그 다음에 오면 읽는 사람이 즉시 맥락을 파악할 수 있습니다.

## 자주 묻는 질문: 학기 과제를 공개해도 되는가

학기 과제 코드의 공개 여부는 학교 정책에 따라 다릅니다. 일부 학교는 과제 코드 공개를 금지합니다. 공개 전에 학교 정책을 먼저 확인하는 것이 중요합니다.

과제 코드를 공개할 수 없는 경우의 대안:
- 같은 아이디어를 새로운 데이터셋이나 다른 언어로 재구현
- 핵심 알고리즘만 추출해 독립 라이브러리로 작성
- 과제에서 배운 내용을 블로그 포스트나 기술 노트로 남기기

어떤 경우에도 "무엇을 배웠는가"는 공개할 수 있습니다.

## 자주 하는 실수 5가지

1. **README를 비워 두는 일입니다.** 코드가 아무리 좋아도 설명이 없으면 다른 사람이 읽지 않습니다.
2. **커밋 메시지를 모두 "update"처럼 모호하게 남기는 일입니다.** 커밋 로그가 의사결정 기록이 되어야 합니다.
3. **라이선스를 빼먹는 일입니다.** 라이선스가 없으면 기본적으로 사용 불가입니다.
4. **스크린샷이나 데모 없이 설명만 남기는 일입니다.** 동작하는 증거가 가장 강한 설득입니다.
5. **실행 방법을 적지 않아 재현이 어려운 상태로 두는 일입니다.** 5분 안에 실행할 수 없으면 면접관이 포기합니다.

## 운영 체크리스트

- [ ] README에 핵심 섹션(요약, 데모, 실행, 배운 점)을 넣었습니다.
- [ ] 라이선스를 추가했습니다.
- [ ] 스크린샷이나 데모를 준비했습니다.
- [ ] 실행 명령을 바로 보이게 적었습니다.
- [ ] 기술 선택 근거를 1개 이상 기록했습니다.
- [ ] 커밋 메시지가 변경 이유를 담고 있습니다.
- [ ] 분기 1회 점검 루틴을 캘린더에 넣었습니다.

## 처음 질문으로 돌아가기

- **전공 과제와 프로젝트는 어떻게 포트폴리오가 될 수 있을까요?**
  - 저장소에 README를 붙이고, 실행 방법과 데모를 추가하고, 의사결정 이유를 기록하면 과제가 포트폴리오가 됩니다. 코드는 그대로여도 문서가 맥락을 만들어 줍니다. 재민 시나리오가 이 차이를 잘 보여 줍니다.

- **GitHub 저장소, README, 실행 방법, 데모 링크는 왜 모두 중요할까요?**
  - 각각이 다른 질문에 답합니다. 저장소는 "코드가 있는가", README는 "무엇을 왜 만들었는가", 실행 방법은 "직접 확인할 수 있는가", 데모는 "실제로 동작하는가"입니다. 하나라도 빠지면 면접관이 추측으로 채워야 합니다.

- **코드만 올려 두는 것과 설명 가능한 결과물을 공개하는 것은 무엇이 다를까요?**
  - 재민 시나리오처럼 코드만 있으면 읽는 사람이 맥락을 추측해야 합니다. 설명 가능한 결과물은 "왜 이걸 만들었고 어떤 선택을 했는지"를 바로 전달합니다. 코드 품질이 같아도 설명 능력이 다르면 면접 결과가 달라집니다.

- **면접관이 포트폴리오를 볼 때 실제로 무엇을 먼저 확인할까요?**
  - README를 먼저 봅니다. 문제 정의가 명확한지, 실행 방법이 있는지, 기술 선택 이유가 있는지를 빠르게 확인합니다. 코드는 그 다음입니다. README에서 관심이 생겨야 코드를 열어 봅니다.

- **포트폴리오를 지속적으로 개선하는 최소 루틴은 무엇일까요?**
  - 분기 1회 점검이 핵심입니다. 데모 링크, 실행 가능 여부, README 최신화를 체크하면 품질이 유지됩니다. 프로젝트를 추가하는 것보다 기존 프로젝트를 읽기 쉽게 만드는 것이 더 효과적입니다.

## 정리

포트폴리오는 특별한 사람만 만드는 장식물이 아니라, 이미 만든 과제와 프로젝트를 읽을 수 있는 형태로 정리하는 작업입니다. 저장소 이름, README, 실행 방법, 데모, 문서화가 갖춰지면 작은 과제도 충분히 의미 있는 결과물이 됩니다. 수진 시나리오처럼 10개를 얕게 만들기보다 3개를 깊게 만들고 잘 설명하는 전략이 면접에서 훨씬 강합니다. 다음 글에서는 시리즈를 마무리하며 졸업 전에 갖춰 두면 좋은 역량을 정리하겠습니다.

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
- **Computer Science Major 101 (9/10): 포트폴리오로 연결하기 (현재 글)**
- [Computer Science Major 101 (10/10): 졸업 전 갖춰야 할 역량](./10-skills-before-graduation.md)

<!-- toc:end -->

## 참고 자료

- [GitHub Docs - About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Open Source Guides - Starting an Open Source Project](https://opensource.guide/starting-a-project/)
- [The Turing Way](https://book.the-turing-way.org/)
- [Good Enough Practices in Scientific Computing](https://doi.org/10.1371/journal.pcbi.1005510)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-major-101/ko)

Tags: CS, Portfolio, GitHub, Career, Beginner
