---
title: "바이브코딩을 위한 Computer Science 기초 (9/10): 소프트웨어 엔지니어링"
series: computer-science-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - ComputerScience
  - SoftwareEngineering
  - Testing
  - Git
  - Refactoring
---

# 바이브코딩을 위한 Computer Science 기초 (9/10): 소프트웨어 엔지니어링

이 글은 "바이브코딩을 위한 Computer Science 기초" 시리즈의 9번째 글입니다.

---

바이브코딩에서 AI는 작동하는 코드를 빠르게 만들어 줍니다. 하지만 혼자 짠 스크립트가 한 번 잘 도는 것과, 여러 사람이 몇 년 동안 계속 바꿔도 버티는 시스템을 만드는 일은 다릅니다. 시간이 흐르고 사람이 바뀌는 동안에도 "여전히 잘 동작한다"를 보장하는 습관이 소프트웨어 엔지니어링입니다.

AI가 만들어 준 코드는 테스트 없이 빠르게 동작하지만, 변경이 생겼을 때 무엇이 깨졌는지 알 수 없습니다. 작동하는 코드를 짜는 능력만으로는 5년 차에 멈춥니다. 같은 코드도 6개월 후의 자신과 동료에게 친절해야 하고, 변경에 깨지지 않아야 합니다.

엔지니어링 습관 — 테스트, 리뷰, 작은 커밋, 명확한 이름 — 이 코딩과 엔지니어링의 차이를 만듭니다. 코드는 한 번 쓰지만 백 번 읽히고, 좋은 코드는 처음에 빨리 짜는 코드가 아니라 오래 고치기 쉬운 코드입니다.

테스트, 버전 관리, 코드 리뷰, 리팩터링 네 기둥을 중심으로 소프트웨어 엔지니어링의 기초를 정리합니다.

> **핵심 인사이트:** 엔지니어링은 "지금 동작" 위에 "내일도 동작"을 보장하는 활동입니다. 테스트가 없으면 변경이 두렵고, 두려운 변경은 기술 부채로 쌓입니다.

## 이 글에서 다룰 문제

- 코딩과 소프트웨어 엔지니어링의 차이는 어디에서 생길까요?
- 테스트는 왜 변경을 안전하게 만드는 최소 장치일까요?
- Git 기반 협업 흐름은 어떤 단위와 습관으로 유지될까요?
- 리팩터링과 기술 부채는 어떻게 관리해야 할까요?
- AI가 만든 코드에서 엔지니어링 관점으로 확인할 것은 무엇인가요?

## 소프트웨어 엔지니어링 핵심 패턴

```python
# 테스트: 변경을 안전하게 만드는 최소 장치
def add(a: int, b: int) -> int:
    return a + b

def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

# 명확한 이름과 단일 책임 (리팩터링 전/후)
# BAD: 무엇을 하는지 이름으로 알 수 없음
def process(x):
    return x * 1.1 if x > 0 else 0

# GOOD: 이름이 의도를 드러냄
def apply_tax(price: float, tax_rate: float = 0.1) -> float:
    if price <= 0:
        return 0.0
    return price * (1 + tax_rate)
```

```bash
# Git 협업 흐름
git checkout -b feature/add-payment-retry   # 기능 브랜치
git add -p                                   # 변경 단위별 스테이징
git commit -m "feat: add retry for payment API timeout"
git push origin feature/add-payment-retry
# PR 열기 → 코드 리뷰 → 머지
```

## 변경 전후 비교

**Before: 테스트 없는 코드**
```text
- 변경하면 무엇이 깨지는지 모름
- 기능 추가할 때마다 수동 테스트
- 거대한 함수에 모든 로직이 뒤섞임
- git commit -m "fix" (무엇을 고쳤는지 모름)
```

