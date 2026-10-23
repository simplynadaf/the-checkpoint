---
title: "Strands Decider 2B: the cheap guardrail that stops your AI agent getting talked into anything"
published: false
description: "LLM agents commit to bad calls when the input sounds confident. I used AWS Strands Decider 2B, a tiny calibrated decision model, to build a guardrail cheap enough to run on every tool call, and proved it with a game."
tags: aws, ai, agents, python
cover_image:
canonical_url:
---

> Built for the AWS Agent Experience Hackathon: Strands Decider. Decision pattern: Policy (also demonstrates Guardrails). Repo, live demo, and a 90 second video are linked at the end.

## The bug nobody wants to talk about

Give an LLM agent a confident-sounding input and it will commit to things it has no business committing to. This is not a vibe, it is measured. A July 2026 paper (arXiv 2608.27167) put twelve frontier models in front of a professional-looking market panel and asked them to call a provably unpredictable outcome. Commitment jumped from 6.5% on the bare question to 54.0% once the input looked authoritative. The evidence was noise. The models acted anyway.

If you have shipped an agent with real tools, you have felt this. A user phrases a request confidently, and the agent issues the refund, closes the account, or runs the destructive tool, because nothing in the loop had a calibrated sense of whether it should. The usual fix is to ask a second LLM to double check. That is slow and expensive, so in practice most agents skip it and hope.

A Stack Overflow field guide on production agents (October 2026) put the real fix well: you get guarantees by shrinking the model's job to the smallest decision that needs judgment, then wrapping that decision in deterministic machinery you can test and gate. The problem has always been that the "small decision" still cost a full LLM call. That is what changed.

---

## Enter Strands Decider 2B

Strands Decider 2B is a small, open decision model AWS released on October 1, 2026. It does not generate text. You hand it a state and a few typed questions, and it returns a probability for every possible answer in one forward pass, each with a calibrated confidence. A yes or no, a pick one of N, or a rating on a rubric. On a GPU it answers in about 115ms.

Two properties make it a different tool from a chat model:

1. It is calibrated. When it says 0.9, it is right about that often. That turns "act when confident, ask a human when not" into a real, tunable threshold instead of a guess.
2. It is cheap. One forward pass, no generation, and several questions about the same state cost almost nothing extra because it reads the state once.

Cheap and calibrated together is what changes the game. A guardrail you can actually afford to run on every single tool call.

---

## Proving it with a game you cannot sweet-talk

Abstract guardrails are hard to feel, so I built something you can play. The Checkpoint is a night border checkpoint. Amazon Bedrock Nova Pro plays Sergeant Vance, who narrates and asks questions. You are the traveler, trying to talk your way through.

The twist: Vance never decides anything. Every turn, the engine builds one state out of the scene, everything you have claimed so far, and your latest line, and hands Decider 2B three typed questions:

- score: how suspicious is the traveler, from calm and ordinary to alarming threat
- yes/no: does the latest statement agree with the earlier claims
- choice: wave them through, press for detail, demand a document, or raise the alarm

The suspicion gauge on screen is not decoration. It is the probability straight out of the model. Lie and contradict yourself, and the model's own confidence collapses while the suspicion climbs. Nobody wrote a rule that says "if they mention a bag, get suspicious." The calibration does the work.

---

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

One detail did more for quality than anything else: the criteria. A bare question like "should a human handle this" gave a mushy spread where nothing was clearly anything. Adding explicit true and false descriptions, and a one line description per choice option, gave the model a clean boundary. If you take one practical thing from this post, make it that.

---

## The reusable piece: SuspicionGate

The decision is wired in as a Strands intervention, so it sits in front of the guard's committing tools. This is the part you lift into your own agent.

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

It runs on before_tool_call and returns one typed action. Proceed when the model is confident and the action is grounded in what the user actually said. Guide to hand the turn back with feedback when it is not grounded or confidence is low, so the agent asks a question instead of committing. Deny for a hard stop. Swap in your own questions and it protects refunds, posting guardrails, deletes, or any irreversible action.

---

## What I learned running it on a CPU

I ran the whole thing on a CPU only box with no GPU. Two honest findings.

First, latency. On CPU a three question call took about 11 seconds warm. On a GPU the same model is around 115ms. Rather than hide the CPU pause I leaned into it: the delay became the guard studying your papers, which fits the scene. For anything real time you serve Decider on a GPU and it is instant.

Second, where the signal lives. An honest traveler cleared on turn one with low suspicion and a confident wave through. A liar's reaction confidence collapsed as the contradictions piled up, from 0.63 to 0.29 to 0.17, and the suspicion score climbed. The raw yes/no consistency check was softer than I expected on subtle contradictions at this model size. The strong, reliable signals were the suspicion score and the confidence collapse. It is a 2B experimental model, and knowing which of its signals to trust is the actual skill.

---

## Why this is worth your time

It is not that a game is impressive. It is that the same four lines protect a real agent. A calibrated decision is one forward pass, so you can run it on every turn and every tool call, which a second LLM judge can never be cheap enough to do. You get a confidence number you can build a threshold on. And one of the three questions checks grounding, so a self-contradicting input gets caught before the agent commits to it.

That is the shift: from "the model sounded confident, so we acted" to "the model was measured as confident and grounded, so we acted, and otherwise we asked."

Bedrock writes the words. Decider 2B makes the call.

---

## Try it

- Live demo, zero setup (static replay, costs nothing to run): https://simplynadaf.github.io/the-checkpoint/
- Code and the reusable SuspicionGate pattern: https://github.com/simplynadaf/the-checkpoint
- 90 second walkthrough: https://youtu.be/0QMQK89Cj5E

Clone it, start the Decider server, start the web game, and see how long it takes you to get past Sergeant Vance.

---

*Built by Sarvar Nadaf, Cloud Architect working in Cloud, AI Infrastructure, and DevOps.*
*[Portfolio](https://sarvarnadaf.com) | [GitHub](https://github.com/simplynadaf) | [LinkedIn](https://www.linkedin.com/in/sarvar04/) | [Dev.to](https://dev.to/sarvar_04)*
