
import MaterialEmployeeRegister from "./EmployeeRegister";
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
import React from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import MaterialLogin from "./materialLogin";
import MaterialHome from "./materialHome";
import { MaterialAbout } from "./materialHome";
import MaterialHrRegister from "./hrRegister";
import ProtectedRoutes from "./ProtectedRoutes";

import MaterialNavBars from "./materialNavBars";
import PasswordResetRequest from "./PasswordResetRequest";

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
