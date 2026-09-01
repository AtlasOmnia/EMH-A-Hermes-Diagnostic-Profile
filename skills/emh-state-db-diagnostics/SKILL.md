---
name: emh-state-db-diagnostics
description: Use when Hermes state.db, SQLite, FTS, session-search, WAL, or session persistence failures need safe diagnosis and recovery orchestration.
version: 0.2.0
author: Jonathan Rivera
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagnostics, state-db, sqlite, fts, recovery, sessions]
    related_skills: [emh-triage, emh-update-recovery, emh-profile-session-skill-diagnostics, emh-rescue-media]
---

# EMH state database diagnostics

## Response presentation

Use the shared [EMH response reference](../emh-triage/references/response-templates.md) for normal answers: lead with **What I found**, **What it means**, **Safest next step**, **Permission needed: Yes/No**, then **Technical details**. Preserve this skill's domain workflow, evidence labels, and safety/approval rules; this presentation guidance does not replace them. Keep mutation, data-loss, recovery, and external-contact warnings in the concise answer, and keep technical proof complete and redacted.

## Overview

This skill diagnoses failures involving the canonical Hermes SQLite session store, `state.db`, and its derived FTS indexes. It is for a suspected post-update loop, `session_search` failure, malformed database error, missing schema column, blocked session persistence, unexpected WAL growth, or repair that appears to succeed and then fails again.

The central safety rule is separation: run EMH from a separate healthy profile and inspect the affected profile as a named target. Do not change EMH's own `HERMES_HOME` to the affected target, and do not use target `session_search`, session browse, or resume as a diagnostic probe. Those paths may exercise the damaged index or create a new writer.

The current runtime and installed source outrank generic guidance. The official docs are authoritative current documentation, but repair behavior must be matched to the installed Hermes version and the exact error class. Official source guidance: https://github.com/NousResearch/hermes-agent/blob/v2026.8.31/docs/state-db-recovery.md

## When to Use

Use when:

- Hermes reports `database disk image is malformed`, `file is not a database`, a b-tree error, a `no such column` error, a locked database, or failed session persistence.
- A repair appears to work until reasoning, session discovery, `/resume`, or `session_search` reaches the session store again.
- `messages_fts`, `messages_fts_trigram`, an FTS trigger, a malformed inverted index, or a `constraint failed` error appears in a session or message path.
- A recent update, concurrent CLI/gateway/cron activity, a database replacement, large WAL, filesystem change, or stale maintenance lock may be relevant.
- A user needs an evidence-labeled, redacted recovery plan rather than a blind reinstall or repeated self-repair loop.

**Don't use for:** ordinary prompt-quality, provider, or tool-call failures without any session-store evidence; a missing skill or stale context without SQLite errors; routine session cleanup, pruning, or archive management; a request to delete history; or an unscoped request to “fix Hermes.” Route those cases to the owning EMH skill. Do not use this skill to bypass approvals, to run forensic SQL against a live store, or to treat a community report as a confirmed root cause.

## Evidence collection workflow

Record **Complaint**; **Vitals**; **Differential diagnosis**; **Confirmed diagnosis**; **Treatment**; **Post-treatment verification**; and **Discharge summary or escalation packet** in that order.

1. **Contain the target identity.** Record the affected profile/home summary, installed version, install method, OS, launch surface, gateway state, and whether an interactive CLI, Desktop backend, dashboard, cron worker, or another Hermes process can write the target. Keep EMH's own profile and `HERMES_HOME` unchanged.
2. **Capture bounded vitals.** Collect only process state, gateway state, version, database/WAL size, free-space signal, and the first relevant redacted error. Do not dump transcripts, database contents, credentials, raw logs, full process arguments, or private paths.
3. **Classify evidence before treatment.** Use these mutually exclusive provisional classes:
   - **Schema migration / concurrency:** startup-time `no such column`, schema-version mismatch, migration error, or repeated lock/busy failure around simultaneous initialization. This can be related to an unsafe migration or concurrent writer, but is not confirmed by a generic “corrupt database” message.
   - **FTS-only:** errors name `messages_fts*`, FTS triggers, malformed inverted index, or a content-dependent constraint while canonical tables and `PRAGMA integrity_check` remain readable. `session_search` may be the first visible trigger. A green basic doctor result does not by itself rule this class out.
   - **Structural / WAL:** `database disk image is malformed`, `file is not a database`, canonical `sessions` or `messages` b-tree errors, failed integrity check, or a database that returns to failure after replacement because another live writer or stale sidecar remained. This is a preservation and offline-recovery case, not an FTS rebuild assumption.
