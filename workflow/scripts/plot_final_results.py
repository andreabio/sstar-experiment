import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(snakemake.input.tsv, sep="\t").copy()

df["Precision"] = pd.to_numeric(df["Precision"], errors="coerce")
df["Recall"] = pd.to_numeric(df["Recall"], errors="coerce")
df["Cutoff"] = pd.to_numeric(df["Cutoff"], errors="coerce")
df = df.dropna(subset=["Precision", "Recall"])

# ---------- Plot 1: Precision vs Recall ----------
plt.figure(figsize=(8, 6))

for _, row in df.iterrows():
    label = row["Method"]
    if row["Feature_Set"] != "NA":
        label += f".{row['Feature_Set']}"
    if row["Model_Cutoff"] != "NA":
        label += f".q_{row['Model_Cutoff']}"

    plt.scatter(row["Recall"], row["Precision"], s=60)
    plt.annotate(
        label,
        (row["Recall"], row["Precision"]),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=8,
    )

plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Segment-based Precision vs Recall")
plt.grid(True)
plt.tight_layout()
plt.savefig(snakemake.output.pr_png, dpi=300)
plt.close()

# ---------- Plot 2: S* cutoff sweep ----------
sstar = df[df["Method"] == "sstar"].copy()
sstar["Model_Cutoff"] = pd.to_numeric(sstar["Model_Cutoff"], errors="coerce")
sstar = sstar.dropna(subset=["Model_Cutoff"]).sort_values("Model_Cutoff")

if not sstar.empty:
    sstar["F1"] = 2 * sstar["Precision"] * sstar["Recall"] / (sstar["Precision"] + sstar["Recall"])

    plt.figure(figsize=(8, 6))
    plt.plot(sstar["Model_Cutoff"], sstar["Precision"], marker="o", label="Precision")
    plt.plot(sstar["Model_Cutoff"], sstar["Recall"], marker="o", label="Recall")
    plt.plot(sstar["Model_Cutoff"], sstar["F1"], marker="o", label="F1")

    plt.xlabel("S* quantile cutoff")
    plt.ylabel("Score")
    plt.title("S* Cutoff Sweep")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(snakemake.output.sstar_png, dpi=300)
    plt.close()
