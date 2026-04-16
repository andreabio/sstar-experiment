from pathlib import Path
import re
import pandas as pd

rows = []

for f in snakemake.input.tsvs:
    path = Path(f)
    df = pd.read_csv(path, sep="\t")
    if df.empty:
        continue

    row = df.iloc[0].to_dict()
    name = path.name

    method = "unknown"
    feature_set = "NA"
    model_cutoff = "NA"

    # sstar.q_0.80.segment_evaluation.tsv
    m_sstar = re.match(r"^sstar\.q_(\d+\.\d+)\.segment_evaluation\.tsv$", name)
    if m_sstar:
        method = "sstar"
        feature_set = "NA"
        model_cutoff = m_sstar.group(1)
    else:
        # quantile.region_snp.quantile_regression.segment_evaluation.tsv
        # gradient.region_snp.quantile_regression.segment_evaluation.tsv
        # qrf.region_snp.quantile_regression.segment_evaluation.tsv
        m_ml = re.match(
            r"^(quantile|gradient|qrf)\.(region_snp|sstar_snp|both)\.quantile_regression\.segment_evaluation\.tsv$",
            name,
        )
        if m_ml:
            method = m_ml.group(1)
            feature_set = m_ml.group(2)

    row["Method"] = method
    row["Feature_Set"] = feature_set
    row["Model_Cutoff"] = model_cutoff
    row["Source_File"] = name
    rows.append(row)

out = pd.DataFrame(rows)

front = ["Method", "Feature_Set", "Model_Cutoff", "Source_File"]
rest = [c for c in out.columns if c not in front]
out = out[front + rest]

out.to_csv(snakemake.output.tsv, sep="\t", index=False)
