---
name: emh-github-publishing
description: Use when a confirmed Hermes diagnosis needs a redacted, approval-gated GitHub issue or pull-request workflow.
version: 0.2.0
author: Jonathan Rivera
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [emh, github, issues, pull-requests, approval, verification]
    related_skills: [emh-triage, emh-release-intelligence]
---

# EMH GitHub publishing

## Response presentation

Use the shared [EMH response reference](../emh-triage/references/response-templates.md) for normal answers: lead with **What I found**, **What it means**, **Safest next step**, **Permission needed: Yes/No**, then **Technical details**. Preserve this skill's domain workflow, evidence labels, and safety/approval rules; this presentation guidance does not replace them. Reuse the existing [evidence and source policy](../emh-triage/references/evidence-and-source-policy.md), [safety and redaction policy](../emh-triage/references/safety-and-redaction.md), and triage escalation packet. Keep the publication state, external-contact warning, mutation warning, rollback, and residual uncertainty in the concise answer rather than hiding them below technical details.

## Overview

Use this skill for one narrow handoff: a confirmed, redacted Hermes diagnosis may become a locally verified GitHub issue or pull-request candidate. The current runtime and installed source outrank generic guidance; official docs are authoritative current documentation for Hermes behavior. This skill is instruction-only and contains no executable, reference, or template file.

The skill does not make diagnosis, community intake, network contact, local source mutation, push, issue or pull-request creation, merge, or cleanup implicit. Each is a separate evidence-bound state with an exact, just-in-time approval. A successful local command is not proof of a remote result, and a remote result is not proof of CI, review, merge, release, or deployment.

## When to Use

Use when EMH has a confirmed diagnosis, a minimal redacted case, and an explicitly requested route to a local draft, a GitHub issue, or a GitHub pull request. The input must identify the exact target, source state, writer boundary, requested route, and evidence needed for the next state.

Don't use for: an unconfirmed complaint, a Hypothesis presented as fact, an unreviewed community proposal, status: PROPOSED promotion, generic repository administration, credential setup, unattended network contact, automatic source changes, direct issue or pull-request publication without approval, merge, release, deployment, or cleanup without its own approval. Stop at a blocked or local-only state and route the request to the appropriate diagnostic or separately approved workflow.

## Input and output contract

The input must contain a redacted case and the exact publication boundary. Require all of the following before preparing an issue or pull-request candidate:

- A confirmed diagnosis supported by reproduction, installed source or tests, or authoritative version-matched evidence. An unconfirmed diagnosis is rejected for publication planning.
- An unreviewed community proposal is input evidence only and never confirmation; it cannot satisfy the confirmed-diagnosis requirement.
- Installed Hermes version, EMH distribution version, install method, safe platform scope, bounded reproduction, expected result, actual result, minimal redacted evidence, and residual question.
- Exact `OWNER/REPO`, verified canonical checkout, normalized origin remote, base branch, head branch, base SHA, head SHA, isolated worktree, authenticated writer permission, controller/writer ownership source, and the named sole writer.
- Requested route is exactly one of local draft only, issue, or PR. Never infer issue-plus-PR.
- A redaction attestation covering secrets, raw logs, private paths and URLs, user/account/contact identifiers, repository-private identifiers, and unrelated incident material.

Return one bounded result: a blocked result with the missing evidence or approval; a sanitized local issue body candidate; a sanitized local PR body candidate with exact local commit and test evidence; a verified issue or PR record only after its later approval and remote readback; an honest CI state; or a merge-ready report that remains `MERGE_AWAITING_APPROVAL`. Never persist the full diagnostic transcript. A body candidate contains only the minimum public packet.

## Evidence collection workflow

1. Consume the existing redacted triage escalation packet. Preserve its evidence policy and redaction boundary; do not turn a community report, proposal, or copied transcript into a diagnosis.
2. Confirm the seven case fields in this order: **Complaint**; **Vitals**; **Differential diagnosis**; **Confirmed diagnosis**; **Treatment**; **Post-treatment verification**; **Discharge summary or escalation packet**.
3. Use only these six evidence labels, with the supporting command, source symbol, or version-matched citation adjacent to the claim:
   - **Observed**
   - **Reproduced**
   - **Confirmed in installed source**
   - **Officially documented**
   - **Known upstream fix**
   - **Hypothesis**
