import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  ApiError,
  apiRequest,
} from "../api/client";
import { AuthContext } from "./auth-context";

const TOKEN_STORAGE_KEY = "talentmatch_access_token";

const SESSION_RESTORE_ERROR_MESSAGE =
  "The TalentMatch API is temporarily unavailable. "
  + "Your saved session has been preserved. "
  + "Retry when the API is reachable.";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() =>
    localStorage.getItem(TOKEN_STORAGE_KEY),
  );
  const [user, setUser] = useState(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const [
    sessionRestoreError,
    setSessionRestoreError,
  ] = useState("");
  const [restoreAttempt, setRestoreAttempt] = useState(0);

  const clearSession = useCallback(() => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken(null);
    setUser(null);
    setSessionRestoreError("");
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    async function restoreSession() {
      if (!token) {
        setUser(null);
        setSessionRestoreError("");
        setIsInitializing(false);
        return;
      }

      setIsInitializing(true);
      setSessionRestoreError("");

      try {
        const currentUser = await apiRequest("/auth/me", {
          token,
          signal: controller.signal,
        });

        setUser(currentUser);
      } catch (error) {
        if (error.name === "AbortError") {
          return;
        }

        if (
          error instanceof ApiError
          && error.status === 401
        ) {
          clearSession();
          return;
        }

        setUser(null);
        setSessionRestoreError(
          SESSION_RESTORE_ERROR_MESSAGE,
        );
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
  }, [
    token,
    clearSession,
    restoreAttempt,
  ]);

  const retrySessionRestore = useCallback(() => {
    if (!token) {
      return;
    }

    setRestoreAttempt((attempt) => attempt + 1);
  }, [token]);

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
    setSessionRestoreError("");

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
      sessionRestoreError,
      retrySessionRestore,
      login,
      logout,
    }),
    [
      token,
      user,
      isInitializing,
      sessionRestoreError,
      retrySessionRestore,
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
