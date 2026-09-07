"""gate_3 retrodiction arm -- floor artifact v3 (FLOORS ONLY, NO LOCK).

v2 answered the two adversarial referees. An INDEPENDENT VERIFIER then
recomputed v2 from the raw printings, confirmed the three blocking
referee findings CLOSED, and returned **NOT VERIFIED as lock-ready** on
seven new findings. v3 answers those seven, and nothing else changes:
``gates.yaml`` is untouched, v1 and v2 are byte-identical and read-only,
no candidate is scored, and nothing here is locked.

The seven, and where each is closed:

1. **Residual exposure was understated about 2x.** v2's published
   residual (12 of 88) was LEAVE-ONE-OUT WITHIN its own eleven-rule
   panel -- the panel's exposure to its own members, not to a rule
   nobody registered. The verifier built an out-of-panel rule set and
   measured a textbook degree-2 trend on the last eight fit rows
   (``quad_last8``) passing 23 of the 88 gated pairs. v3 widens the
   REGISTERED panel from 11 rules to 55 -- every rule the verifier
   built, by name and construction, ``quad_last8`` included -- makes
   the panel OPEN and VERSIONED with a published admission procedure,
   sets every gated tolerance strictly below the minimum over the
   widened panel, measures the residual again against a NEW 35-rule
   adversarial probe set, and reports the gated count honestly: the
   surface falls from 88 pairs to 43.
2. **Leg 2's rolling-origin blocks were ambiguous** between a global
   stride-5 partition of the nine origins and a per-pair partition of
   each pair's eight admissible ones -- readings that disagree on 108
   of 108 pairs. v3 fixes ONE rule (the global partition of 2004-2012),
   states how an inadmissible target is handled, and prints the exact
   admissible origin list per horizon.
3. **v2's report contradicted v2's artifact** and attributed a census
   to referee B that referee B never wrote. v3 emits every count the
   report may state, as a sentence, FROM the computed surface
   (``report_counts``), and the test suite re-derives each one.
4. **``report_only`` was a regression**: v1's broken globs left 5 of the
   17 non-eligible cells with no contract text, v2's six-entry
   enumeration left 10. v3 enumerates all 17 with their blocking
   reasons and pins the partition
   gated + eligible-not-gated + report_only == the whole registry.
5. **No tolerance cap.** Every locked gate has a power cap; the
   retrodiction arm had none, and v2's widest relative band (33.8 %)
   was wider than the 29 % pair referee A flagged in v1. v3 states a
   cap in the locked gates' grammar, derived from ln(1.5), applies it,
   and reports what it demotes.
6. **Rounding-tie dependence.** Three v2 tolerances were exact 3-dp
   half-way ties and the rule text fixed no tie convention; on one, a
   half-to-even implementation disagreed with the committed literal.
   v3 states the convention (6-dp deviations, then ROUND_HALF_EVEN in
   exact decimal arithmetic) and implements it explicitly.
7. **A8's cure is contested.** Referee A wanted gate_3's own headline
   narrowed plus a declared live-arm sibling; referee B wanted a narrow
   locked tranche leaving gate_3 unlocked and broad. v2 took B's and
   presented it as A's. v3 takes NEITHER: both cures are written as
   alternative fragment texts, side by side, with each referee's
   reason, and marked as the one decision the ratifying round must
   take.

Run: ``uv run python scripts/build_gate3_retrodiction_floors_v3.py``
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
V1_BUILDER = REPO / "scripts" / "build_gate3_retrodiction_floors.py"
V2_BUILDER = REPO / "scripts" / "build_gate3_retrodiction_floors_v2.py"
V1_ARTIFACT = REPO / "runs" / "gate3_retrodiction_floors_v1.json"
V2_ARTIFACT = REPO / "runs" / "gate3_retrodiction_floors_v2.json"
ARTIFACT = REPO / "runs" / "gate3_retrodiction_floors_v3.json"
ENV_SIDECAR = ARTIFACT.with_suffix(".env.json")
INPUT_SIDECAR = ARTIFACT.with_suffix(".inputs.json")

#: v1 and v2 are READ, never rewritten. Pinned so a moved predecessor is
#: a loud failure rather than a silent re-floor of a different package.
V1_ARTIFACT_SHA256 = (
    "d78721185856650b1898a7e21d31203c4f0cf0f29e5c79e989f676aec1c78875"
)
V1_BUILDER_SHA256 = (
    "eedf2485c48daee3a8d52d214b52f98a17892e466a508400c7281856d1fae720"
)
V2_ARTIFACT_SHA256 = (
    "385cb7c5e780f5bd174740542c37da191d7d6ee2fa96babafd1cc7a13614461d"
)
V2_BUILDER_SHA256 = (
    "726ad3a13cbdfc013f9338613df26466af26d5643fec2059769d4d453ad42189"
)

#: The independent verifier's report, whose seven findings this artifact
#: answers. It lives outside the repository, so it is pinned by digest
#: and size in prose only -- no path is read here.
VERIFIER_REPORT_SHA256 = (
    "2b84514baf607d29fda9f02ae50bbc9e1d49c111ed032c1de7e58b77b02c17dd"
)
VERIFIER_REPORT_BYTES = 74961

SCHEMA_VERSION = "gate3_retrodiction_floors.v3"
RUN = "gate3_retrodiction_floors_v3"


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_obj(obj) -> str:
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


def _load(name: str, path: Path, expected: str):
    """Import a pinned predecessor builder WITHOUT modifying it."""
    if _sha256_path(path) != expected:
        raise ValueError(
            f"{name} digest moved: refusing to build v3 against a "
            "different predecessor than the one that was verified"
        )
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v1b = _load("build_gate3_retrodiction_floors", V1_BUILDER, V1_BUILDER_SHA256)
v2b = _load(
    "build_gate3_retrodiction_floors_v2", V2_BUILDER, V2_BUILDER_SHA256
)

T_STAR = v2b.T_STAR  # 2012
FIT_FIRST_YEAR = v2b.FIT_FIRST_YEAR  # 1998
SEEDS = v2b.SEEDS
CLAIM_2014 = v2b.CLAIM_2014
CLAIM_2023 = v2b.CLAIM_2023
METRICS = v2b.METRICS
GATED_HORIZONS = v2b.GATED_HORIZONS  # (2, 3, 4, 5, 6, 7)
ROLLING_ORIGIN_FIRST = v2b.ROLLING_ORIGIN_FIRST  # 2004
EXCLUDED_TARGET_YEARS = v2b.EXCLUDED_TARGET_YEARS  # 2013, 2020-2022
RHO_SENSITIVITY = v2b.RHO_SENSITIVITY  # (0.5, 0.75, 0.9)
DRAFT_RHO = v2b.DRAFT_RHO  # 0.75 -- a POLICY CONSTANT, not chosen here
DRAFT_ROUNDING = v2b.DRAFT_ROUNDING  # 3
DRAFT_K = v2b.DRAFT_K  # 4
DEVIATION_ROUNDING = 6


# --------------------------------------------------------------------------
# FINDING 6: the tie rule.
#
# The verifier found three tolerances that are EXACT half-way ties at 3
# decimal places in exact rational arithmetic (81/400, 51/400, 27/400),
# and on one of them -- claim_share.age63|male@h5 -- a half-to-even
# implementation gives 0.202 against v2's committed 0.203. v2's rule text
# said `round(rho * F2_panel_min, 3)` and named no tie convention, while
# its committed literals were what CPython's binary-float round() happens
# to produce after a 6-dp cleaning step the rule text did not mention.
#
# v3 fixes both halves in the CONTRACT and implements them explicitly:
#
#   (1) the deviation is rounded to 6 decimal places FIRST, and that
#       6-dp value is the published quantity and the only input to the
#       tolerance;
#   (2) the tolerance is rho * that value evaluated in EXACT DECIMAL
#       arithmetic and quantised to 3 dp under ROUND_HALF_EVEN.
#
# Why half-to-even rather than half-up: it is the IEEE-754 and
# `decimal` default, it is unbiased across a panel of 108 pairs, and it
# is the convention CPython's own round() documents. The cost is one
# literal moving against v2 (0.203 -> 0.202 at claim_share.age63|male@h5)
# and that pair is not gated in v3 at all. Evaluating in `Decimal`
# rather than binary float is what makes the convention BINDING: the
# tie is exact, so the answer no longer depends on which of two nearby
# binary doubles the arithmetic landed on.
# --------------------------------------------------------------------------
TIE_RULE = (
    "ROUNDING, STATED SO IT CANNOT BE READ TWO WAYS. (1) The deviation "
    "is metric(prediction, realized) rounded to 6 decimal places; that "
    "6-dp number is what is published and is the ONLY input to the "
    "tolerance. (2) tolerance = rho * F2_panel_min evaluated in EXACT "
    "DECIMAL arithmetic on that 6-dp value and quantised to 3 decimal "
    "places under ROUND_HALF_EVEN (round half to even). Ties are exact "
    "and are resolved by the stated convention, not by whichever binary "
    "double the arithmetic happened to land on. Under this rule the "
    "three exact 3-dp ties the independent verifier found -- 81/400, "
    "51/400 and 27/400 -- resolve to 0.202, 0.128 and 0.068."
)


def deviation_6dp(prediction: float, realized: float, metric) -> float:
    """The published deviation: 6 decimal places, and nothing else."""
    return round(float(metric(prediction, realized)), DEVIATION_ROUNDING)


def tolerance_from(panel_min: float, rho: float) -> float:
    """rho * panel_min in exact decimal, 3 dp, ROUND_HALF_EVEN."""
    exact = Decimal(str(rho)) * Decimal(repr(panel_min))
    return float(exact.quantize(Decimal("0.001"), rounding=ROUND_HALF_EVEN))


#: The three exact ties the verifier isolated, kept as a pinned fixture
#: so the convention is testable independently of which pairs gate.
VERIFIER_TIES = (
    ("claim_share.age63|male@h5", 0.27, 0.202, "81/400 = 0.2025"),
    ("claim_share.age63|male@h7", 0.17, 0.128, "51/400 = 0.1275"),
    (
        "claim_share.disability_conversion|male@h3",
        0.09,
        0.068,
        "27/400 = 0.0675",
    ),
)


# --------------------------------------------------------------------------
# FINDING 1: the WIDENED registered information-null panel.
#
# A rule is information-null iff it reads only rows of the FIT SOURCE at
# or before the origin. Every rule below satisfies that by construction:
# each receives only (fit_years, values) truncated at the origin and the
# target year, and cannot see the resolution vintage at all.
#
# v2 registered 11 rules. The independent verifier built a further set
# outside that panel and measured `quad_last8` -- ordinary least squares
# of degree 2 on the last eight fit rows -- passing 23 of v2's 88 gated
# tolerances and clearing two cells at every gated horizon. v2's
# published residual of "12 of 88" was leave-one-out WITHIN the panel,
# which measures the panel's exposure to its own members and is not a
# bound on exposure to a rule nobody registered.
#
# v3 registers every rule the verifier built. Three notes on provenance,
# because the count matters and the verifier's own report and script
# disagree about it:
#
#   * the verifier's report says "45"; its script
#     (work/verify_residual.py) defines 41 distinct rule names. All 41
#     are registered below under `verifier_script`.
#   * the report's prose describes three classes its script omits --
#     medians over 2 and 7 rows, and a cubic on the last 8 rows. Those
#     three are registered below under `verifier_prose` so that the
#     panel contains every class the verifier DESCRIBED, not only every
#     rule it ran.
#   * `mean_last3` appears in the report's prose class ("means ... over
#     2/3/5/7 rows") and is already a v2 panel member; it is not
#     double-registered.
#
# 11 + 41 + 3 = 55 registered rules.
#
# The v2 members reuse v2's own function objects rather than
# re-implementations, so the two artifacts cannot drift on a shared
# rule definition.
# --------------------------------------------------------------------------
_persistence = v2b._persistence
_linear_trend = v2b._linear_trend
_drift = v2b._drift
_trend_last = v2b._trend_last
_damped = v2b._damped
_mean_last3 = v2b._mean_last3


def _mean_last(window: int):
    """Mean of the last `window` fit rows."""

    def rule(years, values, target):
        if len(values) < window:
            return None
        return float(np.mean(values[-window:]))

    return rule


def _median_last(window: int):
    """Median of the last `window` fit rows."""

    def rule(years, values, target):
        if len(values) < window:
            return None
        return float(np.median(values[-window:]))

    return rule


def _poly(degree: int, window: int | None = None):
    """OLS polynomial of `degree`, evaluated at the target year."""

    def rule(years, values, target):
        use_y = years if window is None else years[-window:]
        use_v = values if window is None else values[-window:]
        if len(use_v) < degree + 1:
            return None
        coefficients = np.polyfit(
            np.asarray(use_y, dtype=float),
            np.asarray(use_v, dtype=float),
            degree,
        )
        return float(np.polyval(coefficients, target))

    return rule


def _holt(alpha: float, beta: float):
    """Holt linear exponential smoothing, fit rows only."""

    def rule(years, values, target):
        level, trend = float(values[0]), float(values[1] - values[0])
        for value in values[1:]:
            previous = level
            level = alpha * value + (1 - alpha) * (level + trend)
            trend = beta * (level - previous) + (1 - beta) * trend
        return float(level + (target - years[-1]) * trend)

    return rule


def _theta():
    """Theta method (theta = 0/2 pair): SES(0.3) blended with OLS."""

    def rule(years, values, target):
        slope, intercept = np.polyfit(
            np.asarray(years, dtype=float),
            np.asarray(values, dtype=float),
            1,
        )
        linear = slope * target + intercept
        level = float(values[0])
        for value in values[1:]:
            level = 0.3 * value + 0.7 * level
        return float(0.5 * level + 0.5 * linear)

    return rule


def _blend(first, second, weight: float):
    """Convex blend w * first + (1 - w) * second."""

    def rule(years, values, target):
        a = first(years, values, target)
        b = second(years, values, target)
        if a is None or b is None:
            return None
        return float(weight * a + (1 - weight) * b)

    return rule


V1_SOURCE = "registered in v1 (persistence / linear trend)"
V2_SOURCE = "registered in v2 after referee B exhibited it against v1"
VS_SOURCE = (
    "independent verifier of v2, report section 2.7, built in its "
    "scratch program work/verify_residual.py"
)
VP_SOURCE = (
    "independent verifier of v2, report section 2.7: a class the "
    "verifier's PROSE describes that its script did not build"
)

NULL_RULE_PANEL_V3: dict = {
    # ---- the eleven v2 registered (function objects reused verbatim) ----
    "persistence": (_persistence, "pred(T*+h) = v(T*)", V1_SOURCE),
    "linear_trend": (
        _linear_trend,
        "pred(T*+h) = OLS(v on year, fit window 1998..T*) at T*+h",
        V1_SOURCE,
    ),
    "drift3": (
        _drift(3),
        "pred(T*+h) = v(T*) + h * (v(T*) - v(T*-3)) / 3",
        V2_SOURCE,
    ),
    "drift5": (
        _drift(5),
        "pred(T*+h) = v(T*) + h * (v(T*) - v(T*-5)) / 5",
        V2_SOURCE,
    ),
    "trend_last5": (
        _trend_last(5),
        "pred(T*+h) = OLS on the last 5 fit rows, at T*+h",
        V2_SOURCE,
    ),
    "trend_last8": (
        _trend_last(8),
        "pred(T*+h) = OLS on the last 8 fit rows, at T*+h",
        V2_SOURCE,
    ),
    "trend_last10": (
        _trend_last(10),
        "pred(T*+h) = OLS on the last 10 fit rows, at T*+h",
        V2_SOURCE,
    ),
    "damped0.7_last10": (
        _damped(0.7, 10),
        "pred(T*+h) = v(T*) + slope_last10 * sum(0.7^j, j=1..h)",
        V2_SOURCE,
    ),
    "damped0.8": (
        _damped(0.8),
        "pred(T*+h) = v(T*) + slope_fitwindow * sum(0.8^j, j=1..h)",
        V2_SOURCE,
    ),
    "damped0.9": (
        _damped(0.9),
        "pred(T*+h) = v(T*) + slope_fitwindow * sum(0.9^j, j=1..h)",
        V2_SOURCE,
    ),
    "mean_last3": (
        _mean_last3,
        "pred(T*+h) = mean(v(T*-2), v(T*-1), v(T*))",
        V2_SOURCE,
    ),
}

#: The 41 the verifier's script defines, by name and construction.
for _lag in (1, 2, 4, 6, 7, 10, 14):
    NULL_RULE_PANEL_V3[f"drift{_lag}"] = (
        _drift(_lag),
        f"pred(T*+h) = v(T*) + h * (v(T*) - v(T*-{_lag})) / {_lag}",
        VS_SOURCE,
    )
for _w in (3, 4, 6, 7, 9, 12):
    NULL_RULE_PANEL_V3[f"trend_last{_w}"] = (
        _trend_last(_w),
        f"pred(T*+h) = OLS on the last {_w} fit rows, at T*+h",
        VS_SOURCE,
    )
for _phi in (0.6, 0.75, 0.85, 0.95, 0.99):
    NULL_RULE_PANEL_V3[f"damped{_phi}"] = (
        _damped(_phi),
        f"pred(T*+h) = v(T*) + slope_fitwindow * sum({_phi}^j, j=1..h)",
        VS_SOURCE,
    )
for _phi, _win in ((0.5, 5), (0.8, 5), (0.9, 8), (0.7, 5)):
    NULL_RULE_PANEL_V3[f"damped{_phi}_last{_win}"] = (
        _damped(_phi, _win),
        f"pred(T*+h) = v(T*) + slope_last{_win} * sum({_phi}^j, j=1..h)",
        VS_SOURCE,
    )
for _w in (2, 5, 7):
    NULL_RULE_PANEL_V3[f"mean_last{_w}"] = (
        _mean_last(_w),
        f"pred(T*+h) = mean of the last {_w} fit rows",
        VS_SOURCE,
    )
for _w in (3, 5):
    NULL_RULE_PANEL_V3[f"median_last{_w}"] = (
        _median_last(_w),
        f"pred(T*+h) = median of the last {_w} fit rows",
        VS_SOURCE,
    )
NULL_RULE_PANEL_V3.update(
    {
        "quad_full": (
            _poly(2),
            "pred(T*+h) = OLS degree 2 on the fit window 1998..T*, at T*+h",
            VS_SOURCE,
        ),
        "quad_last8": (
            _poly(2, 8),
            "pred(T*+h) = OLS degree 2 on the last 8 fit rows "
            "(2005..T*), at T*+h",
            VS_SOURCE
            + " -- THE RULE THAT FOUND THE HOLE: it passes 23 of v2's "
            "88 gated tolerances and clears two cells at every gated "
            "horizon, which is why v3 exists",
        ),
        "cubic_full": (
            _poly(3),
            "pred(T*+h) = OLS degree 3 on the fit window 1998..T*, at T*+h",
            VS_SOURCE,
        ),
        "holt(.3,.1)": (
            _holt(0.3, 0.1),
            "pred(T*+h) = Holt linear exponential smoothing, "
            "alpha = 0.3, beta = 0.1, over the fit rows",
            VS_SOURCE,
        ),
        "holt(.5,.2)": (
            _holt(0.5, 0.2),
            "pred(T*+h) = Holt linear exponential smoothing, "
            "alpha = 0.5, beta = 0.2, over the fit rows",
            VS_SOURCE,
        ),
        "holt(.8,.3)": (
            _holt(0.8, 0.3),
            "pred(T*+h) = Holt linear exponential smoothing, "
            "alpha = 0.8, beta = 0.3, over the fit rows",
            VS_SOURCE,
        ),
        "theta": (
            _theta(),
            "pred(T*+h) = 0.5 * SES(alpha = 0.3) + 0.5 * "
            "OLS(fit window), the theta = 0/2 pair",
            VS_SOURCE,
        ),
        "blend_pers_lin_50": (
            _blend(_persistence, _linear_trend, 0.5),
            "pred(T*+h) = 0.50 * persistence + 0.50 * linear_trend",
            VS_SOURCE,
        ),
        "blend_pers_lin_25": (
            _blend(_persistence, _linear_trend, 0.25),
            "pred(T*+h) = 0.25 * persistence + 0.75 * linear_trend",
            VS_SOURCE,
        ),
        "blend_pers_lin_75": (
            _blend(_persistence, _linear_trend, 0.75),
            "pred(T*+h) = 0.75 * persistence + 0.25 * linear_trend",
            VS_SOURCE,
        ),
        "blend_pers_drift3_50": (
            _blend(_persistence, _drift(3), 0.5),
            "pred(T*+h) = 0.50 * persistence + 0.50 * drift3",
            VS_SOURCE,
        ),
        "blend_drift3_trend8_50": (
            _blend(_drift(3), _trend_last(8), 0.5),
            "pred(T*+h) = 0.50 * drift3 + 0.50 * trend_last8",
            VS_SOURCE,
        ),
        "blend_drift3_drift5_50": (
            _blend(_drift(3), _drift(5), 0.5),
            "pred(T*+h) = 0.50 * drift3 + 0.50 * drift5",
            VS_SOURCE,
        ),
        "blend_d0.8_d0.9_50": (
            _blend(_damped(0.8), _damped(0.9), 0.5),
            "pred(T*+h) = 0.50 * damped0.8 + 0.50 * damped0.9",
            VS_SOURCE,
        ),
        # ---- the three classes the verifier's prose names, not its code
        "median_last2": (
            _median_last(2),
            "pred(T*+h) = median of the last 2 fit rows",
            VP_SOURCE,
        ),
        "median_last7": (
            _median_last(7),
            "pred(T*+h) = median of the last 7 fit rows",
            VP_SOURCE,
        ),
        "cubic_last8": (
            _poly(3, 8),
            "pred(T*+h) = OLS degree 3 on the last 8 fit rows, at T*+h",
            VP_SOURCE,
        ),
    }
)

PANEL_V3 = tuple(NULL_RULE_PANEL_V3)
PANEL_VERSION = 3
PANEL_DEFINITIONS = {
    "panel_v1_registered": ("persistence", "linear_trend"),
    "panel_v2_eleven": tuple(v2b.NULL_RULE_PANEL),
    "panel_v3_registered": PANEL_V3,
}
BINDING_PANEL = "panel_v3_registered"


# --------------------------------------------------------------------------
# FINDING 1, second half: the RESIDUAL PROBE SET.
#
# Widening the panel does not answer the verifier's finding on its own.
# The finding was that a residual measured INSIDE the panel understates
# the exposure to a rule outside it, and that defect recurs at any panel
# size unless it is measured again from outside the NEW panel. So v3
# carries a second, explicitly UNREGISTERED set of 35 rules -- drawn
# from classes the 55 does not contain (robust slopes, recency-weighted
# least squares, logit- and log-space trends, an AR(1) on first
# differences, simple and double exponential smoothing, damped Holt,
# degree-4 polynomials, local-linear smoothers, knotted splines, and
# blends involving quad_last8) -- and measures what they pass against
# the v3 gated surface.
#
# These rules are NOT in the panel and set no tolerance. They are the
# honest number that replaces v2's mislabelled "12 of 88", and they are
# the worked example the admission procedure below is written against.
# --------------------------------------------------------------------------
def _theil_sen(window: int | None = None):
    """Median of pairwise slopes, extended from the last fit row."""

    def rule(years, values, target):
        use_y = years if window is None else years[-window:]
        use_v = values if window is None else values[-window:]
        if len(use_v) < 2:
            return None
        slopes = [
            (use_v[j] - use_v[i]) / (use_y[j] - use_y[i])
            for i in range(len(use_v))
            for j in range(i + 1, len(use_v))
        ]
        return float(
            use_v[-1] + float(np.median(slopes)) * (target - use_y[-1])
        )

    return rule


def _wls(decay: float, window: int | None = None):
    """OLS with geometric recency weights decay ** (age in years)."""

    def rule(years, values, target):
        use_y = np.asarray(
            years if window is None else years[-window:], dtype=float
        )
        use_v = np.asarray(
            values if window is None else values[-window:], dtype=float
        )
        if len(use_v) < 2:
            return None
        weights = decay ** (use_y[-1] - use_y)
        slope, intercept = np.polyfit(use_y, use_v, 1, w=np.sqrt(weights))
        return float(slope * target + intercept)

    return rule


def _logit_trend(window: int | None = None):
    """Linear trend in logit space, inverted back to a share."""

    def rule(years, values, target):
        use_y = np.asarray(
            years if window is None else years[-window:], dtype=float
        )
        use_v = np.asarray(
            values if window is None else values[-window:], dtype=float
        )
        if len(use_v) < 2 or np.any(use_v <= 0) or np.any(use_v >= 100):
            return None
        z = np.log(use_v / (100.0 - use_v))
        slope, intercept = np.polyfit(use_y, z, 1)
        return float(100.0 / (1.0 + np.exp(-(slope * target + intercept))))

    return rule


def _log_trend(window: int | None = None):
    """Linear trend in log space, exponentiated back."""

    def rule(years, values, target):
        use_y = np.asarray(
            years if window is None else years[-window:], dtype=float
        )
        use_v = np.asarray(
            values if window is None else values[-window:], dtype=float
        )
        if len(use_v) < 2 or np.any(use_v <= 0):
            return None
        slope, intercept = np.polyfit(use_y, np.log(use_v), 1)
        return float(np.exp(slope * target + intercept))

    return rule


def _ar1_on_differences():
    """Fit d_t = a + b d_{t-1} on first differences and iterate."""

    def rule(years, values, target):
        diffs = np.diff(np.asarray(values, dtype=float))
        if len(diffs) < 3:
            return None
        previous, nxt = diffs[:-1], diffs[1:]
        b = float(np.polyfit(previous, nxt, 1)[0])
        a = float(np.mean(nxt) - b * np.mean(previous))
        current, level = float(diffs[-1]), float(values[-1])
        for _ in range(target - years[-1]):
            current = a + b * current
            level = level + current
        return float(level)

    return rule


def _median_drift():
    """Random walk with drift equal to the median first difference."""

    def rule(years, values, target):
        diffs = np.diff(np.asarray(values, dtype=float))
        if len(diffs) < 1:
            return None
        return float(
            values[-1] + float(np.median(diffs)) * (target - years[-1])
        )

    return rule


def _ses(alpha: float):
    """Simple exponential smoothing: a flat forecast at the level."""

    def rule(years, values, target):
        level = float(values[0])
        for value in values[1:]:
            level = alpha * value + (1 - alpha) * level
        return level

    return rule


def _brown(alpha: float):
    """Brown's double exponential smoothing (linear trend form)."""

    def rule(years, values, target):
        single = double = float(values[0])
        for value in values[1:]:
            single = alpha * value + (1 - alpha) * single
            double = alpha * single + (1 - alpha) * double
        level = 2 * single - double
        slope = alpha / (1 - alpha) * (single - double)
        return float(level + slope * (target - years[-1]))

    return rule


