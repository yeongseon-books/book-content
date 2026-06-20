---
title: "바이브코딩을 위한 Azure AKS 심화 (2/6): kubelet과 containerd"
series: azure-aks-deep-dive
episode: 2
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAKS심화
- kubelet
- containerd
- AI코딩
seo_description: "바이브코딩을 위한 Azure AKS 심화 2편: kubelet과 containerd. 노드에서 컨테이너가 뜨기까지 kubelet-CRI-containerd-runc 실행 체인을 이해합니다."
---

# 바이브코딩을 위한 Azure AKS 심화 (2/6): kubelet과 containerd

이 글은 바이브코딩을 위한 Azure AKS 심화 시리즈의 2번째 글입니다.

`kubectl apply` 뒤에 Pod가 Running이 되면 실행 전체가 한 번에 끝난 일처럼 보입니다. 하지만 scheduler가 노드를 고른 뒤에도 node-local 경로에서는 kubelet, CRI, containerd, runc가 각자 다른 계층의 책임을 순서대로 이어받습니다. 이 실행 사슬을 분해해서 보지 않으면 이미지 pull 실패, sandbox 준비 실패, 실제 프로세스 기동 실패가 모두 비슷한 "컨테이너가 안 뜬다"는 말로 뭉개집니다. AKS에서 이 주제가 더 중요한 이유는 Docker가 더 이상 중심이 아니기 때문입니다. 지금 AKS Linux 노드의 기본 runtime 경로는 kubelet에서 CRI를 거쳐 containerd로 내려갑니다. `docker ps`나 dockershim 시절의 디버깅 습관으로는 노드 실행 문제를 정확히 볼 수 없습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 Pod 기동 실패 진단 코드를 요청할 때 실행 사슬 계층을 명시하지 않으면, docker 명령을 사용하거나 실행 단계를 잘못 특정하는 코드가 생성되기 때문입니다.

> kubelet과 containerd의 핵심은 RunPodSandbox → PullImage → CreateContainer → StartContainer라는 실행 순서와 각 단계의 실패 신호를 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- kubelet은 정확히 무엇을 감시하고 어떤 시점에 CRI를 호출할까요?
- dockershim이 사라진 뒤 AKS 노드 디버깅 방식은 왜 달라졌을까요?
- RunPodSandbox, PullImage, CreateContainer, StartContainer는 왜 이 순서로 호출될까요?
- 각 단계 실패 시 kubectl describe에서 어떤 신호가 나타날까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

kubelet과 containerd 실행 경로를 이해하면 AI에게 "Pod ImagePullBackOff 진단 시 kubelet 이벤트, containerd crictl images, ACR 자격증명 순서로 확인하는 명령"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "Pod가 안 뜨는데 원인 찾는 방법?"
→ docker ps, docker logs 명령 제안
→ AKS는 containerd 기반이라 docker 명령 불일치
→ 실행 단계별 구분 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "AKS Pod 기동 실패를 kubelet-CRI-containerd 순서로 진단해줘.
    1) kubelet 이벤트: kubectl describe pod로 Events 확인
       (sandbox 준비 실패 vs image pull 실패 구분)
    2) containerd 상태: crictl ps -a, crictl images
       (docker 명령 대신 crictl 사용)
    3) node SSH: kubectl debug node로 node에 접근해
       journalctl -u containerd로 containerd 로그 확인
    단계별 실패 신호와 원인 구분 명시"
→ 실행 사슬 계층별 정확한 진단
→ docker 명령 대신 crictl 사용
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| AKS 노드에서 docker 명령 사용 시도 | dockershim 제거로 docker는 container runtime 아님 | crictl을 사용해 containerd 직접 조회 |
| image pull 실패와 sandbox 실패 혼동 | 원인 계층이 달라 해결 방법 다름 | kubectl describe Events에서 단계 확인 |
| container runtime 문제를 앱 코드 버그로 가정 | runc 실행 실패는 앱 코드와 무관 | Events에서 runtime 오류 메시지 먼저 확인 |
| kubelet 재시작을 node 재부팅으로 해결 시도 | 과도한 조치, 원인 미파악 | journalctl -u kubelet으로 원인 먼저 확인 |
| CRI 오류를 kubernetes 버그로 가정 | AKS 버전 업그레이드로 해결 안 될 수 있음 | containerd 로그와 이미지 상태 먼저 확인 |

## AI 협업 팁

kubelet/containerd 진단 관련 효과적인 AI 프롬프트 패턴:

1. **Pod 기동 실패 진단 요청**: "AKS Pod ImagePullBackOff를 kubelet Events, crictl, ACR 자격증명 순서로 진단하는 명령 작성해줘"
2. **containerd 상태 확인 요청**: "AKS 노드에서 crictl로 컨테이너 목록과 이미지 목록을 확인하는 명령 작성해줘"
3. **node 디버깅 접근 요청**: "kubectl debug node로 AKS 노드에 접근해 containerd 로그를 journalctl로 확인하는 명령 작성해줘"

예시 프롬프트:
> "AKS Pod CrashLoopBackOff 진단을 실행 단계별로 작성해줘. 1) kubectl describe pod Events로 단계 특정 2) crictl ps -a로 컨테이너 상태 3) kubectl logs --previous로 이전 컨테이너 로그 4) kubectl debug node로 kubelet 로그 확인. dockershim 대신 crictl 사용 명시."

## 운영 체크리스트

- [ ] AKS 노드에서 docker 대신 crictl을 사용하는가?
- [ ] Pod 실패 시 실행 단계(sandbox/image/container)를 Events에서 먼저 확인하는가?
- [ ] kubectl debug node로 node 로컬 진단을 수행할 수 있는가?
- [ ] containerd 로그를 journalctl로 확인하는 방법을 알고 있는가?
- [ ] 다음 글에서 CNI와 Pod IP 할당을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

kubelet과 containerd를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 실행 사슬 계층과 crictl 사용을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 Pod 기동 실패 진단 코드의 완성도는 크게 다릅니다.

## 정리

kubelet과 containerd 편은 바이브코딩을 위한 Azure AKS 심화에서 node-local 실행 경로를 이해하는 핵심 단계입니다. kubelet-CRI-containerd-runc 실행 사슬, dockershim 제거 후 crictl 사용, 단계별 실패 신호를 이해했습니다. 다음 글에서는 CNI와 Pod IP가 어디서 오는지를 다룹니다.

## 참고 자료

- [AKS node access](https://docs.microsoft.com/azure/aks/node-access)
- [containerd runtime](https://containerd.io/)
- [crictl usage](https://kubernetes.io/docs/tasks/debug/debug-cluster/crictl/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-deep-dive/ko/02-kubelet-and-containerd)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure AKS 심화 (1/6): Control Plane 해부
- **바이브코딩을 위한 Azure AKS 심화 (2/6): kubelet과 containerd (현재 글)**
- 바이브코딩을 위한 Azure AKS 심화 (3/6): CNI와 Azure CNI Overlay
- 바이브코딩을 위한 Azure AKS 심화 (4/6): Scheduler와 Pod 배치
- 바이브코딩을 위한 Azure AKS 심화 (5/6): HPA와 Cluster Autoscaler 내부
- 바이브코딩을 위한 Azure AKS 심화 (6/6): KEDA 내부
<!-- toc:end -->

Tags: 바이브코딩, AzureAKS심화, kubelet, AI코딩
