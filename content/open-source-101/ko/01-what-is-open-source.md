---
series: open-source-101
episode: 1
title: "Open Source 101 (1/10): 오픈소스란 무엇인가"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - OpenSource
  - GitHub
  - Community
  - Contribution
  - Beginner
seo_description: 오픈소스를 단순한 무료 코드를 넘어 권리, 책임, 협업 문화가 공존하는 생태계로 정의하고 기본 용어와 참여 경로를 정리합니다.
last_reviewed: '2026-05-15'
---

# Open Source 101 (1/10): 오픈소스란 무엇인가

처음 오픈소스를 접하면 대개 가격부터 떠올립니다. 무료로 내려받아 쓸 수 있는 코드라는 감각은 출발점으로는 맞습니다. 하지만 그 설명만으로는 왜 라이선스를 읽어야 하는지, 왜 이슈와 PR이 중요한지, 왜 메인테이너와 커뮤니티 문화가 프로젝트 품질에 직접 영향을 주는지 설명되지 않습니다.

이 글은 오픈소스 101 시리즈의 첫 번째 글입니다.

여기서는 오픈소스를 단순한 코드 공개가 아니라, 읽고 고치고 다시 나눌 수 있는 권리와 그 권리를 실제 협업으로 굴리는 문화까지 포함한 개념으로 정리하겠습니다.

![Open Source 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/open-source-101/01/01-01-a-concept-map-you-can-keep-in-your-head.ko.png)
*Open Source 101 1장 흐름 개요*
> 오픈소스를 이해한다는 것은 기술 선택을 넘어 법적 조건, 참여 경로, 커뮤니티 문화까지 함께 읽는 능력입니다.

## 이 글에서 다룰 문제

- 오픈소스를 공짜 코드라고만 보면 왜 계속 오해가 생길까요?
- free software, upstream, fork, contributor 같은 기본 용어는 어떻게 구분해야 할까요?
- 코드 작성 외에도 왜 문서, 번역, 재현 절차 정리가 모두 기여가 될까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 글이 중요한가

오픈소스를 "공짜 소프트웨어"로만 이해하면 라이선스 위반, 잘못된 의존성 선택, 커뮤니티 규칙 오해 같은 실수가 계속 따라옵니다. 실무에서 서비스를 운영하는 팀이 오픈소스 라이브러리를 도입할 때는 기능 외에도 라이선스 호환성, 프로젝트 건강 상태, 메인테이너 응답 속도까지 함께 평가합니다. 이 판단 기준을 갖추려면 오픈소스가 단순한 코드 공개 이상의 개념임을 먼저 이해해야 합니다.

또한 오픈소스 기여 경험은 개인 성장에도 직접 연결됩니다. 이력서에 "Django를 다룰 줄 압니다"라고 쓰는 것과 "Django 공식 저장소에 버그 수정 PR 3개를 머지했습니다"라고 쓰는 것은 신뢰도가 다릅니다. 이 시리즈는 그 출발점을 만드는 데 목적이 있습니다.

## 핵심 관점

오픈소스를 가장 정확하게 이해하는 방법은 **코드가 공개돼 있다는 사실**과 **그 코드를 읽고, 수정하고, 재배포할 수 있는 권리**를 분리해 보는 것입니다. 소스를 볼 수 있어도 수정이나 배포가 제한된다면 오픈소스가 아닙니다. Open Source Initiative(OSI)는 이 권리를 10가지 기준으로 정의합니다.

> 오픈소스는 코드가 공개돼 있다는 사실이 아니라, 그 코드를 읽고 고치고 나눌 수 있는 **권리와 그 권리를 실제 협업으로 굴리는 문화**까지 포함한 생태계입니다.

이 관점이 중요한 이유는 이후 글들 전체가 여기서 출발하기 때문입니다. 라이선스는 이 권리를 문서로 적어 둔 장치이고, 이슈는 문제를 함께 정의하는 공간이며, PR은 변경을 공동 검토하는 절차입니다.

## 핵심 개념