def _damped_holt(alpha: float, beta: float, phi: float):
    """Holt with a damped trend."""

    def rule(years, values, target):
        level, trend = float(values[0]), float(values[1] - values[0])
        for value in values[1:]:
            previous = level
            level = alpha * value + (1 - alpha) * (level + phi * trend)
            trend = beta * (level - previous) + (1 - beta) * phi * trend
        horizon = target - years[-1]
        return float(
            level + trend * sum(phi**j for j in range(1, horizon + 1))
        )

    return rule


def _loess_linear(window: int):
    """Local linear fit with tricube weights centred on the last row."""

    def rule(years, values, target):
        use_y = np.asarray(years[-window:], dtype=float)
        use_v = np.asarray(values[-window:], dtype=float)
        if len(use_v) < 3:
            return None
        distance = np.abs(use_y - use_y[-1])
        span = distance.max() if distance.max() > 0 else 1.0
        weights = (1 - (distance / span) ** 3) ** 3
        slope, intercept = np.polyfit(use_y, use_v, 1, w=np.sqrt(weights))
        return float(slope * target + intercept)

    return rule


def _spline_from(knot: int):
    """OLS on the rows at or after a fixed knot year."""

    def rule(years, values, target):
        use_y = np.asarray(years, dtype=float)
        use_v = np.asarray(values, dtype=float)
        mask = use_y >= knot
        if mask.sum() < 2:
            return None
        slope, intercept = np.polyfit(use_y[mask], use_v[mask], 1)
        return float(slope * target + intercept)

    return rule


RESIDUAL_PROBE_SET_V3: dict = {
    "theil_sen_full": (_theil_sen(), "median pairwise slope, full window"),
    "theil_sen_last8": (_theil_sen(8), "median pairwise slope, last 8"),
    "theil_sen_last5": (_theil_sen(5), "median pairwise slope, last 5"),
    "wls0.9": (_wls(0.9), "OLS with 0.9^age recency weights, full"),
    "wls0.8": (_wls(0.8), "OLS with 0.8^age recency weights, full"),
    "wls0.7_last10": (
        _wls(0.7, 10),
        "OLS with 0.7^age recency weights, last 10",
    ),
    "logit_trend_full": (_logit_trend(), "linear trend in logit space"),
    "logit_trend_last8": (
        _logit_trend(8),
        "linear trend in logit space, last 8",
    ),
    "log_trend_full": (_log_trend(), "linear trend in log space"),
    "log_trend_last8": (
        _log_trend(8),
        "linear trend in log space, last 8",
    ),
    "ar1_on_differences": (
        _ar1_on_differences(),
        "AR(1) fitted to first differences, iterated to the target",
    ),
    "median_drift": (
        _median_drift(),
        "random walk with the median first difference as drift",
    ),
    "ses0.3": (_ses(0.3), "simple exponential smoothing, alpha 0.3"),
    "ses0.5": (_ses(0.5), "simple exponential smoothing, alpha 0.5"),
    "ses0.8": (_ses(0.8), "simple exponential smoothing, alpha 0.8"),
    "brown0.3": (_brown(0.3), "Brown double exponential, alpha 0.3"),
    "brown0.5": (_brown(0.5), "Brown double exponential, alpha 0.5"),
    "damped_holt(.5,.1,.85)": (
        _damped_holt(0.5, 0.1, 0.85),
        "Holt with a damped trend, alpha 0.5, beta 0.1, phi 0.85",
    ),
    "damped_holt(.8,.2,.9)": (
        _damped_holt(0.8, 0.2, 0.9),
        "Holt with a damped trend, alpha 0.8, beta 0.2, phi 0.9",
    ),
    "holt(.2,.05)": (_holt(0.2, 0.05), "Holt, alpha 0.2, beta 0.05"),
    "holt(.9,.5)": (_holt(0.9, 0.5), "Holt, alpha 0.9, beta 0.5"),
    "holt(.6,.4)": (_holt(0.6, 0.4), "Holt, alpha 0.6, beta 0.4"),
    "quartic_full": (_poly(4), "OLS degree 4 on the fit window"),
    "quartic_last10": (_poly(4, 10), "OLS degree 4 on the last 10 rows"),
    "cubic_last10": (_poly(3, 10), "OLS degree 3 on the last 10 rows"),
    "quad_last5": (_poly(2, 5), "OLS degree 2 on the last 5 rows"),
    "quad_last6": (_poly(2, 6), "OLS degree 2 on the last 6 rows"),
    "quad_last10": (_poly(2, 10), "OLS degree 2 on the last 10 rows"),
    "loess_last8": (
        _loess_linear(8),
        "tricube-weighted local linear fit on the last 8 rows",
    ),
    "loess_last10": (
        _loess_linear(10),
        "tricube-weighted local linear fit on the last 10 rows",
    ),
    "spline_knot2008": (_spline_from(2008), "OLS on 2008..T* only"),
    "spline_knot2005": (_spline_from(2005), "OLS on 2005..T* only"),
    "blend_quad8_pers_50": (
        _blend(_poly(2, 8), _persistence, 0.5),
        "0.50 * quad_last8 + 0.50 * persistence",
    ),
    "blend_quad8_drift3_50": (
        _blend(_poly(2, 8), _drift(3), 0.5),
        "0.50 * quad_last8 + 0.50 * drift3",
    ),
    "blend_theta_pers_50": (
        _blend(_theta(), _persistence, 0.5),
        "0.50 * theta + 0.50 * persistence",
    ),
}

ADMISSION_PROCEDURE = (
    "THE PANEL IS OPEN AND VERSIONED. It is not a claim to have "
    "enumerated every information-null rule -- no panel can -- so the "
    "contract states how a rule enters instead. (1) ADMISSIBILITY: a "
    "proposed rule is admissible iff it is INFORMATION-NULL by "
    "construction (it reads only rows of the fit source at or before "
    "the origin and cannot reach the resolution vintage), DETERMINISTIC "
    "(no seed, no randomisation), and IMPLEMENTABLE FROM ITS PUBLISHED "
    "FORMULA ALONE by a reader who has never seen this builder. (2) "
    "PROCEDURE: admission is an AMENDMENT -- public proposal, "
    "adversarial referee round, independent verification, maintainer "
    "ratification by merge -- and it increments panel_version. (3) "
    "EFFECT, which is mechanical and stated in advance so nobody has "
    "to be trusted about it: F2_panel_min is a MINIMUM, so adding a "
    "rule can only lower it; every tolerance it touches gets TIGHTER "
    "or stays equal; a pair whose new tolerance no longer sits "
    "strictly between the measurement lower bound and the panel "
    "minimum is DEMOTED to reported-not-gated; therefore the gated set "
    "can only SHRINK, never grow, and no admission can loosen a "
    "tolerance or admit a candidate the previous panel would have "
    "failed. (4) NO SELF-RESCUE: under gate_1's inherited amendment "
    "rules an admission binds only runs registered after its "
    "ratification, so a candidate that has already failed cannot be "
    "rescued by a later panel change and a candidate that has already "
    "passed cannot be retroactively failed by one. (5) THE WORKED "
    "EXAMPLE IS PUBLISHED: null_rule_exposure.out_of_panel_probe_set "
    "measures 35 unregistered rules against the v3 surface, and "
    "null_rule_exposure.counterfactual_if_every_probe_were_admitted "
    "computes the exact surface that admitting all 35 would produce."
)


# --------------------------------------------------------------------------
# FINDING 5: the tolerance POWER CAP.
#
# Every locked gate has one and the retrodiction arm had none. gate_2,
# gate_2b, gate_2c and gate_m4 all read `tolerance <= T_max = ln(1.5)`;
# gate_m6 carries `metric_caps` PER METRIC -- log_ratio and abs_gap_log
# at ln(1.5), and abs_gap_corr at 0.15 derived from a ratified tolerance
# in another gate, because a log cap has no meaning on a correlation.
#
# This arm's metrics are `abs_pp` (percentage points of a share) and
# `abs_years`. Neither is a log ratio, so ln(1.5) cannot be applied as a
# literal; gate_m6's own move -- derive a per-metric cap from a named
# source -- is the precedent, and this is the derivation:
#
#   |ln(pred / realized)| <= ln(1.5)  <=>  pred / realized in [2/3, 3/2].
#   The widest ABSOLUTE band entirely inside that ratio band is
#   |pred - realized| <= (1 - 1/1.5) * realized = realized / 3, because
#   the low side binds first: an absolute band of realized/2 would admit
#   pred = realized/2, a 2x error, which ln(1.5) exists to refuse.
#
# So CAP_FACTOR = 1 - 1/1.5 = 1/3 exactly, applied to the quantity's
# distance from the ZERO OF ITS OWN SCALE:
#
#   * abs_pp:    origin 0. A share of zero means nobody claims in that
#                band; the ratio reading is available and the cap is
#                realized / 3.
#   * abs_years: origin 62. A ratio cap on a mean claiming AGE is
#                meaningless -- the scale has no meaningful zero, and
#                realized/3 would be about 21 years, a cap that caps
#                nothing. 62 is the statutory earliest entitlement age
#                and the support floor of this very table (its first
#                category is `age62`), so `realized - 62` is the
#                quantity that does have a true zero: it is zero when
#                every award is claimed at the earliest possible age.
#
# A pair whose tolerance exceeds its cap is DEMOTED to
# reported-not-gated, following gate_2's grammar ("gate-eligible iff ...
# tolerance <= T_max"), NOT clipped to the cap. gate_m6 clips; clipping
# is rejected here because this arm's tolerance is a SKILL RATIO -- a
# clipped tolerance would no longer equal rho * F2_panel_min, so the
# published number would stop meaning "beat the null panel by 1/rho"
# and the instrument's one interpretive claim would need a second rule.
# --------------------------------------------------------------------------
CAP_FACTOR = 1.0 - 1.0 / 1.5
METRIC_ORIGINS = {"abs_pp": 0.0, "abs_years": 62.0}

