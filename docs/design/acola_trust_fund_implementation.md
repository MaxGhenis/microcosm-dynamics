# A-COLA trust fund test: implementation note (Registration 18, d658)

This note maps every element of Registration 18 to the code and tests
that implement it, states the invariants the build relies on, and lists
every interpretation the build made where the registration leaves a
detail open. The second registration comment discloses each
interpretation before the run.

- **Registration.** Issue #42, comment 5919983573
  (`https://github.com/PolicyEngine/microcosm-dynamics/issues/42#issuecomment-5919983573`),
  authorized by decision d658 (Max, 2026-09-30). Report-only: no pass
  band, no acceptance rule, publishes regardless.
- **Verbatim specification.** `docs/design/acola_registration18.md`,
  SHA-256 `02287d54f12285c8dffcb94ba7dae9cbe3cc34ba338c602a5ad4afe14d598f20`
  (37,425 bytes). It is the UTF-8 encoding of the comment's `body`
  string as the GitHub API returns it, with no trailing newline.
  `gh api repos/PolicyEngine/microcosm-dynamics/issues/comments/5919983573 --jq .body`
  prints the same bytes followed by one newline, which `--jq` appends.
  The comment's `created_at` and `updated_at` are both
  2026-09-30T21:23:35Z, so it has not been edited. The SHA-256 is pinned
  in `acola_track/config.py` (`SPECIFICATION_SHA256`) and checked by the
  entry script's preflight and again by the runner.
- **Blindness.** Every number in this note is a model input, arithmetic
  on the specification, a file hash, a count or a line of code. No
  comparator value was read.

## Layout

| Path | Role |
|---|---|
| `src/populace_dynamics/acola_track/config.py` | the row registry (C0, C1, C0-D deferred, M0-M4), `ACOLAConfig`, the specification binding and the d658 authorization record |
| `src/populace_dynamics/acola_track/runner.py` | `run_acola`: guards, one projection per draw, mechanism L benefit rows per row, the statistics, nulls, context item and gaps |
| `src/populace_dynamics/acola_track/statistics.py` | P, the OASI and DI split, the spouse memo, the MINT-band statistics, the weighted median and the A7 floors |
| `src/populace_dynamics/acola_track/nulls.py` | the spec-only nulls and the two narrow Trustees Report extractions |
| `scripts/run_acola_registered.py` | the guarded one-shot entry script (`preflight`, `DEFAULT_OUTPUT`) |
| `scripts/compare_acola.py` | the comparison lane's script (standard library only) |
| `scripts/build_acola_spec_only_nulls.py` | writes `docs/design/acola_spec_only_nulls.json` |
| `scripts/capture_tr2026_v_c1.py` | the TR 2026 Table V.C1 capture |
| `data/external/snapshots/tr2026_v_c1_vintage1/` | the captured V.C1 table fragment and its COLA timing footnote |
| `tests/acola_track/` | every new test (invented data only) |

The artifact is `runs/trust_fund_acola_2030_v1.json` with the sidecar
`runs/trust_fund_acola_2030_v1.env.json`. Neither exists until the one
shot runs.

## Registration elements and where they live