### 오픈소스 역할 지도

오픈소스 생태계에는 네 가지 역할이 있습니다. 역할은 고정되지 않으며 참여 경로에 따라 자연스럽게 이동합니다.

| 역할 | 주요 활동 | 권한 | 진입 조건 |
|---|---|---|---|
| 사용자 (User) | 코드 다운로드, 실행, 이슈 보고 | 라이선스 허용 범위 내 사용 | 없음 |
| 기여자 (Contributor) | 버그 수정, 문서 개선, 번역, 테스트 | PR 제출, 이슈 작성 | 첫 PR 머지 후 |
| 커미터 (Committer) | 코드 리뷰, 라벨링, 일부 머지 | 브랜치 쓰기 권한 | 메인테이너 추천 |
| 메인테이너 (Maintainer) | 방향 결정, PR 머지, 릴리스 관리 | 저장소 전체 관리 | 장기 기여 + 신뢰 |

**사용자(User)** 는 코드를 내려받아 사용합니다. 라이선스 조건을 지키면 자유롭게 사용할 수 있습니다. 이슈를 열면 이미 기여자가 되는 첫 걸음을 뗀 셈입니다.

**기여자(Contributor)** 는 버그 리포트, 코드 수정, 문서 개선, 번역, 테스트 추가를 통해 프로젝트를 더 나은 방향으로 만드는 사람입니다. 코드 기여만이 아닙니다. 오타 수정, 번역, 예제 추가도 모두 기여입니다.

**메인테이너(Maintainer)** 는 프로젝트의 방향을 결정하고, PR을 머지하고, 이슈를 분류하고, 릴리스를 관리합니다. 장기적으로 프로젝트의 건강을 책임집니다.

**커뮤니티 리더(Community Leader)** 는 기술보다 사람을 관리합니다. 행동 강령(Code of Conduct) 유지, 갈등 조정, 신규 기여자 온보딩, 문화 형성 등을 맡습니다.

### 반드시 알아야 할 기본 용어

오픈소스를 처음 읽을 때는 많은 용어를 외우기보다, 저장소를 이해하는 데 꼭 필요한 최소 단어를 정확히 구분하는 편이 낫습니다.

**오픈소스 vs free software** — 오픈소스는 소스 코드를 볼 수 있다는 사실만이 아니라, 수정과 재배포를 허용하는 라이선스 조건까지 포함한 개념입니다. free software는 가격보다 자유에 무게를 둡니다. 비용이 0원이라는 뜻이 아니라 사용자의 권리를 강조하는 표현입니다.

**upstream** — 원래 프로젝트 저장소를 가리킵니다. 내가 포크한 저장소가 아니라 기준이 되는 본류입니다. `git remote add upstream https://github.com/owner/repo.git` 명령으로 연결합니다.

**fork** — 원본 저장소를 내 계정 아래 복제한 작업 사본입니다. 기여 흐름에서는 안전하게 실험하는 개인 작업 공간 역할을 합니다. 원본에 영향 없이 자유롭게 변경할 수 있습니다.

**contributor** — 코드만 고치는 사람이 아닙니다. 문서, 번역, 디자인, 재현 절차 정리, 사용자 지원도 모두 기여에 들어갑니다. 한 번의 기여만 해도 기여자가 됩니다.

**CONTRIBUTING.md** — 프로젝트 기여 규칙을 담은 파일입니다. 개발 환경 설정, 브랜치 전략, PR 제출 방법, 코드 스타일 기준이 여기 있습니다. 기여 전에 반드시 읽어야 합니다.

### 오픈소스 라이선스 분류

오픈소스 라이선스를 처음 읽을 때는 종류가 너무 많아 혼란스럽습니다. 하지만 실무에서는 네 가지 기준으로 대부분의 상황을 정리할 수 있습니다.

