# 34 Files That Lost One Image Each in Commit 57f24bd6

## Summary
The transformation script removed 34 images from Korean content files across 7 series. All affected images are the "이 글에서 답할 질문" (Questions this post answers) diagrams that appear early in articles, plus 2-3 additional diagnostic images from python-dbapi-101 and rag-benchmark-101.

## Root Cause
The transformation script from commit a24d2745 → 57f24bd6 was designed to restructure Korean articles to blog format. During this process:
- Intro blocks containing the "이 글에서 답할 질문" images were removed
- The python-dbapi-101 series lost architecture/design images 
- rag-benchmark-101/01 lost an extra diagnostic image

## Affected Files by Series

### ai-app-patterns-101 (6 files)
- content/ai-app-patterns-101/ko/01-chatbot-pattern.md (6→5 images)
- content/ai-app-patterns-101/ko/02-rag-qa-pattern.md (6→5 images)
- content/ai-app-patterns-101/ko/03-document-assistant.md (6→5 images)
- content/ai-app-patterns-101/ko/04-agent-tool-pattern.md (6→5 images)
- content/ai-app-patterns-101/ko/05-workflow-automation.md (6→5 images)
- content/ai-app-patterns-101/ko/06-human-in-the-loop.md (6→5 images)

### document-ingestion-101 (6 files)
- content/document-ingestion-101/ko/01-pdf-parsing.md (5→4 images)
- content/document-ingestion-101/ko/02-chunking-strategies.md (5→4 images)
- content/document-ingestion-101/ko/03-metadata-filtering.md (5→4 images)
- content/document-ingestion-101/ko/04-incremental-indexing.md (5→4 images)
- content/document-ingestion-101/ko/05-multi-format-pipeline.md (5→4 images)
- content/document-ingestion-101/ko/06-pipeline-completion.md (5→4 images)

### llm-finetuning-101 (6 files)
- content/llm-finetuning-101/ko/01-intro.md (5→4 images)
- content/llm-finetuning-101/ko/02-dataset.md (5→4 images)
- content/llm-finetuning-101/ko/03-lora.md (5→4 images)
- content/llm-finetuning-101/ko/04-training.md (5→4 images)
- content/llm-finetuning-101/ko/05-evaluation.md (5→4 images)
- content/llm-finetuning-101/ko/06-serving.md (5→4 images)

### python-dbapi-101 (3 files)
- content/python-dbapi-101/ko/01-why-db-api-pep-249.md (4→3 images)
- content/python-dbapi-101/ko/02-connection-cursor-lifecycle.md (4→3 images)
- content/python-dbapi-101/ko/03-execute-fetch-patterns.md (4→3 images)

### rag-benchmark-101 (6 files)
- content/rag-benchmark-101/ko/01-evaluation-metrics.md (5→3 images, **-2 images**)
- content/rag-benchmark-101/ko/02-retrieval-benchmarking.md (5→4 images)
- content/rag-benchmark-101/ko/03-embedding-comparison.md (5→4 images)
- content/rag-benchmark-101/ko/04-vectordb-selection.md (5→4 images)
- content/rag-benchmark-101/ko/05-e2e-evaluation.md (5→4 images)
- content/rag-benchmark-101/ko/06-benchmark-complete.md (5→4 images)

### rag-deep-dive (6 files)
- content/rag-deep-dive/ko/01-document-loading-and-chunking.md (6→5 images)
- content/rag-deep-dive/ko/02-embeddings-and-vector-index.md (6→5 images)
- content/rag-deep-dive/ko/03-retriever-design.md (6→5 images)
- content/rag-deep-dive/ko/04-prompt-construction-and-context-injection.md (6→5 images)
- content/rag-deep-dive/ko/05-rag-chain-assembly.md (6→5 images)
- content/rag-deep-dive/ko/06-evaluation-and-quality-gates.md (6→5 images)

## Removed Image Patterns

### "이 글에서 답할 질문" (Questions Diagrams) - 30 files
- Path pattern: `../../../assets/<series>/<NN>/<NN>-01-questions-this-post-answers.ko.png`
- Context: These were part of the intro section that was restructured during blog format transformation
- Impact: Series visual consistency reduced; readers miss the "questions answered" summary

### Architecture/Design Images - 4 files
From python-dbapi-101:
- `01-01-why-db-api-2-0-the-problem-pep-249-solve.ko.png`
- `02-01-connection-and-cursor-lifecycle.ko.png`
- `03-01-execute-executemany-and-fetch-patterns.ko.png`

From rag-benchmark-101:
- `01-05-per-query-and-average-report-reading-flo.ko.png` (rag-benchmark-101/01)

## Remediation Strategy

**For Blog Format Consistency:**
- These intro question images may have been intentionally removed to match the new blog-first structure
- Verify if this is desired behavior per BLOG_WRITING_GUIDE.md

**For eBook/Long-form Content:**
- These images should be restored when building complete eBook versions
- Consider retaining in en/*.md versions if they exist and were preserved there

**For Web/MkDocs Display:**
- Verify if the missing images affect TOC, landing pages, or series index displays
- Check `.sisyphus/medium/to-medium.py` for image handling rules

## Verification Commands

Count remaining images in affected series:
```bash
find content/ai-app-patterns-101/ko -name "*.md" -exec grep -c "!\[" {} + | awk '{s+=$1} END {print "ai-app-patterns-101: " s}'
find content/document-ingestion-101/ko -name "*.md" -exec grep -c "!\[" {} + | awk '{s+=$1} END {print "document-ingestion-101: " s}'
find content/llm-finetuning-101/ko -name "*.md" -exec grep -c "!\[" {} + | awk '{s+=$1} END {print "llm-finetuning-101: " s}'
find content/python-dbapi-101/ko -name "*.md" -exec grep -c "!\[" {} + | awk '{s+=$1} END {print "python-dbapi-101: " s}'
find content/rag-benchmark-101/ko -name "*.md" -exec grep -c "!\[" {} + | awk '{s+=$1} END {print "rag-benchmark-101: " s}'
find content/rag-deep-dive/ko -name "*.md" -exec grep -c "!\[" {} + | awk '{s+=$1} END {print "rag-deep-dive: " s}'
```

Compare to previous commit:
```bash
git diff a24d2745 57f24bd6 -- 'content/**/*.md' | grep '^-!\[' | wc -l
```

## Next Steps

1. Review BLOG_WRITING_GUIDE.md to understand if image removal is intentional
2. Check if en/*.md versions kept these images
3. Decide: restore images or document as intentional structural change
4. Update ROADMAP.md if this is outstanding technical debt
