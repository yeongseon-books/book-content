---
series: open-source-101
episode: 6
title: "Open Source 101 (6/10): 릴리스와 버전 관리"
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
  - SemVer
  - Release
  - Changelog
  - Beginner
seo_description: 시맨틱 버전, 변경 기록, 태그, 릴리스 노트를 함께 써서 예측 가능한 릴리스를 만드는 법을 설명합니다.
last_reviewed: '2026-05-15'
---

# Open Source 101 (6/10): 릴리스와 버전 관리

프로젝트를 처음 공개할 때는 코드가 돌아가기만 하면 된다고 생각하기 쉽습니다. 그런데 사용자가 생기기 시작하면 다른 문제가 바로 따라옵니다. 이번 배포가 호환성을 깨는지, 버그 수정만 들어갔는지, 지금 업데이트해도 되는지 사용자에게 어떻게 알려 줄 것인지가 중요해집니다.

이 글은 오픈소스 101 시리즈의 6번째 글입니다.

여기서는 시맨틱 버전, 변경 기록, 태그, 릴리스 노트를 함께 묶어 예측 가능한 릴리스를 만드는 기본 절차를 정리하겠습니다.

![Open Source 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/open-source-101/06/06-01-the-basic-release-map.ko.png)
*Open Source 101 6장 흐름 개요*
> 버전 관리는 기술 정보일 뿐만 아니라 **사용자와의 신뢰 계약**입니다. 버전 이름이 의미하는 바를 명확히 해야 사용자는 안심하고 업그레이드합니다.

## 이 글에서 다룰 문제

- 시맨틱 버전의 세 숫자는 각각 어떤 위험과 변화를 전달할까요?
- 사전 릴리스 태그는 언제 써야 하고 왜 생략하면 안 될까요?
- 변경 기록은 릴리스 노트와 어떻게 연결될까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 글이 중요한가

버전 번호가 일관되지 않으면 사용자는 업데이트를 두려워하게 됩니다. 호환성을 깨는 변경이 PATCH로 나가거나, 기능 추가가 아무 설명 없이 배포되면 프로젝트를 믿기 어렵습니다. 생태계는 기능보다 예측 가능성을 더 오래 기억합니다.

오픈소스뿐 아니라 내부 라이브러리도 마찬가지입니다. 의존성이 늘어날수록 버전 표기와 변경 기록은 협업 비용을 줄이는 핵심 수단이 됩니다.

## 핵심 관점

시맨틱 버전을 암기 규칙처럼만 외우면 금방 잊습니다. 대신 사용자 입장에서 이해하면 쉽습니다.

```text
MAJOR.MINOR.PATCH

MAJOR: 조심하라는 신호 (기존 코드가 깨질 수 있음)
MINOR: 새로운 기능이 들어왔다는 신호 (하위 호환 유지)
PATCH: 안심하고 올려도 된다는 신호 (버그 수정만)
```

> 버전은 변경의 크기를 말해 주는 **약속**이고, 변경 기록은 그 약속의 **실제 내용**을 설명하는 기록입니다. 이 원칙이 흔들리면 코드보다 신뢰가 먼저 흔들립니다.

## 핵심 개념

### 시맨틱 버전 규칙

| 변경 유형 | 예시 | 버전 변화 | 사용자 영향 |
|---|---|---|---|
| Breaking change | API 시그니처 변경, 기능 제거 | `1.2.3 → 2.0.0` | 마이그레이션 필요 |
| 기능 추가 (하위 호환) | 새 파라미터 추가, 새 엔드포인트 | `1.2.3 → 1.3.0` | 선택적 사용 |
| 버그 수정 | 오류 수정, 예외 처리 | `1.2.3 → 1.2.4` | 즉시 적용 권장 |
| 사전 릴리스 | 베타, 릴리스 후보 | `1.0.0-alpha.1` | 프로덕션 사용 비권장 |

### 변경 기록(CHANGELOG) 형식

**Keep a Changelog** 형식이 가장 널리 쓰입니다.

```markdown
# Changelog

모든 주목할 만한 변경 사항이 이 파일에 기록됩니다.

## [Unreleased]

### Added
- 새로운 기능 (예정)

## [1.3.0] - 2026-05-04

### Added
- `--json` 플래그 추가 (#123)
- Python 3.12 지원 (#456)

### Changed
- 기본 타임아웃을 30초에서 60초로 변경 (#789)

### Deprecated
- `old_method()` 사용 중단 예고 (v2.0.0에서 제거 예정)

### Fixed
- Windows에서 경로 구분자 오류 수정 (#101)
- UTF-8 이외 인코딩 처리 오류 수정 (#102)

### Security
- 의존성 업데이트: requests 2.31.0 (CVE-2023-32681 수정)

## [1.2.3] - 2026-04-01

### Fixed
- 빈 입력 시 발생하는 IndexError 수정 (#95)

[Unreleased]: https://github.com/owner/repo/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/owner/repo/compare/v1.2.3...v1.3.0
[1.2.3]: https://github.com/owner/repo/releases/tag/v1.2.3
```

### 사전 릴리스 전략

