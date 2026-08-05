import { useState, useEffect, useContext } from "react";
import { AuthContext } from "../contexts/AuthContext";
import Timepoint from "../components/projects/Timepoint";
import { getPipelines } from "../api/pipelines";

export default function Project() {
  const { token } = useContext(AuthContext);
  const [pipelines, setPipelines] = useState([]);
  const [selectedPipeline, setSelectedPipeline] = useState(null);

  useEffect(() => {
    if (token) {
      getPipelines(token).then((data) => setPipelines(data));
    }
  }, [token]);

  return (
    <div
      style={{ padding: "20px", maxWidth: "800px", fontFamily: "sans-serif" }}
    >
      <h2 style={{ marginBottom: "16px", color: "#1e293b" }}>
        Create New Project
      </h2>

      {/* --- PIPELINE SELECTION BUTTONS --- */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        {pipelines.map((pipeline) => {
          const isActive = selectedPipeline === pipeline.pipeline_name;

          return (
            <button
              key={pipeline.id}
              onClick={() => setSelectedPipeline(pipeline.pipeline_name)}
              style={{
                padding: "10px 18px",
                fontSize: "14px",
                fontWeight: "600",
                cursor: "pointer",
                borderRadius: "6px",
                border: isActive ? "2px solid #2563eb" : "1px solid #cbd5e1",
                backgroundColor: isActive ? "#eff6ff" : "#ffffff",
                color: isActive ? "#2563eb" : "#475569",
                transition: "all 0.15s ease",
              }}
            >
              {pipeline.display_name}
            </button>
          );
        })}
      </div>

      <hr
        style={{
          border: "none",
          borderTop: "1px solid #e2e8f0",
          marginBottom: "20px",
        }}
      />

      {/* --- SHOW FORM BASED ON SELECTION --- */}
      {selectedPipeline === "TIMEPOINT" && <Timepoint />}

      {selectedPipeline === "STRAIN_QC" && (
        <div
          style={{
            padding: "16px",
            backgroundColor: "#f8fafc",
            borderRadius: "6px",
            color: "#64748b",
          }}
        >
          Strain QC pipeline under development...
        </div>
      )}

      {!selectedPipeline && (
        <p style={{ color: "#64748b", fontSize: "14px" }}>
          Please select a pipeline above to display its setup form.
        </p>
      )}
    </div>
  );
}
