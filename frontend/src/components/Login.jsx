import { useState, useContext } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../contexts/AuthContext";

export default function Login() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const [apiMessage, setApiMessage] = useState(null);

  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  async function onSubmit(formData) {
    try {
      setApiMessage(null);

      const response = await fetch(
        "http://localhost:8000/api/v1/accounts/login/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        },
      );

      const data = await response.json();

      if (response.ok) {
        login(data.token);
        navigate("/");
      } else {
        // Formats Django error response or defaults to standard text
        const errorText =
          data.non_field_errors?.join(" ") ||
          data.detail ||
          data.error ||
          "Invalid username or password!";

        setApiMessage({
          type: "error",
          text: errorText,
        });
      }
    } catch (error) {
      setApiMessage({
        type: "error",
        text: "Network connection error occurred.",
      });
      console.error(error);
    }
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
    </div>
  );
}
