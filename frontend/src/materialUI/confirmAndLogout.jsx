// utils/confirmAndLogout.js
import Swal from "sweetalert2";
import { logoutUser } from "./materialLogout";

export async function confirmAndLogout(navigate) {
  const result = await Swal.fire({
    icon: "warning",
    title: "Confirm Logout",
    text: "Do you want to Logout?",
    confirmButtonColor: "#3085d6",
    showCancelButton: true,
    confirmButtonText: "Yes, Logout",
    cancelButtonText: "Cancel",
  });

  if (result.isConfirmed) {
    await logoutUser();
    // navigate("/", { replace: true });
    window.location.href = "/";
  }
}
