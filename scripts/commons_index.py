#!/usr/bin/env python3
"""Index public P-vs-NP Commons metadata without importing research claims or code."""
from collections import Counter
from datetime import datetime, timezone
import json
import os
import re
import urllib.parse
import urllib.request

API = "https://lets-p-np-together.odedbendov814653.chatgpt.site/api/v1"
POSTS_URL = API + "/posts"
STATS_URL = API + "/stats"
LIMIT = 100
MAX_PAGES = 5
TIMEOUT = 20
OUT_JSON = "reports/external-research-index.json"
OUT_MD = "reports/EXTERNAL_RESEARCH_INDEX.md"
ID_RE = re.compile(r"^[A-Za-z0-9-]{1,80}$")


def now():
    return datetime.now(timezone.utc).isoformat()


def get_json(url):
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "OpenPvsNP-coordinator/1.0 (+https://github.com/cdut007/OpenPvsNP)",
        },
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.load(response)


def short_string(value, limit=300):
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value[:limit] if value else None


def sanitize_post(post):
    """Keep metadata only; never copy external post content or code."""
    if not isinstance(post, dict):
        return None
    post_id = short_string(post.get("id"), 80)
    if not post_id or not ID_RE.fullmatch(post_id):
        return None
    related_id = short_string(post.get("related_id"), 80)
    if related_id and not ID_RE.fullmatch(related_id):
        related_id = None
    return {
        "id": post_id,
        "title": short_string(post.get("title"), 500) or "(untitled)",
        "kind": short_string(post.get("kind"), 80),
        "track": short_string(post.get("track"), 120),
        "status": short_string(post.get("status"), 80) or "unknown",
        "related_id": related_id,
        "created_at": short_string(post.get("created_at"), 80),
        "updated_at": short_string(post.get("updated_at"), 80),
        "model": short_string(post.get("model"), 120),
        "author_id": short_string(post.get("author_id"), 120),
        "update_count": post.get("update_count") if isinstance(post.get("update_count"), int) else 0,
        "url": "https://pequalsnp.ai/research/" + urllib.parse.quote(post_id, safe="-"),
    }


def fetch_posts():
    posts = []
    cursor = None
    seen_cursors = set()
    errors = []
    for page in range(MAX_PAGES):
        params = {"limit": LIMIT}
        if cursor:
            params["cursor"] = cursor
        url = POSTS_URL + "?" + urllib.parse.urlencode(params)
        try:
            payload = get_json(url)
        except Exception as exc:
            errors.append(f"posts page {page + 1}: {type(exc).__name__}: {exc}")
            break
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            errors.append(f"posts page {page + 1}: unexpected response schema")
            break
        posts.extend(
            item for item in (sanitize_post(row) for row in payload["data"]) if item is not None
        )
        next_cursor = payload.get("next_cursor")
        if not next_cursor:
            break
        next_cursor = str(next_cursor)
        if next_cursor in seen_cursors:
            errors.append("posts pagination returned a repeated cursor")
            break
        seen_cursors.add(next_cursor)
        cursor = next_cursor
    return posts, errors


def fetch_stats():
    try:
        stats = get_json(STATS_URL)
        if not isinstance(stats, dict):
            raise ValueError("unexpected stats response schema")
        allowed = ("threads", "in_progress", "needs_review", "contributors", "updates")
        return {key: stats.get(key) for key in allowed if isinstance(stats.get(key), int)}, None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def cluster_roots(posts):
    by_id = {post["id"]: post for post in posts}
    roots = {}
    for post in posts:
        current = post["id"]
        visited = set()
        while current in by_id and by_id[current].get("related_id"):
            parent = by_id[current]["related_id"]
            if parent not in by_id or parent in visited or parent == current:
                break
            visited.add(current)
            current = parent
        roots[post["id"]] = current
    return roots


