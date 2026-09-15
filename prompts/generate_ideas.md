You are generating candidate benchmark task ideas for the AAI Research Papers to
Tasks track.

Seed paper: {{SEED_TITLE}}
Seed slug: {{SEED_SLUG}}

Use the paper only as a source of failure modes and assumptions. Do not propose
reimplementing the paper, reproducing its experiments, building a generic trading bot,
or tuning a strategy for alpha. A good idea breaks one load-bearing assumption and
turns that break into a concrete coding task with a hidden, implementation-independent
binary verifier.

Seed assumptions and available data:

{{ASSUMPTIONS}}

Generate exactly {{N_IDEAS}} distinct ideas. Each idea must satisfy all constraints:

1. The task is a software engineering task that can be scaffolded with a Dockerfile,
   `task.toml`, `instruction.md`, public fixtures, hidden tests, and a reference
   solution.
2. The reward is binary pass/fail. Do not propose continuous rewards, weighted scores,
   threshold chasing, leaderboard optimization, or subjective human judgement.
3. The solver-facing instructions must be concise and must not reveal hidden cases,
   thresholds, oracle mechanics, exact objective weights, or evaluation internals.
4. The verifier must be independent of the reference solution. Prefer semantic oracles,
   metamorphic cases, randomized hidden fixtures, mutation tests, and edge cases that
   catch shortcut implementations.
5. Use real or realistic public-domain inputs when possible. Synthetic data is allowed
   only for protocol-correctness stress cases, and the idea must explain why the data is
   market-shaped rather than toy.
6. Avoid artificial difficulty such as arbitrary memory limits, token limits, confusing
   prose, excessive file formats, or overspecified implementation plans.
7. The task should be hard because it requires preserving causal time, provenance,
   market-execution semantics, state consistency, or adversarial robustness, not because
   it hides a trick.

Diversity requirements:

- At least one idea should target backtest leakage or time-consistent splits.
- At least one idea should target execution semantics such as fills, cash, fees,
  invalid orders, or survivorship handling.
- At least one idea should target agent memory/retrieval provenance under stale,
  conflicting, or future-dated evidence.
- Do not produce near-duplicates with renamed market data fields.

Write only valid JSON to `{{OUTPUT_PATH}}` with this shape:

{
  "ideas": [
    {
      "title": "short lowercase handle",
      "statement": "one paragraph describing what the agent must build, without revealing hidden verifier mechanics",
      "assumption_broken": "which seed assumption is broken and why this creates a hard task",
      "difficulty_claim": "why a frontier coding agent is unlikely to one-shot this without robust reasoning",
      "dataset_ref": "real or realistic dataset source and what is visible to the solver"
    }
  ]
}

The JSON must contain exactly {{N_IDEAS}} ideas and no markdown.
