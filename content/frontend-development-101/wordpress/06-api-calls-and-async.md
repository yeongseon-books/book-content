---
series: frontend-development-101
episode: 6
title: "바이브코딩을 위한 프론트엔드 개발 기초 (6/10): API 호출과 비동기"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Frontend
  - API
  - Async
  - Fetch
  - JavaScript
seo_description: fetch와 async 흐름, 로딩과 에러 상태를 프론트엔드 관점에서 정리합니다. 바이브코딩에서 AI 생성 비동기 코드를 검토하고 안정성을 높이는 방법을 익힙니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 프론트엔드 개발 기초 (6/10): API 호출과 비동기

이 글은 **바이브코딩을 위한 프론트엔드 개발 기초** 시리즈의 여섯 번째 글입니다. AI에게 서버 데이터를 불러오는 코드를 만들어 달라고 할 때, 비동기 흐름과 상태 관리를 이해해야 로딩·에러 문제를 스스로 해결할 수 있습니다.

AI가 생성한 `fetch` 코드는 종종 로딩 상태나 에러 처리가 빠져 있습니다. 데이터를 받아오는 기본 흐름은 작동하지만, 네트워크가 느리거나 서버가 오류를 반환할 때 사용자는 빈 화면이나 멈춘 앱을 만납니다. 바이브코딩으로 만든 앱이 실제로 동작하려면 이 세 가지 상태를 모두 다뤄야 합니다.

> 프론트의 비동기 코드는 거의 항상 세 가지 상태를 동시에 관리합니다 — loading / data / error. 이 셋을 명시적으로 모델링하지 않으면 'fetch 한 번 했는데 UI가 깜빡거리는 / 실패가 안 보이는' 버그가 끝없이 재생산됩니다.

## 이 글에서 다룰 문제

- `fetch`와 `async/await`는 어떤 최소 패턴으로 시작하면 될까요?
- 로딩 상태와 에러 상태를 왜 반드시 화면에 드러내야 할까요?
- 컴포넌트가 사라질 때 요청 취소가 왜 필요할까요?
- AI가 생성한 비동기 코드에서 자주 빠지는 부분은 무엇일까요?
- 경쟁 상태(race condition)를 방지하는 방법은 무엇일까요?

## 바이브코딩 관점에서 시작하기

"AI야, 사용자 목록을 API에서 받아와서 화면에 보여줘"라고 요청하면 `fetch` 코드가 나옵니다. 하지만 로딩 중 빈 화면, 오류 시 아무 메시지도 없는 상태, 화면 이동 시 이전 요청이 완료되어 덮어쓰는 버그 등이 생길 수 있습니다. 이런 문제를 AI에게 구체적으로 요청하려면 비동기 상태 모델을 알아야 합니다.

## 개념 한눈에 보기

| 용어 | 뜻 | 바이브코딩에서 왜 중요한가 |
|---|---|---|
| `fetch` | 브라우저에 기본 내장된 HTTP 클라이언트입니다. | AI 생성 코드에서 가장 자주 보이는 API 호출 방법입니다. |
| Promise | 미래에 도착할 값을 표현하는 객체입니다. | async/await 코드가 왜 그렇게 생겼는지 이해하는 기반입니다. |
| `async/await` | Promise를 동기 코드처럼 읽게 해 주는 문법입니다. | AI에게 "callback 대신 async/await로 작성해줘"라고 요청하는 기준입니다. |
| AbortController | 진행 중인 요청을 취소하는 도구입니다. | 화면 전환 시 오래된 요청이 남는 버그를 방지하는 데 필요합니다. |
| Stale-while-revalidate | 캐시된 데이터를 먼저 보여 주고 뒤에서 새로 고치는 전략입니다. | 체감 속도를 높이는 TanStack Query나 SWR의 핵심 동작입니다. |

## 콜백 중심 비동기에서 상태 중심 비동기로

| 방식 | 코드 특징 | 실무 영향 |
|---|---|---|
| 콜백 중첩 중심 흐름 | 제어 흐름과 상태 분기가 여러 곳에 흩어집니다. | 예외 처리와 취소 로직이 뒤늦게 붙으며 복잡도가 빠르게 올라갑니다. |
| `async/await` + 명시적 상태 | 흐름을 위에서 아래로 읽고 화면 상태를 분리합니다. | 네트워크 지연, 에러, 요청 취소를 한 모델 안에서 다루기 쉬워집니다. |

**Before (콜백 지옥)**

```javascript
fetch(url, (res) => {
  parse(res, (data) => {
    render(data, (e) => { ... });
  });
});
```

**After (async/await + 명시적 상태)**

```javascript
setState({ status: "loading" });
try {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  setState({ status: "success", data });
} catch (err) {
  setState({ status: "error", err });
}
```

AI에게 요청할 때 "로딩/성공/에러 세 가지 상태를 모두 처리해줘"라고 명시하면 두 번째 패턴의 코드가 나옵니다.

## AI 팁: 비동기 코드 품질 향상 요청

