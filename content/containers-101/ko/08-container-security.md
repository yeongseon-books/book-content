---
series: containers-101
episode: 8
title: "Containers 101 (8/10): Container Security"
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
- Security
- seccomp
- Cosign
- DevOps
seo_description: 비root, capability, seccomp, 시크릿 처리까지 컨테이너 보안 기초를 설명합니다
last_reviewed: '2026-05-15'
---

# Containers 101 (8/10): Container Security

컨테이너는 격리되어 있으니 기본적으로 안전할 것처럼 느껴집니다. 하지만 기본값 그대로 실행하면 root 사용자, 과한 capability, 느슨한 시크릿 처리, 검증 없는 이미지가 그대로 운영에 들어가기도 합니다.

이 글은 Containers 101 시리즈의 여덟 번째 글입니다.

여기서는 non-root, capability 축소, seccomp, 읽기 전용 파일시스템, 이미지 스캔과 서명이 어떻게 하나의 보안 기본선으로 이어지는지 정리합니다.

## 먼저 던지는 질문

- 격리된 컨테이너가 왜 자동으로 안전한 것은 아닐까요?
- non-root 실행은 어떤 보안 의미를 가질까요?
- capabilities와 seccomp는 무엇을 줄여 줄까요?

## 큰 그림

![Containers 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/08/08-01-concept-at-a-glance.ko.png)

*Containers 101 8장 흐름 개요*

Container Security는 이미지 빌드 시점, 런타임 정책, 호스트 커널 관리까지 여러 계층을 아우릅니다. 한 계층만 신경 쓴다고 안전하지 않습니다.

> Container Security의 핵심은 root로 실행하지 않는 것, 최소 권한 원칙, 그리고 격리는 완전하지 않다는 가정 아래 심층 방어(defense-in-depth)입니다.

## 왜 중요한가

기본 컨테이너는 생각보다 많은 권한을 가질 수 있습니다. 별도 조치를 하지 않으면 root로 실행되고, 불필요한 capability를 가진 채 시작하며, 시크릿도 환경 변수에 그대로 노출되기 쉽습니다.

그래서 컨테이너 보안은 “컨테이너를 썼으니 안전하다”가 아니라 “기본값을 얼마나 줄였는가”의 문제입니다. 보안 사고는 대개 복잡한 공격보다 느슨한 기본값에서 시작합니다.

## 한눈에 보는 개념

이미지는 먼저 검사하고, 가능하면 서명하고, 실행 시에는 비root·최소 capability·적절한 시크릿 마운트로 공격 표면을 줄입니다.

## 핵심 용어

- **non-root**: UID 1000 같은 일반 사용자로 실행하는 방식입니다.
- **capability**: root 권한을 잘게 나눈 조각입니다.
- **seccomp**: 허용할 시스템 콜을 제한하는 정책입니다.
- **image scanning**: 알려진 CVE를 기준으로 이미지를 검사하는 절차입니다.
- **secret**: 환경 변수보다 전용 시스템이나 볼륨 마운트로 다뤄야 하는 민감 값입니다.

특히 capability와 seccomp를 함께 이해하면 “root가 아니면 끝”이 아니라 실행 권한 표면을 단계적으로 줄여 가는 구조가 보입니다.

## Before / After

**Before**: root와 과도한 권한으로 컨테이너를 실행합니다.

**After**: non-root, 최소 capability, seccomp로 공격 표면을 줄입니다.

보안은 하나의 기능이 아니라 기본값을 덜 위험하게 바꾸는 연속된 선택입니다.

## 실습: 컨테이너를 더 안전하게 실행하기

### Step 1 — Scan the image

```python
import subprocess

def scan(image):
    res = subprocess.run(
        ["trivy", "image", "--severity", "HIGH,CRITICAL", image],
        capture_output=True, text=True,
    )
    return res.returncode == 0
```

실행 전 이미지 스캔을 먼저 합니다. 취약점은 런타임 정책만으로 해결되지 않기 때문에 공급망 입구부터 확인해야 합니다.

### Step 2 — Force non-root

```python
def run_nonroot(image):
    subprocess.run([
        "docker", "run", "--rm", "-d",
        "--user", "1000:1000", image,
    ], check=True)
```

