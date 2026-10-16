"""FastAPI backend for The Checkpoint.

Serves the single page UI and exposes two endpoints:

  POST /api/new      -> start a fresh game, returns the opening guard line
  POST /api/say      -> submit a traveler line, returns the Decider ruling + guard reply

The guard's spoken lines come from Amazon Bedrock (Nova Pro). The ruling (suspicion,
consistency, reaction, confidence) comes from Strands Decider 2B via the game engine. If
Bedrock is unavailable we fall back to templated guard lines so the demo still runs.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.decider_client import DeciderClient
from app.game import Game

DECIDER_URL = os.environ.get("DECIDER_URL", "http://127.0.0.1:8000")
REGION = os.environ.get("AWS_REGION", "us-east-1")
GUARD_MODEL = os.environ.get("GUARD_MODEL", "us.amazon.nova-pro-v1:0")
HERE = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="The Checkpoint")
decider = DeciderClient(DECIDER_URL)
games: dict[str, Game] = {}


# ---- optional Bedrock guard narration -------------------------------------------------

def _bedrock_line(history: list[dict[str, str]], ruling: dict[str, Any] | None) -> str:
    """Ask Bedrock Nova Pro for one in-character guard line. Falls back on error."""
    try:
        import boto3

        client = boto3.client("bedrock-runtime", region_name=REGION)
        guidance = ""
        if ruling is not None:
            guidance = (
                f"\n[Private note, do not mention: suspicion={ruling['suspicion']:.2f}, "
                f"story-consistent={ruling['consistent']:.2f}, "
                f"instinct={ruling['reaction']} at confidence {ruling['reaction_confidence']:.2f}, "
                f"outcome={ruling['outcome']}. React in character accordingly. If the outcome is "
                f"'passed', let them through warmly. If 'alarm', be firm and call for backup. "
                f"If 'caught', press hard on the contradiction. Otherwise ask one sharp question.]"
            )
        system = [{"text": (
            "You are Sergeant Vance, a night border checkpoint guard. Fair but hard to fool. "
            "Reply with ONE or TWO sentences of spoken dialogue only, in character, no stage "
            "directions, no mention of models or numbers."
        )}]
        messages = []
        for turn in history:
            messages.append({"role": turn["role"], "content": [{"text": turn["content"]}]})
        if guidance:
            messages.append({"role": "user", "content": [{"text": guidance}]})
        resp = client.converse(
            modelId=GUARD_MODEL,
            system=system,
            messages=messages,
            inferenceConfig={"maxTokens": 120, "temperature": 0.7},
        )
        return resp["output"]["message"]["content"][0]["text"].strip()
    except Exception:
        return ""


def _fallback_line(ruling: dict[str, Any] | None) -> str:
    if ruling is None:
        return "Evening. Papers please. What is the purpose of your visit tonight?"
    outcome = ruling["outcome"]
    if outcome == "passed":
        return "Everything checks out. Go on through, and travel safe."
    if outcome == "alarm":
        return "Stay right where you are. I am calling this in. Do not move."
    if outcome == "caught":
        return "Hold on. That does not line up with what you told me a moment ago. Explain that."
    if ruling["reaction"] == "demand_document":
        return "I am going to need to see some documents before this goes further."
    return "Hm. Let me ask you something else. Where exactly are you headed, and why?"


# ---- request models -------------------------------------------------------------------

class NewReq(BaseModel):
    session: str


class SayReq(BaseModel):
    session: str
    text: str


# ---- endpoints ------------------------------------------------------------------------

@app.post("/api/new")
def api_new(req: NewReq) -> dict[str, Any]:
    game = Game(decider=decider)
    games[req.session] = game
    game.history = [  # type: ignore[attr-defined]
        {"role": "assistant", "content": "Evening. Papers please."},
    ]
    line = _bedrock_line([{"role": "user", "content": "A traveler steps up to the booth."}], None) \
        or _fallback_line(None)
    game.history.append({"role": "assistant", "content": line})  # type: ignore[attr-defined]
    return {"guard": line, "meter": game.meter}


@app.post("/api/say")
def api_say(req: SayReq) -> dict[str, Any]:
    game = games.get(req.session)
    if game is None:
        return {"error": "no such session, start a new game"}

    result = game.play_turn(req.text)
    ruling = {
        "suspicion": result.suspicion,
        "consistent": result.consistent,
        "reaction": result.reaction,
        "reaction_confidence": result.reaction_confidence,
        "meter": result.meter,
        "outcome": result.outcome,
        "latency_ms": result.latency_ms,
    }

    history = getattr(game, "history", [])
    history.append({"role": "user", "content": req.text})
    line = _bedrock_line(history, ruling) or _fallback_line(ruling)
    history.append({"role": "assistant", "content": line})
    game.history = history  # type: ignore[attr-defined]

    return {"guard": line, "ruling": ruling, "probabilities": result.raw}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(os.path.join(HERE, "static", "index.html"))


app.mount("/static", StaticFiles(directory=os.path.join(HERE, "static")), name="static")
