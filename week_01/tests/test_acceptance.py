"""Week 1 acceptance tests. They fail on the starter code and pass when the spec is met.

Run:  pytest -q
Stretch (needs tiktoken and a network connection):  TOK_STRETCH=1 pytest -q -k stretch
"""

import itertools
import json
import math
import os
import random
import time
import tracemalloc
from collections import Counter
from pathlib import Path

import pytest
import regex
from hypothesis import given, settings, strategies as st

from tok.bpe import BPE, FORMAT_VERSION, GPT2_PATTERN, merge
from tok.cli import main
from tok.contracts import Constraint, LanguageModel, Tokenizer
from tok.decode import beam_search, generate, greedy
from tok.grammar import JsonConstraint, is_valid_json
from tok.ngram import NGramLM
from tok.sample import Sampler, argmax, categorical, log_softmax, reservoir_sample, softmax, top_k_filter, top_p_filter
from tok.stream import SEPARATOR, iter_documents

DATA = Path(__file__).resolve().parent.parent / "data"
CORPUS, RECORDS = DATA / "alice.txt", DATA / "records.txt"
NEG_INF = float("-inf")


@pytest.fixture(scope="module")
def docs():
    return list(iter_documents(CORPUS))


@pytest.fixture(scope="module")
def tok(docs):
    return BPE.train(docs, 1000)


@pytest.fixture(scope="module")
def records():
    return list(iter_documents(RECORDS))


@pytest.fixture(scope="module")
def json_tok(records):
    return BPE.train(records, 512)


@pytest.fixture(scope="module")
def json_lm(json_tok, records):
    return NGramLM(3, json_tok.vocab_size, 0.01).fit(json_tok.encode(r) for r in records)


def naive_train(texts, vocab_size):
    """The spec, written as slowly and plainly as possible. Your train() must give the same merges."""
    split = regex.compile(GPT2_PATTERN)
    counts = Counter(c.encode("utf-8") for t in texts for c in split.findall(t))
    words, freqs, merges = [list(w) for w in counts], list(counts.values()), []
    while 256 + len(merges) < vocab_size:
        pairs = Counter()
        for w, f in zip(words, freqs):
            for p in zip(w, w[1:]):
                pairs[p] += f
        if not pairs:
            break
        best = min(pairs, key=lambda p: (-pairs[p], p))  # most frequent, then the smallest pair
        if pairs[best] < 2:
            break
        merges.append(best)
        words = [merge(w, best, 255 + len(merges)) for w in words]
    return merges


class TableLM:
    """A tiny fixed language model: next-token scores depend on the last two tokens."""

    def __init__(self, vocab_size, seed=0):
        self.vocab_size, self.seed = vocab_size, seed

    def logprobs(self, context):
        rng = random.Random(f"{self.seed}:{tuple(context[-2:])}")
        return log_softmax([rng.gauss(0, 2) for _ in range(self.vocab_size)])


# --- Tokenizer: the contract ---------------------------------------------------------------

def test_tokenizer_satisfies_the_protocol(tok):
    assert isinstance(tok, Tokenizer)
    assert tok.vocab_size == 1000


def test_vocab_size_below_256_is_rejected():
    with pytest.raises(ValueError):
        BPE.train(["abc"], 255)


def test_golden_merges_with_the_tie_break_rule():
    # (a,a) is most frequent. Then (a,b) and (aa,a) tie at 2: the smaller pair (97, 98) wins.
    assert BPE.train(["aaabdaaabac"], 259).merges == [(97, 97), (97, 98), (256, 257)]


def test_training_stops_when_no_pair_repeats():
    assert BPE.train(["abcdef"], 300).vocab_size == 256


def test_train_matches_the_naive_spec(docs):
    sample = docs[:60]
    assert BPE.train(sample, 400).merges == naive_train(sample, 400)


def test_merges_never_cross_pre_tokenization_chunks(tok):
    split = regex.compile(GPT2_PATTERN)
    for i in range(256, tok.vocab_size):
        piece = tok.vocab[i].decode("utf-8", errors="replace")
        assert len(split.findall(piece)) == 1, f"token {i} {piece!r} spans chunks"


def test_training_is_not_a_rescan_per_merge(docs):
    start = time.perf_counter()
    BPE.train(docs, 2000)
    assert time.perf_counter() - start < 3.0, "re-counting every pair after every merge is too slow; use a heap"


# --- Tokenizer: round trip and compression --------------------------------------------------

@settings(max_examples=300, deadline=None)
@given(st.text())
def test_round_trip_any_text(tok, text):
    assert tok.decode(tok.encode(text)) == text


