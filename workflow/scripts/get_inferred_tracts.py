import pandas as pd
import pyranges as pr

df = pd.read_csv(snakemake.input.predictions, sep="\t")

required_cols = ["chrom", "start", "end", "sample", "S*_score", "expected_S*_score"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df = df.dropna(subset=["S*_score", "expected_S*_score"]).copy()
df = df[df["S*_score"] > df["expected_S*_score"]].copy()

if df.empty:
    open(snakemake.output.bed, "w").close()
else:
    bed = df[["chrom", "start", "end", "sample"]].copy()
    bed.columns = ["Chromosome", "Start", "End", "Sample"]
    bed["Chromosome"] = bed["Chromosome"].astype(str)

    gr = pr.PyRanges(bed).merge(by="Sample")
    gr.to_csv(snakemake.output.bed, sep="\t", header=False)
