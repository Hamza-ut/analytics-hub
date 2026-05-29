import "./Header.css";

function Header({
  isAuthenticated,
  homePageClick,
  loginClick,
  signupClick,
  dashboardClick,
  logoutClick,
}) {
  return (
    <header className="site-header">
      <h1>Digibio Tools</h1>

      <nav className="header-nav">
        <button className="nav-link" onClick={homePageClick}>
          Home
        </button>

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
  );
}

export default Header;
