---
series: operating-systems-101
episode: 10
title: 컨테이너와 운영체제
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 운영체제
  - 컨테이너
  - namespace
  - cgroup
  - 격리
seo_description: namespace, cgroup, overlayfs로 컨테이너 격리가 만들어지는 방식을 정리합니다.
last_reviewed: '2026-05-12'
---

# 컨테이너와 운영체제

컨테이너는 새로운 운영체제를 발명한 것이 아닙니다. 이미 운영체제 안에 있던 기능을 더 촘촘하게 조합해서, 한 커널 위에 여러 격리된 실행 환경을 만든 것입니다.

그래서 컨테이너를 제대로 이해하려면 결국 프로세스, 메모리, 파일 시스템, 시스템 콜을 다시 운영체제 관점에서 읽어야 합니다. 이 글은 그 연결을 한 번에 묶는 시리즈의 마무리입니다.

이 글은 Operating Systems 101 시리즈의 10번째 글입니다.

## 이 글에서 다룰 문제

- 컨테이너와 가상 머신은 격리 방식이 어떻게 다를까요?
- namespace는 "무엇이 보이는가"를, cgroup은 "얼마나 쓸 수 있는가"를 어떻게 나눌까요?
- overlayfs는 왜 컨테이너 이미지를 가볍게 느끼게 만들까요?
- 컨테이너 격리의 한계를 알면 어떤 추가 보호를 설계할 수 있을까요?

> 컨테이너는 운영체제를 대체하는 새 계층이 아니라, 같은 커널을 더 잘게 나누는 운영 기법입니다. 보이는 자원은 namespace로 끊고, 쓸 수 있는 양은 cgroup으로 제한하고, 파일 계층은 overlayfs로 쌓아 올립니다.

## 기본 모델
> VM은 하이퍼바이저 위에 게스트 OS를 통째로 올립니다. 컨테이너는 호스트 커널을 그대로 쓰고, namespace로 "보이는 것"을 격리하고, cgroup으로 "쓸 수 있는 자원"을 제한합니다. 따라서 컨테이너는 가볍고 빠르게 시작하지만, 커널 취약점은 호스트와 공유합니다.

```text
[VM]                          [Container]
+-----------+                 +-----------+
| Guest OS  |                 |   App     |
+-----------+                 +-----------+
| Hypervisor|                 |  cgroup   |
+-----------+                 |  ns       |
|  Host OS  |                 +-----------+
+-----------+                 |  Host OS  |
|  HW       |                 +-----------+
+-----------+                 |  HW       |
                              +-----------+
```

## 같은 코드를 다르게 읽는 법

**이전 관점 — "컨테이너는 가벼운 가상 머신":**

```text
Misconception: same isolation level as a VM
Result: surprised that "container escape" is even a thing
```

**바꿔서 보면 — "컨테이너는 호스트 커널을 공유한다":**

```text
Truth: isolation is namespaces + cgroups + seccomp + capabilities together
Result: security must be designed as layered defense
```

차이를 알면 컨테이너의 한계를 인정하고 적절한 추가 보호(seccomp, rootless, gVisor 등)를 적용합니다.

## 단계별로 확인하기

### 1단계: 컨테이너 안의 프로세스 번호 보기

```bash
docker run --rm -it alpine sh -c "ps -ef | head"
# Inside the container, PID 1 is sh, not init
```

PID namespace 덕분에 컨테이너 안의 프로세스는 자기만의 PID 공간을 가집니다.

### 2단계: 호스트에서 같은 프로세스 보기

```bash
# On the host
ps -ef | grep <container PID command>
# The same process appears with a different PID
```

호스트는 모든 컨테이너 프로세스를 볼 수 있고, 컨테이너는 호스트를 볼 수 없습니다. 격리는 비대칭입니다.

### 3단계: 제어 그룹으로 메모리 한도 보기

```bash
docker run --rm -m 64m alpine sh -c "
  cat /sys/fs/cgroup/memory.max
  yes 'data' | head -c 200m > /tmp/big || echo 'OOM-killed'
"
# memory.max = 67108864 (64MB), 200MB write → OOM
```

cgroup이 한도를 강제합니다. 컨테이너 안에서는 free 명령이 호스트 전체를 보여줄 수 있어 자주 혼동의 원인입니다.