비root 실행은 가장 기본적인 권한 축소입니다. root가 아니면 불가능한 공격 범위를 자연스럽게 줄일 수 있습니다.

### Step 3 — Drop capabilities

```python
def run_min_caps(image):
    subprocess.run([
        "docker", "run", "--rm", "-d",
        "--cap-drop=ALL", "--cap-add=NET_BIND_SERVICE", image,
    ], check=True)
```

필요한 capability만 다시 추가합니다. “모두 허용 후 일부 차단”보다 “모두 제거 후 필요한 것만 허용”이 더 안전한 기본값입니다.

### Step 4 — Read-only filesystem

```python
def run_readonly(image):
    subprocess.run([
        "docker", "run", "--rm", "-d",
        "--read-only", "--tmpfs", "/tmp", image,
    ], check=True)
```

읽기 전용 루트 파일시스템은 런타임에서 쓰기 가능 면적을 줄여 줍니다. 애플리케이션이 실제로 어디에 써야 하는지 더 명확하게 드러나는 장점도 있습니다.

### Step 5 — Mount a secret

```python
def run_with_secret(image, secret_path):
    subprocess.run([
        "docker", "run", "--rm", "-d",
        "-v", f"{secret_path}:/run/secrets/db_pw:ro", image,
    ], check=True)
```

시크릿은 환경 변수보다 읽기 전용 마운트나 전용 시크릿 시스템을 통해 다루는 편이 안전합니다.

## 이 코드에서 먼저 봐야 할 점

- `--user`는 root 실행을 피하게 합니다.
- `--cap-drop=ALL` 이후 필요한 capability만 다시 추가합니다.
- 시크릿은 볼륨처럼 마운트해서 전달합니다.

이 세 가지는 복잡한 보안 제품이 없어도 바로 적용할 수 있는 기본값입니다. 초반에 이 기준만 잡아도 보안 수준이 눈에 띄게 좋아집니다.

## 빠른 검증과 장애 신호

```bash
trivy image --severity HIGH,CRITICAL python:3.12-slim
docker run --rm --user 1000:1000 python:3.12-slim id
docker run --rm --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx:1.27-alpine nginx -t
docker run --rm --read-only --tmpfs /tmp python:3.12-slim python -c "print("ok")"
```

**Expected output:**
- `id` 출력에서 root가 아닌 UID/GID가 보입니다.
- 필요한 capability만 추가해도 서비스가 동작하는지 확인할 수 있습니다.
- 읽기 전용 루트 파일시스템에서도 예외 경로만 쓰면 기동 가능합니다.

**먼저 확인할 것:**
- non-root에서 실패하면 쓰기 경로와 파일 소유권을 먼저 봅니다.
- `--read-only` 실패 시 앱이 어디에 임시 파일을 쓰는지 추적합니다.
- 스캔 결과가 많으면 베이스 이미지와 패키지 구성을 먼저 정리합니다.

## 자주 하는 실수 5가지

1. **root로 실행하면서 내부를 믿습니다.**
2. **시크릿을 환경 변수로 그대로 노출합니다.**
3. **스캔 없이 운영에 배포합니다.**
4. **privileged 컨테이너를 과하게 사용합니다.**
5. **서명 검증을 생략해 이미지 바꿔치기 위험을 엽니다.**

보안 사고는 대개 고급 기법보다 기본값 방치에서 시작합니다. 그래서 가장 먼저 점검해야 할 것도 거창한 도구가 아니라 기본 실행 옵션입니다.

## 운영에서는 이렇게 나타납니다

Kubernetes에서는 Pod Security, admission controller 같은 정책을 통해 non-root, privileged 금지, signed image only 같은 규칙을 런타임에 강제하기도 합니다. 즉, 로컬에서 배운 보안 기본값이 오케스트레이션 환경에서는 정책으로 확장됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 기본값은 대체로 위험하다고 전제합니다.
- capability는 명시적으로 필요한 것만 더합니다.
- 시크릿은 전용 시스템에 둡니다.
- 스캔은 CI 게이트의 일부라고 봅니다.
- 서명은 공급망 신뢰의 시작이라고 생각합니다.

