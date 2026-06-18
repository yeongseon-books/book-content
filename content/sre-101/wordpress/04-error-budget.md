---
episode: 4
language: ko
series: sre-101
title: "바이브코딩을 위한 SRE 기초 (4/10): Error Budget"
tags:
- SRE
- 바이브코딩
- ErrorBudget
- Reliability
- Release
- Risk
targets:
  wordpress: true
---

# 바이브코딩을 위한 SRE 기초 (4/10): Error Budget

이 글은 **바이브코딩을 위한 SRE 기초** 시리즈의 네 번째 글입니다. AI로 빠르게 기능을 만드는 팀에서 "지금 배포해도 되나요?"라는 질문은 늘 긴장을 낳습니다. 에러 버짓은 그 긴장을 숫자로 바꿔서, 감정 대신 데이터로 배포 결정을 내리게 해 주는 도구입니다.

---

바이브코딩 팀에서 가장 자주 생기는 갈등 중 하나는 이런 모양입니다.

개발자: "새 기능 완성됐으니까 오늘 배포합시다." 운영 담당자: "지난주에 배포했다가 장애 났잖아요, 좀 더 지켜봅시다." 개발자: "그때랑 다른데요." 운영 담당자: "그래도 불안하네요."

이 대화에서 두 사람은 같은 서비스를 보면서 완전히 다른 판단을 내립니다. 에러 버짓이 없기 때문입니다. 에러 버짓이 있으면 이 대화가 달라집니다. "이번 달 에러 버짓의 35%를 소진했으니까 배포 가능합니다" 또는 "버짓의 85%를 소진했으니 이번 배포는 다음 주로 미룹니다"라고 숫자로 이야기할 수 있습니다.

AI로 코드를 빠르게 만들수록 배포 빈도도 높아집니다. 배포가 잦을수록 에러 버짓이 빠르게 소진됩니다. 바이브코딩 팀에서 에러 버짓을 관리하지 않으면, 출시 속도와 안정성 사이의 충돌은 매번 감정 싸움으로 끝납니다.

> 에러 버짓은 목표와 현실 사이에서 팀이 감수하기로 한 실패 여유분이며, 그 숫자가 릴리스 행동을 바꿔야 의미가 있습니다.

## 이 글에서 다룰 문제

- 에러 버짓은 왜 속도와 안정성 사이의 공통 언어가 될까요?
- SLO를 세운 뒤 허용 가능한 실패 범위는 어떻게 계산할까요?
- 누적 소진량과 burn rate는 왜 다른 질문에 답할까요?
- 바이브코딩 팀에서 에러 버짓 정책을 처음 만들 때 어떻게 시작할까요?
- AI 코드 배포 빈도가 높을 때 에러 버짓을 어떻게 운영해야 할까요?

## 에러 버짓 계산하기

에러 버짓은 SLO에서 직접 나옵니다. 30일간 99.9% 가용성을 목표로 한다면, 0.1%만큼의 실패가 허용됩니다. 월간 100만 요청이라면 1,000번의 에러가 허용되는 것입니다.

```python
def calculate_error_budget(total_requests, target_availability, current_errors):
    allowed_errors = total_requests * (1 - target_availability)
    remaining_errors = allowed_errors - current_errors
    spent_ratio = current_errors / allowed_errors if allowed_errors > 0 else 0

    status = "HEALTHY"
    if spent_ratio >= 1.0:
        status = "EXHAUSTED"
    elif spent_ratio >= 0.8:
        status = "CRITICAL"
    elif spent_ratio >= 0.5:
        status = "WARNING"

    return {
        "allowed_errors": allowed_errors,
        "current_errors": current_errors,
        "remaining_errors": remaining_errors,
        "spent_ratio": spent_ratio,
        "status": status
    }

# 예시: 월간 100만 요청, 99.9% 목표, 현재 800개 에러
result = calculate_error_budget(1_000_000, 0.999, 800)
```

## 버짓 상태별 배포 정책