정식 릴리스 전에 사전 릴리스 버전을 공개하면 사용자 피드백을 받을 수 있고, 호환성 문제를 조기에 발견할 수 있습니다.

```text
1.0.0-alpha.1  → 초기 시험판, 기능 불완전, API 변경 가능
1.0.0-alpha.2  → 추가 기능, 버그 수정
1.0.0-beta.1   → 기능 완성, 버그 수정 단계
1.0.0-beta.2   → 피드백 반영
1.0.0-rc.1     → 최종 후보, 치명적 버그만 수정
1.0.0-rc.2     → 마지막 수정
1.0.0           → 정식 릴리스
```

메이저 버전(2.0.0)은 사전 릴리스를 반드시 여러 번 거치는 편이 안전합니다.

## 릴리스 절차 전체 예시

```bash
# 1. 버전 결정
# 이번 변경이 새 기능인지, 버그 수정인지, 호환성을 깨는지 판단
# Breaking change → MAJOR
# New feature (backward compatible) → MINOR
# Bug fix → PATCH

# 2. CHANGELOG 갱신
# [Unreleased] 섹션을 새 버전으로 이동
vim CHANGELOG.md

# 3. 버전 파일 업데이트
# Python 프로젝트
sed -i 's/version = "1.2.3"/version = "1.3.0"/' pyproject.toml
# 또는 bump2version 사용
bump2version minor  # 1.2.3 → 1.3.0

# 4. 최종 확인
git diff  # 변경 내용 검토
pytest    # 테스트 통과 확인

# 5. 태그 생성 (주석 달린 태그 사용)
git add CHANGELOG.md pyproject.toml
git commit -m "chore: release v1.3.0"
git tag -a v1.3.0 -m "Release v1.3.0

Added --json flag and Python 3.12 support.
See CHANGELOG.md for full details."

# 6. 태그 푸시
git push origin main
git push origin v1.3.0

# 7. GitHub Release 생성
gh release create v1.3.0 \
  --title "v1.3.0 - JSON Output and Python 3.12 Support" \
  --notes-file CHANGELOG-1.3.0.md \
  --latest

# 8. 패키지 배포 (선택)
# Python
python -m build
twine upload dist/*
```