시니어 엔지니어는 보안을 “특별한 모드”로 보지 않습니다. 평소 기본값이 곧 보안 수준을 만든다고 보기 때문에 Dockerfile, 런타임 옵션, CI 정책을 함께 설계합니다.

## 체크리스트

- [ ] non-root 사용자로 실행합니다.
- [ ] `cap-drop=ALL` 후 최소 capability만 추가합니다.
- [ ] 읽기 전용 파일시스템을 검토했습니다.
- [ ] 시크릿은 볼륨 또는 전용 시크릿 매니저로 전달합니다.

## 연습 문제

1. capability가 왜 존재하는지 한 줄로 설명해 보세요.
2. seccomp의 역할을 한 줄로 설명해 보세요.
3. 서명된 이미지가 막아 주는 공격 하나를 적어 보세요.

## 정리와 다음 글

컨테이너 보안은 격리를 믿는 태도가 아니라 권한을 줄이고 이미지를 검증하고 런타임 정책을 명시하는 태도에서 시작합니다. non-root, capability 축소, 시크릿 분리, 이미지 스캔과 서명을 함께 가져가야 기본이 갖춰집니다.

다음 글에서는 컨테이너와 VM의 차이를 비교하며, 어떤 격리 모델을 언제 선택해야 하는지 살펴보겠습니다.


## 심화: 이미지 스캔 도구 비교와 런타임 최소권한 설계

컨테이너 보안은 특정 도구 하나를 도입한다고 끝나지 않습니다. 이미지 단계에서 취약점을 줄이고, 런타임 단계에서 권한을 줄이고, 배포 단계에서 무결성을 검증해야 합니다. 이 세 단계가 이어져야 실제 위험이 줄어듭니다.

## 스캔 도구 비교

| 도구 | 강점 | 주의점 | 대표 사용 위치 |
| --- | --- | --- | --- |
| Trivy | 사용이 간단, 빠른 스캔 | 정책 커스터마이징은 추가 작업 필요 | 로컬/CI |
| Grype | SBOM 기반 분석 강점 | 초기 학습 필요 | CI, 보안팀 파이프라인 |
| Docker Scout | Docker 생태계 통합 | 도구 종속성 고려 필요 | Docker 중심 팀 |
| Snyk Container | 정책/리포팅 강점 | 유료 기능 고려 | 기업 보안 운영 |

도구 선택보다 중요한 것은 "어느 심각도에서 빌드를 실패시킬 것인가"입니다. 보통 HIGH/CRITICAL 기준 차단부터 시작합니다.

## Distroless vs Alpine 비교

| 항목 | Distroless | Alpine |
| --- | --- | --- |
| 이미지 크기 | 매우 작음 | 작음 |
| 셸/패키지 도구 | 없음 | 있음 |
| 운영 디버깅 | 어렵지만 공격 표면 작음 | 상대적으로 쉬움 |
| 권장 사용처 | 안정화된 프로덕션 서비스 | 개발/테스트/일반 운영 |

Distroless는 공격 표면을 줄이는 데 효과적이지만, 셸이 없어 긴급 디버깅이 어렵습니다. 따라서 팀의 운영 성숙도에 맞춰 선택해야 합니다.

## 런타임 최소권한 실행 예시

```bash
docker run --rm -d   --user 1000:1000   --read-only   --tmpfs /tmp   --cap-drop=ALL   --cap-add=NET_BIND_SERVICE   myorg/api:1.0.0
```

이 명령은 보안 기본값을 명확히 보여 줍니다.

- root 금지
- 쓰기 가능한 루트 파일시스템 금지
- capability 최소화
- 임시 쓰기 경로만 제한 허용

## CI 보안 게이트 예시

```bash
trivy image --severity HIGH,CRITICAL --exit-code 1 myorg/api:1.0.0
cosign verify myorg/api:1.0.0
```

이 두 단계만으로도 "취약점 많은 이미지"와 "검증되지 않은 이미지"를 배포 전 차단할 수 있습니다.

## 운영 체크리스트

- non-root 실행 기본값
- capability 최소화 정책
- read-only root filesystem 검토
- 시크릿은 파일 마운트 또는 전용 매니저 사용
- 스캔/서명 검증을 CI 필수 단계로 설정

