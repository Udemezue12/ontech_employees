import React, { useState } from "react";
import Box from "@mui/material/Box";
import TextFields from "./forms/TextField";
import PasswordFields from "./forms/PasswordField";
import ButtonFields from "./forms/ButtonField";
import { Link, useNavigate } from "react-router-dom";
import { useForm, Controller } from "react-hook-form";

import { validateRegisterForm } from "./formValidators";
import axios from "axios";
import { MenuItem, Select, InputLabel, FormControl } from "@mui/material";
import { cookies } from "./Cookie";
//
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

function MaterialRegister() {
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
        role: formData.role,
        phone_number: formData.phone_number,
        name: formData.name,
        department: formData.department,
      };

      console.log("Payload being sent:", payload);
      const csrfToken = await fetchCSRFToken();

      await axios.post(
        "https://ontech-systems.onrender.com/api/register/",
        payload,
        {
          headers: {
            "Content-Type": "application/json",
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
    <div className="background">
      <form onSubmit={handleSubmit(submit)}>
        <Box className="whiteBox">
          <Box className="itemBox">
            <Box className="title">REGISTER</Box>
          </Box>

          {error && (
            <Box className="itemBox">
              <p style={{ color: "red", fontWeight: "bold" }}>{error}</p>
            </Box>
          )}

          {message && (
            <Box className="itemBox">
              <p style={{ color: "green", fontWeight: "bold" }}>{message}</p>
            </Box>
          )}

          <Box className="itemBox">
            <TextFields
              label="Email"
              name="email"
              control={control}
              defaultValue=""
            />
          </Box>

          <Box className="itemBox">
            <TextFields
              label="Username"
              name="username"
              control={control}
              defaultValue=""
            />
          </Box>

          <Box className="itemBox">
            <PasswordFields
              label="Password"
              name="password"
              control={control}
            />
          </Box>

          <Box className="itemBox">
            <PasswordFields
              label="Confirm Password"
              name="confirmPassword"
              control={control}
            />
          </Box>

          <Box className="itemBox">
            <TextFields label="Name" name="name" control={control} />
          </Box>

          <Box className="itemBox">
            <TextFields
              label="Phone Number"
              name="phone_number"
              control={control}
            />
          </Box>

          <Box className="itemBox">
            <FormControl fullWidth>
              <InputLabel id="role-label">Role</InputLabel>
              <Controller
                name="role"
                control={control}
                defaultValue="" // Ensure this is set to an empty string or valid default
                render={({ field }) => (
                  <Select labelId="role-label" label="Role" {...field}>
                    <MenuItem value="Hr_Manager">HR Manager</MenuItem>{" "}
                    {/* Updated value */}
                    <MenuItem value="Manager">Manager</MenuItem>
                    <MenuItem value="Employee">Employee</MenuItem>
                    <MenuItem value="Overall_Admin">Overall Admin</MenuItem>
                  </Select>
                )}
              />
            </FormControl>
          </Box>
          <Box className="itemBox">
            <FormControl fullWidth>
              <InputLabel id="department-label">Department</InputLabel>
              <Controller
                name="department"
                control={control}
                defaultValue=""
                render={({ field }) => (
                  <Select
                    labelId="department-label"
                    label="Department"
                    {...field}
                  >
                    <MenuItem value="Human Resources">Human Resources</MenuItem>{" "}
                    {/* Updated value */}
                    <MenuItem value="Engineering">Engineering</MenuItem>
                    <MenuItem value="Sales">Sales</MenuItem>
                    <MenuItem value="Marketing">Marketing</MenuItem>
                  </Select>
                )}
              />
            </FormControl>
          </Box>

          <Box className="itemBox">
            <ButtonFields label="Register" type="submit" />
          </Box>

          <Box className="itemBox">
            <Link to="/login" className="link">
              Already have an account?
            </Link>
          </Box>
        </Box>
      </form>
    </div>
  );
}

export default MaterialRegister;
