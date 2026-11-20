# How Do You Design Facebook's "People You May Know"?

### Start with mutual friends. End with a probability, a loss function — and a trap hidden in your own data.

![A user, a social graph, and a ranked list of suggested people.](images/hero.jpg)

*This is a design reconstruction from first principles — the way you'd build it in an ML system design interview or on a whiteboard — not a description of Facebook's internal systems.*

---

Every social app has the same quiet box:

**People You May Know.**

It looks trivial. A photo, a name, a button. Underneath it sits one of the cleanest ML problems in consumer tech — clean enough that if you can design this well, you can design almost any recommendation system.

Let's build it in the order you'd actually build it. Not model first. Business first.

## 1. What does "good" even look like?

A business doesn't want a model. It wants engagement.

But "engagement" is a foggy word until you pin it to an event you can count. In this box, the countable events are, in order:

1. We **show** person *v* to person *u* — an impression.
2. *u* **clicks** on *v*'s profile.
3. *u* **sends a friend request**.
4. *v* **accepts** it.
5. Weeks later, *u* and *v* actually **interact** — messages, comments, reactions.

Each step is a different definition of success, and the choice changes everything you build afterwards.

Optimise for clicks, and you'll surface familiar, curious, click-bait-y faces — exes, celebrities, people *u* wants to look at but never befriend. Optimise for requests sent, and you'll favour people *u* adds impulsively. Optimise for requests **accepted**, and now you need *v* to want this too — it's a two-sided event. Optimise for interaction 30 days later, and you get the truest "good connection" — but the label arrives a month late, and it's rare.

A sensible primary target, and the one we'll use:

> **A request is sent after the impression, and accepted within a fixed window — say 7 days.**

It's countable, it's two-sided, it arrives fast enough to learn from, and it's close to what the business actually means by engagement: a new, real connection, not a click.

Hold onto that sentence. Every design decision below is just that sentence, made mathematical.

## 2. The whole problem, in one function

Take two users, *u* (the viewer) and *v* (the candidate). We want a function:

$$f(u, v) \;\rightarrow\; P(\text{request sent and accepted} \mid u \text{ is shown } v)$$

A probability. Not just a score.

Why insist on a probability when, for ranking, any score that orders people correctly would do? Four reasons:

- **Calibration lets you compare across surfaces.** A 0.3 on the feed box and a 0.3 in search suggestions should mean the same thing if you're going to blend or budget them.
- **You can set thresholds.** "Never show anything below 0.02" is a product decision you can only make with real probabilities.
- **You can compute expected value.** Show the candidate with the highest expected *good* outcome, not just the highest rank — useful when a slot has a cost, like annoying the user.
- **You can debug it.** If the model says 0.8 and only 4 out of 10 such pairs connect, the model is *wrong in a measurable way*, not just "ranking badly."

A score says *v₁ before v₂*. A probability says *how much, and how sure*. For a system that will make billions of these calls, the second is worth having.

## 3. Who are *u* and *v*, exactly?

A user is not an ID. For this function, each user is two things:

**A profile** — relatively stable facts: location, school, workplace, groups, pages followed, language, how long they've been on the platform, how many friends they already have.

**A behavioural profile** — what they *do*: how often they log in, how often they send requests, how often they accept them, whose profiles they view, what they dismiss, how quickly they respond.

And here's the first real insight of the whole design:

> **The pair features matter more than either person's features.**

Knowing *u* is active and *v* is popular tells you little. Knowing *u* and *v* went to the same school, in the same years, share 14 friends, and *u* viewed *v*'s profile twice last month — that tells you almost everything. Link prediction is a problem about the *space between* two people, not about either person alone.

So the question "given *u* and *v*, how likely is a connection?" is really: *how much evidence of a shared world do these two people carry, and how receptive is each of them, right now?*

## 4. Start dumb: the mutual-friends rule

Before any ML, build the rule a smart person would write in an afternoon:

$$\text{score}(u,v) = |\,\text{friends}(u) \cap \text{friends}(v)\,|$$

Rank candidates by how many mutual friends they share with *u*. Show the top few.

