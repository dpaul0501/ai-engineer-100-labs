# System Design & Engineering Practice

How systems are designed and how industry builds and ships them. Each week: one design (requirements, estimates, variations, failure modes) and the practices applied in your own repo.

## Week 1 · Lookups, Vectors, and Your First LLM Call

**[Requirements, estimates, and proof](../weeks/week_01.md#system-design-engineering-practice-requirements-estimates-and-proof)**

Study sources:

- [*Pro Git*](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository), chapter 2.
- [pytest: get started](https://docs.pytest.org/en/stable/getting-started.html) and [parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html).
- The [System Design Primer](https://github.com/donnemartin/system-design-primer#back-of-the-envelope-calculations), back-of-the-envelope calculations, and the [latency numbers](https://gist.github.com/jboner/2841832) table.
- [ByteByteGo](https://www.youtube.com/@ByteByteGo) on YouTube, for system design basics.
- [The reviewer guide](https://google.github.io/eng-practices/review/reviewer/) in Google's engineering practices.

| Unit | Study |
|---|---|
| [Design: requirements and estimates for pocket search](../weeks/week_01.md#design-requirements-and-estimates-for-pocket-search) | Back-of-the-envelope calculations and the latency numbers. |
| [Practice 1: git and a clean repo](../weeks/week_01.md#practice-1-git-and-a-clean-repo) | |
| [Practice 2: tests that prove something](../weeks/week_01.md#practice-2-tests-that-prove-something) | |
| [Practice 3: code review](../weeks/week_01.md#practice-3-code-review) | |

## Week 2 · Pointers, Matrices, and Structured Output

**[Interfaces, data models, and proof](../weeks/week_02.md#system-design-engineering-practice-interfaces-data-models-and-proof)**

Study sources:

- [Test Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html) by Martin Fowler.
- The [`typing` module](https://docs.python.org/3/library/typing.html) docs, `TypedDict` and `Literal`.
- The [Pydantic docs](https://docs.pydantic.dev/latest/).
- The error-handling sections of the [Zalando RESTful API guidelines](https://opensource.zalando.com/restful-api-guidelines/).
- The [Hypothesis docs](https://hypothesis.readthedocs.io/en/latest/), the quick start.
- [ByteByteGo](https://www.youtube.com/@ByteByteGo) on YouTube, for API design basics.
- [The reviewer guide](https://google.github.io/eng-practices/review/reviewer/) in Google's engineering practices.

| Unit | Study |
|---|---|
| [Design: API design and data modeling for the extraction tool](../weeks/week_02.md#design-api-design-and-data-modeling-for-the-extraction-tool) | The Zalando guidelines on errors and compatibility. |
| [Practice 1: red, green, refactor](../weeks/week_02.md#practice-1-red-green-refactor) | |
| [Practice 2: type hints and runtime validation](../weeks/week_02.md#practice-2-type-hints-and-runtime-validation) | |
| [Practice 3: property tests and code review](../weeks/week_02.md#practice-3-property-tests-and-code-review) | |
