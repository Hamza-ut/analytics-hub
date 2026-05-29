import "./Login.css"; // This links Login directly to its own styles!

function Login() {
  return (
    <div className="login-container">
      <h2>DigiBio Tools V2 Login</h2>
      <form className="login-form">
        <label htmlFor="username">Username</label>
        <input type="text" id="username" name="username" />

        <label htmlFor="password">Password</label>
        <input type="password" id="password" name="password" />

        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default Login;
