# ML/DL

From NumPy to training a small GPT. Each concept: study it, implement it from scratch, vary it, test it against the library, and cover its numerical corner cases and parameters.

## Week 1 · Lookups, Vectors, and Your First LLM Call

**[NumPy and vectors](../weeks/week_01.md#mldl-numpy-and-vectors)**

Study sources:

- [Python NumPy tutorial](https://cs231n.github.io/python-numpy-tutorial/) from Stanford CS231n.
- [Data manipulation](https://d2l.ai/chapter_preliminaries/ndarray.html) and [linear algebra](https://d2l.ai/chapter_preliminaries/linear-algebra.html) in *Dive into Deep Learning*.
- [3Blue1Brown](https://www.youtube.com/@3blue1brown): *Essence of Linear Algebra*, the dot product chapter.
- The [foundation chapter](https://dpaul0501.github.io/llm-agent-reads/module_01_foundations/) of *LLM Foundations from Scratch*.

| Unit | Study |
|---|---|
| [1. Arrays, dtype, and broadcasting](../weeks/week_01.md#1-arrays-dtype-and-broadcasting) | [Broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) and [copies and views](https://numpy.org/doc/stable/user/basics.copies.html) in the NumPy docs. |
| [2. Vectors: dot product, norms, and similarity](../weeks/week_01.md#2-vectors-dot-product-norms-and-similarity) | The dot product chapter (3Blue1Brown), and [pairwise metrics](https://scikit-learn.org/stable/modules/metrics.html) in the scikit-learn user guide. |
| [3. A numerically stable softmax](../weeks/week_01.md#3-a-numerically-stable-softmax) | The masking section of the [attention chapter](https://dpaul0501.github.io/llm-agent-reads/part_03_attention/), and [`math_utils.py`](https://github.com/dpaul0501/llm-agent-reads/blob/main/llm_foundations/math_utils.py) in llm-agent-reads. |

## Week 2 · Pointers, Matrices, and Structured Output

**[Matrices and probability for evals](../weeks/week_02.md#mldl-matrices-and-probability-for-evals)**

Study sources:

- [Linear algebra](https://d2l.ai/chapter_preliminaries/linear-algebra.html) and [probability](https://d2l.ai/chapter_preliminaries/probability.html) in *Dive into Deep Learning*.
- [Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra) by 3Blue1Brown, the chapters on rank and change of basis.
- [StatQuest](https://www.youtube.com/@statquest) on YouTube, for PCA, variance, and the bootstrap.
- [Seeing Theory](https://seeing-theory.brown.edu/), the chapters on basic probability and distributions.
- [Shapes and dot products](https://dpaul0501.github.io/llm-agent-reads/module_01_foundations/#foundation-linear-algebra), [linear maps and SVD](https://dpaul0501.github.io/llm-agent-reads/module_01_foundations/#foundation-svd), and [probability](https://dpaul0501.github.io/llm-agent-reads/module_01_foundations/#foundation-probability) in *LLM Foundations from Scratch*.

| Unit | Study |
|---|---|
| [1. Shapes, matrix multiply, and reshape vs transpose](../weeks/week_02.md#1-shapes-matrix-multiply-and-reshape-vs-transpose) | [copies and views](https://numpy.org/doc/stable/user/basics.copies.html) in the NumPy docs, and [`multi_head_attention.py`](https://github.com/dpaul0501/llm-agent-reads/blob/main/llm_foundations/multi_head_attention.py) in llm-agent-reads. Matmul is a shape contract: `(m, k) @ (k, n) → (m, n)`. |
| [2. Rank, the SVD, and PCA](../weeks/week_02.md#2-rank-the-svd-and-pca) | The rank chapters (3Blue1Brown), and [PCA](https://scikit-learn.org/stable/modules/decomposition.html#pca) in the scikit-learn user guide. `A = U Σ Vᵀ`; the condition number is the largest singular value over the smallest. Principal components are the right singular vectors of the *centered* data, with variance `S**2 / (n − 1)`. |
| [3. Probability for evals: expectation, variance, log-probabilities, standard error, the bootstrap](../weeks/week_02.md#3-probability-for-evals-expectation-variance-log-probabilities-standard-error-the-bootstrap) | Seeing Theory, and [`scipy.stats.bootstrap`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html) (`n_resamples`, `confidence_level`, `method`). An accuracy measured on n examples has a standard error of about √(p(1−p)/n). The bootstrap gives an interval without the formula. |
