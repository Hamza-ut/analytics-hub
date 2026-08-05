import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../contexts/AuthContext";

export default function PublicOnlyRoute({ children }) {
  const { token } = useContext(AuthContext);

  // If token exists, user is ALREADY logged in!
  // Bounce them away from Login/Signup to Dashboard
  if (token) {
    return <Navigate to="/" replace />;
  }

  // If NOT logged in, render Login or Signup normally
  return children;
}
