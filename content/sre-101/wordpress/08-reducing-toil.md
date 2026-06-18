---
title: "바이브코딩을 위한 SRE 기초 (8/10): Toil 줄이기"
series: sre-101
episode: 8
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - SRE
  - Toil
  - Automation
  - Operations
---

# 바이브코딩을 위한 SRE 기초 (8/10): Toil 줄이기

이 글은 "바이브코딩을 위한 SRE 기초" 시리즈의 8번째 글입니다.

---

바이브코딩에서 AI는 자동화 스크립트를 빠르게 만들어 줍니다. 그런데 무엇을 자동화해야 할지 모르면, 자동화가 오히려 복잡성을 추가합니다. 진짜 문제는 자동화 도구가 없는 것이 아니라, 팀이 매주 같은 수동 작업을 반복하면서도 그것이 없애야 할 Toil임을 인식하지 못하는 것입니다.

SRE에서 Toil은 단순한 귀찮은 작업이 아닙니다. 수동적이고, 반복적이고, 자동화할 수 있고, 전술적이며, 서비스 성장에 비례해 늘어나는 작업을 말합니다. 인증서 수동 갱신, 배포 후 매번 같은 점검 명령 실행, 서버 용량 부족 때마다 수동 스케일업 요청이 Toil의 전형적인 예입니다.

Google SRE 원칙은 Toil이 전체 업무의 50%를 넘지 않아야 한다고 말합니다. 넘기 시작하면 팀은 전략적 개선 대신 운영 유지에 모든 에너지를 쓰게 됩니다. AI가 스크립트를 빠르게 만들 수 있는 환경에서도, 어느 Toil부터 없애야 할지 우선순위를 잡는 것은 사람의 판단입니다.

> **핵심 인사이트:** Toil은 단순 반복 작업이 아니라 "자동화하지 않으면 서비스가 성장할수록 계속 늘어나는 작업"입니다. 주 빈도 × 작업 시간으로 점수를 매겨 우선순위를 정하고, 자동화 구축 시간이 6개월 내 회수되는 항목부터 시작하면 투자 대비 효과가 명확합니다.

## 이 글에서 다룰 문제

- Toil의 5가지 특성은 무엇인가요?
- 어떤 작업이 Toil이고 어떤 것이 엔지니어링 작업인가요?
- Toil 우선순위는 어떻게 정할까요?
- 자동화 투자 회수 시점은 어떻게 계산할까요?
- AI가 만든 자동화 코드에서 Toil 관점으로 확인할 것은 무엇인가요?

## Toil 줄이기 핵심 패턴

```python
# Toil 기록: 반복 작업을 가시화
def log_toil(name, freq_per_week, minutes_each, automatable=True):
    return {
        "name": name,
        "freq_per_week": freq_per_week,
        "minutes_each": minutes_each,
        "weekly_minutes": freq_per_week * minutes_each,
        "automatable": automatable,
    }

toil_items = [
    log_toil("인증서 수동 갱신",       freq_per_week=0.1, minutes_each=30),
    log_toil("배포 후 상태 점검",       freq_per_week=5,   minutes_each=10),
    log_toil("서버 스케일업 요청",      freq_per_week=2,   minutes_each=20),
    log_toil("DB 슬로우쿼리 수동 확인", freq_per_week=3,   minutes_each=15),
]

# Toil 비율: 전체 업무의 50% 초과 여부 확인
def toil_ratio(toil_minutes_per_week, total_work_minutes=2400):
    ratio = toil_minutes_per_week / total_work_minutes
    status = "위험" if ratio > 0.5 else ("경고" if ratio > 0.3 else "정상")
    return {"ratio": ratio, "status": status}
```

```python
# 우선순위 점수: 빈도 × 시간으로 자동화 순서 결정
def score(freq_per_week, minutes_each):
    return freq_per_week * minutes_each  # 높을수록 우선 자동화

# 자동화 손익분기점 계산
def break_even(saved_per_week_min, build_minutes):
    weeks = build_minutes / saved_per_week_min
    return {"break_even_weeks": weeks, "worthwhile": weeks < 26}  # 6개월 기준

# 예시: 배포 후 상태 점검 자동화
item = log_toil("배포 후 상태 점검", freq_per_week=5, minutes_each=10)
result = break_even(
    saved_per_week_min=item["weekly_minutes"],  # 50분/주 절약
    build_minutes=240,                           # 구축 4시간
)
# → break_even_weeks: 4.8주, worthwhile: True
```

```bash
# 자동화 예시: 인증서 갱신 Toil 제거
# Before: 매월 수동으로 certbot 명령 실행
# After: cron으로 자동화

# /etc/cron.d/certbot-renew
0 3 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"

# 상태 확인 자동화 (배포 후 수동 점검 제거)
#!/bin/bash
set -e
SERVICES=("api" "worker" "scheduler")
for svc in "${SERVICES[@]}"; do
    STATUS=$(curl -sf "https://internal/$svc/health" | jq -r '.status')
    [ "$STATUS" = "ok" ] || { echo "$svc unhealthy"; exit 1; }
done
echo "All services healthy"
```

## 변경 전후 비교

