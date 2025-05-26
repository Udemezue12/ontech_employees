// materialLogout.jsx
import axios from "axios";
import { cookies } from "./Cookie";

export async function fetchCSRFToken() {
  try {
    const response = await axios.get(
      "https://ontech-systems.onrender.com/api/csrf/",
      {
        withCredentials: true,
      }
    );
    return cookies.get("csrftoken");
  } catch (err) {
    console.error("Failed to get CSRF token", err);
    return null;
  }
}

export async function logoutUser(navigate) {
  const csrfToken = await fetchCSRFToken();

  try {
    const token = localStorage.getItem("Token");

    await axios.post(
      "https://ontech-systems.onrender.com/api/logout/",
      {},
      {
        headers: {
          Authorization: `Token ${token}`,
          "X-CSRFToken": csrfToken,
        },
        withCredentials: true,
      }
    );
  } catch (error) {
    console.error("Logout Failed:", error.response?.data);
  } finally {
    // Clear localStorage
    localStorage.removeItem("Token");
    localStorage.removeItem("UserId");
    localStorage.removeItem("UserEmail");
    localStorage.removeItem("UserRole");
    localStorage.removeItem("UserDepartment");
    localStorage.removeItem("UserName");
    cookies.remove("csrftoken");
    cookies.remove("sessionid");
    localStorage.clear();
    window.location.href = "/";
    // Navigate to login (handled externally by caller if needed)
  }
}