POWER_CAP_LAW = (
    "POWER CAP, in the locked gates' grammar. A (cell, horizon) pair is "
    "gate-eligible only if tolerance(cell, h) <= cap(cell, h), where "
    "cap(cell, h) = (1 - 1/1.5) * (realized(cell, T*+h) - origin(unit)) "
    "and origin(unit) is 0 for abs_pp and 62 for abs_years. The factor "
    "is ln(1.5) transcribed into an absolute-deviation metric: "
    "|ln(pred/realized)| <= ln(1.5) is pred/realized in [2/3, 3/2], and "
    "the widest absolute band entirely inside it is realized/3, the low "
    "side binding first. The origin is the zero of the quantity's own "
    "scale: a share of zero is meaningful, a claiming age of zero is "
    "not, and 62 is the statutory earliest entitlement age and this "
    "table's own first category. A pair over its cap is REPORTED, NOT "
    "GATED -- demoted as in gate_2 and gate_m4, not clipped as in "
    "gate_m6, because a clipped tolerance would no longer equal "
    "rho * F2_panel_min and the skill-ratio reading would need a "
    "second rule."
)


def power_cap(key: str, unit: str, realized: float) -> float:
    """The cap for one (cell, horizon), in the cell's own unit."""
    origin = METRIC_ORIGINS[unit]
    exact = Decimal(str(CAP_FACTOR)) * Decimal(
        repr(round(float(realized) - origin, DEVIATION_ROUNDING))
    )
    return float(exact.quantize(Decimal("0.000001")))


# --------------------------------------------------------------------------
# Deviations, lower bounds and the v3 surface
# --------------------------------------------------------------------------
def _gated_cells() -> list[str]:
    """The 18 draft-eligible claiming cells, taken from v1 unchanged."""
    v1 = json.loads(V1_ARTIFACT.read_text())
    return sorted(
        key
        for key, entry in v1["cell_stability"].items()
        if entry["draft_gate_eligible"]
    )


def panel_deviations(
    cells: list[str],
    fit_series: dict,
    resolution_series: dict,
    registry: dict,
    rules: dict,
) -> dict:
    """Every rule's 6-dp deviation at the REGISTERED origin T* = 2012.

    The registered origin is the only basis for a tolerance: referee A's
    decision 3 and referee B's decision 3 agree that the rolling origins
    are nested prefixes of one realized series, so their across-block sd
    is not a replication dispersion. They appear below as provenance and
    as leg 2 of the pass rule, and enter no tolerance.
    """
    out = {}
    for key in cells:
        metric = METRICS[registry[key]["metric"]]
        fit = fit_series[key]
        realized = resolution_series[key]
        years = [y for y in sorted(fit) if FIT_FIRST_YEAR <= y <= T_STAR]
        values = [fit[y] for y in years]
        per_horizon = {}
        for horizon in GATED_HORIZONS:
            target = T_STAR + horizon
            if target not in realized:
                continue
            scored = {}
            for name, entry in rules.items():
                function = entry[0]
                try:
                    prediction = function(years, values, target)
                except (ValueError, np.linalg.LinAlgError, ZeroDivisionError):
                    prediction = None
                if prediction is None or not np.isfinite(prediction):
                    continue
                scored[name] = {
                    "prediction": round(float(prediction), DEVIATION_ROUNDING),
                    "deviation": deviation_6dp(
                        prediction, realized[target], metric
                    ),
                }
            per_horizon[f"h{horizon}"] = {
                "target_year": target,
                "realized": round(float(realized[target]), 6),
                "rules": scored,
                "n_rules_defined": len(scored),
            }
        out[key] = {
            "metric": registry[key]["metric"],
            "unit": registry[key]["unit"],
            "registered_origin": T_STAR,
            "fit_window": [FIT_FIRST_YEAR, T_STAR],
            "by_horizon": per_horizon,
        }
    return out


TOLERANCE_LAW = (
    "tolerance(cell, h) = rho * F2_panel_min(cell, h), where "
    "F2_panel_min is the SMALLEST 6-dp deviation, at the registered "
    "origin T* = 2012, over EVERY rule in the registered "
    "information-null panel (panel_version 3, 55 rules), evaluated in "
    "exact decimal arithmetic and quantised to 3 decimal places under "
    "ROUND_HALF_EVEN. A (cell, horizon) pair is GATED only if "
    "lower_bound(cell) < tolerance(cell, h) < F2_panel_min(cell, h), "
    "both inequalities STRICT, where lower_bound = max(F0, instrument "
    "A), AND tolerance(cell, h) <= cap(cell, h), the power cap. A pair "
    "failing any of the three is REPORTED, NOT GATED, with the reason "
    "recorded. There is no per-cell rule selection: the minimum is both "
    "the selection and the basis, which is what referee A's decision 3 "
    "and referee B's decision 3 independently required."
)

DEMOTION_EXACT = "a_registered_null_rule_is_EXACT_at_this_pair"
DEMOTION_NO_ROOM = "no_strict_room_below_the_null_panel"
DEMOTION_BELOW_FLOOR = (
    "tolerance_not_strictly_above_the_measurement_lower_bound"
)
DEMOTION_OVER_CAP = "tolerance_exceeds_the_power_cap"
DEMOTION_REASONS = (
    DEMOTION_EXACT,
    DEMOTION_NO_ROOM,
    DEMOTION_BELOW_FLOOR,
    DEMOTION_OVER_CAP,
)


def _panel_min(entry: dict, panel) -> tuple[float, str]:
    candidates = {
        name: row["deviation"]
        for name, row in entry["rules"].items()
        if name in panel
    }
    best = min(candidates, key=lambda name: candidates[name])
    return candidates[best], best


def gated_surface(
    deviations: dict, bounds: dict, *, panel, rho: float, cap: bool = True
) -> dict:
    """Apply the v3 tolerance law. Returns gated pairs AND demotions."""
    gated, demoted = {}, {}
    panel = set(panel)
    for key, entry in deviations.items():
        lower = bounds[key]["lower_bound_used"]
        unit_metric = entry["metric"]
        for horizon, row in entry["by_horizon"].items():
            if not (set(row["rules"]) & panel):
                continue
            floor_value, best_rule = _panel_min(row, panel)
            tolerance = tolerance_from(floor_value, rho)
            cap_value = power_cap(key, unit_metric, row["realized"])
            pair = f"{key}@{horizon}"
            common = {
                "F2_panel_min": floor_value,
                "achieved_by": best_rule,
                "tolerance_would_be": tolerance,
                "lower_bound": lower,
                "power_cap": cap_value,
            }
            if floor_value <= 0.0:
                demoted[pair] = {
                    "reason": DEMOTION_EXACT,
                    "detail": (
                        f"{best_rule} reproduces the realized value "
                        f"exactly at {row['target_year']}; no positive "
                        "tolerance can sit strictly below zero, so no "
                        "tolerance at this pair can certify skill"
                    ),
                    **common,
                }
                continue
            if not tolerance < floor_value:
                demoted[pair] = {
                    "reason": DEMOTION_NO_ROOM,
                    "detail": (
                        "rounding lifts rho * F2_panel_min to or above "
                        "the panel minimum itself"
                    ),
                    **common,
                }
                continue
            if not lower < tolerance:
                demoted[pair] = {
                    "reason": DEMOTION_BELOW_FLOOR,
                    "detail": (
                        "the panel minimum is so small that rho times "
                        "it lands at or below max(F0, instrument A) -- "
                        "the truth side cannot resolve the difference "
                        "between the candidate and a null rule here"
                    ),
                    **common,
                }
                continue
            if cap and tolerance > cap_value:
                demoted[pair] = {
                    "reason": DEMOTION_OVER_CAP,
                    "detail": (
                        "the tolerance is wider than the ln(1.5) power "
                        "cap transcribed into this cell's unit, so a "
                        "pass here would not reject a materially wrong "
                        "model"
                    ),
                    **common,
                }
                continue
            gated[pair] = {
                "tolerance": tolerance,
                "F2_panel_min": floor_value,
                "achieved_by": best_rule,
                "lower_bound": lower,
                "power_cap": cap_value,
                "target_year": row["target_year"],
                "realized": row["realized"],
                "room_ratio": round(floor_value / lower, 4),
                "cap_headroom": round(cap_value - tolerance, 6),
            }
    cells_gated = sorted({pair.split("@")[0] for pair in gated})
    all_horizons = sorted(
        key
        for key in deviations
        if deviations[key]["by_horizon"]
        and all(
            f"{key}@{horizon}" in gated
            for horizon in deviations[key]["by_horizon"]
        )
    )
    return {
        "panel_version": PANEL_VERSION,
        "n_panel_rules": len(panel),
        "rho": rho,
        "power_cap_applied": cap,
        "n_pairs_considered": sum(
            1
            for entry in deviations.values()
            for row in entry["by_horizon"].values()
            if row["rules"]
        ),
        "n_gated": len(gated),
        "n_reported_not_gated": len(demoted),
        "n_cells_with_at_least_one_gated_horizon": len(cells_gated),
        "cells_with_at_least_one_gated_horizon": cells_gated,
        "n_cells_gated_at_every_horizon": len(all_horizons),
        "cells_gated_at_every_horizon": all_horizons,
        "sum_of_tolerances": round(
            sum(row["tolerance"] for row in gated.values()), 3
        ),
        "demotion_census": {
            reason: sum(
                1 for row in demoted.values() if row["reason"] == reason
            )
            for reason in DEMOTION_REASONS
        },
        "gated": dict(sorted(gated.items())),
        "reported_not_gated": dict(sorted(demoted.items())),
    }


def null_rule_exposure(
    deviations: dict,
    probe_deviations: dict,
    combined_deviations: dict,
    surface: dict,
    bounds: dict,
    *,
    panel,
) -> dict:
    """Three measurements, of which only the third answers finding 1.

    ``in_panel``: every registered rule's pass count against the gated
    surface. Zero for all 55 by construction at rho < 1, computed rather
    than asserted.

    ``leave_one_out``: hold a rule out, re-derive from the other 54,
    count what the held-out rule then passes. This is the panel's
    exposure to ITS OWN MEMBERS. v2 published this number as "the honest
    residual exposure"; the independent verifier's finding 1 is that it
    is not, and this block now says so on its face.

    ``out_of_panel_probe_set``: 35 rules that are NOT in the panel,
    measured against the gated surface. THIS is the residual exposure,
    and it is the measurement v2 lacked.
    """
    panel = set(panel)
    in_panel = {}
    for name in sorted(panel):
        passes = 0
        for pair, row in surface["gated"].items():
            key, horizon = pair.split("@")
            rules = deviations[key]["by_horizon"][horizon]["rules"]
            if name in rules and rules[name]["deviation"] <= row["tolerance"]:
                passes += 1
        in_panel[name] = passes

    leave_one_out = {}
    for held in sorted(panel):
        reduced = panel - {held}
        sub = gated_surface(
            deviations, bounds, panel=reduced, rho=surface["rho"]
        )
        passes = [
            pair
            for pair, row in sub["gated"].items()
            if held
            in deviations[pair.split("@")[0]]["by_horizon"][
                pair.split("@")[1]
            ]["rules"]
            and deviations[pair.split("@")[0]]["by_horizon"][
                pair.split("@")[1]
            ]["rules"][held]["deviation"]
            <= row["tolerance"]
        ]
        leave_one_out[held] = {
            "n_gated_without_this_rule": sub["n_gated"],
            "n_passed_by_the_held_out_rule": len(passes),
            "pairs": sorted(passes),
        }

    gated_by_cell: dict[str, int] = {}
    for pair in surface["gated"]:
        key = pair.split("@")[0]
        gated_by_cell[key] = gated_by_cell.get(key, 0) + 1

    probes = {}
    for name in sorted(probe_deviations_names(probe_deviations)):
        hits = []
        for pair, row in surface["gated"].items():
            key, horizon = pair.split("@")
            rules = probe_deviations[key]["by_horizon"][horizon]["rules"]
            if name in rules and rules[name]["deviation"] <= row["tolerance"]:
                hits.append(pair)
        cleared = sorted(
            key
            for key, total in gated_by_cell.items()
            if sum(1 for pair in hits if pair.startswith(key + "@")) == total
        )
        probes[name] = {
            "n_passed_of_the_gated_surface": len(hits),
            "pairs": sorted(hits),
            "cells_cleared_at_every_gated_horizon": cleared,
            "n_gated_horizons_in_those_cells": {
                key: gated_by_cell[key] for key in cleared
            },
        }
    worst = max(
        probes, key=lambda name: probes[name]["n_passed_of_the_gated_surface"]
    )

    combined = gated_surface(
        combined_deviations,
        bounds,
        panel=panel | set(RESIDUAL_PROBE_SET_V3),
        rho=surface["rho"],
    )
    return {
        "what_in_panel_proves": (
            "a rule inside the registered panel passes ZERO gated "
            "pairs. True by construction at rho < 1 and computed here "
            "rather than asserted, because v1's equivalent claim ('a "
            "carried candidate would score EXACTLY the naive baseline, "
            "by construction') was false as bytes."
        ),
        "what_leave_one_out_measures": (
            "THE PANEL'S EXPOSURE TO ITS OWN MEMBERS, and nothing "
            "wider. v2 published this quantity (12 of 88) under the "
            "words 'the honest residual exposure'. The independent "
            "verifier's finding 1 is that the label was wrong by about "
            "a factor of two: leave-one-out cannot bound the exposure "
            "to a rule that was never in the panel, and the first "
            "unregistered class the verifier tried -- a degree-2 trend "
            "on the last eight fit rows -- passed 23 of v2's 88. The "
            "number is kept because it is informative about which "
            "panel members are load-bearing; the LABEL is corrected "
            "here and in the fragment."
        ),
        "what_the_probe_set_measures": (
            "THE RESIDUAL. 35 rules that are not in the panel and set "
            "no tolerance, drawn from classes the 55 does not contain, "
            "measured against the v3 gated surface. This is the "
            "measurement v2 did not have, and it is the one the "
            "residual_null_rule_exposure margin now quotes."
        ),
        "in_panel_pass_counts": in_panel,
        "n_registered_rules_passing_any_gated_pair": sum(
            1 for count in in_panel.values() if count
        ),
        "leave_one_out": leave_one_out,
        "worst_leave_one_out_rule": max(
            leave_one_out,
            key=lambda name: leave_one_out[name][
                "n_passed_by_the_held_out_rule"
            ],
        ),
        "out_of_panel_probe_set": {
            "n_probes": len(RESIDUAL_PROBE_SET_V3),
            "formulas": {
                name: entry[1]
                for name, entry in sorted(RESIDUAL_PROBE_SET_V3.items())
            },
            "results": probes,
            "worst_probe": worst,
            "worst_probe_n_passed": probes[worst][
                "n_passed_of_the_gated_surface"
            ],
            "n_gated_pairs": surface["n_gated"],
            "worst_probe_share_of_the_gated_surface": round(
                probes[worst]["n_passed_of_the_gated_surface"]
                / surface["n_gated"],
                4,
            ),
            "comparison_to_v2": (
                "the verifier measured its worst unregistered rule at "
                "23 of v2's 88 gated pairs (26.1 per cent of the "
                "surface). v3's worst unregistered probe is measured "
                "here against the v3 surface."
            ),
        },
        "counterfactual_if_every_probe_were_admitted": {
            "why_published": (
                "the admission procedure claims that admitting a rule "
                "can only tighten tolerances and only shrink the gated "
                "set. That claim is checkable, so it is checked: this "
                "is the exact surface a 90-rule panel would produce."
            ),
            "n_panel_rules": len(panel) + len(RESIDUAL_PROBE_SET_V3),
            "n_gated": combined["n_gated"],
            "n_reported_not_gated": combined["n_reported_not_gated"],
            "n_cells_with_at_least_one_gated_horizon": combined[
                "n_cells_with_at_least_one_gated_horizon"
            ],
            "sum_of_tolerances": combined["sum_of_tolerances"],
            "demotion_census": combined["demotion_census"],
            "gated_set_is_a_subset_of_the_v3_gated_set": set(combined["gated"])
            <= set(surface["gated"]),
            "no_tolerance_loosened": all(
                combined["gated"][pair]["tolerance"]
                <= surface["gated"][pair]["tolerance"]
                for pair in combined["gated"]
                if pair in surface["gated"]
            ),
        },
    }


def probe_deviations_names(probe_deviations: dict) -> set:
    names: set = set()
    for entry in probe_deviations.values():
        for row in entry["by_horizon"].values():
            names |= set(row["rules"])
    return names


# --------------------------------------------------------------------------
# FINDING 2: leg 2's blocks, defined by ONE rule.
#
# v2's pass rule said "origins are partitioned into the five stride-5
# blocks" and left two readings open:
#   (a) partition the NINE rolling origins 2004-2012 once, globally;
#   (b) partition each (cell, horizon) pair's own admissible origins.
# v2's builder did (b). The independent verifier computed both and found
# they give DIFFERENT blocks on 108 of 108 pairs, so the block-level
# conjunction had no single referent. Under (b) the blocks also differ
# BY HORIZON, and four of the five h2 blocks score only targets at or
# before T* -- rows the fence lets a candidate read, so those blocks
# would be free.
#
# v3 takes reading (a) and says so:
#
#   BLOCKS: the nine rolling origins 2004..2012 are partitioned ONCE,
#   globally, by stride 5 on the ascending origin list. The five blocks
#   are {2004,2009} {2005,2010} {2006,2011} {2007,2012} {2008}. They do
#   not depend on the cell, the horizon, or which targets are
#   admissible, so "every gated pair at every origin in that block" has
#   exactly one referent.
#
#   DROPPED TARGETS: an (origin, horizon) whose target year is excluded
#   (2013, 2020-2022) or absent from the resolution vintage imposes NO
#   CONSTRAINT. It is not a pass and not a failure; there is nothing
#   there to score.
#
#   NON-VACUITY, measured not assumed: every one of the five blocks
#   carries at least one admissible (origin, horizon) whose target is
#   AFTER T*, so no block can be passed for free out of rows the fence
#   already hands the candidate. The measurement is published below.
# --------------------------------------------------------------------------
LEG2_BLOCK_LAW = (
    "LEG 2 BLOCKS, ONE RULE. The nine rolling origins 2004..2012 are "
    "partitioned ONCE, globally, into five stride-5 blocks of the "
    "ascending origin list: {2004, 2009}, {2005, 2010}, {2006, 2011}, "
    "{2007, 2012}, {2008}. The partition does not depend on the cell, "
    "the horizon or which targets are admissible, so the block-level "
    "conjunction has exactly one referent. An (origin, horizon) whose "
    "target year is excluded (2013, 2020-2022) or absent from the "
    "resolution vintage imposes NO CONSTRAINT -- it is neither a pass "
    "nor a failure. A block PASSES iff every gated (cell, horizon) pair "
    "is in band at every origin in that block for which the target is "
    "admissible. Leg 2 passes iff at least 4 of the 5 blocks pass. The "
    "blocks are UNEQUAL by construction -- sizes (2, 2, 2, 2, 1) -- so "
    "the 4-of-5 allowance waives one origin if the singleton block "
    "{2008} is the one dropped and two origins otherwise; that "
    "asymmetry is an allowance, not a dispersion, and is disclosed as "
    "one."
)


