
import re
import pandas as pd


def format_sample(sample: str) -> str:
    """
    Convert phased sample names in S* output to the sample format used in BED.

    Parameters
    ----------
    sample : str
        Sample name in the S* score file, e.g. ``tsk_58_hap2``.

    Returns
    -------
    str
        Sample name in BED format, e.g. ``tsk_58_2``.
    """
    return re.sub(r"_hap([12])$", r"_\1", sample)


def label_introgressed(
    score_file: str,
    bed_file: str,
) -> pd.DataFrame:
    """
    Label S* windows by overlap with true introgressed tracts.

    Parameters
    ----------
    score_file : str
        Path to the S* score table.
    bed_file : str
        Path to the BED file with true introgressed tracts.

    Returns
    -------
    pd.DataFrame
        S* score table with true labels and introgressed lengths.
    """
    scores = pd.read_csv(score_file, sep="\t")
    scores["sample_bed"] = scores["sample"].map(format_sample)

    scores["S*_score"] = pd.to_numeric(scores["S*_score"], errors="coerce")
    scores["region_ind_SNP_number"] = pd.to_numeric(
        scores["region_ind_SNP_number"], errors="coerce"
    )
    scores["S*_SNP_number"] = pd.to_numeric(scores["S*_SNP_number"], errors="coerce")

    scores = scores.dropna(
        subset=["S*_score", "region_ind_SNP_number", "S*_SNP_number"]
    ).copy()

    scores["chrom"] = scores["chrom"].astype(str)
    scores["start"] = scores["start"].astype(int)
    scores["end"] = scores["end"].astype(int)

    try:
        tracts = pd.read_csv(
            bed_file,
            sep="\t",
            header=None,
            names=["chrom", "start", "end", "sample_bed"],
        )
    except pd.errors.EmptyDataError:
        scores["true_label"] = 0
        scores["true_introgressed_length"] = 0
        return scores

    tracts["chrom"] = tracts["chrom"].astype(str)
    tracts["start"] = tracts["start"].astype(int)
    tracts["end"] = tracts["end"].astype(int)

    true_label = []
    true_introgressed_length = []

    for row in scores.itertuples(index=False):
        x = tracts[
            (tracts["chrom"] == row.chrom)
            & (tracts["sample_bed"] == row.sample_bed)
            & (tracts["start"] < row.end)
            & (tracts["end"] > row.start)
        ]

        if x.empty:
            true_label.append(0)
            true_introgressed_length.append(0)
            continue

        overlap = (
            x[["start", "end"]]
            .apply(
                lambda y: max(
                    0,
                    min(row.end, y["end"]) - max(row.start, y["start"]),
                ),
                axis=1,
            )
            .sum()
        )
        true_label.append(int(overlap > 0))
        true_introgressed_length.append(int(overlap))

    scores["true_label"] = true_label
    scores["true_introgressed_length"] = true_introgressed_length

    return scores


df = label_introgressed(
    score_file=snakemake.input.score,
    bed_file=snakemake.input.bed,
)

df.to_csv(snakemake.output.tsv, sep="\t", index=False)
