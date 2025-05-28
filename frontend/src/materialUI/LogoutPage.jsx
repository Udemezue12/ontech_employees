// pages/LogoutPage.jsx
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { confirmAndLogout } from "./confirmAndLogout";


export default function LogoutPage() {
  const navigate = useNavigate();

  useEffect(() => {
    confirmAndLogout(navigate);
  }, [navigate]);

  return null; // No UI needed, just redirect after logout
}