from pathlib import Path

import pandas as pd

INPUT_FILE = Path("data/input/orders.csv")
OUTPUT_DIRECTORY = Path("data/output")

def load_orders() -> pd.DataFrame:
    return pd.read_csv(INPUT_FILE, parse_dates=["order_date"])

def validate_orders(orders: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    invalid_mask = (
        orders["order_id"].isna()
        | orders["order_date"].isna()
        | (orders["quantity"] <= 0)
        | (orders["unit_price"] < 0)
    )

    valid_orders = orders.loc[~invalid_mask].copy()
    rejected_orders = orders.loc[invalid_mask].copy()

    rejected_orders["rejection_reason"] = "Invalid required value"

    return valid_orders, rejected_orders

def calculate_daily_revenue(orders: pd.DataFrame) -> pd.DataFrame:
    completed = orders.loc[orders["status"] == "Completed"].copy()
    completed["line_total"] = (
        completed["quantity"] * completed["unit_price"]
    ).round(2)

    return (
        completed.groupby("order_date", as_index=False)["line_total"]
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
    print(f"\Rejected records: {len(rejected_orders)}")


if __name__ == "__main__":
    main()
