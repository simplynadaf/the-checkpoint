# TODO (later)

Open items to pick up in a future session. Nothing here blocks submission.

## UI polish
- [ ] Fix duplicate guard line: a guard message can repeat if the player sends a new line
      while the previous turn is still "thinking". The input is disabled during the request,
      but the fix is to also guard against double submits and ensure one guard reply per
      resolved turn. File: `ui/static/index.html` (submit handler) and possibly
      `ui/server.py` (dedupe history append). Cosmetic only; the recording still reads well.

## Submission (human steps, tracked in docs/SUBMISSION.md)
- [ ] Add voiceover to docs/the-checkpoint-gameplay.mp4 using docs/DEMO_SCRIPT.md, upload public.
- [ ] Publish docs/ARTICLE.md on Builder Center, add repo + video links.
- [ ] Submit on the hackathon page with tags #strands-decider-2b and #policy.

## Nice to have (optional, raises polish)
- [ ] Short animated GIF of a lying run for the top of the README.
- [ ] Optional GPU serving path for ~115ms decisions (set DECIDER_URL to a GPU host) so a
      live demo is instant.
- [ ] Persist the Decider + UI servers via a systemd user service so they survive reboots.
