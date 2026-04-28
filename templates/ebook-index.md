# Template: eBook index (`exports/ebook-source/<series>-<lang>/docs/index.md`)
#
# 책의 첫 페이지 / 안내. private mkdocs-ebook 빌더가 표지 다음에 사용한다.

# {{ ebook_title }}

{{ ebook_subtitle }}

저자: {{ author }}
초판: {{ first_edition_date }}
이 판: {{ this_edition_date }}

## 한눈에 보는 목차

{% for chapter in chapters %}
- 제 {{ chapter.number }} 장: {{ chapter.title }}
{% endfor %}

## 라이선스

본 책의 본문은 별도 명시가 없는 한 작성자 저작권을 따릅니다.
인용된 외부 코드는 각 코드의 라이선스를 따릅니다.
