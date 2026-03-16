import { referenceRanges } from "./referenceRanges";

export type Classification = "low" | "normal" | "high";
export type Severity = "low" | "moderate" | "high";

export interface PatientInfo {
  age?: number;
  gender?: "male" | "female" | "other";
  medicalHistory?: string[];
}

export interface BloodParameter {
  key: string;
  name: string;
  value: number;
  unit: string;
  referenceRange: { low: number; high: number };
  classification: Classification;
}

export interface ClinicalPattern {
  id: string;
  name: string;
  description: string;
  severity: Severity;
  parameters: string[];
  details: string;
}

export interface RiskScore {
  name: string;
  value: number | string;
  interpretation: string;
  severity: Severity;
}

export interface Recommendation {
  text: string;
  category: "diet" | "exercise" | "lifestyle" | "medical";
  source: string;
  priority: Severity;
}

export interface AnalysisResult {
  parameters: BloodParameter[];
  patterns: ClinicalPattern[];
  riskScores: RiskScore[];
  recommendations: Recommendation[];
  summary: string;
  patientInfo: PatientInfo;
  timestamp: string;
}

function classifyParameter(
  value: number,
  range: { low: number; high: number }
): Classification {
  if (value < range.low) return "low";
  if (value > range.high) return "high";
  return "normal";
}

function getRangeForPatient(
  key: string,
  gender: "male" | "female" | "other",
  age?: number
): { low: number; high: number } {
  const ref = referenceRanges[key];
  if (!ref) return { low: 0, high: 999 };

  const g = gender === "other" ? "male" : gender;
  let range = { ...ref[g] };

  if (age && ref.ageAdjustment) {
    const adjusted = ref.ageAdjustment(age);
    if (adjusted) range = adjusted;
  }
  return range;
}

export function classifyAllParameters(
  values: Record<string, number>,
  patient: PatientInfo
): BloodParameter[] {
  const gender = patient.gender || "male";
  return Object.entries(values)
    .filter(([key]) => referenceRanges[key])
    .map(([key, value]) => {
      const ref = referenceRanges[key];
      const range = getRangeForPatient(key, gender, patient.age);
      return {
        key,
        name: ref.parameter,
        value,
        unit: ref.unit,
        referenceRange: range,
        classification: classifyParameter(value, range),
      };
    });
}

