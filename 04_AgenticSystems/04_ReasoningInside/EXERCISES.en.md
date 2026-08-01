# Exercises · Chapter 4

Two exercises. Both force a perspective shift that goes beyond the single miniature.

---

## Exercise 1 · The price of "reasoning: high"

`01_thinking_visible.py` runs with `reasoning="high"`. In `common/llm.py` this maps for Anthropic to `budget_tokens=8192` (see `_reasoning_budget`).

**Task:** Change the `reasoning` parameter in the second-model call to `"minimal"`, then to `"medium"`. Run each. Fill in a table:

| Level | budget_tokens | thinking tokens actually used | answer tokens | wall time |
|---|---|---|---|---|
| minimal | 512 | ? | ? | ? |
| medium | 2048 | ? | ? | ? |
| high | 8192 | ? | ? | ? |

Then answer:

1. Does Claude still get the tank task right at all three levels?
2. From which level does the answer **quality** noticeably change (intermediate steps get dropped, numbers get rounded, etc.)?
3. If you were building an agent making millions of calls per day — how would you decide which level to use?

**What you learn:** `reasoning: high` is not a "quality switch" but a **cost / latency / quality trade-off**. For most production calls `minimal` is enough. For the sparse 5% of hard tasks `high` is worth it. The trick is knowing which 5% those are — or fielding a router model that pre-sorts the calls (see Chapter 4 of the accompanying deck: *"small / fast" as router*).

---

## Exercise 2 · What the provider withholds from you

The script shows that Anthropic Claude makes thinking tokens *visible*, while OpenAI's o-series returns only the *number* via `usage.reasoning_tokens`. That is black on white in the provider matrix at the end of the output.

**Task · thought exercise, not a coding exercise:**

Suppose you are building an agent in the SAP context: an approval agent that reviews invoices and recommends *"approve / decline / clarify"*. The agent uses a reasoning model.

1. **Compliance question:** an auditor reviews your system and wants to see the *reasoning path* for every recommendation in the audit log. Can you satisfy the same requirement with OpenAI o3 as with Claude 4.5? Where is the problem, and how could you work around it (hint: you can ask the model in the final `text` field to explicitly restate its reasoning path — but that costs tokens and does not guarantee it is the *same* reasoning path the model actually used internally).
2. **Cost question:** o3 samples N reasoning traces internally and picks the best (see README). An auditor asks you: *"If I submit the same case twice, do I get the same answer?"* — how do you answer precisely? (Hint: the auditor is implicitly asking about determinism. Chapter 6 will bring this question up again in its own miniature.)
3. **IP question:** Anthropic exposes the thinking tokens in the response. OpenAI hides them. Come up with at least *one* business reason why a vendor might do the one or the other. And one reason for an SAP customer why the one or the other is better for them.

**What you learn:** the choice of reasoning model is not just a technical decision — it is also a compliance, cost, and contract decision. For an internal chatbot it doesn't matter; for an approval agent with audit requirements it is critical.

---

## How you know you have understood this chapter

If you can say in **one sentence**: *"A reasoning model runs a loop *inside* one HTTP call — the loop lives in the autoregressive token generation, and the model reads its own thinking as context for the next tokens; the developer controls only `budget_tokens`, not the individual steps."* — you're done with Chapter 4.

And if you can also say there are *three* loop categories (yours in Chapter 3, the model's in Chapter 4, and the provider's invisible Best-of-N loop) — then you're really done.