import { API_BASE_URL } from "../api/config";
import axios from "axios";

// create config for project creation
export async function TimepointRunConfigure(token, myData) {
  const { projectId, ...bodyData } = myData;
  try {
    const response = await axios({
      method: "POST",
      url: `${API_BASE_URL}/workflows/timepoint/config/${projectId}/`,
      headers: { Authorization: `Token ${token}` },
      data: bodyData,
    });
    return response.data;
  } catch (error) {
    console.error("Failed to configure timepoint run:", error);
    throw error;
  }
}

// fetches files list
export async function getUploadedFiles(token) {
  if (!token) return [];
  try {
    const response = await axios({
      method: "GET",
      url: `${API_BASE_URL}/uploads/all/`,
      headers: { Authorization: `Token ${token}` },
    });
    return response.data;
  } catch (error) {
    console.error("Failed to fetch files:", error);
    return []; // Returns empty array so .map() doesn't break
  }
}

// file downloader for button on uploads page
export async function downloadFile(token, uploadId) {
  if (!token) return null;
  try {
    const response = await axios({
      method: "GET",
      url: `${API_BASE_URL}/uploads/file/${uploadId}/download/`,
      headers: { Authorization: `Token ${token}` },
      responseType: "blob",
    });
    return response.data;
  } catch (error) {
    console.error("Failed to download file:", error);
    return null;
  }
}

// file deleter for button
export async function deleteFile(token, uploadId) {
  if (!token) return { success: false, message: "No token provided." };

  try {
    const response = await axios({
      method: "DELETE",
      url: `${API_BASE_URL}/uploads/file/${uploadId}/`,
      headers: { Authorization: `Token ${token}` },
    });

    // HTTP status 200-299 means Django deleted the file successfully
    return {
      success: true,
      message: response.data?.message || "File deleted successfully.",
    };
  } catch (error) {
    console.error("Failed to delete file:", error);

    if (error.response && error.response.data) {
      const serverData = error.response.data;

      // Extract message whether it's an object { message: "..." } or string
      const extractedMessage =
        typeof serverData === "string"
          ? serverData
          : serverData.message || serverData.detail || "Failed to delete file.";

      return {
        success: false,
        message: extractedMessage,
      };
    }

    return {
      success: false,
      message: "Server unreachable or network error.",
    };
  }
}
