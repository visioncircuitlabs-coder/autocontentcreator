# Content Machine — Style Rubric

**Purpose:** Codified voice + quality standard for all social & product marketing copy produced by the Content Machine (demo fixture: unofficial Neutrogena-style skincare brand, India market). Every section is written to be dropped directly into a generator prompt or applied by an LLM judge.

**Sources of truth:** Observed copy from Nike, Apple, Aesop, Dove, Glossier, The Ordinary, Drunk Elephant, Liquid Death, Oatly, Patagonia — Instagram captions, product pages, campaign lines — plus Indian D2C skincare conventions (Nykaa-era brands: Minimalist, Plum, mCaffeine).

---

## 1. Observed Patterns per Brand

### Nike — imperative compression
- Pattern: 2–6 word commands. No product features in the line; the feature is the *feeling*.
- "Just Do It." / "You can't stop sport." / "Don't ask if your dream is crazy. Ask if it's crazy enough."
- Lesson: **verb-first, second person, zero hedging.** The product appears late or not at all.

### Apple — noun-stacking + confident minimalism
- Pattern: short declaratives with a single concrete noun doing the work. "Privacy. That's iPhone." / "Blast past fast." / "Pro. Beyond."
- Product pages pair one poetic line with one spec sentence ("A16 Bionic. 20 billion transistors.")
- Lesson: **poetry line + proof line.** Never two adjectives where one noun works.

### Aesop — literary restraint
- Pattern: full sentences, no exclamation, no emoji, sensory-but-precise language ("a hydrating gel-cream with a matte finish, redolent of citrus rind").
- Never claims transformation; describes texture, ritual, and formulation rationale.
- Lesson: **describe, don't promise.** Confidence via specificity, not superlatives.

### Dove — emotional realism, campaign architecture
- "Real Beauty" / #ShowUs / "Turn your back on the filter."
- Pattern: a single human insight stated plainly, then held for years across formats.
- Lesson: **one insight, many executions.** The insight must be true before it is clever.

### Glossier — peer voice, lowercase intimacy
- Pattern: captions read like texts from a friend. "skin first. makeup second." Questions to the audience ("what's your skin freak-out?"). Heavy comment-section engagement as copy strategy.
- Lesson: **write at eye level, not from a podium.** Sentence fragments are allowed; brand-speak is not.

### The Ordinary — radical transparency as voice
- Product names ARE the ingredient deck ("Niacinamide 10% + Zinc 1%"). Copy states concentration, pH, and what it does — nothing else.
- Lesson: **when the audience is informed, precision beats charm.** Numbers are copy.

### Drunk Elephant — playful expertise
- Quirky names (Protini, T.L.C. Framboos) backed by serious biocompatibility logic; conversational founder voice on social; education-first posts.
- Lesson: **personality on the surface, science underneath.** Playfulness never cancels the claim discipline.

### Liquid Death — committed absurdity
- "Murder Your Thirst." Water sold with metal aesthetics. The joke is total; there is no winking.
- Lesson: **if you commit to an unusual angle, commit 100%.** Half-committed quirk reads as corporate cosplay.

### Oatly — deadpan self-awareness
- "It's like milk but made for humans." Packaging copy about the packaging copy. Anti-marketing marketing ("ANOTHER AD FOR OUR OAT DRINK PROVIDING NO REASON AT ALL WHY YOU SHOULD TRY IT").
- Lesson: **voice consistency beats channel optimization** — even word-count-restricted retail fields stay in voice.

### Patagonia — values as copy
- "Don't Buy This Jacket." Activism stated as instruction, not sentiment.
- Lesson: **a contrarian truth outperforms a comfortable claim** when the brand has earned it.

---

## 2. Universal Dimensions

These apply to every piece of copy the Machine generates.

### 2.1 Hook construction
- First 5–8 words carry the entire scroll-stop burden. Hooks that work across the studied brands:
  1. **Command** (Nike): verb + object, no preamble.
  2. **Contradiction** (Patagonia/Oatly): state something that shouldn't be said by this brand.
  3. **Confession** (Glossier/UGC India): an admission the reader makes privately.
  4. **Specific number** (The Ordinary): "10% niacinamide. Not 5. Not 'a blend'."
  5. **Question with stakes**: only if genuinely answerable, not rhetorical filler.
- Banned hooks: "Introducing…", "Say hello to…", "We're excited to announce", any hook starting with the brand name.

