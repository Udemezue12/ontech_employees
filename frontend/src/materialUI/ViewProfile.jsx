import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import {
  Container,
  Typography,
  Card,
  CardContent,
  Avatar,
  Box,
  Button,
  Grid,
  Divider,
} from "@mui/material";
import { Link } from "react-router-dom";
import LoadingDots from "./Loading";
import defaultCover from "../assets/defaultCover.jpg"; // Optional: Add a local banner image
import defaultAvatar from "../assets/defaultAvatar.jpg"; // Fallback avatar image
import { cookies } from "./Cookie";

const ViewProfile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem("Token");
  const name = localStorage.getItem("UserName");
  const email = localStorage.getItem("UserEmail");
  const department = localStorage.getItem("UserDepartment");
  const role = localStorage.getItem("UserRole");

  useEffect(() => {
    fetchProfile();
  }, []);

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

  const fetchProfile = useCallback(async () => {
    setLoading(true);
    try {
      const csrfToken = await fetchCSRFToken();

      const response = await axios.get(
        "https://ontech-systems.onrender.com/api/view/profile/",
        {
          headers: {
            Authorization: `Token ${token}`,
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        }
      );

      setProfile(response.data);
    } catch (error) {
      console.error(
        "Error fetching profile:",
        error.response?.data || error.message
      );
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);
  if (loading) return <LoadingDots />;

  return (
    <div className="background">
      <Container maxWidth="md" sx={{ mt: 5 }}>
        <Card elevation={3} sx={{ borderRadius: 3, overflow: "hidden" }}>
          {/* Banner */}
          <Box
            sx={{
              height: 200,
              backgroundImage: `url(${defaultCover})`,
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
          />

          {/* Avatar (overlapping) */}
          <Box sx={{ position: "relative", top: -60, ml: 3 }}>
            <Avatar
              src={
                profile?.picture
                  ? `http://localhost:8000${profile.picture}`
                  : defaultAvatar
              }
              alt="Profile"
              sx={{
                width: 120,
                height: 120,
                border: "4px solid white",
              }}
            />
          </Box>

          {/* Name + Email + Role */}
          <CardContent sx={{ mt: -4 }}>
            <Box
              display="flex"
              justifyContent="space-between"
              alignItems="start"
            >
              <Box>
                <Typography variant="h5" fontWeight="bold">
                  {name || "No Name"}
                </Typography>
                <Typography variant="subtitle2" color="text.secondary">
                  {email || "No Email"}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Role: {role || "N/A"} | Department: {department || "N/A"}
                </Typography>
              </Box>
              <Button
                variant="outlined"
                size="small"
                component={Link}
                to={profile ? "/edit/profile" : "/create/profile"}
                sx={{ textTransform: "none", borderRadius: 5, mt: 1 }}
              >
                {profile ? "Edit Profile" : "Create Profile"}
              </Button>
            </Box>

            {/* Personal Details */}
            <Typography variant="body1" sx={{ mt: 2 }}>
              {profile?.personal_details || "No personal details provided"}
            </Typography>

            <Divider sx={{ my: 2 }} />

            {/* Location Info */}
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography
                  variant="h5"
                  fontWeight="bold"
                  color="text.secondary"
                >
                  Country
                </Typography>
                <Typography variant="body1">
                  {profile?.country || "N/A"}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography
                  variant="h6"
                  fontWeight="bold"
                  color="text.secondary"
                >
                  State
                </Typography>
                <Typography variant="body1">
                  {profile?.state || "N/A"}
                </Typography>
              </Grid>
            </Grid>

            {/* Resume */}
            <Box mt={2}>
              <Typography variant="h6" color="text.secondary">
                Resume
              </Typography>
              {profile?.resume ? (
                <a
                  href={`http://localhost:8000${profile.resume}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ textDecoration: "none", color: "#1DA1F2" }}
                >
                  View Resume
                </a>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No resume uploaded
                </Typography>
              )}
            </Box>
          </CardContent>
        </Card>
      </Container>
    </div>
  );
};

export default ViewProfile;
