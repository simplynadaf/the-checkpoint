"""Unit tests that do not require a running model or AWS.

These validate the question builders, the schema shapes, and the game meter logic using a
fake decider. Run:  python -m pytest tests/  (or python -m tests.test_unit)
"""

from __future__ import annotations

from app.decider_client import DeciderResult, choice, noul, score
from app.game import Game, SUSPICION_LEVELS, turn_questions


# ---- question builders ----------------------------------------------------------------

def test_noul_builder_criteria_subset():
    q = noul("Is it true?", true="yes it is", false="no it is not")
    assert q["type"] == "noul"
    assert set(q["criteria"]).issubset({"true", "false"})


def test_choice_builder_requires_two():
    try:
        choice("pick", {"only": "one"})
        raise AssertionError("should have raised")
    except ValueError:
        pass
    q = choice("pick", {"a": "first", "b": "second"})
    assert q["type"] == "choice" and len(q["criteria"]) == 2


def test_score_builder_level_bounds():
    try:
        score("rate", ["only"])
        raise AssertionError("should have raised")
    except ValueError:
        pass
    q = score("rate", ["low", "high"])
    assert q["type"] == "score"


def test_turn_questions_shape():
    q = turn_questions()
    assert set(q) == {"suspicion", "consistent", "reaction"}
    assert q["suspicion"]["type"] == "score"
    assert q["consistent"]["type"] == "noul"
    assert q["reaction"]["type"] == "choice"
    assert len(q["suspicion"]["criteria"]) == len(SUSPICION_LEVELS)


# ---- fake decider to drive the engine deterministically -------------------------------

class FakeDecider:
    """Returns canned answers so we can test the meter and outcome logic offline."""

    def __init__(self, suspicion_idx: float, consistent: float, reaction: str, conf: float):
        self._s = suspicion_idx
        self._c = consistent
        self._r = reaction
        self._conf = conf

    def decide(self, state, questions, retries: int = 2):
        levels = len(SUSPICION_LEVELS)
        probs = {str(i): (1.0 if i == round(self._s) else 0.0) for i in range(levels)}
        answers = {
            "suspicion": {"type": "score", "score": self._s, "legend": {}, "probabilities": probs, "confidence": 0.5},
            "consistent": {"type": "noul", "noul": self._c},
            "reaction": {"type": "choice", "choice": self._r,
                         "probabilities": {self._r: self._conf}, "confidence": self._conf},
        }
        return DeciderResult(answers=answers, latency_ms=1.0, raw=answers)


def test_honest_traveler_passes():
    g = Game(decider=FakeDecider(suspicion_idx=0.2, consistent=0.9, reaction="wave_through", conf=0.8))
    r = g.play_turn("I am just going home.")
    assert r.outcome == "passed"
    assert r.meter <= g.pass_meter


def test_threat_raises_alarm():
    g = Game(decider=FakeDecider(suspicion_idx=3.0, consistent=0.2, reaction="raise_alarm", conf=0.9))
    r = g.play_turn("I will not answer your questions.")
    assert r.outcome == "alarm"


def test_contradiction_is_caught():
    g = Game(decider=FakeDecider(suspicion_idx=1.0, consistent=0.1, reaction="press_for_detail", conf=0.5))
    r = g.play_turn("I have never been here, but I live here.")
    assert r.outcome in {"caught", "alarm"}


def test_claims_are_tracked():
    g = Game(decider=FakeDecider(suspicion_idx=0.5, consistent=0.8, reaction="press_for_detail", conf=0.3))
    g.play_turn("first line")
    g.play_turn("second line")
    assert g.claims == ["first line", "second line"]


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        fn()
        passed += 1
        print(f"  ok  {fn.__name__}")
    print(f"\n{passed}/{len(fns)} tests passed")
