# agenti-call

Agentic voice-calling stack design for running an OpenClaw-powered voice agent on
Oracle Cloud Infrastructure (OCI), with Asterisk as the SIP/PSTN edge and Google
Gemini Live as the first realtime voice model target.

## Current design direction

- **Telephony edge:** Asterisk on OCI, connected to a third-party SIP trunk/DID
  provider.
- **Voice bridge:** A custom ARI/ExternalMedia service that connects Asterisk
  call media to Gemini Live, optional ElevenLabs TTS, DTMF/keypad signaling, and
  OpenClaw tools.
- **Agent runtime:** OpenClaw Gateway plus a robocall/voice-agent skill and
  plugin/service API.
- **Admin surface:** Web UI for characters, scripts, decision trees, campaigns,
  voices, transcripts, call logs, consent, and opt-out state.

## Stunt Banana integration stance

[stuntbanana/stuntbanana](https://github.com/stuntbanana/stuntbanana) is useful
as a reference for minimalist Asterisk deployment patterns, but it is archived,
AWS-oriented, and centered on caller-ID spoofing/DISA flows. This project should
reuse only the safe Asterisk configuration ideas:

- private include files for trunk/device secrets;
- explicit PJSIP trunk and phone templates;
- TLS for SIP devices;
- a reduced Asterisk module allowlist;
- narrow SIP/RTP firewall rules.

The spoofing dialplan and DISA caller-ID replacement flow should not be included
in this system. Outbound caller ID must be restricted to verified/assigned
numbers from the SIP provider.

See [docs/stuntbanana-integration.md](docs/stuntbanana-integration.md) for the
integration plan and required Asterisk changes.

See [docs/voice-generation-and-dtmf.md](docs/voice-generation-and-dtmf.md) for
the ElevenLabs voice-generation and DTMF/keypad dialing design.

See [docs/testing-and-dev-deployment.md](docs/testing-and-dev-deployment.md) for
the current test status and the planned mock, Asterisk lab, OCI dev, live SIP,
and OpenClaw skill-extension validation path.

## Agent orchestration

This repo imports the `.AGENT/` operating surface from
[`lehelkovach/agent-repo-boilerplate`](https://github.com/lehelkovach/agent-repo-boilerplate)
and customizes it for agenti-call.

Agents should start by reading:

- `.AGENT/agent.md` for the live prompt and repo-specific orchestration rules;
- `.AGENT/agent-run.md` for recurring startup checks;
- `.AGENT/agent-run-once.md` for one-time queued work;
- `.AGENT/agent-action-log.md` for prior agent activity and handoffs;
- `.AGENT/dev-notes.md` for service lanes, expected secret names, and open
  orchestration decisions.

Validate agent support files with:

```sh
python3 .AGENT/tests/agent_architecture_smoke.py
```
