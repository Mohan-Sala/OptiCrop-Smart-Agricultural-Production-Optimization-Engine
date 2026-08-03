import React, { createContext, useContext, useState, useEffect } from "react";

export interface User {
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

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  register: (details: Omit<User, "registrationDate" | "lastLogin">, password?: string) => Promise<boolean>;
  logout: () => void;
  updateProfile: (updatedDetails: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const DEFAULT_USERS_KEY = "opticrop_registered_users";
const CURRENT_USER_KEY = "opticrop_current_user";

// Pre-populated default user
const DEFAULT_USER: User = {
  fullName: "John Doe",
  email: "john@farm.com",
  phone: "+1 (555) 123-4567",
  role: "Farmer",
  registrationDate: new Date("2025-01-15T10:00:00Z").toLocaleDateString(),
  lastLogin: new Date().toLocaleDateString(),
  bio: "Passionate about sustainable crop cultivation and leveraging AI for modern agricultural excellence.",
  location: "Green Valley Farms, California",
  occupation: "Senior Agronomist & Farm Owner",
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize Auth State from Local Storage
  useEffect(() => {
    // 1. Initialize registered users in LocalStorage if not exists
    const storedUsers = localStorage.getItem(DEFAULT_USERS_KEY);
    if (!storedUsers) {
      localStorage.setItem(DEFAULT_USERS_KEY, JSON.stringify([
        { ...DEFAULT_USER, password: "password123" }
      ]));
    }

    // 2. Check for current session
    const storedCurrentUser = localStorage.getItem(CURRENT_USER_KEY);
    if (storedCurrentUser) {
      setUser(JSON.parse(storedCurrentUser));
    }
    setIsLoading(false);
  }, []);

  // Login
  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      const storedUsers = localStorage.getItem(DEFAULT_USERS_KEY);
      if (storedUsers) {
        const users = JSON.parse(storedUsers) as Array<User & { password?: string }>;
        const foundUser = users.find(
          (u) => u.email.toLowerCase() === email.toLowerCase() && (!u.password || u.password === password)
        );

        if (foundUser) {
          const updatedUser: User = {
            ...foundUser,
            lastLogin: new Date().toLocaleDateString(),
          };
          delete (updatedUser as any).password; // do not store password in active session

          // Update registration users list with new lastLogin
          const updatedUsers = users.map((u) => 
            u.email.toLowerCase() === email.toLowerCase() ? { ...u, lastLogin: updatedUser.lastLogin } : u
          );
          localStorage.setItem(DEFAULT_USERS_KEY, JSON.stringify(updatedUsers));

          // Save current session
          localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(updatedUser));
          setUser(updatedUser);
          setIsLoading(false);
          return true;
        }
      }
      setIsLoading(false);
      return false;
    } catch (e) {
      console.error("Login failed:", e);
      setIsLoading(false);
      return false;
    }
  };

  // Register
  const register = async (
    details: Omit<User, "registrationDate" | "lastLogin">,
    password = "password123"
  ): Promise<boolean> => {
    setIsLoading(true);
    try {
      const storedUsers = localStorage.getItem(DEFAULT_USERS_KEY);
      const users = storedUsers ? JSON.parse(storedUsers) : [];

      // Check if user already exists
      if (users.some((u: User) => u.email.toLowerCase() === details.email.toLowerCase())) {
        setIsLoading(false);
        return false;
      }

      const newUser: User = {
        ...details,
        registrationDate: new Date().toLocaleDateString(),
        lastLogin: new Date().toLocaleDateString(),
      };

      // Add user to registration store
      users.push({ ...newUser, password });
      localStorage.setItem(DEFAULT_USERS_KEY, JSON.stringify(users));

      // Automatically sign in the user
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(newUser));
      setUser(newUser);
      setIsLoading(false);
      return true;
    } catch (e) {
      console.error("Registration failed:", e);
      setIsLoading(false);
      return false;
    }
  };

  // Logout
  const logout = () => {
    localStorage.removeItem(CURRENT_USER_KEY);
    setUser(null);
  };

  // Update Profile
  const updateProfile = (updatedDetails: Partial<User>) => {
    if (!user) return;

    const updatedUser: User = {
      ...user,
      ...updatedDetails,
    };

    // Save session
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(updatedUser));
    
    // Sync into registered users list
    const storedUsers = localStorage.getItem(DEFAULT_USERS_KEY);
    if (storedUsers) {
      const users = JSON.parse(storedUsers) as Array<User & { password?: string }>;
      const updatedUsers = users.map((u) =>
        u.email.toLowerCase() === user.email.toLowerCase() ? { ...u, ...updatedDetails } : u
      );
      localStorage.setItem(DEFAULT_USERS_KEY, JSON.stringify(updatedUsers));
    }

    setUser(updatedUser);
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
