from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIENTATION = ROOT / "skills/emh-orientation/SKILL.md"
NIGHTLY_SELF_CHECK = ROOT / "skills/emh-nightly-self-check/SKILL.md"
CHANGELOG = ROOT / "CHANGELOG.md"


def test_orientation_uses_explicit_default_profile_for_cron_and_channel_detection():
    content = ORIENTATION.read_text(encoding="utf-8")

    assert "hermes --profile default cron list" in content
    assert "hermes --profile default cron status" in content
    assert "hermes --profile default status" in content
    assert "Platforms:" in content
    assert "hermes --profile default gateway status" in content
    assert "does not list messaging channels" in content.lower()


def test_orientation_uses_v0231_positional_cron_create_syntax():
    content = ORIENTATION.read_text(encoding="utf-8")
    commands = (
        'hermes --profile default cron create --name emh-nightly-self-check --deliver <channel|local> "0 3 * * *" "<self-contained canonical prompt>"',
        'hermes --profile default cron create --name emh-repo-update-check --deliver <channel|local> "0 4 * * 1" "<self-contained canonical prompt>"',
    )

    for command in commands:
        assert command in content
    assert "--schedule" not in content
    assert "--prompt-file" not in content
    assert "hermes --profile default cron remove <job-id>" in content


def test_orientation_discloses_cron_profile_and_self_contained_prompt_limits():
    content = ORIENTATION.read_text(encoding="utf-8")
    lower = content.lower()

    assert "a bare cron command targets whatever `hermes_home` the session runs in" in lower
    assert "inside an emh session, `hermes_home` is the emh profile" in lower
    assert "`hermes --profile default` explicitly targets the default store" in lower
    assert "each prompt must be self-contained" in lower
    assert "do not attach emh skills with `--skill`" in lower
    assert "emh skills are installed only in the emh profile" in lower
    assert "terminal, file" not in lower
    assert "toolsets" not in lower


def test_orientation_has_no_unsupported_cron_toolset_guarantee():
    content = ORIENTATION.read_text(encoding="utf-8").lower()

    assert "toolsets `terminal, file`" not in content
    assert "enable toolsets" not in content
    assert "hermes v0.23.1's cron cli offers no per-job toolset restriction" in content
    assert "read-only guarantee rests on the self-contained prompt" in content


def test_nightly_self_check_does_not_claim_per_job_read_only_toolsets():
    content = NIGHTLY_SELF_CHECK.read_text(encoding="utf-8").lower()

    assert "read-only toolsets `terminal, file`" not in content
    assert "toolsets `terminal, file`" not in content


def test_issue_8_is_recorded_in_release_notes():
    changelog = CHANGELOG.read_text(encoding="utf-8")
    unreleased = changelog.split("## Unreleased", 1)[1].split("## 0.2.15", 1)[0]
    lower = unreleased.lower()

    assert "### Fixed" in unreleased
    assert "issue #8" in lower
    assert "cron" in lower
    assert "channel" in lower
    assert "positional" in lower
    assert "toolset" in lower
