from pathlib import Path

import pandas as pd

INPUT_FILE = Path("data/input/orders.csv")
OUTPUT_DIRECTORY = Path("data/output")

def load_orders() -> pd.DataFrame:
    return pd.read_csv(INPUT_FILE, parse_dates=["order_date"])

def get_rejection_reason(row):
    reasons = []

    if pd.isna(row["order_id"]):
        reasons.append("missing_order_id")

    if pd.isna(row["order_date"]):
        reasons.append("missing_order_date")

    if row["quantity"] <= 0:
        reasons.append("quantity_must_be_positive")

    if row["unit_price"] < 0:
        reasons.append("unit_price_must_be_positive")

    if pd.isna(row["customer_country"]):
        reasons.append("missing_customer_country")

    return ", ".join(reasons)

def validate_orders(orders: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    orders["rejection_reason"] = orders.apply(
        get_rejection_reason,
        axis=1
    )

    invalid_mask = orders["rejection_reason"] != ""
    duplicate_mask = orders["order_id"].duplicated(keep=False)
    orders.loc[duplicate_mask, "rejection_reason"] = "duplicate_order_id"

    #print(orders.head())

    valid_orders = orders.loc[~invalid_mask & ~duplicate_mask].copy()
    rejected_orders = orders.loc[invalid_mask | duplicate_mask].copy()

    return valid_orders, rejected_orders

def calculate_daily_revenue(orders: pd.DataFrame) -> pd.DataFrame:
    completed = orders.loc[orders["status"] == "Completed"].copy()
    completed["line_total"] = (
        completed["quantity"] * completed["unit_price"]
    ).round(2)

    return (
        completed.groupby(["order_date", "customer_country"], as_index=False)["line_total"]
        .sum()
        .rename(columns={"line_total": "revenue"})
        .sort_values("order_date")
    )


def main():
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    orders = load_orders()
    valid_orders, rejected_orders = validate_orders(orders)
    daily_revenue = calculate_daily_revenue(valid_orders)

    valid_orders.to_csv(OUTPUT_DIRECTORY / "valid_orders.csv", index=False)
    rejected_orders.to_csv(OUTPUT_DIRECTORY / "rejected_orders.csv", index=False)

    print("Daily revenue")
    print(daily_revenue.to_string(index=False))
    print(f"\nAccepted records: {len(valid_orders)}")
    print(f"\nRejected records: {len(rejected_orders)}")


if __name__ == "__main__":
    main()
