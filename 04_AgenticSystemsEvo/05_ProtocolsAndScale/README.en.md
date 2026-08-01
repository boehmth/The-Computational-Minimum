# Chapter 5 · Protocols and Scale

**How foreign tools and foreign agents talk to your loop — without you writing a wrapper for each.**

Two miniatures. The first shows a minimal **MCP server** and its matching **client**: JSON-RPC 2.0 over stdio, tool discovery, tool call. The second shows an **A2A client** that talks to an agent endpoint — same wire format as MCP, but the callable is a model, not a tool.

Both fit into ~100–150 lines of Python. No framework.

---

## 📜 Historical context

Before November 2024 the tool landscape looked like this:

- Anthropic Claude had its own `<tool_use>` tags in the text.
- OpenAI had `function_calling` with its own JSON schema.
- Google Gemini had `function_declarations` — related, but not compatible.
- Every company had its own internal tool registries with their own schemas.

Result: **N × M bespoke integrations**. 10 models × 20 tools = 200 hand-written adapters. Every new combination a new adapter project. Every tool API change a refactor across 10 models.

**November 2024 · Anthropic publishes the Model Context Protocol (MCP).** A simple proposal: standardise the *tool schema* — not the model, not the client, but the *in between*. An MCP server offers tools over a JSON-RPC-2.0 interface. Any client that speaks MCP can talk to any server. *N × M* collapses to *N + M*.

The trick: **MCP is deliberately almost empty**. It defines only the *framing*:

- `initialize` — handshake, version, capabilities
- `tools/list` — which tools do you offer? (names + descriptions + JSON schemas)
- `tools/call` — execute tool X with arguments Y
- `prompts/list`, `resources/list` — optional extensions

No framework. No magic runtime. Just a proven RPC format (JSON-RPC 2.0, from 2005) and a small set of standard methods.

**Early 2025 · Google formulates A2A (Agent-to-Agent).** Same observation, one level up: if tools can be reachable in a standardised way, why not *agents*? An A2A endpoint accepts a natural-language request and returns a natural-language answer — with in-flight progress updates. From the client's viewpoint an A2A server is indistinguishable from an MCP server with one very general tool called "ask me anything".

Together they enable an architecture that wasn't possible before MCP:

> Your agent loop can consume foreign tools (via MCP) and foreign agents (via A2A) without you writing any bespoke code for them. The loop runner needs only *one* MCP/A2A client — and the tool landscape can grow without your loop code changing.

---

## 🔬 The two miniatures

### `src/01_mcp_client.py` (+ `src/mcp_server.py`) — server and client speak JSON-RPC

Two files. The first (`mcp_server.py`) is a minimal MCP-server implementation — it registers **two tools**:

- `getSupplierMasterData(supplier_id)` — returns (mock) master data for a supplier
- `getOpenPurchaseOrders(supplier_id)` — returns (mock) open purchase orders

Both are deliberately SAP-flavoured: these are exactly the tools a procurement agent would need in an ERP context.

The second (`01_mcp_client.py`) is the client. It:

1. Runs the handshake (send `initialize`, check the response).
2. Asks for the tool list (`tools/list`) — and prints it.
3. Executes a tool call (`tools/call getSupplierMasterData supplier_id=ACME-42`).
4. Displays the answer.

The server runs in the *same* Python runtime as the client — not as a subprocess. This is a deliberate simplification: in the real world the server would run as its own process, communicating via stdio or HTTP+SSE. For the miniature it suffices to see how the **messages look** and how the **registry works**. The real wire-format point stands: everything is JSON-RPC 2.0, everything is text, everything is standardised.

### `src/02_a2a_client.py` — the callable is an agent, not a tool

A2A is in wire format practically identical to MCP — except the method is called `tasks/send` instead of `tools/call`, and the server has no explicit tools list but an agent description with capabilities.

The miniature simulates an A2A server that hosts a small "procurement analyst agent": it takes a natural-language request (*"What does product X cost in region Y?"*), runs *its own* LLM loop internally with MCP tools, and returns a structured answer.

From the client's viewpoint: **you see only the request and the answer**. The whole loop inside the agent is invisible — just as in Chapter 4 the thinking loop inside a reasoning model was invisible.

---

## 💡 Wow moment

The most important moment is in the first miniature, at `tools/list`.

The client asks: *"which tools do you have?"* — and the server answers with a JSON list, in which every tool has a name, a description, and a JSON schema for its arguments. Precisely **this JSON schema** is what you had to write into the system prompt by hand in Chapter 2 — except now it comes from the server *automatically*.

That means: **when your agent needs a new tool tomorrow, you change no line in your loop.** The server operator (which can be another department, an external vendor, or another agent) registers the tool in *their* server. On the next `tools/list` call your client sees it. Done.

For an SAP context that matters structurally: your approval agent needs access to tools from MM, FI, SD, HR — each built by a different functional area. Without MCP: 4 different integration projects, 4 different adapters, 4 different update cycles. With MCP: 4 MCP servers, one client, one `tools/list` call.

And in the A2A miniature you see: **if the other endpoint isn't a tool but is itself an agent, almost nothing about the protocol changes**. The call looks the same. Only what happens behind it is completely different — a whole agent loop. From your code's viewpoint: the same JSON-RPC call.

That is the scaling conjecture the protocol rests on: **if we standardise everything on JSON-RPC, it stops mattering what runs on the other side**. A static tool server, a runtime-generated SQL, an agent with reasoning=high, or a chain of five specialised agents — all look the same to your client.

---

## 🚀 Run it

```powershell
cd "C:\Users\D041506\Source\RPT Agent"

python "Agentic Systems/05_ProtocolsAndScale/src/01_mcp_client.py"
python "Agentic Systems/05_ProtocolsAndScale/src/02_a2a_client.py"
```

The first miniature is purely deterministic (no LLM) — it only shows the JSON-RPC messages. The second calls the LLM for the simulated A2A agent and needs your `.env` configuration.

---

## 🧭 Bridge to the next chapter

At the end of Chapter 5 you have seen: **you can build almost anything.** Wiring in tools is trivial. Calling agents is trivial. The loop scales.

That leads to a new danger: **you build it even though you shouldn't.**

Chapter 6 is the verdict. Two miniatures show where agents are *not* the right tool — deterministic tasks and non-determinism problems. No framework, no pretty library can answer these questions for you. The two-question test from the deck becomes the reference: **do you need judgement at runtime? Can you tolerate one wrong answer in twenty?**

If both are yes, the effort from Chapters 1–5 was justified. If not: write a Python function.