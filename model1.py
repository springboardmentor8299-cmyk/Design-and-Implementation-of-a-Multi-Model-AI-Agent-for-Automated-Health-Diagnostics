from ranges import REFERENCE_RANGES

def interpret_parameters(params: dict):

    results = {}

    for name, value in params.items():

        if value is None:
            continue

        if name not in REFERENCE_RANGES:
            continue

        low, high = REFERENCE_RANGES[name]

        if value < low:
            status = "LOW"
        elif value > high:
            status = "HIGH"
        else:
            status = "NORMAL"

        results[name] = {
            "value": value,
            "status": status,
            "range": f"{low}-{high}"
        }

    return results