def rolling_origin_provenance(
    cells: list[str],
    fit_series: dict,
    resolution_series: dict,
    registry: dict,
    *,
    panel,
) -> dict:
    """Panel-minimum deviation at every rolling origin, one block rule."""
    panel = set(panel)
    origins = list(range(ROLLING_ORIGIN_FIRST, T_STAR + 1))
    blocks = {str(seed): origins[seed :: len(SEEDS)] for seed in SEEDS}
    admissible_by_horizon = {
        f"h{horizon}": [
            origin
            for origin in origins
            if (origin + horizon) not in EXCLUDED_TARGET_YEARS
        ]
        for horizon in GATED_HORIZONS
    }
    block_reach = {}
    for seed, members in blocks.items():
        admissible = [
            [origin, horizon]
            for origin in members
            for horizon in GATED_HORIZONS
            if (origin + horizon) not in EXCLUDED_TARGET_YEARS
        ]
        post = [pair for pair in admissible if pair[0] + pair[1] > T_STAR]
        block_reach[seed] = {
            "origins": members,
            "n_origins": len(members),
            "n_admissible_origin_horizon": len(admissible),
            "n_with_a_post_T_star_target": len(post),
            "post_T_star_origin_horizon": post,
            "is_free_under_the_fence": not post,
        }

    out = {}
    for key in cells:
        metric = METRICS[registry[key]["metric"]]
        fit = fit_series[key]
        realized = resolution_series[key]
        per_horizon = {}
        for horizon in GATED_HORIZONS:
            by_origin = {}
            for origin in admissible_by_horizon[f"h{horizon}"]:
                target = origin + horizon
                if target not in realized or origin not in fit:
                    continue
                years = [
                    y for y in sorted(fit) if FIT_FIRST_YEAR <= y <= origin
                ]
                values = [fit[y] for y in years]
                best = None
                for name in panel:
                    function = NULL_RULE_PANEL_V3[name][0]
                    try:
                        prediction = function(years, values, target)
                    except (
                        ValueError,
                        np.linalg.LinAlgError,
                        ZeroDivisionError,
                    ):
                        continue
                    if prediction is None or not np.isfinite(prediction):
                        continue
                    deviation = deviation_6dp(
                        prediction, realized[target], metric
                    )
                    if best is None or deviation < best:
                        best = deviation
                if best is not None:
                    by_origin[origin] = best
            if not by_origin:
                continue
            per_horizon[f"h{horizon}"] = {
                "admissible_origins": sorted(by_origin),
                "n_admissible_origins": len(by_origin),
                "inadmissible_origins": [
                    origin for origin in origins if origin not in by_origin
                ],
                "panel_min_by_origin": {
                    str(origin): by_origin[origin]
                    for origin in sorted(by_origin)
                },
                "origins_in_each_block": {
                    seed: [o for o in members if o in by_origin]
                    for seed, members in blocks.items()
                },
            }
        out[key] = per_horizon
    return {
        "status": (
            "PROVENANCE AND THE LEG-2 REFERENT. No tolerance in this "
            "artifact reads any number in this block."
        ),
        "block_law": LEG2_BLOCK_LAW,
        "blocks": blocks,
        "block_sizes": [len(blocks[str(seed)]) for seed in SEEDS],
        "blocks_are_equal_sized": len(
            {len(blocks[str(seed)]) for seed in SEEDS}
        )
        == 1,
        "n_single_observation_blocks": sum(
            1 for seed in SEEDS if len(blocks[str(seed)]) == 1
        ),
        "block_shape": str(tuple(len(blocks[str(seed)]) for seed in SEEDS)),
        "why_one_global_partition": (
            "the independent verifier measured that a per-pair "
            "partition of each pair's admissible origins and a global "
            "partition of all nine origins give DIFFERENT blocks on "
            "108 of 108 pairs, and that under the per-pair reading the "
            "blocks differ by horizon, so 'every gated pair at every "
            "origin in that block' had no single referent. One global "
            "partition removes the ambiguity: the blocks are the same "
            "five sets for every cell and every horizon."
        ),
        "why_no_dispersion_is_taken_from_it": (
            "the origins are NESTED PREFIXES (referee A 3.2): origin "
            "2004 fits 1998-2004, origin 2009 fits 1998-2009 and "
            "contains all of it, origin 2012 contains both. The blocks "
            "are disjoint in ORIGIN LABEL only; the underlying fit rows "
            "are maximally overlapping and the targets are adjacent "
            "years of one autocorrelated series. An across-block sd "
            "computed on these is not a between-replication dispersion "
            "and its bias relative to a true replication sd is "
            "UNDETERMINED IN SIGN from what is committed."
        ),
        "admissible_origins_by_horizon": admissible_by_horizon,
        "n_admissible_origins_by_horizon": {
            horizon: len(value)
            for horizon, value in admissible_by_horizon.items()
        },
        "dropped_origin_horizon": [
            [origin, horizon]
            for origin in origins
            for horizon in GATED_HORIZONS
            if (origin + horizon) in EXCLUDED_TARGET_YEARS
        ],
        "block_reach_under_the_fence": block_reach,
        "no_block_is_free_under_the_fence": all(
            not entry["is_free_under_the_fence"]
            for entry in block_reach.values()
        ),
        "cells": out,
    }


PASS_RULE_V3 = (
    "Pair-level conjunction with a rolling-origin stability leg. "
    "LEG 1 (registered origin, T* = 2012): the candidate passes leg 1 "
    "iff EVERY gated (cell, horizon) pair is in band -- "
    "deviation(candidate, cell, h) <= tolerance(cell, h) -- with no "
    "n-of-m allowance over pairs, cells or horizons. "
    "LEG 2 (rolling-origin stability): the candidate is re-fit at each "
    "rolling origin 2004-2012 and re-scored against the same "
    "panel-derived tolerances. The nine origins are partitioned ONCE, "
    "globally, by stride 5 on the ascending origin list, giving the "
    "five blocks {2004, 2009}, {2005, 2010}, {2006, 2011}, "
    "{2007, 2012}, {2008}; the partition does not depend on the cell, "
    "the horizon or which targets are admissible. An (origin, horizon) "
    "whose target year is excluded (2013, 2020-2022) or absent from "
    "the resolution vintage imposes NO CONSTRAINT. A block passes iff "
    "every gated pair is in band at every origin in that block for "
    "which the target is admissible, and leg 2 passes iff at least 4 "
    "of the 5 blocks pass. THE GATE PASSES IFF LEG 1 AND LEG 2 BOTH "
    "PASS. A single breach of leg 1 fails the gate."
)


def pass_rule_draft(surface: dict, rolling: dict) -> dict:
    """A conjunction in the locked gates' grammar, with real counts."""
    gated_cells: dict[str, list[str]] = {}
    for pair in surface["gated"]:
        key, horizon = pair.split("@")
        gated_cells.setdefault(key, []).append(horizon)
    return {
        "status": "DRAFT FOR THE RATIFYING ROUND. Not locked, not applied.",
        "pass_rule": PASS_RULE_V3,
        "leg_2_block_law": LEG2_BLOCK_LAW,
        "why_the_seed_leg_cannot_be_inherited": (
            "gate_1, gate_2, gate_2b, gate_2c, gate_w1, gate_m4 and "
            "gate_m6 all state an n-of-5-SEED conjunction over person- "
            "or household-disjoint splits. This arm's truth side is a "
            "100-percent MBR census, so there is no split to seed, and "
            "the recommended instrument reads ONE registered origin. "
            "Referee A 3.3 established that under `basis: "
            "registered_origin` the five stride-5 blocks contribute "
            "nothing to any tolerance. A pass rule that cited '4 of 5 "
            "seeds' here would be citing an object this arm does not "
            "have."
        ),
        "replacement_for_the_seed_leg": (
            "REGISTERED ORIGIN (leg 1) plus ROLLING-ORIGIN BLOCKS "
            "(leg 2). Leg 1 is the number a candidate actually competes "
            "against and is one realization (n = 1), stated as such. "
            "Leg 2 requires the candidate to be RE-FIT at each rolling "
            "origin and re-scored, which converts the nested-prefix "
            "origins from a dispersion claim they cannot support into a "
            "STABILITY requirement they can."
        ),
        "why_leg_1_is_all_pairs_not_n_of_m": (
            "gate_2's conjunction is 'every gate-eligible cell ... at "
            "seed s' AND '>=4 of 5 seeds': the n-of-m allowance is over "
            "SEEDS, never over cells. There is no seed axis here, so "
            "the only faithful transcription of that grammar is "
            "all-cells-all-horizons on leg 1, with the n-of-m allowance "
            "moved to the axis that replaced seeds."
        ),
        "leg_2_allowance_disclosed": (
            "the five blocks have sizes (2, 2, 2, 2, 1). '4 of 5' "
            "therefore waives ONE origin if the singleton block {2008} "
            "is the one that fails and TWO origins otherwise. That is "
            "an allowance with an uneven price, and it is disclosed as "
            "an allowance rather than presented as a dispersion."
        ),
        "leg_2_is_not_free_under_the_fence": {
            "claim": (
                "no block can be passed purely out of rows the fenced "
                "reference already hands the candidate (targets at or "
                "before T* = 2012)"
            ),
            "measured": rolling["no_block_is_free_under_the_fence"],
            "per_block_post_T_star_counts": {
                seed: entry["n_with_a_post_T_star_target"]
                for seed, entry in rolling[
                    "block_reach_under_the_fence"
                ].items()
            },
        },
        "counts": {
            "n_gated_pairs": surface["n_gated"],
            "n_gated_cells": len(gated_cells),
            "n_cells_gated_at_every_horizon": surface[
                "n_cells_gated_at_every_horizon"
            ],
            "cells_gated_at_every_horizon": surface[
                "cells_gated_at_every_horizon"
            ],
            "gated_horizons": list(GATED_HORIZONS),
            "gated_target_years": [T_STAR + h for h in GATED_HORIZONS],
            "registered_origin": T_STAR,
            "n_registered_origin_realizations": 1,
            "rolling_origins": [ROLLING_ORIGIN_FIRST, T_STAR],
            "n_rolling_origins": len(range(ROLLING_ORIGIN_FIRST, T_STAR + 1)),
            "rolling_origin_blocks": rolling["blocks"],
            "block_shape": rolling["block_shape"],
            "n_rolling_origin_blocks": len(SEEDS),
            "n_admissible_origins_by_horizon": rolling[
                "n_admissible_origins_by_horizon"
            ],
            "leg_2_conjunction": f"4 of {len(SEEDS)} blocks",
            "cells_and_their_gated_horizons": {
                key: sorted(horizons, key=lambda h: int(h[1:]))
                for key, horizons in sorted(gated_cells.items())
            },
        },
        "publishes_regardless": (
            "`publishes_regardless` is NOT a gates.yaml key -- it "
            "appears zero times in the file and lives in the RUN "
            "contract. So it belongs in the fragment's "
            "`governance.registration` and `fresh_run_artifact_schema`, "
            "not beside the pass rule."
        ),
        "no_self_rescue": (
            "Inherited verbatim from gate_1.amendment_rules: no "
            "candidate's committed run verdict changes under a rule "
            "proposed after that run. This bites hard here, because "
            "the panel is OPEN: admitting a fifty-sixth null rule "
            "TIGHTENS every tolerance it touches, and no_self_rescue "
            "means a candidate that has already failed cannot be "
            "rescued by a later panel change, nor can a candidate that "
            "has already passed be retroactively failed by one."
        ),
    }


# --------------------------------------------------------------------------
# FINDING 4: the cell partition.
#
# v1 used glob patterns in `report_only`: referee A measured that
# `covered_earnings.*` matched ZERO registry keys and `di_stock_*`
# missed `di_worker_termination_rate`, leaving 5 of the 17 non-eligible
# cells with no contract text. v2 replaced the globs with an explicit
# six-entry enumeration -- and left 10 with none, the whole di_stock_*
# family, with `di_worker_termination_rate` surviving only inside a YAML
# comment. The verifier called that a regression on v1, correctly:
# referee A's D6 asked for enumeration, not for a smaller surface.
#
# v3 enumerates all 17 with their blocking reasons, and pins the
# partition: every one of the registry's 35 cells is in exactly one of
# GATED, ELIGIBLE-BUT-NOT-GATED, or REPORT-ONLY.
# --------------------------------------------------------------------------
def cell_partition(registry: dict, surface: dict) -> dict:
    """gated + eligible_not_gated + report_only == the whole registry."""
    v1 = json.loads(V1_ARTIFACT.read_text())
    stability = v1["cell_stability"]
    all_cells = sorted(registry)
    eligible = sorted(
        key for key in all_cells if stability[key]["draft_gate_eligible"]
    )
    non_eligible = sorted(
        key for key in all_cells if not stability[key]["draft_gate_eligible"]
    )
    gated = sorted({pair.split("@")[0] for pair in surface["gated"]})
    eligible_not_gated = sorted(set(eligible) - set(gated))
    report_only = {
        key: {
            "family": stability[key]["family"],
            "unit": registry[key]["unit"],
            "blocking_reasons": stability[key]["blocking_reasons"],
            "two_publication_vintages_in_repository": stability[key][
                "two_vintage"
            ],
        }
        for key in non_eligible
    }
    partition_ok = (
        set(gated) | set(eligible_not_gated) | set(non_eligible)
        == set(all_cells)
    ) and not (
        set(gated) & set(eligible_not_gated)
        or set(gated) & set(non_eligible)
        or set(eligible_not_gated) & set(non_eligible)
    )
    return {
        "law": (
            "Every cell in the registry is in EXACTLY ONE class. GATED: "
            "at least one (cell, horizon) pair carries a tolerance. "
            "ELIGIBLE_NOT_GATED: the cell is draft-gate-eligible but "
            "the tolerance law demotes every one of its horizons, so it "
            "is published and never scored. REPORT_ONLY: the cell is "
            "not draft-gate-eligible at all, for the recorded reason, "
            "so it is published and never scored. No glob patterns: "
            "referee A measured that v1's `covered_earnings.*` matched "
            "zero registry keys and `di_stock_*` missed "
            "`di_worker_termination_rate`."
        ),
        "n_registry_cells": len(all_cells),
        "n_gated": len(gated),
        "n_eligible_not_gated": len(eligible_not_gated),
        "n_report_only": len(non_eligible),
        "partition_is_exact": partition_ok,
        "gated": gated,
        "eligible_not_gated": {
            key: {
                "reason": (
                    "draft-gate-eligible, but every horizon is demoted "
                    "by the tolerance law"
                ),
                "demoted_horizons": sorted(
                    (f"{pair.split('@')[1]} " f"({row['reason']})")
                    for pair, row in surface["reported_not_gated"].items()
                    if pair.split("@")[0] == key
                ),
            }
            for key in eligible_not_gated
        },
        "report_only": report_only,
        "report_only_names": non_eligible,
        "v1_and_v2_coverage_defect": {
            "v1": (
                "glob patterns: `covered_earnings.*` matched 0 of the "
                "35 registry keys and `di_stock_*` missed "
                "`di_worker_termination_rate`, so 5 of the 17 "
                "non-eligible cells had no contract text"
            ),
            "v2": (
                "an explicit enumeration of six, which left 10 of the "
                "17 with no contract text -- the whole di_stock_* "
                "family. `di_worker_termination_rate` appeared only "
                "inside a YAML comment. A regression on v1, and the "
                "reason test_D6 could not catch it is that it asserted "
                "only that no entry contains a `*`."
            ),
            "v3": (
                "all 17 enumerated with their blocking reasons, and the "
                "partition pinned by test rather than by eye"
            ),
            "n_non_eligible_cells_without_contract_text_v1": 5,
            "n_non_eligible_cells_without_contract_text_v2": 10,
            "n_non_eligible_cells_without_contract_text_v3": 0,
        },
    }


# --------------------------------------------------------------------------
# FINDING 3: the counts a report may state are EMITTED, not typed.
#
# v2's report printed `n_rolling_origins_per_pair observed [6, 7, 8]`
# where v2's own artifact and fragment both said [8]; it printed a
# block-shape census of 252 / 36 / 36 where the artifact measured one
# shape at all 108 block sets; and it attributed that census to referee
# B, who never wrote it (B's own correction reports 310 blocks of 8, 210
# of 9, 70 of 7 and 40 of 6 -- a different statistic over a different
# index set). The artifact was right and the prose was wrong.
#
# The structural cure is to stop typing counts. Every count the v3
# report is entitled to state is emitted HERE, as a sentence, resolved
# from a dotted path into this artifact; the test suite re-resolves each
# path and requires the value to appear in the sentence. A report that
# quotes these sentences cannot contradict the artifact, and a report
# that states a count NOT in this block is stating something the
# artifact does not carry.
# --------------------------------------------------------------------------
def _dig(obj, dotted: str):
    for part in dotted.split("."):
        obj = obj[part]
    return obj


