from utils.standard_ranges import ALIASES, STANDARD_RANGES


def _canonical_name(name):
    return ALIASES.get(name, name)


def validate_data(data):
    clean_data = {}

    for key, value in data.items():
        canonical_key = _canonical_name(key)

        if canonical_key not in STANDARD_RANGES:
            continue

        if not isinstance(value, (int, float)):
            continue

        value = _normalize_value(canonical_key, float(value))

        low, high = STANDARD_RANGES[canonical_key]
        hard_max = max(10000.0, high * 5)
        if value <= 0 or value >= hard_max:
            continue

        clean_data[canonical_key] = float(value)

    return clean_data


def _normalize_value(param, value):
    # Many reports express these in K/uL; convert to absolute counts.
    if param in {"WBC", "Platelets"} and value < 1000:
        return value * 1000.0
    return value
