import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "./contexts/AuthContext";

// Components
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import PublicOnlyRoute from "./components/PublicOnlyRoute";
import Timepoint from "./components/projects/Timepoint";
import TimepointResults from "./components/results/TimepointResults";

// Pages
import Home from "./pages/Home";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Project from "./pages/Project";
import ProjectDetail from "./pages/ProjectDetail";
import Pipeline from "./pages/Workflows";

function AppLayout() {
  const { token } = useContext(AuthContext);

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
  return (
    <div style={{ fontFamily: "sans-serif", padding: "20px" }}>
      <Navbar />

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

            {/* Uploads & Pipelines */}
            <Route path="/uploads" element={<Upload />} />
            <Route path="/workflows" element={<Pipeline />} />
            {/* Timepoint Results Route */}
            <Route
              path="/projects/:projectId/results"
              element={<TimepointResults />}
            />
          </Route>

          {/* 404 Fallback */}
          <Route path="*" element={<h3>404 Not Found</h3>} />
        </Routes>
      </main>
    </div>
  );
}
