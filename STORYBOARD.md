# Scene-wise storyboard

Declarative Attention — bytes-on-the-bus cut.

Paper: [arXiv:2609.02737](https://arxiv.org/abs/2609.02737)

This is the planning document we used to direct the Manim scene. Keep the spine in order. Do not add extra architecture lectures.

## Design rules

- Captions hold about 3 seconds when they carry the argument (reading speed ~15 characters per second).
- No abstract arrows. All data movement is byte packets: small colored squares streaming through a channel. Packet density = bytes moved.
- Time encodes cost: a vanilla decode step takes ~2.6s on screen (bus saturated); a focused DA step is ~0.8s so the viewer feels tokens get cheaper.
- The right panel is the host: first the model checkpoint, then the request, then the model's streaming output.
- Dim unused KV in place. Never unmount it. That is the punchline.

## Beat list

| Time | Beat | On screen |
| --- | --- | --- |
| 0:00–0:04 | Empty GPU | GPU outline, SM rows, L2, VRAM box draw in. |
| 0:04–0:08 | Hold | Caption: empty GPU — compute (SMs) on top, VRAM below. VRAM conspicuously empty. |
| 0:08–0:10 | Host + bridge | Host panel (checkpoint: embed, L0–L3, head) and the PCIe bridge appear. Caption: a model arrives — weights stream over PCIe. |
| 0:10–0:18 | Weights load | Per layer (~1.25s): byte packets cross the bridge into VRAM; that layer's weights segment lights; the host copy dims. |
| 0:18–0:21 | Loaded | "model weights" label lands. Caption: weights resident in VRAM — the GPU is ready. |
| 0:21–0:24 | Request arrives | Checkpoint fades; request appears: sys+question (grey) + magic chunks 1–6 (colored). Caption: a long request, split into ~2K-token magic chunks. |
| 0:24–0:33 | Prefill | Per chunk (~1.25s): packets cross the bridge into the SMs (K/V computed), then drop into VRAM as that chunk's KV block. Host rows dim as sent. |
| 0:33–0:35 | Prefill done | Caption: prefill done — the KV cache sits in VRAM and never moves again. |
| 0:35–0:38 | Panel switch | Request fades; "model output" + "KV bytes read per token" bar; "response KV" slot. Caption: generating — each new token must read the old keys/values. |
| 0:38–0:41 | Vanilla step (slow) | ~2.6s: dense packets from scaffold + all chunks into the SMs; bar at 100% (red); first word; green response-KV square appended. |
| 0:41–0:44 | Steps 2–3 | ~1.5s each: same full stream, more words, more response KV. |
| 0:44–0:47 | The cost | Caption: every token — all that KV crosses the bus as a read, not a move. |
| 0:47–0:50 | Memory-bound | Caption: decode is memory-bound — the bus sets the speed, not the ALUs. |
| 0:50–0:53 | DA title | Declarative Attention. Caption: the model writes what it needs into its own output. |
| 0:53–0:55 | The tag | Output types `<focus magic_chunks="3">`, boxed yellow. Caption: the engine parses the tag like a tool call. |
| 0:55–0:57 | The mask | Other chunks dim in place; "masked (still resident)". No packet moves — masking is metadata only. |
| 0:57–1:00 | Focused steps ×3 | ~0.8s each: sparse packets from scaffold + C3 + response; bar drops; tokens land faster. |
| 1:00–1:03 | The numbers | Caption with paper result (fewer attended tokens, small accuracy hit). |
| 1:03–1:06 | `<global>` | Tag typed; blocks relight; one slow dense step; bar back to 100% red. |
| 1:06–1:08 | `<local>` | Tag typed; all magic chunks dim. Caption: write the answer from scaffold + its own response. |
| 1:08–1:10 | Answer | Two fast sparse steps; tiny bar; answer appears in output. |
| 1:10–1:13 | The point | Caption: no KV block ever moved — DA only changed which bytes cross the bus. VRAM pulses once. |
| 1:13 | End | Final frame holds. |

## Spine (short form)

1. Empty GPU  
2. Weights stream host → PCIe → VRAM  
3. Long request as magic chunks  
4. Prefill into KV that stays  
5. Vanilla decode (slow, full read)  
6. Focus tag; unused KV dims in place  
7. Focused decode (fast, sparse)  
8. Global, then local  
9. Punchline: KV never moved  

