# The Copy Bar — Global + India Craft Standard for Skincare Social Copy

**Status:** proposed bar v1 (research doc; no code changed)
**Scope:** Instagram-first skincare social captions (feed, Reels, carousels) for a Neutrogena-like fixture brand in India, judged against the highest craft standard observable globally and in Indian D2C.
**Relationship to existing docs:** `docs/style/rubric.md` defines the current 7-dimension LLM judge bar (PASS = avg ≥ 4.0, no dim = 1–2) and `apps/api/boxes/rubric.py` the deterministic 5-dimension scorer (PASS = avg ≥ 3.8, no dim < 3). **This document raises the bar above both** and ends with a concrete scorer-upgrade spec (§5).

**Evidence convention:** every performance claim carries a source link. Claims marked **[practitioner-consensus]** reflect widely-agreed operator practice without a single citable dataset. Campaign facts carry award/press links. Where studies conflict, both findings are shown and a decision rule is given.

---

## 1. THE BAR — 10 points

Each point states the rule, the evidence, and a deterministic test (how the upgraded scorer will check it).

### B1. The first line is the ad; everything else is the proof

The first line carries the entire scroll-stop burden. On feed posts, only the first **~125 characters** render before Instagram's "more" fold ([glowsocial](https://glowsocial.com/blog/social-media-caption-length)); posts whose first line was a provocative statement/question averaged **+41% engagement** vs context-first openings (n=10,000 posts, [Campground Social](https://campgroundsocial.com/blog/engagement-study-2026)). For video ads, the same physics appear as Meta's hook rate: **30–40% (3-sec views ÷ impressions) is the working benchmark; below ~25% is treated as a creative problem, not a media problem** ([Motion](https://motionapp.com/blog/key-creative-performance-metrics)) **[practitioner-consensus]**.

Rules: hook lands in ≤ 8 words AND ≤ 60 characters; no preamble, no greeting, no brand name, no "Introducing/Say hello to". Hook types allowed: command, contradiction, confession, specific number, genuinely-answerable question (see B5).

### B2. Voice physics: "I" confesses, "we" announces — ration the brand plural

The largest causal dataset on headline wording (Upworthy Research Archive, **32,487 randomized A/B experiments**) found first-person *singular* ("I") strongly positive (**β=0.24, p≈6×10⁻¹⁴**) while first-person *plural* ("we") was **negative** (**β=−0.15, p≈2×10⁻⁵**); plain "you" was *not* a reliable winner in headline CTR ([PLOS One 2023](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0281682)). In persuasion contexts (donations, crowdfunding), second-person "you"-words show a strong *positive* causal effect ([Columbia causal-text paper](http://www.columbia.edu/~on2110/Papers/Causal_text.pdf)), consistent with Packard & Berger (2020): "you" makes readers map the appeal onto a specific person they know. In languages with formal/informal address, the **informal form outperforms formal — and formal scores below no-pronoun control** ([Radboud T/V study](https://repository.ubn.ru.nl/bitstream/handle/2066/296831/1/296831.pdf)).

Translation for us: confessions and peer voice ("I used to sleep in makeup…") are the engine; direct "you" address earns attention in CTAs and pain-point lines; **"we" is reserved for receipts** (launches, proof, policy). Corporate "we're excited…" is a hard fail.

### B3. Numbers are copy

Every benefit claim carries a number, ingredient+concentration, timeframe, or sensory mechanism within one sentence. This is the shared grammar of the brands that built trust-led categories: The Ordinary's names *are* the ingredient deck; Minimalist prints concentrations, pH and even supplier names on pack — co-founder Mohit Yadav: printing a number forces R&D readiness because "people can ask why this is 3.6, not 3.8" ([Blume podcast S4E7](https://blume.vc/podcasts/blume-podcast/how-minimalist-won-indias-skincare-market-by-being-transparent-s4e7-destiny-avenged-weekend-ep)). d'you compresses a whole pitch into counted nouns: *"One serum. 11 actives. 36 iterations. No fluff."* ([d'you About](https://www.dyou.co/pages/about-us)).

Test: at least one `[%|₹|\d+\s*(ml|g|x|weeks|days|%)]` token per caption; zero unanchored superlatives.

### B4. One concrete image beats three adjectives

Adjective pairs ("luxurious and nourishing") are replaced by a picture a reader can see ("absorbs before your chai cools"). This is Aesop/Oatly craft applied to India: specificity does the persuading, adjectives only decorate. Test: adjective-adjective pairs within two words (`\b(\w+)\s+(and|&)\s+(\w+)ed?\b` heuristics + curated list), doubled intensifiers, and abstract nouns (*glow, radiance, perfection*) appearing without a mechanism nearby.

### B5. Question economy: earn the comment, don't beg for it

Questions measurably drive conversation: **+37% more comments** when the caption poses a question, and comment-directed CTAs earn **~203% more comments**, while asking-for-likes slightly *reduces* likes (Metricool 2026 study, 24.4M posts / 375K accounts, via [eMarketer](https://emarketer.com/content/carousels-questions-drive-instagram-engagement) and [unlockdm summary](https://tryunlockdm.com/blog/instagram-comments-vs-likes-2026)); an independent 4,278-post analysis found questions ≈**2× engagement** (3.5% vs 1.9%) and **hard CTAs slightly hurt** (1.7% vs 2.3%, [PostQuick](https://postquick.ai/blog/what-drives-engagement-data-study-2026)); a third study found end-of-caption questions **+34% comment rate** and "save this" CTAs **+67% save rate** (n=10,000, [Campground Social](https://campgroundsocial.com/blog/engagement-study-2026)).

But the question must be *answerable in one line on a phone* ("Which step are you stuck on — 1, 2, or 3?"). Rhetorical filler ("Want glowing skin?") is banned: it reads as ad-speak, and our rubric already treats it as a 3-at-best hook. Max one question per caption; generic engagement bait ("comment YES") is a fail — platforms demote it and replies are low-value ([practitioner-consensus], [unlockdm](https://tryunlockdm.com/blog/instagram-comments-vs-likes-2026)).

### B6. Length obeys the format, and avoids the dead zones

Findings conflict by format and account size — so we encode bands, not one number:

| Format / objective | Band | Evidence |
|---|---|---|
| Reels caption (discovery) | ≤ 50 chars (punchy) **or** 151–400 chars | <50-char captions spiked at 6.23% ER vs 2.04% for 51–125 (n=4,408, [PostPlanify](https://postplanify.com/blog/instagram-caption-length)); mid-tier creators peaked at 151–400 chars and fell **~5×** past 400 (9,487 videos, [ContentLabs](https://www.thecontentlabs.app/blog/do-seo-captions-work-on-tiktok-instagram-2026)) |
| Feed single image | 126–800 chars | feed-post ER climbed with length: ≤125 chars median ~0 interactions vs 5.0–5.42% for 126+ (PostPlanify) |
| Carousel (education/save) | 800–2,200 chars allowed; hook still first | long captions win saves/shares; carousels earn **9× more saves** than single images (Metricool via eMarketer); 1,500–2,200-char captions hit 5.2% ER in a 2,400-post panel ([iimagined](https://iimagined.ai/blog/instagram-captions-guide-2026) — directional, self-published) |
| Dead zone (avoid) | ~51–125 chars on feed; 200–800 "middle" on short-form | both panels independently find the middle underperforms both extremes (PostPlanify; iimagined calls 200–800 "the dead zone" at 2.4%) |

Universal sub-rules: captions > 300 chars must use line breaks/white space (**+8% engagement** vs wall-of-text, Campground Social); the searchable phrase belongs inside the first 125 characters — keyword-led captions beat hashtag-only twins by **~30% reach** in Hootsuite's matched test ([via biogpt summary](https://biogpt.io/instagram-seo-captions-how-to-write-captions-that-rank-in-search)); since July 2025 public professional content is Google-indexable, so captions are landing-page titles too.

### B7. Hashtags are seasoning, not strategy

Instagram leadership has said publicly that hashtags don't drive reach (Mosseri), and the 2026 working consensus caps them at **~5** ([algorithm summary citing Mosseri](https://aipowereddahlia.com/blog/instagram-algorithm-2026-what-works)). Data: **1–3 relevant tags = 4.8% ER; 11+ tags = 0.9% (worst bucket)** (PostQuick, n=4,278); posts using ≥1 hashtag showed 32% fewer views — explicitly correlational, likely reflecting account habits (Metricool via eMarketer); 30-tag stuffing now reads as a spam signal ([gwaa analysis](https://hashtags.gwaa.net/how-many-hashtags-instagram)). Our rule: **1–3 niche tags** (mid-volume, 50K–500K posts), varied between consecutive posts, never a wall, never trending-tag hijacking.

### B8. Emoji rationing — meaning or nothing

Emoji lift engagement broadly (tweets +25.4%, Wordstream; Facebook likes +57%, Zazzle — via [Sendible roundup](https://www.sendible.com/insights/social-media-emojis); HubSpot's 19.6M-post study found rare/novel emojis out-click popular ones, [HubSpot](https://blog.hubspot.com/marketing/best-emojis)). But skincare sits near the medical-adjacent zone where a reported Moz test found emojis in titles **cut CTR 3–5%** for medical/legal content ([getmoji summary of Moz data](https://getmoji.app/blog/emoji-seo-social-media) — secondary citation, treat directionally). Our bar stays conservative: **0–2 emoji per caption**, chosen for meaning; zero in claim sentences; zero on PDP/email. Accessibility: screen readers announce every emoji by name — decoration costs comprehension.

### B9. Claim safety is craft, and derm-brands prove warmth ≠ claims

Cosmetic-zone language only ("visibly", "reduces the look of", "helps manage"); no cure/treat/permanent, no unsourced "dermatologist-approved", no before-after guarantees (ASCI norms; already enforced in `docs/style/rubric.md` §D6). The global winners show you can be warm and funny **around** the claim without touching it: CeraVe spent a four-week conspiracy comedy ("Michael CeraVe") defending exactly one sentence of claim copy — *"CeraVe is and always has been developed with dermatologists"* — and won the Cannes Social & Influencer Grand Prix, 32B earned impressions and **+25% sales** ([Adweek](https://adweek.com/brand-marketing/michael-cera-cerave-super-bowl-ad), [Marketing Dive](https://marketingdive.com/news/cerave-michael-cera-super-bowl-campaign-trail/707307), [D&AD archive](https://www.dandad.org/work/d-ad-awards-archive/michael-cerave), [Cannes 2024 GP list](https://www.nrgdigital.com.au/2024-cannes-lions-winners/)). La Roche-Posay runs humor and celebrity (Law Roach name-play, 2025) while its health work stays strictly educational ([PR Newswire via Lelezard](https://lelezard.com/en/news-21935987.html), [#DermsAgainstBurns](https://beautymatter.com/articles/la-roche-posay-pushes-back-against-tik-toks-risky-sunburn-tattoos-trend), [Life-Saving Routine](https://betc.com/en/society/la-roche-posay-saving-life-routine-en)). d'you states the ethic outright: *"If we can't explain it, we don't deserve to sell it"* and "education over fear" ([d'you](https://www.dyou.co/pages/about-us)). Fear-selling and miracle talk are anti-patterns even when legal.

### B10. Local truth, not local costume

India shows up as a *situation*, never as a sticker: humidity/T-zone wars, monsoon fungal-acne season, 3 PM webcam shine, metro commute, shaadi-season timelines, ₹ pricing with comma format, metric sizes. Hinglish-light (≤ 2 words, social only) passes only the Pune-texting-friend test. Precedents: Foxtale's meme-native "No Fox Given!" register and "You Glow Different" campaign ([Foxtale IG](https://www.instagram.com/foxtaleskin?hl=en), [campaign](https://www.facebook.com/impactonnet/videos/foxtales-new-campaign-you-glow-different-celebrates-beauty-thats-real-raw-and-un/1432048585587799)); mCaffeine building a whole vocabulary around coffee ("Naked & Raw", "Addicted to Good", body wash served *in a coffee cup*) ([Comunicaffe](https://comunicaffe.com/mcaffeines-coffee-skincare-and-hair-care-is-a-rage-in-indian-millennials), [Adgully](https://adgully.com/mcaffeine-launches-new-range-of-coffee-body-washes-in-go-to-cups-of-coffee-109487.html)); Minimalist treating "income disparity but knowledge parity" as the voice brief — never talk down ([Blume podcast](https://blume.vc/podcasts/blume-podcast/how-minimalist-won-indias-skincare-market-by-being-transparent-s4e7-destiny-avenged-weekend-ep)). US-centric references, USD, Fahrenheit = fail.

---

## 2. Twenty annotated exemplar lines

*Lines marked **[real]** are verbatim/press-verified; lines marked **[demo]** are written here to the bar and labeled as such.*

**Global**

1. **Nike — "Just Do It."** **[real]** — Imperative compression, zero hedging, product absent. The ancestor of mode `imperative-compression`. Lesson: 3 words can command a category.
2. **Nike — "Don't ask if your dream is crazy. Ask if it's crazy enough."** **[real, brand channel]** — Contradiction structure: repeats the reader's inner question then escalates it. Long hook that works because word 1 is already the pivot.
3. **Apple — "Privacy. That's iPhone."** **[real]** — Noun-stacked poetry line + proof line. Two fragments; the period does the work. Lesson: confidence via compression, not adjectives.
4. **Patagonia — "Don't Buy This Jacket."** **[real, 2011 campaign]** — Contradiction as instruction; only credible because the brand had the receipts. Lesson: a contrarian truth outperforms a comfortable claim *when earned*.
5. **Liquid Death — "Murder Your Thirst."** **[real]** — Committed absurdity; the joke never winks. Lesson for skincare: one weird angle, executed 100%.
6. **Oatly — "It's like milk but made for humans."** **[real, pack copy]** — Deadpan reframe of the category's default. Lesson: define yourself against the boring incumbent in one clause.
7. **Glossier — "skin first. makeup second."** **[real, brand axiom]** — Lowercase peer axiom; a value stated as a ratio. Lesson: eye-level voice turns a slogan into an identity marker.
8. **The Ordinary — "Niacinamide 10% + Zinc 1%."** **[real, product naming as copy]** — The name IS the claim; precision replaces charm. Direct template for Minimalist. Lesson: for informed audiences, numbers are the poetry.
9. **CeraVe — "CeraVe is and always has been developed with dermatologists."** **[real, campaign line defended through the Michael CeraVe conspiracy]** — One claim sentence repeated until it became culture. Lesson: pick the one sentence competitors are stealing from you; make comedy defend it.
10. **CeraVe × Michael Cera — "Let my cream hydrate you."** **[real, Super Bowl spot]** — Absurdist first-person invitation; the *brand* stayed out of the joke's punchline and reclaimed authority after. Lesson: humor may carry the invite; the claim stays clean.
11. **Dove — "Turn your back on the filter."** **[real, #TurnYourBack — Cannes Grand Prix + Gold Creative Effectiveness lineage]** ([Ogilvy awards](https://www.ogilvy.com/ideas/ogilvy-caps-2025-cannes-lions-international-festival-creativity-titanium-for-vaseline-glass)) — Physical action as metaphor; instruction, not sentiment. Dove's Real Beauty system won its third Grand Prix in 2025 ([WPP Media](https://www.wppmedia.com/news/dove-wins-cannes-lions-media-grand-prix)). Lesson: one human insight, held for decades, expressed as something to *do*.
12. **La Roche-Posay — "#DermsAgainstBurns."** **[real, 2024–25 program]** — Authority collectivized into a hashtag: the dermatologists, not the brand, are the subject. Lesson: medical-adjacent brands earn warmth by lending the mic to experts.

**India**

13. **d'you — "One serum. 11 actives. 36 iterations. No fluff."** **[real, About page]** — Counted-noun stacking; the last two words dismiss the entire category's noise. Lesson: enumeration is rhythm; the fragment lands the attitude.
14. **d'you — "If we can't explain it, we don't deserve to sell it."** **[real, founder Shamika Haldipurkar]** — Conditional moral contract; "we" appears only to accept obligation. Lesson: this is the one legitimate use of brand-"we" — taking responsibility, not announcing excitement.
15. **Minimalist — "#HideNothing."** **[real, brand motto]** ([Elle India](https://elle.in/elle-carnival-partner-minimalist/)) — Three syllables carrying the whole transparency position; doubles as product truth (published concentrations) and community challenge. Lesson: a motto that is also an operating procedure.
16. **Minimalist — "Salicylic Acid 2%."** **[real, product-name convention]** — Ingredient-first naming imported from The Ordinary and localized. Lesson: when your audience reads INCI lists for fun, the label is the hook.
17. **mCaffeine — "Naked & Raw."** **[real, flagship range name]** — Sensory double-meaning (unretouched ingredients / skin) plus "Addicted to Good" as the habit loop. Lesson: build a small owned vocabulary and reuse it relentlessly across SKUs.
18. **Foxtale — "You Glow Different."** **[real, 2025–26 campaign title]** ([Impact on Net](https://www.facebook.com/impactonnet/videos/foxtales-new-campaign-you-glow-different-celebrates-beauty-thats-real-raw-and-un/1432048585587799)) — Second-person comparative with no object ("different *from what?*" is the curiosity gap); slang-native grammar signals insider status. Lesson: break grammar deliberately, once, in the campaign spine.

**Demo lines (house style, written to the bar)**

19. **"Wash your face tonight. Even tired. Especially tired."** **[demo, imperative-compression mode]** — Command + concessive echo; anticipates the excuse and deletes it in four words.
20. **"i used to sleep in makeup. then i met a mirror at 9 am."** **[demo, peer-voice-intimate mode]** — First-person confession (per B2 evidence), lowercase intimacy, consequence implied not preached. Companion demo for `describe-dont-promise`: *"a gel-cream that absorbs before your chai cools, matte by morning."*

---

## 3. Failure catalog — 15 anti-patterns

Each: the pattern → why it fails (evidence where numeric).

| # | Anti-pattern | Example smell | Why it fails |
|---|---|---|---|
| F1 | Brand-name opener | "Introducing HydroGlow…" | Zero curiosity, zero tension; banned opener in current rubric; wastes the only line guaranteed to be seen (125-char fold) |
| F2 | Rhetorical filler question | "Want glowing skin?" | Reads as ad-speak; questions help only when answerable (+37% comments applies to genuine prompts, Metricool) |
| F3 | Adjective-pair fog | "luxurious and nourishing" | No image, no memory; violates B4 |
| F4 | Medical creep | "cures acne permanently" | Regulatory exposure (ASCI/drug-claim boundary) + instant distrust with ingredient-literate buyers (Minimalist/d'you audience) |
| F5 | Urgency theater | "HURRY!!! Only 3 left!!!" | Fake scarcity detected by audience; multiple exclamations correlate with hype-register our rubric fails |
| F6 | Hashtag wall | 12–30 tags stacked | Worst-performing bucket (0.9% ER at 11+, PostQuick); spam-signal reading (gwaa); contradicts 1–3 tag data |
| F7 | Engagement bait | "Comment YES if you agree 👇" | Thin replies, platform-demoted pattern; comment volume without depth ([unlockdm](https://tryunlockdm.com/blog/instagram-comments-vs-likes-2026)) |
| F8 | We-we announce voice | "We're so excited to share…" | "We"-openings negatively associated with success (PLOS One β=−0.15); corporate register, not peer voice |
| F9 | Dead-zone length | 210-char feed caption that trails off | Middle lengths lose to both extremes in two independent panels (PostPlanify valley; iimagined dead zone) |
| F10 | Wall of text | 900 chars, no breaks | Whitespace adds ~+8% (Campground); unreadable pre-fold structure kills the save |
| F11 | Emoji confetti | "✨🌟💖 GLOW 💖🌟✨" | Decoration not meaning; medical-adjacent credibility penalty reported for emoji-heavy text (Moz via getmoji, directional); screen-reader cost |
| F12 | Transformation promise | "Erases dark spots in 7 days" | Before/after guarantee territory; process framing converts better and stays safe (rubric H4) |
| F13 | Imported idiom | "Perfect for your morning commute ☕ (USD $12)" | Breaks B10: wrong currency, wrong climate, wrong rituals; localization is situation not translation |
| F14 | Forced Hinglish | "Your skin will become total glowing-yaar! 😜" | Cringe test fail; code-mixing works only where a real friend would (≤2 words, natural placement) |
| F15 | Clone variants | 3 captions differing by one word | Mode-diversity mandate violated; A/B value collapses when variants aren't structurally different (our modes exist precisely to force real variance) |

---

## 4. How to A/B judge — scorer upgrade proposal (v2)

### 4.1 What stays

Deterministic-only scoring (no LLM in the hot path), 1–5 integer dimensions, verdict tuple `(verdict, average, one_line_fix)`, hard cliché blacklist gate, and the existing five dimensions as a subset. Files affected when implemented: `apps/api/boxes/rubric.py`, `apps/api/tests/test_style_rubric.py` (+ `craft.py` prompt constants). **No code changed in this task.**

### 4.2 New dimensions (5 → 9)

| Dim | Name | Deterministic checks | Anchor evidence |
|---|---|---|---|
| D6 | `claim_safety` | deny-list regexes: `\b(cure|treat|erases?|removes? permanently|guaranteed)\b`, unsourced "dermatologist-approved/approved by doctors", before/after phrasing; allow-list hedges ("visibly", "reduces the look of", "helps") required near outcome words | ASCI norms; rubric.md §D6 promoted to code (currently LLM-only) |
| D7 | `format_fit` | length-band table by declared format/objective (§B6): Reels target ≤50 or 151–400 chars; feed 126–800; carousel up to 2,200; flag dead zones (51–125 on feed; 200–800 on short-form) as score ≤3; require ≥1 line break if len > 300 | PostPlanify; ContentLabs; Campground (+8%) |
| D8 | `hashtag_discipline` | count tags: 1–3 → 5; 4–5 → 4; 6–10 → 2; >10 → 1; identical tag-set repeat across last N posts → −1 (needs history param, optional) | PostQuick buckets; Mosseri cap |
| D9 | `variant_diversity` | scored on the SET: each caption maps 1:1 to a distinct MODES entry; pairwise shared-trigram ratio < 0.4; ≥2 distinct hook types across the set; ≤1 question-hook per set; flag clone-variants (F15) | mode-diverse variants imperative in current pipeline; A/B validity requires structural variance |

Existing dims get sharpened checks:
- `hook_strength`: keep ≤8 words; ADD first-line ≤60 chars; ADD "we"-opener penalty (score cap 2) per PLOS One β=−0.15; keep banned-opener=1, brand-first=2; rhetorical-question hooks capped at 3.
- `specificity`: keep digit/₹/% logic; require anchor within same sentence as the outcome word (regex window), not anywhere in caption.
- `emotional_truth`: keep situation-word hits; add penalty when emotion words appear with zero situation words ("amazing glow" pattern).
- `cta_physics` (folded into brand_fit today, now explicit): pass = exactly one CTA + a reason clause ("because/so that/or X happens") OR one answerable question; fail = stacked CTAs, "comment YES"-style bait tokens, like-begging (asking-for-likes measured −5% in Metricool).
- `rhythm_economy`: keep filler/exclamation logic; add doubled-adjective regex and wall-of-text check (>300 chars, 0 `\n` → cap 3).

### 4.3 Verdict math — raise the pass bar, weight the load-bearing dims

Current: PASS = flat avg ≥ 3.8, min ≥ 3. Proposal:

```
weights = {hook_strength:.22, specificity:.18, rhythm_economy:.13,
           emotional_truth:.11, brand_fit:.10, cta_physics:.09,
           format_fit:.09, hashtag_discipline:.04, claim_safety:.04}
weighted_avg >= 4.2 AND no dimension <= 2  -> PASS (publishable)
weighted_avg >= 3.8 AND no dimension <= 2  -> PASS_DRAFT (internal ok, not go-live)
else                                        -> REWRITE (fix string for worst dim)
claim_safety == 1                            -> hard FAIL regardless (veto)
```

Rationale: hook + specificity = 0.40 of mass because they are the two dims with both causal evidence (PLOS One; Upworthy) and category precedent (Ordinary/Minimalist). Publishing bar rises 3.8 → 4.2 to make the new bar strictly stricter than `docs/style/rubric.md`'s 4.0 LLM bar; draft floor stays 3.8 so pipelines don't thrash.

### 4.4 Calibration protocol (before shipping)

1. **Golden set:** all 20 exemplars in §2 must score weighted_avg ≥ 4.2 with no dim ≤ 2; all 15 failures in §3 must FAIL with the correct worst-dim named (F4/F12 trip the claim_safety veto specifically).
2. **Regression:** existing `test_style_rubric.py` cases updated; expect intentional deltas documented in the PR (e.g., "we"-openers drop from 4→2).
3. **False-positive budget:** run scorer over 200 recent accepted captions; target ≤ 5% newly-failing on rhythm/format dims; tune regex windows before tightening thresholds further.
4. **Live A/B loop (where the data comes back):** publish PASS pairs that differ on ONE structural axis (hook type, question-vs-command, length band); record hook-rate proxy (3-sec views/impressions for Reels) and comment rate per arm; after ~20 paired observations per axis, feed observed lifts back into weights. Treat all platform numbers as correlational until we have our own pairs (Metricool's own caveat).

### 4.5 Known limitations (honesty block)

- Caption-length panels conflict across formats/account sizes; bands encode the *overlap* of findings, not settled science.
- Emoji/medical penalty is a secondary citation (Moz data via getmoji.app) — directional only.
- Hook-rate 30–40% is video-ad lore from media-buying practitioners, not peer-reviewed; used as analogy only.
- Exemplar lines 19–20 are ours, not brand quotes; they demonstrate modes, not proven performance.
