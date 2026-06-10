# Testing and dev deployment plan

## Current state

The repository currently has **agent-orchestration smoke validation only**. It
does not yet contain a runnable robocaller runtime, Asterisk deployment, OpenClaw
plugin package, Terraform/OpenTofu root, Docker Compose stack, or live telecom
test harness.

Current executable validation:

```sh
python3 .AGENT/tests/agent_architecture_smoke.py
git diff --check
```

The smoke test verifies that the `.AGENT/` operating surface, docs, and required
architecture keywords stay present. It does **not** validate SIP, RTP, Asterisk,
Gemini Live, ElevenLabs, OpenClaw plugin behavior, or real calls.

## Target validation layers

Testing should be added in layers so failures are diagnosable before involving
live telecom.

### 1) Repository and contract tests

Purpose: validate static contracts without network access.

Planned checks:

- `.AGENT` smoke test.
- Markdown/link checks for docs.
- JSON/YAML/schema validation for future config examples.
- Tool contract tests for actions such as:
  - `robocall.start_call`
  - `robocall.end_call`
  - `robocall.get_status`
  - `robocall.send_dtmf`
  - `robocall.synthesize_speech`
- Validation tests for:
  - verified caller ID enforcement;
  - opt-out and consent gates;
  - DTMF digit normalization and redaction;
  - script/decision-tree step parsing.

### 2) Mock-provider service tests

Purpose: validate application behavior without Asterisk, SIP, Gemini, or
ElevenLabs.

Planned mock components:

- fake Asterisk ARI server;
- fake SIP call state machine;
- fake Gemini Live WebSocket;
- fake ElevenLabs TTS endpoint;
- fake OpenClaw Gateway/tool dispatcher.

Required test flows:

- outbound call request accepted when consent and caller ID checks pass;
- outbound call rejected when destination opted out;
- inbound call routed to a selected character/script;
- agent emits structured `send_dtmf`, bridge validates and sends mock DTMF;
- agent asks for speech, bridge calls the selected mock voice provider;
- call lifecycle events are persisted in order;
- transcripts/logs redact PIN-like DTMF sequences.

### 3) Local development deployment

Purpose: run the app stack locally with deterministic mock telecom.

Recommended first local stack:

```text
docker compose
  - agenti-call API / voice bridge
  - mock ARI server
  - mock OpenClaw Gateway adapter
  - database
  - admin frontend
```

Local development should not require real SIP credentials or public phone
numbers. The first useful local command should prove the control plane:

```sh
agenti-call dev smoke --scenario outbound-mock
```

Expected result:

- creates a mock call;
- applies compliance gates;
- runs a sample character/script;
- emits a mock TTS response;
- emits optional DTMF;
- ends the call;
- writes structured call events.

### 4) Asterisk lab deployment

Purpose: validate Asterisk ARI/Stasis and media integration before using a SIP
trunk.

Recommended lab shape:

```text
local or OCI dev VM
  - Asterisk
  - agenti-call voice bridge
  - SIP softphone endpoint
  - mock Gemini/ElevenLabs where possible
```

Required checks:

- ARI credentials are private and reachable only from the bridge;
- `Stasis(agenti-call, ...)` receives inbound test calls;
- ARI originate can create outbound calls to a SIP softphone;
- ExternalMedia or AudioSocket media path can pass test audio;
- DTMF can be sent and received through the selected Asterisk path;
- no DISA/caller-ID spoofing dialplan is enabled.

### 5) OCI dev deployment

Purpose: validate infrastructure and network behavior in the target cloud.

Recommended dev deployment:

```text
OCI dev compartment or tagged resources
  - VCN and subnets
  - Asterisk VM with reserved public IP
  - private app/bridge host or container host
  - database
  - object storage for recordings/samples
  - logs/metrics
```

Required OCI checks:

- SSH is restricted to operator IPs;
- SIP signaling is restricted to provider CIDRs;
- RTP range matches `rtp.conf` and OCI Network Security Groups;
- ARI is private only;
- secrets are injected from Cursor/OCI secret surfaces, not committed;
- teardown is documented for all dev resources.

