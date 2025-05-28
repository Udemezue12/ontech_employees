import React from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import BootstrapButtonFields from "./forms/BootstrapButtonFields";
import BootstrapPasswordFields from "./forms/BootstrapPasswordFields";
import BootstrapTextFields from "./forms/BootstrapTextFields";
import { cookies } from "./Cookie";
import axios from "axios";
import "./bootstrap_style.css";

const MaterialLogin = () => {
  const { handleSubmit, control } = useForm();
  const navigate = useNavigate();

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

  const onSubmit = async (data) => {
    console.log("Login Data:", data);
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
    <div className="container-fluid fringer min-vh-100 d-flex justify-content-center align-items-center">
      <div
        className="card shadow-lg p-4 rounded-4 border-0 w-100"
        style={{ maxWidth: "420px", transition: "all 0.3s ease-in-out" }}
      >
        <form onSubmit={handleSubmit(onSubmit)}>
          <h4 className="text-center fw-bold mb-4">LOGIN</h4>

          {/* Email Field */}
          <div className="mb-3">
            <BootstrapTextFields
              label="Email"
              name="email"
              control={control}
              placeholder="Enter your email"
            />
          </div>

          {/* Password Field */}
          <div className="mb-3">
            <BootstrapPasswordFields
              label="Password"
              name="password"
              control={control}
              placeholder="Enter your password"
            />
          </div>

          {/* Login Button */}
          <div className="d-grid mb-3">
            <BootstrapButtonFields
              label="Login"
              type="submit"
              className="btn btn-primary rounded-pill"
            />
          </div>

          {/* Divider */}
          <div className="text-center text-muted mb-2">
            <small>Or log in using your passkey:</small>
          </div>

          {/* Passkey Button */}
          <div className="d-grid mb-3">
            <Link
              to="/login/fingerprint"
              className="btn btn-outline-secondary rounded-pill"
            >
              Login with Passkey
            </Link>
          </div>

          {/* Additional Links */}
          <div className="text-center">
            <small>
              <Link to="/register" className="text-decoration-none">
                Don’t have an account?
              </Link>
            </small>
            <br />
            <small>
              <Link to="/reset-password" className="text-decoration-none">
                Forgot Password? Reset it Here
              </Link>
            </small>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MaterialLogin;
