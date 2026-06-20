---
title: "바이브코딩을 위한 AI 이미지 생성 기초 (9/10): 레퍼런스 이미지 활용"
series: ai-image-gen-101
episode: 9
language: ko
last_reviewed: '2026-06-18'
status: draft
targets:
  wordpress: true
tags:
- AI
- ChatGPT
- "이미지 생성"
- "프롬프트 엔지니어링"
- "바이브코딩"
seo_description: "바이브코딩 프로젝트에서 기준 이미지를 만들고 계절·스타일·분위기를 변형하는 프롬프트 변주 기법. 앱 이미지를 시리즈로 만드는 방법."
---

# 바이브코딩을 위한 AI 이미지 생성 기초 (9/10): 레퍼런스 이미지 활용

> "히어로 이미지를 하나 만들었는데, 이 느낌 그대로 다크 모드 버전도 필요해."
>
> 기준 이미지 하나로 계절·스타일·분위기 변형본을 만드는 방법을 배웁니다.

바이브코딩으로 앱을 만들 때 하나의 이미지만 필요한 경우는 드뭅니다. 라이트/다크 모드, 계절 이벤트 버전, 다양한 SNS 플랫폼 포맷... 같은 브랜드 느낌을 유지하면서 여러 버전이 필요합니다. 기준 프롬프트 하나로 이 모든 변형을 만드는 방법이 있습니다.

---

## 이 글에서 다루는 5가지 질문

1. 기준 프롬프트를 유지하면서 분위기만 바꾸면 같은 브랜드로 인식되는가?
2. 스타일 변환 시 구도와 요소가 얼마나 유지되는가?
3. 바이브코딩 앱에서 자주 필요한 변형 유형은 무엇인가?
4. 한 번에 하나의 변형만 적용해야 하는 이유는?
5. 변형 프롬프트를 어떻게 코드처럼 관리하는가?

---

## 기준 장면 만들기

모든 변형의 출발점이 될 기준 프롬프트:

```
// 바이브코딩 앱 히어로 이미지 기준 프롬프트
BASE_SCENE = """
A person working on a laptop in a clean modern home office,
natural daylight from a large window,
minimalist desk with a plant,
photorealistic, wide shot, eye level
"""
```

이 기준 프롬프트의 앵커 요소와 변형 가능 요소:

| 요소 | 앵커 (고정) | 변형 가능 |
|------|-----------|---------|
| 공간 | 홈 오피스 + 큰 창문 | 고정 |
| 인물 | 노트북 작업 중 | 고정 |
| 조명 | 자연광 | 계절/시간에 따라 변경 |
| 분위기 | 미니멀 | 밝음/어두움 변경 가능 |
| 스타일 | photorealistic | 스타일 변환 가능 |

---

## Before / After: 변형 비교

### Before: 기준 없이 매번 새로 생성

> A modern workspace for a productivity app
>
> A dark workspace for dark mode
>
> A cozy workspace for winter

매번 다른 스타일, 구도, 분위기. 같은 앱의 이미지로 보이지 않습니다.

### After: 기준 프롬프트 + 변형 축

```
// 한 번에 하나의 변형 축만 교체
BASE_SCENE + "dark mode aesthetic, cool blue tones, minimal artificial light"
BASE_SCENE + "winter, warm golden light, snow visible outside window"
BASE_SCENE + "watercolor illustration style, soft washes"
```

| 요소 | Before | After |
|------|--------|-------|
| 브랜드 일관성 | 없음 | 같은 공간의 다른 버전 |
| 제작 시간 | 매번 처음부터 | 기준 복사 후 한 단어 교체 |
| 시리즈 느낌 | 없음 | 명확한 시리즈 연결 |

---

## 4가지 변형 축

### 변형 1: 다크/라이트 모드

바이브코딩에서 가장 자주 필요한 변형입니다.

```
// 라이트 모드
BASE_SCENE + "bright natural daylight, clean white tones, energetic atmosphere"

// 다크 모드
BASE_SCENE + "evening atmosphere, dark aesthetic, cool artificial lighting, focused mood"
```

### 변형 2: 계절 이벤트

앱의 시즌 이벤트나 마케팅 캠페인용:

| 계절 | 창밖 | 조명 | 소품 추가 |
|------|------|------|---------|
| 봄 | cherry blossom | bright natural | flowers on desk |
| 여름 | clear sunny sky | harsh bright | cold drink |
| 가을 | autumn leaves | warm amber | warm drink |
| 겨울 | snowy scene | cozy warm | hot cocoa |

```
// 계절 변형 공식
BASE_SCENE + [창밖 풍경 변경] + [조명 조정] + [계절 소품]
```

### 변형 3: 스타일 변환

앱의 다양한 콘텐츠 채널에 맞게:

