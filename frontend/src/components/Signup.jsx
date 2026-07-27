import { useState } from "react";
import { useForm } from "react-hook-form";

export default function Signup() {
  const {
    register,
    handleSubmit,
    getValues,
    reset,
    formState: { errors },
  } = useForm();

  const [apiMessage, setApiMessage] = useState(null);

  async function onSubmit(formData) {
    try {
      setApiMessage(null);

      const response = await fetch(
        "http://localhost:8000/api/v1/accounts/signup/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        // Format Django validation errors (e.g., username already taken)
        const formattedError = Object.entries(data)
          .map(
            ([field, msgs]) =>
              `${field}: ${Array.isArray(msgs) ? msgs.join(" ") : msgs}`,
          )
          .join(" | ");

        setApiMessage({
          type: "error",
          text: `Django rejected it: ${formattedError || "Signup failed."}`,
        });
        return;
      }

      // Shows "User created successfully." from your Django response
      setApiMessage({
        type: "success",
        text: data.message || "User created successfully!",
      });

      reset();
    } catch (error) {
      setApiMessage({
        type: "error",
        text: "Real network connectivity error occurred.",
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
