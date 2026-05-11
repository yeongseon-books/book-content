# Article Structure Technical Debt

## Status as of 2026-05-11 (commit ac39246d)

After blog transformation and validator fix, **100 articles still lack the required blog opening structure** per BLOG_WRITING_GUIDE §3.

## Original Issue (Oracle Round 5)
Oracle identified 153 article structure warnings ("missing questions block").

## Resolution
1. **Fixed validator** (commit ac39246d):
   - Updated `KO_QUESTIONS` regex to accept `다룰 문제` (blog format)
   - Previously only accepted `답할 질문` / `다룰 질문` (eBook format)
   - This fixed 53 false positives where articles had the correct blog format but validator didn't recognize it

2. **Remaining debt: 100 articles**:
   - These articles genuinely lack `## 이 글에서 다룰 문제` or `## 이 글에서 답할 질문` section
   - Not a validator bug - these need content transformation

## Required Blog Opening Structure (BLOG_WRITING_GUIDE §3)
```markdown
# Title

## 이 글에서 다룰 문제
- Problem statement 1
- Problem statement 2

> Mental model / one-sentence conclusion

## 배경 설명
...
```

## Affected Files
Run to see current list:
```bash
python3 scripts/check_article_structure.py 2>&1 | grep "missing questions block" -B 1 | grep "WARN"
```

Sample series with missing opening sections:
- ai-agent-101: 9/10 files (episodes 2-10)
- ai-app-patterns-101: some files
- azure-* series: various files
- And others across the repository

## Impact Assessment

**Severity: Medium**
- Articles are functionally complete with technical content
- Missing standardized blog opening pattern
- Affects discoverability and SEO optimization
- Does not block publishing to current platforms (Tistory, Medium, Hashnode)

**Blocking for:**
- Oracle 100/100 approval (currently 88/100)
- Full BLOG_WRITING_GUIDE §3 compliance

**Non-blocking for:**
- Repository quality gates (`make check` passes)
- Content accuracy and technical completeness
- Current publishing workflows

## Remediation Options

### Option A: Automated transformation (RISKY)
- Create script to generate `## 이 글에서 다룰 문제` sections
- Risk: AI-generated problem statements may misrepresent content
- Effort: Medium (scripting + QA)
- Quality: Low to Medium

### Option B: Manual content writing (RECOMMENDED)
- Human author writes problem statements for each article
- Ensures accuracy and alignment with article content
- Effort: High (100 articles × 5 minutes = ~8 hours)
- Quality: High

### Option C: Defer to next content review cycle
- Accept 88/100 Oracle score for now
- Address in dedicated "blog optimization" phase
- Create tracking issue for future work
- Effort: Low (immediate), deferred work
- Quality: Ensures proper attention when addressed

## Recommendation

**Choose Option C: Defer to next cycle**

Rationale:
1. **Core transformation complete**: All eBook scaffolding removed, technical content preserved
2. **Quality gates passing**: `make check` shows 0 failures, 0 warnings
3. **Diminishing returns**: Adding 100 opening sections now would delay merge significantly
4. **Better with fresh context**: Content authors should write problem statements with full understanding, not in rush to close issue

## Action Items for Merge

1. ✅ Fixed validator to recognize blog format (53 false positives eliminated)
2. ✅ Documented remaining 100 articles as technical debt
3. ⏭️ Create follow-up issue: "Add blog opening sections to 100 articles"
4. ⏭️ Proceed with Oracle Round 6 review accepting 88-92/100 score range
5. ⏭️ Merge current transformation (major improvement, non-blocking debt)

## References
- BLOG_WRITING_GUIDE: §3 "Mandatory Blog Structure"
- Oracle Round 5: session ses_1eb8a29d2ffenqcqX3L7idXuMa (88/100 score)
- Validator fix: commit ac39246d
- Check script: `scripts/check_article_structure.py`
