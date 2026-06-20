---
title: "AI 이미지 생성 101 (6/10): 복잡한 장면 설계하기"
series: ai-image-gen-101
episode: 6
language: ko
last_reviewed: '2026-06-18'
status: draft
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: false
tags:
- AI
- ChatGPT
- "이미지 생성"
- "프롬프트 엔지니어링"
seo_description: "여러 인물과 요소를 한 화면에 배치하는 복잡한 장면을 설계하는 프롬프트 기법을 실험합니다."
---

# AI 이미지 생성 101 (6/10): 복잡한 장면 설계하기

한 명을 그리는 건 쉽습니다. 하지만 "두 사람이 대화하는 장면"을 요청하면 두 사람이 겹치거나, 한 명이 사라지거나, 이상한 방향을 보고 있습니다. 여러 요소가 들어가는 장면일수록 AI가 임의로 결정하는 부분이 많아지고, 원하는 결과를 얻기 어려워집니다.

오늘은 단순한 1인 장면에서 시작해서 다인 장면, 레이어 배치, 공간 분할, 동작 상호작용까지 복잡도를 단계적으로 올려봅니다. 실패하는 패턴도 함께 보여드립니다.

이 글은 AI 이미지 생성 101 시리즈의 6번째 글입니다.

---

![AI 이미지 생성 101 (6/10): 복잡한 장면 설계하기](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/06-01-ai-image-generation-101-6-10-designing-c.ko.png)
*복잡한 장면의 단계별 접근*

## 먼저 던지는 질문

- 여러 인물을 배치할 때 AI가 가장 자주 실패하는 지점은 어디인가?
- 전경/중경/배경 레이어를 지정하면 무엇이 달라지는가?
- 복잡한 장면에서 혼란을 피하는 프롬프트 구조는 무엇인가?

---

## 1단계: 1인 장면 — 기준선

> A chef in a white coat standing alone in a modern kitchen, holding a knife, clean stainless steel counter, photorealistic, medium shot

![1인 장면](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/01-single-person.png)

*1인 장면: 주인공이 명확하고 배경이 단순. AI가 가장 잘 처리하는 난이도.*

한 명의 인물 + 단순한 배경은 AI가 가장 안정적으로 생성합니다. 이것이 기준선입니다.

---

## 2단계: 2인 상호작용

> A chef in a white coat teaching a young apprentice how to chop vegetables in a modern kitchen, both facing the cutting board, photorealistic, medium shot

![2인 장면](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/02-two-people.png)

*2인 장면: 두 사람의 관계와 행동을 명시하면 자연스러운 상호작용이 나온다.*

**핵심 기법**: 두 인물의 **관계**(선생-제자)와 **공통 행동**(도마를 향해 있음)을 지정했습니다.

**2인 장면 프롬프트 체크리스트**:
- 각 인물의 구분점 (의상, 나이, 역할)
- 관계 또는 상호작용 (가르치는, 대화하는, 건네주는)
- 시선/신체 방향 (둘 다 도마를 향해)
- 공간적 배치 (나란히, 마주보고, 뒤에서)

---

## 3단계: 다인 장면 (5명 이상)

> A busy restaurant kitchen with five chefs working at different stations, one grilling, one plating, one chopping, steam rising from pots, organized chaos, photorealistic, wide shot

![다인 장면](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/03-busy-kitchen.png)

*다인 장면: 각 인물에게 고유 행동을 부여하면 구분이 가능해진다.*

**핵심 기법**: 5명 각각에게 **고유한 동작**을 배정했습니다 (grilling, plating, chopping). "5명의 셰프"만 쓰면 전부 같은 자세로 서 있게 됩니다.

**다인 장면 원칙**:

| 원칙 | 나쁜 예 | 좋은 예 |
|------|--------|--------|
| 고유 행동 부여 | "다섯 명이 일하고 있다" | "한 명은 굽고, 한 명은 플레이팅, 한 명은 썰고" |
| 공간 분배 | "주방에 셰프들" | "각각 다른 스테이션에서" |
| 분위기 키워드 | (없음) | "organized chaos, steam rising" |

