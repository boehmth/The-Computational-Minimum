# Milestones in Agentic Systems

**Seven milestones that show how a language model turns into an autonomously acting system — up to the agent that writes its own tools.**

All hand-written, no agent frameworks. Every prompt, every tool call, every retry decision is visible in the code. If you have backend access to SAP GenAI Hub, all examples run against real models (`gpt-4o`, `anthropic--claude-4.5-sonnet`, the o-series).

> **🇩🇪 German version:** [`README.md`](README.md). This is the English parallel.

---

## 📜 Why this part?

At the end of *Milestones in Machine Intelligence* you built a tiny GPT-style model yourself. That gave you **the foundation**. The interesting question: **what has been made from it in the last years?**

Less than ten years lie between 2018 (GPT-1) and today — but the step from *"model answers one prompt"* to *"model plans, uses tools, iterates, corrects itself"* is qualitatively as large as the step from perceptron to transformer.

This part follows that trajectory. In seven chapters.

---

## 🕰️ Historical arc

| Year | Event | Chapter |
|------|-------|---------|
| **1950** | Turing — *Computing Machinery and Intelligence* | **1. Text-in / Text-out** |
| **2018** | Radford (OpenAI) — GPT-1, autoregressive language model | |
| **2022 Nov** | ChatGPT — the one-prompt era begins | |
| **2022 Oct** | Yao et al. — **ReAct**, "reasoning + acting" | **2. Tools & Planning** |
| **2023 Mar** | Schick et al. — **Toolformer**, model learns to call tools | |
| **2023 Mar** | Auto-GPT, BabyAGI — loops enter public consciousness | **3. The Loop** |
| **2023 Jun** | OpenAI — function calling | |
| **2024 Sep** | OpenAI — **o1**, reasoning models | **4. Reasoning Inside** |
| **2025 Feb** | Anthropic — Claude 3.7 extended-thinking | |
| **2025** | DeepSeek-R1 open-weight, RLVR-trained | |
| **2024 Nov** | Anthropic — **MCP**, Model Context Protocol | **5. Protocols & Scale** |
| **2025** | Google — **A2A**, Agent-to-Agent protocol | |
| — | ...and the practical question: *when is all this actually worth it?* | **6. When NOT to Build** |
| **2023 May** | Cai et al. — *LLMs as Tool Makers* (LATM) | **7. Dynamic Tool Agent** |
| **2023 Oct** | NVIDIA — **Voyager**, growing skill library in Minecraft | |
| **2025** | Devin · SWE-agent · Claude Code — runtime code generation becomes standard | |

Ten years — seven chapters — one small runnable miniature each.

---

## 🧭 The seven milestones

### [`01_TextInTextOut/`](01_TextInTextOut/README.md) — What an LLM actually is, from the API side

**Core:** The smallest possible programs. A six-liner `01_hello_llm.py` proves the first principle: *an LLM consumes text and produces text — nothing else*. A second script `02_math_breaks.py` asks the model for the product of two five-digit numbers; the result is plausible but wrong. Python computes the truth alongside.

**Wow moment:** The model guesses `6,343,522,638` — Python computes `634,442,838` — off by ~6 billion. Not because the model is "dumb", but because it predicts text, it doesn't compute. This realisation motivates every remaining chapter.

**Bridge:** If models can't compute but the question requires computation — who does? → Chapter 2.

### [`02_ToolsAndPlanning/`](02_ToolsAndPlanning/README.md) — Tools and the first plan

**Core:** The system prompt describes ONE tool (calculator). The model gets the same multiplication as in Chapter 1 — and this time it does not respond with a number, but with a JSON object describing the tool call. A tiny orchestrator parses the JSON, runs the deterministic operation in Python, and the answer is correct. A second script shows: the same tool pair, three natural-language tasks, three different call orderings — none of them written in Python.

**Wow moment:** *Same tools, three prompts, three different plans.* No engineer specified the ordering. This is the moment when control over flow shifts from developer to model.

**Bridge:** One tool call is not yet a loop. What happens when the task needs *multiple* tool calls? → Chapter 3.

### [`03_TheLoop/`](03_TheLoop/README.md) — The external loop and what it costs

**Core:** The actual agent. `while not done: LLM → parse → tool → observe`. About 50 lines of Python. A second script instruments the loop and prints the cumulative token count per turn — you see token growth from 400 to ~5000 in five turns. A third script compares **four retry strategies** side by side: naïve, exponential backoff, circuit breaker, and LLM-guided recovery (the model itself analyses the error and suggests the next strategy).

**Wow moment:** In strategy D the retry decision *itself* becomes a model call. The loop now contains a second, semantic level of recursion: the model helps the developer debug the model.

**Bridge:** The loop runs on a *non-reasoning* model (`gpt-4o`). What changes when the model itself already has a loop inside? → Chapter 4.

