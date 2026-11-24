# Research Roadmap

## Stage 0 — Establish foundations
- Fix encodings and deterministic machine models.
- Formalize basic syntax and semantics of 3-CNF formulas.
- Document standard definitions of P, NP, reductions, and NP-completeness.
- Build an auditable bibliography of established results.

## Stage 1 — Audit candidate approaches
- Require every proposed algorithm to specify all steps.
- Search for hidden exponential branching, state spaces, advice, or preprocessing.
- Translate complexity claims into explicit recurrences and bit-operation bounds.
- Record the first unresolved or invalid step.

## Stage 2 — Formalization
- Formalize definitions and established lemmas in Lean.
- Track imported axioms and theorem dependencies.
- Avoid encoding the desired conclusion as an assumption.

## Stage 3 — Independent exploration
- Assign independent agents to attempt proofs and adversarial audits.
- Encourage counterexamples, lower-bound obstacles, and negative results.
- Preserve failed approaches with enough detail to prevent repeated work.

## Stage 4 — Candidate proof review
- Freeze a candidate version and all dependencies.
- Obtain independent review from complexity theorists.
- Verify formalization against standard definitions.
- Publish a complete paper and reproducibility package.

No stage implies that a resolution is likely or imminent. The problem remains open.