**After: 엔지니어링 습관 적용**
```text
- 단위 테스트로 회귀 자동 감지
- CI가 머지 전에 테스트 통과 확인
- 단일 책임 함수, 명확한 이름
- 의도를 담은 커밋 메시지 (feat/fix/refactor)
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 테스트 없이 "동작하면 됐다" | 변경할 때마다 수동 검증 반복 | 핵심 경로에 최소 단위 테스트 추가 |
| 거대한 커밋 ("fix everything") | 코드 리뷰 어렵고 롤백 범위 넓음 | 논리적 단위로 작은 커밋 분리 |
| main 직접 푸시 | 팀 코드베이스 불안정화 | 브랜치 + PR + 리뷰 흐름 |
| 리팩터링을 "나중에" | 기술 부채가 기하급수적으로 증가 | 작은 개선을 기능 개발에 포함 |
| 함수/변수 이름에 의미 없음 | 6개월 후 자신도 이해 못함 | 이름이 의도를 드러내도록 작성 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"이 함수에 대한 단위 테스트를 만들어줘.
경계값, 예외 케이스, 정상 케이스를 모두 포함해야 해.
pytest 스타일로 작성해줘"

# AI 코드 리뷰 체크포인트:
# - 함수가 하나의 일만 하는가 (단일 책임)
# - 이름이 의도를 드러내는가
# - 테스트 없이 변경하기 두려운 코드가 있는가
# - 중복 로직이 3번 이상 반복되는가 (함수로 추출)
# - 매직 넘버 없이 의미 있는 상수를 사용하는가
```

## 운영 체크리스트

- [ ] 핵심 비즈니스 로직에 단위 테스트가 있다
- [ ] CI가 머지 전에 테스트를 자동으로 실행한다
- [ ] 커밋 메시지가 변경 의도를 담고 있다
- [ ] 브랜치 + PR + 리뷰 흐름이 팀에 정착되어 있다
- [ ] 기술 부채 목록이 관리되고 있다

## 처음 질문으로 돌아가기

- **코딩과 소프트웨어 엔지니어링의 차이는?** 코딩은 "지금 동작"을 만들고, 엔지니어링은 "내일도 동작"을 보장하는 습관을 더합니다. 테스트, 리뷰, 명확한 이름이 그 차이를 만듭니다.
- **테스트가 변경을 안전하게 만드는 이유는?** 테스트가 있으면 변경 후 무엇이 깨졌는지 자동으로 알 수 있습니다. 테스트 없이는 변경이 두렵고, 두려운 변경은 기술 부채로 쌓입니다.
- **리팩터링을 "나중에" 하면 안 되는 이유는?** 기술 부채는 복리로 쌓입니다. 작은 개선을 기능 개발에 포함하는 습관이 장기적으로 속도를 유지합니다.

## 정리

바이브코딩에서 AI가 만들어 준 코드에 테스트를 추가하고, 거대 함수를 단일 책임 함수로 분리하고, 의미 있는 이름을 붙이는 작업이 엔지니어링 습관의 시작입니다. AI는 코드를 빠르게 만들어 주지만, 오래 유지되는 코드를 만드는 판단은 여전히 사람의 역할입니다. 다음 글에서는 AI와 데이터사이언스까지의 연결을 정리합니다.

## 참고 자료

- [The Pragmatic Programmer](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)
- [Refactoring — Martin Fowler](https://refactoring.com/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Computer Science 기초 (1/10): 컴퓨터 과학이란 무엇인가?
- 바이브코딩을 위한 Computer Science 기초 (2/10): 계산과 프로그램
- 바이브코딩을 위한 Computer Science 기초 (3/10): 데이터 표현
- 바이브코딩을 위한 Computer Science 기초 (4/10): 알고리즘과 복잡도
- 바이브코딩을 위한 Computer Science 기초 (5/10): 컴퓨터 구조
- 바이브코딩을 위한 Computer Science 기초 (6/10): 운영체제
- 바이브코딩을 위한 Computer Science 기초 (7/10): 네트워크
- 바이브코딩을 위한 Computer Science 기초 (8/10): 데이터베이스
- **바이브코딩을 위한 Computer Science 기초 (9/10): 소프트웨어 엔지니어링 (현재 글)**
- 바이브코딩을 위한 Computer Science 기초 (10/10): AI와 데이터사이언스까지의 연결
<!-- toc:end -->

Tags: 바이브코딩, ComputerScience, SoftwareEngineering, Testing, Git, Refactoring
