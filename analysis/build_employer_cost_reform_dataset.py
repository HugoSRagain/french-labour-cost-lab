import pandas as pd
from pathlib import Path

MAY_PATH = Path("archive/labour_cost_grid_2026_05_corrected.csv")
JUNE_PATH = Path("docs/data/labour_cost_grid_mon_entreprise.csv")
OUTPUT_PATH = Path("docs/data/employer_cost_reform_june_2026.csv")

may = pd.read_csv(MAY_PATH)
june = pd.read_csv(JUNE_PATH)

PROFILE_ID = "non_cadre__standard__standard"

cols = [
    "profile_id",
    "smic_multiple",
    "employer_cost_monthly_eur"
]

may = may[cols]
june = june[cols]

may = may[may["profile_id"] == PROFILE_ID].copy()
june = june[june["profile_id"] == PROFILE_ID].copy()

may = may.drop_duplicates().sort_values("smic_multiple")
june = june.drop_duplicates().sort_values("smic_multiple")

comparison = may.merge(
    june,
    on=["profile_id", "smic_multiple"],
    suffixes=("_may", "_june")
)

comparison["delta_cost_eur"] = (
    comparison["employer_cost_monthly_eur_june"]
    - comparison["employer_cost_monthly_eur_may"]
)

comparison["delta_cost_pct"] = (
    100
    * comparison["delta_cost_eur"]
    / comparison["employer_cost_monthly_eur_may"]
)

comparison = comparison[comparison["smic_multiple"] >= 1.0].copy()

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
comparison.to_csv(OUTPUT_PATH, index=False)

print(f"Created: {OUTPUT_PATH}")
print(comparison.head(10).to_string(index=False))