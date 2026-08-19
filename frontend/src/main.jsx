import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import { AuthProvider } from "./contexts/AuthContext.jsx";
import { BackendStatusProvider } from "./contexts/BackendStatusContext.jsx";
import Footer from "./components/Footer.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BackendStatusProvider>
      <AuthProvider>
        {/* 🎯 Wrap the entire App component so ALL sub-files can use navigate() safely */}
        <BrowserRouter>
          <App />
          <Footer />
        </BrowserRouter>
      </AuthProvider>
    </BackendStatusProvider>
  </React.StrictMode>,
);
