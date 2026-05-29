import "./Signup.css"; // This links Signup directly to its own styles!

function Signup() {
  return (
    <div className="signup-container">
      <h2>DigiBio Tools V2 Signup</h2>
      <form className="signup-form">
        <label htmlFor="username">Username</label>
        <input type="text" id="username" name="username" />

        <label htmlFor="email">Email</label>
        <input type="email" id="email" name="email" />

        <label htmlFor="password">Password</label>
        <input type="password" id="password" name="password" />

        <label htmlFor="confirmPassword">Confirm Password</label>
        <input type="password" id="confirmPassword" name="confirmPassword" />

        <button type="submit">Sign Up</button>
      </form>
    </div>
  );
}

export default Signup;
