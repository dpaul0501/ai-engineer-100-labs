# AI

LLMs from the inside out: tokens and decoding, prompts, context and memory, retrieval, agents and skills, then the models themselves. Each unit: study it, build it, vary it, test it, and cover its corner cases.

## Week 1 · Tokens and Decoding

**[Tokens and decoding](../weeks/week_01.md#ai-tokens-and-decoding)**

Study sources:

- Andrej Karpathy, [Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE) (video) and [minbpe](https://github.com/karpathy/minbpe) (code).
- Imad Dabbura, [Byte Pair Encoding from Scratch](https://imaddabbura.github.io/posts/nlp/BPE-Tokenizer.html): a short, code-first walkthrough.
- Patrick von Platen, [How to generate text](https://huggingface.co/blog/how-to-generate) (Hugging Face blog): greedy, beam, top-k, top-p, side by side.
- Chip Huyen, [Generation configurations: temperature, top-k, top-p, and test time compute](https://huyenchip.com/2024/01/16/sampling.html), including structured outputs.
- MLC, [Structured generation with XGrammar](https://blog.mlc.ai/2024/11/22/achieving-efficient-flexible-portable-structured-generation-with-xgrammar): pushdown automata and why most of a mask can be precomputed.
- Papers: Sennrich et al., [BPE for NMT](https://arxiv.org/abs/1508.07909); Holtzman et al., [The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751) (top-p); Willard and Louf, [Efficient Guided Generation](https://arxiv.org/abs/2307.09702) (Outlines).

| Unit | Study |
|---|---|
| [1. Bytes, UTF-8, and BPE](../weeks/week_01.md#1-bytes-utf-8-and-bpe) | How UTF-8 encodes a code point in 1–4 bytes; the merge loop in minbpe's `basic.py`; why encoding applies merges by **rank**, not frequency. |
| [2. From logits to one token](../weeks/week_01.md#2-from-logits-to-one-token) | The Hugging Face and Chip Huyen posts above. |
| [3. Structured output by construction](../weeks/week_01.md#3-structured-output-by-construction) | The XGrammar post; [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259), sections 2–7 (JSON's grammar is two pages); llama.cpp's [GBNF grammars](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md). |
