"""Client for a running Strands Decider server (POST /v1/systemone).

The Decider model does not generate text. It reads a state and a set of typed questions
and returns one calibrated answer per question in a single forward pass. This client is a
thin, dependency-light wrapper over that HTTP contract, with sensible timeouts and a
retry while a server is still loading its weights.

Question types (from strands_decider/schema.py):
    noul   -> yes/no      -> {"noul": P(true)}
    choice -> one of N    -> {"choice": name, "probabilities": {...}, "confidence": c}
    score  -> rubric 0..L -> {"score": expected_level, "legend": {...}}

Example:
    client = DeciderClient("http://127.0.0.1:8000")
    answers = client.decide(
        state="Traveler says: I am here for business.",
        questions={
            "suspicion": score(
                "How suspicious is the traveler?",
                ["calm", "slightly off", "suspicious", "alarming"],
            ),
            "consistent": noul(
                "Is the new statement consistent with earlier claims?",
                true="matches earlier claims",
                false="contradicts or invents",
            ),
            "reaction": choice(
                "How should the guard respond?",
                {
                    "wave_through": "nothing is wrong, let them pass",
                    "press_for_detail": "ask a sharper follow up question",
                    "demand_document": "ask to see papers",
                    "raise_alarm": "this person is a threat",
                },
            ),
        },
    )
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx


# ----------------------------------------------------------------------------
# Question builders. These produce the exact dict shape the server validates.
# ----------------------------------------------------------------------------

def noul(instructions: str, true: str | None = None, false: str | None = None) -> dict[str, Any]:
    """A yes/no question. Optional true/false descriptions sharpen the boundary."""
    q: dict[str, Any] = {"type": "noul", "instructions": instructions}
    criteria: dict[str, str] = {}
    if true is not None:
        criteria["true"] = true
    if false is not None:
        criteria["false"] = false
    if criteria:
        q["criteria"] = criteria
    return q


def choice(instructions: str, options: dict[str, str]) -> dict[str, Any]:
    """Pick one of N named options. options maps option name to a short description."""
    if len(options) < 2:
        raise ValueError("choice needs at least 2 options")
    return {"type": "choice", "instructions": instructions, "criteria": options}


def score(instructions: str, levels: list[str]) -> dict[str, Any]:
    """Rate on an ordered rubric. levels is ascending: index 0 is the low end."""
    if not (2 <= len(levels) <= 10):
        raise ValueError("score needs between 2 and 10 levels")
    return {"type": "score", "instructions": instructions, "criteria": levels}


# ----------------------------------------------------------------------------
# Client
# ----------------------------------------------------------------------------

@dataclass
class DeciderResult:
    """Parsed answers plus raw payload and measured latency."""

    answers: dict[str, dict[str, Any]]
    latency_ms: float
    raw: dict[str, Any]

    def noul(self, name: str) -> float:
        """P(true) for a yes/no question."""
        return float(self.answers[name]["noul"])

    def choice(self, name: str) -> tuple[str, float]:
        """(selected option, confidence) for a choice question."""
        a = self.answers[name]
        return a["choice"], float(a["confidence"])

    def probabilities(self, name: str) -> dict[str, float]:
        return {k: float(v) for k, v in self.answers[name]["probabilities"].items()}

    def score(self, name: str) -> float:
        """Expected level (a float over the rubric indices)."""
        return float(self.answers[name]["score"])

    def legend(self, name: str) -> dict[str, str]:
        return self.answers[name].get("legend", {})


class DeciderClient:
    """Minimal client for a local or remote Strands Decider server."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        timeout: float = 120.0,
        model: str = "strands-decider-latest",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(timeout=timeout)

    def health(self) -> bool:
        """True when the server answers. Does not guarantee the model has finished loading."""
        try:
            r = self._client.get(f"{self.base_url}/", timeout=5.0)
            return r.status_code < 500
        except httpx.HTTPError:
            return False

    def wait_until_ready(self, questions_probe: dict[str, Any] | None = None, max_wait: float = 1800.0) -> bool:
        """Poll until the server returns a real answer, tolerating the model load window."""
        probe = questions_probe or {"ready": noul("Is this sentence in English?")}
        deadline = time.time() + max_wait
        while time.time() < deadline:
            try:
                self.decide("The quick brown fox.", probe)
                return True
            except Exception:
                time.sleep(5.0)
        return False

    def decide(self, state: Any, questions: dict[str, Any], retries: int = 2) -> DeciderResult:
        """Send one state and a set of typed questions; return parsed answers."""
        payload = {"state": state, "questions": questions, "model": self.model}
        last_err: Exception | None = None
        for attempt in range(retries + 1):
            try:
                t0 = time.perf_counter()
                r = self._client.post(f"{self.base_url}/v1/systemone", json=payload)
                r.raise_for_status()
                data = r.json()
                latency_ms = (time.perf_counter() - t0) * 1000.0
                return DeciderResult(
                    answers=data.get("answers", {}),
                    latency_ms=data.get("latency_ms", latency_ms),
                    raw=data,
                )
            except httpx.HTTPError as exc:  # transient server or load state
                last_err = exc
                if attempt < retries:
                    time.sleep(3.0)
        raise RuntimeError(f"decider request failed after {retries + 1} attempts: {last_err}")

    def close(self) -> None:
        self._client.close()