에러 버짓의 진짜 가치는 계산이 아니라, 그 숫자가 팀의 행동을 바꾸는 데 있습니다.

| 버짓 상태 | 소진 비율 | 행동 방향 | 바이브코딩 팀 예시 |
| --- | --- | --- | --- |
| 버짓 남음 | 50% 이하 | 공격적 배포, 실험 기능 출시 | AI로 만든 새 기능 자유롭게 배포 |
| 버짓 경계 | 50~80% | 추가 리뷰, 테스트 강화 | 카나리 배포 필수, 로그 점검 강화 |
| 버짓 초과 | 80% 이상 | 배포 freeze, 안정화 작업 우선 | hotfix만 허용, 기술 부채 제거 |
| 버짓 소진 | 100% 이상 | 모든 배포 중단, 포스트모템 | 임시 운영 체제, 원인 분석 의무화 |

## Burn Rate: 지금 어떤 속도로 타고 있나

누적 소진량만 보면 조기 경고를 놓칠 수 있습니다. 이번 달 버짓이 30%밖에 소진되지 않았어도 지난 1시간 동안 비정상적으로 빠르게 소진되고 있다면 대응이 늦어집니다.

burn rate는 "현재 속도로 가면 언제 버짓이 바닥나는가"를 보여 줍니다. burn rate = 1이면 정확히 월말에 바닥납니다. burn rate = 14.4라면 약 2일 만에 바닥납니다.

```python
# PromQL: Fast burn 알림 (1시간 윈도우에서 14.4배 속도 초과)
# (현재 에러율) > (14.4 * SLO 허용 에러율)
# 예: SLO 0.1% 기준이면 현재 에러율 > 1.44%일 때 즉시 알림
```

## Before / After: 에러 버짓 도입 전후

| 상황 | 에러 버짓 전 | 에러 버짓 후 |
| --- | --- | --- |
| 배포 결정 | "느낌상 괜찮을 것 같아요" | "버짓 35% 소진, 배포 가능" |
| 장애 후 반응 | "이번엔 진짜 조심해야 해" 감정적 대응 | "버짓 80% 소진, 배포 동결 정책 발동" |
| 속도 vs 안정성 갈등 | 매번 의견 충돌 | 버짓 상태가 기준이 되어 논쟁 없음 |
| 야간 호출 | 매번 판단이 다름 | 버짓 소진 속도 기준 알림으로 일관성 확보 |
| 팀 문화 | 장애 나면 누가 잘못했나 탐색 | 버짓 소진 원인 분석, 학습 중심 |

## 바이브코딩에서 자주 하는 실수

| 실수 | 왜 문제인가 | 개선 방법 |
| --- | --- | --- |
| 에러 버짓을 계산만 하고 정책 없음 | 숫자는 있지만 행동이 바뀌지 않음 | 소진 비율별 행동 규칙을 팀이 합의 |
| 누적 소진량만 봄 | 빠른 소진 상황을 놓쳐 대응이 늦어짐 | burn rate 알림을 별도로 설정 |
| 에러 버짓을 비난 도구로 사용 | 팀이 숫자를 숨기거나 방어적으로 행동 | 학습과 의사결정 도구로 문화 정착 |
| AI 배포 후 버짓 추적 안 함 | 빠른 배포 사이클에서 버짓이 모르는 새 소진 | 배포 이벤트를 버짓 대시보드에 표시 |

## AI 팁: 에러 버짓 관련 자동화 요청하기

**버짓 계산 함수 요청**: "SLO 목표율, 측정 기간, 현재 에러 수를 입력받아 허용 에러 수, 소진 비율, 상태(HEALTHY/WARNING/CRITICAL/EXHAUSTED)를 반환하는 Python 함수를 만들어줘"

**burn rate 알림 요청**: "Prometheus에서 에러율이 1시간 동안 SLO 허용 에러율의 14.4배를 초과할 때 PagerDuty로 알림을 보내는 alerting rule YAML을 만들어줘"

