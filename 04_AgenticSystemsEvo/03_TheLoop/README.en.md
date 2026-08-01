# Chapter 3 · The Loop

**The actual agent — and what it costs.**

Three miniatures. The first builds the loop in ~60 lines of Python. The second instruments it and shows why a three-turn loop does not cost ~3× a one-shot call but more like ~10×. The third compares four different retry strategies and shows where the model itself becomes the error analyst.

---

## 📜 Historical context

At the end of Chapter 2 stood a plan with a placeholder:

```
step 1: currency_converter(132877 USD -> EUR)
step 2: calculator(divide, <result_from_step_1>, 5.3)
```

The model had understood the plan — but it did not yet have the value for the second step. The value only comes into existence once step 1 has been executed. That means: the runner must execute step 1, hand the result back to the model, and the model must reformulate step 2 (with the now-known number instead of the placeholder). That is a *loop*.

**October 2022** — Yao et al. with the *ReAct* paper (from Chapter 2) had already formulated this loop: `Thought → Action → Observation → Thought → ...`. The loop ends when the model produces a final answer instead of another action.

**March 2023** — *Auto-GPT* and *BabyAGI* land as viral repos on GitHub. For the first time the public sees an agent that runs *multiple turns* autonomously — and occasionally gets stuck in infinite loops. Neither repo was technically ground-breaking, but they made it clear to a broader audience: **the loop is the actual invention**, not the model. The model is the engine. The loop is the car.

**June 2023** — OpenAI introduces *function calling*. If you had been building agents until then, you had written your own JSON parser. Function calling made that easier, but it did not make the *loop* obsolete — it just made one part of it more convenient.

Since then the loop has appeared in every agent library: LangChain's `AgentExecutor`, Semantic Kernel's `Planner`, AutoGen's `initiate_chat`, OpenAI's Assistants API. Every one of those libraries hides the same loop behind a nicer interface. The first script of this chapter shows the loop naked — without a library. That way you understand what the libraries do for you (and what they do not).

---

## 🔬 The three miniatures

### `src/01_basic_loop.py` — the loop in raw form

Same task as Chapter 2 task 2: *"I have 132,877 USD, how many units at 5.30 EUR each can I buy?"*. But this time:

- the system prompt expects **exactly one JSON object per turn**: either a tool call or `{"final": "..."}` to end;
- the runner (the 60 lines of Python) sits in a `while` loop, executes every tool call, appends the result as an "observation" to the conversation, and calls the model again;
- **three stop conditions are explicit in the code**: `{"final": ...}` (success), turn limit (safety net), same-tool-three-times-in-a-row (loop guard).

After 2 or 3 turns you get `{"final": "You can buy roughly 23,073 units."}`.

**What you see here:** an agent that hides *nothing* from the model. Every LLM answer is printed. Every parsing decision is visible in the code. Every stop condition sits as an `if` in plain text.

### `src/02_token_growth.py` — what the loop really costs

Same loop, but with an instrumented task that needs 3–4 tool calls. After each turn the runner prints one line:

```
Turn 1:   in= 187   out= 34   cumulative= 221 tokens
Turn 2:   in= 265   out= 41   cumulative= 527 tokens
Turn 3:   in= 342   out= 39   cumulative= 908 tokens
Turn 4:   in= 421   out= 62   cumulative=1391 tokens
```

You see immediately: `tokens_in` **grows with every turn**, because the entire previous conversation (system prompt + all previous model answers + all observations) has to be sent *afresh* at every turn. The loop has no memory on the model's side — *the memory is the prompt*.

**What you see here:** why LLM-based agents are so much more expensive than they look at first sight. Someone running 4 turns pays not four times a single call — more like ten times, because every late turn has to carry a very long prompt history.

### `src/03_retry_strategies.py` — four strategies compared

A simulated tool `flaky_price_lookup(sku)` that fails the first three calls with HTTP 503 and returns the correct answer on the fourth. We compare four retry strategies:

- **A · naïve** — `sleep(0.5), retry`, fixed, no thinking
- **B · exponential backoff** — `sleep(0.5, 1, 2, 4)`, classic
- **C · circuit breaker** — after three failures, break for a cooldown period
- **D · LLM-guided recovery** — send the error text to the model and ask *"what now?"*

Every strategy is run against the same error sequence. At the end the script prints a comparison table:

```
                   Attempts   Latency    Tokens   Outcome
A · naïve               4     1.2 s        0      OK
B · exp. backoff        4     1.4 s        0      OK
C · circuit breaker     3     0.4 s        0      Abort (fine for "fail fast")
D · LLM-guided          2     6.7 s      243      OK, with reasoned switch
```

**What makes strategy D special:** it is the only one that *understands* why the failure happens. Instead of blindly waiting, the error text is sent to the model: *"The price lookup returns 503. What now?"* — and the model answers with a structured recommendation: *"Use the cached version, or switch to `fallback_price_lookup(sku)`."* The loop now has a second level of recursion: the model itself becomes the error diagnostician.

Price for that: one additional LLM call per error. For rare, semantically complex errors that is cheap. For mass timeouts it would be ruinous.

---

## 💡 Wow moment

The most important moment lies in miniature 3, strategy D.

Up to this point in our series the model has only solved *tasks* — multiplications, tool selection, plan creation. In strategy D the model, for the first time, solves a *problem of the program itself*: it analyses an error message and recommends a different program action.

That is qualitatively new. In Chapter 4 we will see that modern reasoning models have this capability *within a single call* — the model "thinks" about its own answer before delivering it. But the underlying idea is the same: **the model becomes a meta-reasoner over its own context**. Strategy D is the simplest version of that which you can build by hand.

---

## 🚀 Run it

```powershell
cd "C:\Users\D041506\Source\RPT Agent"

python "Agentic Systems/03_TheLoop/src/01_basic_loop.py"
python "Agentic Systems/03_TheLoop/src/02_token_growth.py"
python "Agentic Systems/03_TheLoop/src/03_retry_strategies.py"
```

Expected runtime: ~30–60 seconds per script. Cost: ~2000–6000 tokens for miniatures 1 and 2, ~500 tokens for miniature 3 (because a lot is simulated there).

---

## 🧭 Bridge to the next chapter

What we built in Chapter 3 is an **external loop** — the loop lives in *our* Python code, every turn is a separate HTTP call, every decision "keep going or done?" is made by *our* code.

Late 2024 brought a second kind of loop into the world: the **internal loop** — the loop lives *inside a single HTTP call*, in the reasoning model itself. We send a prompt, the model "thinks" (produces an internal chain-of-thought), and we get two streams back: the thinking and the answer.

That is Chapter 4.