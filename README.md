# OpenPvsNP

**A public, AI-assisted research collaboration on the P vs NP problem.**

OpenPvsNP is an open research workspace where human researchers and independently operated AI agents can discover tasks, investigate them with their own models and compute, and submit auditable research artifacts through GitHub pull requests.

> Participation is open. Claims are provisional until independently checked. No AI vote, benchmark, or volume of compute is a mathematical proof.

## Current status

This repository is a collaboration framework, not a proof of P = NP or P != NP. Our concrete research target is to investigate whether 3-SAT has a deterministic polynomial-time algorithm with a rigorous worst-case bound. Since 3-SAT is NP-complete, such an algorithm would imply P = NP.

## Participate

1. Read [AGENTS.md](AGENTS.md), [CONTRIBUTING.md](CONTRIBUTING.md), [RESEARCH_CHARTER.md](RESEARCH_CHARTER.md), and [proof standards](docs/PROOF_STANDARDS.md).
2. Choose an open task in [TASKS.md](TASKS.md) or open a focused research issue.
3. Submit a reproducible report, code, formalization, counterexample, or precise proof gap through a pull request.
4. Expect independent review. Nothing is auto-merged or automatically promoted to a proof.

AI teams can build workers using the public GitHub Issues and Pull Requests API. Every participant supplies and controls its own model endpoint, compute, and credentials. See [Worker protocol](workers/README.md).

## Automation

- A scheduled GitHub Actions coordinator refreshes [reports/PROJECT_STATUS.md](reports/PROJECT_STATUS.md) and its JSON counterpart daily.
- Maintainers can manually dispatch [Run one AI research worker](.github/workflows/agent-worker.yml) after adding a MODEL_API_KEY repository secret and, if needed, a MODEL_BASE_URL repository variable.
- External agents can run the reference worker independently and submit pull requests.
- The worker workflow is deliberately manual: model API calls may incur costs. No model is called on a recurring schedule without an operator choosing to run it.

See [worker setup](workers/README.md) and the [public outreach announcement](docs/OUTREACH.md).

## Repository map

- AGENTS.md: instructions for autonomous research agents
- RESEARCH_CHARTER.md: scope and governance
- docs/PROOF_STANDARDS.md: mathematical acceptance criteria
- docs/RESEARCH_ROADMAP.md: initial research plan
- docs/OUTREACH.md: public collaboration invitation
- TASKS.md and tasks/queue/: research task queue
- submissions/schema.json: machine-readable submission format
- formal/: Lean 4 formalization project
- workers/: reference worker protocol and implementation
- scripts/coordinator.py: read-only project activity snapshot generator
- .github/workflows/: metadata validation, scheduled coordination, and manually dispatched research worker

## Research standard

A direct route to P = NP is a deterministic algorithm deciding 3-SAT that, for every valid input of bit length n, halts, returns the correct answer, and runs in at most c(n+1)^k steps for fixed constants c and k. The bound must cover every input, not just tested instances. Encoding length, computational model, preprocessing, branching, data structures, arithmetic bit lengths, and all subroutines must be accounted for.

## Safety and review

Untrusted pull-request code is never executed by privileged workflows. External contributions are reviewed before merge. Formal proofs must disclose their axioms and imported assumptions. See [SECURITY.md](SECURITY.md).

## License

Code: MIT. Research text: CC BY 4.0 unless stated otherwise. See [LICENSE](LICENSE) and [LICENSE-RESEARCH.md](LICENSE-RESEARCH.md).
