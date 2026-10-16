"""The border guard agent.

Amazon Bedrock (Nova Pro) plays the guard: it narrates, stays in character, and asks the
traveler questions. It has four tools that represent what the guard can DO. The important
part is that the committing tools (wave_through, raise_alarm) are gated by the
SuspicionGate intervention, which hands the real decision to Strands Decider 2B.

Division of labour:
    Bedrock LLM     -> language: persona, narration, follow up questions (system two)
    Decider 2B      -> the ruling: suspicion, grounding, reaction, with confidence (system one)

The agent never decides on its own whether to trust the traveler. The calibrated model does.
"""

from __future__ import annotations

from typing import Any

from strands import Agent
from strands.models import BedrockModel

GUARD_SYSTEM_PROMPT = """\
You are Sergeant Vance, a border checkpoint guard. You are fair but hard to fool.

Your job: decide whether to let the traveler through. Stay fully in character. Keep each
reply to two or three sentences. Speak only as the guard, never break character, never
mention models, tools, or probabilities.

You have these tools:
- ask_traveler: ask the traveler a direct question. Use this to probe their story.
- demand_document: ask to see their papers or proof of their claim.
- wave_through: let the traveler pass. Use only when you are satisfied.
- raise_alarm: call for backup. Use only for a real threat.

Rules of play:
- You cannot see inside the traveler's head. Judge only what they say.
- If an intervention tells you to hold off or ask more, obey it: ask another question,
  do not force the traveler through.
- When you are satisfied the story holds up, call wave_through.
- Open the scene with a short, firm greeting and your first question.
"""


def build_guard_agent(interventions: list[Any], region: str = "us-east-1",
                      model_id: str = "us.amazon.nova-pro-v1:0") -> Agent:
    """Create the guard agent on Bedrock with the given interventions attached.

    Tools are defined as closures that simply report the guard's intended action back to
    the game loop through the agent's shared state. The SuspicionGate runs before the
    committing tools and can cancel or redirect them.
    """
    model = BedrockModel(model_id=model_id, region_name=region, temperature=0.7)

    from strands import tool

    @tool
    def ask_traveler(question: str) -> str:
        """Ask the traveler a direct question. Returns a note that the question was asked."""
        return f"You asked: {question}"

    @tool
    def demand_document(reason: str) -> str:
        """Ask the traveler to present papers or proof. reason explains why."""
        return f"You demanded documents because: {reason}"

    @tool
    def wave_through(note: str) -> str:
        """Let the traveler pass the checkpoint. Only call when satisfied."""
        return "WAVE_THROUGH"

    @tool
    def raise_alarm(note: str) -> str:
        """Call for backup. Only for a genuine threat."""
        return "RAISE_ALARM"

    agent = Agent(
        model=model,
        system_prompt=GUARD_SYSTEM_PROMPT,
        tools=[ask_traveler, demand_document, wave_through, raise_alarm],
        interventions=interventions,
    )
    return agent


# The committing tools the SuspicionGate guards. Reading tools (ask, demand) are free.
ACT_TOOLS = {"wave_through", "raise_alarm"}
