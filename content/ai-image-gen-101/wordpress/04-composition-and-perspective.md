---
title: "바이브코딩을 위한 AI 이미지 생성 기초 (4/10): 구도와 시점"
series: ai-image-gen-101
episode: 4
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
seo_description: "바이브코딩 프로젝트의 다양한 이미지 용도에 맞는 구도 키워드를 실험으로 배웁니다. 클로즈업부터 아이소메트릭까지."
---

# 바이브코딩을 위한 AI 이미지 생성 기초 (4/10): 구도와 시점

> "히어로 섹션 이미지는 와이드하게, 기능 아이콘은 정면으로, 팀 소개는 인물 클로즈업으로..."
>
> 용도마다 다른 구도가 필요합니다. 그 키워드를 지금 배웁니다.

바이브코딩으로 랜딩 페이지를 만들 때 섹션마다 필요한 이미지 유형이 다릅니다. 히어로는 넓고, 피처는 아이소메트릭, 팀 소개는 클로즈업. 이 구도를 AI에게 정확히 전달하는 방법을 배웁니다.

---

## 이 글에서 다루는 5가지 질문

1. 랜딩 페이지 각 섹션에 맞는 구도는 무엇인가?
2. 클로즈업과 와이드 샷의 차이는 무엇인가?
3. 아이소메트릭 뷰는 어떤 상황에 쓰는가?
4. 카메라 각도가 느낌을 어떻게 바꾸는가?
5. 구도와 각도를 조합하면 어떤 결과가 나오는가?

---

## 촬영 거리 4가지

| 거리 | 키워드 | 바이브코딩 용도 |
|------|--------|--------------|
| 익스트림 클로즈업 | `extreme close-up, macro` | 소재/텍스처 강조 |
| 클로즈업 | `close-up, portrait shot` | 인물 소개, 썸네일 |
| 미디엄 샷 | `medium shot, waist shot` | 기능 설명, 본문 |
| 와이드 샷 | `wide shot, establishing` | 히어로, 배너 |

## 카메라 각도 4가지

| 각도 | 키워드 | 바이브코딩 용도 |
|------|--------|--------------|
| 버드아이 | `bird's eye view, top-down` | 플랫레이, 인포그래픽 |
| 로우 앵글 | `low angle, worm's eye` | 위엄 있는 제품/인물 |
| 더치 앵글 | `Dutch angle, tilted` | 긴장감, 창의적 |
| 아이소메트릭 | `isometric view` | 앱 UI 목업, 다이어그램 |

---

## Before / After: 구도가 만드는 차이

### Before: 구도 미지정

> A smartphone showing a productivity app

AI가 임의로 구도를 결정합니다.

### After: 아이소메트릭 구도

> A smartphone showing a productivity app, **isometric 3D perspective**, clean white background, soft shadows, product visualization style

아이소메트릭 뷰로 앱 UI를 명확하게 보여주는 목업 이미지가 됩니다.

---

## 자주 하는 실수

| 실수 | 예시 | 문제 | 해결책 |
|------|------|------|--------|
| 구도 미지정 | 구도 키워드 없음 | AI가 임의 결정 | 반드시 거리 + 각도 지정 |
| 용도와 구도 불일치 | 히어로에 클로즈업 | 레이아웃에서 이상해 보임 | 섹션 용도에 맞는 구도 선택 |
| 구도 과잉 | "close-up wide-angle" | 모순된 요청 | 하나만 선택 |

---

## 바이브코딩 랜딩 페이지 섹션별 구도 가이드

| 섹션 | 추천 구도 | 키워드 |
|------|---------|--------|
| Hero | 와이드 샷 + 아이 레벨 | `wide establishing shot, eye level` |
| Features | 아이소메트릭 | `isometric view, clean composition` |
| Team | 클로즈업 + 아이 레벨 | `close-up portrait, eye level` |
| CTA | 클로즈업 + 약간 로우 앵글 | `close-up, slightly low angle` |
| Footer | 와이드 + 버드아이 | `wide shot, aerial perspective` |

---

## AI 팁: 구도 프리셋

```
// 바이브코딩 랜딩 페이지 구도 프리셋
HERO_SHOT = "wide establishing shot, eye level perspective"
FEATURE_SHOT = "isometric 3D view, clean white background"
TEAM_SHOT = "close-up portrait, eye level, professional"
PRODUCT_SHOT = "isometric product visualization, soft shadows"
```

---

## 체크리스트

- [ ] 프로젝트 각 섹션의 이미지 용도 정의
- [ ] 각 용도에 맞는 구도 키워드 선택
- [ ] 구도 프리셋 저장
- [ ] 동일한 섹션의 이미지들에 같은 구도 적용

---

## 처음 질문으로 돌아가기

**"히어로 섹션 이미지는 와이드하게, 기능 아이콘은 정면으로, 팀 소개는 인물 클로즈업으로..."**

각각 `wide establishing shot`, `isometric view`, `close-up portrait`를 쓰면 됩니다. 섹션별 구도 프리셋을 저장해두고 재사용하면 바이브코딩 흐름이 더 빨라집니다.

---

## 정리

- 구도(거리 + 각도)는 이미지가 전달하는 감정을 결정한다
- 바이브코딩 프로젝트의 각 섹션에는 최적의 구도가 있다
- 아이소메트릭 뷰는 앱 목업과 다이어그램에 특히 효과적이다
- 구도 프리셋을 만들어두면 일관성 있는 디자인을 유지할 수 있다

---

## 참고 자료

- [OpenAI 이미지 생성 가이드](https://platform.openai.com/docs/guides/images)
- [Photography Composition Techniques](https://digital-photography-school.com/composition/)

<!-- toc:begin -->
## 이 시리즈에서 다루는 글

- [바이브코딩을 위한 AI 이미지 생성 기초 (1/10): 첫 이미지 생성하기](./01-first-image-generation.md)
- [바이브코딩을 위한 AI 이미지 생성 기초 (2/10): 좋은 프롬프트의 구조](./02-prompt-structure.md)
- [바이브코딩을 위한 AI 이미지 생성 기초 (3/10): 스타일 마스터하기](./03-mastering-styles.md)
- **바이브코딩을 위한 AI 이미지 생성 기초 (4/10): 구도와 시점 (현재 글)**
- 바이브코딩을 위한 AI 이미지 생성 기초 (5/10): 색감과 조명 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (6/10): 복잡한 장면 설계하기 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (7/10): 일관성 유지하기 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (8/10): 텍스트와 타이포그래피 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (9/10): 레퍼런스 이미지 활용 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (10/10): 실전 워크플로우 (예정)
<!-- toc:end -->

Tags: AI, ChatGPT, 이미지 생성, 프롬프트 엔지니어링, 바이브코딩
