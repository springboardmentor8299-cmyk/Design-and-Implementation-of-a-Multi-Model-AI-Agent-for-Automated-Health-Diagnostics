export interface ReferenceRange {
  parameter: string;
  unit: string;
  male: { low: number; high: number };
  female: { low: number; high: number };
  ageAdjustment?: (age: number) => { low: number; high: number } | null;
}

export const referenceRanges: Record<string, ReferenceRange> = {
  hemoglobin: {
    parameter: "Hemoglobin",
    unit: "g/dL",
    male: { low: 13.5, high: 17.5 },
    female: { low: 12.0, high: 15.5 },
  },
  glucose: {
    parameter: "Glucose (Fasting)",
    unit: "mg/dL",
    male: { low: 70, high: 100 },
    female: { low: 70, high: 100 },
  },
  totalCholesterol: {
    parameter: "Total Cholesterol",
    unit: "mg/dL",
    male: { low: 125, high: 200 },
    female: { low: 125, high: 200 },
  },
  hdl: {
    parameter: "HDL Cholesterol",
    unit: "mg/dL",
    male: { low: 40, high: 60 },
    female: { low: 50, high: 60 },
  },
  ldl: {
    parameter: "LDL Cholesterol",
    unit: "mg/dL",
    male: { low: 0, high: 100 },
    female: { low: 0, high: 100 },
  },
  triglycerides: {
    parameter: "Triglycerides",
    unit: "mg/dL",
    male: { low: 0, high: 150 },
    female: { low: 0, high: 150 },
  },
  creatinine: {
    parameter: "Creatinine",
    unit: "mg/dL",
    male: { low: 0.7, high: 1.3 },
    female: { low: 0.6, high: 1.1 },
    ageAdjustment: (age: number) => {
      if (age > 60) return { low: 0.8, high: 1.5 };
      return null;
    },
  },
  ast: {
    parameter: "AST (SGOT)",
    unit: "U/L",
    male: { low: 10, high: 40 },
    female: { low: 9, high: 32 },
  },
  alt: {
    parameter: "ALT (SGPT)",
    unit: "U/L",
    male: { low: 7, high: 56 },
    female: { low: 7, high: 45 },
  },
  mcv: {
    parameter: "MCV",
    unit: "fL",
    male: { low: 80, high: 100 },
    female: { low: 80, high: 100 },
  },
  wbc: {
    parameter: "WBC Count",
    unit: "×10³/µL",
    male: { low: 4.5, high: 11.0 },
    female: { low: 4.5, high: 11.0 },
  },
  platelets: {
    parameter: "Platelet Count",
    unit: "×10³/µL",
    male: { low: 150, high: 400 },
    female: { low: 150, high: 400 },
  },
};

export const unitConversions: Record<string, { from: string; to: string; factor: number }[]> = {
  glucose: [{ from: "mmol/L", to: "mg/dL", factor: 18.018 }],
  creatinine: [{ from: "µmol/L", to: "mg/dL", factor: 0.0113 }],
  totalCholesterol: [{ from: "mmol/L", to: "mg/dL", factor: 38.67 }],
  hdl: [{ from: "mmol/L", to: "mg/dL", factor: 38.67 }],
  ldl: [{ from: "mmol/L", to: "mg/dL", factor: 38.67 }],
  triglycerides: [{ from: "mmol/L", to: "mg/dL", factor: 88.57 }],
};
