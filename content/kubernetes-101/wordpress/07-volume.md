---
series: kubernetes-101
episode: 7
title: "바이브코딩을 위한 Kubernetes 기초 (7/10): Volume"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Kubernetes
  - Volume
  - PersistentVolume
  - DevOps
seo_description: AI가 생성한 Volume/PVC YAML을 제대로 이해하기 위해 알아야 할 파드 수명과 데이터 수명 분리, PVC와 StorageClass 구조를 바이브코딩 관점에서 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Kubernetes 기초 (7/10): Volume

이 글은 **바이브코딩을 위한 Kubernetes 기초** 시리즈의 일곱 번째 글입니다. AI와 함께 K8s YAML을 만들기 전에, Kubernetes가 어떻게 동작하는지 먼저 이해하는 것을 목표로 합니다.

---

AI에게 "PostgreSQL을 Kubernetes에 배포하는 YAML 만들어줘"라고 하면 PersistentVolumeClaim(PVC)이 포함된 YAML이 나옵니다. 그런데 PVC가 뭔지, 왜 필요한지 이해하지 못하면 데이터베이스를 배포했다가 파드가 재시작될 때 데이터가 모두 사라지는 경험을 할 수 있습니다.

바이브코딩 흐름에서 데이터베이스를 Kubernetes에 올릴 때 가장 많이 하는 실수가 있습니다. "파드가 다시 살아났는데 왜 데이터가 없죠?" 컨테이너 파일 시스템은 파드의 수명과 함께합니다. 파드가 재시작되면 컨테이너 안에 썼던 데이터는 사라집니다. PVC를 통해 외부 저장소를 연결해야만 파드가 바뀌어도 데이터가 유지됩니다.

> Volume의 핵심은 '디스크를 붙인다'가 아니라 '파드의 수명과 데이터의 수명을 분리한다'입니다. 컨테이너 파일시스템은 임시 작업 공간일 뿐이고, 영구 데이터는 PV/PVC 계층을 통해 파드 교체와 무관한 수명을 가져야 stateful 워크로드가 운영 가능해집니다.

## 이 글에서 답하는 질문들

- 파드가 재시작되면 컨테이너 파일시스템은 왜 사라질까요?
- `emptyDir`와 PVC는 어떤 순간에 갈라질까요?
- StorageClass는 단순 옵션이 아니라 무엇을 결정할까요?
- Volume을 잘못 설정하면 운영에서 어떤 데이터 손실이 생길까요?
- AI가 생성한 PVC YAML에서 가장 먼저 확인할 항목은 무엇일까요?

## 바이브코딩 관점: 컨테이너 파일 시스템은 임시다

AI가 데이터베이스 Deployment YAML을 만들 때 PVC를 포함하는 이유를 이해하려면 먼저 컨테이너 파일 시스템의 특성을 알아야 합니다.

컨테이너 안에 파일을 쓰면 그 파일은 파드가 살아있는 동안만 존재합니다. 파드가 재시작되면(`kubectl rollout restart`, OOM 킬, 노드 장애 등) 컨테이너는 처음 이미지 상태로 초기화됩니다. 데이터베이스 파일, 업로드된 파일, 작업 로그 등이 모두 사라집니다.

```
비유:
컨테이너 파일 시스템 = 호텔 방 (체크아웃하면 모두 리셋)
PVC = 외부 창고 (체크아웃해도 물건이 남아있음)
```

그래서 상태를 유지해야 하는 워크로드(데이터베이스, 파일 저장 등)는 반드시 PVC를 사용해야 합니다.

## Volume 구조: 한눈에 보기

**주요 개념**

