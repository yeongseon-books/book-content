---
series: open-source-101
episode: 2
title: "Open Source 101 (2/10): 라이선스 이해하기"
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
  - License
  - MIT
  - GPL
  - Beginner
seo_description: MIT, Apache 2.0, GPL의 차이와 오픈소스 라이선스를 권한과 의무 기준으로 읽는 법을 정리합니다.
last_reviewed: '2026-05-15'
---

# Open Source 101 (2/10): 라이선스 이해하기

오픈소스를 고를 때 초보자는 기능부터 봅니다. 당장 문제를 해결해 줄 수 있는지, 설치가 쉬운지, 예제가 잘 돼 있는지가 먼저 눈에 들어옵니다. 그런데 실무에서는 코드보다 먼저 읽어야 하는 문서가 있습니다. 바로 라이선스입니다. 어떤 권리가 허용되는지, 어떤 고지를 남겨야 하는지, 어디까지 재배포할 수 있는지가 모두 여기에서 갈립니다.

이 글은 오픈소스 101 시리즈의 2번째 글입니다.

여기서는 MIT, Apache 2.0, GPL을 중심으로, 오픈소스 라이선스를 이름 암기가 아니라 권한과 의무를 읽는 기준으로 정리하겠습니다.

![Open Source 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/open-source-101/02/02-01-draw-the-license-map-first.ko.png)
*Open Source 101 2장 흐름 개요*
> 라이선스는 기술 문서가 아닙니다. 공동으로 소프트웨어를 개발하는 사람들 사이의 **신뢰 계약**입니다.

## 이 글에서 다룰 문제

- permissive와 copyleft는 무엇이 다를까요?
- MIT, Apache 2.0, GPL v3는 어떤 상황에서 부담이 달라질까요?
- SPDX 식별자는 왜 문서화와 자동화에서 중요할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 글이 중요한가

라이선스를 법무팀 일로만 미루면 늦는 경우가 많습니다. 기업에서 오픈소스 도입을 결정하는 순간은 개발자가 `pip install` 또는 `npm install`을 치는 순간입니다. 그 라이브러리에 GPL이 붙어 있고 제품에 정적으로 링크되면, 나중에 이를 제거하거나 소스를 공개하는 비용이 크게 늘어납니다.

반대로 라이선스를 초기에 이해하고 관리하면 보안 리스크를 줄이고, 법적 분쟁을 예방하고, 기업 컴플라이언스 요건을 충족하기가 훨씬 쉬워집니다. 오픈소스는 기술 선택과 법적 선택이 동시에 일어나는 영역입니다.

## 핵심 관점

라이선스를 읽을 때는 이름보다 질문이 중요합니다.

- 이 코드를 수정해도 되는가
- 재배포해도 되는가
- 저작권 고지를 남겨야 하는가
- 파생물의 소스를 공개해야 하는가
- 특허 관련 보호는 있는가

이 다섯 질문에 답할 수 있으면 이미 절반은 이해한 셈입니다.

> 라이선스 선택은 현재보다 **미래**를 좌우합니다. 지금 당장 코드를 실행하는 데는 차이가 없어 보여도, 나중에 상용 제품에 포함할지, 수정본을 배포할지, 특허 위험을 어떻게 다룰지는 모두 라이선스 문장에서 갈립니다.

## 핵심 개념

### 라이선스 분류 체계

오픈소스 라이선스는 크게 허용형(permissive)과 카피레프트(copyleft)로 나뉩니다.

**허용형(permissive)** 라이선스는 사용, 수정, 배포, 상용 이용까지 비교적 넓게 허용합니다. MIT, Apache 2.0, BSD가 여기에 속합니다. 파생물을 비공개로 유지할 수 있습니다.

**카피레프트(copyleft)** 라이선스는 파생 저작물에도 공유 의무를 강하게 연결합니다. GPL, LGPL, AGPL이 여기에 속합니다. 수정 배포 시 소스를 공개해야 합니다.

어느 쪽이 더 낫다기보다, 프로젝트 목표와 배포 방식에 따라 부담과 이점이 달라집니다.

### 라이선스 비교 요약 표

