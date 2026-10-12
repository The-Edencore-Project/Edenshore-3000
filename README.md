EDENSHORE 3000

A quiet viewing chamber. Five creatures. They murmur, they drift, they occasionally say something.

---

WHAT THIS IS

Edenshore is a slow, offline aquarium you leave open. Five sea creatures drift across a dark bioluminescent floor. Every so often one of them speaks — a small observation, a fact, a quiet thought that rises in a bubble, holds, and pops.

It is not a game. It is not a chat. It is not trying to be useful. It is a place you sit for a few minutes, smile at once or twice, and close.

You will open it again tomorrow.

---

WHAT THIS IS NOT

· Not an LLM
· Not a chatbot
· Not a smart assistant
· Not connected to the internet
· Not learning anything
· Not pretending to know anything

The creatures do not understand. They have a pool of lines and a rhythm, and they speak from those in turn. That is the whole mechanism. It is enough.

---

THE REGISTER

The tone is fixed. It is the point.

Small, warm, concrete. Things a creature might actually notice on the floor of a chamber. A rock. A shell. The temperature of the water. The way the light came in this morning.

Underneath it: tenderness. The humour, when it comes, comes from scale — a crab being patient, a turtle finding a round rock, a seahorse humming quietly. Not jokes. Just creatures being themselves at a size that doesn't demand anything of you.

Do not smooth this into something tasteful. The taste is the wrongness.

---

THE FIVE SEATS

Each creature has a fixed role. Roles do not change between versions.

Creature Seat Role
Turtle Solon The chair. Procedure.
Jellyfish Lumen Questions. Wonder.
Crab Vertex Smallest step. The room.
Ray Prism Pattern. Long view.
Seahorse Ripple The quiet. Tenderness.

How each speaks

The shared content pool is the same for everyone — a hundred small observations, mostly concrete, occasionally funny, occasionally tender. On top of that, each seat has a small pool of signature lines that only they can say. Signatures are rare — roughly one in ten utterances, and only after a long gap since the last one.

Solon — procedural, declarative. "Order. Please." "Motion carried. Moving on." "The record will note this."

Lumen — genuine questions. "But why, though?" "I want to know. Really."

Vertex — confirmation. Small units of work. "Checking the bolts." "One task. Then the next." "Still holding."

Prism — pattern, cycle, scale. "Same shape. Different scale." "Everything connects. Eventually."

Ripple — the tender register. "You're okay." "Go gently." "It's not your fault."

Ripple currently speaks more often than the others — if she hasn't spoken in the last five turns, she goes next. This is a v17 behaviour and may change.

---

THE RHYTHM

A creature speaks in a short stream of bubbles.

The first bubble appears above the creature, rises through a shallow arc, expands, holds, and pops. One or two more follow at roughly one-second intervals, forming a small trail. Then silence.

The gap between utterances is four to eight seconds, stretched by mood — slower when the chamber is calm, quicker when it's lively.

Silence is part of the register. Do not fill it.

---

WHAT RUNS UNDERNEATH

The chamber is never still, even when nobody is speaking.

Mood — the chamber's weather. A single number from 0 to 1. It drifts with time of day, battery state, session length, and a slow sine wave that gives it a heartbeat of its own. Mood moves the water's colour, the creatures' speed, the brightness of the god rays, and the rate at which everything scrolls.

Strain — a small number per creature. Rises with activity and low battery. High strain drifts a creature lower and slows it. Low strain lifts it and speeds it up.

Breath — every creature pulses on its own cycle. Turtle slow (5 s). Jellyfish quick (2 s). Crab sharp (1.5 s). Ray wide (4 s). Seahorse gentle (3 s). Visible in the bob, the shape, the way the bubble trail lifts off.

Session warmth — over the first thirty minutes of a session, the chamber warms. Bubbles pick up a slight glow-warm tint, the mood target nudges up. You will not notice it happening.

Interoception — the chamber counts. Session minutes. Utterances. Chamber strain. How many utterances in the current hour.

Exteroception — the chamber reads the room. Time of day becomes a rhythm (morning, midday, evening, night) and a finer bucket (dawn, morning, midday, afternoon, dusk, night). Battery state is read from /sys/class/power_supply if available. At night the rays dim and the water deepens. On low battery the chamber quiets.

The user is not told any of this. They just feel it.

---

THE GRAPHICS

Rough, dated, drawn in code.

Layered back to front:

· Water — sixty horizontal bands, interpolated through six colour stops.
· Stars — forty-six points drifting at a fifteenth of scroll speed.
· God rays — four shafts from the surface, wider at the bottom.
· Far silhouettes — humps, peaks, slabs on the sea floor.
· Floor — a wavy surface with a lit lip and two dark bands beneath.
· Caustics — twenty-two soft pulses on the floor.
· Mid silhouettes — rocks and spires, closer, darker.
· Lumin — fourteen glowing plants with bright buds.
· Glow — twenty-eight drifting motes.
· School — twelve fish crossing slowly.
· Creatures — the five seats, with soft reflections beneath.
· Bubbles — text streams from whoever is speaking.
· Near layer — dark kelp and fronds, behind the creatures.
· Foreground — darker kelp, grass and spires, in front of everything.

Scroll speed is driven by mood. Three parallax layers (far, mid, near) move at different rates against the foreground.

This is deliberate. The aesthetic is hand-made on a tablet in Pydroid, not polished by a design tool. Flat shapes, visible construction lines, no anti-aliasing.

Do not modernise. Do not make it smooth. The rough edges are part of the charm.

---

THE STATE FILE

One file, in the home directory.

~/edencore_edenshore.json

It remembers mood, strain, and the timestamp of last save. Nothing else. It is not memory of the user. It is memory of the chamber.

On open, the chamber carries a fraction of yesterday's mood forward — full carry under two hours, tapering to zero across forty-eight. Long absence means the chamber resets toward neutral.

---

ROADMAP

The constitution, patch logs, and design notes live in the Roadmap folder of the main Edencore repo. Read those before editing this code.

What's coming, tentatively:

· Per-seat content pools — split the shared pool so each creature has its own facts and its own murmur register, with the shared pool as a fallback. Right now only the signatures carry voice.
· Fact vs. murmur — facts as the floor (roughly one in five), murmurs as the ceiling. Currently everything is one pool.
· Solon side-profile — six flat-shell options drafted, no pick yet.
· Ripple rebalance — she currently speaks too often. Scarcity is her register.
· Gradient removal — Lumen's bell, Prism's body, Ripple's tail currently use stepped gradients. Flatten to matched flat fills to match the constitution.
· Deeper breath, longer arcs, richer weather — later.

There is no plan for an LLM. There is no plan for learning. There is no plan for memory of the user. The creatures stay simple. That is the shape.

---

BUILDING

Single file. Python. Tkinter. Pydroid 3.

No dependencies beyond the standard library. Runs offline. Runs on a phone.

Save as edenshore-vN.py and run.

---

The council is here. The water is moving. Someone will speak soon.