### 2.2 Sentence rhythm
- Vary length deliberately: a long sentence earns the right to be followed by a very short one.
- Read-aloud test: if you can't say it in one breath, split it.
- One idea per sentence. Fragments allowed in social copy, sparingly in product pages.

### 2.3 Restraint / economy
- Cut every word that survives only out of politeness ("very", "really", "actually", "simply", "just").
- No double adjectives ("luxurious and nourishing") — pick one or replace both with a concrete image.
- Exclamation marks: maximum one per caption, zero preferred. Zero on product pages.

### 2.4 Specificity vs abstraction
- Concrete > abstract, always: "niacinamide 10%" not "powerful blend"; "SPF 50, no white cast" not "superior protection".
- Every benefit claim needs a mechanism or a number within one sentence of it.
- Banned abstractions: "revolutionary", "game-changing", "magical", "the perfect …".

### 2.5 Emotional register
- Warm, assured, peer-level. Never preachy, never giddy, never clinical-cold.
- Emotion comes from a recognized situation ("3 PM meeting, forehead shining on the webcam"), not from adjective stacking ("amazing glow!").
- Humor allowed only where the fixture brand's persona supports it; deadpan over zany.

### 2.6 CTA handling
- One CTA per piece. Soft CTAs in social ("Link in bio", "Save this for your next shelf check"), direct CTAs on PDP/ads ("Shop 30 ml — ₹499").
- CTAs state the action AND the reason when possible: "Try it for 4 weeks — retinol results show by week 8."
- Never stack CTAs. Never use urgency theater ("HURRY!! Only a few left!") unless factually true.