| 라이선스 | 허용 범위 | 주요 제약 | 적합한 경우 |
|---|---|---|---|
| MIT | 사용, 수정, 배포, 판매 | 저작권 고지 유지 | 작은 라이브러리, 최소 제약 선호 |
| Apache 2.0 | 동일 | 저작권 고지 + 특허 보호 | 기업 환경, 특허 리스크 회피 |
| GPL v3 | 동일 | 파생물 소스 공개 의무 | 공유 의무 강제, 커뮤니티 환원 |
| LGPL | 동일 | 라이브러리로 사용 시 공개 의무 제외 | 상용 제품과 함께 쓰이는 라이브러리 |
| BSD (3-Clause) | 동일 | 저작권 고지 + 이름 사용 제한 | 학술 · 연구 배경 프로젝트 |

라이선스 선택은 단순한 문서 작업이 아니라 프로젝트의 배포 전략과 협업 문화를 결정합니다. 같은 코드라도 어떤 라이선스를 붙이느냐에 따라 상용 제품에 포함 가능 여부, 파생물 공개 의무, 특허 보호 수준이 모두 달라집니다.

## 기여 유형별 구체적 사례

오픈소스 기여는 코드 작성만이 아닙니다. 아래는 실제 프로젝트에서 이루어지는 기여 유형과 예시입니다.

### 코드 기여

```bash
# 버그 수정 예시: FastAPI 저장소에서 실제 발생했던 타입 힌트 오류 수정
# 이슈: #1234 - Response model type hint incorrect for Optional fields
# PR: fix: correct Optional type hint in response_model validation

# 수정 전
def validate_response(response_model: Type[BaseModel]) -> None:
    pass

# 수정 후
def validate_response(response_model: Optional[Type[BaseModel]]) -> None:
    pass
```

### 문서 기여

```markdown
<!-- requests 라이브러리 문서에 실제로 기여된 예시 -->
## Quickstart

To install Requests, use pip:

```bash
pip install requests
```

<!-- 기여 내용: 예제 코드에 오류 처리 추가 -->
import requests

try:
    response = requests.get('https://api.example.com/data', timeout=10)
    response.raise_for_status()
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
```

### 번역 기여

```bash
# Django 공식 문서 한국어 번역 기여 흐름
git clone https://github.com/django/django.git
# docs/locale/ko/ 디렉토리에서 .po 파일 수정
# 예: docs/locale/ko/LC_MESSAGES/intro/tutorial01.po
msgid "Writing your first Django app"
msgstr "첫 번째 Django 앱 작성하기"
```

### 이슈 기여

```markdown
<!-- 좋은 버그 리포트 예시 -->
## Bug Report

**환경**
- Python: 3.11.2
- Django: 4.2.1
- OS: Ubuntu 22.04

**재현 단계**
1. `python manage.py runserver` 실행
2. `/admin/` 접속
3. 로그인 시도

**기대 동작**: 관리자 대시보드로 이동
**실제 동작**: 500 Internal Server Error 발생

**스택 트레이스**
```
AttributeError: 'NoneType' object has no attribute 'user'
  File "django/contrib/admin/sites.py", line 233
```
```

## PR 워크플로 전체 흐름

오픈소스 기여의 표준 흐름을 단계별로 봅니다. 첫 기여 전에 이 흐름을 한 번 눈에 넣어 두면 실수를 크게 줄일 수 있습니다.

```bash
# 1단계: 저장소 포크 및 클론
gh repo fork fastapi/fastapi --clone
cd fastapi

# 2단계: upstream 연결 (나중에 동기화를 위해 필수)
git remote add upstream https://github.com/fastapi/fastapi.git
git remote -v
# origin    https://github.com/yourusername/fastapi.git (fetch)
# upstream  https://github.com/fastapi/fastapi.git (fetch)

# 3단계: 작업 브랜치 생성 (이슈 번호 포함 권장)
git checkout -b fix/1234-optional-type-hint

# 4단계: 변경 구현 후 커밋
git add fastapi/responses.py
git commit -m "fix: correct Optional type hint in response_model

Closes #1234

The response_model parameter should accept Optional[Type[BaseModel]]
to properly handle cases where the response model may be None."

# 5단계: 테스트 실행
pytest tests/test_responses.py -v

# 6단계: 포크에 푸시
git push origin fix/1234-optional-type-hint

# 7단계: PR 생성
gh pr create \
  --title "fix: correct Optional type hint in response_model" \
  --body "Closes #1234

## Summary
Response model type hint was incorrect for Optional fields.

## Changes
- Changed `Type[BaseModel]` to `Optional[Type[BaseModel]]`
- Added test for None response model case

## Testing
- All existing tests pass
- Added 2 new test cases for Optional handling"

# 8단계: 리뷰 피드백 반영 (리뷰어 코멘트 후)
git add fastapi/responses.py tests/test_responses.py
git commit -m "fix: apply review feedback - add docstring"
git push origin fix/1234-optional-type-hint
```

