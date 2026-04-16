# workflow/rules/evaluation.smk

SSTAR_CUTOFFS = ["0.80", "0.85", "0.90", "0.95", "0.99"]


rule get_quantile_inferred_tracts:
    input:
        predictions=(
            "results/results_introgression/ml/"
            "{model_type}.{feature_set}.quantile_regression.predictions.tsv"
        ),
    output:
        bed=(
            "results/results_introgression/ml/"
            "{model_type}.{feature_set}.quantile_regression.inferred_tracts.bed"
        ),
    conda:
        "../envs/env.yaml"
    script:
        "../scripts/get_inferred_tracts.py"


rule evaluate_quantile_segment_based:
    input:
        true_tracts="results/results_introgression/simulation/introgression.true.tracts.bed",
        inferred_tracts=(
            "results/results_introgression/ml/"
            "{model_type}.{feature_set}.quantile_regression.inferred_tracts.bed"
        ),
    output:
        tsv=(
            "results/results_introgression/ml/"
            "{model_type}.{feature_set}.quantile_regression.segment_evaluation.tsv"
        ),
    params:
        length_bp=200000000,
        cutoff=0.90,
    conda:
        "../envs/env.yaml"
    script:
        "../scripts/segment_based_evaluation.py"


rule get_sstar_inferred_tracts:
    input:
        predictions="results/results_introgression/ml/sstar.q_{cutoff}.predictions.tsv",
    output:
        bed="results/results_introgression/ml/sstar.q_{cutoff}.inferred_tracts.bed",
    conda:
        "../envs/env.yaml"
    script:
        "../scripts/get_inferred_tracts.py"


rule evaluate_sstar_segment_based:
    input:
        true_tracts="results/results_introgression/simulation/introgression.true.tracts.bed",
        inferred_tracts="results/results_introgression/ml/sstar.q_{cutoff}.inferred_tracts.bed",
    output:
        tsv="results/results_introgression/ml/sstar.q_{cutoff}.segment_evaluation.tsv",
    params:
        length_bp=200000000,
        cutoff=lambda wildcards: float(wildcards.cutoff),
    conda:
        "../envs/env.yaml"
    script:
        "../scripts/segment_based_evaluation.py"


rule collect_segment_evaluations:
    input:
        tsvs=
            [
                "results/results_introgression/ml/quantile.region_snp.quantile_regression.segment_evaluation.tsv",
                "results/results_introgression/ml/quantile.sstar_snp.quantile_regression.segment_evaluation.tsv",
                "results/results_introgression/ml/quantile.both.quantile_regression.segment_evaluation.tsv",
                "results/results_introgression/ml/gradient.region_snp.quantile_regression.segment_evaluation.tsv",
                "results/results_introgression/ml/qrf.region_snp.quantile_regression.segment_evaluation.tsv",
            ]
            + expand(
                "results/results_introgression/ml/sstar.q_{cutoff}.segment_evaluation.tsv",
                cutoff=SSTAR_CUTOFFS,
            ),
    output:
        tsv="results/results_introgression/ml/segment_evaluation.summary.tsv",
    conda:
        "../envs/env.yaml"
    script:
        "../scripts/collect_segment_evaluations.py"


rule plot_segment_evaluation_pr_curve:
    input:
        tsv="results/results_introgression/ml/segment_evaluation.summary.tsv",
    output:
        png="results/results_introgression/ml/segment_evaluation.pr_curve.png",
    conda:
        "../envs/env.yaml"
    script:
        "../scripts/plot_segment_pr_curve.py"


rule plot_final_results:
    input:
        tsv="results/results_introgression/ml/segment_evaluation.summary.tsv",
    output:
        pr_png="results/results_introgression/ml/segment_evaluation.pr_scatter.png",
        sstar_png="results/results_introgression/ml/sstar.cutoff_sweep.png",
    conda:
        "../envs/env.yaml"
    script:
        "../scripts/plot_final_results.py"