@pytest.mark.parametrize("text", [
    "", " ", "\n\n\n", "  leading and trailing  ", "tabs\tand\r\nCRLF",
    "नमस्ते दुनिया", "日本語のテキスト", "emoji 🙂👍🏽 and ZWJ 👩‍💻", "é vs é", "12345678901234567890",
])
def test_round_trip_hard_cases(tok, text):
    assert tok.decode(tok.encode(text)) == text


def test_compression_on_the_corpus(docs):
    text = "\n".join(docs)
    ours = len(text.encode("utf-8")) / len(BPE.train(docs, 2000).encode(text))
    try:
        from tokenizers import ByteLevelBPETokenizer
    except ImportError:
        assert ours >= 3.3
        return
    hf = ByteLevelBPETokenizer(add_prefix_space=False)
    hf.train_from_iterator(docs, vocab_size=2000, min_frequency=2, show_progress=False, special_tokens=[])
    theirs = len(text.encode("utf-8")) / len(hf.encode(text).ids)
    assert ours >= 0.9 * theirs, f"{ours:.2f} bytes/token vs Hugging Face {theirs:.2f}"


def test_decode_rejects_unknown_ids(tok):
    with pytest.raises(ValueError):
        tok.decode([tok.vocab_size])


def test_decode_of_a_partial_character_does_not_crash(tok):
    first_byte = "é".encode("utf-8")[0]
    assert tok.decode([first_byte]) == "�"


def test_save_and_load(tok, tmp_path):
    path = tmp_path / "tok.json"
    tok.save(path)
    loaded = BPE.load(path)
    assert loaded.merges == tok.merges
    assert loaded.encode("Alice was beginning") == tok.encode("Alice was beginning")


def test_load_rejects_another_format_version(tok, tmp_path):
    path = tmp_path / "tok.json"
    tok.save(path)
    doc = json.loads(path.read_text())
    assert doc["format_version"] == FORMAT_VERSION
    doc["format_version"] = FORMAT_VERSION + 1
    path.write_text(json.dumps(doc))
    with pytest.raises(ValueError):
        BPE.load(path)


# --- Streaming and held-out splits ---------------------------------------------------------

def test_iter_documents_reads_both_formats(tmp_path):
    txt = tmp_path / "c.txt"
    txt.write_text(f"one\n{SEPARATOR}\n\n{SEPARATOR}\ntwo\nlines\n", encoding="utf-8")
    assert list(iter_documents(txt)) == ["one", "two\nlines"]
    jl = tmp_path / "c.jsonl"
    jl.write_text('{"text": "a"}\n\n{"text": "b"}\n', encoding="utf-8")
    assert list(iter_documents(jl)) == ["a", "b"]


def test_iter_documents_keeps_memory_flat(tmp_path):
    path = tmp_path / "big.txt"
    doc = ("All work and no play makes a dull model. " * 25) + f"\n{SEPARATOR}\n"
    with path.open("w", encoding="utf-8") as f:
        for _ in range(20_000):  # about 20 MB
            f.write(doc)
    tracemalloc.start()
    n = sum(1 for _ in iter_documents(path))
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert n == 20_000
    assert peak < 5_000_000, f"peak {peak / 1e6:.1f} MB: are you reading the whole file?"


def test_reservoir_returns_everything_when_k_is_large():
    assert sorted(reservoir_sample(iter(range(5)), 10, random.Random(0))) == list(range(5))
    with pytest.raises(ValueError):
        reservoir_sample([], -1, random.Random(0))


def test_reservoir_is_uniform():
    rng, hits, trials = random.Random(42), Counter(), 20_000
    for _ in range(trials):
        hits.update(reservoir_sample(iter(range(10)), 3, rng))
    for item in range(10):
        assert abs(hits[item] / trials - 0.3) < 0.02, f"item {item}: {hits[item] / trials:.3f}"


# --- N-gram baseline -------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 3])
def test_probabilities_sum_to_one(tok, docs, n):
    lm = NGramLM(n, tok.vocab_size).fit(tok.encode(d) for d in docs[:50])
    assert isinstance(lm, LanguageModel)
    for context in ([], tok.encode("Alice"), [5, 6, 7], tok.encode("the Queen said")):
        lp = lm.logprobs(context)
        assert len(lp) == tok.vocab_size
        assert abs(sum(math.exp(x) for x in lp) - 1) < 1e-9
        assert lp[42] == pytest.approx(math.log(lm.prob(42, context)))


def test_an_untrained_model_has_perplexity_equal_to_the_vocab_size():
    assert NGramLM(2, 300).perplexity([[1, 2, 3, 4]]) == pytest.approx(300)


