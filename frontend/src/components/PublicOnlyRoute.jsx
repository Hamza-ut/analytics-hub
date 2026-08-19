import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function PublicOnlyRoute({ children }) {
  const { token } = useAuth();

  // If token exists, user is ALREADY logged in!
  // Bounce them away from Login/Signup to Dashboard
  if (token) {
    return <Navigate to="/" replace />;
  }

  // If NOT logged in, render Login or Signup normally
  return children;
}
