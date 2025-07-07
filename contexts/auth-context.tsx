"use client";

import React, { createContext, useContext, ReactNode } from "react";
import { useAuth } from "@/hooks/use-auth";

interface AuthContextType {
  user: {
    id: string;
    username: string;
    email?: string;
    full_name?: string;
  } | null;
  isLoading: boolean;
  error: string | null;
  login: (credentials: { username: string; password: string }) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  fetchUserInfo: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const auth = useAuth();

  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
};

export const useAuthContext = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuthContext must be used within an AuthProvider");
  }
  return context;
};
