from pathlib import Path

import pandas as pd

INPUT_FILE = Path("data/input/orders.csv")
OUTPUT_DIRECTORY = Path("data/output")

def load_orders() -> pd.DataFrame:
    return pd.read_csv(INPUT_FILE, parse_dates=["order_date"])

def get_rejection_reason(row, duplicate_id: set) -> str:
    reasons = []

    if pd.isna(row["order_id"]):
        reasons.append("missing_order_id")
    elif row["order_id"] in duplicate_id:
        reasons.append("duplicate_order_id")

    if pd.isna(row["order_date"]):
        reasons.append("missing_order_date")

    if pd.isna(row["quantity"]):
        reasons.append("missing_quantity")
    elif row["quantity"] <= 0:
        reasons.append("quantity_must_be_positive")

    if (pd.isna(row["unit_price"])):
        reasons.append("missing_unit_price")
    elif row["unit_price"] < 0:
        reasons.append("unit_price_must_be_positive")

    country = row["customer_country"]

    if pd.isna(country) or str(country).strip() == "":
        reasons.append("missing_customer_country")

    allowed_statuses = {"Completed", "Cancelled"}

    if pd.isna(row["status"]):
        reasons.append("missing_status")
    elif row["status"] not in allowed_statuses:
        reasons.append("invalid_status")

    return ", ".join(reasons)

def validate_orders(orders: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    orders = orders.copy()

    orders["quantity"] = pd.to_numeric(
        orders["quantity"],
        errors="coerce"
    )

    orders["unit_price"] = pd.to_numeric(
        orders["unit_price"],
        errors="coerce"
    )

    duplicate_mask = (
        orders["order_id"].notna()
        & orders["order_id"].duplicated(keep=False)
    )

    duplicate_ids = set(
        orders.loc[duplicate_mask, "order_id"]
    )

    orders["rejection_reason"] = orders.apply(
        lambda row: get_rejection_reason(row, duplicate_ids),
        axis=1
    )

    invalid_mask = orders["rejection_reason"].ne("")

    valid_orders = orders.loc[~invalid_mask].copy()
    rejected_orders = orders.loc[invalid_mask].copy()

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
        .sort_values(["order_date", "customer_country"])
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
