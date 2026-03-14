"""Backward-compatible wrappers around the new extraction module."""

from data_extractor import extract_parameters


def extract_from_text(raw_text):
    data = extract_parameters(raw_text)
    return [{"name": k, "value": v} for k, v in data.items()]


def extract_from_json(json_data):
    data = extract_parameters(json_data)
    return [{"name": k, "value": v} for k, v in data.items()]
