import { useState, useEffect, useCallback, ReactNode } from "react";
import AuthContext, { User } from "./AuthContext";
import loginApi from "../services/auth/login";
import logoutApi from "../services/auth/logout";
import refreshApi from "../services/auth/refresh";
import getUserApi from "../services/auth/getUser";

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function init() {
      try {
        const userData = await getUserApi();
        setUser(userData);
      } catch {
        try {
          const { access } = await refreshApi();
          setAccessToken(access);
          const userData = await getUserApi(access);
          setUser(userData);
        } catch {
          setUser(null);
          setAccessToken(null);
        }
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const login = useCallback(async (username: string, password: string): Promise<void> => {
    const { access } = await loginApi(username, password);
    setAccessToken(access);
    const userData = await getUserApi(access);
    setUser(userData);
  }, []);

  const logout = useCallback(async (): Promise<void> => {
    try {
      await logoutApi();
    } catch (error) {
      console.error("Logout API failed:", error);
    } finally {
      setUser(null);
      setAccessToken(null);
    }
  }, []);

  const refresh = useCallback(async (): Promise<string> => {
    try {
      const { access } = await refreshApi();
      setAccessToken(access);
      return access;
    } catch {
      setUser(null);
      setAccessToken(null);
      throw new Error("Refresh failed");
    }
  }, []);

  const value = { user, accessToken, login, logout, refresh, loading };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
