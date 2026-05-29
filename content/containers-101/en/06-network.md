---
series: containers-101
episode: 6
title: "Containers 101 (6/10): Network"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
- Containers
- Docker
- Networking
- Bridge
- DevOps
seo_description: Container network modes (bridge, host, overlay) and DNS-based service
  discovery — explained with hands-on docker network examples.
last_reviewed: '2026-05-15'
---

# Containers 101 (6/10): Network

Container networking can look like a matter of ports and IP addresses. In practice, restart and rescheduling pressure make name-based discovery and boundary design much more important than memorizing one static address.

This is the 6th post in the Containers 101 series.

In this chapter, we compare bridge, host, overlay, and none, then explain why user-defined networks and DNS names are the stable foundation behind both Compose and Kubernetes.

> Stable container networking starts with names and boundaries, not with memorized IP addresses.


![containers 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/06/06-01-concept-at-a-glance.en.png)
*containers 101 chapter 6 flow overview*
> Container networking is not just about port mapping; it is about choosing which containers can see each other and how traffic flows between them.

## Questions to Keep in Mind

- The bridge / host / overlay / none modes?
- Container-to-container DNS?
- Publish (-p) vs expose?

## Why It Matters

Both Compose and Kubernetes ride on top of these abstractions. If you do not understand bridge isolation, DNS discovery, and publish vs expose, debugging connectivity issues in multi-container setups becomes guesswork. In production, the first question during an outage is often "can container A reach container B?"—and the answer lives in network configuration, not application code.

bridge mode isolates containers on a virtual network. host mode runs the container with the host network stack (no isolation, higher performance). overlay spreads containers across multiple hosts. DNS lets containers find each other by service name.

bridge mode isolates containers on a virtual network. host mode runs the container with the host network stack (no isolation, higher performance). overlay spreads containers across multiple hosts. DNS lets containers find each other by service name.

## Key Terms

- **bridge**: the default virtual L2 network.
- **host**: shares the host network namespace.
- **overlay**: spans multiple hosts.
- **none**: no network at all.
- **expose**: documents an internal port; does not publish it.

## Before/After

**Before**: containers communicate by IP — they break on restart.

**After**: a user-defined bridge gives them DNS names that survive restarts.

## Hands-on: User-Defined Network

### Step 1 — Create

```python
import subprocess

def create_net(name):
    subprocess.run(["docker", "network", "create", name], check=True)
```

A user-defined network provides built-in DNS resolution between containers. Unlike the default bridge, containers on a user-defined network can reach each other by name—critical for stable service discovery.

### Step 2 — Run DB

```python
def run_db(net):
    subprocess.run([
        "docker", "run", "-d", "--name", "db", "--network", net,
        "-e", "POSTGRES_PASSWORD=secret", "postgres:16",
    ], check=True)
```

The database container does not publish any ports externally—it is only reachable from other containers on the same network. This is the network boundary in action: external traffic cannot reach the DB directly.

### Step 3 — Run app

```python
def run_app(net):
    subprocess.run([
        "docker", "run", "-d", "--name", "app", "--network", net,
        "-p", "8080:8080",
        "-e", "DB_HOST=db",
        "myorg/app:latest",
    ], check=True)
```

The app container uses `DB_HOST=db` to find the database by DNS name. If the DB container restarts with a new IP, DNS still resolves correctly. This is why name-based discovery beats hardcoded IPs.

### Step 4 — Inspect

```python
def inspect(net):
    res = subprocess.run(
        ["docker", "network", "inspect", net],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

`docker network inspect` shows which containers are attached, their assigned IPs, and the network driver. Use this to verify connectivity assumptions before debugging at the application level.

### Step 5 — Cleanup

```python
def cleanup(net):
    subprocess.run(["docker", "rm", "-f", "app", "db"])
    subprocess.run(["docker", "network", "rm", net])
```

Always remove containers before the network—Docker refuses to remove a network with active endpoints. This ordering mirrors production teardown: drain traffic, stop services, then remove infrastructure.

## What to Notice in This Code

- `DB_HOST=db` uses the DNS name.
- User-defined networks beat the default bridge.
- `-p` only when you actually want external exposure.

## Quick verification and failure signals

```bash
docker network create app-net
docker run -d --name db --network app-net -e POSTGRES_PASSWORD=secret postgres:16
docker run --rm --network app-net busybox nslookup db
docker network inspect app-net
```

**Expected output:**
- `nslookup db` resolves through the user-defined network DNS.
- `docker network inspect` shows the attached container membership.

**Check first if it fails:**
- If name resolution fails, verify both containers are on the same network.
- If outside access fails, inspect published ports and the app bind address together.
- If host mode is involved, check port collisions and firewall policy first.

## Five Common Mistakes

1. **Using the default bridge — no DNS.**
2. **Publishing the DB with `-p` — public exposure.**
3. **Confusing overlay with bridge.**
4. **Overusing host mode and hitting port collisions.**
5. **Letting unused networks pile up.**

## How This Shows Up in Production

Compose creates a per-project user-defined network. Kubernetes uses a CNI to give every Pod L3 connectivity.

## How a Senior Engineer Thinks

- DNS is the foundation of connection.
- External exposure is an explicit decision.
- Mode choice has security consequences.
- Networks are state — clean them up.
- Compose and K8s abstract things, but the principles do not change.

## Checklist

- [ ] User-defined networks in use.
- [ ] DB is not externally published.
- [ ] Communication via DNS names.
- [ ] Unused networks cleaned up.

## Practice Problems

1. Limitation of the default bridge, in one line.
2. One canonical use of an overlay network.
3. Difference between `expose` and `publish (-p)`, in one line.

## Wrap-up and Next Steps

Once connectivity is solved, the next question is *where to keep images*. The next post covers Registry.

## Answering the Opening Questions

- **What distinguishes bridge, host, overlay, and none modes?**
  - Bridge is a virtual L2 network within a single host — user-defined bridges support DNS name resolution. Host shares the host network directly for no-NAT speed but weaker isolation. Overlay connects containers across multiple hosts into one logical network for distributed services. None blocks communication entirely for security testing or batch isolation.
- **How do containers on the same host find each other by name?**
  - Containers on a user-defined bridge resolve container names to IPs through Docker's built-in DNS server (127.0.0.11). Even if a container restarts and gets a new IP, the DNS record auto-updates so connection configurations need no changes.
- **How do `publish (-p)` and `expose` differ?**
  - `expose` is a documentation directive in the Dockerfile declaring "this container uses this port." It doesn't actually open the port. `-p` is a runtime decision mapping a host port to a container port — only this routes external traffic to the container. Internal services should use `expose` only, with `-p` reserved for entry-point services.
<!-- toc:begin -->
## In this series

- [Containers 101 (1/10): What is a Container?](./01-what-is-a-container.md)
- [Containers 101 (2/10): Image and Layer](./02-image-and-layer.md)
- [Containers 101 (3/10): Runtime](./03-runtime.md)
- [Containers 101 (4/10): Dockerfile](./04-dockerfile.md)
- [Containers 101 (5/10): Volume](./05-volume.md)
- **Network (current)**
- Registry (upcoming)
- Container Security (upcoming)
- Containers vs VMs (upcoming)
- Build a Container App (upcoming)

<!-- toc:end -->

## References

- [Docker networking overview](https://docs.docker.com/network/)
- [Bridge networks](https://docs.docker.com/network/bridge/)
- [Overlay networks](https://docs.docker.com/network/overlay/)
- [DNS in Docker](https://docs.docker.com/network/network-tutorial-standalone/)

Tags: Containers, Docker, Kubernetes, DevOps
