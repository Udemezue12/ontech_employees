import React, { useEffect, useState } from "react";
import axios from "axios";
import { cookies } from "./Cookie";

// Set up axios instance to handle the base URL and credentials
// const axiosInstance = axios.create({
//   baseURL: "https://ontech-systems.onrender.com", // Use the backend URL
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
    const csrfToken = fetchCSRFToken(); 
   

    if (!csrfToken) {
      console.error("CSRF Token is missing.");
      setError("CSRF Token is missing.");
      return;
    }

    try {
      const res = await axios.get(
        "https://ontech-systems.onrender.com/current_user/",
        {
          headers: {
            "X-CSRFToken": csrfToken, 
            Authorization: `Token ${token}`,
          },
        }
      );

      

      if (res.data && res.data.user) {
        setUser(res.data.user); 
      } else {
        setError("No user data returned.");
      }
    } catch (error) {
      console.error("Error fetching current user:", error); 

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
