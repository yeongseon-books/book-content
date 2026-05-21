---
episode: 8
language: ko
last_reviewed: '2026-05-14'
seo_description: 반복 수작업 Toil의 정의와 측정법, 빈도와 시간 기준으로 자동화 우선순위와 손익분기점을 정하는 방법입니다.
series: sre-101
status: content-ready
tags:
- SRE
- Toil
- Automation
- Productivity
- Operations
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "SRE 101 (8/10): Toil 줄이기"
---

# SRE 101 (8/10): Toil 줄이기

운영팀이 바쁘다는 사실만으로 그 일이 모두 가치 있다고 볼 수는 없습니다. 어떤 일은 시스템 이해를 깊게 만들고, 어떤 일은 고객 가치와 직접 연결됩니다. 반면 어떤 일은 반복되고 자동화도 가능하지만, 사람이 계속 붙어 있어야만 굴러갑니다.

SRE에서는 이런 반복 수작업을 Toil이라고 부릅니다. Toil을 줄인다는 말은 편해지자는 뜻이 아니라, 사람 시간을 더 가치 있는 엔지니어링 작업으로 되돌리자는 뜻에 가깝습니다.

이 글은 SRE 101 시리즈의 8번째 글입니다. 여기서는 Toil이 무엇인지, 어떻게 측정하는지, 자동화 후보를 어떤 기준으로 정렬할지, 손익분기점을 어떻게 계산할지, 그리고 왜 Toil이 운영 부채와 닮았는지 설명합니다.

## 먼저 던지는 질문

- Toil은 일반적인 운영 업무와 무엇이 다를까요?
- 팀 시간이 반복 수작업에 얼마나 쓰이는지 어떻게 재야 할까요?
- 어떤 작업부터 자동화해야 투자 효과가 클까요?

## 큰 그림

![SRE 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/08/08-01-concept-at-a-glance.ko.png)

*SRE 101 8장 흐름 개요*

Toil을 반복 수작업으로 분류하고, 그 중 어디까지를 자동화할 수 있는지 우선순위를 매깁니다.

> Toil은 일의 이름이 아니라, 어떤 작업을 자동화할 수 있는지, 안 한다면 왜 안 하는지 묻는 태도입니다.

## 왜 이 주제가 중요한가

Toil이 팀 시간의 큰 비중을 차지하면 개선 작업이 멈춥니다. 테스트 강화, 배포 안전성 보강, 모니터링 개선, 장애 예방 같은 일은 자꾸 뒤로 밀리고, 팀은 같은 운영 작업을 계속 반복하게 됩니다.

또한 Toil은 눈에 잘 보이지 않는 부채입니다. 서비스는 돌아가는 것처럼 보이지만 실제로는 야간 호출, 수동 복구, 반복 점검 같은 사람 노동 위에 서 있을 수 있습니다. 이런 구조는 규모가 커질수록 빠르게 한계에 닿습니다.

## 한 문장으로 잡는 멘탈 모델

> Toil은 단순히 귀찮은 일이 아니라, 반복되고 자동화 가능한 작업이 사람 시간을 계속 태우는 상태입니다.

## 한눈에 보는 구조

이 흐름은 측정과 자동화의 방향을 단순하게 보여 줍니다. 수작업을 그냥 익숙한 절차로 두지 말고, Toil로 식별하고, 자동화로 넘겨 팀 시간을 되찾아야 합니다.

## 핵심 용어 먼저 정리

| 용어 | 뜻 | 실무에서 보는 포인트 |
| --- | --- | --- |
| toil | 반복적이고 자동화 가능한 수작업 | 장기적으로 팀 생산성을 깎습니다 |
| runbook | 사람이 따라 하는 운영 절차 문서 | 자동화 전 단계일 수 있습니다 |
| automation | 절차를 코드로 옮긴 것 | 사람 개입을 줄이고 속도를 높입니다 |
| toil ratio | 전체 시간 중 Toil 비율 | 팀 상태를 수치로 보여 줍니다 |
| break-even | 자동화 투자 시간이 회수되는 시점 | 무엇부터 자동화할지 정하게 해 줍니다 |

## Toil은 왜 단순 피로와 다를까

바쁜 일이라고 해서 모두 Toil은 아닙니다. 예를 들어 처음 설계하는 배포 파이프라인이나 새로운 장애 패턴을 분석하는 일은 시간이 많이 들어도 가치가 큽니다. 반대로 같은 서비스 재시작을 매주 밤마다 손으로 반복한다면, 그 일은 Toil일 가능성이 큽니다.