![u and v share three mutual friends, M1, M2 and M3. The dashed edge is the one we're predicting.](images/fig1-mutual-friends.png)

This works embarrassingly well, because of a deep fact about social graphs — **triadic closure**: if *u* knows M and *v* knows M, *u* and *v* probably move in the same world and are far more likely to know, or want to know, each other than two strangers.

Ship this first. It's your baseline, your fallback, and — importantly — the thing every fancier model must *beat*, or you delete the fancier model.

But the rule has cracks, and naming them is how you discover your features:

- **All mutual friends are not equal.** A mutual friend who knows everyone (the school celebrity with 4,000 friends) is weak evidence. A mutual friend with 30 friends who knows both of you is strong evidence. That's the idea behind **Adamic–Adar**: weight each mutual friend by *1 / log(their friend count)*.
- **It ignores receptiveness.** 40 mutual friends means nothing if *v* hasn't logged in for a year or never accepts requests.
- **It can't personalise.** It gives the same answer for a *u* who adds everyone and a *u* who adds nobody.
- **It dies on cold start.** A new user has no friends, so no mutuals, so no suggestions — exactly when suggestions matter most.

You can patch each crack with another hand-written rule — same school + overlapping years, same workplace, imported contacts, shared group. Do it. This "rules v1" is a genuinely useful system.

But notice what you're doing: hand-tuning weights ("is a shared school worth 3 mutual friends, or 5?") with no principled way to know if you're right. That discomfort is the doorway to ML.

## 5. Do we have history? Then it's supervised learning

The question that decides your whole approach:

**Have we shown suggestions before, and recorded what happened?**

At Facebook scale, yes — billions of impressions, each with an outcome. That turns a guessing problem into a **supervised learning** problem:

- **One row per impression**: the pair *(u, v)* that was shown, the features of that pair *at the moment it was shown*, and what happened next.
- **Label = 1** if a request was sent and accepted within the window. **Label = 0** otherwise.
- **Learn** a function that maps features → probability of label 1, in a way that generalises to pairs it has never seen.

(If the answer were *no* — a brand-new product with no history — you'd stay with rules and exploration while you collect this data. That's a different article.)

Two warnings belong here, because they quietly ruin real systems:

**Point-in-time correctness.** Features must be what was true *at impression time*, not today. If you compute "mutual friends" using today's graph, you've leaked the future into training — *u* and *v* are friends *now partly because you suggested them*. Your offline numbers will look magical and your live system will not.

**"Ignored" is not the same as "rejected."** A 0 can mean *v* was a bad suggestion — or that *u* never scrolled far enough to see it. Keep the strong signal separate: an explicit **dismiss / "remove" click** is a true negative. A passive non-click is a weak one. Good label design is half of good modelling.

## 6. Error and loss: what does "wrong" mean?

A model outputs a probability *p*. Reality outputs 0 or 1. The gap between them is **error** — and to train anything, you need one number that says how wrong, overall, the model was. That's the **loss function**.

For this problem, the standard choice is **log loss** (binary cross-entropy):

$$\text{loss} = -\big[\, y \log p + (1-y)\log(1-p) \,\big]$$

Read it in plain English:

- If the connection happened (*y = 1*) and you predicted *p = 0.9*, loss is small: −log(0.9) ≈ **0.11**.
- If it happened and you predicted *p = 0.1* — you were confidently wrong — loss is −log(0.1) = **2.30**. Twenty times worse.
- If it didn't happen (*y = 0*) and you predicted *p = 0.9*, same punishment in mirror image.

Log loss has exactly the personality this problem needs:

1. **It punishes confident wrongness brutally** — which is what makes the outputs behave like real probabilities, not just ranks.
2. **It's smooth and differentiable**, so a model can climb down it by gradient descent. "Accuracy" can't be trained on directly — it's a staircase, flat almost everywhere, with no signal about *which way* to move.
3. **It rewards honesty.** The best strategy under log loss is to say what you truly believe. A model gaming it only hurts itself.

Train by minimising average log loss over millions of historical impressions. That one sentence *is* the learning algorithm's job description; everything else is machinery.

## 7. The predictor: models, in the order you'd try them

**v1 — Logistic regression** on a handful of pair features. It's linear, fast, interpretable ("same school adds this much, each Adamic–Adar point adds that much"), and its probabilities are naturally well-calibrated. You will be surprised how far this gets. This is also the model you can *explain* when product asks why someone was suggested.

**v2 — Gradient-boosted trees.** Real life has interactions a line can't express: *mutual friends matter a lot — but only if v is active; same city matters — but only for users with few friends so far.* Trees find these bends without you hand-specifying them. In practice, this class of model carried most large-scale ranking systems for a decade, for good reason.

**v3 — Learned representations.** Two-tower / embedding models learn a vector per user such that likely connections sit near each other; graph neural networks go further and learn from the structure of the friend graph itself. These shine at **candidate generation** — finding plausible *v*'s among billions — and at cold start, where hand features are empty but behaviour still leaves a trace.

And split the system in two while you're at it, because no model scores *every* pair:

![Candidates first, then ranking, then a few shown slots, then outcomes that become tomorrow's data.](images/fig2-funnel.png)

**Candidate generation** (cheap, high-recall): friends-of-friends, same school/work/city, contact imports, embedding neighbours. Thousands in, no one good lost. **Ranking** (expensive, high-precision): the *f(u, v)* above, applied to those thousands, top-K shown.

The rule for moving from v1 → v2 → v3 is not fashion. It's: *the new model must beat the old one offline, then online, by enough to pay for its complexity.* Otherwise the dumb rule from §4 is still your production system — and there's no shame in that. There's shame in the opposite.

## 8. Features: where the wins actually come from

Models are interchangeable. Features are the product. The groups that matter:

**Graph features (the pair)**
Mutual-friend count · Jaccard similarity of friend sets · Adamic–Adar score · mutual friends weighted by how strongly *u* actually interacts with them · shortest path between *u* and *v* · time since the newest mutual connection formed.

**Shared-world features (the pair)**
Same school / workplace, and did the years overlap? · same city · shared groups, events, pages · contact-book overlap, if the user granted it.

**Receptiveness features (each person)**
*v*'s historical acceptance rate · *v*'s recent activity · *u*'s historical sending rate · *u*'s friend count (a user at 4,900 friends needs nobody) · account age.

**Behavioural / affinity features (the pair, handled with care)**
*u* viewed *v*'s profile · *u* searched *v*'s name · past interactions in comments or groups. These are powerful — and exactly where you must be strict about consent, product policy, and leakage.

**Negative features (often the strongest of all)**
*u* dismissed *v* before · *u* dismissed people *like v* before · *v* was shown to *u* repeatedly with no action. A system that re-suggests a dismissed person isn't dumb — it's rude, and users remember it.

**Context features**
Which surface, what position in the list, time of day, device. Position matters more than you'd like: things shown first get clicked more *because they were shown first* — remember that when we get to evaluation.

## 9. Offline evaluation: why accuracy is a lie here

Now: how do you know the function is *good enough* — before it touches a real user?

First, kill the metric everyone reaches for. **Accuracy.**

Suppose 10,000 impressions produce 100 accepted connections — a 1% positive rate, realistic for this problem. A "model" that predicts **no, for everyone**, scores:

**99% accuracy. And it is completely useless.** It suggests nobody, ranks nobody, learns nothing.

Accuracy fails because the classes are wildly imbalanced and because we don't actually make yes/no decisions — we *rank*. So use metrics that measure ranking:

**ROC-AUC.** Pick one random positive pair and one random negative pair. What's the probability your model scored the positive one higher? That's AUC. 0.5 is coin-flipping; 1.0 is perfect separation. It's a good, stable, threshold-free summary.

**PR-AUC (average precision).** Same ranking, judged through precision and recall instead — and when positives are rare, this is the honest one. Its random baseline isn't 0.5; it's the prevalence itself, ~0.01. A model can post a proud ROC-AUC of 0.92 while its PR-AUC is 0.31 — which is the number that tells you what the top of your list actually looks like.

![The same model can look excellent on ROC-AUC and merely decent on PR-AUC. With rare positives, believe the second.](images/fig3-roc-vs-pr.png)

**Precision@K / Recall@K.** You only have K slots — often fewer than ten. What fraction of your top-K were real connections? Of all the connections you could have made, how many were in your top-K? This is the offline metric closest to the user's actual experience.

**Calibration.** Bucket predictions: of all pairs scored ≈0.2, did ≈20% connect? If not, your "probabilities" are just scores wearing a costume — go back to §2 and fix it.

Three evaluation disciplines matter as much as the metric choice:

- **Split by time, not randomly.** Train on last month, test on this month. A random split leaks the future and flatters you.
- **Slice everything.** New users, low-friend users, different countries and languages, dismissed-rate by slice. An average can improve while the experience for new users — the ones who need this most — quietly gets worse.
- **Compare against the rule.** Every offline report starts with: mutual-friends baseline, then your model. No baseline, no claim.

## 10. Online evaluation: the A/B test is the real exam

Offline metrics are a rehearsal. The performance is an **A/B test**:

- Randomly assign **users** (not impressions — the same person must live in one world) to control (old system) or treatment (new model).
- **Primary metric:** accepted connections per user — the business sentence from §1, counted live.
- **Guardrail metrics:** dismissals per impression, reports/blocks, session time, overall retention. A model that grows connections by spamming suggestions will show it here first.
- Run it long enough to outlast the **novelty effect** — anything new gets clicked for a week.

One subtlety specific to this problem: **network interference.** If *u* is in treatment and *v* is in control, *u*'s new suggestion can change *v*'s experience too. Your two worlds leak into each other, which dilutes the measured effect. The clean fix — randomising whole clusters of the graph — is expensive; the pragmatic fix is knowing the bias exists and reading your lift as a lower bound.

Ship rule: offline win + online win on the primary metric + no guardrail regression. All three, or it doesn't ship.

## 11. The trap: exposure bias

Everything above has a crack running through it, and it's the most important idea in this article.

**Your training data was created by your previous system.**

You only have labels for pairs you *showed*. You showed those pairs because the old rule — mutual friends — already thought they were good. So your shiny new model learns, in part, "pairs the old rule liked tend to succeed." Pairs the old rule never surfaced have no labels at all, and if you treat "never shown" as "negative," you teach the model they were bad — when in truth **they were never tried**.

![The old model decides who's shown; we only learn from who's shown; the new model inherits the old model's blind spots.](images/fig4-exposure-bias.png)

Left alone, this loop narrows the world: the same kinds of suggestions, for the same kinds of users, forever — and your offline metrics will *approve*, because your test set has the same bias as your training set. This is **exposure bias** (a form of selection bias), and it compounds.

The standard defences:

- **Log the propensity.** Record *why and with what probability* each pair was shown. That lets you re-weight training and do counterfactual evaluation — estimating how a *new* policy would have done on *old* data (inverse propensity scoring).
- **Keep an exploration bucket.** For a small slice of traffic, show some candidates at random from a broader pool. It costs a little short-term quality and buys you unbiased data about the world outside your current beliefs. No exploration, no discovery — ever.
- **Never shown ≠ negative.** Treat unshown pairs as *unlabelled*, not as zeros. (This framing has a name: positive–unlabelled learning.)
- **Correct for position.** A click on position 1 and a click on position 8 are not the same evidence. Model position as a feature in training — then remove it at serving time.

Notice the pattern: the hardest problems in this system are not model problems. They're **data problems created by the system itself.**

## 12. The whole thing, on one page

1. **Define the win.** Engagement = a request sent *and accepted* within a window. Everything else is a proxy.
2. **Write the function.** *f(u, v) → P(connection)* — a calibrated probability, not just a score.
3. **Ship the dumb rule.** Rank by mutual friends. Measure it. It's your baseline and your fallback.
4. **Sharpen the rule.** Adamic–Adar, shared school/work/city, contacts — hand features, hand weights.
5. **Turn history into data.** One row per impression, point-in-time features, label in a fixed window, dismissals as true negatives.
6. **Pick the loss.** Log loss — it punishes confident wrongness and forces honest probabilities.
7. **Climb the model ladder.** Logistic regression → boosted trees → embeddings / graph models, only when each step beats the last, offline *and* online.
8. **Evaluate like an adult.** Never accuracy. PR-AUC and Precision@K for ranking quality, ROC-AUC as a summary, calibration for honesty — split by time, sliced by user type, always against the baseline.
9. **Prove it live.** User-level A/B test, accepted connections as the primary metric, dismissals and reports as guardrails, interference in mind.
10. **Fight your own shadow.** Log propensities, explore on a small slice, and never mistake "never shown" for "no good."

That's the design. A box that says *People You May Know* is really a loop:

**show → observe → learn → show better** —

and the craft is in keeping that loop honest.

---

*If you're preparing for ML system design interviews: practise saying §1 and §11 out loud. Anyone can name a model. Naming the right label, and spotting that your data was generated by your last model, is what separates a designer from a model-picker.*

**Suggested Medium tags:** Machine Learning, Recommendation Systems, System Design, Data Science, Social Networks