| 항목 | MIT | Apache 2.0 | GPL v3 | LGPL v2.1 | BSD 2-Clause |
|---|---|---|---|---|---|
| 상업적 사용 | 허용 | 허용 | 허용 | 허용 | 허용 |
| 수정 후 비공개 배포 | 가능 | 가능 | 불가 (소스 공개 의무) | 조건부 (동적 링크 시 가능) | 가능 |
| 특허 조항 | 없음 | 명시적 특허 허여 | 없음 | 없음 | 없음 |
| 저작권 고지 유지 | 필수 | 필수 | 필수 | 필수 | 필수 |
| 변경 사항 표시 | 불필요 | 필요 | 필요 | 필요 | 불필요 |
| 대표 사용처 | jQuery, Express | Kubernetes, Android | Linux kernel, GCC | Qt, glibc | FreeBSD, nginx |

### 반드시 알아야 할 다섯 가지 개념

**permissive** — 사용, 수정, 배포, 상용 이용까지 비교적 넓게 허용합니다. 재사용 장벽이 낮습니다.

**copyleft** — 파생 저작물에도 공유 의무를 강하게 연결합니다. 수정 후 배포 시 소스를 공개해야 합니다.

**public domain** — 저작권 제한을 사실상 두지 않는 개념입니다. 국가별 해석 차이까지 확인해야 합니다. CC0 표기를 사용합니다.

**dual license** — 하나의 소프트웨어를 두 가지 라이선스 체계로 제공합니다. MySQL은 GPL과 상업용 라이선스를 동시에 제공합니다. 오픈소스와 상용 모델을 함께 운영할 때 자주 보입니다.

**SPDX** — 라이선스를 짧고 일관된 식별자로 표현하는 표준입니다. `MIT`, `Apache-2.0`, `GPL-3.0-only`처럼 씁니다. 자동 검사 도구가 읽기 쉬워서 실무 가치가 큽니다.

## 라이선스별 실제 의무 예시

### MIT 라이선스

가장 단순한 허용형 라이선스입니다. 조건이 하나뿐입니다.

```text
MIT License

Copyright (c) 2024 Author Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

**실제 의무**: 배포 시 위 저작권 고지를 포함하면 됩니다. 소스 공개 의무 없음.

### Apache 2.0 라이선스

MIT와 비슷하지만 특허 조항이 명시됩니다.

```text
Apache License, Version 2.0

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

4. Redistribution. You may reproduce and distribute copies of the Work...

Subject to the terms and conditions of this License, each Contributor hereby
grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free,
irrevocable patent license...
```

**실제 의무**: 저작권 고지 + NOTICE 파일 유지 + 변경 사항 표시. 특허 보호 포함.

### GPL v3 라이선스

강한 카피레프트입니다. 파생물 소스 공개가 필수입니다.

```text
GNU GENERAL PUBLIC LICENSE Version 3

You may copy and distribute verbatim copies of the Program's source code
as you receive it...

You may convey verbatim copies of the Program's source code as you receive it...
but you must also release all derivative works under GPL v3 terms.
```

**실제 의무**: 배포 시 소스 코드 공개 필수. 파생물도 GPL v3 적용 필수.

## 라이선스 선택 결정 트리

프로젝트를 시작할 때 라이선스 선택은 다음 순서로 결정합니다.

```text
1. 상용 제품에 포함할 계획인가?
   - Yes: MIT, Apache 2.0, BSD 중 선택
   - No: GPL 계열 고려 가능

2. 특허 보호가 필요한가?
   - Yes: Apache 2.0 선택
   - No: MIT로 충분

3. 커뮤니티 환원을 강제하고 싶은가?
   - Yes: GPL v3 선택
   - No: MIT, Apache 2.0

4. 라이브러리로서 상용 제품과 함께 쓰이는가?
   - Yes: LGPL 고려 (동적 링크 허용)
   - No: MIT
```

가장 흔한 실수는 "모든 사람이 MIT를 쓰니까 나도 MIT"라고 생각하는 것입니다. 프로젝트의 목표와 맞지 않는 라이선스는 나중에 변경하기 매우 어렵습니다. 기존 기여자 전원의 동의가 필요하기 때문입니다.

## 실무에서 라이선스 확인하는 법

### 의존성 라이선스 자동 확인

수동으로 모든 의존성의 라이선스를 확인하는 것은 불가능합니다. 도구를 사용합니다.

```bash
# Python 프로젝트
pip install pip-licenses
pip-licenses --format=markdown --with-urls

# 출력 예시:
# | Name       | Version | License    | URL                          |
# |------------|---------|------------|------------------------------|
# | requests   | 2.31.0  | Apache 2.0 | https://github.com/psf/...   |
# | flask      | 3.0.0   | BSD-3      | https://github.com/pallets/  |
# | django     | 4.2.1   | BSD-3      | https://github.com/django/   |
```

```bash
# Node.js 프로젝트
npx license-checker --summary