REPORT_COUNT_SPECS = (
    (
        "n_pairs_considered",
        "gated_surface_recommended.n_pairs_considered",
        "The v3 surface considers {} (cell, horizon) pairs, the same "
        "108 v1 and v2 considered.",
    ),
    (
        "n_gated",
        "gated_surface_recommended.n_gated",
        "The v3 gated surface is {} (cell, horizon) pairs.",
    ),
    (
        "n_reported_not_gated",
        "gated_surface_recommended.n_reported_not_gated",
        "Pairs REPORTED, NOT GATED, each with its reason: {}.",
    ),
    (
        "n_gated_cells",
        "gated_surface_recommended.n_cells_with_at_least_one_gated_horizon",
        "The gated pairs fall in {} cells.",
    ),
    (
        "n_cells_gated_at_every_horizon",
        "gated_surface_recommended.n_cells_gated_at_every_horizon",
        "Cells gated at every one of their horizons: {}.",
    ),
    (
        "sum_of_tolerances",
        "gated_surface_recommended.sum_of_tolerances",
        "The gated tolerances sum to {}.",
    ),
    (
        "n_panel_rules",
        "null_rule_panel.n_rules",
        "The registered information-null panel holds {} rules at "
        "panel_version 3.",
    ),
    (
        "n_registered_rules_passing_a_gated_pair",
        "null_rule_exposure.n_registered_rules_passing_any_gated_pair",
        "Registered rules passing any gated pair: {}.",
    ),
    (
        "worst_probe_n_passed",
        "null_rule_exposure.out_of_panel_probe_set.worst_probe_n_passed",
        "The worst UNREGISTERED probe passes {} of the gated pairs.",
    ),
    (
        "worst_probe",
        "null_rule_exposure.out_of_panel_probe_set.worst_probe",
        "The worst unregistered probe is {}.",
    ),
    (
        "n_probes",
        "null_rule_exposure.out_of_panel_probe_set.n_probes",
        "The out-of-panel probe set holds {} rules.",
    ),
    (
        "counterfactual_n_gated",
        "null_rule_exposure.counterfactual_if_every_probe_were_admitted"
        ".n_gated",
        "Gated pairs left if all 35 probes were admitted: {}.",
    ),
    (
        "n_rolling_origins",
        "pass_rule_draft.counts.n_rolling_origins",
        "Leg 2 runs over {} rolling origins, 2004 to 2012.",
    ),
    (
        "n_rolling_origin_blocks",
        "pass_rule_draft.counts.n_rolling_origin_blocks",
        "They are partitioned once, globally, into {} stride-5 blocks.",
    ),
    (
        "block_shape",
        "rolling_origin_provenance.block_shape",
        "The block shape is {}, the same for every cell and every " "horizon.",
    ),
    (
        "n_single_observation_blocks",
        "rolling_origin_provenance.n_single_observation_blocks",
        "Single-observation blocks among the five: {}.",
    ),
    (
        "n_registry_cells",
        "cell_partition.n_registry_cells",
        "The registry holds {} cells.",
    ),
    (
        "n_report_only",
        "cell_partition.n_report_only",
        "Non-eligible cells enumerated as report_only with their "
        "blocking reasons: {}.",
    ),
    (
        "n_eligible_not_gated",
        "cell_partition.n_eligible_not_gated",
        "Cells draft-gate-eligible but gating at no horizon: {}.",
    ),
    (
        "n_cap_demotions",
        "power_cap.n_demoted_on_the_v3_surface",
        "Pairs the power cap demotes on the v3 surface: {}.",
    ),
    (
        "n_cap_demotions_on_v2",
        "power_cap.n_demoted_if_applied_to_the_v2_surface",
        "Pairs the same cap would demote on v2's committed 88-pair "
        "surface: {}.",
    ),
    (
        "n_cap_demotions_on_v1_panel",
        "power_cap.n_demoted_if_applied_to_the_v1_panel_surface",
        "Pairs it would demote on the v1 two-rule panel at rho = 0.75: " "{}.",
    ),
)

FORBIDDEN_REPORT_STRINGS = (
    "[6, 7, 8]",
    "(2, 2, 1, 1, 1)",
    "(2, 1, 1, 1, 1)",
    "252 of 324",
    "two to four of the five",
)


def report_counts(artifact: dict) -> dict:
    """Every count the v3 report may state, emitted from the artifact."""
    sentences = {}
    for name, path, template in REPORT_COUNT_SPECS:
        value = _dig(artifact, path)
        sentences[name] = {
            "value": value,
            "artifact_path": path,
            "sentence": template.format(value),
        }
    return {
        "law": (
            "A count in the v3 report is quoted from this block or it "
            "is not stated. Each entry names the dotted path in this "
            "artifact it was resolved from; "
            "tests/test_gate3_retrodiction_floors_v3.py re-resolves "
            "every path and requires the value to appear in the "
            "sentence, so a typed number cannot drift from a computed "
            "one."
        ),
        "why": (
            "v2's report printed a THREE-element origin-count "
            "list for `n_rolling_origins_per_pair observed` "
            "where v2's artifact and fragment both carried the "
            "single-element list, and printed a block-shape census "
            "of 252 / 36 / 36 "
            "attributed to referee B, where the artifact measured a "
            "single shape at all 108 block sets and referee B never "
            "wrote that census. The artifact was right; the prose was "
            "wrong; and the v2 test for that block asserted only that "
            "the blocks were unequal, which the true shape satisfies."
        ),
        "misattribution_corrected": (
            "The 252 / 36 / 36 census over 324 cell x rule x horizon "
            "combinations appears in v2's builder comment and report "
            "attributed to referee B. Referee B did not write it. "
            "Referee B's own correction 2 reports 310 blocks of 8, 210 "
            "of 9, 70 of 7 and 40 of 6 -- a different statistic over a "
            "different index set. v3 attributes the 252 / 36 / 36 "
            "census to nobody, because no source for it has been "
            "located, and carries it as no measurement of its own: "
            "counting BOTH the spaced and the unspaced spelling, the "
            "figures occur in this artifact ONLY inside THREE fields "
            "-- this correction, the `why` beside it, and "
            "answers_the_verifier.3_report_contradicts_artifact."
            "verdict_in_the_verifier_report, which summarises the "
            "first verifier's own finding -- and each of the three "
            "describes the defect rather than asserting the census. "
            "The correction v3's second sitting wrote here named two "
            "fields because it counted the spaced spelling alone; the "
            "second independent verification counted both spellings "
            "and found the third."
        ),
        "forbidden_strings": list(FORBIDDEN_REPORT_STRINGS),
        "why_forbidden": (
            "these are the v1-shaped counts v2's report carried into a "
            "v2 context. None of them describes this artifact, and "
            "tests/test_gate3_retrodiction_floors_v3.py serialises the "
            "WHOLE artifact and requires each of them to occur EXACTLY "
            "ONCE -- the occurrence inside this list -- so a stale "
            "count cannot be reintroduced anywhere else and the ban "
            "cannot be satisfied by deleting the list."
        ),
        "self_description_law": (
            "FINDING 3'S STANDARD, TURNED ON THESE BYTES. A sentence "
            "here that describes this artifact must be true of it. "
            "The check is mechanical and lives in "
            "tests/test_gate3_retrodiction_floors_v3.py::"
            "test_every_self_referential_claim_is_registered_and_true"
            ": every string leaf is matched against a fixed "
            "self-reference regex; the matching dotted paths must be "
            "exactly the FOURTEEN registered claims; and each "
            "registered claim carries its own predicate over the "
            "serialised bytes. v3's second and fourth sittings ran "
            "that sweep over report_counts and missed two claims, "
            "which the second independent verification found by "
            "running it over every leaf. A self-describing sentence "
            "added by a later hand fails the registry check until it "
            "is registered with a predicate of its own. This clause "
            "is checked too: the same test requires the number it "
            "names to equal the size of the registry it enforces."
        ),
        "sentences": sentences,
    }


# --------------------------------------------------------------------------
# FINDING 7: A8's two cures, side by side. v3 chooses NEITHER.
# --------------------------------------------------------------------------
NARROWED_TRANCHE_DESCRIPTION = (
    "gate_3 retrodiction arm (tranche): the PSEUDO-VINTAGE "
    "retrodiction of the claiming-age distribution of retired-worker "
    "awards, SSA Annual Statistical Supplement Table 6.B5.1, fit only "
    "on rows the 2014 Supplement printed and settled (entitlement "
    "years 1998-2012) and scored against the 2023 Supplement's settled "
    "rows for entitlement years 2014-2019, with a published deviation "
    "log. No other Tier-2 quantity, no live resolution, and no other "
    "table is claimed."
)

CURE_A_GATE_3_DESCRIPTION = (
    "gate_3 (retrodiction arm only, at this lock): the PSEUDO-VINTAGE "
    "retrodiction of the claiming-age distribution of retired-worker "
    "awards, SSA Annual Statistical Supplement Table 6.B5.1, graded "
    "against a published deviation log. The Tier-2 LIVE-RESOLUTION "
    "arm -- near-term components resolving against administrative "
    "publications on named resolution rules -- is NOT claimed by this "
    "gate and is declared as the unlocked sibling gate_3b_live_"
    "resolution below."
)


def description_defect(gates_text: str) -> dict:
    """Both referees' A8 cures, written out, with neither applied."""
    current = (
        "Tier-2 near-term components resolve against administrative "
        "publications on named resolution rules; retrodiction backtests "
        "grade as pseudo-vintage with a published deviation log."
    )
    return {
        "status": (
            "TWO ALTERNATIVE PROPOSED TEXTS. NEITHER IS APPLIED. "
            "gates.yaml is untouched. v3 does not choose between them: "
            "the referees disagree, both readings are defensible under "
            "the ratified rule, and the choice is the ratifying round's "
            "to make."
        ),
        "binding_rule": (
            "description_claims_exactly_the_scored_surface, promoted "
            "into gate_2.governance.amendment_rules by amendment 2. Its "
            "`applies_to` list names gate_3 explicitly."
        ),
        "rule_text_verbatim": (
            "A gate or tranche's description and holdout_basis must "
            "claim EXACTLY the surface its gated cells score at lock "
            "time -- no provision class, holdout, or transition named "
            "in the headline beyond what the cells actually gate. A "
            "headline broader than the scored surface is a lock defect, "
            "to be corrected before ratification."
        ),
        "current_description_verbatim": current,
        "current_description_is_in_gates_yaml": current
        in " ".join(gates_text.split()),
        "the_defect": (
            "gate_3's description has two clauses. Clause (a), 'Tier-2 "
            "near-term components resolve against administrative "
            "publications on named resolution rules', is the "
            "LIVE-RESOLUTION arm -- out of this arm's scope, binding "
            "FUTURE publications, and scored by NO cell. Clause (b) is "
            "the retrodiction arm, and even that is scored for one "
            "quantity family from one table."
        ),
        "THE_DECISION_THE_RATIFYING_ROUND_MUST_TAKE": (
            "Referee A and referee B proposed DIFFERENT cures and v2 "
            "implemented B's while presenting it as A's. They are set "
            "out below as cure_A and cure_B, each with its own referee's "
            "words, its own fragment text, and its own consequences. "
            "v3 implements NEITHER: the fragment below is emitted in "
            "BOTH forms and the ceremony picks one. Picking is not "
            "optional -- under the ratified rule an unnarrowed headline "
            "over a narrow scored surface is a lock defect, so leaving "
            "this open blocks the lock."
        ),
        "cure_A_referee_A": {
            "referee": "A (protocol and record lens)",
            "referee_words_verbatim": (
                "narrow the description to clause (b) and to the "
                "claiming-age surface actually scored, moving clause "
                "(a) to a declared unlocked sibling arm"
            ),
            "and_also": (
                "referee A adds: '(ii) alone leaves the headline "
                "broad' -- that is, the not_certified margin is the "
                "candour standard that should ACCOMPANY the narrowing, "
                "not a substitute for it."
            ),
            "what_changes_in_the_fragment": [
                "gate_3.description is REPLACED by the narrowed text",
                "a sibling block gate_3b_live_resolution is declared, "
                "unlocked, with no floor and no scored run",
                "the retrodiction surface still locks as the tranche "
                "gate_3a_retrodiction_claiming",
            ],
            "proposed_gate_3_description": CURE_A_GATE_3_DESCRIPTION,
            "reason_it_is_right": (
                "the ratified rule binds 'a gate OR TRANCHE's "
                "description'. gate_3 is the object a reader meets "
                "first, and after this lock gate_3 will carry gated "
                "cells underneath it; a headline that still names the "
                "live-resolution arm is broader than anything scored "
                "anywhere under gate_3. Reading the rule as satisfied "
                "by a narrow tranche headline under a broad gate "
                "headline lets any gate keep an unscored claim forever "
                "by pushing the cells one level down."
            ),
            "consequence_D8_sequencing": (
                "referee A's own D8: v1's committed artifact pins "
                "`arm_scope.gate_3_text_verbatim` and v1's test "
                "requires that text to appear in gates.yaml. Narrowing "
                "gate_3.description therefore INVALIDATES the committed "
                "v1 artifact and forces a v1 rebuild and a new v1 "
                "sha256 -- which in turn moves the digest v2 and v3 "
                "pin. Under cure A the ceremony must sequence that "
                "rebuild, or amend v1's test, before the lock."
            ),
            "cost": (
                "a v1 rebuild, a new v1 digest, and re-pinning it in "
                "the v2 and v3 builders and test suites"
            ),
        },
        "cure_B_referee_B": {
            "referee": "B (numbers and statistics lens)",
            "referee_words_verbatim": (
                "Lock a named sub-gate ... leaving `gate_3` itself "
                "unlocked for the live arm"
            ),
            "what_changes_in_the_fragment": [
                "gate_3.description is LEFT AS IT IS",
                "no live-arm sibling block is declared",
                "the retrodiction surface locks as the tranche "
                "gate_3a_retrodiction_claiming, whose own description "
                "is exactly its scored surface",
                "the live arm is carried only as the not_certified "
                "margin tier2_live_resolution_arm_unscored INSIDE the "
                "locked tranche",
            ],
            "proposed_gate_3_description": current,
            "reason_it_is_right": (
                "the ratified rule binds the description 'at lock "
                "time', and at lock time the object that locks is the "
                "TRANCHE. gate_3 itself has no gated cells and stays "
                "`locked: false`, so its headline is not yet a claim "
                "about any scored surface -- it is a statement of what "
                "gate_3 will eventually cover, including the live arm "
                "it genuinely describes. Narrowing it now would make "
                "gate_3's headline NARROWER than its eventual scope "
                "and would have to be widened again at the live-arm "
                "lock."
            ),
            "consequence_D8_sequencing": (
                "none. gate_3.description does not move, so v1's "
                "`arm_scope.gate_3_text_verbatim` pin still resolves "
                "and no rebuild is forced."
            ),
            "cost": (
                "gate_3's headline continues to name an arm nothing "
                "scores, for as long as the live arm stays unlocked"
            ),
        },
        "what_v2_did": (
            "v2 implemented cure B -- 'gate_3's own headline stays with "
            "the live-resolution arm it actually describes and remains "
            "unlocked' -- while labelling it 'cure (i)', which is "
            "referee A's. There is no gate_3b_live_resolution sibling "
            "in v2's fragment and gate_3.description is byte-identical "
            "to gates.yaml. The independent verifier caught the "
            "mislabel; it is corrected here by refusing to choose "
            "rather than by choosing again."
        ),
        "what_both_cures_share": {
            "narrowed_tranche_description": NARROWED_TRANCHE_DESCRIPTION,
            "required_margin": {
                "margin": "tier2_live_resolution_arm_unscored",
                "detail": (
                    "The tier-2 LIVE-RESOLUTION arm of gate_3 is NOT "
                    "certified and is scored by NO cell here. It binds "
                    "future annual SSA publications and its clock "
                    "cannot start until thresholds lock. Both source "
                    "documents close scoring surface 3 with the same "
                    "sentence: docs/scoring-and-resolution.md -- "
                    "'Retrodictive scores are necessary but not "
                    "sufficient ... so they complement, and NEVER "
                    "SUBSTITUTE FOR, the live annual cells in surface "
                    "1'; paper/paper.qmd -- 'backtests complement "
                    "rather than substitute for live resolution'. A "
                    "PASS here may never be reported as evidence about "
                    "live resolution."
                ),
            },
            "note": (
                "the tranche description and the margin are IDENTICAL "
                "under both cures. The whole disagreement is about "
                "gate_3's own headline and whether a live-arm sibling "
                "is declared now or later."
            ),
        },
    }


# --------------------------------------------------------------------------
# The margin list. v2's fourteen are carried FROM v2's committed bytes
# so they cannot drift on a retype; three move because the verifier's
# findings move them, and three are new.
# --------------------------------------------------------------------------
MARGINS_UNCHANGED_FROM_V2 = (
    "tier2_live_resolution_arm_unscored",
    "scored_window_is_the_quietest_in_the_panel",
    "shock_window_2020_2022",
    "shock_partition_is_scored_side_only",
    "provisional_terminal_rows",
    "settlement_is_measured_only_at_printing_age_4_plus",
    "single_table_single_family",
    "level_cells",
    "carried_claiming_path",
    "the_TR_anchor_is_true_vintage",
    "no_replication",
)


