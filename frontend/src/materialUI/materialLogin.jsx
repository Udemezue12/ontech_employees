
import React from "react";
import "./material.css";
import Box from "@mui/material/Box";
import TextFields from "./forms/TextField";
import PasswordFields from "./forms/PasswordField";
import axios from "axios";
import ButtonFields from "./forms/ButtonField";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { cookies } from "./Cookie";


export default function MaterialLogin() {
  const navigate = useNavigate();
  const { control, handleSubmit } = useForm();
  
  async function fetchCSRFToken() {
    try {
      
      await axios.get("https://ontech-systems.onrender.com/api/csrf/", {
        withCredentials: true, 
      });
      return cookies.get("csrftoken"); 
    } catch (err) {
      console.error("Failed to get CSRF token", err);
      return null;
    }
  }

  const submit = async (data) => {
    data.preventDefault()
    const csrfToken = await fetchCSRFToken();
  

    try {
     
      const response = await axios.post(
        "https://ontech-systems.onrender.com/api/login/",
        {
          email: data.email,
          password: data.password,
        },
        {
          headers: {
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true, 
        }
      );

      const { token, user } = response.data;

      if (!user || !user.id) {
        throw new Error("User data missing in response");
      }

      // 2. Save Knox token and user info
      localStorage.setItem("Token", token);
      localStorage.setItem("UserId", user.id);
      localStorage.setItem("UserEmail", user.email);
      localStorage.setItem("UserRole", user.role);
      localStorage.setItem("UserName", user.name);
      localStorage.setItem("UserDepartment", user.department);

      console.log("Login successful:", response.data);

      
      await axios.post(
        "https://ontech-systems.onrender.com/api/session-login/",
        
        {
          email: data.email,
          password: data.password,
        },
        {
          headers: {
            "X-CSRFToken": csrfToken,
          },

          withCredentials: true, 
        }
      );

      
      navigate("/dashboard", { replace: true });
    } catch (error) {
      console.error("Login failed:", error.response?.data || error.message);
    }
  };

  return (
    <div className="backgrounder">
      <form onSubmit={handleSubmit(submit)}>
        <Box className="whiteBox">
          <Box className="itemBox">
            <Box className="title">Login for Auth App</Box>
          </Box>

          <Box className="itemBox">
            <TextFields label="Email" name="email" control={control} />
          </Box>

          <Box className="itemBox">
            <PasswordFields
              label="Password"
              name="password"
              control={control}
            />
          </Box>

          <Box className="itemBox">
            <ButtonFields label="Login" type="submit" />
          </Box>

          <Box className="itemBox">
            <p>Or log in using your passkey:</p>
            <Link to="/login/fingerprint">
              <ButtonFields label="Login with Passkey" type="button" />
            </Link>
          </Box>

          <Box className="itemBox">
            <Link to="/register" className="link">
              Don't have an account?
            </Link>
          </Box>

          <Box className="itemBox">
            <Link to="/request/password_reset" className="link">
              Forgot Password? Reset it Here
            </Link>
          </Box>
        </Box>
      </form>
    </div>
  );
}
