# Compliance Bar — Regulated Branded Content (Skincare)

**Project:** Content Machine · `feat-foolproof-design`
**Purpose:** Define the regulatory bar the generation pipeline must meet for branded skincare
content, and enumerate gaps between that bar and the current system design.
**Scope:** Paid/branded promotional content (brand posts, influencer-style copy) for topical
skincare/cosmetics. Markets: **IN**, **US**, **EU**. This doc is research output, not legal advice;
final launch copy sign-off belongs to qualified counsel per target market.
**Compiled:** 2026-08-24. Sources verified via live web search (register in §7).

---

## 1. Claims taxonomy

Every generated sentence that asserts anything about product effect falls in exactly one tier.
Tier drives the compliance gate (§6 gap G1–G2).

| Tier | Name | Definition | Burden of proof | Gate |
|---|---|---|---|---|
| **T0** | **Puffery / hyperbole** | Subjective, non-measurable praise an average consumer would not take literally. No substantiation required. | None (but must stay non-literal). | Allow-list pass only |
| **T1** | **Structure-function / cosmetic performance** | Measurable cosmetic effect on appearance/skin surface, or ingredient→product extrapolation. Includes "derm-tested/-approved" style authority claims. | Adequate, verifiable evidence held **before** publication (EU "evidential support"; US "adequate substantiation"; IN substantiation on demand). | Registry entry + evidence link + human approval |
| **T2** | **Drug-class / therapeutic** | Treats, cures, prevents, mitigates disease/medical condition, or alters body structure/physiology beyond cosmetics. | Effectively prohibited in cosmetic copy; requires drug registration pathway. | **Block** |

### Tier definitions with skincare examples

- **T0 puffery:** "glow like never before", "pure luxury", "the most refreshing ritual",
  "feels weightless". Test: could anyone measure it or sue over its falsity? If yes → not puffery.
  EU: hyperbole not taken literally is exempt from substantiation ([Reg 655/2013, recital 8](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32013R0655)).