| Registration element | Code | Tests (`tests/acola_track/`) |
|---|---|---|
| Rows C0, C1, M0-M4; one field changed per alternative | `config.REGISTERED_ROWS`, `ACOLARow.track_row` | `test_config.py::test_all_registered_rows_have_the_registered_fields`, `::test_each_alternative_changes_exactly_one_registered_field` |
| C0-D registered, deferred, never run | `config.DEFERRED_ROWS`; `ACOLAConfig` refuses it; artifact `deferred_rows` | `test_config.py::test_deferred_D_has_a_full_spec_and_cannot_run`; `test_runner.py::test_whole_invented_run_has_every_row_memo_null_and_label` |
| R0's population, wave 2011, opening year 2010, closed cohort | `ACOLAConfig.track_a_config()` returns `TrackAConfig(rows=("R0",), ...)`; the runner never calls `run_track_a` | `test_config.py::test_projection_composes_R0_without_extending_its_registry` |
| K = 20 draws, seeds 5200 + k; base and reform from one projected state | `ACOLAConfig.draw_indices`; one `_project_population` per run; one `StateLookups` and one `pia_cache` per draw shared by every row | `test_runner.py::test_projection_once_per_draw_with_shared_lookups_and_cache`, `::test_same_draw_seed_is_deterministic`; `test_timing_properties.py::test_registered_draw_root_and_module_stream_are_deterministic` |
| Eligibility clock; entitlement clock on M3 | `ACOLARow.exposure_clock` | `test_timing_properties.py` (both start-year tests) |
| Calendar-year payments; December × 12 on C1 and M2 | `ACOLARow.benefit_period` | same |
| Five components | `PRIMARY_COMPONENTS` | `test_statistics.py::test_component_accounting_and_spouse_three_classes` |
| TR 2008 baseline COLA path to 2030 | the entry script's `tr2008_baseline_cola`; `_parameter_consistency` with committed-value checks | `test_runner.py::test_registered_real_requires_committed_parameter_values` |
| REFUSE, reported not hidden | runner `_check_floor` (strictly positive reduced rates through 2030, before any projection); a `ValueError` from the emitter refuses that row and draw, recorded with its message and class | `test_runner.py::test_reduced_rate_floor_refuses_before_projection`, `::test_refused_row_is_published_with_every_null_statistic` |
| Opening stock frozen at 2010 (d075) | carried by `TrackAConfig`; `check_registered` refuses any departure | `test_config.py::test_invalid_config_refuses` |
| Labels plus "report-only" | `config.LABELS`; each row's `labels`; legacy label check | `test_runner.py::test_source_seal_and_labels_are_checked_before_projection` |
| P = 100 (T_reform − T_base) / T_base over S_s | `statistics._cost_cell` | `test_statistics.py::test_ratio_means_and_union_differential_against_existing_functions` |
| Mean of P over draws, draw SD (ddof 1), A7 floor | `statistics._summarize`, `_summary`, A7 `_draw_summary` and `_floor_summary` | `test_statistics.py::test_draw_sample_sd_and_weight_variation_are_reported`, `::test_cost_floor_matches_v2_and_ratio_means_floor_matches_a7` |
| Ratio of scenario means; count and weight of S_base and S_reform | A7 `_cell` inside `_scenario_cell` | same |
| P_OASI, P_DI, group shares, per-component totals | `_cost_cell` | `test_statistics.py::test_component_accounting_and_spouse_three_classes`, `::test_accounting_identity_and_cut_bound_on_invented_components` |
| Spouse benefits resting on an entitled, unconverted DI worker | `runner.spouse_worker_class` and the `spouse_worker_classes` memo | `test_runner.py::test_spouse_classification_uses_living_link_2030_di_state`; `test_statistics.py::test_spouse_memo_counts_positive_component_by_scenario` |
| MINT population and bands | `statistics.MINT_BANDS`, `summarize_mint` | `test_statistics.py::test_band_boundaries_and_m4_age_offset` |
| Ratio of means, median of individual percent changes, difference of medians | `_mint_cell`, `weighted_median` | `test_statistics.py::test_three_mint_estimands_are_distinct_and_memos_have_floors`, `::test_mint_uses_scenario_specific_sets_and_intersection_for_changes` |
| Memo items: falling share, median levels | `_mint_cell` | same |
| Spec-only nulls N, N_model, N_MINT, M1's null | `nulls.build_nulls`, `nulls_for_run`; committed file | `test_nulls.py` |
| P − N, P − N_model; MINT equivalents with N_MINT (M1: its own) | `runner._add_null_gaps` | `test_runner.py::test_whole_invented_run_has_every_row_memo_null_and_label` |
| Context: model 2030 beneficiary count beside TR 2026 IV.B4 | `nulls.context_beneficiary_count`; runner `context_beneficiary_count` | `test_nulls.py::test_context_extractor_returns_only_one_count_and_no_other_values` |
| No acceptance rule | `ACOLAConfig.check_runnable` | `test_config.py::test_an_acceptance_rule_is_refused` |
| One shot, pointer, HEAD, clean tree, no existing artifact, specification pin | `scripts/run_acola_registered.py::preflight` | `test_registered_run_script.py` |
| No-drop: every row, undefined values null with a reason | `check_registered` refuses a partial row set; `_refused_cell`; empty draws | `test_statistics.py::test_empty_band_and_undefined_floor_serialize_with_reasons` and the refusal tests |
| Unchanged legacy registries and consumers | none changed | `test_unchanged.py` |
| Start-year check | the legacy emitter, unchanged | `test_timing_properties.py::test_future_start_year_reaches_the_actual_legacy_emitter`, `::test_opening_stock_carries_reduced_increases_from_the_registered_year` |
| Comparisons, interval rules, gaps | `scripts/compare_acola.py` | `test_compare.py`; `test_runner.py::test_compare_reads_the_whole_invented_run_artifact` |

