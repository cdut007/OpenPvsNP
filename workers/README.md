## Run one research task

This is a one-shot reference worker. It discovers the first open task issue, calls an OpenAI-compatible Chat Completions endpoint, writes a JSON artifact on a worker branch, and opens a pull request. It does not run continuously; an operator may schedule it with their own scheduler after reviewing its behavior.

1. Fork this repository, or use a dedicated bot account with explicit write access to the upstream.
2. Copy workers/.env.example to workers/.env and fill in credentials. Never commit the file.
3. Install dependencies: python -m pip install -r workers/requirements.txt
4. Export the variables in workers/.env into the process environment.
5. Run: python workers/openpvsnp/worker.py

Required GitHub permissions: Issues read/write on upstream, Pull requests read/write on upstream, and Contents read/write on the repository where the worker creates its branch. For fork mode, OPENPVSNP_PUSH_REPO must point to the fork. MODEL_BASE_URL and MODEL_API_KEY must target an OpenAI-compatible Chat Completions API.

The issue comment is only an advisory claim, not an atomic lock; concurrent workers may duplicate effort. The worker treats model output as untrusted JSON and does not execute generated code. All PRs remain unverified and require human review. Test in a disposable fork first; review the script before granting write permissions.