import React from "react"; // Make sure this imports React
import PropTypes from "prop-types";
import {
  AppBar,
  Box,
  CssBaseline,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
} from "@mui/material";
import EnhancedEncryptionIcon from "@mui/icons-material/EnhancedEncryption";

import DashboardIcon from "@mui/icons-material/Dashboard";
import PersonIcon from "@mui/icons-material/Person";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import FingerprintIcon from "@mui/icons-material/Fingerprint";
import MenuIcon from "@mui/icons-material/Menu";
import InboxIcon from "@mui/icons-material/MoveToInbox";
import LogoutIcon from "@mui/icons-material/Logout";
import InfoSharpIcon from "@mui/icons-material/InfoSharp";
import LoginIcon from "@mui/icons-material/Login";
import AppRegistrationIcon from "@mui/icons-material/AppRegistration";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AxiosInstance } from "./AxiosInstance";
import useAutoLogout from "./AutoLogout"; // Ensure it's being imported correctly
import axios from "axios";
import Swal from "./../../node_modules/sweetalert2/src/sweetalert2";
import { cookies } from "./Cookie";
import { logoutUser } from "./materialLogout";
import { confirmAndLogout } from "./confirmAndLogout";

const drawerWidth = 240;

export function MaterialNavBars(props) {
  const { window, content } = props;
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState("");
  const location = useLocation();
  const path = location.pathname;
  const navigate = useNavigate();
  const userRole = localStorage.getItem("UserRole");

  // Check if the user is logged in by checking localStorage for the Token
  const isLoggedIn = localStorage.getItem("Token");

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  useAutoLogout(logoutUser);

  const drawerItems = isLoggedIn
    ? [
        

        {
          text: "Dashboard",
          icon: <DashboardIcon />,
          link: "/dashboard",
        },
        {
          text: "Create Profile",
          icon: <InfoSharpIcon />,
          link: "/create/profile",
        },
        ...(userRole === "Overall_Admin"
          ? [
              {
                text: "Create Company Profile",
                icon: <InfoSharpIcon />,
                link: "/create/company/profile",
              },
            ]
          : []),
        {
          text: "Profile",
          icon: <PersonIcon />,
          link: "/view/profile",
        },
        {
          text: "Manual Attendance",
          icon: <AccessTimeIcon />,
          link: "/manual/attendance",
        },
        {
          text: "Biometric Attendance",
          icon: <FingerprintIcon />,
          link: "/biometric/attendance",
        },
        {
          text: "Create Passkey",
          icon: <EnhancedEncryptionIcon />,
          link: "/create/fingerprint",
        },
        
        {
          text: "Logout",
          icon: <LogoutIcon />,
          action: () => {
            confirmAndLogout(navigate);
          },
        },
      ]
    : [
        {
          text: "Login",
          icon: <LoginIcon />,
          link: "/login",
        },
        {
          text: "Register",
          icon: <AppRegistrationIcon />,
          link: "/register",
        },
      ];
  const drawer = (
    <div>
      <Toolbar />
      <Divider />
      <List>
        {drawerItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component={item.link ? Link : "button"}
              to={item.link || undefined}
              onClick={() => {
                setMobileOpen(false);
                if (item.action) item.action();
              }}
              selected={path === item.link}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  );

  const container =
    window !== undefined ? () => window().document.body : undefined;

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography
            variant="h4"
            noWrap
            component="div"
            sx={{ fontWeight: "bold" }}
          >
            ONTECH
          </Typography>
        </Toolbar>
      </AppBar>

      <Box component="nav">
        <Drawer
          container={container}
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: "block", sm: "block" },
            "& .MuiDrawer-paper": { width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        {errorMessage && <Box sx={{ color: "red", mb: 2 }}>{errorMessage}</Box>}
        {content}
      </Box>
    </Box>
  );
}

MaterialNavBars.propTypes = {
  window: PropTypes.func,
  content: PropTypes.node,
};

export default MaterialNavBars;
