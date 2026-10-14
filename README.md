# 100 Days: Zero to One AI Engineer · Guide and Labs

The self-paced guide for the [100-day Zero to One AI Engineer program](https://dpaul0501.github.io/ai-engineer-100/). It is free and open to anyone. To join the peer group (mock interviews, defenses, idea reviews, and demo day), [sign up](https://forms.gle/RSezwZ7xUM5WRHiE8).

## The weeks

One page per week. Each lists the units for four pillars, and every unit follows the same cycle: **study** an authoritative source, **do** it yourself, make **1–2 variations**, write **tests**, and cover the **corner cases**.

| Week | Guide | Lab |
|---|---|---|
| 1 | [Lookups, Vectors, and Your First LLM Call](guide/docs/weeks/week_01.md) | [Pocket search CLI](week_01/) |
| 2 | [Pointers, Matrices, and Structured Output](guide/docs/weeks/week_02.md) | [Extraction tool with an eval set](week_02/) |

More weeks are added as they are ready.

**By pillar:** [DSA](guide/docs/tracks/dsa.md) · [ML/DL](guide/docs/tracks/ml-dl.md) · [AI Engineering](guide/docs/tracks/ai-engineering.md) · [System Design & Engineering Practice](guide/docs/tracks/system-design.md)

## How to work

1. Create your own public repo for the 100 days.
2. Work through one week at a time. Commit every unit, and keep a `PROGRESS.md` with what you finished and when.
3. For each weekly build, follow the lab spec in `week_NN/` and make the acceptance tests pass.
4. Post one finding a day on LinkedIn as **Day N/100**.

## Read the guide as a site

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
| `guide/docs/tracks/` | One page per pillar, generated from the weekly pages |
| `week_NN/` | The lab for each weekly build: spec, acceptance tests, and starter code where there is any |
| `scripts/` | `write_tracks.py` and `write_nav.py`, which regenerate the pillar pages and the nav |