def test_fit_rejects_tokens_outside_the_vocabulary():
    with pytest.raises(ValueError):
        NGramLM(2, 10).fit([[1, 10]])


def test_bigram_beats_unigram_on_held_out_text(docs):
    train = [d for i, d in enumerate(docs) if i % 10]
    held = [d for i, d in enumerate(docs) if i % 10 == 0]
    tok = BPE.train(train, 512)
    ppl = {n: NGramLM(n, tok.vocab_size, 0.1).fit(tok.encode(d) for d in train).perplexity(tok.encode(d) for d in held)
           for n in (1, 2)}
    assert ppl[2] < 0.5 * ppl[1], ppl


# --- Sampling: from logits to one token ------------------------------------------------------

def test_log_softmax_is_stable_for_huge_logits():
    out = log_softmax([1000.0, 1000.0, NEG_INF])
    assert out[0] == pytest.approx(-math.log(2)) and out[1] == pytest.approx(-math.log(2))
    assert out[2] == NEG_INF
    with pytest.raises(ValueError):
        log_softmax([NEG_INF, NEG_INF])


@settings(max_examples=200, deadline=None)
@given(st.lists(st.floats(-50, 50), min_size=1, max_size=20), st.floats(-1e4, 1e4))
def test_softmax_sums_to_one_and_ignores_a_shift(logits, shift):
    p, q = softmax(logits), softmax([x + shift for x in logits])
    assert sum(p) == pytest.approx(1.0)
    assert p == pytest.approx(q, abs=1e-9)


def test_argmax_breaks_ties_to_the_lowest_id():
    assert argmax([1.0, 3.0, 3.0, 2.0]) == 1


def test_top_k_keeps_exactly_k_with_the_tie_break():
    out = top_k_filter([1.0, 3.0, 3.0, 2.0, 3.0], 2)
    assert [i for i, x in enumerate(out) if x != NEG_INF] == [1, 2]
    assert top_k_filter([1.0, 2.0], 10) == [1.0, 2.0]
    with pytest.raises(ValueError):
        top_k_filter([1.0], 0)


def test_top_p_keeps_the_smallest_set_that_reaches_p():
    logits = [math.log(x) for x in (0.5, 0.3, 0.2)]
    kept = lambda p: [i for i, x in enumerate(top_p_filter(logits, p)) if x != NEG_INF]
    assert kept(0.5) == [0]
    assert kept(0.7) == [0, 1]
    assert kept(0.8) == [0, 1]
    assert kept(0.81) == [0, 1, 2]
    assert kept(1.0) == [0, 1, 2]


@settings(max_examples=200, deadline=None)
@given(st.lists(st.floats(-10, 10), min_size=1, max_size=30), st.floats(0.01, 1.0))
def test_top_p_is_minimal(logits, p):
    probs = softmax(logits)
    kept = [i for i, x in enumerate(top_p_filter(logits, p)) if x != NEG_INF]
    mass = sum(probs[i] for i in kept)
    assert mass >= p - 1e-9
    assert mass - min(probs[i] for i in kept) < p + 1e-9  # dropping the smallest kept token falls short


def test_categorical_matches_the_probabilities_and_never_draws_zero():
    rng, probs = random.Random(7), [0.0, 0.1, 0.3, 0.0, 0.6]
    counts = Counter(categorical(probs, rng) for _ in range(100_000))
    assert counts[0] == counts[3] == 0
    for i in (1, 2, 4):
        assert abs(counts[i] / 100_000 - probs[i]) < 0.01


def test_temperature_reshapes_the_distribution():
    logits, rng = [2.0, 1.0, 0.0], random.Random(0)
    for t in (0.5, 1.0, 2.0):
        sampler = Sampler(temperature=t)
        counts = Counter(sampler(logits, rng) for _ in range(30_000))
        expect = softmax([x / t for x in logits])
        for i in range(3):
            assert abs(counts[i] / 30_000 - expect[i]) < 0.015, (t, i)


def test_temperature_is_applied_before_top_p():
    # At T=1, top-p 0.9 keeps tokens 0 and 1. At T=3 the distribution flattens and token 2 is needed too.
    rng, sampler = random.Random(0), Sampler(temperature=3.0, top_p=0.9)
    counts = Counter(sampler([3.0, 1.0, 0.0], rng) for _ in range(5_000))
    assert counts[2] > 500, counts


def test_temperature_zero_and_top_k_one_are_greedy():
    rng = random.Random(0)
    for _ in range(50):
        logits = [rng.gauss(0, 1) for _ in range(20)]
        assert Sampler(temperature=0)(logits, rng) == argmax(logits)
        assert Sampler(temperature=1.5, top_k=1)(logits, rng) == argmax(logits)


