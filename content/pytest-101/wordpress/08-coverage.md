---
title: "바이브코딩을 위한 pytest 기초 (8/10): 커버리지"
series: pytest-101
episode: 8
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - pytest
  - Testing
  - Coverage
  - CI
---

# 바이브코딩을 위한 pytest 기초 (8/10): 커버리지

이 글은 "바이브코딩을 위한 pytest 기초" 시리즈의 8번째 글입니다.

---

바이브코딩에서 AI는 테스트 코드를 빠르게 만들어 줍니다. 그런데 "테스트가 있다"는 것과 "코드를 충분히 테스트했다"는 것은 다른 이야기입니다. 테스트가 10개 있어도 모두 정상 경로만 확인한다면 예외 처리 코드는 한 번도 실행되지 않은 채 운영에 나갈 수 있습니다.

커버리지는 테스트가 실제로 어느 줄을 실행했는지 측정합니다. 100%가 목표가 아닙니다. 커버리지가 낮은 곳이 어디인지 보여주는 도구입니다. 30%라면 코드의 70%가 테스트된 적 없다는 뜻이고, 그 안에 버그가 숨어 있을 가능성이 큽니다.

`pytest-cov`는 pytest와 함께 커버리지를 측정해 줍니다. `--cov-report=term-missing`을 붙이면 어느 줄이 실행되지 않았는지 줄 번호로 보여줍니다. 브랜치 커버리지(`--cov-branch`)는 `if/else`에서 두 경로가 모두 실행됐는지 확인합니다. 줄 커버리지가 100%여도 브랜치 중 하나가 실행되지 않으면 버그가 숨을 수 있습니다.

AI가 만든 테스트 코드에 커버리지를 돌려보면 어떤 경로가 빠졌는지 바로 드러납니다. 특히 예외 처리, 빈 입력, 경계값 처리는 AI가 종종 빠뜨리는 부분입니다.

> **핵심 인사이트:** `pytest --cov=src --cov-report=term-missing`을 실행하면 어느 줄이 테스트되지 않았는지 줄 번호로 확인할 수 있습니다. 100% 커버리지가 버그 없음을 보장하지는 않지만, 30%라면 테스트가 거의 없다는 분명한 경고입니다.

## 이 글에서 다룰 문제

- 줄 커버리지와 브랜치 커버리지는 어떻게 다를까요?
- `pytest-cov`는 어떻게 설치하고 실행할까요?
- 커버리지 리포트에서 어떤 정보를 읽어야 할까요?
- 커버리지 최소 기준은 어떻게 설정할까요?
- AI가 만든 테스트에서 커버리지로 무엇을 확인해야 할까요?

## 커버리지 핵심 패턴

```bash
# pytest-cov 설치
pip install pytest-cov

# 기본 커버리지 측정 (src 디렉터리 대상)
pytest --cov=src

# 줄 번호로 미실행 줄 표시
pytest --cov=src --cov-report=term-missing

# 브랜치 커버리지 포함
pytest --cov=src --cov-branch --cov-report=term-missing

# HTML 리포트 생성 (브라우저에서 확인)
pytest --cov=src --cov-report=html
```

```python
# 브랜치 커버리지가 중요한 예시
def validate_email(email: str) -> bool:
    if not email:               # 브랜치 1: 빈 문자열
        return False
    if "@" not in email:        # 브랜치 2: @ 없음
        return False
    local, domain = email.split("@", 1)
    if not local:               # 브랜치 3: @ 앞이 비어있음
        return False
    if "." not in domain:       # 브랜치 4: 도메인에 . 없음
        return False
    return True

# 이 테스트만으로는 줄 커버리지 100%지만 브랜치가 빠짐
def test_valid_email():
    assert validate_email("user@example.com") is True
    assert validate_email("") is False

# 브랜치 커버리지를 위한 추가 테스트
def test_email_branches():
    assert validate_email("") is False          # 브랜치 1
    assert validate_email("noatsign") is False  # 브랜치 2
    assert validate_email("@example.com") is False  # 브랜치 3
    assert validate_email("user@nodot") is False    # 브랜치 4
    assert validate_email("user@example.com") is True
```

```ini
# .coveragerc: 커버리지 설정 파일
[run]
source = src
branch = True
omit =
    src/migrations/*
    src/settings.py

[report]
fail_under = 80     # 80% 미만이면 실패
show_missing = True

[html]
directory = htmlcov
```

## 변경 전후 비교

**Before: 커버리지 확인 없음**
```text
- 테스트가 통과하면 완료로 간주
- 예외 처리 코드가 한 번도 실행되지 않음
- 어떤 경로가 빠졌는지 알 수 없음
- 운영에서 예상치 못한 예외 발생
```

