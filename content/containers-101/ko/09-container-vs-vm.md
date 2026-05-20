---
series: containers-101
episode: 9
title: "Containers 101 (9/10): Containers vs VMs"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
- Containers
- VM
- Linux
- Hypervisor
- DevOps
seo_description: 호스트 커널 공유와 하이퍼바이저 격리의 차이점을 통해 컨테이너와 가상 머신의 속도, 밀도, 보안 trade-off를
  분석합니다.
last_reviewed: '2026-05-15'
---

# Containers 101 (9/10): Containers vs VMs

컨테이너와 VM 비교는 속도만의 문제가 아닙니다. 어떤 격리 경계가 필요한지, 멀티테넌트 요구가 얼마나 강한지, 부팅 시간과 자원 밀도가 어디까지 중요한지에 따라 답이 달라집니다.

이 글은 Containers 101 시리즈의 아홉 번째 글입니다.

여기서는 호스트 커널 공유와 하이퍼바이저 기반 격리를 대비시키고, 어떤 워크로드에서 컨테이너·VM·microVM을 각각 먼저 검토해야 하는지 살펴봅니다.

## 먼저 던지는 질문

- 컨테이너와 VM은 어떤 격리 모델 차이를 가질까요?
- 커널 공유와 하이퍼바이저 차이는 왜 중요한가요?
- 시작 속도와 자원 사용량은 얼마나 다르게 느껴질까요?

## 큰 그림

![Containers 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/09/09-01-concept-at-a-glance.ko.png)

*Containers 101 9장 흐름 개요*

이 그림에서는 Containers vs VMs를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Containers vs VMs의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

격리 수준을 워크로드에 맞게 고르는 일은 비용과 보안을 동시에 좌우합니다. 모든 것을 컨테이너로 밀어 넣어도 문제이고, 모든 것을 VM으로 감싸도 비효율이 커집니다.

특히 멀티테넌트 환경이나 강한 보안 경계가 필요한 워크로드에서는 VM이 더 적합할 수 있고, 빠른 배포와 높은 밀도가 중요한 서비스형 워크로드에서는 컨테이너가 훨씬 유리합니다. 중요한 것은 둘 중 하나를 신념처럼 고르는 것이 아니라 요구사항에 맞춰 격리 단위를 고르는 것입니다.

## 한눈에 보는 개념

VM은 하이퍼바이저 위에서 자체 커널을 부팅하고, 컨테이너는 호스트 커널 위에서 프로세스를 격리합니다. 출발 구조 자체가 다르기 때문에 격리, 속도, 밀도도 달라집니다.

## 핵심 용어

- **hypervisor**: VM을 부팅하고 관리하는 가상화 계층입니다.
- **guest kernel**: VM 내부에서 독립적으로 실행되는 커널입니다.
- **container**: 호스트 커널을 공유하는 프로세스 격리 단위입니다.
- **microVM**: Firecracker 같은 경량 VM입니다.
- **gVisor / Kata**: 컨테이너에 추가 격리를 더하는 접근입니다.

이 용어를 함께 이해하면 “컨테이너가 가볍다”는 말이 단순한 속도 자랑이 아니라 아키텍처 차이에서 나온 결과라는 점이 보입니다.

## Before / After

**Before**: 모든 워크로드를 VM으로만 돌려 느리고 비쌉니다.

**After**: 일반 서비스는 컨테이너에, 멀티테넌트 경계는 VM 또는 microVM에 둡니다.

즉, 현대 운영에서는 둘 중 하나를 버리는 것이 아니라 적절히 조합하는 편이 더 자연스럽습니다.

## 실습: 같은 앱을 두 방식으로 비교하기

### Step 1 — Run as a container

```python
import subprocess, time

def run_container(image):
    t = time.time()
    subprocess.run(["docker", "run", "--rm", "-d", image], check=True)
    return time.time() - t
```

컨테이너는 보통 밀리초에서 수초 안에 시작합니다. 빠른 부팅은 오토스케일과 배포 전략에 직접 영향을 줍니다.

### Step 2 — Run as a VM (concept)

```python
def run_vm(image_path):
    t = time.time()
    subprocess.run([
        "qemu-system-x86_64", "-m", "1024", "-hda", image_path,
        "-display", "none", "-daemonize",
    ], check=True)
    return time.time() - t
```

VM은 커널 부팅을 포함하므로 시작 비용이 더 큽니다. 대신 그만큼 강한 격리 경계를 제공합니다.

### Step 3 — Compare memory

```python
def mem_usage(pid):
    res = subprocess.run(
        ["ps", "-o", "rss=", "-p", str(pid)],
        capture_output=True, text=True, check=True,
    )
    return int(res.stdout.strip())
```

메모리 사용량을 비교하면 프로세스 격리와 OS 격리의 비용 차이를 더 현실적으로 볼 수 있습니다.

### Step 4 — Compare startup time

```python
def compare(image, vm_image):
    return {
        "container_sec": run_container(image),
        "vm_sec": run_vm(vm_image),
    }
```

비교는 감상이 아니라 측정으로 해야 합니다. 그래야 워크로드에 맞는 격리 단위를 더 합리적으로 선택할 수 있습니다.

### Step 5 — Report

```python
def report(stats):
    print(f"container={stats['container_sec']:.2f}s vm={stats['vm_sec']:.2f}s")
```

최종 결과를 수치로 남깁니다. 컨테이너와 VM의 차이는 개념 설명보다 측정 결과에서 더 잘 체감됩니다.

