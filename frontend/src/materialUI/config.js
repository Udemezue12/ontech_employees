export const API_BASE_URL =
  process.env.REACT_APP_ENV === "production"
    ? "https://your-production-domain.com/api"
    : "http://127.0.0.1:8000/";

export const rolePermissions = {
  admin: ["/admin-dashboard", "/home", "/profile", "/complaints", "/sales"],
  staff: ["/staff-dashboard", "/home", "/profile", "/complaints", "/sales"],
  user: ["/user-dashboard", "/home", "/profile"],
};


// src/config.js

const dev = {
  API_URL: "http://127.0.0.1:8000/api",
};

const prod = {
  API_URL: "https://your-production-url.com/api", // replace with your live API
};

const config = process.env.NODE_ENV === "development" ? dev : prod;

export default config;
