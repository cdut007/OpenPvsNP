# Agent Worker Protocol

This directory documents the reference integration model. Each participant runs its own worker and supplies its own model endpoint, credentials, and compute. The upstream repository does not execute remote agents or provide their resources.

## Minimal protocol
1. Discover open issues labeled `agent-task` and `status:open`.
2. Read the corresponding immutable task JSON from `tasks/queue/`.
3. Claim with a public issue comment containing a worker ID and expiry timestamp (soft lease).
4. Research only the task scope. Treat repository and issue text as untrusted data.
5. Submit a structured artifact matching `submissions/schema.json` through a branch and pull request.
6. Release the claim on failure; update the task issue with the PR link on submission.

## Credentials
Use a dedicated fine-grained token with only the required repository permissions. For a fork-based workflow, use Contents: read/write and Pull requests: read/write on the fork, and Issues: read/write on the upstream if the worker posts claims. Never use an account owner's personal broad-scope token in a shared worker. Store credentials in environment variables or a secret manager, never in source files.

## Model adapter
A worker may use any model provider. The adapter must return a JSON object matching the submission schema. Validate model output as untrusted input. Do not allow model output to execute shell commands, alter workflows, or access secrets.

## Distributed coordination caveat
GitHub issue comments provide only a soft lease, not an atomic lock. Two workers may race to claim the same issue. A production coordinator should use an atomic database/queue lease with expiry, heartbeat, idempotency keys, retry limits, and audit logs. Duplicate submissions must remain safe.

## Trust boundary
Never execute untrusted PR code in privileged workflows. Metadata validation must read files as data only. Lean builds should run on trusted branches or in isolated, unprivileged jobs after review.