// {
//   headers: {
//     Authorization: `Token ${token}`,
//     "X-CSRFToken": csrfToken,
//   },
//   withCredentials: true,
// }
// "https://ontech-systems.onrender.com/api/manual-attendance/",

// const getCSRFToken = async () => {
//   try {
//     await axios.get("https://ontech-systems.onrender.com/api/csrf/", {
//       withCredentials: true,
//     });
//     return cookies.get("csrftoken");
//   } catch (err) {
//     console.error("CSRF fetch error:", err);
//     return null;
//   }
// };

import React, { useState, useEffect } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import { cookies } from "./Cookie";
import { useCallback } from "react";
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

const csrfToken = await fetchCSRFToken();
// Function to get CSRF token from cookies

const ManualAttendanceForm = () => {
  const [attendance, setAttendance] = useState({
    should_show_check_in: true,
    should_show_check_out: false,
    can_check_out: false,
    check_in: null,
    check_out: null,
    worked_hours: 0,
    overtime_hours: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // API base URL
  const API_URL = "https://ontech-systems.onrender.com/attendance/";

  // Get Knox token from localStorage
  const token = localStorage.getItem("Token"); // Verify this key

  // Axios instance with Knox authentication
  const axiosInstance = axios.create({
    baseURL: API_URL,
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    withCredentials: true,
  });

  // Fetch attendance data
  // const fetchAttendance = async () => {
  //   setLoading(true);
  //   setError(null);
  //   try {
  //     const response = await axiosInstance.get("");
  //     console.log("API Response:", response.data);
  //     setAttendance({
  //       should_show_check_in: response.data.should_show_check_in || false,
  //       should_show_check_out: response.data.should_show_check_out || false,
  //       can_check_out: response.data.can_check_out || false,
  //       check_in: response.data.check_in || null,
  //       check_out: response.data.check_out || null,
  //       worked_hours: response.data.worked_hours || 0,
  //       overtime_hours: response.data.overtime_hours || 0,
  //     });
  //   } catch (err) {
  //     console.error("Fetch Error:", {
  //       status: err.response?.status,
  //       data: err.response?.data,
  //       message: err.message,
  //     });
  //     setError(err.response?.data?.error || "Failed to fetch attendance data");
  //     setAttendance({
  //       should_show_check_in: true,
  //       should_show_check_out: false,
  //       can_check_out: false,
  //       check_in: null,
  //       check_out: null,
  //       worked_hours: 0,
  //       overtime_hours: 0,
  //     });
  //   } finally {
  //     setLoading(false);
  //   }
  // };
  const fetchAttendance = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axiosInstance.get("");
      setAttendance({
        should_show_check_in: response.data.should_show_check_in || false,
        should_show_check_out: response.data.should_show_check_out || false,
        can_check_out: response.data.can_check_out || false,
        check_in: response.data.check_in || null,
        check_out: response.data.check_out || null,
        worked_hours: response.data.worked_hours || 0,
        overtime_hours: response.data.overtime_hours || 0,
      });
    } catch (err) {
      console.error("Fetch Error:", err);
      setError(err.response?.data?.error || "Failed to fetch attendance data");
    } finally {
      setLoading(false);
    }
  }, [axiosInstance]);

  useEffect(() => {
    fetchAttendance();
    const interval = setInterval(() => {
      if (attendance.check_in && !attendance.check_out) {
        fetchAttendance();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [attendance.check_in, attendance.check_out, fetchAttendance]);

  const handleAction = async (action) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const response = await axiosInstance.post("", { action });
      setAttendance({
        should_show_check_in: response.data.should_show_check_in || false,
        should_show_check_out: response.data.should_show_check_out || false,
        can_check_out: response.data.can_check_out || false,
        check_in: response.data.check_in || null,
        check_out: response.data.check_out || null,
        worked_hours: response.data.worked_hours || 0,
        overtime_hours: response.data.overtime_hours || 0,
      });
      setSuccess(
        action === "check_in"
          ? "Checked in successfully!"
          : "Checked out successfully!"
      );
    } catch (err) {
      console.error("Action Error:", err);
      setError(err.response?.data?.error || "Action failed");
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="background">
      <div className="container mt-5">
        <h2 className="mb-4 text-center">Attendance Management</h2>
        {error && (
          <div
            className="alert alert-danger alert-dismissible fade show"
            role="alert"
          >
            {error}
            <button
              type="button"
              className="btn-close"
              onClick={() => setError(null)}
              aria-label="Close"
            ></button>
          </div>
        )}
        {success && (
          <div
            className="alert alert-success alert-dismissible fade show"
            role="alert"
          >
            {success}
            <button
              type="button"
              className="btn-close"
              onClick={() => setSuccess(null)}
              aria-label="Close"
            ></button>
          </div>
        )}
        {loading && (
          <div className="text-center">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        )}
        <div className="card shadow-sm">
          <div className="card-body">
            <h5 className="card-title">Today's Attendance</h5>
            <div className="row">
              <div className="col-md-6">
                <p>
                  <strong>Check-In:</strong>{" "}
                  {attendance.check_in
                    ? new Date(attendance.check_in).toLocaleString()
                    : "Not checked in"}
                </p>
                <p>
                  <strong>Check-Out:</strong>{" "}
                  {attendance.check_out
                    ? new Date(attendance.check_out).toLocaleString()
                    : "Not checked out"}
                </p>
              </div>
              <div className="col-md-6">
                <p>
                  <strong>Worked Hours:</strong> {attendance.worked_hours} hrs
                </p>
                <p>
                  <strong>Overtime Hours:</strong> {attendance.overtime_hours}{" "}
                  hrs
                </p>
              </div>
            </div>
            <div className="mt-4 d-flex justify-content-center gap-3">
              {attendance.should_show_check_in && (
                <button
                  className="btn btn-primary"
                  onClick={() => handleAction("check_in")}
                  disabled={loading}
                >
                  Check In
                </button>
              )}
              {attendance.should_show_check_out && (
                <button
                  className="btn btn-success"
                  onClick={() => handleAction("check_out")}
                  disabled={loading || !attendance.can_check_out}
                >
                  Check Out
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManualAttendanceForm;