### 4단계: 계층형 파일 시스템 레이어 보기

```bash
docker pull alpine
docker image inspect alpine | grep -i layer
# Layered file system — sharing a base saves disk
```

같은 기반 이미지를 쓰는 컨테이너들은 디스크 계층을 공유합니다. 그래서 컨테이너가 가볍게 느껴집니다.

### 5단계: 세분 권한과 보안 필터 확인

```bash
docker run --rm alpine sh -c "
  cat /proc/self/status | grep Cap
"
# Even as root, the capability set is restricted
```

기본 컨테이너의 root는 호스트 root보다 약합니다. capability와 seccomp가 권한을 잘게 자릅니다.

## 여기서 먼저 볼 점

- 격리는 "namespace + cgroup + seccomp + capabilities"의 합입니다
- 컨테이너 안의 PID 1은 컨테이너의 init이고, 호스트에서는 일반 프로세스
- cgroup 한도와 free 명령의 시야가 달라 자주 혼동을 만듭니다
- overlayfs 덕분에 같은 이미지를 쓰는 컨테이너는 디스크를 공유합니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 컨테이너 = VM 가정 | 보안 격리 과대평가 | layered defense (seccomp, rootless 등) |
| 컨테이너 안 free로 메모리 판단 | 호스트 전체를 봄 | cgroup 파일 또는 docker stats |
| privileged 모드 남용 | 격리 사실상 무력화 | 필요한 capability만 추가 |
| 거대한 single-layer 이미지 | 빌드/배포 느림, 캐시 무력 | 다단계 빌드 + 작은 base |
| init 프로세스 없이 PID 1 직접 사용 | 좀비 수확 안 됨 | tini 등 init 사용 또는 --init |

## 실무에서는 이렇게 본다

- 마이크로서비스: 서비스당 컨테이너로 의존성 격리
- CI/CD: 빌드 환경을 이미지로 고정
- 멀티테넌트: cgroup으로 자원 보장 + 네트워크 namespace로 격리
- 서버리스: gVisor, Firecracker 같은 추가 격리 계층
- 개발 환경: docker compose / dev container로 환경 재현

## 체크리스트

- [ ] 컨테이너와 VM의 차이를 설명할 수 있다
- [ ] namespace와 cgroup의 역할을 안다
- [ ] 컨테이너 안에서 메모리 한도를 어떻게 보는지 안다
- [ ] overlayfs가 디스크 공유에 어떻게 기여하는지 안다
- [ ] 격리의 한계와 추가 보호 수단을 안다

## 마무리와 다음 글

컨테이너는 새로운 운영체제가 아니라 리눅스 커널을 namespace, cgroup, overlayfs로 정밀하게 나누는 도구입니다. 이 시리즈에서 본 운영체제 개념이 컨테이너 위에서 다시 등장합니다. 컨테이너를 이해하면 운영체제가 더 선명해집니다.

이 시리즈는 여기서 마무리됩니다. 다음 학습으로는 같은 OS 개념이 네트워크와 분산 시스템으로 확장되는 방향(컴퓨터 네트워크 101, 분산 시스템 101) 또는 컨테이너 운영 자체를 깊게 다루는 방향(도커 101, 쿠버네티스 101)을 권장합니다.

<!-- toc:begin -->
- [운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [프로세스와 스레드](./02-processes-and-threads.md)
- [스케줄링](./03-scheduling.md)
- [동시성과 경쟁 상태](./04-concurrency-and-race-conditions.md)
- [락, 뮤텍스, 세마포어](./05-locks-mutex-semaphore.md)
- [메모리 관리](./06-memory-management.md)
- [가상 메모리](./07-virtual-memory.md)
- [파일 시스템](./08-file-systems.md)
- [시스템 콜](./09-system-calls.md)
- **컨테이너와 운영체제 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Linux namespaces(7)](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Linux cgroups(7)](https://man7.org/linux/man-pages/man7/cgroups.7.html)
- [Open Container Initiative](https://opencontainers.org/)
- [Docker — Overview](https://docs.docker.com/get-started/overview/)

Tags: Computer Science, 운영체제, 컨테이너, namespace, cgroup, 격리
