import React, { useState } from "react";
import axios from "axios";
import { Box } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import ButtonFields from "./forms/ButtonField";
import { cookies } from "./Cookie";

function FingerprintLogin() {
  const [error, setError] = useState("");
  const navigate = useNavigate();
  async function fetchCSRFToken() {
    try {
     await axios.get(
        "https://ontech-systems.onrender.com/api/csrf/",
        {
          withCredentials: true, // ensure cookies are sent
        }
      );
      return cookies.get("csrftoken"); // Fetch it after Django sets it
    } catch (err) {
      console.error("Failed to get CSRF token", err);
      return null;
    }
  }

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

  const handleFingerprintLogin = async () => {
    const csrfToken = await fetchCSRFToken();
    setError("");

    try {
      const response = await axios.get(
        "https://ontech-systems.onrender.com/api/fingerprint/request-options/",
        {
          headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "multipart/form-data",
          },
          withCredentials: true, // include cookies for CSRF
        }
      );
      const publicKey = response.data.publicKey;

      // Convert challenge and allowCredentials[].id from base64url to ArrayBuffer
      publicKey.challenge = base64urlToBuffer(publicKey.challenge);
      publicKey.allowCredentials = publicKey.allowCredentials.map((cred) => ({
        ...cred,
        id: base64urlToBuffer(cred.id),
      }));

      const credential = await navigator.credentials.get({ publicKey });

      const credentialId = credential.id;
      const authResponse = await axios.post(
        "http://localhost:8000/api/fingerprint/auth/",
        {
          credential_id: credentialId,
        },
        {
          headers: {
            "X-CSRFToken": csrfToken,
          },
          withCredentials: true,
        }
      );

      const { token, user_id, email, role, department } = authResponse.data;
      localStorage.setItem("Token", token);
      localStorage.setItem("UserId", user_id);
      localStorage.setItem("Email", email);
      localStorage.setItem("Role", role);
      localStorage.setItem("Department", department);

      navigate("/", { replace: true });
    } catch (err) {
      console.error("Fingerprint login failed:", err);
      if (err.response && err.response.data?.error) {
        setError(err.response.data.error);
      } else {
        setError("Fingerprint login failed. Try again.");
      }
    }
  };

  return (
    <div className="background">
      <Box className="whiteBox">
        <Box className="itemBox"></Box>

        {error && (
          <Box className="itemBox">
            <p style={{ color: "red" }}>{error}</p>
          </Box>
        )}

        <Box className="itemBox">
          <ButtonFields
            label="Authenticate Passkey"
            type="button"
            onClick={handleFingerprintLogin}
          />
        </Box>
        <Box className="itemBox">
          <Link to="/dasboard" className="link">
            Login in Manually Here
          </Link>
        </Box>
      </Box>
    </div>
  );
}

export default FingerprintLogin;
