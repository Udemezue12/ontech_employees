import React, { useState } from "react";
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
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import "./material.css";
import { cookies } from "./Cookie";
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

const Profile = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    personal_details: "",
    resume: null,
    picture: null,
    // signature: null,
    country: "",
    state: "",
  });

  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({
    resume: "",
    picture: "",
  });

  const userId = localStorage.getItem("UserId");
  const token = localStorage.getItem("Token");


  const handleInputChange = (e) => {
    const { name, type, value, files } = e.target;
    if (type === "file") {
      setFormData({ ...formData, [name]: files[0] });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const validateFiles = () => {
    let isValid = true;
    const newErrors = { resume: "", picture: "" };

    if (formData.resume) {
      const validFormats = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      ];
      if (!validFormats.includes(formData.resume.type)) {
        newErrors.resume = "Resume must be a PDF or DOCX file.";
        isValid = false;
      }
    }

    if (formData.picture) {
      const validFormats = ["image/jpeg", "image/png"];
      if (!validFormats.includes(formData.picture.type)) {
        newErrors.picture = "Profile picture must be PNG or JPG.";
        isValid = false;
      }
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

    const data = new FormData();
    data.append("personal_details", formData.personal_details);
    data.append("resume", formData.resume);
    data.append("picture", formData.picture);

    data.append("country", formData.country);
    data.append("state", formData.state);
    data.append("user", userId);

    const debugPayload = {
      personal_details: formData.personal_details,
      resume: formData.resume?.name || null,
      picture: formData.picture?.name || null,
     
      country: formData.country?.name || null,
      state: formData.state?.name || null,
    };

    
    const csrfToken = await fetchCSRFToken();
  

    try {
      await axios.post(
        `https://ontech-systems.onrender.com/api/create/profile/`,
        data,
        {
          headers: {
            Authorization: `Token ${token}`, // Using Knox token
            "Content-Type": "multipart/form-data",
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        }
      );
      alert("Profile created successfully!");
      navigate("/view/profile");
    } catch (error) {
      if (
        error.response?.data?.detail === "Profile already exists for this user."
      ) {
        alert("You already have a profile. You can edit it instead.");
      } else {
        console.error(
          "Error creating profile:",
          error.response?.data || error.message
        );
        alert("An error occurred while creating your profile.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingDots />;
  }

  return (
    <div className="background">
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
              Create Profile
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
                  "& .MuiOutlinedInput-root": {
                    borderRadius: "12px",
                  },
                  "& .MuiInputLabel-root": {
                    color: "#7f8c8d",
                  },
                }}
              />

              <TextField
                label="Country"
                name="country"
                fullWidth
                value={formData.country}
                onChange={handleInputChange}
                variant="outlined"
                margin="normal"
                required
              />
              <TextField
                label="State"
                name="state"
                fullWidth
                value={formData.state}
                onChange={handleInputChange}
                variant="outlined"
                margin="normal"
                required
              />

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

              <Button
                variant="contained"
                color="primary"
                type="submit"
                fullWidth
                sx={{
                  borderRadius: "8px",
                  marginTop: 3,
                  transition: "background-color 0.3s ease",
                  "&:hover": {
                    backgroundColor: "#3498db",
                  },
                }}
              >
                Create Profile
              </Button>
            </form>
          </CardContent>
        </Card>
      </Container>
    </div>
  );
};

export default Profile;