4. Confirm the diagnosis before drafting public issue or PR content. A Hypothesis remains uncertainty. A community proposal is input evidence only; `status: PROPOSED` is not a promotion signal and must never be promoted to a confirmed diagnosis.
5. Redact before display, persistence, body drafting, or escalation. Keep only the minimal symptom, impact, version/install method/platform class, bounded reproduction, expected versus actual result, adjacent evidence, upstream-fix status, and one maintainer question.
6. Pin `OWNER/REPO`, canonical checkout, normalized origin remote, base/head branches, base/head SHAs, isolated worktree, authenticated writer permission, controller/writer ownership source, and sole writer. Worktree enumeration alone does not prove ownership.
7. Choose one route: local draft only, issue, or PR. Do not infer issue-plus-PR. If a required fact or approval is missing, return `BLOCKED` and name the exact missing item.
8. Keep the following states separate: `DIAGNOSIS_NOT_CONFIRMED`; `CASE_CONFIRMED_LOCAL_ONLY`; `DRAFT_READY_LOCAL_ONLY`; `LOCAL_CHANGE_APPROVED`; `LOCAL_TESTS_PASSED`; `PUSH_AWAITING_APPROVAL`; `PUSH_VERIFIED`; `ISSUE_OR_PR_AWAITING_APPROVAL`; `ISSUE_OPEN_VERIFIED`; `PR_OPEN_VERIFIED`; `CI_PENDING`; `CI_FAILED`; `CI_PASSED`; `NO_REQUIRED_CHECKS`; `CI_UNKNOWN`; `MERGE_AWAITING_APPROVAL`; `MERGED_VERIFIED`; `BLOCKED`.
9. Record raw command exit state without sensitive output. The local candidate is not a remote publication, and a remote publication is not a test, review, CI, merge, release, or deployment result.

## Decision tree

1. If the diagnosis is not confirmed, reject publication planning and return `DIAGNOSIS_NOT_CONFIRMED`. When confirmation is complete, record `CASE_CONFIRMED_LOCAL_ONLY`. A local note may identify missing evidence, but it is not a GitHub issue or PR candidate.
2. If the material is an unreviewed community proposal, a Hypothesis presented as fact, or `status: PROPOSED`, reject promotion. A proposal is input evidence only; do not promote it.
3. If `OWNER/REPO`, canonical checkout, normalized origin, base/head branch, base/head SHA, isolated worktree, authenticated writer permission, controller/writer ownership source, or sole writer is unknown or conflicting, return `BLOCKED`.
4. If target discovery contacts GitHub, obtain `NETWORK_READ_APPROVAL` unless the current request explicitly includes that bounded read. Read-only does not mean contact-free.
5. After the network gate, read duplicate issue and PR lists. Do not create a duplicate silently; keep the candidate local or report the verified duplicate.
6. For an issue route, stop at `ISSUE_OR_PR_AWAITING_APPROVAL` with the exact title, sanitized body, repository, and issue route. Issue approval does not approve a PR.
7. For a PR route, require `LOCAL_CHANGE_APPROVAL` before creating the isolated worktree or changing source. Verify the clean base, exact remote, target guidance, file scope, rollback, sole writer, and local test plan.
8. Run the original reproduction, focused tests, canonical repository gate, privacy scan, and diff review. Set `LOCAL_TESTS_PASSED` only from real local evidence; otherwise remain `BLOCKED` or rework locally.
9. Present the exact immutable commit, ref, target, and remote. Obtain separate `PUSH_APPROVAL`; then push only that approved commit/ref and read back the remote head SHA before setting `PUSH_VERIFIED`.
10. Present the exact issue or PR route, repository, title, body file, base, and head. Obtain separate `ISSUE_OR_PR_APPROVAL`; push approval is not issue or PR approval. Create only the approved route and read back the exact remote record before setting `ISSUE_OPEN_VERIFIED` or `PR_OPEN_VERIFIED`.
11. Classify required checks honestly: pending checks are `CI_PENDING`; failed checks are `CI_FAILED`; all required checks passing is `CI_PASSED`; an empty required-check set means NO_REQUIRED_CHECKS, not pass or green CI; an ambiguous API or transport result is `CI_UNKNOWN`.
12. For a PR, obtain separate `MERGE_APPROVAL` bound to the current PR head SHA, base, checks, and merge strategy. Only a verified merge may become `MERGED_VERIFIED`.
13. Obtain separate `CLEANUP_APPROVAL` before removing a branch, worktree, body file, or remote artifact. Cleanup denial does not silently change the publication state.

Diagnosis never implies draft; draft never implies push; push never implies PR; PR never implies CI pass; CI pass never implies merge approval. Never infer issue-plus-PR.

## Exact commands and tool calls

All commands in this section are instructions only. Do not execute them as part of EMH distribution tests. Use the smallest bounded read and record only the redacted exit state.

### Read-only allowlist

Local reads before any mutation:

- `git -C <target-repo> rev-parse --show-toplevel`
- `git -C <target-repo> rev-parse HEAD`
- `git -C <target-repo> branch --show-current`
- `git -C <target-repo> status --porcelain=v1 -uall`
- `git -C <target-repo> remote get-url origin`
- `git -C <target-repo> worktree list --porcelain`
- `git -C <target-repo> config --get user.name`
- `git -C <target-repo> config --get user.email`

