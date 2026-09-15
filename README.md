# llm_agents_explanation

Manim scenes that explain how LLM agents work.

Right now this repo has one scene: **Declarative Attention** as a “bytes on the bus” story.

## Explain it like I’m five

Imagine your brain is a desk with lots of sticky notes.

When someone asks a long question, you write sticky notes for every part of it and keep them on the desk. That pile is the **KV cache**.

Every time you say the next word, you usually have to **look at every sticky note again**. That takes time. The desk doesn’t move — you just keep rereading it.

**Declarative Attention** is when you write a little instruction for yourself, like:

- “only look at sticky note 3”
- “look at all of them again”
- “just use what I already said”

The sticky notes stay where they are. You only change **which ones you read**. Less reading means you can answer faster.

## What’s in here

- `DeclarativeAttention_BytesOnTheBus.py` — Manim scene for that story (GPU, VRAM, PCIe, KV cache, focus / global / local tags)

Paper: [arXiv:2609.02737](https://arxiv.org/abs/2609.02737)

## Run it

```bash
manim -pqh DeclarativeAttention_BytesOnTheBus.py DeclarativeAttentionBytes
```
