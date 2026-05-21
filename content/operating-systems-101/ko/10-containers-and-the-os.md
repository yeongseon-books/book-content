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

## 먼저 던지는 질문

- 컨테이너와 가상 머신은 격리 방식이 어떻게 다를까요?
- namespace는 "무엇이 보이는가"를, cgroup은 "얼마나 쓸 수 있는가"를 어떻게 나눌까요?
- overlayfs는 왜 컨테이너 이미지를 가볍게 느끼게 만들까요?

## 큰 그림

![Operating Systems 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/10/10-01-the-layers-that-create-container-isolati.ko.png)

*Operating Systems 101 10장 흐름 개요*

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

## 컨테이너 장애를 볼 때 먼저 나누는 기준

컨테이너 장애를 볼 때는 "애플리케이션이 죽었는가"만 묻지 말고, 어느 OS 계층에서 문제가 시작됐는지를 먼저 나누는 편이 빠릅니다.

| 증상 | 먼저 볼 것 | 연결되는 OS 계층 |
| --- | --- | --- |
| 컨테이너가 갑자기 종료됨 | `docker ps -a`, 종료 코드, OOM 여부 | cgroup 메모리 한도 |
| 안에서는 되는데 외부 통신이 안 됨 | 포트 매핑, 네트워크 namespace, 정책 | namespace / 네트워크 스택 |
| CPU는 남는데 응답이 들쭉날쭉함 | `docker stats`, throttling, CPU quota | cgroup CPU 스케줄링 |
| 파일이 사라지거나 느림 | overlayfs 레이어, bind mount, volume | 파일 시스템 / overlayfs |
| root인데도 어떤 명령이 실패 | capability, seccomp, rootless 여부 | 권한 모델 |

이 표를 기준으로 보면 "컨테이너가 이상하다"는 막연한 표현이 OS의 어떤 하위 계층을 먼저 점검해야 하는지로 바로 바뀝니다. 운영에서는 이 질문 순서가 문제 해결 시간을 크게 줄입니다.

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

## 연습 문제

1. 같은 베이스 이미지를 공유하는 컨테이너 두 개를 만들고, 실제 디스크 사용량이 어떻게 절약되는지 확인해 보세요.
2. 64MB 메모리 한도가 있는 컨테이너에서 안전한 캐시 상한을 계산하고, 어느 값에서 OOM-kill이 나는지 비교해 보세요.
3. 기본 seccomp 프로파일이 있을 때와 없을 때 `strace`로 어떤 시스템 콜이 차단되는지 비교해 보세요.

## 마무리와 다음 글

컨테이너는 새로운 운영체제가 아니라 리눅스 커널을 namespace, cgroup, overlayfs로 정밀하게 나누는 도구입니다. 이 시리즈에서 본 운영체제 개념이 컨테이너 위에서 다시 등장합니다. 컨테이너를 이해하면 운영체제가 더 선명해집니다.

이 시리즈는 여기서 마무리됩니다. 다음 학습으로는 같은 OS 개념이 네트워크와 분산 시스템으로 확장되는 방향(컴퓨터 네트워크 101, 분산 시스템 101) 또는 컨테이너 운영 자체를 깊게 다루는 방향(도커 101, 쿠버네티스 101)을 권장합니다.


## 운영체제 개념을 실무 판단으로 연결하기

### 스케줄링 정책을 숫자로 비교하는 방법
스케줄링은 이론 용어보다 대기시간과 응답시간으로 비교할 때 이해가 빠릅니다. 예를 들어 작업 집합이 `P1(도착 0, 실행 7)`, `P2(도착 2, 실행 4)`, `P3(도착 4, 실행 1)`일 때 FCFS와 SRTF의 결과를 비교하면 차이가 명확합니다.

- FCFS 평균 대기시간: `(0 + 5 + 7) / 3 = 4.0`
- SRTF 평균 대기시간: `(5 + 1 + 0) / 3 = 2.0`

같은 작업 집합이라도 정책에 따라 사용자 체감 지연이 크게 달라집니다. 서버가 인터랙티브 트래픽 중심인지, 배치 작업 중심인지에 따라 정책 선택 기준이 달라져야 합니다.

### 메모리 계층과 페이지 교체를 그림으로 정리하기
가상 메모리에서는 "어떤 페이지를 언제 내보내는가"가 성능을 좌우합니다. 아래 개념도는 자주 발생하는 페이지 폴트 경로를 보여줍니다.

```text
CPU 접근 -> 페이지 테이블 조회 -> miss
miss -> 페이지 폴트 트랩 -> 커널 핸들러
핸들러 -> victim 페이지 선택(LRU 근사)
victim dirty? yes -> 디스크 write-back
새 페이지 read -> 매핑 갱신 -> 재실행
```

핵심은 디스크 I/O가 개입되는 순간 지연이 급증한다는 점입니다. 따라서 워킹셋을 메모리에 유지하도록 데이터 구조와 접근 패턴을 설계해야 합니다. 순차 접근과 지역성 높은 캐시 친화 구조가 중요한 이유가 여기에 있습니다.

### 시스템 콜 경계에서 비용이 발생하는 이유
애플리케이션 코드는 사용자 모드에서 실행되지만, 파일 I/O와 네트워크 I/O는 커널 모드 전환이 필요합니다. 전환이 잦으면 오버헤드가 누적되므로 호출 단위를 조정하는 것이 좋습니다.

