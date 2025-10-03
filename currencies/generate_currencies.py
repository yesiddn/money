# generate_currencies.py
import json
from iso4217 import Currency as ISO_Currency


def generate_currency_fixture():
    currencies = []

    for currency in ISO_Currency:
        currencies.append(
            {
                "model": "currencies.currency",
                "pk": currency.code,
                "fields": {
                    "name": currency.currency_name,
                    "numeric_code": str(currency.number).zfill(3),
                    "minor_unit": currency.exponent if currency.exponent is not None else 0,
                    "is_active": True,
                },
            }
        )

    with open("currencies/fixtures/currencies.json", "w", encoding="utf-8") as f:
        json.dump(currencies, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(currencies)} currencies")


if __name__ == "__main__":
    generate_currency_fixture()
