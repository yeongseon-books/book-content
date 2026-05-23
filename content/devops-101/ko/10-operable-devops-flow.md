---
series: devops-101
episode: 10
title: "DevOps 101 (10/10): 운영 가능한 DevOps 흐름"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DevOps
  - DORA
  - Strategy
  - Capstone
  - Engineering
seo_description: 코드부터 포스트모템까지를 하나의 흐름으로 묶는 DevOps 운영 모델을 설명합니다.
last_reviewed: '2026-05-12'
---

# DevOps 101 (10/10): 운영 가능한 DevOps 흐름

이 글은 DevOps 101 시리즈의 마지막 글입니다.

![DevOps 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/10/10-01-diagram.ko.png)
*DevOps 101 10장 흐름 개요*
> 운영 가능한 DevOps의 핵심은 배포와 모니터링, 장애 대응까지가 하나의 피드백 루프를 이루는 것입니다.

## 먼저 던지는 질문

- CI, CD, 모니터링, 장애 대응이 각각 있는데도 팀 전체 속도가 느린 이유는 무엇일까요?
- DevOps를 도구 목록이 아니라 하나의 운영 흐름으로 보려면 어떤 그림이 필요할까요?
- DORA 4지표는 무엇을 측정하며 왜 함께 봐야 할까요?

## 왜 중요한가

도구를 하나씩 붙이는 것만으로는 DevOps가 완성되지 않습니다. CI는 성공하는데 배포는 느리고, 배포는 자주 하는데 장애에서 배우지 못한다면 도구는 있어도 흐름은 없는 상태입니다.

운영 가능한 DevOps는 개별 최적화보다 연결을 봅니다. build, deploy, monitor, incident, postmortem이 서로의 입력이 될 때 속도와 안정성을 함께 끌어올릴 수 있습니다.

> 측정되지 않는 것은 개선되지 않습니다.

## 한눈에 보는 개념

이 그림의 핵심은 마지막 화살표입니다. 포스트모템이 코드와 절차로 돌아오지 않으면, 앞선 모든 자동화는 선형 파이프라인일 뿐 학습 루프가 되지 못합니다.

## 핵심 용어

- **DORA metrics**: Google 연구에서 널리 알려진 네 가지 DevOps 지표입니다.
- **Deploy frequency**: 얼마나 자주 배포하는지를 나타내는 지표입니다.
- **Lead time for changes**: 변경이 merge에서 production까지 가는 데 걸린 시간입니다.
- **Change failure rate**: 장애를 만든 배포의 비율입니다.
- **MTTR**: 장애에서 복구하는 데 걸린 평균 시간입니다.
- **Ritual**: 분명한 목적을 가진 반복 팀 미팅입니다.

DevOps가 추상적으로 느껴질 때는 이 용어들을 흐름 위에 올려 보면 좋습니다. 팀이 어디서 느리고 어디서 불안정한지 숫자와 리듬으로 읽을 수 있기 때문입니다.

## 전환 전후

**Before**: build, deploy, and monitoring run *separately* and no one looks at the *whole picture*.

도구는 각각 존재하지만 연결이 없습니다. 그래서 같은 문제가 매번 다른 모습으로 다시 나타나고, 팀은 부분 최적화만 반복하게 됩니다.

**After**: a *single dashboard* shows the *four DORA metrics* and the team reviews it weekly.

흐름이 잡힌 팀은 전체 그림을 함께 봅니다. 배포 수, 리드 타임, 실패율, 복구 시간이 같은 대화 안에서 다뤄지기 때문에 속도와 안정성을 동시에 조정할 수 있습니다.

## 흐름을 만드는 5단계

### 1단계 — 한 페이지에 흐름 그리기

많은 팀이 자기 단계만 잘 압니다. 그래서 먼저 해야 할 일은 자동화 추가보다, 전체 흐름을 같은 종이에 올려 모두가 보는 것입니다.

```text
On a single sheet of paper:
PR -> CI -> staging -> prod -> alert -> on-call -> postmortem
For each step, write the *owner* and the *tool*.
```

### 2단계 — DORA 측정 시작

자동 수집이 완벽히 준비되기 전이라도 측정은 시작할 수 있습니다. 처음에는 손으로 적어도 됩니다. 중요한 것은 숫자를 보기 시작하는 습관입니다.

```python
# 가장 간단한 시작: 배포마다 GitHub Release를 생성합니다.
# 이 네 가지 숫자를 매주 수동으로 추적하는 것만으로도 충분합니다.
metrics = {
    "deploy_frequency": "5 per week",
    "lead_time": "6 hours average",
    "change_failure_rate": "8%",
    "mttr": "22 minutes",
}
```

