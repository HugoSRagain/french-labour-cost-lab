from pathlib import Path
import pandas as pd
import yaml


BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "scenarios.yml"
DATA_DIR = BASE_DIR / "data"
OUTPUT_PATH = DATA_DIR / "labour_cost_grid.csv"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def employer_rate_with_relief(
    smic_multiple: float,
    rate_at_smic: float,
    rate_above_relief: float,
    relief_end: float
) -> float:
    """
    Stylized employer contribution schedule.

    At 1.0 SMIC, employer contributions are reduced.
    Between 1.0 and relief_end SMIC, the relief is phased out linearly.
    Above relief_end SMIC, the full employer contribution rate applies.
    """

    if smic_multiple <= 1.0:
        return rate_at_smic

    if smic_multiple >= relief_end:
        return rate_above_relief

    progress = (smic_multiple - 1.0) / (relief_end - 1.0)
    return rate_at_smic + progress * (rate_above_relief - rate_at_smic)


def build_dataset():
    config = load_config()

    baseline = config["baseline"]
    assumptions = config["assumptions"]

    monthly_smic_gross = baseline["monthly_smic_gross"]
    min_multiple = baseline["min_smic_multiple"]
    max_multiple = baseline["max_smic_multiple"]
    step = baseline["step_smic_multiple"]

    employee_rate = assumptions["employee_contribution_rate"]
    employer_rate_above = assumptions["employer_contribution_rate_above_relief"]
    employer_rate_at_smic = assumptions["employer_contribution_rate_at_smic"]
    relief_end = assumptions["relief_end_smic_multiple"]

    smic_multiples = []
    current = min_multiple

    while current <= max_multiple + 1e-9:
        smic_multiples.append(round(current, 2))
        current += step

    rows = []

    for multiple in smic_multiples:
        gross_monthly = monthly_smic_gross * multiple

        employer_rate = employer_rate_with_relief(
            smic_multiple=multiple,
            rate_at_smic=employer_rate_at_smic,
            rate_above_relief=employer_rate_above,
            relief_end=relief_end
        )

        employee_contributions = gross_monthly * employee_rate
        employer_contributions = gross_monthly * employer_rate

        net_monthly = gross_monthly - employee_contributions
        employer_cost = gross_monthly + employer_contributions

        social_wedge = employer_cost - net_monthly
        social_wedge_rate = social_wedge / employer_cost if employer_cost else None

        rows.append({
            "smic_multiple": multiple,
            "gross_monthly_eur": round(gross_monthly, 2),
            "net_monthly_eur": round(net_monthly, 2),
            "employer_cost_monthly_eur": round(employer_cost, 2),
            "employee_contributions_monthly_eur": round(employee_contributions, 2),
            "employer_contributions_monthly_eur": round(employer_contributions, 2),
            "employee_contribution_rate": round(employee_rate, 4),
            "employer_contribution_rate": round(employer_rate, 4),
            "social_wedge_monthly_eur": round(social_wedge, 2),
            "social_wedge_rate": round(social_wedge_rate, 4),
            "cost_to_net_ratio": round(employer_cost / net_monthly, 4)
        })

    df = pd.DataFrame(rows)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Dataset created: {OUTPUT_PATH}")
    print(df.head())


if __name__ == "__main__":
    build_dataset()