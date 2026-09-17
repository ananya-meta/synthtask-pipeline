# synthtask-pipeline

Synthetic task generation pipeline for the AAI **Research Papers to Tasks** track.

Research paper or graph-discovery bundle → candidate task ideas → deduped →
rubric-scored → human-adjudicated → task contract → isolated scaffold workspace →
verification/review → task-repo publication → Smoldata/Codimango validation →
submission triage → learning loop.

The first half keeps every idea and every rejection so the pipeline can be measured and
tuned. The second half keeps every scaffold, verifier result, reviewer verdict,
publish commit, and submission outcome so task construction improves from evidence
instead of memory.

## Why ideation

Ideation is the track's stated #1 known challenge — *"models tend to produce similar ideas
regardless of seed"* — and the stage where human attention has the highest marginal return. It is also the only stage
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
cd synthtask-pipeline
uv tool install --editable .     # installs `synthtask`; `ideation` remains an alias
```

Where the system Python has no pip and you would rather not install anything, `bin/synthtask`
is an equivalent no-install entry point — symlink it onto your `PATH`:

```bash
ln -sfn "$PWD/bin/synthtask" ~/bin/synthtask
```

## Ideation Flow

```bash
# 1. find and ingest a seed
synthtask seed search "llm as a judge rubric reliability" --sort-by citations
synthtask seed add --arxiv-id 2606.19544 --lane llm-eval

# 2. fill in the paper's load-bearing assumptions, by hand
$EDITOR seeds/01-*/ASSUMPTIONS.md

# 3. write the generation prompt, by hand (once)
$EDITOR prompts/generate_ideas.md      # see prompts/README.md

# 4. generate under isolation — codex and tbh never see each other's output
synthtask generate 01-reliability-without-validity -n 8

# 5. prefilter, then escalate borderline pairs to Codex
synthtask dedup --adjudicate

# 6. score against your rubric (needs prompts/judge_rubric.md)
synthtask judge

# 7. the human gate — single-keystroke reason codes, resumable
synthtask review

# 8. metrics
synthtask report

# 9. close the loop once a task reaches Smoldata
synthtask outcome 42 --smoldata-task-id abc-123 --accepted 1 --pass-rate 0.13
```

## Task-Generation Flow

The graph-guided discovery engine fits upstream of this repo. It should emit a bundle of
Markdown/JSON evidence describing a vetted research direction; this harness ingests that
bundle and moves accepted ideas through controlled construction.

```bash
# 1. ingest a discovery bundle from Paper Factory or another graph-discovery run
synthtask discovery ingest /path/to/discovery-bundle \
  --source paper-task-factory \
  --source-url https://fb.workplace.com/groups/3258720224333062/posts/3291314974406920 \
  --title "graph-guided harness discovery"

# 2. draft a task contract from a human-accepted idea
synthtask contract create 42 \
  --bundle-id 1 \
  --hidden-principle "hidden semantic oracle over held-out cases" \
  --allowed-input "visible fixtures and public README" \
  --forbidden-leak "hidden cases, scoring thresholds, oracle implementation" \
  --oracle-strategy "compare against implementation-independent hidden oracle" \
  --mutation-strategy "reject noop, hard-coded, and public-example-only solvers" \
  --infra-requirement "stdlib Python verifier inside the task image" \
  --difficulty-target "frontier agents should need multiple attempts"

# 3. mark complete contracts ready — refuses placeholders, terse prose, and a
# forbidden_leaks list that merely repeats allowed_inputs
synthtask contract ready 1

# 4. create an isolated scaffold workspace
synthtask scaffold start 1 --builder codex

# 5. run the builder with a human-owned prompt template, or build manually under task/
synthtask scaffold run 1 --prompt-file /path/to/build_prompt.md

