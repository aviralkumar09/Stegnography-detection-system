def evaluate_decision(results: list[dict]) -> dict:
    weights = {
        "chi_square": 0.15,
        "rs_analysis": 0.15,
        "histogram": 0.1,
        "texture": 0.1,
        "transform": 0.15,
        "ai_detection": 0.2,
        "anomaly": 0.15,
    }
    risk = sum(item["score"] * weights.get(item["module"], 0.0) for item in results)
    if risk >= 0.7:
        risk_level, classification = "high", "suspicious"
    elif risk >= 0.45:
        risk_level, classification = "medium", "suspicious"
    else:
        risk_level, classification = "low", "benign"
    summary = (
        "Potential steganographic indicators detected across multiple modules."
        if classification == "suspicious"
        else "No strong steganographic indicators detected."
    )
    return {
        "risk_score": round(float(risk), 4),
        "risk_level": risk_level,
        "classification": classification,
        "summary": summary,
    }
