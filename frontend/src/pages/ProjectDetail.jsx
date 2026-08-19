import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { getProjectDetail } from "../api/projects";
import { TimepointResults } from "../components/results/TimepointResults";

export default function ProjectDetail() {
  const { projectId } = useParams();
  const { token } = useAuth();

  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchProjectData() {
      const data = await getProjectDetail(token, projectId);
      setProject(data);
      setLoading(false);
    }
    if (token && projectId) {
      fetchProjectData();
    }
  }, [token, projectId]);

  if (loading) return <p>Loading project details...</p>;
  if (!project) return <p>Project not found.</p>;

  const isCompleted =
    project.status === "COMPLETED" || project.status === "SUCCESS";
  const isFailed =
    project.status === "FAILED" || project.status === "ERROR";

  return (
    <div style={{ padding: "20px" }}>
      <Link to="/projects" style={{ color: "#2563eb", textDecoration: "none" }}>
        ← Back to Projects
      </Link>

      {/* GENERIC METADATA SECTION */}
      <div style={{ marginTop: "20px", marginBottom: "32px" }}>
        <h2 style={{ marginBottom: "16px" }}>Project Detail</h2>
        <table style={styles.metaTable}>
          <tbody>
            <tr>
              <td style={styles.metaLabel}>Project ID</td>
              <td style={styles.metaValue}>{project.project_id}</td>
            </tr>
            <tr>
              <td style={styles.metaLabel}>Workflow</td>
              <td style={styles.metaValue}>{project.workflow}</td>
            </tr>
            <tr>
              <td style={styles.metaLabel}>Status</td>
              <td style={styles.metaValue}>
                <span
                  style={{
                    padding: "4px 8px",
                    borderRadius: "4px",
                    fontSize: "12px",
                    fontWeight: "600",
                    backgroundColor: isCompleted
                      ? "#dcfce7"
                      : isFailed
                        ? "#fee2e2"
                        : "#f1f5f9",
                    color: isCompleted
                      ? "#15803d"
                      : isFailed
                        ? "#991b1b"
                        : "#475569",
                  }}
                >
                  {project.status}
                </span>
              </td>
            </tr>
            <tr>
              <td style={styles.metaLabel}>Created</td>
              <td style={styles.metaValue}>
                {project.created_at
                  ? new Date(project.created_at).toLocaleString()
                  : "—"}
              </td>
            </tr>
            <tr>
              <td style={styles.metaLabel}>Started</td>
              <td style={styles.metaValue}>
                {project.started_at
                  ? new Date(project.started_at).toLocaleString()
                  : "—"}
              </td>
            </tr>
            <tr>
              <td style={styles.metaLabel}>Completed</td>
              <td style={styles.metaValue}>
                {project.completed_at
                  ? new Date(project.completed_at).toLocaleString()
                  : "—"}
              </td>
            </tr>
            <tr>
              <td style={styles.metaLabel}>Duration</td>
              <td style={styles.metaValue}>{project.duration ?? "—"}</td>
            </tr>
            <tr>
              <td style={styles.metaLabel}>User</td>
              <td style={styles.metaValue}>{project.username}</td>
            </tr>
            {project.error_message && (
              <tr>
                <td style={styles.metaLabel}>Error</td>
                <td style={{ ...styles.metaValue, color: "#991b1b" }}>
                  {project.error_message}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <hr style={{ margin: "24px 0", borderColor: "#e2e8f0" }} />

      {/* WORKFLOW-SPECIFIC RESULTS SECTION */}
      <div>
        <h3 style={{ marginBottom: "16px" }}>Analysis Results</h3>
        {isCompleted ? (
          <TimepointResults projectId={projectId} authToken={token} />
        ) : isFailed ? (
          <div
            style={{
              padding: "16px",
              background: "#fee2e2",
              borderRadius: "8px",
              color: "#991b1b",
            }}
          >
            <strong>Analysis failed.</strong>
            {project.error_message && (
              <p style={{ marginTop: "8px" }}>{project.error_message}</p>
            )}
          </div>
        ) : (
          <div
            style={{
              padding: "16px",
              background: "#fef3c7",
              borderRadius: "8px",
            }}
          >
            <strong>Analysis Status:</strong> {project.status}. Results will
            appear here once processing completes.
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  metaTable: {
    borderCollapse: "collapse",
    width: "100%",
    maxWidth: "600px",
  },
  metaLabel: {
    padding: "8px 16px 8px 0",
    color: "#64748b",
    fontWeight: "600",
    fontSize: "14px",
    width: "160px",
    verticalAlign: "top",
  },
  metaValue: {
    padding: "8px 0",
    color: "#0f172a",
    fontSize: "14px",
  },
};
