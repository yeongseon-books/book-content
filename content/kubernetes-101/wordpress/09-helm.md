---
title: "바이브코딩을 위한 Kubernetes 기초 (9/10): Helm"
series: kubernetes-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Kubernetes
  - Helm
  - Chart
  - PackageManager
  - DevOps
---

# 바이브코딩을 위한 Kubernetes 기초 (9/10): Helm

이 글은 "바이브코딩을 위한 Kubernetes 기초" 시리즈의 9번째 글입니다.

---

Kubernetes를 실제로 쓰기 시작하면 YAML이 빠르게 늘어납니다. 바이브코딩에서 AI는 환경별 YAML을 각각 만들어 주지만, 개발/스테이징/운영 환경이 갈라지면 복사한 매니페스트가 금방 쌓이고 어떤 파일이 기준인지 흐려집니다.

Helm을 단순한 패키지 매니저가 아니라, 공통 템플릿과 환경별 값을 분리해 Kubernetes 배포를 반복 가능하게 만드는 배포 단위로 이해해야 합니다. 매니페스트 복사가 늘기 시작하면 이미 차트로 묶어야 할 시점입니다.

> **핵심 인사이트:** Helm은 '공통 템플릿과 환경별 값을 분리'해 Kubernetes 배포를 반복 가능하게 만드는 배포 단위입니다. values.yaml의 분리가 환경 차이를 정직하게 드러냅니다.

## 이 글에서 다룰 문제

- 환경마다 YAML을 복사하는 방식은 왜 드리프트를 만들까요?
- Chart와 `values.yaml`은 어떤 책임을 나눌까요?
- `install`, `upgrade`, `rollback`은 어떤 흐름으로 이어질까요?
- `--atomic`은 왜 더 안전한 옵션일까요?
- AI가 만든 Helm 차트에서 확인해야 할 것은 무엇인가요?

## Helm 핵심 패턴

```yaml
# values.yaml (환경별로 달라지는 값만)
replicaCount: 2
image:
  repository: myorg/app
  tag: "1.0"
service:
  type: ClusterIP
  port: 80
```

```bash
# 설치 및 업그레이드
helm install web ./chart -f values.yaml
helm upgrade web ./chart -f values-prod.yaml --atomic  # 실패 시 자동 롤백
helm rollback web 1  # 이전 revision으로 롤백

# 검증
helm template web ./chart -f values.yaml  # 적용 전 YAML 미리 보기
helm lint ./chart
helm history web
```

## 변경 전후 비교

**Before: 환경별 YAML 사본 관리**
```text
k8s/
├── dev/deployment.yaml
├── staging/deployment.yaml
└── prod/deployment.yaml
# 공통 구조 변경 시 3개 파일 모두 수정 필요
```

**After: 차트 + 환경별 values**
```text
charts/myapp/  # 공통 템플릿 (한 번만 관리)
values-dev.yaml
values-staging.yaml
values-prod.yaml
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| values와 차트 책임을 같은 파일에 혼합 | 환경별 차이가 불분명해짐 | 구조는 차트에, 값은 values에 |
| Secret 값을 values에 평문으로 | Git에 올라가면 노출 | 외부 비밀 관리 시스템 사용 |
| `latest` 태그로 배포 | 재현성 없음, 롤백 불가 | 버전 고정 |
| 롤백 절차 모르고 업그레이드만 | 장애 시 복구 어려움 | `helm rollback` 사전 숙지 |
| `--atomic` 미사용 | 실패 시 반쯤 적용된 상태로 남음 | 야간 배포 등에 `--atomic` 기본 사용 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"FastAPI 앱용 Helm 차트를 만들어줘.
values.yaml에 환경별 차이만 남기고,
Secret은 외부화해야 해.
upgrade는 --atomic으로 실패 시 자동 롤백이 되어야 해"

# 배포 전 검증:
helm template web ./chart -f values.yaml | kubectl apply --dry-run=client -f -
helm lint ./chart
```

## 운영 체크리스트

- [ ] 차트와 values 책임이 분리됐다
- [ ] 이미지 태그 버전이 고정됐다
- [ ] `--atomic` 사용 여부를 검토했다
- [ ] Secret 처리를 외부화했다 (Vault, Sealed Secrets 등)
- [ ] `helm history`로 rollback 가능한 상태를 확인했다

## 처음 질문으로 돌아가기

- **환경별 YAML 복사는 왜 드리프트를 만들까요?** 공통 구조 변경이 모든 사본에 반영되지 않으면 환경 간 불일치가 누적됩니다.
- **Chart와 values의 책임 차이는?** Chart는 공통 배포 계약, values는 환경별 입력값입니다.
- **`--atomic`이 더 안전한 이유는?** 업그레이드 실패 시 자동으로 이전 상태로 롤백하여 반쯤 적용된 상태를 방지합니다.

## 정리

Helm은 YAML 복사 문제를 해결하는 도구이지만, 차트와 values의 책임 분리를 제대로 하지 않으면 오히려 복잡성만 늘어납니다. 바이브코딩에서 AI가 만들어 준 Helm 차트에서 Secret 처리, 버전 고정, `--atomic` 설정을 반드시 확인하세요. 다음 글에서는 시리즈를 마무리하며 운영 관점의 Kubernetes를 정리합니다.

## 참고 자료

- [Helm Documentation](https://helm.sh/docs/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Kubernetes 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Kubernetes 기초 (1/10): Kubernetes란 무엇인가?
- 바이브코딩을 위한 Kubernetes 기초 (2/10): Pod
- 바이브코딩을 위한 Kubernetes 기초 (3/10): Deployment
- 바이브코딩을 위한 Kubernetes 기초 (4/10): Service
- 바이브코딩을 위한 Kubernetes 기초 (5/10): Ingress
- 바이브코딩을 위한 Kubernetes 기초 (6/10): ConfigMap과 Secret
- 바이브코딩을 위한 Kubernetes 기초 (7/10): Volume
- 바이브코딩을 위한 Kubernetes 기초 (8/10): HPA
- **바이브코딩을 위한 Kubernetes 기초 (9/10): Helm (현재 글)**
- 바이브코딩을 위한 Kubernetes 기초 (10/10): 운영 관점의 Kubernetes
<!-- toc:end -->

Tags: 바이브코딩, Kubernetes, Helm, Chart, PackageManager, DevOps
