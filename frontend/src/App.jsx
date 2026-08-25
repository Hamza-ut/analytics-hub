import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";

// for checking backend status
import { useBackendStatus } from "./contexts/BackendStatusContext";

// Components
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import PublicOnlyRoute from "./components/PublicOnlyRoute";
import Timepoint from "./components/workflows/Timepoint";
import TimepointResults from "./components/results/TimepointResults";

// Pages
import Home from "./pages/Home";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Project from "./pages/Project";
import ProjectDetail from "./pages/ProjectDetail";
import Workflows from "./pages/Workflows";
import IgvViewer from "./pages/IgvViewer";
import Practice from "./learning/Practice";

// for protected routes bounce it to login if not logged in
function AppLayout() {
  const { token } = useAuth();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div style={{ display: "flex", minHeight: "80vh" }}>
      <Sidebar />
      <main style={{ flex: 1, padding: "20px" }}>
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  const { isBackendDown } = useBackendStatus();

  return (
    <div style={{ fontFamily: "sans-serif", padding: "20px" }}>
      <Navbar />

      {isBackendDown && (
        <div
          style={{
            backgroundColor: "#fee2e2",
            color: "#991b1b",
            padding: "12px 20px",
            textAlign: "center",
          }}
        >
          Backend is unreachable. Please check your connection or try again
          later.
        </div>
      )}

      <main style={{ padding: "20px 0" }}>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Home />} />
          <Route
            path="/login"
            element={
              <PublicOnlyRoute>
                <Login />
              </PublicOnlyRoute>
            }
          />
          <Route
            path="/signup"
            element={
              <PublicOnlyRoute>
                <Signup />
              </PublicOnlyRoute>
            }
          />

          {/* Protected Routes */}
          <Route element={<AppLayout />}>
            {/* Redirect /dashboard to /projects so everything points to one URL */}
            <Route
              path="/dashboard"
              element={<Navigate to="/projects" replace />}
            />

            {/* Project Routes */}
            <Route path="/projects" element={<Dashboard />} />
            <Route path="/projects/new" element={<Project />} />
            <Route path="/projects/timepoint" element={<Timepoint />} />

            {/* Project Detail Route */}
            <Route path="/projects/:projectId" element={<ProjectDetail />} />

            {/* Uploads & Workflows */}
            <Route path="/uploads" element={<Upload />} />
            <Route path="/workflows" element={<Workflows />} />
            {/* Timepoint Results Route */}
            <Route
              path="/projects/:projectId/results"
              element={<TimepointResults />}
            />
          </Route>

          {/* IgvViewer Route */}
          <Route path="/igv" element={<IgvViewer />} />

          {/* Practice / learning sandbox — no login required */}
          <Route path="/practice" element={<Practice />} />

          {/* 404 Fallback */}
          <Route path="*" element={<h3>404 Not Found</h3>} />
        </Routes>
      </main>
    </div>
  );
}
