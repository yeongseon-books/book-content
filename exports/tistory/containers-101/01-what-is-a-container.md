
# Container란 무엇인가?

> Containers 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *컨테이너* 는 *왜* *VM* 처럼 보이지만 *VM이 아닌* 걸까요?

> *컨테이너 는 *호스트 OS 커널* 을 *공유* 하면서 *프로세스* 를 *격리* 한 *경량 패키지* 입니다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *컨테이너* 의 *정의*
- *호스트 OS* 와 *공유* 하는 것
- *VM* 과의 *결정적 차이*
- *Docker* 의 *기본 흐름*
- 흔한 함정 5가지

## 왜 중요한가

*컨테이너* 는 *2013년 이후* *배포* 의 *기본 단위* 입니다. *모르면* 현대 *DevOps* 에 *진입할 수 없습니다*.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Host["host os kernel"] --> C1["container 1"]
    Host --> C2["container 2"]
    Host --> C3["container 3"]
    C1 --> App1["app process"]
```

## 핵심 용어 정리

- **Container**: *격리된 프로세스* 묶음.
- **Image**: 컨테이너의 *정적인 템플릿*.
- **Namespace**: *프로세스/네트워크/파일* 공간 격리.
- **cgroups**: *CPU/메모리* 자원 *제한*.
- **Runtime**: 컨테이너를 *실행* 하는 엔진.

## Before/After

**Before**: *서버* 에 *직접 설치* → *환경 차이* 로 *깨짐*.

**After**: *이미지* 한 개 → *어디서나* *동일하게* 실행.

## 실습: 첫 컨테이너 실행

### 1단계 — 버전 확인

```python
import subprocess

def docker_version():
    res = subprocess.run(["docker", "--version"], capture_output=True, text=True)
    return res.stdout.strip()
```

### 2단계 — 이미지 pull

```python
def pull(image):
    subprocess.run(["docker", "pull", image], check=True)
```

### 3단계 — 컨테이너 실행

```python
def run_nginx():
    subprocess.run(
        ["docker", "run", "-d", "-p", "8080:80", "--name", "web", "nginx:latest"],
        check=True,
    )
```

### 4단계 — 상태 확인

```python
def ps():
    res = subprocess.run(["docker", "ps"], capture_output=True, text=True)
    return res.stdout
```

### 5단계 — 정리

```python
def cleanup(name):
    subprocess.run(["docker", "rm", "-f", name], check=True)
```

## 이 코드에서 주목할 점

- *-d* 는 *백그라운드* 실행.
- *-p 8080:80* 은 *호스트:컨테이너* 포트 매핑.
- *--name* 으로 *식별자* 부여.

## 자주 하는 실수 5가지

1. ***포트 매핑* 누락 → *접근 불가*.**
2. ***컨테이너* 와 *이미지* 혼동.**
3. ***cleanup* 안 해서 *디스크 가득*.**
4. ***root* 로 컨테이너 실행.**
5. ***로컬에선 되는데* 라는 신화 유지.**

## 실무에서는 이렇게 쓰입니다

*개발자* 는 *Docker Desktop* 에서 *동일 이미지* 빌드, *CI* 가 *registry* 푸시, *프로덕션* 은 *Kubernetes* 에서 동일 이미지 실행.

## 시니어 엔지니어는 이렇게 생각합니다

- *컨테이너* 는 *프로세스* 다, *VM이 아니다*.
- *이미지* 는 *불변 (immutable)*.
- *상태* 는 *볼륨* 으로 *분리*.
- *root 회피* 가 *기본*.
- *재현 가능성* 이 *핵심 가치*.

## 체크리스트

- [ ] *Docker* 설치 확인.
- [ ] *이미지/컨테이너* 차이 설명 가능.
- [ ] *port mapping* 이해.
- [ ] *cleanup 명령* 숙지.

## 연습 문제

1. *컨테이너* 와 *VM* 의 *결정적 차이* 한 줄로.
2. *docker run* 의 *-d* 옵션이 *없으면* 어떻게 되는지 설명.
3. *이미지* 와 *컨테이너* 의 *관계* 를 *클래스/인스턴스* 비유로 설명.

## 정리 및 다음 단계

이미지가 *템플릿* 이라면 *내부 구조* 를 봐야 합니다. 다음 글은 *Image와 Layer*.

- **Container란 무엇인가? (현재 글)**
- Image와 Layer (예정)
- Runtime (예정)
- Dockerfile (예정)
- Volume (예정)
- Network (예정)
- Registry (예정)
- Container Security (예정)
- Container와 VM 차이 (예정)
- 실전 컨테이너 앱 만들기 (예정)
## 참고 자료

- [Docker 공식 문서](https://docs.docker.com/)
- [OCI Image Spec](https://github.com/opencontainers/image-spec)
- [Linux namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [cgroups v2](https://www.kernel.org/doc/Documentation/admin-guide/cgroup-v2.rst)

Tags: Containers, Docker, Linux, DevOps, Architecture

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
