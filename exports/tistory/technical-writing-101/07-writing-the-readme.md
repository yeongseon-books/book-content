
# README 작성하기

> 기술 글쓰기 101 시리즈 (7/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *처음 본 사람* 이 *README* 만 보고 *5분* 안에 *실행* 할 수 있나요?

> *입구* 가 *친절* 해야 *집* 도 *친절* 해 보입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *5요소* 구조
- *Quick Start* 작성
- *배지* 사용
- *FAQ* 추가
- *라이선스* 명시

## 왜 중요한가

*README* 가 *프로젝트* 의 *첫 인상* 입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    W[What] --> Y[Why]
    Y --> H[How]
    H --> D[Demo]
    D --> L[License]
```

## 핵심 용어 정리

- **What**: *무엇* 인가.
- **Why**: *왜* 만들었나.
- **How**: *어떻게* 쓰나.
- **Demo**: *동작* 증거.
- **License**: *법적* 사용 조건.

## Before/After

**Before**: "*Hello* 라는 *Python 패키지*."

**After**: *5요소* 가 모두 있는 *README*.

## 실습: README 5요소

### 1단계 — What

```markdown
# greeter
간단한 인사말 라이브러리.
```

### 2단계 — Why

```markdown
## Why
다국어 인사말을 한 줄로 만들고 싶어 만들었습니다.
```

### 3단계 — How

```bash
pip install greeter
python3 -c "from greeter import hello; print(hello('ko'))"
```

### 4단계 — Demo

```text
안녕하세요!
```

### 5단계 — License

```markdown
## License
MIT
```

## 이 코드에서 주목할 점

- *5요소* 가 모두 있다.
- *명령* 이 *복사* 가능.
- *결과* 가 *보인다*.

## 자주 하는 실수 5가지

1. ***Why* 가 *없다*.**
2. ***Quick Start* 가 *길다*.**
3. ***Demo* 결과가 *없다*.**
4. ***라이선스* 가 *없다*.**
5. ***스크린샷* 이 *없다*.**

## 실무에서는 이렇게 쓰입니다

깃허브 추세 1위 프로젝트들도 거의 동일한 *5요소* 패턴을 씁니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *5분* 안에 *실행* 가능.
- *Why* 한 줄.
- *명령* 은 *그대로* 동작.
- *라이선스* 는 *명시*.
- *스크린샷* 은 *최소 1장*.

## 체크리스트

- [ ] *5요소* 모두.
- [ ] *Quick Start* 5줄 이하.
- [ ] *데모 결과* 표시.
- [ ] *라이선스* 명시.

## 연습 문제

1. *What* 의 정의 한 줄.
2. *Demo* 의 의미 한 줄.
3. *License* 의 예 한 줄.

## 정리 및 다음 단계

다음 글은 *튜토리얼 작성하기* 입니다.

- [기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- [독자 정의하기](./02-defining-the-reader.md)
- [제목과 구조 잡기](./03-title-and-structure.md)
- [개념 설명하기](./04-explaining-concepts.md)
- [예제 코드 설명하기](./05-explaining-example-code.md)
- [그림과 표 사용하기](./06-using-figures-and-tables.md)
- **README 작성하기 (현재 글)**
- 튜토리얼 작성하기 (예정)
- 블로그와 문서 차이 (예정)
- 발행 전 체크리스트 (예정)
## 참고 자료

- [Make a README - GitHub](https://www.makeareadme.com/)
- [Standard README - RichardLitt](https://github.com/RichardLitt/standard-readme)
- [Awesome README - matiassingers](https://github.com/matiassingers/awesome-readme)
- [Choose a License](https://choosealicense.com/)

Tags: TechnicalWriting, README, OpenSource, Documentation, Beginner

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