### [`04_ReasoningInside/`](04_ReasoningInside/README.md) — The second loop, invisible

**Core:** The same prompt, sent once to `gpt-4o` (baseline, no reasoning tokens) and once to `anthropic--claude-4.5-sonnet` with `thinking={"type":"enabled"}` — both a single HTTP call, but Claude returns two text streams: a private thinking stream and the final answer. A provider matrix shows which vendors expose the thinking tokens in the response at all (Claude/DeepSeek: yes; OpenAI/Gemini: only the counter in `usage`).

**Wow moment:** From the developer's viewpoint it is *one* call — one `chat()`, one `Response`. From the model's viewpoint it is hundreds of autoregressive forward passes, where the model reads its own freshly generated tokens. The loop has retreated from Python code into the model architecture — and in a third case, into the provider's server (Best-of-N, "reasoning: high").

**Bridge:** An agent alone is a tool. What if many agents should talk to each other — or your tools should be open to many foreign models? → Chapter 5.

### [`05_ProtocolsAndScale/`](05_ProtocolsAndScale/README.md) — MCP and A2A as runnable miniatures

**Core:** Two small executable examples in the ~50-line format:

- **A minimal MCP server** (Anthropic Model Context Protocol, Nov 2024). Offers a tool `getSupplierMasterData(supplier_id)` over JSON-RPC via stdio. A second script is the corresponding *client*, which discovers the tool via `tools/list` and executes it via `tools/call`. No framework, just `requests` and `json`.
- **An A2A client** (Google Agent-to-Agent, 2025). Shows: same wire format as MCP, but the endpoint being called is itself an agent, not a tool. The "callee" is a conversation, not a single function call.

**Wow moment:** One JSON-RPC call, three lines of code, and your colleagues' tools (or a third-party vendor's) are live. The *N×M* integration cost of the pre-MCP era (every client × every tool = one bespoke API) collapses to *N+M*.

**Bridge:** Now agents can do everything. So — do we build one for everything? No. → Chapter 6.

### [`06_WhenNotToBuild/`](06_WhenNotToBuild/README.md) — The verdict

**Core:** Two runnable scripts demonstrate the anti-patterns:

- `01_agent_vs_sum.py` — deliberately builds an agent for `sum([1,2,3,4,5])`. Compares latency, tokens, and cost to the Python one-liner. The agent is ~14,000,000× slower and costs a few cents for an operation that costs 5 characters of code.
- `02_determinism_check.py` — sends the same prompt five times with `temperature=0` to the same model and shows that the plan sequence differs between runs. For regulated processes that is a defect, not a feature.

**Wow moment:** The two-question test — *"Does this need judgement at runtime? Can you tolerate one wrong answer in twenty?"* — as a practical decision tool. Only if both are *yes* is the effort from Chapter 3 worth it.

**Bridge:** Chapters 1–6 show the base pattern. Chapter 7 shows the state of the art in summer 2026 — what happens when the tools no longer have to come from humans either?

### [`07_DynamicToolAgent/`](07_DynamicToolAgent/README.md) — The agent that writes its own tools

**Core:** The agent has *no* hard-wired tools. When it needs a tool it doesn't know, it picks the `generate_tool` action via JSON — the runner then calls a second LLM that delivers Python code. An AST whitelist checks it (no imports, no `open`, no dunder attributes), compiles it in a sandbox namespace, and stores it in a registry. Two miniatures: one with an in-memory registry, one with disk persistence.

**Wow moment:** After four questions the agent has four tools *it wrote itself* — sitting as ordinary `.py` files under `generated_tools/`. But: the responsibility does not travel with the tool. The sandbox, the namespace definition, the persistence policy, and the error protocol all remain *your* code. Principle 3 in its hardest form.

**Arc end:** Systems like Devin, SWE-agent, and Claude Code are elaborations of exactly this pattern — with better sandboxes and richer tooling. Understand the loop of this chapter, and you can analyse any modern code-agent system.

---

## 🧭 The red thread

Each chapter answers the question the previous one raised:

> **Chapter 1**: An LLM consumes and produces text. → But the answer is sometimes wrong.  
> **Chapter 2**: Give it a tool, then Python computes. → But many tasks need multiple tools.  
> **Chapter 3**: Build a loop around it. → But you pay with tokens and latency.  
> **Chapter 4**: Some models iterate internally. → But they don't replace your loop.  
> **Chapter 5**: Standardise the tool interface. → But now you can build "too much".  
> **Chapter 6**: Less is more. Build only when P2 + P3 pay off.  
> **Chapter 7**: Let the agent write its own tools. → But sandbox + safety do *not* travel to the model.

At the end you will have **run all seven miniatures yourself once** and can then make an informed decision about where an agent is the right tool — and where a simple Python function does the job better.

---

## 📏 Scaling as the actual thread