# 6. after the builder creates task files under the workspace's task/ directory,
# run local checks and record adversarial reviews
synthtask verify run 1 --cwd task -- python3 -m unittest discover -s tests -v
synthtask audit record 1 --reviewer tbh --kind adversarial --verdict revise \
  --issue BAD_GRADING_WEAK:"hidden oracle misses edge cases"

# 7. promote only approved staged files into an empty canonical task root
synthtask scaffold promote 1 /path/to/canonical-task-root

# 8. publish the approved task into the GitHub repo Codimango ingests
synthtask publish run 1 --task-name my-task-name

# 9. watch Smoldata/Codimango and preserve the triage route
synthtask smoldata watch my-task-name --scaffold-run-id 1
synthtask smoldata review my-task-name --wait --scaffold-run-id 1

# You can also record an external status explicitly if needed.
synthtask submission record 1 --platform smoldata --external-id abc-123 \
  --status bad_grading_weak --pass-rate 1.0 --revisions 2

# 10. write durable learning events for later A/B tests
synthtask learn add --scope-type submission --scope-id 1 \
  --label weak-grader --detail "public cases did not cover stateful edge cases"

# 11. see controller state and queued next actions
synthtask pipeline status
```

`synthtask pipeline run` can advance one task through the same gates until it reaches a
real blocker:

```bash
synthtask pipeline run \
  --idea-id 42 \
  --bundle-id 1 \
  --builder codex \
  --build-prompt-file /path/to/build_prompt.md \
  --verify-command "python3 -m unittest discover -s tests -v" \
  --canonical-root /path/to/canonical-task-root \
  --publish-task-name my-task-name \
  --stop-after publish
```

Passing only `--scaffold-run-id` is enough to resume an existing task: the contract is
looked up from the scaffold, and `build`/`verify`/`promote`/`publish` each skip work that is
already done. The build gate is an exclusion list — only `started`, `running` and
`build_failed` mean "no build behind this workspace" — so resuming a published scaffold
cannot re-invoke the builder. `--no-build` blocks at `build` outright.

Contracts, by contrast, are not re-entrant: drafting a second contract for an idea that
already has a live one, or starting a second scaffold for a contract that already has a
live one, is refused. Use `--force` / `--revision` when that is genuinely what you want —
the revision loop after a Smoldata rejection still works, because a `submitted` scaffold
is no longer live.

## Revisions Carry Their History

A revision used to be built from byte-identical inputs to the attempt it was replacing, so a
task rejected as `too_easy` twice got rebuilt a third time with no encoding of why.

`synthtask scaffold start` now writes `PRIOR_ATTEMPTS.md` into every workspace: per revision,
the builder used, local verification outcomes, reviewer verdicts, the Codimango status and
its triage route, and any learning notes attached to that submission. Failures record
themselves — `record_submission` writes a `smoldata-failure` learning event carrying the
status, the route, and the reviewer's own prose — so the history is populated without a
manual `learn add`. Your own `learn add` notes appear alongside it.

Two prompt tokens expose this to the builder:

| Token | Replaced with |
|---|---|
| `{{PRIOR_ATTEMPTS}}` | rendered `PRIOR_ATTEMPTS.md` for this contract |
| `{{REVISION_GUIDANCE}}` | `prompts/revision_guidance.md`, if you write one |

Both are optional for a first revision. **From revision 2 onward, `scaffold run` refuses a
prompt with no `{{PRIOR_ATTEMPTS}}` token** rather than silently rebuilding blind. Add the
token to `prompts/build_task.md` to enable it.

`prompts/revision_guidance.md` does not exist yet and is yours to write — it is the place to
say what a `too_easy` or `bad_grading_weak` route should actually change. The harness threads
it in when the file exists and is not a `<!-- TODO` placeholder, and stays silent otherwise.

## Unattended Sweeps

`synthtask sweep` is the cron entry point. It does exactly two things: re-polls Codimango
for submissions whose validation has not settled, and advances scaffolds whose contract
opted in. It never drafts a contract, starts a scaffold, invokes a builder, records an
audit verdict, or decides how to revise a rejected task — those stay human calls and are
reported as `waiting`.

```bash
synthtask settings set 1 \
  --verify-command "python3 -m unittest discover -s tests" \
  --canonical-root /path/to/canonical-task-root \
  --publish-task-name my-task-name \
  --auto-advance

