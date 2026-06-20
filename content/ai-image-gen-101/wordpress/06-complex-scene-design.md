---
title: "바이브코딩을 위한 AI 이미지 생성 기초 (6/10): 복잡한 장면 설계하기"
series: ai-image-gen-101
episode: 6
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
seo_description: "바이브코딩 프로젝트에서 여러 인물과 요소가 있는 복잡한 장면을 AI로 만드는 방법. 레이어 배치와 공간 분할 기법."
---

# 바이브코딩을 위한 AI 이미지 생성 기초 (6/10): 복잡한 장면 설계하기

> "팀 협업 장면을 보여주는 이미지가 필요한데, 세 명이 화이트보드 앞에서 토론하는 장면으로."
>
> 단순한 1인 장면을 넘어 복잡한 다인 장면을 만드는 방법을 배웁니다.

바이브코딩으로 만드는 랜딩 페이지의 팀 섹션, 사용자가 제품을 쓰는 모습, 여러 기능이 동시에 보이는 장면... 이런 복잡한 장면을 AI에게 요청할 때는 전략이 필요합니다.

---

## 이 글에서 다루는 5가지 질문

1. 여러 인물이 있는 장면을 어떻게 요청하는가?
2. AI가 복잡한 장면에서 자주 실패하는 이유는?
3. 전경/중경/배경 레이어는 어떻게 지정하는가?
4. 공간 분할로 비교 이미지를 만드는 방법은?
5. 복잡도 한계는 어디까지인가?

---

## 단계별 복잡도

| 단계 | 설명 | 안정성 |
|------|------|--------|
| 1인 | 한 명 + 단순 배경 | 매우 안정 |
| 2인 상호작용 | 두 명의 관계와 행동 명시 | 안정 |
| 다인 (3-6명) | 각각 다른 행동 부여 | 대체로 안정 |
| 다인 (7명+) | 그룹 단위 묘사 필요 | 불안정 |

---

## Before / After: 복잡한 장면 요청

### Before: 막연한 다인 장면

> Three people in a meeting

세 명이 겹치거나 같은 자세로 서있는 이상한 결과가 나옵니다.

### After: 구체적인 역할과 위치 지정

> Three people in a modern office conference room: on the left a woman in glasses presenting at a whiteboard, in the center a man taking notes on a laptop, on the right another woman listening and thinking, warm office lighting, wide shot, photorealistic

| 요소 | Before | After |
|------|--------|-------|
| 인물 구분 | 없음 | 각각 다른 외형/행동 |
| 위치 지정 | 없음 | left/center/right |
| 상호작용 | 없음 | 각각의 역할 명시 |
| 결과 | 이상한 배치 | 자연스러운 팀 장면 |

---

## 자주 하는 실수

| 실수 | 예시 | 문제 | 해결책 |
|------|------|------|--------|
| 위치 없이 다인 | "five people working" | 무작위 배치 | "on the left/center/right" 지정 |
| 인물 구분 없음 | "several people" | 모두 같아 보임 | 각 인물에게 외형/행동 부여 |
| 중심 구조물 없음 | 구조물 없이 많은 인물 | 혼란스러운 배치 | 테이블/보드 등 앵커 먼저 |
| 7명 이상 개별 묘사 | 10명 각각 상세 묘사 | AI가 혼란 | 그룹 단위로 묶어 묘사 |

---

## 레이어 배치 기법

깊이감이 있는 이미지를 만드는 레이어 구조:

```
[전경: 주요 요소 + sharp focus] +
[중경: 보조 요소 + slightly blurred] +
[배경: 환경 + soft bokeh] +
shallow depth of field
```

**바이브코딩 활용 예시**:
> In the foreground a smartphone with the app interface in sharp focus, in the midground a smiling user, background shows a modern cafe with soft bokeh, lifestyle photography

---

## 공간 분할: Before/After 비교 이미지

바이브코딩 랜딩 페이지에서 자주 쓰이는 Before/After 비교:

```
On the left side [이전 상태 + 어둡고 복잡한],
on the right side [이후 상태 + 밝고 깔끔한],
connected by a thin dividing line in the center,
product comparison visualization
```

---

## 복잡한 장면 프롬프트 공식

```
1. 중심 구조물 정의 (테이블, 보드, 무대)
2. 인물별 역할 + 행동 + 위치 (on the left/center/right)
3. 인물 간 관계
4. 분위기 + 조명
5. wide shot (필수)
```

---

## 체크리스트

- [ ] 중심 구조물(테이블, 화이트보드 등) 먼저 정의
- [ ] 각 인물에게 구분되는 역할과 행동 부여
- [ ] 공간 위치(left/center/right) 명시
- [ ] 인물 수가 6명 이상이면 그룹 단위로 묘사
- [ ] wide shot 키워드 추가

---

## 처음 질문으로 돌아가기

**"팀 협업 장면을 보여주는 이미지가 필요한데, 세 명이 화이트보드 앞에서 토론하는 장면으로."**

중심 구조물(화이트보드) + 각 인물의 위치와 행동(왼쪽에 발표자, 가운데 메모하는 사람, 오른쪽 듣는 사람) + wide shot으로 요청하면 됩니다.

---

## 정리

- 복잡한 장면은 중심 구조물을 앵커로 삼아 인물을 배치한다
- 각 인물에게 고유한 행동과 위치를 부여해야 AI가 제대로 배치한다
- 7명 이상은 그룹 단위로 묘사하거나 분할 생성한다
- 레이어 배치(전경/중경/배경)로 깊이감 있는 이미지를 만든다

---

## 참고 자료

- [OpenAI 이미지 생성 가이드](https://platform.openai.com/docs/guides/images)
- [god-tibo-imagen GitHub 저장소](https://github.com/NomaDamas/god-tibo-imagen)

<!-- toc:begin -->
## 이 시리즈에서 다루는 글

- [바이브코딩을 위한 AI 이미지 생성 기초 (1/10): 첫 이미지 생성하기](./01-first-image-generation.md)
- [바이브코딩을 위한 AI 이미지 생성 기초 (2/10): 좋은 프롬프트의 구조](./02-prompt-structure.md)
- [바이브코딩을 위한 AI 이미지 생성 기초 (3/10): 스타일 마스터하기](./03-mastering-styles.md)
- [바이브코딩을 위한 AI 이미지 생성 기초 (4/10): 구도와 시점](./04-composition-and-perspective.md)
- [바이브코딩을 위한 AI 이미지 생성 기초 (5/10): 색감과 조명](./05-color-and-lighting.md)
- **바이브코딩을 위한 AI 이미지 생성 기초 (6/10): 복잡한 장면 설계하기 (현재 글)**
- 바이브코딩을 위한 AI 이미지 생성 기초 (7/10): 일관성 유지하기 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (8/10): 텍스트와 타이포그래피 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (9/10): 레퍼런스 이미지 활용 (예정)
- 바이브코딩을 위한 AI 이미지 생성 기초 (10/10): 실전 워크플로우 (예정)
<!-- toc:end -->

Tags: AI, ChatGPT, 이미지 생성, 프롬프트 엔지니어링, 바이브코딩
