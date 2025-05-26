// // src/components/ProtectedRoutes.js
// import React from "react";
// import { Navigate, Outlet } from "react-router-dom";

// const ProtectedRoutes = () => {
//   const isLoggedIn = localStorage.getItem("Token"); // or sessionStorage

//   return isLoggedIn ? <Outlet /> : <Navigate to="/login" replace />;
// };

// export default ProtectedRoutes;

// src/components/ProtectedRoutes.js
import React, { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { token } from './credentialKey';
const ProtectedRoutes = () => {
  const [authChecked, setAuthChecked] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    
    setIsLoggedIn(!!token);
    setAuthChecked(true);
  }, []);

  if (!authChecked) return null; // or loading spinner

  return isLoggedIn ? <Outlet /> : <Navigate to="/login" replace={true} />;
};

export default ProtectedRoutes;
