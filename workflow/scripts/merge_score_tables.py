
import re
import pandas as pd


def get_rep(path: str) -> int:
    """
    Extract replicate index from file path.
    """
    return int(re.search(r"rep_(\d+)", path).group(1))


dfs = []
for f in snakemake.input.tsvs:
    df = pd.read_csv(f, sep="\t")
    df["rep"] = get_rep(f)
    dfs.append(df)

pd.concat(dfs, ignore_index=True).to_csv(snakemake.output.tsv, sep="\t", index=False)
