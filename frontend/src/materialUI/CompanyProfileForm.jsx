import React, { useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  InputLabel,
  FormHelperText,
} from "@mui/material";
import axios from "axios";
import { cookies } from "./Cookie";
import "./material.css";

const CompanyProfileForm = () => {
  const userRole = localStorage.getItem("UserRole");

  const [formData, setFormData] = useState({
    company_name: "",
    company_address: "",
    company_email: "",
    company_phone: "",
    business_info: "",
    company_logo: null,
  });

  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const token = localStorage.getItem("Token");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    setFormData((prev) => ({ ...prev, company_logo: e.target.files[0] }));
  };

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
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setErrors({});
    setSuccessMsg("");

    const payload = new FormData();
    Object.entries(formData).forEach(([key, value]) => {
      if (value) payload.append(key, value);
    });

    const csrfToken = await fetchCSRFToken();

    try {
      const response = await axios.post(
        "https://ontech-systems.onrender.com/api/company/profile/",
        payload,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Token ${token}`,
            "X-CSRFToken": csrfToken,
          },
        }
      );
      setSuccessMsg("Company profile created successfully!");
      setFormData({
        company_name: "",
        company_address: "",
        company_email: "",
        company_phone: "",
        business_info: "",
        company_logo: null,
      });
    } catch (err) {
      if (err.response?.data) {
        setErrors(err.response.data);
      } else {
        setErrors({ detail: "An error occurred. Please try again." });
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (userRole !== "Overall_Admin") {
    return (
      <Typography variant="h6" color="error">
        Only Overall_Admin can create a company profile.
      </Typography>
    );
  }

  return (
    <div className="background">
      <Card sx={{ maxWidth: 600, mx: "auto", mt: 5 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Create Company Profile
          </Typography>
          <Box component="form" onSubmit={handleSubmit} noValidate>
            <TextField
              fullWidth
              label="Company Name"
              name="company_name"
              margin="normal"
              value={formData.company_name}
              onChange={handleChange}
              error={!!errors.company_name}
              helperText={errors.company_name}
              required
            />
            <TextField
              fullWidth
              label="Company Address"
              name="company_address"
              margin="normal"
              value={formData.company_address}
              onChange={handleChange}
              error={!!errors.company_address}
              helperText={errors.company_address}
              required
            />
            <TextField
              fullWidth
              label="Company Email"
              name="company_email"
              type="email"
              margin="normal"
              value={formData.company_email}
              onChange={handleChange}
              error={!!errors.company_email}
              helperText={errors.company_email}
            />
            <TextField
              fullWidth
              label="Company Phone"
              name="company_phone"
              margin="normal"
              value={formData.company_phone}
              onChange={handleChange}
              error={!!errors.company_phone}
              helperText={errors.company_phone}
            />
            <TextField
              fullWidth
              label="Business Info"
              name="business_info"
              multiline
              rows={4}
              margin="normal"
              value={formData.business_info}
              onChange={handleChange}
              error={!!errors.business_info}
              helperText={errors.business_info}
            />
            <Box mt={2}>
              <InputLabel>Company Logo</InputLabel>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                style={{ marginTop: "8px" }}
              />
              {errors.company_logo && (
                <FormHelperText error>{errors.company_logo}</FormHelperText>
              )}
            </Box>
            {errors.detail && (
              <Typography color="error" sx={{ mt: 2 }}>
                {errors.detail}
              </Typography>
            )}
            {successMsg && (
              <Typography color="success.main" sx={{ mt: 2 }}>
                {successMsg}
              </Typography>
            )}
            <Button
              type="submit"
              variant="contained"
              color="primary"
              sx={{ mt: 3 }}
              disabled={submitting}
            >
              {submitting ? "Submitting..." : "Create Profile"}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </div>
  );
};

export default CompanyProfileForm;
