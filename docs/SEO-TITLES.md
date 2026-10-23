# SEO & Titles — The Checkpoint (Strands Decider 2B)

Keyword research done via live web search on 2026-10-23. Bands/evidence only, no fabricated volumes.

## Keyword findings (what people actually search + the gap)

- **Exact high-value term:** `Strands Decider 2B` (AWS released it Oct 1, 2026). Exact-match
  searches are real and growing. Front-load this in every title.
- **Existing content (the competition) is almost all SETUP/TUTORIAL:** "running locally",
  "WSL2 guide", "deploy on SageMaker", "local setup and testing". Evidence: dev.to +
  builder.aws.com results all skew "how to install/run".
- **The GAP (our differentiator):** nobody owns the **guardrail / policy / "can't be
  talked into anything"** angle. There is one AWS "role-playing game example", so a plain
  "game" title would blend in. Lead with the guardrail value, not the word "game".
- **Recurring co-keywords:** decision model, calibrated confidence, agentic AI, routing,
  guardrails, tool call, escalation, overconfidence.
- **Citable proof for the problem (used in the Dev.to piece):** arXiv 2608.27167 (Jul 2026),
  LLM agent commitment rises 6.5% -> 54.0% when the input looks authoritative. Stack
  Overflow production-agents field guide (Oct 2026): shrink the model's job to the smallest
  decision, wrap it in deterministic machinery.

## Final titles (keyword front-loaded)

### YouTube (search + curiosity)
```
Strands Decider 2B: I Built an AI Agent That Can't Be Fooled (AWS Bedrock)
```
- Keyword first, concrete hook, under 70 chars, names AWS Bedrock for the ecosystem search.

### Dev.to (distinct angle: the guardrail / problem framing)
```
Strands Decider 2B: the cheap guardrail that stops your AI agent getting talked into anything
```
- Keyword first, targets the open "guardrail" gap, mirrors the searched pain ("talked into").

### Builder Center (hackathon submission)
```
Strands Decider 2B: the AI border guard that cannot be sweet-talked
```
- Keyword first, keeps the memorable hook for the human judges.

## Distinct-angle + canonical (POSSE, per article-writeup-guide)

The two articles must NOT read as duplicates (protects SEO and the hackathon originality score):
- **Builder Center** = the hackathon submission. Narrative: the game, the decision, what I
  learned, the rubric story. This is the primary/owned submission.
- **Dev.to** = the practitioner angle. Narrative: "LLM agents get talked into anything, here
  is a cheap calibrated guardrail", opens with the arXiv stat and the Stack Overflow guide,
  the game is the proof not the subject.
- **Canonical:** when syndicating the Dev.to post, set `canonical_url` to the owned copy
  (sarvarnadaf.com post) once it exists, or leave blank if Dev.to is the only web home.
  Do NOT canonical the Dev.to post to the Builder Center post (different platform intent).

## Tags
- YouTube: see YOUTUBE-METADATA.md (comma-separated list, keyword-rich).
- Dev.to: `aws, ai, agents, python` (4 tags, one clear topic cluster, per the skill).
- Builder Center: `#strands-decider-2b` + `#policy` (required by hackathon rules).

## Live demo cost note (verified 2026-10-23)
The public live demo (https://simplynadaf.github.io/the-checkpoint/) is a STATIC GitHub
Pages page. Verified by grep: no fetch, no API call, no Bedrock/Decider endpoint. It embeds
recorded model output (`const DATA`). It makes ZERO AWS calls and costs nothing to keep live.
The interactive Bedrock+Decider app only runs locally, never behind the public URL.
