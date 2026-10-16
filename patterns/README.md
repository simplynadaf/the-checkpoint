# Reusable decision pattern: the SuspicionGate

A drop-in Strands intervention that hands a tool-call decision to Strands Decider 2B
instead of an LLM. Copy `suspicion_gate.py` into your own agent and wire it in. This is
the reusable asset for the Agent Experience Hackathon.

Pattern tags: `#strands-decider-2b`, `#policy` (classify how to react) and `#guardrails`
(ground the arguments).

## The idea in one line

Put a small, calibrated decision model in front of your agent's committing tools, so a
cheap call with a real confidence number decides whether to proceed, probe, or block,
in a place where a second LLM call would be too slow and too expensive to live.

## The typed questions

The gate asks Decider up to three questions about one state, in a single call:

```python
from app.decider_client import choice, noul, score

questions = {
    "suspicion": score(
        "How suspicious is the person's behaviour and story?",
        ["calm and ordinary", "slightly off", "clearly suspicious", "alarming threat"],
    ),
    "grounded": noul(
        "Is the action the agent wants to take justified by what the person actually said?",
        true="every part of the action traces to something the person stated",
        false="the action assumes facts the person never provided",
    ),
    "reaction": choice(
        "What should happen next?",
        {
            "allow": "the story holds up, let the action proceed",
            "probe": "something is unclear, ask one more question first",
            "block": "this is a threat or clearly unjustified, stop it",
        },
    ),
}
```

Notice every question carries criteria. A bare question gives a mushy spread; explicit
`true`/`false` text and per-option descriptions give the calibrated model a clean
boundary. This is the single biggest lever on answer quality.

## The wiring

```python
from strands import Agent
from app.decider_client import DeciderClient
from patterns.suspicion_gate import SuspicionGate

decider = DeciderClient("http://127.0.0.1:8000")  # a running `strands-decider serve`

gate = SuspicionGate(
    decider,
    act_tools={"issue_refund", "close_account"},      # only gate committing tools
    get_state=lambda event: build_state(event),       # what the model reads
    alarm_threshold=0.70,
    grounded_threshold=0.50,
    min_confidence=0.45,
)

agent = Agent(tools=[...], interventions=[gate])
```

The gate runs on `before_tool_call`. It returns one typed action:

- `Proceed` when the model is confident and the action is grounded
- `Guide` when the action is not grounded, or confidence is low, with feedback that sends
  the turn back to the agent so it asks a question instead of committing
- `Deny` when a hard stop condition is met (high suspicion or an explicit block)

## How to adapt it to your own agent

1. Decide which tools are committing or irreversible. Pass their names as `act_tools`.
   Read-only tools pass straight through, no model call.
2. Write `get_state(event)`: return the text or JSON the model should read. Usually the
   user's request plus the tool the agent wants to call.
3. Keep the default `questions` for a trust decision, or pass your own set for a different
   domain. The three question types cover most decisions: `noul` for yes or no, `choice`
   for one of N, `score` for a rubric.
4. Tune the thresholds. The gate exposes `last_decision` so a UI can read the latest
   calibrated numbers (this project uses it to drive the suspicion gauge).

## Why a decision model here and not an LLM

- One forward pass, no token generation, so it is cheap enough to sit on every tool call.
- A calibrated confidence on every answer, which frontier LLM inference APIs do not give
  you. The gate acts on confident answers and sends everything else back for a human
  question. That is the whole point.
- Several questions about one state cost almost the same as one, because the state is
  read once.

## Files

- `suspicion_gate.py`: the `SuspicionGate(InterventionHandler)` and `default_questions()`.
- `../app/decider_client.py`: the `noul`, `choice`, `score` builders and the HTTP client.
