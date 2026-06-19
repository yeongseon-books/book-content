---
series: operating-systems-101
episode: 10
title: "Operating Systems 101 (10/10): 컨테이너와 운영체제"
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
last_reviewed: '2026-05-15'
---

# Operating Systems 101 (10/10): 컨테이너와 운영체제

컨테이너는 새로운 운영체제를 발명한 것이 아닙니다. 이미 운영체제 안에 있던 기능을 더 촘촘하게 조합해서, 한 커널 위에 여러 격리된 실행 환경을 만든 것입니다.

그래서 컨테이너를 제대로 이해하려면 결국 프로세스, 메모리, 파일 시스템, 시스템 콜을 다시 운영체제 관점에서 읽어야 합니다. 이 글은 그 연결을 한 번에 묶는 시리즈의 마무리입니다.

이 글은 Operating Systems 101 시리즈의 마지막 글입니다.

![Operating Systems 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/10/10-01-the-layers-that-create-container-isolati.ko.png)
*Operating Systems 101 10장 흐름 개요*

## 이 글에서 다룰 문제

- 컨테이너와 가상 머신은 격리 방식이 어떻게 다를까요?
- namespace는 "무엇이 보이는가"를, cgroup은 "얼마나 쓸 수 있는가"를 어떻게 나눌까요?
- overlayfs는 왜 컨테이너 이미지를 가볍게 느끼게 만들까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 기본 모델

> VM은 하이퍼바이저 위에 게스트 OS를 통째로 올립니다. 컨테이너는 호스트 커널을 그대로 쓰고, namespace로 "보이는 것"을 격리하고, cgroup으로 "쓸 수 있는 자원"을 제한합니다. 따라서 컨테이너는 가볍고 빠르게 시작하지만, 커널 취약점은 호스트와 공유합니다.

### 컨테이너 격리를 이루는 층

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

### Linux namespace 종류와 역할

```text
PID  namespace : 프로세스 번호 공간 격리
NET  namespace : 네트워크 인터페이스, 라우팅 테이블 격리
MNT  namespace : 파일시스템 마운트 포인트 격리
UTS  namespace : 호스트명, 도메인명 격리
IPC  namespace : System V IPC, POSIX 메시지 큐 격리
USER namespace : 사용자/그룹 ID 매핑 격리
TIME namespace : 시스템 시계 격리 (Linux 5.6+)
```

컨테이너 런타임은 이 7가지를 조합해서 "독자적인 세계"를 만듭니다.

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

cgroup이 한도를 강제합니다. 컨테이너 안에서는 `free` 명령이 호스트 전체를 보여줄 수 있어 자주 혼동의 원인입니다.

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

## 자주 하는 실수

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

## 운영 체크리스트

- [ ] 컨테이너와 VM의 차이를 설명할 수 있다
- [ ] namespace와 cgroup의 역할을 안다
- [ ] 컨테이너 안에서 메모리 한도를 어떻게 보는지 안다
- [ ] overlayfs가 디스크 공유에 어떻게 기여하는지 안다
- [ ] 격리의 한계와 추가 보호 수단을 안다

## 시스템 관찰: 컨테이너에서도 OS 지표를 그대로 읽기

컨테이너는 인터페이스가 다를 뿐, 본질적으로 운영체제 지표를 읽는 작업입니다.

### 컨테이너 내부 `/proc` 출력 확인

```bash
docker run --rm alpine sh -c "
  echo '--- /proc/1/status ---';
  cat /proc/1/status | grep -E 'Name|State|Pid|PPid|Threads|VmRSS';
  echo '--- cgroup ---';
  cat /proc/1/cgroup;
"
```

```text
Name:   sh
State:  S (sleeping)
Pid:    1
PPid:   0
Threads: 1
VmRSS:  1188 kB
```

컨테이너 내부의 PID 1 동작을 보면 signal 전달, 좀비 회수 문제를 조기에 확인할 수 있습니다.

### PID 1 문제와 좀비 프로세스

컨테이너에서 PID 1은 일반 init과 달리 자식 프로세스 회수(reaping) 기능이 없을 수 있습니다.

