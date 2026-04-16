import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(snakemake.input.tsv, sep="\t")

# keep only rows with numeric precision/recall
df = df.copy()
df["Precision"] = pd.to_numeric(df["Precision"], errors="coerce")
df["Recall"] = pd.to_numeric(df["Recall"], errors="coerce")
df = df.dropna(subset=["Precision", "Recall"])

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
plt.title("Segment-based Precision-Recall Comparison")
plt.grid(True)
plt.tight_layout()
plt.savefig(snakemake.output.png, dpi=300)
