#!/usr/bin/env python3
"""Read-only GitHub coordinator: rebuild a public status snapshot from issues and PRs."""
import json, os, urllib.request, urllib.parse
from datetime import datetime, timezone

REPO=os.getenv("GITHUB_REPOSITORY","cdut007/OpenPvsNP")
TOKEN=os.getenv("GITHUB_TOKEN","")
API="https://api.github.com"
def get(path):
    headers={"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}
    if TOKEN: headers["Authorization"]="Bearer "+TOKEN
    req=urllib.request.Request(API+path,headers=headers)
    with urllib.request.urlopen(req,timeout=30) as r: return json.load(r)

def pages(path):
    out=[]
    for page in range(1,6):
        sep="&" if "?" in path else "?"
        rows=get(path+sep+urllib.parse.urlencode({"per_page":100,"page":page}))
        out.extend(rows)
        if len(rows)<100: break
    return out

def main():
    issues=[x for x in pages(f"/repos/{REPO}/issues?state=all") if "pull_request" not in x]
    prs=pages(f"/repos/{REPO}/pulls?state=all")
    counts={}
    for x in issues:
        state=x["state"]
        counts[state]=counts.get(state,0)+1
    report={
      "generated_at":datetime.now(timezone.utc).isoformat(),
      "repository":f"https://github.com/{REPO}",
      "notice":"Activity metadata only. Issue/PR state, AI consensus, CI, and benchmarks do not verify mathematical correctness.",
      "issues":{"total":len(issues),"by_state":counts,"items":[{"number":x["number"],"title":x["title"],"state":x["state"],"url":x["html_url"],"updated_at":x["updated_at"]} for x in issues]},
      "pull_requests":{"total":len(prs),"items":[{"number":x["number"],"title":x["title"],"state":x["state"],"draft":x["draft"],"url":x["html_url"],"updated_at":x["updated_at"]} for x in prs]}
    }
    os.makedirs("reports",exist_ok=True)
    with open("reports/project-status.json","w") as f: json.dump(report,f,indent=2)
    lines=["# OpenPvsNP — live project activity","",f"Generated: {report['generated_at']}","","> This is an activity snapshot, not a mathematical verification report.","","## Issues","",f"Total: **{len(issues)}**",""]
    for x in issues:
        lines.append(f"- [#{x['number']} {x['title']}]({x['html_url']}) — {x['state']}; updated {x['updated_at']}")
    lines += ["","## Pull requests","",f"Total: **{len(prs)}**",""]
    for x in prs:
        lines.append(f"- [PR #{x['number']}: {x['title']}]({x['html_url']}) — {x['state']}{' (draft)' if x['draft'] else ''}")
    lines += ["","## Integrity note","","A task marked completed, a merged pull request, passing CI, a benchmark, or agreement among agents is not proof of P=NP or P≠NP. Claims require complete mathematical arguments and independent expert review.",""]
    with open("reports/PROJECT_STATUS.md","w") as f: f.write("\n".join(lines))
    print(f"Snapshot: {len(issues)} issues, {len(prs)} pull requests")
if __name__=="__main__": main()
