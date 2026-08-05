import { useState, useEffect, useContext } from "react";
import { useParams, Link } from "react-router-dom";
import { AuthContext } from "../contexts/AuthContext";
import { getProjectDetail } from "../api/projects";
// 1. Import your newly created TimepointResults component
import { TimepointResults } from "../components/results/TimepointResults";

export default function ProjectDetail() {
  const { projectId } = useParams();
  const { token } = useContext(AuthContext);

  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);

  async function fetchProjectData() {
    const data = await getProjectDetail(token, projectId);
    setProject(data);
    setLoading(false);
  }

  useEffect(() => {
    if (token && projectId) {
      fetchProjectData();
    }
  }, [token, projectId]);

  if (loading) return <p>Loading project details...</p>;
  if (!project) return <p>Project not found.</p>;

  return (
    <div style={{ padding: "20px" }}>
      <Link to="/projects">← Back to Projects</Link>

      <h2>Project: {project.project_id}</h2>
      <p>
        <strong>Status:</strong> {project.status}
      </p>

      {/* CONFIGURATION SECTION */}
      <div style={{ marginBottom: "20px" }}>
        <h3>Configuration</h3>
        <p>
          <strong>Pipeline:</strong> {project.pipeline}
        </p>
        <p>
          <strong>Group Fields:</strong>{" "}
          {project.config?.group_fields?.join(", ")}
        </p>
        <p>
          <strong>Dose Field:</strong> {project.config?.dose_field}
        </p>
        <p>
          <strong>OD Field:</strong> {project.config?.od_field}
        </p>
        <p>
          <strong>Time Field:</strong> {project.config?.time_field}
        </p>
      </div>

      {/* FILES SECTION */}
      <div style={{ marginBottom: "20px" }}>
        <h3>Attached Datasets</h3>
        <ul>
          {project.files?.map(function (file) {
            return (
              <li key={file.upload_id}>
                {file.original_filename} ({file.upload_id})
              </li>
            );
          })}
        </ul>
      </div>

      <hr style={{ margin: "24px 0" }} />

      {/* 2. RESULTS SECTION */}
      <div>
        {project.status === "COMPLETED" || project.status === "SUCCESS" ? (
          <TimepointResults projectId={projectId} authToken={token} />
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