Bounded remote reads after `NETWORK_READ_APPROVAL`:

- `gh auth status`
- `gh repo view OWNER/REPO --json nameWithOwner,isPrivate,defaultBranchRef,viewerPermission,url`
- `git ls-remote origin refs/heads/<base-branch>`
- `gh issue list --repo OWNER/REPO --state all --search "<redacted-signature>" --json number,title,state,url`
- `gh pr list --repo OWNER/REPO --state all --head <head-branch> --json number,title,state,url,headRefName,baseRefName`

No allowlisted read creates, edits, pushes, merges, comments, reviews, or cleanup. Network reads remain gated because they contact an external service.

### Approval-gated local source change

Only after exact `LOCAL_CHANGE_APPROVAL`, create the isolated worktree and make the explicitly bounded source change:

```text
git -C <canonical-repo> worktree add -b <head-branch> <isolated-worktree> <verified-base-sha>
```

Verify branch, base SHA, clean status, target guidance, sole writer, and exact changed paths. Use a verified backup for difficult-to-reverse work, run the original reproduction and repository tests, and record `LOCAL_CHANGE_APPROVED` followed by `LOCAL_TESTS_PASSED` only when each result is real. Keep a draft body in a nontracked file; inspect its exact redacted bytes before any later approval.

### Approval-gated push

Only after presenting the immutable commit, target remote, ref, expected effect, backup/rollback, and test evidence may the operator grant separate `PUSH_APPROVAL`:

```text
git -C <isolated-worktree> push origin HEAD:refs/heads/<head-branch>
```

The command is not success evidence by itself. Read the remote head back with `git ls-remote origin refs/heads/<head-branch>` and set `PUSH_VERIFIED` only when the returned SHA equals the approved local SHA. Any target, body, commit, or ref change invalidates the approval.

### Approval-gated issue/PR creation

Issue and PR creation are distinct routes. Never infer issue-plus-PR. After a duplicate read, present the exact repository, route, title, sanitized body file, and expected effect; then obtain separate `ISSUE_OR_PR_APPROVAL`.

For an issue, document but do not execute:

```text
gh issue create --repo OWNER/REPO --title <approved-title> --body-file <approved-body-file>
```

For a PR, document but do not execute:

```text
gh pr create --repo OWNER/REPO --base <base-branch> --head <head-branch> --title <approved-title> --body-file <approved-body-file>
```

Use `--body-file`; never pass rich Markdown through a double-quoted `--body` argument. Never rich Markdown inside a double-quoted --body argument. `gh pr create --dry-run` may still push and is not a safety probe. Read the created record back before claiming `ISSUE_OPEN_VERIFIED` or `PR_OPEN_VERIFIED`.

Required issue readback:

```text
gh issue view <issue-number> --repo OWNER/REPO --json number,url,state,title,body
```

Required PR readback:

```text
gh pr view <pr-number> --repo OWNER/REPO --json number,url,state,title,body,baseRefName,headRefName,headRefOid,mergeable
gh pr checks <pr-number> --repo OWNER/REPO --required --json name,state,bucket,link
```

Compare the readback title, body, state, URL, base, head, and head SHA with the approved candidate. Report raw command exit state without copying sensitive output.

### Approval-gated merge

A PR is not a merge request merely because it exists or its checks pass. Obtain separate `MERGE_APPROVAL` for the exact PR number, current head SHA, base branch, checks, and selected merge strategy. Re-read the PR and required checks immediately before any approved merge, then read back merge state and the default-branch SHA. A merge never authorizes release, deployment, profile update, or cleanup.

### Approval-gated cleanup

Branch, worktree, body-file, issue, and PR cleanup are separate state changes. Obtain `CLEANUP_APPROVAL` for the exact artifact and operation, preserve a verified backup and rollback path where applicable, and read back the result. Do not silently remove a writer worktree, remote ref, issue, PR, or evidence file after a publication attempt.

## Safety and approval boundaries

**Read-only first.** Begin with the redacted triage packet, exact local Git reads, and bounded duplicate checks. Do not silently install, update, fetch, checkout, reset, stash, clean, alter configuration, contact a remote, push, create an issue or PR, merge, or remove evidence.

Every mutation or external contact requires **explicit approval** for the exact target, route, scope, and expected effect. `NETWORK_READ_APPROVAL`, `LOCAL_CHANGE_APPROVAL`, `PUSH_APPROVAL`, `ISSUE_OR_PR_APPROVAL`, `MERGE_APPROVAL`, and `CLEANUP_APPROVAL` are separate; one never implies another. A proposal, a diagnosis, a draft, a push, an issue, a PR, or passing CI never grants a later approval.

For destructive or difficult-to-reverse work, require a **verified backup**, an explicit **rollback** path, an abort condition, and post-change verification before execution. Keep private material out of the body and command output. Never ask an operator to paste credentials or raw logs.

