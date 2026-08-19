import { API_BASE_URL } from "../api/config";
import axios from "axios";

// fetches workflows list
export async function getWorkflows(token) {
  if (!token) return [];
  try {
    const response = await axios({
      method: "GET",
      url: `${API_BASE_URL}/projects/workflows/`,
      headers: { Authorization: `Token ${token}` },
    });
    return response.data;
  } catch (error) {
    console.error("Failed to fetch workflows:", error);
    return []; // Returns empty array so .map() doesn't break
  }
}
