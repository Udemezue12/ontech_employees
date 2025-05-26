import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import reportWebVitals from "./reportWebVitals";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min";

import { BrowserRouter } from "react-router-dom";
import Material from "./materialUI/Material";
// import CookieApp from "./Cookie";

import { RoleAuthProvider } from "./materialUI/RoleAuthContext";

const root_container = document.getElementById("root");

if (root_container) {
  const root = ReactDOM.createRoot(root_container);
  root.render(
    <React.StrictMode>
      <RoleAuthProvider>
        <BrowserRouter future={{ v7_startTransition: true }}>
          <Material />
        </BrowserRouter>
      </RoleAuthProvider>
    </React.StrictMode>
  );
}

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