보안은 복잡한 도구보다 기본 실행 옵션의 일관성에서 시작합니다. 이 기본값이 팀 전반에 적용되어야 사고 빈도를 줄일 수 있습니다.


## 추가 실무 노트: 정책 기반 차단과 예외 관리

보안 정책을 CI에 넣을 때는 "차단 기준"과 "예외 승인 절차"를 함께 정의해야 합니다. 차단만 있고 예외 절차가 없으면 우회가 늘고, 예외만 많으면 정책이 무력화됩니다.

권장 절차:

1. HIGH/CRITICAL 기본 차단
2. 예외는 티켓 번호와 만료일 필수
3. 만료 시 자동 재검토

이 방식은 개발 속도와 보안 기준을 동시에 지키는 현실적인 균형점입니다.


## 추가 정리: 운영 적용 전 최종 점검 질문

아래 질문은 도구 지식이 아니라 운영 준비도를 확인하기 위한 질문입니다. 각 질문에 문서와 명령으로 답할 수 있어야 실제 팀 운영에서 반복 가능한 품질을 만들 수 있습니다.

1. 이 구성은 새 팀원이 같은 절차로 재현할 수 있는가?
2. 실패했을 때 어디서 원인을 확인해야 하는지 런북이 있는가?
3. 보안 기본값(root 금지, 최소 권한, 시크릿 분리)이 강제되는가?
4. 버전과 아티팩트 동일성(digest, lock file)이 보장되는가?
5. 데이터/네트워크/권한 경계가 문서로 정의되어 있는가?

다음은 공통 점검 명령 예시입니다.

```bash
# 아티팩트 동일성
docker inspect --format '{{index .RepoDigests 0}}' <image>

# 실행 상태
docker ps --format 'table {{.Names}}	{{.Status}}	{{.Ports}}'

# 로그 관측
docker logs --tail 100 <container>

# 네트워크/볼륨 구조
docker network ls
docker volume ls
```

이 명령 자체가 중요한 것이 아니라, 팀이 같은 순서로 문제를 좁혀 가는 절차를 공유한다는 점이 중요합니다. 컨테이너 운영의 성숙도는 개인의 숙련도보다 팀의 표준화 수준에서 결정됩니다. 따라서 시리즈 학습의 최종 목표는 기능 이해가 아니라 운영 계약의 명문화입니다.

## 처음 질문으로 돌아가기
- **컨테이너가 root로 실행되면 뭐가 위험할까요?**
  - 컨테이너 격리가 뚫리면 host root가 됩니다. 컨테이너는 root 권한이 필요 없도록 설계하고, 꼭 필요하면 non-root 사용자로 권한을 제한합니다.
- **이미지 스캔과 런타임 정책은 어떻게 다를까요?**
  - 이미지 스캔은 알려진 취약점을 찾아내고, 런타임 정책은 실행 권한(syscall, 파일 접근 등)을 제한합니다. 둘 다 필요합니다.
- **SELinux, AppArmor, seccomp는 왜 따로 필요할까요?**
  - 컨테이너 격리 자체의 한계를 보완하기 위함입니다. 같은 커널을 쓰기 때문에 격리가 뚫릴 가능성이 있고, 이를 추가 정책으로 제어합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Containers 101 (1/10): Container란 무엇인가?](./01-what-is-a-container.md)
- [Containers 101 (2/10): Image와 Layer](./02-image-and-layer.md)
- [Containers 101 (3/10): Runtime](./03-runtime.md)
- [Containers 101 (4/10): Dockerfile](./04-dockerfile.md)
- [Containers 101 (5/10): Volume](./05-volume.md)
- [Containers 101 (6/10): Network](./06-network.md)
- [Containers 101 (7/10): Registry](./07-registry.md)
- **Container Security (현재 글)**
- Containers vs VMs (예정)
- 실전 컨테이너 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Docker security](https://docs.docker.com/engine/security/)
- [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Trivy](https://aquasecurity.github.io/trivy/)
- [seccomp profiles](https://docs.docker.com/engine/security/seccomp/)

Tags: Containers, Docker, Kubernetes, DevOps
