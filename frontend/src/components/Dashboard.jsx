import { useState, useEffect } from "react";

export default function Dashboard() {
  const [files, setFiles] = useState([]);
  const [projects, setProjects] = useState([]);

  // Grab token directly from localStorage (for now!)
  const token = localStorage.getItem("userToken");

  // 1. Fetch Projects List
  async function fetchProjectsList() {
    const response = await fetch("http://127.0.0.1:8000/api/v1/projects/all/", {
      method: "GET",
      headers: {
        Authorization: `Token ${token}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      setProjects(data);
    }
  }

  // 2. Fetch Files List
  async function fetchFilesList() {
    const response = await fetch("http://127.0.0.1:8000/api/v1/uploads/all/", {
      method: "GET",
      headers: {
        Authorization: `Token ${token}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      setFiles(data);
    }
  }

  // Run both fetch calls once when page loads
  useEffect(() => {
    if (token) {
      fetchProjectsList();
      fetchFilesList();
    }
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h2>Biofoundry Dashboard</h2>

      {/* PROJECT DISPLAY LIST */}
      <h3>Your Projects</h3>
      <ul>
        {projects.map((project) => (
          <li key={project.project_id}>{project.project_id}</li>
        ))}
      </ul>

      {/* FILE DISPLAY LIST */}
      <h3>Your Uploaded Files</h3>
      <ul>
        {files.map((file) => (
          <li key={file.upload_id}>{file.original_filename}</li>
        ))}
      </ul>
    </div>
  );
}
