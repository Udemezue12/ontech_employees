// pages/LogoutPage.jsx
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { logoutUser } from "./materialLogout";
import { confirmAndLogout } from "./confirmAndLogout";

// export default function LogoutPage() {
//   const navigate = useNavigate();

//   useEffect(() => {
//     async function doLogout() {
//       await logoutUser(); // no navigate passed, we handle it here
//       navigate("/login", { replace: true });
//     }

//     doLogout();
//   }, [navigate]);

//   return <p>Logging you out...</p>;
// }
export default function LogoutPage() {
  const navigate = useNavigate();

  useEffect(() => {
    confirmAndLogout(navigate);
  }, [navigate]);

  return null; // No UI needed, just redirect after logout
}