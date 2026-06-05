# Agent Runbook

Persistent startup operations and standing checks for agents working in this
repository. Agents should read this file at the start of each run after reading
`.AGENT/agent.md`.

## Recurring Startup Operations

1) Refresh Agent Context
	a) Read `.AGENT/agent.md`, `.AGENT/dev-notes.md`, `.AGENT/agent-run.md`,
	   `.AGENT/agent-run-once.md`, and the latest relevant entries in
	   `.AGENT/agent-action-log.md`.
	b) Read `README.md` and any docs related to the task, especially
	   `docs/stuntbanana-integration.md` for Asterisk work.
	c) Check the current branch and working tree before editing.
	d) Preserve existing user or agent work.

2) Process One-Shot Queue
	a) Review `.AGENT/agent-run-once.md` for active one-time operations.
	b) Complete active run-once items before starting unrelated work when safe.
	c) Remove completed items from `.AGENT/agent-run-once.md`.
	d) Append completed or blocked run-once results to `.AGENT/agent-action-log.md` with
	   timestamp, agent name, role, branch, scope, verification, and follow-ups.

3) Prompt Feedback Loop
	a) If the maintainer gives a new standing instruction, persist it in the correct
	   `.AGENT/` file rather than leaving it only in chat context.
	b) Re-read `.AGENT/agent.md` after changing prompt instructions.
	c) Log prompt, runbook, and run-once changes in `.AGENT/agent-action-log.md`.

4) Subtask Progress Logging
	a) Before substantial work, identify the current subtask scope in the action log or in
	   an existing in-progress log entry when the work changes repository state.
	b) As each meaningful subtask completes, update `.AGENT/agent-action-log.md` with what
	   changed, what was learned, and any verification already run.
	c) Before committing, ensure pending verification notes are replaced with exact commands,
	   manual checks, or explicit skipped-verification rationale.

5) Branch Synchronization
	a) Use feature branches for review, concurrent work, or changes that may conflict.
	b) Avoid creating competing edits to `.AGENT/agent-run-once.md`; consume one-shot items
	   carefully and preserve other agents' pending work.
	c) When `.AGENT/` files change, commit and push those changes with the rest of the
	   logical task so future agents can read the updated orchestration state.

6) Architecture Guardrails
	a) Keep OCI, Asterisk, voice bridge, OpenClaw, admin UI, and compliance concerns
	   separated in docs and code.
	b) Prefer explicit service contracts over implicit coupling between agent prompts and
	   telephony runtime behavior.
	c) Document required secrets by name and purpose only; never commit live values.

## Active Recurring Items

1) Maintain agenti-call orchestration map
	a) Keep `.AGENT/agent.md` aligned with the current architecture direction.
	b) Keep `README.md` and `docs/` updated when subsystem boundaries or required services
	   change.
	c) Log non-trivial orchestration decisions in `.AGENT/agent-action-log.md`.

2) Preserve safe telephony defaults
	a) Re-check that design changes do not reintroduce arbitrary caller-ID spoofing.
	b) Re-check that ARI stays private and SIP/RTP exposure is limited to intended sources.
	c) Re-check that compliance gates are enforced by application logic, not only prompts.
