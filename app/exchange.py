from __future__ import annotations

from typing import Any


def validate_exchange_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Ответ должен быть в формате JSON")

    result = payload.get("result")
    if result != "success":
        raise ValueError(f"Статус ответа = {result!r}")

    time_last_update_unix = payload.get("time_last_update_unix")
    if not isinstance(time_last_update_unix, int):
        raise ValueError("time_last_update_unix должен быть целым числом")

    base_code = payload.get("base_code")
    if not isinstance(base_code, str) or not base_code:
        raise ValueError("base_code должен быть string")

    conversion_rates = payload.get("conversion_rates")
    if not isinstance(conversion_rates, dict) or not conversion_rates:
        raise ValueError("conversion_rates должен быть словарем")
    for currency_code, rate in conversion_rates.items():
        if not isinstance(currency_code, str) or not currency_code:
            raise ValueError("Ключи conversion_rates должны быть непустыми строками")
        if not isinstance(rate, (int, float)) or isinstance(rate, bool):
            raise ValueError("Значения conversion_rates должны быть числами")

    return {
        "result": result,
        "time_last_update_unix": time_last_update_unix,
        "base_code": base_code,
        "conversion_rates": conversion_rates,
    }