def not_certified_margins(
    v2: dict, surface: dict, exposure: dict, partition: dict
) -> list[dict]:
    """v2's fourteen, three of them rewritten, plus three new ones."""
    carried = {row["margin"]: row for row in v2["not_certified"]}
    probe = exposure["out_of_panel_probe_set"]
    worst_loo = exposure["worst_leave_one_out_rule"]
    worst_loo_n = exposure["leave_one_out"][worst_loo][
        "n_passed_by_the_held_out_rule"
    ]
    margins = [
        dict(carried[name], carried_verbatim_from_v2=True)
        for name in MARGINS_UNCHANGED_FROM_V2
    ]
    margins.append(
        {
            "margin": "residual_null_rule_exposure",
            "new_in_v2": True,
            "rewritten_in_v3": True,
            "answers": (
                "independent verifier finding 1 -- v2's number for this "
                "margin measured the wrong thing"
            ),
            "detail": (
                "The panel minimum closes the hole for every rule IN "
                "the panel: all "
                f"{surface['n_panel_rules']} registered rules pass ZERO "
                "gated pairs, computed not asserted. It does NOT close "
                "the hole for a rule nobody registered, and no panel "
                "can. v2 published a leave-one-out number (12 of 88) "
                "under the words 'the honest residual exposure'; that "
                "quantity is the panel's exposure to its OWN MEMBERS, "
                "and an independent verifier measured a rule outside "
                "v2's panel -- a degree-2 trend on the last eight fit "
                "rows -- passing 23 of v2's 88, nearly double. v3 "
                "registers that rule and every other rule the verifier "
                "built, and then MEASURES THE RESIDUAL FROM OUTSIDE "
                "THE NEW PANEL: "
                f"{probe['n_probes']} unregistered probe rules against "
                f"the {surface['n_gated']} gated pairs, worst is "
                f"`{probe['worst_probe']}` at "
                f"{probe['worst_probe_n_passed']} pairs "
                f"({probe['worst_probe_share_of_the_gated_surface']:.1%} "
                "of the surface). Within-panel leave-one-out is "
                f"reported separately: worst is `{worst_loo}` at "
                f"{worst_loo_n}. THE RESIDUAL IS THE FIRST NUMBER. It "
                "is not zero and cannot be driven to zero; what the "
                "contract adds instead is an OPEN, VERSIONED panel "
                "with a published admission procedure, so the residual "
                "is a quantity the ceremony can act on rather than a "
                "hole nobody may name."
            ),
        }
    )
    margins.append(
        {
            "margin": "the_panel_was_assembled_with_the_answer_in_hand",
            "new_in_v2": True,
            "rewritten_in_v3": True,
            "answers": "the leakage class the widened panel inherits",
            "detail": (
                "Nine of v2's eleven rules were exhibited by referee B "
                "AFTER reading the resolution vintage, specifically "
                "because they passed v1's tolerances. v3 is worse on "
                "this axis, not better: 44 of its 55 rules come from "
                "an independent verifier who had also read the "
                "resolution vintage, and one of them -- `quad_last8` "
                "-- was selected precisely because it beat v2's "
                "tolerances. So the panel is not pre-registered in any "
                "sense; it is an after-the-fact hardening chosen with "
                "2014-2022 in hand, twice over. The DIRECTION is "
                "provable and is proved in "
                "null_rule_exposure.counterfactual_if_every_probe_were_"
                "admitted: a minimum over a larger set can only fall, "
                "so every admission TIGHTENS tolerances and SHRINKS "
                "the gated set, and no candidate can be flattered by "
                "it. But it must be logged as leakage rather than "
                "presented as a pre-registration this artifact does "
                "not have."
            ),
        }
    )
    margins.append(
        {
            "margin": "specification_leakage",
            "new_in_v2": False,
            "rewritten_in_v3": True,
            "answers": "A's D4, extended to the v3 panel",
            "detail": (
                "Cells, rules, T*, the shock partition, the "
                "provisional exclusions, THE NULL-RULE PANEL AND NOW "
                "ITS 44-RULE WIDENING were all chosen in 2026 with "
                "2014-2022 in hand; the settlement finding was "
                "DISCOVERED, not pre-registered. A PASS is conditional "
                "on the whole deviation log and may never be stated as "
                "an unconditional out-of-sample result."
            ),
        }
    )
    margins.append(
        {
            "margin": "the_gateable_surface_is_small_and_got_smaller",
            "new_in_v3": True,
            "answers": (
                "the honest consequence of answering verifier finding 1"
            ),
            "detail": (
                "Widening the panel from 11 rules to 55 cut the gated "
                f"surface from 88 pairs over 17 cells to "
                f"{surface['n_gated']} pairs over "
                f"{surface['n_cells_with_at_least_one_gated_horizon']} "
                "cells, and the sum of tolerances from 54.711 to "
                f"{surface['sum_of_tolerances']}. "
                f"{surface['n_cells_gated_at_every_horizon']} cell is "
                "gated at every one of its horizons. BOTH "
                "claim_average_age cells now gate at ZERO horizons: "
                "some registered rule reproduces the printed digit, or "
                "lands inside the publication-rounding floor, at every "
                "horizon of both. "
                f"{surface['demotion_census'][DEMOTION_EXACT]} of the "
                "108 pairs are demoted because a registered rule is "
                "EXACT there. This is what the arm actually supports "
                "once trivial rules are taken seriously, and the "
                "ceremony should read the small surface as the "
                "measurement it is rather than as a defect of v3: the "
                "88-pair surface was the same table with a weaker "
                "adversary."
            ),
        }
    )
    margins.append(
        {
            "margin": "the_panel_is_open_not_complete",
            "new_in_v3": True,
            "answers": "verifier finding 1, the part no panel can close",
            "detail": (
                "55 rules is not a completeness claim and the contract "
                "does not make one. The instrument's "
                "null_rule_admission_procedure states how a "
                "fifty-sixth enters, what it does to the surface "
                "(tightens, never loosens), and that admission is an "
                "amendment binding only later-registered runs. A PASS "
                "licenses 'beat every rule in panel_version 3 by a "
                "factor of 1/rho at every gated pair', and nothing "
                "wider."
            ),
        }
    )
    margins.append(
        {
            "margin": "leg_2_blocks_are_unequal",
            "new_in_v3": True,
            "answers": "verifier finding 2, the residue after the fix",
            "detail": (
                "The five leg-2 blocks have sizes (2, 2, 2, 2, 1), so "
                "the '4 of 5' allowance waives one rolling origin if "
                "the singleton block {2008} fails and two origins "
                "otherwise. Fixing the partition globally removed the "
                "ambiguity about WHICH blocks; it did not make them "
                "equal, because nine origins do not divide by five. "
                "The allowance is disclosed as an allowance."
            ),
        }
    )
    return margins


# --------------------------------------------------------------------------
# The draft fragment, emitted TWICE -- once per A8 cure. TEXT ONLY.
# --------------------------------------------------------------------------
def _yaml_block(text: str, indent: int) -> str:
    """Fold a prose string into a YAML block scalar at `indent` spaces."""
    pad = " " * indent
    words, lines, current = text.split(), [], ""
    for word in words:
        if current and len(current) + 1 + len(word) > 66:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return ">-\n" + "\n".join(f"{pad}{line}" for line in lines)


def draft_fragment(
    *,
    cure: str,
    surface: dict,
    exposure: dict,
    fence: dict,
    defect: dict,
    passrule: dict,
    partition: dict,
    margins: list,
    rolling: dict,
    cap_block: dict,
) -> str:
    """Emit the proposed gate_3 tranche block under one A8 cure."""
    if cure not in ("A", "B"):
        raise ValueError("cure must be 'A' or 'B'")
    by_cell: dict[str, dict[str, float]] = {}
    for pair, row in surface["gated"].items():
        key, horizon = pair.split("@")
        by_cell.setdefault(key, {})[horizon] = row["tolerance"]
    demoted_by_cell: dict[str, list[str]] = {}
    for pair, row in surface["reported_not_gated"].items():
        key, horizon = pair.split("@")
        demoted_by_cell.setdefault(key, []).append(
            f"{horizon} ({row['reason']})"
        )

    lines: list[str] = []
    add = lines.append
    add("  gate_3:")
    add("    name: forward projection")
    if cure == "A":
        add("    # CURE A (referee A). gate_3's OWN headline is narrowed")
        add("    # to the surface that actually locks, and the live-")
        add("    # resolution arm moves to a declared unlocked sibling.")
        add("    # A8 cure (i). NOT APPLIED -- gates.yaml is untouched.")
        add("    description: " + _yaml_block(CURE_A_GATE_3_DESCRIPTION, 6))
    else:
        add("    # CURE B (referee B). gate_3's headline is LEFT AS IT")
        add("    # IS: gate_3 has no gated cells at lock time, the")
        add("    # object that locks is the tranche, and gate_3's text")
        add("    # describes the live arm it will eventually cover.")
        add("    # NOT APPLIED -- gates.yaml is untouched.")
        add(
            "    description: "
            + _yaml_block(defect["current_description_verbatim"], 6)
        )
    add("    thresholds:")
    add("      locked: false")
    add("")
    add("    # ---- PROPOSAL ONLY. Not locked, not ratified, not scored.")
    add("    # gates.yaml is byte-identical to origin/master at this")
    add("    # commit. THIS IS ONE OF TWO ALTERNATIVE TEXTS: the other")
    add(
        "    # is cure "
        + ("B" if cure == "A" else "A")
        + ", and the ratifying round must choose."
    )
    add("    gate_3a_retrodiction_claiming:")
    add("      id: gate_3a_retrodiction_claiming")
    add("      status: draft_pending_ratifying_round")
    add("      locked: false")
    add("      kind: pseudo_vintage_backtest")
    add("      gates_yaml_untouched_by_this_draft: true")
    add("      a8_cure_applied_in_this_text: " + cure)
    add("      description: " + _yaml_block(NARROWED_TRANCHE_DESCRIPTION, 8))
    add("      floor_run: runs/gate3_retrodiction_floors_v3.json")
    add("      floor_run_sha256: <FILLED AT RATIFICATION -- the v3")
    add("        artifact digest is stated in the report footer and")
    add("        must be pasted here, never left as a placeholder>")
    add(
        "      superseded_floor_runs: "
        "[runs/gate3_retrodiction_floors_v1.json, "
        "runs/gate3_retrodiction_floors_v2.json]"
    )
    add(f"      superseded_v1_sha256: {V1_ARTIFACT_SHA256}")
    add(f"      superseded_v2_sha256: {V2_ARTIFACT_SHA256}")
    covers = (
        "the PSEUDO-VINTAGE retrodiction of the claiming-age "
        "distribution of retired-worker awards (SSA Annual Statistical "
        "Supplement Table 6.B5.1) ONLY: fit only on rows the 2014 "
        "Supplement printed and settled (entitlement years 1998-2012), "
        "project entitlement years 2014-2019, score against the 2023 "
        f"Supplement's settled rows. {surface['n_gated']} gated (cell, "
        "horizon) pairs over "
        f"{surface['n_cells_with_at_least_one_gated_horizon']} cells; "
        f"the remaining {surface['n_reported_not_gated']} pairs are "
        "REPORTED, NOT GATED, each with its reason."
    )
    add("      covers: " + _yaml_block(covers, 8))
    add("      holdout_basis:")
    for entry in (
        "PUBLICATION VINTAGE, not persons. The truth side is a "
        "100-percent MBR census (SSA: 'Master Beneficiary Record, 100 "
        "percent data (not a sample)'), so a person-disjoint "
        "half-split is unavailable IN PRINCIPLE and a bootstrap over "
        "published shares would invent a variance the source does not "
        "have.",
        "The held-out object is every row after T* = 2012. A candidate "
        "loads the FENCED reference defined in "
        "candidate_reference_fence and cannot read the resolution "
        "vintage at all.",
        "ONE vintage pair, ONE realized history, NO seeds. The "
        "tolerance basis is a single realization at the registered "
        "origin (n = 1). Any reading of a block count as gate_2's five "
        "person-disjoint seeds is a category error.",
    ):
        add("        - " + _yaml_block(entry, 10))
    add("      not_certified:")
    for margin in margins:
        add(f"        - margin: {margin['margin']}")
        add("          detail: " + _yaml_block(margin["detail"], 12))
    add("      protocol:")
    add("        vintage_boundary_year: 2014")
    add("        T_star: 2012")
    add("        T_star_leakage_class: true_vintage_artifact")
    add("        fit_window: [1998, 2012]")
    add(
        "        fit_source: "
        "data/external/ssa_claim_ages_2014supplement.json"
    )
    add(f"        fit_source_sha256: {_sha256_path(CLAIM_2014)}")
    add(
        "        resolution_source: "
        "data/external/ssa_claim_ages_2023supplement.json"
    )
    add(f"        resolution_source_sha256: {_sha256_path(CLAIM_2023)}")
    add("        scored_years: [2014, 2015, 2016, 2017, 2018, 2019]")
    add("        horizons: [2, 3, 4, 5, 6, 7]")
    add("        excluded_years: [2013, 2022]   # provisional terminal")
    add("        shock_years: [2020, 2021, 2022]   # gate_m6's window")
    add("        min_settlement_age_printings: 4")
    add("      instrument:")
    add("        chosen: skill_ratio_against_a_registered_null_panel")
    add(f"        rho: {DRAFT_RHO}")
    add("        rho_sensitivity: [0.5, 0.75, 0.9]")
    add(
        "        rho_is_a_policy_constant: "
        + _yaml_block(
            "rho is NOT chosen by this artifact. Three values are "
            "published with their full surfaces and both referees "
            "recommended 0.5; every headline count here is quoted at 0.75, "
            "which is v2's headline and is retained only so the two "
            "packages are comparable. THE RATIFYING ROUND MUST SET IT.",
            10,
        )
    )
    add("        basis: registered_origin_panel_minimum")
    add("        horizon_shape: as_measured")
    add("        rule: " + _yaml_block(TOLERANCE_LAW, 10))
    add("        rounding: " + _yaml_block(TIE_RULE, 10))
    add("        power_cap: " + _yaml_block(POWER_CAP_LAW, 10))
    add("        power_cap_factor: 0.3333333333333333")
    add("        power_cap_metric_origins: {abs_pp: 0, abs_years: 62}")
    add(
        "        rolling_origin_fallback_is_FORBIDDEN: "
        + _yaml_block(
            "referee A decision 3, required addition 2. No tolerance in "
            "this tranche may be derived from a rolling-origin statistic, "
            "not as a primary basis and not as a fallback when the "
            "registered-origin panel minimum is unavailable or "
            "inconvenient. If the registered-origin minimum does not "
            "exist at a pair, the pair is REPORTED, NOT GATED. The rolling "
            "origins enter leg 2 of the pass rule and nothing else.",
            10,
        )
    )
    add(
        "        authoritative: "
        + _yaml_block(
            "THE FORMULA, not the literals -- and the formula is now "
            "complete, which is what v2's was not. It fixes the panel "
            "(panel_version 3, enumerated below by name and formula), the "
            "6-dp deviation step, the exact-decimal ROUND_HALF_EVEN tie "
            "convention, the three strict/cap conditions and the power "
            "cap. The per-cell tables below are emitted from it and are "
            "re-derived from it by "
            "tests/test_gate3_retrodiction_floors_v3.py. What CANNOT recur "
            "is v1's cause -- a per-cell selection the text did not "
            "describe; what is now also fixed is the residue the "
            "independent verifier found in v2, where the text left one "
            "literal of 88 convention-dependent.",
            10,
        )
    )
    add(f"        panel_version: {PANEL_VERSION}")
    add(f"        n_registered_null_rules: {len(PANEL_V3)}")
    add(
        "        null_rule_admission_procedure: "
        + _yaml_block(ADMISSION_PROCEDURE, 10)
    )
    add("        null_rule_panel:")
    add("          # The panel IS the contract. Adding, removing or")
    add("          # reordering a rule is an amendment under the")
    add("          # admission procedure above and, under")
    add("          # no_self_rescue, binds only runs registered after")
    add("          # ratification.")
    for name in PANEL_V3:
        formula = NULL_RULE_PANEL_V3[name][1]
        add(f"          {json.dumps(name)}: {json.dumps(formula)}")
    add("        panel_minimum_is_both_selection_and_basis: true")
    add(
        "        publication_rounding_floor: "
        + _yaml_block(
            "0.05 for every gated cell (half of the 0.1 printed "
            "granularity). UNITS ARE PER CELL: percentage points of share "
            "for the claim_share cells, YEARS for claim_average_age. It is "
            "an ELIGIBILITY BOUND, not a floor a tolerance is raised to: a "
            "tolerance below max(F0, instrument A) demotes its pair to "
            "reported-not-gated, because the truth side cannot resolve the "
            "difference between the candidate and a null rule there.",
            10,
        )
    )
    add("      scoring:")
    add("        pass_rule: " + _yaml_block(PASS_RULE_V3, 10))
    add("        leg_2_block_law: " + _yaml_block(LEG2_BLOCK_LAW, 10))
    add("        conjunction_leg_1: every gated (cell, horizon) pair")
    add("        conjunction_leg_2: 4 of 5 blocks")
    add(f"        n_gated_pairs: {surface['n_gated']}")
    add(
        "        n_gated_cells: "
        f"{surface['n_cells_with_at_least_one_gated_horizon']}"
    )
    add("        registered_origin: 2012")
    add("        n_registered_origin_realizations: 1")
    add("        rolling_origins: [2004, 2012]")
    add(
        "        n_rolling_origins: "
        f"{passrule['counts']['n_rolling_origins']}"
    )
    add("        rolling_origin_blocks:")
    for seed in sorted(rolling["blocks"]):
        add(f"          {seed}: {rolling['blocks'][seed]}")
    add(f"        block_shape: \"{rolling['block_shape']}\"")
    add("        n_rolling_origin_blocks: 5")
    add("        admissible_origins_by_horizon:")
    for horizon in sorted(
        rolling["admissible_origins_by_horizon"],
        key=lambda h: int(h[1:]),
    ):
        add(
            f"          {horizon}: "
            f"{rolling['admissible_origins_by_horizon'][horizon]}"
        )
    add(
        "        why_no_seed_conjunction: "
        + _yaml_block(passrule["why_the_seed_leg_cannot_be_inherited"], 10)
    )
    add(
        "        leg_2_allowance_disclosed: "
        + _yaml_block(passrule["leg_2_allowance_disclosed"], 10)
    )
    add("      cells:")
    add("        # DRAFT per-cell x horizon tolerances. Units:")
    add("        # percentage points of share (0-100 scale), except")
    add("        # claim_average_age, which is YEARS. Emitted from the")
    add("        # formula above, never typed.")
    for key in sorted(by_cell):
        row = by_cell[key]
        inner = ", ".join(
            f"{h}: {row[h]}" for h in sorted(row, key=lambda h: int(h[1:]))
        )
        add(f"        {key + ':':<42}{{{inner}}}")
    add("      reported_not_gated:")
    add("        # NOT gated, with the reason. Published, never scored.")
    for key in sorted(demoted_by_cell):
        add(f"        {key}:")
        for entry in sorted(
            demoted_by_cell[key], key=lambda s: int(s.split()[0][1:])
        ):
            add(f"          - {entry}")
    add("      eligible_not_gated:")
    add("        # Draft-gate-eligible cells that gate at NO horizon.")
    for key in sorted(partition["eligible_not_gated"]):
        add(f"        - {key}")
    add("      report_only:")
    add("        # ALL 17 non-eligible registry cells, enumerated with")
    add("        # their blocking reasons. No glob patterns: referee A")
    add("        # measured that v1's covered_earnings.* matched zero")
    add("        # registry keys and di_stock_* missed")
    add("        # di_worker_termination_rate, and v2's six-entry list")
    add("        # left ten cells with no contract text at all.")
    for key in partition["report_only_names"]:
        reasons = ", ".join(partition["report_only"][key]["blocking_reasons"])
        add(f"        - cell: {key}")
        add(f"          reasons: [{reasons}]")
    add("      candidate_reference_fence:")
    add("        law: " + _yaml_block(fence["law"], 10))
    add(
        "        fenced_reference_rows_sha256: "
        + fence["fenced_reference"]["rows_sha256"]
    )
    add("        admissible_years: [1998, 2012]")
    add("        deployed_module_passes_this_fence_today: false")
    add(
        "        required_module_change: "
        + _yaml_block(fence["required_module_change"], 10)
    )
    add(
        "        also_unreadable_at_run_time: "
        + _yaml_block(fence["also_unreadable_at_run_time"], 10)
    )
    add(
        "        proof_of_non_readability: "
        + _yaml_block(fence["proof_of_non_readability"], 10)
    )
    add("      deviation_log:")
    add(
        "        vintage_revision: "
        "floor_run_v2.referee_corrections.settlement"
    )
    add(
        "        specification_leakage: "
        "floor_run.not_certified[specification_leakage]"
    )
    add(
        "        panel_selection_leakage: "
        "floor_run.not_certified"
        "[the_panel_was_assembled_with_the_answer_in_hand]"
    )
    add(
        "        residual_null_rule_exposure: "
        "floor_run.null_rule_exposure.out_of_panel_probe_set"
    )
    add("      governance:")
    add(
        "        registration: "
        + _yaml_block(
            "Pre-registered on issue #42, exactly as every gate-1 and "
            "gate-2 candidate run. A gate-3 retrodiction candidate "
            "registers, BEFORE scoring: its spec; its claiming path "
            "declared as BEHAVIOURAL or CARRIED; the fenced reference "
            "digest it will load; its COLA / wage-index source, which MUST "
            "be the T*-vintage Trustees assumptions "
            "(data/external/ssa_tr_ultimate_assumptions_2014.json) and NOT "
            "realized post-T* COLAs; the panel_version its tolerances come "
            "from; and its simulation seeds. Outer runs are one-shot: a "
            "first pass must come from a fresh registration run. The run "
            "PUBLISHES REGARDLESS of verdict, with at most one disclosed "
            "re-execution.",
            10,
        )
    )
    add(
        "        fresh_run_artifact_schema: "
        + _yaml_block(
            "a registered gate-3 retrodiction run artifact carries "
            "protocol.publishes_regardless, the fenced reference digest it "
            "actually loaded, the panel_version its tolerances come from, "
            "the proof_of_non_readability described in "
            "candidate_reference_fence, the per-pair deviations at the "
            "registered origin AND at all nine rolling origins, and its "
            "verdict under both legs of the pass rule above.",
            10,
        )
    )
    add("        amendment_rules:")
    add("          inherits: gate_1")
    add(
        "          no_self_rescue: "
        + _yaml_block(passrule["no_self_rescue"], 12)
    )
    add(
        "          amendments_only_via: "
        + _yaml_block(
            "public proposal + adversarial referee round + independent "
            "verification + maintainer ratification by merge -- the same "
            "ceremony gate 1's amendments follow. Admitting a null rule to "
            "the panel is an amendment and increments panel_version.",
            12,
        )
    )
    add("          description_claims_exactly_the_scored_surface:")
    add("            rule: " + _yaml_block(defect["rule_text_verbatim"], 14))
    if cure == "A":
        add(
            "            satisfied_how: "
            + _yaml_block(
                "CURE A. gate_3's own description is narrowed to the "
                "retrodiction arm actually scored, and the live-resolution "
                "arm is declared as the unlocked sibling "
                "gate_3b_live_resolution below. The tranche's own "
                "description names exactly Table 6.B5.1's claiming-age "
                "distribution and entitlement years 2014-2019. Referee A: "
                "'(ii) alone leaves the headline broad', so the "
                "tier2_live_resolution_arm_unscored margin accompanies the "
                "narrowing rather than replacing it.",
                14,
            )
        )
    else:
        add(
            "            satisfied_how: "
            + _yaml_block(
                "CURE B. The object that locks is the TRANCHE, and its "
                "description names exactly Table 6.B5.1's claiming-age "
                "distribution and entitlement years 2014-2019. gate_3 "
                "itself has no gated cells at lock time and stays "
                "locked: false, so its broader headline is a statement of "
                "eventual scope rather than a claim about a scored "
                "surface. The tier2_live_resolution_arm_unscored margin "
                "carries the two source sentences that say backtests never "
                "substitute for live resolution. REFEREE A DISAGREES WITH "
                "THIS READING -- see the gate_3 description comment above "
                "and cure A.",
                14,
            )
        )
    add("      history:")
    for entry in (
        "floors v1 proposed 108 gated pairs under a two-rule baseline "
        "with a per-cell selection. Two independent referees returned "
        "NOT LOCK-READY without disputing a single number.",
        "floors v2 answered them: the baseline became the MINIMUM over "
        "an eleven-rule registered panel, 88 pairs, sum 54.711. An "
        "independent verifier recomputed every number from the raw "
        "printings, confirmed all three blocking findings CLOSED, and "
        "returned NOT VERIFIED as lock-ready on seven further "
        "findings.",
        "floors v3 answers those seven. The panel widened to 55 rules "
        "-- every rule the verifier built, quad_last8 included -- and "
        f"the gated surface fell to {surface['n_gated']} pairs over "
        f"{surface['n_cells_with_at_least_one_gated_horizon']} cells, "
        f"sum {surface['sum_of_tolerances']}. The residual is now "
        "measured from OUTSIDE the panel, the panel is open and "
        "versioned with a published admission procedure, leg 2's "
        "blocks are fixed by one global rule, the tie convention and "
        "the power cap are stated, all 17 non-eligible cells are "
        "enumerated, and A8's two referee cures are set out side by "
        "side for the ratifying round to choose between.",
    ):
        add("        - " + _yaml_block(entry, 10))
    if cure == "A":
        add("")
        add("    # ---- CURE A ONLY: the declared unlocked sibling ----")
        add("    gate_3b_live_resolution:")
        add("      id: gate_3b_live_resolution")
        add("      status: declared_unlocked_no_floor_no_scored_run")
        add("      locked: false")
        add("      kind: live_annual_resolution")
        add(
            "      description: "
            + _yaml_block(
                "Tier-2 near-term components resolve against administrative "
                "publications on named resolution rules. This arm has NO "
                "floor artifact, NO scored run and NO thresholds; its clock "
                "cannot start until it has its own lock ceremony. It is "
                "declared here so that the retrodiction lock does not "
                "silently carry a claim about it, following the "
                "gate_2 -> gate_2b / gate_2c precedent "
                "(gates.yaml amendment 2), where the unlocked sibling "
                "tranches were declared at the moment the parent headline "
                "was narrowed.",
                8,
            )
        )
        add("      thresholds:")
        add("        locked: false")
    return "\n".join(lines) + "\n"


