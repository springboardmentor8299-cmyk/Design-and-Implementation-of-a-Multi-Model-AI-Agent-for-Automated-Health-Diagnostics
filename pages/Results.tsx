import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Activity, ArrowLeft, Download, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AnalysisResult } from "@/lib/bloodAnalysis";
import ParameterTable from "@/components/ParameterTable";
import ParameterChart from "@/components/ParameterChart";
import PatternCards from "@/components/PatternCards";
import RecommendationsList from "@/components/RecommendationsList";
import { useRef, useCallback } from "react";

const Results = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const result = location.state?.result as AnalysisResult | undefined;
  const reportRef = useRef<HTMLDivElement>(null);

  const handleDownloadPDF = useCallback(async () => {
    if (!reportRef.current) return;
    const html2canvas = (await import("html2canvas")).default;
    const { jsPDF } = await import("jspdf");
    const canvas = await html2canvas(reportRef.current, { scale: 2, useCORS: true });
    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF("p", "mm", "a4");
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
    pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
    pdf.save("blood-report-analysis.pdf");
  }, []);

  if (!result) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="text-muted-foreground mb-4">No analysis data found.</p>
          <Button onClick={() => navigate("/")}>
            <ArrowLeft className="w-4 h-4 mr-2" /> Go Back
          </Button>
        </div>
      </div>
    );
  }

  const abnormalCount = result.parameters.filter((p) => p.classification !== "normal").length;
  const highPatterns = result.patterns.filter((p) => p.severity === "high").length;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="gradient-hero">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-primary-foreground/20 flex items-center justify-center">
              <Activity className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-lg font-display font-bold text-primary-foreground">BloodInsight AI</span>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => navigate("/")} className="bg-primary-foreground/10 border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/20">
              <RotateCcw className="w-4 h-4 mr-1" /> New Analysis
            </Button>
            <Button variant="outline" size="sm" onClick={handleDownloadPDF} className="bg-primary-foreground/10 border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/20">
              <Download className="w-4 h-4 mr-1" /> Download PDF
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8" ref={reportRef}>
        {/* Summary Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-card rounded-xl shadow-elevated p-6 mb-8"
        >
          <div className="flex flex-col md:flex-row md:items-center gap-4 justify-between">
            <div>
              <h2 className="text-xl font-display font-bold text-card-foreground">Analysis Results</h2>
              <p className="text-sm text-muted-foreground mt-1">{result.summary}</p>
            </div>
            <div className="flex gap-4">
              <div className="text-center px-4">
                <p className="text-2xl font-display font-bold text-foreground">{result.parameters.length}</p>
                <p className="text-xs text-muted-foreground">Parameters</p>
              </div>
              <div className="text-center px-4 border-l border-border">
                <p className={`text-2xl font-display font-bold ${abnormalCount > 0 ? "text-status-high" : "text-status-normal"}`}>{abnormalCount}</p>
                <p className="text-xs text-muted-foreground">Abnormal</p>
              </div>
              <div className="text-center px-4 border-l border-border">
                <p className={`text-2xl font-display font-bold ${highPatterns > 0 ? "text-status-high" : "text-status-normal"}`}>{result.patterns.length}</p>
                <p className="text-xs text-muted-foreground">Patterns</p>
              </div>
            </div>
          </div>

          {result.patientInfo.age && (
            <div className="mt-4 pt-4 border-t border-border flex flex-wrap gap-4 text-sm text-muted-foreground">
              {result.patientInfo.age && <span>Age: <strong className="text-foreground">{result.patientInfo.age}</strong></span>}
              {result.patientInfo.gender && <span>Gender: <strong className="text-foreground capitalize">{result.patientInfo.gender}</strong></span>}
              {result.patientInfo.medicalHistory && result.patientInfo.medicalHistory.length > 0 && (
                <span>History: <strong className="text-foreground capitalize">{result.patientInfo.medicalHistory.join(", ")}</strong></span>
              )}
              <span>Date: <strong className="text-foreground">{new Date(result.timestamp).toLocaleDateString()}</strong></span>
            </div>
          )}
        </motion.div>

        {/* Chart */}
        <div className="mb-8">
          <ParameterChart parameters={result.parameters} />
        </div>

        {/* Parameter Table */}
        <div className="mb-8">
          <ParameterTable parameters={result.parameters} />
        </div>

        {/* Patterns & Risk */}
        <div className="mb-8">
          <PatternCards patterns={result.patterns} riskScores={result.riskScores} />
        </div>

        {/* Recommendations */}
        <div className="mb-8">
          <RecommendationsList recommendations={result.recommendations} />
        </div>

        {/* Disclaimer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="bg-muted rounded-xl p-5 text-center"
        >
          <p className="text-xs text-muted-foreground">
            ⚠️ <strong>Medical Disclaimer:</strong> This AI-powered analysis is for informational purposes only and does not constitute medical advice, diagnosis, or treatment.
            Always consult a qualified healthcare professional for medical decisions. Results should be verified with laboratory confirmation.
          </p>
        </motion.div>
      </main>
    </div>
  );
};

export default Results;
