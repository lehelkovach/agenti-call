# Agent Prompt

This file is the live repository prompt imported from
`lehelkovach/agent-repo-boilerplate` and customized for agenti-call. Agents
working in this repository should read this file before planning, coding, or
changing orchestration state.

## Base-Agent Section

1) Mission
	a) Deliver small, reviewable improvements while preserving repository integrity.
	b) Read available context before acting, including `.AGENT/agent.md`, the README, and
	   task-specific docs.
	c) Make focused changes, verify them, and leave clear handoff notes.

2) Operating Loop
	a) Inspect repository state, branch, and current changes before editing.
	b) Identify the smallest safe change that satisfies the task.
	c) Use existing project conventions, tools, and file organization.
	d) Run targeted verification before broad or expensive checks.
	e) Update `.AGENT/agent-action-log.md` for meaningful setup, implementation,
	   verification, or handoff events.
	f) Commit and prepare work for review when the workflow or maintainer request requires
	   it.

3) Startup and Run Files
	a) At the start of a new agent run, read `.AGENT/agent.md`, `.AGENT/agent-run.md`,
	   `.AGENT/agent-run-once.md`, `.AGENT/dev-notes.md`, and the latest relevant entries
	   in `.AGENT/agent-action-log.md`.
	b) Treat `.AGENT/agent-run.md` as the persistent runbook for recurring startup
	   operations and standing checks.
	c) Treat `.AGENT/agent-run-once.md` as the one-shot queue for startup operations that
	   should run once and then be removed from that file.
	d) When a run-once item is completed, delete that item from `.AGENT/agent-run-once.md`,
	   then append the completed operation to `.AGENT/agent-action-log.md` with timestamp,
	   agent name, agent role, scope, result, verification, and follow-ups.
	e) If a run-once item cannot be completed, leave it in `.AGENT/agent-run-once.md` with
	   a short blocked note and append the blocker to the action log.
	f) Re-read `.AGENT/agent.md` after processing run-once items because those actions may
	   have updated the prompt or repository-specific directions.

4) Prompt Feedback Loop
	a) When a maintainer gives a new standing instruction, decide whether it belongs in
	   `.AGENT/agent.md`, `.AGENT/agent-run.md`, `.AGENT/agent-run-once.md`,
	   `.AGENT/dev-notes.md`, or only the current task notes.
	b) Add repository-specific rules to `.AGENT/agent.md` below `#### Below:
	   Repository-Specific Directions` and keep them ordered by priority.
	c) Add recurring operational instructions to `.AGENT/agent-run.md`.
	d) Add one-time startup operations to `.AGENT/agent-run-once.md`.
	e) Log every prompt, runbook, or run-once change in `.AGENT/agent-action-log.md`.
	f) Do not leave important orchestration decisions only in chat context.

5) Agent Identity and Roles
	a) Identify yourself in action-log entries by agent name or tool, role, and branch.
	b) Use "master repo agent" for the primary agent coordinating repository-level prompt,
	   runbook, architecture, and synchronization changes.
	c) Use "worker sub-agent" for delegated agents working on narrower subsystems.
	d) If multiple agents touch `.AGENT/` files, preserve each agent's log entries and
	   avoid overwriting another agent's queued work.

6) Repository Safety
	a) Preserve existing user work and never discard unrelated changes.
	b) Do not expose or commit secrets, credentials, tokens, phone numbers that are private,
	   or machine-specific configuration.
	c) Avoid adding dependencies unless the task clearly requires them.
	d) Keep generated or boilerplate edits scoped to the requested files.
	e) Do not rewrite history or force push unless explicitly instructed.

7) Default Engineering Behavior
	a) Prefer repository-local patterns over new abstractions.
	b) Favor readable, maintainable code over cleverness.
	c) Add tests for behavior changes when a test framework exists.
	d) Explain skipped verification with the reason and residual risk.
	e) Escalate blockers with concrete evidence and suggested next steps.

8) Agent Action Log Usage
	a) Treat `.AGENT/agent-action-log.md` as the authoritative activity log for agent work.
	b) Add an entry for non-trivial setup, implementation, verification, migration,
	   permission, or handoff work.
	c) Keep entries in reverse chronological order.
	d) Update "Verification" from pending to actual commands or manual checks before
	   finishing a task.
	e) Record follow-ups as "None currently known" when there are no known gaps.
	f) Use this entry shape:

	   ```markdown
	   ## YYYY-MM-DD - Short title

	   1) Timestamp
	   	a) YYYY-MM-DD HH:MM UTC
	   2) Agent
	   	a) <agent name or tool>
	   3) Role
	   	a) <master repo agent, worker sub-agent, or other role>
	   4) Branch
	   	a) <branch name>
	   5) Scope
	   	a) <files, subsystem, or issue>
	   6) Actions
	   	a) <what changed>
	   7) Verification
	   	a) <commands or manual checks>
	   8) Follow-ups
	   	a) <known gaps or none>
	   ```

9) Optional Prompt Commands
	a) For documentation changes, update README/docs affected by setup, usage, commands,
	   configuration, or operational behavior.
	b) For security-sensitive changes, inspect touched files for secret exposure, unsafe
	   input handling, over-broad permissions, and insecure defaults.
	c) For live-service changes, keep dev testing distinct from production deployment and
	   document rollback or cleanup steps.
	d) For environment-dependent tasks, document required variable names and purpose without
	   inventing or exposing secret values.

10) Support Files
	a) Keep agent support files inside `.AGENT/`.
	b) Use `.AGENT/dev-notes.md` for future agent infrastructure notes, including
	   inter-agent communication rules, agentic environment variables, and service
	   orchestration assumptions.

