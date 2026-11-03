import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { API_BASE_URL } from "../api/config";
import axios from "axios";
import { BACKEND_URL } from "../api/config";

export default function Login() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const [apiMessage, setApiMessage] = useState(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  async function onSubmit(myData) {
    try {
      setApiMessage(null);

      const response = await axios({
        method: "POST",
        url: `${API_BASE_URL}/accounts/login/`,
        data: myData,
        timeout: 1000,
      });

      login(response.data.token);
      navigate("/");
    } catch (error) {
      let errorText = "Cannot connect to server. Is backend running?";

      // 1. If error.response exists, it means backend IS running and sent a message
      if (error.response) {
        const errorData = error.response.data;
        errorText =
          errorData.error ||
          (errorData.non_field_errors && errorData.non_field_errors[0]) ||
          errorData.detail ||
          "Invalid username or password!";
      }

      // 2. Set the text message (works whether server is online or offline!)
      setApiMessage({
        type: "error",
        text: errorText,
      });

      console.error(error);
    }
  }

  // SSO: a real page navigation (like typing a URL), NOT axios —
  // the browser itself must travel to Django → Keycloak's login page → back.
  function startSsoLogin() {
    // TODO: put your backend's SSO start URL here, e.g.
    const ssoLoginUrl = `${BACKEND_URL}/api/v1/sso_experiment/sso-login/`;

    if (!ssoLoginUrl) {
      setApiMessage({ type: "error", text: "SSO login URL is not set yet." });
      return;
    }
    window.location.href = ssoLoginUrl;
  }

  return (
    <div
      style={{
        maxWidth: "400px",
        margin: "50px auto",
        fontFamily: "sans-serif",
      }}
    >
      <h2>Login</h2>

      {apiMessage && (
        <div
          style={{
            padding: "12px",
            borderRadius: "6px",
            marginBottom: "20px",
            fontSize: "14px",
            fontWeight: "bold",
            backgroundColor: "#f8d7da",
            color: "#721c24",
            border: "1px solid #f5c6cb",
          }}
        >
          {apiMessage.text}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <div>
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            placeholder="Enter username"
            {...register("username", {
              required: "Username is required",
            })}
          />
          {errors.username && (
            <p style={{ color: "red", margin: "4px 0" }}>
              {errors.username.message}
            </p>
          )}
        </div>

        <br />

        <div>
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            placeholder="Enter password"
            {...register("password", {
              required: "Password is required",
            })}
          />
          {errors.password && (
            <p style={{ color: "red", margin: "4px 0" }}>
              {errors.password.message}
            </p>
          )}
        </div>

        <br />

        <button
          type="submit"
          style={{ padding: "8px 16px", cursor: "pointer" }}
        >
          Log In
        </button>
      </form>

      {/* divider between the two ways to log in */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
          margin: "24px 0",
          color: "#888",
          fontSize: "14px",
        }}
      >
        <hr style={{ flex: 1, border: "none", borderTop: "1px solid #ddd" }} />
        or
        <hr style={{ flex: 1, border: "none", borderTop: "1px solid #ddd" }} />
      </div>

      <button
        type="button"
        onClick={startSsoLogin}
        style={{
          width: "100%",
          padding: "10px 16px",
          cursor: "pointer",
          fontSize: "15px",
          fontWeight: "bold",
          color: "#fff",
          backgroundColor: "#2c5282",
          border: "none",
          borderRadius: "6px",
        }}
      >
        Sign in with University account
      </button>
    </div>
  );
}
