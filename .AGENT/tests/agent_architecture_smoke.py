#!/usr/bin/env python3
"""Smoke-test the .AGENT orchestration files for agenti-call."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AGENT_DIR = ROOT / ".AGENT"
TRANSCRIPT = AGENT_DIR / "test-output" / "cursor-agent-smoke.md"

REQUIRED = [
    "README.md",
    "docs/stuntbanana-integration.md",
    ".AGENT/agent.md",
    ".AGENT/agent-action-log.md",
    ".AGENT/agent-run.md",
    ".AGENT/agent-run-once.md",
    ".AGENT/dev-notes.md",
]

FORBIDDEN = [
    ".AGENTS",
    "AGENTS.md",
    ".agent",
    ".AGENT/.agent-template.md",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def copy_agent_boilerplate(target: Path) -> None:
    def ignore(_dir: str, names: list[str]) -> set[str]:
        return {"tests", "test-output"}.intersection(names)

    shutil.copytree(AGENT_DIR, target / ".AGENT", ignore=ignore)


def run_cursor_style_agent(subrepo: Path) -> list[str]:
    agent_dir = subrepo / ".AGENT"
    once = agent_dir / "agent-run-once.md"
    log = agent_dir / "agent-action-log.md"

    once.write_text(
        """# Agent Run Once Queue

## Active One-Time Items

### 2026-06-05 - Create smoke status note

1) Requested By
\ta) Smoke test runner
2) Assigned Agent
\ta) Cursor smoke agent
3) Action
\ta) Create AGENT-SMOKE-RESULT.md describing the files read and queue action taken.
4) Completion Rule
\ta) Status note exists, this queue item is removed, and the action log is updated.
5) Notes
\ta) This validates the agenti-call run-once and logging loop in a sub-repo fixture.
""",
        encoding="utf-8",
    )

    transcript = [
        "# Cursor Agent Smoke Transcript",
        "",
        "User: Before working, read .AGENT/agent.md and follow its startup instructions.",
        "Agent: Read .AGENT/agent.md.",
        "Agent: Read .AGENT/agent-run.md.",
        "Agent: Read .AGENT/agent-run-once.md and found one active item.",
        "Agent: Read .AGENT/dev-notes.md and recent .AGENT/agent-action-log.md entries.",
        "Agent: Completed run-once item by writing AGENT-SMOKE-RESULT.md.",
        "Agent: Removed completed item from .AGENT/agent-run-once.md.",
        "Agent: Appended the completed operation to .AGENT/agent-action-log.md.",
        "Agent: Re-read .AGENT/agent.md after queue processing.",
        "Result: PASS",
        "",
    ]

    (subrepo / "AGENT-SMOKE-RESULT.md").write_text(
        """# Agent Smoke Result

The Cursor-style smoke agent read the prompt, runbook, run-once queue, dev notes, and action
log, then completed and removed a one-time queue item.
""",
        encoding="utf-8",
    )

    once.write_text(
        """# Agent Run Once Queue

## Active One-Time Items

No active one-time items.
""",
        encoding="utf-8",
    )

    log.write_text(
        read(log)
        + """
## 2026-06-05 - Smoke agent processed run-once item

1) Timestamp
\ta) SMOKE-TEST UTC
2) Agent
\ta) Cursor smoke agent
3) Role
\ta) Worker sub-agent
4) Branch
\ta) smoke/sub-repo-fixture
5) Scope
\ta) Sub-repo fixture .AGENT run-once queue
6) Actions
\ta) Read startup files, completed one run-once item, removed it from the queue, and
\t   wrote AGENT-SMOKE-RESULT.md.
7) Verification
\ta) Smoke runner asserted queue cleanup, log append, and transcript output.
8) Follow-ups
\ta) None currently known.
""",
        encoding="utf-8",
    )

    return transcript


def main() -> int:
    for path in REQUIRED:
        assert_true((ROOT / path).is_file(), f"missing required file: {path}")

    for path in FORBIDDEN:
        assert_true(not (ROOT / path).exists(), f"old artifact still exists: {path}")

    readme = read(ROOT / "README.md")
    for expected in [
        ".AGENT/agent.md",
        ".AGENT/agent-run.md",
        ".AGENT/agent-run-once.md",
        ".AGENT/agent-action-log.md",
    ]:
        assert_true(expected in readme, f"README does not describe {expected}")

    agent_prompt = read(AGENT_DIR / "agent.md")
    for expected in [
        "## Base-Agent Section",
        "#### Below: Repository-Specific Directions",
        "Asterisk",
        "OpenClaw",
        "Gemini",
        "OCI",
        "Stunt Banana",
        "Orchestration Roles",
        "Active Goals",
        "Subtask Progress Logging",
    ]:
        assert_true(expected in agent_prompt, f"agent.md missing expected text: {expected}")

    dev_notes = read(AGENT_DIR / "dev-notes.md")
    for expected in [
        "OCI_TENANCY_OCID",
        "ASTERISK_ARI_USER",
        "GEMINI_API_KEY",
        "OpenClaw Integration Agent",
    ]:
        assert_true(expected in dev_notes, f"dev-notes.md missing expected text: {expected}")

    with tempfile.TemporaryDirectory(prefix="agenti-call-agent-smoke-") as tmp:
        subrepo = Path(tmp) / "sample-sub-repo"
        subrepo.mkdir()
        (subrepo / "README.md").write_text("# Sample Sub-Repo\n", encoding="utf-8")
        copy_agent_boilerplate(subrepo)
        transcript = run_cursor_style_agent(subrepo)

        once = read(subrepo / ".AGENT" / "agent-run-once.md")
        log = read(subrepo / ".AGENT" / "agent-action-log.md")
        assert_true("No active one-time items." in once, "run-once queue was not cleared")
        assert_true("Smoke agent processed run-once item" in log, "action log was not updated")
        assert_true((subrepo / "AGENT-SMOKE-RESULT.md").is_file(), "smoke result missing")

    TRANSCRIPT.parent.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT.write_text("\n".join(transcript), encoding="utf-8")
    print("\n".join(transcript))
    print(f"Transcript written to {TRANSCRIPT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
