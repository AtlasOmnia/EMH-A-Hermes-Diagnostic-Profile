#!/usr/bin/env python3
"""EMH upstream knowledge probe — stdlib only, read-only.

Compares the installed EMH distribution version against the published
GitHub repo, and optionally fetches one repository file from an immutable
release tag or full commit SHA. Never installs, never updates, never writes
anything. Fail-closed: network errors are a diagnostic result.

Usage:
  python3 upstream_check.py --installed 0.2.14
  python3 upstream_check.py --installed 0.2.14 --fetch skills/emh-gateway-diagnostics/SKILL.md
  python3 upstream_check.py --fetch skills/emh-gateway-diagnostics/SKILL.md --ref v0.2.14
  python3 upstream_check.py --offline --installed 0.2.14
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import quote, urlunsplit

API_BASE = "https://api.github.com/repos/AtlasOmnia/EMH-A-Hermes-Diagnostic-Profile"
RAW_HOST = "raw.githubusercontent.com"
RAW_REPO_PATH = "/AtlasOmnia/EMH-A-Hermes-Diagnostic-Profile"
DISTRIBUTION = "distribution.yaml"
TIMEOUT = 15
VERSION_PATTERN = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
TAG_PATTERN = re.compile(r"v((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))")
SHA_PATTERN = re.compile(r"[0-9a-fA-F]{40}")
PATH_PATTERN = re.compile(r"[A-Za-z0-9._/-]+")


def fetch(url, accept="text/plain"):
    request = urllib.request.Request(
        url,
        headers={"Accept": accept, "User-Agent": "emh-upstream-probe"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read().decode("utf-8", errors="replace")


def raw_url(ref, path):
    raw_path = f"{RAW_REPO_PATH}/{quote(ref, safe='')}/{path}"
    return urlunsplit(("https", RAW_HOST, raw_path, "", ""))


def version_from_distribution(text):
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("version:"):
            version = line.split(":", 1)[1].strip().strip("\"'")
            if VERSION_PATTERN.fullmatch(version):
                return version
            break
    raise ValueError("distribution version unavailable")


def version_tuple(version):
    return tuple(int(part) for part in version.split("."))


def latest_tag_version():
    payload = json.loads(fetch(f"{API_BASE}/tags", "application/vnd.github+json"))
    if not isinstance(payload, list):
        raise ValueError("malformed tag listing")
    versions = []
    for tag in payload:
        if not isinstance(tag, dict):
            continue
        name = tag.get("name")
        if not isinstance(name, str):
            continue
        match = TAG_PATTERN.fullmatch(name)
        if match:
            versions.append(match.group(1))
    if not versions:
        raise ValueError("no version tags available")
    return max(versions, key=version_tuple)


def upstream_version():
    """Prefer published version tags; use main only for version metadata fallback."""
    try:
        return latest_tag_version()
    except Exception:
        # Version-only fallback: this URL is never used to retrieve skill content.
        return version_from_distribution(fetch(raw_url("main", DISTRIBUTION)))


def valid_repo_path(path):
    if not path or PATH_PATTERN.fullmatch(path) is None or path.startswith("/"):
        return False
    return all(part not in {"", ".", ".."} for part in path.split("/"))


def valid_ref(ref):
    if not ref:
        return False
    return TAG_PATTERN.fullmatch(ref) is not None or SHA_PATTERN.fullmatch(ref) is not None


def ref_from_installed_version(version):
    if VERSION_PATTERN.fullmatch(version or "") is None:
        return ""
    return f"v{version}"


def latest_report(installed):
    upstream = upstream_version()
    return {
        "status": "ok",
        "installed": installed or "unknown",
        "upstream": upstream,
        "update_available": bool(installed) and installed != upstream,
    }


def version_only_report(installed, reason):
    try:
        upstream = upstream_version()
    except Exception:
        upstream = "unknown"
    return {
        "status": "version_only",
        "installed": installed or "unknown",
        "upstream": upstream,
        "update_available": bool(installed) and upstream != "unknown" and installed != upstream,
        "reason": reason,
    }


def error_report(reason):
    return {"status": "error", "reason": reason}


def verify_tag(tag):
    """Verify the exact Git tag and its manifest version before content retrieval."""
    try:
        ref_payload = json.loads(
            fetch(f"{API_BASE}/git/ref/tags/{quote(tag, safe='')}", "application/vnd.github+json")
        )
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None, "no pinned release tag; content fetch refused"
        raise
    if not isinstance(ref_payload, dict) or ref_payload.get("ref") != f"refs/tags/{tag}":
        return None, "release tag could not be verified; content fetch refused"
    try:
        version = version_from_distribution(fetch(raw_url(tag, DISTRIBUTION)))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None, "no pinned release tag; content fetch refused"
        raise
    expected_version = tag[1:]
    if version != expected_version:
        return None, "release tag does not match distribution.yaml version; content fetch refused"
    return version, ""


def verify_commit(commit):
    """Confirm a full SHA identifies a commit object in the official repo."""
    try:
        payload = json.loads(
            fetch(f"{API_BASE}/git/commits/{quote(commit, safe='')}", "application/vnd.github+json")
        )
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    if not isinstance(payload, dict):
        return False
    resolved_sha = payload.get("sha")
    return isinstance(resolved_sha, str) and resolved_sha.lower() == commit.lower()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed", default="", help="installed distribution version")
    parser.add_argument("--fetch", default="", help="repo-relative file to fetch from a pinned ref")
    parser.add_argument("--ref", default="", help="pinned release tag vX.Y.Z or full 40-character commit SHA")
    parser.add_argument("--offline", action="store_true", help="never touch the network")
    args = parser.parse_args()

    if args.offline:
        print(json.dumps({"status": "unavailable", "reason": "offline mode"}))
        return 0

    if args.ref and not args.fetch:
        print(json.dumps(error_report("--ref requires --fetch")))
        return 0
    if args.fetch and not valid_repo_path(args.fetch):
        print(json.dumps(error_report("invalid path")))
        return 0

    if args.fetch:
        ref = args.ref or ref_from_installed_version(args.installed)
        if not ref:
            print(json.dumps(error_report("--fetch requires --installed <version> or an explicit --ref")))
            return 0
        if not valid_ref(ref):
            print(json.dumps(error_report("invalid ref; use a vX.Y.Z release tag or a 40-character commit SHA")))
            return 0
        try:
            if TAG_PATTERN.fullmatch(ref):
                _, refusal = verify_tag(ref)
                if refusal:
                    print(json.dumps(version_only_report(args.installed, refusal)))
                    return 0
            else:
                verified = verify_commit(ref)
                if verified is None:
                    print(json.dumps(version_only_report(args.installed, "pinned commit not found; content fetch refused")))
                    return 0
                if not verified:
                    print(json.dumps(version_only_report(args.installed, "pinned commit could not be verified; content fetch refused")))
                    return 0
                try:
                    version_from_distribution(fetch(raw_url(ref, DISTRIBUTION)))
                except urllib.error.HTTPError as exc:
                    if exc.code == 404:
                        print(json.dumps(version_only_report(args.installed, "pinned commit not found; content fetch refused")))
                        return 0
                    raise
            print(fetch(raw_url(ref, args.fetch)), end="")
        except Exception as exc:
            print(json.dumps(error_report(type(exc).__name__)))
        return 0

    try:
        print(json.dumps(latest_report(args.installed)))
    except Exception as exc:  # network failures are a diagnostic result, not a crash
        print(json.dumps(error_report(type(exc).__name__)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
