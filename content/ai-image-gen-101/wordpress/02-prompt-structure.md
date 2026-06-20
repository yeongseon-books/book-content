---
title: "바이브코딩을 위한 AI 이미지 생성 기초 (2/10): 좋은 프롬프트의 구조"
series: ai-image-gen-101
episode: 2
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
seo_description: "바이브코딩 프로젝트에서 AI 이미지 프롬프트를 체계적으로 작성하는 5요소 레이어링 공식을 실험으로 배웁니다."
---

# 바이브코딩을 위한 AI 이미지 생성 기초 (2/10): 좋은 프롬프트의 구조

> "예쁜 이미지 만들어줘."
>
> 이 요청이 왜 실패하는지, 그리고 어떻게 바꿔야 하는지를 지금 배웁니다.

바이브코딩에서 AI에게 "버튼 컴포넌트 만들어줘"가 아니라 "파란색 배경의 흰 글씨 버튼, hover 시 어두워지는 효과, border-radius 8px"처럼 구체적으로 요청할수록 원하는 결과를 얻는 것과 같습니다. 이미지도 마찬가지입니다.

이 글에서는 프롬프트를 요소별로 쌓아가는 **레이어링 방식**을 실험으로 배웁니다.

---

## 이 글에서 다루는 5가지 질문

1. 레이어링 방식이란 무엇인가?
2. 요소를 하나씩 추가할 때 이미지가 어떻게 달라지는가?
3. "예쁜, 멋있는" 같은 형용사는 왜 효과가 없는가?
4. 프롬프트에서 요소의 순서가 중요한가?
5. 바이브코딩 용도별 실전 템플릿은 무엇인가?

---

## 레이어링 공식

```
[주제] + [스타일] + [배경/장소] + [조명] + [구도/앵글]
```

이 공식을 로봇을 예시로 단계별로 실험합니다.

---

## Before / After: 레이어링 전후 비교

### Before: 주제만 (1단계)

> a robot

AI가 스타일, 배경, 분위기를 모두 임의로 결정합니다.

### After: 5가지 요소 모두 (5단계)

> a friendly robot with round eyes and a small antenna, watercolor painting style, standing in a flower garden surrounded by sunflowers and daisies, golden hour sunlight casting long soft shadows, gentle warm atmosphere, wide shot showing the full scene

| 단계 | 추가 요소 | 변화 |
|------|---------|------|
| 1단계 | 주제만 | AI가 전부 결정 |
| 2단계 | + 스타일 | 전체 분위기 결정 |
| 3단계 | + 배경 | 이야기 생성 |
| 4단계 | + 조명 | 온도감 추가 |
| 5단계 | + 구도 | 시선 유도 |

---

## 자주 하는 실수: 빈 형용사 나열

많은 분이 "더 좋은 이미지를 얻으려면 좋은 말을 많이 해야 한다"고 생각합니다. 실제로는 반대입니다.

| 비효과적 (형용사) | 효과적 (명사/동사) |
|----------------|----------------|
| beautiful, amazing, stunning | 둥글고 큰 눈을 가진 |
| nice lovely place | 해바라기와 데이지가 있는 화원 |
| great lighting | 골든아워 햇살, 긴 그림자 |
| awesome colors | 따뜻한 주황색 톤 |

**규칙**: 형용사보다 명사와 동사로 구체적으로 쓰세요.

---

## 바이브코딩 용도별 실전 템플릿

### 랜딩 페이지 히어로 이미지

```
[제품/서비스의 핵심 시각적 메타포],
flat illustration style, vibrant [브랜드 색상],
centered composition, clean white background,
professional product illustration
```

### 기능 소개 아이콘

```
a set of 4 consistent [기능 주제] icons in a 2x2 grid,
same flat vector illustration style,
consistent [색상] color palette, white background,
clean geometric shapes, minimal design
```

### 블로그 썸네일

```
[주제의 시각적 메타포],
flat illustration style, clean background,
[브랜드 색상] accents, centered composition,
blog thumbnail format
```

### SNS 포스트

```
[주제 + 행동], lifestyle photography style,
[장소], [시간대] lighting, medium shot,
[분위기] atmosphere
```

---

## AI 팁: 프롬프트 디버깅

바이브코딩에서 코드가 예상대로 동작하지 않으면 디버깅하듯, 프롬프트도 디버깅할 수 있습니다.

| 문제 증상 | 원인 추측 | 수정 방향 |
|---------|---------|---------|
| 배경이 이상함 | 배경 지정 부족 | 배경을 더 구체적으로 |
| 분위기가 차가움 | 조명/색온도 미지정 | warm tones, golden hour 추가 |
| 주인공이 작음 | 구도 미지정 | close-up, portrait shot 추가 |
| 스타일이 다름 | 스타일 미지정 또는 충돌 | 하나의 스타일만 명시 |

---

## 체크리스트

- [ ] 레이어링 공식(주제→스타일→배경→조명→구도) 이해
- [ ] 로봇 예시를 5단계로 직접 실험
- [ ] 형용사 나열 프롬프트와 구체적 프롬프트 비교
- [ ] 내 프로젝트에 맞는 템플릿 하나 저장

---

## 처음 질문으로 돌아가기

**"예쁜 이미지 만들어줘."**

"예쁜"이라는 형용사 대신 "무엇이, 어디에, 어떤 스타일로, 어떤 빛 아래"를 명시하면 됩니다. 5요소 레이어링 공식이 이 과정을 체계화해줍니다.

---

## 정리

- 레이어링은 주제 → 스타일 → 배경 → 조명 → 구도 순서로 요소를 쌓는 것
- 형용사(예쁜, 멋있는)보다 명사와 동사가 훨씬 효과적
- 가장 중요한 요소를 프롬프트 앞에 놓으면 AI가 더 강조함
- 바이브코딩 용도별 템플릿을 저장해두면 재사용 가능

---

## 참고 자료

- [OpenAI DALL-E 프롬프트 가이드](https://platform.openai.com/docs/guides/images)
- [god-tibo-imagen GitHub 저장소](https://github.com/NomaDamas/god-tibo-imagen)

<!-- toc:begin -->
## 이 시리즈에서 다루는 글

- [바이브코딩을 위한 AI 이미지 생성 기초 (1/10): 첫 이미지 생성하기](./01-first-image-generation.md)
- **바이브코딩을 위한 AI 이미지 생성 기초 (2/10): 좋은 프롬프트의 구조 (현재 글)**
- 바이브코딩을 위한 AI 이미지 생성 기초 (3/10): 스타일 마스터하기 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (4/10): 구도와 시점 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (5/10): 색감과 조명 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (6/10): 복잡한 장면 설계하기 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (7/10): 일관성 유지하기 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (8/10): 텍스트와 타이포그래피 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (9/10): 레퍼런스 이미지 활용 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (10/10): 실전 워크플로우 (예정)
<!-- toc:end -->

Tags: AI, ChatGPT, 이미지 생성, 프롬프트 엔지니어링, 바이브코딩
