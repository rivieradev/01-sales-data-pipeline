# Sales Data Pipeline

A small Python ETL project that reads sales orders from CSV, validates each record, separates rejected rows, and calculates daily revenue by country.

## What it does

- Loads orders from `data/input/orders.csv`
- Rejects records with missing or invalid values
- Rejects every occurrence of a duplicate `order_id`
- Saves valid and rejected records separately
- Calculates completed-order revenue by date and customer country

Generated files are written to `data/output/`:

- `valid_orders.csv`
- `rejected_orders.csv`
- `daily_revenue.csv`

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Installation

Clone the repository and install its dependencies:

```bash
git clone https://github.com/YOUR_USERNAME/01-sales-data-pipeline.git
cd 01-sales-data-pipeline
uv sync
```

Place the input file at:

```text
data/input/orders.csv
```

## Run the pipeline

```bash
uv run python main.py
```

The command prints a revenue summary and writes the output CSV files to `data/output/`.

## Run the tests

```bash
uv run pytest -v
```

The tests check revenue calculations, invalid quantities, and duplicate order handling.
