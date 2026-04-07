# Tech Blog

Medium 블로그 포스트 원고 저장소.

## 시리즈

### Azure App Service 101

Azure App Service 입문자를 위한 실전 가이드 시리즈.

| # | 제목 | 파일 | 예상 분량 |
|---|---|---|---|
| 1 | Azure App Service란? - 플랫폼 아키텍처 이해하기 | [01-what-is-app-service.md](./azure-app-service-101/01-what-is-app-service.md) | 8분 |
| 2 | Request Lifecycle: 요청이 앱에 도달하기까지 | [02-request-lifecycle.md](./azure-app-service-101/02-request-lifecycle.md) | 7분 |
| 3 | Hosting Models: 어떤 플랜을 선택해야 할까? | [03-hosting-models.md](./azure-app-service-101/03-hosting-models.md) | 6분 |
| 4 | 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask) | [04-first-deploy.md](./azure-app-service-101/04-first-deploy.md) | 10분 |
| 5 | Configuration 마스터하기: App Settings & 환경변수 | [05-configuration.md](./azure-app-service-101/05-configuration.md) | 7분 |
| 6 | 로그와 모니터링 기초 | [06-logging-monitoring.md](./azure-app-service-101/06-logging-monitoring.md) | 8분 |
| 7 | Scaling 101: 언제 Scale Up vs Scale Out? | [07-scaling-101.md](./azure-app-service-101/07-scaling-101.md) | 6분 |

## 폴더 구조

```
tech-blog/
├── README.md
├── azure-app-service-101/
│   ├── 01-what-is-app-service.md
│   ├── 02-request-lifecycle.md
│   ├── 03-hosting-models.md
│   ├── 04-first-deploy.md
│   ├── 05-configuration.md
│   ├── 06-logging-monitoring.md
│   └── 07-scaling-101.md
└── assets/
    └── azure-app-service-101/
        ├── 01/
        ├── 02/
        ...
```

## 이미지 규칙

- 모든 이미지는 `assets/<시리즈>/<포스트번호>/` 폴더에 저장
- 파일명: `01-description.png` 형식
- Medium 업로드 시 직접 드래그 앤 드롭

## Medium 퍼블리싱 체크리스트

- [ ] 제목과 서브타이틀 확인
- [ ] 이미지 플레이스홀더에 실제 캡처 삽입
- [ ] 코드 블록 syntax highlighting 확인
- [ ] 태그 추가: `Azure`, `App Service`, `Cloud`, `DevOps`
- [ ] 시리즈 링크 연결