---

## 4단계: 전경/중경/배경 레이어 배치

> foreground shows a beautifully plated dish in sharp focus... midground shows a chef garnishing... background shows the rest of the kitchen team with soft bokeh

![레이어 배치](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/04-foreground-mid-back.png)

*레이어 배치: 전경(요리), 중경(셰프), 배경(팀)이 깊이감을 만든다. 초점 차이로 시선이 유도된다.*

**핵심 기법**: `foreground`, `midground`, `background`를 명시하고 각 레이어에 무엇이 있는지 지정했습니다. `shallow depth of field`를 추가하면 초점 차이로 깊이감이 생깁니다.

**레이어 프롬프트 구조**:

```
[전경: 대상 + sharp focus] + 
[중경: 대상 + slightly blurred] + 
[배경: 대상 + soft bokeh] + 
shallow depth of field
```

이 구조를 사용하면 단순히 "여러 요소가 있는 장면"이 아니라 시선이 유도되는 **깊이 있는 구도**가 됩니다.

---

## 5단계: 공간 분할

> on the left side a traditional wooden ramen stall with a Japanese chef, on the right side a modern fusion taco stand with a Mexican chef, both sides connected by a shared counter

![공간 분할](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/05-spatial-left-right.png)

*공간 분할: 좌/우를 명시적으로 나누면 AI가 대칭적 구성을 만든다.*

**핵심 기법**: `on the left side... on the right side...`로 공간을 명시적으로 분할했습니다. 비교 이미지, 전/후, 두 세계의 대비를 표현할 때 효과적입니다.

**공간 지정 키워드**:
- 좌/우: `on the left`, `on the right`, `left half`, `right half`
- 상/하: `top portion`, `bottom portion`, `upper half`, `lower half`
- 연결: `connected by`, `shared`, `between them`

---

## 6단계: 동작과 상호작용

> a chef tossing a flaming pan high in the air... a wide-eyed apprentice jumps back in surprise... another chef in the background calmly plates food

![동작 상호작용](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/06-action-interaction.png)

*동작 장면: 각 인물에게 서로 다른 반응을 부여하면 드라마가 만들어진다.*

**핵심 기법**: 같은 순간에 세 사람이 **서로 다른 반응**을 보이게 했습니다. 한 명은 행동(불 던지기), 한 명은 반응(놀라서 뒤로), 한 명은 무관심(묵묵히 작업). 이 대비가 드라마를 만듭니다.

---

## 실패 사례: 과도한 복잡도

> A confusing overcrowded scene with too many elements: ten different people doing ten different activities, dogs, cats, children...

![과도한 복잡도](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/07-bad-overcrowded.png)

*과도한 복잡도: 너무 많은 요소를 넣으면 AI가 혼란에 빠진다. 일부가 사라지거나 합쳐진다.*

**왜 실패하는가**: AI에게는 한 번에 처리할 수 있는 복잡도 한계가 있습니다. 10명 이상 + 동물 + 가구 + 소품을 동시에 요청하면 일부가 생략되거나 비정상적으로 합쳐집니다.

**복잡도 한계 가이드**:

| 요소 수 | 안정성 | 대처법 |
|---------|--------|--------|
| 1-3명 + 단순 배경 | 매우 안정 | 그대로 사용 |
| 4-6명 + 중간 배경 | 대체로 안정 | 각각에게 행동 부여 |
| 7명 이상 | 불안정 | 그룹으로 묶어 묘사 |
| 10+ 요소 동시 | 높은 실패율 | 분할 생성 후 합성 |

---

## 성공 사례: 정돈된 복잡한 장면

> A well-organized complex family dinner scene: a large rectangular table with eight family members of different ages, grandmother at the head serving roast turkey...

![정돈된 복잡한 장면](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/06/08-good-organized.png)

*정돈된 복잡한 장면: 중심 구조물(테이블)이 있고 각 인물의 위치와 행동이 명확하면 8명도 안정적이다.*

