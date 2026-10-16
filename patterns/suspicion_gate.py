"""SuspicionGate: a reusable Strands intervention backed by Strands Decider 2B.

This is the reusable decision pattern. Drop it into any Strands agent to gate tool calls
on a small, calibrated decision model instead of an LLM. The gate reads the current
situation plus the tool the model wants to run, asks Decider a short set of typed
questions, and converts the calibrated answers into one typed intervention action:

    Proceed  -> the model is confident and allowed, let the tool run
    Guide    -> not grounded or not confident, hand the turn back with feedback
    Deny     -> a hard stop condition was met

Why a decision model and not another LLM call here: Decider answers in one forward pass,
returns a calibrated confidence on every answer, and can ask several questions about the
same state nearly for free. That makes it cheap enough to sit in front of every tool call,
a place a second LLM call would be too slow and too expensive to live.

Pattern tag: #policy (classify how to react) and #guardrails (ground the arguments).

Usage:

    from strands import Agent
    from app.decider_client import DeciderClient
    from patterns.suspicion_gate import SuspicionGate

    decider = DeciderClient("http://127.0.0.1:8000")
    gate = SuspicionGate(
        decider,
        act_tools={"wave_through", "raise_alarm", "let_pass"},
        get_state=lambda event: build_state(event),  # you decide what Decider sees
        alarm_threshold=0.70,
    )
    agent = Agent(tools=[...], interventions=[gate])

The gate is deliberately generic: you supply the set of tools to guard and a function
that turns an intervention event into the Decider `state`. The question set below is the
default for a trust/suspicion decision, but you can pass your own `questions` to reuse the
same wiring for any domain (refund approval, content posting, data deletion, and so on).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from strands.interventions import Deny, Guide, InterventionHandler, Proceed

from app.decider_client import DeciderClient, choice, noul, score


def default_questions() -> dict[str, Any]:
    """The default trust decision: how suspicious, is it grounded, what to do.

    Criteria are included on purpose. A bare question gives a mushy spread; explicit
    true/false and per-option descriptions give the calibrated model a clean boundary.
    """
    return {
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


class SuspicionGate(InterventionHandler):
    """Gate tool calls on a Strands Decider decision with calibrated confidence.

    Args:
        decider: a DeciderClient pointing at a running Strands Decider server.
        act_tools: names of tools that commit an irreversible or high-trust action. Only
            these are gated; read-only tools pass straight through.
        get_state: a function mapping the intervention event to the Decider `state`
            (text or JSON). This is what the model reads to make its call.
        questions: the typed question set. Defaults to default_questions().
        alarm_threshold: suspicion (expected level, normalised 0..1) at or above which the
            gate blocks outright.
        grounded_threshold: minimum P(grounded) required to let an action through.
        min_confidence: minimum choice confidence to act on the model's reaction; below
            this the gate asks the agent to probe instead of committing.
        on_block: optional text used when blocking.
    """

    name = "suspicion-gate"

    def __init__(
        self,
        decider: DeciderClient,
        act_tools: set[str],
        get_state: Callable[[Any], Any],
        questions: dict[str, Any] | None = None,
        alarm_threshold: float = 0.70,
        grounded_threshold: float = 0.50,
        min_confidence: float = 0.45,
        on_block: str = "Blocked: the story does not hold up. A supervisor must review this.",
    ) -> None:
        self.decider = decider
        self.act_tools = act_tools
        self.get_state = get_state
        self.questions = questions or default_questions()
        self.alarm_threshold = alarm_threshold
        self.grounded_threshold = grounded_threshold
        self.min_confidence = min_confidence
        self.on_block = on_block
        # Exposed so a UI can read the latest decision (the suspicion gauge).
        self.last_decision: dict[str, Any] | None = None

    def before_tool_call(self, event: Any):
        tool_name = _tool_name(event)
        if tool_name not in self.act_tools:
            return Proceed()

        state = self.get_state(event)
        result = self.decider.decide(state, self.questions)

        # Normalise the score to 0..1 over its rubric so thresholds are rubric independent.
        levels = max(len(self.questions["suspicion"]["criteria"]) - 1, 1)
        suspicion = result.score("suspicion") / levels
        grounded = result.noul("grounded")
        reaction, confidence = result.choice("reaction")

        self.last_decision = {
            "tool": tool_name,
            "suspicion": suspicion,
            "grounded": grounded,
            "reaction": reaction,
            "confidence": confidence,
            "latency_ms": result.latency_ms,
            "raw": result.answers,
        }

        # Hard stop: clearly a threat.
        if suspicion >= self.alarm_threshold or reaction == "block":
            return Deny(reason=self.on_block)

        # Not grounded: the action assumes things the person never said. Send it back.
        if grounded < self.grounded_threshold:
            return Guide(
                feedback=(
                    "Do not take this action yet. The person has not actually justified it. "
                    "Ask them a direct question to fill the gap before acting."
                )
            )

        # Unsure: let the agent probe rather than commit on a low-confidence call.
        if confidence < self.min_confidence or reaction == "probe":
            return Guide(
                feedback=(
                    "Hold off on the action. Something is unclear. Ask one sharp follow up "
                    "question, then decide."
                )
            )

        # Confident and grounded: allow.
        return Proceed()


def _tool_name(event: Any) -> str:
    """Read the tool name from a BeforeToolCallEvent across SDK shapes."""
    tool_use = getattr(event, "tool_use", None)
    if isinstance(tool_use, dict):
        return tool_use.get("name", "")
    if tool_use is not None:
        return getattr(tool_use, "name", "")
    return getattr(event, "name", "")
