import { createContext, useContext, useEffect, useState } from "react";
import {
  loginUser,
  registerUser,
  getCurrentUser,
} from "../services/api";

const AuthContext = createContext(null);

const TOKEN_KEY = "documind_token";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    const handleAuthExpired = () => {
      localStorage.removeItem(TOKEN_KEY);
      setUser(null);
    };

    window.addEventListener(
      "documind:auth-expired",
      handleAuthExpired
    );

    const restoreSession = async () => {
      const token = localStorage.getItem(TOKEN_KEY);

      if (!token) {
        setAuthLoading(false);
        return;
      }

      try {
        const data = await getCurrentUser();
        setUser(data.user);
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        setUser(null);
      } finally {
        setAuthLoading(false);
      }
    };

    restoreSession();

    return () => {
      window.removeEventListener(
        "documind:auth-expired",
        handleAuthExpired
      );
    };
  }, []);

  const login = async (email, password) => {
    const data = await loginUser(email, password);

    localStorage.setItem(TOKEN_KEY, data.token);
    setUser(data.user);

    return data;
  };

  const register = async (email, password) => {
    const data = await registerUser(email, password);

    localStorage.setItem(TOKEN_KEY, data.token);
    setUser(data.user);

    return data;
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        authLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside an AuthProvider."
    );
  }

  return context;
}