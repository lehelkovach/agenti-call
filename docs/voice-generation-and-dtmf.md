# Voice generation and DTMF design

## Summary

agenti-call should support two separate audio/control capabilities:

1) **Voice generation** for the agent's spoken responses and character voices.
2) **DTMF/keypad signaling** for dialing digits into phone menus, conference
   bridges, IVRs, extensions, and PIN prompts.

These should not be conflated. Spoken voice can come from Gemini Live,
ElevenLabs, or another TTS provider. Keypad dialing should normally be sent as
telephony DTMF events through Asterisk rather than synthesized as spoken audio.

## ElevenLabs voice generation

ElevenLabs should be treated as an optional TTS/voice provider alongside Gemini
Live's native audio output.

Recommended uses:

- character-specific text-to-speech when Gemini Live voices are not enough;
- low-latency TTS for scripted outbound calls;
- admin-managed voice profiles linked to characters;
- fallback TTS when the realtime speech-to-speech provider is unavailable;
- pre-generating static prompts such as disclosures, greetings, and voicemail
  messages.

Implementation boundary:

```text
OpenClaw / script engine
  -> agenti-call voice bridge
    -> voice provider adapter
      -> Gemini Live native audio OR ElevenLabs streaming TTS
    -> Asterisk media playback
```

The first implementation should expose a provider-neutral voice interface:

```text
synthesize_speech(text, character_id, voice_profile_id?, format?)
stream_speech(text_stream, character_id, voice_profile_id?)
```

The adapter should store only provider IDs and configuration references in the
database. Do not store API keys, raw private voice samples, or cloned voice
artifacts in git.

Expected configuration names:

- `ELEVENLABS_API_KEY`
- `ELEVENLABS_DEFAULT_VOICE_ID`
- `ELEVENLABS_MODEL_ID`

## Voice samples and consent

If the admin UI accepts voice samples:

- store samples outside git, preferably object storage;
- require explicit consent metadata for any cloned or reference voice;
- track who uploaded the sample, when, and for which character/use case;
- allow disabling or deleting a voice profile;
- avoid training or cloning voices from samples without a documented lawful
  basis and project-level approval.

## DTMF/keypad dialing

DTMF should be a call-control action, not a TTS feature.

Preferred path:

```text
OpenClaw tool call / script step
  -> agenti-call API send_dtmf(call_id, digits)
    -> voice bridge validates sequence
      -> Asterisk ARI sends DTMF on the SIP channel
        -> trunk/provider emits RFC 4733 telephone-event or supported DTMF mode
```

Fallback path when provider/channel support requires it:

```text
send_dtmf(call_id, digits, mode="inband")
  -> generate dual-tone audio for each digit
  -> inject/play tones through Asterisk media path
```

The default should be Asterisk/provider DTMF signaling. In-band tone synthesis
should be a compatibility fallback because it is more sensitive to codecs,
transcoding, volume, and noise suppression.

## Structured agent output contract

The LLM must not be allowed to emit arbitrary raw telephony commands. DTMF output
should be structured and validated.

Recommended tool action:

```json
{
  "action": "send_dtmf",
  "call_id": "call_123",
  "digits": "ww123456#"
}
```

Allowed symbols:

- digits: `0` through `9`
- star: `*`
- pound/hash: `#`
- pause markers: `w` or `,` after normalization, if supported by the bridge

Validation rules:

- reject empty sequences;
- reject unsupported symbols;
- cap sequence length;
- require an active call;
- log the action without exposing sensitive PIN values unless debugging is
  explicitly enabled and safe;
- rate-limit repeated DTMF actions.

## Script and decision-tree use cases

The admin/script layer should support explicit steps such as:

```yaml
- say: "One moment while I join the conference bridge."
- dtmf: "ww123456#"
- say: "I am connected."
```

The agent may also request DTMF when a caller or IVR asks for keypad input, but
only through the validated `send_dtmf` action. For sensitive values such as PINs,
prefer configured secret references over prompt-visible literals.

## Asterisk configuration implications

Asterisk/PJSIP endpoint templates should set a DTMF mode supported by the SIP
provider, commonly `auto`, `rfc4733`, or provider-specific guidance. The bridge
must test DTMF end-to-end with the selected SIP trunk because IVR behavior varies
by carrier and codec.

The Asterisk design should preserve:

- ARI private network access only;
- verified caller ID enforcement;
- no DISA caller-ID spoofing flow;
- clear call logs for DTMF actions while protecting PIN-like values.

## Open implementation decisions

1) Whether the first voice provider implementation uses Gemini Live only, or
   includes ElevenLabs TTS from the first runnable bridge.
2) Whether static prompt pre-generation is needed before live TTS streaming.
3) Which DTMF path each SIP provider supports best: RFC 4733, SIP INFO, or
   in-band audio.
4) How to redact PIN-like DTMF sequences in logs while preserving enough
   observability to debug IVR failures.
