# Chapter 7 · Exercises

The exercises are the real teaching device. They force you to modify the miniature — and modification is the only honest way to understand code.

## Exercise 1 · Provoke a malicious tool

Extend the example questions in `01_dynamic_tool_agent.py` with one that tries to make the agent write a file — e.g. *"Create a file with the contents 'hello' at /tmp/x.txt"*.

Observe:

1. Which `action` does the model propose on turn 1?
2. If it tries `generate_tool`: which code does the tool generator produce, and exactly why does `_validate_tool_ast` reject it?
3. What happens on the next turn, when the agent sees the error message?

This exercise makes the purpose of the sandbox tangible: the whitelist is not decoration, it catches the first realistic attack scenario.

## Exercise 2 · Make the sandbox stricter

`FORBIDDEN_NAMES` currently contains only a few obviously dangerous names. Sophisticated generated code could still work around it — e.g. `().__class__.__bases__[0].__subclasses__()` (the classic "RestrictedPython escape" trick).

Try:

1. Extend `_validate_tool_ast` so that **every** attribute access to dunder names (`__.*__`) is forbidden, not just those that *start* with dunder.
2. Additionally forbid `ast.Subscript` with a constant `0` (a common first step in the escape trick).
3. Write a short test string that passes the old whitelist but fails your new one.

No sandbox design is ever "done" — every extension closes one class of attacks but perhaps opens the next. This exercise is meant to make that price concrete.

## Exercise 3 · Resource limit via timeout

The current agent can be hung by a generated `while True: pass`. Extend `ToolRegistry.call()` (or its persistent variant) so that every tool call is aborted after 2 seconds via `signal.SIGALRM` (Unix) or a thread timer (Windows compatible).

Try:

1. What exception class does your timeout raise, and how does the agent loop present it back to the model?
2. Can the agent recognise the timeout and generate a *different* tool that is faster? Test with a task like *"Find the 100,000th prime number"*.

This is the transition from "safety as forbidding" (whitelist) to "safety as consumption limit" (resources). The second is, for complex tasks, often the only practical answer.

## Exercise 4 · Share the registry

If two runs of `02_dynamic_tool_agent_persisted.py` are running independently, they could overwrite each other's tools. Extend `_persist_tool`:

1. Check whether `generated_tools/{name}.py` already exists.
2. If yes, compare the existing code to the new one. If identical: only update the metadata, leave the code alone.
3. If different: decide sensibly — keep the new version and back up the old one as `generated_tools/{name}.v{N}.py.bak`.

Result: a small but real tool version history. In a production version those would be git commits rather than `.bak` files; the idea stays the same.

## Exercise 5 · Manipulate persisted code by hand

Run `02_dynamic_tool_agent_persisted.py` once so that at least `is_prime.py` sits under `generated_tools/`. Open the file in an editor and add a line `import os` at the top. Save.

Run the script again:

1. What appears in the `[Persistenz]` output?
2. Which specific `ToolCodeError` message shows up?
3. What does the agent do on the next turn when it wants to use `is_prime` — does it fall back to `generate_tool`?

This is the "attacker manipulates disk between two runs" exercise. The answer to question 3 shows whether your system is *robust* or merely *not currently broken*.

## Exercise 6 · Provoke the self-healing loop

In miniature 3 the repair LLM only kicks in when the generated code is broken. That doesn't happen on demand in normal use. Provoke it deliberately:

1. Sabotage the tool generator by temporarily rewriting `TOOL_GENERATOR_SYSTEM_PROMPT` so that it deliberately violates the rules (e.g. force `import os`, or embed a known dunder-attribute reference). Expectation: `ToolCodeError` on the first try, the repair prompt fixes it, the second attempt succeeds.
2. Set `max_repair_attempts=0` in the registry constructor and re-run. Expectation: the same sabotage now leads to immediate give-up, just like in miniature 2. That is the proof that the repair loop is really a separate policy and not a hardwired part of the sandbox.
3. Count the additional LLM calls: how many tokens does a successful repair *cost* vs. a miniature-2-style re-generation (where the agent loop generates the whole tool from scratch)?

This exercise makes visible what the scaling box in the text claims: self-healing is not a new idea, it is a selectable retry strategy — just as in Chapter 3, only with generated code as the "flaky operation".

## Bonus · Compare with Chapter 3

Open `../03_TheLoop/src/01_basic_loop.py` next to `01_dynamic_tool_agent.py`. Mentally strip the `generate_tool` action and the sandbox. What is left?

Note: which lines from Chapter 3 reappear structurally here? Where is the boundary between "Chapter 3 with different prompts" and "genuinely new idea"?

Then open `../03_TheLoop/src/03_retry_strategies.py` next to `03_dynamic_tool_agent_self_healing.py`. Find the LLM-guided-recovery site in both. The repair prompt and the four retry strategies have structurally the same form: *observe the error → re-prompt the LLM with the error context → use the corrected answer*. What is the only substantive difference?

If you do this exercise, you will see: Chapter 7 is not a new loop. It is the loop from Chapter 3, plus a tool registry that can grow at runtime — and the retry policy is the same on both levels. That is the entire conceptual novelty. The rest is sandbox policy.
