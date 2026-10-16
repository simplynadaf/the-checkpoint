"""Smoke test: run a scripted conversation through the game engine against the live
Decider server. Prints the calibrated numbers each turn so we can see the meter move.

Run:  python -m tests.test_game   (from the repo root, with the venv active)
"""

from __future__ import annotations

from app.decider_client import DeciderClient
from app.game import Game


SCRIPT = [
    "Evening officer. I am just heading home after visiting my mother.",
    "She lives in the next town over, about an hour away.",
    # deliberate contradiction with the first line (home vs just arrived):
    "Actually I have never been to this country before, this is my first visit.",
    "I am carrying nothing to declare, just my clothes.",
]


def main() -> None:
    decider = DeciderClient("http://127.0.0.1:8000")
    print("waiting for decider server to be ready...")
    if not decider.wait_until_ready(max_wait=300):
        raise SystemExit("decider server not ready")

    game = Game(decider=decider)
    print(f"\nscene: {game.scene}\nstart meter: {game.meter:.2f}\n")

    for line in SCRIPT:
        print(f'traveler: "{line}"')
        r = game.play_turn(line)
        bar = "#" * int(r.meter * 20)
        print(
            f"  suspicion={r.suspicion:.2f}  consistent={r.consistent:.2f}  "
            f"reaction={r.reaction}({r.reaction_confidence:.2f})"
        )
        print(f"  meter [{bar:<20}] {r.meter:.2f}  -> {r.outcome}  ({r.latency_ms:.0f} ms)\n")
        if r.outcome in {"passed", "alarm"}:
            print(f"GAME OVER: {r.outcome}")
            break

    decider.close()


if __name__ == "__main__":
    main()
