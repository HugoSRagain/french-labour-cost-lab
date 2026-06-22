var GERMANY_DATA = [];

const GERMANY_COLORS = {
    blue: "#2563eb",
    orange: "#f97316",
    green: "#16a34a",
    red: "#dc2626",
    purple: "#7c3aed",
    teal: "#0891b2",
    navy: "#0f172a",
    gray: "#6b7280"
};

function deNum(value) {
    if (value === null || value === undefined || value === "") {
        return 0;
    }

    if (typeof value === "number") {
        return Number.isFinite(value) ? value : 0;
    }

    const parsed = Number(
        String(value)
            .replace(/\s/g, "")
            .replace(",", ".")
    );

    return Number.isFinite(parsed) ? parsed : 0;
}

function deEuro(value) {
    return Math.round(deNum(value)).toLocaleString("fr-FR") + " €";
}

function dePct(value) {
    return (deNum(value) * 100).toFixed(1).replace(".", ",") + " %";
}

function getGermanySelectedProfile() {
    const select = document.getElementById("germany-profile-select");

    if (!select) {
        return "germany__public_health__with_children__outside_saxony";
    }

    return select.value;
}

function getGermanyProfileData() {
    const profileId = getGermanySelectedProfile();

    return GERMANY_DATA
        .filter(row => row.profile_id === profileId)
        .sort((a, b) => deNum(a.smic_multiple) - deNum(b.smic_multiple));
}

function germanyBaseLayout(yTitle) {
    return {
        template: "plotly_white",
        height: 440,
        margin: {
            l: 72,
            r: 42,
            t: 48,
            b: 90
        },
        font: {
            family: "Arial",
            size: 13,
            color: GERMANY_COLORS.navy
        },
        paper_bgcolor: "#ffffff",
        plot_bgcolor: "#ffffff",
        hovermode: "x unified",
        legend: {
            orientation: "h",
            yanchor: "top",
            y: -0.20,
            xanchor: "center",
            x: 0.5,
            font: {
                size: 12
            }
        },
        xaxis: {
            title: "Salaire brut, multiple du salaire minimum allemand",
            showgrid: false,
            zeroline: false
        },
        yaxis: {
            title: yTitle,
            showgrid: true,
            gridcolor: "#e5e7eb",
            zeroline: false
        }
    };
}

function germanyPlot(targetId, traces, layout) {
    const target = document.getElementById(targetId);

    if (!target) {
        console.warn("Plot target not found:", targetId);
        return;
    }

    Plotly.react(target, traces, layout, {
        responsive: true,
        displaylogo: false,
        modeBarButtonsToRemove: ["select2d", "lasso2d", "autoScale2d"]
    });
}

function findGermanyClosestRow(data, targetMultiple) {
    let closestRow = data[0];
    let minDistance = Infinity;

    data.forEach(row => {
        const distance = Math.abs(
            deNum(row.smic_multiple) - targetMultiple
        );

        if (distance < minDistance) {
            closestRow = row;
            minDistance = distance;
        }
    });

    return closestRow;
}

function renderGermanyMetrics() {
    const data = getGermanyProfileData();

    if (!data.length) {
        return;
    }

    const rowOne = findGermanyClosestRow(data, 1.00);
    const rowTwo = findGermanyClosestRow(data, 2.00);

    document.getElementById("germany-net-minimum").textContent =
        deEuro(rowOne.net_before_income_tax_monthly_eur);

    document.getElementById("germany-cost-minimum").textContent =
        deEuro(rowOne.employer_cost_monthly_eur);

    document.getElementById("germany-employer-rate").textContent =
        dePct(rowOne.employer_contribution_rate);

    document.getElementById("germany-cost-net-ratio").textContent =
        deNum(rowTwo.cost_to_net_ratio).toFixed(2);
}

function renderGermanyCostChart() {
    const data = getGermanyProfileData();

    const traces = [
        {
            x: data.map(row => deNum(row.smic_multiple)),
            y: data.map(row => deNum(row.gross_monthly_eur)),
            mode: "lines",
            name: "Salaire brut",
            line: {
                color: GERMANY_COLORS.green,
                width: 2.5,
                dash: "dot"
            },
            type: "scatter"
        },
        {
            x: data.map(row => deNum(row.smic_multiple)),
            y: data.map(row => deNum(row.net_before_income_tax_monthly_eur)),
            mode: "lines",
            name: "Salaire net avant impôt",
            line: {
                color: GERMANY_COLORS.orange,
                width: 3
            },
            type: "scatter"
        },
        {
            x: data.map(row => deNum(row.smic_multiple)),
            y: data.map(row => deNum(row.employer_cost_monthly_eur)),
            mode: "lines",
            name: "Coût employeur",
            line: {
                color: GERMANY_COLORS.blue,
                width: 3
            },
            type: "scatter"
        }
    ];

    const layout = germanyBaseLayout("Montant mensuel, euros");
    layout.yaxis.ticksuffix = " €";

    germanyPlot("chart-germany-cost", traces, layout);
}

