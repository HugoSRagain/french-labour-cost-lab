import json
import time
import requests


API_URL = "https://mon-entreprise.urssaf.fr/api/v1/evaluate"

EFFECTIF_RULE = "entreprise . salariés . effectif . seuil"

EXPRESSIONS = [
    "salarié . contrat . salaire brut",
    "salarié . rémunération . net",
    "salarié . coût total employeur",
    "salarié . cotisations . employeur",
    "salarié . cotisations . salarié",
    "salarié . cotisations . exonérations . RGDU",
]


def make_situation(gross_monthly, effectif_value):
    return {
        "salarié . contrat . salaire brut": {
            "valeur": gross_monthly,
            "unité": "€/mois"
        },
        "salarié . contrat . statut cadre": "non",
        "salarié . régimes spécifiques . alsace moselle": "non",
        EFFECTIF_RULE: effectif_value,
    }


def evaluate_case(effectif_value, gross_monthly):
    payload = {
        "situation": make_situation(gross_monthly, effectif_value),
        "expressions": EXPRESSIONS
    }

    response = requests.post(API_URL, json=payload, timeout=30)

    print("=" * 90)
    print(f"Effectif tested: {effectif_value}")
    print(f"Status code: {response.status_code}")
    print()

    try:
        data = response.json()
    except Exception:
        print(response.text[:2000])
        return None

    if "situationError" in data:
        print("Situation error:")
        print(json.dumps(data["situationError"], indent=2, ensure_ascii=False))
        return None

    evaluate = data.get("evaluate", [])

    if not evaluate:
        print("No evaluate block returned.")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
        return None

    values = {}

    for expression, result in zip(EXPRESSIONS, evaluate):
        value = result.get("nodeValue")
        missing = result.get("missingVariables", {})
        values[expression] = value

        print(expression)
        print(f"  value: {value}")
        print(f"  missing variables: {len(missing)}")
        print()

    return values


def main():
    gross_monthly = 3603.60  # 2 SMIC

    summary = []

    for effectif in [10, 50, 250]:
        values = evaluate_case(effectif, gross_monthly)

        if values:
            summary.append({
                "effectif": effectif,
                "net": values.get("salarié . rémunération . net"),
                "employer_cost": values.get("salarié . coût total employeur"),
                "employer_contrib": values.get("salarié . cotisations . employeur"),
                "employee_contrib": values.get("salarié . cotisations . salarié"),
                "rgdu": values.get("salarié . cotisations . exonérations . RGDU"),
            })

        time.sleep(2)

    print()
    print("#" * 90)
    print("SUMMARY")
    print("#" * 90)

    for row in summary:
        print(
            f"effectif={row['effectif']} | "
            f"net={row['net']} | "
            f"employer_cost={row['employer_cost']} | "
            f"employer_contrib={row['employer_contrib']} | "
            f"employee_contrib={row['employee_contrib']} | "
            f"rgdu={row['rgdu']}"
        )


if __name__ == "__main__":
    main()