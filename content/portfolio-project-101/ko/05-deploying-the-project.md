---
series: portfolio-project-101
episode: 5
title: "Portfolio Project 101 (5/10): 배포하기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Portfolio
  - Deploy
  - DevOps
  - Hosting
  - Beginner
seo_description: 프로젝트 결과물을 외부에서 확인 가능한 URL로 배포하는 과정과 지속적 업데이트를 위한 자동화 파이프라인 구축을 익힙니다.
last_reviewed: '2026-05-15'
---

# Portfolio Project 101 (5/10): 배포하기

포트폴리오 프로젝트는 로컬에서만 돌아가면 절반만 끝난 상태입니다. 구현이 잘 되었다는 주장과, 다른 사람이 실제로 열어 볼 수 있다는 사실은 다릅니다. 저장소 설명이 아무리 좋아도 공개 URL이 없으면 프로젝트는 여전히 설명에 의존합니다. 반대로 작은 서비스라도 링크가 살아 있고 다시 배포할 수 있으면 훨씬 실전처럼 읽힙니다.

이 글은 Portfolio Project 101 시리즈의 5번째 글입니다. 여기서는 포트폴리오 배포를 거대한 인프라 설계가 아니라 공개 URL, 환경 변수 분리, 재배포 가능한 흐름, 상태 확인 경로를 갖추는 일로 보고 정리해 보겠습니다.


![Portfolio Project 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/portfolio-project-101/05/05-01-diagram.ko.png)
*Portfolio Project 101 5장 흐름 개요*
> 로컬에서만 동작하는 코드는 증거가 아닙니다. 배포되어 모든 사람이 접근할 수 있을 때, 비로소 '끝까지 완성한 프로젝트'로 읽힙니다.

## 먼저 던지는 질문

- 포트폴리오 프로젝트에서 공개 URL이 왜 필수에 가까울까요?
- 호스팅 플랫폼은 화려함보다 어떤 기준으로 골라야 할까요?
- 시크릿과 환경 변수는 왜 코드가 아니라 배포 환경에서 관리해야 할까요?

## 왜 중요한가

배포는 작업 결과를 세상과 연결합니다. 채용 담당자나 동료 개발자는 로컬 환경을 상상하면서 평가하지 않습니다. 직접 접속하고, 눌러 보고, 상태를 확인할 수 있어야 프로젝트가 현실적인 결과물로 읽힙니다.

또 배포 방식은 개발자의 운영 감각을 보여 줍니다. 프로젝트가 작더라도 시크릿을 코드에서 분리하고, 같은 절차로 다시 올릴 수 있고, 상태를 확인하는 경로까지 갖추면 단순 구현을 넘어 운영 관점까지 생각한 흔적이 남습니다.

## 머릿속에 먼저 그릴 그림

배포를 복잡하게 볼 필요는 없습니다. 코드가 저장소로 올라가고, 빌드되고, 배포되고, 상태를 확인한 뒤, 안정적으로 열리는 URL로 이어지면 됩니다.

이 흐름은 문제가 생겼을 때도 유용합니다. 빌드에서 막혔는지, 배포는 됐지만 애플리케이션이 뜨지 않는지, URL은 열리는데 내부 상태가 깨졌는지 구분할 수 있기 때문입니다. 포트폴리오도 결국 이런 구분이 가능한 쪽이 더 성숙하게 보입니다.

## 핵심 용어

- 호스팅: 애플리케이션을 실제로 올리는 서비스 제공자입니다.
- **도메인 또는 공식 URL**: 사용자가 접속하는 대표 주소입니다.
- **환경 변수**: 시크릿이나 환경별 설정 값을 담는 배포 환경의 변수입니다.
- **지속 배포**: 코드 변경이 배포까지 자동으로 이어지는 흐름입니다.
- 비용: 매달 실제로 감당해야 하는 운영 비용입니다.

## 바꾸기 전과 후