- **emptyDir**: 파드 안에서 컨테이너들이 공유하는 임시 디렉토리. 파드가 사라지면 데이터도 사라짐
- **PersistentVolume(PV)**: 클러스터 관점의 실제 저장소 리소스(클라우드 디스크, NFS 등)
- **PersistentVolumeClaim(PVC)**: 워크로드가 원하는 저장소를 요청하는 객체. "5Gi짜리 디스크 줘"
- **StorageClass**: 디스크를 어떤 방식으로 만들지 정의. AWS EBS gp3, GCP SSD 등
- **AccessMode**: ReadWriteOnce(단일 노드 읽쓰기), ReadOnlyMany(다중 노드 읽기 전용), ReadWriteMany(다중 노드 읽쓰기)

## 도입 전과 후

**PVC 없이 컨테이너 파일 시스템에 DB 파일을 쓸 때**

파드 재시작 시 모든 데이터 손실. 개발 환경에서는 운 좋게 지나가도 운영에서는 반드시 문제가 됩니다.

**PVC를 사용하면**

파드가 교체되어도 데이터는 외부 디스크에 남아있습니다. 새 파드가 같은 PVC를 마운트해서 이전 데이터를 그대로 이어받습니다.

## 단계별 파드에 디스크 붙이기

### 1단계: PVC 작성

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: gp3  # 클라우드 환경마다 다름
```

PVC는 "이런 저장소가 필요합니다"라는 요청입니다. StorageClass를 통해 실제 디스크가 동적으로 생성됩니다.

### 2단계: 파드에서 PVC 사용

```yaml
spec:
  containers:
  - name: postgres
    image: postgres:16
    env:
    - name: POSTGRES_PASSWORD
      valueFrom:
        secretKeyRef:
          name: postgres-secret
          key: password
    volumeMounts:
    - name: data
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: postgres-data
```

컨테이너는 `/var/lib/postgresql/data` 경로를 로컬 폴더처럼 쓰지만, 실제로는 PVC를 통해 연결된 외부 디스크를 사용합니다.

### 3단계: 상태 확인

```bash
kubectl get pvc
kubectl describe pvc postgres-data
kubectl get pv
```

PVC가 `Pending` 상태면 StorageClass 설정이나 클러스터 스토리지 프로비저너를 확인해야 합니다. `Bound`면 정상적으로 연결된 상태입니다.

### 4단계: PVC 삭제 시 주의

```bash
# 이 명령 실행 전 reclaimPolicy를 반드시 확인하세요
kubectl get pv postgres-data-pv -o jsonpath='{.spec.persistentVolumeReclaimPolicy}'
# Delete: PVC 삭제 시 실제 디스크도 삭제
# Retain: PVC 삭제해도 실제 디스크 보존
```

PVC를 삭제하면 `reclaimPolicy`에 따라 실제 디스크까지 삭제될 수 있습니다. 운영 데이터를 다루는 PVC는 삭제 전 반드시 확인해야 합니다.

## 자주 하는 실수 5가지

| 실수 | 실제 문제 | 올바른 접근 |
|------|-----------|-------------|
| 상태 데이터를 `emptyDir`에 저장 | 파드 재시작 시 데이터 손실 | PVC 사용 |
| PVC만 있으면 백업도 끝났다고 오해 | 디스크 장애나 실수로 데이터 삭제 가능 | 별도 백업 정책 필요 |
| reclaimPolicy 확인 없이 PVC 삭제 | 실제 디스크와 데이터 모두 삭제 | 삭제 전 reclaimPolicy 확인 필수 |
| RWX(ReadWriteMany)가 어디서나 기본 지원된다고 가정 | StorageClass마다 지원 여부 다름 | 클라우드 환경 공식 문서 확인 |
| StorageClass를 기본값으로만 사용 | 성능/비용 최적화 기회 놓침 | 워크로드에 맞는 StorageClass 선택 |

## AI 팁: Volume/PVC YAML 요청과 검토

```
# 데이터베이스 스토리지 설정 요청 예시
"PostgreSQL을 Kubernetes에 배포하는 YAML을 만들어줘.
데이터는 10Gi PVC에 저장하고, AWS EKS 환경에서 gp3
StorageClass를 쓸 거야. 파드가 재시작되어도 데이터가
유지되도록 해줘."

