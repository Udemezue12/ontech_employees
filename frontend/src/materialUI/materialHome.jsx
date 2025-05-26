import React from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  IconButton,
} from "@mui/material";
import { Link } from "react-router-dom";
import LoginIcon from "@mui/icons-material/Login";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import LightModeIcon from "@mui/icons-material/LightMode";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import "./material.css";

function MaterialHome() {
  const [darkMode, setDarkMode] = React.useState(false);

  const toggleTheme = () => {
    setDarkMode(!darkMode);
    // Placeholder for context-based theme logic
  };

  return (
    <div className="background">
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          px: 2,
          py: 4,
        }}
      >
        {/* Theme Toggle - Top Right */}
        <Box
          sx={{
            position: "absolute",
            top: 20,
            right: 20,
          }}
        >
          <IconButton onClick={toggleTheme}>
            {darkMode ? <DarkModeIcon /> : <LightModeIcon />}
          </IconButton>
        </Box>

        {/* Main Content */}
        <Box
          sx={{
            flexGrow: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            mt: 4,
            mb: 6,
          }}
        >
          <Typography
            variant="h4"
            gutterBottom
            sx={{ fontWeight: "bold", textAlign: "center" }}
          >
            Welcome to OnTech Employee Task and Management System
          </Typography>

          <Typography
            variant="body1"
            sx={{
              maxWidth: 700,
              textAlign: "center",
              mb: 6,
              fontSize: "1.1rem",
              lineHeight: 1.8,
            }}
          >
            OnTech’s system is a secure and modern platform built for managing
            employees, tracking daily attendance using biometric passkeys,
            assigning tasks, overseeing project timelines, and maintaining
            departmental records. Whether you're HR, a Manager, or an Employee —
            this system provides streamlined tools to ensure efficiency,
            accountability, and transparency across your organization.
          </Typography>

          <Grid container spacing={4} justifyContent="center">
            <Grid item xs={12} sm={6} md={4}>
              <Card
                sx={{
                  transition: "transform 0.3s, box-shadow 0.3s",
                  boxShadow: 2,
                  "&:hover": {
                    transform: "translateY(-5px)",
                    boxShadow: 6,
                  },
                }}
              >
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
                    Existing User
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 3 }}>
                    Login securely using credentials or passkey to access
                    your workspace.
                  </Typography>
                  <Button
                    component={Link}
                    to="/login"
                    fullWidth
                    variant="outlined"
                    startIcon={<LoginIcon />}
                  >
                    Login
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Card
                sx={{
                  transition: "transform 0.3s, box-shadow 0.3s",
                  boxShadow: 2,
                  "&:hover": {
                    transform: "translateY(-5px)",
                    boxShadow: 6,
                  },
                }}
              >
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
                    New Here?
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 3 }}>
                    Join OnTech and start managing your tasks, employees, and
                    department records today.
                  </Typography>
                  <Button
                    component={Link}
                    to="/register"
                    fullWidth
                    variant="outlined"
                    startIcon={<PersonAddIcon />}
                  >
                    Register
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>

        {/* Footer */}
        <Box sx={{ textAlign: "center", py: 2, fontSize: "0.9rem" }}>
          &copy; {new Date().getFullYear()} OnTech Corporation. All rights
          reserved.
        </Box>
      </Box>
    </div>
  );
}

export default MaterialHome;

export function MaterialAbout() {
  return (
    <div>
      <h1 className="mt-5 p-5 bg-light">Welcome to Payroll Ssytem</h1>
      <p className="lead">
        This is a simple payroll system that allows you to manage employee
        payrolls, including salary calculations, deductions, and tax management.
        The system is designed to be user-friendly and efficient, making it easy
        for HR departments to handle payroll tasks.
      </p>
      {/* <p className='my-4'>
        The system includes features such as employee management, salary calculations, tax calculations, and reporting. It is built using modern web technologies and follows best practices for security and performance.
      </p> */}
      <hr className="my-4" />
      <p>Click the button below to register or login</p>
      <Link className="btn btn-primary btn-lg" to="/register" role="button">
        Register
      </Link>
      <Link className="btn btn-secondary btn-lg mx-2" to="/login" role="button">
        Login
      </Link>
    </div>
  );
}
