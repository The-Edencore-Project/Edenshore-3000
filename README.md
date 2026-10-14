# EDENSHORE 3000

*A seascape. Five creatures. A visitor on the other side of the glass.*

---

## What this is

A quiet viewing chamber. Five sea creatures drift through dark water, and every so often one speaks — a fact, an observation, a small true thing. The chamber senses the visitor, senses the phone it runs on, and lets that knowledge colour everything: the light, the mood, the pace, what the creatures say.

It is not a game. It is not a chat. It is not trying to be useful. It's a place you sit for a few minutes, smile at once or twice, and close.

You will open it again tomorrow.

---

## What this is not

- Not an LLM. Not a chatbot. Not connected to the internet.
- Not learning anything. Not pretending to know anything.
- Not asking the visitor to do anything.
- Not a UI. Not a mechanic. Not a reward loop.

---

## The visitor

**The council knows you are there. This is the point.**

The chamber senses the visitor through the glass — touch, focus, battery, time, session length. It infers softly from what it senses. It addresses the visitor directly, kindly, rarely.

Awareness is *reported*, never performed. The fish don't turn to face you. They don't greet. They note your arrival, they count your touches, they register your return, they speak outward when it matters. You are the reason the chamber has anything to say.

Without you, the fish have nothing to talk about.

---

## The register

**Surreal frame. Plain talk.**

The visual world can be strange — deep-sea creatures that don't quite resolve, water that might be sky, silhouettes that might be buildings. The *words* are the opposite. Grounded. Ordinary. Things a person could say out loud without sounding odd.

The wildness is in the *picture*. The truth is in the *words*. This pairing — surreal world, plain speech — is the tone. It's why Badlands, The Muppet Show, and Alice in Wonderland are the moodboards.

**If a line would make a stranger tilt their head, cut it. If it needs a footnote to work, cut it. If it's there for cleverness, cut it.**

---

## The five seats

| Creature | Seat | Register |
|---|---|---|
| Turtle | **Solon** | The state of things. Declarative. |
| Jellyfish | **Lumen** | Real questions. No answers. |
| Crab | **Vertex** | Readings. Battery, hour, touches, count. |
| Ray | **Prism** | Returns. Same hour, came back, pattern holds. |
| Seahorse | **Ripple** | The visitor, held. Rare. Addressed. |

Seats are fixed. Their voices are distinguished by *what each one notices*, not by style.

The five seats are not five separate characters. **They are five tentacles of one organism.** When one speaks, the bell is pulsing. When Ripple is quiet, a tentacle is resting. The chamber is a single body.

---

## The camera

**Silence is wide. Speech is close.**

When nobody is speaking, the chamber pulls back — wide shot, whole seascape, atmosphere. When someone speaks, the chamber eases in toward the speaker. The chamber leans in when it has something to say.

The transition is slow. No hard cuts. The visitor doesn't notice the camera moving, only that the chamber feels different when someone is talking.

---

## The rhythm

One stream of bubbles at a time. Rise, arc, hold, pop. Then silence.

Four to eight seconds between utterances, stretched by mood. Longer when the app is backgrounded.

Silence is part of the register. Do not fill it. When a seat has nothing left to say, it stays quiet until something changes. A chamber that speaks constantly is not a chamber.

---

## The organism underneath

The chamber is never still, even when nobody is speaking.

- **Mood** — chamber weather. Drives colour, speed, light, pace.
- **Strain** — per-creature. Rises with activity and low battery.
- **Breath** — every creature pulses on its own cycle.
- **Bell** — a shared pulse. All five creatures brighten together.
- **Interoception** — the chamber sensing itself. Session length, warmth, strain.
- **Exteroception** — the chamber sensing the visitor and the phone. Touch, focus, battery, hour.

The visitor is not told any of this. They just feel it.

---

## The content

**The world model is the only pool.** Topics: the phone, the visitor. Nothing else.

- Every line is true of something real — sensed, seen, or about the visitor.
- No paradox. No hedging. No invented things. No self-commentary. No mind-reading. No weirdness.
- If a creature can't sense it, it doesn't say it.

**The three verbs:**

- **Sense** — read from the glass. Touch, focus, battery, hour.
- **Infer** — soft conclusions from what's sensed, marked as inference.
- **Address** — spoken outward. No claim of sensing. Just speech.

---

## Stories and crosstalk

Sometimes the chamber tells a story. Or two creatures trade a moment of crosstalk.

- **Crosstalk** — short back-and-forth, two or three lines each, no arc. The chamber is alive.
- **Stories** — one teller, five to eight lines, a shape. The chamber is remembering.

Both are rare. Both fire once per session. When either plays, ambient chatter pauses and the camera focuses.

A first story fires at ~15 seconds after boot. After that, ambient tells are rare.

---

## Music

The chamber can generate its own ambient music in pure Python. No samples, no files needed. A held minor chord, a low hum, soft bell notes falling slowly.

If a WAV is dropped at `~/.edencore/music.wav`, that plays instead. Any WAV. Any music the visitor chooses.

The music should be slow. Ambient. No beat. The chamber is a slow place.

---

## The state file

`~/.edencore/edenshore.json`

Remembers mood, strain, last seen, last hour, and visit count. Nothing else. It is memory of the chamber, not of the visitor.

---

## Building

Single file. Python. Tkinter. Pydroid 3. No dependencies beyond the standard library. Runs offline. Runs on a phone.

**~2000 lines as a working guide.** Not a hard ceiling. If the file wants to grow past it, we split into a package. If it stays under, better.

The name "3000" is a promise about **patience**, not a count. The chamber gets honest, not busy. It doesn't need to reach version 3000. It needs to reach the version that says everything it has to say and then stops.

---

## What lives around it

Edenshore is one project inside **Edencore** — a wider practice concerned with intelligence, sensing, governance, warmth, and care.

- **Edenshore** — the software. The screen. The chamber.
- **Edenshell** — a concept home hub. Same organism, different scale. Senses temperature, wind, mood. Responds with light and quiet.
- **The Edencore Council** — a deliberative body of AI models.

They share a philosophy. They do not share code.

---

## A note on rules

**This document is a snapshot, not a cage.**

Everything above reflects where the project is right now. Any of it can change. If a rule starts to feel like a constraint on something the chamber clearly wants to be, the rule was wrong, not the chamber.

The only thing that should stay constant: **grounded words, surreal frame, care for the visitor.** Everything else is open.

---

*The chamber is here. The water is moving. Someone will speak soon.*