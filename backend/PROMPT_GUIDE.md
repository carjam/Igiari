# Prompt Engineering Guide

## Quick Start

The system prompt is now stored in **`prompt_template.txt`** for easy editing without touching the Python code.

## How to Modify the Prompt

1. Edit `backend/prompt_template.txt`
2. Test locally: `python server.py`
3. Commit and push to redeploy

**Note**: The `{TAXONOMY}` placeholder is automatically replaced with the full fallacy taxonomy at runtime.

## Testing Your Changes

### Option 1: Manual Testing
```bash
cd backend
python server.py

# In another terminal:
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"text":"Your test text here"}'
```

### Option 2: Run Eval Script
```bash
cd backend
python run_eval.py
```

This runs 30 test cases and shows precision/recall metrics. Compare before/after scores to measure prompt improvements.

## Structure of the Template

```
[Preamble]
You are a logical fallacy detection system...

[Taxonomy Section]
TAXONOMY OF 136 FALLACIES:
{TAXONOMY}  ← This gets replaced at runtime

[Output Format]
JSON schema specification...

[Calibration Rules]
Guidelines to prevent over-flagging...
```

## Tips for Prompt Tweaking

### Increase Recall (catch more fallacies)
- Adjust confidence thresholds in calibration rules
- Add examples of subtle fallacies
- Emphasize thoroughness

### Increase Precision (reduce false positives)
- Strengthen the "distinguish real fallacies from weak arguments" rule
- Add examples of what is NOT a fallacy
- Emphasize conservative flagging

### Change Output Format
- Modify the JSON schema section
- Update Pydantic models in `server.py` if adding new fields
- Update frontend in `app.js` to handle new fields

### Add Context Awareness
- Add instructions about domain-specific language
- Add guidelines for handling rhetorical devices vs fallacies
- Add examples of acceptable reasoning patterns

## Common Tweaks

**Make it more conservative:**
```
Add to CALIBRATION RULES:
7. **Err on the side of caution.** If uncertain whether something is a fallacy, omit it rather than flag it.
```

**Add domain-specific guidance:**
```
Add after taxonomy:

DOMAIN-SPECIFIC NOTES:
- Political rhetoric: Expect hyperbole, which is not necessarily a fallacy
- Academic arguments: Higher bar for logical rigor
- Casual conversation: More lenient interpretation
```

**Request more detailed explanations:**
```
Change in OUTPUT FORMAT:
"explanation": "2-3 sentences explaining: (1) why this is a fallacy, (2) why the reasoning fails, (3) what would be a valid alternative"
```

## Deployment Notes

Changes to `prompt_template.txt` deploy automatically:
- **Render**: Detects file changes on git push, redeploys backend
- **Takes ~2-3 minutes** for deployment to complete
- **No environment variables needed** for prompt changes
- **Check logs** in Render dashboard if something breaks

## Evaluation Workflow

1. **Baseline**: Run `python run_eval.py` and note current scores
2. **Edit**: Modify `prompt_template.txt`
3. **Test**: Run eval script again
4. **Compare**: Check if precision/recall improved
5. **Deploy**: If satisfied, commit and push

The eval set has 30 cases covering:
- True positives (should catch)
- True negatives (should NOT flag)
- Edge cases (borderline arguments)

## Advanced: Multiple Prompt Versions

Want to A/B test prompts?

```bash
# Create variants
cp prompt_template.txt prompt_v1_conservative.txt
cp prompt_template.txt prompt_v2_aggressive.txt

# Edit each variant

# Test each
python run_eval.py  # uses prompt_template.txt by default

# To test a specific variant, temporarily rename:
mv prompt_template.txt prompt_template_backup.txt
mv prompt_v1_conservative.txt prompt_template.txt
python run_eval.py
# ... restore afterward
```

Or modify `server.py` to accept a prompt variant parameter.

## Troubleshooting

**Server won't start after prompt change:**
- Check for unmatched curly braces (remember `{TAXONOMY}` is replaced)
- Verify file encoding is UTF-8
- Look for syntax issues that break Python's `.replace()` method

**Model returns invalid JSON:**
- Review OUTPUT FORMAT section clarity
- Check if prompt became too long (>100k tokens with taxonomy)
- Try adding more explicit JSON examples

**Scores dropped after prompt change:**
- Compare prompt_template.txt before/after
- Review eval failures: `cat backend/eval_results.json`
- Consider reverting and making smaller, incremental changes

## Questions?

See also:
- `specs/03_architecture.md` - Why Claude Haiku, model choice reasoning
- `backend/TODO_CACHING.md` - Performance optimization ideas
- `docs/DEPLOYMENT_GUIDE.md` - How deployments work
