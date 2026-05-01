.PHONY: check finalize medium docs ebook ebook-build ebook-doctor ebook-upgrade

check:
	python3 .sisyphus/medium/finalize-posts.py --check
	bash .sisyphus/style/check-ko.sh
	python3 scripts/check_catalog.py
	python3 scripts/check_exports.py
	python3 scripts/check_frontmatter.py
	python3 scripts/lint_captions.py
	python3 scripts/check_links.py

finalize:
	python3 .sisyphus/medium/finalize-posts.py

medium:
ifndef SERIES
	$(error SERIES is required: make medium SERIES=langgraph-101)
endif
	python3 .sisyphus/medium/to-medium.py content/$(SERIES)/en
	python3 .sisyphus/medium/finalize-posts.py

docs:
	python3 scripts/build_docs.py
	mkdocs serve

# eBook targets — require mkdocs-ebook installed from private repo.
# Run `make ebook-upgrade` first to ensure the latest builder is installed.
# See EBOOK.md §1.3 for the "always latest" policy.

ebook-upgrade:
	pip install --upgrade --force-reinstall \
	  git+ssh://git@github.com/yeongseon/mkdocs-ebook.git

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
