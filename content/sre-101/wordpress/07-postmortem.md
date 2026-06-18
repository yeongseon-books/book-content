---
title: "바이브코딩을 위한 SRE 기초 (7/10): 포스트모템"
series: sre-101
episode: 7
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - SRE
  - Postmortem
  - BlamelessCulture
  - Operations
---

# 바이브코딩을 위한 SRE 기초 (7/10): 포스트모템

이 글은 "바이브코딩을 위한 SRE 기초" 시리즈의 7번째 글입니다.

---

바이브코딩에서 AI는 장애 대응 코드와 경보 시스템을 빠르게 만들어 줍니다. 그런데 장애가 끝난 후 무엇을 해야 할지 정해져 있지 않으면, 같은 장애가 반복됩니다. 타임라인은 채널에 흩어져 있고, 원인 분석은 기억에 의존하고, 재발 방지 조치는 누가 맡을지 불분명한 채로 팀이 다음 장애를 기다립니다.

포스트모템은 장애를 정리하는 문서가 아닙니다. 시스템이 왜 실패했는지 이해하고, 같은 실패가 다시 일어나지 않도록 구조를 바꾸는 과정입니다. 그런데 포스트모템이 제대로 작동하려면 한 가지 전제가 필요합니다. 사람을 탓하지 않는다는 원칙입니다.

블레임리스 포스트모템은 "누가 실수했는가"가 아니라 "어떤 조건이 이 실수를 가능하게 했는가"를 묻습니다. 엔지니어는 최선을 다했지만 시스템이 그 실수를 허용했습니다. 시스템을 바꾸는 것이 재발 방지의 핵심입니다.

> **핵심 인사이트:** 포스트모템의 가치는 문서 자체가 아니라 조치 항목(action item)의 완료율에 있습니다. 블레임리스 원칙이 없으면 팀원이 사실을 숨기고, 근본 원인이 드러나지 않습니다. 타임라인을 장애 중에 실시간으로 기록해 두면 포스트모템 초안이 저절로 만들어집니다.

## 이 글에서 다룰 문제

- 블레임리스 포스트모템이란 무엇이고 왜 필요할까요?
- 포스트모템 템플릿에 반드시 포함해야 할 항목은 무엇인가요?
- 근본 원인 분석은 어떻게 수행할까요?
- 조치 항목을 어떻게 추적하고 완료율을 높일까요?
- AI가 만든 장애 대응 시스템에서 포스트모템 관점으로 확인할 것은 무엇인가요?

## 포스트모템 핵심 패턴

```python
# 포스트모템 템플릿: 필수 항목 정의
postmortem = {
    "title": "2024-05-19 Redis OOM으로 인한 홈 피드 장애",
    "summary": "Redis primary 노드 OOM kill로 홈 피드 p99 latency 5초 초과, 25분 서비스 저하",
    "impact": {
        "duration_min": 25,
        "affected_users": 48000,
        "severity": "SEV1",
    },
    "timeline": [
        "14:12 - Redis primary OOM kill 발생",
        "14:13 - 홈 피드 latency 경보 (p99 5초 초과)",
        "14:15 - IC 지정, 전용 채널 생성",
        "14:20 - failover 명령 승인",
        "14:22 - replica 승격 완료",
        "14:37 - incident 종료",
    ],
    "root_cause": "Redis maxmemory 설정 없음 → 트래픽 급증 시 OOM",
    "contributing_factors": [
        "메모리 사용률 경보 없음",
        "replica 자동 승격 미설정",
        "maxmemory-policy 기본값(noeviction) 유지",
    ],
    "actions": [
        {"item": "Redis maxmemory 설정 추가", "owner": "alice", "due": "2024-05-26"},
        {"item": "메모리 사용률 80% 경보 설정", "owner": "bob", "due": "2024-05-23"},
        {"item": "replica 자동 승격 활성화", "owner": "alice", "due": "2024-05-30"},
    ],
    "lessons": "메모리 제한 없는 캐시는 트래픽 급증 시 OOM 위험. 경보와 자동 복구 없이는 감지가 늦음.",
}
```

```python
# 근본 원인 분석: 5 Whys 적용
def five_whys(initial_symptom):
    """
    증상:   홈 피드 latency 5초 초과
    Why 1: Redis 응답 없음
    Why 2: Redis primary 노드 OOM kill
    Why 3: maxmemory 설정 없어 메모리 무제한 증가
    Why 4: 트래픽 급증 시 캐시 항목 만료 없이 쌓임
    Why 5: Redis 설정 리뷰 체크리스트에 maxmemory 항목 없음
    → 근본 원인: 인프라 설정 리뷰 절차 미비
    """
    return "인프라 설정 리뷰 절차에 maxmemory 체크 항목 추가"

# 포스트모템 건강도 측정
def postmortem_health_metrics(postmortems):
    total = len(postmortems)
    if total == 0:
        return {}
    completed = sum(
        1 for p in postmortems
        if all(a.get("done") for a in p.get("actions", []))
    )
    repeat = sum(1 for p in postmortems if p.get("repeat_incident"))
    return {
        "action_completion_rate": completed / total,  # 목표: 0.8 이상
        "repeat_incident_rate": repeat / total,        # 목표: 0.1 이하
    }
```

