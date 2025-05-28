import React, { useState } from "react";
import BootstrapTextFields from "./forms/BootstrapTextFields";
import BootstrapPasswordFields from "./forms/BootstrapPasswordFields";
import BootstrapButtonFields from "./forms/BootstrapButtonFields";
import BootstrapSelect from "./forms/BootstrapDropDown";
import "./bootstrap_style.css";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";

import { validateRegisterForm } from "./formValidators";
import axios from "axios";
import {cookies} from './Cookie'
export const fetchCSRFToken = async () => {
  try {
    await axios.get("https://ontech-systems.onrender.com/api/csrf/", {
      withCredentials: true,
       headers: {
          Accept: "application/json",
        },
    });
    return cookies.get("csrftoken");
  } catch (err) {
    console.error("CSRF fetch error:", err);
    return null;
  }
};
// export const fetchCSRFToken = async () => {
//   try {
//     const response = await axios.get(
//       "https://ontech-systems.onrender.com/api/csrf/",
//       {
//         withCredentials: true,
        // headers: {
        //   Accept: "application/json",
        // },
//       }
//     );

//     if (
//       typeof response.data === "string" &&
//       response.data.includes("<!doctype html")
//     ) {
//       throw new Error("Received HTML instead of JSON");
//     }

//     const csrfToken = response.data.csrfToken;

//     if (!csrfToken) {
//       throw new Error("CSRF token not found in response");
//     }

//     return csrfToken;
//   } catch (error) {
//     console.error("Failed to fetch CSRF token:", error);
//     return null;
//   }
// };
function OverallAdminRegister() {
  const navigate = useNavigate();
  const { control, handleSubmit } = useForm();
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const submit = async (formData) => {
    setError("");
    setMessage("");

    const validation = validateRegisterForm(formData);
    if (!validation.valid) {
      setError(validation.message);
      setMessage(validation.message);
      return;
    } else {
      setMessage(validation.message);
    }

    try {
      const payload = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        role: "Overall_Admin",
        phone_number: formData.phone_number,
        name: formData.name,
        department: formData.department,
      };
      const csrfToken = await fetchCSRFToken();

      console.log("Payload being sent:", payload);

      await axios.post(
        "https://ontech-systems.onrender.com/api/overallAdmin_register/",
        payload,
        {
          headers: {
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        }
      );
      setMessage("Registration successful! Redirecting to login...");
      setTimeout(() => navigate("/login"), 2000);
    } catch (error) {
      const response = error.response?.data;
      console.error("Registration Failed:", error);
      console.error("Response Data:", response);

      if (response) {
        if (response.email?.[0]) {
          setError("Email already in use.");
        } else if (response.username?.[0]) {
          setError("Username already taken.");
        } else if (response.phone_number?.[0]) {
          setError("Phone number already exists.");
        } else {
          setError("Registration failed. Please check your inputs.");
        }
      } else {
        setError("Something went wrong. Please try again.");
      }
    }
  };

  return (
    <div className="container-fluid fringer min-vh-100 d-flex justify-content-center align-items-center">
      <div
        className="card shadow-lg p-4 rounded-4 border-0 w-100"
        style={{ maxWidth: "420px", transition: "all 0.3s ease-in-out" }}
      >
        <form onSubmit={handleSubmit(submit)}>
          <h4 className="text-center fw-bold mb-4">Login for Auth App</h4>

          {error && (
            <div className="alert alert-danger text-center py-2" role="alert">
              {error}
            </div>
          )}

          {message && (
            <div className="alert alert-success text-center py-2" role="alert">
              {message}
            </div>
          )}

          <div className="mb-3">
            <BootstrapTextFields
              label="Email"
              name="email"
              control={control}
              placeholder="Enter your email"
            />
          </div>

          <div className="mb-3">
            <BootstrapTextFields
              label="Username"
              name="username"
              control={control}
              placeholder="Enter your username"
            />
          </div>

          <div className="mb-3">
            <BootstrapPasswordFields
              label="Password"
              name="password"
              control={control}
              placeholder="Enter your password"
            />
          </div>

          <div className="mb-3">
            <BootstrapPasswordFields
              label="Confirm Password"
              name="confirmPassword"
              control={control}
            />
          </div>

          <div className="mb-3">
            <BootstrapTextFields
              label="Name"
              name="name"
              control={control}
              placeholder="Enter your name"
            />
          </div>

          <div className="mb-3">
            <BootstrapTextFields
              label="Phone Number"
              name="phone_number"
              control={control}
              placeholder="Enter your phone number"
            />
          </div>

          <div className="mb-3">
            <BootstrapSelect
              label="Department"
              name="department"
              control={control}
            />
          </div>

          <div className="d-grid mb-3">
            <BootstrapButtonFields
              label="Login"
              type="submit"
              className="btn btn-primary rounded-pill"
            />
          </div>

          <div className="text-center">
            <small>
              <Link to="/login" className="text-decoration-none">
                Already have an account?
              </Link>
            </small>
          </div>
        </form>
      </div>
    </div>
  );
}

export default OverallAdminRegister;
