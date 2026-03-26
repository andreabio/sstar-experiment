REPS = range(n_rep)


rule label_introgressed:
    input:
        score="results_introgression/results/sstar/rep_{rep}/sstar.phased.rep_{rep}.scores.tsv",
        bed="results_introgression/results/simulation/rep_{rep}/simulation.rep_{rep}.true.tracts.bed",
    output:
        tsv="results_introgression/results/labeled/rep_{rep}/sstar.phased.rep_{rep}.labeled.tsv",
    script:
        "../scripts/label_introgressed.py"


rule merge_introgression_labels:
    input:
        tsvs=expand(
            "results_introgression/results/labeled/rep_{rep}/sstar.phased.rep_{rep}.labeled.tsv",
            rep=REPS,
        ),
    output:
        tsv="results_introgression/results/labeled/introgression.labeled.tsv",
    script:
        "../scripts/merge_score_tables.py"


rule merge_null_scores:
    input:
        tsvs=expand(
            "results_null/results/sstar/rep_{rep}/sstar.phased.rep_{rep}.scores.tsv",
            rep=REPS,
        ),
    output:
        tsv="results_null/results/sstar/null.training.tsv",
    script:
        "../scripts/merge_score_tables.py"


rule run_quantile_regression:
    input:
        null_tsv="results_null/results/sstar/null.training.tsv",
        intro_tsv="results_introgression/results/labeled/introgression.labeled.tsv",
    output:
        summary="results_introgression/results/ml/quantile_regression.summary.tsv",
        predictions="results_introgression/results/ml/quantile_regression.predictions.tsv",
        report="results_introgression/results/ml/quantile_regression.report.txt",
    params:
        quantile=0.90,
        alpha=0.0,
    script:
        "../scripts/quantile_regression.py"