**왜 성공하는가**: 중심 구조물(큰 직사각형 테이블)이 배치의 앵커 역할을 합니다. 그리고 모든 인물이 이 구조물과의 관계로 정의됩니다(테이블 머리에 할머니, 빵을 집는 아이들, 와인을 따르는 부모).

---

## 복잡한 장면 프롬프트 공식

```
1. 중심 구조물/배경 정의 (테이블, 무대, 거리)
2. 인물별 역할 + 행동 + 위치
3. 인물 간 관계/상호작용
4. 분위기/조명
5. 구도 (wide shot 필수)
```

**핵심 원칙**:
- 중심 구조물을 먼저 놓고 인물을 그 위에 배치한다
- 각 인물에게 구분 가능한 특징과 행동을 준다
- 7명 넘어가면 그룹 단위로 묘사한다
- `wide shot`을 써서 모든 요소가 보이게 한다

---

## 정리

복잡한 장면을 단계적으로 쌓아올리면서 확인한 것:

- 1→2인은 관계와 상호작용을 명시하면 된다
- 다인 장면은 각 인물에게 고유한 행동을 부여해야 한다
- 전경/중경/배경 레이어를 지정하면 깊이감이 생긴다
- 과도한 요소는 실패를 부르므로, 중심 구조물 + 관계 기반 배치가 안전하다

다음 글에서는 일관성 유지하기—같은 캐릭터를 여러 이미지에 걸쳐 반복 생성하는 방법을 다룹니다.

---

## 처음 질문으로 돌아가기

**여러 인물을 배치할 때 AI가 가장 자주 실패하는 지점은?**

7명 이상을 구체적 행동 없이 배치하면 인물이 합쳐지거나 사라집니다. 해결책은 각 인물에게 고유한 행동과 위치를 지정하고, 중심 구조물(테이블, 카운터)을 앵커로 사용하는 것입니다.

**전경/중경/배경 레이어를 지정하면 무엇이 달라지는가?**

단순히 "여러 요소가 있는 장면"에서 "시선이 유도되는 깊이 있는 구도"로 바뀝니다. AI가 초점 차이를 적용해서 가장 중요한 요소에 시선이 가게 됩니다.

**복잡한 장면에서 혼란을 피하는 프롬프트 구조는?**

중심 구조물 정의 → 인물별 역할/행동/위치 → 관계/상호작용 → 분위기 → 구도 순서입니다. 모든 인물이 구조물과의 관계로 정의되면 AI가 배치를 결정하기 쉬워집니다.

---

<!-- toc:begin -->
## 이 시리즈에서 다루는 글

- [AI 이미지 생성 101 (1/10): 첫 이미지 생성하기](./01-first-image-generation.md)
- [AI 이미지 생성 101 (2/10): 좋은 프롬프트의 구조](./02-prompt-structure.md)
- [AI 이미지 생성 101 (3/10): 스타일 마스터하기](./03-mastering-styles.md)
- [AI 이미지 생성 101 (4/10): 구도와 시점](./04-composition-and-perspective.md)
- [AI 이미지 생성 101 (5/10): 색감과 조명](./05-color-and-lighting.md)
- **AI 이미지 생성 101 (6/10): 복잡한 장면 설계하기 (현재 글)**
- AI 이미지 생성 101 (7/10): 일관성 유지하기 (예정)
- AI 이미지 생성 101 (8/10): 텍스트와 타이포그래피 (예정)
- AI 이미지 생성 101 (9/10): 레퍼런스 이미지 활용 (예정)
- AI 이미지 생성 101 (10/10): 실전 워크플로우 (예정)
<!-- toc:end -->

## 참고 자료

- [OpenAI 이미지 생성 가이드](https://platform.openai.com/docs/guides/images)
- [god-tibo-imagen GitHub 저장소](https://github.com/NomaDamas/god-tibo-imagen)

Tags: AI, ChatGPT, 이미지 생성, 프롬프트 엔지니어링
