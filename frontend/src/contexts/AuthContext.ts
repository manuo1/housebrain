import { createContext } from "react";

export interface User {
  username: string;
}

export interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<string>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export default AuthContext;
