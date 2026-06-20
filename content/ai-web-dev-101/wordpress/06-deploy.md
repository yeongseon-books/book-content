---
series: ai-web-dev-101
episode: 6
title: "바이브코딩을 위한 AI 웹 개발 (6/7): 배포하기"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - AI 웹 개발
  - Deployment
  - Vercel
  - Azure
language: ko
---

# 바이브코딩을 위한 AI 웹 개발 (6/7): 배포하기

> 이 글은 **바이브코딩을 위한 AI 웹 개발** 시리즈 6편입니다. Vercel과 Azure App Service로 AI 앱을 배포하고, 시크릿 관리와 비용 모니터링을 설정하는 방법을 다룹니다.

바이브코딩으로 AI 앱을 만들었다면 이제 배포할 차례다. 로컬에서 잘 되던 앱을 프로덕션에 올리면 예상치 못한 문제가 생기는 경우가 많다. API 키가 환경변수로 주입되지 않거나, 모델 호출 지연이 serverless 함수 타임아웃을 초과하거나, 비용이 예상보다 빠르게 쌓이거나.

Next.js 앱은 Vercel이 가장 간단하다. GitHub 리포지토리를 연결하고 환경변수를 설정하면 자동으로 CI/CD가 구성된다. API 키는 Vercel 대시보드의 Environment Variables에 넣고, 코드에는 절대 하드코딩하지 않는다.

FastAPI 같은 Python 백엔드는 Azure App Service가 현실적이다. `az webapp up` 한 줄로 배포를 시작할 수 있고, gunicorn + uvicorn 조합으로 프로덕션 서버를 구성한다.

시크릿 관리는 처음부터 제대로 해야 한다. AWS Secrets Manager, Azure Key Vault, Vercel Environment Variables처럼 플랫폼 제공 시크릿 저장소를 사용하고, `.env` 파일은 로컬에서만 사용하고 Git에 올리지 않는다.

비용 알림도 처음부터 설정한다. OpenAI 대시보드에서 usage limit을 설정하고, 클라우드 플랫폼에서 예산 알림을 만들면 예상치 못한 비용 폭증을 막을 수 있다.

롤백 기준도 미리 정해야 한다. 오류율이 갑자기 오르거나 API 응답 지연이 기준을 초과하면 이전 버전으로 즉시 롤백할 수 있는 절차가 있어야 한다.

> 배포는 코드를 서버에 올리는 일이 아닙니다. 시크릿 관리, 비용 통제, 롤백 기준까지 포함한 운영 준비입니다.

## 이 글에서 다룰 문제

- Vercel에 Next.js AI 앱을 배포하는 단계는 무엇인가요?
- Azure App Service에 Python FastAPI 앱을 배포하는 방법은 무엇인가요?
- API 키와 시크릿을 안전하게 관리하는 방법은 무엇인가요?
- 비용 알림은 어떻게 설정해야 할까요?
- 롤백 기준은 어떻게 정의해야 할까요?

## Before / After: 배포 전후

| 상황 | 준비 없이 배포 | 준비 후 배포 |
|------|--------------|------------|
| API 키 | 코드에 하드코딩 | 플랫폼 환경변수로 주입 |
| 비용 | 폭증 뒤 발견 | 예산 알림으로 조기 감지 |
| 장애 발생 | 수동 확인 후 롤백 | 오류율 기준 자동 알림 |
| CI/CD | 수동 배포 | Git push로 자동 배포 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| `.env` 파일을 Git에 커밋 | API 키 노출 | `.gitignore`에 추가 |
| 비용 알림 미설정 | 월말에 청구서 충격 | OpenAI + 클라우드 양쪽에 예산 알림 |
| serverless 타임아웃 초과 | 모델 호출 실패 | 타임아웃 설정 확인, 스트리밍 고려 |
| 롤백 기준 없이 운영 | 장애 시 판단 지연 | 오류율/지연 기준 사전 정의 |

## AI 팁: 배포 빠르게 시작하는 방법

Claude나 GPT-4에 "Vercel에 Next.js AI 앱을 배포하는 단계와 환경변수 설정 방법을 알려줘"라고 요청하면 단계별 가이드를 얻을 수 있다. Vercel CLI는 `npm i -g vercel`로 설치하고 `vercel`로 배포한다. 환경변수는 `vercel env add OPENAI_API_KEY`로 추가한다. Azure는 `az webapp up --name myapp --resource-group mygroup`으로 시작할 수 있다. 비용 알림은 OpenAI 대시보드 Settings > Limits에서 hard limit을 설정하는 것부터 시작한다.

## 운영 체크리스트

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는가
- [ ] API 키가 플랫폼 환경변수로만 주입되는가
- [ ] OpenAI usage limit과 클라우드 예산 알림을 설정했는가
- [ ] health check 엔드포인트가 있는가
- [ ] 오류율/지연 기준 롤백 정책을 문서화했는가

## 처음 질문으로 돌아가기

- **Vercel vs Azure 선택 기준은?** Next.js 앱은 Vercel이 통합이 자연스럽다. Python 백엔드나 컨테이너가 필요하면 Azure App Service나 Container Apps.
- **시크릿 관리 핵심은?** 플랫폼 환경변수 사용, `.env`는 로컬에서만, Git에는 절대 올리지 않는다.
- **비용 통제는?** OpenAI hard limit + 클라우드 예산 알림을 양쪽에 설정한다.

## 정리

배포는 코드를 올리는 것이 아니라 운영을 시작하는 것이다. 시크릿 관리, 비용 통제, 장애 대응 기준까지 처음부터 갖추면 바이브코딩의 빠른 배포 속도를 안전하게 유지할 수 있다.

## 참고 자료

- [Vercel Deployment](https://vercel.com/docs/deployments/overview)
- [Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/ai-web-dev-101/ko/06-deploy)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 AI 웹 개발 (1/7): AI API 첫 걸음
- 바이브코딩을 위한 AI 웹 개발 (2/7): 프롬프트 엔지니어링 기초
- 바이브코딩을 위한 AI 웹 개발 (3/7): AI 챗봇 만들기
- 바이브코딩을 위한 AI 웹 개발 (4/7): RAG 기초
- 바이브코딩을 위한 AI 웹 개발 (5/7): AI 에이전트
- **바이브코딩을 위한 AI 웹 개발 (6/7): 배포하기 (현재 글)**
- 바이브코딩을 위한 AI 웹 개발 (7/7): 평가와 개선
<!-- toc:end -->

Tags: 바이브코딩, AI 웹 개발, Deployment, Vercel, Azure
