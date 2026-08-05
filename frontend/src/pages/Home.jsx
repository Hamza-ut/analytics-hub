import { useContext } from "react";
import { AuthContext } from "../contexts/AuthContext";

export default function Home() {
  // 1. Pull the 'user' object directly out of AuthContext
  const { user } = useContext(AuthContext);

  return (
    <div
      style={{ maxWidth: "600px", margin: "40px auto", textAlign: "center" }}
    >
      <h2>Welcome to Biofoundry Analytics Hub</h2>

      {/* 2. If 'user' exists in AuthContext, greet them by name! */}
      {user && (
        <p style={{ color: "#6c757d", lineHeight: "1.6" }}>
          Hello, {user.username}!
        </p>
      )}

      <p style={{ color: "#6c757d", lineHeight: "1.6" }}>
        Manage your analytical pipelines and microservice containers seamlessly
        from a single unified workspace.
      </p>
    </div>
  );
}