## 이 코드에서 먼저 봐야 할 점

- 컨테이너는 보통 밀리초에서 수초 안에 시작합니다.
- VM은 수초에서 수분이 걸릴 수 있습니다.
- 비교는 자동화해서 재현 가능하게 해야 합니다.

이 세 가지를 함께 보면 “가볍다”와 “강하게 격리된다”가 어떤 운영 비용 차이로 이어지는지 훨씬 선명해집니다.

## 빠른 검증과 장애 신호

```bash
/usr/bin/time -p docker run --rm nginx:1.27-alpine true
/usr/bin/time -p qemu-system-x86_64 -m 1024 -display none -daemonize -hda vm.img
```

**Expected output:**
- 컨테이너는 보통 밀리초~수초, VM은 수초 이상으로 차이가 드러납니다.
- 같은 앱이어도 격리 단위에 따라 부팅 비용과 기본 자원 사용량이 달라집니다.

**먼저 확인할 것:**
- 같은 호스트와 조건에서 반복 측정해야 비교가 의미 있습니다.
- QEMU가 실패하면 가상화 지원과 이미지 준비 상태를 먼저 확인합니다.
- 강한 멀티테넌트 환경이면 성능보다 경계 강도를 먼저 봅니다.

## 자주 하는 실수 5가지

1. **모든 워크로드를 컨테이너에 넣어 멀티테넌트 격리를 약하게 만듭니다.**
2. **모든 워크로드를 VM으로만 운영해 비용이 과도하게 커집니다.**
3. **컨테이너를 곧 보안이라고 생각합니다.**
4. **Mac/Windows의 Docker가 내부적으로 VM을 쓴다는 사실을 잊습니다.**
5. **커널 의존적인 워크로드를 무리하게 컨테이너에 욱여넣습니다.**

이 실수들은 모두 격리 모델을 기능 목록으로만 볼 때 나옵니다. 실제로는 운영 목적과 보안 요구 수준을 함께 고려해야 합니다.

## 운영에서는 이렇게 나타납니다

AWS Fargate나 Lambda는 Firecracker microVM 위에 컨테이너 스타일 실행을 얹어, 컨테이너의 속도와 VM 수준 격리를 함께 가져가려는 방향을 보여 줍니다. 즉, 현대 인프라는 둘을 섞는 하이브리드 접근을 기본값으로 가져가고 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 격리 수준은 비즈니스 요구를 따라야 한다고 봅니다.
- 컨테이너는 VM 안에서 실행될 수도 있다고 생각합니다.
- 부팅 시간은 아키텍처 선택 요소라고 봅니다.
- 멀티테넌트 경계는 VM 수준이 더 안전하다고 판단할 수 있습니다.
- 하이브리드가 현대적 기본값이라고 봅니다.

시니어 엔지니어는 “무엇이 더 최신인가”보다 “어떤 격리 경계가 이 서비스에 맞는가”를 먼저 묻습니다. 그 질문이 맞아야 비용과 보안을 동시에 관리할 수 있기 때문입니다.

## 체크리스트

- [ ] 서비스 격리에는 컨테이너를 우선 검토합니다.
- [ ] 테넌트 격리에는 VM 또는 microVM을 검토합니다.
- [ ] 보안 등급을 문서화했습니다.
- [ ] 시작 시간 SLA를 측정합니다.

## 연습 문제

1. 커널 공유가 왜 컨테이너를 가볍게 만드는지 한 줄로 설명해 보세요.
2. VM이 컨테이너보다 유리한 사례 하나를 적어 보세요.
3. Firecracker의 역할을 한 줄로 설명해 보세요.

## 정리와 다음 글

컨테이너와 VM은 서로를 대체하는 절대적인 승자와 패자가 아닙니다. 컨테이너는 빠르고 가볍고, VM은 더 강한 격리를 제공합니다. 그래서 현대 운영에서는 둘을 적절히 섞는 하이브리드 전략이 자연스럽습니다.

다음 글에서는 지금까지 배운 개념을 하나의 실제 애플리케이션으로 묶어, 실전 컨테이너 앱 만들기를 진행하겠습니다.

## 처음 질문으로 돌아가기

- **컨테이너와 VM은 어떤 격리 모델 차이를 가질까요?**
  - 본문의 기준은 Containers vs VMs를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **커널 공유와 하이퍼바이저 차이는 왜 중요한가요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **시작 속도와 자원 사용량은 얼마나 다르게 느껴질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Containers 101 (1/10): Container란 무엇인가?](./01-what-is-a-container.md)
- [Containers 101 (2/10): Image와 Layer](./02-image-and-layer.md)
- [Containers 101 (3/10): Runtime](./03-runtime.md)
- [Containers 101 (4/10): Dockerfile](./04-dockerfile.md)
- [Containers 101 (5/10): Volume](./05-volume.md)
- [Containers 101 (6/10): Network](./06-network.md)
- [Containers 101 (7/10): Registry](./07-registry.md)
- [Containers 101 (8/10): Container Security](./08-container-security.md)
- **Containers vs VMs (현재 글)**
- 실전 컨테이너 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [What is a container? (Docker)](https://www.docker.com/resources/what-container/)
- [Firecracker](https://firecracker-microvm.github.io/)
- [Kata Containers](https://katacontainers.io/)
- [gVisor](https://gvisor.dev/)

Tags: Containers, Docker, Kubernetes, DevOps
