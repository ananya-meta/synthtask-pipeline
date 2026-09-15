Score each candidate benchmark idea on five dimensions from 1.0 to 5.0.

General rule: reward ideas that break a seed-paper assumption and can become a
realistic, binary-verifiable coding task. Penalize ideas that simply reimplement the
paper, expose the evaluator, rely on subjective grading, or create difficulty through
arbitrary limits.

Novelty:

- 1.0: Textbook exercise, generic CRUD, or direct reproduction of the paper.
- 3.0: Familiar ingredients but a task-specific composition or failure mode.
- 5.0: Distinct task shape that is unlikely to be found as a memorized benchmark or
  public tutorial.

Feasibility:

- 1.0: Requires unavailable services, ambiguous data rights, excessive compute, or
  manual judgement.
- 3.0: Buildable with careful scoping, but needs disciplined fixture and verifier design.
- 5.0: Clearly scaffoldable in a small Docker task with deterministic local verification.

Difficulty:

- 1.0: Frontier agents likely pass by following a short obvious recipe.
- 3.0: Requires handling edge cases, state, provenance, or adversarial inputs.
- 5.0: Requires sustained reasoning across interacting constraints while still having a
  fair path to a correct solution.

Interestingness:

- 1.0: Busywork, format conversion, or arbitrary puzzle.
- 3.0: Meaningful engineering problem with some real system analogue.
- 5.0: Captures a genuine bottleneck from the seed area and would teach useful lessons
  about task quality or agent limitations.

Verifiability:

- 1.0: No clean binary oracle, subjective evaluation, or leaked thresholds.
- 3.0: Verifiable with hidden cases but the oracle needs careful independence checks.
- 5.0: Strong implementation-independent verifier is natural, with hidden randomized or
  metamorphic tests and mutation resistance.

Return one JSON object matching the provided schema. Use half-point increments when
needed. The rationale should be one concise paragraph and mention the main reason to
accept or reject the idea.
