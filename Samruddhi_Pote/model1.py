"""Backward-compatible model classification using milestone 1 interpreter."""

from models.parameter_interpreter import classify_value


def run_model1(validated_data):
    output = []

    for item in validated_data:
        status = classify_value(item["name"], item["value"])
        result = dict(item)
        result["status"] = status
        output.append(result)

    return output
