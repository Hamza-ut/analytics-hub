import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Navbar() {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogoutClick() {
    logout();
    navigate("/login");
  }

  return (
    <header
      style={{
        display: "flex",
        justifyContent: "space-between",
        backgroundColor: "#f8f9fa",
        padding: "15px 20px",
        alignItems: "center",
        borderBottom: "1px solid #dee2e6",
      }}
    >
      {/* Brand logo/name as a Home link */}
      <Link
        to="/"
        style={{
          fontSize: "20px",
          fontWeight: "bold",
          color: "#212529",
          textDecoration: "none",
        }}
      >
        🧬 Analytics Hub
      </Link>

      <nav style={{ display: "flex", gap: "15px", alignItems: "center" }}>
        {token ? (
          /* --- LOGGED IN VIEW --- */
          <>
            <span style={{ color: "#6c757d" }}>
              👤 {user ? user.username : "Loading..."}
            </span>

            <Link to="/dashboard">Dashboard</Link>

            <button
              onClick={handleLogoutClick}
              style={{
                background: "none",
                border: "none",
                color: "red",
                cursor: "pointer",
                fontSize: "16px",
                padding: 0,
              }}
            >
              Logout
            </button>
          </>
        ) : (
          /* --- LOGGED OUT VIEW --- */
          <>
            <Link to="/login">Login</Link>
            <Link to="/signup">Signup</Link>
          </>
        )}
      </nav>
    </header>
  );
}
