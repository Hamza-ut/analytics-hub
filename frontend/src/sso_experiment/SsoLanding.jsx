import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

// SSO sandbox: Django's SSO callback redirects the browser here with ?token=<drf token>.
// We store it exactly like a password login would, then leave this URL.
export default function SsoLanding() {
  const [searchParams] = useSearchParams(); // read ?token=... from the address bar
  const navigate = useNavigate(); // move to another page from code
  const { login } = useAuth(); // the same login() your password Login page uses

  // runs once, right after the page appears
  useEffect(() => {
    const token = searchParams.get("token");

    if (token) {
      login(token); // saves to localStorage + fetches the user (AuthContext)
      navigate("/dashboard", { replace: true }); // replace: drop this URL (with the token) from history
    } else {
      navigate("/login", { replace: true }); // no token: something went wrong, back to login
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <p>Signing you in…</p>;
}
