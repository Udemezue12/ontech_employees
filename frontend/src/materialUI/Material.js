// // import React from "react";
// // import { Routes, Route, useLocation } from "react-router-dom";
// // import MaterialLogin from "./materialLogin";
// // import MaterialHome from "./materialHome";
// // import { MaterialAbout } from "./materialHome";
// // import MaterialHrRegister from "./hrRegister";
import MaterialEmployeeRegister from "./EmployeeRegister";
// // import ProtectedRoutes from "./ProtectedRoutes";
// // // import { WindowLocation } from "./AxiosInstance";
// // import MaterialNavBars from "./materialNavBars";
// // import PasswordResetRequest from "./PasswordResetRequest";
// // import PasswordResetToken from "./PasswordResetToken";
// // import { PasswordReset } from "./PasswordResetToken";
import OverallAdminRegister from "./OverallAdminRegister";
import ManagerRegister from "./ManagerRegister";
import RegistrationCards from "./Register";
import Profile from "./Profile";
import ViewProfile from "./ViewProfile";
import EditProfile from "./EditProfile";
import "./AxiosInstance";
import RegisterFingerprint from "./RegisterFingerprint";
import FingerprintLogin from "./FingerPrintLogin";
import CompanyProfileForm from "./CompanyProfileForm";
import ManualAttendance from "./ManualAttendance";
import BiometricAttendance from "./BiometricAttendance";

// // function Material() {
// //   const location = useLocation();
// //   const noNavBar =
// //     location.pathname === "/login" ||
// //     location.pathname === "/register" ||
// //     location.pathname === "/hr_register" ||
// //     location.pathname === "/employee_register" ||
// //     location.pathname === "/manager_register" ||
// //     location.pathname === "/admin_register" ||
// //     location.pathname === "/login/fingerprint" ||
// //     location.pathname.includes("password");
// //   React.useEffect(() => {
// //     // Prevent back navigation after logout
// //     window.history.pushState(null, null, window.location.href);
// //     window.onpopstate = () => {
// //       window.history.go(1);
// //     };
// //   }, []);
// //   return (
// //     <>
// //       {noNavBar ? (
// //         <Routes>
// //           <Route path="/login" element={<MaterialLogin />} />
// //           <Route path="/register" element={<RegistrationCards />} />
// //           {/* <Route path="/register" element={<MaterialRegister />} /> */}
// //           {/* <Route path="/register_hr" element={<MaterialRegister />} /> */}
// //           <Route path="/hr_register" element={<MaterialHrRegister />} />
// //           <Route path="/manager_register" element={<ManagerRegister />} />
// //           <Route
// //             path="/employee_register"
// //             element={<MaterialEmployeeRegister />}
// //           />
// //           <Route path="/admin_register" element={<OverallAdminRegister />} />

// //           <Route path="/login/fingerprint" element={<FingerprintLogin />} />

// //           <Route
// //             path="/request/password_reset"
// //             element={<PasswordResetRequest />}
// //           />
// //           <Route
// //             path="/password-reset/:token"
// //             element={<PasswordResetToken />}
// //           />
// //           <Route path="/password-reset" element={<PasswordReset />} />
// //         </Routes>
// //       ) : (
// //         <MaterialNavBars
// //           content={
// //             <Routes>
// //               <Route element={<ProtectedRoutes />}>
// //                 <Route path="/" element={<MaterialHome />} />
// //                 {/* <Route path="/home" element={<WindowLocation />} /> */}
// //                 <Route path="/about" element={<MaterialAbout />} />
// //                 <Route path="/create/profile" element={<Profile />} />
// //                 <Route path="/view/profile" element={<ViewProfile />} />
// //                 <Route path="/edit/profile" element={<EditProfile />} />
// //                 <Route
// //                   path="/create/company/profile"
// //                   element={<CompanyProfileForm />}
// //                 />
// //                 <Route
// //                   path="/manual/attendance"
// //                   element={<ManualAttendance />}
// //                 />
// //                 {/* <Route path='attendance/manual' element={<ManualAttendanceForm/>}/>               */}
// //                 <Route
// //                   path="/biometric/attendance"
// //                   element={<BiometricAttendance />}
// //                 />
// //                 <Route
// //                   path="/create/fingerprint"
// //                   element={<RegisterFingerprint />}
// //                 />
// //               </Route>
// //             </Routes>
// //           }
// //         />
// //       )}
// //     </>
// //   );
// // }

// // export default Material;
// // // complete logout flow that works seamlessly across your Django templates and React app