```bash
# 문제: bash 스크립트를 직접 PID 1로 실행하면
# 서브프로세스가 종료되어도 수확되지 않아 좀비가 쌓임

# 해결 1: --init 플래그 사용
docker run --init --rm alpine sh -c "sleep 1 & wait"

# 해결 2: tini를 명시적으로 entrypoint로 설정
# ENTRYPOINT ["/sbin/tini", "--"]
```

### cgroup CPU 제한이 스케줄링에 주는 효과

```bash
docker run --rm --cpus=0.5 alpine sh -c "yes > /dev/null" &
# 호스트에서: docker stats 로 CPU % 확인
docker stats --no-stream
```

CPU quota가 낮으면 runnable 상태라도 실제 실행 비율이 제한됩니다. "CPU 사용률은 100%인데 느리다"는 증상은 종종 quota throttling 때문입니다.

```bash
# cgroup CPU throttling 상태 직접 확인
cat /sys/fs/cgroup/cpu/docker/<container_id>/cpu.stat
# nr_throttled: 쓰로틀링된 횟수
# throttled_time: 쓰로틀링된 총 시간(나노초)
```

### overlayfs 레이어 구조 이해

```bash
# 레이어 개수와 크기 확인
docker history ubuntu:22.04
# IMAGE       CREATED       CREATED BY              SIZE
# <hash>      2 weeks ago   /bin/sh -c #(nop) CMD   0B
# <hash>      2 weeks ago   /bin/sh -c apt-get ...  77.8MB
# <hash>      2 weeks ago   /bin/sh -c #(nop) ADD   77.8MB
```

각 `RUN` 명령은 새 레이어를 만듭니다. 레이어가 많아질수록 이미지 빌드 캐시를 활용하기 좋지만, 레이어 수에 한계도 있습니다.

```dockerfile
# 비효율: 레이어 3개
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# 효율: 레이어 1개
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
```

### 컨테이너 장애를 볼 때 먼저 나누는 기준

| 증상 | 먼저 볼 것 | 연결되는 OS 계층 |
| --- | --- | --- |
| 컨테이너가 갑자기 종료됨 | `docker ps -a`, 종료 코드, OOM 여부 | cgroup 메모리 한도 |
| 안에서는 되는데 외부 통신이 안 됨 | 포트 매핑, 네트워크 namespace, 정책 | namespace / 네트워크 스택 |
| CPU는 남는데 응답이 들쭉날쭉함 | `docker stats`, throttling, CPU quota | cgroup CPU 스케줄링 |
| 파일이 사라지거나 느림 | overlayfs 레이어, bind mount, volume | 파일 시스템 / overlayfs |
| root인데도 어떤 명령이 실패 | capability, seccomp, rootless 여부 | 권한 모델 |

### 보안 계층 점검 순서

```bash
# 1. privileged 여부 확인
docker inspect <container> | grep -i privileged

# 2. capability 목록 확인
docker run --rm alpine sh -c "cat /proc/1/status | grep Cap"
# CapPrm, CapEff, CapBnd 등 — 숫자를 capsh로 해석 가능

# 3. seccomp 프로파일 확인
docker info | grep -i seccomp
```

컨테이너 보안은 단일 옵션이 아니라 커널 권한 표면을 단계적으로 줄이는 설계 문제입니다.

### 이 시리즈의 OS 개념이 컨테이너에서 다시 등장하는 방식

| OS 개념 (글) | 컨테이너에서의 모습 |
| --- | --- |
| 프로세스 (2장) | PID namespace로 격리된 프로세스 트리 |
| 스케줄링 (3장) | cgroup CPU quota로 제어되는 CFS 스케줄링 |
| 메모리 관리 (6장) | cgroup memory.max로 강제되는 OOM 제한 |
| 가상 메모리 (7장) | 공유 커널 페이지 테이블, 컨테이너별 가상 공간 |
| 파일 시스템 (8장) | overlayfs로 계층화된 이미지 파일시스템 |
| 시스템 콜 (9장) | seccomp 필터로 제한된 syscall 표면 |

## 처음 질문으로 돌아가기