**Never silently** promote a Hypothesis, community proposal, or `status: PROPOSED`; infer issue-plus-PR; treat a successful command as remote proof; report no checks as green CI; widen the target; change the approved commit; or remove a worktree, branch, body file, or evidence.

## Common pitfalls and recovery

- **Unconfirmed case:** return `DIAGNOSIS_NOT_CONFIRMED`; collect the missing bounded evidence through triage. Do not manufacture a confirmed diagnosis from a proposal or Hypothesis.
- **Proposal promotion:** a community proposal and `status: PROPOSED` are input evidence only. Reject the promotion and preserve the original evidence label.
- **Wrong target or competing writer:** stop at `BLOCKED`, preserve the worktree, and re-check the exact checkout, origin, branch, SHA, ownership source, and sole-writer boundary. Do not take over another writer.
- **Body-file mistake:** keep rich Markdown in a nontracked, redacted body file and use `--body-file`. Never use a double-quoted `--body` argument for rich Markdown, and never attach a raw transcript.
- **Push/create ambiguity:** a zero exit code proves only command completion. Read back the remote ref and exact issue/PR fields before changing state.
- **CI ambiguity:** distinguish `CI_PENDING`, `CI_FAILED`, `CI_PASSED`, `NO_REQUIRED_CHECKS`, and `CI_UNKNOWN`. An empty required-check set is `NO_REQUIRED_CHECKS`, never green CI.
- **Dry-run trap:** `gh pr create --dry-run` may push, so it is not a safety probe. Do not use it to test whether publication would be harmless.
- **Approval mismatch:** if target, route, body, commit, base, head, or expected effect changes, invalidate the prior approval and request a new exact approval.
- **Cleanup pressure:** preserve evidence and stop if cleanup is not separately approved. A denied cleanup is not a reason to rewrite or hide the publication state.

## Verification checklist

- [ ] The seven case fields are present in the required order.
- [ ] Every material claim uses only one of the six allowed evidence labels and has adjacent support.
- [ ] Diagnosis is confirmed; proposals, `status: PROPOSED`, and Hypotheses were not promoted.
- [ ] The exact `OWNER/REPO`, normalized origin, canonical checkout, base/head branches and SHAs, isolated worktree, authenticated writer permission, controller/writer ownership source, and sole writer are pinned.
- [ ] The requested route is exactly local draft only, issue, or PR; issue-plus-PR was not inferred.
- [ ] The case and body are redacted; no raw secrets, private identifiers, private paths or URLs, raw logs, or copied transcript remain.
- [ ] Local source change, push, issue/PR creation, merge, and cleanup each have their own just-in-time approval.
- [ ] The original reproduction, focused tests, canonical gate, privacy scan, diff, and raw exit states are recorded.
- [ ] A nontracked body file and `--body-file` are used for rich Markdown.
- [ ] Remote ref and issue/PR readbacks match the approved target, body, route, base, head, and SHA.
- [ ] CI is classified honestly; no required checks are `NO_REQUIRED_CHECKS`, not green CI.
- [ ] The final publication state is named, and any remaining human gate is explicit.

## Escalation packet requirements

Reuse the existing redacted triage escalation packet and keep it minimal. Include these fields, with no raw transcript:

- **Installed version:** Hermes and EMH versions actually under review.
- **Platform:** safe OS family, architecture, and relevant interface class.
- **Reproduction:** exact bounded read-only steps and raw command exit state without sensitive output.
- **Expected behavior:** one precise expected result.
- **Actual behavior:** one precise redacted result.
- **Minimal evidence:** only the smallest adjacent evidence needed for the diagnosis, with one of the six allowed labels.
- **Residual question:** one concrete maintainer or operator question.
- **Publication state:** one of the explicit local, push, issue/PR, CI, merge, or blocked states.
- **Target and writer boundary:** exact `OWNER/REPO`, normalized origin, base/head, isolated worktree, controller/writer ownership source, and sole writer when safe to disclose in the local packet.
- **Redaction note:** state what was removed or omitted. Redact secrets, private paths and URLs, account/contact identifiers, repository-private identifiers, raw logs, and unrelated incident material.

An issue body contains the redacted symptom and impact, versions/install method/platform, bounded reproduction, expected versus actual result, minimal evidence, Known upstream fix status including `not established` when appropriate, no unsupported fix claim, and one maintainer question. A PR body additionally contains the confirmed diagnosis, exact change scope, focused and canonical command results, risk, rollback, residual uncertainty, and a linked issue only when verified and explicitly approved. Do not use `Fixes` or `Closes` text unless automatic closure is deliberately approved. Do not claim that a draft, push, issue, PR, CI result, review, merge, release, or deployment is another state. Stop with `MERGE_AWAITING_APPROVAL` when merge approval is the remaining gate.