**Before**: localhost에서만 실행되고, 다른 사람은 결과를 확인할 방법이 없습니다.

**After**: 공개 URL이 있고, 시크릿이 분리되어 있으며, 같은 절차로 다시 배포할 수 있습니다.

전자는 설명 중심 프로젝트입니다. 후자는 확인 중심 프로젝트입니다. 포트폴리오에서 강한 쪽은 거의 항상 후자입니다. 실제로 열어 볼 수 있기 때문입니다.

## 단계별로 살펴보기

### 1단계 — 호스팅 선택

처음부터 복잡한 인프라를 고를 필요는 없습니다.

```python
host = "fly.io"  # or render, railway
```

여기서 중요한 기준은 화려함이 아니라 반복 가능성입니다. 배포가 쉬운가, 다시 배포하기 쉬운가, 무료 또는 저비용으로 오래 유지할 수 있는가를 먼저 보는 편이 좋습니다.

### 2단계 — 환경 변수 분리

시크릿은 코드에 넣지 않고 배포 환경에서 주입해야 합니다.

```python
env = {"DATABASE_URL": "...", "SECRET_KEY": "..."}
```

이 분리는 공개 저장소에서 특히 중요합니다. 동시에 로컬, 테스트, 운영 환경을 나누는 출발점이 되기도 합니다. 포트폴리오에서 이 기본기만 보여 줘도 신뢰가 크게 올라갑니다.

### 3단계 — 빌드 명령 정리

배포는 수작업 복사가 아니라 반복 가능한 빌드 절차여야 합니다.

```bash
docker build -t app .
```

Docker를 쓰면 실행 환경 차이를 줄이기 쉽습니다. 검토자 입장에서도 "어떻게 다시 띄우는가"가 더 분명해집니다.

### 4단계 — 실제 배포

한 번 성공시키는 것보다 같은 명령으로 다시 올릴 수 있는 상태가 중요합니다.

```bash
fly deploy
```

포트폴리오 프로젝트도 결국 유지 가능한 흐름이 있어야 오래 살아남습니다. 재배포가 복잡하면 작은 수정조차 미루게 되고, 데모는 금방 낡습니다.

### 5단계 — 헬스체크

배포가 끝난 뒤 상태를 확인할 기준이 필요합니다.

```python
url = "https://app.fly.dev/healthz"
```

헬스체크는 문제가 생겼을 때 어디서부터 볼지 알려 줍니다. 링크가 안 열리는지, 앱은 열리지만 내부 기능이 깨졌는지, 초기화가 필요한지 구분하는 출발점이 됩니다.

## 이 코드에서 먼저 볼 점

- 호스팅 선택은 복잡성보다 단순함과 유지 가능성이 우선입니다.
- 환경 변수 분리는 공개 저장소의 기본 안전장치입니다.
- 헬스체크와 재배포 절차는 운영 감각을 보여 주는 흔적입니다.

## 자주 하는 실수

1. 시크릿 값을 코드나 README 예제에 그대로 넣는 경우
2. 데모 URL은 있지만 어떤 주소가 공식 주소인지 분명하지 않은 경우
3. 상태 확인 경로가 없어 장애 판단이 어려운 경우
4. 무료 요금제와 월 비용을 고려하지 않아 데모를 오래 유지하지 못하는 경우
5. 재배포 절차가 수동이라 작은 수정도 바로 반영하지 못하는 경우

이 실수들은 결국 데모 수명을 짧게 만듭니다. 포트폴리오는 하루 반짝 열리는 서비스보다, 몇 주와 몇 달 꾸준히 보여 줄 수 있는 작은 서비스가 훨씬 낫습니다.

## 실무에서는 이렇게 본다

초기 제품이나 개인 서비스도 작은 단계에서는 단순한 플랫폼을 많이 씁니다. Render, Fly.io, Railway, Vercel처럼 접근이 쉬운 도구를 먼저 고르고, 서비스 가치가 검증되면 그다음에 복잡도를 올립니다. 포트폴리오도 이 판단이 잘 맞습니다.

