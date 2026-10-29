"""Writes library/counts.json: how often each bundle was downloaded, every version summed.

Run by .github/workflows/counts.yml (daily, on each release, and by hand). Reads this repo's
releases through the GitHub API with the workflow's own token; Pie UI reads the file with the index
and shows the counts in its bundle library. Standard library only.

A bundle version is the release tagged <slug>-v<version>, and its download is the asset <slug>.zip
(see Pie UI's tools/library_core.py). Anything else on a release is not counted.
"""
import datetime
import json
import os
import pathlib
import re
import sys
import urllib.request

TAG = re.compile(r"^([a-z0-9-]+)-v([0-9]+)$")


def releases(repo, token):
    page, out = 1, []
    while True:
        req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases?per_page=100&page={page}",
                                     headers={"Accept": "application/vnd.github+json",
                                              "Authorization": f"Bearer {token}",
                                              "X-GitHub-Api-Version": "2022-11-28"})
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.load(r)
        out += batch
        if len(batch) < 100:
            return out
        page += 1


def counts(rels):
    """{slug: downloads} from a list of GitHub release objects."""
    out = {}
    for rel in rels:
        m = TAG.match(rel.get("tag_name") or "")
        if not m or rel.get("draft"):
            continue
        slug = m.group(1)
        for a in rel.get("assets") or []:
            if a.get("name") == f"{slug}.zip":
                out[slug] = out.get(slug, 0) + int(a.get("download_count") or 0)
    return out


def main():
    repo, token = os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"]
    path = pathlib.Path("library/counts.json")
    new = counts(releases(repo, token))
    try:
        old = json.loads(path.read_text(encoding="utf-8")).get("downloads")
    except (OSError, ValueError, AttributeError):
        old = None
    if old == new:
        print("Counts unchanged.")
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {"format": 1,
           "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "downloads": dict(sorted(new.items()))}
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"Counts written for {len(new)} bundles.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
