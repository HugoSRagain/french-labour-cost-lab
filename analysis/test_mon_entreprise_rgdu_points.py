import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_dataset_mon_entreprise as b

TEST_WAGES = [1801.80, 1819.82, 1837.84]

profiles = b.load_profiles()
profile = profiles["non_cadre__standard__standard"]
profile_situation = profile.get("situation", {})

rgdu_expression = b.select_rgdu_expression(
    test_gross_monthly=1801.80,
    profile_situation=profile_situation
)

print("RGDU expression:", rgdu_expression)
print()

for wage in TEST_WAGES:
    payload = b.make_payload(
        gross_monthly=wage,
        expressions=b.BASE_EXPRESSIONS + [rgdu_expression],
        profile_situation=profile_situation
    )

    result = b.post_payload(payload)

    indicators = b.compute_indicators(
        result=result,
        gross_monthly=wage,
        rgdu_expression=rgdu_expression
    )

    print(
        f"Brut: {wage:.2f} € | "
        f"Coût employeur: {indicators['employer_cost']:.2f} € | "
        f"RGDU: {indicators['rgdu_monthly']:.2f} €"
    )