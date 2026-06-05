# Stunt Banana integration plan

## Summary

`stuntbanana/stuntbanana` should be treated as an Asterisk configuration
reference, not as a direct runtime dependency. It is archived, was built for AWS
and Ubuntu 18.04, vendors an old/custom Asterisk tree, and its primary feature is
a DISA-based caller-ID spoofer. The useful parts for this project are its
minimalist Asterisk posture and private-include layout.

For agenti-call, the Asterisk server should be based on a current Asterisk LTS
package or source build on OCI, then selectively adapt Stunt Banana's safe
configuration patterns.

## Reuse from Stunt Banana

Reuse these ideas:

- `/etc/asterisk/private/*` files for credentials and deployment-specific
  dialplan fragments.
- `pjsip_wizard.conf` style templates for:
  - a default SIP trunk;
  - optional SIP phone/admin test endpoints.
- Explicit codec lists such as `ulaw`/`alaw`/`g722`, with direct media disabled
  on trunks that must pass through Asterisk.
- `rtp.conf` with a known RTP range, translated into OCI Network Security Group
  rules.
- A reduced `modules.conf`, but with the additional ARI/media modules required
  by the voice-agent bridge.
- SIP TLS for user/device registrations if softphones or desk phones are added.

## Do not reuse

Do not include these features in the robocalling stack:

- `extensions/spoofer.conf`
- DISA flows that allow arbitrary caller-ID replacement
- user-entered outbound caller ID
- default public SIP exposure beyond carrier/provider IP ranges
- the archived custom Asterisk fork as the default production build

Outbound caller ID must be selected from numbers assigned to this deployment by
the SIP provider. The admin UI and bridge API should enforce this invariant.

## Required changes for the AI voice-agent path

Stunt Banana's module list intentionally disables some modules that an
ARI/ExternalMedia voice bridge needs. At minimum, the agenti-call Asterisk
profile needs to enable and test:

```ini
; ARI / Stasis control plane
load = app_stasis.so
load = res_ari.so
load = res_ari_applications.so
load = res_ari_asterisk.so
load = res_ari_bridges.so
load = res_ari_channels.so
load = res_ari_events.so
load = res_http_websocket.so

; ExternalMedia / UnicastRTP media plane
load = chan_rtp.so
load = bridge_mixing.so

; Optional if the bridge uses AudioSocket instead of RTP ExternalMedia
; load = app_audiosocket.so
; load = chan_audiosocket.so
```

Exact module names vary by Asterisk version/package. The deployment scripts
should validate the loaded modules with `asterisk -rx "module show like ari"`,
`asterisk -rx "module show like stasis"`, and an end-to-end call smoke test.

## Target dialplan shape

The inbound path should send assigned DIDs into a Stasis app instead of a DISA
or spoofing context:

```ini
[from-pstn]
; Include generated DID routes from private config.
#include private/from-pstn

[voice-agent-inbound]
exten => _X!,1,NoOp(Voice agent inbound DID ${EXTEN})
 same => n,Stasis(agenti-call, inbound, ${EXTEN})
 same => n,Hangup()
```

Example private route:

```ini
; /etc/asterisk/private/from-pstn
exten => 15551234567,1,Goto(voice-agent-inbound,${EXTEN},1)
```

Outbound calls should originate through ARI using a verified caller ID and the
configured trunk:

```text
ARI originate -> PJSIP/<target>@DefaultTrunk -> Stasis(agenti-call, outbound, ...)
```

The bridge service should reject any outbound request whose `from_number` is not
present in the deployment's verified number registry.

## OCI network translation

Translate Stunt Banana's AWS security group guidance to OCI Network Security
Groups:

| Purpose | Protocol/ports | Source |
| --- | --- | --- |
| SSH | TCP 22 | operator IPs only |
| SIP trunk signaling | UDP/TCP 5060 or TCP 5061 | SIP provider signaling CIDRs only |
| RTP media | UDP configured RTP range, e.g. 10000-20000 | SIP provider media CIDRs where available |
| ARI HTTP/WebSocket | TCP 8088 or chosen private port | private subnet / bridge service only |
| Admin/API HTTPS | TCP 443 | public or VPN-restricted, depending on deployment |

Avoid exposing ARI to the public internet. The voice bridge should reach ARI on a
private address or localhost.

## OpenClaw integration

The official OpenClaw `@openclaw/voice-call` plugin is still useful as a model
for tool naming and call lifecycle semantics, but its documented realtime
telephony path is provider-webhook based. The Asterisk path should be a separate
service/plugin boundary:

```text
OpenClaw agent/tool
  -> agenti-call API
    -> Asterisk ARI originate/hangup/status
    -> ExternalMedia RTP bridge
    -> Gemini Live websocket
```

Recommended OpenClaw tool surface:

- `robocall.start_call`
- `robocall.end_call`
- `robocall.get_status`
- `robocall.transfer_call`
- `robocall.send_dtmf`
- `robocall.list_verified_numbers`

## Compliance and safety invariants

The system should enforce these before any call is placed:

- the destination has consent or another documented lawful basis;
- destination is not on the project opt-out list;
- campaign is inside allowed calling windows;
- caller ID is an assigned/verified number;
- script includes required AI/recording disclosures where applicable;
- call attempts are rate-limited and capped;
- "do not call", "stop", and equivalent opt-out phrases terminate future
  attempts.

These checks belong in the application/API layer, not only in prompts.
