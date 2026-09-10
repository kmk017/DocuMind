import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import "./AuthPage.css";

function AuthPage() {
  const { login, register } = useAuth();

  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const isLogin = mode === "login";

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    const trimmedEmail = email.trim();

    if (!trimmedEmail || !password) {
      setError("Email and password are required.");
      return;
    }

    if (!isLogin && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (!isLogin && password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    setLoading(true);

    try {
      if (isLogin) {
        await login(trimmedEmail, password);
      } else {
        await register(trimmedEmail, password);
      }
    } catch (err) {
      setError(
        err.message ||
          "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setMode(isLogin ? "register" : "login");
    setError("");
    setPassword("");
    setConfirmPassword("");
  };

  return (
    <main className="auth-page">
      <div className="auth-card">

        <div className="auth-brand">
          <div className="auth-logo">D</div>

          <div>
            <h1>DocuMind</h1>
            <p>AI-powered document intelligence</p>
          </div>
        </div>

        <div className="auth-heading">
          <h2>
            {isLogin
              ? "Welcome back"
              : "Create your account"}
          </h2>

          <p>
            {isLogin
              ? "Sign in to access your documents."
              : "Start understanding your documents with AI."}
          </p>
        </div>

        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >
          <div className="auth-field">
            <label htmlFor="auth-email">
              Email
            </label>

            <input
              id="auth-email"
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              placeholder="you@example.com"
              autoComplete="email"
              disabled={loading}
            />
          </div>

          <div className="auth-field">
            <label htmlFor="auth-password">
              Password
            </label>

            <input
              id="auth-password"
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Enter your password"
              autoComplete={
                isLogin
                  ? "current-password"
                  : "new-password"
              }
              disabled={loading}
            />
          </div>

          {!isLogin && (
            <div className="auth-field">
              <label htmlFor="auth-confirm-password">
                Confirm password
              </label>

              <input
                id="auth-confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(event.target.value)
                }
                placeholder="Confirm your password"
                autoComplete="new-password"
                disabled={loading}
              />
            </div>
          )}

          {error && (
            <div
              className="auth-error"
              role="alert"
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >
            {loading
              ? isLogin
                ? "Signing in..."
                : "Creating account..."
              : isLogin
              ? "Sign in"
              : "Create account"}
          </button>
        </form>

        <div className="auth-switch">
          <span>
            {isLogin
              ? "Don't have an account?"
              : "Already have an account?"}
          </span>

          <button
            type="button"
            onClick={switchMode}
            disabled={loading}
          >
            {isLogin
              ? "Create account"
              : "Sign in"}
          </button>
        </div>

      </div>
    </main>
  );
}

export default AuthPage;