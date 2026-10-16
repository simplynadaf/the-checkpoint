"""The Checkpoint game engine.

A turn works like this:
  1. The traveler (player) says something.
  2. Strands Decider 2B reads the whole situation and returns, in one calibrated call:
       - suspicion  (score)  how suspicious the story is now
       - consistent (noul)   does the new line agree with everything claimed so far
       - reaction   (choice) wave_through / press / demand_document / raise_alarm
  3. The engine updates a running suspicion meter from those calibrated numbers and
     decides the outcome:
       - confident low suspicion and consistent  -> the guard can wave them through
       - caught in a contradiction                -> suspicion jumps
       - confident high suspicion                 -> alarm
       - anything unsure                          -> the guard presses for more
  4. A Bedrock LLM guard turns that ruling into in-character dialogue.

The confidence number is the game. The meter the player watches is literally the
calibrated probability coming out of the decision model.

This engine can run standalone (Decider only, fast, deterministic to reason about) or be
paired with the Bedrock guard agent for the narration. The web UI uses this engine
directly so the suspicion gauge reflects real model output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.decider_client import DeciderClient, choice, noul, score

SUSPICION_LEVELS = ["calm and ordinary", "slightly off", "clearly suspicious", "alarming threat"]

REACTIONS = {
    "wave_through": "the story holds, let them pass",
    "press_for_detail": "ask one sharper question",
    "demand_document": "ask to see papers or proof",
    "raise_alarm": "treat the traveler as a threat",
}


def turn_questions() -> dict[str, Any]:
    """The three typed questions Decider answers each turn."""
    return {
        "suspicion": score(
            "Read the traveler's claims so far and their latest statement. How suspicious "
            "or deceptive does the traveler seem?",
            SUSPICION_LEVELS,
        ),
        "consistent": noul(
            "Does the traveler's latest statement agree with the claims they made earlier "
            "in this same conversation?",
            true="the latest statement fits their earlier claims with no contradiction",
            false="the latest statement contradicts or cannot be true alongside an earlier claim",
        ),
        "reaction": choice("How should the guard respond right now?", REACTIONS),
    }


@dataclass
class TurnResult:
    suspicion: float          # 0..1 normalised over the rubric
    consistent: float         # P(consistent)
    reaction: str             # chosen reaction key
    reaction_confidence: float
    meter: float              # running suspicion meter 0..1 after this turn
    outcome: str              # "continue" | "passed" | "caught" | "alarm"
    latency_ms: float
    raw: dict[str, Any]


@dataclass
class Game:
    """Holds the running state and drives turns against a DeciderClient."""

    decider: DeciderClient
    scene: str = (
        "A night border checkpoint. A lone traveler approaches the booth. "
        "Sergeant Vance must decide whether to let them through."
    )
    claims: list[str] = field(default_factory=list)   # everything the traveler has said
    meter: float = 0.15                                # starting suspicion
    turns: int = 0
    # Tuning thresholds (also the knobs the article explains).
    pass_meter: float = 0.30
    alarm_meter: float = 0.80
    consistent_floor: float = 0.45
    confident: float = 0.45

    def _state(self, latest: str) -> dict[str, Any]:
        return {
            "scene": self.scene,
            "traveler_claims_so_far": self.claims or ["(nothing yet)"],
            "traveler_latest_statement": latest,
            "current_suspicion_meter": round(self.meter, 2),
        }

    def play_turn(self, traveler_line: str) -> TurnResult:
        """Run one turn: ask Decider, update the meter, decide the outcome."""
        self.turns += 1
        state = self._state(traveler_line)
        result = self.decider.decide(state, turn_questions())

        levels = len(SUSPICION_LEVELS) - 1
        suspicion = result.score("suspicion") / levels
        consistent = result.noul("consistent")
        reaction, conf = result.choice("reaction")

        # Record the claim only after the model has judged it against the prior ones.
        self.claims.append(traveler_line)

        # Update the running meter. A contradiction (low consistency) pushes it up hard;
        # a calm consistent answer lets it drift down. The model's own suspicion score
        # pulls the meter toward itself. All numbers come from the calibrated model.
        contradiction_push = (1.0 - consistent) * 1.0
        self.meter = _clamp(0.45 * self.meter + 0.35 * suspicion + contradiction_push - 0.04)

        outcome = "continue"
        if reaction == "raise_alarm" and conf >= self.confident:
            outcome = "alarm"
        elif self.meter >= self.alarm_meter:
            outcome = "alarm"
        elif consistent < self.consistent_floor:
            outcome = "caught"       # caught in a contradiction, guard presses hard
        elif reaction == "wave_through" and conf >= self.confident and self.meter <= self.pass_meter:
            outcome = "passed"

        return TurnResult(
            suspicion=suspicion,
            consistent=consistent,
            reaction=reaction,
            reaction_confidence=conf,
            meter=self.meter,
            outcome=outcome,
            latency_ms=result.latency_ms,
            raw=result.answers,
        )


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))
