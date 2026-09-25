import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { api, getStoredToken, clearStoredTokens, UserProfile } from "./api";

export interface User {
  id: string;
  fullName: string;
  email: string;
  phone: string;
  role: string;
  avatar?: string;
  registrationDate: string;
  lastLogin: string;
  bio?: string;
  location?: string;
  occupation?: string;
}

export interface AuthActionResult {
  success: boolean;
  error?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<AuthActionResult>;
  register: (details: Omit<User, "id" | "registrationDate" | "lastLogin">, password: string) => Promise<AuthActionResult>;
  logout: () => void;
  updateProfile: (updatedDetails: Partial<User>) => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function mapBackendProfileToUser(p: UserProfile): User {
  return {
    id: p.id,
    fullName: p.full_name,
    email: p.email,
    phone: p.phone || "",
    role: p.role,
    avatar: p.avatar_url || "",
    registrationDate: p.created_at ? new Date(p.created_at).toLocaleDateString() : "",
    lastLogin: p.last_login ? new Date(p.last_login).toLocaleDateString() : new Date().toLocaleDateString(),
    bio: p.bio || "",
    location: p.location || "",
    occupation: p.occupation || "",
  };
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Restore authenticated session from MongoDB Atlas via JWT token on mount
  const restoreSession = useCallback(async () => {
    const token = getStoredToken();
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const profile = await api.profile.get();
      setUser(mapBackendProfileToUser(profile));
    } catch (err) {
      console.warn("Session restore failed, clearing token:", err);
      clearStoredTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    restoreSession();

    const handleUnauthorized = () => {
      setUser(null);
    };

    window.addEventListener("opticrop:unauthorized", handleUnauthorized);
    return () => {
      window.removeEventListener("opticrop:unauthorized", handleUnauthorized);
    };
  }, [restoreSession]);

  // Login against MongoDB Atlas
  const login = async (email: string, password: string): Promise<AuthActionResult> => {
    setIsLoading(true);
    try {
      const response = await api.auth.login({ email, password });
      setUser(mapBackendProfileToUser(response.user));
      setIsLoading(false);
      return { success: true };
    } catch (e: any) {
      console.error("Login failed:", e);
      setIsLoading(false);
      return { success: false, error: e?.message || "Login failed" };
    }
  };

  // Register new user into MongoDB Atlas
  const register = async (
    details: Omit<User, "id" | "registrationDate" | "lastLogin">,
    password: string
  ): Promise<AuthActionResult> => {
    setIsLoading(true);
    try {
      await api.auth.register({
        email: details.email,
        password,
        full_name: details.fullName,
      });

      // Automatically log in with the new credentials
      const loginRes = await api.auth.login({
        email: details.email,
        password,
      });

      setUser(mapBackendProfileToUser(loginRes.user));
      setIsLoading(false);
      return { success: true };
    } catch (e: any) {
      console.error("Registration failed:", e);
      setIsLoading(false);
      return { success: false, error: e?.message || "Registration failed" };
    }
  };

  // Logout
  const logout = () => {
    api.auth.logout();
    setUser(null);
  };

  // Update profile in MongoDB Atlas
  const updateProfile = async (updatedDetails: Partial<User>) => {
    if (!user) return;

    try {
      const updatedProfile = await api.profile.update({
        full_name: updatedDetails.fullName ?? user.fullName,
        phone: updatedDetails.phone ?? user.phone,
        bio: updatedDetails.bio ?? user.bio,
        location: updatedDetails.location ?? user.location,
        occupation: updatedDetails.occupation ?? user.occupation,
        avatar_url: updatedDetails.avatar ?? user.avatar,
      });

      setUser(mapBackendProfileToUser(updatedProfile));
    } catch (e) {
      console.error("Failed to update profile:", e);
      throw e;
    }
  };

  const refreshProfile = async () => {
    try {
      const profile = await api.profile.get();
      setUser(mapBackendProfileToUser(profile));
    } catch (e) {
      console.error("Failed to refresh profile:", e);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        updateProfile,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
