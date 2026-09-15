# Voiceover cue sheet

What we send to TTS / Grok audio, and how it should sit on the picture.

Use **one speaker**. Lines must be **non-overlapping**. Leave gaps between lines so captions can breathe.

## How to use this

1. Render the silent Manim cut first.
2. Generate each line below as its own clip (Grok audio, ElevenLabs, or similar).
3. Lay clips at the cue start times — do not stack them.
4. Mux onto the silent video.

If two lines collide, shorten the copy or slide the later cue. Never overlap.

## Final non-overlapping cues (revised cut)

These are the spoken lines Astra mapped for the remux of `declarative_attention.mp4` (~54s).

| Cue | Start–end (s) | Spoken line |
| --- | --- | --- |
| V1 | ~0.0–4.5 | Empty GPU. Compute on top. Memory below. |
| V2 | ~5.0–9.0 | Weights cross PCIe and stay in VRAM. |
| V3 | ~10.0–13.0 | A long request, split into magic chunks. |
| V4 | ~14.0–19.0 | Prefill turns each chunk into keys and values that stay in VRAM. |
| V5 | 23.8–30.2 | Vanilla decoding reads the full KV cache each step. The bus sets the speed. |
| V6 | 32.8–38.8 | A focus tag narrows attention. Other seats dim, but they stay resident. |
| V7 | 41.0–45.5 | Attention goes global, then local, when the model needs to look around or answer. |
| V8 | 47.6–52.6 | The key idea: attention changed, but the KV cache never moved. |

Clip durations from the revised Grok VO batch (for packing):

| Clip | Approx length (s) |
| --- | --- |
| 01 | 4.6 |
| 02 | 3.6 |
| 03 | 2.3 |
| 04 | 4.4 |
| 05 | 6.4 |
| 06 | 6.0 |
| 07 | 4.5 |
| 08 | 5.0 |

## On-screen caption copy (picture source of truth)

These captions live in `DeclarativeAttention_BytesOnTheBus.py`. Voiceover should agree with them, even if the spoken line is a little shorter.

1. Empty GPU. Compute on top. Memory below.  
2. GPU computes. Host coordinates. PCIe connects them.  
3. Weights cross PCIe and stay in VRAM.  
4. Same GPU. Weights resident. VRAM is no longer empty.  
5. A long request, split into ~2K-token magic chunks.  
6. Prefill: SMs turn each chunk into keys and values.  
7. Prefill done. KV sits in VRAM and does not move again.  
8. Generating: each new token must reread the old keys.  
9. Every token rereads the full KV. The bus sets the speed.  
10. The model writes where it needs to look — in its own output.  
11. The engine parses the tag. Unused KV dims. It is still there.  
12. This step reads SYS + C3. Across a whole decode: Gemma-4-31B attends 52% fewer tokens, −1.3pp.  
13. `<global>` surveys the full context when it needs to look around.  
14. `<local>` drops every magic chunk. Scaffold + the reply stay.  
15. No KV block ever moved. DA only changed which bytes cross the bus.  
16. End card: KV never moved.

## Voice rules

- One voice for the whole film.  
- No bed music under the argument lines unless it is very quiet.  
- Prefer gaps of 0.5s+ between VO lines.  
- When picture is dense (packet storms), let VO finish before the next visual joke starts.  