### 2.7 Emoji & hashtag policy
- Emoji: 0–2 per Instagram caption, chosen for meaning not decoration. Zero on product pages, emails subject lines optional (max 1).
- Hashtags: 0–3 relevant tags max (#SkincareIndia, #SPFEveryday). No hashtag walls. No trending-tag hijacking.
- All-caps: reserved for single words of emphasis, max once per piece.

---

## 3. Scoring Rubric (for LLM judge)

Score each dimension 1–5. Pass bar for published copy: **average ≥ 4.0, no dimension = 1–2.**

### D1 — Hook strength
| Score | Anchor |
|---|---|
| 1 | Starts with brand name or "Introducing"; generic greeting |
| 3 | Clear but predictable ("Tired of dull skin?") |
| 5 | Scroll-stopping in ≤8 words via command/contradiction/confession/specific number; no banned openers |

### D2 — Specificity
| Score | Anchor |
|---|---|
| 1 | All abstract claims ("amazing results", "advanced formula") |
| 3 | At least one concrete detail; rest vague |
| 5 | Every claim carries a number, ingredient+concentration, timeframe, or sensory detail |

### D3 — Economy & rhythm
| Score | Anchor |
|---|---|
| 1 | Filler words, doubled adjectives, multiple exclamations |
| 3 | Mostly tight; 1–2 flabby sentences |
| 5 | Every word load-bearing; varied rhythm; passes read-aloud test; ≤1 exclamation |

### D4 — Emotional register / voice fit
| Score | Anchor |
|---|---|
| 1 | Corporate-speak, hype-y, or preachy |
| 3 | Pleasant but interchangeable with any brand |
| 5 | Warm, peer-level, distinctly the fixture brand's voice; emotion rooted in a recognizable situation |

### D5 — CTA quality
| Score | Anchor |
|---|---|
| 1 | Missing, stacked, or urgency-theater |
| 3 | Single clear CTA |
| 5 | Single CTA with action + reason; matches channel convention (soft social / direct PDP) |

### D6 — Claim safety (skincare-specific)
| Score | Anchor |
|---|---|
| 1 | Medical promises ("cures acne", "removes scars permanently"), before/after guarantees |
| 3 | Hedged but sloppy ("erases wrinkles") |
| 5 | Cosmetic-zone language only: "reduces the look of", "helps with", "visibly", consistent with ASCI norms; disclaimers where required |

### D7 — Localization fit (India)
| Score | Anchor |
|---|---|
| 1 | US-centric references, USD, Fahrenheit, foreign idioms |
| 3 | Neutral but flavorless |
| 5 | INR pricing, Indian context (humidity, pollution, sun intensity, festival moments), natural Hinglish-light where fitting (see §5) |

Judge output format:
```json
{"D1": n, "D2": n, ..., "D7": n, "avg": x.x, "pass": bool,
 "worst_dimension": "D#", "one_line_fix": "..."}
```

---

## 4. Rewrite Heuristics (before → after)

**H1 — Kill the abstraction, keep the mechanism.**
- ❌ "Experience revolutionary hydration with our advanced formula."
- ✅ "Hyaluronic acid holds 1,000× its weight in water. Your skin notices by day 3."

**H2 — Move the brand name out of the first line.**
- ❌ "NeutroGlow is here! Say hello to radiant skin."
- ✅ "Dull skin isn't a personality. 10% vitamin C, ₹699, done."

**H3 — Trade adjective pairs for one concrete image.**
- ❌ "Luxurious, silky-smooth texture."
- ✅ "Absorbs before your chai cools."

**H4 — Convert promises into processes.**
- ❌ "Erases dark spots."
- ✅ "Dark spots fade when cell turnover speeds up. That's what 2% retinal does — visibly, in 8 weeks."

**H5 — Put the price objection in the copy yourself.**
- ❌ (no price mention)
- ✅ "₹499. Compare it to the ₹2,000 serum doing nothing on your shelf."

**H6 — Replace rhetorical questions with commands or confessions.**
- ❌ "Want glowing skin?"
- ✅ "Wash your face tonight. Even tired. Especially tired." (command)
- ✅ "I used to sleep in makeup. Then I met a mirror at 9 AM." (confession)

**H7 — Localize the moment, not just the words.**
- ❌ "Perfect for your morning commute with coffee."
- ✅ "Mumbai humidity vs. your T-zone. SPF 50 wins. No white cast, no excuses."

**H8 — One CTA, with a reason.**
- ❌ "Shop now!!! Link in bio! Follow us!"
- ✅ "Start with the cleanser. Link in bio — everything else can wait."

---

## 5. Skincare Voice Guidance — Indian Audience

**Market facts to respect:** Asia/Kolkata time framing; INR pricing always (₹ symbol, comma format: ₹1,299); climate context (heat, humidity, monsoon, hard water, pollution); sun intensity year-round (SPF is not seasonal here); Tier-1 + Tier-2 audiences; price-vs-trust is the #1 objection; ASCI guidelines restrict before/after imagery and medical claims.

**Voice stance:** a knowledgeable friend who happens to know skincare — not a dermatologist lecturing, not an influencer gushing. Confident, warm, lightly funny, scientifically literate.

**Hinglish-light policy:**
- Use natural code-mixed phrases where a real friend would: "yaar", "bas", "thoda", "na" as tag, "seriously", "bilkul" sparingly. Max 1–2 Hinglish words per caption.
- Never force it, never transliterate whole sentences, never use it in product pages or claim copy — social captions and Reels hooks only.
- Test: would a 25-year-old in Pune text this to a friend without cringing?

**Situations to mine for hooks:** webcam-shine at 3 PM; monsoon frizz/fungal-acne season; Diwali/festival late nights → dull skin; metro commute pollution; gym-after-office skincare; "shaadi season" prep timelines; hard-water hair/skin complaints; hostel/tier-2 budget constraints.

**Claim discipline (non-negotiable):**
- "Reduces the appearance of…" / "visibly brighter in X weeks" / "helps manage" — yes.
- "Cures", "treats", "removes permanently", "dermatologist-approved" (unless sourced), before/after imagery — no.
- Patch-test note on actives (retinol/AHA/BHA/vitamin C): include once per educational post.

**Format conventions:**
- Prices: ₹499 / ₹1,299. Timeframes: "weeks, not days". Sizes: ml/g metric.
- Instagram caption skeleton: hook (≤8 words) → mechanism or story (1–3 lines) → proof point (number/ingredient) → single soft CTA → 0–3 hashtags.
- Product page skeleton: poetic one-liner → what it is (ingredient + %) → what it does (mechanism + timeframe) → how to use → what it pairs with / avoid.

---

## Appendix — Quick Generator Prompt Block

> Write in the voice of a knowledgeable, warm friend who knows skincare science. Hook in ≤8 words using command/contradiction/confession/specific-number — never the brand name, never "introducing". Every claim carries a number, ingredient+concentration, or timeframe. Concrete images over adjectives. INR pricing, Indian context (humidity, pollution, sun, festivals), natural Hinglish-light (max 1–2 words) in social only. Cosmetic-safe claims only ("reduces the look of", "visibly"). One CTA with a reason. 0–2 emoji, 0–3 hashtags, ≤1 exclamation. Then score yourself against rubric dimensions D1–D7; revise until avg ≥ 4.0.
