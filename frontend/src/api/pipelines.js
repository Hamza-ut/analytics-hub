import { API_BASE_URL } from "../api/config";
import axios from "axios";

// fetches pipelines list
export async function getPipelines(token) {
  if (!token) return [];
  try {
    const response = await axios({
      method: "GET",
      url: `${API_BASE_URL}/projects/pipelines/`,
      headers: { Authorization: `Token ${token}` },
    });
    return response.data;
  } catch (error) {
    console.error("Failed to fetch pipelines:", error);
    return []; // Returns empty array so .map() doesn't break
  }
}