처음부터 거대한 인프라를 도입하는 것보다, 공개 URL과 재배포 흐름을 안정적으로 유지하는 편이 훨씬 설득력 있습니다. 리뷰어는 배포 규모보다 배포 품질을 더 많이 봅니다.

## 체크리스트

- [ ] 호스팅 플랫폼을 하나로 정했다.
- [ ] 공식 공개 URL을 README에 명확히 적었다.
- [ ] 데이터베이스와 시크릿 값을 환경 변수로 분리했다.
- [ ] 최소한의 헬스체크 경로를 준비했다.

## 연습 문제

1. 여러분 프로젝트에 맞는 호스팅 후보 하나를 고르고 이유를 적어 보세요.
2. 코드에서 환경 변수로 옮겨야 할 민감한 값 세 가지를 써 보세요.
3. 현재 데모가 깨졌을 때 가장 먼저 확인할 경로가 무엇인지 적어 보세요.

## 정리와 다음 글

포트폴리오 배포의 핵심은 거대한 인프라가 아닙니다. 누구나 접속할 수 있는 URL, 코드와 분리된 환경 변수, 다시 실행할 수 있는 배포 흐름, 기본 상태를 확인할 수 있는 헬스체크가 있으면 충분합니다. 이 네 가지가 갖춰지면 작은 프로젝트도 운영 가능한 결과물로 읽힙니다.

다음 글에서는 테스트와 문서화를 통해 이 프로젝트가 우연히 돌아가는 것이 아니라 반복해서 검증되는 상태라는 점을 어떻게 보여 줄지 봅니다.

### CI/CD 파이프라인 기본 YAML 예시

배포 품질을 높이려면 "한 번 배포 성공"이 아니라 "코드가 바뀔 때마다 같은 방식으로 검증 후 배포"되는 흐름이 필요합니다. 아래 예시는 포트폴리오 프로젝트에 적합한 최소 CI/CD 파이프라인 구조입니다.

```yaml
name: ci-cd
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest -q

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t app:${{ github.sha }} .

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/deploy.sh
```

핵심은 순서입니다. 테스트 없이 배포하지 않고, 빌드 성공 없이 배포하지 않는 구조를 고정해야 합니다. 이 원칙만 지켜도 데모 장애율을 크게 줄일 수 있습니다.

### 테스트 전략 표(무엇을 어디서 검증할지)

테스트를 많이 작성하는 것보다, 어떤 실패를 어디서 잡을지 전략을 분리하는 편이 중요합니다.

| 테스트 종류 | 목적 | 예시 | 실행 시점 |
| --- | --- | --- | --- |
| 단위 테스트 | 로직 오류 조기 탐지 | 날짜 정규화 함수 검증 | PR마다 |
| 통합 테스트 | API-DB 경계 확인 | `/healthz`, `/schedule` 응답 검증 | PR마다 |
| 스모크 테스트 | 배포 후 생존 확인 | 메인 페이지/헬스체크 확인 | 배포 직후 |
| 회귀 체크 | 핵심 흐름 유지 | 로그인-조회-공유 시나리오 | 릴리스 전 |

이 표를 README나 `docs/testing.md`에 포함하면 "검증이 우연이 아니라 설계"라는 신호를 줄 수 있습니다.

### 배포 실패 대응 런북(간단 버전)

배포가 실패했을 때 당황하지 않으려면 최소 런북이 필요합니다. 아래처럼 단계별 확인 항목만 있어도 문제 분류가 빨라집니다.

```markdown
## Deploy Failure Runbook
1. CI test job 실패 여부 확인
2. Docker build 로그에서 의존성/네트워크 오류 확인
3. 배포 플랫폼 환경 변수 누락 확인
4. `/healthz` 상태코드와 응답 본문 확인
5. 직전 정상 버전으로 롤백
```

