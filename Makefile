.PHONY: check check-quality check-quality-audit refresh-quality-audit check-content check-generated check-links finalize medium docs docs-build docs-serve series sync ebook ebook-build ebook-doctor ebook-upgrade assets-sync assets-sync-dry assets-sync-prune assets-check tistory tistory-one hashnode hashnode-one publish-check

check: check-content check-generated check-links

check-quality: check-quality-audit
	python3 scripts/check_content_quality.py

check-quality-audit:
	python3 scripts/quality_audit.py --check

refresh-quality-audit:
	python3 scripts/quality_audit.py

# Validate source content (style, structure, metadata)
check-content:
	bash .sisyphus/style/check-ko.sh
	python3 scripts/check_catalog.py
	python3 scripts/check_nav_coverage.py
	python3 scripts/check_frontmatter.py
	python3 scripts/check_seo_quality.py
	python3 scripts/check_status_sync.py
	python3 scripts/check_local_paths.py
	python3 scripts/check_image_language.py
	python3 scripts/check_target_language_alignment.py
	python3 scripts/lint_captions.py
	python3 scripts/check_article_structure.py
	python3 scripts/check_ko_headings.py
	python3 scripts/check_code_comments.py
	python3 scripts/check_no_boilerplate_duplication.py
	python3 scripts/check_no_trailing_colon_heading.py
	python3 scripts/check_no_empty_links.py
	python3 scripts/check_intro_no_next_link.py
	python3 scripts/check_no_emoji.py
	python3 scripts/check_en_ai_slop.py
	python3 scripts/check_orphan_assets.py
	python3 scripts/check_ko_ai_cliches.py
	python3 scripts/check_ko_translation_residue.py
	python3 scripts/check_caption_presence.py
	python3 scripts/check_empty_boilerplate_headings.py
	python3 scripts/check_duplicate_series_intro.py
	python3 scripts/check_boilerplate_answers.py
	python3 scripts/check_ko_typos.py
	python3 scripts/check_fences.py
	python3 scripts/check_no_big_picture_section.py
	python3 scripts/check_trivial_code.py
	python3 scripts/check_ko_en_ratio.py
	python3 scripts/check_short_h2.py

# Validate generated outputs (Medium HTML, exports)
check-generated:
	python3 .sisyphus/medium/finalize-posts.py --check
	python3 scripts/check_exports.py
	python3 scripts/check_drift.py

# Validate internal and external links (can be slow)
check-links:
	python3 scripts/check_links.py

finalize:
	python3 .sisyphus/medium/finalize-posts.py

sync:
	python3 scripts/sync_series_per.py
	python3 scripts/build_series_index.py

series: sync

medium:
ifndef SERIES
	$(error SERIES is required: make medium SERIES=azure-functions-101)
endif
	python3 .sisyphus/medium/to-medium.py content/$(SERIES)/en --asset-mode $(ASSET_MODE)
	python3 .sisyphus/medium/finalize-posts.py

docs-build:
	python3 scripts/build_docs.py
	mkdocs build --strict

docs-serve:
	python3 scripts/build_docs.py
	mkdocs serve

docs: docs-serve

# eBook targets — require mkdocs-ebook installed from private repo.
# Run `make ebook-upgrade` first to ensure the latest builder is installed.
# See EBOOK.md §1.3 for the "always latest" policy.

ebook-upgrade:
ifdef GH_TOKEN
	pip install --upgrade --force-reinstall \
	  "git+https://x-access-token:$(GH_TOKEN)@github.com/yeongseon/mkdocs-ebook.git"
else
	pip install --upgrade --force-reinstall \
	  git+ssh://git@github.com/yeongseon/mkdocs-ebook.git
endif

ebook-doctor:
	mkdocs-ebook doctor

ebook:
ifndef SERIES
	$(error SERIES is required: make ebook SERIES=azure-functions-101 LANG=ko)
endif
ifndef LANG
	$(error LANG is required: make ebook SERIES=azure-functions-101 LANG=ko)
endif
	python3 scripts/export_ebook_source.py $(SERIES) --lang $(LANG)

ebook-build:
ifndef SERIES
	$(error SERIES is required: make ebook-build SERIES=azure-functions-101 LANG=ko)
endif
ifndef LANG
	$(error LANG is required: make ebook-build SERIES=azure-functions-101 LANG=ko)
endif
	python3 scripts/export_ebook_source.py $(SERIES) --lang $(LANG)
	mkdocs-ebook doctor
	mkdocs-ebook build exports/ebook-source/$(SERIES)-$(LANG)

# Asset sync targets — require ASSET_TARGET pointing to a book-public-assets checkout.
# See ASSET_POLICY.md for details.

ASSET_TARGET ?= ../book-public-assets
ASSET_MODE ?= public

assets-sync-dry:
	python3 scripts/sync_assets.py --target $(ASSET_TARGET)

assets-sync:
	python3 scripts/sync_assets.py --target $(ASSET_TARGET) --apply

assets-sync-prune:
	python3 scripts/sync_assets.py --target $(ASSET_TARGET) --apply --prune

# Validate public asset URLs against the local book-public-assets checkout.
# Requires ASSET_TARGET to point to a checked-out yeongseon-books/book-public-assets repo.
assets-check:
	python3 scripts/check_public_assets.py --target $(ASSET_TARGET)

# --- Publishing targets ---

tistory:
ifndef SERIES
	$(error SERIES is required: make tistory SERIES=azure-functions-101)
endif
	python3 scripts/export_tistory.py $(SERIES) --all

tistory-one:
ifndef SERIES
	$(error SERIES is required: make tistory-one SERIES=azure-functions-101 EPISODE=1)
endif
ifndef EPISODE
	$(error EPISODE is required: make tistory-one SERIES=azure-functions-101 EPISODE=1)
endif
	python3 scripts/export_tistory.py $(SERIES) --episode $(EPISODE)

hashnode:
ifndef SERIES
	$(error SERIES is required: make hashnode SERIES=rag-deep-dive)
endif
	python3 scripts/export_hashnode.py $(SERIES) --all

hashnode-one:
ifndef SERIES
	$(error SERIES is required: make hashnode-one SERIES=rag-deep-dive EPISODE=1)
endif
ifndef EPISODE
	$(error EPISODE is required: make hashnode-one SERIES=rag-deep-dive EPISODE=1)
endif
	python3 scripts/export_hashnode.py $(SERIES) --episode $(EPISODE)

# Validate existing export artifacts and public asset references.
# This target does not regenerate publishing outputs.
# Run export targets and assets-sync before publish-check when content changed.
publish-check:
	$(MAKE) check
	$(MAKE) docs-build
	$(MAKE) assets-check
