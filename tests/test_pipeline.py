import pandas as pd
import pytest

from main import calculate_daily_revenue, validate_orders

def test_calculate_daily_revenue():
    orders = pd.DataFrame(
        [
            {
                "order_id": 1,
                "order_date": pd.Timestamp("2026-01-01"),
                "product": "Keyboard",
                "quantity": 2,
                "unit_price": 50.00,
                "status": "Completed",
                "customer_country": "Greece"
            },
            {
                "order_id": 2,
                "order_date": pd.Timestamp("2026-01-01"),
                "product": "Mouse",
                "quantity": 1,
                "unit_price": 25.00,
                "status": "Cancelled",
                "customer_country": "Greece"

            },
        ]
    )

    result = calculate_daily_revenue(orders)

    assert len(result) == 1
    assert result.iloc[0]["revenue"] == pytest.approx(100.00)


def test_reject_negative_quantity():
    orders = pd.DataFrame(
        [
            {
                "order_id": 1,
                "order_date": pd.Timestamp("2026-01-01"),
                "product": "Monitor",
                "quantity": -1,
                "unit_price": 200.00,
                "status": "Completed",
                "customer_country": "Greece"

            }
        ]
    )

    valid, rejected = validate_orders(orders)

    assert valid.empty
    assert len(rejected) == 1
    assert "quantity_must_be_positive" in rejected.iloc[0]["rejection_reason"]

def test_rejects_every_occurrence_of_duplicate_id():
    orders = pd.DataFrame(
        [
            {
                "order_id": 1,
                "order_date": pd.Timestamp("2026-01-01"),
                "product": "Keyboard",
                "quantity": 1,
                "unit_price": 50.00,
                "status": "Completed",
                "customer_country": "Greece"

            },
            {
                "order_id": 1,
                "order_date": pd.Timestamp("2026-01-02"),
                "product": "Mouse",
                "quantity": 2,
                "unit_price": 25.00,
                "status": "Completed",
                "customer_country": "Greece"
            },
            {
                "order_id": 2,
                "order_date": pd.Timestamp("2026-01-03"),
                "product": "Monitor",
                "quantity": 1,
                "unit_price": 200.00,
                "status": "Completed",
                "customer_country": "Greece"
            },
        ]
    )

    valid, rejected = validate_orders(orders)

    assert valid["order_id"].tolist() == [2]
    assert rejected["order_id"].tolist() == [1, 1]
    assert all(
        reason == "duplicate_order_id"
        for reason in rejected["rejection_reason"]
    )
