---
title: "AI 이미지 생성 101 (2/10): 좋은 프롬프트의 구조"
series: ai-image-gen-101
episode: 2
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
seo_description: "이미지 생성 프롬프트의 5가지 구성 요소와 조합 공식을 실제 예제로 알아봅니다."
---

# AI 이미지 생성 101 (2/10): 좋은 프롬프트의 구조

"이쁜 로봇 좌 그려줘." 결과는 나오는데 내가 상상한 것과는 다릅니다. "예쁜 풍경 그려줘." 풍경은 나오는데 어딘가 이상합니다. "멋있는 이미지 만들어줘." 멋있긴 한데 원한 게 이게 아닙니다.

이런 경험, 익숙하시죠? 문제는 프롬프트에 \"무엇을\" 넣었느냐가 아니라 \"어떻게\" 넣었느냐에 있습니다. \"예쁘다\", \"멋있다\", \"놀라운\" 같은 형용사는 AI에게 거의 정보를 주지 못합니다. AI는 구체적인 지시가 필요합니다.

이 글은 AI 이미지 생성 101 시리즈의 2번째 글입니다. 여기서는 좋은 프롬프트의 구체적인 구조를 배우고, 요소를 하나씩 추가하면서 결과가 어떻게 달라지는지 실험해 보겠습니다.

---

![AI 이미지 생성 101 (2/10): 좋은 프롬프트의 구조](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/02/02-01-ai-image-generation-101-2-10-the-structu.ko.png)
*프롬프트 구성 요소의 레이어링 구조*

## 먼저 던지는 질문

- 프롬프트에 요소를 하나씩 더할 때마다 이미지가 어떻게 달라질까요?
- "예쁜", "멋있는" 같은 형용사를 많이 넣으면 더 좋은 이미지가 나올까요?
- 프롬프트에서 요소의 순서가 결과에 영향을 줄까요?

---

## 프롬프트 공식: 레이어링 방식

좋은 프롬프트는 \"많이 쓰는 것\"이 아니라 \"정확하게 쓰는 것\"입니다. 핵심은 레이어링—요소를 하나씩 취하는 것입니다.

```
[주제] + [스타일] + [배경/장소] + [조명] + [구도/앙글]
```

이 공식을 로봇을 주제로 실험해 보겠습니다. 요소를 하나씩 추가하면서 이미지가 어떻게 변하는지 눈으로 확인합니다.

---

## 실험: 요소를 하나씩 쌓아보기

### 단계 1: 주제만

> a robot

![주제만 입력한 결과](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/02/01-subject-only.png)

*주제만 썼을 때: AI가 로봇의 형태, 색상, 배경, 분위기를 모두 임의로 결정한다.*

로봇은 나왔지만, 어떤 스타일인지, 어디에 있는지, 분위기가 어떤지 모두 AI 재량입니다.

### 단계 2: 주제 + 스타일

> a robot, watercolor painting style

![주제 + 스타일](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/02/02-subject-style.png)

*스타일을 추가하자 전체 분위기가 바뀌었다. 수채화 특유의 부드러움과 번짐 효과가 나타난다.*

스타일 하나만 추가했을 뿐인데, 같은 로봇이라도 완전히 다른 느낌의 이미지가 됩니다.

### 단계 3: 주제 + 스타일 + 배경

> a robot, watercolor painting style, standing in a flower garden

![주제 + 스타일 + 배경](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/02/03-subject-style-setting.png)

*배경을 지정하자 로봇이 화원에 놓였다. 이야기가 생긴다.*

주제에 장소를 주면 이미지에 이야기가 생깁니다. "로봇이 있다"에서 "로봇이 화원에 있다"로 바뀌면서 보는 사람이 궁금해하는 장면이 됩니다.

### 단계 4: 주제 + 스타일 + 배경 + 조명

> a robot, watercolor painting style, standing in a flower garden, golden hour sunlight casting long shadows

![주제 + 스타일 + 배경 + 조명](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/02/04-subject-style-setting-light.png)

