import { API_BASE_URL } from "./config";
import axios from "axios";

// Fetch timepoint config
export async function fetchTimepointConfig(token, projectId) {
  if (!token) return null;

  try {
    const response = await axios({
      method: "GET",
      url: `${API_BASE_URL}/workflows/timepoint/config/${projectId}/`,
      headers: {
        Authorization: `Token ${token}`,
        "Content-Type": "application/json",
      },
    });

    return response.data;
  } catch (error) {
    if (error.response) {
      console.error(
        "Failed to fetch timepoint config:",
        error.response.status,
        error.response.data,
      );
    } else {
      console.error("Network Error:", error.message);
    }
    return null;
  }
}

// Fetch results for a specific project by its ID
export async function fetchTimepointResults(token, projectId) {
  if (!token || !projectId) return null;

  try {
    const response = await axios({
      method: "GET",
      url: `${API_BASE_URL}/workflows/timepoint/results/${projectId}/`,
      headers: {
        Authorization: `Token ${token}`,
        "Content-Type": "application/json",
      },
    });

    return response.data;
  } catch (error) {
    if (error.response) {
      console.error(
        "Failed to fetch project results:",
        error.response.status,
        error.response.data,
      );
    } else {
      console.error("Network Error:", error.message);
    }
    return null;
  }
}