# 출력 예시:
# MIT: 142
# ISC: 23
# Apache-2.0: 18
# BSD-3-Clause: 12
```

### CI에서 라이선스 정책 강제

```yaml
# .github/workflows/license-check.yml
name: License Policy Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - run: pip install pip-licenses
    - name: 금지 라이선스 확인
      run: |
        pip-licenses --fail-on="GPL-2.0;GPL-3.0;AGPL-3.0" \
          --format=markdown
```

### 저장소에 라이선스 정보 추가

```toml
# pyproject.toml
[project]
name = "my-tool"
version = "1.0.0"
license = { text = "MIT" }

# SPDX 식별자 사용 (자동화 도구 호환)
# license = { expression = "MIT" }
```

## 기여 안내 문서의 라이선스 조항

기여 시 라이선스 관련 규칙을 CONTRIBUTING.md에 명시합니다.

```markdown
## 라이선스 기여 원칙

이 프로젝트는 MIT 라이선스를 따릅니다.

### 기여 시 확인 사항

- 외부 코드 조각 인용 시 원문 URL과 라이선스를 PR에 명시합니다
- 저작권 고지가 필요한 파일은 제거하지 않습니다
- 의존성 추가 시 라이선스 종류를 PR 본문에 함께 적습니다
- GPL 계열 코드는 이 프로젝트에 포함할 수 없습니다

### 허용 라이선스 목록 (allowlist)

- MIT
- Apache-2.0
- BSD-2-Clause
- BSD-3-Clause
- ISC

### 금지 라이선스 목록 (blocklist)

- GPL-2.0
- GPL-3.0
- AGPL-3.0
- LGPL (정적 링크 시)
```

## 직접 따라해 보기: 라이선스 비교 절차

### 1단계 — MIT의 핵심 읽기

MIT는 입문자가 가장 자주 만나는 라이선스입니다. 허용 범위가 넓고 조건이 비교적 단순합니다.

```text
Allows: use, modify, distribute, sell
Requires: keep the copyright notice
Copyleft: No
Patent protection: No
```

### 2단계 — Apache 2.0의 차이 보기

Apache 2.0은 MIT와 비슷해 보여도 특허 조항이 명시된다는 점에서 실무적으로 자주 구분됩니다.

```text
Allows: same as MIT
Adds: explicit patent grant
Requires: copyright notice + NOTICE file + mark changes
Copyleft: No
Patent protection: Yes (explicit grant)
```

### 3단계 — GPL v3의 의무 읽기

GPL은 공유를 강하게 지키는 라이선스입니다. 사용만 하는 경우와 배포하는 경우를 구분해 읽어야 합니다.

```text
Allows: use, modify, distribute
Requires: derivative works share their source under GPL v3
Copyleft: Strong (all derivatives)
Patent protection: Implicit
```

### 4단계 — SPDX 식별자 확인하기

자동 도구가 읽을 수 있는 식별자를 함께 정리합니다.

```yaml
# package.json
{
  "license": "MIT"
}

# pyproject.toml
license = { expression = "Apache-2.0" }

# 파일 헤더
# SPDX-License-Identifier: GPL-3.0-only
```

### 5단계 — 원문 라이선스 가져오기

직접 복사해 붙이는 것보다 검증된 원문을 가져와 사용합니다.

```bash
# choosealicense.com에서 원문 다운로드
curl -sL https://api.github.com/licenses/mit \
  | jq -r '.body' > LICENSE

# GitHub CLI로 저장소 생성 시 라이선스 지정
gh repo create my-project --public --license mit
```

## 자주 하는 실수

| 실수 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| 라이선스 텍스트 무의미 복사 | MIT 텍스트를 붙여 넣고 내용은 읽지 않음 | 권리·의무 5가지 질문으로 읽기 |
| 저작권 고지 삭제 | 배포 패키지에서 LICENSE 파일 제거 | 모든 배포에 저작권 고지 포함 필수 |
| GPL 상용 무의식 사용 | GPL 라이브러리를 정적 링크해 상용 제품 출시 | 도입 전 라이선스 확인, LGPL이나 MIT 대안 탐색 |
| dual license 오독 | 오픈소스 버전 조건으로 상용 버전 사용 | 두 라이선스 모두 읽고 적용 조건 확인 |
| SPDX 누락 | `license = "MIT"`를 파일에 넣지 않음 | 패키지 메타데이터와 파일 헤더에 SPDX 식별자 추가 |

## 실무에서는 이렇게 생각한다

기업은 보통 개발자 개인 판단만으로 라이선스를 도입하지 않습니다. FOSSA, Snyk 같은 스캐너로 의존성 트리를 훑고, 금지 목록이나 검토 목록을 따로 둡니다. 한 번 릴리스된 제품 안에 들어간 코드의 법적 부담은 나중에 되돌리기 어렵기 때문입니다.

**조직의 라이선스 검토 프로세스** — 기업에서 오픈소스 도입을 결정할 때는 다음 단계를 거칩니다:

```text
1. 기술 팀이 후보 라이브러리 선정
2. 라이선스 스캐너로 전체 의존성 트리 분석
   - pip-licenses (Python)
   - license-checker (Node.js)
   - FOSSA, Snyk (다국어)
