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

      console.log("Biometric Status Response:", response.data);

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
        console.log("Polling biometric status...");
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

      console.log("Handle Action Response:", resp);

      showSnackbar(resp.message || `${action} recorded`);

      // Immediately re-fetch status to ensure correct state
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
// //////////////
// import React, { useEffect, useState, useCallback } from "react";
// import {
//   Box,
//   Typography,
//   Button,
//   Alert,
//   Snackbar,
//   CircularProgress,
// } from "@mui/material";
// import axios from "axios";
// import { cookies } from "./Cookie";

// // Constants for API endpoints and intervals
// const API_BASE_URL = "https://ontech-systems.onrender.com/api/";
// const POLLING_INTERVAL_MS = 30000; // 30 seconds for general updates
// const CHECKOUT_DELAY_HOURS = 1; // 1 hour delay for check-out

// export default function BiometricAttendance() {
//   const token = localStorage.getItem("Token");
//   const [loadingAction, setLoadingAction] = useState("");
//   const [snackbarOpen, setSnackbarOpen] = useState(false);
//   const [snackbarMessage, setSnackbarMessage] = useState("");
//   const [canCheckIn, setCanCheckIn] = useState(false);
//   const [canCheckOut, setCanCheckOut] = useState(false);
//   const [doneForToday, setDoneForToday] = useState(false);
//   const [overtimeHours, setOvertimeHours] = useState(null);
//   const [checkInTime, setCheckInTime] = useState(null); // Store check-in time for precise timing
//   const [clock, setClock] = useState(new Date().toLocaleTimeString());
//   const [useManual, setUseManual] = useState(false);

//   // Update clock every second
//   useEffect(() => {
//     const interval = setInterval(() => {
//       setClock(new Date().toLocaleTimeString());
//     }, 1000);
//     return () => clearInterval(interval);
//   }, []);

//   // Fetch CSRF token
//   const fetchCSRFToken = useCallback(async () => {
//     try {
//       await axios.get(`${API_BASE_URL}csrf/`, { withCredentials: true });
//       return cookies.get("csrftoken");
//     } catch (err) {
//       console.error("CSRF fetch error:", err);
//       return null;
//     }
//   }, []);

//   // Show snackbar message
//   const showSnackbar = useCallback((message, success = true) => {
//     setSnackbarMessage(`${success ? "✔️" : "❌"} ${message}`);
//     setSnackbarOpen(true);
//   }, []);

//   // Fetch user attendance method (manual or biometric)
//   const fetchUserAttendanceMethod = useCallback(async () => {
//     const csrfToken = await fetchCSRFToken();
//     if (!csrfToken) return;

//     try {
//       const response = await axios.get(`${API_BASE_URL}attendance/check-method/`, {
//         headers: {
//           Authorization: `Token ${token}`,
//           "X-CSRFToken": csrfToken,
//         },
//         withCredentials: true,
//       });

//       if (response.data.method === "manual") {
//         setUseManual(true);
//       } else {
//         setCanCheckIn(response.data.can_check_in ?? false);
//         setCanCheckOut(response.data.can_check_out ?? false);
//         setDoneForToday(
//           !response.data.can_check_in && !response.data.can_check_out
//         );
//         setOvertimeHours(response.data.overtime_hours ?? null);
//       }
//     } catch (error) {
//       console.error("Error checking attendance method:", error);
//       showSnackbar("Error loading attendance preferences", false);
//     }
//   }, [token, fetchCSRFToken, showSnackbar]);

//   // Fetch biometric attendance status
//   const fetchBiometricStatus = useCallback(async () => {
//     const csrfToken = await fetchCSRFToken();
//     if (!csrfToken) return;

//     try {
//       const response = await axios.get(`${API_BASE_URL}attendance/biometric/`, {
//         headers: {
//           Authorization: `Token ${token}`,
//           "X-CSRFToken": csrfToken,
//         },
//         withCredentials: true,
//       });

//       console.log("Biometric Status Response:", response.data);

//       setCanCheckIn(response.data.can_check_in ?? false);
//       setCanCheckOut(response.data.can_check_out ?? false);
//       setDoneForToday(response.data.done_for_today ?? false);
//       setOvertimeHours(response.data.overtime_hours ?? null);

//       // Set check-in time for precise check-out timing
//       if (response.data.biometric_attendance?.check_in) {
//         setCheckInTime(new Date(response.data.biometric_attendance.check_in));
//       } else {
//         setCheckInTime(null);
//       }

//       if (response.data.manual_attendance) {
//         setUseManual(true);
//       }
//     } catch (error) {
//       const message = error.response?.data?.error || "Failed to load attendance data.";
//       console.error("Biometric Status Error:", error);
//       if (message.includes("manual")) {
//         setUseManual(true);
//       }
//       showSnackbar(message, false);
//     }
//   }, [token, fetchCSRFToken, showSnackbar]);

//   // Handle check-in/check-out actions
//   const handleAction = useCallback(
//     async (action) => {
//       const csrfToken = await fetchCSRFToken();
//       if (!csrfToken) {
//         showSnackbar("CSRF token missing", false);
//         return;
//       }

//       setLoadingAction(action);

//       try {
//         const { data: optionsData } = await axios.get(
//           `${API_BASE_URL}fingerprint/request-options/`,
//           {
//             headers: {
//               Authorization: `Token ${token}`,
//               "X-CSRFToken": csrfToken,
//             },
//             withCredentials: true,
//           }
//         );

