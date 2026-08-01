# Chapter 6 · When NOT to Build

**The verdict.**

Up to now every miniature has shown *what is possible*. This chapter shows *what is not sensible*. Two miniatures. Two anti-patterns. One two-question test.

---

## 📜 Historical context

After Chapter 5 you stand at the most dangerous point in the journey: everything is possible, everything scales, everything is standardised. That is exactly the situation in which most bad agent systems get built.

To recap what we've built:

- **Chapter 1** — LLMs are text-in / text-out. But they don't compute.
- **Chapter 2** — Tools solve that. The model decides at runtime which tools in which order.
- **Chapter 3** — We build a loop around it. It costs 10× a one-shot call. It can fail and needs retries.
- **Chapter 4** — Some models have the loop inside (reasoning). That costs too.
- **Chapter 5** — Tools and agents can be reachable in a standardised way. Scales beautifully.

Now comes the uncomfortable question: **when is that actually worth it?**

Early 2024 every consulting pitch contained the word "agent". Early 2025 every enterprise roadmap said "agent-first". By the end of 2025 people had noticed in some of those projects that a batch job with two `if` branches did the same task cheaper, faster, deterministically, and auditable.

The point of this chapter: **the agent architecture is a tool**, not a default layer. Like every tool it has a specific area of use — and a very large area outside it where it is *worse* than the alternative.

---

## 🔬 The two miniatures

### `src/01_agent_vs_sum.py` — the maximally absurd comparison

Task: the sum of `[1, 2, 3, 4, 5]`. Result: `15`. No doubt.

- **Path A**: `sum([1, 2, 3, 4, 5])`. Five characters of Python. Runs in ~1 microsecond. Costs 0 cents.
- **Path B**: an agent that uses a `calculator` tool. A `chat()` call, JSON parsing, tool dispatch, response. Runs in ~2 seconds. Costs ~50–100 tokens.

The miniature runs both and prints the **comparison table**:

| | Latency | Cost (tokens) | Determinism | Auditable |
|---|---|---|---|---|
| **A · Python `sum`** | 1 µs | 0 | ✓ | ✓ (code) |
| **B · Agent** | ~2 s | ~80 | ✗ | partly |

The wow moment: the factor of ~14,000,000 in latency. But more importantly: the determinism difference. For `sum([1..5])` it is absurd at small scale — for a batch job over a million invoices it becomes an existential question.

### `src/02_determinism_check.py` — the hard case

We send **the same prompt five times** to the model (`temperature=0`, which intuitively should mean "deterministic"). The prompt: a small multi-step planning task that should return a structured plan.

We compare the five answers character by character:

- Are all five answers **identical**?
- If not: are they at least **semantically equal** (same structure, same values)?
- If not even that: where exactly do they diverge?

Empirical: with `gpt-4o` and `temperature=0`, ~60–80% of runs are character-identical, the rest deviate in order, wording, or intermediate steps. For more complex tasks the character-identity rate quickly drops below 50%.

**The point:** *"deterministic"* in the LLM context does not mean *"identical answers"*. It means: *"identical probability distribution"* — but the server infrastructure fiddles with that via batched requests, load balancing across regions, and internal best-of-N sampling. Even with `temperature=0`, repeatability is not a contract.

For a chatbot that does not matter. For an automated approval process in a regulated industry it is a compliance defect.

---

## 💡 Wow moment

The actual value of this chapter is **not** in the two scripts. It is in the **two-question test** you take away. Before every agent project ask:

1. **Does the task need judgement at runtime?**  
   That is: is there a step at which *a human* would look at the result of a previous step and *decide* what to do next? If yes, that is a candidate for an agent. If no — i.e. if the flow logic is known in advance — then `if`s and functions are cheaper, faster, deterministic, and auditable.

