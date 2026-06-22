import pandas as pd
import uuid

df = pd.read_csv("data/catalogue.csv")


def check_stock(sku):
    product = df[df["sku"] == sku]

    if product.empty:
        return {
            "error": "SKU not found"
        }

    return {
        "sku": sku,
        "stock": int(product.iloc[0]["stock"])
    }


def find_parts_by_vehicle(vehicle_name):
    results = df[
        df["vehicle_fitment"]
        .str.contains(vehicle_name, case=False, na=False)
    ]

    return results[
        [
            "sku",
            "name",
            "brand",
            "price_inr",
            "stock"
        ]
    ].to_dict(orient="records")


def create_order(dealer_name, line_items):
    return {
        "order_id": str(uuid.uuid4())[:8],
        "dealer": dealer_name,
        "items": line_items,
        "status": "created"
    }


if __name__ == "__main__":

    print(check_stock("BRK-1002"))

    parts = find_parts_by_vehicle(
        "Bajaj Pulsar 150"
    )

    print(parts[:3])

    order = create_order(
        "ABC Motors",
        [
            {
                "sku": "BRK-1002",
                "quantity": 10
            }
        ]
    )

    print(order)
#python assistant/tools.py