import React, { useEffect, useState, useCallback } from "react";
import {
  Box,
  Typography,
  Button,
  Alert,
  Snackbar,
  CircularProgress,
} from "@mui/material";
import axios from "axios";
import { cookies } from "./Cookie";
import "./material.css";

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

export default function BiometricAttendance() {
  const token = localStorage.getItem("Token");
  const [loadingAction, setLoadingAction] = useState("");
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [canCheckIn, setCanCheckIn] = useState(false);
  const [canCheckOut, setCanCheckOut] = useState(false);
  const [doneForToday, setDoneForToday] = useState(false);
  const [overtimeHours, setOvertimeHours] = useState(null);
  const [clock, setClock] = useState(new Date().toLocaleTimeString());
  const [useManual, setUseManual] = useState(false);
  

  // Update clock every second
  useEffect(() => {
    const interval = setInterval(() => {
      setClock(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchUserAttendanceMethod = async () => {
      try {
        const response = await axios.get(
          "https://ontech-systems.onrender.com/api/attendance/check-method/",
          {
            headers: {
              Authorization: `Token ${token}`,
              "X-CSRFToken": csrfToken,
            },
            withCredentials: true,
          }
        );
        if (response.data.method === "manual") {
          setUseManual(true);
        } else {
          setCanCheckIn(response.data.can_check_in);
          setCanCheckOut(response.data.can_check_out);
          setDoneForToday(
            !response.data.can_check_in && !response.data.can_check_out
          );
          setOvertimeHours(response.data.overtime_hours);
        }
      } catch (error) {
        console.error("Error checking attendance method", error);
        showSnackbar("Error loading attendance preferences", false);
      }
    };
    fetchUserAttendanceMethod();
  }, [token]);

  const fetchBiometricStatus = useCallback(async () => {
    try {
      const response = await axios.get(
        "https://ontech-systems.onrender.com/api/attendance/biometric/",
        {
          headers: {
            Authorization: `Token ${token}`,
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        }
      );

      

      setCanCheckIn(response.data.can_check_in ?? false);
      setCanCheckOut(response.data.can_check_out ?? false);
      setDoneForToday(response.data.done_for_today ?? false);
      setOvertimeHours(response.data.overtime_hours ?? null);

      if (response.data.manual_attendance) {
        setUseManual(true);
      }
    } catch (error) {
      const message =
        error.response?.data?.error || "Failed to load attendance data.";
      console.error("Biometric Status Error:", error);
      if (message.includes("manual")) {
        setUseManual(true);
      }
      showSnackbar(message, false);
    }
  }, [token]); // Include all dependencies

  useEffect(() => {
    fetchBiometricStatus();

    let timer;
    if (!canCheckIn && !doneForToday && !useManual) {
      const checkInTime = new Date();
      checkInTime.setHours(checkInTime.getHours() + 1);
      const timeUntilCheckOut = checkInTime - new Date();

      if (timeUntilCheckOut > 0) {
        timer = setTimeout(() => {
          fetchBiometricStatus();
        }, timeUntilCheckOut);
      }
    }

    const interval = setInterval(() => {
      if (!canCheckIn && !doneForToday && !useManual) {
        
        fetchBiometricStatus();
      }
    }, 30000);

    return () => {
      clearInterval(interval);
      if (timer) clearTimeout(timer);
    };
  }, [fetchBiometricStatus, canCheckIn, doneForToday, useManual]);

  const showSnackbar = (message, success = true) => {
    setSnackbarMessage(`${success ? "✔️" : "❌"} ${message}`);
    setSnackbarOpen(true);
  };

  const base64urlToBuffer = (base64url) => {
    const padding = "=".repeat((4 - (base64url.length % 4)) % 4);
    const base64 = base64url.replace(/-/g, "+").replace(/_/g, "/") + padding;
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  };

  const handleAction = async (action) => {
    if (!csrfToken) {
      showSnackbar("CSRF token missing", false);
      return;
    }

    setLoadingAction(action);

    try {
      const { data: optionsData } = await axios.get(
        "https://ontech-systems.onrender.com/api/fingerprint/request-options/",
        {
          headers: {
            Authorization: `Token ${token}`,
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        }
      );

      const publicKey = optionsData.publicKey;
      publicKey.challenge = base64urlToBuffer(publicKey.challenge);
      publicKey.allowCredentials = publicKey.allowCredentials.map((cred) => ({
        ...cred,
        id: base64urlToBuffer(cred.id),
      }));

      const credential = await navigator.credentials.get({ publicKey });

      const { data: resp } = await axios.post(
        "https://ontech-systems.onrender.com/api/attendance/biometric/",
        {
          credential_id: credential.id,
          action,
        },
        {
          headers: {
            Authorization: `Token ${token}`,
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        }
      );

      

      showSnackbar(resp.message || `${action} recorded`);

     
      await fetchBiometricStatus();
    } catch (err) {
      const errorMsg =
        err.response?.data?.error || err.message || "Unexpected error";
      showSnackbar(errorMsg, false);
    } finally {
      setLoadingAction("");
    }
  };

  return (
    <div className="background">
      <Box sx={{ maxWidth: 400, mx: "auto", mt: 4, textAlign: "center" }}>
        <Typography variant="h5" gutterBottom>
          ⏰ Current Time: {clock}
        </Typography>

        <Typography variant="h6" gutterBottom>
          Biometric Attendance
        </Typography>

        {useManual ? (
          <Alert severity="info" sx={{ mt: 2 }}>
            📌 You’ve already started using the manual method today. Please
            continue with that.
          </Alert>
        ) : doneForToday ? (
          <Alert severity="success" sx={{ mt: 2 }}>
            ✅ You're done for today!
          </Alert>
        ) : (
          <Box sx={{ display: "flex", justifyContent: "space-around", mt: 3 }}>
            {canCheckIn && (
              <Button
                variant="contained"
                onClick={() => handleAction("check_in")}
                disabled={loadingAction === "check_in"}
                startIcon={
                  loadingAction === "check_in" ? (
                    <CircularProgress size={20} />
                  ) : null
                }
                sx={{
                  backgroundColor: "#4caf50",
                  "&:hover": { backgroundColor: "#388e3c" },
                }}
              >
                Check In
              </Button>
            )}
            {canCheckOut && (
              <Button
                variant="contained"
                onClick={() => handleAction("check_out")}
                disabled={loadingAction === "check_out"}
                startIcon={
                  loadingAction === "check_out" ? (
                    <CircularProgress size={20} />
                  ) : null
                }
                sx={{
                  backgroundColor: "#f44336",
                  "&:hover": { backgroundColor: "#d32f2f" },
                }}
              >
                Check Out
              </Button>
            )}
          </Box>
        )}

        {overtimeHours != null && !useManual && (
          <Alert severity="info" sx={{ mt: 2 }}>
            ⏱️ Overtime: <strong>{overtimeHours} hours</strong>
          </Alert>
        )}

        <Snackbar
          open={snackbarOpen}
          autoHideDuration={6000}
          onClose={() => setSnackbarOpen(false)}
        >
          <Alert
            onClose={() => setSnackbarOpen(false)}
            severity={snackbarMessage.startsWith("✔️") ? "success" : "error"}
            sx={{ width: "100%" }}
          >
            {snackbarMessage}
          </Alert>
        </Snackbar>
      </Box>
    </div>
  );
}
