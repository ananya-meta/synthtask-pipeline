# ananyajain-ideation

Ideation pipeline for the AAI **Research Papers to Tasks** track.

Research paper or graph-discovery bundle → candidate task ideas → deduped →
rubric-scored → human-adjudicated → task contract → isolated scaffold workspace →
verification/review → submission triage → learning loop.

The first half keeps every idea and every rejection so the pipeline can be measured and
tuned. The second half keeps every scaffold, verifier result, reviewer verdict, and
submission outcome so task construction improves from evidence instead of memory.

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

## Ideation Flow

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

## Task-Generation Flow

The graph-guided discovery engine fits upstream of this repo. It should emit a bundle of
Markdown/JSON evidence describing a vetted research direction; this harness ingests that
bundle and moves accepted ideas through controlled construction.

```bash
# 1. ingest a discovery bundle from Paper Factory or another graph-discovery run
ideation discovery ingest /path/to/discovery-bundle \
  --source paper-task-factory \
  --source-url https://fb.workplace.com/groups/3258720224333062/posts/3291314974406920 \
  --title "graph-guided harness discovery"

# 2. draft a task contract from a human-accepted idea
ideation contract create 42 \
  --bundle-id 1 \
  --hidden-principle "hidden semantic oracle over held-out cases" \
  --allowed-input "visible fixtures and public README" \
  --forbidden-leak "hidden cases, scoring thresholds, oracle implementation" \
  --oracle-strategy "compare against implementation-independent hidden oracle" \
  --mutation-strategy "reject noop, hard-coded, and public-example-only solvers" \
  --infra-requirement "stdlib Python verifier inside the task image" \
  --difficulty-target "frontier agents should need multiple attempts"

# 3. mark complete contracts ready
ideation contract ready 1

# 4. create an isolated scaffold workspace
ideation scaffold start 1 --builder codex

# 5. run the builder with a human-owned prompt template, or build manually under task/
ideation scaffold run 1 --prompt-file /path/to/build_prompt.md

# 6. after the builder creates task files under the workspace's task/ directory,
# run local checks and record adversarial reviews
ideation verify run 1 --cwd task -- python3 -m unittest discover -s tests -v
ideation audit record 1 --reviewer tbh --kind adversarial --verdict revise \
  --issue BAD_GRADING_WEAK:"hidden oracle misses edge cases"

# 7. promote only approved staged files into an empty canonical task root
ideation scaffold promote 1 /path/to/canonical-task-root

# 8. record Smoldata/Codimango results and preserve the triage route
ideation submission record 1 --platform smoldata --external-id abc-123 \
  --status bad_grading_weak --pass-rate 1.0 --revisions 2

# 9. write durable learning events for later A/B tests
ideation learn add --scope-type submission --scope-id 1 \
  --label weak-grader --detail "public cases did not cover stateful edge cases"

# 10. see controller state and queued next actions
ideation pipeline status
```

`ideation pipeline run` can advance one task through the same gates until it reaches a
real blocker:

```bash
ideation pipeline run \
  --idea-id 42 \
  --bundle-id 1 \
  --builder codex \
  --build-prompt-file /path/to/build_prompt.md \
  --verify-command "python3 -m unittest discover -s tests -v" \
  --canonical-root /path/to/canonical-task-root \
  --stop-after promote
```

## Where Smoldata Fits

Smoldata is the external validation and feedback gate, not the source of task ideas and
not the local build harness.

```text
local harness:
  discovery -> ideas -> contract -> scaffold -> local verifier -> adversarial review

external validation:
  upload canonical task -> Smoldata/Codimango agents run -> Agentic Full-Task Review

feedback loop:
  Smoldata result -> triage label -> targeted revision -> local verifier -> resubmit
```

The installed `codimango` CLI currently exposes inspection, watch, rerun, trial artifact,
and Agentic Full-Task Review commands. It does not expose task creation in this harness.
So submission/upload remains an explicit external step, and this repo records the
resulting task name or ID:

```bash
ideation smoldata watch my-task-name --scaffold-run-id 1
ideation smoldata review my-task-name --wait --scaffold-run-id 1
ideation smoldata rerun my-task-name
```

Smoldata feedback is mapped into controller routing:

| Smoldata signal | Pipeline route |
|---|---|
| `accepted` | done |
| `pending` | poll again |
| `infra` / `infra_error` | fix Docker/runtime/artifacts |
| `bad_grading_weak` | strengthen hidden oracle and mutation tests |
| `grading_wrong` | fix verifier contract |
| `too_easy` | reduce leakage or add hidden state/scale |
| `too_hard` | simplify or retarget |
| `leak` | separate visible task from hidden scoring |
| `timeout` | reduce runtime or budget |

## Isolation

Valentina's Codex-vs-TBH comparison was invalidated because the agents could read each
other's tasks, and NG Li caught Muse writing outside its assigned workspace. So each run
gets a fresh root under `runs/<seed>/<generator>/<timestamp>/` containing only the paper
and the assumptions file, and `assert_isolated()` fails the run if anything else appears.

Scaffold construction uses the same principle. `ideation scaffold start` creates a fresh
workspace with `TASK_CONTRACT.json`, `TASK_CONTRACT.md`, controller notes, and empty
`task/`, `logs/`, `reviews/`, and `verification/` directories. Builders work only inside
that workspace. `ideation scaffold promote` is the only command that copies staged task
files into a canonical output directory.

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
