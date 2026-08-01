# Chapter 2 · Tools and the First Plan

**How control over the flow shifts, at runtime, from the developer to the model.**

Two miniatures. The first shows a single tool call. The second shows three tasks and three different call orderings — none written in Python.

---

## 📜 Historical context

In October 2022 Yao et al. published the paper *"ReAct: Synergizing Reasoning and Acting in Language Models"* (arXiv:2210.03629). The title sounds obvious today — the content was provocative at the time:

The standard model back then was *"prompt in, answer out"*. You gave the model a chain-of-thought example and got an answer at the end. The model decided nothing. It computed, or pretended to compute.

ReAct proposed: **the model should distinguish between thoughts and actions.** An action token means a tool call. The model produces thoughts (`Thought:`), then an action (`Action: search[milk]`), then the runner reads the observation back (`Observation: 3.20 EUR`), then more thoughts. The loop is born.

Five months later (March 2023) Meta published the *Toolformer* paper (arXiv:2302.04761): models can learn *when to* call a tool themselves. Three months after that (June 2023) OpenAI shipped *function calling* — the first commercial API with a JSON-schema-based tool interface.

Two connected observations from that period:

1. **Tool use requires no special model architecture.** Any capable language model can use tools if you explain in the system prompt what the tool is called and what the call looks like. Function calling is more convenient, but not necessary.
2. **Control over the flow shifts.** In the pre-ReAct era the developer decided every branch and every loop. After ReAct the model decides at runtime — which tool, with which arguments, in which order. That is the actual break that brought us here.

Both observations underlie the two miniatures.

---

## 🔬 The two miniatures

### `src/01_give_it_a_tool.py` — the first tool call

We take the same multiplication as in Chapter 1 (`43,177 × 14,694`). This time the system prompt says: *"You have a tool called `calculator`. To use it, answer exclusively with a JSON object."*

The model does not answer with a number. It answers with:

```json
{"tool": "calculator", "operation": "multiply", "a": 43177, "b": 14694}
```

A tiny orchestrator (10 lines of Python in the same script) parses the JSON, calls the Python function `calculator(...)`, and the answer is correct.

**What is actually happening here?** Two separated responsibilities:

- **The model** identifies the intent (*here we need to multiply*) and produces the structured representation (*JSON with the correct arguments*). That is language work.
- **The code** parses the structure and executes the deterministic operation. That is compute work.

That is the dividing line that carries everything after. The error from Chapter 1 is gone. Not because the model computes better — but because the model no longer computes.

### `src/02_model_plans.py` — three tasks, three plans

We extend the tool set by a second one: `currency_converter(amount, source, target)`. Both tools are described in the system prompt. Then we hand the model three natural-language tasks:

- *"What is the total price for 43,177 units at 14,694 EUR each?"*
- *"I have 132,877 USD budget, how many units can I buy at 5.30 EUR each?"*
- *"What is the total price in EUR for 43,177 units at 14,694 USD each?"*

The model produces a *plan* for each task — an ordered list of tool calls:

- Task 1 → `[calculator(multiply, 43177, 14694)]`
- Task 2 → `[currency_converter(132877, USD, EUR), calculator(divide, ..., 5.30)]`
- Task 3 → `[calculator(multiply, 43177, 14694), currency_converter(..., USD, EUR)]`

**Three tasks, the same tool set, three completely different call orderings.** No `if/elif` in our code. The developer did *not* write "if USD appears in the question, then convert". The model figured it out itself — freshly for each task.

---

## 💡 Wow moment

Precisely this is Principle 2 in action:

> **The model decides the steps at runtime. Not the developer, not in advance.**

Before 2023 you would have written two different handlers (or one with a branching tree) for tasks 2 vs 3. After ReAct you write one tool description — and the same description, unchanged, covers both tasks. The model figures out the order itself.

What you lose: **predictability**. On the next run the model could pick a different plan for task 3 — for example convert the unit price to EUR first, then multiply. Both plans are mathematically correct, but they are not the *same* plan. That is the trade-off you accept with P2, and it will come up again in Chapter 6 (determinism, replay, audit).

What you gain: **adaptability to new tasks without code changes**. When someone comes tomorrow and asks *"What is the total price in USD for 43,177 units at 5.30 EUR each?"* — that is a fourth task, and your code already works for it. Without anyone writing `if usd_target:`.

---

## 🚀 Run it

```powershell
cd "C:\Users\<USERNAME>\Source\RPT Agent"

python "Agentic Systems/02_ToolsAndPlanning/src/01_give_it_a_tool.py"
python "Agentic Systems/02_ToolsAndPlanning/src/02_model_plans.py"
```

Expected output of `02_model_plans.py` — your model will pick slightly different wording, but the *structure* will match:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    TASK 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌── Task ──────────────────────────────────────────────────────────
│  Was ist der Gesamtpreis für 43177 Einheiten zu je 14694 EUR?
└───────────────────────────────────────────────────────────────────

┌── Model's plan ──────────────────────────────────────────────────
│  intent: total price berechnen
│  step 1: calculator({'operation': 'multiply', 'a': 43177, 'b': 14694})
└───────────────────────────────────────────────────────────────────
```

...and similar for all three tasks, each with a different plan.

Note that Task 2 produces a two-step plan with a `<result_from_currency_converter>` placeholder — the model knows the second step depends on the first, but the first hasn't run yet. That placeholder is exactly the motivation for Chapter 3.

---

## 🧭 Bridge to the next chapter

Up to this point it was *one* tool call per task (miniature 1) or *one plan* per task which we only *read* but do not execute (miniature 2). Task 2 in the second miniature already shows: the plan has *two* steps. The second step depends on the result of the first (you have to know how many EUR the 132,877 USD are before you can divide).

That means: the orchestrator must execute step 1, return the result to the model, and the model must decide step 2 in the light of that result. That is a **loop**, not a linear execution.

And precisely this loop — what it costs, what it can get wrong, and who is responsible for what within it — is Chapter 3.