//         const publicKey = optionsData.publicKey;
//         publicKey.challenge = base64urlToBuffer(publicKey.challenge);
//         publicKey.allowCredentials = publicKey.allowCredentials.map((cred) => ({
//           ...cred,
//           id: base64urlToBuffer(cred.id),
//         }));

//         const credential = await navigator.credentials.get({ publicKey });

//         const { data: resp } = await axios.post(
//           `${API_BASE_URL}attendance/biometric/`,
//           {
//             credential_id: credential.id,
//             action,
//           },
//           {
//             headers: {
//               Authorization: `Token ${token}`,
//               "X-CSRFToken": csrfToken,
//             },
//             withCredentials: true,
//           }
//         );

//         console.log("Handle Action Response:", resp);
//         showSnackbar(resp.message || `${action} recorded`);

//         // Re-fetch status to update state
//         await fetchBiometricStatus();
//       } catch (err) {
//         const errorMsg = err.response?.data?.error || err.message || "Unexpected error";
//         showSnackbar(errorMsg, false);
//       } finally {
//         setLoadingAction("");
//       }
//     },
//     [token, fetchCSRFToken, showSnackbar, fetchBiometricStatus]
//   );

//   // Convert base64url to buffer for WebAuthn
//   const base64urlToBuffer = (base64url) => {
//     const padding = "=".repeat((4 - (base64url.length % 4)) % 4);
//     const base64 = base64url.replace(/-/g, "+").replace(/_/g, "/") + padding;
//     const binary = atob(base64);
//     const bytes = new Uint8Array(binary.length);
//     for (let i = 0; i < binary.length; i++) {
//       bytes[i] = binary.charCodeAt(i);
//     }
//     return bytes.buffer;
//   };

//   // Fetch initial state and set up polling/timing
//   useEffect(() => {
//     fetchUserAttendanceMethod();
//     fetchBiometricStatus();

//     // Periodic polling for overtime updates
//     const pollingInterval = setInterval(() => {
//       if (!canCheckIn && !doneForToday && !useManual) {
//         console.log("Polling biometric status for updates...");
//         fetchBiometricStatus();
//       }
//     }, POLLING_INTERVAL_MS);

//     return () => clearInterval(pollingInterval);
//   }, [
//     fetchUserAttendanceMethod,
//     fetchBiometricStatus,
//     canCheckIn,
//     doneForToday,
//     useManual,
//   ]);

//   // Precise timer for check-out button visibility
//   useEffect(() => {
//     let timer;
//     if (checkInTime && !canCheckOut && !doneForToday && !useManual) {
//       const checkOutTime = new Date(checkInTime);
//       checkOutTime.setHours(checkOutTime.getHours() + CHECKOUT_DELAY_HOURS);
//       const timeUntilCheckOut = checkOutTime - new Date();

//       if (timeUntilCheckOut > 0) {
//         console.log(`Scheduling check-out button for ${checkOutTime.toLocaleTimeString()}`);
//         timer = setTimeout(() => {
//           fetchBiometricStatus(); // Fetch updated status to show check-out button
//         }, timeUntilCheckOut);
//       }
//     }

//     return () => {
//       if (timer) clearTimeout(timer);
//     };
//   }, [checkInTime, canCheckOut, doneForToday, useManual, fetchBiometricStatus]);

//   return (
//     <div className="background">
//     <Box sx={{ maxWidth: 400, mx: "auto", mt: 4, textAlign: "center" }}>
//       <Typography variant="h5" gutterBottom>
//         ⏰ Current Time: {clock}
//       </Typography>

//       <Typography variant="h6" gutterBottom>
//         Biometric Attendance
//       </Typography>

//       {useManual ? (
//         <Alert severity="info" sx={{ mt: 2 }}>
//           📌 You’ve already started using the manual method today. Please continue with that.
//         </Alert>
//       ) : doneForToday ? (
//         <Alert severity="success" sx={{ mt: 2 }}>
//           ✅ You're done for today!
//         </Alert>
//       ) : (
//         <Box sx={{ display: "flex", justifyContent: "space-around", mt: 3 }}>
//           {canCheckIn && (
//             <Button
//               variant="contained"
//               onClick={() => handleAction("check_in")}
//               disabled={loadingAction === "check_in"}
//               startIcon={loadingAction === "check_in" ? <CircularProgress size={20} /> : null}
//               sx={{
//                 backgroundColor: "#4caf50",
//                 "&:hover": { backgroundColor: "#388e3c" },
//               }}
//             >
//               Check In
//             </Button>
//           )}
//           {canCheckOut && (
//             <Button
//               variant="contained"
//               onClick={() => handleAction("check_out")}
//               disabled={loadingAction === "check_out"}
//               startIcon={loadingAction === "check_out" ? <CircularProgress size={20} /> : null}
//               sx={{
//                 backgroundColor: "#f44336",
//                 "&:hover": { backgroundColor: "#d32f2f" },
//               }}
//             >
//               Check Out
//             </Button>
//           )}
//         </Box>
//       )}

//       {overtimeHours != null && !useManual && (
//         <Alert severity="info" sx={{ mt: 2 }}>
//           ⏱️ Overtime: <strong>{overtimeHours} hours</strong>
//         </Alert>
//       )}

//       <Snackbar
//         open={snackbarOpen}
//         autoHideDuration={6000}
//         onClose={() => setSnackbarOpen(false)}
//       >
//         <Alert
//           onClose={() => setSnackbarOpen(false)}
//           severity={snackbarMessage.startsWith("✔️") ? "success" : "error"}
//           sx={{ width: "100%" }}
//         >
//           {snackbarMessage}
//         </Alert>
//       </Snackbar>
//     </Box></div>
//   );
// }
