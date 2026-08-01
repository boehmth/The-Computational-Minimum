# Exercises · Chapter 6

Three exercises. All three are questions to *you*, not to the model. By the end your judgement should be more solid.

---

## Exercise 1 · Apply the two-question test

For EACH of the following real-world "agent projects" that have actually been proposed, decide using the two-question test from the chapter README: **agent, deterministic function, or human with assistant?** Justify in one or two sentences.

1. A bot that automatically approves **vacation requests**: duration < 5 days, no blocked periods, remaining vacation days are enough.
2. A system that picks the **best support agent** for an incoming ticket (from a 200-person team).
3. A system that **automatically answers an incoming customer email**.
4. A system that extracts the 5 most important **risks from a contract text**.
5. A system that decides whether an **invoice over 10,000 EUR** gets approved.
6. A system that prepares and files the **monthly VAT return**.
7. A system that extracts the agreed **next steps from sales meetings**.
8. A system that drafts an initial reply for a customer with a **complaint**.

**What you learn:** the answer is rarely *"yes agent"* or *"no function"*. Usually it is: *"agent for class A of the cases, function for class B, human-with-assistant for class C — and the classification itself can be done by an LLM"*. That is exactly the router approach from Chapter 4 in new clothing.

---

## Exercise 2 · Fix determinism

`02_determinism_check.py` shows: with `temperature=0` you don't get the same answer twice. In practice, for regulated processes, you still need *repeatability*.

**Task:** Build a `deterministic_chat()` wrapper around `chat()` from `common/llm.py` that:

1. Computes a deterministic hash of the prompt (SHA-1 over `system` + `user` + `model`).
2. If a cached response for that hash exists (in `.llm_cache/<hash>.json`), load and return it.
3. If not, make the real call, cache the response, then return.

Then run `02_determinism_check.py` with your wrapper. All five runs should now be character-identical.

**What you learn:** *determinism* in the LLM context practically always means *caching* — not a property of the model, but a property of your architecture. Exactly the point: *"repeatability is an architecture property of your system around the model"*.

**Bonus:** How long should the cache live? For an approval system that approved an invoice yesterday — should the cache be reused today? What if the rules changed between the two requests? (Hint: the cache key should also hash the *version* of the rules, not just the input text.)

---

## Exercise 3 · The honest anti-pattern case

Take a process from your own work — one you have thought about "automating with an agent". Be honest with yourself.

Answer in writing:

1. **What is the actual business value?** — Not the feature I want to build, but the outcome behind it.
2. **What would the "unglamorous solution" look like?** — A combination of a few `if` branches, a database query, and an approval UI for humans. Without an LLM.
3. **How would I NOTICE the unglamorous solution isn't enough?** — What is the concrete edge case where the process really needs a model?
4. **Is that edge case common enough to justify the agent architecture?** — If it happens in 3% of cases, an "unglamorous solution + human sign-off for the rest" might be enough.
5. **What is the error-cost comparison?** — 5% wrong recommendations from the LLM agent vs. 15% cases escalated to a human by the unglamorous solution — which is more expensive for the company?

If you end up concluding that the unglamorous solution suffices: **you've just saved a lot of time**. If not: you now have a much better justification for your agent project than "we want to do AI".

**What you learn:** the hardest exercise of this whole chapter is *not writing code*. It is *honest self-report*. And it happens to be the one that distinguishes you as an engineer from an enthusiast with a GitHub-Copilot subscription.

---

## How you know you have understood the whole repo

If you can explain in **one paragraph** to a colleague,

- *what* an LLM is (Chapter 1),
- *why* you give it tools (Chapter 2),
- *how* you build a loop around it and what that costs (Chapter 3),
- *that* some models have the loop inside (Chapter 4),
- *why* MCP and A2A scale the tool landscape (Chapter 5),
- and *when* you don't need any of this (Chapter 6) —

...**all without naming a single framework** — then for the rest of your career you can make informed decisions about agent architectures. That is the actual gain of this repo.

Everything else is detail that changes every 18 months.