Toil을 구분하는 기준은 반복성, 수작업성, 자동화 가능성입니다. 이 세 가지가 겹치면 팀은 계속 같은 비용을 지불하게 됩니다. 그래서 Toil은 피로의 문제가 아니라 구조의 문제입니다.

## 측정하지 않으면 우선순위도 흔들린다

어떤 작업이 가장 짜증 나는지는 쉽게 기억납니다. 하지만 어떤 작업이 가장 많은 시간을 태우는지는 기록하지 않으면 잘 보이지 않습니다. 강한 팀은 자동화 논의를 감으로 하지 않고, 빈도와 소요 시간으로 정렬합니다.

이 관점이 있어야 자동화도 더 현실적이 됩니다. 멋진 자동화를 만드는 것보다, 지금 시간을 가장 많이 잡아먹는 반복 작업을 먼저 줄이는 편이 보통 더 큰 효과를 냅니다.

## Toil 판별 기준

Toil을 정확하게 분류하려면 명확한 기준이 필요합니다. 다음 표는 어떤 작업이 Toil인지 판단하는 기준을 보여 줍니다.

| 기준 | 설명 | Toil 예시 | Non-Toil 예시 |
| --- | --- | --- | --- |
| 수동 | 사람이 직접 실행해야 함 | 서버 수동 재시작 | 자동 재시작 스크립트 |
| 반복 | 같은 절차를 계속 수행 | 매일 로그 수동 수집 | 일회성 장애 분석 |
| 자동화 가능 | 코드로 표현할 수 있음 | 인증서 갱신 절차 | 새로운 아키텍처 설계 |
| 전술적 | 긴급 대응이지만 근본 해결 아님 | 장애 때마다 수동 재시작 | Health check와 자동 failover 설계 |
| 가치 없음 | 비즈니스나 신뢰성에 기여 적음 | 의미 없는 보고서 작성 | 고객 영향 모니터링 개선 |

한 작업이 이 다섯 가지 기준을 모두 충족하면 높은 우선순위 Toil로 분류되며, 일부만 충족하면 낮은 우선순위 Toil이 됩니다. Toil이 아닌 작업은 자동화 대상에서 제외하고, 엔지니어링 작업으로 분류합니다.

## 인증서 갱신 자동화 예제

SSL/TLS 인증서는 만료되면 서비스가 중단됩니다. 인증서 갱신을 사람이 수동으로 하는 것은 전형적인 Toil입니다. 다음은 Let's Encrypt를 사용한 자동 갱신 예제입니다.

