# Agent Dev Notes

Development notes for future agent support files, inter-agent coordination, and
service orchestration. These notes document names and assumptions only; do not
store live secret values here.

## Future Inter-Agent Communication

1) Communication Rules
	a) Define message formats before agents exchange task state.
	b) Include sender agent UUID, recipient or channel, timestamp, task scope, and expected
	   response behavior.
	c) Record durable decisions in `.AGENT/agent-action-log.md` or project docs rather than
	   relying only on transient bus messages.

2) Agentic Environment Variables
	a) `IAC_BUS_HOST`: Placeholder host or IP address for a future inter-agent
	   communication bus.
	b) `IAC_BUS_PORT`: Placeholder port for the future inter-agent communication bus.
	c) `AGENT_UUID`: Placeholder UUID registered for the current agent runtime.
	d) `AGENT_REPO_SLUG`: Repository owner/name value for agent registration, expected to be
	   `lehelkovach/agenti-call`.
	e) `AGENT_RUN_ID`: Run identifier for correlating logs and bus messages.
	f) `SLACK_WEBHOOK_URL`: Optional secret for Slack or compatible webhook notifications.
	g) `SLACK_CHANNEL`: Optional default channel name or identifier for agent status
	   messages when the webhook service supports it.
	h) `AGENT_NOTIFY_LEVEL`: Optional notification threshold such as `off`, `blockers`,
	   `handoff`, or `all`.

3) Registration Notes
	a) Future agents may register their UUID, capabilities, repository scope, current branch,
	   and subsystem lane with an IAC bus when that service exists.
	b) Registration should never require committing secrets or machine-local credentials.
	c) Any required local-only values should be documented here as names and purpose, not as
	   live values.

## Service-Orchestration Secret Names

Document expected secret names here so implementation agents can wire config
without inventing values:

1) OCI
	a) `OCI_TENANCY_OCID`
	b) `OCI_USER_OCID`
	c) `OCI_FINGERPRINT`
	d) `OCI_PRIVATE_KEY`
	e) `OCI_REGION`
	f) `OCI_COMPARTMENT_OCID`
	g) `SSH_PUBLIC_KEY`

2) SIP/Asterisk
	a) `SIP_PROVIDER`
	b) `SIP_SERVER`
	c) `SIP_USERNAME`
	d) `SIP_PASSWORD`
	e) `SIP_DID`
	f) `SIP_ALLOWED_IPS`
	g) `ASTERISK_ARI_USER`
	h) `ASTERISK_ARI_PASSWORD`

3) Voice/Agent Services
	a) `GEMINI_API_KEY`
	b) `ELEVENLABS_API_KEY`
	c) `OPENCLAW_GATEWAY_TOKEN`
	d) `DATABASE_URL`
	e) `ADMIN_SESSION_SECRET`

## Orchestration Lanes

1) Master Repo Agent
	a) Owns `.AGENT/`, README, architecture docs, branch/PR hygiene, and cross-lane
	   decisions.

2) OCI Infrastructure Agent
	a) Owns Terraform/OpenTofu, OCI networking, compute, secret references, storage,
	   logging, and deployment topology.

3) Asterisk/SIP Agent
	a) Owns PJSIP trunking, DID routing, ARI/Stasis config, RTP ranges, module allowlists,
	   and Stunt Banana pattern adaptation.

4) Voice Bridge Agent
	a) Owns ARI call lifecycle, ExternalMedia/AudioSocket, audio conversion, VAD/barge-in,
	   Gemini Live sessions, and telemetry.

5) OpenClaw Integration Agent
	a) Owns OpenClaw skills, plugin/service tool contracts, agent prompt injection, and
	   Gateway integration.

6) Admin/Compliance Agent
	a) Owns character/script/campaign UI, opt-outs, consent, call logs, transcripts,
	   disclosure rules, and rate limits.

## Open Decisions

1) Choose first runnable stack shape
	a) Options include Docker Compose for local development, OCI-first Terraform/OpenTofu, or
	   a hybrid with local app services and remote Asterisk.

2) Choose SIP provider target
	a) Telnyx, Bandwidth, DIDLogic, VoIP.ms, or another provider must be selected before
	   provider-specific trunk templates are finalized.

3) Choose voice bridge media method
	a) ARI ExternalMedia RTP is the primary design candidate.
	b) AudioSocket remains an alternative if it proves simpler for bidirectional PCM.

4) Choose OpenClaw integration boundary
	a) The likely first boundary is an agenti-call API plus OpenClaw tool/skill wrapper,
	   rather than patching OpenClaw's unmerged Asterisk provider work.