포트폴리오에서 런북은 과한 문서가 아닙니다. 오히려 운영 관점을 갖고 있다는 강한 증거입니다. 작은 프로젝트라도 장애 대응 기준이 있으면 완성도가 확실히 다르게 보입니다.

### 배포 환경 변수 관리 가이드

환경 변수는 단순 설정값이 아니라 보안과 운영 품질의 경계선입니다. 최소한 아래 분류로 관리하면 실수를 줄일 수 있습니다.

| 분류 | 예시 | 저장 위치 | 주의점 |
| --- | --- | --- | --- |
| 비밀값 | SECRET_KEY, DB_PASSWORD | 배포 플랫폼 시크릿 | 저장소 커밋 금지 |
| 환경별 값 | APP_ENV, LOG_LEVEL | dev/prod 분리 | 기본값 명시 |
| 공개 가능 값 | FEATURE_FLAG | 설정 파일/문서 | 목적 설명 필요 |

```markdown
.env.example 원칙
- 실제 비밀번호 대신 플레이스홀더 사용
- 필수/선택 변수 구분
- 기본 포맷과 타입 설명
```

이 정리만 되어도 새 환경으로 옮길 때 배포 속도가 크게 올라가고, 장애 원인 추적도 쉬워집니다.

### GitHub Actions 배포 파이프라인 완전 예시

포트폴리오 프로젝트에 CI/CD를 설정하면 '다시 배포할 수 있는 프로젝트'라는 신뢰를 줘야 합니다. 아래는 FastAPI 앱을 Render에 배포하는 실제 워크플로입니다.

```yaml
# .github/workflows/deploy.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint
        run: ruff check .

      - name: Type check
        run: mypy src/

      - name: Test
        run: pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} .
          docker tag ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}

      - name: Wait for deploy
        run: sleep 30

      - name: Health check
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${{ secrets.APP_URL }}/healthz)
          if [ "$STATUS" != "200" ]; then
            echo "Deploy failed! Health check returned $STATUS"
            exit 1
          fi
```

이 파이프라인의 핵심은 3단계 분리입니다. test → build → deploy 순서로 진행하며, 앞 단계가 실패하면 뒤 단계는 실행되지 않습니다. PR에서는 test만, main push에서만 build/deploy가 동작합니다.

### Dockerfile 작성 기본

배포 가능한 프로젝트라면 Dockerfile이 있어야 합니다. 아래는 FastAPI 프로젝트의 기본 Dockerfile입니다.

