import { NavLink } from "react-router-dom";

export default function Sidebar() {
  const linkStyle = ({ isActive }) => ({
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "10px 14px",
    borderRadius: "8px",
    textDecoration: "none",
    fontSize: "14px",
    fontWeight: isActive ? "600" : "500",
    color: isActive ? "#ffffff" : "#64748b",
    backgroundColor: isActive ? "#1e293b" : "transparent",
    transition: "all 0.15s ease-in-out",
  });

  return (
    <aside
      style={{
        width: "240px",
        backgroundColor: "#ffffff",
        borderRight: "1px solid #e2e8f0",
        padding: "24px 16px",
        display: "flex",
        flexDirection: "column",
        gap: "24px",
        boxSizing: "border-box",
        minHeight: "100vh",
      }}
    >
      <nav style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        {/* GROUP 1: PROJECTS & RUNS */}
        <div>
          <div
            style={{
              fontSize: "11px",
              fontWeight: "700",
              color: "#94a3b8",
              letterSpacing: "0.05em",
              marginBottom: "8px",
              paddingLeft: "8px",
            }}
          >
            PROJECT RUNS
          </div>

          <NavLink to="/projects" end style={linkStyle}>
            📊 <span>All Runs</span>
          </NavLink>

          <NavLink to="/projects/new" style={linkStyle}>
            ➕ <span>New Project</span>
          </NavLink>
        </div>

        {/* GROUP 2: UPLOADS & WORKFLOWS */}
        <div>
          <div
            style={{
              fontSize: "11px",
              fontWeight: "700",
              color: "#94a3b8",
              letterSpacing: "0.05em",
              marginBottom: "8px",
              paddingLeft: "8px",
            }}
          >
            DATA & WORKFLOWS
          </div>

          <NavLink to="/uploads" style={linkStyle}>
            📁 <span>Data Manager</span>
          </NavLink>

          <NavLink to="/workflows" style={linkStyle}>
            🛠️ <span>Workflows</span>
          </NavLink>
        </div>
      </nav>
    </aside>
  );
}
