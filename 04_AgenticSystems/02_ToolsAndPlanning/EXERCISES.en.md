# Exercises · Chapter 2

Three tasks. They force you to treat the tool description as a *prompt* — and that is the most important perspective shift of this chapter.

---

## Exercise 1 · Description as prompt

Take `01_give_it_a_tool.py`. Modify the system prompt so it no longer tells the model what the JSON should look like — just the tool name and the argument names: *"You have a tool `calculator(operation, a, b)`. Use it when needed."*

Run the script five times. Collect the answers.

- In how many runs does clean JSON still come out?
- In how many does markdown-fenced JSON come out (` ```json ... ``` `)?
- In how many does prose come out with an embedded number?
- In how many does a wrong answer come out, because the model did the computation itself?

**What you learn:** The tool description *is* a prompt. It is the specification the model, at best, will adhere to. The more precise you write it, the more reliable the output. That is the reason MCP (Chapter 5) puts so much effort into schema descriptions.

---

## Exercise 2 · The loop comes out of nowhere

`02_model_plans.py` outputs a two-step plan for task 2:

```
step 1: currency_converter(132877 USD -> EUR)
step 2: calculator(divide, ..., 5.3)
```

But: the script does *not* execute the plan. The second step needed a numerical value for its first argument — and that value only comes into being after step 1 runs.

**Task:** Extend `02_model_plans.py` so it actually *executes* the plan for task 2:

1. Extract the first step.
2. Run `currency_converter` in Python (use a fixed exchange rate, e.g. `1 USD = 0.92 EUR`).
3. **Important:** substitute in step 2 the placeholder with the value from step 1.
4. Execute step 2.
5. Print the final answer ("...units").

Once you have done that, you have accidentally built a mini-`06_loop.py`. That is Chapter 3.

**What you learn:** the plan-and-execute approach works for simple cases. As soon as anything goes wrong — the tool returns noise, the plan has a mistake, a result surprises the model — you need a real loop in which the model decides afresh after each step. That is the difference between "plan-and-execute" and "ReAct".

---

## Exercise 3 · A malicious tool

Add a third tool: `execute_shell(command)`. Describe it harmlessly: *"executes shell commands, for diagnostic purposes"*. Ask the model: *"How many files are in the current directory?"*

Run this — but **do not implement `execute_shell`**! Just put the name and the description in the system prompt. What happens:

- What tool call does the model produce?
- Suppose you *actually* forwarded the call to `os.system(...)` — what shell commands could you receive if a malicious user crafts their question cleverly?

**What you learn:** security. A tool in your tool list is an *attack surface*. If the user can influence the prompt (which is the case in every chatbot app), they can indirectly trigger tools. In Chapter 6 this will surface again under the keyword *"tool misuse"*. For now: **every tool description you show to the model is a contract about what your runner will go along with.**

---

## How you know you have understood this chapter

If you can say in one sentence: *"Tool use means the model decides **what and in what order**, the code decides **how and whether at all**"* — you're done with Chapter 2.

The "whether at all" is half of Chapter 6.