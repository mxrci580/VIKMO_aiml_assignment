import pandas as pd
from sklearn.ensemble import RandomForestRegressor
df = pd.read_csv("data/sales_history.csv")

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(["sku", "date"])

for lag in [1, 2, 3, 4]:
    df[f"lag_{lag}"] = (
        df.groupby("sku")["units_sold"]
        .shift(lag)
    )

df["rolling_mean_4"] = (
    df.groupby("sku")["units_sold"]
      .shift(1)
      .rolling(4)
      .mean()
)

model_df = df.dropna().copy()

print(model_df.head())

test_idx = (
    model_df.groupby("sku")
    .tail(4)
    .index
)

test_df = model_df.loc[test_idx]
train_df = model_df.drop(test_idx)

print("Train:", train_df.shape)
print("Test :", test_df.shape)

from sklearn.metrics import mean_absolute_error

baseline_pred = test_df["rolling_mean_4"]

baseline_mae = mean_absolute_error(
    test_df["units_sold"],
    baseline_pred
)

print("Baseline MAE:", baseline_mae)

from sklearn.ensemble import RandomForestRegressor

features = [
    "lag_1",
    "lag_2",
    "lag_3",
    "lag_4",
    "rolling_mean_4",
    "promo_flag"
]

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(
    train_df[features],
    train_df["units_sold"]
)

preds = model.predict(
    test_df[features]
)

rf_mae = mean_absolute_error(
    test_df["units_sold"],
    preds
)

print("RF MAE:", rf_mae)

sku_results = (
    test_df.assign(pred=preds)
    .groupby("sku")
    .apply(
        lambda x: mean_absolute_error(
            x["units_sold"],
            x["pred"]
        )
    )
)

print(sku_results.sort_values())

features = [

    "lag_1",

    "lag_2",

    "lag_3",

    "lag_4",

    "rolling_mean_4",

    "promo_flag"

]

final_model = RandomForestRegressor(

    n_estimators=200,

    random_state=42

)

final_model.fit(

    model_df[features],

    model_df["units_sold"]

)

def forecast_next_4_weeks(df, sku, model):
    sku_df = df[df["sku"] == sku].sort_values("date")

    history = list(sku_df["units_sold"].values)

    forecasts = []

    for _ in range(4):

        lag_1 = history[-1]
        lag_2 = history[-2]
        lag_3 = history[-3]
        lag_4 = history[-4]

        rolling_mean_4 = sum(history[-4:]) / 4

        row = [[
            lag_1,
            lag_2,
            lag_3,
            lag_4,
            rolling_mean_4,
            0
        ]]

        pred = model.predict(row)[0]

        forecasts.append(round(pred, 2))

        history.append(pred)

    return forecasts

all_forecasts = []

for sku in sorted(df["sku"].unique()):

    future = forecast_next_4_weeks(
        df,
        sku,
        final_model
    )

    all_forecasts.append({
        "sku": sku,
        "week_1": future[0],
        "week_2": future[1],
        "week_3": future[2],
        "week_4": future[3]
    })

forecast_df = pd.DataFrame(all_forecasts)

print(forecast_df.head())

forecast_df.to_csv(
    "forecast_next_4_weeks.csv",
    index=False
)

importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

print(importance)

#python demand_forecasting.py