import { useState } from "react";
import { useForm } from "react-hook-form";
import { API_BASE_URL } from "../api/config";
import axios from "axios";

export default function Signup() {
  const {
    register,
    handleSubmit,
    getValues,
    reset,
    formState: { errors },
  } = useForm();

  const [apiMessage, setApiMessage] = useState(null);

  async function onSubmit(myData) {
    try {
      setApiMessage(null);

      const response = await axios({
        method: "POST",
        url: `${API_BASE_URL}/accounts/signup/`,
        data: myData,
        timeout: 3000,
      });

      // SUCCESS: Runs when Django returns 201 CREATED
      setApiMessage({
        type: "success",
        text: response.data.message || "User created successfully!",
      });

      reset();
    } catch (error) {
      let errorText = "Cannot connect to server. Is backend running?";
      if (error.response) {
        const errorData = error.response.data;

        // Turn Django field errors object into a string: "username: A user with... | password: This..."
        const formattedErrors = Object.entries(errorData)
          .map(([field, msgs]) => {
            const messageText = Array.isArray(msgs) ? msgs.join(" ") : msgs;
            return `${field}: ${messageText}`;
          })
          .join(" | ");

        errorText = formattedErrors || "Signup failed.";
      }

      setApiMessage({
        type: "error",
        text: errorText,
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
      <h2>Sign Up</h2>

      {apiMessage && (
        <div
          style={{
            padding: "12px",
            borderRadius: "6px",
            marginBottom: "20px",
            fontSize: "14px",
            fontWeight: "bold",
            backgroundColor:
              apiMessage.type === "success" ? "#d4edda" : "#f8d7da",
            color: apiMessage.type === "success" ? "#155724" : "#721c24",
            border: `1px solid ${apiMessage.type === "success" ? "#c3e6cb" : "#f5c6cb"}`,
          }}
        >
          {apiMessage.text}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <label htmlFor="username">Username:</label>
        <input
          type="text"
          id="username"
          placeholder="Username"
          {...register("username", {
            required: "Username is required",
            minLength: {
              value: 3,
              message: "Username must be at least 3 characters",
            },
          })}
        />
        {errors.username && (
          <p style={{ color: "red", margin: "4px 0" }}>
            {errors.username.message}
          </p>
        )}
        <br />

        <label htmlFor="email">Email:</label>
        <input
          type="text"
          id="email"
          placeholder="Email"
          {...register("email", {
            required: "Email is required",
            pattern: {
              value: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
              message: "Invalid email format",
            },
          })}
        />
        {errors.email && (
          <p style={{ color: "red", margin: "4px 0" }}>
            {errors.email.message}
          </p>
        )}
        <br />

        <label htmlFor="password">Password:</label>
        <input
          type="password"
          id="password"
          placeholder="Password"
          {...register("password1", {
            required: "Password required",
            minLength: {
              value: 6,
              message: "Password must be at least 6 characters",
            },
          })}
        />
        {errors.password1 && (
          <p style={{ color: "red", margin: "4px 0" }}>
            {errors.password1.message}
          </p>
        )}
        <br />

        <label htmlFor="confirmPassword">Confirm Password:</label>
        <input
          type="password"
          id="confirmPassword"
          placeholder="Confirm Password"
          {...register("password2", {
            required: "Please confirm your password",
            validate: (value) =>
              value === getValues("password1") || "Passwords do not match!",
          })}
        />
        {errors.password2 && (
          <p style={{ color: "red", margin: "4px 0" }}>
            {errors.password2.message}
          </p>
        )}
        <br />

        <button
          type="submit"
          style={{ padding: "8px 16px", cursor: "pointer" }}
        >
          Sign Up
        </button>
      </form>
    </div>
  );
}
