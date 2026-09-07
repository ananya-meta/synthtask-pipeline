# Prompts — human-authored, by policy and by design

Everything in this directory is written by Ananya. Nothing here is Claude-authored.

## Why

Two reasons, and they point the same way.

**Policy.** The track guidelines say *"Models: Codex and TBH only. No Claude (account
restrictions, and Claude is too relaxed as reviewer)"*, and define a policy-compliant task
as one with *"no 3p tokens in the agent facing files."* These prompts shape what task ideas
exist, so they sit on the wrong side of that line for a 3p model to write.

**Design.** The prompt *is* the pipeline. The harness in `ideation/` is plumbing — anyone
could write it. What separates a pipeline that yields accepted tasks from one that yields
slop is the accumulated judgement encoded in these files. Adhi's note in the track's
Findings tab is worth taking literally: *"This is a prompt refined over time and 100% human
written."*

## How to write the first version

Don't write it cold. Run one paper through by hand first — ask TBH for ideas, reject the
bad ones, and **write down why you rejected each one**. Those rejection reasons are the
prompt. A rule you can't trace back to an idea you actually rejected is a rule you're
guessing at.

The reason codes in `ideation/review.py` are the starting vocabulary; they come from failure
modes the track has already documented across seven people's pilots.

## Files

| File | Used by | Purpose |
|---|---|---|
| `generate_ideas.md` | `ideation generate` | Turn a seed paper into N candidate task ideas |
| `judge_rubric.md` | `ideation judge` | Score an idea on the five rubric dimensions |
| `extract_assumptions.md` | manual, for now | Pull the paper's load-bearing assumptions |
| `rank_ideas.md` | manual, for now | Feasibility-rank a batch (Valentina's two-agent split) |

## Template variables

`generate_ideas.md` is rendered with these substitutions before it reaches the model:

| Token | Replaced with |
|---|---|
| `{{N_IDEAS}}` | how many ideas to produce |
| `{{SEED_TITLE}}` | paper title |
| `{{SEED_SLUG}}` | seed directory name |
| `{{ASSUMPTIONS}}` | full text of the seed's `ASSUMPTIONS.md` |
| `{{OUTPUT_PATH}}` | where to write the JSON (`ideas.json`) |

The harness refuses to run while a prompt file still begins with `<!-- TODO`, so an
unfinished prompt fails loudly instead of silently producing garbage.

## Output contract

`generate_ideas.md` must instruct the model to write `{{OUTPUT_PATH}}` as JSON:

```json
{
  "ideas": [
    {
      "title": "short handle",
      "statement": "what the agent must build, stated without leaking how",
      "assumption_broken": "which paper assumption this violates, and why that is hard",
      "difficulty_claim": "why a frontier model would not solve this in one shot",
      "dataset_ref": "the real dataset this uses"
    }
  ]
}
```

`title`, `statement`, and `assumption_broken` are required; the harness drops entries
missing them. Codex additionally receives this as a JSON Schema via `--output-schema`.
