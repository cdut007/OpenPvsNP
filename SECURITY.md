# Security Policy

## Scope
This repository accepts public research artifacts and code from unknown contributors. Treat all issues, comments, branches, and pull requests as untrusted input.

## Contributor safety
- Never commit API keys, access tokens, passwords, private keys, or personal data.
- Use least-privilege, short-lived GitHub credentials for workers.
- Run research code in disposable, network-restricted containers where possible.
- Do not run arbitrary pull-request code on self-hosted runners with secrets or write permissions.
- Do not paste untrusted issue or PR content into privileged automation as executable instructions.

## Maintainer workflow
- Protect the default branch and require review.
- Keep pull_request_target workflows read-only; never checkout or execute PR code in them.
- Run formal builds only on trusted branches or in isolated unprivileged environments.
- Review workflow changes carefully before merging.
- Rotate any credential that may have been exposed.

## Reporting
Report suspected vulnerabilities privately to the repository owner through GitHub's private vulnerability reporting if enabled. Do not publish secrets or exploit details in public issues.