```python
#!/usr/bin/env python3
"""
인증서 자동 갱신 스크립트

만료 30일 전 인증서를 확인하고 자동으로 갱신합니다.
Let's Encrypt certbot을 사용하고, 대상 도메인 목록을 받습니다.
"""
import subprocess
import datetime
import sys
from pathlib import Path

def check_cert_expiry(domain: str) -> int:
    """Check days until certificate expires"""
    cmd = [
        "openssl", "s_client",
        "-connect", f"{domain}:443",
        "-servername", domain,
        "-showcerts"
    ]
    
    try:
        # Get certificate info
        proc = subprocess.run(
            cmd,
            input=b"",
            capture_output=True,
            timeout=10
        )
        
        # Parse expiry date from openssl output
        output = proc.stdout.decode()
        for line in output.split("\n"):
            if "Not After" in line:
                # Extract date
                date_str = line.split(":", 1)[1].strip()
                expiry = datetime.datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z")
                days_left = (expiry - datetime.datetime.now()).days
                return days_left
    except Exception as e:
        print(f"Error checking {domain}: {e}")
        return -1
    
    return -1

def renew_certificate(domain: str) -> bool:
    """Renew certificate using certbot"""
    cmd = [
        "certbot", "renew",
        "--cert-name", domain,
        "--force-renewal",
        "--non-interactive"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=300)
        if result.returncode == 0:
            print(f"Successfully renewed certificate for {domain}")
            return True
        else:
            print(f"Failed to renew {domain}: {result.stderr.decode()}")
            return False
    except Exception as e:
        print(f"Error renewing {domain}: {e}")
        return False

def reload_nginx():
    """Reload nginx to apply new certificate"""
    subprocess.run(["systemctl", "reload", "nginx"])

def main():
    domains = [
        "example.com",
        "api.example.com",
        "www.example.com"
    ]
    
    threshold_days = 30  # Renew if expiring within 30 days
    
    renewed = []
    
    for domain in domains:
        days_left = check_cert_expiry(domain)
        
        if days_left < 0:
            print(f"Could not check {domain}")
            continue
        
        print(f"{domain}: {days_left} days until expiry")
        
        if days_left < threshold_days:
            print(f"Renewing {domain} (expires in {days_left} days)")
            if renew_certificate(domain):
                renewed.append(domain)
        else:
            print(f"{domain} is valid for {days_left} days, no renewal needed")
    
    if renewed:
        print(f"Reloading nginx to apply new certificates")
        reload_nginx()
        print(f"Renewed certificates for: {', '.join(renewed)}")
    else:
        print("No certificates needed renewal")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Cron으로 매일 실행:**

```bash
# /etc/cron.d/cert-renewal
0 3 * * * root /usr/local/bin/renew-certs.py >> /var/log/cert-renewal.log 2>&1
```

이 스크립트는 매일 새벽 3시에 실행되며, 만료 30일 이내 인증서를 자동으로 갱신합니다. 사람이 매번 달력을 확인하고 수동으로 갱신하던 Toil을 제거합니다.

## Toil 버짓 (50% 규칙)

Google SRE는 팀 시간의 50% 이상을 Toil에 써서는 안 된다고 권장합니다. 나머지 50%는 엔지니어링 작업(자동화, 모니터링 개선, 신뢰성 개선)에 할애해야 합니다.

### Toil 버짓이 필요한 이유

1. **규모 한계**: Toil은 선형적으로 늘어납니다. 서비스가 2배 커지면 Toil도 2배 늘어납니다. 자동화 없이는 타임은 계속 늘어납니다.
2. **복리 효과**: 엔지니어링 작업은 복리로 쌓입니다. 좋은 모니터링은 장애를 더 빠르게 찾게 하고, 자동화는 다음 자동화를 더 쉽게 만듭니다.
3. **노화 방지**: Toil에만 매달리면 팀의 스킬이 정체됩니다. 새로운 기술, 도구, 패턴을 배울 시간이 없어집니다.
4. **채용과 유지**: Toil이 많은 팀은 좋은 엔지니어를 유치하기 어렵습니다. 성장 기회가 적고 반복 작업에 지치기 때문입니다.

### Toil 버짓 추적 방법

```python
def toil_budget_status(team_hours_per_week, toil_hours):
    """
    Toil 버짓 상태 확인
    
    50% 규칙: 팀 시간의 절반 이상을 Toil에 쓰면 안 됨
    """
    toil_pct = (toil_hours / team_hours_per_week) * 100
    budget_limit = team_hours_per_week * 0.5
    remaining_budget = budget_limit - toil_hours
    
    status = {
        "toil_hours": toil_hours,
        "toil_pct": toil_pct,
        "budget_limit": budget_limit,
        "remaining_budget": remaining_budget,
        "engineering_hours": team_hours_per_week - toil_hours
    }
    
    if toil_pct <= 30:
        status["health"] = "healthy"
        status["recommendation"] = "Toil 비율 적정. 현재 수준 유지"
    elif toil_pct <= 50:
        status["health"] = "warning"
        status["recommendation"] = "Toil 비율 증가 중. 자동화 검토 권장"
    else:
        status["health"] = "critical"
        status["recommendation"] = "Toil 버짓 초과! 즐각 자동화 필요"
    
    return status

# 예시
team_hours = 200  # 5명 x 40시간
toil_hours = 60   # 주당 60시간 Toil

