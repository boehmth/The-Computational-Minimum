# Chapter 4 · Reasoning Inside

**The other loop — the one you didn't write.**

One miniature. It sends the same question to two models: a normal gpt-4o and a reasoning-capable Claude 4.5. With Claude you see two text streams come back — the private *thinking tokens* and the final answer. Both in a single HTTP call.

---

## 📜 Historical context

Up through Chapter 3 the loop lived in *your* code. Every turn was a separate HTTP call. Every "keep going or done?" decision sat as an `if` in your Python file.

That changed in autumn 2024.

**September 2024 · OpenAI o1.** For the first time in a commercial model: the model "thinks" *before* it answers. A specialised training on reasoning traces (RLVR — Reinforcement Learning from Verifiable Rewards) had given OpenAI a model that *no longer needs a chain-of-thought in the prompt* — it generates one internally. The user sends a question, waits 10–60 seconds, and gets an answer. Between "question" and "answer" lie hundreds to thousands of thinking tokens which the user pays for but never sees.

**February 2025 · Claude 3.7 extended-thinking.** Anthropic follows suit — with an important difference: the thinking tokens are *visible* to the developer, as their own field in the API response. You can literally watch the model talking to itself before formulating the final answer.

**Spring 2025 · DeepSeek-R1 open-weight.** For the first time a reasoning model available for self-hosting. You can download the weights, run the model on your own hardware, and see the thinking tokens in the generated text directly (as `<think>...</think>` tags).

Together these three events created a new category of loop:

> **The loop no longer lives in your code — it lives inside the model itself.**

From *your* API perspective it is still *one* HTTP call. One `chat()` call, one response object. But the response object now carries two streams instead of one — and you pay for both.

---

## 🔬 The one miniature

### `src/01_thinking_visible.py` — the internal loop, made visible

Same task, sent to two models:

> *"A tank holds 240 litres. Pipe 1 fills it at 12 L/min, pipe 2 at 8 L/min, a drain empties at 5 L/min. All three run simultaneously. How long until the tank is full?"*

**Model A — gpt-4o (baseline):** a normal one-shot model. Answers with a reasoning path and an answer, all in one text stream. No thinking visible. The reasoning path *is* the answer.

**Model B — Claude 4.5 Sonnet with `thinking={"type": "enabled"}`:** the model produces two separate content blocks:

- `content[type=thinking]` — the internal chain-of-thought (typically 500–2000 tokens for this task)
- `content[type=text]` — the final, cleaned-up answer (typically 100–300 tokens)

The script shows both streams in two separate `hard_card`s. You see side by side what the model *thinks* and what it *says* — and how many tokens each costs.

At the end the script prints a provider matrix: which vendor exposes the thinking tokens in the response, and who hides them but lets you pay for them anyway.

| Vendor | Thinking in response? | Field |
|---|---|---|
| **Anthropic Claude** | ✓ yes | `content[type=thinking]` |
| **OpenAI o1/o3/o4** | ✗ no — only the number | `usage.reasoning_tokens` |
| **Google Gemini 2.5+** | ✗ opt-in | `thinking_config.include_thoughts=True` |
| **DeepSeek-R1** | ✓ yes | `<think>...</think>` inline |

---

## 💡 Wow moment

When you run the script for the first time you'll notice two things:

**1. The thinking block is longer than the answer.** For the tank task Claude may crank through 800 tokens of thinking before delivering 150 tokens of answer. That is roughly a 5:1 ratio. For more complex tasks it becomes even more extreme.

**2. The reasoning path in the thinking is *better* than the one in the gpt-4o response.** Not because Claude is smarter — but because Claude is *listening to itself*. It takes intermediate steps, verifies, corrects. It calculates: *"Net flow = 12 + 8 - 5 = 15 L/min. Time = 240 / 15 = 16. Check: 16 min × 15 L/min = 240 ✓."* That *"check"* at the end is the core — the model tests its own answer *before* delivering it.

That is qualitatively the same thing as Chapter 3 miniature 3 strategy D (LLM-guided recovery). Only that here it happens automatically, inside a single call, invisible to anyone who doesn't specifically ask.

**What you don't see — and pay for anyway:** if you use OpenAI o3 with `reasoning_effort="high"`, the provider internally samples *N* different reasoning traces in parallel and picks the best. Those *N* traces are not shown to you (not even anonymised) and you get only the one chosen answer — but the token bill is for all *N*. That is why "reasoning: high" costs 5–20× more than "reasoning: minimal" without the visible answer getting longer.

That's why: **three loop levels, three control levels.** Your loop (Chapter 3), the loop in the model (Chapter 4 miniature 1), and the loop at the provider's (invisible). You pay for each. You control only the first.

---

## 🚀 Run it

```powershell
cd "C:\Users\D041506\Source\RPT Agent"
python "Agentic Systems/04_ReasoningInside/src/01_thinking_visible.py"
```

Prerequisite: the reasoning model must be deployed in your GenAI Hub resource group. Set in `.env`:

```
LLM_REASONING_MODEL=anthropic--claude-4.5-sonnet
```

(For other models like `anthropic--claude-4.5-opus` or o3 the level of detail changes, but the pattern is the same.) Expected runtime: 10–60 seconds per model — reasoning models are deliberately slow, that *is* the trade-off.

---

## 🧭 Bridge to the next chapter

Chapter 3 shows: **the loop can live in your code.** Chapter 4 shows: **the loop can live in the model.** In both cases the loop is *local* — it lives between you and the model. Only two parties involved.

Chapter 5 introduces a third party: **foreign tools and foreign agents**, reachable via a standardised protocol. That is the point at which your colleagues' tools (or a vendor's) can slot cleanly into your loop — without you writing a bespoke API wrapper for each.

The protocol is called **MCP** (Model Context Protocol, Anthropic, November 2024). And because agents should also talk to each other, there is an extension since early 2025: **A2A** (Agent-to-Agent, Google).

Both are in Chapter 5 as runnable miniatures.