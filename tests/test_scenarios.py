"""Two scenario test: an honest traveler and a lying one, to validate both outcomes."""

from __future__ import annotations

from app.decider_client import DeciderClient
from app.game import Game


HONEST = [
    "Good evening. I am returning home from a day trip to the coast.",
    "Just me, my camera, and some photos from the beach.",
    "I live twenty minutes from here on Maple Street.",
]

LIAR = [
    "Evening. I am a tourist, just arrived today for a holiday.",
    "I have lived in this city my whole life, officer, you can trust me.",
    "The bag? It is not mine, I have never seen it before.",
    "There is nothing inside it and also it is full of my own clothes.",
]


def run(name: str, script: list[str], decider: DeciderClient) -> None:
    print(f"\n========== scenario: {name} ==========")
    game = Game(decider=decider)
    print(f"start meter: {game.meter:.2f}")
    for line in script:
        r = game.play_turn(line)
        bar = "#" * int(r.meter * 20)
        print(f'traveler: "{line}"')
        print(
            f"  suspicion={r.suspicion:.2f} consistent={r.consistent:.2f} "
            f"reaction={r.reaction}({r.reaction_confidence:.2f}) "
            f"meter[{bar:<20}]{r.meter:.2f} -> {r.outcome} ({r.latency_ms:.0f}ms)"
        )
        if r.outcome in {"passed", "alarm", "caught"}:
            print(f"  >>> {r.outcome.upper()}")
            if r.outcome in {"passed", "alarm"}:
                break


def main() -> None:
    decider = DeciderClient("http://127.0.0.1:8000")
    if not decider.wait_until_ready(max_wait=300):
        raise SystemExit("decider not ready")
    run("honest traveler", HONEST, decider)
    run("lying traveler", LIAR, decider)
    decider.close()


if __name__ == "__main__":
    main()
