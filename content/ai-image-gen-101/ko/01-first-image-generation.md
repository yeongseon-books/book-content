---
title: "AI 이미지 생성 101 (1/10): 첫 이미지 생성하기"
series: ai-image-gen-101
episode: 1
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
seo_description: "ChatGPT로 이미지를 만들어 보고 싶은데 어디서부터 시작해야 할지 모르겠다면, 여기서 시작하세요."
---

# AI 이미지 생성 101 (1/10): 첫 이미지 생성하기

블로그 썸네일이 필요한데 디자이너에게 의뢰할 예산이 없습니다. SNS에 올릴 이미지가 필요한데 스톡 사진으로는 분위기가 안 나옵니다. 프레젠테이션에 넣을 일러스트가 필요한데 무료 이미지 사이트에서는 딱 맞는 걸 찾기 어렵습니다.

ChatGPT의 이미지 생성 기능은 이런 순간에 쓸 수 있는 도구입니다. 텍스트로 원하는 이미지를 설명하면, AI가 그 설명에 맞는 이미지를 만들어 줍니다. 다만 같은 도구라도 어떻게 설명하느냐에 따라 결과가 크게 달라집니다.

이 글은 AI 이미지 생성 101 시리즈의 첫 번째 글입니다. 여기서는 ChatGPT로 첫 이미지를 만들어보고, 프롬프트를 조금만 바꿀 때 결과가 어떻게 달라지는지 직접 비교해 보겠습니다.

---

![AI 이미지 생성 101 (1/10): 첫 이미지 생성하기](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/01-01-ai-image-generation-101-1-10-creating-yo.ko.png)
*프롬프트 작성부터 결과 확인까지의 이미지 생성 흐름*

## 먼저 던지는 질문

- ChatGPT에게 이미지를 그려달라고 할 때, 어디까지 자세하게 써야 원하는 결과가 나올까요?
- "고양이 그려줘"라고 하면 어떤 고양이가 나올까요? 내가 상상한 고양이와 같을까요?
- 프롬프트를 바꿀 때마다 결과가 달라지는데, 어떤 요소가 가장 큰 영향을 줄까요?

---

## ChatGPT 이미지 생성이란?

ChatGPT의 이미지 생성 기능은 텍스트 설명을 받아 이미지를 만들어내는 AI 기술입니다. 전문 디자인 도구를 다룰 줄 몰라도, 한국어나 영어로 원하는 장면을 설명하면 됩니다.

이 기능을 쓰는 방법은 두 가지입니다.

| 방법 | 설명 | 적합한 사람 |
|------|------|------------|
| ChatGPT 웹/앱 | 대화창에서 바로 요청 | 모든 사람 |
| 오픈소스 도구 (god-tibo-imagen) | 코드로 자동화 | 반복 작업이 많은 사람 |

이 시리즈에서는 두 방법 모두 다룹니다. 프롬프트 작성법 자체는 동일하고, 도구만 다를 뿐이니까요.

---

## 첫 번째 실험: 단순한 프롬프트 vs 자세한 프롬프트

같은 주제로 두 번 이미지를 만들어 보겠습니다.

### 실험 1: 고양이

**프롬프트 A** (2단어):

> a cat

**프롬프트 B** (상세 설명):

> A fluffy orange tabby cat sitting on a windowsill at golden hour, soft warm sunlight streaming through the window, bokeh background of a cozy living room, photorealistic style, shallow depth of field

결과를 비교해 보세요.

| 프롬프트 A: "a cat" | 프롬프트 B: 상세 설명 |
|:---:|:---:|
| ![a cat 프롬프트 결과](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/01-simple-prompt.png) | ![상세 고양이 프롬프트 결과](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/02-detailed-prompt.png) |

*왼쪽: AI가 임의로 결정한 고양이. 오른쪽: 프롬프트에서 지정한 대로 오렌지 털 고양이, 창가, 골든아워 조명.*

여기서 중요한 차이가 보입니다. "a cat"만 썼을 때 AI는 고양이의 종류, 색상, 포즈, 배경, 조명을 모두 임의로 결정합니다. 주사위를 던져서 나온 결과와 같습니다. 반면 상세 프롬프트는 원하는 결과에 훨씬 가까워집니다.

### 실험 2: 산

**프롬프트 A** (2단어):

> a mountain

**프롬프트 B** (상세 설명):

> A snow-capped mountain peak at sunrise, dramatic pink and orange clouds reflecting in a crystal-clear alpine lake in the foreground, pine trees framing the edges, landscape photography style, wide-angle lens

