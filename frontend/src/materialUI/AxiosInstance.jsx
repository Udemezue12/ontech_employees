// import axios from "axios";
// // import { API_BASE_URL } from "./../self-Practice/config";
// import config from "./config"

// export const API_URL = "http://127.0.0.1:8000/api";
// export const BASE_API_URL = "https://ontech-systems.onrender.com/api/";
// export const AxiosInstance = axios.create({
//   baseURL: config.API_URL,
//   timeout: 5000,
//   headers: {
//     "Content-Type": "application/json",
//     Accept: "application/json",
//   },
// });
// AxiosInstance.interceptors.request.use((config) => {
//   const token = localStorage.getItem("Token");
//   if (token) {
//     config.headers.Authorization = `Token ${token}`;
//   } else {
//     config.headers.Authoriation = ``;
//   }
//   return config;
// });
// AxiosInstance.interceptors.request.use(
//   (response) => {
//     return response;
//   },
//   (error) => {
//     if (error.response && error.response.status === 401) {
//       localStorage.removeItem("Token");
//       window.location.href = "/";
//     }
//   }
// );

// export function WindowLocation() {
//   return (window.location.href = "http://127.0.0.1:8000/");
// }

// // fuaa mwks vtnz kxpp

// src/setupAxiosInterceptors.js

// import axios from 'axios';
// import Swal from 'sweetalert2';

// axios.defaults.withCredentials = true;
// axios.interceptors.response.use(
//   (response) => response,
//   (error) => {
//     if (error.response && error.response.status === 401) {
//       console.warn("Unauthorized! Redirecting to login...");

//       localStorage.removeItem("Token");
//       localStorage.removeItem("UserId");

//       Swal.fire({
//         icon: 'warning',
//         title: 'Session Expired',
//         text: 'Please login again.',
//         confirmButtonText: 'OK',
//         timer: 4000,
//         timerProgressBar: true,
//       }).then(() => {
//         window.location.href = '/login';
//       });
//     }
//     return Promise.reject(error);
//   }
// );
///////
import axios from "axios";
import Cookies from "universal-cookie";
import Swal from "sweetalert2";

const cookies = new Cookies();

// Set global config
axios.defaults.withCredentials = true;

const AxiosInstance = axios.create({
  baseURL: "https://ontech-systems.onrender.com/api", // Adjust as needed
  withCredentials: true,
});

// Request interceptor: add CSRF + Knox Token
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

// Response interceptor: handle 401 Unauthorized
AxiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn("Unauthorized! Redirecting to login...");

      // Remove stored credentials
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

// CSRF helper
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