export function detectPatterns(
  params: BloodParameter[],
  patient: PatientInfo
): ClinicalPattern[] {
  const patterns: ClinicalPattern[] = [];
  const get = (k: string) => params.find((p) => p.key === k);

  const glucose = get("glucose");
  const trig = get("triglycerides");
  const hdl = get("hdl");

  // Metabolic syndrome
  let metCount = 0;
  const metParams: string[] = [];
  if (glucose && glucose.value > 100) { metCount++; metParams.push("Glucose"); }
  if (trig && trig.value > 150) { metCount++; metParams.push("Triglycerides"); }
  if (hdl) {
    const threshold = patient.gender === "female" ? 50 : 40;
    if (hdl.value < threshold) { metCount++; metParams.push("HDL"); }
  }
  if (metCount >= 2) {
    patterns.push({
      id: "metabolic_syndrome",
      name: "Metabolic Syndrome Risk",
      description: `${metCount} of 3 measurable criteria met. Additional factors (blood pressure, waist circumference) not available.`,
      severity: metCount >= 3 ? "high" : "moderate",
      parameters: metParams,
      details: "Metabolic syndrome increases risk of heart disease, stroke, and type 2 diabetes.",
    });
  }

  // Cardiovascular risk
  const totalChol = get("totalCholesterol");
  const ldl = get("ldl");
  if (totalChol && hdl && hdl.value > 0) {
    const ratio = totalChol.value / hdl.value;
    const ldlHdlRatio = ldl && hdl.value > 0 ? ldl.value / hdl.value : null;
    let severity: Severity = "low";
    if (ratio > 5) severity = "high";
    else if (ratio > 4) severity = "moderate";
    patterns.push({
      id: "cardiovascular",
      name: "Cardiovascular Risk Assessment",
      description: `Total/HDL ratio: ${ratio.toFixed(1)}${ldlHdlRatio ? `, LDL/HDL ratio: ${ldlHdlRatio.toFixed(1)}` : ""}`,
      severity,
      parameters: ["Total Cholesterol", "HDL", ...(ldl ? ["LDL"] : [])],
      details: ratio > 5 ? "High cardiovascular risk. Consult a cardiologist." : ratio > 4 ? "Moderate risk. Lifestyle changes recommended." : "Low cardiovascular risk.",
    });
  }

  // Kidney function (eGFR)
  const creatinine = get("creatinine");
  if (creatinine && patient.age && patient.gender && patient.gender !== "other") {
    const isFemale = patient.gender === "female";
    const kappa = isFemale ? 0.7 : 0.9;
    const alpha = isFemale ? -0.329 : -0.411;
    const scrOverK = creatinine.value / kappa;
    const minVal = Math.min(scrOverK, 1);
    const maxVal = Math.max(scrOverK, 1);
    let eGFR = 141 * Math.pow(minVal, alpha) * Math.pow(maxVal, -1.209) * Math.pow(0.993, patient.age);
    if (isFemale) eGFR *= 1.018;

    let severity: Severity = "low";
    let interp = `eGFR: ${eGFR.toFixed(0)} mL/min/1.73m² — Normal kidney function`;
    if (eGFR < 60) { severity = "high"; interp = `eGFR: ${eGFR.toFixed(0)} mL/min/1.73m² — Reduced kidney function (Stage 3+)`; }
    else if (eGFR < 90) { severity = "moderate"; interp = `eGFR: ${eGFR.toFixed(0)} mL/min/1.73m² — Mildly reduced kidney function`; }

    patterns.push({
      id: "kidney",
      name: "Kidney Function (CKD-EPI)",
      description: interp,
      severity,
      parameters: ["Creatinine"],
      details: "Estimated Glomerular Filtration Rate calculated using the CKD-EPI formula.",
    });
  }

  // Liver function
  const ast = get("ast");
  const alt = get("alt");
  if (ast && alt && alt.value > 0) {
    const ratio = ast.value / alt.value;
    if (ratio > 2) {
      patterns.push({
        id: "liver_alcoholic",
        name: "Liver Function — Elevated AST/ALT Ratio",
        description: `AST/ALT ratio: ${ratio.toFixed(1)} (>2 may suggest alcoholic liver disease)`,
        severity: "high",
        parameters: ["AST", "ALT"],
        details: "An AST/ALT ratio greater than 2 is commonly associated with alcoholic hepatitis.",
      });
    } else if (ast.classification === "high" || alt.classification === "high") {
      patterns.push({
        id: "liver_elevated",
        name: "Liver Enzymes Elevated",
        description: `AST/ALT ratio: ${ratio.toFixed(1)}. One or more liver enzymes above normal.`,
        severity: "moderate",
        parameters: ["AST", "ALT"],
        details: "Elevated liver enzymes may indicate liver inflammation or damage.",
      });
    }
  }

  // Anemia
  const hb = get("hemoglobin");
  const mcv = get("mcv");
  if (hb && hb.classification === "low") {
    if (mcv) {
      if (mcv.value < 80) {
        patterns.push({ id: "anemia_iron", name: "Microcytic Anemia Pattern", description: "Low hemoglobin with low MCV suggests iron deficiency anemia.", severity: "high", parameters: ["Hemoglobin", "MCV"], details: "Consider iron studies and dietary assessment." });
      } else if (mcv.value > 100) {
        patterns.push({ id: "anemia_b12", name: "Macrocytic Anemia Pattern", description: "Low hemoglobin with high MCV suggests B12/folate deficiency.", severity: "high", parameters: ["Hemoglobin", "MCV"], details: "Consider B12 and folate levels." });
      } else {
        patterns.push({ id: "anemia_normo", name: "Normocytic Anemia", description: "Low hemoglobin with normal MCV. May indicate chronic disease or blood loss.", severity: "moderate", parameters: ["Hemoglobin", "MCV"], details: "Further evaluation recommended." });
      }
    } else {
      patterns.push({ id: "anemia_simple", name: "Low Hemoglobin Detected", description: "Hemoglobin is below normal range. MCV not available for further classification.", severity: "moderate", parameters: ["Hemoglobin"], details: "Consider complete blood count with MCV for anemia classification." });
    }
  }

  return patterns;
}

