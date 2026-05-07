---
series: operating-systems-101
episode: 10
title: 컨테이너와 운영체제
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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
seo_description: namespace, cgroup, overlayfs — 컨테이너가 같은 커널 위에서 어떻게 격리된 환경을 만드는지 정리합니다.
last_reviewed: '2026-05-04'
---

# 컨테이너와 운영체제

> Operating Systems 101 시리즈 (10/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 컨테이너는 가상 머신과 무엇이 다르고, 같은 커널을 공유하면서 어떻게 "격리된 시스템"처럼 보이게 만들까요?

> 컨테이너는 마법이 아닙니다. namespace, cgroup, overlayfs 같은 리눅스 기본 기능의 조합일 뿐입니다. 시리즈에서 배운 프로세스, 메모리, 파일 시스템, 시스템 콜이 모두 컨테이너 안에서 다시 등장합니다. 이 글은 시리즈의 마무리이자, OS 개념이 현대 인프라로 이어지는 다리입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 컨테이너와 가상 머신의 차이
- namespace로 만드는 격리 — pid, net, mount, user 등
- cgroup으로 만드는 자원 한도 — CPU, 메모리, I/O
- overlayfs로 만드는 이미지 레이어와 copy-on-write 파일 시스템

## 왜 중요한가

컨테이너 시대에 OS를 안다는 것은 곧 namespace와 cgroup을 안다는 뜻입니다. 컨테이너에서 발생하는 OOM-kill, CPU throttling, 네트워크 격리 문제는 모두 OS 기본 기능 위에서 일어납니다. 컨테이너를 "그냥 가벼운 VM"으로만 알면, 정작 중요한 운영 사고에서 원인을 짚지 못합니다.

> 컨테이너는 새로운 OS가 아니라 같은 OS를 더 정밀하게 자르는 도구입니다.

## 개념 한눈에 보기

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

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| namespace | 프로세스에 보이는 자원(PID, 네트워크, 마운트 등)을 격리 |
| cgroup | 자원 사용 한도(CPU, 메모리, I/O)를 제어 |
| overlayfs | 읽기 전용 base 위에 read-write 레이어를 쌓는 파일 시스템 |
| capability | root 권한을 잘게 나눈 권한 단위 |
| OCI | 컨테이너 이미지/런타임 표준 |

## Before / After

**Before — "컨테이너는 가벼운 VM":**

```text
오해: VM과 같은 격리 수준
결과: "컨테이너 탈출"이 가능하다는 사실에 놀람
```

**After — "컨테이너는 호스트 커널을 공유":**

```text
사실: 격리는 namespace + cgroup + seccomp + capabilities의 조합
결과: 보안은 layered defense로 설계해야 함
```

차이를 알면 컨테이너의 한계를 인정하고 적절한 추가 보호(seccomp, rootless, gVisor 등)를 적용합니다.

## 실습: 단계별로 따라하기

### 1단계: 컨테이너 안의 PID 보기

```bash
docker run --rm -it alpine sh -c "ps -ef | head"
# 컨테이너 안에서 PID 1은 init이 아니라 sh
```

PID namespace 덕분에 컨테이너 안의 프로세스는 자기만의 PID 공간을 가집니다.

### 2단계: 호스트에서 같은 프로세스 보기

```bash
# 호스트에서
ps -ef | grep <container PID 명령어>
# 같은 프로세스가 다른 PID로 보임
```

호스트는 모든 컨테이너 프로세스를 볼 수 있고, 컨테이너는 호스트를 볼 수 없습니다. 격리는 비대칭입니다.

### 3단계: cgroup으로 메모리 한도

```bash
docker run --rm -m 64m alpine sh -c "
  cat /sys/fs/cgroup/memory.max
  yes 'data' | head -c 200m > /tmp/big || echo 'OOM-killed'
"
# memory.max = 67108864 (64MB), 200MB 쓰기는 OOM
```

cgroup이 한도를 강제합니다. 컨테이너 안에서는 free 명령이 호스트 전체를 보여줄 수 있어 자주 혼동의 원인입니다.

### 4단계: overlayfs 레이어 보기

```bash
# 이미지를 가져온 뒤
docker pull alpine
docker image inspect alpine | grep -i layer
# layered filesystem — 같은 base를 공유하면 디스크 절약
```

같은 base 이미지를 쓰는 컨테이너들은 disk를 공유합니다. 그래서 컨테이너는 "가볍다"고 느껴집니다.

### 5단계: capability와 seccomp 확인

```bash
docker run --rm alpine sh -c "
  cat /proc/self/status | grep Cap
"
# 기본은 root지만 capability 집합이 제한됨
```

기본 컨테이너의 root는 호스트 root보다 약합니다. capability와 seccomp가 권한을 잘게 자릅니다.

## 이 코드에서 주목할 점

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

## 실무에서는 이렇게 쓰입니다

- 마이크로서비스: 서비스당 컨테이너로 의존성 격리
- CI/CD: 빌드 환경을 이미지로 고정
- 멀티테넌트: cgroup으로 자원 보장 + 네트워크 namespace로 격리
- 서버리스: gVisor, Firecracker 같은 추가 격리 계층
- 개발 환경: docker compose / dev container로 환경 재현

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 컨테이너를 "OS의 편리한 사용법"으로 봅니다. namespace, cgroup, overlayfs를 모르고 컨테이너만 안다고 말하면, 운영 사고가 일어났을 때 손쓸 수 없습니다. 시리즈에서 본 프로세스, 메모리, 파일 시스템, 시스템 콜이 모두 컨테이너 안에서 다시 등장합니다.

또한 시니어는 격리의 한계를 인정합니다. 같은 커널을 공유한다는 사실은 보안 모델의 시작이지 끝이 아닙니다. seccomp, rootless, gVisor, 신뢰 경계 분리 같은 추가 보호를 항상 적절히 조합합니다. 격리는 "있다/없다"가 아니라 "어디까지"의 문제입니다.

## 체크리스트

- [ ] 컨테이너와 VM의 차이를 설명할 수 있다
- [ ] namespace와 cgroup의 역할을 안다
- [ ] 컨테이너 안에서 메모리 한도를 어떻게 보는지 안다
- [ ] overlayfs가 디스크 공유에 어떻게 기여하는지 안다
- [ ] 격리의 한계와 추가 보호 수단을 안다

## 연습 문제

1. 같은 base 이미지를 쓰는 두 컨테이너의 디스크 사용량 합과, base 이미지 크기를 비교해 overlayfs의 효과를 정량적으로 측정하세요.

2. 메모리 한도 64MB의 컨테이너에서 안전하게 도는 캐시 상한을 결정하고, OOM-kill이 나는 한도와 비교합니다.

3. seccomp 없이 docker run과, 기본 seccomp 프로파일이 적용된 docker run에서 차단되는 syscall 차이를 strace로 확인하세요.

## 정리 및 다음 단계

컨테이너는 새로운 OS가 아니라 리눅스 OS를 namespace, cgroup, overlayfs로 정밀하게 자르는 도구입니다. 이 시리즈에서 본 모든 OS 개념이 컨테이너 위에서 다시 활용됩니다. 컨테이너를 안다는 것은 결국 OS를 안다는 뜻입니다.

이 시리즈는 여기서 마무리됩니다. 다음 학습으로는 같은 OS 개념이 네트워크와 분산 시스템으로 확장되는 방향(컴퓨터 네트워크 101, 분산 시스템 101) 또는 컨테이너 운영 자체를 깊게 다루는 방향(도커 101, 쿠버네티스 101)을 권장합니다.

<!-- toc:begin -->
- [운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [프로세스와 스레드](./02-processes-and-threads.md)
- [스케줄링](./03-scheduling.md)
- [동시성과 race condition](./04-concurrency-and-race-conditions.md)
- [lock, mutex, semaphore](./05-locks-mutex-semaphore.md)
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
