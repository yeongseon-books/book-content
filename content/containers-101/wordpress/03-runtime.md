---
series: containers-101
episode: 3
title: "바이브코딩을 위한 컨테이너 기초 (3/10): Runtime"
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Containers
- Runtime
- containerd
- Docker
language: ko
---

# 바이브코딩을 위한 컨테이너 기초 (3/10): Runtime

이 글은 **바이브코딩을 위한 컨테이너 기초** 시리즈의 세 번째 글입니다.

바이브코딩으로 앱을 만들고 컨테이너 이미지까지 완성했습니다. 이제 이 이미지를 실제로 실행하는 것은 누구일까요? "Docker가 실행한다"고 답하기 쉽지만, 사실 실행은 여러 계층을 거칩니다. 이 계층을 이해하지 못하면 나중에 Kubernetes로 이동할 때 "왜 docker ps에 아무것도 안 보이지?"라는 상황에 막힙니다.

---

## 오늘의 핵심 질문

AI가 만든 앱을 Docker로 실행했는데 잘 됩니다. 나중에 Kubernetes로 이전했더니 `docker ps`에 컨테이너가 보이지 않습니다. 컨테이너가 사라진 걸까요? 아니면 다른 계층을 봐야 할까요?

> "Runtime의 핵심은 '더 빠르고 작다'는 게 아니라, 어디서 디버깅하고 어디서 스케일링을 제어할지 아는 것입니다."

---

## 이 글에서 다룰 문제

- Docker, containerd, runc는 왜 따로 존재할까요?
- 고수준 런타임과 저수준 런타임은 무엇이 다를까요?
- Docker에서 Kubernetes로 이동할 때 무엇이 달라질까요?
- 바이브코딩 앱을 디버깅할 때 어느 계층을 봐야 할까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

---

## 바이브코딩 관점에서 런타임 계층이 중요한 이유

AI가 만든 앱을 로컬에서 Docker로 실행하면 `docker ps`로 확인할 수 있습니다. 그런데 팀이 Kubernetes를 도입하거나 클라우드 서비스(ECS, Cloud Run)로 이전하면 `docker ps`는 빈 화면을 보여줍니다.

이건 컨테이너가 사라진 게 아닙니다. 관찰 계층이 달라진 것입니다.

```text
docker run nginx
↓
docker CLI → dockerd → containerd → containerd-shim → runc → 컨테이너 프로세스
```

`docker run`을 입력하면 이 흐름이 일어납니다. Kubernetes는 Docker를 거치지 않고 containerd에 직접 말을 겁니다. 그래서 Kubernetes 환경에서는 `docker ps`가 아니라 `crictl ps`를 써야 합니다.

### 런타임 계층 구조

```text
사용자/오케스트레이터
        ↓
Docker CLI 또는 CRI 클라이언트
        ↓
    containerd
        ↓
      runc
        ↓
  격리된 프로세스
```

**핵심 용어:**

- **Docker**: 사용자가 가장 자주 만나는 고수준 CLI와 데몬 조합입니다.
- **containerd**: 컨테이너 생명주기를 관리하는 데몬입니다.
- **runc**: OCI 표준에 맞춰 컨테이너를 실제로 실행하는 저수준 실행기입니다.
- **CRI**: Kubernetes가 런타임과 통신할 때 사용하는 인터페이스입니다.
- **OCI**: 컨테이너 이미지와 런타임 호환성의 기반이 되는 표준입니다.

---

## 적용 전후: 디버깅 계층이 달라질 때

**Before**: Docker만 알고 Kubernetes를 만납니다.

```text
장애 발생
→ docker ps → 비어 있음
→ "컨테이너가 사라졌다"
→ 막막함
```

**After**: 런타임 계층을 알고 적절한 도구를 씁니다.

```text
장애 발생
→ docker ps -a → 상태 확인 (Docker 환경)
→ crictl ps -a → 상태 확인 (Kubernetes 환경)
→ journalctl -u containerd → 데몬 오류 확인
→ 문제 계층 특정 → 정확한 조치
```

환경이 달라도 문제 해결 순서는 같습니다. 어느 계층을 보는지만 달라집니다.

---

## 자주 하는 실수

