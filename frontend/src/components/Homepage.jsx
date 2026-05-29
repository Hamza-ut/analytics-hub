import "./Homepage.css";

function Homepage({ isAuthenticated, dashboardClick, signupClick }) {
  return (
    <div>
      <h2>Welcome Digibio Tools</h2>

      <p>A platform for managing and analyzing biological data.</p>

      <h3>Features</h3>

      <ul>
        <li>Dose response curve: identifying optimal timepoint for analysis</li>

        <li>Organize projects and samples data</li>

        <li>Track processing history</li>

        <li>Visualize data with interactive plots (not implemented yet)</li>

        <li>sequence analysis (not implemented yet)</li>
      </ul>

      <br />

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
  );
}

export default Homepage;
