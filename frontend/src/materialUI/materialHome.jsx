import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "./boots.css"; // or your CSS file

function HomePage() {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    document.body.classList.toggle("dark-mode", darkMode);
  }, [darkMode]);

  return (
    <div className="container-fluid finger min-vh-100 d-flex flex-column justify-content-between px-3 py-5">
      {/* Dark Mode Toggle */}
      <div className="form-check form-switch position-absolute top-0 end-0 m-3">
        <input
          className="form-check-input"
          type="checkbox"
          id="darkModeToggle"
          onChange={() => setDarkMode(!darkMode)}
          checked={darkMode}
        />
        <label className="form-check-label" htmlFor="darkModeToggle">
          Dark Mode
        </label>
      </div>

      {/* Onboarding Illustration */}
      <div className="text-center animate__animated animate__fadeInDown mb-4">
      

      </div>

      {/* Welcome Text */}
      <div className="text-center animate__animated animate__fadeInUp mb-5">
        <h1 className="fw-bold display-5 mb-3">
          Welcome to OnTech Task & Employee Management System
        </h1>
        <p className="lead mx-auto" style={{ maxWidth: "900px" }}>
          Manage your workforce, monitor attendance with biometrics, assign
          tasks, and handle departments efficiently using OnTech’s unified
          platform. Perfect for HR, Managers, and Employees alike.
        </p>
      </div>

      {/* Cards */}
      <div className="row g-4 justify-content-center animate__animated animate__fadeInUp">
        {/* Login */}
        <div className="col-12 col-md-5 col-lg-4">
          <div className="card shadow-lg p-4 border-0 rounded-4 h-100">
            <h5 className="fw-bold mb-2">Already Registered?</h5>
            <p className="text-muted mb-4">
              Log in securely with your credentials or biometric passkey.
            </p>
            <Link to="/login" className="btn btn-outline-primary w-100">
              Login
            </Link>
          </div>
        </div>

        {/* Register */}
        <div className="col-12 col-md-5 col-lg-4">
          <div className="card shadow-lg p-4 border-0 rounded-4 h-100">
            <h5 className="fw-bold mb-2">New Here?</h5>
            <p className="text-muted mb-4">
              Register now to join your team and start managing tasks.
            </p>
            <Link to="/register" className="btn btn-outline-primary w-100">
              Register
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center mt-5 pt-4 pb-2 small text-muted">
        &copy; {new Date().getFullYear()} OnTech Corporation. All rights
        reserved.
      </footer>
    </div>
  );
}

export default HomePage;




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