def test_sampling_is_reproducible_with_a_seed():
    logits, s = [0.1 * i for i in range(50)], Sampler(top_p=0.9)
    a = [s(logits, r) for r in [random.Random(3)] for _ in range(100)]
    b = [s(logits, r) for r in [random.Random(3)] for _ in range(100)]
    assert a == b


# --- Decoding loops --------------------------------------------------------------------------

def test_generate_with_temperature_zero_is_greedy():
    lm = TableLM(8)
    assert generate(lm, [1], 10, Sampler(temperature=0), random.Random(0)) == greedy(lm, [1], 10)


def test_beam_of_width_one_is_greedy():
    lm = TableLM(8, seed=1)
    (score, seq), = beam_search(lm, [2], 1, 6)
    assert seq == greedy(lm, [2], 6)


def test_a_wide_beam_finds_the_exact_best_sequence():
    lm, prompt, steps = TableLM(4, seed=2), [0], 3

    def score(seq):
        ids, total = list(prompt), 0.0
        for t in seq:
            total += lm.logprobs(ids)[t]
            ids.append(t)
        return total

    best = max(itertools.product(range(4), repeat=steps), key=score)
    beams = beam_search(lm, prompt, 4 ** steps, steps)
    assert beams[0][1] == list(best)
    assert beams[0][0] == pytest.approx(score(best))
    assert [b[0] for b in beams] == sorted((b[0] for b in beams), reverse=True)


# --- JSON grammar: the automaton -------------------------------------------------------------

@pytest.mark.parametrize("text", [
    '{}', '[]', '{"a":1}', '[1,-2,3.5,-0.5e10,0,1E+2]', '{"a":{"b":[true,false,null]}}',
    '["\\n\\t\\"\\\\\\u00e9"]', '{"नमस्ते":"दुनिया 🙂"}', '[[[[]]]]', '{"":""}',
])
def test_the_automaton_accepts_compact_json(text):
    assert is_valid_json(text.encode("utf-8"))


@pytest.mark.parametrize("text", [
    '', '1', '"a"', 'true', '{', '[1,]', '{"a":1,}', '{"a"}', '{"a":}', '[01]', '[1.]', '[.5]', '[-]',
    '[1e]', '[tru]', '[nul]', '{a:1}', '{"a" :1}', '[1, 2]', '[] ', '[]]', '[}', '{"a":1]', '["\\x"]',
    '["\\u12g4"]', '["a\nb"]', '[NaN]', '[Infinity]',
])
def test_the_automaton_rejects_invalid_json(text):
    assert not is_valid_json(text.encode("utf-8"))


def test_the_automaton_rejects_invalid_utf8_inside_strings():
    assert not is_valid_json(b'["\x80"]')
    assert not is_valid_json(b'["\xc3"]')  # a lead byte with no continuation
    assert is_valid_json('["é"]'.encode("utf-8"))


json_values = st.recursive(
    st.none() | st.booleans() | st.integers(-10**6, 10**6) | st.floats(allow_nan=False, allow_infinity=False) | st.text(),
    lambda inner: st.lists(inner, max_size=4) | st.dictionaries(st.text(max_size=5), inner, max_size=4),
    max_leaves=12,
)


@settings(max_examples=300, deadline=None)
@given(st.one_of(st.lists(json_values, max_size=4), st.dictionaries(st.text(max_size=5), json_values, max_size=4)))
def test_the_automaton_accepts_everything_json_dumps_writes(value):
    data = json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    assert is_valid_json(data)