## Payment timing

Under the model's annual convention, the amount paid in calendar year t
reflects the increases determined through t − 1
(`scenario_benefits.increased_pia_path`). A row's payment year is 2030
for calendar-year rows and 2031 for December rows
(`scenario_benefits.payment_year_for_reference`), and a person carries
the reduced increases determined from max(first reduced year, exposure
start) through the payment year minus one. The tests run invented people
through the unchanged legacy emitter and check these counts:

| Eligible in | C0 | C1 | M0 | M1 |
|---|---|---|---|---|
| 2027 or earlier | 3 | 4 | 2030 − max(2011, year) | 2030 − max(2010, year) |
| 2028 | 2 | 3 | 2 | 2 |
| 2029 | 1 | 2 | 1 | 1 |
| 2030 | 0 | 1 | 0 | 0 |

A person first eligible in 2030 has an identical base and reform amount
on C0, M0 and M1. C1 and M2 include the increase effective December
2030, which N, N_model and N_MINT exclude (ruling 11; no December null is
registered, so none is computed).

## Interpretations

Each choice below fills a detail the registration leaves open. Where an
existing function had the registered rule, its semantics were kept.

1. **Arithmetic of P.** P is computed as 100 × (T_reform / T_base − 1),
   the order of Track A v2's `ratio_of_all_alive_weighted_totals`, which
   the registration names. It equals 100 × (T_reform − T_base) / T_base
   algebraically and can differ only in the last bits.
2. **Sets for the ratio of means.** A7's `SCENARIO_SPECIFIC` membership:
   the base mean over S_base and the reform mean over S_reform, within
   the cell (all ages on the cost rows; the band on the MINT rows). Under
   mechanism L the two sets are equal by construction (the legacy emitter
   keeps people with a positive baseline, refuses a positive baseline
   with no reform benefit, and sets both flags), so equal counts are not
   evidence (ruling 6). The artifact says so on every row.
3. **People with a benefit in one scenario only.** The median of
   individual percent changes uses S_alt (both scenarios, b_base > 0),
   as A7 defines it. The difference of medians takes each scenario's
   median over its own S_s. The falling share is the weight of S_base
   members with b_reform < b_base (strict), over the weight of S_base.
4. **Weighted median (ruling 7).** Zero weights are excluded and counted
   (`median_zero_weight_exclusions`). Cumulative weights are exact
   rationals of the binary weights (`fractions.Fraction`), so "reaches
   W/2" and "equals W/2 exactly" are exact comparisons. Ties in x sort by
   person id. An empty positive-weight sample is undefined, with a reason.
5. **Spouse on a DI worker (ruling 4).** For every emitted row, the
   person in the 2030 state's `spouse_person_id` is read. If that person
   is alive in 2030 and `di_entitled` is true with no
   `di_conversion_year`, the class is "entitled_unconverted_di_worker"
   (the legacy `worker_record` gives such a worker `kind == "disabled"`);
   a living linked worker otherwise is "another_worker"; no living link
   is "unclassified". Counts and dollars are weighted, per scenario, over
   rows whose spouse component is positive in that scenario, opening
   stock included.
