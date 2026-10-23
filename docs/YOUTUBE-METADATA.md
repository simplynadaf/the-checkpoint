# YouTube Metadata — The Checkpoint (Strands Decider 2B)

Video file: `docs/the-checkpoint-full.mp4` (1080p, 1:29, intro + gameplay + closing card) — recommended upload.
Alt cuts: `docs/the-checkpoint-smooth.mp4` (1:06, gameplay only), `docs/the-checkpoint-4k.mp4` (2:14, 4K).
Thumbnail: `docs/youtube-thumbnail.png` (1280x720)
Visibility for the hackathon: Unlisted is fine (must be publicly reachable by link).

---

## TITLE (pick one)

**A/B option A — SEO-optimized, keyword-front-loaded (recommended):**
```
Strands Decider 2B: I Built an AI Agent That Can't Be Fooled (AWS Bedrock)
```

**A/B option B — curiosity/first-person:**
```
This AI border guard refuses to be sweet-talked 🛂 (AWS Strands Decider 2B)
```

Why A: keyword "Strands Decider 2B" is first (exact-match search is real and growing, and
existing content is mostly setup tutorials, so the "AI agent that can't be fooled" hook is
the gap). Names AWS Bedrock for ecosystem search. Under 70 chars so it is not truncated.

---

## DESCRIPTION

```
🛂 Give a language model a character to play and players talk it into anything. One clever sentence and the AI guard hands over the key. So I built the opposite: a border guard you genuinely have to outwit.

The twist 👉 the guard never decides anything. Amazon Bedrock (Nova Pro) speaks the words. Strands Decider 2B makes every trust call, with a calibrated confidence on each one. The suspicion meter you watch IS that number.

🧠 Strands Decider 2B is a small, open decision model from AWS. It does not write text. It reads a situation and answers typed questions (a score, a yes/no, a pick-one-of-N), each with a calibrated confidence, in ~115ms. Pair it with Bedrock for the talking and you get a guardrail cheap enough to run on every single turn.

In this build (The Checkpoint) Decider 2B answers three questions per turn:
🔸 How suspicious is the traveler? (score)
🔸 Is the new statement consistent with earlier claims? (yes/no)
🔸 How should the guard react: wave through, press, demand papers, or raise the alarm? (choice)

Lie and contradict yourself, and the model's own confidence collapses while the suspicion meter climbs. Nobody wrote that rule. That is the calibration doing the work.

The reusable piece 🧩 is SuspicionGate: a drop-in Strands intervention you can put in front of any agent's committing tools (refunds, deletes, posts). Point it at your tools, swap in your own questions, and a cheap calibrated call decides proceed / probe / block.

🏷️ Decision pattern: Policy (also demonstrates Guardrails)
⚡ Bedrock writes the words. Decider 2B makes the call.

Built for the AWS Agent Experience Hackathon: Strands Decider.

━━━━━━━━━━━━━━━━━━━━━━
⏱️ CHAPTERS
━━━━━━━━━━━━━━━━━━━━━━
0:00 The problem: AI NPCs get talked into anything
0:18 What Strands Decider 2B actually is
0:30 Honest run: cleared with high confidence
0:48 Lying run: the confidence collapses
1:14 Bedrock writes the words, Decider makes the call

━━━━━━━━━━━━━━━━━━━━━━
🔗 LINKS
━━━━━━━━━━━━━━━━━━━━━━
▶️ Live demo (zero setup): https://simplynadaf.github.io/the-checkpoint/
💻 Code + reusable pattern: https://github.com/simplynadaf/the-checkpoint
🧠 Strands Decider 2B: https://strandsagents.com/blog/introducing-strands-decider/
☁️ Amazon Bedrock: https://aws.amazon.com/bedrock/

━━━━━━━━━━━━━━━━━━━━━━
🙋 ABOUT ME
━━━━━━━━━━━━━━━━━━━━━━
Built by Sarvar Nadaf, Cloud Architect working in Cloud, AI Infrastructure, and DevOps.
🌐 Portfolio: https://sarvarnadaf.com
🐙 GitHub: https://github.com/simplynadaf
💼 LinkedIn: https://www.linkedin.com/in/sarvar04/

#StrandsDecider2B #AWS #AmazonBedrock #AIagents #AgentExperienceHackathon
```

---

## TAGS (copy-paste, comma-separated)

```
strands decider 2b, strands decider, strands agents, aws, amazon bedrock, bedrock nova pro, ai agents, agentic ai, decision model, ai guardrails, llm guardrails, agent experience hackathon, aws hackathon, ai border guard game, calibrated confidence, policy decision pattern, suspicion gate, ai npc, python ai agent, aws ai, nova pro, small language model, decision making ai, ai agent tutorial, sarvar nadaf
```

---

## PINNED COMMENT (post after upload)

```
🛂 Try it yourself (no setup): https://simplynadaf.github.io/the-checkpoint/
💻 Code + the reusable SuspicionGate pattern: https://github.com/simplynadaf/the-checkpoint
How long did it take you to get past Sergeant Vance? Drop your best line below 👇
```

---

## UPLOAD SETTINGS CHECKLIST
- [ ] Category: Science & Technology
- [ ] Thumbnail: upload `docs/youtube-thumbnail.png`
- [ ] Visibility: Unlisted (public link works for the hackathon) or Public
- [ ] "Altered/synthetic content": the voiceover is AI-generated (Amazon Polly). If YouTube
      asks about synthetic voice, disclose it. The footage is a real screen recording.
- [ ] Add to a playlist if you have an AWS/agents one
- [ ] Paste the chapters exactly as above (first must be 0:00, each >= 10s) so YouTube shows them
