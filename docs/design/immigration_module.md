# Immigration module — new-entrant cohorts through the scheduled-entry seam

- **Design id**: `2026-07-15-immigration-module`
- **Roadmap**: [#113](https://github.com/PolicyEngine/populace-dynamics/issues/113),
  M6 immigration entry cohorts and the versioned Trustees alignment layer.
- **Status**: DESIGN DRAFT (revision 5; refereed O1–O16 folded; build-ready
  pending P1–P4). No immigration surface is certified by this document.
- **Repository pin**: `afd8f44838c71bca1ce558ffcff5e7701b94f791` (`origin/master`,
  2026-09-06). Every `path:line` in this revision was opened at that tree unless
  it names a different revision. Revision 4's baseline
  `75d30dd57d71b91ee0929246b2f3cbb92263b350` is retained only in the drift table
  at §3.1a; it is no longer the reading tree.
- **Second pinned revision**: `29aa8c6c96a39ecab71af86f01859d53a71f9c0c`
  (`cap/entrant-schedule`, committed and unpushed). Sections §2.2, §4.3, §4.4
  and §5 describe the donor and the schedule **as that branch's code builds
  them**, and every pin into `data/nativity_frame.py`,
  `data/trustees_immigration.py`, `engine/entrant_schedule.py`,
  `engine/entrant_domains.py`, `scripts/build_entrant_schedule_v1.py` and
  `runs/entrant_schedule_v1.json` resolves at `29aa8c6`, not at `afd8f44`. That
  branch is not merged; the design records the code that exists, and P1 below
  names what a merge would still owe.
- **Information boundaries**: **two boundaries govern this design, not one.**
  The inherited M6 temporal gate boundary remains `T* = 2014` for every surface
  that enters the M6 scored path. The proposed `gate_imm`, under the adjudicated
  certified-frame donor, is **not** an M6-boundary gate: its truth is the 2024
  reference-period `populace_us_2024` deployment frame, its estimand is the
  `gate_w1` deployment universe, and it registers against the `gate_w1` boundary
  and lock (`gates.yaml:3725-3734`, `:3732`, `:3737-3745`). A current 2026
  Trustees assumption may drive a separately versioned forward scenario, and may
  not enter or re-anchor the inherited M6 scored path. See O6.
- **Non-change declaration**: this is a docs-only design. It edits no code, gate,
  floor, run artifact, certified model, threshold, or test.
- **Donor fork**: adjudicated **certified-frame-first** by the plan owner. The
  revision-4 ACS-first apparatus is preserved verbatim in **Appendix A** and is
  the named successor that buys annual arrival resolution; nothing in it is
  lost, and reversing the fork costs a re-read rather than a rewrite.

## Revision log (finding → section)

- Revision 5 folds the O1–O16 referee round, applies its three blocking changes,
  and re-pins the whole document to `afd8f44`. (D-1) The donor half is rewritten
  in certified-frame vocabulary — `PENATVTY`/`PEINUSYR`/`PRCITSHP` on the pinned
  `populace_us_2024` frame, band-native gate masses, a household-disjoint split,
  and `floor_max_exceeds_tolerance` in place of a weight cap — with the ACS text
  preserved verbatim as Appendix A. (D-2) §9.1 is extended to
  `estimates/career.py` and `estimates/preparation.py`, the two live
  `scheduled_entries_by_year` consumers that did not exist at the revision-4
  baseline, and the `anchor_wave` schema conflict is decided rather than left
  open. (D-3) PR #221 is recorded as **merged** with its F2 **implemented**;
  Table V.A2 is recorded as **acquired and parsed**, not as an unverified
  quotation; and §4.6's newborn-ordinal consequence is stated as a measured
  design constraint. O12's insured-status gap becomes a hard exclusion, O15's
  horizon becomes an explicit prerequisite with its fail-closed parameters
  named, and four prerequisites P1–P4 replace "verification pending" →
  header, §0, §1.2, §1.4, §2.2, §2.4, §3.1–3.2, §3.5, §4.3–4.7, §4.9, §4.11,
  §5, §6.2–6.3, O1–O16, §8, §9.1–9.2, §10, §11, Appendix A, Appendix B.
- Revision 4 applies all four SPEC-SOUND referee amendments: global fitted-
  namespace IDs and a pinned domain-disjointness assertion; runner reporting
  invalidations; corrected ACS archive headers; and a training-only gate cohort-
  mix input. It also labels the 3h condensation as a paraphrase, marks the
  Trustees glossary page pin confirm-at-fetch, pins the family-B publisher, and
  exposes the remaining assignment choice as O16 → §2.2–2.4, §3.1–3.5,
  §4.1–4.7, §4.11, §5, §6, O3/O6/O10/O16, §9.1.
- Revision 3 replaces invalid collection-year slicing of five-year ACS PUMS with
  separately weighted annual 1-year files; freezes year-namespaced units, annual
  replicate designs and cross-year normalization; adds component-aware timing,
  conditional controls, a projection-origin/first-cohort decision, and explicit
  module-native initializer blockers → §2.2, §3.2, §4.2–4.9, §5, §6,
  O2/O3/O5/O6/O11–O15.
- Revision 2 incorporates the pre-PR adversarial review: it distinguishes the
  ACS survivor/stayer stock proxy from state at arrival; treats prior U.S.
  covered earnings as censored for possible return entrants; adds fertility,
  claiming, flow-to-stock, and stock-to-arrival blockers; composes immigrant IDs
  with the existing 2017/2019 schedule; guards caller-supplied allocators; and
  requires entrant RNG isolation before any byte-identity claim → §2.2–2.4,
  §3.1–3.4, §4.1–4.11, §5, §6, O2/O5/O8–O14.
- Dormant-generator finding: the engine already owns an entrant seam, but there
  is no immigration schedule generator → §3.1, §4.
- Net-is-not-entry finding: the 2026 Trustees component table distinguishes
  1.340 million positive stock-accounting inflows from 0.130 million total net
  change in 2026 → §2.4, §4.3, §4.10.
- No-history finding: a row inserted through the seam is absent from the cached
  marital, disability, household, and earnings support objects → §3.4, §4.7–4.9.
- Certificate-boundary finding: §2.8.3a, §2.8.2g, and amendment 3h prohibit
  repairing an unsupported universe by fabricating state or bypassing a live-
  roster guard → §3.3–3.5, §5.6.
- Global-ID-namespace finding: the run-local engine allocator can alias an
  omitted person retained by a global fitted surface; adopt the pending
  [PR #221](https://github.com/PolicyEngine/populace-dynamics/pull/221)
  §2.8.2i F2 law and assert entrant/domain disjointness before projection →
  §3.1–3.2, §3.5, §4.6–4.7, §4.11.
- Runner-reporting invalidation finding: the closed-panel entrant report hardcodes
  zero immigrants and counts the whole schedule as realized openers; require
  row-level `entry_kind` classification in the open-run integration → §3.1,
  §4.7, §5.6, §9.1.
- External-metadata finding: correct the 2012/2014 ACS person-archive server
  `Last-Modified` dates and mark mutable archive/glossary pins for confirmation
  when bytes are hash-bound → §2.2, §2.4, §6.2, O6.
- Donor-support finding: MINT's sparse annual cohorts and the public surveys'
  different universes require floors before any accuracy threshold → §2.1–2.3,
  §5.3.

## 0. Executive disposition

The immigration v1 object is a **pre-projection schedule builder**, not a ninth
`PeriodModules` step. It produces deterministic, pre-ID-assigned entry frames and
places only those frames at metadata key
`m6_scheduled_entries_by_year`. The existing engine then activates each frame at
the top of its period.

Revision 5 makes five choices. The first four were revision 4's provisional
proposals and are now **ratified on the referee's evidence**; the fifth is new.

1. Use the positive inflow components of the 2026 Trustees stock accounting, not
   net migration, as the size control. In that table, adjustment of status is a
   reclassification and not a new person. The temporary/unlawfully present
   inflow counts only people who remain to year-end, so it is not a count of
   every border arrival. **This is no longer an uncommitted quotation:** Table
   V.A2 has been acquired as a content-decoded HTTP 200 snapshot, hash-pinned,
   and parsed, and the parse reproduces revision 4's §2.4 table exactly
   (600 / 740 / 1,340 / 263 / 947 / 450 / 130) with all four of V.A2's published
   accounting identities asserted per row — `data/trustees_immigration.py`
   @ `29aa8c6`, snapshot sha256 `5dfd05e5…89da`. See §2.4 and O1.
2. Draw the donor from the **certified `populace_us_2024` deployment frame**,
   not from ACS PUMS. The frame carries the CPS ASEC nativity trio as live,
   populated person columns; no ACS reader or artifact exists in this repository.
   The result is a joint **resident survivor/stayer stock proxy**, exactly as
   revision 4 said of the ACS donor, and it inherits the same prohibition: a
   separately estimated stock-to-arrival bridge must map that proxy before it can
   be called entry-time state. See §2.2 and O3.
3. Copy donor information only through entry. Post-entry outcomes come from
   named populace-dynamics laws; no donor's future is cloned.
4. Keep emigration outside the entry builder. Therefore entry-only v1 is
   report-only for population stocks and cannot claim Trustees net alignment.
   A separately designed exit law is mandatory before that claim can be made.
5. **Exclude entrants from every law that was not fitted on them, by an active
   check rather than by accident.** The referee established that three of the
   four exclusions the design assumed are already enforced by code — earnings
   (`engine/earnings_domain.py:150-159`, `:217-225`), fertility
   (`engine/assembly.py:325` via `engine/panel_builders.py:164`), and, one layer
   down and for an unrelated reason, benefits
   (`estimates/career.py:1580-1581`) — while claiming is enforced **nowhere**:
   `apply_claiming` draws a claim age for every person aged 50 or over, testing
   only age and sex (`engine/steps.py:402-413`, `:411-413`). An exclusion that
   holds by accident is not a design; §4.9, §4.11 and O12 make each one an
   assertion.

The fourth choice is intentionally costly but honest. Substituting total net
change for a positive entrant control would create a reduced-form residual cohort
whose age, family, earnings, and nativity composition has no literal
interpretation. In 2026 it would also replace a 1,340 thousand positive
stock-accounting inflow proxy with 130 thousand residual persons. The 1,340
thousand itself is not all physical arrivals during the year. That alternative
remains an explicit referee decision, not a silent implementation shortcut.

**What revision 5 does not resolve.** Four prerequisites stand between this
document and a build, and the status line names them rather than describing the
draft as verification-pending:

- **P1 — the `estimates/` seam amendment.** `estimates/career.py:602` requires
  `anchor_wave` on every scheduled frame and `:612-615` asserts it equals the
  entry year; `estimates/preparation.py:332` classifies every non-reserved
  trajectory ID as a native birth and `:335-336`/`:349-352` then raise. An
  immigration frame crashes the first-estimates pipeline on its first open run.
  §9.1 decides which of the two admissible fixes is taken; the fix itself is a
  ratified amendment this design cannot make. **Blocking for any open run.**
- **P2 — the horizon.** Every executable surface stops at 2022
  (`harness/m6_runner.py:112`, `estimates/runner.py:39-40`,
  `estimates/career.py:26`, `estimates/ledgers.py:51`), and `advance_age`
  fails closed on any year the NAWI and taxable-maximum series do not cover
  (`engine/steps.py:160-165`). A 2015–2100 path is a different project with its
  own acquisition. §4.3 and O15 bind v1 to 2015–2022 and name the series.
  **Blocking for any horizon past 2022.**
- **P3 — the third leg of the universe chain.** The chain is
  `SSA area → Census resident → certified-frame universe`. Revision 4 named one
  bridge and presumed the third leg is the identity. The frame's own universe
  definition — its treatment of the institutionalized population, active-duty
  armed forces and territories — lives in microcosm-build and is not in this
  repository. **Blocking for any resident-alignment claim; see O11.**
- **P4 — two floors-ceremony measurements this design has now taken but a floors
  PR must own.** The recent-arrival Kish effective sample and the closed-vs-open
  newborn diff are reported at §5.3a and §4.6a with the exact commands. They are
  measurements, not assertions, and both are adverse: see O10 and O14.

## 1. Scope and non-goals

### 1.1 Roadmap authority and the scope it does not settle

Roadmap issue #113 is open and explicitly places immigration in M6:

> “M6 | **Projection engine**: year-by-year forward simulation to ~2100 —
> demographics (M3) + earnings forward + DI (M4) + immigration entry cohorts +
> an explicit, versioned alignment layer to Trustees intermediate assumptions”

It also defines the target panel:

> “The proposal here is that **the canonical object is a person-period panel**:
> populace persons × years (~2026–2100), with future births and immigrant
> entrants as synthetic persons entering the panel, per-year calibrated weights,
> and the full variable surface as column groups.”

Those statements authorize entry cohorts, synthetic person rows, calibrated
weights, and Trustees alignment. They do **not** decide gross versus net flows,
emigration, legal status, donor construction, entry timing, family-unit
materialization, or the state histories required by downstream modules. This
document proposes that missing scope.

### 1.2 In scope for v1

V1 specifies:

- a vintage-pinned annual cohort-control manifest;
- an estimated, versioned recent-arrival donor artifact drawn from the certified
  `populace_us_2024` deployment frame;
- a deterministic builder for entry frames and module-native entry-state
  packets;
- activation exclusively through `SCHEDULED_ENTRIES_KEY`;
- invariant checks for time coordinates, IDs, ordinals, weights, roster
  presence, and provenance;
- explicit domain adapters that **exclude** entrants from every law not fitted
  on them, reported as suppressed counts rather than zeros;
- a proposed additive `gate_imm` for entrant characteristics, registered against
  the `gate_w1` boundary; and
- report-only reconciliation to SSA and Census population projections.

The design covers people whose **reported year of entry** places them in the
recent-arrival proxy for the modeled spell. Under the certified-frame donor that
item is CPS ASEC `PEINUSYR`, which is **grouped, not annual**: on the pinned
frame the recent bands are two to three years wide and their edges are
vintage-dependent (`data/nativity_frame.py:144-148` @ `29aa8c6`). CPS asks the
year the person came to the United States to stay; the public item establishes
neither a first migration, nor legal admission, nor continuous U.S. residence.
Splitting a band into annual cohorts is a declared schedule-realization rule
(`BAND_SPLIT_RULE = "band_midpoint_rounded_up"`,
`data/nativity_frame.py:180` @ `29aa8c6`), never a donor or gate rule, and it is
un-gradeable against the survey itself. See O3-c.

### 1.3 Non-goals

V1 does not:

- model legal-status transitions, visa classes, removals, adjustment of status,
  naturalization, or status-specific program eligibility;
- infer undocumented status from ACS, CPS, or SIPP;
- treat foreign earnings as Social Security covered earnings;
- model return migration as a distinct state;
- implement emigration or an overseas-beneficiary population;
- modify mortality to disguise emigration;
- claim that SSA's Social Security-area population and the Census resident
  population are the same universe;
- clone a donor's post-entry life;
- certify long-run entrant earnings, DI, marriage, fertility, household,
  claiming, benefit, or population-stock outcomes;
- perform M7 trust-fund accounting or M8 rules execution; or
- change the inherited M6 gate, frozen floors, model registries, RNG registry, or
  module order.

### 1.4 Emigration boundary

Emigration is **out of the v1 entry builder** because it has a different risk
universe and event law: it removes a roster-present person, can end an employment
spell, may preserve accrued U.S. benefit rights, and depends on time since entry.
The current entrant seam only adds prebuilt rows. Reusing mortality, negative
weights, or a fabricated negative entrant cohort would confound distinct events.

The engine makes this a stronger statement than revision 4 knew. The only
person-removal path in the eight ordered adapters is `apply_mortality`
(`engine/steps.py:113-134`), which draws one uniform per person and returns
`ordered.loc[~death]` and nothing else. `PeriodModules` is a frozen dataclass of
exactly eight adapters plus an optional initializer
(`engine/loop.py:117-129`) and the loop calls those eight in fixed order
(`engine/loop.py:297-350`). An exit law is therefore **not expressible** without
either a ninth adapter — which §8 forbids — or entrant-aware conditional code
inside the mortality slot. Revision 4's O1 branch (b) read as "widen the design";
at head it is "amend the frozen module order," a materially different ask. O1
records that correction.

This is a component boundary, not a declaration that emigration is unimportant.
MINT, DYNASIM, PENSIM, and PENSIM2 all provide evidence that literal entrant
modeling and population alignment require exits. Until a separate exit design is
ratified, v1 may certify only the named recent-arrival stock-proxy
characteristics conditional on a positive inflow control. Every stock,
dependency ratio, benefit total, and net-migration reconciliation remains
report-only.

## 2. Evidence and adjudication

### 2.1 What predecessor models actually do

| Model/source | Cohort count and exits | Entrant state | Transportable lesson |
|---|---|---|---|
| DYNASIM4 | The 2024 overview says immigration adds people, lists immigration and emigration separately, and says immigration is aligned to OACT targets (Cosic, Johnson, and Smith, *[Urban's Dynamic Simulation of Income Model 4](https://www.urban.org/sites/default/files/2024-09/Urban%E2%80%99s%20Dynamic%20Simulation%20of%20Income%20Model%204.pdf)*, pp. 1–2). | The public 2024 overview does not document a detailed donor algorithm. | Cite DYNASIM4 only for the listed flows and OACT alignment; do not attribute undocumented separation or donor mechanics to it. |
| DYNASIM3 detail | Table 1 of Favreault, Smith, and Johnson, *[The Dynamic Simulation of Income Model (DYNASIM): An Overview](https://www.urban.org/sites/default/files/publication/67366/2000391-The-Dynamic-Simulation-of-Income-Model-DYNASIM-%20An-Overview.pdf)* (2015), p. 7, uses OACT/Dowhan-Duleep targets by sex, age at entry, and source region, and a separate SSA-data emigration hazard using entry age and origin. | The same table says observed post-1980 immigrants' life histories are donors. | Donor histories plus distinct exit hazards are a useful precedent, but this report describes DYNASIM3 and cannot establish DYNASIM4's detailed implementation. |
| MINT6/MINT8 | MINT6 derived gross flows from OACT net targets and an emigration hazard; MINT8 uses projected gross legal and other-than-legal entries and models emigration separately (Smith et al., *[Modeling Income in the Near Term Version 6](https://www.urban.org/sites/default/files/publication/24986/412479-Modeling-Income-in-the-Near-Term-Version-.PDF)*, ch. II §VI, pp. II-24–II-28; Smith and Favreault, *[Modeling Income in the Near Term 8 and 2014: Primer](https://www.urban.org/sites/default/files/publication/100965/modeling_income_in_the_near_term_8_and_2014_primer.pdf)*, pp. 15–16, note 21 p. 29, Table 3 pp. 39–40). | MINT6 uses post-1990 SIPP immigrants to initialize sex, immigration age, source region, marital history/status, financial assets, and employment at arrival. It then runs ordinary post-entry modules. | Copy a coherent entry packet, never a donor's future. An initializer and the later transition laws are separate estimands. |
| PENSIM | Holmer, Janney, and Cohen, *[PENSIM Overview](https://www.retirementplanblog.com/wp-content/uploads/sites/304/2006/10/overview.pdf)* (Policy Simulation Group for the U.S. Department of Labor, Employee Benefits Security Administration, Sept. 2006), §2.1.6 p. 8, combines SSASIM/Trustees net immigration with native- and foreign-born emigration assumptions to derive gross flows; Appendix B §B.1 p. 99 begins a synthetic life at age zero, §§B.1.2–B.1.3 p. 100 schedule immigration/emigration, and §§B.7–B.8 pp. 106–107 execute them. | A person's whole pre-entry life exists before the immigration event. | Whole-life synthesis avoids missing histories, but is not portable to a roster that materializes a person at entry. The needed analogue is an explicit entry-state packet. |
| PENSIM2 | O'Donoghue, Redway, and Lennon, *[Simulating migration in the Pensim2 dynamic microsimulation model](https://www.microsimulation.pub/articles/00039)* (2010), §5.1 and Figure 3, disaggregates ONS net controls into gross immigration and emigration. | §3 discusses synthetic generation versus cloning and Table 2 inventories model components; §5.2 samples immigrant **families** from the 2003 Labour Force Survey and calibrates person totals. | Preserve joint family state and distinguish the control unit from the donor/simulation unit. Net-only migration can bias population structure (§3 and §4). |

MINT is the closest architectural analogue. Earlier MINT versions cloned a
donor's later trajectory, but MINT6 “modifies this approach markedly”: donor
information stops at arrival and the entrant then passes through ordinary
modules (MINT6, pp. II-24–II-26). MINT6 also reports roughly 300 synthetic entrant
records per year and noisy single-age results (pp. II-25–II-28, Tables 2-15 and
2-16). That is direct evidence for support floors and against an arbitrarily fine
matching grid.

The SSA research trilogy reaches a compatible conclusion. Duleep and Dowhan,
“[Incorporating Immigrant Flows into Microsimulation Models](https://www.ssa.gov/policy/docs/ssb/v68n1/v68n1p67.html),”
*Social Security Bulletin* 68(1), 2008, §§“Projecting the Flow of Immigrants” and
“Giving the New Immigrants Earnings Profiles,” identifies flow projection and
earnings imputation as different tasks. It recommends immigrant donors grouped
by sex, age at migration, and source region, and warns that a parametric approach
may suppress within-cell variation. The companion “[Adding Immigrants to
Microsimulation Models](https://www.ssa.gov/policy/docs/ssb/v68n1/v68n1p51.html),”
pp. 51–66, shows why initial relative earnings and time since entry matter and why
emigration cannot be ignored.

### 2.2 The donor: sources, roles and limitations

**The fork, and how it was settled.** Revision 4 routed the donor through five
separately weighted annual ACS 1-year PUMS files. The plan owner has adjudicated
**certified-frame-first**, and the referee took that adjudication as settled
rather than re-litigating it. The reason is measurable, not preferential:

- **There is no ACS artifact and no PUMS reader in this repository.**
  `data/external/` holds 56 entries — PSID, NCHS, Census tabulations, SSA, BDS,
  J2J, QWI, SUSB, ONS, UKHLS — and no ACS file of any kind. A grep for
  `acs_pums|PUMS|PWGTP|YOEP|SERIALNO|ADJINC` across `src/` and `scripts/`
  returns only CPS-ASEC/IPUMS **firm-size** hits
  (`src/populace_dynamics/data/asec_firm_size.py`,
  `src/populace_dynamics/firms/banding.py`). Revision 4's `YOEP`, `PWGTP`,
  replicate blocks and `(survey_year, SERIALNO)` units have **no referent here**.
- **The nativity data is already in hand, on the frame the engine deploys onto.**
  The `gate_w1` deployment frame — `populace_us_2024.h5`, sha256
  `c2065b642ab00da74746afdfd9f06890e5f32f9b10bd6610ff236452d40f39c5`, pinned at
  `gates.yaml:3729` and restated in code at
  `src/populace_dynamics/data/deployment_frame.py:43-62`, whose own comment says
  "the pin **is** the estimand's identity" (`:41-42`) — carries `PENATVTY`,
  `PEINUSYR` and `PRCITSHP` as live, populated person columns.

Revision 4's ACS apparatus is preserved verbatim in **Appendix A** and remains
the named successor artifact that buys annual arrival resolution. Its cost is
recorded honestly in O3-c: this donor cannot express an annual entry cohort.

| Source | Exact public support | V1 role | Binding limitation |
|---|---|---|---|
| **Certified `populace_us_2024` deployment frame** | The exact blob pinned by `gates.yaml:3725-3734` (`dataset_uri` with build revision `populace-us-2024-sparse-l0-refit-57k-71a0887-national-only-20260701` at `:3728`, `artifact_sha256` at `:3729`, `reference_period: '2024'` at `:3732`, `n_persons: 166302` / `n_households: 57240`), read by `src/populace_dynamics/data/nativity_frame.py:502` @ `29aa8c6`. Carries the CPS ASEC nativity trio `PENATVTY` (country of birth), `PRCITSHP` (citizenship status, five codes) and `PEINUSYR` (grouped year of entry), plus `A_MARITL` already mapped through the seven Census ASEC recodes at `deployment_frame.py:65-73`. | **Primary joint donor and `gate_imm` truth** for the named recent-arrival stock-proxy surface. Fit and score on a **household-disjoint split** of the one frame (§5.2). | The frame is a **single 2024 reference period** — there is no annual dimension to slice, and no temporal fence is available (§5.2, O6). `PEINUSYR` is **grouped and vintage-keyed**, not annual. The nativity columns are **not calibration targets**: no nativity column appears in `deployment_frame.REQUIRED_SOURCE_COLUMNS` (`:92-99`), and the frame pins no nativity margin, so this composition is a free consequence of the L0 sparse reweighting rather than a target it hit. A recent-arrival respondent is a resident survivor/stayer observed at interview, not an arrival. |
| CPS ASEC documentation | Census ASEC data dictionaries and technical documentation for the vintages behind the frame's nativity columns; `PRCITSHP` value labels transcribed from the 2024 dictionary (position 147); `PENATVTY` country codes from **Appendix I, "Countries and Areas of the World"** — the dictionary's own "See Appendix H" note is a stale cross-reference to the Source and Accuracy Statement. Encoded at `data/nativity_frame.py:82-107`, `:110-148` @ `29aa8c6`. | **Donor provenance**, not a separate diagnostic file. This is O7 inverted: CPS ASEC stops being report-only triangulation and becomes the donor's own code book. | ASEC code books cannot be taken at face value across vintages, and this repository has already adjudicated one such case: it keeps two vintage-keyed code→interval maps for `FIRMSIZE` (`firms/banding.py:246-253`, `:265-276`) after concluding that the 2019+ relabeling was **documentary, not real** (`:66-67`, `:255-264`; `data/asec_firm_size.py:10-16`). A cross-vintage difference may be real — as `PEINUSYR`'s top code is — or phantom; only the dictionaries distinguish them. See O7′ and the findings below. |
| SIPP | Census, *[2014 SIPP Metadata, all sections v2](https://www2.census.gov/programs-surveys/sipp/tech-documentation/data-dictionaries/2014/w1/2014SIPP_Metadata_AllSections_v2.pdf)*: `WPFINWGT` p. 9; marital status p. 23; age p. 30; nativity/citizenship pp. 35–37; grouped `TYRENTRY` and entry-status item `TIMSTAT` pp. 38–39; education p. 42; sex p. 43; disability p. 1368; monthly earnings p. 2766. | **Narrowed to one role: parity and birth history** — the single state the certified frame does not carry and a jointly matched second donor could (O13). Marital and employment state now come from the same frame that supplies nativity, which is strictly better on the two grounds that matter: already hash-pinned, and jointly observed on the same person row. | No SIPP artifact of any kind exists in `data/external/`. Wave 1 covers the 2013 reference year and a civilian-noninstitutional universe. `TIMSTAT` is neither a legal-history panel nor authority to model status and is excluded from v1 state. O8 is **no longer blocking for v1** (see O8). |
| ACS PUMS | See **Appendix A** — every URL, dictionary, Accuracy statement, erratum and concept break preserved verbatim from revision 4. | **Named successor artifact.** Buys annual `YOEP` resolution and a genuine temporal fence. | Nothing in this repository reads it; adopting it is a 2.5–4.0 lane-week greenfield acquisition. Not a v1 dependency. |

**The predicate, as the code writes it.** The recent-arrival donor is
`recent_arrival_donor()` at `data/nativity_frame.py:395` @ `29aa8c6`:

```text
source_year == vintage                     # a single ASEC vintage, default 2024
and PEINUSYR in codes                      # default (28,), the vintage's top band
and PRCITSHP in FOREIGN_BORN_CODES         # (4, 5) — nativity_frame.py:93
```

with `entry_age = max(age - (source_year - arrival_year), 0)` attached, and
`arrival_year` taken from the vintage's own published bin table, never from a
midpoint crosswalk. Three properties of that predicate are design law, and each
was discovered by building it rather than assumed:

1. **The band table is keyed on `(source_year, code)`, not on code alone**
   (`data/nativity_frame.py:144-148` @ `29aa8c6`). The certified frame **pools
   three ASEC vintages** (`source_year ∈ {2022, 2023, 2024}`), and `PEINUSYR`'s
   top code means different windows in each: code 27 is 2020–2022 on the 2022
   vintage, 2020–2023 on the 2023 vintage, and 2020–2021 on the 2024 vintage,
   which adds a code 28 for 2022–2024. One crosswalk over the pooled file
   mislabels arrival years. `vintage_domain_mismatch()`
   (`data/nativity_frame.py:278`) measures the residue rather than assuming it
   away: 795 of the 25,968 in-universe rows carry a `(source_year, code)` pair
   the labelled vintage's dictionary does not define, and **no arrival year is
   asserted for them** (`runs/entrant_schedule_v1.json` → `donor.vintage_domain_mismatch`).
2. **`PEINUSYR`'s universe is everyone not born in the fifty states**, so the
   recent-arrival band also contains **natives**: people born in Puerto Rico or
   a US outlying area (`PRCITSHP == 2`) and people born abroad of US parents
   (`PRCITSHP == 3`). They are US citizens at birth and appear in **neither** of
   Table V.A2's two stocks — their move is internal migration, not immigration —
   so sizing them against a V.A2 inflow would put people the control never
   counted into the cohort. Measured on the 2024-vintage top band: **30 of 1,185
   rows** (25 born abroad of US parents, 5 PR/outlying). The donor excludes them
   (`foreign_born_only=True`, `data/nativity_frame.py:400`, applied at `:443-444`).
3. **The universe identity holds exactly, which is evidence the columns survived
   the L0 sparse refit intact rather than being partially zeroed.** On the pinned
   blob, `PEINUSYR == 0` and `PRCITSHP == 1` are the same 140,334 rows. Because
   no nativity column is in `deployment_frame.REQUIRED_SOURCE_COLUMNS`,
   `nativity_frame.REQUIRED_NATIVITY_COLUMNS` (`:156-160` @ `29aa8c6`) is the
   only guard standing between a future zeroed column and a silently degenerate
   donor; it is a hard requirement of the donor artifact, not a nicety.

**Measured support — two numbers, and which one governs.** Both were reproduced
this revision from the pinned blob (§5.3a records the command):

| Pool | Person rows | Households | Weighted persons | Persons/hh |
|---|---:|---:|---:|---:|
| All-vintage `PEINUSYR ∈ {27,28}`, natives included | 3,835 | 1,866 | 8.996 M | 2.06 |
| All-vintage `PEINUSYR ∈ {26,27,28}`, natives included | 5,444 | 2,605 | 13.147 M | 2.09 |
| **2024 vintage, code 28, foreign-born only — the donor the code builds** | **1,155** | **562** | **2.345 M** | **2.06** |
| 2024 vintage, code 28, natives included | 1,185 | 579 | 2.430 M | 2.05 |
| 2024 vintage, codes 27+28, foreign-born only | 1,671 | 806 | 3.316 M | 2.07 |

The **3,835 persons in 1,866 households** figure is the referee's, and it is
exact: it is the pooled all-vintage code-27/28 count under one midpoint
crosswalk. It is **not** the donor. Restricting to one vintage for band
coherence (finding 1) and to the control's universe (finding 2) takes it to
**1,155 rows in 562 households**. This design records the smaller number as
governing, because it is what `recent_arrival_donor()` returns, and it records
the larger one because it is the ceiling that relaxing either restriction would
buy — and because O10's support finding is decided on the difference. Pooling
bands buys support and costs vintage coherence; that tension is real, it is
measured on the same pool, and §5.3 requires the floors ceremony to price it
rather than resolve it by preference.

**The limit that survives every branch.** Both surveys observe a *resident
survivor/stayer at interview*, not an arrival. Education, marriage, disability,
employment, earnings and residence all change between reported entry and
interview. This predicate therefore defines a resident **stock proxy**, not
entry-time truth. Directly copying that state onto an entry-year row is only a
named report-only initializer. A literal arrival-state claim requires the
separately bound stock-to-arrival bridge in §6.2/O12, and under this donor that
bridge is **worse off** than revision 4 assumed: `PEINUSYR` is a two-to-three
year band, so duration since arrival cannot be computed to the year even in
principle, and the frame is a single cross-section with no second observation
from which pre-interview attrition could be estimated. The restriction to the
most recent band is what keeps the interview-minus-arrival lag short — under
`BAND_SPLIT_RULE = "band_midpoint_rounded_up"` the 2024-vintage code-28 band
(2022–2024) yields `arrival_year = 2023` and therefore a lag of **exactly one
year for every one of the 1,155 donor rows**, measured — which is what makes the
proxy tolerable for age and sex, and tolerable for nothing else.

### 2.3 Donor-based versus model-based assignment (O16, resolved)

**Adjudication, ratified at O16: donor-based joint assignment, with model-based
calibration and no cloned future.** This preserves observed covariance among the
characteristics the donor actually carries (§4.5) — age, sex, nativity,
citizenship, arrival band and marital status. A purely parametric set of
independent draws is rejected for v1 because passing marginal cells would not
establish a coherent person or family packet.

“Donor-based” does not mean raw row copying:

- the donor pool, matching grid, fallback ladder, unit construction, weight
  trimming, allocation-flag policy, and calibration loss are fitted/versioned;
- survey concepts are mapped to named entrant concepts with missing/unsupported
  states rejected rather than guessed;
- an explicit duration/backcast and survivor/stayer selection law maps the
  interview-date stock proxy to arrival state, or the result stays labelled
  `stock_proxy` — and under this donor that law is **not identified from the
  donor at all** and must come from outside it (O12);
- a second history donor, if used for the one state the frame lacks (parity;
  O13), is a separate named imputation with its own joint-fidelity diagnostics;
- future outcomes are never present in the donor artifact; and
- runtime realization is deterministic conditional on the frozen artifact,
  controls, and seed.

A genuinely joint parametric challenger may compete only on the same fit/holdout
split, unit-closure law, joint holdout surface, and floors, and **it is deferred
out of v1** (O16-d): on the support measured in §5.3a a two-family gate cannot
discriminate two joint-assignment architectures. Independent marginal hot-decks
remain inadmissible — there is no seam in this engine that would accept their
output (O16) — and lower marginal error alone is insufficient.

Because the joint surface a `gate_imm` PASS would score is itself outside
populace's calibration loss, that adjudication carries a mandatory disclosure at
headline prominence; see §5.6 and O16-c.

### 2.4 Gross inflow, net change, and status adjustment

The control is *The 2026 Annual Report of the Board of Trustees of the Federal
Old-Age and Survivors Insurance and Federal Disability Insurance Trust Funds*,
§V.A.3, released June 9, 2026, and the [Supplemental Single-Year Table V.A2,
“Immigration Assumptions, Calendar Years
1940–2100”](https://www.ssa.gov/oact/TR/2026/lr5a2.html). The assumptions were
set in February 2026. Table V.A2 carries, separately, LPR new-arrival inflow,
LPR/citizen outflow, adjustment to LPR status, LPR net change,
temporary-or-unlawfully-present inflow, outflow, the offsetting status
adjustment, that stock's net change, and total net change.

**The table is acquired, hash-pinned and parsed — it is no longer a quotation.**
Revision 4 asserted the figures below as evidence while the bytes were not in the
repository, and `lr5a2` was not among the six hash-pinned snapshots in
`data/external/snapshots/ssa_level_anchors_vintage1/capture_manifest.txt`. That
gap is closed at `29aa8c6`:

```text
source_url   https://www.ssa.gov/oact/TR/2026/lr5a2.html
http_status  200
sha256       5dfd05e5c5d4bbe413dd97f2256db24d5595e561623455edca3761bbfece89da
bytes        326209
retrieved    2026-09-06T14:55:07Z
manifest     data/external/snapshots/trustees_va2_vintage1/capture_manifest.txt
provenance   data/external/trustees2026_lr5a2.source.provenance.json
reader       src/populace_dynamics/data/trustees_immigration.py
```

`ssa.gov` answers HTTP 403 to `curl` and to WebFetch from the lane environment.
The snapshot was obtained by **browser network-response capture** — the route the
repository already documents at
`scripts/extract_ssa_tr_ultimate_assumptions_2014.py:1-11` for the identical 403
class — and the content-decoded HTTP 200 body was committed **directly, with no
transcription step**. Both the snapshot and its one-line capture manifest are
pinned by sha256 inside the reader module, so a source reissue fails closed
rather than silently re-parsing different bytes. Two consequences the manifest
records: Akamai adds request-specific delivery markup, so the hash identifies
this one reviewed acquisition; and the page leaves the calendar-year `<td>`
**unclosed** on every data row, which makes the repository's existing
`_AllTablesParser` (`scripts/build_ssa_level_anchors.py`) raise "nested table
cell" and cannot read the page at all — hence
`_ImmigrationTableParser` (`data/trustees_immigration.py:188` @ `29aa8c6`), which
closes an open cell implicitly and is the only variant that preserves the year.

For intermediate 2026, in thousands — **parsed from the committed snapshot, and
identical to revision 4's independently quoted table in every component**:

| Component | Persons (thousands) | Parsed = rev. 4 quoted | Entry-seam meaning |
|---|---:|:--:|---|
| LPR new-arrival inflow | 600 | ✓ | SSA stock-accounting new-person inflow |
| Temporary/unlawfully present inflow | 740 | ✓ | SSA stock-accounting new-person inflow, conditioned on remaining to year-end |
| **Positive SSA inflow components** | **1,340** | ✓ | The entry control (`ImmigrationYear.positive_inflow`, `data/trustees_immigration.py:144`) |
| LPR/citizen outflow | 263 | ✓ | Exit, never an entrant |
| Temporary/unlawfully present outflow | 947 | ✓ | Exit, never an entrant |
| Adjustment to LPR status | 450 in each stock, opposite signs | ✓ | Internal reclassification; not a new person |
| **Total net change** | **130** | ✓ | Reconciliation target, not a literal cohort |
| *derived* `entry_only_minus_net_gap` | 1,210 | — | The named audit line (`data/trustees_immigration.py:155`), never minimized |

The reader asserts **V.A2's own four published accounting identities on every
row** (`_check_row_identities`, `data/trustees_immigration.py:357` @ `29aa8c6`) —
LPR net = inflow − outflow + adjustment; other net = inflow − outflow −
adjustment; the two adjustment figures are equal; total net = LPR net + other
net — across **311 rows in four scenario sections** (historical, intermediate,
low-cost, high-cost), with a ±2-thousand tolerance that is the sum of the terms'
rounding half-widths because the table publishes whole thousands, not slack
chosen to make the check pass. It exposes `positive_inflow` as the **only**
entry-seam control and structurally refuses to hand out a net-change figure as a
sizing basis. The control across an illustrative 2026–2035 activation window, in
thousands: 1,340 · 1,350 · 1,390 · 1,460 · 1,570 · 1,670 · 1,740 · 1,780 ·
1,790 · 1,800.

The 75-year intermediate average total net change is 1.138 million, but Table
V.A2 is annual and materially non-flat; the annual component values, not the
average or ultimate constant, are the binding shape. Components may differ by
rounding — the 2026 row exercises exactly that: LPR net publishes 788 while
600 − 263 + 450 = 787, and total net publishes 130 while 788 + (−657) = 131.

For the temporary/unlawfully present stock, “inflow” counts people who enter the
Social Security-area population and remain through the end of the year. Thus the
positive sum is neither a border-admissions series nor an unselected gross-arrival
flow.

**Table V.A2 has no public age/sex detail.** It sizes cohorts only; all
composition comes from the donor. That division — V.A2 for the level, the frame
for the shape — is the whole architecture.

The table's universe is the **Social Security area**, not the Census resident
population, and not the certified frame's universe either. Even gross inflow is
therefore not directly a resident-population control, and revision 5 records that
the chain has **three legs, not two** (O11, P3). A named universe bridge is
required before production use (§6.1). Until then, both the gross entry schedule
and the net reconciliation are report-only and the schedule is labelled
`ssa_area_proxy`.

## 3. Binding repository and domain law

### 3.1 The only entrant activation seam

The engine already defines
[`SCHEDULED_ENTRIES_KEY = "m6_scheduled_entries_by_year"`](../../src/populace_dynamics/engine/loop.py#L27)
at `engine/loop.py:27`. V1 feeds that seam and creates no parallel entry hook.

The contract at `afd8f44` is exact. Every pin below was re-opened at that tree
for revision 5:

- `PeriodModules` is a frozen dataclass carrying the eight ordered adapters plus
  an optional initial-frame hook, and **no entrant adapter**
  (`engine/loop.py:117-129`; the docstring at `:119` reads "All eight required
  adapters in the binding section 2.2 order").
- Initialization runs once on the original starting slice before the schedule is
  read (`engine/loop.py:203-214`). Scheduled entrants do not pass through it.
- Each schedule key must satisfy `start_year < entry_year <= end_year`
  (`engine/loop.py:228-232`, raising "scheduled entry year … lies outside the
  projection" at `:231`); its value must be a validated `DataFrame`
  (`_validate_slice`, `:162-168`) carrying the single coordinate
  `year == entry_year - 1` (`:236-239`).
- Every scheduled `person_id` is pre-supplied and unique across the initial slice
  and all cohorts (`engine/loop.py:242-250`).
- If metadata does not already supply one, the dynamic synthetic-ID allocator is
  created at `max(initial ∪ all scheduled ids) + 1` (`engine/loop.py:251-257`).
  Because the code uses `setdefault` (`:254`), a caller-supplied allocator is
  only **type-checked** (`:258-262`); v1 must separately range-check it.
- Stable person RNG ordinals are preassigned over the complete
  initial-plus-scheduled ID universe before period 1, by
  `enumerate(sorted(all_initial_ids))` (`engine/loop.py:263-266`).
- At entry year the frame is concatenated and stably sorted at the very top of
  the period (`engine/loop.py:271-286`: the collision guard at `:273-280`, the
  `pd.concat` at `:281-283`, the stable sort at `:284-286`), strictly before
  mortality (`:297`) and the remaining ordered modules (`:297-350`).
- Newborns and any other dynamically created rows receive ordinals only after the
  projected slice validates, and the ordinal assigned is the **cardinality of the
  ordinal map** (`engine/loop.py:352-360`; `person_ordinals[person_id] =
  len(person_ordinals)` at `:360`). §4.6a develops the measured consequence.

The seam is not wholly dormant. `M6RealizedPopulation.projection_metadata`
already publishes later PSID openers through the same key
(`harness/m6_population.py:52-82`, the metadata builder at `:70-82`), and the
realized-population builder schedules 2017/2019 openers with its convention
written out at `harness/m6_population.py:329-335`. The missing object is an
**immigration/new-entrant generator and its state packet**, not a generic engine
entry mechanism.

The immigration builder must **compose with**, not replace, that existing
mapping. For each shared year it schema-reconciles and concatenates a
value/ID-preserving copy of the PSID opener frame with the immigrant frame, then
validates one prior-year coordinate and global ID uniqueness. The composed copy
adds and validates the reporting discriminator `entry_kind`; this annotation does
not mutate the source opener mapping or alter any pre-existing opener value or
ID. The `entry_kind` vocabulary is already implemented at
`engine/entrant_schedule.py:73-77` @ `29aa8c6`
(`ENTRY_KIND_COLUMN = "entry_kind"`, and the values `immigrant_cohort`,
`maternal_birth`, `realized_opener`, `incumbent`), and the design adopts those
literals rather than inventing a second vocabulary.

**PR #221 is merged, and its F2 is implemented in code.** Revision 4 recorded
[PR #221](https://github.com/PolicyEngine/populace-dynamics/pull/221) §2.8.2i
**F2** as a *pending* dependency and instructed integrators to build an
equivalent floor themselves. Both statements have been false for 52 days. PR #221
merged at **2026-07-16T01:08:01Z**, merge commit
`00d5443d9df21ac13e42669d13d94c5ef734134c` — one minute and forty-two seconds
after this design's last push. What the code now provides, at `afd8f44`:

- `SyntheticPersonIdAllocator` carries `reserved_real_ids` and raises "synthetic
  person IDs overlap the reserved real-person namespace"
  (`engine/loop.py:44-64`, the raise at `:57-62`);
- `M6RealizedPopulation` carries `reserved_real_ids` and `synthetic_id_start`
  (`harness/m6_population.py:59-61`) — neither field existed at the revision-4
  baseline;
- `harness/m6_runner.py:432-441` constructs the reserved set as the anchor ∪
  `realized_earn_2014_by_person` ∪ `u_w_by_person`; and
- `harness/m6_population.py:70-82` hands the engine a **pre-built** allocator
  carrying that set.

An implementer following revision 4's §3.5 — "Until PR #221 lands, an
integration must implement the equivalent explicit floor" — would build a floor
that already exists. Two things the code still does **not** provide, and this design must
therefore keep:

1. **The design's floor is stronger than the code's, and the difference matters.**
   The implemented `synthetic_id_start` is `max(holdout_ids ∪ reserved_real_ids)
   + 1` (`harness/m6_population.py:226-229`, the assignment at `:229`) and does
   **not** union the scheduled
   opener IDs. This design's floor does:

   ```text
   immigrant_id_floor = 1 + max(
       reserved_real_person_ids union preexisting_schedule_ids
   )
   ```

   A birth allocated onto a scheduled opener's ID would fail closed at
   `engine/loop.py:273-280` ("scheduled entrants are already active") rather than
   corrupt silently, so the gap is a latent crash and not silent aliasing — but
   the design's formula is the right one and is retained with that reason stated.
2. **The seam never consults the reserved set for scheduled entrant IDs.** The
   schedule path checks only column presence and `person_id` uniqueness
   (`_validate_slice`, `engine/loop.py:162-168`), the `year - 1` coordinate
   (`:236-239`) and cross-frame collisions (`:242-250`). A scheduled entrant may
   therefore alias a reserved real person omitted from the run — precisely the
   hazard F2 exists to prevent, left open on the entrant path. Separately, the
   engine's own fallback allocator (`engine/loop.py:255-257`) is constructed with
   an **empty** reserved set, so a caller that omits the metadata allocator loses
   the F2 protection entirely. §4.11 makes both builder-side assertions and O14-d
   records the engine-side check that should follow.

Before any gate split or other subsetting, construct and freeze
`reserved_real_person_ids` as the union of the full anchor and every person-keyed
fitted support consumed by assembly. At minimum this includes the keys of both
earnings fitted-state maps (and therefore every `adapter.domain_person_ids`
member), marital attributes, household attributes/person waves, and disability-
panel person keys. Let `preexisting_schedule_ids` contain every PSID opener ID,
freeze the floor unchanged through every subset operation, and allocate immigrant
IDs from it in deterministic order. Because the floor also exceeds every
pre-existing scheduled ID, existing-person and existing-opener sorted ordinals
remain unchanged — **measured, not argued**: see §4.6a. A different high namespace
is admissible only if its manifest proves it disjoint from the same complete
reserved union; a side-local maximum is never admissible.

### 3.1a Pin drift from the revision-4 baseline

Revision 4 declared its baseline and every one of its pins resolved at that tree;
the drift below is disclosed movement, not error. It is recorded because a
builder needs the mapping, and because two of the rows are more than arithmetic.
Baseline `75d30dd` → head `afd8f44`:

| Revision-4 pin (baseline) | Content | Revision-5 pin (head) |
|---|---|---|
| `loop.py:192-211` | schedule-key validation | `:227-240` |
| `loop.py:213-221` | global ID uniqueness | `:242-250` |
| `loop.py:222-228` | allocator `setdefault` | `:251-257` |
| `loop.py:225-233` | allocator type check | `:258-262` |
| `loop.py:234-237` | ordinal preassignment | `:263-266` |
| `loop.py:239-257` | concat + stable sort | `:271-286` |
| `loop.py:258-321` | mortality + ordered modules | `:297-350` |
| `loop.py:323-331` | newborn ordinal append | `:352-360` |
| `loop.py:110-122` | `PeriodModules` | `:117-129` |
| `loop.py:180-192` | `initialize` before the schedule | `:203-214` |
| `m6_population.py:49-73` | `M6RealizedPopulation` + `projection_metadata` | `:52-82`, **two new fields** at `:59-61` |
| `m6_population.py:313-335` | opener timing convention | `:329-335` |
| `m6_runner.py:873-874` | `initial_ids` / `synthetic_ids` | `:986-987` |
| `m6_runner.py:909-920` | the `"entrants"` block | `:1022-1036`, **one new field** `roster_absent_births` at `:1033-1035` |
| `m6_runner.py:1091-1106` | zero-immigrant fallback + consumer | `:1207-1224`, matching new key at `:1215` |
| `steps.py:113-134`, `:137-166` | mortality, aging | unchanged spans; `advance_age` gained the NAWI/wage-base block at `:149-165` |
| `earnings_domain.py:68-100`, `:156-210` | domain predicate, initializer | `:71-88`, `:161-208`; `membership` `:150-159`; `validate_domain` `:217-225` |
| `assembly.py:81-99`, `:174-192`, `:271-295`, `:297-324`, `:326-377`, `:385-424`, `:239-250` | assembly surfaces | `_merge_period_columns` **byte-unchanged** at `:174-192`; fertility holdout at `:325`; marital builder at `:283`, `:297`; initialize at `:252-254` |
| `panel_builders.py:150-165`, `:167-174` | certified marital builder | `del frame` at `:164`; the inner join at `:169-176` |
| `steps.py:409-414` | absent-parent guard | `:479-484` |
| `marital.py:313` | parity initialized to zero | `:363` — same statement, `parity = np.zeros(len(attrs), dtype=np.int64)`, moved 50 lines. Revision 4's pin was **correct at its baseline**; it is *incomplete*, not wrong, and O13 adds the two further citations the hazard needs. |
| `steps.py:320-378` | *cited by rev. 4 for `apply_claiming`* | `:390-413`; the age-only selection is `:411-413` |
| `m6_reporting.py:71-73`, `:104-118`, `:285-301` | family-B disclosure, bridge, publisher | `:71-74`, `:104-118`, `:277-318` — **byte-identical file**; the `"gated": False` at `:300` and `truth_basis` at `:317` |

Two consequences beyond arithmetic. First, the head `"entrants"` block gained
`roster_absent_births`, so revision 4's §9.1 patch list is not merely
mis-numbered but **short a field**. Second, the `"immigrant_cohorts": 0` hardcode
now appears at **two** live sites — `harness/m6_runner.py:1027` and `:1212` — and
is read into the family-B publisher at `:1220`. §9.1 names both.

### 3.2 Consequences for timing, IDs, and RNG

An entry frame is a pre-period state. Mortality sees it first
(`engine/steps.py:113-134`); aging then adds one to `age` and writes the target
year (`engine/steps.py:137-166`, the increment at `:147`, the year write at
`:148`). The existing PSID opener builder deliberately stores the prior year
coordinate while retaining the observed collection-wave age, and writes out why:
"The loop's first mortality step therefore sees the observed anchor age, and its
later aging step advances toward the next collection-wave age used by the forward
earnings fit" (`harness/m6_population.py:329-335`). **An immigration frame that
adopts a different convention makes the composed schedule internally inconsistent
at the exact point `engine/loop.py:281-283` concatenates the two into one frame.**
That is the strongest argument for O2 branch (a) and revision 4 did not use it.

`apply_mortality` draws one uniform per person and returns survivors
(`engine/steps.py:113-134`, the per-person addressed draw at `:121-132`): there
is no exposure fraction and no per-person weighting of the hazard. `advance_age`
does `age + 1` unconditionally (`:147`). There is no hook between them. So the
unchanged adapters implement only a full mortality draw at the scheduled age
followed by unconditional `age += 1`; they cannot express a fractional exposure,
defer aging, or output a target-year age-zero immigrant without an entrant-aware
wrapper inside two of the eight certified slots. O2 resolves this.

**`advance_age` has a second obligation an entry frame must satisfy, and it fails
closed.** At head it also rolls `nawi` and `taxable_max` from
`context.metadata["nawi_by_year"]` and `["wage_base_by_year"]`, raising
"aging cannot roll `<column>` without `<metadata_key>`" when a frame carries the
column and the metadata does not carry the series (`engine/steps.py:149-165`, the
raise at `:156-158`), and raising "`<metadata_key>` has no value for
`<year>`" for any year the series does not cover (`:160-165`). That block did not
exist at the revision-4 baseline. Two consequences are now design law:

- **An immigration entry frame carries neither `nawi` nor `taxable_max`, or the
  schedule builder supplies both `nawi_by_year` and `wage_base_by_year`.** An
  earnings-seeded entrant carrying either column aborts the period otherwise.
  §4.7 adds this to the invariant list.
- **The horizon is a parameter-series question, not a schedule question** (P2,
  O15). A run to 2100 needs NAWI and taxable-maximum series through 2100 — the
  Trustees intermediate assumptions — entering by a second door, and
  `engine/steps.py:160-165` makes their absence an execution blocker rather than
  a reporting gap.

That timing choice must also respect the source component's exposure basis. Table
V.A2's temporary/unlawfully-present inflow is already conditioned on remaining
through year end; applying the unchanged engine's full source-year mortality to
the raw control would apply a second survival filter. O2 therefore blocks
production until a component-aware **aggregate** timing/exposure bridge is bound —
aggregate, because the adjustment belongs at the control and not at the person,
and because a per-person adjustment is exactly the wrapper §8 forbids. The bridge
may alter the cohort control/exposure convention; it may not assign a Trustees
stock or legal-status label to individual donor rows.

IDs are assigned outside the loop in deterministic order. They must be finite
integers, begin at the frozen global `immigrant_id_floor`, be collision-free
across all years, and be invariant to row order. The floor, not a recomputed
selected-side maximum, is carried into every subset/diagnostic run. Projection
metadata must omit a pre-supplied synthetic allocator, or assert its mutable
`next_id` is strictly above every reserved real-person and scheduled-person ID
before period 1; otherwise the loop does not protect births from collision — and,
because the loop's own fallback allocator is built with an **empty** reserved set
(`engine/loop.py:255-257`), omitting the metadata allocator forfeits F2 as well.

Any run claiming full-population/original-person byte identity must additionally
check the precondition `run_real_person_ids ⊇ fitted_support_person_ids`, where
the run universe includes its initial real people and every real scheduled
opener. A subset run normally fails that precondition and may not inherit the
claim; the global namespace reservation still makes its synthetic IDs
collision-safe. No existing M6 module stream is consumed to construct the
schedule. **A byte-identity claim for dynamically created rows is separately
prohibited even within one schedule** — see §4.6a, where it is measured.

### 3.3 Amendment 3h / M6 §2.8.2h: live-roster materialization

Amendment 3h is absent from the pinned engine baseline. It subsequently merged
to master as
[PR #216](https://github.com/PolicyEngine/populace-dynamics/pull/216), commit
`0e27be2d857719b30e33b556580b4a360808b5e0`, after this branch point. Its public
forensic source is the
[3h forensics/adjudication](https://github.com/PolicyEngine/populace-dynamics/issues/42#issuecomment-4984997277)
and the merged M6 §2.8.2h text. This sibling design adopts that law as a
dependency while retaining the stated baseline for every code pin. The following
is a faithful paraphrase, not a verbatim quotation:

> **Paraphrase of merged M6 §2.8.2h:** A scheduled maternal birth may materialize
> a child only when the mother is present in the live post-mortality roster. The
> frame-independent risk schedule may remain the scoring universe; absent-mother
> events are dropped after the draw and reconciled report-only so RNG addresses
> do not shift.

Entrants are roster-present when their own rows are activated, and their later
maternal births obey this exact 3h law. V1 separately proposes a broader
**immigration relationship-closure invariant**: a donor packet may not materialize
a linked spouse, child, or other person whose row is absent. That new invariant
is analogous to, but not certified by, 3h; becoming `married` in the marital core
does not itself materialize a spouse person. Neither law may weaken the existing
birth-parent guard at `engine/steps.py:409-414`.

### 3.4 Why an entry row is not an initialized person

The current certified assembly consumes fitted objects and native-panel builders
(`engine/assembly.py:81-99`). Several adapters construct and cache a whole-window
projection once per draw:

- marital support is built once and cached (`engine/assembly.py:271-295`), and
  its certified builder deliberately ignores the live frame
  (`engine/panel_builders.py:150-165`);
- fertility draws over the cached marital IDs (`engine/assembly.py:297-324`);
- disability simulates once over realized PSID support
  (`engine/assembly.py:326-377`);
- household composition builds and caches its native panel
  (`engine/assembly.py:385-424`); and
- earnings initialization runs only on the original initial slice
  (`engine/assembly.py:239-250`; `engine/loop.py:180-185`).

When a cached update has rows for the current year, `_merge_period_columns` drops
existing state columns before left-merging it (`engine/assembly.py:174-192`). An
immigrant absent from that nonempty update receives missing state even if the
scheduled row carried a seed value; only a wholly empty year returns the frame
unchanged.
The later PSID openers work because their realized support is known to the
whole-window builders in advance. An unknown synthetic immigrant has no such
support.

Therefore the immigration generator must produce both an entry row and an
explicit, module-native **EntrantStateBundle**. Merely adding more columns to the
entry frame is rejected.

### 3.5 The §2.8.3a / §2.8.2g / 3h / merged-3i domain-law family

The sibling M6 domain laws bind this module. Revision 5 records which of them the
code **already enforces**, with citations, so that a build does not re-implement
fences that exist — and, more importantly, so that the one fence that does *not*
exist is visible:

- **Earnings §2.8.3a — enforced, fail-closed.** The certified forward generator's
  domain is the intersection with realized 2014 earnings state
  (`engine/earnings_domain.py:71-88`). `membership` is computed from the fitted
  maps and is independent of the frame's marker
  (`:150-159`); the initializer writes zero/missing outside the domain
  (`:161-208`); and `validate_domain` raises "earnings_domain marker disagrees
  with fitted 2014 state" on **any** disagreement (`:217-225`). `apply_earnings`
  validates the whole frame (`engine/steps.py:218-232`) before applying the
  `age >= 15 & domain` mask (`:296-299`), and writes
  `out["earnings"] = generated` unconditionally at `:356`. Attempting the fitted
  route instead raises "initial frame has no fitted earnings state for 2014=…,
  u_w=…" (`engine/forward_earnings.py:1421-1436`). So "no fake 2014 anchor" is
  not a policy here; it is enforced. An entrant marked in-domain aborts the
  period, and an entrant marked or left out-of-domain is pinned to
  `earnings = 0.0` in every projected slice.
- **Marital §2.8.2g — enforced by construction.** In production assembly the
  certified marital panel builder **discards the live frame**
  (`engine/panel_builders.py:164`, `del frame`) and inner-joins the certified
  attributes to the anchor (`:169-176`), so an entrant is simply not in the
  panel. The immigrant analogue is to construct a named entrant risk-set seed;
  it is not to weaken the core or pretend the PSID certificate covers the new
  population.
- **Fertility amendment 3h — enforced, and the entrant is outside the risk set by
  construction.** `apply_fertility` receives `holdout_ids = state.marital_ids`
  (`engine/assembly.py:325`), which comes from the certified builder above
  (`:283`, `:297`). A child materializes only against a live mother, guarded by
  the raise at `engine/steps.py:479-484`. **One caveat revision 4 did not record:**
  the fallback at `engine/steps.py:539` —
  `ids = holdout_ids or set(int(value) for value in frame["person_id"])` — puts
  every roster member in the risk set whenever a caller omits `holdout_ids`.
  Production never does; an entrant-aware kernel is precisely the caller that
  would. O13-c requires the risk set to be passed explicitly.
- **Synthetic IDs, merged §2.8.2i F2 — implemented.** PR #221 merged (§3.1) and
  the reserved-namespace machinery exists at `engine/loop.py:44-64`,
  `harness/m6_runner.py:432-441` and `harness/m6_population.py:70-82`. This
  design keeps the stronger floor of §3.1 and requires the two checks the code
  still lacks.
- **Claiming — NOT enforced anywhere, and this is the sharpest finding in the
  round.** `apply_claiming` requires only `{"age", "sex"}` and draws a claim age
  for every unassigned person with `age >= 50`
  (`engine/steps.py:402-413`, the selection at `:411-413`), with **no
  insured-status, quarters-of-coverage, AIME or PIA test**, and
  `src/populace_dynamics/ss/` contains no such function to call (§4.9, O12).
  Downstream, `estimates/career.py:1580-1581` excludes every person outside
  `earnings_domain_ids` with `reason = "excluded_domain_incomplete"` before any
  career is built, so an entrant today becomes a **claimant in the panel** and a
  **non-person in the benefit ledger**. Revision 4's §4.9 described an
  eligibility-domain adapter that does not exist, and did not notice that a
  domain-shaped exclusion already exists one layer down with different
  semantics. That exclusion holds **by accident** — because entrants have no
  fitted 2014 earnings state, not because anyone decided entrants are
  uninsured — and it opens in the same commit that lands an entrant earnings
  law. O12-b converts it into a guard.

No existing certificate transfers across these bridges. Reuse of unchanged core
code may be plumbing at implementation time, but applying it to an entrant
population is a new domain claim and remains report-only until its expressly
named successor gate passes.

## 4. Proposed design

### 4.1 Components and one-way data flow

The design separates source estimation, scenario binding, schedule realization,
and period activation:

```text
certified frame ─> DonorArtifact ─> ArrivalStateBridge ─┐
  (populace_us_2024, pinned)                            │
SSA Table V.A2 ────────────────> BindingManifest ───────┼─> ScheduleBuilder
second history donor (parity, O13) ─> bridge evidence ──┘       ├─> entry frames
Census scenarios ──────────> report-only corridor audit         └─> StateBundle

entry frames ──metadata[SCHEDULED_ENTRIES_KEY]──> existing engine loop
StateBundle ──entrant-only adapters/builders──> downstream state
```

The conceptual products are:

- **`ImmigrationBindingManifest`**: immutable source/vintage/schema/hash records,
  annual flow controls, universe labels, and scenario identity;
- **`ImmigrationDonorArtifact`**: a fitted pool of recent-arrival person or family
  units, matching cells, fallback hierarchy, concept mappings, and provenance,
  including the vintage-keyed band predicate, the declared band-split rule, and
  the fit-side band masses `M_gate[band]` defined in §5.2;
- **`ArrivalStateBridge`**: an estimated duration/backcast and selection law, or
  an explicit `stock_proxy` identity label that prohibits an arrival-state claim;
- **`EntrantStateBundle`**: the entry frame plus module-native initial state and
  exposure objects for the same people;
- **`ImmigrationSchedule`**: `entries_by_year`, the state bundle, deterministic
  ID ledger, and reconciliation tables; and
- **`ImmigrationAudit`**: cohort totals, donor support, calibration residuals,
  universe caveats, dropped/unsupported units, hashes, and certification labels.

The builder merges `ImmigrationSchedule.entries_by_year` with the pre-existing
mapping and sends that single combined mapping to `SCHEDULED_ENTRIES_KEY`; it
never overwrites the PSID opener frames. The state bundle is consumed by explicit entrant-side
builders/adapters assembled before projection. There is no entrant event draw in
the annual engine loop.

### 4.2 Estimation versus deterministic realization

The campaign's estimation/determinism split is binding:

**Estimated and versioned**

- recent-arrival definition and survey concept map;
- donor unit, matching variables, and fallback order;
- sampling/calibration loss and weight trimming;
- the fit-side band-mass construction, the household-disjoint split protocol
  and seed grid, support/demotion rules, and unit-mass convention in §5.2;
- any joint-history imputation from a second donor (O13);
- the stock-to-arrival duration/selection bridge, return-entry treatment, and
  fertility/parity and prior-coverage mappings;
- any entrant-specific earnings or disability initializer; and
- every evaluation floor and eventual gate threshold.

**Deterministic conditional on frozen inputs**

- parsing the committed, hash-verified external-control table;
- selecting an artifact by exact ID/hash;
- schedule realization under an explicit schedule seed;
- synthetic IDs and arrival-unit IDs;
- conversion to the seam's prior-year frame coordinate;
- cohort weight calibration to the mode-specific bound control (a production
  flow control or the frozen unit-mass gate vector); and
- serialization and audit calculations.

**Design law U1 — uncertainty nesting.** A schedule is built once per scenario
and schedule seed before the K projection draws, then reused across those draws.
The K draws therefore represent engine process uncertainty conditional on one
schedule; separately named schedule seeds/artifacts form an outer sampling-
uncertainty dimension. The schedule consumes none of the eight existing M6
period-module streams.

### 4.3 Annual cohort sizing for production/report-only scenarios

Every `G_*` quantity in this subsection is a production or report-only scenario
control. Trustees and Census controls are prohibited in `gate_imm`; gate mode
uses only the donor-derived band masses in §5.2.

For Trustees calendar year `y`, define the unbridged positive-inflow control

```text
G_ssa_stock[y] = 1,000 * (
    V_A2_selected_path[y].lpr_new_arrival_inflow
    + V_A2_selected_path[y].temporary_or_unlawfully_present_inflow
)
```

Adjustment of status is excluded because the same person moves between the two
Trustees stocks. Outflows are excluded because they are exit events. The
intermediate total-net column is retained as `N_ssa[y]` for reconciliation only.
This quantity is `ImmigrationYear.positive_inflow`
(`data/trustees_immigration.py:144` @ `29aa8c6`) and the reader exposes no
net-change accessor that a sizing path could reach.

`G_ssa_stock` is not yet a usable resident-population cohort. It includes the
temporary/unlawfully present end-of-year-stayer condition. Production
construction requires an adjudicated, vintage-pinned bridge
`G_resident_entry_proxy[y] = bridge(G_ssa_stock[y])` across the **three-leg**
universe chain of O11. The calibration target is conditional and both source
series remain in the audit:

```text
G_schedule_target[y] =
    G_resident_entry_proxy[y]  for a resident-labeled run with O11 bound
    G_ssa_stock[y]             only for an explicitly report-only ssa_area_proxy
```

Until O11 supplies the universe bridge, the builder must either hard-stop or use
the second branch. It may not silently set the bridge to identity and label the
result resident-population aligned.

**Sizing is reweighting, not resampling.** Every donor row appears once per
activation year with its weight scaled by a single factor so the cohort's
weighted total equals the control (`engine/entrant_schedule.py:158` @ `29aa8c6`).
That is deterministic, **consumes no RNG**, and reproduces the donor composition
exactly, so any residual against the control is floating-point arithmetic and not
sampling noise: the built artifact records a maximum absolute relative residual
of **2.97e-16** across its ten activation years
(`runs/entrant_schedule_v1.json` → `schedule.by_activation_year[*].alignment`).
Under this rule the "physical annual sample size" of revision 4 is not a design
choice at all: it is the donor's row count, fixed by the predicate. O10 records
that consequence.

#### 4.3a The schedule interval — a prerequisite, not a parameter (P2)

Revision 4 built its origin decision on 2015–2025 plus 2026–2100 and never
mentioned 2022. **Every executable surface in this repository stops at 2022**, and
a grep of revision 4 for `2022` returned nothing:

| Constant | Pin at `afd8f44` | Value |
|---|---|---|
| `PROJECTION_END_YEAR` | `harness/m6_runner.py:112`, consumed at `:584` | 2022 |
| `PROJECTION_START_YEAR` / `PROJECTION_END_YEAR` | `estimates/runner.py:39-40` | 2014 / 2022 |
| `PROJECTED_END_YEAR` | `estimates/career.py:26` | 2022 |
| `REPORT_YEARS` | `estimates/ledgers.py:51` (and the same tuple in `estimates/parameters.py`, `estimates/anchor_context_registry.py`, `estimates/publication.py`) | `range(2015, 2023)` |

And extending the horizon is **not** a schedule change. `advance_age` raises
`"<metadata_key>' has no value for <year>"` for any year the NAWI or
taxable-maximum series does not cover (`engine/steps.py:160-165`). A 2100 run
therefore needs both series through 2100 — the Trustees intermediate assumptions
— which is the same acquisition class as Table V.A2, entering through a second
door.

Revision 5 therefore binds the interval in two named modes:

- **v1 (this design, buildable):** origin = the realized 2014 M6 initial slice,
  first schedule key **2015**, control range **2015–2022**, drawn from Table
  V.A2's historical/estimated rows and preserving the source's row-class and
  footnote flags. This is a complete, scoreable, report-only product that needs
  no new initial-population artifact and no new parameter series.
- **v2 (blocked on P2):** any horizon past 2022. It requires, and the manifest
  must name, (i) the NAWI series and (ii) the taxable-maximum series with their
  coverage, (iii) a runner whose `PROJECTION_END_YEAR` reaches the target, and
  (iv) a decision on whether the open run is bound by `REPORT_YEARS`. Until all
  four are bound, a 2015–2100 schedule is not a longer version of v1; it is a
  different project, and this design will not let the two be confused by silence.

The interval must be continuous from `start_year + 1` through the bound end year.
No 2015–2025 gap and no silently dropped first cohort is permitted. A 2026 initial
slice cannot accept a 2026 schedule key: that cohort must be demonstrably included
in baseline stock or the run has an omission/double-count.

The schedule uses a manageable synthetic sample and positive calibration weights;
it does not create 1.34 million physical rows in any year. For each
production/report-only schedule year:

- the number of donor units is the frozen donor predicate's row count, published
  before the truth floor and never chosen by the external population count or by
  a candidate;
- unit sampling preserves all members selected together;
- person weights are finite and positive;
- the sum of person weights equals the selected `G_schedule_target[y]` branch
  within a pinned numerical tolerance;
- age/sex and other composition margins come from the frozen donor artifact,
  never from Table V.A2, which has no public age/sex detail; and
- no unannounced ultimate-value or nearest-year fallback is allowed. A missing
  year is a hard failure.

**Composition is constant across activation years under this donor, and that is a
disclosed limitation rather than a modelling result.** One band is rescaled across
every activation year, so the schedule models no change in entrant composition
over the window. Design law C1 already prohibits an unbound composition trend;
§5.5 and the artifact's `disclosures` block publish the constancy explicitly.

Low-cost and high-cost Trustees series are separately named report-only
scenarios. The 75-year average is a disclosure, never a replacement for annual
values.

### 4.4 Donor and simulation unit

PENSIM2's family sampling exposes a real unit mismatch: the external control is
people, while the state to preserve may be a family. V1's unit is a **constructed
co-resident same-reported-entry unit**, not a claimed historical travel party.
O4 ratifies it, and the measured support is the reason:

- the donor pool is **1,155 person rows in 562 households**, ≈ 2.06 persons per
  arrival household (§2.2, measured this revision). A person-donor rule discards
  that structure; a unit rule keeps it at the cost of an effective sample of 562
  clusters — and §5.3a measures what that is actually worth.

Under the certified frame the construction is:

1. Start from the certified frame's household, linked by `person_household_id` →
   `household.household_id` (`data/deployment_frame.py:92-99` lists
   `person_household_id` among the guarded required columns; the nativity reader
   carries it through as `household_id`,
   `data/nativity_frame.py:502-547` @ `29aa8c6`).
2. Select foreign-born recent-arrival people with the same
   `(source_year, PEINUSYR)` band classification — the vintage-keyed predicate
   of §2.2, never a pooled-vintage code.
3. Preserve only links unambiguously resolvable from the frame's own household
   structure when both endpoints are selected. Arbitrary spouse/parent pointers
   are unavailable and remain unresolved.
4. Assign a new `arrival_unit_id`; never expose either the household ID or the
   person ID of the source frame as a synthetic person or household identifier.

A spouse, child, or parent who is native-born, entered in a different band, or is
absent from the frame household is not cloned. The entrant may retain an observed
marital/parental state with a named `relation_outside_entry_roster` marker, but no
related synthetic row or relationship ID is invented. This is the immigration
relationship-closure invariant of §3.3, not a 3h-certified claim.

Two amendments the referee round adds, both because **no engine backstop exists**:

- **O4-a — the closure check is a post-build re-validation, not only a
  builder-side one.** The seam validates column presence and `person_id`
  uniqueness (`engine/loop.py:162-168`), the `year - 1` coordinate (`:236-239`)
  and cross-frame ID collisions (`:242-250`); it never checks a relationship
  endpoint. The birth path *does* guard its analogue, at materialization time,
  inside the loop (`engine/steps.py:479-484`), and there is no equivalent for an
  arrival-unit link. The closure check must therefore run **again over the
  composed schedule mapping**, after the merge with the PSID opener frames and
  immediately before `projection_metadata()` is handed to the engine. Same-year
  merges are exactly where an endpoint can be lost.
- **O4-b — "never identifies a travel party" becomes a schema prohibition, not
  prose.** The frame carries `arrival_unit_id` and unit size, and carries **no**
  field naming a relationship type between two entrant rows unless both endpoints
  are scheduled in the same or an earlier year.

Sampling whole units while calibrating person totals requires an explicit rule for
within-unit weights. The binding invariant is **one common simulation weight for
every member of an arrival unit**, with a calibration algorithm that reproduces
person margins; under the reweighting rule of §4.3 that is satisfied by a single
per-year scale factor applied to every donor row. Because the unit weight is
common, modelling later exits **by person** would make it incoherent; an exit law
must be unit-consistent or must re-open O4. The floor ceremony prices the unit
that is selected, and §5.3 requires household clustering because the split object
is the household.

### 4.5 Characteristic assignment

The fitted donor artifact preserves, at minimum, whatever the pinned frame
actually carries for the selected people. On the certified frame at `29aa8c6` the
reader materializes:

- `age` at the survey date, and derived `entry_age = max(age - lag, 0)` where
  `lag = source_year - arrival_year` (`data/nativity_frame.py:395`);
- `is_female`;
- `PENATVTY` country of birth, label-verified against CPS ASEC **Appendix I,
  "Countries and Areas of the World"** — `057 = United States`
  (`data/nativity_frame.py:97`), with the outlying-area codes at `:98-104`;
- `PRCITSHP` citizenship status, five value labels transcribed verbatim from the
  2024 dictionary at position 147 (`data/nativity_frame.py:82-88`), of which
  **codes 2 and 3 are NATIVE** — born in PR/outlying areas, and born abroad of US
  parents. Treating them as foreign-born would overstate the margin;
- `PEINUSYR` grouped year of entry, with `arrival_band(source_year, code)`
  (`:191`) and the vintage bin tables (`:144-148`);
- `A_MARITL`, already mapped through the seven Census ASEC recodes at
  `data/deployment_frame.py:65-73` and guarded at a 0.99 non-zero floor
  frame-wide (`:92-99`, enforced by `assert_columns_populated`, `:347-368`);
- the household weight, carried as the person weight exactly as
  `deployment_frame.load_certified_persons` computes it, so the two modules
  cannot disagree about the denominator; and
- `source_year`, the band, `arrival_year`, `arrival_lag_years`,
  `arrival_band_known`, and the full concept-map provenance.

**What the frame does not carry, and this design therefore does not claim:**
education and enrollment, source-region groupings beyond `PENATVTY`, disability
question items, employment/weeks/hours, and parity or birth history. Revision 4
listed all of these because ACS PUMS carries them; under the adjudicated donor
they are either unavailable or must be separately bound, and the design says so
rather than carrying a wish list. Any of them that a later artifact supplies
enters through §6.2 as a new binding with its own vintage, not as an assumed
column. The `A_MARITL` availability specifically must be measured **on the
recent-arrival subpopulation** before it is used: the 0.99 floor at
`deployment_frame.py:92-99` is frame-wide and is not conditional on nativity
(O8's refutation test).

These remain **interview-date stock characteristics**. They become entry-time
characteristics only after the `ArrivalStateBridge`; an identity bridge must be
named `stock_proxy` and is report-only. The artifact says so in those words
(`runs/entrant_schedule_v1.json` → `donor.provenance.stock_proxy_disclosure`).

The stock-proxy matching ladder begins with sex × derived entry-age band and then
uses whatever further support the frame provides, consistent with the
MINT/Duleep-Dowhan precedent that grouping should be by sex, age at migration and
source region. `DONOR_AGE_BANDS` (`data/nativity_frame.py:166-174`) are
deliberately **wider** than `deployment_frame.EARN_BANDS`, because the measured
single-band support bottoms out in the tail and the donor should be reported on
bands a floor could plausibly price rather than on bands that would need demoting
on sight. `PENATVTY`'s 161 distinct codes must be collapsed hard or demoted
outright (§5.4). The precise cells are selected and frozen before candidate
scoring. Fallbacks coarsen in a published order; they never cross a prohibited
concept boundary merely to fill a cohort. Every fallback count appears in the
audit.

**Design law C1 — no unbound composition drift.** Long-run composition is held at
the donor artifact's calibrated distribution unless a separately sourced, gate-
reviewed composition trajectory is bound. Trustees aggregate totals cannot be used
to manufacture one. Constant composition across the activation window is the
conservative absence-of-evidence fallback and a visible extrapolation limitation,
not an empirical forecast claim — and under this donor it is not merely permitted
but forced, because there is one band and one reference period (§4.3).

### 4.6 Schedule seed, IDs, and reproducibility

The schedule PRNG address is conceptually

```text
(schedule_seed, binding_manifest_hash, donor_artifact_hash,
 entry_year, unit_slot, member_slot, purpose_tag)
```

It is independent of `ProjectionRNGRegistry`. Unit selection, tie-breaking, and
any stochastic calibration use named `purpose_tag` values so adding one draw does
not shift another purpose's addresses. Under the reweighting rule of §4.3 the
realized v1 builder consumes **no** projection or schedule randomness at all,
which is the strongest form of this property and is separately tested at
`29aa8c6`.

After the full schedule is realized, IDs are allocated in stable order
`(entry_year, unit_slot, member_slot)` beginning at the pre-split global
`immigrant_id_floor` from §3.1. The builder stores the reserved-set digest, floor,
and allocation ledger, merges same-year frames without changing their existing
rows, and verifies global uniqueness and reserved-set disjointness before calling
the engine. Arrival-unit and household IDs use their own namespaces and may not
alias person IDs.

The metadata adapter omits `synthetic_id_allocator` so the loop creates it from
the combined universe. If another caller requires a supplied allocator, the
adapter asserts `allocator.next_id > max(combined_person_ids)` before period 1;
the loop's type check alone is insufficient (`engine/loop.py:258-262`). Note the
cost of the omission branch: the loop's own fallback allocator is built with an
**empty** `reserved_real_ids` (`engine/loop.py:255-257`), so omitting the metadata
allocator trades the range check for the loss of F2. O14-d requires the engine to
close this rather than leaving the design to choose between two gaps.

**Addressing law.** `PeriodContext.person_generator` looks up
`self.person_ordinals[person_id]` — — the lookup at
`engine/loop.py:107`, raising "no stable RNG ordinal for person" when absent
(`:109-111`), inside `person_generator` at `:100-113` — — and forwards to
`rng_registry.person_generator(period_index, module, ordinal)`
(`engine/rng.py:158-168`), whose spawn key is `(*sequence.spawn_key, child_index)`
(`engine/rng.py:85-99`). Its docstring states the law: "The ordinal, rather than
the identifier's representation, is part of the spawn key." **A person's RNG
address is their ordinal.**

Changing a source vintage, donor artifact, recent-arrival definition, or schedule
seed creates a new schedule identity, and the design promises no byte identity
across those scenarios. Within one schedule the global floor leaves every original
and pre-existing-opener sorted-ID ordinal unchanged, because ordinals are assigned
by `enumerate(sorted(all_initial_ids))` (`engine/loop.py:263-266`) over a set that
already contains every scheduled entrant. A full-population byte-identity claim
also requires the checked `run_real_person_ids ⊇ fitted_support_person_ids`
precondition in §3.2; stable ordinals alone never confer that claim on a subset
run.

Downstream RNG needs a separate isolation law. C16, fertility, and candidate-9
consume shared ordered generators, so merely adding entrants to their panels can
shift existing-person draws even though person ordinals are stable. A composite
adapter must run the baseline closed support in its original order with its
original generators, run entrant-only transitions under named disjoint
draw×period×person namespaces, and return one authoritative partitioned marital
result to the existing fertility/household reader slots. Any cross-domain marriage
or household reconciliation that can change baseline people is a distinct
report-only open-market product; it makes no byte-identity claim.

#### 4.6a The newborn-ordinal law — measured, not argued

Revision 4 wrote that the design "does not promise entrant or newborn byte
identity **across such scenarios**", where "such scenarios" are vintage, donor,
definition or seed changes. The comparison §8 and §9.2 step 5 actually depend on
— **closed run versus open run within one schedule** — is not in that set, and
under it newborn identity is broken by construction. This is now a measurement.

The mechanism is arithmetic on `len()`. Ordinals are pre-seeded over the whole
scheduled universe (`engine/loop.py:263-266`), and a row created during the loop
takes `person_ordinals[person_id] = len(person_ordinals)`
(`engine/loop.py:352-360`, the assignment at `:360`). So for a projection with `N`
scheduled immigrants, every synthetic birth receives an ordinal exactly `N` higher
than in the otherwise-identical run without them, and its mortality draw —
addressed per person at `engine/steps.py:121-132` — comes from a different stream.
No ID floor prevents this; the floor is orthogonal to it.

Run at `afd8f44` this revision (the script is in the report packet, not in the
repository; it schedules `N` immigrants at floor 10,000 over a one-real-person
roster with one scheduled birth in 2015, and compares the closed and open runs):

| `N` scheduled | newborn `person_id` closed → open | newborn ordinal closed → open | shift | newborn mortality bytes identical | original-person ordinal unchanged | original-person mortality bytes identical |
|---:|---|---|---:|:--:|:--:|:--:|
| 1 | 6 → 10001 | 1 → 2 | +1 | **no** | yes | yes |
| 7 | 6 → 10007 | 1 → 8 | +7 | **no** | yes | yes |
| 100 | 6 → 10100 | 1 → 101 | +100 | **no** | yes | yes |

Three findings, all measured:

- **L1 (the newborn-ordinal law).** Scheduled entrants shift every dynamically
  created row's ordinal by exactly the scheduled-entrant count, and therefore
  change its RNG address. **An open run makes no byte-identity claim for
  synthetic births even within one schedule.** This is now design law, stated
  here rather than left inside "such scenarios".
- **L2 (a second channel revision 4 did not name).** The newborn's **`person_id`
  itself relocates**, because the engine's fallback allocator starts at
  `max(all_initial_ids) + 1` over the *combined* universe
  (`engine/loop.py:251-257`), and `all_initial_ids` includes every scheduled
  entrant (`:242-250`). With an immigrant floor at 10,000 the birth is allocated
  at 10,001 rather than 6. Any consumer that identifies births by ID arithmetic
  is therefore wrong in an open run — which is exactly what
  `harness/m6_runner.py:986-987` and `:1022-1036` do today (§9.1).
- **L3 (the ID-floor claim, confirmed).** The original person's ordinal and its
  mortality draw bytes are **unchanged** in every case. Revision 4's §4.6 claim
  about existing-person ordinals is verified rather than assumed.

Because newborns enter the marital and household panels, L1 feeds the
shared-generator channel this section already flags. Whether the *gated* score
survives is a separate, answerable question: synthetic births are family-B open
additions and are report-only by ratified margin (`gates.yaml:5416-5420`), so a
gated surface computed on `holdout_ids` alone should be insulated. §9.2 step 5
requires that to be **measured on the real closed panel**, not asserted (O14-c).

### 4.7 Entry-frame schema and hard invariants

Every scheduled entry frame contains these conceptual groups:

| Group | Required fields |
|---|---|
| Engine | `person_id`, `year`, `age`, `sex`, `weight` |
| Entry identity | `synthetic_entry = true`, `entry_kind = "immigrant_cohort"`, `entry_year`, `arrival_unit_id`, `foreign_born = true` |
| Timing | `entry_timing_basis`, `age_timing_basis`, `reported_entry_band`, `arrival_year`, `arrival_lag_years`, `entry_year`; `years_since_entry` is derived, not stored as mutable state |
| Provenance | binding-manifest ID/hash, donor-artifact and arrival-state-bridge ID/hash, schedule ID/seed, donor-cell and fallback code, `source_year` and `PEINUSYR` code |
| Static/donor state | whatever the pinned donor actually carries for the selected person (§4.5) — never a column the frame does not have |
| Domain markers | `earnings_domain = false` and named entrant-domain flags for every composite adapter |

Two schema laws are new in revision 5:

- **`entry_kind` uses the implemented vocabulary**, not a parallel one:
  `immigrant_cohort`, `maternal_birth`, `realized_opener`, `incumbent`
  (`engine/entrant_schedule.py:73-77` @ `29aa8c6`). The three schedule classes
  are mutually exclusive; total schedule size is not an opener counter.
- **`anchor_wave` is prohibited on an immigration frame**, and the seam consumer
  that requires it is amended instead. `estimates/career.py:602` requires
  `("person_id", "year", "anchor_wave", "age")` on **every** scheduled frame and
  `:612-615` asserts `anchor_waves == {entry_year}`. `anchor_wave` means "PSID
  collection wave"; an immigrant has none, and supplying the entry year as an
  invented value would satisfy the assertion numerically while abusing the
  concept. §9.1 (P1) records the decision and the amendment it requires.

**Two invariants the engine's own head code forces, and revision 4 did not have:**

- an immigration entry frame carries **neither `nawi` nor `taxable_max`**, or the
  builder supplies both `nawi_by_year` and `wage_base_by_year` in projection
  metadata. Otherwise `advance_age` raises and aborts the period
  (`engine/steps.py:149-165`, the raise at `:156-158`);
- an immigration entry frame carries **`earnings_domain = false`** and its IDs are
  disjoint from every fitted domain. A frame marked in-domain without fitted state
  raises at `engine/earnings_domain.py:217-225`; a frame that reaches the fitted
  route without `u_w`/`realized_earn_2014` raises at
  `engine/forward_earnings.py:1421-1436`.

Before engine invocation the builder hard-checks:

- mapping keys are integer entry years in the bound projection range (§4.3a), and
  `start_year < entry_year <= end_year` as the seam requires
  (`engine/loop.py:228-232`);
- each frame has exactly `year = entry_year - 1` (`engine/loop.py:236-239`);
- pre/post-aging age identities match decision O2;
- person IDs are finite integers, globally unique, start no lower than the frozen
  `immigrant_id_floor`, and are disjoint from `reserved_real_person_ids` and every
  pre-existing scheduled ID — **the seam does not check the reserved set for
  scheduled entrants (§3.1), so this is the only place it is checked**;
- for every active certified earnings adapter, the literal assertion
  `immigrant_ids ∩ adapter.domain_person_ids == ∅` holds; the
  `earnings_domain = false` marker is not a bypass for fitted membership. This is
  implemented as an active check at
  `engine/entrant_domains.py:164` @ `29aa8c6`, not a comment;
- the pre-split namespace floor is unchanged after every gate/subset operation,
  and any full-population byte-identity claim separately satisfies
  `run_real_person_ids ⊇ fitted_support_person_ids`;
- no dynamically created row's identity is claimed to be stable between a closed
  and an open run (§4.6a, L1/L2);
- all relation endpoints are either scheduled no later than the relation's
  materialization year or explicitly marked outside-roster, **re-validated over
  the composed mapping** after the opener merge (O4-a);
- weights are finite, positive, and reconcile at person and unit level;
- every required downstream state is supplied by the state bundle, not merely a
  frame column that a later merge will erase (§3.4);
- no donor future outcome or post-cutoff gate input is present; and
- every source, parser, derived artifact, and schedule payload matches its bound
  hash.

Any failure aborts before period 1. There is no nearest-year, nearest-vintage,
native-donor, legal-status, or fabricated-history fallback.

Every entrant adapter derives `years_since_entry = context.year - entry_year` at
read time. `advance_age` does not update that field, so a mutable carried counter
is prohibited.

### 4.8 `EntrantStateBundle`

The state bundle is atomic by scheduled person ID and contains:

| Native support object | Purpose |
|---|---|
| `entry_frames_by_year` | The exact frames sent through the seam. |
| `entrant_marital_seed` | Entry state/history, risk-set start year, relation IDs only for roster-present people, and entrant-domain marker. |
| `entrant_household_seed` | Arrival-unit household links, household state, and entry-year exposure mask. |
| `entrant_disability_seed` | Survey-concept indicators plus the explicitly estimated mapping to any entrant disability state. |
| `entrant_fertility_seed` | Prior parity/birth-history state, its source/uncertainty, and an exposure-start rule; absent a bound bridge the entrant is excluded from fertility risk. |
| `entrant_earnings_seed` | Current-spell entry employment/earnings state, censored/unknown prior U.S.-covered history, any entrant-specific lag state, and normalization provenance. |
| `entrant_claiming_seed` | `claimed`, `claim_age`, `claim_year`, prior-coverage/insured-status provenance, and an eligibility-domain marker. |
| `entrant_relationship_roster` | Parent/spouse/child endpoints and the first year each endpoint can materialize. |
| `entrant_audit` | Donor support, fallback, imputation, weight, universe, and hash records. |

The packet must be coherent. State surfaces come from the same donor unit unless
a separately fitted joint imputation is named and validated. Independent
hot-decks for education, marriage, disability, and earnings are rejected because
they can construct combinations absent from the observed support while still
passing marginal checks.

The packet includes only state through entry and the minimum pre-entry history
needed to define a downstream covariate. It never contains realized post-entry
outcomes. Foreign earnings may inform education/occupation matching if a future
source supports it. Because reported year of entry does not identify first entry,
prior U.S. Social Security covered earnings are **unknown/censored**, not zero.
A separately named first-entry-only scenario may set them to zero only with an
adjudicated identification rule. Under the adjudicated donor there is no such
rule available — `PEINUSYR` carries no first-versus-most-recent disambiguation,
so repeat entry is bound **not identifiable** (O12-d) — and insured-status and
benefit outputs are therefore **excluded, not merely suppressed** (§4.9a, E1–E3).
In v1 the `entrant_claiming_seed` carries a pre-set `claim_age` sentinel and an
eligibility-domain marker, so `engine/steps.py:411-413` never selects an entrant;
it does not carry an insured-status determination, because no function in
`src/populace_dynamics/ss/` can make one.

### 4.9 Downstream module-state contract

| Existing step | What an entrant hits at `afd8f44` | Entrant analogue | Certification boundary |
|---|---|---|---|
| Mortality | Age/sex draw at the entry age, before aging (`engine/steps.py:113-134`, per-person addressing at `:121-132`) | **Entrants enter this domain.** O2 defines first-year exposure at the aggregate control, not the person | Mortality drift is already report-only; applying it to entrants is not newly certified. Emigration may not be encoded as excess mortality |
| Aging | Deterministic `age += 1` and `year` write (`engine/steps.py:137-166`, `:147-148`), plus the NAWI/wage-base roll at `:149-165` | **Entrants enter this domain.** The frame must satisfy the §4.7 `nawi`/`taxable_max` invariant | Plumbing only; the entry-age convention, not the function, is the new law |
| Marital core | Certified builder **discards the live frame** (`engine/panel_builders.py:164`) and inner-joins certified attrs to the anchor (`:169-176`); an entrant is not in the panel | An entrant-side panel builder supplies one admissible entry seed and risk-set start. A production open-panel adapter may combine markets only in a report-only run | Candidate-16's PSID certificate does not transfer to immigrants or to cross-domain matching. Closed-panel scored outputs must remain unchanged |
| Fertility | Risk set is `holdout_ids = state.marital_ids` (`engine/assembly.py:325`), so entrants are outside it **by construction**; but `engine/steps.py:539` falls back to the whole roster when a caller omits `holdout_ids` | Entrants excluded from fertility risk until a bound parity/history seed and an entrant-aware kernel exist. The risk set must be passed **explicitly** (O13-c). Later maternal births obey the 3h live-roster guard (`engine/steps.py:479-484`) | No parity-zero default and no absent mother. Entrant fertility is blocked/report-only pending O13 |
| Disability | `engine/disability.py:56-60` filters `person_years` to `holdout_ids` on a PSID-built panel; entrants are not in the panel at all | A separately estimated entrant initializer/forward law. ASEC/SIPP items are never relabelled as realized PSID M4 status | M4 reproduction support and certificate stay unchanged. Entrant disability is a successor-gate surface |
| Earnings | Entrants are outside `domain_person_ids` (`engine/earnings_domain.py:150-159`) so `apply_earnings` pins `earnings = 0.0` (`engine/steps.py:296-299`, `:356`) forever; marking them in-domain raises (`earnings_domain.py:217-225`, `forward_earnings.py:1421-1436`) | Entrants remain `earnings_domain = false`. A separate immigrant-entrant generator owns current-spell entry earnings and all later entrant earnings until a future handoff law is designed. Prior U.S.-covered history remains censored unless O12 supplies it | No fake 2014 earnings, `u_w`, `gen_earn_w2`, or `gen_earn_w4`; the §2.8.3a generator is untouched and its certificate does not transfer |
| Claiming | **Unfenced.** `apply_claiming` requires only `{"age","sex"}` and draws a claim age for every unassigned person with `age >= 50` (`engine/steps.py:402-413`, selection at `:411-413`) — no insured-status, quarters-of-coverage, AIME or PIA test, and `src/populace_dynamics/ss/` has no such function (§4.9a) | An eligibility-domain adapter, **or** a pre-set `claim_age` sentinel on `entry_kind == "immigrant_cohort"` rows so `:411-413` never selects them. Implemented at `engine/entrant_domains.py:154`, `:287` @ `29aa8c6` | No unconditional claiming draw; entrant claims and benefits are blocked/report-only until O5/O12 and an eligibility gate |
| Household composition | PSID-keyed cached panels; `_merge_period_columns` drops state columns and left-merges (`engine/assembly.py:174-192`, `:187-189`, `:190-192`), leaving an absent entrant `NaN` on every household column | An entrant-side native panel starts exposure at entry, carries arrival-unit links, and makes no link to an absent person | Candidate-9's PSID certificate does not transfer. Open-market effects on existing people are report-only |

**Entrants enter exactly two domains — mortality and aging — and every other
exclusion is reported as a suppressed count, never as a zero.** An excluded
entrant is *outside the estimand* for that domain; it is not a person modelled as
having no children, no disability and no claim. The distinction is the whole point
of the refusal, and the built artifact publishes the counterfactual each exclusion
prevents rather than asserting the exclusion abstractly
(`runs/entrant_schedule_v1.json` → `exclusions`; on the 11,550-row built schedule,
**1,350** rows would have drawn a claim age and **3,830** would have entered
fertility risk without the adapters).

#### 4.9a The oracle's insured-status gap — a hard exclusion (O12)

The statutory oracle **silently supplies the wrong answer rather than refusing**,
and this is the reason entrant benefit output is excluded rather than merely
disclosed:

1. **There is no insured-status test anywhere in the stack.**
   `src/populace_dynamics/ss/` is 747 lines across three files
   (`__init__.py` 43, `benefits.py` 349, `params.py` 355). Its public functions
   are `creditable_history`, `indexed_history`, `aime`, `pia`, `early_reduction`,
   `delayed_credit`, `age62_monthly_benefit`, `spousal_early_reduction`,
   `spousal_benefit`, `survivor_reduction`, `widow_benefit`, and
   `widow_benefit_survives_remarriage`. A grep of `ss/` for
   `quarter|insured|coverage_credit` returns **nothing**. Quarters of coverage and
   the 40-QC fully-insured test (§214(a)) are not modelled.
2. **`aime()` zero-pads to 35 computation years and puts the obligation on
   callers.** `ss/benefits.py:100-117`:
   `top = sorted(indexed.values(), reverse=True)[:_COMPUTATION_YEARS]` (`:115`)
   then `top += [0.0] * (_COMPUTATION_YEARS - len(top))` (`:116`), with
   `_COMPUTATION_YEARS = 35` (`:61`). The docstring (`:105-112`) is explicit:
   "Years absent from the mapping contribute zero if selected — callers are
   responsible for only passing histories whose coverage supports that reading
   (415(b) counts every computation year, earnings or not)." That is statutorily
   right for someone who **is** insured. It is silently wrong for someone whose
   missing years are missing because they were not in the country.
3. **The career builder's coverage span is birth-anchored, not presence-anchored.**
   `estimates/career.py:1004`: `coverage_start = max(OBSERVED_START_YEAR,
   birth_year + 22)` with `OBSERVED_START_YEAR = 1968` (`:22`) and
   `end_year = min(claim_year, PROJECTED_END_YEAR)` (`:1003`,
   `PROJECTED_END_YEAR = 2022` at `:26`). Nothing in the span consults presence,
   nativity, or an entry year. For an entrant arriving at age 40, the ~18
   pre-arrival years between `birth_year + 22` and the entry year are
   indistinguishable from covered years with zero earnings, and enter the 35-year
   denominator on the same footing.
4. **The hazard is fenced today only by accident, and the fence is one line.**
   `estimates/career.py:1580-1581` excludes every person outside
   `earnings_domain_ids` as `"excluded_domain_incomplete"`. An entrant is never in
   that set, so O12's own remedy — "claiming/benefit outputs are suppressed" — is
   already true at head **for an unrelated reason**. The day an entrant earnings
   law lands, that fence opens and the zero-padding goes live in the same commit.

Therefore, as design law: **entrant benefit output (insured status, AIME, PIA,
claiming levels) is excluded — hard — until an insured-status function exists.**
Not disclosed; not caveated; excluded. The exclusion has three parts:

- **E1.** Any entrant reaching `build_career` must **raise**, not be filtered as
  `excluded_domain_incomplete`. The two conditions are semantically different and
  will diverge. The cheapest correct form is an `entry_kind`-aware precondition in
  `build_career_inclusion` that refuses a person whose coverage span begins before
  their entry year unless an O12 bridge is bound.
- **E2.** The gap is an **API** question as well as a data question: the AIME path
  needs a covered-years or presence-window argument, or a wrapper that refuses a
  history whose span exceeds the person's U.S. presence. Today the contract lives
  in a docstring, and there will be a caller who does not read it.
- **E3.** Prior U.S. covered earnings are **unknown/censored, never zero**, because
  reported year of entry does not identify first entry — and under this donor
  `PEINUSYR` carries no first-versus-most-recent disambiguation at all, so repeat
  entry is bound as **not identifiable** rather than left open (O12-d).

The scored M6 closed-panel run and an open-population production run are distinct
products. Entrant interactions may affect existing people's marriages, households,
and births in the open run, but those effects cannot be allowed to retroactively
change the frozen closed-panel gate or its certificate.

### 4.10 Emigration and net reconciliation

The v1 audit publishes, by year:

```text
ssa_stock_accounting_inflow_control
scheduled_entry_weight
trustees_gross_outflow_required
trustees_status_adjustment_reclassification
trustees_total_net_target
entry_only_minus_net_gap
universe_bridge_status
```

With no exit law, `entry_only_minus_net_gap` is expected and disqualifies any net
alignment claim. A chart may show what the Trustees total-net path would imply,
but no population stock produced by entry-only v1 is “aligned” to that path.

A successor emigration design must decide at least the exit timing/order, risk
population, age/sex/source/duration hazard, family versus individual exit,
return-entry identity, employment termination, household reconciliation,
accrued-coverage and overseas-benefit state, death-versus-exit observability, and
RNG addressing. Table V.A2 supplies aggregate outflow controls, not those hazards.

**Rejected for production:** feeding total net change through the entry seam and
calling the rows immigrants. If the referee authorizes a reduced-form
`net_entry_proxy` experiment, its metadata, report, and output columns must say
that exact name; it cannot enter `gate_imm`, family-unit evaluation, entrant
characteristic claims, or M7 accounting.

### 4.11 Fail-closed audit behavior

Every build writes a machine-readable audit before projection. The audit includes
source and derived hashes, retrieval/publication/observation dates, parser and
schema versions, schedule seed, the reserved-real-ID-set digest, frozen immigrant
floor and allocated ID ranges, per-year physical rows and weighted totals,
donor-cell effective sample sizes, fallback counts, calibration residuals,
unit-size distribution, state-bundle completeness, and all report-only/certified
labels. A gate build additionally records the split protocol, the band-mass table
`M_gate[band]`, the support/demotion ledger, the unit-mass check, and the
derived-artifact hash from §5.2.

Three audit lines are **required** by the referee round and were not in
revision 4:

- **A1 (O1-C2).** Publish `weighted_person_year_count` and
  `weighted_covered_earner_count` **partitioned by `entry_kind`**. The measured
  artifact of an entry-only v1 is a **denominator** effect, not a numerator
  effect: the benefit ledger consumes `inclusion.included`
  (`estimates/preparation.py:559`) and `estimates/career.py:1580-1581` excludes
  every out-of-domain person, so entrants contribute **$0 to aggregate benefits**;
  the revenue ledger consumes the whole projection with no domain filter
  (`estimates/preparation.py:574`, `estimates/ledgers.py:1032`), so entrants
  contribute **$0 to taxable payroll, contributions and the covered-earner
  count** but **do** add to `unweighted_person_year_count` and
  `weighted_person_year_count` (`estimates/ledgers.py:955-967`, the person-year counts at `:957-960` and the covered-earner counts at `:961-966`). The
  exact artifact is therefore: **the benefits/payroll ratio does not move; every
  per-person-year and covered-earner-share statistic falls.** That is a dilution
  artifact, and without A1 a reader would see it as an immigration result.
- **A2.** Publish the per-domain exclusion counts **and the counterfactual each
  one prevents** — how many rows would have drawn a claim age, entered fertility
  risk, and so on — so that an exclusion is auditable as a refusal rather than
  invisible as an absence (`engine/entrant_domains.py:244` @ `29aa8c6`).
- **A3.** Publish `entry_only_minus_net_gap` per year as a named line, never a
  quantity minimized toward zero (§4.10).

The builder refuses to run when a binding required by the selected run is missing
or mutable, a raw or derived hash differs, a required year is absent, a unit
crosses an unsupported concept, an outside-roster relation is assigned an ID, the
composed-mapping closure re-validation fails (O4-a), the namespace floor changes
after a split, or either `immigrant_ids ∩ reserved_real_person_ids` or
`immigrant_ids ∩ adapter.domain_person_ids` is nonempty. It also refuses:

- a full-population byte-identity claim when the §3.2 run-universe precondition
  fails, **and any byte-identity claim for dynamically created rows at all**
  (§4.6a);
- a resident-alignment claim when the universe bridge is absent (O11, P3);
- any entrant benefit, AIME, PIA or insured-status output (§4.9a, E1–E3); and
- an entry frame carrying `nawi` or `taxable_max` without both metadata series
  (§4.7), or any schedule year outside the bound horizon (§4.3a, P2).

Network access and runtime redownload are prohibited on a scored or production
run. The V.A2 reader already satisfies this: it reads only the committed,
hash-verified snapshot and fails closed on a digest mismatch of either the
snapshot or its capture manifest (`data/trustees_immigration.py:305`, `:332`
@ `29aa8c6`).

## 5. Evaluation and proposed `gate_imm`

### 5.1 Gate identity and estimand

`gate_imm` is a proposed **additive successor gate**. This document does not add
it to `gates.yaml`, choose tolerances, build a floor, or lock an artifact.

The candidate estimand is narrow:

> Conditional on the named recent-arrival resident-stock proxy drawn from the
> pinned `populace_us_2024` frame and that frame's survey universe, does the
> frozen donor/schedule procedure reproduce a **household-disjoint held-out**
> recent-arrival stock-proxy composition at its empirical noise floor?

This is not a gate on literal arrival-time state or on external cohort counts:
exact agreement with a forced control is tautological, and §4.3's reweighting
makes the control residual identically zero to floating point. Gate mode uses only
the donor-derived band masses of §5.2. It is not truth for gross arrivals, for
people who left or died before interview, for legal status, or for post-entry
trajectories.

**Which boundary governs.** `gate_imm` under this donor is **not an M6-boundary
gate**. Its truth is a 2024 reference-period cross-section
(`gates.yaml:3732`; the same pin restated at
`data/deployment_frame.py:43-62`, `reference_period` at `:61`) whose observations
post-date `T* = 2014` by a decade. It registers against the **`gate_w1` boundary
and lock** (`gates.yaml:3725-3734`, `:3737-3745`), whose lock ceremony completed
2026-07-12 on the same frame. The information-boundaries header states this
explicitly rather than leaving a reader to infer that a 2024 frame is admissible
under a 2014 boundary. Nothing scored here may enter or re-anchor the inherited M6
path; that prohibition is unchanged and is what the two-boundary rule protects.

### 5.2 The split and the leakage fence

**There is no temporal fence available, and the design says so instead of
implying one.** Revision 4's fence was five separately released annual ACS files
with 2010–2013 fit and 2014 held out. The certified frame has **one reference
period** (`gates.yaml:3732`), so there is no annual dimension to split on and no
out-of-time comparison to make. What replaces it is the ratified `gate_w1`
pattern, and only that:

- **Split object: the household.** `scripts/build_gate_w1_floors.py:163` states
  the rule and its provenance — "The split object is `household_id` (fix, the 2c
  couple-disjoint lesson)". `gates.yaml:3741` records the precedent as "a
  pre-registered gate on a 100-seed HOUSEHOLD-DISJOINT split noise floor".
  Members of one household are **never** split. Under O4 the household is also the
  correlation unit for every floor.
- **Fit on one side, score the other.** Build the donor and freeze the candidate
  artifact and surface on the fit side; generate the synthetic recent-arrival
  cross-section without reading any held-out person record or weight; score
  against the held-out side under the same predicate, concept map, universe and
  weight treatment.
- **The seed grid is the `gate_w1` grid**: 100 household-disjoint split seeds,
  frozen with the surface, so no favourable single split can define a PASS.

**Gate masses are band-native, not annual.** Revision 4's
`M_gate[reported_entry_year = 2014 - d] = q[d]` presupposed annual `YOEP`.
`PEINUSYR` is grouped and vintage-keyed (§2.2), so the gate scores **band
masses**:

```text
M_gate[band] = share of the fit-side recent-arrival pool in that band,
               computed under the vintage-keyed predicate only
gate_total_mass = 1
```

Revision 4's own rule at §5.2 — "any O3-pooled duration bin retains its explicit
bin label rather than inventing a single entry year" — is promoted from an
exception to **the default**. A band is never converted to an entry year for
scoring purposes. Splitting a band into annual cohorts is a declared
**schedule-realization** rule (`BAND_SPLIT_RULE`,
`data/nativity_frame.py:180` @ `29aa8c6`), never a donor or gate rule, and it is
un-gradeable against the survey itself; it is labelled as such wherever it appears.

Households are indivisible; truth and candidate each normalize to unit mass before
characteristic scoring; absolute total is not a gate cell. Trustees, Census, CPS
tabulations and every held-out record, weight, total or marginal are prohibited
from constructing `M_gate`; the held-out weights enter only truth scoring after
lock.

**What this split does and does not buy.** It is a **transport** test: it grades
whether the schedule procedure reproduces the frame it was built from. It cannot
detect composition drift over time, and a PASS must never be read as an
out-of-time claim. The successor that would upgrade the claim — fitting on ASEC
vintages at or before a boundary and holding out a later vintage — needs
additional vintages staged, and the frame's own two-to-three year entry bins blur
any such fence. Both facts are named here so the boundary of the claim is on the
face of the gate, in the `gate_w1` `covers`-block style.

**Donor refits are out of v1 and their trigger moves out of this repository.** No
exact-artifact certificate transfers across a donor refit; a refit product is
report-only until it runs its own ceremony. Under this donor the refit cadence is
**microcosm's**, not this design's, so the operative question is not "may we
inherit a certificate when we refit?" but "what happens to `gate_imm` when someone
else refits the donor?" §6.2 answers it with a donor-pin watch. See O9.

### 5.3 Floors before thresholds

The ceremony order is mandatory:

1. Using fit-side analysis only, freeze the recent-arrival predicate (vintage,
   codes, `foreign_born_only`), the donor/simulation unit, the household-disjoint
   split protocol and seed grid, calibration constraints, fallback limits, the
   concept map, the matching ladder, the `M_gate[band]` construction, the
   support/demotion rules, the unit-mass convention, gate cells, metrics and
   weighting rules — without candidate holdout results.
2. Construct a correlation-respecting real-vs-real floor from deterministic
   **household-disjoint** splits. Never split members of one household.
3. On fit-side pseudo-holdouts only, run the complete donor-selection,
   calibration, fallback and schedule pipeline across the registered seed grid,
   recomputing `M_gate` from that pseudo-holdout's fit side only. Freeze how
   candidate-pipeline variability combines with the truth-side floor; no
   favourable single split seed can define a PASS.
4. Publish, for every proposed cell, raw person count, **raw household count**,
   person-weight Kish ESS, **cluster/household-weight ESS**, denominator, and both
   truth-side and pipeline distance distributions. The binding support measure is
   the most conservative applicable unit/design quantity, **not person ESS alone**.
5. Prune, pool, or demote every cell that fails predeclared support or whose floor
   is unstable. Record each demotion; **do not widen a threshold to retain one.**
6. Price thresholds from the surviving empirical floors using a predeclared
   transform. No numerical tolerance is assumed by this design.
7. Run an operating-characteristic experiment on the surviving conjunction using
   predeclared degraded pseudo-candidates. If power is weak or the gate is
   near-tautological, **pause and redesign before any lock**. §5.3a makes this
   step mandatory and expected to fire.
8. Only then score the registered candidate and, if it passes, bind the exact
   artifacts, floor, registry, code commit and hashes.

**Two rules adopted by name from the same donor's precedent:**

- **The demotion criterion is `gate_w1`'s heavy-tail guard, not a weight cap.**
  `runs/gate_w1_floors_v1.json:20599` records the measurement and the remedy:
  household weights are highly concentrated (max ≈ 433k against a mean ≈ 2.3k), so
  "a mean+4*sd tolerance does not always cover the worst seed, so a NEW
  gate-eligibility criterion (the heavy-tail guard: tolerance >= floor max over
  the 100 seeds, report_reason `floor_max_exceeds_tolerance`) demotes exactly
  those cells". A cap reweights the donor; the guard demotes the cell. This
  repository has already litigated the choice once on this frame and chose the
  guard.
- **The ESS machinery is a build deliverable, not an assumed capability.**
  `kish_n_eff = float(w.sum() ** 2 / np.sum(w**2))` exists in exactly one place —
  `scripts/build_gate_w1_floors.py:1575`, published under `weight_concentration`
  at `:1729-1736` — and `src/` contains no effective-sample or Kish helper at all.
  The floors PR must lift it into a shared helper and add the cluster/unit-weight
  quantity step 4 requires. Nothing computes the second one today.

#### 5.3a The support measurement — taken, and adverse

The referee named the recent-arrival effective sample as "the single cheapest
measurement that would change this adjudication". Revision 5 takes it, from the
pinned blob, so that O10 is decided on a number rather than on an
order-of-magnitude prior. Measured this revision on
`populace_us_2024.h5` @ sha256 `c2065b64…f39c5`, over
`recent_arrival_donor(persons)` — 2024 vintage, code 28, foreign-born:

| Pool | Rows | Households | Weighted | Kish n_eff (persons) | Kish n_eff (household weights) |
|---|---:|---:|---:|---:|---:|
| Frame-wide (all persons) | 166,302 | 57,240 | 340.009 M | **14,327.8** | — |
| Donor: 2024 / code 28 / foreign-born | 1,155 | 562 | 2.345 M | **156.1** | **82.0** |
| Donor + natives | 1,185 | 579 | 2.430 M | 163.4 | 85.3 |
| Donor, codes 27+28 | 1,671 | 806 | 3.316 M | 215.7 | 110.5 |
| All-vintage codes 27+28 (the referee's pool) | 3,835 | 1,866 | 8.996 M | — | — |

The frame-wide figure **reproduces the committed one** —
`runs/gate_w1_floors_v1.json:72` records "Kish n_eff ~ 14.3k of 166k nominal" —
which is the check that the measurement is the same quantity the precedent uses.

Per proposed A1 cell, on the same donor:

| Cell | Rows | Households | Kish n_eff (persons) | Kish n_eff (household weights) |
|---|---:|---:|---:|---:|
| 0–17 female | 128 | 110 | 23.6 | 18.5 |
| 0–17 male | 138 | 104 | 31.7 | 23.6 |
| 18–24 female | 60 | 57 | 8.0 | 7.6 |
| 18–24 male | 89 | 81 | 10.5 | 9.4 |
| 25–34 female | 187 | 178 | 36.6 | 36.0 |
| 25–34 male | 158 | 134 | 30.5 | 25.5 |
| 35–44 female | 92 | 89 | 10.9 | 10.8 |
| 35–44 male | 111 | 103 | 13.0 | 13.0 |
| 45–54 female | 51 | 50 | 7.2 | 7.2 |
| 45–54 male | 53 | 51 | 7.2 | 7.2 |
| 55–64 female | 25 | 24 | 6.9 | 6.0 |
| 55–64 male | 26 | 25 | 2.8 | 2.7 |
| 65+ female | 25 | 25 | 5.1 | 5.1 |
| 65+ male | 12 | 12 | 2.8 | 2.8 |

**Read this before designing the surface.** The best cell in the proposed
fourteen has a clustered effective sample of **36 households**; nine of the
fourteen are **below 14**; two are **below 3**. The pool as a whole is 82
effective household weights. The honest consequence, and it is now a
pre-registration rather than a prediction:

- **O10-c is binding: step 7's operating-characteristic pause check is mandatory
  and is expected to fire.** A `gate_imm` whose surviving surface is two or three
  cells is the likely outcome, and the design pre-commits to reporting that rather
  than widening thresholds to keep a table.
- **Pooling bands is the only lever that buys support, and it costs vintage
  coherence.** Codes 27+28 raise the pool from 82 to 110 effective household
  weights while mixing two arrival windows whose edges differ by vintage (§2.2,
  finding 1). Neither side of that trade may be taken silently; the floors PR
  must price both and record the choice with its reason.
- **Sex splits are the first thing to demote.** Collapsing sex within each age
  band is the cheapest support gain that costs no vintage coherence at all, and
  it should be the pre-registered fallback rather than a post-hoc rescue.

### 5.4 Candidate gate surface

The floor ceremony may consider these predeclared families. Every family is
band-native and none may be scored on a concept the pinned frame does not carry
(§4.5):

| Family | Candidate observables | Candidate metric | Measured support |
|---|---|---|---|
| A1 Demographic | derived entry-age band × sex shares of the recent-arrival pool | total-variation or weighted absolute-share distance | 14 cells; rows 12–187; **clustered n_eff 2.7–36.0** (§5.3a) |
| A2 Nativity share | foreign-born share within age band | total-variation distance | 7 cells over the whole frame; the widest support in the surface |
| A3 Band composition | mass by `(source_year, PEINUSYR)` band | total-variation distance | thin by construction; presumptively report-only |
| A4 Source region | broad region of birth, `PENATVTY` collapsed | total-variation distance | 161 raw codes — **must be collapsed hard or demoted** |
| A5 Unit structure | arrival-unit size distribution | unit-weighted total-variation distance | 562 households; the correlation unit itself |

Fine source-region, single-age, high-order family and any earnings or education
cells are **presumptively report-only**, and under §4.5 the last two are not
available from this donor at all. The final registry contains only cells that
clear the floors.

`entry_age = max(age - (source_year - arrival_year), 0)` is a **derived proxy**
and `arrival_year` is a band midpoint under a declared rule; neither is literal
duration or age at arrival, and neither can certify O12's arrival-state bridge.
The constructed unit is a co-resident same-band unit, never a claimed historical
travel party.

### 5.5 Report-only evaluation

The following are useful but are not gate truth:

- the entrant schedule's own alignment ledger — control, scheduled weight,
  residual, and `entry_only_minus_net_gap` per year;
- 2026 Trustees low-cost/intermediate/high-cost positive stock-accounting
  inflows, outflows and total-net paths;
- the 2023 Census National Population Projections main/high/low/zero immigration
  corridors;
- CPS ASEC published foreign-born tabulations, as a check on the frame's
  **uncalibrated** nativity margin. The frame's measured foreign-born share is
  **17.96 %** (23,732 rows, 61.075 M weighted), and because no nativity column is
  a calibration target (`data/deployment_frame.py:92-99`) that share is a free
  consequence of the L0 reweighting. Whether it is high, and by how much, is
  **unresolved**: no published external figure was obtained. It is a motivation
  for scoring a nativity margin; it is not yet evidence of a defect, and this
  design will not quote a comparison it has not opened; and
- foreign-born population stocks, dependency ratios, AIME/PIA, DI, claiming,
  household and benefit outputs — all suppressed for entrants under §4.9a.

The Census “zero immigration” scenario is especially easy to misstate: its method
sets gross foreign-born immigration to zero while leaving emigration and net
native migration in place, so net international migration may be negative.
Agreement with any Census corridor is a cross-model comparison, not validation.

### 5.6 What a PASS would and would not certify

A `gate_imm` PASS could certify only:

- the exact donor artifact, concept map, schedule procedure, split protocol, seed
  protocol, and surviving registry named in the lock;
- reproduction of the named household-disjoint held-out recent-arrival
  stock-proxy composition within floor-priced thresholds; and
- deterministic conversion of that artifact into seam-valid entry frames and
  **structural/schema completeness** of the packet fields exercised by the gate.
  It would not substantively validate latent histories or module-native mappings.

**The disclosure that makes the claim honest (O16-c).** The joint surface
`gate_imm` scores is itself uncertified, and this repository has already said so
in writing about the same frame. `runs/gate_w1_floors_v1.json:72`: populace
calibrates the certified frame to national admin **totals**, so marginal totals
ride on a certified target, but "the age x sex x marital and household-size JOINTS
family A scores are CPS-ASEC joints as reweighted by the L0 sparse refit (Kish
n_eff ~ 14.3k of 166k nominal); they are **NOT in populace's calibration loss and
ride UNCERTIFIED**. Family A certifies transport CONSISTENCY to those joints, not
their external truth." The nativity joints are in strictly weaker shape than that
sentence describes: it covers age × sex × marital and household size, so the
nativity joints' calibration status is **unestablished** rather than
known-uncertified, and establishing it is a microcosm lookup (P3). Any `gate_imm`
PASS statement must therefore say, **at the same prominence as the headline
claim**, that it certifies transport consistency to the certified frame's
nativity composition and not that composition's external truth. This is the
gate_m6 amendment-1 candour standard (`gates.yaml:5384-5396`) applied to this
gate.

A PASS would not certify gross-flow truth, the Social Security-area→resident
bridge, the frame's own universe definition, emigration, legal status,
current-vintage refits, composition across the activation window, entry-year
mortality exposure, donor representativeness for people who left or died before
interview, any post-entry transition, any interaction with the closed population,
or any Social Security eligibility or benefit result.

It also would not modify or extend the M6 certificate. Entrants remain family-B
open additions under the limitation at `harness/m6_reporting.py:71-74`, the
explicit immigrant person-row bridge at `harness/m6_reporting.py:104-118`, and the
family-B ledger published by `build_entrant_diagnostics` at
`harness/m6_reporting.py:277-318` (`"gated": False` at `:300`, `truth_basis` at
`:317`), until a later ratified gate says otherwise. Note that the gate margin and
the runtime disclosure **agree in content but are not the same string**:
`gates.yaml:5416-5420` reads "The closed-panel holdout (§4.8) certifies the
dynamics of the T*-present population only; entrants, births, and open-panel
margins are report-only", while `harness/m6_reporting.py:71-74` reads "The gate
covers the closed panel only; synthetic births, immigrant cohorts, and other open
additions remain report-only."

## 6. External bindings

### 6.1 Manifest contract

Every external or derived input selected for a run is represented by a field-
level manifest entry, following the sibling §2.8.10 pattern. Each entry must
contain:

- stable binding ID and semantic version;
- source agency, exact report/file title, table/section, scenario and columns;
- observation universe, reference-period convention, units, and covered years;
- information date, publication/release date, retrieval timestamp, canonical URL,
  and raw SHA-256;
- parser name/version, ordered source-field map, unit conversion, rounding rule,
  missing-year behavior, and universe transformation;
- derived artifact schema, row count, minimum/maximum year, SHA-256, and immutable
  artifact location;
- consuming component and whether use is gated, alignment-only, report-only, or
  blocking; and
- explicit alternatives rejected or still open.

An implementation factory must take no unbound source arguments. It resolves
repository-root-relative immutable artifacts, checks every raw and derived hash,
checks the declared time range and schema independently, and returns the ordered
binding objects. No scored or production run may fetch a source over the network.

This design creates no raw or derived artifact, and invents no hash. Two of its
sources are nevertheless **already acquired and hash-pinned by other work**, and
their digests are quoted here rather than invented: the Table V.A2 snapshot
(`5dfd05e5…89da`, §2.4) and the certified deployment frame
(`c2065b64…f39c5`, `gates.yaml:3729`). For every source still marked **UNBOUND**
in §6.2, `raw_sha256` and `derived_sha256` remain **required lock-ceremony
fields** and stay blocking until an acquisition PR records the actual bytes.

### 6.2 Binding ledger

Rows marked **ACQUIRED** name bytes that exist and are hash-pinned. Rows marked
**UNBOUND** name a source that has not been selected. `P1`–`P4` are the
prerequisites in §0.

| Binding ID | Exact source and vintage | Fields/transformation | Consumer and status |
|---|---|---|---|
| `ssa_tr2026_v_a2_components` | **ACQUIRED.** SSA, *[The 2026 Annual Report of the Board of Trustees of the Federal Old-Age and Survivors Insurance and Federal Disability Insurance Trust Funds](https://www.ssa.gov/OACT/TR/2026/tr2026.pdf)*, §V.A.3, and Supplemental Single-Year Table V.A2, “[Immigration Assumptions, Calendar Years 1940–2100](https://www.ssa.gov/oact/TR/2026/lr5a2.html),” assumptions set Feb. 2026, report released June 9, 2026. Snapshot `data/external/snapshots/trustees_va2_vintage1/trustees2026_lr5a2.html`, sha256 `5dfd05e5c5d4bbe413dd97f2256db24d5595e561623455edca3761bbfece89da`, 326,209 bytes, HTTP 200, retrieved 2026-09-06T14:55:07Z; capture manifest and `data/external/trustees2026_lr5a2.source.provenance.json` beside it. All @ `29aa8c6`. | Annual LPR inflow/outflow/status-adjustment/net; temporary-or-unlawfully-present inflow/outflow/status-adjustment/net; total net; thousands→persons; retain row class, estimate footnotes and rounding. Four published accounting identities asserted per row at ±2 thousand (`data/trustees_immigration.py:357`); 311 rows across four scenario sections. `positive_inflow` (`:144`) is the only control accessor; there is no net-change sizing accessor. | Positive-inflow control and net reconciliation. Report-only until the universe chain (P3), the timing bridge (O2) and an exit design exist; **prohibited as gate-estimation data**. |
| `ssa_tr2026_v_a2_sensitivity` | Same report/table/vintage/snapshot, low-cost and high-cost alternative sections (`alt_1`, `alt_3`). | Same component schema; never substitute 75-year average or ultimate value for annual rows. | Report-only scenario sensitivity. |
| `ssa_area_to_census_resident_bridge` | **UNBOUND.** Must reconcile the 2026 report's Social Security-area glossary definition to the Census resident universe with an exact source and vintage; the exact PDF page pin is **CONFIRM_AT_FETCH**. | Annual inclusion/exclusion or factor by population category; preserve an auditable raw-SSA series beside the bridged series. Identity is not an admissible silent default. | **BLOCKING** for a schedule labelled resident-population aligned. Leg 1→2 of the O11 chain. |
| `certified_frame_universe_definition` | **UNBOUND (P3).** The `populace_us_2024` build's own universe definition, in microcosm-build, not in this repository. | Name the frame's universe and its treatment of the institutionalized population, active-duty armed forces, and territories; record it in the manifest beside `CERTIFIED_PIN`. | **BLOCKING** for any resident-alignment claim and for the §4.11 A1 denominator audit, which has no denominator definition without it. Leg 2→3 of the O11 chain — the leg revision 4 presumed was the identity. **Cheapest of the three to close: a documentation lookup, and it discharges O7′'s successor question in the same trip.** |
| `certified_frame_nativity_donor` | **ACQUIRED.** `populace_us_2024.h5`, sha256 `c2065b642ab00da74746afdfd9f06890e5f32f9b10bd6610ff236452d40f39c5`, build revision `populace-us-2024-sparse-l0-refit-57k-71a0887-national-only-20260701`, reference period 2024, 166,302 persons / 57,240 households. Pinned three ways: `gates.yaml:3728`, `:3729`, and `data/deployment_frame.py:43-62`. Reader `data/nativity_frame.py` @ `29aa8c6`. | `PENATVTY`, `PRCITSHP`, `PEINUSYR`, `source_year`, `age`, `is_female`, household weight and `person_household_id`. Vintage-keyed bin table `:144-148`; populated guard `REQUIRED_NATIVITY_COLUMNS` `:156-160`; predicate `recent_arrival_donor` `:395`; declared band-split rule `:180`. | **Primary donor and `gate_imm` truth**, registered against the `gate_w1` boundary and lock, never against `T* = 2014`. Never literal arrival-state truth. |
| `certified_frame_donor_pin_watch` | Derived from the row above. | The registered `gate_imm` names `artifact_sha256` and build revision. **Any frame bump — including one made in microcosm for unrelated reasons — invalidates the lock** rather than silently re-scoring against a different population. `gate_imm` carries its own pin and does **not** inherit `gate_w1`'s. | **BLOCKING** for a lock; see O9-c. |
| `projection_origin_population` | Existing realized 2014 M6 initial slice for the v1 path; a 2025/2026 resident baseline is an **UNBOUND** alternative. The pinned 2024 frame is an explicitly **rejected** origin (O15-d). | Bind `start_year`, population universe/artifact/hash, first schedule key, first-cohort disposition and continuous control interval. | **BLOCKING** for an origin other than the existing 2014 report-only open run; decision O15. |
| `m6_nawi_and_wage_base_series` | **UNBOUND (P2).** The `nawi_by_year` and `wage_base_by_year` metadata series consumed by `advance_age` (`engine/steps.py:149-165`). | Name each series, its source and vintage, and its **exact year coverage**. `advance_age` raises `"<key>' has no value for <year>"` at `:160-165` for any uncovered year, and raises at `:156-158` if a frame carries `nawi`/`taxable_max` without the series. | **BLOCKING for any horizon past 2022** — an execution blocker, not a reporting gap. Revision 4's binding table had no wage-index series at all. |
| `entry_timing_exposure_bridge` | **UNBOUND.** Must document each Table V.A2 inflow component's event/survival timing and the selected population-origin convention with exact report text and vintage. | Translate controls to opening-of-year exposure without applying source-year survival twice; bind scheduled and target-year age meaning. **Aggregate only** — no person-level status assignment, and no conditional code inside the mortality or aging slot. | **BLOCKING** for a production entry schedule; decision O2. |
| `estimates_seam_amendment` | **UNBOUND (P1).** A ratified amendment to `estimates/career.py` and `estimates/preparation.py`. | `career.py:602`/`:612-615` must stop requiring `anchor_wave` of an immigration frame; `preparation.py:332`/`:335-352` must stop inferring "native birth" from "non-reserved synthetic ID". §9.1 states which of the two admissible fixes this design takes. | **BLOCKING for any open run.** Without it the first-estimates pipeline raises on the first immigration frame it sees. |
| `stock_to_arrival_state_bridge` | **UNBOUND.** No cited cross-section identifies state at the arrival instant or everyone who subsequently left or died. | Must pin a duration/backcast law, survivor/stayer selection adjustment, reported-entry ambiguity treatment, repeat-entry identification, source and vintage. An identity mapping is labelled `stock_proxy` only. | **BLOCKING** for literal entry-time characteristics; decision O12. Under this donor the selection correction is **not identified from the donor at all**: `PEINUSYR` is a 2–3 year band and the frame is a single cross-section with no second observation. An external law is required. |
| `ss_insured_status_function` | **UNBOUND.** No quarters-of-coverage or §214(a) fully-insured implementation exists: `src/populace_dynamics/ss/` (747 lines, twelve public functions) has none, and `aime()` zero-pads to 35 computation years (`ss/benefits.py:115-116`, `_COMPUTATION_YEARS = 35` at `:61`). | Must supply an insured-status test **and** a presence-window argument or refusal wrapper on the AIME path (§4.9a, E1–E3). | **BLOCKING** for every entrant benefit output. The current failure mode is a **plausible non-zero PIA**, not a visible error. |
| `entrant_marital_household_history_initializer` | **UNBOUND.** Candidate evidence is the certified frame's own `A_MARITL` (`data/deployment_frame.py:65-73`), jointly observed on the same person row as nativity and already hash-pinned — strictly better than a separately matched second donor on both counts. | Map entry marital history/status, spouse/relations outside roster, household seed, exposure start and later entrant-only law jointly. Measure `A_MARITL` **on the recent-arrival subpopulation** first: the 0.99 floor at `deployment_frame.py:92-99` is frame-wide and is not conditional on nativity. | **BLOCKING** for entrant marital/household domains and every mixed market; decisions O4/O5/O14. |
| `entrant_disability_state_bridge` | **UNBOUND.** The certified frame carries no disability question items (§4.5); a source must be named before a mapping can exist. | Estimate entry state and an entrant-specific forward law without relabelling survey concepts as M4 status. | **BLOCKING** for entrant disability outputs; decision O5 and a successor gate. |
| `entrant_earnings_initializer_forward_law` | **UNBOUND.** The certified frame carries no earnings concept for this donor's purpose; source, universe and vintage are not selected. | Estimate partial-year current-spell state, lags/persistence and entrant-only forward earnings; `m6_projected_wage_index` normalizes dollars but supplies no behaviour. | **BLOCKING** for entrant earnings and downstream benefit outputs; decisions O5/O12 and a successor gate. **Landing this opens the accidental benefit fence at `estimates/career.py:1580-1581` in the same commit** (§4.9a); E1 must land first. |
| `cps_asec_dictionary_vintages` | **PARTIALLY BOUND.** CPS ASEC data dictionaries for the vintages the frame pools (2022, 2023, 2024) plus CPS technical documentation **Appendix I, "Countries and Areas of the World"** — the dictionary's own "See Appendix H" note is a stale cross-reference to the Source and Accuracy Statement. Read and encoded at `data/nativity_frame.py:82-107`, `:110-148` @ `29aa8c6`. | `PRCITSHP` five value labels (position 147); `PENATVTY` country codes (`057 = United States`); **`PEINUSYR` bin edges per vintage** — the top code differs by vintage, so the table is keyed on `(source_year, code)`. | **Donor provenance, not a diagnostic file.** This is O7 inverted (O7′). The bin edges and code labels are bound; what remains is naming the vintage binding **in the manifest beside `CERTIFIED_PIN`**, which the same microcosm lookup as P3 supplies. |
| `sipp_2014_wave1_entry_state` | Census, *[2014 SIPP Metadata All Sections v2](https://www2.census.gov/programs-surveys/sipp/tech-documentation/data-dictionaries/2014/w1/2014SIPP_Metadata_AllSections_v2.pdf)*; [Wave 1 raw directory](https://www2.census.gov/programs-surveys/sipp/data/datasets/2014/w1/); *[Source and Accuracy Statement, Wave 1](https://www2.census.gov/programs-surveys/sipp/tech-documentation/source-accuracy-statements/2014/sipp-2014-source-and-accuracy-statement.pdf)*. No SIPP artifact exists in `data/external/`. The directory is discovery evidence, not an immutable binding; exact filename/version **UNBOUND**. | Narrowed to **parity and birth history** — the one state the certified frame does not carry. Marital and employment state come from the frame instead. `TIMSTAT` is excluded from legal-status state. | **NON-BLOCKING for v1** (O8). Retained only as the successor question for O13, with which it must be resolved jointly. |
| `entrant_fertility_history_bridge` | **UNBOUND.** Candidate evidence must name exact SIPP fertility-history or CPS fertility-supplement files, variables, universe, observation years and release vintage. | Map prior parity/birth history and exposure start jointly with entrant family state; **never default parity to zero**. Exposure start binds to the entry year, and the design makes no claim about pre-arrival fertility. | **BLOCKING** for entrant fertility risk; decision O13. An entrant-aware kernel is a **new fit**, not a wrapper: the certified kernel's cells are `(age, min(parity,3), birth_decade)` (`models/family_transitions/components/fertility.py:80-86`) and there is no unknown-parity stratum. |
| `prior_us_covered_earnings_bridge` | **UNBOUND.** Reported year of entry does not establish first entry or prior U.S. covered earnings, and under this donor `PEINUSYR` offers no first-versus-most-recent disambiguation at all. | Identify repeat-entry/first-entry status, covered quarters and prior indexed earnings with a source, universe and vintage; otherwise retain censored/unknown. Repeat entry is bound **not identifiable** under this donor (O12-d). | **BLOCKING** for entrant insured status, claiming, AIME/PIA and benefits; decision O12. |
| `census_np2023_nim_corridors` | Census Bureau, *[Methodology, Assumptions, and Inputs for the 2023 National Population Projections](https://www2.census.gov/programs-surveys/popproj/technical-documentation/methodology/methodstatement23.pdf)* (Nov. 2023), migration pp. 8–14; Table 1 in the Main Series and each Alternative Scenario: [main](https://www2.census.gov/programs-surveys/popproj/tables/2023/2023-summary-tables/np2023-t1.xlsx), [high](https://www2.census.gov/programs-surveys/popproj/tables/2023/2023-summary-tables/np2023-t1-h.xlsx), [low](https://www2.census.gov/programs-surveys/popproj/tables/2023/2023-summary-tables/np2023-t1-l.xlsx), [zero](https://www2.census.gov/programs-surveys/popproj/tables/2023/2023-summary-tables/np2023-t1-z.xlsx). | Annual net international migration in thousands for main/high/low/zero; July 1 prior year–June 30 current year. Preserve scenario definitions: alternatives change gross foreign-born immigration, not every migration component. | Report-only cross-model corridors; never gate truth or a positive entrant control. |
| `m6_projected_wage_index` | Existing sibling design §2.7.6.3/§2.8.10: `I_bound[y]` is realized SSA NAWI through 2014 and `I_proj[y]` beyond, estimated only from `<=T*`. | Normalizes entrant earnings dollars only. Never use realized post-2014 NAWI on a scored path. Distinct from `m6_nawi_and_wage_base_series`, which is the engine's **execution** requirement rather than a normalization. | Reused by a future entrant-earnings initializer. No new external fetch and no certificate transfer to entrant earnings. |
| `acs_pums_annual_2010_2014_recent_arrivals` | **SUCCESSOR, not a v1 dependency.** Every URL, dictionary, Accuracy statement, `Last-Modified` header, erratum 87/97 and the 2013 same-sex married-couple user note are preserved verbatim in **Appendix A**. | Would buy annual `YOEP` resolution, replicate designs and a genuine temporal fence. | **Deferred.** Nothing in this repository reads ACS; adoption is a greenfield acquisition. If the fork is revisited, Appendix A is the specification and O3/O6/O7/O10 revert to their revision-4 text verbatim. |
| `emigration_duration_hazard` | **UNBOUND.** Table V.A2 supplies aggregate outflow counts only. The Duleep-Dowhan 2008 hazards and legacy model methods are research evidence, not a current operational binding. | Must identify age, sex, source grouping, time since entry, family/individual unit, re-entry treatment, universe and vintage. **And a delivery mechanism:** the only person-removal path in the engine is `apply_mortality` (`engine/steps.py:113-134`) inside a frozen eight-adapter order (`engine/loop.py:117-129`, `:297-350`), so an exit law needs an amendment to that order, not merely a hazard. | **BLOCKING** for explicit exits and any Trustees net-alignment claim; outside entry-builder v1. |

### 6.3 Binding-specific guards

**The V.A2 parser** must assert the caption verbatim, resolve all four scenario
sections by their in-table anchors (`alt_h`, `alt_2`, `alt_1`, `alt_3`), require
strictly increasing years per scenario, assert continuous annual coverage over the
bound schedule interval, assert units, and assert the source's own identities

```text
lpr_net       = lpr_inflow       - lpr_outflow       + status_adjustment
temporary_net = temporary_inflow - temporary_outflow - status_adjustment
total_net     = lpr_net + temporary_net
status_adjustment_lpr == status_adjustment_temporary
```

within the source's whole-thousand rounding, with the tolerance **sized as the sum
of the terms' rounding half-widths** rather than chosen to make the check pass. It
must not treat status adjustment as two events or as a new arrival, and it must
expose no accessor that would let net change size a cohort. All of this is
implemented and tested at `data/trustees_immigration.py:357`, `:423`, `:483` @
`29aa8c6`; the test file mutates the snapshot and the manifest in a temporary copy
and asserts each **fails closed**, and separately pins the unclosed-`<td>`
recovery, because a parser that silently restarted the cell would drop the
calendar year and mis-key every row without raising.

**The certified-frame donor extractor** must:

- resolve the frame by the pinned `revision` **and** verify `artifact_sha256`
  before reading it, and refuse to proceed on a mismatch — the pin is the
  estimand's identity (`data/deployment_frame.py:41-42`);
- enforce `REQUIRED_NATIVITY_COLUMNS` (`data/nativity_frame.py:156-160`). **No
  nativity column appears in `deployment_frame.REQUIRED_SOURCE_COLUMNS`
  (`:92-99`)**, so this guard is the only thing standing between a future zeroed
  column and a silently degenerate donor. The L0-sparse default zeroes untargeted
  inputs, and `assert_columns_populated` (`:347-368`) demonstrates the pattern for
  the columns it does cover;
- key every arrival band on `(source_year, code)` and **refuse to draw a donor
  from an unlabelled band** (`data/nativity_frame.py:429-438`, the raises at `:430-432` and `:435-438`), publishing the
  count of rows whose pair the labelled vintage's dictionary does not define
  (`vintage_domain_mismatch`, `:278`) rather than silently assigning them a year;
- restrict the donor to a **single ASEC vintage** unless a pooled draw is
  explicitly registered with its vintage-coherence cost priced (§5.3a);
- restrict the donor to the control's universe (`PRCITSHP ∈ {4,5}`) and publish
  the excluded native count and reason, because those people appear in neither
  V.A2 stock;
- publish the **uncalibrated** status of the nativity margin in words, not only as
  a flag; and
- name the band-split rule in the artifact (`BAND_SPLIT_RULE`, `:180`) and label
  every annual figure derived through it as un-gradeable against the survey.

The gate-derived artifact must assert its split protocol and seed grid, finite
nonnegative band masses summing to one within a pinned tolerance, and supported
bands only. Its provenance must contain no held-out record, weight, total or
marginal; each pseudo-holdout repeats the same assertions with only its fit-side
households.

**The schedule builder** must emit `entry_kind` on every row and derive provenance
counters from that column, **rejecting a frame that lacks it rather than falling
back to ID arithmetic** (`engine/entrant_schedule.py:292` @ `29aa8c6`). §4.6a L2
is why: in an open run the engine's fallback allocator relocates every birth ID
above the immigrant floor, so ID arithmetic is not merely fragile but wrong.

**The Census parser** must preserve its July-to-June event year and
resident-population universe. A calendar-year bridge to Trustees may be displayed
only as a named transformation with both originals retained. The “zero” scenario
may not be rewritten to zero net international migration.

## 7. Refereed resolutions O1–O16

**Status of this section.** Revision 4 posed sixteen open decisions. A referee
round adjudicated all sixteen against current head, refute-first, opening every
cited byte at both the revision-4 baseline and `afd8f44` and recording where it
could not resolve a question from the artifact. Revision 5 **folds those
resolutions into design law**. Each entry below carries: the resolution, quoted
from the round; the evidence that decides it, by `path:line` at the revision named
in the header; and — where the round said a question could not be decided from the
artifact — the **open item** and exactly what would close it.

The donor fork itself was adjudicated by the plan owner
(**certified-frame-first**) and was taken as settled rather than re-litigated.
Where a resolution changes under that branch, the entry gives the answer for that
branch and says what the ACS branch would have required, so that reversing the
fork costs a re-read rather than a re-review. Appendix A preserves the ACS text.

Fixed mechanics outside this list remain design laws: U1 nests schedule
uncertainty outside K engine draws, C1 prohibits an unbound composition trend, and
**L1–L3** (§4.6a) bind newborn identity in an open run.

### O1 — Positive SSA inflow, exit scope, and net proxy — RESOLVED (a), amended

> "**Recommended resolution: (a), amended.** Adopt the positive-inflow control,
> keep entry-only v1 report-only, and defer emigration — but add two conditions
> #218 does not state."

**Evidence.** The report-only clause costs nothing because it is already the
ratified posture: `gates.yaml:5416-5420` carries `margin: entrants_open_panel`,
the runtime disclosure agrees in content at `harness/m6_reporting.py:71-74`, and
`build_entrant_diagnostics` publishes it with `"gated": False` and
`"truth_basis": "no_psid_truth_for_family_b_open_additions"`
(`harness/m6_reporting.py:277-318`, `:300`, `:317`). Option (b) is **larger than
revision 4 admitted**: the only person-removal path is `apply_mortality`
(`engine/steps.py:113-134`) inside a frozen eight-adapter order
(`engine/loop.py:117-129`, `:297-350`), so an exit law is not expressible without
amending that order (§1.4).

**Folded, with both conditions:**

- **O1-C1 — the control's acquisition.** The round made this blocking: "The
  control is blocking on an acquisition PR that commits `trustees2026_lr5a2.html`
  … Until then §4.3's `G_ssa_stock[y]` has no bytes." **This condition is
  discharged.** The snapshot is committed and hash-pinned at `29aa8c6` (§2.4,
  §6.2), the parse asserts V.A2's four identities on 311 rows, and it reproduces
  revision 4's quoted table exactly. What remains is that those bytes live on an
  **unmerged branch**; merging them is a precondition of a build, not of this
  design.
- **O1-C2 — the audit's denominators.** "The v1 audit must publish
  `weighted_person_year_count` and `weighted_covered_earner_count` **partitioned
  by `entry_kind`**, because the measured artifact is a denominator effect, not a
  numerator effect." Folded as §4.11 A1, with the mechanism spelled out: benefits
  are domain-filtered (`estimates/preparation.py:559`,
  `estimates/career.py:1580-1581`) and revenue is not
  (`estimates/preparation.py:574`, `estimates/ledgers.py:1032`,
  `:955-967`), so entrants move denominators only. Without A1 a reader sees a
  dilution artifact as an immigration result.

**Open item — none.** The remaining work is a merge, not a decision.

### O2 — Entry-year timing, age, and mortality exposure — RESOLVED (a)

> "**Recommended resolution: (a), with the exposure adjustment made at the
> aggregate control, not the person.** Bind `entry_timing_basis =
> "opening_of_entry_year"`, keep the unchanged mortality/aging pair, and discharge
> the double-survival problem in the `entry_timing_exposure_bridge` by inflating
> the temporary/unlawfully-present component to an opening-of-year equivalent
> before it becomes `G_schedule_target[y]`. Branch (b) should be refused for v1."

**Evidence.** Activation concatenates and stably sorts at the top of the period
(`engine/loop.py:271-286`) strictly before mortality (`:297`);
`apply_mortality` draws one uniform per person with no exposure fraction
(`engine/steps.py:113-134`); `advance_age` does `age + 1` unconditionally
(`:147`) and writes the target year (`:148`). There is no hook between them, so
(a) is the only convention the unchanged engine expresses and (b) requires new
conditional code inside two of the eight certified slots — the one thing §8
promises not to do, bought for a precision the report-only estimand cannot use.

Two facts the round supplied that revision 4 did not use, both folded into §3.2:

- **The precedent already chose (a) and wrote down why**
  (`harness/m6_population.py:329-335`), and a different convention makes the
  composed schedule internally inconsistent at the exact concatenation point.
- **`advance_age` has a second obligation** — the NAWI/taxable-max roll at
  `engine/steps.py:149-165`, which did not exist at the revision-4 baseline and
  which raises when a frame carries either column without the metadata series.
  Folded as a §4.7 hard invariant.

**Open item — the inflation factor's identifiability.** The round's own
refutation test: "A demonstration that the aggregate inflation factor is not
identified from public Trustees text — that would make (a)'s bridge unbindable
and force (b) or a pause." `entry_timing_exposure_bridge` stays **UNBOUND** and
**BLOCKING** for a production schedule (§6.2) until that factor is derived from
the acquired V.A2 bytes or from named report text.

### O3 — Recent-arrival window and matching ladder — RESOLVED, band-native

> "**O3-a.** The recent-arrival predicate is `PRCITSHP ∈ {4,5} ∧ PEINUSYR ∈
> {27,28}` … Do **not** adopt a 0–4-year window, because the frame cannot express
> one … **O3-b.** The gate scores **band masses**, not annual entry-year masses …
> **O3-c.** Splitting a band into annual cohorts is a **schedule-realization**
> rule … **O3-d.** The correlation unit is the household."

**Folded — with one amendment the round could not have made**, because the build
that followed it measured two facts about the frame the round did not have:

- **O3-a is narrowed to a single vintage.** The round's `PEINUSYR ∈ {27,28}`
  predicate pools three ASEC vintages whose top codes mean **different arrival
  windows** — code 27 is 2020–2022 on the 2022 vintage and 2020–2021 on the 2024
  vintage (`data/nativity_frame.py:144-148` @ `29aa8c6`). One crosswalk over the
  pooled file mislabels arrival years. The predicate is therefore keyed on
  `(source_year, code)` and defaults to the 2024 vintage's code 28.
- **O3-a is further restricted to the control's universe.** `PEINUSYR`'s universe
  is everyone not born in the fifty states, so the band contains **natives** who
  appear in neither V.A2 stock — 30 of 1,185 rows. They are excluded
  (`data/nativity_frame.py:400`, `:443-444`).
- **The resulting support is smaller than the round's figure and the design says
  both numbers.** The round's 3,835 persons in 1,866 households is exact for the
  pooled predicate and is reproduced in §2.2; the donor the code builds is
  **1,155 rows in 562 households**. §5.3a decides O10 on the difference.
- **O3-b, O3-c and O3-d are folded verbatim** as §5.2's band masses, §1.2/§6.3's
  declared `BAND_SPLIT_RULE`, and §4.4/§5.2's household correlation unit
  (`scripts/build_gate_w1_floors.py:163`), with `(survey_year, SERIALNO)` mapping
  to `person_household_id` → `household.household_id`.

**Open item — the bin edges are bound; the vintage binding is not recorded in the
manifest.** The round listed the CPS bin edges as unverified. The build read the
2022/2023/2024 dictionaries and Appendix I and encoded them
(`data/nativity_frame.py:82-107`, `:110-148`), so the edges are now evidence.
What remains is naming the source ASEC vintage **in the manifest beside
`CERTIFIED_PIN`** — the same microcosm lookup as P3 (see O7′, O11-b).

### O4 — Person versus constructed same-reported-entry units — RESOLVED, units

> "**Recommended resolution: constructed co-resident same-reported-entry units,
> with one common simulation weight per unit, and the unit as the floor's
> correlation unit** — #218's provisional choice, ratified."

**Evidence.** The engine has **no household materialization for a scheduled
entrant**: `_merge_period_columns` drops state columns and left-merges
(`engine/assembly.py:174-192`, `:187-189`, `:190-192`), leaving an entrant `NaN`
on every household column — revision 4's §3.4 claim, still exact and
byte-unchanged. The one open-addition path that does carry household state copies
it **from a parent** (`engine/steps.py:485-503`), which has no analogue for a unit
arriving with no pre-existing member. And the measured structure says units: 2.06
persons per arrival household (§2.2).

**Folded, with both amendments** (§4.4): **O4-a**, the closure check is a
post-build re-validation over the **composed** mapping, because the seam validates
only `person_id`/`year` and the `year - 1` coordinate
(`engine/loop.py:162-168`, `:236-239`, `:242-250`) and never checks a relationship
endpoint — while the birth path *does* guard its analogue in-loop
(`engine/steps.py:479-484`); and **O4-b**, "never identifies a travel party"
becomes a schema prohibition rather than prose.

**Open item — the round's own flip condition, now decided by §5.3a.** The round
wrote: "A floors run showing 1,866 household clusters cannot support even the
coarsest §5.4 demographic cell — then person donors with report-only structure
become the only feasible branch, and O4 flips." The measurement is in: the donor
carries **562 households, 82 effective**, and the best A1 cell is **36 effective
household weights**. That is adverse to the *surface*, not to the *unit*: person
donors would inflate nominal n without changing the clustered design effect, so
O4 does **not** flip. What it decides is O10 and §5.4 — fewer cells, not a
different correlation unit. This design records that reading explicitly so the
floors PR does not re-derive it as a rescue.

Because the unit weight is common, an exit law that removes **persons** would make
it incoherent; §4.4 records that as a constraint on the successor emigration
design rather than leaving it to be discovered.

### O5 — Atomic state/history packet and post-entry laws — RESOLVED, with three subparts closed by code

> "**Recommended resolution.** Ratify the design's default (no hot-decks, no
> certificate transfer, entrants out of every unresolved domain) and additionally:
> **O5-a.** Record subparts 1–3 as **closed by code, with citations** … **O5-b.**
> Make the entrant claiming exclusion explicit rather than incidental … **O5-c.**
> Add `estimates/career.py` and `estimates/preparation.py` to §9.1."

**Evidence, folded into §3.5 and §4.9 with citations so a build does not
re-implement fences that exist:**

1. **Earnings — closed by code.** `initialize` runs once before the schedule
   (`engine/loop.py:203-214`, invoked at `engine/assembly.py:252-254`), so an
   entrant never reaches `materialize_initial_frame`. Membership comes from the
   fitted maps (`engine/earnings_domain.py:150-159`); `validate_domain` raises on
   any disagreement (`:217-225`); `apply_earnings` validates the whole frame
   (`engine/steps.py:218-232`) before masking (`:296-299`) and writes
   `earnings` unconditionally (`:356`); the fitted route raises without
   `u_w`/`realized_earn_2014` (`engine/forward_earnings.py:1421-1436`).
2. **Fertility — closed by code.** `holdout_ids = state.marital_ids`
   (`engine/assembly.py:325`) comes from a builder that discards the live frame
   (`engine/panel_builders.py:164`) and inner-joins certified attrs (`:169-176`).
   **Caveat now recorded:** `engine/steps.py:539` falls back to the whole roster
   when a caller omits `holdout_ids`.
3. **Claiming — NOT closed in the engine, and closed *differently* one layer
   down.** `apply_claiming` tests only age and sex
   (`engine/steps.py:402-413`, `:411-413`); `estimates/career.py:1580-1581`
   excludes out-of-domain people from the benefit ledger. So an entrant is a
   claimant in the panel and a non-person in the ledger. Revision 4 described an
   adapter that does not exist and did not notice the accidental one that does.
4. **The unnamed blocker.** `src/populace_dynamics/estimates/` did not exist at
   the revision-4 baseline (added 2026-07-25, `070cbb7`) and at head rejects an
   immigration frame outright — see O5-c, §9.1 and P1.

**O5-b is folded as a decision, not a hope.** The design takes the *sufficient*
form the round named: `entry_kind == "immigrant_cohort"` rows carry a pre-set
`claim_age` sentinel and an eligibility-domain marker, so
`engine/steps.py:411-413` never selects them. Implemented at
`engine/entrant_domains.py:154`, `:287` @ `29aa8c6`.

**Open item — the certification boundary for ordinary cores applied to entrant
inputs.** Subparts for marital history, the disability-concept bridge, entry
employment and the entrant earnings law remain **BLOCKING** with their bindings
UNBOUND (§6.2). The default stands: no independent marginal hot-decks, no
certificate transfer, and an entrant stays outside every unresolved domain.

### O6 — Observation date versus publication date at `T*` — RESOLVED as a two-boundary question

> "**O6-a.** `gate_imm` in the certified-frame branch is **not** an M6-boundary
> gate … it must be registered against the `gate_w1` boundary and lock, not
> `T* = 2014` … **O6-b.** The temporal fence therefore cannot be a year split …
> It must be the `gate_w1` pattern — a **household-disjoint split** … **O6-c.** If
> a referee later restores the ACS branch, #218's O6 text stands unchanged and
> should be preserved verbatim as the alternative."

**Evidence.** The frame is a 2024 reference-period artifact
(`gates.yaml:3732`; the same pin in code at `data/deployment_frame.py:61`, inside
`CERTIFIED_PIN` at `:43-62` with `revision` at `:55-57` and `artifact_sha256` at
`:58-60`), so its observations post-date `T*` by a decade — while it is already a
**certified** surface for `gate_w1` (`gates.yaml:3725-3734`) with a completed lock
dated 2026-07-12 (`:3737-3745`). The question is therefore not "may we use
post-2014 bytes" but "which gate's boundary governs a surface both gates touch."

**Folded** in the header's information-boundaries block, §5.1 and §5.2. Revision 4
would have left a reader to infer that a 2024 frame is admissible under a 2014
boundary; the header now says which boundary governs what, and §5.2 says plainly
that **no temporal fence exists under this donor** rather than implying one.
O6-c is honoured: Appendix A carries revision 4's O6 text verbatim.

**Open item — the frame's nativity columns' own reference year.** The round's
refutation test: "Evidence that the pinned frame's nativity columns are themselves
2014-vintage passthroughs rather than 2024 CPS ASEC values — I verified the
columns are populated and internally consistent, not their reference year." The
build's `source_year` column and the vintage-keyed bin table make the pooled
vintages `{2022, 2023, 2024}` explicit, which answers it for the donor pool; the
manifest must still record it (O7′).

### O7 — CPS ASEC diagnostic vintage — RETIRED and replaced by O7′

> "**Recommended resolution.** Retire O7 as posed and replace it with **O7′ — bind
> the ASEC vintage behind the certified frame's nativity columns.** … Traditional-
> versus-Redesign remains the right *form* of the question; its subject changes
> from a diagnostic file to the donor's own provenance."

**Evidence that the question inverts.** The frame's nativity trio and its
`A_MARITL` (mapped through the seven Census ASEC recodes at
`data/deployment_frame.py:65-73`) are CPS ASEC concepts carried onto the populace
frame, so ASEC stops being report-only triangulation and becomes the **donor's own
code book**. That an ASEC code book cannot be taken at face value across vintages
is not speculation here: this repository has already had to adjudicate one such
disagreement and keeps two vintage-keyed code→interval maps as a result —
`CPS_FIRMSIZE_INTERVALS_2011_2018` (`src/populace_dynamics/firms/banding.py:246-253`)
and `CPS_FIRMSIZE_INTERVALS_STANDARD` (`:265-276`).

**And the direction of that adjudication is the useful part.** In the `FIRMSIZE`
case the dictionaries disagreed and the *dictionary* was wrong: the 2019+
relabeling of codes 2/5 is "phantom … it inherits the Census 2019+ NOEMP
dictionary error, and the instrument has in fact collected 10-49 / 50-99
continuously since 2011" (`firms/banding.py:255-264`; the same conclusion at
`:66-67`, "a documentary relabeling only — the instrument is unchanged", and the
data evidence at `src/populace_dynamics/data/asec_firm_size.py:10-16`). So a
cross-vintage difference in an ASEC code book may be **real** — as `PEINUSYR`'s
top code is, where the underlying window genuinely differs — or **documentary**,
as `FIRMSIZE`'s was. Only opening the dictionaries distinguishes them, which is
precisely why O7′ demands the vintage binding rather than a crosswalk.

**O7′ is substantially discharged.** The round asked for the vintage and the
`PEINUSYR` bin edges, noting that microcosm's `_ARRIVAL_YEAR_MIDPOINTS` crosswalk
gives midpoints and not edges. The build read the 2022/2023/2024 ASEC dictionaries
and the CPS technical documentation and encoded the actual edges keyed by vintage
(`data/nativity_frame.py:110-148` @ `29aa8c6`), transcribed `PRCITSHP`'s five
labels from the 2024 dictionary at position 147 (`:82-88`), and corrected the
dictionary's stale "See Appendix H" cross-reference — the country codes are
**Appendix I** — pinning `057 = United States` from it (`:97`) rather than from a
row-count mode.

**Open item — the manifest binding.** The edges and labels are evidence; the
*binding* is not yet written down beside `CERTIFIED_PIN`. That is one microcosm
lookup, and it discharges O3's residue and O11-b in the same trip (P3).

### O8 — Exact SIPP Wave 1 file and correction vintage — DEFERRED, non-blocking

> "**Recommended resolution: defer O8 out of v1 and mark it non-blocking for the
> build.** … Keep O8 open only as the successor question for the one state SIPP
> has and the frame does not: **fertility/parity history** (O13)."

**Evidence.** The principle — "directory identity alone is not a binding" — is
right and the repository enforces it elsewhere: the external snapshot manifest
binds `(timestamp, sha256, size, filename)` per file, and
`scripts/build_ssa_level_anchors.py` reads only committed, hash-verified
snapshots with `build.network_access: "none"`. But there is **no SIPP artifact of
any kind** in `data/external/`, and the marital and employment state O8 would
supply now comes from the same frame that supplies nativity — already hash-pinned
by `gates.yaml:3729` and **jointly observed on the same person row**, which is
exactly the joint-coherence property §4.8 demands and a separately matched donor
cannot give without a second imputation.

**Folded** in §2.2 (SIPP narrowed to parity/birth history) and §6.2 (status
changed from blocking to non-blocking for v1, retained as O13's successor).

**Open item — measure `A_MARITL` on the recent-arrival subpopulation.** The
round's refutation test is precise: `REQUIRED_SOURCE_COLUMNS`
(`data/deployment_frame.py:92-99`) floors `A_MARITL` at 0.99 non-zero
**frame-wide**, and the guard at `:347-368` raises below that floor, but neither
statement is conditional on nativity. Measuring it on the 1,155 donor rows would
settle whether the frame can carry entrant marital state at all. Recorded as a
required step in §6.2's `entrant_marital_household_history_initializer` row.

### O9 — Current-vintage production refits — RESOLVED, and non-blocking for v1

> "**Recommended resolution: adopt the conservative default, and additionally bind
> the trigger.** … **O9-d.** Record that **O9 does not block v1.**"

**Evidence.** Revision 4 already stated the conservative default as design law in
its own §5.2, so O9 as a heading overstated what was open; what is genuinely open
is what a refit re-enters and what triggers it. The repository's non-transfer
precedent is stated at maximum prominence and is **law-shaped, not
vintage-shaped**: `gates.yaml:5384-5386` records that the gated {2016, 2018}
earnings cells come from a *different stochastic law* than the gate_1-certified
chain and that "no gate_1 certificate transfers". And the mechanism that actually
decides O9 is a **hash pin, not a policy**: every `lock_ceremony` block attaches to
exact artifacts, and this donor is pinned three ways at once
(`gates.yaml:3728`, `:3729`, `data/deployment_frame.py:43-62`), whose comment says
"the pin **is** the estimand's identity" (`:41-42`). A refit changes the blob, so
the sha changes, so the pin does not resolve; the certificate cannot transfer
because there is nothing under the registered identity for it to transfer to.

**Folded** in §5.2: the default is promoted from a §5.2 aside to law; a refit
**re-enters the ordered ceremony at step 2** (acquisition/hash-binding) and runs
steps 2–8, never at step 6 with a new candidate against an old lock; and — because
under this donor the refit cadence is **microcosm's, not this design's** — a
**donor-pin watch** is added to the manifest (`certified_frame_donor_pin_watch`,
§6.2). `gate_imm` carries its own pin and must not inherit `gate_w1`'s. O9 does
not block v1, because a report-only product has no certificate to transfer.

**Open item — none for v1.** O9 binds the first certification attempt.

### O10 — Physical cohort size and calibration constraints — RESOLVED, and the support is measured

> "**Recommended resolution.** Ratify O10's ordering law unchanged — it is the M6
> law and it is right — and re-scope its content to the adjudicated donor:
> **O10-a.** Delete "annual" from every O10 quantity … **O10-b.** Adopt
> `gate_w1`'s heavy-tail guard by name — `floor_max_exceeds_tolerance` — as
> `gate_imm`'s pre-registered demotion criterion, rather than inventing a weight
> cap … **O10-c.** Make the operating-characteristic pause check of §5.3 step 7
> **mandatory and expected to fire** … **O10-d.** The ESS machinery is a build
> deliverable, not an assumed capability."

**Evidence.** The floors-before-thresholds machinery exists roughly a dozen times
over in `scripts/`, so O10 asks for a step this repository has executed
repeatedly, not a novel process. The nearest precedent is `gate_w1` on the **same
donor**, splitting on `household_id` — "the fix, the 2c couple-disjoint lesson"
(`scripts/build_gate_w1_floors.py:163`) — which removes the "annual physical
sample size" degree of freedom entirely, because **there is no annual dimension in
the certified frame**. The weight-cap question is already answered adversely by a
committed measurement: `runs/gate_w1_floors_v1.json:20599` records the
concentration (max ≈ 433k against a mean ≈ 2.3k) and the remedy — the heavy-tail
guard `floor_max_exceeds_tolerance` — and `:72` records "Kish n_eff ~ 14.3k of
166k nominal". `kish_n_eff` lives in exactly one script
(`scripts/build_gate_w1_floors.py:1575`, published at `:1729-1736`) and `src/`
contains no ESS helper at all.

**Folded** in §4.3 ("annual" deleted; the unit count is the donor's row count,
fixed by the predicate rather than chosen), §5.3 step 5 and its two named rules,
and §5.3 step 4's requirement to publish the clustered quantity.

**O10-c is no longer a prior — it is a measurement (§5.3a).** The round wrote:
"the plausible effective sample [is] in the low hundreds of units", and named the
computation as "the single cheapest measurement that would change this
adjudication". Revision 5 takes it. On the donor pool: **156.1** persons and
**82.0** household weights effective, against 1,155 nominal rows in 562
households. Per proposed A1 cell the clustered effective sample runs from
**2.7 to 36.0**, with nine of fourteen cells below 14. The frame-wide figure
reproduces the committed 14.3k/166k, which is the check that the quantity is the
same one the precedent uses.

So the round's refutation test — "A measured Kish n_eff on the … subset
materially above the frame-wide ratio … would soften O10-c" — resolves the other
way in the sense that matters. The *ratio* is mildly better than frame-wide
(156.1/1,155 ≈ 0.135 against 14,327.8/166,302 ≈ 0.086), and the **absolute
number is tiny**. Floors are priced in absolute effective units, not in ratios.
§5.3a therefore pre-registers the consequence: the pause check is mandatory, a
two-or-three-cell surviving surface is the expected outcome, collapsing sex within
age band is the pre-declared fallback, and pooling bands is the only other lever —
one that costs vintage coherence and must be priced, not taken silently.

**Open item — O10-d, the ESS helper.** Nothing in `src/` computes person or
cluster ESS today. The floors PR must lift `kish_n_eff` into a shared helper and
add the cluster/unit-weight quantity §5.3 step 4 requires. The numbers in §5.3a
were computed for this revision **outside** the repository and are evidence for a
design decision, not a substitute for that deliverable.

### O11 — Social Security-area to Census-resident universe bridge — RESOLVED as a three-leg chain, still BLOCKING

> "**Recommended resolution: keep O11 blocking, and re-pose it as a three-universe
> chain.** **O11-a.** The chain is `SSA area → Census resident → certified-frame
> universe` … **O11-b.** Leg three is the cheapest to close and must be closed
> **first** … **O11-c.** Retain the `ssa_area_proxy` label and the report-only
> suppression exactly as written … **O11-d.** Fold the acquisition into O1-C1."

**Evidence.** No population-universe series is committed: the registered SSA series
are all money and caseload, and `scripts/build_ssa_level_anchors.py` enforces the
list exactly, raising when "registered series IDs are missing, extra, duplicated,
or reordered". The machinery a bridge needs exists and is strict — each series
carries an `official_concept` object and the builder raises on "official
concept/scope drift", with every series stamped `comparison_status:
"context_only"` — so O11's bridge is precisely a concept binding of that shape,
for a series that has not been acquired. And the frame's own total does not settle
the universe question: 166,302 person rows summing to 340.009 M weighted persons
is close enough to several published US population concepts that it discriminates
between none of them.

**Folded**: §2.4 and §4.3 state the chain as three legs; §6.2 splits it into
`ssa_area_to_census_resident_bridge` (leg 1→2) and
`certified_frame_universe_definition` (leg 2→3, **P3**), both BLOCKING; O11-c's
`ssa_area_proxy` label and report-only suppression survive verbatim into §4.3 and
the artifact's `universe_bridge_status`; O11-d is folded by requiring the same
acquisition PR that commits a universe series to record it with an
`official_concept` block in the existing pattern, rather than acquiring the same
table twice under two decisions.

**Open item — P3, and it is the cheapest of the three legs.** Leg three is a
documentation lookup in microcosm-build, not a commissioned transformation: name
the frame's universe definition and its treatment of the institutionalized
population, active-duty armed forces and territories, and record it beside
`CERTIFIED_PIN`. Until it is named, the schedule cannot claim to add people to a
known universe and O1-C2's denominator audit has no denominator definition. The
same trip discharges O7′ and O3's residue.

The round also named an option this design should answer rather than leave open:
"A ruling that the entry control is scored only as a *share* rather than a level
… would make the universe bridge unnecessary for v1". **This design does not take
that option.** V1 sizes cohorts to a level, publishes
`entry_only_minus_net_gap` as a level, and keeps O11 blocking. A share-only v1
would be a different product with a different audit, and adopting it silently to
retire a blocker is exactly the move §4.11 exists to prevent.

### O12 — Stock-to-arrival state, repeat entry, and prior U.S. coverage — RESOLVED, hard exclusion

> "**Recommended resolution: keep O12 blocking for benefits, and convert its
> 'suppression' from an accident into a guard.** … **O12-a.** Ratify `stock_proxy`
> and the prior-coverage censoring as written … **O12-b.** The suppression must
> become an assertion, not a side effect … **O12-c.** Prior coverage is … an
> `aime()` API question … **O12-d.** Repeat entry: … Bind it as **not
> identifiable** rather than leaving it open."

**Evidence** — the sharpest finding of the round, because the statutory oracle
**silently supplies the wrong answer rather than refusing**. Set out in full at
§4.9a: no insured-status test exists anywhere in `ss/` (747 lines, twelve public
functions, and a grep for `quarter|insured|coverage_credit` returns nothing);
`aime()` zero-pads to 35 computation years and assigns coverage adequacy to
callers in a docstring (`ss/benefits.py:100-117`, `:115-116`, `:61`, `:105-112`);
the career builder's coverage span is birth-anchored, not presence-anchored
(`estimates/career.py:1004`, `:1003`, `:22`, `:26`); and the only thing fencing
the hazard today is one line written for an unrelated reason
(`estimates/career.py:1580-1581`), which opens in the same commit that lands an
entrant earnings law.

**Folded as design law E1–E3** (§4.9a) and as two UNBOUND bindings
(`ss_insured_status_function`, `prior_us_covered_earnings_bridge`, §6.2). O12-a is
strengthened: under this donor the stock-to-arrival problem is **worse** than
revision 4 assumed — `PEINUSYR` is a 2–3 year band, so duration since arrival
cannot be computed to the year even in principle, and a single cross-section
offers no second observation from which pre-interview attrition could be
estimated. The design says plainly that the selection correction is **not
identified from the donor at all** and requires an external law. O12-d is bound:
repeat entry is **not identifiable** under this donor.

**Open item — the round's third refutation path, answered here.** "A ruling that
`stock_proxy` outputs may report benefits with a disclosure rather than
suppression — defensible for a diagnostic, but it needs the O12-c guard first,
because the current failure mode is a plausible non-zero PIA, not a visible
error." **This design refuses that ruling for v1.** Benefit output is excluded,
not disclosed, until `ss_insured_status_function` is bound. A plausible non-zero
PIA is the one failure mode a disclosure cannot catch.

### O13 — Fertility history and entrant exposure — RESOLVED, blocking, with the mechanism attached

> "**Recommended resolution: keep O13 blocking for entrant fertility, and ratify
> the prohibition with its mechanism attached.** **O13-a.** Record *why*
> parity-zero is prohibited … **O13-b.** An entrant-aware fertility kernel is a
> **new fit**, not a wrapper … **O13-c.** Harden `steps.py:539` … **O13-d.**
> Exposure start: bind it to the entry year."

**Evidence, and a completed citation.** Revision 4 cited `engine/marital.py:313`
for "the current kernel initializes parity to zero". That pin was **correct at
its baseline** — at `75d30dd` line 313 is
`parity = np.zeros(len(attrs), dtype=np.int64)` — and it has simply drifted, to
`engine/marital.py:363` at head. It is **incomplete, not wrong**: one citation
does not carry O13-a's burden, because the parity-zero hazard has three separate
mechanisms in two different modules, and an implementer who fixes only the one
revision 4 named would still ship the other two. O13-a requires all three, so
that an implementer who sees zeros does not assume they are data:

1. **The certified kernel is parity-conditioned in its cell definition.**
   `models/family_transitions/components/fertility.py:80-86` — "Keys are
   `(age, min(parity, 3), birth_decade)` for ages 15 through 49" — and the weight
   tables are built by `groupby(["age", "parity_band", "decade"])` at `:137`.
   A person with unknown parity has **no cell**: there is no unknown-parity
   stratum, no marginalized fallback and no imputation hook.
2. **`_parity` returns 0 for an unknown person.** `fertility.py:49-71` counts
   prior births by `np.searchsorted` into `births_by[person_id]`; an entrant has
   no entry, so `arr is None: continue` (`:67-69`) leaves the zeros initialized at
   `:58`. That is exactly the parity-zero default O13 forbids, and it is what the
   code does today if an entrant reaches the fit or the simulator.
3. **The simulator seeds a running parity vector at zero.**
   `models/family_transitions/simulator.py:170` —
   `parity = np.zeros(n_people, dtype=np.int64)` — incremented at `:356` and read
   at `:346`. Correct only for a person whose fertility history begins inside the
   simulation; silently 0 for a 35-year-old entrant.

**Folded** in §4.9 and §6.2. O13-b: an entrant-aware kernel is a **new fit**,
because the cell structure requires a parity value the donor does not carry — and
that is the one irreplaceable role SIPP retains (O8). O13-c: `engine/steps.py:539`
is a silent whole-roster risk set under an open population; the risk set must be
passed explicitly or the site must carry an entrant-exclusion assertion. O13-d:
exposure starts at the **entry year**, and the design makes **no claim** about
pre-arrival fertility — the frame has no such observation and the kernel has no
cell for it; any imputed parity is a report-only imputation with its own
uncertainty, never an observed state.

**Open item — two, both named by the round.** (i) The frame's 222 person columns
were enumerated for nativity and marital status, **not exhaustively for a
birth-history variable**; a parity source in the frame would change O13-b from
"new fit" to "existing fit, new input". (ii) The design should say whether
entrants stay permanently outside fertility — the natural companion of the
entry-only posture. **It does: for v1, yes.** Entrant fertility is a v2 estimand,
and §4.9 excludes it by an active adapter rather than by an absent kernel.

### O14 — RNG-isolated composite and cross-domain markets — RESOLVED, with the newborn law measured

> "**Recommended resolution: adopt the composite-adapter branch, and add the
> newborn-ordinal law.** **O14-a.** Ratify the composite adapter as #218 describes
> it … **O14-b.** Add to §4.6: *scheduled entrants shift every dynamically created
> row's ordinal by the scheduled-entrant count* … **O14-c.** … §9.2 step 5's
> claim … unless the run is measured, not argued … **O14-d.** Extend the seam
> validation to consult `reserved_real_ids` … **O14-e.** Keep cross-domain
> entrant/existing marriage and household markets a **separate report-only
> product**."

**Evidence.** The addressing chain is verified end to end:
`PeriodContext.person_generator` (`engine/loop.py:100-113`, the raise at
`:107-110`) forwards to `ProjectionRNGRegistry.person_generator`
(`engine/rng.py:158-168`), whose spawn key is `(*sequence.spawn_key, child_index)`
(`engine/rng.py:85-99`), with the docstring stating the law: "The ordinal, rather
than the identifier's representation, is part of the spawn key." Ordinals are
assigned by `enumerate(sorted(all_initial_ids))` (`engine/loop.py:263-266`) over a
set unioned with every scheduled entrant (`:242-250`), and dynamically created
rows take `len(person_ordinals)` (`:352-360`, the assignment at `:360`).

**Folded, and O14-b/O14-c are now measurements rather than deductions.** §4.6a
runs the experiment the round named as the cheap refutation — "schedule one
immigrant, run two seeds, diff the birth roster" — against `afd8f44` and records
three laws:

- **L1.** The newborn's ordinal shifts by exactly the scheduled-entrant count
  (+1, +7, +100 measured) and its mortality draw bytes change. An open run makes
  **no byte-identity claim for synthetic births even within one schedule**. The
  round's point 3 is confirmed, not refuted.
- **L2** — a channel the round did not name. The newborn's **`person_id` itself
  relocates**, because the engine's fallback allocator starts at
  `max(all_initial_ids) + 1` over the *combined* universe
  (`engine/loop.py:251-257`, `:242-250`). Measured: id 6 → 10,001 with the
  immigrant floor at 10,000. Any consumer identifying births by ID arithmetic is
  therefore wrong in an open run — which is precisely what
  `harness/m6_runner.py:986-987` and `:1022-1036` do today (§9.1).
- **L3.** The original person's ordinal and mortality draw bytes are
  **unchanged** in every case, so revision 4's §4.6 ID-floor claim is verified
  rather than assumed.

**O14-a and O14-e are ratified verbatim** (§4.6): the composite adapter runs the
baseline closed support in its original order with its original generators, runs
entrant-only transitions under named disjoint draw×period×person namespaces, and
returns one authoritative partitioned result to the reader slots; and any
cross-domain market that can change a baseline person's panel membership stays a
separate report-only product, because it reaches existing-person draws through the
shared-generator channel and no isolation law survives it.

**O14-c is folded into §9.2 step 5**: "without changing the M6 closed-panel score"
becomes a **measurement** — run the closed panel with and without the schedule and
diff the gated cells — not a design property. The expected outcome, given the
ratified report-only margin for family-B open additions
(`gates.yaml:5416-5420`), is "unchanged on the gated surface, changed on the
report-only birth surface". That is a hypothesis until it is run on the real
panel; §4.6a establishes only that the birth surface *does* change, which is the
half that was previously asserted the other way.

**Open item — O14-d, an engine-side check this design cannot make.** The seam
never consults `reserved_real_ids` for scheduled entrant IDs
(`engine/loop.py:162-168`, `:236-239`, `:242-250`), and the engine's fallback
allocator carries an **empty** reserved set (`:255-257`). §4.7 makes both
builder-side assertions, which is everything a docs-only design can do; the
engine-side check is a separate amendment. Note the trap it closes: §4.6 tells the
metadata adapter to **omit** the allocator so the loop builds it — and the loop's
built one has no reserved set. Today the design must choose between a range check
and F2; O14-d removes the choice.

### O15 — Projection origin and the first entrant cohort — RESOLVED (a), horizon bound to 2022

> "**Recommended resolution: branch (a) for the v1 report-only run, with the
> horizon told the truth.** **O15-a.** Adopt branch (a) … **O15-b.** Bind the
> horizon to **2022**, not 2100, for v1, and say why … **O15-c.** … name the NAWI
> and taxable-maximum series and their coverage … **O15-d.** Add the 2024 origin
> as an explicit, *rejected* branch with its reason."

**Evidence.** The seam constraint is two-sided and exact:
`engine/loop.py:228-232` raises "scheduled entry year … lies outside the
projection" unless `start_year < entry_year <= end_year`. And `end_year` is
**2022, not 2100, everywhere in the executable stack** — `harness/m6_runner.py:112`
consumed at `:584`; `estimates/runner.py:39-40`; `estimates/career.py:26`;
`REPORT_YEARS = tuple(range(2015, 2023))` at `estimates/ledgers.py:51` and in three
sibling modules. A grep of revision 4 for `2022` returned nothing, so branch (a) as
written required a horizon **78 years beyond anything this repository executes**
and did not say so. Extending it is a **parameter-series** change with a
fail-closed guard: `advance_age` raises for any year the NAWI or taxable-maximum
series does not cover (`engine/steps.py:160-165`).

**Folded as §4.3a and prerequisite P2**, in two named modes: v1 is origin 2014,
first schedule key 2015, control range **2015–2022**, buildable today; anything
past 2022 is blocked on four named items including both parameter series.
O15-c is folded into §6.2 as the new `m6_nawi_and_wage_base_series` binding —
revision 4's table had **no** wage-index series at all, only V.A2 and the Census
corridors. O15-d is folded: the pinned 2024 frame is recorded as an explicit
**rejected** origin, because a 2024-reference origin re-anchors the M6 path and
collides head-on with O6; O15 and O6 are answered together, not separately.

**A consequence for the built artifact, recorded rather than glossed.** The
entrant schedule built at `29aa8c6` activates **2026–2035**, which is the Trustees
intermediate window and not the v1 interval. Attached to the current M6 runner
(`start_year = 2014`, `PROJECTION_END_YEAR = 2022`) every one of those keys would
raise at `engine/loop.py:228-232`. The artifact is therefore a **standalone
report-only schedule**, not an M6 open-run schedule; wiring it to the M6 runner
requires either rebuilding it on 2015–2022 or discharging P2. Neither this design
nor that artifact may be read as if the two windows were interchangeable.

**Open item — the round's own refutation paths, both still open.** (i) A
long-horizon runner elsewhere under `scripts/` would change P2 from "blocked" to
"already available"; a grep of `harness/m6_runner.py` and `estimates/runner.py`
found only the 2022 constants. (ii) A ruling that the open run is a *separate
product* not bound by `REPORT_YEARS` is plausible — §9.2 step 5 does call it a
"report-only open-population run" — but it still needs an `end_year` and the
parameter series to reach it, so it changes who owns the constant, not whether it
must exist.

### O16 — Joint assignment family — RESOLVED, donor-based, with the disclosure

> "**Recommended resolution: donor-based joint assignment, with the joint
> surface's own status disclosed on the face of the gate.** **O16-a.** Adopt the
> recommended donor-based branch … **O16-b.** Keep the joint-surface decisive
> criterion verbatim … **O16-c.** Add the disclosure that makes the criterion
> honest … **O16-d.** A predeclared challenger … should be explicitly deferred out
> of v1."

**Evidence.** The prohibition on marginal hot-decks is architecturally consistent
with what the engine already enforces — `engine/earnings_domain.py:217-225` raises
on marker/fitted-state disagreement, `engine/forward_earnings.py:1421-1436` raises
without fitted state, and `engine/panel_builders.py:169-176` inner-joins so an
unmatched person simply is not in the panel — so marginal hot-decking is not
merely disfavoured here: **there is no seam that would accept its output**. And
donor-based joint assignment is not a new class of object for this codebase: the
certified forward earnings law is a regime-gated quantile forest
(`engine/forward_earnings.py:194`, `:207`, `:979-987`), so the recommended branch
competes against an incumbent architecture the repository already knows how to
certify.

**Folded**: §2.3's provisional adjudication becomes final (donor-based joint
assignment with model-based calibration and no cloned future); the decisive
criterion — "a challenger cannot win on lower marginal error while failing the
joint surface" — is kept verbatim; and **O16-c is folded into §5.6 as a required
PASS disclosure at headline prominence**, citing
`runs/gate_w1_floors_v1.json:72`: the frame's age × sex × marital and
household-size joints "are NOT in populace's calibration loss and ride
UNCERTIFIED", so family A "certifies transport CONSISTENCY to those joints, not
their external truth". This is the gate_m6 amendment-1 candour standard
(`gates.yaml:5384-5396`) applied to this gate. O16-d is folded: a challenger is
explicitly deferred out of v1, because on the support measured in §5.3a a
two-family gate cannot discriminate two joint-assignment architectures, and
running one against an underpowered surface would produce a PASS that means
nothing.

**Open item — the one place the adjudication rests on adjacent cells.** The quoted
note covers age × sex × marital and household size; it does **not** cover
nativity. So the nativity joints' calibration status is **strictly unestablished
rather than known-uncertified**. The build measured the supporting fact — no
nativity column is in `REQUIRED_SOURCE_COLUMNS` (`data/deployment_frame.py:92-99`) and
the certified file pins no nativity margin — which is strong evidence of
uncalibrated, but establishing it properly is the same microcosm lookup as P3.
§5.6 therefore requires the disclosure to say **unestablished**, not
**uncertified**, until P3 closes. A power analysis showing 562 households can
discriminate two joint architectures would revive O16-d; §5.3a makes that
unlikely.

## 8. What this design does not change

This document and its eventual entrant-side implementation must leave these
surfaces unchanged unless a later, separately adjudicated design explicitly
authorizes surgery:

- `gates.yaml`, every `gate_m6` cell/threshold, the v1/v2/v3 M6 floors and their
  hashes, `tests/tier_counts.json`, and all existing run artifacts;
- M6's `T* = 2014`, temporal holdout, shock partition, weight convention, and
  closed-panel scoring support;
- the certified candidate-16 marital core, candidate-9 household composition
  object, M4 disability reproduction object, gate-2c earnings modifier, and
  gate-1/backward or M6/forward certified earnings specifications;
- the existing age/sex mortality fit and frozen `<=2014` claiming schedule;
- the §2.8.3a earnings-domain predicate and its realized-2014 state maps;
- the §2.8.2g marital risk-set guard and seed-at-domain-entry law;
- amendment 3h's schedule-versus-live-roster materialization distinction and
  absent-parent guard;
- `SCHEDULED_ENTRIES_KEY`, its frame/year/ID contract, and every existing
  2017/2019 PSID opener row; the immigration builder merges that mapping and never
  overwrites it;
- the eight-member `PeriodModules` order (`engine/loop.py:117-129`), existing
  module RNG streams, original-person ordinals, and period trace; synthetic-ID
  allocation follows **merged** M6 §2.8.2i F2 (PR #221, merge commit
  `00d5443d9df21ac13e42669d13d94c5ef734134c`), implemented at
  `engine/loop.py:44-64`, `harness/m6_runner.py:432-441` and
  `harness/m6_population.py:70-82`, extended by this design's stronger
  `immigrant_id_floor` (§3.1) rather than by the current side-local default;
- M6's current statement that immigrant/open-panel additions are report-only;
- M7 trust-fund accounting, M8 rules execution, and any PolicyEngine-US legal
  eligibility rule; and
- every source or artifact outside the immigration binding manifest.

An entrant adapter may call unchanged core code, but it must do so under an
entrant-domain label and separate report/gate surface. It may not alter the
closed-panel input or score and call the resulting difference “immigration.”
The metadata adapter also must carry the pre-split global floor and omit a caller
allocator or enforce the complete reserved-plus-scheduled guard in §4.6. Any
mixed entrant/existing-person market remains the
report-only O14 product and makes no closed-run byte-identity claim.

## 9. Candidate-blind implementation and certification order

### 9.1 Required integration patch pointers

**Five source files consume `scheduled_entries_by_year` at `afd8f44`**, not two.
Revision 4 named `harness/m6_runner.py` and `harness/m6_reporting.py`. The full
list is `engine/loop.py`, `harness/m6_population.py`, `harness/m6_runner.py`,
**`estimates/career.py`** and **`estimates/preparation.py`**. The last two did not
exist at the revision-4 baseline — `src/populace_dynamics/estimates/` was added
2026-07-25 by `070cbb7`, ten days after this design was written — and **neither
tolerates an immigration frame**. This is the one item that would crash a build on
its first open run.

#### The runner surfaces (re-pinned, and one field longer)

`harness/m6_runner.py:986-987` derives `synthetic_ids` as
`set(household_result.panel["person_id"]) - initial_ids`, and `:1022-1036`
consumes it under the comment "Every synthetic ID allocated by this closed-panel
engine is a step-4 materialized maternal birth" — true today, and **false the
moment a schedule is supplied**. In that block, `"synthetic_births"` is
`len(synthetic_ids)` (`:1026`), `"immigrant_cohorts"` is hardcoded `0` (`:1027`),
and `"scheduled_realized_openers"` sums **every** frame in the schedule mapping
(`:1029-1032`). The head block also carries `roster_absent_births`
(`:1033-1035`), which revision 4's patch list did not have. The no-seed fallback
repeats the zero at `:1207-1217` (`"immigrant_cohorts": 0` at `:1212`,
`"roster_absent_births": {}` at `:1215`) and the consumer reads it into the
family-B publisher at `:1218-1224` (`immigrant_cohorts=int(...)` at `:1220`).

These are mandatory patch surfaces when the module lands; the closed-panel path
may retain its current result. The open-run report must derive mutually exclusive
counters from **explicit provenance**: immigrant schedule rows where
`entry_kind == "immigrant_cohort"`, realized PSID opener rows where
`entry_kind == "realized_opener"`, and materialized births identified by birth
provenance or by the allocation ledger after all scheduled IDs are removed. It
must never infer opener count from the size of the merged schedule, infer births
from every non-initial ID, or inherit the hardcoded zero-immigrant fallback.
§4.6a L2 shows why the ID-arithmetic route is not merely fragile but **wrong**: in
an open run the engine's fallback allocator relocates every birth ID above the
immigrant floor. The resulting immigrant count feeds the existing family-B
publisher at `harness/m6_reporting.py:277-318` and remains report-only.

#### The `estimates/` surfaces (new, and blocking — P1)

**(i) `estimates/career.py:564-620` — `build_seed_coordinates`.** It requires the
columns `("person_id", "year", "anchor_wave", "age")` on **every** scheduled frame
(`:577`, `:602`) and asserts `anchor_waves == {entry_year}` (`:612-615`) and
`seed_years == {entry_year - 1}` (`:616-619`). This design's entry-frame schema
has no `anchor_wave`, and `anchor_wave` means "PSID collection wave" — an
immigrant has none.

> **Decision.** Revision 5 takes the **exclusion** branch, not the
> widening branch. Immigration frames are excluded from `build_seed_coordinates`
> by an explicit `entry_kind` filter; `anchor_wave` keeps its PSID meaning and is
> **prohibited** on an immigration frame (§4.7).

The reason is semantic and it matters downstream. An immigration frame *could*
satisfy `estimates/career.py:612-615` numerically by carrying the entry year in an `anchor_wave`
column, which is why the round classed this as "concept abuse rather than a
crash". But `build_seed_coordinates` feeds the career and benefit machinery that
§4.9a excludes entrants from on statutory grounds; widening the concept would let
entrants in through the seed door while E1 was shutting the career door. The
filter must **fail closed**: a scheduled frame that carries no `entry_kind` at all
raises, rather than being silently treated as PSID.

**(ii) `estimates/preparation.py:317-359` — `derive_synthetic_birth_years`.** It
classifies **every** trajectory ID outside `reserved_real_ids` as a native birth
(`:332`) and then raises "synthetic trajectory rows lack native birth_year"
(`:335-336`) or "synthetic person {id} has no native birth_year" (`:349-352`). An
immigrant allocated above the reserved floor is exactly such an ID. This is the
same "every synthetic ID is a birth" inference §9.1 already forbids for the runner
counters — in a file revision 4 did not name.

> **Decision.** The birth inference is replaced by the same **explicit
> provenance** rule the runner counters use: classify by `entry_kind` (or by the
> allocation ledger with all scheduled IDs removed), and **raise on an ID whose
> provenance is unknown** rather than defaulting it to a birth.

Both changes are ratified amendments to certified-run reporting and to the
first-estimates pipeline. This design cannot make them; it names them, decides
their form, and records them as **P1 — blocking for any open run**
(`estimates_seam_amendment`, §6.2). `preparation.py` consumes
`scheduled_entries_by_year` unconditionally (`estimates/preparation.py:518`, `:520`,
`:539`), so the
burden of showing that an open run bypasses the pipeline rests on whoever claims
it does.

### 9.2 Ordered ceremony

A later implementation should proceed in this order:

1. **Referee round — done.** O1–O16 are adjudicated and folded into §7 of this
   revision. What remains at this step is ratification of the external-binding
   schema in §6.1–6.2 and of the two amendments §9.1 decides (P1).
2. **Acquisition PR** commits and hash-binds exact source bytes and parsers; the
   zero-argument binding factory passes independently of any candidate. **Partly
   done and unmerged:** Table V.A2 (§2.4) and the certified-frame donor reader
   exist at `29aa8c6`. Still owed at this step: the universe series and the
   `official_concept` block for O11/P3, the NAWI and taxable-maximum series for
   P2, and the frame's own universe/vintage binding beside `CERTIFIED_PIN`.
   **A donor refit re-enters the ceremony here, at step 2, and runs steps 2–8**;
   it never re-enters at step 6 with a new candidate against an old lock (O9-b).
3. **Donor/bridge PR** constructs only fit-side artifacts, the separately
   identified arrival-state, fertility and prior-coverage bridges, and synthetic
   fixtures; held-out outcomes remain sealed.
4. **Floors PR** freezes the household-disjoint split protocol and seed-grid
   aggregation, lifts `kish_n_eff` into a shared helper and adds the
   cluster/unit-weight ESS (O10-d), creates truth-vs-truth and
   pipeline-variability floors, prunes unsupported cells under
   `floor_max_exceeds_tolerance`, and **runs the operating-characteristic pause
   check, which §5.3a expects to fire**.
5. **Schedule/state PR** implements the deterministic builder, seam adapter,
   structurally complete state packet, failure guards, and a report-only
   open-population run. Revision 4 wrote this step as "without changing the M6
   closed-panel score". **That is now a measurement, not a design property**
   (O14-c): run the M6 closed panel with and without the immigration schedule and
   **diff the gated cells**, publishing the diff. §4.6a establishes that the
   report-only birth surface *does* change; whether the gated surface is insulated
   by the ratified family-B margin (`gates.yaml:5416-5420`) is the question this
   step must answer with bytes. A step-5 PR that asserts the property instead of
   measuring it does not satisfy this design.
6. A registered `gate_imm` candidate is scored **once** against the locked
   surface.
7. If PASS is verified and ratified, the lock names exact source, derived, floor,
   code and schedule-protocol hashes — **including the donor's own
   `artifact_sha256` and build revision**, so that a microcosm-side refit
   invalidates the lock rather than silently re-scoring a different population
   (O9-c). `gate_imm` does not inherit `gate_w1`'s pin.
8. Emigration and current-vintage refit designs run their own ceremonies before
   any net-population or benefit certification claim. The emigration design must
   additionally propose how an exit is **expressed**, since the frozen
   eight-adapter order has no removal slot but mortality (§1.4).

No stage reads a later stage's candidate outcomes to redesign an earlier frozen
surface.

**What pauses, and on what.** A literal resident-entry schedule pauses while O11
(P3) and O12 remain unbound. Entrant fertility pauses on O13; entrant claiming,
insured status, AIME, PIA and every benefit output pause on O12 and
`ss_insured_status_function` — **excluded, not disclosed** (§4.9a). Any open run
at all pauses on P1. Any horizon past 2022 pauses on P2. A `stock_proxy`
diagnostic schedule may exercise seam structure inside those limits, in a
report-only run with the excluded domains reported as **suppressed counts rather
than zeros**.

## 10. Referee citation ledger

- **DYNASIM4**: Cosic, Johnson, and Smith, *Urban's Dynamic Simulation of Income
  Model 4* (Urban Institute, September 2024), pp. 1–2. Detailed donor mechanics
  are not public in that overview.
- **DYNASIM3 detail, not DYNASIM4**: Favreault, Smith, and Johnson, *The Dynamic
  Simulation of Income Model (DYNASIM): An Overview* (Urban Institute, September
  2015), Table 1, report p. 7.
- **MINT**: Smith et al., *Modeling Income in the Near Term Version 6* (Urban
  Institute, December 2010), ch. II §VI, pp. II-24–II-28, Tables 2-14–2-16; Smith
  and Favreault, *Modeling Income in the Near Term 8 and 2014: Primer* (Urban
  Institute, April 2019), pp. 15–16, note 21 p. 29, Table 3 pp. 39–40.
- **PENSIM/PENSIM2**: Holmer, Janney, and Cohen, *PENSIM Overview* (Policy
  Simulation Group for the U.S. Department of Labor, Employee Benefits Security
  Administration, September 2006), §2.1.6 p. 8, Appendix B §B.1 p. 99,
  §§B.1.2–B.1.3 p. 100, and §§B.7–B.8 pp. 106–107;
  O'Donoghue, Redway, and Lennon, “Simulating migration in the Pensim2 dynamic
  microsimulation model,” *International Journal of Microsimulation* 3(2), 2010,
  Table 2, §§5.1–5.2.
- **SSA methods/current controls**: Duleep and Dowhan, “Adding Immigrants to
  Microsimulation Models” and “Incorporating Immigrant Flows into
  Microsimulation Models,” *Social Security Bulletin* 68(1), 2008; *The 2026
  Annual Report of the Board of Trustees of the Federal Old-Age and Survivors
  Insurance and Federal Disability Insurance Trust Funds*, §V.A.3, and
  Supplemental Single-Year Table V.A2 — **acquired**, sha256 `5dfd05e5…89da`
  (§2.4, §6.2).
- **Donor microdata**: the certified `populace_us_2024` deployment frame, sha256
  `c2065b64…f39c5`, pinned at `gates.yaml:3728-3729` and
  `data/deployment_frame.py:43-62`; the CPS ASEC data dictionaries for the
  vintages it pools (2022, 2023, 2024) and CPS technical documentation
  **Appendix I, "Countries and Areas of the World"** — not Appendix H, which the
  dictionary's own note stale-references. Exact columns, bin edges and code
  labels are encoded at `data/nativity_frame.py:82-148` @ `29aa8c6` and pinned in
  §2.2, §4.5 and §6.2.
- **ACS PUMS (successor, not used)**: Census annual 1-year ACS PUMS person files
  and annual Accuracy statements for 2010–2014, the 2010–2014 dictionary as
  schema/crosswalk evidence, 2014 ACS Subject Definitions “Year of Entry”
  pp. 128–129, errata 87/97 and the 2013 same-sex married-couple user note — all
  preserved verbatim in **Appendix A**.
- **SIPP (narrowed to O13)**: Census 2014 SIPP Wave 1 metadata and
  source/accuracy statement; the exact raw file remains unbound at O8, which is
  non-blocking for v1.
- **Projection corridors**: Census, *Methodology, Assumptions, and Inputs for the
  2023 National Population Projections* (November 2023), migration pp. 8–14, and
  Table 1 in the Main Series and each Alternative Scenario.
- **Repository evidence.** Every `path:line` in this revision resolves at
  `afd8f44` unless it names `29aa8c6`. **Appendix B** lists them and records the
  check that each one was opened.

## 11. Design parameters and amendment history

```json immigration-design-parameters
{
  "design_id": "2026-07-15-immigration-module",
  "revision": 5,
  "status": "design_draft_revision_5_refereed_o1_o16_folded_build_ready_pending_p1_p4",
  "repository_pin": "afd8f44838c71bca1ce558ffcff5e7701b94f791",
  "second_pinned_revision": {
    "ref": "cap/entrant-schedule",
    "commit": "29aa8c6c96a39ecab71af86f01859d53a71f9c0c",
    "merged": false,
    "scope": "data/nativity_frame.py, data/trustees_immigration.py, engine/entrant_schedule.py, engine/entrant_domains.py, scripts/build_entrant_schedule_v1.py, runs/entrant_schedule_v1.json, data/external/snapshots/trustees_va2_vintage1/"
  },
  "superseded_engine_baseline": "75d30dd57d71b91ee0929246b2f3cbb92263b350",
  "roadmap_issue": 113,
  "docs_only": true,
  "certifies_now": [],
  "donor_fork": {
    "adjudicated": "certified_frame_first",
    "adjudicated_by": "plan owner",
    "acs_branch": "preserved verbatim in Appendix A as the named successor artifact; not a v1 dependency"
  },
  "prerequisites": {
    "P1_estimates_seam_amendment": "BLOCKING for any open run. estimates/career.py:602,:612-615 requires anchor_wave on every scheduled frame; estimates/preparation.py:332,:335-352 infers native birth from every non-reserved synthetic ID. Section 9.1 decides both fixes; the amendment itself is not this design's to make.",
    "P2_horizon_and_parameter_series": "BLOCKING for any horizon past 2022. harness/m6_runner.py:112, estimates/runner.py:39-40, estimates/career.py:26 and estimates/ledgers.py:51 all stop at 2022, and engine/steps.py:160-165 fails closed on any year the NAWI or taxable-maximum series does not cover.",
    "P3_certified_frame_universe_definition": "BLOCKING for any resident-alignment claim. Leg three of the SSA-area -> Census-resident -> certified-frame chain; a documentation lookup in microcosm-build that also discharges O7-prime and O16's calibration-status question.",
    "P4_floors_measurements": "Taken in this revision (sections 5.3a and 4.6a) and owed as build deliverables: the recent-arrival Kish effective sample and the closed-vs-open newborn diff. Both are adverse."
  },
  "information_boundaries": {
    "two_boundary_rule": "T*=2014 governs every surface entering the M6 scored path; gate_imm under the certified-frame donor registers against the gate_w1 boundary and lock (gates.yaml:3725-3734, :3732, :3737-3745) and is NOT an M6-boundary gate",
    "inherited_m6_T_star": 2014,
    "gate_imm_reference_period": "2024",
    "trustees_2026_role": "versioned forward assumption and report-only alignment; never gate-estimation evidence",
    "certified_frame_gate_role": "single 2024 reference period; household-disjoint split only; no temporal fence exists under this donor",
    "realized_post_T_star_nawi_on_scored_path": "prohibited"
  },
  "entry_seam": {
    "metadata_key": "m6_scheduled_entries_by_year",
    "definition_pin": "src/populace_dynamics/engine/loop.py:27",
    "contract_pin": "src/populace_dynamics/engine/loop.py:227-266",
    "frame_year": "entry_year - 1",
    "first_entry_year": "strictly greater than start_year; v1 origin 2014, first schedule key 2015",
    "activation": "top of period before mortality (loop.py:271-286 then :297)",
    "new_period_module": false,
    "ids_preassigned": true,
    "entry_kind_vocabulary": ["immigrant_cohort", "maternal_birth", "realized_opener", "incumbent"],
    "synthetic_allocator_start": "engine default is max(initial and all scheduled person_id) + 1 when caller metadata omits the allocator (loop.py:251-257), and that fallback allocator carries an EMPTY reserved set",
    "reserved_real_person_namespace": "freeze before any split as full anchor union every person-keyed fitted support, including both earnings maps, marital attrs, household person keys, and disability-panel person keys",
    "immigrant_id_floor": "1 + max(reserved_real_person_ids union every pre-existing scheduled person_id); preserve unchanged through subsets; STRONGER than the implemented synthetic_id_start at m6_population.py:228, which does not union scheduled opener IDs",
    "f2_status": "MERGED and IMPLEMENTED (PR #221, merge commit 00d5443d9df21ac13e42669d13d94c5ef734134c) at loop.py:44-64, m6_runner.py:432-441, m6_population.py:70-82",
    "seam_gaps_still_open": [
      "the seam never consults reserved_real_ids for scheduled entrant IDs (loop.py:162-168, :236-239, :242-250)",
      "the engine's fallback allocator is constructed with an empty reserved set (loop.py:255-257)"
    ],
    "domain_disjoint_assertion": "immigrant_ids intersect adapter.domain_person_ids is empty for every active earnings adapter before period 1",
    "byte_identity_precondition": "a full-population/original-person byte-identity claim requires checked run_real_person_ids superset fitted_support_person_ids; subset runs do not inherit the claim",
    "caller_allocator_guard": "omit caller allocator or assert next_id exceeds the reserved real-person namespace and every scheduled person_id"
  },
  "design_laws": {
    "U1_uncertainty_nesting": "build one schedule per scenario and schedule seed, reuse it across K conditional engine draws, and vary schedule seeds only as an outer uncertainty dimension",
    "C1_no_unbound_composition_drift": "hold long-run composition at the frozen donor distribution unless a separately sourced and gate-reviewed trajectory is bound; under this donor constant composition is forced, not merely permitted, because there is one band and one reference period",
    "L1_newborn_ordinal_shift": "MEASURED at afd8f44. Scheduled entrants shift every dynamically created row's RNG ordinal by exactly the scheduled-entrant count (loop.py:263-266 pre-seeds the map; loop.py:360 assigns len(person_ordinals)), and the newborn's mortality draw bytes change. An open run makes NO byte-identity claim for synthetic births even within one schedule. No ID floor prevents this.",
    "L2_newborn_id_relocation": "MEASURED at afd8f44. The newborn's person_id itself relocates above the immigrant floor, because the engine's fallback allocator starts at max(all_initial_ids)+1 over the combined universe. Identifying births by ID arithmetic is wrong in an open run.",
    "L3_original_person_stability": "MEASURED at afd8f44. Original-person ordinals and mortality draw bytes are UNCHANGED by scheduling entrants above the floor, confirming the section 4.6 ID-floor claim.",
    "E1_career_refusal": "any entrant reaching build_career must RAISE, not be filtered as excluded_domain_incomplete",
    "E2_aime_api": "the AIME path needs a covered-years or presence-window argument, or a wrapper that refuses a history whose span exceeds the person's US presence",
    "E3_prior_coverage_censored": "prior US covered earnings are unknown/censored, never zero; repeat entry is NOT IDENTIFIABLE under this donor"
  },
  "adjudications": {
    "cohort_control": "positive SSA stock-accounting inflow only; G_resident_entry_proxy for a resident-labeled bound run, raw G_ssa_stock only for an explicitly report-only ssa_area_proxy",
    "projection_origin": "existing 2014 initial slice, first schedule key 2015, control range 2015-2022 for v1; the pinned 2024 frame is an explicitly REJECTED origin because it re-anchors the M6 path",
    "entry_timing": "opening_of_entry_year; unchanged mortality/aging pair; the double-survival correction is made at the AGGREGATE control, never at the person; an entrant-aware wrapper inside the mortality or aging slot is refused for v1",
    "status_adjustment": "aggregate reclassification; not an entrant and not assigned to persons",
    "emigration": "outside entry-builder v1; mandatory successor before net-alignment claim; must also propose how an exit is expressed, since the frozen eight-adapter order has no removal slot but mortality",
    "donor": "certified populace_us_2024 frame; predicate keyed on (source_year, PEINUSYR code) and restricted to PRCITSHP in {4,5}; 2024 vintage code 28 by default",
    "assignment": "donor-based joint assignment with model-based calibration and no cloned future (O16-a); a joint parametric challenger is DEFERRED out of v1 on the measured support",
    "gate_split": "household-disjoint, the gate_w1 pattern; 100 split seeds; NO temporal fence is available under this donor and none is implied",
    "gate_masses": "band-native M_gate[band]; a band is never converted to an entry year for scoring; band splitting is a declared schedule-realization rule and is un-gradeable against the survey",
    "demotion_criterion": "gate_w1's heavy-tail guard floor_max_exceeds_tolerance, not a weight cap",
    "prior_us_covered_earnings": "unknown/censored; never default zero",
    "entrant_fertility": "excluded from fertility risk for v1; a v2 estimand; excluded by an active adapter, not by an absent kernel",
    "entrant_claiming_and_benefits": "EXCLUDED, not disclosed, until an insured-status function exists",
    "rng_isolation": "composite partition required; and no byte-identity claim for dynamically created rows at all (L1/L2)",
    "entrant_reporting": "open-run counters partition schedule rows by entry_kind and births by explicit materialization provenance; whole-schedule opener counts, hardcoded zero immigrants, and ID-arithmetic birth inference are all prohibited",
    "anchor_wave": "PROHIBITED on an immigration frame; build_seed_coordinates excludes immigration frames by an explicit entry_kind filter that fails closed on a frame with no entry_kind at all",
    "legal_status_dynamics": "out of scope",
    "current_entry_only_outputs": "report_only"
  },
  "measurements_taken_in_revision_5": {
    "donor_pool": {"rows": 1155, "households": 562, "weighted_persons": 2345368.4, "vintage": 2024, "peinusyr_code": 28, "arrival_window": [2022, 2024], "arrival_lag_years": 1},
    "referee_pool_reproduced": {"rows": 3835, "households": 1866, "weighted_persons_millions": 8.996, "note": "all-vintage PEINUSYR in {27,28}; reproduces the referee round exactly; NOT the donor"},
    "kish_n_eff": {"frame_wide_persons": 14327.8, "frame_nominal": 166302, "donor_persons": 156.1, "donor_household_weights": 82.0, "best_A1_cell_household_weights": 36.0, "worst_A1_cell_household_weights": 2.7, "cells_below_14": 9, "of_cells": 14},
    "newborn_ordinal_experiment": {"shift_equals_scheduled_count": true, "newborn_rng_bytes_change": true, "newborn_person_id_relocates": true, "original_person_ordinal_unchanged": true, "original_person_rng_bytes_unchanged": true, "N_tested": [1, 7, 100]},
    "trustees_v_a2_2026_intermediate_thousands": {"lpr_inflow": 600, "temporary_inflow": 740, "positive_inflow": 1340, "lpr_outflow": 263, "temporary_outflow": 947, "status_adjustment": 450, "total_net": 130, "entry_only_minus_net_gap": 1210, "identity_checked_rows": 311}
  },
  "gate_imm": {
    "exists_now": false,
    "estimand": "household-disjoint held-out recent-arrival stock-proxy composition on the pinned populace_us_2024 frame",
    "boundary_and_lock": "gate_w1 (gates.yaml:3725-3734, :3737-3745), NOT T*=2014",
    "raw_input": "one certified frame artifact, pinned by artifact_sha256 and build revision",
    "split": "household-disjoint, 100 seeds; members of one household are never split",
    "temporal_fence": "NONE AVAILABLE; this is a transport test, not an out-of-time test, and a PASS may never be read as one",
    "unit_key": ["person_household_id"],
    "absolute_count_input": "none",
    "gate_total_mass": 1,
    "band_masses": "M_gate[band] from the fit side only, under the vintage-keyed predicate",
    "control_leakage": "Trustees, Census, CPS tabulations and every held-out record, weight, total or marginal are prohibited from constructing M_gate; held-out weights enter truth scoring only",
    "count_alignment_gated": false,
    "physical_sample_design": "not chosen; it is the donor predicate's row count",
    "floors_before_thresholds": true,
    "operating_characteristic_before_lock": "MANDATORY and EXPECTED TO FIRE on the measured support",
    "expected_surviving_surface": "two or three cells; the design pre-commits to reporting that rather than widening a threshold",
    "predeclared_support_fallback": "collapse sex within age band before pooling bands, because it costs no vintage coherence",
    "pass_disclosure_required": "at headline prominence: gate_imm certifies TRANSPORT CONSISTENCY to the certified frame's nativity composition, not that composition's external truth; the frame's joints ride outside populace's calibration loss (runs/gate_w1_floors_v1.json:72) and the nativity joints' status is UNESTABLISHED until P3 closes",
    "donor_pin_watch": "any frame bump invalidates the lock; gate_imm carries its own artifact_sha256 and revision and does not inherit gate_w1's",
    "packet_certification": "structural_schema_only",
    "downstream_life_course_certified": false
  },
  "open_items_after_revision_5": [
    "O2: whether the aggregate entry-timing inflation factor is identified from public Trustees text",
    "O3/O7-prime/O11-b/O16: the certified frame's universe definition and source ASEC vintage binding, recorded beside CERTIFIED_PIN (one microcosm lookup; P3)",
    "O8: measure A_MARITL on the 1,155 recent-arrival donor rows; the 0.99 floor at deployment_frame.py:92-99 is frame-wide and not conditional on nativity",
    "O10-d: lift kish_n_eff into a shared helper and add the cluster/unit-weight ESS; nothing in src/ computes either today",
    "O13: whether the frame's 222 person columns contain a birth-history variable; they were enumerated for nativity and marital status only",
    "O14-c: run the M6 closed panel with and without the schedule and diff the gated cells",
    "O14-d: an engine-side reserved-set check on scheduled entrant IDs and a range-checked fallback allocator",
    "O15: whether any runner projects past 2022, and who owns end_year for a separate open-run product",
    "P1: ratify the estimates/ seam amendment in the form section 9.1 decides",
    "merge: the V.A2 snapshot, the nativity reader and the entrant modules currently live on unmerged branch 29aa8c6"
  ],
  "certified_surfaces_untouched": [
    "gate_m6 registry, thresholds, floors, hashes, and closed-panel support",
    "gate_w1 registry, floors, lock and its deployment-frame pin",
    "candidate-16 marital core",
    "candidate-9 household composition object",
    "M4 disability reproduction object",
    "existing age-sex mortality fit",
    "frozen claiming schedule estimated through 2014",
    "certified earnings specifications and section 2.8.3a domain",
    "section 2.8.2g marital domain law",
    "amendment 3h live-roster materialization law",
    "PeriodModules order and ProjectionRNGRegistry",
    "SCHEDULED_ENTRIES_KEY contract and every existing PSID opener row",
    "original closed-support generator order, RNG consumption, and outputs",
    "M7 trust-fund accounting and M8 rules execution"
  ],
  "amendment_history": [
    {
      "revision": 1,
      "date": "2026-07-15",
      "kind": "initial_docs_only_design",
      "changes": [
        "bind immigration activation to the existing scheduled-entry seam",
        "separate gross entry controls from outflows, status adjustments, and net reconciliation",
        "select donor-based entry state provisionally while prohibiting cloned futures",
        "define the EntrantStateBundle and no-certificate-transfer boundary",
        "propose floors-first gate_imm and enumerate external bindings and open referee decisions"
      ]
    },
    {
      "revision": 2,
      "date": "2026-07-15",
      "kind": "pre_pr_adversarial_hardening",
      "changes": [
        "distinguish SSA positive stock-accounting inflows from all physical arrivals and separate the population-universe bridge",
        "label recent arrivals as a survivor/stayer stock proxy and make stock-to-arrival state an unbound bridge",
        "treat possible prior U.S. covered earnings as censored and block unsupported claiming and benefit outputs",
        "block entrant fertility until parity history and an entrant-aware kernel are bound",
        "merge rather than overwrite existing PSID scheduled entries and guard caller-supplied synthetic allocators",
        "require physical-sample and schedule-seed protocols before floors and limit packet PASS to structural/schema completeness",
        "require RNG-isolated composite adapters before any original-person byte-identity claim",
        "expand referee decisions through O14 and pin unresolved external bindings"
      ]
    },
    {
      "revision": 3,
      "date": "2026-07-15",
      "kind": "annual_gate_and_origin_correction",
      "changes": [
        "replace invalid collection-year slicing of five-year ACS PUMS with separately bound annual 1-year files and weights",
        "namespace donor units by survey year and SERIALNO and block annual replicate designs by year",
        "bind annual archive corrections, the 2013 marital concept break, and explicit 2010-2014 earnings normalization",
        "make raw SSA-area versus bridged resident calibration targets conditional and auditable",
        "add component-aware entry timing so year-end-stayer controls cannot receive duplicate source-year survival filtering",
        "add projection-origin decision O15 and require continuous controls from start_year plus one",
        "add blocking marital-household, disability, and earnings initializer bindings",
        "synchronize the machine-readable binding list and preserve mortality and claiming among untouched surfaces"
      ]
    },
    {
      "revision": 4,
      "date": "2026-07-15",
      "kind": "spec_sound_referee_fixes",
      "changes": [
        "adopt pending PR 221 section 2.8.2i F2 by reserving the global fitted real-person namespace before splits and asserting immigrant IDs are disjoint from every earnings adapter domain",
        "name the m6_runner closed-panel entrant counters invalidated by integration and require row-level entry_kind classification for immigrants, realized PSID openers, and materialized births",
        "correct the ACS 2012 and 2014 person-archive Last-Modified dates and require header confirmation plus raw-hash binding at acquisition",
        "pin gate mode to a unit-mass reported-entry-duration mix C[s,d]/q[d] derived only from 2010-2013 ACS training weights, with O10 supplying physical sample design",
        "add O16 for donor-versus-joint-parametric assignment and label uncertainty nesting U1 and no-unbound-composition-drift C1 as explicit design laws",
        "mark the amendment 3h condensation as a paraphrase, the Trustees glossary PDF page pin confirm-at-fetch, and the actual family-B publisher line span",
        "re-derive M6 wage-index design pins against merged master c6a3c78"
      ]
    },
    {
      "revision": 5,
      "date": "2026-09-06",
      "kind": "referee_round_fold_and_three_blocking_changes",
      "changes": [
        "D-1: rewrite the donor half in certified-frame vocabulary (sections 2.2, 5.2, 5.3, 5.4, O3, O6, O7, O10) and preserve the ACS apparatus verbatim as Appendix A",
        "D-2: extend section 9.1 to estimates/career.py and estimates/preparation.py, the two live scheduled_entries_by_year consumers added after the revision-4 baseline, and DECIDE the anchor_wave conflict by exclusion rather than by widening a PSID concept",
        "D-3: record PR #221 as merged with F2 implemented, record Table V.A2 as acquired and parsed rather than quoted, and state the newborn-ordinal consequence as measured design law L1-L3",
        "fold every O1-O16 resolution with its evidence, and record the open item where the round could not decide from the artifact",
        "re-pin the whole document from baseline 75d30dd to head afd8f44 and add the drift table at section 3.1a, which resolves the revision-4 pins at the revision-4 baseline rather than scoring them as errors; complete the single parity citation marital.py:313 (correct at baseline, now :363) with the two further mechanisms O13-a needs",
        "adopt the two-boundary rule: gate_imm registers against the gate_w1 boundary and lock, not T*=2014, and NO temporal fence exists under this donor",
        "make the entrant claiming and benefit exclusion a hard exclusion with named mechanism (E1-E3), because the statutory oracle zero-pads rather than refusing",
        "lift the horizon into prerequisite P2 with the fail-closed parameter series named, and record that the built artifact's 2026-2035 window is not the v1 2015-2022 window",
        "take the two measurements the round named as decisive: the recent-arrival Kish effective sample (sections 5.3a) and the closed-vs-open newborn diff (section 4.6a)",
        "replace 'verification pending' with four named prerequisites P1-P4"
      ]
    }
  ]
}
```

## Appendix A. The ACS-first donor branch (revision 4 text, preserved verbatim)

The donor fork was adjudicated **certified-frame-first** by the plan owner, and
the referee round took that adjudication as settled rather than re-litigating it.
This appendix preserves revision 4's ACS-first apparatus **verbatim and unedited**
so that nothing is lost and reversing the fork costs a re-read rather than a
rewrite (O6-c). Nothing in this appendix is current design law. Its pins resolve
at the revision-4 baseline `75d30dd57d71b91ee0929246b2f3cbb92263b350`, not at
`afd8f44`, and its `§` cross-references are to revision 4's own numbering.

**Why it is not v1.** `data/external/` (56 entries) holds no ACS artifact; a grep
for `acs_pums|PUMS|PWGTP|YOEP|SERIALNO|ADJINC` across `src/` and `scripts/`
returns only CPS-ASEC firm-size hits. A builder handed the text below could not
start §9.2 step 3, because the artifact it names does not exist here and the
annual pooling branch it must select is undefined on a single file. Adopting it
is a greenfield acquisition (five annual files, replicate weights, per-year
crosswalks, two errata, one concept break), and it is the named successor that
buys annual arrival resolution.

**What would restore it.** An ACS acquisition PR that commits and hash-binds the
five annual person archives. On that day O3, O6, O7 and O10 revert to the
revision-4 text reproduced in §A.5, §5.2–§5.4 revert to §A.2–§A.4, and the
binding rows of §A.6 return to §6.2 with their status unchanged.

---

### A.1 Revision 4 §2.2 — public microdata: roles and limitations

| Source | Exact public support | V1 role | Binding limitation |
|---|---|---|---|
| ACS PUMS | Census annual 1-year person PUMS files for [2010](https://www2.census.gov/programs-surveys/acs/data/pums/2010/1-Year/csv_pus.zip), [2011](https://www2.census.gov/programs-surveys/acs/data/pums/2011/1-Year/csv_pus.zip), [2012](https://www2.census.gov/programs-surveys/acs/data/pums/2012/1-Year/csv_pus.zip), [2013](https://www2.census.gov/programs-surveys/acs/data/pums/2013/1-Year/csv_pus.zip), and [2014](https://www2.census.gov/programs-surveys/acs/data/pums/2014/1-Year/csv_pus.zip); annual dictionaries [2010](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMSDataDict10.pdf), [2011](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMSDataDict11.pdf), [2012](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMSDataDict12.pdf), [2013](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMSDataDict13.pdf), and [2014](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMSDataDict14.pdf); and corresponding annual Accuracy statements ([2010](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/accuracy/2010AccuracyPUMS.pdf), [2011](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/accuracy/2011AccuracyPUMS.pdf), [2012](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/accuracy/2012AccuracyPUMS.pdf), [2013](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/accuracy/2013AccuracyPUMS.pdf), [2014](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/accuracy/2014AccuracyPUMS.pdf)). The *[2010–2014 PUMS dictionary](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2010-2014.pdf)* is crosswalk evidence only. The *[2014 ACS Subject Definitions](https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2014_ACSSubjectDefinitions.pdf)*, “Year of Entry,” pp. 128–129, documents response ambiguity. | Primary joint-stock donor and gate truth only for the named stock-proxy surface. Fit 2010–2013 with each annual file's `PWGTP` and replicate weights; hold the separately weighted 2014 file out in full. Bind annual `YOEP`, `POBP`, `AGEP`, `SEX`, `RELP`, education, disability, employment and earnings concepts. | A recent-arrival respondent is a resident survivor/stayer observed at interview, not a gross arrival. Interviewers request the most recent entry, but unclarified/mail answers can be first or most recent. `WAGP` covers the prior 12 months, possibly including pre-entry months. `RELP` identifies relationship to the reference person, not arbitrary relationship pointers. The gate never uses 5-year pooled weights. Current 2010/2011 bytes are corrected Mar. 4, 2013 re-releases ([erratum 87](https://www.census.gov/programs-surveys/acs/technical-documentation/errata/087.html)); the current 2013 person archive was reposted Feb. 12, 2015 alongside a housing-only `MV` correction ([erratum 97](https://www.census.gov/programs-surveys/acs/technical-documentation/errata/097.html)). The [2013 same-sex married-couple user note](https://www.census.gov/programs-surveys/acs/technical-documentation/user-notes/2013-03.html) is a marital/family concept break. Exact bytes/correction status and observation versus release date remain bound/O6 decisions. |
| CPS ASEC | Census, *[2014 Traditional ASEC technical documentation](https://www2.census.gov/programs-surveys/cps/techdocs/cpsmar14.pdf)* or *[2014 Redesigned ASEC technical documentation](https://www2.census.gov/programs-surveys/cps/techdocs/cpsmar14R.pdf)*: the cited Redesigned layout has demographics p. 65; six disability items pp. 68–69; `PENATVTY`, grouped `PEINUSYR`, `PRCITSHP`, `MARSUPWT` p. 69; wage/salary and earnings pp. 77, 83. | Report-only marginal and earnings triangulation. | Smaller civilian noninstitutional universe plus Armed Forces members living in civilian housing; grouped entry years; survey-date demographics versus prior-calendar-year income. Traditional and Redesign files must never be silently combined. |
| SIPP | Census, *[2014 SIPP Metadata, all sections v2](https://www2.census.gov/programs-surveys/sipp/tech-documentation/data-dictionaries/2014/w1/2014SIPP_Metadata_AllSections_v2.pdf)*: `WPFINWGT` p. 9; marital status p. 23; age p. 30; nativity/citizenship pp. 35–37; grouped `TYRENTRY` and entry-status item `TIMSTAT` pp. 38–39; education p. 42; sex p. 43; disability p. 1368; monthly earnings p. 2766. | Report-only joint-state and initializer plausibility check. | Wave 1 covers the 2013 reference year and a civilian-noninstitutional universe. Later waves do not represent newly arrived immigrant-only households, although new co-residents of original sample people can enter. `TIMSTAT` is neither a legal-history panel nor authority to model status and is excluded from v1 state. |

For the exact ACS person-archive URLs above, the server currently reports
`Last-Modified` dates of Mar. 4, 2013 for the corrected 2010/2011 archives,
Dec. 11, 2013 for 2012, Feb. 12, 2015 for the current 2013 archive, and Oct. 6,
2015 for 2014. These mutable headers must be confirmed at acquisition; the
committed raw SHA-256 values, not an HTTP date, bind the actual bytes. Oct. 27,
2015 is the 2014 Accuracy statement's server date and is not the person archive's
vintage.

The ACS donor predicate is named, not implied:

```text
foreign_born == true
and 0 <= survey_year - reported_year_of_entry <= recent_arrival_max_duration
```

`survey_year` comes only from the bound annual-file manifest; `SERIALNO` is a
within-file household/GQ identifier and contains no year. Annual `YOEP` supplies
the reported year. The training unit key is therefore
`(survey_year, SERIALNO)`. The initial proposal is a 0–4 year window, but the
exact duration, annual-pooling rule, and fallback hierarchy remain decision O3.
The extractor must bind allocation-flag treatment, top/bottom-code treatment,
group-quarters policy, per-year schema crosswalks, replicate weights, and the use
of `ADJINC` before any artifact can be certified.

This predicate defines a resident **stock proxy**, not entry-time truth. Education,
marriage, disability, employment, earnings, survival, and residence may all
change between reported entry and interview. Directly copying that state onto an
entry-year row is only a named report-only initializer. A literal arrival-state
claim requires the separately bound stock-to-arrival bridge in §6.2/O12.

### A.2 Revision 4 §5.2 — temporal split and leakage fence

The primary proposed split uses five separately released annual ACS 1-year PUMS
files:

- fit donor construction and all matching/calibration choices on the 2010–2013
  annual files using each year's own person and replicate weights, with equal-
  year-mass versus population-mass pooling and cross-year normalization frozen
  from training only;
- freeze the candidate artifact and surface;
- generate a synthetic 2014 recent-arrival resident cross-section without
  reading any 2014 person record, weight, or marginal; and
- score against the separately weighted annual 2014 file using the same recent-
  arrival predicate, concept map, universe, and annual-weight treatment.

The gate-mode cohort-size/duration-mix input is pinned. Let training years
`S = {2010, 2011, 2012, 2013}` and let O3 freeze the supported reported-entry-
duration bins `D`. Using only each training file's own person weights, compute

```text
C[s,d] = sum_i PWGTP[s,i] * 1[
    i satisfies the recent-arrival predicate and duration_bin(i) = d
]

q_equal[d] = mean_s(C[s,d] / sum_k C[s,k])
q_population[d] = sum_s C[s,d] / sum_s,k C[s,k]
q[d] = the O3-selected branch, with sum_d q[d] = 1
```

Before any 2014 access, store and hash `C`, `q`, the pooling branch, support, and
demotions in `ImmigrationDonorArtifact`. For the sealed 2014 candidate, the gate
pipeline uses the normalized reported-entry stock-cohort masses

```text
M_gate[reported_entry_year = 2014 - d] = q[d]
gate_total_mass = 1
```

for exact one-year duration bins; any O3-pooled duration bin retains its explicit
bin label rather than inventing a single entry year. These are reported-entry
**stock-proxy** masses, not literal arrivals, engine `entry_year` values, or an O12
arrival bridge. The gate invokes the complete donor-selection, calibration,
fallback, seed-grid, and schedule-realization pipeline in this normalized stock-
evaluation mode. O10 supplies its physical unit count, weight caps, and
calibration constraints; no absolute population-count target exists in gate
mode.

Households/arrival units keyed by `(survey_year, SERIALNO)` are indivisible. The
2014 truth and candidate each normalize to unit mass before characteristic
scoring; absolute total is not a gate cell. Each training-era pseudo-holdout
recomputes `C` and `q` from its fit side only. No 2014 record, weight, total,
marginal, or holdout-informed top-code treatment; no CPS/SIPP statistic; and no
current Trustees assumption or Census projection may construct the gate input.
The 2014 weights enter only truth scoring after lock. The 2010–2014
5-year PUMS is prohibited from both fitting and truth: its five-year weights
represent/rerake to the pooled period, so slicing it by survey year would neither
recover annual truth nor preserve the leakage fence. The 2013 same-sex married-
couple edit change is frozen in the per-year concept map. Marital/family cells
must harmonize to a definition stable across all five annual files or be demoted
before the truth floor; a dictionary crosswalk alone is not evidence of
longitudinal concept invariance.

The annual files are observations at or before `T*`, but at least the 2014 file
was released after its observation year. Decision O6 must ratify an observation-
date rule analogous to the M6 NAWI publication-lag reasoning or reject every
post-boundary release. Rejection pauses the gate; it does not silently move the
boundary or fall back to the pooled file.

Later ACS windows, including 2015–2019 and 2020–2024, are temporal-drift stress
tests only under this gate. Refitting on them creates a new production artifact
to which no exact-artifact certificate automatically transfers.

### A.3 Revision 4 §5.3 — floors before thresholds

The ceremony order is mandatory:

1. Using training-only power analysis, freeze the recent-arrival predicate,
   donor/simulation unit, physical annual sample size, weight caps, calibration
   constraints, fallback limits, schedule-seed grid and aggregation/conjunction
   rule, concept map, matching ladder, `C[s,d]` construction, O3-selected `q[d]`
   pooling branch, duration support/demotion rules, unit-mass convention, gate
   cells, metrics, and weighting rules without candidate holdout results.
2. Construct a correlation-respecting real-vs-real floor from deterministic,
   household-disjoint splits or the annual 2014 replicate-weight design. Never
   split members of one `(survey_year, SERIALNO)` unit. Training uncertainty
   treats each year's replicate set as a separate block; replicate columns are
   never concatenated across years as one common design.
3. On training-era pseudo-holdouts only, run the complete donor-selection,
   calibration, fallback, and schedule pipeline across the registered seed grid,
   recomputing `C` and `q` from that pseudo-holdout's fit side only. Freeze how
   candidate-pipeline variability combines with the truth-side floor; no
   favorable single schedule seed can define a PASS.
4. Publish, for every proposed cell, raw person count, raw unit count, person-
   weight Kish ESS, cluster/unit-weight ESS, replicate-design variance,
   denominator, allocation share, top-code share, and both truth-side and
   pipeline distance distributions. The binding support measure is the most
   conservative applicable unit/design quantity, not person ESS alone.
5. Prune, pool, or demote every cell that fails predeclared support or whose floor
   is unstable. Record each demotion; do not widen a threshold to retain it.
6. Price thresholds from the surviving empirical floors using a predeclared
   transform. No numerical tolerance is assumed by this design.
7. Run an operating-characteristic experiment on the surviving conjunction
   using predeclared degraded pseudo-candidates. If power is weak or the gate is
   near-tautological, pause and redesign before any lock.
8. Only then score the registered candidate and, if it passes, bind the exact
   artifacts, floor, registry, code commit, and hashes.

This order is the M6 floors-before-thresholds law. Sparse single-age MINT6 cohorts
and the ACS weighted/unit structure make it substantive, not ceremonial.

### A.4 Revision 4 §5.4 — candidate gate surface

The floor ceremony may consider these predeclared families:

| Family | Candidate observables | Candidate metric |
|---|---|---|
| Demographic | broad derived reported-entry-age proxy × sex shares; reported-entry-duration proxy; broad source region | total-variation or weighted absolute-share distance |
| Education | attainment band overall and by broad age/sex | total-variation distance |
| Family state | marital-state shares; constructed co-resident same-reported-entry unit size; spouse/child same-reported-entry co-residence indicators | total-variation distance, unit-weighted where applicable |
| Employment | employed/unemployed/NILF; zero earnings; work-intensity bands | absolute-share or total-variation distance |
| Positive earnings | `WAGP`/earnings normalized under the pinned economic index, p10/p50/p90 and log spread | floor-scaled log-quantile distance |
| Disability proxy | the six ACS question concepts individually and “any” | absolute-share distance; never named DI status |
| Named joints | derived reported-entry-age proxy × sex × education; sex × marital state × reported-entry-duration proxy; education × employment/earnings band | pooled-cell total-variation distance |

The final registry contains only cells that clear the floors. Fine source-region,
single-age, detailed education, high-order family, and earnings-tail cells are
presumptively report-only until their support proves otherwise.

`reported_entry_duration_proxy = survey_year - reported_year_of_entry`; a
derived age proxy subtracts that duration from interview age under a frozen age/
birthday convention. Neither is literal duration or age at arrival, and neither
can certify O12's arrival-state bridge. The constructed unit is a co-resident
same-reported-entry unit, never a claimed historical travel party.

### A.5 Revision 4 O3, O6, O7 and O10 — verbatim

#### Revision 4 O3. Recent-arrival window and matching ladder

Ratify the proposed 0–4-year **reported-entry** window or a different duration;
decide whether duration-zero/one donors receive priority; and freeze age/source/
education/family matching cells, annual pooling/replicate-block treatment,
same-sex-marriage concept harmonization, and fallback order. The pooling choice
also selects `q_equal` or `q_population` in §5.2 before 2014 is opened. Repeat-
entry identification and prior U.S. coverage belong to O12.

#### Revision 4 O6. Observation date versus publication date at `T*`

The proposed annual ACS files contain 2010–2014 observations, but the person-
archive server `Last-Modified` dates are Oct. 6, 2015 for 2014; Mar. 4, 2013 for
the corrected 2010/2011 bytes; Dec. 11, 2013 for 2012; and Feb. 12, 2015 for the
current 2013 archive whose associated erratum affected only a housing-file
variable. Confirm those headers and bind the raw hashes at acquisition. Ratify
an observation-date rule analogous to the M6 NAWI publication-lag reasoning, or
reject every file whose byte vintage crosses the boundary and redesign an earlier
annual holdout. The five-year pooled file is not an alternative under either
rule. The same issue affects later-published SIPP metadata, which is report-only
here.

#### Revision 4 O7. CPS ASEC diagnostic vintage

Choose Traditional or Redesign 2014 ASEC public-use data and bind its correction
history. This affects report-only triangulation, not candidate fitting or gate
truth.

#### Revision 4 O10. Physical cohort size and calibration constraints

Freeze annual physical unit counts, weight caps, calibration margins and maximum
fallback share through training-only power analysis **before** truth floors are
constructed. The floor may prune an infeasible surface, but it may not
candidate-adaptively choose the sample design. No arbitrary “one row per N
people” constant is adopted here. In gate mode these choices realize the unit-
mass `q[d]` target in §5.2; they do not introduce an absolute cohort-count input.

### A.6 Revision 4 binding rows and extractor guards that named ACS

The binding-ledger rows, verbatim (revision 4 §6.2):

| Binding ID | Exact source and vintage | Fields/transformation | Consumer and status |
|---|---|---|---|
| `acs_pums_annual_2010_2014_recent_arrivals` | Census Bureau annual 1-year person PUMS `csv_pus.zip` files for survey years 2010–2014, with exact URLs, annual dictionaries and annual Accuracy statements in §2.2; 2014 Subject Definitions “Year of Entry,” pp. 128–129. The exact person-archive URLs currently return server `Last-Modified` dates of Mar. 4, 2013 for the corrected 2010/2011 bytes (erratum 87), Dec. 11, 2013 for 2012, Feb. 12, 2015 for the current 2013 bytes associated with housing-only erratum 97, and Oct. 6, 2015 for 2014; confirm those headers at acquisition and bind raw SHA-256 hashes. | Bind each file/hash/release/correction status separately. Set survey year only from its manifest; namespace units as `(survey_year, SERIALNO)` and validate `SERIALNO` within file. Bind annual `PWGTP`/replicate weights, `ADJINC`, `AGEP`, `SEX`, `YOEP`, `POBP`, `NATIVITY`, `RELP`, education, disability, employment, income/earnings and allocation flags. Fit 2010–2013 and derive/hash the §5.2 training-only `C[s,d]`/`q[d]` duration mix; seal annual 2014. The 2014 file may enter truth scoring only. The 5-year PUMS and weights are prohibited. | Primary resident survivor/stayer stock donor, sole unit-mass gate-mode cohort-mix input, and proposed `gate_imm` truth, conditional on O6; no absolute gate count and never literal arrival-state truth. |
| `acs_stock_to_arrival_state_bridge` | **UNBOUND.** No cited ACS cross-section identifies state at the arrival instant or everyone who subsequently left/died. | Must pin a duration/backcast law, survivor/stayer selection adjustment, reported-entry ambiguity treatment, repeat-entry identification and source vintage. An identity mapping is labeled `stock_proxy` only. | **BLOCKING** for literal entry-time characteristics; decision O12. |
| `cps_asec_2014_foreign_born` | Census Bureau, *[2014 Traditional ASEC technical documentation](https://www2.census.gov/programs-surveys/cps/techdocs/cpsmar14.pdf)*, *[2014 Redesigned ASEC technical documentation](https://www2.census.gov/programs-surveys/cps/techdocs/cpsmar14R.pdf)*, and [2014 ASEC data page](https://www.census.gov/data/datasets/time-series/demo/cps/cps-asec.2014.html). Calendar-year 2013 income, 2014 interview characteristics. | `A-AGE`, `A-MARITL`, `A-SEX`, `A-HGA`, six disability items, `PENATVTY`, grouped `PEINUSYR`, `PRCITSHP`, `MARSUPWT`, `WSAL-VAL`, `PEARNVAL`, `PTOTVAL`; civilian noninstitutional population plus Armed Forces members in civilian housing. Bind Traditional **or** Redesign bytes and correction/repost status. | Report-only marginal triangulation. Exact file choice is O7; the two designs may not be combined silently. |

The ACS extractor guard, verbatim (revision 4 §6.3):

The ACS extractor must resolve five separate annual manifests, set and validate
`survey_year` from the manifest/path alone, namespace household/GQ linkage by
`(survey_year, SERIALNO)`, map that annual vintage's `YOEP` and `POBP`, use
only that file's person and replicate weights, and publish allocation/top-code/
group-quarters counts. It must hard-fail on a 5-year pooled input. It must use
`reported_year_of_entry`: the intended interviewer concept is most recent entry,
while unclarified/self responses may mean first or most recent entry.
`first_entry_year` is prohibited without another source.
The concept-map manifest must also name the 2013 same-sex married-couple edit
break and its common-definition harmonization or explicit report-only demotion.
The gate-derived artifact must assert source years exactly `{2010, 2011, 2012,
2013}`, finite nonnegative `C[s,d]` and `q[d]`, supported O3 duration bins, and
`sum_d q[d] = 1` within a pinned numerical tolerance. Its provenance must contain
no 2014 row, weight, total, or marginal; each pseudo-holdout repeats the same
assertions with only its fit-side years.

## Appendix B. Verification record for revision 5

Revision 5 makes many more repository claims than revision 4, across **two**
revisions rather than one. This appendix records how each was checked and what
was not checked, so that a referee can reproduce the check rather than trust it.

### B.1 The two revisions, and which pins live where

| Revision | Ref | Role | Pins |
|---|---|---|---:|
| `afd8f44838c71bca1ce558ffcff5e7701b94f791` | `origin/master`, 2026-09-06 | The reading tree. Every pin resolves here unless its sentence names another revision. | 451 |
| `29aa8c6c96a39ecab71af86f01859d53a71f9c0c` | `cap/entrant-schedule`, committed and **not pushed** | The entrant-schedule build. Four modules and their artifacts exist only here. | 61 |
| `75d30dd57d71b91ee0929246b2f3cbb92263b350` | revision 4's declared baseline | **The left column of §3.1a only.** Those are revision-4 pins and are resolved *there*, which is what makes §3.1a a drift table rather than an error list. | 34 |

**The pins that are not on `master`.** A reader must know which claims depend on
unmerged work, so they are listed rather than left to be discovered:

| File @ `29aa8c6` | Citations in this document | What depends on it |
|---|---:|---|
| `src/populace_dynamics/data/nativity_frame.py` | 39 | the donor predicate, the vintage-keyed band table, the code labels, the populated guard, the band-split rule — §2.2, §4.5, §5.2, §6.3, O3, O7′ |
| `src/populace_dynamics/data/trustees_immigration.py` | 12 | the V.A2 control, its identity assertions and the `positive_inflow`-only accessor — §2.4, §4.3, §6.2, §6.3, O1 |
| `src/populace_dynamics/engine/entrant_domains.py` | 6 | the four exclusion adapters and the earnings-domain assertion — §4.7, §4.9, §4.11 |
| `src/populace_dynamics/engine/entrant_schedule.py` | 4 | the `entry_kind` vocabulary, the reweighting sizing rule and the provenance counters — §3.1, §4.3, §4.7, §6.3 |

Also on that branch and cited by digest rather than by line:
`data/external/snapshots/trustees_va2_vintage1/trustees2026_lr5a2.html`
(sha256 `5dfd05e5…89da`), its `capture_manifest.txt`,
`data/external/trustees2026_lr5a2.source.provenance.json`, and
`runs/entrant_schedule_v1.json`.

**Merging that branch is a precondition of a build, not of this design.** Nothing
in §0's P1–P4 depends on the merge; the merge is listed separately in §11's
`open_items_after_revision_5`.

### B.2 How the pins were checked

A checker script (in the revision packet, **not committed** — it lives under the
worktree's `scratch/`) parses every `` `path:line` `` and continuation `` `:line` ``
citation out of this document, resolves each path to a repository path, selects
the revision, and opens the bytes with `git show <rev>:<path>`. It refuses to
carry a continuation pin across a line boundary, so a bare pin of the form
`:NNNN` can only ever refer to a path named earlier in the same paragraph, and
never to one named in a different paragraph, table row, heading or code block.

Two levels of check are applied:

1. **Resolution** — the path exists at the selected revision and the cited span is
   within the file. **546 citations, 0 unresolved and 0 unattributable**, across
   39 files and the three revisions above. 240 of the 546 are bare continuation
   pins resolved from a path named earlier in the same paragraph; they are
   reported separately by the script so they can be reviewed by eye rather than
   trusted.
2. **Content** — for the load-bearing pins, the resolved line must *contain the
   thing the design says it contains*, so that "resolves" cannot degrade into
   "is in range". **87 assertions, 0 failures.** They cover every seam-contract
   line, both fail-closed raises in `advance_age`, the claiming selection, the
   newborn-ordinal assignment, the ordinal-is-the-address docstring, the
   zero-padding in `aime()`, both `"immigrant_cohorts": 0` sites, the
   `anchor_wave` requirement and assertion, the domain-incomplete exclusion, the
   three parity citations, the frame pin in code and in `gates.yaml`, the
   household-disjoint split rule, `kish_n_eff`, and the two `runs/` sentences.
   Nine of the 97 are **baseline** assertions that prove the §3.1a mapping
   itself — for example that `loop.py:111` was `class PeriodModules:` at
   `75d30dd` and is `:118` at head, and that `marital.py:313` really did carry
   `parity = np.zeros(len(attrs), dtype=np.int64)` there before moving to
   `:363`.

Appendix A is excluded from the check by design: it is revision-4 text preserved
verbatim, and its pins resolve at the revision-4 baseline
`75d30dd57d71b91ee0929246b2f3cbb92263b350`, which is exactly what "preserved
verbatim" means.

**Two claims inherited from the referee round did not survive this check, and are
corrected rather than carried.**

*First,* the round characterised
`src/populace_dynamics/firms/banding.py` as keeping two code→interval maps
"because 'the 2019+ dictionary band break is a different variable'". Opening the
file shows the opposite conclusion: the 2019+ relabeling is "a documentary
relabeling only — the instrument is unchanged" (`firms/banding.py:66-67`) and
"phantom" (`:257`). The two maps (`:246-253`, `:265-276`) exist to *correct* a
dictionary error, not
to track a real instrument change. §2.2 and O7 state the corrected version, which
is the stronger point for O7′: a cross-vintage difference in an ASEC code book may
be real or documentary, and only reading the dictionaries distinguishes them.

*Second,* the round attributed revision 4's instruction "Until PR #221 lands, an
integration must implement the equivalent explicit floor" to revision 4's §2.6.
Opening `docs/design/immigration_module.md` at `152d087` shows that sentence at
lines 510–511, under the heading `### 3.5`. §3.1 cites **§3.5**. The substance is
unaffected — the instruction is stale either way, because PR #221 merged and its
F2 is implemented — but a specification that mis-cites its own predecessor invites
an implementer to go looking in the wrong place.

Both corrections are the reason this appendix exists: a fold is only as good as
the bytes behind the claims it folds, including the referee's own.

### B.3 The two measurements, and how to reproduce them

Both were run for this revision and are reported in the body. Neither is a
committed artifact; both are owed as build deliverables (P4).

**M1 — recent-arrival support and Kish effective sample (§5.3a).** Resolve the
pinned frame from the local Hugging Face cache by `CERTIFIED_PIN`, load it through
`nativity_frame.load_nativity_persons`, and compute row, household and
`w.sum()**2 / (w**2).sum()` figures for the donor pool, the pooled alternatives
and each proposed A1 cell. The frame-wide result reproduces the committed
`runs/gate_w1_floors_v1.json:72` figure ("Kish n_eff ~ 14.3k of 166k nominal") at
14,327.8 of 166,302, which is the check that the quantity is the same one the
`gate_w1` precedent uses. The all-vintage `PEINUSYR ∈ {27,28}` pool reproduces the
referee round's 3,835 persons in 1,866 households exactly.

**M2 — the closed-vs-open newborn diff (§4.6a).** A ~130-line script builds the
minimal roster the round proposed — one real person, one scheduled birth, `N`
scheduled immigrants above an ID floor — runs `ProjectionEngine` at `afd8f44`
twice, and compares the newborn's `person_id`, RNG ordinal and mortality draw
bytes, plus the original person's. Run at `N ∈ {1, 7, 100}`. It is a synthetic
harness, not a certified run: it establishes the addressing consequence (L1–L3),
**not** the effect on any gated cell, which is O14-c's separate measurement on the
real closed panel.

### B.4 What was not verified

Stated plainly rather than left implicit.

- **The V.A2 numeric values were not re-fetched.** `ssa.gov` returns HTTP 403 to
  this environment. They are verified against the **committed snapshot** and its
  digest, and the parse independently reproduces revision 4's separately quoted
  table; that is a strong internal check and it is not a re-fetch.
- **No gate, floor or certified run was executed.** M1 and M2 read a pinned
  artifact and drive a synthetic engine harness respectively.
- **The recent-arrival `A_MARITL` fraction was not measured** (O8's open item).
- **The certified frame's universe definition was not read** (P3): it is in
  microcosm-build, not in this repository.
- **The 17.96 % foreign-born share was not compared to a published figure.** It is
  reproduced from the pinned blob; no external comparison was obtained, and this
  design will not quote one from memory (§5.5).
- **The frame's 222 person columns were not exhaustively enumerated** for a
  birth-history variable (O13's open item); they were read for nativity and
  marital status only.