status = toil_budget_status(team_hours, toil_hours)
print(f"Toil: {status['toil_hours']}시간 ({status['toil_pct']:.1f}%)")
print(f"Engineering: {status['engineering_hours']}시간")
print(f"Status: {status['health']}")
print(f"Recommendation: {status['recommendation']}")
```

Toil 버짓을 주기적으로 측정하고 공유하면, 팀이 엔지니어링 작업에 충분한 시간을 할애하고 있는지 확인할 수 있습니다. 이 수치가 50%를 넘어가면 자동화가 긴급 우선순위가 됩니다.

모든 반복 작업을 한께번에 자동화할 수는 없습니다. 빈도와 위험도를 기준으로 우선순위를 매기면 어떤 작업부터 자동화해야 할지 판단하기 쉬워집니다.

| 빈도 \ 위험도 | 높음 | 보통 | 낮음 |
| --- | --- | --- | --- |
| **주간 5회+** | 즉시 자동화 (P0) | 1분기 내 자동화 (P1) | 2분기 내 자동화 (P2) |
| **주간 2-4회** | 1분기 내 자동화 (P1) | 2분기 내 자동화 (P2) | 문서화 후 보류 (P3) |
| **주간 0-1회** | 2분기 내 자동화 (P2) | 문서화 후 보류 (P3) | runbook만 유지 |

빈도가 높고 위험도가 높은 작업이 가장 먼저 자동화되어야 합니다. 빈도가 낮고 위험도가 낮은 작업은 runbook으로 처리하는 편이 더 현명할 수 있습니다.
## 단계별로 Toil 측정하고 자동화하기
## 단계별로 Toil 측정하고 자동화하기

### 1단계 — Toil 시간 기록

```python
def log_toil(task, minutes):
    return {"task": task, "minutes": minutes}
```

자동화를 논의하기 전에 먼저 시간을 기록해야 합니다. 어떤 작업이 얼마나 자주 발생하고, 한 번에 얼마나 걸리는지 보여야 우선순위가 생깁니다.

### 2단계 — Toil 비율 계산

```python
def toil_ratio(toil_min, total_min):
    return toil_min / total_min
```

Toil ratio는 팀이 얼마만큼 개선 여력을 잃고 있는지 보여 주는 간단한 지표입니다. 운영이 문제라기보다, 반복 수작업이 전체 시간에서 차지하는 비중이 문제라는 점이 드러납니다.

### 3단계 — 자동화 후보 점수화

```python
def score(freq_per_week, minutes_each):
    return freq_per_week * minutes_each
```

빈도와 소요 시간을 곱하면 어떤 작업이 시간을 가장 많이 태우는지 비교하기 쉬워집니다. 가장 거슬리는 작업보다 가장 큰 비용을 만드는 작업부터 손보는 편이 더 실용적일 때가 많습니다.

### 4단계 — 손익분기점 계산

```python
def break_even(saved_per_week, build_minutes):
    return build_minutes / saved_per_week
```

자동화는 공짜가 아닙니다. 만드는 데 드는 시간과 매주 절약되는 시간을 함께 봐야 합니다. 손익분기점은 어떤 자동화부터 투자할지 판단하게 해 줍니다.

## 자동 롤백 스크립트 예제

```python
#!/usr/bin/env python3
"""
자동 롤백 스크립트

조건:
- 배포 후 5분 동안 error rate > 5%
- latency p99 > 3000ms

행동:
- 이전 버전으로 자동 롤백
- Slack 알림 발송
"""
import time
import requests

def check_metrics(api_url, threshold_error_rate=0.05, threshold_latency_ms=3000):
    """Check current error rate and latency"""
    response = requests.get(f"{api_url}/metrics")
    data = response.json()
    
    error_rate = data["error_rate"]
    latency_p99 = data["latency_p99_ms"]
    
    return error_rate > threshold_error_rate or latency_p99 > threshold_latency_ms

def rollback_deployment(service, previous_version):
    """Rollback to previous version"""
    return f"kubectl set image deployment/{service} {service}={previous_version}"

def notify_slack(channel, message):
    """Send Slack notification"""
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    payload = {"channel": channel, "text": message}
    requests.post(webhook_url, json=payload)

def main():
    service = "api"
    current_version = "v2.1.0"
    previous_version = "v2.0.5"
    api_url = "http://api.example.com"
    
    # Wait 5 minutes after deployment
    time.sleep(300)
    
    if check_metrics(api_url):
        # Trigger rollback
        cmd = rollback_deployment(service, previous_version)
        print(f"Rolling back: {cmd}")
        
        # Notify team
        notify_slack(
            "#alerts",
            f":warning: Auto-rollback triggered for {service} {current_version} -> {previous_version}"
        )
        return 1
    
    print("Deployment healthy")
    return 0

if __name__ == "__main__":
    exit(main())
