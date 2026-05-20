import json
import time
import requests


API_URL = "https://mon-entreprise.urssaf.fr/api/v1/evaluate"

EXPRESSIONS = [
    "salarié . contrat . salaire brut",
    "salarié . rémunération . net",
    "salarié . coût total employeur",
    "salarié . cotisations . employeur",
    "salarié . cotisations . salarié",
    "salarié . cotisations . exonérations . RGDU",
    "établissement . taux ATMP",
    "salarié . cotisations . ATMP",
]


TEST_PROFILES = {
    "standard_default": {
        "label": "Standard non-cadre, taux AT/MP implicite",
        "situation": {
            "salarié . contrat . statut cadre": "non",
            "salarié . régimes spécifiques . alsace moselle": "non",
        }
    },

    "atmp_1_percent": {
        "label": "Non-cadre, taux AT/MP 1 %",
        "situation": {
            "salarié . contrat . statut cadre": "non",
            "salarié . régimes spécifiques . alsace moselle": "non",
            "établissement . taux ATMP": 1,
        }
    },

    "atmp_2_percent": {
        "label": "Non-cadre, taux AT/MP 2 %",
        "situation": {
            "salarié . contrat . statut cadre": "non",
            "salarié . régimes spécifiques . alsace moselle": "non",
            "établissement . taux ATMP": 2,
        }
    },

    "atmp_4_percent": {
        "label": "Non-cadre, taux AT/MP 4 %",
        "situation": {
            "salarié . contrat . statut cadre": "non",
            "salarié . régimes spécifiques . alsace moselle": "non",
            "établissement . taux ATMP": 4,
        }
    },

    "fonctions_support": {
        "label": "Non-cadre, taux fonctions support",
        "situation": {
            "salarié . contrat . statut cadre": "non",
            "salarié . régimes spécifiques . alsace moselle": "non",
            "salarié . cotisations . ATMP . taux fonctions support": "oui",
        }
    },
}


def make_situation(gross_monthly, profile_situation):
    situation = {
        "salarié . contrat . salaire brut": {
            "valeur": gross_monthly,
            "unité": "€/mois"
        }
    }

    situation.update(profile_situation)
    return situation


def evaluate_profile(profile_id, profile, gross_monthly):
    payload = {
        "situation": make_situation(gross_monthly, profile["situation"]),
        "expressions": EXPRESSIONS
    }

    response = requests.post(API_URL, json=payload, timeout=30)

    print("=" * 90)
    print(f"Profile: {profile_id} — {profile['label']}")
    print(f"Status code: {response.status_code}")
    print()

    try:
        data = response.json()
    except Exception:
        print("Non-JSON response:")
        print(response.text[:2000])
        return None

    if "situationError" in data:
        print("Situation error:")
        print(json.dumps(data["situationError"], indent=2, ensure_ascii=False))
        print()
        return None

    evaluate = data.get("evaluate")

    if not evaluate:
        print("No evaluate block returned.")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
        return None

    values = {}

    for expression, result in zip(EXPRESSIONS, evaluate):
        value = result.get("nodeValue")
        missing = result.get("missingVariables", {})
        unit = result.get("unit", {})

        values[expression] = value

        print(expression)
        print(f"  value: {value}")
        print(f"  unit: {unit}")
        print(f"  missing variables: {len(missing)}")
        print()

    warnings = data.get("warnings", [])
    if warnings:
        print("Warnings:")
        for warning in warnings[:5]:
            print(warning.get("message", "").strip())
            print()

    return values


def main():
    gross_monthly = 3603.60  # 2 SMIC
    summary = []

    for profile_id, profile in TEST_PROFILES.items():
        values = evaluate_profile(profile_id, profile, gross_monthly)

        if values:
            summary.append({
                "profile": profile_id,
                "net": values.get("salarié . rémunération . net"),
                "employer_cost": values.get("salarié . coût total employeur"),
                "employer_contrib": values.get("salarié . cotisations . employeur"),
                "employee_contrib": values.get("salarié . cotisations . salarié"),
                "rgdu": values.get("salarié . cotisations . exonérations . RGDU"),
                "atmp_rate": values.get("établissement . taux ATMP"),
                "atmp_contrib": values.get("salarié . cotisations . ATMP"),
            })

        time.sleep(2)

    print()
    print("#" * 90)
    print("SUMMARY")
    print("#" * 90)

    for row in summary:
        print(
            f"{row['profile']} | "
            f"net={row['net']} | "
            f"employer_cost={row['employer_cost']} | "
            f"employer_contrib={row['employer_contrib']} | "
            f"rgdu={row['rgdu']} | "
            f"atmp_rate={row['atmp_rate']} | "
            f"atmp_contrib={row['atmp_contrib']}"
        )


if __name__ == "__main__":
    main()