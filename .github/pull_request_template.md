## Summary

<!-- Brief description of the changes -->

## Checklist

### Content (if articles changed)

- [ ] H1 matches front matter `title`
- [ ] Required front matter fields present
- [ ] Questions block exists (for publish-ready+)
- [ ] Mental model blockquote exists (for publish-ready+)
- [ ] Minimal runnable example exists where applicable
- [ ] References section exists
- [ ] Tags line exists as last line

### Publishing (if publishing targets changed)

- [ ] Tistory export tested (`scripts/export_tistory.py`)
- [ ] Medium HTML regenerated (`.sisyphus/medium/to-medium.py`)
- [ ] MkDocs build tested (`make docs-build`)
- [ ] eBook source export tested if applicable

### Validation

- [ ] `make check` passed
- [ ] `make docs-build` passed (if MkDocs output changed)
