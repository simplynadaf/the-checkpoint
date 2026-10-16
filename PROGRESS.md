# Build Progress: The Checkpoint

Single source of truth for build status. Updated continuously.

Project: a social-stealth agent game. A Bedrock Nova Pro LLM plays a border guard; the
player talks their way through. Strands Decider 2B is the guard's instinct, a calibrated
suspicion meter that decides, with confidence, whether to wave the traveler through,
press for detail, demand a document, or raise the alarm. The confidence number is the
suspicion gauge.

- Decision pattern tags: #strands-decider-2b + #policy (also demonstrates #guardrails)
- Reusable asset: a drop-in Strands InterventionHandler (patterns/suspicion_gate.py)

## Status legend
[ ] todo   [~] in progress   [x] done   [!] blocked

## Steps

- [x] 0. Research + validate rules, model API, intervention contract
- [x] 1. Environment: Python 3.11 venv, install strands-agents + strands-decider
- [x] 2. Confirm model API/schema (noul/choice/score) from source
- [x] 3. Download model weights and start decider server (CPU + 8G swap). VERIFIED answering 3-question calls (~20s/call on CPU).
- [x] 4. decider_client.py: Python client for POST /v1/systemone (+ retry/timeout)
- [x] 5. suspicion_gate.py: reusable InterventionHandler (the asset) + patterns/README
- [x] 6. guard_agent.py: Strands Agent on Bedrock Nova Pro, guard tools
- [x] 7. game.py: turn loop, player-claims state, win/lose. VALIDATED: honest->passed, liar->meter climbs + confidence collapses
- [x] 8. Tune question wording/criteria for a clean suspicion spread
- [x] 9. Web UI (FastAPI + animated suspicion gauge) using frontend skills. VERIFIED end to end: /api/new + /api/say return Bedrock narration + Decider ruling.
- [x] 10. Tests: client, gate logic, schema validation. 8/8 offline unit tests pass; scripted live scenarios validated.
- [x] 11. README (styled like simplynadaf/ai-agent-observability-aws), no em dashes. Verified clean.
- [x] 12. Article draft (docs/ARTICLE.md) per challenge rules
- [x] 13. Demo video plan (docs/DEMO_SCRIPT.md), <3 min shot list
- [x] 14. Create GitHub repo (via gh, token auth, no password), push, verify. Live: https://github.com/simplynadaf/the-checkpoint
- [x] 15. Final validation pass end to end. UI 200, servers up, screenshot captured, repo verified, topics set.

## DONE. All 15 steps complete. Repo: https://github.com/simplynadaf/the-checkpoint

## Environment facts (verified on this box)
- Host: CPU only (no CUDA). Decider inference will be seconds per call -> designed as a
  narrative "the guard studies you" beat.
- Python 3.11.16 venv at ~/agent-experiance/.venv
- strands-agents 1.61.1, strands-decider 0.1.0, torch 2.14.1, boto3 1.43.114
- AWS account 175662053988 (user: server); Bedrock us-east-1 has amazon.nova-pro-v1:0,
  amazon.nova-2-lite-v1:0, anthropic.claude-sonnet-4-6, anthropic.claude-haiku-4-5
- Model: StrandsAgents/strands-decider-2B-qwen3.5-v1-2610, served at 127.0.0.1:8000

## Model API contract (from strands_decider/schema.py)
- POST /v1/systemone  {state, questions:{name:{type,instructions,criteria?}}, model?}
- noul:   criteria keys subset of {true,false}; returns {noul: P(true)}
- choice: criteria {option: desc} (>=2); returns {choice, probabilities{}, confidence}
- score:  criteria ascending list[str] (2..10 levels); returns {score: expected_level, legend{}}

## Decision log
- Chose "The Checkpoint" (border guard) theme: simplest to understand, demos cleanly,
  grounding check (cover-story consistency) fits naturally.
- Primary tag #policy (classify how the guard should react); shows #guardrails too.
- CPU latency reframed as a feature: the pause becomes dramatic tension.
- Server HTTP integration (not python import) because the package exposes serve/ask only.
- OOM on first server start: box has 7.8G RAM, no swap; fp32 CPU load needs ~9G. Fixed by
  adding an 8G swap file so the load peak spills to disk; resident settles ~4G. Verified.
- Server persistence: setsid+nohup via scripts/run_decider.sh with a PID file; plain
  background jobs did not survive the tool shell exiting.
- Measured: a 3-question call takes ~20s on CPU (input 235 tokens). Game makes ONE
  decider call per turn and shows a "the guard studies you" beat to make latency feel
  intentional. Keep prompts short to cut latency.
