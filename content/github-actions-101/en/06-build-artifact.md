---
series: github-actions-101
episode: 6
title: "GitHub Actions 101 (6/10): Build Artifacts"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - GitHubActions
  - Artifact
  - Build
  - Release
  - CICD
seo_description: From upload-artifact and download-artifact to Releases. Safely store and pass build outputs across jobs and to users.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (6/10): Build Artifacts

If a CI run finishes the build and then throws the output away, the pipeline is only half done. The logs say "success," but no one can later confirm which wheel, archive, or report actually passed validation, and deploy often ends up rebuilding work it should have reused.

That is why artifacts matter more than they first appear to. They preserve the exact output a workflow produced and give later jobs, release tooling, and humans a traceable handoff point.

This is the 6th post in the GitHub Actions 101 series. In this post, we will use artifacts to keep build outputs, move them across jobs, and carry them into GitHub Releases when the workflow becomes an external delivery channel.

![github actions 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/06/06-01-concept-at-a-glance.en.png)
*github actions 101 chapter 6 flow overview*

## Questions to Keep in Mind

- When are `upload-artifact` and `download-artifact` each used?
- Why are artifacts useful for passing results between jobs?
- How does `retention-days` relate to cost?

## Why It Matters

Runners are not permanent servers. When a build job ends, the `dist/` directory inside vanishes with it. Without explicitly storing the output, even a successful build cannot be reused. If the deploy job must repeat the same build in the next stage, time grows and identifying what was actually deployed becomes difficult.

I think of artifacts as "receipts of the build." A record of what input produced what output is necessary before supply-chain security, release reproduction, and rollback decisions can operate reliably.

## Artifact Flow at a Glance

The importance of this flow lies in decoupling build from deploy — they no longer need to share a runner. The next job simply reads the stored output, making pipeline structure far more flexible.

## Key Terms

| Term | Meaning | Practical Point |
| --- | --- | --- |
| Artifact | File bundle produced by a workflow | The means for preserving build results, reports, and logs |
| `upload-artifact` | Action that uploads files to GitHub storage | Keeps results available after job ends |
| `download-artifact` | Downloads artifacts within the same workflow | Reuse without rebuilding in the next job |
| `retention-days` | How long artifacts are kept | Determines both cost and retention policy |
| Release | GitHub's official release page | Good for publishing outputs to external users |

## Before and After

Without artifacts, the moment the build job ends, results effectively vanish. Logs show success, but the actual `dist/*.whl` files are inaccessible to the next job. The workaround becomes either rebuilding in the deploy job or manually uploading files from a local machine.

When the build job uploads results and the deploy job downloads them, "the exact output that passed validation" moves to the next stage untouched. This difference looks small but changes pipeline reliability significantly.

## Artifacts in 5 Steps

### Step 1 — Upload Build Output

```yaml
- run: python -m build
- uses: actions/upload-artifact@v7
  with:
    name: dist
    path: dist/*
    retention-days: 14
```

The key here is moving the output outside the filesystem. It must persist after the build ends so the next step can reference it.

### Step 2 — Download in the Next Job

```yaml
deploy:
  needs: build
  runs-on: ubuntu-latest
  steps:
    - uses: actions/download-artifact@v8
      with:
        name: dist
        path: dist/
    - run: ls dist/
```

Even across different jobs, artifacts can be shared within the same workflow. The important point: the deploy stage does not need to rebuild.

### Step 3 — Bundle Multiple Files

```yaml
- uses: actions/upload-artifact@v7
  with:
    name: reports
    path: |
      coverage.xml
      report.xml
      logs/*.log
```

Artifacts are not only for wheels or binaries. Test reports, coverage results, failure logs — anything you might need to review later can be bundled.

### Step 4 — Auto-publish a Release

```yaml
- uses: softprops/action-gh-release@v2
  if: startsWith(github.ref, 'refs/tags/')
  with:
    files: dist/*
    generate_release_notes: true
```

When the pipeline needs to become an external delivery channel, Releases are the natural next step. Tying them to tag pushes codifies the release procedure.

### Step 5 — Retention Policy