## CI 기반 릴리스 자동화

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      id-token: write  # PyPI trusted publishing

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # 전체 히스토리 (릴리스 노트 자동 생성용)

    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Run tests
      run: pytest

    - name: Build package
      run: python -m build

    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        generate_release_notes: true  # PR 제목 기반 자동 생성
        files: dist/*

    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      # trusted publishing - 토큰 불필요
```

### 사전 릴리스 자동화

```yaml
# .github/workflows/pre-release.yml
name: Pre-Release

on:
  push:
    tags:
      - 'v*-alpha*'
      - 'v*-beta*'
      - 'v*-rc*'

jobs:
  pre-release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Create pre-release
      run: |
        gh release create ${{ github.ref_name }} \
          --prerelease \
          --generate-notes \
          --title "Pre-release ${{ github.ref_name }}"
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 릴리스 노트 작성 모범 사례

릴리스 노트는 CHANGELOG와 달리 사용자 관점에서 쓴 설명입니다.

```markdown
# Release v2.0.0 - Major Redesign

## 주요 변경 사항

### 비동기 API로 전환
모든 네트워크 호출이 이제 async/await를 지원합니다.
응답 속도가 평균 3배 향상됩니다.

### 타입 힌트 완전 지원
MyPy strict 모드와 호환됩니다.

### 개선된 오류 메시지
오류 발생 시 수정 방법을 함께 제안합니다.

## Breaking Changes

기존 v1.x 사용자분들께 안내드립니다:

### connect()가 이제 async 함수입니다

```python
# Before (v1.x)
client = Client(api_key)
result = client.fetch()

# After (v2.0)
client = await Client.create(api_key)
result = await client.fetch()
```

### 설정 형식 변경

```python
# Before (v1.x)
Config(timeout=30, retry=3)

# After (v2.0)
Config(timeout_seconds=30, max_retries=3)
```

## 마이그레이션 가이드

전체 가이드: https://docs.example.com/v2-migration

자동 마이그레이션 도구:
```bash
pip install mytool-migrate
mytool-migrate --input old_code.py --output new_code.py
```

## 기여자 감사

@alice, @bob 외 12명의 기여자 덕분에 이번 릴리스가 가능했습니다.
```

## 버전 관리 도구 비교

| 도구 | 방식 | 장점 | 단점 | 추천 상황 |
|---|---|---|---|---|
| 수동 | 직접 버전 파일 수정 + 태그 | 유연함, 제어 가능 | 실수 가능, 시간 소요 | 초소규모 프로젝트 |
| bump2version | 설정 파일 기반 버전 증가 | Python 통합 쉬움 | 릴리스 노트 자동화 없음 | Python 프로젝트 |
| release-drafter | PR 라벨 기반 초안 작성 | 릴리스 노트 자동화 | 버전 태깅 수동 | 팀 프로젝트 |
| semantic-release | commit message 기반 완전 자동화 | CI/CD 완전 자동화 | 초기 설정 복잡 | 릴리스 빈도 높은 프로젝트 |

## 자주 하는 실수

| 실수 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| Breaking change를 MINOR로 배포 | 함수 시그니처 변경을 `1.3.0`으로 릴리스 | Breaking change는 반드시 MAJOR 버전 증가 |
| CHANGELOG 없는 릴리스 | 태그만 붙이고 변경 내용 없음 | 릴리스 전 CHANGELOG 항상 업데이트 |
| 버전 문자열과 태그 불일치 | 코드에 `1.3.0`, 태그는 `v1.3.1` | 버전 파일과 태그를 같은 커밋에서 동기화 |
| 사전 릴리스 건너뜀 | 큰 변경을 테스트 없이 바로 1.0.0으로 출시 | alpha → beta → rc 단계 거치기 |
| 릴리스 노트 비어 있음 | GitHub Release에 "Release v1.3.0" 제목만 | 변경 사항, Breaking change, 마이그레이션 가이드 포함 |

## 실무에서는 이렇게 생각한다

시니어 엔지니어는 버전 번호를 기술 장식이 아니라 소통 수단으로 봅니다. 버전 표기가 정확하면 업그레이드 판단이 빨라지고, 변경 기록이 좋으면 지원 비용이 줄어듭니다.

**RELEASING.md 문서를 두는 것을 권장합니다**:

```markdown
# Releasing

## 버전 상승 규칙
- MAJOR: 공개 API 호환성 깨짐, `config.py`의 `API_VERSION` 변경 포함
- MINOR: 하위 호환 기능 추가, 새 파라미터 추가
- PATCH: 버그 수정, 문서/내부 개선, 의존성 업데이트

## 릴리스 전 체크리스트
- [ ] CHANGELOG [Unreleased] 섹션 업데이트
- [ ] `pyproject.toml` 버전 업데이트
- [ ] 모든 테스트 통과 (`pytest`)
- [ ] 문서 업데이트 (`docs/`)
- [ ] Breaking change 시 마이그레이션 가이드 작성
- [ ] `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] `git push origin vX.Y.Z`
- [ ] GitHub Release 생성 및 릴리스 노트 작성
```

## 운영 체크리스트

- [ ] 이번 변경에 맞는 버전을 골랐습니다.
- [ ] CHANGELOG를 업데이트했습니다.
- [ ] 태그를 만들고 푸시할 준비를 했습니다.
- [ ] 릴리스 노트를 공개할 방법을 정했습니다.
- [ ] CI/CD가 태그 기반으로 자동 배포를 처리합니다.

## 연습 문제

1. 호환성 깨짐 변경 예시를 한 문장으로 적어 보세요.
2. 사전 릴리스 태그 예시를 한 줄 적어 보세요.
3. 태그와 브랜치의 차이를 한 문장으로 적어 보세요.

## 정리

이번 글에서는 릴리스와 버전 관리를 코드 배포 절차가 아니라 사용자와의 약속 관리로 보는 관점을 정리했습니다. 시맨틱 버전과 변경 기록이 함께 움직이면 프로젝트는 훨씬 예측 가능해집니다.

다음 글에서는 커뮤니티 운영을 다룹니다. 코드를 공개하고 릴리스까지 했다면, 이제는 사람들이 오래 머물 수 있는 환경도 함께 만들어야 합니다.

## 처음 질문으로 돌아가기

- **시맨틱 버전의 세 숫자는 각각 어떤 위험과 변화를 전달할까요?**
  - MAJOR는 기존 코드가 깨질 수 있다는 경고 신호이고, 사용자는 마이그레이션을 준비해야 합니다. MINOR는 기존 코드를 그대로 두고 새 기능을 선택적으로 쓸 수 있다는 신호입니다. PATCH는 버그만 수정되어 즉시 적용해도 안전하다는 신호입니다.
- **사전 릴리스 태그는 언제 써야 하고 왜 생략하면 안 될까요?**
  - 대규모 변경(MAJOR 버전), 새 API 설계, 큰 아키텍처 변화 시 사전 릴리스를 거쳐야 합니다. 생략하면 사용자가 실제 사용에서 처음 버그를 발견하게 되어 신뢰가 떨어집니다. alpha → beta → rc 단계를 거치면 각 단계에서 다른 유형의 사용자가 테스트에 참여합니다.
- **변경 기록은 릴리스 노트와 어떻게 연결될까요?**
  - CHANGELOG는 기술 변경을 시간 순으로 기록하는 개발자 내부 문서입니다. 릴리스 노트는 CHANGELOG를 기반으로 사용자 관점에서 다시 쓴 공개 문서입니다. CHANGELOG의 항목을 사용자 영향 기준으로 재구성하고, Breaking change에 마이그레이션 가이드를 추가하면 릴리스 노트가 됩니다.

<!-- toc:end -->

## 참고 자료

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [git tag docs](https://git-scm.com/docs/git-tag)
- [semver/semver 저장소](https://github.com/semver/semver)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/open-source-101/ko)

Tags: OpenSource, SemVer, Release, Changelog, Beginner