// // /////////////////////////////////////////
// // ////////////////////////////////
// import React from "react";
// import { Routes, Route, useLocation, useNavigate } from "react-router-dom";
// import MaterialLogin from "./materialLogin";
// import MaterialHome, { MaterialAbout } from "./materialHome";
// import MaterialHrRegister from "./hrRegister";
// import MaterialEmployeeRegister from "./EmployeeRegister";
// import ProtectedRoutes from "./ProtectedRoutes";
// import MaterialNavBars from "./materialNavBars";
// import PasswordResetRequest from "./PasswordResetRequest";
// import PasswordResetToken, { PasswordReset } from "./PasswordResetToken";
// import OverallAdminRegister from "./OverallAdminRegister";
// import ManagerRegister from "./ManagerRegister";
// import RegistrationCards from "./Register";
// import Profile from "./Profile";
// import ViewProfile from "./ViewProfile";
// import EditProfile from "./EditProfile";
// import RegisterFingerprint from "./RegisterFingerprint";
// import FingerprintLogin from "./FingerPrintLogin";
// import CompanyProfileForm from "./CompanyProfileForm";
// import ManualAttendance from "./ManualAttendance";
// import BiometricAttendance from "./BiometricAttendance";
// import "./AxiosInstance";
// import useAutoLogout from "./AutoLogout";
// import { logoutUser } from "./materialLogout";
// import LogoutPage from "./LogoutPage";
// import DashboardLink from "./Dashboard";
// // import { Route } from 'react-router-dom';
// function Material() {
//   useAutoLogout(logoutUser);
//   const location = useLocation();
//   const navigate = useNavigate();

//   const publicRoutes = [
//     "/",
//     "/login",
//     "/register",
//     "/hr_register",
//     "/employee_register",
//     "/manager_register",
//     "/admin_register",
//     "/login/fingerprint",
//     "/password-reset/:token",
//     "/password-reset",
//     "/request/password_reset",
//   ];

//   const noNavBar =
//     publicRoutes.includes(location.pathname) ||
//     location.pathname.includes("password");

//   // 🚫 Prevent back navigation after logout
//   React.useEffect(() => {
//     window.history.pushState(null, null, window.location.href);
//     window.onpopstate = () => {
//       window.history.go(1);
//     };
//   }, []);

//   // 🔐 Redirect if not authenticated and trying to access protected route
//   React.useEffect(() => {
//     const token = localStorage.getItem("Token");
//     const isPublic = publicRoutes.some((route) =>
//       location.pathname.startsWith(route)
//     );

//     if (!token && !isPublic) {
//       navigate("/login", { replace: true });
//     }
//   }, [location, navigate]);

//   return (
//     <>
//       {noNavBar || location.pathname === "/" ? (
//   <Routes>
//   </Routes>
// ) : (
//   <MaterialNavBars
//     content={
//       <Routes>
//         <Route element={<ProtectedRoutes />}>
//         </Route>
//       </Routes>
//     }
//   />
// )}

//     </>
//   );
// }

// export default Material;
import React from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import MaterialLogin from "./materialLogin";
import MaterialHome from "./materialHome";
import { MaterialAbout } from "./materialHome";
import MaterialRegister from "./materialRegister";
import MaterialHrRegister from "./hrRegister";
import ProtectedRoutes from "./ProtectedRoutes";
import { WindowLocation } from "./AxiosInstance";
import LogoutIcon from "@mui/icons-material/Logout";
import MaterialNavBars from "./materialNavBars";
import PasswordResetRequest from "./PasswordResetRequest";
// import PasswordResetToken from "./PasswordResetToken";
import { PasswordReset } from "./PasswordResetToken";
import DashboardLink from './Dashboard';
import LogoutPage from './LogoutPage';

function Material() {
  const location = useLocation();
  const noNavBar =
    location.pathname === "/login" ||
    location.pathname === "/register" ||
    location.pathname === "/hr_register" ||
    location.pathname === "/employee_register" ||
    location.pathname === "/manager_register" ||
    location.pathname === "/admin_register" ||
    location.pathname === "/login/fingerprint" ||
    location.pathname === "/request/password_reset" ||
    // location.pathname === "/password-reset/:token" ||
    location.pathname === "/" 
    // location.pathname.includes("password");
  return (
    <>
      {noNavBar ? (
        <Routes>
          <Route path="/" element={<MaterialHome />} />
          <Route path="/login" element={<MaterialLogin />} />
          <Route path="/register" element={<RegistrationCards />} />
          <Route path="/hr_register" element={<MaterialHrRegister />} />
          <Route path="/manager_register" element={<ManagerRegister />} />
          <Route
            path="/employee_register"
            element={<MaterialEmployeeRegister />}
          />
          <Route path="/admin_register" element={<OverallAdminRegister />} />
          <Route path="/login/fingerprint" element={<FingerprintLogin />} />

          <Route
            path="/request/password_reset"
            element={<PasswordResetRequest />}
          />
          {/* <Route
            path="/password-reset/:token"
            element={<PasswordResetToken />}
          /> */}
          <Route path="/password-reset" element={<PasswordReset />} />
        </Routes>
      ) : (
        <MaterialNavBars
          content={
            <Routes>
              <Route element={<ProtectedRoutes />}>
                <Route path="/dashboard" element={<DashboardLink />} />
                <Route path="/about" element={<MaterialAbout />} />
                <Route path="/create/profile" element={<Profile />} />
                <Route path="/view/profile" element={<ViewProfile />} />
                <Route path="/edit/profile" element={<EditProfile />} />
                <Route
                  path="/create/company/profile"
                  element={<CompanyProfileForm />}
                />
                <Route
                  path="/manual/attendance"
                  element={<ManualAttendance />}
                />
                <Route
                  path="/biometric/attendance"
                  element={<BiometricAttendance />}
                />
                <Route
                  path="/create/fingerprint"
                  element={<RegisterFingerprint />}
                />
                <Route path="/logout" element={<LogoutPage />} />
              </Route>
            </Routes>
          }
        />
      )}
    </>
  );
}

export default Material;