```yaml
- uses: actions/upload-artifact@v7
  with:
    name: nightly-build
    path: dist/
    retention-days: 7
```

Without explicit retention, the default accumulates. For repositories with frequent builds, this setting directly affects cost.

## What to Notice in This Code

- `retention-days` controls both storage cost and retention policy.
- `generate_release_notes` reduces the effort of writing changelogs.
- `download-artifact` works only within the same workflow run.

In other words, artifacts are not a simple storage feature — they are a tool for designing the lifecycle of build outputs.

## Five Common Mistakes

1. **Using outdated `upload-artifact@v3`.** Upgrade to v7.
2. **Uploading everything.** Cost explodes.
3. **Omitting `retention-days`.** Default 90-day retention accumulates silently.
4. **Reusing artifact names.** A second upload with the same name errors out.
5. **No checksum on Releases.** No tamper detection.

The last mistake matters from a supply-chain security perspective. If release files exist, integrity evidence should accompany them.

## How Mature Teams Operate

Mature teams do not just store build outputs. They include checksums, SBOMs, test reports, and coverage results alongside, signing release files when needed. This is how you answer "what was built, what was deployed, and what verification did it pass?" in one place.

Artifact naming also matters. Purpose-revealing names like `dist`, `reports`, `nightly-build` make execution history readable even as runs accumulate.

## Checklist

- [ ] Using `upload-artifact@v7`.
- [ ] `retention-days` is set.
- [ ] Release auto-publishes on tag push.
- [ ] Checksums or signatures are attached.

## Practice Problems

1. Upload pytest report and coverage as a single artifact.
2. Have the deploy job download build job output.
3. Auto-publish a Release on tag push.

## Understanding the Artifact Lifecycle

Artifacts are created within a workflow run and automatically deleted after the configured retention period. Understanding this lifecycle helps balance cost and convenience.

| Timing | Action | Cost Impact |
| --- | --- | --- |
| During job execution | Stored via upload-artifact | Transfer time |
| Within same workflow run | Retrieved via download-artifact in other jobs | Transfer time |
| After run completes | Downloadable from Actions UI | Storage cost |
| After retention-days elapse | Automatically deleted | Cost resolved |

The default retention is 90 days, but 1-7 days suffices for CI purposes. Release artifacts are better attached to GitHub Releases for both permanence and accessibility.

### Artifact Size Limits and Optimization

| Limit | Value |
| --- | --- |
| Maximum single artifact size | 10 GB |
| Total artifact storage per repo (Free) | 500 MB |
| Total artifact storage per repo (Pro) | 2 GB |
| Upload concurrency | Parallel chunks per file |

Practical ways to reduce size:

```yaml
- uses: actions/upload-artifact@v7
  with:
    name: dist
    path: |
      dist/*.whl
      dist/*.tar.gz
    # Exclude unnecessary files
    if-no-files-found: error
    retention-days: 3
    compression-level: 6
```

`if-no-files-found: error` explicitly fails when the build produced no files. The default `warn` allows an empty artifact to upload while the job succeeds, leading to download failures in the next job.

---

## Python Package Build Strategy

Python project build artifacts are typically wheels (.whl) and source distributions (.tar.gz).

