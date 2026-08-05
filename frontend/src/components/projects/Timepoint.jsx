// src/components/projects/Timepoint.jsx
import { useState, useEffect, useContext } from "react";
import { AuthContext } from "../../contexts/AuthContext";
import { useNavigate } from "react-router-dom";

// helper functions
import { getUploadedFiles } from "../../api/files";
import { createProject } from "../../api/projects";

export default function Timepoint() {
  const navigate = useNavigate();
  const { token } = useContext(AuthContext);
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState(null);

  // Single state object for the entire form
  const [formData, setFormData] = useState({
    fileId: "",
    group_fields: "",
    dose_field: "",
    od_field: "",
    time_field: "",
  });

  // Fetch Files List
  async function FilesList() {
    try {
      const data = await getUploadedFiles(token);
      console.log("Files returned from Django:", data);
      setFiles(data);
    } catch (error) {
      console.error("Error fetching uploaded files:", error);
    }
  }

  // Run once on load and whenever token changes
  useEffect(() => {
    if (token) {
      FilesList();
    }
  }, [token]);

  // Dynamic input handler
  function handleChange(e) {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  }

  // Submit handler
  async function handleSubmit(e) {
    e.preventDefault();
    setStatus(null);

    // Split comma-separated string into clean array of trimmed strings
    const groupList = formData.group_fields
      .split(",")
      .map((item) => item.trim())
      .filter((item) => item.length > 0);

    // Construct the payload expected by Django backend
    const myData = {
      pipeline: "TIMEPOINT",
      // Pass fileId directly as a string (e.g., ["upl_2c4f9c"])
      files: formData.fileId ? [formData.fileId] : [],
      config: {
        group_fields: groupList,
        dose_field: formData.dose_field,
        od_field: formData.od_field,
        time_field: formData.time_field,
      },
    };

    const result = await createProject(token, myData);

    if (result && result.project_id) {
      setStatus({
        type: "success",
        message: `Project created successfully! (ID: ${result.project_id}) Redirecting...`,
      });

      // Reset form fields
      setFormData({
        fileId: "",
        group_fields: "",
        dose_field: "",
        od_field: "",
        time_field: "",
      });
    } else {
      setStatus({
        type: "error",
        message: "Failed to create project. Check server logs.",
      });
    }
    setTimeout(() => {
      navigate("/projects"); // Navigate to projects list
    }, 1500);
  }

  return (
    <div
      style={{
        marginTop: "24px",
        padding: "24px",
        border: "1px solid #e2e8f0",
        borderRadius: "8px",
        backgroundColor: "#ffffff",
        maxWidth: "600px",
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: "8px" }}>Optimal Timepoint</h2>
      <p style={{ color: "#475569", marginTop: 0, marginBottom: "16px" }}>
        Identify optimal timepoints for dose response curve modelling by
        selecting a dataset and setting field parameters.
      </p>

      {/* SUCCESS / ERROR FEEDBACK */}
      {status && (
        <div
          style={{
            padding: "10px 14px",
            borderRadius: "4px",
            marginBottom: "16px",
            backgroundColor: status.type === "success" ? "#dcfce7" : "#fee2e2",
            color: status.type === "success" ? "#166534" : "#991b1b",
          }}
        >
          {status.message}
        </div>
      )}

      {/* INSTRUCTION BOX */}
      <div
        style={{
          backgroundColor: "#f8fafc",
          border: "1px solid #cbd5e1",
          borderRadius: "6px",
          padding: "16px",
          marginBottom: "24px",
        }}
      >
        <strong style={{ display: "block", marginBottom: "8px" }}>
          Required columns (case-insensitive):
        </strong>
        <ul
          style={{
            margin: 0,
            paddingLeft: "20px",
            color: "#334155",
            lineHeight: "1.6",
          }}
        >
          <li>
            <strong>Group Fields:</strong> Column(s) to group by (separate
            multiple columns with commas).
          </li>
          <li>
            <strong>Dose Field:</strong> Column containing numeric
            dose/concentration values.
          </li>
          <li>
            <strong>OD Field:</strong> Column containing raw OD measurements.
          </li>
          <li>
            <strong>Time Field:</strong> Column containing measurement
            timepoints.
          </li>
        </ul>
      </div>

      <form onSubmit={handleSubmit}>
        {/* 1. FILE DROPDOWN */}
        <div style={{ marginBottom: "15px" }}>
          <label
            style={{ display: "block", fontWeight: "600", marginBottom: "6px" }}
          >
            Select File:
          </label>
          <select
            name="fileId"
            value={formData.fileId}
            onChange={handleChange}
            required
            style={{
              width: "100%",
              padding: "8px 12px",
              borderRadius: "4px",
              border: "1px solid #cbd5e1",
            }}
          >
            <option value="" disabled>
              -- Select a file --
            </option>
            {files.map((file) => (
              <option key={file.upload_id} value={file.upload_id}>
                {file.original_filename}
              </option>
            ))}
          </select>
        </div>

        {/* 2. GROUP FIELDS INPUT */}
        <div style={{ marginBottom: "15px" }}>
          <label
            style={{ display: "block", fontWeight: "600", marginBottom: "6px" }}
          >
            Group Fields:
          </label>
          <input
            type="text"
            name="group_fields"
            placeholder="e.g. condition, ratio"
            value={formData.group_fields}
            onChange={handleChange}
            required
            style={{
              width: "100%",
              padding: "8px 12px",
              borderRadius: "4px",
              border: "1px solid #cbd5e1",
              boxSizing: "border-box",
            }}
          />
        </div>

        {/* 3. DOSE FIELD INPUT */}
        <div style={{ marginBottom: "15px" }}>
          <label
            style={{ display: "block", fontWeight: "600", marginBottom: "6px" }}
          >
            Dose Field:
          </label>
          <input
            type="text"
            name="dose_field"
            placeholder="e.g. xMIC"
            value={formData.dose_field}
            onChange={handleChange}
            required
            style={{
              width: "100%",
              padding: "8px 12px",
              borderRadius: "4px",
              border: "1px solid #cbd5e1",
              boxSizing: "border-box",
            }}
          />
        </div>

        {/* 4. OD FIELD INPUT */}
        <div style={{ marginBottom: "15px" }}>
          <label
            style={{ display: "block", fontWeight: "600", marginBottom: "6px" }}
          >
            OD Field:
          </label>
          <input
            type="text"
            name="od_field"
            placeholder="e.g. raw_OD"
            value={formData.od_field}
            onChange={handleChange}
            required
            style={{
              width: "100%",
              padding: "8px 12px",
              borderRadius: "4px",
              border: "1px solid #cbd5e1",
              boxSizing: "border-box",
            }}
          />
        </div>

        {/* 5. TIME FIELD INPUT */}
        <div style={{ marginBottom: "15px" }}>
          <label
            style={{ display: "block", fontWeight: "600", marginBottom: "6px" }}
          >
            Time Field:
          </label>
          <input
            type="text"
            name="time_field"
            placeholder="e.g. HOUR"
            value={formData.time_field}
            onChange={handleChange}
            required
            style={{
              width: "100%",
              padding: "8px 12px",
              borderRadius: "4px",
              border: "1px solid #cbd5e1",
              boxSizing: "border-box",
            }}
          />
        </div>

        {/* SUBMIT BUTTON */}
        <button
          type="submit"
          style={{
            backgroundColor: "#2563eb",
            color: "#ffffff",
            padding: "10px 20px",
            border: "none",
            borderRadius: "4px",
            fontSize: "14px",
            fontWeight: "600",
            cursor: "pointer",
          }}
        >
          Create Timepoint Project
        </button>
      </form>
    </div>
  );
}