```

이 스크립트는 배포 후 메트릭을 지속적으로 확인하다가, 임계값을 초과하면 자동으로 이전 버전으로 돌립니다. 사람이 대기하지 않아도 비정상 상태를 감지하고 복구할 수 있습니다.

## Toil 측정과 감소

Toil을 줄이려면 먼저 얼마나 쓰고 있는지 알아야 합니다. Google SRE는 팀 시간의 50% 이상을 Toil에 써서는 안 된다고 권장합니다. 나머지 50%는 엔지니어링 작업(자동화, 모니터링 개선, 신뢰성 개선)에 할애해야 합니다.

```python
def calculate_toil_percentage(team_hours_per_week):
    """
    Toil 비율 계산
    
    예시:
    - 5명 팀, 주당 40시간 = 200시간
    - Toil: 배포 30분 x 20회 = 10시간
           로그 수집 1시간 x 5회 = 5시간
           수동 재시작 15분 x 10회 = 2.5시간
    - 총 Toil = 17.5시간
    - Toil % = 17.5 / 200 = 8.75%
    """
    toil_tasks = {
        "수동 배포": {"minutes_each": 30, "freq_per_week": 20},
        "로그 수집": {"minutes_each": 60, "freq_per_week": 5},
        "서비스 재시작": {"minutes_each": 15, "freq_per_week": 10},
        "백업 검증": {"minutes_each": 45, "freq_per_week": 3},
    }
    
    total_toil_minutes = sum(
        task["minutes_each"] * task["freq_per_week"]
        for task in toil_tasks.values()
    )
    
    total_toil_hours = total_toil_minutes / 60
    toil_percentage = (total_toil_hours / team_hours_per_week) * 100
    
    return {
        "total_toil_hours": total_toil_hours,
        "toil_percentage": toil_percentage,
        "engineering_hours": team_hours_per_week - total_toil_hours,
        "tasks": toil_tasks
    }

# 예시
team_hours = 200  # 5명 x 40시간
result = calculate_toil_percentage(team_hours)

print(f"Toil: {result['total_toil_hours']:.1f}시간 ({result['toil_percentage']:.1f}%)")
print(f"Engineering: {result['engineering_hours']:.1f}시간")

if result['toil_percentage'] > 50:
    print("⚠️ Toil이 50%를 초과했습니다. 자동화 필요")
elif result['toil_percentage'] > 30:
    print("🟡 Toil이 30% 초과. 개선 권장")
else:
    print("✅ Toil 비율 적정")
```

Toil 비율을 주기적으로 측정하면 팀이 엔지니어링 작업에 얼마나 투자하고 있는지 볼 수 있습니다. 이 수치가 높아지면 자동화와 개선 작업에 시간을 할애하는 것이 우선 과제가 됩니다.

### 5단계 — 자동화 구현

```python
def auto_restart(service):
    return f"systemctl restart {service}"
```

코드는 단순해 보여도 의미는 분명합니다. 사람이 매번 하던 복구 절차를 시스템이 대신하게 만들면, 복구 시간도 줄고 사람의 집중력도 더 중요한 문제에 쓸 수 있습니다.

## Canary Deployment YAML 예시

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-canary
  labels:
    app: api
    track: canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api
      track: canary
  template:
    metadata:
      labels:
        app: api
        track: canary
    spec:
      containers:
      - name: api
        image: myapp:v2.1.0
        ports:
        - containerPort: 8000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-stable
  labels:
    app: api
    track: stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: api
      track: stable
  template:
    metadata:
      labels:
        app: api
        track: stable
    spec:
      containers:
      - name: api
        image: myapp:v2.0.5
        ports:
        - containerPort: 8000
```

카나리 배포는 전체 트래픽의 10% 정도를 새 버전으로 보냅니다. 10분 이상 문제가 없으면 stable로 확대하고, 오류가 나면 즉시 canary를 중단합니다.

## 변경 실패율(CFR) 측정

Change Failure Rate는 전체 변경 중 얼마나 많은 변경이 롤백이나 핫픽스를 초래하는지 보여 줍니다. 변경의 질을 측정하는 핵심 지표입니다.

```python
def change_failure_rate(total_changes, failed_changes):
    """
    CFR = (실패한 변경 수 / 전체 변경 수) * 100
    
    예시:
    - 한 달간 배포 100번, 그 중 롤백 5번 → CFR = 5%
    - Elite: 0-15%, High: 16-30%, Medium: 31-45%, Low: 46%+
    """
    if total_changes == 0:
        return 0
    return (failed_changes / total_changes) * 100

# 예시
total = 80
failed = 4
cfr = change_failure_rate(total, failed)
print(f"CFR: {cfr:.1f}%")  # 5.0%

# DORA 기준 평가
if cfr <= 15:
    print("Elite performer")
elif cfr <= 30:
    print("High performer")
elif cfr <= 45:
    print("Medium performer")
else:
    print("Low performer")
```

