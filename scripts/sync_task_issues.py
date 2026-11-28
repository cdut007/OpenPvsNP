#!/usr/bin/env python3
"""Idempotently mirror trusted task queue JSON files into GitHub Issues."""
import glob
import json
import os
import re
import urllib.error
import urllib.request

API = "https://api.github.com"
REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]
TASK_DIR = "tasks/queue"
MARKER = "<!-- openpvsnp-task-id: {task_id} -->"
TASK_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,100}$")
TIMEOUT = 30


def request_json(method, path, payload=None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + TOKEN,
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "OpenPvsNP-task-issue-sync/1.0",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"GitHub API {method} {path} failed: HTTP {exc.code}: {detail}") from exc


def list_issues():
    rows = []
    for page in range(1, 11):
        path = f"/repos/{REPO}/issues?state=all&per_page=100&page={page}"
        batch = request_json("GET", path)
        if not isinstance(batch, list):
            raise RuntimeError("GitHub issues endpoint returned an unexpected response")
        rows.extend(row for row in batch if "pull_request" not in row)
        if len(batch) < 100:
            break
    return rows


def load_tasks():
    tasks = []
    seen = set()
    for path in sorted(glob.glob(os.path.join(TASK_DIR, "*.json"))):
        with open(path, encoding="utf-8") as handle:
            task = json.load(handle)
        task_id = task.get("task_id")
        title = task.get("title")
        objective = task.get("objective")
        if not isinstance(task_id, str) or not TASK_ID_RE.fullmatch(task_id):
            raise ValueError(f"{path}: invalid task_id")
        if task_id in seen:
            raise ValueError(f"{path}: duplicate task_id {task_id}")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{path}: missing title")
        if not isinstance(objective, str) or not objective.strip():
            raise ValueError(f"{path}: missing objective")
        seen.add(task_id)
        task["_path"] = path
        tasks.append(task)
    return tasks


def matching_issue(task_id, issues):
    marker = MARKER.format(task_id=task_id)
    prefix = f"[{task_id}]"
    for issue in issues:
        body = issue.get("body") or ""
        title = issue.get("title") or ""
        if marker in body or title.startswith(prefix):
            return issue
    return None


def bullets(values):
    if not isinstance(values, list) or not values:
        return "- Not specified"
    return "\n".join("- " + str(value) for value in values)


def issue_body(task, commit_sha):
    task_id = task["task_id"]
    marker = MARKER.format(task_id=task_id)
    refs = task.get("source_references", [])
    references = "\n".join("- " + str(ref) for ref in refs) if refs else "- None supplied"
    dependencies = ", ".join(str(x) for x in task.get("dependencies", [])) or "None"
    verification = task.get("verification", {})
    if not isinstance(verification, dict):
        verification = {}
    lines = [
        marker,
        "## Objective",
        str(task["objective"]).strip(),
        "",
        "## Scope",
        bullets(task.get("scope", [])),
        "",
        "## Deliverables",
        bullets(task.get("deliverables", [])),
        "",
        "## Acceptance criteria",
        bullets(task.get("acceptance_criteria", [])),
        "",
        "## Dependencies",
        dependencies,
        "",
        "## Source references",
        references,
        "",
        "## Verification",
        f"- Independent review required: {bool(verification.get('independent_review_required', True))}",
        f"- Lean required: {bool(verification.get('lean_required', False))}",
        "",
        "## Provenance",
        f"- Task file: {task['_path']}",
        f"- Queue revision: {commit_sha or 'not supplied'}",
        "",
        "> This issue mirrors the task JSON. Task completion, passing CI, model agreement, or finite experiments are not mathematical verification. An explicit obstruction or no-result report is acceptable when it follows the task standard.",
    ]
    return "\n".join(lines) + "\n"


def main():
    tasks = load_tasks()
    issues = list_issues()
    created = 0
    skipped = 0
    commit_sha = os.getenv("GITHUB_SHA", "")
    for task in tasks:
        task_id = task["task_id"]
        existing = matching_issue(task_id, issues)
        if existing:
            print(f"SKIP {task_id}: issue #{existing['number']} already mirrors this task ({existing['state']})")
            skipped += 1
            continue
        priority = str(task.get("priority", "normal")).lower()
        title = f"[{task_id}] {task['title'].strip()}"[:240]
        body = issue_body(task, commit_sha)
        payload = {
            "title": title,
            "body": body,
        }
        labels = task.get("labels", [])
        if isinstance(labels, list):
            allowed = [str(label) for label in labels if isinstance(label, str) and label.strip()]
            if allowed:
                payload["labels"] = allowed
        issue = request_json("POST", f"/repos/{REPO}/issues", payload)
        issues.append(issue)
        print(f"CREATED {task_id}: issue #{issue['number']} {issue['html_url']} (priority={priority})")
        created += 1
    print(f"Task issue sync complete: {created} created, {skipped} already mirrored, {len(tasks)} task files scanned.")


if __name__ == "__main__":
    main()