- **컨테이너와 가상 머신은 격리 방식이 어떻게 다를까요?**
  - VM은 하이퍼바이저가 하드웨어를 가상화해 각 VM이 완전히 독립된 OS를 실행합니다. 컨테이너는 호스트 커널 위에서 namespace로 시야를 격리하고 cgroup으로 자원을 제한할 뿐입니다. 따라서 VM은 커널도 독립이지만 컨테이너는 커널을 공유합니다. 시작 시간은 컨테이너가 훨씬 빠르지만, 커널 취약점은 모든 컨테이너가 공유합니다.
- **namespace는 "무엇이 보이는가"를, cgroup은 "얼마나 쓸 수 있는가"를 어떻게 나눌까요?**
  - namespace는 PID, 네트워크, 마운트, UTS, IPC 등의 시야를 컨테이너별로 분리합니다. 컨테이너 안에서는 자기 namespace 안의 자원만 보입니다. cgroup은 CPU 시간, 메모리, 디스크 I/O 등의 사용량을 그룹별로 제한합니다. 둘을 합쳐서 "보이는 것을 자기 것으로, 쓸 수 있는 양은 정해진 한도 안에서"가 성립합니다.
- **overlayfs는 왜 컨테이너 이미지를 가볍게 느끼게 만들까요?**
  - overlayfs는 여러 파일시스템 레이어를 하나로 겹쳐 보여주는 기술입니다. 컨테이너 이미지의 베이스 레이어는 여러 컨테이너가 공유하고, 각 컨테이너는 자기 변경 사항만 추가 레이어에 씁니다. 100개의 컨테이너가 같은 ubuntu 베이스를 써도 디스크는 한 벌만 씁니다.

## 연습 문제

1. 같은 베이스 이미지를 공유하는 컨테이너 두 개를 만들고, 실제 디스크 사용량이 어떻게 절약되는지 확인해 보세요.
2. 64MB 메모리 한도가 있는 컨테이너에서 안전한 캐시 상한을 계산하고, 어느 값에서 OOM-kill이 나는지 비교해 보세요.
3. 기본 seccomp 프로파일이 있을 때와 없을 때 `strace`로 어떤 시스템 콜이 차단되는지 비교해 보세요.

## 마무리

컨테이너는 새로운 운영체제가 아니라 리눅스 커널을 namespace, cgroup, overlayfs로 정밀하게 나누는 도구입니다. 이 시리즈에서 본 운영체제 개념이 컨테이너 위에서 다시 등장합니다. 컨테이너를 이해하면 운영체제가 더 선명해집니다.

이 시리즈는 여기서 마무리됩니다. 다음 학습으로는 같은 OS 개념이 네트워크와 분산 시스템으로 확장되는 방향(컴퓨터 네트워크 101, 분산 시스템 101) 또는 컨테이너 운영 자체를 깊게 다루는 방향(도커 101, 쿠버네티스 101)을 권장합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Operating Systems 101 (1/10): 운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [Operating Systems 101 (2/10): 프로세스와 스레드](./02-processes-and-threads.md)
- [Operating Systems 101 (3/10): 스케줄링](./03-scheduling.md)
- [Operating Systems 101 (4/10): 동시성과 경쟁 상태](./04-concurrency-and-race-conditions.md)
- [Operating Systems 101 (5/10): 락, 뮤텍스, 세마포어](./05-locks-mutex-semaphore.md)
- [Operating Systems 101 (6/10): 메모리 관리](./06-memory-management.md)
- [Operating Systems 101 (7/10): 가상 메모리](./07-virtual-memory.md)
- [Operating Systems 101 (8/10): 파일 시스템](./08-file-systems.md)
- [Operating Systems 101 (9/10): 시스템 콜](./09-system-calls.md)
- **Operating Systems 101 (10/10): 컨테이너와 운영체제 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Operating Systems 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/operating-systems-101/ko)
- [Linux namespaces(7)](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Linux cgroups(7)](https://man7.org/linux/man-pages/man7/cgroups.7.html)
- [Open Container Initiative](https://opencontainers.org/)
- [Docker — Overview](https://docs.docker.com/get-started/overview/)
- [Rootless mode (Docker Docs)](https://docs.docker.com/engine/security/rootless/)
- [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec)

Tags: Computer Science, 운영체제, 컨테이너, namespace, cgroup, 격리