export function calculateRiskScores(
  params: BloodParameter[],
  patient: PatientInfo
): RiskScore[] {
  const scores: RiskScore[] = [];
  const get = (k: string) => params.find((p) => p.key === k);

  const totalChol = get("totalCholesterol");
  const hdl = get("hdl");

  if (totalChol && hdl && hdl.value > 0) {
    const ratio = totalChol.value / hdl.value;
    scores.push({
      name: "Total Cholesterol / HDL Ratio",
      value: ratio.toFixed(1),
      interpretation: ratio < 3.5 ? "Optimal" : ratio < 5 ? "Borderline" : "High Risk",
      severity: ratio < 3.5 ? "low" : ratio < 5 ? "moderate" : "high",
    });
  }

  const abnormalCount = params.filter((p) => p.classification !== "normal").length;
  const healthScore = Math.max(0, 100 - abnormalCount * 12);
  scores.push({
    name: "Overall Health Index",
    value: healthScore,
    interpretation: healthScore >= 80 ? "Good" : healthScore >= 50 ? "Needs Attention" : "Requires Medical Review",
    severity: healthScore >= 80 ? "low" : healthScore >= 50 ? "moderate" : "high",
  });

  return scores;
}

export function generateRecommendations(
  params: BloodParameter[],
  patterns: ClinicalPattern[],
  patient: PatientInfo
): Recommendation[] {
  const recs: Recommendation[] = [];
  const get = (k: string) => params.find((p) => p.key === k);

  const glucose = get("glucose");
  if (glucose && glucose.classification === "high") {
    recs.push({ text: "Reduce refined sugar and simple carbohydrate intake. Consider whole grains and complex carbs.", category: "diet", source: "High Glucose", priority: "high" });
    recs.push({ text: "Engage in at least 150 minutes of moderate aerobic exercise per week to help regulate blood sugar.", category: "exercise", source: "High Glucose", priority: "moderate" });
  }

  const chol = get("totalCholesterol");
  const ldl = get("ldl");
  if ((chol && chol.classification === "high") || (ldl && ldl.classification === "high")) {
    recs.push({ text: "Increase intake of omega-3 fatty acids (fish, flaxseed). Reduce saturated and trans fats.", category: "diet", source: "High Cholesterol/LDL", priority: "high" });
  }

  const trig = get("triglycerides");
  if (trig && trig.classification === "high") {
    recs.push({ text: "Limit alcohol consumption and reduce sugar intake. Increase fiber-rich foods.", category: "diet", source: "High Triglycerides", priority: "moderate" });
  }

  const hb = get("hemoglobin");
  if (hb && hb.classification === "low") {
    recs.push({ text: "Include iron-rich foods (lean red meat, spinach, lentils) and vitamin C to aid absorption.", category: "diet", source: "Low Hemoglobin", priority: "high" });
  }

  if (patterns.some((p) => p.id === "metabolic_syndrome")) {
    recs.push({ text: "Consult an endocrinologist for comprehensive metabolic syndrome evaluation.", category: "medical", source: "Metabolic Syndrome Risk", priority: "high" });
  }

  if (patterns.some((p) => p.id.startsWith("kidney") && p.severity !== "low")) {
    recs.push({ text: "Stay well-hydrated. Limit sodium and protein intake. Follow up with a nephrologist.", category: "lifestyle", source: "Kidney Function Concern", priority: "high" });
  }

  if (patient.medicalHistory?.includes("diabetes")) {
    recs.push({ text: "Monitor HbA1c every 3 months. Maintain fasting glucose under 130 mg/dL as per diabetic guidelines.", category: "medical", source: "Known Diabetes", priority: "high" });
  }

  if (patient.medicalHistory?.includes("hypertension")) {
    recs.push({ text: "Follow DASH diet principles. Limit sodium to <2300 mg/day.", category: "diet", source: "Known Hypertension", priority: "moderate" });
  }

  // Always add disclaimer
  recs.push({ text: "These recommendations are AI-generated and should not replace professional medical advice. Consult your healthcare provider.", category: "medical", source: "Disclaimer", priority: "low" });

  return recs;
}

