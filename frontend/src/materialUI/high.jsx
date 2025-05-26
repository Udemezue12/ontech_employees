// // // export default function BiometricAttendance() {
// // //   const token = localStorage.getItem("Token");

// // //   const [loadingAction, setLoadingAction] = useState("");
// // //   const [snackbarOpen, setSnackbarOpen] = useState(false);
// // //   const [snackbarMessage, setSnackbarMessage] = useState("");
// // //   const [showCheckIn, setShowCheckIn] = useState(false);
// // //   const [showCheckOut, setShowCheckOut] = useState(false);
// // //   const [overtimeHours, setOvertimeHours] = useState(null);

// // //   const base64urlToBuffer = (base64url) => {
// // //     const padding = "=".repeat((4 - (base64url.length % 4)) % 4);
// // //     const base64 = base64url.replace(/-/g, "+").replace(/_/g, "/") + padding;
// // //     const binary = atob(base64);
// // //     const bytes = new Uint8Array(binary.length);
// // //     for (let i = 0; i < binary.length; i++) {
// // //       bytes[i] = binary.charCodeAt(i);
// // //     }
// // //     return bytes.buffer;
// // //   };

// // // useEffect(() => {
// // //   const fetchStatus = async () => {
// // //     try {
// // //       const { data } = await axios.get("http://localhost:8000/api/attendance/biometric/status/", {
// // //         headers: { Authorization: Token ${token} },
// // //         withCredentials: true,
// // //       });

// // //       setShowCheckIn(data.can_check_in);
// // //       setShowCheckOut(data.can_check_out);
// // //       setOvertimeHours(data.overtime_hours || 0);

// // //       if (data.attendance) {
// // //         // Optionally store attendance data if needed
// // //       }
// // //     } catch (err) {
// // //       const data = err.response?.data;

// // //       if (data?.can_check_in === false && data?.can_check_out === false) {
// // //         setShowCheckIn(false);
// // //         setShowCheckOut(false);
// // //         showSnackbar(data.error || "Manual attendance used today.", false);
// // //       } else {
// // //         showSnackbar("Failed to load attendance status.", false);
// // //       }
// // //     }
// // //   };

// // //   fetchStatus();
// // // }, []);

// // //   const fetchCSRFToken = async () => {
// // //     try {
// // //       await axios.get("https://ontech-systems.onrender.com/api/csrf/", {
// // //         withCredentials: true,
// // //       });
// // //       return cookies.get("csrftoken");
// // //     } catch (err) {
// // //       console.error("CSRF fetch error:", err);
// // //       return null;
// // //     }
// // //   };

// // //   const showSnackbar = (message, success = true) => {
// // //     setSnackbarMessage(${success ? "✔️" : "❌"} ${message});
// // //     setSnackbarOpen(true);
// // //   };

// // //   const handleAction = async (action) => {
// // //     const csrfToken = await fetchCSRFToken();
// // //     if (!csrfToken) {
// // //       showSnackbar("CSRF token missing", false);
// // //       return;
// // //     }

// // //     setLoadingAction(action);

// // //     try {
// // //       // Get WebAuthn request options
// // //       const { data: optionsData } = await axios.get(
// // //         "http://localhost:8000/api/fingerprint/request-options/",
// // //         {
// // //           headers: {
// // //             Authorization: Token ${token},
// // //             "X-CSRFToken": csrfToken,
// // //           },
// // //           withCredentials: true,
// // //         }
// // //       );

// // //       const publicKey = optionsData.publicKey;
// // //       publicKey.challenge = base64urlToBuffer(publicKey.challenge);
// // //       publicKey.allowCredentials = publicKey.allowCredentials.map((cred) => ({
// // //         ...cred,
// // //         id: base64urlToBuffer(cred.id),
// // //       }));

// // //       const credential = await navigator.credentials.get({ publicKey });

// // //       const credentialId = credential.id;

// // //       // Submit biometric action
// // //       const { data: resp } = await axios.post(
// // //         "http://localhost:8000/api/attendance/biometric/",
// // //         {
// // //           credential_id: credentialId,
// // //           action,
// // //         },
// // //         {
// // //           headers: {
// // //             Authorization: Token ${token},
// // //             "X-CSRFToken": csrfToken,
// // //           },
// // //           withCredentials: true,
// // //         }
// // //       );

