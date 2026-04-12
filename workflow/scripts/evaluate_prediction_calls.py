import pandas as pd


def evaluate(
    prediction_file: str,
    output: str,
) -> None:
    """
    Determine whether a window is introgressed based on actual and expected S* scores.
    """
    df = pd.read_csv(prediction_file, sep="\t")

    required_cols = ["S*_score", "expected_S*_score"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required columns in prediction file: {missing_cols}"
        )

    df = df.copy()
    df["pred_label"] = (df["S*_score"] > df["expected_S*_score"]).astype(int)

    df.to_csv(output, sep="\t", index=False)


evaluate(
    prediction_file=snakemake.input.predictions,
    output=snakemake.output.tsv,
)