- **T1 structure-function (cosmetic):**
  - Performance: "reduces the *appearance* of fine lines in 4 weeks", "24h hydration",
    "improves skin texture". Must be qualified to what evidence showed (appearance vs structure;
    duration; population).
  - Authority/endorsement: "dermatologically tested", "derm-approved", "#1 dermatologist
    recommended" — each implies a third-party endorsement that must actually exist and be
    represented honestly ([EU Technical Document on Cosmetic Claims](https://webgate.ec.europa.eu/circabc-ewpp/rest/download/83d29cfc-b5c8-4496-bee3-2e25f08e2e73)).
  - Ingredient extrapolation: "with retinol → regenerates skin" requires evidence the finished
    product carries the ingredient at an effective concentration (Reg 655/2013 art. 2(6)).
- **T2 drug-class (block in cosmetic copy):**
  - "cures acne / heals eczema / treats rosacea" (disease claims);
  - "boosts collagen production", "repairs skin barrier at the cellular level"
    (physiological structure/function claims);
  - "guaranteed results", "permanently removes dark spots" (absolute therapeutic outcome).
  - US: such claims convert a cosmetic into an unapproved new drug ([FDA: Cosmetic or Drug?](https://www.fda.gov/cosmetics/cosmetics-labeling-claims/it-cosmetic-drug-or-both)).
  - IN: external-use preparations claiming cure/mitigation of scheduled conditions fall within
    DMRA 1954 advertising prohibitions ([Act text](https://indiankanoon.org/doc/1929849/)).
  - EU: falsely claiming a product cures illness/dysfunction/malformation is banned in **all**
    circumstances ([UCPD 2005/29/EC Annex I ¶17](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32005L0029)).

**Superlative/comparative note ("best", "only", "#1"):** straddles T0–T1. Subjective framing
("our richest cream") ≈ puffery; objective-superiority framing ("best moisturizer for dry skin",
"the only serum with X") is a comparative claim needing verifiable substantiation and is treated
as **T1 minimum** everywhere (see IN-5, US-4, EU-4).

---

## 2. Jurisdiction checklists — testable rules

Each item is written so a reviewer (human or script) can answer PASS/FAIL. A generated post must
pass every applicable row for its markets before publish.

### 2.1 India (IN)

- [ ] **IN-1 Material-connection disclosure.** Any post about an advertiser's product where any
  value passed hands (payment, free product, discount, trip, barter, family/employment tie) MUST
  carry a disclosure label. PASS iff label present even though evaluation is otherwise honest.
  [ASCI Influencer Guidelines](https://ascionline.in/social/wp-content/uploads/2025/04/ASCI-Influencer-Guidelines.pdf)
- [ ] **IN-2 Approved labels only.** Label ∈ {Advertisement, Ad, Sponsored, Collaboration/
  Collab, Partnership, Affiliate, Free Gift, Paid Promotion} (or "XYZ Ambassador" on
  character-limited platforms). PASS iff exact approved term appears.
- [ ] **IN-3 Upfront placement.** Label MUST appear within the first two lines of the caption,
  before any "more" fold; never buried inside a hashtag cluster. PASS iff label precedes the fold
  and stands outside hashtag runs.
  ([ASCI guidelines](https://ascionline.in/social/wp-content/uploads/2025/04/ASCI-Influencer-Guidelines.pdf); [DCA "Know-Hows" analysis](https://mondaq.com/india/advertising-marketing--branding/1283848/endorsement-know-hows-a-guide-to-advertising-disclosures-by-celebrities-and-influencers))
- [ ] **IN-4 Platform tool additive.** Instagram "Paid partnership"/YouTube toggle is used **in
  addition to** the text label, never instead. PASS iff both exist.
- [ ] **IN-5 Substantiation before publish.** No exaggerated or unverifiable superiority claim;
  advertiser must be able to substantiate every performance claim on demand; endorser due
  diligence expected (and product actually used by the endorsing human).
  [ASCI Code/Guidelines](https://ascionline.in/social/wp-content/uploads/2025/04/ASCI-Influencer-Guidelines.pdf); [Know-Hows](https://mondaq.com/india/advertising-marketing--branding/1283848/endorsement-know-hows-a-guide-to-advertising-disclosures-by-celebrities-and-influencers)
- [ ] **IN-6 DMRA screen (T2 kill-switch).** Copy MUST NOT suggest the product diagnoses, cures,
  mitigates, treats, or prevents any condition in the DMRA Schedule (54 entries incl. leucoderma),
  nor miscarriage/conception, sexual-capacity, or menstrual-disorder uses; no "magic remedy"
  framing (miraculous-power language). Violation is a cognizable offence (§7: up to 6 months'
  imprisonment first offence; up to 1 year subsequent).
  [DMRA 1954 text §§2–5,7](https://indiankanoon.org/doc/1929849/)
- [ ] **IN-7 Fair-skin/beauty-equity guardrail.** Skin-tone alteration promises ("fairness",
  "whitening") attract ASCI action and regulator scrutiny; treat as blocked vocabulary absent
  explicit legal sign-off. [ASCI monitoring practice](https://journalism.university/persuasive-communication/ethical-issues-influencer-marketing)

### 2.2 United States (US)

- [ ] **US-1 Substantiation in hand, pre-publication.** Every express AND implied efficacy claim
  must be supported **before** dissemination — retroactive search for evidence is non-compliance.
  [Health Products Compliance Guidance](https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance)
- [ ] **US-2 Competent & reliable scientific evidence for health-related claims.** For any claim
  of skin-health benefit: randomized, controlled human clinical testing; control group +
  randomization + blinding; statistically significant AND clinically meaningful results; animal/
  in-vitro/consumer-survey evidence alone insufficient. PASS iff evidence file meets these
  attributes for the specific claim made.
  [HPCG](https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance); [16 CFR 255](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255)
- [ ] **US-3 Testimonials = advertiser claims.** An endorser's personal-result story carries the
  advertiser's substantiation burden. "Results not typical" disclaimers do NOT cure an
  atypical-results testimonial; the normally-expected result must be disclosed clearly and
  conspicuously instead. PASS iff any quoted user story reflects achievable results or the
  expected result is disclosed with equal prominence.
  [Endorsement Guides 2023 revision](https://www.ftc.gov/news-events/news/press-releases/2023/06/federal-trade-commission-announces-updated-advertising-guides-combat-deceptive-reviews-endorsements)
- [ ] **US-4 Superlative/comparative claims substantiated.** "Best", "only", "#1", clinical-grade
  comparisons PASS only with a verifiable, current basis for the comparison universe claimed.
  [FTC deception standard, HPCG](https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance)
- [ ] **US-5 Material-connection disclosure, clear & conspicuous.** Any payment/free-product/
  relationship tie between brand and speaker must be disclosed so it is "difficult to miss":
  unavoidable, in the same medium (video ⇒ audio AND visual), proximate to the endorsement, not
  buried below the fold or behind a link. Platform built-in tools alone are insufficient.
  [16 CFR 255.1/255.5](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255)
- [ ] **US-6 Cosmetic/drug boundary respected.** Copy must not represent the product treating,
  curing, preventing disease or altering skin structure/physiology (intended-use is judged from
  marketing language, not just the label). PASS iff zero T2 verbs/phrases survive the gate.
  [FDA: Is It a Cosmetic, a Drug, or Both?](https://www.fda.gov/cosmetics/cosmetics-labeling-claims/it-cosmetic-drug-or-both)

### 2.3 European Union (EU)

- [ ] **EU-1 Six common criteria screen.** Every cosmetic claim satisfies: legal compliance,
  truthfulness, evidential support, honesty, fairness, informed decision-making. FAIL on any
  criterion ⇒ claim withdrawn.
  [Reg (EU) 655/2013](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32013R0655)
- [ ] **EU-2 Evidence held by Responsible Person.** Adequate and verifiable evidence for each
  claim (studies meeting accepted protocols; surveys only with defined methodology) must be kept
  available for market surveillance — including the Product Information File where the claim
  bears on the safety report's "proof of effect claimed".
  [Reg 655/2013 art. 2(3)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32013R0655); [Reg (EC) 1223/2009 arts. 11/19](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32009R1223)
- [ ] **EU-3 Honesty on extrapolation.** Ingredient-property claims may not imply finished-
  product efficacy unless presence at effective concentration is demonstrated; "free from"
  claims only where the substance is legally excluded and the absence is meaningful.
  [Reg 655/2013 art. 2(6)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32013R0655); [EC Technical Document](https://webgate.ec.europa.eu/circabc-ewpp/rest/download/83d29cfc-b5c8-4496-bee3-2e25f08e2e73)
- [ ] **EU-4 Fairness toward competitors.** No denigration of competitor products/ingredients
  (e.g., "cleaner than conventional retinol"), no exploiting category fear.
  [Reg 655/2013 criterion 5](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32013R0655)
- [ ] **EU-5 Cure-claims absolute ban.** Never claim the product cures illness, dysfunction or
  malformations (misleading action banned in all circumstances, no defence of substantiation).
  [UCPD Annex I ¶17](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32005L0029)
- [ ] **EU-6 Commercial-content identifiability.** Paid promotion presented through editorial-
  style content MUST be clearly identified as commercial in the content itself (visible marker;
  member-state codes add local labels e.g. DE "Anzeige/Werbung", FR "Publicité").
  [UCPD Annex I ¶11](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32005L0029)
- [ ] **EU-7 Authority claims evidenced.** "Dermatologically tested/approved", "clinically
  proven", "hypoallergenic": PASS iff the named testing/authority relationship actually occurred,
  with adequate evidence retained (test type, population, protocol).
  [EC Technical Document on Cosmetic Claims](https://webgate.ec.europa.eu/circabc-ewpp/rest/download/83d29cfc-b5c8-4496-bee3-2e25f08e2e73)

---

## 3. Mandatory disclosure formats per jurisdiction

| Aspect | 🇮🇳 India (ASCI/DCA) | 🇺🇸 United States (FTC 16 CFR 255) | 🇪🇺 European Union (UCPD) |
|---|---|---|---|
| Legal force | Self-regulatory + DCA Know-Hows (binding on endorsers) | Guides construing §5 FTC Act; enforced | Statute (max-harmonised UCPD + national law) |
| Required label | `Ad` / `Advertisement` / `Sponsored` / `Collab` / `Partnership` / `Affiliate` / `Free Gift` / `Paid Promotion` | Any unambiguous disclosure: `#ad`, `Sponsored`, "I get paid by X" — endorser's voice ok; ambiguity fails | Clear, visible commercial identifier (`#ad`, `Werbung`, `Publicité`, platform tag) |
| Placement | First two lines of caption, outside hashtag block, before fold | Unavoidable: proximate to endorsement, same scroll depth, not behind "more" | In the content itself, plainly visible |
| Video | ≤15s: label ≥3s on screen · ≤2min: ≥1/3 runtime · >2min: whole segment mentioning brand · live: announced start AND end | Disclosed in **both audio and video track**; spoken-only or overlay-only fails | Visual marker sufficient if unmistakable; audio acceptable complement |
| Language | Same language as the post/content | Understandable to ordinary English audience | Language of the member-state audience |
| Platform tools | Additional only (never substitute) | Additional only | Acceptable only if equally clear |
| Non-disclosure trigger | No material connection ⇒ no label needed | Same | Same |

Sources: [ASCI Influencer Guidelines PDF](https://ascionline.in/social/wp-content/uploads/2025/04/ASCI-Influencer-Guidelines.pdf) ·
[ASCI Guide for Influencers (timing/ready reckoner summaries)](https://journalism.university/persuasive-communication/ethical-issues-influencer-marketing) ·
[16 CFR Part 255 (2023)](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) ·
[UCPD Annex I ¶11](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32005L0029)

---

## 4. Record retention & audit trail

- **Substantiation must pre-date the claim.** US: evidence in hand before dissemination
  ([HPCG](https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance));
  EU: evidence held and producible for surveillance authorities
  ([Reg 655/2013](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32013R0655)).
- **Retention period: no single statutory figure spans our markets.** ⚠️ *ANALOGY, not law:* ISO
  9001:2015 clause 7.5 treats claim-support records as controlled documented information — unique
  ID, version, approver, protection from unauthorized change, defined retention, controlled
  disposition; the standard leaves the length to the organization based on legal exposure, with
  ≥3 years common practice and 6 years matching contract limitation norms (UK Limitation Act
  analogy). Recommendation: **retain claim evidence + approval records ≥ 6 years**, configurable.
  [ISO 9001 cl. 7.5 explainer](https://isomanaged.com/knowledge-base/iso-standards/iso-9001/iso-9001-clause-7-5-documented-information) (marked analogy);
  [document-control practice](https://clausewise.co.uk/blog/iso-9001-document-control/)
- **What an evidence pack must reconstruct:** the exact published text, every claim's registry
  entry + source URL, tier classification, approver identity + reason + timestamp, disclosures
  applied, and generator/prompt provenance.

---

## 5. GAP LIST — Content Machine vs compliance bar

Priority key: **MUST** = ship-blocker (regulatory exposure if absent) · **SHOULD** = strong
defensive control · **NICE** = quality/hardening.

| # | Mechanism (proposed) | Compliance driver | Priority | Notes / acceptance test |
|---|---|---|---|---|
| G1 | **Claims registry** — every non-T0 claim has `source_url`, `status`, `review_by`; enforced **pre-LLM** (generator refuses unregistered claims) | US-1/US-2 (substantiation in hand); EU-1/EU-2 (evidential support, RP-held); IN-5 | **MUST** | Hard-fail build if any T1 sentence lacks a registry id whose `status=approved`. Registry lookup happens before prompt assembly, not after generation. |
| G2 | Registry schema extension: `tier` (T0/T1), `jurisdictions[]`, `review_due` expiry | §1 taxonomy; EU-1 criteria re-review; ISO-analogy review dates | **SHOULD** | Without tier, T0 allow-list can't be distinguished from T1 gate; expired reviews auto-demote claim to blocked. |
| G3 | **Banned-token gate** — `cures`, `heals`, `best`, `only`, `guaranteed` (+ `treats`, `prevents`, `reverses`, `clinically proven` unbacked, fairness/whitening terms) | IN-6/IN-7 (DMRA, equity); US-6 (drug boundary); US-4; EU-5 | **MUST** (for T2 verbs: cures/heals/treats/prevents/guarantees) / **SHOULD** (superlatives) | Tokens are a floor, not the wall: "best-smelling" is legal puffery, "cures" never is. Split list: absolute T2 verbs = unconditional reject; superlatives = reject unless registry entry backs the comparison. Add LLM-based implied-claim classifier as backstop — paraphrases ("erases eczema overnight") dodge token lists. |
| G4 | **Disclaimer injection on benefit lines** | US-3 (qualifications); EU-1 (informed decision-making) | **SHOULD**, with hard constraint | Constraint: a disclaimer may narrow a truthful T1 claim; it may NEVER launder an unsupported claim ("results not typical" is expressly rejected by FTC 2023 Guides). Disclaimers render in the same medium/placement rules as §3. |
| G5 | **Named-human approval + recorded reason** before publish | ISO-analogy approval trail (cl. 7.5); IN-5 endorser due diligence; EU-2 accountability | **MUST** for T1+ and any IN-market post · **NICE** for pure-T0 | Approval object: `{approver_id, role, reason, claim_ids[], content_hash, ts}`. Anonymous/service accounts don't satisfy "named human". |
| G6 | **audit.json + rendered audit.html shipped in ZIP** | §4 retention/audit-trail reconstruction; EU-2 producible-to-regulator | **MUST** | audit.json: content hash, claim ids, source_urls, approvals, disclosures applied, model/prompt ids, timestamps. HTML = human-readable rendering for counsel/regulator hand-off. Verify: unzip artifact offline ⇒ full §4 reconstruction possible. |
| G7 | Jurisdiction-aware disclosure formatter (caption header, video-duration rules per §3) | IN-1..IN-4; US-5; EU-6 | **SHOULD** | **Status 2026-08-24: landed for static captions** — `boxes/disclosure.py`: approved-label vocabulary (IN/US/EU incl. Werbung/Publicité), placement check (first two lines, hashtag-bury detection), deterministic `ensure_disclosure` injection; wired into `run_hard_rules(organic=False)` and the loop's paid path. Video-duration timing rules remain open (demo produces captions only). |
| G8 | Market routing gate (post blocked in market J if any checklist row for J fails) | All of §2 | **SHOULD** | One content unit may be EU-clean yet IN-failing (e.g., comparative claims); distribution metadata must respect per-market verdicts. |
| G9 | Token-gate bypass attempts logged to audit trail | §4 evidence of control (analogy) | **NICE** | Rejected generations with matched tokens become training/audit signal; proves gate exercised. |

**Minimum shippable bar:** G1 + G3(T2 half) + G5 + G6. Everything else can land iteratively, but
G1 without pre-LLM enforcement is decorative — the gate must sit between registry and prompt.

---

## 6. Checklist coverage map (rule → gap)

| Checklist area | Covered by |
|---|---|
| IN-1…IN-4 disclosures | G7, G8 |
| IN-5 substantiation/due diligence | G1, G5 |
| IN-6/IN-7 DMRA + equity guardrails | G3 |
| US-1/US-2 substantiation | G1, G6 |
| US-3 testimonials/results | G3, G4 |
| US-4 superlatives | G3 (SHOULD arm) |
| US-5 disclosure | G7 |
| US-6/EU-5 drug boundary | G3 (MUST arm) |
| EU-1…EU-4, EU-7 criteria/evidence | G1, G2 |
| EU-6 identifiability | G7 |
| Retention (§4) | G6 |

---

## 7. Source register

1. ASCI, *Guidelines for Influencer Advertising in Digital Media* (consolidated 2025 ed.):
   <https://ascionline.in/social/wp-content/uploads/2025/04/ASCI-Influencer-Guidelines.pdf>
2. Mondaq/Obhan & Associates, *Endorsement Know-Hows* (DCA binding guidance analysis):
   <https://mondaq.com/india/advertising-marketing--branding/1283848/endorsement-know-hows-a-guide-to-advertising-disclosures-by-celebrities-and-influencers>
3. Drugs and Magic Remedies (Objectionable Advertisements) Act 1954, full text (Indian Kanoon):
   <https://indiankanoon.org/doc/1929849/>
4. Journalism Univ., ASCI guideline timing-rules summary (video/live-stream disclosure):
   <https://journalism.university/persuasive-communication/ethical-issues-influencer-marketing>
5. FTC, *Health Products Compliance Guidance* (Dec 2022; substantiation standard):
   <https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance>
6. FTC press release, updated Endorsement Guides (Jun 2023):
   <https://www.ftc.gov/news-events/news/press-releases/2023/06/federal-trade-commission-announces-updated-advertising-guides-combat-deceptive-reviews-endorsements>
7. 16 CFR Part 255, *Guides Concerning the Use of Endorsements and Testimonials in Advertising*:
   <https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255>
8. Cooley LLP, *FTC Revises Health Products Compliance Guidance* (analysis):
   <https://www.cooley.com/news/insight/2023/2023-03-02-ftc-revises-health-products-compliance-guidance>
9. Regulation (EU) No 655/2013, common criteria for cosmetic claims (EUR-Lex):
   <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32013R0655>
10. Directive 2005/29/EC (UCPD), incl. Annex I ¶11 & ¶17 (EUR-Lex):
    <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32005L0029>
11. European Commission, *Technical Document on Cosmetic Claims* (derm-claims, free-from,
    hypoallergenic annexes): <https://webgate.ec.europa.eu/circabc-ewpp/rest/download/83d29cfc-b5c8-4496-bee3-2e25f08e2e73>
12. Regulation (EC) No 1223/2009 (Cosmetics Regulation; PIF/RP duties) (EUR-Lex):
    <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32009R1223>
13. FDA, *Is It a Cosmetic, a Drug, or Both?* (intended-use boundary):
    <https://www.fda.gov/cosmetics/cosmetics-labeling-claims/it-cosmetic-drug-or-both>
14. ISO 9001:2015 cl. 7.5 documented-information controls (retention analogy — marked as such):
    <https://isomanaged.com/knowledge-base/iso-standards/iso-9001/iso-9001-clause-7-5-documented-information>;
    <https://clausewise.co.uk/blog/iso-9001-document-control/>

*Research limitations noted: two web-search backend failures occurred during compilation; all
statutory points above rest on retrieved primary/secondary sources listed here. Items marked
⚠️ ANALOGY are engineering conventions, not legal requirements.*
