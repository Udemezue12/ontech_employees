import React, { useState } from "react";
import axios from "axios";

import { Link, useNavigate } from "react-router-dom";
import BootstrapButtonFields from "./forms/BootstrapButtonFields";
import { cookies } from "./Cookie";
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
// const csrfToken = await fetchCSRFToken();
function FingerprintLogin() {
  const [error, setError] = useState("");
  const navigate = useNavigate();

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
          withCredentials: true, 
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
        "https://ontech-systems.onrender.com/api/fingerprint/auth/",
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

      const { token, user_id, role, department } = authResponse.data;
      localStorage.setItem("Token", token);
      localStorage.setItem("UserId", user_id);
      localStorage.setItem("Role", role);
      localStorage.setItem("Department", department);

      navigate("/dashboard", { replace: true });
      
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
    <div className="container-fluid fringer min-vh-100 d-flex justify-content-center align-items-center">
      <div
        className="card shadow-lg p-4 rounded-4 border-0 w-100"
        style={{ maxWidth: "420px", transition: "all 0.3s ease-in-out" }}
      >
        {error && (
          <div className="mb-3">
            <p style={{ color: "red" }}>{error}</p>
          </div>
        )}

        <div className="d-grid mb-3">
          <BootstrapButtonFields
            onClick={handleFingerprintLogin}
            label="Authenticate Passkey"
            type="button"
            className="btn btn-primary rounded-pill"
          />
        </div>
        <div className="text-center">
          <small>
          <Link to="/login" className="text-decoration-non">
            Login Manually
          </Link></small>
        </div>
      </div>
    </div>
  );
}

export default FingerprintLogin;
