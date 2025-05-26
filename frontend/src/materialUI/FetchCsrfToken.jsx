import { cookies } from "./Cookie";
import axios from "axios";

export const fetchCSRFToken = async () => {
  try {
    await axios.get("https://ontech-systems.onrender.com/api/csrf/", {
      withCredentials: true,
    });
    return cookies.get("csrftoken");
  } catch (err) {
    console.error("CSRF fetch error:", err);
    return null;
  }
};

export const csrfToken = await fetchCSRFToken();
export const csrf = await fetchCSRFToken();
export const csrftoken = await fetchCSRFToken();
