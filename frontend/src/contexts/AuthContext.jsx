import { createContext, useState, useEffect } from "react";
import { API_BASE_URL } from "../api/config";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("userToken"));
  const [user, setUser] = useState(null);

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
    // 1. Synchronous outer function (React is happy)

    if (!token) {
      setUser(null);
      return;
    }

    // 2. Mini async function defined inside
    async function fetchUser() {
      try {
        const response = await fetch(`${API_BASE_URL}/accounts/user/`, {
          headers: { Authorization: `Token ${token}` },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          logout();
        }
      } catch (error) {
        console.error("Error fetching user profile:", error);
      }
    }

    // 3. Call it immediately!
    fetchUser();
  }, [token]);

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
