---
title: "바이브코딩을 위한 Information Security 기초 (10/10): 보안 사고 대응"
series: information-security-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Security
  - IncidentResponse
  - Runbook
  - Postmortem
---

# 바이브코딩을 위한 Information Security 기초 (10/10): 보안 사고 대응

이 글은 "바이브코딩을 위한 Information Security 기초" 시리즈의 마지막 글입니다.

---

바이브코딩에서 AI는 보안 기능을 빠르게 만들어 줍니다. 하지만 사고는 결국 일어납니다. 좋은 대응은 손실을 줄이고, 나쁜 대응은 같은 사고를 더 크게 키웁니다. 첫 5분에 누가 결정을 내리는지, 어떤 기록을 남기는지, 증거를 어떻게 보존하는지가 그 뒤 몇 시간의 품질을 거의 결정합니다.

평온한 시기에 준비하지 않은 절차는 사고 순간에 절차가 되지 못합니다. 예방만으로 보안이 끝나지 않습니다. 대응은 실제 보안의 절반입니다.

기술적으로는 해결 가능한 사고도 누가 어떤 결정을 해야 하는지 정해져 있지 않으면 혼선과 증거 훼손 때문에 훨씬 크게 번집니다. 첫 30분을 자동화하고 나머지 판단은 명확한 역할 아래에서 수행하는 조직이 사고를 통제합니다.

NIST IR 사이클(Prepare→Detect→Contain→Eradicate→Recover→Lessons), 런북, 무비난 회고를 중심으로 정리합니다.

> **핵심 인사이트:** 사고는 피할 수 없지만 손실 규모는 줄일 수 있습니다. 런북과 사고 지휘관이 미리 지정된 조직은 그렇지 않은 조직보다 격리 시간이 10배 이상 빠릅니다. "일어나면 그때 생각하겠다"는 계획이 아닙니다.

## 이 글에서 다룰 문제

- 사고가 발생하면 첫 5분에 무엇을 해야 할까요?
- NIST IR 사이클은 어떤 흐름으로 이어질까요?
- 격리와 증거 보존은 어떻게 균형을 잡아야 할까요?
- 무비난 회고는 왜 중요할까요?
- AI가 만든 보안 코드에서 사고 대응 관점으로 확인할 것은 무엇인가요?

## 사고 대응 핵심 패턴

```python
# 사고 시작 시 즉시 실행: 채널 생성 + 타임라인 시작
from datetime import datetime, timezone

def start_incident(severity: str, summary: str) -> dict:
    incident_id = datetime.now(timezone.utc).strftime("INC-%Y%m%d-%H%M%S")
    return {
        "incident_id": incident_id,
        "severity": severity,
        "summary": summary,
        "channel": f"#inc-{incident_id.lower()}",
        "timeline_started": True,
    }

# 격리 전 반드시 증거 보존 먼저
def contain_compromised_account(user_id: str):
    snapshot_logs(user_id, hours=24)    # 증거 보존 먼저
    revoke_all_sessions(user_id)        # 그 다음 격리
    rotate_credentials(user_id)
    block_ip_list(get_recent_ips(user_id))
```

```text
# 무비난 회고 템플릿
- What happened (timeline)
- Impact
- Root cause (5 Whys)
- What went well
- What to improve
- Action items (owner + due date)

# NIST IR 사이클
Prepare → Detect → Contain → Eradicate → Recover → Lessons → (반복)
```

## 변경 전후 비교

**Before: 즉흥 대응**
```text
- 누가 결정할지 정해지지 않음 → 혼선
- 시스템을 즉시 꺼버림 → 증거 소멸
- 여러 채널(DM, 이메일, 전화)에서 동시에 소통 → 타임라인 복원 불가
- 회고에서 사람을 비난 → 다음 사고에서 정보 숨김
```

