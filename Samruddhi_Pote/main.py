import json
import sys

from data_extractor import extract_parameters
from data_validator import validate_data
from input_parser import parse_input
from models.panel_detector import detect_test_panels
from models.panel_interpreter import analyze_panels
from models.parameter_interpreter import interpret_parameters, interpret_severity
from models.pattern_analyzer import (
    calculate_health_risk,
    detect_patterns,
    generate_recommendations,
)
from utils.metadata_extractor import extract_patient_metadata, fill_missing_metadata


def run_pipeline(file_path, context=None):
    raw_input = parse_input(file_path)
    patient_metadata = extract_patient_metadata(raw_input)
    patient_metadata = fill_missing_metadata(
        patient_metadata,
        fallback_context=context or {},
        seed=file_path,
    )
    extracted = extract_parameters(raw_input)
    clean_data = validate_data(extracted)

    effective_context = dict(context or {})
    if patient_metadata.get("patient_name") and not effective_context.get("patient_name"):
        effective_context["patient_name"] = patient_metadata["patient_name"]
    if patient_metadata.get("age") and not effective_context.get("age"):
        effective_context["age"] = patient_metadata["age"]
    if patient_metadata.get("gender") and not effective_context.get("gender"):
        effective_context["gender"] = patient_metadata["gender"]

    interpretation = interpret_parameters(clean_data, context=effective_context)
    severity = interpret_severity(clean_data, context=effective_context)

    panels = detect_test_panels(clean_data)
    panel_results = analyze_panels(clean_data, panels)

    patterns = detect_patterns(clean_data, panels=panels)
    risk = calculate_health_risk(clean_data, panels=panels)
    recommendations = generate_recommendations(clean_data, interpretation)

    return {
        "values": clean_data,
        "interpretation": interpretation,
        "severity": severity,
        "patterns": patterns,
        "risk": risk,
        "panels": panels,
        "panel_results": panel_results,
        "recommendations": recommendations,
        "patient_metadata": patient_metadata,
        "patient_context": context or {},
        "effective_context": effective_context,
    }


def main(file_path):
    result = run_pipeline(file_path, context={})
    print("\n=== Milestone 2 Output ===\n")
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <file_path>")
    else:
        main(sys.argv[1])
