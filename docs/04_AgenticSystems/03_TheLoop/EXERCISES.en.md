# Exercises · Chapter 3

Three exercises. They require you not just to run the loop but to *modify* it. That is where the substance lies.

---

## Exercise 1 · Context hygiene

`02_token_growth.py` shows: `tokens_in` grows with every turn because the entire conversation is re-sent. In a five-turn loop `tokens_in` in turn 5 can easily be four times as large as in turn 1.

**Task:** Modify `02_token_growth.py` so that **tool results are summarised between turns**. Concretely:

1. After each tool call, instead of writing the whole raw result into the history (e.g. `[observation] fetch_news({...}) = {"headlines": [3 long sentences]}`), write a one-sentence summary (e.g. `"news: 3 headlines about SAP SE"`).
2. Run the script again. Compare the token curve to the original.

**What you learn:** *context hygiene* is one of the cheapest and most effective optimisations in the agent loop. And it is always *your* job — no framework does it right.

**Bonus:** Instead of summarising after every turn, keep the last three raw observations and summarise only the *rest*. Why is that better than "summarise everything"? (Hint: the model needs the fresh detail to make its decision for the *current* turn.)

---

## Exercise 2 · A second loop guard

`01_basic_loop.py` has a loop guard that breaks when the same tool signature (name + args) comes three times in a row. But there is a subtle variant it does *not* catch: what if the model flips back and forth between two tool calls?

```
Turn 1: calculator(multiply, 100, 5) = 500
Turn 2: calculator(divide, 500, 5)   = 100
Turn 3: calculator(multiply, 100, 5) = 500
Turn 4: calculator(divide, 500, 5)   = 100
...
```

The model is going in circles, but no individual call repeats immediately.

**Task:** Extend the loop guard so it also detects **short cycles** (length 2 or 3). Concretely:

1. Keep a list of the last N tool signatures (e.g. N=6).
2. On each turn, check: do the last K entries form a repeated pattern (K ∈ {2, 3})?
3. If yes: abort and print which sequence was detected.

**What you learn:** that "there is no obvious error" is not the same as "the agent is making progress". Loop guards in production are never as simple as "is the last call the same as the previous one". Cycle detection is its own problem.

**Bonus:** Look up the *"budget"* approach — instead of counting turns, count cumulative cost (in tokens or EUR). Why is that often the *only* really reliable stop condition for a commercial agent?

---

## Exercise 3 · The fifth kind of retry

`03_retry_strategies.py` shows four strategies. But in practice you rarely use just one — you *combine*. And there is a fifth strategy the script is missing:

> **E · "hedged" requests** — make TWO calls *in parallel*, to the primary and to the fallback backend. Take the first response that comes back. Throw the second away.

**Task:** Build a `strategy_hedged()` function.

1. Use `concurrent.futures.ThreadPoolExecutor` or `asyncio`.
2. Fire off `TOOL.price_lookup(SKU)` and `TOOL.fallback_lookup(SKU)` in parallel.
3. Take the first successful response.
4. Measure the latency.

Then discuss:

- When is strategy E better than D? (Hint: latency.)
- When is it worse than D? (Hint: cost.)
- When should you *not* use E? (Hint: for calls with side effects — e.g. database writes.)

**What you learn:** retry strategies are not a black-box choice — every one has a concrete trade-off (latency vs cost vs safety), and the right choice depends on context. Large cloud providers use hedged requests routinely for read-only operations; for write operations almost never.

---

## How you know you have understood this chapter

If you can explain in **one sentence** why the sentence *"the loop is yours to write"* holds for all agent systems — including those built on LangChain or Semantic Kernel — you're done with Chapter 3.

In two sentences: the framework writes you the loop, but it does not decide which stop conditions you want, which retry strategy fits which error, or how much context to carry between turns. Those are always your decision — and if you don't make it consciously, you've picked the default.