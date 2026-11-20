# Week 1 pages: authoring spec (v3)

Source of truth for every page of Week 1. Pages are assembled by `build.py` from
`shell_head.html` + `pages/<name>.body.html` + `shell_tail.html`. You write only the body.

## Who reads this, and what they want

Engineering students through working professionals. They come to **learn, apply,
practise, and become interview-ready** (Google/Meta-level coding and ML/system design rounds).
They start from a product problem and watch it grow: a DSA question, then the same
question at scale, then a graph, then ML, then distributed systems and product design.

## The week's arc (one problem, expanding)

| Page | Rail title | What it does |
|---|---|---|
| `index` | The problem | Defines the problem. What the box is, inputs and outputs, what a good suggestion is (short; Day 4 does it properly), scale numbers, the naive score (mutual friends) that Days 1–3 use, the running example, the week's road map. No algorithms beyond a hand count. |
| `day_1` | Common friends | Counting mutual friends = **intersecting two friend lists**. Nested loops → hash set → sorted merge (two pointers) → galloping/binary search when sizes differ → bitsets. Then **advanced: distributed** — lists live on different machines (ship the smaller list), the all-pairs mutual-friend count as a MapReduce job (emit friend pairs per user, reduce by pair), skew from hubs, and approximate intersection with **MinHash** (Jaccard) and LSH as the at-scale shortcut. |
| `day_2` | The top k | From counts to the ten shown. **Static**: sort, size-k heap, quickselect, bucket counting; when each wins. **Stream**: counts change as friendships arrive — size-k heap over a stream, the median/two-heaps idea, heavy hitters with Misra–Gries / Space-Saving and Count-Min sketch, sliding windows. Why it matters for PYMK (static per-user lists vs live updates/trending). **Advanced: distributed** — local top-k + merge (k-way merge with a heap) is exact only when each item lives on one shard; when an item's count is split across shards you must aggregate first (or a threshold algorithm); fan-out/fan-in cost. |
| `day_3` | It is a graph | Only now name the graph. Friend lists = adjacency lists; friends-of-friends = a 2-hop BFS; the cost is the sum over friends of their degree, so hubs dominate (heavy-tailed degrees, measured); triadic closure and triangles; better pair scores from the graph: Jaccard, Adamic–Adar, resource allocation; random walks / personalised PageRank; connected components and union-find; capping hubs. Advanced: graph partitioning and vertex-centric (Pregel-style) computation. Bridge: we have several scores and no principled way to weigh them → Day 4. |
| `day_4` | Learn what engagement means | **The ML chapter.** Built from the article in `article_pymk_ml.md` (the author's own text: keep its order, its sections, its voice and most of its prose; adapt into page markup; add measured numbers and code). Days 1–3 assumed a naive score; companies want to maximise engagement, which depends on many factors. Then the **data science** part: calibration, percentiles and the bootstrap, A/B tests as hypothesis tests (two-proportion test, p-value, power, sample size, minimum detectable effect, novelty, network interference). **Ends** with "From features to representations": classical rankers drop raw ids, but when there are no features the id itself can learn a vector from behaviour (factorise who-befriends-whom; embeddings; two towers), measured on the week's graph, and it sets up Week 2. |
| `day_5` | A billion users | **Distributed algorithms** and **product design**, product last. Estimation; batch precompute vs online; the friends-of-friends join as a distributed job; sharding by user id and consistent hashing; caching (LRU); incremental updates from a stream of new friendships; tail latency and fan-out; Little's law; architecture end to end; then product design: eligibility and blocks, privacy and consent (contact import), notifications and fatigue, fair exposure, cold start; and the **same design in other products** (directed follow graphs, professional networks, "people to work with" inside a company). Ends with the Week 2 teaser (below). |
| `worksheet` | Worksheet and checks | Lab work items WI-1 to WI-8 (keep from old worksheet, retitled to the new day order), checks per day, interview drills (coding, ML design, system design) mapped to the new days. |

### Week 2 teaser (end of day_5, short)

Week 2 is **representation learning → word embeddings → representations in context (attention)**,
anchored on a new practical design problem from a different domain (not e-commerce, not social
media): **support-ticket triage** — route a new ticket to the person who can solve it, and show
the past tickets that solved the same problem. Ids (products, agents) and text with no hand
features: exactly where Day 4's last section leaves off. Two or three sentences, no dates.

## Teaching template, per concept

1. **Situation**: what the product needs right now, in the running example.
2. **The obvious attempt**, and where it breaks (measured if possible).
3. **The idea in plain words**, with a hand example on the running example.
4. **Code + a measured number** (on the week's graph, or a stated synthetic workload).
5. **Trade-off + interview takeaway** (what you would say out loud).
6. `<details class="deep"><summary>The math, step by step: …</summary><div>…</div></details>` — closed by default; derivations go here, guided line by line, never thrown at the reader in the main flow.
7. **Practice**: the day's LeetCode problems, linked.

Optional per major idea: `<p class="idea"><b>In one line.</b> …</p>`.

## Voice rules (hard)

- Applied first; math guided and folded. A formula in the main flow only when it is short and immediately read in words.
- No meta text: never mention feedback, earlier versions, rewrites, "as requested", mistakes, or the authoring process. No defensive hedging.
- No calendar dates. No study-time estimates ("this takes 30 minutes", "a few hours"). Day numbers only.
- British spelling (neighbour, optimise, behaviour), matching the article.
- Never describe any company's internal system; designs are reconstructions from first principles. Company names only for linked public sources.
- Nothing copied from third parties. Link papers/blogs/videos; don't reproduce their text or figures.

## Running example (use everywhere)

You (0), Ben (1), Chloe (2), Dev (3), Esha (4), Farid (5). You are friends with Ben and Chloe.
Ben and Chloe are friends. Ben knows Dev and Esha; Chloe knows Esha and Farid.
Mutual friends with You: Esha 2 (Ben, Chloe); Dev 1; Farid 1; Dev ranks before Farid by id.
Ben and Chloe are already friends of You, so never suggested.

## Numbers and code (hard)

- Every number on a page is **measured** by a script you ran, or is plain arithmetic shown on the page, or is an explicitly hypothetical input ("suppose a billion users with 300 friends each").
- Every code block is **tested**: it lives in `code/<page>/` as a runnable `.py` whose asserts pass, and the page shows the same code (or an exact excerpt).
- Measurement scripts print their numbers; keep their output in `code/<page>/*.out`.
- The week's graph: `code/data/edges.csv` (u,v,t; 10,000 users, 100,000 friendships in formation order) and `code/data/users.csv` (user, city, groups), generated by `week_01/data/make_graph.py` with seed 0. Regenerate with `python3 week_01/data/make_graph.py guide/src/week_01/code/data` if missing.
- Python 3 with NumPy is available as `python3`. No other third-party packages unless already installed; check first.
- Timings: state the machine-independent ratio or operation count as the headline; absolute times only as "on one laptop core".

## Markup (reuse the shell's CSS; read `old/*.body.html` for live examples)

- One `<section class="s" id="…" data-sec="…">` per page (more if the page is long), starting with
  `<div class="shead"><span class="sno">DAY 1 · COMMON FRIENDS</span><span class="dims"><span class="dim dsa">DSA</span>…</span></div>` then `<h2>`.
- Blocks: `<div class="blk dsa|ml|ai|sys|del"><div class="bh"><span class="kind">DSA · …</span></div> … </div>`; numbered `<h4>1 · Title</h4>` inside.
- Display math `<div class="eq">\[ … \]</div>`; inline `\( … \)` (MathJax 3).
- Code card: `<div class="code"><div class="ch"><span>path/file.py</span><button class="copy" type="button">Copy</button></div><pre><code class="language-python">…</code></pre></div>` (HTML-escape `<`, `>`, `&`).
- Tables inside `<div class="tablewrap"><table>…</table></div>`.
- Small flow diagrams: `<div class="dg"><div class="seq"><span class="nd">a</span><span class="lk">→</span><span class="nd hot">b</span></div><div class="cap">caption</div></div>`. Mermaid is not available.
- Figures: `<figure class="fig"><img src="img/NAME" alt="…"><figcaption>…</figcaption></figure>`. Images live in `img/` (source) and are copied by the build.
- LeetCode links: `<a href="https://leetcode.com/problems/<slug>/">NNN. Title</a>`.
- End each day with a checkpoint block:
  ```html
  <div class="check" data-check="day1">
    <div class="ch"><b>Checkpoint · Day 1</b><span data-count></span></div>
    <label class="ck"><input type="checkbox" data-id="d1a" data-dim="dsa"><span class="tx">…</span><span class="dim dsa">DSA</span></label>
  </div>
  ```
  Ids: `r1…` (index), `d1a…` (day 1) … `d5a…`, `w1…` and `c1…` (worksheet). Dims: `dsa ml ai sys del`. 6–10 checkpoints per day.
- No `<html>`, `<head>`, `<body>`, `<nav>`, pager or footer in a body file.

## LeetCode problems per day (all verified free)

- Day 1: ★349 Intersection of Two Arrays · 350 Intersection of Two Arrays II · 2540 Minimum Common Value · 2248 Intersection of Multiple Arrays · 2215 Find the Difference of Two Arrays · 1002 Find Common Characters · 160 Intersection of Two Linked Lists · 986 Interval List Intersections
- Day 2: ★347 Top K Frequent Elements · 215 Kth Largest Element in an Array · 692 Top K Frequent Words · 973 K Closest Points to Origin · ★703 Kth Largest Element in a Stream · 295 Find Median from Data Stream · 23 Merge k Sorted Lists · 373 Find K Pairs with Smallest Sums
- Day 3: ★1971 Find if Path Exists in Graph · 997 Find the Town Judge · 841 Keys and Rooms · 547 Number of Provinces · 684 Redundant Connection · 785 Is Graph Bipartite? · 133 Clone Graph · 1761 Minimum Degree of a Connected Trio in a Graph
- Day 4: 528 Random Pick with Weight · 382 Linked List Random Node · 398 Random Pick Index · 470 Implement Rand10() Using Rand7()
- Day 5: ★146 LRU Cache · 460 LFU Cache · 981 Time Based Key-Value Store · 1146 Snapshot Array · 380 Insert Delete GetRandom O(1) · 355 Design Twitter

## Reuse

`old/*.body.html` are the previous Week 1 pages (old order: reading, count it exactly, popular people,
read less, learn who connects, a billion users). Mine them freely for code, measurements, figures-as-HTML
and explanations — but re-run any code and re-measure any number you keep, and re-shape it to this arc.