function renderGermanyContributionRateChart() {
    const data = getGermanyProfileData();

    const traces = [
        {
            x: data.map(row => deNum(row.smic_multiple)),
            y: data.map(row => deNum(row.employee_contribution_rate) * 100),
            mode: "lines",
            name: "Taux salarié",
            line: {
                color: GERMANY_COLORS.orange,
                width: 3
            },
            type: "scatter"
        },
        {
            x: data.map(row => deNum(row.smic_multiple)),
            y: data.map(row => deNum(row.employer_contribution_rate) * 100),
            mode: "lines",
            name: "Taux employeur",
            line: {
                color: GERMANY_COLORS.blue,
                width: 3
            },
            type: "scatter"
        }
    ];

    const layout = germanyBaseLayout("Taux effectif");
    layout.yaxis.ticksuffix = "%";

    germanyPlot("chart-germany-rates", traces, layout);
}

function renderGermanyWedgeChart() {
    const data = getGermanyProfileData();

    const traces = [
        {
            x: data.map(row => deNum(row.smic_multiple)),
            y: data.map(row => deNum(row.social_wedge_rate) * 100),
            mode: "lines",
            name: "Coin social",
            line: {
                color: GERMANY_COLORS.teal,
                width: 3
            },
            fill: "tozeroy",
            fillcolor: "rgba(8, 145, 178, 0.12)",
            type: "scatter"
        }
    ];

    const layout = germanyBaseLayout("Coin social / coût employeur");
    layout.yaxis.ticksuffix = "%";

    germanyPlot("chart-germany-wedge", traces, layout);
}

function renderGermanyDecompositionChart() {
    const data = getGermanyProfileData();

    if (!data.length) {
        return;
    }

    const row = findGermanyClosestRow(data, 2.00);

    const labels = [
        "Salaire net avant impôt",
        "Cotisations salarié",
        "Cotisations employeur",
        "Coût employeur"
    ];

    const values = [
        deNum(row.net_before_income_tax_monthly_eur),
        deNum(row.employee_contributions_monthly_eur),
        deNum(row.employer_contributions_monthly_eur),
        deNum(row.employer_cost_monthly_eur)
    ];

    const traces = [
        {
            x: labels,
            y: values,
            type: "bar",
            text: values.map(value => deEuro(value)),
            textposition: "outside",
            marker: {
                color: [
                    GERMANY_COLORS.orange,
                    GERMANY_COLORS.red,
                    GERMANY_COLORS.blue,
                    GERMANY_COLORS.purple
                ]
            },
            hovertemplate:
                "<b>%{x}</b><br>" +
                "Montant: %{y:,.0f} €" +
                "<extra></extra>"
        }
    ];

    const layout = germanyBaseLayout("Montant mensuel, euros");
    layout.height = 460;
    layout.showlegend = false;
    layout.xaxis.title = "";
    layout.yaxis.ticksuffix = " €";

    germanyPlot("chart-germany-decomposition", traces, layout);
}

function renderGermanyContributionBreakdownChart() {
    const data = getGermanyProfileData();

    if (!data.length) {
        return;
    }

    const row = findGermanyClosestRow(data, 2.00);

    const labels = [
        "Retraite",
        "Chômage",
        "Maladie",
        "Dépendance"
    ];

    const employeeValues = [
        deNum(row.employee_pension_monthly_eur),
        deNum(row.employee_unemployment_monthly_eur),
        deNum(row.employee_health_monthly_eur),
        deNum(row.employee_care_monthly_eur)
    ];

    const employerValues = [
        deNum(row.employer_pension_monthly_eur),
        deNum(row.employer_unemployment_monthly_eur),
        deNum(row.employer_health_monthly_eur),
        deNum(row.employer_care_monthly_eur)
    ];

    const traces = [
        {
            x: labels,
            y: employeeValues,
            name: "Salarié",
            type: "bar",
            marker: {
                color: GERMANY_COLORS.orange
            }
        },
        {
            x: labels,
            y: employerValues,
            name: "Employeur",
            type: "bar",
            marker: {
                color: GERMANY_COLORS.blue
            }
        }
    ];

    const layout = germanyBaseLayout("Montant mensuel à 2 salaires minimums, euros");
    layout.barmode = "group";
    layout.yaxis.ticksuffix = " €";
    layout.xaxis.title = "";

    germanyPlot("chart-germany-breakdown", traces, layout);
}

function renderGermany() {
    renderGermanyMetrics();
    renderGermanyCostChart();
    renderGermanyContributionRateChart();
    renderGermanyWedgeChart();
    renderGermanyDecompositionChart();
    renderGermanyContributionBreakdownChart();
}

function setupGermanyEvents() {
    const profileSelect = document.getElementById("germany-profile-select");

    if (profileSelect) {
        profileSelect.addEventListener("change", function() {
            renderGermany();
        });
    }
}

function loadGermanyData() {
    if (typeof Papa === "undefined") {
        console.error("PapaParse is not loaded.");
        return;
    }

    Papa.parse("../../data/germany/germany_labour_cost_grid_2026.csv", {
        download: true,
        header: true,
        dynamicTyping: false,
        complete: function(results) {
            GERMANY_DATA = results.data
                .filter(row => row.profile_id)
                .sort((a, b) => deNum(a.smic_multiple) - deNum(b.smic_multiple));

            console.log(
                "Germany Labour Cost Lab data loaded:",
                GERMANY_DATA.length,
                "rows"
            );

            setupGermanyEvents();
            renderGermany();
        },
        error: function(error) {
            console.error("Germany CSV loading error:", error);
        }
    });
}

document.addEventListener("DOMContentLoaded", loadGermanyData);