#### Below: Repository-Specific Directions

1) Project Mission
	a) This repository is for an agentic voice-calling system that can run on OCI with
	   Asterisk as the SIP/PSTN edge, OpenClaw as the agent/tool runtime, and Google Gemini
	   Live as the first realtime speech-to-speech model target.
	b) The architecture should keep telephony control, model/voice bridging, OpenClaw agent
	   tools, admin UI, and compliance enforcement as separate concerns.
	c) Stunt Banana is a reference for minimalist Asterisk configuration patterns only; do
	   not import or enable caller-ID spoofing/DISA flows.

2) Orchestration Roles
	a) The master repo agent coordinates architecture, `.AGENT/` state, branch hygiene,
	   PR-ready documentation, and cross-subsystem decisions.
	b) Worker sub-agents may be used for scoped research or implementation in these lanes:
	   OCI/Terraform, Asterisk/SIP, voice bridge, OpenClaw plugin/skill, admin frontend,
	   compliance/safety, and tests/observability.
	c) Record delegated findings or handoffs in `.AGENT/agent-action-log.md` or docs before
	   relying on them in later work.

3) Subsystem Boundaries
	a) OCI infrastructure should own VCN, subnets, Network Security Groups, compute, storage,
	   secret references, observability, and deploy wiring.
	b) Asterisk should own SIP trunk registration, DID routing, ARI/Stasis call control, RTP
	   media boundaries, and optional SIP device endpoints.
	c) The voice bridge should own ARI sessions, ExternalMedia/AudioSocket handling,
	   telephony audio conversion, VAD/barge-in, Gemini Live sessions, optional
	   ElevenLabs TTS, DTMF/keypad signaling, and call lifecycle events.
	d) OpenClaw should own agent identity, prompts, tool calls, memory/context, and
	   high-level call actions exposed through a robocall plugin/service.
	e) The admin surface should own characters, scripts, decision trees, campaigns, contact
	   governance, voice profiles, transcripts, call logs, consent, and opt-outs.

4) Safety and Compliance Invariants
	a) Never add functionality that enables arbitrary caller-ID spoofing.
	b) Outbound caller ID must be selected from verified/assigned numbers.
	c) Calls must pass application-level consent, opt-out, rate-limit, allowed-window, and
	   disclosure checks before placement.
	d) Do not commit live customer/contact data, recordings, transcripts, API keys, SIP
	   credentials, private phone numbers, or OCI private keys.
	e) Prefer deterministic enforcement in code/config over prompt-only safety rules.

5) Current Repository State
	a) The repo is currently documentation-first. Existing tracked project files include
	   `README.md`, `docs/stuntbanana-integration.md`,
	   `docs/voice-generation-and-dtmf.md`, `docs/testing-and-dev-deployment.md`, and
	   `.AGENT/`.
	b) No application package manager, build system, Terraform root, Docker Compose stack, or
	   runtime service code is configured yet.
	c) Until implementation exists, use documentation review, `.AGENT` smoke tests,
	   `git diff --check`, and `git status` as primary verification.

6) Expected Future Work Order
	a) Define repository skeleton and service boundaries before provisioning live telecom
	   resources.
	b) Add infrastructure-as-code for OCI and Asterisk only after required secrets and SIP
	   provider assumptions are documented.
	c) Build an Asterisk ARI/ExternalMedia proof of concept before adding admin campaigns.
	d) Add OpenClaw skill/plugin integration once the call bridge API is stable enough to
	   expose tools.
	e) Add admin UI after single-call inbound/outbound flows and compliance gates are
	   validated.

7) Active Goals
	a) Keep the repository agent-ready by maintaining `.AGENT/` files as durable
	   orchestration state, not just passive documentation.
	b) Turn the current architecture plan into an implementation-ready skeleton with clear
	   folders, service contracts, and verification commands before writing runtime code.
	c) Preserve the safe Asterisk direction: use Stunt Banana as a minimalist configuration
	   reference, keep ARI private, and exclude caller-ID spoofing/DISA behavior.
	d) Prepare for an OCI-hosted Asterisk + voice bridge stack that can make and receive
	   calls through assigned SIP-provider numbers and route media to Gemini Live or
	   ElevenLabs-backed speech generation where appropriate.
	e) Prepare OpenClaw integration around explicit tools and skills for call control,
	   scripts, decision trees, and compliance-aware robocalling workflows.
	f) Support validated DTMF/keypad actions from structured agent or script output for IVR,
	   conference bridge, extension, and PIN workflows without exposing arbitrary raw
	   telephony commands.
	g) Build testability in layers: mock-local first, then Asterisk lab, OCI dev, live SIP
	   smoke tests, and OpenClaw skill-extension validation.

8) Subtask Progress Logging
	a) Update `.AGENT/agent-action-log.md` when completing meaningful subtasks, not only at
	   final handoff.
	b) For multi-step work, add or update an action-log entry as each completed subtask
	   changes repository state, resolves a blocker, establishes a decision, or completes
	   verification.
	c) Keep in-progress verification marked as pending only while work is actively ongoing;
	   replace it with exact commands or manual checks before committing.
	d) If goals change, update this Active Goals section and record the prompt/goals change
	   in `.AGENT/agent-action-log.md`.

9) Verification Commands
	a) Run `.AGENT` smoke validation after changing agent support files:

	   ```sh
	   python3 .AGENT/tests/agent_architecture_smoke.py
	   ```

	b) Run whitespace validation before committing:

	   ```sh
	   git diff --check
	   ```

	c) For documentation-only changes, include file review plus the commands above in the
	   action log or final handoff.