**After: 런북 + 사고 지휘관**
```text
- 사고 지휘관 즉시 지정 → 단일 의사결정 창구
- 증거 보존 후 격리 → 포렌식 가능
- 하나의 사고 채널에서 모든 소통 → 타임라인 재현 가능
- 무비난 회고 → 시스템 개선으로 연결
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 시스템을 즉시 꺼버림 | 증거가 사라짐 | 격리 전 로그/메모리 스냅샷 먼저 |
| 여러 사람이 동시에 결정 | 모순과 혼선이 커짐 | 사고 지휘관 1명 지정 |
| 회고에서 사람을 비난 | 다음 사고에서 정보가 숨겨짐 | 무비난 회고 원칙 |
| 심각도 체계가 없음 | 대응 우선순위 무너짐 | SEV1/SEV2/SEV3 명확히 정의 |
| 런북 없이 사고 대응 | 첫 5분을 허비 | 주요 사고 유형별 런북 사전 작성 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"보안 사고 대응 런북을 만들어줘.
'S3 버킷 공개 오픈' 시나리오,
NIST IR 사이클 6단계 기반,
각 단계별 담당자, 시간 목표, 체크리스트 포함,
증거 보존 절차와 커뮤니케이션 템플릿까지"

# AI 결과물 검증 체크포인트:
# - 사고 지휘관 역할이 명시되어 있는가?
# - 증거 보존이 격리보다 먼저인가?
# - 심각도 체계(SEV1/SEV2/SEV3)가 있는가?
# - 무비난 회고 템플릿이 포함되어 있는가?
# - 액션 아이템에 담당자와 마감일이 있는가?
```

## 운영 체크리스트

- [ ] 사고 지휘관 역할이 정의되고 대체자가 있다
- [ ] 주요 사고 유형별 런북이 작성되어 있다
- [ ] 심각도 체계와 호출 체계가 최신으로 유지된다
- [ ] 무비난 회고 템플릿이 준비되어 있다
- [ ] 최근 6개월 내 게임데이(훈련)를 실시했다

## 처음 질문으로 돌아가기

- **사고 첫 5분에 해야 할 것은?** 사고 지휘관 지정, 사고 채널 개설(#inc-날짜), 타임라인 기록 시작, 외부 커뮤니케이션 보류(법무 합류 전까지)입니다.
- **NIST IR 사이클이란?** Prepare(준비) → Detect(탐지) → Contain(격리) → Eradicate(제거) → Recover(복구) → Lessons(교훈) 순환 구조입니다. 한 번의 사고에서 얻은 교훈이 다음 준비로 돌아가야 조직이 강해집니다.
- **격리 vs 증거 보존 우선순위는?** 가능하면 증거(로그 스냅샷, 메모리 덤프)를 보존한 후 격리합니다. 즉시 끄면 중요한 단서가 함께 사라질 수 있습니다.

## 정리

바이브코딩에서 AI가 만들어 준 보안 코드에서 런북 연동 여부, 증거 보존 절차, 사고 채널 표준화를 반드시 확인하세요. 보안 사고 대응은 준비가 눈에 보이는 형태로 드러나는 순간입니다. Information Security 101 시리즈를 통해 CIA에서 시작해 인증, 암호화, 웹 보안, 비밀 정보, 권한, 로그, 사고 대응까지 이어지는 기본 축을 갖추셨기를 바랍니다.

## 참고 자료

- [NIST SP 800-61 — Computer Security Incident Handling Guide](https://csrc.nist.gov/publications/detail/sp/800-61/rev-2/final)
- [Google SRE Book — Managing Incidents](https://sre.google/sre-book/managing-incidents/)
- [PagerDuty — Incident Response Documentation](https://response.pagerduty.com/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/information-security-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Information Security 기초 (1/10): 정보 보안이란 무엇인가?
- 바이브코딩을 위한 Information Security 기초 (2/10): 인증과 인가
- 바이브코딩을 위한 Information Security 기초 (3/10): 암호화와 해시
- 바이브코딩을 위한 Information Security 기초 (4/10): TLS와 인증서
- 바이브코딩을 위한 Information Security 기초 (5/10): 웹 보안 기초
- 바이브코딩을 위한 Information Security 기초 (6/10): SQL Injection과 XSS
- 바이브코딩을 위한 Information Security 기초 (7/10): 비밀 정보 관리
- 바이브코딩을 위한 Information Security 기초 (8/10): 권한 최소화
- 바이브코딩을 위한 Information Security 기초 (9/10): 로그와 감사
- **바이브코딩을 위한 Information Security 기초 (10/10): 보안 사고 대응 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, Security, IncidentResponse, Runbook, Postmortem