### pyproject.toml-Based Build

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install build tools
        run: pip install build

      - name: Build package
        run: python -m build

      - name: Verify build output
        run: |
          ls -la dist/
          pip install twine
          twine check dist/*

      - uses: actions/upload-artifact@v7
        with:
          name: dist-${{ github.sha }}
          path: dist/
          retention-days: 7
```

`twine check` validates package metadata. Passing this check before PyPI upload prevents upload failures.

### Version in Artifact Names

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.value }}
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0  # needed for git describe

      - id: version
        run: |
          VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
          echo "value=${VERSION}" >> "$GITHUB_OUTPUT"

      - run: python -m build

      - uses: actions/upload-artifact@v7
        with:
          name: myapp-${{ steps.version.outputs.value }}
          path: dist/
```

Including the version in artifact names makes it immediately clear which build corresponds to which version.

---

## Cross-Job Artifact Passing Patterns

The pattern for using build results in subsequent jobs (test, deploy):

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: python -m build
      - uses: actions/upload-artifact@v7
        with:
          name: dist
          path: dist/

  test-install:
    needs: build
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}

      - uses: actions/download-artifact@v7
        with:
          name: dist
          path: dist/

      - name: Test wheel installation
        run: |
          pip install dist/*.whl
          python -c "import myapp; print(myapp.__version__)"

  publish:
    needs: [build, test-install]
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # PyPI trusted publishing
    steps:
      - uses: actions/download-artifact@v7
        with:
          name: dist
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

The workflow flow:

1. **build**: Build once and store the artifact.
2. **test-install**: Verify wheel installation across multiple environments. Confirms the built package is actually installable.
3. **publish**: Deploy to PyPI only on tag push. Uses trusted publishing — no token needed.

The key principle is "build once, verify many times, deploy once." Rebuilding in every job risks environment-difference issues.

---

## GitHub Release and Artifact Connection

Artifacts are temporary storage. Build outputs needing permanent retention belong in GitHub Releases.

```yaml
jobs:
  release:
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: python -m build

      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          files: |
            dist/*.whl
            dist/*.tar.gz
          generate_release_notes: true
          draft: false
          prerelease: ${{ contains(github.ref, 'rc') || contains(github.ref, 'beta') }}
```

`generate_release_notes: true` automatically includes commits and PRs since the last release in the notes. The `prerelease` flag automatically marks releases as pre-release when the tag contains `rc` or `beta`.

---

## Multi-Platform Builds and Artifact Merging

When distributing Python packages with C extensions or binaries, you need to build on multiple OSes and combine the results.

```yaml
jobs:
  build-wheels:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: pip install build
      - run: python -m build --wheel

      - uses: actions/upload-artifact@v7
        with:
          name: wheel-${{ matrix.os }}
          path: dist/*.whl

  merge-and-publish:
    needs: build-wheels
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v7
        with:
          path: all-wheels/
          pattern: wheel-*
          merge-multiple: true

      - run: ls -la all-wheels/
      # All platform wheels are now in one directory
```

`merge-multiple: true` combines multiple artifacts into a single directory. Wheels uploaded per-OS from the matrix are gathered in one place for release attachment or PyPI upload.

---

## Build Cache Strategy

Another way to reduce build time is caching intermediate results.

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      .mypy_cache
      .ruff_cache
      .pytest_cache
    key: build-${{ runner.os }}-${{ hashFiles('pyproject.toml', 'requirements*.txt') }}
    restore-keys: |
      build-${{ runner.os }}-
```

Understanding the difference between cache and artifacts is important:

| Aspect | Cache | Artifact |
| --- | --- | --- |
| Purpose | Speed up execution | Pass results between jobs |
| Access scope | All workflows in the same repo | Within the same workflow run |
| Key mechanism | Hash-based matching | Name-based |
| Retention | Removed after 7 days unused | retention-days setting |
| UI download | Not possible | Possible |

Cache is for "repeating the same work faster"; artifacts are for "passing results to the next stage."

---

## Artifact Security Considerations

Ensure artifacts do not contain sensitive information.

1. **Verify environment variables or secrets are not embedded in build outputs.** `.env` files or config files mixed into artifacts can be exposed via other jobs or UI downloads.
2. **Understand artifact access permissions.** All jobs within the same workflow run can download artifacts. Artifacts from fork PR workflows are also accessible from the source repository.
3. **Set retention to the minimum necessary.** Shorter retention reduces both exposure risk and storage cost simultaneously.

```yaml
- uses: actions/upload-artifact@v7
  with:
    name: build-output
    path: |
      dist/
      !dist/**/*.env
      !dist/**/config.local.*
    retention-days: 1
```

The `!` pattern explicitly excludes potentially sensitive files, preventing accidental exposure.

---

## Cross-Workflow Artifact Sharing

Within the same workflow run, `download-artifact` handles sharing easily. When you need artifacts from a different workflow, additional configuration is required.

### workflow_run for Cross-Workflow Artifact Transfer

```yaml
# .github/workflows/deploy.yml
name: deploy
on:
  workflow_run:
    workflows: ["build"]
    types: [completed]
    branches: [main]