### 3단계 — 주간 의식: 배포 리뷰 (30분)

지표는 읽지 않으면 쌓이기만 합니다. 짧고 반복적인 주간 리뷰는 흐름을 살아 있게 만드는 최소한의 팀 리듬입니다.

```text
- Last week's deploy count
- One incident summary from last week
- This week's risky deploys
```

### 4단계 — 월간 의식: 포스트모템 읽기 (60분)

개별 장애보다 중요한 것은 반복 패턴입니다. 포스트모템을 함께 읽어야 시스템 결함이 팀의 다음 변경으로 이어집니다.

```text
- Read the month's postmortems together
- Track the action-item completion rate
- When patterns appear, change the *system*
```

### 5단계 — 분기마다 다음 단계 고르기

DevOps 흐름은 한 번 설계하고 끝나는 체계가 아닙니다. 팀 규모와 병목이 바뀌면 다음 학습 주제와 도구 구성도 함께 바뀌어야 합니다.

```text
- Pick the next learning track
- Add or remove tools
- Propose org-structure changes
```

## 도라 지표를 실제 운영 대화로 바꾸는 법

DORA 4지표는 숫자를 모으는 것으로 끝나면 금방 형식이 됩니다. 핵심은 각 숫자가 어떤 운영 질문으로 이어지는지 팀이 함께 알고 있는가입니다. 예를 들어 배포 빈도는 "우리가 자주 배포하느냐"보다 "작게 나눠 배포할 수 있을 만큼 변경 단위를 관리하고 있느냐"라는 질문으로 읽는 편이 더 유용합니다.

```text
Deploy frequency      -> 변경을 충분히 작게 나누고 있는가
Lead time             -> 리뷰/빌드/승인 중 어디가 병목인가
Change failure rate   -> 어떤 종류의 변경이 자주 사고를 내는가
MTTR                  -> 탐지, 판단, 복구 중 어디가 가장 느린가
```

이렇게 해석해야 숫자가 회고 자료가 아니라 다음 액션의 입력으로 바뀝니다.

## 90일 운영 개선 계획 예시

마지막 장에서 가장 필요한 것은 거대한 비전보다 실행 가능한 다음 90일 계획입니다. 예를 들면 작은 팀은 아래처럼 잡을 수 있습니다.

```text
1-30일   PR 필수 체크 정리, staging 스모크 테스트 추가, runbook 3개 작성
31-60일  RED 대시보드 구축, alert -> runbook 링크 연결, DORA 수기 집계 시작
61-90일  배포 리뷰/포스트모템 리듬 고정, 가장 잦은 실패 유형 1개 자동화
```

이 계획이 좋은 이유는 도구 도입보다 루프 단축에 직접 연결되기 때문입니다. 팀이 이미 가진 시스템을 더 자주 보고, 더 빨리 복구하고, 더 작은 변경으로 움직이게 만드는 항목만 남겨 두는 것이 중요합니다.

## 이 코드에서 먼저 봐야 할 점

- 지표는 처음부터 자동 수집하지 않아도 됩니다. 중요한 것은 측정을 시작하는 일입니다.
- 팀 리듬은 길고 무거운 행사보다 짧고 반복적인 의식이 더 잘 유지됩니다.
- 피드백 루프가 닫힐 때 팀은 비로소 장애에서 학습하기 시작합니다.

좋은 DevOps 흐름은 자동화 수가 아니라, 팀이 같은 데이터를 같은 주기로 읽고 실제 변경으로 연결하는 힘에서 만들어집니다.

## 운영 성숙도 레벨

DevOps 성숙도는 도구의 수가 아니라, 자동화와 피드백 루프의 깊이로 판단합니다. 아래 표는 네 단계 성숙도를 정리한 것입니다.

| 레벨 | 특징 | 자동화 수준 |
| --- | --- | --- |
| 0 | 수동 배포, SSH로 직접 접속, 로그는 서버에서 grep | 없음 |
| 1 | CI 존재, 테스트 자동화, 배포는 수동 클릭 | 빌드 자동화 |
| 2 | CD 파이프라인, 중앙 로그 수집, 기본 메트릭 | 배포 자동화 |
| 3 | 자동 롤백, SLO 기반 알림, 포스트모템에서 학습 | 복구 자동화 |

대부분의 팀은 레벨 1-2 사이에 있습니다. 레벨 3은 성숙한 플랫폼 팀의 목표지이고, 작은 팀은 레벨 2를 먼저 안정적으로 유지하는 편이 좋습니다. 중요한 것은 현재 레벨을 정확히 아는 것입니다.

