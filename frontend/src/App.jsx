import { useState } from "react";
import "./App.css";

import Header from "./components/Header.jsx";
import Footer from "./components/Footer.jsx";
import Homepage from "./components/Homepage.jsx";

import Signup from "./components/Signup.jsx";
import Login from "./components/Login.jsx";
import Dashboard from "./components/Dashboard.jsx";

function App() {
  const [view, setView] = useState("Homepage");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const homePageClick = () => {
    setView("Homepage");
  };

  const loginClick = () => {
    setView("Login");
  };

  const signupClick = () => {
    setView("Signup");
  };

  const dashboardClick = () => {
    setView("Dashboard");
  };

  const logoutClick = () => {
    setView("Homepage");
    setIsAuthenticated(false);
  };

  return (
    <div className="site-layout">
      <Header
        isAuthenticated={isAuthenticated}
        homePageClick={homePageClick}
        loginClick={loginClick}
        signupClick={signupClick}
        dashboardClick={dashboardClick}
        logoutClick={logoutClick}
      />

      <p>debugger for my learning, page_name: {view}</p>

      <main className="main-content">
        {view === "Homepage" && (
          <Homepage
            isAuthenticated={isAuthenticated}
            dashboardClick={dashboardClick}
            signupClick={signupClick}
          />
        )}

        {view === "Login" && <Login />}

        {view === "Signup" && <Signup />}

        {view === "Dashboard" && <Dashboard />}
      </main>

      <Footer />
    </div>
  );
}

export default App;
