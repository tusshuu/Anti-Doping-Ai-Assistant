import { useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import {
  FileText,
  Camera,
  Mic,
  Search,
  AlertTriangle,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

type InputMode = "text" | "image" | "voice";

interface CheckResult {
  medicine: string;
  status: "safe" | "banned" | "caution";
  bannedChemical?: string;
  category?: string;
  details: string;
}

const CheckPrescription = () => {
  const [mode, setMode] = useState<InputMode>("text");
  const [textInput, setTextInput] = useState("");
  const [results, setResults] = useState<CheckResult[]>([]);
  const [hasChecked, setHasChecked] = useState(false);
  const [aiExplanation, setAiExplanation] = useState("");

  const handleCheck = async () => {
    if (!textInput.trim()) {
      toast.error("Please enter medicine names or prescription text");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textInput }),
      });

      if (!response.ok) throw new Error("Backend error");

      const data = await response.json();
      console.log("Backend response:", data);

      setAiExplanation(data.ai_explanation || "");

      if (Array.isArray(data.results) && data.results.length === 0) {
        setResults([
          {
            medicine: textInput,
            status: "safe",
            details: data.message || "No banned substances detected.",
          },
        ]);
      } else if (Array.isArray(data.results)) {
        const formatted = data.results.map((item: any) => ({
          medicine: item.medicine || item.name || "Unknown",
          status: item.status || "caution",
          bannedChemical: item.bannedChemical,
          category: item.category,
          details: item.details || "No details provided.",
        }));
        setResults(formatted);
      }

      setHasChecked(true);
    } catch (error) {
      toast.error("Backend connection failed");
      console.error(error);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="pt-24 pb-20 px-4">
        <div className="max-w-4xl mx-auto">

          {/* Header */}
          <div className="text-center mb-10">
            <h1 className="text-3xl sm:text-4xl font-bold mb-3">
              Check Your Prescription
            </h1>
            <p className="text-muted-foreground">
              Enter medicine names or upload prescription details to check for banned substances.
            </p>
          </div>

          {/* Mode Selector */}
          <div className="flex gap-2 justify-center mb-8">
            {[
              { key: "text" as InputMode, icon: FileText, label: "Text" },
              { key: "image" as InputMode, icon: Camera, label: "Image" },
              { key: "voice" as InputMode, icon: Mic, label: "Voice" },
            ].map((m) => (
              <button
                key={m.key}
                onClick={() => setMode(m.key)}
                className={`flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-medium transition ${
                  mode === m.key
                    ? "bg-primary text-primary-foreground"
                    : "bg-card border border-border hover:bg-muted"
                }`}
              >
                <m.icon className="h-4 w-4" />
                {m.label}
              </button>
            ))}
          </div>

          {/* Input Area */}
          <div className="bg-card border rounded-xl p-6 mb-8">

            {mode === "text" && (
              <div className="space-y-4">
                <Textarea
                  placeholder="e.g., Aspirin, Prednisolone..."
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  className="min-h-[120px]"
                />
                <Button onClick={handleCheck} className="w-full gap-2">
                  <Search className="h-4 w-4" />
                  Check for Banned Substances
                </Button>
              </div>
            )}

            {mode === "image" && (
              <div className="text-center py-10">
                <Camera className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-sm text-muted-foreground mb-4">
                  Upload prescription image (AI backend required)
                </p>
                <Input
                  type="file"
                  accept="image/*"
                  onChange={() =>
                    toast.info("Image OCR backend not yet implemented.")
                  }
                />
              </div>
            )}

            {mode === "voice" && (
              <div className="text-center py-10">
                <Mic className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-sm text-muted-foreground mb-4">
                  Voice input requires speech-to-text backend.
                </p>
                <Button
                  variant="outline"
                  onClick={() =>
                    toast.info("Voice backend not yet implemented.")
                  }
                >
                  Start Recording
                </Button>
              </div>
            )}
          </div>

          {/* Results */}
          {hasChecked && results.length > 0 && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold">Analysis Results</h2>

              {results.map((r, i) => (
                <div
                  key={i}
                  className={`border rounded-xl p-5 ${
                    r.status === "safe"
                      ? "bg-green-50 border-green-300"
                      : r.status === "banned"
                      ? "bg-red-50 border-red-300"
                      : "bg-yellow-50 border-yellow-300"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {r.status === "safe" ? (
                      <CheckCircle2 className="h-6 w-6 text-green-600" />
                    ) : r.status === "banned" ? (
                      <XCircle className="h-6 w-6 text-red-600" />
                    ) : (
                      <AlertTriangle className="h-6 w-6 text-yellow-600" />
                    )}

                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">{r.medicine}</h3>
                        <span className="text-xs px-2 py-0.5 border rounded-full">
                          {r.status.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {r.details}
                      </p>
                    </div>
                  </div>
                </div>
              ))}

              {/* AI Explanation */}
              {aiExplanation && (
                <div className="p-5 bg-blue-50 border border-blue-300 rounded-xl">
                  <h3 className="font-semibold text-blue-700 mb-2">
                    🤖 AI Explanation
                  </h3>
                  <p className="text-sm whitespace-pre-line">
                    {aiExplanation}
                  </p>
                </div>
              )}
            </div>
          )}

        </div>
      </div>

      <Footer />
    </div>
  );
};

export default CheckPrescription;