2. **Can you tolerate one wrong answer in twenty?**  
   That is: are the costs of an error (financial, legal, reputational) tolerable enough that a 5% error rate model is acceptable? If yes: good candidate. If no — for a payment approval process, a medical finding, a compliance check — an LLM-based agent is by construction the wrong choice, and you need deterministic code plus human sign-off.

**Only if both are *yes* was the effort from Chapters 1–5 justified.** A *no* to question 1: `sum([1..5])`. A *no* to question 2: `if regulated: refuse_agent`. A *no* to both: a simple Python script.

---

## 🚀 Run it

```powershell
cd "C:\Users\<USERNAME>\Source\RPT Agent"

python "Agentic Systems/06_WhenNotToBuild/src/01_agent_vs_sum.py"
python "Agentic Systems/06_WhenNotToBuild/src/02_determinism_check.py"
```

Expected runtime: 5–20 seconds per script. Miniature 2 makes 5 LLM calls, so it is the more expensive one.

---

## 🧭 Interim balance — and the last question

That was the actual journey. Six milestones, built from a total of 11 small runnable scripts:

| Chapter | Miniatures | Focus |
|---|---|---|
| 1 · Text-in / Text-out | 2 | LLM as an API object, why computation fails |
| 2 · Tools & Planning | 2 | same task with a tool, three plans for three prompts |
| 3 · The Loop | 3 | real multi-turn loop, token growth, four retry strategies |
| 4 · Reasoning Inside | 1 | thinking tokens visible, provider matrix |
| 5 · Protocols & Scale | 2 | MCP server + client, A2A client as agent call |
| 6 · When NOT to Build | 2 | agent vs. `sum`, determinism test |

When you have run all 11 scripts yourself once, you have earned the right to decide when in your context an agent is the right tool — and when a Python function does it better. That is the actual skill. Not the building. The *deciding whether*.

But now comes the last question. The slide deck poses it in **Slide 44**: *"The question is no longer 'can it?' — it's 'should it?'"*. In this chapter we learned how to answer it. **Slide 45** then poses a new one: *"Where are agents heading?"*.

---

## ↷ Where it goes — Chapter 7

Slide 45 in the deck draws the trajectory in three stages:

> **Fixed tools → Generated tools → Self-extending capability**

- **Today** (Chapters 1–6): an engineer curates a catalogue of tools. The model picks, sequences, and calls them — but cannot go beyond what was provided. Joule, function-calling agents, MCP tool servers. What you built in this repo.
- **Emerging**: when the right tool does not exist, the agent writes it on the fly — a Python script, a SQL query, an API client. Runs it, observes the result, continues. **Cline** already works this way. **The slide deck accompanying this repo was built like this** (Slide 46: *"Every change was a script Cline wrote in the moment"*).
- **Next**: agents that don't just generate one-off scripts but *persist, test and reuse* new capabilities — growing their own toolset and publishing it to other agents via A2A.

**Chapter 7 is the smallest honest miniature of the middle stage.** An agent with no hard-wired tools. When it needs something, a second LLM generates the Python code, an AST whitelist validates it, a registry holds it. The second variant persists the catalogue to disk — the third stage (self-extending) in the small.

And the most important afterthought applies immediately: *"the boundary between using a tool and building one disappears — orchestration becomes where new capabilities are governed."* That is the second flavour of this chapter's two-question test. This time it asks not *"should I build an agent?"* but *"should I let an agent build?"* — and the answer depends on a new sandbox policy that did not exist in Chapters 1–6.

→ Continue in **[Chapter 7 · Dynamic Tool Agent](../07_DynamicToolAgent/README.en.md)**.

---

## 📚 Further reading

- **Anthropic** — *Building Effective Agents* (2024). The classic on agent patterns.
- **Karpathy** — *Software 3.0* (2025 talk). The framework-free perspective.
- **Amodei** — *Machines of Loving Grace* (2024). The most ambitious outlook.
- **EU AI Act** (2024, in force from 2026). Legal framework for high-risk AI systems — what an *agent* is in the legal sense remains open.