4. **Label the confidence.** Use only **Observed**, **Reproduced**, **Confirmed in installed source**, **Officially documented**, **Known upstream fix**, or **Hypothesis**. A GitHub issue or Reddit comment is a lead, not a diagnosis.
5. **Freeze the first failure.** Preserve the exact error class, time window, version, active process roles, and whether the failure happened during startup, message persistence, FTS search, recovery, or update. Do not repeatedly run repair to manufacture a result.
6. **Propose the smallest treatment.** A live repair, process stop, repair command, recovery command, database promotion, restoration, configuration change, or update is a proposal until the operator gives explicit approval.

## Decision tree

1. **Is the target profile/home and current writer set known?**
   - No: collect only bounded profile, process, and gateway facts. Do not run a database command.
   - Yes: continue.
2. **Are any target writers live?**
   - Yes: HOLD. Do not repair, copy, vacuum, restore, or replace the SQLite bundle while a gateway, Desktop backend, CLI, dashboard, cron worker, or parent CLI can still write it.
   - No: continue with read-only classification evidence.
3. **Does evidence name a missing column, schema version, or startup race?**
   - Yes: classify schema migration / concurrency. Compare the installed source and version-matched upstream history before proposing an update or repair.
   - No: continue.
4. **Does evidence isolate an FTS table or trigger while canonical integrity remains readable?**
   - Yes: classify FTS-only. Prefer the supported `sessions repair` path after approval; do not drop tables or triggers manually.
   - No: continue.
5. **Does a structural integrity check fail, or do canonical tables report malformed/b-tree errors?**
   - Yes: classify structural / WAL. Preserve the source and reported backup, then use the offline `sessions recover` workflow after approval. Do not keep retrying in-place repair.
   - No: retain competing hypotheses and produce a redacted escalation packet instead of guessing.
6. **Did a repair pass but the original symptom recur?**
   - Recheck writer ownership, the exact error class, database bundle continuity, and whether FTS-only versus structural evidence was conflated. A successful command is not post-treatment verification.

## Exact commands and tool calls

Run only the smallest relevant subset. Treat the affected database, its session content, and all log paths as private until redacted.

### Read-only allowlist

- `hermes --version`
- `HERMES_HOME="<target-home>" hermes status --all`
- `HERMES_HOME="<target-home>" hermes gateway status`
- `hermes profile show <target-profile>`
- `hermes profile info <target-profile>`
- `process(action="list")`
- `read_file(path="<redacted-log-path>", offset=1, limit=200)`
- `sqlite3 "<consistent-snapshot.db>" "PRAGMA integrity_check;"`
- `sqlite3 "<consistent-snapshot.db>" "PRAGMA quick_check;"`
- `sqlite3 "<consistent-snapshot.db>" "SELECT 'sessions', COUNT(*) FROM sessions UNION ALL SELECT 'messages', COUNT(*) FROM messages;"`

A snapshot must be consistent before it is treated as evidence. Do not point a SQLite shell at a live WAL-mode target while other processes may write it. Do not call target `session_search`, browse, resume, or message-send paths merely to see whether they fail.

### Approval-gated reproductions and mutations

The following require explicit approval, verified backup evidence, rollback, an abort condition, and post-change verification:

- Stop every target writer, including the gateway, Desktop/backend, dashboard, cron workers, and the interactive parent CLI. Run recovery from a fresh shell with no Hermes session open against that target.
- Run the supported repair flow only after writers are stopped:

  ```bash
  HERMES_HOME="<target-home>" hermes gateway stop
  HERMES_HOME="<target-home>" hermes gateway status
  HERMES_HOME="<target-home>" hermes sessions repair --check-only
  HERMES_HOME="<target-home>" hermes sessions repair
  HERMES_HOME="<target-home>" hermes sessions repair --check-only
  ```

  For a loaded target service, proceed only after the target-scoped stop reports `✓ Service stopped` or `✓ Stopped hermes-gateway service`, and the target-scoped status confirms the service is not loaded. If it reports `Gateway PID … did not exit gracefully; sent SIGKILL`, any stop error, or a still-loaded target service, HOLD and preserve the result instead of running repair. If the target gateway was already not loaded, record that observed state before continuing.

- If in-place repair fails, inspect and recover into a new database without replacing the active source automatically:

  ```bash
  HERMES_HOME="<target-home>" hermes sessions recover \
    --source "<reported-backup-or-snapshot>" --inspect-only
  HERMES_HOME="<target-home>" hermes sessions recover \
    --source "<reported-backup-or-snapshot>" --output recovered-state.db
  ```

- Restore, install, promote, or replace a recovered database only after its report is reviewed and the operator separately approves that exact target action.

`state.db`, `state.db-wal`, and `state.db-shm` are one SQLite bundle. Never independently copy them with `cp`, delete a sidecar to “see what happens,” replace one member while another is live, or use raw SQL surgery as a shortcut. The supported repair and recovery commands own their snapshot and promotion safeguards.

## Safety and approval boundaries

