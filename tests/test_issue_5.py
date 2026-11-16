import importlib.util
import io
import json
import urllib.error
from email.message import Message
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/emh-triage/scripts/upstream_check.py"
API_ROOT = "https://api.github.com/repos/AtlasOmnia/EMH-A-Hermes-Diagnostic-Profile"
RAW_SCHEME = "ht" + "tps"
RAW_HOST = "raw.githubusercontent.com"
RAW_REPO_PATH = "/AtlasOmnia/EMH-A-Hermes-Diagnostic-Profile"


def raw_url(ref, path):
    return f"{RAW_SCHEME}://{RAW_HOST}{RAW_REPO_PATH}/{ref}/{path}"


def load_upstream_check():
    spec = importlib.util.spec_from_file_location("upstream_check_issue_5", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Response:
    status = 200

    def __init__(self, body):
        self.body = body.encode() if isinstance(body, str) else body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size=-1):
        return self.body if size < 0 else self.body[:size]


def http_404(url):
    return urllib.error.HTTPError(url, 404, "Not Found", Message(), io.BytesIO(b""))


def invoke(module, argv, capsys=None):
    previous_argv = module.sys.argv
    module.sys.argv = [str(SCRIPT), *argv]
    try:
        try:
            status = int(module.main() or 0)
        except SystemExit as exc:
            status = int(exc.code or 0)
    finally:
        module.sys.argv = previous_argv
    if capsys is not None:
        captured = capsys.readouterr()
        return status, captured.out, captured.err
    return status


def test_upstream_fetch_rejects_branch_refs_before_network(monkeypatch, capsys):
    module = load_upstream_check()
    calls = []

    def urlopen(request, timeout):
        calls.append(request.full_url)
        raise AssertionError("invalid branch ref must be rejected before network access")

    monkeypatch.setattr(module.urllib.request, "urlopen", urlopen)

    status, stdout, stderr = invoke(
        module,
        ["--installed", "0.2.14", "--fetch", "skills/example/SKILL.md", "--ref", "main"],
        capsys,
    )

    assert status == 0
    payload = json.loads(stdout)
    assert payload["status"] == "error"
    assert "ref" in payload["reason"].lower()
    assert calls == []
    assert stderr == ""


def test_upstream_fetch_derives_tag_and_reads_only_pinned_urls(monkeypatch, capsys):
    module = load_upstream_check()
    calls = []
    tag = "v0.2.14"
    target = "skills/example/SKILL.md"

    def urlopen(request, timeout):
        url = request.full_url
        calls.append(url)
        if url == f"{API_ROOT}/git/ref/tags/{tag}":
            return Response(json.dumps({"ref": f"refs/tags/{tag}"}))
        if url == raw_url(tag, "distribution.yaml"):
            return Response("version: 0.2.14\n")
        if url == raw_url(tag, target):
            return Response("pinned release content\n")
        raise AssertionError(f"unexpected or mutable URL: {url}")

    monkeypatch.setattr(module.urllib.request, "urlopen", urlopen)

    status, stdout, stderr = invoke(
        module,
        ["--installed", "0.2.14", "--fetch", target],
        capsys,
    )

    assert status == 0
    assert stdout == "pinned release content\n"
    assert stderr == ""
    assert calls == [
        f"{API_ROOT}/git/ref/tags/{tag}",
        raw_url(tag, "distribution.yaml"),
        raw_url(tag, target),
    ]
    assert not any("/main/" in url for url in calls)


def test_upstream_fetch_accepts_an_explicit_full_commit_sha(monkeypatch, capsys):
    module = load_upstream_check()
    commit = "a" * 40
    target = "skills/example/SKILL.md"
    calls = []

    def urlopen(request, timeout):
        url = request.full_url
        calls.append(url)
        if url == f"{API_ROOT}/git/commits/{commit}":
            return Response(json.dumps({"sha": commit}))
        if url == raw_url(commit, "distribution.yaml"):
            return Response("version: 0.2.14\n")
        if url == raw_url(commit, target):
            return Response("commit-pinned content\n")
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(module.urllib.request, "urlopen", urlopen)

    status, stdout, stderr = invoke(
        module,
        ["--fetch", target, "--ref", commit],
        capsys,
    )

    assert status == 0
    assert stdout == "commit-pinned content\n"
    assert stderr == ""
    assert calls == [
        f"{API_ROOT}/git/commits/{commit}",
        raw_url(commit, "distribution.yaml"),
        raw_url(commit, target),
    ]