```yaml
# 포스트모템 조치 항목 추적 (GitHub Issues 연동 예시)
postmortem_actions:
  - id: PM-2024-05-19-1
    item: "Redis maxmemory 설정 추가"
    owner: alice
    due: 2024-05-26
    severity: SEV1
    status: open
    linked_issue: "github.com/org/repo/issues/342"

  - id: PM-2024-05-19-2
    item: "메모리 사용률 80% 경보 설정"
    owner: bob
    due: 2024-05-23
    severity: SEV1
    status: closed
    closed_at: 2024-05-22
```

## 변경 전후 비교

**Before: 포스트모템 없는 장애 마무리**
```text
- 장애 종료 후 Slack 채널 아카이브
- 원인 분석 없이 "Redis 문제였음"으로 종결
- 재발 방지 조치 없음
- 같은 장애 3개월 후 재발
- 팀원이 실수를 숨김 (탓할까봐)
```

**After: 블레임리스 포스트모템 적용**
```text
- 장애 타임라인 → 포스트모템 초안 자동 생성
- 5 Whys로 근본 원인 (설정 리뷰 절차 미비) 확인
- 조치 항목에 담당자와 기한 명시
- 완료율 80% 이상 추적
- 팀원이 사실을 솔직하게 공유 (블레임 없음)
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| "누가 실수했나" 초점 | 팀원이 사실 숨김, 근본 원인 미발견 | 시스템/절차 문제로 프레이밍 전환 |
| 조치 항목에 담당자 없음 | 아무도 실행 안 함 | 항목마다 owner와 due date 명시 |
| 장애 후 기억으로 타임라인 작성 | 디테일 손실, 순서 불정확 | 장애 중 Slack 채널에 실시간 기록 |
| 포스트모템 완료율 미추적 | 조치 항목이 백로그에 묻힘 | 주간 리뷰에 미완료 항목 포함 |
| 근본 원인을 증상으로 오판 | 재발 방지 불가 | 5 Whys로 절차/구조 수준까지 파고들기 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"Slack 장애 채널 타임라인을 포스트모템 초안으로 변환해줘.
제목, 요약, 영향 범위, 타임라인, 근본 원인, 조치 항목, 교훈 포함,
조치 항목마다 담당자와 기한 필드 포함"

# AI 결과물 검증 체크포인트:
# - 근본 원인이 증상(Redis OOM)이 아닌 절차/구조 수준인가?
# - 조치 항목마다 owner와 due date가 있는가?
# - "누가 실수했나"가 아닌 "어떤 조건이 실수를 허용했나" 관점인가?
# - 타임라인이 실시간 기록 기반인가?
# - 유사 과거 장애와 연결되어 있는가?
```

## 운영 체크리스트

- [ ] 블레임리스 포스트모템 원칙이 팀에 공유되어 있다
- [ ] 포스트모템 템플릿에 타임라인, 근본 원인, 조치 항목이 포함된다
- [ ] 조치 항목마다 담당자와 기한이 명시된다
- [ ] 조치 항목 완료율을 주간 단위로 추적한다
- [ ] 장애 중 Slack 채널 기록이 포스트모템 초안으로 이어지는 구조가 있다

## 처음 질문으로 돌아가기

- **블레임리스 포스트모템이 왜 필요한가?** 사람을 탓하면 팀원이 사실을 숨깁니다. 근본 원인이 드러나지 않으면 같은 장애가 반복됩니다. "어떤 시스템 조건이 이 실수를 가능하게 했는가"를 물어야 구조적 개선이 가능합니다.
- **근본 원인 분석을 어떻게 하는가?** 5 Whys 방법으로 증상에서 시작해 "왜"를 다섯 번 반복합니다. Redis OOM → maxmemory 없음 → 설정 리뷰 절차 미비. 증상 수준에서 멈추면 재발 방지가 안 됩니다.
- **조치 항목 완료율을 어떻게 높이는가?** 항목마다 담당자와 기한을 명시하고, 주간 리뷰에 미완료 항목을 포함합니다. 완료율 목표(80% 이상)를 팀 지표로 관리합니다.

## 정리

바이브코딩에서 AI가 만든 장애 대응 시스템에 포스트모템 절차가 없다면, 장애를 닫아도 같은 장애가 반복됩니다. 블레임리스 원칙, 5 Whys 근본 원인 분석, 조치 항목 추적을 갖춘 포스트모템 절차를 팀에 심어 두세요. 다음 글에서는 Toil 줄이기를 다룹니다.

## 참고 자료

- [Postmortem Culture — Google SRE Book](https://sre.google/sre-book/postmortem-culture/)
- [Blameless PostMortems — Etsy](https://www.etsy.com/codeascraft/blameless-postmortems/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/sre-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 SRE 기초 (1/10): SRE란 무엇인가?
- 바이브코딩을 위한 SRE 기초 (2/10): 신뢰성
- 바이브코딩을 위한 SRE 기초 (3/10): SLI, SLO, SLA
- 바이브코딩을 위한 SRE 기초 (4/10): 에러 예산
- 바이브코딩을 위한 SRE 기초 (5/10): 모니터링
- 바이브코딩을 위한 SRE 기초 (6/10): 장애 대응
- **바이브코딩을 위한 SRE 기초 (7/10): 포스트모템 (현재 글)**
- 바이브코딩을 위한 SRE 기초 (8/10): Toil 줄이기
- 바이브코딩을 위한 SRE 기초 (9/10): 용량 계획
- 바이브코딩을 위한 SRE 기초 (10/10): 운영 가능한 시스템
<!-- toc:end -->

Tags: 바이브코딩, SRE, Postmortem, BlamelessCulture, Operations
