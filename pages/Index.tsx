import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Activity, Beaker, ChevronRight, Sparkles, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import UploadZone from "@/components/UploadZone";
import { PatientInfo, sampleReports, runFullAnalysis } from "@/lib/bloodAnalysis";

const medicalConditions = ["diabetes", "hypertension", "thyroid disorder", "heart disease", "kidney disease", "liver disease"];

const Index = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [age, setAge] = useState("");
  const [gender, setGender] = useState<string>("");
  const [history, setHistory] = useState<string[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [manualMode, setManualMode] = useState(false);
  const [manualValues, setManualValues] = useState<Record<string, string>>({});

  const parameterKeys = [
    { key: "hemoglobin", label: "Hemoglobin (g/dL)" },
    { key: "glucose", label: "Glucose (mg/dL)" },
    { key: "totalCholesterol", label: "Total Cholesterol (mg/dL)" },
    { key: "hdl", label: "HDL (mg/dL)" },
    { key: "ldl", label: "LDL (mg/dL)" },
    { key: "triglycerides", label: "Triglycerides (mg/dL)" },
    { key: "creatinine", label: "Creatinine (mg/dL)" },
    { key: "ast", label: "AST (U/L)" },
    { key: "alt", label: "ALT (U/L)" },
    { key: "mcv", label: "MCV (fL)" },
    { key: "wbc", label: "WBC (×10³/µL)" },
    { key: "platelets", label: "Platelets (×10³/µL)" },
  ];

  const toggleHistory = (condition: string) => {
    setHistory((prev) =>
      prev.includes(condition) ? prev.filter((c) => c !== condition) : [...prev, condition]
    );
  };

  const runAnalysis = useCallback((values: Record<string, number>, patient: PatientInfo) => {
    setIsAnalyzing(true);
    setTimeout(() => {
      const result = runFullAnalysis(values, patient);
      navigate("/results", { state: { result } });
    }, 2000);
  }, [navigate]);

  const handleAnalyze = () => {
    const patient: PatientInfo = {
      age: age ? parseInt(age) : undefined,
      gender: gender as PatientInfo["gender"] || undefined,
      medicalHistory: history.length > 0 ? history : undefined,
    };

    if (manualMode) {
      const values: Record<string, number> = {};
      Object.entries(manualValues).forEach(([k, v]) => {
        if (v) values[k] = parseFloat(v);
      });
      if (Object.keys(values).length === 0) return;
      runAnalysis(values, patient);
    } else if (file) {
      // Simulate OCR extraction with sample data
      const sample = sampleReports[0];
      runAnalysis(sample.values, { ...sample.patient, ...patient });
    }
  };

  const loadSample = (idx: number) => {
    const sample = sampleReports[idx];
    setAge(sample.patient.age?.toString() || "");
    setGender(sample.patient.gender || "");
    setHistory(sample.patient.medicalHistory || []);
    setManualMode(true);
    const vals: Record<string, string> = {};
    Object.entries(sample.values).forEach(([k, v]) => { vals[k] = v.toString(); });
    setManualValues(vals);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="gradient-hero">
        <div className="container mx-auto px-4 py-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-foreground/20 flex items-center justify-center">
              <Activity className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-display font-bold text-primary-foreground">BloodInsight AI</h1>
              <p className="text-xs text-primary-foreground/70">Intelligent Blood Report Analysis</p>
            </div>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="gradient-hero pb-16 pt-8">
        <div className="container mx-auto px-4 text-center">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <div className="inline-flex items-center gap-2 bg-primary-foreground/10 rounded-full px-4 py-1.5 mb-6">
              <Sparkles className="w-4 h-4 text-primary-foreground" />
              <span className="text-sm text-primary-foreground/90">Multi-Model AI Analysis Engine</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-display font-bold text-primary-foreground mb-4 leading-tight">
              Understand Your Blood<br />Report in Seconds
            </h2>
            <p className="text-primary-foreground/70 max-w-xl mx-auto text-lg">
              Upload your report or enter values manually. Our AI classifies parameters, detects clinical patterns, calculates risk scores, and generates personalized recommendations.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Main Content */}
      <main className="container mx-auto px-4 -mt-8 pb-16">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-card rounded-2xl shadow-elevated p-6 md:p-8 space-y-6"
          >
            {/* Mode Toggle */}
            <div className="flex gap-2">
              <Button
                variant={!manualMode ? "default" : "outline"}
                size="sm"
                onClick={() => setManualMode(false)}
              >
                <FileText className="w-4 h-4 mr-1" /> Upload Report
              </Button>
              <Button
                variant={manualMode ? "default" : "outline"}
                size="sm"
                onClick={() => setManualMode(true)}
              >
                <Beaker className="w-4 h-4 mr-1" /> Enter Values
              </Button>
            </div>

            {!manualMode ? (
              <UploadZone onFileSelect={setFile} />
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="grid grid-cols-2 md:grid-cols-3 gap-3"
              >
                {parameterKeys.map(({ key, label }) => (
                  <div key={key}>
                    <Label className="text-xs text-muted-foreground">{label}</Label>
                    <Input
                      type="number"
                      step="any"
                      placeholder="—"
                      value={manualValues[key] || ""}
                      onChange={(e) => setManualValues((prev) => ({ ...prev, [key]: e.target.value }))}
                      className="mt-1"
                    />
                  </div>
                ))}
              </motion.div>
            )}

            {/* Patient Info */}
            <div className="border-t border-border pt-6">
              <h3 className="text-sm font-display font-semibold text-foreground mb-4">Patient Information (Optional)</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-xs text-muted-foreground">Age</Label>
                  <Input
                    type="number"
                    placeholder="e.g., 45"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">Gender</Label>
                  <Select value={gender} onValueChange={setGender}>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="Select gender" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="mt-4">
                <Label className="text-xs text-muted-foreground">Medical History</Label>
                <div className="flex flex-wrap gap-3 mt-2">
                  {medicalConditions.map((condition) => (
                    <label key={condition} className="flex items-center gap-2 text-sm cursor-pointer">
                      <Checkbox
                        checked={history.includes(condition)}
                        onCheckedChange={() => toggleHistory(condition)}
                      />
                      <span className="capitalize text-card-foreground">{condition}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {/* Analyze Button */}
            <Button
              size="lg"
              className="w-full gradient-hero text-primary-foreground font-display font-semibold text-base"
              onClick={handleAnalyze}
              disabled={isAnalyzing || (!file && !manualMode) || (manualMode && Object.values(manualValues).every((v) => !v))}
            >
              {isAnalyzing ? (
                <span className="flex items-center gap-2">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full"
                  />
                  Analyzing with AI Models...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  Analyze Report <ChevronRight className="w-5 h-5" />
                </span>
              )}
            </Button>

            {/* Sample Reports */}
            <div className="border-t border-border pt-4">
              <p className="text-xs text-muted-foreground mb-3">Or try a sample report:</p>
              <div className="flex flex-wrap gap-2">
                {sampleReports.map((sample, i) => (
                  <Button key={i} variant="outline" size="sm" onClick={() => loadSample(i)} className="text-xs">
                    {sample.name}
                  </Button>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
};

export default Index;
