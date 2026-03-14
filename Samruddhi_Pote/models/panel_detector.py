from utils.test_panels import TEST_PANELS


def detect_test_panels(data):
    """Detect which test panels are represented in the extracted data.

    Args:
        data: Dict mapping canonical parameter name -> numeric value.

    Returns:
        Dict of detected panels with present/missing parameter lists.
    """

    detected = {}

    for panel, parameters in TEST_PANELS.items():
        present = [p for p in parameters if p in data]

        if present:
            detected[panel] = {
                "parameters_present": present,
                "parameters_missing": [p for p in parameters if p not in data],
            }

    return detected