**Read-only first.** Never silently stop or restart processes, run `doctor --fix`, repair or recover a database, restore a snapshot, replace a SQLite bundle, update Hermes, change `HERMES_HOME`, browse/resume target sessions, invoke target `session_search`, delete sidecars, vacuum, alter journal mode, or modify configuration.

- Obtain **explicit approval** immediately before every mutating or target-touching recovery stage. Approval to diagnose does not authorize treatment.
- Require a **verified backup** or a source-preservation plan, a credible **rollback**, an exact target identity, all-writer quiescence, an abort condition, and post-change verification before repair or recovery.
- Preserve the original database and the repair-reported backup when recovery fails. Do not delete canonical rows to hide a derived-index error.
- Do not expose transcripts, session IDs, local paths, process arguments, backup contents, credentials, private URLs, or raw logs. Use redacted counts and bounded error excerpts.
- Do not classify an FTS-only error as structural corruption, and do not classify a failed structural repair as proof that the source data is lost.
- Never silently route around a lock, approval denial, failed integrity check, or stale repair result through another profile or shell.

## Common pitfalls and recovery

1. **Running EMH inside the damaged target home.** This can make EMH itself a writer or let its own session tools touch the damaged store. Recovery: keep EMH in a separate healthy profile and inspect the target by explicit identity.
2. **Using `session_search` as a health check.** It can activate the FTS path that is under investigation. Recovery: use bounded log, process, and consistent-snapshot evidence instead.
3. **Treating `PRAGMA quick_check` or a single basic doctor result as complete proof.** FTS-only or content-dependent corruption can evade a narrow probe. Recovery: retain the exact failing operation and its FTS/canonical classification.
4. **Repairing while a writer is alive.** A gateway, cron worker, Desktop process, dashboard, or parent CLI can reintroduce the problem or invalidate a snapshot. Recovery: stop every writer under approval and use a fresh shell.
5. **Copying the SQLite bundle member by member.** A main file, WAL, and SHM can represent different points in time. Recovery: use the guarded `sessions repair` or `sessions recover` workflow, not ad hoc file copies.
6. **Treating reinstall or rollback as database repair.** Application replacement does not automatically repair a persisted session store. Recovery: separate code version, database condition, and active process state.
7. **Replacing the active database after a partial recovery.** A verified partial output may still have skipped ranges or reconstructed sessions. Recovery: review the JSON report and obtain a separate promotion approval.
8. **Publishing raw incident material.** Logs and transcripts can contain private data. Recovery: produce a minimal, redacted escalation packet and seek approval before any public issue.

## Verification checklist

- [ ] EMH ran from a separate healthy profile; the target `HERMES_HOME` was not adopted by EMH.
- [ ] Target profile/home, installed version, launch surface, active writer roles, and first error class are recorded.
- [ ] The diagnosis distinguishes schema migration, FTS-only, and structural/WAL evidence.
- [ ] Every conclusion is labeled Observed, Reproduced, Confirmed in installed source, Officially documented, Known upstream fix, or Hypothesis.
- [ ] No target session browse, resume, `session_search`, repair, recovery, process action, database write, or configuration change occurred without explicit approval.
- [ ] Any proposed repair names the verified backup/source-preservation evidence, rollback, all-writer stop condition, abort condition, and post-change verification.
- [ ] The SQLite bundle was preserved as one unit; no independent main/WAL/SHM copy, deletion, or replacement occurred.
- [ ] Post-treatment verification repeats the original failing class, checks canonical row-count continuity, and records remaining uncertainty.
- [ ] Any public escalation remains redacted and separately approval-gated.

## Escalation packet requirements

Provide a redacted escalation packet containing:

- **Installed version:** Hermes version, install method, and source identity summary.
- **Platform:** OS, launch surface, target profile/home summary, filesystem class, and gateway/Desktop/CLI/cron involvement.
- **Reproduction:** the smallest safe sequence, whether startup, persistence, or search triggered it, and whether the target was quiesced.
- **Expected behavior:** expected session persistence, schema availability, FTS search behavior, or recovery result.
- **Actual behavior:** first error class, exact stage, recurrence pattern, and whether it names schema, FTS, canonical tables, WAL, or a lock.
- **Minimal evidence:** redacted version/process summary, bounded error excerpt, database/WAL size signal, integrity result from a consistent snapshot, and the supported-command result if approved.
- **Differential:** why schema migration, FTS-only, structural/WAL, filesystem, or concurrent-writer hypotheses remain or were rejected.
- **Residual question:** one maintainer question that would distinguish the remaining hypothesis, such as whether the failing operation references an FTS trigger or a canonical b-tree.
- **Safety record:** read-only probes, approvals, all-writer status, verified backup/rollback, repair/recovery result, and post-treatment verification.
- **Redaction boundary:** redact private paths, profile/session identifiers, transcript content, credentials, raw logs, and backup contents. Keep the packet private until reviewed; never publish raw logs or recovery artifacts automatically.