// // //       showSnackbar(resp.message || ${action} recorded, true);

// // //       // Update visibility based on backend logic
// // //       setShowCheckIn(resp.can_check_in);
// // //       setShowCheckOut(resp.can_check_out);

// // //       // Show overtime if any
// // //       if (resp.overtime_hours != null) {
// // //         setOvertimeHours(resp.overtime_hours);
// // //       }
// // //     } catch (err) {
// // //       const errorMsg =
// // //         err.response?.data?.error || err.message || "Unexpected error";
// // //       showSnackbar(errorMsg, false);
// // //     } finally {
// // //       setLoadingAction("");
// // //     }
// // //   };

// // //   return (
// // //     <Box sx={{ maxWidth: 400, mx: "auto", mt: 4, textAlign: "center" }}>
// // //       <Typography variant="h6" gutterBottom>
// // //         Biometric Attendance
// // //       </Typography>

// // //       {overtimeHours != null && (
// // //         <Alert severity="info" sx={{ mt: 2 }}>
// // //           ⏱️ Overtime: <strong>{overtimeHours} hours</strong>
// // //         </Alert>
// // //       )}

// // //       <Box sx={{ display: "flex", justifyContent: "space-around", mt: 3 }}>
// // //         {showCheckIn && (
// // //           <Button
// // //             variant="contained"
// // //             onClick={() => handleAction("check_in")}
// // //             disabled={loadingAction === "check_in"}
// // //             startIcon={
// // //               loadingAction === "check_in" ? (
// // //                 <CircularProgress size={20} />
// // //               ) : null
// // //             }
// // //             sx={{
// // //               backgroundColor: "#4caf50",
// // //               "&:hover": { backgroundColor: "#388e3c" },
// // //             }}
// // //           >
// // //             Check In
// // //           </Button>
// // //         )}
// // //         {showCheckOut && (
// // //           <Button
// // //             variant="contained"
// // //             onClick={() => handleAction("check_out")}
// // //             disabled={loadingAction === "check_out"}
// // //             startIcon={
// // //               loadingAction === "check_out" ? (
// // //                 <CircularProgress size={20} />
// // //               ) : null
// // //             }
// // //             sx={{
// // //               backgroundColor: "#f44336",
// // //               "&:hover": { backgroundColor: "#d32f2f" },
// // //             }}
// // //           >
// // //             Check Out
// // //           </Button>
// // //         )}
// // //       </Box>

// // //       <Snackbar
// // //         open={snackbarOpen}
// // //         autoHideDuration={6000}
// // //         onClose={() => setSnackbarOpen(false)}
// // //       >
// // //         <Alert
// // //           onClose={() => setSnackbarOpen(false)}
// // //           severity={snackbarMessage.startsWith("✔️") ? "success" : "error"}
// // //           sx={{ width: "100%" }}
// // //         >
// // //           {snackbarMessage}
// // //         </Alert>
// // //       </Snackbar>
// // //     </Box>
// // //   );
// // // }

// // useEffect(() => {
// //     const fetchStatus = async () => {
// //       try {
// //         const { data } = await axios.get(
// //           "http://localhost:8000/api/attendance/biometric/status/",
// //           {
// //             headers: { Authorization: `Token ${token}` },
// //             withCredentials: true,
// //           }
// //         );
// //       // setAttendance(data);

// //         setCanCheckIn(data.can_check_in);
// //         setCanCheckOut(data.can_check_out);
// //         setDoneForToday(data.done_for_today);
// //         setOvertimeHours(data.overtime_hours || 0);
// //         setOvertimeHours(data.overtime_hours.toFixed(2));
// //       } catch (err) {
// //         const data = err.response?.data;
// //         if (data?.can_check_in === false && data?.can_check_out === false) {
// //           setCanCheckIn(false);
// //           setCanCheckOut(false);
// //           setDoneForToday(true);
// //           showSnackbar(data.error || "Manual attendance used today.", false);
// //         } else {
// //           showSnackbar("Failed to load attendance status.", false);
// //         }
// //       }
// //     };

// //     fetchStatus();
// //   }, []);

