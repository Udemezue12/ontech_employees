
import React, { createContext, useState, useContext } from "react";

const RoleAuthContext = createContext();

export function RoleAuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  const login = (userData) => {
    setIsAuthenticated(true);
    setUser(userData);
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <RoleAuthContext.Provider
      value={{ isAuthenticated, user, login, logout }}
    >
      {children}
    </RoleAuthContext.Provider>
  );
}

export function useRoleAuth() {
  return useContext(RoleAuthContext);
}
