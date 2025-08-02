
import axios from "axios";
import Cookies from "universal-cookie";
import Swal from "sweetalert2";

const cookies = new Cookies();


axios.defaults.withCredentials = true;

const AxiosInstance = axios.create({
  baseURL: "https://ontech-systems.onrender.com/api", 
  withCredentials: true,
});


AxiosInstance.interceptors.request.use(
  (config) => {
    const csrfToken = getCookie("csrftoken");
    if (csrfToken) {
      config.headers["X-CSRFToken"] = csrfToken;
    }

    const token = cookies.get("authToken");
    if (token) {
      config.headers["Authorization"] = `Token ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);


AxiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn("Unauthorized! Redirecting to login...");

   
      localStorage.removeItem("Token");
      localStorage.removeItem("UserId");
      cookies.remove("authToken", { path: "/" });

      Swal.fire({
        icon: "warning",
        title: "Session Expired",
        text: "Please login again.",
        confirmButtonText: "OK",
        timer: 4000,
        timerProgressBar: true,
      }).then(() => {
        window.location.href = "/login";
      });
    }
    return Promise.reject(error);
  }
);


function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export default AxiosInstance;
