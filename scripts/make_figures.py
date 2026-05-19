from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "labour_cost_grid.csv"
FIGURES_DIR = BASE_DIR / "figures"


def save_figure(filename: str):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FIGURES_DIR / filename
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    print(f"Figure created: {output_path}")


def main():
    df = pd.read_csv(DATA_PATH)

    plt.figure(figsize=(9, 5))
    plt.plot(df["gross_monthly_eur"], df["employer_cost_monthly_eur"], label="Employer cost")
    plt.plot(df["gross_monthly_eur"], df["net_monthly_eur"], label="Net wage")
    plt.xlabel("Gross monthly wage, euros")
    plt.ylabel("Monthly amount, euros")
    plt.title("Gross wage, net wage and employer cost")
    plt.legend()
    plt.grid(True, alpha=0.3)
    save_figure("cost_and_net_vs_gross.png")

    plt.figure(figsize=(9, 5))
    plt.plot(df["smic_multiple"], df["employer_contribution_rate"] * 100)
    plt.xlabel("Gross wage, SMIC multiple")
    plt.ylabel("Employer contribution rate, %")
    plt.title("Stylized effective employer contribution rate")
    plt.grid(True, alpha=0.3)
    save_figure("employer_contribution_rate.png")

    plt.figure(figsize=(9, 5))
    plt.plot(df["smic_multiple"], df["social_wedge_rate"] * 100)
    plt.xlabel("Gross wage, SMIC multiple")
    plt.ylabel("Social wedge, % of employer cost")
    plt.title("Stylized social wedge")
    plt.grid(True, alpha=0.3)
    save_figure("social_wedge_rate.png")

    plt.figure(figsize=(9, 5))
    plt.plot(df["smic_multiple"], df["cost_to_net_ratio"])
    plt.xlabel("Gross wage, SMIC multiple")
    plt.ylabel("Employer cost / net wage")
    plt.title("Cost-to-net ratio")
    plt.grid(True, alpha=0.3)
    save_figure("cost_to_net_ratio.png")


if __name__ == "__main__":
    main()