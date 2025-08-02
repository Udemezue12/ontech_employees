import React from "react";
import "./material.css";

import { useNavigate, useLocation } from "react-router-dom";

import { useState } from "react";

import axios from "axios";



export const PasswordReset = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const queryParams = new URLSearchParams(location.search);
  const token = queryParams.get("token");
  const email = queryParams.get("email");

  const [formData, setFormData] = useState({
    newPassword: "",
    confirmPassword: "",
  });

  const [message, setMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setErrorMessage("");

    const { newPassword, confirmPassword } = formData;

    if (newPassword !== confirmPassword) {
      setErrorMessage("Passwords do not match 😢");
      return;
    }

    try {
      await axios.post(
        "https://ontech-systems.onrender.com/api/password_reset/confirm/",
        {
          email,
          token,
          password: newPassword,
        }
      );

      setMessage("✨ Password reset successful!");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      const data = err.response?.data;

      if (data?.password?.some((msg) => msg.includes("entirely numeric"))) {
        setErrorMessage("❗ Password cannot be entirely numeric.");
      } else if (data?.password?.length) {
        setErrorMessage(data.password.join(" "));
      } else if (data?.non_field_errors?.length) {
        setErrorMessage(data.non_field_errors.join(" "));
      } else {
        setErrorMessage("Something went wrong. Please try again later.");
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-100 to-purple-100 px-4">
      <div className="bg-white shadow-xl rounded-3xl p-8 w-full max-w-lg transition duration-300 ease-in-out transform hover:scale-[1.01]">
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-6">
          🔐 Reset Password
        </h2>

        {errorMessage && (
          <div className="mb-4 px-4 py-3 rounded bg-red-100 text-red-700 font-medium">
            {errorMessage}
          </div>
        )}

        {message && (
          <div className="mb-4 px-4 py-3 rounded bg-green-100 text-green-700 font-medium">
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label
              htmlFor="newPassword"
              className="block text-sm font-medium text-gray-700"
            >
              New Password
            </label>
            <input
              type="password"
              name="newPassword"
              id="newPassword"
              placeholder="Enter new password"
              value={formData.newPassword}
              onChange={handleChange}
              className="mt-1 w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium text-gray-700"
            >
              Confirm Password
            </label>
            <input
              type="password"
              name="confirmPassword"
              id="confirmPassword"
              placeholder="Confirm new password"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="mt-1 w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-2.5 rounded-lg hover:opacity-90 transition duration-300"
          >
            🔁 Reset Password
          </button>
        </form>
      </div>
    </div>
  );
};