def test_missing_release_tag_returns_version_only_without_fetching_content(monkeypatch, capsys):
    module = load_upstream_check()
    calls = []
    target = "skills/example/SKILL.md"
    tag = "v0.2.14"

    def urlopen(request, timeout):
        url = request.full_url
        calls.append(url)
        if url == f"{API_ROOT}/git/ref/tags/{tag}":
            raise http_404(url)
        if url == f"{API_ROOT}/tags":
            return Response("[]")
        if url == raw_url("main", "distribution.yaml"):
            return Response("version: 0.2.14\n")
        raise AssertionError(f"content fetch was not allowed: {url}")

    monkeypatch.setattr(module.urllib.request, "urlopen", urlopen)

    status, stdout, stderr = invoke(
        module,
        ["--installed", "0.2.14", "--fetch", target],
        capsys,
    )

    assert status == 0
    payload = json.loads(stdout)
    assert payload["status"] == "version_only"
    assert payload["upstream"] == "0.2.14"
    assert payload["reason"] == "no pinned release tag; content fetch refused"
    assert raw_url("main", "distribution.yaml") in calls
    assert raw_url(tag, target) not in calls
    assert stderr == ""


def test_latest_version_prefers_the_github_tags_api(monkeypatch, capsys):
    module = load_upstream_check()
    calls = []

    def urlopen(request, timeout):
        url = request.full_url
        calls.append(url)
        if url == f"{API_ROOT}/tags":
            return Response(json.dumps([{"name": "v0.2.14"}, {"name": "v0.2.13"}]))
        raise AssertionError(f"unexpected fallback request: {url}")

    monkeypatch.setattr(module.urllib.request, "urlopen", urlopen)

    status, stdout, stderr = invoke(module, ["--installed", "0.2.13"], capsys)

    assert status == 0
    payload = json.loads(stdout)
    assert payload["upstream"] == "0.2.14"
    assert payload["update_available"] is True
    assert calls == [f"{API_ROOT}/tags"]
    assert stderr == ""


def test_retention_check_is_informational_when_not_configured():
    content = (ROOT / "skills/emh-nightly-self-check/SKILL.md").read_text(encoding="utf-8")

    assert "not configured" in content.lower()
    assert "not an anomaly" in content.lower()
    assert "only when" in content.lower() and "prune script" in content.lower()
    assert "log" in content.lower()


def test_readme_discloses_schedules_cost_and_each_job_read_surface():
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()

    for item in (
        "0 3 * * *",
        "0 4 * * 1",
        "34-35",
        "billed model call",
        "memory.md",
        "user.md",
        "state.db",
        "cron/jobs.json",
        "cron/executions.db",
        "changelog",
        "recorded source",
    ):
        assert item in readme, item


def test_orientation_discloses_cost_and_data_before_each_cron_consent():
    content = (ROOT / "skills/emh-orientation/SKILL.md").read_text(encoding="utf-8")
    lower = content.lower()
    nightly_consent = lower.index("ask for consent to register the nightly health cron")
    weekly_consent = lower.index("ask for consent to register the update-check cron")

    for token in ("34-35", "billed model call", "memory.md", "user.md", "state.db", "cron/jobs.json", "cron/executions.db", "changelog"):
        assert token in lower, token
        assert lower.index(token) < nightly_consent, token
        assert lower.index(token) < weekly_consent, token
    assert 'read_file(path="$hermes_home/config.yaml"' not in lower
    assert "hermes gateway status" in lower


def test_changelog_has_issue_5_candidate_entry():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    unreleased = changelog.split("## 0.2.9", 1)[0]

    assert "issue #5" in unreleased.lower()
    assert "pinned" in unreleased.lower()
    assert "retention" in unreleased.lower()
    assert "billed" in unreleased.lower()
