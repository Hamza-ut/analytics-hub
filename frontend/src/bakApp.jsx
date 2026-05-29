import { useState } from "react"; // 1. We must import the state tool!
import "./App.css";
import Header from "./components/Header";
import Footer from "./components/Footer";

import Signup from "./components/Signup.jsx";
import Login from "./components/Login.jsx";
import Dashboard from "./components/Dashboard.jsx";

function App() {
  const [view, setView] = useState("Homepage");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  <Header
    isAuthenticated={isAuthenticated}
    setView={setView}
    logoutClick={logoutClick}
  />;

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
      <header className="site-header">
        <h1>Digibio Tools</h1>

        <nav className="header-nav">
          <button className="nav-link" onClick={homePageClick}>
            Home
          </button>

          {/* If user is logged in, show Dashboard & Logout. Otherwise, show Login & Register */}
          {isAuthenticated ? (
            <>
              <button className="nav-link" onClick={dashboardClick}>
                Dashboard
              </button>
              <button className="nav-link" onClick={logoutClick}>
                Logout
              </button>
            </>
          ) : (
            <>
              <button className="nav-link" onClick={loginClick}>
                Login
              </button>
              <button className="nav-link" onClick={signupClick}>
                Register
              </button>
            </>
          )}
        </nav>
      </header>
      <p>debugger for my learning, page_name: {view}</p>
      {/* this is where the change will happen*/}
      <div className="main-content">
        {/* for first state a simple home page*/}
        {view === "Homepage" && (
          <div>
            <h2>Welcome Digibio Tools</h2>

            <p>A platform for managing and analyzing biological data.</p>

            <h3>Features</h3>
            <ul>
              <li>
                Dose response curve: identifying optimal timepoint for analysis
              </li>
              <li>Organize projects and samples data</li>
              <li>Track processing history</li>
              <li>
                Visualize data with interactive plots (not implemented yet)
              </li>
              <li>sequence analysis (not implemented yet)</li>
            </ul>

            <br />
            {/* If logged in, show Dashboard button. Otherwise, show Get Started */}

            {isAuthenticated ? (
              <button className="action-btn" onClick={dashboardClick}>
                Dashboard
              </button>
            ) : (
              <button className="action-btn" onClick={signupClick}>
                Get Started
              </button>
            )}
          </div>
        )}

        {/* if state is login, we will redirect it to login component */}
        {view === "Login" && <Login />}

        {/* if state is signup, we will redirect it to signup component */}
        {view === "Signup" && <Signup />}

        {/* if state is dashboard, we will redirect it to dashboard component */}
        {view === "Dashboard" && <Dashboard />}
      </div>

      {/* FOOTER */}
      <footer className="site-footer">
        <hr className="divider" />
        <p>&copy; {new Date().getFullYear()} DigiBio Project</p>
        <p className="footer-links">
          <a href="https://digibio.ut.ee/" target="_blank" rel="noreferrer">
            Website
          </a>
          <span> | </span>
          <a
            href="https://github.com/estonian-biofoundry"
            target="_blank"
            rel="noreferrer"
          >
            GitHub
          </a>
          <span> | </span>
          <a href="https://www.linkedin.com/" target="_blank" rel="noreferrer">
            Linkedin
          </a>
          <span> | </span>
          <a
            href="https://www.instagram.com/digibio.est/"
            target="_blank"
            rel="noreferrer"
          >
            Instagram
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
