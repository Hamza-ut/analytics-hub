import { useContext, useState, useEffect } from "react";
import { AuthContext } from "../contexts/AuthContext";
import FileUploadForm from "../components/uploads/FileUploadForm";

// helper functions
import { formatBytes, formatDate } from "../utils/formatters";
import { getUploadedFiles, downloadFile, deleteFile } from "../api/files";

export default function Upload() {
  const { token } = useContext(AuthContext);
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState(null);

  async function FilesList() {
    const data = await getUploadedFiles(token);
    setFiles(data);
  }

  useEffect(() => {
    if (token) FilesList();
  }, [token]);

  async function handleDownload(uploadId, filename) {
    const blobData = await downloadFile(token, uploadId);
    if (!blobData) {
      alert("Failed to download file.");
      return;
    }

    const url = window.URL.createObjectURL(new Blob([blobData]));
    const tempLink = document.createElement("a");
    tempLink.href = url;
    tempLink.download = filename;
    document.body.appendChild(tempLink);
    tempLink.click();
    tempLink.remove();
    window.URL.revokeObjectURL(url);
  }

  async function handleDelete(uploadId) {
    // 1. Wait for Django to respond
    const result = await deleteFile(token, uploadId);

    // 2. CHECK THE RESULT FIRST!
    if (result.success) {
      // 🟢 Django deleted it! NOW remove it from screen.
      setFiles(files.filter((file) => file.upload_id !== uploadId));
      setStatus({ type: "success", message: result.message });
    } else {
      // 🔴 Django blocked it! DO NOT touch setFiles!
      // Just show Django's error message on screen.
      setStatus({ type: "error", message: result.message });
    }
  }

  return (
    <div style={{ padding: "20px", maxWidth: "900px" }}>
      <h2>Data Manager</h2>
      {/* 🟢/🔴 ADD THIS STATUS DISPLAY BLOCK HERE */}
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

      <div
        style={{
          backgroundColor: "#f8fafc",
          padding: "20px",
          borderRadius: "8px",
          marginBottom: "30px",
        }}
      >
        <h3>Upload New Dataset</h3>
        <p
          style={{
            color: "#555",
            fontSize: "14px",
            marginTop: "-10px",
            marginBottom: "20px",
          }}
        >
          Upload your datasets to create and run projects using specific
          pipelines.
        </p>

        <p
          style={{
            margin: 0,
            fontSize: "13px",
            color: "#495057",
            fontWeight: "bold",
          }}
        >
          Pipeline Requirements to keep in mind before uploading your files:
        </p>
        <ul
          style={{
            margin: "6px 0 0 0",
            paddingLeft: "18px",
            fontSize: "12px",
            color: "#6c757d",
          }}
        >
          <li> Max file size for any upload is 10 GB. </li>
          <li>
            <strong>Optimal Timepoint:</strong> Accepts CSV files (.csv)
          </li>
          <li>
            <strong>Strain QC:</strong> Accepts sequence files (.fastq,
            .fastq.gz, .fq, .fasta, .fna, .fa, .gbk, .gb)
          </li>
        </ul>
        <br />
        <FileUploadForm onUploadSuccess={FilesList} />
      </div>

      <div
        style={{
          backgroundColor: "#f8fafc",
          padding: "20px",
          borderRadius: "8px",
          marginBottom: "30px",
        }}
      >
        <h3>Your Uploaded Datasets</h3>
        {files.length === 0 ? (
          <p>No datasets found. Upload your first file above!</p>
        ) : (
          <table
            style={{
              width: "100%",
              textAlign: "left",
              border: "1px solid #ddd",
              borderCollapse: "collapse",
            }}
          >
            <thead style={{ borderBottom: "0.5px solid #ddd" }}>
              <tr>
                <th>ID</th>
                <th>Filename</th>
                <th>Size</th>
                <th>Upload at </th>
                <th>Uploaded by</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {files.map((file) => (
                <tr
                  key={file.upload_id}
                  style={{ borderBottom: "0.5px solid #ddd" }}
                >
                  <td>{file.upload_id}</td>
                  <td>{file.original_filename}</td>
                  <td>{formatBytes(file.file_size)}</td>
                  <td>{formatDate(file.uploaded_at)}</td>
                  <td>{file.user}</td>
                  <td>
                    <button
                      onClick={() =>
                        handleDownload(file.upload_id, file.original_filename)
                      }
                    >
                      Download
                    </button>
                    &nbsp;|&nbsp;
                    <button onClick={() => handleDelete(file.upload_id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
