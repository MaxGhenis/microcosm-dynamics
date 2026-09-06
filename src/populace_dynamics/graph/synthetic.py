"""Small hand-specified engineering inputs, independent of generated draws."""

from pathlib import Path

from .model import json_bytes


def write_synthetic_inputs(directory):
    """Write synthetic sources to an explicit directory; preserve edits."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    training = [
        {
            "person_id": 1001 + i,
            "event_year": 2013,
            "required_interview_year": 2013,
            "age_band": "0+",
            "sex": "female" if i < 4 else "male",
            "start_weight": 1.0,
            "exposure": 1.0,
            "death": float(i % 4 == 0),
        }
        for i in range(8)
    ]
    training.extend(
        [
            {**training[0], "person_id": 1009, "event_year": 2015},
            {
                **training[0],
                "person_id": 1010,
                "required_interview_year": 2015,
            },
        ]
    )
    rates = [
        {
            "lower_age": 0,
            "upper_age": 120,
            "age_band": "0+",
            "sex": sex,
            "central_rate": rate,
        }
        for sex, rate in (("female", 0.005), ("male", 0.006))
    ]
    initial = [
        {
            "person_id": 100 + i,
            "age": 30 + 2 * i,
            "sex": "female" if i % 2 == 0 else "male",
            "weight": float(1 + i % 3),
        }
        for i in range(20)
    ]
    holdout = {
        "scope": "synthetic_engineering",
        "fixture_max_abs_death_rate_gap": 0.25,
        "outcomes": [
            {
                "person_id": row["person_id"],
                "year": 2015,
                "age": row["age"] + 1,
                "death": int(i % 5 == 0),
            }
            for i, row in enumerate(initial)
        ],
    }
    result = {}
    for name, value in (
        ("training", training),
        ("rates", rates),
        ("initial", initial),
        ("holdout", holdout),
    ):
        path = directory / f"{name}.json"
        if not path.exists():
            path.write_bytes(json_bytes(value))
        result[name] = path
    return result


def synthetic_earnings_path(
    *,
    price_basis="nominal",
    sign_domain="nonnegative",
    unit="XTS",
    calendar="calendar_year",
    boundary_year=2014,
    count=20,
):
    """Build a hand-specified earnings path for the synthetic population.

    Three observed periods and one supplied next-period value per person.
    ``XTS`` is the reserved testing currency code; the graph never reads
    any meaning into the token. The path deliberately holds a known zero,
    an explicit unknown, and a period that is simply absent, so that the
    three states can be told apart downstream. Under a ``signed`` domain
    one person also holds a negative period.
    """
    from .earnings import EarningsPathArtifact

    rows = []
    for i in range(count):
        person = 100 + i
        rows.append(
            (person, boundary_year - 2, "observed", "known", 30000.0 + 500 * i)
        )
        if i == 3:
            rows.append(
                (person, boundary_year - 1, "observed", "unknown", None)
            )
        elif i == 7:
            pass  # Absent, which is not the same as unknown or as zero.
        elif i == 1:
            rows.append((person, boundary_year - 1, "observed", "known", 0.0))
        elif i == 9 and sign_domain == "signed":
            rows.append(
                (person, boundary_year - 1, "observed", "known", -2500.0)
            )
        else:
            rows.append(
                (
                    person,
                    boundary_year - 1,
                    "observed",
                    "known",
                    31000.0 + 500 * i,
                )
            )
        rows.append(
            (
                person,
                boundary_year,
                "observed",
                "known",
                0.0 if i == 5 else 32000.0 + 500 * i,
            )
        )
        rows.append(
            (person, boundary_year + 1, "scenario", "known", 33000.0 + 500 * i)
        )
    return EarningsPathArtifact(
        source="synthetic_engineering",
        unit=unit,
        price_basis=price_basis,
        calendar=calendar,
        sign_domain=sign_domain,
        rows=tuple(rows),
    )


def write_synthetic_earnings(directory, *, name="earnings", **kwargs):
    """Write one earnings path source; an existing file is preserved."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    if not path.exists():
        path.write_bytes(synthetic_earnings_path(**kwargs).to_bytes())
    return path