## 오픈소스 참여의 실무적 이점

오픈소스 기여는 단순히 코드를 나눠 쓰는 일을 넘어 실무 역량을 키우는 가장 직접적인 경로입니다.

**이력서와 포트폴리오 효과** — 깃허브 프로필은 이력서를 보완하는 증거입니다. 면접에서 "Django를 잘 다룹니다"라고 말하는 것과 "Django 공식 저장소에 버그 수정 PR 3개를 머지했습니다"라고 말하는 것은 신뢰도가 다릅니다. 특히 신입 개발자에게는 오픈소스 기여 이력이 경력 공백을 메워 주는 가장 강한 무기가 됩니다.

**네트워크와 평판** — 오픈소스 커뮤니티에서 꾸준히 활동하면 자연스럽게 같은 기술 스택을 쓰는 개발자와 연결됩니다. 좋은 PR 하나가 메인테이너의 눈에 띄면 채용 제안으로 이어지기도 합니다. 실제로 많은 기업이 오픈소스 기여자를 우선 채용 풀로 봅니다.

**기술력과 코드 리뷰 감각** — 회사 안에서는 비슷한 사람들과 일하기 쉽지만, 오픈소스에서는 전 세계 개발자와 코드 리뷰를 주고받습니다. 다른 사람의 코드 스타일, 문서 작성법, 테스트 전략을 보면서 자연스럽게 수준이 올라갑니다.

**실패의 비용이 낮음** — 오픈소스 기여는 실패해도 크게 손해가 없습니다. PR이 거부되거나 이슈가 닫힐 수 있지만, 그 과정에서 코드 리뷰 경험, Git 흐름 연습, 커뮤니티 규칙 이해는 모두 남습니다.

## 직접 따라해 보기: 오픈소스 저장소 읽기

### 1단계 — 저장소 찾기

처음에는 아무 프로젝트나 보기보다 언어와 주제가 분명한 저장소를 고르는 편이 좋습니다.

```bash
gh search repos --language python --topic open-source
```

### 2단계 — 라이선스 확인하기

프로젝트 소개보다 먼저 라이선스를 확인해 보세요. 어떤 권리가 허용되고, 어떤 고지를 남겨야 하는지 읽는 습관이 여기서 시작됩니다.

```bash
gh repo view fastapi/fastapi --json licenseInfo
# 출력: {"licenseInfo": {"name": "MIT License", "spdxId": "MIT"}}
```

### 3단계 — 기여자 흐름 보기

저장소가 혼자 유지되는지, 여러 사람이 함께 돌보는지 보는 가장 빠른 단서입니다.

```bash
gh api repos/fastapi/fastapi/contributors --jq '.[].login' | head -10
# 출력: tiangolo, Kludex, adriangb, ...
```

### 4단계 — 입구가 열려 있는지 확인하기

`good first issue` 라벨은 프로젝트가 신규 기여자를 받아들일 준비가 되어 있다는 신호입니다.

```bash
gh issue list --repo fastapi/fastapi --label "good first issue"
```

### 5단계 — CONTRIBUTING.md 읽기

기여 규칙을 먼저 파악해야 첫 PR에서 실수를 피할 수 있습니다.

