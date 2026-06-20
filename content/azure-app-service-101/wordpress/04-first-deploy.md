---
title: "바이브코딩을 위한 Azure App Service (4/7): 첫 번째 배포"
series: azure-app-service-101
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAppService
- 첫배포
- Flask
- AI코딩
seo_description: "바이브코딩을 위한 Azure App Service 4편: 첫 번째 배포. Flask 앱을 로컬에서 검증하고 Azure App Service에 배포한 뒤 상태와 로그까지 확인하는 흐름을 이해합니다."
---

# 바이브코딩을 위한 Azure App Service (4/7): 첫 번째 배포

이 글은 바이브코딩을 위한 Azure App Service 시리즈의 4번째 글입니다.

로컬에서 잘 돌던 앱이 App Service에서 안 뜨는 경험은 대부분 시작 명령어, 포트, requirements.txt 세 가지 중 하나가 문제입니다. "배포가 됐다"는 성공 메시지는 코드가 업로드됐다는 뜻이지 앱이 응답한다는 뜻이 아닙니다. 배포 후 반드시 /health 엔드포인트 응답을 확인하고, LogStream으로 시작 로그를 직접 봐야 합니다. 특히 App Service에서 Python 앱은 gunicorn을 사용하고 기본 포트는 8000이 아닌 App Service가 지정하는 환경변수 PORT를 써야 합니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 배포 코드를 요청할 때 startup command, PORT 환경변수 바인딩, 배포 후 검증 단계를 명시하지 않으면, 배포는 성공해도 앱이 안 뜨는 상황이 발생하기 때문입니다.

> 배포 성공 메시지는 코드 업로드 완료를 의미합니다. 앱이 실제로 응답하는지는 /health 엔드포인트와 LogStream으로 직접 확인해야 합니다.

---

## 이 글에서 다룰 문제

- App Service에서 Python 앱의 startup command는 어떻게 설정해야 할까요?
- PORT 환경변수를 왜 직접 바인딩해야 할까요?
- 배포 후 배포 실패와 앱 시작 실패를 어떻게 구분할까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

첫 배포 절차를 이해하면 AI에게 "Flask 앱을 App Service에 배포하고 startup command, PORT 설정, /health 검증까지 포함한 배포 스크립트"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "Flask 앱을 Azure App Service에 배포하는 코드 작성해줘"
→ az webapp up만 실행하는 단순 스크립트
→ startup command 미설정
→ 배포 후 검증 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "Flask 앱을 Linux App Service에 배포하는 스크립트를 작성해줘.
    startup command는 'gunicorn app:app --bind 0.0.0.0:$PORT'로 설정해줘.
    배포 후 az webapp show로 상태 확인하고
    /health 엔드포인트에 curl을 보내 200 응답 확인까지 포함해줘"
→ 시작 명령어와 포트 바인딩 명시
→ 배포 성공과 앱 시작 성공을 분리 검증
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| startup command 없이 배포 | App Service가 앱 시작 방법 모름 | gunicorn/uvicorn 명령을 명시 |
| 포트를 8000으로 하드코딩 | App Service는 다른 포트를 사용할 수 있음 | `--bind 0.0.0.0:$PORT`로 환경변수 참조 |
| requirements.txt 누락 | 의존 패키지 설치 실패로 앱 미시작 | 루트 디렉토리에 requirements.txt 필수 |
| 배포 성공을 앱 시작 성공으로 오해 | 코드 업로드와 앱 실행은 별개 | LogStream으로 시작 로그 직접 확인 |
| 로컬 포트와 운영 포트를 같다고 가정 | 환경별 포트 충돌 가능 | PORT 환경변수를 항상 동적으로 읽기 |

## AI 협업 팁

App Service 첫 배포 관련 효과적인 AI 프롬프트 패턴:

1. **배포 스크립트 요청**: "Flask 앱을 zip 배포로 App Service에 올리고 startup command를 gunicorn으로 설정하는 bash 스크립트 작성해줘"
2. **검증 스크립트 요청**: "배포 후 /health 엔드포인트에 30초 간격으로 3번 확인해 모두 200이면 성공, 아니면 LogStream URL을 출력하는 스크립트 작성해줘"
3. **트러블슈팅 요청**: "App Service에서 앱이 시작하지 않을 때 startup 로그에서 원인을 찾는 az webapp log tail 명령과 주요 에러 패턴을 알려줘"

예시 프롬프트:
> "Flask 앱을 Azure App Service Linux에 배포하는 스크립트를 작성해줘. 단계: 1) az webapp up으로 배포 2) startup command를 'gunicorn app:app --bind 0.0.0.0:$PORT'로 설정 3) /health에 curl로 200 확인 4) 실패 시 az webapp log tail 출력."

## 운영 체크리스트

- [ ] startup command가 gunicorn/uvicorn과 $PORT를 사용하는가?
- [ ] requirements.txt가 루트 디렉토리에 있는가?
- [ ] /health 엔드포인트가 구현되어 있는가?
- [ ] 배포 후 LogStream으로 앱 시작 로그를 확인했는가?
- [ ] 다음 글에서 배포된 앱의 설정을 App Settings로 관리할 준비가 됐는가?

## 처음 질문으로 돌아가기

첫 번째 배포를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. startup command와 배포 후 검증을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 배포 스크립트의 완성도는 크게 다릅니다.

## 정리

첫 번째 배포는 바이브코딩을 위한 Azure App Service에서 로컬 개발을 운영으로 연결하는 핵심 단계입니다. startup command, PORT 환경변수, 배포 성공과 앱 시작 성공의 구분을 이해했습니다. 다음 글에서는 배포된 앱의 설정을 안전하게 관리하는 방법을 다룹니다.

## 참고 자료

- [Deploy Python (Flask) app to App Service](https://docs.microsoft.com/azure/app-service/quickstart-python)
- [Configure startup command](https://docs.microsoft.com/azure/app-service/configure-language-python)
- [az webapp up reference](https://docs.microsoft.com/cli/azure/webapp#az-webapp-up)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-app-service-101/ko/04-first-deploy)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure App Service (1/7): App Service란 무엇인가
- 바이브코딩을 위한 Azure App Service (2/7): 요청 수명 주기
- 바이브코딩을 위한 Azure App Service (3/7): 호스팅 모델 선택
- **바이브코딩을 위한 Azure App Service (4/7): 첫 번째 배포 (현재 글)**
- 바이브코딩을 위한 Azure App Service (5/7): 설정 관리
- 바이브코딩을 위한 Azure App Service (6/7): 로그와 모니터링
- 바이브코딩을 위한 Azure App Service (7/7): 스케일링
<!-- toc:end -->

Tags: 바이브코딩, AzureAppService, 첫배포, AI코딩
