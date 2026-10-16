# TODO (later)

Snapshot of what is done and what remains. Nothing in "remaining" blocks the repo being
complete; the required items are human-only submission steps.

## DONE (code + build side, verified)
- [x] Agent using Decider 2B for the decision, paired with Bedrock (app/game.py, app/guard_agent.py)
- [x] Reusable decision pattern: SuspicionGate intervention (patterns/suspicion_gate.py + README)
- [x] Web UI with live suspicion gauge (ui/server.py, ui/static/index.html)
- [x] Tests: 8/8 offline unit tests pass; live scenarios validated
- [x] Gameplay video footage recorded, 2:06, under 3 min (docs/the-checkpoint-gameplay.mp4)
- [x] Article draft (docs/ARTICLE.md)
- [x] Demo script (docs/DEMO_SCRIPT.md)
- [x] README styled like the reference repo, no em dashes
- [x] Public GitHub repo pushed + topics set (https://github.com/simplynadaf/the-checkpoint)
- [x] Submission checklist (docs/SUBMISSION.md)

## REMAINING: required to submit (HUMAN ONLY, I cannot do these)
- [ ] 1. Add a voiceover to docs/the-checkpoint-gameplay.mp4 using docs/DEMO_SCRIPT.md,
         then upload it publicly (YouTube unlisted is fine). Or ship a captioned silent cut.
- [ ] 2. Publish docs/ARTICLE.md as a Builder Center article; add the repo + video links.
- [ ] 3. Submit on the hackathon project page with the repo, article, and video links, and
         both tags: #strands-decider-2b and #policy.

## REMAINING: optional polish (I CAN do these, not blocking)
- [ ] Fix duplicate guard line: a guard message can repeat if the player sends a new line
      while the previous turn is still "thinking". Guard against double submits and ensure
      one guard reply per resolved turn. Files: ui/static/index.html (submit handler),
      ui/server.py (dedupe history). Cosmetic only; the recording still reads well.
- [ ] Short animated GIF of a lying run for the top of the README.
- [ ] Optional GPU serving path for ~115ms decisions (set DECIDER_URL to a GPU host) so a
      live demo is instant instead of the CPU "guard studies you" pause.
- [ ] Persist the Decider + UI servers via a systemd user service so they survive reboots.

## Notes / environment
- This box is CPU only: a Decider call takes ~11 to 20s warm. On a GPU it is ~115ms.
- Decider server needs ~8G RAM; we added an 8G swap file so the fp32 load peak fits.
- Restart servers anytime: `bash scripts/run_decider.sh 8000` and `bash scripts/run_ui.sh 8080`.
