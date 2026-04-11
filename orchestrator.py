from model1 import interpret_parameters
from model2 import detect_health_patterns
from model3 import apply_context   # (you added this)
from synthesis import synthesize_findings
from recommendations import generate_recommendations
from severity import get_severity
from model3 import apply_context   # NEW

def run_pipeline(data):

    analysis = interpret_parameters(data)
    risks = detect_health_patterns(data)

    # ⭐ APPLY CONTEXT MODEL
    risks = apply_context(data, risks)

    severity = get_severity(risks)
    summary = synthesize_findings(analysis, risks)
    recommendations = generate_recommendations(risks, data)

    return {
        "analysis": analysis,
        "risks": risks,
        "severity": severity,
        "summary": summary,
        "recommendations": recommendations
    }