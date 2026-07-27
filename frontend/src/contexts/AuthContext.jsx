import { createContext, useState, useEffect } from "react";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("userToken"));
  const [user, setUser] = useState(null);

  function login(newToken, userData = null) {
    localStorage.setItem("userToken", newToken); // Save token to browser storage
    setToken(newToken); // Update React state
    if (userData) setUser(userData); // Update user details if available
  }

  function logout() {
    localStorage.removeItem("userToken"); // Delete token from browser storage
    setToken(null); // Clear token state
    setUser(null); // Clear user state
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
        const response = await fetch(
          "http://localhost:8000/api/v1/accounts/user/",
          {
            headers: { Authorization: `Token ${token}` },
          },
        );

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
