import React, { useEffect, useState } from "react";
import axios from "axios";
import { Box, Typography, Button } from "@mui/material";
import FingerprintJS from "@fingerprintjs/fingerprintjs";
// import { cookies } from "./Cookie";
import "./material.css";
export const fetchCSRFToken = async () => {
  try {
    const response = await axios.get("https://ontech-systems.onrender.com/api/csrf/", {
      withCredentials: true,
      headers: {
        "Accept": "application/json",
      }
    });

    if (
      typeof response.data === "string" &&
      response.data.includes("<!doctype html")
    ) {
      throw new Error("Received HTML instead of JSON");
    }

    const csrfToken = response.data.csrfToken;

    if (!csrfToken) {
      throw new Error("CSRF token not found in response");
    }

    return csrfToken;
  } catch (error) {
    console.error("Failed to fetch CSRF token:", error);
    return null;
  }
};
const RegisterFingerprint = () => {
  const [deviceFingerprint, setDeviceFingerprint] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [alreadyRegistered, setAlreadyRegistered] = useState(false);

  const userId = localStorage.getItem("UserId");
  const token = localStorage.getItem("Token");
  //
  useEffect(() => {
    const loadFingerprintAndCheck = async () => {
      try {
        const fp = await FingerprintJS.load();
        const result = await fp.get();
        const fingerprint = result.visitorId;
        setDeviceFingerprint(fingerprint);
        const csrfToken = await fetchCSRFToken();

        //

        const res = await axios.get(
          "https://ontech-systems.onrender.com/api/create/fingerprint/",
          {
            headers: {
              Authorization: `Token ${token}`,
              "X-CSRFToken": csrfToken,
            },
            withCredentials: true,
          }
        );

        if (res.data.some((cred) => cred.device_fingerprint === fingerprint)) {
          setAlreadyRegistered(true);
        }
      } catch (error) {
        console.error("Error checking existing passkey:", error);
      }
    };

    loadFingerprintAndCheck();
  }, [token]);



  const registerFingerprint = async () => {
  setIsSubmitting(true);

  if (!userId || !token || !deviceFingerprint) {
    alert("User not authenticated or device passkey not available.");
    setIsSubmitting(false);
    return;
  }

  try {
    const credential = await navigator.credentials.create({
      publicKey: {
        rp: { name: "Astro", id: "ontech-systems.onrender.com" },
        user: {
          id: new TextEncoder().encode(userId.toString()),
          name: userId,
          displayName: userId,
        },
        challenge: crypto.getRandomValues(new Uint8Array(32)),
        pubKeyCredParams: [
          { type: "public-key", alg: -7 },
          { type: "public-key", alg: -257 },
        ],
        timeout: 70000,
        attestation: "direct",
        authenticatorSelection: {
          authenticatorAttachment: "platform",
          userVerification: "required",
        },
      },
    });

    const csrfToken = await fetchCSRFToken();
    if (!csrfToken) {
      throw new Error("Failed to fetch CSRF token");
    }

    const credentialId = credential.id;
    const attestationObject = credential.response.attestationObject;
    const publicKey = btoa(
      String.fromCharCode(...new Uint8Array(attestationObject))
    );

    
   await axios.post(
      "https://ontech-systems.onrender.com/api/create/fingerprint/",
      {
        credential_id: credentialId,
        public_key: publicKey,
        device_fingerprint: deviceFingerprint,
      },
      {
        headers: {
          Authorization: `Token ${token}`,
          "X-CSRFToken": csrfToken,
        },
        withCredentials: true,
      }
    );

   
    alert("Passkey created successfully!");
    window.location.reload();
  } catch (error) {
    console.error("Error creating Passkey:", error);
    if (error.message === "Failed to fetch CSRF token" || error.message === "Invalid response from CSRF endpoint") {
      alert("Failed to fetch CSRF token. Please refresh and try again.");
    } else if (error.response && error.response.status === 403) {
      alert("CSRF token error. Please refresh and try again.");
    } else if (error.response && error.response.status === 400 && error.response.data) {
      const messages = Object.values(error.response.data).flat().join(" ");
      alert(`Error: ${messages}`);
    } else {
      alert("Passkey creation failed. Please try again.");
    }
  } finally {
    setIsSubmitting(false);
  }
};

  return (
    <div className="finger">
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          px: 2,
        }}
      >
        <Box sx={{ textAlign: "center", width: "100%", maxWidth: 400 }}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: "bold" }}>
            Create Passkey
          </Typography>

          {alreadyRegistered ? (
            <Box className="itemBox">
              <Typography color="error">
                You have already created a Passkey
              </Typography>
            </Box>
          ) : (
            <Box className="itemBox" mt={2}>
              <Button
                variant="contained"
                color="primary"
                onClick={registerFingerprint}
                disabled={isSubmitting}
                fullWidth
              >
                {isSubmitting ? "Registering..." : "Register"}
              </Button>
            </Box>
          )}
        </Box>
      </Box>
    </div>
  );
};

export default RegisterFingerprint;
