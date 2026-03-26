
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import QuantileRegressor
from sklearn.metrics import classification_report, precision_recall_fscore_support


def get_xy(df: pd.DataFrame, features: list[str]) -> tuple[pd.DataFrame, pd.Series]:
    """
    Extract model features and target.
    """
    x = df[features].copy()
    y = df["S*_score"].copy()
    return x, y


null_df = pd.read_csv(snakemake.input.null_tsv, sep="\t")
intro_df = pd.read_csv(snakemake.input.intro_tsv, sep="\t")

feature_sets = {
    "sstar_snp": ["S*_SNP_number"],
    "region_snp": ["region_ind_SNP_number"],
    "both": ["S*_SNP_number", "region_ind_SNP_number"],
}

quantile = float(snakemake.params.quantile)
alpha = float(snakemake.params.alpha)

results = []
pred_tables = []

for model_name, features in feature_sets.items():
    train = null_df.dropna(subset=features + ["S*_score"]).copy()
    test = intro_df.dropna(subset=features + ["S*_score", "true_label"]).copy()

    x_train, y_train = get_xy(train, features)
    x_test, _ = get_xy(test, features)

    # Linear quantile regression
    # model = QuantileRegressor(
    #     quantile=quantile,
    #     alpha=alpha,
    # )

    # Gradient boosting quantile regression
    model = GradientBoostingRegressor(
        loss="quantile",
        alpha=quantile,
        n_estimators=200,
        max_depth=3,
        random_state=42,
    )

    model.fit(x_train, y_train)

    test = test.copy()
    test["predicted_threshold"] = model.predict(x_test)
    test["pred_label"] = (test["S*_score"] > test["predicted_threshold"]).astype(int)
    test["model"] = model_name

    precision, recall, f1, _ = precision_recall_fscore_support(
        test["true_label"],
        test["pred_label"],
        average="binary",
        zero_division=0,
    )

    results.append(
        {
            "model": model_name,
            "features": ",".join(features),
            "quantile": quantile,
            "alpha": alpha,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "n_rows": len(test),
            "n_positive_true": int(test["true_label"].sum()),
            "n_positive_pred": int(test["pred_label"].sum()),
        }
    )

    pred_tables.append(test)

pd.DataFrame(results).to_csv(snakemake.output.summary, sep="\t", index=False)
pd.concat(pred_tables, ignore_index=True).to_csv(
    snakemake.output.predictions, sep="\t", index=False
)

with open(snakemake.output.report, "w") as o:
    pred_df = pd.concat(pred_tables, ignore_index=True)
    for model_name in feature_sets:
        x = pred_df[pred_df["model"] == model_name]
        o.write(f"[{model_name}]\n")
        o.write(
            classification_report(
                x["true_label"],
                x["pred_label"],
                zero_division=0,
            )
        )
        o.write("\n")
