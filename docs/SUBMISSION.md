# Submission checklist: Agent Experience Hackathon (Strands Decider)

Everything the code side needs is done. These are the final human steps to submit.

## Status

| Requirement | Status | Where |
|---|---|---|
| Agent uses Decider 2B for a meaningful decision, paired with Bedrock | DONE | `app/game.py`, `app/guard_agent.py` |
| Written article on Builder Center | DRAFT READY | `docs/ARTICLE.md` (paste in) |
| Public repo with source + reusable decision pattern | DONE | https://github.com/simplynadaf/the-checkpoint, `patterns/suspicion_gate.py` |
| Public live demo (static replay, zero setup) | LIVE | https://simplynadaf.github.io/the-checkpoint/ |
| Public demo video under three minutes | FOOTAGE READY | `docs/the-checkpoint-gameplay.mp4` (2:06) add voiceover from `docs/DEMO_SCRIPT.md` |
| One declared decision pattern | DONE | `#policy` (also demonstrates `#guardrails`) |
| Original agent, not published before | DONE | verified unbuilt |
| Both tags | TO ADD ON SUBMISSION | `#strands-decider-2b` and `#policy` |

## Final steps for you

1. **Video**: `docs/the-checkpoint-gameplay.mp4` is a clean 2 minute 6 second screen capture
   of a cleared honest run and a lying run where suspicion climbs. Record a voiceover over it
   using `docs/DEMO_SCRIPT.md`, or use it as is if a silent captioned cut is acceptable.
   Upload it somewhere public (YouTube unlisted is fine).

2. **Article**: open `docs/ARTICLE.md`, paste into a new Builder Center article, add the repo
   and video links at the end, publish.

3. **Submit**: on the hackathon project page, attach the repo link, the article link, and the
   video link. Add both tags: `#strands-decider-2b` and `#policy`.

## One line pitch for the submission form

An AI border guard you have to outwit. Amazon Bedrock speaks the guard's words, but Strands
Decider 2B makes every trust decision with a calibrated confidence, and that confidence is
the suspicion meter you play against. Ships a reusable SuspicionGate intervention any Strands
agent can drop in front of its committing tools.