| 프롬프트 A: "a mountain" | 프롬프트 B: 상세 설명 |
|:---:|:---:|
| ![a mountain 프롬프트 결과](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/03-vague-landscape.png) | ![상세 산 프롬프트 결과](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/04-detailed-landscape.png) |

*왼쪽: AI가 임의로 그린 산. 오른쪽: 일출, 호수 반영, 소나무 프레이밍을 지정한 결과.*

패턴이 보이시나요? 단순한 프롬프트는 AI에게 거의 모든 결정을 맡기는 것이고, 상세한 프롬프트는 내가 원하는 방향으로 AI를 안내하는 것입니다.

---

## 프롬프트의 기본 요소 5가지

상세한 프롬프트가 더 좋은 결과를 낸다는 걸 확인했습니다. 그럼 프롬프트에 어떤 요소를 넣어야 할까요?

| 요소 | 설명 | 예시 |
|------|------|------|
| **주제** (Subject) | 무엇을 그릴지 | 오렌지색 털 고양이 |
| **스타일** (Style) | 어떤 분위기로 그릴지 | 사진처럼, 수채화처럼 |
| **구도** (Composition) | 어떤 각도에서 볼지 | 클로즈업, 위에서 내려다보는 시점 |
| **조명** (Lighting) | 빛이 어떻게 들어오는지 | 따뜻한 오후 햇살, 네온 조명 |
| **배경** (Background) | 주제 뒤에 뭔가 있는지 | 아늘한 거실, 도심 야경 |

이 다섯 요소를 모두 넣을 필요는 없습니다. 주제만으로도 이미지는 나옵니다. 하지만 요소를 더할수록 원하는 결과에 가까워집니다.

### 실험 3: 커피 한 잔

이번에는 요소를 하나씩 추가하면서 차이를 봐보겠습니다.

**프롬프트 A** (주제만):

> a coffee cup on a table

**프롬프트 B** (5가지 요소 모두 포함):

> A steaming latte with beautiful latte art in a ceramic cup, sitting on a rustic wooden table in a cozy cafe, morning light coming through the window, warm tones, overhead shot, food photography style