## 데브옵스 메트릭 (도라 4지표)

Google DORA 연구는 네 가지 핑심 지표를 제시했습니다. 이 지표들은 속도와 안정성의 균형을 함께 보여줍니다.

### 1. Deployment Frequency (배포 빈도)

얼마나 자주 배포하는지 측정합니다. 높을수록 변경을 작게 나눈다는 의미입니다.

```text
Elite: Multiple deploys per day
High: Once per day to once per week
Medium: Once per week to once per month
Low: Fewer than once per month
```

### 2. Lead Time for Changes (변경 리드 타임)

코드가 merge된 후 production에 도달하기까지 걸리는 시간입니다.

```text
Elite: Less than 1 hour
High: Less than 1 day
Medium: 1 day to 1 week
Low: More than 1 week
```

### 3. Change Failure Rate (변경 실패율)

배포가 장애를 일으킨 비율입니다. 낮을수록 테스트와 리뷰 품질이 높다는 의미입니다.

```text
Elite: 0-15%
High: 16-30%
Medium: 31-45%
Low: More than 45%
```

### 4. Mean Time to Recovery (MTTR) (평균 복구 시간)

장애가 발생한 후 복구까지 걸리는 평균 시간입니다.

```text
Elite: Less than 1 hour
High: Less than 1 day
Medium: 1 day to 1 week
Low: More than 1 week
```

이 네 지표는 함께 봐야 합니다. 배포 빈도만 높이고 실패율이 높으면 불안정한 빠른 배포입니다. 반대로 실패율은 낮지만 리드 타임이 길면 안전하지만 느린 배포입니다.

## 파이썬 배포 빈도 측정 예제

배포 때마다 GitHub Release를 만들고, 이를 집계하는 간단한 스크립트입니다.

```python
import httpx
from datetime import datetime, timedelta
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "myorg/myapp"

async def get_deploy_frequency(days=7):
    """Calculate deployment frequency over the last N days"""
    url = f"https://api.github.com/repos/{REPO}/releases"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        releases = response.json()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_deploys = [
        r for r in releases
        if datetime.fromisoformat(r["published_at"].replace("Z", "+00:00")) > cutoff_date
    ]
    
    frequency = len(recent_deploys) / days
    
    return {
        "period_days": days,
        "total_deploys": len(recent_deploys),
        "deploys_per_day": round(frequency, 2),
        "classification": classify_frequency(frequency)
    }

def classify_frequency(deploys_per_day):
    """Map to DORA performance levels"""
    if deploys_per_day >= 1:
        return "Elite"
    elif deploys_per_day >= 0.14:  # ~1 per week
        return "High"
    elif deploys_per_day >= 0.03:  # ~1 per month
        return "Medium"
    else:
        return "Low"

# Usage
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(get_deploy_frequency(30))
    print(f"Deploy Frequency (last 30 days): {result}")
```

이 스크립트는 GitHub Release API를 통해 최근 배포 빈도를 계산하고 DORA 레벨로 분류합니다. CI에서 주기적으로 실행하면 팀의 배포 속도를 추적할 수 있습니다.

## 자주 하는 실수 5가지

1. **도구부터 도입하는 실수**입니다. 흐름이 없으면 도구는 연결되지 않은 섬이 됩니다.
2. **DORA 네 지표 중 하나만 보는 실수**입니다. 네 개를 함께 봐야 속도와 안정성의 균형이 보입니다.
3. **포스트모템을 읽지 않는 실수**입니다. 문서는 남아도 학습은 남지 않습니다.
4. **의식을 길고 형식적으로 만드는 실수**입니다. 짧고 데이터 중심이어야 지속됩니다.
5. **개선 책임자를 두지 않는 실수**입니다. 흐름에도 owner가 필요합니다.

## 실무에서는 이렇게 이어집니다

성숙한 조직은 플랫폼 팀을 두고, 내부 개발자 플랫폼을 통해 이 흐름 자체를 셀프서비스로 제공합니다. 새 서비스가 기본 CI, 배포, 관측성, 문서 템플릿을 자동으로 상속받게 만드는 식입니다.

하지만 작은 팀이라면 한 장짜리 흐름, 손으로 적는 DORA 지표, 짧은 주간·월간 리뷰만으로도 충분히 큰 변화를 만들 수 있습니다. DevOps의 핵심은 거대한 시스템보다 학습 리듬에 있습니다.

## 시니어 엔지니어는 이렇게 봅니다