**Before: Toil이 쌓이는 팀**
```text
- 매주 50분: 배포 후 상태 점검 수동 실행
- 매월 30분: 인증서 수동 갱신
- 매주 40분: 서버 스케일업 티켓 처리
- Toil 비율 40%, 전략적 개선 시간 없음
- 서비스 성장하면 Toil도 함께 성장
```

**After: Toil을 줄인 팀**
```text
- 배포 후 상태 점검 → 파이프라인 자동화 (0분)
- 인증서 갱신 → cron 자동화 (0분)
- 스케일업 → 오토스케일링 설정 (0분)
- Toil 비율 15%, 엔지니어링 작업 시간 확보
- 서비스 성장해도 Toil은 제자리
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| Toil을 측정하지 않음 | 비율 초과해도 모름 | 주간 Toil 시간을 팀 지표로 기록 |
| 모든 반복 작업을 Toil로 오판 | 가치 있는 반복 작업도 있음 | 자동화 가능 + 성장 비례 여부 확인 |
| 자동화 ROI 계산 없이 시작 | 회수 안 되는 자동화에 시간 낭비 | 손익분기 26주(6개월) 기준 사용 |
| 자동화 후 모니터링 없음 | 자동화가 조용히 실패 | 자동화 결과에 경보 연결 |
| Toil 줄이기를 개인 책임으로 | 팀 전체의 Toil이 줄지 않음 | Toil 비율을 팀 OKR에 포함 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"배포 후 상태 점검 스크립트를 자동화해줘.
/health 엔드포인트 확인, 비정상 시 Slack 알림,
GitHub Actions 배포 워크플로우에 후속 단계로 통합,
실패 시 롤백 트리거 포함"

# AI 결과물 검증 체크포인트:
# - 자동화가 실패했을 때 경보가 울리는가?
# - 자동화 이전보다 실제로 수동 작업이 줄었는가?
# - 자동화 스크립트 자체가 새로운 Toil이 되지 않는가?
# - 손익분기 시점이 6개월 이내인가?
# - Toil 비율이 50% 미만으로 유지되는가?
```

## 운영 체크리스트

- [ ] 팀의 주간 Toil 시간을 측정하고 기록한다
- [ ] Toil 비율이 전체 업무의 50% 미만으로 유지된다
- [ ] 자동화 우선순위를 빈도 × 시간 점수로 결정한다
- [ ] 자동화 구축 전 손익분기 시점(6개월 기준)을 계산한다
- [ ] 자동화 결과에 경보가 연결되어 조용한 실패를 감지한다

## 처음 질문으로 돌아가기

- **Toil의 5가지 특성은?** 수동적(사람이 직접 실행), 반복적(같은 작업 반복), 자동화 가능(기계로 대체 가능), 전술적(서비스 개선 없음), 성장 비례(서비스가 커질수록 작업도 증가). 이 다섯 가지를 모두 만족해야 Toil입니다.
- **어떤 작업이 Toil이 아닌가?** 새로운 기능 설계, 성능 최적화 분석, 장애 근본 원인 분석은 반복적으로 보여도 Toil이 아닙니다. 엔지니어링 판단이 필요하고 서비스를 실제로 개선하는 작업은 가치 있는 반복입니다.
- **자동화 투자 회수는 어떻게 계산하는가?** 자동화 구축 시간 ÷ 주당 절약 시간 = 손익분기 주수. 배포 점검 자동화(구축 4시간, 절약 50분/주)는 약 5주 만에 회수됩니다. 6개월(26주) 이내 회수 가능한 항목부터 시작하세요.

## 정리

바이브코딩에서 AI가 자동화 스크립트를 빠르게 만들어 줘도, 어느 Toil부터 없애야 할지 판단하는 것은 팀의 몫입니다. 주간 Toil 시간을 측정하고, 빈도 × 시간으로 우선순위를 정하고, 손익분기 6개월 기준으로 자동화를 시작하세요. Toil 비율 50% 미만을 팀 지표로 유지하면 서비스가 성장해도 운영 부담이 함께 늘지 않습니다. 다음 글에서는 용량 계획을 다룹니다.

## 참고 자료

- [Eliminating Toil — Google SRE Book](https://sre.google/sre-book/eliminating-toil/)
- [SRE Workbook: Toil](https://sre.google/workbook/eliminating-toil/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/sre-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 SRE 기초 (1/10): SRE란 무엇인가?
- 바이브코딩을 위한 SRE 기초 (2/10): 신뢰성
- 바이브코딩을 위한 SRE 기초 (3/10): SLI, SLO, SLA
- 바이브코딩을 위한 SRE 기초 (4/10): 에러 예산
- 바이브코딩을 위한 SRE 기초 (5/10): 모니터링
- 바이브코딩을 위한 SRE 기초 (6/10): 장애 대응
- 바이브코딩을 위한 SRE 기초 (7/10): 포스트모템
- **바이브코딩을 위한 SRE 기초 (8/10): Toil 줄이기 (현재 글)**
- 바이브코딩을 위한 SRE 기초 (9/10): 용량 계획
- 바이브코딩을 위한 SRE 기초 (10/10): 운영 가능한 시스템
<!-- toc:end -->

Tags: 바이브코딩, SRE, Toil, Automation, Operations