### 6) Live SIP trunk smoke tests

Purpose: validate the smallest real-phone behavior safely.

Live test prerequisites:

- assigned test DID;
- verified outbound caller ID;
- one allowlisted test destination number;
- documented consent for the test number;
- low call-rate limits;
- recording disabled unless consent is explicit;
- clear test script that identifies itself as an AI test call where required.

Minimum live tests:

1) Inbound:
	- call the test DID;
	- Asterisk routes to `Stasis`;
	- voice bridge starts a session;
	- agent speaks a short greeting;
	- caller says a short phrase;
	- call ends cleanly.

2) Outbound:
	- start a call through the OpenClaw tool or agenti-call API;
	- verify caller ID is assigned/verified;
	- agent says a short scripted message;
	- call ends cleanly.

3) DTMF:
	- call a test IVR, conference bridge, or local Asterisk extension;
	- send a short validated DTMF sequence;
	- verify the remote side receives it;
	- verify logs redact sensitive sequences.

4) Voice provider:
	- run one call with Gemini Live native audio;
	- run one call with ElevenLabs TTS if the adapter is enabled;
	- compare latency, interruption behavior, and failure fallback.

## OpenClaw skill-extension testing

The OpenClaw integration should be validated in two modes.

### Mock OpenClaw skill test

Purpose: prove the skill/tool contract before placing calls.

Expected skill behavior:

- OpenClaw loads a local `robocall` skill or plugin-provided skill.
- The skill exposes or documents safe tool actions.
- The agent can call mock tools such as:
  - `robocall.start_call`
  - `robocall.get_status`
  - `robocall.send_dtmf`
  - `robocall.end_call`
- Tool calls return deterministic mock call IDs and states.
- Attempts to call non-allowlisted numbers fail with clear errors.

Example mock test prompt:

```text
Use the robocall skill in mock mode. Start a test call to the configured mock
allowlisted number, say the sample greeting, send DTMF "12#", get status, then
end the call. Do not place a real phone call.
```

### Live OpenClaw skill test

Purpose: prove an OpenClaw agent can drive the deployed bridge.

Prerequisites:

- OpenClaw Gateway running with the robocall skill/plugin enabled;
- agenti-call API reachable from the Gateway;
- OpenClaw tool token configured;
- a single allowlisted test number;
- live-call mode explicitly enabled.

Example live test prompt:

```text
Using the robocall skill in live-test mode, call the allowlisted test number,
use the "smoke-test-character" script, disclose this is a test AI call, wait for
one response, then end the call. Do not call any other number.
```

Pass criteria:

- OpenClaw emits only validated tool calls;
- agenti-call accepts the request only because live-test mode and allowlist are
  configured;
- Asterisk places or receives the call;
- the voice bridge completes one conversational turn;
- call status and transcript/call-event logs are available;
- the OpenClaw session receives a final call summary.

## Development deployment environments

Recommended environment names:

1) `mock-local`
	- no real telecom;
	- no external voice providers required;
	- suitable for CI.

2) `asterisk-lab`
	- local or dev VM Asterisk;
	- SIP softphone only;
	- no PSTN trunk.

3) `oci-dev`
	- OCI network and Asterisk VM;
	- optional SIP trunk;
	- restricted to test DIDs and allowlisted numbers.

4) `live-test`
	- explicitly enabled real call tests;
	- strongest rate limits and allowlists;
	- never used for broad campaigns.

## Readiness gates before broader live use

Before this project can move beyond a single allowlisted live test:

- mock tests pass in CI;
- Asterisk lab tests pass;
- OCI deployment is reproducible and teardown is documented;
- OpenClaw skill mock test passes;
- one inbound and one outbound live smoke test pass;
- DTMF test passes with the chosen SIP provider;
- opt-out and consent gates are enforced in code;
- call logs redact secrets and PIN-like DTMF;
- failure behavior is tested for provider timeouts, no answer, busy, and hangup.
