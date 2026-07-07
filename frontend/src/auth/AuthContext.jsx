import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { apiRequest } from "../api/client";
import { AuthContext } from "./auth-context";

const TOKEN_STORAGE_KEY = "talentmatch_access_token";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() =>
    localStorage.getItem(TOKEN_STORAGE_KEY),
  );
  const [user, setUser] = useState(null);
  const [isInitializing, setIsInitializing] = useState(true);

  const clearSession = useCallback(() => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    async function restoreSession() {
      if (!token) {
        setIsInitializing(false);
        return;
      }

      try {
        const currentUser = await apiRequest("/auth/me", {
          token,
          signal: controller.signal,
        });

        setUser(currentUser);
      } catch (error) {
        if (error.name !== "AbortError") {
          clearSession();
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsInitializing(false);
        }
      }
    }

    restoreSession();

    return () => {
      controller.abort();
    };
  }, [token, clearSession]);

  const login = useCallback(async (email, password) => {
    const response = await apiRequest("/auth/login", {
      method: "POST",
      body: {
        email,
        password,
      },
    });

    const currentUser = await apiRequest("/auth/me", {
      token: response.access_token,
    });

    localStorage.setItem(
      TOKEN_STORAGE_KEY,
      response.access_token,
    );
    setToken(response.access_token);
    setUser(currentUser);

    return currentUser;
  }, []);

  const logout = useCallback(() => {
    clearSession();
  }, [clearSession]);

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token && user),
      isInitializing,
      login,
      logout,
    }),
    [
      token,
      user,
      isInitializing,
      login,
      logout,
    ],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}