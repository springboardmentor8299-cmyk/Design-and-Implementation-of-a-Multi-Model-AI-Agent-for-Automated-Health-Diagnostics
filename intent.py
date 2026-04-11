def detect_intent(user_input):
    text = user_input.lower()

    if "diabetes" in text and ("why" in text or "reason" in text):
        return "cause_diabetes"

    elif any(word in text for word in ["reduce", "control", "prevent"]):
        return "reduce_diabetes"

    elif any(word in text for word in ["eat", "diet", "food"]):
        return "diet"

    return "general"