3. 금지 라이선스 포함 여부 확인
   - GPL-2.0, GPL-3.0, AGPL → 대부분 상용 금지
   - MIT, Apache-2.0, BSD → 대부분 허용
   - LGPL → 동적 링크 조건 검토
4. 법무팀 검토 요청 (불명확한 경우)
5. 승인 후 내부 허용 목록에 추가
```

시니어 엔지니어도 라이선스를 법무팀 일로만 미루지 않습니다. 오히려 초기에 어떤 라이선스가 들어왔는지 파악하고, 저장소 문서와 패키지 메타데이터가 일관된지 확인하는 습관을 가집니다.

## 운영 체크리스트

- [ ] `LICENSE` 파일이 있는지 확인했습니다.
- [ ] SPDX 식별자를 확인하거나 추가할 위치를 파악했습니다.
- [ ] 저작권 고지 유지 의무를 이해했습니다.
- [ ] 사용하려는 프로젝트와 내 프로젝트의 라이선스 호환성을 검토했습니다.
- [ ] CI에서 의존성 라이선스를 자동 검사하는 단계가 있습니다.

## 연습 문제

1. 허용형과 카피레프트의 차이를 한 문장으로 적어 보세요.
2. Apache 2.0이 MIT와 구분되는 대표 지점을 한 문장으로 적어 보세요.
3. dual license가 왜 비즈니스 전략이 될 수 있는지 설명해 보세요.

## 정리

이번 글에서는 라이선스를 저장소의 부속 문서가 아니라 사용 조건을 적어 둔 계약서로 보는 관점을 정리했습니다. 오픈소스를 쓴다는 것은 기능만 가져오는 일이 아니라, 그 코드에 붙어 있는 규칙까지 함께 받아들이는 일입니다.

다음 글에서는 이슈를 읽는 법을 다룹니다. 기여를 시작하려면 어떤 문제를 고를지, 그리고 그 문제를 어떻게 해석할지부터 분명해야 합니다.

## 처음 질문으로 돌아가기

- **permissive와 copyleft는 무엇이 다를까요?**
  - permissive는 파생물의 소스 공개 의무가 없어 상용 제품에 포함하기 쉽습니다. copyleft는 파생물도 같은 라이선스를 적용해야 하므로 소스를 공개해야 합니다. 같은 오픈소스라도 MIT 코드를 수정한 상용 제품은 소스를 숨길 수 있지만, GPL 코드를 수정한 상용 제품은 소스를 공개해야 합니다.
- **MIT, Apache 2.0, GPL v3는 어떤 상황에서 부담이 달라질까요?**
  - MIT는 저작권 고지만 유지하면 상업 이용 포함 자유롭게 사용 가능합니다. Apache 2.0은 MIT에 특허 보호 조항이 추가되어 기업 환경에서 선호됩니다. GPL v3는 수정 배포 시 소스 공개 의무가 있어 상용 제품에 포함하기 전 법무 검토가 필수입니다.
- **SPDX 식별자는 왜 문서화와 자동화에서 중요할까요?**
  - SPDX 식별자는 `MIT`, `Apache-2.0`처럼 표준화된 짧은 문자열로 라이선스를 표현합니다. CI 도구, 패키지 관리자, 법적 검토 도구가 이 식별자를 파싱해 자동으로 정책을 검사합니다. 식별자가 없으면 자동 검사 체인이 끊기고 수동 검토 비용이 늘어납니다.

<!-- toc:end -->

## 참고 자료

- [Choose a License](https://choosealicense.com/)
- [SPDX License List](https://spdx.org/licenses/)
- [Open Source Initiative Licenses](https://opensource.org/licenses)
- [github/choosealicense.com 저장소](https://github.com/github/choosealicense.com)
- [tl;dr Legal](https://www.tldrlegal.com/)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/open-source-101/ko)

Tags: OpenSource, License, MIT, GPL, Beginner