def v1_answer_key_census(v1: dict, deviations: dict) -> dict:
    """Measure what v1 publishes, since v1 has no F2_panel_deviations.

    The fourth sitting found that the fence clause named a path v1 does
    not have.  v1 is not cleaner than v2/v3 for that reason -- it is
    leakier, by a different path -- so the clause states the measured
    census rather than a family resemblance.
    """
    series = {
        cell: entry["resolution_vintage_series"]
        for cell, entry in v1["reference_values"].items()
    }
    years = sorted({int(year) for s in series.values() for year in s})
    n_values = sum(len(s) for s in series.values())
    n_after = sum(
        1 for s in series.values() for year in s if int(year) > T_STAR
    )
    n_realized = 0
    n_reproduced = 0
    for cell, entry in deviations.items():
        for row in entry["by_horizon"].values():
            n_realized += 1
            stored = series.get(cell, {}).get(str(row["target_year"]))
            if stored is not None and abs(stored - row["realized"]) < 1e-12:
                n_reproduced += 1
    return {
        "v1_has_an_F2_panel_deviations_block": ("F2_panel_deviations" in v1),
        "path": "reference_values[cell].resolution_vintage_series",
        "n_cells": len(series),
        "n_values": n_values,
        "n_values_after_t_star": n_after,
        "year_span": [years[0], years[-1]],
        "n_realized_in_the_v3_panel": n_realized,
        "n_reproduced_exactly_by_v1": n_reproduced,
    }


def candidate_reference_fence(v2: dict, v1: dict, deviations: dict) -> dict:
    """v2's fence, re-executed, plus the verifier's two scope limits."""
    fenced = v2b.build_fenced_reference()
    module = v2b.deployed_module_fence_check()
    committed = v2["candidate_reference_fence"]
    census = v1_answer_key_census(v1, deviations)
    return {
        "law": v2b.FENCE_LAW,
        "answers": (
            "referee B blocking finding 1, re-executed at v3 rather "
            "than inherited on trust, plus the two scope limits the "
            "independent verifier added in its section 1.5"
        ),
        "fenced_reference": fenced,
        "rebuilt_fence_matches_v2": (
            fenced["rows_sha256"]
            == committed["fenced_reference"]["rows_sha256"]
        ),
        "deployed_module_fence_check": module,
        "v1_publishes_the_answer_key_by_another_path": census,
        "also_unreadable_at_run_time": (
            "VERIFIER SECTION 1.5, ITEM 1. The fence as v2 built it is "
            "a property of an OBJECT, not of a process: nothing makes "
            "ssa_claim_ages_2023supplement.json unreadable, and the "
            "committed floor artifacts are worse. v2 and v3 each "
            f"publish all {census['n_realized_in_the_v3_panel']} "
            "realized values at "
            "F2_panel_deviations[cell].by_horizon[h].realized. v1 has "
            "NO F2_panel_deviations block, and is leakier rather than "
            "cleaner: it publishes "
            "reference_values[cell].resolution_vintage_series, "
            f"{census['n_values']} values over {census['n_cells']} "
            f"cells spanning {census['year_span'][0]}-"
            f"{census['year_span'][1]}, of which "
            f"{census['n_values_after_t_star']} fall after T*, and "
            "those series reproduce "
            f"{census['n_reproduced_exactly_by_v1']} of the "
            f"{census['n_realized_in_the_v3_panel']} realized values "
            "exactly. A candidate process could therefore obtain the "
            "answer key from any of the three with one json.load on "
            "runs/. The registration clause names FOUR objects, not "
            "one, as unreadable from a candidate process: "
            "data/external/ssa_claim_ages_2023supplement.json, "
            "runs/gate3_retrodiction_floors_v1.json, "
            "runs/gate3_retrodiction_floors_v2.json and "
            "runs/gate3_retrodiction_floors_v3.json. The tolerances a "
            "candidate needs are the literals in the ratified "
            "gates.yaml block, which contain no realized value."
        ),
        "proof_of_non_readability": (
            "VERIFIER SECTION 1.5, ITEM 2. v2 required the run "
            "artifact to carry 'a proof that the resolution vintage "
            "was not readable from the candidate process' and left the "
            "form undefined, which is not a requirement. The form is: "
            "the candidate process runs with the four named paths "
            "absent from its filesystem view, and its run artifact "
            "records, for each of the four, the outcome of an "
            "open() attempt made INSIDE the scoring process "
            "(expected: FileNotFoundError), together with the sha256 "
            "of the fenced reference it did load and the "
            "panel_version its tolerances came from. An artifact that "
            "records a successful open, or omits the attempt, fails "
            "the fence and its run is void."
        ),
        "required_module_change": module["required_module_change"],
        "where_this_belongs_in_the_contract": committed[
            "where_this_belongs_in_the_contract"
        ],
        "still_open": (
            "src/populace_dynamics/claiming.py STILL FAILS THE FENCE, "
            "measured live above. This is a candidate-side module "
            "change, not a floors change, and it blocks any candidate "
            "run. v3 does not edit the module."
        ),
    }


def power_cap_block(
    deviations: dict,
    v2_deviations: dict,
    bounds: dict,
    surface: dict,
) -> dict:
    """What the cap is, and exactly what it demotes here and in v2."""

    def _count(devs, panel, rho):
        with_cap = gated_surface(devs, bounds, panel=panel, rho=rho, cap=True)
        without = gated_surface(devs, bounds, panel=panel, rho=rho, cap=False)
        demoted = sorted(set(without["gated"]) - set(with_cap["gated"]))
        return with_cap, without, demoted

    _, _, v3_demoted = _count(deviations, set(PANEL_V3), DRAFT_RHO)
    _, v2_no_cap, v2_demoted = _count(
        v2_deviations, set(v2b.NULL_RULE_PANEL), DRAFT_RHO
    )
    _, v1_no_cap, v1_demoted = _count(
        v2_deviations,
        {"persistence", "linear_trend"},
        DRAFT_RHO,
    )
    bands = []
    for pair, row in surface["gated"].items():
        key = pair.split("@")[0]
        unit = deviations[key]["metric"]
        base = row["realized"] - METRIC_ORIGINS[unit]
        bands.append(
            {
                "pair": pair,
                "tolerance": row["tolerance"],
                "realized": row["realized"],
                "unit": unit,
                "band_relative_to_the_scale_origin": (
                    round(row["tolerance"] / base, 6) if base else None
                ),
                "power_cap": row["power_cap"],
            }
        )
    bands.sort(
        key=lambda row: row["band_relative_to_the_scale_origin"] or 0.0,
        reverse=True,
    )
    return {
        "law": POWER_CAP_LAW,
        "answers": (
            "referee A section 5.6, left open by v2 and re-raised as "
            "independent verifier finding 5"
        ),
        "locked_gate_precedents": {
            "gate_2": "tolerance <= T_max = ln(1.5)",
            "gate_2b": "tolerance <= T_max = ln(1.5)",
            "gate_2c": "tolerance <= T_max = ln(1.5)",
            "gate_m4": "T_max = ln(1.5)",
            "gate_m6": (
                "metric_caps per metric: log_ratio and abs_gap_log at "
                "0.4054651081081644 = ln(1.5); abs_gap_corr at 0.15, "
                "derived as about twice gate_1's "
                "autocorr_log_10yr_tolerance of 0.07 -- the precedent "
                "for deriving a cap when a log cap has no meaning on "
                "the metric"
            ),
        },
        "factor": CAP_FACTOR,
        "factor_derivation": (
            "|ln(pred/realized)| <= ln(1.5) is pred/realized in "
            "[2/3, 3/2]. The widest absolute band entirely inside that "
            "ratio band is |pred - realized| <= (1 - 1/1.5) * realized "
            "= realized/3, because the low side binds first: an "
            "absolute band of realized/2 would admit pred = "
            "realized/2, a 2x error."
        ),
        "metric_origins": METRIC_ORIGINS,
        "why_62_for_abs_years": (
            "a ratio cap on a mean claiming AGE is meaningless -- the "
            "scale has no true zero and realized/3 would be about 21 "
            "years, a cap that caps nothing. 62 is the statutory "
            "earliest entitlement age and the support floor of this "
            "very table, whose first category is age62, so "
            "realized - 62 is the quantity with a true zero: it is "
            "zero when every award is claimed at the earliest possible "
            "age."
        ),
        "demote_not_clip": (
            "gate_2, gate_2b, gate_2c and gate_m4 DEMOTE a cell whose "
            "tolerance exceeds T_max; gate_m6 CLIPS the tolerance to "
            "the cap. v3 demotes. Clipping is rejected because this "
            "arm's tolerance is a SKILL RATIO: a clipped tolerance "
            "would no longer equal rho * F2_panel_min, so the "
            "published number would stop meaning 'beat the null panel "
            "by 1/rho' and the instrument's one interpretive claim "
            "would need a second rule."
        ),
        "n_demoted_on_the_v3_surface": len(v3_demoted),
        "demoted_on_the_v3_surface": v3_demoted,
        "n_demoted_if_applied_to_the_v2_surface": len(v2_demoted),
        "demoted_if_applied_to_the_v2_surface": v2_demoted,
        "v2_surface_size_without_the_cap": v2_no_cap["n_gated"],
        "n_demoted_if_applied_to_the_v1_panel_surface": len(v1_demoted),
        "v1_panel_surface_size_without_the_cap": v1_no_cap["n_gated"],
        "reading_the_zero": (
            "the cap demotes NOTHING on the v3 surface, and that is a "
            "measurement rather than a token: the same cap demotes "
            f"{len(v2_demoted)} pair of v2's committed 88 "
            "(claim_share.age70plus|male@h7, tolerance 1.725 against a "
            "cap of 1.700 on a realized share of 5.100 -- the 33.8 "
            "per cent band the verifier flagged as wider than the 29 "
            "per cent pair referee A flagged in v1) and "
            f"{len(v1_demoted)} of the "
            f"{v1_no_cap['n_gated']} the v1 two-rule panel would gate "
            "at the same rho. Widening the panel tightened tolerances "
            "so far that the power cap stopped binding; the cap "
            "remains in the contract because a future panel_version, a "
            "future rho or a future cell can put a pair back over it, "
            "and because every locked gate has one."
        ),
        "widest_relative_bands": bands[:8],
        "median_relative_band": round(
            float(
                np.median(
                    [
                        row["band_relative_to_the_scale_origin"]
                        for row in bands
                        if row["band_relative_to_the_scale_origin"] is not None
                    ]
                )
            ),
            6,
        ),
    }


