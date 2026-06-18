---
series: distributed-systems-101
episode: 2
title: "바이브코딩을 위한 분산 시스템 기초 (2/10): 장애 모델"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 분산시스템
  - 장애모델
  - 크래시
  - 비잔틴
  - 신뢰성
language: ko
---

# 바이브코딩을 위한 분산 시스템 기초 (2/10): 장애 모델

이 글은 **바이브코딩을 위한 분산 시스템 기초** 시리즈의 2편입니다. AI가 만든 서비스를 스케일하려면 장애가 어떤 종류로 나타나는지부터 구분해야 합니다. 장애를 모델링하지 않으면 알고리즘도, 운영 비용도 말할 수 없습니다.

---

AI에게 "서버가 죽으면 어떻게 처리할까요?"라고 물으면 try-except 코드를 만들어 줍니다. 그런데 실제 운영에서 "서버가 죽었다"는 말 안에는 프로세스가 멈춘 것, 패킷이 빠지는 것, 너무 느려서 살아 있어도 죽은 것처럼 보이는 것이 뒤섞여 있습니다. 이를 구분하지 못하면 잘못된 처방을 내리게 됩니다.

운영 채널에서 "서버가 죽었습니다"라고 말할 때, 실제로는 여러 종류의 사건이 한 문장에 섞여 있습니다.

> "장애 모델은 알고리즘의 가격표입니다. 어떤 장애를 가정하느냐에 따라 필요한 노드 수와 비용이 결정됩니다."

## 이 글에서 다룰 질문들

- 장애 모델이란 무엇이며 왜 장애를 모델링해야 할까요?
- crash, omission, timing, Byzantine은 어떻게 다를까요?
- 네트워크 파티션은 왜 별도 범주로 봐야 할까요?
- AI가 생성한 코드의 장애 처리가 충분한지 어떻게 판단할까요?
- 바이브코딩 프로젝트에서 어떤 장애 모델을 선택해야 할까요?

---

## 바이브코딩과 장애 모델: AI 코드가 놓치는 것

AI가 생성한 에러 처리 코드는 대부분 "성공/실패" 이분법으로 작성됩니다. 하지만 분산 환경에서 실패는 훨씬 복잡합니다.

### Before: AI가 만든 단순한 에러 처리

```python
# AI가 생성한 전형적인 에러 처리
try:
    result = payment_service.charge(amount)
    return {"ok": True}
except Exception as e:
    return {"error": str(e)}  # 모든 장애를 같은 방식으로 처리
```

이 코드는 crash 장애와 timing 장애를 구분하지 않습니다. 결과적으로 타임아웃 시에도 "실패"로 처리해 중복 결제 위험이 생깁니다.

### After: 장애 유형을 구분한 처리

```python
# 장애 유형을 구분해서 처리
import requests

def charge_with_model(amount: int, idempotency_key: str):
    try:
        result = payment_service.charge(
            amount,
            idempotency_key=idempotency_key,
            timeout=2.0
        )
        return {"status": "success", "id": result.id}

    except requests.exceptions.ConnectionError:
        # Crash 장애: 서버가 죽음 — 재시도 안전
        return {"status": "failed", "retryable": True}

    except requests.exceptions.ReadTimeout:
        # Timing 장애: 모름 상태 — 결제됐는지 확인 필요
        return {"status": "unknown", "key": idempotency_key}

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            # Crash-like: 영구 실패 — 재시도 불필요
            return {"status": "failed", "retryable": False}
```

---

## 장애 모델 스펙트럼

오른쪽으로 갈수록 더 험한 세계를 가정합니다. 가정이 험할수록 알고리즘은 비싸지고 노드가 더 필요합니다.

```
Crash (fail-stop) ⊂ Crash-recovery ⊂ Omission ⊂ Timing ⊂ Byzantine
────────────────────────────────────────────────────────────────────
약한 가정 (cheap)  ────────────────────────────────→  강한 가정 (expensive)
```

| 모델 | 설명 | f개 장애 허용 시 최소 노드 | 대표 시스템 |
|------|------|--------------------------|------------|
| Crash (fail-stop) | 노드가 멈추면 그대로 남음 | 2f+1 | Raft, Paxos |
| Crash-recovery | 죽었다 다시 살아남 | 2f+1 | Kafka, PostgreSQL |
| Omission | 메시지를 가끔 누락 | 2f+1 | 재전송 프로토콜 |
| Timing | 응답이 임의로 매우 느려짐 | 2f+1 | 적응형 타임아웃 |
| Byzantine | 거짓말하거나 임의의 행동 | 3f+1 | BFT, 블록체인 |

---

