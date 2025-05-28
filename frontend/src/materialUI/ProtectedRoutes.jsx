import React from "react";
import { Navigate, Outlet } from "react-router-dom";

const ProtectedRoutes = () => {
  const isLoggedIn = () => {
    const token = localStorage.getItem("Token");
    return token !== null;
  };
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace={true} />;
  }
  return <Outlet />;
};
export default ProtectedRoutes;
