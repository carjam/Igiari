---
name: fallacy-detection
description: Detect, classify, and explain logical fallacies in text, transcripts, speeches, debates, arguments, or written content. Use this skill whenever the user asks to "check for logical fallacies," "find flaws in this argument," "analyze this transcript/speech/debate for reasoning errors," "is this argument valid," "spot the manipulation tactics," or wants critical/rhetorical analysis of any persuasive text or speech — even if they don't use the word "fallacy" explicitly. Also use when asked to label, tag, or annotate fallacies in a document for downstream use (e.g., training data, dataset construction, content moderation). Trigger proactively any time the user shares a transcript, speech, op-ed, debate, sales pitch, or argumentative passage and asks for an assessment of its reasoning quality.
---

# Fallacy Detection

A skill for identifying logical fallacies in text — including informal/spoken-register text like audio transcripts — and reporting them in a structured, defensible way.

## When to use this

Use this skill for any task that involves:
- Scanning text/transcripts for logical fallacies or reasoning errors
- Classifying a flagged passage by fallacy type
- Building or labeling training data for a fallacy detector
- Critiquing an argument's validity or rhetorical tactics
- Explaining why a specific statement is (or isn't) fallacious

Do **not** use this skill for general reading comprehension, summarization, or fact-checking (verifying whether a claim is *true*) — fallacy detection is about reasoning *structure*, not factual accuracy. A claim can be false without being fallacious, and an argument can be fallacious while its conclusion happens to be true.

## Reference files

- `references/fallacy_taxonomy.md` — full taxonomy of 136 fallacies (formal + informal), each with definition, abstract logical pattern, a textbook example, and a conversational example. Organized by category with a table of contents. **Read this when you need definitions, examples, or to browse categories.**
- `references/fallacies.json` — the same 136 fallacies as structured data (`name`, `category`, `subcategory`, `aliases`, `definition`, `pattern`, `example_textbook`, `example_conversational`). **Use this when you need to process the taxonomy programmatically** (e.g., writing a script to match against it, exporting to another format, building few-shot prompts).

Don't load the full markdown file into context for every small task — for a quick single-fallacy lookup, grep the JSON or markdown for the name instead of reading the whole file.

## Workflow

1. **Read the input closely, in segments.** For long transcripts, work through it in chunks (e.g., by speaker turn or paragraph) rather than skimming for keywords. Many fallacies (straw man, moving the goalposts, motte-and-bailey) only become visible across multiple turns — track claims across the whole window, not just sentence-by-sentence.

2. **Distinguish real fallacies from merely weak or unwelcome arguments.** Not every bad argument is a *named* fallacy, and rhetorical strategies (e.g., genuinely citing a relevant expert) are not automatically fallacious. Before tagging something, check it actually matches the **pattern**, not just the topic. When uncertain, say so rather than forcing a label — false positives are as costly as misses for downstream training data.

3. **Match against the taxonomy.** Consult `references/fallacy_taxonomy.md` (or the JSON) to confirm the precise name and pattern rather than relying on memory — several fallacies are easily confused (e.g., *hasty generalization* vs. *cherry picking*; *post hoc* vs. *cum hoc*; *straw man* vs. *red herring*; *ad hominem* vs. *circumstantial ad hominem*). Get the right one.

4. **Quote the minimal span that constitutes the fallacy**, not the whole surrounding paragraph. For transcripts, include a timestamp or speaker label if available.

5. **Report using the structured output format below** unless the user has asked for prose commentary instead.

## Output format

Default to this structure for any detection/labeling task (adapt field names to the user's stated schema if they've given one):

```json
{
  "span": "the exact quoted text containing the fallacy",
  "speaker": "optional speaker label / timestamp",
  "fallacy": "canonical name from the taxonomy",
  "category": "Formal | Informal",
  "subcategory": "e.g., Questionable Cause",
  "confidence": "high | medium | low",
  "explanation": "1-2 sentences: why this span matches the fallacy's pattern, in context"
}
```

For conversational/report-style requests instead of structured labeling, lead with the most significant fallacy first, quote the relevant line, name the fallacy, and explain the mismatch between the stated reasoning and what would actually be required to support the conclusion — don't just paste the dictionary definition.

## Calibration notes

- **Confidence matters more than coverage.** A long transcript may contain zero fallacies. Don't manufacture findings to seem thorough.
- **Ambiguous/borderline cases**: many fallacies (appeal to authority, slippery slope, ad hominem) have legitimate non-fallacious forms. Note when a pattern is borderline rather than forcing a binary call.
- **Multi-turn fallacies need the full context window**: if you're only shown a fragment of a transcript, say what additional context would confirm or rule out a suspected fallacy (e.g., straw man requires seeing the original claim being distorted).
- **Don't conflate fallacies with cognitive biases, rhetorical devices, or factual errors.** A misleading statistic is not automatically a fallacy unless it's used in a way that matches one of the taxonomy's patterns.
