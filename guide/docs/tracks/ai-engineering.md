# AI Engineering

From one LLM call to production agents. Each experiment: study the technique, build it without a framework, measure variants, and test it with an eval set and edge cases.

## Week 1 · Lookups, Vectors, and Your First LLM Call

**[The LLM API call](../weeks/week_01.md#ai-engineering-the-llm-api-call)**

Study sources:

- Your LLM provider's official quickstart and API reference.
- [Building LLM applications for production](https://huyenchip.com/2023/04/11/llm-engineering.html) by Chip Huyen.
- [Patterns for building LLM-based systems](https://eugeneyan.com/writing/llm-patterns/) by Eugene Yan.

| Unit | Study |
|---|---|
| [1. The API call and what comes back](../weeks/week_01.md#1-the-api-call-and-what-comes-back) | Your provider's quickstart: messages and roles, and the fields of the response. |
| [2. Temperature](../weeks/week_01.md#2-temperature) | The temperature section of the [inference chapter](https://dpaul0501.github.io/llm-agent-reads/part_06_inference_and_tricks/). Temperature divides the logits before the softmax you wrote above. |
| [3. Grounded answers, retries, and failures](../weeks/week_01.md#3-grounded-answers-retries-and-failures) | The retrieval section of Eugene Yan's patterns post, and [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) on the AWS Architecture Blog. |

## Week 2 · Pointers, Matrices, and Structured Output

**[Structured output and evals](../weeks/week_02.md#ai-engineering-structured-output-and-evals)**

Study sources:

- [Prompt Engineering](https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/) by Lilian Weng, the sections on few-shot and instruction prompting.
- [Getting started with JSON Schema](https://json-schema.org/learn/getting-started-step-by-step): `required`, `type`, and `additionalProperties`.
- [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/) by Hamel Husain.
- [Task-specific LLM evals that do and don't work](https://eugeneyan.com/writing/evals/) by Eugene Yan.
- Your LLM provider's docs on structured output.

| Unit | Study |
|---|---|
| [1. Prompting: system prompts, delimiters, and few-shot examples](../weeks/week_02.md#1-prompting-system-prompts-delimiters-and-few-shot-examples) | Lilian Weng on few-shot and instruction prompting: how example order and format change results. |
| [2. Structured output: ask for JSON, then use a schema](../weeks/week_02.md#2-structured-output-ask-for-json-then-use-a-schema) | The [`json` module](https://docs.python.org/3/library/json.html) docs (what `json.loads` raises), and JSON Schema getting started. Asking for JSON in the prompt is a request, not a guarantee. |
| [3. The eval set: three variants with error bars, then break it](../weeks/week_02.md#3-the-eval-set-three-variants-with-error-bars-then-break-it) | Hamel Husain on why the eval set comes before prompt changes, and Eugene Yan on evals for extraction. |
