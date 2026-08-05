import { API_BASE_URL } from "../api/config";
import axios from "axios";

// Create a new project with the provided data
export async function createProject(token, myData) {
  try {
    const response = await axios({
      method: "POST",
      url: `${API_BASE_URL}/projects/create/`,
      headers: {
        Authorization: `Token ${token}`,
      },
      data: myData,
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error(">>> DJANGO REJECTION DETAILS <<<", error.response.data);
    } else {
      console.error("Network Error:", error.message);
    }
    return null;
  }
}

// Fetch details of a specific project by its ID
export async function getProjectDetail(token, projectId) {
  if (!token || !projectId) return null;
  try {
    const response = await axios({
      method: "GET",
      url: `${API_BASE_URL}/projects/project/${projectId}/`,
      headers: { Authorization: `Token ${token}` },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error("Failed to fetch project details:", error.response.data);
    } else {
      console.error("Network Error:", error.message);
    }
    return null;
  }
}

// fetch all projects created by the user
export async function getCreatedProjects(token) {
  if (!token) return [];
  try {
    const response = await axios({
      method: "GET",
      url: `${API_BASE_URL}/projects/all/`,
      headers: { Authorization: `Token ${token}` },
    });
    return response.data;
  } catch (error) {
    console.error("Failed to fetch files:", error);
    return []; // Returns empty array so .map() doesn't break
  }
}

// Run the project with the given project ID
export async function runProject(token, projectId) {
  if (!token || !projectId) return null;
  try {
    const response = await axios({
      method: "POST",
      url: `${API_BASE_URL}/projects/run/${projectId}/`,
      headers: { Authorization: `Token ${token}` },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error("Failed to run project:", error.response.data);
    } else {
      console.error("Network Error:", error.message);
    }
    return null;
  }
}

// Delete the project with the given project ID
export async function deleteProject(token, projectId) {
  if (!token || !projectId) return null;
  try {
    const response = await axios({
      method: "DELETE",
      url: `${API_BASE_URL}/projects/project/${projectId}/`,
      headers: { Authorization: `Token ${token}` },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error("Failed to delete project:", error.response.data);
    } else {
      console.error("Network Error:", error.message);
    }
    return null;
  }
}