*조명을 추가하자 화면 전체의 온도감이 달라졌다. 긴 그림자가 깊이감을 더한다.*

조명은 이미지의 분위기를 완전히 바꿀 수 있는 요소입니다. 같은 장면이라도 "낮", "밤", "네온 조명"에 따라 완전히 다른 이미지가 됩니다.

### 단계 5: 완성된 프롬프트 (5가지 요소 전체)

> a friendly robot with round eyes and a small antenna, watercolor painting style, standing in a flower garden surrounded by sunflowers and daisies, golden hour sunlight casting long soft shadows, gentle warm atmosphere, wide shot showing the full scene

![완성된 프롬프트](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/02/05-full-formula.png)

*5가지 요소를 모두 넣은 결과. 주제의 성격(친근한), 배경의 디테일(해바라기, 데이지), 구도(와이드샷)까지 지정.*

5가지 요소를 모두 넣으니 AI가 제 마음대로 결정할 여지가 거의 없어졌습니다. 내가 원하는 장면에 훨씬 가깝습니다.

---

## 흔한 실수: 븈 형용사 나열

많은 사람이 "더 좋은 결과를 얻으려면 칭찬을 많이 넣으면 되지 않을까?" 생각합니다. 실험해 보겠습니다.

> a beautiful amazing stunning incredible gorgeous wonderful fantastic robot in a nice pretty lovely amazing place with great lighting and awesome colors

![형용사 나열 프롬프트 결과](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/02/06-bad-adjectives.png)

*형용사를 여러 개 나열한 결과. 화려하지만 구체성이 없다.*

위의 단계 5 결과와 비교해 보세요. 형용사를 아무리 많이 넣어도 AI는 구체적인 지침으로 해석하지 못합니다. "놀라운"보다는 "둥글고 큰 눈을 가진", "예쁜 곳"보다는 "해바라기와 데이지가 있는 화원"이 훨씬 효과적입니다.

| 비효과적 | 효과적 |
|----------|---------|
| beautiful, amazing, stunning | 둥글고 큰 눈을 가진 |
| nice pretty lovely place | 해바라기와 데이지가 있는 화원 |
| great lighting | 골든아워 햇살이 긴 그림자를 만드는 |
| awesome colors | 따뜻한 주황색 톤 |

규칙은 간단합니다: **형용사보다 명사와 동사로 쓰세요.** "예쁜 고양이"보다 "털이 덮인 오렌지색 페르시안"이 AI에게 훨씬 명확한 지시입니다.

---

## 순서가 중요할까?

프롬프트에서 요소를 쓰는 순서가 결과에 영향을 줄까요? 같은 내용을 다른 순서로 주어 보겠습니다.

**배경 먼저**:

> In a dimly lit cyberpunk alley at night, a small delivery robot with glowing blue eyes navigates through puddles reflecting neon signs, cinematic photography style

**주제 먼저**:

> A small delivery robot with glowing blue eyes, cinematic photography style, navigating through puddles in a dimly lit cyberpunk alley at night, neon signs reflecting in the water

| 배경 먼저 | 주제 먼저 |
|:---:|:---:|
| ![배경 먼저 순서](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/02/07-order-setting-first.png) | ![주제 먼저 순서](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/02/08-order-subject-first.png) |

*같은 요소를 다른 순서로 썼을 때의 비교*

둘 다 비슷한 느낌이지만 미묘한 차이가 있습니다. 일반적으로 두 가지 패턴이 있습니다.

| 순서 | 특징 | 적합한 상황 |
|------|------|----------|
| 주제 먼저 | 주제가 화면 중심에 크게 | 제품 사진, 캐릭터 중심 |
| 배경 먼저 | 배경이 더 강조됨 | 풍경, 분위기 중심 |

실용적 팁: **가장 중요한 요소를 맨 앞에 쓰세요.** AI는 앞쪽에 나온 내용을 약간 더 강조하는 경향이 있습니다.

