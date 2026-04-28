# Template: series index page (`docs/<lang>/<series>/index.md`)
#
# scripts/build_docs.py 가 series.yaml 로부터 자동 생성한다.
# 본 템플릿은 수동 수정이 필요한 경우의 fallback.
---
title: "{{ series_title }}"
description: "{{ series_description }}"
---

# {{ series_title }}

{{ series_description }}

## Episodes

{% for ep in episodes %}
- [{{ ep.number }}. {{ ep.title }}]({{ ep.slug }}.md)
{% endfor %}

## Tags

{{ tags | join(", ") }}
