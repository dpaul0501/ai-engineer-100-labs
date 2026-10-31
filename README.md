# 100 Days: Zero to One AI Engineer · Guide and Labs

The self-paced guide for the [100-day Zero to One AI Engineer program](https://dpaul0501.github.io/ai-engineer-100/). It is free and open to anyone. To join the peer group (mock interviews, defenses, idea reviews, and demo day), [sign up](https://forms.gle/RSezwZ7xUM5WRHiE8).

**Read it as a site:** <https://dpaul0501.github.io/ai-engineer-100-labs/>

## The weeks

One page per week, released in order. Each week is one build that moves five dimensions forward: **DSA, ML, AI, System Design, and Software Delivery**. Every build goes spec → contract → test → code.

| Week | Guide | Tutorial | Lab |
|---|---|---|---|
| 1 | [Tokens and Decoding](guide/docs/weeks/week_01.md) | [Week 1 tutorial](https://dpaul0501.github.io/ai-engineer-100-labs/tutorials/week_01.html) | [`tok`](week_01/) |

The plan for Weeks 1–4 is in [Month 1](guide/docs/month_01.md). Later weeks are added as they are ready.

**By dimension:** [DSA](guide/docs/tracks/dsa.md) · [ML](guide/docs/tracks/ml.md) · [AI](guide/docs/tracks/ai.md) · [System Design](guide/docs/tracks/system-design.md) · [Software Delivery](guide/docs/tracks/software-delivery.md)

## How to work

1. Create your own public repo for the 100 days.
2. Work through one week at a time. Commit every unit, and keep a `PROGRESS.md` with what you finished and when.
3. For each weekly build, write the spec and failing tests first, then follow the lab in `week_NN/` until the acceptance tests pass.
4. Post one finding a day on LinkedIn as **Day N/100**.

## Read the guide locally

```bash
cd guide
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Then open `http://127.0.0.1:8000`.

## Layout

| Path | What it holds |
|---|---|
| `guide/docs/weeks/` | One page per week |
| `guide/docs/tutorials/` | The lecture tutorial for each week (HTML, with live demos) |
| `guide/docs/tracks/` | One page per dimension, generated from the weekly pages |
| `week_NN/` | The lab for each weekly build: spec, contracts, acceptance tests, and starter code |
| `scripts/` | `write_tracks.py` and `write_nav.py`, which regenerate the dimension pages and the nav |
