import React, { useEffect, useState } from "react";
import axios from "axios";
import { cookies } from "./Cookie";

// Set up axios instance to handle the base URL and credentials
// const axiosInstance = axios.create({
//   baseURL: "http://localhost:8000", // Use the backend URL
//   withCredentials: true, // Include cookies (session, csrf)
// });

const CurrentUser = () => {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);
  const token = localStorage.getItem("Token");
  const userId = localStorage.getItem("UserId");
  const user_email = localStorage.getItem("UserEmail");
  const user_role = localStorage.getItem("UserRole");

  // Fetch CSRF token from the cookies
  async function fetchCSRFToken() {
    try {
      const response = await axios.get(
        "https://ontech-systems.onrender.com/api/csrf/",
        {
          withCredentials: true, // ensure cookies are sent
        }
      );
      return cookies.get("csrftoken"); // Fetch it after Django sets it
    } catch (err) {
      console.error("Failed to get CSRF token", err);
      return null;
    }
  }

  // Function to fetch current user
  const fetchCurrentUser = async () => {
    const csrfToken = fetchCSRFToken(); // Get the CSRF token from cookies
    console.log("CSRF Token:", csrfToken); // Log CSRF token to check if it's present
    console.log("Token", token);
    console.log("Email:", user_email);

    console.log("Role:", user_role);

    if (!csrfToken) {
      console.error("CSRF Token is missing.");
      setError("CSRF Token is missing.");
      return;
    }

    try {
      const res = await axios.get("http://localhost:8000/current_user/", {
        headers: {
          "X-CSRFToken": csrfToken, // Send the CSRF token in the request header
          Authorization: `Token ${token}`,
        },
      });

      console.log("Response from /current_user:", res); // Log full response

      if (res.data && res.data.user) {
        setUser(res.data.user); // Set the user data if available
      } else {
        setError("No user data returned.");
      }
    } catch (error) {
      console.error("Error fetching current user:", error); // Log error if fetch fails

      if (error.response && error.response.status === 401) {
        setError("User not authenticated.");
      } else {
        setError("Failed to fetch user data.");
      }
    }
  };

  useEffect(() => {
    fetchCurrentUser(); // Fetch current user when the component is mounted
  }, []);

  return (
    <div>
      <h2>Current User</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {user ? <p>Welcome, {user.email}!</p> : <p>Loading user data...</p>}
    </div>
  );
};

export default CurrentUser;
