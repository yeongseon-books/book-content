---
series: operating-systems-101
episode: 10
title: Containers and the Operating System
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Operating Systems
  - Containers
  - Namespace
  - Cgroup
  - Isolation
seo_description: Namespaces, cgroups, and overlayfs — how containers build isolated environments on a shared kernel and how far that isolation actually goes.
last_reviewed: '2026-05-04'
---

# Containers and the Operating System

This is the final post in the Operating Systems 101 series.

> Operating Systems 101 series (10/10)

<!-- a-grade-intro:begin -->

**Core question**: How do containers differ from virtual machines, and how do they make a shared kernel look like an isolated system?

> Containers are not magic. They are a combination of plain Linux features — namespaces, cgroups, and overlayfs. Every concept from this series — processes, memory, file systems, system calls — reappears inside a container. This article closes the series and bridges OS fundamentals to modern infrastructure.

<!-- a-grade-intro:end -->

## What You Will Learn

- The difference between containers and virtual machines
- Isolation built from namespaces — pid, net, mount, user, etc.
- Resource limits built from cgroups — CPU, memory, I/O
- Image layers and copy-on-write file systems via overlayfs

## Why It Matters

In the container era, knowing the OS means knowing namespaces and cgroups. OOM-kills, CPU throttling, and network isolation problems inside containers all happen on top of OS primitives. If you only know "containers are lightweight VMs," you cannot diagnose the operational incidents that matter most.

> A container is not a new OS. It is a tool that slices the same OS more precisely.

## Concept at a Glance

> A VM puts an entire guest OS on top of a hypervisor. A container reuses the host kernel directly, isolates "what is visible" with namespaces, and limits "how much can be used" with cgroups. So containers are light and start fast, but they share kernel vulnerabilities with the host.

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

## Key Terms

| Term | Description |
| --- | --- |
| Namespace | Isolates what a process sees (PID, network, mounts, etc.) |
| Cgroup | Controls how much a group can use (CPU, memory, I/O) |
| Overlayfs | File system that stacks a read-write layer on a read-only base |
| Capability | A finer-grained slice of root privilege |
| OCI | Standards for container images and runtimes |

## Before / After

**Before — "containers are lightweight VMs":**

```text
Misconception: same isolation level as a VM
Result: surprised that "container escape" is even a thing
```

**After — "containers share the host kernel":**

```text
Truth: isolation is namespaces + cgroups + seccomp + capabilities together
Result: security must be designed as layered defense
```

Knowing the difference, you accept the limits and add the right extra protection (seccomp, rootless, gVisor, etc.).

## Hands-on: Step by Step

### Step 1: PIDs inside a container

```bash
docker run --rm -it alpine sh -c "ps -ef | head"
# Inside the container, PID 1 is sh, not init
```

Thanks to the PID namespace, processes inside a container have their own PID space.

### Step 2: The same process from the host

```bash
# On the host
ps -ef | grep <container PID command>
# The same process appears with a different PID
```

The host can see all container processes; the container cannot see the host. Isolation is asymmetric.

### Step 3: cgroup memory limit

```bash
docker run --rm -m 64m alpine sh -c "
  cat /sys/fs/cgroup/memory.max
  yes 'data' | head -c 200m > /tmp/big || echo 'OOM-killed'
"
# memory.max = 67108864 (64MB), 200MB write → OOM
```

cgroups enforce the limit. Inside a container `free` may show the host total, which is a frequent source of confusion.

### Step 4: See overlayfs layers

```bash
docker pull alpine
docker image inspect alpine | grep -i layer
# Layered file system — sharing a base saves disk
```

Containers using the same base image share disk. That is why containers feel "light."

### Step 5: Inspect capabilities and seccomp

```bash
docker run --rm alpine sh -c "
  cat /proc/self/status | grep Cap
"
# Even as root, the capability set is restricted
```

The "root" inside a default container is weaker than the host root. Capabilities and seccomp slice privilege finely.

## What to Notice in This Code

- Isolation is the sum of namespaces, cgroups, seccomp, and capabilities
- PID 1 inside a container is the container's init; it is just another process on the host
- Container memory limits and `free` see different things, which is a common confusion
- Overlayfs lets containers using the same image share disk

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| "Container == VM" | Overestimates isolation | Layered defense (seccomp, rootless, etc.) |
| Reading memory with `free` inside | Sees the host total | Use cgroup files or `docker stats` |
| Abusing `--privileged` | Effectively removes isolation | Add only the capabilities you need |
| Huge single-layer image | Slow build/deploy, no caching | Multi-stage build plus a small base |
| Using PID 1 directly without an init | Zombies are not reaped | Use tini or `--init` |

## How This Shows Up in Production

- Microservices: one container per service to isolate dependencies
- CI/CD: pin the build environment as an image
- Multi-tenant: cgroup for resource guarantees + network namespace for isolation
- Serverless: extra isolation layers like gVisor or Firecracker
- Dev environments: docker compose / dev containers reproduce the environment

## How a Senior Engineer Thinks

A senior engineer treats containers as "a convenient way to use the OS." Without understanding namespaces, cgroups, and overlayfs, they cannot act when something breaks in production. Every concept from this series — processes, memory, file systems, system calls — reappears inside a container.

A senior also accepts the limits of isolation. Sharing a kernel is the start of the security model, not the end. They combine seccomp, rootless mode, gVisor, and trust-boundary separation as appropriate. Isolation is not "yes or no" but "how far."

## Checklist

- [ ] I can explain the difference between a container and a VM
- [ ] I can describe what namespaces and cgroups do
- [ ] I know how to read memory limits from inside a container
- [ ] I know how overlayfs contributes to disk sharing
- [ ] I know the limits of isolation and the available extra protections

## Practice Problems

1. Quantitatively measure overlayfs savings by comparing the disk usage sum of two containers sharing a base image versus the base image size alone.

2. In a 64MB-limited container, decide a safe cache cap and compare it with the size that triggers OOM-kill.

3. Use strace to confirm which syscalls are blocked when running with vs without the default seccomp profile.

## Wrap-up and Next Steps

A container is not a new OS but a tool that slices the same Linux OS precisely with namespaces, cgroups, and overlayfs. Every OS concept from this series gets reused above containers. To know containers is, finally, to know the OS.

This series ends here. As a next step, follow the same OS concepts outward into networks and distributed systems (Computer Networks 101, Distributed Systems 101), or go deeper into container operations themselves (Docker 101, Kubernetes 101).

<!-- toc:begin -->
- [What is an Operating System?](./01-what-is-an-operating-system.md)
- [Processes and Threads](./02-processes-and-threads.md)
- [Scheduling](./03-scheduling.md)
- [Concurrency and Race Conditions](./04-concurrency-and-race-conditions.md)
- [Locks, Mutexes, and Semaphores](./05-locks-mutex-semaphore.md)
- [Memory Management](./06-memory-management.md)
- [Virtual Memory](./07-virtual-memory.md)
- [File Systems](./08-file-systems.md)
- [System Calls](./09-system-calls.md)
- **Containers and the Operating System (current)**
<!-- toc:end -->

## References

- [Linux namespaces(7)](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Linux cgroups(7)](https://man7.org/linux/man-pages/man7/cgroups.7.html)
- [Open Container Initiative](https://opencontainers.org/)
- [Docker — Overview](https://docs.docker.com/get-started/overview/)

Tags: Computer Science, Operating Systems, Containers, Namespace, Cgroup, Isolation