jobs:
  deploy:
    if: github.event.workflow_run.conclusion == 'success'
    runs-on: ubuntu-latest
    steps:
      - name: Download build artifact
        uses: actions/download-artifact@v7
        with:
          name: dist
          path: dist/
          github-token: ${{ secrets.GITHUB_TOKEN }}
          run-id: ${{ github.event.workflow_run.id }}

      - name: Deploy
        run: ./scripts/deploy.sh
```

The `workflow_run` event fires after another workflow completes. Specifying `run-id` retrieves artifacts from that specific run. This pattern fully separates build from deploy while sharing artifacts — advantageous for both security and separation of concerns.

### API-Based Artifact Access

When programmatic access to artifacts is needed, use the GitHub REST API:

```yaml
- name: Download latest successful build artifact
  run: |
    ARTIFACT_URL=$(gh api repos/${{ github.repository }}/actions/artifacts \
      --jq '.artifacts[] | select(.name == "dist") | .archive_download_url' \
      | head -1)

    curl -L -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \
      "$ARTIFACT_URL" -o artifact.zip
    unzip artifact.zip -d dist/
```

This approach is flexible but complex. Prefer `download-artifact` or the `workflow_run` pattern when possible.

---

## Build Reproducibility

To prevent "builds locally but not in CI," manage reproducibility consciously.

```yaml
- name: Record build environment
  run: |
    python --version >> build-env.txt
    pip --version >> build-env.txt
    pip freeze >> build-env.txt
    echo "OS: $(uname -a)" >> build-env.txt
    echo "Date: $(date -u)" >> build-env.txt

- uses: actions/upload-artifact@v7
  with:
    name: build-env-${{ github.sha }}
    path: build-env.txt
    retention-days: 30
```

Recording build environment information as an artifact enables tracing "what environment produced this build?" later. Useful in incident retrospectives.

Additional reproducibility measures:

- **Lock files**: Use `requirements.lock` generated by `pip-compile` in CI.
- **Pin Python version**: Use `"3.12.4"` instead of `"3.12"` to pin the patch version.
- **Pin build tool versions**: Use `pip install build==1.2.1` to fix build tool versions.

## Answering the Opening Questions

- **When are `upload-artifact` and `download-artifact` each used?**
  - `upload-artifact` stores job outputs (build artifacts, test reports, logs) in the workflow run. `download-artifact` retrieves artifacts from a previous job in the next job. The "build once, verify many times" pattern operates on these two actions.
- **Why are artifacts useful for passing results between jobs?**
  - Jobs run on different runners and don't share filesystems. `outputs` can only pass short strings; files like built wheels or test reports can only be passed via artifacts. Rebuilding in every job also risks environment-difference issues, so sharing one build result via artifacts is more stable.
- **How does `retention-days` relate to cost?**
  - Artifacts consume storage during retention — 500MB on Free, 2GB on Pro. Leaving retention at 90 days (default) quickly fills the limit with a few days of build artifacts. 1-3 days for CI purposes and attaching releases separately to GitHub Releases keeps costs reasonable.
<!-- toc:begin -->
## In this series

- [GitHub Actions 101 (1/10): What Is GitHub Actions?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflows and Jobs](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Understanding Triggers](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python Test Automation](./04-python-test-automation.md)
- [GitHub Actions 101 (5/10): Lint and Type Check](./05-lint-and-typecheck.md)
- **Build Artifacts (current)**
- Docker Build (upcoming)
- Deployment Automation (upcoming)
- Secret Management (upcoming)
- A Real-World CI/CD Pipeline (upcoming)

<!-- toc:end -->

## References

- [actions/upload-artifact](https://github.com/actions/upload-artifact)
- [actions/download-artifact](https://github.com/actions/download-artifact)
- [softprops/action-gh-release](https://github.com/softprops/action-gh-release)
- [About artifacts](https://docs.github.com/actions/using-workflows/storing-workflow-data-as-artifacts)
- [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/)

Tags: GitHubActions, Artifact, Build, Release, CICD