| 주제만 | 5가지 요소 모두 |
|:---:|:---:|
| ![커피 기본 프롬프트](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/05-coffee-basic.png) | ![커피 상세 프롬프트](https://yeongseon-books.github.io/book-public-assets/assets/ai-image-gen-101/01/06-coffee-detailed.png) |

*왼쪽: 주제만 지정. 오른쪽: 스타일(푸드 포토), 구도(오버헤드), 조명(아침 자연광), 배경(카페)을 모두 지정.*

오른쪽 이미지는 인스타그램이나 블로그에 바로 올릴 수 있는 수준입니다. 프롬프트에 30초만 더 투자했을 뿐인데 결과의 차이는 큽니다.

---

## 프롬프트 작성 팁 3가지

첫 이미지를 만들어보면서 느낀 점을 정리하면 이렇습니다.

### 1. 구체적으로 쓰세요

"예쁜 꽃"보다 "분홍색 벚꽃이 흩날리는 봄날의 가로수길"이 낫습니다. AI는 우리 머릿속 이미지를 볼 수 없으니까, 문자로 전달할 수 있는 만큼만 이해합니다.

구체성을 높이는 방법:
- **색상**: "꽃"이 아니라 "분홍색 벚꽃"
- **수량**: "사람들"이 아니라 "세 명의 사람"
- **행동**: "앉아 있는"이 아니라 "무릎을 꿇고 책을 읽고 있는"
- **상태**: "오래된"이 아니라 "이끼가 낀 풍화된 돌로 만들어진"

### 2. 스타일을 명시하세요

"사진처럼", "수채화처럼", "픽사 애니메이션 스타일로" 같은 표현을 넣으면 AI가 전체 분위기를 결정하는 데 큰 도움이 됩니다.

자주 쓰이는 스타일 키워드:

| 카테고리 | 키워드 예시 |
|----------|------------|
| 사진 계열 | photorealistic, DSLR photography, film grain |
| 회화 계열 | watercolor, oil painting, pencil sketch |
| 디지털 계열 | flat vector, 3D render, pixel art |
| 애니메이션 계열 | anime style, Studio Ghibli, Pixar |
| 분위기 계열 | cinematic, editorial, documentary |

### 3. 한 번에 완벽할 필요 없습니다

첫 결과가 마음에 안 들면, 프롬프트를 수정해서 다시 만들면 됩니다. 이미지 생성은 반복적인 과정이지, 한 번에 완성하는 과정이 아닙니다. "조금 더 밝게", "배경을 단순하게", "좀 더 왼쪽으로" 같은 수정 지시를 이어서 줄 수도 있습니다.

프롬프트 수정 예시:

| 상황 | 수정 방향 | 추가 키워드 |
|------|----------|------------|
| 색이 너무 어둡다 | 밝기 조정 | bright, well-lit, vibrant |
| 배경이 복잡하다 | 단순화 | clean background, minimal |
| 주인공이 작게 나왔다 | 구도 변경 | close-up, portrait shot |
| 분위기가 차갑다 | 색온도 변경 | warm tones, golden light |

---

## 자주 하는 실수

첫 이미지 생성에서 많은 사람이 겪는 실수들입니다.

| 실수 | 구체적 예시 | 해결책 |
|------|-----------|--------|
| 추상적 형용사 남발 | "beautiful amazing stunning cat" | "short-haired orange tabby cat" |
| 너무 많은 주제 동시 요청 | "고양이 + 강아지 + 토끼 + 새 + 물고기" | 주인공 하나에 집중 |
| 스타일 미지정 | 스타일 키워드 없음 | "photorealistic" 또는 원하는 스타일 추가 |
| 결과 한 번에 포기 | 첫 결과가 이상하다고 중단 | 프롬프트 수정 후 재시도 |
| 영어 vs 한국어 혼용 | 한국어와 영어 섞어서 사용 | 한 언어로 통일 (영어 권장) |

---

## Before & After: 프롬프트 개선 예시

### 예시 1: 홈 오피스

**Before (나쁜 프롬프트)**:
> 좋은 사무실 이미지

**After (개선된 프롬프트)**:
> A minimalist home office with a white wooden desk, a MacBook, a small succulent plant, a coffee mug, and a notebook. Morning sunlight streaming in through large windows, warm bright atmosphere, interior photography style, slightly above eye level

**차이**: Before는 AI에게 모든 것을 맡깁니다. After는 가구(흰 나무 책상), 소품(맥북, 다육이, 머그컵, 노트), 조명(아침 햇살), 스타일(인테리어 사진)을 모두 명시합니다.

### 예시 2: 음식 사진

**Before (나쁜 프롬프트)**:
> 맛있어 보이는 라면 사진

**After (개선된 프롬프트)**:
> A steaming bowl of Korean ramyeon with a rich red broth, topped with a perfectly soft-boiled egg cut in half, green onions, and dried seaweed, served in a traditional Korean ceramic bowl on a dark wooden table, food photography overhead shot, warm soft lighting

**차이**: Before는 "맛있어 보이는"이라는 주관적 형용사만 있습니다. After는 재료(반숙 계란, 파, 김), 그릇(한국 도자기), 배경(어두운 나무 테이블), 구도(오버헤드), 조명(따뜻한 소프트)을 모두 지정합니다.

---

## 프롬프트 구조 연습: 3단계 확장법

처음에는 간단하게 시작해서 조금씩 요소를 추가하는 방법을 연습해 보세요.

**1단계**: 주제만 (최소 프롬프트)
> A lighthouse

**2단계**: 주제 + 스타일 + 조명
> A lighthouse at dusk, photorealistic, golden sunset light

**3단계**: 주제 + 스타일 + 조명 + 구도 + 배경
> A tall white lighthouse on a rocky coastal cliff at dusk, photorealistic photography, dramatic golden sunset casting long shadows, wide establishing shot, turbulent waves crashing against the rocks below, overcast sky with breaks of warm light

이 3단계 확장법으로 연습하면 자연스럽게 풍부한 프롬프트를 작성하게 됩니다.

---

## 오픈소스 도구로 이미지 생성하기

이 시리즈의 예제 이미지는 모두 [god-tibo-imagen](https://github.com/NomaDamas/god-tibo-imagen)이라는 오픈소스 도구로 생성했습니다. 이 도구를 사용하면 ChatGPT의 이미지 생성 기능을 코드로 자동화할 수 있습니다.

```python
from gti import Client

client = Client()
result = client.generate_image(
    prompt="A fluffy orange tabby cat sitting on a windowsill at golden hour",
    output_path="my-cat.png"
)
print(f"이미지 저장 위치: {result.saved_path}")
```

이 도구가 있으면 같은 프롬프트로 여러 번 생성해보거나, 프롬프트를 조금씩 바꿀 때마다 결과를 비교하는 실험을 쉽게 할 수 있습니다. 이 시리즈 뒤쪽에서 자세히 다루겠습니다.

코드 없이 ChatGPT 웹사이트에서 동일한 프롬프트를 입력해도 같은 결과를 얻을 수 있습니다. 프롬프트 작성법이 핵심이지, 도구가 핵심이 아닙니다.

### ChatGPT 웹에서 이미지 생성하는 방법

1. ChatGPT Plus 또는 Team 플랜에 로그인합니다
2. 대화창에 이미지를 설명하는 프롬프트를 입력합니다
3. "이미지 생성해줘"라고 덧붙이거나, 이미지 생성 모드를 선택합니다
4. 생성된 이미지를 다운로드하거나 추가 수정을 요청합니다

무료 ChatGPT 사용자도 제한적으로 이미지 생성을 사용할 수 있습니다. 무료 한도가 부족하면 이 시리즈의 오픈소스 도구를 활용하는 방법을 참고하세요.

---

## 자주 묻는 질문

**Q: 한국어로 프롬프트를 써도 되나요?**

한국어로도 이미지가 생성되지만, 영어 프롬프트가 더 풍부하고 정확한 결과를 냅니다. AI 모델이 영어 데이터로 주로 훈련되었기 때문입니다. 익숙해질 때까지는 영어 프롬프트를 권장합니다.

**Q: 원하는 결과가 안 나올 때 어떻게 해야 하나요?**

두 가지 방향이 있습니다. 첫째, 프롬프트에 더 구체적인 정보를 추가합니다. 둘째, 원하지 않는 요소를 명시적으로 제외합니다 (예: "without text", "no people", "clear sky without clouds"). 보통 2-3번 수정하면 원하는 결과에 근접합니다.

**Q: 생성한 이미지를 상업적으로 사용해도 되나요?**

ChatGPT/DALL-E로 생성한 이미지의 사용 정책은 OpenAI 이용약관을 확인해야 합니다. 일반적으로 개인 사용과 많은 상업적 사용이 허용되지만, 정확한 범위는 약관을 참조하세요.

---

## 정리: 첫 이미지를 만들어보면서 배운 것

오늘 세 번의 실험을 통해 확인한 것은 간단합니다.

- 단순한 프롬프트는 AI에게 거의 모든 결정을 맡긴다
- 상세한 프롬프트는 내가 원하는 방향으로 안내한다
- 주제, 스타일, 구도, 조명, 배경의 5가지 요소가 결과를 좌우한다
- 처음부터 완벽할 필요 없다 — 수정하면서 개선해 나간다

다음 글에서는 이 5가지 요소 중 가장 영향력이 큰 "프롬프트 구조"를 더 깊이 파고들겠습니다.

---

## 처음 질문으로 돌아가기

**ChatGPT에게 이미지를 그려달라고 할 때, 어디까지 자세하게 써야 원하는 결과가 나올까요?**

주제, 스타일, 구도, 조명, 배경의 5가지 요소를 구체적으로 명시하면 원하는 결과에 가깝습니다. 모두 넣을 필요는 없지만, 많이 명시할수록 내 의도에 가까워집니다.

**"고양이 그려줘"라고 하면 어떤 고양이가 나올까요?**

AI가 임의로 결정한 고양이가 나옵니다. 종류, 색상, 포즈, 배경 모두 AI 재량입니다. 내가 상상한 고양이와 같을 확률은 낮습니다.

**프롬프트를 바꿀 때마다 결과가 달라지는데, 어떤 요소가 가장 큰 영향을 줄까요?**

스타일과 조명이 전체 분위기를 가장 크게 바꿉니다. 같은 고양이라도 "사진처럼"과 "수채화처럼"은 완전히 다른 이미지를 만들어냅니다. 스타일에 대해서는 3번째 글에서 자세히 다룹니다.

---

<!-- toc:begin -->
## 이 시리즈에서 다루는 글

- **AI 이미지 생성 101 (1/10): 첫 이미지 생성하기 (현재 글)**
- AI 이미지 생성 101 (2/10): 좋은 프롬프트의 구조 (예정)
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

- [ChatGPT 이미지 생성 공식 가이드](https://help.openai.com/en/articles/9055440-using-dall-e-and-browsing-in-chatgpt)
- [god-tibo-imagen GitHub 저장소](https://github.com/NomaDamas/god-tibo-imagen)

Tags: AI, ChatGPT, 이미지 생성, 프롬프트 엔지니어링
