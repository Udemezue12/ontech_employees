// import React from "react";

// const RouleAuthContext = React.createContext();


// export const RoleAuthProvider = ({ children }) => {
//     const [isAuthenticated, setIsAuthenticated] = React.useState(false);
//     const [user, setUser] = React.useState(null);
//     React.useEffect(()=> {
//         const id = localStorage.getItem('UserId')
//         const token = localStorage.getItem('Token')
//         const email = localStorage.getItem('UserEmail')
//         const role = localStorage.getItem('UserRole')
//         const department = localStorage.getItem('UserDepartment')
//         const name = localStorage.getItem('UserName')
//         if (token && email) {
//             setIsAuthenticated(true)
//             setUser({
//                 'id': id,
//                 'email': email,
//                 'role': role,
//                 'department': department,
//                 'name': name
//             })
//         }

//     }, [])
//     return (
//         <RouleAuthContext.Provider value={{ isAuthenticated, setIsAuthenticated, user, setUser }}>
//             {children}
//         </RouleAuthContext.Provider>
//     )
// }
// export const useRoleAuth = () => {
//     const context = React.useContext(RouleAuthContext);
//     if (context === undefined) {
//         throw new Error("useRoleAuth must be used within a RoleAuthProvider");
//     }
//     return context;
// }

// RoleAuthContext.js
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
