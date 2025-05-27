//
import React, { useState } from "react";
import "./material.css";
import Box from "@mui/material/Box";
import TextFields from "./forms/TextField";
import PasswordFields from "./forms/PasswordField";
import axios from "axios";
import ButtonFields from "./forms/ButtonField";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { cookies } from "./Cookie";

// // export default function MaterialLogin() {
// //   const navigate = useNavigate();
// //   const { control, handleSubmit } = useForm();

// //   // Clear localStorage and cookies when page loads

// //   async function fetchCSRFToken() {
// //     try {
// //       await axios.get("https://ontech-systems.onrender.com/api/csrf/", {
// //         withCredentials: true,
// //       });
// //       return cookies.get("csrftoken");
// //     } catch (err) {
// //       console.error("Failed to get CSRF token", err);
// //       return null;
// //     }
// //   }

// //   const submit = async (data) => {
// //     try {
// //       // ✅ 1. First, fetch the CSRF token
// //       await axios.get("https://ontech-systems.onrender.com/api/csrf/", {
// //         withCredentials: true,
// //       });

// //       const csrfToken = cookies.get("csrftoken");

// //       if (!csrfToken) {
// //         throw new Error("CSRF token not found in cookies");
// //       }

// //       // ✅ 2. THEN, clear existing tokens and cookies (safely before storing new ones)
// //       localStorage.removeItem("Token");
// //       localStorage.removeItem("UserId");
// //       localStorage.removeItem("UserEmail");
// //       localStorage.removeItem("UserRole");
// //       localStorage.removeItem("UserDepartment");
// //       cookies.remove("sessionid");

// //       console.log("Cleared existing session data.");

// //       // ✅ 3. Knox Login
// //       const response = await axios.post(
// //         "https://ontech-systems.onrender.com/api/login/",
// //         {
// //           email: data.email,
// //           password: data.password,
// //         },
// //         {
// //           headers: {
// //             "X-CSRFToken": csrfToken,
// //             "Content-Type": "multipart/form-data",
// //           },
// //           withCredentials: true,
// //         }
// //       );

// //       const { token, user } = response.data;

// //       if (!user || !user.id) {
// //         throw new Error("User data missing in response");
// //       }

// //       // ✅ 4. Save token and user info
// //       localStorage.setItem("Token", token);
// //       localStorage.setItem("UserId", user.id);
// //       localStorage.setItem("UserEmail", user.email);
// //       localStorage.setItem("UserRole", user.role);
// //       localStorage.setItem("UserDepartment", user.department);

// //       console.log("Login successful:", response.data);

// //       // ✅ 5. Django session login
// //       await axios.post(
// //         "https://ontech-systems.onrender.com/api/session-login/",
// //         {
// //           email: data.email,
// //           password: data.password,
// //         },
// //         {
// //           headers: {
// //             "X-CSRFToken": csrfToken,
// //             "Content-Type": "multipart/form-data",
// //           },
// //           withCredentials: true,
// //         }
// //       );

// //       navigate("/dashboard", { replace: true });
// //     } catch (error) {
// //       console.error("Login failed:", error.response?.data || error.message);
// //     }
// //   };

// //   return (
// //     <div className="background">
// //       <form onSubmit={handleSubmit(submit)}>
// //         <Box className="whiteBox">
// //           <Box className="itemBox">
// //             <Box className="title">LOGIN</Box>
// //           </Box>

// //           <Box className="itemBox">
// //             <TextFields label="Email" name="email" control={control} />
// //           </Box>

// //           <Box className="itemBox">
// //             <PasswordFields
// //               label="Password"
// //               name="password"
// //               control={control}
// //             />
// //           </Box>

// //           <Box className="itemBox">
// //             <ButtonFields label="Login" type="submit" />
// //           </Box>

// //           <Box className="itemBox">
// //             <p>Or log in using your Passkey:</p>
// //             <Link to="/login/fingerprint">
// //               <ButtonFields label="Login with Passkey" type="button" />
// //             </Link>
// //           </Box>