| 실수 | 결과 | 해결 방법 |
|------|------|-----------|
| Docker만 배우고 containerd를 건너뜀 | Kubernetes 노드 디버깅 불가 | `crictl`과 `ctr` 기본 사용법 익히기 |
| Kubernetes 노드를 `docker` CLI로 디버깅 | 컨테이너가 안 보임 | `crictl ps`로 전환 |
| 노드마다 런타임 버전 차이 방치 | 재현 어려운 장애 | 구성 관리 도구로 버전 통일 |
| root 실행 검토 없이 배포 | 보안 위험 | rootless 옵션 검토 |
| 런타임 계층을 단일로 생각 | 잘못된 계층에서 디버깅 | Docker/containerd/runc 역할 분리 이해 |

---

## AI 팁: 런타임 관련 에러 디버깅

Kubernetes나 클라우드 환경에서 컨테이너 관련 에러가 나면:

```
다음 환경에서 컨테이너가 시작되지 않습니다:
- 환경: [Docker/Kubernetes/ECS 중 선택]
- 에러 메시지: [에러 내용]
- 이미지: [이미지명:태그]

어느 계층(Docker, containerd, runc, CRI)에서 문제가 발생했을지
판단하고, 각 계층별로 확인할 명령을 알려주세요.
```

AI는 에러 메시지를 분석해서 어느 계층 문제인지, 어떤 명령으로 확인해야 하는지 알려줍니다.

---

## 체크리스트

- [ ] containerd와 runc의 역할 차이를 설명할 수 있습니다
- [ ] Docker 환경과 Kubernetes 환경에서 디버깅 도구가 다르다는 것을 압니다
- [ ] CRI가 Kubernetes와 런타임을 연결하는 인터페이스임을 이해합니다
- [ ] `docker run`이 내부적으로 어떤 계층을 거치는지 설명할 수 있습니다
- [ ] OCI 표준이 런타임 호환성의 기반임을 이해합니다

---

## 처음 질문으로 돌아가기

**Kubernetes로 이전했을 때 `docker ps`에 컨테이너가 보이지 않는 이유는?**

Kubernetes 1.24 이후 kubelet은 Docker를 거치지 않고 containerd에 직접 말을 겁니다. Docker 데몬은 이 컨테이너를 인식하지 못하므로 `docker ps`에 보이지 않습니다. 컨테이너는 정상 실행 중이지만, 관찰 도구를 `crictl ps`로 바꿔야 합니다.

---

## 정리

컨테이너 실행은 Docker 하나가 모두 맡는 단일 구조가 아닙니다. 사용자 경험, 생명주기 관리, 저수준 실행이 계층으로 나뉘어 있고, Kubernetes는 그 위에 CRI를 통해 올라탑니다. 이 구조를 이해해야 환경이 달라져도 당황하지 않습니다.

다음 글에서는 이 런타임이 실행할 이미지를 어떻게 작성하는지, 즉 Dockerfile을 살펴봅니다.

---

## 참고 자료

- [containerd 공식 문서](https://containerd.io/docs/)
- [Kubernetes CRI](https://kubernetes.io/docs/concepts/architecture/cri/)
- [OCI 표준](https://opencontainers.org/)
- Containers 101 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/containers-101/ko

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 컨테이너 기초 (1/10): Container란 무엇인가?
- 바이브코딩을 위한 컨테이너 기초 (2/10): Image와 Layer
- **바이브코딩을 위한 컨테이너 기초 (3/10): Runtime (현재 글)**
- 바이브코딩을 위한 컨테이너 기초 (4/10): Dockerfile
- 바이브코딩을 위한 컨테이너 기초 (5/10): Volume
- 바이브코딩을 위한 컨테이너 기초 (6/10): Network
- 바이브코딩을 위한 컨테이너 기초 (7/10): Registry
- 바이브코딩을 위한 컨테이너 기초 (8/10): Container Security
- 바이브코딩을 위한 컨테이너 기초 (9/10): Containers vs VMs
- 바이브코딩을 위한 컨테이너 기초 (10/10): 실전 컨테이너 앱 만들기

<!-- toc:end -->

Tags: 바이브코딩, Containers, Docker, Runtime, DevOps
