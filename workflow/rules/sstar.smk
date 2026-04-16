# workflow/rules/sstar.smk

import os
import numpy as np
import pandas as pd


rule sstar_quantile:
    input:
        score="results/results_null/sstar/null.training.tsv",
    output:
        quantile="results/results_null/sstar/null.training.quantile.tsv",
    params:
        quantiles=np.arange(0.5, 1, 0.005),
    run:
        df = pd.read_csv(input.score, sep="\t").dropna(subset=["S*_score"])
        scores = np.quantile(df["S*_score"].to_numpy(), params.quantiles)

        os.makedirs(os.path.dirname(output.quantile), exist_ok=True)
        with open(output.quantile, "w") as o:
            o.write("expected_S*_score\tquantile\n")
            for val, q in zip(scores, params.quantiles):
                o.write(f"{val}\t{q}\n")


rule sstar_predict:
    input:
        score="results/results_introgression/sstar/introgression.test.tsv",
        quantile="results/results_null/sstar/null.training.quantile.tsv",
    output:
        predictions="results/results_introgression/ml/sstar.q_{cutoff}.predictions.tsv",
    params:
        cutoff=lambda wildcards: float(wildcards.cutoff),
    run:
        score_df = pd.read_csv(input.score, sep="\t")
        quantile_df = pd.read_csv(input.quantile, sep="\t")

        idx = (quantile_df["quantile"] - params.cutoff).abs().idxmin()
        threshold = float(quantile_df.loc[idx, "expected_S*_score"])

        pred_df = score_df.copy()
        pred_df["expected_S*_score"] = threshold

        os.makedirs(os.path.dirname(output.predictions), exist_ok=True)
        pred_df.to_csv(output.predictions, sep="\t", index=False)


rule evaluate_sstar_prediction:
    input:
        predictions="results/results_introgression/ml/sstar.q_{cutoff}.predictions.tsv",
    output:
        tsv="results/results_introgression/ml/sstar.q_{cutoff}.evaluation.tsv",
    conda:
        "../envs/env.yaml"
    script:
        "../scripts/evaluate_prediction_calls.py"