```dockerfile
# Dockerfile
FROM python:3.11-slim AS base

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY scripts/seed_demo_data.py ./scripts/

# 데모용 시드 데이터 생성
RUN python scripts/seed_demo_data.py

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Dockerfile에서 주의할 점:

1. **slim 이미지 사용**: 이미지 크기를 줄이면 배포 속도가 빨라집니다.
2. **requirements.txt 먼저 복사**: 레이어 캐싱으로 빌드 시간을 단축합니다.
3. **시드 데이터 포함**: 데모 환경에서 빈 화면을 방지합니다.
4. **포트 명시**: 문서화 목적으로 어떤 포트를 사용하는지 명시합니다.

### 도메인 연결과 헬스체크

프로젝트에 커스텀 도메인을 연결하면 전문성이 높아 보입니다. 하지만 필수는 아닙니다. 우선순위는 다음과 같습니다.

| 우선순위 | 설정 | 이유 |
| --- | --- | --- |
| 1 | 헬스체크 엔드포인트 | 데모가 살아 있는지 자동 확인 |
| 2 | HTTPS 설정 | 브라우저 보안 경고 방지 |
| 3 | 커스텀 도메인 | 전문성 + 링크 안정성 |

헬스체크 엔드포인트는 간단하지만 효과가 큽니다:

```python
# src/health.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
```

이 엔드포인트가 있으면 CI/CD에서 배포 성공 여부를 자동으로 판단할 수 있고, 모니터링 도구와 연동해 다운타임을 발견할 수도 있습니다.

### 배포 비용 비교표

포트폴리오 프로젝트는 오래 유지해야 하므로 비용이 중요합니다. 대부분의 포트폴리오 프로젝트는 무료 티어로 충분합니다.

| 플랫폼 | 무료 티어 | 제한사항 | 적합한 용도 |
| --- | --- | --- | --- |
| Vercel | 무제한 배포 | 서버리스/정적 사이트 | 프론트엔드, Next.js |
| Render | 750시간/월 | 15분 불활동 시 sleep | API 서버 |
| Railway | $5 크레딧/월 | 소진 시 정지 | 전체 스택 |
| Fly.io | 3개 VM | 256MB RAM | 컬테이너 기반 |
| GitHub Pages | 무제한 | 정적 사이트만 | 포트폴리오 웹사이트 |

추천 전략: 프론트엔드는 Vercel, API는 Render 또는 Railway, 포트폴리오 웹사이트는 GitHub Pages로 구성하면 월 비용 $0으로 운영할 수 있습니다. 비용이 발생하는 시점에 도달하면 그때 마이그레이션하면 됩니다.

### 배포 후 체크리스트

배포가 완료되면 아래 항목을 순서대로 확인합니다.

```text
[ ] 공개 URL에서 첫 화면 로드 확인
[ ] 헬스체크 엔드포인트 200 응답 확인
[ ] 환경 변수 누락 없음 확인 (에러 로그 점검)
[ ] HTTPS 적용 확인 (브라우저 자물쇠 아이콘)
[ ] 시드 데이터가 정상적으로 보이는지 확인
[ ] README의 데모 URL이 배포된 URL과 일치하는지 확인
[ ] 모바일에서 접속해 레이아웃 확인
```

이 체크리스트를 통과하면 "배포된 프로젝트"로서 최소 요건을 충족합니다. README에 이 체크리스트 통과 사실을 기록해 두면 검토자에게 운영 관점을 보여 줄 수 있습니다.

### Docker Compose로 로컬/프로덕션 환경 일치시키기

로컬에서는 되는데 배포하면 안 되는 문제는 대부분 환경 차이에서 생깁니다. Docker Compose를 사용하면 로컬과 배포 환경의 차이를 최소화할 수 있습니다.

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/portfolio
      - APP_ENV=development
      - SECRET_KEY=${SECRET_KEY:-dev-secret-key}
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: portfolio
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      retries: 3
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

README에 다음 명령을 넣으면 누구나 동일한 환경을 재현할 수 있습니다:

```bash
# 로컬 실행 (3단계)
git clone https://github.com/username/task-tracker.git
cd task-tracker
docker compose up --build
# http://localhost:8000 에서 확인
```

이 방식의 장점은 의존성 버전, OS, 런타임 차이를 모두 컨테이너로 격리한다는 것입니다. "제 환경에서는 되는데요"라는 대화를 원천적으로 차단합니다.

### 롤백 전략

배포가 실패했을 때 빠르게 복구할 수 있는 계획이 있어야 합니다. 포트폴리오에서는 복잡한 롤백 시스템이 필요 없습니다. Git 기반의 단순한 접근으로 충분합니다.

```bash
# 직전 정상 버전으로 롤백
git log --oneline -5        # 정상 커밋 해시 확인
git revert HEAD --no-edit    # 새 커밋으로 되돌리기
git push origin main         # 자동 배포 트리거
```

또는 대부분의 PaaS는 대시보드에서 직접 롤백을 지원합니다:

- **Render**: Dashboard → Manual Deploy → 이전 커밋 선택
- **Vercel**: Deployments 탭 → 이전 배포 → Redeploy
- **Railway**: Deployments → Rollback 버튼

README에 "배포 실패 시 `git revert HEAD`로 복구" 한 줄만 있어도, 이 프로젝트가 운영을 고려한 프로젝트라는 인상을 줍니다.

### 배포 자동화의 단계별 접근

처음부터 완벽한 CI/CD를 구축할 필요는 없습니다. 단계별로 자동화 수준을 높이는 접근이 현실적입니다.

| 단계 | 자동화 수준 | 설정 예상 시간 | 효과 |
| --- | --- | --- | --- |
| 1 | 수동 배포 (CLI) | 0분 | 배포 경험 확보 |
| 2 | Git push → 자동 배포 | 15분 | 반복 비용 제거 |
| 3 | PR에 테스트 추가 | 30분 | 배포 전 검증 |
| 4 | 헬스체크 + 알림 | 20분 | 장애 조기 발견 |
| 5 | 스테이징 환경 추가 | 45분 | 안전한 검증 환경 |

포트폴리오 프로젝트라면 3단계까지만 설정해도 충분합니다. 4-5단계까지 설정했다면 면접에서 "운영 경험"을 구체적으로 설명할 수 있는 근거가 됩니다. 특히 헬스체크와 알림까지 설정한 프로젝트는 신입 개발자 포트폴리오에서 매우 드물게 돋보입니다.

실제로 이 단계를 방법대로 밟아가면, 아직 배포 경험이 없는 사람도 두 시간 이내에 3단계까지 도달할 수 있습니다. 가장 중요한 것은 첫 배포를 내보내는 것이고, 나머지는 조금씩 개선하면 됩니다.

배포 자동화를 면접에서 설명할 때는 단순히 "배포를 자동화했습니다"라고 말하는 것보다, "처음에는 수동으로 배포하다가, PR 테스트를 추가하고, 헬스체크까지 설정했습니다"라고 과정을 설명하는 것이 훨씬 설득력 있습니다. 과정을 보여 주면 "문제를 인식하고 개선할 줄 아는 사람"이라는 신호를 줍니다.
## 처음 질문으로 돌아가기

- **포트폴리오 프로젝트에서 공개 URL이 왜 필수에 가까울까요?**
  - 로컬에서만 동작하는 코드는 증거가 되지 않습니다. 공개 URL이 있어야 검토자가 직접 확인할 수 있고, 그때 비로소 완성된 프로젝트로 읽힙니다.
- **호스팅 플랫폼은 화려함보다 어떤 기준으로 골라야 할까요?**
  - 반복 가능성, 저비용, 운영 단순성이 기준입니다. 화려한 인프라보다 동일한 절차로 다시 배포할 수 있는지가 더 중요합니다.
- **시크릿과 환경 변수는 왜 코드가 아니라 배포 환경에서 관리해야 할까요?**
  - 코드에 시크릿을 넣으면 저장소 공개 시 노출됩니다. 배포 환경의 환경 변수로 분리하면 보안과 운영 유연성을 동시에 확보할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Portfolio Project 101 (1/10): 포트폴리오 프로젝트란 무엇인가](./01-what-is-a-portfolio-project.md)
- [Portfolio Project 101 (2/10): 좋은 프로젝트의 조건](./02-traits-of-a-good-project.md)
- [Portfolio Project 101 (3/10): README 작성](./03-writing-the-readme.md)
- [Portfolio Project 101 (4/10): 데모 만들기](./04-building-the-demo.md)
- **배포하기 (현재 글)**
- 테스트와 문서화 (예정)
- 기술적 의사결정 기록 (예정)
- 블로그 글로 정리하기 (예정)
- 면접에서 설명하기 (예정)
- 포트폴리오 개선 체크리스트 (예정)

<!-- toc:end -->

## 참고 자료

- [Fly.io Docs](https://fly.io/docs/)
- [Render Docs](https://render.com/docs)
- [The Twelve-Factor App](https://12factor.net/)
- [Deployment Strategies - Martin Fowler](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/portfolio-project-101/ko)

Tags: Portfolio, Deploy, DevOps, Hosting, Beginner
