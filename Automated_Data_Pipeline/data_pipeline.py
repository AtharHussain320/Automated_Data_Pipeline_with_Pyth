import csv
from pathlib import Path
from datetime import datetime


INPUT_FILE = Path("raw_sales.csv")
CLEAN_FILE = Path("clean_sales.csv")
ERROR_FILE = Path("error_log.csv")


REQUIRED_COLUMNS = [
    "order_id",
    "customer",
    "product",
    "category",
    "quantity",
    "unit_price",
    "city"
]



# FILE READING

def read_csv_file(filename):
    """Read CSV data and return records."""

    try:

        with open(
            filename,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames:
                raise ValueError(
                    "CSV file does not contain headers."
                )

            missing = [
                column
                for column in REQUIRED_COLUMNS
                if column not in reader.fieldnames
            ]

            if missing:
                raise ValueError(
                    f"Missing columns: {', '.join(missing)}"
                )

            return list(reader)

    except FileNotFoundError:

        print(
            f"Error: {filename} was not found."
        )

    except PermissionError:

        print(
            f"Error: permission denied for {filename}."
        )

    except OSError as error:

        print(
            f"File error: {error}"
        )

    except ValueError as error:

        print(
            f"Data format error: {error}"
        )

    return []



# DATA VALIDATION

def validate_record(record):
    """Validate one raw record."""

    errors = []

    if not record.get("order_id", "").strip():
        errors.append("Missing order ID")

    if not record.get("customer", "").strip():
        errors.append("Missing customer name")

    if not record.get("product", "").strip():
        errors.append("Missing product name")

    if not record.get("category", "").strip():
        errors.append("Missing category")

    if not record.get("city", "").strip():
        errors.append("Missing city")

    try:

        quantity = int(record["quantity"])

        if quantity <= 0:
            errors.append(
                "Quantity must be greater than zero"
            )

    except (ValueError, TypeError, KeyError):

        errors.append("Invalid quantity")

    try:

        price = float(record["unit_price"])

        if price <= 0:
            errors.append(
                "Unit price must be greater than zero"
            )

    except (ValueError, TypeError, KeyError):

        errors.append("Invalid unit price")

    return errors



# DATA CLEANING +TRANSFORMATION

def clean_record(record):
    """Clean and transform a valid record."""

    customer = " ".join(
        record["customer"].strip().split()
    )

    product = " ".join(
        record["product"].strip().split()
    )

    category = record["category"].strip().title()

    city = record["city"].strip().title()

    quantity = int(
        record["quantity"].strip()
    )

    unit_price = round(
        float(record["unit_price"].strip()),
        2
    )

    total_amount = round(
        quantity * unit_price,
        2
    )

    return {
        "order_id": record["order_id"].strip(),
        "customer": customer,
        "product": product,
        "category": category,
        "quantity": quantity,
        "unit_price": unit_price,
        "total_amount": total_amount,
        "city": city
    }



# PIPELINE PROCESSING

def process_records(records):
    """Validate and transform all records."""

    clean_records = []
    errors = []

    for row_number, record in enumerate(
        records,
        start=2
    ):

        validation_errors = validate_record(
            record
        )

        if validation_errors:

            errors.append({
                "row": row_number,
                "order_id": record.get(
                    "order_id",
                    ""
                ),
                "reason": "; ".join(
                    validation_errors
                ),
                "timestamp": datetime.now().isoformat(
                    timespec="seconds"
                )
            })

            continue

        try:

            cleaned = clean_record(record)

            clean_records.append(cleaned)

        except (ValueError, TypeError, KeyError) as error:

            errors.append({
                "row": row_number,
                "order_id": record.get(
                    "order_id",
                    ""
                ),
                "reason": f"Transformation error: {error}",
                "timestamp": datetime.now().isoformat(
                    timespec="seconds"
                )
            })

    return clean_records, errors



# STATISTICS

def calculate_statistics(records):
    """Generate summary statistics."""

    if not records:

        return {
            "records": 0,
            "units": 0,
            "sales": 0,
            "categories": 0,
            "cities": 0
        }

    total_units = sum(
        record["quantity"]
        for record in records
    )

    total_sales = sum(
        record["total_amount"]
        for record in records
    )

    categories = {
        record["category"]
        for record in records
    }

    cities = {
        record["city"]
        for record in records
    }

    return {
        "records": len(records),
        "units": total_units,
        "sales": round(total_sales, 2),
        "categories": len(categories),
        "cities": len(cities)
    }


def category_sales(records):
    """Calculate sales by category."""

    summary = {}

    for record in records:

        category = record["category"]

        summary[category] = (
            summary.get(category, 0)
            + record["total_amount"]
        )

    return summary



# CSV EXPORT

def write_clean_data(records):
    """Export clean records."""

    if not records:
        return False

    fields = [
        "order_id",
        "customer",
        "product",
        "category",
        "quantity",
        "unit_price",
        "total_amount",
        "city"
    ]

    try:

        with open(
            CLEAN_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fields
            )

            writer.writeheader()
            writer.writerows(records)

        return True

    except OSError as error:

        print(
            f"Unable to write clean dataset: {error}"
        )

        return False


def write_error_log(errors):
    """Export rejected records to an error log."""

    fields = [
        "row",
        "order_id",
        "reason",
        "timestamp"
    ]

    try:

        with open(
            ERROR_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fields
            )

            writer.writeheader()
            writer.writerows(errors)

        return True

    except OSError as error:

        print(
            f"Unable to write error log: {error}"
        )

        return False



# REPORTING

def display_report(
    statistics,
    category_summary,
    total_raw,
    total_errors
):
    """Display final pipeline report."""

    print("\n" + "=" * 60)
    print("             PIPELINE SUMMARY")
    print("=" * 60)

    print(
        f"Raw records       : {total_raw}"
    )

    print(
        f"Valid records     : {statistics['records']}"
    )

    print(
        f"Rejected records  : {total_errors}"
    )

    print(
        f"Total units       : {statistics['units']}"
    )

    print(
        f"Total sales       : "
        f"Rs. {statistics['sales']:,.2f}"
    )

    print(
        f"Categories        : "
        f"{statistics['categories']}"
    )

    print(
        f"Cities            : "
        f"{statistics['cities']}"
    )

    print("\nSales by Category")
    print("-" * 60)

    for category, amount in sorted(
        category_summary.items(),
        key=lambda item: item[1],
        reverse=True
    ):

        print(
            f"{category:<20}"
            f"Rs. {amount:>12,.2f}"
        )

    print("=" * 60)



# MAIN PIPELINE

def main():

    print("\n" + "=" * 60)
    print("          AUTOMATED DATA PIPELINE")
    print("=" * 60)

    print("\n[1/5] Reading raw data...")

    raw_records = read_csv_file(
        INPUT_FILE
    )

    if not raw_records:

        print(
            "Pipeline stopped: no input data available."
        )

        return

    print(
        f"✓ Loaded {len(raw_records)} records."
    )

    print("\n[2/5] Validating and cleaning records...")

    clean_records, errors = process_records(
        raw_records
    )

    print(
        f"✓ Valid records: {len(clean_records)}"
    )

    print(
        f"⚠ Rejected records: {len(errors)}"
    )

    print("\n[3/5] Calculating statistics...")

    statistics = calculate_statistics(
        clean_records
    )

    category_summary = category_sales(
        clean_records
    )

    print("✓ Statistics generated.")

    print("\n[4/5] Exporting clean dataset...")

    if write_clean_data(clean_records):

        print(
            f"✓ Clean data saved to {CLEAN_FILE}"
        )

    print("\n[5/5] Writing error log...")

    if write_error_log(errors):

        print(
            f"✓ Error log saved to {ERROR_FILE}"
        )

    display_report(
        statistics,
        category_summary,
        len(raw_records),
        len(errors)
    )

    print(
        "\n✓ Data pipeline completed successfully."
    )


if __name__ == "__main__":
    main()