# workflow/rules/quantile_regression.smk

TRAIN_REPS = range(1000)
TEST_REPS = range(10)


rule merge_null_scores:
    input:
        tsvs=expand(
            "run_null/results/sstar/rep_{rep}/sstar.phased.rep_{rep}.scores.tsv",
            rep=TRAIN_REPS,
        ),
    output:
        tsv="results/results_null/sstar/null.training.tsv",
    conda:
        "../envs/env.yaml"
    script:
        "../scripts/merge_score_tables.py"


rule merge_introgression_scores:
    input:
        tsvs=expand(
            "run_intro/results/sstar/rep_{rep}/sstar.phased.rep_{rep}.scores.tsv",
            rep=TEST_REPS,
        ),
    output:
        tsv="results/results_introgression/sstar/introgression.test.tsv",
    conda:
        "../envs/env.yaml"
    script:
        "../scripts/merge_score_tables.py"


rule run_quantile_regression:
    input:
        null_tsv="results/results_null/sstar/null.training.tsv",
        score_tsv="results/results_introgression/sstar/introgression.test.tsv",
    output:
        predictions=(
            "results/results_introgression/ml/"
            "{model_type}.{feature_set}.quantile_regression.predictions.tsv"
        ),
    params:
        quantile=config["quantile"],
        alpha=0.0,
        model_type="{model_type}",
        feature_set="{feature_set}",
    conda:
        "../envs/env.yaml"
    resources:
        mem_gb=16,
    script:
        "../scripts/quantile_regression.py"


rule evaluate_quantile_regression:
    input:
        predictions=(
            "results/results_introgression/ml/"
            "{model_type}.{feature_set}.quantile_regression.predictions.tsv"
        ),
    output:
        tsv=(
            "results/results_introgression/ml/"
            "{model_type}.{feature_set}.quantile_regression.evaluation.tsv"
        ),
    conda:
        "../envs/env.yaml"
    script:
        "../scripts/evaluate_prediction_calls.py"
