.PHONY: check finalize medium docs

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
