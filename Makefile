.PHONY: check finalize medium docs docs-build docs-serve series sync ebook ebook-build ebook-doctor ebook-upgrade assets-sync assets-sync-dry assets-sync-prune

check:
	python3 .sisyphus/medium/finalize-posts.py --check
	bash .sisyphus/style/check-ko.sh
	python3 scripts/check_catalog.py
	python3 scripts/check_exports.py
	python3 scripts/check_frontmatter.py
	python3 scripts/lint_captions.py
	python3 scripts/check_links.py
	python3 scripts/check_article_structure.py

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
	python3 .sisyphus/medium/finalize-posts.py
	python3 .sisyphus/medium/to-medium.py content/$(SERIES)/en --asset-mode $(ASSET_MODE)

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