6. **Undefined values.** A statistic undefined in any draw makes the
   mean and SD undefined, with the defined-draw count and each draw's
   reason (A7's rule). A floor with fewer than two usable seeds is
   undefined, never zero, and lists the dropped seeds. A completed draw
   with no rows is undefined for that draw.
7. **Refused draws and rows.** A refusal is per row and draw. That
   draw's cell keeps every key with a null value, the reason and the
   exception's class; other draws and rows are kept; the row's status is
   "refused". A tabulation error from the A7 normalizer (no realistic
   trigger is known) refuses that row only, under `tabulation_refusal`,
   so the one shot still writes every other row.
8. **Weights over the projection (ruling 12).** The artifact counts the
   persons alive in at least one 2030 draw whose weight differs between
   draws.
9. **Context item.** The model's count is the mean over the 20 draws of
   C0's S_base weight, all ages. The Trustees count is Table IV.B4's
   "Beneficiaries (in thousands), OASDI" cell in the Intermediate 2030
   row, times 1,000. Nothing is scaled.
10. **Nulls on the MINT rows.** M0, M2, M3 and M4 report gaps against
    N_MINT (2011-2029); M1 against its own null (2010-2029).
11. **Unregistered A7 output.** A7's mean of individual ratios is
    removed from every cell; A7's per-cell mean benefits sit under
    `not_registered` (ruling 8).
12. **The TR 2026 column.** V.C1 prints a COLA column, so it is used
    directly (see below).
13. **compare.py.**
    - (a) The decimal counts that set the OACT and PWBM half units come
      from the record's own counts, cross-checked against the recorded
      strings; a disagreement is reported with the interval the string
      count would give (itself undefined unless p − d > 0 at every
      corner).
    - (b) "Rounds to the displayed one" holds when half-up (ties away
      from zero) or half-even rounding reproduces the HTML value; both
      results are reported, and where they disagree the branch each mode
      alone would give is reported too.
    - (c) A percent number format is one whose applicable section (chosen
      by the value's sign) holds an unquoted, unescaped `%`; more than one
      `%` makes reading S unavailable. A null number format is read
      literally as not a percent format, so the value is `Decimal(s)`; if
      its units differ from the display's it cannot round to the display
      and the HTML branch follows.
    - (d) The decimal count under reading S is that of the shortest form,
      so Python's `.0` on an integral double counts as zero decimals
      (identical to the literal rule under a percent format).
    - (e) MINT values are used as printed; the record has no
      sign-convention field.
    - (f) Under an "unsettled" median type, both medians are labelled
      "compared, no headline"; the ratio of means is "beside" in every
      case.
    - (g) The precision gate is applied to the printed p and d. When OACT
      is undefined for any reason, PWBM is reported as primary (both are
      report-only under d658).
    - (h) The OASI and DI split is compared only where the record flags
      it, and only from fields the record carries.
    - (i) A recorded OACT row label or PWBM year other than 2030 makes
      that comparator undefined. The other recorded match flags (footer,
      provision text, `Last-Modified`, MINT median type and band keys)
      are collected in `identity_checks`, reported and never substituted.
    - (j) Only the record whose producer is "reconciled" is compared, and
      it is read once and checked against its seal entry before parsing.
      A registered comparison also requires the seal's own SHA-256 to be
      the one `EV/RESTRICTED-FILES.md` records, unless
      `--expect-seal-sha256` names another.
    - (k) A registered artifact must carry Registration 18's pointer and
      a clean tree; an invented one needs `--allow-invented` and is
      labelled INVENTED DATA.
    - (l) Numbers are exact rationals. A terminating decimal is written
      in full, any other to 20 significant digits, with interval ends
      rounded outward so the written interval contains the exact one.

## Invariants and their tests

All tests use invented data. Property tests use Hypothesis.

- **Accounting.** Per draw, the component totals sum to T_s,
  T_base = T_base,OASI + T_base,DI, and
  P = s_OASI · P_OASI + s_DI · P_DI. Not across draw means, because the
  shares vary by draw. `test_statistics.py::test_accounting_identity_and_cut_bound_on_invented_components`.
- **Identity.** The ratio of scenario means equals P when S_base =
  S_reform. `::test_ratio_means_and_union_differential_against_existing_functions`.
- **Zero reform.** With `annual_reduction = 0`, P, every change statistic,
  the falling share and every null are exactly 0; the median benefit
  levels, which are memo levels, stay positive. `::test_zero_reform_has_exact_zero_changes_share_and_floors`;
  `test_nulls.py::test_zero_reform_is_exactly_zero`,
  `::test_build_zero_reform_nulls_are_all_exactly_zero`.
- **Bounds.** Under a cut, an individual change lies in [N_full, 0],
  where N_full is the model-rate null over every reduced increase the
  row's payment period carries, and N_model ≤ P ≤ 0 on C0 (with the
  December increase on C1). The bound is tested on the legacy benefit
  paths with the rounding allowance below, on the statistics for a
  uniform cut (`test_statistics.py::test_accounting_identity_and_cut_bound_on_invented_components`,
  `::test_mint_order_falling_share_and_individual_cut_bounds`), and on
  the whole invented run, where P ≤ 0 on C0 and C1. Three effects are
  named:
  - *Dime rounding.* Projected paths floor to dimes after each increase
    and again after the claim-age factor. The tolerance is not a fixed
    percentage: it is 0.1 dollars times the sum of (1 + c)^j over the
    path's years, relative to the person's own baseline (plus one dime
    after the factor on the worker path).
    `test_timing_properties.py::test_cut_bounds_monotonicity_and_zero_reform_on_rounded_paths`.
    Opening-stock amounts are not dime-floored
    (`opening_stock_dime_floor = False`), and their ratio equals the
    exact factor product
    (`::test_opening_stock_carries_reduced_increases_from_the_registered_year`).
  - *Dual entitlement (intended violation).* The spouse excess subtracts
    the full own PIA, while an early own retirement benefit carries a
    smaller claim-age factor. When the own clock carries more reduced
    increases than the linked worker's, the cut can raise the combined
    benefit, so an individual change, and in principle P, can exceed
    zero, and a larger cut or earlier start can raise it. This is
    structural, not rounding; no tolerance is asserted, and the artifact
    labels it (`INTENDED_BOUND_VIOLATIONS`, gap
    `dual_entitlement_bounds_and_monotonicity`).
    `test_statistics.py::test_valid_dual_entitlement_can_raise_benefits_under_registered_cut`,
    `::test_dual_entitlement_bound_violation_is_structural_under_dime_floors`.
  - *Family maximums* are not modeled (annual-convention omission), so
    they cannot move a person outside the bound.
  - *REFUSE cannot intervene on the registered rows.* The runner's
    precheck requires every reduced rate from the row's first year
    through 2030 to be above zero; on the model's TR 2008 path every
    such rate is 2.8 − 1.0 = 1.8 percent (computed for all seven rows).
    Under any other baseline the run refuses before projecting.
- **Monotonicity (intended).** A larger reduction, or an earlier first
  reduced year, weakly lowers every individual benefit and P, outside the
  dual-entitlement exception. `test_statistics.py::test_larger_cut_weakly_lowers_p_and_every_individual_change`;
  the timing property test.
- **Determinism.** The same seed gives the same draw; the order of
  persons changes no statistic or floor.
  `test_runner.py::test_same_draw_seed_is_deterministic`;
  `test_statistics.py::test_cost_and_mint_order_independent_including_every_floor`.
- **Weighted median.** Permutation invariance and weight-scale
  invariance; the ordinary median with equal weights; within [min, max];
  the exact-W/2 midpoint; a near-W/2 case on exact binary weights.
  `test_statistics.py::test_registered_exact_weighted_median`,
  `::test_near_half_weight_uses_exact_binary_fraction`,
  `::test_equal_positive_weights_match_ordinary_median`,
  `::test_median_bounds_permutation_and_weight_scale`.
- **Nulls.** N = 100 (Π f_k − 1), each f_k < 1 for c_k > −1 and a
  positive cut; N_MINT has 19 factors and M1's null 20; more reduced
  increases lower the null; a larger COLA raises it.
  `test_nulls.py::test_null_is_exact_product_with_factors_less_than_one`,
  `::test_more_reduced_increases_strictly_lowers_the_null`,
  `::test_larger_reduction_lowers_null_and_larger_cola_raises_it`,
  `::test_committed_nulls_reproduce_exactly_from_pinned_inputs`.
- **compare.py.** Each four-corner interval contains the point value; C
  is monotone in d (with the sign of p) and, for fixed d, in p (with the
  sign of −d), verified numerically on the actual box by a 9 × 9 grid in
  the script itself and by a property test; the PWBM six-decimal rule and
  the MINT branch rules; interval subtraction [a, b] − [c, d] =
  [a − d, b − c]. `test_compare.py`.
- **Differential.** P against v2's union statistic; the ratio of means
  against A7; the floors against v2's and A7's floor code.
  `test_statistics.py::test_ratio_means_and_union_differential_against_existing_functions`,
  `::test_cost_floor_matches_v2_and_ratio_means_floor_matches_a7`.
- **Guards.** The entry script refuses a wrong or malformed pointer, a
  HEAD other than `--registered-commit`, a dirty tree, an existing
  artifact or sidecar, another output path and a specification whose
  SHA-256 differs from the pin. `test_registered_run_script.py`.
- **Unchanged registries.** `test_unchanged.py` (see below).

## Spec-only nulls

`docs/design/acola_spec_only_nulls.json` (written by
`scripts/build_acola_spec_only_nulls.py`, SHA-256
`61350340db499f93ca849bdb7eeceb920b0b2733b17beb3e868dacb63c12598d`)
holds the exact rationals; the run recomputes them and refuses if the
committed file differs from its inputs.

| Null | Years k | c_k | Factors | Value (percent) |
|---|---|---|---|---|
| N | 2027-2029 | TR 2026 V.C1, Intermediate: 2.4, 2.4, 2.4 | 3 | −2.901170402765… |
| N_model | 2027-2029 | model TR 2008: 2.8 each (Table II.C1 ultimate CPI) | 3 | −2.889991972119… |
| N_MINT | 2011-2029 | model TR 2008: 2.8 each (V.C1 through 2017, then ultimate CPI) | 19 | −16.950197597259… |
| M1's null | 2010-2029 | model TR 2008: 2.8 each | 20 | −17.758075052539… |

N − N_model = −0.011178430645… percentage points. The model's rates for
2018-2029 are TR 2008's ultimate annual-average CPI, not printed COLAs
(`data/tr2008.py`), so N − N_model compares TR 2026's printed COLAs with
that derived rate.

## TR 2026 Table V.C1 capture

- **Page.** `https://www.ssa.gov/oact/TR/2026/V_C_prog.html`, the
  chapter page of section V.C. V.C1 has no page of its own. The 2026
  Report's table of contents (`trTOC.html`) links no table; its "LIST OF
  TABLES" page (`X1_trLOT.html`) links the V.C1 entry to
  `V_C_prog.html#1047210`.
- **Stored bytes.** Only the outermost `<table>` element whose caption
  is "Table V.C1.—Cost-of-Living Benefit Increases, Average Wage Index,
  Contribution and Benefit Bases, and Retirement Earnings Test Exempt
  Amounts, 1975-2035", byte for byte as served:
  `data/external/snapshots/tr2026_v_c1_vintage1/trustees2026_v_c1_table.html`,
  SHA-256 `4d29f2b85d67b995eea25f0bdfb46b3755671c082d75a9855680836d4b80c46a`,
  438,787 bytes, retrieved 2026-10-01T15:01:44Z (`browser-h2` mode). The
  chapter page was held in memory and not stored (its SHA-256 at that
  fetch is in `capture_record.json`). The fragment holds one `<table>`
  and one caption.
- **Timing footnote.** V.C1's COLA column carries footnote a, which sits
  outside the table: "Effective with benefits payable for June in each
  year 1975-82, and for December in each year after 1982." It was taken
  from a second fetch at 15:49:46Z into `cola_timing_note.txt`
  (SHA-256 `f63274d3ef3b06c1647326490945ed05c01421466f9b0cca891bd1d0a511341b`,
  107 bytes) with its own `timing_note_record.json`.
- **Manifest.** `capture_manifest.txt` (SHA-256
  `fd271e0067c70737ac36e3a442c96d0b7e4650aaa14398b8383ac6e24e853abb`),
  two lines in the vintage-1 grammar `<UTC> <sha256> <bytes> <filename>`.
- **Column and rows.** The column "Cost-of-living benefit increase^a
  (percent)", in the "Intermediate:" row group, rows 2027, 2028 and
  2029. V.C1 prints a COLA column, so it is used directly and the CPI
  fallback is not used. It is the same column the model's TR 2008 path
  reads from TR 2008's V.C1 (`cola_percent`) through 2017, with the same
  year mapping: the row labelled k is the increase effective December k,
  as the footnote states for years after 1982.

## Gaps named on the artifact

Each is in the artifact's `gaps` list; none changes a number.

- **Statutory rounding.** Dime floors on projected paths; the tolerance
  above.
- **Dual entitlement.** The intended bound and monotonicity violation
  above.
- **Reform-only auxiliary excess.** The legacy code keeps a spouse or
  widow excess only when its baseline is positive
  (`cola_track_a/benefits.py`, `_spouse_excess` and `_widow_excess`). A
  reform excess above a zero baseline excess is dropped, which pushes P
  slightly away from zero. The public emitter exposes no counter, so the
  count is reported as undefined with that reason; counting would need a
  copy of private benefit arithmetic or an edit to a shared module
  (ruling 5).
- **Annual-convention omissions.** Family maximums, the earnings test,
  recomputation and payment-month timing (`scenario_benefits.py` module
  note; ruling 15).
- **Closed cohort.** No one under 50 in 2030, no post-2010 immigrants or
  earnings, no children; disabled widow(er)s only from the opening stock.
- **Scheduled versus payable, DI and auxiliaries, COLA timing, taxation
  of benefits.** Each of Registration 18's remaining adjustments has its
  own entry, with REG's text and source.
- **Benefits-only cost.** P covers scheduled benefits only; the
  comparators' cost definitions and dilution are reported by
  `compare_acola.py`.
- **Baseline vintage.** TR 2008 paths against TR 2026, PWBM's own and
  MINT5's TR 2008; N − N_model measures the COLA-rate part.
- **December null.** None is registered or computed.

## C0-D

C0-D is C0 with mechanism D (`statutory_415_b_2`). It is registered and
deferred: `config.DEFERRED_ROWS` holds its full row specification and
the registration's reason, `ACOLAConfig` refuses it in the runnable set,
and the artifact carries it under `deferred_rows` with status
"deferred". It runs once Track A v2's own real-data run artifact is on
master, at a commit a further issue #42 comment registers. Nothing in
`acola_track` imports `track_a_v2`.

## Unchanged registries and shared modules

The build edits no shared engine or benefit module. `test_unchanged.py`
pins, byte for byte, the source text of every exercise-1 constant and
helper in `cola_track_a/config.py` (`REGISTERED_ROWS` and `_row`
included), the exercise-3 constants in `fra68_track/config.py`, and
`_check_reform` with the constants it reads in `fra68_track/reform.py`,
at `origin/master` 75cd3524. It checks the consumers by behavior: the
legacy rows' values, Track A v2's 68-row matrix built from the same
`REGISTERED_ROWS` objects, `JointConfig`'s R0-R5 and the dry run's rate
check. The only shared files edited are housekeeping:
`scripts/first_estimates_birth_evidence.py` and its exact-tuple test
(the five `acola_track` source files appended to
`POST_REVIEW_SOURCE_EXCLUSIONS`, and the package asserted unreachable
from the birth reducer), `tests/tier_counts.json` and
`tests/README-tiers.md`.