## 자주 하는 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| 모든 장애를 crash로만 가정 | 파티션 시 알고리즘이 잘못 수렴 | 네트워크 파티션을 별도로 고려 |
| 타임아웃을 너무 짧게 설정 | 살아 있는 노드를 죽었다고 오판 | 측정 기반 적응형 타임아웃 사용 |
| 불필요하게 Byzantine 모델 적용 | 비용이 급격히 커짐 | 내부 서비스는 crash 모델로 충분 |
| 파티션 무시 | 클라우드에서 일상적으로 발생하는 사건을 처리 못 함 | CP/AP 정책을 명시적으로 선택 |
| 완벽한 장애 감지기 기대 | 비동기 모델에서 불가능 | false positive/negative 트레이드오프 수용 |

---

## AI 팁: AI 코드의 장애 처리를 강화하는 법

1. **타임아웃 분리**: `ConnectionError`와 `ReadTimeout`을 구분해서 처리하도록 AI에게 요청하세요.
2. **모름 상태 명시**: 타임아웃 발생 시 "실패"가 아닌 "unknown" 상태를 반환하도록 수정하세요.
3. **재시도 가능 여부 표시**: 각 예외 처리에 `retryable: True/False`를 포함시키세요.
4. **장애 모델 문서화**: 서비스의 `README`나 설정 파일에 어떤 장애 모델을 가정하는지 명시하세요.

```python
# AI에게 이렇게 요청하면 더 나은 코드가 나옵니다
# "결제 서비스 호출 코드를 작성할 때 ConnectionError, ReadTimeout, HTTPError를
# 각각 다르게 처리하고, 타임아웃 시에는 idempotency_key를 포함한 unknown 상태를
# 반환하도록 해줘"
```

---

## 실전 체크리스트

- [ ] crash와 omission의 차이를 한 줄로 말할 수 있다
- [ ] Byzantine이 왜 더 비싼지 설명할 수 있다
- [ ] 파티션이 노드 장애와 어떻게 다른지 말할 수 있다
- [ ] 타임아웃 기반 감지가 왜 불완전한지 알고 있다
- [ ] 내가 만드는 서비스가 어떤 장애 모델을 가정하는지 답할 수 있다
- [ ] AI가 생성한 코드에서 장애 유형이 구분되어 있는지 확인했다

---

## 처음 질문으로 돌아가기

- **장애 모델이란 무엇이며 왜 장애를 모델링해야 할까요?**
  장애 모델은 "노드가 어떤 방식으로 망가질 수 있는가"에 대한 가정입니다. 이 가정이 없으면 알고리즘의 정확성과 비용을 계산할 수 없습니다.

- **crash, omission, timing, Byzantine은 어떻게 다를까요?**
  crash는 멈추는 것, omission은 메시지를 빠뜨리는 것, timing은 느려지는 것, Byzantine은 거짓말하는 것입니다. 오른쪽으로 갈수록 대응 비용이 급격히 커집니다.

- **AI가 생성한 코드의 장애 처리가 충분한지 어떻게 판단할까요?**
  타임아웃과 ConnectionError를 구분하는지, 타임아웃 시 재시도 안전성을 표시하는지, 영구 실패와 일시 실패를 다르게 처리하는지를 확인하세요.

---

## 정리

장애 모델은 서비스 설계의 출발점입니다. 어떤 장애를 가정하느냐에 따라 알고리즘, 노드 수, 운영 비용이 결정됩니다. 대부분의 내부 서비스는 crash-recovery 모델로 충분하고, 외부 참여자가 있는 시스템만 Byzantine 비용을 감수합니다. 다음 글에서는 이런 장애 모델 위에서 노드들이 실제로 어떻게 통신하는지, 즉 RPC와 메시지 전달을 다룹니다.

---

## 참고 자료

- [Failure semantics (Wikipedia)](https://en.wikipedia.org/wiki/Failure_semantics)
- [Byzantine fault (Wikipedia)](https://en.wikipedia.org/wiki/Byzantine_fault)
- [Network partition (Wikipedia)](https://en.wikipedia.org/wiki/Network_partition)
- [Designing Data-Intensive Applications — chapter 8](https://dataintensive.net/)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 분산 시스템 기초 (1/10): 분산 시스템이란 무엇인가?
- **바이브코딩을 위한 분산 시스템 기초 (2/10): 장애 모델 (현재 글)**
- 바이브코딩을 위한 분산 시스템 기초 (3/10): RPC와 메시지 전달
- 바이브코딩을 위한 분산 시스템 기초 (4/10): 일관성과 CAP
- 바이브코딩을 위한 분산 시스템 기초 (5/10): 복제
- 바이브코딩을 위한 분산 시스템 기초 (6/10): 합의와 Raft
- 바이브코딩을 위한 분산 시스템 기초 (7/10): 리더 선출
- 바이브코딩을 위한 분산 시스템 기초 (8/10): 메시지 큐와 이벤트 소싱
- 바이브코딩을 위한 분산 시스템 기초 (9/10): 분산 트랜잭션
- 바이브코딩을 위한 분산 시스템 기초 (10/10): 운영 가능한 분산 패턴
<!-- toc:end -->

Tags: 바이브코딩, 분산시스템, 장애모델, 크래시, 비잔틴, 신뢰성
