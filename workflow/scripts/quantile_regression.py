import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import QuantileRegressor
from quantile_forest import RandomForestQuantileRegressor


def get_xy(df: pd.DataFrame, features: list[str]) -> tuple[pd.DataFrame, pd.Series]:
    """
    Extract model features and target.
    """
    x = df[features].copy()
    y = df["S*_score"].copy()
    return x, y


def get_model(model_type: str, quantile: float, alpha: float):
    """
    Return the selected regression model.
    """
    if model_type == "quantile":
        return QuantileRegressor(
            quantile=quantile,
            alpha=alpha,
            solver="highs",
        )

    if model_type == "gradient":
        return GradientBoostingRegressor(
            loss="quantile",
            alpha=quantile,
            n_estimators=200,
            max_depth=3,
            random_state=42,
        )

    if model_type == "qrf":
        return RandomForestQuantileRegressor(
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
        )

    raise ValueError(
        f"Unsupported model_type: {model_type}. "
        "Choose from: 'quantile', 'gradient', or 'qrf'."
    )


null_df = pd.read_csv(snakemake.input.null_tsv, sep="\t")
score_df = pd.read_csv(snakemake.input.score_tsv, sep="\t")

feature_sets = {
    "sstar_snp": ["S*_SNP_number"],
    "region_snp": ["region_ind_SNP_number"],
    "both": ["S*_SNP_number", "region_ind_SNP_number"],
}

quantile = float(snakemake.params.quantile)
alpha = float(snakemake.params.alpha)
model_type = snakemake.params.model_type
feature_set = snakemake.params.feature_set

if feature_set not in feature_sets:
    raise ValueError(
        f"Unsupported feature_set: {feature_set}. "
        f"Choose from: {list(feature_sets.keys())}"
    )

features = feature_sets[feature_set]

train = null_df.dropna(subset=features + ["S*_score"]).copy()
pred_df = score_df.dropna(subset=features + ["S*_score"]).copy()

x_train, y_train = get_xy(train, features)
x_pred, _ = get_xy(pred_df, features)

model = get_model(model_type, quantile, alpha)
model.fit(x_train, y_train)

pred_df = pred_df.copy()

if model_type == "qrf":
    pred_df["expected_S*_score"] = model.predict(
        x_pred,
        quantiles=quantile,
    )
else:
    pred_df["expected_S*_score"] = model.predict(x_pred)

pred_df.to_csv(snakemake.output.predictions, sep="\t", index=False)
