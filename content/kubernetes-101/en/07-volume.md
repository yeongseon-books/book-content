---
series: kubernetes-101
episode: 7
title: "Kubernetes 101 (7/10): Volume"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Kubernetes
  - Volume
  - PersistentVolume
  - StorageClass
  - DevOps
seo_description: A beginner guide to Kubernetes Volumes, PVCs, StorageClasses, and the dynamic provisioning flow that keeps data alive across Pod restarts
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (7/10): Volume

Containers are easy to replace because their local filesystem is disposable. That convenience becomes a liability the moment your workload owns state that cannot disappear on the next reschedule.

This is the 7th post in the Kubernetes 101 series.

Here, we will connect Volumes, PersistentVolumeClaims, and StorageClasses into one storage model so you can separate Pod lifetime from data lifetime before stateful workloads become fragile.

> Kubernetes can restart a Pod for you. It preserves data only when you attach the right storage contract outside the Pod.


![kubernetes 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/07/07-01-concept-at-a-glance.en.png)
*kubernetes 101 chapter 7 flow overview*

## Questions to Keep in Mind

- emptyDir* vs *PV/PVC?
- The role of *StorageClass?
- Dynamic provisioning?

## Why It Matters

A container's filesystem vanishes with the Pod—by design. Stateless apps benefit from this disposability: any replica can replace any other. But the moment your workload owns data that must survive restarts (a database, uploaded files, a write-ahead log), you need an explicit storage contract that decouples data lifetime from Pod lifetime. Without it, the next reschedule silently destroys state.

## Key Terms

- **Volume**: storage *shared/persisted* inside a Pod.
- **PersistentVolume (PV)**: a *cluster resource* disk.
- **PersistentVolumeClaim (PVC)**: a Pod's *request* for a disk.
- **StorageClass**: defines *how* a disk is created (ssd, gp3).
- **AccessMode**: *RWO / ROX / RWX*.

## Before / After

**Before**: storing *DB data* inside the Pod — *gone on restart*.

**After**: a *PVC + PV* keeps it on an *external disk*.

## Hands-on: Attach a Disk to a Pod

### Step 1 — PVC

```python
"""
apiVersion: v1
kind: PersistentVolumeClaim
metadata: {name: data}
spec:
  accessModes: [ReadWriteOnce]
  resources: {requests: {storage: 5Gi}}
  storageClassName: gp3
"""
```

A PVC is a request, not a disk. `storageClassName: gp3` tells the cluster which provisioner and disk type to use. If StorageClass is omitted, the cluster's default class applies—which may not match your IOPS or replication requirements.

### Step 2 — Use it in a Pod

```python
"""
spec:
  containers:
  - name: app
    image: postgres:16
    volumeMounts:
    - name: data
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: data
    persistentVolumeClaim: {claimName: data}
"""
```

The container sees `/var/lib/postgresql/data` as a local path, but reads and writes flow through the PVC to an external disk. This indirection is what lets the Pod be deleted and recreated on a different node while data persists.

### Step 3 — Apply

```python
import subprocess

def apply(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
```

With dynamic provisioning, applying the PVC manifest triggers the StorageClass provisioner to create a PV automatically. You rarely need to create PV objects by hand in cloud environments—StorageClass handles the lifecycle.

### Step 4 — Inspect

```python
def get_pvc():
    res = subprocess.run(
        ["kubectl", "get", "pvc"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

A PVC stuck in `Pending` means the provisioner cannot fulfill the request. Check StorageClass name spelling, available capacity in the zone, and whether the requested AccessMode is supported by the underlying driver before assuming an app-level bug.

### Step 5 — Cleanup (carefully)

```python
def delete(name):
    subprocess.run(["kubectl", "delete", "pvc", name], check=True)
```

PVC deletion is irreversible when `reclaimPolicy` is `Delete`—the backing disk is destroyed. Always verify the reclaim policy before removing a PVC in production, and prefer `Retain` for databases until you have a tested backup/restore pipeline.

## Verification workflow

```bash
kubectl get pvc
kubectl describe pvc data
kubectl get pv
```

**Expected output:** the PVC should become `Bound`, `describe pvc` should reveal which StorageClass and PV fulfilled the claim, and the PV list should show the actual storage object and reclaim policy behind the claim.

**Failure modes to check first:**

- A PVC stuck in `Pending` usually means StorageClass, capacity, or access-mode mismatch before it means an app issue.
- A bound claim with mount failure usually means the Pod spec path or volume wiring is wrong.
- PVC deletion is dangerous because a `Delete` reclaim policy may remove the underlying disk too.

## What to Notice in This Code

- The *PVC* receives a *PV dynamically*.
- *RWO* allows *read/write on one node only*.
- *Deleting a PVC* may *delete the disk*.

## Five Common Mistakes

1. **Holding *state* in *emptyDir*.**
2. **Assuming *RWX* is *generally available*.**
3. **Ignoring *reclaimPolicy* and losing data.**
4. **Trusting *PVC alone* without a *backup system*.**
5. **Skipping *StorageClass* and getting only the *default*.**

## How This Shows Up in Production

A *StatefulSet* automatically creates *one PVC per Pod*, and tools like *Velero* periodically *snapshot* volumes.

## How a Senior Engineer Thinks

- *State* is safest *outside the cluster*.
- *RWX* must justify *cost and performance*.
- *Backups* are the real *recovery capability*.
- *reclaimPolicy* is set explicitly.
- *StatefulSet* is the start of *stateful patterns*.

## Checklist

- [ ] *State* lives on a *PVC* or *managed DB*.
- [ ] *Backup* policy exists.
- [ ] *AccessMode* explicit.
- [ ] *reclaimPolicy* explicit.

## Practice Problems

1. State the *difference* between emptyDir and PVC in one line.
2. Name *one constraint* of RWO.
3. Explain in one line *why* PVC alone is *not enough* for backup.

## Wrap-up and Next Steps

State is solved. The next post covers *matching Pod count to load* with *HPA*.

## Answering the Opening Questions

- **Why does container filesystem vanish on Pod restart?**
  - The writable layer atop a container image is discarded when the container dies—by design. Any file written there disappears on restart. Persisting data requires mounting a Volume that exists outside the Pod lifecycle, which is precisely what separates stateless from stateful workloads.
- **When do `emptyDir` and PVC diverge?**
  - `emptyDir` is created with the Pod and deleted with it—suitable for caches and temporary build artifacts. A PVC requests persistent storage decoupled from Pod lifetime, so data survives redeployment. Choose PVC when data must outlive the Pod (databases, uploaded files).
- **What does StorageClass actually decide?**
  - StorageClass bundles provisioner, disk type (SSD/HDD), replication policy, and `reclaimPolicy` into a single rule governing "how to create and destroy this PVC's backing storage." Whether `reclaimPolicy` is `Delete` or `Retain` determines if real data vanishes when the PVC is removed—critical for production data.

<!-- toc:begin -->
## In this series

- [Kubernetes 101 (1/10): What is Kubernetes?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- [Kubernetes 101 (6/10): ConfigMap and Secret](./06-configmap-and-secret.md)
- **Volume (current)**
- HPA (upcoming)
- Helm (upcoming)
- Kubernetes in Operation (upcoming)

<!-- toc:end -->

## References

- [Volumes](https://kubernetes.io/docs/concepts/storage/volumes/)
- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Velero](https://velero.io/)
- [Change the reclaim policy of a PersistentVolume](https://kubernetes.io/docs/tasks/administer-cluster/change-pv-reclaim-policy/)

Tags: Kubernetes, Volume, PersistentVolume, StorageClass, DevOps