- 흐름 자체가 아키텍처입니다.
- 지표가 없으면 토론은 쉽게 의견 싸움이 됩니다.
- 작은 의식이 큰 변화를 더 오래 끌고 갑니다.
- 플랫폼화는 규모가 커질수록 중요해집니다.
- 학습은 끝나지 않으므로 다음 학습 트랙을 의도적으로 골라야 합니다.

## 체크리스트

- [ ] 코드부터 포스트모템까지의 전체 흐름이 한 그림에 있습니다.
- [ ] 팀이 DORA 4지표를 매주 확인합니다.
- [ ] 주간과 월간 운영 의식이 일정에 잡혀 있습니다.
- [ ] 흐름의 개선을 책임지는 owner가 분명합니다.

## 연습 문제

1. 팀의 Code -> Postmortem 흐름을 한 장으로 그려 보세요.
2. 한 주 동안 DORA 4지표를 손으로 측정해 보세요.
3. 30분짜리 주간 배포 리뷰를 한 번 직접 운영해 보세요.

## 정리 및 다음 단계

DevOps 101 시리즈는 여기서 마무리입니다. 핵심은 하나입니다. DevOps는 도구의 집합이 아니라, 팀이 빠르게 배포하고 장애에서 배우고 다시 시스템을 고치는 학습 루프입니다.

다음 학습 경로는 현재 팀의 병목에 따라 고르면 됩니다.

- **Observability 101** — 메트릭, 로그, trace를 함께 읽는 방법
- **SRE 101** — SLO, SLI, error budget으로 신뢰성을 운영하는 방법
- **Kubernetes 101** — 컨테이너 오케스트레이션을 본격적으로 다루는 방법

DevOps는 결국 팀이 배우는 방식입니다. 이 감각을 잡았다면 이제 다음 도구보다 다음 학습 루프를 설계할 차례입니다.

## 시리즈 종합: 운영 가능한 데브옵스 시스템 설계도

마지막 단계에서 중요한 것은 개별 기술이 아니라 연결 구조입니다. CI, CD, IaC, 컨테이너, 관측성, on-call이 따로 존재하면 팀은 바쁘지만 느립니다. 반대로 각 단계가 다음 단계의 입력으로 이어지면 팀은 같은 인원으로 더 자주, 더 안전하게 배포할 수 있습니다.

### 플랫폼 엔지니어링 관점 아키텍처

```text
Developer -> IDP Portal -> CI Templates -> Artifact Registry
          -> GitOps Controller -> Runtime Platform
          -> Metrics/Logs/Traces -> Alerting -> Incident Response
          -> Postmortem Actions -> Backlog -> Developer
```

위 흐름은 학습 루프가 닫힌 구조를 보여 줍니다. 포스트모템 결과가 백로그와 템플릿 개선으로 다시 흘러가야 운영 가능한 DevOps가 됩니다.

### IDP(Internal Developer Platform) 구성요소 표

| 구성요소 | 역할 | 최소 기능 |
| --- | --- | --- |
| Service Catalog | 서비스 메타데이터 관리 | owner, repo, runbook 링크 |
| Golden Templates | 표준 프로젝트 생성 | CI, Dockerfile, 기본 모니터링 |
| Deployment Abstraction | 배포 단순화 | 환경별 승격/롤백 버튼 |
| Policy Engine | 규정 자동 강제 | 필수 체크, 보안 게이트 |
| Observability Hub | 통합 관측성 | RED 대시보드, 알림 라우팅 |

### DORA 운영 해석 가이드

| 지표 | 주간 질문 | 개선 레버 |
| --- | --- | --- |
| Deploy Frequency | 왜 배포가 묶음이 커졌는가 | PR 크기 축소, 파이프라인 속도 개선 |
| Lead Time | 가장 긴 대기 단계는 어디인가 | 승인 정책 단순화, 병렬 테스트 |
| Change Failure Rate | 어떤 변경 유형이 실패하는가 | 프리플라이트 테스트, 카나리 강화 |
| MTTR | 탐지-판단-복구 중 병목은 어디인가 | 알림 품질, 런북 보강, 롤백 자동화 |

### 90일 플랫폼 실행 계획

```yaml
phase_1_30d:
  - create_service_catalog
  - standardize_ci_template
  - define_dora_collection
phase_2_60d:
  - rollout_gitops_for_stage
  - add_security_gate_sast_dast
  - publish_runbook_baseline
phase_3_90d:
  - self_service_deploy_for_teams
  - monthly_postmortem_review
  - automate_top_incident_prevention
```

### 운영 성숙도 점검표

