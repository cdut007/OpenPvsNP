# Research Task Queue

The canonical machine-readable tasks are in `tasks/queue/*.json`. Issues may mirror these tasks for convenient assignment and discussion. Always record the task file and commit version used.

## Initial tasks
- `FOUNDATIONS-001`: Formalize a precise encoding and standard definitions needed for 3-SAT complexity claims.
- `SURVEY-001`: Produce a cited survey of standard P, NP, NP-completeness definitions and relevant known results.
- `COMPLEXITY-001`: Create an adversarial checklist and worked audits for hidden exponential costs in proposed SAT algorithms.
- `RESEARCH-001`: Independently investigate candidate deterministic 3-SAT approaches and report exact theorem statements or proof gaps.

## Targeted audits from the external research commons
- `CRT-INVERSE-AUDIT-001`: Independently audit the SAT grid inverse, Laurent-support, exact-root-count, and promise-gap coNP-hardness claims.
- `AFFINE-ORBIT-001`: Audit the affine-orbit averaging theorem, uniformity and bit complexity, and its relation to the separate width-three threshold claim.
- `QSEL-MODEL-AUDIT-001`: Formalize and audit the global selection primitive; separate its augmented model from standard quantum complexity classes.

These are audit tasks, not endorsements. The linked commons entries are unverified leads, and a no-result or precise obstruction is an acceptable outcome.

## Task lifecycle
`open → claimed → submitted → reviewing → verified` or `rejected / needs_revision / blocked`.

A task is not mathematically verified merely because a worker completed it or a pull request passed CI. A maintainer must record the review scope and evidence. Multiple workers may independently investigate the same task; claims should be coordinated through issue comments or an external scheduler with leases.

## Propose a task
Open a GitHub issue with:
- precise question and definitions;
- known assumptions and references;
- expected artifact;
- acceptance and falsification criteria;
- dependencies.