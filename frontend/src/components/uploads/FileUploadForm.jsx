// FileUploadForm.jsx
import { useState, useContext } from "react";
import axios from "axios";
import { AuthContext } from "../../contexts/AuthContext";
import { API_BASE_URL } from "../../api/config";

export default function FileUploadForm({ onUploadSuccess }) {
  const { token } = useContext(AuthContext);
  const [selectedFile, setSelectedFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [apiMessage, setApiMessage] = useState(null);

  function handleFileChange(e) {
    if (e.target.files?.[0]) {
      setSelectedFile(e.target.files[0]);
      setApiMessage(null);
    }
  }

  async function handleUpload() {
    if (!selectedFile) return;
    setIsUploading(true);
    setApiMessage(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/uploads/file/`,
        formData,
        {
          headers: { Authorization: `Token ${token}` },
          onUploadProgress: (e) => {
            if (e.total) setProgress(Math.round((e.loaded * 100) / e.total));
          },
        },
      );

      if (
        response.status === 200 ||
        response.status === 201 ||
        response.status === 202
      ) {
        setApiMessage({ type: "success", text: "File uploaded successfully!" });
        setSelectedFile(null);
        if (onUploadSuccess) onUploadSuccess();
      }
    } catch (error) {
      // 💡 DYNAMICALLY PARSE DJANGO'S ERROR RESPONSE:
      const errorData = error.response?.data;

      let errorMessage = "Upload failed.";

      if (errorData) {
        if (typeof errorData === "string") {
          errorMessage = errorData;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.file && Array.isArray(errorData.file)) {
          errorMessage = errorData.file[0]; // e.g. "File extension not allowed"
        } else {
          errorMessage = JSON.stringify(errorData);
        }
      }

      setApiMessage({ type: "error", text: errorMessage });
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <>
      <input type="file" onChange={handleFileChange} />
      <button
        onClick={handleUpload}
        disabled={isUploading}
        style={{ marginLeft: "10px" }}
      >
        {isUploading ? `Uploading (${progress}%)` : "Upload"}
      </button>
      {apiMessage && (
        <p
          style={{
            color: apiMessage.type === "error" ? "#dc2626" : "#16a34a",
            marginTop: "10px",
          }}
        >
          {apiMessage.text}
        </p>
      )}
    </>
  );
}