| 질문 | 예/아니오 |
| --- | --- |
| 신규 서비스가 하루 안에 표준 파이프라인을 갖추는가 |  |
| 배포 실패 시 10분 내 롤백 경로가 준비되어 있는가 |  |
| 알림에서 런북까지 한 번에 이동 가능한가 |  |
| 월간 포스트모템 액션 완료율을 추적하는가 |  |

### 종합 결론

운영 가능한 DevOps는 기술 도입 결과가 아니라 시스템 설계 결과입니다. 표준화된 진입점, 측정 가능한 지표, 짧은 학습 루프, 책임이 분명한 운영 리듬이 함께 있을 때 비로소 지속 가능한 속도가 만들어집니다. 플랫폼 엔지니어링은 이 구조를 팀 전체에 확장하는 방법입니다.

### 플랫폼 엔지니어링 도입 시 흔한 오해

플랫폼 팀을 만든다고 DevOps가 자동 완성되지는 않습니다. 플랫폼의 목적은 팀을 대신해 배포하는 것이 아니라, 각 팀이 안전한 기본값을 빠르게 재사용하도록 돕는 것입니다.

| 오해 | 실제 원칙 |
| --- | --- |
| 플랫폼 팀이 모든 운영을 담당한다 | 플랫폼은 셀프서비스 경로를 제공한다 |
| 템플릿은 자유를 제한한다 | 반복 실수를 줄이는 안전 기본값이다 |
| 지표는 보고용이다 | 우선순위 결정을 위한 운영 입력이다 |

따라서 IDP 성공 기준은 기능 수가 아니라 신규 팀 온보딩 시간, 표준 파이프라인 채택률, 장애 재발률 감소 같은 운영 결과로 측정해야 합니다.

## 0-5분
1. SEV 판정 (SEV1/SEV2)
2. incident 채널 개설
3. 최근 배포 커밋 확인

## 5-10분
1. canary/최근 릴리스 롤백 시도
2. 에러율, p95, DB 연결수 확인
3. 고객 영향 범위 요약 공지

## 10-20분
1. 임시 완화 조치 적용
2. 영구 수정 owner 지정
3. postmortem 일정 예약
```

운영에서는 "잘 아는 사람"보다 "같은 순서를 따르는 팀"이 더 빠르게 복구합니다. 그래서 runbook은 설명 문서가 아니라 실행 문서여야 하며, 경보에서 한 번에 열 수 있어야 합니다.

## 처음 질문으로 돌아가기

- **CI, CD, 모니터링, 장애 대응이 각각 있는데도 팀 전체 속도가 느린 이유는 무엇일까요?**
  - 이 글은 도구가 따로 존재해도 `build -> deploy -> monitor -> incident -> postmortem`이 서로 연결되지 않으면 팀은 부분 최적화만 반복한다고 설명합니다. 포스트모템 결과가 다시 코드와 절차로 돌아오지 않으면, 자동화가 있어도 학습 루프는 닫히지 않아 전체 속도가 계속 느립니다.
- **DevOps를 도구 목록이 아니라 하나의 운영 흐름으로 보려면 어떤 그림이 필요할까요?**
  - 본문은 한 장짜리 흐름에 `PR -> CI -> staging -> prod -> alert -> on-call -> postmortem`을 그리고 각 단계의 owner와 tool을 적으라고 제안합니다. 마지막에는 IDP, 서비스 카탈로그, 관측성 허브까지 이어지는 구조를 보여 주며, 모든 단계가 다음 단계의 입력이 되는 그림이 필요하다고 정리합니다.
- **DORA 4지표는 무엇을 측정하며 왜 함께 봐야 할까요?**
  - DORA 4지표는 배포 빈도, 변경 리드 타임, 변경 실패율, MTTR을 측정해 속도와 안정성을 함께 읽게 해 줍니다. 배포 빈도만 높고 실패율도 높으면 불안정한 팀이고, 실패율은 낮아도 리드 타임이 길면 지나치게 느린 팀이므로 네 지표를 함께 봐야 실제 병목을 해석할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [DevOps 101 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [DevOps 101 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [DevOps 101 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [DevOps 101 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [DevOps 101 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- [DevOps 101 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- [DevOps 101 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- [DevOps 101 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- **운영 가능한 DevOps 흐름 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [DORA Research Program](https://dora.dev/)
- [Google SRE Workbook](https://sre.google/workbook/table-of-contents/)
- [Accelerate (book)](https://itrevolution.com/product/accelerate/)
- [Team Topologies](https://teamtopologies.com/)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)

Tags: DevOps, DORA, Strategy, Capstone, Engineering
