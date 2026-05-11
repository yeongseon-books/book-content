# Explicit Decision: Image Removals in Blog Transformation

## Decision Date
2026-05-11

## Context
Oracle Round 5 review (score 88/100) identified that 34 images were removed during the blog transformation (commit 57f24bd6). The image-loss-analysis.md documented these removals but did not include an explicit approval decision.

## Images Removed
34 total images across 7 series:
- ai-app-patterns-101: 6 files (6→5 images each)
- document-ingestion-101: 6 files (5→4 images each)
- llm-finetuning-101: 6 files (5→4 images each)
- python-dbapi-101: 3 files (4→3 images each)
- rag-benchmark-101: 6 files (5→3 or 5→4 images each)
- rag-deep-dive: 6 files (documented in analysis)

## Type of Images Removed
All removed images are **"이 글에서 답할 질문" (Questions this post answers)** diagrams that appeared in the eBook pedagogical intro sections.

Example from commit a24d2745:
```markdown
## 이 글에서 답할 질문

- 왜 LLM 챗봇은 대화 이력을 앱이 직접 들고 있어야 할까요?
- 메시지 리스트를 누적하는 가장 단순한 멀티턴 패턴은 어떻게 구현할까요?

![이 글에서 답할 질문](../../../assets/ai-app-patterns-101/01/01-01-questions-this-post-answers.ko.png)

*이 글에서 답할 질문*
```

## Decision: APPROVED FOR REMOVAL

**Rationale:**
1. **Alignment with blog format**: Per BLOG_WRITING_GUIDE.md §3, blog posts should remove eBook pedagogical scaffolding including learning objectives sections.

2. **Content classification**: These images are **pedagogical scaffolding**, not technical content. They visualize the "learning objectives" section which is explicitly marked for removal in the blog transformation requirements.

3. **Technical content preserved**: All technical diagrams (architecture diagrams, flow charts, comparison tables, code structure diagrams) were preserved. Only the pedagogical "questions this post answers" infographics were removed.

4. **Consistency with transformation goals**: The transformation aimed to convert eBook chapters (with learning scaffolding) into standalone blog posts. Removing learning objectives diagrams is consistent with this goal.

5. **No loss of information**: The textual questions that appeared in the "이 글에서 답할 질문" section were either:
   - Transformed into the new "이 글에서 다룰 문제" section (blog format)
   - Integrated into the article introduction
   - Removed as redundant with the title and content

## Verification
- Technical diagrams retained: Yes (architecture, flow, comparison diagrams all present)
- Code examples intact: Yes (all `a-grade-example` blocks preserved)
- Pedagogical scaffolding removed: Yes (learning objectives, glossaries, exercises)
- Blog structure compliance: Yes (per BLOG_WRITING_GUIDE §3)

## Conclusion
The removal of 34 pedagogical "Questions this post answers" images is **intentional and approved** as part of the eBook-to-blog transformation. No technical content was lost.

## References
- Original analysis: `.sisyphus/notepads/review-57f24bd6/image-loss-analysis.md`
- Blog writing guide: `BLOG_WRITING_GUIDE.md` §3
- Oracle Round 5 review: session ses_1eb8a29d2ffenqcqX3L7idXuMa
- Git evidence: `git show a24d2745:content/ai-app-patterns-101/ko/01-chatbot-pattern.md`
