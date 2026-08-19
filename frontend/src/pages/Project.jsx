import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import Timepoint from "../components/workflows/Timepoint";
import { getWorkflows } from "../api/workflows";

export default function Project() {
  const { token } = useAuth();
  const [workflows, setWorkflows] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);

  useEffect(() => {
    if (token) {
      getWorkflows(token).then((data) => setWorkflows(data));
    }
  }, [token]);

  return (
    <div
      style={{ padding: "20px", maxWidth: "800px", fontFamily: "sans-serif" }}
    >
      <h2 style={{ marginBottom: "16px", color: "#1e293b" }}>
        Create New Project
      </h2>

      {/* --- WORKFLOW SELECTION BUTTONS --- */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        {workflows.map((workflow) => {
          const isActive = selectedWorkflow === workflow.display_name;

          return (
            <button
              key={workflow.id}
              onClick={() => setSelectedWorkflow(workflow.display_name)}
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
              {workflow.display_name}
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
      {selectedWorkflow === "DRC Optimal Timepoint" && <Timepoint />}

      {selectedWorkflow === "Strain QC Analysis" && (
        <div
          style={{
            padding: "16px",
            backgroundColor: "#f8fafc",
            borderRadius: "6px",
            color: "#64748b",
          }}
        >
          Strain QC workflow under development...
        </div>
      )}

      {!selectedWorkflow && (
        <p style={{ color: "#64748b", fontSize: "14px" }}>
          Please select a workflow above to display its setup form.
        </p>
      )}
    </div>
  );
}
