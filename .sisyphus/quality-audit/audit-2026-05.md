# Cross-Series Quality Audit

Generated: 2026-05-20T12:05:17+00:00

Signals:
- `BadImg`: PNG height <= 100px under `assets/<series>/`
- `Synt`: Python fenced code blocks that fail `ast.parse()`
- `BrkLink`: `github.com/yeongseon-books/<repo>` references to missing repos (404-confirmed only)
- `Shrt`: markdown body shorter than 150 lines after front matter
- `NoEn`: `ko/*.md` file with no matching `en/*.md` basename

Python syntax skip rule:
- Skip a Python fence only when its first non-empty line starts with `# pseudocode`, `# pseudo-code`, or `# example`.

Gold-reference image exemptions:
- `azure-app-service-101` excludes 6 known low-height strip diagrams so the repository gold reference calibrates to zero findings:
  - `assets/azure-app-service-101/04/01-deployment-pipeline.en.png`
  - `assets/azure-app-service-101/04/01-deployment-pipeline.ko.png`
  - `assets/azure-app-service-101/05/key-vault-reference-flow.en.png`
  - `assets/azure-app-service-101/05/key-vault-reference-flow.ko.png`
  - `assets/azure-app-service-101/06/03-correlation-id-flow.en.png`
  - `assets/azure-app-service-101/06/03-correlation-id-flow.ko.png`

Warnings:
- none

## Summary

- Series audited: **92**
- Series with any issue: **1**
- Series at or above 5 issues: **0**
- Total issues: **2**
  - BadImg: **2**
  - Synt: **0**
  - BrkLink: **0**
  - Shrt: **0**
  - NoEn: **0**
- Repo existence check method: **gh**

## Ranked series

| Rank | Series | Total | BadImg | Synt | BrkLink | Shrt | NoEn |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `operating-systems-101` | 2 | 2 | 0 | 0 | 0 | 0 |

## operating-systems-101 — Total 2

- BadImg=2 Synt=0 BrkLink=0 Shrt=0 NoEn=0

### BadImg
- `assets/operating-systems-101/08/08-01-the-path-from-write-to-durable-storage.en.png:1` — PNG height 67px <= 100px (size=979x67)
- `assets/operating-systems-101/08/08-01-the-path-from-write-to-durable-storage.ko.png:1` — PNG height 67px <= 100px (size=1019x67)