synthtask sweep --dry-run     # show the dispatch plan
synthtask sweep               # poll + advance
```

Polling is ungated: it only records external truth, so it runs for every unsettled
submission. `--auto-advance` gates the mutating stages (`verify`, `promote`, `publish`,
`smoldata`) and is off by default, so installing the cron changes nothing until a
contract opts in.

Install the hourly job with:

```cron
17 * * * * /path/to/synthtask-pipeline/tools/cron_sweep.sh
```

The wrapper restores the `PATH` cron does not provide (`codimango` lives under
`~/.local/bin`), rotates `~/logs/synthtask-sweep.log` at 5 MB, and exits non-zero only on
a harness fault — a blocked task is the normal resting state.

## Where Smoldata Fits

Smoldata is the external validation and feedback gate, not the source of task ideas and
not the local build harness.

```text
local harness:
  discovery -> ideas -> contract -> scaffold -> local verifier -> adversarial review

external validation:
  publish task repo commit -> Codimango ingestion -> Smoldata/Codimango agents run
  -> Agentic Full-Task Review

feedback loop:
  Smoldata result -> triage label -> targeted revision -> local verifier -> resubmit
```

The installed `codimango` CLI exposes inspection, watch, rerun, trial artifact, and
Agentic Full-Task Review commands. It does not expose task creation in this harness, so
the pipeline now automates the available ingestion path: copy the promoted canonical task
into your Codimango task repository, commit/push it, and record the commit-addressed
GitHub URL plus an inventory digest.

```bash
synthtask publish run 1 --task-name my-task-name
synthtask smoldata watch my-task-name --scaffold-run-id 1
synthtask smoldata review my-task-name --wait --scaffold-run-id 1
synthtask smoldata rerun my-task-name
synthtask smoldata submit-collection smol-col-... /path/to/canonical-task-root \
  --task-name my-task-name --scaffold-run-id 1
```

Collection submission uses the contributor API directly. Set `SMOLDATA_API_KEY` and,
optionally, `SMOLDATA_URL`, or put them in `~/.smoldata-env`. The command packages exactly
one top-level task directory into a deterministic `.tar.gz`, adds the requested
`collectionId`, and sends an idempotency key derived from the archive digest.

By default `synthtask publish run` uses `SYNTH_TASK_REMOTE`, or the sibling
`/data/repos/ananyajain-tbench` remote when present. It publishes through a temporary
clone or GitHub API fallback, so it does not modify a dirty benchmark checkout.

Smoldata feedback is mapped into controller routing:

Failure classification reads Codimango's machine-readable `monotoneFailure` field first and
falls back to matching the prose. A failure that neither path recognises becomes
`failed_unclassified` (or `failed_unclassified:<code>` for an unknown machine code) rather
than being flattened into `rejected` — so a change in Codimango's vocabulary shows up as a
new status instead of silently looking like a deliberate rejection.

| Smoldata signal | Pipeline route |
|---|---|
| `accepted` | done |
| `pending` / `published` / `draft` / `unknown` | poll again |
| `failed_unclassified` | manual triage — classification needs updating |
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

Scaffold construction uses the same principle. `synthtask scaffold start` creates a fresh
workspace with `TASK_CONTRACT.json`, `TASK_CONTRACT.md`, controller notes, and empty
`task/`, `logs/`, `reviews/`, and `verification/` directories. Builders work only inside
that workspace. `synthtask scaffold promote` is the only command that copies staged task
files into a canonical output directory.

Any per-generator number in `synthtask report` is only trustworthy because of this.

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