| syscall | 용도 | 성능 관점 포인트 |
| --- | --- | --- |
| `read` | 파일/소켓 입력 | 작은 크기로 반복 호출하면 전환 비용 증가 |
| `write` | 파일/소켓 출력 | 버퍼링 없이 자주 호출하면 처리량 저하 |
| `open` | 파일 디스크립터 획득 | 반복 open/close는 캐시 이점 상실 |
| `epoll_wait` | 이벤트 대기 | 다중 연결 처리에서 busy loop 방지 |
| `mmap` | 파일 메모리 매핑 | 랜덤 접근 workload에서 복사 비용 절감 가능 |

예를 들어 로그 수집기를 구현할 때 `write`를 1줄마다 호출하기보다 버퍼 단위로 모아 호출하면 syscall 횟수가 줄어 처리량이 개선됩니다. 운영체제 지식이 코드 수준 최적화로 직접 이어지는 지점입니다.

### 병행성 디버깅 체크리스트
경합 문제를 조사할 때는 증상만 보지 말고 스케줄링, 락 소유 시간, I/O 대기 시간을 함께 봐야 합니다.

1. `pidstat -w`로 컨텍스트 스위치 급증 여부 확인
2. `vmstat 1`로 run queue 길이와 I/O wait 확인
3. `strace -f -tt`로 블로킹 syscall 지점 식별
4. 락 획득/반납 시각을 애플리케이션 로그에 기록

이 네 단계를 함께 적용하면 "CPU가 느린 문제"인지 "락 경합 문제"인지 "디스크 대기 문제"인지를 분리할 수 있습니다. 운영체제 개념은 결국 문제를 정확히 분해하는 관측 프레임입니다.

## 시스템 관찰 지표와 커널 동작의 연결

### run queue와 CPU 사용률을 함께 읽기
CPU 사용률이 낮다고 항상 여유가 있는 것은 아닙니다. run queue 길이가 길고 I/O wait가 높으면 병목이 디스크나 네트워크일 수 있습니다.

```bash
vmstat 1
mpstat -P ALL 1
iostat -xz 1
```

세 도구를 같이 보면 CPU 바운드인지 I/O 바운드인지 분리할 수 있습니다. 운영체제 관점에서 중요한 것은 단일 지표가 아니라 지표 간 관계입니다.

### 페이지 폴트와 메모리 압박 해석
메모리 문제는 OOM 직전에야 드러나는 경우가 많습니다. 아래 지표를 주기적으로 보면 이상 징후를 조기에 잡을 수 있습니다.

- major page fault 증가: 디스크에서 페이지를 자주 끌어오는 상태
- swap in/out 급증: 워킹셋이 물리 메모리를 초과한 상태
- reclaim 스레드 활동 증가: 커널이 메모리 회수에 과도한 시간을 쓰는 상태

애플리케이션이 GC를 쓰는 런타임이라면, 힙 크기 조정과 객체 생존 시간 최적화가 커널 메모리 압박을 완화하는 직접 수단이 됩니다.

### 시스템 콜 추적으로 성능 병목 찾기
`strace`는 느리지만 원인 파악에는 매우 강력합니다. 호출 빈도와 지연 구간을 보면 어떤 API 사용이 비효율적인지 확인할 수 있습니다.

```bash
strace -f -c -p <pid>
```

요약표에서 `read`, `write`, `futex`, `epoll_wait` 비중이 높게 나오면 각각 I/O, 락 경합, 이벤트 대기 구조를 의심할 수 있습니다. 이후 애플리케이션 코드에서 버퍼 크기, 락 범위, 이벤트 루프 타임아웃을 조정하는 식으로 대응합니다.

### 스케줄링과 우선순위 튜닝 주의점
`nice`와 `ionice`는 빠른 응급처치지만, 남용하면 전체 시스템 공정성을 해칠 수 있습니다. 특정 작업의 우선순위를 올리면 다른 서비스의 tail latency가 악화될 수 있기 때문입니다.

운영 환경에서는 다음 원칙을 권장합니다. 첫째, 우선순위 조정은 임시 대응으로 제한합니다. 둘째, 조정 전후 지표를 캡처해 회귀를 확인합니다. 셋째, 근본 원인은 워크로드 분리, 큐 제어, 배치 시간 분산으로 해결합니다. 운영체제 기능은 문제를 숨기는 도구가 아니라 구조를 개선하기 위한 관측/제어 도구입니다.

## 처음 질문으로 돌아가기

- **컨테이너와 가상 머신은 격리 방식이 어떻게 다를까요?**
  - 본문의 기준은 컨테이너와 운영체제를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **namespace는 "무엇이 보이는가"를, cgroup은 "얼마나 쓸 수 있는가"를 어떻게 나눌까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **overlayfs는 왜 컨테이너 이미지를 가볍게 느끼게 만들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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
- **컨테이너와 운영체제 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Linux namespaces(7)](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Linux cgroups(7)](https://man7.org/linux/man-pages/man7/cgroups.7.html)
- [Open Container Initiative](https://opencontainers.org/)
- [Docker — Overview](https://docs.docker.com/get-started/overview/)
- [Rootless mode (Docker Docs)](https://docs.docker.com/engine/security/rootless/)
- [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec)

Tags: Computer Science, 운영체제, 컨테이너, namespace, cgroup, 격리
