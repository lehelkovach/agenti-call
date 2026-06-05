# agenti-call

Agentic voice-calling stack design for running an OpenClaw-powered voice agent on
Oracle Cloud Infrastructure (OCI), with Asterisk as the SIP/PSTN edge and Google
Gemini Live as the first realtime voice model target.

## Current design direction

- **Telephony edge:** Asterisk on OCI, connected to a third-party SIP trunk/DID
  provider.
- **Voice bridge:** A custom ARI/ExternalMedia service that connects Asterisk
  call media to Gemini Live and OpenClaw tools.
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