VERIFIER_FINDINGS = {
    "1_residual_exposure_understated_2x": {
        "verdict_in_the_verifier_report": (
            "v2 published '12 of 88 is the honest residual exposure'; "
            "12 is leave-one-out WITHIN the panel. An unregistered "
            "quad_last8 passes 23 of 88 and clears two cells at every "
            "gated horizon."
        ),
        "closed_by": [
            "null_rule_panel (11 -> 55 registered rules, every rule "
            "the verifier built, quad_last8 by name)",
            "instrument.null_rule_admission_procedure (the panel is "
            "OPEN and VERSIONED, with the admission criterion, the "
            "procedure, and the proved direction of its effect)",
            "null_rule_exposure.out_of_panel_probe_set (35 NEW "
            "unregistered rules, measured against the v3 surface)",
            "null_rule_exposure.counterfactual_if_every_probe_were_"
            "admitted (the exact surface admitting all 35 would give)",
            "gated_surface_recommended (the honest, smaller count)",
            "not_certified[residual_null_rule_exposure] (relabelled) "
            "and not_certified[the_panel_is_open_not_complete]",
        ],
    },
    "2_leg_2_blocks_ambiguous": {
        "verdict_in_the_verifier_report": (
            "'the five stride-5 blocks' is ambiguous between the nine "
            "rolling origins and each pair's eight admissible ones; "
            "the readings differ on 108 of 108 pairs, and under the "
            "per-pair reading four of five h2 blocks score only "
            "targets the fence lets the candidate read."
        ),
        "closed_by": [
            "rolling_origin_provenance.block_law and "
            "scoring.leg_2_block_law (ONE global stride-5 partition of "
            "2004-2012, independent of cell and horizon)",
            "rolling_origin_provenance.admissible_origins_by_horizon "
            "(the exact origin list per horizon, printed)",
            "rolling_origin_provenance.block_reach_under_the_fence "
            "(no block is free: each carries a post-T* target)",
            "not_certified[leg_2_blocks_are_unequal]",
        ],
    },
    "3_report_contradicts_artifact": {
        "verdict_in_the_verifier_report": (
            "v2's report printed a three-element origin-count "
            "list where the artifact carried a single-element "
            "one, and a 252/36/36 block census attributed to referee "
            "B, who wrote 310/210/70/40 about a different index set."
        ),
        "closed_by": [
            "report_counts (every count the report may state, emitted "
            "from a dotted artifact path)",
            "report_counts.forbidden_strings (the stale v1-shaped "
            "counts: the suite asserts that each of them occurs "
            "exactly once in the whole serialised artifact -- the "
            "occurrence inside the list itself -- and NOT that they "
            "are absent from it, which is the weaker ban that "
            "deleting the list would satisfy)",
            "report_counts.misattribution_corrected",
            "report_counts.self_description_law and "
            "test_every_self_referential_claim_is_registered_and_true "
            "(Finding 3's standard turned on these bytes: every "
            "string leaf matching the fixed self-reference regex must "
            "be one of the fourteen registered claims, and each "
            "registered claim carries its own predicate over the "
            "serialised bytes)",
        ],
    },
    "4_report_only_regression": {
        "verdict_in_the_verifier_report": (
            "v1's broken globs left 5 of 17 non-eligible cells with no "
            "contract text; v2's six-entry enumeration left 10."
        ),
        "closed_by": [
            "cell_partition (all 17 enumerated with blocking reasons; "
            "gated + eligible_not_gated + report_only == 35)",
            "the fragment's report_only block, 17 entries with reasons",
        ],
    },
    "5_no_tolerance_cap": {
        "verdict_in_the_verifier_report": (
            "referee A section 5.6 still open; v2's widest relative "
            "band is 33.8 per cent, wider than the 29 per cent pair A "
            "flagged in v1."
        ),
        "closed_by": [
            "power_cap (ln(1.5) transcribed per metric, with the "
            "derivation and the locked-gate precedents)",
            "the tolerance law's third condition and the "
            "tolerance_exceeds_the_power_cap demotion reason",
            "power_cap.n_demoted_if_applied_to_the_v2_surface",
        ],
    },
    "6_rounding_tie_dependence": {
        "verdict_in_the_verifier_report": (
            "three exact 3-dp ties in exact rationals; half-to-even "
            "gives 0.202 against the committed 0.203 on "
            "claim_share.age63|male@h5, and the rule text fixes no tie "
            "convention."
        ),
        "closed_by": [
            "TIE_RULE, carried into instrument.rounding",
            "tolerance_from() -- exact Decimal arithmetic, "
            "ROUND_HALF_EVEN, no binary float in the tie path",
            "tie_rule_fixture (all three of the verifier's ties, "
            "resolved and pinned)",
        ],
    },
    "7_A8_two_referee_cures_disagree": {
        "verdict_in_the_verifier_report": (
            "v2 implemented referee B's cure and presented it as "
            "referee A's. Both are defensible; they are not the same "
            "cure."
        ),
        "closed_by": [
            "description_defect_A8 (both cures, each in its referee's "
            "words, with consequences and costs)",
            "draft_gates_yaml_fragment.text_cure_A and .text_cure_B "
            "(two complete alternative fragment texts)",
            "description_defect_A8.THE_DECISION_THE_RATIFYING_ROUND_"
            "MUST_TAKE",
        ],
        "v3_chooses": "NEITHER, deliberately",
    },
}


def build() -> dict:
    for path, expected, label in (
        (V1_ARTIFACT, V1_ARTIFACT_SHA256, "v1 artifact"),
        (V2_ARTIFACT, V2_ARTIFACT_SHA256, "v2 artifact"),
    ):
        if _sha256_path(path) != expected:
            raise ValueError(
                f"{label} digest moved: v3 re-floors the package that "
                "was refereed and verified, or it re-floors nothing"
            )
    v1 = json.loads(V1_ARTIFACT.read_text())
    v2 = json.loads(V2_ARTIFACT.read_text())
    registry = v1b.cell_registry()
    cells = _gated_cells()
    fit_series = v1b.claiming_series(CLAIM_2014)
    resolution_series = v1b.claiming_series(CLAIM_2023)

    bounds = v2b._lower_bounds(v1, cells)
    deviations = panel_deviations(
        cells, fit_series, resolution_series, registry, NULL_RULE_PANEL_V3
    )
    probe_dev = panel_deviations(
        cells,
        fit_series,
        resolution_series,
        registry,
        RESIDUAL_PROBE_SET_V3,
    )
    combined_dev = panel_deviations(
        cells,
        fit_series,
        resolution_series,
        registry,
        {**NULL_RULE_PANEL_V3, **RESIDUAL_PROBE_SET_V3},
    )
    v2_dev = panel_deviations(
        cells,
        fit_series,
        resolution_series,
        registry,
        v2b.NULL_RULE_PANEL,
    )

    surfaces = {
        name: {
            str(rho): gated_surface(deviations, bounds, panel=panel, rho=rho)
            for rho in RHO_SENSITIVITY
        }
        for name, panel in PANEL_DEFINITIONS.items()
    }
    surfaces["panel_v3_plus_probe_set"] = {
        str(rho): gated_surface(
            combined_dev,
            bounds,
            panel=set(PANEL_V3) | set(RESIDUAL_PROBE_SET_V3),
            rho=rho,
        )
        for rho in RHO_SENSITIVITY
    }
    recommended = surfaces[BINDING_PANEL][str(DRAFT_RHO)]
    exposure = null_rule_exposure(
        deviations,
        probe_dev,
        combined_dev,
        recommended,
        bounds,
        panel=PANEL_V3,
    )
    rolling = rolling_origin_provenance(
        cells, fit_series, resolution_series, registry, panel=PANEL_V3
    )
    passrule = pass_rule_draft(recommended, rolling)
    partition = cell_partition(registry, recommended)
    fence = candidate_reference_fence(v2, v1, deviations)
    cap_block = power_cap_block(deviations, v2_dev, bounds, recommended)
    defect = description_defect((REPO / "gates.yaml").read_text())
    margins = not_certified_margins(v2, recommended, exposure, partition)

    artifact = {
        "schema_version": SCHEMA_VERSION,
        "run": RUN,
        "status": (
            "PRE-LOCK EVIDENCE, THIRD PASS. NOT A GATE RUN, NOT A "
            "LOCK, NOT A CANDIDATE SCORE. gates.yaml is byte-identical "
            "to origin/master and carries gate_3 locked: false with no "
            "thresholds. v1 and v2 are byte-identical and read-only."
        ),
        "supersedes": {
            "v1": {
                "artifact": str(V1_ARTIFACT.relative_to(REPO)),
                "sha256": V1_ARTIFACT_SHA256,
            },
            "v2": {
                "artifact": str(V2_ARTIFACT.relative_to(REPO)),
                "sha256": V2_ARTIFACT_SHA256,
            },
            "relationship": (
                "v1 and v2 are READ, never rewritten. Their files, "
                "their builders and their 31- and 41-test suites are "
                "byte-identical on this branch and still pass. v3 "
                "answers the INDEPENDENT VERIFIER's seven findings on "
                "v2; it disputes none of v2's arithmetic, which the "
                "verifier reproduced exactly from the raw printings."
            ),
            "referee_verdicts_on_v1": {
                "lens_A_protocol_and_record": "NOT LOCK-READY",
                "lens_B_numbers_and_statistics": "NOT LOCK-READY",
            },
            "verifier_verdict_on_v2": {
                "verdict": "NOT VERIFIED as lock-ready",
                "blocking_referee_findings": "all three VERIFIED CLOSED",
                "arithmetic_disputed": False,
                "report_sha256": VERIFIER_REPORT_SHA256,
                "report_bytes": VERIFIER_REPORT_BYTES,
                "new_findings": 7,
            },
        },
        "answers_the_verifier": VERIFIER_FINDINGS,
        "protocol": {
            "T_star": T_STAR,
            "fit_window": [FIT_FIRST_YEAR, T_STAR],
            "gated_horizons": list(GATED_HORIZONS),
            "gated_target_years": [T_STAR + h for h in GATED_HORIZONS],
            "rolling_origins": [ROLLING_ORIGIN_FIRST, T_STAR],
            "excluded_target_years": list(EXCLUDED_TARGET_YEARS),
            "rho": DRAFT_RHO,
            "rho_sensitivity": list(RHO_SENSITIVITY),
            "rho_is_not_chosen_here": (
                "rho is a POLICY CONSTANT. Three values are published "
                "with their full surfaces; both referees recommended "
                "0.5; every headline count is quoted at 0.75 so this "
                "package is comparable with v2's. The ratifying round "
                "must set it."
            ),
            "k": DRAFT_K,
            "ddof": 1,
            "deviation_rounding": DEVIATION_ROUNDING,
            "tolerance_rounding": DRAFT_ROUNDING,
            "tie_rule": TIE_RULE,
            "min_settlement_age_printings": (v2b.MIN_SETTLEMENT_AGE_PRINTINGS),
            "shock_years": list(v2b.SHOCK_YEARS_V2),
        },
        "tie_rule_fixture": {
            "why": (
                "the three exact 3-dp half-way ties the independent "
                "verifier isolated in exact rational arithmetic, "
                "resolved under the stated convention. They are pinned "
                "here as a FIXTURE, independent of whether those pairs "
                "gate under the v3 panel, so the convention is testable "
                "even when the surface moves."
            ),
            "ties": [
                {
                    "pair_in_v2": pair,
                    "exact_deviation": deviation,
                    "exact_rho_times_deviation": exact,
                    "v3_tolerance_under_ROUND_HALF_EVEN": (
                        tolerance_from(deviation, DRAFT_RHO)
                    ),
                    "expected": expected,
                    "matches": tolerance_from(deviation, DRAFT_RHO)
                    == expected,
                    "v2_committed": (
                        v2["gated_surface_recommended"]["gated"]
                        .get(pair, {})
                        .get("tolerance")
                    ),
                }
                for pair, deviation, expected, exact in VERIFIER_TIES
            ],
        },
        "null_rule_panel": {
            "panel_version": PANEL_VERSION,
            "n_rules": len(PANEL_V3),
            "law": (
                "A rule is INFORMATION-NULL iff it reads only rows of "
                "the fit source at or before the origin. Every rule "
                "below satisfies that by construction: each receives "
                "only (fit_years, values) truncated at the origin and "
                "the target year, and cannot see the resolution "
                "vintage at all."
            ),
            "admission_procedure": ADMISSION_PROCEDURE,
            "provenance_counts": {
                source: sum(
                    1
                    for entry in NULL_RULE_PANEL_V3.values()
                    if entry[2].startswith(source)
                )
                for source in (V1_SOURCE, V2_SOURCE, VS_SOURCE, VP_SOURCE)
            },
            "verifier_rule_count_discrepancy": (
                "the independent verifier's report says it built 45 "
                "rules; its scratch program work/verify_residual.py "
                "defines 41 distinct rule names. All 41 are registered "
                "here. Three further classes the report's PROSE names "
                "but its script omits -- medians over 2 and 7 rows and "
                "a cubic on the last 8 -- are registered too, so the "
                "panel covers every class the verifier described, not "
                "only every rule it ran. mean_last3 is in the prose "
                "class and was already a v2 member, so it is not "
                "double-registered. 11 + 41 + 3 = 55."
            ),
            "rules": {
                name: {"formula": entry[1], "source": entry[2]}
                for name, entry in NULL_RULE_PANEL_V3.items()
            },
            "panel_digest": _sha256_obj(
                {name: entry[1] for name, entry in NULL_RULE_PANEL_V3.items()}
            ),
        },
        "measurement_lower_bounds": bounds,
        "F2_panel_deviations": deviations,
        "probe_deviations": probe_dev,
        "gated_surface_recommended": recommended,
        "gated_surface_sensitivity": {
            name: {
                rho: {
                    "n_gated": surface["n_gated"],
                    "n_reported_not_gated": surface["n_reported_not_gated"],
                    "n_cells": surface[
                        "n_cells_with_at_least_one_gated_horizon"
                    ],
                    "n_cells_gated_at_every_horizon": surface[
                        "n_cells_gated_at_every_horizon"
                    ],
                    "sum_of_tolerances": surface["sum_of_tolerances"],
                    "demotion_census": surface["demotion_census"],
                }
                for rho, surface in by_rho.items()
            }
            for name, by_rho in surfaces.items()
        },
        "null_rule_exposure": exposure,
        "power_cap": cap_block,
        "pass_rule_draft": passrule,
        "cell_partition": partition,
        "candidate_reference_fence": fence,
        "description_defect_A8": defect,
        "rolling_origin_provenance": rolling,
        "not_certified": margins,
        "roll_up": {
            "n_cells_considered": len(cells),
            "n_pairs_considered": recommended["n_pairs_considered"],
            "n_gated_v1": 108,
            "n_gated_v2": 88,
            "n_gated_v3": recommended["n_gated"],
            "sum_of_tolerances_v1": 184.052,
            "sum_of_tolerances_v2": 54.711,
            "sum_of_tolerances_v3": recommended["sum_of_tolerances"],
            "n_panel_rules_v1": 2,
            "n_panel_rules_v2": 11,
            "n_panel_rules_v3": len(PANEL_V3),
            "registered_null_rules_passing_a_gated_pair": sum(
                exposure["in_panel_pass_counts"].values()
            ),
            "worst_out_of_panel_probe": exposure["out_of_panel_probe_set"][
                "worst_probe"
            ],
            "worst_out_of_panel_probe_n_passed": exposure[
                "out_of_panel_probe_set"
            ]["worst_probe_n_passed"],
            "worst_leave_one_out_exposure": exposure["leave_one_out"][
                exposure["worst_leave_one_out_rule"]
            ]["n_passed_by_the_held_out_rule"],
            "n_power_cap_demotions": cap_block["n_demoted_on_the_v3_surface"],
            "cell_partition_is_exact": partition["partition_is_exact"],
            "deployed_module_passes_the_fence": False,
            "a8_cure_chosen": "NEITHER -- the ratifying round decides",
            "gates_yaml_untouched_by_this_draft": True,
            "locked": False,
        },
        "revision_pins": {
            "v1_artifact_sha256": V1_ARTIFACT_SHA256,
            "v1_builder_sha256": V1_BUILDER_SHA256,
            "v2_artifact_sha256": V2_ARTIFACT_SHA256,
            "v2_builder_sha256": V2_BUILDER_SHA256,
            "verifier_report_sha256": VERIFIER_REPORT_SHA256,
            "verifier_report_bytes": VERIFIER_REPORT_BYTES,
            "claim_ages_2014_sha256": _sha256_path(CLAIM_2014),
            "claim_ages_2023_sha256": _sha256_path(CLAIM_2023),
            "claiming_module_sha256": _sha256_path(
                REPO / "src" / "populace_dynamics" / "claiming.py"
            ),
            "gates_yaml_sha256": _sha256_path(REPO / "gates.yaml"),
        },
        "draft_gates_yaml_fragment": {
            "status": (
                "PROPOSAL ONLY, IN TWO ALTERNATIVE FORMS. Neither "
                "string is written to gates.yaml by this or any "
                "script. gates.yaml is byte-identical to "
                "origin/master."
            ),
            "why_two": (
                "referee A and referee B proposed DIFFERENT cures for "
                "A8 and v2 implemented B's while labelling it A's. v3 "
                "emits both complete texts and chooses neither; the "
                "ratifying round must pick one, and picking is not "
                "optional, because an unnarrowed headline over a "
                "narrow scored surface is a lock defect under the "
                "ratified rule."
            ),
            "generated_from": "gated_surface_recommended",
            "text_cure_A": None,
            "text_cure_B": None,
        },
        "reproducibility": {
            "no_wall_clock": True,
            "no_git_derived_value": (
                "no git-derived value appears in this artifact; the "
                "commit is in the .env.json sidecar, excluded from the "
                "byte comparison"
            ),
            "rebuild_is_byte_identical": (
                "tests/test_gate3_retrodiction_floors_v3.py rebuilds "
                "via build() and compares the full text"
            ),
            "environment": "runs/gate3_retrodiction_floors_v3.env.json",
            "inputs": "runs/gate3_retrodiction_floors_v3.inputs.json",
        },
    }
    artifact["report_counts"] = report_counts(artifact)
    for cure in ("A", "B"):
        artifact["draft_gates_yaml_fragment"][f"text_cure_{cure}"] = (
            draft_fragment(
                cure=cure,
                surface=recommended,
                exposure=exposure,
                fence=fence,
                defect=defect,
                passrule=passrule,
                partition=partition,
                margins=margins,
                rolling=rolling,
                cap_block=cap_block,
            )
        )
    return artifact


SOURCE_INPUTS = (
    (
        CLAIM_2014,
        "https://www.ssa.gov/policy/docs/statcomps/supplement/2014/6b.html",
    ),
    (
        CLAIM_2023,
        "https://www.ssa.gov/policy/docs/statcomps/supplement/2023/6b.html",
    ),
    (V1_ARTIFACT, "in-repository committed evidence artifact (v1, read-only)"),
    (V1_BUILDER, "in-repository committed builder (v1, read-only)"),
    (V2_ARTIFACT, "in-repository committed evidence artifact (v2, read-only)"),
    (V2_BUILDER, "in-repository committed builder (v2, read-only)"),
    (
        REPO / "src" / "populace_dynamics" / "claiming.py",
        "in-repository module under the B1 fence check",
    ),
    (REPO / "gates.yaml", "in-repository ratified contract (read-only)"),
)


def environment_block() -> dict:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:  # pragma: no cover - provenance best effort
        commit = "unknown"
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "repo_commit": commit,
        "note": (
            "This sidecar is EXCLUDED from the byte comparison. Nothing "
            "here is an input to any number in the artifact."
        ),
    }


def main() -> None:
    artifact = build()
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n")
    INPUT_SIDECAR.write_text(
        json.dumps(
            {
                "artifact": ARTIFACT.name,
                "status": "SOURCE_INPUT_DIGESTS",
                "source_inputs": [
                    {
                        "path": str(path.relative_to(REPO)),
                        "sha256": _sha256_path(path),
                        "bytes": path.stat().st_size,
                        "official_url": url,
                    }
                    for path, url in SOURCE_INPUTS
                ],
            },
            indent=2,
        )
        + "\n"
    )
    ENV_SIDECAR.write_text(
        json.dumps(
            {
                "artifact": ARTIFACT.name,
                "status": "MEASUREMENT_ENVIRONMENT",
                "environment": environment_block(),
            },
            indent=2,
        )
        + "\n"
    )
    print(f"wrote {ARTIFACT}")
    for key, value in artifact["roll_up"].items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