```bash
gh api repos/fastapi/fastapi/contents/CONTRIBUTING.md \
  --jq '.content' | base64 -d | head -50
```

## 자주 하는 실수

| 실수 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| 라이선스 미확인 | GPL 코드를 상용 제품에 포함 후 소스 미공개 | 도입 전 라이선스 확인, 법무 검토 |
| fork와 upstream 혼동 | 내 포크에 커밋 후 upstream에 PR 없이 사용 | `git remote -v`로 원격 확인, upstream PR 제출 |
| 이슈를 질문 게시판으로 사용 | 설치 방법 질문을 Issues에 올림 | Discussions 또는 Stack Overflow 사용 |
| 코드만 기여라고 착각 | 문서·번역 기여 시도 자체를 포기 | 오타 수정, 예제 추가도 가치 있는 기여 |
| 첫 기여를 큰 기능으로 시작 | 300줄짜리 새 기능 PR 제출 | `good first issue` 라벨 이슈부터 시작 |

## 실무에서는 이렇게 생각한다

시니어 엔지니어는 오픈소스를 기능 카탈로그처럼만 보지 않습니다. 릴리스 주기, 이슈 응답 속도, 문서 품질, 라이선스 호환성, 메인테이너 수까지 함께 봅니다. 이유는 간단합니다. 회사 서비스는 그 프로젝트의 건강 상태 위에 올라가기 때문입니다.

**오픈소스 건강도 평가 지표** — 프로젝트를 선택할 때 다음 지표를 확인하면 좋습니다:

```bash
# GitHub CLI로 프로젝트 건강도 빠르게 확인
gh repo view fastapi/fastapi --json \
  stargazerCount,forkCount,openIssues,updatedAt,licenseInfo

# 최근 커밋 날짜 (활발히 유지보수 중인가)
gh api repos/fastapi/fastapi/commits --jq '.[0].commit.author.date'

# 이슈 응답 속도 (커뮤니티가 살아 있는가)
gh issue list --repo fastapi/fastapi --state open --limit 5

# 기여자 수 (버스 팩터가 높은가)
gh api repos/fastapi/fastapi/contributors | jq length
```

작은 기여 경험은 생각보다 큰 신뢰로 이어집니다. 문서 오타 하나를 고치는 일이라도 저장소 구조를 읽고, 규칙을 따르고, 리뷰를 받고, 변경 이력을 남기는 과정을 한 번 통과하면 이후 기여 난도가 크게 낮아집니다. 첫 기여가 작아도 의미가 큰 이유가 여기 있습니다.

## 첫 기여 체크리스트

오픈소스 기여를 처음 시도할 때는 무엇부터 준비해야 할지 막막합니다. 이 체크리스트는 첫 PR을 열기 전에 놓치기 쉬운 단계를 정리한 것입니다.

**프로젝트 선택 단계**

- [ ] 내가 실제로 사용해 본 프로젝트인가
- [ ] 최근 3개월 내 활동 이력이 있는가
- [ ] `good first issue` 또는 `help wanted` 라벨이 있는가
- [ ] 기여 가이드 (`CONTRIBUTING.md`)가 있는가

**이슈 선택 단계**

- [ ] 이슈 본문에 재현 방법이나 구체적 요구사항이 있는가
- [ ] 담당자가 비어 있거나 명시적으로 도움을 요청했는가
- [ ] 내가 이해할 수 있는 범위의 문제인가
- [ ] 해결 방향에 대해 메인테이너와 합의가 있는가

**작업 준비 단계**

- [ ] 저장소를 포크하고 로컬에 클론했는가
- [ ] 개발 환경 설정 문서를 따라 빌드에 성공했는가
- [ ] 작업용 브랜치를 새로 만들었는가
- [ ] 코드 스타일 가이드를 확인했는가

**PR 제출 단계**

- [ ] 커밋 메시지가 프로젝트 규칙을 따르는가
- [ ] 테스트를 추가하거나 기존 테스트가 통과하는가
- [ ] PR 템플릿이 있다면 모든 항목을 채웠는가
- [ ] 관련 이슈를 `Closes #N` 형식으로 연결했는가

