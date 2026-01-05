# Week4/contextual_analysis.py

import csv
import os


def contextual_analysis(
    patient_id: str,
    age: int,
    gender: str,
    validated_params: dict,
    pattern_result: dict
) -> dict:
    """
    Model 3: Contextual Analysis (Age & Gender based)
    Aggressive risk interpretation
    """

    gender = gender.lower().strip()
    context_score = 0
    flags = []
    notes = []

    # -------- Age-based risk modifier --------
    if age < 30:
        age_modifier = 0
    elif 30 <= age <= 45:
        age_modifier = 1
        flags.append("early_age_risk")
    elif 46 <= age <= 60:
        age_modifier = 2
        flags.append("mid_age_risk")
    else:
        age_modifier = 3
        flags.append("high_age_risk")

    context_score += age_modifier

    # -------- Gender-based risk modifier --------
    lipid_abnormal = any(
        p in validated_params and validated_params[p]["status"] == "valid"
        for p in ["ldl_cholesterol", "triglycerides"]
    )

    if gender == "male" and lipid_abnormal:
        context_score += 1
        flags.append("male_lipid_penalty")
        notes.append("Male patient with lipid abnormality → aggressive cardiac risk")

    if gender == "female":
        hdl = validated_params.get("hdl_cholesterol")
        if hdl and hdl["value"] < 50:
            context_score += 1
            flags.append("female_low_hdl")
            notes.append("Low HDL in female patient → increased cardiac concern")

    # -------- Glucose + Age interaction --------
    glucose = validated_params.get("glucose")
    if glucose:
        if age >= 35 and glucose["value"] >= 100:
            context_score += 1
            flags.append("age_glucose_risk")
            notes.append("Age-adjusted glucose risk detected")

    # -------- Thyroid (Aggressive mode) --------
    tsh = validated_params.get("tsh")
    if tsh and (tsh["value"] < 0.4 or tsh["value"] > 4.5):
        context_score += 1
        flags.append("thyroid_monitoring_required")
        notes.append("Aggressive thyroid monitoring applied")

    # -------- Combine with Pattern Risk --------
    pattern_score = pattern_result.get("pattern_risk_score", 0)
    total_score = context_score + pattern_score

    return {
        "patient_id": patient_id,
        "age": age,
        "gender": gender,
        "context_score": context_score,
        "pattern_score": pattern_score,
        "final_contextual_risk_score": total_score,
        "flags": flags,
        "notes": notes
    }


def save_contextual_analysis_to_csv(patient_id: str, result: dict):
    os.makedirs("outputs/contextual", exist_ok=True)
    path = "outputs/contextual/contextual_analysis.csv"

    file_exists = os.path.isfile(path)

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "patient_id",
                "age",
                "gender",
                "context_score",
                "pattern_score",
                "final_contextual_risk_score",
                "flags",
                "notes"
            ])

        writer.writerow([
            patient_id,
            result["age"],
            result["gender"],
            result["context_score"],
            result["pattern_score"],
            result["final_contextual_risk_score"],
            "; ".join(result["flags"]),
            "; ".join(result["notes"])
        ])