// // ////////////////
// // /////////////
// useEffect(() => {
//     const fetchUserAttendanceMethod = async () => {
//       const csrfToken = await fetchCSRFToken();
//       try {
//         const response = await axios.get(
//           "http://localhost:8000/api/attendance/check-method/",
//           {
//             headers: {
//               Authorization: `Token ${token}`,
//               "X-CSRFToken": csrfToken,
//             },
//             withCredentials: true,
//           }
//         );
//         if (response.data.method === "manual") {
//           setUseManual(true);
//         } else {
//           setCanCheckIn(response.data.can_check_in);
//           setCanCheckOut(response.data.can_check_out);
//           setDoneForToday(
//             !response.data.can_check_in && !response.data.can_check_out
//           );
//           setOvertimeHours(response.data.overtime_hours);
//         }
//       } catch (error) {
//         console.error("Error checking attendance method", error);
//         showSnackbar("Error loading attendance preferences", false);
//       }
//     };
//     fetchUserAttendanceMethod();
//   }, [token]);

//
// Using this "class ManualAttendance(models.Model):
// CHECKOUT_ELIGIBLE_HOURS = 1
// employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
// date = models.DateField(default=timezone.now)
// check_in = models.DateTimeField(null=True, blank=True)
// check_out = models.DateTimeField(null=True, blank=True)
// worked_hours = models.DecimalField(
// max_digits=5, decimal_places=2, default=0)
// overtime\_hours = models.DecimalField(
// max_digits=5, decimal_places=2, default=0)
// manual_check_in = models.BooleanField(default=True)
// method = models.CharField(default="manual", max_length=10)

// ```
// def __str__(self):
//     return f"{self.employee.name} - Manual - {self.date}"

// def save(self, *args, **kwargs):
//     # Calculate worked hours if checked out
//     if self.check_in and self.check_out:
//         self.worked_hours = self.calculate_worked_hours()
//     # Always update overtime (including if check_out is None)
//     self.calculate_overtime()
//     super().save(*args, **kwargs)

// def calculate_worked_hours(self):
//     if self.check_in and self.check_out:
//         worked_seconds = (self.check_out - self.check_in).total_seconds()
//         return round(worked_seconds / 3600, 2)
//     return 0

// def calculate_overtime(self):
//     if self.check_in:
//         end_time = self.check_out or timezone.now()
//         worked_seconds = (end_time - self.check_in).total_seconds()
//         overtime_seconds = worked_seconds - (8 * 3600)
//         self.overtime_hours = round(max(overtime_seconds / 3600, 0), 2)

// def can_check_out(self):
//     if self.check_in:
//         return timezone.now() >= self.check_in + timedelta(hours=self.CHECKOUT_ELIGIBLE_HOURS)
//     return False

// def should_show_check_in(self):
//     return self.check_in is None and self.check_out is None

// def should_show_check_out(self):
//     if self.check_in and not self.check_out:
//         elapsed = (timezone.now() - self.check_in).total_seconds()
//         return elapsed >= self.CHECKOUT_ELIGIBLE_HOURS * 3600
//     return False" and "class ManualAttendanceSerializer(serializers.ModelSerializer):
// can_check_out = serializers.SerializerMethodField()
// should_show_check_in = serializers.SerializerMethodField()
// should_show_check_out = serializers.SerializerMethodField()

// class Meta:
//     model = ManualAttendance
//     fields = '__all__'

// def get_can_check_out(self, obj):
//     return obj.can_check_out()

// def get_should_show_check_in(self, obj):
//     return obj.should_show_check_in()

// def get_should_show_check_out(self, obj):
//     return obj.should_show_check_out()" write a cpmplete viewsst where whena new user logins in, he see check-in button first(if he has not checked in with biometric), then after clicking check_in, check_in button disappears, in which after 1hr check_out button appears., the user clicks check_out and check_in doesn't appear until the next day..if the user didn't click check_out when it appears, overtime is calculated an d inputted, but the moment its clicked, overtime stops..also i want if check_in is clicked, it should be so till check_out button appears even if the user refreshes or goes back and forth, also add validation to check if the user has used Biometric to check_in, if so, he should continue with biometric
// ```