**배포 정책 자동화 요청**: "에러 버짓 소진 비율에 따라 배포를 허용/검토/차단하는 GitHub Actions 스크립트를 만들어줘. Prometheus API에서 현재 소진 비율을 읽어와서 판단해줘"

## 운영 체크리스트

- [ ] SLO에서 에러 버짓을 계산할 수 있다.
- [ ] 누적 소진 비율과 burn rate를 함께 본다.
- [ ] review와 freeze 정책이 문서화되어 있다.
- [ ] 버짓 상태가 실제 릴리스 판단에 반영된다.
- [ ] 버짓을 비난 도구가 아니라 운영 기준으로 사용한다.

## 처음 질문으로 돌아가기

- **에러 버짓은 왜 속도와 안정성 사이의 공통 언어가 될까요?**
  - 에러 버짓은 "어느 정도 실패까지 감수한다"고 미리 합의된 수치입니다. 버짓이 있으면 "지금 배포해도 되나요?"라는 질문이 "현재 버짓 소진이 35%이니 배포 가능합니다"라는 데이터 기반 답변으로 바뀝니다.
- **AI 코드 배포 빈도가 높을 때 에러 버짓을 어떻게 운영해야 할까요?**
  - AI로 코드를 자주 만들고 배포할수록 burn rate를 더 주의 깊게 봐야 합니다. 각 배포 후 1시간 동안의 에러율 변화를 추적하고, burn rate가 급등하면 자동 롤백 트리거를 걸어 두는 것이 좋습니다.
- **누적 소진량과 burn rate는 왜 다른 질문에 답할까요?**
  - 누적 소진량은 "지금까지 얼마를 썼나(상태판)"를 보여 주고, burn rate는 "지금 얼마나 빠르게 타고 있나(경고등)"를 보여 줍니다. 누적량이 낮아도 burn rate가 높으면 빠른 대응이 필요합니다.

## 정리

에러 버짓은 목표와 현실 사이의 허용 가능한 실패 범위를 숫자로 드러내는 도구입니다. 바이브코딩으로 빠르게 배포하는 팀일수록 에러 버짓을 배포 결정에 연결해야 출시 속도와 안정성을 함께 지킬 수 있습니다.

다음 글에서는 모니터링을 다룹니다. 지금 움직여야 하는지 바로 판단하게 만드는 측정 설계 방법을 소개합니다.

## 참고 자료

- [Embracing Risk - Google SRE Book](https://sre.google/sre-book/embracing-risk/)
- [Alerting on SLOs - Google SRE Workbook](https://sre.google/workbook/alerting-on-slos/)
- [Error Budgets - Atlassian](https://www.atlassian.com/incident-management/kpis/error-budget)
- [Error Budget Policy - Google](https://sre.google/workbook/error-budget-policy/)
- [SRE 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/sre-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 SRE 기초 (1/10): SRE란 무엇인가?](./01-what-is-sre.md)
- [바이브코딩을 위한 SRE 기초 (2/10): Reliability](./02-reliability.md)
- [바이브코딩을 위한 SRE 기초 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- **바이브코딩을 위한 SRE 기초 (4/10): Error Budget (현재 글)**
- [바이브코딩을 위한 SRE 기초 (5/10): Monitoring](./05-monitoring.md)
- [바이브코딩을 위한 SRE 기초 (6/10): Incident Response](./06-incident-response.md)
- [바이브코딩을 위한 SRE 기초 (7/10): Postmortem](./07-postmortem.md)
- [바이브코딩을 위한 SRE 기초 (8/10): Toil 줄이기](./08-reducing-toil.md)
- [바이브코딩을 위한 SRE 기초 (9/10): Capacity Planning](./09-capacity-planning.md)
- [바이브코딩을 위한 SRE 기초 (10/10): 운영 가능한 시스템 만들기](./10-building-operable-systems.md)

<!-- toc:end -->

Tags: SRE, 바이브코딩, ErrorBudget, Reliability, Release, Risk
