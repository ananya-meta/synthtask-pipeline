# ananyajain-ideation

Ideation pipeline for the AAI **Research Papers to Tasks** track.

Research paper → candidate task ideas → deduped → rubric-scored → human-adjudicated,
with every idea and every rejection kept so the pipeline can be measured and tuned.

It stops at *"here is an idea worth scaffolding."* Scaffolding, tests, and Smoldata
submission stay manual.

## Why ideation

Ideation is the track's stated #1 known challenge — *"models tend to produce similar ideas
regardless of seed"* — and the stage where human attention has the highest marginal return
(Adhi: human-in-the-loop at ideation raises accepted-task yield). It is also the only stage
cheap enough to iterate on: a scaffold round-trip is hours, an ideation round-trip is minutes.

The differentiator is not that it generates ideas — everyone's pipeline does. It is that
every idea is kept with a **reason-coded human verdict**, so:

- rejections aggregate into a rubric,
- the rubric becomes a Codex judge,
- judge-vs-human agreement (macro-F1, Cohen's κ) is tracked per rubric version,
- and accepted ideas are traced to their downstream Smoldata fate.

That closes the outer loop the track keeps asking for, and it directly answers the
documented blind spot that *"when TBH both generates and reviews its own tasks, it tends to
approve them too easily."*

## Install

Stdlib only — no dependencies.

```bash
cd ~/AAI/ananyajain-ideation
uv tool install --editable .     # or: alias ideation='python3 -m ideation.cli'
```

## Flow

```bash
# 1. find and ingest a seed
ideation seed search "llm as a judge rubric reliability" --sort-by citations
ideation seed add --arxiv-id 2606.19544 --lane llm-eval

# 2. fill in the paper's load-bearing assumptions, by hand
$EDITOR seeds/01-*/ASSUMPTIONS.md

# 3. write the generation prompt, by hand (once)
$EDITOR prompts/generate_ideas.md      # see prompts/README.md

# 4. generate under isolation — codex and tbh never see each other's output
ideation generate 01-reliability-without-validity -n 8

# 5. prefilter, then escalate borderline pairs to Codex
ideation dedup --adjudicate

# 6. score against your rubric (needs prompts/judge_rubric.md)
ideation judge

# 7. the human gate — single-keystroke reason codes, resumable
ideation review

# 8. metrics
ideation report

# 9. close the loop once a task reaches Smoldata
ideation outcome 42 --smoldata-task-id abc-123 --accepted 1 --pass-rate 0.13
```

## Isolation

Valentina's Codex-vs-TBH comparison was invalidated because the agents could read each
other's tasks, and NG Li caught Muse writing outside its assigned workspace. So each run
gets a fresh root under `runs/<seed>/<generator>/<timestamp>/` containing only the paper
and the assumptions file, and `assert_isolated()` fails the run if anything else appears.

Any per-generator number in `ideation report` is only trustworthy because of this.

## Reason codes

| Code | Meaning |
|---|---|
| `ACCEPT` / `ACCEPT_WITH_EDIT` | proceed to scaffolding |
| `MEMORIZED` | textbook fix a model recalls rather than reasons to |
| `PAPER_REIMPL` | reimplements the paper; no assumption broken |
| `DUPLICATE` | near-dupe of an idea already in the corpus |
| `STALE_PATTERN` | known attractor (constrain memory, token limit, …) |
| `OVERSPEC_RISK` | can't be stated without leaking the solution |
| `NOT_VERIFIABLE` | no clean binary oracle |
| `TOO_EASY` | a frontier model solves it trivially |
| `TOO_ARTIFICIAL` | difficulty is synthetic, not real |
| `NEEDS_SYNTH_DATA` | no real dataset available |
| `SCOPE_TOO_BIG` | doesn't fit a task budget |

Each maps to a failure mode documented in the track's Findings tab.

## Authorship

`prompts/**` is human-written and stays that way — both because the track bars Claude from
the generation loop, and because the prompt is the actual differentiator. See
[`prompts/README.md`](prompts/README.md) and [`AGENTS.md`](AGENTS.md).
