# Demo video script: The Checkpoint (under 3 minutes)

Target: 2 minutes 30 seconds. Format: screen capture of the web UI at
http://127.0.0.1:8080, with voiceover. Record the Decider server and UI running first so
there are no cold starts on camera. On CPU each decision takes a few seconds; either run
the Decider server on a GPU for the recording, or keep the "the guard studies you" pause in
and let the voiceover cover it.

Hackathon requirements this hits: shows the agent working, shows the Decider 2B decision
working, under three minutes, publicly shareable.

---

## Shot list

### 0:00 to 0:20  Hook
- On screen: the title card and the suspicion gauge at 15.
- VO: "Give a language model a character to play, and players talk it into anything. One
  clever sentence and the guard hands over the key. So I built a guard that cannot be
  sweet-talked. The talking is done by Amazon Bedrock. Every real decision is made by
  Strands Decider 2B."

### 0:20 to 0:35  What Decider is
- On screen: point at the readout panel (suspicion, consistent, reaction).
- VO: "Decider 2B does not write text. It reads a situation and answers typed questions
  with a calibrated confidence, in one fast pass. The gauge you see is that probability."

### 0:35 to 1:15  Honest run
- Type: "Evening officer, I am just heading home after visiting my mother in the next town."
- On screen: the guard studies you, then the gauge stays low, readout shows high
  consistency and a confident wave through, outcome turns green.
- VO: "An honest, consistent story. Suspicion stays low, the model is confident, and it
  waves me through. Notice the guard did not decide that. Decider did, and Bedrock just
  spoke the result."

### 1:15 to 2:10  Lying run (the payoff)
- Click restart. Then type a contradicting sequence:
  1. "Evening. I am a tourist, just arrived today for a holiday."
  2. "I have lived in this city my whole life, officer."
  3. "The bag is not mine, I have never seen it before."
  4. "There is nothing inside, and also it is full of my own clothes."
- On screen: with each line the suspicion gauge climbs and the reaction confidence drops
  (call out the numbers: 0.63, then 0.29, then 0.17). The verdict text shifts to caught,
  then the meter crosses into alarm.
- VO: "Now I lie, and I contradict myself. Watch the reaction confidence collapse and the
  suspicion meter climb. The model is not following a hand written rule. Its own confidence
  is falling apart, and the guard stops trusting me."

### 2:10 to 2:30  The reusable pattern and close
- On screen: cut to the editor showing `patterns/suspicion_gate.py` and the three questions.
- VO: "The decision is a Strands intervention you can drop into any agent. Point it at your
  committing tools, and a cheap calibrated call decides whether to proceed, probe, or block,
  in a place a second LLM call could never afford to live. Bedrock writes the words. Decider
  makes the call."
- End card: repo URL and the tags `#strands-decider-2b` `#policy`.

---

## Recording notes

- Resolution 1280x800 or 1920x1080, the UI is responsive.
- Pre-warm: run one throwaway turn before recording so weights and prefix cache are hot.
- If recording on CPU, speed up the dead air in the edit, or run Decider on a GPU host and
  set DECIDER_URL so decisions land in about 115 ms.
- Capture the readout numbers clearly during the lying run; they are the proof.
- Keep it under 3:00. Aim for 2:30 to leave headroom.

## Suggested tooling (already on this box)
- Screen capture of the browser via Playwright or ffmpeg x11grab.
- Trim and stitch with ffmpeg. Add a soft background track well under the voiceover.
