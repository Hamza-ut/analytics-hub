import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { getProjectDetail } from "../api/projects";
import { TimepointResults } from "../components/results/TimepointResults";

import styles from "./ProjectDetail.module.css";

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
  const isFailed = project.status === "FAILED" || project.status === "ERROR";

  const statusBadgeClass = isCompleted
    ? styles.badgeSuccess
    : isFailed
      ? styles.badgeFailed
      : styles.badgePending;

  return (
    <div className={styles.container}>
      <Link to="/projects" className={styles.backLink}>
        ← Back to Projects
      </Link>

      {/* CLEAN METADATA SECTION */}
      <div className={styles.metaSection}>
        <h2 className={styles.heading}>Project Detail</h2>

        <p>
          <strong>Project ID:</strong> {project.project_id}
        </p>
        <p>
          <strong>Workflow:</strong> {project.workflow}
        </p>
        <p>
          <strong>Status:</strong>{" "}
          <span className={`${styles.badge} ${statusBadgeClass}`}>
            {project.status}
          </span>
        </p>
        <p>
          <strong>Created:</strong>{" "}
          {project.created_at
            ? new Date(project.created_at).toLocaleString()
            : "—"}
        </p>
        <p>
          <strong>Started:</strong>{" "}
          {project.started_at
            ? new Date(project.started_at).toLocaleString()
            : "—"}
        </p>
        <p>
          <strong>Completed:</strong>{" "}
          {project.completed_at
            ? new Date(project.completed_at).toLocaleString()
            : "—"}
        </p>
        <p>
          <strong>Duration:</strong> {project.duration ?? "—"}
        </p>
        <p>
          <strong>User:</strong> {project.username}
        </p>

        {project.error_message && (
          <p className={styles.metaValueError}>
            <strong>Error:</strong> {project.error_message}
          </p>
        )}
      </div>

      <hr className={styles.divider} />

      {/* WORKFLOW-SPECIFIC RESULTS SECTION */}
      <div>
        <h3 className={styles.heading}>Results</h3>
        {isCompleted ? (
          <TimepointResults projectId={projectId} authToken={token} />
        ) : isFailed ? (
          <div className={styles.alertError}>
            <strong>failed.</strong>
            {project.error_message && <p>{project.error_message}</p>}
          </div>
        ) : (
          <div className={styles.alertPending}>
            <strong>Status:</strong> {project.status}. Results will appear here
            once processing completes.
          </div>
        )}
      </div>
    </div>
  );
}