- **세 가지 상태 명시 요청**: "idle, loading, success, error 상태를 모두 명시적으로 처리해줘"를 항상 포함하세요.
- **AbortController 요청**: "컴포넌트 unmount 시 요청을 취소하는 cleanup 함수도 포함해줘"를 추가하세요.
- **res.ok 확인 요청**: "fetch 후 res.ok 검사를 포함해줘. HTTP 오류도 catch에서 처리해줘"를 명시하세요.
- **React Query 활용 제안**: "직접 상태 관리 대신 TanStack Query를 사용해서 캐싱과 에러 처리를 자동화해줘"로 업그레이드할 수 있습니다.
- **Slow 3G 테스트 요청**: "DevTools에서 Slow 3G로 테스트하는 방법도 알려줘"를 추가하면 실제 환경을 검증할 수 있습니다.

## 실수 유형과 바이브코딩 대처법

| 실수 유형 | 증상 | 바이브코딩 대처 |
|---|---|---|
| 로딩 상태 생략 | 사용자가 앱이 멈췄다고 느낌 | "로딩 스피너 또는 스켈레톤 UI 추가해줘" 요청 |
| 에러를 콘솔에만 출력 | 사용자는 이유 없는 빈 화면만 봄 | "에러 발생 시 사용자에게 친절한 메시지 표시해줘" 요청 |
| race condition 무시 | 오래된 검색 결과가 최신을 덮어씀 | "AbortController로 이전 요청을 취소해줘" 요청 |
| 같은 데이터를 여러 곳에서 각각 요청 | 중복 API 호출 | "TanStack Query나 SWR로 캐시 공유 구조로 바꿔줘" 요청 |
| 캐시 무효화 전략 없음 | 오래된 데이터가 계속 표시됨 | "데이터 변경 후 캐시를 무효화하는 로직 추가해줘" 요청 |

## 체크리스트

- [ ] `fetch`를 `async/await`와 함께 작성할 수 있습니다.
- [ ] 로딩, 에러, 성공 상태를 각각 따로 렌더링할 수 있습니다.
- [ ] `AbortController`를 한 번 사용해 봤습니다.
- [ ] React Query나 SWR을 직접 써 봤습니다.
- [ ] Slow 3G 환경에서 동작을 점검해 봤습니다.
- [ ] AI가 생성한 fetch 코드에서 누락된 상태 처리를 발견할 수 있습니다.

## 처음 질문으로 돌아가기

- **`fetch`와 `async/await`는 어떤 최소 패턴으로 시작하면 될까요?**
  `async` 함수 안에서 `await fetch(url)`로 요청하고, `res.ok`를 확인하고, `await res.json()`으로 데이터를 읽습니다. try-catch로 에러를 잡습니다. 이 다섯 줄이 최소 패턴입니다.

- **로딩 상태와 에러 상태를 왜 반드시 화면에 드러내야 할까요?**
  사용자는 앱이 무엇을 하고 있는지 알 권리가 있습니다. 로딩 표시 없이 기다리면 앱이 멈춘 것처럼 보이고, 에러 표시 없이 빈 화면이 나오면 사용자는 자신이 뭘 잘못했다고 생각합니다.

- **컴포넌트가 사라질 때 요청 취소가 왜 필요할까요?**
  사용자가 화면을 이동했는데 이전 요청이 완료되면 이미 unmount된 컴포넌트의 상태를 업데이트하려다 오류가 발생합니다. AbortController로 요청을 취소하면 이 문제를 방지할 수 있습니다.

## 정리

비동기는 결국 상태입니다. 로딩, 성공, 실패를 각각 다른 화면으로 다루는 관점이 생기면 다음에 다룰 폼과 유효성 검사도 같은 방식으로 이해할 수 있습니다.

다음 글에서는 폼과 유효성 검사를 통해 사용자 입력을 안전하고 친절하게 다루는 방법을 살펴봅니다.

## 참고 자료

### 공식 문서
- [MDN: Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [MDN: AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)
- [TanStack Query docs](https://tanstack.com/query/latest)

### 확인용 자료
- [SWR documentation](https://swr.vercel.app/)
- [web.dev: Fetch API error handling](https://web.dev/articles/fetch-api-error-handling)
- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/frontend-development-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 프론트엔드 개발 기초 (1/10): 프론트엔드 개발이란 무엇인가?
- 바이브코딩을 위한 프론트엔드 개발 기초 (2/10): HTML과 CSS 기본
- 바이브코딩을 위한 프론트엔드 개발 기초 (3/10): JavaScript 기본
- 바이브코딩을 위한 프론트엔드 개발 기초 (4/10): 컴포넌트와 상태
- 바이브코딩을 위한 프론트엔드 개발 기초 (5/10): 라우팅과 페이지
- **바이브코딩을 위한 프론트엔드 개발 기초 (6/10): API 호출과 비동기 (현재 글)**
- 바이브코딩을 위한 프론트엔드 개발 기초 (7/10): 폼과 유효성 검사
- 바이브코딩을 위한 프론트엔드 개발 기초 (8/10): 스타일링과 디자인 시스템
- 바이브코딩을 위한 프론트엔드 개발 기초 (9/10): 빌드 도구와 번들링
- 바이브코딩을 위한 프론트엔드 개발 기초 (10/10): 작은 프론트엔드 앱 만들기

<!-- toc:end -->

Tags: 바이브코딩, Frontend, API, Async, Fetch, JavaScript