export function generateSummary(
  params: BloodParameter[],
  patterns: ClinicalPattern[],
  patient: PatientInfo
): string {
  const abnormal = params.filter((p) => p.classification !== "normal");
  const highSeverity = patterns.filter((p) => p.severity === "high");

  let summary = `Analysis of ${params.length} blood parameters completed. `;

  if (abnormal.length === 0) {
    summary += "All values are within normal ranges. ";
  } else {
    summary += `${abnormal.length} parameter${abnormal.length > 1 ? "s" : ""} outside normal range: ${abnormal.map((p) => `${p.name} (${p.classification})`).join(", ")}. `;
  }

  if (patterns.length > 0) {
    summary += `${patterns.length} clinical pattern${patterns.length > 1 ? "s" : ""} detected. `;
  }

  if (highSeverity.length > 0) {
    summary += `⚠️ ${highSeverity.length} high-severity finding${highSeverity.length > 1 ? "s" : ""} requiring attention: ${highSeverity.map((p) => p.name).join(", ")}.`;
  }

  return summary;
}

export function runFullAnalysis(
  values: Record<string, number>,
  patient: PatientInfo
): AnalysisResult {
  const parameters = classifyAllParameters(values, patient);
  const patterns = detectPatterns(parameters, patient);
  const riskScores = calculateRiskScores(parameters, patient);
  const recommendations = generateRecommendations(parameters, patterns, patient);
  const summary = generateSummary(parameters, patterns, patient);

  return {
    parameters,
    patterns,
    riskScores,
    recommendations,
    summary,
    patientInfo: patient,
    timestamp: new Date().toISOString(),
  };
}

// Sample reports for demo
export const sampleReports: { name: string; values: Record<string, number>; patient: PatientInfo }[] = [
  {
    name: "Sample: Male, 45, Pre-Diabetic",
    values: { hemoglobin: 14.2, glucose: 118, totalCholesterol: 230, hdl: 38, ldl: 145, triglycerides: 195, creatinine: 1.1, ast: 28, alt: 32, mcv: 88, wbc: 7.2, platelets: 250 },
    patient: { age: 45, gender: "male", medicalHistory: ["hypertension"] },
  },
  {
    name: "Sample: Female, 32, Anemic",
    values: { hemoglobin: 10.5, glucose: 85, totalCholesterol: 175, hdl: 58, ldl: 90, triglycerides: 110, creatinine: 0.7, ast: 22, alt: 18, mcv: 72, wbc: 6.1, platelets: 310 },
    patient: { age: 32, gender: "female", medicalHistory: [] },
  },
  {
    name: "Sample: Male, 60, Multi-Condition",
    values: { hemoglobin: 12.8, glucose: 145, totalCholesterol: 260, hdl: 35, ldl: 170, triglycerides: 280, creatinine: 1.6, ast: 55, alt: 22, mcv: 95, wbc: 9.8, platelets: 180 },
    patient: { age: 60, gender: "male", medicalHistory: ["diabetes", "hypertension"] },
  },
];