@settings(max_examples=300, deadline=None)
@given(st.dictionaries(st.text(max_size=5), json_values, min_size=1, max_size=4), st.data())
def test_anything_the_automaton_accepts_parses(value, data):
    raw = bytearray(json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    i = data.draw(st.integers(0, len(raw) - 1))
    raw[i] = data.draw(st.sampled_from(b'{}[],:"0-.e\\ atx'))
    if is_valid_json(bytes(raw)):
        assert isinstance(json.loads(bytes(raw).decode("utf-8")), (dict, list))


def test_nesting_depth_is_limited():
    assert is_valid_json(b"[" * 32 + b"]" * 32)
    assert not is_valid_json(b"[" * 33 + b"]" * 33)


# --- JSON grammar: masking a vocabulary ------------------------------------------------------

def _states_along(constraint, tokens):
    s = constraint.start()
    yield s
    for t in tokens:
        s = constraint.advance(s, t)
        if s is None:
            return
        yield s


def test_json_constraint_satisfies_the_protocol(json_tok):
    assert isinstance(JsonConstraint(json_tok.vocab), Constraint)


def test_the_mask_matches_brute_force(json_tok, records):
    c = JsonConstraint(json_tok.vocab)
    for r in records[:15]:
        for s in _states_along(c, json_tok.encode(r)):
            brute = [t for t in range(json_tok.vocab_size) if c.advance(s, t) is not None]
            assert c.allowed(s) == brute
            assert (brute == []) == c.is_done(s)


def test_the_trie_prunes_when_few_tokens_fit(docs, records):
    big = BPE.train(docs + records, 4096)
    c = JsonConstraint(big.vocab, cache_size=0)
    states = [s for r in records[:20] for s in _states_along(c, big.encode(r))]
    sparse = [s for s in states if len(c.allowed(s)) < big.vocab_size // 10]  # e.g. after a value: only , ] }
    assert len(sparse) > 50
    start = time.perf_counter()
    for s in sparse:
        [t for t in range(big.vocab_size) if c.advance(s, t) is not None]
    brute = time.perf_counter() - start
    start = time.perf_counter()
    for s in sparse:
        c.allowed(s)
    trie = time.perf_counter() - start
    assert brute / trie > 4, f"only {brute / trie:.1f}x faster than checking every token: prune subtrees"


def test_constrained_generation_always_stays_valid(json_tok, json_lm):
    c, rng, done = JsonConstraint(json_tok.vocab), random.Random(0), 0
    for _ in range(30):
        ids = generate(json_lm, [], 300, Sampler(temperature=1.0), rng, c)
        states = list(_states_along(c, ids))
        assert len(states) == len(ids) + 1, "a sampled token left the grammar"
        if c.is_done(states[-1]):
            done += 1
            assert isinstance(json.loads(json_tok.decode(ids)), (dict, list))
            assert len(ids) < 300
    assert done >= 20, f"only {done}/30 samples finished within 300 tokens"


# --- CLI -------------------------------------------------------------------------------------

def test_cli_end_to_end(tmp_path, capsys):
    model = tmp_path / "tok.json"
    assert main(["train", str(CORPUS), "--vocab-size", "600", "--out", str(model)]) == 0
    capsys.readouterr()
    main(["encode", "--model", str(model), "Down the Rabbit-Hole"])
    ids = json.loads(capsys.readouterr().out)
    main(["decode", "--model", str(model), json.dumps(ids)])
    assert capsys.readouterr().out == "Down the Rabbit-Hole"
    main(["ppl", "--model", str(model), "--train", str(CORPUS), "--eval", str(CORPUS), "--n", "2"])
    assert json.loads(capsys.readouterr().out)["perplexity"] > 1


def test_cli_generate_json(tmp_path, capsys):
    model = tmp_path / "rec.json"
    main(["train", str(RECORDS), "--vocab-size", "512", "--out", str(model)])
    capsys.readouterr()
    main(["generate", "--model", str(model), "--train", str(RECORDS), "--json", "--samples", "10", "--seed", "1", "--temperature", "0.7"])
    out = json.loads(capsys.readouterr().out)
    assert len(out["samples"]) == 10 and out["valid_rate"] >= 0.7


# --- Stretch ---------------------------------------------------------------------------------

@pytest.mark.skipif(not os.environ.get("TOK_STRETCH"), reason="stretch: set TOK_STRETCH=1")
def test_stretch_matches_tiktoken_gpt2(docs):
    tiktoken = pytest.importorskip("tiktoken")
    enc, ours = tiktoken.get_encoding("gpt2"), BPE.from_tiktoken("gpt2")
    for text in docs[:100] + ["नमस्ते 🙂  wörld\n\n  x"]:
        assert [ours.vocab[i] for i in ours.encode(text)] == [enc.decode_single_token_bytes(i) for i in enc.encode(text)]


@pytest.mark.skipif(not os.environ.get("TOK_STRETCH"), reason="stretch: set TOK_STRETCH=1")
def test_stretch_masks_gpt2s_vocabulary(records):
    pytest.importorskip("tiktoken")
    gpt2 = BPE.from_tiktoken("gpt2")
    c = JsonConstraint(gpt2.vocab, cache_size=0)
    states = [s for r in records[:3] for s in _states_along(c, gpt2.encode(r))][::5]
    start = time.perf_counter()
    for s in states:
        c.allowed(s)
    assert (time.perf_counter() - start) / len(states) < 0.05
    for s in states[:5]:
        assert c.allowed(s) == [t for t in range(gpt2.vocab_size) if c.advance(s, t) is not None]