// //           <Box className="itemBox">
// //             <Link to="/register" className="link">
// //               Don't have an account?
// //             </Link>
// //           </Box>

// //           <Box className="itemBox">
// //             <Link to="/request/password_reset" className="link">
// //               Forgot Password? Reset it Here
// //             </Link>
// //           </Box>
// //         </Box>
// //         <Box sx={{ textAlign: "center", py: 2, fontSize: "0.9rem" }}>
// //           &copy; {new Date().getFullYear()} OnTech Corporation. All rights
// //           reserved.
// //         </Box>
// //       </form>
// //     </div>
// //   );
// // }

// /////
// import React from "react";
// import "./material.css";
// import Box from "@mui/material/Box";
// import TextFields from "./forms/TextField";
// import PasswordFields from "./forms/PasswordField";
// import axios from "axios";
// import ButtonFields from "./forms/ButtonField";
// import { Link, useNavigate } from "react-router-dom";
// import { useForm } from "react-hook-form";
// import { cookies } from "./Cookie";
// import { useRoleAuth } from "./RoleAuthContext";

// export default function MaterialLogin() {
//   const navigate = useNavigate();
//   const { control, handleSubmit } = useForm();
//   const [isReloaded, setIsReloaded] = React.useState(false);
//   const { login } = useRoleAuth();

//   async function fetchCSRFToken() {
//     try {
//       await axios.get("https://ontech-systems.onrender.com/api/csrf/", {
//         withCredentials: true, // ensure cookies are sent
//       });
//       return cookies.get("csrftoken"); // Fetch it after Django sets it
//     } catch (err) {
//       console.error("Failed to get CSRF token", err);
//       return null;
//     }
//   }

//   const submit = async (data) => {
//     const csrfToken = await fetchCSRFToken();

//     try {
//       // ✅ 1. First, fetch the CSRF token
//       // await axios.get("https://ontech-systems.onrender.com/api/csrf/", {
//       //   withCredentials: true,
//       // });

//       // const csrfToken = cookies.get("csrftoken");

//       // if (!csrfToken) {
//       //   throw new Error("CSRF token not found in cookies");
//       // }

//       // ✅ 2. THEN, clear existing tokens and cookies (safely before storing new ones)
//       // localStorage.removeItem("Token");
//       // localStorage.removeItem("UserId");
//       // localStorage.removeItem("UserEmail");
//       // localStorage.removeItem("UserRole");
//       // localStorage.removeItem("UserDepartment");
//       // cookies.remove("sessionid");
//       // cookies.remove("X-CSRFToken")

//       // console.log("Cleared existing session data.");

//       // 1. Knox Login
//       const response = await axios.post(
//         "https://ontech-systems.onrender.com/api/login/",
//         {
//           email: data.email,
//           password: data.password,
//         },
//         {
//           headers: {
//             "X-CSRFToken": csrfToken,
//             "Content-Type": "multipart/form-data",
//           },
//           withCredentials: true, // include cookies for CSRF
//         }
//       );

//       const { token, user } = response.data;

//       if (!user || !user.id) {
//         throw new Error("User data missing in response");
//       }

//       // 2. Save Knox token and user info
//       localStorage.setItem("Token", token);
//       localStorage.setItem("UserId", user.id);
//       localStorage.setItem("UserEmail", user.email);
//       localStorage.setItem("UserRole", user.role);
//       localStorage.setItem("UserDepartment", user.department);
//       localStorage.setItem("UserName", user.name);

//       login(user);
//       console.log("Login successful:", response.data);

//       // ✅ 3. Session Login for @login_required views
//       await axios.post(
//         "https://ontech-systems.onrender.com/api/session-login/",
//         {
//           email: data.email,
//           password: data.password,
//         },
//         {
//           withCredentials: true,
//         }
//       );

