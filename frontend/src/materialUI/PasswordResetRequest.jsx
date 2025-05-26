import React from "react";
import "./material.css";
import Box from "@mui/material/Box";
import TextFields from "./forms/TextField";
import PasswordFields from "./forms/PasswordField";
import ButtonFields from "./forms/ButtonField";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { AxiosInstance } from "./AxiosInstance";
import MyMessage from "./Message";
import axios from "axios";
import { cookies } from "./Cookie";

function PasswordResetRequest() {
  const navigate = useNavigate();
  const { control, handleSubmit } = useForm();
  const [showMessage, setShowMessage] = React.useState(false);
  async function fetchCSRFToken() {
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

  const submit = async (data) => {
    const csrfToken = await fetchCSRFToken();
    try {
      const payload = {
        email: data.email,
      };

      const response = await axios.post(
        "https://ontech-systems.onrender.com/api/password_reset/",
        payload,
        {
          headers: {
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        }
      ); // ✅ capture response

      setShowMessage(true);
    } catch (error) {
      console.error("Password reset error:", error);
      // Optionally show an error message
      // setErrorMessage("Something went wrong. Please try again.");
    }
  };

  return (
    <div className="backgrounder">
      {showMessage ? (
        <MyMessage
          text={
            "If your email exists, you have received an email with instructions for resetting your password."
          }
        />
      ) : null}
      <form onSubmit={handleSubmit(submit)}>
        <Box className="whiteBox">
          <Box className="itemBox">
            <Box className="title">Request Password Reset</Box>
          </Box>

          <Box className="itemBox">
            <TextFields label="Email" name="email" control={control} />
          </Box>

          <Box className="itemBox">
            <ButtonFields label="Request Password Reset" type="submit" />
          </Box>

          <Box className="itemBox"></Box>
        </Box>
      </form>
    </div>
  );
}

export default PasswordResetRequest;
