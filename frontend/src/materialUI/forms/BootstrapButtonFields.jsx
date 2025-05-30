import React from "react";

export default function BootstrapButtonFields({
  label,
  type = "button",
  onClick,
  className = "",
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      className={`btn btn-primary w-100 ${className}`}
    >
      {label}
    </button>
  );
}

export function BootstrapButtonField({
  label,
  type = "button",
  onClick,
  className = "",
  loading = false,
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      className={`btn btn-primary w-100 d-flex justify-content-center align-items-center ${className}`}
      disabled={loading}
    >
      {loading ? (
        <>
          <span
            className="spinner-border spinner-border-sm me-2"
            role="status"
            aria-hidden="true"
          ></span>
          Loading...
        </>
      ) : (
        label
      )}
    </button>
  );
}
