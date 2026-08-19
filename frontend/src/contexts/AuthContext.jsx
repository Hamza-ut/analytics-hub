import { createContext, useContext, useState, useEffect } from "react";
import { useBackendStatus } from "./BackendStatusContext";
import { API_BASE_URL } from "../api/config";

// private, not to be exported
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("userToken"));
  const [user, setUser] = useState(null);
  const { isBackendDown } = useBackendStatus();

  function login(newToken, userData = null) {
    localStorage.setItem("userToken", newToken); // Save token to browser storage
    setToken(newToken); // Update React state
    if (userData) setUser(userData); // Update user details if available
  }

  async function logout() {
    const currentToken = localStorage.getItem("userToken");

    // 1. Tell Django to delete the token from the database
    if (currentToken) {
      try {
        await fetch(`${API_BASE_URL}/accounts/logout/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${currentToken}`,
          },
        });
      } catch (error) {
        console.error("Failed to invalidate token on server:", error);
      }
    }

    // 2. Always clean up frontend state no matter what
    localStorage.removeItem("userToken");
    setToken(null);
    setUser(null);
  }

  // Fetch user info whenever the token changes
  useEffect(() => {
    // async function defined inside
    async function fetchUser() {
      if (!token) {
        setUser(null);
        return;
      }
      try {
        const response = await fetch(`${API_BASE_URL}/accounts/user/`, {
          headers: { Authorization: `Token ${token}` },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          // Directly clean state here so useEffect doesn't rely on outside functions
          localStorage.removeItem("userToken");
          setToken(null);
          setUser(null);
        }
      } catch (error) {
        console.error("Error fetching user profile:", error);
      }
    }
    // Call it immediately!
    fetchUser();
  }, [token, isBackendDown]);

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use the AuthContext in other files without additional imports of useContext everytime but it needs suppression for eslint because of react-refresh rules.
// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