//       navigate("/view/profile", { replace: true });
//     } catch (error) {
//       console.error("Login failed:", error.response?.data || error.message);
//     }
//   };
//   return (
//     <div className="backgrounder">
//       <form onSubmit={handleSubmit(submit)}>
//         <Box className="whiteBox">
//           <Box className="itemBox">
//             <Box className="title">LOGIN</Box>
//           </Box>

//           <Box className="itemBox">
//             <TextFields label="Email" name="email" control={control} />
//           </Box>

//           <Box className="itemBox">
//             <PasswordFields
//               label="Password"
//               name="password"
//               control={control}
//             />
//           </Box>

//           <Box className="itemBox">
//             <ButtonFields label="Login" type="submit" />
//           </Box>

//           <Box className="itemBox">
//             <p>Or log in using your Passkey:</p>
//             <Link to="/login/fingerprint">
//               <ButtonFields label="Login with Passkey" type="button" />
//             </Link>
//           </Box>

//           <Box className="itemBox">
//             <Link to="/register" className="link">
//               Don't have an account?
//             </Link>
//           </Box>

//           <Box className="itemBox">
//             <Link to="/request/password_reset" className="link">
//               Forgot Password? Reset it Here
//             </Link>
//           </Box>
//         </Box>
//         <Box sx={{ textAlign: "center", py: 2, fontSize: "0.9rem" }}>
//           &copy; {new Date().getFullYear()} OnTech Corporation. All rights
//           reserved.
//         </Box>
//       </form>
//     </div>
//   );
// }
// //////////
// /////////////////
// ////////////////
export default function MaterialLogin() {
  const navigate = useNavigate();
  const { control, handleSubmit } = useForm();
  // const [setCsrfToken] = useState("")
  async function fetchCSRFToken() {
    try {
      // await axios.get("https://ontech-systems.onrender.com/api/csrf/", {
      await axios.get("https://ontech-systems.onrender.com/api/csrf/", {
        withCredentials: true, // ensure cookies are sent
      });
      return cookies.get("csrftoken"); // Fetch it after Django sets it
    } catch (err) {
      console.error("Failed to get CSRF token", err);
      return null;
    }
  }

  const submit = async (data) => {
    const csrfToken = await fetchCSRFToken();
    // setCsrfToken(csrfToken)

    try {
      // 1. Knox Login
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
          withCredentials: true, // include cookies for CSRF
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

      // ✅ 3. Session Login for @login_required views
      await axios.post(
        "https://ontech-systems.onrender.com/api/session-login/",
        // "https://ontech-systems.onrender.com/api/session-login/",
        {
          email: data.email,
          password: data.password,
        },
        {
          headers: {
            "X-CSRFToken": csrfToken,
          },

          withCredentials: true, // send/receive cookies (sessionid)
        }
      );

      // 4. Navigate to homepage
      navigate("/dashboard", { replace: true });
    } catch (error) {
      console.error("Login failed:", error.response?.data || error.message);
    }
  };

  return (
    <div className="backgrounder">
      <form onSubmit={handleSubmit(submit)}>
        <Box className="whiteBox">
          <Box className="itemBox">
            <Box className="title">Login for Auth App</Box>
          </Box>

          <Box className="itemBox">
            <TextFields label="Email" name="email" control={control} />
          </Box>

          <Box className="itemBox">
            <PasswordFields
              label="Password"
              name="password"
              control={control}
            />
          </Box>

          <Box className="itemBox">
            <ButtonFields label="Login" type="submit" />
          </Box>

          <Box className="itemBox">
            <p>Or log in using your fingerprint:</p>
            <Link to="/login/fingerprint">
              <ButtonFields label="Login with Fingerprint" type="button" />
            </Link>
          </Box>

          <Box className="itemBox">
            <Link to="/register" className="link">
              Don't have an account?
            </Link>
          </Box>

          <Box className="itemBox">
            <Link to="/request/password_reset" className="link">
              Forgot Password? Reset it Here
            </Link>
          </Box>
        </Box>
      </form>
    </div>
  );
}
