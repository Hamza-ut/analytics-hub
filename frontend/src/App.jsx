import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./components/Home";
import Signup from "./components/Signup";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";

export default function App() {
  return (
    <div style={{ fontFamily: "sans-serif", padding: "20px" }}>
      {/* Navbar sits at the top of every page */}
      <Navbar />

      {/* Main content changes based on the URL */}
      <main style={{ padding: "20px 0" }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="*" element={<h3>404 Not Found</h3>} />
        </Routes>
      </main>
    </div>
  );
}