| 원본 | 변환 | 교체 키워드 | 용도 |
|------|------|-----------|------|
| photorealistic | 플랫 일러스트 | `flat illustration style` | 블로그 썸네일 |
| photorealistic | 수채화 | `watercolor painting style` | 뉴스레터 |
| photorealistic | 애니메이션 | `anime illustration style` | SNS |
| photorealistic | 3D 렌더 | `3D render, clean studio` | 앱 스토어 |

### 변형 4: 분위기 전환

같은 공간에 반대되는 형용사 적용:

```
// 집중 모드
BASE_SCENE + "focused, minimal distractions, high contrast"

// 릴렉스 모드
BASE_SCENE + "relaxed, cozy, soft warm light, casual atmosphere"
```

---

## 자주 하는 실수

| 실수 | 예시 | 결과 | 해결책 |
|------|------|------|--------|
| 앵커 요소 변경 | 공간 자체를 바꿈 | 기준과 다른 장면 | 공간/구도 고정 |
| 여러 축 동시 변형 | 계절 + 스타일 + 분위기 동시 | 기준과 연결 끊김 | 한 번에 하나씩 |
| 기준 미확정 | 기준 없이 변형 시작 | 일관성 없는 시리즈 | 기준 먼저 확정 |
| 변형 프롬프트 미저장 | 성공한 변형 미저장 | 재현 불가 | 파일로 저장 |

---

## 바이브코딩 변형 프롬프트 관리

```
// 바이브코딩 이미지 변형 시스템
BASE_SCENE = "[기준 장면 프롬프트]"

// 모드 변형
LIGHT_MOD = "bright natural daylight, white clean tones"
DARK_MOD = "evening, cool artificial light, dark aesthetic"

// 계절 변형
SPRING_MOD = "cherry blossom outside, bright spring light"
WINTER_MOD = "snowy scene, cozy warm lighting"

// 스타일 변형
FLAT_STYLE = "flat illustration style, vector art"
PHOTO_STYLE = "photorealistic, DSLR quality"

// 사용법: BASE_SCENE + DARK_MOD + FLAT_STYLE
```

---

## 체크리스트

- [ ] 기준 프롬프트를 파일로 저장 (base-scene.txt)
- [ ] 앵커 요소 3가지 이상 명시
- [ ] 한 번에 하나의 변형 축만 변경
- [ ] 성공한 변형 프롬프트를 variants.txt에 저장
- [ ] 다크/라이트 모드 버전 둘 다 준비

---

## 처음 질문으로 돌아가기

**"히어로 이미지를 하나 만들었는데, 이 느낌 그대로 다크 모드 버전도 필요해."**

기준 프롬프트를 저장해두고 조명과 분위기 키워드만 "dark mode aesthetic, cool blue tones"로 교체하면 됩니다. 공간과 구도를 고정(앵커)하고 분위기만 바꾸면 같은 브랜드의 다른 버전으로 인식됩니다.

---

## 정리

- 기준 프롬프트를 앵커로 고정하면 시리즈 이미지를 일관되게 만들 수 있다
- 바이브코딩에서 자주 필요한 변형 축: 다크/라이트, 계절, 스타일, 분위기
- 한 번에 하나의 변형 축만 바꿔야 기준과의 연결이 유지된다
- 변형 프롬프트를 코드처럼 변수로 관리하면 재사용이 쉬워진다

---

## 참고 자료

- [OpenAI 이미지 생성 가이드](https://platform.openai.com/docs/guides/images)
- [Canva 무료 사용](https://www.canva.com)

<!-- toc:begin -->
## 이 시리즈에서 다루는 글

- [바이브코딩을 위한 AI 이미지 생성 기초 (1/10): 첫 이미지 생성하기](./01-first-image-generation.md)
- [바이브코딩을 위한 AI 이미지 생성 기초 (2/10): 좋은 프롬프트의 구조](./02-prompt-structure.md)
- [바이브코딩을 위한 AI 이미지 생성 기초 (3/10): 스타일 마스터하기](./03-mastering-styles.md)
- [바이브코딩을 위한 AI 이미지 생성 기초 (4/10): 구도와 시점](./04-composition-and-perspective.md)
- [바이브코딩을 위한 AI 이미지 생성 기초 (5/10): 색감과 조명](./05-color-and-lighting.md)
- [바이브코딩을 위한 AI 이미지 생성 기초 (6/10): 복잡한 장면 설계하기](./06-complex-scene-design.md)
- [바이브코딩을 위한 AI 이미지 생성 기초 (7/10): 일관성 유지하기](./07-consistency-across-images.md)
- [바이브코딩을 위한 AI 이미지 생성 기초 (8/10): 텍스트와 타이포그래피](./08-text-and-typography.md)
- **바이브코딩을 위한 AI 이미지 생성 기초 (9/10): 레퍼런스 이미지 활용 (현재 글)**
- 바이브코딩을 위한 AI 이미지 생성 기초 (10/10): 실전 워크플로우 (예정)
<!-- toc:end -->

Tags: AI, ChatGPT, 이미지 생성, 프롬프트 엔지니어링, 바이브코딩