# StorageClass 선택 도움 요청
"로컬 개발 환경(minikube), AWS EKS, GKE에서
각각 어떤 StorageClass를 써야 해? 차이점 설명해줘."

# 백업 방법 질문
"Kubernetes에서 PostgreSQL PVC 백업을 자동화하는
방법을 알려줘. Velero나 다른 도구를 사용하는 예제 포함해줘."
```

## 운영 체크리스트

- [ ] 상태 데이터가 PVC 또는 관리형 DB(RDS, Cloud SQL 등)에 있는가
- [ ] `emptyDir`를 영구 데이터 저장에 쓰지 않고 있는가
- [ ] 백업 정책을 준비했는가
- [ ] `reclaimPolicy`를 확인했는가(`Delete` vs `Retain`)
- [ ] `AccessMode`를 명시했는가

## 처음 질문으로 돌아가기

**파드가 재시작되면 컨테이너 파일시스템은 왜 사라질까요?**
컨테이너는 이미지를 기반으로 시작됩니다. 파드가 재시작되면 컨테이너도 이미지 초기 상태로 새로 시작됩니다. 실행 중에 컨테이너 안에 쓴 파일은 이미지의 일부가 아니므로 사라집니다.

**`emptyDir`와 PVC는 어떤 순간에 갈라질까요?**
`emptyDir`는 파드 안의 여러 컨테이너가 임시로 데이터를 공유할 때 씁니다. 파드가 사라지면 데이터도 사라집니다. PVC는 파드의 수명과 무관하게 데이터를 보존해야 할 때 씁니다.

**StorageClass는 단순 옵션이 아니라 무엇을 결정할까요?**
어떤 종류의 디스크를 어떻게 만들지 결정합니다. AWS EBS gp3, GCP SSD, Azure Premium SSD 등 성능과 비용이 다른 옵션들이 있습니다. StorageClass를 통해 PVC 요청이 실제 클라우드 디스크로 자동 변환됩니다.

## 정리

이번 글에서 다룬 핵심은 세 가지입니다. 첫째, 컨테이너 파일 시스템은 파드 수명과 함께하므로 영구 데이터는 PVC를 통해 외부 저장소에 보관해야 합니다. 둘째, PVC는 "저장소 요청"이고 StorageClass를 통해 실제 디스크로 연결됩니다. 셋째, PVC가 있어도 백업이 없으면 데이터 손실을 막을 수 없습니다.

다음 글에서는 트래픽 변화에 따라 파드 수를 자동으로 조절하는 HPA를 바이브코딩 관점에서 살펴보겠습니다.

## 참고 자료

- [Kubernetes 공식 문서: 퍼시스턴트 볼륨](https://kubernetes.io/ko/docs/concepts/storage/persistent-volumes/)
- [Kubernetes 공식 문서: StorageClass](https://kubernetes.io/ko/docs/concepts/storage/storage-classes/)
- [Velero - Kubernetes 백업 도구](https://velero.io/)
- [Kubernetes 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Kubernetes 기초 (1/10): Kubernetes란 무엇인가?
- 바이브코딩을 위한 Kubernetes 기초 (2/10): Pod
- 바이브코딩을 위한 Kubernetes 기초 (3/10): Deployment
- 바이브코딩을 위한 Kubernetes 기초 (4/10): Service
- 바이브코딩을 위한 Kubernetes 기초 (5/10): Ingress
- 바이브코딩을 위한 Kubernetes 기초 (6/10): ConfigMap과 Secret
- **바이브코딩을 위한 Kubernetes 기초 (7/10): Volume (현재 글)**
- 바이브코딩을 위한 Kubernetes 기초 (8/10): HPA
- 바이브코딩을 위한 Kubernetes 기초 (9/10): Helm
- 바이브코딩을 위한 Kubernetes 기초 (10/10): 운영 관점의 Kubernetes

<!-- toc:end -->

Tags: 바이브코딩, Kubernetes, Volume, PersistentVolume, DevOps