CFR이 높다는 것은 변경이 충분히 테스트되지 않았거나, 카나리 검증이 없거나, 롤백 경로가 병목이라는 뜻입니다. 이 수치를 낮추려면 빌드 파이프라인, 테스트 커버리지, 모니터링 품질을 함께 개선해야 합니다.
## 이 코드에서 먼저 봐야 할 점

- Toil 감소의 출발점은 자동화 기술이 아니라 측정입니다.
- 점수화가 있어야 자동화 후보 우선순위를 설명할 수 있습니다.
- 손익분기점은 감이 아니라 투자 판단 근거가 됩니다.
- runbook은 끝이 아니라 코드화로 가는 중간 단계입니다.

## 여기서 자주 헷갈립니다

첫 번째 실수는 Toil 시간을 기록하지 않는 것입니다. 그러면 우선순위가 매번 가장 눈에 띄는 불편으로 바뀝니다.

두 번째 실수는 runbook이 있으니 충분하다고 생각하는 것입니다. 문서화는 중요하지만, 반복 절차를 사람이 계속 수행한다면 Toil은 아직 남아 있습니다.

세 번째 실수는 자동화 자체의 유지보수 비용을 무시하는 것입니다. 자동화도 코드이므로 오너와 관리 계획이 필요합니다.

## 운영 체크리스트

- [ ] 팀의 Toil 시간을 주기적으로 기록한다.
- [ ] 빈도와 소요 시간을 기준으로 자동화 후보를 정렬한다.
- [ ] 손익분기점을 계산해 투자 우선순위를 정한다.
- [ ] 자동화 코드에도 오너와 유지 계획이 있다.
- [ ] runbook을 코드로 옮길 후보를 따로 관리한다.

## 실무에서는 이렇게 생각합니다

시니어 엔지니어는 Toil을 단순 피로가 아니라 운영 부채로 봅니다. 반복 호출이 많다는 사실은 아직 시스템이나 절차 어딘가가 코드로 치환되지 않았다는 뜻이기 때문입니다.

또한 야간 복구, 로그 수집, 캐시 비우기, 공지 초안 만들기 같은 일은 작은 자동화만으로도 큰 효과를 낼 수 있습니다. 화려한 자동화보다 반복이 큰 작업을 먼저 없애는 편이 대개 더 현명합니다.

## 정리

Toil은 반복되고 자동화 가능한 수작업이 사람 시간을 지속적으로 소모하는 상태입니다. 중요한 점은 불편함을 줄이는 데서 끝나지 않고, 시간을 측정하고 우선순위를 정해 자동화 투자로 연결하는 데 있습니다.

다음 글에서는 capacity planning을 다룹니다. 앞으로 들어올 수요를 어떻게 예측하고, 어느 정도 헤드룸을 남겨야 하는지 이어서 정리하겠습니다.

## 처음 질문으로 돌아가기

- **Toil은 일반적인 운영 업무와 무엇이 다를까요?**
  - 본문의 기준은 Toil 줄이기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **팀 시간이 반복 수작업에 얼마나 쓰이는지 어떻게 재야 할까요?**
  - 자동화 비용과 인력 비용을 비교하면, 일부 Toil은 굳이 자동화할 필요가 없다는 판단도 나옵니다.
- **어떤 작업부터 자동화해야 투자 효과가 클까요?**
  - Toil을 줄이지 않으면 팀은 계속 반복 작업에 묶이고, 신뢰성 개선이나 기능 개발에 할애할 시간이 줄어듭니다.

<!-- toc:begin -->
## 시리즈 목차

- [SRE 101 (1/10): SRE란 무엇인가?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- [SRE 101 (5/10): Monitoring](./05-monitoring.md)
- [SRE 101 (6/10): Incident Response](./06-incident-response.md)
- [SRE 101 (7/10): Postmortem](./07-postmortem.md)
- **Toil 줄이기 (현재 글)**
- Capacity Planning (예정)
- 운영 가능한 시스템 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Eliminating Toil - Google SRE Book](https://sre.google/sre-book/eliminating-toil/)
- [Identifying and Tracking Toil - Google SRE Workbook](https://sre.google/workbook/eliminating-toil/)
- [Automating Operations - Google SRE Book](https://sre.google/sre-book/automation-at-google/)
- [Toil Reduction - Atlassian](https://www.atlassian.com/incident-management/devops/toil)

Tags: SRE, Toil, Automation, Productivity, Operations
