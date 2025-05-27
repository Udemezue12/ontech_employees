import React, { useState, useEffect } from "react";
import axios from "axios";
import LoadingDots from "./Loading";
import {
  Container,
  TextField,
  Button,
  Box,
  Card,
  CardContent,
  Typography,
  FormHelperText,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import "./material.css";
import { cookies } from "./Cookie";
// import { csrfToken } from "./FetchCsrfToken";
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
// const csrfToken = await fetchCSRFToken();
const EditProfile = () => {
  const [formData, setFormData] = useState({
    personal_details: "",
    resume: null,
    picture: null,
    country: "",
    state: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({
    resume: "",
    picture: "",
    signature: "",
  });

  const userId = localStorage.getItem("UserId");
  const token = localStorage.getItem("Token");

  const navigate = useNavigate();

  useEffect(() => {
    // Get userId and token from localStorage
    if (!userId) {
      console.error("No userId found in localStorage.");
      alert("No user found in localStorage. Please log in again.");
      return;
    }

    if (!token) {
      console.error("No token found in localStorage.");
      alert("You're not logged in. Please log in again.");
      return;
    }

    const fetchProfile = async () => {
      const csrfToken = await fetchCSRFToken();

      console.log("CSRF Token:", csrfToken);
      setIsLoading(true);
      if (!token) return;
      try {
        const response = await axios.put(
          `https://ontech-systems.onrender.com/api/my/profile/`,

          {
            headers: {
              Authorization: `Token ${token}`,
              "X-CSRFToken": csrfToken,
            },
            withCredentials: true,
          }
        );
        const { id, personal_details, country, state, resume, picture } =
          response.data;

        setFormData({
          personal_details: personal_details || "",
          resume: resume || null,
          picture: picture || null,

          country: country || "",
          state: state || "",
        });
        localStorage.setItem("ProfileId", id);
      } catch (error) {
        // You may add error handling here
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, [userId, token]);

  const handleInputChange = (e) => {
    const { name, type, value, files } = e.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: type === "file" ? files[0] : value,
    }));
  };

  const validateFiles = () => {
    let isValid = true;
    const newErrors = { resume: "", picture: "", signature: "" };

    if (
      formData.resume &&
      ![
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      ].includes(formData.resume.type)
    ) {
      newErrors.resume = "Resume must be a PDF or DOCX file.";
      isValid = false;
    }

    if (
      formData.picture &&
      !["image/jpeg", "image/png"].includes(formData.picture.type)
    ) {
      newErrors.picture = "Profile picture must be PNG or JPG.";
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateFiles()) return;

    setIsLoading(true);

    if (!token) {
      console.error("No token found in localStorage.");
      alert("You're not logged in. Please log in again.");
      setIsLoading(false);
      return;
    }
    if (!userId) {
      console.error("No userId found in localStorage.");
      alert("User ID not found. Cannot update profile.");
      setIsLoading(false);
      return;
    }

    const data = new FormData();
    Object.entries(formData).forEach(([key, value]) => {
      // Only append file if it's a File object, else append string/empty
      if (value instanceof File) {
        data.append(key, value);
      } else if (value !== null) {
        data.append(key, value);
      }
    });
    data.append("user", userId);
    const csrfToken = await fetchCSRFToken();

    console.log("CSRF Token:", csrfToken);

    try {
      const profileId = localStorage.getItem("ProfileId");
      await axios.put(
        `https://ontech-systems.onrender.com/api/my/profile/${profileId}/`,
        data,
        {
          headers: {
            Authorization: `Token ${token}`,
            "Content-Type": "multipart/form-data",
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        }
      );
      alert("Profile updated successfully!");
      navigate("/view/profile");
    } catch (error) {
      console.error("Error updating profile:", error);
      alert("An error occurred while updating your profile.");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingDots />;
  }

  return (
    <div className="finger">
      <Container
        maxWidth="sm"
        sx={{
          display: "flex",
          justifyContent: "center",
          height: "100vh",
          alignItems: "center",
        }}
      >
        <Card
          sx={{
            width: "100%",
            padding: 3,
            boxShadow: 6,
            borderRadius: "16px",
            transition: "transform 0.3s ease, box-shadow 0.3s ease",
            "&:hover": {
              transform: "scale(1.05)",
              boxShadow: "0 12px 20px rgba(0, 0, 0, 0.1)",
            },
            backgroundColor: "#f7f9fc",
          }}
        >
          <CardContent>
            <Typography
              variant="h5"
              component="h2"
              gutterBottom
              sx={{ fontWeight: "bold", color: "#2c3e50" }}
            >
              Edit Profile
            </Typography>
            <form onSubmit={handleSubmit}>
              <TextField
                label="Personal Details"
                name="personal_details"
                fullWidth
                multiline
                rows={4}
                value={formData.personal_details}
                onChange={handleInputChange}
                variant="outlined"
                margin="normal"
                required
                sx={{
                  "& .MuiOutlinedInput-root": { borderRadius: "12px" },
                  "& .MuiInputLabel-root": { color: "#7f8c8d" },
                }}
              />

              {/* Country - Manual Input */}
              <TextField
                label="Country"
                name="country"
                fullWidth
                margin="normal"
                required
                value={formData.country}
                onChange={handleInputChange}
                variant="outlined"
                sx={{
                  "& .MuiOutlinedInput-root": { borderRadius: "12px" },
                  "& .MuiInputLabel-root": { color: "#7f8c8d" },
                }}
              />
              <FormHelperText error>{errors.country}</FormHelperText>

              {/* State - Manual Input */}
              <TextField
                label="State"
                name="state"
                fullWidth
                margin="normal"
                required
                value={formData.state}
                onChange={handleInputChange}
                variant="outlined"
                sx={{
                  "& .MuiOutlinedInput-root": { borderRadius: "12px" },
                  "& .MuiInputLabel-root": { color: "#7f8c8d" },
                }}
              />
              <FormHelperText error>{errors.state}</FormHelperText>

              {/* Resume Upload */}
              <Box marginY={2}>
                <input
                  type="file"
                  name="resume"
                  onChange={handleInputChange}
                  accept=".pdf,.docx,.doc"
                  style={{ display: "none" }}
                  id="resume-upload"
                />
                <label htmlFor="resume-upload">
                  <Button
                    variant="outlined"
                    component="span"
                    sx={{ borderRadius: "8px", marginBottom: 1 }}
                  >
                    Upload Resume
                  </Button>
                </label>
                {formData.resume && (
                  <Typography
                    variant="body2"
                    color="textSecondary"
                    sx={{ marginTop: 1 }}
                  >
                    Resume: {formData.resume.name}
                  </Typography>
                )}
                {errors.resume && (
                  <p style={{ color: "red" }}>{errors.resume}</p>
                )}
              </Box>

              {/* Profile Picture Upload */}
              <Box marginY={2}>
                <input
                  type="file"
                  name="picture"
                  onChange={handleInputChange}
                  accept=".jpg,.jpeg,.png"
                  style={{ display: "none" }}
                  id="picture-upload"
                />
                <label htmlFor="picture-upload">
                  <Button
                    variant="outlined"
                    component="span"
                    sx={{ borderRadius: "8px", marginBottom: 1 }}
                  >
                    Upload Profile Picture
                  </Button>
                </label>
                {formData.picture && (
                  <Typography
                    variant="body2"
                    color="textSecondary"
                    sx={{ marginTop: 1 }}
                  >
                    Picture: {formData.picture.name}
                  </Typography>
                )}
                {errors.picture && (
                  <p style={{ color: "red" }}>{errors.picture}</p>
                )}
              </Box>

              {/* Signature Upload */}

              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                sx={{ borderRadius: "8px", marginTop: 3 }}
              >
                Update Profile
              </Button>
            </form>
          </CardContent>
        </Card>
      </Container>
    </div>
  );
};

export default EditProfile;