---

## 실전 템플릿 3가지

이제 공식을 알았으니, 실전에서 바로 쓸 수 있는 템플릿을 드립니다.

### 블로그 썸네일용

```
[Blog topic icon or metaphor], flat illustration style, 
clean white background, vibrant [brand color] accents, 
centered composition, soft even lighting
```

예: "A magnifying glass examining lines of code, flat illustration style, clean white background, vibrant blue and purple accents, centered composition, soft even lighting"

### SNS 포스트용

```
[Main subject doing action], [photography style], 
[specific location], [time of day] lighting, 
[angle] shot, [mood] atmosphere
```

예: "A person reading a book in a cozy window seat, lifestyle photography style, modern minimalist apartment, afternoon golden light, medium shot, peaceful calm atmosphere"

### 프레젤테이션 일러스트용

```
[Concept or process as visual metaphor], 
isometric illustration style, pastel color palette, 
clean minimal background, soft shadows, 
slightly above eye-level perspective
```

예: "A conveyor belt transforming raw materials into finished products as visual metaphor for data pipeline, isometric illustration style, pastel blue and mint color palette, clean minimal background, soft shadows"

---

## 정리: 프롬프트 구조의 핵심

오늘 배운 것을 정리하면:

1. **레이어링**: 주제 → 스타일 → 배경 → 조명 → 구도 순서로 쌓는다
2. **구체성**: 형용사 대신 명사와 동사로 쓴다
3. **순서**: 가장 중요한 요소를 앞에 둔다

다음 글에서는 5가지 요소 중 이미지의 전체 분위기를 가장 크게 바꾸는 "스타일"을 깊이 파고들겠습니다.

---

## 처음 질문으로 돌아가기

**프롬프트에 요소를 하나씩 더할 때마다 이미지가 어떻게 달라지나요?**

주제만 있을 때는 AI가 나머지를 전부 결정합니다. 스타일을 주면 분위기가, 배경을 주면 이야기가, 조명을 주면 온도감이, 구도를 주면 시선이 달라집니다.

**형용사를 많이 넣으면 더 좋은 이미지가 나올까요?**

아닙니다. "beautiful amazing stunning"은 AI에게 구체적 정보를 주지 못합니다. "둥글고 큰 눈을 가진" 같은 구체적 설명이 훨씬 효과적입니다.

**프롬프트에서 요소의 순서가 결과에 영향을 줄까요?**

약간의 영향은 있습니다. AI는 앞쪽 내용을 조금 더 강조하는 경향이 있어서, 가장 중요한 요소를 앞에 놓는 것이 좋습니다.

---

<!-- toc:begin -->
## 이 시리즈에서 다루는 글

- [AI 이미지 생성 101 (1/10): 첫 이미지 생성하기](./01-first-image-generation.md)
- **AI 이미지 생성 101 (2/10): 좋은 프롬프트의 구조 (현재 글)**
- AI 이미지 생성 101 (3/10): 스타일 마스터하기 (예정)
- AI 이미지 생성 101 (4/10): 구도와 시점 (예정)
- AI 이미지 생성 101 (5/10): 색감과 조명 (예정)
- AI 이미지 생성 101 (6/10): 복잡한 장면 설계하기 (예정)
- AI 이미지 생성 101 (7/10): 일관성 유지하기 (예정)
- AI 이미지 생성 101 (8/10): 텍스트와 타이포그래피 (예정)
- AI 이미지 생성 101 (9/10): 레퍼런스 이미지 활용 (예정)
- AI 이미지 생성 101 (10/10): 실전 워크플로우 (예정)
<!-- toc:end -->

## 참고 자료

- [OpenAI DALL-E 프롬프트 가이드](https://platform.openai.com/docs/guides/images)
- [god-tibo-imagen GitHub 저장소](https://github.com/NomaDamas/god-tibo-imagen)

Tags: AI, ChatGPT, 이미지 생성, 프롬프트 엔지니어링
