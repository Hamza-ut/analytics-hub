import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { formatDate } from "../utils/formatters";
import {
  getProjectsList,
  runTimepointProject,
  deleteProject,
} from "../api/projects";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoadingId, setActionLoadingId] = useState(null); // Track pending operations
  const { token } = useAuth();

  async function fetchProjects() {
    try {
      const data = await getProjectsList(token);
      setProjects(data);
    } catch (error) {
      console.error("Error fetching projects:", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (token) {
      fetchProjects();
    }
  }, [token]);

  // Handle Project Execution
  const handleRun = async (projectId) => {
    setActionLoadingId(projectId);
    const result = await runTimepointProject(token, projectId);
    if (result) {
      // Refresh list to update status pill (CREATED -> RUNNING/COMPLETED)
      await fetchProjects();
    } else {
      alert("Failed to run project.");
    }
    setActionLoadingId(null);
  };

  // Handle Project Deletion
  const handleDelete = async (projectId) => {
    const confirmDelete = window.confirm(
      `Are you sure you want to delete project ${projectId}? This action cannot be undone.`,
    );
    if (!confirmDelete) return;

    setActionLoadingId(projectId);
    const result = await deleteProject(token, projectId);

    // Check for success (204 No Content often returns null in axios, check if call succeeded)
    if (result !== undefined) {
      // Remove item locally from state so it disappears instantly without full reload
      setProjects((prev) => prev.filter((p) => p.project_id !== projectId));
    } else {
      alert("Failed to delete project.");
    }
    setActionLoadingId(null);
  };

  return (
    <div style={{ padding: "20px" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >
        <h2>All Project Runs</h2>
        <Link
          to="/projects/new"
          style={{
            padding: "8px 16px",
            backgroundColor: "#2563eb",
            color: "#ffffff",
            borderRadius: "6px",
            textDecoration: "none",
            fontWeight: "500",
            fontSize: "14px",
          }}
        >
          + New Project
        </Link>
      </div>

      {loading ? (
        <p>Loading projects...</p>
      ) : projects.length === 0 ? (
        <p>No project runs created yet.</p>
      ) : (
        <table
          style={{
            width: "100%",
            textAlign: "left",
            border: "1px solid #e2e8f0",
            borderCollapse: "collapse",
          }}
        >
          <thead>
            <tr
              style={{
                backgroundColor: "#f8fafc",
                borderBottom: "1px solid #e2e8f0",
              }}
            >
              <th style={{ padding: "12px" }}>Project ID</th>
              <th style={{ padding: "12px" }}>Workflow</th>
              <th style={{ padding: "12px" }}>Created</th>
              <th style={{ padding: "12px" }}>User</th>
              <th style={{ padding: "12px" }}>Status</th>
              <th style={{ padding: "12px" }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((proj) => (
              <tr
                key={proj.project_id}
                style={{ borderBottom: "1px solid #e2e8f0" }}
              >
                <td style={{ padding: "12px" }}>
                  <Link
                    to={`/projects/${proj.project_id}`}
                    style={{
                      color: "#2563eb",
                      fontWeight: "600",
                      textDecoration: "none",
                    }}
                  >
                    {proj.project_id}
                  </Link>
                </td>
                <td style={{ padding: "12px" }}>{proj.workflow}</td>
                <td style={{ padding: "12px" }}>
                  {formatDate(proj.created_at)}
                </td>
                <td style={{ padding: "12px" }}>{proj.username}</td>
                <td style={{ padding: "12px" }}>
                  <span
                    style={{
                      padding: "4px 8px",
                      borderRadius: "4px",
                      fontSize: "12px",
                      fontWeight: "600",
                      backgroundColor:
                        proj.status === "COMPLETED"
                          ? "#dcfce7"
                          : proj.status === "RUNNING"
                            ? "#fef9c3"
                            : "#f1f5f9",
                      color:
                        proj.status === "COMPLETED"
                          ? "#15803d"
                          : proj.status === "RUNNING"
                            ? "#a16207"
                            : "#475569",
                    }}
                  >
                    {proj.status}
                  </span>
                </td>
                <td style={{ padding: "12px" }}>
                  <button
                    disabled={actionLoadingId === proj.project_id}
                    onClick={() => handleRun(proj.project_id)}
                  >
                    Run
                  </button>
                  {" | "}
                  <Link to={`/projects/${proj.project_id}`}>
                    <button>View Results</button>
                  </Link>
                  {" | "}
                  <button
                    disabled={actionLoadingId === proj.project_id}
                    onClick={() => handleDelete(proj.project_id)}
                    style={{ color: "red" }}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