## 생각이 어떻게 바뀌어야 할까

처음에는 오픈소스를 무료 코드라고만 보기 쉽습니다. 하지만 조금만 더 들여다보면, 더 정확한 정의는 따로 있습니다. 오픈소스는 코드를 읽고 고치고 공유할 수 있는 권리와, 그 권리를 실제 협업으로 바꾸는 프로젝트 운영 방식까지 포함한 생태계입니다.

이 차이를 이해하면 이후 글들도 한 줄로 이어집니다. 라이선스는 권리를 문서로 적어 둔 장치이고, 이슈는 문제를 함께 정의하는 공간이며, PR은 변경을 공동 검토하는 절차이고, 메인테이너는 이 흐름을 오래 유지하게 만드는 사람입니다.

## 운영 체크리스트

- [ ] 관심 있는 저장소 하나를 찾았습니다.
- [ ] LICENSE 또는 `licenseInfo`를 확인했습니다.
- [ ] `good first issue` 라벨이 붙은 이슈를 하나 찾았습니다.
- [ ] `CONTRIBUTING` 또는 README에서 기여 흐름을 읽었습니다.

## 연습 문제

1. 오픈소스를 한 문장으로 정의해 보세요.
2. upstream과 fork의 차이를 한 문장으로 설명해 보세요.
3. 코드 작성 외의 기여 예시를 세 가지 적어 보세요.

## 정리

이번 글에서는 오픈소스를 무료 코드가 아니라 권리와 협업 구조를 가진 생태계로 보는 기본 관점을 잡았습니다. 이 관점이 있어야 이후에 나오는 라이선스, 이슈, PR, 커뮤니티, 메인테이너 역할이 따로 놀지 않고 하나의 흐름으로 이어집니다.

다음 글에서는 라이선스를 읽는 법을 봅니다. 오픈소스를 쓰는 순간 기술 선택만 하는 것이 아니라, 법적 조건도 함께 받아들인다는 점을 더 구체적으로 봅니다.

## 처음 질문으로 돌아가기

- **오픈소스를 공짜 코드라고만 보면 왜 계속 오해가 생길까요?**
  - 오픈소스는 가격이 아니라 권리의 문제입니다. GPL 코드는 상용 제품에 넣으면 소스 공개 의무가 생기고, Apache 2.0 코드는 특허 조항이 있습니다. "공짜니까 아무거나 써도 된다"는 생각은 라이선스 위반으로 이어집니다.
- **free software, upstream, fork, contributor 같은 기본 용어는 어떻게 구분해야 할까요?**
  - free software는 가격이 아닌 자유를 의미하고, upstream은 원본 저장소, fork는 내 작업 복사본, contributor는 코드·문서·번역을 포함한 모든 기여자를 가리킵니다. 이 네 단어를 정확히 구분하면 저장소 구조 전체가 또렷해집니다.
- **코드 작성 외에도 왜 문서, 번역, 재현 절차 정리가 모두 기여가 될까요?**
  - 메인테이너의 시간 중 가장 많이 소비되는 것은 반복 질문 답변입니다. 문서 기여는 이 비용을 줄이고, 번역은 더 많은 사람이 프로젝트를 쓸 수 있게 합니다. 오픈소스는 코드만이 아니라 그 코드를 쓸 수 있게 만드는 생태계 전체가 협업 대상입니다.

<!-- toc:end -->

## 참고 자료

- [Open Source Initiative](https://opensource.org/osd)
- [Free Software Foundation - GNU Project](https://www.gnu.org/philosophy/free-sw.html)
- [Open Source Guides - GitHub](https://opensource.guide/)
- [github/opensource.guide 저장소](https://github.com/github/opensource.guide)
- [The Cathedral and the Bazaar - Eric Raymond](http://www.catb.org/~esr/writings/cathedral-bazaar/)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/open-source-101/ko)

Tags: OpenSource, GitHub, Community, Contribution, Beginner
