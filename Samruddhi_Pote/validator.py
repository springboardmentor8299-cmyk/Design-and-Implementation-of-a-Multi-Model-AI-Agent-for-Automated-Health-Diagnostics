"""Backward-compatible wrapper for validation output."""

from data_validator import validate_data
from utils.standard_ranges import STANDARD_RANGES, UNITS


def validate_and_standardize(extracted_data):
    if isinstance(extracted_data, list):
        as_dict = {item["name"]: item["value"] for item in extracted_data if "name" in item and "value" in item}
    elif isinstance(extracted_data, dict):
        as_dict = extracted_data
    else:
        as_dict = {}

    clean = validate_data(as_dict)

    result = []
    for name, value in clean.items():
        rmin, rmax = STANDARD_RANGES[name]
        result.append(
            {
                "name": name,
                "value": value,
                "unit": UNITS.get(name, ""),
                "reference_min": rmin,
                "reference_max": rmax,
            }
        )
    return result