What the red thread above says *conceptually* boils down to one word: **scaling**. Every chapter scales the same core idea to a new level, without discarding the previous one.

| Chapter | Tool palette | Who defines the tools? | What scales? |
|---|---|---|---|
| **1** | none | — | (only LLM, no tool) |
| **2** | 1 tool (`calculator`) | Developer, at design time | Principle: *split model / tool* |
| **2** (miniature 2) | 2 tools | Developer, at design time | *Model picks from a set* |
| **3** | 2 tools, in a loop | Developer, at design time | *Chain tool calls + retries* |
| **5** | any, over MCP | Foreign teams, at design time | *Tool catalogue grows externally* |
| **7 · M1/M2** | any, **generated at runtime** | The model, at runtime | *Catalogue grows internally, on demand* |
| **7 · M3** | ditto, **plus self-healing** | Model + repair LLM | *Catalogue also gets repaired when broken* |

The arc behind it: *if the calculator can be a tool, then anything can be a tool. If a fixed set works, a dynamic set can work. If runtime-generated code can break, then the repair has to be at runtime too — with the same LLM pattern.* Chapter 7 · miniature 3 is therefore not a new blueprint, but the last recursion: the retry from Chapter 3, applied to code the model wrote itself.

---

## 🚀 Quick start

Prerequisite: you are in the parent `RPT Agent` root, you have `.env` populated, and `sap_service_key.json` sits next to it (see [`../README.md`](../README.md)).

```powershell
cd "C:\Users\<USERNAME>\Source\RPT Agent"

# Chapter 1
python "Agentic Systems/01_TextInTextOut/src/01_hello_llm.py"
python "Agentic Systems/01_TextInTextOut/src/02_math_breaks.py"

# Chapter 2
python "Agentic Systems/02_ToolsAndPlanning/src/01_give_it_a_tool.py"
python "Agentic Systems/02_ToolsAndPlanning/src/02_model_plans.py"

# Chapter 3
python "Agentic Systems/03_TheLoop/src/01_basic_loop.py"
python "Agentic Systems/03_TheLoop/src/02_token_growth.py"
python "Agentic Systems/03_TheLoop/src/03_retry_strategies.py"

# Chapter 4
python "Agentic Systems/04_ReasoningInside/src/01_thinking_visible.py"

# Chapter 5
python "Agentic Systems/05_ProtocolsAndScale/src/01_mcp_client.py"
python "Agentic Systems/05_ProtocolsAndScale/src/02_a2a_client.py"

# Chapter 6
python "Agentic Systems/06_WhenNotToBuild/src/01_agent_vs_sum.py"
python "Agentic Systems/06_WhenNotToBuild/src/02_determinism_check.py"

# Chapter 7
python "Agentic Systems/07_DynamicToolAgent/src/01_dynamic_tool_agent.py"
python "Agentic Systems/07_DynamicToolAgent/src/02_dynamic_tool_agent_persisted.py"
```

---

## 📖 How to work through this part

1. Read the preface ([`PREFACE.en.md`](PREFACE.en.md)) — it frames the seven milestones.
2. Start with Chapter 1. The README there explains the historical context; then run the scripts in `src/`.
3. Every chapter ends with **exercises** in `EXERCISES.en.md` — they are the real teaching device, because they force you to *modify* the example.
4. Chapter 5 (MCP + A2A) is the only point where you start additional processes. All other chapters are pure single-script miniatures.

> **A note on the script output:** the scripts talk to the model in German, and the model answers in German ("Empfehlung: FREIGEBEN..."). This is intentional. The pedagogical points land regardless of language; and it also serves as a live demonstration of a point the deck slides skip — LLMs work in any language, they aren't English-only artefacts.

---

## 🧠 What this part deliberately does not show

- **No framework.** No LangChain, no Semantic Kernel, no AutoGen, no LlamaIndex. All loops, all parsers, all retry policies sit in plain text in the script. That is uncomfortable — that is exactly why we do it. A framework hides precisely the responsibilities this part wants to make visible (see Principle 3 below).
- **No UI.** Everything runs in the terminal. If you want the result to look "nice", that's an excellent exercise project for Chapter 5.
- **No persistence.** No RAG, no vector store, no chat history across sessions. Those are sensible next steps, but not milestones — they are applications of the milestones.

---

## 🧭 The three principles that carry all chapters

This repo has a twin: a slide deck titled *"Why Agents, and Why Now"* which tells the same story for a less technical audience. From it come the three principles that run through every chapter:

> **P1 · What an LLM is** — It consumes text and produces text. Nothing else.  
> **P2 · What an agent is** — The model decides the steps at runtime. Not the developer, not in advance.  
> **P3 · What the developer owes** — Everything around the model is your code.

Every chapter is a consequence of one of these three principles.

---

## 📜 Licence and use

Free for educational use. Contributions, translations, and additions welcome.