def build_markdown(report):
    posts = report.get("posts", [])
    roots = cluster_roots(posts)
    clusters = {}
    for post in posts:
        clusters.setdefault(roots[post["id"]], []).append(post)
    for members in clusters.values():
        members.sort(key=lambda item: item.get("updated_at") or "", reverse=True)

    stats = report.get("stats") or {}
    lines = [
        "# External Research Commons — metadata index",
        "",
        f"Generated: {report.get('generated_at')}",
        f"Source status: **{report.get('source_status', 'unknown')}**",
        f"Source: {POSTS_URL}?limit={LIMIT}",
        "",
        "> Metadata only. External posts, AI outputs, finite experiments, and update counts are not mathematical verification.",
        "> This index excludes post bodies, code blocks, credentials, and any claim of proof status beyond the source's own label.",
        "",
    ]
    if report.get("source_status") != "ok":
        lines += [
            f"> **Feed warning:** {report.get('source_error') or 'The most recent feed fetch was incomplete.'}",
            f"> Last successful fetch: {report.get('last_successful_fetch') or 'not available'}",
            "",
        ]
    if stats:
        lines += [
            "## Source-reported activity",
            "",
            " | ".join(f"{key}: **{value}**" for key, value in stats.items()),
            "",
        ]
    statuses = Counter(post.get("status", "unknown") for post in posts)
    tracks = Counter(post.get("track") or "unspecified" for post in posts)
    lines += [
        "## Indexed metadata",
        "",
        f"- Threads indexed: **{len(posts)}**",
        f"- Related clusters: **{len(clusters)}**",
        "- Status labels: " + ", ".join(f"{key}={value}" for key, value in sorted(statuses.items())),
        "- Research tracks: " + ", ".join(f"{key}={value}" for key, value in sorted(tracks.items())),
        "",
        "## Research clusters",
        "",
    ]
    ordered = sorted(
        clusters.items(),
        key=lambda pair: max((p.get("updated_at") or "") for p in pair[1]),
        reverse=True,
    )
    for root_id, members in ordered:
        root_post = next((p for p in members if p["id"] == root_id), members[0])
        lines.append(f"### {root_post['title']}")
        lines.append("")
        lines.append(f"Cluster ID: {root_id} · {len(members)} thread(s)")
        lines.append("")
        for post in members:
            model = f" · model: {post['model']}" if post.get("model") else ""
            updates = f" · updates: {post['update_count']}" if post.get("update_count") else ""
            lines.append(
                f"- [{post['title']}]({post['url']}) — {post['status']}; "
                f"track: {post.get('track') or 'unspecified'}; "
                f"updated: {post.get('updated_at') or 'unknown'}{model}{updates}"
            )
        lines.append("")
    lines += [
        "## Review policy",
        "",
        "- Treat every external item as an unverified lead until its definitions, reductions, bit complexity, edge cases, and proof steps are independently checked.",
        "- Cluster membership indicates a source-reported relationship, not correctness or equivalence.",
        "- Do not promote a result based on model identity, popularity, contributor count, or finite test cases.",
        "",
    ]
    return "\n".join(lines)


def main():
    os.makedirs("reports", exist_ok=True)
    generated_at = now()
    previous = {}
    try:
        with open(OUT_JSON, encoding="utf-8") as handle:
            previous = json.load(handle)
    except (OSError, ValueError):
        pass

    posts, post_errors = fetch_posts()
    stats, stats_error = fetch_stats()
    if posts:
        status = "ok" if not post_errors else "partial"
        report = {
            "generated_at": generated_at,
            "last_successful_fetch": generated_at if status == "ok" else previous.get("last_successful_fetch"),
            "source_status": status,
            "source": POSTS_URL,
            "notice": "Metadata only; external claims have not been verified by OpenPvsNP.",
            "stats": stats if stats is not None else previous.get("stats"),
            "stats_error": stats_error,
            "source_error": "; ".join(post_errors) if post_errors else None,
            "posts": posts,
        }
    else:
        report = dict(previous) if previous else {
            "source": POSTS_URL,
            "notice": "Metadata only; external claims have not been verified by OpenPvsNP.",
            "stats": None,
            "posts": [],
        }
        report.update({
            "generated_at": generated_at,
            "source_status": "unavailable",
            "source_error": "; ".join(post_errors) or "Feed returned no valid posts",
            "stats_error": stats_error,
        })

    with open(OUT_JSON, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    with open(OUT_MD, "w", encoding="utf-8") as handle:
        handle.write(build_markdown(report))
    cluster_count = len(set(cluster_roots(report.get("posts", [])).values()))
    print(
        f"Commons index: {len(report.get('posts', []))} threads; "
        f"status={report.get('source_status')}; clusters={cluster_count}"
    )


if __name__ == "__main__":
    main()
