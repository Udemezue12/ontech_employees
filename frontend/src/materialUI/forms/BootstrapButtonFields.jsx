import React from "react";

export default function BootstrapButtonFields({ label, type = "button", onClick, className = "" }) {
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