**After: 커버리지 기반 테스트 보완**
```text
- pytest --cov=src --cov-report=term-missing 실행
- 줄 번호로 미실행 코드 즉시 확인
- 브랜치 커버리지로 조건 분기 누락 발견
- CI에서 80% 미만이면 빌드 실패로 처리
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 커버리지를 100% 목표로 설정 | 의미 없는 테스트 양산 | 80% 기준, 중요 경로 집중 |
| 줄 커버리지만 측정 | 브랜치 누락을 감지 못함 | `--cov-branch` 추가 |
| 테스트 코드를 커버리지 대상에 포함 | 수치가 왜곡됨 | `omit`으로 테스트 파일 제외 |
| 커버리지 리포트를 읽지 않음 | 어느 줄이 빠졌는지 모름 | `term-missing`으로 줄 번호 확인 |
| CI에 커버리지 게이트 없음 | 커버리지가 점차 낮아짐 | `fail_under` 설정으로 최소 기준 강제 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"validate_email 함수에 대한 pytest 테스트를 작성해줘.
브랜치 커버리지 100%를 목표로,
빈 문자열, @ 없음, 도메인 없음 등 경계값을 모두 포함해줘"

# AI 결과물 검증 체크포인트:
# - 정상 경로 외에 예외/경계값 테스트가 있는가?
# - pytest --cov-branch를 실행해 브랜치 누락이 없는가?
# - .coveragerc에 fail_under가 설정되어 있는가?
# - 테스트 파일이 omit에 포함되어 있는가?
# - HTML 리포트로 시각적으로 확인했는가?
```

## 운영 체크리스트

- [ ] `pytest-cov`가 설치되어 있고 `--cov-branch`로 측정한다
- [ ] `--cov-report=term-missing`으로 미실행 줄 번호를 확인한다
- [ ] `.coveragerc`에 `fail_under = 80` (또는 팀 기준) 이 설정되어 있다
- [ ] 테스트 파일과 마이그레이션은 `omit`에서 제외되어 있다
- [ ] CI 파이프라인에서 커버리지 게이트가 동작한다

## 처음 질문으로 돌아가기

- **줄 커버리지와 브랜치 커버리지의 차이는?** 줄 커버리지는 해당 줄이 한 번이라도 실행됐는지 확인합니다. 브랜치 커버리지는 `if`문의 참/거짓 모두가 실행됐는지 확인합니다. 줄 커버리지 100%여도 `if` 조건이 항상 참이었다면 거짓 경로의 버그를 못 잡습니다.
- **커버리지 80% 기준은 어떻게 정할까요?** 절대적인 숫자는 없습니다. 신규 프로젝트는 80%, 운영 중인 레거시는 60%부터 시작하는 경우가 많습니다. 숫자보다 중요한 것은 핵심 비즈니스 로직의 커버리지입니다.
- **커버리지가 높으면 버그가 없는가?** 아닙니다. 커버리지는 코드가 실행됐다는 것만 확인합니다. 잘못된 기댓값으로 작성된 테스트는 커버리지를 올려도 버그를 잡지 못합니다. 커버리지는 테스트의 충분성 지표이지 정확성 지표가 아닙니다.

## 정리

바이브코딩에서 AI가 만들어 준 테스트에 `pytest --cov=src --cov-branch --cov-report=term-missing`을 실행해 어느 경로가 빠졌는지 확인하세요. 100%가 목표가 아니라, 빠진 곳을 아는 것이 목표입니다. CI에 커버리지 게이트를 걸어 기준이 점차 낮아지는 것을 막으세요. 다음 글에서는 CI와 GitHub Actions를 다룹니다.

## 참고 자료

- [pytest-cov — GitHub](https://github.com/pytest-dev/pytest-cov)
- [Coverage.py — Branch Coverage](https://coverage.readthedocs.io/en/latest/branch.html)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 pytest 기초 (1/10): pytest란 무엇인가?
- 바이브코딩을 위한 pytest 기초 (2/10): 첫 번째 테스트 작성
- 바이브코딩을 위한 pytest 기초 (3/10): assert와 예외 테스트
- 바이브코딩을 위한 pytest 기초 (4/10): 픽스처
- 바이브코딩을 위한 pytest 기초 (5/10): 파라미터화 테스트
- 바이브코딩을 위한 pytest 기초 (6/10): Mock과 패치
- 바이브코딩을 위한 pytest 기초 (7/10): 파일, 환경변수, 시간 테스트
- **바이브코딩을 위한 pytest 기초 (8/10): 커버리지 (현재 글)**
- 바이브코딩을 위한 pytest 기초 (9/10): CI와 GitHub Actions
- 바이브코딩을 위한 pytest 기초 (10/10): 테스트하기 좋은 코드
<!-- toc:end -->

Tags: 바이브코딩, pytest, Testing, Coverage, CI
