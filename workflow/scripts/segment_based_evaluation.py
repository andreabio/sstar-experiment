import numpy as np
import pandas as pd
import pyranges as pr


def calc_pr(
    ntrue_tracts: int, ninferred_tracts: int, ntrue_positives: int
) -> tuple[float, float]:
    if float(ninferred_tracts) == 0:
        precision = np.nan
    else:
        precision = ntrue_positives / float(ninferred_tracts)

    if float(ntrue_tracts) == 0:
        recall = np.nan
    else:
        recall = ntrue_positives / float(ntrue_tracts)

    return precision, recall


def evaluate(
    true_tract_file: str,
    inferred_tract_file: str,
    seq_len: int,
    cutoff: float,
    output: str,
) -> None:
    try:
        true_tracts = pd.read_csv(
            true_tract_file,
            sep="\t",
            header=None,
            names=["Chromosome", "Start", "End", "Sample"],
        )
    except pd.errors.EmptyDataError:
        true_tracts_samples = []
    else:
        true_tracts_samples = true_tracts["Sample"].unique()
        true_tracts = pr.PyRanges(true_tracts).merge(by="Sample")

    try:
        inferred_tracts = pd.read_csv(
            inferred_tract_file,
            sep="\t",
            header=None,
            names=["Chromosome", "Start", "End", "Sample"],
        )
    except pd.errors.EmptyDataError:
        inferred_tracts_samples = []
    else:
        inferred_tracts_samples = inferred_tracts["Sample"].unique()
        inferred_tracts = pr.PyRanges(inferred_tracts).merge(by="Sample")

    res = pd.DataFrame(
        columns=[
            "Cutoff",
            "Precision",
            "Recall",
            "L_TT_sample",
            "L_IT_sample",
            "L_TP_sample",
            "L_FP_sample",
            "L_TN_sample",
            "L_FN_sample",
        ]
    )

    sum_ntrue_tracts = 0
    sum_ninferred_tracts = 0
    sum_ntrue_positives = 0

    overlap = np.intersect1d(true_tracts_samples, inferred_tracts_samples)
    true_tracts_only = np.setdiff1d(true_tracts_samples, inferred_tracts_samples)
    inferred_tracts_only = np.setdiff1d(inferred_tracts_samples, true_tracts_samples)

    sample_size = len(overlap) + len(true_tracts_only) + len(inferred_tracts_only)

    for s in overlap:
        ind_true_tracts = true_tracts[true_tracts.Sample == s]
        ind_inferred_tracts = inferred_tracts[inferred_tracts.Sample == s]
        ind_overlaps = ind_true_tracts.intersect(ind_inferred_tracts)

        ntrue_tracts = (ind_true_tracts.End - ind_true_tracts.Start).sum()
        ninferred_tracts = (ind_inferred_tracts.End - ind_inferred_tracts.Start).sum()
        ntrue_positives = (
            (ind_overlaps.End - ind_overlaps.Start).sum() if len(ind_overlaps) > 0 else 0
        )

        sum_ntrue_tracts += ntrue_tracts
        sum_ninferred_tracts += ninferred_tracts
        sum_ntrue_positives += ntrue_positives

    for s in true_tracts_only:
        ind_true_tracts = true_tracts[true_tracts.Sample == s]
        ntrue_tracts = (ind_true_tracts.End - ind_true_tracts.Start).sum()
        sum_ntrue_tracts += ntrue_tracts

    for s in inferred_tracts_only:
        ind_inferred_tracts = inferred_tracts[inferred_tracts.Sample == s]
        ninferred_tracts = (ind_inferred_tracts.End - ind_inferred_tracts.Start).sum()
        sum_ninferred_tracts += ninferred_tracts

    total_precision, total_recall = calc_pr(
        sum_ntrue_tracts, sum_ninferred_tracts, sum_ntrue_positives
    )

    sum_ntrue_negatives = seq_len * sample_size - sum_ntrue_tracts
    sum_nfalse_positives = sum_ninferred_tracts - sum_ntrue_positives
    sum_nfalse_negatives = sum_ntrue_tracts - sum_ntrue_positives

    res.loc[len(res.index)] = [
        cutoff,
        total_precision,
        total_recall,
        sum_ntrue_tracts / sample_size,
        sum_ninferred_tracts / sample_size,
        sum_ntrue_positives / sample_size,
        sum_nfalse_positives / sample_size,
        sum_ntrue_negatives / sample_size,
        sum_nfalse_negatives / sample_size,
    ]

    res.fillna("NaN").to_csv(output, sep="\t", index=False)


evaluate(
    true_tract_file=snakemake.input.true_tracts,
    inferred_tract_file=snakemake.input.inferred_tracts,
    seq_len=int(snakemake.params.length_bp),
    cutoff=float(snakemake.params.cutoff),
    output=snakemake.output.tsv,
)
