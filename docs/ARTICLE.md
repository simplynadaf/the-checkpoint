# The guard that cannot be sweet-talked: a game where Strands Decider 2B makes every call

> Builder Center submission for the Agent Experience Hackathon: Strands Decider.
> Tags: `#strands-decider-2b` `#policy`. Cover image: `docs/banner-builder.png` (1200x675, under 2MB).
> Paste everything below the line into the article body.

---

## The problem I wanted to fix

Give a language model a character to play and it will get talked into anything. If you have
ever bolted an LLM onto a game NPC, you have seen it: a player types one confident sentence
and the guard at the gate hands over the key. The model is wonderful at talking and weak at
holding a firm, consistent line. It has no reliable sense of how sure it is.

I wanted to build the opposite. A guard you genuinely have to outwit, where the decision to
trust you is made by something calibrated, not by whatever the chat model felt like saying.

That is exactly what Strands Decider 2B is for.

## What Decider 2B actually is

Decider 2B is a decision model. It does not write text. You hand it a state and a few typed
questions, and it returns a probability for every possible answer in a single forward pass,
with a calibrated confidence on each one. A yes or no, a pick one of N, or a rating on a
rubric. On a GPU it answers in about 115 ms, and asking several questions about the same
state costs almost nothing extra because it reads the state once.

The calibration is the part that matters. When the model says 0.9, it is right about that
often. That gives you a clean rule you cannot get from a frontier LLM API: act when the
model is confident, and ask a human when it is not.

## The game: The Checkpoint

A night border checkpoint. Amazon Bedrock Nova Pro plays Sergeant Vance, who narrates and
asks questions. You are the traveler, trying to talk your way through. The twist is that
Vance never decides anything. Decider 2B does.

Each turn, the engine builds one state out of the scene, everything you have claimed so far,
and your latest line, and asks Decider three typed questions:

- `score`: how suspicious is the traveler, from calm and ordinary to alarming threat
- `noul`: does the latest statement agree with the earlier claims
- `choice`: wave them through, press for detail, demand a document, or raise the alarm

The suspicion gauge on screen is not decoration. It is the probability coming straight out
of the model. Watch it climb as your story stops adding up.

## The decision, in code

```python
from app.decider_client import choice, noul, score

questions = {
    "suspicion": score(
        "How suspicious is the traveler's behaviour and story?",
        ["calm and ordinary", "slightly off", "clearly suspicious", "alarming threat"],
    ),
    "consistent": noul(
        "Does the latest statement agree with the claims made earlier?",
        true="it fits the earlier claims with no contradiction",
        false="it contradicts or cannot be true alongside an earlier claim",
    ),
    "reaction": choice(
        "How should the guard respond right now?",
        {
            "wave_through": "the story holds, let them pass",
            "press_for_detail": "ask one sharper question",
            "demand_document": "ask to see papers",
            "raise_alarm": "treat the traveler as a threat",
        },
    ),
}

result = decider.decide(state, questions)   # one call, three calibrated answers
```

One detail did more for quality than anything else: the criteria. A bare question like
"should a human handle this" gave a mushy spread where nothing was clearly anything. Adding
explicit true and false descriptions, and a one line description per choice option, gave the
model a clean boundary. If you take one practical thing from this, make it that.

## The reusable pattern: SuspicionGate

The decision is wired in as a Strands intervention, so it sits in front of the guard's
committing tools. This is the piece you can lift into your own agent.

```python
from strands import Agent
from patterns.suspicion_gate import SuspicionGate

gate = SuspicionGate(
    decider,
    act_tools={"issue_refund", "close_account"},   # only gate the committing tools
    get_state=lambda event: build_state(event),
    alarm_threshold=0.70,
    grounded_threshold=0.50,
    min_confidence=0.45,
)
agent = Agent(tools=[...], interventions=[gate])
```

It runs on `before_tool_call` and returns one typed action. `Proceed` when the model is
confident and the action is grounded in what the user actually said. `Guide` to hand the
turn back with feedback when it is not grounded or confidence is low, so the agent asks a
question instead of committing. `Deny` for a hard stop. Swap in your own questions and it
works for refund approvals, posting guardrails, or anything where a cheap calibrated call
beats a second LLM call.

## What I learned

I ran this on a CPU only box with no GPU. Two honest findings.

First, latency. On CPU a three question call took about 11 seconds warm. On a GPU the same
model is around 115 ms. Rather than hide the CPU pause I leaned into it: the delay became
the guard studying your papers, which actually fits the scene. For a real time game you
would serve Decider on a GPU and it is instant.

Second, where the signal lives. An honest traveler cleared on turn one with low suspicion
and a confident wave through. A liar's reaction confidence collapsed as the contradictions
piled up, from 0.63 to 0.29 to 0.17, and the suspicion score climbed. Interestingly the raw
`consistent` yes or no was softer than I expected on subtle contradictions at this model
size. The strong, reliable signals were the suspicion score and the confidence collapse. I
would rather report that honestly than pretend the model is magic. It is a 2B experimental
model, and knowing which of its signals to trust is the actual skill.

## Why a decision model earns its place here

You could ask a second LLM to judge each turn. You should not. A decision model is one
forward pass with no generation, so it is cheap enough to sit on every single turn. It gives
you a calibrated confidence, which is the entire mechanic of the game. And it answers three
questions about one state for nearly the price of one. That combination is what makes a
guard you cannot sweet-talk feel fast and fair at the same time.

Bedrock writes the words. Decider 2B makes the call.

## Try it

Code, the reusable pattern, and a two minute narrated demo are in the repo. There is also a
zero-setup live replay you can open right now, built from real recorded model output.

- Live demo (no setup): https://simplynadaf.github.io/the-checkpoint/
- Repo (source + the SuspicionGate pattern): https://github.com/simplynadaf/the-checkpoint
- Demo video: [add your upload link here]

Clone it, start the Decider server, start the web game, and see how long it takes you to get
past Sergeant Vance.

---

*Built by Sarvar Nadaf, Cloud Architect working in Cloud, AI Infrastructure, and DevOps.*
*[Portfolio](https://sarvarnadaf.com) · [GitHub](https://github.com/simplynadaf) · [LinkedIn](https://www.linkedin.com/in/sarvar04/)*
