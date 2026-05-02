.PHONY: check check-content check-generated check-links finalize medium docs docs-build docs-serve series sync ebook ebook-build ebook-doctor ebook-upgrade assets-sync assets-sync-dry assets-sync-prune assets-check tistory tistory-one hashnode hashnode-one publish-check

check: check-content check-generated check-links

# Validate source content (style, structure, metadata)
check-content:
	bash .sisyphus/style/check-ko.sh
	python3 scripts/check_catalog.py
	python3 scripts/check_frontmatter.py
	python3 scripts/lint_captions.py
	python3 scripts/check_article_structure.py

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
	python3 scripts/gen_series_md.py

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
