# Copyright Notice Templates

> Used by publishing exports to insert copyright information.
> Values are sourced from `series.yaml` meta block.

## Korean (eBook / Tistory)

```
© {copyright_year} {copyright_holder}. All rights reserved.

이 글의 무단 복제·배포를 금합니다. 개인 학습 목적의 링크 공유는 허용됩니다.
```

## English (Medium / Hashnode)

```
© {copyright_year} {copyright_holder}. All rights reserved.

Unauthorized reproduction or distribution is prohibited.
Sharing links for personal learning purposes is permitted.
```

## Placeholders

| Placeholder | Source | Example |
| --- | --- | --- |
| `{copyright_year}` | `series.yaml` → `meta.copyright_year` | 2026 |
| `{copyright_holder}` | `series.yaml` → `meta.copyright_holder` | YeongseonBooks |

## Insertion Policy

- **Tistory**: Not inserted automatically. The author adds a copyright footer
  manually if desired.
- **Medium**: Not inserted automatically. Medium's own terms cover republishing.
- **eBook**: Inserted as a copyright page by `mkdocs-ebook` builder. The builder
  reads `meta.copyright_holder` and `meta.copyright_year` from the source bundle's
  `series.yaml`.
- **MkDocs web book**: Shown in the site footer via `mkdocs.yml` `copyright` field.
